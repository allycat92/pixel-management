# 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) 이동 (3D 마네킹) · `sheet/hero/kai` → `gait/sheet_hero_kai_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/kai --guides 3d` 로 만듦; 3D 마네킹 시범).** Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → Antigravity 가 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `kai`)이 경량(light) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 80ms 박자로 넘긴다 (뜬 칸 포함). 보폭·박자·디딘 발 규칙은 경량 부류 그대로다 (엔진의 runCells).

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
- 무기: 지팡이 (먼 손) — 아래팔에 대한 손목 각도 0~120도 안 (가이드: R1:87 R2:83 R3:98 R4:107 R5:99 R6:93 R7:100 R8:100).
- 디딘 발: 한 걸음 원본 275px(게임 45.5px) → 디딘 발은 칸마다 **정확히 68.8px**(±3, 게임 11.4px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_kai_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/run__hero_kai/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 **실제 크기·모양**으로 그 선을 따라 그린다 (가이드의 길이는 자리 표시).
- **손목 범위**: 무기 방향은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

- 가볍고 조용한, 상체를 세운 정찰병의 달리기 — 바렌의 낮게 웅크린 달리기와 반대: 경량 마네킹보다 상체가 2~3도 더 서 있고 엉덩이가 약 3px 높다(3D 마네킹에 이미 들어 있다 — 따라 그린다). 머리는 수평으로 흔들림 없이, 눈은 앞길을 살핀다.
- 탄력 있고 소리 없는 발, 길고 편한 보폭: 지나가는 프레임과 공중 프레임에서 뒤쪽 발뒤꿈치가 조금 더 높이 차 올라가고, 엉덩이가 조금 더 돌며(골반 비틀기), 가슴은 차분하다 — 힘껏 펌프질하지 않고 미끄러지듯.
- 활은 먼 손(왼손)에 대기 그림의 손잡이 그대로 똑바로 세워 든다. 팔꿈치를 약 90도 굽혀 배·가슴 앞에 가까이: 위 활끝은 위로 약간 앞으로, 아래 활끝은 아래로 약간 뒤로, 시위는 몸 쪽, 화살은 걸지 않는다. 가이드의 청록 지팡이 모양 윤곽은 활의 끝-끝 선일 뿐이다(3D 리그에 활 모양이 없다; 둥근 머리 = 위 활끝): 그 선을 따라 은빛 리커브 활대, 감은 손잡이, 가는 시위를 대기 그림 크기로 그린다(손잡이에서 위 끝 약 125px, 아래 끝 약 130px). 팔과 함께 몇 px 만 흔들린다.
- 가까운 손(오른손)은 비어 있다: 느슨하게 반쯤 편 손이 다리와 반대로 앞뒤로 흔들리며 한 프레임 늦게 따라간다 — 꽉 쥔 주먹이 아니다.
- 화살통은 등에 고정(흰 깃이 먼 어깨 위로). 녹색 리본 아래의 긴 금발, 녹색 어깨 망토의 뒷자락, 무릎까지 오는 튜닉 뒷자락은 뒤로 날리며 한 프레임 늦다: 공중 프레임(R4/R8)에서 가장 높이 뜨고, 받는 프레임(R2/R6)에서 가라앉는다.

## 요약 (한국어)

카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자)의 경량 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_kai_run_a.png`·`art/inbox/gait/sheet_hero_kai_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 카이(숲을 떠난 엘프 정찰병): 뾰족한 엘프 귀, 뒤통수 귀 높이에서 짙은 녹색 리본으로 묶은 긴 물결 금발(풀린 머리는 등 뒤로 허리띠쯤까지, 볼 옆에 짧은 앞머리 몇 가닥), 녹색 눈과 차분하고 단호한 얼굴, 크림색 테두리와 둥근 잎 브로치가 달린 팔꿈치 길이의 짙은 녹색 어깨 망토, 금색 잎 자수와 크림색 단의 짙은 녹색 트임 튜닉(다리 사이 크림 테두리 앞자락, 무릎까지 오는 뒷자락), 갈색 가죽 팔보호대·허리띠·네모 버클 가슴끈, 갈색 바지, 접힌 단의 갈색 장화, 은회색 짧은 리커브 활 한 자루(검게 감은 손잡이, 금색 띠, 가는 흰 시위), 흰 깃 화살이 든 갈색 화살통(등). 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 68.8px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for Antigravity

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
    it. Paint the character's OWN weapon at its idle size and shape along that line (the ghost only marks the line).
  - WRIST RANGE (owner rule): every held weapon points 0-120 deg UPWARD (thumb side) from the forearm line
    (elbow -> wrist); 0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the
    arm line (no dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (R1:87 R2:83 R3:98 R4:107 R5:99 R6:93 R7:100 R8:100 deg).
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
  - Lean forward (hip to neck): R1 21.2, R2 16.4, R3 25.5, R4 27.8, R5 19.4, R6 15.4, R7 25.5, R8 29.5 deg.
  - Height: the mannequin's head top is at y=470/468/473/475 in R1 R2 R3 R4 and 470/468/473/476 in R5 R6 R7 R8: R1 +0, R2 -2, R3 +3, R4 +5 px from R1 (+ = lower) - move your head top by the same amounts (bob 8 px).
  - Stride: one step = 275 source px = 45.5 game px; 8 frames = two steps, 80 ms a frame in the game.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 68.8 px per frame (the mannequin: 68.7-68.8 px; tolerance 3 px) - the engine moves the unit
    11.4 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: R1 x=284 -> R2 x=215 -> R3 x=146
      far foot: R5 x=296 -> R6 x=227 -> R7 x=159
      (R4 / R8: flight - no foot on the floor; the next contact lands ahead again)

PERSONALITY (this character's own run):
  - A light, quiet, UPRIGHT scout's run - the opposite of Baren's low prowl: the torso 2-3 deg more upright than the light class mannequin and the hips ~3 px higher (the mannequin already has both - follow it). The head stays level and still, eyes scanning the road ahead.
  - Springy, near-silent feet with long easy strides: the trailing heel kicks up a little higher behind in the passing and flight frames, the hips swing a touch more (pelvis twist), the chest stays calm - gliding, not hard pumping.
  - The BOW rides UPRIGHT in the FAR (left) hand at the idle grip, held close in front of the belly/chest with the elbow bent about 90 deg: upper limb tip up and slightly forward, lower limb tip down and a little back, the string toward the body, no arrow nocked. The teal staff-like ghost on the guide is ONLY the bow's tip-to-tip line (the 3D rig has no bow shape; its round head = the upper limb tip): paint the silver recurve limbs, the wrapped grip and the thin string along it at the idle size (~125 px grip to upper tip, ~130 px to lower tip). It sways only a few px with the arm.
  - The near (right) hand is free: a loose, half-open hand that swings forward and back with the legs, one frame behind them - relaxed, not a tight fist.
  - The quiver stays fixed on the back (white fletchings over the far shoulder). The long blond hair below the green ribbon, the rear edge of the green shoulder cloak and the knee-length rear tunic flap trail back one frame late: highest in the flight frames (R4/R8), settling in the catch frames (R2/R6).
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit - change a weapon's angle (inside the wrist range) instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, weapon, cloth) at or above y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 66 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its head top near y=468-476.
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
  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
