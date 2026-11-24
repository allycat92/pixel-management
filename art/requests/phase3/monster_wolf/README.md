# 몬스터 — 들늑대 — GPT handoff (`monster_wolf`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CREATURES`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md` (메시지 E).
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a wild wolf (들늑대), a common monster. Save it as art/inbox/sheet_monster_wolf.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a lean grey wild wolf in side three-quarter view, head low, tail down: a long horizontal shape. Size: SMALL: shoulder about half a standing human, nose to tail about one human height (idle ~420 x 250 px). Attack: melee: lunging bite. Appears in: plains and forest battles (the most frequent beast).

DESIGN: shaggy grey fur with a darker back and a lighter belly; amber eyes; bared fangs, ears back; four legs, ONE tail, ONE head.

COLOURS (keep close, muted): fur grey #8a8f99, dark #5c606a, light grey-beige belly; eyes amber #f2c94c; mouth dark red-brown.

FROM concept.png (the owner's pick, NovelAI draft #6; design only) TAKE: the head held below the shoulder line with a snarl and bared fangs, a thick darker ruff over the neck and shoulders, pale cheeks and muzzle, pale lower legs and paws, a long bushy tail, a lean long-legged build.

FIX (do not reproduce the draft here):
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - a real wolf (not a werewolf, never standing up)
  - exactly four legs, one tail and one head in every pose
  - the PAWS are the lowest pixels (on the baseline, as DELIVERABLE says); the low-hanging tail tip always stays above the paw line
  - the draft fur is a noise of thin hatching strokes: a few big fur clumps in 2-3 tones
  - the draft fur is olive / khaki grey: neutral-cool grey as in COLOURS, darker back, lighter belly
  - the draft eye is orange-red: amber
  - the draft has four legs and one tail - keep exactly that; paint the two far legs a tone darker so all four read separately
  - the draft holds the tail out level and the ears up: the tail hangs low and the ears are laid back (as in DESIGN / POSES)

POSES (no posekit mannequin for this creature: the text gives the pose, guide_layout.png the place and size):
  1. idle (top-left quadrant): standing on all fours, head lowered, snarling, tail down
  2. attack wind-up (top-right quadrant): crouched back on the haunches, front low, ready to pounce, ears flat
  3. attack strike (bottom-left quadrant): leaping lunge to the right: body stretched, forelegs reaching forward, jaws wide open; one hind paw still touches the baseline
  4. hit reaction (bottom-right quadrant): recoiling backward: head thrown up and back, yelping, hind legs bent, front paws lifted

REFERENCES (folder art/requests/phase3/monster_wolf/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_wolf ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR: match its rendering, outline, palette treatment and lighting
  - guide_layout.png (layout, baseline and the SIZE BOX of each pose - the lines, boxes and labels are guide-only)
  - guide_scale.png (the same pixel scale as a 4-head human captain; the grey human is NOT drawn)
  - concept.png (DESIGN ONLY)

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
  [ ] reads clearly when shrunk to game size (idle ~41 px tall) on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **2번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안** `concept.png` = `art/concepts/monster_wolf/concept_06.png` (주인이 고른 #6, 디자인만) — 가져올 것: 어깨선 아래로 낮춘 머리와 드러낸 송곳니, 목·어깨의 짙은 갈기, 밝은 뺨·주둥이, 밝은 다리 끝·발, 굵고 긴 꼬리, 다리가 긴 마른 체격.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 가는 빗금 털(노이즈) → 큰 털 덩어리 2~3단. 올리브·카키빛 회색 → 중성·찬 회색(등 짙게, 배 밝게). 주황빛 붉은 눈 → 호박색. 다리 넷·꼬리 하나 그대로, 먼 쪽 다리 둘은 한 단계 어둡게. 초안은 꼬리를 수평으로 들고 귀를 세웠다 → 꼬리는 낮게 늘어뜨리고 귀는 뒤로 젖힌다(DESIGN·POSES 대로). 바닥선에는 발, 꼬리 끝은 발보다 위.
- 설계: 회색 들늑대, 머리 낮추고 으르렁, 꼬리 아래. 작은 몬스터(대기 상자 약 420x250px). 물기 근접 공격.
- 자세: ① 네 발로 서서 으르렁 ② 뒷다리에 웅크려 덮칠 준비 ③ 오른쪽으로 덮치며 문다(뒷발 하나는 바닥) ④ 머리를 젖히며 뒤로 물러남
- 배치: 1536x1024 **2x2 격자** (768x512 네 칸: 왼쪽 위 대기, 오른쪽 위 공격 준비, 왼쪽 아래 공격 타격, 오른쪽 아래 피격), 칸마다 맨 아래 픽셀 y=461. posekit 마네킹 없음(사람 골격이 아니다) — 자세는 글로, 자리·크기는 `guide_layout.png`의 상자로.
- 크기: 대장과 같은 배율(머리 110px). 자세별 상자 대기 420x250, 공격 준비 400x220, 공격 타격 540x260, 피격 400x280 px. `guide_scale.png` = 같은 배율의 4등신 사람(대기 약 407 px) 옆에 대기 상자. 게임에서는 약 16.5% (대기 약 41 px 높이).
- 공격: melee: lunging bite
- 결과 파일: `art/inbox/sheet_monster_wolf.png` (id `sheet/monster/들늑대`; 이름은 게임의 몬스터 이름 그대로)

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| (`art-inbox`의 `art/inbox/sheet_captain_blademaster.png`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |
| `guide_layout.png` | 결과물 배치: 2x2 칸, 바닥선, 자세별 크기 상자 (선·상자·글씨는 가이드에만) |
| `guide_scale.png` | 같은 배율의 사람(회색, 그리지 않음)과 대기 상자 — 크기 비교 |
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_monster_wolf.png --dry-run --work /tmp/sheets   # 미리보기 (요청서의 scale·cell·layout 을 쓴다)
python3 tools/art/sheets.py art/inbox/sheet_monster_wolf.png                                 # 등록
```
