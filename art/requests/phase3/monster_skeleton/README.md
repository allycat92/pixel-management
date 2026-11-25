# 몬스터 — 해골 병사 — GPT handoff (`monster_skeleton`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a skeleton soldier (해골 병사), a common monster. Save it as art/inbox/sheet_monster_skeleton.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a human-sized undead soldier: the same 4-head build as the captains (the helmeted skull is the 110 px head), round shield and sword. Size: SMALL (human scale, the same height as a captain). Attack: melee: sword slash. Appears in: frost and holy-ground battles, magic-investigation contracts, the demon calamity army (the most frequent monster in battle).

CHARACTER: a notched one-handed sword (neutral grey steel) in the near hand and a battered round wooden shield with an iron rim on the far arm (the guide shield's size); skull under a dented open-faced steel helmet; two small red points of light in the eye sockets (just two small red pixel clusters, no halo); CHUNKY simplified bones: the ribcage as one shape, thick limb bones, big hands and feet; tattered dark cloth scraps at the hips; no skin, no hair.

COLOURS (keep close, muted): bone pale ivory #e8e2cc, shaded #b4ad98 / #7e786a (never pure white); helmet, sword, shield rim NEUTRAL grey steel #8a8a86 / #5a5652, light #c8c6c0 (no rust brown); cloth scraps dark desaturated red #5e2f2c / #3e2220 or cold grey #4a4e56; shield wood warm brown; eyes bright red #ff4a3a (two small clusters, no halo); outline dark neutral #2e2a28 around the bones.

FROM concept.png (the owner's pick, NovelAI draft #1; design only) TAKE: the bowl-shaped open-faced helmet over a grinning skull (its colour from COLOURS: neutral grey steel, not rusty brown), two red eye points, the big ribcage, pale bones, tattered cloth hanging from the shoulders and as a ragged loincloth, the round wooden shield with an iron rim, bare bony feet.

FIX (do not reproduce the draft here):
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - bones must stay chunky: thin realistic bones vanish at 64 px
  - no green fire, glow or aura
  - four separate materials, not one warm-brown mass: ivory bone, grey steel, dark red / cold grey cloth, brown wood; the dark outline keeps the pale bones readable on snow, and the bright red eyes read in the dark eye sockets
  - exactly ONE head (sibling drafts of this design came out with a duplicated head): one head, one neck: one skull inside one helmet
  - the draft sword is a hooked, machete-like blade: a straight, notched one-handed sword in the near hand as the guide holds it
  - the draft faces the viewer and fills the far leg and forearm solid black: three-quarter view facing right, every limb drawn as bone (no black silhouette limbs)
  - the draft spine is thin and leaves a hole of background at the waist: a chunky spine and pelvis, no background showing through the torso
  - the draft cloth is blue-black: dark desaturated red or cold grey (COLOURS)
  - the draft eyes glow with a halo: two small red clusters, no halo

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: shield up, sword ready, slightly hunched
  2. attack wind-up: weight on the back leg; sword raised up and back behind the head, shield kept forward
  3. attack strike: step-in lunge; sword cutting forward and down at full extension, shield pulled in
  4. hit reaction: torso thrown back, weight on the rear leg, skull snapped back, jaw open; shield up, sword arm dropped down-back

REFERENCES (folder art/requests/phase3/monster_skeleton/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_skeleton ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly
  - guide_strip.png (layout + poses + size: the most important reference)
  - guide_1_idle.png .. guide_4_hit.png (the same four poses, larger)
  - concept.png (DESIGN ONLY)

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
  [ ] every FIX applied
  [ ] no text, floor, shadow, effects or projectiles; >= 32 px of magenta between figures and from the border
  [ ] no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **1번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 몬스터 설계: 해골 병사 — SMALL (human scale, the same height as a captain); 공격 melee: sword slash; 나오는 곳 frost and holy-ground battles, magic-investigation contracts, the demon calamity army (the most frequent monster in battle).
- 결과 파일: `art/inbox/sheet_monster_skeleton.png` (id `sheet/monster/해골 병사`)
- 무기: posekit `sword_shield` 마네킹 → a notched one-handed sword (neutral grey steel) in the near hand and a battered round wooden shield with an iron rim on the far arm (the guide shield's size)
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 찌그러진 회색 강철 개방형 투구 아래 해골, 눈구멍의 밝은 붉은 점 둘, 굵게 단순화한 뼈, 허리의 해진 천, 이 빠진 한손검 + 쇠테 두른 둥근 나무 방패.
- 고칠 것: 재질을 나눈다: 뼈 = 옅은 상아색, 투구·칼 = 중성 회색 강철(녹슨 갈색 아님), 천 = 탁한 짙은 빨강 또는 찬 회색, 눈 = 밝은 빨강 #ff4a3a — 온통 따뜻한 갈색 덩어리 금지, 눈 위에서도 보이게 뼈 둘레에 어두운 외곽선. 뼈는 굵게(가는 뼈는 64px 에서 사라진다), 순백 금지, 초록 불꽃·빛 없음. 사람과 같은 크기.
- **초안** `concept.png` = `art/concepts/monster_skeleton/concept_01.png` (주인이 고른 #1, 디자인만) — 가져올 것: 사발 모양 개방형 투구(색은 회색 강철)와 이를 드러낸 해골, 붉은 눈 점 둘, 큰 갈비뼈, 때 묻은 흰 뼈, 어깨와 허리에 걸친 해진 검은 천, 쇠테 두른 둥근 나무 방패, 맨발 뼈.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 머리는 정확히 하나(같은 초안의 다른 장들은 머리가 둘). 갈고리 진 마체테 같은 칼 → 곧고 이 빠진 한손검(가이드 손). 정면을 보며 먼 다리·팔이 새까만 덩어리 → 오른쪽 보는 3/4, 모든 팔다리를 뼈로. 가는 척추·허리에 뚫린 배경 구멍 → 굵은 척추·골반, 몸통에 구멍 없음. 청흑색 천 → 탁한 짙은 빨강 또는 찬 회색. 눈의 빛 번짐 없이 작은 붉은 점.
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
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_monster_skeleton.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_monster_skeleton.png                                 # 등록
```
