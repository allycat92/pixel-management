# 벨라도나 — 저주 거래상 (저주술사) · `sheet/captain/hexer`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_hexer.png` + `art/inbox/NOTES.md`의 「3단계 — 벨라도나」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 벨라도나: 남청 장발·넓은 자주 마녀 모자(해골·초승달)·초록 테두리 코트의 저주 상인. 무기는 초록 보석 박힌 꼬인 나무 지팡이. 손바닥 초록 불꽃은 그리지 않음(효과는 엔진), 보석도 빛나지 않게. 자주색은 분홍으로 밝히지 말 것.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json hexer` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Belladonna (벨라도나), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_hexer.png on the art-inbox branch.

CHARACTER: Belladonna: pale woman in her thirties, slender, very long wavy dark navy-blue hair, sly smirk, dark lips, beauty mark under the eye, gold earrings; huge wide-brimmed dark plum witch hat with a bent tip, green band, bone skull charm and gold crescent; dark plum high-collared coat with green swirl trim and a green gem brooch, fingerless dark gloves with gold bangle; a twisted wooden staff with a coiled top holding a green gem. Class: 저주술사 (mage). Colours: skin #f5d6b8, hair #3a3f6b (long, dark blue), outfit #3a1a3a (dark plum), accent #7ed37e (green trim/gem); portrait extras: skull charm bone ~#e0d4c0, staff wood ~#a08a6a, gold ~#d9a441.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Weapon is ONE twisted wooden staff with a coiled top cradling a green gem; the staff head stays outside the hat brim and body on the background in every pose / NO green curse flame in her palm (the portrait's flame is an effect — the engine draws curse bolts); the gem is flat green with one highlight pixel, no glow; free hand empty and open / The wide witch hat stays on in every pose; it may enlarge the silhouette but must not grow the figure (head stays 110 px) and must not hide the face / Plum outfit and dark hair: keep the lightest plum around #6a3a5e (no pink/violet) and give the dark hair/coat a clear lighter rim so she does not vanish on dark terrain; every colour >=170 from #FF00FF / Green swirl trim as a few bold lines, not fine filigree.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: relaxed caster stance, staff held upright in the near hand slightly in front of the body edge, free hand at the hip with fingers spread.
2 wind-up: staff raised high in the near hand, gem end high behind the hat brim on the background, free hand lifted, body coiled.
3 strike: casting thrust — lunge, free hand pushed forward with an open palm toward the target; staff held upright behind in the near hand, gem head clear of the hat brim; NO flame, orb or glow.
4 hit: torso thrown back, weight on the rear leg, head jerked back with the hat tipped, staff dropped low and out to the side.

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

DELIVERY: commit art/inbox/sheet_captain_hexer.png and add a section "3단계 — 벨라도나" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
