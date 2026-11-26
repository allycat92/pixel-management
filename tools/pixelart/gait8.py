#!/usr/bin/env python3
"""8-frame HEAVY and ROBE movement skeletons on the posekit mannequin (pose guides for drawing battle movement; not game art).

  python3 tools/pixelart/gait8.py OUT_DIR --style heavy|robe [--name heavy_base|robe_base] [--step HEADS]
                                  [--aseprite tools/art/ase_headless.sh] [--compare RUN_DIR]

Owner decision 2026-11-26: battle movement comes in three classes - LIGHT (the accepted run, run8.py / run_base v2), HEAVY and
ROBE: "펑퍼짐한 천 복장을 입고 뛰는것도 좀 부자연스러울거고, 중장비를 갖추면 당연히 뛰는건 물론이고 몸이 저렇게 땅에서 떨어지거나
몸을 앞으로 기울인 채로 가누기도 어려울테니까." Battle movement is still the fastest natural gait of that body (not a stroll), but:
  heavy  heavy armour / big shield: NO flight (one foot always down, both at contact), torso nearly upright (8-9 deg), knees stay
         bent (a grounded jog, not a walk: the leg never straightens at passing), the hip SINKS onto the landing leg (the weight),
         short stride, low foot clearance, arms held close (they carry the shield / weapon) and their hands drop a frame late.
  robe   long loose cloth: NO flight, upright (6-7 deg), the knees barely lift (the hem hides them), short hurried steps at a
         quick cadence, the hip nearly level (a glide), a hem (cloth_front layer) pushed by the leading leg whose edges fall back
         one frame late.
Same mannequin, canvas, floor row, joints and layer files as walk8.py / run8.py (384x1024 per frame, hip centre x=192, floor
y=870, head 110 px); the helpers are imported from walk8.py / run8.py, only the pose tables differ (those files are not changed).

Frames (tag H for heavy, G for robe - "glide"; near = the character's right leg, drawn light; far = dark). Per half cycle:
  1 contact   near foot lands FLAT ahead of the hip, the far foot is still down behind on its toe (double support)
  2 down      weight on the near foot: hip lowest (heavy: a clear sink); the far foot has just left the floor
  3 passing   near foot under the body, its knee still bent; the far foot passes LOW (heavy 2x-3x lower than a walk, robe lower still)
  4 push      near heel lifts, the near TOE stays where it was; the far foot reaches forward, low, about to land
  5-8         the same with near/far swapped.
The body travels step/4 per frame, so the TOE (front end) of a planted sole retreats by exactly step/4 per frame through the five
frames it is down (contact, down, passing, push, and as the rear foot of the next contact): `toe_shift` solves the heel-up frames.

Writes the same files as run8.py: <name>_a.png / _b.png (1x4 strips, #FF00FF), <name>_preview.gif (game size x4, nominal ms),
<name>_review.png, pose.json (gait "heavy" / "robe", step_px, run_stride_game_px, nominal_ms, per-frame measurements and the
proposed check thresholds), layers/<tag><n>_<layer>.png and, with --aseprite, <name>.aseprite (8 frames x nominal ms; robe adds a
cloth_front layer between torso and head). --compare RUN_DIR (a run8.py output, e.g. art/requests/guides/run_base/v2) also writes
<name>_vs_run.gif: the light run and this set side by side at game size x4, each at its own nominal ms, in place (top) and
travelling over the floor by step/4 per frame (bottom - a planted foot that slides shows here).
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run8  # noqa: E402
import walk8 as w8  # noqa: E402
from walk8 import BASELINE, HEAD_PX, JOINTS, SCALE, SH_, SLOT, SW_, pk  # noqa: E402

FLOOR = run8.FLOOR

# ---------------------------------------------------------------------------------------------------------------- pose tables
# per half cycle: index 0 contact, 1 down, 2 passing, 3 push   (head units; x forward of the hip centre, h above the floor)
# arms: (upper-arm deg from straight down, + = forward; elbow flex deg) - angles in the picture (walk8.swing_arms).
# *_ST = the arm on the side of the stance leg, *_SW = the arm of the other side; ARM_* near arm, FAR_* far arm.
# The arms lag the legs by one frame (extremes at `down`, crossing between passing and push).
GAME_SPEED = 58.0      # unit speed in battle (canvas = game px per second at 1x speed; warrior-class units, measured)
# The game plays drawn heavy / robe cells PLANTED: one step = the drawn stride (shorter than the code stride), so the body moves
# stride/4 per cell and a cell lasts stride/4 / GAME_SPEED seconds (js/battle.js gaitUpdate r.rp). `game_ms` is that time; the
# drafts are timed and tuned at it (a slower unit or a 1.5x boss sheet stretches every cell by the same factor).


def game_ms(step):
    """ms per cell in the game at GAME_SPEED for a stride of `step` heads (rounded to whole ms)"""
    return round(step * HEAD_PX * SCALE / 4 / GAME_SPEED * 1000)


STYLES = {
    'heavy': dict(
        tag='H', name='heavy_base', step=1.29,                   # 141.9 px = 23.5 game px per step -> 101 ms a cell in the game (8 cells 808 ms, 149 steps a minute)
        HIP=[1.60, 1.535, 1.58, 1.595],                          # the weight drops ONLY at down (-7 px), then the hip comes back up slowly; the push is never above contact: bob 7 px
        LEAN=[0.05, 0.06, 0.05, 0.045],                          # measured 4.7-5.6 deg (hip -> neck dot): the armour keeps the body upright - 5 deg (4-6)
        TILT=[-0.02, -0.025, -0.02, -0.015],                     # the head stays level
        SHW=[1.02, 1.03, 1.0, 0.99],
        CONTACT=0.42,                                            # ankle of the landing foot ahead of the hip (46 px): short reach, mid-stance under the hip
        LAND=0, PUSH=12, REAR=24,                                # foot angles (deg, + = heel up): lands flat (a stomp), push heel lift, rear foot at contact
        # the other leg after contact: ankle x, ankle h, foot angle (deg; + = toe down) - shuffled low, the boot barely clears the floor
        SWING=[(-0.56, 0.34, 34), (-0.04, 0.27, 12), (0.33, 0.165, -4)],
        # arms held close and HIGH as if a shield is carried in front (far arm, forearm across the front) and a weapon at the side
        # (near arm, hand at the belt, forearm forward): they ride with the body, swing only +-4-6 deg, the elbows fold a little
        # more at down (the hands sink with the weight)
        ARM_ST=[(-6, 70), (-5, 64), (-2, 68), (2, 72)],
        ARM_SW=[(4, 70), (5, 64), (2, 68), (-4, 72)],
        FAR_ST=[(-2, 104), (-1, 98), (2, 102), (4, 104)],       # the far (shield) arm: elbow at the side, forearm across the front, rising a little
        FAR_SW=[(5, 104), (4, 98), (1, 102), (-2, 104)],
        robe=False,
    ),
    'robe': dict(
        tag='G', name='robe_base', step=1.22,                    # 134.2 px = 22.2 game px per step -> 96 ms a cell in the game (8 cells 768 ms, 156 steps a minute)
        HIP=[1.62, 1.605, 1.645, 1.65],                          # nearly level (5 px): a glide, lowest at down, highest passing / push
        LEAN=[0.085, 0.095, 0.08, 0.08],                         # measured 6.6-7.5 deg (hip -> neck dot): a small hurrying lean - 7 deg (5-8)
        TILT=[-0.035, -0.04, -0.03, -0.03],
        SHW=[1.04, 1.05, 0.98, 0.99],
        CONTACT=0.46,
        LAND=0, PUSH=12, REAR=24,
        SWING=[(-0.58, 0.31, 28), (-0.04, 0.22, 8), (0.34, 0.165, -6)],   # the foot barely leaves the floor: knees hidden, only the toes show
        # arms close: the hands stay near the waist (a staff / the hem held), elbows folded 70-78 deg, swing +-6-12 deg
        ARM_ST=[(-10, 72), (-12, 76), (-4, 74), (6, 72)],
        ARM_SW=[(8, 72), (10, 76), (4, 74), (-8, 72)],
        FAR_ST=[(-16, 72), (-18, 76), (-10, 74), (-2, 72)],
        FAR_SW=[(2, 72), (4, 76), (-4, 74), (-12, 72)],
        robe=True,
    ),
}
PHASES = ('contact', 'down', 'passing', 'push')

# robe hem (cloth_front): one length of cloth hanging from the waist; its bottom is HEM_LEN below the hip of the PREVIOUS frame
# (the cloth falls a frame late), and its front / back edges are pushed out by the legs at once but fall back a frame late.
HEM_LEN = 1.245                    # hip -> hem bottom (heads): the hem stays 40-46 px above the floor (SPEC 7: 38 or more, toes visible)
HEM_REST = (0.44, -0.50)           # front / back edge of the hanging hem when nothing pushes it (heads from the hip centre)
HEM_CLEAR = 0.20                   # cloth outside a shin / knee centre line (the limb radius is 0.12-0.155)
pk.PAL.setdefault('robe', ((124, 92, 146), (92, 66, 112)))
LAYERS_ROBE = w8.LAYERS[:4] + (('cloth_front', ('robe',)),) + w8.LAYERS[4:]     # SPEC section 4: torso < cloth_front < head


def tables(S, step, dx):
    """stance-leg and other-leg tables (ankle x, ankle h, foot angle) for a step of `step` heads. dx = {'push', 'rear'}: ankle x
    corrections of the heel-up frames (see `toe_shift`). The planted heights are starting values: `planted` settles them"""
    d = step / 4
    a = pk.Body(4.0).ank
    C = S['CONTACT']
    stance = [(C, a, S['LAND']), (C - d, a, 0), (C - 2 * d, a, 0), (C - 3 * d + run8.roll(S['PUSH']) + dx.get('push', 0.0), 0.2, S['PUSH'])]
    other = [(C - 4 * d + run8.roll(S['REAR']) + dx.get('rear', 0.0), 0.25, S['REAR'])] + list(S['SWING'])
    return stance, other


def pose(S, i, B, step, lift=(0.0, 0.0), dx=None):
    k, near_stance = i % 4, i < 4
    stance, other = tables(S, step, dx or {})
    st, ot = stance[k], other[k]
    st = (st[0], st[1] + lift[0], st[2])
    ot = (ot[0], ot[1] + (lift[1] if k == 0 else 0.0), ot[2])
    p = dict(hip=(0.0, S['HIP'][k]), lean=S['LEAN'][k], tilt=S['TILT'][k], hipw=0.05, kneeN=(1.0, 0.0), kneeF=(1.0, 0.0))
    sn, sf = (st, ot) if near_stance else (ot, st)
    p.update(footN=(sn[0], sn[1]), faN=sn[2], toeN=0.9, footF=(sf[0], sf[1]), faF=sf[2])
    p['sw'] = S['SHW'][k] if near_stance else 2 - S['SHW'][k]
    w8.swing_arms(p, B, {'N': S['ARM_ST'][k] if near_stance else S['ARM_SW'][k], 'F': S['FAR_SW'][k] if near_stance else S['FAR_ST'][k]})
    p['z'] = {'farfore': 'back'}
    return p


def planted(S, i, B, step, oy, dx=None):
    """pose i on the one floor: the stance ankle (at contact: both ankles) settled until that leg's lowest pixel is on y=870"""
    k, near_stance = i % 4, i < 4
    sides = ('N', 'F') if near_stance else ('F', 'N')
    return w8.settle(lambda lift: pose(S, i, B, step, lift, dx), B, oy, sides, 2 if k == 0 else 1, f'{S["tag"]}{i + 1}')


def toe_shift(S, B, step, oy):
    """ankle x corrections (heads) of the two heel-up frames: the push frame (stance heel up) and the rear foot of the next
    contact (heel up further). In both the toe as drawn must be exactly step/4 per frame behind the toe of the flat `down` frame
    (2 / 3 frames later), or the foot slides while the game moves the body step/4 per frame. Solved per leg from the picture,
    then averaged so the two halves keep the same ankle x (the feet are drawn 10% different in size)"""
    out = {}
    d = step / 4 * HEAD_PX
    for kind, frames, n in (('push', ((3, 1, 'N'), (7, 5, 'F')), 2), ('rear', ((4, 1, 'N'), (0, 5, 'F')), 3)):
        vals = []
        for i, ref, side in frames:
            target = run8.toe_px(planted(S, ref, B, step, oy)[2], side, oy) - n * d
            x, best = 0.0, None
            for it in range(20):
                err = run8.toe_px(planted(S, i, B, step, oy, {kind: x})[2], side, oy) - target
                if best is None or abs(err) < abs(best[1]):
                    best = (x, err)
                if abs(err) <= 0.75:
                    break
                x -= err / HEAD_PX * (1.0 if it < 4 else 0.4)          # damped: a whole pixel can overshoot
            if abs(best[1]) > 1.0:
                raise AssertionError(f'{S["tag"]}{i + 1}: the toe does not settle ({best[1]} px)')
            vals.append(best[0])
        out[kind] = sum(vals) / 2
    return out


# ---------------------------------------------------------------------------------------------------------------- robe hem
def _x_at(a, b, h):
    """x of the segment a-b (world points, y-down) at height h above the floor, clamped to the segment"""
    ya, yb = -a[1], -b[1]
    if abs(ya - yb) < 1e-6:
        return float(a[0])
    t = min(1.0, max(0.0, (ya - h) / (ya - yb)))
    return float(a[0] + (b[0] - a[0]) * t)


def hem_need(J, hb):
    """how far the legs push the cloth out in this frame: (front, back) at the hem bottom height hb and (front, back) at the
    knees, in heads from the hip centre"""
    hx = float(J['hip'][0])
    bot = [_x_at(J['knee' + s], J['ank' + s], hb) - hx for s in 'NF']
    kn = [float(J['knee' + s][0]) - hx for s in 'NF']
    return (max(HEM_REST[0], max(bot) + HEM_CLEAR), min(HEM_REST[1], min(bot) - HEM_CLEAR),
            max(HEM_REST[0] - 0.04, max(kn) + HEM_CLEAR + 0.04), min(HEM_REST[1] + 0.04, min(kn) - HEM_CLEAR - 0.04))


def hem_parts(J, need, prev_need, hb):
    """the hem polygon: pushed out at once by this frame's legs, falling back a frame late (prev_need)"""
    L = J['L']
    hx = float(J['hip'][0])
    f_bot, b_bot = max(need[0], prev_need[0]), min(need[1], prev_need[1])
    f_kn, b_kn = max(need[2], prev_need[2]), min(need[3], prev_need[3])
    hk = hb + 0.50                                                       # the knee-level side points
    # the bottom corners rise when the cloth is pushed out (a shin lifting the hem); the middle of the hem hangs lowest
    rf = 0.30 * max(0.0, f_bot - HEM_REST[0])
    rb = 0.30 * max(0.0, HEM_REST[1] - b_bot)
    pts = [L(-0.43, 0.15), L(-0.47, -0.12),
           pk.P(hx + b_kn, hk), pk.P(hx + b_bot, hb + 0.03 + rb), pk.P(hx + 0.5 * b_bot, hb - 0.01),
           pk.P(hx + 0.5 * f_bot, hb - 0.01), pk.P(hx + f_bot, hb + 0.04 + rf), pk.P(hx + f_kn, hk),
           L(0.45, -0.12), L(0.41, 0.15)]
    shape = pk.poly(pts)
    J['hem'] = dict(front=f_bot, back=b_bot, bottom_h=hb, front_lift=rf, back_lift=rb)
    return [('robe', shape, 'robe', 45, 0.12)]


def solve_all(S, B, step, oy, dx):
    solved = [planted(S, i, B, step, oy, dx) for i in range(8)]
    if not S['robe']:
        return solved
    hbs = [S['HIP'][(i - 1) % 4] - HEM_LEN for i in range(8)]           # the cloth's height follows the hip a frame late
    needs = [hem_need(J, hbs[i]) for i, (_, J, _) in enumerate(solved)]
    out = []
    for i, (p, J, parts) in enumerate(solved):
        cloth = hem_parts(J, needs[i], needs[(i - 1) % 8], hbs[i])
        out.append((p, J, sorted(parts + cloth, key=lambda q: q[3])))
    return out


# ---------------------------------------------------------------------------------------------------------------- export
LUA = r'''
local p = app.params
local dir, out = p.dir, p.out
local n = tonumber(p.frames) or 8
local ms = tonumber(p.ms) or 120
local names = {}
for nm in string.gmatch(p.layers, "[^,]+") do names[#names + 1] = nm end
local first = Image{ fromFile = dir .. "/F1_torso.png" }
local spr = Sprite(first.width, first.height, ColorMode.RGB)
local bg = spr.layers[1]
bg.name = "Background"
for f = 2, n do spr:newEmptyFrame(f) end
for f = 1, n do
  local img = Image(spr.width, spr.height, ColorMode.RGB)
  img:clear(Color{ r = 255, g = 0, b = 255, a = 255 })
  spr:newCel(bg, f, img, Point(0, 0))
  spr.frames[f].duration = ms / 1000.0
end
for _, name in ipairs(names) do
  local l = spr:newLayer()
  l.name = name
  for f = 1, n do
    spr:newCel(l, f, Image{ fromFile = dir .. "/F" .. f .. "_" .. name .. ".png" }, Point(0, 0))
  end
  if name == "joints" then l.isVisible = false end
end
spr:saveAs(out)
'''


def frame_layers(parts, J, oy, layers):
    """walk8.frame_layers with a layer list (the robe adds cloth_front)"""
    full = w8.draw(parts, None, oy)
    out = {}
    for name, sel in layers:
        rgb = w8.draw(parts, set(sel), oy)
        a = np.any(rgb != np.array(pk.BG, np.uint8), axis=-1)
        out[name] = Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), 'RGBA')
    jl = np.zeros((SH_, SLOT, 4), np.uint8)
    for _, key, col in JOINTS:
        x, y = int(round(SLOT / 2 + J[key][0] * HEAD_PX)), int(round(oy + J[key][1] * HEAD_PX))
        jl[y - 1:y + 2, x - 1:x + 2] = (*col, 255)
    out['joints'] = Image.fromarray(jl, 'RGBA')
    return out, Image.fromarray(full, 'RGB')


def game_cell(flat, pad=28):
    """one frame at game size (BOX), the battle floor colour behind it, the floor drawn just under the soles"""
    a = np.asarray(flat).copy()
    m = np.all(a == np.array(pk.BG, np.uint8), axis=-1)
    a[m] = FLOOR
    cell = Image.fromarray(a, 'RGB').crop((0, BASELINE - 500, SLOT, BASELINE + pad))
    return cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX)


def export(out, name, tag, solved, oy, layers, ms, aseprite):
    ldir = os.path.join(out, 'layers')
    os.makedirs(ldir, exist_ok=True)
    strips = [np.full((SH_, SW_, 3), pk.BG, np.uint8) for _ in range(2)]
    flats = []
    for i, (p, J, parts) in enumerate(solved):
        lay, flat = frame_layers(parts, J, oy, layers)
        flats.append(flat)
        for ln, im in lay.items():
            im.save(os.path.join(ldir, f'{tag}{i + 1}_{ln}.png'))
        mask = np.any(np.asarray(flat) != np.array(pk.BG, np.uint8), axis=-1)
        xs = np.nonzero(mask.any(0))[0]
        assert xs.min() >= 32 and xs.max() <= SLOT - 33, (f'{tag}{i + 1}', xs.min(), xs.max())   # the strip's 32 px magenta border
        strips[i // 4][:, (i % 4) * SLOT:(i % 4 + 1) * SLOT] = np.asarray(flat)
    for k, s in enumerate('ab'):
        Image.fromarray(strips[k], 'RGB').save(os.path.join(out, f'{name}_{s}.png'))
    small = []
    for f in flats:
        cell = f.crop((0, BASELINE - 500, SLOT, BASELINE + 12))
        cell = cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX)
        small.append(cell.resize((cell.width * 4, cell.height * 4), Image.NEAREST))
    small[0].save(os.path.join(out, f'{name}_preview.gif'), save_all=True, append_images=small[1:], duration=ms, loop=0, disposal=1)
    if aseprite:
        dst = os.path.abspath(os.path.join(out, name + '.aseprite'))
        with tempfile.TemporaryDirectory(prefix='gait8-ase-') as tmp:
            for fn in os.listdir(ldir):
                if fn.startswith(tag) and fn.endswith('.png'):
                    os.symlink(os.path.abspath(os.path.join(ldir, fn)), os.path.join(tmp, 'F' + fn[len(tag):]))
            lua = os.path.join(tmp, 'build.lua')
            with open(lua, 'w') as f:
                f.write(LUA)
            names = [ln for ln, _ in layers] + ['joints']
            r = subprocess.run([aseprite, '-b', '--script-param', 'dir=' + tmp, '--script-param', 'out=' + dst, '--script-param', 'frames=8',
                                '--script-param', f'ms={ms}', '--script-param', 'layers=' + ','.join(names), '--script', lua], capture_output=True)
        print(('wrote ' + dst) if os.path.exists(dst) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    return flats


def compare(path, sets, travel_w=200):
    """the comparison GIF: per set a column at game size (x4 nearest) in place, and below all of them one lane each travelling
    over a ticked floor by step/4 per frame. Each set runs at its own nominal ms on one timeline (10 ms ticks); the loop is the
    least common multiple of the cycles when that is under 8 s"""
    cells = [[game_cell(f) for f in flats] for _, flats, _, _ in sets]
    cw, ch = cells[0][0].size
    cycles = [8 * ms for _, _, ms, _ in sets]
    total = 1
    for c in cycles:
        total = total * c // math.gcd(total, c)
    total = total if total <= 8000 else max(cycles) * 4
    top_w = (cw + 40) * len(sets)
    W = max(top_w, travel_w)
    lane_h = ch + 2
    H = 12 + ch + 4 + len(sets) * (lane_h + 10)
    out, prev, durs = [], None, []
    for t in range(0, total, 10):
        img = Image.new('RGB', (W, H), FLOOR)
        d = ImageDraw.Draw(img)
        for k, (lab, _, ms, step) in enumerate(sets):
            n = t // ms
            x0 = k * (cw + 40) + (W - top_w) // 2 + 20
            img.paste(cells[k][n % 8], (x0, 12))
            d.text((x0 - 12, 1), lab, fill=(225, 225, 205))
        for k, (lab, _, ms, step) in enumerate(sets):
            n = t // ms
            y = 12 + ch + 4 + k * (lane_h + 10)
            dpx = step / 4 * SCALE
            span = W - cw
            x = (n * dpx) % span
            img.paste(cells[k][n % 8], (int(math.floor(x)), y))
            fy = y + ch - 28 * SCALE                                     # the floor row (y=870) inside the cell
            for tx in range(0, W, 8):
                d.point((tx, int(fy) + 1), fill=(120, 140, 110))
        big = img.resize((W * 4, H * 4), Image.NEAREST)
        key = big.tobytes()
        if key == prev:
            durs[-1] += 10
        else:
            out.append(big)
            durs.append(10)
            prev = key
    pal = out[0].quantize(colors=64, method=Image.Quantize.MEDIANCUT)      # one palette (the mannequin has few colours): ~half the size
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in out]
    out[0].save(path, save_all=True, append_images=out[1:], duration=durs, loop=0, optimize=True)
    return total


def flats_of(run_dir, name='run_base'):
    """the 8 frames of a run8.py output folder (two 1x4 strips)"""
    fr = []
    for s in 'ab':
        im = Image.open(os.path.join(run_dir, f'{name}_{s}.png')).convert('RGB')
        fr += [im.crop((k * SLOT, 0, (k + 1) * SLOT, SH_)) for k in range(4)]
    return fr


# ---------------------------------------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('--style', choices=sorted(STYLES), required=True)
    ap.add_argument('--name')
    ap.add_argument('--step', type=float, help='step length in heads (footfall to footfall = body travel per step)')
    ap.add_argument('--aseprite', help='Aseprite executable (e.g. tools/art/ase_headless.sh): also build <name>.aseprite')
    ap.add_argument('--compare', help='a run8.py output folder (e.g. art/requests/guides/run_base/v2): also write <name>_vs_run.gif')
    a = ap.parse_args(argv)
    S = STYLES[a.style]
    name, step, tag = a.name or S['name'], a.step or S['step'], S['tag']
    ms = game_ms(step)
    os.makedirs(a.out, exist_ok=True)
    B = pk.Body(4.0)
    oy = w8.floor_row(B, 1.30)                     # the walk / run floor row: every set stands on the same canvas line
    dx = toe_shift(S, B, step, oy)
    solved = solve_all(S, B, step, oy, dx)
    layers = LAYERS_ROBE if S['robe'] else w8.LAYERS
    warns = [f'{tag}{i + 1}: {m}' for i, (p, J, _) in enumerate(solved) for m in pk.check(f'{tag}{i + 1}', J, B, p)]
    flats = export(a.out, name, tag, solved, oy, layers, ms, a.aseprite)
    key = np.array(pk.BG, np.uint8)
    frames = []
    for i, ((p, J, parts), flat) in enumerate(zip(solved, flats)):
        k, st = i % 4, ('N' if i < 4 else 'F')
        ot = 'F' if st == 'N' else 'N'
        sole = {s: w8.lowest(w8.draw(parts, w8.LEGS[s], oy)) for s in 'NF'}
        mask = np.any(np.asarray(flat) != key, axis=-1)

        def px(v):
            return [round(float(SLOT / 2 + v[0] * HEAD_PX), 1), round(float(oy + v[1] * HEAD_PX), 1)]
        fr = dict(frame=f'{tag}{i + 1}', strip='ab'[i // 4], slot=k + 1, phase=PHASES[k], stance='near' if st == 'N' else 'far',
                  feet_down=['near', 'far'] if k == 0 else ['near' if st == 'N' else 'far'],
                  hip_height_px=round(S['HIP'][k] * HEAD_PX, 1), lowest_px=w8.lowest(np.asarray(flat)),
                  sole_px=sole, other_sole_height_px=BASELINE - sole[ot],
                  toe_x_px={'stance': run8.toe_px(parts, st, oy), 'rear': run8.toe_px(parts, ot, oy) if k == 0 else None},
                  ankle_x_px={s: round(float(J['ank' + s][0] * HEAD_PX), 1) for s in 'NF'},
                  knee_flex_deg={s: round(run8.angle_deg(J['H' + s], J['knee' + s], J['ank' + s]), 1) for s in 'NF'},
                  elbow_flex_deg={s: round(run8.angle_deg(J['S' + s], J['elb' + s], J['hand' + s]), 1) for s in 'NF'},
                  lean_deg=round(math.degrees(math.atan2(J['neck0'][0] - J['hip'][0], J['hip'][1] - J['neck0'][1])), 1),
                  neck_x_px=round(float(J['neck0'][0] * HEAD_PX), 1),
                  hand_from_shoulder_px={s: round(float((J['hand' + s][0] - J['S' + s][0]) * HEAD_PX), 1) for s in 'NF'},
                  hand_h_px={s: round(float(-J['hand' + s][1] * HEAD_PX), 1) for s in 'NF'},
                  top_px=int(np.nonzero(mask.any(1))[0].min()),
                  joints={kk: px(J[kk]) for kk in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF', 'elbN', 'elbF', 'handN', 'handF', 'neck0')})
        if 'hem' in J:
            h = J['hem']
            fr['hem'] = dict(bottom_above_floor_px=round(h['bottom_h'] * HEAD_PX, 1), front_x_px=round(h['front'] * HEAD_PX, 1),
                             back_x_px=round(h['back'] * HEAD_PX, 1), front_lift_px=round(h['front_lift'] * HEAD_PX, 1),
                             back_lift_px=round(h['back_lift'] * HEAD_PX, 1))
        frames.append(fr)
    strips = [Image.open(os.path.join(a.out, f'{name}_{s}.png')) for s in 'ab']
    run8.review(flats, strips, os.path.join(a.out, f'{name}_review.png'))
    hips = [f['hip_height_px'] for f in frames]
    st_toes = []
    for half, side in ((0, 'N'), (4, 'F')):
        seq = [frames[half + k]['toe_x_px']['stance'] for k in range(4)] + [frames[(half + 4) % 8]['toe_x_px']['rear']]
        st_toes.append(dict(leg='near' if side == 'N' else 'far', toe_x_px=seq,
                            retreat_px=[round(seq[j] - seq[j + 1], 1) for j in range(4)]))
    leans = [f['lean_deg'] for f in frames]
    info = dict(set=name, gait=a.style, movement_class=a.style, head_px=HEAD_PX, baseline=BASELINE, scale=SCALE, frames_per_cycle=8,
                nominal_ms=ms, game_ms_basis=f'stride/4 per cell at {GAME_SPEED:g} game px/s (unit speed at 1x; the game plays heavy / robe cells planted)',
                step_px=round(step * HEAD_PX, 1), run_stride_game_px=round(step * HEAD_PX * SCALE, 1),
                speed_at_nominal_ms_game_px_s=round(step * HEAD_PX * SCALE / (4 * ms / 1000), 1),
                steps_per_minute=round(60000 / (4 * ms), 1),
                bob_px=round(max(hips) - min(hips), 1), sink_contact_to_down_px=round(hips[0] - hips[1], 1),
                lean_deg=[min(leans), max(leans)], planted_toes=st_toes,
                other_foot_max_px=max(f['other_sole_height_px'] for f in frames if f['phase'] != 'contact'),
                heel_up_ankle_shift_px={k: round(v * HEAD_PX, 1) for k, v in dx.items()},
                bones_px=w8.bones_px(B), posekit_warnings=warns, frames=frames)
    with open(os.path.join(a.out, 'pose.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
        f.write('\n')
    if a.compare:
        lms = game_ms(run8.STEP)                   # the light run planted the same way (owner's option B: unit speed kept, cadence from the drawn stride)
        total = compare(os.path.join(a.out, f'{name}_vs_run.gif'),
                        [(f'light {lms}', flats_of(a.compare), lms, run8.STEP * HEAD_PX), (f'{a.style} {ms}', flats, ms, step * HEAD_PX)])
        print(f'compare gif loop {total} ms')
    print(f'{name}: step {info["step_px"]} px ({info["run_stride_game_px"]} game px), bob {info["bob_px"]} px '
          f'(sink {info["sink_contact_to_down_px"]}), lean {info["lean_deg"][0]}-{info["lean_deg"][1]} deg, {ms} ms/frame, '
          f'posekit warnings {len(warns)} -> {a.out}')
    for w in warns:
        print('  ' + w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
