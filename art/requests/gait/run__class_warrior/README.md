# 병과 전사 달리기 · `sheet/class/warrior` → `gait/sheet_class_warrior_run`

**상태: 요청 (2026-11-26, 클라우드).** GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 달리기는 쓰지 않는다. **확정된 달리기 마네킹(`art/requests/guides/run_base/v2/`) 8프레임 위에 캐릭터를 프레임마다 덧그린다.**
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js` 의 `anims.run`)이 코드 달리기와 같은 박자(80ms)로 넘긴다.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리 가이드** = 확정 마네킹 띠 그대로(R1~R4 / R5~R8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게) 위에 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**임을 보여 준다. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선 |
| `concept_800.jpg` | 주인이 고른 디자인 초안(가벼운 사본, 원본 `art/requests/phase3/class_warrior/concept.png`) — 디자인만 |
| `art/inbox/sheet_class_warrior.png` | **승인된 전투 시트 원본**(이 브랜치와 art-inbox 에 있다) — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 납품: art-inbox `art/inbox/gait/sheet_class_warrior_run_a.png` (R1~R4) + `art/inbox/gait/sheet_class_warrior_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「## gait/sheet_class_warrior_run - 병과 전사 달리기」.
- 팔·무기: 방패는 먼 팔에 들고 **가슴 앞에** 그대로(시트와 같이), 칼은 가까운 손에 **낮게, 칼날은 뒤-아래로** — 휘두르지 않는다. 얼굴은 면갑을 내린 그대로.
- 열쇠 색 7개(제복 4 + 장식 3)는 시트와 **정확히 같은 값**으로만 칠한다(엔진이 세력 색으로 바꾼다).
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_class_warrior_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames) of the generic class warrior (전사) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_class_warrior_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_class_warrior_run_b.png  = frames R5 R6 R7 R8
Draw the character OVER the accepted run mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the run look squashed.

REFERENCES (load all; if the sheet or the concept does not load, do not draw - report BLOCKED):
  - art/requests/gait/run__class_warrior/guide_run_a.png, guide_run_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted run mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__class_warrior/size_run_a.png, size_run_b.png = the same frames with guide lines, and on the left
    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_class_warrior.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/gait/run__class_warrior/concept_800.jpg = the design draft (design only).

CHARACTER (unchanged from the accepted sheet): closed steel great helm with the visor DOWN (one dark eye slit, small top spike,
no face shows in any frame), mail coif and mail sleeves, knee-length sleeveless tabard split at the front with the accent trim,
brown belt with a square buckle, brown gloves, dark trousers, tall brown boots, a plain arming sword in the NEAR hand and the
round shield on the FAR arm.

THE RUN (owner's rhythm, already in the mannequin - copy it, do not invent another):
  - Each frame: the legs, the torso lean and the arm swing of that mannequin frame. Joint for joint: hips, knees, ankles, feet,
    shoulders, elbows. The mannequin's big round head is a placeholder: draw the warrior's own helmeted head on the mannequin's
    neck, at the warrior's own size (as in the sheet).
  - R1 contact (near foot lands a little ahead, knee bent) - R2 catch (body drops onto the foot, lowest) - R3 push-off (stance
    leg extends behind, heel up) - R4 FLIGHT (both feet clearly off the ground, legs scissored, body pressed forward and leaning
    the most). R5-R8 = the same with the far foot.
  - Lean forward: about 24 deg (R1/R5), 19 (R2/R6), 29 (R3/R7), 31 (R4/R8). It leans most in flight and rises a little once
    the landing is caught. The hips stay nearly level: the top of the head stays within about 10 px of the same height in all
    8 frames. NO hopping, no bouncing up and down.
  - Feet: copy the mannequin's feet exactly (the standing foot moves back about 69 px per frame from R1 to R3 - that is the
    stride; do not shorten it).

ARMS AND WEAPON:
  - Shield (far arm): held in FRONT of the chest in every frame, face toward the viewer's right as in the sheet. It moves with
    the far arm's rhythm (a little further forward in R6-R8 and R1, pulled in toward the belt in R2-R5) but never swings
    behind the body, and its front rim stays left of x=345 in each slot (keep the elbow bent - do not push it out at arm's
    length).
  - Sword (near hand): held LOW, hand between belt and hip height, swinging with the mannequin's near arm (forward in R2-R5,
    back in R6-R8/R1). The blade points BACK and DOWN (about 40-60 deg below horizontal, steeper when the hand is back) so the
    blade trails behind the hand; the tip shows on the magenta background behind the hip/rear thigh. No raised sword, no
    swing, no slash. Never shorten the blade - change its angle instead.
  - Weapon outside the body silhouette where possible (the tip and most of the blade behind the body; the hilt may overlap the
    hip in R2-R4), 1 px dark outline.
  - Tabard skirt and its split front flap trail back and lag the body by one frame (they lift most in R1/R5, right after the
    flight, and settle in R3/R7).

MUST NOT CHANGE: outfit, colours, proportions, helmet, weapon and shield shapes and sizes, and the SCALE of the accepted sheet.
The body must not be shrunk to fit. KEY COLOURS: the tabard and the shield face use ONLY the exact sheet keys
#263459 #394b78 #52679c #7489be (outfit, dark to light) and the trim/shield band ONLY #3f7a6c #5ea590 #96d1bb (accent), flat
fills; these seven colours nowhere else; steel neutral grey, leather warm brown, outline and shadows warm/neutral dark (as in
the sheet).

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 / R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, sword tip, tabard) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross
    into the next slot);
  - head 110 px scale = the scale of the accepted sheet; the figure about as tall as the mannequin (top of head near y=450-460).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_class_warrior_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_class_warrior_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/class/warrior --gait run --src art/inbox/gait/sheet_class_warrior_run_a.png art/inbox/gait/sheet_class_warrior_run_b.png --pose art/requests/guides/run_base/v2/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS. The third must end without an error and write <temp dir>/sheet_class_warrior_preview_x4.png
and sheet_class_warrior_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at 4x game size): the
warrior must look like the idle warrior running, not squashed or shrunk. (add_gait refuses mannequin pixels: the frames must be
your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_class_warrior_run - 병과 전사 달리기
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, size_run_a/b, sheet_class_warrior.png, concept_800.jpg -> ok / FAILED (reason)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPON lines -
              write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  PROPOSALS: optional
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
