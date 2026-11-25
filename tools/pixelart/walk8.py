#!/usr/bin/env python3
"""8-frame walk skeleton on the posekit mannequin (pose guide for drawing walk frames; not game art).

  python3 tools/pixelart/walk8.py OUT_DIR [--name walk_base] [--step 1.30]

Writes OUT_DIR/<name>_a.png (W1-W4) and <name>_b.png (W5-W8): 1536x1024, #FF00FF, 1x4, head 110 px, lowest pixel y=870;
<name>_preview.gif (game scale 0.1654, x4 nearest, 120 ms); pose.json (joints per frame in strip px, measurements);
layers/W<n>_<layer>.png (each frame on a 384x1024 canvas, split into the SPEC layers + a `joints` layer of colour-coded 3x3 dots)
and, with --aseprite EXE, <name>.aseprite: 8 frames x 120 ms with those layers - the file the Aseprite session plays and refines
(measured afterwards by tools/art/check_skeleton.py).

Frames (near = the character's right leg, drawn light; far = dark):
  W1 contact (near heel strikes, both feet down)  W2 down (near foot flat, weight on it, far foot kicked up, arm extremes)
  W3 passing (near leg straight under the hip, far knee leading)  W4 up (near heel lifting, far foot reaching toe-up)
  W5-W8 the same with near/far swapped.
The numbers follow art/requests/guides/SPEC.md (geometry first: a straight supporting leg at passing sets the body bob).
2026-11-26: the Aseprite session's refinement (art-inbox 2c31b96) is folded in - passing swing ankle (0.13, 0.45), elbow of the arm
going back at passing 30 deg with shoulder factor 0.92, heel lift at `up` 22 deg - together with one floor for all frames (`planted`).
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
HIP = [1.625, 1.61, 1.74, 1.75]                # hip joint height: lowest at down, highest at passing/up
LEAN = [0.13, 0.15, 0.11, 0.10]                # torso lean forward (rad)
TILT = [0.0, 0.03, 0.0, -0.02]                 # head tilt (rad)
SHW = [1.10, 1.10, 0.92, 0.95]                 # shoulder width factor (counter-rotation), mirrored for the other half
ARM_FWD = [(30, 40), (32, 45), (5, 20), (-15, 12)]     # arm swinging forward: (upper-arm deg from straight down, elbow flex deg)
ARM_BACK = [(-28, 10), (-32, 8), (-5, 30), (15, 30)]   # arm swinging back


def tables(step):
    """stance-leg and swing-leg ankle tables for a step of `step` heads (ankle to ankle at contact)."""
    k = step / 1.30
    # the front foot lands 0.56 ahead of the hip, the rear pushes off 0.74 behind: with the body leaning forward the near leg
    # (its hip joint sits 0.05 behind the centre) still reaches the floor with a nearly straight knee at heel strike
    fx, rx, d = 0.56 * k, -0.74 * k, step / 4
    a = pk.Body(4.0).ank
    # ankle x, ankle h, foot angle (deg; - = toe up). The heights of feet on the floor are starting values: `planted` settles them
    stance = [(fx, 0.13, -20), (fx - d, a, 0), (fx - 2 * d, a, 0), (fx - 3 * d, 0.23, 22)]
    swing = [(rx, 0.30, 35), (rx + 0.06, 0.50, 60), (0.13, 0.45, 10), (0.50 * k, 0.30, -15)]
    return stance, swing


NEAR_FWD = 7                                   # the near shoulder sits further back: its arm swings this many degrees further forward


def pose(i, B, step, lift=(0.0, 0.0)):
    """pose table for frame i; lift = extra ankle height (heads) of the stance / the other leg (see `planted`)"""
    k, near_stance = i % 4, i < 4
    stance, swing = tables(step)
    st, sw = stance[k], swing[k]
    st, sw = (st[0], st[1] + lift[0], st[2]), (sw[0], sw[1] + lift[1], sw[2])
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
        if side == 'N' and not near_stance:
            ud += NEAR_FWD * max(0.0, ud) / 32
        a, b = math.radians(ud), math.radians(ud + fl)
        elbow = shoulders[side] + B.upper * np.array((math.sin(a), math.cos(a)))
        hand = elbow + (B.fore + B.hand) * np.array((math.sin(b), math.cos(b)))
        p['hand' + side] = ('p', hand[0], -hand[1])
        p['elb' + side] = tuple(elbow - (shoulders[side] + hand) / 2) if fl > 1 else (-1.0, 0.0)
    p['z'] = {'farfore': 'back'}
    return p


LAYERS = (('arm_far', ('upperF', 'foreF', 'handF')), ('leg_far', ('thighF', 'shinF', 'bootF')), ('leg_near', ('thighN', 'shinN', 'bootN')),
          ('torso', ('neck', 'pelvis', 'torso', 'belt')), ('head', ('head', 'hair', 'ear', 'eyeN', 'eyeF')), ('arm_near', ('upperN', 'foreN', 'handN')))
# joints layer: one 3x3 dot per joint, a fixed colour each (the cloud measures bone lengths, stride and bob from these dots)
JOINTS = (('hipN', 'HN', (255, 255, 0)), ('hipF', 'HF', (200, 200, 0)), ('kneeN', 'kneeN', (0, 255, 0)), ('kneeF', 'kneeF', (0, 170, 0)),
          ('ankN', 'ankN', (0, 255, 255)), ('ankF', 'ankF', (0, 170, 170)), ('shoN', 'SN', (255, 128, 0)), ('shoF', 'SF', (200, 100, 0)),
          ('elbN', 'elbN', (255, 0, 0)), ('elbF', 'elbF', (170, 0, 0)), ('handN', 'handN', (0, 0, 255)), ('handF', 'handF', (0, 0, 170)),
          ('neck', 'neck0', (255, 255, 255)))


LEGS = {'N': ('thighN', 'shinN', 'bootN'), 'F': ('thighF', 'shinF', 'bootF')}


def draw(parts, sel, oy):
    """the parts named in sel (None = all) on one 384x1024 frame canvas, hip centre on x=192, world floor on row oy; hard edges"""
    R = pk.Raster(SLOT, SH_, HEAD_PX, SLOT / 2, oy, 1)
    return np.asarray(pk.render_guide([q for q in parts if sel is None or q[0] in sel], R, 2.3))


def lowest(rgb):
    return int(np.nonzero(np.any(rgb != np.array(pk.BG, np.uint8), axis=-1).any(1))[0].max())


def floor_row(B, step):
    """the canvas row of the world floor: chosen so a flat planted boot (W2) ends exactly on the baseline"""
    _, parts = pk.build(pose(1, B, step), B, 'none')
    return BASELINE - (lowest(draw(parts, LEGS['N'], BASELINE)) - BASELINE)


def planted(i, B, step, oy):
    """pose i with its feet on ONE floor: the ankle of the stance leg (at contact: of both legs) is raised or lowered until that
    leg's lowest pixel is on the baseline. The floor never moves, so the hip heights of the table are what the picture shows
    (shifting each frame to its own lowest pixel made the mirror halves differ by 3 px and floated the heel strike)."""
    k, near_stance = i % 4, i < 4
    lift = [0.0, 0.0]
    sides = ('N', 'F') if near_stance else ('F', 'N')          # stance side, other side
    for it in range(24):
        p = pose(i, B, step, tuple(lift))
        J, parts = pk.build(p, B, 'none')
        off = [lowest(draw(parts, LEGS[sides[0]], oy)) - BASELINE, lowest(draw(parts, LEGS[sides[1]], oy)) - BASELINE if k == 0 else 0]
        if not any(off):
            break
        lift = [lift[j] + off[j] / HEAD_PX * (1.0 if it < 3 else 0.35) for j in range(2)]   # damped: a whole pixel can overshoot
    else:
        raise AssertionError(f'W{i + 1}: the feet do not settle on the floor ({off})')
    return p, J, parts


def frame_layers(parts, J, oy):
    """one walk frame on a 384x1024 canvas (hip centre x=192, world floor on row oy), split into the SPEC layers.
    -> ({layer: RGBA image}, flattened RGB image)"""
    full = draw(parts, None, oy)
    out = {}
    for name, sel in LAYERS:
        rgb = draw(parts, set(sel), oy)
        a = np.any(rgb != np.array(pk.BG, np.uint8), axis=-1)
        out[name] = Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), 'RGBA')
    jl = np.zeros((SH_, SLOT, 4), np.uint8)
    for _, key, col in JOINTS:
        x, y = int(round(SLOT / 2 + J[key][0] * HEAD_PX)), int(round(oy + J[key][1] * HEAD_PX))
        jl[y - 1:y + 2, x - 1:x + 2] = (*col, 255)
    out['joints'] = Image.fromarray(jl, 'RGBA')
    return out, Image.fromarray(full, 'RGB')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('--name', default='walk_base')
    ap.add_argument('--step', type=float, default=1.30, help='step length in heads (ankle to ankle at contact; 1.30 = 143 px)')
    ap.add_argument('--aseprite', help='Aseprite executable (e.g. tools/art/ase_headless.sh): also build <name>.aseprite - 8 frames, part layers, hidden joints layer')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    B = pk.Body(4.0)
    oy = floor_row(B, a.step)
    solved = [planted(i, B, a.step, oy) for i in range(8)]
    poses, builds = [q[0] for q in solved], [(q[1], q[2]) for q in solved]
    warns = [f'W{i + 1}: {m}' for i, (p, (J, _)) in enumerate(zip(poses, builds)) for m in pk.check(f'W{i + 1}', J, B, p)]
    frames, small = [], []
    strips = [np.full((SH_, SW_, 3), pk.BG, np.uint8) for _ in range(2)]
    # every frame on its own 384x1024 canvas (hip centre on x=192: the body stays put, the feet travel), split into layers
    # for the Aseprite working file; the strips are exactly those frames side by side
    ldir = os.path.join(a.out, 'layers')
    os.makedirs(ldir, exist_ok=True)
    for i, (p, (J, parts)) in enumerate(zip(poses, builds)):
        layers, flat = frame_layers(parts, J, oy)
        for name, im in layers.items():
            im.save(os.path.join(ldir, f'W{i + 1}_{name}.png'))
        sx = (i % 4) * SLOT
        strips[i // 4][:, sx:sx + SLOT] = np.asarray(flat)
        mask = np.any(np.asarray(flat) != np.array(pk.BG, np.uint8), axis=-1)
        xs = np.nonzero(mask.any(0))[0]
        assert xs.min() >= 8 and xs.max() < SLOT - 8, (i, xs.min(), xs.max())     # inside its own frame (check_delivery measures the gaps)

        def px(v):   # world (heads) -> strip px
            return [round(float(sx + SLOT / 2 + v[0] * HEAD_PX), 1), round(float(oy + v[1] * HEAD_PX), 1)]
        flex = {s: round(2 * math.degrees(math.acos(min(1.0, float(np.linalg.norm(J['ank' + s] - J['H' + s])) / (B.thigh + B.shin)))), 1) for s in 'NF'}
        joints = {k: px(J[k]) for k in ('hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'SN', 'SF', 'elbN', 'elbF', 'handN', 'handF', 'neck0')
                  if k in J and hasattr(J[k], '__len__')}
        frames.append(dict(frame=f'W{i + 1}', strip='ab'[i // 4], slot=i % 4 + 1, hip_height_px=round(HIP[i % 4] * HEAD_PX, 1),
                           top_px=int(np.nonzero(mask.any(1))[0].min()), knee_flex_deg=flex, joints=joints))
        cell = flat.crop((0, BASELINE - 500, SLOT, BASELINE + 12))
        small.append(cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX))
    for k, name in enumerate('ab'):
        Image.fromarray(strips[k], 'RGB').save(os.path.join(a.out, f'{a.name}_{name}.png'))
    if a.aseprite:
        import subprocess
        lua = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_skeleton_ase.lua')
        out = os.path.abspath(os.path.join(a.out, a.name + '.aseprite'))
        r = subprocess.run([a.aseprite, '-b', '--script-param', 'dir=' + os.path.abspath(ldir), '--script-param', 'out=' + out,
                            '--script-param', 'frames=8', '--script-param', 'ms=120', '--script', lua], capture_output=True)
        print(('wrote ' + out) if os.path.exists(out) else 'Aseprite build FAILED: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
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
