# 몬스터 — 가고일 — GPT handoff (`monster_gargoyle`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CREATURES`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md` (메시지 E).
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a gargoyle (가고일), a common monster. Save it as art/inbox/sheet_monster_gargoyle.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a hunched stone demon statue come alive: crouching on clawed hands and feet, bat wings, curved horns, a tail. Size: SMALL: crouched about 0.8 of a human idle height (idle ~380 x 330 px); wider when the wings spread. Attack: ranged in the game data (template "drake": the engine shoots a fire bolt): a roaring / spitting pose, no projectile drawn. Appears in: the volcanic mountains and the beast calamity army.

DESIGN: grey stone skin with a few big cracks and chipped edges; curved horns; bat wings of stone; red eyes (two small red clusters); big claws, a pointed tail.

COLOURS (keep close, muted): stone grey #6b737c, dark #44494f, light #9aa3ad; eyes red #d6455d; mouth dark.

FIX:
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - stone texture only as a few big cracks, not noise
  - the engine draws the fire: no flames, glow or dust in the drawing

POSES (no posekit mannequin for this creature: the text gives the pose, guide_layout.png the place and size):
  1. idle (top-left quadrant): crouched like a statue on all fours, wings folded half open, head low
  2. attack wind-up (top-right quadrant): rearing up on the hind legs, wings spread wide, claws raised, head pulled back
  3. attack strike (bottom-left quadrant): lunging forward low: head thrust forward with the jaws wide open (spitting), claws reaching forward, wings swept back
  4. hit reaction (bottom-right quadrant): knocked back onto the haunches: head thrown back, wings flung up, one claw raised to guard

REFERENCES (folder art/requests/phase3/monster_gargoyle/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_gargoyle ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR: match its rendering, outline, palette treatment and lighting
  - guide_layout.png (layout, baseline and the SIZE BOX of each pose - the lines, boxes and labels are guide-only)
  - guide_scale.png (the same pixel scale as a 4-head human captain; the grey human is NOT drawn)
  - concept.png - NOT IN THE FOLDER YET: it is added after the owner picks a NovelAI design draft. Do not start this sheet before concept.png is there

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

STYLE (same as every character):
  - high-quality HD pixel art for a modern 2D fantasy tactics game (crisp pixel clusters, no blur, no painterly rendering)
  - natural creature proportions at the SAME pixel scale as the 4-head humans (head 110 px; see guide_scale.png); NOT chibi
  - three-quarter view facing RIGHT (four-legged and eight-legged creatures mostly from the side with the head turned slightly toward the viewer); light from the upper left
  - muted, desaturated, hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones
  - dark, desaturated, NON-black outline used selectively (no thick uniform black lineart), soft rim light on one side
  - readable at 1x game size (the drawing is shrunk to about 16.5%: a 300 px pose becomes ~50 px) on a dark battlefield: big clear shapes, strong silhouette, few tiny details

DELIVERABLE:
  - ONE PNG, 1536x1024 (landscape), a 2x2 grid of four equal 768x512 quadrants, one pose per quadrant: top-left idle, top-right wind-up, bottom-left strike, bottom-right hit (as guide_layout.png); never a 1x4 row or a single pose
  - the lowest pixel of each pose (feet, paws, talons or tail tip) on y = 461 of its quadrant (y = 461 in the top row, y = 973 in the bottom row); each pose about the size of its box, all four at the same scale
  - at least 32 px of empty magenta between the creature and its quadrant's edges; nothing crosses into another quadrant
  - background: perfectly flat solid magenta #FF00FF everywhere (preferred; a transparent PNG is also accepted) - no gradient, floor, cast shadow or scenery
  - NO figure pixel may be magenta-like: every colour of the figure must stay clearly away from the background key #FF00FF, RGB distance sqrt((255-R)^2 + G^2 + (255-B)^2) >= 150 (no hot pink, magenta or bright violet; purples stay dark blue-purple such as #5a4a7a). If you reduce the palette, reduce the FIGURE colours only and never merge a figure colour into the background colour
  - NO text, labels, numbers, guide lines or boxes, watermark; NO effects outside the body (no trails, sparks, dust, glow, motion lines, projectiles)

SELF-CHECK before saving (redraw if any fails):
  [ ] 1536x1024, flat #FF00FF (or transparent), 2x2 quadrants: idle / wind-up / strike / hit as in guide_layout.png
  [ ] the lowest pixel of every pose on its baseline; each pose about its box size; the same scale as guide_scale.png
  [ ] the same creature, colours and proportions in all four poses; every FIX applied
  [ ] no text, guide lines, boxes, floor, shadow, effects or projectiles
  [ ] no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)
  [ ] reads clearly when shrunk to game size (idle ~55 px tall) on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **6번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안 대기**: 주인이 NovelAI 초안(`jobs_monsters.json`)을 고르면 `art/concepts/monster_gargoyle/`에 두고 `handoff.py`의 `CREATURES['monster_gargoyle']['concepts']`에 `{'concept.png': 'monster_gargoyle/concept_NN.png'}`를 넣어 다시 실행한다. 그 전에는 그림 쪽에 보내지 않는다.
- 설계: 살아 움직이는 돌 악마상: 웅크린 몸, 박쥐 날개, 굽은 뿔, 꼬리. 웅크린 대기 약 380x330px. 게임에서는 원거리(엔진이 불덩이를 그림).
- 자세: ① 석상처럼 네 발로 웅크림 ② 뒷다리로 일어서며 날개 펼침 ③ 낮게 앞으로 덮치며 입을 크게 벌림 ④ 주저앉듯 뒤로 밀리며 날개가 젖혀짐
- 배치: 1536x1024 **2x2 격자** (768x512 네 칸: 왼쪽 위 대기, 오른쪽 위 공격 준비, 왼쪽 아래 공격 타격, 오른쪽 아래 피격), 칸마다 맨 아래 픽셀 y=461. posekit 마네킹 없음(사람 골격이 아니다) — 자세는 글로, 자리·크기는 `guide_layout.png`의 상자로.
- 크기: 대장과 같은 배율(머리 110px). 자세별 상자 대기 380x330, 공격 준비 520x420, 공격 타격 560x340, 피격 460x360 px. `guide_scale.png` = 같은 배율의 4등신 사람(대기 약 407 px) 옆에 대기 상자. 게임에서는 약 16.5% (대기 약 55 px 높이).
- 공격: ranged in the game data (template "drake": the engine shoots a fire bolt): a roaring / spitting pose, no projectile drawn
- 결과 파일: `art/inbox/sheet_monster_gargoyle.png` (id `sheet/monster/가고일`; 이름은 게임의 몬스터 이름 그대로)

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| (`art-inbox`의 `art/inbox/sheet_captain_blademaster.png`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |
| `guide_layout.png` | 결과물 배치: 2x2 칸, 바닥선, 자세별 크기 상자 (선·상자·글씨는 가이드에만) |
| `guide_scale.png` | 같은 배율의 사람(회색, 그리지 않음)과 대기 상자 — 크기 비교 |
| (`concept.png`) | **대기** — 주인이 NovelAI 초안을 고르면 들어간다 |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_monster_gargoyle.png --dry-run --work /tmp/sheets   # 미리보기 (요청서의 scale·cell·layout 을 쓴다)
python3 tools/art/sheets.py art/inbox/sheet_monster_gargoyle.png                                 # 등록
```
