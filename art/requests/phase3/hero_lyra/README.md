# 리라 — 가면 쓴 의적 (가면 의적) · `sheet/hero/lyra`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `none`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_hero_lyra.png` + `art/inbox/NOTES.md`의 「3단계 — 리라」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.

## Prompt for GPT

```
TASK: draw the battle sprite strip of Lyra (리라), a special mercenary of the guild, as ONE new PNG:
art/inbox/sheet_hero_lyra.png on the art-inbox branch.

CHARACTER: 리라: young woman in a white half-mask, dark violet outfit, hood, quick daggers, mischievous smile. Class: 가면 의적 (rogue). Colors: skin #f5d6b8, hair #8c2f2f (long), outfit main color #2a1a3a, accent color #e8e4d8. Weapon: dagger.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: ONE dagger in reverse grip in the near hand (a second dagger may hang sheathed at the belt) / white half-mask stays on in every pose, hood up.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: crouched ready stance, one dagger in reverse grip in the near hand, free hand guarding.
2 wind-up: wind-up: dagger arm drawn back high, body coiled.
3 strike: strike: lunge forward, dagger slashing across at full extension.
4 hit: torso thrown back, weight on the rear leg, head jerked back, dagger hand flung out.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · weapon matches NOTES · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.

DELIVERY: commit art/inbox/sheet_hero_lyra.png and add a section "3단계 — 리라" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
