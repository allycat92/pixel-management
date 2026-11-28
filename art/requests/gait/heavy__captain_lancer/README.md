# 로드릭 — 말을 잃은 기사 (창기병) 이동 (3D 마네킹) · `sheet/captain/lancer` → `gait/sheet_captain_lancer_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/captain/lancer --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `lancer`)이 중량(heavy) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 101ms 박자로 넘긴다. 박자·디딘 발 규칙은 중량 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_heavy_a.png` / `guide_heavy_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 H1~H4 / H5~H8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870 |
| `guide_heavy_plain_a.png` / `guide_heavy_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_heavy_a.png` / `size_heavy_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 H1/H5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_heavy.gif` / `preview_heavy_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 101ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/captain_lancer/concept.png` | 디자인 초안 — 디자인만 |
| `art/requests/phase3/captain_lancer/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_captain_lancer.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **중량** — polished blue plate armour, steel greaves and sabatons, ornate plumed helmet, surcoat, infantry lance. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_captain_lancer_run_a.png` (H1~H4) + `art/inbox/gait/sheet_captain_lancer_run_b.png` (H5~H8) + `art/inbox/NOTES.md` 절 「gait/sheet_captain_lancer_run - 로드릭 — 말을 잃은 기사 (창기병) 이동」 + 「## 판정 — gait/sheet_captain_lancer_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 창 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 (가이드: H1:82 H2:82 H3:79 H4:76 H5:73 H6:74 H7:77 H8:81).
- 보폭: 한 걸음 게임 26.5px = 중량 부류 보폭 23.57px × 다리 비율 1.123 — 맞춘 마네킹의 다리(허벅지+정강이+발목)가 부류 마네킹보다 +12% 길어, 같은 관절 각도·같은 무릎 굽힘으로 디디면 한 걸음이 그만큼 길다(다리 비율 규칙: 5% 넘게 다르면 보폭이 다리를 따른다; 그대로 부류 보폭을 쓰면 무릎이 펴지거나 발이 덜 나간다). 엔진(js/battle.js runCells)은 시트마다 그 시트의 runStride/4 씩 디딘 칸을 넘기므로 디딘 발은 미끄러지지 않는다. 유닛의 빠르기는 그대로(같은 거리에서 걸음 수만 조금 적다), 박자(101ms)는 부류 그대로.
- 디딘 발: 한 걸음 원본 160.05px(게임 26.5px) → 디딘 발은 칸마다 **정확히 40.0px**(±3, 게임 6.6px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_lancer_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/heavy__captain_lancer/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 **실제 크기·모양**으로 그 자리를 따라 그린다 (가이드의 모양은 자리 표시).
  - 창 = 긴 자루와 끝의 잎 모양 강철 창끝. 두 손으로 쥘 수 있다(두 손이 같은 자루 위).
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 말을 잃고도 돌격을 이끄는 기사: 중량 부류보다 꼿꼿하게(기울기 약 3도) 턱을 들고, 디딜 때마다 판금 무게로 푹 가라앉았다 천천히 올라온다(출렁임 약 11px). 골반·어깨는 네모나게 거의 안 돌고(3/1.5), 창은 두 손으로 비껴 세워 창끝만 한 박자 늦게 끄덕인다.

- 말을 잃었어도 아직 돌격을 이끄는 듯 걷는 기사: 자부심 있게 꼿꼿한 중량 걸음 — 중량 마네킹보다 1~2도 덜 기울고, 가슴은 보는 쪽으로 열려(사자 문장이 보이게) 턱을 들고 시선은 앞을 본다(3D 마네킹에 이미 들어 있다 — 따라 그린다).
- 발을 디딜 때마다 판금 무게가 실린다: 내려앉는 프레임(H2/H6)이 부류 마네킹보다 약 3px 더 낮고, 천천히 다시 올라온다 — 묵직하고 신중한 박자, 통통 튀지 않는다.
- 랜스는 내내 두 손으로 비껴 든다(가까운 손은 허리띠, 먼 손은 가슴 옆 자루 위쪽). 대기보다 더 세워 들어 랜스 길이 그대로 칸에 들어가게 한다. 창끝은 앞-위를 향하고 발 디딤마다 한 프레임 늦게 몇 px 끄덕인다 — 휘두르지 않고, 바닥 쪽으로 처지지 않는다.
- 두 손이 한 자루를 잡고 있어 엉덩이·어깨 비틀림은 부류 마네킹보다 작다. 파란 깃털, 파란 창 깃발, 해진 붉은 망토와 겉옷 자락은 한 프레임 늦게 절제된 흔들림으로 따라오고, 내려앉는 프레임에서 가라앉는다.

## 요약 (한국어)

로드릭 — 말을 잃은 기사 (창기병)의 중량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_captain_lancer_run_a.png`·`art/inbox/gait/sheet_captain_lancer_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 로드릭(말을 잃은 기사): 창살 바이저를 위로 올려 얼굴이 다 보이는 황동빛 투구와 뒤쪽의 짙은 파란 깃털, 턱까지 오는 짧은 적갈색 머리, 수염 자국, 코와 뺨을 가로지르는 흉터, 단호한 눈매; 금테와 둥근 리벳의 광택 나는 파란 판금(둥근 큰 어깨갑·팔갑·허리갑); 가슴에 단순한 파란 사자 문장이 있는 낡은 흰(미색) 겉옷과 무릎까지 오는 앞자락; 은색 버클의 갈색 가죽 허리띠; 뒤로 짧게 늘어진 해진 짙은 붉은 망토; 짙은 파란 바지; 강철 무릎갑·정강이갑·철신; 갈색 가죽 장갑. 보병 랜스 한 자루: 평범한 갈색 나무 자루, 가는 잎 모양 강철 창끝, 창끝 바로 아래 꼬리 둘 달린 작은 파란 깃발, 대기 그림과 같은 길이(원본 약 357px) — 원뿔 마상창·손 보호대 없음. 개성 — 말을 잃고도 돌격을 이끄는 기사: 중량 부류보다 꼿꼿하게(기울기 약 3도) 턱을 들고, 디딜 때마다 판금 무게로 푹 가라앉았다 천천히 올라온다(출렁임 약 11px). 골반·어깨는 네모나게 거의 안 돌고(3/1.5), 창은 두 손으로 비껴 세워 창끝만 한 박자 늦게 끄덕인다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 40.0px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the HEAVY TRUDGE (fast, purposeful) CYCLE (8 frames, movement class HEAVY) of 로드릭 — 말을 잃은 기사 (창기병) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_lancer_run_a.png  = frames H1 H2 H3 H4
  art/inbox/gait/sheet_captain_lancer_run_b.png  = frames H5 H6 H7 H8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/heavy__captain_lancer/guide_heavy_a.png, guide_heavy_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/heavy__captain_lancer/guide_heavy_plain_a.png, guide_heavy_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/heavy__captain_lancer/size_heavy_a.png, size_heavy_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/heavy__captain_lancer/preview_heavy.gif, preview_heavy_game_x4.gif = the motion at speed (101 ms a frame).
  - art/inbox/sheet_captain_lancer.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/captain_lancer/concept.png = the design draft (design only - not proportions or rendering).
  - art/requests/phase3/captain_lancer/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/heavy__captain_lancer/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Roderick (로드릭), the knight who lost his horse, exactly as on the accepted sheet: a brass-tan great helm with a barred visor RAISED on top so the whole face shows, a dark-blue plume at the back; short red-brown hair to the jaw, stubble, a scar across the nose and cheek, stern determined eyes; polished blue plate (big rounded pauldrons, vambraces, tassets) with gold trim and round rivets; a worn off-white surcoat / tabard with a simple blue lion emblem on the chest and a long off-white front panel to the knees; a brown leather belt with a silver buckle; a short TATTERED dark-red cape behind; dark-blue trousers; steel knee cops, greaves and sabatons; brown leather gauntlets. ONE infantry lance: a plain brown wooden shaft, a slim leaf-shaped steel tip, a small blue two-tailed pennant just below the tip, as long as on the idle (~357 source px) - no jousting cone, no vamplate.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's OWN weapon at its idle size and shape in that place (the ghost only marks it):
    SPEAR = a long shaft with a leaf-shaped steel head at the end; both hands may hold the shaft.
  - WRIST RANGE (owner rule): every held weapon's GRIP AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (H1:82 H2:82 H3:79 H4:76 H5:73 H6:74 H7:77 H8:81 deg).
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
  - Lean forward (hip to neck): H1 2.9, H2 3.5, H3 3.3, H4 3.6, H5 2.8, H6 3.4, H7 3.3, H8 3.7 deg.
  - Height: the mannequin's head top is at y=441/452/445/442 in H1 H2 H3 H4 (the same in H5 H6 H7 H8): H1 +0, H2 +11, H3 +4, H4 +1 px from H1 (+ = lower) - move your head top by the same amounts (bob 11 px).
  - Stride: one step = 160.05 source px = 26.5 game px; 8 frames = two steps, 101 ms a frame in the game.
  - Stride rule: 26.5 game px = the heavy class stride 23.57 px x leg factor 1.123: this character's fitted legs are 12% longer than the class mannequin's, so the same joint angles and stance-knee bend give a longer step (legs more than 5% off -> the stride follows the legs). The engine advances each sheet by its OWN runStride/4 per planted cell, so the planted foot does not slide; the unit's ground speed is unchanged (a few fewer steps). The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 40.0 px per frame (the mannequin: 40.0-40.0 px; tolerance 3 px) - the engine moves the unit
    6.6 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: H1 x=279 -> H2 x=239 -> H3 x=199 -> H4 x=159  (-> H5 x=119 as the REAR foot, heel up, toe still on the floor)
      far foot: H5 x=292 -> H6 x=252 -> H7 x=212 -> H8 x=172  (-> H1 x=132 as the REAR foot, heel up, toe still on the floor)

PERSONALITY (this character's own run):
  - A dismounted knight who still marches as if leading a charge: a proud, UPRIGHT heavy trudge - 1-2 deg less lean than the heavy class mannequin, chest open to the viewer (the lion emblem shows), chin up, eyes fixed ahead (the mannequin already has it - follow it).
  - Each footfall settles into the plate: the down frames (H2/H6) sit ~3 px lower than the class mannequin, then he rises back slowly - a deliberate, weighty rhythm, never a bounce.
  - The lance is held at port in BOTH hands the whole time (near fist at the belt, far fist up the shaft by the chest), tilted more upright than the idle so the full-length lance fits the slot; the tip leads forward-up and nods a few px with each footfall, one frame late - it never swings, never drops toward the floor.
  - Hips and shoulders turn less than the class mannequin (both hands locked on one shaft). The blue plume, the blue pennant, the tattered red cape and the surcoat hem trail one frame late with restrained sway, settling in the down frames.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit - change a weapon's angle (inside the wrist range) instead.
COLOURS: take every colour from the accepted sheet (same palette, ~40 colours); the design colours were skin #f2c9a0; hair #5a3720; outfit #3d5a9c; accent #e8e4d8.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_heavy_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 69 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its head top near y=441-452.
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_lancer_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_lancer_run_b.png
  python3 tools/art/add_gait.py sheet/captain/lancer --gait run --src art/inbox/gait/sheet_captain_lancer_run_a.png art/inbox/gait/sheet_captain_lancer_run_b.png --pose art/requests/gait/heavy__captain_lancer/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS. The third must end without an error and write
<temp dir>/sheet_captain_lancer_preview_x4.png and sheet_captain_lancer_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_lancer_run - 로드릭 — 말을 잃은 기사 (창기병) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_heavy_a/b, guide_heavy_plain_a/b, size_heavy_a/b, preview_heavy.gif, sheet_captain_lancer.png, concept.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_captain_lancer_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
