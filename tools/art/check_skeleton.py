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
      rotation), the head's tilt ranging over more than 8 deg across the frames (a nod; for a nearly round head, whose shape gives no
      rotation, the angle of its centre around the neck dot is the tilt), a frame duration that differs from pose.json nominal_ms
      (walk 120, run 80 when no pose.json is given).
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

ATTACK / HIT / IDLE mannequin sequences (SPEC section 10; set id <atk|hit|idle>__<sheet stem without sheet_>):
  python3 tools/art/check_skeleton.py SET.aseprite --motion attack|hit|idle --set <set id> [--idle IDLE_SET.aseprite] [--export DIR]
The frames, ms, contact / hold / cut and the numbers come from tools/art/specs/motion_bible.json (the set's archetype, hit weight or
idle) and motion_chars.json (timing.ms, hit.sheets, mannequin.pivot_foot). The frames are in world coordinates: floor y=870, the
planted foot stays put, the hip moves (only an idle set's rest frame is pinned to hip x=192). --motion defaults from a set id /
file name starting atk__ / hit__ / idle__. --export writes f<NN>_<name>.png per frame, <set>_preview.gif and pose_measured.json.
FAIL (all): frame count, durations or tags (one tag named after the motion over all frames; a tag named after a bible frame on that
      frame) differ from the bible, the shared layer / dot / bone / crisp-edge rules, both feet off y=870 in a frame, the picture
      touching the frame edge, neighbouring frames that are pixel copies (idle: WARN).
  attack: the pivot foot (pivot_foot; default: at least one foot) sliding - in a frame its toe end and heel end (the sole in rows
      y=866-870) and its ankle dot all more than 3 px from the span's first frame (a heel lift on the toe passes); melee: the
      head (from the ankles' mid-point) not behind at the hold and ahead at the contact or travelling under 100 px, the hip under
      55 px; no contact on the contact frame (a blade turning one way swing -> contact -> follow, 10 deg or more into the contact -
      with a shield shove at the contact 25 deg or more in all, else it is carried along, not a cut - or the tip / shield face at
      its unique furthest reach); a cut turning under 120 deg hold -> follow, a thrust tip under 165 px; a cut's follow more than
      10 deg over the bible's weapon_past_line_deg maximum past the contact (25-40: over 50 = the contact frame is still mid-arc);
      swing -> contact silhouette change under 15 %; recover not closer to the first frame than the follow. Blade angle: grip hand
      dot -> centroid of the weapon pixels at least half the farthest pixel's distance away. bow (bow hand = the hand dot nearest
      the bow layer's centroid): draw length (bow hand - string hand) under 100 px at the hold or not longest there, the release
      moving the string hand under 60 px back or not being its biggest move back.
  hit: a foot off y=870, an ankle more than 3 px off the idle height, the front foot moved, the back foot moved (light: 0..-33 px),
      the front knee more than 1 px above the idle, lean back over 15 deg; at K1 / K2 a hip drop outside 12-30 px or a head
      displacement outside the weight's band (heavy 12-35, mid 25-60, light 40-90 px), K2 not deeper than K1; the frame after the
      peak not closer to the idle. The idle is the bible's idle_reference on the posekit mannequin standing on K1's feet, its hip
      0.05 head ahead of their mid-point (--idle: the rest frame of the character's idle set).
  idle: the rest hip off x=192 +-1, a foot moving more than 2 px, a loop that does not close (last -> first more than the biggest
      step + 1 px or twice the first step + 1 px; silhouette the same + 2 %).
WARN: the picture outside x=32-351; neighbouring silhouettes under 8 % at game size (pairs with the hold frame and idle exempt); the
      head tilting over 8 deg against the torso (round head: by angle) or its centre's distance from the neck dot changing over 4 px
      (hit 10); attack: follow-through outside weapon_past_line_deg (25-40) past the contact (or the hip falling back), contact ->
      follow over 35 %, weapon under 60 % clear of the body
      or its tip within 33 px of it, a shield shove under 55 px, the bow hand moving at the release, a leaning archer, settle not
      closer than recover, kinds without rules here (gun, cast, creature); hit: later recovery frames, last frame over 12 px from
      the idle, without --idle the idle reference's hip off x=192 +-3 (the stance is off the idle column); idle: a joint moving
      over 12 px, no motion, neighbours with the same joints.
"""
import argparse
from collections import Counter
import json
import math
import os
import re
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
HEAD_TILT = 8          # deg the head's tilt may range over the cycle (max - min; drafts: run 1.0, walk under 5)
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
    """the head against the neck dot over the cycle. A small tilt about the neck is allowed: the head's own rotation (from its
    shape) is taken out, the rest is drift (a head that pecks or slides on the neck); the tilt itself may range over HEAD_TILT deg
    (more is a nod). A nearly round head gives no usable rotation: then the drift is the change of its distance from the neck and
    the tilt is the angle of its centre around the neck dot (so a round head cannot slide round the neck unseen)."""
    hp = [m.get('head') for m in meas]
    if any(h is None for h in hp):
        return
    hp = [(tuple(h['from_neck_px']), h['axis_rad'], h['elongation']) for h in hp]
    (c0x, c0y), th0, _ = hp[0]
    round_head = min(h[2] for h in hp) < 1.08
    drift, tilts = [], []
    for (cx, cy), th, _ in hp:
        if round_head:
            dt = (math.atan2(cy, cx) - math.atan2(c0y, c0x) + math.pi) % (2 * math.pi) - math.pi
        else:
            dt = (th - th0 + math.pi / 2) % math.pi - math.pi / 2
        tilts.append(math.degrees(dt))
        px, py = c0x * math.cos(dt) - c0y * math.sin(dt), c0x * math.sin(dt) + c0y * math.cos(dt)
        drift.append(abs(math.hypot(cx, cy) - math.hypot(c0x, c0y)) if round_head else math.hypot(cx - px, cy - py))
    span = max(tilts) - min(tilts)
    info.append('head against the neck dot (after its own tilt' + (', round head: distance, tilt = angle around the neck' if round_head else '')
                + '): drift ' + ' '.join(f'{d:.1f}' for d in drift) + f' px, tilt {min(tilts):+.1f}..{max(tilts):+.1f} deg from {T}1'
                + f' (range {span:.1f}, SPEC asks {HEAD_TILT} or less)')
    for i, d in enumerate(drift):
        if d > HEAD_DRIFT:
            warns.append(f'{T}{i + 1}: the head layer sits {d:.1f} px off its {T}1 place against the neck dot (after its tilt), SPEC asks '
                         f'{HEAD_DRIFT} or less - the head pecks or slides on the neck (move it with the torso, or tilt it about the neck)')
    if span > HEAD_TILT:
        lo, hi = tilts.index(min(tilts)), tilts.index(max(tilts))
        warns.append(f'the head tilts over {span:.1f} deg across the frames ({T}{lo + 1} {tilts[lo]:+.1f}, {T}{hi + 1} {tilts[hi]:+.1f} deg from {T}1'
                     + (', round head: angle of its centre around the neck dot' if round_head else '')
                     + f'), SPEC asks {HEAD_TILT} or less - the head nods (keep it near level, it moves with the torso)')


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


# ───────── attack / hit / idle mannequin sets (SPEC section 10; motion_bible.json + motion_chars.json) ─────────
# A set id is <motion prefix>__<sheet stem without 'sheet_'>: atk__class_warrior, hit__captain_shadowqueen, idle__class_warrior.
# The frames are in WORLD coordinates: the floor is y=870 in every frame and the planted feet stay where they stand, the hip
# moves (it is not pinned to x=192 as in the walk / run cycles; an idle set's rest frame defines the column, hip x=192).
SPECS = os.path.join(ROOT, 'tools', 'art', 'specs')
MOTION_PREFIX = dict(attack='atk', hit='hit', idle='idle')
PREFIX_MOTION = {v: k for k, v in MOTION_PREFIX.items()}
MOTION_KINDS = ('melee_swing', 'melee_thrust', 'bow')     # checks_by_kind entries with kind rules here (gun / cast / creature: common rules only)
EDGE_BAND = 32           # the picture stays inside x=32..351 of its frame (the strips keep 32 px of magenta at the borders)
PIVOT_TOL = 3            # px a planted foot may move (motion_bible checks_by_kind pivot_foot_tol_src_px)
FEET_FLAT_TOL = 3        # hit: ankle height within +-3 px of the idle's (feet_flat "soles at y=870 +-3, no foot angle")
HIT_HEAD_DRIFT = 10      # hit: the head may move against the neck by HIT_KEYS head_off (up to 0.05 head = 5.5 px) plus HEAD_DRIFT
IDLE_MOVE = 12           # idle: a breathing frame moves 1-2 game px (= 12 src px) at most
CHAIN = ('hipN', 'hipF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'shoN', 'shoF', 'elbN', 'elbF', 'handN', 'handF', 'neck')
BODY_JOINTS = ('hipN', 'hipF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'shoN', 'shoF', 'neck')
WEAPON_LAYERS = ('weapon_front', 'weapon_back', 'shield')
BLADE_FAR = 0.5          # the blade angle is measured from the grip hand to the centroid of the weapon pixels at least this fraction of
                         # the farthest pixel's distance away (the far half of the weapon): a wide head does not jump the angle
CROSS_MIN = 10           # deg a blade turns swing -> contact (one way on into the follow) for the contact to be a crossing of its strike line
SHOVE_SLASH_MIN = 25     # deg: when the contact is a shield shove, a blade must turn this much one way swing -> contact -> follow to be a cut too
PAST_FAIL_OVER = 10      # deg over the bible's weapon_past_line_deg maximum: a follow this far past the contact means the contact frame
                         # is still mid-arc (the strike line is crossed a frame late) -> FAIL (bible 25-40 -> over 50 fails)
HIT_COLUMN_TOL = 3       # hit without --idle: the idle reference's hip x (built on K1's feet) within x=192 +-3, else WARN


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def parse_pivot(text, names):
    """motion_chars.json mannequin.pivot_foot -> [(side 'N'|'F'|'NF', first frame index, last frame index)] or None (no rule:
    at least one foot fixed through the whole sequence). 'rear (footN) ...', 'front (footF) from the swing frame on - ...; rear
    before', 'both planted ...'."""
    if not text:
        return None
    t = text.lower()
    n = len(names)
    if t.startswith('both'):
        return [('NF', 0, n - 1)]
    m = re.match(r'\s*(rear|front)\b[^;]*?\(foot([nf])\)', t)
    if not m:
        return None
    side = m.group(2).upper()
    other = 'F' if side == 'N' else 'N'
    f = re.search(r'from the (\w+) frame on', t)
    if f and f.group(1) in names:
        k = names.index(f.group(1))
        spans = [(side, k, n - 1)]
        if k > 0 and re.search(r'\b(rear|front) before\b', t):
            spans.insert(0, (other, 0, k - 1))
        return spans
    return [(side, 0, n - 1)]


def motion_spec(motion, set_id, bible_path, chars_path):
    """the bible entry a set is checked against -> (spec dict, problems). spec: motion, set, sheet, arch, kind, weight, names, ms,
    contact, hold, cut, loop, keys (frames with joint targets), checks, pivot, char"""
    problems = []
    m = re.match(r'^(atk|hit|idle)__(.+)$', set_id or '')
    if not m:
        return None, [f'set id "{set_id}" is not <atk|hit|idle>__<sheet stem without sheet_> (e.g. atk__class_warrior; SPEC section 10)']
    if PREFIX_MOTION[m.group(1)] != motion:
        problems.append(f'set id "{set_id}" is a {PREFIX_MOTION[m.group(1)]} set but --motion is {motion}')
    stem = m.group(2)
    if '_' not in stem:
        return None, problems + [f'set id "{set_id}": "{stem}" is not a sheet stem <kind>_<key> (class_warrior, captain_ironwall)']
    kind_, key = stem.split('_', 1)
    sheet = f'sheet/{kind_}/{key}'
    bible, chars = read_json(bible_path), read_json(chars_path)
    char = chars.get('chars', {}).get(sheet)
    arch = char.get('arch') if char else None
    if not arch:
        arch = next((a for a, v in bible['archetypes'].items() if sheet in v.get('users', [])), None)
    if not arch or arch not in bible['archetypes']:
        return None, problems + [f'{sheet}: no archetype (not in motion_chars.json chars and in no motion_bible.json archetypes.*.users)']
    A = bible['archetypes'][arch]
    spec = dict(motion=motion, set=set_id, sheet=sheet, arch=arch, char=char, kind=None, weight=None, checks={}, pivot=None, keys=[])
    if motion == 'attack':
        if 'attack' not in A:
            return None, problems + [f'archetype {arch} has no attack sequence in motion_bible.json']
        E = A['attack']
        spec['kind'] = A.get('checks')
        spec['checks'] = bible.get('checks_by_kind', {}).get(spec['kind'], {})
        over = ((char or {}).get('timing') or {}).get('ms') or {}
        spec['ms'] = [over.get(f['name'], f['ms']) for f in E['frames']]
        spec['contact'], spec['hold'], spec['cut'] = E.get('contact'), E.get('hold'), E.get('cut')
        # follow-through past the strike line: the archetype's own frames.*.joints.weapon_past_line_deg, else the first one in the bible
        spec['past'] = None
        for a_, v in [(arch, A)] + [(k, x) for k, x in bible['archetypes'].items() if k != arch]:
            for f in (v.get('attack') or {}).get('frames', []):
                p = (f.get('joints') or {}).get('weapon_past_line_deg')
                if p and spec['past'] is None:
                    spec['past'] = (float(p[0]), float(p[1]), f'archetypes.{a_}.attack.{f["name"]}.joints.weapon_past_line_deg')
        if char and (char.get('mannequin') or {}).get('pivot_foot'):
            spec['pivot'] = parse_pivot(char['mannequin']['pivot_foot'], [f['name'] for f in E['frames']])
    elif motion == 'hit':
        w = chars.get('hit', {}).get('sheets', {}).get(sheet) or A.get('hit_default')
        if w not in bible['hit']['weights']:
            return None, problems + [f'{sheet}: no hit weight (motion_chars.json hit.sheets or archetype hit_default)']
        E = bible['hit']['weights'][w]
        spec['weight'], spec['checks'] = w, E['checks']
        spec['ms'] = [f['ms'] for f in E['frames']]
        spec['contact'], spec['cut'] = E.get('contact'), E.get('cut')
        spec['hold'] = next((i for i, f in enumerate(E['frames']) if f['name'].endswith(' hold')), None)
        spec['keys'] = [i for i, f in enumerate(E['frames']) if 'joints' in f and 'hip' in f['joints']]
        spec['idle_reference'] = bible['hit']['idle_reference']
    else:
        E = bible['idle']['flyer' if arch == 'flyer' else 'humanoid']
        spec['ms'] = [f['ms'] for f in E['frames']]
        spec['contact'] = spec['hold'] = spec['cut'] = None
    spec['names'] = [f['name'] for f in E['frames']]
    spec['loop'] = bool(E.get('loop'))
    spec['exempt'] = list(bible['rules'].get('neighbour_exempt', ['idle', 'hold']))
    spec['neighbour_min'] = 100.0 * bible['rules'].get('neighbour_silhouette_change_min', 0.08)
    return spec, problems


def load_tags(src, exe, work):
    """-> [(name, from, to)] frame tags of an .aseprite (0-based, inclusive)"""
    os.makedirs(work, exist_ok=True)
    data = os.path.join(work, 'tags.json')
    run(exe, src, '--list-tags', '--sheet', os.path.join(work, 'tags.png'), '--data', data, '--format', 'json-array')
    with open(data, encoding='utf-8') as f:
        return [(t['name'], int(t['from']), int(t['to'])) for t in json.load(f).get('meta', {}).get('frameTags', [])]


def weapon_geom(fr, J):
    """per weapon layer present: pixel count, front-most x, centroid, and per hand dot the nearest / farthest pixel and the centroid
    of the far half (pixels at least BLADE_FAR of the farthest distance away) -> filled into grip / tip / angle later"""
    out = {}
    for ln in WEAPON_LAYERS:
        if ln not in fr:
            continue
        ys, xs = np.nonzero(fr[ln][..., 3] > 0)
        if not len(xs):
            continue
        g = dict(n=int(len(xs)), front=int(xs.max()), low=int(ys.max()), centroid=(float(xs.mean()), float(ys.mean())))
        for s in 'NF':
            d = np.hypot(xs - J['hand' + s][0], ys - J['hand' + s][1])
            g['near_' + s] = float(d.min())
            k = int(d.argmax())
            g['tip_' + s] = (int(xs[k]), int(ys[k]))
            far = d >= BLADE_FAR * d[k]
            g['far_' + s] = (float(xs[far].mean()), float(ys[far].mean()))
            g['to_centroid_' + s] = float(math.hypot(g['centroid'][0] - J['hand' + s][0], g['centroid'][1] - J['hand' + s][1]))
        out[ln] = g
    return out


def grow(mask, r):
    for _ in range(r):
        mask = grow1(mask)
    return mask


def unwrap(angles):
    out = [angles[0]]
    for a in angles[1:]:
        out.append(out[-1] + ((a - out[-1] + 180) % 360 - 180))
    return out


def joint_dist(a, b, keys=CHAIN):
    return sum(dist(a[k], b[k]) for k in keys) / len(keys)


def build_idle_ref(ankN_x, ankF_x, ir):
    """the idle of motion_bible.json hit.idle_reference (hip (0, 1.40) head, lean 0.08, feet -1.10 / 1.00) built on the posekit
    mannequin with its feet where the hit set's K1 feet stand (a hit's K1 keeps the idle stance) and its hip 0.05 head (the bible
    idle's offset, not scaled with the stance) ahead of their mid-point, measured like a set frame. -> {joints, hip, hip_h, head}"""
    import posekit as pk
    import walk8
    B = pk.Body(4.0)
    oy = walk8.floor_row(B, 1.30)
    fN, fF = ir.get('footN', -1.10), ir.get('footF', 1.00)
    width = (ankF_x - ankN_x) / HEAD_PX
    ahead = -(fN + fF) / 2                                    # the bible idle's hip ahead of its ankles' mid-point (+0.05 head = 5.5 px)
    feet = (-width / 2 - ahead, width / 2 - ahead)            # the set's stance; the hip that far ahead of its mid-point, not scaled with
                                                              # the width (a narrow stance keeps the body's weight where the idle has it)

    def make(lift):
        return dict(hip=tuple(ir.get('hip', (0.0, 1.40))), lean=ir.get('lean', 0.08), tilt=0.0, footN=(feet[0], B.ank + lift[0]),
                    footF=(feet[1], B.ank + lift[1]), toeN=0.85, faN=0, faF=0, handN=('p', -0.45, 1.05), handF=('p', 0.40, 1.05),
                    elbN=(-0.3, 1.0), elbF=(0.3, 1.0))
    _, J, parts = walk8.settle(make, B, oy, ('N', 'F'), 2, 'idle reference')
    layers, _ = walk8.frame_layers(parts, J, oy)
    dx = ankN_x - (SLOT / 2 + feet[0] * HEAD_PX)
    D, _ = dots(np.asarray(layers['joints']))
    D = {k: (v[0] + dx, v[1]) for k, v in D.items()}
    head = np.asarray(layers['head'])[..., 3] > 0
    ys, xs = np.nonzero(head)
    hip = ((D['hipN'][0] + D['hipF'][0]) / 2, (D['hipN'][1] + D['hipF'][1]) / 2)
    return dict(joints=D, hip=hip, hip_h=BASELINE - hip[1], head=(float(xs.mean()) + dx, float(ys.mean())), source='posekit idle_reference')


def frame_ref(fr, names, label):
    """an idle reference from the rest frame of an idle set (--idle): {joints, hip, hip_h, head}"""
    D, bad = dots(fr['joints'])
    if bad:
        raise RuntimeError(f'{label}: ' + '; '.join(bad))
    ys, xs = np.nonzero(fr['head'][..., 3] > 0)
    hip = ((D['hipN'][0] + D['hipF'][0]) / 2, (D['hipN'][1] + D['hipF'][1]) / 2)
    return dict(joints=D, hip=hip, hip_h=BASELINE - hip[1], head=(float(xs.mean()), float(ys.mean())), source=label)


def head_tilt_motion(meas, T, warns, info, drift_max):
    """the head against the neck over the sequence (SPEC 6: tilt range <= 8 deg, round head by angle) - relative to the torso,
    because an attack or a hit turns the whole torso on purpose: the head's own rotation minus the torso's (hip -> neck) rotation.
    The drift is the change of the head centre's distance from the neck dot only (the head swinging round the neck with the lean is
    not a slide; walk / run keep head_cycle's rotate-then-compare drift)."""
    hp = [(tuple(m['head']['from_neck_px']), m['head']['axis_rad'], m['head']['elongation']) for m in meas]
    (c0x, c0y), th0, _ = hp[0]
    round_head = min(h[2] for h in hp) < 1.08
    tilts, drift = [], []
    for m, ((cx, cy), th, _) in zip(meas, hp):
        if round_head:
            dt = (math.atan2(cy, cx) - math.atan2(c0y, c0x) + math.pi) % (2 * math.pi) - math.pi
        else:
            dt = (th - th0 + math.pi / 2) % math.pi - math.pi / 2
        drift.append(abs(math.hypot(cx, cy) - math.hypot(c0x, c0y)))
        tilts.append(math.degrees(dt) - (m['lean_deg'] - meas[0]['lean_deg']))
    span = max(tilts) - min(tilts)
    info.append('head against the torso (its own rotation minus the hip->neck rotation' + (', round head: angle around the neck' if round_head else '')
                + f'): tilt {min(tilts):+.1f}..{max(tilts):+.1f} deg from {meas[0]["frame"]} (range {span:.1f}, SPEC asks {HEAD_TILT} or less); '
                'drift (head centre to neck dot distance against ' + meas[0]['frame'] + ') ' + ' '.join(f'{d:.1f}' for d in drift) + ' px')
    if span > HEAD_TILT:
        lo, hi = tilts.index(min(tilts)), tilts.index(max(tilts))
        warns.append(f'the head tilts over {span:.1f} deg against the torso ({meas[lo]["frame"]} {tilts[lo]:+.1f}, {meas[hi]["frame"]} {tilts[hi]:+.1f} deg'
                     + (', round head: angle of its centre around the neck dot' if round_head else '')
                     + f'), SPEC asks {HEAD_TILT} or less - the head nods on the neck (turn it with the torso)')
    for m, d in zip(meas, drift):
        if d > drift_max:
            warns.append(f'{m["frame"]}: the head centre is {d:.1f} px nearer to / further from the neck dot than in {meas[0]["frame"]}, '
                         f'{drift_max} or less - the head slides on the neck (keep the chin on the neck)')


def check_motion(frames, durs, names, hidden, tags, bones, spec, idle_ref=None):
    """SPEC section 10: one attack / hit / idle mannequin sequence against its motion_bible.json entry"""
    errors, warns, info, meas = [], [], [], []
    motion, N = spec['motion'], spec['names']
    n, want_n = len(frames), len(N)
    lab = [f'f{i:02d} {N[i]}' if i < want_n else f'f{i:02d}' for i in range(n)]
    info.append(f'{motion} set {spec["set"]}: {spec["sheet"]}, archetype {spec["arch"]}' + (f', kind {spec["kind"]}' if spec['kind'] else '')
                + (f', hit weight {spec["weight"]}' if spec['weight'] else '') + '; frames ' + ' · '.join(f'{nm} {ms}' for nm, ms in zip(N, spec['ms']))
                + ' ms' + (f'; contact {N[spec["contact"]]}' if spec['contact'] is not None else '') + (f', hold {N[spec["hold"]]}' if spec['hold'] is not None else '')
                + (f', cut {N[spec["cut"]]}' if spec['cut'] is not None else ''))
    if n != want_n:
        errors.append(f'{n} frames, the {motion} sequence of {spec["arch"] if motion == "attack" else spec["weight"] or "idle"} has {want_n} '
                      f'({", ".join(N)}) - one Aseprite frame per sequence frame, in this order')
    h, w = next(iter(frames[0].values())).shape[:2]
    if (w, h) != (SLOT, SH_):
        errors.append(f'frame canvas {w}x{h}, expected {SLOT}x{SH_}')
    info.append(f'{n} frames, {w}x{h}, durations {durs} ms, layers: {" · ".join(names)}, tags: '
                + (', '.join(f'{t} {a + 1}-{b + 1}' for t, a, b in tags) or 'none'))
    for miss in [m for m in BODY + ('joints',) if m not in names]:
        errors.append(f'layer "{miss}" is missing')
    for odd in [m for m in names if m not in ORDER + ('Background', 'joints')]:
        errors.append(f'layer "{odd}" is not a SPEC section 4 name')
    for hid in [m for m in hidden if m != 'joints']:
        errors.append(f'layer "{hid}" is hidden: only joints may be hidden (a hidden layer is not in the exported picture)')
    present = [m for m in names if m in ORDER]
    if present != [m for m in ORDER if m in present]:
        warns.append(f'layer order {present} differs from SPEC section 4 (bottom to top: {" · ".join(m for m in ORDER if m in present)})')
    # tags: one tag named after the motion over the whole sequence; a tag named after a bible frame must sit on that frame
    whole = [t for t in tags if t[0] == motion]
    if not whole:
        errors.append(f'no frame tag "{motion}" - the sequence carries one tag named after its motion, frames 1-{want_n}'
                      + (f' (found: {", ".join(t[0] for t in tags)})' if tags else ''))
    elif (whole[0][1], whole[0][2]) != (0, n - 1):
        errors.append(f'tag "{motion}" covers frames {whole[0][1] + 1}-{whole[0][2] + 1}, it must cover the whole sequence 1-{n}')
    for t, a, b in tags:
        if t == motion:
            continue
        if t in N:
            if (a, b) != (N.index(t), N.index(t)):
                errors.append(f'tag "{t}" sits on frames {a + 1}-{b + 1}, the bible puts {t} on frame {N.index(t) + 1} (wrong frame order?)')
        else:
            warns.append(f'tag "{t}" is neither the motion ("{motion}") nor a frame name of the bible ({", ".join(N)})')
    if errors:
        return errors, warns, info, meas, []
    if 'joints' not in hidden:
        errors.append('layer "joints" is visible: hide it (the dots would be in the exported frames)')
    odd_ms = [f'{lab[i]} {d} (bible {spec["ms"][i]})' for i, d in enumerate(durs) if d != spec['ms'][i]]
    if odd_ms:
        errors.append('frame durations differ from the bible (+ the character\'s timing.ms): ' + ', '.join(odd_ms)
                      + ' ms - the engine plays these ms; a change is proposed in NOTES, not made in the file')
    flats = []
    for i, fr in enumerate(frames):
        tag = lab[i]
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
        m = dict(frame=tag, name=N[i] if i < want_n else None, ms=durs[i], joints={k: [round(v[0], 1), round(v[1], 1)] for k, v in J.items()})
        m['_J'] = J
        hip = ((J['hipN'][0] + J['hipF'][0]) / 2, (J['hipN'][1] + J['hipF'][1]) / 2)
        m['hip'] = (round(hip[0], 1), round(hip[1], 1))
        m['hip_height_px'] = round(BASELINE - hip[1], 1)
        m['lean_deg'] = round(math.degrees(math.atan2(J['neck'][0] - hip[0], hip[1] - J['neck'][1])), 1)
        head = fr['head'][..., 3] > 0
        hp = head_pose(head, J['neck'])
        if hp is None:
            errors.append(f'{tag}: the head layer is empty')
        else:
            ys_, xs_ = np.nonzero(head)
            m['head'] = dict(from_neck_px=[round(hp[0][0], 2), round(hp[0][1], 2)], axis_rad=round(hp[1], 4), elongation=round(hp[2], 3),
                             centre=[round(float(xs_.mean()), 1), round(float(ys_.mean()), 1)])
            if not (grow1(head) & (fr['torso'][..., 3] > 0)).any():
                errors.append(f'{tag}: the head layer does not touch the torso layer (a detached head: move it back onto the neck)')
        m['bones_px'] = {}
        for bone, a, b in BONES:
            for s in 'NF':
                d = dist(J[a + s], J[b + s])
                m['bones_px'][bone + s] = round(d, 1)
                if abs(d - bones[bone]) > 2:
                    errors.append(f'{tag}: {bone} ({"near" if s == "N" else "far"}) is {d:.1f} px, must be {bones[bone]} +-2')
        m['knee_flex_deg'] = {s: round(knee_flex(J['hip' + s], J['knee' + s], J['ank' + s]), 1) for s in 'NF'}
        ys = np.nonzero(mask.any(1))[0]
        xs = np.nonzero(mask.any(0))[0]
        m['lowest_px'], m['top_px'], m['x_range'] = int(ys.max()), int(ys.min()), [int(xs.min()), int(xs.max())]
        m['leg_low'] = {s: int(np.nonzero((fr[ln][..., 3] > 0).any(1))[0].max()) for s, ln in (('N', 'leg_near'), ('F', 'leg_far'))}
        # the ends of the sole in the SOLE_BAND rows above the floor line: front = toe, back = heel (or the ball once the heel is up).
        # A planted foot pivots on one of them, so a heel lift (the ankle rises) or a toe lift does not move both; None when the leg
        # does not reach the floor
        m['sole_front'], m['sole_back'] = {}, {}
        for s, ln in (('N', 'leg_near'), ('F', 'leg_far')):
            band = np.nonzero((fr[ln][BASELINE - SOLE_BAND:BASELINE + 1, :, 3] > 0).any(0))[0]
            on = m['leg_low'][s] == BASELINE and len(band) > 0
            m['sole_front'][s] = int(band.max()) if on else None
            m['sole_back'][s] = int(band.min()) if on else None
        if m['lowest_px'] > BASELINE:
            errors.append(f'{tag}: lowest pixel at y={m["lowest_px"]}, nothing may be below the floor line {BASELINE}')
        if BASELINE not in m['leg_low'].values():
            errors.append(f'{tag}: no foot on the floor line y={BASELINE} (legs end at near {m["leg_low"]["N"]} / far {m["leg_low"]["F"]}) - '
                          f'a {motion} never leaves the ground: the planted foot stays on y={BASELINE}')
        if xs.min() == 0 or xs.max() == w - 1 or ys.min() == 0:
            errors.append(f'{tag}: the picture touches the frame edge (x {xs.min()}-{xs.max()}, top {ys.min()}) - it is cut off; '
                          'change how the weapon is held, never the scale (SPEC section 3)')
        elif xs.min() < EDGE_BAND or xs.max() > w - 1 - EDGE_BAND:
            warns.append(f'{tag}: the picture spans x={xs.min()}-{xs.max()}, keep it inside {EDGE_BAND}-{w - 1 - EDGE_BAND} '
                         '(the GPT strip keeps 32 px of magenta at its borders)')
        m['weapons'] = weapon_geom(fr, J)
        meas.append(m)
    if any(m is None for m in meas) or n != want_n:
        return errors, warns, info, clean(meas), flats
    # neighbouring frames: pixel copies, silhouette change at game size
    small = []
    for _, mask in flats:
        im = Image.fromarray((mask * 255).astype(np.uint8)).resize((round(w * SCALE), round(h * SCALE)), Image.BOX)
        small.append(np.asarray(im) >= 128)

    def change(i, j):
        a, b = small[i], small[j]
        return 100.0 * (a ^ b).sum() / max(1, (a | b).sum())
    pairs = list(range(n - 1)) + ([n - 1] if spec['loop'] else [])
    diffs = {}
    for i in pairs:
        j = (i + 1) % n
        diffs[i] = change(i, j)
        same = all(np.array_equal(frames[i][ln], frames[j][ln]) for ln in names if ln != 'Background')
        if same and motion != 'idle':
            errors.append(f'{lab[i]} -> {lab[j]}: the two frames are pixel copies - every frame of the sequence is its own pose '
                          '(a longer hold is a longer duration, not a second frame)')
        exempt = motion == 'idle' or (spec['hold'] is not None and spec['hold'] in (i, j))
        if not exempt and diffs[i] < spec['neighbour_min']:
            warns.append(f'{lab[i]} -> {lab[j]}: silhouettes differ by {diffs[i]:.0f}% at game size (under {spec["neighbour_min"]:.0f}%: the frame adds nothing)')
    info.append('silhouette change to the next frame at game size: ' + ' '.join(f'{diffs[i]:.0f}%' for i in pairs)
                + (' (idle: no 8% rule, the loop must close instead)' if motion == 'idle' else
                   f' (hold frame {N[spec["hold"]]} exempt)' if spec['hold'] is not None else ''))
    if motion == 'attack':
        attack_rules(meas, frames, flats, spec, change, errors, warns, info)
    elif motion == 'hit':
        hit_rules(meas, spec, idle_ref, errors, warns, info)
    else:
        idle_rules(meas, spec, change, errors, warns, info)
    if all('head' in m for m in meas):
        head_tilt_motion(meas, 'f', warns, info, HIT_HEAD_DRIFT if motion == 'hit' else HEAD_DRIFT)
    return errors, warns, info, clean(meas), flats


def clean(meas):
    return [None if m is None else {k: v for k, v in m.items() if not k.startswith('_')} for m in meas]


def foot_spans(meas, spans, errors, info, lab):
    """the planted foot (SPEC 8: at least one foot stays put; motion_chars pivot_foot names which, and from which frame). In every
    frame of the span one anchor of the foot is where it was in the span's first frame (+-PIVOT_TOL): the front end of the sole on
    the floor (toe; rows y=870-SOLE_BAND..870), its back end (heel), or the ankle dot (x and y). So the heel may lift (the foot
    rolls onto the toe, the ankle rises), the toe may lift (it rocks on the heel); a slide moves all three.
    -> (worst move px of the anchor that stayed, None when the foot leaves the floor; on the floor in every frame; anchors used; worst ankle move)"""
    def fixed(side, a, b):
        floor = all(meas[k]['leg_low'][side] == BASELINE and meas[k]['sole_front'][side] is not None for k in range(a, b + 1))
        J0, f0, h0 = meas[a]['_J']['ank' + side], meas[a]['sole_front'][side], meas[a]['sole_back'][side]
        ank = max(dist(meas[k]['_J']['ank' + side], J0) for k in range(a, b + 1))
        if not floor:
            return None, False, set(), ank
        worst, used = 0.0, set()
        for k in range(a, b + 1):
            J = meas[k]['_J']['ank' + side]
            cand = {'toe': abs(meas[k]['sole_front'][side] - f0), 'heel': abs(meas[k]['sole_back'][side] - h0),
                    'ankle': max(abs(J[0] - J0[0]), abs(J[1] - J0[1]))}
            best = min(cand, key=lambda c: (cand[c], ('toe', 'heel', 'ankle').index(c)))
            worst = max(worst, cand[best])
            if cand[best] > 0:
                used.add(best)
        return worst, True, used, ank

    def says(s, r):
        nm = 'near' if s == 'N' else 'far'
        if not r[1]:
            return f'{nm} foot leaves the floor (ankle up to {r[3]:.1f} px)'
        return f'{nm} foot stays within {r[0]:.0f} px' + (f' (on its {"/".join(sorted(r[2]))})' if r[2] and r[0] <= PIVOT_TOL else '') \
            + f', ankle up to {r[3]:.1f} px'
    n = len(meas)
    if spans is None:
        res = {s: fixed(s, 0, n - 1) for s in 'NF'}
        ok = [s for s, r in res.items() if r[1] and r[0] <= PIVOT_TOL]
        info.append('planted foot (no pivot_foot in motion_chars.json: at least one foot fixed; toe / heel end of the sole in rows '
                    f'y={BASELINE - SOLE_BAND}-{BASELINE} or the ankle dot): ' + ', '.join(says(s, res[s]) for s in 'NF'))
        if not ok:
            errors.append(f'no foot stays put through the sequence ({says("N", res["N"])}; {says("F", res["F"])}; the toe end, the heel end or the '
                          f'ankle +-{PIVOT_TOL} px and the sole on y={BASELINE} in every frame) - SPEC 8: at least one foot is the pivot, the engine moves the body')
        return
    for sides, a, b in spans:
        for s in sides:
            r = fixed(s, a, b)
            nm = 'near (back)' if s == 'N' else 'far (front)'
            info.append(f'pivot foot {nm} {lab[a]}..{lab[b]}: ' + says(s, r))
            if not r[1] or r[0] > PIVOT_TOL:
                errors.append(f'the pivot foot ({nm}, motion_chars.json pivot_foot) ' + (f'slides: its toe end, heel end and ankle all move, the least by {r[0]:.0f} px'
                              if r[1] else 'leaves the floor') + f' between {lab[a]} and {lab[b]} - it stays put (the toe end, the heel end or the ankle '
                              f'+-{PIVOT_TOL} px, sole on y={BASELINE}; a heel lift keeps the toe where it stood)')


def attack_rules(meas, frames, flats, spec, change, errors, warns, info):
    """SPEC 8 + motion_bible.json checks_by_kind: anticipation reads, one contact frame, follow-through, recovery"""
    C, H, K = spec['contact'], spec['hold'], spec['checks']
    n = len(meas)
    lab = [m['frame'] for m in meas]
    foot_spans(meas, spec['pivot'], errors, info, lab)
    kind = spec['kind']
    if kind not in MOTION_KINDS:
        warns.append(f'kind "{kind}" (archetype {spec["arch"]}): only the common rules are measured here - its own rules '
                     f'({", ".join(k for k in K if k not in ("note",))}) are not implemented yet (checks_by_kind.{kind})')
        recover_rule(meas, C, errors, warns, info)
        return
    # which hand holds which weapon layer: the hand dot closest to the layer, over the whole sequence (median); a bow: the hand dot
    # closest to the layer's centroid (the drawn string touches the string hand, the stave is the bulk of the layer)
    grips = {}
    key = ('to_centroid_N', 'to_centroid_F') if kind == 'bow' else ('near_N', 'near_F')
    for ln in WEAPON_LAYERS:
        ds = [(m['weapons'][ln][key[0]], m['weapons'][ln][key[1]]) for m in meas if ln in m['weapons']]
        if len(ds) == n:
            grips[ln] = 'N' if np.median([d[0] for d in ds]) <= np.median([d[1] for d in ds]) else 'F'
    for m in meas:
        for ln, s in grips.items():
            g = m['weapons'][ln]
            hx, hy = m['_J']['hand' + s]
            g['grip'], g['tip'], g['far'] = s, g['tip_' + s], g['far_' + s]
            g['angle'] = math.degrees(math.atan2(-(g['far'][1] - hy), g['far'][0] - hx))
    if grips:
        info.append('weapon layers: ' + ', '.join(f'{ln} in the {"near" if s == "N" else "far"} hand' for ln, s in grips.items())
                    + (' (bow hand = the hand dot nearest the layer\'s centroid)' if kind == 'bow' else ''))
    if kind == 'bow':
        bow_rules(meas, spec, grips, errors, warns, info)
        recover_rule(meas, C, errors, warns, info)
        return
    blades = [ln for ln in grips if ln != 'shield']
    if not blades and 'shield' not in grips:
        errors.append('no weapon layer (weapon_front / weapon_back / shield) in every frame - the contact is measured on the weapon')
        return
    # anticipation: head x from the feet's mid-point flips sign hold -> contact and travels; the hip travels
    hx = [m['head']['centre'][0] - (m['_J']['ankN'][0] + m['_J']['ankF'][0]) / 2 for m in meas]
    hipx = [m['hip'][0] for m in meas]
    info.append('head x from the mid-point of the ankles: ' + ' '.join(f'{v:+.0f}' for v in hx) + ' px; hip x: ' + ' '.join(f'{v:.0f}' for v in hipx))
    if K.get('head_x_sign_flip'):
        if not (hx[H] < 0 < hx[C]):
            errors.append(f'anticipation: the head is {hx[H]:+.0f} px from the feet\'s mid-point at {lab[H]} and {hx[C]:+.0f} px at {lab[C]} - '
                          'SPEC 8: behind the feet at the hold (weight back), ahead of them at the contact (the direction reverses)')
        tr = hx[C] - hx[H]
        if tr < K.get('head_x_travel_min_src_px', 100):
            errors.append(f'anticipation: the head travels {tr:.0f} px from {lab[H]} to {lab[C]}, SPEC 8 asks {K.get("head_x_travel_min_src_px", 100)} or more')
    if K.get('hip_travel_min_src_px'):
        tr = hipx[C] - hipx[H]
        if tr < K['hip_travel_min_src_px']:
            errors.append(f'anticipation: the hip travels {tr:.0f} px from {lab[H]} to {lab[C]}, SPEC 8 asks {K["hip_travel_min_src_px"]} or more')
    # contact: a blade crossing its strike line, or the furthest reach (thrust tip / shield face) - on the contact frame only
    F = C + 1 if C + 1 < n else None
    found, how = [], []
    for ln in blades:
        ang = unwrap([m['weapons'][ln]['angle'] for m in meas])
        tipx = [m['weapons'][ln]['tip'][0] for m in meas]
        info.append(f'{ln}: angle ' + ' '.join(f'{a:.0f}' for a in ang) + ' deg; tip x ' + ' '.join(str(t) for t in tipx))
        if kind == 'melee_swing' and F is not None and C >= 1:
            s1, s2 = ang[C] - ang[C - 1], ang[F] - ang[C]
            if s1 * s2 > 0 and abs(s1) >= CROSS_MIN:
                found.append(('cross', ln, ang, s1, s2))
        if max(tipx) - sorted(tipx)[-2] >= 2 and tipx.index(max(tipx)) == C:
            found.append(('reach', ln, tipx))
        how.append(f'{ln} reach peaks at {lab[tipx.index(max(tipx))]}')
    if 'shield' in grips:
        sx = [m['weapons']['shield']['front'] for m in meas]
        info.append('shield front x ' + ' '.join(str(v) for v in sx))
        if max(sx) - sorted(sx)[-2] >= 2 and sx.index(max(sx)) == C:
            found.append(('shove', 'shield', sx))
        how.append(f'shield reach peaks at {lab[sx.index(max(sx))]}')
    if kind == 'melee_thrust':
        found = [f for f in found if f[0] == 'reach']
    if any(f[0] == 'shove' for f in found):
        # a shield shove with a weapon carried along: a small turn of the blade is not a cut (the slash rules would demand 120 deg)
        weak = [f for f in found if f[0] == 'cross' and abs(f[3] + f[4]) < SHOVE_SLASH_MIN]
        for f in weak:
            info.append(f'{f[1]} turns {abs(f[3] + f[4]):.0f} deg one way {lab[C - 1]} -> {lab[C]} -> {lab[F]}, under {SHOVE_SLASH_MIN} with a shield '
                        'shove at the contact: carried along, not a cut (no slash rules)')
        found = [f for f in found if f not in weak]
    if not found:
        errors.append(f'no contact at {lab[C]}: ' + ('a blade must cross its strike line there (swing -> contact -> follow turning one way) or '
                      if kind == 'melee_swing' else '') + 'the tip / shield face must reach furthest there (' + '; '.join(how)
                      + ') - the contact frame reads on its own (an unpredicted attack starts at it)')
    else:
        info.append('contact at ' + lab[C] + ': ' + ', '.join(f'{f[1]} ' + {'cross': 'crosses its strike line', 'reach': 'tip at its furthest reach',
                                                                           'shove': 'face at its furthest reach'}[f[0]] for f in found))
    cross = [f for f in found if f[0] == 'cross']
    if kind == 'melee_swing':
        if cross or not [f for f in found if f[0] == 'shove']:
            best = 0.0
            for ln in blades:
                ang = unwrap([m['weapons'][ln]['angle'] for m in meas])
                if F is not None:
                    best = max(best, abs(ang[F] - ang[H]))
            info.append(f'weapon angle change {lab[H]} -> {lab[F] if F is not None else "?"}: {best:.0f} deg (SPEC 8 slash: 120 or more)')
            if best < 120:
                errors.append(f'the weapon turns {best:.0f} deg from {lab[H]} to {lab[F] if F is not None else "the follow"}, SPEC 8 asks 120 or more for a '
                              'cut (wind it further back at the hold or carry it further through)')
        else:
            sx = [m['weapons']['shield']['front'] for m in meas]
            if sx[C] - sx[H] < K.get('hip_travel_min_src_px', 55):
                warns.append(f'shield shove: the shield face travels {sx[C] - sx[H]} px from {lab[H]} to {lab[C]}, at least the hip travel '
                             f'({K.get("hip_travel_min_src_px", 55)}) so the shove reads')
    if kind == 'melee_thrust':
        best = max((meas[C]['weapons'][ln]['tip'][0] - meas[H]['weapons'][ln]['tip'][0] for ln in blades), default=0)
        if best < K.get('tip_travel_min_src_px', 165):
            errors.append(f'thrust: the tip travels {best} px from {lab[H]} to {lab[C]}, SPEC 8 asks {K.get("tip_travel_min_src_px", 165)} or more')
    # follow-through passes the contact line
    if F is not None:
        if cross and spec.get('past') is None:
            warns.append('no weapon_past_line_deg in motion_bible.json: the follow-through past the strike line is not measured')
        elif cross:
            lo, hi, src = spec['past']
            for _, ln, ang, s1, s2 in cross:
                past = abs(ang[F] - ang[C])
                info.append(f'follow-through: {ln} {past:.0f} deg past the contact (bible {lo:g}-{hi:g}, {src}; over {hi + PAST_FAIL_OVER:g} fails)')
                if past > hi + PAST_FAIL_OVER:
                    errors.append(f'{lab[F]}: {ln} is {past:.0f} deg past its contact angle, more than {hi + PAST_FAIL_OVER:g} (bible {lo:g}-{hi:g} + '
                                  f'{PAST_FAIL_OVER}) - {lab[C]} is still mid-arc: the blade reaches its strike line a frame late (put the strike pose '
                                  f'on {lab[C]}, {lo:g}-{hi:g} deg further on {lab[F]})')
                elif not lo <= past <= hi:
                    warns.append(f'{lab[F]}: {ln} is {past:.0f} deg past its contact angle, the bible asks {lo:g}-{hi:g} (follow-through past the line)')
        else:
            dx = meas[F]['hip'][0] - meas[C]['hip'][0]
            info.append(f'follow-through: hip {dx:+.0f} px from the contact (bible +0.08 head = +9)')
            if dx < 0:
                warns.append(f'{lab[F]}: the hip moves {dx:.0f} px back from the contact - the follow-through carries the body on past the contact line '
                             '(bible: hips +0.08 head forward)')
    if C >= 1 and K.get('swing_to_contact_change_min') is not None:
        ch = change(C - 1, C)
        if ch < 100 * K['swing_to_contact_change_min']:
            errors.append(f'{lab[C - 1]} -> {lab[C]}: the silhouette changes {ch:.0f}% at game size, the bible asks {100 * K["swing_to_contact_change_min"]:.0f}% '
                          'or more (the contact must read as a new shape)')
    if F is not None and K.get('contact_to_follow_change_max') is not None:
        ch = change(C, F)
        if ch > 100 * K['contact_to_follow_change_max']:
            warns.append(f'{lab[C]} -> {lab[F]}: the silhouette changes {ch:.0f}% at game size, the bible asks {100 * K["contact_to_follow_change_max"]:.0f}% '
                         'or less (the follow continues the contact shape)')
    weapon_outside(meas, frames, flats, spec, blades, warns)
    recover_rule(meas, C, errors, warns, info)


def weapon_outside(meas, frames, flats, spec, blades, warns):
    """SPEC 8: at the hold and the contact >= 60 % of the weapon over magenta, the tip >= 33 px outside the body"""
    if spec['kind'] != 'melee_swing':
        return
    body_layers = [ln for ln in BODY]
    for i in (spec['hold'], spec['contact']):
        fr = frames[i]
        body = np.zeros(fr['torso'].shape[:2], bool)
        for ln in body_layers:
            body |= fr[ln][..., 3] > 0
        near = None
        for ln in blades:
            wpx = fr[ln][..., 3] > 0
            free = 100.0 * (wpx & ~body).sum() / max(1, wpx.sum())
            tx, ty = meas[i]['weapons'][ln]['tip']
            if near is None:
                near = grow(body, 33)
            if free < 60:
                warns.append(f'{meas[i]["frame"]}: only {free:.0f}% of {ln} is clear of the body, SPEC 8 asks 60% or more (the weapon reads outside the silhouette)')
            if near[ty, tx]:
                warns.append(f'{meas[i]["frame"]}: the {ln} tip ({tx},{ty}) is within 33 px of the body, SPEC 8 asks 33 or more outside')


def bow_rules(meas, spec, grips, errors, warns, info):
    """SPEC 8 bow exception: upright, no head flip; the wind-up is the draw length, the release throws the string hand back"""
    C, H, K = spec['contact'], spec['hold'], spec['checks']
    lab = [m['frame'] for m in meas]
    bows = [ln for ln in grips if ln != 'shield']
    if not bows:
        errors.append('bow set without a weapon layer holding the bow (weapon_front / weapon_back)')
        return
    bh = grips[bows[0]]
    dh = 'N' if bh == 'F' else 'F'
    dx = [m['_J']['hand' + dh][0] for m in meas]
    bx = [m['_J']['hand' + bh] for m in meas]
    info.append(f'bow in the {"near" if bh == "N" else "far"} hand; draw hand x ' + ' '.join(f'{v:.0f}' for v in dx)
                + '; draw length (bow hand - draw hand) ' + ' '.join(f'{b[0] - d:.0f}' for b, d in zip(bx, dx)))
    draw = [b[0] - d for b, d in zip(bx, dx)]
    need = K.get('draw_hand_travel_min_src_px', 100)
    if draw[H] < need:
        errors.append(f'draw: the string hand is {draw[H]:.0f} px behind the bow hand at {lab[H]}, SPEC 8 bow asks {need} or more - the wind-up '
                      'of a bow is the draw length (the string hand travels from the string at the bow to the cheek)')
    if H and max(draw[:H]) >= draw[H]:
        errors.append(f'draw: the draw is already {max(draw[:H]):.0f} px at {lab[draw[:H].index(max(draw[:H]))]}, not longest at the hold '
                      f'({lab[H]} {draw[H]:.0f} px) - the string comes back through the nock / raise frames into the full draw')
    back = dx[H] - dx[C]
    if back < K.get('release_hand_travel_min_src_px', 60):
        errors.append(f'release: the string hand moves {back:.0f} px back from {lab[H]} to {lab[C]}, the bible asks '
                      f'{K.get("release_hand_travel_min_src_px", 60)} or more (the release is the weakest-reading contact)')
    jumps = [dx[k] - dx[k + 1] for k in range(len(dx) - 1)]
    if jumps.index(max(jumps)) != C - 1:
        errors.append(f'the string hand\'s biggest move back is {lab[jumps.index(max(jumps))]} -> {lab[jumps.index(max(jumps)) + 1]}, '
                      f'not into the release ({lab[C]}) - the contact frame is the release')
    hold_bow = dist(bx[H], bx[C])
    if hold_bow > 6:
        warns.append(f'{lab[C]}: the bow hand moves {hold_bow:.0f} px from {lab[H]}, the bow arm holds through the release (6 or less)')
    lean = [m['lean_deg'] for m in meas]
    if max(abs(v) for v in lean[H:C + 1]) > 10:
        warns.append(f'the archer leans {max(abs(v) for v in lean[H:C + 1]):.0f} deg at the hold / release, SPEC 8 bow: upright (draw to the cheek standing)')


def recover_rule(meas, C, errors, warns, info):
    """after the follow-through every frame comes back toward the first one (the idle the attack started from)"""
    n = len(meas)
    ref = meas[0]['_J']
    d = [joint_dist(m['_J'], ref) for m in meas]
    info.append('mean joint distance from ' + meas[0]['frame'] + ': ' + ' '.join(f'{v:.0f}' for v in d) + ' px')
    for k in range(C + 2, n):
        if d[k] >= d[k - 1]:
            msg = (f'{meas[k]["frame"]}: {d[k]:.0f} px from {meas[0]["frame"]}, {meas[k - 1]["frame"]} was {d[k - 1]:.0f} - after the follow-through '
                   'every frame returns toward the guard')
            (errors if k == C + 2 else warns).append(msg)


def hit_rules(meas, spec, ref, errors, warns, info):
    """posekit HIT_KEYS / handoff HIT_RULES / motion_bible hit.weights.<w>.checks: feet planted, knees absorb, head snaps away"""
    K, keys, w = spec['checks'], spec['keys'], spec['weight']
    lab = [m['frame'] for m in meas]
    J0 = meas[0]['_J']
    built = ref is None
    if built:
        ref = build_idle_ref(J0['ankN'][0], J0['ankF'][0], spec['idle_reference'])
    R = ref['joints']
    info.append(f'idle reference: {ref["source"]} - hip x {ref["hip"][0]:.1f}, hip height {ref["hip_h"]:.1f} px, head centre x {ref["head"][0]:.1f}, '
                f'ankles near {R["ankN"][0]:.0f} / far {R["ankF"][0]:.0f}')
    if built and abs(ref['hip'][0] - SLOT / 2) > HIT_COLUMN_TOL:
        warns.append(f'the idle reference stood on {lab[0]}\'s feet has its hip at x={ref["hip"][0]:.1f}, {ref["hip"][0] - SLOT / 2:+.1f} px off the idle '
                     f'column x={SLOT // 2} (+-{HIT_COLUMN_TOL}) - a hit starts where the idle stands: move the whole sequence so K1\'s feet are the idle\'s '
                     '(or check it with --idle <the idle set>.aseprite)')
    lo, hi = K['head_dx_src_px']
    rows = []
    for i, m in enumerate(meas):
        J = m['_J']
        r = dict(lean_back=-m['lean_deg'], drop=ref['hip_h'] - m['hip_height_px'], head_dx=m['head']['centre'][0] - ref['head'][0],
                 knee_rise=R['kneeF'][1] - J['kneeF'][1], front_move=J['ankF'][0] - R['ankF'][0], slide=J['ankN'][0] - R['ankN'][0],
                 ank_dy={s: J['ank' + s][1] - R['ank' + s][1] for s in 'NF'})
        m['hit'] = {k: (round(v, 1) if not isinstance(v, dict) else {s: round(x, 1) for s, x in v.items()}) for k, v in r.items()}
        rows.append(r)
        t = lab[i]
        if m['leg_low']['F'] != BASELINE:
            errors.append(f'{t}: the front foot (leg_far) ends at y={m["leg_low"]["F"]}, it stays flat on y={BASELINE} - front-foot lift is 0 in a hit')
        if m['leg_low']['N'] != BASELINE:
            errors.append(f'{t}: the back foot (leg_near) ends at y={m["leg_low"]["N"]}, both feet stay on y={BASELINE} (a light hit slides it, never lifts it)')
        for s in 'NF':
            if abs(r['ank_dy'][s]) > FEET_FLAT_TOL:
                errors.append(f'{t}: the {"back" if s == "N" else "front"} ankle is {-r["ank_dy"][s]:+.0f} px off the idle ankle height - feet flat '
                              f'(+-{FEET_FLAT_TOL}, no heel or toe raised)')
        if abs(r['front_move']) > PIVOT_TOL:
            errors.append(f'{t}: the front foot moved {r["front_move"]:+.0f} px from where the idle stands it - it stays put (+-{PIVOT_TOL})')
        slide_max = K.get('back_foot_slide_max_src_px')
        if slide_max:
            if not -slide_max - PIVOT_TOL <= r['slide'] <= PIVOT_TOL:
                errors.append(f'{t}: the back foot slid {r["slide"]:+.0f} px, a light hit allows one short step back of {slide_max} px (0.3 head) at most')
        elif abs(r['slide']) > PIVOT_TOL:
            errors.append(f'{t}: the back foot moved {r["slide"]:+.0f} px - a {w} hit keeps both feet where they stood (only light slides it)')
        if r['knee_rise'] > K.get('knee_rise_max_src_px', 1):
            errors.append(f'{t}: the front knee is {r["knee_rise"]:.1f} px above its idle height, {K.get("knee_rise_max_src_px", 1)} at most '
                          '(a knee-up hit reads as comic; the knees bend DOWN to absorb the blow)')
        if r['lean_back'] > K.get('lean_max_deg', 15):
            errors.append(f'{t}: the torso leans back {r["lean_back"]:.1f} deg (hip to neck), {K.get("lean_max_deg", 15)} at most - the head and '
                          'shoulders snap away, the body is not thrown back')
    for i in keys:
        r, t = rows[i], lab[i]
        if not K['hip_drop_src_px'][0] <= r['drop'] <= K['hip_drop_src_px'][1]:
            errors.append(f'{t}: the hip drops {r["drop"]:.1f} px below the idle, the bible asks {K["hip_drop_src_px"][0]}-{K["hip_drop_src_px"][1]} '
                          '(the knees absorb the blow)')
        if not lo <= -r['head_dx'] <= hi:
            errors.append(f'{t}: the head moves {-r["head_dx"]:+.1f} px away from the blow (centre of the head layer against the idle), '
                          f'a {w} hit asks {lo}-{hi} ({round(lo * SCALE)}-{round(hi * SCALE)} game px)')
    if len(keys) >= 2:
        a, b = keys[0], keys[1]
        if rows[b]['drop'] < rows[a]['drop'] - 1 or -rows[b]['head_dx'] < -rows[a]['head_dx'] - 1:
            errors.append(f'{lab[b]} is not the deepest point: hip drop {rows[a]["drop"]:.0f} -> {rows[b]["drop"]:.0f} px, head away '
                          f'{-rows[a]["head_dx"]:.0f} -> {-rows[b]["head_dx"]:.0f} px from {lab[a]} - K1 is the impact, K2 goes further (wrong frame order?)')
    info.append('hit (against the idle; hip drop / head away / lean back / front knee rise / back foot slide): ' + ' | '.join(
        f'{lab[i]} {r["drop"]:.0f} / {-r["head_dx"]:.0f} / {r["lean_back"]:.1f} / {r["knee_rise"]:.1f} / {r["slide"]:+.0f}' for i, r in enumerate(rows)))
    # the way back: every frame after the deepest key is closer to the idle; the last one within 12 px of it
    d = [joint_dist(m['_J'], R, BODY_JOINTS) for m in meas]
    last = keys[-1] if keys else 0
    for k in range(last + 1, len(meas)):
        if d[k] >= d[k - 1]:
            (errors if k == last + 1 else warns).append(f'{lab[k]}: {d[k]:.0f} px from the idle, {lab[k - 1]} was {d[k - 1]:.0f} - after the peak the body '
                                                       'comes back toward the idle')
    far = max(dist(meas[-1]['_J'][j], R[j]) for j in BODY_JOINTS)
    if far > K.get('k_last_vs_idle_max_src_px', 12):
        warns.append(f'{lab[-1]}: a body joint is still {far:.0f} px from the idle, the bible asks {K.get("k_last_vs_idle_max_src_px", 12)} or less '
                     '(the last frame hands over to the idle)')


def idle_rules(meas, spec, change, errors, warns, info):
    """a breathing loop: the rest frame defines the column (hip x=192), the feet never move, tiny motion, the loop closes"""
    n = len(meas)
    lab = [m['frame'] for m in meas]
    hip0 = meas[0]['hip']
    if abs(hip0[0] - SLOT / 2) > HIP_X_TOL:
        errors.append(f'{lab[0]}: hip centre at x={hip0[0]:.1f}, the rest frame stands on the column x={SLOT // 2} +-{HIP_X_TOL} (registration anchors '
                      'it there; attack and hit sets are measured from the same column)')
    for m in meas:
        for s in 'NF':
            mv = dist(m['_J']['ank' + s], meas[0]['_J']['ank' + s])
            if mv > 2 or m['leg_low'][s] != BASELINE:
                errors.append(f'{m["frame"]}: the {"near" if s == "N" else "far"} foot ' + (f'moves {mv:.1f} px' if mv > 2 else 'leaves the floor')
                              + f' - an idle stands on both feet (+-2 px, soles on y={BASELINE})')
        if abs(m['hip'][0] - hip0[0]) > 2:
            warns.append(f'{m["frame"]}: the hip moves {m["hip"][0] - hip0[0]:+.1f} px sideways, breathing moves it up and down only')
    moves = [max(dist(m['_J'][j], meas[0]['_J'][j]) for j in CHAIN) for m in meas]
    info.append('largest joint move from the rest frame: ' + ' '.join(f'{v:.1f}' for v in moves) + f' px (a breathing idle: up to {IDLE_MOVE})')
    for m, v in zip(meas, moves):
        if v > IDLE_MOVE:
            warns.append(f'{m["frame"]}: a joint moves {v:.0f} px from the rest frame, a breathing idle moves 1-2 game px ({IDLE_MOVE} px) - '
                         'a bigger change is a different pose')
    if n > 1 and max(moves[1:]) < 0.5:
        warns.append('every frame is the rest pose (no joint moves): the breathing frames add nothing (chest and shoulders up 1 game px at the top)')
    steps = [joint_dist(meas[k + 1]['_J'], meas[k]['_J']) for k in range(n - 1)]
    close = joint_dist(meas[0]['_J'], meas[-1]['_J'])
    sil = [change(k, k + 1) for k in range(n - 1)]
    sc = change(n - 1, 0)
    info.append('loop: joint step ' + ' '.join(f'{v:.1f}' for v in steps) + f' px, last -> first {close:.1f} px; silhouette '
                + ' '.join(f'{v:.0f}%' for v in sil) + f', last -> first {sc:.0f}%')
    if n > 1 and (close > max(steps) + 1 or sc > max(sil) + 2 or close > 2 * steps[0] + 1 or sc > 2 * sil[0] + 2):
        errors.append(f'the loop does not close: {lab[-1]} -> {lab[0]} moves {close:.1f} px / {sc:.0f}% (the steps inside the loop at most '
                      f'{max(steps):.1f} px / {max(sil):.0f}%, the step out of {lab[0]} {steps[0]:.1f} px / {sil[0]:.0f}%) - the last frame leads back '
                      f'into the first like any neighbour (at most 2x the first step + 1 px / + 2%: exhale mirrors inhale)')
    for k in range(n):
        j = (k + 1) % n
        if moves and joint_dist(meas[k]['_J'], meas[j]['_J']) == 0 and n > 1 and max(moves[1:]) >= 0.5:
            warns.append(f'{lab[k]} -> {lab[j]}: the two frames have the same joints (a copy?) - each breathing frame is its own step '
                         '(check the frame order: rest, inhale, top, exhale)')


def export_motion(flats, durs, out, name, spec):
    """one PNG per frame f<NN>_<name>.png (384x1024 RGB, NN 0-based in the bible order) and the game-size preview GIF"""
    os.makedirs(out, exist_ok=True)
    small = []
    for i, (rgb, _) in enumerate(flats):
        fn = re.sub(r'[^A-Za-z0-9]+', '_', spec['names'][i]).strip('_')
        Image.fromarray(rgb, 'RGB').save(os.path.join(out, f'f{i:02d}_{fn}.png'))
        cell = Image.fromarray(rgb, 'RGB').crop((0, BASELINE - 500, SLOT, BASELINE + 12))
        cell = cell.resize((round(cell.width * SCALE), round(cell.height * SCALE)), Image.BOX)
        small.append(cell.resize((cell.width * 4, cell.height * 4), Image.NEAREST))
    small[0].save(os.path.join(out, f'{name}_preview.gif'), save_all=True, append_images=small[1:], duration=durs, loop=0, disposal=1)


def main_motion(a, motion, bones):
    set_id = a.set or os.path.splitext(os.path.basename(os.path.normpath(a.src)))[0]
    try:
        spec, problems = motion_spec(motion, set_id, a.bible, a.chars)
    except (OSError, ValueError, KeyError) as e:
        print(f'FAIL: cannot read the bible / chars: {e}')
        return 1
    print(f'# skeleton {set_id} ({motion})')
    if spec is None:
        for p in problems:
            print('FAIL: ' + p)
        print('RESULT: FAIL')
        return 1
    stem = os.path.splitext(os.path.basename(os.path.normpath(a.src)))[0]
    pre_w = [] if stem == set_id else [f'the file is named {stem}, the set {set_id}: deliver it as art/inbox/guides/{set_id}/{set_id}.aseprite']
    if os.path.isdir(a.src):
        print('FAIL: a motion set is read from its .aseprite (frame tags and durations); a layers folder has neither')
        print('RESULT: FAIL')
        return 1
    with tempfile.TemporaryDirectory(prefix='skeleton-') as tmp:
        try:
            frames, durs, names, hidden = load_aseprite(a.src, a.aseprite_exe, os.path.join(tmp, 'new'))
            tags = load_tags(a.src, a.aseprite_exe, os.path.join(tmp, 'tags'))
            ref = None
            if a.idle:
                fr2, _, names2, _ = load_aseprite(a.idle, a.aseprite_exe, os.path.join(tmp, 'idle'))
                ref = frame_ref(fr2[0], names2, f'rest frame of {os.path.basename(a.idle)}')
        except (RuntimeError, OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
            print(f'FAIL: cannot read {a.src}: {e}')
            print('RESULT: FAIL')
            return 1
        errors, warns, info, meas, flats = check_motion(frames, durs, names, hidden, tags, bones, spec, ref)
        errors = problems + errors
        warns = pre_w + warns
        for ln in info:
            print('- ' + ln)
        if a.base:
            try:
                print('- changed against the start file:')
                for ln in compare(frames, load_aseprite(a.base, a.aseprite_exe, os.path.join(tmp, 'base'))[0], warns, 'f'):
                    print('    ' + ln)
            except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
                warns.append(f'could not read the start file {a.base}: {e}')
        for w in warns:
            print('WARN: ' + w)
        for e in errors:
            print('FAIL: ' + e)
        if a.export and flats and len(flats) == len(spec['names']):
            export_motion(flats, durs, a.export, set_id, spec)
            with open(os.path.join(a.export, 'pose_measured.json'), 'w', encoding='utf-8') as f:
                json.dump(dict(set=set_id, motion=motion, sheet=spec['sheet'], arch=spec['arch'], weight=spec['weight'], source=os.path.basename(a.src),
                               baseline=BASELINE, scale=SCALE, names=spec['names'], durations_ms=durs, contact=spec['contact'], hold=spec['hold'],
                               cut=spec['cut'], frames=meas), f, ensure_ascii=False, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
                f.write('\n')
            print(f'- exported f<NN>_<name>.png per frame, {set_id}_preview.gif and pose_measured.json to {a.export}')
        print('RESULT: ' + ('FAIL' if errors else 'PASS' + (f' ({len(warns)} warning(s))' if warns else '')))
    return 1 if errors else 0


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
    ap.add_argument('--motion', choices=('attack', 'hit', 'idle'), help='measure an attack / hit / idle mannequin sequence (SPEC section 10) '
                    'against tools/art/specs/motion_bible.json + motion_chars.json. Default: from a set id / file name atk__ / hit__ / idle__')
    ap.add_argument('--set', help='the set id <atk|hit|idle>__<sheet stem without sheet_> (default: the file name), e.g. atk__class_warrior')
    ap.add_argument('--idle', help='hit sets: the idle set of the character (.aseprite, rest frame 1) as the reference instead of the bible '
                                   'idle_reference built on the posekit mannequin')
    ap.add_argument('--bible', default=os.path.join(SPECS, 'motion_bible.json'), help=argparse.SUPPRESS)
    ap.add_argument('--chars', default=os.path.join(SPECS, 'motion_chars.json'), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    bones = dict(DEFAULT_BONES)
    request = {}
    if a.pose:
        with open(a.pose, encoding='utf-8') as f:
            request = json.load(f)
        bones.update(request.get('bones_px', {}))
    pm = re.match(r'^(atk|hit|idle)__', a.set or os.path.basename(os.path.normpath(a.src)))
    motion = a.motion or (PREFIX_MOTION[pm.group(1)] if pm and not a.gait and not request.get('gait') else None)
    if motion:
        if a.gait:
            print(f'FAIL: --gait {a.gait} and --motion {motion}: a set is either a walk / run cycle or an attack / hit / idle sequence')
            return 1
        return main_motion(a, motion, bones)
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
