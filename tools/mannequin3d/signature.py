"""Is this image an (unpainted or half-painted) 3D mannequin guide? A colour check that does not depend on where the
guides were written nor on the silhouette.

The mannequin renderer (render.py) only ever writes a small fixed palette on the body: 4 cel bands of each material,
the outline / inner-edge colours, the belt / sternum / eye / sole marks, the SPEC.md joint-dot colours and the ghost
outline colours. Painted art practically never hits those exact RGB values on more than a few per cent of its pixels
(the 57 accepted drawings: see tools/mannequin3d/test_mannequin3d.py), while a mannequin strip is made of them.

  python3 tools/mannequin3d/signature.py FILE.png [...]      # prints the share of mannequin-palette pixels per frame

add_gait.py calls mannequin3d_reason(path) next to its silhouette check (guide_reason), so a traced or copied 3D guide
is refused even when it was never put into art/requests/ (the silhouette IoU set does not know the scratch folders).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from render import (MAT, BANDS, OUTLINE, INNER, MARK, JOINT_COL, NECK_COL, GHOST_LINE, GHOST_HIDDEN,  # noqa: E402
                    MAGENTA, SLOT_W)

SHARE = 0.25          # a frame whose non-background pixels are >= 25% mannequin palette is a mannequin


def palette():
    cols = set()
    for base in MAT.values():
        for f in BANDS:
            cols.add(tuple(np.clip(np.array(base, float) * f, 0, 255).astype(np.uint8).tolist()))
    for c in (OUTLINE, INNER):
        cols.add(tuple(int(v) for v in c))
    for c in MARK.values():
        cols.add(tuple(c))
    for a, b in JOINT_COL.values():
        cols.add(tuple(a))
        cols.add(tuple(b))
    for c in (NECK_COL, GHOST_LINE, GHOST_HIDDEN):
        cols.add(tuple(c))
    return cols


_PAL = None


def _codes(rgb):
    return (rgb[..., 0].astype(np.int64) << 16) | (rgb[..., 1].astype(np.int64) << 8) | rgb[..., 2].astype(np.int64)


def frame_shares(arr):
    """share of mannequin-palette pixels among the non-background pixels, per 384-px slot (or the whole image)"""
    global _PAL
    if _PAL is None:
        _PAL = np.array(sorted((r << 16) | (g << 8) | b for r, g, b in palette()), np.int64)
    if arr.shape[-1] == 4:
        fg = arr[..., 3] > 0
        rgb = arr[..., :3]
    else:
        rgb = arr
        fg = np.ones(arr.shape[:2], bool)
    fg &= ~np.all(rgb == np.array(MAGENTA, np.uint8), -1)
    hit = np.isin(_codes(rgb), _PAL) & fg
    w = arr.shape[1]
    n = w // SLOT_W if w % SLOT_W == 0 and w >= SLOT_W else 1
    sw = w // n
    out = []
    for k in range(n):
        f = fg[:, k * sw:(k + 1) * sw].sum()
        out.append(float(hit[:, k * sw:(k + 1) * sw].sum() / f) if f else 0.0)
    return out


def mannequin3d_reason(path):
    """reason string when the image is a 3D mannequin guide (palette share >= SHARE in any frame), else None"""
    try:
        arr = np.asarray(Image.open(path).convert('RGBA'))
    except (OSError, ValueError):
        return None
    shares = frame_shares(arr)
    k = int(np.argmax(shares)) if shares else 0
    if shares and shares[k] >= SHARE:
        return (f'{k + 1}번 프레임의 {shares[k] * 100:.0f}% 가 3D 마네킹(tools/mannequin3d)의 색 그대로 — 칠하지 않은 3D 마네킹 '
                f'가이드 (>= {SHARE * 100:.0f}%)')
    return None


if __name__ == '__main__':
    for p in sys.argv[1:]:
        arr = np.asarray(Image.open(p).convert('RGBA'))
        print(p, ['%.3f' % s for s in frame_shares(arr)], mannequin3d_reason(p) or 'not a 3D mannequin')
