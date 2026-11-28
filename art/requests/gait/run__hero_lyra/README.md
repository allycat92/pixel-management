# 리라 — 가면 쓴 의적 (가면 의적) 이동 (3D 마네킹) · `sheet/hero/lyra` → `gait/sheet_hero_lyra_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/lyra --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `lyra`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_lyra/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_lyra.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — hooded masked outlaw: short shoulder capelet over a knee-length coat open below the belt, full trousers and boots, one dagger in idle. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_lyra_run_a.png` (R1~R4) + `art/inbox/gait/sheet_hero_lyra_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_lyra_run - 리라 — 가면 쓴 의적 (가면 의적) 이동」 + 「## 판정 — gait/sheet_hero_lyra_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 단검 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 (가이드: R1:29 R2:23 R3:33 R4:32 R5:19 R6:14 R7:32 R8:38).
- 보폭: 한 걸음 게임 49.1px = 경량 부류 보폭 45.48px × 다리 비율 1.079 — 맞춘 마네킹의 다리(허벅지+정강이+발목)가 부류 마네킹보다 +8% 길어, 같은 관절 각도·같은 무릎 굽힘으로 디디면 한 걸음이 그만큼 길다(다리 비율 규칙: 5% 넘게 다르면 보폭이 다리를 따른다; 그대로 부류 보폭을 쓰면 무릎이 펴지거나 발이 덜 나간다). 엔진(js/battle.js runCells)은 시트마다 그 시트의 runStride/4 씩 디딘 칸을 넘기므로 디딘 발은 미끄러지지 않는다. 유닛의 빠르기는 그대로(같은 거리에서 걸음 수만 조금 적다), 박자(80ms)는 부류 그대로.
- 디딘 발: 한 걸음 원본 296.76px(게임 49.1px) → 디딘 발은 칸마다 **정확히 74.2px**(±3, 게임 12.3px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_lyra_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__hero_lyra/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 단검 = 짧은 날과 작은 코등이.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓고, 각도는 대기와 달라도 표의 값. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 3도(양손 무기 1.5도) 이하, 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠).
- **각도 바뀜**: 대기 그림은 단검을(를) 약 -132도로 든다. 달리기에서는 표의 -107도 — -107도로 그린다. 대기 각도를 그대로 두지 않는다(길이·모양은 대기 그대로).
- 단계: R1 닿기 - R2 받기(엉덩이 가장 낮음) - R3 밀기(뒤꿈치 듦) - R4 공중(두 발 모두 뜸). R5~R8 은 먼 발로 같은 동작.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 가면 쓴 의적의 발끝 질주: 엉덩이를 높이 띄워 통통 튀고, 골반·가슴이 고양이처럼 크게 엇돈다(11/8). 단검 팔은 뒤로 곧게 끌고, 팔 흔들림은 반쯤 편 빈 손에만 있다.

- 발끝으로 가볍게 튀듯 달리는 의적의 질주: 경량 마네킹보다 엉덩이가 2~3px 높고(바렌은 낮게, 리라는 높고 탄력 있게) 기울기는 1~3도만 더한다. 착지 전 앞무릎이 조금 더 높이 올라온다(짧고 경쾌한 걸음 — 3D 마네킹에 이미 들어 있다, 따라 그린다). 엉덩이 흔들림이 부류보다 크다(골반 11도, 가슴 반대 회전 8도): 병사의 각진 달리기가 아니라 고양이처럼 유연한 흔들림.
- 단검 팔(가까운 팔)은 뒤로 끈다: 엉덩이 뒤로 거의 곧게 뻗어 아래로 내린 채, 단검은 대기 그림 그대로 — 칼날이 주먹 아래로 나와 팔 선을 이어 뒤아래로 — 언제든 앞으로 튕겨 낼 자세. 어깨와 함께 몇 px 만 움직이고, 흔들거나 휘두르지 않는다. R5/R6 에서 차올린 가까운 장화가 그 주먹 뒤를 지나간다: 팔과 단검이 장화 위에(가깝게) 그려진다.
- 빈 손(먼 손)은 대기 그림의 반쯤 편 경계 손으로 가슴 앞에서 흔든다 — 달리기의 팔 흔들림은 거의 이 손에 있다. 공중 프레임에서 뒤로 빠진 다리는 조금 덜 뻗는다(장화가 칸 안에 남게).
- 후드 아래 고개는 든다(목을 5도 되세움): 가면 쓴 얼굴은 앞을 보고 대기 그림의 장난스러운 반웃음 그대로. 긴 붉은 머리는 후드 밑에서 뒤로 날리며 한 프레임 늦다(R4/R8·R1/R5 에서 가장 뜬다). 후드 끝과 코트 뒷자락도 한 프레임 늦게 뒤로 튄다.

## 요약 (한국어)

리라 — 가면 쓴 의적 (가면 의적)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_lyra_run_a.png`·`art/inbox/gait/sheet_hero_lyra_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 리라: 눈을 가린 흰 반가면(벗지 않는다)과 장난스러운 반웃음, 크림색 테와 크림색 백합 문양이 있는 뾰족한 짙은 보라 후드(항상 쓴다), 후드 밑에서 허리까지 내려오는 긴 물결 짙은 붉은 머리와 가면 옆 한 가닥, 작은 금 고리 귀걸이, 둥근 금 브로치가 달린 짧은 보라 어깨망토와 크림색 크라바트, 크림색 테의 짙은 보라 코트(갈색 허리띠·네모난 금 버클까지 단추, 그 아래로 트여 무릎까지 오는 자락과 뒷자락 하나), 넉넉한 짙은 보라 바지, 크림색 단이 있는 갈색 장화, 가까운 손에 짧은 은빛 단검 한 자루(작은 금 코등이, 검은 손잡이) — 대기 그림 그대로 쥔다(칼날이 주먹 아래로 나와 팔 선을 잇는다). 개성 — 가면 쓴 의적의 발끝 질주: 엉덩이를 높이 띄워 통통 튀고, 골반·가슴이 고양이처럼 크게 엇돈다(11/8). 단검 팔은 뒤로 곧게 끌고, 팔 흔들림은 반쯤 편 빈 손에만 있다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 74.2px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 리라 — 가면 쓴 의적 (가면 의적) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_lyra_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_hero_lyra_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__hero_lyra/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__hero_lyra/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__hero_lyra/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__hero_lyra/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_hero_lyra.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_lyra/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__hero_lyra/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Lyra (리라), the masked outlaw, exactly as on the accepted sheet: a WHITE half-mask over the eyes (never off) and a mischievous half-smile; a pointed dark-violet HOOD with a cream trim and a cream fleur-de-lis, always up; long wavy dark-red hair falling from under the hood down her back to the belt, one lock beside the mask; small gold hoop earrings; a short violet shoulder capelet with a round gold brooch and a cream cravat; a dark-violet coat with cream trim buttoned to a brown belt with a square gold buckle and open below it, the knee-length skirt with one rear tail; full dark-violet trousers; brown boots with cream cuffs; ONE short silver dagger (small gold crossguard, dark grip) in the near hand, held exactly as in the idle (blade out of the bottom of the fist, continuing the arm line).

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    DAGGER = a short blade with a small guard.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip). A
    straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it. Never
    shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S) and TIP
    for each frame (+-4 px); its angle is the table's even where it differs from the idle. The tip MAY be above the
    head and is NOT limited by the Height numbers - those are the top of the HEAD (hair / helmet / hat) only. Between
    neighbouring frames the weapon turns at most 3 deg (two-handed: 1.5) and its tip follows the smooth path of the
    table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the weapon
    rides with the chest (strip b = strip a).
  - ANGLE CHANGE: the idle drawing holds the dagger at ~-132 deg; the run carries it at -107 deg (the table) - draw -107, do NOT keep the idle angle (keep its length and shape).
  - WRIST RANGE (owner rule): every held weapon's GRIP AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:29 R2:23 R3:33 R4:32 R5:19 R6:14 R7:32 R8:38 deg).
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
  - Lean forward (hip to neck): R1 24.9, R2 20.2, R3 31.2, R4 32.4, R5 22.8, R6 18.9, R7 31.2, R8 34.2 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=446/445/451/452 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 -1, R3 +5, R4 +6 px from R1 (+ = lower) - move your head top by the same amounts (bob 7 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - Stride: one step = 296.76 source px = 49.1 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 49.1 game px = the light class stride 45.48 px x leg factor 1.079: this character's fitted legs are 8% longer than the class mannequin's, so the same joint angles and stance-knee bend give a longer step (legs more than 5% off -> the stride follows the legs). The engine advances each sheet by its OWN runStride/4 per planted cell, so the planted foot does not slide; the unit's ground speed is unchanged (a few fewer steps). The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 74.2 px per frame (the mannequin: 74.1-74.3 px; tolerance 3 px) - the engine moves the unit
    12.3 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=292 -> R2 x=218 -> R3 x=143
      far foot: R5 x=304 -> R6 x=230 -> R7 x=155
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      R1: feet x 100 .. 292 (hip column 192; near toe 292, far toe 66), far 134 px up
      R2: feet x 115 .. 218 (hip column 192; near toe 218, far toe 93), far 133 px up
      R3: feet x 83 .. 242 (hip column 192; near toe 143, far toe 242), far 54 px up
      R4: feet x 65 .. 336 (hip column 192; near toe 46, far toe 336), near 62 px up, far 29 px up
      R5: feet x 87 .. 304 (hip column 192; near toe 53, far toe 304), near 134 px up
      R6: feet x 103 .. 230 (hip column 192; near toe 80, far toe 230), near 133 px up
      R7: feet x 95 .. 228 (hip column 192; near toe 228, far toe 155), near 54 px up
      R8: feet x 79 .. 321 (hip column 192; near toe 321, far toe 60), near 29 px up, far 62 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      R1: butt (87,641) fist (82,654) tip (52,734)  angle -110 deg  butt->tip 100 px
      R2: butt (89,657) fist (84,670) tip (55,751)  angle -110 deg  butt->tip 100 px
      R3: butt (94,639) fist (90,652) tip (64,733)  angle -108 deg  butt->tip 100 px
      R4: butt (102,646) fist (98,660) tip (75,742)  angle -106 deg  butt->tip 100 px
      R5: butt (110,672) fist (106,686) tip (85,769)  angle -105 deg  butt->tip 100 px
      R6: butt (110,679) fist (106,693) tip (84,776)  angle -105 deg  butt->tip 100 px
      R7: butt (97,643) fist (93,656) tip (68,738)  angle -107 deg  butt->tip 100 px
      R8: butt (92,622) fist (87,635) tip (59,716)  angle -109 deg  butt->tip 100 px

PERSONALITY (this character's own run):
  - A sly thief's sprint, light on the toes: the hips ride 2-3 px HIGHER than the light class mannequin (Baren runs low - Lyra runs tall and springy), only 1-3 deg more lean, and the front knee comes up a little higher before each landing (quick, prancing steps; the mannequin already has all of it - follow it). The hips swing more than the class (pelvis twist 11 deg, chest counter-turn 8 deg): a supple, cat-like sway, not a soldier's square run.
  - The dagger arm (near) TRAILS: it stays stretched back and down behind the hip, almost straight, the dagger held exactly as in the idle - the blade coming out of the bottom of the fist and continuing the arm line back-down, ready to flick forward. It only rides with the shoulder (a few px), never pumps and never slashes. In R5/R6 the kicked-up near boot passes behind that fist: the arm and the dagger are drawn OVER the boot (nearer).
  - The free (far) hand is the idle's half-open guard claw, pumping in front of the chest - nearly all the arm swing of the run is in this hand. In the flight frames the trailing leg stays a little closer (keeps the boot inside the frame).
  - Head up under the hood (neck turned back up 5 deg): the masked face looks ahead, the mischievous half-smile of the idle. The long red hair streams back from under the hood and lags one frame (lifts most in R4/R8 and R1/R5); the hood point and the coat's rear tail flick back one frame late.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 70 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=445-452 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_lyra_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_lyra_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/hero/lyra --gait run --src art/inbox/gait/sheet_hero_lyra_run_a.png art/inbox/gait/sheet_hero_lyra_run_b.png --pose art/requests/gait/run__hero_lyra/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_hero_lyra_preview_x4.png and sheet_hero_lyra_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_lyra_run - 리라 — 가면 쓴 의적 (가면 의적) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_hero_lyra.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_lyra_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
