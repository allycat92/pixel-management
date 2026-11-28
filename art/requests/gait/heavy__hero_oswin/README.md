# 오스윈 — 몰락한 기사단장 (몰락 기사단장) 이동 (3D 마네킹) · `sheet/hero/oswin` → `gait/sheet_hero_oswin_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/oswin --guides 3d` 로 만듦; 3D 마네킹 시범).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → Antigravity 가 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `oswin`)이 중량(heavy) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 101ms 박자로 넘긴다. 보폭·박자·디딘 발 규칙은 중량 부류 그대로다 (엔진의 runCells).

| 파일 | 내용 |
|---|---|
| `guide_heavy_a.png` / `guide_heavy_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 H1~H4 / H5~H8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870 |
| `guide_heavy_plain_a.png` / `guide_heavy_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_heavy_a.png` / `size_heavy_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 H1/H5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_heavy.gif` / `preview_heavy_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 101ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_oswin/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_oswin.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **중량** — old knight commander in weathered silver plate with greaves and sabatons, two-handed longsword, rear blue cape and front tabard. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_oswin_run_a.png` (H1~H4) + `art/inbox/gait/sheet_hero_oswin_run_b.png` (H5~H8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_oswin_run - 오스윈 — 몰락한 기사단장 (몰락 기사단장) 이동」 + 「## 판정 — gait/sheet_hero_oswin_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 칼 (가까운 손) — 아래팔에 대한 손목 각도 0~120도 안 (가이드: H1:91 H2:91 H3:88 H4:85 H5:84 H6:85 H7:87 H8:90).
- 디딘 발: 한 걸음 원본 142.5px(게임 23.6px) → 디딘 발은 칸마다 **정확히 35.6px**(±3, 게임 5.9px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_oswin_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/heavy__hero_oswin/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 **실제 크기·모양**으로 그 선을 따라 그린다 (가이드의 길이는 자리 표시).
- **손목 범위**: 무기 방향은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

- 중량 부류의 빠른 걸음 박자 그대로인 노기사단장의 행군: 몸통은 중량 마네킹보다 더 곧다(기울기 5도 대신 약 3도). 가슴을 펴고 턱을 들고 앞길을 똑바로 본다 — 서두르지 않고 앞장선다.
- 발을 디딜 때마다 무게를 싣는다: 내려앉는 프레임(H2/H6)에서 엉덩이가 부류보다 몇 px 더 깊게 가라앉았다가 천천히 올라온다. 판금 때문에 골반과 가슴이 거의 돌지 않아 몸 전체가 한 덩어리로 움직인다.
- 양손 장검은 대기 그림처럼 든다 — 두 주먹이 한 손잡이에(가까운 주먹은 허리띠 위, 먼 주먹은 십자 가드 바로 밑), 팔꿈치는 몸에 붙이고, 칼날은 앞으로 약 70도로 깃대처럼 세운다. 몸과 함께 움직이고 한 프레임 늦게 2도쯤만 흔들린다 — 베거나 휘두르지 않는다.
- 뒤쪽 파란 망토와 해진 앞자락(타바드)은 한 프레임 늦게 무겁게 흔들린다. 회색 머리와 수염은 발을 디딜 때마다 조금만 들린다.

## 요약 (한국어)

오스윈 — 몰락한 기사단장 (몰락 기사단장)의 중량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_oswin_run_a.png`·`art/inbox/gait/sheet_hero_oswin_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 오스윈(몰락한 기사단장): 뒤로 넘긴 헝클어진 회색 머리, 짙은 회색 눈썹과 짧은 회색 수염, 엄하고 주름진 얼굴. 녹슨 자국이 큼직하게 몇 군데 있는 낡은 은빛 판금 갑옷(놋쇠 리벳 원판이 달린 둥글고 큰 어깨갑, 흉갑, 마디 팔갑과 건틀릿, 허벅지 판, 둥근 무릎 덮개, 정강이갑과 철신), 가슴에 바랜 왕실 문장 = 파란 방패 모양 하나, 놋쇠 버클의 갈색 가죽 허리띠, 다리 사이 앞으로 늘어진 해진 긴 파란 타바드와 뒤쪽의 해진 파란 망토, 양손으로 쥔 유럽식 양손 장검 한 자루(녹 자국이 있는 곧고 긴 칼날, 놋쇠 십자 가드와 폼멜, 가죽 손잡이). 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 35.6px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for Antigravity

```
TASK: draw the HEAVY TRUDGE (fast, purposeful) CYCLE (8 frames, movement class HEAVY) of 오스윈 — 몰락한 기사단장 (몰락 기사단장) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_oswin_run_a.png  = frames H1 H2 H3 H4
  art/inbox/gait/sheet_hero_oswin_run_b.png  = frames H5 H6 H7 H8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/heavy__hero_oswin/guide_heavy_a.png, guide_heavy_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/heavy__hero_oswin/guide_heavy_plain_a.png, guide_heavy_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/heavy__hero_oswin/size_heavy_a.png, size_heavy_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/heavy__hero_oswin/preview_heavy.gif, preview_heavy_game_x4.gif = the motion at speed (101 ms a frame).
  - art/inbox/sheet_hero_oswin.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_oswin/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/heavy__hero_oswin/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Oswin (오스윈), the fallen knight commander, exactly as on the accepted sheet: an old man with wild swept-back grey hair, heavy grey brows and a short grey beard, stern weathered face; weathered silver plate armour (big rounded pauldrons with brass rivet discs, breastplate, articulated arms and gauntlets, plate thighs, round knee cops, greaves and sabatons) covered in a few large RUST patches; a faded royal crest = one simple blue shield shape on the chest; a brown leather belt with brass buckles; a long tattered BLUE tabard hanging in front between the legs and a tattered blue cape behind; ONE two-handed European longsword (long straight blade with rust spots, brass cross-guard and pommel, leather grip) held in both hands.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's OWN weapon at its idle size and shape along that line (the ghost only marks the line).
  - WRIST RANGE (owner rule): every held weapon points 0-120 deg UPWARD (thumb side) from the forearm line
    (elbow -> wrist); 0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the
    arm line (no dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (H1:91 H2:91 H3:88 H4:85 H5:84 H6:85 H7:87 H8:90 deg).
  - The mannequin's round head is a placeholder: paint the character's own head, hair and headgear at the idle's size on
    its neck. The joints, limbs and torso are fitted to the idle - put the character's own body exactly on them.
  - PAINT OVER EVERY MANNEQUIN PIXEL. add_gait.py refuses a strip in which >= 25% of a frame still has the mannequin's
    colours, and a recoloured mannequin (silhouette IoU > 0.93 with this guide). Clothing, hair, cloth and the real
    weapon change the silhouette - that is the work.
  - FLOOR: the standing sole on y=870; nothing of the body below it. A weapon tip or cloth that would dip below the
    floor line (or below y=852 in a flight frame) is touched up while painting - lift it a little.
  - Samples of other characters are only baselines. Do not recolour another character's strip.

THE MOVE (movement class heavy: heavy armour / tower shield / very large weapon: cannot really run. Fastest natural gait for that body = a heavy, purposeful, FAST trudge (not a stroll): NO flight phase (one foot always on the ground), torso upright, short stride, the weight dropped onto each footfall, arms held close and high. - with this character's personality on top, already in the mannequin):
  - H1 contact - H2 catch (lowest hips) - H3 push-off (heel up) - H4 push. H5-H8 = the same with the far foot.
  - Lean forward (hip to neck): H1 3, H2 3.5, H3 2.9, H4 2.7, H5 2.9, H6 3.5, H7 2.9, H8 2.7 deg.
  - Height: the mannequin's head top is at y=457/467/460/458 in H1 H2 H3 H4 (the same in H5 H6 H7 H8): H1 +0, H2 +10, H3 +3, H4 +1 px from H1 (+ = lower) - move your head top by the same amounts (bob 10 px).
  - Stride: one step = 142.5 source px = 23.6 game px; 8 frames = two steps, 101 ms a frame in the game.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 35.6 px per frame (the mannequin: 35.6-35.7 px; tolerance 3 px) - the engine moves the unit
    5.9 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: H1 x=269 -> H2 x=233 -> H3 x=198 -> H4 x=162  (-> H5 x=126 as the REAR foot, heel up, toe still on the floor)
      far foot: H5 x=281 -> H6 x=245 -> H7 x=210 -> H8 x=174  (-> H1 x=138 as the REAR foot, heel up, toe still on the floor)

PERSONALITY (this character's own run):
  - An old knight commander's march at the heavy trudge cadence: the trunk stays more UPRIGHT than the heavy class mannequin (about 3 deg of lean instead of 5), chest out, chin up, eyes level on the road ahead - he leads, he does not hurry.
  - Each footfall is SETTLED: the hips sink a few px deeper than the class in the down frames (H2/H6) and come back up slowly; the plate keeps the hips and the chest almost square (very little twist), so the whole body moves as one block.
  - The two-handed longsword is held as in the idle - BOTH fists on one hilt (near fist on the belt, far fist just under the cross-guard), elbows tucked, the blade upright forward at about 70 deg like a raised standard. It rides with the body and sways only a couple of degrees one frame late - no slash, no swing.
  - The rear blue cape and the tattered tabard swing heavily one frame late; the grey hair and beard lift only a little with each footfall.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit - change a weapon's angle (inside the wrist range) instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_heavy_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 71 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its head top near y=457-467.
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_oswin_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_oswin_run_b.png
  python3 tools/art/add_gait.py sheet/hero/oswin --gait run --src art/inbox/gait/sheet_hero_oswin_run_a.png art/inbox/gait/sheet_hero_oswin_run_b.png --pose art/requests/gait/heavy__hero_oswin/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS. The third must end without an error and write
<temp dir>/sheet_hero_oswin_preview_x4.png and sheet_hero_oswin_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_oswin_run - 오스윈 — 몰락한 기사단장 (몰락 기사단장) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_heavy_a/b, guide_heavy_plain_a/b, size_heavy_a/b, preview_heavy.gif, sheet_hero_oswin.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_oswin_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
