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
  - every NON-key colour on the figure (outline, shadows, metal, leather, skin, eyes ...) must be at RGB distance sqrt(dR^2 + dG^2 + dB^2) >= 50 from all seven keys: the pipeline snaps colours within 34 of a key ONTO the key (so they get recoloured), and shades 34-50 away stay as untinted blue islands
  - outline and shadows: use a warm / neutral dark ramp, e.g. outline #2a2220, shadows #3a2e2a / #4a3a2e, and outline the uniform with that same warm dark (never a key colour). Do NOT reuse the anchor (Baren)'s dark violet-navy outline and shadow colours (#474269, #2c2840, #28253c, #444061 ...) on this sheet: they are within the snap distance of the outfit keys, so the game would recolour every outline and shadow with the faction colour. Match the anchor's outline WEIGHT and placement, not its hue
  - anti-aliased, blended or compressed in-between shades of the keys are failures. A final palette pass that snaps every pixel of the uniform areas to its nearest key is allowed (figure only; never snap other parts or the background onto a key)
  - after export, run this check from the repository root (in a chat, run it on your PNG if you can run Python): python3 -c "from PIL import Image; import numpy as np; K=['263459','394b78','52679c','7489be','3f7a6c','5ea590','96d1bb']; k=np.array([[int(h[i:i+2],16) for i in (0,2,4)] for h in K]); a=np.asarray(Image.open('art/inbox/sheet_class_warrior.png').convert('RGBA')).astype(int); p=a[...,:3][(a[...,3]>127)&(np.sqrt(((a[...,:3]-[255,0,255])**2).sum(-1))>=150)]; d=np.sqrt(((p[:,None,:]-k[None])**2).sum(-1)); m=d.min(1); print('exact key pixels:', {'#'+h: int((d[:,i]==0).sum()) for i,h in enumerate(K)}); print('near-key non-key pixels (distance 1-49, target 0):', int(((m>0)&(m<50)).sum()))" - it prints the pixel count of each exact key (each key you used > 0) and the near-key non-key pixels (target 0)

COLOURS of everything else (keep close, muted): eye slit warm near-black #2a2220; helmet, mail, sword, shield rim and boss NEUTRAL steel grey (no blue tint), e.g. #c8c6c0 / #8a8a86 / #5a5652; leather and wood warm browns.

FROM concept.png (the owner's pick, NovelAI draft #5; design only) TAKE: the plain foot-soldier look: closed steel helm with the visor down and one dark eye slit (its small top spike may stay, small), mail coif and mail sleeves under a sleeveless knee-length tabard split at the front, brown belt with a square buckle, brown gloves, grey trousers, tall brown boots, a plain round shield on the far arm and a straight arming sword.

FIX (do not reproduce the draft here):
  - the face stays covered / shadowed the SAME way in ALL FOUR poses: the visor, hood, mask, brim or veil never slips, opens or falls back, not even in the hit pose; the shadowed face is a warm or neutral dark (e.g. #3a2e2a), never blue and never a key colour
  - the helm stays readable as a helmet at 64 px: a clear visor line and eye slit, NEUTRAL grey (no blue sheen)
  - no emblem, crest or heraldry: the faction colour comes from the recoloured keys only
  - HEAD SIZE: the closed helm IS the head: its outline and the mail coif enclose the 110 px head (outer silhouette about 115-125 px from crown to chin, the small top spike extra); do not draw a 110 px head and then a bigger helm / hood around it, and do not enlarge the figure (this overrides "headgear is extra" in DELIVERABLE for this sheet)
  - the draft's slate-blue / teal / cyan cloth only marks WHERE the key colours go: repaint those areas with the exact KEY COLOURS ramps above (flat), never with the draft's own blues, teals or cyans
  - the draft shield is bare wood grain: its FACE uses the outfit keys (flat, no wood texture) with one accent-key band, and a plain iron rim and boss (see CHARACTER)
  - the draft tabard has no trim: add the accent-key border trim
  - the draft's ochre-yellow boot cuffs become plain warm brown (nothing yellow on the figure)
  - the draft helm is bright polished silver with white glints: neutral mid steel grey, small highlights only
  - the draft's rear leg crosses awkwardly behind the front one: legs and stance come ONLY from the guide

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: shield up, sword ready
  2. attack wind-up: weight on the back leg; sword raised up and back behind the head, shield kept forward
  3. attack strike: step-in lunge; sword cutting forward and down at full extension, shield pulled in
  4. hit reaction: torso thrown back, weight on the rear leg, head jerked back; shield up in front of the chest, sword arm dropped down-back

REFERENCES (folder art/requests/phase3/class_warrior/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/class_warrior ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly - EXCEPT its dark violet-navy outline and shadow colours: on this sheet they would turn into key colours (use the warm dark ramp #2a2220 / #3a2e2a / #4a3a2e, see KEY COLOURS)
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
  [ ] the uniform (the tabard and the shield face) uses ONLY the four outfit keys and the trim (the tabard's border trim and one plain band across the shield face) ONLY the three accent keys, exact hex, flat; the seven keys appear nowhere else and nothing else on the figure is blue, slate, teal or mint; every other figure colour (outline and shadows included) is at RGB distance >= 50 from all seven keys: the key check prints 0 near-key pixels
  [ ] every FIX applied
  [ ] no text, floor, shadow, effects or projectiles; >= 32 px of magenta between figures and from the border
  [ ] no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```

## 주인용 요약 (한국어)

- 순서: 일반 병과 **1번째** (메시지 D, 대장 9명 다음) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **얼굴 가림** (주인 요청): 이 그림 한 장을 서로 다른 여러 사람이 같이 쓰므로 얼굴이 가려지는 복장 — 전사는 면갑을 내린 투구(눈 틈만). 네 자세 모두 같은 만큼 가린다(피격 때도 벗겨지지 않음). 가려진 얼굴 그늘은 따뜻하거나 중성인 어두운 색(파랑·열쇠 색 금지). 상급·최상급 직업은 어울릴 때만, 억지로 하지 않는다.
- **열쇠 색** (전투에서 진영 색으로 바뀐다): 제복 `#263459` `#394b78` `#52679c` `#7489be`, 장식 `#3f7a6c` `#5ea590` `#96d1bb` — 이 7색은 그 자리에만, 평평하게. 다른 곳에는 파랑·청회색·청록을 쓰지 않는다.
- **열쇠 색 거리**: 열쇠 색이 아닌 모든 색(외곽선·그늘 포함)은 7색 모두와 RGB 거리 50 이상 — `sheets.py`는 거리 34 안을 열쇠 색으로 붙인다. 바렌의 남보라 외곽선·그늘(#474269 등)은 그 안이라 쓰지 않고 따뜻한 어둠 `#2a2220` / `#3a2e2a` / `#4a3a2e`을 쓴다. 영어 블록 KEY COLOURS 의 확인 한 줄이 열쇠 색별 픽셀 수와 「열쇠 색 근처 픽셀」(목표 0)을 센다.
- **머리 크기**: 투구·후드·두건·모자 챙과 깃이 110px 머리를 감싼다(바깥 실루엣 약 115~125px). 머리 110px 위에 더 큰 투구를 씌워 인물을 키우지 않는다.
- 결과 파일: `art/inbox/sheet_class_warrior.png` (id `sheet/class/warrior`)
- 무기: posekit `sword_shield` 마네킹 → a plain one-handed arming sword in the near hand and a round wooden shield (the guide shield's size) on the far arm; the shield FACE is painted with the outfit keys (it shows the faction colour), its rim and boss are plain iron
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 면갑을 내린 강철 그레이트 헬름(눈 틈만 보임), 사슬 갑옷, 무릎 길이 민소매 겉옷(제복), 가죽 띠, 갈색 장갑·장화, 한손검 + 둥근 나무 방패.
- 고칠 것: 겉옷·방패 면 = 제복 열쇠 색, 겉옷 테두리·방패의 띠 하나 = 장식 열쇠 색. 금속은 푸른 기 없는 중성 회색. 문장·무늬 없음. 면갑은 네 자세 모두 내린 채.
- **초안** `concept.png` = `art/concepts/class_warrior/concept_05.png` (주인이 고른 #5, 디자인만) — 가져올 것: 면갑 내린 투구(눈 틈 하나, 위의 작은 뿔은 작게 둬도 됨), 사슬 두건·사슬 소매, 앞이 갈라진 무릎 길이 민소매 겉옷, 네모 버클 갈색 띠, 갈색 장갑, 회색 바지, 갈색 긴 장화, 둥근 방패 + 곧은 한손검.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 초안의 청회색·청록은 열쇠 색 자리 표시일 뿐 → 정확한 열쇠 색으로. 나무결 방패 → 방패 면은 제복 열쇠 색(평평하게) + 장식 띠 하나, 쇠 테·쇠 돌기. 겉옷에 장식 테두리 추가. 노란 장화 끝단 → 갈색. 번쩍이는 은색 투구 → 중성 회색. 꼬인 뒷다리 → 자세는 가이드대로.
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
python3 tools/art/sheets.py art/inbox/sheet_class_warrior.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_class_warrior.png                                 # 등록
```
