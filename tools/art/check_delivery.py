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
from collections import Counter
import math
import os
import re
import subprocess
import sys
import tempfile

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


def compare_base(rgb, base_path, layout, feet, errors, warns, info):
    """Touch-ups: what changed against the received PNG, and which failures were already there."""
    b_err, _, _ = check_png(base_path, layout, feet)
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


def check_png(path, layout, feet, cell=None, scale=None):
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

    poses = []  # (bbox in canvas coords, quadrant top y, soles line)
    if layout == "1x1":
        fy = feet if feet is not None else (461 if rgb.size[1] == 512 else 870)
        poses = [(whole, 0, fy)]
    elif layout == "1x4":
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
    expected = 1 if layout == "1x1" else 4
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
        if cell and scale:
            hh, budget = (bb[3] - bb[1]) * scale, cell - 6
            if hh > budget:
                warns.append(f"pose {i}: {bb[3] - bb[1]} px tall = {hh:.1f} game px, over the {budget} px a {cell} px cell holds "
                             f"(the pose is shrunk or the sheet needs a bigger cell): keep raised weapons below this")
        stem = os.path.basename(path)
        if i == 1 and layout == "1x4" and stem.startswith(("sheet_captain_", "sheet_hero_")) and not stem.endswith("_mounted.png") \
                and bb[3] - bb[1] < SMALL_IDLE:
            warns.append(f"pose 1 (idle) is {bb[3] - bb[1]} px tall with hat and weapon; the other captains are 385-440 px. The game converts "
                         "every sheet at one scale, so this character will stand shorter than the rest: keep the head at 110 px and the "
                         "body at guide size - when a wide pose does not fit, change the weapon angle or the stance, never the body size")
        if abs(rel - fy) > 3:
            errors.append(f"pose {i}: lowest pixel at y={rel}, expected {fy} (soles on the guide line)")
        elif rel != fy:
            warns.append(f"pose {i}: lowest pixel at y={rel}, guide line is {fy}")
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
    ap.add_argument("--export", action="store_true", help="first export --aseprite to the PNG path (then check it)")
    ap.add_argument("--feet", type=int, default=None, help="soles line (default 870 for 1x4, 461 per 2x2 quadrant)")
    ap.add_argument("--aseprite", help="the .aseprite source to export and compare with the PNG")
    ap.add_argument("--aseprite-exe", default=os.environ.get("ASEPRITE_PATH", "aseprite"),
                    help="Aseprite executable (default: $ASEPRITE_PATH or 'aseprite')")
    a = ap.parse_args()
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
    errors, warns, info = check_png(a.png, a.layout, a.feet, cell, scale)
    unchecked = None
    rgb = Image.open(a.png).convert("RGB")
    spots = [h for h in (a.spot.split(",") if a.spot is not None else (req.get("spots") or [])) if h.strip()]
    if spots:
        check_spots(rgb, spots, errors, warns, info)
    if a.base:
        if not os.path.isfile(a.base):
            errors.append(f"base not found: {a.base}")
        else:
            compare_base(rgb, a.base, a.layout, a.feet, errors, warns, info)
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
