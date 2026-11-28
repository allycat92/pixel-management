#!/usr/bin/env python3
"""Self-check a battle-sheet delivery before it is pushed to art-inbox (and on receipt).

Checks the dot_queue / package README spec for a 1x4 strip (or a 2x2 grid):
  * 1536x1024, flat #FF00FF background, no transparency
  * every figure colour at RGB distance >= 150 from #FF00FF (>= 170 recommended)
  * figure colour count (~40 with hard edges; many more = soft / anti-aliased edges)
  * pose count, lowest pixel of each pose on y=870 (2x2: y=461 inside each 768x512 quadrant); run strips: --flight-slots 4 makes
    pose 4 a flight frame (lowest pixel >= 18 px above y=870 instead of on it)
  * >= 32 px of magenta between poses and to the border
  * WARN for a straight break that shifts opposite sides of a pose; enlarged crops go to --work (or a temp folder)
  * WARN for debris per pose: loose fragments (>= 3 px, 8-connected) more than 6 px from the figure, flat loose slivers within
    12 px above the soles line, and thin strokes (< 7 px thick, >= 24 px wide) sticking out of the figure in the 50 px above it
Optionally exports an .aseprite source with Aseprite (--aseprite) and checks that it equals the PNG.
Run sets (--gait-pair <run_b.png>, positional = run_a.png): the body against the sheet's idle drawing with
tools/art/gait_body.py (needs numpy; ~15 s): H1 phase-locked width pump, H2 same-phase mismatch, H3 head squashed
vs the idle, V1 sunk figure, staff / spear fist -> tip length (FAIL); horizontal paste seam (WARN). The sheet and
the request pose.json come from the file name (receive.py sheet_id / gait_pose) unless --sheet / --pose are given.

Usage:
  python3 tools/art/check_delivery.py art/inbox/sheet_hero_lyra.png
  python3 tools/art/check_delivery.py art/inbox/sheet_hero_lyra.png \
      --aseprite art/inbox/aseprite/sheet_hero_lyra.aseprite --aseprite-exe "C:/Program Files/Aseprite/Aseprite.exe"
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_class_warrior_run_a.png --flight-slots 4   # run strip: R4 is in the air
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_oswin_run_a.png --gait-pair art/inbox/gait/sheet_hero_oswin_run_b.png
  (Windows without a system Python:  uv run --no-project --with pillow python tools\\art\\check_delivery.py ...)

Exit code 0 = pass (warnings allowed), 1 = fail, 2 = could not run.
Only Pillow and the standard library; the Aseprite call uses an argument list (no shell).
"""
import argparse
from collections import Counter
from functools import reduce
import math
import os
from operator import and_, or_
import re
import subprocess
import sys
import tempfile
from typing import NamedTuple

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover
    print("Pillow is missing: pip install pillow  (or: uv run --no-project --with pillow python ...)")
    sys.exit(2)

KEY = (255, 0, 255)
SPOT_TOL = 40.0     # tools/art/sheets.py SPOT_TOL: pixels this close to a declared spot colour are kept at game size
W, H = 1536, 1024
MIN_DIST = 150.0
REC_DIST = 170.0
GAP = 32


def pixels(im):
    """Flat pixel sequence (Pillow >= 12.1 renamed getdata)."""
    return getattr(im, "get_flattened_data", im.getdata)()


def dist(c):
    return math.sqrt((255 - c[0]) ** 2 + c[1] ** 2 + (255 - c[2]) ** 2)


def load_rgb(path, errors):
    im = Image.open(path)
    im.load()
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        lo = rgba.getchannel("A").getextrema()[0]
        if lo < 255:
            errors.append("transparent pixels found: the background must be flat opaque #FF00FF "
                          "(fill the bottom 'Background' layer with #FF00FF)")
    return im.convert("RGB")


def components(mask, block=4, radius=3):
    """Figures as groups of pixels: parts closer than ~24 px join, groups >= 32 px apart stay separate.

    Works on a block-reduced mask (any pixel in a 4x4 block), dilated by `radius` blocks, so a pose whose
    weapon overlaps a neighbour's columns (but keeps 32 px of air in every direction) is still its own pose.
    Returns full-resolution masks, one per group, sorted left to right.
    """
    w, h = mask.size
    small = mask.convert("L").reduce(block).point(lambda v: 255 if v else 0)
    grown = small.filter(ImageFilter.MaxFilter(2 * radius + 1))
    sw, sh = grown.size
    gp = grown.load()
    groups = []
    label = 1
    for y in range(sh):
        for x in range(sw):
            if gp[x, y] == 255:
                ImageDraw.floodfill(grown, (x, y), label)
                lab = grown.point(lambda v, L=label: 255 if v == L else 0)
                full = lab.resize((sw * block, sh * block), Image.NEAREST).crop((0, 0, w, h)).convert("1")
                part = ImageChops.logical_and(full, mask)
                bb = part.getbbox()
                if bb:
                    groups.append((bb, part))
                label += 1
                if label >= 250:
                    return sorted(groups, key=lambda g: g[0][0])
    return sorted(groups, key=lambda g: g[0][0])


def trapped_key_pixels(rgb):
    """Key pixels not connected to the border (gaps inside a figure: fine if they are real gaps)."""
    w, h = rgb.size
    m = Image.new("L", (w, h), 0)
    m.putdata([255 if c == KEY else 0 for c in pixels(rgb)])
    mp = m.load()
    border = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
             [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    for p in border:
        if mp[p] == 255:
            ImageDraw.floodfill(m, p, 128)
    return m.histogram()[255]


def request_item(png):
    """The art/requests/phase3.json entry for this file name (layout, cell, scale, spots), or {}."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        import json
        with open(os.path.join(here, "..", "..", "art", "requests", "phase3.json"), encoding="utf-8") as f:
            items = json.load(f).get("items", [])
    except (OSError, ValueError):
        return {}
    name = os.path.basename(png)
    for it in items:
        if it.get("file") == name:
            return it
    return {}


def hex_rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def check_spots(rgb, spots, errors, warns, info):
    """Declared 'spot colours' (tiny must-show colours such as eyes): they must be unique enough in the sheet,
    because the converter keeps every pixel within SPOT_TOL of them at game size."""
    colors = [(n, c) for n, c in (rgb.getcolors(maxcolors=1 << 24) or []) if c != KEY]
    for h in spots:
        try:
            sc = hex_rgb(h)
        except ValueError:
            errors.append(f"spot colour '{h}' is not #rrggbb")
            continue
        d = lambda c: math.sqrt(sum((c[i] - sc[i]) ** 2 for i in range(3)))  # noqa: E731
        exact = sum(n for n, c in colors if c == sc)
        near = sum(n for n, c in colors if d(c) <= SPOT_TOL)
        others = [d(c) for n, c in colors if d(c) > SPOT_TOL]
        nearest = min(others, default=999.0)
        info.append(f"spot {h}: {exact} px exact, {near} px within {SPOT_TOL:.0f}, nearest other colour at distance {nearest:.1f}")
        if exact == 0:
            errors.append(f"spot {h}: no pixel has exactly this colour")
        elif near > 2 * exact:
            errors.append(f"spot {h}: {near} px lie within {SPOT_TOL:.0f} of it but only {exact} are exact - it is not unique "
                          "(other materials would be painted in the spot colour); choose a colour >= 60 away from every other colour")
        elif nearest < 60:
            warns.append(f"spot {h}: another colour is only {nearest:.0f} away (keep >= 60)")


REDRAW_SHARE = 0.30   # a touch-up changes a prop or some colours; above this share of the figure it is a new drawing


def compare_base(rgb, base_path, layout, feet, errors, warns, info, flight=()):
    """Touch-ups: what changed against the received PNG, and which failures were already there."""
    b_err, _, _ = check_png(base_path, layout, feet, flight=flight)
    base = Image.open(base_path).convert("RGB")
    if base.size != rgb.size:
        errors.append(f"base size {base.size} differs")
        return
    sil = col = 0
    cols = [[0, 0] for _ in range(4)]
    w = rgb.size[0]
    for i, (p, q) in enumerate(zip(pixels(base), pixels(rgb))):
        if p == q:
            continue
        x, y = i % w, i // w
        k = (x * 4 // w) if layout == "1x4" else (int(y >= H // 2) * 2 + int(x >= W // 2))
        if (p == KEY) != (q == KEY):
            sil += 1; cols[k][0] += 1
        else:
            col += 1; cols[k][1] += 1
    info.append(f"against the base: silhouette changed {sil} px, colour changed {col} px "
                f"(per pose silhouette/colour: {', '.join(f'{a}/{b}' for a, b in cols)})")
    figure = sum(1 for p in pixels(base) if p != KEY) or 1
    if (sil + col) > REDRAW_SHARE * figure:
        # most of the drawing is new: a failure that the old drawing also had is not "pre-existing", it was drawn again
        info.append(f"{100 * (sil + col) / figure:.0f}% of the figure differs from the base: treated as a redraw - no failure is excused as pre-existing")
        return
    old = set(b_err)
    for m in list(errors):
        if m in old:
            errors.remove(m)
            warns.append("pre-existing (also fails on the base, not caused by this touch-up): " + m)


# idle silhouettes (hat and weapon included) of the 36 humanoid strips delivered by 2026-11-26: median 418 px, two under 380 px
# (Crimson 367, Bjorn 373) - both had to be converted at a larger scale to stand level with the others
SMALL_IDLE = 380


FLIGHT_CLEAR = 18   # px: a run's flight frame (both feet off the ground) - tools/art/check_skeleton.py RUN['clear'], 3 game px
GAIT_STRIP = re.compile(r"_(run|walk)_[ab]\.png$")   # gait frame strips (<sheet stem>_<gait>_a.png): pose 1 is not an idle pose


class SeamEdge(NamedTuple):
    line: int
    start: int
    end: int
    grows: bool
    left: bool


def seam_on_axis(rgb, mask):
    """Find two long, bare edge changes on opposite sides of a connected silhouette."""
    w, h = mask.size
    # Measure relative to the tight pose, so 1x4, 2x2, and different drawing scales use the same test.
    depth = max(2, round(h * .012))
    minimum = max(12, round(w * .115))
    max_spacing = max(6, round(h * .085))
    edge_margin = round(w * .035)
    raster = mask.convert("L").tobytes()
    rows = [int.from_bytes(raster[y:y + w], "little") for y in range(0, len(raster), w)]
    long_run = re.compile(rb"\xff{%d,}" % minimum)
    colors = rgb.load()
    edges = []
    for y in range(depth, h - depth + 1):
        upper, lower = rows[y - 1], rows[y]
        shared = (upper & lower).bit_count() // 8
        if (shared < w * .21 or shared < max(upper.bit_count(), lower.bit_count()) / 16
                or (upper ^ lower).bit_count() < 8 * minimum):
            continue
        combined = upper | lower
        left = ((combined & -combined).bit_length() - 1) // 8
        right = (combined.bit_length() - 1) // 8
        above, below = rows[y - depth:y], rows[y:y + depth]
        # A candidate must switch in one row and persist on both sides of the boundary.
        added = reduce(and_, below) & ~reduce(or_, above)
        removed = reduce(and_, above) & ~reduce(or_, below)
        for grows, change in ((True, added), (False, removed)):
            edge_y, inner_y = (y, y + depth - 1) if grows else (y - 1, y - depth)
            for run in long_run.finditer(change.to_bytes(w, "little")):
                start, end = run.span()
                at_left, at_right = start - left <= edge_margin, right - end + 1 <= edge_margin
                if at_left == at_right:
                    continue
                # A normal drawn outline or shaded hem usually differs from the pixels just inside it.
                similar = sum(max(abs(a - b) for a, b in zip(colors[x, edge_y], colors[x, inner_y])) <= 30
                              for x in range(start, end))
                if similar >= .62 * (end - start):
                    edges.append(SeamEdge(y, start, end, grows, at_left))

    best, best_width = None, w * .32
    for i, first in enumerate(edges):
        for second in edges[i + 1:]:
            if second.line - first.line > max_spacing:
                break
            span = first.end - first.start + second.end - second.start
            if first.grows != second.grows and first.left != second.left and span >= best_width:
                best, best_width = (first, second), span
    return best


def report_pose_seams(rgb, mask, box, pose, stem, work, warns):
    frame, shape = rgb.crop(box), mask.crop(box)
    for axis in ("horizontal", "vertical"):
        if axis == "horizontal":
            sample, silhouette = frame, shape
            across, along = box[0], box[1]
        else:
            sample = frame.transpose(Image.Transpose.TRANSPOSE)
            silhouette = shape.transpose(Image.Transpose.TRANSPOSE)
            across, along = box[1], box[0]
        pair = seam_on_axis(sample, silhouette)
        if not pair:
            continue
        first, second = pair
        u, v = ("x", "y") if axis == "horizontal" else ("y", "x")
        coords = " and ".join(f"{v}={along + e.line}, {u}={across + e.start}-{across + e.end - 1}" for e in pair)
        msg = f"pose {pose}: possible {axis} seam at {coords}"
        pad = max(12, round(sample.height * .05))
        a, b = min(e.start for e in pair), max(e.end for e in pair)
        left, top = max(0, a - pad), max(0, first.line - pad)
        right, bottom = min(sample.width, b + pad), min(sample.height, second.line + pad)
        # Crop the original orientation, using the transposed coordinates only for detection.
        crop_box = (left, top, right, bottom) if axis == "horizontal" else (top, left, bottom, right)
        crop = frame.crop(crop_box)
        preview = crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.NEAREST)
        try:
            work = work or tempfile.mkdtemp(prefix="check-delivery-")
            os.makedirs(work, exist_ok=True)
            path = os.path.join(work, f"{stem}_pose{pose}_{axis}_{along + first.line}-{along + second.line}.png")
            preview.save(path)
            msg += f"; enlarged crop: {path}"
        except OSError as err:
            msg += f"; could not save enlarged crop: {err}"
        warns.append(msg)
    return work


STRAY_MIN = 3        # px: smaller loose specks are anti-alias noise and are ignored
STRAY_GAP = 6        # px: a loose part this close to the figure (figure mask dilated by 6 px) is a design part (tassel, string, spark)
FLOOR_BAND = 12      # px above the soles line where a loose flat sliver (wider than FLOOR_RATIO x its height) is a ground line
FLOOR_RATIO = 3
SPUR_OPEN = 7        # an opening with a 7x7 square keeps everything 7 px thick or more: what it strips off are thin strokes
SPUR_BAND = 50       # px above the soles line searched for thin strokes attached to the figure (lines dragged out of a boot)
SPUR_MIN_W, SPUR_RATIO, SPUR_MIN_PX = 24, 2.5, 40   # a flagged stroke: >= 24 px wide, >= 2.5x wider than tall, >= 40 px


def label8(mask):
    """8-connected components of a mode-"1" / "L" mask (row runs + union-find, no numpy): [(bbox, pixel count, runs)],
    runs as (y, x_start, x_end) with x_end exclusive, bbox (x0, y0, x1, y1) exclusive like getbbox()."""
    w, h = mask.size
    raw = mask.convert("L").tobytes()
    run_re = re.compile(rb"[^\x00]+")
    runs, parent, prev = [], [], []

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for y in range(h):
        cur = []
        for m in run_re.finditer(raw, y * w, (y + 1) * w):
            s, e = m.start() - y * w, m.end() - y * w
            i = len(runs)
            runs.append((y, s, e))
            parent.append(i)
            cur.append(i)
            for j in prev:
                if runs[j][1] <= e and runs[j][2] >= s:   # touching or diagonal neighbours in the row above
                    a, b = find(i), find(j)
                    if a != b:
                        parent[a] = b
        prev = cur
    groups = {}
    for i, r in enumerate(runs):
        groups.setdefault(find(i), []).append(r)
    out = []
    for rs in groups.values():
        bb = (min(r[1] for r in rs), min(r[0] for r in rs), max(r[2] for r in rs), max(r[0] for r in rs) + 1)
        out.append((bb, sum(r[2] - r[1] for r in rs), rs))
    return out


def paint_runs(size, runs, box=(0, 0)):
    """L image of `size` with the runs (canvas coords, shifted by -box) painted 255."""
    im = Image.new("L", size, 0)
    d = ImageDraw.Draw(im)
    for y, s, e in runs:
        d.line((s - box[0], y - box[1], e - 1 - box[0], y - box[1]), fill=255)
    return im


def fmt_box(bb):
    return f"x {bb[0]}-{bb[2] - 1}, y {bb[1]}-{bb[3] - 1} ({bb[2] - bb[0]}x{bb[3] - bb[1]} px)"


def report_strays(mask, layout, feet, warns):
    """Debris around each pose: loose specks of >= STRAY_MIN px more than STRAY_GAP px from the figure (the largest 8-connected
    part of the pose), flat loose slivers just above the soles line (ground lines), and thin strokes dragged out of the figure
    near the floor (an attached line below the feet that is not part of the design)."""
    w, h = mask.size
    if layout == "1x4":
        slots = [((k * w // 4, 0, (k + 1) * w // 4, h), feet) for k in range(4)]
    elif layout == "2x2":
        slots = [((x0, y0, x0 + w // 2, y0 + h // 2), y0 + feet) for y0 in (0, h // 2) for x0 in (0, w // 2)]
    else:
        slots = [((0, 0, w, h), feet)]
    comps = label8(mask)
    owner = lambda bb: next((k for k, (s, _) in enumerate(slots)  # noqa: E731 - slot of a part's bbox centre
                             if s[0] <= (bb[0] + bb[2]) / 2 < s[2] and s[1] <= (bb[1] + bb[3]) / 2 < s[3]), None)
    per_slot = [[] for _ in slots]
    for c in comps:
        k = owner(c[0])
        if k is not None:
            per_slot[k].append(c)
    figures = []
    for k, ((sx0, sy0, sx1, sy1), fy) in enumerate(slots):
        parts = sorted(per_slot[k], key=lambda c: -c[1])
        if not parts:
            continue
        fig = parts[0]
        figures.append(fig)
        pad = STRAY_GAP + 1
        fb = fig[0]
        box = (max(0, fb[0] - pad), max(0, fb[1] - pad), min(w, fb[2] + pad), min(h, fb[3] + pad))
        grown = paint_runs((box[2] - box[0], box[3] - box[1]), fig[2], box)
        for _ in range(STRAY_GAP):   # Chebyshev dilation by STRAY_GAP px
            grown = grown.filter(ImageFilter.MaxFilter(3))
        gp = grown.load()

        def near(runs):
            for y, s, e in runs:
                if box[1] <= y < box[3]:
                    for x in range(max(s, box[0]), min(e, box[2])):
                        if gp[x - box[0], y - box[1]]:
                            return True
            return False

        for bb, n, runs in parts[1:]:
            if n < STRAY_MIN:
                continue
            bw, bh = bb[2] - bb[0], bb[3] - bb[1]
            if bb[1] >= fy - FLOOR_BAND and bb[3] <= fy + 1 and bw > FLOOR_RATIO * bh:
                warns.append(f"pose {k + 1}: thin line just above the floor at {fmt_box(bb)}, {n} px, not connected to the figure "
                             f"(a ground line or leftover stroke is not part of the sprite: erase it)")
            elif not near(runs):
                warns.append(f"pose {k + 1}: stray fragment at {fmt_box(bb)}, {n} px, more than {STRAY_GAP} px from the figure "
                             f"(leftover pixels or debris: erase it, or join it to the figure if it is part of the design)")
    # thin strokes attached to the figure near the floor: what an opening with a SPUR_OPEN square strips off the figure
    for k, ((sx0, sy0, sx1, sy1), fy) in enumerate(slots):
        fig = next((f for f in figures if owner(f[0]) == k), None)
        if fig is None:
            continue
        pad = SPUR_OPEN
        top = max(0, fy - SPUR_BAND)
        box = (max(0, fig[0][0] - pad), max(0, top - pad), min(w, fig[0][2] + pad), min(h, fy + 1 + pad))
        fm = paint_runs((box[2] - box[0], box[3] - box[1]), fig[2], box)
        opened = fm.filter(ImageFilter.MinFilter(SPUR_OPEN)).filter(ImageFilter.MaxFilter(SPUR_OPEN))
        residue = ImageChops.subtract(fm, opened)
        band = Image.new("L", residue.size, 0)
        band.paste(255, (0, top - box[1], residue.width, fy + 1 - box[1]))
        residue = ImageChops.multiply(residue, band)
        for bb, n, _ in label8(residue):
            bw, bh = bb[2] - bb[0], bb[3] - bb[1]
            if n >= SPUR_MIN_PX and bw >= SPUR_MIN_W and bw >= SPUR_RATIO * bh:
                cb = (bb[0] + box[0], bb[1] + box[1], bb[2] + box[0], bb[3] + box[1])
                warns.append(f"pose {k + 1}: thin line sticking out of the figure near the floor at {fmt_box(cb)}, {n} px thinner "
                             f"than {SPUR_OPEN} px (a stroke dragged out of a foot or a ground line? erase it unless it is part of the design)")


def check_png(path, layout, feet, cell=None, scale=None, flight=(), report_seams=False, work=None):
    """flight: 1-based pose numbers of a 1x4 strip that are flight frames of a run (both feet off the ground): their lowest
    pixel must be FLIGHT_CLEAR px or more above the soles line instead of on it."""
    errors, warns, info = [], [], []
    mode = Image.open(path).mode
    if mode != "RGB":
        warns.append(f"PNG mode is {mode}, not RGB: an indexed PNG can import into Aseprite with a scrambled palette - save as RGB")
    rgb = load_rgb(path, errors)
    if layout == "1x1":
        # idle check (one pose before the full sheet): a quadrant of a 2x2 sheet or one slot of a 1x4 strip
        if rgb.size not in ((768, 512), (384, 1024)):
            errors.append(f"size {rgb.size[0]}x{rgb.size[1]}, expected 768x512 (2x2 sheets) or 384x1024 (1x4 sheets) for an idle check")
    elif rgb.size != (W, H):
        errors.append(f"size {rgb.size[0]}x{rgb.size[1]}, expected {W}x{H}")
    colors = rgb.getcolors(maxcolors=1 << 24) or []
    key_count = sum(n for n, c in colors if c == KEY)
    total = rgb.size[0] * rgb.size[1]
    fig = [(n, c) for n, c in colors if c != KEY]
    info.append(f"background #FF00FF: {100.0 * key_count / total:.1f}% of the canvas")
    if key_count < total * 0.4:
        errors.append("less than 40% of the canvas is exact #FF00FF: is the background flat magenta?")
    info.append(f"figure colours: {len(fig)}")
    if len(fig) > 96:
        warns.append(f"{len(fig)} figure colours: aim for ~40 with hard pixel edges (no anti-aliasing / soft blending)")
    near = [(dist(c), n, c) for n, c in fig if dist(c) < REC_DIST]
    bad = [t for t in near if t[0] < MIN_DIST]
    mind = min((dist(c) for n, c in fig), default=999.0)
    info.append(f"closest figure colour to #FF00FF: distance {mind:.1f} (rule >= {MIN_DIST:.0f}, recommended >= {REC_DIST:.0f})")
    if bad:
        n_px = sum(t[1] for t in bad)
        worst = sorted(bad)[:5]
        errors.append(f"{len(bad)} figure colours ({n_px} px) are within {MIN_DIST:.0f} of #FF00FF and will be erased: "
                      + ", ".join("#%02x%02x%02x(d=%.0f,%dpx)" % (c[0], c[1], c[2], d, n) for d, n, c in worst))
    elif near:
        warns.append(f"{len(near)} figure colours are between {MIN_DIST:.0f} and {REC_DIST:.0f} from #FF00FF (allowed, but keep >= {REC_DIST:.0f})")

    if layout != "1x1" and rgb.size != (W, H):
        return errors, warns, info
    mask = Image.new("1", rgb.size, 0)
    mask.putdata([0 if c == KEY else 1 for c in pixels(rgb)])
    whole = mask.getbbox()
    if not whole:
        errors.append("no figure pixels at all")
        return errors, warns, info
    l, t, r, b = whole
    cw_, ch_ = rgb.size
    if l < GAP or t < GAP or cw_ - r < GAP or ch_ - b < GAP:
        errors.append(f"figure bbox {whole} is closer than {GAP}px to the border")

    poses = []  # (bbox in canvas coords, pose mask, quadrant top y, soles line)
    if layout == "1x1":
        fy = feet if feet is not None else (461 if rgb.size[1] == 512 else 870)
        poses = [(whole, mask, 0, fy)]
    elif layout == "1x4":
        fy = feet if feet is not None else 870
        poses = [(bb, part, 0, fy) for bb, part in components(mask)]
    else:
        fy = feet if feet is not None else 461
        for y0 in (0, H // 2):
            for x0 in (0, W // 2):
                q = (x0, y0, x0 + W // 2, y0 + H // 2)
                bb = mask.crop(q).getbbox()
                if not bb:
                    errors.append(f"quadrant at ({x0},{y0}) is empty")
                    continue
                if bb[0] < 8 or bb[1] < 8 or (W // 2) - bb[2] < 8 or (H // 2) - bb[3] < 8:
                    warns.append(f"quadrant at ({x0},{y0}): figure is within 8px of the quadrant edge")
                poses.append(((x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]), mask, y0, fy))
    expected = 1 if layout == "1x1" else 4
    if len(poses) != expected:
        errors.append(f"found {len(poses)} separate figures, expected {expected} poses "
                      "(poses must be >= 32px apart in every direction; no detached effects / projectiles)")
    stem = os.path.basename(path)
    for i, (bb, pose_mask, y0, fy) in enumerate(poses, 1):
        top, low = bb[1], bb[3] - 1
        rel = low - y0
        msg = f"pose {i}: x {bb[0]}-{bb[2] - 1} (w {bb[2] - bb[0]}), top y={top}, lowest pixel y={low}"
        if layout == "2x2":
            msg += f" (y={rel} in its quadrant)"
        info.append(msg)
        if cell and scale:
            hh, budget = (bb[3] - bb[1]) * scale, cell - 6
            if hh > budget:
                warns.append(f"pose {i}: {bb[3] - bb[1]} px tall = {hh:.1f} game px, over the {budget} px a {cell} px cell holds "
                             f"(the pose is shrunk or the sheet needs a bigger cell): keep raised weapons below this")
        if i == 1 and layout == "1x4" and stem.startswith(("sheet_captain_", "sheet_hero_")) and not stem.endswith("_mounted.png") \
                and not GAIT_STRIP.search(stem) and bb[3] - bb[1] < SMALL_IDLE:
            warns.append(f"pose 1 (idle) is {bb[3] - bb[1]} px tall with hat and weapon; the other captains are 385-440 px. The game converts "
                         "every sheet at one scale, so this character will stand shorter than the rest: keep the head at 110 px and the "
                         "body at guide size - when a wide pose does not fit, change the weapon angle or the stance, never the body size")
        if layout == "1x4" and i in flight:
            if fy - rel < FLIGHT_CLEAR:
                errors.append(f"pose {i} (flight): lowest pixel at y={rel}, {fy - rel} px above the guide line y={fy}; a flight frame "
                              f"needs {FLIGHT_CLEAR} px or more (both feet clearly off the ground)")
            else:
                info.append(f"pose {i} (flight): {fy - rel} px above the guide line (>= {FLIGHT_CLEAR})")
        elif abs(rel - fy) > 3:
            errors.append(f"pose {i}: lowest pixel at y={rel}, expected {fy} (soles on the guide line)")
        elif rel != fy:
            warns.append(f"pose {i}: lowest pixel at y={rel}, guide line is {fy}")
        if report_seams:
            work = report_pose_seams(rgb, pose_mask, bb, i, os.path.splitext(stem)[0], work, warns)
    report_strays(mask, layout, fy, warns)
    trapped = trapped_key_pixels(rgb)
    info.append(f"magenta pixels enclosed by the figure: {trapped} (fine if they are real gaps, e.g. bow and string)")
    return errors, warns, info


def aseprite_runs(exe):
    """False when the executable is missing or cannot start (a fresh cloud container has the wrapper script but no build)."""
    try:
        r = subprocess.run([exe, "--version"], stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and b"seprite" in (r.stdout + r.stderr)


def export_aseprite(src, exe, out_png):
    env = dict(os.environ)
    if os.name != "nt":
        env.pop("DISPLAY", None)
        env.pop("WAYLAND_DISPLAY", None)
    r = subprocess.run([exe, "--batch", src, "--save-as", out_png], stdin=subprocess.DEVNULL,
                       capture_output=True, timeout=180, env=env)
    if r.returncode != 0 or not os.path.exists(out_png):
        raise RuntimeError("Aseprite export failed: " + (r.stderr or r.stdout).decode("utf-8", "replace")[-400:])


ALLOWED_LAYERS = {"Background", "touchup", "original_ref", "head", "torso", "arm_near", "arm_far", "leg_near", "leg_far",
                  "cloth_back", "cloth_front", "weapon", "weapon_back", "weapon_front", "shield", "joints"}


def check_layers(src, exe, base, errors, warns, info):
    """Layer names (all layers, hidden included) and the hidden original_ref layer, which must be the received PNG."""
    env = dict(os.environ)
    if os.name != "nt":
        env.pop("DISPLAY", None); env.pop("WAYLAND_DISPLAY", None)
    r = subprocess.run([exe, "--batch", "--all-layers", "--list-layers", src], stdin=subprocess.DEVNULL, capture_output=True, timeout=120, env=env)
    names = [ln.strip() for ln in r.stdout.decode("utf-8", "replace").splitlines() if ln.strip()]
    if not names:
        warns.append(".aseprite layers could not be listed (Aseprite printed nothing): hidden layers were NOT checked")
        return
    rv = subprocess.run([exe, "--batch", "--list-layers", src], stdin=subprocess.DEVNULL, capture_output=True, timeout=120, env=env)
    visible = [ln.strip() for ln in rv.stdout.decode("utf-8", "replace").splitlines() if ln.strip()]
    # a multiset, not a set: a hidden layer may share its name with a visible one ("touchup" + hidden "touchup")
    hidden = list((Counter(names) - Counter(visible)).elements())
    info.append(".aseprite layers: " + " / ".join(names) + (f"  (hidden: {', '.join(hidden)})" if hidden else ""))
    for n, k in Counter(names).items():
        if k > 1:
            errors.append(f'{k} layers are named "{n}": layer names must be unique (the checks address layers by name)')
    odd = [n for n in names if n not in ALLOWED_LAYERS and not n.startswith("touchup")]
    if odd:
        warns.append("layer names outside the agreed set (see art/requests/pc_notes.md): " + ", ".join(odd))
    bad_hidden = [n for n in hidden if n not in ("original_ref", "joints")]
    if bad_hidden:
        errors.append("hidden layers other than original_ref / joints are not allowed (a hidden layer can carry reference art "
                      "into the repository): " + ", ".join(bad_hidden))
    if "original_ref" in names and base:
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "ref.png")
            subprocess.run([exe, "--batch", "--all-layers", "--layer", "original_ref", src, "--save-as", out],
                           stdin=subprocess.DEVNULL, capture_output=True, timeout=180, env=env)
            if os.path.exists(out):
                ref = Image.new("RGB", (W, H), KEY)
                im = Image.open(out).convert("RGBA")
                ref.paste(im, (0, 0), im)
                got = Image.open(base).convert("RGB")
                diff = sum(1 for p, q in zip(pixels(ref), pixels(got)) if p != q) if ref.size == got.size else -1
                if diff:
                    warns.append(f"hidden layer original_ref differs from the base PNG in {diff} px "
                                 "(an indexed PNG imported with the wrong palette? convert to RGB before importing)")
                else:
                    info.append("hidden layer original_ref == base PNG")


def compare_aseprite(src, exe, png, errors, info):
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "export.png")
        export_aseprite(src, exe, out)
        exp = Image.open(out)
        exp.load()
        if exp.mode in ("RGBA", "LA", "P"):
            a = exp.convert("RGBA").getchannel("A").getextrema()[0]
            if a < 255:
                errors.append(".aseprite export has transparent pixels: fill an opaque #FF00FF 'Background' layer")
        exp = exp.convert("RGB")
        got = Image.open(png).convert("RGB")
        if exp.size != got.size:
            errors.append(f".aseprite canvas {exp.size} differs from the PNG {got.size}")
            return
        diff = sum(1 for p, q in zip(pixels(exp), pixels(got)) if p != q)
        if diff:
            errors.append(f".aseprite export differs from the PNG in {diff} pixels: re-export the PNG from the .aseprite "
                          "(visible layers only; guide layers hidden)")
        else:
            info.append(".aseprite export == PNG (pixel-identical)")


def gait_pair_checks(a, errors, warns, info):
    """--gait-pair: tools/art/gait_body.py on the set (needs numpy); findings go to errors / warns / info"""
    import json
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import gait_body
    except ImportError as e:
        warns.append(f"--gait-pair: body checks not run ({e}; needs numpy)")
        return
    if not os.path.isfile(a.gait_pair):
        errors.append(f"--gait-pair not found: {a.gait_pair}")
        return
    m = re.match(r"(sheet_.+?)_(run|walk)_a\.png$", os.path.basename(a.png))
    sid, pose = a.sheet, None
    if a.pose:
        with open(a.pose, encoding="utf-8") as f:
            pose = json.load(f)
    if m and (not sid or pose is None):
        import receive
        sid = sid or receive.sheet_id(m.group(1)[len("sheet_"):])
        if pose is None:
            try:
                pp, p = receive.gait_pose(m.group(1), m.group(2))
                pose = p if pp else None
            except (OSError, ValueError):
                pose = None
    if not sid:
        errors.append("--gait-pair: cannot tell the sheet from the file name (<sheet stem>_run_a.png): pass --sheet")
        return
    for lv, msg in gait_body.check_set(sid, [a.png, a.gait_pair], pose):
        (errors if lv == "FAIL" else warns if lv == "WARN" else info).append("body: " + msg)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png")
    ap.add_argument("--layout", choices=["1x4", "2x2", "1x1"], default=None,
                    help="1x4 row or 2x2 grid of 768x512 quadrants. Default: the entry for this file in art/requests/phase3.json, else 1x4")
    ap.add_argument("--base", help="touch-ups: the received PNG this was made from - reports what changed and marks failures "
                                   "that the base already had as pre-existing warnings")
    ap.add_argument("--base-rev", help="like --base, but takes the base from git: the version of this PNG at that commit of the "
                                       "repository the PNG is in (e.g. the 바탕 hash of the dot_queue row)")
    ap.add_argument("--spot", help="declared spot colours (tiny must-show colours), e.g. '#d6455d,#f2c94c'. Default: phase3.json 'spots'")
    ap.add_argument("--cell", type=int, help="game cell size for the height budget (default: phase3.json 'cell', else 96)")
    ap.add_argument("--work", help="scratch folder for enlarged seam crops (default: a temp folder when a seam is found)")
    ap.add_argument("--export", action="store_true", help="first export --aseprite to the PNG path (then check it)")
    ap.add_argument("--feet", type=int, default=None, help="soles line (default 870 for 1x4, 461 per 2x2 quadrant)")
    ap.add_argument("--flight-slots", default="",
                    help="1x4 run strips: poses that are flight frames, e.g. '4' (run_<set>_a/_b: R4 / R8). Their lowest pixel must be "
                         f">= {FLIGHT_CLEAR} px above the soles line instead of on it")
    ap.add_argument("--aseprite", help="the .aseprite source to export and compare with the PNG")
    ap.add_argument("--aseprite-exe", default=os.environ.get("ASEPRITE_PATH", "aseprite"),
                    help="Aseprite executable (default: $ASEPRITE_PATH or 'aseprite')")
    ap.add_argument("--gait-pair", help="run sets: the _b strip of the set whose _a strip is the positional PNG - adds the body "
                                        "checks against the idle drawing (tools/art/gait_body.py)")
    ap.add_argument("--sheet", help="--gait-pair: the manifest sheet id (default: from the file name)")
    ap.add_argument("--pose", help="--gait-pair: the request pose.json the set was painted over (default: receive.py gait_pose)")
    a = ap.parse_args()
    try:
        flight = tuple(sorted({int(s) for s in a.flight_slots.replace(" ", "").split(",") if s}))
    except ValueError:
        print(f"--flight-slots must be pose numbers 1-4 separated by commas, got '{a.flight_slots}'")
        return 2
    if any(not 1 <= s <= 4 for s in flight):
        print(f"--flight-slots must be pose numbers 1-4, got '{a.flight_slots}'")
        return 2
    tmp_base = None
    if a.base_rev and not a.base:
        # before --export (a typo in the hash must not cost the PNG); git resolves "./name" in the PNG's own folder, so links,
        # junctions and short paths to the checkout do not matter
        d = os.path.dirname(os.path.abspath(a.png))
        blob = subprocess.run(["git", "-C", d, "show", f"{a.base_rev}:./{os.path.basename(a.png)}"], capture_output=True)
        if blob.returncode != 0:
            print(f"could not read {os.path.basename(a.png)} at {a.base_rev} (in {d})")
            return 2
        fd, tmp_base = tempfile.mkstemp(suffix=".png")
        with os.fdopen(fd, "wb") as f:
            f.write(blob.stdout)
        a.base = tmp_base
    if a.export:
        if not a.aseprite or not os.path.isfile(a.aseprite):
            print("--export needs --aseprite <source>")
            return 2
        try:
            export_aseprite(a.aseprite, a.aseprite_exe, a.png)
        except Exception as e:  # noqa: BLE001
            print("export failed: " + str(e))
            return 2
    if not os.path.isfile(a.png):
        print(f"not found: {a.png}")
        return 2
    req = request_item(a.png)
    src_note = ""
    m_idle = re.match(r"check_(.+)_idle\.png$", os.path.basename(a.png))
    if m_idle:
        # idle check: art/inbox/check_<sheet file stem>_idle.png - settings of the sheet it belongs to, one pose
        req = request_item(m_idle.group(1) + ".png") or request_item("sheet_monster_" + m_idle.group(1) + ".png")
        a.layout = a.layout or "1x1"
    if a.layout is None:
        a.layout = req.get("layout") if req.get("layout") in ("1x4", "2x2") else "1x4"
        src_note = " from phase3.json" if req.get("layout") else ""
    cell = a.cell or req.get("cell") or 96
    scale = req.get("scale") or 0.1654
    if flight and a.layout != "1x4":
        print("--flight-slots applies to 1x4 strips only")
        return 2
    errors, warns, info = check_png(a.png, a.layout, a.feet, cell, scale, flight, report_seams=True, work=a.work)
    unchecked = None
    rgb = Image.open(a.png).convert("RGB")
    spots = [h for h in (a.spot.split(",") if a.spot is not None else (req.get("spots") or [])) if h.strip()]
    if spots:
        check_spots(rgb, spots, errors, warns, info)
    if a.base:
        if not os.path.isfile(a.base):
            errors.append(f"base not found: {a.base}")
        else:
            compare_base(rgb, a.base, a.layout, a.feet, errors, warns, info, flight)
    if a.aseprite:
        if not os.path.isfile(a.aseprite):
            errors.append(f".aseprite not found: {a.aseprite}")
        elif not aseprite_runs(a.aseprite_exe):
            unchecked = f"Aseprite could not be run ({a.aseprite_exe}): the .aseprite source and its layers were NOT checked"
        else:
            try:
                compare_aseprite(a.aseprite, a.aseprite_exe, a.png, errors, info)
                check_layers(a.aseprite, a.aseprite_exe, a.base, errors, warns, info)
            except Exception as e:  # noqa: BLE001
                errors.append(str(e))
    if a.gait_pair:
        gait_pair_checks(a, errors, warns, info)
    print(f"== {a.png} ({a.layout}{src_note}, cell {cell})")
    for m in info:
        print("  info: " + m)
    for m in warns:
        print("  WARN: " + m)
    for m in errors:
        print("  FAIL: " + m)
    if unchecked:
        print("  NOT CHECKED: " + unchecked)
    print("RESULT: " + ("FAIL" if errors else ("PASS (with warnings)" if warns else "PASS")) + (" - PNG only, source not checked" if unchecked else ""))
    if tmp_base:
        os.unlink(tmp_base)
    return 1 if errors else (2 if unchecked else 0)


if __name__ == "__main__":
    sys.exit(main())
