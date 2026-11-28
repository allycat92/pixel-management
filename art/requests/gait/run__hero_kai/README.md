# 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) 이동 (3D 마네킹) · `sheet/hero/kai` → `gait/sheet_hero_kai_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/kai --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `kai`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_kai/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_kai.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — elf scout: green shoulder cloak and split tunic over trousers and boots, with a bow and quiver. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_kai_run_a.png` (R1~R4) + `art/inbox/gait/sheet_hero_kai_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_kai_run - 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) 이동」 + 「## 판정 — gait/sheet_hero_kai_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 활 (먼 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 — 두 손으로 쥐면 두 손 모두 (가이드: R1:96 R2:91 R3:104 R4:109 R5:102 R6:96 R7:104 R8:105).
- 보폭: 한 걸음 게임 45.5px = 경량 부류 보폭 그대로 — 맞춘 다리가 부류 마네킹과 5% 안(다리 비율 0.977)이라 다리 비율 규칙을 쓰지 않는다. 박자(80ms)도 부류 그대로.
- 디딘 발: 한 걸음 원본 275px(게임 45.5px) → 디딘 발은 칸마다 **정확히 68.8px**(±3, 게임 11.4px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_kai_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__hero_kai/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 활 = 휜 활대 둘(손잡이에서 위·아래 활끝으로, 끝으로 갈수록 시위 쪽으로 휜다)과 활끝을 잇는 가는 시위 선. 한 손으로 손잡이를 쥔다. 손목 규칙은 손잡이에서 위 활끝 쪽으로 가는 활대 방향(손잡이 축)에 잰다.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓는다. 각도는 대기 그대로이거나 대기 가까이(얼마나·프레임마다 어떻게·왜 바뀌는지는 아래 「각도」 줄) — 대기의 무기를 쥔 주먹을 축으로 프레임마다 표의 각도까지 한 덩어리로 돌려 그린다. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 최대 2.2도(이 마네킹에서 잰 값; 검사 한도 한 손 무기 3.5도), 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠). 표의 **둘째 주먹은 밑동→끝 직선 위**에 있다(1.5px 안으로 검사) — 자루를 두 주먹을 지나는 한 직선으로 긋고, 둘째 손에서 꺾지 않는다.
- **각도**: 달리기는 활을(를) 화면에서 약 65도로, 팔과 함께 62~68도 사이에서 흔들리며 이웃 프레임 사이 최대 2.2도씩 바뀐다(표 그대로) — 대기 약 73도에서 -8도(약 15도 안). 대기의 무기를 그대로(길이·모양·곧은 자루) 쥔 주먹을 축으로 그만큼만 한 덩어리로 돌린다 — 프레임마다 표의 각도로(매끈한 흔들림, 튀지 않게). 이 각도에서 잰 값: 무기를 포함한 그림 전체가 칸(x 32~351) 안쪽으로 13px 이상(검사는 8px 이상).
- 단계: R1 닿기 - R2 받기(엉덩이 가장 낮음) - R3 밀기(뒤꿈치 듦) - R4 공중(두 발 모두 뜸). R5~R8 은 먼 발로 같은 동작.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **허리띠**: 그리는 허리띠(코트·갑옷의 허리선)의 가운데는 마네킹 허리의 **갈색 띠** 가운데 — 노란 엉덩이 점이 아니다(점은 약 20px 아래, 골반 속). 프레임별 y: R1 675 / R2 675 / R3 675 / R4 675 / R5 675 / R6 675 / R7 675 / R8 675.
- **머리카락 꼭대기 → 허리띠 = 대기의 길이(210px)**: 몸통·머리를 눌러 줄이거나 늘이지 않는다. 이 가이드의 머리 꼭대기 → 허리띠 줄 간격은 189-201px(몸통이 기울어 선 자세보다 화면에서 조금 짧다) — 머리·가슴을 한 덩어리로 프레임마다 「Height」 줄과 허리띠 줄로 옮긴다.
- **주먹→끝 = 127-128px**: 쥔 주먹 가운데에서 무기 끝까지 모든 프레임에서 같다 — 끝 자리에 맞추려고 자루를 늘이거나 줄이지 않고, 주먹을 무기와 함께 옮긴다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 숲을 떠난 엘프 정찰병의 미끄러지는 활보: 키아라와 반대로 머리·엉덩이가 거의 오르내리지 않고(출렁임 1px 미만) 고개는 수평에 못 박혀 앞을 살피며(목 7도 되세움), 골반·어깨가 작게(5/3) 돈다. 무릎은 낮게, 앞발은 길게 뻗고, 활은 팔을 길게 내려 앞으로 기울여 든다.

- 엘프 정찰병의 미끄러지는 활보 — 키아라의 통통 튀는 숲 달리기와 반대: 엉덩이가 한 바퀴 내내 **수평**이다(마네킹의 엉덩이 높이가 1px 도 안 변한다 — 오르내림 없음). 기울기는 경량 마네킹보다 1~2도 더하고, 머리는 수평에 고정해 눈은 지평선을 본다(기운 만큼 목을 7도 되세움 — '매의 눈'). 3D 마네킹에 이미 들어 있다 — 따라 그린다.
- 조용하고 아끼는 엉덩이·어깨: 골반 비틀림 작게(5도, 부류 7), 가슴 반대 회전 작게(3, 부류 6) — 몸통이 거의 돌지 않는다. 길고 **낮게** 뻗는 보폭: 지나가는 프레임에서 무릎을 낮게 끌고, 뒤로 빠진 뒤꿈치도 낮게(차올리지 않음), 착지 전 앞발을 길게 뻗는다 — 땅을 먹어 들어가는 미끄러짐, 전력 질주가 아니다.
- 활은 **준비 자세로 낮게, 앞으로 기울여** 먼 손(왼손)에 대기 그림의 손잡이 그대로 든다: 먼 팔은 거의 힘을 뺀 채 앞아래로 뻗고(팔꿈치 약 70도), 활대는 앞으로 약 64도 기운다 — 위 활끝은 가슴 앞, 아래 활끝은 무릎 뒤, 시위는 몸 쪽, 화살은 걸지 않는다. 팔과 함께 몇 px 만 흔들린다. 가이드의 청록 반투명 활(휜 활대, 가는 시위)이 자리를 보여 준다: 은빛 리커브 활대, 감은 손잡이, 가는 시위를 대기 그림 크기로 그린다(손잡이에서 위 끝 약 125px, 아래 끝 약 128px).
- 가까운 손(오른손)은 비어 있고 조용하다: 느슨하게 반쯤 편 손이 **작게**(부류 흔들기의 절반 아래, 한 프레임 늦게) 흔들린다 — 팔을 펌프질하지 않는다.
- 화살통은 등에 고정(흰 깃이 먼 어깨 위로). 녹색 리본 아래의 긴 금발, 녹색 어깨 망토의 뒷자락, 무릎까지 오는 튜닉 뒷자락은 한 프레임 늦게 고르게 뒤로 흐른다 — 몸이 오르내리지 않으니 튀지 않고 매끈한 선으로 끌린다.

## 요약 (한국어)

카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_kai_run_a.png`·`art/inbox/gait/sheet_hero_kai_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 카이(숲을 떠난 엘프 정찰병): 뾰족한 엘프 귀, 뒤통수 귀 높이에서 짙은 녹색 리본으로 묶은 긴 물결 금발(풀린 머리는 등 뒤로 허리띠쯤까지, 볼 옆에 짧은 앞머리 몇 가닥), 녹색 눈과 차분하고 단호한 얼굴, 크림색 테두리와 둥근 잎 브로치가 달린 팔꿈치 길이의 짙은 녹색 어깨 망토, 금색 잎 자수와 크림색 단의 짙은 녹색 트임 튜닉(다리 사이 크림 테두리 앞자락, 무릎까지 오는 뒷자락), 갈색 가죽 팔보호대·허리띠·네모 버클 가슴끈, 갈색 바지, 접힌 단의 갈색 장화, 은회색 짧은 리커브 활 한 자루(검게 감은 손잡이, 금색 띠, 가는 흰 시위), 흰 깃 화살이 든 갈색 화살통(등). 개성 — 숲을 떠난 엘프 정찰병의 미끄러지는 활보: 키아라와 반대로 머리·엉덩이가 거의 오르내리지 않고(출렁임 1px 미만) 고개는 수평에 못 박혀 앞을 살피며(목 7도 되세움), 골반·어깨가 작게(5/3) 돈다. 무릎은 낮게, 앞발은 길게 뻗고, 활은 팔을 길게 내려 앞으로 기울여 든다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 68.8px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_kai_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_hero_kai_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__hero_kai/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__hero_kai/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__hero_kai/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__hero_kai/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_hero_kai.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_kai/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__hero_kai/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Kai (카이), the young elf scout who left the forest (silver ranger), exactly as on the accepted sheet: pointed elf ears; long wavy BLOND hair tied with a dark-green ribbon at the back of the head at ear height, the loose waves hanging down the back to about the belt, short locks beside the cheeks; green eyes, calm stern face; an elbow-length dark-green shoulder cloak with cream trim and a round leaf brooch at the collar; a dark-green split tunic (gold leaf embroidery, cream hem) with a cream-trimmed front tab between the legs and a knee-length rear flap; brown leather bracers, belt and cross strap with a square buckle; brown trousers; brown boots with turned cuffs; ONE silver-grey short recurve bow (dark wrapped grip, gold bands, thin off-white string); a brown quiver of white-fletched arrows on the back.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    BOW = two curved limbs (from the grip to each tip, curling back toward the string near the tips) and a thin string line tip to tip; ONE hand on the grip. The wrist rule is measured on the stave at the grip, toward the upper tip.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip).
    A straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it.
    Never shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S)
    and TIP for each frame (+-4 px). Its angle is the idle's or near it (the ANGLE line below says how much, how it
    changes from frame to frame and why): draw the idle's own weapon turned as one piece about the holding fist to the
    table's angle in each frame. The tip MAY be above the head and is NOT limited by the Height numbers - those are
    the top of the HEAD (hair / helmet / hat) only. Between neighbouring frames the weapon turns at most 2.2 deg
    (measured on this mannequin; the check allows 3.5 for a one-handed weapon) and its tip follows the smooth path of
    the table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the
    weapon rides with the chest (strip b = strip a). The table's 2ND FIST is ON the butt -> tip line (checked <= 1.5
    px): draw the shaft as one straight line through BOTH fists - never kink it at the second hand.
  - ANGLE: the run carries the bow at about 65 deg on screen, swaying 62-68 deg with the arm and changing at most 2.2
    deg between neighbouring frames, as in the table - -8 deg from the idle's ~73 (within ~15). Keep the idle's weapon
    as drawn (same length, shape, straight shaft), turned as one piece about the holding fist by that little -
    following the table frame by frame (a smooth sway, never a jump). Measured at this carry: the whole figure, weapon
    included, stays >= 13 px inside the slot band x 32..351 (the check needs >= 8).
  - WRIST RANGE (owner rule; EVERY hand on the weapon, a two-handed grip's second hand too): every held weapon's GRIP
    AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:96 R2:91 R3:104 R4:109 R5:102 R6:96 R7:104 R8:105 deg).
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
  - Lean forward (hip to neck): R1 25.9, R2 21.2, R3 29.5, R4 31.3, R5 24.8, R6 20.6, R7 29.5, R8 32.2 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=478/474/483/486 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 -4, R3 +5, R4 +8 px from R1 (+ = lower) - move your head top by the same amounts (bob 12 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - BELT per frame (y on the canvas = the centre of the mannequin's BROWN BAND at the waist - NOT the yellow hip dot,
    which sits ~20 px lower in the pelvis): R1 675 / R2 675 / R3 675 / R4 675 / R5 675 / R6 675 / R7 675 / R8 675.
    Paint the belt (and the waist line of a coat / armour) centred on these rows.
  - hair top -> belt = the idle's span (210 px); do not squash or stretch the body or head.
    In this guide the HEAD top -> BELT rows are 189-201 px apart (the leaning trunk is a little shorter on screen than
    standing): move the whole head-and-chest block as ONE piece to the Height and BELT rows of each frame.
  - Stride: one step = 275 source px = 45.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 45.5 game px = the light class stride: the fitted legs are within 5% of the class mannequin's (leg factor 0.977), so the class stride is kept. The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 68.8 px per frame (the mannequin: 68.7-68.8 px; tolerance 3 px) - the engine moves the unit
    11.4 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=284 -> R2 x=215 -> R3 x=146
      far foot: R5 x=296 -> R6 x=227 -> R7 x=159
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      R1: feet x 104 .. 284 (hip column 192; near toe 284, far toe 73), far 100 px up
      R2: feet x 117 .. 215 (hip column 192; near toe 215, far toe 97), far 107 px up
      R3: feet x 87 .. 228 (hip column 192; near toe 146, far toe 228), far 30 px up
      R4: feet x 69 .. 337 (hip column 192; near toe 53, far toe 337), near 55 px up, far 25 px up
      R5: feet x 91 .. 296 (hip column 192; near toe 60, far toe 296), near 100 px up
      R6: feet x 104 .. 227 (hip column 192; near toe 84, far toe 227), near 107 px up
      R7: feet x 99 .. 214 (hip column 192; near toe 214, far toe 159), near 30 px up
      R8: feet x 83 .. 322 (hip column 192; near toe 322, far toe 67), near 25 px up, far 55 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      R1: butt (239,803) fist (311,695) tip (335,570)  angle 68 deg  butt->tip 252 px
      R2: butt (238,793) fist (311,686) tip (336,561)  angle 67 deg  butt->tip 252 px
      R3: butt (226,809) fist (303,705) tip (332,581)  angle 65 deg  butt->tip 251 px
      R4: butt (215,811) fist (295,710) tip (329,587)  angle 63 deg  butt->tip 251 px
      R5: butt (213,799) fist (296,700) tip (332,578)  angle 62 deg  butt->tip 251 px
      R6: butt (218,792) fist (299,692) tip (334,569)  angle 62 deg  butt->tip 251 px
      R7: butt (223,809) fist (301,706) tip (332,583)  angle 64 deg  butt->tip 251 px
      R8: butt (231,815) fist (305,709) tip (331,585)  angle 66 deg  butt->tip 252 px
    FIST -> TIP = 127-128 px in every frame (the holding fist's centre to the weapon's tip; the same piece every frame):
    keep that length - never lengthen the shaft to reach the tip row nor shorten it; move the fist WITH the weapon.

PERSONALITY (this character's own run):
  - An elf scout's GLIDING lope - the opposite of Kiara's bouncing forest run: the hips stay LEVEL through the whole cycle (the mannequin's hip height changes by less than 1 px - no rise and fall), the lean 1-2 deg more than the light class mannequin, and the head is pinned level, eyes on the horizon (the neck turned back up 7 deg against the lean - the 'hawkeye' scan). The mannequin already has all of it - follow it.
  - Quiet, economical hips and shoulders: small pelvis twist (5 deg, class 7) and chest counter-turn (3, class 6) - the trunk barely turns. Long, LOW, reaching strides: the knee drives low through the passing frame, the recovering heel stays low behind (no kick-up), and the front foot reaches out long before each landing - a ground-eating glide, not a sprint.
  - The BOW is carried READY, low and canted forward, in the FAR (left) hand at the idle grip: the far arm reaches down and forward almost relaxed (elbow ~70 deg), the stave tilted forward about 64 deg - upper limb tip ahead of the chest, lower limb tip back by the knee, string toward the body, no arrow nocked. It sways only a few px with the arm. The teal see-through bow on the guide (curved limbs, thin string) marks it: paint the silver recurve limbs, the wrapped grip and the thin string at the idle size (~125 px grip to upper tip, ~128 px to lower tip).
  - The near (right) hand is free and quiet: a loose, half-open hand with a SMALL swing (under half the class swing, one frame late) - he does not pump his arms.
  - The quiver stays fixed on the back (white fletchings over the far shoulder). The long blond hair below the green ribbon, the rear edge of the green shoulder cloak and the knee-length rear tunic flap stream back evenly one frame late - because the body does not bob, they trail in a smooth line rather than bouncing.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 66 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=474-486 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_kai_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_kai_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/hero/kai --gait run --src art/inbox/gait/sheet_hero_kai_run_a.png art/inbox/gait/sheet_hero_kai_run_b.png --pose art/requests/gait/run__hero_kai/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_hero_kai_preview_x4.png and sheet_hero_kai_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_kai_run - 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_hero_kai.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_kai_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
