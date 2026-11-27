"""Report images for the owner and reviewers (no guide is made here): contact sheet (idle vs fitted mannequin),
the warrior's comparison with its already-drawn run (compare_run.png / .json) and the table vs run_base v2.
Used by build.py after the guides are rendered."""
import io
import json
import math
import os
import subprocess
import textwrap

import numpy as np
from PIL import Image, ImageDraw

from common import REPO, CELL, ANCHOR, font, keyed
from render import SLOT_W, SLOT_H, FLOOR, HIP_X, MAGENTA


# ---------------------------------------------------------------- contact sheet
def contact_sheet(name, rgb_src, mask_src, info, P, cam, rep, path, idle_frame):
    """accepted idle | mannequin idle | overlay, same scale: soles y=870, anchor column on x=192"""
    ac = info['anchor_col']
    dx = int(round(HIP_X - ac))
    idle = np.full((SLOT_H, SLOT_W, 3), 255, np.uint8)
    idle[:] = MAGENTA
    ys, xs = np.nonzero(mask_src)
    ok = (xs + dx >= 0) & (xs + dx < SLOT_W)
    idle[ys[ok], xs[ok] + dx] = rgb_src[ys[ok], xs[ok]]
    imask = np.zeros((SLOT_H, SLOT_W), bool)
    imask[ys[ok], xs[ok] + dx] = True
    man_img, man_mask = idle_frame      # (image, mask) of the fitted mannequin in the idle stance with its props
    # overlay: idle faint + mannequin silhouette outline (cyan)
    ov = (idle.astype(float) * 0.45 + 255 * 0.55).astype(np.uint8)
    ov[~imask] = MAGENTA
    m = man_mask
    edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
    edge = edge | np.roll(edge, 1, 0) | np.roll(edge, 1, 1)
    ov[edge] = (0, 200, 255)
    y0, y1 = 360, 905
    W = SLOT_W * 3 + 40
    sheet = Image.new('RGB', (W, (y1 - y0) + 190), (30, 30, 36))
    d = ImageDraw.Draw(sheet)
    fs = font(13)
    for i, (im, lab) in enumerate(((Image.fromarray(idle), 'accepted idle (art/inbox, source px)'),
                                   (man_img, '3D mannequin, fitted, idle stance + props'),
                                   (Image.fromarray(ov), 'overlay: idle faint + mannequin outline'))):
        x = 10 + i * (SLOT_W + 10)
        sheet.paste(im.crop((0, y0, SLOT_W, y1)), (x, 30))
        d.text((x, 8), lab, font=fs, fill=(230, 230, 230))
        d.line([(x, 30 + FLOOR - y0), (x + SLOT_W, 30 + FLOOR - y0)], fill=(255, 255, 255))
        d.line([(x + HIP_X, 30), (x + HIP_X, 30 + y1 - y0)], fill=(200, 200, 200))
    m = rep['measured']
    fm = rep['fitted_measured']
    lines = [f"{rep['sheet']}  - source {rep['source']}  - anchor column {info['anchor_col']} -> x=192, soles y=870, 1:1 source px",
             f"drawing : height {m['height']} ({m['top_method']}), head {m['head']} ({m['head_method']}), shoulder {m['shoulder_h']}, "
             f"hip {m['hip_h']} ({m['hip_method']}), lower leg {m.get('leg_w')} px, reach front/back {m['reach_front']}/{m['reach_back']}",
             f"fitted  : height {fm['height']}, head {fm['head']}, shoulder {fm['shoulder_h']}, hip {fm['hip_h']}, lower leg {fm.get('leg_w')}",
             'factors : ' + ', '.join(f'{k} {v}' for k, v in rep['factors'].items())]
    wrapped = [w for t in lines for w in textwrap.wrap(t, 150, subsequent_indent='          ')]
    for i, t in enumerate(wrapped):
        d.text((10, 30 + (y1 - y0) + 10 + i * 20), t, font=fs, fill=(230, 230, 230))
    sheet.save(path)


# ---------------------------------------------------------------- comparison (warrior)
def sheet_run_cells(sid):
    man = json.load(open(os.path.join(REPO, 'assets/art/manifest.json'), encoding='utf-8'))
    e = man[sid]
    meta = e['sheet']
    g = Image.open(os.path.join(REPO, e['file'])).convert('RGBA')
    a = meta['anims']['run']
    cells = []
    for i in range(a['from'], a['to'] + 1):
        x, y = meta['frames'][i]
        cells.append(g.crop((x, y, x + CELL, y + CELL)))
    return cells


def cell_to_slot(cell, scale=0.1654):
    """inverse of game_cell: blow a 96x96 cell up to the add_gait window (nearest) and place it on a 384x1024 slot"""
    S = int(round(CELL / scale))
    ox = S // 2
    oy = int(math.floor(ANCHOR[1] * S / CELL + 0.5))
    big = cell.resize((S, S), Image.Resampling.NEAREST)
    slot = Image.new('RGBA', (SLOT_W, SLOT_H), (0, 0, 0, 0))
    slot.paste(big, (HIP_X - ox, FLOOR + 1 - oy), big)
    return slot


def inbox_run_strips(stem):
    out = []
    for h in 'ab':
        rel = f'art/inbox/gait/{stem}_run_{h}.png'
        p = os.path.join(REPO, rel)
        if os.path.exists(p):
            out.append(Image.open(p).convert('RGB'))
            continue
        r = subprocess.run(['git', '-C', REPO, 'show', f'origin/art-inbox:{rel}'], capture_output=True)
        if r.returncode != 0:
            return None
        out.append(Image.open(io.BytesIO(r.stdout)).convert('RGB'))
    return out


def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 0.0


def compare_run(man_slots, man_masks, sid, stem, path, json_path):
    cells = sheet_run_cells(sid)
    reg = [cell_to_slot(c) for c in cells]
    big = inbox_run_strips(stem)
    inbox = []
    if big:
        for k in range(8):
            s = big[k // 4].crop(((k % 4) * SLOT_W, 0, (k % 4 + 1) * SLOT_W, SLOT_H))
            inbox.append(keyed(s))
    y0, y1 = 400, 900
    sets = [('registered', 'registered sheet run cells 7-14 (96x96 game px) blown up x6.04 (nearest) to guide scale', reg)]
    if inbox:
        sets.append(('inbox', 'art-inbox originals sheet_class_warrior_run_a/b.png (the drawn source, guide scale)', inbox))
    k_sc = 0.75
    pw, ph = int(SLOT_W * k_sc), int((y1 - y0) * k_sc)
    W = 8 * pw + 20
    rows = []
    for key, lab, drawn in sets:
        rows.append((key, 'blend', lab + ': drawn at 40% over the 3D mannequin', drawn))
        rows.append((key, 'outline', lab + ': drawn silhouette as a yellow outline over the 3D mannequin', drawn))
    sheet = Image.new('RGB', (W, 44 + len(rows) * (ph + 44)), (30, 30, 36))
    d = ImageDraw.Draw(sheet)
    d.text((10, 10), 'warrior light run R1-R8: 3D mannequin (fitted, with its sword low and the shield in front) vs the '
           'already-drawn frames - same hip column x=192, same floor y=870, no shifting', font=font(16, True), fill=(240, 240, 240))
    stats = []
    for r, (key, mode, lab, drawn) in enumerate(rows):
        ytop = 44 + r * (ph + 44)
        d.text((10, ytop), lab, font=font(13), fill=(220, 220, 220))
        for k in range(8):
            base = np.asarray(man_slots[k].convert('RGB')).astype(float)
            dr = drawn[k]
            da = np.asarray(dr)[..., 3] > 0
            comp = base.copy()
            if mode == 'blend':
                dc = np.asarray(dr.convert('RGB')).astype(float)
                comp[da] = comp[da] * 0.6 + dc[da] * 0.4
            else:
                e = da & ~(np.roll(da, 1, 0) & np.roll(da, -1, 0) & np.roll(da, 1, 1) & np.roll(da, -1, 1))
                e = e | np.roll(e, 1, 0) | np.roll(e, 1, 1) | np.roll(e, -1, 0)
                comp[e] = (255, 230, 0)
            im = Image.fromarray(comp.astype(np.uint8)).crop((0, y0, SLOT_W, y1)).resize((pw, ph), Image.Resampling.LANCZOS)
            x = 10 + k * pw
            sheet.paste(im, (x, ytop + 18))
            mm = man_masks[k]
            if mode == 'blend':
                st = {'frame': f'R{k + 1}', 'row': key, 'iou_body': round(iou(mm, da), 3)}
                dys = np.flatnonzero(da.any(1))
                mys = np.flatnonzero(mm.any(1))
                st.update({'drawn_top': int(dys.min()), 'mannequin_top': int(mys.min()), 'drawn_lowest': int(dys.max()),
                           'mannequin_lowest': int(mys.max())})
                stats.append(st)
            st = next(s_ for s_ in stats if s_['row'] == key and s_['frame'] == f'R{k + 1}')
            d.text((x + 4, ytop + 18 + ph + 2), f"R{k + 1}  silhouette IoU {st['iou_body']:.2f}", font=font(12), fill=(230, 230, 160))
    sheet.save(path)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=1)
    return stats




def vs_v2(r, log):  # noqa: E302
    """foot / hip / neck positions of the warrior's 3D run vs the accepted 2D mannequin run_base v2 (screen px)"""
    v2 = json.load(open(os.path.join(REPO, 'art/requests/guides/run_base/v2/pose.json'), encoding='utf-8'))
    lines = []
    for a, b in zip(v2['frames'], r['recs']):
        ja, jb = a['joints'], b['joints']
        def rel(j, k):
            return (j[k][0] - j['hip'][0], FLOOR - j[k][1])
        d = {}
        for k in ('ankN', 'ankF', 'neck0', 'handN', 'handF'):
            pa, pb = rel(ja, k), rel(jb, k)
            d[k] = (round(pb[0] - pa[0]), round(pb[1] - pa[1]))
        lines.append(f"{a['frame']}: hip h v2 {FLOOR - ja['hip'][1]:.0f} / 3D {FLOOR - jb['hip'][1]:.0f}; toe x v2 {a.get('toe_x_px')} / 3D {b.get('toe_x_px')}; "
                     + ', '.join(f'{k} d({v[0]:+d},{v[1]:+d})' for k, v in d.items()))
    with open(os.path.join(r['dir'], 'vs_run_base_v2.txt'), 'w', encoding='utf-8') as f:
        f.write('3D warrior run vs art/requests/guides/run_base/v2/pose.json (screen px; d(x,y) = 3D minus v2, x relative to the hip column, y up)\n')
        f.write('\n'.join(lines) + '\n')
    log('warrior vs run_base v2 written: vs_run_base_v2.txt')


