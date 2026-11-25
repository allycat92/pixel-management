#!/usr/bin/env python3
"""walk_base v2, PC refinement of tools/pixelart/walk8.py (same tables, three changes, per-part layers).

  python walk8_pc.py REPO_ROOT OUT_DIR      (REPO_ROOT = game branch checkout with tools/pixelart/walk8.py, posekit.py)

Changes against walk8.py (head units; W(i+4) stays the exact mirror of W(i)):
  1. passing swing ankle (0.08, 0.42) -> (0.13, 0.45): the lifted knee leads more (W7 was 40.5 px ahead, W3 58)
  2. arm swinging back at passing: elbow flex 15 -> 30 deg, and shoulder counter-rotation 1.00 -> 0.92
     (the far arm in W7 hung behind the torso; now its hand clears the torso front)
  3. up (W4/W8) stance foot: heel lift 15 -> 22 deg (reads at game size)
Writes walk_base_a.png / _b.png (composite), layer_<a|b>_<part>.png (RGBA), walk_base_preview.gif, pose.json.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

root, out = sys.argv[1:3]
sys.path.insert(0, os.path.join(root, 'tools', 'pixelart'))
import posekit as pk  # noqa: E402
import walk8 as w8  # noqa: E402

# ---- the three changes
w8.SHW = [1.10, 1.10, 0.92, 0.95]
w8.ARM_BACK = [(-28, 10), (-32, 8), (-5, 30), (15, 30)]
_orig_tables = w8.tables


def tables(step):
    stance, swing = _orig_tables(step)
    stance = list(stance)
    swing = list(swing)
    x, h, fa = stance[3]
    stance[3] = (x, h + 0.03, 22)          # more heel lift needs the ankle a little higher
    swing[2] = (0.13, 0.45, 10)
    return stance, swing


w8.tables = tables

LAYERS = [  # bottom -> top (SPEC 4)
    ('arm_far', {'upperF', 'foreF', 'handF'}),
    ('leg_far', {'thighF', 'shinF', 'bootF'}),
    ('leg_near', {'thighN', 'shinN', 'bootN'}),
    ('torso', {'pelvis', 'torso', 'belt', 'neck'}),
    ('head', {'head', 'hair', 'ear', 'eyeN', 'eyeF'}),
    ('arm_near', {'upperN', 'foreN', 'handN'}),
]
B = pk.Body(4.0)
STEP = 1.30
HEAD_PX, SW_, SH_, BASELINE, SLOT, SCALE = w8.HEAD_PX, w8.SW_, w8.SH_, w8.BASELINE, w8.SLOT, w8.SCALE
poses = [w8.pose(i, B, STEP) for i in range(8)]
builds = [pk.build(p, B, 'none') for p in poses]
warns = [f'W{i + 1}: {m}' for i, (p, (J, _)) in enumerate(zip(poses, builds)) for m in pk.check(f'W{i + 1}', J, B, p)]

strips = [np.full((SH_, SW_, 3), pk.BG, np.uint8) for _ in range(2)]
layers = [{ln: np.zeros((SH_, SW_, 4), np.uint8) for ln, _ in LAYERS} for _ in range(2)]
frames, small = [], []
pad = 8
for i, (p, (J, parts)) in enumerate(zip(poses, builds)):
    # placement exactly as walk8.render + main
    x0b, y0b, x1b, y1b = pk.bbox(parts)
    w = int(np.ceil((x1b - x0b) * HEAD_PX)) + 2 * pad
    h = int(np.ceil((y1b - y0b) * HEAD_PX)) + 2 * pad
    ox, oy = pad - x0b * HEAD_PX, pad - y0b * HEAD_PX
    R = pk.Raster(w, h, HEAD_PX, ox, oy, 1)
    full = np.asarray(pk.render_guide(parts, R, 2.3)).copy()
    mask = np.any(full != np.array(pk.BG, np.uint8), axis=-1)
    ys, xs = np.nonzero(mask)
    t, b, l, r = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    hx, hy = ox - l, oy - t
    ch, cw = b - t, r - l
    X0 = int(round((i % 4) * SLOT + SLOT / 2 - hx))
    Y0 = BASELINE + 1 - ch
    assert X0 >= 32 and X0 + cw <= SW_ - 32, (i, X0, cw)
    s = i // 4
    for ln, names in LAYERS:
        sub = [q for q in parts if q[0] in names]
        img = np.asarray(pk.render_guide(sub, R, 2.3))[t:b, l:r]
        m = np.any(img != np.array(pk.BG, np.uint8), axis=-1)
        view = layers[s][ln][Y0:Y0 + ch, X0:X0 + cw]
        view[m, :3] = img[m]
        view[m, 3] = 255
    view = strips[s][Y0:Y0 + ch, X0:X0 + cw]
    view[mask[t:b, l:r]] = full[t:b, l:r][mask[t:b, l:r]]

    def px(v):
        return [round(float(X0 + hx + v[0] * HEAD_PX), 1), round(float(Y0 + hy + v[1] * HEAD_PX), 1)]
    flex = {sd: round(2 * math.degrees(math.acos(min(1.0, float(np.linalg.norm(J['ank' + sd] - J['H' + sd])) / (B.thigh + B.shin)))), 1)
            for sd in 'NF'}
    joints = {k: px(J[k]) for k in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF', 'elbN', 'elbF', 'handN', 'handF', 'neck0')
              if k in J and hasattr(J[k], '__len__')}
    frames.append(dict(frame=f'W{i + 1}', strip='ab'[s], slot=i % 4 + 1, hip_height_px=round(w8.HIP[i % 4] * HEAD_PX, 1),
                       top_px=int(Y0), knee_flex_deg=flex, joints=joints))

for s, name in enumerate('ab'):
    comp = np.full((SH_, SW_, 3), pk.BG, np.uint8)
    for ln, _ in LAYERS:
        L = layers[s][ln]
        m = L[..., 3] > 0
        comp[m] = L[m, :3]
        Image.fromarray(L, 'RGBA').save(os.path.join(out, f'layer_{name}_{ln}.png'))
    diff = int(np.any(comp != strips[s], axis=-1).sum())
    print(f'strip {name}: layered composite vs single render differs in {diff} px')
    Image.fromarray(comp, 'RGB').save(os.path.join(out, f'walk_base_{name}.png'))
    for k in range(4):
        cell = Image.fromarray(comp[BASELINE - 500:BASELINE + 12, k * SLOT:(k + 1) * SLOT], 'RGB')
        small.append(cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX))
big = [f.resize((f.width * 4, f.height * 4), Image.NEAREST) for f in small]
big[0].save(os.path.join(out, 'walk_base_preview.gif'), save_all=True, append_images=big[1:], duration=120, loop=0, disposal=1)
hips = [f['hip_height_px'] for f in frames]
info = dict(set='walk_base', made_by='PC walk8_pc.py (walk8.py tables + 3 changes, see script header)',
            head_px=HEAD_PX, baseline=BASELINE, scale=SCALE, frames_per_cycle=8, nominal_ms=120,
            step_px=round(STEP * HEAD_PX, 1), walk_stride_game_px=round(STEP * HEAD_PX * SCALE, 1),
            bob_px=round(max(hips) - min(hips), 1),
            bones_px=dict(thigh=round(B.thigh * HEAD_PX, 2), shin=round(B.shin * HEAD_PX, 2), upper_arm=round(B.upper * HEAD_PX, 2),
                          forearm_hand=round((B.fore + B.hand) * HEAD_PX, 2)),
            posekit_warnings=warns, frames=frames)
with open(os.path.join(out, 'pose.json'), 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('step', info['step_px'], 'bob', info['bob_px'], 'warnings', len(warns))
for wmsg in warns:
    print('  ' + wmsg)
