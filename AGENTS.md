# Notes for coding agents (Codex, Claude, ...)

- Game: vanilla HTML/CSS/JS. Open `index.html` via any static server (`python3 -m http.server`).
- Art workflow: see `art/README.md` (image agents draw and push PNGs to the `art-inbox` branch;
  `tools/art/process.py` converts them into `assets/art/`).
- Sprite post-processing: `.claude/skills/sprite-gen/SKILL.md` — vendored `tools/sprite-gen`,
  **offline commands only**; no generation / server / rife / face-bake commands, no API keys.
- Procedural pixel characters: `tools/pixelart/` (`python3 tools/pixelart/baren.py OUT_DIR`).
- Aseprite: never commit Aseprite binaries (EULA forbids redistribution). Build notes only.
