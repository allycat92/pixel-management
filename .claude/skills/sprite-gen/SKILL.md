---
name: sprite-gen
description: Post-process pixel-art sprite frames for this game with the vendored sprite-gen CLI (offline only) - breathing idle loops, sheet slicing, cutout, atlas/GIF composition, recolor, Aseprite export. Use when turning character frames (hand-drawn, tools/pixelart output, or images from the art inbox) into animation assets.
---

# sprite-gen (offline commands only)

Vendored copy: `tools/sprite-gen` (sprite-gen 4.3.0, Apache-2.0, upstream github.com/aldegad/sprite-gen).
Dependencies: Pillow + NumPy only.

## Setup (once per container)

```bash
python3 -m venv tools/sprite-gen/.venv
tools/sprite-gen/.venv/bin/pip install -e tools/sprite-gen
SG=tools/sprite-gen/.venv/bin/sprite-gen
```

## Allowed commands

| command | use |
|---|---|
| `breathe FRAMES OUT --mode pixel` | lay a breathing loop over idle frames (needs ~2px empty margin above the sprite) |
| `slice-sheet` / `unpack-atlas` | cut a sheet image into frames |
| `cutout` / `extract` | remove background, isolate a sprite |
| `compose-atlas` / `compose-gif` | pack frames into an atlas or transparent GIF |
| `recolor` | palette swap (faction / class variants) |
| `export-aseprite` | write a layered .aseprite file |

Run `$SG <command> --help` before use; messages are partly Korean.

## Battle sheet pipeline (uses `breathe` for you)

`python3 tools/art/sheets.py [art/inbox/sheet_<kind>_<key>.png ...] [--dry-run] [--work DIR] [--aseprite OUT]`
- input: 1x4 key-pose strip (idle, wind-up, strike, hit), 2x2 grid, or one full-body pose; flat #FF00FF or transparent bg
- per pose: chroma matte + despill, one scale for all poses (idle body -> 64px), premultiplied box downscale,
  alpha > 0.45, shared ~40-colour palette, 1px dark edge, 80x80 cell with feet at (40,76)
- idle loop: `breathe --mode pixel` over 4 copies of the idle cell (falls back to a 1px bob without the venv)
- writes sheet png + Aseprite json-array (tags idle/attack/hit) and calls `tools/art/register_sheet.py`
- check `preview_x4.png` in the work dir before committing

## NovelAI (separate tool, not sprite-gen)

`tools/art/novelai.py` is allowed **when the user asks for generation**: free tier only by default
(<= 1024x1024 area, <= 28 steps, 1 sample, `--max` 2 images per run), prompts from `art/requests/phase3.json`.
sprite-gen's own generation commands stay forbidden.

## Do NOT run without the user's explicit request

- Any generation command (`gen`, `pixel-draw`, `grok`, `video`, `reroll`, ...): they call paid or
  subscription image APIs, and fall back to `ANTHROPIC_API_KEY` / `XAI_API_KEY` billing silently.
- `serve` / curator / composer local servers (no CSRF/Origin checks).
- `rife install` (downloads a native binary), `face-bake` (executes JS from the pack folder).
- Never set `SPRITE_GEN_*_BASE_URL` (sends tokens to that host).

## Game conventions

- Battle characters: 80x80 cell, body ~64px, feet at (40,76), 4 heads tall (not chibi; see art/STYLE.md / art/requests/gpt_handoff_notes.md), front 3/4 view facing right,
  muted hue-shifted palette, dark non-black selective outline, rim light. See `art/STYLE.md` (전투 캐릭터).
  Older procedural reference (48x56): `tools/pixelart/`.
- Final assets go under `assets/art/` and are registered in `assets/art/manifest.json`.
