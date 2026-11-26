"""Motion mannequin (attack / hit / idle) from a frame table, on the posekit body - PC (Aseprite) session tool.
This copy: atk__captain_ironwall (Brigginda, tower-shield shove with a flanged mace cocked behind). The delivered set's table is
embedded below (SET), so

  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO OUT_DIR              (the embedded table)
  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO SET.json OUT_DIR     (another table)

rebuilds it. REPO = the pixel-management checkout (tools/pixelart/posekit.py and walk8.py are imported from it).
build_motion_ase.lua must sit next to this script (it assembles the .aseprite in Aseprite from ASEPRITE_PATH).

Table format (SET / SET.json):
  {"set": "atk__captain_ironwall", "tag": "attack", "x0": 170, "frame_tags": true,
   "layers": [bottom -> top above Background, "joints" last],
   "pose_defaults": {posekit keys every frame starts from, e.g. "toeN": 0.85, "faN": 0, "faF": 0, "elbF": [-0.3, 1.0]},
   "weapon": {"type": "mace", "hand": "N", "layer": "weapon_back", "reach": 0.80, "butt": 0.10, "shaft_w": 0.07,
              "head_len": 0.20, "head_w": 0.22, "head_rgb": "#9A9AA6", "shaft_rgb": "#8A5A2B"}
             or {"type": "sword", ..., "blade", "reach", "grip", "width", "guard", "blade_rgb", "grip_rgb"},
   "shield": {"type": "tower", "hand": "F", "layer": "shield", "w": 0.40, "h": 1.30, "ang": 0, "rgb": "#6E7F99"}
             or {"type": "round", ... "w", "h"} (an ellipse),
   "frames": [{"name", "ms", "hip": [x, h], "lean": rad, "tilt": rad (extra), "footN": [x, h], "footF": [x, h],
               "handN": [x, h], "handF": [x, h], "elbN": [dx, dy], "elbF": [dx, dy], "wa": deg, "shield_ang": deg}, ...]}
Table units are heads (110 px): x from the set's column x0 (x px = x0 + 110 x), h above the floor (y px = 870 - 110 h).
Planted feet (h <= ankle height) are settled so that leg's lowest pixel is exactly on y=870 (one floor for every frame).
Props are flat single colours with a 1.5 px outline; their sizes include the outline (a 0.40-head shield is 44 px wide).
"auto_tilt" (default true, attack sets): tilt = lean/2 (+ the frame's own tilt) and the head stays on the torso axis.
Writes OUT_DIR/layers/F<n>_<layer>.png, <set>.aseprite (frame ms, the motion tag, one tag per frame name with frame_tags,
hidden joints), <set>_strip.png (all frames side by side, 384 px each), <set>_game.png (game size 0.1654 x4, side by side),
<set>_preview.gif (game size x4, the frame ms) and frames.json (joint px per frame, weapon tip, shield front, posekit warnings)."""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- the delivered table (README atk__captain_ironwall 2026-11-26e)
# Changed from the README table (PC, after playing it at game size; check_skeleton PASS, 0 warnings):
#   swing   far hand (shield) h 2.22 -> 2.15 (-7.7 px): the far elbow stuck 5 px out of the shield's lower front corner
#   contact far hand (shield) (1.30, 2.20) -> (1.34, 2.10) (+4.4 px, -11 px): the elbow stuck 12 px out in front of the shield;
#           now it folds down under the shield as at the hold, the shield face reaches 4 px further (339)
#   follow  far hand (shield) x 1.05 -> 1.09 (+4.4 px): keeps the README's 0.25-head rebound from the moved contact
#   recover mace 135 -> 105 deg: the mace starts down toward the rim (135 -> 40 was a 95-deg snap in the one settle frame)
SET = {
    "set": "atk__captain_ironwall", "tag": "attack", "x0": 170, "frame_tags": True,
    "layers": ["weapon_back", "arm_far", "shield", "leg_far", "leg_near", "torso", "head", "arm_near", "joints"],
    "pose_defaults": {"toeN": 0.85, "faN": 0, "faF": 0, "elbF": [-0.3, 1.0]},
    "weapon": {"type": "mace", "hand": "N", "layer": "weapon_back", "reach": 0.80, "butt": 0.10, "shaft_w": 0.07,
               "head_len": 0.20, "head_w": 0.22, "head_rgb": "#9A9AA6", "shaft_rgb": "#8A5A2B"},
    "shield": {"type": "tower", "hand": "F", "layer": "shield", "w": 0.40, "h": 1.30, "ang": 0, "rgb": "#6E7F99"},
    "frames": [
        {"name": "in", "ms": 70, "hip": [-0.14, 1.30], "lean": 0.08, "footN": [-0.80, 0.12], "footF": [0.95, 0.12],
         "handN": [-0.05, 2.15], "handF": [0.42, 2.18], "wa": 115},
        {"name": "hold", "ms": 170, "hip": [-0.36, 1.16], "lean": 0.10, "footN": [-0.80, 0.12], "footF": [0.95, 0.12],
         "handN": [-0.45, 2.25], "handF": [0.38, 2.20], "wa": 140},
        {"name": "swing", "ms": 50, "hip": [0.00, 1.20], "lean": 0.20, "footN": [-0.80, 0.12], "footF": [1.02, 0.12],
         "handN": [-0.40, 2.22], "handF": [0.75, 2.15], "wa": 140},
        {"name": "contact", "ms": 80, "hip": [0.36, 1.12], "lean": 0.32, "footN": [-0.80, 0.12], "footF": [1.10, 0.12],
         "handN": [-0.28, 2.20], "handF": [1.34, 2.10], "wa": 140},
        {"name": "follow", "ms": 80, "hip": [0.40, 1.18], "lean": 0.34, "footN": [-0.80, 0.12], "footF": [1.10, 0.12],
         "handN": [-0.22, 2.20], "handF": [1.09, 1.92], "wa": 140},
        {"name": "recover", "ms": 90, "hip": [0.10, 1.26], "lean": 0.18, "footN": [-0.80, 0.12], "footF": [1.02, 0.12],
         "handN": [-0.30, 2.10], "handF": [0.70, 2.20], "wa": 105},
        {"name": "settle", "ms": 70, "hip": [0.00, 1.32], "lean": 0.10, "footN": [-0.80, 0.12], "footF": [0.95, 0.12],
         "handN": [0.10, 2.30], "handF": [0.50, 2.15], "wa": 40},
    ],
}

# ---------------------------------------------------------------- ARMS: table changes for posekit natural-arms 2 (README 「팔 고침」 2차)
# the frame keys below replace the table's (None removes the key); "*" = set-level keys
ARMS_FIX = {"*": {"pose_defaults": {"toeN": 0.85, "faN": 0, "faF": 0}}, "in": {"handN": [-0.06, 2.24], "handF": [0.68, 2.14]}, "hold": {"handN": [-0.31, 2.20], "handF": [0.46, 2.26]}, "swing": {"handN": [0.20, 2.15], "handF": [0.93, 2.21]}, "contact": {"handN": [-0.04, 2.32], "elbN": [-0.3, 1.0], "handF": [1.40, 1.89]}, "follow": {"handN": [0.04, 2.38], "elbN": [-0.3, 1.0], "handF": [1.36, 1.80]}, "recover": {"handN": [0.28, 2.20], "handF": [1.02, 2.22]}, "settle": {"handN": [0.12, 2.22], "handF": [0.84, 2.15]}}
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
if len(args) == 2:
    repo, out = args
    cfg = SET
elif len(args) == 3:
    repo, setf, out = args
    cfg = json.load(open(setf, encoding='utf-8'))
else:
    sys.exit('usage: mannequin_pc.py REPO [SET.json] OUT_DIR')
sys.path.insert(0, os.path.join(repo, 'tools', 'pixelart'))
import posekit as pk  # noqa: E402
assert getattr(pk, 'ARMS_VERSION', '').startswith('posekit natural-arms 2'), 'pull the repo: this table needs posekit natural-arms 2 (tools/pixelart/posekit.py)'  # ARMS
import walk8 as w8  # noqa: E402

HEAD, SLOT, H, BASE, SCALE = w8.HEAD_PX, w8.SLOT, w8.SH_, w8.BASELINE, w8.SCALE
DX = (SLOT / 2 - cfg.get('x0', SLOT / 2)) / HEAD          # table x -> posekit world x (posekit puts world x 0 on column 192)
B = pk.Body(4.0)
OUTLINE = (58, 54, 64)
OUT_PX = 1.5                                               # prop outline width (px)
DEFAULTS = cfg.get('pose_defaults', {})


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def xy(v):
    return (v[0] - DX, v[1])


def make_pose(f, lift=(0.0, 0.0)):
    f = {**DEFAULTS, **f}
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
    for k in ('hipw', 'sw', 'head_off', 'toeN', 'toeF'):
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
    p['z'] = f.get('z', {'farfore': 'back'})
    return p


def floor_row():
    """canvas row of the world floor: a flat boot with its ankle at the standard height ends on the baseline"""
    p = make_pose(dict(hip=[DX, 1.40], footN=[DX - 0.9, B.ank], footF=[DX + 0.8, B.ank], handN=[DX - 0.3, 1.5], handF=[DX + 0.4, 1.5]))
    _, parts = pk.build(p, B, 'none')
    return BASE - (w8.lowest(w8.draw(parts, w8.LEGS['N'], BASE)) - BASE)


OY = floor_row()


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


def prop_layer(shapes):
    """flat props: [(shape, colour)] drawn in order with a 1.5 px outline, no shading -> RGBA"""
    R = pk.Raster(SLOT, H, HEAD, SLOT / 2, OY, 1)
    img = np.zeros((H, SLOT, 4), np.uint8)
    g = OUT_PX / HEAD
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
    return [(pk.cap(back + d * 0.04, g0, 0.035), rgb(wcfg['grip_rgb'])), (pk.ell(back + d * 0.04, 0.045, 0.045), rgb(wcfg['grip_rgb'])),
            (pk.poly(bl), rgb(wcfg['blade_rgb'])), (pk.poly(guard), rgb(wcfg['grip_rgb']))]


def mace(J, f, wcfg):
    """flanged mace in one hand: a shaft from `butt` behind the hand dot to the head, the head (head_len along the shaft x head_w
    across, four flanges seen as a squared head with bevelled ends) ending `reach` from the hand dot. Sizes include the outline."""
    Hd = J['hand' + wcfg.get('hand', 'N')]
    d = pk.wdir(f['wa'])
    pn = np.array((d[1], -d[0]))
    o = OUT_PX / HEAD
    reach, butt, sw = wcfg['reach'] - o, wcfg['butt'] - o, wcfg['shaft_w'] - 2 * o
    hl, hw = wcfg['head_len'] - o, wcfg['head_w'] - 2 * o
    h0 = reach - hl                                     # where the head starts along the shaft
    shaft = pk.cap(Hd - d * (butt - sw / 2), Hd + d * (h0 + 0.02), sw / 2)
    core = hw * 0.55 / 2                                # half width of the head's neck / crown (the flanges stand out to hw/2)

    def A(a, c):
        return Hd + d * a + pn * c
    head = pk.poly([A(h0, -core), A(h0 + 0.03, -hw / 2), A(reach - 0.035, -hw / 2), A(reach, -core),
                    A(reach, core), A(reach - 0.035, hw / 2), A(h0 + 0.03, hw / 2), A(h0, core)])
    J['wtip'] = Hd + d * reach
    return [(shaft, rgb(wcfg['shaft_rgb'])), (head, rgb(wcfg['head_rgb']))]


def shield(J, f, scfg):
    c = J['hand' + scfg.get('hand', 'F')]
    ang = math.radians(f.get('shield_ang', scfg.get('ang', 0)))
    o = OUT_PX / HEAD
    if scfg.get('type', 'round') == 'tower':
        # upright tower shield seen nearly edge-on (3/4 side view): w x h heads with the outline, the hand dot at its centre
        hw, hh = scfg['w'] / 2 - o, scfg['h'] / 2 - o
        ux, uy = pk.rot(pk.v2(1, 0), -ang), pk.rot(pk.v2(0, 1), -ang)
        pts = [c - ux * hw - uy * hh, c + ux * hw - uy * hh, c + ux * hw + uy * hh, c - ux * hw + uy * hh]
        J['shield_front'] = max(p[0] for p in pts) + o
        J['shield_low'] = max(p[1] for p in pts) + o
        return [(pk.poly(pts), rgb(scfg['rgb']))]
    return [(pk.ell(c, scfg['w'] / 2, scfg['h'] / 2, ang), rgb(scfg['rgb']))]


def frame_images(J, parts, f):
    layers, _ = w8.frame_layers(parts, J, OY)
    if 'weapon' in cfg:
        wc = cfg['weapon']
        fn = mace if wc.get('type') == 'mace' else sword
        layers[wc['layer']] = Image.fromarray(prop_layer(fn(J, f, wc)), 'RGBA')
    if 'shield' in cfg:
        sc = cfg['shield']
        layers[sc['layer']] = Image.fromarray(prop_layer(shield(J, f, sc)), 'RGBA')
    flat = Image.new('RGB', (SLOT, H), pk.BG)
    for name in cfg['layers']:
        if name == 'joints':
            continue
        flat.paste(layers[name], (0, 0), layers[name])
    return layers, flat


def game_size(fl):
    a = np.asarray(fl).copy()
    msk = np.all(a == np.array(pk.BG, np.uint8), axis=-1)
    a[msk] = (46, 58, 46)
    c = Image.fromarray(a).crop((0, BASE - 520, SLOT, BASE + 20))
    c = c.resize((round(c.width * SCALE), round(c.height * SCALE)), Image.BOX)
    return c.resize((c.width * 4, c.height * 4), Image.NEAREST)


def main():
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
                                                                          'elbN', 'elbF', 'handN', 'handF', 'neck0', 'C')})
        if 'wtip' in J:
            rec['weapon_tip'] = [round(c, 1) for c in W2P(J['wtip'])]
        if 'shield_front' in J:
            rec['shield_front_x'] = round(SLOT / 2 + J['shield_front'] * HEAD, 1)
            rec['shield_low_above_floor'] = round(BASE - (OY + J['shield_low'] * HEAD), 1)
        recs.append(rec)
    strip = Image.new('RGB', (SLOT * len(flats), H), pk.BG)
    for i, fl in enumerate(flats):
        strip.paste(fl, (i * SLOT, 0))
    strip.save(os.path.join(out, f'{cfg["set"]}_strip.png'))
    small = [game_size(fl) for fl in flats]
    sheet = Image.new('RGB', (sum(s.width for s in small) + 8 * (len(small) - 1), small[0].height), (20, 20, 20))
    x = 0
    for s in small:
        sheet.paste(s, (x, 0))
        x += s.width + 8
    sheet.save(os.path.join(out, f'{cfg["set"]}_game.png'))
    small[0].save(os.path.join(out, f'{cfg["set"]}_preview.gif'), save_all=True, append_images=small[1:],
                  duration=[f['ms'] for f in cfg['frames']], loop=0)
    json.dump(dict(set=cfg['set'], oy=OY, posekit_warnings=warns, frames=recs), open(os.path.join(out, 'frames.json'), 'w', encoding='utf-8'), indent=1)
    exe = os.environ.get('ASEPRITE_PATH')
    dst = os.path.abspath(os.path.join(out, cfg['set'] + '.aseprite'))
    if exe:
        if os.path.exists(dst):
            os.remove(dst)
        lua = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_motion_ase.lua')
        cmd = [exe, '-b', '--script-param', 'dir=' + os.path.abspath(ldir), '--script-param', 'out=' + dst,
               '--script-param', 'ms=' + ','.join(str(f['ms']) for f in cfg['frames']),
               '--script-param', 'layers=' + ','.join(cfg['layers']), '--script-param', 'tag=' + cfg.get('tag', '')]
        if cfg.get('frame_tags'):
            cmd += ['--script-param', 'ftags=' + ','.join(f['name'] for f in cfg['frames'])]
        r = subprocess.run(cmd + ['--script', lua], capture_output=True)
        print(('wrote ' + dst) if os.path.exists(dst) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    else:
        print('ASEPRITE_PATH is not set: no .aseprite written')
    print(f'{cfg["set"]}: {len(flats)} frames, floor row {OY}, posekit warnings {len(warns)}')
    for w in warns:
        print('  ' + w)
    for r_ in recs:
        print(f'  {r_["frame"]:8s} x {r_["x_range"][0]}..{r_["x_range"][1]}  top {r_["top"]}  lowest {r_["lowest"]}  tip {r_.get("weapon_tip")}'
              f'  shield front {r_.get("shield_front_x")} low +{r_.get("shield_low_above_floor")}')


main()
