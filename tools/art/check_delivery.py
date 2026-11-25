#!/usr/bin/env python3
"""Self-check a battle-sheet delivery before it is pushed to art-inbox (and on receipt).

Checks the dot_queue / package README spec for a 1x4 strip (or a 2x2 grid):
  * 1536x1024, flat #FF00FF background, no transparency
  * every figure colour at RGB distance >= 150 from #FF00FF (>= 170 recommended)
  * figure colour count (~40 with hard edges; many more = soft / anti-aliased edges)
  * pose count, lowest pixel of each pose on y=870 (2x2: y=461 inside each 768x512 quadrant)
  * >= 32 px of magenta between poses and to the border
Optionally exports an .aseprite source with Aseprite (--aseprite) and checks that it equals the PNG.

Usage:
  python3 tools/art/check_delivery.py art/inbox/sheet_hero_lyra.png
  python3 tools/art/check_delivery.py art/inbox/sheet_hero_lyra.png \
      --aseprite art/inbox/aseprite/sheet_hero_lyra.aseprite --aseprite-exe "C:/Program Files/Aseprite/Aseprite.exe"
  (Windows without a system Python:  uv run --no-project --with pillow python tools\\art\\check_delivery.py ...)

Exit code 0 = pass (warnings allowed), 1 = fail, 2 = could not run.
Only Pillow and the standard library; the Aseprite call uses an argument list (no shell).
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
except ImportError:  # pragma: no cover
    print("Pillow is missing: pip install pillow  (or: uv run --no-project --with pillow python ...)")
    sys.exit(2)

KEY = (255, 0, 255)
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


def check_png(path, layout, feet):
    errors, warns, info = [], [], []
    rgb = load_rgb(path, errors)
    if rgb.size != (W, H):
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

    if rgb.size != (W, H):
        return errors, warns, info
    mask = Image.new("1", rgb.size, 0)
    mask.putdata([0 if c == KEY else 1 for c in pixels(rgb)])
    whole = mask.getbbox()
    if not whole:
        errors.append("no figure pixels at all")
        return errors, warns, info
    l, t, r, b = whole
    if l < GAP or t < GAP or W - r < GAP or H - b < GAP:
        errors.append(f"figure bbox {whole} is closer than {GAP}px to the border")

    poses = []  # (bbox in canvas coords, quadrant top y, soles line)
    if layout == "1x4":
        fy = feet if feet is not None else 870
        poses = [(bb, 0, fy) for bb, _ in components(mask)]
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
                poses.append(((x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]), y0, fy))
    expected = 4
    if len(poses) != expected:
        errors.append(f"found {len(poses)} separate figures, expected {expected} poses "
                      "(poses must be >= 32px apart in every direction; no detached effects / projectiles)")
    for i, (bb, y0, fy) in enumerate(poses, 1):
        top, low = bb[1], bb[3] - 1
        rel = low - y0
        msg = f"pose {i}: x {bb[0]}-{bb[2] - 1} (w {bb[2] - bb[0]}), top y={top}, lowest pixel y={low}"
        if layout == "2x2":
            msg += f" (y={rel} in its quadrant)"
        info.append(msg)
        if abs(rel - fy) > 3:
            errors.append(f"pose {i}: lowest pixel at y={rel}, expected {fy} (soles on the guide line)")
        elif rel != fy:
            warns.append(f"pose {i}: lowest pixel at y={rel}, guide line is {fy}")
    trapped = trapped_key_pixels(rgb)
    info.append(f"magenta pixels enclosed by the figure: {trapped} (fine if they are real gaps, e.g. bow and string)")
    return errors, warns, info


def export_aseprite(src, exe, out_png):
    env = dict(os.environ)
    if os.name != "nt":
        env.pop("DISPLAY", None)
        env.pop("WAYLAND_DISPLAY", None)
    r = subprocess.run([exe, "--batch", src, "--save-as", out_png], stdin=subprocess.DEVNULL,
                       capture_output=True, timeout=180, env=env)
    if r.returncode != 0 or not os.path.exists(out_png):
        raise RuntimeError("Aseprite export failed: " + (r.stderr or r.stdout).decode("utf-8", "replace")[-400:])


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png")
    ap.add_argument("--layout", choices=["1x4", "2x2"], default="1x4",
                    help="1x4 row (default) or 2x2 grid of 768x512 quadrants (the package README DELIVERABLE decides)")
    ap.add_argument("--feet", type=int, default=None, help="soles line (default 870 for 1x4, 461 per 2x2 quadrant)")
    ap.add_argument("--aseprite", help="the .aseprite source to export and compare with the PNG")
    ap.add_argument("--aseprite-exe", default=os.environ.get("ASEPRITE_PATH", "aseprite"),
                    help="Aseprite executable (default: $ASEPRITE_PATH or 'aseprite')")
    a = ap.parse_args()
    if not os.path.isfile(a.png):
        print(f"not found: {a.png}")
        return 2
    errors, warns, info = check_png(a.png, a.layout, a.feet)
    if a.aseprite:
        if not os.path.isfile(a.aseprite):
            errors.append(f".aseprite not found: {a.aseprite}")
        else:
            try:
                compare_aseprite(a.aseprite, a.aseprite_exe, a.png, errors, info)
            except Exception as e:  # noqa: BLE001
                errors.append(str(e))
    print(f"== {a.png} ({a.layout})")
    for m in info:
        print("  info: " + m)
    for m in warns:
        print("  WARN: " + m)
    for m in errors:
        print("  FAIL: " + m)
    print("RESULT: " + ("FAIL" if errors else ("PASS (with warnings)" if warns else "PASS")))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
