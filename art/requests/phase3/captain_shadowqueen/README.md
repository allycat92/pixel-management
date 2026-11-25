# 니클라 — 그림자 길드의 여왕 (밤의 여왕) · `sheet/captain/shadowqueen`

## THIS ROUND (overrides anything below that disagrees)

```
KIND: fix (pose 1 only). BASE: art/inbox/sheet_captain_shadowqueen.png @ 0cc6046 on art-inbox (accepted). Poses 2, 3 and 4 stay exactly
as they are, pixel for pixel.
FIX pose 1 (idle) only - owner, 2026-11-26: "why raise one sword in idle? With one blade hidden behind the body and held down it would
look natural." Our request asked for the raised blade; that was our mistake.
  - keep the same low, ready stance, face, hood, hair, cloak, size (idle ~420 px) and feet (soles on y=870);
  - BOTH blades DOWN: near hand low at her side, its blade angled down and slightly forward, tip near the front knee, on the background;
  - far arm hangs down behind her: the far blade is mostly hidden behind her body and cloak - only its lower part and tip show behind
    the rear leg (here, and only here, a blade may be partly behind the body);
  - relaxed but dangerous: shoulders loose, weight slightly forward - she can spring into the X wind-up of pose 2.
DELIVER: art/inbox/sheet_captain_shadowqueen.png (overwrite, all four poses). NOTES "## sheet/captain/shadowqueen - 니클라 대기 자세".
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
- 요점: 니클라: 진홍 테 짙은 자주빛 후드·망토, 금 문장 걸쇠, 긴 청흑색 웨이브 머리, 루비 귀걸이·펜던트, 금 버클 가죽 띠. 무기: 초상화에서 등에 멘 쌍검(곧은 강철 날 약 머리 2개 길이, 붉은 손잡이, 금 코등이·둥근 금 자루끝)을 양손에 하나씩 든다(주인 결정 11-26). 동작: 대기 = 두 칼을 모두 아래로 — 가까운 칼은 옆에 낮게, 먼 칼은 몸 뒤에 반쯤 가려짐 / 준비 = 두 팔을 어깨 뒤로 교차해 X 자로 크게 감는다 / 타격 = X 를 풀며 낮게 돌진하는 가위 베기 / 피격 = 뒤로 젖히며 두 날이 양옆으로.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json shadowqueen` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Nikla (니클라), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_shadowqueen.png on the art-inbox branch.

CHARACTER: Nikla, queen of the shadow guilds, elegant dangerous woman in her thirties, lithe build, long wavy blue-black hair, tan skin, dark-red eyes, faint scar on the cheek, knowing smile, deep plum-black hood and cloak with crimson trim and a gold emblem clasp, ruby earring and pendant, dark corset with gold-buckled leather belts, dark boots, long dagger with a red-wrapped grip and gold guard. Class: 밤의 여왕 (rogue). Colours: skin #e0ac7e, hair #1b1420 (long, blue-black), outfit #1a0a2a (deep plum, painted dark charcoal-violet), accent #d6455d (crimson trim), gold fittings.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: TWIN SHORT SWORDS, one in EACH hand (the pair she carries on her back in the portrait: straight steel blades about 2 heads (~220 px) long, red-wrapped grips, gold crossguards and round gold pommels) - owner decision 2026-11-26: she fights with both blades; nothing stays on her back / each blade is bright neutral steel (~#d8dde3, no blue or violet tint), 1 px dark outline; in wind-up, strike and hit both blades are on the magenta background outside the body and never overlap each other; in idle the far blade may be partly hidden behind her body / dark outfit vanishes on dark ground: paint it dark charcoal-violet (not black), cool rim light on the upper-left edges, slightly lighter outline / crimson trim stays red (highlights toward orange-red, never pink); plum lit side stays dark violet (magenta rule) / hood up in every pose with the face visible; no shadow smoke, afterimages or trails (the engine draws the shadow flurry of her 4-hit dash '그림자 난무').

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: relaxed low assassin stance, BOTH blades held DOWN: near blade low at her side, tip angled down and slightly forward beside the front knee; far arm hangs down so the far blade is mostly hidden behind her body and cloak, only its lower part and tip showing behind the rear leg (owner 2026-11-26: raising one blade in idle looked odd).
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
