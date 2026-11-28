# 이사벨 — 퇴역 참모 (전술가) 이동 (3D 마네킹) · `sheet/captain/tactician` → `gait/sheet_captain_tactician_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/captain/tactician --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `isabel`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/captain_tactician/concept.png` | 디자인 초안 — 디자인만 |
| `art/requests/phase3/captain_tactician/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_captain_tactician.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — charcoal military coat to the knee, trousers, boots, short cane. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_captain_tactician_run_a.png` (R1~R4) + `art/inbox/gait/sheet_captain_tactician_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_captain_tactician_run - 이사벨 — 퇴역 참모 (전술가) 이동」 + 「## 판정 — gait/sheet_captain_tactician_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 지팡이 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 — 두 손으로 쥐면 두 손 모두 (가이드: R1:82 R2:76 R3:83 R4:81 R5:70 R6:66 R7:81 R8:88).
- 보폭: 한 걸음 게임 48.5px = 경량 부류 보폭 45.48px × 다리 비율 1.066 — 맞춘 마네킹의 다리(허벅지+정강이+발목)가 부류 마네킹보다 +7% 길어, 같은 관절 각도·같은 무릎 굽힘으로 디디면 한 걸음이 그만큼 길다(다리 비율 규칙: 5% 넘게 다르면 보폭이 다리를 따른다; 그대로 부류 보폭을 쓰면 무릎이 펴지거나 발이 덜 나간다). 엔진(js/battle.js runCells)은 시트마다 그 시트의 runStride/4 씩 디딘 칸을 넘기므로 디딘 발은 미끄러지지 않는다. 유닛의 빠르기는 그대로(같은 거리에서 걸음 수만 조금 적다), 박자(80ms)는 부류 그대로.
- 디딘 발: 한 걸음 원본 293.12px(게임 48.5px) → 디딘 발은 칸마다 **정확히 73.3px**(±3, 게임 12.1px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_tactician_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__captain_tactician/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 지팡이 = 곧은 막대와 끝의 둥근 머리.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓는다. 각도는 대기 그대로이거나 대기 가까이(얼마나·프레임마다 어떻게·왜 바뀌는지는 아래 「각도」 줄) — 대기의 무기를 쥔 주먹을 축으로 프레임마다 표의 각도까지 한 덩어리로 돌려 그린다. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 최대 3도(이 마네킹에서 잰 값; 검사 한도 한 손 무기 3.5도), 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠). 표의 **둘째 주먹은 밑동→끝 직선 위**에 있다(1.5px 안으로 검사) — 자루를 두 주먹을 지나는 한 직선으로 긋고, 둘째 손에서 꺾지 않는다.
- **각도 바뀜(+152도, 약 15도 넘음)**: 대기 그림은 지팡이을(를) 약 -90도로 든다. 달리기에서는 화면에서 약 62도로, 팔과 함께 58~66도 사이에서 흔들리며 이웃 프레임 사이 최대 3도씩 바뀐다(표 그대로). 무기를 새로 그리지 않는다: 대기의 그 무기(길이·모양·곧은 자루 그대로)를 쥔 주먹을 축으로 한 덩어리로 돌린다 — 프레임마다 표의 각도로(매끈한 흔들림, 튀지 않게), 대기 각도 쪽으로 왔다 갔다 하지 않는다. 이 각도에서 잰 값: 무기를 포함한 그림 전체가 칸(x 32~351) 안쪽으로 14px 이상(검사는 8px 이상).
- 단계: R1 닿기 - R2 받기(엉덩이 가장 낮음) - R3 밀기(뒤꿈치 듦) - R4 공중(두 발 모두 뜸). R5~R8 은 먼 발로 같은 동작.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **허리띠**: 그리는 허리띠(코트·갑옷의 허리선)의 가운데는 마네킹 허리의 **갈색 띠** 가운데 — 노란 엉덩이 점이 아니다(점은 약 20px 아래, 골반 속). 프레임별 y: R1 657 / R2 660 / R3 655 / R4 654 / R5 657 / R6 660 / R7 655 / R8 654.
- **머리카락 꼭대기 → 허리띠 = 대기의 길이(207px)**: 몸통·머리를 눌러 줄이거나 늘이지 않는다. 이 가이드의 머리 꼭대기 → 허리띠 줄 간격은 196-204px(몸통이 기울어 선 자세보다 화면에서 조금 짧다) — 머리·가슴을 한 덩어리로 프레임마다 「Height」 줄과 허리띠 줄로 옮긴다.
- **주먹→끝 = 173-174px**: 쥔 주먹 가운데에서 무기 끝까지 모든 프레임에서 같다 — 끝 자리에 맞추려고 자루를 늘이거나 줄이지 않고, 주먹을 무기와 함께 옮긴다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 퇴역 참모의 꼿꼿한 달리기: 경량보다 5~6도 덜 기울고 어깨·견장을 반듯하게(골반 4.5·가슴 3), 뒤꿈치는 낮게 단정한 보폭. 지팡이는 지휘봉처럼 허리에서 앞-위로 들어 금손잡이가 눈높이에서 길을 가리킨다.

- 꼿꼿하고 침착한 장교의 달리기: 경량 마네킹보다 5~6도 덜 기울고 엉덩이는 1~2px 높다(3D 마네킹에 이미 들어 있다 — 따라 그린다). 어깨는 반듯하고 금 견장은 흔들리지 않는다(가슴 비틀림·골반 비틀림이 작다). 턱은 수평, 눈은 앞의 전장을 본다.
- 단정하고 군더더기 없는 보폭: 뒤로 차올리는 뒤꿈치가 단거리 주자보다 낮다(마네킹의 다리에 이미 들어 있다) — 빠르고 정확한 걸음, 허둥대지 않는다. 공중 프레임에서 뒤로 빠진 다리는 조금 덜 뻗는다.
- 검은 지팡이는 가까운 손에 원수의 지휘봉처럼 든다 — 승인된 시트의 공격 준비·타격 그림과 같은 쥐는 법: 주먹이 아래 끝(물미 쪽)을 쥐고 몸 앞 허리띠 높이에 있으며, 지팡이는 앞쪽 위로 비스듬히 서서 금손잡이가 눈높이쯤 얼굴 앞에서 길을 가리키듯 앞장선다. 아래팔과 함께 움직이고 몇 px 만 흔들린다: 휘두르지 않고, 바닥에 닿지 않고, 얼굴을 가로지르지 않는다.
- 먼 손은 대기 그림처럼 허리띠 앞의 쥔 주먹으로, 작고 절제된 박자로만 흔든다.
- 무릎까지 오는 숯색 코트 자락과 긴 물결 짙은 남보라 머리는 뒤로 날리며 몸보다 한 프레임 늦다: 공중 프레임(R4/R8)에서 가장 높이 뜨고, 받는 프레임(R2/R6)에서 가라앉는다. 챙 달린 장교모는 단단히 쓰고 윤곽을 바꾸지 않는다.

## 요약 (한국어)

이사벨 — 퇴역 참모 (전술가)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_captain_tactician_run_a.png`·`art/inbox/gait/sheet_captain_tactician_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 이사벨(퇴역 참모, 전술가): 금테·옆의 작은 금단추·금 백합 휘장이 달린 검은 챙 장교모(삼각모 아님), 어깨와 등으로 흘러내리는 긴 물결 짙은 남보라 머리, 침착하고 날카로운 얼굴, 금단추·금테 소매와 주머니 덮개·금술 견장·높은 깃의 크림색 크라바트가 있는 무릎 길이 숯색 군복 코트, 금 버클 가죽 허리띠, 짙은 바지, 금 버클 검은 장화, 둥근 금손잡이와 금 물미가 달린 가는 검은 지팡이 한 자루(끝에서 끝까지 약 200px — 길이를 지킨다). 개성 — 퇴역 참모의 꼿꼿한 달리기: 경량보다 5~6도 덜 기울고 어깨·견장을 반듯하게(골반 4.5·가슴 3), 뒤꿈치는 낮게 단정한 보폭. 지팡이는 지휘봉처럼 허리에서 앞-위로 들어 금손잡이가 눈높이에서 길을 가리킨다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 73.3px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 이사벨 — 퇴역 참모 (전술가) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_tactician_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_captain_tactician_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__captain_tactician/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__captain_tactician/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__captain_tactician/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__captain_tactician/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_captain_tactician.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/captain_tactician/concept.png = the design draft (design only - not proportions or rendering).
  - art/requests/phase3/captain_tactician/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__captain_tactician/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Isabel (이사벨), the retired staff officer (tactician), exactly as on the accepted sheet: a black PEAKED officer's cap with a gold band, a small gold button at the side and a gold fleur-de-lis badge (NOT a tricorne); long wavy dark-indigo hair over the shoulders and down the back; a calm, sharp face; a charcoal knee-length military coat with gold buttons, gold-trimmed cuffs and pocket flaps, gold fringed epaulettes and a cream cravat at the high collar; a dark leather belt with a gold buckle; dark trousers; black boots with gold buckles; ONE slim black cane with a round gold knob and a gold ferrule (about 200 px end to end - keep its length).

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    STAFF = a straight pole with a round knob at the end.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip).
    A straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it.
    Never shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S)
    and TIP for each frame (+-4 px). Its angle is the idle's or near it (the ANGLE line below says how much, how it
    changes from frame to frame and why): draw the idle's own weapon turned as one piece about the holding fist to the
    table's angle in each frame. The tip MAY be above the head and is NOT limited by the Height numbers - those are
    the top of the HEAD (hair / helmet / hat) only. Between neighbouring frames the weapon turns at most 3 deg
    (measured on this mannequin; the check allows 3.5 for a one-handed weapon) and its tip follows the smooth path of
    the table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the
    weapon rides with the chest (strip b = strip a). The table's 2ND FIST is ON the butt -> tip line (checked <= 1.5
    px): draw the shaft as one straight line through BOTH fists - never kink it at the second hand.
  - ANGLE CHANGE (+152 deg, more than ~15): the idle holds the staff at ~-90 deg; the run carries it at about 62 deg
    on screen, swaying 58-66 deg with the arm and changing at most 3 deg between neighbouring frames, as in the table.
    Do NOT redraw the weapon: take the idle's own weapon (same length, shape and straight shaft) and turn it as ONE
    piece about the holding fist to the table's angle, following the table frame by frame (a smooth sway, never a
    jump); it never swings back toward the idle angle and forth. Measured at this carry: the whole figure, weapon
    included, stays >= 14 px inside the slot band x 32..351 (the check needs >= 8).
  - WRIST RANGE (owner rule; EVERY hand on the weapon, a two-handed grip's second hand too): every held weapon's GRIP
    AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:82 R2:76 R3:83 R4:81 R5:70 R6:66 R7:81 R8:88 deg).
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
  - Lean forward (hip to neck): R1 17.8, R2 14.2, R3 22.4, R4 24.4, R5 17.1, R6 13.8, R7 22.4, R8 25 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=456/456/458/458 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 +0, R3 +2, R4 +2 px from R1 (+ = lower) - move your head top by the same amounts (bob 2 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - BELT per frame (y on the canvas = the centre of the mannequin's BROWN BAND at the waist - NOT the yellow hip dot,
    which sits ~20 px lower in the pelvis): R1 657 / R2 660 / R3 655 / R4 654 / R5 657 / R6 660 / R7 655 / R8 654.
    Paint the belt (and the waist line of a coat / armour) centred on these rows.
  - hair top -> belt = the idle's span (207 px); do not squash or stretch the body or head.
    In this guide the HEAD top -> BELT rows are 196-204 px apart (the leaning trunk is a little shorter on screen than
    standing): move the whole head-and-chest block as ONE piece to the Height and BELT rows of each frame.
  - Stride: one step = 293.12 source px = 48.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 48.5 game px = the light class stride 45.48 px x leg factor 1.066: this character's fitted legs are 7% longer than the class mannequin's, so the same joint angles and stance-knee bend give a longer step (legs more than 5% off -> the stride follows the legs). The engine advances each sheet by its OWN runStride/4 per planted cell, so the planted foot does not slide; the unit's ground speed is unchanged (a few fewer steps). The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 73.3 px per frame (the mannequin: 73.2-73.3 px; tolerance 3 px) - the engine moves the unit
    12.1 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=291 -> R2 x=218 -> R3 x=144
      far foot: R5 x=302 -> R6 x=228 -> R7 x=155
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      R1: feet x 97 .. 291 (hip column 192; near toe 291, far toe 63), far 115 px up
      R2: feet x 110 .. 218 (hip column 192; near toe 218, far toe 88), far 122 px up
      R3: feet x 88 .. 224 (hip column 192; near toe 144, far toe 224), far 51 px up
      R4: feet x 69 .. 331 (hip column 192; near toe 50, far toe 331), near 63 px up, far 28 px up
      R5: feet x 85 .. 302 (hip column 192; near toe 51, far toe 302), near 115 px up
      R6: feet x 99 .. 228 (hip column 192; near toe 76, far toe 228), near 122 px up
      R7: feet x 99 .. 212 (hip column 192; near toe 212, far toe 155), near 51 px up
      R8: feet x 82 .. 317 (hip column 192; near toe 317, far toe 63), near 28 px up, far 63 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      R1: butt (228,675) fist (236,663) tip (327,516)  angle 58 deg  butt->tip 188 px
      R2: butt (230,673) fist (237,660) tip (328,512)  angle 59 deg  butt->tip 188 px
      R3: butt (236,673) fist (243,660) tip (327,508)  angle 61 deg  butt->tip 188 px
      R4: butt (243,669) fist (249,656) tip (325,499)  angle 64 deg  butt->tip 189 px
      R5: butt (246,658) fist (252,645) tip (323,486)  angle 66 deg  butt->tip 189 px
      R6: butt (244,657) fist (250,644) tip (324,486)  angle 65 deg  butt->tip 189 px
      R7: butt (240,670) fist (247,657) tip (327,503)  angle 62 deg  butt->tip 189 px
      R8: butt (231,676) fist (239,664) tip (327,514)  angle 60 deg  butt->tip 188 px
    FIST -> TIP = 173-174 px in every frame (the holding fist's centre to the weapon's tip; the same piece every frame):
    keep that length - never lengthen the shaft to reach the tip row nor shorten it; move the fist WITH the weapon.

PERSONALITY (this character's own run):
  - An upright, composed officer's run: 5-6 deg LESS lean than the light class mannequin and the hips 1-2 px higher (the mannequin already has both - follow it). Shoulders square and the gold epaulettes steady (small chest counter-turn and pelvis twist); chin level, eyes on the field ahead.
  - A neat, economical stride: the trailing heel kicks up less than a sprinter's (already in the mannequin's swing legs) - quick, precise steps, never a scramble; in the flight frames the trailing leg stays a little closer.
  - The black cane is carried like a field marshal's baton in the NEAR hand, the way the accepted sheet's wind-up and strike hold it: the fist on its lower (ferrule) end at the belt in front of the body, the cane slanting forward-up so the GOLD KNOB leads ahead of her face at about eye height - as if pointing the way. It rides with the forearm and dips only a few px: it never swings, never touches the floor and never crosses the face.
  - The far hand is a closed fist at the belt (as in the idle) with a small, controlled pump.
  - The knee-length charcoal coat tails and the long wavy dark-indigo hair stream BACK and lag the body by one frame: they lift most in the flight frames (R4/R8) and settle in the catch frames (R2/R6). The peaked cap stays firmly on, its outline unchanged.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.
COLOURS: take every colour from the accepted sheet (same palette, ~40 colours); the design colours were skin #f5d6b8; hair #3a3f6b; outfit #3a3a4a; accent #f2c94c.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 73 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=456-458 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_tactician_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_tactician_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/captain/tactician --gait run --src art/inbox/gait/sheet_captain_tactician_run_a.png art/inbox/gait/sheet_captain_tactician_run_b.png --pose art/requests/gait/run__captain_tactician/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_captain_tactician_preview_x4.png and sheet_captain_tactician_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_tactician_run - 이사벨 — 퇴역 참모 (전술가) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_captain_tactician.png, concept.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_captain_tactician_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
