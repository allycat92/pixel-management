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

## Do NOT run without the user's explicit request

- Any generation command (`gen`, `pixel-draw`, `grok`, `video`, `reroll`, ...): they call paid or
  subscription image APIs, and fall back to `ANTHROPIC_API_KEY` / `XAI_API_KEY` billing silently.
- `serve` / curator / composer local servers (no CSRF/Origin checks).
- `rife install` (downloads a native binary), `face-bake` (executes JS from the pack folder).
- Never set `SPRITE_GEN_*_BASE_URL` (sends tokens to that host).

## Game conventions

- Battle characters: ~40x48 px cell, 2.5-head chibi, dark 1px outline, light from top-left.
  See `art/STYLE.md` and `tools/pixelart/` for the procedural reference character.
- Final assets go under `assets/art/` and are registered in `assets/art/manifest.json`.
