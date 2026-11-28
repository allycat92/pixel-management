# 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동 (3D 마네킹) · `sheet/hero/astel` → `gait/sheet_hero_astel_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/astel --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `astel`)이 로브(robe) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 96ms 박자로 넘긴다. 박자·디딘 발 규칙은 로브 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_robe_a.png` / `guide_robe_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 G1~G4 / G5~G8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870 |
| `guide_robe_plain_a.png` / `guide_robe_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_robe_a.png` / `size_robe_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 G1/G5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_robe.gif` / `preview_robe_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 96ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_astel/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_astel.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **로브** — purple scholar robe with gold embroidery, split shin-length panels and visible trousers between the panels; staff and an open book at the hip. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_astel_run_a.png` (G1~G4) + `art/inbox/gait/sheet_hero_astel_run_b.png` (G5~G8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_astel_run - 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동」 + 「## 판정 — gait/sheet_hero_astel_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 지팡이 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 — 두 손으로 쥐면 두 손 모두 (가이드: G1:65 G2:64 G3:58 G4:52 G5:49 G6:51 G7:55 G8:62).
- 보폭: 한 걸음 게임 23.9px = 로브 부류 보폭 22.2px × 다리 비율 1.077 — 맞춘 마네킹의 다리(허벅지+정강이+발목)가 부류 마네킹보다 +8% 길어, 같은 관절 각도·같은 무릎 굽힘으로 디디면 한 걸음이 그만큼 길다(다리 비율 규칙: 5% 넘게 다르면 보폭이 다리를 따른다; 그대로 부류 보폭을 쓰면 무릎이 펴지거나 발이 덜 나간다). 엔진(js/battle.js runCells)은 시트마다 그 시트의 runStride/4 씩 디딘 칸을 넘기므로 디딘 발은 미끄러지지 않는다. 유닛의 빠르기는 그대로(같은 거리에서 걸음 수만 조금 적다), 박자(96ms)는 부류 그대로.
- 디딘 발: 한 걸음 원본 144.51px(게임 23.9px) → 디딘 발은 칸마다 **정확히 36.1px**(±3, 게임 6.0px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_astel_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/robe__hero_astel/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 지팡이 = 곧은 막대와 끝의 둥근 머리.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓는다. 각도는 대기 그대로이거나 대기에서 약 15도 안(얼마나·왜 바뀌는지는 아래 「각도」 줄) — 대기의 무기를 쥔 주먹을 축으로 그만큼 한 덩어리로 돌려 그린다. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 3도(양손 무기 1.5도) 이하, 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠). 표의 **둘째 주먹은 밑동→끝 직선 위**에 있다(1.5px 안으로 검사) — 자루를 두 주먹을 지나는 한 직선으로 긋고, 둘째 손에서 꺾지 않는다.
- **각도**: 달리기는 지팡이을(를) 화면에서 82도로 든다 — 대기 약 78도에서 +4도(약 15도 안). 대기의 무기를 그대로(길이·모양·곧은 자루) 쥔 주먹을 축으로 그만큼만 한 덩어리로 돌린다. 모든 프레임에서 같은 각도.
- **로브**: 반투명 로브 모양은 **움직이지 않는 대리 모양**이다 — 로브의 크기·자락 높이·무릎을 가린다는 것만 알려 주고, 걸음마다 일부러 움직이지 않는다(한 걸음 4프레임에서 걸음마다 움직이면 지그재그가 된다). 천의 작은 흔들림은 그 위에 한 프레임 늦게 그린다(닿기에서 뒷다리에 밀려 조금 뒤로, 지나가기까지 가라앉음) — 몇 px, 프레임 사이 매끈하게, 튀지 않게.
- 단계(3D 가이드 그대로): G1 **닿기**(두 발 모두 바닥: 앞발은 막 디뎠고 뒷발은 발끝으로, 뒤꿈치 듦) - G2 **내려앉기**(엉덩이 가장 낮음, 뒷발이 떨어져 발끝이 몇 px 뜸) - G3 **지나가기**(드는 발이 디딘 발 옆을 지나 앞으로, 약 10px 뜸) - G4 **내딛기**(드는 발이 **엉덩이보다 앞**, 발끝을 들고 바닥 위 약 5px — 곧 디딘다; 디딘 발 뒤꿈치는 이제 막 뜨기 시작). G5~G8 은 먼 발로 같은 동작. **G4·G8 에서 드는 발은 엉덩이 열보다 앞**(아래 발 표) — 뒤에 남기거나 밀어 내는 자세가 아니다. 뒷발은 표보다 더 뒤로 빠지지 않고, 아무것도 x=32 / x=351 선에 닿지 않는다.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 서고에 늦은 학자의 종종걸음: 로브 부류보다 덜 기울고 턱이 앞서 나가며, 엉덩이가 크게 비틀려(6도) 트인 로브 자락이 좌우로 스친다. 지팡이는 가슴 앞에 곧게.

- 꼿꼿하고 바쁜 학자의 종종걸음 — 싸움꾼이 아니라 서고에 늦은 사람: 몸통은 로브 부류보다 1~2도 덜 기울고(약 5~6도), 엉덩이는 2px 쯤 높게 곧은 디딤 다리 위에 얹히며, 목이 머리를 5도쯤 앞으로 내밀되 얼굴은 수평 — 턱이 앞서고 안경 너머로 앞길을 본다 (3D 마네킹에 이미 들어 있다 — 따라 그린다).
- 엉덩이가 로브 부류보다 조금 더 돈다(골반 비틀림 4 대신 6): 짧고 빠른 걸음마다 트인 로브의 앞·뒷자락이 좌우로 스친다. 자락은 장화보다 한 프레임 늦고 바닥에 닿지 않으며, 대기 그림처럼 트인 사이로 바지가 보인다.
- 지팡이는 대기 그림 그대로의 쥠새로 가까운 손이 가슴 높이에서 곧게 세워 든다(고리 머리가 약 8도 앞으로, 얼굴 앞 가장자리 앞). 팔을 따라 몇 도 이내로만 흔들리고 휘두르지 않으며, 밑동은 바닥에 닿지 않는다.
- 빈 손(먼 손)은 느슨한 주먹으로 허리띠 버클 앞에서 짧고 빠르게 흔든다 — 낮고 몸 가까이, 가슴 옆에서 흔드는 바렌과 다르다.
- 묶은 긴 머리 꼬리와 짧은 어깨 망토는 한 프레임 늦다(G3/G7 에서 조금 뜨고 G1/G5 에서 가라앉는다). 가까운 허리의 펼친 책은 끈에 매인 채 엉덩이와 함께 2~3px 튄다.

## 요약 (한국어)

아스텔 — 마탑의 마지막 제자 (마탑 계승자)의 로브 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_astel_run_a.png`·`art/inbox/gait/sheet_hero_astel_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 아스텔: 젊은 남자, 뒤로 넘겨 금색 머리고리로 낮게 묶은 긴 은회색 머리(#c9c2b8)와 관자놀이의 흘러내린 가닥, 검은 테 동그란 안경, 차분하고 진지한 얼굴(피부 #f2c9a0); 금색(#f2d24b) 덩굴 자수와 금테를 두른 짙은 보라 로브(#3a1a5a), 둥근 자홍 보석 브로치와 크림색 크라바트가 달린 짧은 어깨 망토, 금 버클의 갈색 가죽 허리띠, 정강이까지 앞·뒤로 갈라진 긴 자락(금테 앞자락에 금색 문장)과 그 사이로 보이는 짙은 보라 바지, 금띠 두른 짙은 보라 장화, 가까운 허리에 가죽 끈으로 맨 펼친 책; 지팡이: 금장식의 짙은 갈색 나무 자루, 금 밑동, 보라 구슬을 감싼 네 갈래 금고리 머리 (빛 없음). 개성 — 서고에 늦은 학자의 종종걸음: 로브 부류보다 덜 기울고 턱이 앞서 나가며, 엉덩이가 크게 비틀려(6도) 트인 로브 자락이 좌우로 스친다. 지팡이는 가슴 앞에 곧게. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 36.1px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the ROBE GLIDE (hurried, purposeful) CYCLE (8 frames, movement class ROBE) of 아스텔 — 마탑의 마지막 제자 (마탑 계승자) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_astel_run_a.png  = frames G1 G2 G3 G4
  art/inbox/gait/sheet_hero_astel_run_b.png  = frames G5 G6 G7 G8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/robe__hero_astel/guide_robe_a.png, guide_robe_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/robe__hero_astel/guide_robe_plain_a.png, guide_robe_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/robe__hero_astel/size_robe_a.png, size_robe_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/robe__hero_astel/preview_robe.gif, preview_robe_game_x4.gif = the motion at speed (96 ms a frame).
  - art/inbox/sheet_hero_astel.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_astel/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/robe__hero_astel/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Astel (아스텔), the last disciple of the burned mage tower, exactly as on the accepted sheet: young man, long pale silver-grey hair (#c9c2b8) swept back, tied low into a tail with a gold hair ring, loose strands at the temples; round dark-rimmed glasses; calm, serious face (skin #f2c9a0); deep-purple robe (#3a1a5a) with gold (#f2d24b) scroll embroidery and gold trim, a short shoulder capelet with a round magenta-gem brooch and a cream cravat; brown leather belt with a gold buckle; the robe split into long front and back panels to the shins (a gold-trimmed front tab with a gold fleur mark) with dark-purple trousers showing in the split; dark-purple boots with gold bands; an OPEN book in a leather holder strapped at the near hip; the staff: a dark-brown wooden shaft with gold fittings, a gold butt cap and a gold RING head with four points around a purple orb (no glow).

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    STAFF = a straight pole with a round knob at the end.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip). A
    straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it. Never
    shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S) and TIP
    for each frame (+-4 px). Its angle is the idle's or within ~15 deg of it (the ANGLE line below says how much and
    why): draw the idle's own weapon turned by that much as one piece about the holding fist. The tip MAY be above the
    head and is NOT limited by the Height numbers - those are the top of the HEAD (hair / helmet / hat) only. Between
    neighbouring frames the weapon turns at most 3 deg (two-handed: 1.5) and its tip follows the smooth path of the
    table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the weapon
    rides with the chest (strip b = strip a). The table's 2ND FIST is ON the butt -> tip line (checked <= 1.5 px): draw
    the shaft as one straight line through BOTH fists - never kink it at the second hand.
  - ANGLE: the run carries the staff at 82 deg on screen, +4 deg from the idle's ~78 (within ~15) - keep the idle's weapon as drawn (same length, shape, straight shaft), turned as one piece about the holding fist by that little; the same angle in every frame.
  - WRIST RANGE (owner rule; EVERY hand on the weapon, a two-handed grip's second hand too): every held weapon's GRIP
    AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (G1:65 G2:64 G3:58 G4:52 G5:49 G6:51 G7:55 G8:62 deg).
  - ROBE: the see-through robe shape is a STEADY proxy - it gives the robe's size, its hem height and that the hem
    covers the knees; it does not move with each step on purpose (moved per step at 4 frames a step it zig-zagged).
    Paint the cloth's own small one-frame-late sway on it (the hem pushed back a little by the trailing leg at
    contact, settling by passing) - a few px, smooth from frame to frame, never a jump.
  - The mannequin's round head is a placeholder: paint the character's own head, hair and headgear at the idle's size on
    its neck. The joints, limbs and torso are fitted to the idle - put the character's own body exactly on them.
  - PAINT OVER EVERY MANNEQUIN PIXEL. add_gait.py refuses a strip in which >= 25% of a frame still has the mannequin's
    colours, and a recoloured mannequin (silhouette IoU > 0.93 with this guide). Clothing, hair, cloth and the real
    weapon change the silhouette - that is the work.
  - FLOOR: the standing sole on y=870; nothing of the body below it. A weapon tip or cloth that would dip below the
    floor line (or below y=852 in a flight frame) is touched up while painting - lift it a little.
  - Samples of other characters are only baselines. Do not recolour another character's strip.

THE MOVE (movement class robe: loose long cloth: running in it looks unnatural. Fastest natural gait = a hurried, purposeful glide (not a stroll): NO flight phase, NO big knee lift, a small forward lean, short quick steps; the hem swings and hides the knees, only the feet flick out at the hem. - with this character's personality on top, already in the mannequin):
  - G1 CONTACT (both feet on the floor: the front foot just landed, the rear foot on its toe, heel up) - G2 DOWN (lowest hips; the rear foot lifts off, toe a few px up) - G3 PASSING (the swing foot is carried forward past the planted foot, ~10 px up) - G4 REACH (the swing foot is AHEAD of the hip, toes up, ~5 px above the floor, about to land; the planted heel only starts to peel). G5-G8 = the same with the far foot.
  - In G4 / G8 the swing foot is IN FRONT of the hip column (table FEET below) - not left behind, not a push-off lunge. No foot is behind the planted foot except where the table says so; the rear foot never trails further back than the table, and nothing touches the slot band lines x=32 / x=351.
  - Lean forward (hip to neck): G1/G5 5.6, G2/G6 6.1, G3/G7 5.3, G4/G8 5.3 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=435/437/432/432 in G1 G2 G3 G4 (the same in G5 G6 G7 G8): G1 +0, G2 +2, G3 -3, G4 -3 px from G1 (+ = lower) - move your head top by the same amounts (bob 5 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - Stride: one step = 144.51 source px = 23.9 game px; 8 frames = two steps, 96 ms a frame in the game.
  - Stride rule: 23.9 game px = the robe class stride 22.2 px x leg factor 1.077: this character's fitted legs are 8% longer than the class mannequin's, so the same joint angles and stance-knee bend give a longer step (legs more than 5% off -> the stride follows the legs). The engine advances each sheet by its OWN runStride/4 per planted cell, so the planted foot does not slide; the unit's ground speed is unchanged (a few fewer steps). The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 36.1 px per frame (the mannequin: 36.1-36.2 px; tolerance 3 px) - the engine moves the unit
    6.0 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: G1 x=286 -> G2 x=250 -> G3 x=213 -> G4 x=177  (-> G5 x=141 as the REAR foot, heel up, toe still on the floor)
      far foot: G5 x=286 -> G6 x=250 -> G7 x=213 -> G8 x=177  (-> G1 x=141 as the REAR foot, heel up, toe still on the floor)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      G1: feet x 80 .. 286 (hip column 192; near toe 286, far toe 141), both soles down
      G2: feet x 95 .. 250 (hip column 192; near toe 250, far toe 148), far 8 px up
      G3: feet x 147 .. 236 (hip column 192; near toe 213, far toe 236), far 11 px up
      G4: feet x 112 .. 272 (hip column 192; near toe 177, far toe 272), far 6 px up
      G5: feet x 80 .. 286 (hip column 192; near toe 141, far toe 286), both soles down
      G6: feet x 95 .. 250 (hip column 192; near toe 148, far toe 250), near 8 px up
      G7: feet x 147 .. 236 (hip column 192; near toe 236, far toe 213), near 11 px up
      G8: feet x 112 .. 272 (hip column 192; near toe 272, far toe 177), near 6 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      G1: butt (233,719) fist (252,616) tip (291,410)  angle 79 deg  butt->tip 315 px
      G2: butt (235,719) fist (253,616) tip (290,410)  angle 80 deg  butt->tip 315 px
      G3: butt (238,705) fist (253,601) tip (283,393)  angle 82 deg  butt->tip 315 px
      G4: butt (241,695) fist (252,590) tip (274,382)  angle 84 deg  butt->tip 315 px
      G5: butt (243,694) fist (252,589) tip (270,380)  angle 85 deg  butt->tip 315 px
      G6: butt (243,698) fist (253,594) tip (273,385)  angle 85 deg  butt->tip 315 px
      G7: butt (240,701) fist (253,597) tip (280,388)  angle 83 deg  butt->tip 315 px
      G8: butt (236,710) fist (253,606) tip (288,400)  angle 81 deg  butt->tip 315 px

PERSONALITY (this character's own run):
  - An upright, hurried scholar's glide - a man late for the library, not a fighter: the trunk leans 1-2 deg LESS than the robe class (about 5-6 deg), the hips ride ~2 px higher on a straighter stance leg, and the neck pushes the head ~5 deg forward while the face stays level - chin leading, eyes on the road through the glasses (the mannequin already has all of it - follow it).
  - The hips roll a little more than the robe class (pelvis twist 6 instead of 4), so the split front and back panels of the robe swish side to side with each short, quick step; the panels trail the boots by one frame and never reach the floor, the trousers show in the split as on the idle.
  - The staff rides UPRIGHT in the near hand at chest height with exactly the idle grip (ring head tipped ~8 deg forward, in front of the face's front edge): it rides the arm, sways at most a few degrees and never swings, the butt never touches the floor.
  - The free (far) hand is a loose fist that pumps short and brisk in front of the belt buckle - low and close, not Baren's tight pump beside the chest.
  - The long tied hair tail and the short shoulder cape lag one frame (lift a little in G3/G7, settle in G1/G5); the open book at the near hip bounces 2-3 px with the hip on its strap.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_robe_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 78 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=432-437 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_astel_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_astel_run_b.png
  python3 tools/art/add_gait.py sheet/hero/astel --gait run --src art/inbox/gait/sheet_hero_astel_run_a.png art/inbox/gait/sheet_hero_astel_run_b.png --pose art/requests/gait/robe__hero_astel/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS. The third must end without an error and write
<temp dir>/sheet_hero_astel_preview_x4.png and sheet_hero_astel_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_astel_run - 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_robe_a/b, guide_robe_plain_a/b, size_robe_a/b, preview_robe.gif, sheet_hero_astel.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_astel_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
