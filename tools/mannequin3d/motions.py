"""Keyframed motions for the 3D mannequin, authored as joint-angle tables (degrees, see rig.py for the conventions).

Gaits (8 frames a cycle, frame k at cycle phase k/8; the far leg / far arm run half a cycle behind the near ones):
  run_light  R1..R8  contact, down, push-off, FLIGHT        (art/requests/guides/run_base/v2: 80 ms, step 275 px)
  run_heavy  H1..H8  contact (both feet), down, passing, push (heavy_base/v1: 101 ms, step 142.5 px, no flight)
  run_robe   G1..G8  contact (both feet), down, passing, push (robe_base/v1: 96 ms, step 134.2 px, no flight)

How a gait frame is made:
  1. the SWING leg (off the floor) comes straight from the table SWING: thigh angle, knee bend, foot pitch;
  2. the STANCE leg is foot-locked: its toe ball sits on the floor at toe0 - 2*step*phase on SCREEN (relative to the hip
     column), i.e. exactly step/4 further back every cell - the rule the engine needs to keep feet planted
     (js/battle.js runCells moves the unit step/4 per stance cell). A 2-bone IK (rig.leg_ik) finds thigh + knee, the
     table's STANCE_PITCH gives the foot angle (heel rising at push-off);
  3. hip height, lean, arm swing, chest counter-turn come from the per-frame tables;
  4. the 8 key frames are joined by periodic Catmull-Rom splines, so any number of in-between frames can be sampled
     (stance legs are re-solved with IK at every sampled phase). With n = 8 the frames ARE the table rows.
The numbers were read off the accepted 2D mannequins (pose.json of the three base sets: hip heights, lean, toe x,
swing-leg thigh/knee angles) so the 3D motion keeps the same rhythm, stride and cadence; arms were re-authored in 3D.

Actions (attack_swing, hit): key poses with both feet locked to the floor; in-betweens by eased interpolation.
"""
import math

import numpy as np

from rig import leg_ik, fk, full_pose, foot_points, rz, leg_len, CANON

CANON_LEG = CANON['thigh'] + CANON['shin'] + CANON['ankle_h']

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
        'swing': {0.375: (-14.0, 72.0, -120.0), 0.5: (-6.0, 114.0, -145.0), 0.625: (10.0, 134.0, -130.0),
                  0.75: (60.0, 110.0, -45.0), 0.875: (55.0, 44.0, 15.0)},
        # near arm per frame (its far twin is half a cycle later): shoulder (from the torso axis), elbow
        'arm': [(-22.0, 80.0), (14.0, 92.0), (40.0, 104.0), (46.0, 108.0), (28.0, 100.0), (-18.0, 86.0),
                (-34.0, 80.0), (-36.0, 78.0)],
        'pelvis_twist': 7.0, 'chest_counter': 6.0, 'head_pitch': 4.0,
    },
    'run_heavy': {
        'set': 'run3d_heavy', 'gait': 'heavy', 'class': 'heavy', 'prefix': 'H', 'ms': 101, 'step_px': 142.5,
        'phases': ['contact', 'down', 'passing', 'push'],
        'stance': [0.0, 0.125, 0.25, 0.375, 0.5],
        'toe0': 83.0,
        'stance_pitch': [0.0, 0.0, 0.0, -8.0, -26.0],
        'hip_h': [180.0, 172.9, 177.8, 179.5],
        'lean': [5.0, 5.6, 5.0, 4.8],
        'swing': {0.625: (14.0, 72.0, -18.0), 0.75: (36.0, 72.0, -8.0), 0.875: (40.0, 48.0, 4.0)},
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
        'swing': {0.625: (8.0, 60.0, -15.0), 0.75: (29.0, 58.0, -6.0), 0.875: (34.0, 38.0, 4.0)},
        'arm': [(-10.0, 72.0), (-12.0, 76.0), (-4.0, 74.0), (6.0, 72.0), (10.0, 72.0), (12.0, 76.0), (4.0, 74.0), (-6.0, 72.0)],
        'pelvis_twist': 4.0, 'chest_counter': 3.0, 'head_pitch': 2.0,
        'robe': {'hem': 40.0, 'flare': 8.0, 'lag': 6.0, 'trail': 12.0},
    },
}


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


def _stance_target(spec, psi, cam, hip_w, P):
    """toe-ball (x on screen relative to the hip column) and foot pitch of a stance foot at leg phase psi"""
    toe_tip = spec['toe0'] - 2.0 * spec['step_px'] * psi
    st = spec['stance']
    pitch = interp_linear(st, spec['stance_pitch'], psi)
    return toe_tip, pitch


def _solve_stance(P, pose, side, toe_tip_screen, pitch, cam, char):
    """IK one stance leg so that its toe tip lands at toe_tip_screen (screen px rel. to the hip column) on the floor"""
    q = full_pose(pose)
    q['abd_' + side] = 0.0
    body = fk(P, q)
    hip = body.joints['H' + side]
    hip_mid = body.joints['hip']
    c, s = math.cos(math.radians(cam.yaw)), math.sin(math.radians(cam.yaw))
    z = hip[2]
    # screen_rel(p) = c*(x - hx) - s*(z - hz) for the view yaw (rig turn convention)
    tip_world_x = hip_mid[0] + (toe_tip_screen + s * (z - hip_mid[2])) / c
    R = rz(pitch)
    tip_off = R @ np.array([P['toe'] + P['r_foot'], -(P['ankle_h'] - P['r_foot']), 0.0])
    ank = np.array([tip_world_x, 0.0, z]) - tip_off
    # sit the lowest point of the foot on the floor
    heel, toe = foot_points(ank, pitch, P)
    ank[1] += P['r_foot'] - min(heel[1], toe[1])
    thigh, knee, ok = leg_ik(P, hip[:2], ank[:2])
    return thigh, knee, pitch - (thigh - knee), ok


def gait_keys(spec, P, cam, char):
    """the 8 key poses of a gait (dicts), with meta. Stance legs solved by IK."""
    k_leg = (P['thigh'] + P['shin'] + P['ankle_h']) / CANON_LEG
    rows = []
    for f in range(8):
        phi = f / 8.0
        half = f % 4
        L = spec['lean'][half]
        pose = {
            'hip_h': spec['hip_h'][half] * k_leg,
            # 1.2 x the table lean: the screen lean (hip -> neck base) of the turned, curved trunk comes out ~0.83 x
            'pelvis_pitch': L * 0.5, 'spine_pitch': L * 0.35, 'chest_pitch': L * 0.35,
            'pelvis_yaw': char.get('pelvis_yaw', 0.0) - spec['pelvis_twist'] * math.cos(2 * math.pi * phi),
            'chest_yaw': char.get('chest_open', 30.0) + spec['chest_counter'] * math.cos(2 * math.pi * phi) * 2,
            'head_pitch': spec['head_pitch'],
            'neck_pitch': -L * 0.5,
        }
        meta = {'stance': [], 'reached': True}
        for side, off in (('N', 0.0), ('F', 0.5)):
            psi = round((phi + off) % 1.0, 4)
            if psi in spec['swing']:
                th, kn, pitch = spec['swing'][psi]
                pose['thigh_' + side], pose['knee_' + side], pose['ankle_' + side] = th, kn, pitch - (th - kn)
            else:
                meta['stance'].append(side)
        for side, off in (('N', 0.0), ('F', 0.5)):
            arm_f = (f + (0 if side == 'N' else 4)) % 8
            sh, el = spec['arm'][arm_f]
            pose['shoulder_' + side], pose['elbow_' + side] = sh, el
        meta['hip_lowered'] = 0.0
        for _ in range(13):        # a stance foot out of reach: lower the hip by 0.5 px steps (at most 6 px), report it
            ok_all = True
            for side in meta['stance']:
                psi = round((phi + (0.0 if side == 'N' else 0.5)) % 1.0, 4)
                tip, pitch = _stance_target(spec, psi, cam, 0, P)
                th, kn, an, ok = _solve_stance(P, pose, side, tip, pitch, cam, char)
                pose['thigh_' + side], pose['knee_' + side], pose['ankle_' + side] = th, kn, an
                pose['abd_' + side] = 0.0
                ok_all &= ok
            if ok_all:
                break
            pose['hip_h'] -= 0.5
            meta['hip_lowered'] += 0.5
        meta['reached'] = ok_all
        char_pose(pose, char, f / 8.0, P)
        rows.append((pose, meta))
    return rows


def char_pose(pose, char, phi, P=None):
    """per-character carry: char['arm_N'] / ['arm_F'] = (shoulder, elbow) or a callable(shoulder, elbow) -> (shoulder, elbow)
    applied to the gait table's arm swing; char['wrist_N'/'_F'] = wrist bend; char['grip'] = two-hand grip solved by arm IK
    (see apply_grip)."""
    for side in 'NF':
        o = char.get('arm_' + side)
        if o is not None:
            sh, el = o(pose['shoulder_' + side], pose['elbow_' + side]) if callable(o) else o
            pose['shoulder_' + side], pose['elbow_' + side] = sh, el
        if char.get('wrist_' + side) is not None:
            pose['wrist_' + side] = char['wrist_' + side]
    if char.get('grip') and P is not None:
        apply_grip(P, pose, char['grip'], phi)


def apply_grip(P, pose, grip, phi=0.0):
    """two-hand grip: grip = {'N': (dx, dy, dz), 'F': (...)} wrist targets in the CHEST frame from the neck base
    (x forward, y up, z toward the near side), plus optional 'swing' px fore-aft (cos of the cycle).
    Solved with a 2-bone arm IK in each arm's swing plane (elbow pointing back/down)."""
    from rig import arm_ik
    body = fk(P, pose)
    J, Fm = body.joints, body.frames
    sw = grip.get('swing', 0.0) * math.cos(2 * math.pi * phi)
    for side in 'NF':
        if side not in grip:
            continue
        off = np.array(grip[side], float) + np.array([sw, 0.0, 0.0])
        target = J['neck0'] + Fm['chest'] @ off
        sh, el = arm_ik(P, pose, J['S' + side], target)
        pose['shoulder_' + side], pose['elbow_' + side] = sh, el
        pose['arm_abd_' + side] = 0.0


CHANNELS = ['hip_h', 'pelvis_pitch', 'spine_pitch', 'chest_pitch', 'pelvis_yaw', 'chest_yaw', 'head_pitch', 'neck_pitch',
            'thigh_N', 'knee_N', 'ankle_N', 'thigh_F', 'knee_F', 'ankle_F',
            'shoulder_N', 'elbow_N', 'shoulder_F', 'elbow_F', 'wrist_N', 'wrist_F']


def gait_frames(name, P, cam, char, n=8):
    """sample n frames of a gait cycle -> list of (pose, meta) where meta has phase, stance, frame name"""
    spec = GAITS[name]
    keys = gait_keys(spec, P, cam, char)
    out = []
    for i in range(n):
        phi = i / n
        pose = {}
        for ch in CHANNELS:
            vals = [full_pose(k[0])[ch] for k in keys]
            pose[ch] = float(catmull_periodic(vals, phi))
        stance = []
        reached = True
        for side, off in (('N', 0.0), ('F', 0.5)):
            psi = (phi + off) % 1.0
            st = spec['stance']
            if psi <= st[-1] + 1e-6:
                tip, pitch = _stance_target(spec, psi, cam, 0, P)
                th, kn, an, ok = _solve_stance(P, pose, side, tip, pitch, cam, char)
                pose['thigh_' + side], pose['knee_' + side], pose['ankle_' + side] = th, kn, an
                pose['abd_' + side] = 0.0
                stance.append(side)
                reached &= ok
        if char.get('grip'):
            apply_grip(P, pose, char['grip'], phi)
        k = i * 8 / n
        meta = {'phi': phi, 'stance': stance, 'reached': reached,
                'key': abs(k - round(k)) < 1e-9}
        if meta['key']:
            f = int(round(k)) % 8
            meta['frame'] = f'{spec["prefix"]}{f + 1}'
            meta['phase'] = spec['phases'][f % 4]
            meta['slot'] = f % 4 + 1
            meta['strip'] = 'a' if f < 4 else 'b'
        out.append((pose, meta))
    return out


# ------------------------------------------------------------------ actions
def ease(u):
    return u * u * (3 - 2 * u)


def lerp_pose(a, b, u):
    fa, fb = full_pose(a), full_pose(b)
    out = {k: fa[k] + (fb[k] - fa[k]) * u for k in fa}
    return out


def lerp_props(pa, pb, u):
    out = []
    for a, b in zip(pa, pb):
        c = dict(a)
        for k in ('angle', 'roll'):
            if k in a or k in b:
                c[k] = a.get(k, 0.0) + (b.get(k, 0.0) - a.get(k, 0.0)) * u
        out.append(c)
    return out


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
            R = rz(pitch)
            tip_off = R @ np.array([P['toe'] + P['r_foot'], -(P['ankle_h'] - P['r_foot']), 0.0])
            ank = np.array([tip_x, 0.0, hip[2]]) - tip_off
            heel, toe = foot_points(ank, pitch, P)
            ank[1] += P['r_foot'] - min(heel[1], toe[1])
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


def action_frames(keys, P, cam, inbetweens):
    """keys = list of (name, pose, props, feet); inbetweens = {index of key: count before the next key}.
    -> list of (name, pose, props, key?, reached)"""
    out = []
    for i, (name, pose, props, feet) in enumerate(keys):
        p, ok = lock_feet(P, pose, cam, feet)
        out.append((name, p, props, True, ok))
        if i + 1 < len(keys) and inbetweens.get(i):
            n2, pose2, props2, feet2 = keys[i + 1]
            m = inbetweens[i]
            for j in range(1, m + 1):
                u = ease(j / (m + 1))
                pp = lerp_pose(pose, pose2, u)
                ff = {s: (feet[s][0] + (feet2[s][0] - feet[s][0]) * u, feet[s][1] + (feet2[s][1] - feet[s][1]) * u) for s in feet}
                pp, ok = lock_feet(P, pp, cam, ff)
                out.append((f'{name}>{n2} {j}/{m + 1}', pp, lerp_props(props, props2, u), False, ok))
    return out


def warrior_attack(P, char):
    """sword swing (sheet/class/warrior cells 4-5): READY -> WINDUP (key) -> 2 in-betweens -> STRIKE (key)"""
    k = (P['thigh'] + P['shin'] + P['ankle_h']) / CANON_LEG
    feet = {'N': (-62.0, -8.0), 'F': (112.0, 0.0)}
    feet_lunge = {'N': (-62.0, -26.0), 'F': (112.0, 0.0)}
    base = {'chest_yaw': char.get('chest_open', 30.0), 'head_pitch': 6.0, 'arm_abd_N': 8, 'arm_abd_F': 10}
    ready = dict(base, hip_h=166 * k, x=0.0, pelvis_pitch=6, spine_pitch=4, chest_pitch=4,
                 shoulder_N=10, elbow_N=95, shoulder_F=30, elbow_F=100, wrist_N=-10)
    windup = dict(base, hip_h=170 * k, x=-12.0, pelvis_pitch=-2, spine_pitch=-4, chest_pitch=-4, chest_yaw=base['chest_yaw'] + 14,
                  shoulder_N=165, elbow_N=105, shoulder_F=40, elbow_F=95, wrist_N=-20, head_pitch=2)
    strike = dict(base, hip_h=152 * k, x=12.0, pelvis_pitch=14, spine_pitch=8, chest_pitch=6, chest_yaw=base['chest_yaw'] - 12,
                  shoulder_N=78, elbow_N=8, shoulder_F=-10, elbow_F=80, wrist_N=-8, head_pitch=4)
    sword = lambda a: [{'hand': 'N', 'kind': 'sword', 'angle': a}, {'hand': 'F', 'kind': 'shield', 'radius': 58.0}]
    keys = [('ready', ready, sword(60.0), feet), ('windup', windup, sword(125.0), feet),
            ('strike', strike, sword(285.0), feet_lunge)]
    return keys, {1: 2}


def warrior_hit(P, char):
    """hit reaction: IMPACT (key) -> RECOVER (key) with feet planted"""
    k = (P['thigh'] + P['shin'] + P['ankle_h']) / CANON_LEG
    feet = {'N': (-70.0, -6.0), 'F': (92.0, 8.0)}
    base = {'chest_yaw': char.get('chest_open', 30.0), 'arm_abd_N': 12, 'arm_abd_F': 14}
    impact = dict(base, hip_h=160 * k, x=-26.0, pelvis_pitch=-10, spine_pitch=-10, chest_pitch=-6, chest_yaw=base['chest_yaw'] + 10,
                  head_pitch=-18, shoulder_N=-30, elbow_N=50, shoulder_F=46, elbow_F=70)
    recover = dict(base, hip_h=162 * k, x=-12.0, pelvis_pitch=0, spine_pitch=-2, chest_pitch=0,
                   head_pitch=0, shoulder_N=-8, elbow_N=80, shoulder_F=30, elbow_F=95)
    props_i = [{'hand': 'N', 'kind': 'sword', 'angle': 30.0}, {'hand': 'F', 'kind': 'shield', 'radius': 58.0}]
    props_r = [{'hand': 'N', 'kind': 'sword', 'angle': 50.0}, {'hand': 'F', 'kind': 'shield', 'radius': 58.0}]
    return [('impact', impact, props_i, feet), ('recover', recover, props_r, feet)], {}
