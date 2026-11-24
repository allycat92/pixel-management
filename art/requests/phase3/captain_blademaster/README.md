# 바렌 — 떠돌이 검귀 (검귀) — GPT handoff (`captain_blademaster`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Baren (바렌, blademaster), a mercenary captain. Save it as art/inbox/sheet_captain_blademaster.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

CHARACTER: ONE katana (slim curved single-edged sword, dark wrapped hilt, small round guard), held with both hands; messy dark-brown hair; white headband with two long tails (keep the tails short enough to stay clear of the neighbouring figure); thin scar across one cheek; fitted dark-navy tunic; dark-crimson half cape / hip wrap hanging on one side; leather belt and a cross strap; dark trousers, brown boots; calm, focused expression.

COLOURS (keep close, muted): skin #e0ac7e; hair #2b1d14; tunic (main garment) dark navy #2a3150; half cape / hip wrap dark crimson #3a1018; headband off-white #e8e4d8.

FIX (do not reproduce the draft here):
  - concept.png is the LOOK reference; concept_pixel.png shows how SIMPLE the shapes must stay: big clear shapes, few folds, few small details, so it survives downscaling to 64 px
  - the TUNIC is dark navy; dark crimson is ONLY the half cape / hip wrap (the portrait's wine-red coat is not the battle outfit)
  - portrait.png is for the face and hair only (light stubble as in the portrait is fine); ignore its coat and the sword over its shoulder
  - exactly one katana: no scabbard, no second sword, no arm wraps or bracers (the drafts add them; leave them out)
  - this image becomes the STYLE ANCHOR for the eight other captains: keep it clean and exemplary

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: katana held diagonally up in front, both hands on the hilt
  2. attack wind-up: weight on the back leg, more upright; both hands raised above the head, the blade pointing UP and BACK over the head
  3. attack strike: step-in lunge; both arms extended forward, the blade cutting down and forward
  4. hit reaction: torso thrown back, weight on the rear leg, head snapped back wincing; the katana drops down-back in the near hand, the free hand flies up

REFERENCES (folder art/requests/phase3/captain_blademaster/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_blademaster ; in a chat they are the attached images):
  - guide_strip.png (layout + poses + size: the most important reference)
  - guide_1_idle.png .. guide_4_hit.png (the same four poses, larger)
  - concept.png (DESIGN ONLY)
  - concept_pixel.png (how simple the shapes must stay)
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
  - NO text, labels, numbers, frames, grid lines, watermark; NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles)

SELF-CHECK before saving (redraw if any fails):
  [ ] 1536x1024, background flat #FF00FF (or transparent), 4 figures in ONE row: idle / wind-up / strike / hit as in the guide
  [ ] soles of all four on y = 870; same size in all four; head ~110 px; idle ~401 px without headgear
  [ ] 4 heads tall; front three-quarter view facing right; light from the upper left
  [ ] same face, hair, outfit, colours and weapon in all four poses; exactly the weapons in CHARACTER (nothing extra)
  [ ] every FIX applied
  [ ] no text, floor, shadow, effects or projectiles; >= 32 px of magenta between figures and from the border
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```

## 주인용 요약 (한국어)

- 순서: **1번째** — **화풍 기준(앵커)**: 이 그림을 먼저 받아 승인한 뒤 나머지 8명을 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_blademaster.png` (id `sheet/captain/blademaster`)
- 무기: posekit `katana` 마네킹 → ONE katana (slim curved single-edged sword, dark wrapped hilt, small round guard), held with both hands
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 헝클어진 짙은 갈색 머리, 꼬리가 긴 흰 머리띠, 뺨의 흉터, 짙은 남색 상의(#2a3150), 한쪽에 늘어진 짙은 진홍 반망토(#3a1018), 가죽 띠, 갈색 장화, 카타나(두 손).
- 고칠 것: concept = 생김새 기준, concept_pixel = 도트로 줄여도 살아남을 만큼 단순한 형태의 기준. 상의는 남색, 진홍은 반망토만. 칼집·두 번째 칼·팔 붕대 없음. 이 그림이 나머지 8명의 화풍 기준(앵커).
- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.
- 가이드 띠: 머리 하나 = 110 px (모든 캐릭터 같음). 선 키라면 440 px 이지만 대기 자세가 웅크려서 정수리~발바닥 약 401 px(높이의 39%). 모자·투구·깃털·무기는 따로. 발바닥(맨 아래 픽셀) y=870.

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |
| `guide_1_idle.png` | 자세 가이드 832x1216 — 대기 |
| `guide_2_windup.png` | 자세 가이드 832x1216 — 공격 준비 |
| `guide_3_strike.png` | 자세 가이드 832x1216 — 공격 타격 |
| `guide_4_hit.png` | 자세 가이드 832x1216 — 피격 |
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |
| `concept_pixel.png` | 도트로 줄여도 살아남는 단순한 형태의 기준 |
| `portrait.png` | 승인된 초상화 (얼굴·머리만 참고) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png                                 # 등록
```
