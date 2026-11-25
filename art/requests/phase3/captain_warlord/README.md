# 가르마크 — 백전의 전쟁군주 (전쟁군주) · `sheet/captain/warlord`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_warlord.png` + `art/inbox/NOTES.md`의 「3단계 — 가르마크」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 가르마크: 거구(그래도 4등신·같은 배율), 붉은 장발과 땋은 붉은 수염, 코·뺨 흉터, 뿔 달린 철투구, 회색 늑대 모피, 진홍 망토, 사자 걸쇠. 초상화 등의 대검을 무기로(가이드 katana). 스킬명·요청서는 '전쟁 도끼'라 충돌 — 양손 도끼로 바꿀지 주인 확인. 칼날은 몸 바깥, 회색 강철+진한 외곽선.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json warlord` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Garmak (가르마크), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_warlord.png on the art-inbox branch.

CHARACTER: Garmak: huge, broad-shouldered man in his forties, long dark-red hair and a big braided red beard, heavy brows, scar across the nose and cheek, grey iron horned helmet with curved ivory horns and a star emblem, grey wolf-fur mantle, crimson cloak, iron lion-head round clasp, brown leather harness with square buckle, two-handed greatsword with a red-wrapped grip and round pommel (carried on his back in the portrait). Class: 전쟁군주 (warrior). Colours: skin #c68a5c, hair #8c2f2f (red, beard braided), outfit #5a3a1a (brown leather), accent #d6455d (crimson cloak); fur grey-brown ~#8a7a6a, iron ~#8a8a8a.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon follows the PORTRAIT: a heavy two-handed greatsword (red-wrapped grip, round pommel, broad straight blade), not a katana and not an axe (his skill is named '전쟁 도끼'; owner may swap to a two-handed war axe — then keep the same guide) / Blade stays outside the body silhouette on magenta in every pose; give it a neutral grey steel with a dark outline so it reads against the grey fur and red cloak / Bulky and broad (wide chest, thick arms) but still exactly 4 heads tall and the same scale as other captains — not a giant; horned helmet stays on in every pose and the horns are not counted in the height / Fur mantle and crimson cloak kept as large simple shapes; cloak must not cover the sword or sword arm / No rally-horn, banner or effects (his rally skill is drawn by the engine).

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: two-handed greatsword held diagonally in front, point forward-up, wide low stance.
2 wind-up: sword raised high over the rear shoulder, weight back, blade clear above and behind the helmet horns.
3 strike: step-in lunge, sword cut down and forward at full extension.
4 hit: torso thrown back, weight on the rear leg, head jerked back, sword dropped low.

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

DELIVERY: commit art/inbox/sheet_captain_warlord.png and add a section "3단계 — 가르마크" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
