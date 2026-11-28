"""Automatic checks for the 3D mannequin guides. Every check returns (level, message) with level 'OK', 'WARN' or 'FAIL';
build.py writes them to build_log.txt and exits non-zero when any check FAILs (the guides are still written, so the
failure can be looked at).

Run (gait) checks - gait_checks():
  floor       no pixel below the floor row 870; the stance sole's lowest pixel ON 870 in every stance frame        FAIL
  flight      light run flight frames clear the floor by >= min_flight_px (18)                                     FAIL
  planted     each planted toe retreats step/4 (+-1 px) a cell on screen (js/battle.js runCells cadence)            FAIL
  ik          every stance foot reached (no straightened leg short of its target)                                  FAIL
  knee        stance knee flex >= 10 deg (a locked straight knee reads as a stilt; too long a stride)              FAIL
  mirror      knee flex of the near leg at frame f == far leg at f+4 (+-3 deg); hip height +-1 px                   FAIL
  band        everything incl. props inside the slot band x 32..351                                                FAIL
  margin      every frame keeps >= 8 px (BAND_MARGIN) to that band, props included - room for the painted cloth, hair
              and the real weapon shape (review 2026-11-28); fix it by carry angles / positions, never by shrinking   WARN
  feet        each foot keeps >= 75% of its own area clear of the other leg (no two-feet blob); a foot lifted >= 8 px
              while passing a planted one >= 45% (it may go behind the planted ankle, as in the 2D bases)        FAIL
  knees       the far knee is visible or >= 14 px from the near knee on screen                                     WARN
  upper body  each hand travels >= 12 px (relative to the hip) over the cycle - no frozen cut-out torso             FAIL
  props       a mace / weapon head is >= its radius + 8 px from the other hand (not sitting on the shield hand)     FAIL
  weapon      hand range (owner 2026-11-28): every held weapon's GRIP AXIS angle to its forearm (a reverse grip: the thumb
              side of the fist, the blade flipped) inside the character's
              weapon_limit [0, 120] deg (0 = straight along the forearm, + = upward) in EVERY frame - a frame that
              needed rig.py's clamp FAILs (no blade bent down past the arm line, dangling)                        FAIL
  blade/head  (sword carriers) blade-over-head pixels, reported only (owner 11-28: overlaps are fine; the z-buffer
              draws the nearer part over the farther one)                                                        INFO
  robe        hem bottom 38-52 px above the floor (robe_base); hem width change <= 15% between frames; the robe is
              widest within 14 px of its hem (cloth flares to the hem, no gourd)                                   FAIL
Action checks - action_checks():
  weapon      hand range as above, every action frame (READY and in-betweens included)                            FAIL
  blade/head, blade/trunk  overlap pixels, reported only (owner 11-28: overlaps fine, depth order decides)        INFO
  blade dir   screen direction of the blade, reported only (owner 11-28: up or down does not matter as long as
              the wrist range relative to the forearm holds - that is the 'weapon' check)                          INFO
  (props below the floor line are touched up when drawn - owner 11-28; body/feet floor rules stay FAIL)
  band, floor, ik as above (each frame placed by its own feet centre, the sheets' pose_feet_x rule)               FAIL
"""
import math

import numpy as np

from render import rasterize, FLOOR, HIP_X, SLOT_W

BAND = (32, SLOT_W - 1 - 32)
BAND_MARGIN = 8
FAIL, WARN, OK = 'FAIL', 'WARN', 'OK'
FEET_VIS, FEET_VIS_PASSING, FEET_LIFT = 0.75, 0.45, 8


def extent_x(img, bg=(255, 0, 255)):
    a = np.asarray(img.convert('RGB')).astype(int)
    nz = np.flatnonzero((np.abs(a - np.array(bg)).sum(-1) > 0).any(0))
    return int(nz.min()), int(nz.max())


def part_mask(body, cam, parts, ghosts=False):
    """screen mask of the named parts alone (no occlusion by the rest)"""
    prims = [p for p in (body.ghosts if ghosts else body.prims) if p['part'] in parts]
    if not prims:
        return np.zeros((cam.size[1], cam.size[0]), bool)
    buf, _, _ = rasterize(prims, cam, *cam.size)
    return buf.depth > -np.inf


def visible_fraction(body, cam, parts, blockers=None):
    """share of the parts' own screen area that is not hidden in the rendered frame (body.render_info) - by anything,
    or only by the `blockers` parts when given (e.g. the other leg: two feet merging)"""
    own = part_mask(body, cam, parts)
    if not own.any():
        return 1.0
    info = body.render_info
    names = np.array(info['parts'], dtype=object)
    hit = np.zeros_like(own)
    sel = info['buf'].part >= 0
    if blockers is None:
        hit[sel] = ~np.isin(names[info['buf'].part[sel]], list(parts))
    else:
        hit[sel] = np.isin(names[info['buf'].part[sel]], list(blockers))
    return float((own & ~hit).sum() / own.sum())


LEG = ('foot', 'instep', 'ankle', 'shin', 'thigh')


def weapon_checks(label, names, bodies):
    """hand range of motion: FAIL when any frame's requested weapon direction was outside [min, max] of its forearm
    (rig.py clamped it); reports the measured angle per frame and the range"""
    rows = [(n, w) for n, b in zip(names, bodies) for w in b.weapons]
    if not rows:
        return []
    lim = rows[0][1]['limit']
    bad = [f"{n} {w['kind']} {w['raw_deg']:.1f}" for n, w in rows if w['clamped']]
    raws = [w['raw_deg'] for _, w in rows]
    rv = [w['blade_deg'] for _, w in rows if w.get('grip') == 'reverse' and 'blade_deg' in w]
    return [(FAIL if bad else OK,
             f"{label}weapon angle to the forearm (deg, 0 = straight, + = up; range {lim[0]:g}..{lim[1]:g}) per frame "
             + ' '.join(f"{n}:{w['raw_deg']:.0f}" for n, w in rows) + f"  -> {min(raws):.1f}..{max(raws):.1f}"
             + (f"  OUTSIDE (clamped by the rig): {bad}" if bad else '')
             + (f"  [REVERSE grip: measured on the grip axis (thumb side of the fist); the blade is flipped 180 deg -> "
                f"{min(rv):.0f}..{max(rv):.0f} deg from the forearm]" if rv else ''))]


# weapon stability (owner verdict 2026-11-28: bent spear, wobbling greatsword / mace): every held weapon is ONE rigid object
W_LEN_TOL = 0.02            # on-screen butt -> tip length within +-2% over the cycle
W_STEP = {1: 3.5, 2: 1.5}   # deg between neighbouring frames: one-handed (arm sway) / two-handed (chest-locked)
W_RANGE = {1: 8.5, 2: 4.0}  # deg over the cycle (one-handed: +-4 deg sway, seen at the 3/4 camera)
W_TIP_STEP = 0.08           # tip move per frame <= 0.08 x the weapon length, relative to the chest (two-handed) or
                            # to its fist (one-handed: the weapon's own turn, the arm's swing excluded)
W_REVERSALS = 2             # tip path direction reversals (turn > 120 deg between moves >= max(2 px, 1% length)) per cycle
W_GRIP_TOL = 3.0            # two-handed: the grip stays within +-3 px of its chest-fixed place; strip a vs b <= 3 px / 1 deg
W_IDLE_WARN = 15.0          # |run carry angle - idle angle| above this: WARN, and the README must say it


def _wrapd(a):
    return (a + 180.0) % 360.0 - 180.0


SWING_STEP_MAX = 1.5        # each swing-foot step <= 1.5 x the accepted 2D base's step (x the sheet's stride factor)
REACH_SOLE_MIN = 4          # the reach frame's swing sole >= 4 px up (not a second contact frame)
TOE_OFF_SOLE_MAX = 10       # the first swing frame lifts the foot <= 10 px (x the leg factor): no snap up
REACH_AHEAD_MIN = 15        # the reach frame's swing ankle >= 15 px ahead of the hip column (x the stride factor)
REAR_FLEX_MAX = 30.0        # the trailing leg at double support: knee flex <= 30 deg ...
REAR_THIGH_MAX = -12.0      # ... and its thigh >= 12 deg behind vertical on screen (2D bases: -16..-28)


def foot_paths(spec, recs, slot_rel=True):
    """per leg, the swing cycle of a no-flight gait (heavy / robe): [(frame, ankle x, sole px up, knee x, thigh deg)] from
    the trailing contact through lift, passing and reach to the next contact (hip-relative screen px)"""
    out = {}
    for s, start in (('N', 4), ('F', 0)):
        seq = []
        for k in range(5):
            r = recs[(start + k) % 8]
            J = r['joints']
            org = (r['slot'] - 1) * 384 if spec['gait'] == 'run' else 0
            hx = J['hip'][0] - org
            H, K, A = J['H' + s], J['knee' + s], J['ank' + s]
            seq.append((r['frame'], round(A[0] - org - hx, 1), FLOOR - r['sole_px'][s], round(K[0] - org - hx, 1),
                        round(math.degrees(math.atan2(K[0] - H[0], K[1] - H[1])), 1), r['knee_flex_deg'][s]))
        out[s] = seq
    return out


def foot_path_checks(spec, recs):
    """owner verdict 2026-11-28 (the back foot snapped, only the foot trailed back): the swing foot of heavy / robe moves
    forward every frame in the accepted 2D bases' rhythm, the reach frame is a reach (ahead of the hip, off the floor), the
    toe-off does not snap up, and the trailing leg at double support is a straight-ish leg angled back"""
    if 'swing_target' not in spec:
        return []
    k = spec['stride_k']
    kh = spec.get('leg_k', 1.0)
    ref = spec['swing_ref']
    out = []
    for s, seq in foot_paths(spec, recs).items():
        leg = 'near' if s == 'N' else 'far'
        xs = [a for _, a, _, _, _, _ in seq]
        steps = [round(xs[i + 1] - xs[i], 1) for i in range(4)]
        lim = [round(SWING_STEP_MAX * r * k, 1) for r in ref]
        bad = [i for i in range(4) if steps[i] <= 0 or steps[i] > lim[i]]
        out.append((FAIL if bad else OK, f'{leg} swing foot: ankle x {" -> ".join(f"{f} {a:+.0f}" for f, a, *_ in seq)} = steps '
                    f'{steps} px (each > 0 and <= 1.5 x the 2D base {lim}; 2D {[round(r * k, 1) for r in ref]})'))
        kx = [kx_ for _, _, _, kx_, _, _ in seq[1:4]]
        over = any(kx[i + 1] < kx[i] - 2.0 for i in range(2))
        out.append((FAIL if over else OK, f'{leg} swing knee x (lift / passing / reach) {kx} - moves forward, no overshoot'))
        lift, reach = seq[1], seq[3]
        okr = reach[2] >= REACH_SOLE_MIN and reach[1] >= REACH_AHEAD_MIN * k
        out.append((OK if okr else FAIL, f'{leg} REACH {reach[0]}: swing ankle {reach[1]:+.0f} px ahead of the hip '
                    f'(>= {REACH_AHEAD_MIN * k:.0f}), sole {reach[2]} px up (>= {REACH_SOLE_MIN}) - not a second contact'))
        okt = lift[2] <= TOE_OFF_SOLE_MAX * kh
        out.append((OK if okt else FAIL, f'{leg} toe-off {lift[0]}: sole {lift[2]} px up (<= {TOE_OFF_SOLE_MAX * kh:.0f}) - '
                    'no snap up'))
        rear = seq[0]
        okc = rear[5] <= REAR_FLEX_MAX and rear[4] <= REAR_THIGH_MAX
        out.append((OK if okc else FAIL, f'{leg} trailing leg at contact {rear[0]}: knee flex {rear[5]} (<= {REAR_FLEX_MAX:g}), '
                    f'thigh {rear[4]:+.0f} deg (<= {REAR_THIGH_MAX:g}: angled back, not a vertical thigh with the foot '
                    'dragged behind)'))
    return out


def weapon_stability(recs, carry=None):
    """the weapon rules on pose.json `weapon_px` (build.weapon_px) -> [(level, message)]"""
    W = [r.get('weapon_px') for r in recs]
    if not all(W):
        return []
    n = len(W)
    hands = 2 if W[0].get('two_hand') else 1
    rel = lambda w, k: np.array(w[k]) - np.array(w['chest'])
    out = []
    L = np.array([w['length_px'] for w in W])
    dl = (L.max() - L.min()) / L.mean()
    out.append((FAIL if dl > 2 * W_LEN_TOL else OK,
                f"weapon rigid: butt->tip {L.min():.1f}..{L.max():.1f} px on screen (spread {dl * 100:.1f}% of the mean, <= +-{W_LEN_TOL * 100:.0f}%), "
                f"fist->tip {min(w['fist_tip_px'] for w in W):.0f}..{max(w['fist_tip_px'] for w in W):.0f}, one straight "
                f"{W[0]['kind']} (a rigid capsule: never bent, shortened or stretched)"))
    A = np.array([w['angle_deg'] for w in W])
    wp = next((p for p in (carry or {}).get('props', []) if p.get('kind') == W[0]['kind']), {})
    # a weapon set in the HAND frame (no abs_angle: e.g. a reverse-gripped dagger lying along the forearm) is part of the
    # forearm - it turns with the arm pump; it must hold its angle TO THE FOREARM instead
    in_hand = bool(wp) and wp.get('abs_angle') is None and not wp.get('between')
    if in_hand:
        F = np.array([w0['raw_deg'] for r in recs for w0 in (r.get('weapon_angle') or [])[:1]])
        steps = [abs(_wrapd(F[(i + 1) % n] - F[i])) for i in range(n)]
        rng = float(max(abs(_wrapd(a - b)) for a in F for b in F))
        ok = max(steps) <= W_STEP[1] + 1e-6 and rng <= W_RANGE[1] + 1e-6
        out.append((OK if ok else FAIL, f"weapon held in the hand frame (it rides the forearm): angle TO THE FOREARM per frame "
                    + ' '.join(f"{r['frame']}:{a:.1f}" for r, a in zip(recs, F))
                    + f"  max step {max(steps):.2f} deg (<= {W_STEP[1]}), range {rng:.2f} (<= {W_RANGE[1]}); on screen "
                    f"{' '.join(f'{a:.0f}' for a in A)} with the arm"))
    else:
        steps = [abs(_wrapd(A[(i + 1) % n] - A[i])) for i in range(n)]
        rng = float(max(abs(_wrapd(a - b)) for a in A for b in A))
        ok = max(steps) <= W_STEP[hands] + 1e-6 and rng <= W_RANGE[hands] + 1e-6
        out.append((OK if ok else FAIL,
                    f"weapon angle ({'two-handed, chest-locked' if hands == 2 else 'one-handed'}): "
                    + ' '.join(f"{r['frame']}:{a:.1f}" for r, a in zip(recs, A))
                    + f"  max step {max(steps):.2f} deg (<= {W_STEP[hands]}), range {rng:.2f} deg (<= {W_RANGE[hands]})"))
    T = [rel(w, 'tip') if hands == 2 else np.array(w['tip']) - np.array(w['fist']) for w in W]
    mv = [float(np.hypot(*(T[(i + 1) % n] - T[i]))) for i in range(n)]
    rev = 0
    small = max(2.0, 0.01 * L.mean())
    for i in range(n):
        a, b = T[i] - T[i - 1], T[(i + 1) % n] - T[i]
        if np.hypot(*a) >= small and np.hypot(*b) >= small:
            c = float(a @ b / (np.hypot(*a) * np.hypot(*b)))
            if c < math.cos(math.radians(120)):
                rev += 1
    lim = W_TIP_STEP * L.mean()
    if in_hand:
        out.append((OK, f'weapon tip path: rides the forearm (hand-frame weapon) - moves {" ".join(f"{m:.0f}" for m in mv)} px '
                        'with the arm pump (checked as the angle to the forearm above)'))
    else:
        out.append((OK if max(mv) <= lim and rev <= W_REVERSALS else FAIL,
                    f'weapon tip path (relative to {"the chest" if hands == 2 else "its fist"}): moves '
                    f'{" ".join(f"{m:.0f}" for m in mv)} px (<= {lim:.0f}), {rev} reversals (<= {W_REVERSALS}) - one smooth '
                    'path, no back-and-forth'))
    if hands == 2:
        G = np.array([rel(w, 'fist') for w in W])
        dev = float(np.max(np.hypot(*(G - G.mean(0)).T)))
        ab = []
        if n == 8:
            for i in range(4):
                j = i + 4
                ab.append(max(abs(_wrapd(A[i] - A[j])),
                              *(float(np.hypot(*(rel(W[i], k) - rel(W[j], k))))
                                for k in ('fist', 'tip'))))
        al = [w.get('fist2_along_px') for w in W if w.get('fist2_along_px') is not None]
        spread = (max(al) - min(al)) if al else 0.0
        okg = (dev <= W_GRIP_TOL + 1e-6 and (not ab or max(ab) <= W_GRIP_TOL + 1e-6)
               and spread <= 2 * W_GRIP_TOL + 1e-6)
        out.append((OK if okg else FAIL, f'two-handed grip fixed to the chest: deviation {dev:.1f} px (<= {W_GRIP_TOL:g}); '
                    f'strip a vs b at the same leg phase (deg / px) {" ".join(f"{v:.1f}" for v in ab)} (<= {W_GRIP_TOL:g}); '
                    f'fist-to-fist on screen {min(al or [0]):.0f}..{max(al or [0]):.0f} px (spread <= {2 * W_GRIP_TOL:g}: both '
                    'fists keep their places on the grip)'))
    idle = wp.get('idle_deg')
    run = run_angle(W)
    if idle is None:
        out.append((WARN, f'weapon idle angle not measured (carry3d props[].idle_deg) - the run carry ({run:.0f} deg) cannot '
                          'be compared with the idle drawing'))
    else:
        d = _wrapd(run - float(idle))
        out.append((WARN if abs(d) > W_IDLE_WARN else OK,
                    f'weapon run angle {run:.0f} vs idle {float(idle):.0f} deg ({d:+.0f}; > {W_IDLE_WARN:g} -> WARN, the README '
                    'states the change)'))
    return out


def run_angle(W):
    """circular mean of the on-screen weapon angle (butt -> tip, deg from forward, + = up) over the frames"""
    a = np.radians([w['angle_deg'] for w in W])
    return float(math.degrees(math.atan2(np.sin(a).mean(), np.cos(a).mean())))


def gait_checks(spec, recs, bodies, plains, cam, carry=None):
    out = []
    step4 = spec['step_px'] / 4
    tops = [r['top_px'] for r in recs]
    out.append((OK, f"head top y {min(tops)}..{max(tops)} (spread {max(tops) - min(tops)} px), hip height "
                    f"{min(r['hip_height_px'] for r in recs)}..{max(r['hip_height_px'] for r in recs)}, lean "
                    f"{min(r['lean_deg'] for r in recs)}..{max(r['lean_deg'] for r in recs)} deg"))
    # floor
    bad = [r['frame'] for r in recs if r['lowest_px'] > FLOOR or (r['feet_down'] and r['lowest_px'] != FLOOR)]
    out.append((FAIL if bad else OK, 'floor: lowest pixel per frame ' + ' '.join(f"{r['frame']}:{r['lowest_px']}" for r in recs)
                + (f'  (off the floor / below it: {bad})' if bad else '')))
    fl = [r for r in recs if r['phase'] == 'flight']
    if fl:
        need = spec.get('min_flight_px', 18)
        low = [r['frame'] for r in fl if FLOOR - r['lowest_px'] < need]
        out.append((FAIL if low else OK, f'flight clearance (>= {need} px): '
                    + ', '.join(f"{r['frame']} {FLOOR - r['lowest_px']} px" for r in fl)))
    # planted toes
    for start, leg in ((0, 'N'), (4, 'F')):
        xs = []
        for k in range(len(spec['stance'])):
            r = recs[(start + k) % 8]
            org = (r['slot'] - 1) * SLOT_W if spec['gait'] == 'run' else 0
            xs.append(round(r['joints']['toetip' + leg][0] - org - HIP_X, 1))
        ret = [round(xs[i] - xs[i + 1], 1) for i in range(len(xs) - 1)]
        okr = all(abs(v - step4) <= 1.0 for v in ret)
        out.append((OK if okr else FAIL, f"planted {'near' if leg == 'N' else 'far'} toe x {xs} -> retreat per cell {ret} "
                                         f"(target {step4:.1f} +-1)"))
    bad = [r['frame'] for r in recs if not r['ik_reached']]
    out.append((FAIL if bad else OK, 'IK: every stance foot reached' if not bad else f'IK could not reach: {bad}'))
    out += foot_path_checks(spec, recs)
    lowered = [(r['frame'], r['hip_lowered_px']) for r in recs if r.get('hip_lowered_px')]
    if lowered:
        out.append((WARN, 'hip lowered to reach the planted foot: ' + ', '.join(f'{f} {v} px' for f, v in lowered)))
    # stance knee
    kn = []
    for r in recs:
        for s in r['feet_down']:
            kn.append((r['frame'], s, r['knee_flex_deg'][s[0].upper()]))
    low = [f'{f} {s} {v}' for f, s, v in kn if v < 10.0]
    out.append((FAIL if low else OK, f'stance knee flex >= 10 deg: min {min(v for _, _, v in kn):.1f}'
                + (f'  too straight: {low}' if low else '')))
    # mirror halves
    dk = [abs(recs[f]['knee_flex_deg']['N'] - recs[(f + 4) % 8]['knee_flex_deg']['F']) for f in range(8)]
    dh = [abs(recs[f]['hip_height_px'] - recs[(f + 4) % 8]['hip_height_px']) for f in range(8)]
    okm = max(dk) <= 3.0 and max(dh) <= 1.0
    out.append((OK if okm else FAIL, f'mirror halves: knee flex near(f) vs far(f+4) max diff {max(dk):.1f} deg (<= 3), '
                                     f'hip height max diff {max(dh):.1f} px (<= 1)'))
    # band
    ext = [extent_x(im) for im in plains]
    okb = all(a >= BAND[0] and b <= BAND[1] for a, b in ext)
    out.append((OK if okb else FAIL, f'x extent incl. props per frame (slot band {BAND[0]}..{BAND[1]}): '
                + ' '.join(f'{a}-{b}' for a, b in ext)))
    mg = min(min(a - BAND[0], BAND[1] - b) for a, b in ext)
    out.append((OK if mg >= BAND_MARGIN else WARN, f'band margin (>= {BAND_MARGIN} px to x {BAND[0]}..{BAND[1]}, props included): '
                f'min {mg} px'))
    # feet / knees
    fv, low = [], []
    for r, b in zip(recs, bodies):
        cam.fit(b)
        vis = {'N': visible_fraction(b, cam, {'footN', 'instepN', 'ankleN'}, {p + 'F' for p in LEG}),
               'F': visible_fraction(b, cam, {'footF', 'instepF', 'ankleF'}, {p + 'N' for p in LEG})}
        fv.append((r['frame'], vis['N'], vis['F']))
        for s in 'NF':
            o = 'F' if s == 'N' else 'N'
            # passing frame (one foot lifted >= 8 px past a planted one): the feet may overlap as in the accepted 2D bases
            # (swing ankle -4 beside the stance ankle -25); the height difference keeps them two feet - depth order decides
            # (owner 11-28). Otherwise two feet merging into one blob FAIL.
            passing = ((FLOOR - r['sole_px'][s] >= FEET_LIFT and r['sole_px'][o] == FLOOR)
                       or (FLOOR - r['sole_px'][o] >= FEET_LIFT and r['sole_px'][s] == FLOOR))
            need = FEET_VIS_PASSING if passing else FEET_VIS
            if vis[s] < need:
                low.append(f'{r["frame"]} {"near" if s == "N" else "far"} {vis[s]:.2f} (< {need})')
    out.append((FAIL if low else OK, f'feet not covered by the other leg (>= {FEET_VIS}; a foot lifted >= {FEET_LIFT} px past '
                f'a planted one >= {FEET_VIS_PASSING}): '
                + ' '.join(f'{f}:{n:.2f}/{fa:.2f}' for f, n, fa in fv) + (f'  merged: {low}' if low else '')))
    kw = []
    for r, b in zip(recs, bodies):
        jN, jF = r['joints']['kneeN'], r['joints']['kneeF']
        sep = math.hypot(jN[0] - jF[0], jN[1] - jF[1])
        cam.fit(b)
        if sep < 14 and visible_fraction(b, cam, {'shinF'}) < 0.25:
            kw.append(f"{r['frame']} {sep:.0f} px")
    out.append((WARN if kw else OK, 'far knee readable (visible or >= 14 px from the near knee)' + (f': hidden {kw}' if kw else '')))
    # upper body motion
    trav = {}
    for s in 'NF':
        pts = np.array([[r['joints']['hand' + s][0] - r['joints']['hip'][0], r['joints']['hand' + s][1] - r['joints']['hip'][1]]
                        for r in recs])
        trav[s] = float(max(np.hypot(*(pts[i] - pts[j])) for i in range(8) for j in range(8)))
    locked = bool((carry or {}).get('two_hand'))
    lowh = [s for s in 'NF' if trav[s] < 12.0]
    if locked:      # both fists on a chest-locked weapon: they ride the trunk (bob, lean, twist) by design
        out.append((OK, f"hand travel over the cycle: near {trav['N']:.0f}, far {trav['F']:.0f} px (both fists on the "
                        "chest-locked two-handed weapon - they ride the trunk; the >= 12 px rule is for free hands)"))
    else:
        out.append((FAIL if lowh else OK, f"hand travel over the cycle (>= 12 px): near {trav['N']:.0f}, far {trav['F']:.0f}"))
    # props: weapon head vs the other hand
    probs = []
    for r, b in zip(recs, bodies):
        J = b.joints
        for g in b.ghosts:
            if g['part'] == 'mace_head':
                other = 'F' if 'N' in b.grips else 'N'
                cam.fit(b)
                p1, _ = cam.to_screen(g['c'])
                p2, _ = cam.to_screen(J['hand' + other])
                d = float(np.hypot(*(p1 - p2)))
                if d < g['radii'][0] + 8:
                    probs.append(f"{r['frame']} {d:.0f} px")
    if any(g['part'] == 'mace_head' for g in bodies[0].ghosts):
        out.append((FAIL if probs else OK, 'mace head clear of the shield hand (>= head radius + 8 px)' + (f': {probs}' if probs else '')))
    # weapon hand range; weapon stability; a sword blade never over the head
    out += weapon_checks('', [r['frame'] for r in recs], bodies)
    out += weapon_stability(recs, carry)
    if any(g['part'] == 'blade' for g in bodies[0].ghosts):
        hd = []
        for b in bodies:
            cam.fit(b)
            hd.append(blade_overlap(b, cam, {'head', 'nose'}))
        out.append((OK, f'blade over the head (px) per frame {hd} (info: overlap allowed, depth order decides)'))
    # robe
    if any(g['part'] == 'robe' for g in bodies[0].ghosts):
        out += robe_checks(recs, bodies, cam)
    return out


def robe_checks(recs, bodies, cam):
    out = []
    hems, widths, widest = [], [], []
    for r, b in zip(recs, bodies):
        cam.fit(b)
        m = part_mask(b, cam, {'robe'}, ghosts=True)
        rows = np.flatnonzero(m.any(1))
        hem_row = int(rows.max())
        hems.append(FLOOR - hem_row)
        w = m.sum(1)
        widths.append(int(w[hem_row - 6:hem_row + 1].max()))
        widest.append(hem_row - int(np.argmax(w)))
    okh = all(38 <= h <= 52 for h in hems)
    out.append((OK if okh else FAIL, f'robe hem bottom above the floor (38-52, robe_base): {hems}'))
    ch = [abs(widths[i] - widths[i - 1]) / max(widths[i - 1], 1) for i in range(len(widths))]
    out.append((OK if max(ch) <= 0.16 else FAIL, f'robe hem width per frame {widths} px, max change {max(ch) * 100:.0f}% (<= 15%)'))
    out.append((OK if max(widest) <= 14 else FAIL, f'robe widest row within 14 px of the hem (A-line, no bulge): {widest}'))
    return out


def blade_overlap(body, cam, parts):
    blade = part_mask(body, cam, {'blade'}, ghosts=True)
    other = part_mask(body, cam, parts)
    return int((blade & other).sum())


def action_checks(act, names, bodies, plains, recs, cam_of):
    """cam_of(i) -> the camera frame i was rendered with"""
    out = weapon_checks(f'{act}: ', names, bodies)
    head = []
    for i, b in enumerate(bodies):
        head.append(blade_overlap(b, cam_of(i), {'head', 'nose'}))
    out.append((OK, f'{act}: blade over the head (px) per frame {head} (info: overlap allowed, depth order decides)'))
    if act == 'hit':
        tr = [blade_overlap(b, cam_of(i), {'pelvis', 'spine', 'chest'}) for i, b in enumerate(bodies)]
        out.append((OK, f'{act}: blade over the trunk (px) per frame {tr} (info: overlap allowed, depth order decides)'))
    # blade direction (screen): tip relative to the fist
    dirs = []
    for i, b in enumerate(bodies):
        c = cam_of(i)
        g, _ = c.to_screen(b.joints['sword_grip'])
        t, _ = c.to_screen(b.joints['sword_tip'])
        dirs.append((round(float(t[0] - g[0])), round(float(g[1] - t[1]))))     # (+x forward, +y up)
    bad = []
    if act == 'attack':
        for nm, (dx, dy) in zip(names, dirs):
            if nm == 'windup' and not (dx < 0 and dy > 0):
                bad.append(f'{nm} blade not back and up {dx, dy}')
            if nm != 'strike' and dy < -5:
                bad.append(f'{nm} blade points down {dx, dy}')
            if nm == 'strike' and dy >= 0:
                bad.append(f'strike blade not down {dx, dy}')
    else:
        for nm, (dx, dy) in zip(names, dirs):
            if not (dy < 0 and dx <= 0):
                bad.append(f'{nm} blade not down and back {dx, dy}')
    out.append((OK, f'{act}: blade direction (tip - fist, screen x fwd / y up) {dict(zip(names, dirs))} (info only)'
                + (f'  differs from the old preference: {bad}' if bad else '')))
    ext = [extent_x(im) for im in plains]
    okb = all(a >= BAND[0] and b <= BAND[1] for a, b in ext)
    out.append((OK if okb else FAIL, f'{act}: x extent incl. props per frame {[f"{a}-{b}" for a, b in ext]} '
                                     f'(slot band {BAND[0]}..{BAND[1]}; each frame placed by its feet centre)'))
    lows = [r['lowest_px'] for r in recs]
    iks = [r['ik_reached'] for r in recs]
    out.append((OK if all(v == FLOOR for v in lows) and all(iks) else FAIL,
                f'{act}: frames {names}, lowest px {lows}, IK ok {iks}'))
    return out
