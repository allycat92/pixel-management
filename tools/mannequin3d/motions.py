"""Keyframed motions for the 3D mannequin, authored as joint-angle tables (degrees, see rig.py for the conventions).

Gaits (8 frames a cycle, frame k at cycle phase k/8; the far leg / far arm run half a cycle behind the near ones):
  run_light  R1..R8  contact, down, push-off, FLIGHT        (art/requests/guides/run_base/v2: 80 ms, step 275 px)
  run_heavy  H1..H8  contact (both feet), down, passing, push (heavy_base/v1: 101 ms, step 142.5 px, no flight)
  run_robe   G1..G8  contact (both feet), down, passing, push (robe_base/v1: 96 ms, step 134.2 px, no flight)

How a gait frame is made:
  1. the SWING leg (off the floor) comes straight from the table SWING: thigh angle, knee bend, foot pitch;
  2. the STANCE leg is foot-locked: its toe tip sits on the floor (toe0 - 2*step*phase) / cos(yaw) in front of the hip
     midpoint (world x), i.e. exactly step/4 further back every cell on screen - the rule the engine needs to keep feet
     planted (js/battle.js runCells moves the unit step/4 per stance cell). Both legs use the same WORLD rule, so the
     two halves of the cycle mirror exactly (same knee bend); on screen the 3/4 yaw puts the near toe 5 px behind and the
     far toe 5 px in front of the mid-plane value. A 2-bone IK (rig.leg_ik) finds thigh + knee, the table's
     STANCE_PITCH gives the foot angle (heel rising at push-off);
  3. hip height, lean, chest counter-turn come from the per-frame tables; arms and props from the character's carry
     (specs/carry3d.json: arm swing with a lag, prop swing with a lag, two-hand grips);
  4. the 8 key frames are joined by periodic Catmull-Rom splines, so any number of in-between frames can be sampled
     (stance legs are re-solved with IK at every sampled phase). With n = 8 the frames ARE the table rows.
The numbers were read off the accepted 2D mannequins (pose.json of the three base sets: hip heights, lean, toe x,
swing-leg thigh/knee angles) so the 3D motion keeps the same rhythm, stride and cadence; arms were re-authored in 3D.

Stride: gait_spec() = the class's GAME stride / the sheet's scale (x the fitted leg factor when > 5% off), so the
registered runStride stays the class stride at any sheet scale and short-legged bodies keep a bent stance knee.
Actions (warrior_attack, warrior_hit): frames with both feet locked to the floor, the sword arm solved by arm IK to a
fist target per frame (relative to the head, shoulder, hip or - READY - the idle drawing's own grip), blade angles
per frame; in-between bodies by eased interpolation.
"""
import copy
import math

import numpy as np

from rig import leg_ik, fk, full_pose, CANON, ankle_on_floor, arm_ik, WEAPONS, WEAPON_LIMIT

CANON_LEG = CANON['thigh'] + CANON['shin'] + CANON['ankle_h']
CANON_SCALE = 0.1654          # the scale the gait tables (and v2 / heavy_base / robe_base) were made for
LEG_DEADBAND = 0.05           # a fitted leg within 5% of the canonical leg keeps the class stride exactly
ARM_PHASE = -0.1              # the near arm swings furthest forward at cycle phase 0.4 (the light table's R4)

GAITS = {
    'run_light': {
        'set': 'run3d_light', 'gait': 'run', 'class': 'light', 'prefix': 'R', 'ms': 80, 'step_px': 275.0,
        'phases': ['contact', 'down', 'push-off', 'flight'],
        'stance': [0.0, 0.125, 0.25],          # leg phases with the foot on the floor
        'toe0': 98.0,                          # toe tip x (screen px from the hip column) at contact
        'stance_pitch': [3.0, 0.0, -16.0],
        'hip_h': [180.0, 178.4, 182.2, 183.9],  # hip joint height for the canonical leg (v2), per half-cycle frame
        'lean': [24.0, 19.4, 29.1, 31.4],
        # leg phase -> (thigh, knee, foot pitch) while the foot is up (pitch absolute: 0 = sole level, - = toes down)
        # 0.625 (the far leg in R2 / near in R6): thigh 2 (was 10) so its knee sits clearly behind the stance knee
        'swing': {0.375: (-14.0, 72.0, -120.0), 0.5: (-6.0, 114.0, -145.0), 0.625: (0.0, 130.0, -125.0),
                  0.75: (60.0, 110.0, -45.0), 0.875: (55.0, 44.0, 15.0)},
        # near arm per frame (its far twin is half a cycle later): shoulder (from the torso axis), elbow
        'arm': [(-22.0, 80.0), (14.0, 92.0), (40.0, 104.0), (46.0, 108.0), (28.0, 100.0), (-18.0, 86.0),
                (-34.0, 80.0), (-36.0, 78.0)],
        'pelvis_twist': 7.0, 'chest_counter': 6.0, 'head_pitch': 4.0,
        'min_flight_px': 18,
    },
    'run_heavy': {
        'set': 'run3d_heavy', 'gait': 'heavy', 'class': 'heavy', 'prefix': 'H', 'ms': 101, 'step_px': 142.5,
        'phases': ['contact', 'down', 'passing', 'push'],
        'stance': [0.0, 0.125, 0.25, 0.375, 0.5],
        'toe0': 83.0,
        'stance_pitch': [0.0, 0.0, 0.0, -8.0, -26.0],
        'hip_h': [180.0, 172.9, 177.8, 179.5],
        'lean': [5.0, 5.6, 5.0, 4.8],
        # passing (leg phase 0.75 = H3 far / H7 near): the swing foot is carried ahead of the stance foot (ankles ~20 px
        # apart; was 36 deg -> 11 px, one blob) with the sole 13 px up (the class's 5-13 px knee-lift band)
        'swing': {0.625: (14.0, 72.0, -18.0), 0.75: (41.0, 72.0, -8.0), 0.875: (40.0, 48.0, 4.0)},
        'arm': [(-4.0, 70.0), (-5.0, 66.0), (-2.0, 68.0), (2.0, 72.0), (4.0, 70.0), (5.0, 66.0), (2.0, 68.0), (-2.0, 72.0)],
        'pelvis_twist': 4.0, 'chest_counter': 2.0, 'head_pitch': 2.0,
    },
    'run_robe': {
        'set': 'run3d_robe', 'gait': 'robe', 'class': 'robe', 'prefix': 'G', 'ms': 96, 'step_px': 134.2,
        'phases': ['contact', 'down', 'passing', 'push'],
        'stance': [0.0, 0.125, 0.25, 0.375, 0.5],
        'toe0': 87.0,
        'stance_pitch': [0.0, 0.0, 0.0, -8.0, -24.0],
        'hip_h': [182.2, 180.5, 185.0, 185.5],
        'lean': [7.1, 7.6, 6.8, 6.8],
        # passing (0.75 = G3 / G7): swing foot ahead of the stance foot, sole 13 px up (was 29 deg: ankles 3 px apart)
        'swing': {0.625: (8.0, 60.0, -15.0), 0.75: (38.0, 62.0, -4.0), 0.875: (34.0, 38.0, 4.0)},
        'arm': [(-10.0, 72.0), (-12.0, 76.0), (-4.0, 74.0), (6.0, 72.0), (10.0, 72.0), (12.0, 76.0), (4.0, 74.0), (-6.0, 72.0)],
        'pelvis_twist': 4.0, 'chest_counter': 3.0, 'head_pitch': 2.0,
        # robe proxy: hem height (robe_base v1: 38-52 px, check fail < 38), hem corner lift, margins around the leading
        # knee / trailing heel; the hem follows one cell late when the legs close (robe_base hem lag)
        'robe': {'hem_h': 42.0, 'lift_front': 6.0, 'lift_back': 8.0, 'knee_margin': 18.0, 'heel_margin': 14.0,
                 'max_change': 0.15},
    },
}


def leg_factor(P):
    return (P['thigh'] + P['shin'] + P['ankle_h']) / CANON_LEG


def gait_spec(name, scale=CANON_SCALE, legs=1.0):
    """the gait table for one character: the stride is the class's GAME stride (step_px x 0.1654) divided by the sheet's
    own scale, times the fitted leg factor when it is more than 5% off the canonical leg (a goblin's legs are 17% shorter
    -> a 17% shorter stride, so the stance knee keeps its bend). toe0 follows the stride."""
    spec = copy.deepcopy(GAITS[name])
    lf = legs if abs(legs - 1.0) > LEG_DEADBAND else 1.0
    k = (CANON_SCALE / scale) * lf
    spec['stride_game_class'] = round(spec['step_px'] * CANON_SCALE, 2)
    spec['step_px'] = round(spec['step_px'] * k, 2)
    spec['toe0'] = spec['toe0'] * k
    spec.update({'scale': scale, 'stride_k': round(k, 4), 'leg_factor': round(legs, 4), 'leg_factor_used': round(lf, 4)})
    return spec


def catmull_periodic(keys, t):
    """keys = values at k/len, periodic; t in [0,1)"""
    n = len(keys)
    x = (t % 1.0) * n
    i = int(math.floor(x)) % n
    u = x - math.floor(x)
    p0, p1, p2, p3 = (np.asarray(keys[(i + d) % n], float) for d in (-1, 0, 1, 2))
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def interp_linear(keys_t, keys_v, t):
    return float(np.interp(t, keys_t, keys_v))


def _stance_target(spec, psi):
    """toe tip x (screen px from the hip column, for a foot on the body's mid plane) and foot pitch at leg phase psi"""
    toe_tip = spec['toe0'] - 2.0 * spec['step_px'] * psi
    pitch = interp_linear(spec['stance'], spec['stance_pitch'], psi)
    return toe_tip, pitch


def _solve_stance(P, pose, side, toe_tip_screen, pitch, cam):
    """IK one stance leg so that its toe tip lands on the floor at toe_tip_screen / cos(yaw) in front of the hip midpoint
    (world x). Both legs use the SAME world rule, so the far leg at phase psi mirrors the near leg at phase psi exactly
    (same knee bend); on screen the 3/4 yaw then puts the near toe s*hip_w behind and the far toe s*hip_w in front of the
    mid-plane value - a constant per leg, so each planted foot still retreats exactly step/4 a cell."""
    q = full_pose(pose)
    q['abd_' + side] = 0.0
    body = fk(P, q)
    hip = body.joints['H' + side]
    hip_mid = body.joints['hip']
    c = math.cos(math.radians(cam.yaw))
    ank = ankle_on_floor(P, np.array([hip_mid[0] + toe_tip_screen / c, 0.0, hip[2]]), pitch)
    thigh, knee, ok = leg_ik(P, hip[:2], ank[:2])
    return thigh, knee, pitch - (thigh - knee), ok


def _solve_stances(spec, P, pose, phi, cam):
    stance, ok_all = [], True
    for side, off in (('N', 0.0), ('F', 0.5)):
        psi = round((phi + off) % 1.0, 6)
        if psi <= spec['stance'][-1] + 1e-6:
            tip, pitch = _stance_target(spec, psi)
            th, kn, an, ok = _solve_stance(P, pose, side, tip, pitch, cam)
            pose['thigh_' + side], pose['knee_' + side], pose['ankle_' + side] = th, kn, an
            pose['abd_' + side] = 0.0
            stance.append(side)
            ok_all &= ok
    return stance, ok_all


def gait_keys(spec, P, cam, carry):
    """the 8 key poses of a gait (dicts), with meta. Stance legs solved by IK."""
    k_leg = leg_factor(P)
    rows = []
    for f in range(8):
        phi = f / 8.0
        half = f % 4
        L = spec['lean'][half]
        cc = carry.get('chest_counter', spec['chest_counter'])
        pose = {
            'hip_h': spec['hip_h'][half] * k_leg,
            # 1.2 x the table lean: the screen lean (hip -> neck base) of the turned, curved trunk comes out ~0.83 x
            'pelvis_pitch': L * 0.5, 'spine_pitch': L * 0.35, 'chest_pitch': L * 0.35,
            'pelvis_yaw': carry.get('pelvis_yaw', 0.0) - spec['pelvis_twist'] * math.cos(2 * math.pi * phi),
            'chest_yaw': carry.get('chest_open', 30.0) + cc * math.cos(2 * math.pi * phi) * 2,
            'head_pitch': spec['head_pitch'],
            'neck_pitch': -L * 0.5,
        }
        for side, off in (('N', 0.0), ('F', 0.5)):
            psi = round((phi + off) % 1.0, 4)
            if psi in spec['swing']:
                th, kn, pitch = spec['swing'][psi]
                pose['thigh_' + side], pose['knee_' + side], pose['ankle_' + side] = th, kn, pitch - (th - kn)
        for side in 'NF':
            arm_f = (f + (0 if side == 'N' else 4)) % 8
            sh, el = spec['arm'][arm_f]
            pose['shoulder_' + side], pose['elbow_' + side] = sh, el
        meta = {'hip_lowered': 0.0}
        for _ in range(13):        # a stance foot out of reach: lower the hip by 0.5 px steps (at most 6 px), report it
            stance, ok_all = _solve_stances(spec, P, pose, phi, cam)
            if ok_all:
                break
            pose['hip_h'] -= 0.5
            meta['hip_lowered'] += 0.5
        meta.update({'stance': stance, 'reached': ok_all})
        carry_arms(pose, carry, phi)
        rows.append((pose, meta))
    return rows


# ------------------------------------------------------------------ carry (per character, from specs/carry3d.json)
def wave(phi, side, lag_frames=0.0):
    """arm swing wave in -1..1: the near arm is furthest forward at phase 0.4 (+lag), the far arm half a cycle later"""
    v = -math.cos(2 * math.pi * (phi - ARM_PHASE - lag_frames / 8.0))
    return v if side == 'N' else -v


def carry_arms(pose, carry, phi):
    """arms: shoulder = table_scale x the gait table's shoulder + shoulder + swing x wave; elbow = elbow (+ elbow_swing x
    wave) or the table's; the wave lags the legs by `lag` frames (secondary motion)"""
    for side in 'NF':
        a = (carry.get('arms') or {}).get(side)
        if not a:
            continue
        w = wave(phi, side, a.get('lag', 0.0))
        pose['shoulder_' + side] = (a.get('table_scale', 1.0) * pose['shoulder_' + side] + a.get('shoulder', 0.0)
                                    + a.get('swing', 0.0) * w)
        if a.get('elbow') is not None:
            pose['elbow_' + side] = a['elbow'] + a.get('elbow_swing', 0.0) * w
        if a.get('wrist') is not None:
            pose['wrist_' + side] = a['wrist']
        if a.get('abd') is not None:
            pose['arm_abd_' + side] = a['abd']


def weapon_limit(carry):
    """[min, max] of the hand's weapon range (deg from the forearm line, + = upward) - carry3d.json `weapon_limit`"""
    lim = (carry or {}).get('weapon_limit') or {}
    return [float(lim.get('min', WEAPON_LIMIT[0])), float(lim.get('max', WEAPON_LIMIT[1]))]


def carry_props(carry, phi):
    """the props for cycle phase phi: a weapon's abs_angle swings `swing` deg with its hand's wave, `lag` frames late;
    every weapon carries the character's hand range (`limit`, enforced by rig.add_prop)"""
    out = []
    for pr in carry.get('props', []):
        p = {k: v for k, v in pr.items() if k not in ('swing', 'lag', 'measured')}
        if p.get('kind') in WEAPONS:
            p['limit'] = weapon_limit(carry)
        if pr.get('swing') and p.get('abs_angle') is not None:
            p['abs_angle'] = p['abs_angle'] + pr['swing'] * wave(phi, pr.get('hand', 'N'), pr.get('lag', 0.0))
        if pr.get('swing') and p.get('kind') == 'shield':
            p['face'] = p.get('face', 30.0) + pr['swing'] * wave(phi, pr.get('hand', 'F'), pr.get('lag', 0.0))
        out.append(p)
    return out


def two_hand(P, pose, carry, props):
    """second hand on a staff / two-handed weapon: carry['two_hand'] = {'prop': index, 'other': 'F', 'along': px}
    -> the other wrist is IK'd onto the prop line `along` px past the holding hand"""
    th = carry.get('two_hand')
    if not th:
        return
    body = fk(P, pose, props=props)
    J = body.joints
    pr = props[th.get('prop', 0)]
    d = J['prop_dir_' + pr.get('kind', 'staff')]       # the direction after the hand's range limit
    target = J['hand' + pr.get('hand', 'N')] + d * th.get('along', 40.0)
    side = th.get('other', 'F')
    sh, el = arm_ik(P, pose, J['S' + side], target - (J['hand' + side] - J['wri' + side]))
    pose['shoulder_' + side], pose['elbow_' + side] = sh, el
    pose['arm_abd_' + side] = th.get('abd', 0.0)


CHANNELS = ['hip_h', 'pelvis_pitch', 'spine_pitch', 'chest_pitch', 'pelvis_yaw', 'chest_yaw', 'head_pitch', 'neck_pitch',
            'thigh_N', 'knee_N', 'ankle_N', 'thigh_F', 'knee_F', 'ankle_F',
            'shoulder_N', 'elbow_N', 'shoulder_F', 'elbow_F', 'wrist_N', 'wrist_F', 'arm_abd_N', 'arm_abd_F']


def gait_frames(spec, P, cam, carry, n=8):
    """sample n frames of a gait cycle -> list of (pose, meta); meta has phase, stance, frame name and the props"""
    keys = gait_keys(spec, P, cam, carry)
    out = []
    for i in range(n):
        phi = i / n
        pose = {}
        for ch in CHANNELS:
            vals = [full_pose(k[0])[ch] for k in keys]
            pose[ch] = float(catmull_periodic(vals, phi))
        stance, reached = _solve_stances(spec, P, pose, phi, cam)
        props = carry_props(carry, phi)
        two_hand(P, pose, carry, props)
        k = i * 8 / n
        meta = {'phi': phi, 'stance': stance, 'reached': reached, 'props': props, 'key': abs(k - round(k)) < 1e-9}
        if meta['key']:
            f = int(round(k)) % 8
            meta.update({'frame': f'{spec["prefix"]}{f + 1}', 'phase': spec['phases'][f % 4], 'slot': f % 4 + 1,
                         'strip': 'a' if f < 4 else 'b', 'hip_lowered': keys[f][1]['hip_lowered']})
        out.append((pose, meta))
    return out


def robe_hems(spec, P, bodies):
    """hem of the robe proxy per frame (a cycle, in order): front edge = the leading knee + margin, back edge = the
    trailing heel - margin; the hem pushes out at once but falls back one cell late (robe_base), and its width never
    changes by more than max_change between neighbouring frames (no balloon)."""
    r = spec['robe']
    n = len(bodies)
    raw = []
    for b in bodies:
        J = b.joints
        front = max(J['kneeN'][0], J['kneeF'][0]) + P['r_thigh'][1] + r['knee_margin']
        back = min(J['heelN'][0], J['heelF'][0]) - P['r_foot'] - r['heel_margin']
        raw.append([front, back, J['hip'][0]])
    raw = np.array(raw)
    front = np.array([max(raw[i, 0], raw[i - 1, 0]) for i in range(n)])
    back = np.array([min(raw[i, 1], raw[i - 1, 1]) for i in range(n)])
    mid, half = (front + back) / 2, (front - back) / 2
    lim = 1.0 + r['max_change']
    for _ in range(50):
        changed = False
        for i in range(n):
            j = (i + 1) % n
            hi, lo = (i, j) if half[i] > half[j] else (j, i)
            if half[hi] > lim * half[lo] + 1e-6:
                g = math.sqrt(half[hi] * half[lo])
                half[hi], half[lo] = g * math.sqrt(lim), g / math.sqrt(lim)
                changed = True
        if not changed:
            break
    depth = P['hip_w'] + P['r_thigh'][0] + 14.0
    return [{'hem_h': r['hem_h'], 'front': mid[i] + half[i], 'back': mid[i] - half[i], 'depth': max(depth, 0.5 * half[i]),
             'lift_front': r['lift_front'], 'lift_back': r['lift_back']} for i in range(n)]


# ------------------------------------------------------------------ actions
def ease(u):
    return u * u * (3 - 2 * u)


def lerp_pose(a, b, u):
    fa, fb = full_pose(a), full_pose(b)
    return {k: fa[k] + (fb[k] - fa[k]) * u for k in fa}


def lock_feet(P, pose, cam, feet, max_lower=14.0):
    """solve both legs with IK so the toe tips sit on the floor at feet = {'N': (tip_x_world, pitch), 'F': ...};
    if a foot is out of reach the hip is lowered 1 px at a time (at most max_lower px). -> (pose, reached)"""
    pose = dict(pose)
    lowered = 0.0
    while True:
        q = full_pose(pose)
        body = fk(P, q)
        ok_all = True
        for side, (tip_x, pitch) in feet.items():
            hip = body.joints['H' + side]
            ank = ankle_on_floor(P, np.array([tip_x, 0.0, hip[2]]), pitch)
            th, kn, ok = leg_ik(P, hip[:2], ank[:2])
            pose['thigh_' + side], pose['knee_' + side], pose['ankle_' + side] = th, kn, pitch - (th - kn)
            pose['abd_' + side] = 0.0
            ok_all &= ok
        if ok_all or lowered >= max_lower:
            break
        pose['hip_h'] = full_pose(pose)['hip_h'] - 1.0
        lowered += 1.0
    pose['_hip_lowered'] = lowered
    return pose, ok_all


def arm_target(P, pose, cam, side, tgt, props):
    """world wrist target for an arm spec: ('head', dx, dy) from the head centre, ('shoulder', dx, dy) from that
    shoulder, ('hip', dx, dy) from the hip midpoint (x forward, y up, world px), or ('feet', x, h) = screen x relative
    to the feet centre and height above the floor (the idle drawing's own coordinates: anchor column, floor)."""
    body = fk(P, pose, props=props)
    J = body.joints
    kind, dx, dy = tgt
    if kind == 'feet':
        c, s = math.cos(math.radians(cam.yaw)), math.sin(math.radians(cam.yaw))
        xs = [c * J[k + sd][0] - s * J[k + sd][2] for k in ('heel', 'toetip') for sd in 'NF']
        fc = (min(xs) + max(xs)) / 2
        z = J['S' + side][2]
        hand = np.array([(fc + dx + s * z) / c, dy, z])
    else:
        ref = {'head': J['head'], 'shoulder': J['S' + side], 'hip': J['hip']}[kind]
        hand = ref + np.array([dx, dy, 0.0])
    return hand - (J['hand' + side] - J['wri' + side])


def solve_arms(P, pose, cam, arms, props):
    for side, tgt in (arms or {}).items():
        if tgt[0] == 'angles':
            pose['shoulder_' + side], pose['elbow_' + side] = tgt[1], tgt[2]
            continue
        for _ in range(2):        # the hand offset depends on the arm itself: one refinement pass
            body = fk(P, pose, props=props)
            sh, el = arm_ik(P, pose, body.joints['S' + side], arm_target(P, pose, cam, side, tgt, props))
            pose['shoulder_' + side], pose['elbow_' + side] = sh, el
    return pose


def action_frames(keys, P, cam):
    """keys = list of dicts {name, pose, props, feet, arms, key}: legs foot-locked, arms solved to their targets.
    -> list of (name, pose, props, key?, reached)"""
    out = []
    for k in keys:
        p, ok = lock_feet(P, k['pose'], cam, k['feet'])
        p = solve_arms(P, p, cam, k.get('arms'), k['props'])
        out.append((k['name'], p, k['props'], k.get('key', True), ok))
    return out


def _sword(abs_angle, carry):
    sw = next((p for p in carry.get('props', []) if p.get('kind') == 'sword'), {})
    sh = next((p for p in carry.get('props', []) if p.get('kind') == 'shield'), {'hand': 'F', 'kind': 'shield'})
    sword = {'hand': 'N', 'kind': 'sword', 'abs_angle': abs_angle, 'length': sw.get('length', 150.0), 'back': sw.get('back', 22.0),
             'limit': weapon_limit(carry)}
    shield = {k: v for k, v in sh.items() if k not in ('swing', 'lag', 'measured')}
    return [sword, shield]


def warrior_attack(P, carry):
    """overhead sword swing (sheet cells 4-5): READY (the idle's grip) -> WINDUP (key: fist up behind the head, blade
    cocked back and up ~45 deg) -> 1/3 (fist over the head, blade vertical) -> 2/3 (fist over the brow, blade level
    forward, above the head) -> STRIKE (key: arm forward and down, blade forward and down). Only the strike points
    down. The body stays over its feet (feet centre = the sheet anchor) so the whole swing fits the slot band."""
    k = leg_factor(P)
    hr = P['head_r']
    feet = {'N': (-52.0 * k, -8.0), 'F': (100.0 * k, 0.0)}
    feet_lunge = {'N': (-52.0 * k, -26.0), 'F': (100.0 * k, 0.0)}
    co = carry.get('chest_open', 30.0)
    base = {'chest_yaw': co, 'head_pitch': 6.0, 'arm_abd_N': 8, 'arm_abd_F': 10}
    rd = carry.get('ready', {})
    ready = dict(base, hip_h=166 * k, x=0.0, pelvis_pitch=6, spine_pitch=4, chest_pitch=4, wrist_N=0)
    windup = dict(base, hip_h=170 * k, x=-2.0 * k, pelvis_pitch=-2, spine_pitch=-4, chest_pitch=-4, chest_yaw=co + 10,
                  head_pitch=2, wrist_N=0)
    strike = dict(base, hip_h=154 * k, x=2.0 * k, pelvis_pitch=12, spine_pitch=8, chest_pitch=6, chest_yaw=co - 12,
                  head_pitch=4, wrist_N=0)
    u1, u2 = ease(1 / 3), ease(2 / 3)
    ff = lambda u: {s: (feet[s][0], feet[s][1] + (feet_lunge[s][1] - feet[s][1]) * u) for s in feet}
    keys = [
        {'name': 'ready', 'pose': ready, 'feet': feet, 'props': _sword(rd.get('blade_deg', 38.0), carry),
         'arms': {'N': ('feet', *rd.get('hand_N', [-25.0, 191.0])), 'F': ('angles', 34.0, 104.0)}},
        {'name': 'windup', 'pose': windup, 'feet': feet, 'props': _sword(135.0, carry),
         'arms': {'N': ('head', -hr[0] * 0.6, hr[1] * 0.8), 'F': ('angles', 44.0, 100.0)}},
        {'name': 'windup>strike 1/3', 'key': False, 'pose': lerp_pose(windup, strike, u1), 'feet': ff(u1),
         'props': _sword(95.0, carry), 'arms': {'N': ('head', -hr[0] * 0.1, hr[1] + 20.0), 'F': ('angles', 34.0, 96.0)}},
        {'name': 'windup>strike 2/3', 'key': False, 'pose': lerp_pose(windup, strike, u2), 'feet': ff(u2),
         'props': _sword(12.0, carry), 'arms': {'N': ('head', hr[0] * 0.1, hr[1] + 16.0), 'F': ('angles', 10.0, 90.0)}},
        {'name': 'strike', 'pose': strike, 'feet': feet_lunge, 'props': _sword(-50.0, carry),
         'arms': {'N': ('shoulder', 58.0 * k, -74.0 * k), 'F': ('angles', -10.0, 80.0)}},
    ]
    return keys


def warrior_hit(P, carry):
    """hit reaction (sheet cell 6): IMPACT (key: trunk thrown back, sword arm flung back and down, blade pointing down
    and back clear of the trunk, shield up) -> RECOVER (key)"""
    k = leg_factor(P)
    feet = {'N': (-70.0 * k, -6.0), 'F': (92.0 * k, 8.0)}
    co = carry.get('chest_open', 30.0)
    base = {'chest_yaw': co, 'arm_abd_N': 16, 'arm_abd_F': 14}
    impact = dict(base, hip_h=160 * k, x=-26.0 * k, pelvis_pitch=-10, spine_pitch=-10, chest_pitch=-6, chest_yaw=co + 10,
                  head_pitch=-18)
    recover = dict(base, hip_h=162 * k, x=-12.0 * k, pelvis_pitch=0, spine_pitch=-2, chest_pitch=0, head_pitch=0)
    return [
        {'name': 'impact', 'pose': impact, 'feet': feet, 'props': _sword(-118.0, carry),
         'arms': {'N': ('hip', -58.0 * k, -6.0 * k), 'F': ('angles', 70.0, 104.0)}},
        {'name': 'recover', 'pose': recover, 'feet': feet, 'props': _sword(-104.0, carry),
         'arms': {'N': ('hip', -44.0 * k, 4.0 * k), 'F': ('angles', 46.0, 106.0)}},
    ]
