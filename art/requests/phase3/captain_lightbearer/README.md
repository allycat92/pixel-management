# 루치아 — 빛을 든 사도 (빛의 사도) · `sheet/captain/lightbearer`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_lightbearer.png` + `art/inbox/NOTES.md`의 「3단계 — 루치아」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 루치아: 긴 금발 웨이브, 파란 눈, 흰 꽃·금 잎 서클릿과 짧은 흰 베일, 주황 불꽃 자수의 크림색 로브·망토, 금 팔각별 브로치, 흰 장갑. 무기는 태양 머리 철퇴 홀(흰 자루·금 띠, 가이드 지팡이 3/4 길이). 손·머리의 빛, 후광, 반짝임 모두 금지(엔진 효과). 로브는 순백이 아닌 따뜻한 크림+베이지 그늘. 2·3번 치유 시전 자세.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json lightbearer` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Lucia (루치아), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_lightbearer.png on the art-inbox branch.

CHARACTER: Lucia, prophesied apostle of light, young woman around twenty, slender build, very long wavy golden hair, blue eyes, gentle smile, gold leaf circlet with a white flower and a short white veil, layered cream-white robes and cape with orange flame embroidery on the hem, gold eight-pointed star brooch, gold belt, white gloves, sun-headed mace scepter. Class: 빛의 사도 (cleric). Colours: skin #f2c9a0, hair #e3c565 (long), robes #f2ecd8 (warm cream, shaded beige), accent #f39c12 (orange-gold embroidery, star, mace head).
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: weapon: a long sun-mace scepter (white haft with gold bands, spiked sun head) — the guide staff is the haft, about 3/4 of its length, the sun head where the guide orb is / NO light: no glow around the hands, no halo, no rays or sparkles on the mace or brooch — the engine draws her heals; the sun head is a flat gold-orange spiked disc with a pale cream centre / cream robes are never pure white: mid warm beige shadows and a dark outline so she reads on snow; orange flame embroidery as a few large shapes / flower, circlet and veil stay small and on the head; long hair stays inside the figure's space / slots 2-3 are her cast poses (the same sheet is used for her heals); the forward hand is open and empty.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: serene stance, sun-mace held upright at her side in the near hand with the head above the shoulder, free hand low.
2 wind-up: sun-mace raised high in the near hand, free hand lifted and drawn back, weight on the back leg, gathering.
3 strike: lunge; free arm extended straight forward, palm open (blessing); sun-mace held upright behind, head clear of hair and body.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hair and veil swinging, mace dropped low.

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

DELIVERY: commit art/inbox/sheet_captain_lightbearer.png and add a section "3단계 — 루치아" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
