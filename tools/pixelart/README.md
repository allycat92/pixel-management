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

## posekit.py — pose / proportion guides for image models

Procedural pixel shading is not good enough for final art, so `posekit.py` only builds the
**skeleton**: a flat-shaded wooden-mannequin-style figure (4 heads tall by default, front
three-quarter view facing right, weapon in hand) posed through the game's animation set.
The guide goes to an image model (NovelAI img2img now, GPT image generation later), which keeps
the pose and proportions and paints the character on top.

```bash
python3 tools/pixelart/posekit.py OUT_DIR [--heads 4] [--weapon katana] [--frames idle_0,attack_2,...] [--check]
# weapons: katana (default) | sword_shield | spear | staff | bow | none
```

Frames: `idle_0..3`, `walk_0..3`, `attack_0..4` (anticipation, wind-up, strike, follow-through,
recover), `hit_0`, `cast_0..2`. Per frame, on a flat `#FF00FF` background:

| file | size | use |
| --- | --- | --- |
| `guide_<frame>.png` | 832x1216 | img2img init image: colour-blocked mannequin, 2 tones per part, light from the upper left, near limbs lighter than far limbs, feet at y≈1119 (92%), idle body ≈70-73% of the height (head = exactly 1/N of the standing height: hair top to chin is 1 head unit) |
| `stick_<frame>.png` | 832x1216 | OpenPose (COCO-18) stick figure on black, plus a grey weapon line (`--no-stick-weapon` drops it). The near / screen-left side is the character's RIGHT |
| `small_<frame>.png` | 80x80 | preview cell, feet at y=76 |

plus `sheet.png` (all guides), `anim.gif` (every animation looping side by side) and
`anim_<anim>.gif`; `--check` also writes `stand.png` with a head-unit ruler.

Guarantees (each run prints violations; expected `0 check warnings`): bone lengths are identical
in every frame (2-bone IK for arms and legs), planted feet sit on the y=0 baseline, hands are
locked to points on the weapon grip, weapon tip / butt never below the floor, one scale for the whole set (only the x origin may slide
when a weapon would leave the canvas). Deterministic; the fit never depends on `--frames`.

### Intended use

- **NovelAI img2img**: `action: "img2img"`, `parameters.image` = base64 of `guide_<frame>.png`,
  `width`/`height` = 832/1216 (same as the guide), `strength` 0.6-0.75 (lower keeps the pose more
  strictly, higher repaints more), `noise` 0. Put the character description (hair, headband,
  clothes, colours, "pixel art, full body, simple magenta background") in the prompt; the guide
  only fixes the pose, proportions and the light direction. Mannequin colours are mid-value
  placeholders: if the outfit colour matters, say it in the prompt.
- **GPT image generation**: attach `guide_<frame>.png` (optionally also the stick image and the
  approved character art) with "match this pose and proportions exactly; redraw it as <character>".
- Generate the idle frame first, then reuse its look (same seed / reference image) for the other frames.

Known limits: the figure is a 2D mannequin (no real 3D rotation, so twisting poses are faked by
moving the shoulders); hair, clothing, capes and smears are left to the model; the eye marks only
indicate facing; long weapons make the whole set a little smaller (idle body: katana / sword_shield 73%,
staff 72%, bow 70%, spear 70%), since one scale must fit the widest strike / thrust frame.

## Deferred: per-class / per-character pose kits

Agreed to postpone (long task). The current `posekit.py` is one generic 4-head mannequin with
weapon variants. Later it should get:
- per-class pose sets (warrior/archer/cleric/mage/rogue and their promotion lines: stance,
  weapon handling, cast gestures, signature skill poses);
- per-character overrides for the unique captains/heroes (body type, height, bulk, signature
  weapon and skill poses, cape/hair secondary motion hints);
- body-type parameters (heavy armour, slight caster, old veteran) instead of one build.
Until then, use the generic guides and describe class-specific details in the GPT request.
