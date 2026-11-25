# 아스텔 — 마탑의 마지막 제자 (마탑 계승자) · `sheet/hero/astel`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_hero_astel.png` + `art/inbox/NOTES.md`의 「3단계 — 아스텔」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.

## Prompt for GPT

```
TASK: draw the battle sprite strip of Astel (아스텔), a special mercenary of the guild, as ONE new PNG:
art/inbox/sheet_hero_astel.png on the art-inbox branch.

CHARACTER: 아스텔: young man scholar-mage, glasses, purple robes with gold embroidery, floating spellbook. Class: 마탑 계승자 (mage). Colors: skin #f2c9a0, hair #c9c2b8 (long), outfit main color #3a1a5a, accent color #f2d24b. Weapon: staff.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: the spellbook is held in the free hand or hangs open at the belt — it does NOT float (no floating objects, no glow) / glasses visible; purple robe with gold embroidery as large simple shapes.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: weapon held ready in the near hand, free hand low, wide stance.
2 wind-up: gathering: weapon raised, free hand drawn back.
3 strike: casting / striking: free hand thrust forward with an open palm (or the weapon swung forward) — NO glow, NO orb, NO effect.
4 hit: torso thrown back, weight on the rear leg, head jerked back, weapon dropped low.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · weapon matches NOTES · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.

DELIVERY: commit art/inbox/sheet_hero_astel.png and add a section "3단계 — 아스텔" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
