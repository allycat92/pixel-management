# Character design concepts (NovelAI drafts chosen by the owner)

Design references for the GPT final-art step — see `art/requests/gpt_handoff_notes.md`.
They are **design-only** (costume, colours, weapon, marks); style is unified by GPT.
NovelAI is for design drafts ONLY (owner decision): nothing here is ever processed into a game sheet — final game art
always goes through GPT, and `tools/art/sheets.py` refuses files under `art/concepts/` and any NovelAI-made PNG.
Raw candidates from `tools/art/novelai.py` land in `art/concepts/<id>/drafts/` (git-ignored); only the owner's picks are
copied up as `concept_NN.png` and recorded in `selections.json`.

`selections.json` records, per character, the chosen sample numbers from the numbered
contact sheets, their role, and the exact NovelAI parameters (model, seed, prompt, negative)
so each image can be regenerated.

- `captain_blademaster` (바렌): #5 = aesthetic reference, #8 = pixelization reference.
- `captain_ironwall` (브리긴다): #8 = design reference.
- `captain_tactician` (이사벨): #7 = design reference.
- `captain_huntress` (키아라): #4 = design reference.
- `captain_hedgemage` (펠릭스): #8. `captain_fieldmedic` (마그다): #3 (in final art REMOVE the white cross on the red apron bib / chest — no cross or symbol anywhere; the armband stays a plain dark-red band).
- `captain_fixer` (진): #5 (one dagger; add rim light so the black outfit reads on dark ground). `captain_veteran` (하랄드): #3.
- `captain_lancer` (로드릭): two variants — mounted #5 (`concept_a_05.png`) and on-foot noble knight #12 (`concept_b_12.png`).
  At 3x zoom the horse's head in #5 looks like two armoured chanfrons side by side (two eye slits, two muzzles) —
  owner to re-check; the mounted prompt says the draft's head looks doubled and to draw exactly one.
- Generic classes (faces covered so the same sprite can be many different people; uniform = key-colour slot):
  `class_warrior` #5, `class_archer` #10, `class_mage` #9, `class_cleric` #4, `class_rogue` #2.
- Monsters: `monster_skeleton` #1, `monster_wolf` #6, `monster_desert-bandit` #5, `monster_harpy` #9 (cover the torso with feathers/leather),
  `monster_bandit` #1, `monster_gargoyle` #2, `monster_giant-spider` #3 (exactly 8 legs, rim light), `monster_wraith` #7.
