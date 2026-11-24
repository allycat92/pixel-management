# 브리긴다 — 철벽의 여단장 (철벽 수호자) — GPT handoff (`captain_ironwall`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of Briginda (브리긴다, ironwall), a mercenary captain. Save it as art/inbox/sheet_captain_ironwall.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

CHARACTER: a spiked mace (morning star) in the near hand and a tall rectangular tower shield with a gold rim on the far arm; the shield is about 2 heads tall (~220 px) and 1 head wide (~110 px), top edge at shoulder height; open steel helmet; long auburn hair in a thick braid; scar across the nose; slate-grey plate armour with gold trim; grey tabard; leather belt; dark trousers, brown boots; broad shoulders, sturdy build.

COLOURS (keep close, muted): skin #f2c9a0; hair / braid auburn #a8642a; armour and tabard slate grey #4a5a6a; trim and shield rim gold #d9a441 (muted).

FIX (do not reproduce the draft here):
  - the BRAID hangs down her BACK on the screen-left side (away from the shield) so it shows in the silhouette in every pose
  - the guide shows a small round shield: draw the tower shield (size above) on the same arm, centred where the round shield is; it may cover part of the body but never the face, and it must keep the 32 px distance to the neighbouring figures
  - the guide shows a sword: draw the spiked mace in that hand, same grip and angle

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: shield raised forward, mace held ready across the body as in the guide
  2. attack wind-up: weight on the back leg; mace raised up and back behind the head, shield kept forward
  3. attack strike: step-in lunge; mace smashing forward and down at full extension, shield pulled in
  4. hit reaction: torso thrown back, weight on the rear leg, wincing; shield up in front of the chest, mace arm dropped down-back

REFERENCES (folder art/requests/phase3/captain_ironwall/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_ironwall ; in a chat they are the attached images):
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

- 순서: **2번째** — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- 결과 파일: `art/inbox/sheet_captain_ironwall.png` (id `sheet/captain/ironwall`)
- 무기: posekit `sword_shield` 마네킹 → a spiked mace (morning star) in the near hand and a tall rectangular tower shield with a gold rim on the far arm; the shield is about 2 heads tall (~220 px) and 1 head wide (~110 px), top edge at shoulder height
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `key_windup` ③ 공격 타격 `key_strike` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 강철 투구, 땋은 적갈색 긴 머리, 콧등 흉터, 금테 두른 회청색 판금갑옷, 회색 겉옷, 금테 탑실드(머리 2개 높이·1개 폭), 철퇴(모닝스타).
- 고칠 것: 땋은 머리는 방패 반대쪽 등 뒤로 늘어져 실루엣에서 보이게. 가이드의 작은 원형 방패 → 같은 자리에 탑실드, 칼 → 철퇴.
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
python3 tools/art/sheets.py art/inbox/sheet_captain_ironwall.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_captain_ironwall.png                                 # 등록
```
