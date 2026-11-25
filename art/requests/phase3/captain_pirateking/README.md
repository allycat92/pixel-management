# 크림슨 — 붉은 돛의 해적왕 (해적왕) · `sheet/captain/pirateking`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `sword_shield`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_pirateking.png` + `art/inbox/NOTES.md`의 「3단계 — 크림슨」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 크림슨: 금테 검은 삼각모(작은 해골·크림/빨강 깃털), 진홍 웨이브 긴 머리, 갈색 피부, 뺨 흉터 두 줄, 금 귀걸이, 크림색 깃 진홍 코트. 무기는 금 손잡이 커틀러스 하나(가이드 방패는 그리지 않음, 빈 손). 갈고리 사슬은 어깨·허리에 걸린 소품만. 머리와 코트 빨강 구분, 분홍 금지.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json pirateking` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Crimson (크림슨), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_pirateking.png on the art-inbox branch.

CHARACTER: Crimson, confident pirate queen woman in her thirties, athletic build, long wavy crimson hair, tan skin, two slash scars on the cheek, gold hoop earring, sly smile, black tricorne with gold trim, a small skull emblem and a cream-and-red feather, crimson long coat with cream lapels and a cream ruffled shirt, gold chain with a steel hook on the shoulder, dark gloves, dark boots, cutlass with a gold basket guard. Class: 해적왕 (rogue). Colours: skin #c68a5c, hair #8c2f2f (long), coat #7a1a1a (crimson), accent #1b1420 (black hat, gloves, boots — lift to dark charcoal-violet), lapels/shirt cream, trim gold.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: weapon: ONE curved cutlass with a gold basket guard in the near hand; the guide's shield is NOT drawn: the far hand is empty and open as a guard / the hook chain is a prop only: a short gold chain with a steel hook hanging from the shoulder/belt, never swung or thrown (no flying hook) / the blade is bright neutral steel with a 1 px dark outline and always sits on the magenta background, never across the crimson coat / hair and coat are both red: separate them with a dark outline, the cream lapels, and a warmer/browner hair red vs a deeper coat red / the feather stays compact; tricorne on in every pose; skull emblem as one tiny simple shape; no pink highlights (magenta rule).

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: swaggering ready stance, cutlass held forward-low in the near hand clear of the body, free hand open at chest height in front (where the guide holds the shield).
2 wind-up: weight on the back leg; cutlass raised up and back above the shoulder, free hand thrust forward.
3 strike: step-in lunge; cutlass slashing forward and down at full extension, free hand open at chest height in front (where the guide holds the shield).
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hat still on, cutlass arm flung out-back.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
CELL BUDGET (game cell 96): no pixel of any pose - weapon tip, hat, plume included - above y = 340 (pose height <= 530 px). A raised weapon that would cross that line is tilted back or held lower, never shrunk.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.
WEAPON/PROP READABILITY: in every pose keep the weapon outside the body silhouette, over the background, with a 1px dark outline.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · highest pixel at or below y=340 · head ≈110 px · facing right · weapon matches NOTES and sits outside the body in every pose · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_pirateking.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_pirateking.png and add a section "3단계 — 크림슨" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
