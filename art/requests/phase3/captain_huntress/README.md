# 키아라 — 숲의 덫꾼 (덫사냥꾼) — GPT handoff (`captain_huntress`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`, `art/STYLE.md`(전투 캐릭터). 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.

## 주인용 요약 (한국어)

- 순서: **5번째** — 승인된 바렌 그림(`art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_huntress.png` (id `sheet/captain/huntress`)
- 무기: posekit `bow` 마네킹 → a short recurve bow, quiver of arrows on the back
- 자세(posekit 프레임): ① 대기 `idle_0` ② 공격 준비 `attack_2` ③ 공격 타격 `attack_3` ④ 피격 `hit_0`
- 초안에서 가져올 것: 높게 묶은 적갈색 포니테일, 황토색 머리띠, 주근깨, 올리브색 후드 상의, 가죽 조끼, 허리의 밧줄 뭉치, 등의 화살통, 짧은 활.
- 고칠 것: 초안의 큰 활 → 가이드 크기의 짧은 활. 화살은 당길 때(준비)만, 쏜 뒤(타격)에는 날아가는 화살 없음(엔진이 그린다).
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
python3 tools/art/sheets.py art/inbox/sheet_captain_huntress.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_huntress.png                                 # 등록
```

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Kiara (키아라, huntress), a mercenary captain. Save it as art/inbox/sheet_captain_huntress.png (do not rename).

REFERENCES:
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch = the APPROVED STYLE ANCHOR (Baren). Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly
  - art/requests/phase3/captain_huntress/guide_strip.png (layout + poses, the most important reference)
  - art/requests/phase3/captain_huntress/guide_1_idle.png .. guide_4_hit.png (the same poses, larger)
  - art/requests/phase3/captain_huntress/concept.png (DESIGN ONLY)
  - art/requests/phase3/captain_huntress/portrait.png (face and hair only)

CHARACTER: a short recurve bow, quiver of arrows on the back; long auburn hair in a high ponytail; ochre headband; freckles; olive-green hooded tunic; brown leather vest; rope coil on the belt; quiver on the back; dark trousers, brown boots.

GAME COLOURS (keep close, muted): skin #e0ac7e, hair #a8642a, outfit #4a5a2a, accent #c58f1e.

FIX (do not reproduce the draft here):
  - the draft bow is very large: draw a short bow the size of the guide bow
  - an arrow appears ONLY on the drawn bow in the wind-up; after the release (strike) there is NO flying arrow (the engine draws projectiles)

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

POSES (match the guide mannequin exactly; it only fixes pose, proportions, size and position - its colours, round head and plain clothes are placeholders):
  1. idle: bow held low in front, ready, as in the guide
  2. attack wind-up: full draw: arrow nocked, string pulled back to the cheek
  3. attack strike: release: bow arm extended, string straight, drawing hand flung back, no arrow
  4. hit reaction: recoiling backwards, wincing, bow still in hand

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
