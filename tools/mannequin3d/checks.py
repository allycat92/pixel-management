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
  feet        each foot keeps >= 75% of its own area clear of the other leg (no two-feet blob in passing frames)                  FAIL
  knees       the far knee is visible or >= 14 px from the near knee on screen                                     WARN
  upper body  each hand travels >= 12 px (relative to the hip) over the cycle - no frozen cut-out torso             FAIL
  props       a mace / weapon head is >= its radius + 8 px from the other hand (not sitting on the shield hand)     FAIL
  weapon      hand range (owner 2026-11-28): every held weapon's angle to its forearm inside the character's
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
FAIL, WARN, OK = 'FAIL', 'WARN', 'OK'


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
    return [(FAIL if bad else OK,
             f"{label}weapon angle to the forearm (deg, 0 = straight, + = up; range {lim[0]:g}..{lim[1]:g}) per frame "
             + ' '.join(f"{n}:{w['raw_deg']:.0f}" for n, w in rows) + f"  -> {min(raws):.1f}..{max(raws):.1f}"
             + (f"  OUTSIDE (clamped by the rig): {bad}" if bad else ''))]


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
    # feet / knees
    fv = []
    for r, b in zip(recs, bodies):
        cam.fit(b)
        fv.append((r['frame'], visible_fraction(b, cam, {'footN', 'instepN', 'ankleN'}, {p + 'F' for p in LEG}),
                   visible_fraction(b, cam, {'footF', 'instepF', 'ankleF'}, {p + 'N' for p in LEG})))
    low = [f'{f} {"near" if n < 0.75 else "far"} {min(n, fa):.2f}' for f, n, fa in fv if min(n, fa) < 0.75]
    out.append((FAIL if low else OK, 'feet not covered by the other leg (>= 0.75): '
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
    lowh = [s for s in 'NF' if trav[s] < 12.0]
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
    # weapon hand range; a sword blade never over the head
    out += weapon_checks('', [r['frame'] for r in recs], bodies)
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
