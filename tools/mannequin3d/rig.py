"""3D mannequin rig: skeleton, per-character proportions, forward kinematics and a 2-bone leg IK (numpy only).

Units are SOURCE (guide) pixels - the same pixels as the 1536x1024 request strips (scale 0.1654 to the game).
World axes: x = forward (the character faces +x, right on screen), y = up (floor at y = 0), z = toward the camera
(the NEAR side of the body is +z, the far side -z).

Pose angles are in degrees:
  root      hip_h (height of the hip JOINTS above the floor), x (forward offset of the pelvis, normally 0)
  pelvis    pelvis_pitch (forward tilt +), pelvis_yaw (turn toward the viewer +), pelvis_roll
  torso     spine_pitch, chest_pitch (forward bend +, added on top of the pelvis), chest_yaw (extra turn toward the viewer),
            neck_pitch, head_pitch (head_pitch is ABSOLUTE: 0 = looking straight ahead, + = chin down)
  legs      thigh_N / thigh_F   thigh angle from the vertical, forward + (absolute, like an animator's chart)
            knee_N / knee_F     knee bend (0 = straight, + = shin folds back)
            ankle_N / ankle_F   ankle relative to the shin (0 = foot at a right angle to the shin, + = toes up)
            abd_N / abd_F       leg out to the side (+ = away from the body)
  arms      shoulder_N/_F       upper arm angle from the TORSO's down axis, forward + (the arm follows the lean)
            elbow_N/_F          elbow bend (+ = forearm comes forward/up)
            wrist_N/_F          hand bend, arm_abd_N/_F arm out to the side
  prop      prop: {'hand': 'N'|'F', 'kind': 'sword'|'mace'|'staff'|'shield', 'angle': deg in the hand's plane,
            'roll': deg about the forearm} - optional held weapon bone

fk(prop_set, pose) -> Body: joint positions (3-vectors), the part frames (3x3) and the primitive list for render.py.
"""
import copy
import math

import numpy as np

DOWN = np.array([0.0, -1.0, 0.0])
UP = np.array([0.0, 1.0, 0.0])
FWD = np.array([1.0, 0.0, 0.0])

# Canonical proportions = the accepted 2D run mannequin (art/requests/guides/run_base/v2/pose.json bones_px, head_px 110,
# hip ~180, neck base ~285, head top ~417 above the floor). fit.py rescales these per character.
CANON = {
    'thigh': 89.65, 'shin': 89.65, 'ankle_h': 17.2, 'heel': 14.0, 'toe': 26.0,
    'hip_w': 21.0, 'hip_drop': 7.0,
    'spine': 48.0, 'chest': 64.0, 'neck': 16.0,
    'head_r': [50.0, 56.0, 46.0], 'head_c': 44.0,
    'shoulder_w': 40.0, 'shoulder_drop': 14.0,
    'upper_arm': 68.2, 'forearm': 56.0, 'hand': 15.5,
    'r_thigh': [21.0, 16.0], 'r_shin': [16.0, 12.0], 'r_foot': 10.0,
    'r_upper_arm': [14.0, 12.0], 'r_forearm': [12.0, 10.0], 'r_hand': 12.0,
    'pelvis_r': [30.0, 24.0, 32.0], 'chest_r': [34.0, 42.0, 44.0], 'r_spine': 26.0, 'r_neck': 11.0,
    'r_shoulder': 15.0,
}


def leg_len(P):
    return P['thigh'] + P['shin']


def rx(d):
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(d):
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(d):
    a = math.radians(d)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def turn(d):
    """turn the body toward the viewer (+z) by d degrees: forward (1,0,0) -> (cos, 0, sin)"""
    return ry(-d)


def lean(d):
    """bend forward by d degrees: up (0,1,0) -> (sin, cos, 0)"""
    return rz(-d)


SIDES = {'N': 1.0, 'F': -1.0}

DEFAULT_POSE = {
    'x': 0.0, 'hip_h': 180.0, 'pelvis_pitch': 0.0, 'pelvis_yaw': 0.0, 'pelvis_roll': 0.0,
    'spine_pitch': 0.0, 'chest_pitch': 0.0, 'chest_yaw': 0.0, 'neck_pitch': 0.0, 'head_pitch': 0.0,
    'thigh_N': 0.0, 'thigh_F': 0.0, 'knee_N': 0.0, 'knee_F': 0.0, 'ankle_N': 0.0, 'ankle_F': 0.0,
    'abd_N': 2.0, 'abd_F': 2.0,
    'shoulder_N': 0.0, 'shoulder_F': 0.0, 'elbow_N': 20.0, 'elbow_F': 20.0, 'wrist_N': 0.0, 'wrist_F': 0.0,
    'arm_abd_N': 6.0, 'arm_abd_F': 6.0,
}


def full_pose(pose):
    p = dict(DEFAULT_POSE)
    p.update({k: v for k, v in pose.items() if v is not None})
    return p


class Body:
    """FK result: joints (name -> 3-vector), frames (name -> 3x3), prims (render primitives), bones (pairs)."""

    def __init__(self):
        self.joints = {}
        self.frames = {}
        self.prims = []
        self.ghosts = []      # see-through extras (props, robe) drawn over the body as outlines + light fill

    def add_capsule(self, a, b, r0, r1, mat, part, ghost=False):
        (self.ghosts if ghost else self.prims).append(
            {'type': 'capsule', 'a': np.asarray(a, float), 'b': np.asarray(b, float), 'r0': float(r0), 'r1': float(r1),
             'mat': mat, 'part': part})

    def add_ellipsoid(self, c, R, radii, mat, part, ghost=False):
        (self.ghosts if ghost else self.prims).append(
            {'type': 'ellipsoid', 'c': np.asarray(c, float), 'R': np.asarray(R, float), 'radii': np.asarray(radii, float),
             'mat': mat, 'part': part})


def foot_points(ankle, pitch, P):
    """heel and toe-ball centres of the foot capsule for a foot at absolute pitch (0 = flat, + = toes up)."""
    R = rz(pitch)
    off = P['ankle_h'] - P['r_foot']
    heel = ankle + R @ np.array([-P['heel'], -off, 0.0])
    toe = ankle + R @ np.array([P['toe'], -off, 0.0])
    return heel, toe


def sole_y(ankle, pitch, P):
    """lowest point of the foot (the sole) for a foot at that pitch"""
    heel, toe = foot_points(ankle, pitch, P)
    return min(heel[1], toe[1]) - P['r_foot']


def fk(P, pose, props=None, robe=None):
    """forward kinematics. P = proportions, pose = angle dict (see module doc), props = list of prop dicts,
    robe = None or {'hem': height above floor, 'flare': extra radius, 'lag': [dxN, dxF]} (a see-through cloth proxy)."""
    q = full_pose(pose)
    B = Body()
    J, Fm = B.joints, B.frames
    # pelvis: centre above the hip joints
    R_pelvis = turn(q['pelvis_yaw']) @ lean(q['pelvis_pitch']) @ rx(q['pelvis_roll'])
    pelvis = np.array([q['x'], q['hip_h'], 0.0]) + R_pelvis @ np.array([0.0, P['hip_drop'], 0.0])
    J['pelvis'] = pelvis
    Fm['pelvis'] = R_pelvis
    R_spine = R_pelvis @ lean(q['spine_pitch']) @ turn(q['chest_yaw'] * 0.4)
    waist = pelvis + R_spine @ (UP * P['spine'])
    J['waist'] = waist
    Fm['spine'] = R_spine
    R_chest = R_spine @ lean(q['chest_pitch']) @ turn(q['chest_yaw'] * 0.6)
    neck0 = waist + R_chest @ (UP * P['chest'])
    J['neck0'] = neck0
    Fm['chest'] = R_chest
    R_neck = R_chest @ lean(q['neck_pitch'])
    neck1 = neck0 + R_neck @ (UP * P['neck'])
    J['neck1'] = neck1
    # head: pitch is absolute (keeps the head level while the trunk leans), yaw follows the chest
    yaw_total = q['pelvis_yaw'] + q['chest_yaw']
    R_head = turn(yaw_total) @ lean(q['head_pitch'])
    head = neck1 + R_head @ np.array([4.0, P['head_c'], 0.0])
    J['head'] = head
    J['headtop'] = head + R_head @ np.array([0.0, P['head_r'][1], 0.0])
    Fm['head'] = R_head

    # legs (absolute thigh angle in the world sagittal plane; hip joints ride on the pelvis)
    for s, sg in SIDES.items():
        hip = pelvis + R_pelvis @ np.array([0.0, -P['hip_drop'], sg * P['hip_w']])
        R_th = rz(q['thigh_' + s]) @ rx(-sg * q['abd_' + s])
        knee = hip + R_th @ (DOWN * P['thigh'])
        R_sh = R_th @ rz(-q['knee_' + s])
        ank = knee + R_sh @ (DOWN * P['shin'])
        shin_abs = q['thigh_' + s] - q['knee_' + s]
        pitch = shin_abs + q['ankle_' + s]
        heel, toe = foot_points(ank, pitch, P)
        J['H' + s], J['knee' + s], J['ank' + s], J['heel' + s], J['toe' + s] = hip, knee, ank, heel, toe
        J['toetip' + s] = toe + rz(pitch) @ np.array([P['r_foot'], 0.0, 0.0])
        J['sole' + s] = np.array([0.0, sole_y(ank, pitch, P), 0.0])
        Fm['foot' + s] = rz(pitch)
    J['hip'] = (J['HN'] + J['HF']) / 2

    # arms: shoulders on the (turned) chest, swing in the torso's lean plane
    lean_total = q['pelvis_pitch'] + q['spine_pitch'] + q['chest_pitch']
    R_armbase = turn(q['pelvis_yaw']) @ lean(lean_total)
    for s, sg in SIDES.items():
        sho = neck0 + R_chest @ np.array([-4.0, -P['shoulder_drop'], sg * P['shoulder_w']])
        R_ua = R_armbase @ rz(q['shoulder_' + s]) @ rx(-sg * q['arm_abd_' + s])
        elb = sho + R_ua @ (DOWN * P['upper_arm'])
        R_fa = R_ua @ rz(q['elbow_' + s])
        wri = elb + R_fa @ (DOWN * P['forearm'])
        R_hd = R_fa @ rz(q['wrist_' + s])
        hand = wri + R_hd @ (DOWN * (P['hand'] * 0.55))
        J['S' + s], J['elb' + s], J['wri' + s], J['hand' + s] = sho, elb, wri, hand
        Fm['upper_arm' + s], Fm['forearm' + s], Fm['hand' + s] = R_ua, R_fa, R_hd

    # ---- volumes ----
    M = {'N': 'near', 'F': 'far'}
    for s in 'FN':   # far first (order does not matter for the z-buffer; kept for readability)
        m = M[s]
        B.add_capsule(J['H' + s], J['knee' + s], *P['r_thigh'], m, 'thigh' + s)
        B.add_capsule(J['knee' + s], J['ank' + s], P['r_thigh'][1] * 0.95, P['r_shin'][1], m, 'shin' + s)
        B.add_capsule(J['heel' + s], J['toe' + s], P['r_foot'], P['r_foot'], m + '_foot', 'foot' + s)
        B.add_capsule(J['ank' + s], (J['heel' + s] + J['toe' + s]) / 2, P['r_shin'][1], P['r_foot'], m + '_foot', 'foot' + s)
        B.add_capsule(J['S' + s], J['elb' + s], *P['r_upper_arm'], m, 'upper_arm' + s)
        B.add_capsule(J['elb' + s], J['wri' + s], *P['r_forearm'], m, 'forearm' + s)
        B.add_ellipsoid(J['hand' + s], Fm['hand' + s], [P['r_hand'] * 0.8, P['r_hand'], P['r_hand'] * 0.7], m, 'hand' + s)
        B.add_ellipsoid(J['S' + s], R_chest, [P['r_shoulder']] * 3, m, 'shoulder' + s)
    B.add_ellipsoid(pelvis, R_pelvis, P['pelvis_r'], 'body', 'pelvis')
    B.add_capsule(pelvis, waist, P['r_spine'], P['r_spine'] * 0.95, 'body', 'spine')
    chest_c = waist + R_chest @ (UP * (P['chest'] * 0.5))
    J['chest'] = chest_c
    B.add_ellipsoid(chest_c, R_chest, P['chest_r'], 'body', 'chest')
    B.add_capsule(neck0, neck1, P['r_neck'], P['r_neck'], 'body', 'neck')
    B.add_ellipsoid(head, R_head, P['head_r'], 'head', 'head')
    # nose: shows which way the face points (it turns with the chest)
    nose = head + R_head @ np.array([P['head_r'][0] * 0.92, -P['head_r'][1] * 0.12, 0.0])
    J['nose'] = nose
    B.add_ellipsoid(nose, R_head, [7.0, 8.0, 6.0], 'head', 'nose')

    for pr in props or []:
        add_prop(B, P, pr)
    if robe:
        add_robe(B, P, robe)
    return B


PROP_LEN = {'sword': 150.0, 'mace': 120.0, 'staff': 330.0, 'shield': 0.0}


def add_prop(B, P, pr):
    """held weapon: a bone that leaves the fist perpendicular to the forearm (sword/mace) or runs through it (staff)."""
    J, Fm = B.joints, B.frames
    s = pr.get('hand', 'N')
    kind = pr.get('kind', 'sword')
    R_hd = Fm['hand' + s]
    grip = J['hand' + s]
    if kind == 'shield':
        # flat disc on the forearm, its face turned like the chest (toward the viewer-front)
        R = Fm['chest'] @ turn(pr.get('angle', 0.0))
        c = (J['wri' + s] * 0.6 + J['elb' + s] * 0.4) + R @ np.array([14.0, 0.0, 0.0])
        rad = pr.get('radius', 62.0)
        h = pr.get('height', rad)
        J['prop_base'], J['prop_tip'] = c, c + R @ np.array([0.0, h, 0.0])
        B.add_ellipsoid(c, R, [6.0, h, rad], 'prop', 'shield', ghost=True)
        return
    if pr.get('between'):
        a_, b_ = (J['wri' + h] for h in pr['between'])
        d = (b_ - a_) / max(np.linalg.norm(b_ - a_), 1e-9)
        grip = a_
        R = np.eye(3)
    elif pr.get('abs_angle') is not None:
        # direction fixed in the world sagittal plane (deg from forward-horizontal, + = up), turned like the pelvis
        a_ = math.radians(pr['abs_angle'])
        d = turn(pr.get('yaw', 0.0)) @ np.array([math.cos(a_), math.sin(a_), 0.0])
        R = np.eye(3)
    else:
        R = R_hd @ rx(pr.get('roll', 0.0)) @ rz(pr.get('angle', 0.0))
        d = R @ FWD
    L = pr.get('length', PROP_LEN[kind])
    back = pr.get('back', {'sword': 22.0, 'mace': 14.0, 'staff': 140.0}[kind])
    base, tip = grip - d * back, grip + d * L
    J['prop_base'], J['prop_tip'] = base, tip
    if kind == 'sword':
        B.add_capsule(base, grip + d * 12, 4.5, 4.5, 'prop', 'grip', ghost=True)
        B.add_capsule(grip + d * 12 + R @ np.array([0, 0, 18.0]), grip + d * 12 - R @ np.array([0, 0, 18.0]), 4, 4, 'prop', 'guard', ghost=True)
        B.add_capsule(grip + d * 14, tip, 7.0, 2.5, 'prop', 'blade', ghost=True)
    elif kind == 'mace':
        B.add_capsule(base, tip, 5.0, 5.0, 'prop', 'haft', ghost=True)
        B.add_ellipsoid(tip, R, [22.0, 22.0, 22.0], 'prop', 'mace_head', ghost=True)
    else:  # staff
        B.add_capsule(base, tip, 6.0, 5.0, 'prop', 'staff', ghost=True)
        B.add_ellipsoid(tip, R, [10.0, 10.0, 10.0], 'prop', 'staff_head', ghost=True)


def add_robe(B, P, robe):
    """see-through cloth proxy for long robes: a cone from the waist to the hem, the hem trailing the knees."""
    J = B.joints
    hem_h = robe.get('hem', 40.0)
    lag = robe.get('lag', 0.0)
    kx = [J['kneeN'][0], J['kneeF'][0], J['ankN'][0], J['ankF'][0]]
    front, back = max(kx) + 14.0, min(kx) - 14.0 - robe.get('trail', 10.0)
    mid = (front + back) / 2 - lag
    hem_r = max(28.0, (front - back) / 2 + robe.get('flare', 6.0))
    top = J['pelvis'] + np.array([0.0, P['pelvis_r'][1] * 0.6, 0.0])
    hem = np.array([mid, hem_h + 6.0, 0.0])
    B.add_capsule(top, hem + np.array([0.0, hem_r * 0.6, 0.0]), P['pelvis_r'][2] * 1.05, hem_r, 'robe', 'robe', ghost=True)
    B.ghosts[-1]['clip_below'] = hem_h


# ---------------------------------------------------------------- IK
def leg_ik(P, hip_xy, ank_xy):
    """2-bone IK in the sagittal plane with the knee in FRONT. -> (thigh_abs_deg, knee_deg, reached).
    If the target is out of reach the leg straightens toward it (reached = False)."""
    a, b = P['thigh'], P['shin']
    dx, dy = ank_xy[0] - hip_xy[0], ank_xy[1] - hip_xy[1]
    d = math.hypot(dx, dy)
    reached = d <= a + b - 1e-6
    d = min(max(d, abs(a - b) + 1e-3), a + b - 1e-6)
    ang_target = math.degrees(math.atan2(dx, -dy))       # angle from straight down, forward +
    cos_h = (a * a + d * d - b * b) / (2 * a * d)
    alpha = math.degrees(math.acos(max(-1.0, min(1.0, cos_h))))
    cos_k = (a * a + b * b - d * d) / (2 * a * b)
    knee = 180.0 - math.degrees(math.acos(max(-1.0, min(1.0, cos_k))))
    thigh = ang_target + alpha        # knee forward of the hip-ankle line
    return thigh, knee, reached


def arm_ik(P, pose, sho, target):
    """2-bone arm IK -> (shoulder, elbow) for the rig's arm convention (swing plane = the torso lean plane turned by the
    pelvis yaw; elbow bends with the forearm coming forward, so the elbow points back/down)."""
    q = full_pose(pose)
    lean_total = q['pelvis_pitch'] + q['spine_pitch'] + q['chest_pitch']
    R_armbase = turn(q['pelvis_yaw']) @ lean(lean_total)
    v = R_armbase.T @ (np.asarray(target, float) - sho)
    a, b = P['upper_arm'], P['forearm']
    d = math.hypot(v[0], v[1])
    d = min(max(d, abs(a - b) + 1e-3), a + b - 1e-6)
    ang = math.degrees(math.atan2(v[0], -v[1]))
    alpha = math.degrees(math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))))
    elbow = 180.0 - math.degrees(math.acos(max(-1.0, min(1.0, (a * a + b * b - d * d) / (2 * a * b)))))
    return ang - alpha, elbow


def scaled(P, k):
    Q = copy.deepcopy(P)
    for key, v in Q.items():
        if isinstance(v, list):
            Q[key] = [x * k for x in v]
        else:
            Q[key] = v * k
    return Q
