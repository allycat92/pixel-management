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
            arm_twist_N/_F      upper-arm (humeral) rotation, + = inward (a bent forearm turns across the body); 0 for every
                                carry so far except the second hand of a two-handed grip (motions.two_hand, arm_ik3d)
  prop      prop: {'hand': 'N'|'F', 'kind': 'sword'|'mace'|'staff'|'bow'|'spear'|'dagger'|'shield', 'angle': deg in
            the hand's plane, 'roll': deg about the forearm, 'grip': 'normal'|'reverse'} - optional held weapon bone
            (add_prop: a bow is held at its grip in one hand, a spear may take two hands, a reverse grip flips the blade)

Weapon joint limit (owner 2026-11-28: no weapon that bends down past the arm line and dangles): every held WEAPON
(sword, mace, staff, bow, spear, dagger - not a shield) has a hard range of motion at the hand, measured in the arm's swing
plane as the angle from the FOREARM direction (elbow -> wrist) to the GRIP AXIS (fist -> tip; staff / spear: the head end;
bow: the stave at the grip toward the upper tip; a REVERSE grip: the thumb side of the fist, the blade the other way):
  0 deg = the weapon straight along the forearm (fully extended), + = rotated UPWARD = toward the thumb side, i.e. the
  head side when the forearm points forward, back over the shoulder when it points up (the elbow's flex sense);
  allowed [limit_min, limit_max] = [0, 120] by default (specs/carry3d.json `weapon_limit` per character).
A requested direction outside the range is CLAMPED to the nearest bound (safety net) and recorded in Body.weapons
(raw and final angle, clamped flag); checks.py FAILs any frame that needed the clamp - motions must be authored inside.

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
    'arm_abd_N': 6.0, 'arm_abd_F': 6.0, 'arm_twist_N': 0.0, 'arm_twist_F': 0.0,
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
        self.weapons = []     # per held weapon: kind, hand, raw / final angle to the forearm (deg), limit, clamped

    @property
    def weapon_clamps(self):
        return sum(1 for w in self.weapons if w['clamped'])

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


def arm_chain(P, q, s, sho, R_armbase):
    """one arm from its shoulder point: -> (elbow, wrist, hand centre, R_upper_arm, R_forearm, R_hand)"""
    sg = SIDES[s]
    R_ua = R_armbase @ rz(q['shoulder_' + s]) @ rx(-sg * q['arm_abd_' + s]) @ ry(sg * q.get('arm_twist_' + s, 0.0))
    elb = sho + R_ua @ (DOWN * P['upper_arm'])
    R_fa = R_ua @ rz(q['elbow_' + s])
    wri = elb + R_fa @ (DOWN * P['forearm'])
    R_hd = R_fa @ rz(q['wrist_' + s])
    hand = wri + R_hd @ (DOWN * (P['hand'] * 0.55))
    return elb, wri, hand, R_ua, R_fa, R_hd


def arm_base(q):
    """the arms' swing frame: the torso lean plane turned by the pelvis yaw"""
    return turn(q['pelvis_yaw']) @ lean(q['pelvis_pitch'] + q['spine_pitch'] + q['chest_pitch'])


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
    R_armbase = arm_base(q)
    Fm['armbase'] = turn(q['pelvis_yaw'])      # the arms' swing plane = its xy plane (weapon limit is measured in it)
    for s, sg in SIDES.items():
        sho = neck0 + R_chest @ np.array([-4.0, -P['shoulder_drop'], sg * P['shoulder_w']])
        elb, wri, hand, R_ua, R_fa, R_hd = arm_chain(P, q, s, sho, R_armbase)
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


PROP_LEN = {'sword': 150.0, 'mace': 120.0, 'staff': 330.0, 'shield': 0.0, 'bow': 125.0, 'spear': 300.0, 'dagger': 80.0}
PROP_BACK = {'sword': 22.0, 'mace': 14.0, 'staff': 140.0, 'bow': 110.0, 'spear': 80.0, 'dagger': 12.0}
WEAPONS = ('sword', 'mace', 'staff', 'bow', 'spear', 'dagger')
WEAPON_LIMIT = (0.0, 120.0)     # default hand range of motion: weapon vs forearm, deg (0 = straight, + = upward)
GRIPS = ('normal', 'reverse')


def _wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def weapon_angle(B, side, d):
    """signed angle (deg) from the forearm of `side` to direction d in the arm swing plane: 0 = straight along the
    forearm, + = upward (thumb side, the elbow's flex sense), - = bent down past the arm line"""
    Rb = B.frames.get('armbase', np.eye(3))
    f = Rb.T @ (B.joints['wri' + side] - B.joints['elb' + side])
    v = Rb.T @ np.asarray(d, float)
    return _wrap(math.degrees(math.atan2(v[1], v[0]) - math.atan2(f[1], f[0])))


def weapon_angle_hand(B, side, d):
    """signed angle (deg) from the forearm of `side` to direction d in that forearm's OWN bending plane (perpendicular to
    its elbow hinge): the wrist rule for an arm that reaches across the body (the second hand of a two-handed grip, a
    twisted upper arm). Same sense as weapon_angle (+ = the elbow's flex sense = upward for a forward forearm); for an
    untwisted, unabducted arm the two are equal."""
    Rf = B.frames['forearm' + side]
    f = Rf.T @ (B.joints['wri' + side] - B.joints['elb' + side])
    v = Rf.T @ np.asarray(d, float)
    # forearm local frame: the forearm runs along -y, the hinge is z; measured like weapon_angle (from the forearm, + = z)
    return _wrap(math.degrees(math.atan2(v[1], v[0]) - math.atan2(f[1], f[0])))


def limit_weapon(B, side, d, limit=None):
    """hard joint limit: -> (direction inside [min, max] of the forearm, raw angle, final angle, clamped). Out of range
    = rotated in the swing plane to the nearest bound (out-of-plane part kept)."""
    lo, hi = limit if limit is not None else WEAPON_LIMIT
    raw = weapon_angle(B, side, d)
    if lo - 1e-6 <= raw <= hi + 1e-6:
        return np.asarray(d, float), raw, raw, False
    # nearest bound on the circle
    to_lo = (lo - raw) % 360.0
    to_hi = (raw - hi) % 360.0
    new = lo if to_lo <= to_hi else hi
    Rb = B.frames.get('armbase', np.eye(3))
    v = Rb.T @ np.asarray(d, float)
    m = math.hypot(v[0], v[1])
    rot = math.radians(new - raw)
    c, s_ = math.cos(rot), math.sin(rot)
    v2 = np.array([c * v[0] - s_ * v[1], s_ * v[0] + c * v[1], v[2]])
    if m < 1e-9:
        v2 = v
    d2 = Rb @ v2
    d2 = d2 / max(np.linalg.norm(d2), 1e-9)
    return d2, raw, weapon_angle(B, side, d2), True


def add_slab(B, c, u, v, half, corner, mat, part, ghost=True):
    """flat rounded rectangle (a disc when corner = both halves): centre c, width axis u, height axis v (unit vectors)"""
    u = np.asarray(u, float) / np.linalg.norm(u)
    v = np.asarray(v, float) / np.linalg.norm(v)
    n = np.cross(u, v)
    (B.ghosts if ghost else B.prims).append(
        {'type': 'slab', 'c': np.asarray(c, float), 'R': np.stack([u, v, n], 1), 'half': [float(half[0]), float(half[1])],
         'corner': float(corner), 'mat': mat, 'part': part})


def _perp(d, pref):
    """unit vector perpendicular to d, as close as possible to `pref` (fallback: up, then forward)"""
    for p in (pref, UP, FWD):
        v = np.asarray(p, float) - (np.asarray(p, float) @ d) * d
        if np.linalg.norm(v) > 0.3:
            return v / np.linalg.norm(v)
    return np.array([0.0, 0.0, 1.0])


def _frame_along(d):
    """3x3 with columns (d, w, n): d the long axis, w in the picture plane across it, n toward the camera-ish"""
    w = np.cross(np.array([0.0, 0.0, 1.0]), d)
    if np.linalg.norm(w) < 1e-6:
        w = np.cross(UP, d)
    w = w / np.linalg.norm(w)
    n = np.cross(d, w)
    return np.stack([d, w, n], 1)


def bow_points(grip, d, belly, L, back, brace, recurve, n=6):
    """the two limbs of a braced recurve bow as polylines from the grip to each tip. d = the stave direction at the grip
    (toward the upper tip), belly = unit vector the limbs bulge toward (away from the string). Each limb runs along d and
    curls back toward the string by `brace` px at the tip (brace height), with the last fifth flicking forward by
    `recurve` px (the recurve)."""
    out = []
    for sgn, ln in ((1.0, L), (-1.0, back)):
        pts = []
        for i in range(n + 1):
            t = i / n
            off = -brace * t ** 1.6 + recurve * max(0.0, (t - 0.78) / 0.22) ** 2
            pts.append(grip + d * (sgn * ln * t) + belly * off)
        out.append(pts)
    return out


def add_prop(B, P, pr):
    """held prop. kind:
      shield  strapped on the forearm of pr['hand']: shape 'round' (a disc of `radius`) or 'tower' (rounded rectangle
              `half` = [half width, half height], `corner`); its face turned `face` deg from forward toward the viewer
              (world, about the vertical), centre at the forearm middle + `lift` px up, `offset` px out along its normal.
      weapons (sword, mace, staff, bow, spear, dagger)  a bone from the fist: the GRIP AXIS direction from `abs_angle`
              (deg from forward-horizontal, + = up, in the world sagittal plane), or `angle`/`roll` in the hand frame, or
              `between` two wrists; `length` beyond the fist, `back` px behind it (pommel / staff butt / lower bow limb).
              The grip axis is what the hand range (WEAPON_LIMIT / `limit`) is measured on - the thumb side of the fist.
        sword   grip, cross guard, blade                      mace   haft + round head (`head_r`)
        staff   pole + knob at the tip                        spear  long shaft + leaf-shaped steel head (`head_len`,
                                                                     `head_w`); two-hand grips via carry `two_hand`
        bow     held at the grip in ONE hand: `length` = grip -> upper tip, `back` = grip -> lower tip along the stave;
                the limbs curve back toward the string (`brace` px, default 13% of the bow) with recurved tips
                (`recurve`), bulging toward `belly` (default: forward, away from the body) - the string a thin line
                tip to tip on the body side. The grip axis (wrist rule) = the stave direction at the grip.
        dagger  short blade, small guard (`guard` half width, default 9)
      grip: 'reverse' (sword / dagger)  REVERSE grip: the blade leaves the little-finger side of the fist - it is drawn
              flipped 180 deg from the grip axis (pommel on the thumb side). The wrist rule still applies to the grip axis,
              so a reverse-gripped blade lies at -180..-60 deg from the forearm when the axis is inside 0..120."""
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
    if kind not in WEAPONS:
        raise ValueError(f'prop kind {kind!r} unknown (weapons {WEAPONS}, or shield)')
    grip_mode = pr.get('grip', 'normal')
    if grip_mode not in GRIPS:
        raise ValueError(f'prop grip {grip_mode!r} unknown ({GRIPS})')
    if grip_mode == 'reverse' and kind not in ('sword', 'dagger'):
        raise ValueError(f'grip reverse is for a sword or a dagger, not a {kind}')
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
    hold = pr['between'][0] if pr.get('between') else s
    if pr.get('limit', True) is not False:
        lim = pr.get('limit')
        lim = tuple(lim) if isinstance(lim, (list, tuple)) else WEAPON_LIMIT
        d, raw, fin, clamped = limit_weapon(B, hold, d, lim)
        rec = {'kind': kind, 'hand': hold, 'grip': grip_mode, 'raw_deg': round(raw, 2), 'deg': round(fin, 2),
               'limit': [lim[0], lim[1]], 'clamped': clamped}
        if grip_mode == 'reverse':
            rec['blade_deg'] = round(_wrap(fin + 180.0), 2)
        B.weapons.append(rec)
    h2 = pr.get('hand2')
    if h2 and h2 != hold and pr.get('limit', True) is not False:
        # the SECOND hand on a two-handed weapon (owner 2026-11-28: the wrist rule holds for EVERY hand on the weapon): its
        # grip axis is the same weapon direction; it is not clamped (the first hand sets the weapon) - checks.py FAILs it
        a2 = weapon_angle_hand(B, h2, d)
        lim = tuple(pr['limit']) if isinstance(pr.get('limit'), (list, tuple)) else WEAPON_LIMIT
        B.weapons.append({'kind': kind, 'hand': h2, 'role': 'second', 'grip': grip_mode, 'raw_deg': round(a2, 2),
                          'deg': round(a2, 2), 'limit': [lim[0], lim[1]], 'clamped': False,
                          'outside': not (lim[0] - 1e-6 <= a2 <= lim[1] + 1e-6)})
    J['prop_axis_' + kind] = d                   # the grip axis (thumb side of the fist; the wrist rule)
    if grip_mode == 'reverse':
        d = -d                                   # the blade leaves the little-finger side
    L = pr.get('length', PROP_LEN[kind])
    back = pr.get('back', PROP_BACK[kind])
    base, tip = grip - d * back, grip + d * L
    J['prop_base'], J['prop_tip'], J['prop_grip'] = base, tip, grip
    J['prop_dir_' + kind] = d                    # along the drawn weapon, toward its tip / head / upper limb
    if kind in ('sword', 'dagger'):
        J['blade_a'], J['blade_b'] = grip + d * 14, tip
        J['sword_grip'], J['sword_tip'] = grip, tip
        side = np.cross(d, UP if abs(d[1]) < 0.9 else FWD)
        side = side / max(np.linalg.norm(side), 1e-9)
        if kind == 'sword':
            gw, gr, br = 18.0, 4.0, (7.0, 2.5)
        else:
            gw, gr, br = pr.get('guard', 9.0), 3.0, (5.5, 1.8)
        B.add_capsule(base, grip + d * 12, 4.5, 4.5, 'prop', 'grip', ghost=True)
        B.add_capsule(grip + d * 12 + side * gw, grip + d * 12 - side * gw, gr, gr, 'prop', 'guard', ghost=True)
        B.add_capsule(grip + d * 14, tip, *br, 'prop', 'blade', ghost=True)
    elif kind == 'mace':
        hr = pr.get('head_r', 22.0)
        B.add_capsule(base, tip - d * hr * 0.6, 5.0, 5.0, 'prop', 'haft', ghost=True)
        B.add_ellipsoid(tip, np.eye(3), [hr, hr, hr], 'prop', 'mace_head', ghost=True)
    elif kind == 'spear':
        hl, hw = pr.get('head_len', 44.0), pr.get('head_w', 18.0)
        B.add_capsule(base, tip - d * hl * 0.8, 5.0, 4.5, 'prop', 'shaft', ghost=True)
        # leaf blade: a flat oval widest a little below its middle, drawn out to a point at the tip
        B.add_ellipsoid(tip - d * hl * 0.58, _frame_along(d), [hl * 0.42, hw * 0.5, 3.0], 'prop', 'spear_head', ghost=True)
        B.add_capsule(tip - d * hl * 0.45, tip, hw * 0.32, 1.2, 'prop', 'spear_head', ghost=True)
    elif kind == 'bow':
        belly = _perp(d, turn(pr.get('yaw', 0.0)) @ FWD * pr.get('belly', 1.0))
        brace = pr.get('brace', 0.13 * (L + back))
        upper, lower = bow_points(grip, d, belly, L, back, brace, pr.get('recurve', 0.05 * (L + back) / 2))
        B.add_capsule(grip - d * 13, grip + d * 13, 5.5, 5.5, 'prop', 'bow_grip', ghost=True)
        for limb, nm in ((upper, 'bow_limb_upper'), (lower, 'bow_limb_lower')):
            for i in range(len(limb) - 1):
                r0 = 4.5 - 2.0 * i / (len(limb) - 1)
                r1 = 4.5 - 2.0 * (i + 1) / (len(limb) - 1)
                B.add_capsule(limb[i], limb[i + 1], r0, r1, 'prop', nm, ghost=True)
        B.add_capsule(upper[-1], lower[-1], 1.3, 1.3, 'prop', 'bow_string', ghost=True)
        J['prop_tip'], J['prop_base'] = upper[-1], lower[-1]
        J['bow_upper'], J['bow_lower'], J['bow_belly'] = upper[-1], lower[-1], belly
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


ELBOW_FLEX_MAX = 145.0     # a human elbow: flexion at most 145 deg (forearm-to-upper-arm angle >= 35 deg) - checks.py
ARM_ABD_RANGE = (-70.0, 60.0)   # arm out to the side (+) / across the body (-), deg
ARM_TWIST_RANGE = (-30.0, 90.0)  # upper-arm rotation: + = inward (the forearm turns across the body), deg
IK3D_REG = 0.04            # px of reach traded per deg of abduction / twist away from 0 (picks the relaxed arm of the family)


WRIST_IK_MARGIN = 12.0     # arm_ik3d keeps the second hand's wrist this far inside its range when the arm family allows
WRIST_IK_W = 0.6           # px of reach traded per deg the wrist is outside that margin


def arm_ik3d(P, pose, side, goal, iters=80, weapon_dir=None, limit=None):
    """3D arm IK: (shoulder, elbow, arm_abd, arm_twist) of `side` that put its HAND centre (rig.fk 'hand' joint, wrist
    bend kept) on the world point `goal` - across the body when the goal is on the other side (the second hand of a
    two-handed grip: the upper arm turns inward, arm_twist). Four angles for three coordinates: of the family that reaches
    the goal the most relaxed arm is taken (abduction and twist kept near 0, IK3D_REG); the elbow stays inside
    0..ELBOW_FLEX_MAX. With `weapon_dir` (the weapon the hand holds) the family member whose wrist (weapon vs this
    forearm in its own bending plane, weapon_angle_hand) is inside `limit` (default WEAPON_LIMIT) by WRIST_IK_MARGIN is
    preferred - the wrist rule holds for the second hand too. Damped least squares from a few starts.
    -> (shoulder, elbow, abd, twist, residual px)"""
    q = full_pose(pose)
    B = fk(P, q)
    sho = B.joints['S' + side]
    Rb = arm_base(q)
    goal = np.asarray(goal, float)
    lo = np.array([-120.0, 0.0, ARM_ABD_RANGE[0], ARM_TWIST_RANGE[0]])
    hi = np.array([160.0, ELBOW_FLEX_MAX, ARM_ABD_RANGE[1], ARM_TWIST_RANGE[1]])

    def hand_of(x):
        qq = dict(q)
        qq['shoulder_' + side], qq['elbow_' + side], qq['arm_abd_' + side], qq['arm_twist_' + side] = x
        return arm_chain(P, qq, side, sho, Rb)[2]

    wlo, whi = limit if limit is not None else WEAPON_LIMIT
    wlo, whi = wlo + WRIST_IK_MARGIN, whi - WRIST_IK_MARGIN

    reg = [IK3D_REG]

    def resid(x):
        qq = dict(q)
        qq['shoulder_' + side], qq['elbow_' + side], qq['arm_abd_' + side], qq['arm_twist_' + side] = x
        _, _, hand, _, R_fa, _ = arm_chain(P, qq, side, sho, Rb)
        extra = [reg[0] * x[2], reg[0] * x[3]]
        if weapon_dir is not None:
            v = R_fa.T @ weapon_dir         # the forearm runs along local -y: angle from it, + = the flex sense
            a = _wrap(math.degrees(math.atan2(v[1], v[0])) + 90.0)
            extra.append(WRIST_IK_W * (max(0.0, wlo - a) + max(0.0, a - whi)))
        return np.concatenate([hand - goal, extra])

    sh0, el0 = arm_ik(P, q, sho, goal - (B.joints['hand' + side] - B.joints['wri' + side]))
    best = None
    for start in ((sh0, max(el0, 5.0), 0.0, 0.0), (sh0, 60.0, -30.0, 40.0), (40.0, 90.0, -20.0, 70.0), (0.0, 60.0, 0.0, 20.0)):
        x = np.clip(np.array(start, float), lo, hi)
        lam = 1e-2
        r = resid(x)
        for _ in range(iters):
            Jm = np.zeros((len(r), 4))
            for k in range(4):
                dx = np.zeros(4)
                dx[k] = 0.05
                Jm[:, k] = (resid(x + dx) - resid(x - dx)) / 0.1
            step = -np.linalg.solve(Jm.T @ Jm + lam * np.eye(4), Jm.T @ r)
            xn = np.clip(x + np.clip(step, -15.0, 15.0), lo, hi)
            rn = resid(xn)
            if rn @ rn < r @ r - 1e-12:
                x, r = xn, rn
                lam = max(lam * 0.3, 1e-7)
            else:
                lam *= 10.0
                if lam > 1e8:
                    break
        cost = float(r @ r)
        if best is None or cost < best[0] - 1e-9:
            best = (cost, x)
    x = best[1]
    # polish: the regularisation picked the family member; a few steps without it put the hand exactly on the goal
    reg[0] = 1e-4
    r = resid(x)
    lam = 1e-3
    for _ in range(20):
        Jm = np.zeros((len(r), 4))
        for k in range(4):
            dx = np.zeros(4)
            dx[k] = 0.02
            Jm[:, k] = (resid(x + dx) - resid(x - dx)) / 0.04
        xn = np.clip(x - np.linalg.solve(Jm.T @ Jm + lam * np.eye(4), Jm.T @ r), lo, hi)
        rn = resid(xn)
        if rn @ rn < r @ r:
            x, r = xn, rn
            lam *= 0.3
        else:
            lam *= 10.0
        if np.linalg.norm(hand_of(x) - goal) < 1e-4 or lam > 1e6:
            break
    res = float(np.linalg.norm(hand_of(x) - goal))
    return float(x[0]), float(x[1]), float(x[2]), float(x[3]), res


def scaled(P, k):
    Q = copy.deepcopy(P)
    for key, v in Q.items():
        if isinstance(v, list):
            Q[key] = [x * k for x in v]
        else:
            Q[key] = v * k
    return Q
