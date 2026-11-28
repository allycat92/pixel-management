"""Shared helpers for build.py / report.py: carry spec loading, image helpers (keyed RGBA, the add_gait game cell,
GIFs, strips), fonts."""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from render import SLOT_W, SLOT_H, FLOOR, HIP_X, MAGENTA

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CARRY_JSON = os.path.join(HERE, 'specs', 'carry3d.json')
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CELL, ANCHOR = 96, (48, 92)
PREVIEW_BG = (58, 70, 60)


def load_carry(path=CARRY_JSON):
    with open(path, encoding='utf-8') as f:
        return json.load(f)['chars']


def load_painter(path=CARRY_JSON):
    """who paints over the 3D guides (carry3d.json `painter.name`; owner 2026-11-28: GPT until he switches back to
    Antigravity) - the ONE place the 3D request READMEs take the painter's name from"""
    with open(path, encoding='utf-8') as f:
        name = (json.load(f).get('painter') or {}).get('name')
    if not name:
        raise ValueError(f'{path}: no painter.name - set who paints the 3D requests (GPT or Antigravity)')
    return name


def sheet_scale(sid):
    """the sheet's registration scale from art/requests/phase3.json (the same source run_request_guides uses)"""
    with open(os.path.join(REPO, 'art', 'requests', 'phase3.json'), encoding='utf-8') as f:
        ph = json.load(f)
    items = ph.get('items', ph) if isinstance(ph, dict) else ph
    for it in items if isinstance(items, list) else []:
        if isinstance(it, dict) and it.get('id') == sid and isinstance(it.get('scale'), (int, float)):
            return float(it['scale'])
    raise SystemExit(f'{sid}: no recorded scale in art/requests/phase3.json')


def font(sz, bold=False):
    try:
        return ImageFont.truetype(FONTB if bold else FONT, sz)
    except OSError:
        return ImageFont.load_default()


def keyed(img):
    """RGBA with the magenta background (and nothing else) transparent"""
    a = np.asarray(img.convert('RGB')).astype(int)
    alpha = (np.abs(a - np.array(MAGENTA)).sum(-1) > 0).astype(np.uint8) * 255
    return Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), 'RGBA')


def game_cell(img_slot, scale=0.1654):
    """the add_gait window (hip column x=192 -> anchor x 48, floor bottom edge 871 -> anchor y 92) shrunk to 96x96"""
    S = int(round(CELL / scale))
    ox = S // 2
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
