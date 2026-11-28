#!/usr/bin/env python3
"""Body-consistency checks for a painted run set (gait/<sheet stem>_run_a.png + _b.png) against the sheet's idle drawing.

The owner refused five redrawn runs on 2026-11-28 that passed every pixel check (Magda: the upper body pumps sideways;
Grom: squashed face; Oswin: flattened face, figure sunk; Seraphine: head and chest wobble; Astel: the staff grows and
shrinks). These checks measure what the owner saw. Thresholds were set on the 15 accepted runs (blademaster, fixer,
hedgemage, huntress, ironwall, lancer, shadowqueen, tactician, veteran, archer, cleric, mage, rogue, warrior, kai).

Head-block tracker (H1-H3): the idle head (fit.measure head top .. neck row, the row runs through the head column,
columns clipped to head_col +- 0.9 head; other figure pixels weigh 0) is matched into each 384-px slot by weighted
RGB SSD (FFT) with independent x / y scale: coarse sx 0.60-1.25, sy 0.75-1.25 (step 0.05) in a window of the idle
head top -70..+60 rows, x -90..+120 around the idle head box (anchor moved to x=192), then +-0.05 in steps of 0.0125
within +-8 px. A frame whose error is more than HEAD_LOST x the median error is "head not found" (WARN, skipped).

  H1  phase-locked width pump: range over the 4 phase pairs (n, n+4) of mean(sx(n), sx(n+4))        FAIL > 0.09
      (a body stretched sideways in some phases and squeezed in others - Magda .138; accepted max .075)
  H2  same-phase mismatch: max |s(n) - s(n+4)| for sx or sy                                        FAIL > 0.15
      (the two half-cycles do not repeat: Seraphine sy .275; accepted max .112)
  H3  head squashed vs the idle: median sx / sy                                                    FAIL < 0.78 or > 1.25
      (Grom .66; accepted .86-1.13)
  V1  sunk figure: median (870 - head-band top) / (870 - idle head top)                            FAIL < 0.97
      (head-band top as tools/mannequin3d/delivery.py head_band_top; Oswin .944, Grom .965; accepted .982-1.099)
  SEAM a horizontal paste seam: a row whose count of strong row-to-row differences (|dRGB| > 120, figure on both rows)
      is > 2x the median of the rows +-40 around it, at the same row (+-3) in >= 6 of 8 frames, that does NOT follow the
      figure's bob (a belt or armour line moves with the body: its row minus the head row stays constant); rows
      within 60 px of the floor are not searched (hems / boots do not bob)                                    WARN
      (a plain "> 2x" rule fires on all 15 accepted runs - ratio 3.2-6.6 from belt / armour lines; the bob test keeps
      Magda y~678, row spread 2 px vs 7 px for row - head row)
  WEAPON rigid weapon length (pose.json weapon_px, staff / spear / mace: one straight haft). Per frame the painted
      shaft line is fitted (the straightest, most uniformly coloured figure line within +-10 deg / +-20 px of the table
      line in frame 1, then within +-5 deg of frame 1's line turned by the table's angle change). Frame 1's weapon
      (a +-10 px band along that line, butt .. tip) is cut in two at half the table fist -> tip length under its tip,
      turned to frame n's line, and each half is matched into frame n by translation (+-30 px). On a rigid weapon
      both halves move together; the difference of their shifts along the shaft = how much longer (+) or shorter (-)
      the weapon is than in frame 1 (Astel: 0 2 11 23 26 23 17 3). Staff / spear: FAIL when the range over the 8 frames
      is > WEAPON_FAIL px, WARN > WEAPON_WARN; mace: WARN only (no accepted mace run to set a FAIL on). Swords, daggers
      and bows rotate in the hand / are not a straight haft: not measured. Accepted: hedgemage 10.5, tactician 8.0,
      lancer 7.2 px; Astel 26.3.

Runtime: about 13-20 s per set on one core (the head tracker, numpy FFT with the region spectra computed once per
frame and pass; no scipy) - the prototype took ~35 s. The weapon and seam checks add ~2 s.

  python3 tools/art/gait_body.py sheet/hero/oswin STRIP_A.png STRIP_B.png [--pose POSE.json]
Prints one line per finding, ends with RESULT: PASS | WARN | FAIL (exit 1 on FAIL). Reads only.
"""
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
M3D = os.path.join(ROOT, 'tools', 'mannequin3d')

SLOT, FLOOR, HIP_X = 384, 870, 192
MAGENTA = np.array([255, 0, 255])

HEAD_LOST = 1.6
H1_FAIL = 0.09
H2_FAIL = 0.15
H3_LO, H3_HI = 0.78, 1.25
V1_FAIL = 0.97
SEAM_RATIO, SEAM_FRAMES, SEAM_ROW_TOL = 2.0, 6, 3
WEAPON_FAIL_KINDS = ('staff', 'spear')
WEAPON_WARN_KINDS = ('mace',)
WEAPON_FAIL, WEAPON_WARN = 18, 12
WEAPON_HALF, WEAPON_SEARCH = 10, 30

COARSE_SX = np.arange(0.60, 1.2501, 0.05)
COARSE_SY = np.arange(0.75, 1.2501, 0.05)


def _m3d():
    if M3D not in sys.path:
        sys.path.insert(0, M3D)
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import fit  # noqa: E402  (tools/mannequin3d/fit.py: idle_drawing, measure, run_through)
    import delivery  # noqa: E402  (tools/mannequin3d/delivery.py: head_band_top, weapon_mask)
    return fit, delivery


def fg_mask(a):
    return np.abs(a[..., :3].astype(int) - MAGENTA).sum(-1) > 60


def load_frames(strips):
    out = []
    for s in strips:
        a = np.asarray(Image.open(s).convert('RGB'))
        out += [a[:, k * SLOT:(k + 1) * SLOT] for k in range(a.shape[1] // SLOT)]
    return out


def fit_override(sid):
    """tools/mannequin3d/specs/carry3d.json fit_override of the sheet (a measured head top for a weapon over the head)"""
    try:
        with open(os.path.join(M3D, 'specs', 'carry3d.json'), encoding='utf-8') as f:
            chars = json.load(f).get('chars') or {}
    except (OSError, ValueError):
        return {}
    for k, v in chars.items():
        if isinstance(v, dict) and (k == sid or k == sid.split('/')[-1] or v.get('sheet') == sid):
            return v.get('fit_override') or {}
    return {}


def idle_head(sid):
    """the idle head block (template, weights) and the idle measurements. The idle is found like add_gait / the 3D
    request do it (tools/mannequin3d/fit.idle_drawing): art/inbox/<sheet png stem>.png here, else on origin/art-inbox,
    else the registered sheet's frame 0 blown up."""
    fit, _ = _m3d()
    rgb, mask, info = fit.idle_drawing(sid)
    ov = fit_override(sid)
    mb = mask.copy()
    if ov.get('head_top_y'):
        mb[:int(ov['head_top_y'])] = False
    m = fit.measure(mb, info['anchor_col'], info['heads'], ov)
    top, ny, hc = m['top'], m['neck_y'], m['head_col']
    keep = np.zeros_like(mask)
    xs = []
    for y in range(top, ny + 1):
        r = fit.run_through(mask[y], hc)
        if r:
            keep[y, r[0]:r[1]] = True
            xs += [r[0], r[1]]
    hw = ny - top
    x0 = max(int(min(xs)), int(hc - 0.9 * hw))
    x1 = min(int(max(xs)), int(hc + 0.9 * hw))
    T = rgb[top:ny + 1, x0:x1].astype(float)
    W = np.ones(T.shape[:2])
    W[mask[top:ny + 1, x0:x1] & ~keep[top:ny + 1, x0:x1]] = 0
    return T, W, dict(top=top, neck=ny, x0=x0, x1=x1, anchor=info['anchor_col'], source=info.get('source'))


def _fast_len(n):
    """the smallest 2^a 3^b 5^c >= n (a quick FFT size)"""
    best = 1 << max(0, int(n - 1).bit_length())
    p5 = 1
    while p5 < 2 * n:
        p35 = p5
        while p35 < 2 * n:
            p2 = p35
            while p2 < n:
                p2 *= 2
            best = min(best, p2)
            p35 *= 3
        p5 *= 5
    return best


def best_fit(I, T, W, win, scales_x, scales_y):
    """min weighted SSD of the scaled template over top-left positions in win=(ya, yb, xa, xb) ->
    (err, sx, sy, top y, left x, h, w). SSD = sum W I^2 - 2 sum W T I + sum W T^2, the correlations by FFT on one
    padded region (its spectra computed once for every scale)."""
    ya, yb, xa, xb = win
    oy, ox = max(0, ya), max(0, xa)
    h0, w0 = T.shape[:2]
    sizes = [(max(4, round(h0 * sy)), max(4, round(w0 * sx)), sx, sy) for sy in scales_y for sx in scales_x]
    hmax, wmax = max(s[0] for s in sizes), max(s[1] for s in sizes)
    R = I[oy:yb + hmax, ox:xb + wmax]
    RH, RW = R.shape[:2]
    ny, nx = yb - oy + 1, xb - ox + 1          # top-left positions searched
    sh = (_fast_len(RH + hmax), _fast_len(RW + wmax))
    F2 = np.fft.rfft2((R * R).sum(-1), sh)
    Fc = [np.fft.rfft2(R[..., c], sh) for c in range(3)]
    T8 = Image.fromarray(T.astype(np.uint8))
    W8 = Image.fromarray((W * 255).astype(np.uint8))
    best = None
    for h, w, sx, sy in sizes:
        if RH < h or RW < w:
            continue
        Ts = np.asarray(T8.resize((w, h), Image.BILINEAR)).astype(float)
        Ws = np.asarray(W8.resize((w, h), Image.NEAREST)).astype(float) / 255
        ws = Ws.sum()
        if ws <= 0:
            continue
        # correlation = convolution with the flipped kernel; valid position (y, x) sits at index (y + h - 1, x + w - 1)
        spec = F2 * np.fft.rfft2(Ws[::-1, ::-1], sh)
        for c in range(3):
            spec = spec - 2 * Fc[c] * np.fft.rfft2((Ws * Ts[..., c])[::-1, ::-1], sh)
        full = np.fft.irfft2(spec, sh)
        sc = full[h - 1:h - 1 + min(ny, RH - h + 1), w - 1:w - 1 + min(nx, RW - w + 1)]
        sc = (sc + (Ws[..., None] * Ts ** 2).sum()) / ws
        iy, ix = np.unravel_index(np.argmin(sc), sc.shape)
        v = float(sc[iy, ix])
        if best is None or v < best[0]:
            best = (v, float(sx), float(sy), oy + int(iy), ox + int(ix), h, w)
    return best


def track_heads(frames, T, W, d):
    hx = d['x0'] - d['anchor'] + HIP_X
    out = []
    for a in frames:
        I = a.astype(float)
        b = best_fit(I, T, W, (d['top'] - 70, d['top'] + 60, int(hx - 90), int(hx + 120)), COARSE_SX, COARSE_SY)
        if b is None:
            out.append(None)
            continue
        _, sx, sy, ty, tx, _, _ = b
        f = best_fit(I, T, W, (ty - 8, ty + 8, tx - 8, tx + 8),
                     np.arange(sx - 0.05, sx + 0.051, 0.0125), np.arange(sy - 0.05, sy + 0.051, 0.0125))
        out.append(f or b)
    return out


def seam_peaks(frames, y_lo=350, y_hi=FLOOR - 60):
    """per frame the row with the largest ratio (strong row-to-row differences / median of the rows +-40) ->
    [(ratio, y)]. Rows from y_hi down are skipped: hems and boots stay on the floor while the body bobs, so a line there
    would never follow the head."""
    res = []
    for a in frames:
        s = a.astype(int)
        m = fg_mask(a)
        strong = (np.abs(s[1:] - s[:-1]).sum(-1) > 120) & m[1:] & m[:-1]
        cnt = strong.sum(1).astype(float)
        best = (0.0, None)
        for y in range(max(41, y_lo), min(len(cnt) - 41, y_hi)):
            if cnt[y] < 2:
                continue
            ref = np.median(np.r_[cnt[y - 40:y - 3], cnt[y + 4:y + 41]])
            r = cnt[y] / max(ref, 8.0)
            if r > best[0]:
                best = (float(r), y)
        res.append(best)
    return res


def check_seam(frames, head_y):
    peaks = seam_peaks(frames)
    ys = [y for r, y in peaks if y is not None and r > SEAM_RATIO]
    if len(ys) < SEAM_FRAMES:
        return None
    med = float(np.median(ys))
    idx = [i for i, (r, y) in enumerate(peaks) if y is not None and r > SEAM_RATIO and abs(y - med) <= SEAM_ROW_TOL]
    if len(idx) < SEAM_FRAMES:
        return None
    rows = np.array([peaks[i][1] for i in idx], float)
    hy = np.array([head_y[i] if head_y[i] is not None else np.nan for i in idx], float)
    ok = ~np.isnan(hy)
    fixed = float(np.ptp(rows[ok])) if ok.any() else float(np.ptp(rows))
    follow = float(np.ptp(rows[ok] - hy[ok])) if ok.sum() >= 2 else None
    detail = (f'row y {", ".join(str(int(peaks[i][1])) for i in idx)} in {len(idx)}/8 frames, ratio '
              f'{", ".join(f"{peaks[i][0]:.1f}" for i in idx)}')
    if follow is not None and follow < fixed:
        # it moves with the head: a belt / armour line, not a paste seam
        return ('OK', f'SEAM: strongest row-difference line at y~{med:.0f} follows the figure (row - head row spread '
                      f'{follow:.0f} px < row spread {fixed:.0f}): a belt or armour line ({detail})')
    return ('WARN', f'SEAM: a horizontal cut at y~{med:.0f} in {len(idx)}/8 frames that does not follow the figure\'s bob '
                    f'(row spread {fixed:.0f} px, row - head row spread {follow if follow is not None else float("nan"):.0f} px; '
                    f'{detail}) - upper and lower body pasted together as separate pieces? Join the drawing across it')


def shaft_axis(I, m, F, T, L, da_max=10.0, off_max=20, ga=None):
    """the painted shaft near the line from F toward angle ga (default: toward T): (angle, point on it nearest F, tip u)"""
    ga = math.atan2(T[1] - F[1], T[0] - F[0]) if ga is None else ga
    best = None
    for da in np.arange(-da_max, da_max + 0.01, 0.5):
        ang = ga + math.radians(da)
        d = np.array([math.cos(ang), math.sin(ang)])
        n = np.array([-d[1], d[0]])
        for off in range(-off_max, off_max + 1, 2):
            P = F + n * off
            us = np.arange(0.2 * L, 0.7 * L)
            pts = P[None] + us[:, None] * d[None]
            xi = np.clip(np.round(pts[:, 0]).astype(int), 0, I.shape[1] - 1)
            yi = np.clip(np.round(pts[:, 1]).astype(int), 0, I.shape[0] - 1)
            col, fg = I[yi, xi], m[yi, xi]
            sc = fg.mean() - np.abs(col - np.median(col, 0)).sum(1).mean() / 300
            if best is None or sc > best[0]:
                best = (sc, ang, P)
    _, ang, P = best
    d = np.array([math.cos(ang), math.sin(ang)])
    u, miss, tip = 0.3 * L, 0, 0.3 * L
    while u < 2 * L and miss < 6:
        x, y = int(round(P[0] + d[0] * u)), int(round(P[1] + d[1] * u))
        if 0 <= x < I.shape[1] and 0 <= y < I.shape[0] and m[max(0, y - 2):y + 3, max(0, x - 2):x + 3].any():
            tip, miss = u, 0
        else:
            miss += 1
        u += 1
    return ang, P, tip


def _band(shape, P, d, half, u_lo, u_hi):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    vx, vy = xx - P[0], yy - P[1]
    u = vx * d[0] + vy * d[1]
    return (u >= u_lo) & (u < u_hi) & (np.abs(vx * d[1] - vy * d[0]) < half)


def weapon_stretch(pose, frames):
    """rigid-weapon check (module doc, WEAPON) -> (kind, [stretch px per frame, frame 1 = 0]) or (kind, None)"""
    light = pose.get('gait') == 'run'
    w0 = pose['frames'][0].get('weapon_px')
    kind = (w0 or {}).get('kind')
    if kind not in WEAPON_FAIL_KINDS + WEAPON_WARN_KINDS:
        return kind, None
    axes = []
    for k, (fr, a) in enumerate(zip(pose['frames'], frames)):
        w = fr.get('weapon_px')
        if not w:
            return kind, None
        o = (fr['slot'] - 1) * SLOT if light else 0
        F = np.array([w['fist'][0] - o, w['fist'][1]], float)
        T = np.array([w['tip'][0] - o, w['tip'][1]], float)
        L = float(np.linalg.norm(T - F))
        g = math.atan2(T[1] - F[1], T[0] - F[0])
        I, m = a.astype(int), fg_mask(a)
        if k == 0:
            g0 = g
            axes.append(shaft_axis(I, m, F, T, L) + (L, float(w.get('fist_butt_px') or 0.0)))
        else:
            axes.append(shaft_axis(I, m, F, T, L, da_max=5.0, ga=axes[0][0] + (g - g0)) + (L, 0.0))
    a1, P1, tip1, L, fb = axes[0]
    split = tip1 - 0.5 * L
    out = []
    for i, a in enumerate(frames):
        ai, Pi = axes[i][0], axes[i][1]
        di = np.array([math.cos(ai), math.sin(ai)])
        R = np.asarray(Image.fromarray(frames[0]).rotate(math.degrees(a1 - ai), resample=Image.NEAREST,
                                                         center=(float(P1[0]), float(P1[1])), fillcolor=(255, 0, 255))).astype(float)
        shift = {}
        for part, (lo, hi) in (('up', (split, tip1 + 12)), ('low', (-fb - 20, split))):
            Wm = _band(R.shape[:2], P1, di, WEAPON_HALF, lo, hi)
            ys, xs = np.nonzero(Wm)
            if not ys.size:
                return kind, None
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            py, px = int(round(y0 + Pi[1] - P1[1])), int(round(x0 + Pi[0] - P1[0]))
            b = best_fit(a.astype(float), R[y0:y1, x0:x1], Wm[y0:y1, x0:x1].astype(float),
                         (py - WEAPON_SEARCH, py + WEAPON_SEARCH, px - WEAPON_SEARCH, px + WEAPON_SEARCH), [1.0], [1.0])
            if b is None:
                return kind, None
            shift[part] = np.array([b[4] - px, b[3] - py], float)
        out.append(round(float((shift['up'] - shift['low']) @ di), 1))
    return kind, out


def check_set(sid, strips, pose=None, log=None):
    """-> [(level, message)] with level OK / WARN / FAIL. strips: [run_a.png, run_b.png]; pose: the request pose.json
    the set was painted over (receive.gait_pose), for the head band (V1) and the weapon line."""
    t0 = time.time()
    _, delivery = _m3d()
    frames = load_frames(strips)
    out = []
    if len(frames) != 8:
        return [('FAIL', f'{len(frames)} slots in the strips, a run set has 8')]
    try:
        T, W, d = idle_head(sid)
    except Exception as e:  # noqa: BLE001
        return [('WARN', f'idle drawing of {sid} could not be read ({e}): H1-H3 / V1 not checked')]
    out.append(('OK', f'idle {d["source"]}: head top y {d["top"]}, neck y {d["neck"]}, head block {d["x1"] - d["x0"]} px wide'))
    heads = track_heads(frames, T, W, d)
    err = np.array([h[0] if h else np.inf for h in heads], float)
    med = float(np.median(err[np.isfinite(err)])) if np.isfinite(err).any() else np.inf
    ok = np.isfinite(err) & (err <= HEAD_LOST * med)
    for i in np.flatnonzero(~ok):
        out.append(('WARN', f'F{i + 1}: idle head not found (match error {err[i] / med:.2f} x the median > {HEAD_LOST}): '
                            'skipped by H1-H3'))
    sx = np.array([h[1] if h else np.nan for h in heads])
    sy = np.array([h[2] if h else np.nan for h in heads])
    hy = [h[3] if h else None for h in heads]
    out.append(('OK', 'head block per frame (sx/sy/top y): ' + ' '.join(
        f'F{i + 1}:{sx[i]:.2f}/{sy[i]:.2f}/{hy[i]}' + ('' if ok[i] else '?') for i in range(8))))
    pairs = [i for i in range(4) if ok[i] and ok[i + 4]]
    if pairs:
        pm = [(sx[i] + sx[i + 4]) / 2 for i in pairs]
        h1 = max(pm) - min(pm)
        msg = (f'H1 width pump: phase-pair mean head sx {" ".join(f"{v:.3f}" for v in pm)} -> range {h1:.3f} (FAIL > {H1_FAIL})')
        out.append(('FAIL', msg + ' - the body is stretched sideways in some phases and squeezed in others: move it as one '
                                  'block (100% width)') if h1 > H1_FAIL else ('OK', msg))
        dx = [abs(sx[i] - sx[i + 4]) for i in pairs]
        dy = [abs(sy[i] - sy[i + 4]) for i in pairs]
        h2 = max(max(dx), max(dy))
        msg = (f'H2 same-phase mismatch: |s(n) - s(n+4)| sx {" ".join(f"{v:.3f}" for v in dx)}, '
               f'sy {" ".join(f"{v:.3f}" for v in dy)} -> max {h2:.3f} (FAIL > {H2_FAIL})')
        out.append(('FAIL', msg + ' - the two half-cycles do not repeat (head / upper body wobble): frame n and n+4 are the '
                                  'same phase') if h2 > H2_FAIL else ('OK', msg))
    else:
        out.append(('WARN', 'H1 / H2: no phase pair with the head found in both frames - not checked'))
    if ok.any():
        h3 = float(np.median((sx / sy)[ok]))
        msg = f'H3 head aspect vs the idle: median sx/sy {h3:.2f} (FAIL < {H3_LO} or > {H3_HI})'
        out.append(('FAIL', msg + (' - the head is squashed (narrower than the idle head for its height)' if h3 < H3_LO else
                                   ' - the head is stretched sideways')) if not H3_LO <= h3 <= H3_HI else ('OK', msg))
    if pose and len(pose.get('frames', [])) == 8:
        light = pose.get('gait') == 'run'
        tops = [delivery.head_band_top(fg_mask(a), fr, light) for fr, a in zip(pose['frames'], frames)]
        r = [(FLOOR - t) / (FLOOR - d['top']) for t in tops if t is not None]
        if r:
            v1 = float(np.median(r))
            msg = (f'V1 figure height vs the idle: (870 - head-band top) / (870 - idle top {d["top"]}) = {v1:.3f} median '
                   f'(head-band top {" ".join(str(t) for t in tops)}; FAIL < {V1_FAIL})')
            out.append(('FAIL', msg + ' - the figure is drawn shorter than the idle (sunk / slumped upper body, head pushed '
                                      'into the collar)') if v1 < V1_FAIL else ('OK', msg))
        kind, st = weapon_stretch(pose, frames)
        if st:
            rng = max(st) - min(st)
            msg = (f'WEAPON ({kind}) rigid length: painted weapon longer (+) / shorter (-) than in frame 1, per frame '
                   f'{" ".join(f"{v:+.0f}" for v in st)} px -> range {rng:.1f} px (WARN > {WEAPON_WARN}'
                   + (f', FAIL > {WEAPON_FAIL})' if kind in WEAPON_FAIL_KINDS else ', mace: WARN only)'))
            hint = (' - the weapon is not one rigid piece: the shaft was stretched / shortened (or the hand left behind '
                    'while the tip follows the guide). Cut the idle weapon out once and only move / turn it')
            if rng > WEAPON_FAIL and kind in WEAPON_FAIL_KINDS:
                out.append(('FAIL', msg + hint))
            elif rng > WEAPON_WARN:
                out.append(('WARN', msg + hint))
            else:
                out.append(('OK', msg))
    s = check_seam(frames, hy)
    if s:
        out.append(s)
    out.append(('OK', f'gait_body checks took {time.time() - t0:.0f} s'))
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    pose = None
    if '--pose' in argv:
        k = argv.index('--pose')
        with open(argv[k + 1], encoding='utf-8') as f:
            pose = json.load(f)
        argv = argv[:k] + argv[k + 2:]
    if len(argv) != 3:
        print(__doc__)
        return 2
    res = check_set(argv[0], argv[1:], pose)
    for lv, msg in res:
        print(f'  [{lv}] {msg}')
    worst = 'FAIL' if any(lv == 'FAIL' for lv, _ in res) else ('WARN' if any(lv == 'WARN' for lv, _ in res) else 'PASS')
    print(f'RESULT: {worst} ({argv[0]})')
    return 1 if worst == 'FAIL' else 0


if __name__ == '__main__':
    sys.exit(main())
