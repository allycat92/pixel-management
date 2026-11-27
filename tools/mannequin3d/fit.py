"""Fit the 3D mannequin's proportions to a registered character from its accepted idle drawing (silhouette only).

  python3 tools/mannequin3d/fit.py sheet/class/warrior [sheet/captain/ironwall ...]   # prints the fitted proportions (JSON)

Source of the drawing (source px = the request strips' pixels, floor y = 870):
  1. art/inbox/<stem>.png in this checkout, else 2. `git show origin/art-inbox:art/inbox/<stem>.png`; the idle is the
     first pose of the 1x4 strip, cut and anchored exactly as tools/art/run_request_guides.py does (geometry()).
  3. If neither exists: frame 0 of the registered sheet (assets/art/sheets/*.png) blown up by 1/scale (coarse).

What is measured on the idle silhouette (all heights above the floor, source px):
  top       first row from the top whose silhouette is >= 14 px wide (helmet spikes, plumes, hat tips are skipped);
            `top_raw` is the very first pixel. height = 871 - top.
  hat       a hat brim (a row band >= 1.5x wider than 15 px above and below it, in the top 35%) moves the top down to
            0.45 head above the brim (the brim sits at about the eyes): hats and hoods are costume, not body.
  head      the neck = the narrowest row (width of the run through the head's centre column) between 17% and 36% of
            the height below the top; head = neck - top. Falls back to height / heads (phase3.json "heads", 4).
  shoulder  first row under the neck where that run is >= 1.5 x the neck width (fallback: neck + 0.22 head).
  hip       the crotch: going up from the feet, the last row that still shows two separate legs (gap >= 4 px).
            Accepted only if it lands at 33-50% of the height (a tabard / robe hem closes the gap lower or not at
            all) -> hip = crotch + 0.09 x height; otherwise hip = 0.43 x height (canonical 4-head ratio).
  reach     furthest silhouette pixel in front of / behind the anchor column between the shoulder and the hip rows
            (includes held weapons and shields: reported, not used for the arm length).
  leg_w     limb bulk: per leg the narrowest run 25-65 px above the floor (lower leg / boot), median of the two legs.
            Robes hide the legs -> no value (bulk 1). Arms, weapons and shields make trunk widths useless, so the trunk
            radii follow the limb bulk half way.
Every number is also measured, the same way, on the canonical mannequin rendered in an idle stance (wide stance like
the sheets), and the RATIOS drawing / mannequin set the factors: height -> uniform scale; head (clamped 0.8-1.25);
trunk length from shoulder - hip (0.85-1.2); legs from a measured crotch only (0.85-1.15); limb bulk (0.85-1.45).
Arms keep the canonical arm : height ratio. A last pass rescales so the fitted mannequin's idle has the measured height.
The result is a rig proportions dict (rig.CANON keys).
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'tools', 'art'))

from rig import CANON, scaled, fk  # noqa: E402

FLOOR = 870
MIN_TOP_W = 14


def load_json(rel):
    with open(os.path.join(REPO, rel), encoding='utf-8') as f:
        return json.load(f)


def idle_drawing(sid):
    """-> (rgb array of the 1536x1024 source strip or None, idle mask in source px with the anchor column, info)"""
    import run_request_guides as rrg
    man = load_json('assets/art/manifest.json')
    e = man[sid]
    stem = os.path.splitext(os.path.basename(e['file']))[0]
    rel = f'art/inbox/{stem}.png'
    src = None
    origin = None
    if os.path.exists(os.path.join(REPO, rel)):
        src, origin = np.asarray(Image.open(os.path.join(REPO, rel)).convert('RGB')), rel
    else:
        r = subprocess.run(['git', '-C', REPO, 'show', f'origin/art-inbox:{rel}'], capture_output=True)
        if r.returncode == 0:
            import io
            src, origin = np.asarray(Image.open(io.BytesIO(r.stdout)).convert('RGB')), f'origin/art-inbox:{rel}'
    req = rrg.request_item(sid)
    scale = req.get('scale') or 0.1654
    if src is not None and os.path.exists(os.path.join(REPO, rel)):
        geo = rrg.geometry(sid, man)
        mk = rrg.fig_mask(rrg.gait_idle_source(src, req.get('layout'), req.get('gait_split')))
        x0, x1 = geo['idle_x']
        idle = np.zeros_like(mk)
        idle[:, x0:x1 + 1] = mk[:, x0:x1 + 1]
        rgb = src.copy()
        return rgb, idle, {'source': origin, 'anchor_col': geo['anchor_col'], 'scale': scale, 'heads': req.get('heads', 4),
                           'idle_x': [x0, x1], 'stem': stem}
    if src is not None:
        mk = rrg.fig_mask(src)
        col = mk.any(0)
        x0 = int(np.argmax(col))
        x1 = x0
        while x1 + 1 < len(col) and col[x1 + 1]:
            x1 += 1
        idle = np.zeros_like(mk)
        idle[:, x0:x1 + 1] = mk[:, x0:x1 + 1]
        return src, idle, {'source': origin, 'anchor_col': float(rrg.feet_x(idle)), 'scale': scale,
                           'heads': req.get('heads', 4), 'idle_x': [x0, x1], 'stem': stem}
    # registered sheet frame 0, blown up
    meta = e['sheet']
    g = np.asarray(Image.open(os.path.join(REPO, e['file'])).convert('RGBA'))
    cw, ch = meta['cell']
    fx, fy = meta['frames'][0]
    cell = g[fy:fy + ch, fx:fx + cw]
    k = 1.0 / scale
    big = np.asarray(Image.fromarray(cell).resize((int(cw * k), int(ch * k)), Image.Resampling.NEAREST))
    ax, ay = meta['anchor']
    rgb = np.zeros((1024, 384, 3), np.uint8)
    rgb[:] = (255, 0, 255)
    ox, oy = int(round(192 - ax * k)), int(round(FLOOR + 1 - ay * k))
    a = big[..., 3] > 0
    ys, xs = np.nonzero(a)
    ok = (ys + oy >= 0) & (ys + oy < 1024) & (xs + ox >= 0) & (xs + ox < 384)
    rgb[ys[ok] + oy, xs[ok] + ox] = big[ys[ok], xs[ok], :3]
    idle = np.zeros((1024, 384), bool)
    idle[ys[ok] + oy, xs[ok] + ox] = True
    return rgb, idle, {'source': e['file'] + ' (frame 0 x %.2f)' % k, 'anchor_col': 192.0, 'scale': scale,
                       'heads': req.get('heads', 4), 'idle_x': [int(xs.min() + ox), int(xs.max() + ox)], 'stem': stem}


def run_through(row, col):
    """[x0, x1) of the run of True in a 1-D bool row that contains col (or the nearest True pixel)"""
    xs = np.flatnonzero(row)
    if len(xs) == 0:
        return None
    c = xs[np.argmin(np.abs(xs - col))]
    x0 = c
    while x0 - 1 >= 0 and row[x0 - 1]:
        x0 -= 1
    x1 = c
    while x1 + 1 < len(row) and row[x1 + 1]:
        x1 += 1
    return x0, x1 + 1


def measure(mask, anchor_col, heads=4):
    """silhouette measurements (see the module doc). mask: bool HxW in source px, floor row 870."""
    rows = mask.sum(1)
    ys = np.flatnonzero(rows)
    top_raw = int(ys.min())
    low = int(ys.max())
    top = int(next(y for y in ys if rows[y] >= MIN_TOP_W))
    H = FLOOR + 1 - top
    # head centre column: centroid of the top 10% rows
    band = mask[top:top + int(0.1 * H)]
    by, bx = np.nonzero(band)
    head_col = float(bx.mean())
    m = {'top_raw': top_raw, 'top': top, 'lowest': low, 'height': H, 'head_col': round(head_col, 1)}
    widths = {}
    for y in range(top, FLOOR + 1):
        r = run_through(mask[y], head_col)
        widths[y] = 0 if r is None else r[1] - r[0]
    # a hat brim (a band much wider than the rows 15 px above and below it): the hat is costume, not body ->
    # the head top is put 0.45 head under the brim (a brim sits about at the eyes)
    brim = None
    for y in range(top + 15, top + int(0.35 * H)):
        if widths[y] >= 1.5 * max(widths[y - 15], 1) and widths[y] >= 1.5 * max(widths[min(y + 15, FLOOR)], 1):
            if brim is None or widths[y] > widths[brim]:
                brim = y
    if brim is not None:
        m['hat_brim_y'] = brim
        top = int(round(brim - 0.45 * (FLOOR + 1 - brim) / (heads - 0.45)))
        H = FLOOR + 1 - top
        m.update({'top': top, 'height': H, 'top_method': 'hat brim at y=%d -> head top 0.45 head above it' % brim})
    else:
        m['top_method'] = 'first row >= %d px wide' % MIN_TOP_W
    y0, y1 = top + int(0.17 * H), top + int(0.36 * H)
    seg = [(widths[y], y) for y in range(y0, y1)]
    wmin, ny = min(seg)
    spec_head = H / heads
    if abs((ny - top) - spec_head) <= 0.15 * spec_head:
        m['head_method'] = 'neck = narrowest row under the head'
    else:
        m['head_method'] = f'height / {heads} heads (narrowest row gave {ny - top} px: helmet / hat / hood)'
        ny = top + int(round(spec_head))
    m['neck_y'] = ny
    head = ny - top
    m['head'] = head
    m['neck_w'] = widths[ny]
    # shoulder line = the biggest widening over 6 rows below the neck (arms and shoulders start)
    jumps = [(widths[min(y + 6, FLOOR)] - widths[y], y + 6) for y in range(ny - int(0.1 * head), ny + int(0.6 * head))]
    jmax, sy = max(jumps)
    if jmax >= 15:
        m['shoulder_method'] = 'biggest widening under the neck'
    else:
        sy, m['shoulder_method'] = ny + int(0.22 * head), 'neck + 0.22 head'
    m['shoulder_y'] = sy
    m['shoulder_h'] = FLOOR + 1 - sy
    # crotch: from the feet up, rows with two separate runs around the anchor column
    crotch = None
    for y in range(FLOOR - 30, top + int(0.3 * H), -1):
        xs = np.flatnonzero(mask[y])
        if len(xs) == 0:
            break
        gaps = np.diff(xs)
        big = gaps[gaps > 4]
        # a gap between the legs = a gap near the anchor column
        gx = xs[:-1][gaps > 4]
        if len(big) and np.any(np.abs(gx - anchor_col) < 0.25 * H):
            crotch = y
            continue
        break
    m['crotch_y'] = crotch
    ch = None if crotch is None else FLOOR + 1 - crotch
    if ch is not None and 0.33 * H <= ch <= 0.50 * H:
        m['hip_h'], m['hip_method'] = round(ch + 0.09 * H, 1), 'crotch + 0.09 height'
    else:
        m['hip_h'] = round(0.43 * H, 1)
        m['hip_method'] = ('0.43 height (leg gap closes at %s px: hem or no gap)' % ch) if ch else '0.43 height (no leg gap)'
    hip_y = FLOOR + 1 - m['hip_h']
    fr, bk = 0, 0
    for y in range(sy, int(hip_y)):
        xs = np.flatnonzero(mask[y])
        if len(xs):
            fr = max(fr, xs.max() + 1 - anchor_col)
            bk = max(bk, anchor_col - xs.min())
    m['reach_front'], m['reach_back'] = round(float(fr), 1), round(float(bk), 1)
    # limb bulk: lower-leg width = per leg the narrowest run between 25 and 65 px above the floor (the two runs
    # nearest the anchor column on each row; the foot itself sticks out lower down). Robes hide the legs -> None.
    legs = []
    for y in range(FLOOR - 65, FLOOR - 25):
        xs = np.flatnonzero(mask[y])
        if len(xs) == 0:
            continue
        segs = np.split(xs, np.flatnonzero(np.diff(xs) > 1) + 1)
        segs = [g for g in segs if len(g) >= 8]
        if len(segs) >= 2:
            segs.sort(key=lambda g: g[0])
            legs.append((len(segs[0]), len(segs[-1])))
    if len(legs) >= 10:
        a = np.array(legs)
        m['leg_w'] = round(float(np.median([a[:, 0].min(), a[:, 1].min()])), 1)
        m['leg_w_rows'] = len(legs)
    else:
        m['leg_w'] = None
    return m


def idle_pose(P):
    """the mannequin's measuring pose: wide idle stance like the battle sheets"""
    from motions import lock_feet
    return {'hip_h': (P['thigh'] + P['shin'] + P['ankle_h']) * 0.9, 'chest_yaw': 35.0, 'pelvis_pitch': 4,
            'shoulder_N': 12, 'elbow_N': 70, 'shoulder_F': 20, 'elbow_F': 80, 'head_pitch': 4,
            '_feet': {'N': (-80.0 * P['thigh'] / CANON['thigh'], -8.0), 'F': (110.0 * P['thigh'] / CANON['thigh'], 0.0)}}


def render_mask(P, pose, yaw=15.0):
    from motions import lock_feet
    from render import Camera, render
    cam = Camera(yaw=yaw)
    feet = pose.pop('_feet', None)
    if feet:
        pose, _ = lock_feet(P, pose, cam, feet)
    body = fk(P, pose)
    cam.fit(body)
    img, mask = render(body, P, cam, joints=False, ground=False, ghosts=False)
    return img, mask, body, cam, pose


def fit(sid, yaw=15.0, verbose=False):
    rgb, mask, info = idle_drawing(sid)
    m = measure(mask, info['anchor_col'], info['heads'])
    # the same numbers on the canonical mannequin in its idle stance
    _, cmask, cbody, ccam, _ = render_mask(CANON, idle_pose(CANON), yaw)
    cm = measure(cmask, 192.0, 4)
    k = m['height'] / cm['height']
    P = scaled(CANON, k)
    # head: measured head height vs the mannequin's (relative to the uniform scale)
    kh = (m['head'] / cm['head']) / k
    kh = float(np.clip(kh, 0.8, 1.25))
    P['head_r'] = [v * kh for v in P['head_r']]
    P['head_c'] *= kh
    # legs from the hip height (keep the ankle height), trunk from shoulder - hip
    leg_c = CANON['thigh'] + CANON['shin'] + CANON['ankle_h']
    hip_c = cm['hip_h']
    kl = (m['hip_h'] / hip_c) / k if not m['hip_method'].startswith('0.43') else 1.0
    kl = float(np.clip(kl, 0.85, 1.15))
    for key in ('thigh', 'shin'):
        P[key] *= kl
    # trunk length from the measured shoulder height - hip height (the mannequin's hip measured the same way)
    cm_hip = cm['hip_h'] if not m['hip_method'].startswith('0.43') else 0.43 * cm['height']
    kt = ((m['shoulder_h'] - m['hip_h']) / (cm['shoulder_h'] - cm_hip)) / k
    kt = float(np.clip(kt, 0.85, 1.2))
    P['spine'] *= kt
    P['chest'] *= kt
    # bulk: limb radii from the lower-leg width, the trunk follows half way
    kb = (m['leg_w'] / cm['leg_w']) / k if (m.get('leg_w') and cm.get('leg_w')) else 1.0
    kb = float(np.clip(kb, 0.85, 1.45))
    for key in ('r_thigh', 'r_shin', 'r_upper_arm', 'r_forearm', 'r_hand', 'r_foot', 'r_shoulder'):
        P[key] = [v * kb for v in P[key]] if isinstance(P[key], list) else P[key] * kb
    kbt = 1 + (kb - 1) * 0.5
    for key in ('pelvis_r', 'chest_r', 'r_spine'):
        P[key] = [v * kbt for v in P[key]] if isinstance(P[key], list) else P[key] * kbt
    P['shoulder_w'] *= kbt
    P['hip_w'] *= kbt
    # iterate once on the total height so that the fitted mannequin's idle has the measured height
    _, fmask, _, _, _ = render_mask(P, idle_pose(P), yaw)
    fm = measure(fmask, 192.0, 4)
    k2 = m['height'] / fm['height']
    P = scaled(P, k2)
    _, fmask, _, _, _ = render_mask(P, idle_pose(P), yaw)
    fm = measure(fmask, 192.0, 4)
    report = {'sheet': sid, 'source': info['source'], 'anchor_col': info['anchor_col'], 'measured': m,
              'canonical_measured': cm, 'fitted_measured': fm,
              'factors': {'height': round(k * k2, 4), 'head': round(kh, 4), 'legs': round(kl, 4), 'trunk': round(kt, 4), 'limb_bulk': round(kb, 4), 'trunk_bulk': round(kbt, 4)},
              'proportions': {kk: ([round(x, 2) for x in v] if isinstance(v, list) else round(v, 2)) for kk, v in P.items()}}
    return P, report, (rgb, mask, info)


def jsonable(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sheets', nargs='+')
    ap.add_argument('--yaw', type=float, default=15.0)
    a = ap.parse_args(argv)
    for sid in a.sheets:
        _, rep, _ = fit(sid, a.yaw)
        print(json.dumps(rep, ensure_ascii=False, indent=1, default=jsonable))


if __name__ == '__main__':
    main()
