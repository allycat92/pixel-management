# 몬스터 — 산적 — GPT handoff (`monster_bandit`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of a bandit (산적), a common monster. Save it as art/inbox/sheet_monster_bandit.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

BRIEF: a scruffy human outlaw with a hand axe and a small buckler. Size: SMALL (human scale). Attack: melee: axe chop. Appears in: plains, holy-ground and coast battles (the starting region).

CHARACTER: a short hand axe in the near hand (where the guide holds the sword, same angle) and a SMALL round wooden buckler on the far arm (about 0.6 heads across, smaller than the guide shield); red bandana on the head; stubble and a sneer; patched brown leather jerkin; rope belt; dark trousers, worn boots; wiry build.

COLOURS (keep close, muted): skin #e0ac7e; bandana dark red #8f2d3a; jerkin brown leather #a8764e / #6b4a32; axe head NEUTRAL steel grey.

FROM concept.png (the owner's pick, NovelAI draft #1; design only) TAKE: the red bandana with two short tails at the back, long dark hair, stubble and a sneer, a torn short-sleeved shirt under a sleeveless jerkin, a rope belt wound several times, dark trousers, worn boots folded down at the top, a short hand axe.

FIX (do not reproduce the draft here):
  - a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy
  - he must read differently from the desert bandit: red bandana, bare face, axe and buckler
  - exactly ONE head (sibling drafts of this design came out with a duplicated head): one head, one neck
  - the draft holds a second wooden handle / club in the far hand and has NO buckler: the far arm carries ONLY the small round wooden buckler of CHARACTER; exactly one axe, nothing else in the hands
  - the draft holds the axe across the belly: the axe only in the near hand, as the guide holds the sword
  - the draft jerkin is black and the build bulky and muscle-heavy: a patched brown leather jerkin (COLOURS) on a wiry build
  - the draft bandana is bright red: muted dark red #8f2d3a

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: buckler forward, axe ready
  2. attack wind-up: weight on the back leg; axe raised up and back behind the head, buckler kept forward
  3. attack strike: step-in lunge; axe chopping forward and down at full extension, buckler pulled in
  4. hit reaction: torso thrown back, weight on the rear leg, wincing; buckler up, axe arm dropped down-back

REFERENCES (folder art/requests/phase3/monster_bandit/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/monster_bandit ; in a chat they are the attached images):
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

- 순서: 1차 몬스터 **5번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 몬스터 설계: 산적 — SMALL (human scale); 공격 melee: axe chop; 나오는 곳 plains, holy-ground and coast battles (the starting region).
- 결과 파일: `art/inbox/sheet_monster_bandit.png` (id `sheet/monster/산적`)
- 무기: posekit `sword_shield` 마네킹 → a short hand axe in the near hand (where the guide holds the sword, same angle) and a SMALL round wooden buckler on the far arm (about 0.6 heads across, smaller than the guide shield)
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 붉은 두건, 수염 자국·비웃는 얼굴, 기운 가죽 조끼, 밧줄 허리띠, 짧은 손도끼 + 작은 둥근 나무 버클러.
- 고칠 것: 사막 도적과 확실히 다르게(붉은 두건·드러난 얼굴·도끼·버클러). 버클러는 가이드 방패보다 작게.
- **초안** `concept.png` = `art/concepts/monster_bandit/concept_01.png` (주인이 고른 #1, 디자인만) — 가져올 것: 뒤로 짧은 꼬리 둘이 늘어진 붉은 두건, 검은 긴 머리, 수염 자국과 비웃음, 찢어진 반소매 셔츠 위 민소매 조끼, 여러 번 감은 밧줄 허리띠, 짙은 바지, 끝을 접은 낡은 장화, 짧은 손도끼.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 머리는 정확히 하나(같은 초안의 다른 장들은 머리가 둘). 먼 손의 두 번째 나무 자루(곤봉)를 없애고 버클러만(초안에는 버클러가 없다) — 도끼 하나뿐. 배 앞에 가로로 든 도끼 → 가까운 손(가이드 손). 검은 조끼·우람한 근육 → 기운 갈색 가죽 조끼, 마른 체격. 새빨간 두건 → 탁한 짙은 빨강 #8f2d3a.
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
python3 tools/art/sheets.py art/inbox/sheet_monster_bandit.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_monster_bandit.png                                 # 등록
```
