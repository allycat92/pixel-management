# GPT handoff notes (character sprites)

## Rules changed (newest first — read this list every time)

- 2026-11-26 **Body size is fixed — do not shrink the figure to fit the width**: Crimson (idle 367 px) and Bjorn (373 px) arrived 8-12% smaller than
  the other captains (385-440 px, hat and weapon included) after a "layout width correction". The game converts every sheet at one scale, so they
  stood a head shorter; we fixed those two in conversion. From now on: head 110 px, idle top-of-head to sole about 400 px. When a wide pose does not
  fit between its neighbours, change the weapon angle or narrow the stance. `check_delivery.py` now prints a WARN when the idle pose is under 380 px.
- 2026-11-26 **One bad pose does not block a sheet**: if three poses are right and one misses a rule you cannot fix with your tools
  (e.g. a weapon overlapping the body), DELIVER the sheet and name that pose under DEVIATIONS. The PC Aseprite session moves or repaints
  the prop in that pose. Report 막힘 only when the whole sheet cannot be made (a reference will not load, the request contradicts itself).
- 2026-11-26 **How work arrives**: one standing instruction (`art/requests/GPT_STANDING.md`) + `dot_queue.md` section "지금 차례". No per-item messages.
  NOTES sections use the template there (CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS).
- 2026-11-26 **References must load**: use the `*_800.jpg` copies. If a design reference (portrait, concept) does not load, do not draw from the text — report "막힘".
- 2026-11-26 **MUST SURVIVE beats FIX**: what the owner liked in a draft (MUST SURVIVE / "FROM concept TAKE") wins over Claude's readability suggestions.
  The first spider redraw failed because our FIX notes ("smooth carapace", "keep grey legs") erased the draft's hair and dark legs.
- 2026-11-26 **Cell budget**: each README states the highest allowed pixel (cell 96: nothing above y=340; cell 112: y=245). Tilt or lower a raised weapon; never shrink the figure.
- 2026-11-26 **Idle-check first** for creatures without a mannequin, bosses, and redraws after an owner rejection: one idle pose (`check_<stem>_idle.png`), then the rest.
- 2026-11-25 **Spot colours**: tiny must-show colours (eyes, gems) vanish at 1/6 scale unless declared. Paint them >= 60 RGB away from every other colour, >= 14 px wide at source, and list them in NOTES as `SPOT: #rrggbb`.
- 2026-11-25 **Weapon decisions are final when marked CONFIRMED** (they may contradict the portrait: the owner chose the skill/story weapon three times out of three).
- 2026-11-25 **Weapon / key prop outside the body silhouette** in every pose, over the background, with a 1 px dark outline (Lyra's dagger vanished at 64 px).
- 2026-11-25 **Crisp pixels**: about 40 colours, hard edges, no blending into the background (Kai's first sheet had 110k colours).
- 2026-11-25 **Magenta distance**: every figure colour >= 170 from #FF00FF (hard minimum 150).
- 2026-11-25 **Self-check tool**: `python3 tools/art/check_delivery.py <png>` (finds layout / cell / spots itself). Your numbers have matched ours exactly; visual "looks fine at 64 px" claims have not — list risks instead.

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
- Generic classes and the first eight monsters: each chosen draft's own defects are listed in its package README
  (`FROM concept.png ... TAKE` + the `the draft ...` lines at the end of FIX, from `draft=` in `handoff.py`). The big ones:
  the class drafts' slate / teal / cyan cloth is only the key-colour SLOT (paint the exact key ramps) and their faces are flat
  black voids (paint a warm-dark shadow); the mage draft has a second crystal floating over its hand, the cleric a glowing
  white starburst and a morning star, the rogue a hunched body with the head sunk into the chest; the skeleton, bandit and
  desert-bandit designs had duplicated-head siblings (exactly one head), the bandit draft holds a second handle and no
  buckler, the desert bandit a huge sickle blade; the harpy draft is too revealing (cover the whole torso with feathers /
  leather, two wings only), the giant spider is near-black (exactly 8 legs + rim light), the gargoyle's wings fill the canvas.
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
   Soles (lowest pixel) on y=870. Layout: the 1x4 row for captains, generic classes and the humanoid / wraith monsters
   (no single pose); a 2x2 grid of 768x512 quadrants only where the package README's DELIVERABLE says so (the wide
   wolf, harpy, gargoyle and giant spider, and the optional mounted lancer). The README DELIVERABLE decides.
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
  the horse must have exactly one head) → Felix recolour (message C, wait for the owner's approval) → the five generic
  classes (message D) and the first eight monsters (message E): the owner's NovelAI design picks are in, every package has
  its `concept.png` and draft notes → later groups (promoted classes, heroes, the other monsters and bosses, the other captains).
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

- outfit keys (tabard / the mage's hat, robe with shoulder capelet and high collar / hooded tunic and mask, the hood's edge
  around the face included / cowl and veil / hood, cape and the rogue's scarf, the warrior's shield face), dark to light:
  `#263459` `#394b78` `#52679c` `#7489be`
- accent keys (trim, sash, the cleric's cowl edge, hat band, the mage's front trim line and capelet edge, the cleric's chest
  disc, the archer's tunic hem, the rogue's thin belt sash), dark to light:
  `#3f7a6c` `#5ea590` `#96d1bb`
- **cloth over the face (mask, scarf, veil) is OUTFIT keys, never accent keys** (owner review of the first class delivery):
  factions with a bright accent (cities `#f2c94c`, elves lime, clans cream) turned the archer's hood edge and the rogue's
  scarf into solid yellow blocks over the face. The archer's hood edge around the face is outfit keys too.
- flat fills only on those areas (no dithering, gradients, texture or in-between shades); the seven keys appear nowhere
  else, and nothing else on the figure is blue, slate, teal or mint (steel is neutral grey, leather and wood warm brown,
  other shadows warm or neutral - this overrides the general "shadows toward purple/blue" rule for these sheets).
- every NON-key colour of the figure (outline and shadows included) stays at RGB distance >= 50 from all seven keys:
  `sheets.py` snaps colours within 34 (`KEY_TOL`) onto the keys, and shades 34-50 away stay as untinted blue islands.
  Do NOT reuse the anchor's dark violet-navy outline / shadow colours on these sheets (#474269, #2c2840, #28253c,
  #444061 ... are about 25% of Baren's figure pixels and lie within 34 of #263459 / #394b78, so the faction recolour
  would tint every outline): use a warm / neutral dark ramp, e.g. outline `#2a2220`, shadows `#3a2e2a` / `#4a3a2e`.
  Match the anchor's outline weight and placement, not its hue. A final "snap the uniform areas to the nearest key"
  palette pass on the figure is allowed. Each class README has a one-line Python check: pixel count per exact key and
  the near-key non-key pixels (distance 1-49, target 0).
- covered heads keep the scale: the helm / hood / cowl / brim-and-collar encloses the 110 px head (outer silhouette
  ~115-125 px); it does not sit around a full 110 px head and enlarge the figure.
- no emblem or heraldry (the faction colour comes from the keys). The cleric's plain filled accent-key chest disc is the one
  allowed shape: it is not an emblem.
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

First delivery (owner review): Felix recolour, the five classes and seven monsters were accepted and registered; the giant
spider is redrawn (legs not countable as eight), and the accepted sheets get small re-exports (message F in `phase3_gpt.md`):
archer / rogue face cloth to outfit keys, skeleton materials, wolf and gargoyle eye / mouth colours, desert bandit and harpy
outline and dark value accents on sand. Breathing in idle is added by the pipeline (`sprite-gen breathe`), not drawn by GPT.

Both batches have the owner's NovelAI design picks (`art/concepts/selections.json`: classes warrior #5, archer #10, mage #9,
cleric #4, rogue #2; monsters skeleton #1, wolf #6, desert bandit #5, harpy #9, bandit #1, gargoyle #2, giant spider #3,
wraith #7) as `concept.png` in their packages, with per-draft keep / fix notes. Messages D and E are ready to send.
