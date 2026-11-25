# 브로크 — 룬 새기는 대장장이 (룬 대장장이) · `sheet/captain/runesmith`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `katana`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_runesmith.png` + `art/inbox/NOTES.md`의 「3단계 — 브로크」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 브로크: 땅딸막한 구릿빛 수염 대장장이. 실제 무기는 양손 룬 전쟁망치(가이드 양손검 자리). 룬은 평평한 하늘색 선(빛·불꽃 없음). 초상화대로 투구 없음. 체격은 넓게, 크기는 키우지 말고 준비 자세 망치가 칸 위로 넘치지 않게.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json runesmith` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Brok (브로크), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_runesmith.png on the art-inbox branch.

CHARACTER: Brok: stout, barrel-chested man in his forties, broad and stocky (still 4 heads tall), bare head with swept-back copper-orange hair, huge braided orange beard bound with gold rings, heavy brow, scar on the cheek; dark-brown leather-and-steel armour with big rounded grey steel pauldrons and plates engraved with cyan runes, gold trim bands; a heavy two-handed rune warhammer (grey steel block head with a cyan rune, dark wrapped haft, gold collar). Class: 룬 대장장이 (warrior). Colours: skin #e0ac7e, hair #a8642a (copper-orange, braided beard), outfit #6a4a2a (dark brown leather), accent #7fd6e8 (rune lines); portrait extras: steel plate grey ~#8a8890 / light ~#c4c2c6, gold bands ~#d9a441.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Real weapon is ONE two-handed rune warhammer, not a sword: rectangular steel head ~0.6 head wide, haft ~1.5 heads long; the guide's two-handed blade is the placeholder for its position. Keep the hammer head on the magenta background, outside the body and beard, in every pose / Runes are FLAT cyan #7fd6e8 lines on the hammer head and pauldrons — no glow, no light halo, no sparks (the prompt's 'glowing' is done by the engine) / Bare head as in the portrait (no helmet, even though the class data lists one); the big orange beard braid with gold rings must read at 64px / Stocky build: wide shoulders and short thick legs inside the same 110 px head / 4-head scale — do not enlarge the figure; keep the raised hammer within about one head above the hair so the wind-up does not run off the top of the cell / Armour as a few big plates (pauldrons, chest plate, belt), not small rivet noise; no anvil or tongs.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: low wide stance, warhammer held two-handed diagonally in front, head up and forward clear of the beard.
2 wind-up: hammer heaved up and back over the near shoulder, weight on the rear leg, hammer head behind and above the head on the background.
3 strike: step-in lunge, hammer smashed down and forward at full extension, hammer head low in front of the front foot at about knee height (never below the soles line y=870).
4 hit: torso thrown back, weight on the rear leg, head jerked back, hammer dropped low to the side away from the body.

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

DELIVERY: commit art/inbox/sheet_captain_runesmith.png and add a section "3단계 — 브로크" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
