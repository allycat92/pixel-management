# 카시안 — 파문당한 마검사 (마검사) · `sheet/captain/spellblade`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_spellblade.png` + `art/inbox/NOTES.md`의 「3단계 — 카시안」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 카시안: 긴 물결 은발, 뺨의 두 줄 흉터, 남색 하이칼라 코트+하늘색 장식, 금 별 브로치. 무기는 주인 결정(2026-11-25)으로 청록 룬이 새겨진 장검(가이드 katana, 가이드처럼 두 손으로 쥐는 자세) — 초상화의 수정 지팡이는 쓰지 않는다(얼굴·머리·코트만 초상화에서). 룬은 평평한 하늘색 선, 빛·연기·궤적 없음(마력검 베기는 엔진 효과). 칼날은 몸 바깥, 보라 대신 짙은 남색.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json spellblade` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Cassian (카시안), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_spellblade.png on the art-inbox branch.

CHARACTER: Cassian: tall, elegant man in his thirties, long wavy ash-silver hair to mid-back, stern blue eyes, two thin diagonal scars on the cheek, high-collared dark navy long coat with pale-cyan trim and swirl embroidery on the shoulder cape, small gold four-point star brooch; wields a one-handed rune longsword (straight light-steel blade engraved with flat pale-cyan runes, gold cross-guard, dark wrapped grip). Class: 마검사 (mage). Colours: skin #f5d6b8, hair #c9c2b8 (long), outfit #2a2a6a (dark navy), accent #7fd6e8 (pale cyan trim, blade runes); gold fittings ~#d9a441, blade steel ~#c8ccd2.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon (owner decision): ONE longsword with flat pale-cyan runes along the blade, gold cross-guard, dark grip long enough for a second hand — NOT the portrait's crystal staff (take only face, hair and coat from portrait.png). Hold it as the guide does (both hands on the grip where the guide shows two hands); the guide's blade marks the sword's position and length / Runes are FLAT cyan #7fd6e8 lines on a light neutral-steel blade (~#c8ccd2) with a dark outline: NO glow, no blue smoke, no floating runes or particles (the engine draws the '마력검' slash) / Blade stays outside the head/hair and coat silhouette on magenta in every pose; long hair is kept as a compact mass behind the shoulders / Coat is dark navy-blue, not violet; keep any purple highlights blue-shifted and dark (magenta rule), cyan trim crisp so the coat reads on dark terrain / Cheek scars and the gold star brooch remain visible.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: low guard stance, sword gripped with both hands at the waist, blade angled up and forward ahead of the body on magenta.
2 wind-up: sword raised overhead with both hands, blade pointing back behind and above the head on magenta, weight on the back leg.
3 strike: deep lunge, two-handed down-forward cut with the arms extended, blade angled down and forward in front of the body, tip above knee height — NO trail, NO glow, NO effect.
4 hit: torso thrown back, weight on the rear leg, head jerked back, free arm flung up, sword hanging low in the near hand pointing down-forward away from the body.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.
WEAPON/PROP READABILITY: in every pose keep the weapon outside the body silhouette, over the background, with a 1px dark outline.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · weapon matches NOTES and sits outside the body in every pose · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.

DELIVERY: commit art/inbox/sheet_captain_spellblade.png and add a section "3단계 — 카시안" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
