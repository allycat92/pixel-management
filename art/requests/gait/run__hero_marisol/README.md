# 마리솔 — 닻을 잃은 해적 선장 (해적 선장) 이동 (3D 마네킹) · `sheet/hero/marisol` → `gait/sheet_hero_marisol_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/marisol --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `marisol`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 박자·디딘 발 규칙은 경량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 R1~R4 / R5~R8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `guide_run_plain_a.png` / `guide_run_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_run.gif` / `preview_run_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 80ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_marisol/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_marisol.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **경량** — pirate captain: split navy coat, trousers and tall boots, with a carried bow and holstered pistol. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_marisol_run_a.png` (R1~R4) + `art/inbox/gait/sheet_hero_marisol_run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_marisol_run - 마리솔 — 닻을 잃은 해적 선장 (해적 선장) 이동」 + 「## 판정 — gait/sheet_hero_marisol_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 활 (먼 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 (가이드: R1:72 R2:68 R3:81 R4:86 R5:78 R6:73 R7:82 R8:82).
- 보폭: 한 걸음 게임 45.5px = 경량 부류 보폭 그대로 — 맞춘 다리가 부류 마네킹과 5% 안(다리 비율 1.025)이라 다리 비율 규칙을 쓰지 않는다. 박자(80ms)도 부류 그대로.
- 디딘 발: 한 걸음 원본 275px(게임 45.5px) → 디딘 발은 칸마다 **정확히 68.8px**(±3, 게임 11.4px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_marisol_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__hero_marisol/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 모양으로, 청록 모양의 **선 위에 그 길이·각도 그대로** 그린다 (프롬프트의 WEAPON 표: 프레임마다 밑동·주먹·끝 좌표).
  - 활 = 휜 활대 둘(손잡이에서 위·아래 활끝으로, 끝으로 갈수록 시위 쪽으로 휜다)과 활끝을 잇는 가는 시위 선. 한 손으로 손잡이를 쥔다. 손목 규칙은 손잡이에서 위 활끝 쪽으로 가는 활대 방향(손잡이 축)에 잰다.
- **무기는 하나의 단단한 물체다.** 모든 프레임에서 길이·모양이 같다(아래 표: 밑동→끝, 주먹→끝). 곧은 자루·칼날은 밑동부터 끝까지 **한 직선** — 자로 그어 확인하고 절대 휘지 않는다. 어떤 선에 맞추려고 줄이거나 구부리거나 늘이지 않는다. 프레임마다 표의 밑동·주먹·끝 좌표(±4px)에 놓고, 각도는 대기와 달라도 표의 값. 무기 끝은 머리보다 위로 가도 된다 — 「높이」 숫자는 머리(머리카락·투구·모자) 꼭대기일 뿐, 프레임의 맨 윗점이 아니다. 이웃 프레임 사이 무기 각도는 3도(양손 무기 1.5도) 이하, 끝은 표의 매끈한 길을 따른다 — 앞뒤로 떨지 않는다. 양손 무기는 두 주먹이 매 프레임 손잡이의 같은 자리에 있고, 무기는 가슴을 따라 움직인다(b 띠 = a 띠).
- 단계: R1 닿기 - R2 받기(엉덩이 가장 낮음) - R3 밀기(뒤꿈치 듦) - R4 공중(두 발 모두 뜸). R5~R8 은 먼 발로 같은 동작.
- **높이**: 아래 「Height」 숫자는 **머리 꼭대기**(머리카락·투구·모자)일 뿐 — 무기 끝·지팡이 머리·깃털은 그보다 위로 가도 된다.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 당당한 해적 선장의 갑판 달리기: 가슴을 펴고 3~4도 더 곧게, 엉덩이를 좌우로 크게 흔들며(10도) 턱을 든다. 공중에서 뒤꿈치가 높이 튀고, 활은 가슴 앞에 똑바로, 빈 손은 크게 휘젓는다.

- 선장의 당당한 갑판 달리기: 가슴을 펴고 보는 쪽으로 열며, 경량 마네킹보다 3~4도 더 곧게 서고 엉덩이는 1~2px 높다(통통 튀는 느낌, 웅크리지 않는다 — 바렌의 낮은 검객 달리기와 반대. 3D 마네킹에 이미 들어 있다 — 따라 그린다). 엉덩이가 좌우로 더 크게 돌고(골반 비틀림 7도 대신 10도) 가슴이 반대로 받는다: 자신 있게 흔들리는 걸음, 턱은 든다.
- 공중 프레임(R4/R8)에서 뒤쪽 장화 뒤꿈치가 높이 튀어 오른다(뒷무릎이 부류보다 약 10도 더 접힘): 가볍고 탄력 있는 발걸음.
- 활은 8프레임 내내 먼 손에 가슴 앞에서 똑바로 세워 든다. 위쪽 금색 끝은 수직보다 조금 앞, 시위는 몸 쪽에서 끝에서 끝까지 곧게(당기지 않고 화살 없음). 몸과 함께 몇 px 만 흔들릴 뿐 몽둥이처럼 휘두르지 않는다. 가이드의 청록 반투명 활(휜 활대, 가는 시위)이 자리를 보여 준다: 앞쪽으로 휜 크림색 활대를 대기처럼 주먹에서 위 활대 약 145px, 아래 활대 약 137px 로 그린다.
- 빈 가까운 손은 느슨한 장갑 주먹으로 크게 여유 있게 흔든다(부류보다 조금 크게, 한 프레임 늦게) — R4/R8 에서 가슴 높이로 활 손 앞을 지나간다(그 위에 그린다).
- 크림색 깃털, 등 뒤로 늘어진 긴 곱슬 검은 머리, 모자 아래 빨간 리본, 찢어진 뒤 코트 자락은 뒤로 날리며 몸보다 한 프레임 늦다: 공중 프레임(R4/R8)에서 가장 높이 뜨고, 받는 프레임(R2/R6)에서 가라앉는다. 삼각모는 벗겨지지 않고 수평을 유지한다.

## 요약 (한국어)

마리솔 — 닻을 잃은 해적 선장 (해적 선장)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_marisol_run_a.png`·`art/inbox/gait/sheet_hero_marisol_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 마리솔: 빨간 테두리·금색 해골 휘장·큰 크림색 깃털이 달린 남색 삼각모, 모자 아래 뒤통수에 묶은 빨간 리본; 등 뒤로 내려오는 긴 짙은 갈색 곱슬머리와 먼 쪽 턱 앞에 늘어진 머리 한 가닥; 따뜻한 갈색 피부, 가까운 뺨의 금색 고리 귀걸이와 가는 흉터(가리지 않는다); 진홍 테두리·소매, 놋쇠 단추, 찢어진 밑단과 긴 뒤 자락이 있는 긴 남색 코트(앞자락은 허리에서 갈라짐); 흰 셔츠와 금 펜던트, 갈색 가슴띠와 놋쇠 버클 허리띠; 가까운 허리 권총집에 꽂힌 플린트락 권총(뽑거나 쏘지 않는다); 등에 맨 흰 깃 화살 화살통; 짙은 남색 바지; 버클 달린 갈색 긴 장화; 갈색 장갑; 리커브 활 한 자루(크림색 활대, 빨강·금색 감은 손잡이, 양끝 금색 둥근 끝, 가는 밝은 시위) — 달릴 때 화살은 걸지 않는다; 자신 있고 집중한 얼굴. 개성 — 당당한 해적 선장의 갑판 달리기: 가슴을 펴고 3~4도 더 곧게, 엉덩이를 좌우로 크게 흔들며(10도) 턱을 든다. 공중에서 뒤꿈치가 높이 튀고, 활은 가슴 앞에 똑바로, 빈 손은 크게 휘젓는다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 68.8px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames, movement class LIGHT) of 마리솔 — 닻을 잃은 해적 선장 (해적 선장) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_marisol_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_hero_marisol_run_b.png  = frames R5 R6 R7 R8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/run__hero_marisol/guide_run_a.png, guide_run_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__hero_marisol/guide_run_plain_a.png, guide_run_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/run__hero_marisol/size_run_a.png, size_run_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/run__hero_marisol/preview_run.gif, preview_run_game_x4.gif = the motion at speed (80 ms a frame).
  - art/inbox/sheet_hero_marisol.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_marisol/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/run__hero_marisol/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Marisol (마리솔), the pirate captain who lost her anchor, exactly as on the accepted sheet: a navy TRICORN hat with red trim, a gold skull-and-crossbones badge and a big cream plume, a red ribbon tied at the back of the head under the hat; long dark-brown wavy hair down the back, one loose lock hanging in front of the jaw on the far side; warm brown skin, a gold hoop earring and a thin scar on the near cheek (kept bare); a long NAVY coat with crimson trim and cuffs, brass buttons, a torn ragged hem and long rear coat tails, front coat panels open at the hips; white shirt with a gold pendant, a brown cross-belt and belt with a brass buckle; a FLINTLOCK pistol holstered on the near hip (never drawn or fired); a QUIVER of white-fletched arrows strapped on the back; dark navy trousers; tall brown buckled boots; brown gloves; ONE recurve bow (cream limbs, red-and-gold wrapped grip, gold knobs at both tips, a thin pale string) - no arrow nocked in the run; confident, focused expression.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's own weapon (the idle's shape) ON THAT LINE at the table's length and angle (WEAPON below):
    BOW = two curved limbs (from the grip to each tip, curling back toward the string near the tips) and a thin string line tip to tip; ONE hand on the grip. The wrist rule is measured on the stave at the grip, toward the upper tip.
  - WEAPON = ONE RIGID OBJECT. In every frame it has the same length and shape (the table: butt -> tip, fist -> tip). A
    straight shaft or blade is ONE straight line from butt to tip - check it with a ruler line, never curve it. Never
    shorten, bend or stretch it to reach a point or to stay under a line. Place it by the table's BUTT, FIST(S) and TIP
    for each frame (+-4 px); its angle is the table's even where it differs from the idle. The tip MAY be above the
    head and is NOT limited by the Height numbers - those are the top of the HEAD (hair / helmet / hat) only. Between
    neighbouring frames the weapon turns at most 3 deg (two-handed: 1.5) and its tip follows the smooth path of the
    table - no back-and-forth. Two-handed: both fists stay at the same places on the grip in every frame, and the weapon
    rides with the chest (strip b = strip a).
  - WRIST RANGE (owner rule): every held weapon's GRIP AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:72 R2:68 R3:81 R4:86 R5:78 R6:73 R7:82 R8:82 deg).
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
  - Lean forward (hip to neck): R1 20, R2 16.3, R3 24.5, R4 25.9, R5 18.4, R6 15.4, R7 24.5, R8 27.3 deg.
  - Height: the HEAD top (hair / helmet / hat - NOT the weapon) is at y=449/449/452/453 in R1 R2 R3 R4 and 449/448/452/453 in R5 R6 R7 R8: R1 +0, R2 +0, R3 +3, R4 +4 px from R1 (+ = lower) - move your head top by the same amounts (bob 5 px). A
    weapon tip, staff head, plume or raised cloth may go HIGHER than these rows - they never limit it.
  - Stride: one step = 275 source px = 45.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - Stride rule: 45.5 game px = the light class stride: the fitted legs are within 5% of the class mannequin's (leg factor 1.025), so the class stride is kept. The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 68.8 px per frame (the mannequin: 68.7-68.8 px; tolerance 3 px) - the engine moves the unit
    11.4 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=284 -> R2 x=215 -> R3 x=146
      far foot: R5 x=296 -> R6 x=228 -> R7 x=159
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)
  - FEET per frame (x in the 384-px slot: rear-most heel .. front-most toe; keep both within ~20 px of these):
      R1: feet x 113 .. 284 (hip column 192; near toe 284, far toe 78), far 141 px up
      R2: feet x 119 .. 215 (hip column 192; near toe 215, far toe 98), far 122 px up
      R3: feet x 84 .. 228 (hip column 192; near toe 146, far toe 228), far 47 px up
      R4: feet x 62 .. 332 (hip column 192; near toe 44, far toe 332), near 64 px up, far 27 px up
      R5: feet x 100 .. 296 (hip column 192; near toe 65, far toe 296), near 141 px up
      R6: feet x 106 .. 228 (hip column 192; near toe 85, far toe 228), near 122 px up
      R7: feet x 97 .. 215 (hip column 192; near toe 215, far toe 159), near 47 px up
      R8: feet x 77 .. 316 (hip column 192; near toe 316, far toe 59), near 27 px up, far 64 px up
  - WEAPON per frame (x in the 384-px slot, y on the canvas; the same butt->tip length in every frame - one straight
    rigid piece; tip above the head is fine):
      R1: butt (280,765) fist (313,629) tip (289,484)  angle 88 deg  butt->tip 282 px
      R2: butt (274,760) fist (309,624) tip (286,478)  angle 88 deg  butt->tip 282 px
      R3: butt (271,773) fist (310,639) tip (292,492)  angle 86 deg  butt->tip 282 px
      R4: butt (260,774) fist (304,642) tip (292,494)  angle 83 deg  butt->tip 282 px
      R5: butt (251,764) fist (297,632) tip (288,485)  angle 82 deg  butt->tip 282 px
      R6: butt (252,761) fist (298,629) tip (288,481)  angle 83 deg  butt->tip 282 px
      R7: butt (268,774) fist (309,640) tip (294,493)  angle 85 deg  butt->tip 282 px
      R8: butt (279,778) fist (315,643) tip (295,497)  angle 87 deg  butt->tip 282 px

PERSONALITY (this character's own run):
  - A captain's swaggering deck-runner's run: chest up and open to the viewer, 3-4 deg MORE UPRIGHT than the light class mannequin and the hips 1-2 px higher (springy, never crouched - the opposite of Baren's low swordsman's run; the mannequin already has it - follow it). The hips roll more from side to side (pelvis twist 10 deg instead of 7) and the chest counters them: a confident sway, chin up.
  - The trailing boot heel flicks up high behind in the flight frames (R4/R8: the rear knee folded ~10 deg more than the class): a light, bouncy step.
  - The bow stays UPRIGHT in the far hand in front of the chest in all 8 frames, the upper gold knob a little forward of vertical, the string on the body side, straight from knob to knob (nothing drawn, no arrow). It only rides with the body and bobs a few px - it never swings like a club. The teal see-through bow on the guide (curved limbs, thin string) marks its place: paint the cream limbs bulging forward, upper limb about 145 px and lower limb about 137 px from the fist as in the idle.
  - The free near hand is a loose gloved fist with a BIG relaxed swing (a little larger than the class, one frame late) - it crosses in front of the bow hand at chest height in R4/R8 (drawn over it).
  - The cream plume, the long wavy dark hair down the back, the red ribbon under the hat and the torn rear coat tails stream back and lag the body by one frame: they lift most in the flight frames (R4/R8), settle in the catch frames (R2/R6). The tricorn stays on and level.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit, and the weapon is never shortened or bent to fit - it follows the WEAPON table.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 73 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its HEAD top near y=448-453 (a weapon may reach higher).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_marisol_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_marisol_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/hero/marisol --gait run --src art/inbox/gait/sheet_hero_marisol_run_a.png art/inbox/gait/sheet_hero_marisol_run_b.png --pose art/requests/gait/run__hero_marisol/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). The third must end without an error and write
<temp dir>/sheet_hero_marisol_preview_x4.png and sheet_hero_marisol_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_marisol_run - 마리솔 — 닻을 잃은 해적 선장 (해적 선장) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, guide_run_plain_a/b, size_run_a/b, preview_run.gif, sheet_hero_marisol.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_marisol_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
