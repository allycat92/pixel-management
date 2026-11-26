"""Motion mannequin (attack / hit / idle) from a frame table, on the posekit body - PC (Aseprite) session tool.

  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO SET.json OUT_DIR
  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO OUT_DIR        (the table embedded below, SET)

SET.json = {"set": "atk__class_warrior", "tag": "attack", "x0": 170, "auto_tilt": true,
            "layers": ["arm_far", "shield", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
            "weapon": {"type": "sword", "hand": "N", "layer": "weapon_front", "blade": 0.75, "reach": 0.85, "grip": 0.22,
                       "width": 0.08, "guard": [0.30, 0.06], "blade_rgb": "#C8C8D0", "grip_rgb": "#8A5A2B"},
            "shield": {"hand": "F", "layer": "shield", "w": 0.68, "h": 0.90, "ang": 0, "rgb": "#6E7F99"},
            "frames": [{"name": "in", "ms": 70, "hip": [x, h], "lean": rad, "tilt": rad,
                        "footN": [x, h], "footF": [x, h], "faN": deg, "faF": deg,
                        "handN": [x, h], "handF": [x, h], "elbN": [dx, dy], "elbF": [dx, dy], "wa": deg}, ...]}
Table units are heads (110 px): x from the set's column x0 (x px = x0 + 110 x), h above the floor (y px = 870 - 110 h).
Planted feet (h <= ankle height) are settled so that leg's lowest pixel is exactly on y=870 (one floor for every frame).
Writes OUT_DIR/layers/F<n>_<layer>.png, <set>.aseprite (Aseprite from ASEPRITE_PATH; frame ms, tag, hidden joints),
<set>_strip.png (all frames side by side), <set>_preview.gif (game size 0.1654 x4, the frame ms) and frames.json
(joint px per frame + posekit warnings).
The Lua that assembles the .aseprite (build_motion_ase.lua) is looked up next to this script."""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- the delivered table (atk__class_warrior, README 2026-11-26e)
# README table as given (x0 = 170 = the set's idle hip column, faN 15 = heel up on swing/contact, toeN 0.85, tilt = lean/2 via
# auto_tilt). Changes against the README are marked "# PC:" above their frame (all far-hand / shield only; body, feet, sword as given):
#   swing   handF (0.95, 2.55) -> (1.20, 2.55)  = px (274, 590) -> (302, 590): the shield bash reaches further (front x 313 -> 340), so the
#           swing stays the shield's furthest frame while the contact shield can sit in front of the face.
#   contact handF (0.88, 2.42) -> (1.14, 2.27)  = px (267, 604) -> (295, 620), elbF up-back: with the README value the leaning body
#           covered the shield (only a sliver behind the head) and the folded far elbow jutted forward at head height (x 335). Now the
#           round shield stays in front of the face/chest (README "방패는 앞에 그대로") and the blade passes under its lower edge (y 670 vs 700).
#   follow  handF (0.65, 2.30) -> (0.70, 2.05)  = px (242, 617) -> (247, 645): the pulled-back shield peeked out behind the head like a
#           hood; lowered, it tucks behind the torso (still pulled back, as the README means).
SET = {"set": "atk__class_warrior", "tag": "attack", "x0": 170, "auto_tilt": True,
       "layers": ["arm_far", "shield", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
       "weapon": {"type": "sword", "hand": "N", "layer": "weapon_front", "blade": 0.75, "reach": 0.85, "grip": 0.22, "width": 0.08,
                  "guard": [0.30, 0.06], "blade_rgb": "#C8C8D0", "grip_rgb": "#8A5A2B"},
       "shield": {"hand": "F", "layer": "shield", "w": 0.68, "h": 0.90, "ang": 0, "rgb": "#6E7F99"},
       "frames": [
           {"name": "in", "ms": 70, "hip": [-0.12, 1.34], "lean": 0.06, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 0,
            "handN": [-0.30, 1.80], "handF": [0.62, 2.20], "wa": 90},
           {"name": "hold", "ms": 160, "hip": [-0.30, 1.32], "lean": 0.04, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 0,
            "handN": [-0.75, 1.75], "handF": [0.45, 2.42], "wa": 120},
           # PC: handF x 0.95 -> 1.20
           {"name": "swing", "ms": 50, "hip": [0.00, 1.24], "lean": 0.16, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 15,
            "handN": [-0.15, 1.55], "handF": [1.20, 2.55], "wa": 250},
           # PC: handF (0.88, 2.42) -> (1.14, 2.27), far elbow bends up-back (hidden behind the head)
           {"name": "contact", "ms": 70, "hip": [0.27, 1.24], "lean": 0.32, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 15,
            "handN": [0.75, 1.55], "handF": [1.14, 2.27], "elbF": [-0.5, -1.0], "wa": 355},
           # PC: handF (0.65, 2.30) -> (1.06, 2.20), far elbow bends up-back like contact (touch-up 2: at (0.70, 2.05) only 11% of the
           #     shield showed, mostly a grey wedge behind the neck that read as a hood; now it stays in front of the chest)
           {"name": "follow", "ms": 90, "hip": [0.33, 1.18], "lean": 0.40, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 0,
            "handN": [0.72, 1.80], "handF": [1.06, 2.20], "elbF": [-0.5, -1.0], "wa": 385},
           {"name": "recover", "ms": 90, "hip": [0.10, 1.30], "lean": 0.18, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 0,
            "handN": [0.40, 1.65], "handF": [0.70, 2.15], "wa": 405},
           {"name": "settle", "ms": 70, "hip": [0.00, 1.38], "lean": 0.08, "footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 0,
            "handN": [0.06, 1.71], "handF": [0.78, 2.07], "wa": 398},
       ]}

# ---------------------------------------------------------------- ARMS: table changes for posekit natural arms (pc_changes.md)
# the frame keys below replace the table's (None removes the key); "*" = set-level keys
ARMS_FIX = {"in": {"handN": [0.10, 1.86], "handF": [0.68, 2.18]}, "hold": {"handN": [-0.65, 3.05], "wa": 125, "handF": [0.47, 2.44]}, "swing": {"handN": [0.22, 1.42]}, "contact": {"elbF": None, "handF": [1.10, 2.50]}, "follow": {"elbF": None, "handF": [0.95, 2.75]}, "recover": {"handF": [0.98, 2.01]}, "settle": {"handN": [0.26, 1.71], "handF": [0.84, 2.13]}}
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
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(repo, 'tools', 'pixelart'))
import posekit as pk  # noqa: E402
import walk8 as w8  # noqa: E402

HEAD, SLOT, H, BASE, SCALE = w8.HEAD_PX, w8.SLOT, w8.SH_, w8.BASELINE, w8.SCALE
DX = (SLOT / 2 - cfg.get('x0', SLOT / 2)) / HEAD          # table x -> posekit world x (posekit puts world x 0 on column 192)
B = pk.Body(4.0)
OUTLINE = (58, 54, 64)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


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
    p['arms'] = 'natural'      # ARMS: posekit natural-arms 1 - the elbow bends the anatomical way (SPEC 10.3b)
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
    g = 1.5 / HEAD
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


def shield(J, f, scfg):
    c = J['hand' + scfg.get('hand', 'F')]
    ang = math.radians(f.get('shield_ang', scfg.get('ang', 0)))
    return [(pk.ell(c, scfg['w'] / 2, scfg['h'] / 2, ang), rgb(scfg['rgb']))]


def frame_images(J, parts, f):
    layers, _ = w8.frame_layers(parts, J, OY)
    if 'weapon' in cfg:
        wc = cfg['weapon']
        layers[wc['layer']] = Image.fromarray(prop_layer(sword(J, f, wc)), 'RGBA')
    if 'shield' in cfg:
        sc = cfg['shield']
        layers[sc['layer']] = Image.fromarray(prop_layer(shield(J, f, sc)), 'RGBA')
    flat = Image.new('RGB', (SLOT, H), pk.BG)
    for name in cfg['layers']:
        if name == 'joints':
            continue
        flat.paste(layers[name], (0, 0), layers[name])
    return layers, flat


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
            rec['weapon_tip'] = [round(float(c), 1) for c in W2P(J['wtip'])]
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
    # game-size contact sheet of the preview frames side by side (what the GIF plays, for a quick look at every frame)
    sheet = Image.new('RGB', (sum(s.width for s in small) + 4 * (len(small) - 1), small[0].height), (20, 20, 20))
    x = 0
    for s in small:
        sheet.paste(s, (x, 0))
        x += s.width + 4
    sheet.save(os.path.join(out, f'{cfg["set"]}_game_sheet.png'))
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
        print('ASEPRITE_PATH not set: no .aseprite written')
    print(f'{cfg["set"]}: {len(flats)} frames, floor row {OY}, posekit warnings {len(warns)}')
    for w in warns:
        print('  ' + w)
    for r_ in recs:
        print(f'  {r_["frame"]:8s} x {r_["x_range"][0]}..{r_["x_range"][1]}  top {r_["top"]}  lowest {r_["lowest"]}  tip {r_.get("weapon_tip")}')


main()
