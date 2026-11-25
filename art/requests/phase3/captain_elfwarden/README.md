# 세레니엘 — 숲의 수호대장 (엘프 숲지기) · `sheet/captain/elfwarden`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `bow`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_elfwarden.png` + `art/inbox/NOTES.md`의 「3단계 — 세레니엘」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 세레니엘: 은회색 장발·금 이마띠·뾰족귀, 크림색 잎무늬의 초록 망토를 두른 엘프 순찰대장. 무기는 조각 장식 리커브 장궁 하나. 은발과 크림 무늬가 한 덩어리가 되지 않게 외곽선. 키만 크게 느끼게, 크기는 동일. 화살은 준비 자세에만.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json elfwarden` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Sereniel (세레니엘), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_elfwarden.png on the art-inbox branch.

CHARACTER: Sereniel: tall, slender elf woman of ageless look, very long wavy silver-grey hair with a side braid, long pointed ears, green eyes, serious face; gold circlet with a small green gem, a green leaf hair ornament; dark-green hooded cloak with large cream leaf patterns and cream trim, cream square clasp, brown leather strap; an elegant carved wooden recurve longbow and a brown quiver of cream-fletched arrows on her back. Class: 엘프 숲지기 (archer). Colours: skin #f5d6b8, hair #c9c2b8 (long silver-grey), outfit #2f6a3a (forest green), accent #e8e4d8 (cream leaf patterns/trim); portrait extras: circlet gold ~#d9a441, leaf ornament ~#6a9a4a, bow wood ~#b08a5a.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: Main weapon is ONE elegant carved recurve longbow; bow and string stay outside the body and the long hair on the magenta background in every pose / Long pointed ears and the gold circlet must read at 64px; silver hair is separated from the cream cloak pattern by a clear outline (do not merge hair and cream into one pale blob) / Cream leaf pattern on the cloak as 3-4 big simple leaf shapes, not small noise / Tall and slender but the same 4-head / 110 px head scale as everyone — do not enlarge the figure; distinguish her from Kai (blond male elf) by the silver hair, circlet and patterned cloak / Arrow only in the wind-up; NO arrow in flight, no leaf swirl, no glow.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: poised ranger stance, knees bent, bow held low in front in the near hand, drawing hand near the quiver, long hair behind.
2 wind-up: full draw — arrow nocked, string pulled back to the cheek, bow arm extended straight forward, bow upright clear of the hair.
3 strike: release — bow arm extended, string straight, drawing hand flung far back behind the shoulder, NO arrow in flight.
4 hit: torso thrown back, weight on the rear leg, head and hair jerked back, bow dropped low-forward away from the body.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_elfwarden.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_elfwarden.png and add a section "3단계 — 세레니엘" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
