#!/usr/bin/env python3
"""Baren "검귀" (Sword Demon) battle sprite generator — 80x80 HD pixel-art style.

Final version (draft B + judge fixes + grafts from drafts A/C):
  * ~3.6-head proportions: small head template (15x17), longer shins, wide low stance.
  * Near arm held across the chest, hands at the sternum, blade raised ~38 deg (ref rifle hold).
  * Crimson scarf/collar between head and tunic; tunic one value above the charcoal trousers.
  * Cape: 3 clean fold valleys radiating from the shoulder pin, notched hem, lining peeks.
  * Headband tails: 2 tapered ribbons (long + short), tips move <= 1px per idle frame.
  * Palette discipline: every pixel is a ramp tone (rim light / lines / outlines snapped),
    one global dark outline for the shadow side, ~50-60 colours per frame.
  * Idle uses whole-pixel offsets only (head moves with the torso), so shading never boils.
  * Hit frame: real pose change (recoil, head snapped back, eyes shut, guard dropped),
    fully opaque, no baked tint (the engine applies its own flash).

Pipeline per frame:
  pose (skeleton + IK) -> parts rasterised as shapes with pseudo-normals
  -> directional light + cast shadows -> quantised into hue-shifted ramps
  -> orphan cleanup -> internal contour lines -> rim light -> selective outline
  -> slash smear overlay.

Usage: python3 baren_hd.py OUT_DIR  ->  OUT_DIR/frames/{anim}_{n}.png
       (+ OUT_DIR/preview.png, hero.png, onefx.png for review)
Python 3 + Pillow + NumPy only. Deterministic: no randomness.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

W = H = 80
FOOT = 76
X, Y = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)

# ---------------------------------------------------------------- palette
# ramps go dark -> light; shadows drift to cool violet/blue, lights to warm.
RAMP = {
    'cloak': [(34, 12, 24), (58, 20, 32), (84, 24, 34), (108, 30, 38), (142, 46, 44), (172, 76, 60)],
    'lining': [(24, 12, 26), (44, 18, 34)],
    'tunic': [(20, 23, 38), (30, 35, 54), (42, 49, 72), (58, 67, 92), (82, 92, 116)],
    'pants': [(15, 16, 20), (24, 26, 30), (35, 38, 40), (50, 54, 54), (70, 75, 72)],
    'greave': [(58, 56, 76), (94, 94, 112), (136, 136, 146), (178, 176, 176), (214, 210, 198)],
    'boot': [(18, 14, 22), (30, 24, 31), (46, 36, 40), (66, 52, 50), (92, 74, 64)],
    'leather': [(30, 19, 24), (54, 33, 31), (84, 55, 43), (116, 81, 57), (150, 112, 76)],
    'skin': [(62, 40, 58), (112, 80, 96), (158, 124, 128), (194, 164, 156), (222, 200, 186)],
    'hair': [(18, 12, 20), (31, 21, 28), (47, 31, 35), (68, 45, 42), (96, 66, 54), (128, 94, 72)],
    'band': [(70, 72, 100), (154, 160, 184), (190, 194, 210), (226, 228, 234), (246, 244, 236)],
    'steel': [(32, 38, 56), (66, 76, 100), (112, 124, 148), (164, 176, 194), (210, 218, 230), (250, 250, 246)],
    'brass': [(40, 27, 25), (80, 56, 38), (128, 95, 56), (180, 142, 82), (220, 188, 120)],
    'wrap': [(18, 15, 24), (34, 27, 38), (54, 42, 54)],
    'mark': [(96, 52, 66), (206, 156, 158)],
}
MATS = list(RAMP.keys())
MID = {m: i for i, m in enumerate(MATS)}
OUTD = (14, 11, 20)                      # the one global dark outline (shadow side / ground contact)
RIM_STEP = {'hair': 2, 'cloak': 2, 'skin': 1, 'band': 1, 'tunic': 2, 'pants': 2, 'boot': 2}
LIGHT = np.array((-0.52, -0.62, 0.6))
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def v2(x, y):
    return np.array((float(x), float(y)))


def norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v * 0


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array((v[0] * c - v[1] * s, v[0] * s + v[1] * c))


def ik(root, target, l1, l2, bend, tag=''):
    """2-bone IK; bend=+1/-1 chooses the side of the joint. Lengths are preserved."""
    d = target - root
    dist = np.linalg.norm(d)
    dist_c = min(max(dist, abs(l1 - l2) + 0.05), l1 + l2 - 0.05)
    if abs(dist - dist_c) > 0.6:
        print('  ik %s: target out of reach by %.1f' % (tag, dist - dist_c))
    dirv = d / dist
    a = (l1 * l1 - l2 * l2 + dist_c * dist_c) / (2 * dist_c)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    perp = np.array((-dirv[1], dirv[0])) * bend
    joint = root + dirv * a + perp * h
    end = root + dirv * dist_c
    return joint, end


# ---------------------------------------------------------------- shapes
# each returns (mask, nx, ny)

def sh_capsule(a, b, ra, rb):
    ab = b - a
    L2 = max(ab @ ab, 1e-6)
    t = np.clip(((X - a[0]) * ab[0] + (Y - a[1]) * ab[1]) / L2, 0, 1)
    cx, cy = a[0] + ab[0] * t, a[1] + ab[1] * t
    r = ra + (rb - ra) * t
    dx, dy = X - cx, Y - cy
    d = np.sqrt(dx * dx + dy * dy)
    m = d <= r
    return m, dx / np.maximum(r, 0.5), dy / np.maximum(r, 0.5)


def sh_ellipse(c, rx, ry):
    nx, ny = (X - c[0]) / rx, (Y - c[1]) / ry
    m = nx * nx + ny * ny <= 1.0
    return m, nx, ny


def poly_mask(pts):
    pts = np.asarray(pts, float)
    m = np.zeros((H, W), bool)
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if y1 == y2:
            continue
        cond = (Y >= min(y1, y2)) & (Y < max(y1, y2))
        xi = x1 + (Y - y1) * (x2 - x1) / (y2 - y1)
        m ^= cond & (X < xi)
    return m


def sh_poly(pts, bevel=3.0, strength=0.9):
    """polygon with a bevelled pseudo-normal (rounded edges, flat middle)."""
    pts = np.asarray(pts, float)
    m = poly_mask(pts)
    best = np.full((H, W), 1e9)
    bx = np.zeros((H, W))
    by = np.zeros((H, W))
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ab = b - a
        L2 = max(ab @ ab, 1e-6)
        t = np.clip(((X - a[0]) * ab[0] + (Y - a[1]) * ab[1]) / L2, 0, 1)
        qx, qy = a[0] + ab[0] * t, a[1] + ab[1] * t
        d = np.hypot(X - qx, Y - qy)
        sel = d < best
        best = np.where(sel, d, best)
        bx = np.where(sel, qx - X, bx)
        by = np.where(sel, qy - Y, by)
    dn = np.maximum(best, 1e-6)
    f = np.clip(1 - best / bevel, 0, 1) * strength
    return m, bx / dn * f, by / dn * f


def sh_union(*shapes):
    m = np.zeros((H, W), bool)
    nx = np.zeros((H, W))
    ny = np.zeros((H, W))
    for (mm, x, y) in shapes:
        nx = np.where(mm, x, nx)
        ny = np.where(mm, y, ny)
        m |= mm
    return m, nx, ny


def shift(a, dx, dy, fill):
    """shift a 2-D array by (dx, dy) without wrap-around."""
    out = np.full_like(a, fill)
    ys = slice(max(dy, 0), H + min(dy, 0))
    yd = slice(max(-dy, 0), H + min(-dy, 0))
    xs = slice(max(dx, 0), W + min(dx, 0))
    xd = slice(max(-dx, 0), W + min(-dx, 0))
    out[yd, xd] = a[ys, xs]
    return out


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.mat = np.full((H, W), -1, int)
        self.val = np.zeros((H, W))
        self.pid = np.full((H, W), -1, int)
        self.grp = np.full((H, W), -1, int)
        self.nx = np.zeros((H, W))
        self.ny = np.zeros((H, W))
        self.fixed = np.full((H, W), -1, int)      # explicit ramp index (overrides light)
        self.parts = []                              # (name, line_flag, rimmable)
        self.groups = {}

    def _register(self, name, line, rimmable, group):
        idx = len(self.parts)
        self.parts.append((name, line, rimmable))
        g = self.groups.setdefault(group or name, len(self.groups))
        return idx, g

    def part(self, name, mat, shape, group=None, line=True, bias=0.0, cast=0.0,
             fold=None, rimmable=True, flat=0.0, vadd=None, clip=None):
        m, nx, ny = shape
        if clip is not None:
            m = m & clip
        if not m.any():
            return None
        idx, g = self._register(name, line, rimmable, group)
        if fold is not None:
            nx = nx + fold(X, Y)
        if flat:
            nx, ny = nx * (1 - flat), ny * (1 - flat)
        r2 = np.clip(nx * nx + ny * ny, 0, 0.95)
        nz = np.sqrt(1 - r2)
        ln = np.sqrt(r2 + nz * nz)
        dif = np.clip((nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / ln, 0, 1)
        v = 0.08 + 0.78 * dif + bias
        if vadd is not None:
            v = v + vadd(X, Y)
        if cast:
            sh = np.zeros_like(m)
            sh[2:, 1:] = m[:-2, :-1]
            sh2 = np.zeros_like(m)
            sh2[1:, 1:] = m[:-1, :-1]
            hit = (sh | sh2) & ~m & (self.mat >= 0)
            self.val = np.where(hit, self.val - cast, self.val)
        self.mat = np.where(m, MID[mat], self.mat)
        self.val = np.where(m, v, self.val)
        self.pid = np.where(m, idx, self.pid)
        self.grp = np.where(m, g, self.grp)
        self.nx = np.where(m, nx, self.nx)
        self.ny = np.where(m, ny, self.ny)
        self.fixed = np.where(m, -1, self.fixed)
        return m

    def pixels(self, name, mat, pix, group=None, line=True, rimmable=False):
        """explicit pixels: list of (x, y, ramp_index)."""
        m = np.zeros((H, W), bool)
        f = np.full((H, W), -1, int)
        for (x, y, i) in pix:
            if 0 <= x < W and 0 <= y < H:
                m[y, x] = True
                f[y, x] = i
        if not m.any():
            return
        idx, g = self._register(name, line, rimmable, group)
        self.mat = np.where(m, MID[mat], self.mat)
        self.pid = np.where(m, idx, self.pid)
        self.grp = np.where(m, g, self.grp)
        self.fixed = np.where(m, f, self.fixed)
        self.nx = np.where(m, 0.0, self.nx)
        self.ny = np.where(m, 0.0, self.ny)

    def template(self, name, rows, legend, ox, oy, group=None, line=True):
        """hand-placed pixel block: each char -> (material, ramp index). '.' = empty."""
        m = np.zeros((H, W), bool)
        mat = np.full((H, W), -1, int)
        f = np.full((H, W), -1, int)
        rimn = np.zeros((H, W))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == '.' or ch == ' ':
                    continue
                x, y = ox + i, oy + j
                if 0 <= x < W and 0 <= y < H:
                    mt, ix = legend[ch]
                    m[y, x] = True
                    mat[y, x] = MID[mt]
                    f[y, x] = ix
                    rimn[y, x] = 1.0 if mt == 'hair' else 0.0
        idx, g = self._register(name, line, True, group)
        self.mat = np.where(m, mat, self.mat)
        self.pid = np.where(m, idx, self.pid)
        self.grp = np.where(m, g, self.grp)
        self.fixed = np.where(m, f, self.fixed)
        self.nx = np.where(m, rimn * 0.7, self.nx)
        self.ny = np.where(m, rimn * -0.5, self.ny)
        return m

    # ------------------------------------------------------------ render
    def render(self, rim=True):
        mat, val = self.mat, self.val.copy()
        op = mat >= 0
        # ground falloff: lower legs sink into shade
        val -= np.clip(Y - 60, 0, None) * 0.006
        idx = np.zeros((H, W), int)
        for m in MATS:
            n = len(RAMP[m])
            sel = mat == MID[m]
            idx = np.where(sel, np.clip(np.floor(val * n), 0, n - 1).astype(int), idx)
        idx = np.where(self.fixed >= 0, self.fixed, idx)
        idx = self.cleanup(idx, op)

        # internal contour: back pixel next to a front part of another group -> darkest ramp tone
        line = np.zeros((H, W), bool)
        lineflag = np.array([p[1] for p in self.parts] + [False])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q_pid = shift(self.pid, dx, dy, -1)
            q_grp = shift(self.grp, dx, dy, -1)
            front = (q_pid > self.pid) & (q_grp != self.grp) & (q_pid >= 0) & op
            front &= lineflag[q_pid]
            line |= front
        idx = np.where(line, 0, idx)

        # rim light on silhouette edges facing up-right (cool back light): snapped to a ramp tone
        if rim:
            rimflag = np.array([p[2] for p in self.parts] + [False])
            edge_r = op & ~shift(op, 1, 0, False)
            edge_u = op & ~shift(op, 0, -1, False)
            facing = (self.nx * 0.85 - self.ny * 0.45) > 0.25
            sel = (edge_r | edge_u) & rimflag[self.pid] & ~line & facing
            for m in MATS:
                s = sel & (mat == MID[m])
                n = len(RAMP[m])
                idx = np.where(s, np.minimum(idx + RIM_STEP.get(m, 2), n - 1), idx)

        rgb = np.zeros((H, W, 3))
        for m in MATS:
            ramp = np.array(RAMP[m], float)
            sel = mat == MID[m]
            rgb[sel] = ramp[idx[sel]]

        # selective outline (outside, 4-neighbour). Light comes from the upper left:
        # the top/left outline takes the material's own darkest tone (coloured, softer),
        # the right/bottom outline (shadow side, ground contact) uses the global dark.
        out = np.zeros((H, W, 3))
        outm = np.zeros((H, W), bool)
        for dx, dy, lit in ((0, 1, True), (1, 0, True), (-1, 0, False), (0, -1, False)):
            nb = shift(mat, dx, dy, -1)
            cand = (~op) & (nb >= 0) & ~outm
            if lit:
                for m in MATS:
                    sel = cand & (nb == MID[m])
                    out[sel] = RAMP[m][0]
                    outm |= sel
            else:
                out[cand] = OUTD
                outm |= cand
        # anything resting on the ground gets the dark line under it
        rgb = np.where(outm[..., None], out, rgb)
        alpha = (op | outm).astype(np.uint8) * 255
        return np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), alpha])

    def cleanup(self, idx, op):
        """remove orphan tone pixels inside one part (single pixels unlike all same-part neighbours)."""
        for _ in range(2):
            new = idx.copy()
            pid = self.pid
            for y in range(1, H - 1):
                for x in range(1, W - 1):
                    if not op[y, x] or self.fixed[y, x] >= 0:
                        continue
                    p = pid[y, x]
                    ns = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                    same = [idx[b, a] for (a, b) in ns if pid[b, a] == p]
                    if len(same) >= 3 and all(s != idx[y, x] for s in same):
                        vals, cnt = np.unique(same, return_counts=True)
                        new[y, x] = vals[np.argmax(cnt)]
            idx = new
        return idx


# ---------------------------------------------------------------- pixel lines
def bres(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return pts


# ---------------------------------------------------------------- head template (15x17, faces right)
# hair a..f (0..5) | skin 1..5 (0..4) | band U V W Z (1..4) | k eye, B brow | s/t scar light/dark
HEAD = [
    "..ab...........",
    ".abc...bc......",
    "abcd..bcd..c...",
    ".bcdd.bcdd.cd..",
    "abcdeebcdeecdd.",
    ".abcdeedcdeedcc",
    "aabccdddccddccb",
    "abbbcccbcccbccb",
    "UVVVWWWWWZZZZWb",
    "aUUVVVWWWWWWVcb",
    "abbbbcb3c4cc3c.",
    ".abbbbb4443433.",
    ".abbbb34kk43k3.",
    "..abb124s44433.",
    "...ab2ts43m3...",
    "....a2234433...",
    "......1222.....",
]
HEAD_WINCE = list(HEAD)
HEAD_WINCE[11] = ".abbbbb4444343."
HEAD_WINCE[12] = ".abbbb3BBB43B3."
HEAD_ORG = (7, 9)        # template pixel placed on the head centre C
HEAD_KNOT = (0, 8)       # headband knot (tails start here)
HEAD_NECK = (8, 16)      # chin/neck join
HEAD_LEGEND = {
    'a': ('hair', 0), 'b': ('hair', 1), 'c': ('hair', 2), 'd': ('hair', 3), 'e': ('hair', 4), 'f': ('hair', 5),
    '1': ('skin', 0), '2': ('skin', 1), '3': ('skin', 2), '4': ('skin', 3), '5': ('skin', 4),
    'U': ('band', 1), 'V': ('band', 2), 'W': ('band', 3), 'Z': ('band', 4),
    'k': ('hair', 0), 'B': ('hair', 0), 's': ('mark', 1), 't': ('mark', 0), 'm': ('skin', 1),
}


# ---------------------------------------------------------------- the character
LT, LS = 15.5, 17.5                        # thigh / shin lengths (long legs, ~41% of height)
CAPE_FOLDS = (0.18, 0.46, 0.74)            # fold valleys as fractions of the cape's angular span


def draw(P):
    cv = Canvas()
    hip = P['hip']
    lean = P['lean']
    up = rot(v2(0, -1), lean)
    rt = rot(v2(1, 0), lean)

    def L(r, u):  # torso-local -> screen
        return hip + rt * r + up * u

    S = L(0.5, 17)                     # shoulder centre
    Sn = L(-5.0, 16.0)                 # near shoulder (screen-left)
    Sf = L(5.0, 16.2)                  # far shoulder
    Hn = L(-3.4, 0.5)
    Hf = L(3.6, 0.0)
    C = L(2.0, 24.6) + P.get('head_off', v2(0, 0))   # head centre
    hx = int(round(C[0])) - HEAD_ORG[0]
    hy = int(round(C[1])) - HEAD_ORG[1]
    knot = v2(hx + HEAD_KNOT[0], hy + HEAD_KNOT[1])

    # ---------------- sword geometry
    G = P['grip']                        # guard position
    sd = norm(v2(*P['sword_dir']))
    blade_len = P.get('blade_len', 29)
    tip = G + sd * blade_len
    pommel = G - sd * 7.5
    handN = G - sd * 2.0                 # near/top hand
    handF = G - sd * 5.4                 # far/bottom hand

    def sword():
        cv.part('handle', 'wrap', sh_capsule(pommel, G, 1.2, 1.2), bias=0.0)
        cv.part('pommel', 'brass', sh_ellipse(pommel - sd * 0.4, 1.3, 1.3), bias=0.1)
        pr = np.array((-sd[1], sd[0]))
        cv.part('guard', 'brass', sh_capsule(G - pr * 2.6, G + pr * 2.6, 1.1, 1.1), bias=0.12)
        # blade: two clean bresenham rails (spine + edge); fixed specular band (no idle boil)
        b0 = G + sd * 1.2
        rail = bres(b0[0], b0[1], tip[0], tip[1])
        n = len(rail)
        if abs(sd[0]) >= abs(sd[1]):
            off = (0, 1)
        else:
            off = (1, 0) if sd[1] < 0 else (-1, 0)
        gl = P.get('glint', 0.32)
        pix = []
        for i, (x, y) in enumerate(rail):
            t = i / max(n - 1, 1)
            spine, edge = 2, 3
            if abs(t - gl) < 0.07:
                spine, edge = 4, 5
            elif abs(t - gl) < 0.14:
                spine, edge = 3, 4
            if t > 0.9:
                edge = 4
            pix.append((x, y, spine))
            if i < n - 2:
                pix.append((x + off[0], y + off[1], edge))
        cv.pixels('blade', 'steel', pix, line=True, rimmable=False)

    # ---------------- back cape (polar coords around the shoulder pin)
    sway = P.get('cape', 0.0)
    flare = P.get('flare', 0.0)
    ca = Sn + v2(1.0, -1.0)
    thL, thR = 131 + flare * 3, 80
    fold_th = [math.radians(thR + (thL - thR) * f) for f in CAPE_FOLDS]
    brot = math.radians(sway * 6.0 + flare * 9.0)

    def cape_polar(xx, yy):
        dx, dy = xx - ca[0], yy - ca[1]
        r = np.hypot(dx, dy)
        th = np.arctan2(dy, dx) - brot * np.clip(r / 28.0, 0, 1)
        return r, th

    def fold_d(r, th):
        """signed pixel distance (along the arc) to the nearest fold valley."""
        best = None
        for ft in fold_th:
            d = r * (th - ft)
            best = d if best is None else np.where(np.abs(d) < np.abs(best), d, best)
        return best

    def hem_r(th_deg):
        th = math.radians(th_deg)
        d = fold_d(30.0, th)
        notch = 1.8 * max(0.0, 1.0 - abs(float(d)) / 2.4)
        return 31.0 - flare * 2.0 - notch + 2.0 * math.sin((th_deg - 80) / 50 * math.pi)

    def cape_pt(th_deg, r):
        th = math.radians(th_deg) + brot * min(r / 28.0, 1.0)
        return ca + v2(math.cos(th) * r, math.sin(th) * r)

    cape_pts = [ca + v2(8.5, -0.5), ca + v2(3, -2.2), ca + v2(-1.5, -0.6)]
    cape_pts += [cape_pt(thL - 2, 9), cape_pt(thL, 18)]
    NS = 40
    for i in range(NS + 1):
        td = thL - (thL - thR) * i / NS
        cape_pts.append(cape_pt(td, hem_r(td)))
    cape_pts += [cape_pt(thR, 14), ca + v2(9, 4)]

    def cape_v(xx, yy):
        r, th = cape_polar(xx, yy)
        d = fold_d(r, th)
        amp = np.clip((r - 5) / 6, 0, 1)
        valley = (np.abs(d) < 1.0) * -0.42
        ridge = ((d >= 1.0) & (d < 3.2)) * 0.2          # lit ridge on the light side of each valley
        front = (th < math.radians(thR + 4)) * 0.0
        return amp * (valley + ridge) + front - np.clip((r - 24) / 8, 0, 1) * 0.08

    cmask = poly_mask(cape_pts)
    cv.part('cape_back', 'cloak', sh_poly(cape_pts, bevel=2.5, strength=0.35), bias=-0.08, vadd=cape_v)
    # lit crimson band along the front edge of the cape
    r_, th_ = cape_polar(X, Y)
    front_band = cmask & (r_ * (th_ - math.radians(thR)) < 2.2) & (r_ > 8) & (Y < hip[1] + 1)
    cv.part('cape_front', 'cloak', (front_band, np.zeros((H, W)), np.zeros((H, W))), group='cape_back',
            line=False, bias=0.52, rimmable=True)

    # lining glimpsed in the fold valleys right at the hem
    def lin_mask():
        r, th = cape_polar(X, Y)
        d = fold_d(r, th)
        thd = np.degrees(th)
        hr = 31.0 - flare * 2.0 + 2.0 * np.sin((thd - 80) / 50 * np.pi)
        m = (np.abs(d) < 1.6) & (r > hr - 4.2) & cmask
        return m, np.zeros((H, W)), np.zeros((H, W))
    cv.part('cape_lin', 'lining', lin_mask(), group='cape_back', line=False, bias=0.1, rimmable=False)

    # ---------------- headband tails: two tapered ribbons (behind head, over cape)
    ta = P.get('tail_ang', 0.0)
    tl = P.get('tail_len', 0.0)
    toff = P.get('tail_off', (0, 0))
    pix = []
    for k, (ln, ang, dy0) in enumerate(((11, 12, 0), (6, 44, 2))):
        Lk = ln + tl * (1.0 if k == 0 else 0.6)
        a = math.radians(ang + ta * (1.0 if k == 0 else 0.8))
        s0 = knot + v2(-1, dy0)
        e = s0 + v2(-math.cos(a) * Lk, math.sin(a) * Lk)
        pts = bres(s0[0], s0[1], e[0], e[1])
        n = len(pts)
        for i, (x, y) in enumerate(pts):
            t = i / max(n - 1, 1)
            y += int(round(toff[k] * t))          # tip moves at most 1px, root stays fixed
            wide = t < (0.45 if k == 0 else 0.3)
            pix.append((x, y, 3 if t < 0.8 else 2))
            if wide:
                pix.append((x, y + 1, 1))
    cv.pixels('tails', 'band', pix, group='tails', line=True, rimmable=False)

    # ---------------- far arm (behind torso)
    elbF, endF = ik(Sf, handF, 9.4, 8.8, P.get('bendF', 1), 'armF')
    cv.part('armF_up', 'tunic', sh_capsule(Sf, elbF, 2.6, 2.3), group='armF', bias=-0.14)
    cv.part('armF_lo', 'tunic', sh_capsule(elbF, endF, 2.3, 2.0), group='armF', bias=-0.12)
    cv.part('armF_br', 'leather', sh_capsule(elbF + (endF - elbF) * 0.45, endF - norm(endF - elbF) * 0.6, 2.4, 2.3),
            group='armF', bias=-0.1, line=False)

    # ---------------- legs
    def leg(prefix, hipj, ank, bend, bias, toe_dir, grp):
        knee, ankr = ik(hipj, ank, LT, LS, bend, prefix)
        cv.part(prefix + 'thigh', 'pants', sh_capsule(hipj, knee, 4.0, 3.1), group=grp, bias=bias + 0.06)
        cv.part(prefix + 'shin', 'pants', sh_capsule(knee, ankr, 3.0, 2.4), group=grp, bias=bias - 0.02)
        sdir = norm(ankr - knee)
        # pale greave / shin wrap + knee cop (the ref's pale knees)
        g0 = knee + sdir * 1.6
        g1 = knee + sdir * 9.5
        cv.part(prefix + 'greave', 'greave', sh_capsule(g0, g1, 2.7, 2.5), group=grp + 'g', bias=bias + 0.06,
                cast=0.1)
        cv.part(prefix + 'knee', 'greave', sh_ellipse(knee + v2(0.3 * toe_dir, -0.2), 2.6, 2.3), group=grp + 'g',
                bias=bias + 0.1)
        # boot: shaft + foot
        b0 = knee + sdir * 9.8
        toe = ankr + v2(4.6 * toe_dir, 2.4)
        heel = ankr + v2(-2.2 * toe_dir, 2.4)
        foot = [ankr + v2(-2.8 * toe_dir, -2.0), ankr + v2(2.3 * toe_dir, -1.6), toe + v2(0, -1.6),
                toe + v2(0.6 * toe_dir, 0.6), heel + v2(0, 0.6), heel + v2(-0.3 * toe_dir, -1.2)]
        if toe_dir < 0:
            foot = foot[::-1]
        cv.part(prefix + 'boot', 'boot', sh_union(sh_capsule(b0, ankr, 2.9, 2.8),
                                                  sh_poly(foot, bevel=2, strength=0.7)),
                group=grp + 'b', bias=bias + 0.04, cast=0.12)
        cv.part(prefix + 'toecap', 'greave', sh_ellipse(ankr + v2(3.6 * toe_dir, 1.4), 1.9, 1.3), group=grp + 'b',
                bias=bias - 0.08, line=False)
        cuff = [b0 + v2(-3.2, -0.6), b0 + v2(3.2, -0.6), b0 + v2(3.2, 1.0), b0 + v2(-3.2, 1.0)]
        cv.part(prefix + 'cuff', 'boot', sh_poly(cuff, bevel=1.2, strength=0.8), group=grp + 'b', bias=bias + 0.12)
        return knee, ankr

    leg('F_', Hf, P['footF'], P.get('kneeF', -1), -0.06, 1, 'legF')
    pel = [L(-5.6, 3), L(5.6, 3), L(6.0, -2.5), L(3.5, -5.0), L(-4.0, -5.0), L(-6.4, -2)]
    cv.part('pelvis', 'pants', sh_poly(pel, bevel=3, strength=0.7), group='legN', bias=-0.08)
    leg('N_', Hn, P['footN'], P.get('kneeN', -1), -0.02, 1, 'legN')

    # ---------------- torso (tunic, one value step above the trousers)
    tor = [L(-7.0, 16.2), L(-4.5, 17.8), L(3.5, 17.8), L(6.4, 16.0), L(7.4, 11.0), L(6.0, 5),
           L(5.2, 1.0), L(-5.6, 1.0), L(-6.6, 6), L(-7.6, 11)]
    cv.part('torso', 'tunic', sh_poly(tor, bevel=4.5, strength=0.85), bias=0.06, cast=0.15)
    cv.part('lapel', 'tunic', sh_capsule(L(1.0, 16.6), L(2.0, 4.0), 0.75, 0.6), group='torso', bias=0.34, line=False)
    cv.part('seam', 'tunic', sh_capsule(L(2.2, 16.0), L(3.0, 4.0), 0.5, 0.45), group='torso', bias=-0.5, line=False,
            rimmable=False)
    sk = [L(-6.0, 2.0), L(5.6, 2.0), L(7.0, -3.6), L(4.6, -5.4), L(1.8, -4.2), L(-1.4, -6.0),
          L(-4.6, -4.6), L(-7.4, -5.6)]
    cv.part('skirt', 'tunic', sh_poly(sk, bevel=2.5, strength=0.8), group='skirt', bias=0.0, cast=0.18,
            fold=lambda xx, yy: 0.45 * np.sin((xx - hip[0]) * 1.1))
    belt = [L(-6.4, 3.6), L(6.0, 3.6), L(6.2, 0.9), L(-6.6, 0.9)]
    cv.part('belt', 'leather', sh_poly(belt, bevel=1.3, strength=0.8), bias=-0.04, cast=0.12)
    strap_a, strap_b = L(-5.2, 16.0), L(5.4, 3.2)
    cv.part('strap', 'leather', sh_capsule(strap_a, strap_b, 1.1, 1.1), bias=0.0, cast=0.1)
    cv.part('buckle', 'brass', sh_ellipse(L(1.8, 2.25), 1.6, 1.4), bias=0.1, line=False)
    cv.part('pouch', 'leather', sh_poly([L(-6.6, 1.2), L(-3.6, 1.2), L(-3.6, -3.4), L(-6.8, -3.0)],
                                        bevel=1.5, strength=0.8), bias=-0.06, cast=0.12)

    # ---------------- capelet over the near shoulder (raised 2px so the arm shows) + scarf
    cs = P.get('capelet', 0.0)

    def cl(x, y):
        return S + rot(v2(x, y), lean * 0.6) + v2(-cs * max(0, y) / 10, 0)

    capelet = [cl(3.5, -2.2), cl(-1.5, -3.4), cl(-7.0, -2.0), cl(-9.6, 1.0), cl(-10.4, 4.6),
               cl(-9.6, 7.6), cl(-7.6, 6.6), cl(-5.8, 8.0), cl(-3.6, 6.4), cl(-1.6, 6.8), cl(0.2, 4.0),
               cl(3.0, 1.0)]

    def capelet_fold(xx, yy):
        dx, dy = xx - S[0], yy - (S[1] - 3)
        th = np.arctan2(dy, dx)
        r = np.hypot(dx, dy)
        return np.clip((r - 4) / 6, 0, 1) * 0.5 * np.sin(th * 7.0 + 1.2)

    cv.part('capelet', 'cloak', sh_poly(capelet, bevel=3.0, strength=0.85), bias=0.0, cast=0.2,
            fold=capelet_fold)
    # crimson scarf/collar: a warm value break between face and tunic
    collar = [cl(-3.5, -4.8), cl(4.4, -4.4), cl(4.8, -0.8), cl(1.5, 0.6), cl(-4.0, -0.8)]
    cv.part('collar', 'cloak', sh_poly(collar, bevel=1.8, strength=0.9), bias=0.2, cast=0.15)
    cv.part('brooch', 'brass', sh_ellipse(cl(-1.0, -0.6), 1.2, 1.2), bias=0.12, line=True)

    # ---------------- near arm (drawn over the capelet: the arm crosses the chest)
    def near_arm():
        elbN, endN = ik(Sn, handN, 9.6, 9.0, P.get('bendN', 1), 'armN')
        cv.part('armN_up', 'tunic', sh_capsule(Sn, elbN, 2.9, 2.5), group='armN', bias=0.2, cast=0.18)
        cv.part('armN_lo', 'tunic', sh_capsule(elbN, endN, 2.5, 2.1), group='armN', bias=0.2, cast=0.18)
        cv.part('armN_br', 'leather', sh_capsule(elbN + (endN - elbN) * 0.5, endN - norm(endN - elbN) * 0.8,
                                                 2.4, 2.2), group='armN', bias=0.16, line=False, cast=0.1)

    if P.get('sword_back'):
        sword()
    # ---------------- head (hand-pixelled template)
    neck_top = v2(hx + HEAD_NECK[0] + 0.5, hy + HEAD_NECK[1] + 0.5)
    cv.part('neck', 'skin', sh_capsule(L(1.2, 18), neck_top, 2.0, 2.0), group='head', bias=-0.32)
    rows = HEAD_WINCE if P.get('wince') else HEAD
    cv.template('head', rows, HEAD_LEGEND, hx, hy, group='head')

    if not P.get('sword_back'):
        cv.part('handF', 'skin', sh_ellipse(handF, 1.9, 1.8), bias=-0.1)
        sword()
    near_arm()
    if P.get('sword_back'):
        cv.part('handF', 'skin', sh_ellipse(handF, 1.9, 1.8), bias=-0.1)
    cv.part('handN', 'skin', sh_ellipse(handN + v2(0, -0.2), 2.0, 1.9), bias=0.02, cast=0.15)

    img = cv.render()

    # ---------------- slash smear
    if P.get('smear'):
        keep_names = {'blade', 'guard', 'handle', 'pommel', 'handN', 'handF'}
        ids = [i for i, p in enumerate(cv.parts) if p[0] in keep_names]
        keep = np.isin(cv.pid, ids)
        k2 = keep.copy()
        k2[1:] |= keep[:-1]
        k2[:-1] |= keep[1:]
        k2[:, 1:] |= keep[:, :-1]
        k2[:, :-1] |= keep[:, 1:]
        k2 &= img[..., 3] > 0
        saved = img.copy()
        smear(img, tip=tip, **P['smear'])
        img[k2] = saved[k2]
    return img


SMEAR_COLS = [(255, 255, 250), (214, 240, 252), (150, 206, 238), (96, 150, 210)]


def smear(img, tip, c, a0, thick, alpha=1.0, clip_y=62, pad=1.0, a1=None, r=None):
    """crescent arc of radius |tip-c| centred on c, sweeping from angle a0 (deg, screen y-down) to the
    blade tip; thickest at the blade. Opaque tones over the body (no new blended colours);
    over empty space the outer, fainter tones use a fixed alpha."""
    cx, cy = c
    r_out = (r if r is not None else math.hypot(tip[0] - cx, tip[1] - cy)) + pad
    if a1 is None:
        a1 = math.degrees(math.atan2(tip[1] - cy, tip[0] - cx))
    ang = np.degrees(np.arctan2(Y - cy, X - cx))
    span = a1 - a0
    t = ((ang - a0) * np.sign(span)) % 360 / abs(span)
    inside = t <= 1.0
    d = np.hypot(X - cx, Y - cy)
    tt = np.clip(t, 0, 1)
    th = thick * (0.1 + 0.9 * tt ** 1.2)
    m = inside & (d <= r_out) & (d >= r_out - th) & (th >= 0.7)
    m &= (X > 2) & (X < W - 2) & (Y > 3) & (Y < clip_y)
    depth = r_out - d
    k = np.where(depth < 1.0, 0, np.where(depth < 2.4, 1, np.where(depth < 4.0, 2, 3)))
    k = np.where(tt < 0.25, np.maximum(k, 2), k)       # the trailing end is only the cool tones
    body = img[..., 3] == 255
    for i, col in enumerate(SMEAR_COLS):
        sel = m & (k == i)
        a_empty = int(255 * alpha * (1.0, 0.95, 0.8, 0.6)[i])
        over_body = sel & body & (alpha >= 0.7 or i <= 1)
        img[over_body, :3] = col
        img[over_body, 3] = 255
        emp = sel & ~body
        img[emp, :3] = col
        img[emp, 3] = a_empty


# ---------------------------------------------------------------- poses
BASE = dict(
    hip=v2(37, 46), lean=0.10,
    footF=v2(53.5, 73.0), footN=v2(19.5, 73.0),
    grip=v2(47.0, 36.0), sword_dir=(1.0, -0.78),
    cape=0.0, flare=0.0, capelet=0.0,
    bendN=1, bendF=1, kneeF=-1, kneeN=-1,
    tail_off=(0, 0), tail_ang=0.0, tail_len=0.0,
)


def pose(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def add(v, dx, dy):
    return v + v2(dx, dy)


def frames():
    F = {}
    # idle: whole-pixel breathing (upper body + grip move together), ribbon tips +-1px, cape sways a hair
    bob = [0, 0, 1, 1]
    toffs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    capes = [0.0, 0.25, 0.25, 0.0]
    F['idle'] = [pose(hip=add(BASE['hip'], 0, bob[i]), grip=add(BASE['grip'], 0, bob[i]),
                      tail_off=toffs[i], cape=capes[i]) for i in range(4)]
    # walk: real steps in guard. contact = body down 1px, passing = up 1px with the swing foot lifted 3px.
    hx = 38.0
    steps = [  # footF, footN, dy, kneeF, kneeN
        (v2(hx + 14, 73.0), v2(hx - 14, 73.0), 1),
        (v2(hx + 8, 73.0), v2(hx - 4, 70.0), -1),
        (v2(hx - 12, 73.0), v2(hx + 14, 73.0), 1),
        (v2(hx - 2, 70.0), v2(hx + 8, 73.0), -1),
    ]
    F['walk'] = []
    for i, (fF, fN, dy) in enumerate(steps):
        ph = i * math.pi / 2
        F['walk'].append(pose(hip=v2(hx, BASE['hip'][1] + dy), footF=fF, footN=fN,
                              grip=add(BASE['grip'], 1, dy), lean=0.16, cape=0.6 * math.sin(ph) + 0.4,
                              flare=0.5, tail_ang=-4, tail_len=1, tail_off=((0, 1, 1, 0)[i], (1, 1, 0, 0)[i]),
                              capelet=0.4 * math.sin(ph)))
    A = []
    # 0 anticipation: sink, hands to the near shoulder, blade up and back (hasso)
    A.append(pose(hip=v2(35.5, 47.5), lean=0.0, grip=v2(33.5, 33.5), sword_dir=(-0.26, -1.0), blade_len=24,
                  footF=v2(53.0, 73.0), footN=v2(18.5, 73.0), cape=0.5, tail_ang=6, sword_back=True,
                  bendN=1, bendF=1, glint=0.2))
    # 1 wind-up: blade cocked behind the head, hips lower, shoulders turned back
    A.append(pose(hip=v2(34.5, 48.5), lean=-0.1, grip=v2(32.0, 27.0), sword_dir=(-0.9, 0.42), blade_len=23,
                  footF=v2(52.5, 73.0), footN=v2(18.0, 73.0), cape=0.9, flare=0.2, tail_ang=-12, tail_len=1,
                  sword_back=True, bendN=1, bendF=1, glint=0.5, head_off=v2(-0.5, 0.5)))
    # 2 slash: lunge, blade cuts down-forward, big crescent from behind the head to the blade tip
    A.append(pose(hip=v2(41, 47.5), lean=0.28, grip=v2(54, 44), sword_dir=(0.85, 0.5), blade_len=23,
                  footF=v2(58.5, 73.0), footN=v2(21.0, 73.0), cape=1.6, flare=1.0, tail_ang=-14, tail_len=2,
                  capelet=1.0, glint=0.45, bendN=-1, bendF=-1, head_off=v2(1, 1),
                  smear=dict(c=(46, 42), a0=-165, thick=8.5)))
    # 3 follow-through: blade carried on down-forward clear of the knee, smear tail fading
    A.append(pose(hip=v2(41.5, 48), lean=0.22, grip=v2(53, 50), sword_dir=(1.0, 0.1), blade_len=21,
                  footF=v2(59.0, 73.0), footN=v2(21.5, 73.0), cape=2.0, flare=1.2, tail_ang=-8, tail_len=2,
                  capelet=1.2, glint=0.7, bendN=-1, bendF=-1, head_off=v2(1, 1),
                  smear=dict(c=(46, 42), r=28.4, a0=-60, a1=22, thick=4.5, alpha=0.8)))
    # 4 recover: settle back toward guard
    A.append(pose(hip=v2(39, 46.5), lean=0.16, grip=v2(49, 39), sword_dir=(1.0, -0.5),
                  footF=v2(55.0, 73.0), footN=v2(20.5, 73.0), cape=1.0, flare=0.5, tail_ang=-4, tail_len=1,
                  capelet=0.4, glint=0.4))
    F['attack'] = A
    # hit: recoil — torso back 3px, head snapped back with eyes shut, guard dropped, cape kicks forward
    F['hit'] = [pose(hip=v2(34, 46.5), lean=-0.2, grip=v2(41, 42), sword_dir=(1.0, 0.32), blade_len=27,
                     footF=v2(51.5, 73.0), footN=v2(19.5, 73.0), head_off=v2(-2, 1),
                     cape=-1.4, flare=0.3, tail_ang=-18, tail_len=1, capelet=0.8, wince=True, glint=0.5)]
    return F


# ---------------------------------------------------------------- previews
BG = (46, 52, 44)
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref2_x4.png')


def load(fd, name):
    return Image.open(os.path.join(fd, name + '.png')).convert('RGBA')


def previews(out, ref=None):
    fd = os.path.join(out, 'frames')
    rows = [('idle', 4), ('walk', 4), ('attack', 5), ('hit', 1)]
    S = 4
    sheet = Image.new('RGB', (5 * 80 * S, len(rows) * 80 * S), BG)
    for r, (a, n) in enumerate(rows):
        for i in range(n):
            im = load(fd, '%s_%d' % (a, i)).resize((80 * S, 80 * S), Image.NEAREST)
            sheet.paste(im, (i * 80 * S, r * 80 * S), im)
    sheet.save(os.path.join(out, 'preview.png'))

    idle = load(fd, 'idle_0').resize((640, 640), Image.NEAREST)
    ref = ref or REF
    if os.path.exists(ref):
        rim = Image.open(ref).convert('RGB')
        rim = rim.resize((int(rim.width * 640 / rim.height), 640), Image.LANCZOS)
        hero = Image.new('RGB', (640 + 16 + rim.width, 640), BG)
        hero.paste(rim, (656, 0))
    else:
        hero = Image.new('RGB', (640, 640), BG)
    hero.paste(idle, (0, 0), idle)
    hero.save(os.path.join(out, 'hero.png'))

    names = ['idle_0', 'walk_1', 'attack_2', 'hit_0']
    one = Image.new('RGB', (len(names) * 84 + len(names) * 164 + 16, 168), BG)
    x = 4
    for nm in names:
        im = load(fd, nm)
        one.paste(im, (x, 44), im)
        x += 84
    x += 8
    for nm in names:
        im = load(fd, nm).resize((160, 160), Image.NEAREST)
        one.paste(im, (x, 4), im)
        x += 164
    one.save(os.path.join(out, 'onefx.png'))


# ---------------------------------------------------------------- output
def check_margins(img, name):
    a = img[..., 3]
    bad = []
    if a[:3].any():
        bad.append('top')
    if a[:, :2].any():
        bad.append('left')
    if a[:, -2:].any():
        bad.append('right')
    if bad:
        print('  margin violation in', name, bad)
        a[:3] = 0
        a[:, :2] = 0
        a[:, -2:] = 0


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'out'
    ref = sys.argv[2] if len(sys.argv) > 2 else None
    fd = os.path.join(out, 'frames')
    os.makedirs(fd, exist_ok=True)
    F = frames()
    for anim, plist in F.items():
        for i, p in enumerate(plist):
            img = draw(p)
            check_margins(img, '%s_%d' % (anim, i))
            Image.fromarray(img, 'RGBA').save(os.path.join(fd, '%s_%d.png' % (anim, i)))
    print('wrote', sum(len(v) for v in F.values()), 'frames to', fd)
    previews(out, ref)


if __name__ == '__main__':
    main()
