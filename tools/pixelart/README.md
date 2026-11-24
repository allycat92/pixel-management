# tools/pixelart

Procedural pixel-art character generators (Python + Pillow), used as hand-tuned reference
sprites while no image model is available.

```bash
python3 tools/pixelart/baren.py OUT_DIR   # writes OUT_DIR/frames/{idle,walk,attack,hit}_N.png + sheet_preview.png
tools/sprite-gen/.venv/bin/sprite-gen breathe IDLE_DIR OUT --mode pixel   # optional breathing idle
```

`baren.py` — 바렌(검귀): 40x48 cell, idle 4 / walk 4 / attack 5 / hit 1 frames.
Shapes are built from masks (`ellipse`, `poly`, `thick_line`) and shaded by `Canvas.part`
(outline ring, top-left light, bottom-right shade).
