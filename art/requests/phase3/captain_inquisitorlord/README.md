# 발타자르 — 심문관장 (대심문관) · `sheet/captain/inquisitorlord`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `staff`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/sheet_captain_inquisitorlord.png` + `art/inbox/NOTES.md`의 「3단계 — 발타자르」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: 발타자르: 금테 진홍 두건 로브, 짙은 갈색 머리, 얼굴 주름·흉터, 가슴의 금 장식 십자 하나, 금 끈, 가죽 장갑. 무기는 긴 자루 철장 철퇴(가이드 지팡이 = 자루, 구슬 자리에 철장 머리). 초상화의 불꽃은 그리지 않음(엔진 효과). 2·3번은 치유·화형 선고 겸용 시전 자세.
- 게임 칸: 96px — 어떤 자세도(든 무기·모자 포함) y=340 위로 올라가지 않게 (자세 높이 530px 이하).
- 생성: `python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json inquisitorlord` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of Balthazar (발타자르), a mercenary captain of the guild, as ONE new PNG:
art/inbox/sheet_captain_inquisitorlord.png on the art-inbox branch.

CHARACTER: Balthazar, severe grand inquisitor in his fifties, lean upright build, swept-back dark-brown hair, deep frown lines and old scars on the cheek, grey eyes, deep crimson hooded inquisitor robe with gold trim and a gold cord across the chest, one large gold ornate cross on the chest, dark leather gloves, dark boots, long-hafted iron mace with a spiked cage head. Class: 대심문관 (cleric). Colours: skin #f2c9a0, hair #2b1d14, robe #4a1a1a (deep crimson), accent #f2c94c (muted gold trim, cord, cross), mace dark iron.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: the guide staff is the mace haft: a long iron mace whose spiked CAGE head (brazier-like) sits where the guide staff has its orb, about the guide staff's length / NO fire: the portrait's 'burning brand' flame is an effect the engine draws; the cage head is plain dark iron, empty, no embers, no glow / ONE simplified gold cross on the chest only (drop the smaller shoulder crosses); hood stays up in every pose with the face visible under it / the dark crimson robe must not merge with the dark outline: lit side a clear warm red, gold trim as large simple lines / slots 2-3 are cast poses: the same sheet is used for his heal and his fire-sentence skill; the casting hand is open and empty.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: upright stern stance, mace held upright at his side in the near hand with the cage head above the shoulder and clear of the hood, free hand low.
2 wind-up: mace raised high and back in the near hand, free hand lifted, weight on the back leg, gathering.
3 strike: lunge; free gloved arm thrust straight forward, palm open toward the enemy (passing sentence); mace held upright behind, head clear of the body.
4 hit: torso thrown back, weight on the rear leg, head jerked back wincing, hood still on, mace dropped low-back.

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
Run `python3 tools/art/check_delivery.py art/inbox/sheet_captain_inquisitorlord.png` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/sheet_captain_inquisitorlord.png and add a section "3단계 — 발타자르" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
