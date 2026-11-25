# 오토 — 성벽 파괴자 (공성 기술자) · `sheet/captain/siegemaster`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `bow`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_siegemaster.png` + `art/inbox/NOTES.md`의 「3단계 — 오토」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 오토: 황동 고글 달린 회색 챙 투구, 갈색 머리·수염, 뺨 그을음, 황토 테 갈색 가죽 코트, 황토 스카프, 가슴의 스패너. 무기는 가이드 활 대신 무거운 쇠뇌(양손, 몸 앞 배경 위). 볼트는 대기·준비에만, 타격은 반동으로 쇠뇌가 들린 빈 홈 — 날아가는 볼트·투석기 없음.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json siegemaster` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Otto (오토), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_siegemaster.png on the art-inbox branch.

CHARACTER: Otto, siege engineer man in his forties, sturdy build, shoulder-length messy brown hair, full short brown beard, green eyes, soot smudge on the cheek, dark-grey round brimmed steel helmet with brass goggles strapped on it, long dark-brown leather coat with ochre-gold trim, ochre neckerchief, steel wrench hanging on a chest strap, brown boots, heavy wooden crossbow with brass fittings and a steel bow-arm. Class: 공성 기술자 (archer). Colours: skin #e0ac7e, hair/beard #5a3720, coat #5a4a3a (dark brown leather), accent #d9a441 (ochre gold trim, neckerchief, brass), helmet dark grey steel.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: the guide bow is a placeholder: draw a HEAVY CROSSBOW (wooden stock, brass fittings, steel prod across the front) held level in both hands, about as long as the guide bow is tall / the crossbow always sits in front of the body on the magenta background, never laid across the dark coat; prod and stock both readable at 64 px / a bolt is loaded only in idle and wind-up; in the strike the groove is empty and NOTHING flies (no bolt, no smoke, no catapult stone — the engine draws projectiles) / brass goggles on the helmet and the wrench on the chest stay visible in every pose; no catapult, no backpack siege gear / dark coat vs dark ground: keep a clear dark outline plus the ochre trim lines, and a warm rim light on the upper-left edges.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: wide stance, crossbow held low-forward at hip height in both hands, loaded bolt, muzzle pointing right-down, clear of the coat.
2 wind-up: crossbow raised to the shoulder and aimed straight right, cheek on the stock, weight on the back leg, loaded bolt.
3 strike: just fired: crossbow bucked upward about 30 degrees by the recoil, string forward, empty groove, front foot braced, rear elbow flung out.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, crossbow dropped low-forward in one hand, helmet still on.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_siegemaster.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_siegemaster.png and add a section "3단계 — 오토" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
