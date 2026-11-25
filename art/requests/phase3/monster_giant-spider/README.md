# 몬스터 — 거대 거미 — GPT handoff (`monster_giant-spider`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CREATURES`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md` (메시지 E).
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a giant spider (거대 거미), a common monster. Save it as art/inbox/sheet_monster_giant-spider.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a low, wide eight-legged spider in side three-quarter view; the body about knee-to-chest height of a human. Size: SMALL in the data but WIDE: about 520 x 220 px in idle (legs spread). Attack: melee: lunging bite with the fangs. Appears in: forest battles (the elf woods).

DESIGN: dark purple carapace with a lighter purple sheen on the top edges; hairy, segmented legs; a cluster of red eyes; two big fangs.

COLOURS (keep close, muted): carapace dark purple #3b3346, darker #241b29, sheen #5a4a66; eyes red #d6455d.

FROM concept.png (the owner's pick, NovelAI draft #3; design only) TAKE: the big round abdomen behind a smaller head, the cluster of glossy red eyes (two big, several small) on the front of the head, short pedipalps at the mouth, long jointed legs in a wide arch, the low crouch.

FIX (do not reproduce the draft here):
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - exactly eight legs, one body, one head
  - very dark: add a clear cool rim light along the top edges so it reads on the dark battlefield
  - side three-quarter view: the four near legs in front of the body, the four FAR legs visible above and behind the body, one tone darker, so all eight can be counted
  - "front two pairs" = the first two legs on EACH side: 4 legs raised, 4 on the ground
  - no web, no poison drip, no effect
  - exactly EIGHT legs, four per side, in every pose (count them); the short pedipalps at the mouth are not legs and stay short
  - the draft body and legs are near-black on a dark ground: dark purple carapace as in COLOURS plus a clear cool rim light along the top edges of the abdomen, the head and every leg
  - the draft is covered in fine hair noise: a smooth carapace and only a few short spikes on the legs
  - the draft legs are very long and thin: thicker, shorter legs so the idle fits about 520 x 220 px and every leg survives downscaling
  - the draft fangs are hidden in the hair: two clear fangs

POSES (no posekit mannequin for this creature: the text gives the pose, guide_layout.png the place and size):
  1. idle (top-left quadrant): crouched on eight legs, the first leg on each side slightly raised
  2. attack wind-up (top-right quadrant): rearing up: the front two pairs of legs (the first two legs on each side, 4 legs) raised high, the other 4 on the ground, fangs bared
  3. attack strike (bottom-left quadrant): lunging forward: body low and stretched, front legs stabbing forward-down, fangs open
  4. hit reaction (bottom-right quadrant): recoiling backward: body tipped back, the legs splayed stiffly outward (NOT curled under), all eight still countable

REFERENCES (folder art/requests/phase3/monster_giant-spider/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_giant-spider ; in a chat they are the attached images):
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
  - the lowest pixel of each pose (feet, paws, talons or tail tip) on y = 461 of its quadrant (y = 461 in the top row, y = 973 in the bottom row); ALL FOUR AT THE SAME SCALE: the head, body, claws and tail keep their idle size in every pose; a bigger box only leaves room for spread wings, reaching limbs or a rearing/lunging pose - never enlarge the creature to fill its box
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
  [ ] reads clearly when shrunk to game size (idle ~36 px tall) on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **7번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안** `concept.png` = `art/concepts/monster_giant-spider/concept_03.png` (주인이 고른 #3, 디자인만) — 가져올 것: 작은 머리 뒤의 크고 둥근 배, 머리 앞의 반짝이는 붉은 눈 무리(큰 눈 둘 + 작은 눈 여럿), 입가의 짧은 더듬이다리, 넓게 휜 긴 마디 다리, 낮게 웅크린 자세.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 다리는 모든 자세에서 정확히 여덟(한쪽에 넷) — 입가의 짧은 더듬이다리는 다리가 아니고 짧게. 어두운 바닥에 묻히는 새까만 몸 → 짙은 보라 등껍질 + 배·머리·다리 윗선의 찬 림 라이트. 온몸의 잔털 노이즈 → 매끈한 등껍질, 다리에 짧은 가시 몇 개. 아주 길고 가는 다리 → 굵고 짧게(대기 약 520x220px, 줄여도 다리가 보이게). 털에 묻힌 독니 → 큰 독니 둘이 보이게.
- 설계: 낮고 넓은 다리 여덟 개 거미, 짙은 보라 등껍질, 붉은 눈 무리, 큰 독니. 대기 약 520x220px. 물기 근접 공격.
- 자세: ① 여덟 다리로 웅크림(양쪽 첫 다리를 조금 듦) ② 앞다리 두 쌍(양쪽 앞 두 다리씩, 4개)을 높이 들고 일어섬, 나머지 4개는 바닥 ③ 낮게 앞으로 덮치며 앞다리로 찍음 ④ 몸이 뒤로 젖혀지며 다리를 뻣뻣하게 벌림(오므리지 않음, 여덟 개가 보이게). 먼 쪽 다리 넷은 몸 위·뒤로 보이게 한 단계 어둡게.
- 배치: 1536x1024 **2x2 격자** (768x512 네 칸: 왼쪽 위 대기, 오른쪽 위 공격 준비, 왼쪽 아래 공격 타격, 오른쪽 아래 피격), 칸마다 맨 아래 픽셀 y=461. posekit 마네킹 없음(사람 골격이 아니다) — 자세는 글로, 자리·크기는 `guide_layout.png`의 상자로.
- 크기: 대장과 같은 배율(머리 110px). 자세별 상자 대기 520x220, 공격 준비 480x320, 공격 타격 600x260, 피격 500x240 px. `guide_scale.png` = 같은 배율의 4등신 사람(대기 약 407 px) 옆에 대기 상자. 게임에서는 약 16.5% (대기 약 36 px 높이).
- 공격: melee: lunging bite with the fangs
- 결과 파일: `art/inbox/sheet_monster_giant-spider.png` (id `sheet/monster/거대 거미`; 이름은 게임의 몬스터 이름 그대로)

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| (`art-inbox`의 `art/inbox/sheet_captain_blademaster.png`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |
| `guide_layout.png` | 결과물 배치: 2x2 칸, 바닥선, 자세별 크기 상자 (선·상자·글씨는 가이드에만) |
| `guide_scale.png` | 같은 배율의 사람(회색, 그리지 않음)과 대기 상자 — 크기 비교 |
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_monster_giant-spider.png --dry-run --work /tmp/sheets   # 미리보기 (요청서의 scale·cell·layout 을 쓴다)
python3 tools/art/sheets.py art/inbox/sheet_monster_giant-spider.png                                 # 등록
```
