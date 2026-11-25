# 모로 — 항구의 쥐왕 (그림자 두목) · `sheet/captain/shadowlord`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `none`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_shadowlord.png` + `art/inbox/NOTES.md`의 「3단계 — 모로」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 모로: 40대, 쥐 같은 능글맞은 웃음, 후드 밖으로 나온 곱슬 갈색 머리, 수염, 금 귀걸이·반지·사슬, 금테 검자주 망토. 가이드 무기 none + 금 코등이 단검 한 자루. 리라 교훈대로 날은 밝은 강철색·1.5배 길이·항상 망토 바깥. 투척 단검·독 효과 그리지 않음.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json shadowlord` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Moro (모로), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_shadowlord.png on the art-inbox branch.

CHARACTER: Moro: wiry man in his forties, cunning toothy rat-like grin, wavy shoulder-length brown hair spilling out of a deep dark-plum hood, short beard and stubble, small cheek scar, gold hoop earrings, dark plum hooded cloak with gold trim and a gold round brooch, gold chain across the chest, brown leather belt with square buckle, gold rings on his fingers, a single straight steel dagger with a gold crossguard. Class: 그림자 두목 (rogue). Colours: skin #e0ac7e, hair #5a3720, outfit #1a1420 (near-black plum), accent #d9a441 (gold trim, rings, chain); dagger blade neutral steel ~#d8dde3.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon: ONE straight dagger with a gold crossguard in the near hand, where the guide mannequin holds its dagger (the guide's short reverse-grip dagger is the placeholder). The blade must be neutral light steel (~#d8dde3) with a 1px dark outline and about 1.5x a normal dagger length (Lyra lesson) / The dagger sits OUTSIDE the cloak silhouette on magenta in every pose; never in front of the dark cloak where it vanishes at 64px / His skill throws poisoned daggers, but draw NO thrown knives, no knives in flight and no second weapon in hand; no poison drips, smoke or glow / Hood stays up in every pose with the face and grin readable; keep gold trim, gold brooch, chain and rings as bold gold blocks so the near-black outfit has readable edges / Plum shadows/highlights stay dark and desaturated (no pink or bright violet) to keep the magenta distance >= 170.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: crouched ready stance, dagger held forward-low in the near hand out beside the body, free hand raised as a guard, sly grin.
2 wind-up: dagger arm drawn back high behind and above the head, blade clear of hood and cloak on magenta, body coiled.
3 strike: lunge forward, dagger thrust/slash across at full arm extension in front of the body.
4 hit: torso thrown back, weight on the rear leg, head jerked back in the hood, dagger hand flung out to the side away from the cloak.

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

DELIVERY: commit art/inbox/sheet_captain_shadowlord.png and add a section "3단계 — 모로" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
