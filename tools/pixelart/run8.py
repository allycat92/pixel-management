#!/usr/bin/env python3
"""8-frame run skeleton on the posekit mannequin (pose guide for drawing run frames; not game art).

  python3 tools/pixelart/run8.py OUT_DIR [--name run_base] [--step 2.50] [--aseprite tools/art/ase_headless.sh]

Owner decision 2026-11-26: in battle the units RUN; the walk set (walk8.py) stays as a reference and for slowed units.
Same mannequin, canvas and floor as walk8.py (384x1024 per frame, hip centre x=192, ONE floor row, head 110 px, hard edges,
facing right); the helpers are imported from walk8.py, only the pose tables differ.

Writes OUT_DIR/<name>_a.png (R1-R4) and <name>_b.png (R5-R8): 1536x1024, #FF00FF, 1x4; <name>_preview.gif (game scale 0.1654,
x4 nearest, 80 ms); <name>_review.png (strips reduced + the 8 frames at game size on the battle floor colour, x3);
pose.json (gait "run", joints per frame, measurements); layers/R<n>_<layer>.png and, with --aseprite EXE, <name>.aseprite
(8 frames x 80 ms, part layers + hidden joints layer) - measured afterwards by tools/art/check_skeleton.py (run mode).

Frames (near = the character's right leg, drawn light; far = dark). ONE foot at most is on the floor:
  R1 contact   near foot lands flat a little ahead of the body, knee bent; the far leg trails folded, heel up
  R2 down      compression: hip lowest, weight over the near foot; the far knee passes under the body; arms cross
  R3 push-off  near leg extended behind on the toe, heel up, body rising; the far knee drives forward; arm extremes begin
  R4 flight    BOTH feet off the floor, hip highest, legs scissored (far leg reaching forward, near leg trailing)
  R5-R8 the same with near/far swapped.
The body travels step/4 per frame, so the planted TOE retreats by step/4 per stance frame (R1 -> R2 -> R3); the ankle of R3 is
further forward than that because the foot has rolled onto the toe (`roll`). step = distance between two footfalls = the game's
runStride (game px per step) once multiplied by the scale.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import walk8 as w8  # noqa: E402
from walk8 import BASELINE, HEAD_PX, SCALE, SLOT, pk  # noqa: E402

MS = 80                                         # per frame: 8 x 80 = 640 ms a cycle, 187 steps a minute
STEP = 2.50                                     # heads between two footfalls (275 px = 45.5 game px)
FLOOR = (46, 58, 46)                            # battle floor colour of the review image
SOLE_BAND = 4                                   # rows above the floor line in which the front end of the planted sole is measured

# per half cycle: index 0 contact, 1 down, 2 push-off, 3 flight   (head units; x forward, h above the floor)
# 2026-11-26: tables below = the PC Aseprite session's refinement (art-inbox 14c9788, then eca075a after the owner asked for a slightly
# forward-leaning run with less bounce); re-baking reproduces the delivery pixel for pixel
HIP = [1.60, 1.575, 1.775, 1.785]                 # hip joint height: lowest at down, highest in flight (bob ~0.21 heads = about 5% of the height, owner 2026-11-26)
LEAN = [0.35, 0.37, 0.35, 0.33]                # torso lean forward (rad) - the walk has 0.10-0.15
TILT = [-0.11, -0.11, -0.11, -0.09]            # head tilt (rad): the head stays level while the torso leans
SHW = [1.06, 1.00, 0.95, 0.94]                 # shoulder width factor while the near leg is the stance leg (mirrored for the far half)
# arms: (upper-arm deg from straight down, + = forward; elbow flex deg), elbows near 90 deg all the way round.
# Opposite to the legs: the stance leg goes back from contact to flight while the arm of that side comes forward; the extremes
# are at push-off/flight. *_ST = the arm on the side of the stance leg, *_SW = the arm of the other side.
ARM_ST = [(-36, 84), (2, 94), (19, 107), (21, 110)]            # near arm
ARM_SW = [(8, 104), (-32, 88), (-54, 82), (-58, 80)]
# The far shoulder is drawn 0.7 heads ahead of the near one: with the near arm's forward swing the far hand would leave the
# 384 px frame (the strip needs 32 px of magenta at its right border) and the forearm would stick out in front of the chest in
# five frames of eight. So the far arm swings further back, and going forward its upper arm stops at the vertical while the
# elbow folds more (the fist comes up in front of the chest).
FAR_ST = [(-50, 82), (-8, 100), (11, 119), (14, 119)]
FAR_SW = [(-4, 110), (-44, 92), (-62, 84), (-66, 80)]
CONTACT = 0.5636                                  # ankle x of the landing foot ahead of the hip (heads)
PUSH = 40                                       # heel lift at push-off (deg)
# the leg that is not on the floor: ankle x, ankle h, foot angle (deg; + = toe down)
SWING = [(-0.85, 1.24, 135), (-0.57, 1.31, 140), (0.16, 0.70, 15)]
FLIGHT = ((-0.98, 0.80, 75), (0.92, 0.52, -18))  # R4: the leg that just pushed off (trailing) / the leg reaching for the next contact


def roll(fa):
    """how far the ankle moves forward when a planted foot turns onto its toe by fa degrees (the front of the sole stays put).
    0.95 = mean foot size of the two legs (near 0.9, far 1.0). A starting value: `push_shift` corrects it from the picture"""
    a = math.radians(fa)
    return 0.95 * (0.38 * (1 - math.cos(a)) + 0.09 * math.sin(a))


def tables(step, dx=0.0):
    """stance-leg and other-leg ankle tables for a step of `step` heads (footfall to footfall); dx = see `push_shift`"""
    d = step / 4
    a = pk.Body(4.0).ank
    # ankle x, ankle h, foot angle. The heights of the planted foot are starting values: `planted` settles them on the floor
    stance = [(CONTACT, a, 0), (CONTACT - d, a, 0), (CONTACT - 2 * d + roll(PUSH) + dx, 0.31, PUSH), FLIGHT[0]]
    other = SWING + [FLIGHT[1]]
    return stance, other


def pose(i, B, step, lift=(0.0, 0.0), dx=0.0):
    """pose table for frame i; lift = extra ankle height (heads) of the stance leg (see `planted`), dx = see `push_shift`"""
    k, near_stance = i % 4, i < 4
    stance, other = tables(step, dx)
    st, sw = stance[k], other[k]
    st = (st[0], st[1] + lift[0], st[2])
    p = dict(hip=(0.0, HIP[k]), lean=LEAN[k], tilt=TILT[k], hipw=0.05, kneeN=(1.0, 0.0), kneeF=(1.0, 0.0))
    sn, sf = (st, sw) if near_stance else (sw, st)
    p.update(footN=(sn[0], sn[1]), faN=sn[2], toeN=0.9, footF=(sf[0], sf[1]), faF=sf[2])
    p['sw'] = SHW[k] if near_stance else 2 - SHW[k]
    w8.swing_arms(p, B, {'N': ARM_ST[k] if near_stance else ARM_SW[k], 'F': FAR_SW[k] if near_stance else FAR_ST[k]})
    p['z'] = {'farfore': 'back'}
    return p


def planted(i, B, step, oy, dx=0.0):
    """pose i on the one floor: in R1-R3 / R5-R7 the stance ankle is settled until that leg's lowest pixel is on the baseline;
    the flight frames (R4, R8) touch nothing"""
    k, near_stance = i % 4, i < 4
    sides = ('N', 'F') if near_stance else ('F', 'N')
    return w8.settle(lambda lift: pose(i, B, step, lift, dx), B, oy, sides, 0 if k == 3 else 1, f'R{i + 1}')


def toe_px(parts, side, oy):
    """the front end of a planted sole: the foremost pixel of that leg within SOLE_BAND rows of the floor, in px ahead of the
    hip centre (tools/art/check_skeleton.py measures the same thing from the leg layer)"""
    rgb = w8.draw(parts, w8.LEGS[side], oy)
    band = np.any(rgb[BASELINE - SOLE_BAND:BASELINE + 1] != np.array(pk.BG, np.uint8), axis=-1)
    return float(np.nonzero(band.any(0))[0].max()) - SLOT / 2


def push_shift(B, step, oy):
    """ankle x correction (heads) of the push-off frames R3 / R7: the toe as drawn must be step/4 behind the toe of the down
    frame, or the foot slides when the game moves the body step/4 per frame. Solved per leg from the picture, then averaged, so
    the two halves keep the same ankle x (the feet are drawn 10% different in size: each toe ends within 1 px of its target)"""
    out = []
    for i in (2, 6):
        side = 'N' if i < 4 else 'F'
        target = toe_px(planted(i - 1, B, step, oy)[2], side, oy) - step / 4 * HEAD_PX
        dx = 0.0
        for _ in range(12):
            err = toe_px(planted(i, B, step, oy, dx)[2], side, oy) - target
            if abs(err) <= 0.75:
                break
            dx -= err / HEAD_PX
        else:
            raise AssertionError(f'R{i + 1}: the toe does not settle ({err} px)')
        out.append(dx)
    return sum(out) / 2


def angle_deg(a, b, c):
    """flex at b of the chain a-b-c (0 = straight)"""
    u, v = np.asarray(a, float) - np.asarray(b, float), np.asarray(c, float) - np.asarray(b, float)
    cs = float(u @ v) / (float(np.linalg.norm(u)) * float(np.linalg.norm(v)) or 1.0)
    return 180 - math.degrees(math.acos(max(-1.0, min(1.0, cs))))


def review(flats, strips, path):
    """the two strips at half size + the 8 frames at game size on the battle floor colour (x3) with the floor line drawn"""
    key = np.array(pk.BG, np.uint8)
    cells = []
    for f in flats:
        a = np.asarray(f).copy()
        m = np.all(a == key, axis=-1)
        a[m] = FLOOR
        a[BASELINE + 1:BASELINE + 4][m[BASELINE + 1:BASELINE + 4]] = (70, 86, 66)       # the floor, just under the soles
        cell = Image.fromarray(a, 'RGB').crop((0, BASELINE - 500, SLOT, BASELINE + 28))
        cell = cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX)
        cells.append(cell.resize((cell.width * 3, cell.height * 3), Image.NEAREST))
    cw, ch = cells[0].size
    small = [s.crop((0, 380, s.width, 900)).resize((s.width // 2, 260), Image.BOX) for s in strips]
    W = max(small[0].width * 2 + 4, cw * 8)
    out = Image.new('RGB', (W, small[0].height + ch + 8), (24, 24, 24))
    for k, s in enumerate(small):
        out.paste(s, (k * (s.width + 4), 0))
    for k, c in enumerate(cells):
        out.paste(c, ((W - cw * 8) // 2 + k * cw, small[0].height + 8))
    out.save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('--name', default='run_base')
    ap.add_argument('--step', type=float, default=STEP, help=f'step length in heads (footfall to footfall; {STEP} = {STEP * HEAD_PX:.0f} px)')
    ap.add_argument('--aseprite', help='Aseprite executable (e.g. tools/art/ase_headless.sh): also build <name>.aseprite - 8 frames, part layers, hidden joints layer')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    B = pk.Body(4.0)
    oy = w8.floor_row(B, 1.30)                   # the walk set's floor row: both sets stand on the same canvas line
    dx = push_shift(B, a.step, oy)
    solved = [planted(i, B, a.step, oy, dx) for i in range(8)]
    frames, warns, flats = w8.export_set(a.out, a.name, solved, B, oy, [HIP[i % 4] for i in range(8)], MS, a.aseprite, tag='R')
    key = np.array(pk.BG, np.uint8)
    for i, (fr, (p, J, parts), flat) in enumerate(zip(frames, solved, flats)):
        k = i % 4
        fr['phase'] = ('contact', 'down', 'push-off', 'flight')[k]
        fr['stance'] = None if k == 3 else ('near' if i < 4 else 'far')
        fr['lowest_px'] = w8.lowest(np.asarray(flat))
        fr['sole_px'] = {s: w8.lowest(w8.draw(parts, w8.LEGS[s], oy)) for s in 'NF'}       # lowest pixel of each leg
        fr['toe_x_px'] = None if k == 3 else toe_px(parts, 'N' if i < 4 else 'F', oy)       # front end of the planted sole, from the hip
        fr['lean_deg'] = round(math.degrees(math.atan2(J['neck0'][0] - J['hip'][0], J['hip'][1] - J['neck0'][1])), 1)
        fr['elbow_flex_deg'] = {s: round(angle_deg(J['S' + s], J['elb' + s], J['hand' + s]), 1) for s in 'NF'}
        fr['arm_table_deg'] = {'N': list((ARM_ST if i < 4 else ARM_SW)[k]), 'F': list((FAR_SW if i < 4 else FAR_ST)[k])}
        fr['neck_x_px'] = round(float(J['neck0'][0] * HEAD_PX), 1)
        mask = np.any(np.asarray(flat) != key, axis=-1)
        fr['head_front_px'] = int(np.nonzero(mask[:BASELINE - 330].any(0))[0].max()) - SLOT // 2
    strips = [Image.open(os.path.join(a.out, f'{a.name}_{s}.png')) for s in 'ab']
    review(flats, strips, os.path.join(a.out, f'{a.name}_review.png'))
    hips = [f['hip_height_px'] for f in frames]
    clear = [BASELINE - frames[i]['lowest_px'] for i in (3, 7)]
    info = dict(set=a.name, gait='run', head_px=HEAD_PX, baseline=BASELINE, scale=SCALE, frames_per_cycle=8, nominal_ms=MS,
                step_px=round(a.step * HEAD_PX, 1), run_stride_game_px=round(a.step * HEAD_PX * SCALE, 1),
                speed_at_nominal_ms_game_px_s=round(a.step * HEAD_PX * SCALE / (4 * MS / 1000), 1),
                bob_px=round(max(hips) - min(hips), 1), flight_clearance_px=min(clear),
                lean_deg=[min(f['lean_deg'] for f in frames), max(f['lean_deg'] for f in frames)],
                push_ankle_shift_px=round(dx * HEAD_PX, 1), bones_px=w8.bones_px(B), posekit_warnings=warns, frames=frames)
    with open(os.path.join(a.out, 'pose.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{a.name}: step {info["step_px"]} px ({info["run_stride_game_px"]} game px), bob {info["bob_px"]} px, '
          f'flight clearance {info["flight_clearance_px"]} px, lean {info["lean_deg"][0]}-{info["lean_deg"][1]} deg, '
          f'{MS} ms/frame, posekit warnings {len(warns)} -> {a.out}')
    for w in warns:
        print('  ' + w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
