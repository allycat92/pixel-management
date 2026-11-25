# 모르데카이 — 마귀 사냥꾼 (마귀 사냥꾼) · `sheet/captain/demonhunter`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_demonhunter.png` + `art/inbox/NOTES.md`의 「3단계 — 모르데카이」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 모르데카이: 50대, 깊은 숯색 후드 망토+잿빛 테두리·십자 문양, 회색 머리·짧은 회색 수염, 주름진 얼굴, 가슴에 은탄 탄띠, 십자 박힌 가시 철퇴. 가이드 staff(세라핀식). 총·석궁 없음, 날아가는 은탄·빛 효과 없음. 철퇴 머리는 망토 바깥, 후드 계속 씀.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json demonhunter` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Mordecai (모르데카이), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_demonhunter.png on the art-inbox branch.

CHARACTER: Mordecai: grizzled, sturdy man in his fifties, deep dark-charcoal hood and long hooded cloak with ash-grey trim and cross motifs, grey hair strands and a short grey beard, deeply lined scowling face, bandolier of large silver bullets/cartridges across the chest, small bone-white cross pendant, holding a holy mace: dark wrapped haft with a gold band and a spiked round head bearing a cross. Class: 마귀 사냥꾼 (cleric). Colours: skin #e0ac7e, hair #c9c2b8 (grey), outfit #2a2a3a (charcoal), accent #c9c2b8 (ash-grey trim, crosses); silver bullets ~#d8dde3, gold band ~#d9a441.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon: ONE holy mace with a spiked round head marked with a cross (as in the portrait); the staff guide is just the cleric pose base. No gun, no crossbow, no shield / Silver bullets are worn as a chest bandolier only; his '은탄' shot is drawn by the engine — no bullets in flight, no muzzle flash / Mace head stays outside the hood/cloak silhouette on magenta in every pose; outline it darkly and keep it lighter than the cloak so it reads at 64px / Hood up in every pose with the bearded face visible; ash-grey trim drawn as bold lines so the charcoal cloak has edges on dark terrain / No holy light, exorcism glow, runes or smoke.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: mace held ready in the near hand, head out ahead of the shoulder, free hand low near the bandolier, wide stance.
2 wind-up: mace raised high in the near hand, head above and behind the hood, free hand lifted, weight back.
3 strike: lunge; free hand thrust forward open-palmed (the ward); mace held upright behind in the near hand, head clear of the hood and cloak — NO glow, NO effect.
4 hit: torso thrown back, weight on the rear leg, head jerked back in the hood, mace dropped low and out to the side.

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

DELIVERY: commit art/inbox/sheet_captain_demonhunter.png and add a section "3단계 — 모르데카이" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
