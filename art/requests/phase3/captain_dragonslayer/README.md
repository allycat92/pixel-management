# 지크린데 — 용살자 (용살자) · `sheet/captain/dragonslayer`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_dragonslayer.png` + `art/inbox/NOTES.md`의 「3단계 — 지크린데」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 지크린데: 30대, 사납게 퍼진 긴 금발+옆 땋은 머리, 이마·뺨 흉터, 투구 없음(초상화 우선), 진홍 용비늘 갑옷+주황 금테, 금 코등이 양손 대검. 가이드 katana(그롬과 같은 대검 자세). 칼날 몸 바깥, 불·용 효과 없음, 비늘은 큰 덩어리로.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json dragonslayer` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Sieglinde (지크린데), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_dragonslayer.png on the art-inbox branch.

CHARACTER: Sieglinde: battle-hardened, athletic woman in her thirties, wild long golden-blonde hair with a side braid, stern dark eyes, scar across the brow and a slash scar on the cheek, bare-headed (no helmet, as in the portrait), dark crimson dragon-scale armour with orange-gold trim and layered scale pauldrons, brown leather belt with gold buckle, huge two-handed greatsword with a gold crossguard and red-wrapped grip. Class: 용살자 (warrior). Colours: skin #f2c9a0, hair #e3c565 (long), outfit #6a1a14 (dark crimson scale), accent #f39c12 (orange-gold trim, hilt); blade neutral steel ~#c8ccd2.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon: a very large two-handed European greatsword (gold crossguard, red-wrapped grip), not a katana; the blade stays outside the body silhouette on magenta in every pose / Bare-headed as in the portrait (the data's 'helmet' headgear is overridden); her face scars stay visible / Dragon-scale armour as a few large scale rows and plates, not noisy texture; crimson darks shift toward brown, not toward magenta/pink / No fire, dragon motifs as effects, glow or slash trails; her execution dash is drawn by the engine / Hair is a big mass but kept behind the head so it never covers the sword or face.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: two-handed greatsword held diagonally in front, point forward-up, wide low stance.
2 wind-up: sword raised high over the rear shoulder, weight back, blade clear of the hair mass.
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

DELIVERY: commit art/inbox/sheet_captain_dragonslayer.png and add a section "3단계 — 지크린데" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
