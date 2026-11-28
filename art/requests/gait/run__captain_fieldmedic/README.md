# 마그다 — 종군 의무관 (야전 의무관) 이동 (3D 마네킹) · `sheet/captain/fieldmedic` → `gait/sheet_captain_fieldmedic_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/captain/fieldmedic --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `magda`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/captain_fieldmedic/concept.png` | 디자인 초안 — 디자인만 |
| `art/requests/phase3/captain_fieldmedic/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_captain_fieldmedic.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — long warm-beige field coat with the back tails at the calf, red front apron to the upper shin, dark trousers and boots; mace. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_captain_fieldmedic_run_a.png` (R1~R4) + `art/inbox/gait/sheet_captain_fieldmedic_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_captain_fieldmedic_run - 마그다 — 종군 의무관 (야전 의무관) 이동」 + 「## 판정 — gait/sheet_captain_fieldmedic_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 철퇴 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 (가이드: R1:102 R2:101 R3:102 R4:101 R5:100 R6:100 R7:102 R8:104).
- 보폭: 한 걸음 게임 45.5px = 경량 부류 보폭 그대로 — 맞춘 다리가 부류 마네킹과 5% 안(다리 비율 1.040)이라 다리 비율 규칙을 쓰지 않는다. 박자(80ms)도 부류 그대로.
- 디딘 발: 한 걸음 원본 275px(게임 45.5px) → 디딘 발은 칸마다 **정확히 68.8px**(±3, 게임 11.4px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_fieldmedic_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__captain_fieldmedic/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 철퇴 = 자루와 둥근 머리.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓고, 각도는 대기와 달라도 표의 값. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 3도(양손 무기 1.5도) 이하, 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠).
- **각도 바뀜**: 대기 그림은 철퇴을(를) 약 63도로 든다. 달리기에서는 표의 117도 — 117도로 그린다. 대기 각도를 그대로 두지 않는다(길이·모양은 대기 그대로).
- 단계: R1 닿기 - R2 받기(엉덩이 가장 낮음) - R3 밀기(뒤꿈치 듦) - R4 공중(두 발 모두 뜸). R5~R8 은 먼 발로 같은 동작.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 부상병에게 달려가는 의무관: 경량보다 3~4도 덜 기울고 고개를 들어 앞을 살핀다. 앞무릎은 높이, 뒤꿈치는 덜 차고, 긴 철퇴는 양손 「앞에 총」으로 가슴을 가로지른다(어깨가 거의 안 돎).

- 부상병에게 달려가는 의무관의 단호한 달리기: 경량 마네킹보다 3~4도 덜 기울고 엉덩이는 약 2px 높다 — 바렌처럼 낮게가 아니라 꼿꼿하게 달린다. 고개는 들고 수평, 눈은 앞쪽 전장을 살핀다(3D 마네킹에 이미 들어 있다 — 따라 그린다).
- 실용적으로 무릎을 끌어올리는 보폭: 착지 전에 앞 무릎이 조금 더 올라오고, 뒤로 차는 발뒤꿈치는 덜 접힌다 — 군더더기 없이.
- 긴 철퇴는 양손으로 '앞에 총' 자세처럼 든다: 가까운 손(완장 팔)의 주먹은 가슴 아래 앞에, 먼 손은 자루를 따라 약 90px 위 먼 어깨 근처. 자루는 가슴을 가로질러 위·뒤로, 가시 쇠공은 머리 위 뒤쪽에 얹힌다. 양손으로 쥐어 어깨는 거의 돌지 않고, 철퇴는 가슴에 고정된다(대기는 앞-위 약 63도, 달리기는 「앞에 총」 약 117도 — 117도로 그린다): 모든 프레임에서 같은 각도·제 길이, 몸을 따라 움직일 뿐 — 휘두르거나 길이가 변하지 않는다.
- 높게 묶은 포니테일과 따뜻한 베이지 코트 자락은 뒤로 날리며 한 프레임 늦다(공중 프레임 R4/R8 에서 가장 높이, 받는 프레임 R2/R6 에서 가라앉음). 짙은 붉은 앞치마는 무릎 사이에서 펄럭이고, 허리 주머니 둘은 한 프레임 늦게 튄다.

## 요약 (한국어)

마그다 — 종군 의무관 (야전 의무관)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_captain_fieldmedic_run_a.png`·`art/inbox/gait/sheet_captain_fieldmedic_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 마그다: 붉은 끈으로 높게 묶은 검은 긴 포니테일, 이마의 흰 붕대, 갈색 피부, 짙은 빨강 스카프, 뒷자락이 종아리까지 오는 따뜻한 베이지 긴 야전 코트(절대 흰색 아님)와 가까운 위팔의 무늬 없는 짙은 빨강 완장, 정강이 위까지 오는 짙은 빨강 앞치마(십자·무늬 없음), 가죽 주머니 둘이 달린 갈색 허리띠, 짙은 바지, 갈색 장화, 긴 자루 철퇴 한 자루(검은 쇠 자루, 원뿔 가시가 박힌 둥근 쇠공 머리), 엄격하고 단호한 얼굴. 치유 빛 없음. 개성 — 부상병에게 달려가는 의무관: 경량보다 3~4도 덜 기울고 고개를 들어 앞을 살핀다. 앞무릎은 높이, 뒤꿈치는 덜 차고, 긴 철퇴는 양손 「앞에 총」으로 가슴을 가로지른다(어깨가 거의 안 돎). 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 68.8px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 마그다 — 종군 의무관 (야전 의무관) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_fieldmedic_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_captain_fieldmedic_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__captain_fieldmedic/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__captain_fieldmedic/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__captain_fieldmedic/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__captain_fieldmedic/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_captain_fieldmedic.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/captain_fieldmedic/concept.png = the design draft (design only - not proportions or rendering).
  - art/requests/phase3/captain_fieldmedic/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__captain_fieldmedic/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Magda (마그다), the field-medic captain, exactly as on the accepted sheet: long black hair in a HIGH PONYTAIL with a red tie; a WHITE bandage around the forehead; tan skin; a dark-red scarf; a long WARM-BEIGE field coat (never white) with the back tails at the calf and a plain dark-red armband on the near upper arm (no symbol); a dark-red front apron to the upper shin (NO cross or symbol anywhere); a brown belt with two leather pouches; dark trousers; brown boots; ONE long-handled mace (dark iron haft, round iron ball head with conical spikes); stern, determined expression. No healing glow.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    MACE = haft and round head.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip). A
    straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it. Never
    shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S) and TIP
    for each frame (+-4 px); its angle is the table's even where it differs from the idle. The tip MAY be above the
    head and is NOT limited by the Height numbers - those are the top of the HEAD (hair / helmet / hat) only. Between
    neighbouring frames the weapon turns at most 3 deg (two-handed: 1.5) and its tip follows the smooth path of the
    table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the weapon
    rides with the chest (strip b = strip a).
  - ANGLE CHANGE: the idle drawing holds the mace at ~63 deg; the run carries it at 117 deg (the table) - draw 117, do NOT keep the idle angle (keep its length and shape).
  - WRIST RANGE (owner rule): every held weapon's GRIP AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:102 R2:101 R3:102 R4:101 R5:100 R6:100 R7:102 R8:104 deg).
  - The mannequin's round head is a placeholder: paint the character's own head, hair and headgear at the idle's size on
    its neck. The joints, limbs and torso are fitted to the idle - put the character's own body exactly on them.
  - PAINT OVER EVERY MANNEQUIN PIXEL. add_gait.py refuses a strip in which >= 25% of a frame still has the mannequin's
    colours, and a recoloured mannequin (silhouette IoU > 0.93 with this guide). Clothing, hair, cloth and the real
    weapon change the silhouette - that is the work.
  - FLOOR: the standing sole on y=870; nothing of the body below it. A weapon tip or cloth that would dip below the
    floor line (or below y=852 in a flight frame) is touched up while painting - lift it a little.
  - Samples of other characters are only baselines. Do not recolour another character's strip.

THE MOVE (movement class light: the accepted run: lean forward, press down in flight, rise a little after the landing is caught, hip nearly level, slight float, no hopping. - with this character's personality on top, already in the mannequin):
  - R1 contact - R2 catch (lowest hips) - R3 push-off (heel up) - R4 FLIGHT (both feet off the ground). R5-R8 = the same with the far foot.
  - Lean forward (hip to neck): R1 19.9, R2 16.2, R3 25.5, R4 27.3, R5 19, R6 15.7, R7 25.5, R8 28.1 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=451/450/455/456 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 -1, R3 +4, R4 +5 px from R1 (+ = lower) - move your head top by the same amounts (bob 6 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - Stride: one step = 275 source px = 45.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 45.5 game px = the light class stride: the fitted legs are within 5% of the class mannequin's (leg factor 1.040), so the class stride is kept. The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 68.8 px per frame (the mannequin: 68.7-68.8 px; tolerance 3 px) - the engine moves the unit
    11.4 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=284 -> R2 x=215 -> R3 x=146
      far foot: R5 x=296 -> R6 x=228 -> R7 x=159
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      R1: feet x 99 .. 284 (hip column 192; near toe 284, far toe 66), far 111 px up
      R2: feet x 119 .. 215 (hip column 192; near toe 215, far toe 98), far 126 px up
      R3: feet x 84 .. 239 (hip column 192; near toe 146, far toe 239), far 49 px up
      R4: feet x 62 .. 332 (hip column 192; near toe 44, far toe 332), near 66 px up, far 27 px up
      R5: feet x 85 .. 296 (hip column 192; near toe 52, far toe 296), near 111 px up
      R6: feet x 106 .. 228 (hip column 192; near toe 85, far toe 228), near 126 px up
      R7: feet x 97 .. 225 (hip column 192; near toe 225, far toe 159), near 49 px up
      R8: feet x 76 .. 316 (hip column 192; near toe 316, far toe 59), near 27 px up, far 66 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      R1: butt (283,679) fist (247,609) 2nd fist (206,530) tip (148,420)  angle 118 deg  butt->tip 293 px
      R2: butt (278,679) fist (241,609) 2nd fist (199,530) tip (141,421)  angle 118 deg  butt->tip 293 px
      R3: butt (290,682) fist (255,610) 2nd fist (214,530) tip (159,420)  angle 117 deg  butt->tip 293 px
      R4: butt (292,682) fist (257,611) 2nd fist (217,530) tip (162,419)  angle 116 deg  butt->tip 293 px
      R5: butt (282,680) fist (245,609) 2nd fist (204,530) tip (146,420)  angle 118 deg  butt->tip 293 px
      R6: butt (278,679) fist (240,609) 2nd fist (198,531) tip (140,421)  angle 118 deg  butt->tip 293 px
      R7: butt (290,682) fist (255,611) 2nd fist (215,531) tip (159,420)  angle 117 deg  butt->tip 293 px
      R8: butt (294,681) fist (258,610) 2nd fist (219,531) tip (164,419)  angle 116 deg  butt->tip 293 px

PERSONALITY (this character's own run):
  - A field medic's purposeful dash to the wounded: more UPRIGHT than the light class mannequin (3-4 deg less lean) with the hips ~2 px higher - she runs tall, not low like Baren. The head is up and level, eyes scanning the field ahead (the mannequin already has all of this - follow it).
  - Practical, knee-driving stride: the front knee comes up a little higher before the landing, and the heel kicks back LESS behind her (a short tuck) - efficient, nothing flashy.
  - The long mace is held at PORT ARMS with BOTH hands: the near (armband) fist in front of the lower chest, the far fist ~90 px up the haft near the far shoulder, the haft across the chest and the spiked ball riding above and behind her head. Her shoulders are locked by the two-handed grip (almost no counter-turn); the mace is LOCKED to the chest (the idle holds it forward-up at ~63 deg; the run carries it at port arms, ~117 - draw 117): the same angle and full length in every frame, it rides the body only - never swings, never pumps.
  - The high ponytail and the warm-beige coat tails stream back and lag one frame (highest in the flight frames R4/R8, settling in the catch frames R2/R6); the dark-red apron flaps between the knees; the two belt pouches bounce a frame late.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.
COLOURS: take every colour from the accepted sheet (same palette, ~40 colours); the design colours were skin #c68a5c; hair #2b1d14; outfit #e8e4d8; accent #9c3b2e.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 68 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=450-456 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_fieldmedic_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_fieldmedic_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/captain/fieldmedic --gait run --src art/inbox/gait/sheet_captain_fieldmedic_run_a.png art/inbox/gait/sheet_captain_fieldmedic_run_b.png --pose art/requests/gait/run__captain_fieldmedic/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_captain_fieldmedic_preview_x4.png and sheet_captain_fieldmedic_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_fieldmedic_run - 마그다 — 종군 의무관 (야전 의무관) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_captain_fieldmedic.png, concept.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_captain_fieldmedic_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
