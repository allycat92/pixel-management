# 나린 — 바람을 쫓는 사냥꾼 (바람 사냥꾼) · `sheet/captain/windhunter`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `bow`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_windhunter.png` + `art/inbox/NOTES.md`의 「3단계 — 나린」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 나린: 갈색 피부, 바람에 날리는 긴 흑갈색 머리, 꼬리 달린 녹색 머리띠, 금 귀걸이, 진녹색 망토+연두 장식, 나뭇잎 브로치, 금테 나무 장궁, 등에 화살통. 가이드 무기 bow. 화살은 준비 자세에서만, 날아가는 화살·바람 효과 없음. 머리카락은 뒤로 날려 활을 가리지 않게.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json windhunter` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Narin (나린), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_windhunter.png on the art-inbox branch.

CHARACTER: Narin: lean, tanned woman in her twenties, very long wild dark-brown hair blowing back, green headband with two long trailing tails, calm narrow eyes, small gold hoop earring, dark forest-green hooded cloak/mantle with lime-green trim and a lime leaf-shaped brooch, gold toggle clasps, brown leather cross-strap with square buckle, brown wooden longbow with gold bands, quiver of white-fletched arrows on her back. Class: 바람 사냥꾼 (archer). Colours: skin #c68a5c, hair #2b1d14 (long), outfit #2a4a3a (dark forest green), accent #a7d26a (lime trim, headband); secondary: brown leather #5a3a22-ish, gold fittings #d9a441-ish.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon: a plain brown wooden longbow with gold grip bands (as in the portrait), held in the far-forward hand so the whole limb and string sit on magenta outside the body; one bow only / Quiver with a few white-fletched arrows stays on her back; an arrow appears only nocked in the wind-up pose, never in flight in the strike pose (the engine draws projectiles) / Hair is long and windswept like the portrait but kept as a compact mass streaming BEHIND her (to the left) so it never covers the bow, bow arm or face; headband tails stream back with it / Green headband, gold hoop earring and lime leaf brooch stay visible in every pose; cloak is dark green with clear lime trim so it does not merge into dark terrain / No wind lines, leaves, glow or motion effects even though she is the 'wind' hunter.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: bow held low in front in the forward hand, string side facing her, ready, wide stance with bent knees.
2 wind-up: full draw: arrow nocked, string pulled back to the cheek, bow arm straight out in front of the body on magenta.
3 strike: release: bow arm extended, string straight, drawing hand flung far back behind the shoulder, NO arrow in flight.
4 hit: torso thrown back, weight on the rear leg, head jerked back, bow dropped low-forward clear of the body.

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

DELIVERY: commit art/inbox/sheet_captain_windhunter.png and add a section "3단계 — 나린" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
