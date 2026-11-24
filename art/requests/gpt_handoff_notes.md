# GPT handoff notes (character sprites)

Work split agreed with the project owner:

| step | who | output |
|---|---|---|
| 1. design draft | NovelAI (`nai-diffusion-4-5-full`, free-tier sizes) | one full-body draft per character |
| 2. pose guides | code (`tools/pixelart/posekit.py`) | 4-head mannequin + stick-figure guide per animation frame |
| 3. final art | **GPT image model** | finished frames / sheet in ONE unified style |
| 4. post-process | `tools/art/` pipeline | pixel cleanup, breathe idle loop, sheet + manifest |

## NovelAI = design drafts ONLY (owner decision)

Final game art **always goes through GPT**. NovelAI output is never a final asset and is never turned into a
game sheet: the owner judged that NovelAI-made "finals" keep coming back with errors, while the GPT step finishes cleanly.

- `tools/art/novelai.py` writes only to `art/concepts/<id>/drafts/nai_<id>_s<seed>.png` (git-ignored) or a scratch
  `--outdir`; it refuses `art/inbox/`, `assets/` and `art/requests/` and never produces a `sheet_*.png` name.
- `tools/art/sheets.py` refuses NovelAI images (NovelAI PNG metadata, files under `art/concepts/`, `art/requests/` or a
  `drafts/` folder, `nai_*` names). `--allow-draft` exists only to test the pipeline and always implies `--dry-run`.
- The owner's chosen draft becomes `art/concepts/<id>/concept_NN.png` and the package's `concept.png` — a design reference
  for GPT, nothing more.

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
- Draft-specific defects to fix, not reproduce: fieldmedic has a white cross on the red apron
  bib / chest (remove it: no cross or symbol anywhere; her armband stays a plain dark-red band);
  fixer holds two daggers (should be one, reverse grip); tactician is too tall for the 4-head spec;
  the mounted lancer draft's horse head looks doubled (draw exactly one).
- The three Baren action drafts (windup/strike/hit) drift in coat length and art style even with
  the same seed — frame-to-frame consistency must come from the pose guides + one style anchor,
  not from the drafts.

## How GPT must unify the style

1. **Style anchor first.** Produce Baren (`captain_blademaster`) first, following his package
   README, `art/STYLE.md` and the target screenshots (not in the repo — the owner attaches them).
   Stop for owner approval. After approval that image is the
   **style anchor**: every other character is drawn to match the anchor's proportions,
   rendering, outline, palette treatment and lighting — not its own draft's.
2. **One spec for everyone:** 4 heads tall, front three-quarter view facing right, light from
   the upper left, muted hue-shifted palette, dark non-black selective outlines, same character
   scale. Head = 110 px; standing height would be 440 px, but the guide idle pose is crouched, so
   idle top-of-head to sole is about 400 px (headgear and weapons are extra and not counted).
   Soles (lowest pixel) on y=870. Only the 1x4 row is asked for (no 2x2 grid, no single pose).
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
| `guide_strip.png` | the four guides laid out EXACTLY as the deliverable: 1536x1024, flat #FF00FF, soles on y=870 (85%), 110 px per head for every character (idle ≈ 400 px ≈ 39%), >= 32 px of magenta between figures (in any direction) and from the border |
| `README.md` | the English prompt block for GPT first (character / colours / fix / poses, then references and the common rules), then a Korean summary for the owner and the file list to attach in a chat |

- The old "figure about 55% of the height" could not fit four wide stances with weapons in 1536 px;
  the guide strip (≈40%) is the size reference now. The pipeline normalises the idle height to 64 px anyway.
- Weapons use the generic posekit mannequin with the closest weapon (per-class / per-character pose kits are deferred);
  the README says what the placeholder becomes (tower shield, mace, cane, lance ...). Fixer's guide draws its one reverse-grip dagger.
- Key poses: idle is the posekit frame; wind-up / strike / hit mostly come from `KEY_POSES` in `handoff.py`
  (wind-up = weight back and more upright, strike = step-in lunge with the arms extended, hit = torso thrown back,
  weight on the rear leg, weapon dropped), so the four poses also differ in the legs and still read at 64 px.
- Branches: every reference is read from `claude/dot-fantasy-management-game-saupju` (it must be pushed first);
  results go ONLY to the `art-inbox` branch (its own older `art/STYLE.md` and requests are not the rules).
- Order: Baren (anchor, wait for approval) → ironwall, tactician, lancer, huntress, hedgemage, fieldmedic, fixer, veteran
  → optional lancer mounted sheet (`sheet_captain_lancer_mounted.png`, 2x2 grid, wider cell, not used by the game yet;
  the horse must have exactly one head) → Felix recolour (message C) → after the owner picks NovelAI drafts: the five
  generic classes (message D) and the first eight monsters (message E) → later groups (promoted classes, heroes, the other
  monsters and bosses, the other captains).
- The copy-paste messages for the image agent are in `art/requests/phase3_gpt.md`.

## Magenta rule (every sheet)

The background key is #FF00FF and the pipeline deletes every colour near it. Felix's first delivery saved his lit robe and
hat exactly as #FF00FF (the palette reduction merged them with the background), so the robe came out full of holes.
Every figure colour must stay at RGB distance >= 150 from #FF00FF (`sqrt((255-R)^2 + G^2 + (255-B)^2)`): no hot pink,
magenta or bright violet; purples stay dark blue-purple (#5a4a7a). Reduce the palette of the figure only, never merging
a figure colour into the background colour. The rule is in every package README (DELIVERABLE + SELF-CHECK).

## Generic class sheets (`class_<key>`, message D): key colours

One sheet per base class (warrior, archer, mage, cleric, rogue) is shared by every nameless mercenary and faction
soldier, friend and foe; promoted classes fall back to it. The engine recolours the uniform per faction by replacing
EXACT colours (`js/battle.js` `sheetRecolor`: key -> faction colour x key luminance / mean luminance of that role's keys).

- outfit keys (tabard / robe and high collar / hooded tunic and mask / cowl and veil / hood and cape, the warrior's shield face), dark to light:
  `#263459` `#394b78` `#52679c` `#7489be`
- accent keys (trim, sash, hood / cowl edge, hat band, the cleric's chest disc, the rogue's scarf), dark to light:
  `#3f7a6c` `#5ea590` `#96d1bb`
- flat fills only on those areas (no dithering, gradients, texture or in-between shades); the seven keys appear nowhere
  else, and nothing else on the figure is blue, slate, teal or mint (steel is neutral grey, leather and wood warm brown,
  other shadows warm or neutral - this overrides the general "shadows toward purple/blue" rule for these sheets).
- no emblem or heraldry (the faction colour comes from the keys).
- **faces covered (owner request):** one generic sheet stands for many different people, so the base-class outfits
  hide or shade the face where it suits the class — warrior: closed helm, visor down (eye slit only); archer: hood up +
  cloth mask over the lower face; mage: hat brim pulled low + high collar, face in shadow; cleric: deep cowl + veil, face
  shadowed; rogue: deep hood (+ scarf), face shadowed. Same coverage in all four poses (nothing slips in the hit pose);
  the face shadow is a warm / neutral dark, never blue or a key colour; hood / mask / cowl / veil / collar cloth uses the
  outfit keys. Later promoted / master classes: only where natural for the class — don't force it.
- code side: `sheets.py` reads `tint` from `phase3.json`, snaps colours within RGB distance 34 of a key back to the key at
  full resolution (non-key colours never become keys), writes `preview_tint_x4.png` (test recolour) and registers the keys
  with `register_sheet.py --tint-outfit/--tint-accent`.

## First monster batch (`monster_<key>`, message E)

The eight most frequent non-boss monsters (counted from `Battle.plan` over simulated contracts; evidence in
`phase3_gpt.md`): skeleton soldier, wild wolf, desert bandit, harpy, bandit, gargoyle, giant spider, wraith.

- Same pixel scale as the humans (guide head 110 px) - monsters are never drawn bigger to fill the frame.
- Humanoids (skeleton, desert bandit, bandit) use the posekit guide strip like the captains.
- Non-humanoids have no mannequin: the README gives a design brief (silhouette, size, colours, attack) and four
  descriptive poses; `guide_layout.png` shows the layout (2x2 quadrants for the wide wolf / harpy / gargoyle / spider,
  lowest pixel on y=461 of each quadrant; the 1x4 row for the wraith) with a size box per pose, and `guide_scale.png`
  shows the idle box next to a grey 4-head human at the same scale. Boxes, lines, labels and the grey human are guide-only.
- Ranged monsters (harpy, gargoyle, wraith) get a cast / shriek pose; the engine draws the projectile.

Both batches wait for the owner's NovelAI design picks (`concept.png` is missing until then; the README says so).
