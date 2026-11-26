"""Build the run-drawing guide images for art/requests/gait/run__<id>/ (PIL + numpy).

Usage: python3 tools/art/run_request_guides.py class_warrior captain_shadowqueen.

guide_run_a.png / guide_run_b.png = exact copies of the accepted run mannequin strips (v2).
size_run_a.png / size_run_b.png  = 1920x1024: a SIZE panel (the character's accepted idle, faint, with the mannequin's
    first frame of that strip outlined over it at the same scale) + the 4 mannequin frames in their delivery slots, with the
    floor line y=870, the hip column x=192 of each slot, the 32-px border band and frame labels.
"""
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import os
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/"
MANN = REPO + "art/requests/guides/run_base/v2/run_base_%s.png"
MAG = np.array([255, 0, 255])
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CHARS = {
    # id: (sheet stem, idle x-range in the sheet, idle hip column in the sheet, display name)
    "class_warrior": ("sheet_class_warrior", (34, 324), 180, "class warrior"),
    "captain_shadowqueen": ("sheet_captain_shadowqueen", (59, 305), 195, "Nikla"),
}
LABELS = {
    "a": ["R1 contact (near foot)", "R2 catch / down", "R3 push-off", "R4 FLIGHT (both feet up)"],
    "b": ["R5 contact (far foot)", "R6 catch / down", "R7 push-off", "R8 FLIGHT (both feet up)"],
}


def fig_mask(rgb):
    return np.sqrt(((rgb.astype(int) - MAG) ** 2).sum(-1)) > 60


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


def build(cid, outdir):
    stem, (ix0, ix1), hip, name = CHARS[cid]
    sheet = np.asarray(Image.open(REPO + "art/inbox/%s.png" % stem).convert("RGB"))
    idle = sheet[:, ix0:ix1 + 1]
    imask = fig_mask(idle)
    f_reg = ImageFont.truetype(FONT, 22)
    f_small = ImageFont.truetype(FONT, 18)
    f_big = ImageFont.truetype(FONTB, 28)
    for half in "ab":
        shutil.copyfile(MANN % half, outdir + "/guide_run_%s.png" % half)
        strip = np.asarray(Image.open(MANN % half).convert("RGB"))
        W = 384 * 5
        canvas = np.zeros((1024, W, 3), np.uint8)
        canvas[:] = MAG
        # SIZE panel (slot 0): faint idle, hip column on x=192, soles on y=870 (the sheet already has its soles on 870)
        ox = 192 - hip + ix0
        faint = (idle.astype(float) * 0.45 + np.array([235, 235, 235]) * 0.55).astype(np.uint8)
        sub = canvas[:, ox:ox + idle.shape[1]]
        sub[imask] = faint[imask]
        # mannequin first frame of this strip as a cyan outline over it
        m0 = fig_mask(strip[:, 0:384])
        ol = outline(m0)
        canvas[:, 0:384][ol] = (0, 200, 255)
        # annotations first (behind the figures), then the 4 mannequin frames pasted on top in slots 1..4
        im = Image.fromarray(canvas)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 300, 383, 1023], outline=(255, 255, 255), width=3)
        for s in range(4):
            x0 = 384 + s * 384
            d.rectangle([x0, 300, x0 + 383, 1023], outline=(60, 0, 60), width=1)
            dashed_v(d, x0 + 32, 345, 925, (150, 60, 150), dash=4, gap=8, w=1)
            dashed_v(d, x0 + 351, 345, 925, (150, 60, 150), dash=4, gap=8, w=1)
            dashed_v(d, x0 + 192, 345, 925, (255, 255, 255), dash=8, gap=8, w=1)
            if s == 3:
                d.line([(x0 + 40, 852), (x0 + 344, 852)], fill=(255, 255, 0), width=1)
        dashed_h(d, 0, W, 871, (255, 255, 255), dash=14, gap=8, w=2)
        arr = np.asarray(im).copy()
        smask = fig_mask(strip)
        arr[:, 384:][smask] = strip[smask]
        im = Image.fromarray(arr)
        d = ImageDraw.Draw(im)
        for s in range(4):
            x0 = 384 + s * 384
            d.text((x0 + 10, 310), LABELS[half][s], font=f_reg, fill=(255, 255, 255))
            if s == 3:
                d.text((x0 + 40, 885), "lowest pixel at or above y=852", font=f_small, fill=(255, 255, 0))
                d.text((x0 + 40, 907), "(mannequin: %d px clear)" % (23 if half == "a" else 24), font=f_small, fill=(255, 255, 0))
        d.text((392, 960), "white dashed line: floor y=870 (soles of the standing foot, R1-R3 / R5-R7)", font=f_small, fill=(255, 255, 255))
        d.text((392, 985), "white dashes in each slot: hip column x=192  |  purple dashes: x=32 and x=351 - keep every pixel between them",
               font=f_small, fill=(255, 255, 255))
        d.text((10, 945), "faint = accepted idle (its own", font=f_small, fill=(255, 255, 255))
        d.text((10, 967), "head/body size); cyan = mannequin", font=f_small, fill=(255, 255, 255))
        d.text((10, 989), "(pose and placement only)", font=f_small, fill=(255, 255, 255))
        # header
        d.text((14, 20), "%s RUN - strip %s  (frames %s)" % (name.upper(), half.upper(), "R1-R4" if half == "a" else "R5-R8"),
               font=f_big, fill=(255, 255, 255))
        d.text((14, 62), "LEFT PANEL (not delivered): the accepted idle from art/inbox/%s.png, faint, with the cyan outline of "
               "the run mannequin's %s on top." % (stem, "R1" if half == "a" else "R5"), font=f_reg, fill=(255, 255, 255))
        d.text((14, 92), "Same scale: soles on y=870, hip column x=192, about the same height. Draw the character at the size of its "
               "idle (its own head, torso, boots) - never shrink it.", font=f_reg, fill=(255, 255, 255))
        d.text((14, 122), "RIGHT 4 SLOTS = the delivery layout (1536x1024 = this image without the left panel). Follow each "
               "mannequin's legs, torso lean and arm swing.", font=f_reg, fill=(255, 255, 255))
        d.text((14, 152), "The guide lines and text are for reading only - the delivered strip has nothing but the character "
               "on flat #FF00FF.", font=f_reg, fill=(255, 255, 255))
        d.text((10, 310), "SIZE (idle + mannequin)", font=f_reg, fill=(255, 255, 255))
        im.save(outdir + "/size_run_%s.png" % half, optimize=True)


def main():
    for cid in sys.argv[1:]:
        build(cid, REPO + "art/requests/gait/run__%s" % cid)


if __name__ == "__main__":
    main()
