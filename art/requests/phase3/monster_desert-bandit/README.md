# 몬스터 — 사막 도적 — GPT handoff (`monster_desert-bandit`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a desert bandit (사막 도적), a common monster. Save it as art/inbox/sheet_monster_desert-bandit.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a human raider in loose desert robes and a head wrap, one curved sword. Size: SMALL (human scale). Attack: melee: scimitar slash. Appears in: desert battles (the two desert provinces).

CHARACTER: a curved scimitar in the near hand (where the guide holds the sword, same angle). NO shield: the guide's round shield is a placeholder - the far hand is EMPTY and held up open as a guard where the shield is; sand-coloured head wrap and a face veil (only the eyes show); loose sand-coloured robe-tunic; brown leather vest and a sash; baggy trousers tucked into leather boots; tan skin on the hands.

COLOURS (keep close, muted): skin #c68a5c; head wrap, robe sand #e8d5a3 (muted, shaded toward warm grey; never white); vest, sash, boots brown #8d5a3b; scimitar NEUTRAL steel grey.

FIX (do not reproduce the draft here):
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - exactly one weapon (the scimitar); no shield, no second blade
  - the sand robe must not merge with the desert background: give it a darker outline and clear shading

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: scimitar held ready in front, free hand up as a guard
  2. attack wind-up: weight on the back leg; scimitar raised up and back behind the head, free hand forward
  3. attack strike: step-in lunge; scimitar slashing forward and down at full extension, free hand pulled back
  4. hit reaction: torso thrown back, weight on the rear leg, wincing; scimitar arm dropped down-back, free hand up

REFERENCES (folder art/requests/phase3/monster_desert-bandit/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_desert-bandit ; in a chat they are the attached images):
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
  [ ] every FIX applied
  [ ] no text, floor, shadow, effects or projectiles; >= 32 px of magenta between figures and from the border
  [ ] no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **3번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안 대기**: 주인이 NovelAI 초안(`jobs_monsters.json`)을 고르면 `art/concepts/monster_desert-bandit/`에 두고 `handoff.py`의 `CHARS['monster_desert-bandit']['concepts']`에 `{'concept.png': 'monster_desert-bandit/concept_NN.png'}`를 넣어 다시 실행한다. 그 전에는 그림 쪽에 보내지 않는다.
- 몬스터 설계: 사막 도적 — SMALL (human scale); 공격 melee: scimitar slash; 나오는 곳 desert battles (the two desert provinces).
- 결과 파일: `art/inbox/sheet_monster_desert-bandit.png` (id `sheet/monster/사막 도적`)
- 무기: posekit `sword_shield` 마네킹 → a curved scimitar in the near hand (where the guide holds the sword, same angle). NO shield: the guide's round shield is a placeholder - the far hand is EMPTY and held up open as a guard where the shield is
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 모래색 머리 두건과 얼굴 가리개(눈만 보임), 헐렁한 모래색 겉옷, 갈색 가죽 조끼·허리 천, 통 넓은 바지와 장화, 곡도(시미터) 하나.
- 고칠 것: 방패 없음 — 가이드의 둥근 방패 자리는 빈손(막는 자세). 모래색이 사막 배경에 묻히지 않게 외곽선·명암 분명히.
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
python3 tools/art/sheets.py art/inbox/sheet_monster_desert-bandit.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_monster_desert-bandit.png                                 # 등록
```
