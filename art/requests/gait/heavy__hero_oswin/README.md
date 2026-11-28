# 오스윈 — 몰락한 기사단장 (몰락 기사단장) 이동 (3D 마네킹) · `sheet/hero/oswin` → `gait/sheet_hero_oswin_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/oswin --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `oswin`)이 중량(heavy) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 101ms 박자로 넘긴다. 박자·디딘 발 규칙은 중량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

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
- 무기: 칼 (먼 손), 칼 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 — 두 손으로 쥐면 두 손 모두 (가이드: H1:100 H2:99 H3:98 H4:98 H5:97 H6:98 H7:98 H8:99; 둘째 손(먼 손)은 제 아래팔에 대해: H1:99 H2:96 H3:91 H4:87 H5:85 H6:86 H7:90 H8:97).
- 보폭: 한 걸음 게임 23.6px = 중량 부류 보폭 그대로 — 맞춘 다리가 부류 마네킹과 5% 안(다리 비율 1.010)이라 다리 비율 규칙을 쓰지 않는다. 박자(101ms)도 부류 그대로.
- 디딘 발: 한 걸음 원본 142.5px(게임 23.6px) → 디딘 발은 칸마다 **정확히 35.6px**(±3, 게임 5.9px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_oswin_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/heavy__hero_oswin/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 칼 = 손잡이, 십자 코등이, 칼날.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓는다. 각도는 대기 그대로이거나 대기 가까이(얼마나·프레임마다 어떻게·왜 바뀌는지는 아래 「각도」 줄) — 대기의 무기를 쥔 주먹을 축으로 프레임마다 표의 각도까지 한 덩어리로 돌려 그린다. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 최대 0.1도(이 마네킹에서 잰 값; 검사 한도 양손 무기 1.5도), 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠). 표의 **둘째 주먹은 밑동→끝 직선 위**에 있다(1.5px 안으로 검사) — 자루를 두 주먹을 지나는 한 직선으로 긋고, 둘째 손에서 꺾지 않는다.
- **각도**: 달리기는 칼을(를) 화면에서 73도로, 모든 프레임에서 같은 각도(표: 73도) — 대기 약 61도에서 +12도(약 15도 안). 대기의 무기를 그대로(길이·모양·곧은 자루) 쥔 주먹을 축으로 그만큼만 한 덩어리로 돌린다 — 그 한 각도로. 이 각도에서 잰 값: 무기를 포함한 그림 전체가 칸(x 32~351) 안쪽으로 33px 이상(검사는 8px 이상).
- 단계(3D 가이드 그대로): H1 **닿기**(두 발 모두 바닥: 앞발은 막 디뎠고 뒷발은 발끝으로, 뒤꿈치 듦) - H2 **내려앉기**(엉덩이 가장 낮음, 뒷발이 떨어져 발끝이 몇 px 뜸) - H3 **지나가기**(드는 발이 디딘 발 옆을 지나 앞으로, 약 10px 뜸) - H4 **내딛기**(드는 발이 **엉덩이보다 앞**, 발끝을 들고 바닥 위 약 5px — 곧 디딘다; 디딘 발 뒤꿈치는 이제 막 뜨기 시작). H5~H8 은 먼 발로 같은 동작. **H4·H8 에서 드는 발은 엉덩이 열보다 앞**(아래 발 표) — 뒤에 남기거나 밀어 내는 자세가 아니다. 뒷발은 표보다 더 뒤로 빠지지 않고, 아무것도 x=32 / x=351 선에 닿지 않는다.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 기사단과 이름을 잃은 노기사단장의 무거운 행군: 로드릭과 반대로 상체를 앞으로 숙이고(약 10도) 턱을 당겨 눈썹 아래로 앞을 보며, 엉덩이는 내내 낮게 깔려 거의 오르내리지 않는다(출렁임 약 5px). 대신 어깨와 골반이 좌우로 구르지만(6/4) 두 손 장검은 가슴에 고정되어 기울지 않는다.

- 늙은 기사단장의 무겁고 지친 행군 — 기사단과 이름을 잃고도 걷는다: 몸통을 앞으로 약 10도 숙이고(중량 마네킹 5도, 로드릭은 3도로 꼿꼿), 판금 아래 어깨가 둥글게 말린다. 턱을 **당겨** 짙은 회색 눈썹 아래로 앞을 본다(목을 되세우지 않는다). 3D 마네킹에 이미 들어 있다 — 따라 그린다.
- 낮고 평평하게: 무릎은 내내 굽어 있고 엉덩이는 부류 마네킹보다 4~7px 낮게 깔려 거의 오르내리지 않는다(한 바퀴 출렁임 약 5px — 닿기 프레임에서 뒷발이 기준 보폭 안에 있게 약 3px 올라온다 — 로드릭은 디딜 때마다 11px 가라앉았다 올라온다). 드는 발은 무릎을 조금 더 굽혀 낡은 장화가 땅에 걸리지 않게 — 터벅터벅 신중한 걸음.
- 구르는 어깨: 엉덩이와 가슴이 중량 부류보다 **더** 돈다(골반 6도, 가슴 반대 회전 4) — 판금 입은 노인의 좌우로 흔들리는 무게, 로드릭의 네모나게 굳은 몸통이 아니다.
- 양손 장검은 대기 그림처럼 제 길이 그대로 든다 — 두 주먹이 한 손잡이에(가까운 주먹은 허리띠 위, 먼 주먹은 십자 가드 바로 밑), 팔꿈치는 몸에 붙이고, 칼날은 앞-위로 약 72도. 장검은 가슴에 고정된다: 모든 프레임에서 같은 각도·같은 길이, 몸의 출렁임만 따른다 — 구르는 어깨를 따라 기울지 않고, 베거나 휘두르지 않는다.
- 뒤쪽 파란 망토와 해진 타바드는 구르는 엉덩이를 따라 한 프레임 늦게 무겁게 흔들린다. 회색 머리와 수염은 거의 들리지 않는다(머리가 오르내리지 않는다).

## 요약 (한국어)

오스윈 — 몰락한 기사단장 (몰락 기사단장)의 중량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_oswin_run_a.png`·`art/inbox/gait/sheet_hero_oswin_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 오스윈(몰락한 기사단장): 뒤로 넘긴 헝클어진 회색 머리, 짙은 회색 눈썹과 짧은 회색 수염, 엄하고 주름진 얼굴. 녹슨 자국이 큼직하게 몇 군데 있는 낡은 은빛 판금 갑옷(놋쇠 리벳 원판이 달린 둥글고 큰 어깨갑, 흉갑, 마디 팔갑과 건틀릿, 허벅지 판, 둥근 무릎 덮개, 정강이갑과 철신), 가슴에 바랜 왕실 문장 = 파란 방패 모양 하나, 놋쇠 버클의 갈색 가죽 허리띠, 다리 사이 앞으로 늘어진 해진 긴 파란 타바드와 뒤쪽의 해진 파란 망토, 양손으로 쥔 유럽식 양손 장검 한 자루(녹 자국이 있는 곧고 긴 칼날, 놋쇠 십자 가드와 폼멜, 가죽 손잡이). 개성 — 기사단과 이름을 잃은 노기사단장의 무거운 행군: 로드릭과 반대로 상체를 앞으로 숙이고(약 10도) 턱을 당겨 눈썹 아래로 앞을 보며, 엉덩이는 내내 낮게 깔려 거의 오르내리지 않는다(출렁임 약 5px). 대신 어깨와 골반이 좌우로 구르지만(6/4) 두 손 장검은 가슴에 고정되어 기울지 않는다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 35.6px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

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
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    SWORD = grip, cross guard, blade.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip).
    A straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it.
    Never shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S)
    and TIP for each frame (+-4 px). Its angle is the idle's or near it (the ANGLE line below says how much, how it
    changes from frame to frame and why): draw the idle's own weapon turned as one piece about the holding fist to the
    table's angle in each frame. The tip MAY be above the head and is NOT limited by the Height numbers - those are
    the top of the HEAD (hair / helmet / hat) only. Between neighbouring frames the weapon turns at most 0.1 deg
    (measured on this mannequin; the check allows 1.5 for a two-handed weapon) and its tip follows the smooth path of
    the table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the
    weapon rides with the chest (strip b = strip a). The table's 2ND FIST is ON the butt -> tip line (checked <= 1.5
    px): draw the shaft as one straight line through BOTH fists - never kink it at the second hand.
  - ANGLE: the run carries the sword at 73 deg on screen, the same angle in every frame (the table: 73) - +12 deg from
    the idle's ~61 (within ~15). Keep the idle's weapon as drawn (same length, shape, straight shaft), turned as one
    piece about the holding fist by that little - one fixed angle. Measured at this carry: the whole figure, weapon
    included, stays >= 33 px inside the slot band x 32..351 (the check needs >= 8).
  - WRIST RANGE (owner rule; EVERY hand on the weapon, a two-handed grip's second hand too): every held weapon's GRIP
    AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (H1:100 H2:99 H3:98 H4:98 H5:97 H6:98 H7:98 H8:99; the second (far) hand, against its own forearm: H1:99 H2:96 H3:91 H4:87 H5:85 H6:86 H7:90 H8:97 deg).
  - The mannequin's round head is a placeholder: paint the character's own head, hair and headgear at the idle's size on
    its neck. The joints, limbs and torso are fitted to the idle - put the character's own body exactly on them.
  - PAINT OVER EVERY MANNEQUIN PIXEL. add_gait.py refuses a strip in which >= 25% of a frame still has the mannequin's
    colours, and a recoloured mannequin (silhouette IoU > 0.93 with this guide). Clothing, hair, cloth and the real
    weapon change the silhouette - that is the work.
  - FLOOR: the standing sole on y=870; nothing of the body below it. A weapon tip or cloth that would dip below the
    floor line (or below y=852 in a flight frame) is touched up while painting - lift it a little.
  - Samples of other characters are only baselines. Do not recolour another character's strip.

THE MOVE (movement class heavy: heavy armour / tower shield / very large weapon: cannot really run. Fastest natural gait for that body = a heavy, purposeful, FAST trudge (not a stroll): NO flight phase (one foot always on the ground), torso upright, short stride, the weight dropped onto each footfall, arms held close and high. - with this character's personality on top, already in the mannequin):
  - H1 CONTACT (both feet on the floor: the front foot just landed, the rear foot on its toe, heel up) - H2 DOWN (lowest hips; the rear foot lifts off, toe a few px up) - H3 PASSING (the swing foot is carried forward past the planted foot, ~10 px up) - H4 REACH (the swing foot is AHEAD of the hip, toes up, ~5 px above the floor, about to land; the planted heel only starts to peel). H5-H8 = the same with the far foot.
  - In H4 / H8 the swing foot is IN FRONT of the hip column (table FEET below) - not left behind, not a push-off lunge. No foot is behind the planted foot except where the table says so; the rear foot never trails further back than the table, and nothing touches the slot band lines x=32 / x=351.
  - Lean forward (hip to neck): H1/H5 10.1, H2/H6 10.7, H3/H7 10.1, H4/H8 9.9 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=463/468/466/465 in H1 H2 H3 H4 (the same in H5 H6 H7 H8): H1 +0, H2 +5, H3 +3, H4 +2 px from H1 (+ = lower) - move your head top by the same amounts (bob 5 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - Stride: one step = 142.5 source px = 23.6 game px; 8 frames = two steps, 101 ms a frame in the game.
  - Stride rule: 23.6 game px = the heavy class stride: the fitted legs are within 5% of the class mannequin's (leg factor 1.010), so the class stride is kept. The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 35.6 px per frame (the mannequin: 35.6-35.7 px; tolerance 3 px) - the engine moves the unit
    5.9 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: H1 x=275 -> H2 x=239 -> H3 x=204 -> H4 x=168  (-> H5 x=132 as the REAR foot, heel up, toe still on the floor)
      far foot: H5 x=275 -> H6 x=239 -> H7 x=204 -> H8 x=168  (-> H1 x=132 as the REAR foot, heel up, toe still on the floor)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      H1: feet x 74 .. 275 (hip column 192; near toe 275, far toe 132), both soles down
      H2: feet x 104 .. 239 (hip column 192; near toe 239, far toe 152), far 8 px up
      H3: feet x 141 .. 233 (hip column 192; near toe 204, far toe 233), far 16 px up
      H4: feet x 106 .. 266 (hip column 192; near toe 168, far toe 266), far 9 px up
      H5: feet x 74 .. 275 (hip column 192; near toe 132, far toe 275), both soles down
      H6: feet x 104 .. 239 (hip column 192; near toe 152, far toe 239), near 8 px up
      H7: feet x 141 .. 233 (hip column 192; near toe 233, far toe 204), near 16 px up
      H8: feet x 106 .. 266 (hip column 192; near toe 266, far toe 168), near 9 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      H1: butt (230,691) fist (236,670) 2nd fist (246,639) tip (315,418)  angle 73 deg  butt->tip 286 px
      H2: butt (231,696) fist (237,675) 2nd fist (247,644) tip (317,423)  angle 73 deg  butt->tip 286 px
      H3: butt (230,694) fist (236,673) 2nd fist (246,642) tip (316,421)  angle 73 deg  butt->tip 286 px
      H4: butt (229,693) fist (236,672) 2nd fist (246,642) tip (315,420)  angle 73 deg  butt->tip 286 px
      H5: butt (230,691) fist (236,670) 2nd fist (246,640) tip (315,418)  angle 73 deg  butt->tip 286 px
      H6: butt (231,696) fist (237,675) 2nd fist (247,644) tip (317,423)  angle 73 deg  butt->tip 286 px
      H7: butt (230,694) fist (236,673) 2nd fist (246,642) tip (316,420)  angle 73 deg  butt->tip 286 px
      H8: butt (230,693) fist (236,672) 2nd fist (246,642) tip (315,420)  angle 73 deg  butt->tip 286 px

PERSONALITY (this character's own run):
  - An OLD knight commander's heavy, weary march - he lost his order and his name, and still marches on: the trunk LEANS forward about 10 deg (the heavy class mannequin leans 5; Roderick stands at 3), the shoulders rounded under the plate, the chin DOWN so he looks ahead from under his heavy grey brows (the neck does not turn back up). The mannequin already has all of it - follow it.
  - Low and level: the knees stay bent the whole cycle, the hips sit 4-7 px below the class mannequin and barely rise or fall (about 5 px over the cycle; at the contact frames they come up ~3 px so the trailing boot stays within the reference stride - Roderick dips 11 px into each footfall and rises again). The lifted foot is picked up a little (foot a few px higher in the passing and reach frames) so the old boots clear the ground - a plodding, deliberate step.
  - Rolling shoulders: the hips and the chest turn MORE than the heavy class (pelvis twist 6 deg, chest counter-turn 4) - a side-to-side heave of an old man in plate, not Roderick's square, locked trunk.
  - The two-handed longsword is held as in the idle at its full length - BOTH fists on one hilt (near fist on the belt, far fist just under the cross-guard), elbows tucked, the blade forward-up at about 72 deg. It is LOCKED to the chest: the same angle and length in every frame, riding only the body's bob - it does not tip with the rolling shoulders, no slash, no swing.
  - The rear blue cape and the tattered tabard swing heavily one frame late with the rolling hips; the grey hair and beard barely lift (the head does not bob).
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_heavy_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 71 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=463-468 (a weapon may reach higher).
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
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
