"""Build the movement-drawing guide images of a gait request art/requests/gait/<prefix>__<short>/ (PIL + numpy).

Any registered battle sheet, any movement class (light run / heavy / robe - tools/art/specs/gait_classes.json):

  python3 tools/art/run_request_guides.py sheet/class/archer sheet/captain/ironwall      # class from gait_classes.json
  python3 tools/art/run_request_guides.py sheet/class/mage --out DIR                     # somewhere else (scratch)
  python3 tools/art/run_request_guides.py sheet/class/rogue --info                       # only print the derived geometry
  (a short id such as class_warrior or the png stem sheet_class_warrior works too; an existing request folder needs --force)

The README of a request is written by tools/art/gait_requests.py --write (which calls build() below).

guide_<p>_a.png / guide_<p>_b.png = class mannequin strips (<p> = run / heavy / robe). If the sheet scale differs by
    more than 1%, the strips and a request-local pose.json are scaled around the slot anchor.
size_<p>_a.png / size_<p>_b.png  = 1920x1024: a SIZE panel (the character's accepted idle, faint, placed the way the engine places it
    - its anchor column on x=192, soles on y=870 - with the mannequin's first frame of that strip outlined over it at the same scale)
    + the 4 mannequin frames in their delivery slots, with the floor line y=870, the hip column x=192 of each slot, the 32-px border
    band, the planted toe of each stance frame (yellow tick + x) and, for the light run, the flight line y=852.

Nothing is hard-coded per character: the idle x-range, the anchor ("hip") column and the scale come from the source sheet
art/inbox/<stem>.png (first pose = idle; upper-left for 2x2), the registered sheet (assets/art/manifest.json: file, anchor, frame 0)
and the request scale (art/requests/phase3.json). The anchor column = the idle's sole centre in the source (the column sheets.py put
on the anchor) corrected by how far the registered idle's sole centre sits from the anchor. Writes only under the request folder
(or --out); never assets/ or art/inbox/.
"""
import argparse
import glob
import json
import math
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = 'assets/art/manifest.json'
SPEC = 'tools/art/specs/gait_classes.json'
PHASE3 = 'art/requests/phase3.json'
MAG = np.array([255, 0, 255])
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SLOT, FLOOR, HIP, BAND = 384, 870, 192, 32
FLIGHT_LINE = 852          # check_delivery.py --flight-slots: the flight frame's lowest pixel >= 18 px above the floor
CLASSES = ('light', 'heavy', 'robe')
PREFIX = {'light': 'run', 'heavy': 'heavy', 'robe': 'robe'}       # request folder head and guide/size file names
GUIDE_SET = {'light': 'run_base', 'heavy': 'heavy_base', 'robe': 'robe_base'}
PHASE_EN = {'contact': 'contact', 'down': 'down (weight drops)', 'passing': 'passing', 'push': 'push',
            'push-off': 'push-off', 'flight': 'FLIGHT (both feet up)'}


class Fail(Exception):
    pass


def path(rel):
    return os.path.join(REPO, rel)


def load_json(rel):
    with open(path(rel), encoding='utf-8') as f:
        return json.load(f)


def resolve(arg, man):
    """'sheet/class/archer' | 'sheet_class_archer' | 'class_archer' -> manifest id"""
    if arg in man:
        return arg
    body = arg[len('sheet_'):] if arg.startswith('sheet_') else arg
    body = body[:-4] if body.endswith('.png') else body
    for sid, e in man.items():
        if sid.startswith('sheet/') and isinstance(e, dict) and 'sheet' in e:
            if os.path.splitext(os.path.basename(e['file']))[0] == 'sheet_' + body:
                return sid
    raise Fail(f'{arg}: not a registered battle sheet in {MANIFEST}')


def movement_class(sid):
    cls = ((load_json(SPEC).get('sheets') or {}).get(sid) or {}).get('gait')
    if cls not in CLASSES:
        raise Fail(f'{sid}: movement class {cls!r} in {SPEC} - only light / heavy / robe sheets get a drawn run')
    return cls


def mannequin(cls):
    """the confirmed mannequin of a class -> (pose.json rel path, pose dict, [strip a, strip b] rel paths)"""
    if cls == 'light':
        pj = ((load_json(SPEC).get('classes') or {}).get('light') or {}).get('guide') or 'art/requests/guides/run_base/v2/pose.json'
    else:
        vs = sorted(glob.glob(path(f'art/requests/guides/{GUIDE_SET[cls]}/v*/pose.json')),
                    key=lambda p: int(re.sub(r'\D', '', os.path.basename(os.path.dirname(p))) or 0))
        if not vs:
            raise Fail(f'{cls}: no confirmed mannequin art/requests/guides/{GUIDE_SET[cls]}/v<n>/ yet (draft/ is not a request guide)')
        pj = os.path.relpath(vs[-1], REPO)
    pose = load_json(pj)
    pj = pj.replace(os.sep, '/')
    d = os.path.dirname(pj)
    strips = [f'{d}/{pose["set"]}_{h}.png' for h in 'ab']
    for s in strips:
        if not os.path.exists(path(s)):
            raise Fail(f'mannequin strip missing: {s}')
    return pj, pose, strips


def request_item(sid):
    try:
        for it in load_json(PHASE3)['items']:
            if it.get('id') == sid:
                return it
    except (OSError, ValueError, KeyError):
        pass
    return {}


def sheet_scale(sid):
    scale = request_item(sid).get('scale')
    if not isinstance(scale, (int, float)) or isinstance(scale, bool) or not math.isfinite(scale) or scale <= 0:
        raise Fail(f'{sid}: no recorded scale in {PHASE3}; record the registration scale before making a gait guide')
    return scale


def fig_mask(rgb):
    return np.sqrt(((rgb.astype(int) - MAG) ** 2).sum(-1)) > 60


def feet_x(mask):
    """sheets.py feet_x: centre of the opaque pixels in the lowest 6 rows (the column sheets.py puts on the anchor)"""
    ys, xs = np.nonzero(mask)
    band = ys >= ys.max() - 5
    return (xs[band].min() + xs[band].max() + 1) / 2


def idle_region(src, layout):
    # 같은 1536×1024라도 2×2는 위쪽 첫 칸만 대기다. 아래 칸(공격/피격)을 섞지 않는다.
    return src[:src.shape[0] // 2, :src.shape[1] // 2] if layout == '2x2' else src


def geometry(sid, man=None):
    """everything the guides and the README need about one sheet, derived from the files (no per-character table)"""
    man = man or load_json(MANIFEST)
    scale = sheet_scale(sid)
    e = man[sid]
    meta = e['sheet']
    stem = os.path.splitext(os.path.basename(e['file']))[0]
    src_rel = f'art/inbox/{stem}.png'
    if not os.path.exists(path(src_rel)):
        raise Fail(f'{sid}: the accepted source sheet {src_rel} is not in this checkout')
    src = np.asarray(Image.open(path(src_rel)).convert('RGB'))
    if src.shape[:2] != (1024, 1536):
        raise Fail(f'{src_rel}: {src.shape[1]}x{src.shape[0]}, expected a 1536x1024 1x4 strip')
    req = request_item(sid)
    layout = req.get('layout')
    mk = fig_mask(idle_region(src, layout))
    col = mk.any(0)
    if not col.any():
        raise Fail(f'{src_rel}: empty')
    x0 = int(np.argmax(col))
    if layout == '2x2':
        x1 = int(np.flatnonzero(col)[-1])  # 같은 칸 안의 떨어진 장비도 대기 그림에 남긴다
    else:
        x1 = x0
        while x1 + 1 < len(col) and col[x1 + 1]:
            x1 += 1
    idle = mk[:, x0:x1 + 1]
    ys = np.nonzero(idle.any(1))[0]
    # the registered idle (frame 0 of the game sheet)
    g = np.asarray(Image.open(path(e['file'])).convert('RGBA'))
    cw, ch = meta['cell']
    fx, fy = meta['frames'][0]
    ga = g[fy:fy + ch, fx:fx + cw, 3] > 0
    gys = np.nonzero(ga.any(1))[0]
    reg_scale = (gys.max() - gys.min() + 1) / (ys.max() - ys.min() + 1)
    ax, ay = meta['anchor']
    anchor_col = x0 + feet_x(idle) + (ax - feet_x(ga)) / scale
    return {
        'sheet': sid, 'stem': stem, 'short': stem[len('sheet_'):], 'source': src_rel, 'registered': e['file'],
        'idle_x': [x0, x1], 'idle_top': int(ys.min()), 'idle_low': int(ys.max()), 'anchor_col': round(float(anchor_col), 1),
        'scale': scale, 'scale_src': 'phase3.json', 'source_layout': layout,
        'scale_registered': round(float(reg_scale), 4), 'cell': [cw, ch], 'anchor': [ax, ay],
        'game_idle_h': int(gys.max() - gys.min() + 1), 'tint': req.get('tint') or meta.get('tint'),
        'spots': req.get('spots'), 'package': req.get('package'), 'name_ko': req.get('name'),
    }


def outline(mask):
    m = mask
    inner = m.copy()
    inner[1:, :] &= m[:-1, :]
    inner[:-1, :] &= m[1:, :]
    inner[:, 1:] &= m[:, :-1]
    inner[:, :-1] &= m[:, 1:]
    edge = m & ~inner
    thick = edge.copy()  # 2 px wide
    for dy, dx in ((0, 1), (1, 0), (1, 1)):
        thick |= np.roll(np.roll(edge, dy, 0), dx, 1)
    return thick


def dashed_h(d, x0, x1, y, col, dash=10, gap=6, w=2):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + dash, x1), y)], fill=col, width=w)
        x += dash + gap


def dashed_v(d, x, y0, y1, col, dash=10, gap=6, w=2):
    y = y0
    while y < y1:
        d.line([(x, y), (x, min(y + dash, y1))], fill=col, width=w)
        y += dash + gap


def wrap(d, text, font, width):
    """split text into lines that fit width px"""
    lines, cur = [], ''
    for w in text.split(' '):
        t = (cur + ' ' + w).strip()
        if cur and d.textlength(t, font=font) > width:
            lines.append(cur)
            cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


def frame_label(fr):
    lab = f'{fr["frame"]} {PHASE_EN.get(fr.get("phase"), fr.get("phase", ""))}'
    if fr.get('phase') == 'contact':
        lab += ' - both feet down' if len(fr.get('feet_down') or []) == 2 else f' ({fr.get("stance", "?")} foot)'
    return lab


def stance_toes(fr):
    """[(toe x relative to the hip column, label)] of the feet on the floor in a frame (pose.json toe_x_px)"""
    t = fr.get('toe_x_px')
    if t is None:
        return []
    if isinstance(t, (int, float)):
        return [(t, 'toe')]
    out = [(t['stance'], 'toe')] if t.get('stance') is not None else []
    if t.get('rear') is not None:
        out.append((t['rear'], 'rear toe'))
    return out


def scale_pose(source, pose, sheet_scale):
    ratio = pose['scale'] / sheet_scale

    def distance(value):
        if value is None:
            return None
        if isinstance(value, dict):
            return {key: distance(item) for key, item in value.items()}
        if isinstance(value, list):
            return [distance(item) for item in value]
        return round(value * ratio, 4)

    def y_pos(value):
        if value is None:
            return None
        if isinstance(value, dict):
            return {key: y_pos(item) for key, item in value.items()}
        return round(FLOOR + (value - FLOOR) * ratio)

    scaled = dict(pose, scale=sheet_scale, scaled_from=source,
                  source_scale=pose['scale'], scale_ratio=ratio, anchor=[HIP, FLOOR])
    for key in ('head_px', 'step_px', 'bob_px', 'flight_clearance_px', 'push_ankle_shift_px',
                'sink_contact_to_down_px', 'other_foot_max_px', 'heel_up_ankle_shift_px', 'bones_px'):
        if key in pose:
            scaled[key] = distance(pose[key])
    if 'planted_toes' in pose:
        scaled['planted_toes'] = [dict(toes, toe_x_px=distance(toes['toe_x_px'])) for toes in pose['planted_toes']]

    scaled['frames'] = []
    for frame in pose['frames']:
        # Run poses store strip-wide joint x; heavy/robe store the joints in each slot.
        origin = HIP if pose.get('gait') in ('heavy', 'robe') else HIP + (frame['slot'] - 1) * SLOT
        out = {}
        for key, value in frame.items():
            if key == 'joints':
                out[key] = {joint: [round(origin + (x - origin) * ratio, 4),
                                    round(FLOOR + (y - FLOOR) * ratio, 4)]
                            for joint, (x, y) in value.items()}
            elif key in ('top_px', 'lowest_px', 'sole_px'):
                out[key] = y_pos(value)
            elif key.endswith('_px') or key == 'hem':
                out[key] = distance(value)
            else:
                out[key] = value
        scaled['frames'].append(out)
    return scaled


def scale_strip(strip, ratio):
    """Resample each slot about its own anchor, without reading neighbouring slots."""
    sx = np.rint(HIP + (np.arange(SLOT) - HIP) / ratio).astype(int)
    sy = np.rint(FLOOR + (np.arange(strip.shape[0]) - FLOOR) / ratio).astype(int)
    valid_x = (sx >= 0) & (sx < SLOT)
    valid_y = (sy >= 0) & (sy < strip.shape[0])
    out = np.empty_like(strip)
    out[:] = MAG
    for slot in range(strip.shape[1] // SLOT):
        offset = slot * SLOT
        ys, xs = np.nonzero(fig_mask(strip[:, offset:offset + SLOT]))
        left, right = HIP + (np.array([xs.min(), xs.max()]) - HIP) * ratio
        top = FLOOR + (ys.min() - FLOOR) * ratio
        if left < BAND or right > SLOT - 1 - BAND or top < 0:
            raise Fail(f'scaled mannequin slot {slot + 1} exceeds x={BAND}..{SLOT - 1 - BAND} or top y=0 '
                       f'(x={left:.1f}..{right:.1f}, top={top:.1f})')
        out[np.ix_(np.flatnonzero(valid_y), np.flatnonzero(valid_x) + offset)] = (
            strip[np.ix_(sy[valid_y], sx[valid_x] + offset)])
    return out


def build(sid, outdir, cls=None, man=None, force=False):
    """write guide_<p>_a/b.png + size_<p>_a/b.png for one sheet into outdir -> geometry dict (+ class, mannequin)"""
    man = man or load_json(MANIFEST)
    geo = geometry(sid, man)
    cls = cls or movement_class(sid)
    pj, pose, strips = mannequin(cls)
    source_pose = pj
    scaled = abs(geo['scale'] / pose['scale'] - 1) > 0.01
    p = PREFIX[cls]
    os.makedirs(outdir, exist_ok=True)
    names = [f'guide_{p}_{h}.png' for h in 'ab'] + [f'size_{p}_{h}.png' for h in 'ab']
    if scaled:
        names.append('pose.json')
    if not force:
        there = [n for n in names if os.path.exists(os.path.join(outdir, n))]
        if there:
            raise Fail(f'{outdir}: {", ".join(there)} already there - pass --force to rebuild')
    sheet = np.asarray(Image.open(path(geo['source'])).convert('RGB'))
    ix0, ix1 = geo['idle_x']
    idle = idle_region(sheet, geo['source_layout'])[:, ix0:ix1 + 1]
    idle_y = 0
    if geo['source_layout'] == '2x2':
        # 위 왼쪽 원본은 y≈461에 디딘다. 위치 비교판은 y=870으로 옮기고 배율은 유지한다.
        idle_y = FLOOR - geo['idle_low'] + geo['idle_top']
        idle = idle[geo['idle_top']:geo['idle_low'] + 1]
    imask = fig_mask(idle)
    ox = int(round(HIP - (geo['anchor_col'] - ix0)))        # idle column 0 lands here in the SIZE panel
    f_reg = ImageFont.truetype(FONT, 22)
    f_small = ImageFont.truetype(FONT, 18)
    f_big = ImageFont.truetype(FONTB, 28)
    guide_strips = [np.asarray(Image.open(path(p)).convert('RGB')) for p in strips]
    if scaled:
        pose = scale_pose(source_pose, pose, geo['scale'])
        guide_strips = [scale_strip(strip, pose['scale_ratio']) for strip in guide_strips]
        local_pose = os.path.join(outdir, 'pose.json')
        try:
            pj = os.path.relpath(local_pose, REPO).replace(os.sep, '/')
        except ValueError:  # --out may be on another Windows drive
            pj = local_pose.replace(os.sep, '/')
    elif force:
        local_pose = os.path.join(outdir, 'pose.json')
        if os.path.isfile(local_pose) and load_json(local_pose).get('scaled_from'):
            os.remove(local_pose)
    frames = pose['frames']
    flight_any = any(fr.get('phase') == 'flight' for fr in frames)
    for k, half in enumerate('ab'):
        strip = guide_strips[k]
        guide = os.path.join(outdir, f'guide_{p}_{half}.png')
        if scaled:
            Image.fromarray(strip).save(guide, optimize=True)
        else:
            shutil.copyfile(path(strips[k]), guide)
        frs = [fr for fr in frames if fr.get('strip') == half] or frames[k * 4:(k + 1) * 4]
        W = SLOT * 5
        canvas = np.zeros((1024, W, 3), np.uint8)
        canvas[:] = MAG
        # SIZE panel (slot 0): faint idle, anchor column on x=192, soles on y=870 (2x2 idle is moved down without resizing)
        lo, hi = max(0, -ox), min(idle.shape[1], SLOT - ox)
        faint = (idle.astype(float) * 0.45 + np.array([235, 235, 235]) * 0.55).astype(np.uint8)
        sub = canvas[idle_y:idle_y + idle.shape[0], ox + lo:ox + hi]
        m = imask[:, lo:hi]
        sub[m] = faint[:, lo:hi][m]
        # mannequin first frame of this strip as a cyan outline over it
        canvas[:, 0:SLOT][outline(fig_mask(strip[:, 0:SLOT]))] = (0, 200, 255)
        im = Image.fromarray(canvas)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 300, SLOT - 1, 1023], outline=(255, 255, 255), width=3)
        dashed_v(d, HIP, 362, 882, (255, 255, 255), dash=8, gap=8, w=1)
        for s in range(4):
            x0 = SLOT + s * SLOT
            d.rectangle([x0, 300, x0 + SLOT - 1, 1023], outline=(60, 0, 60), width=1)
            dashed_v(d, x0 + BAND, 362, 882, (150, 60, 150), dash=4, gap=8, w=1)
            dashed_v(d, x0 + SLOT - 1 - BAND, 362, 882, (150, 60, 150), dash=4, gap=8, w=1)
            dashed_v(d, x0 + HIP, 362, 882, (255, 255, 255), dash=8, gap=8, w=1)
            if s < len(frs) and frs[s].get('phase') == 'flight':
                d.line([(x0 + 40, FLIGHT_LINE), (x0 + 344, FLIGHT_LINE)], fill=(255, 255, 0), width=1)
        dashed_h(d, 0, W, FLOOR + 1, (255, 255, 255), dash=14, gap=8, w=2)
        arr = np.asarray(im).copy()
        smask = fig_mask(strip)
        arr[:, SLOT:][smask] = strip[smask]
        im = Image.fromarray(arr)
        d = ImageDraw.Draw(im)
        for s, fr in enumerate(frs[:4]):
            x0 = SLOT + s * SLOT
            d.text((x0 + 10, 310), frame_label(fr), font=f_reg, fill=(255, 255, 255))
            if fr.get('lean_deg') is not None:
                d.text((x0 + 10, 336), f'lean {fr["lean_deg"]:g} deg  head top y={fr.get("top_px", "?")}', font=f_small,
                       fill=(255, 255, 255))
            if fr.get('phase') == 'flight':
                clear = FLOOR - fr.get('lowest_px', FLOOR)
                d.text((x0 + 40, 885), f'lowest pixel at or above y={FLIGHT_LINE}', font=f_small, fill=(255, 255, 0))
                d.text((x0 + 40, 907), f'(mannequin: {clear} px clear)', font=f_small, fill=(255, 255, 0))
                continue
            for j, (tx, lab) in enumerate(stance_toes(fr)):
                x = int(round(x0 + HIP + tx))
                d.line([(x, FLOOR + 4), (x, FLOOR + 22)], fill=(255, 255, 0), width=3)
                d.text((min(x - 30, x0 + SLOT - 150), 897 + 22 * j), f'{lab} x={int(round(HIP + tx))}', font=f_small,
                       fill=(255, 255, 0))
        if flight_any:
            floor_txt = ('white dashed line: floor y=870 (sole of the standing foot)  |  yellow tick: the planted toe (x in the slot) '
                         '|  yellow line: flight, nothing below y=852')
        else:
            floor_txt = ('white dashed line: floor y=870 - a sole on it in EVERY frame (no flight)  |  yellow tick: the planted toe '
                         '(x in the slot)')
        d.text((392, 960), floor_txt, font=f_small, fill=(255, 255, 255))
        d.text((392, 985), 'white dashes in each slot: hip column x=192  |  purple dashes: x=32 and x=351 - keep every pixel between them',
               font=f_small, fill=(255, 255, 255))
        d.text((10, 945), 'faint = accepted idle (its own', font=f_small, fill=(255, 255, 255))
        d.text((10, 967), 'head/body size); cyan = mannequin', font=f_small, fill=(255, 255, 255))
        d.text((10, 989), '(pose and placement only)', font=f_small, fill=(255, 255, 255))
        rng = f'{frs[0]["frame"]}-{frs[-1]["frame"]}' if frs else ''
        d.text((14, 20), f'{geo["short"].upper()} {cls.upper()} {"RUN" if cls == "light" else "MOVE"} - strip {half.upper()}  '
               f'(frames {rng}, mannequin {os.path.dirname(pj)})', font=f_big, fill=(255, 255, 255))
        y = 62
        for para in (f'LEFT PANEL (not delivered): the accepted idle from {geo["source"]}, faint, placed as the game places it '
                     f'(anchor column on x=192, soles on y=870), with the cyan outline of the mannequin\'s '
                     f'{frs[0]["frame"] if frs else ""} on top: the SAME SCALE. Draw the character at the size of its idle (its own '
                     'head, torso, boots) - never shrink it.',
                     'RIGHT 4 SLOTS = the delivery layout (1536x1024 = this image without the left panel). Follow each '
                     'mannequin\'s legs, torso lean and arm swing. '
                     + ('' if flight_any else 'NO flight: one sole stays on y=870 in every frame. ')
                     + 'The guide lines and text are for reading only - the delivered strip has nothing but the character '
                     'on flat #FF00FF.'):
            for line in wrap(d, para, f_reg, W - 28):
                d.text((14, y), line, font=f_reg, fill=(255, 255, 255))
                y += 30
        d.text((10, 310), 'SIZE (idle + mannequin)', font=f_reg, fill=(255, 255, 255))
        im.save(os.path.join(outdir, f'size_{p}_{half}.png'), optimize=True)
    if scaled:
        with open(local_pose, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(pose, f, ensure_ascii=False, indent=2)
            f.write('\n')
    geo.update(cls=cls, prefix=p, pose=pj, source_pose=source_pose, scaled=scaled, strips=strips, idle_offset=ox, files=names)
    return geo


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sheets', nargs='+', help='manifest id (sheet/class/archer), png stem (sheet_class_archer) or short id (class_archer)')
    ap.add_argument('--class', dest='cls', choices=CLASSES, help='movement class (default: tools/art/specs/gait_classes.json)')
    ap.add_argument('--out', help='output folder (one sheet only; default art/requests/gait/<prefix>__<short>/)')
    ap.add_argument('--force', action='store_true', help='rebuild images that are already there')
    ap.add_argument('--info', action='store_true', help='only print the derived geometry (JSON)')
    a = ap.parse_args(argv)
    if a.out and len(a.sheets) > 1:
        print('--out takes one sheet', file=sys.stderr)
        return 2
    man = load_json(MANIFEST)
    try:
        for arg in a.sheets:
            sid = resolve(arg, man)
            if a.info:
                g = geometry(sid, man)
                g['class'] = a.cls or movement_class(sid)
                print(json.dumps(g, ensure_ascii=False))
                continue
            cls = a.cls or movement_class(sid)
            short = os.path.splitext(os.path.basename(man[sid]['file']))[0][len('sheet_'):]
            out = a.out or path(f'art/requests/gait/{PREFIX[cls]}__{short}')
            g = build(sid, out, cls, man, a.force)
            print(f'{sid} [{cls}]: {os.path.relpath(out, REPO)}/ {" ".join(g["files"])}  (idle x {g["idle_x"][0]}-{g["idle_x"][1]}, '
                  f'anchor column {g["anchor_col"]}, scale {g["scale"]} from {g["scale_src"]}, registered idle {g["scale_registered"]})')
    except Fail as e:
        print(f'run_request_guides: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
