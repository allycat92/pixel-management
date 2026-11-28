# 진 — 뒷골목 해결사 (해결사) 이동 (3D 마네킹) · `sheet/captain/fixer` → `gait/sheet_captain_fixer_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/captain/fixer --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `fixer`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/captain_fixer/concept.png` | 디자인 초안 — 디자인만 |
| `art/requests/phase3/captain_fixer/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_captain_fixer.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — black leather jacket, trousers, boots, dagger; lean agile build. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_captain_fixer_run_a.png` (R1~R4) + `art/inbox/gait/sheet_captain_fixer_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_captain_fixer_run - 진 — 뒷골목 해결사 (해결사) 이동」 + 「## 판정 — gait/sheet_captain_fixer_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 단검 (가까운 손) — 역수(칼날이 새끼손가락 쪽) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 (가이드: R1:25 R2:25 R3:25 R4:25 R5:25 R6:25 R7:25 R8:25).
- 보폭: 한 걸음 게임 49.3px = 경량 부류 보폭 45.48px × 다리 비율 1.085 — 맞춘 마네킹의 다리(허벅지+정강이+발목)가 부류 마네킹보다 +8% 길어, 같은 관절 각도·같은 무릎 굽힘으로 디디면 한 걸음이 그만큼 길다(다리 비율 규칙: 5% 넘게 다르면 보폭이 다리를 따른다; 그대로 부류 보폭을 쓰면 무릎이 펴지거나 발이 덜 나간다). 엔진(js/battle.js runCells)은 시트마다 그 시트의 runStride/4 씩 디딘 칸을 넘기므로 디딘 발은 미끄러지지 않는다. 유닛의 빠르기는 그대로(같은 거리에서 걸음 수만 조금 적다), 박자(80ms)는 부류 그대로.
- 디딘 발: 한 걸음 원본 298.31px(게임 49.3px) → 디딘 발은 칸마다 **정확히 74.6px**(±3, 게임 12.3px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_fixer_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__captain_fixer/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 **실제 크기·모양**으로 그 자리를 따라 그린다 (가이드의 모양은 자리 표시).
  - 단검 = 짧은 날과 작은 코등이.
  - **역수(거꾸로 쥐기)**: 가까운 손의 단검은 칼날이 주먹의 **새끼손가락 쪽**(주먹 아래)으로 나온다 — 보통 쥐기에서 칼날만 180도 뒤집은 것이다. 손목 규칙은 칼날이 아니라 **손잡이 축**(주먹의 엄지 쪽 방향)에 잰다: 이 축이 아래팔 선에서 위로 0~120도 안(가이드: 25도)이고, 칼날은 그 반대쪽(아래팔 선에서 새끼손가락 쪽으로 155도 — 팔뚝을 따라 뒤로 눕는다). 손목을 비트는 것이 아니다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 뒷골목 해결사의 낮고 조용한 질주: 착지마다 상체를 접어(3~6도 더) 충격을 소리 없이 삼키고, 고개는 후드 속에, 발뒤꿈치는 낮게. 역수 단검은 팔뚝 밑에 눕혀 허리에서 짧게 흔들고, 빈 손은 턱 앞 가드.

- 낮고 조용하게 웅크린 뒷골목 달리기: 상체가 경량 마네킹보다 3~6도 더 숙여진다 — 발이 닿고 받는 프레임(R1~R2 / R5~R6)에서 가장 많이, 착지를 소리 없이 흡수하듯 몸을 접는다. 엉덩이는 2~4px 만 낮다(바렌처럼 깊게 앉지 않는다). 고개는 후드 속으로 살짝 숙여 턱을 당기고, 눈은 후드 아래에서 앞을 본다. 3D 마네킹에 이미 들어 있다 — 따라 그린다.
- 조용한 발: 뒤로 차올리는 발뒤꿈치가 경량 마네킹보다 낮다(지나오는 동안 무릎이 12~14도 덜 굽음, R1~R2 / R5~R6). 앞으로 나가는 발은 부드럽게 다음 걸음을 뻗는다 — 발이 낮게 미끄러지듯. 공중 프레임(R4/R8)에서 뒤로 빠진 다리는 조금 덜 뻗는다(짧고 단단한 보폭 — 장화가 칸 안쪽에 넉넉히 남는다). 엉덩이 비틀림은 작다(작고 단단하게, 거들먹거림 없음).
- 가까운 손의 단검: 모든 프레임에서 대기 그림 그대로 **역수(거꾸로 쥐기)** — 칼날이 주먹의 **새끼손가락 쪽(주먹 아래)**으로 나와 팔뚝 아래·바깥을 따라 뒤로 눕고, 칼자루 끝은 엄지 쪽에 있다. 그렇다고 손목을 꺾는 것이 아니다: 주먹 자체는 아래팔 위에 보통대로 있고(손잡이 축 = 엄지 쪽이 아래팔 선에서 위로 약 25도 — 주인의 0~120도 안), 칼날만 180도 뒤집혀 있다. 가까운 팔은 허리 높이에서 짧고 단단하게 흔든다: 주먹이 앞으로 올 때(R2~R5) 칼날은 주먹 뒤로 약간 아래를 향해 끌려오고, 팔이 뒤로 갈 때(R6~R8 / R1) 팔꿈치 너머 뒤로 약간 위를 향한다. 바로 쥐기로 바꾸지 않고, 보는 사람 쪽이나 몸 앞을 가로지르지 않는다. 1px 어두운 외곽선과 밝은 강철색을 지켜 어두운 재킷에 묻히지 않게.
- 먼 손: 대기 그림의 빈 가드 손 — 손가락 없는 장갑을 낀 주먹을 가슴 앞 턱 가까이 들고, 팔꿈치를 굽힌 채 조금만(부류 흔들기의 1/3 정도) 흔든다.
- 천: 후드와 회색 스카프는 머리에 붙어 있다(펄럭이지 않음). 허리의 짧은 재킷 자락과 느슨한 스카프 끝만 뒤로 날리며 몸보다 한 프레임 늦다(공중 프레임 R4 / R8 에서 가장 뜨고, 받는 프레임 R2 / R6 에서 가라앉음).

## 요약 (한국어)

진 — 뒷골목 해결사 (해결사)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_captain_fixer_run_a.png`·`art/inbox/gait/sheet_captain_fixer_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 진: 밝은 베이지회색 테두리의 짙은 숯색·청회색 후드, 그 밖으로 이마에 흘러내린 헝클어진 짙은 갈색 머리, 가는 눈, 입과 코를 가리고 목에 감은 회색 스카프, 밝은 테두리와 작은 별 무늬의 짧은 어깨 케이프, 밝은 테두리의 몸에 붙는 숯색 가죽 재킷, 가슴의 네모 고리 달린 갈색 가죽 교차 띠와 네모 버클 갈색 허리띠, 엉덩이에서 짧게 갈라진 재킷 자락, 장화에 넣은 헐렁한 짙은 바지, 짙은 장화, 손가락 없는 짙은 장갑, 가까운 손에 역수로 쥔 짧은 단검 한 자루(밝은 강철 날, 작은 코등이, 짙은 손잡이), 마르고 날랜 체격. 옷은 검정이 아니라 짙은 숯색·청회색이고 시트처럼 왼쪽 위 가장자리에 차가운 림 라이트. 개성 — 뒷골목 해결사의 낮고 조용한 질주: 착지마다 상체를 접어(3~6도 더) 충격을 소리 없이 삼키고, 고개는 후드 속에, 발뒤꿈치는 낮게. 역수 단검은 팔뚝 밑에 눕혀 허리에서 짧게 흔들고, 빈 손은 턱 앞 가드. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 74.6px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 진 — 뒷골목 해결사 (해결사) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_fixer_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_captain_fixer_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__captain_fixer/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__captain_fixer/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__captain_fixer/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__captain_fixer/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_captain_fixer.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/captain_fixer/concept.png = the design draft (design only - not proportions or rendering).
  - art/requests/phase3/captain_fixer/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__captain_fixer/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Jin (진), the back-alley fixer captain, exactly as on the accepted sheet: a dark charcoal / slate HOOD with a light beige-grey trimmed edge, messy dark-brown hair falling out of it over the forehead, narrow eyes; a grey SCARF wrapped over the mouth and nose and around the neck; a short shoulder capelet with light trim and small star marks; a fitted charcoal leather jacket with light trim, a brown leather cross strap with a square ring on the chest and a brown leather belt with a square buckle; the jacket splits into short tails at the hips; baggy dark trousers tucked into dark boots; dark fingerless gloves; ONE short dagger (light-steel blade, small guard, dark grip) in the near hand in REVERSE grip; lean, agile build. The outfit is dark charcoal / blue-grey, NOT black, with the cool rim light on the upper-left edges as on the sheet.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's OWN weapon at its idle size and shape in that place (the ghost only marks it):
    DAGGER = a short blade with a small guard.
    REVERSE GRIP (near hand dagger): the blade comes out of the LITTLE-FINGER side of the fist (under the fist) - a normal grip with only the blade flipped 180 deg, the pommel on the thumb side. The wrist rule is measured on the GRIP AXIS (the thumb side of the fist), not on the blade: that axis stays 0-120 deg up from the forearm line (guide: 25 deg) and the blade points the opposite way (155 deg from the forearm line on the little-finger side - lying back along the forearm). The wrist is not twisted for it.
  - WRIST RANGE (owner rule): every held weapon's GRIP AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:25 R2:25 R3:25 R4:25 R5:25 R6:25 R7:25 R8:25 deg).
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
  - Lean forward (hip to neck): R1 29.5, R2 24.9, R3 31.2, R4 33.2, R5 28.7, R6 24.4, R7 31.2, R8 33.7 deg.
  - Height: the mannequin's head top is at y=468/466/468/468 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 -2, R3 +0, R4 +0 px from R1 (+ = lower) - move your head top by the same amounts (bob 2 px).
  - Stride: one step = 298.31 source px = 49.3 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 49.3 game px = the light class stride 45.48 px x leg factor 1.085: this character's fitted legs are 8% longer than the class mannequin's, so the same joint angles and stance-knee bend give a longer step (legs more than 5% off -> the stride follows the legs). The engine advances each sheet by its OWN runStride/4 per planted cell, so the planted foot does not slide; the unit's ground speed is unchanged (a few fewer steps). The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 74.6 px per frame (the mannequin: 74.5-74.6 px; tolerance 3 px) - the engine moves the unit
    12.3 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=292 -> R2 x=217 -> R3 x=143
      far foot: R5 x=305 -> R6 x=230 -> R7 x=156
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)

PERSONALITY (this character's own run):
  - A low, quiet, hunched back-alley sprint: the shoulders lean 3-6 deg more than the light class mannequin - most when the foot lands and catches (R1-R2 / R5-R6), folding over the landing to absorb it without a sound - while the hips sit only 2-4 px lower (not Baren's deep crouch). The head is ducked a little into the hood (chin down, eyes up from under the hood edge). The mannequin already has all of it - follow it.
  - Quiet feet: the recovering heel is tucked less high than the class mannequin (knee 12-14 deg less bent while it comes through, R1-R2 / R5-R6) and the swing foot reaches softly into the next step - the feet skim low. In the flight frames (R4/R8) the trailing leg stays a little closer under him (a short, compact stride that keeps the boot well inside the frame). The hips twist less (compact, no swagger).
  - Dagger in the near hand: REVERSE GRIP in EVERY frame, exactly as in the idle - the blade comes out of the LITTLE-FINGER side of the fist (under the fist) and lies back along the underside / outside of the forearm, the pommel on the thumb side. The wrist is not bent for it: the fist itself sits normally on the forearm (its grip axis about 25 deg up from the forearm line, inside the owner's 0-120 range); only the blade is flipped 180 deg. The near arm pumps short and tight at belt height: when the fist comes forward (R2-R5) the blade trails back and a little down behind it, when the arm swings back (R6-R8 / R1) it points back and a little up past the elbow. Never a forward grip, never pointing at the viewer or across the body; keep its 1 px dark outline and the light steel so it never merges into the dark jacket.
  - Far hand: the idle's empty guard hand - fingerless-gloved fist held up in front of the chest near the chin, elbow bent, pumping only a little (about a third of the class swing).
  - Cloth: hood and grey scarf stay snug on the head (no flapping); the short jacket tails at the hips and the loose scarf end flick back and lag the body by ONE frame (lift most in the flight frames R4 / R8, settle in the catch frames R2 / R6).
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit - change a weapon's angle (inside the wrist range) instead.
COLOURS: take every colour from the accepted sheet (same palette, ~40 colours); the design colours were skin #e0ac7e; hair #2b1d14; outfit #2a2a2a; accent #c9c2b8.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 68 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its head top near y=466-468.
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_fixer_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_fixer_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/captain/fixer --gait run --src art/inbox/gait/sheet_captain_fixer_run_a.png art/inbox/gait/sheet_captain_fixer_run_b.png --pose art/requests/gait/run__captain_fixer/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_captain_fixer_preview_x4.png and sheet_captain_fixer_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_fixer_run - 진 — 뒷골목 해결사 (해결사) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_captain_fixer.png, concept.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_captain_fixer_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
