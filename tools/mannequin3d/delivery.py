"""Compare a painted gait delivery with the 3D-mannequin request it was painted over (owner verdict 2026-11-28).

  python3 tools/mannequin3d/delivery.py art/requests/gait/heavy__hero_oswin/pose.json STRIP_A.png STRIP_B.png

The batch-1 deliveries passed every pixel check and still went wrong in ways the request's pose.json can see:
  feet     the REACH frame (slot 4) drawn as a push-off: the swing foot left behind the hip, the rear foot pushed back to
           the slot band edge (the next contact then snaps the foot ~110 px forward in one frame). Per frame the front-most
           and rear-most foot pixels (bottom 34 rows) are compared with the guide's (rear heel .. front toe); FAIL when a
           no-flight REACH frame has its front-most foot behind the hip column while the guide's is ahead, WARN when an
           extent is more than FEET_TOL px off
  band     a figure pixel ON the band lines x=32 / x=351 of a slot (drawn up to the line and clipped)               WARN
  top pin  the topmost pixel sits on the mannequin's HEAD-top row (+-1) in >= 6 of 8 frames while the guide's weapon tip
           is above the head - the weapon was squeezed under the head row (bent spear, shortened greatsword)        WARN
  weapon   the delivered silhouette sampled along the table's butt -> tip line (pose.json weapon_px): the outer fifth
           toward the tip must have figure pixels within +-WEAPON_TOL px of the line                                WARN
  V2       head top vs the guide: median over the frames of (painted head-band top - head_top_px), the head-band top being
           the topmost row with >= 6 figure px in x headtop-45 .. headtop+35 with the weapon line masked out
           (head_band_top). More than HEAD_TOP_WARN px under the mannequin's head top = the figure was drawn shorter / sunk
           (Oswin +32, Magda +20, Grom +17; accepted runs -5..+1)                                                    WARN
           (only a WARN: 3D guide head tops sit 10-23 px above the idle top on most requests; the FAIL for a sunk figure is
           V1 in tools/art/gait_body.py, measured against the idle drawing)
Prints one line per finding, ends with RESULT: PASS | WARN | FAIL. Exit 1 on FAIL. Reads only.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

SLOT, FLOOR, HIP_X = 384, 870, 192
BAND = (32, 351)
FEET_ROWS = 34
FEET_TOL = 20
WEAPON_TOL = 6
HEAD_TOP_WARN = 12       # V2: median (painted head-band top - guide head_top_px) in px
BAND_L, BAND_R, BAND_MIN = 45, 35, 6   # head band: x headtop-45 .. headtop+35, a row counts with >= 6 figure px
MAGENTA = np.array([255, 0, 255])


def fg_mask(img):
    a = np.asarray(img.convert('RGBA')).astype(int)
    rgb, al = a[..., :3], a[..., 3]
    return (al > 0) & (np.abs(rgb - MAGENTA).sum(-1) > 60)


def slots(strip):
    m = fg_mask(Image.open(strip))
    return [m[:, k * SLOT:(k + 1) * SLOT] for k in range(m.shape[1] // SLOT)]


def frame_origin(fr, light):
    """x of the slot's left edge in the pose.json coordinates (light run: strip x; heavy / robe: slot x)"""
    return (fr['slot'] - 1) * SLOT if light else 0


def weapon_mask(fr, light, shape, half_w=10, head_r=45):
    """True on the table weapon (pose.json weapon_px): a band of +-half_w px along butt -> tip (15 px past the butt,
    40 px past the tip) and a disc of head_r px at the tip (mace ball, staff ring, guard)"""
    m = np.zeros(shape, bool)
    w = fr.get('weapon_px')
    if not w:
        return m
    o = frame_origin(fr, light)
    b = np.array([w['butt'][0] - o, w['butt'][1]], float)
    t = np.array([w['tip'][0] - o, w['tip'][1]], float)
    d = t - b
    L = float(np.linalg.norm(d)) or 1.0
    d /= L
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    vx, vy = xx - b[0], yy - b[1]
    along = vx * d[0] + vy * d[1]
    perp = np.abs(vx * d[1] - vy * d[0])
    m |= (along > -15) & (along < L + 40) & (perp < half_w)
    m |= (xx - t[0]) ** 2 + (yy - t[1]) ** 2 < head_r ** 2
    return m


def head_band_top(mask, fr, light):
    """topmost row with >= BAND_MIN figure px in the head band x headtop-45 .. headtop+35 (the guide's head-top joint,
    else its neck), the table weapon masked out -> int or None. mask: one 384-px slot."""
    J = fr.get('joints') or {}
    o = frame_origin(fr, light)
    j = J.get('headtop') or J.get('neck0')
    if not j:
        return None
    hx = j[0] - o
    x0, x1 = max(0, int(hx - BAND_L)), max(0, int(hx + BAND_R))
    band = mask[:, x0:x1] & ~weapon_mask(fr, light, mask.shape)[:, x0:x1]
    rows = np.flatnonzero(band.sum(1) >= BAND_MIN)
    return int(rows.min()) if rows.size else None


def guide_feet(fr, light, r_foot):
    """rear heel .. front toe of the guide's feet that reach into the bottom FEET_ROWS rows (a light run's foot tucked
    high is not there in the delivery either) -> (rear, front) or None"""
    J = fr['joints']
    org = (fr['slot'] - 1) * SLOT if light else 0
    low = [s for s in 'NF' if FLOOR - fr['sole_px'][s] < FEET_ROWS - 8]
    if not low:
        return None
    toes = [J['toetip' + s][0] - org for s in low]
    heels = [J['heel' + s][0] - org - r_foot for s in low]
    return min(heels), max(toes)


def compare(pose, strips):
    frames = pose['frames']
    light = pose.get('gait') == 'run'
    rf = (pose.get('proportions') or {}).get('r_foot', 10.0)
    masks = [m for s in strips for m in slots(s)]
    out = []
    if len(masks) != len(frames):
        return [('FAIL', f'{len(masks)} slots delivered, the request has {len(frames)} frames')]
    pins, tip_above = 0, 0
    tops = []
    for fr, m in zip(frames, masks):
        name = fr['frame']
        rows = np.flatnonzero(m.any(1))
        if not rows.size:
            out.append(('FAIL', f'{name}: empty slot'))
            continue
        cols = np.flatnonzero(m[FLOOR - FEET_ROWS + 1:FLOOR + 1].any(0))
        gf = guide_feet(fr, light, rf)
        if cols.size and gf:
            g_rear, g_front = gf
            d_rear, d_front = int(cols.min()), int(cols.max())
            line = (f'{name}: feet x {d_rear}..{d_front} (guide {g_rear:.0f}..{g_front:.0f}; hip column {HIP_X})')
            reach = fr.get('phase') == 'reach'
            if reach and d_front < HIP_X <= g_front - FEET_TOL:
                out.append(('FAIL', line + ' - REACH frame: the swing foot must be AHEAD of the hip (drawn as a push-off, '
                                          'the next contact would snap it forward)'))
            elif abs(d_rear - g_rear) > FEET_TOL or abs(d_front - g_front) > FEET_TOL:
                out.append(('WARN', line + f' - more than {FEET_TOL} px off'))
            else:
                out.append(('OK', line))
        edge = [x for x in BAND if m[:, x].any()]
        if edge:
            out.append(('WARN', f'{name}: figure pixels ON the band line x={edge} (drawn to the line and clipped?)'))
        head = fr.get('head_top_px', fr.get('top_px'))
        bt = head_band_top(m, fr, light)
        if bt is not None and head is not None:
            tops.append((name, bt, head))
        w = fr.get('weapon_px')
        if head is not None and abs(int(rows.min()) - head) <= 1:
            pins += 1
        if w and min(w['tip'][1], w['butt'][1]) < head - 10:
            tip_above += 1
        if w:
            org = (fr['slot'] - 1) * SLOT if light else 0
            b = np.array([w['butt'][0] - org, w['butt'][1]])
            t = np.array([w['tip'][0] - org, w['tip'][1]])
            hits = []
            for u in np.linspace(0.8, 1.0, 9):
                p = b + (t - b) * u
                x0, y0 = int(round(p[0])), int(round(p[1]))
                win = m[max(0, y0 - WEAPON_TOL):y0 + WEAPON_TOL + 1, max(0, x0 - WEAPON_TOL):x0 + WEAPON_TOL + 1]
                hits.append(bool(win.any()))
            if sum(hits) < 5:
                out.append(('WARN', f'{name}: the outer fifth of the weapon line (table tip ({t[0]:.0f},{t[1]:.0f})) is '
                                    f'empty in {9 - sum(hits)}/9 samples - weapon shortened, bent or at another angle?'))
    if tops:
        off = sorted(bt - h for _, bt, h in tops)
        med = float(np.median(off))
        line = (f'V2 head top vs the guide: painted head-band top - head_top_px = {med:+.0f} px median '
                f'(per frame {" ".join(f"{bt - h:+.0f}" for _, bt, h in tops)})')
        if med > HEAD_TOP_WARN:
            out.append(('WARN', line + f' - more than {HEAD_TOP_WARN} px under the mannequin head: the figure was drawn '
                                       'shorter or sunk (check V1 against the idle)'))
        else:
            out.append(('OK', line))
    if tip_above >= 4 and pins >= 6:
        out.append(('WARN', f'top pin: the topmost pixel is on the mannequin HEAD-top row in {pins}/8 frames while the '
                            'weapon tip is above the head - the weapon was squeezed under the head row'))
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 3:
        print(__doc__)
        return 2
    with open(argv[0], encoding='utf-8') as f:
        pose = json.load(f)
    res = compare(pose, argv[1:])
    for lv, msg in res:
        print(f'  [{lv}] {msg}')
    worst = 'FAIL' if any(lv == 'FAIL' for lv, _ in res) else ('WARN' if any(lv == 'WARN' for lv, _ in res) else 'PASS')
    print(f'RESULT: {worst} ({os.path.basename(argv[1])}, {os.path.basename(argv[2])} vs {argv[0]})')
    return 1 if worst == 'FAIL' else 0


if __name__ == '__main__':
    sys.exit(main())
