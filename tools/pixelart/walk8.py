#!/usr/bin/env python3
"""8-frame walk skeleton on the posekit mannequin (pose guide for drawing walk frames; not game art).

  python3 tools/pixelart/walk8.py OUT_DIR [--name walk_base] [--step 1.30]

Writes OUT_DIR/<name>_a.png (W1-W4) and <name>_b.png (W5-W8): 1536x1024, #FF00FF, 1x4, head 110 px, lowest pixel y=870;
<name>_preview.gif (game scale 0.1654, x4 nearest, 120 ms); pose.json (joints per frame in strip px, measurements).

Frames (near = the character's right leg, drawn light; far = dark):
  W1 contact (near heel strikes, both feet down)  W2 down (near foot flat, weight on it, far foot kicked up, arm extremes)
  W3 passing (near leg straight under the hip, far knee leading)  W4 up (near heel lifting, far foot reaching toe-up)
  W5-W8 the same with near/far swapped.
The numbers follow art/requests/guides/SPEC.md (geometry first: a straight supporting leg at passing sets the body bob).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import posekit as pk  # noqa: E402

HEAD_PX = 110
SW_, SH_ = 1536, 1024
BASELINE = 870
SLOT = SW_ // 4
SCALE = 0.1654

# per half cycle: index 0 contact, 1 down, 2 passing, 3 up   (head units; x forward, h above the floor)
HIP = [1.64, 1.62, 1.74, 1.75]                 # hip joint height: lowest at down, highest at passing/up
LEAN = [0.13, 0.15, 0.11, 0.10]                # torso lean forward (rad)
TILT = [0.0, 0.03, 0.0, -0.02]                 # head tilt (rad)
SHW = [1.10, 1.10, 1.0, 0.95]                  # shoulder width factor (counter-rotation), mirrored for the other half
ARM_FWD = [(30, 40), (32, 45), (5, 20), (-15, 12)]     # arm swinging forward: (upper-arm deg from straight down, elbow flex deg)
ARM_BACK = [(-28, 10), (-32, 8), (-5, 15), (15, 30)]   # arm swinging back


def tables(step):
    """stance-leg and swing-leg ankle tables for a step of `step` heads (ankle to ankle at contact)."""
    k = step / 1.30
    fx, rx, d = 0.62 * k, -0.68 * k, step / 4
    a = pk.Body(4.0).ank
    stance = [(fx, 0.165, -20), (fx - d, a, 0), (fx - 2 * d, a, 0), (fx - 3 * d, 0.20, 15)]      # ankle x, ankle h, foot angle (deg; - = toe up)
    swing = [(rx, 0.30, 35), (rx + 0.06, 0.50, 60), (0.08, 0.42, 10), (0.55 * k, 0.30, -15)]
    return stance, swing


def pose(i, B, step):
    k, near_stance = i % 4, i < 4
    stance, swing = tables(step)
    st, sw = stance[k], swing[k]
    p = dict(hip=(0.0, HIP[k]), lean=LEAN[k], tilt=TILT[k], hipw=0.05, kneeN=(1.0, 0.0), kneeF=(1.0, 0.0))
    sn, sf = (st, sw) if near_stance else (sw, st)
    p.update(footN=(sn[0], sn[1]), faN=sn[2], toeN=0.9, footF=(sf[0], sf[1]), faF=sf[2])
    shw = SHW[k] if near_stance else 2 - SHW[k]
    p['sw'] = shw
    hip = pk.P(*p['hip'])
    up, rt = pk.rot(pk.v2(0, -1), p['lean']), pk.rot(pk.v2(1, 0), p['lean'])
    shoulders = {'N': hip + rt * (-0.40 * shw) + up * (B.torso - 0.05), 'F': hip + rt * (0.34 * shw) + up * (B.torso - 0.07)}
    # the arm swings opposite to the leg on its side: near leg forward -> near arm back
    arms = {'N': ARM_BACK[k] if near_stance else ARM_FWD[k], 'F': ARM_FWD[k] if near_stance else ARM_BACK[k]}
    for side in 'NF':
        ud, fl = arms[side]
        a, b = math.radians(ud), math.radians(ud + fl)
        elbow = shoulders[side] + B.upper * np.array((math.sin(a), math.cos(a)))
        hand = elbow + (B.fore + B.hand) * np.array((math.sin(b), math.cos(b)))
        p['hand' + side] = ('p', hand[0], -hand[1])
        p['elb' + side] = tuple(elbow - (shoulders[side] + hand) / 2) if fl > 1 else (-1.0, 0.0)
    p['z'] = {'farfore': 'back'}
    return p


def render(parts, pad=8):
    """one pose cropped to its pixels at HEAD_PX. -> (rgb, mask, x of hip-centre column, sole row)"""
    x0, y0, x1, y1 = pk.bbox(parts)
    w, h = int(np.ceil((x1 - x0) * HEAD_PX)) + 2 * pad, int(np.ceil((y1 - y0) * HEAD_PX)) + 2 * pad
    ox, oy = pad - x0 * HEAD_PX, pad - y0 * HEAD_PX
    rgb = np.asarray(pk.render_guide(parts, pk.Raster(w, h, HEAD_PX, ox, oy, 1), 2.3)).copy()   # ss=1: hard edges (no colours blended with the key)
    mask = np.any(rgb != np.array(pk.BG, np.uint8), axis=-1)
    ys, xs = np.nonzero(mask)
    t, b, l, r = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return rgb[t:b, l:r], mask[t:b, l:r], ox - l, oy - t


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('--name', default='walk_base')
    ap.add_argument('--step', type=float, default=1.30, help='step length in heads (ankle to ankle at contact; 1.30 = 143 px)')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    B = pk.Body(4.0)
    poses = [pose(i, B, a.step) for i in range(8)]
    builds = [pk.build(p, B, 'none') for p in poses]
    warns = [f'W{i + 1}: {m}' for i, (p, (J, _)) in enumerate(zip(poses, builds)) for m in pk.check(f'W{i + 1}', J, B, p)]
    frames, small = [], []
    strips = [np.full((SH_, SW_, 3), pk.BG, np.uint8) for _ in range(2)]
    for i, (p, (J, parts)) in enumerate(zip(poses, builds)):
        rgb, mask, hx, hy = render(parts)
        h, w = mask.shape
        x0 = int(round((i % 4) * SLOT + SLOT / 2 - hx))   # hip centre on the slot centre: the body stays put, the feet travel
        y0 = BASELINE + 1 - h                             # lowest pixel on the baseline
        assert x0 >= 32 and x0 + w <= SW_ - 32, (i, x0, w)
        view = strips[i // 4][y0:y0 + h, x0:x0 + w]
        view[mask] = rgb[mask]

        def px(v):   # world (heads) -> strip px
            return [round(float(x0 + hx + v[0] * HEAD_PX), 1), round(float(y0 + hy + v[1] * HEAD_PX), 1)]
        flex = {s: round(2 * math.degrees(math.acos(min(1.0, float(np.linalg.norm(J['ank' + s] - J['H' + s])) / (B.thigh + B.shin)))), 1) for s in 'NF'}
        joints = {k: px(J[k]) for k in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF', 'elbN', 'elbF', 'handN', 'handF', 'neck0')
                  if k in J and hasattr(J[k], '__len__')}
        frames.append(dict(frame=f'W{i + 1}', strip='ab'[i // 4], slot=i % 4 + 1, hip_height_px=round(HIP[i % 4] * HEAD_PX, 1),
                           top_px=int(y0), knee_flex_deg=flex, joints=joints))
        cell = Image.fromarray(strips[i // 4][BASELINE - 500:BASELINE + 12, (i % 4) * SLOT:(i % 4 + 1) * SLOT], 'RGB')
        small.append(cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX))
    for k, name in enumerate('ab'):
        Image.fromarray(strips[k], 'RGB').save(os.path.join(a.out, f'{a.name}_{name}.png'))
    big = [f.resize((f.width * 4, f.height * 4), Image.NEAREST) for f in small]
    big[0].save(os.path.join(a.out, f'{a.name}_preview.gif'), save_all=True, append_images=big[1:], duration=120, loop=0, disposal=1)
    hips = [f['hip_height_px'] for f in frames]
    info = dict(set=a.name, head_px=HEAD_PX, baseline=BASELINE, scale=SCALE, frames_per_cycle=8, nominal_ms=120,
                step_px=round(a.step * HEAD_PX, 1), walk_stride_game_px=round(a.step * HEAD_PX * SCALE, 1),
                bob_px=round(max(hips) - min(hips), 1),
                bones_px=dict(thigh=round(B.thigh * HEAD_PX, 2), shin=round(B.shin * HEAD_PX, 2), upper_arm=round(B.upper * HEAD_PX, 2),
                              forearm_hand=round((B.fore + B.hand) * HEAD_PX, 2)),
                posekit_warnings=warns, frames=frames)
    with open(os.path.join(a.out, 'pose.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{a.name}: step {info["step_px"]} px ({info["walk_stride_game_px"]} game px), bob {info["bob_px"]} px, '
          f'posekit warnings {len(warns)} -> {a.out}')
    for w in warns:
        print('  ' + w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
