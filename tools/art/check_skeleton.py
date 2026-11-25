#!/usr/bin/env python3
"""Measure a walk or run skeleton set (pose guide, not game art) against art/requests/guides/SPEC.md sections 3-6 (run: 5b).

  python3 tools/art/check_skeleton.py SET.aseprite [--pose pose.json] [--base DRAFT.aseprite] [--export DIR] [--gait walk|run]
  python3 tools/art/check_skeleton.py LAYERS_DIR          # W<n>_<layer>.png files as tools/pixelart/walk8.py writes them (no Aseprite needed)
                                                          # (R<n>_<layer>.png from tools/pixelart/run8.py)

The working file is the layered 8-frame .aseprite that walk8.py builds (384x1024 per frame, layers per body part, a hidden
`joints` layer with one colour-coded 3x3 dot per joint). The Aseprite session plays and refines it; this tool then measures
what only numbers can tell (bone lengths, the planted foot, the mirror half, the bob) from the joint dots and the layers.

FAIL: canvas/frames/layers wrong, the joints layer not hidden, a joint dot missing or left behind by its limb, bone length off by
      more than 2 px in any frame, the hip centre (mid-point of hipN/hipF) more than 1 px off x=192 (the body stays on the frame's
      centre column: add_gait.py anchors every frame on it), the head layer empty or not touching the torso layer (detached head),
      stance sole not on y=870 or a foot below it, step outside 135-151 px, planted foot not retreating by step/4 (+-3 px) per frame,
      W(i+4) not the mirror of W(i), soft (half-transparent) pixels.
WARN: bob outside 12-16 px or in the wrong order, passing knee bent more than 15 deg, lifted foot outside 30-36 px,
      forward hand less than 20 px outside the torso, neighbouring frames nearly identical at game size, the head moving more than
      4 px against the neck dot across the frames (a tilt about the neck is allowed: the drift is what is left after the head's own
      rotation), a frame duration that differs from pose.json nominal_ms (walk 120, run 80 when no pose.json is given).
--export DIR writes the strips (<set>_a.png, <set>_b.png), the game-size preview GIF and pose_measured.json from the file,
so the Aseprite session only has to deliver the .aseprite. --base DRAFT.aseprite lists what was changed per frame and layer.
Exit code 1 on FAIL.

RUN sets (gait "run" in --pose pose.json, or --gait run, or R<n>_ layer files, or a file named run_*): frames R1 contact, R2 down,
R3 push-off, R4 flight, R5-R8 the mirror. The shared rules (canvas, layers, joint dots on their limbs, bones +-2 px, crisp edges)
stay; the walk rules are replaced by:
FAIL: R1-R3 / R5-R7: the supporting sole not on y=870, a pixel below it, or the OTHER foot less than 12 px above the floor (both
      feet down is a walk); R4 / R8: lowest pixel less than 18 px above the floor (no flight); the planted toe (front end of the
      supporting sole) not retreating by step/4 (+-3 px) per stance frame, where step = 2 x (toe R1 - toe R3) is the distance the
      body travels per step; step more than 14 px from the request (pose.json step_px, default 275); R(i+4) not the mirror of
      R(i) (hip height +-1, ankle x +-2, ankle y +-4); hip not lowest at down or not highest in flight; R4 / R8: the leg that
      just pushed off (near in R4, far in R8) not trailing the other one by 110 px or more (ankle x - scissored legs, the right
      leg behind); the arm of the pushing leg BEHIND the other one at push-off / flight (arms pumping the wrong way).
WARN: bob outside 32-46 px; elbow flex outside 60-125 deg in any frame; the arm of the pushing leg less than 60 px ahead of
      the other one at push-off / flight (hand x from its shoulder); lean outside 14-26 deg, lean range over 5 deg or the neck
      travelling more than 12 px (pecking); push-off knee bent more than 30 deg; down knee outside 35-65 deg; landing foot not
      0-70 px ahead of the hip; neighbouring frames nearly identical at game size;
      strip findings of check_delivery.py (the two strips are built in memory and checked with --flight-slots 4: slot 4 is the
      flight frame and must be 18 px or more above the floor instead of on it).
"""
import argparse
from collections import Counter
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'pixelart'))
from walk8 import BASELINE, HEAD_PX, JOINTS, SCALE, SLOT, SH_  # noqa: E402
from run8 import SOLE_BAND, STEP as RUN_STEP  # noqa: E402

HEADLESS = os.path.join(ROOT, 'tools', 'art', 'ase_headless.sh')
BODY = ('arm_far', 'leg_far', 'leg_near', 'torso', 'head', 'arm_near')          # the layers every set must have
ORDER = ('cloth_back', 'weapon_back', 'arm_far', 'shield', 'leg_far', 'leg_near', 'torso', 'cloth_front', 'head',
         'weapon_front', 'arm_near')                                           # SPEC section 4, bottom to top
PART_OF = dict(hipN='leg_near', kneeN='leg_near', ankN='leg_near', hipF='leg_far', kneeF='leg_far', ankF='leg_far',
               shoN='arm_near', elbN='arm_near', handN='arm_near', shoF='arm_far', elbF='arm_far', handF='arm_far', neck='torso')
BONES = (('thigh', 'hip', 'knee'), ('shin', 'knee', 'ank'), ('upper_arm', 'sho', 'elb'), ('forearm_hand', 'elb', 'hand'))
DEFAULT_BONES = dict(thigh=89.65, shin=89.65, upper_arm=68.2, forearm_hand=71.5)
KEY = (255, 0, 255)


def run(exe, *args):
    env = dict(os.environ)
    if os.name != 'nt':
        env.pop('DISPLAY', None)
        env.pop('WAYLAND_DISPLAY', None)
    return subprocess.run([exe, '--batch', *args], stdin=subprocess.DEVNULL, capture_output=True, timeout=300, env=env)


def load_aseprite(src, exe, work):
    """-> (frames: [{layer: RGBA array}], durations ms, layer names bottom to top, hidden layer names)"""
    os.makedirs(work, exist_ok=True)
    names = [n.strip() for n in run(exe, '--all-layers', '--list-layers', src).stdout.decode('utf-8', 'replace').splitlines() if n.strip()]
    if not names:
        raise RuntimeError(f'Aseprite listed no layers for {src} (is {exe} an Aseprite executable?)')
    visible = [n.strip() for n in run(exe, '--list-layers', src).stdout.decode('utf-8', 'replace').splitlines() if n.strip()]
    dup = [n for n, k in Counter(names).items() if k > 1]
    if dup:
        raise RuntimeError(f'layer names must be unique, more than one layer is named: {", ".join(dup)}')
    data = os.path.join(work, 'data.json')
    run(exe, src, '--sheet', os.path.join(work, 'sheet.png'), '--data', data, '--format', 'json-array')
    with open(data, encoding='utf-8') as f:
        durs = [fr['duration'] for fr in json.load(f)['frames']]
    r = run(exe, '--all-layers', '--split-layers', src, '--save-as', os.path.join(work, '{layer}_{frame}.png'))
    frames = []
    for i in range(len(durs)):
        fr = {}
        for n in names:
            p = os.path.join(work, f'{n}_{i}.png')
            if not os.path.exists(p):
                raise RuntimeError(f'Aseprite did not export layer {n} frame {i}: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
            fr[n] = np.asarray(Image.open(p).convert('RGBA'))
        frames.append(fr)
    return frames, durs, names, list((Counter(names) - Counter(visible)).elements())


def dir_prefix(src):
    """'R' for a folder of run8.py layer files (R<n>_<layer>.png), else 'W'"""
    return 'R' if os.path.isdir(src) and os.path.exists(os.path.join(src, 'R1_torso.png')) else 'W'


def load_dir(src):
    frames, i, t = [], 1, dir_prefix(src)
    while os.path.exists(os.path.join(src, f'{t}{i}_torso.png')):
        fr = {}
        for fn in sorted(os.listdir(src)):
            if fn.startswith(f'{t}{i}_') and fn.endswith('.png'):
                fr[fn[len(f'{t}{i}_'):-4]] = np.asarray(Image.open(os.path.join(src, fn)).convert('RGBA'))
        frames.append(fr)
        i += 1
    names = [n for n in ORDER if frames and n in frames[0]] + ['joints']
    return frames, [120 if t == 'W' else 80] * len(frames), ['Background'] + names, ['joints']


def flatten(fr, names):
    """the visible picture of one frame: body layers over the key colour -> (RGB array, body mask)"""
    h, w = next(iter(fr.values())).shape[:2]
    rgb = np.empty((h, w, 3), np.uint8)
    rgb[:] = KEY
    mask = np.zeros((h, w), bool)
    for n in names:
        if n in ('Background', 'joints') or n not in fr:
            continue
        a = fr[n][..., 3] > 0
        rgb[a] = fr[n][..., :3][a]
        mask |= a
    return rgb, mask


def dots(joints_layer):
    """-> ({joint: (x, y) centre}, problems)"""
    out, bad = {}, []
    opaque = joints_layer[..., 3] == 255
    for name, _, col in JOINTS:
        ys, xs = np.nonzero(opaque & np.all(joints_layer[..., :3] == np.array(col, np.uint8), axis=-1))
        if not len(xs):
            bad.append(f'joint dot {name} {col} is missing')
        elif xs.max() - xs.min() > 4 or ys.max() - ys.min() > 4:
            bad.append(f'joint dot {name} {col} appears more than once ({xs.min()},{ys.min()})-({xs.max()},{ys.max()})')
        else:
            out[name] = (float(xs.mean()), float(ys.mean()))
    return out, bad


def near_opaque(layer, x, y, r=3):
    x, y = int(round(x)), int(round(y))
    return bool((layer[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1, 3] > 0).any())


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def knee_flex(hip, knee, ank):
    """bend at the middle joint of a three-joint chain in degrees (0 = straight); also used for the elbow"""
    a = (hip[0] - knee[0], hip[1] - knee[1])
    b = (ank[0] - knee[0], ank[1] - knee[1])
    c = (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b) or 1)
    return 180 - math.degrees(math.acos(max(-1.0, min(1.0, c))))


# run sets (SPEC section 5b). Numbers from the run_base v1 draft: step 275 px, bob 37.4 px, flight clearance 37-41 px,
# elbows 80-110 deg, lean 18.2-20.5 deg, push-off knee 16-18 deg, down knee 51-53 deg, landing ankle 40 px ahead of the hip,
# flight ankles 176 px apart with the pushing leg behind
RUN = dict(step=RUN_STEP * HEAD_PX, step_tol=14, clear=18, other=12, bob=(32, 46), elbow=(60, 125), pump=60, lean=(14, 26), lean_range=5,
           neck=12, push_flex=30, down_flex=(35, 65), land=(0, 70), scissor=110)
HIP_X_TOL = 1          # the hip centre stays on the frame's centre column x = SLOT / 2 (add_gait.py anchors there)
HEAD_DRIFT = 4         # px the head may move against the neck dot over the cycle, after its own tilt (both drafts: under 1.1)
NOMINAL_MS = dict(walk=120, run=80)


def grow1(mask):
    """the mask grown by one pixel (8 neighbours), NumPy only (the PC runs this with pillow + numpy)"""
    g = mask.copy()
    g[1:] |= mask[:-1]
    g[:-1] |= mask[1:]
    h = g.copy()
    h[:, 1:] |= g[:, :-1]
    h[:, :-1] |= g[:, 1:]
    return h


def head_pose(head_mask, neck):
    """-> (centroid of the head layer from the neck dot (x, y), orientation of the head's shape in rad, elongation) or None.
    The orientation (principal axis of the second moments) lets head_cycle() tell a tilt about the neck from a head that slides."""
    ys, xs = np.nonzero(head_mask)
    if not len(xs):
        return None
    x, y = xs - xs.mean(), ys - ys.mean()
    a, b, c = float((x * x).mean()), float((x * y).mean()), float((y * y).mean())
    root = math.sqrt(((a - c) / 2) ** 2 + b * b)
    lo, hi = (a + c) / 2 - root, (a + c) / 2 + root
    return (float(xs.mean()) - neck[0], float(ys.mean()) - neck[1]), 0.5 * math.atan2(2 * b, a - c), hi / max(lo, 1e-6)


def head_cycle(meas, T, warns, info):
    """the head against the neck dot over the cycle. A tilt about the neck is allowed: the head's own rotation (from its shape)
    is taken out, the rest is drift (a head that pecks or slides on the neck). A nearly round head gives no usable rotation:
    then only the distance from the neck is compared."""
    hp = [m.get('head') for m in meas]
    if any(h is None for h in hp):
        return
    hp = [(tuple(h['from_neck_px']), h['axis_rad'], h['elongation']) for h in hp]
    (c0x, c0y), th0, _ = hp[0]
    round_head = min(h[2] for h in hp) < 1.08
    drift, tilts = [], []
    for (cx, cy), th, _ in hp:
        dt = 0.0 if round_head else (th - th0 + math.pi / 2) % math.pi - math.pi / 2
        tilts.append(math.degrees(dt))
        px, py = c0x * math.cos(dt) - c0y * math.sin(dt), c0x * math.sin(dt) + c0y * math.cos(dt)
        drift.append(abs(math.hypot(cx, cy) - math.hypot(c0x, c0y)) if round_head else math.hypot(cx - px, cy - py))
    info.append('head against the neck dot (after its own tilt' + (', round head: distance only' if round_head else '') + '): drift '
                + ' '.join(f'{d:.1f}' for d in drift) + f' px, tilt {min(tilts):+.1f}..{max(tilts):+.1f} deg from {T}1')
    for i, d in enumerate(drift):
        if d > HEAD_DRIFT:
            warns.append(f'{T}{i + 1}: the head layer sits {d:.1f} px off its {T}1 place against the neck dot (after its tilt), SPEC asks '
                         f'{HEAD_DRIFT} or less - the head pecks or slides on the neck (move it with the torso, or tilt it about the neck)')


def check(frames, durs, names, hidden, bones, gait='walk', want_step=None, nominal_ms=None):
    errors, warns, info, meas = [], [], [], []
    n = len(frames)
    T = 'R' if gait == 'run' else 'W'
    if n != 8:
        errors.append(f'{n} frames, a walk cycle is 8 (SPEC section 5)' if gait == 'walk' else f'{n} frames, a run cycle is 8 (SPEC section 5b)')
    h, w = next(iter(frames[0].values())).shape[:2]
    if (w, h) != (SLOT, SH_):
        errors.append(f'frame canvas {w}x{h}, expected {SLOT}x{SH_}')
    info.append(f'{n} frames, {w}x{h}, durations {sorted(set(durs))} ms, layers: {" · ".join(names)}')
    for miss in [m for m in BODY + ('joints',) if m not in names]:
        errors.append(f'layer "{miss}" is missing')
    for odd in [m for m in names if m not in ORDER + ('Background', 'joints')]:
        errors.append(f'layer "{odd}" is not a SPEC section 4 name')
    for hid in [m for m in hidden if m != 'joints']:
        errors.append(f'layer "{hid}" is hidden: only joints may be hidden (a hidden layer is not in the exported picture)')
    present = [m for m in names if m in ORDER]
    if present != [m for m in ORDER if m in present]:
        warns.append(f'layer order {present} differs from SPEC section 4 (bottom to top: {" · ".join(m for m in ORDER if m in present)})')
    if errors:
        return errors, warns, info, meas, []
    if 'joints' not in hidden:
        errors.append('layer "joints" is visible: hide it (the dots would be in the exported strips and in the game frames '
                      'add_gait.py makes from the .aseprite)')
    want_ms = nominal_ms or NOMINAL_MS[gait]
    odd_ms = [f'{T}{i + 1} {d}' for i, d in enumerate(durs) if d != want_ms]
    if odd_ms:
        warns.append(f'frame duration differs from pose.json nominal_ms {want_ms} ms: {", ".join(odd_ms)} ms '
                     f'(add_gait.py takes anims.{gait}.ms from the .aseprite durations)')
    flats = []
    for i, fr in enumerate(frames):
        tag = f'{T}{i + 1}'
        for ln in names:
            if ln in ('Background', 'joints'):
                continue
            al = fr[ln][..., 3]
            soft = int(((al > 0) & (al < 255)).sum())
            if soft:
                errors.append(f'{tag} {ln}: {soft} half-transparent pixels (edges must be crisp)')
        if 'Background' in fr and not np.all(fr['Background'][..., :3] == np.array(KEY, np.uint8)):
            errors.append(f'{tag}: Background is not pure #FF00FF')
        rgb, mask = flatten(fr, names)
        flats.append((rgb, mask))
        J, bad = dots(fr['joints'])
        errors += [f'{tag}: {b}' for b in bad]
        if bad:
            meas.append(None)
            continue
        for jn, layer in PART_OF.items():
            if not near_opaque(fr[layer], *J[jn]):
                errors.append(f'{tag}: joint dot {jn} at ({J[jn][0]:.0f},{J[jn][1]:.0f}) is not on the {layer} layer '
                              '(the limb was moved without its dot, or the dot without the limb)')
        m = dict(frame=tag, joints={k: [round(v[0], 1), round(v[1], 1)] for k, v in J.items()})
        hip = ((J['hipN'][0] + J['hipF'][0]) / 2, (J['hipN'][1] + J['hipF'][1]) / 2)
        m['hip_x_px'] = round(hip[0], 1)
        if abs(hip[0] - SLOT / 2) > HIP_X_TOL:
            errors.append(f'{tag}: hip centre (between hipN and hipF) at x={hip[0]:.1f}, must be {SLOT // 2} +-{HIP_X_TOL} - the body stays '
                          'on the frame\'s centre column (add_gait.py anchors every frame on it: this frame would jump sideways in the game)')
        m['hip_height_px'] = round(BASELINE - hip[1], 1)
        head = fr['head'][..., 3] > 0
        hp = head_pose(head, J['neck'])
        if hp is None:
            errors.append(f'{tag}: the head layer is empty')
        else:
            m['head'] = dict(from_neck_px=[round(hp[0][0], 2), round(hp[0][1], 2)], axis_rad=round(hp[1], 4), elongation=round(hp[2], 3))
            if not (grow1(head) & (fr['torso'][..., 3] > 0)).any():
                errors.append(f'{tag}: the head layer does not touch the torso layer (a detached head: move it back onto the neck)')
        m['bones_px'] = {}
        for bone, a, b in BONES:
            for s in 'NF':
                d = dist(J[a + s], J[b + s])
                m['bones_px'][bone + s] = round(d, 1)
                if abs(d - bones[bone]) > 2:
                    errors.append(f'{tag}: {bone} ({"near" if s == "N" else "far"}) is {d:.1f} px, must be {bones[bone]} +-2')
        m['ankle_x'] = {s: round(J['ank' + s][0] - hip[0], 1) for s in 'NF'}
        m['knee_flex_deg'] = {s: round(knee_flex(J['hip' + s], J['knee' + s], J['ank' + s]), 1) for s in 'NF'}
        ys = np.nonzero(mask.any(1))[0]
        m['lowest_px'] = int(ys.max())
        stance, swing = (('leg_near', 'leg_far') if i < 4 else ('leg_far', 'leg_near'))
        lows = {ln: int(np.nonzero((fr[ln][..., 3] > 0).any(1))[0].max()) for ln in (stance, swing)}
        if gait == 'run':
            run_frame(m, i, fr, J, hip, lows, stance, swing, errors)
        else:
            if m['lowest_px'] != BASELINE:
                errors.append(f'{tag}: lowest pixel at y={m["lowest_px"]}, the planted sole must be on y={BASELINE}')
            if lows[stance] != BASELINE:
                errors.append(f'{tag}: the stance leg ({stance}) ends at y={lows[stance]}, not on the floor line {BASELINE}')
            m['swing_sole_height_px'] = BASELINE - lows[swing]
        m['top_px'] = int(ys.min())
        tx = np.nonzero((fr['torso'][..., 3] > 0).any(0))[0]
        m['hand_past_torso_px'] = {s: round(J['hand' + s][0] - float(tx.max()), 1) for s in 'NF'}
        meas.append(m)
    if any(m is None for m in meas) or n != 8:
        return errors, warns, info, meas, flats
    if gait == 'run':
        run_cycle(meas, want_step, errors, warns, info)
    else:
        walk_cycle(meas, errors, warns, info)
    head_cycle(meas, T, warns, info)
    # neighbouring frames at game size
    small = []
    for _, mask in flats:
        im = Image.fromarray((mask * 255).astype(np.uint8)).resize((round(w * SCALE), round(h * SCALE)), Image.BOX)
        small.append(np.asarray(im) >= 128)
    diffs = []
    for i in range(n):
        a, b = small[i], small[(i + 1) % n]
        diffs.append(100.0 * (a ^ b).sum() / max(1, (a | b).sum()))
        if diffs[-1] < 8:
            warns.append(f'{T}{i + 1}->{T}{(i + 1) % n + 1}: silhouettes differ by {diffs[-1]:.0f}% at game size (under 8%: the frame adds nothing)')
    info.append('silhouette change to the next frame at game size: ' + ' '.join(f'{d:.0f}%' for d in diffs))
    return errors, warns, info, meas, flats


def walk_cycle(meas, errors, warns, info):
    """the walk rules that compare frames (SPEC section 5)"""
    # the step and the planted foot
    step = [meas[0]['ankle_x']['N'] - meas[0]['ankle_x']['F'], meas[4]['ankle_x']['F'] - meas[4]['ankle_x']['N']]
    info.append(f'step (ankle to ankle at contact): W1 {step[0]:.1f} px, W5 {step[1]:.1f} px (= {step[0] * SCALE:.1f} game px, the sheet\'s walkStride)')
    for k, s in enumerate(step):
        if not 135 <= s <= 151:
            errors.append(f'W{k * 4 + 1}: step {s:.1f} px, must be 135-151')
    for half, side in ((0, 'N'), (4, 'F')):
        xs = [meas[half + k]['ankle_x'][side] for k in range(4)]
        want = step[half // 4] / 4
        for k in range(3):
            d = xs[k] - xs[k + 1]
            if abs(d - want) > 3:
                errors.append(f'W{half + k + 1}->W{half + k + 2}: planted foot moves back {d:.1f} px, must be {want:.1f} +-3 (the foot would slide)')
        info.append(f'planted {"near" if side == "N" else "far"} ankle x (from the hip): ' + ' -> '.join(f'{x:.0f}' for x in xs)
                    + f' (step/4 = {want:.1f})')
    # W(i+4) is W(i) with the legs swapped
    for k in range(4):
        a, b = meas[k], meas[k + 4]
        if abs(a['hip_height_px'] - b['hip_height_px']) > 1:
            errors.append(f'W{k + 1}/W{k + 5}: hip height {a["hip_height_px"]} vs {b["hip_height_px"]} px (mirror halves must match +-1)')
        for s, o in (('N', 'F'), ('F', 'N')):
            if abs(a['ankle_x'][s] - b['ankle_x'][o]) > 2:
                errors.append(f'W{k + 1}/W{k + 5}: ankle x {a["ankle_x"][s]} vs {b["ankle_x"][o]} px (mirror halves must match +-2)')
    hips = [m['hip_height_px'] for m in meas]
    bob = max(hips) - min(hips)
    info.append('hip height: ' + ' '.join(f'{v:.0f}' for v in hips) + f' -> bob {bob:.1f} px ({bob * SCALE:.1f} game px)')
    if not 12 <= bob <= 16:
        warns.append(f'bob {bob:.1f} px, SPEC asks 12-16 (less reads stiff, more reads as hopping)')
    for half in (0, 4):
        hh = hips[half:half + 4]
        if hh.index(min(hh)) not in (0, 1) or hh.index(max(hh)) not in (2, 3):
            warns.append(f'W{half + 1}-W{half + 4}: the hip must be lowest at contact/down and highest at passing/up, got {hh}')
    for i, side, far_side in ((2, 'N', 'F'), (6, 'F', 'N')):
        m = meas[i]
        if m['knee_flex_deg'][side] > 17:
            warns.append(f'{m["frame"]} (passing): the supporting knee is bent {m["knee_flex_deg"][side]:.0f} deg, SPEC asks 15 or less (a straight leg carries the weight)')
        if not 30 <= m['swing_sole_height_px'] <= 36:
            warns.append(f'{m["frame"]} (passing): the lifted foot is {m["swing_sole_height_px"]} px above the floor, SPEC asks 30-36')
        if meas[i]['joints']['knee' + far_side][0] - meas[i]['joints']['knee' + side][0] < 38:
            warns.append(f'{m["frame"]} (passing): the lifted knee leads the supporting knee by '
                         f'{meas[i]["joints"]["knee" + far_side][0] - meas[i]["joints"]["knee" + side][0]:.0f} px, SPEC asks 38 or more')
    for i, side in ((1, 'F'), (5, 'N')):     # arm extremes: the arm opposite to the planted leg is forward
        v = meas[i]['hand_past_torso_px'][side]
        if v < 20:
            warns.append(f'W{i + 1}: the forward hand is {v:.0f} px outside the torso, SPEC asks 20 or more (it must read at game size)')


def run_frame(m, i, fr, J, hip, lows, stance, swing, errors):
    """the run rules of one frame (SPEC section 5b): R1-R3 / R5-R7 stand on ONE foot, R4 / R8 on none. Fills m with what
    run_cycle compares between frames"""
    tag, k = m['frame'], i % 4
    m['phase'] = ('contact', 'down', 'push-off', 'flight')[k]
    m['sole_height_px'] = {'N' if ln == 'leg_near' else 'F': BASELINE - lows[ln] for ln in (stance, swing)}
    m['ankle_y'] = {s: round(J['ank' + s][1] - hip[1], 1) for s in 'NF'}
    m['elbow_flex_deg'] = {s: round(knee_flex(J['sho' + s], J['elb' + s], J['hand' + s]), 1) for s in 'NF'}
    m['hand_from_shoulder_px'] = {s: round(J['hand' + s][0] - J['sho' + s][0], 1) for s in 'NF'}
    m['lean_deg'] = round(math.degrees(math.atan2(J['neck'][0] - hip[0], hip[1] - J['neck'][1])), 1)
    m['neck_x'] = round(J['neck'][0] - hip[0], 1)
    m['toe_x'] = None
    if m['lowest_px'] > BASELINE:
        errors.append(f'{tag}: lowest pixel at y={m["lowest_px"]}, nothing may be below the floor line {BASELINE}')
    if k == 3:
        m['clearance_px'] = BASELINE - m['lowest_px']
        if m['clearance_px'] < RUN['clear']:
            errors.append(f'{tag} (flight): the lowest pixel is {m["clearance_px"]} px above the floor (y={m["lowest_px"]}), a flight frame needs '
                          f'{RUN["clear"]} or more - both feet must be clearly off the ground')
        # scissor: the leg that pushed off in the frame before (the stance leg of this half) trails, the other one reaches forward
        p, o = ('N', 'F') if stance == 'leg_near' else ('F', 'N')
        m['scissor_px'] = round(m['ankle_x'][p] - m['ankle_x'][o], 1)
        if m['scissor_px'] > -RUN['scissor']:
            errors.append(f'{tag} (flight): the {"near" if p == "N" else "far"} ankle (the leg that just pushed off) is '
                          + (f'{m["scissor_px"]:.0f} px AHEAD of' if m['scissor_px'] > 0 else f'{-m["scissor_px"]:.0f} px behind')
                          + f' the other one, it must trail by {RUN["scissor"]} or more - legs scissored, the pushing leg behind '
                          '(wrong frame order or the legs swapped?)')
        return
    if lows[stance] != BASELINE:
        errors.append(f'{tag}: the stance leg ({stance}) ends at y={lows[stance]}, not on the floor line {BASELINE}')
    else:
        band = fr[stance][BASELINE - SOLE_BAND:BASELINE + 1, :, 3] > 0
        m['toe_x'] = round(float(np.nonzero(band.any(0))[0].max()) - hip[0], 1)
    if BASELINE - lows[swing] < RUN['other']:
        errors.append(f'{tag}: the other leg ({swing}) is {BASELINE - lows[swing]} px above the floor, a run has ONE foot down '
                      f'(at least {RUN["other"]} px; both feet on the floor is a walk)')


def run_cycle(meas, want_step, errors, warns, info):
    """the run rules that compare frames (SPEC section 5b)"""
    want = float(want_step or RUN['step'])
    steps = []
    for half, side in ((0, 'N'), (4, 'F')):
        toes = [meas[half + k]['toe_x'] for k in range(3)]
        name = 'near' if side == 'N' else 'far'
        if any(t is None for t in toes):
            continue                                   # the stance leg is not on the floor: reported per frame
        step = 2 * (toes[0] - toes[2])
        steps.append(step)
        info.append(f'planted {name} toe x (front of the sole, from the hip): ' + ' -> '.join(f'{x:.0f}' for x in toes)
                    + f' -> step {step:.0f} px (step/4 = {step / 4:.1f})')
        for k in range(2):
            d = toes[k] - toes[k + 1]
            if abs(d - step / 4) > 3:
                errors.append(f'R{half + k + 1}->R{half + k + 2}: planted toe moves back {d:.1f} px, must be {step / 4:.1f} +-3 '
                              '(the body travels step/4 per frame: the foot would slide)')
        if abs(step - want) > RUN['step_tol']:
            errors.append(f'R{half + 1}-R{half + 3}: step {step:.1f} px, must be {want:.0f} +-{RUN["step_tol"]} '
                          f'(the request; a different stride needs a new runStride and a new request)')
    if steps:
        s = sum(steps) / len(steps)
        info.append(f'step (body travel per step = 2 x the toe retreat R1->R3): {" / ".join(f"{v:.0f}" for v in steps)} px '
                    f'(= {s * SCALE:.1f} game px, the sheet\'s runStride)')
    # R(i+4) is R(i) with the legs swapped
    for k in range(4):
        a, b = meas[k], meas[k + 4]
        if abs(a['hip_height_px'] - b['hip_height_px']) > 1:
            errors.append(f'R{k + 1}/R{k + 5}: hip height {a["hip_height_px"]} vs {b["hip_height_px"]} px (mirror halves must match +-1)')
        for s, o in (('N', 'F'), ('F', 'N')):
            if abs(a['ankle_x'][s] - b['ankle_x'][o]) > 2:
                errors.append(f'R{k + 1}/R{k + 5}: ankle x {a["ankle_x"][s]} vs {b["ankle_x"][o]} px (mirror halves must match +-2)')
            if abs(a['ankle_y'][s] - b['ankle_y'][o]) > 4:
                errors.append(f'R{k + 1}/R{k + 5}: ankle {a["ankle_y"][s]} vs {b["ankle_y"][o]} px below the hip (mirror halves must match +-4)')
    hips = [m['hip_height_px'] for m in meas]
    bob = max(hips) - min(hips)
    info.append('hip height: ' + ' '.join(f'{v:.0f}' for v in hips) + f' -> bob {bob:.1f} px ({bob * SCALE:.1f} game px)')
    if not RUN['bob'][0] <= bob <= RUN['bob'][1]:
        warns.append(f'bob {bob:.1f} px, SPEC asks {RUN["bob"][0]}-{RUN["bob"][1]} (about 9% of the height: less reads as a fast walk, more as jumping)')
    for half in (0, 4):
        hh = hips[half:half + 4]
        if hh.index(min(hh)) != 1 or hh.index(max(hh)) != 3:
            errors.append(f'R{half + 1}-R{half + 4}: the hip must be lowest at down and highest in flight, got {hh}')
    clear = [meas[i].get('clearance_px') for i in (3, 7)]
    info.append(f'flight clearance (lowest pixel above the floor): R4 {clear[0]} px, R8 {clear[1]} px; other foot in the stance frames: '
                + ' '.join(str(meas[i]['sole_height_px']['F' if i < 4 else 'N']) for i in (0, 1, 2, 4, 5, 6)) + ' px')
    el = [v for m in meas for v in m['elbow_flex_deg'].values()]
    info.append(f'elbow flex {min(el):.0f}-{max(el):.0f} deg, lean {min(m["lean_deg"] for m in meas):.1f}-{max(m["lean_deg"] for m in meas):.1f} deg, '
                f'neck x {min(m["neck_x"] for m in meas):.0f}-{max(m["neck_x"] for m in meas):.0f} px ahead of the hip')
    for m in meas:
        for s in 'NF':
            v = m['elbow_flex_deg'][s]
            if not RUN['elbow'][0] <= v <= RUN['elbow'][1]:
                warns.append(f'{m["frame"]}: the {"near" if s == "N" else "far"} elbow is bent {v:.0f} deg, a run keeps it at '
                             f'{RUN["elbow"][0]}-{RUN["elbow"][1]} (near 90) all the way round')
        if not RUN['lean'][0] <= m['lean_deg'] <= RUN['lean'][1]:
            warns.append(f'{m["frame"]}: torso lean {m["lean_deg"]:.1f} deg (hip to neck), SPEC asks {RUN["lean"][0]}-{RUN["lean"][1]} (the walk has 8-11)')
    leans = [m['lean_deg'] for m in meas]
    if max(leans) - min(leans) > RUN['lean_range']:
        warns.append(f'lean changes by {max(leans) - min(leans):.1f} deg over the cycle, SPEC asks {RUN["lean_range"]} or less (the head must not peck)')
    necks = [m['neck_x'] for m in meas]
    if max(necks) - min(necks) > RUN['neck']:
        warns.append(f'the neck travels {max(necks) - min(necks):.0f} px forward and back, SPEC asks {RUN["neck"]} or less (the head must not peck)')
    pump = []
    for i in (2, 3, 6, 7):
        m, s, o = meas[i], 'NF'[i // 4], 'FN'[i // 4]
        d = m['hand_from_shoulder_px'][s] - m['hand_from_shoulder_px'][o]
        pump.append(d)
        if d < 0:
            errors.append(f'{m["frame"]} ({m["phase"]}): the {"near" if s == "N" else "far"} hand is {-d:.0f} px BEHIND the other one (each from its '
                          'shoulder) - the arm of the pushing leg must be forward: the arms pump the wrong way (arms or frames swapped?)')
        elif d < RUN['pump']:
            warns.append(f'{m["frame"]} ({m["phase"]}): the {"near" if s == "N" else "far"} hand is {d:.0f} px ahead of the other one (each from its '
                         f'shoulder), SPEC asks {RUN["pump"]} or more - the arm of the pushing leg is forward, the other one back')
    info.append('arm pump at push-off/flight (hand of the pushing side ahead of the other, from the shoulders): ' + ' '.join(f'{d:.0f}' for d in pump) + ' px')
    for i, s in ((2, 'N'), (6, 'F')):
        v = meas[i]['knee_flex_deg'][s]
        if v > RUN['push_flex']:
            warns.append(f'R{i + 1} (push-off): the pushing knee is bent {v:.0f} deg, SPEC asks {RUN["push_flex"]} or less (the leg extends behind the body)')
    for i, s in ((1, 'N'), (5, 'F')):
        v = meas[i]['knee_flex_deg'][s]
        if not RUN['down_flex'][0] <= v <= RUN['down_flex'][1]:
            warns.append(f'R{i + 1} (down): the supporting knee is bent {v:.0f} deg, SPEC asks {RUN["down_flex"][0]}-{RUN["down_flex"][1]} '
                         '(compression carries the weight; less reads as a skipping walk)')
    for i, s in ((0, 'N'), (4, 'F')):
        v = meas[i]['ankle_x'][s]
        if not RUN['land'][0] <= v <= RUN['land'][1]:
            warns.append(f'R{i + 1} (contact): the landing ankle is {v:.0f} px ahead of the hip, SPEC asks {RUN["land"][0]}-{RUN["land"][1]} '
                         '(a little ahead of the body, knee bent)')
    info.append('flight scissor (ankle of the leg that pushed off minus the other one, from the hip): '
                + ' '.join(f'R{i + 1} {meas[i]["scissor_px"]:.0f}' for i in (3, 7)) + f' px (must be -{RUN["scissor"]} or less)')


def strip_rules(flats, work, errors, warns, info):
    """run sets: the two strips against tools/art/check_delivery.py (size, flat key colour, colour distance, gaps, four poses),
    with pose 4 as the flight frame (check_delivery --flight-slots 4: 18 px or more above y=870 instead of on it)"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import check_delivery
    os.makedirs(work, exist_ok=True)
    for k, s in enumerate('ab'):
        path = os.path.join(work, f'strip_{s}.png')
        Image.fromarray(np.concatenate([flats[k * 4 + j][0] for j in range(4)], axis=1), 'RGB').save(path)
        e, w_, inf = check_delivery.check_png(path, '1x4', None, flight=(4,))
        errors += [f'strip {s} (check_delivery --flight-slots 4): {msg}' for msg in e]
        warns += [f'strip {s} (check_delivery --flight-slots 4): {msg}' for msg in w_]
        info += [f'strip {s} (check_delivery --flight-slots 4): {msg}' for msg in inf if '(flight)' in msg]


def export(flats, durs, out, name):
    os.makedirs(out, exist_ok=True)
    for k, s in enumerate('ab'):
        strip = np.concatenate([flats[k * 4 + j][0] for j in range(4)], axis=1)
        Image.fromarray(strip, 'RGB').save(os.path.join(out, f'{name}_{s}.png'))
    small = []
    for rgb, _ in flats:
        cell = Image.fromarray(rgb, 'RGB').crop((0, BASELINE - 500, SLOT, BASELINE + 12))
        cell = cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX)
        small.append(cell.resize((cell.width * 4, cell.height * 4), Image.NEAREST))
    small[0].save(os.path.join(out, f'{name}_preview.gif'), save_all=True, append_images=small[1:], duration=durs, loop=0, disposal=1)


def compare(frames, base, warns, T='W'):
    """what changed against the draft, per frame and layer; warns when a limb was repainted but none of its joint dots moved
    (a small shift keeps the dot on the limb, so the measurements would silently describe the old pose)"""
    lines = []
    for i, (a, b) in enumerate(zip(frames, base)):
        ch = []
        if 'joints' in a and 'joints' in b and a['joints'].shape == b['joints'].shape:
            ja, jb = dots(a['joints'])[0], dots(b['joints'])[0]
            for ln in BODY:
                if ln in a and ln in b and a[ln].shape == b[ln].shape and int(np.any(a[ln] != b[ln], axis=-1).sum()) >= 150:
                    mine = [j for j, part in PART_OF.items() if part == ln and j in ja and j in jb]
                    if mine and all(dist(ja[j], jb[j]) < 0.75 for j in mine):
                        warns.append(f'{T}{i + 1}: {ln} was repainted but its joint dots ({", ".join(mine)}) did not move - '
                                     'move the dots with the limb, or say in NOTES that only the outline changed')
        for ln in a:
            if ln == 'Background':
                continue
            if ln not in b:
                ch.append(f'{ln} new')
            elif a[ln].shape != b[ln].shape:
                ch.append(f'{ln} resized')
            else:
                d = int(np.any(a[ln] != b[ln], axis=-1).sum())
                if d:
                    ch.append(f'{ln} {d}px')
        lines.append(f'{T}{i + 1}: ' + (', '.join(ch) if ch else 'unchanged'))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', help='SET.aseprite, or a folder of W<n>_<layer>.png (run sets: R<n>_<layer>.png)')
    ap.add_argument('--pose', help='pose.json of the request (bone lengths); default: the lengths of SPEC section 6')
    ap.add_argument('--base', help='the draft .aseprite (or layers folder) this was refined from: list what changed')
    ap.add_argument('--export', help='write <set>_a.png, <set>_b.png, <set>_preview.gif and pose_measured.json here')
    ap.add_argument('--name', help='set name for --export (default: the file name)')
    ap.add_argument('--gait', choices=('walk', 'run'), help='which rules to apply. Default: "gait" of --pose pose.json, else run for a folder '
                                                            'of R<n>_ files or a file named run_*, else walk')
    ap.add_argument('--aseprite-exe', default=os.environ.get('ASEPRITE_PATH') or (HEADLESS if os.path.exists(HEADLESS) else 'aseprite'))
    a = ap.parse_args(argv)
    bones = dict(DEFAULT_BONES)
    request = {}
    if a.pose:
        with open(a.pose, encoding='utf-8') as f:
            request = json.load(f)
        bones.update(request.get('bones_px', {}))
    gait = a.gait or request.get('gait') or ('run' if dir_prefix(a.src) == 'R' or os.path.basename(os.path.normpath(a.src)).startswith('run_') else 'walk')
    if gait not in ('walk', 'run'):
        print(f'FAIL: {a.pose}: unknown gait "{gait}" (walk or run)')
        return 1
    with tempfile.TemporaryDirectory(prefix='skeleton-') as tmp:
        def load(src, sub):
            return load_dir(src) if os.path.isdir(src) else load_aseprite(src, a.aseprite_exe, os.path.join(tmp, sub))
        try:
            frames, durs, names, hidden = load(a.src, 'new')
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
            print(f'FAIL: cannot read {a.src}: {e}')
            return 1
        errors, warns, info, meas, flats = check(frames, durs, names, hidden, bones, gait,
                                                 request.get('step_px') if request.get('gait') == 'run' else None,
                                                 request.get('nominal_ms') if request.get('gait', 'walk') == gait else None)
        if gait == 'run' and len(flats) == 8 and all(m is not None for m in meas):
            strip_rules(flats, os.path.join(tmp, 'strips'), errors, warns, info)
        name = a.name or os.path.splitext(os.path.basename(os.path.normpath(a.src)))[0]
        print(f'# skeleton {name}' + (' (run)' if gait == 'run' else ''))
        for ln in info:
            print('- ' + ln)
        if a.base:
            try:
                print('- changed against the draft:')
                for ln in compare(frames, load(a.base, 'base')[0], warns, 'R' if gait == 'run' else 'W'):
                    print('    ' + ln)
            except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
                warns.append(f'could not read the draft {a.base}: {e}')
        for w in warns:
            print('WARN: ' + w)
        for e in errors:
            print('FAIL: ' + e)
        if a.export and len(flats) == 8:
            export(flats, durs, a.export, name)
            with open(os.path.join(a.export, 'pose_measured.json'), 'w', encoding='utf-8') as f:
                json.dump(dict(set=name, source=os.path.basename(a.src), baseline=BASELINE, scale=SCALE, durations_ms=durs, frames=meas), f,
                          ensure_ascii=False, indent=1)
                f.write('\n')
            print(f'- exported strips, preview and pose_measured.json to {a.export} ' + (
                '(run check_delivery.py on the two strips)' if gait == 'walk' else
                '(the strip rules of check_delivery.py are applied above; on its own run it with --flight-slots 4)'))
        print('RESULT: ' + ('FAIL' if errors else 'PASS' + (f' ({len(warns)} warning(s))' if warns else '')))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
