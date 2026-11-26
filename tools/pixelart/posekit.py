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
  leg (hip joint -> floor) 1.75 + 0.6*(N-4), torso (hip -> shoulder line) 1.05 + 0.4*(N-4),
  neck 0.20, head 1.0 (hair top -> chin, drawn at B.hs so it measures exactly 1); thigh = shin; 2-bone IK (lengths are exact in every frame) for
  legs (planted feet on the y=0 baseline) and arms (hands locked to points on the weapon).
  One scale for every frame of a run (fitted so the idle body is ~73% of the image height and
  every frame, weapon included, stays inside); only the x origin may slide per frame.
  Every run prints IK / bone-length / baseline violations (expected: 0 warnings).

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


# ------------------------------------------------------------------ natural arms (motion mannequins, 2026-11-26)
# Owner after gate 1: "팔이 어떻게 꺾이는지 좀 봐봐" - chicken-wing elbows (upper arm back behind the torso, forearm folding forward
# to the belly), elbows flaring forward above a hand that comes back to the belt, forearms crossing in a V. Cause: the elbow side was
# a fixed WORLD preference (0.25, 1.0) that ties when the hand hangs below the shoulder (lean flips it frame to frame), and hands
# placed too close to their shoulder for a hanging elbow. A pose with "arms": "natural" (the attack / hit / idle mannequin scripts)
# takes the anatomical side instead: the character faces +x (y down), so the elbow sits on (-d.y, d.x) of the shoulder -> hand
# direction d - back when the hand hangs, down when it reaches forward, forward when it is overhead. An explicit elbN / elbF still
# wins (bow draw, a deliberate raised elbow); check() then reports the arm's class (arm_eval) so a bad override is visible.
# Poses without "arms" (walk8 / run8 / gait8 / this file's own guides) keep the old preference: their output is byte-identical.
ARMS_VERSION = 'posekit natural-arms 1 (2026-11-26)'
ARM_BACK, ARM_BACK_WARN = -0.15, -0.08      # chicken-wing: elbow behind its own shoulder (torso heads) with the forearm running forward
ARM_WING_BENT = 115.0                       # ... and the elbow bent under this (a straighter arm hanging a little back is relaxed)
ARM_FOLD, ARM_FOLD_WARN = 20.0, 35.0        # inner elbow angle (180 = straight): under 20 the hand sits on the shoulder
ARM_FLARE = 0.15                            # flared: a reversed elbow this far in front of both the shoulder and the hand
ARM_CROSS = (0.30, -0.05)                   # crossing: elbow this far in front of the shoulder, hand behind it (and not raised:
                                            # a hand cocked above the shoulder behind the head has its elbow forward - natural)
ARM_STRAIGHT = 160.0                        # an arm straighter than this has no bend side
ARM_REV = 0.04                              # reversed only when the elbow is this far (heads) on the wrong side of shoulder -> hand
ARM_TUCK = (0.10, -0.35)                    # tucked (warn): hand over 0.10 above its shoulder, forearm running over 0.35 back to it
                                            # and the elbow above the hand - a hand wrapped behind the neck under a raised elbow
HANG_UPPER, HANG_FORE = 0.62, 0.65          # upper arm / forearm + hand (4-head Body) for hang_gap


def natural_pref(root, target):
    """the anatomical elbow side for a right-facing figure (world y-down): (-d.y, d.x) of root -> target"""
    d = np.asarray(target, float) - np.asarray(root, float)
    return np.array((-d[1], d[0]))


def torso_frame(hip, neck0, torso=1.05):
    """(rt, up) unit axes of the torso from the hip and the neck point (posekit neck0 = L(0.04, torso)), world y-down"""
    v = np.asarray(neck0, float) - np.asarray(hip, float)
    lean = math.atan2(v[0], -v[1]) - math.atan2(0.04, torso)
    return np.array((math.cos(lean), math.sin(lean))), np.array((math.sin(lean), -math.cos(lean))), lean


def arm_eval(S, E, H, hip, neck0, unit=1.0, torso=1.05, allow_draw=False):
    """classify one arm (shoulder S, elbow E, hand H; world y-down, `unit` = length of one head: 1 in posekit, 110 on the 384x1024 px
    frames). Torso coordinates: r forward, u up, heads, lean removed. Returns dict(level ok|warn|fail, cls, why, numbers):
      folded        inner elbow angle < 20 (warn < 35): the hand is on its own shoulder
      crossing      elbow > 0.30 in front of its shoulder while the hand is behind it and under shoulder + 0.20: the forearm crosses
                    the chest backwards (the V)
      flared        reversed hinge with the elbow > 0.15 in front of both the shoulder and the hand (elbow out front above a low hand)
      draw          reversed hinge, hand at/above the shoulder, elbow behind the hand and not dropped: the bow draw - ok only with
                    allow_draw (the string arm of a bow), else it is "hyper"
      hyper         any other reversed hinge (the elbow bends the wrong way)
      tucked        (warn) hand over 0.10 above its shoulder, the forearm running > 0.35 back to it and the elbow ABOVE the hand: the
                    hand is wrapped behind the neck / head under a raised elbow (a cocked weapon: the hand goes above the elbow)
      chicken-wing  elbow > 0.15 behind its own shoulder (warn > 0.08), bent under 115 deg, while the forearm runs > 0.35 forward
                    to a hand below the shoulder + 0.10: the upper arm points back behind the torso and the forearm folds forward again
    hang_gap = 0.65 - |hand - (shoulder - 0.62 up)|: > 0 means the hand cannot be reached with the elbow hanging under the shoulder
    (move the hand out / down by about that much)."""
    rt, up, lean = torso_frame(hip, neck0, torso)
    hip = np.asarray(hip, float)

    def tc(p):
        q = np.asarray(p, float) - hip
        return np.array((q @ rt, q @ up)) / unit
    s, e, h = tc(S), tc(E), tc(H)
    dE, dH = e - s, h - s
    reach = float(np.linalg.norm(dH))
    a, b = s - e, h - e
    inner = math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b) / max(1e-9, float(np.linalg.norm(a) * np.linalg.norm(b)))))))
    n = np.array((dH[1], -dH[0])) / max(reach, 1e-9)
    side = float(dE @ n)                                   # + = the natural side, heads off the shoulder -> hand line
    hang = HANG_FORE - float(np.linalg.norm(dH - np.array((0.0, -HANG_UPPER))))
    num = dict(inner_deg=round(inner, 1), side=round(side, 3), reach=round(reach, 3), hang_gap=round(hang, 3),
               elbow_back=round(float(dE[0]), 3), S=[round(float(x), 3) for x in s], E=[round(float(x), 3) for x in e],
               H=[round(float(x), 3) for x in h], lean_deg=round(math.degrees(lean), 1))
    out = dict(level='ok', cls='natural', why='', **num)

    def res(level, cls, why):
        out.update(level=level, cls=cls, why=why)
        return out
    if inner < ARM_FOLD:
        return res('fail', 'folded', f'elbow folded to {inner:.0f} deg (min {ARM_FOLD:.0f}): the hand is {reach:.2f} head from its '
                   f'shoulder - move it out to about 0.45+')
    if dE[0] > ARM_CROSS[0] and dH[0] < ARM_CROSS[1] and dH[1] < 0.20:
        return res('fail', 'crossing', f'elbow {dE[0]:+.2f} head in front of its shoulder, hand {dH[0]:+.2f} behind it: the forearm '
                   'crosses the chest backwards')
    if side < -ARM_REV and inner < ARM_STRAIGHT:
        drawn = dH[1] > -0.15 and e[0] < h[0] - 0.20 and dE[1] > -0.30
        if drawn and allow_draw:
            return res('ok', 'draw', f'raised elbow {e[0] - h[0]:+.2f} head behind the hand at shoulder height: the bow draw')
        if e[0] > max(h[0], s[0]) + ARM_FLARE:
            return res('fail', 'flared', f'elbow out front ({dE[0]:+.2f} head from its shoulder, {e[0] - h[0]:+.2f} ahead of the hand, '
                       f'{e[1] - h[1]:+.2f} above it): it bends the wrong way; hang_gap {hang:+.2f}')
        return res('fail', 'hyper', f'elbow bends the wrong way ({side:+.2f} head on the reversed side, inner {inner:.0f} deg)'
                   + (' - a raised elbow behind the hand is only the string arm of a bow (draw)' if drawn else ''))
    fwd = h[0] - e[0] > 0.35 and dH[1] < 0.10 and inner < ARM_WING_BENT
    if fwd and dE[0] < ARM_BACK:
        return res('fail', 'chicken-wing', f'elbow {-dE[0]:.2f} head behind its shoulder with the forearm running {h[0] - e[0]:.2f} '
                   f'forward to the hand: hang_gap {hang:+.2f} - move the hand about {max(hang, 0.05):.2f} head forward / down')
    if fwd and dE[0] < ARM_BACK_WARN:
        return res('warn', 'chicken-wing', f'elbow {-dE[0]:.2f} head behind its shoulder (borderline, fail at {-ARM_BACK:.2f})')
    if dH[1] > ARM_TUCK[0] and h[0] - e[0] < ARM_TUCK[1] and e[1] > h[1]:
        return res('warn', 'tucked', f'hand {dH[1]:.2f} head above its shoulder tucked {e[0] - h[0]:.2f} back under an elbow '
                   f'{e[1] - h[1]:.2f} above it: raise the hand above the elbow (a cocked weapon) or bring it forward')
    if inner < ARM_FOLD_WARN:
        return res('warn', 'folded', f'elbow folded to {inner:.0f} deg (under {ARM_FOLD_WARN:.0f}): hand {reach:.2f} head from its shoulder')
    if side < -ARM_REV:
        return res('warn', 'hyper', f'almost straight arm ({inner:.0f} deg) bent the wrong way')
    return out


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
        self.neck = 0.20
        self.hs = 1.0 / 1.09             # head drawing scale: hair top -> chin is exactly 1 head
        self.torso = 1.05 + 0.4 * d
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
    J['SN'] = L(-0.40 * pose.get('swN', sw), T - 0.05)       # swN / swF: one shoulder's spread only (the archer's bow / draw arm)
    J['SF'] = L(0.34 * pose.get('swF', sw), T - 0.07)
    hw = pose.get('hipw', 0.17)   # half spacing of the hip joints; a side-on walk uses 0.05 so the legs do not cross into an X
    J['HN'] = L(-hw, 0.0)
    J['HF'] = L(hw, 0.0)
    J['neck0'] = L(0.04, T)
    hup = rot(up, pose.get('tilt', 0.0))
    ho = pose.get('head_off', (0.0, 0.0))
    J['hs'] = B.hs
    J['C'] = J['neck0'] + up * B.neck + hup * (0.55 * B.hs) + v2(ho[0], -ho[1])   # chin sits on the neck
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
    natural = pose.get('arms') == 'natural'
    for side in 'NF':
        spec = pose['hand' + side]
        tgt = hand_target(spec)
        if 'elb' + side in pose:
            pref = pose['elb' + side]
        elif natural:
            pref = natural_pref(J['S' + side], tgt)
        else:
            pref = (0.25, 1.0)
        elb, hand, miss = ik(J['S' + side], tgt, B.upper, B.fore + B.hand, pref)
        J['elb' + side], J['hand' + side] = elb, hand
        J['wrist' + side] = elb + norm(hand - elb) * B.fore
        J['miss']['arm' + side] = miss
        J['on' + side] = spec[0] == 'w'
    return J


# ------------------------------------------------------------------ mannequin parts
def head_parts(J, z0):
    C, a, k = J['C'], J['hang'], J['hs']
    hx, hy = rot(v2(1, 0), a) * k, rot(v2(0, 1), a) * k

    def H(u, v):
        return C + hx * u + hy * v
    skull = ell(C, 0.43 * k, 0.45 * k, a)
    jaw = poly([H(-0.32, 0.02), H(-0.27, 0.30), H(-0.08, 0.49), H(0.14, 0.55), H(0.31, 0.47),
                H(0.41, 0.30), H(0.44, 0.06), H(0.2, -0.05), H(-0.2, -0.05)])
    hairline = poly([H(-0.75, -0.85), H(0.75, -0.85), H(0.75, -0.17), H(0.42, -0.15), H(0.22, -0.09),
                     H(0.04, -0.05), H(-0.02, 0.15), H(-0.10, 0.03), H(-0.28, 0.24), H(-0.50, 0.40),
                     H(-0.75, 0.40)])
    hair = ('and', ell(H(-0.03, -0.04), 0.48 * k, 0.50 * k, a), hairline)
    J['kp_nose'] = H(0.41, 0.30)
    J['kp_eyeN'] = H(0.12, 0.17)
    J['kp_eyeF'] = H(0.34, 0.16)
    J['kp_ear'] = H(-0.15, 0.11)
    return [
        ('head', ('or', skull, jaw), 'skin', z0, 0.16),
        ('hair', hair, 'hair', z0 + 1, 0.14),
        ('ear', ell(H(-0.15, 0.11), 0.07 * k, 0.10 * k, a), 'skin', z0 + 2, 0.04),
        ('eyeN', ell(H(0.12, 0.17), 0.05 * k, 0.08 * k, a), 'eye', z0 + 3, None),
        ('eyeF', ell(H(0.34, 0.16), 0.035 * k, 0.075 * k, a), 'eye', z0 + 3, None),
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
    neck = cap(J['neck0'], J['C'] + rot(v2(0, 0.30 * J['hs']), J['hang']), 0.12, 0.11)
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
        Lb = 1.62
        J['wtip'] = G + d * (0.04 + Lb) + pn * 0.06
        J['wbutt'] = G - d * 0.50
        out.append(('handle', cap(G - d * 0.50, G - d * 0.02, 0.055), 'wrap', 'handle', 0.03))
        out.append(('pommel', ell(G - d * 0.51, 0.06, 0.06), 'brass', 'handle', None))
        spine, edge = [], []
        n = 24
        for i in range(n + 1):
            t = i / n
            c = G + d * (0.04 + Lb * t) + pn * (0.06 * t * t)
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
        top, bot = (1.36, 0.76) if weapon == 'spear' else (1.45, 0.95)
        J['wtip'] = G + d * (top + (0.36 if weapon == 'spear' else 0.32))
        J['wbutt'] = G - d * bot
        out.append(('shaft', cap(G - d * bot, G + d * top, 0.045), 'wood', 'handle', 0.03))
        if weapon == 'spear':
            h0 = G + d * top
            hp = [h0 - d * 0.05 + pn * 0.035, h0 + d * 0.10 + pn * 0.08, h0 + d * 0.36,
                  h0 + d * 0.10 - pn * 0.08, h0 - d * 0.05 - pn * 0.035]
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


# ------------------------------------------------------------------ hit reaction keys
# Owner decision 2026-11-26 (art/requests/feedback.md): a hit reads as head and shoulders snapping AWAY from the blow and
# coming back, the knees absorbing it, the feet planted (one short stagger step at most), the weapon kept in hand, the face
# changing - never the old "torso thrown back, weight on the rear leg" body (lean -0.42, tilt -0.30, front knee pulled up),
# which the image model balanced by lifting the front knee. K1 = impact, K2 = deepest point, per character weight:
# heavy barely rocks, mid, light is pushed further (the back foot slides one short step back in K2).
# Values in head units as in frames(): hip = (x, height above the floor), footN / footF = x of the planted feet (the idle
# stance is -1.10 / 1.00), lean / tilt in radians (negative = back, away from the enemy on the right), head_off = extra
# head offset. Measured at 110 px/head (handoff.py hit_metrics): lean <= 15 deg, hip 12-30 px below idle, front foot and
# front knee never above their idle height, head displaced 20-30 (heavy) / 35-60 (mid) / 50-90 (light) px.
HIT_KEYS = {
    'k1_heavy': dict(hip=(-0.02, 1.29), lean=0.05, footN=-1.10, footF=1.00, tilt=-0.08, head_off=(-0.02, -0.03)),
    'k2_heavy': dict(hip=(-0.04, 1.26), lean=0.03, footN=-1.10, footF=1.00, tilt=-0.06, head_off=(-0.03, -0.03)),
    'k1_mid': dict(hip=(-0.05, 1.27), lean=0.00, footN=-1.10, footF=1.00, tilt=-0.12, head_off=(-0.04, -0.02)),
    'k2_mid': dict(hip=(-0.08, 1.21), lean=-0.06, footN=-1.10, footF=1.00, tilt=-0.10, head_off=(-0.04, -0.03)),
    'k1_light': dict(hip=(-0.08, 1.24), lean=-0.06, footN=-1.10, footF=1.00, tilt=-0.16, head_off=(-0.05, -0.02)),
    'k2_light': dict(hip=(-0.22, 1.15), lean=-0.15, footN=-1.40, footF=1.00, tilt=-0.12, head_off=(-0.05, -0.03)),
}
HIT_DEFAULT = 'k2_mid'          # the one hit slot of the 4-pose packages
HIT_ARM_REF = dict(hip=(-0.22, 1.38), lean=-0.24)   # the body the hit_0 arm targets below were authored on


def hit_body(key):
    """HIT_KEYS[key] as frames()-style body keywords (feet flat: no foot angle)."""
    b = dict(HIT_KEYS[key])
    return dict(b, toeN=0.85, faN=0, faF=0)


def arm_shift(pose, ref, B, k=1.0):
    """(dx, dy) that keeps arm targets authored on body `ref` at the same place relative to the shoulders of `pose`:
    the shoulder line moves with the hip x and the lean (at() already follows the hip height)."""
    T = B.torso
    dx = (pose['hip'][0] + math.sin(pose.get('lean', 0.08)) * T) - (ref['hip'][0] + math.sin(ref.get('lean', 0.08)) * T)
    dy = (math.cos(pose.get('lean', 0.08)) - math.cos(ref.get('lean', 0.08))) * T
    return dx, dy


def shift_arms(pose, dx, dy):
    """move the grip and every free hand target ('p', x, h) of a pose by (dx, dy) head units (dy = up)."""
    if 'grip' in pose:
        pose['grip'] = (pose['grip'][0] + dx, pose['grip'][1] + dy)
    for side in 'NF':
        sp = pose.get('hand' + side)
        if sp and sp[0] == 'p':
            pose['hand' + side] = ('p', sp[1] + dx, sp[2] + dy)


# ------------------------------------------------------------------ pose library
def grip_spec(weapon):
    return {
        'katana': (('w', -0.12), ('w', -0.40)),
        'sword_shield': (('w', -0.14), None),
        'spear': (('w', -0.62), ('w', 0.0)),     # near (right) hand at the rear
        'staff': (('w', -0.55), ('w', 0.0)),
        'bow': (None, ('w', 0.0)),
        'none': (None, None),
    }[weapon]


def frames(weapon, B):
    """the animation set as {name: pose}. Values are head units; heights are above the floor.
    Hip heights scale with the leg length so --heads 4..5 keeps the same stance."""
    k = B.leg / 1.75                                  # leg scale
    ka = (B.upper + B.fore) / 1.18                    # arm scale
    A = B.ank
    hN, hF = grip_spec('katana' if weapon == 'none' else weapon)

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
        body((0.0, 1.50), 0.12, (-0.62, 0.17), (0.64,), faN=-22, toeN=0.9),
        body((0.0, 1.60), 0.10, (-0.12, 0.52), (0.16,), faN=24, toeN=0.9, kneeN=(1.0, 0.0), kneeF=(1.0, 0.0)),
        body((0.0, 1.50), 0.12, (0.60,), (-0.66, 0.17), faF=-22),
        body((0.0, 1.60), 0.10, (-0.10,), (0.18, 0.40), faF=20, toeN=0.9, kneeF=(1.0, 0.0), kneeN=(1.0, 0.0)),
    ]
    attack = [
        body((-0.08, 1.30), 0.00, (-1.10,), (0.98,), toeN=0.85),                     # anticipation
        body((-0.20, 1.30), -0.12, (-1.12,), (0.80,), toeN=0.85, tilt=0.06),          # wind-up
        body((0.22, 1.20), 0.16, (-0.78,), (1.20,), toeN=0.85, tilt=-0.08),           # strike (lunge)
        body((0.30, 1.10), 0.40, (-0.90,), (1.26,), toeN=0.85, tilt=-0.10),           # follow-through
        body((0.12, 1.34), 0.14, (-1.08,), (1.12,), toeN=0.85),                       # recover
    ]
    hb = hit_body(HIT_DEFAULT)                        # K2-mid reaction (see HIT_KEYS)
    hit = [body(hb.pop('hip'), hb.pop('lean'), (hb.pop('footN'),), (hb.pop('footF'),), **hb)]
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
        arms('attack_0', grip=at(hh('attack_0'), -0.30, 2.50), wa=108, handN=hN, handF=hF,
             elbN=(-0.6, 1.0), elbF=(0.3, 1.0), z={'blade': 'mid', 'farfore': 'front'})
        # 1 wind-up: hands above the near shoulder, blade cocked back behind the head
        arms('attack_1', grip=at(hh('attack_1'), -1.00, 2.92), wa=234, handN=hN, handF=hF,
             elbN=(-1.0, 0.3), elbF=(0.3, 1.0), z={'blade': 'back', 'handle': 'back', 'farfore': 'back'})
        # 2 strike: arms extended forward, blade cutting down-forward
        arms('attack_2', grip=at(hh('attack_2'), 1.26, 1.96), wa=-54, handN=hN, handF=hF,
             elbN=(0.0, 1.0), elbF=(0.0, 1.0))
        # 3 follow-through: blade carried on down, low-forward
        arms('attack_3', grip=at(hh('attack_3'), 0.86, 1.58), wa=-54, handN=hN, handF=hF,
             elbN=(0.0, 1.0), elbF=(0.0, 1.0))
        # 4 recover: back toward the guard
        arms('attack_4', grip=at(hh('attack_4'), 0.80, 1.88), wa=48, handN=hN, handF=hF)
        arms('hit_0', grip=at(hh('hit_0'), 0.32, 1.72), wa=18, handN=hN, handF=hF, elbF=(1.0, 0.5))
        # cast (katana): blade lowered in the near hand, free hand channels
        arms('cast_0', grip=at(hh('cast_0'), -0.42, 1.55), wa=-120, handN=('w', -0.13),
             handF=('p',) + at(hh('cast_0'), 0.42, 2.12), elbF=(0.3, 1.0), elbN=(-0.5, 0.5))
        arms('cast_1', grip=at(hh('cast_1'), -0.46, 1.58), wa=-118, handN=('w', -0.13),
             handF=('p',) + at(hh('cast_1'), 0.66, 2.98), elbF=(0.6, 0.6), elbN=(-0.5, 0.5))
        arms('cast_2', grip=at(hh('cast_2'), -0.40, 1.52), wa=-122, handN=('w', -0.13),
             handF=('p',) + at(hh('cast_2'), 1.42, 2.36), elbF=(0.0, 1.0), elbN=(-0.5, 0.5))
        if weapon == 'none':                 # unarmed: fists stay where they held the katana
            for n, p in F.items():
                G, d = P(*p.pop('grip')), wdir(p.pop('wa'))
                for side in 'NF':
                    sp = p['hand' + side]
                    if sp[0] == 'w':
                        q = G + d * sp[1] + (v2(-0.06, 0.04) if side == 'N' else v2(-0.04, -0.06))
                        p['hand' + side] = ('p', q[0], -q[1])
                p.pop('z', None)
    elif weapon == 'sword_shield':
        for i in range(4):
            h = hh('idle_%d' % i)
            arms('idle_%d' % i, grip=at(h, 0.06, 1.66), wa=38, handN=hN,
                 handF=('p',) + at(h, 0.78, 2.02), elbF=(0.4, 1.0), z={'blade': 'top', 'handle': 'top'})
        for i in range(4):
            h = hh('walk_%d' % i)
            arms('walk_%d' % i, grip=at(h, 0.06, 1.66), wa=36, handN=hN,
                 handF=('p',) + at(h, 0.78, 2.02), elbF=(0.4, 1.0), z={'blade': 'top', 'handle': 'top'})
        arms('attack_0', grip=at(hh('attack_0'), -0.18, 2.40), wa=100, handN=hN,
             handF=('p',) + at(hh('attack_0'), 0.72, 2.05), elbN=(-1.0, 0.4))
        arms('attack_1', grip=at(hh('attack_1'), -0.50, 2.80), wa=150, handN=hN,
             handF=('p',) + at(hh('attack_1'), 0.80, 2.10), elbN=(-0.4, -1.0), z={'blade': 'back'})
        zs = {'shield': 58, 'boss': 58.5}
        arms('attack_2', grip=at(hh('attack_2'), 1.05, 2.00), wa=-25, handN=hN,
             handF=('p',) + at(hh('attack_2'), 0.62, 2.10), elbN=(0.0, 1.0), shield_ang=-20, z=zs)
        arms('attack_3', grip=at(hh('attack_3'), 0.90, 1.45), wa=-40, handN=hN,
             handF=('p',) + at(hh('attack_3'), 0.55, 2.10), elbN=(0.0, 1.0), shield_ang=-20, z=zs)
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
            arms('idle_%d' % i, grip=at(h, 0.62, 2.10), wa=34 if weapon == 'spear' else 78, handN=hN, handF=hF)
        for i in range(4):
            h = hh('walk_%d' % i)
            arms('walk_%d' % i, grip=at(h, 0.62, 2.10), wa=32 if weapon == 'spear' else 78, handN=hN, handF=hF)
        if weapon == 'spear':
            arms('attack_0', grip=at(hh('attack_0'), 0.40, 2.05), wa=18, handN=hN, handF=hF)
            arms('attack_1', grip=at(hh('attack_1'), 0.05, 2.05), wa=10, handN=hN, handF=hF,
                 elbN=(-0.5, 1.0))
            arms('attack_2', grip=at(hh('attack_2'), 0.70, 2.05), wa=3, handN=hN, handF=hF)
            arms('attack_3', grip=at(hh('attack_3'), 0.62, 1.98), wa=-1, handN=hN, handF=hF)
            arms('attack_4', grip=at(hh('attack_4'), 0.58, 2.05), wa=30, handN=hN, handF=hF)
        else:
            arms('attack_0', grip=at(hh('attack_0'), 0.52, 2.34), wa=98, handN=hN, handF=hF)
            arms('attack_1', grip=at(hh('attack_1'), -0.62, 2.72), wa=140, handN=hN, handF=hF,
                 elbN=(-1.0, 0.3), z={'blade': 'back', 'handle': 'mid'})
            arms('attack_2', grip=at(hh('attack_2'), 0.98, 2.00), wa=-40, handN=hN, handF=hF)
            arms('attack_3', grip=at(hh('attack_3'), 0.80, 1.66), wa=-48, handN=hN, handF=hF)
            arms('attack_4', grip=at(hh('attack_4'), 0.65, 2.00), wa=60, handN=hN, handF=hF)
        arms('hit_0', grip=at(hh('hit_0'), 0.40, 1.85), wa=40 if weapon == 'staff' else 14, handN=hN,
             handF=hF)
        # cast: weapon in the near hand, planted / raised; free hand channels
        zc = {'blade': 'mid', 'handle': 'mid'}
        arms('cast_0', grip=at(hh('cast_0'), -0.62, 1.95), wa=94, handN=('w', 0.0),
             handF=('p',) + at(hh('cast_0'), 0.50, 2.10), elbN=(-0.6, 0.8), z=zc)
        arms('cast_1', grip=at(hh('cast_1'), -0.62, 2.55), wa=96, handN=('w', 0.0),
             handF=('p',) + at(hh('cast_1'), 0.70, 2.85), elbN=(-0.8, 0.5), z=zc)
        arms('cast_2', grip=at(hh('cast_2'), 0.35, 2.55), wa=62, handN=('w', 0.0),
             handF=('p',) + at(hh('cast_2'), 1.40, 2.40), elbN=(-0.3, 1.0))
    elif weapon == 'bow':
        def rest(h):
            return dict(grip=at(h, 0.80, 1.70), wa=-20, handF=hF, handN=('p',) + at(h, 0.05, 1.55),
                        elbF=(0.5, 1.0), nocked=False, draw=0.0)
        for n in ('idle_0', 'idle_1', 'idle_2', 'idle_3', 'walk_0', 'walk_1', 'walk_2', 'walk_3'):
            arms(n, **rest(hh(n)))
        h = hh('attack_0')
        arms('attack_0', grip=at(h, 0.90, 2.10), wa=5, handF=hF, handN=('p',) + at(h, 0.72, 2.12),
             nocked=True, draw=0.0, elbF=(0.0, 1.0))
        for n in ('attack_1', 'attack_2', 'attack_3'):          # archers stay upright while drawing
            F[n].update(lean=0.06, tilt=0.0, hip=(F[n]['hip'][0] - 0.12, F[n]['hip'][1]))
        h = hh('attack_1')
        arms('attack_1', grip=at(h, 1.18, 2.30), wa=2, handF=hF, handN=('p',) + at(h, 0.35, 2.28),
             nocked=True, draw=0.5, elbF=(0.0, 1.0), elbN=(-0.3, -1.0))
        h = hh('attack_2')
        arms('attack_2', grip=at(h, 1.30, 2.34), wa=0, handF=hF, handN=('p',) + at(h, 0.00, 2.38),
             nocked=True, draw=1.0, elbF=(0.0, 1.0), elbN=(-0.3, -1.0))
        h = hh('attack_3')
        arms('attack_3', grip=at(h, 1.30, 2.32), wa=0, handF=hF, handN=('p',) + at(h, -0.25, 2.50),
             nocked=False, draw=0.0, elbF=(0.0, 1.0), elbN=(-0.3, -1.0))
        h = hh('attack_4')
        arms('attack_4', **rest(h))
        h = hh('hit_0')
        arms('hit_0', grip=at(h, 0.60, 1.60), wa=-35, handF=hF, handN=('p',) + at(h, -0.05, 1.70),
             elbF=(0.5, 1.0))
        for i, (hx, hy) in enumerate(((0.45, 2.05), (0.60, 2.95), (1.35, 2.40))):
            n = 'cast_%d' % i
            arms(n, grip=at(hh(n), -0.45, 1.62), wa=-172, handF=('p',) + at(hh(n), hx, hy),
                 handN=('w', 0.0), elbN=(-0.5, 0.5), elbF=(0.3, 1.0))
    # the hit_0 arm targets above were authored on HIT_ARM_REF: move them with the shoulders of the reaction body
    ref = dict(HIT_ARM_REF, hip=(HIT_ARM_REF['hip'][0], HIT_ARM_REF['hip'][1] * k))
    shift_arms(F['hit_0'], *arm_shift(F['hit_0'], ref, B, k))
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
    """One scale for every frame (so the character never changes size between frames) and a
    per-frame x origin. Scale: the reference frame's body (feet -> head top, weapon excluded) is
    body_h px tall, shrunk if any frame (weapon included) cannot fit. Origin: the reference body
    is centred; a frame whose weapon would leave the canvas is slid sideways just enough."""
    bb = bbox(builds[ref][1], is_body)
    s = body_h / max(-bb[1], 1e-6)
    boxes = {n: bbox(b[1]) for n, b in builds.items()}
    for n, b in boxes.items():
        s = min(s, (W - 2 * margin) / (b[2] - b[0]), (feet - margin) / -b[1])
    ox0 = W / 2 - (bb[0] + bb[2]) / 2 * s
    ox = {n: min(max(ox0, margin - b[0] * s), W - margin - b[2] * s) for n, b in boxes.items()}
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
    if 'wtip' in J:
        for nm in ('wtip', 'wbutt'):
            if J[nm][1] > 0.02:
                msgs.append('weapon %s %.2f below the floor' % (nm[1:], J[nm][1]))
    for side in 'NF':
        planted = pose['foot' + side][1] <= B.ank + 1e-6
        if planted and abs(J['ank' + side][1] + B.ank) > 1e-3:
            msgs.append('foot%s off the baseline' % side)
    if pose.get('arms') == 'natural':            # motion mannequins: the arm classes of check_skeleton.py --motion
        for side in 'NF':
            r = arm_eval(J['S' + side], J['elb' + side], J['hand' + side], J['hip'], J['neck0'], 1.0, B.torso,
                         allow_draw=pose.get('bow_draw') == side)
            if r['level'] != 'ok':
                ov = ' (elb%s override %s)' % (side, list(pose['elb' + side])) if 'elb' + side in pose else ''
                msgs.append('arm%s %s %s%s: %s' % (side, r['level'].upper(), r['cls'], ov, r['why']))
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
    gs, gox, goy = fit(builds, GW, GH, GH * GUIDE_FEET, GH * GUIDE_BODY, 'idle_0', 0.025 * GW)
    ss_, sox, soy = fit(builds, SW, SW, SMALL_FEET, SMALL_BODY, 'idle_0', 1.0)
    print('guide scale %.1f px/head (standing height %.0f px = %.0f%%), small %.1f px/head'
          % (gs, gs * B.N, 100 * gs * B.N / GH, ss_))
    bad = 0
    for n in names:
        J, parts = builds[n]
        for m in check(n, J, B, F[n]):
            print('  %s: %s' % (n, m))
            bad += 1
        Rg = Raster(GW, GH, gs, gox[n], goy, a.ss)
        render_guide(parts, Rg, 5.0).save(os.path.join(a.out, 'guide_%s.png' % n))
        render_stick(J, Rg, not a.no_stick_weapon).save(os.path.join(a.out, 'stick_%s.png' % n))
        Rs = Raster(SW, SW, ss_, sox[n], soy, 4)
        render_guide(parts, Rs, 0.9).save(os.path.join(a.out, 'small_%s.png' % n))
    if a.check:
        J, parts = build(stand_pose(B), B, 'none')
        Rg = Raster(GW, GH, gs, gox['idle_0'], goy, a.ss)
        img = render_guide(parts, Rg, 5.0)
        dr = ImageDraw.Draw(img)
        for i in range(int(B.N) + 1):
            y = goy - i * gs
            dr.line((40, y, 140, y), fill=(0, 0, 0), width=3)
            dr.line((40, y, GW - 40, y), fill=(0, 0, 0), width=1)
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
