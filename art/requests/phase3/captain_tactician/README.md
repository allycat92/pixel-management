# 이사벨 — 퇴역 참모 (전술가) — GPT handoff (`captain_tactician`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`, `art/STYLE.md`(전투 캐릭터). 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.

## 주인용 요약 (한국어)

- 순서: **3번째** — 승인된 바렌 그림(`art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_tactician.png` (id `sheet/captain/tactician`)
- 무기: posekit `staff` 마네킹 → a slim black officer's cane / baton with a gold knob (no orb, no crystal)
- 자세(posekit 프레임): ① 대기 `cast_0` ② 공격 준비 `cast_1` ③ 공격 타격 `cast_2` ④ 피격 `hit_0`
- 초안에서 가져올 것: 금테 검은 삼각모, 곧은 짙은 남보라 긴 머리, 숯색 긴 군복 코트, 금 견장·금단추, 검은 장화, 침착한 표정.
- 고칠 것: 초안은 약 6등신 → 4등신으로. 지팡이는 가늘고 짧은 장교 지휘봉(금 손잡이)으로, 손 위치는 가이드 그대로. 시전 자세(cast)로 지휘.
- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.
- 가이드 띠: 머리 하나 = 110.0 px (모든 캐릭터 같음), 대기 자세 키 약 401 px = 그림 높이의 39%, 발 기준선 y=870.

### 파일

| 파일 | 내용 |
|---|---|
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |
| `portrait.png` | 승인된 초상화 (얼굴·머리만 참고) |
| `guide_1_idle.png` | posekit 가이드 832x1216 — 대기 |
| `guide_2_windup.png` | posekit 가이드 832x1216 — 공격 준비 |
| `guide_3_strike.png` | posekit 가이드 832x1216 — 공격 타격 |
| `guide_4_hit.png` | posekit 가이드 832x1216 — 피격 |
| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_captain_tactician.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_tactician.png                                 # 등록
```

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Isabel (이사벨, tactician), a mercenary captain. Save it as art/inbox/sheet_captain_tactician.png (do not rename).

REFERENCES:
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch = the APPROVED STYLE ANCHOR (Baren). Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly
  - art/requests/phase3/captain_tactician/guide_strip.png (layout + poses, the most important reference)
  - art/requests/phase3/captain_tactician/guide_1_idle.png .. guide_4_hit.png (the same poses, larger)
  - art/requests/phase3/captain_tactician/concept.png (DESIGN ONLY)
  - art/requests/phase3/captain_tactician/portrait.png (face and hair only)

CHARACTER: a slim black officer's cane / baton with a gold knob (no orb, no crystal); black tricorne hat with gold trim; long straight dark-indigo hair; charcoal long military coat; gold epaulettes and gold buttons; leather belt; dark trousers, black boots; calm, sharp expression.

GAME COLOURS (keep close, muted): skin #f5d6b8, hair #3a3f6b, outfit #3a3a4a, accent #f2c94c.

FIX (do not reproduce the draft here):
  - the draft is about 6 heads tall: draw her 4 HEADS tall like everyone else (bigger head, shorter legs and coat, as the guide)
  - the guide staff is a placeholder: draw a slim officer's cane instead; it may be shorter than the guide staff, but the hand that holds it stays exactly where the guide hand is
  - the coat must not be longer than the knees, so the legs still read in the wide stance

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

POSES (match the guide mannequin exactly; it only fixes pose, proportions, size and position - its colours, round head and plain clothes are placeholders):
  1. idle: upright commander stance, cane planted at her side, as in the guide
  2. attack wind-up: cane raised, free hand lifted (about to give an order)
  3. attack strike: commanding gesture: free arm thrust forward, pointing with the index finger at the enemy
  4. hit reaction: recoiling backwards, wincing, hat still on

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
