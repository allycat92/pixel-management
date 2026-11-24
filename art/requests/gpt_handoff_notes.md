# GPT handoff notes (character sprites)

Work split agreed with the project owner:

| step | who | output |
|---|---|---|
| 1. design draft | NovelAI (`nai-diffusion-4-5-full`, free-tier sizes) | one full-body draft per character |
| 2. pose guides | code (`tools/pixelart/posekit.py`) | 4-head mannequin + stick-figure guide per animation frame |
| 3. final art | **GPT image model** | finished frames / sheet in ONE unified style |
| 4. post-process | `tools/art/` pipeline | pixel cleanup, breathe idle loop, sheet + manifest |

## IMPORTANT: the NovelAI drafts are NOT consistent with each other

The owner reviewed the drafts and judged that, to a human eye, they do **not** read as one
unified art style. Use them **only as design references**, never as style references:

- **Take from a draft:** costume pieces, colour scheme, hair, face marks (scars, beard),
  headgear, weapon and shield type, silhouette idea, personality of the pose.
- **Do NOT copy from a draft:** proportions, rendering/shading technique, outline weight,
  saturation, lighting, level of detail. These vary wildly between drafts.

Known inconsistencies in the current drafts (`art/requests/phase3/<id>/concept.png`):

- Proportions range from ~4 heads (Baren) to ~5 (ironwall, veteran) to ~6 (tactician).
- Rendering ranges from crisp pixel art (Baren base, veteran) to flat anime cel shading
  (Baren hit pose) and comic-style lineart.
- Saturation/brightness differ: hedgemage's bright yellow trim, fieldmedic's near-white coat,
  fixer's near-black outfit that vanishes on the dark battlefield.
- Draft-specific defects to fix, not reproduce: fieldmedic has a small white cross on the
  armband (should be a plain dark-red armband); fixer holds two daggers (should be one,
  reverse grip); tactician is too tall for the 4-head spec.
- The three Baren action drafts (windup/strike/hit) drift in coat length and art style even with
  the same seed — frame-to-frame consistency must come from the pose guides + one style anchor,
  not from the drafts.

## How GPT must unify the style

1. **Style anchor first.** Produce Baren (`captain_blademaster`) first, following `art/STYLE.md`
   and the target screenshots. Stop for owner approval. After approval that image is the
   **style anchor**: every other character is drawn to match the anchor's proportions,
   rendering, outline, palette treatment and lighting — not its own draft's.
2. **One spec for everyone:** 4 heads tall, front three-quarter view facing right, light from
   the upper left, muted hue-shifted palette, dark non-black selective outlines, same character
   scale, feet on the common baseline of the guide.
3. **Poses come from posekit guides only:** match the guide's pose, limb lengths and proportions
   exactly; the draft only says what the character wears and carries.
4. **Readability on the dark battlefield:** very dark or very bright outfits get a rim light /
   lighter outline so they read at 1x game scale.
5. **Per-character message** = style anchor image + that character's concept draft + its pose
   guides + the per-character notes (what to keep, what to fix) from its `README.md`.

## Per-character packages (built by code)

`python3 tools/art/handoff.py` writes one folder per character, `art/requests/phase3/<id>/`:

| file | what it is |
|---|---|
| `concept.png` | the owner's chosen NovelAI draft — DESIGN ONLY (Baren also `concept_pixel.png` = #8, how simple the shapes must stay) |
| `portrait.png` | the approved portrait — face and hair only |
| `guide_1_idle.png` .. `guide_4_hit.png` | posekit 4-head mannequin, 832x1216, one per key pose |
| `guide_strip.png` | the four guides laid out EXACTLY as the deliverable: 1536x1024, flat #FF00FF, feet on y=870 (85%), 110 px per head for every character (idle ≈ 400 px ≈ 39%), figures never touching |
| `README.md` | Korean summary for the owner + the English prompt block for GPT (keep / fix / do-not-copy / poses / deliverable / self-check) |

- The old "figure about 55% of the height" could not fit four wide stances with weapons in 1536 px;
  the guide strip (≈40%) is the size reference now. The pipeline normalises the idle height to 64 px anyway.
- Weapons use the generic posekit mannequin with the closest weapon (per-class / per-character pose kits are deferred);
  the README says what the placeholder becomes (tower shield, mace, cane, dagger ...).
- Order: Baren (anchor, wait for approval) → ironwall, tactician, lancer, huntress, hedgemage, fieldmedic, fixer, veteran
  → optional lancer mounted sheet (`sheet_captain_lancer_mounted.png`, 2x2 grid, wider cell, not used by the game yet;
  the horse must have exactly one head) → later groups (classes, heroes, monsters, other captains) after the nine.
- The copy-paste messages for the image agent are in `art/requests/phase3_gpt.md`.
