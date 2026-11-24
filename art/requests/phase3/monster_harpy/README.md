# 몬스터 — 하피 — GPT handoff (`monster_harpy`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CREATURES`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md` (메시지 E).
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a harpy (하피), a common monster. Save it as art/inbox/sheet_monster_harpy.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a hovering bird-woman: human head and torso (4-head proportions, head 110 px), wings instead of arms, bird legs with talons, a feather tail - wide because of the wings. Size: SMALL: body like a human, the wings make it wide (idle ~440 x 400 px including the raised wings). Attack: ranged in the game data (template "drake": the engine shoots a fire bolt): a shrieking pose, no projectile drawn. Appears in: desert battles and the beast calamity army.

DESIGN: wild auburn hair; red eyes, a fierce face; purple feathered wings instead of arms (three small claws at the wing bend); a feathered chest wrap (no bare chest); scaly bird legs with big talons; a short fan of tail feathers.

COLOURS (keep close, muted): skin #e0ac7e (muted); feathers muted purple #8a6aa8 shaded with #5a4a7a (blue-purple, never pink or magenta); legs and talons brown #a8764e; eyes red #d6455d.

FIX:
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - tasteful: the chest is covered with feathers
  - the feathers stay blue-purple and dark enough: no pixel may come close to the #FF00FF background (see the magenta rule)
  - the engine draws the projectile and the glow: no fire, light or effect in the drawing

POSES (no posekit mannequin for this creature: the text gives the pose, guide_layout.png the place and size):
  1. idle (top-left quadrant): hovering low with the wings half raised; talons dangling, the lowest talon on the baseline
  2. attack wind-up (top-right quadrant): wings raised high and back, head drawn back, mouth open (about to shriek), talons drawn up
  3. attack strike (bottom-left quadrant): lunging forward: head and chest thrust forward, mouth wide open shrieking, wings flung forward, talons reaching forward-down
  4. hit reaction (bottom-right quadrant): knocked back: wings flung up and out, body jerked back, feathers ruffled, wincing

REFERENCES (folder art/requests/phase3/monster_harpy/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_harpy ; in a chat they are the attached images):
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
  [ ] reads clearly when shrunk to game size (idle ~66 px tall) on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **4번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안 대기**: 주인이 NovelAI 초안(`jobs_monsters.json`)을 고르면 `art/concepts/monster_harpy/`에 두고 `handoff.py`의 `CREATURES['monster_harpy']['concepts']`에 `{'concept.png': 'monster_harpy/concept_NN.png'}`를 넣어 다시 실행한다. 그 전에는 그림 쪽에 보내지 않는다.
- 설계: 공중에 뜬 새 여인. 사람 머리·몸통(4등신), 팔 대신 보라 날개, 새 다리·발톱. 날개 때문에 넓다(대기 약 440x400px). 게임에서는 원거리(엔진이 불덩이를 그림).
- 자세: ① 날개 반쯤 들고 낮게 떠 있음(발톱 끝이 바닥선) ② 날개를 높이 뒤로, 입 벌림 ③ 머리·가슴을 앞으로 내밀며 비명, 날개 앞으로 ④ 날개가 위로 젖혀지며 뒤로 밀림
- 배치: 1536x1024 **2x2 격자** (768x512 네 칸: 왼쪽 위 대기, 오른쪽 위 공격 준비, 왼쪽 아래 공격 타격, 오른쪽 아래 피격), 칸마다 맨 아래 픽셀 y=461. posekit 마네킹 없음(사람 골격이 아니다) — 자세는 글로, 자리·크기는 `guide_layout.png`의 상자로.
- 크기: 대장과 같은 배율(머리 110px). 자세별 상자 대기 440x400, 공격 준비 420x420, 공격 타격 560x340, 피격 480x400 px. `guide_scale.png` = 같은 배율의 4등신 사람(대기 약 407 px) 옆에 대기 상자. 게임에서는 약 16.5% (대기 약 66 px 높이).
- 공격: ranged in the game data (template "drake": the engine shoots a fire bolt): a shrieking pose, no projectile drawn
- 결과 파일: `art/inbox/sheet_monster_harpy.png` (id `sheet/monster/하피`; 이름은 게임의 몬스터 이름 그대로)

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| (`art-inbox`의 `art/inbox/sheet_captain_blademaster.png`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |
| `guide_layout.png` | 결과물 배치: 2x2 칸, 바닥선, 자세별 크기 상자 (선·상자·글씨는 가이드에만) |
| `guide_scale.png` | 같은 배율의 사람(회색, 그리지 않음)과 대기 상자 — 크기 비교 |
| (`concept.png`) | **대기** — 주인이 NovelAI 초안을 고르면 들어간다 |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_monster_harpy.png --dry-run --work /tmp/sheets   # 미리보기 (요청서의 scale·cell·layout 을 쓴다)
python3 tools/art/sheets.py art/inbox/sheet_monster_harpy.png                                 # 등록
```
