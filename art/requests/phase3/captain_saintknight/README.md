# 엘리노어 — 성광의 기사 (성광 기사) · `sheet/captain/saintknight`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_saintknight.png` + `art/inbox/NOTES.md`의 「3단계 — 엘리노어」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 엘리노어: 긴 금발 물결머리+땋은 왕관, 흰 리본, 투구 없음(초상화 우선), 금 테두리 흰 판금, 가슴·어깨 금 별 문양, 금빛 별 모양 가시 철퇴(방패 없음). 세라핀처럼 가이드 staff. 빛·후광 없음, 흰 갑옷은 회청색 음영+진한 외곽선, 철퇴 머리는 금발과 안 겹치게.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json saintknight` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Eleanor (엘리노어), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_saintknight.png on the art-inbox branch.

CHARACTER: Eleanor: noble young woman knight in her twenties, long wavy golden hair with a braided crown and a large white ribbon bow at the back, calm blue eyes, bare-headed (no helmet, as in the portrait), white plate armour with gold trim and gold four-point star emblems on the breastplate and pauldrons, white gauntlets, wielding a gold spiked star-headed mace (morning-star head on a steel haft). Class: 성광 기사 (cleric). Colours: skin #f2c9a0, hair #e3c565 (long), outfit #e8e4d8 (ivory-white plate), accent #f2c94c (gold trim, stars, mace head); armour shadows cool grey ~#9a96a0.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon: a one-handed mace with a gold spiked star-shaped head on a steel haft (not a staff — the staff guide is only the healer pose base); no shield / Bare-headed with the white ribbon and braid as in the portrait (the data's 'helmet' headgear is overridden by the portrait) / Mace head stays outside the head/hair silhouette on magenta in every pose; outline the gold mace head darkly so it does not merge with her golden hair / No holy light, halo, glow or sparkles (the engine draws heal/smite effects) / White armour needs grey-blue shading and a dark outline so it reads on snow and pale terrain; gold star emblems stay large and simple.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: mace held ready in the near hand, head raised beside and ahead of the shoulder, free hand low, wide stance.
2 wind-up: mace raised high in the near hand, star head above and behind the head, free hand lifted, weight back.
3 strike: lunge; free hand thrust forward with an open palm (heal / smite gesture); mace held upright behind in the near hand, star head clear of hair and body — NO glow, NO effect.
4 hit: torso thrown back, weight on the rear leg, head jerked back, mace dropped low and out to the side.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.
WEAPON/PROP READABILITY: in every pose keep the weapon outside the body silhouette, over the background, with a 1px dark outline.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · weapon matches NOTES and sits outside the body in every pose · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.

DELIVERY: commit art/inbox/sheet_captain_saintknight.png and add a section "3단계 — 엘리노어" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
