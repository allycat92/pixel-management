# 우르그 이동 · `sheet/captain/titan` → `gait/sheet_captain_titan_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/captain/titan` 로 만듦).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 중량(heavy)의 확정 마네킹(`art/requests/guides/heavy_base/v1/`) 8프레임 위에 캐릭터를 프레임마다 덧그린다.** 그린 그림은 찌그러뜨리지 않는다(엔진은 칸을 그대로 넘긴다).
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 101ms 박자로 넘긴다 (디딘 발이 붙어 있게: 칸마다 한 걸음의 1/4).

| 파일 | 내용 |
|---|---|
| `guide_heavy_a.png` / `guide_heavy_b.png` | **자세·자리 가이드** = 확정 중량 마네킹 띠 그대로(H1~H4 / H5~H8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, 뜨는 칸 없음 |
| `size_heavy_a.png` / `size_heavy_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 마네킹 H1/H5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `art/requests/phase3/captain_titan/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_captain_titan.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |
| `art/requests/guides/heavy_base/v1/` (`pose.json`, `heavy_base_preview.gif`, `heavy_base.aseprite`) | 마네킹 원본 — 숫자·움직임 확인용 |

- 부류: **중량** — giant-blooded man with an enormous build carrying a huge two-handed stone maul (head bigger than his own head); leather harness, fur collar. (tools/art/specs/gait_classes.json)
- 납품: art-inbox `art/inbox/gait/sheet_captain_titan_run_a.png` (H1~H4) + `art/inbox/gait/sheet_captain_titan_run_b.png` (H5~H8) + `art/inbox/NOTES.md` 절 「gait/sheet_captain_titan_run - 우르그 이동」 + 「## 판정 — gait/sheet_captain_titan_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 팔·무기: 중량: 거대한 몸과 돌망치. 대기·준비 x 투영은 겹치므로 분리한 실제 대기(약 413px·게임 69px) 기준. 자기 몸의 폭·길이로, 발끝·각도만 복사. 뒤손 x123–136/y688–702, 앞손 x207–223/y666–679, 돌 전체 x249–351·y≥585, 얼굴·모피·앞무릎 분리. 금빛 룬·앞 허리띠와 튜닉 유지.
- 디딘 발: 한 걸음 원본 142.5px(게임 23.6px) → 디딘 발은 칸마다 **정확히 35.6px**(±3, 게임 5.9px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표. (병과 전사 R5 는 디딘 발이 30px 앞에 그려져 한 번 고쳤다.)
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_titan_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다 (`--pose art/requests/guides/heavy_base/v1/pose.json`).

## Prompt for Antigravity

```
TASK: draw the HEAVY TRUDGE (fast, purposeful) CYCLE (8 frames, movement class HEAVY) of Urg as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_titan_run_a.png  = frames H1 H2 H3 H4
  art/inbox/gait/sheet_captain_titan_run_b.png  = frames H5 H6 H7 H8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
Draw the character OVER the accepted heavy mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the moves look squashed.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/heavy__captain_titan/guide_heavy_a.png, guide_heavy_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/heavy__captain_titan/size_heavy_a.png, size_heavy_b.png = the same frames with guide lines and the planted-toe ticks, and on the left
    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_captain_titan.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/captain_titan/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/guides/heavy_base/v1/pose.json (the numbers below come from it), art/requests/guides/heavy_base/v1/heavy_base_preview.gif (the motion at speed), art/requests/guides/heavy_base/v1/heavy_base.aseprite (the mannequin source -
    you may open it as an underlay and draw on your own layers, but the delivered PNGs contain ONLY your drawing).

CHARACTER (unchanged from the accepted sheet): Enormous giant-blooded Urg, bare muscular arms, brown swept hair and beard, white fur collar, leather and gold harness, rune medallion, split front tunic, fur boots and one two-handed stone maul with a gold spiral rune.

THE MOVE (owner's three movement classes; heavy: heavy armour / tower shield / very large weapon: cannot really run. Fastest natural gait for that body = a heavy, purposeful, FAST trudge (not a stroll): NO flight phase (one foot always on the ground), torso upright, short stride, the weight dropped onto each footfall, arms held close and high. It is already in the mannequin - copy it, do not invent another):
  - Take the heavy mannequin’s leg ANGLES, lean, small bob, planted toe x and ground line. Keep Urg’s own longer torso and
    wide shoulders. Do NOT place his head, shoulders, elbows, hips or knees on the mannequin’s joints; see FORMAT and ARMS.
  - H1 contact (BOTH feet on the floor: the near foot lands ahead, the far foot still behind, heel up) - H2 down (the weight drops onto the near foot: lowest frame, knees bent most) - H3 passing (the far foot swings low past the standing foot, only 5-13 px off the floor) - H4 push (the standing heel lifts, the body rises back). H5-H8 = the same with the far foot.
  - NO FLIGHT: one sole is on y=870 in EVERY frame (both in H1/H5). The torso is almost upright and the head stays level; the weight shows ONLY as the drop in the down frame, then it comes back up slowly (the push is never higher than the contact). Knees low, stride short - heavy, grounded footfalls at a quick cadence, not a stroll.
  - Lean forward (hip to neck): H1/H5 5, H2/H6 5.6, H3/H7 5, H4/H8 4.8 deg.
  - Height: the mannequin's head top is at y=440/447/442/441 in H1 H2 H3 H4 (the same in H5 H6 H7 H8): H1 +0, H2 +7, H3 +2, H4 +1 px from H1 (+ = lower) - move your head top by the same amounts (bob 7 px).
  - Stride: one step = 142.5 source px = 23.6 game px; 8 frames = two steps, 101 ms a frame in the game.
  - PLANTED FOOT (the rule the class warrior's R5 needed a fix for): a foot on the floor never slides in the drawing. From its
    contact frame on, the SAME boot moves LEFT by exactly step/4 = 35.6 px per frame (the mannequin: 35-36 px;
    tolerance 3 px) - the engine moves the unit 5.9 game px per frame, so the boot stays still on the ground.
    Toe tip of the planted boot = its FRONT-MOST pixel (the toe; on a tapered boot it may sit a few px above y=870, as on the     mannequin) = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: H1 x=275 -> H2 x=239 -> H3 x=204 -> H4 x=169  (-> H5 x=133 as the REAR foot, heel up, toe still on the floor)
      far foot: H5 x=280 -> H6 x=244 -> H7 x=209 -> H8 x=173  (-> H1 x=137 as the REAR foot, heel up, toe still on the floor)
    Draw the planted boot once, then copy it from frame to frame and only shift it (lift the heel in the push frame); measure
    YOUR toe tip against these numbers (the size_* images mark them with yellow ticks).

ARMS AND WEAPONS:
  - Lower the two-handed stone maul from its idle diagonal to a short, braced carry across the low torso (intentional). NEAR hand to the rear x=123–136, y=688–702; FAR hand forward x=207–223, y=666–679, on the same haft. Aim for the stone head center x≈298, y≈638–654: keep the full head within x=249–351 and entirely below y=585 (larger y), above the lead knee. Keep the whole handle above the floor and preserve the gold spiral side. The shaft may cross the low harness in front; the stone must not cover the head or fur collar.
  - Both arms are exempt from the mannequin arm swing (intended). Bend the elbows from Urg’s own wider shoulders, which are not interchangeable with the mannequin’s; keep the weight large, braced and close rather than swinging it.
  - White fur and gold shoulder medallion stay on the body; front belt and split tunic remain in front. Only the loose hair behind the shoulder and rear tips lag.
  - Face: keep cheek marks, short beard, hairline and earring visible. Do not replace the loose hair behind him with a hood.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon and shield shapes and sizes, and the SCALE of the accepted
sheet. The body must not be shrunk to fit - change a weapon's angle instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_heavy_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame); in H1/H5 both soles are on y=870; the lifted sole 3-13 px above it; nothing below y=870 (no weapon tip, no hem);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - head 110 px scale = the scale of the accepted sheet (0.1654 source -> game: the idle is 69 game px tall); Urg’s accepted idle is about 413 source px head to sole (about 69 game px at 0.1654 / cell 112). Keep its own wide shoulders and long trunk. As a starting landmark at contact: hair around y≈455–470, shoulders around y≈550–580 and hips about y≈690–720 before the prescribed body drop. No taller mannequin head, stretched limbs, or shrinking the maul..
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_titan_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_titan_run_b.png
  python3 tools/art/add_gait.py sheet/captain/titan --gait run --src art/inbox/gait/sheet_captain_titan_run_a.png art/inbox/gait/sheet_captain_titan_run_b.png --pose art/requests/guides/heavy_base/v1/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (NO --flight-slots: every pose must stand on y=870). The third must end without an error and write
<temp dir>/sheet_captain_titan_preview_x4.png and sheet_captain_titan_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_titan_run - 우르그 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_heavy_a/b, size_heavy_a/b, sheet_captain_titan.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you drew, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPONS
              lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  ## 판정 — gait/sheet_captain_titan_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the QA cross-check should look at; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
