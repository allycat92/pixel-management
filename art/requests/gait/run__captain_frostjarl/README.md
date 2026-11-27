# 비요른 달리기 · `sheet/captain/frostjarl` → `gait/sheet_captain_frostjarl_run`

**상태: 요청 (2026-11-27, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/captain/frostjarl` 로 만듦).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 경량(light)의 이 폴더의 조정된 가이드 8프레임 위에 캐릭터를 프레임마다 덧그린다.** 그린 그림은 찌그러뜨리지 않는다(엔진은 칸을 그대로 넘긴다).
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함).

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리 가이드** = 확정 경량 마네킹 띠를 시트 배율에 맞춰 조정(R1~R4 / R5~R8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `art/requests/phase3/captain_frostjarl/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_captain_frostjarl.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |
| `art/requests/gait/run__captain_frostjarl/pose.json`, `art/requests/guides/run_base/v2/run_base_preview.gif` | 이 요청의 좌표·보폭과 원본 움직임. 덧그리기는 이 폴더의 `guide_run_a.png` / `guide_run_b.png` 위에만 한다. |

- 부류: **경량** — slate-blue armoured tunic of layered silver-trimmed bands and skirt panels to the upper thigh (front flap to just above the knee), big white fur mantle on the shoulders, baggy dark trousers, brown boots with thick white fur cuffs, long-hafted axe. (tools/art/specs/gait_classes.json)
- 납품: art-inbox `art/inbox/gait/sheet_captain_frostjarl_run_a.png` (R1~R4) + `art/inbox/gait/sheet_captain_frostjarl_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_captain_frostjarl_run - 비요른 달리기」 + 「## 판정 — gait/sheet_captain_frostjarl_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 팔·무기: 양손으로 도끼를 쥐되 대기와 달리 몸을 가로질러 뒤로 기울여(받들어총처럼) 들고, 도끼 머리는 머리 뒤 위쪽에 둔다 (아래 손 x=225–245, y=680–700 배 앞, 자루는 뒤쪽으로 50–60°). 자루·날은 얼굴·수염·땋은 머리를 지나지 않는다. 두 팔을 따로 흔들지 않는다. 앞머리 두 갈래는 가슴 앞에 남긴다.
- 디딘 발: 한 걸음 원본 252.694px(게임 45.5px) → 디딘 발은 칸마다 **정확히 63.2px**(±3, 게임 11.4px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표. (병과 전사 R5 는 디딘 발이 30px 앞에 그려져 한 번 고쳤다.)
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_frostjarl_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다 (`--pose art/requests/gait/run__captain_frostjarl/pose.json`).

## Prompt for Antigravity

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 비요른 as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_frostjarl_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_captain_frostjarl_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
Draw the character OVER the accepted light mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the moves look squashed.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__captain_frostjarl/guide_run_a.png, guide_run_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__captain_frostjarl/size_run_a.png, size_run_b.png = the same frames with guide lines and the planted-toe ticks, and on the left
    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_captain_frostjarl.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/captain_frostjarl/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__captain_frostjarl/pose.json (the scaled coordinates and stride), art/requests/guides/run_base/v2/run_base_preview.gif (motion reference only).
    Draw only over this folder's guide_run_a.png and guide_run_b.png.

CHARACTER (unchanged from the accepted sheet): Bjorn: blond frost jarl with two front braids, blond beard, slate-blue armoured tunic, snowflake pauldron, pale fur mantle and fur-trimmed boots. Copy the long-hafted bearded axe and its two-handed grip from the accepted idle.

THE MOVE (owner's three movement classes; light: the accepted run: lean forward, press down in flight, rise a little after the landing is caught, hip nearly level, slight float, no hopping. It is already in the mannequin - copy it, do not invent another):
  - Each frame: the legs, the torso lean and the arm swing of that mannequin frame. Joint for joint: hips, knees, ankles, feet,
    shoulders, elbows (hands: see ARMS - where the text moves a hand, that is intended, not a deviation).
    The mannequin's big round head is a placeholder: draw the character's own head on the mannequin's neck, at its own size
    (as in the sheet).
  - R1 contact (near foot lands a little ahead, knee bent) - R2 catch (the hips drop onto the foot: lowest hips, but the torso straightens, so the head top is the HIGHEST of the cycle - see Height) - R3 push-off (stance leg extends behind, heel up) - R4 FLIGHT (both feet clearly off the ground, legs scissored, body pressed forward and leaning the most). R5-R8 = the same with the far foot.
  - The hips stay nearly level: the top of the head stays within about 10 px of the same height in all 8 frames. NO hopping, no bouncing up and down.
  - Lean forward (hip to neck): R1/R5 24, R2/R6 19.4, R3/R7 29.1, R4/R8 31.4 deg.
  - Height: the mannequin's head top is at y=487/484/490/492 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 -3, R3 +3, R4 +5 px from R1 (+ = lower) - move your head top by the same amounts (bob 8 px).
  - Stride: one step = 252.694 source px = 45.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - PLANTED FOOT (the rule the class warrior's R5 needed a fix for): a foot on the floor never slides in the drawing. From its
    contact frame on, the SAME boot moves LEFT by exactly step/4 = 63.2 px per frame (the mannequin: 62-63 px;
    tolerance 3 px) - the engine moves the unit 11.4 game px per frame, so the boot stays still on the ground.
    Toe tip of the planted boot = its FRONT-MOST pixel (the toe; on a tapered boot it may sit a few px above y=870, as on the     mannequin) = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=282 -> R2 x=220 -> R3 x=158
      far foot: R5 x=287 -> R6 x=224 -> R7 x=161
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
    Draw the planted boot once, then copy it from frame to frame and only shift it (lift the heel in the push frame); measure
    YOUR toe tip against these numbers (the size_* images mark them with yellow ticks).

ARMS AND WEAPONS:
  - Keep both hands on the axe, about 70 px apart on the shaft as in the idle, but carry it sloped BACK across the body (port arms): the near right hand low in front of the belly at x=225–245, y=680–700 (at most 30 px fore-aft), the shaft rising up and BACK (toward the left) at 50–60 deg above horizontal over the near shoulder, and the far left hand about 70 px up the shaft at the chest (about x=180–210, y=620–645). The axe head rides above and behind the back of the head (all axe pixels between x=60 and x=351, top at or below y=445, butt about 40 px forward-down of the lower hand). The shaft and blade never cross the face, beard or braids; they may overlap only the back hair and the mantle. The idle's forward-up angle does not fit: at any angle it runs the shaft through the running head, which leans forward (intended, not a deviation). The mannequin's two separate arm swings and elbow positions do NOT apply to this character (intended, not a deviation): the shoulders follow the torso lean and the grip rides with the torso, no arm pump, no swing.
  - Both gold-bound braids stay over the FRONT of the chest (the far forearm passes under their tips) and bounce lightly. Keep the white fur mantle across the shoulders. The long wavy back hair streams back a little and settles one frame late, as do the side and rear tunic panels. The front centre flap hangs between the thighs and swings with the leading thigh; never let it trail back. Leave the trousers and boots free.
  - Face and beard: exactly as in the accepted idle.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon and shield shapes and sizes, and the SCALE of the accepted
sheet. The body must not be shrunk to fit - change a weapon's angle instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - head 101.078 px scale = the scale of the accepted sheet (0.18 source -> game: the idle is 68 game px tall); the figure about as tall as the idle stood up (the mannequin's head top is near y=484-492).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_frostjarl_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_frostjarl_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/captain/frostjarl --gait run --src art/inbox/gait/sheet_captain_frostjarl_run_a.png art/inbox/gait/sheet_captain_frostjarl_run_b.png --pose art/requests/gait/run__captain_frostjarl/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_captain_frostjarl_preview_x4.png and sheet_captain_frostjarl_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_frostjarl_run - 비요른 달리기
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, size_run_a/b, sheet_captain_frostjarl.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you drew, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPONS
              lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  ## 판정 — gait/sheet_captain_frostjarl_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the QA cross-check should look at; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
