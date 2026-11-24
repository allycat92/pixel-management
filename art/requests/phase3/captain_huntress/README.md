# 키아라 — 숲의 덫꾼 (덫사냥꾼) — GPT handoff (`captain_huntress`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Kiara (키아라, huntress), a mercenary captain. Save it as art/inbox/sheet_captain_huntress.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

CHARACTER: a short recurve bow the size of the guide bow, quiver of arrows on the back; long auburn hair in a high ponytail; ochre headband; freckles; olive-green hooded tunic; brown leather vest; rope coil on the belt; dark trousers, brown boots.

COLOURS (keep close, muted): skin #e0ac7e; hair auburn #a8642a; tunic olive green #4a5a2a; headband and accents ochre #c58f1e.

FIX (do not reproduce the draft here):
  - the draft bow is very large: draw a short bow the size of the guide bow
  - an arrow appears ONLY on the drawn bow in the wind-up; after the release (strike) there is NO flying arrow (the engine draws projectiles)

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: bow held low in front, ready
  2. attack wind-up: full draw: arrow nocked, string pulled back to the cheek
  3. attack strike: release: bow arm extended, string straight, drawing hand flung back, no arrow
  4. hit reaction: torso thrown back, weight on the rear leg, wincing; bow dropped low-forward, drawing hand flung back

REFERENCES (folder art/requests/phase3/captain_huntress/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_huntress ; in a chat they are the attached images):
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

- 순서: **5번째** — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_huntress.png` (id `sheet/captain/huntress`)
- 무기: posekit `bow` 마네킹 → a short recurve bow the size of the guide bow, quiver of arrows on the back
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `attack_2` ③ 공격 타격 `attack_3` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 높게 묶은 적갈색 포니테일, 황토색 머리띠, 주근깨, 올리브색 후드 상의, 가죽 조끼, 허리의 밧줄 뭉치, 등의 화살통, 짧은 활.
- 고칠 것: 초안의 큰 활 → 가이드 크기의 짧은 활. 화살은 당길 때(준비)만, 쏜 뒤(타격)에는 날아가는 화살 없음(엔진이 그린다).
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

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_captain_huntress.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_huntress.png                                 # 등록
```
