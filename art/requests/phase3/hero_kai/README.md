# 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) · `sheet/hero/kai`

납품 시운전용 요청서 (dot_queue.md 의 DOT_READY 항목). 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 활) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_hero_kai.png` + `art/inbox/NOTES.md`의 「3단계 — 카이 (시운전)」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.

## Prompt for GPT

```
TASK: draw the battle sprite strip of 카이 (Kai), a special mercenary of the guild, as ONE new PNG:
art/inbox/sheet_hero_kai.png on the art-inbox branch.

CHARACTER: young elf man, pointed ears, long blond hair (tied back or flowing behind so the face stays readable),
green ranger cloak with hood DOWN, light leather armour, silver longbow-styled SHORT bow (the size of the guide bow), quiver on the back.
Class: 은빛 순찰자 (archer). Take the face, hair and outfit design from portrait.png (design only; not its painting style).

COLOURS: skin #f5d6b8, hair #e3c565, cloak/main outfit forest green #2f6a4a, accent off-white #e8e4d8 (trim, bowstring wrap),
leather warm brown, bow limbs silver-grey (neutral, not blue). Muted, hue-shifted shading as in the anchor.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size):
1 idle: bow held low in front, ready, wide stance with bent knees.
2 wind-up: full draw — arrow nocked, string pulled back toward the cheek.
3 strike: release — bow arm extended, string straight, drawing hand flung back, NO arrow in flight (the engine draws projectiles).
4 hit: torso thrown back, weight on the rear leg, head jerked back, bow dropped low-forward.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair/weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks).
MAGENTA RULE: every figure colour must be at RGB distance >= 150 from #FF00FF; never merge figure colours with the background when reducing the palette.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · one bow, one string, arrow only in pose 2 ·
no effects · flat #FF00FF background · no figure colour within distance 150 of #FF00FF.

DELIVERY: commit art/inbox/sheet_hero_kai.png and add a section "3단계 — 카이 (시운전)" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
