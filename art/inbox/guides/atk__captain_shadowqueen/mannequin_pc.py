"""Motion mannequin (attack / hit / idle) from a frame table, on the posekit body - PC (Aseprite) session tool.
Copy for atk__captain_shadowqueen (Nikla, twin daggers): two weapons (one per hand, own layer and own angle), frame-name tags,
the delivered set table (SET) and the Aseprite build script (LUA) embedded, so this one file rebuilds the delivery.

  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO OUT_DIR              (the embedded table SET below)
  uv run --no-project --with pillow --with numpy python mannequin_pc.py REPO SET.json OUT_DIR     (a table from a json file)

SET = {"set": "atk__captain_shadowqueen", "tag": "attack", "x0": 52, "frame_tags": true,
       "layers": ["weapon_back", "arm_far", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
       "pose": {"toeN": 0.85, "faN": 0, "faF": 0},                 # keys every frame gets unless it sets its own
       "weapons": [{"type": "dagger", "hand": "N", "layer": "weapon_front", "angle": "wa", "reach": 0.85, "guard_at": 0.12,
                    "behind": 0.20, "width": 0.08, "point": 0.10, "guard": [0.25, 0.06], "grip_r": 0.025, "pommel_r": 0.035,
                    "blade_rgb": "#D0D0D8", "grip_rgb": "#6B4A30"},
                   {... "hand": "F", "layer": "weapon_back", "angle": "waF", ...}],
       "frames": [{"name": "in", "ms": 60, "hip": [x, h], "lean": rad, "tilt": rad (added to lean/2),
                   "footN": [x, h], "footF": [x, h], "faN": deg, "faF": deg, "toeN": k,
                   "handN": [x, h], "handF": [x, h], "elbN": [dx, dy], "elbF": [dx, dy], "wa": deg, "waF": deg}, ...]}
(the older single "weapon" (type sword) and "shield" keys of the generic tool still work.)
Table units are heads (110 px): x from the set's column x0 (x px = x0 + 110 x), h above the floor (y px = 870 - 110 h);
hands are the hand centre at its real height above the floor. Weapon angles are maths degrees from the hand dot to the tip
(0 forward, 90 up, -90 down). A dagger: hand dot -> tip = reach, the guard `guard_at` in front of the hand dot, the grip and
pommel ending `behind` behind it, the blade `width` wide narrowing to the tip over the last `point`; flat colours, 1.5 px outline.
Planted feet (h <= ankle height) are settled so that leg's lowest pixel is exactly on y=870 (one floor for every frame).
Writes OUT_DIR/layers/F<n>_<layer>.png, <set>.aseprite (Aseprite from ASEPRITE_PATH; frame ms, the motion tag over all frames,
one tag per frame name when frame_tags, hidden joints), <set>_strip.png (all frames side by side, 384 px each), <set>_game.png
(game size 0.1654 x4, side by side, on a dark floor colour), <set>_preview.gif (game size x4, the frame ms) and frames.json
(joint px per frame, weapon tips + posekit warnings). The Aseprite build script is written to OUT_DIR/build_motion_ase.lua from LUA."""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- the delivered set (README table + the PC's changes)
SET = {
    "set": "atk__captain_shadowqueen", "tag": "attack", "x0": 52, "frame_tags": True, "auto_tilt": True,
    "layers": ["weapon_back", "arm_far", "leg_far", "leg_near", "torso", "head", "weapon_front", "arm_near", "joints"],
    "pose": {"toeN": 0.85, "faN": 0, "faF": 0},
    # daggers: README sizes (hand -> tip 0.85, blade 0.08 wide, guard 0.25 x 0.06, grip + pommel 0.20 behind the hand);
    # PC: grip / pommel thin (radius 0.025 / 0.035) and a short point (0.10) so 60 %+ of each dagger reads outside the body
    "weapons": [
        {"type": "dagger", "hand": "N", "layer": "weapon_front", "angle": "wa", "reach": 0.85, "guard_at": 0.12, "behind": 0.20,
         "width": 0.08, "point": 0.10, "guard": [0.25, 0.06], "grip_r": 0.025, "pommel_r": 0.035,
         "blade_rgb": "#D0D0D8", "grip_rgb": "#6B4A30"},
        {"type": "dagger", "hand": "F", "layer": "weapon_back", "angle": "waF", "reach": 0.85, "guard_at": 0.12, "behind": 0.20,
         "width": 0.08, "point": 0.10, "guard": [0.25, 0.06], "grip_r": 0.025, "pommel_r": 0.035,
         "blade_rgb": "#A8A8B4", "grip_rgb": "#5A3E28"}],
    "frames": [
        {"name": "in",      "ms": 60,  "hip": [0.70, 1.36], "lean": 0.00,  "footN": [0.00, 0.12], "footF": [1.40, 0.12],
         "handN": [0.75, 2.45], "handF": [0.95, 2.35], "wa": 60,  "waF": 100},
        # hold (PC, measured on accepted cell #2 aligned on the rear boot): fists ~95 px apart above their own shoulders, elbows
        # out, the X crossing mid-blade above the head (README: hands 0.90 / 1.05 at 3.40, 50 / 130 deg)
        {"name": "hold",    "ms": 110, "hip": [0.90, 1.34], "lean": -0.10, "footN": [0.00, 0.12], "footF": [1.75, 0.12],
         "handN": [0.45, 3.55], "handF": [1.36, 3.55], "elbN": [-1, 0.2], "elbF": [1, 0.2], "wa": 38,  "waF": 145},
        # swing (PC, measured on accepted cell #3 aligned on the front boot): torso leaned forward like the cell (~0.45 there),
        # hip a little forward / lower, hands still pulled in so the tips stay inside x=351 and behind the contact's reach
        # (README: hip 0.95 / 1.12, lean 0.22, hands 1.62 / 1.85 and 1.66 / 2.10)
        {"name": "swing",   "ms": 50,  "hip": [1.00, 1.10], "lean": 0.38,  "footN": [0.00, 0.12], "footF": [1.95, 0.12],
         "handN": [1.72, 1.78], "handF": [1.78, 1.98], "wa": -30, "waF": 10},
        {"name": "contact", "ms": 60,  "hip": [1.42, 1.08], "lean": 0.20,  "footN": [0.00, 0.12], "footF": [1.95, 0.12],
         "handN": [1.92, 1.70], "handF": [1.82, 2.20], "wa": 25,  "waF": -10},
        {"name": "follow",  "ms": 80,  "hip": [1.46, 1.10], "lean": 0.24,  "footN": [0.15, 0.12], "footF": [1.95, 0.12],
         "handN": [1.95, 1.85], "handF": [1.85, 2.05], "wa": 55,  "waF": -40},
        {"name": "recover", "ms": 80,  "hip": [1.32, 1.26], "lean": 0.12,  "footN": [0.35, 0.12], "footF": [1.95, 0.12],
         "handN": [1.62, 1.60], "handF": [1.68, 1.78], "wa": -60, "waF": -50},
        {"name": "settle",  "ms": 60,  "hip": [1.28, 1.34], "lean": 0.04,  "footN": [0.60, 0.12], "footF": [1.95, 0.12],
         "handN": [1.34, 1.62], "handF": [1.58, 1.68], "wa": -80, "waF": -70},
    ]}

# ---------------------------------------------------------------- Aseprite build script (written next to the output)
LUA = r'''-- Builds a layered, animated .aseprite for a motion mannequin from per-frame layer PNGs <dir>/F<n>_<layer>.png
-- params: dir, out, ms (comma list), layers (bottom to top), tag (over all frames), names (comma list: one tag per frame, optional)
-- Background (#FF00FF) at the bottom, then `layers` bottom to top; `joints` is hidden.
local p = app.params
local dir, out = p.dir, p.out
local ms = {}
for v in string.gmatch(p.ms, "[^,]+") do ms[#ms + 1] = tonumber(v) end
local n = #ms
local names = {}
for v in string.gmatch(p.layers, "[^,]+") do names[#names + 1] = v end
local first = Image{ fromFile = dir .. "/F1_" .. names[1] .. ".png" }
local spr = Sprite(first.width, first.height, ColorMode.RGB)
local bg = spr.layers[1]
bg.name = "Background"
for f = 2, n do spr:newEmptyFrame(f) end
for f = 1, n do
  local img = Image(spr.width, spr.height, ColorMode.RGB)
  img:clear(Color{ r = 255, g = 0, b = 255, a = 255 })
  spr:newCel(bg, f, img, Point(0, 0))
  spr.frames[f].duration = ms[f] / 1000.0
end
for _, name in ipairs(names) do
  local l = spr:newLayer()
  l.name = name
  for f = 1, n do
    local im = Image{ fromFile = dir .. "/F" .. f .. "_" .. name .. ".png" }
    spr:newCel(l, f, im, Point(0, 0))
  end
  if name == "joints" then l.isVisible = false end
end
if p.tag and p.tag ~= "" then
  local t = spr:newTag(1, n)
  t.name = p.tag
end
if p.names and p.names ~= "" then
  local i = 0
  for v in string.gmatch(p.names, "[^,]+") do
    i = i + 1
    local t = spr:newTag(i, i)
    t.name = v
  end
end
spr:saveAs(out)
'''

if len(sys.argv) == 3:
    repo, out = sys.argv[1:3]
    cfg = SET
elif len(sys.argv) == 4:
    repo, setf, out = sys.argv[1:4]
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
FLOOR_RGB = (46, 58, 46)


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def xy(v):
    return (v[0] - DX, v[1])


def frame_cfg(f):
    """the frame's keys over the set's per-pose defaults"""
    d = dict(cfg.get('pose', {}))
    d.update(f)
    return d


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
        for k in ('elb', 'knee'):
            if k + side in f:
                p[k + side] = tuple(f[k + side])
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
    """the warrior's sword (generic tool): reach = hand -> tip, blade = guard -> tip, grip = guard -> pommel"""
    Hd = J['hand' + wcfg.get('hand', 'N')]
    d = pk.wdir(f[wcfg.get('angle', 'wa')])
    pn = np.array((d[1], -d[0]))
    reach, blade, grip, wid = wcfg['reach'], wcfg['blade'], wcfg['grip'], wcfg['width']
    g0 = Hd + d * (reach - blade)                       # guard centre = start of the blade
    tip = Hd + d * reach
    bl = [g0 + pn * wid / 2, tip - d * wid + pn * wid / 2, tip, tip - d * wid - pn * wid / 2, g0 - pn * wid / 2]
    gl, gt = wcfg['guard']
    guard = [g0 + pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 - d * gt / 2, g0 + pn * gl / 2 - d * gt / 2]
    back = g0 - d * grip
    return tip, [(pk.cap(back + d * 0.04, g0, 0.035), rgb(wcfg['grip_rgb'])), (pk.ell(back + d * 0.04, 0.045, 0.045), rgb(wcfg['grip_rgb'])),
                 (pk.poly(bl), rgb(wcfg['blade_rgb'])), (pk.poly(guard), rgb(wcfg['grip_rgb']))]


def dagger(J, f, wcfg):
    """a short blade in a forward grip: hand dot -> tip = reach, guard `guard_at` in front of the hand dot, grip + pommel ball
    ending `behind` behind it, the blade `width` wide narrowing to its point over the last `point`"""
    Hd = J['hand' + wcfg['hand']]
    d = pk.wdir(f[wcfg['angle']])
    pn = np.array((d[1], -d[0]))
    wid, ga, pt = wcfg['width'], wcfg['guard_at'], wcfg.get('point', 0.14)
    g0 = Hd + d * ga
    tip = Hd + d * wcfg['reach']
    bl = [g0 + pn * wid / 2, tip - d * pt + pn * wid / 2, tip, tip - d * pt - pn * wid / 2, g0 - pn * wid / 2]
    gl, gt = wcfg['guard']
    guard = [g0 + pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 + d * gt / 2, g0 - pn * gl / 2 - d * gt / 2, g0 + pn * gl / 2 - d * gt / 2]
    rp = wcfg.get('pommel_r', 0.045)
    pom = Hd - d * (wcfg['behind'] - rp)
    col_g = rgb(wcfg['grip_rgb'])
    return tip, [(pk.cap(pom, g0, wcfg.get('grip_r', 0.035)), col_g), (pk.ell(pom, rp, rp), col_g), (pk.poly(bl), rgb(wcfg['blade_rgb'])),
                 (pk.poly(guard), col_g)]


def shield(J, f, scfg):
    c = J['hand' + scfg.get('hand', 'F')]
    ang = math.radians(f.get('shield_ang', scfg.get('ang', 0)))
    return [(pk.ell(c, scfg['w'] / 2, scfg['h'] / 2, ang), rgb(scfg['rgb']))]


def weapon_list():
    ws = list(cfg.get('weapons', []))
    if 'weapon' in cfg:
        ws.append(cfg['weapon'])
    return ws


def frame_images(J, parts, f):
    layers, _ = w8.frame_layers(parts, J, OY)
    tips = {}
    for wc in weapon_list():
        tip, shapes = (dagger if wc.get('type') == 'dagger' else sword)(J, f, wc)
        tips[wc['layer']] = tip
        layers[wc['layer']] = Image.fromarray(prop_layer(shapes), 'RGBA')
    if 'shield' in cfg:
        sc = cfg['shield']
        layers[sc['layer']] = Image.fromarray(prop_layer(shield(J, f, sc)), 'RGBA')
    flat = Image.new('RGB', (SLOT, H), pk.BG)
    for name in cfg['layers']:
        if name == 'joints':
            continue
        flat.paste(layers[name], (0, 0), layers[name])
    return layers, flat, tips


def game_size(fl):
    a = np.asarray(fl).copy()
    msk = np.all(a == np.array(pk.BG, np.uint8), axis=-1)
    a[msk] = FLOOR_RGB
    c = Image.fromarray(a).crop((0, BASE - 520, SLOT, BASE + 20))
    c = c.resize((round(c.width * SCALE), round(c.height * SCALE)), Image.BOX)
    return c.resize((c.width * 4, c.height * 4), Image.NEAREST)


def main():
    ldir = os.path.join(out, 'layers')
    os.makedirs(ldir, exist_ok=True)
    recs, flats, warns = [], [], []
    for i, f0 in enumerate(cfg['frames']):
        f = frame_cfg(f0)
        tag = f'F{i + 1} {f["name"]}'
        p, J, parts = solve(f, tag)
        warns += [f'{tag}: {m}' for m in pk.check(tag, J, B, p)]
        layers, flat, tips = frame_images(J, parts, f)
        for name in cfg['layers']:
            layers[name].save(os.path.join(ldir, f'F{i + 1}_{name}.png'))
        flats.append(flat)
        a = np.asarray(flat)
        m = np.any(a != np.array(pk.BG, np.uint8), axis=-1)
        xs, ys = np.nonzero(m.any(0))[0], np.nonzero(m.any(1))[0]
        rec = dict(frame=f['name'], ms=f['ms'], x_range=[int(xs.min()), int(xs.max())], top=int(ys.min()), lowest=int(ys.max()),
                   joints={k: [round(c, 1) for c in W2P(J[k])] for k in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF',
                                                                          'elbN', 'elbF', 'handN', 'handF', 'neck0', 'C')})
        rec['weapon_tips'] = {ln: [round(c, 1) for c in W2P(t)] for ln, t in tips.items()}
        recs.append(rec)
    strip = Image.new('RGB', (SLOT * len(flats), H), pk.BG)
    for i, fl in enumerate(flats):
        strip.paste(fl, (i * SLOT, 0))
    strip.save(os.path.join(out, f'{cfg["set"]}_strip.png'))
    small = [game_size(fl) for fl in flats]
    sheet = Image.new('RGB', (sum(s.width for s in small) + 8 * (len(small) - 1), small[0].height), (20, 20, 20))
    for i, s in enumerate(small):
        sheet.paste(s, (i * (s.width + 8), 0))
    sheet.save(os.path.join(out, f'{cfg["set"]}_game.png'))
    small[0].save(os.path.join(out, f'{cfg["set"]}_preview.gif'), save_all=True, append_images=small[1:],
                  duration=[f['ms'] for f in cfg['frames']], loop=0)
    json.dump(dict(set=cfg['set'], oy=OY, posekit_warnings=warns, frames=recs), open(os.path.join(out, 'frames.json'), 'w', encoding='utf-8'), indent=1)
    exe = os.environ.get('ASEPRITE_PATH')
    dst = os.path.abspath(os.path.join(out, cfg['set'] + '.aseprite'))
    if exe:
        if os.path.exists(dst):
            os.remove(dst)
        lua = os.path.abspath(os.path.join(out, 'build_motion_ase.lua'))
        with open(lua, 'w', encoding='utf-8') as fh:
            fh.write(LUA)
        names = ','.join(f['name'] for f in cfg['frames']) if cfg.get('frame_tags') else ''
        r = subprocess.run([exe, '-b', '--script-param', 'dir=' + os.path.abspath(ldir), '--script-param', 'out=' + dst,
                            '--script-param', 'ms=' + ','.join(str(f['ms']) for f in cfg['frames']),
                            '--script-param', 'layers=' + ','.join(cfg['layers']), '--script-param', 'tag=' + cfg.get('tag', ''),
                            '--script-param', 'names=' + names, '--script', lua], capture_output=True)
        print(('wrote ' + dst) if os.path.exists(dst) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    else:
        print('ASEPRITE_PATH not set: no .aseprite written')
    print(f'{cfg["set"]}: {len(flats)} frames, floor row {OY}, posekit warnings {len(warns)}')
    for w in warns:
        print('  ' + w)
    for r_ in recs:
        print(f'  {r_["frame"]:8s} x {r_["x_range"][0]}..{r_["x_range"][1]}  top {r_["top"]}  lowest {r_["lowest"]}  hip {r_["joints"]["hip"]}  '
              f'hands N {r_["joints"]["handN"]} F {r_["joints"]["handF"]}  tips {r_["weapon_tips"]}')


main()
