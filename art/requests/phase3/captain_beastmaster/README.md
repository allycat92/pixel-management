# 오르가 — 늑대 무리의 어미 (야수 조련사) · `sheet/captain/beastmaster`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `bow`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_beastmaster.png` + `art/inbox/NOTES.md`의 「3단계 — 오르가」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 오르가: 짙은 피부·흑갈색 장발·흰 전투 칠·회색 늑대 모피 망토의 조련사. 무기는 장궁 하나. 초상화의 늑대는 그리지 않음(늑대는 엔진이 연출, 모피·금 늑대 메달로 표현). 화살은 준비 자세에만, 쏜 뒤 손을 크게 뒤로.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json beastmaster` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Orga (오르가), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_beastmaster.png on the art-inbox branch.

CHARACTER: Orga: dark-skinned woman in her thirties, strong athletic build, long thick dark-brown wavy hair with a braid, stern face, white war-paint stripes on the forehead and across the cheek, gold earrings; huge grey-and-cream wolf-fur mantle over the shoulders fastened with a round gold wolf-head medallion, dark brown leather tunic with brown strap and square gold buckle, headband; a dark wooden longbow with gold-capped tips and a quiver of cream-fletched arrows on her back. Class: 야수 조련사 (archer). Colours: skin #8d5a3b, hair #2b1d14 (long), outfit #5a4a3a (brown leather), accent #d9a441 (gold medallion/tips); portrait extras: wolf fur grey ~#8a8690 with cream ~#e0d4c4 tips, face paint ~#ece6dc.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: Main weapon is ONE longbow (dark wood, gold-capped tips); bow and string stay outside the body silhouette on the magenta background in every pose / The grey wolf from the portrait is NOT drawn (no companion animal, no wolf head on the ground) — the wolf-pack skill is drawn by the engine; the wolf theme lives in the fur mantle and gold wolf medallion / Wolf-fur mantle as a few big jagged grey/cream fur clumps over both shoulders, not pixel noise; keep it from swallowing the bow arm / White face-paint stripes on forehead and cheek must read at 64px (one or two bold pixels-wide strokes) / Arrow only in the wind-up (nocked); NO arrow in flight, no motion lines, no glow.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: wide hunter's stance, knees bent, bow held low in front in the near hand with the bow away from the body, drawing hand resting near the quiver strap.
2 wind-up: full draw — arrow nocked, string pulled back to the cheek, bow arm extended straight forward, bow upright clear of the fur mantle.
3 strike: release — bow arm still extended, string straight, drawing hand flung far back behind the shoulder (clearly further than in the wind-up), NO arrow in flight.
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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_beastmaster.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_beastmaster.png and add a section "3단계 — 오르가" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
