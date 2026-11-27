# 병과 마법사 이동 (로브) · `sheet/class/mage` → `gait/sheet_class_mage_run`

**상태: 요청 (2026-11-26, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/class/mage` 로 만듦).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 로브(robe)의 확정 마네킹(`art/requests/guides/robe_base/v1/`) 8프레임 위에 캐릭터를 프레임마다 덧그린다.** 그린 그림은 찌그러뜨리지 않는다(엔진은 칸을 그대로 넘긴다).
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 96ms 박자로 넘긴다 (디딘 발이 붙어 있게: 칸마다 한 걸음의 1/4).

| 파일 | 내용 |
|---|---|
| `guide_robe_a.png` / `guide_robe_b.png` | **자세·자리 가이드** = 확정 로브 마네킹 띠 그대로(G1~G4 / G5~G8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, 뜨는 칸 없음 |
| `size_robe_a.png` / `size_robe_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 마네킹 G1/G5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `art/requests/phase3/class_mage/concept.png` | 디자인 초안 — 디자인만 |
| `art/inbox/sheet_class_mage.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |
| `art/requests/guides/robe_base/v1/` (`pose.json`, `robe_base_preview.gif`, `robe_base.aseprite`) | 마네킹 원본 — 숫자·움직임 확인용 |

- 부류: **로브** — long robe to the shin with sash; only the boots show; wide pointed hat. (tools/art/specs/gait_classes.json)
- 납품: art-inbox `art/inbox/gait/sheet_class_mage_run_a.png` (G1~G4) + `art/inbox/gait/sheet_class_mage_run_b.png` (G5~G8) + `art/inbox/NOTES.md` 절 「gait/sheet_class_mage_run - 병과 마법사 이동 (로브)」 + 「## 판정 — gait/sheet_class_mage_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 팔·무기: 지팡이는 대기처럼 **두 손으로 몸 앞에 비스듬히**(수정이 위·앞) 들고 다닌다 — 짚지 않는다. 로브 자락은 **한 칸 늦게** 흔들리며 **무릎을 늘 가리고**, 장화 끝만 자락 밖으로 나온다.
- 디딘 발: 한 걸음 원본 134.2px(게임 22.2px) → 디딘 발은 칸마다 **정확히 33.5px**(±3, 게임 5.5px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표. (병과 전사 R5 는 디딘 발이 30px 앞에 그려져 한 번 고쳤다.)
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_class_mage_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다 (`--pose art/requests/guides/robe_base/v1/pose.json`).

## Prompt for Antigravity

```
TASK: draw the ROBE GLIDE (hurried, purposeful) CYCLE (8 frames, movement class ROBE) of the generic class mage (마법사) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_class_mage_run_a.png  = frames G1 G2 G3 G4
  art/inbox/gait/sheet_class_mage_run_b.png  = frames G5 G6 G7 G8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
Draw the character OVER the accepted robe mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the moves look squashed.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/robe__class_mage/guide_robe_a.png, guide_robe_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/robe__class_mage/size_robe_a.png, size_robe_b.png = the same frames with guide lines and the planted-toe ticks, and on the left
    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_class_mage.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/class_mage/concept.png = the design draft (design only - not proportions or rendering).
  - art/requests/guides/robe_base/v1/pose.json (the numbers below come from it), art/requests/guides/robe_base/v1/robe_base_preview.gif (the motion at speed), art/requests/guides/robe_base/v1/robe_base.aseprite (the mannequin source -
    you may open it as an underlay and draw on your own layers, but the delivered PNGs contain ONLY your drawing).

CHARACTER (unchanged from the accepted sheet): face hidden in shadow under a wide-brimmed pointed HAT pulled low (compact cone about one head tall, brim no wider than the shoulders, accent hat band) and a HIGH COLLAR over the mouth and chin; long ROBE to the shins with a shoulder capelet, an accent front trim line, accent hem and cuff trim and an accent SASH; brown belt pouches; brown boots; a straight wooden STAFF with a small AMBER crystal on top (warm orange-yellow, no glow).

THE MOVE (owner's three movement classes; robe: loose long cloth: running in it looks unnatural. Fastest natural gait = a hurried, purposeful glide (not a stroll): NO flight phase, NO big knee lift, a small forward lean, short quick steps; the hem swings and hides the knees, only the feet flick out at the hem. It is already in the mannequin - copy it, do not invent another):
  - Each frame: the legs, the torso lean and the arm swing of that mannequin frame. Joint for joint: hips, knees, ankles, feet,
    shoulders, elbows (hands: see ARMS - where the text moves a hand, that is intended, not a deviation).
    The mannequin's big round head is a placeholder: draw the character's own head on the mannequin's neck, at its own size
    (as in the sheet).
  - G1 contact (BOTH feet on the floor under the hem) - G2 down (a small settle onto the near foot) - G3 passing (the far foot slides past just above the floor, 5-10 px) - G4 push. G5-G8 = the same with the far foot.
  - NO FLIGHT, no big knee lift: one sole is on y=870 in EVERY frame (both in G1/G5). A smooth, nearly level glide with a small forward lean and short quick steps - hurried, not a stroll.
  - Lean forward (hip to neck): G1/G5 7.1, G2/G6 7.6, G3/G7 6.8, G4/G8 6.8 deg.
  - Height: the mannequin's head top is at y=438/440/436/435 in G1 G2 G3 G4 (the same in G5 G6 G7 G8): G1 +0, G2 +2, G3 -2, G4 -3 px from G1 (+ = lower) - move your head top by the same amounts (bob 5 px).
  - Stride: one step = 134.2 source px = 22.2 game px; 8 frames = two steps, 96 ms a frame in the game.
  - PLANTED FOOT (the rule the class warrior's R5 needed a fix for): a foot on the floor never slides in the drawing. From its
    contact frame on, the SAME boot moves LEFT by exactly step/4 = 33.5 px per frame (the mannequin: 33-35 px;
    tolerance 3 px) - the engine moves the unit 5.5 game px per frame, so the boot stays still on the ground.
    Toe tip of the planted boot = its FRONT-MOST pixel (the toe; on a tapered boot it may sit a few px above y=870, as on the     mannequin) = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: G1 x=279 -> G2 x=245 -> G3 x=212 -> G4 x=179  (-> G5 x=145 as the REAR foot, heel up, toe still on the floor)
      far foot: G5 x=284 -> G6 x=250 -> G7 x=217 -> G8 x=183  (-> G1 x=148 as the REAR foot, heel up, toe still on the floor)
    Draw the planted boot once, then copy it from frame to frame and only shift it (lift the heel in the push frame); measure
    YOUR toe tip against these numbers (the size_* images mark them with yellow ticks).

ARMS AND WEAPONS:
  - Staff: held diagonally in front of the body with BOTH hands, as in the idle (upper hand at the chest, lower hand at the belt), the top tilted forward, the crystal above the hat brim. It is CARRIED, not planted: it moves only with the hands (the mannequin's small hand swing, at most ~35 px fore-aft), its lower end never goes below y=840, never touches the floor and never passes between the feet; the crystal stays inside x<=351 of the slot.
  - Robe class: follow the mannequin for the legs and torso only. Neither mannequin arm swing nor its elbow path applies (intended, not a deviation): place both arms so they KEEP THE IDLE'S two-hand GRIP on the staff (upper hand at the chest, lower hand at the belt); the grip rides with the torso and moves at most about 35 px fore-aft. The open far hand of the attack cells is attack-only - never use it in the gait.
  - Volume: keep the idle's robe volume - skirt flaring to about the idle's hem width, the capelet, the wide sleeves. The mannequin's narrow skirt is only a placement guide; drawing it as narrow as the mannequin makes add_gait refuse the frames as a mannequin copy. If add_gait still refuses a frame at IoU <= ~0.9, write 막힘 in NOTES - do not distort the drawing.
  - HEM: the robe hides the knees and thighs in EVERY frame (like the mannequin's cloth_front layer); only the boots flick out at the hem - the front boot ahead of / below the hem at contact, the back boot peeking out behind. The hem is pushed out at once by the stepping leg and falls back ONE FRAME LATE (G2/G6 still keep the contact hem shape). Keep the robe length of the idle: the hem trim's lowest point about y 840-850 at the front (about 20-30 px above the floor), higher at the sides; it never touches y=870.
  - The capelet and the sleeves sway a little and lag one frame. The visible sash end hangs on the FRONT of the robe as in the idle and keeps hanging there, with only a small swing across the front panel - never thrown back behind the body.
  - Face: in shadow between the brim and the collar in every frame (no eyes, no skin); the hat stays on and steady.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon and shield shapes and sizes, and the SCALE of the accepted
sheet. The body must not be shrunk to fit - change a weapon's angle instead.
KEY COLOURS (the engine recolours them per faction): the uniform cloth uses ONLY the exact sheet keys #263459 #394b78 #52679c #7489be (outfit, dark to light) and the trim ONLY #3f7a6c #5ea590 #96d1bb (accent), flat fills, on the SAME areas as in the sheet; these 7 colours nowhere else (not on metal, skin, leather, wood, outline or shadows). Steel neutral grey, leather and wood warm brown, outline and shadows warm/neutral dark (as in the sheet).

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_robe_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame); in G1/G5 both soles are on y=870; the lifted sole 3-10 px above it; nothing below y=870 (no weapon tip, no hem);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - head 110 px scale = the scale of the accepted sheet (0.1654 source -> game: the idle is 72 game px tall); the figure about as tall as the idle stood up (the mannequin's head top is near y=435-440).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_class_mage_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_class_mage_run_b.png
  python3 tools/art/add_gait.py sheet/class/mage --gait run --src art/inbox/gait/sheet_class_mage_run_a.png art/inbox/gait/sheet_class_mage_run_b.png --pose art/requests/guides/robe_base/v1/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (NO --flight-slots: every pose must stand on y=870). The third must end without an error and write
<temp dir>/sheet_class_mage_preview_x4.png and sheet_class_mage_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_class_mage_run - 병과 마법사 이동 (로브)
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_robe_a/b, size_robe_a/b, sheet_class_mage.png, concept.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you drew, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPONS
              lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  ## 판정 — gait/sheet_class_mage_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the QA cross-check should look at; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
