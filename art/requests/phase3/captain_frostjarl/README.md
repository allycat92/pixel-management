# 비요른 — 서리 협곡의 영주 (서리 영주) · `sheet/captain/frostjarl`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_frostjarl.png` + `art/inbox/NOTES.md`의 「3단계 — 비요른」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 비요른: 금 고리로 묶은 앞 땋은머리 둘, 금발 긴 머리·수염, 뺨 흉터, 투구 없음, 은백 테 청회색 갑옷, 어깨 눈송이 문장, 흰 서리 모피 망토. 무기는 이야기·스킬대로 양손 수염도끼(초상화 등의 칼자루는 그리지 않음 — 주인 확인 권장). 서리는 색으로만, 얼음 빛·입자 없음.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json frostjarl` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Bjorn (비요른), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_frostjarl.png on the art-inbox branch.

CHARACTER: Bjorn, frost jarl man in his thirties, tall broad build, long wavy blond hair with two thick front braids bound by gold rings, full blond beard, blue eyes, diagonal scars on the cheek, small gold earring, no helmet, slate-blue armoured tunic with silver-white trim and a snowflake emblem on the pauldron, huge white frosted fur mantle on the shoulders, dark trousers, fur-trimmed boots, long-hafted bearded war axe. Class: 서리 영주 (warrior). Colours: skin #f5d6b8, hair/beard #e3c565 (long), armour #4a6a8a (slate blue), accent #e8eef2 (white fur and trim, shaded pale blue-grey), axe steel.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: the guide katana is a placeholder: draw a long-hafted two-handed bearded Dane axe (axe head where the blade tip is) — 'frost axe' from his story and skills; do NOT draw the sword hilt that shows on his back in the portrait / the axe head stays outside the body silhouette on the background in every pose, never in front of the fur mantle / frost = painted colour only: white fur and pale-blue rime on armour and axe; NO ice glow, mist, snowflakes or particles / the fur mantle stays compact (no huge pelt reaching the neighbour); shade the white fur pale blue-grey, never pure white, with a dark outline / both blond braids and the snowflake pauldron stay visible; no helmet (as the portrait).

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: wide braced stance, axe held diagonally in front with both hands, head up to the right, clear of the mantle.
2 wind-up: weight on the back leg; axe raised high over the rear shoulder in both hands, head behind and above the head.
3 strike: step-in lunge; axe cleaving down and forward at full extension, head out in front of the front foot.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, braids swinging, axe dropped low in the near hand, free arm flung up.

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

DELIVERY: commit art/inbox/sheet_captain_frostjarl.png and add a section "3단계 — 비요른" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
