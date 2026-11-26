"""Motion mannequin (attack / hit / idle) from a frame table, on the posekit body - PC (Aseprite) session tool.

  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO OUT_DIR            (the table embedded below, SET)
  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO SET.json OUT_DIR   (a table from a json file)

SET = {"set": "atk__class_warrior", "tag": "attack", "x0": 152,
       "layers": ["arm_far", "shield", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
       "defaults": {...keys every frame gets unless it has its own...},
       "weapon": {"type": "sword", "hand": "N", "layer": "weapon_front", "blade": 0.75, "reach": 0.85, "grip": 0.22,
                  "width": 0.08, "guard": [0.30, 0.06], "blade_rgb": "#C8C8D0", "grip_rgb": "#8A5A2B"}
              or {"type": "bow", "hand": "F", "layer": "weapon_front", "height": 1.50, "thick": 0.06, "bend": 0.16, "draw_bend": 0.06,
                  "recurve": 0.07, "rgb": "#8A5A2B", "string_px": 2.5, "string_rgb": "#E6E6E6", "arrow": 1.31, "arrow_px": 4,
                  "arrow_rgb": "#B0B0B8", "arrowhead": [0.09, 0.075]},
       "shield": {"hand": "F", "layer": "shield", "w": 0.68, "h": 0.90, "ang": 0, "rgb": "#6E7F99"},
       "frames": [{"name": "in", "ms": 70, "hip": [x, h], "lean": rad, "tilt": rad,
                   "footN": [x, h], "footF": [x, h], "faN": deg, "faF": deg, "toeN": k,
                   "handN": [x, h], "handF": [x, h], "elbN": [dx, dy], "elbF": [dx, dy],
                   "sw": k (both shoulders' spread, posekit) | "swN": k, "swF": k (one shoulder only - see _solve_sides),
                   "wa": deg (sword angle) | "ba": deg or "aim" (bow: top limb tilted forward from upright; "aim" = across the arrow line
                   string hand -> bow hand), "nocked": bool (bow: string pulled to the string hand + arrow on it)}, ...]}
Table units are heads (110 px): x from the set's column x0 (x px = x0 + 110 x), h above the floor (y px = 870 - 110 h).
Planted feet (h <= ankle height) are settled so that leg's lowest pixel is exactly on y=870 (one floor for every frame).
Writes OUT_DIR/layers/F<n>_<layer>.png, <set>.aseprite (Aseprite from ASEPRITE_PATH; frame ms, tag, hidden joints),
<set>_strip.png (all frames side by side), <set>_preview.gif (game size 0.1654 x4, the frame ms) and frames.json
(joint px per frame + posekit warnings).

Bow (atk__class_archer README): a flat short recurve in the bow (far) hand - its middle (the grip = the arrow rest = the far hand
dot = the arrow's origin) on the hand dot, 1.50 heads tip to tip along its axis, stave 0.06 heads thick with the 1.5 px prop outline,
limbs bending back toward the archer and the last quarter curling forward (the tips bend away from the archer). The string is a flat
2-3 px line (no outline): tips -> string hand while nocked, tip to tip after the release. The arrow (1.31 heads, 4 px shaft + a small
head, outlined) runs from the string hand dot through the bow hand dot while nocked; from the release on there is no arrow."""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- the delivered table (atk__class_archer, README 2026-11-26e)
# hip / lean / handN / handF / feet / ms = the README table exactly (x from the column x0 = 172, h above the floor, heads of 110 px).
# Added on the PC (README hands unchanged): per-side shoulder spread swN / swF so the bow arm is straight at hold-release-follow
# ("활 팔은 곧게": far elbow bend 81 -> 28 deg at hold, 73 -> 20 at release) and the drawing elbow sits back behind the head at the hold
# and folds straight back at the release; bow angle ba (nock / settle 20 deg = "앞으로 20° 기움", lower 14 = rigid rotation down,
# release / follow 5 = the hold's aim kept); elbN prefs put the draw elbow back. auto_tilt: tilt = lean / 2 on every frame.
SET = {
    "set": "atk__class_archer", "tag": "attack", "x0": 172, "auto_tilt": True,
    "layers": ["arm_far", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
    "defaults": {"footN": [-0.85, 0.12], "footF": [0.85, 0.12], "toeN": 0.85, "faN": 0, "faF": 0},
    "weapon": {"type": "bow", "hand": "F", "layer": "weapon_front", "height": 1.50, "thick": 0.06, "bend": 0.16, "draw_bend": 0.06,
               "recurve": 0.07, "rgb": "#8A5A2B", "string_px": 2.5, "string_rgb": "#E6E6E6", "arrow": 1.31, "arrow_px": 4,
               "arrow_rgb": "#B0B0B8", "arrowhead": [0.09, 0.075]},
    "frames": [
        {"name": "nock",    "ms": 80,  "hip": [0.00, 1.40],  "lean": 0.06,  "handN": [0.45, 1.92],  "handF": [0.55, 1.78], "ba": 20,    "nocked": True},
        {"name": "raise",   "ms": 80,  "hip": [0.00, 1.41],  "lean": 0.04,  "handN": [0.30, 2.28],  "handF": [0.80, 2.16], "ba": "aim", "nocked": True,
         "swN": 0.6, "swF": 0.6},
        {"name": "hold",    "ms": 200, "hip": [0.00, 1.42],  "lean": 0.02,  "handN": [0.15, 2.72],  "handF": [1.30, 2.62], "ba": "aim", "nocked": True,
         "elbN": [-1.0, -0.3], "swN": 0.2, "swF": 0.2},
        {"name": "release", "ms": 60,  "hip": [-0.02, 1.42], "lean": -0.02, "handN": [-0.50, 2.78], "handF": [1.30, 2.62], "ba": 5,
         "elbN": [-1.0, -0.3], "swN": 1.0, "swF": 0.32},
        {"name": "follow",  "ms": 110, "hip": [-0.03, 1.42], "lean": -0.03, "handN": [-0.62, 2.70], "handF": [1.28, 2.58], "ba": 5,
         "elbN": [-1.0, -0.3], "swN": 1.0, "swF": 0.30},
        {"name": "lower",   "ms": 100, "hip": [-0.01, 1.41], "lean": 0.03,  "handN": [-0.15, 2.10], "handF": [0.95, 2.20], "ba": 14,
         "swN": 1.0, "swF": 0.6},
        {"name": "settle",  "ms": 70,  "hip": [0.00, 1.40],  "lean": 0.06,  "handN": [-0.05, 1.72], "handF": [0.60, 1.80], "ba": 20},
    ],
}

# ---------------------------------------------------------------- ARMS: table changes for posekit natural-arms 2 (README 「팔 고침」 2차)
# the frame keys below replace the table's (None removes the key); "*" = set-level keys
ARMS_FIX = {"*": {"defaults": {"footN": [-0.85, 0.12], "footF": [0.85, 0.12], "toeN": 0.85, "faN": 0, "faF": 0, "swF": 0.2}, "weapon": {"type": "bow", "hand": "F", "layer": "weapon_front", "height": 1.50, "thick": 0.06, "bend": 0.16, "draw_bend": 0.06, "recurve": 0.07, "rgb": "#8A5A2B", "string_px": 2.5, "string_rgb": "#E6E6E6", "arrow": 1.50, "arrow_px": 4, "arrow_rgb": "#B0B0B8", "arrowhead": [0.09, 0.075]}}, "nock": {"handN": [0.45, 2.12], "handF": [1.00, 1.62]}, "raise": {"swN": None, "swF": None, "handN": [0.08, 2.40]}, "hold": {"swN": None, "swF": None, "handN": [-0.10, 2.84]}, "release": {"swN": None, "swF": None, "handF": [1.275, 2.62], "handN": [-0.66, 2.82]}, "follow": {"swN": None, "swF": None, "handF": [1.262, 2.58], "handN": [-0.90, 2.58], "elbN": [-1.0, 0.2]}, "lower": {"swN": None, "swF": None, "handN": [0.16, 2.12]}, "settle": {"handN": [0.23, 1.66], "handF": [0.98, 1.86]}}
_T = globals().get("SET") or globals().get("CFG")
_T.update(ARMS_FIX.get("*", {}))
for _f in _T["frames"]:
    for _k, _v in ARMS_FIX.get(_f["name"], {}).items():
        if _v is None:
            _f.pop(_k, None)
        else:
            _f[_k] = _v
# ---------------------------------------------------------------- /ARMS
args = sys.argv[1:]
if len(args) == 3:
    repo, setf, out = args
    cfg = json.load(open(setf, encoding='utf-8'))
elif len(args) == 2:
    repo, out = args
    cfg = None
else:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(repo, 'tools', 'pixelart'))
import posekit as pk  # noqa: E402
assert getattr(pk, 'ARMS_VERSION', '').startswith('posekit natural-arms 2'), 'pull the repo: this table needs posekit natural-arms 2 (tools/pixelart/posekit.py)'  # ARMS
import walk8 as w8  # noqa: E402

HEAD, SLOT, H, BASE, SCALE = w8.HEAD_PX, w8.SLOT, w8.SH_, w8.BASELINE, w8.SCALE
OUTLINE = (58, 54, 64)

# ---------------------------------------------------------------- per-side shoulder spread (swN / swF)
# posekit puts the shoulders at L(-0.40 sw, T - 0.05) / L(0.34 sw, T - 0.07) with ONE spread `sw` for both. A frame key "swN" or "swF"
# re-places only that shoulder (the torso drawing does not use the shoulders, so only the arm's root moves) and re-solves that arm
# with the same IK and bone lengths. The archer needs it: with the README's hands (draw hand at the cheek, draw length 127 px) a
# straight bow arm needs the far shoulder near the neck (swF ~0.2-0.3), while the drawing arm folds back cleanly only from the
# shoulder at the torso's back edge (swN 1.0) - one shared sw bends the bow arm 80 deg or throws the draw elbow down.
_pk_solve = pk.solve


def _solve_sides(pose, B, weapon):
    J = _pk_solve(pose, B, weapon)
    T = B.torso
    for side, r, u in (('N', -0.40, T - 0.05), ('F', 0.34, T - 0.07)):
        if 'sw' + side not in pose:
            continue
        spec = pose['hand' + side]
        if spec[0] != 'p':
            continue
        J['S' + side] = J['L'](r * pose['sw' + side], u)
        elb, hand, miss = pk.ik(J['S' + side], pk.P(spec[1], spec[2]), B.upper, B.fore + B.hand, pose.get('elb' + side, (0.25, 1.0)))
        J['elb' + side], J['hand' + side] = elb, hand
        J['wrist' + side] = elb + pk.norm(hand - elb) * B.fore
        J['miss']['arm' + side] = miss
    return J


# ARMS: posekit places swN / swF itself now (same shoulders) and keeps the natural elbow - no re-solve here
# pk.solve = _solve_sides


def load_embedded():
    return json.loads(json.dumps(SET))


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def main():
    global cfg, DX, B, OY
    if cfg is None:
        cfg = load_embedded()
    for f in cfg['frames']:
        for k, v in cfg.get('defaults', {}).items():
            f.setdefault(k, v)
    DX = (SLOT / 2 - cfg.get('x0', SLOT / 2)) / HEAD          # table x -> posekit world x (posekit puts world x 0 on column 192)
    B = pk.Body(4.0)
    OY = floor_row()
    build_all()


def xy(v):
    return (v[0] - DX, v[1])


def make_pose(f, lift=(0.0, 0.0)):
    lean = f.get('lean', 0.08)
    # attack sets (cfg "auto_tilt" true, the default): posekit turns the head by half the lean (hang = lean/2 + tilt), so
    # tilt = lean/2 turns it WITH the torso (pc_notes 2026-11-26e); a frame's own "tilt" is added on top.
    # hit sets ("auto_tilt": false): the table's tilt as it is, no head correction (pc_notes: 피격 세트는 표에 적힌 tilt 그대로)
    auto = cfg.get('auto_tilt', True)
    p = dict(hip=xy(f['hip']), lean=lean, tilt=(lean / 2 if auto else 0.0) + f.get('tilt', 0.0), kneeN=(1.0, 0.0), kneeF=(1.0, 0.0))
    for side, li in (('N', 0), ('F', 1)):
        fx, fh = xy(f['foot' + side])
        p['foot' + side] = (fx, fh + lift[li])
        p['fa' + side] = f.get('fa' + side, 0.0)
        hx, hh = xy(f['hand' + side])
        p['hand' + side] = ('p', hx, hh)
        if 'elb' + side in f:
            p['elb' + side] = tuple(f['elb' + side])
    for k in ('hipw', 'sw', 'swN', 'swF', 'head_off', 'toeN', 'toeF'):
        if k in f:
            p[k] = tuple(f[k]) if isinstance(f[k], list) else f[k]
    # posekit also swings the head CENTRE by the tilt (C = neck + up*neck + rot(up, tilt)*0.55hs); put it back on the torso
    # axis so the head sits on the neck like a rigid part of the torso (no slide on the neck dot)
    if auto:
        up = pk.rot(pk.v2(0, -1), lean)
        hup = pk.rot(up, p['tilt'])
        dv = (up - hup) * 0.55 * B.hs
        ho = p.get('head_off', (0.0, 0.0))
        p['head_off'] = (ho[0] + dv[0], ho[1] - dv[1])
    p['arms'] = 'natural'      # ARMS: posekit natural-arms 2 - the elbow bends the anatomical way (SPEC 10.3b)
    if cfg.get('weapon', {}).get('type') == 'bow':       # ARMS: the string hand may draw (raised elbow behind the hand)
        p['bow_draw'] = 'N' if cfg['weapon'].get('hand', 'F') == 'F' else 'F'
    p['z'] = f.get('z', {'farfore': 'back'})
    return p


def floor_row():
    """canvas row of the world floor: a flat boot with its ankle at the standard height ends on the baseline"""
    p = make_pose(dict(hip=[DX, 1.40], footN=[DX - 0.9, B.ank], footF=[DX + 0.8, B.ank], handN=[DX - 0.3, 1.5], handF=[DX + 0.4, 1.5]))
    _, parts = pk.build(p, B, 'none')
    return BASE - (w8.lowest(w8.draw(parts, w8.LEGS['N'], BASE)) - BASE)


def solve(f, tag):
    planted = [s for s in 'NF' if f['foot' + s][1] <= B.ank + 1e-6]
    if not planted:
        p = make_pose(f)
        J, parts = pk.build(p, B, 'none')
        return p, J, parts
    sides = tuple(planted) + tuple(s for s in 'NF' if s not in planted)
    order = {'N': 0, 'F': 1}

    def make(lift):
        li = [0.0, 0.0]
        for j, s in enumerate(sides):
            li[order[s]] = lift[j]
        return make_pose(f, tuple(li))
    return w8.settle(make, B, OY, sides, len(planted), tag)


def W2P(v):
    """world (heads, y-down) -> frame px"""
    return (SLOT / 2 + v[0] * HEAD, OY + v[1] * HEAD)


def prop_layer(groups):
    """flat props: groups [(outline?, [(shape, colour), ...])] drawn in order; inside an outlined group every outline (1.5 px) goes
    down before the fills, so its pieces join without a line between them. No shading -> RGBA"""
    R = pk.Raster(SLOT, H, HEAD, SLOT / 2, OY, 1)
    img = np.zeros((H, SLOT, 4), np.uint8)
    g = 1.5 / HEAD
    for outlined, shapes in groups:
        if outlined:
            for shp, col in shapes:
                x0, y0, x1, y1 = R.window(shp, g)
                win = (x0, y0, x1, y1)
                view = img[y0:y1, x0:x1]
                view[R.mask(shp, g, win)] = (*OUTLINE, 255)
        for shp, col in shapes:
            x0, y0, x1, y1 = R.window(shp, g)
            win = (x0, y0, x1, y1)
            view = img[y0:y1, x0:x1]
            view[R.mask(shp, 0.0, win)] = (*col, 255)
    return img


def sword(J, f, wcfg):
    Hd = J['hand' + wcfg.get('hand', 'N')]
    d = pk.wdir(f['wa'])
    pn = np.array((d[1], -d[0]))
    reach, blade, grip, wid = wcfg['reach'], wcfg['blade'], wcfg['grip'], wcfg['width']
    g0 = Hd + d * (reach - blade)                       # guard centre = start of the blade
    tip = Hd + d * reach
    bl = [g0 + pn * wid / 2, tip - d * wid + pn * wid / 2, tip, tip - d * wid - pn * wid / 2, g0 - pn * wid / 2]
    gl, gt = wcfg['guard']
    guard = [g0 + pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 - d * gt / 2, g0 + pn * gl / 2 - d * gt / 2]
    back = g0 - d * grip
    J['wtip'] = tip
    return [(True, [(pk.cap(back + d * 0.04, g0, 0.035), rgb(wcfg['grip_rgb'])), (pk.ell(back + d * 0.04, 0.045, 0.045), rgb(wcfg['grip_rgb'])),
                    (pk.poly(bl), rgb(wcfg['blade_rgb'])), (pk.poly(guard), rgb(wcfg['grip_rgb']))])]


def bow(J, f, wcfg):
    """short recurve in the bow hand (its grip on the hand dot), string, and the arrow while nocked (see the module doc)"""
    bs, ss = wcfg.get('hand', 'F'), ('N' if wcfg.get('hand', 'F') == 'F' else 'F')
    G, S = J['hand' + bs], J['hand' + ss]
    aim = pk.norm(G - S)
    ba = f.get('ba', 'aim')
    a = math.atan2(aim[1], aim[0]) if ba == 'aim' else math.radians(ba)
    fw = np.array((math.cos(a), math.sin(a)))           # forward, across the stave (away from the archer), y-down
    up = np.array((math.sin(a), -math.cos(a)))          # along the stave to the top tip
    half = wcfg['height'] / 2
    drawn = f.get('nocked', False)
    dl = float(np.linalg.norm(G - S)) * HEAD if drawn else 0.0
    k = wcfg['bend'] + wcfg.get('draw_bend', 0.0) * min(dl / 127.0, 1.2)
    pts = []
    n = 24
    for i in range(-n, n + 1):
        s = i / n
        back = k * s * s - wcfg['recurve'] * max(0.0, (abs(s) - 0.75) / 0.25) ** 2
        pts.append(G + up * (half * s) - fw * back)
    top, bot = pts[-1], pts[0]
    groups = []
    sw = wcfg.get('string_px', 2.5) / HEAD
    scol = rgb(wcfg.get('string_rgb', '#E6E6E6'))
    if drawn:
        groups.append((False, [(('line', [top, S, bot], sw), scol)]))
    else:
        groups.append((False, [(('line', [top, bot], sw), scol)]))
    groups.append((True, [(('line', pts, wcfg['thick']), rgb(wcfg['rgb']))]))
    J['bow_top'], J['bow_bot'] = top, bot
    if drawn:
        L = wcfg['arrow']
        hl, hw = wcfg.get('arrowhead', [0.09, 0.075])
        tip = S + aim * L
        base = tip - aim * hl
        nrm = np.array((-aim[1], aim[0]))
        aw = wcfg.get('arrow_px', 4) / HEAD
        acol = rgb(wcfg.get('arrow_rgb', '#B0B0B8'))
        groups.append((True, [(('line', [S, base + aim * 0.01], aw), acol), (pk.poly([tip, base + nrm * hw / 2, base - nrm * hw / 2]), acol)]))
        J['wtip'] = tip
    return groups


def shield(J, f, scfg):
    c = J['hand' + scfg.get('hand', 'F')]
    ang = math.radians(f.get('shield_ang', scfg.get('ang', 0)))
    return [(True, [(pk.ell(c, scfg['w'] / 2, scfg['h'] / 2, ang), rgb(scfg['rgb']))])]


def frame_images(J, parts, f):
    layers, _ = w8.frame_layers(parts, J, OY)
    if 'weapon' in cfg:
        wc = cfg['weapon']
        geo = bow if wc.get('type') == 'bow' else sword
        layers[wc['layer']] = Image.fromarray(prop_layer(geo(J, f, wc)), 'RGBA')
    if 'shield' in cfg:
        sc = cfg['shield']
        layers[sc['layer']] = Image.fromarray(prop_layer(shield(J, f, sc)), 'RGBA')
    flat = Image.new('RGB', (SLOT, H), pk.BG)
    for name in cfg['layers']:
        if name == 'joints':
            continue
        flat.paste(layers[name], (0, 0), layers[name])
    return layers, flat


def flex(a, b, c):
    """bend at b of the chain a-b-c in degrees (0 = straight)"""
    u, v = np.asarray(b) - np.asarray(a), np.asarray(c) - np.asarray(b)
    cs = float(u @ v) / max(1e-9, float(np.linalg.norm(u) * np.linalg.norm(v)))
    return math.degrees(math.acos(max(-1.0, min(1.0, cs))))


def build_all():
    ldir = os.path.join(out, 'layers')
    os.makedirs(ldir, exist_ok=True)
    recs, flats, warns = [], [], []
    for i, f in enumerate(cfg['frames']):
        tag = f'F{i + 1} {f["name"]}'
        p, J, parts = solve(f, tag)
        warns += [f'{tag}: {m}' for m in pk.check(tag, J, B, p)]
        layers, flat = frame_images(J, parts, f)
        for name in cfg['layers']:
            layers[name].save(os.path.join(ldir, f'F{i + 1}_{name}.png'))
        flats.append(flat)
        a = np.asarray(flat)
        m = np.any(a != np.array(pk.BG, np.uint8), axis=-1)
        xs, ys = np.nonzero(m.any(0))[0], np.nonzero(m.any(1))[0]
        rec = dict(frame=f['name'], ms=f['ms'], x_range=[int(xs.min()), int(xs.max())], top=int(ys.min()), lowest=int(ys.max()),
                   joints={k: [round(c, 1) for c in W2P(J[k])] for k in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF',
                                                                          'elbN', 'elbF', 'handN', 'handF', 'neck0', 'C')},
                   elbow_flex={s: round(flex(J['S' + s], J['elb' + s], J['hand' + s]), 1) for s in 'NF'})
        for k in ('wtip', 'bow_top', 'bow_bot'):
            if k in J:
                rec[k] = [round(c, 1) for c in W2P(J[k])]
        recs.append(rec)
    strip = Image.new('RGB', (SLOT * len(flats), H), pk.BG)
    for i, fl in enumerate(flats):
        strip.paste(fl, (i * SLOT, 0))
    strip.save(os.path.join(out, f'{cfg["set"]}_strip.png'))
    small = []
    for fl in flats:
        a = np.asarray(fl).copy()
        msk = np.all(a == np.array(pk.BG, np.uint8), axis=-1)
        a[msk] = (46, 58, 46)
        c = Image.fromarray(a).crop((0, BASE - 520, SLOT, BASE + 20))
        c = c.resize((round(c.width * SCALE), round(c.height * SCALE)), Image.BOX)
        small.append(c.resize((c.width * 4, c.height * 4), Image.NEAREST))
    small[0].save(os.path.join(out, f'{cfg["set"]}_preview.gif'), save_all=True, append_images=small[1:],
                  duration=[f['ms'] for f in cfg['frames']], loop=0)
    json.dump(dict(set=cfg['set'], oy=OY, posekit_warnings=warns, frames=recs), open(os.path.join(out, 'frames.json'), 'w', encoding='utf-8'), indent=1)
    exe = os.environ.get('ASEPRITE_PATH')
    dst = os.path.abspath(os.path.join(out, cfg['set'] + '.aseprite'))
    if exe:
        if os.path.exists(dst):
            os.remove(dst)
        lua = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_motion_ase.lua')
        r = subprocess.run([exe, '-b', '--script-param', 'dir=' + os.path.abspath(ldir), '--script-param', 'out=' + dst,
                            '--script-param', 'ms=' + ','.join(str(f['ms']) for f in cfg['frames']),
                            '--script-param', 'layers=' + ','.join(cfg['layers']), '--script-param', 'tag=' + cfg.get('tag', ''),
                            '--script', lua], capture_output=True)
        print(('wrote ' + dst) if os.path.exists(dst) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    else:
        print('ASEPRITE_PATH not set: layers / strip / gif only')
    print(f'{cfg["set"]}: {len(flats)} frames, floor row {OY}, posekit warnings {len(warns)}')
    for w in warns:
        print('  ' + w)
    for r_ in recs:
        jn = r_['joints']
        print(f'  {r_["frame"]:8s} x {r_["x_range"][0]}..{r_["x_range"][1]}  top {r_["top"]}  lowest {r_["lowest"]}  handN {jn["handN"]}  '
              f'handF {jn["handF"]}  elbow flex N {r_["elbow_flex"]["N"]} F {r_["elbow_flex"]["F"]}  tip {r_.get("wtip")}  '
              f'bow {r_.get("bow_top")}..{r_.get("bow_bot")}')


main()
