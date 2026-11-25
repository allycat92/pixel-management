# 테무르 — 초원의 칸 (초원의 칸) · `sheet/captain/khan`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `bow`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_khan.png` + `art/inbox/NOTES.md`의 「3단계 — 테무르」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 테무르: 짙은 갈색 피부, 금고리로 묶은 두 가닥 땋은 머리+긴 흑갈색 머리, 염소수염, 금 귀걸이, 크림색 모피 깃, 금 자수 갈색 유목 코트, 금 원형 걸쇠, 끝이 말린 복합궁. 가이드 bow. 말 없음(도보), 날아가는 화살 없음. 모피·코트는 사막·눈밭에서 안 묻히게 진한 외곽선.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json khan` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Temur (테무르), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_khan.png on the art-inbox branch.

CHARACTER: Temur: strong nomad man in his thirties, dark brown skin, long dark-brown hair in loose locks plus two thick braids bound with gold rings, short goatee, gold hoop earring, heavy cream-white fur collar, brown steppe coat (deel) with gold curling embroidery and a round gold medallion clasp, recurved composite bow with gold bands, quiver of white-fletched arrows on his back. Class: 초원의 칸 (archer). Colours: skin #8d5a3b, hair #2b1d14 (long, braids), outfit #8a5a2a (brown coat), accent #e8c86a (gold embroidery, rings); fur cream ~#e8dcc8.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon: a recurved composite bow with strongly curled tips and gold bands (as in the portrait), held out in front so it sits on magenta outside the body; one bow only / On foot — NO horse (his '기마 돌격' charge is drawn by the engine; do not make a mounted version) / Arrow only nocked in the wind-up; no arrow in flight in the strike pose; quiver stays on the back / Gold-ringed braids, fur collar and gold medallion stay visible; give the cream fur a darker outline and shading so it does not read as a blank blob on snow/desert / Brown coat needs dark outline and darker leather accents so he does not vanish on desert sand.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: recurved bow held low in front, ready, wide stance with bent knees.
2 wind-up: full draw: arrow nocked, string pulled back toward the cheek, bow arm straight out in front.
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

DELIVERY: commit art/inbox/sheet_captain_khan.png and add a section "3단계 — 테무르" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
