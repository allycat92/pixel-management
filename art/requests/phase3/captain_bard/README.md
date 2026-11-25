# 리코 — 노래하는 검 (음유 검객) · `sheet/captain/bard`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `sword_shield`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_bard.png` + `art/inbox/NOTES.md`의 「3단계 — 리코」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 리코: 붉은 장발·깃털 모자·자주 코트의 음유 검객. 실제 무기는 레이피어 한 자루(가이드는 검+방패, 방패 없음, 빈손은 가이드 방패 자리에 편 손). 날은 밝은 강철색으로 늘 몸 바깥. 류트는 등에 메기만(연주·음표 없음). 자주색 밝은 면은 분홍으로 가지 않게.
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json bard` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Rico (리코), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_bard.png on the art-inbox branch.

CHARACTER: Rico: flamboyant young man in his twenties, slim agile build, long wavy dark-red hair in a loose braid over the shoulder, confident smirk, two thin diagonal scars on the left cheek, gold hoop earring; wide-brimmed plum tricorn-style hat with gold trim, gold round badge and a big cream feather; plum frock coat with gold buttons, gold-edged collar and short shoulder cape, cream ruffled jabot; a rapier with a gold cup/swept hilt in hand and a small round-bodied lute strapped on his back. Class: 음유 검객 (rogue). Colours: skin #f2c9a0, hair #8c2f2f (long), outfit #7a2a5a (plum), accent #f2c94c (gold trim/buttons); portrait extras: feather and jabot cream ~#e0d2c0, lute warm brown/ochre.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: Real weapon is ONE rapier (thin straight blade, gold swept/cup hilt) in the near hand; the guide's shield is a placeholder — NO shield: the free hand is empty and open, palm out, exactly where the guide holds the shield / Rapier blade: neutral light steel (~#d8dde3) with a 1px dark outline, about the guide sword's length (long and thin, not longer: it must keep 32 px from the neighbouring poses), always held out on the magenta background, never laid across the plum coat (a thin blade over the dark coat vanishes at 64px) / Lute stays strapped flat on his back as a small prop (top of the neck may peek above the shoulder); never played, never swung, no notes or music symbols / Feathered hat stays on in every pose; feather is a big simple cream shape; long red hair visible below the brim / Plum outfit: keep the lightest plum no brighter/pinker than ~#8e4a62 (shift highlights toward warm grey-rose, not pink) so every colour stays >=170 from #FF00FF / No sparkles, music notes, slash trails or glow (the engine draws the 'battle song' buff).

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: fencer's stance side-on, knees bent, rapier extended forward-low in the near hand, free hand open at chest height in front (where the guide holds the shield); blade fully on the background in front of the body.
2 wind-up: rapier drawn back high beside the head with the point aimed forward, weight on the rear leg, free hand reaching forward for balance; blade above/behind the hat brim, not across the coat.
3 strike: deep fencing lunge, front knee bent, rapier arm at full extension straight forward, free hand open at the chest where the guide holds the shield; the blade reaches past the front foot on the background.
4 hit: torso thrown back, weight on the rear leg, head jerked back (hat stays on), rapier arm flung out and down away from the body, free hand up.

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

DELIVERY: commit art/inbox/sheet_captain_bard.png and add a section "3단계 — 리코" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
