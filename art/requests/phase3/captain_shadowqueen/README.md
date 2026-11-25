# 니클라 — 그림자 길드의 여왕 (밤의 여왕) · `sheet/captain/shadowqueen`

## THIS ROUND (overrides anything below that disagrees)

```
KIND: fix (full redraw of all four poses). BASE: your accepted sheet art/inbox/sheet_captain_shadowqueen.png @ c9d582c on art-inbox -
keep her face, hood, cloak, hair, colours, size (idle 420 px) and soles on y=870 exactly as they are.
WHY: the portrait shows TWIN SWORDS on her back, and her second skill "그림자 난무" is a 4-hit dash. A single dagger was our request's mistake
(Claude's simplification), not yours. Owner, 2026-11-26: every character should move in their own way - Nikla fights with both blades.
CHANGE:
  1. WEAPONS: the two short swords of the portrait, one in EACH hand - straight steel blades ~2 heads (~220 px), red-wrapped grips, gold
     crossguards, round gold pommels; bright neutral steel ~#d8dde3 with a 1 px dark outline; nothing left on her back.
  2. HER OWN MOTION (see "POSES" below - they were rewritten for twin blades):
     idle = low assassin crouch, the two blades an open V in front of her / wind-up = arms crossed behind the near shoulder, the blades an X
     above and behind her - make this anticipation big and clear / strike = the X released in a low dashing scissor slash, both blades ahead /
     hit = thrown back, both blades flung out to the sides.
  Both blades on the magenta background outside the body in every pose, never overlapping each other. No trails or afterimages.
DELIVER: art/inbox/sheet_captain_shadowqueen.png (overwrite), same layout and checks as before. NOTES section "## sheet/captain/shadowqueen - 니클라 쌍검".
```

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `none`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_shadowqueen.png` + `art/inbox/NOTES.md`의 「sheet/captain/shadowqueen - 니클라」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 니클라: 진홍 테 짙은 자주빛 후드·망토, 금 문장 걸쇠, 긴 청흑색 웨이브 머리, 루비 귀걸이·펜던트, 금 버클 가죽 띠. 무기: 초상화에서 등에 멘 쌍검(곧은 강철 날 약 머리 2개 길이, 붉은 손잡이, 금 코등이·둥근 금 자루끝)을 양손에 하나씩 든다(주인 결정 11-26). 동작: 대기 = 낮은 암살자 자세에 두 날이 앞으로 열린 V / 준비 = 두 팔을 어깨 뒤로 교차해 X 자로 크게 감는다 / 타격 = X 를 풀며 낮게 돌진하는 가위 베기 / 피격 = 뒤로 젖히며 두 날이 양옆으로.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json shadowqueen` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Nikla (니클라), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_shadowqueen.png on the art-inbox branch.

CHARACTER: Nikla, queen of the shadow guilds, elegant dangerous woman in her thirties, lithe build, long wavy blue-black hair, tan skin, dark-red eyes, faint scar on the cheek, knowing smile, deep plum-black hood and cloak with crimson trim and a gold emblem clasp, ruby earring and pendant, dark corset with gold-buckled leather belts, dark boots, long dagger with a red-wrapped grip and gold guard. Class: 밤의 여왕 (rogue). Colours: skin #e0ac7e, hair #1b1420 (long, blue-black), outfit #1a0a2a (deep plum, painted dark charcoal-violet), accent #d6455d (crimson trim), gold fittings.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: TWIN SHORT SWORDS, one in EACH hand (the pair she carries on her back in the portrait: straight steel blades about 2 heads (~220 px) long, red-wrapped grips, gold crossguards and round gold pommels) - owner decision 2026-11-26: she fights with both blades; nothing stays on her back / each blade is bright neutral steel (~#d8dde3, no blue or violet tint), 1 px dark outline, and on the magenta background outside the body in every pose (Lyra lesson); the two blades never overlap each other's silhouette / dark outfit vanishes on dark ground: paint it dark charcoal-violet (not black), cool rim light on the upper-left edges, slightly lighter outline / crimson trim stays red (highlights toward orange-red, never pink); plum lit side stays dark violet (magenta rule) / hood up in every pose with the face visible; no shadow smoke, afterimages or trails (the engine draws the shadow flurry of her 4-hit dash '그림자 난무').

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: low assassin crouch, weight forward; near blade held low and forward in a reverse grip, far blade raised by the far shoulder pointing forward - the two blades form an open V in front of her, both on the background.
2 wind-up: body coiled and turned away, both arms drawn back and CROSSED behind the near shoulder so the two blades make an X above and behind her (at least 32 px clear of the hood); this long, clear anticipation is her signature.
3 strike: the X released - dashing low lunge, both arms swept forward and apart in a scissor slash, near blade extended ahead at chest height, far blade sweeping low ahead of the front knee; cloak trailing.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hood still up, both blades flung out to the sides (still in hand, on the background).

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
