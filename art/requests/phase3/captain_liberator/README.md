# 카토 — 쇠사슬을 끊은 자 (해방 검투사) · `sheet/captain/liberator`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `sword_shield`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_liberator.png` + `art/inbox/NOTES.md`의 「3단계 — 카토」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 카토: 민머리·흉터·근육질 검투사, 맨상체에 가죽 띠, 어깨 위 와인색 천. 무기는 한손 장검 하나(검+방패 가이드, 방패 없음). 빈손은 족쇄 찬 주먹. 양 손목 족쇄는 사슬 2~3고리만(휘두르는 사슬 없음). 칼날은 늘 몸 바깥.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json liberator` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Kato (카토), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_liberator.png on the art-inbox branch.

CHARACTER: Kato: dark-skinned, heavily muscled man in his thirties, shaved head with a pale scar across the scalp and cheek scars, short dark beard, scowl; bare scarred torso with a brown leather strap across the chest and a square steel buckle, torn wine-red cloth over one shoulder, dark brown leather gladiator kilt/pants and wraps; heavy iron shackles on both wrists with short broken chain stubs; a broad one-handed gladiator longsword with a red-wrapped grip and round pommel. Class: 해방 검투사 (warrior). Colours: skin #8d5a3b, hair #2b1d14 (shaved head, beard), outfit #7a4a2a (brown leather), accent #c9c2b8 (iron shackles, steel); portrait extras: shoulder cloth wine red ~#7a2a3a, scar highlight ~#d98a6a.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: Weapon is ONE broad one-handed longsword (red-wrapped grip, round steel pommel, light neutral steel blade with a dark outline) in the near hand; the guide shield is a placeholder — NO shield: the off hand is a clenched fist wearing its broken shackle / Shackles on BOTH wrists are costume: thick grey-iron cuffs with only 2-3 broken chain links hanging; no long swinging chain (it would be a second weapon and a thin line lost at 64px) / Sword blade stays outside the torso on the magenta background in every pose — never across the brown chest or the brown kilt / Dark skin and brown leather are close in value: separate them with the light grey shackles, the steel buckle and a clear dark outline; the wine-red shoulder cloth stays a dark red (not pink) / No sparks, chain-break shards, dust or motion lines.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: wide gladiator stance, knees bent, sword held forward-low in the near hand pointing ahead, shackled off-hand fist raised at chest height.
2 wind-up: sword raised high over the near shoulder, weight back, off-hand fist thrust forward; blade above and behind the head on the background.
3 strike: step-in lunge, sword cut down and forward at full one-handed extension, off-hand fist held at chest height in front (where the guide holds the shield) with the chain stubs hanging.
4 hit: torso thrown back, weight on the rear leg, head jerked back, sword arm flung out low away from the body, off-hand shackle up.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_liberator.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_liberator.png and add a section "3단계 — 카토" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
