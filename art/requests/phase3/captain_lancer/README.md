# 로드릭 — 말을 잃은 기사 (창기병) — GPT handoff (`captain_lancer`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Roderick (로드릭, lancer), a mercenary captain. Save it as art/inbox/sheet_captain_lancer.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

CHARACTER: a spear-length infantry lance: straight shaft, slim leaf-shaped steel tip, small blue pennant just below the tip, exactly as long as the guide spear; NO cone-shaped jousting lance and no vamplate (hand guard); ornate steel helmet with a blue plume, visor raised so the face shows; short brown hair, stubble, determined eyes; polished blue plate armour with gold trim; worn white surcoat with a simple blue lion emblem; tattered red cape; steel greaves.

COLOURS (keep close, muted): skin #f2c9a0; hair brown #5a3720; plate armour blue #3d5a9c; surcoat worn off-white #e8e4d8 (shaded, never pure white); cape dark red.

FIX (do not reproduce the draft here):
  - ON FOOT: he is "the knight who lost his horse" - no horse in this sheet
  - the plume and the cape stay compact (no huge flowing cape), so nothing reaches the neighbouring figure
  - simplify the lion emblem to one readable blue shape

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: lance held diagonally forward with both hands
  2. attack wind-up: weight on the back leg; lance pulled back level at hip height, rear hand behind the hip, ready to thrust
  3. attack strike: step-in lunge; both arms extended, lance thrust straight forward at full extension
  4. hit reaction: torso thrown back, weight on the rear leg, wincing; the lance knocked upward (tip up) in both hands

REFERENCES (folder art/requests/phase3/captain_lancer/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_lancer ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly
  - guide_strip.png (layout + poses + size: the most important reference)
  - guide_1_idle.png .. guide_4_hit.png (the same four poses, larger)
  - concept.png (DESIGN ONLY)
  - portrait.png (face and hair only)

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

- 순서: **4번째** — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_lancer.png` (id `sheet/captain/lancer`), 추가 선택: `art/inbox/sheet_captain_lancer_mounted.png`
- 무기: posekit `spear` 마네킹 → a spear-length infantry lance: straight shaft, slim leaf-shaped steel tip, small blue pennant just below the tip, exactly as long as the guide spear; NO cone-shaped jousting lance and no vamplate (hand guard)
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 파란 깃털 장식 투구(얼굴 보이게), 갈색 짧은 머리·수염, 금테 파란 판금, 파란 사자 문장의 낡은 흰 겉옷, 해진 붉은 망토.
- 고칠 것: 말 없이 걷는 기사(본 시트). 무기는 창 길이의 보병용 랜스(가는 잎 모양 날, 파란 작은 깃발, 원뿔 마상창·손 보호대 없음). 문장은 단순하게, 망토·깃털은 작게.
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
| `portrait.png` | 승인된 초상화 (얼굴·머리만 참고) |
| `concept_mounted.png` | 기마 초안 (추가 선택 시트용, 디자인만) |
| `guide_mounted_layout.png` | 기마 시트 2x2 칸 나눔·크기 참고 (선·글씨는 가이드에만, 실루엣은 왼쪽 아래 칸) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_captain_lancer.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_lancer.png                                 # 등록
python3 tools/art/sheets.py art/inbox/sheet_captain_lancer_mounted.png --grid 2x2 --dry-run --work /tmp/sheets  # 기마: 미리보기만 (게임 미사용, 등록하지 않는다)
```

## 추가 선택: 기마 시트 (게임은 아직 쓰지 않는다)

- 이야기는 "말을 잃은 기사"라 본 시트는 걷는 기사다. 기마 그림은 나중에 "군마를 되찾는" 형태가 생길 때를 위한 **추가 시트**다.
- 파일 `art/inbox/sheet_captain_lancer_mounted.png` (본 시트와 다른 이름), id `sheet/captain/lancer_mounted`, 1536x1024 **2x2 격자**. 9명이 끝난 **맨 마지막**에 그린다.
- 갑옷은 걷는 시트와 같은 **파란 판금**(초안의 은색 아님). 무기도 걷는 시트와 같은 깃발 달린 랜스(원뿔 마상창 아님).
- 고른 초안의 말 머리 부분은 투구 낀 머리 둘이 나란히 붙은 것처럼 보인다(주인 확인 필요). 그림에서는 **말 머리 정확히 하나**.

```
TASK (OPTIONAL, LAST): a mounted variant of the same knight (Roderick). Save as art/inbox/sheet_captain_lancer_mounted.png on the art-inbox branch (NOT sheet_captain_lancer.png; in a chat, return the PNG). The game does not use it yet; it is for a possible later "regains a warhorse" form.
REFERENCES: the style anchor art/inbox/sheet_captain_blademaster.png and your art/inbox/sheet_captain_lancer.png (same knight: same face, BLUE plate armour, white surcoat, red cape, plume, colours and style); art/requests/phase3/captain_lancer/concept_mounted.png (design only: armoured dark-brown warhorse with a blue caparison, couched lance, red cape; its armour is silver - paint it blue as on foot); art/requests/phase3/captain_lancer/guide_mounted_layout.png (quadrants and size only).
WEAPON: the same infantry lance as on foot (slim leaf tip, small blue pennant), couched under the arm; no cone-shaped jousting lance.
LAYOUT: one PNG 1536x1024 as a 2x2 grid of four equal quadrants (768x512), one pose per quadrant: top-left idle (horse standing, lance upright), top-right wind-up (horse rearing slightly, lance lowering), bottom-left strike (galloping charge, lance couched forward), bottom-right hit (horse recoiling, rider leaning back). The grey silhouette in the bottom-left quadrant of guide_mounted_layout.png shows the size of ONE pose; the other three quadrants are empty in the guide - draw each pose there at the same size. The dividing lines and labels exist only in the guide: do NOT draw lines or text. Hooves on a baseline at 90% of each quadrant's height, nothing crossing into another quadrant or touching the border; horse+rider+lance no wider than 1.6x its height.
SCALE: the rider is 4 heads tall in proportion to the horse, with a head of about 45 px (the whole group is smaller than the on-foot figures so it fits a quadrant). The horse has EXACTLY ONE head (the draft's horse head looks doubled - draw one), four legs, one tail.
Front three-quarter view facing right. Background flat #FF00FF, no floor, shadow, dust, text or effects. Same STYLE rules as above.
```
