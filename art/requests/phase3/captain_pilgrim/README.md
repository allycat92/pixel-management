# 아멜리 — 맨발의 순례자 (순례 기사) · `sheet/captain/pilgrim`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_pilgrim.png` + `art/inbox/NOTES.md`의 「3단계 — 아멜리」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 아멜리: 금발 땋은 머리·베이지 두건 망토·남색 띠(금 십자)의 맨발 순례자. 무기는 자루 긴 성스러운 철퇴(지팡이 가이드). 네 자세 모두 맨발·발가락 보이게, 두건 유지. 치유 빛·후광 없음.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json pilgrim` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Amelie (아멜리), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_pilgrim.png on the art-inbox branch.

CHARACTER: Amelie: gentle young woman in her twenties, slender, long wavy golden-blonde hair with a braid over one shoulder, calm blue eyes, soft smile; beige hooded pilgrim cloak with a navy-blue hood band and stole embroidered with gold crosses, navy-blue tunic, prayer-bead string with a gold cross at the chest, BARE FEET; a long-hafted holy mace (dark haft, spiked gold-and-steel sun head with a gold cross). Class: 순례 기사 (cleric). Colours: skin #f5d6b8, hair #e3c565 (long), outfit #c8b89a (beige cloak), accent #3d5a9c (navy band/tunic); portrait extras: gold crosses ~#e0b040, mace head steel ~#6a6a78.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Real weapon is ONE long-hafted holy mace (staff-length haft, spiked sun head with a gold cross), held like the guide staff; the mace head stays outside the body silhouette on the background in every pose / BAREFOOT: bare feet with visible toes in every pose — no boots or sandals; the cloak hem must stop above the ankles / Hood up in every pose with the navy band and gold crosses; blonde braid visible outside the hood / Prayer beads with the gold cross hang at the chest as part of the costume (not held up as a second item) / No healing glow, halo, light rays or holy symbols in the air (the engine draws heal effects) / Beige cloak vs magenta-free palette: keep beige shadows toward cool grey-brown, never pink/mauve.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: steady stance, mace held upright in the near hand like a staff with the head above shoulder height in front of the body edge, free hand at the prayer beads.
2 wind-up: mace raised high in the near hand, free hand lifted, weight back, head of the mace above and behind the hood on the background.
3 strike: lunge; free hand thrust forward with an open palm (blessing); mace held upright behind in the near hand, sun head clear of the hood and body.
4 hit: torso thrown back, weight on the rear bare foot, head jerked back (hood stays on), mace dropped low and out to the side.

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

DELIVERY: commit art/inbox/sheet_captain_pilgrim.png and add a section "3단계 — 아멜리" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
