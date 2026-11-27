"""Motion mannequin (attack / hit / idle) from a frame table, on the posekit body - PC (Aseprite) session tool.

  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO OUT_DIR            (the table embedded below, CFG)
  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO SET.json OUT_DIR   (a table from a json file)

SET.json / CFG = {"set": "hit__captain_shadowqueen", "tag": "hit", "x0": 192, "auto_tilt": false, "frame_tags": true,
            "layers": ["weapon_back", "arm_far", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
            "weapons": [{"hand": "N", "layer": "weapon_front", "angle": "wa", "blade": 0.75, "reach": 0.85, "grip": 0.30,
                         "width": 0.08, "guard": [0.25, 0.06], "blade_rgb": "#D0D0D8", "grip_rgb": "#8A5A2B"},
                        {"hand": "F", "layer": "weapon_back", "angle": "waF", ...}],
            ("weapon": {...one sword...} and "shield": {"hand": "F", "layer": "shield", "w", "h", "ang", "rgb"} still work)
            "idle": {...a frame dict...}   (optional: drawn as a grey ghost under every frame of the game-size sheet)
            "frames": [{"name": "K1 impact", "ms": 60, "hip": [x, h], "lean": rad, "tilt": rad, "head_off": [dx, dh],
                        "footN": [x, h], "footF": [x, h], "faN": deg, "faF": deg, "toeN": k,
                        "handN": [x, h], "handF": [x, h], "elbN": [dx, dy], "elbF": [dx, dy], "wa": deg, "waF": deg}, ...]}
Table units are heads (110 px): x from the set's column x0 (x px = x0 + 110 x), h above the floor (y px = 870 - 110 h).
"auto_tilt" true (attack sets, default): tilt = lean / 2 + the frame's tilt, head centre kept on the torso axis;
false (hit sets): the table's tilt as given (pc_notes 2026-11-26e). "frame_tags": one Aseprite tag per frame named as the frame.
Planted feet (h <= ankle height) are settled so that leg's lowest pixel is exactly on y=870 (one floor for every frame).
Writes OUT_DIR/layers/F<n>_<layer>.png, <set>.aseprite (Aseprite from ASEPRITE_PATH; frame ms, tags, hidden joints),
<set>_strip.png (all frames side by side), <set>_preview.gif (game size 0.1654 x4, the frame ms), <set>_game.png (game-size
contact sheet x4: top row as the game shows it, bottom row over the idle ghost) and frames.json (joint px per frame + posekit warnings).
The Aseprite builder build_motion_ase.lua is looked up next to this script."""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- the delivered table (hit__captain_shadowqueen, README 2026-11-26e)
CFG = {
    "set": "hit__captain_shadowqueen", "tag": "hit", "x0": 192, "auto_tilt": False, "frame_tags": True,
    "layers": ["weapon_back", "arm_far", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
    "weapons": [
        {"hand": "N", "layer": "weapon_front", "angle": "wa", "blade": 0.75, "reach": 0.85, "grip": 0.30, "width": 0.08,
         "guard": [0.25, 0.06], "blade_rgb": "#D0D0D8", "grip_rgb": "#8A5A2B"},
        {"hand": "F", "layer": "weapon_back", "angle": "waF", "blade": 0.75, "reach": 0.85, "grip": 0.30, "width": 0.08,
         "guard": [0.25, 0.06], "blade_rgb": "#A8A8B4", "grip_rgb": "#6F4A26"}],
    "idle": {"name": "idle", "ms": 0, "hip": [0.0, 1.40], "lean": 0.08, "tilt": 0.0, "toeN": 0.85,
             "footN": [-0.48, 0.12], "footF": [0.37, 0.12], "handN": [0.30, 1.55], "handF": [0.50, 1.62], "wa": -80, "waF": -70},
    # README table as given (hip, lean, tilt, head_off, feet, hands); PC changes: toeN 0.85 on every frame (the HIT_KEYS hit_body /
    # checker idle-reference back boot) and the blade angles (README: idle -80 / -70, all frames within -85..-60): the tips lag the
    # snap back (K1 -68 / -62, K2 -72 / -64), trail on the way forward (K3 -84 / -76) and settle at the idle's -80 / -70 (K4)
    "frames": [
        {"name": "K1 impact", "ms": 60, "hip": [-0.08, 1.24], "lean": -0.06, "tilt": -0.16, "head_off": [-0.05, -0.02], "toeN": 0.85,
         "footN": [-0.48, 0.12], "footF": [0.37, 0.12], "handN": [0.22, 1.50], "handF": [0.40, 1.58], "wa": -68, "waF": -62},
        {"name": "K2 stagger", "ms": 110, "hip": [-0.12, 1.17], "lean": -0.15, "tilt": -0.12, "head_off": [-0.05, -0.03], "toeN": 0.85,
         "footN": [-0.78, 0.12], "footF": [0.37, 0.12], "handN": [0.05, 1.50], "handF": [0.30, 1.62], "wa": -72, "waF": -64},
        {"name": "K3 recover", "ms": 90, "hip": [-0.06, 1.28], "lean": -0.03, "tilt": -0.06, "head_off": [-0.02, -0.01], "toeN": 0.85,
         "footN": [-0.63, 0.12], "footF": [0.37, 0.12], "handN": [0.18, 1.52], "handF": [0.40, 1.60], "wa": -84, "waF": -76},
        {"name": "K4 settle", "ms": 80, "hip": [-0.02, 1.37], "lean": 0.06, "tilt": -0.01, "head_off": [0.0, 0.0], "toeN": 0.85,
         "footN": [-0.50, 0.12], "footF": [0.37, 0.12], "handN": [0.27, 1.55], "handF": [0.47, 1.62], "wa": -80, "waF": -70},
    ],
}

# ---------------------------------------------------------------- ARMS: table changes for posekit natural-arms 2 (README 「팔 고침」 2차)
# the frame keys below replace the table's (None removes the key); "*" = set-level keys
ARMS_FIX = {"*": {"idle": {"name": "idle", "ms": 0, "hip": [0.0, 1.40], "lean": 0.08, "tilt": 0.0, "toeN": 0.85, "footN": [-0.48, 0.12], "footF": [0.37, 0.12], "handN": [0.30, 1.55], "handF": [0.90, 1.42], "wa": -80, "waF": -70}}, "K1 impact": {"handF": [0.86, 1.52]}, "K2 stagger": {"handF": [0.78, 1.66]}, "K3 recover": {"handF": [0.86, 1.40]}, "K4 settle": {"handF": [0.90, 1.42]}}
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
    cfg = CFG
elif len(args) == 3:
    repo, setf, out = args
    cfg = json.load(open(setf, encoding='utf-8'))
else:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(repo, 'tools', 'pixelart'))
import posekit as pk  # noqa: E402
assert getattr(pk, 'ARMS_VERSION', '').startswith('posekit natural-arms 2'), 'pull the repo: this table needs posekit natural-arms 2 (tools/pixelart/posekit.py)'  # ARMS
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
    return (float(SLOT / 2 + v[0] * HEAD), float(OY + v[1] * HEAD))


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
    """a flat straight blade in one hand: tip `reach` from the hand dot along the frame's angle, guard at reach - blade,
    grip + pommel `grip` behind the guard"""
    side = wcfg.get('hand', 'N')
    Hd = J['hand' + side]
    d = pk.wdir(f[wcfg.get('angle', 'wa')])
    pn = np.array((d[1], -d[0]))
    reach, blade, grip, wid = wcfg['reach'], wcfg['blade'], wcfg['grip'], wcfg['width']
    g0 = Hd + d * (reach - blade)                       # guard centre = start of the blade
    tip = Hd + d * reach
    bl = [g0 + pn * wid / 2, tip - d * wid + pn * wid / 2, tip, tip - d * wid - pn * wid / 2, g0 - pn * wid / 2]
    gl, gt = wcfg['guard']
    guard = [g0 + pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 - d * gt / 2, g0 + pn * gl / 2 - d * gt / 2]
    back = g0 - d * grip
    J['wtip' + side] = tip
    return [(pk.cap(back + d * 0.04, g0, 0.035), rgb(wcfg['grip_rgb'])), (pk.ell(back + d * 0.04, 0.045, 0.045), rgb(wcfg['grip_rgb'])),
            (pk.poly(bl), rgb(wcfg['blade_rgb'])), (pk.poly(guard), rgb(wcfg['grip_rgb']))]


def shield(J, f, scfg):
    c = J['hand' + scfg.get('hand', 'F')]
    ang = math.radians(f.get('shield_ang', scfg.get('ang', 0)))
    return [(pk.ell(c, scfg['w'] / 2, scfg['h'] / 2, ang), rgb(scfg['rgb']))]


def weapon_list():
    if 'weapons' in cfg:
        return cfg['weapons']
    if 'weapon' in cfg:
        return [dict(cfg['weapon'], angle='wa')]
    return []


def frame_images(J, parts, f):
    layers, _ = w8.frame_layers(parts, J, OY)
    for wc in weapon_list():
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


def game_small(flat, ghost=None):
    """one frame as the game shows it: crop, 0.1654 BOX, x4 NEAREST, on a dark ground; ghost = an idle flat drawn grey below"""
    a = np.asarray(flat).copy()
    msk = np.all(a == np.array(pk.BG, np.uint8), axis=-1)
    a[msk] = (46, 58, 46)
    if ghost is not None:
        g = np.asarray(ghost)
        gm = ~np.all(g == np.array(pk.BG, np.uint8), axis=-1)
        a[msk & gm] = (120, 132, 120)
    c = Image.fromarray(a).crop((0, BASE - 520, SLOT, BASE + 20))
    c = c.resize((round(c.width * SCALE), round(c.height * SCALE)), Image.BOX)
    return c.resize((c.width * 4, c.height * 4), Image.NEAREST)


def foot_band(layers):
    """x extent of each leg layer in the 5 rows above and on the floor line (sole band) -> {'N': (x0, x1), 'F': (x0, x1)}"""
    out_ = {}
    for s, ln in (('N', 'leg_near'), ('F', 'leg_far')):
        al = np.asarray(layers[ln])[BASE - 4:BASE + 1, :, 3] > 0
        xs = np.nonzero(al.any(0))[0]
        out_[s] = (int(xs.min()), int(xs.max())) if len(xs) else None
    return out_


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
        hd = np.asarray(layers['head'])[..., 3] > 0
        hy, hx = np.nonzero(hd)
        rec = dict(frame=f['name'], ms=f['ms'], x_range=[int(xs.min()), int(xs.max())], top=int(ys.min()), lowest=int(ys.max()),
                   head_centre=[round(float(hx.mean()), 1), round(float(hy.mean()), 1)], soles=foot_band(layers),
                   joints={k: [round(c, 1) for c in W2P(J[k])] for k in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF',
                                                                          'elbN', 'elbF', 'handN', 'handF', 'neck0', 'C')})
        for k in ('wtip', 'wtipN', 'wtipF'):
            if k in J:
                rec[k] = [round(c, 1) for c in W2P(J[k])]
        recs.append(rec)
    strip = Image.new('RGB', (SLOT * len(flats), H), pk.BG)
    for i, fl in enumerate(flats):
        strip.paste(fl, (i * SLOT, 0))
    strip.save(os.path.join(out, f'{cfg["set"]}_strip.png'))
    small = [game_small(fl) for fl in flats]
    small[0].save(os.path.join(out, f'{cfg["set"]}_preview.gif'), save_all=True, append_images=small[1:],
                  duration=[f['ms'] for f in cfg['frames']], loop=0)
    ghost = None
    if 'idle' in cfg:
        _, Ji, pi_ = solve(cfg['idle'], 'idle ghost')
        _, ghost = frame_images(Ji, pi_, cfg['idle'])
    panels = [game_small(ghost)] if ghost is not None else []
    panels_g = [game_small(ghost)] if ghost is not None else []
    panels += small
    panels_g += [game_small(fl, ghost) for fl in flats]
    pw, ph = panels[0].size
    sheet = Image.new('RGB', (pw * len(panels), ph * 2 + 16), (20, 20, 20))
    dr = ImageDraw.Draw(sheet)
    names = (['idle (ghost)'] if ghost is not None else []) + [f'{f["name"]} {f["ms"]}ms' for f in cfg['frames']]
    for i, (a_, b_) in enumerate(zip(panels, panels_g)):
        sheet.paste(a_, (i * pw, 0))
        sheet.paste(b_, (i * pw, ph + 16))
        dr.text((i * pw + 4, ph + 2), names[i], fill=(255, 255, 255))
    sheet.save(os.path.join(out, f'{cfg["set"]}_game.png'))
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
            cmd += ['--script-param', 'names=' + ','.join(f['name'] for f in cfg['frames'])]
        r = subprocess.run(cmd + ['--script', lua], capture_output=True)
        print(('wrote ' + dst) if os.path.exists(dst) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    else:
        print('ASEPRITE_PATH not set: no .aseprite written')
    print(f'{cfg["set"]}: {len(flats)} frames, floor row {OY}, posekit warnings {len(warns)}')
    for w in warns:
        print('  ' + w)
    for r_ in recs:
        J_ = r_['joints']
        print(f'  {r_["frame"]:11s} x {r_["x_range"][0]}..{r_["x_range"][1]}  top {r_["top"]}  lowest {r_["lowest"]}  head {r_["head_centre"]}'
              f'  hip {J_["hip"]}  ank N {J_["ankN"]} F {J_["ankF"]}  soles N {r_["soles"]["N"]} F {r_["soles"]["F"]}'
              f'  tips N {r_.get("wtipN")} F {r_.get("wtipF")}')


main()
