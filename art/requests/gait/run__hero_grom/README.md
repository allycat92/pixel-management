# 그롬 — 피의 투기장 챔피언 (투기장 패왕) 이동 (3D 마네킹) · `sheet/hero/grom` → `gait/sheet_hero_grom_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/grom --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `grom`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_grom/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_grom.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — massive orc arena champion: fur collar, gold champion belt, cloth hip panels, trousers, boots; greatsword. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_grom_run_a.png` (R1~R4) + `art/inbox/gait/sheet_hero_grom_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_grom_run - 그롬 — 피의 투기장 챔피언 (투기장 패왕) 이동」 + 「## 판정 — gait/sheet_hero_grom_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 칼 (먼 손), 칼 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 — 두 손으로 쥐면 두 손 모두 (가이드: R1:84 R2:82 R3:83 R4:82 R5:81 R6:81 R7:83 R8:85; 둘째 손(먼 손)은 제 아래팔에 대해: R1:69 R2:70 R3:65 R4:67 R5:72 R6:72 R7:66 R8:64).
- 보폭: 한 걸음 게임 45.5px = 경량 부류 보폭 그대로 — 맞춘 다리가 부류 마네킹과 5% 안(다리 비율 1.014)이라 다리 비율 규칙을 쓰지 않는다. 박자(80ms)도 부류 그대로.
- 디딘 발: 한 걸음 원본 275px(게임 45.5px) → 디딘 발은 칸마다 **정확히 68.8px**(±3, 게임 11.4px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_grom_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__hero_grom/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 칼 = 손잡이, 십자 코등이, 칼날.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓는다. 각도는 대기 그대로이거나 대기 가까이(얼마나·프레임마다 어떻게·왜 바뀌는지는 아래 「각도」 줄) — 대기의 무기를 쥔 주먹을 축으로 프레임마다 표의 각도까지 한 덩어리로 돌려 그린다. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 최대 1.4도(이 마네킹에서 잰 값; 검사 한도 양손 무기 1.5도), 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠). 표의 **둘째 주먹은 밑동→끝 직선 위**에 있다(1.5px 안으로 검사) — 자루를 두 주먹을 지나는 한 직선으로 긋고, 둘째 손에서 꺾지 않는다.
- **각도**: 달리기는 칼을(를) 화면에서 약 69도로, 가슴과 함께 68~70도 사이에서 흔들리며 이웃 프레임 사이 최대 1.4도씩 바뀐다(표 그대로) — 대기 약 60도에서 +9도(약 15도 안). 대기의 무기를 그대로(길이·모양·곧은 자루) 쥔 주먹을 축으로 그만큼만 한 덩어리로 돌린다 — 프레임마다 표의 각도로(매끈한 흔들림, 튀지 않게). 이 각도에서 잰 값: 무기를 포함한 그림 전체가 칸(x 32~351) 안쪽으로 11px 이상(검사는 8px 이상).
- 단계: R1 닿기 - R2 받기(엉덩이 가장 낮음) - R3 밀기(뒤꿈치 듦) - R4 공중(두 발 모두 뜸). R5~R8 은 먼 발로 같은 동작.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **허리띠**: 그리는 허리띠(코트·갑옷의 허리선)의 가운데는 마네킹 허리의 **갈색 띠** 가운데 — 노란 엉덩이 점이 아니다(점은 약 21px 아래, 골반 속). 프레임별 y: R1 670 / R2 676 / R3 667 / R4 664 / R5 670 / R6 676 / R7 667 / R8 664.
- **머리카락 꼭대기 → 허리띠 = 대기의 길이(207px)**: 몸통·머리를 눌러 줄이거나 늘이지 않는다. 이 가이드의 머리 꼭대기 → 허리띠 줄 간격은 200-206px(몸통이 기울어 선 자세보다 화면에서 조금 짧다) — 머리·가슴을 한 덩어리로 프레임마다 「Height」 줄과 허리띠 줄로 옮긴다.
- **주먹→끝 = 249px**: 쥔 주먹 가운데에서 무기 끝까지 모든 프레임에서 같다 — 끝 자리에 맞추려고 자루를 늘이거나 줄이지 않고, 주먹을 무기와 함께 옮긴다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 투기장 챔피언의 황소 돌진: 가슴을 펴고 받는 프레임에서 7px 무겁게 내려꽂혔다 밀어 올리며, 엉덩이가 크게 돈다(11도). 무릎은 높이, 대검은 두 손으로 몸 앞에 곧추세운다.

- 거대한 투기장 챔피언의 돌진: 경량 마네킹보다 확실히 더 곧게 선다(12도 덜 기운다 — 곧추세운 대검이 얼굴 앞으로 떨어져 선다; 가슴을 펴고, 턱을 당겨 눈썹 아래로 앞을 노려본다). 대신 받는 프레임에서 무게가 확 가라앉는다(R2/R6 엉덩이 7px 낮게, 닿기·밀기 2~3px, 공중 0) — 무겁게 착지하고 다시 밀어 올린다. 3D 마네킹에 이미 들어 있다 — 따라 그린다.
- 엉덩이가 크게 돈다(골반 비틀림 11도, 부류 기본 7도). 가슴은 더 안정적이다(역회전 4도, 기본 6도): 몸통은 다리 위에서 흔들리지만 대검은 제자리.
- 밟아 대는 황소처럼 무릎을 높이 끌어올린다: 밀기·공중 프레임(R3/R7, R4/R8)에서 앞으로 나오는 무릎이 더 높다.
- 대검은 두 손으로 몸 앞에 곧추세운다 — 가까운 손은 손잡이 아래쪽(배 앞), 먼 손은 금색 코등이 바로 밑 — 투기장에 입장하는 챔피언처럼. 칼날은 가슴에 고정되어 화면에서 약 69도(대기 약 60도에서 칸에 제 길이로 들어갈 만큼만 약 9도 세운다)로 모든 프레임에서 같은 각도·제 길이 그대로 — 몸을 따라 움직일 뿐 까딱이거나 기울지 않는다. 휘두르지 않고 어깨에 메지도 않는다(그건 바렌의 자세).
- 짧은 붉은 어깨 망토, 털 깃 끝, 찢어진 붉은 허리천, 긴 드레드 갈기는 몸보다 한 프레임 늦다: 공중 프레임(R4/R8)에서 뜨고, 받는 프레임(R2/R6)에서 무겁게 떨어진다. 금색 챔피언 벨트는 허리에 고정.

## 요약 (한국어)

그롬 — 피의 투기장 챔피언 (투기장 패왕)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_grom_run_a.png`·`art/inbox/gait/sheet_hero_grom_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 그롬(혼혈 오크 투기장 챔피언): 올리브빛 초록 피부와 얼굴을 가로지르는 흉터, 찌푸린 얼굴과 짧은 짙은 수염, 금 구슬을 꿴 긴 짙은 갈색 드레드 갈기와 금 귀고리, 양어깨를 덮는 커다란 연한 털 깃, 등 뒤로 늘어진 짧은 짙은 붉은 어깨 망토, 갈색 가슴끈과 둥근 금 어깨 장식이 있는 맨가슴, 금테 팔찌, 금색 사자 머리 챔피언 벨트, 금 장식이 달린 찢어진 짙은 붉은 허리천과 다리 사이의 긴 붉은·금 앞자락, 헐렁한 짙은 갈색 바지, 버클 달린 갈색 장화, 무거운 서양식 양손 대검 한 자루(넓고 곧은 강철 날, 금색 코등이와 칼자루 끝, 긴 손잡이) — 카타나가 아니다. 개성 — 투기장 챔피언의 황소 돌진: 가슴을 펴고 받는 프레임에서 7px 무겁게 내려꽂혔다 밀어 올리며, 엉덩이가 크게 돈다(11도). 무릎은 높이, 대검은 두 손으로 몸 앞에 곧추세운다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 68.8px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 그롬 — 피의 투기장 챔피언 (투기장 패왕) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_grom_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_hero_grom_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__hero_grom/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__hero_grom/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__hero_grom/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__hero_grom/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_hero_grom.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_grom/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__hero_grom/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Grom (그롬), the half-orc blood-arena champion, exactly as on the accepted sheet: olive-green skin with a scar across the face, stern scowl and short dark beard; a long dark-brown dreadlocked mane with gold beads and gold ear rings; a big pale FUR collar over both shoulders; a short dark-red shoulder cape hanging behind; bare muscular chest with a brown cross strap and round gold shoulder studs; gold-trimmed bracers; the gold lion-head CHAMPION BELT; ragged dark-red hip panels with gold tabs and a long red-and-gold front tabard between the legs; baggy dark-brown trousers; brown buckled boots; ONE heavy European two-handed GREATSWORD (broad straight steel blade, gold cross guard and pommel, long grip) - not a katana.

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
    the top of the HEAD (hair / helmet / hat) only. Between neighbouring frames the weapon turns at most 1.4 deg
    (measured on this mannequin; the check allows 1.5 for a two-handed weapon) and its tip follows the smooth path of
    the table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the
    weapon rides with the chest (strip b = strip a). The table's 2ND FIST is ON the butt -> tip line (checked <= 1.5
    px): draw the shaft as one straight line through BOTH fists - never kink it at the second hand.
  - ANGLE: the run carries the sword at about 69 deg on screen, swaying 68-70 deg with the chest and changing at most
    1.4 deg between neighbouring frames, as in the table - +9 deg from the idle's ~60 (within ~15). Keep the idle's
    weapon as drawn (same length, shape, straight shaft), turned as one piece about the holding fist by that little -
    following the table frame by frame (a smooth sway, never a jump). Measured at this carry: the whole figure, weapon
    included, stays >= 11 px inside the slot band x 32..351 (the check needs >= 8).
  - WRIST RANGE (owner rule; EVERY hand on the weapon, a two-handed grip's second hand too): every held weapon's GRIP
    AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:84 R2:82 R3:83 R4:82 R5:81 R6:81 R7:83 R8:85; the second (far) hand, against its own forearm: R1:69 R2:70 R3:65 R4:67 R5:72 R6:72 R7:66 R8:64 deg).
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
  - Lean forward (hip to neck): R1 12.1, R2 7.4, R3 16.6, R4 18.1, R5 10.9, R6 6.8, R7 16.6, R8 19.5 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=466/470/466/464 in R1 R2 R3 R4 (the same in R5 R6 R7 R8): R1 +0, R2 +4, R3 +0, R4 -2 px from R1 (+ = lower) - move your head top by the same amounts (bob 6 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - BELT per frame (y on the canvas = the centre of the mannequin's BROWN BAND at the waist - NOT the yellow hip dot,
    which sits ~21 px lower in the pelvis): R1 670 / R2 676 / R3 667 / R4 664 / R5 670 / R6 676 / R7 667 / R8 664.
    Paint the belt (and the waist line of a coat / armour) centred on these rows.
  - hair top -> belt = the idle's span (207 px); do not squash or stretch the body or head.
    In this guide the HEAD top -> BELT rows are 200-206 px apart (the leaning trunk is a little shorter on screen than
    standing): move the whole head-and-chest block as ONE piece to the Height and BELT rows of each frame.
  - Stride: one step = 275 source px = 45.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 45.5 game px = the light class stride: the fitted legs are within 5% of the class mannequin's (leg factor 1.014), so the class stride is kept. The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 68.8 px per frame (the mannequin: 68.7-68.8 px; tolerance 3 px) - the engine moves the unit
    11.4 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=284 -> R2 x=215 -> R3 x=146
      far foot: R5 x=296 -> R6 x=227 -> R7 x=158
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      R1: feet x 105 .. 284 (hip column 192; near toe 284, far toe 73), far 117 px up
      R2: feet x 120 .. 215 (hip column 192; near toe 215, far toe 99), far 114 px up
      R3: feet x 87 .. 233 (hip column 192; near toe 146, far toe 233), far 49 px up
      R4: feet x 63 .. 338 (hip column 192; near toe 47, far toe 338), near 63 px up, far 31 px up
      R5: feet x 92 .. 296 (hip column 192; near toe 61, far toe 296), near 117 px up
      R6: feet x 107 .. 227 (hip column 192; near toe 87, far toe 227), near 114 px up
      R7: feet x 99 .. 220 (hip column 192; near toe 220, far toe 158), near 49 px up
      R8: feet x 78 .. 324 (hip column 192; near toe 324, far toe 61), near 31 px up, far 63 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      R1: butt (223,684) fist (234,654) 2nd fist (246,625) tip (324,422)  angle 69 deg  butt->tip 281 px
      R2: butt (216,688) fist (227,659) 2nd fist (238,629) tip (314,425)  angle 70 deg  butt->tip 281 px
      R3: butt (229,683) fist (241,653) 2nd fist (253,624) tip (333,422)  angle 68 deg  butt->tip 281 px
      R4: butt (231,680) fist (243,651) 2nd fist (255,621) tip (336,420)  angle 68 deg  butt->tip 281 px
      R5: butt (221,684) fist (232,655) 2nd fist (244,625) tip (322,422)  angle 69 deg  butt->tip 281 px
      R6: butt (215,689) fist (226,659) 2nd fist (237,629) tip (313,426)  angle 70 deg  butt->tip 281 px
      R7: butt (229,683) fist (241,653) 2nd fist (253,624) tip (333,422)  angle 68 deg  butt->tip 281 px
      R8: butt (233,680) fist (245,650) 2nd fist (257,621) tip (339,420)  angle 68 deg  butt->tip 281 px
    FIST -> TIP = 249 px in every frame (the holding fist's centre to the weapon's tip; the same piece every frame):
    keep that length - never lengthen the shaft to reach the tip row nor shorten it; move the fist WITH the weapon.

PERSONALITY (this character's own run):
  - A massive arena champion's charge: clearly MORE UPRIGHT than the light mannequin (12 deg less lean: the upright greatsword stands clear in front of his face; chest proud, chin tucked so he glares ahead from under the brows), and the weight sinks HARD into the catch frames (hips 7 px lower in R2/R6, 2-3 px in contact/push, none in flight) - heavy landings, then he drives up again. The mannequin already has it - follow it.
  - Big rolling hips (pelvis twist 11 deg against the class's 7) under a steadier chest (counter-turn 4 against 6): the trunk swings around the legs, the greatsword stays put.
  - High knee drive like a stomping bull: the swinging knee comes up higher in the push-off and flight frames (R3/R7, R4/R8).
  - The greatsword is held UPRIGHT before him in BOTH hands - near fist low on the grip in front of the belly, far fist right under the gold guard - like a champion walking into the arena. The blade is LOCKED to the chest at about 69 deg on screen (the idle's ~60 stood up only ~9 deg, the least the slot band needs for the full blade), the same angle and full length in every frame - it rides the body, it does not bob or tip. Never swung, never laid on the shoulder (that is Baren's carry).
  - The short red shoulder cape, the fur-collar tufts, the ragged red hip panels and the long dreadlocked mane lag the body by one frame: they lift in the flight frames (R4/R8) and drop heavily in the catch frames (R2/R6). The gold champion belt stays fixed on the waist.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 69 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=464-470 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_grom_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_grom_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/hero/grom --gait run --src art/inbox/gait/sheet_hero_grom_run_a.png art/inbox/gait/sheet_hero_grom_run_b.png --pose art/requests/gait/run__hero_grom/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_hero_grom_preview_x4.png and sheet_hero_grom_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_grom_run - 그롬 — 피의 투기장 챔피언 (투기장 패왕) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_hero_grom.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_grom_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
