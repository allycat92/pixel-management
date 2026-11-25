# 그롬 — 피의 투기장 챔피언 (투기장 패왕) · `sheet/hero/grom`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_hero_grom.png` + `art/inbox/NOTES.md`의 「3단계 — 그롬」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.

## Prompt for GPT

```
TASK: draw the battle sprite strip of Grom (그롬), a special mercenary of the guild, as ONE new PNG:
art/inbox/sheet_hero_grom.png on the art-inbox branch.

CHARACTER: 그롬: massive clan warrior man, brown skin, scarred, arena champion belt, greatsword. Class: 투기장 패왕 (warrior). Colors: skin #8fae6a, hair #2b1d14, outfit main color #7a2418, accent color #f2c94c. Weapon: sword.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: weapon: a heavy two-handed greatsword (European), not a katana; massive build but still 4 heads tall / skin colour exactly as in the portrait / arena champion belt clearly visible.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: two-handed sword held diagonally in front, wide low stance.
2 wind-up: wind-up: sword raised high over the shoulder, weight back.
3 strike: strike: step-in lunge, sword cut down and forward at full extension.
4 hit: torso thrown back, weight on the rear leg, head jerked back, sword dropped low.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · weapon matches NOTES · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.

DELIVERY: commit art/inbox/sheet_hero_grom.png and add a section "3단계 — 그롬" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
