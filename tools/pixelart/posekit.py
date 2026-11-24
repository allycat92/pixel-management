#!/usr/bin/env python3
"""posekit — pose / proportion guides for image models (NovelAI img2img, GPT image references).

Procedural pixel shading is not good enough for final art, so this tool only builds the
*skeleton*: a 4-head-tall (adjustable) flat-shaded mannequin in a front three-quarter view
facing right, holding a weapon, posed through the game's animation set. The image model is
expected to keep pose + proportions and paint everything else.

Per frame, on a flat #FF00FF background:
  guide_<frame>.png  832x1216 colour-blocked mannequin (2 tones per part, light from upper-left)
  stick_<frame>.png  832x1216 OpenPose-style (COCO-18) stick figure on black (+ grey weapon line)
  small_<frame>.png  80x80 preview cell, feet at y=76
plus sheet.png (all guides) and anim.gif / anim_<anim>.gif (small cells, looped per animation).

Skeleton (head units; head = 1, standing height = --heads):
  leg (hip joint -> floor) 1.75 + 0.6*(N-4), torso (hip -> shoulder line) 1.0 + 0.4*(N-4),
  neck 0.25, head 1.0; thigh = shin; 2-bone IK (lengths are exact in every frame) for
  legs (planted feet on the y=0 baseline) and arms (hands locked to points on the weapon).

Usage:
  python3 tools/pixelart/posekit.py OUT_DIR [--heads 4] [--weapon katana]
                                    [--frames idle_0,attack_2,...] [--check]
Weapons: katana (default), sword_shield, spear, staff, bow, none.
Python 3 + Pillow + NumPy only. Deterministic: no randomness.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

GW, GH = 832, 1216            # NovelAI free-tier portrait size
GUIDE_FEET = 0.92             # feet baseline, fraction of image height
GUIDE_BODY = 0.73             # idle body height (feet -> head top), fraction of image height
SW = 80                       # small preview cell
SMALL_FEET = 76
SMALL_BODY = 64
BG = (255, 0, 255)
SD = np.array((0.6, 0.8))     # shadow direction (light comes from the upper left), screen y-down

ANIMS = [('idle', 4), ('walk', 4), ('attack', 5), ('hit', 1), ('cast', 3)]
ALL_FRAMES = ['%s_%d' % (a, i) for a, n in ANIMS for i in range(n)]
WEAPONS = ['katana', 'sword_shield', 'spear', 'staff', 'bow', 'none']

# ------------------------------------------------------------------ palette (base, shade)
PAL = {
    'outline': (30, 26, 40),
    'skin': ((234, 192, 160), (196, 146, 122)),
    'skinF': ((214, 170, 142), (176, 128, 108)),
    'hair': ((98, 66, 50), (64, 42, 36)),
    'eye': (44, 32, 46),
    'torso': ((62, 74, 124), (42, 50, 90)),
    'armN': ((82, 96, 150), (56, 66, 112)),
    'armF': ((50, 60, 100), (36, 42, 74)),
    'legN': ((72, 82, 130), (50, 58, 96)),
    'legF': ((50, 58, 96), (34, 40, 70)),
    'pelvis': ((60, 70, 114), (42, 48, 84)),
    'belt': ((126, 88, 56), (92, 64, 42)),
    'bootN': ((158, 118, 76), (120, 86, 56)),
    'bootF': ((128, 94, 62), (96, 70, 46)),
    'steel': ((198, 204, 216), (140, 148, 166)),
    'brass': ((202, 168, 76), (152, 122, 52)),
    'wrap': ((74, 58, 72), (50, 40, 52)),
    'wood': ((150, 108, 66), (112, 78, 48)),
    'shield': ((140, 62, 56), (102, 44, 42)),
    'gem': ((120, 186, 214), (76, 130, 170)),
    'string': ((226, 222, 210), (226, 222, 210)),
}


# ------------------------------------------------------------------ vector helpers
def v2(x, y):
    return np.array((float(x), float(y)))


def P(x, h):
    """world point from (x, height above the floor); world is y-down, floor at y=0."""
    return v2(x, -h)


def norm(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v * 0


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array((v[0] * c - v[1] * s, v[0] * s + v[1] * c))


def wdir(deg):
    """weapon direction from a math angle (0 = right, 90 = up)."""
    a = math.radians(deg)
    return v2(math.cos(a), -math.sin(a))


def ik(root, target, l1, l2, pref):
    """2-bone IK. Bone lengths are exact; of the two solutions the joint that points along
    `pref` is chosen. Returns (joint, end, miss) where miss > 0 means the target was out of reach."""
    d = target - root
    dist = float(np.linalg.norm(d))
    dc = min(max(dist, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-4)
    dirv = d / max(dist, 1e-9)
    a = (l1 * l1 - l2 * l2 + dc * dc) / (2 * dc)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    perp = np.array((-dirv[1], dirv[0]))
    if perp @ np.asarray(pref, float) < 0:
        perp = -perp
    joint = root + dirv * a + perp * h
    end = root + dirv * dc
    return joint, end, dist - dc


# ------------------------------------------------------------------ shapes (world units)
# ('cap', a, b, ra, rb) tapered capsule | ('ell', c, rx, ry, ang) | ('poly', pts)
# ('and', s1, s2) | ('or', s1, s2) | ('line', [pts], w) open polyline of width w
def cap(a, b, ra, rb=None):
    return ('cap', a, b, ra, ra if rb is None else rb)


def ell(c, rx, ry, ang=0.0):
    return ('ell', c, rx, ry, ang)


def poly(pts):
    return ('poly', [np.asarray(p, float) for p in pts])


def cap_pts(a, b, ra, rb, n=14):
    d = b - a
    L = float(np.linalg.norm(d))
    u = d / L if L > 1e-9 else v2(1, 0)
    pn = np.array((-u[1], u[0]))
    pts = []
    for i in range(n + 1):            # half circle around b
        t = -math.pi / 2 + math.pi * i / n
        pts.append(b + (u * math.cos(t) + pn * math.sin(t)) * rb)
    for i in range(n + 1):            # half circle around a
        t = math.pi / 2 + math.pi * i / n
        pts.append(a + (u * math.cos(t) + pn * math.sin(t)) * ra)
    return pts


def ell_pts(c, rx, ry, ang, n=40):
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append(c + v2(x * ca - y * sa, x * sa + y * ca))
    return out


def shape_points(s, grow=0.0):
    k = s[0]
    if k == 'cap':
        return cap_pts(s[1], s[2], s[3] + grow, s[4] + grow)
    if k == 'ell':
        return ell_pts(s[1], s[2] + grow, s[3] + grow, s[4])
    if k == 'poly':
        return s[1]
    if k == 'line':
        return s[1]
    if k == 'and':                     # an intersection is bounded by its first operand
        return shape_points(s[1], grow)
    return shape_points(s[1], grow) + shape_points(s[2], grow)


class Raster:
    """world -> pixel transform + mask rasteriser (supersampled)."""

    def __init__(self, w, h, s, ox, oy, ss):
        self.w, self.h, self.s, self.ox, self.oy, self.ss = w * ss, h * ss, s, ox, oy, ss

    def px(self, p):
        return ((self.ox + p[0] * self.s) * self.ss, (self.oy + p[1] * self.s) * self.ss)

    def window(self, s, grow=0.0, pad=4):
        """integer pixel window (x0, y0, x1, y1) that contains shape s grown by `grow`."""
        if s[0] == 'or':
            a, b = self.window(s[1], grow, pad), self.window(s[2], grow, pad)
            return min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])
        if s[0] == 'and':
            return self.window(s[1], grow, pad)
        pts = np.array([self.px(p) for p in shape_points(s, grow)])
        extra = pad
        if s[0] == 'line':
            extra += (s[2] / 2 + grow) * self.s * self.ss
        if s[0] == 'poly':
            extra += grow * self.s * self.ss
        x0 = max(int(math.floor(pts[:, 0].min() - extra)), 0)
        y0 = max(int(math.floor(pts[:, 1].min() - extra)), 0)
        x1 = min(int(math.ceil(pts[:, 0].max() + extra)) + 1, self.w)
        y1 = min(int(math.ceil(pts[:, 1].max() + extra)) + 1, self.h)
        return x0, y0, max(x1, x0 + 1), max(y1, y0 + 1)

    def mask(self, s, grow=0.0, win=None):
        """boolean mask of shape s (grown by `grow` world units) inside window win."""
        if win is None:
            win = (0, 0, self.w, self.h)
        k = s[0]
        if k == 'and':
            return self.mask(s[1], grow, win) & self.mask(s[2], grow, win)
        if k == 'or':
            return self.mask(s[1], grow, win) | self.mask(s[2], grow, win)
        x0, y0, x1, y1 = win
        img = Image.new('L', (x1 - x0, y1 - y0), 0)
        dr = ImageDraw.Draw(img)

        def q(p):
            x, y = self.px(p)
            return (x - x0, y - y0)
        if k == 'line':
            wpx = (s[2] + 2 * grow) * self.s * self.ss
            pts = [q(p) for p in s[1]]
            dr.line(pts, fill=255, width=max(1, int(round(wpx))), joint='curve')
            r = wpx / 2
            for (x, y) in (pts[0], pts[-1]):
                dr.ellipse((x - r, y - r, x + r, y + r), fill=255)
        else:
            pts = [q(p) for p in shape_points(s, grow if k != 'poly' else 0.0)]
            dr.polygon(pts, fill=255)
            if k == 'poly' and grow > 0:
                wpx = 2 * grow * self.s * self.ss
                dr.line(pts + [pts[0]], fill=255, width=max(1, int(round(wpx))), joint='curve')
                r = wpx / 2
                for (x, y) in pts:
                    dr.ellipse((x - r, y - r, x + r, y + r), fill=255)
        return np.asarray(img) > 127


def shifted(m, dx, dy):
    """out[y, x] = m[y + dy, x + dx] (False outside)."""
    h, w = m.shape
    out = np.zeros_like(m)
    ys, yd = slice(max(dy, 0), h + min(dy, 0)), slice(max(-dy, 0), h + min(-dy, 0))
    xs, xd = slice(max(dx, 0), w + min(dx, 0)), slice(max(-dx, 0), w + min(-dx, 0))
    out[yd, xd] = m[ys, xs]
    return out


# ------------------------------------------------------------------ skeleton
class Body:
    def __init__(self, heads=4.0):
        d = heads - 4.0
        self.N = heads
        self.head = 1.0
        self.neck = 0.25
        self.torso = 1.0 + 0.4 * d
        self.leg = 1.75 + 0.6 * d
        self.ank = 0.12
        self.thigh = self.shin = (self.leg - self.ank) / 2
        self.upper = 0.62 + 0.13 * d
        self.fore = 0.56 + 0.12 * d
        self.hand = 0.09                 # wrist -> hand centre
        self.foot = 1.0 + 0.1 * d        # foot size factor


def solve(pose, B, weapon):
    """pose dict -> joint positions (world, y-down) + weapon geometry + IK misses."""
    J = {'miss': {}}
    hip = P(*pose['hip'])
    lean = pose.get('lean', 0.08)
    up = rot(v2(0, -1), lean)
    rt = rot(v2(1, 0), lean)
    T = B.torso

    def L(r, u):
        return hip + rt * r + up * u
    J['L'] = L
    J['hip'] = hip
    J['lean'] = lean
    sw = pose.get('sw', 1.0)
    J['SN'] = L(-0.40 * sw, T - 0.05)
    J['SF'] = L(0.34 * sw, T - 0.07)
    J['HN'] = L(-0.17, 0.0)
    J['HF'] = L(0.17, 0.0)
    J['neck0'] = L(0.04, T - 0.02)
    hup = rot(up, pose.get('tilt', 0.0))
    ho = pose.get('head_off', (0.0, 0.0))
    J['C'] = J['neck0'] + up * B.neck + hup * 0.55 + v2(ho[0], -ho[1])
    J['hang'] = lean * 0.5 + pose.get('tilt', 0.0)

    # legs
    for side in 'NF':
        tgt = P(*pose['foot' + side])
        knee, ank, miss = ik(J['H' + side], tgt, B.thigh, B.shin, pose.get('knee' + side, (1.0, 0.0)))
        J['knee' + side], J['ank' + side] = knee, ank
        J['miss']['leg' + side] = miss

    # weapon
    G = P(*pose['grip']) if 'grip' in pose else None
    d = wdir(pose.get('wa', 0.0))
    J['G'], J['d'] = G, d

    def hand_target(spec):
        if spec[0] == 'w':
            return G + d * spec[1]
        return P(spec[1], spec[2])
    for side in 'NF':
        spec = pose['hand' + side]
        tgt = hand_target(spec)
        elb, hand, miss = ik(J['S' + side], tgt, B.upper, B.fore + B.hand,
                             pose.get('elb' + side, (0.25, 1.0)))
        J['elb' + side], J['hand' + side] = elb, hand
        J['wrist' + side] = elb + norm(hand - elb) * B.fore
        J['miss']['arm' + side] = miss
        J['on' + side] = spec[0] == 'w'
    return J


# ------------------------------------------------------------------ mannequin parts
def head_parts(J, z0):
    C, a = J['C'], J['hang']
    hx, hy = rot(v2(1, 0), a), rot(v2(0, 1), a)

    def H(u, v):
        return C + hx * u + hy * v
    skull = ell(C, 0.43, 0.45, a)
    jaw = poly([H(-0.32, 0.02), H(-0.27, 0.30), H(-0.08, 0.49), H(0.14, 0.55), H(0.31, 0.47),
                H(0.41, 0.30), H(0.44, 0.06), H(0.2, -0.05), H(-0.2, -0.05)])
    hairline = poly([H(-0.75, -0.85), H(0.75, -0.85), H(0.75, -0.17), H(0.42, -0.15), H(0.22, -0.09),
                     H(0.04, -0.05), H(-0.02, 0.15), H(-0.10, 0.03), H(-0.28, 0.24), H(-0.50, 0.40),
                     H(-0.75, 0.40)])
    hair = ('and', ell(H(-0.03, -0.04), 0.48, 0.50, a), hairline)
    J['kp_nose'] = H(0.41, 0.30)
    J['kp_eyeN'] = H(0.12, 0.17)
    J['kp_eyeF'] = H(0.34, 0.16)
    J['kp_ear'] = H(-0.15, 0.11)
    return [
        ('head', ('or', skull, jaw), 'skin', z0, 0.16),
        ('hair', hair, 'hair', z0 + 1, 0.14),
        ('ear', ell(H(-0.15, 0.11), 0.07, 0.10, a), 'skin', z0 + 2, 0.04),
        ('eyeN', ell(H(0.12, 0.17), 0.05, 0.08, a), 'eye', z0 + 3, None),
        ('eyeF', ell(H(0.34, 0.16), 0.035, 0.075, a), 'eye', z0 + 3, None),
    ]


def leg_parts(J, B, side, pose, z0):
    hipj, knee, ank = J['H' + side], J['knee' + side], J['ank' + side]
    leg, boot = ('legN', 'bootN') if side == 'N' else ('legF', 'bootF')
    fa = math.radians(pose.get('fa' + side, 0.0))
    ts = pose.get('toe' + side, 1.0) * B.foot
    fx, fy = rot(v2(1, 0), fa), rot(v2(0, 1), fa)
    fs = abs(ts)
    sg = 1 if ts >= 0 else -1

    def F(u, v):
        return ank + fx * (u * ts) + fy * (v * fs)
    foot = poly([F(-0.15, 0.12), F(-0.17, -0.05), F(0.06, -0.08), F(0.20, 0.0), F(0.33, 0.03),
                 F(0.38, 0.09), F(0.36, 0.12)] if sg > 0 else
                [F(0.36, 0.12), F(0.38, 0.09), F(0.33, 0.03), F(0.20, 0.0), F(0.06, -0.08),
                 F(-0.17, -0.05), F(-0.15, 0.12)])
    b0 = knee + (ank - knee) * 0.42
    J['kp_toe' + side] = F(0.36, 0.12)
    return [
        ('thigh' + side, cap(hipj, knee, 0.20, 0.155), leg, z0, 0.13),
        ('shin' + side, cap(knee, ank, 0.15, 0.12), leg, z0 + 1, 0.10),
        ('boot' + side, ('or', cap(b0, ank, 0.165, 0.14), foot), boot, z0 + 2, 0.10),
    ]


def arm_parts(J, B, side, z_up, z_lo):
    S, e, w, h = J['S' + side], J['elb' + side], J['wrist' + side], J['hand' + side]
    col = 'armN' if side == 'N' else 'armF'
    skin = 'skin' if side == 'N' else 'skinF'
    ang = math.atan2(*(h - e)[::-1])
    return [
        ('upper' + side, cap(S, e, 0.14, 0.115), col, z_up, 0.09),
        ('fore' + side, cap(e, w, 0.115, 0.09), col, z_lo, 0.075),
        ('hand' + side, ell(h, 0.125, 0.10, ang), skin, z_lo + 1, 0.06),
    ]


def torso_parts(J, B, z0):
    L, T = J['L'], B.torso
    tor = poly([L(-0.44, T - 0.02), L(-0.28, T + 0.07), L(0.20, T + 0.08), L(0.40, T - 0.04),
                L(0.50, T - 0.30), L(0.46, T * 0.55), L(0.36, 0.30), L(0.36, 0.12), L(-0.36, 0.12),
                L(-0.38, 0.32), L(-0.45, T * 0.55), L(-0.48, T - 0.25)])
    pel = poly([L(-0.39, 0.18), L(0.38, 0.18), L(0.41, -0.08), L(0.18, -0.30), L(-0.18, -0.30),
                L(-0.43, -0.08)])
    belt = poly([L(-0.385, 0.27), L(0.375, 0.27), L(0.38, 0.12), L(-0.39, 0.12)])
    neck = cap(J['neck0'], J['C'] + rot(v2(0, 0.30), J['hang']), 0.12, 0.11)
    return [
        ('pelvis', pel, 'pelvis', z0, 0.12),
        ('torso', tor, 'torso', z0 + 1, 0.20),
        ('belt', belt, 'belt', z0 + 2, 0.05),
        ('neck', neck, 'skinF', z0 - 15, 0.07),      # neck goes behind the head (head z is >= 50)
    ]


def weapon_parts(J, weapon, pose):
    """returns [(name, shape, colour, z, shade_k)] for the weapon; z is filled in by the caller via
    the tags 'blade' (blade/head/bow) and 'handle'."""
    G, d = J['G'], J['d']
    out = []
    if weapon == 'none' or G is None:
        return out
    pn = np.array((d[1], -d[0])) * pose.get('edge', 1)          # spine side
    if weapon == 'katana':
        Lb = 1.95
        J['wtip'] = G + d * (0.04 + Lb) + pn * 0.07
        J['wbutt'] = G - d * 0.56
        out.append(('handle', cap(G - d * 0.56, G - d * 0.02, 0.055), 'wrap', 'handle', 0.03))
        out.append(('pommel', ell(G - d * 0.57, 0.06, 0.06), 'brass', 'handle', None))
        spine, edge = [], []
        n = 24
        for i in range(n + 1):
            t = i / n
            c = G + d * (0.04 + Lb * t) + pn * (0.07 * t * t)
            w = 0.075 * (1 - 0.3 * t)
            if t > 0.9:
                k = (t - 0.9) / 0.1
                spine.append(c + pn * w / 2)
                edge.append(c - pn * (w / 2) * (1 - k) + pn * (w / 2) * k * k)
            else:
                spine.append(c + pn * w / 2)
                edge.append(c - pn * w / 2)
        out.append(('blade', poly(spine + edge[::-1]), 'steel', 'blade', 0.03))
        out.append(('guard', ell(G, 0.045, 0.13, math.atan2(d[1], d[0])), 'brass', 'handle', 0.03))
    elif weapon == 'sword_shield':
        Lb = 1.35
        J['wtip'] = G + d * (0.05 + Lb)
        J['wbutt'] = G - d * 0.30
        out.append(('handle', cap(G - d * 0.28, G, 0.05), 'wrap', 'handle', 0.03))
        out.append(('pommel', ell(G - d * 0.31, 0.065, 0.065), 'brass', 'handle', None))
        b0 = G + d * 0.05
        tip = G + d * (0.05 + Lb)
        bl = [b0 + pn * 0.05, tip - d * 0.18 + pn * 0.04, tip, tip - d * 0.18 - pn * 0.04, b0 - pn * 0.05]
        out.append(('blade', poly(bl), 'steel', 'blade', 0.035))
        out.append(('guard', cap(G - pn * 0.2, G + pn * 0.2, 0.04), 'brass', 'handle', 0.03))
    elif weapon in ('spear', 'staff'):
        top, bot = (1.85, 1.2) if weapon == 'spear' else (1.55, 1.05)
        J['wtip'] = G + d * (top + (0.42 if weapon == 'spear' else 0.32))
        J['wbutt'] = G - d * bot
        out.append(('shaft', cap(G - d * bot, G + d * top, 0.045), 'wood', 'handle', 0.03))
        if weapon == 'spear':
            h0 = G + d * top
            hp = [h0 - d * 0.05 + pn * 0.035, h0 + d * 0.12 + pn * 0.08, h0 + d * 0.42,
                  h0 + d * 0.12 - pn * 0.08, h0 - d * 0.05 - pn * 0.035]
            out.append(('spearhead', poly(hp), 'steel', 'blade', 0.03))
        else:
            out.append(('crook', cap(G + d * top, G + d * (top + 0.10) + pn * 0.12, 0.06, 0.05), 'wood',
                        'blade', 0.03))
            out.append(('orb', ell(G + d * (top + 0.18), 0.14, 0.14), 'gem', 'blade', 0.06))
    elif weapon == 'bow':
        draw = pose.get('draw', 0.0)
        bn = np.array((-d[1], d[0]))                # bow axis (perpendicular to the aim)
        if bn[1] > 0:
            bn = -bn                                  # bn points up
        pts = []
        n = 12
        for i in range(-n, n + 1):
            s = i / n
            bend = 0.30 * s * s + draw * 0.10 * s * s
            pts.append(G + bn * (0.95 * s) - d * bend + d * 0.05 * (abs(s) ** 6) * 2)
        out.append(('bow', ('line', pts, 0.07), 'wood', 'blade', 0.03))
        nock = J['handN'] if pose.get('nocked') else None
        if nock is not None and draw > 0:
            out.append(('string', ('line', [pts[0], nock, pts[-1]], 0.018), 'string', 'string', None))
        else:
            out.append(('string', ('line', [pts[0], pts[-1]], 0.018), 'string', 'string', None))
        J['wtip'], J['wbutt'] = pts[-1], pts[0]
        if pose.get('nocked'):
            a0 = nock if nock is not None else G
            a1 = a0 + d * 1.25
            out.append(('arrow', ('line', [a0 - d * 0.05, a1], 0.03), 'wood', 'arrow', None))
            out.append(('arrowhead', poly([a1 + d * 0.16, a1 + bn * 0.05, a1 - bn * 0.05]), 'steel',
                        'arrow', None))
    return out


def shield_parts(J, pose):
    h, e = J['handF'], J['elbF']
    c = h + norm(e - h) * 0.12 + v2(*pose.get('shield_off', (0.02, 0.0)))
    a = math.radians(pose.get('shield_ang', -8))
    J['shield'] = c
    return [('shield', ell(c, 0.34, 0.45, a), 'shield', 66, 0.10),
            ('boss', ell(c + v2(-0.02, 0.0), 0.08, 0.10, a), 'steel', 67, 0.03)]


def build(pose, B, weapon):
    J = solve(pose, B, weapon)
    z = pose.get('z', {})
    parts = []
    parts += [p for p in arm_parts(J, B, 'F', 10, 12)]
    parts += leg_parts(J, B, 'F', pose, 20)
    parts += leg_parts(J, B, 'N', pose, 30)
    parts += torso_parts(J, B, 40)
    parts += head_parts(J, 50)
    if z.get('farfore', 'front') == 'front':
        parts = [(n, s, c, (62 if n == 'foreF' else 63) if n in ('foreF', 'handF') else zz, k)
                 for (n, s, c, zz, k) in parts]
    parts += arm_parts(J, B, 'N', 70, 72)
    zb = {'front': 60, 'back': 5, 'mid': 45, 'top': 80}[z.get('blade', 'front')]
    zh = {'front': 61, 'back': 6, 'mid': 46, 'top': 80}[z.get('handle', 'front')]
    for (n, s, c, tag, k) in weapon_parts(J, weapon, pose):
        zz = {'blade': zb, 'handle': zh, 'string': zb + 0.5, 'arrow': 75}[tag]
        if n in ('pommel', 'guard'):
            zz += 0.2
        parts.append((n, s, c, zz, k))
    if weapon == 'sword_shield':
        parts += shield_parts(J, pose)
    for k, v in z.items():                       # explicit per-part z overrides
        if k not in ('farfore', 'blade', 'handle'):
            parts = [(n, s, c, v if n == k else zz, kk) for (n, s, c, zz, kk) in parts]
    parts.sort(key=lambda p: p[3])
    return J, parts


# ------------------------------------------------------------------ renderers
def render_guide(parts, R, outline_px):
    rgb = np.empty((R.h, R.w, 3), np.uint8)
    rgb[:] = BG
    g = outline_px / R.s
    for (name, shp, col, _z, k) in parts:
        flat = col in ('eye', 'string')
        x0, y0, x1, y1 = R.window(shp, 0.0 if flat else g)
        view = rgb[y0:y1, x0:x1]
        if flat:
            view[R.mask(shp, 0.0, (x0, y0, x1, y1))] = PAL[col] if col == 'eye' else PAL[col][0]
            continue
        view[R.mask(shp, g, (x0, y0, x1, y1))] = PAL['outline']
        m = R.mask(shp, 0.0, (x0, y0, x1, y1))
        base, shade = PAL[col]
        view[m] = base
        if k:
            kp = k * R.s * R.ss
            dx, dy = int(round(SD[0] * kp)), int(round(SD[1] * kp))
            view[m & ~shifted(m, dx, dy)] = shade
    img = Image.fromarray(rgb, 'RGB')
    if R.ss > 1:
        img = img.reduce(R.ss)
    return img


# COCO-18 / OpenPose body: 0 nose 1 neck 2 Rsho 3 Relb 4 Rwri 5 Lsho 6 Lelb 7 Lwri 8 Rhip 9 Rknee
# 10 Rank 11 Lhip 12 Lknee 13 Lank 14 Reye 15 Leye 16 Rear 17 Lear.  Facing right in a front 3/4
# view the near (screen-left) side is the character's RIGHT side.
OP_LIMBS = [(1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11), (11, 12),
            (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17)]
OP_COLS = [(255, 0, 0), (255, 85, 0), (255, 170, 0), (255, 255, 0), (170, 255, 0), (85, 255, 0),
           (0, 255, 0), (0, 255, 85), (0, 255, 170), (0, 255, 255), (0, 170, 255), (0, 85, 255),
           (0, 0, 255), (85, 0, 255), (170, 0, 255), (255, 0, 255), (255, 0, 170), (255, 0, 85)]


def keypoints(J):
    k = [None] * 18
    k[0] = J['kp_nose']
    k[1] = (J['SN'] + J['SF']) / 2
    k[2], k[3], k[4] = J['SN'], J['elbN'], J['wristN']
    k[5], k[6], k[7] = J['SF'], J['elbF'], J['wristF']
    k[8], k[9], k[10] = J['HN'], J['kneeN'], J['ankN']
    k[11], k[12], k[13] = J['HF'], J['kneeF'], J['ankF']
    k[14], k[15], k[16] = J['kp_eyeN'], J['kp_eyeF'], J['kp_ear']
    k[17] = None                                   # far ear is hidden in this view
    return k


def render_stick(J, R, weapon_line=True):
    img = Image.new('RGB', (R.w, R.h), (0, 0, 0))
    sw = 7.0 * R.ss * R.s / 240.0 * 1.6
    kp = keypoints(J)
    if weapon_line and 'wtip' in J:
        dr = ImageDraw.Draw(img)
        dr.line([R.px(J['wbutt']), R.px(J['wtip'])], fill=(128, 128, 128), width=max(1, int(sw * 0.8)))
    arr = np.asarray(img).astype(np.float32)
    for i, (a, b) in enumerate(OP_LIMBS):
        if kp[a] is None or kp[b] is None:
            continue
        pa, pb = np.array(R.px(kp[a])), np.array(R.px(kp[b]))
        c = (pa + pb) / 2
        L = float(np.linalg.norm(pb - pa)) / 2
        ang = math.atan2(pb[1] - pa[1], pb[0] - pa[0])
        pts = np.array([c + rot(v2(L * math.cos(t), sw * math.sin(t)), ang)
                        for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)])
        x0, y0 = np.maximum(np.floor(pts.min(0)).astype(int) - 2, 0)
        x1, y1 = np.minimum(np.ceil(pts.max(0)).astype(int) + 2, (R.w, R.h))
        m = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).polygon([tuple(p - (x0, y0)) for p in pts], fill=255)
        m = np.asarray(m) > 127
        view = arr[y0:y1, x0:x1]
        view[m] = view[m] * 0.4 + np.array(OP_COLS[i], np.float32) * 0.6
    img = Image.fromarray(arr.astype(np.uint8), 'RGB')
    dr = ImageDraw.Draw(img)
    r = sw * 1.05
    for i, p in enumerate(kp):
        if p is None:
            continue
        x, y = R.px(p)
        dr.ellipse((x - r, y - r, x + r, y + r), fill=OP_COLS[i])
    if R.ss > 1:
        img = img.reduce(R.ss)
    return img


# ------------------------------------------------------------------ pose library
def grip_spec(weapon):
    return {
        'katana': (('w', -0.13), ('w', -0.45)),
        'sword_shield': (('w', -0.14), None),
        'spear': (('w', 0.0), ('w', -0.75)),
        'staff': (('w', 0.0), ('w', -0.65)),
        'bow': (None, ('w', 0.0)),
        'none': (None, None),
    }[weapon]


def frames(weapon, B):
    """the animation set as {name: pose}. Values are head units; heights are above the floor.
    Hip heights scale with the leg length so --heads 4..5 keeps the same stance."""
    k = B.leg / 1.75                                  # leg scale
    ka = (B.upper + B.fore) / 1.18                    # arm scale
    A = B.ank
    hN, hF = grip_spec(weapon)

    def body(hip, lean, fN, fF, **kw):
        p = dict(hip=(hip[0], hip[1] * k), lean=lean,
                 footN=(fN[0] * k, fN[1] if len(fN) > 1 else A), footF=(fF[0] * k, fF[1] if len(fF) > 1 else A))
        p.update(kw)
        return p

    def at(hip_h, x, h):
        """a point relative to the shoulder line (keeps grips valid for any --heads)."""
        return (x, hip_h * k + B.torso + (h - 2.40) * ka)

    F = {}
    # ---------------- legs / torso (shared by every weapon)
    stance = dict(fN=(-1.10,), fF=(1.00,))
    bob = [0.0, -0.015, -0.03, -0.015]
    idle = [body((0.0, 1.40 + b), 0.08, stance['fN'], stance['fF'], toeN=0.85) for b in bob]
    walk = [
        body((0.0, 1.54), 0.12, (-0.62, 0.17), (0.66,), faN=-22, toeN=0.9),
        body((0.0, 1.62), 0.10, (-0.06, 0.40), (0.18,), faN=22, toeN=0.9),
        body((0.0, 1.54), 0.12, (0.66,), (-0.62, 0.17), faF=-22),
        body((0.0, 1.62), 0.10, (0.18,), (-0.06, 0.40), faF=22),
    ]
    attack = [
        body((-0.08, 1.30), 0.00, (-1.10,), (0.98,), toeN=0.85),                     # anticipation
        body((-0.16, 1.26), -0.12, (-1.12,), (0.95,), toeN=0.85, tilt=0.06),          # wind-up
        body((0.32, 1.22), 0.30, (-1.05,), (1.42,), toeN=0.85, tilt=-0.05),           # strike (lunge)
        body((0.36, 1.18), 0.36, (-1.02,), (1.45,), toeN=0.85, tilt=-0.08),           # follow-through
        body((0.12, 1.34), 0.14, (-1.08,), (1.12,), toeN=0.85),                       # recover
    ]
    hit = [body((-0.22, 1.42), -0.24, (-1.02,), (0.96,), toeN=0.85, tilt=-0.22, head_off=(-0.06, -0.02),
                faF=-6)]
    cast = [
        body((-0.02, 1.46), 0.04, (-0.95,), (0.92,), toeN=0.85),
        body((-0.08, 1.50), -0.06, (-0.95,), (0.92,), toeN=0.85, tilt=0.06),
        body((0.12, 1.40), 0.16, (-1.00,), (1.10,), toeN=0.85, tilt=-0.03),
    ]
    for a, lst in (('idle', idle), ('walk', walk), ('attack', attack), ('hit', hit), ('cast', cast)):
        for i, p in enumerate(lst):
            F['%s_%d' % (a, i)] = p

    def arms(name, **kw):
        F[name].update(kw)

    def hh(name):
        return F[name]['hip'][1] / k

    # ---------------- arms / weapon per weapon family
    if weapon in ('katana', 'none'):
        for i in range(4):
            h = hh('idle_%d' % i)
            arms('idle_%d' % i, grip=at(h, 0.80, 1.98), wa=58, handN=hN, handF=hF)
        for i in range(4):
            h = hh('walk_%d' % i)
            arms('walk_%d' % i, grip=at(h, 0.80, 1.98 + (0.02 if i % 2 else 0.0)), wa=56 + (2 if i % 2 else 0),
                 handN=hN, handF=hF)
        # 0 anticipation: hands come up to the near shoulder, blade upright (hasso)
        arms('attack_0', grip=at(hh('attack_0'), 0.05, 2.58), wa=96, handN=hN, handF=hF,
             elbN=(-0.6, 1.0), elbF=(0.3, 1.0), z={'blade': 'mid', 'farfore': 'front'})
        # 1 wind-up: hands above the near shoulder, blade cocked back behind the head
        arms('attack_1', grip=at(hh('attack_1'), -0.20, 3.02), wa=150, handN=hN, handF=hF,
             elbN=(-1.0, 0.3), elbF=(0.6, 0.6), z={'blade': 'back', 'farfore': 'front'})
        # 2 strike: arms extended forward, blade cutting down-forward
        arms('attack_2', grip=at(hh('attack_2'), 1.22, 1.78), wa=-28, handN=hN, handF=hF,
             elbN=(0.0, 1.0), elbF=(0.0, 1.0))
        # 3 follow-through: blade carried low-forward
        arms('attack_3', grip=at(hh('attack_3'), 1.02, 1.32), wa=-30, handN=hN, handF=hF,
             elbN=(0.0, 1.0), elbF=(0.0, 1.0))
        # 4 recover: back toward the guard
        arms('attack_4', grip=at(hh('attack_4'), 0.86, 1.82), wa=36, handN=hN, handF=hF)
        arms('hit_0', grip=at(hh('hit_0'), 0.52, 1.62), wa=12, handN=hN, handF=hF, elbF=(1.0, 0.5))
        # cast (katana): blade lowered in the near hand, free hand channels
        arms('cast_0', grip=at(hh('cast_0'), -0.42, 1.55), wa=-120, handN=('w', -0.13),
             handF=('p',) + at(hh('cast_0'), 0.42, 2.12), elbF=(0.3, 1.0), elbN=(-0.5, 0.5))
        arms('cast_1', grip=at(hh('cast_1'), -0.46, 1.58), wa=-118, handN=('w', -0.13),
             handF=('p',) + at(hh('cast_1'), 0.66, 2.98), elbF=(0.6, 0.6), elbN=(-0.5, 0.5))
        arms('cast_2', grip=at(hh('cast_2'), -0.40, 1.52), wa=-122, handN=('w', -0.13),
             handF=('p',) + at(hh('cast_2'), 1.42, 2.36), elbF=(0.0, 1.0), elbN=(-0.5, 0.5))
        if weapon == 'none':
            for n in F:
                F[n].pop('grip', None)
                F[n]['handN'] = ('p', F[n]['hip'][0] + 0.55, F[n]['hip'][1] + 0.55)
                F[n]['handF'] = F[n]['handF'] if F[n]['handF'][0] == 'p' else ('p', F[n]['hip'][0] + 0.85,
                                                                              F[n]['hip'][1] + 0.62)
    elif weapon == 'sword_shield':
        for i in range(4):
            h = hh('idle_%d' % i)
            arms('idle_%d' % i, grip=at(h, 0.30, 1.62), wa=62, handN=hN,
                 handF=('p',) + at(h, 0.78, 2.02), elbF=(0.4, 1.0))
        for i in range(4):
            h = hh('walk_%d' % i)
            arms('walk_%d' % i, grip=at(h, 0.30, 1.62), wa=60, handN=hN,
                 handF=('p',) + at(h, 0.78, 2.02), elbF=(0.4, 1.0))
        arms('attack_0', grip=at(hh('attack_0'), -0.18, 2.40), wa=100, handN=hN,
             handF=('p',) + at(hh('attack_0'), 0.72, 2.05), elbN=(-1.0, 0.4))
        arms('attack_1', grip=at(hh('attack_1'), -0.50, 2.80), wa=150, handN=hN,
             handF=('p',) + at(hh('attack_1'), 0.80, 2.10), elbN=(-0.4, -1.0), z={'blade': 'back'})
        arms('attack_2', grip=at(hh('attack_2'), 1.05, 2.00), wa=-25, handN=hN,
             handF=('p',) + at(hh('attack_2'), 0.48, 1.70), elbN=(0.0, 1.0), shield_ang=-20)
        arms('attack_3', grip=at(hh('attack_3'), 0.90, 1.45), wa=-40, handN=hN,
             handF=('p',) + at(hh('attack_3'), 0.40, 1.80), elbN=(0.0, 1.0), shield_ang=-20)
        arms('attack_4', grip=at(hh('attack_4'), 0.40, 1.70), wa=50, handN=hN,
             handF=('p',) + at(hh('attack_4'), 0.80, 2.00))
        arms('hit_0', grip=at(hh('hit_0'), 0.00, 1.55), wa=20, handN=hN,
             handF=('p',) + at(hh('hit_0'), 0.62, 2.20), shield_ang=10)
        for i, (hx, hy) in enumerate(((0.55, 2.05), (0.70, 2.95), (1.35, 2.40))):
            arms('cast_%d' % i, grip=at(hh('cast_%d' % i), -0.30, 1.55), wa=-110, handN=hN,
                 handF=('p',) + at(hh('cast_%d' % i), hx, hy), elbN=(-0.5, 0.5))
    elif weapon in ('spear', 'staff'):
        for i in range(4):
            h = hh('idle_%d' % i)
            arms('idle_%d' % i, grip=at(h, 0.62, 2.00), wa=24 if weapon == 'spear' else 78, handN=hN, handF=hF)
        for i in range(4):
            h = hh('walk_%d' % i)
            arms('walk_%d' % i, grip=at(h, 0.62, 2.00), wa=22 if weapon == 'spear' else 78, handN=hN, handF=hF)
        if weapon == 'spear':
            arms('attack_0', grip=at(hh('attack_0'), 0.30, 1.95), wa=14, handN=hN, handF=hF)
            arms('attack_1', grip=at(hh('attack_1'), -0.15, 2.02), wa=8, handN=hN, handF=hF,
                 elbN=(-0.5, 1.0))
            arms('attack_2', grip=at(hh('attack_2'), 1.15, 2.05), wa=2, handN=hN, handF=hF)
            arms('attack_3', grip=at(hh('attack_3'), 1.10, 1.95), wa=-2, handN=hN, handF=hF)
            arms('attack_4', grip=at(hh('attack_4'), 0.65, 2.00), wa=16, handN=hN, handF=hF)
        else:
            arms('attack_0', grip=at(hh('attack_0'), 0.25, 2.30), wa=100, handN=hN, handF=hF)
            arms('attack_1', grip=at(hh('attack_1'), -0.15, 2.85), wa=140, handN=hN, handF=hF,
                 elbN=(-1.0, 0.3), z={'blade': 'back'})
            arms('attack_2', grip=at(hh('attack_2'), 1.05, 1.95), wa=-10, handN=hN, handF=hF)
            arms('attack_3', grip=at(hh('attack_3'), 0.95, 1.60), wa=-24, handN=hN, handF=hF)
            arms('attack_4', grip=at(hh('attack_4'), 0.65, 2.00), wa=60, handN=hN, handF=hF)
        arms('hit_0', grip=at(hh('hit_0'), 0.35, 1.70), wa=40 if weapon == 'staff' else 10, handN=hN,
             handF=hF)
        # cast: weapon in the near hand, planted / raised; free hand channels
        arms('cast_0', grip=at(hh('cast_0'), 0.10, 1.95), wa=84, handN=('w', 0.0),
             handF=('p',) + at(hh('cast_0'), 0.55, 2.10), elbN=(-0.6, 0.8))
        arms('cast_1', grip=at(hh('cast_1'), 0.05, 2.75), wa=88, handN=('w', 0.0),
             handF=('p',) + at(hh('cast_1'), 0.70, 2.80), elbN=(-0.8, 0.5))
        arms('cast_2', grip=at(hh('cast_2'), 0.55, 2.45), wa=60, handN=('w', 0.0),
             handF=('p',) + at(hh('cast_2'), 1.45, 2.40), elbN=(-0.3, 1.0))
    elif weapon == 'bow':
        def rest(h):
            return dict(grip=at(h, 0.80, 1.70), wa=-20, handF=hF, handN=('p',) + at(h, 0.05, 1.55),
                        elbF=(0.5, 1.0), nocked=False, draw=0.0)
        for n in ('idle_0', 'idle_1', 'idle_2', 'idle_3', 'walk_0', 'walk_1', 'walk_2', 'walk_3'):
            arms(n, **rest(hh(n)))
        h = hh('attack_0')
        arms('attack_0', grip=at(h, 0.95, 2.10), wa=5, handF=hF, handN=('p',) + at(h, 0.80, 2.12),
             nocked=True, draw=0.0, elbF=(0.0, 1.0))
        h = hh('attack_1')
        arms('attack_1', grip=at(h, 1.05, 2.25), wa=2, handF=hF, handN=('p',) + at(h, 0.35, 2.28),
             nocked=True, draw=0.5, elbF=(0.0, 1.0), elbN=(-0.3, -1.0))
        h = hh('attack_2')
        arms('attack_2', grip=at(h, 1.20, 2.30), wa=0, handF=hF, handN=('p',) + at(h, 0.05, 2.32),
             nocked=True, draw=1.0, elbF=(0.0, 1.0), elbN=(-0.3, -1.0))
        h = hh('attack_3')
        arms('attack_3', grip=at(h, 1.22, 2.28), wa=0, handF=hF, handN=('p',) + at(h, -0.15, 2.38),
             nocked=False, draw=0.0, elbF=(0.0, 1.0), elbN=(-0.3, -1.0))
        h = hh('attack_4')
        arms('attack_4', **rest(h))
        h = hh('hit_0')
        arms('hit_0', grip=at(h, 0.60, 1.60), wa=-35, handF=hF, handN=('p',) + at(h, -0.05, 1.70),
             elbF=(0.5, 1.0))
        for i, (hx, hy) in enumerate(((0.45, 2.05), (0.60, 2.95), (1.35, 2.40))):
            n = 'cast_%d' % i
            arms(n, grip=at(hh(n), -0.35, 1.70), wa=-100, handF=('p',) + at(hh(n), hx, hy),
                 handN=('w', 0.0), elbN=(-0.5, 0.5), elbF=(0.3, 1.0))
    return F


def stand_pose(B):
    """reference 'stand' frame for proportion checks (not part of the animation set)."""
    return dict(hip=(0.0, B.leg), lean=0.0, footN=(-0.17, B.ank), footF=(0.17, B.ank),
                handN=('p', -0.42, B.leg + B.torso - 0.05 - B.upper - B.fore - B.hand),
                handF=('p', 0.36, B.leg + B.torso - 0.07 - B.upper - B.fore - B.hand),
                elbN=(-1.0, 0.0), elbF=(1.0, 0.0), z={'farfore': 'back'})


# ------------------------------------------------------------------ fitting
def bbox(parts, only=None):
    xs, ys = [], []
    for (n, s, c, z, k) in parts:
        if only is not None and not only(n):
            continue
        for p in shape_points(s, 0.0):
            xs.append(p[0])
            ys.append(p[1])
        if s[0] == 'line':
            pts = np.array(s[1])
            r = s[2] / 2
            xs += [pts[:, 0].min() - r, pts[:, 0].max() + r]
            ys += [pts[:, 1].min() - r, pts[:, 1].max() + r]
    return min(xs), min(ys), max(xs), max(ys)


BODY_PARTS = {p + s for p in ('thigh', 'shin', 'boot', 'upper', 'fore', 'hand') for s in 'NF'} | {
    'torso', 'pelvis', 'belt', 'neck', 'head', 'hair', 'ear'}


def is_body(n):
    return n in BODY_PARTS


def fit(builds, W, H, feet, body_h, ref, margin):
    """one scale + origin for every frame: body of the reference frame = body_h px tall, feet on
    `feet`; body centred, then shifted / shrunk until every frame (weapon included) is inside."""
    bb = bbox(builds[ref][1], is_body)
    s = body_h / max(-bb[1], 1e-6)
    allb = [bbox(b[1]) for b in builds.values()]
    bodyb = [bbox(b[1], is_body) for b in builds.values()]
    x0 = min(b[0] for b in allb)
    x1 = max(b[2] for b in allb)
    y0 = min(b[1] for b in allb)
    bx0 = min(b[0] for b in bodyb)
    bx1 = max(b[2] for b in bodyb)
    s = min(s, (W - 2 * margin) / (x1 - x0), (feet - margin) / -y0)
    ox = W / 2 - (bx0 + bx1) / 2 * s
    ox = min(max(ox, margin - x0 * s), W - margin - x1 * s)
    return s, ox, feet


# ------------------------------------------------------------------ checks
def check(name, J, B, pose):
    msgs = []
    for k, v in J['miss'].items():
        if v > 1e-3:
            msgs.append('%s out of reach by %.3f' % (k, v))
    L = lambda a, b: float(np.linalg.norm(J[a] - J[b]))
    bones = {'thighN': L('HN', 'kneeN'), 'shinN': L('kneeN', 'ankN'), 'thighF': L('HF', 'kneeF'),
             'shinF': L('kneeF', 'ankF'), 'upperN': L('SN', 'elbN'), 'foreN': L('elbN', 'handN'),
             'upperF': L('SF', 'elbF'), 'foreF': L('elbF', 'handF')}
    want = {'thigh': B.thigh, 'shin': B.shin, 'upper': B.upper, 'fore': B.fore + B.hand}
    for k, v in bones.items():
        if abs(v - want[k[:-1]]) > 1e-3:
            msgs.append('bone %s %.3f != %.3f' % (k, v, want[k[:-1]]))
    for side in 'NF':
        planted = pose['foot' + side][1] <= B.ank + 1e-6
        if planted and abs(J['ank' + side][1] + B.ank) > 1e-3:
            msgs.append('foot%s off the baseline' % side)
    return msgs


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('out')
    ap.add_argument('--heads', type=float, default=4.0)
    ap.add_argument('--weapon', default='katana', choices=WEAPONS)
    ap.add_argument('--frames', default='')
    ap.add_argument('--ss', type=int, default=2, help='supersampling for the 832x1216 images')
    ap.add_argument('--no-stick-weapon', action='store_true')
    ap.add_argument('--check', action='store_true', help='also write stand.png (proportion ruler)')
    a = ap.parse_args(argv)
    if not 4.0 <= a.heads <= 5.0:
        ap.error('--heads must be in 4..5')
    B = Body(a.heads)
    F = frames(a.weapon, B)
    names = [n.strip() for n in a.frames.split(',') if n.strip()] or list(ALL_FRAMES)
    for n in names:
        if n not in F:
            ap.error('unknown frame %s (have %s)' % (n, ','.join(F)))
    os.makedirs(a.out, exist_ok=True)

    # fit on the full set so scale/origin never depend on --frames
    builds = {n: build(F[n], B, a.weapon) for n in ALL_FRAMES}
    gs, gox, goy = fit(builds, GW, GH, GH * GUIDE_FEET, GH * GUIDE_BODY, 'idle_0', 0.03 * GW)
    ss_, sox, soy = fit(builds, SW, SW, SMALL_FEET, SMALL_BODY, 'idle_0', 1.5)
    print('guide scale %.1f px/head (standing height %.0f px = %.0f%%), small %.1f px/head'
          % (gs, gs * B.N, 100 * gs * B.N / GH, ss_))
    bad = 0
    for n in names:
        J, parts = builds[n]
        for m in check(n, J, B, F[n]):
            print('  %s: %s' % (n, m))
            bad += 1
        Rg = Raster(GW, GH, gs, gox, goy, a.ss)
        render_guide(parts, Rg, 5.0).save(os.path.join(a.out, 'guide_%s.png' % n))
        render_stick(J, Rg, not a.no_stick_weapon).save(os.path.join(a.out, 'stick_%s.png' % n))
        Rs = Raster(SW, SW, ss_, sox, soy, 4)
        render_guide(parts, Rs, 0.9).save(os.path.join(a.out, 'small_%s.png' % n))
    if a.check:
        J, parts = build(stand_pose(B), B, 'none')
        Rg = Raster(GW, GH, gs, gox, goy, a.ss)
        img = render_guide(parts, Rg, 5.0)
        dr = ImageDraw.Draw(img)
        for i in range(int(B.N) + 1):
            y = goy - i * gs
            dr.line((40, y, 140, y), fill=(0, 0, 0), width=3)
            dr.text((150, y - 8), '%d' % i, fill=(0, 0, 0))
        img.save(os.path.join(a.out, 'stand.png'))
    write_sheet(a.out, names)
    write_gifs(a.out, names)
    print('wrote %d frames to %s (%d check warnings)' % (len(names), a.out, bad))
    return 0


def write_sheet(out, names):
    tw, th = GW // 4, GH // 4
    rows = []
    for an, n in ANIMS:
        r = [nm for nm in ('%s_%d' % (an, i) for i in range(n)) if nm in names]
        if r:
            rows.append(r)
    cols = max(len(r) for r in rows)
    sheet = Image.new('RGB', (cols * (tw + 8) + 8, len(rows) * (th + 24) + 8), (40, 40, 48))
    dr = ImageDraw.Draw(sheet)
    for j, r in enumerate(rows):
        for i, nm in enumerate(r):
            im = Image.open(os.path.join(out, 'guide_%s.png' % nm)).convert('RGB').resize((tw, th), Image.LANCZOS)
            x, y = 8 + i * (tw + 8), 8 + j * (th + 24)
            sheet.paste(im, (x, y + 16))
            dr.text((x + 2, y + 2), nm, fill=(230, 230, 230))
    sheet.save(os.path.join(out, 'sheet.png'))


def write_gifs(out, names, scale=3, ms=160):
    anims = []
    for an, n in ANIMS:
        fr = [nm for nm in ('%s_%d' % (an, i) for i in range(n)) if nm in names]
        if fr:
            anims.append((an, [Image.open(os.path.join(out, 'small_%s.png' % nm)).convert('RGB') for nm in fr]))
    if not anims:
        return
    for an, ims in anims:
        big = [im.resize((SW * scale, SW * scale), Image.NEAREST) for im in ims]
        big[0].save(os.path.join(out, 'anim_%s.gif' % an), save_all=True, append_images=big[1:],
                    duration=ms, loop=0, disposal=1)
    T = 1
    for _, ims in anims:
        T = T * len(ims) // math.gcd(T, len(ims))
    T = max(T, 1)
    strip = []
    for t in range(T):
        im = Image.new('RGB', (len(anims) * SW * scale, SW * scale), BG)
        for i, (_, ims) in enumerate(anims):
            im.paste(ims[t % len(ims)].resize((SW * scale, SW * scale), Image.NEAREST), (i * SW * scale, 0))
        strip.append(im)
    strip[0].save(os.path.join(out, 'anim.gif'), save_all=True, append_images=strip[1:], duration=ms,
                  loop=0, disposal=1)


if __name__ == '__main__':
    sys.exit(main())
