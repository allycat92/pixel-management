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
        self.grips = set()    # hands ('N' / 'F') that hold a prop (render marks them)

    def add_capsule(self, a, b, r0, r1, mat, part, ghost=False):
        (self.ghosts if ghost else self.prims).append(
            {'type': 'capsule', 'a': np.asarray(a, float), 'b': np.asarray(b, float), 'r0': float(r0), 'r1': float(r1),
             'mat': mat, 'part': part})

    def add_ellipsoid(self, c, R, radii, mat, part, ghost=False):
        (self.ghosts if ghost else self.prims).append(
            {'type': 'ellipsoid', 'c': np.asarray(c, float), 'R': np.asarray(R, float), 'radii': np.asarray(radii, float),
             'mat': mat, 'part': part})


TOE_TAPER = 0.62     # toe-ball radius / heel radius: a wedge foot (heel block, tapered toe) with a flat sole


def foot_points(ankle, pitch, P):
    """heel and toe-ball centres of the foot capsule for a foot at absolute pitch (0 = flat, + = toes up).
    The heel sphere has radius r_foot, the toe ball TOE_TAPER x r_foot, set lower so the sole stays a straight line."""
    R = rz(pitch)
    rh = P['r_foot']
    rt = rh * TOE_TAPER
    off = P['ankle_h'] - rh
    heel = ankle + R @ np.array([-P['heel'], -off, 0.0])
    toe = ankle + R @ np.array([P['toe'] + (rh - rt), -off - (rh - rt), 0.0])
    return heel, toe


def toe_tip_offset(P, pitch):
    """toe tip (front of the toe ball) relative to the ankle for a foot at that pitch"""
    rh = P['r_foot']
    rt = rh * TOE_TAPER
    return rz(pitch) @ np.array([P['toe'] + rh, -(P['ankle_h'] - rh) - (rh - rt), 0.0])


def sole_y(ankle, pitch, P):
    """lowest point of the foot (the sole) for a foot at that pitch"""
    heel, toe = foot_points(ankle, pitch, P)
    return min(heel[1] - P['r_foot'], toe[1] - P['r_foot'] * TOE_TAPER)


def ankle_on_floor(P, tip, pitch):
    """ankle position for a toe tip at world point `tip` (its y ignored) with the sole's lowest point on y = 0"""
    ank = np.array([tip[0], 0.0, tip[2]], float) - toe_tip_offset(P, pitch)
    ank[1] -= sole_y(ank, pitch, P)
    return ank


def fk(P, pose, props=None, robe=None):
    """forward kinematics. P = proportions, pose = angle dict (see module doc), props = list of prop dicts,
    robe = None or {'hem_h', 'front', 'back', 'depth'} (see robe_rings; a see-through cloth proxy)."""
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
        J['toetip' + s] = ank + toe_tip_offset(P, pitch)
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
        sg = SIDES[s]
        # thigh starts a little down the bone with a smaller cap, so its top stays inside the pelvis (no knob in front
        # of the belt when the thigh swings forward)
        tdir = (J['knee' + s] - J['H' + s]) / max(np.linalg.norm(J['knee' + s] - J['H' + s]), 1e-9)
        B.add_capsule(J['H' + s] + tdir * P['r_thigh'][0] * 0.8, J['knee' + s], P['r_thigh'][0] * 0.78, P['r_thigh'][1],
                      m, 'thigh' + s)
        B.add_capsule(J['knee' + s], J['ank' + s], P['r_thigh'][1] * 0.95, P['r_shin'][1], m, 'shin' + s)
        # wedge foot: heel block (r_foot) tapering to the toe ball; instep from the ankle; an ankle knob that reads as the joint
        B.add_capsule(J['heel' + s], J['toe' + s], P['r_foot'], P['r_foot'] * TOE_TAPER, m + '_foot', 'foot' + s)
        B.add_capsule(J['ank' + s], J['heel' + s] * 0.55 + J['toe' + s] * 0.45 + Fm['foot' + s] @ np.array([0.0, 2.0, 0.0]),
                      P['r_shin'][1] * 0.92, P['r_foot'] * 0.85, m + '_foot', 'instep' + s)
        # ankle bone (malleolus): a knob on the outer side, so it shows even on thick (fitted) shins; never below the sole
        rk = min(P['r_shin'][1] * 1.12, P['ankle_h'] - 3.0)
        B.add_ellipsoid(J['ank' + s] + np.array([0.0, 2.0, sg * P['r_shin'][1] * 0.45]), Fm['foot' + s], [rk] * 3, m,
                        'ankle' + s)
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
PROP_BACK = {'sword': 22.0, 'mace': 14.0, 'staff': 140.0}


def add_slab(B, c, u, v, half, corner, mat, part, ghost=True):
    """flat rounded rectangle (a disc when corner = both halves): centre c, width axis u, height axis v (unit vectors)"""
    u = np.asarray(u, float) / np.linalg.norm(u)
    v = np.asarray(v, float) / np.linalg.norm(v)
    n = np.cross(u, v)
    (B.ghosts if ghost else B.prims).append(
        {'type': 'slab', 'c': np.asarray(c, float), 'R': np.stack([u, v, n], 1), 'half': [float(half[0]), float(half[1])],
         'corner': float(corner), 'mat': mat, 'part': part})


def add_prop(B, P, pr):
    """held prop. kind:
      shield  strapped on the forearm of pr['hand']: shape 'round' (a disc of `radius`) or 'tower' (rounded rectangle
              `half` = [half width, half height], `corner`); its face turned `face` deg from forward toward the viewer
              (world, about the vertical), centre at the forearm middle + `lift` px up, `offset` px out along its normal.
      sword / mace / staff  a bone from the fist: direction from `abs_angle` (deg from forward-horizontal, + = up, in the
              world sagittal plane), or `angle`/`roll` in the hand frame, or `between` two wrists; `length` beyond the
              fist, `back` px behind it (pommel / staff butt below the hand)."""
    J, Fm = B.joints, B.frames
    s = pr.get('hand', 'N')
    kind = pr.get('kind', 'sword')
    B.grips.add(s if not pr.get('between') else pr['between'][0])
    if kind == 'shield':
        n = turn(pr.get('face', 30.0)) @ FWD
        up = UP
        u = np.cross(up, n)
        # strapped on the OUTSIDE of the forearm: out along its face normal, `toward` px toward the viewer (+z) so the
        # forearm and the shield hand sit behind it as in the drawings, `lift` px up
        c = ((J['elb' + s] * 0.45 + J['wri' + s] * 0.55) + n * (P['r_forearm'][1] + pr.get('offset', 4.0))
             + UP * pr.get('lift', 0.0) + np.array([0.0, 0.0, pr.get('toward', 0.0)]))
        if pr.get('shape', 'round') == 'tower':
            hw, hh = pr.get('half', [48.0, 120.0])
            add_slab(B, c, u, up, (hw, hh), pr.get('corner', 14.0), 'prop', 'shield')
        else:
            r = pr.get('radius', 62.0)
            add_slab(B, c, u, up, (r, r), r, 'prop', 'shield')
        J['shield_c'] = c
        return
    R_hd = Fm['hand' + s]
    grip = J['hand' + s]
    if pr.get('between'):
        a_, b_ = (J['wri' + h] for h in pr['between'])
        d = (b_ - a_) / max(np.linalg.norm(b_ - a_), 1e-9)
        grip = a_
        R = np.eye(3)
    elif pr.get('abs_angle') is not None:
        # direction fixed in the world sagittal plane (deg from forward-horizontal, + = up), optionally turned by `yaw`
        a_ = math.radians(pr['abs_angle'])
        d = turn(pr.get('yaw', 0.0)) @ np.array([math.cos(a_), math.sin(a_), 0.0])
        R = np.eye(3)
    else:
        R = R_hd @ rx(pr.get('roll', 0.0)) @ rz(pr.get('angle', 0.0))
        d = R @ FWD
    L = pr.get('length', PROP_LEN[kind])
    back = pr.get('back', PROP_BACK[kind])
    base, tip = grip - d * back, grip + d * L
    J['prop_base'], J['prop_tip'], J['prop_grip'] = base, tip, grip
    J['prop_dir_' + kind] = d
    if kind == 'sword':
        J['blade_a'], J['blade_b'] = grip + d * 14, tip
        J['sword_grip'], J['sword_tip'] = grip, tip
        side = np.cross(d, UP if abs(d[1]) < 0.9 else FWD)
        side = side / max(np.linalg.norm(side), 1e-9)
        B.add_capsule(base, grip + d * 12, 4.5, 4.5, 'prop', 'grip', ghost=True)
        B.add_capsule(grip + d * 12 + side * 18.0, grip + d * 12 - side * 18.0, 4, 4, 'prop', 'guard', ghost=True)
        B.add_capsule(grip + d * 14, tip, 7.0, 2.5, 'prop', 'blade', ghost=True)
    elif kind == 'mace':
        hr = pr.get('head_r', 22.0)
        B.add_capsule(base, tip - d * hr * 0.6, 5.0, 5.0, 'prop', 'haft', ghost=True)
        B.add_ellipsoid(tip, np.eye(3), [hr, hr, hr], 'prop', 'mace_head', ghost=True)
    else:  # staff
        B.add_capsule(base, tip, 6.0, 5.0, 'prop', 'staff', ghost=True)
        B.add_ellipsoid(tip, np.eye(3), [10.0, 12.0, 10.0], 'prop', 'staff_head', ghost=True)


def add_skirt(B, rings, mat, part):
    """cloth surface of revolution-ish: rings = [(y, cx, cz, a, c), ...] from the top down; between rings the centre and
    the half widths (a along x, c along z) change linearly. Rendered as a see-through ghost."""
    B.ghosts.append({'type': 'skirt', 'rings': np.asarray(rings, float), 'mat': mat, 'part': part})


def robe_rings(B, P, robe):
    """the robe proxy for one frame: (capelet rings, robe rings).
    robe = {'hem_h': hem height above the floor, 'front': hem front x (world), 'back': hem back x, 'depth': hem half depth}.
    The capelet hangs from the neck over the shoulders to the upper chest (flaring); the robe hangs from the chest and
    widens in a straight line (A-line) to the hem - widest at the hem, no bulge."""
    J, Fm = B.joints, B.frames
    up = Fm['chest'] @ UP
    nk = J['neck0']
    chest = J['chest']
    sh_w = P['shoulder_w'] + P['r_shoulder']
    cap_top = nk + up * 4.0
    cap_bot = nk - up * (P['shoulder_drop'] + P['chest'] * 0.42)
    capelet = [(cap_top[1], cap_top[0], 0.0, P['r_neck'] * 1.7, P['r_neck'] * 1.7),
               (nk[1] - P['shoulder_drop'] * 0.6, nk[0] - 2.0, 0.0, P['chest_r'][0] * 1.08, sh_w * 1.05),
               (cap_bot[1], cap_bot[0] - 2.0, 0.0, P['chest_r'][0] * 1.32, sh_w * 1.22)]
    top = chest + up * (P['chest'] * 0.12)
    a_top, c_top = P['chest_r'][0] * 1.06, P['chest_r'][2] * 1.02
    hem_mid = (robe['front'] + robe['back']) / 2.0
    a_hem = max((robe['front'] - robe['back']) / 2.0, a_top * 1.3)
    c_hem = max(robe.get('depth', 0.0), c_top * 1.25)
    robe_r = [(top[1], top[0], 0.0, a_top, c_top), (robe['hem_h'], hem_mid, 0.0, a_hem, c_hem)]
    return capelet, robe_r


def add_robe(B, P, robe):
    capelet, robe_r = robe_rings(B, P, robe)
    add_skirt(B, robe_r, 'robe', 'robe')
    B.ghosts[-1]['hem_lift'] = (robe.get('lift_front', 0.0), robe.get('lift_back', 0.0))
    add_skirt(B, capelet, 'robe', 'capelet')
    B.joints['hem_front'] = np.array([robe['front'], robe['hem_h'], 0.0])
    B.joints['hem_back'] = np.array([robe['back'], robe['hem_h'], 0.0])


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
