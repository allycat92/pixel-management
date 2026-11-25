# 니클라 — 그림자 길드의 여왕 (밤의 여왕) · `sheet/captain/shadowqueen`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `none`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_shadowqueen.png` + `art/inbox/NOTES.md`의 「sheet/captain/shadowqueen - 니클라」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 니클라: 진홍 테 짙은 자주빛 후드·망토, 금 문장 걸쇠, 긴 청흑색 웨이브 머리, 루비 귀걸이·펜던트, 금 버클 가죽 띠. 손에는 붉은 손잡이 긴 단검 하나, 두 번째 단검은 등에 꽂혀 손잡이만 보이게. 날은 중성 밝은 강철색·1.5배 길이·몸 바깥 배경 위(리라 교훈). 검정 대신 숯빛 보라 + 림 라이트, 빨강은 분홍 쪽으로 가지 않게. 그림자 효과 없음.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json shadowqueen` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Nikla (니클라), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_shadowqueen.png on the art-inbox branch.

CHARACTER: Nikla, queen of the shadow guilds, elegant dangerous woman in her thirties, lithe build, long wavy blue-black hair, tan skin, dark-red eyes, faint scar on the cheek, knowing smile, deep plum-black hood and cloak with crimson trim and a gold emblem clasp, ruby earring and pendant, dark corset with gold-buckled leather belts, dark boots, long dagger with a red-wrapped grip and gold guard. Class: 밤의 여왕 (rogue). Colours: skin #e0ac7e, hair #1b1420 (long, blue-black), outfit #1a0a2a (deep plum, painted dark charcoal-violet), accent #d6455d (crimson trim), gold fittings.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: ONE long dagger (red-wrapped grip, gold guard) in the near hand; the second dagger stays sheathed on her back with only its hilt over the far shoulder — never two blades in hand / the blade is bright neutral steel (~#d8dde3, no blue or violet tint), about 1.5x a normal dagger, 1 px dark outline, and always on the magenta background outside the body (Lyra lesson) / dark outfit vanishes on dark ground: paint it dark charcoal-violet (not black), cool rim light on the upper-left edges, slightly lighter outline / crimson trim stays red (highlights toward orange-red, never pink); plum lit side stays dark violet (magenta rule) / hood up in every pose with the face visible; no shadow smoke, afterimages or trails (the engine draws the shadow flurry).

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: low crouched stance, dagger hand held out to the side away from the cloak with the blade on the background, free hand up as a guard.
2 wind-up: body coiled, dagger arm drawn back high behind and above the head, blade at least 32 px clear of the hood.
3 strike: dashing lunge; dagger arm fully extended forward slashing across, free hand flung back, cloak trailing.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hood still up, dagger hand flung out.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_shadowqueen.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_shadowqueen.png and add a section "## sheet/captain/shadowqueen - 니클라" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
