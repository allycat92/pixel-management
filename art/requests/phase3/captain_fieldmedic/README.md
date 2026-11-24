# 마그다 — 종군 의무관 (야전 의무관) — GPT handoff (`captain_fieldmedic`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`, `art/STYLE.md`(전투 캐릭터). 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.

## 주인용 요약 (한국어)

- 순서: **7번째** — 승인된 바렌 그림(`art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_fieldmedic.png` (id `sheet/captain/fieldmedic`)
- 무기: posekit `staff` 마네킹 → a long-handled spiked mace (the guide staff is the handle; the orb end of the guide staff is where the spiked iron head goes)
- 자세(posekit 프레임): ① 대기 `idle_0` ② 공격 준비 `cast_1` ③ 공격 타격 `cast_2` ④ 피격 `hit_0`
- 초안에서 가져올 것: 높게 묶은 검은 긴 머리, 갈색 피부, 이마 붕대, 긴 야전 코트, 짙은 빨강 스카프·앞치마, 허리 주머니, 긴 자루 철퇴.
- 고칠 것: 완장의 흰 십자 제거(무늬 없는 짙은 빨강 완장). 코트는 흰색이 아니라 따뜻한 회베이지. 치유 빛 금지(엔진). 시전 자세(cast).
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
python3 tools/art/sheets.py art/inbox/sheet_captain_fieldmedic.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_fieldmedic.png                                 # 등록
```

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Magda (마그다, fieldmedic), a mercenary captain. Save it as art/inbox/sheet_captain_fieldmedic.png (do not rename).

REFERENCES:
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch = the APPROVED STYLE ANCHOR (Baren). Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly
  - art/requests/phase3/captain_fieldmedic/guide_strip.png (layout + poses, the most important reference)
  - art/requests/phase3/captain_fieldmedic/guide_1_idle.png .. guide_4_hit.png (the same poses, larger)
  - art/requests/phase3/captain_fieldmedic/concept.png (DESIGN ONLY)
  - art/requests/phase3/captain_fieldmedic/portrait.png (face and hair only)

CHARACTER: a long-handled spiked mace (the guide staff is the handle; the orb end of the guide staff is where the spiked iron head goes); long black hair tied in a high ponytail; tan skin; bandage around the forehead; long field coat; dark-red scarf; dark-red apron / under-dress; pouches on the belt; dark trousers, brown boots; stern, determined expression.

GAME COLOURS (keep close, muted): skin #c68a5c, hair #2b1d14, outfit #e8e4d8, accent #9c3b2e.

FIX (do not reproduce the draft here):
  - REMOVE the white cross: the armband is a PLAIN dark-red armband, no symbol on it (also not on anything else)
  - the draft coat is near-white: paint it warm grey-beige (game colour #e8e4d8 with hue-shifted shading), never pure white
  - NO healing glow or orb: the engine draws the heal VFX; the raised hand is open and empty

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

POSES (match the guide mannequin exactly; it only fixes pose, proportions, size and position - its colours, round head and plain clothes are placeholders):
  1. idle: mace held at her side, ready, as in the guide
  2. attack wind-up: mace raised, free hand lifted (gathering a heal)
  3. attack strike: free hand pushed forward, palm open (healing / blessing), mace held up behind
  4. hit reaction: recoiling backwards, wincing

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
