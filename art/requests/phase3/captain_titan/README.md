# 우르그 — 거인의 피 (거인의 피) · `sheet/captain/titan`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_titan.png` + `art/inbox/NOTES.md`의 「sheet/captain/titan - 우르그」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 우르그: 거구(어깨·팔이 보통 대장의 약 1.5배, 그래도 4등신·머리 110px), 긴 갈색 머리·수염, 뺨의 흰 전투 칠, 금 귀걸이, 흰 모피 깃, 금 장식 갈색 가죽 하네스, 어깨 금 룬 메달. 무기는 금 나선 룬 돌 망치(양손, 머리는 늘 몸 바깥). 바닥 균열·먼지 효과 없음. size_class large — 칸 112 필요할 수 있음.
- 체격 등급: `large` — 4등신·머리 110px 유지, 덩치(어깨·팔)로만 크게. 시트 칸이 더 커야 할 수 있음.
- 게임 칸: 112px — 어떤 자세도(든 무기·모자 포함) y=244 위로 올라가지 않게 (자세 높이 626px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json titan` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Urg (우르그), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_titan.png on the art-inbox branch.

CHARACTER: Urg, last of the giant-blooded tribe, man in his thirties, enormous muscular build with huge shoulders and bare arms, long wild brown hair, short brown beard, blue eyes, pale war-paint scar streaks on the cheek, gold earring, white fur collar, dark-brown leather harness and tunic with gold fittings and a large gold rune medallion on the shoulder, fur-wrapped boots, huge two-handed stone maul with a gold spiral rune and gold-banded haft. Class: 거인의 피 (warrior). Colours: skin #c68a5c, hair/beard #5a3720 (long), leather #5a3a2a, accent #e8c86a (gold fittings, rune, medallion), fur off-white, maul head grey stone.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: the guide katana is a placeholder: draw a HUGE two-handed maul (grey stone/iron block head about 1 head wide with one gold spiral rune, dark wooden haft with gold bands), head where the blade tip is / size_class large: still 4 heads tall with the 110 px head, the size comes from a much broader, heavier body (shoulders and arms about 1.5x a normal captain); the sheet may need a larger cell (like the lancer's 112) / the maul head always sits on the background outside the body (above, behind or in front), never in front of the torso / NO ground crack, dust, shockwave or debris on the strike — the engine draws the earth slam / skin as in the portrait (warm tan, not stone-grey); fur collar and gold medallion stay visible; no tribal sigils beyond the one rune.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: massive wide stance, maul held diagonally across the front in both hands, head up to the right clear of the body.
2 wind-up: weight on the back leg; maul heaved high over the rear shoulder in both hands, head above and behind the head.
3 strike: step-in lunge; maul slammed down and forward at full extension, head out in front of the front foot at about knee height (never below the soles line y=870).
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hair swinging, maul dropped low in the near hand, free arm flung up.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
CELL BUDGET (game cell 112): no pixel of any pose - weapon tip, hat, plume included - above y = 244 (pose height <= 626 px). A raised weapon that would cross that line is tilted back or held lower, never shrunk.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.
WEAPON/PROP READABILITY: in every pose keep the weapon outside the body silhouette, over the background, with a 1px dark outline.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · highest pixel at or below y=244 · head ≈110 px · facing right · weapon matches NOTES and sits outside the body in every pose · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_titan.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_titan.png and add a section "## sheet/captain/titan - 우르그" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
