"""Render 3D-mannequin guides for real characters (prototype of the owner's approach 1, 2026-11-28).

  python3 tools/mannequin3d/build.py --out DIR [--chars warrior ironwall mage] [--yaw 15] [--chest-open 30]
                                     [--allow-coarse] [--carry specs/carry3d.json]

Per character (specs/carry3d.json): fit the mannequin to the accepted idle (fit.py), run its movement class
(motions.py) at the sheet's own scale with the character's carry (arms, props, robe), and write into DIR/<char>/:
  <set>_a.png, <set>_b.png       guide strips, same canvas as art/requests/guides/*: 1536x1024, 4 slots of 384,
                                 hip column x=192 per slot, standing soles on y=870, #FF00FF, ground line y=871,
                                 SPEC.md joint dots (near bright / far dark), props + robe see-through (teal outline;
                                 dashed light outline where a body part is in front), a teal ring on each hand that holds
                                 a prop
  <set>_plain_a/b.png            the same without joint dots, rings and ground line
  pose.json                      2D joints per frame in the run_base/heavy_base/robe_base pose.json schema
                                 (source: 'tools/mannequin3d ...' - add_gait treats request folders with it as mannequins)
  <set>_game_x1.gif / _x4.gif    the cycle at game size (96x96 cell, the add_gait window at the sheet scale) and x4
  <set>_guide.gif                the cycle at guide size (crop y 380..900)
  <set>_smooth.gif               24 in-between frames of the same cycle (shows the spline interpolation), half size
  contact.png                    accepted idle | mannequin idle with props | overlay, same scale (report.py)
  fit.json                       the fit report
warrior also: attack_ready.png, attack_a.png (windup, 1/3, 2/3, strike), hit_a.png (impact, recover) - every action
  frame placed by its own feet centre (the sheets' pose_feet_x rule) -, attack/hit GIFs and pose.json, and
  compare_run.png / compare_run.json / vs_run_base_v2.txt (report.py).
DIR/build_log.txt: every check (checks.py) as OK / WARN / FAIL. The exit code is 1 when any check FAILs (the files are
still written so the failure can be looked at). Never writes into assets/ or art/.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import checks  # noqa: E402
import fit as fitmod  # noqa: E402
import report  # noqa: E402
from common import (CARRY_JSON, CELL, ANCHOR, REPO, load_carry, sheet_scale, game_cell, on_bg, save_gif,  # noqa: E402
                    strip_of)
from motions import (gait_spec, gait_frames, robe_hems, action_frames, warrior_attack, warrior_hit, lock_feet,  # noqa: E402
                     leg_factor, carry_props, two_hand, solve_arms)
from render import Camera, render, project_joints, SLOT_W, FLOOR, HIP_X  # noqa: E402
from rig import fk, full_pose  # noqa: E402

JOINTS_OUT = ['hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'heelN', 'heelF', 'toetipN', 'toetipF',
              'SN', 'SF', 'elbN', 'elbF', 'wriN', 'wriF', 'handN', 'handF', 'neck0', 'head', 'headtop', 'nose']
ACTIONS = {'attack': (warrior_attack, [150, 45, 45, 260]), 'hit': (warrior_hit, [220, 180])}


# ---------------------------------------------------------------- pose.json
def frame_record(body, cam, mask, spec, meta, pose, slot_origin):
    J = project_joints(body, cam, JOINTS_OUT)
    joints = {k: [round(v[0] + slot_origin, 1), v[1]] for k, v in J.items()}
    hip = J['hip']
    rows = np.flatnonzero(mask.any(1))
    rec = {'frame': meta['frame'], 'strip': meta['strip'], 'slot': meta['slot'], 'phase': meta['phase']}
    st = meta['stance']
    rec['feet_down'] = ['near' if s == 'N' else 'far' for s in st]
    if len(st) == 2:      # double support: the leading (just landed) foot
        rec['stance'] = 'near' if meta['strip'] == 'a' else 'far'
    else:
        rec['stance'] = None if not st else ('near' if st[0] == 'N' else 'far')
    rec['hip_height_px'] = round(FLOOR - hip[1], 1)
    rec['top_px'] = int(rows.min())
    rec['lowest_px'] = int(rows.max())
    rec['sole_px'] = {s: int(round(FLOOR - body.joints['sole' + s][1])) for s in 'NF'}
    tips = {s: round(J['toetip' + s][0] - hip[0], 1) for s in 'NF'}
    if spec['gait'] == 'run':
        rec['toe_x_px'] = tips[st[0]] if st else None
    else:
        lead = rec['stance'][0].upper() if rec['stance'] else None
        rec['toe_x_px'] = {'stance': tips[lead] if lead else None,
                           'rear': (tips['F' if lead == 'N' else 'N'] if len(st) == 2 else None)}
    q = full_pose(pose)
    rec['knee_flex_deg'] = {s: round(q['knee_' + s], 1) for s in 'NF'}
    rec['elbow_flex_deg'] = {s: round(q['elbow_' + s], 1) for s in 'NF'}
    nk = J['neck0']
    rec['lean_deg'] = round(math.degrees(math.atan2(nk[0] - hip[0], hip[1] - nk[1])), 1)
    rec['neck_x_px'] = round(nk[0] - hip[0], 1)
    rec['ik_reached'] = bool(meta['reached'])
    if meta.get('hip_lowered'):
        rec['hip_lowered_px'] = meta['hip_lowered']
    if 'hem_front' in body.joints:
        hf, _ = cam.to_screen(body.joints['hem_front'])
        hb, _ = cam.to_screen(body.joints['hem_back'])
        rec['hem'] = {'bottom_above_floor_px': round(body.joints['hem_front'][1], 1),
                      'front_x_px': round(float(hf[0] - hip[0]), 1), 'back_x_px': round(float(hb[0] - hip[0]), 1)}
    rec['angles_deg'] = {k: round(v, 2) for k, v in q.items() if k not in ('x',) and not k.startswith('_')}
    rec['props'] = meta.get('props', [])
    rec['joints'] = joints
    return rec


def gait_pose_json(spec, P, cam, carry, recs, rep, scale):
    hips = [r['joints']['hip'][1] for r in recs]
    leans = [r['lean_deg'] for r in recs]
    out = {
        'set': spec['set'], 'gait': spec['gait'], 'movement_class': spec['class'], 'head_px': round(2 * P['head_r'][1], 1),
        'baseline': FLOOR, 'scale': scale, 'frames_per_cycle': 8, 'nominal_ms': spec['ms'], 'step_px': spec['step_px'],
        'run_stride_game_px': round(spec['step_px'] * scale, 1),
        'stride_rule': (f"class game stride {spec['stride_game_class']} px / sheet scale {scale} x leg factor "
                        f"{spec['leg_factor_used']} (fitted {spec['leg_factor']}; within 5% -> 1)"),
        'speed_at_nominal_ms_game_px_s': round(spec['step_px'] / 4 * scale / (spec['ms'] / 1000.0), 1),
        'bob_px': round(max(hips) - min(hips), 1), 'lean_deg': [min(leans), max(leans)],
        'bones_px': {'thigh': round(P['thigh'], 2), 'shin': round(P['shin'], 2), 'upper_arm': round(P['upper_arm'], 2),
                     'forearm_hand': round(P['forearm'] + P['hand'], 2)},
        'source': 'tools/mannequin3d (build.py) 3D mannequin guide - a MANNEQUIN, never game art (add_gait refuses it)',
        'character': rep['sheet'], 'fit_source': rep['source'],
        'camera': {'yaw_deg': cam.yaw, 'chest_open_deg': carry.get('chest_open', 30.0)},
        'joint_x': 'strip-wide x (slot offset added) like run_base' if spec['gait'] == 'run' else 'x inside each 384-px slot like heavy_base/robe_base',
        'hip_height_px': 'FLOOR 870 - hip joint y',
        'proportions': rep['proportions'], 'fit_factors': rep['factors'],
    }
    fl = [FLOOR - r['lowest_px'] for r in recs if r['phase'] == 'flight']
    if fl:
        out['flight_clearance_px'] = min(fl)
    if spec['gait'] != 'run':
        planted = []
        for leg, start in (('near', 0), ('far', 4)):
            xs = []
            for k in range(5):
                t = recs[(start + k) % 8]['toe_x_px']
                xs.append(t['stance'] if k < 4 or t['rear'] is None else t['rear'])
            planted.append({'leg': leg, 'toe_x_px': xs, 'retreat_px': [round(xs[i] - xs[i + 1], 1) for i in range(4)]})
        out['planted_toes'] = planted
    out['frames'] = recs
    return out


# ---------------------------------------------------------------- per character
def render_frame(P, pose, cam, props, robe=None, fit_cam=True, **kw):
    body = fk(P, pose, props=props, robe=robe)
    if fit_cam:
        cam.fit(body)
    img, mask = render(body, P, cam, **kw)
    return body, img, mask


def idle_frame(P, cam, carry, key):
    """the fitted mannequin in the idle stance with its props (contact sheet): the READY grip when the character has one,
    else the run carry at phase 0"""
    pose = fitmod.idle_pose(P)
    feet = pose.pop('_feet')
    pose, _ = lock_feet(P, pose, cam, feet)
    if carry.get('ready'):
        keys = warrior_attack(P, carry)
        props = keys[0]['props']
        pose = solve_arms(P, pose, cam, keys[0]['arms'], props)
    else:
        props = carry_props(carry, 0.0)
        two_hand(P, pose, carry, props)
    _, img, mask = render_frame(P, pose, cam, props)
    return img, mask


def build_char(key, carry, out, yaw, chest_open, log, allow_coarse=False):
    carry = dict(carry)
    carry.setdefault('chest_open', chest_open)
    sid = carry['sheet']
    P, rep, (rgb, mask, info) = fitmod.fit(sid, yaw, override=carry.get('fit_override'))
    od = os.path.join(out, key)
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'fit.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, ensure_ascii=False, default=fitmod.jsonable)
    results = []
    if rep['coarse_source']:
        results.append((checks.WARN if allow_coarse else checks.FAIL,
                        f'fit source is the COARSE fallback ({rep["source"]}): the accepted idle drawing is not in this '
                        'checkout nor on origin/art-inbox (git fetch origin art-inbox). Guides for a painter need the drawing'
                        + (' (--allow-coarse given)' if allow_coarse else ' - rerun with it, or --allow-coarse for a look only')))
    else:
        results.append((checks.OK, f'fit source: {rep["source"]}'))
    scale = sheet_scale(sid)
    cam = Camera(yaw=yaw)
    spec = gait_spec(carry['gait'], scale, leg_factor(P))
    frames = gait_frames(spec, P, cam, carry, n=8)
    # robe: a first pass without the robe gives the legs; the hem follows them (robe_hems), then the real render
    robes = [None] * 8
    if carry.get('robe'):
        robes = robe_hems(spec, P, [fk(P, pose) for pose, _ in frames])
    slots, plain, masks, recs, cells, bodies = [], [], [], [], [], []
    for i, (pose, meta) in enumerate(frames):
        body, img, m = render_frame(P, pose, cam, meta['props'], robes[i])
        _, img_p, _ = render_frame(P, pose, cam, meta['props'], robes[i], joints=False, ground=False)
        slots.append(img)
        plain.append(img_p)
        masks.append(m)
        bodies.append(body)
        origin = (meta['slot'] - 1) * SLOT_W if spec['gait'] == 'run' else 0
        recs.append(frame_record(body, cam, m, spec, meta, pose, origin))
        cells.append(game_cell(img_p, scale))
    s = spec['set']
    strip_of(slots[:4]).save(os.path.join(od, f'{s}_a.png'))
    strip_of(slots[4:]).save(os.path.join(od, f'{s}_b.png'))
    strip_of(plain[:4]).save(os.path.join(od, f'{s}_plain_a.png'))
    strip_of(plain[4:]).save(os.path.join(od, f'{s}_plain_b.png'))
    with open(os.path.join(od, 'pose.json'), 'w', encoding='utf-8') as f:
        json.dump(gait_pose_json(spec, P, cam, carry, recs, rep, scale), f, indent=1, ensure_ascii=False)
    save_gif([on_bg(c, floor_y=ANCHOR[1]) for c in cells], os.path.join(od, f'{s}_game_x1.gif'), spec['ms'])
    save_gif([on_bg(c, floor_y=ANCHOR[1]).resize((CELL * 4, CELL * 4), Image.Resampling.NEAREST) for c in cells],
             os.path.join(od, f'{s}_game_x4.gif'), spec['ms'])
    save_gif([im.crop((0, 380, SLOT_W, 900)) for im in slots], os.path.join(od, f'{s}_guide.gif'), spec['ms'])
    smooth_frames = gait_frames(spec, P, cam, carry, n=24)
    srobes = robe_hems(spec, P, [fk(P, p) for p, _ in smooth_frames]) if carry.get('robe') else [None] * 24
    smooth = []
    for (pose, meta), rb in zip(smooth_frames, srobes):
        _, im, _ = render_frame(P, pose, cam, meta['props'], rb)
        smooth.append(im.crop((0, 380, SLOT_W, 900)).resize((SLOT_W // 2, 260), Image.Resampling.BOX))
    save_gif(smooth, os.path.join(od, f'{s}_smooth.gif'), int(round(spec['ms'] * 8 / 24)))
    report.contact_sheet(key, rgb, mask, info, P, cam, rep, os.path.join(od, 'contact.png'), idle_frame(P, cam, carry, key))
    results.append((checks.OK, f"stride: step {spec['step_px']} source px = {round(spec['step_px'] * scale, 1)} game px at "
                               f"scale {scale} (class {spec['stride_game_class']}, leg factor {spec['leg_factor']} -> used "
                               f"{spec['leg_factor_used']})"))
    results += checks.gait_checks(spec, recs, bodies, plain, cam, carry)
    log(f'{key}: {sid} gait {carry["gait"]} ({spec["class"]}) -> {od}')
    for lv, msg in results:
        log(f'   [{lv}] {msg}')
    res = {'dir': od, 'checks': results, 'recs': recs, 'slots': slots, 'plain': plain, 'masks': masks, 'P': P, 'rep': rep,
           'info': info, 'cam': cam, 'carry': carry, 'scale': scale}
    for act in carry.get('actions', []):
        ar = build_action(act, key, P, cam, carry, od, scale)
        for lv, msg in ar:
            log(f'   [{lv}] {msg}')
        results += ar
    return res


def feet_centre_dx(body, cam):
    """camera dx that puts the feet centre (sole extents of both feet) on the hip column x=192: pose_feet_x of
    tools/art/sheets.py places attack / hit cells by their feet the same way"""
    xs = [(cam.V @ body.joints[k + s])[0] for k in ('heel', 'toetip') for s in 'NF']
    return -(min(xs) + max(xs)) / 2


def build_action(act, key, P, cam_run, carry, od, scale):
    fn, ms = ACTIONS[act]
    cam = Camera(yaw=cam_run.yaw, lock_hip=False)
    frames = action_frames(fn(P, carry), P, cam)
    imgs, plain, names, recs, bodies, cams, shifts = [], [], [], [], [], [], []
    for nm, pose, props, is_key, ok in frames:
        body = fk(P, pose, props=props)
        c = Camera(yaw=cam_run.yaw, lock_hip=False)
        c.dx = feet_centre_dx(body, c)
        # the sheets' rule: feet centre on the anchor; a pose that sticks out of the band is pushed in (logged)
        ip0, _ = render(body, P, c, joints=False, ground=False)
        a_, b_ = checks.extent_x(ip0)
        push = 0
        if b_ - a_ <= checks.BAND[1] - checks.BAND[0]:
            if a_ < checks.BAND[0]:
                push = checks.BAND[0] - a_
            elif b_ > checks.BAND[1]:
                push = checks.BAND[1] - b_
        c.dx += push
        shifts.append(push)
        im, m = render(body, P, c)
        ip, _ = render(body, P, c, joints=False, ground=False)
        imgs.append(im)
        plain.append(ip)
        names.append(nm)
        bodies.append(body)
        cams.append(c)
        J = project_joints(body, c, JOINTS_OUT)
        recs.append({'frame': nm, 'key': is_key, 'ik_reached': bool(ok), 'joints': J,
                     'feet_centre_x': round(HIP_X - push, 1), 'pushed_in_px': push,
                     'top_px': int(np.flatnonzero(m.any(1)).min()), 'lowest_px': int(np.flatnonzero(m.any(1)).max()),
                     'angles_deg': {k: round(v, 2) for k, v in full_pose(pose).items() if not k.startswith('_')},
                     'props': props})
    if act == 'attack':
        imgs[0].save(os.path.join(od, 'attack_ready.png'))
        use = list(range(1, len(imgs)))         # windup, in-betweens, strike
    else:
        use = list(range(len(imgs)))
    n = max(4, len(use)) if act == 'attack' else 2
    strip_of([imgs[i] for i in use], n=n).save(os.path.join(od, f'{act}_a.png'))
    strip_of([plain[i] for i in use], n=n).save(os.path.join(od, f'{act}_plain_a.png'))
    cells = [game_cell(plain[i], scale) for i in use]
    save_gif([on_bg(c, floor_y=ANCHOR[1]).resize((CELL * 4, CELL * 4), Image.Resampling.NEAREST) for c in cells],
             os.path.join(od, f'{act}_game_x4.gif'), ms)
    save_gif([on_bg(c, floor_y=ANCHOR[1]) for c in cells], os.path.join(od, f'{act}_game_x1.gif'), ms)
    save_gif([imgs[i].crop((0, 300, SLOT_W, 900)) for i in use], os.path.join(od, f'{act}_guide.gif'), ms)
    with open(os.path.join(od, f'{act}_pose.json'), 'w', encoding='utf-8') as f:
        json.dump({'set': f'{act}3d__{key}', 'baseline': FLOOR, 'scale': scale,
                   'placement': 'each frame: feet centre (sole extents of both feet) on x=192, pushed in only when it '
                                'would leave the slot band 32..351 (tools/art/sheets.py pose_feet_x / place)',
                   'frames': [recs[i] for i in use], 'ready': recs[0] if act == 'attack' else None,
                   'source': 'tools/mannequin3d (build.py) 3D mannequin guide - a MANNEQUIN, never game art'},
                  f, indent=1, ensure_ascii=False)
    out = checks.action_checks(act, names, bodies, plain, recs, lambda i: cams[i])
    if any(shifts):
        out.append((checks.WARN, f'{act}: pushed into the band (px, like sheets.py place) {dict(zip(names, shifts))}'))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('--carry', default=CARRY_JSON, help='per-character carry spec (default specs/carry3d.json)')
    ap.add_argument('--chars', nargs='+')
    ap.add_argument('--yaw', type=float, default=15.0, help='camera turn toward the viewer (deg), the slight 3/4 look')
    ap.add_argument('--chest-open', type=float, default=30.0, help='extra chest turn toward the viewer (deg)')
    ap.add_argument('--allow-coarse', action='store_true',
                    help='allow the coarse fit fallback (registered 96 px cell blown up) - for a look, not for a painter')
    a = ap.parse_args(argv)
    chars = load_carry(a.carry)
    os.makedirs(a.out, exist_ok=True)
    logs = []

    def log(s):
        print(s)
        logs.append(s)
    results = {}
    for key in a.chars or list(chars):
        results[key] = build_char(key, chars[key], a.out, a.yaw, a.chest_open, log, a.allow_coarse)
    if 'warrior' in results:
        r = results['warrior']
        if report.inbox_run_strips(r['info']['stem']) is None:
            msg = ('[WARN] compare: the large drawn run strips (art/inbox/gait/sheet_class_warrior_run_a/b.png) are in neither '
                   'this checkout nor origin/art-inbox - compare_run.png has only the registered 96 px cells')
            log(msg)
            r['checks'].append((checks.WARN, msg))
        stats = report.compare_run(r['plain'], r['masks'], r['carry']['sheet'], r['info']['stem'],
                                   os.path.join(r['dir'], 'compare_run.png'), os.path.join(r['dir'], 'compare_run.json'))
        for row in ('registered', 'inbox'):
            v = [s['iou_body'] for s in stats if s['row'] == row]
            if v:
                log(f'warrior compare ({row}): silhouette IoU per frame {v}, mean {np.mean(v):.3f}')
        report.vs_v2(r, log)
    fails = [(k, m) for k, r in results.items() for lv, m in r['checks'] if lv == checks.FAIL]
    log(f'SUMMARY: {len(fails)} FAIL' + ''.join(f'\n   {k}: {m}' for k, m in fails))
    with open(os.path.join(a.out, 'build_log.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(logs) + '\n')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
