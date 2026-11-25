# 마렌 — 퇴역 제독 (퇴역 제독) · `sheet/captain/admiral`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `bow`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_admiral.png` + `art/inbox/NOTES.md`의 「3단계 — 마렌」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 마렌: 은회색 짧은 곱슬머리·볼 흉터의 노제독, 금 견장·닻 문장의 남색 코트. 무기는 석궁(활 가이드 자리, 활처럼 당기지 않음). 초상화대로 모자 없음. 볼트는 준비 자세에만, 사격 연기·포탄 없음. 짙은 남색 코트에 밝은 테두리.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json admiral` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Maren (마렌), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_admiral.png on the art-inbox branch.

CHARACTER: Maren: elderly woman in her sixties, upright lean build, short voluminous wavy grey hair, stern face with a scar on the cheek and age lines, blue eyes, gold drop earring; navy double-breasted admiral's coat with gold piping, gold buttons, gold fringed epaulettes, gold anchor emblem on the lapel, cream cravat; a wooden-stocked crossbow with a steel prod and string. Class: 퇴역 제독 (archer). Colours: skin #f2c9a0, hair #c9c2b8 (short grey), outfit #1a2a5a (navy), accent #f2c94c (gold trim/epaulettes/anchor); portrait extras: cravat cream ~#e0d6c6, crossbow wood ~#8a6a48, steel ~#a8a8b0.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: Real weapon is ONE crossbow (wooden stock, steel prod), not a bow: held with both hands at shoulder/hip, never drawn like a longbow; the guide bow marks where the weapon sits. The crossbow stays outside the body silhouette on the background in every pose / Bare head with the short wavy grey hair as in the portrait (no hat, even though the class data lists one); no pistol, sword or cannon props / A bolt only in the wind-up (loaded); NO bolt in flight, no smoke, no muzzle flash — the 'naval barrage' skill is drawn by the engine / Navy coat is very dark: give it a clear lighter navy rim and keep the gold epaulettes and trim bold so she reads on dark terrain; grey hair must not merge with the cream cravat (separate with outline) / Elderly but steady and dignified: straight back, no hunch.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: composed officer's stance, crossbow held diagonally across the body with the front of the prod forward and up, clear of the coat.
2 wind-up: crossbow raised to the shoulder and aimed forward, bolt loaded, both arms extended, cheek near the stock, weight back.
3 strike: shot — crossbow kicked up by the recoil with the string forward and empty, rear elbow high, no bolt visible.
4 hit: torso thrown back, weight on the rear leg, head jerked back, crossbow dropped low-forward away from the body in one hand.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_admiral.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_admiral.png and add a section "3단계 — 마렌" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
