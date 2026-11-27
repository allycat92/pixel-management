# 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동 · `sheet/hero/astel` → `gait/sheet_hero_astel_run`

**상태: 요청 (2026-11-27, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/astel` 로 만듦).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 로브(robe)의 확정 마네킹(`art/requests/guides/robe_base/v1/`) 8프레임 위에 캐릭터를 프레임마다 덧그린다.** 그린 그림은 찌그러뜨리지 않는다(엔진은 칸을 그대로 넘긴다).
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 96ms 박자로 넘긴다 (디딘 발이 붙어 있게: 칸마다 한 걸음의 1/4).

| 파일 | 내용 |
|---|---|
| `guide_robe_a.png` / `guide_robe_b.png` | **자세·자리 가이드** = 확정 로브 마네킹 띠 그대로(G1~G4 / G5~G8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, 뜨는 칸 없음 |
| `size_robe_a.png` / `size_robe_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 마네킹 G1/G5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `art/requests/phase3/hero_astel/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_astel.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |
| `art/requests/guides/robe_base/v1/` (`pose.json`, `robe_base_preview.gif`, `robe_base.aseprite`) | 마네킹 원본 — 숫자·움직임 확인용 |

- 부류: **로브** — purple scholar robe with gold embroidery, split shin-length panels and visible trousers between the panels; staff and an open book at the hip. (tools/art/specs/gait_classes.json)
- 납품: art-inbox `art/inbox/gait/sheet_hero_astel_run_a.png` (G1~G4) + `art/inbox/gait/sheet_hero_astel_run_b.png` (G5~G8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_astel_run - 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동」 + 「## 판정 — gait/sheet_hero_astel_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 팔·무기: 가까운 오른손의 지팡이를 들고 먼 손은 비운다. 펼친 책은 허리 곁에 고정하고 트인 로브 자락을 유지한다.
- 디딘 발: 한 걸음 원본 134.2px(게임 22.2px) → 디딘 발은 칸마다 **정확히 33.5px**(±3, 게임 5.5px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표. (병과 전사 R5 는 디딘 발이 30px 앞에 그려져 한 번 고쳤다.)
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_astel_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다 (`--pose art/requests/guides/robe_base/v1/pose.json`).

## Prompt for Antigravity

```
TASK: draw the ROBE GLIDE (hurried, purposeful) CYCLE (8 frames, movement class ROBE) of 아스텔 — 마탑의 마지막 제자 (마탑 계승자) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_astel_run_a.png  = frames G1 G2 G3 G4
  art/inbox/gait/sheet_hero_astel_run_b.png  = frames G5 G6 G7 G8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
Draw the character OVER the accepted robe mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the moves look squashed.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/robe__hero_astel/guide_robe_a.png, guide_robe_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/robe__hero_astel/size_robe_a.png, size_robe_b.png = the same frames with guide lines and the planted-toe ticks, and on the left
    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_hero_astel.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_astel/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/guides/robe_base/v1/pose.json (the numbers below come from it), art/requests/guides/robe_base/v1/robe_base_preview.gif (the motion at speed), art/requests/guides/robe_base/v1/robe_base.aseprite (the mannequin source -
    you may open it as an underlay and draw on your own layers, but the delivered PNGs contain ONLY your drawing).

CHARACTER (unchanged from the accepted sheet): Young scholar-mage with glasses, tied pale hair, purple-and-gold split robe, an open book secured at the near hip, and the gold ring-headed staff shown in the accepted idle.

THE MOVE (owner's three movement classes; robe: loose long cloth: running in it looks unnatural. Fastest natural gait = a hurried, purposeful glide (not a stroll): NO flight phase, NO big knee lift, a small forward lean, short quick steps; the hem swings with the short steps. Match visible boots and trouser gaps to the idle. It is already in the mannequin - copy it, do not invent another):
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
  - Near right hand carries the staff by its idle grip, with travel at most 35 px fore-aft. Keep the shaft vertical or tip the upper head 0–12 deg forward from vertical. Approximate grip-to-head and grip-to-butt distances are 210 and 110 px; keep the butt above y=852 without planting it. Far left hand stays empty close to the waist. Keep the open book at the near hip.
  - Keep the robe's split panels and the trousers visible through the gap as in idle. The front panel stays between the legs; rear cloth settles one frame after the boot and never reaches y=870. Keep the tied hair behind the collar and the short cape on the shoulders.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon and shield shapes and sizes, and the SCALE of the accepted
sheet. The body must not be shrunk to fit - change a weapon's angle instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_robe_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame); in G1/G5 both soles are on y=870; the lifted sole 3-10 px above it; nothing below y=870 (no weapon tip, no hem);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - head 110 px scale = the scale of the accepted sheet (0.1654 source -> game: the idle is 78 game px tall); the figure about as tall as the idle stood up (the mannequin's head top is near y=435-440).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_astel_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_astel_run_b.png
  python3 tools/art/add_gait.py sheet/hero/astel --gait run --src art/inbox/gait/sheet_hero_astel_run_a.png art/inbox/gait/sheet_hero_astel_run_b.png --pose art/requests/guides/robe_base/v1/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (NO --flight-slots: every pose must stand on y=870). The third must end without an error and write
<temp dir>/sheet_hero_astel_preview_x4.png and sheet_hero_astel_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_astel_run - 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_robe_a/b, size_robe_a/b, sheet_hero_astel.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you drew, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPONS
              lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  ## 판정 — gait/sheet_hero_astel_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the QA cross-check should look at; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
