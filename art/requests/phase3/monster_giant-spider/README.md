# 몬스터 — 거대 거미 — GPT handoff (`monster_giant-spider`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CREATURES`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md` (메시지 E).
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## THIS ROUND (overrides anything below that disagrees)

```
KIND: fix (full sheet). BASE: art/inbox/check_giant-spider_idle.png @ 555007c on art-inbox - your idle check PASSED on silhouette:
keep exactly that body, leg layout and foot positions in all four poses. LOAD concept_800.jpg (the owner's draft).
MUST SURVIVE (what the owner liked in the draft): ground-level side view; legs arching higher than the back; big hairy abdomen;
bristly silhouette; glossy red eye cluster; near-black purple mass.
TWO FIXES in all four poses:
  1. EYES: dark purple now, 0 red pixels at game size. Make them GLOSSY BRIGHT RED #d6455d with one white glint each: two big eyes
     14-16 px wide at source plus 3-4 small ones, a 1 px darker red rim, no glow. SPOT: #d6455d (keep every other colour >= 60 away).
  2. BODY TONE: cooler and a little darker (purple-black #241b29, dark purple #3b3346) with a thin COOL rim light (#6a5a80) along
     the top edge of the abdomen and of each near leg arch. Fangs stay pale bone.
POSES - legs stay planted (same foot positions as the idle); the action is in the body, head and fangs:
  top-left idle (the approved one + the two fixes) / top-right threat rear: head and front of the body lift and draw BACK, fangs wide,
  abdomen tucked down (this is also the wind-up of its web-spray special; the engine draws the web) /
  bottom-left lunging bite: legs bend, the whole body thrusts FORWARD and low, fangs snapping shut / bottom-right flinch: body jolts back and up.
DELIVER: art/inbox/sheet_monster_giant-spider.png (overwrite), 1536x1024 2x2, lowest pixel y=461 per quadrant, flat #FF00FF.
```

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a giant spider (거대 거미), a common monster. Save it as art/inbox/sheet_monster_giant-spider.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a big hairy eight-legged spider seen from the side at ground level: legs arching high, body hanging low between them; the body about knee-to-chest height of a human. Size: SMALL in the data but WIDE: about 540 x 260 px in idle (legs spread). Attack: melee: a lunging BITE - the body lunges on planted legs and the fangs snap; the feet do not walk. Appears in: forest battles (the elf woods).

DESIGN: near-black purple, hairy abdomen and legs with a cool rim light; legs arching high above the body; a cluster of glossy red eyes; two pale fangs.

COLOURS (keep close, muted): body and legs purple-black #241b29, dark purple #3b3346, rim/sheen #6a5a80 (cool); eyes red #d6455d with a white glint; fangs pale bone #d8d0c0.

FROM concept.png (the owner's pick, NovelAI draft #3; design only) TAKE: the LOW, GROUND-LEVEL side view (camera at the spider's height, NOT from above); the huge round hairy abdomen behind a smaller head; the long legs ARCHING HIGH above the body - every knee higher than the carapace, so the body hangs low between them; the cluster of glossy red eyes (two big, several small) on the front of the head; short pedipalps and fangs at the mouth; the dense dark hair that makes the silhouette bristly; the menacing near-black purple mass.

FIX (do not reproduce the draft here):
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - exactly eight legs, one body, one head
  - side view at ground level like concept.png: the four near legs arch in front of the body, the four FAR legs arch above and behind it, one tone darker, so all eight can be counted
  - REDRAW 2 (owner feedback on the delivery 77c9e8f): that version lost what the owner liked in the draft - it was seen from above, flat and toy-like, with grey legs and a smooth body. Go back to concept.png: ground-level side view, high-arched dark hairy legs, big hairy abdomen, glossy red eyes. Keep only its readable leg spacing (eight countable legs)
  - MOTION: the legs stay PLANTED in all four poses (no stepping or leg-waving); the action is in the body, head and fangs
  - COUNT the legs in every pose before saving: 4 near + 4 far, each leg one clear line from body to tip, no two legs merging
  - no web, no venom spray, no drip, no effect (the engine draws effects)
  - exactly EIGHT legs, four per side, in every pose (count them); the short pedipalps at the mouth are not legs and stay short
  - the draft body and legs are near-black on a dark ground: keep them dark purple-black, but add a clear cool rim light along the top edges of the abdomen, the head and every leg arch
  - KEEP THE HAIR, but as readable clumps: tufts of bristles along the silhouette edges of the abdomen and the legs (each tuft a few strong pixels at game size), not fine noise all over
  - the draft legs are very thin: a little thicker so every leg survives downscaling, but keep them long and high-arched
  - the draft fangs are hidden in the hair: two clear pale fangs under the eyes

POSES (no posekit mannequin for this creature: the text gives the pose, guide_layout.png the place and size):
  1. idle (top-left quadrant): low crouch on all eight high-arched legs, abdomen slightly raised, palps and fangs visible under the red eyes
  2. attack wind-up (top-right quadrant): threat rear: legs stay planted, the front of the body and the head lift and draw BACK, fangs spread wide open, abdomen tucked down behind
  3. attack strike (bottom-left quadrant): lunging bite: legs stay planted but bend, the whole body thrusts FORWARD and low, head and fangs snapping shut at the front
  4. hit reaction (bottom-right quadrant): flinch: body jolts back and up, abdomen bobbing, legs stay planted and stiffen, all eight still countable

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
  [ ] reads clearly when shrunk to game size (idle ~43 px tall) on a dark background
```

## 주인용 요약 (한국어)

- 순서: 1차 몬스터 **7번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **초안** `concept.png` = `art/concepts/monster_giant-spider/concept_03.png` (주인이 고른 #3, 디자인만) — 가져올 것: 땅높이 옆모습(위에서 내려다보지 않음), 작은 머리 뒤의 크고 털 많은 둥근 배, 무릎이 등보다 높게 솟은 긴 다리 아치(몸이 그 사이에 낮게 매달림), 반짝이는 붉은 눈 무리, 입가의 짧은 더듬이다리·독니, 털로 까칠한 실루엣, 위협적인 검보라 덩어리.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 다리는 모든 자세에서 정확히 여덟. 새까만 몸 → 검보라 유지 + 배·머리·다리 아치 윗선의 찬 림 라이트. 털은 살리되 실루엣 가장자리의 덩어리진 털 뭉치로(온몸 잔털 노이즈 아님). 아주 가는 다리 → 조금 굵게(높은 아치는 유지). 털에 묻힌 독니 → 옅은 독니 둘이 보이게.
- 설계: 땅높이 옆에서 본 털 많은 큰 거미: 다리가 몸보다 높게 아치를 그리고 몸은 그 사이에 낮게. 검보라 몸·다리 + 찬 림 라이트, 반짝이는 붉은 눈 무리, 옅은 독니 둘. 대기 약 540x260px. 공격은 물기(다리는 그대로 디딘 채 몸이 덮친다).
- 자세: 네 자세 모두 다리는 바닥에 그대로(걷거나 흔들지 않음), 움직임은 몸·머리·독니로. ① 높이 휜 여덟 다리로 낮게 웅크림 ② 위협: 머리·몸 앞쪽을 들어 뒤로 당기고 독니를 크게 벌림 ③ 물기: 다리를 굽히며 몸 전체가 앞으로 낮게 덮치고 독니가 닫힘 ④ 움찔: 몸이 뒤·위로 튀고 배가 출렁, 다리는 디딘 채 뻣뻣하게. 먼 쪽 다리 넷은 몸 위·뒤로 한 단계 어둡게.
- 배치: 1536x1024 **2x2 격자** (768x512 네 칸: 왼쪽 위 대기, 오른쪽 위 공격 준비, 왼쪽 아래 공격 타격, 오른쪽 아래 피격), 칸마다 맨 아래 픽셀 y=461. posekit 마네킹 없음(사람 골격이 아니다) — 자세는 글로, 자리·크기는 `guide_layout.png`의 상자로.
- 크기: 대장과 같은 배율(머리 110px). 자세별 상자 대기 540x260, 공격 준비 520x330, 공격 타격 600x280, 피격 520x290 px. `guide_scale.png` = 같은 배율의 4등신 사람(대기 약 407 px) 옆에 대기 상자. 게임에서는 약 16.5% (대기 약 43 px 높이).
- 공격: melee: a lunging BITE - the body lunges on planted legs and the fangs snap; the feet do not walk
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
