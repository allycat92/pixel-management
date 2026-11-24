# 바렌 — 떠돌이 검귀 (검귀) — GPT handoff (`captain_blademaster`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`, `art/STYLE.md`(전투 캐릭터). 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.

## 주인용 요약 (한국어)

- 순서: **1번째** — **화풍 기준(앵커)**: 이 그림을 먼저 받아 승인한 뒤 나머지 8명을 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_blademaster.png` (id `sheet/captain/blademaster`)
- 무기: posekit `katana` 마네킹 → a katana (slim curved single-edged sword, dark wrapped hilt, small round guard), held with both hands
- 자세(posekit 프레임): ① 대기 `idle_0` ② 공격 준비 `attack_1` ③ 공격 타격 `attack_2` ④ 피격 `hit_0`
- 초안에서 가져올 것: 헝클어진 짙은 갈색 머리, 꼬리가 긴 흰 머리띠, 뺨의 흉터, 짙은 남색 상의, 한쪽에 늘어진 짙은 진홍 반망토, 가죽 띠, 갈색 장화, 카타나(두 손).
- 고칠 것: #5 = 생김새 기준, #8 = 도트로 줄여도 살아남을 만큼 단순한 형태의 기준. 이 그림이 나머지 8명의 화풍 기준(앵커)이 된다.
- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.
- 가이드 띠: 머리 하나 = 110.0 px (모든 캐릭터 같음), 대기 자세 키 약 401 px = 그림 높이의 39%, 발 기준선 y=870.

### 파일

| 파일 | 내용 |
|---|---|
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |
| `concept_pixel.png` | #8 — 도트로 줄여도 살아남는 단순한 형태의 기준 |
| `portrait.png` | 승인된 초상화 (얼굴·머리만 참고) |
| `guide_1_idle.png` | posekit 가이드 832x1216 — 대기 |
| `guide_2_windup.png` | posekit 가이드 832x1216 — 공격 준비 |
| `guide_3_strike.png` | posekit 가이드 832x1216 — 공격 타격 |
| `guide_4_hit.png` | posekit 가이드 832x1216 — 피격 |
| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png                                 # 등록
```

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Baren (바렌, blademaster), a mercenary captain. Save it as art/inbox/sheet_captain_blademaster.png (do not rename).

REFERENCES:
  - art/requests/phase3/captain_blademaster/guide_strip.png (layout + poses, the most important reference)
  - art/requests/phase3/captain_blademaster/guide_1_idle.png .. guide_4_hit.png (the same poses, larger)
  - art/requests/phase3/captain_blademaster/concept.png (DESIGN ONLY)
  - art/requests/phase3/captain_blademaster/concept_pixel.png (how simple the shapes must stay)
  - art/requests/phase3/captain_blademaster/portrait.png (face and hair only)

CHARACTER: a katana (slim curved single-edged sword, dark wrapped hilt, small round guard), held with both hands; messy dark-brown hair; white headband with two long tails (keep the tails short enough to stay clear of the neighbouring figure); thin scar across one cheek; fitted dark-navy tunic; dark-crimson half cape / hip wrap hanging on one side; leather belt and a cross strap; dark trousers, brown boots; calm, focused expression.

GAME COLOURS (keep close, muted): skin #e0ac7e, hair #2b1d14, outfit #3a1018, accent #e8e4d8.

FIX (do not reproduce the draft here):
  - concept.png (#5) is the LOOK reference; concept_pixel.png (#8) shows how SIMPLE the shapes must stay: big clear shapes, few folds, few small details, so it survives downscaling to 64 px
  - this image becomes the STYLE ANCHOR for the eight other captains: keep it clean and exemplary

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

POSES (match the guide mannequin exactly; it only fixes pose, proportions, size and position - its colours, round head and plain clothes are placeholders):
  1. idle: katana held diagonally in front, both hands on the hilt, as in the guide
  2. attack wind-up: katana raised high behind the head with both hands, as in the guide
  3. attack strike: diagonal downward cut, arms and blade fully extended forward, as in the guide
  4. hit reaction: recoiling backwards, wincing, katana still in hand

STYLE:
  - high-quality HD pixel art for a modern 2D fantasy tactics game (crisp pixel clusters, no blur, no painterly rendering)
  - 4 heads tall (head = 1/4 of the standing height), exactly the proportions and limb lengths of the guide; NOT chibi, NOT realistic
  - front three-quarter view, facing RIGHT; light from the upper left
  - muted, desaturated, hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones
  - dark, desaturated, NON-black outline used selectively (no thick uniform black lineart), soft rim light on one side
  - readable at 1x game size (the idle figure becomes ~64 px tall on a dark battlefield): big clear shapes, strong silhouette, few tiny details

DELIVERABLE:
  - ONE PNG, 1536x1024 (landscape), the SAME character drawn 4 times in one row, left to right: idle, wind-up, strike, hit
  - each figure exactly where guide_strip.png has it: same size, same scale, same pose, same limb lengths
  - all four pairs of feet on one common baseline at y = 870 (85% of the height); the idle figure is about 401 px tall (39% of the height, 110 px per head) - the same size for every character
  - figures and weapons never touch each other or the image border (keep >= 32 px between figures)
  - background: perfectly flat solid magenta #FF00FF everywhere (or transparent) - no gradient, floor, cast shadow or scenery
  - NO text, labels, numbers, frames, grid lines, watermark; NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles)

SELF-CHECK before saving (redraw if any fails):
  [ ] image is 1536x1024, background exactly #FF00FF (or transparent), nothing else on it
  [ ] 4 figures in one row, idle / wind-up / strike / hit, matching the guide poses
  [ ] feet of all four on the same baseline (~85% height); same size in all four; idle ~39% of the height (~401 px)
  [ ] 4 heads tall; front three-quarter view facing right; light from the upper left
  [ ] same face, hair, outfit, colours and weapon in all four poses; exactly the weapons listed (no extra weapons)
  [ ] every "fix" above applied
  [ ] no text, no floor, no shadow, no effects, no projectiles; figures do not touch each other or the border
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```
