# 서리 트롤 이동 · `sheet/monster/서리 트롤` → `gait/sheet_monster_frost-troll_run`

**상태: 요청 (2026-11-27, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/monster/서리 트롤` 로 만듦).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 중량(heavy)의 이 폴더의 조정된 가이드 8프레임 위에 캐릭터를 프레임마다 덧그린다.** 그린 그림은 찌그러뜨리지 않는다(엔진은 칸을 그대로 넘긴다).
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 101ms 박자로 넘긴다 (디딘 발이 붙어 있게: 칸마다 한 걸음의 1/4).

| 파일 | 내용 |
|---|---|
| `guide_heavy_a.png` / `guide_heavy_b.png` | **자세·자리 가이드** = 확정 중량 마네킹 띠를 시트 배율에 맞춰 조정(H1~H4 / H5~H8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, 뜨는 칸 없음 |
| `size_heavy_a.png` / `size_heavy_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 마네킹 H1/H5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `art/inbox/sheet_monster_frost-troll.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |
| `art/requests/gait/heavy__monster_frost-troll/pose.json`, `art/requests/guides/heavy_base/v1/heavy_base_preview.gif` | 이 요청의 좌표·보폭과 원본 움직임. 덧그리기는 이 폴더의 `guide_heavy_a.png` / `guide_heavy_b.png` 위에만 한다. |

- 부류: **중량** — big bare-handed frost troll, massive shoulders and fists (enemy_tpl brute -> heavy by body size, same as the other brutes); registered 2026-11-27 (Antigravity c4cc054). (tools/art/specs/gait_classes.json)
- 납품: art-inbox `art/inbox/gait/sheet_monster_frost-troll_run_a.png` (H1~H4) + `art/inbox/gait/sheet_monster_frost-troll_run_b.png` (H5~H8) + `art/inbox/NOTES.md` 절 「gait/sheet_monster_frost-troll_run - 서리 트롤 이동」 + 「## 판정 — gait/sheet_monster_frost-troll_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 팔·무기: 승인 2×2 왼쪽 위가 대기. 곤봉 없이 맨주먹, 주먹은 늑골 아래. 마네킹 어깨·팔꿈치(x≈156/232)는 그보다 훨씬 좁아 팔 자리로 쓰지 않는다(의도): 넓은 어깨, 몸통 밖으로 늘어진 긴 팔 — 가까운 주먹은 가까운 허벅지 옆(x≈35–110, y≈710–780), 먼 주먹은 먼 허벅지 옆(x≈277–330); 가이드에서는 작은 앞뒤 흔들림(10–20px)과 출렁임만. 칸 뒤 끝에 닿는 것은 가까운 팔(그림 왼쪽, 대기에서 이미 x≈26): 팔꿈치를 조금 더 굽혀 6–8px 이상 안으로, 모든 칸 x>=32. 먼 주먹은 x<=351. 어두운 허리천은 허리를 두른 띠 + 두 허벅지 위 짧은 너덜 + 가운데 긴 뾰족한 앞자락, 앞에. 맨발.
- 디딘 발: 한 걸음 원본 130.942px(게임 23.6px) → 디딘 발은 칸마다 **정확히 32.7px**(±3, 게임 5.9px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표. (병과 전사 R5 는 디딘 발이 30px 앞에 그려져 한 번 고쳤다.)
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_monster_frost-troll_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다 (`--pose art/requests/gait/heavy__monster_frost-troll/pose.json`).

## Prompt for Antigravity

```
TASK: draw the HEAVY TRUDGE (fast, purposeful) CYCLE (8 frames, movement class HEAVY) of 서리 트롤 as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_monster_frost-troll_run_a.png  = frames H1 H2 H3 H4
  art/inbox/gait/sheet_monster_frost-troll_run_b.png  = frames H5 H6 H7 H8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
Draw the character OVER the accepted heavy mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the moves look squashed.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/heavy__monster_frost-troll/guide_heavy_a.png, guide_heavy_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/heavy__monster_frost-troll/size_heavy_a.png, size_heavy_b.png = the same frames with guide lines and the planted-toe ticks, and on the left
    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_monster_frost-troll.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/gait/heavy__monster_frost-troll/pose.json (the scaled coordinates and stride), art/requests/guides/heavy_base/v1/heavy_base_preview.gif (motion reference only).
    Draw only over this folder's guide_heavy_a.png and guide_heavy_b.png.

CHARACTER (unchanged from the accepted sheet): Bare-handed pale-blue frost troll: bald head, heavy brow, protruding tusks, huge shoulders, low massive fists, ragged dark front loincloth and bare feet. No club or ice weapon in any accepted pose.

THE MOVE (owner's three movement classes; heavy: heavy armour / tower shield / very large weapon: cannot really run. Fastest natural gait for that body = a heavy, purposeful, FAST trudge (not a stroll): NO flight phase (one foot always on the ground), torso upright, short stride, the weight dropped onto each footfall, arms held close and high. It is already in the mannequin - copy it, do not invent another):
  - Each frame: the legs, the torso lean and the body bob of that mannequin frame. Joint for joint: hips, knees, ankles,
    feet. Shoulders, elbows and fists: see ARMS - the mannequin's shoulders are far narrower than his, so they do NOT give
    his arm positions (intended, not a deviation); take only its small fore-aft arm swing.
    The mannequin's big round head is a placeholder: draw the character's own head on the mannequin's neck, at its own size
    (as in the sheet).
  - H1 contact (BOTH feet on the floor: the near foot lands ahead, the far foot still behind, heel up) - H2 down (the weight drops onto the near foot: lowest frame, knees bent most) - H3 passing (the far foot swings low past the standing foot, only 4.5944-11.9456 px off the floor) - H4 push (the standing heel lifts, the body rises back). H5-H8 = the same with the far foot.
  - NO FLIGHT: one sole is on y=870 in EVERY frame (both in H1/H5). The torso is almost upright and the head stays level; the weight shows ONLY as the drop in the down frame, then it comes back up slowly (the push is never higher than the contact). Knees low, stride short - heavy, grounded footfalls at a quick cadence, not a stroll.
  - Lean forward (hip to neck): H1/H5 5, H2/H6 5.6, H3/H7 5, H4/H8 4.8 deg.
  - Height: the mannequin's head top is at y=475/481/477/476 in H1 H2 H3 H4 (the same in H5 H6 H7 H8): H1 +0, H2 +6, H3 +2, H4 +1 px from H1 (+ = lower) - move your head top by the same amounts (bob 6 px).
  - Stride: one step = 130.942 source px = 23.6 game px; 8 frames = two steps, 101 ms a frame in the game.
  - PLANTED FOOT (the rule the class warrior's R5 needed a fix for): a foot on the floor never slides in the drawing. From its
    contact frame on, the SAME boot moves LEFT by exactly step/4 = 32.7 px per frame (the mannequin: 32-33 px;
    tolerance 3 px) - the engine moves the unit 5.9 game px per frame, so the boot stays still on the ground.
    Toe tip of the planted boot = its FRONT-MOST pixel (the toe; on a tapered boot it may sit a few px above y=870, as on the     mannequin) = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: H1 x=268 -> H2 x=235 -> H3 x=203 -> H4 x=171  (-> H5 x=138 as the REAR foot, heel up, toe still on the floor)
      far foot: H5 x=273 -> H6 x=240 -> H7 x=208 -> H8 x=175  (-> H1 x=141 as the REAR foot, heel up, toe still on the floor)
    Draw the planted boot once, then copy it from frame to frame and only shift it (lift the heel in the push frame); measure
    YOUR toe tip against these numbers (the size_* images mark them with yellow ticks).

ARMS AND WEAPONS:
  - Use both bare fists, not a club. Keep the fists low, below the ribs, and clear of the brow, tusks and knee silhouettes.
  - The mannequin's shoulders and elbows (x≈156/232) are far narrower than his, so they do NOT give the troll's arm positions (intended, not a deviation). Keep the idle's wide shoulders and long arms hanging outside the torso: the near fist beside the near thigh (idle x≈35–110, y≈710–780) and the far fist beside the far thigh (idle x≈277–330). From the guide take only the small fore-aft swing (its hands move about 10–20 px per cycle) and the body bob, bending the elbows a little. The near fist never crosses in front of the loincloth and stays at x>=32 (see the near-arm line).
  - The NEAR arm (left in the picture, drawn over the body) is the one at the slot's rear edge. In the idle its elbow and forearm already reach x≈26 (y≈630–700), and the near fist reaches x≈33 (y≈710–770). Tuck that arm in by at least 6–8 px with a slightly more bent elbow, hanging a little closer to the torso, so its whole outline stays at x>=32 in every frame, including the frames where it swings back. Do not narrow the shoulders or shrink the fist. The far fist (idle right edge x≈330) has about 20 px of room and must stay at x<=351.
  - Do not narrow his shoulders or shrink the fists to fit. Adjust the forearm turn before changing the silhouette; keep the planted heavy foot and torso positions from the scaled guide.
  - The dark ragged loincloth wraps the whole waist: a band from hip to hip, with short ragged tatters over the tops of both thighs and a longer pointed front flap hanging between the thighs. It stays in front. Only its free ragged tips lag a little as the thighs move; keep both blue feet separate.
  - Face: keep the bald skull, projecting brow and both tusks unobstructed.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon and shield shapes and sizes, and the SCALE of the accepted
sheet. The body must not be shrunk to fit - change a weapon's angle instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_heavy_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame); in H1/H5 both soles are on y=870; the lifted sole 3-11.9456 px above it; nothing below y=870 (no weapon tip, no hem);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - head 101.078 px scale = the scale of the accepted sheet (0.18 source -> game: the idle is 75 game px tall); Keep the bare-footed troll about as tall as the upper-left idle of the accepted 2×2 sheet (~75 game pixels); retain its broad shoulders and oversized fists..
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_monster_frost-troll_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_monster_frost-troll_run_b.png
  python3 tools/art/add_gait.py 'sheet/monster/서리 트롤' --gait run --src art/inbox/gait/sheet_monster_frost-troll_run_a.png art/inbox/gait/sheet_monster_frost-troll_run_b.png --pose art/requests/gait/heavy__monster_frost-troll/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (NO --flight-slots: every pose must stand on y=870). The third must end without an error and write
<temp dir>/sheet_monster_frost-troll_preview_x4.png and sheet_monster_frost-troll_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_monster_frost-troll_run - 서리 트롤 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_heavy_a/b, size_heavy_a/b, sheet_monster_frost-troll.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you drew, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPONS
              lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  ## 판정 — gait/sheet_monster_frost-troll_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the QA cross-check should look at; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
