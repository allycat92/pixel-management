"""Render 3D-mannequin guides for real characters (prototype of the owner's approach 1, 2026-11-28).

  python3 tools/mannequin3d/build.py --out DIR [--chars warrior ironwall mage] [--yaw 15] [--chest-open 30]

For each character: fit the mannequin to the accepted idle (fit.py), run its movement class (motions.py) with the
character's weapon carry (props + arm overrides / two-hand grip), and write into DIR/<char>/:
  <set>_a.png, <set>_b.png       guide strips, same canvas as art/requests/guides/*: 1536x1024, 4 slots of 384,
                                 hip column x=192 per slot, standing soles on y=870, #FF00FF, ground line y=871,
                                 SPEC.md joint dots (near bright / far dark), props + robe see-through (teal outline)
  <set>_plain_a/b.png            the same without joint dots and ground line
  pose.json                      2D joints per frame in the run_base/heavy_base/robe_base pose.json schema
  <set>_game_x1.gif / _x4.gif    the cycle at game size (96x96 cell, the add_gait window, 0.1654) and x4 nearest
  <set>_guide.gif                the cycle at guide size (crop y 380..900)
  <set>_smooth.gif               24 in-between frames of the same cycle (shows the spline interpolation), half size
  contact.png                    accepted idle | mannequin idle | overlay, same scale (soles 870, anchor column 192)
warrior also: attack_a.png (windup, 2 in-betweens, strike), attack_ready.png, hit_a.png (impact, recover),
  attack/hit GIFs, and compare_run.png (drawn run frames at 40% over the 3D frames: registered sheet cells 7-14 blown
  up to guide scale, and the large art-inbox originals), compare_run.json (silhouette IoU / extents per frame).
Never writes into assets/ or art/.
"""
import argparse
import io
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import fit as fitmod  # noqa: E402
from motions import GAITS, gait_frames, action_frames, warrior_attack, warrior_hit, lock_feet  # noqa: E402
from render import Camera, render, project_joints, SLOT_W, SLOT_H, FLOOR, HIP_X, MAGENTA  # noqa: E402
from rig import fk, full_pose  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCALE = 0.1654
CELL, ANCHOR = 96, (48, 92)
PREVIEW_BG = (58, 70, 60)
ACTION_SHIFT = 24

JOINTS_OUT = ['hip', 'HN', 'HF', 'kneeN', 'kneeF', 'ankN', 'ankF', 'heelN', 'heelF', 'toetipN', 'toetipF',
              'SN', 'SF', 'elbN', 'elbF', 'wriN', 'wriF', 'handN', 'handF', 'neck0', 'head', 'headtop', 'nose']

# ---------------------------------------------------------------- characters
def _warrior_sword_arm(sh, el):
    return sh * 0.55 - 4.0, 42.0          # sword hand low at the belt/hip, swinging less (README: forearm drops)


def _shield_arm(sh, el):
    return 36.0 + sh * 0.1, 118.0         # shield arm: forearm across the front of the chest, barely swinging


CHARS = {
    'warrior': {
        'sheet': 'sheet/class/warrior', 'gait': 'run_light',
        'arm_N': _warrior_sword_arm, 'arm_F': _shield_arm,
        'props': [{'hand': 'N', 'kind': 'sword', 'abs_angle': -138.0, 'length': 118.0},
                  {'hand': 'F', 'kind': 'shield', 'radius': 54.0}],
        'actions': True,
    },
    'ironwall': {
        'sheet': 'sheet/captain/ironwall', 'gait': 'run_heavy',
        'arm_N': lambda sh, el: (sh * 0.8 + 6.0, 78.0), 'arm_F': lambda sh, el: (34.0, 96.0),
        'props': [{'hand': 'N', 'kind': 'mace', 'abs_angle': 44.0, 'length': 118.0},
                  {'hand': 'F', 'kind': 'shield', 'radius': 47.0, 'height': 125.0}],
    },
    'mage': {
        'sheet': 'sheet/class/mage', 'gait': 'run_robe',
        # two-hand staff grip in the chest frame from the neck base (lower hand N at the belt, upper hand F at the chest)
        'grip': {'N': (40.0, -92.0, 18.0), 'F': (50.0, -40.0, -10.0), 'swing': 8.0},
        'props': [{'kind': 'staff', 'between': ('N', 'F'), 'length': 225.0, 'back': 70.0}],
        'robe': True,
    },
}


def font(sz, bold=False):
    try:
        return ImageFont.truetype(FONTB if bold else FONT, sz)
    except OSError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- rendering helpers
def render_frame(P, pose, cam, props, robe_spec=None, **kw):
    body = fk(P, pose, props=props, robe=robe_spec)
    cam.fit(body)
    img, mask = render(body, P, cam, **kw)
    return body, img, mask


def keyed(img):
    """RGBA with the magenta background (and nothing else) transparent"""
    a = np.asarray(img.convert('RGB')).astype(int)
    alpha = (np.abs(a - np.array(MAGENTA)).sum(-1) > 0).astype(np.uint8) * 255
    return Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), 'RGBA')


def game_cell(img_slot):
    """the add_gait window (hip column x=192 -> anchor x 48, floor bottom edge 871 -> anchor y 92) shrunk to 96x96"""
    S, ox = 580, 290
    oy = int(math.floor(ANCHOR[1] * S / CELL + 0.5))
    x0, y0 = HIP_X - ox, FLOOR + 1 - oy
    rgba = np.asarray(keyed(img_slot)).astype(float)
    win = np.zeros((S, S, 4))
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(SLOT_W, x0 + S), min(SLOT_H, y0 + S)
    win[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = rgba[sy0:sy1, sx0:sx1]
    a = win[..., 3:] / 255.0
    pm = win[..., :3] * a

    def box(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), 'F').resize((CELL, CELL), Image.Resampling.BOX))
    A = box(a[..., 0])
    rgb = np.stack([box(pm[..., i]) for i in range(3)], -1) / np.maximum(A[..., None], 1e-6)
    out = np.zeros((CELL, CELL, 4), np.uint8)
    on = A >= 0.45
    out[on, :3] = np.clip(rgb[on], 0, 255).astype(np.uint8)
    out[on, 3] = 255
    return Image.fromarray(out, 'RGBA')


def on_bg(rgba, bg=PREVIEW_BG, floor_y=None):
    im = Image.new('RGB', rgba.size, bg)
    if floor_y is not None:
        ImageDraw.Draw(im).line([(0, floor_y), (rgba.size[0], floor_y)], fill=(90, 104, 92))
    im.paste(rgba, (0, 0), rgba)
    return im


def save_gif(frames, path, ms):
    ms = ms if isinstance(ms, list) else [ms] * len(frames)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0, disposal=2, optimize=False)


def strip_of(slots, n=4):
    s = Image.new('RGB', (SLOT_W * n, SLOT_H), MAGENTA)
    for i, im in enumerate(slots):
        s.paste(im, (i * SLOT_W, 0))
    return s


# ---------------------------------------------------------------- pose.json
def frame_record(body, cam, mask, spec, meta, P, slot_origin):
    J = project_joints(body, cam, JOINTS_OUT)
    ox = slot_origin
    joints = {k: [round(v[0] + ox, 1), v[1]] for k, v in J.items()}
    hip = J['hip']
    rows = np.flatnonzero(mask.any(1))
    rec = {'frame': meta['frame'], 'strip': meta['strip'], 'slot': meta['slot'], 'phase': meta['phase']}
    st = meta['stance']
    rec['feet_down'] = ['near' if s == 'N' else 'far' for s in st]
    if len(st) == 2:      # double support: the leading (just landed) foot
        rec['stance'] = 'near' if meta['strip'] == 'a' else 'far'
    else:
        rec['stance'] = None if not st else ('near' if st[0] == 'N' else 'far')
    rec['hip_height_px'] = round(FLOOR - hip[1], 1)
    rec['top_px'] = int(rows.min())
    rec['lowest_px'] = int(rows.max())
    sole = {}
    for s in 'NF':
        sole[s] = int(round(FLOOR - body.joints['sole' + s][1]))
    rec['sole_px'] = sole
    tips = {s: round(J['toetip' + s][0] - hip[0], 1) for s in 'NF'}
    if spec['gait'] == 'run':
        rec['toe_x_px'] = tips[st[0]] if st else None
    else:
        lead = rec['stance'][0].upper() if rec['stance'] else None
        rec['toe_x_px'] = {'stance': tips[lead] if lead else None,
                           'rear': (tips['F' if lead == 'N' else 'N'] if len(st) == 2 else None)}
    q = full_pose(meta['pose'])
    rec['knee_flex_deg'] = {s: round(q['knee_' + s], 1) for s in 'NF'}
    rec['elbow_flex_deg'] = {s: round(q['elbow_' + s], 1) for s in 'NF'}
    nk = J['neck0']
    rec['lean_deg'] = round(math.degrees(math.atan2(nk[0] - hip[0], hip[1] - nk[1])), 1)
    rec['neck_x_px'] = round(nk[0] - hip[0], 1)
    rec['ik_reached'] = bool(meta['reached'])
    if meta.get('hip_lowered'):
        rec['hip_lowered_px'] = meta['hip_lowered']
    rec['angles_deg'] = {k: round(v, 2) for k, v in q.items() if k not in ('x',)}
    rec['joints'] = joints
    return rec


def gait_pose_json(name, P, cam, char, recs, rep):
    spec = GAITS[name]
    hips = [r['joints']['hip'][1] for r in recs]
    leans = [r['lean_deg'] for r in recs]
    head_px = round(2 * P['head_r'][1], 1)
    out = {
        'set': spec['set'], 'gait': spec['gait'], 'movement_class': spec['class'], 'head_px': head_px, 'baseline': FLOOR,
        'scale': SCALE, 'frames_per_cycle': 8, 'nominal_ms': spec['ms'], 'step_px': spec['step_px'],
        'run_stride_game_px': round(spec['step_px'] * SCALE, 1),
        'speed_at_nominal_ms_game_px_s': round(spec['step_px'] / 4 * SCALE / (spec['ms'] / 1000.0), 1),
        'bob_px': round(max(hips) - min(hips), 1), 'lean_deg': [min(leans), max(leans)],
        'bones_px': {'thigh': round(P['thigh'], 2), 'shin': round(P['shin'], 2), 'upper_arm': round(P['upper_arm'], 2),
                     'forearm_hand': round(P['forearm'] + P['hand'], 2)},
        'source': '3D mannequin prototype tools/mannequin3d (build.py) - NOT an accepted guide',
        'character': rep['sheet'], 'camera': {'yaw_deg': cam.yaw, 'chest_open_deg': char.get('chest_open', 30.0)},
        'joint_x': 'strip-wide x (slot offset added) like run_base' if spec['gait'] == 'run' else 'x inside each 384-px slot like heavy_base/robe_base',
        'hip_height_px': 'FLOOR 870 - hip joint y',
        'proportions': rep['proportions'], 'fit_factors': rep['factors'],
        'frames': recs,
    }
    if spec['gait'] != 'run':
        planted = []
        for leg, start in (('near', 0), ('far', 4)):
            xs = []
            for k in range(5):
                r = recs[(start + k) % 8]
                t = r['toe_x_px']
                xs.append(t['stance'] if k < 4 or t['rear'] is None else t['rear'])
            planted.append({'leg': leg, 'toe_x_px': xs, 'retreat_px': [round(xs[i] - xs[i + 1], 1) for i in range(4)]})
        out['planted_toes'] = planted
    return out


# ---------------------------------------------------------------- contact sheet
def contact_sheet(name, rgb_src, mask_src, info, P, cam, char, rep, path):
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
    pose = fitmod.idle_pose(P)
    feet = pose.pop('_feet')
    pose, _ = lock_feet(P, pose, cam, feet)
    props = char.get('props_idle', [])
    body, man_img, man_mask = render_frame(P, pose, cam, props)
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
                                   (man_img, '3D mannequin, fitted, idle stance'),
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
    import textwrap
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


def cell_to_slot(cell):
    """inverse of game_cell: blow a 96x96 cell up to the 580x580 window (nearest) and place it on a 384x1024 slot"""
    S, ox = 580, 290
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


# ---------------------------------------------------------------- per character
def build_char(key, out, yaw, chest_open, log):
    char = dict(CHARS[key])
    char.setdefault('chest_open', chest_open)
    sid = char['sheet']
    P, rep, (rgb, mask, info) = fitmod.fit(sid, yaw)
    od = os.path.join(out, key)
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, 'fit.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1, ensure_ascii=False, default=fitmod.jsonable)
    cam = Camera(yaw=yaw)
    name = char['gait']
    spec = GAITS[name]
    robe_spec = spec.get('robe') if char.get('robe') else None
    props = char.get('props', [])
    frames = gait_frames(name, P, cam, char, n=8)
    slots, plain, masks, recs, cells = [], [], [], [], []
    for i, (pose, meta) in enumerate(frames):
        meta['pose'] = pose
        rs = dict(robe_spec, lag=robe_spec['lag'] * math.cos(2 * math.pi * (meta['phi'] - 0.125))) if robe_spec else None
        body, img, m = render_frame(P, pose, cam, props, rs)
        _, img_p, _ = render_frame(P, pose, cam, props, rs, joints=False, ground=False)
        slots.append(img)
        plain.append(img_p)
        masks.append(m)
        origin = (meta['slot'] - 1) * SLOT_W if spec['gait'] == 'run' else 0
        recs.append(frame_record(body, cam, m, spec, meta, P, origin))
        cells.append(game_cell(img_p))
    s = spec['set']
    strip_of(slots[:4]).save(os.path.join(od, f'{s}_a.png'))
    strip_of(slots[4:]).save(os.path.join(od, f'{s}_b.png'))
    strip_of(plain[:4]).save(os.path.join(od, f'{s}_plain_a.png'))
    strip_of(plain[4:]).save(os.path.join(od, f'{s}_plain_b.png'))
    pj = gait_pose_json(name, P, cam, char, recs, rep)
    with open(os.path.join(od, 'pose.json'), 'w', encoding='utf-8') as f:
        json.dump(pj, f, indent=1, ensure_ascii=False)
    # GIFs
    save_gif([on_bg(c, floor_y=ANCHOR[1]) for c in cells], os.path.join(od, f'{s}_game_x1.gif'), spec['ms'])
    save_gif([on_bg(c, floor_y=ANCHOR[1]).resize((CELL * 4, CELL * 4), Image.Resampling.NEAREST) for c in cells],
             os.path.join(od, f'{s}_game_x4.gif'), spec['ms'])
    save_gif([im.crop((0, 380, SLOT_W, 900)) for im in slots], os.path.join(od, f'{s}_guide.gif'), spec['ms'])
    smooth = []
    for pose, meta in gait_frames(name, P, cam, char, n=24):
        rs = dict(robe_spec, lag=robe_spec['lag'] * math.cos(2 * math.pi * (meta['phi'] - 0.125))) if robe_spec else None
        _, im, _ = render_frame(P, pose, cam, props, rs)
        smooth.append(im.crop((0, 380, SLOT_W, 900)).resize((SLOT_W // 2, 260), Image.Resampling.BOX))
    save_gif(smooth, os.path.join(od, f'{s}_smooth.gif'), int(round(spec['ms'] * 8 / 24)))
    contact_sheet(key, rgb, mask, info, P, cam, char, rep, os.path.join(od, 'contact.png'))
    checks = gait_checks(spec, recs)
    ext = []
    for im in plain:
        nz = np.flatnonzero((np.abs(np.asarray(im).astype(int) - np.array(MAGENTA)).sum(-1) > 0).any(0))
        ext.append((int(nz.min()), int(nz.max())))
    checks.append('x extent incl. props per frame (slot band 32..351): ' + ' '.join(f'{a_}-{b_}' for a_, b_ in ext)
                  + ('  OK' if all(a_ >= 32 and b_ <= 351 for a_, b_ in ext) else '  OUTSIDE'))
    log(f'{key}: {sid} gait {name} ({spec["class"]}) -> {od}')
    for c in checks:
        log('   ' + c)
    result = {'dir': od, 'checks': checks, 'recs': recs, 'slots': slots, 'plain': plain, 'masks': masks, 'P': P, 'rep': rep,
              'info': info, 'cam': cam, 'char': char}
    if char.get('actions'):
        result['actions'] = build_actions(key, P, cam, char, od, log)
    return result


def gait_checks(spec, recs):
    out = []
    step4 = spec['step_px'] / 4
    tops = [r['top_px'] for r in recs]
    out.append(f"head top y {min(tops)}..{max(tops)} (spread {max(tops) - min(tops)} px), hip height "
               f"{min(r['hip_height_px'] for r in recs)}..{max(r['hip_height_px'] for r in recs)}, lean "
               f"{min(r['lean_deg'] for r in recs)}..{max(r['lean_deg'] for r in recs)} deg")
    low = [(r['frame'], r['lowest_px']) for r in recs]
    out.append('lowest pixel per frame: ' + ' '.join(f'{f}:{y}' for f, y in low))
    flights = [r for r in recs if r['phase'] == 'flight']
    if flights:
        out.append('flight clearance (>= 18 px needed): ' + ', '.join(f"{r['frame']} {FLOOR - r['lowest_px']} px" for r in flights))
    # planted toe retreat per cell (screen px)
    for start, leg in ((0, 'N'), (4, 'F')):
        xs = []
        for k in range(5 if spec['gait'] != 'run' else 3):
            r = recs[(start + k) % 8]
            j = r['joints']
            org = (r['slot'] - 1) * SLOT_W if spec['gait'] == 'run' else 0
            xs.append(round(j['toetip' + leg][0] - org - HIP_X, 1))
        ret = [round(xs[i] - xs[i + 1], 1) for i in range(len(xs) - 1)]
        out.append(f"planted {'near' if leg == 'N' else 'far'} toe x {xs} -> retreat per cell {ret} (target {step4:.1f})")
    bad = [r['frame'] for r in recs if not r['ik_reached']]
    if bad:
        out.append('IK could not reach (leg straight, foot short): ' + ', '.join(bad))
    lowered = [(r['frame'], r['hip_lowered_px']) for r in recs if r.get('hip_lowered_px')]
    if lowered:
        out.append('hip lowered to reach the planted foot: ' + ', '.join(f'{f} {v} px' for f, v in lowered))
    return out


def build_actions(key, P, cam_run, char, od, log):
    cam = Camera(yaw=cam_run.yaw, lock_hip=False)
    res = {}
    for act, fn, ms in (('attack', warrior_attack, None), ('hit', warrior_hit, [220, 180])):
        keys, ib = fn(P, char)
        frames = action_frames(keys, P, cam, ib)
        # fix the camera on the READY / first key's hip so the body really moves in the slot
        b0 = fk(P, frames[0][1])
        cam.dx = -(cam.V @ b0.joints['hip'])[0] - ACTION_SHIFT   # READY hip at x=192-ACTION_SHIFT: room for the strike
        imgs, plain, names, recs = [], [], [], []
        for nm, pose, props, is_key, ok in frames:
            body = fk(P, pose, props=props)
            im, m = render(body, P, cam)
            ip, _ = render(body, P, cam, joints=False, ground=False)
            imgs.append(im)
            plain.append(ip)
            names.append(nm)
            J = project_joints(body, cam, JOINTS_OUT)
            recs.append({'frame': nm, 'key': is_key, 'ik_reached': bool(ok), 'joints': J,
                         'top_px': int(np.flatnonzero(m.any(1)).min()), 'lowest_px': int(np.flatnonzero(m.any(1)).max()),
                         'angles_deg': {k: round(v, 2) for k, v in full_pose(pose).items()},
                         'props': props})
        if act == 'attack':
            imgs[0].save(os.path.join(od, 'attack_ready.png'))
            use = list(range(1, len(imgs)))         # windup, in-betweens, strike
            ms = [150, 45, 45, 260]
        else:
            use = list(range(len(imgs)))
        sl = [imgs[i] for i in use]
        strip_of(sl, n=max(4, len(sl)) if act == 'attack' else 2).save(os.path.join(od, f'{act}_a.png'))
        strip_of([plain[i] for i in use], n=max(4, len(sl)) if act == 'attack' else 2).save(os.path.join(od, f'{act}_plain_a.png'))
        cells = [game_cell(plain[i]) for i in use]
        save_gif([on_bg(c, floor_y=ANCHOR[1]).resize((CELL * 4, CELL * 4), Image.Resampling.NEAREST) for c in cells],
                 os.path.join(od, f'{act}_game_x4.gif'), ms)
        save_gif([on_bg(c, floor_y=ANCHOR[1]) for c in cells], os.path.join(od, f'{act}_game_x1.gif'), ms)
        save_gif([imgs[i].crop((0, 360, SLOT_W, 900)) for i in use], os.path.join(od, f'{act}_guide.gif'), ms)
        with open(os.path.join(od, f'{act}_pose.json'), 'w', encoding='utf-8') as f:
            json.dump({'set': f'{act}3d__{key}', 'baseline': FLOOR, 'scale': SCALE, 'hip_column_of': names[0],
                       'frames': [recs[i] for i in use], 'ready': recs[0] if act == 'attack' else None,
                       'source': '3D mannequin prototype tools/mannequin3d'}, f, indent=1, ensure_ascii=False)
        lows = [recs[i]['lowest_px'] for i in use]
        ext = []
        for i in use:
            nz = np.flatnonzero((np.abs(np.asarray(plain[i]).astype(int) - np.array(MAGENTA)).sum(-1) > 0).any(0))
            ext.append(f'{int(nz.min())}-{int(nz.max())}')
        log(f'   {act}: x extent incl. props per frame {ext} (slot band 32..351)')
        log(f'   {act}: frames {[names[i] for i in use]}, lowest px {lows}, IK ok {[recs[i]["ik_reached"] for i in use]}')
        res[act] = [names[i] for i in use]
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('--chars', nargs='+', default=list(CHARS))
    ap.add_argument('--yaw', type=float, default=15.0, help='camera turn toward the viewer (deg), the slight 3/4 look')
    ap.add_argument('--chest-open', type=float, default=30.0, help='extra chest turn toward the viewer (deg)')
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    logs = []

    def log(s):
        print(s)
        logs.append(s)
    results = {}
    for key in a.chars:
        results[key] = build_char(key, a.out, a.yaw, a.chest_open, log)
    if 'warrior' in results:
        r = results['warrior']
        stats = compare_run(r['plain'], r['masks'], r['char']['sheet'], r['info']['stem'],
                            os.path.join(r['dir'], 'compare_run.png'), os.path.join(r['dir'], 'compare_run.json'))
        for row in ('registered', 'inbox'):
            v = [s['iou_body'] for s in stats if s['row'] == row]
            if v:
                log(f'warrior compare ({row}): silhouette IoU per frame {v}, mean {np.mean(v):.3f}')
        vs_v2(r, log)
    with open(os.path.join(a.out, 'build_log.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(logs) + '\n')


def vs_v2(r, log):
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


if __name__ == '__main__':
    main()
