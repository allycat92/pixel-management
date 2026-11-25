#!/usr/bin/env python3
"""Measure a walk skeleton set (pose guide, not game art) against art/requests/guides/SPEC.md sections 3-6.

  python3 tools/art/check_skeleton.py SET.aseprite [--pose pose.json] [--base DRAFT.aseprite] [--export DIR]
  python3 tools/art/check_skeleton.py LAYERS_DIR          # W<n>_<layer>.png files as tools/pixelart/walk8.py writes them (no Aseprite needed)

The working file is the layered 8-frame .aseprite that walk8.py builds (384x1024 per frame, layers per body part, a hidden
`joints` layer with one colour-coded 3x3 dot per joint). The Aseprite session plays and refines it; this tool then measures
what only numbers can tell (bone lengths, the planted foot, the mirror half, the bob) from the joint dots and the layers.

FAIL: canvas/frames/layers wrong, a joint dot missing or left behind by its limb, bone length off by more than 2 px in any frame,
      stance sole not on y=870 or a foot below it, step outside 135-151 px, planted foot not retreating by step/4 (+-3 px) per frame,
      W(i+4) not the mirror of W(i), soft (half-transparent) pixels.
WARN: bob outside 12-16 px or in the wrong order, passing knee bent more than 15 deg, lifted foot outside 30-36 px,
      forward hand less than 20 px outside the torso, neighbouring frames nearly identical at game size.
--export DIR writes the strips (<set>_a.png, <set>_b.png), the game-size preview GIF and pose_measured.json from the file,
so the Aseprite session only has to deliver the .aseprite. --base DRAFT.aseprite lists what was changed per frame and layer.
Exit code 1 on FAIL.
"""
import argparse
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
from walk8 import BASELINE, JOINTS, SCALE, SLOT, SH_  # noqa: E402

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
    visible = {n.strip() for n in run(exe, '--list-layers', src).stdout.decode('utf-8', 'replace').splitlines() if n.strip()}
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
    return frames, durs, names, [n for n in names if n not in visible]


def load_dir(src):
    frames, i = [], 1
    while os.path.exists(os.path.join(src, f'W{i}_torso.png')):
        fr = {}
        for fn in sorted(os.listdir(src)):
            if fn.startswith(f'W{i}_') and fn.endswith('.png'):
                fr[fn[len(f'W{i}_'):-4]] = np.asarray(Image.open(os.path.join(src, fn)).convert('RGBA'))
        frames.append(fr)
        i += 1
    names = [n for n in ORDER if frames and n in frames[0]] + ['joints']
    return frames, [120] * len(frames), ['Background'] + names, ['joints']


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
    a = (hip[0] - knee[0], hip[1] - knee[1])
    b = (ank[0] - knee[0], ank[1] - knee[1])
    c = (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b) or 1)
    return 180 - math.degrees(math.acos(max(-1.0, min(1.0, c))))


def check(frames, durs, names, hidden, bones):
    errors, warns, info, meas = [], [], [], []
    n = len(frames)
    if n != 8:
        errors.append(f'{n} frames, a walk cycle is 8 (SPEC section 5)')
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
    flats = []
    for i, fr in enumerate(frames):
        tag = f'W{i + 1}'
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
        m['hip_height_px'] = round(BASELINE - hip[1], 1)
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
        if m['lowest_px'] != BASELINE:
            errors.append(f'{tag}: lowest pixel at y={m["lowest_px"]}, the planted sole must be on y={BASELINE}')
        stance, swing = (('leg_near', 'leg_far') if i < 4 else ('leg_far', 'leg_near'))
        lows = {ln: int(np.nonzero((fr[ln][..., 3] > 0).any(1))[0].max()) for ln in (stance, swing)}
        if lows[stance] != BASELINE:
            errors.append(f'{tag}: the stance leg ({stance}) ends at y={lows[stance]}, not on the floor line {BASELINE}')
        m['swing_sole_height_px'] = BASELINE - lows[swing]
        m['top_px'] = int(ys.min())
        tx = np.nonzero((fr['torso'][..., 3] > 0).any(0))[0]
        m['hand_past_torso_px'] = {s: round(J['hand' + s][0] - float(tx.max()), 1) for s in 'NF'}
        meas.append(m)
    if any(m is None for m in meas) or n != 8:
        return errors, warns, info, meas, flats
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
            warns.append(f'W{i + 1}->W{(i + 1) % n + 1}: silhouettes differ by {diffs[-1]:.0f}% at game size (under 8%: the frame adds nothing)')
    info.append('silhouette change to the next frame at game size: ' + ' '.join(f'{d:.0f}%' for d in diffs))
    return errors, warns, info, meas, flats


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


def compare(frames, base, warns):
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
                        warns.append(f'W{i + 1}: {ln} was repainted but its joint dots ({", ".join(mine)}) did not move - '
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
        lines.append(f'W{i + 1}: ' + (', '.join(ch) if ch else 'unchanged'))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('src', help='SET.aseprite, or a folder of W<n>_<layer>.png')
    ap.add_argument('--pose', help='pose.json of the request (bone lengths); default: the lengths of SPEC section 6')
    ap.add_argument('--base', help='the draft .aseprite (or layers folder) this was refined from: list what changed')
    ap.add_argument('--export', help='write <set>_a.png, <set>_b.png, <set>_preview.gif and pose_measured.json here')
    ap.add_argument('--name', help='set name for --export (default: the file name)')
    ap.add_argument('--aseprite-exe', default=os.environ.get('ASEPRITE_PATH') or (HEADLESS if os.path.exists(HEADLESS) else 'aseprite'))
    a = ap.parse_args(argv)
    bones = dict(DEFAULT_BONES)
    if a.pose:
        with open(a.pose, encoding='utf-8') as f:
            bones.update(json.load(f).get('bones_px', {}))
    with tempfile.TemporaryDirectory(prefix='skeleton-') as tmp:
        def load(src, sub):
            return load_dir(src) if os.path.isdir(src) else load_aseprite(src, a.aseprite_exe, os.path.join(tmp, sub))
        try:
            frames, durs, names, hidden = load(a.src, 'new')
        except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as e:
            print(f'FAIL: cannot read {a.src}: {e}')
            return 1
        errors, warns, info, meas, flats = check(frames, durs, names, hidden, bones)
        name = a.name or os.path.splitext(os.path.basename(os.path.normpath(a.src)))[0]
        print(f'# skeleton {name}')
        for ln in info:
            print('- ' + ln)
        if a.base:
            try:
                print('- changed against the draft:')
                for ln in compare(frames, load(a.base, 'base')[0], warns):
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
            print(f'- exported strips, preview and pose_measured.json to {a.export} (run check_delivery.py on the two strips)')
        print('RESULT: ' + ('FAIL' if errors else 'PASS' + (f' ({len(warns)} warning(s))' if warns else '')))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
