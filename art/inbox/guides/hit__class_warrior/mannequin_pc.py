"""Motion mannequin (attack / hit / idle) from a frame table, on the posekit body - PC (Aseprite) session tool.
This copy: hit__class_warrior (general warrior hit reaction, normal weight). The delivered set table is embedded below (SET).

  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO OUT_DIR            (the embedded SET)
  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO SET.json OUT_DIR   (another table)

SET = {"set": "atk__class_warrior", "tag": "attack", "x0": 152,
       "layers": ["arm_far", "shield", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
       "weapon": {"type": "sword", "hand": "N", "layer": "weapon_front", "blade": 0.75, "reach": 0.85, "grip": 0.22,
                  "width": 0.08, "guard": [0.30, 0.06], "blade_rgb": "#C8C8D0", "grip_rgb": "#8A5A2B"},
       "shield": {"hand": "F", "layer": "shield", "w": 0.68, "h": 0.90, "ang": 0, "rgb": "#6E7F99"},
       "auto_tilt": true,            # attack sets: tilt = lean/2 (+ head_off correction); hit sets false: the table's tilt as given
       "frame_tags": false,          # true: one more tag per frame named exactly as the table's frame name
       "defaults": {...},            # keys merged into every frame (e.g. "toeN": 0.85, "faN": 0, "faF": 0, the feet)
       "preview_idle": {...},        # optional: an idle frame (same keys as a frame) shown before/after in <set>_context.gif only
       "frames": [{"name": "in", "ms": 70, "hip": [x, h], "lean": rad, "tilt": rad, "head_off": [x, h],
                   "footN": [x, h], "footF": [x, h], "faN": deg, "faF": deg, "toeN": f,
                   "handN": [x, h], "handF": [x, h], "elbN": [dx, dy], "elbF": [dx, dy], "wa": deg, "shield_ang": deg}, ...]}
Table units are heads (110 px): x from the set's column x0 (x px = x0 + 110 x), h above the floor (y px = 870 - 110 h).
Planted feet (h <= ankle height) are settled so that leg's lowest pixel is exactly on y=870 (one floor for every frame).
Writes OUT_DIR/layers/F<n>_<layer>.png, <set>.aseprite (Aseprite from ASEPRITE_PATH, build_motion_ase.lua next to this script;
frame ms, tag(s), hidden joints), <set>_strip.png (all frames side by side), <set>_preview.gif (game size 0.1654 x4, the frame ms),
<set>_game.png (game-size review sheet: idle + frames x4, and each frame over the idle's ghost), <set>_context.gif
(idle -> the frames -> idle at real ms) and frames.json (joint px per frame + posekit warnings)."""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- the delivered table (README hit__class_warrior, see CHANGES)
SET = {
    "set": "hit__class_warrior", "tag": "hit", "x0": 192, "auto_tilt": False, "frame_tags": True,
    "layers": ["arm_far", "shield", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
    "weapon": {"type": "sword", "hand": "N", "layer": "weapon_front", "blade": 0.75, "reach": 0.85, "grip": 0.22, "width": 0.08,
               "guard": [0.30, 0.06], "blade_rgb": "#C8C8D0", "grip_rgb": "#8A5A2B"},
    "shield": {"hand": "F", "layer": "shield", "w": 0.68, "h": 0.90, "ang": 0, "rgb": "#6E7F99"},
    "defaults": {"footN": [-0.90, 0.12], "footF": [0.80, 0.12], "toeN": 0.85, "faN": 0, "faF": 0},
    "preview_idle": {"name": "idle", "ms": 400, "hip": [0.00, 1.40], "lean": 0.08, "tilt": 0.0,
                     "handN": [0.06, 1.71], "handF": [0.78, 2.07], "wa": 38},
    "frames": [
        {"name": "K1 impact", "ms": 70, "hip": [-0.05, 1.27], "lean": 0.00, "tilt": -0.12, "head_off": [-0.04, -0.02],
         "handN": [0.00, 1.60], "handF": [0.62, 2.25], "wa": 20},
        {"name": "K2 peak", "ms": 100, "hip": [-0.08, 1.21], "lean": -0.06, "tilt": -0.10, "head_off": [-0.04, -0.03],
         "handN": [-0.30, 1.70], "handF": [0.60, 2.12], "wa": 30},
        {"name": "K3 recover", "ms": 80, "hip": [-0.04, 1.31], "lean": 0.03, "tilt": -0.05, "head_off": [-0.02, -0.01],
         "handN": [-0.05, 1.66], "handF": [0.65, 2.10], "wa": 30},
        {"name": "K4 settle", "ms": 70, "hip": [-0.01, 1.38], "lean": 0.07, "tilt": -0.01, "head_off": [0.0, 0.0],
         "handN": [0.05, 1.71], "handF": [0.76, 2.07], "wa": 36},
    ],
}
# CHANGES vs the README table (README "이 캐릭터만의 것": the shield hand retreats only 0.1-0.2 head from the idle 0.78, the head
# ducks behind it; the table had 0.23 / 0.30): K1 shield hand x +0.55 -> +0.62 head (253 -> 260 px), K2 +0.48 -> +0.60 (245 -> 258 px).
# Heights, the K1/K2 body (posekit HIT_KEYS k1_mid / k2_mid), K3, K4, the sword and every ms are the README's.

repo = sys.argv[1]
if len(sys.argv) >= 4:
    setf, out = sys.argv[2], sys.argv[3]
    cfg = json.load(open(setf, encoding='utf-8'))
else:
    out = sys.argv[2]
    cfg = SET
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


def full(f):
    """a frame with the set's defaults filled in"""
    return dict(cfg.get('defaults', {}), **f)


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


def game_size(flat):
    """game-size crop (0.1654, BOX) of a frame, magenta -> dark green, x4 nearest"""
    a = np.asarray(flat).copy()
    msk = np.all(a == np.array(pk.BG, np.uint8), axis=-1)
    a[msk] = (46, 58, 46)
    c = Image.fromarray(a).crop((0, BASE - 520, SLOT, BASE + 20))
    c = c.resize((round(c.width * SCALE), round(c.height * SCALE)), Image.BOX)
    return c.resize((c.width * 4, c.height * 4), Image.NEAREST)


def ghost(flat, idle):
    """game-size frame with the idle silhouette's outline drawn over it (where did it move?)"""
    def mask(im):
        a = np.asarray(im.crop((0, BASE - 520, SLOT, BASE + 20)))
        m = ~np.all(a == np.array(pk.BG, np.uint8), axis=-1)
        s = Image.fromarray((m * 255).astype(np.uint8)).resize((round(SLOT * SCALE), round(540 * SCALE)), Image.BOX)
        return np.asarray(s) >= 128
    g = np.asarray(game_size(flat)).copy()
    mi = mask(idle)
    edge = mi & ~(np.roll(mi, 1, 0) & np.roll(mi, -1, 0) & np.roll(mi, 1, 1) & np.roll(mi, -1, 1))
    e4 = np.kron(edge, np.ones((4, 4), bool))[:g.shape[0], :g.shape[1]]
    g[e4] = (255, 230, 0)
    return Image.fromarray(g)


def main():
    ldir = os.path.join(out, 'layers')
    os.makedirs(ldir, exist_ok=True)
    recs, flats, warns = [], [], []
    frames = [full(f) for f in cfg['frames']]
    for i, f in enumerate(frames):
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
        recs.append(rec)
    strip = Image.new('RGB', (SLOT * len(flats), H), pk.BG)
    for i, fl in enumerate(flats):
        strip.paste(fl, (i * SLOT, 0))
    strip.save(os.path.join(out, f'{cfg["set"]}_strip.png'))
    small = [game_size(fl) for fl in flats]
    small[0].save(os.path.join(out, f'{cfg["set"]}_preview.gif'), save_all=True, append_images=small[1:],
                  duration=[f['ms'] for f in frames], loop=0)
    if 'preview_idle' in cfg:                       # review only, never in the .aseprite
        fi = full(cfg['preview_idle'])
        _, Ji, partsi = solve(fi, 'idle')
        _, idle = frame_images(Ji, partsi, fi)
        si = game_size(idle)
        seq = [si] + small + [si]
        seq[0].save(os.path.join(out, f'{cfg["set"]}_context.gif'), save_all=True, append_images=seq[1:],
                    duration=[fi['ms']] + [f['ms'] for f in frames] + [fi['ms'] + 200], loop=0)
        gh = [ghost(fl, idle) for fl in flats]
        w, h = si.width, si.height
        sheet = Image.new('RGB', ((len(flats) + 1) * (w + 8), 2 * (h + 8)), (20, 20, 20))
        for k, im in enumerate([si] + small):
            sheet.paste(im, (k * (w + 8), 0))
        for k, im in enumerate(gh):
            sheet.paste(im, ((k + 1) * (w + 8), h + 8))
        sheet.save(os.path.join(out, f'{cfg["set"]}_game.png'))
    json.dump(dict(set=cfg['set'], oy=OY, posekit_warnings=warns, frames=recs), open(os.path.join(out, 'frames.json'), 'w', encoding='utf-8'), indent=1)
    exe = os.environ.get('ASEPRITE_PATH')
    dst = os.path.abspath(os.path.join(out, cfg['set'] + '.aseprite'))
    if exe:
        if os.path.exists(dst):
            os.remove(dst)
        lua = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_motion_ase.lua')
        args = [exe, '-b', '--script-param', 'dir=' + os.path.abspath(ldir), '--script-param', 'out=' + dst,
                '--script-param', 'ms=' + ','.join(str(f['ms']) for f in frames),
                '--script-param', 'layers=' + ','.join(cfg['layers']), '--script-param', 'tag=' + cfg.get('tag', '')]
        if cfg.get('frame_tags'):
            args += ['--script-param', 'names=' + ','.join(f['name'] for f in frames)]
        r = subprocess.run(args + ['--script', lua], capture_output=True)
        print(('wrote ' + dst) if os.path.exists(dst) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    else:
        print('ASEPRITE_PATH not set: no .aseprite written')
    print(f'{cfg["set"]}: {len(flats)} frames, floor row {OY}, posekit warnings {len(warns)}')
    for w in warns:
        print('  ' + w)
    for r_ in recs:
        J = r_['joints']
        print(f'  {r_["frame"]:10s} x {r_["x_range"][0]}..{r_["x_range"][1]}  top {r_["top"]}  lowest {r_["lowest"]}  tip {r_.get("weapon_tip")}  '
              f'hip {J["hip"]}  head C {J["C"]}  handF {J["handF"]}  ank {J["ankN"]} / {J["ankF"]}')


main()
