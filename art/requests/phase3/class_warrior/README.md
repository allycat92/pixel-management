# 일반 병과 — 전사 — GPT handoff (`class_warrior`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of the GENERIC warrior class sprite (전사). This ONE sheet is shared by every nameless mercenary and faction soldier of this class, friend and foe, and the game recolours its uniform per faction (see KEY COLOURS). Save it as art/inbox/sheet_class_warrior.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

CHARACTER: a plain one-handed arming sword in the near hand and a round wooden shield (the guide shield's size) on the far arm; the shield FACE is painted with the outfit keys (it shows the faction colour), its rim and boss are plain iron; the FACE is covered or in shadow (see the headgear below), because this one sprite stands for hundreds of different soldiers; whatever little of the face shows is generic, with no scars, marks or distinctive features; closed steel great helm with the VISOR DOWN: no face shows, only a dark horizontal eye slit (hair fully hidden); grey chainmail shirt; knee-length sleeveless TABARD over the mail; leather belt, brown gloves; dark trousers, brown boots; sturdy, ordinary soldier build.

KEY COLOURS (the most important rule of this sheet): ONE sheet is shared by every faction and company, and the game recolours the uniform at runtime by replacing these EXACT colours with the faction colours, keeping their light/dark steps.
  - OUTFIT keys = the tabard and the shield face, darkest to lightest: #263459 (deep shadow, folds), #394b78 (shadow), #52679c (base), #7489be (lit side)
  - ACCENT keys = the tabard's border trim and one plain band across the shield face, darkest to lightest: #3f7a6c (shadow), #5ea590 (base), #96d1bb (lit)
  - flat fills only on these areas: no dithering, gradient, noise, texture, soft blending or in-between shades; their shading uses only these steps
  - these seven colours appear NOWHERE else (not on metal, skin, hair, leather, eyes, outline or background), and nothing else on the figure is blue, slate, teal or mint: steel is NEUTRAL grey, leather and wood are warm browns, shadows on the other parts are warm or neutral, never blue (this overrides the general "shadows toward purple/blue" style rule for this sheet)
  - outline the uniform with the normal dark outline (not a key colour); after export, check with a colour picker that the uniform pixels are exactly these hex values

COLOURS of everything else (keep close, muted): eye slit warm near-black #2a2220; helmet, mail, sword, shield rim and boss NEUTRAL steel grey (no blue tint), e.g. #c8c6c0 / #8a8a86 / #5c5c5a; leather and wood warm browns.

FIX (do not reproduce the draft here):
  - the face stays covered / shadowed the SAME way in ALL FOUR poses: the visor, hood, mask, brim or veil never slips, opens or falls back, not even in the hit pose; the shadowed face is a warm or neutral dark (e.g. #3a2e2a), never blue and never a key colour
  - the helm stays readable as a helmet at 64 px: a clear visor line and eye slit, NEUTRAL grey (no blue sheen)
  - no emblem, crest or heraldry: the faction colour comes from the recoloured keys only

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: shield up, sword ready
  2. attack wind-up: weight on the back leg; sword raised up and back behind the head, shield kept forward
  3. attack strike: step-in lunge; sword cutting forward and down at full extension, shield pulled in
  4. hit reaction: torso thrown back, weight on the rear leg, head jerked back; shield up in front of the chest, sword arm dropped down-back

REFERENCES (folder art/requests/phase3/class_warrior/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/class_warrior ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly
  - guide_strip.png (layout + poses + size: the most important reference)
  - guide_1_idle.png .. guide_4_hit.png (the same four poses, larger)
  - concept.png - NOT IN THE FOLDER YET: it is added after the owner picks a NovelAI design draft. Do not start this sheet before concept.png is there

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

STYLE (same for every character):
  - high-quality HD pixel art for a modern 2D fantasy tactics game (crisp pixel clusters, no blur, no painterly rendering)
  - 4 heads tall (top of the hair to the chin = 1 head), exactly the proportions and limb lengths of the guide; NOT chibi, NOT realistic
  - front three-quarter view, facing RIGHT; light from the upper left
  - muted, desaturated, hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones
  - dark, desaturated, NON-black outline used selectively (no thick uniform black lineart), soft rim light on one side
  - readable at 1x game size (the idle figure becomes ~64 px tall on a dark battlefield): big clear shapes, strong silhouette, few tiny details

DELIVERABLE:
  - ONE PNG, 1536x1024 (landscape), the SAME character drawn 4 times in ONE row (1x4, never a 2x2 grid or a single pose), left to right: idle, wind-up, strike, hit
  - each figure exactly where guide_strip.png has it: same size, same scale, same position, same limb lengths
  - the lowest pixel of every figure (its soles) on the line y = 870 (85% of the height); head = 110 px for every character. Standing height would be 440 px (4 heads), but the guide idle pose is crouched, so the measured idle top-of-head to sole is about 401 px. Headgear (hats, helmets, plumes) and weapons are extra and not counted
  - at least 32 px of empty magenta between any two figures and between a figure and the image border (a weapon may reach over a neighbour's column as in the guide, but never closer than that)
  - background: perfectly flat solid magenta #FF00FF everywhere (preferred; a transparent PNG is also accepted) - no gradient, floor, cast shadow or scenery
  - NO figure pixel may be magenta-like: every colour of the figure must stay clearly away from the background key #FF00FF, RGB distance sqrt((255-R)^2 + G^2 + (255-B)^2) >= 150 (no hot pink, magenta or bright violet; purples stay dark blue-purple such as #5a4a7a). If you reduce the palette, reduce the FIGURE colours only and never merge a figure colour into the background colour
  - NO text, labels, numbers, frames, grid lines, watermark; NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles)

SELF-CHECK before saving (redraw if any fails):
  [ ] 1536x1024, background flat #FF00FF (or transparent), 4 figures in ONE row: idle / wind-up / strike / hit as in the guide
  [ ] soles of all four on y = 870; same size in all four; head ~110 px; idle ~401 px without headgear
  [ ] 4 heads tall; front three-quarter view facing right; light from the upper left
  [ ] same face, hair, outfit, colours and weapon in all four poses; exactly the weapons in CHARACTER (nothing extra)
  [ ] the uniform (the tabard and the shield face) uses ONLY the four outfit keys and the trim (the tabard's border trim and one plain band across the shield face) ONLY the three accent keys, exact hex, flat; the seven keys appear nowhere else and nothing else on the figure is blue, slate, teal or mint
  [ ] every FIX applied
  [ ] no text, floor, shadow, effects or projectiles; >= 32 px of magenta between figures and from the border
  [ ] no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```

## 주인용 요약 (한국어)

- 순서: 일반 병과 **1번째** (메시지 D, 대장 9명 다음) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안 대기**: 주인이 NovelAI 초안(`jobs_classes.json`)을 고르면 `art/concepts/class_warrior/`에 두고 `handoff.py`의 `CHARS['class_warrior']['concepts']`에 `{'concept.png': 'class_warrior/concept_NN.png'}`를 넣어 다시 실행한다. 그 전에는 그림 쪽에 보내지 않는다.
- **얼굴 가림** (주인 요청): 이 그림 한 장을 서로 다른 여러 사람이 같이 쓰므로 얼굴이 가려지는 복장 — 전사는 면갑을 내린 투구(눈 틈만). 네 자세 모두 같은 만큼 가린다(피격 때도 벗겨지지 않음). 가려진 얼굴 그늘은 따뜻하거나 중성인 어두운 색(파랑·열쇠 색 금지). 상급·최상급 직업은 어울릴 때만, 억지로 하지 않는다.
- **열쇠 색** (전투에서 진영 색으로 바뀐다): 제복 `#263459` `#394b78` `#52679c` `#7489be`, 장식 `#3f7a6c` `#5ea590` `#96d1bb` — 이 7색은 그 자리에만, 평평하게. 다른 곳에는 파랑·청회색·청록을 쓰지 않는다.
- 결과 파일: `art/inbox/sheet_class_warrior.png` (id `sheet/class/warrior`)
- 무기: posekit `sword_shield` 마네킹 → a plain one-handed arming sword in the near hand and a round wooden shield (the guide shield's size) on the far arm; the shield FACE is painted with the outfit keys (it shows the faction colour), its rim and boss are plain iron
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 면갑을 내린 강철 그레이트 헬름(눈 틈만 보임), 사슬 갑옷, 무릎 길이 민소매 겉옷(제복), 가죽 띠, 갈색 장갑·장화, 한손검 + 둥근 나무 방패.
- 고칠 것: 겉옷·방패 면 = 제복 열쇠 색, 겉옷 테두리·방패의 띠 하나 = 장식 열쇠 색. 금속은 푸른 기 없는 중성 회색. 문장·무늬 없음. 면갑은 네 자세 모두 내린 채.
- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.
- 가이드 띠: 머리 하나 = 110 px (모든 캐릭터 같음). 선 키라면 440 px 이지만 대기 자세가 웅크려서 정수리~발바닥 약 401 px(높이의 39%). 모자·투구·깃털·무기는 따로. 발바닥(맨 아래 픽셀) y=870.

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| (`art-inbox`의 `art/inbox/sheet_captain_blademaster.png`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |
| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |
| `guide_1_idle.png` | 자세 가이드 832x1216 — 대기 |
| `guide_2_windup.png` | 자세 가이드 832x1216 — 공격 준비 |
| `guide_3_strike.png` | 자세 가이드 832x1216 — 공격 타격 |
| `guide_4_hit.png` | 자세 가이드 832x1216 — 피격 |
| (`concept.png`) | **대기** — 주인이 NovelAI 초안을 고르면 들어간다 |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_class_warrior.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_class_warrior.png                                 # 등록
```
