# 에우리아 — 마지막 대현자 (대현자) · `sheet/captain/archmagus`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_archmagus.png` + `art/inbox/NOTES.md`의 「3단계 — 에우리아」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 에우리아: 주름진 노년 여인, 아주 긴 흰(연보라 음영) 웨이브 머리, 별 장식 금 서클릿, 별 귀걸이, 금별 수놓은 짙은 남색 로브, 연보라 안감, 금 팔각별 브로치. 무기는 금 초승달 지팡이(어두운 원반 + 작은 별, 빛 없음). 모자 없음(초상화대로). 떠다니는 별·마법진 금지, 시전 손은 빈 손바닥.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json archmagus` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Euria (에우리아), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_archmagus.png on the art-inbox branch.

CHARACTER: Euria, the last archmagus, ancient wise woman, slender slightly stooped build, wrinkled serene face, grey eyes, very long wavy white-lavender hair, gold circlet with small star ornaments, gold star-drop earrings, deep navy robe and mantle embroidered with gold stars, lavender inner panel with a gold zigzag pattern, gold eight-pointed star brooch, gold staff with a crescent-moon head around a dark star disc. Class: 대현자 (mage). Colours: skin #f5d6b8, hair #ffffff (long, shaded lavender-grey), robe #1a1a4a (deep navy), accent #f2f2ff (pale silver) with gold #d9a441-family ornaments, inner panel lavender.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: weapon: the gold crescent-moon staff from the portrait, guide staff length; its head is a gold crescent ring around a dark navy disc with a small painted four-point star — NO glow, rays or sparkles / no floating stars, orbs or magic circles; the casting hand is open and empty (the engine draws the arcane beam and falling star) / no hat (as the portrait): gold circlet only; very long hair falls down her back but stays inside the figure's space / white hair shaded lavender/blue-grey (never pink or magenta) and outlined so it does not merge with the pale trim / stars on the robe: a few large gold shapes, not noise; staff head always above or in front of the figure, clear of the hair.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: calm upright stance, staff planted at her side in the near hand with the crescent head above her shoulder, free hand low.
2 wind-up: staff raised high in the near hand, free hand lifted and drawn back, weight on the back leg, gathering.
3 strike: lunge; free arm thrust straight forward, palm open toward the enemy (casting); staff held upright behind, head clear of the body.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hair swinging, staff dropped low.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_archmagus.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_archmagus.png and add a section "3단계 — 에우리아" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
