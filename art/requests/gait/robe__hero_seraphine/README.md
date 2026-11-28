# 세라핀 — 파문당한 성녀 (파문 성녀) 이동 (3D 마네킹) · `sheet/hero/seraphine` → `gait/sheet_hero_seraphine_run`

**상태: 요청 (2026-11-28, 클라우드 — `python3 tools/art/gait_requests.py --write sheet/hero/seraphine --guides 3d` 로 만듦; 3D 마네킹 시범).** **그림: GPT** (주인 2026-11-28: 다시 바꾸라고 할 때까지 그림은 GPT — 이름은 `tools/mannequin3d/specs/carry3d.json` 의 `painter` 한 곳). GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜**: "가상의 3D 마네킹 → 동작 → 스프라이트 띠 → 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). 무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, 그림 판정은 주인이 직접 한다.
→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, `tools/mannequin3d/specs/carry3d.json` 의 `seraphine`)이 로브(robe) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 96ms 박자로 넘긴다. 박자·디딘 발 규칙은 로브 부류 그대로이고(엔진의 runCells), 보폭은 아래 「보폭」 줄대로.

| 파일 | 내용 |
|---|---|
| `guide_robe_a.png` / `guide_robe_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 G1~G4 / G5~G8. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870 |
| `guide_robe_plain_a.png` / `guide_robe_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |
| `size_robe_a.png` / `size_robe_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 G1/G5 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·디딘 발끝 자리(노란 눈금) |
| `preview_robe.gif` / `preview_robe_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, 96ms 박자 |
| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 0.1654, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |
| `art/requests/phase3/hero_seraphine/portrait.png` | 승인된 초상화 — 얼굴·머리·색 |
| `art/inbox/sheet_hero_seraphine.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |

- 부류: **로브** — torn white saint robes with an uneven hem and red sash; brown wrapped boots show beneath the hem. (tools/art/specs/gait_classes.json). 개성은 그 위에 얹는다 (아래 「개성」).
- 납품: art-inbox `art/inbox/gait/sheet_hero_seraphine_run_a.png` (G1~G4) + `art/inbox/gait/sheet_hero_seraphine_run_b.png` (G5~G8) + `art/inbox/NOTES.md` 절 「gait/sheet_hero_seraphine_run - 세라핀 — 파문당한 성녀 (파문 성녀) 이동」 + 「## 판정 — gait/sheet_hero_seraphine_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).
- 무기: 철퇴 (가까운 손) — 아래팔에 대한 손목(손잡이 축) 각도 0~120도 안 (가이드: G1:65 G2:64 G3:60 G4:56 G5:55 G6:56 G7:59 G8:62).
- 보폭: 한 걸음 게임 22.2px = 로브 부류 보폭 그대로 — 맞춘 다리가 부류 마네킹과 5% 안(다리 비율 1.037)이라 다리 비율 규칙을 쓰지 않는다. 박자(96ms)도 부류 그대로.
- 디딘 발: 한 걸음 원본 134.2px(게임 22.2px) → 디딘 발은 칸마다 **정확히 33.5px**(±3, 게임 5.5px) 뒤로 — 발끝 x 는 Prompt 의 PLANTED FOOT 표.
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_hero_seraphine_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` (`--pose art/requests/gait/robe__hero_seraphine/pose.json`). 그림이 좋은지는 주인이 직접 판정한다.

## 3D 가이드 읽는 법

- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.
- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 **실제 크기·모양**으로 그 자리를 따라 그린다 (가이드의 모양은 자리 표시).
  - 철퇴 = 자루와 둥근 머리.
- **손목 범위**: 무기의 손잡이 축(주먹에서 무기 끝 쪽; 활은 손잡이에서 위 활끝 쪽, 역수는 엄지 쪽)은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 0~120도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.
- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 (각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.
- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.
- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.

## 개성

**한 줄**: 다친 이에게 서둘러 가는 파문 성녀의 미끄러짐: 엉덩이를 3~5px 낮추고 고개를 숙이며, 골반만 돌고(6도) 윗몸은 조용하다(2). 철퇴는 허리 앞에서 흔들지 않고, 빈 손바닥을 낮게 내민다.

- 부드럽고 낮게 서두르는 미끄러짐 — 다친 사람에게 달려가는 수녀: 로브 부류 마네킹보다 엉덩이 3~5px 낮고(웅크린 대기처럼 무릎이 부드럽다) 약 1도 더 기울며, 고개는 조금 숙인다(슬픈 얼굴, 눈은 바로 앞길). 3D 마네킹에 이미 들어 있다 — 따라 그린다.
- 짧은 걸음마다 엉덩이가 더 돌아(골반 비틀기 6도, 부류 4도) 찢긴 치맛단이 좌우로 흔들리고, 가슴은 조용하다(반대 비틀기 2, 부류 3): 윗몸은 차분하고 치마가 움직인다. 지나가는 칸(G3/G7)에서는 드는 발이 조금 더 앞에 있어 두 장화가 단 아래로 읽힌다.
- 철퇴는 가까운(오른) 주먹으로 허리에 쥐고 대기처럼 자루를 앞 위로 든다. 몸과 함께 움직이며 몇 px 만 끄덕인다 — 휘두르지 않는다.
- 빈 먼(왼) 손은 대기처럼 손바닥을 아래로 편 채 허벅지 앞에 낮게 앞으로 내민다(누군가를 붙들거나 축복하듯): 거의 펴진 팔이 걸음에 맞춰 앞뒤로 살짝 흔들린다. 빛·주문 없음.
- 찢긴 베일 끝과 긴 웨이브 머리는 뒤로 날리며 한 프레임 늦다. 붉은 띠의 넓은 뒤 끝은 뒤 엉덩이 뒤에서 한 프레임 늦고, 좁은 끝은 다리 사이 가운데 앞에 남는다. 들쭉날쭉한 단 아래로 걸음마다 갈색 감은 장화가 보인다. 아무것도 y=870 에 닿지 않는다.

## 요약 (한국어)

세라핀 — 파문당한 성녀 (파문 성녀)의 로브 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `art/inbox/gait/sheet_hero_seraphine_run_a.png`·`art/inbox/gait/sheet_hero_seraphine_run_b.png` 두 띠로 art-inbox 에 올린다. 모습 — 승인된 시트 그대로의 세라핀(파문당한 성녀): 창백한 젊은 여인, 긴 웨이브 금발(앞머리 가닥은 얼굴 옆으로 옷깃까지), 너덜너덜한 끝과 작은 금 십자가 장식이 달린 찢긴 크림색 두건·베일, 구멍 나고 단이 들쭉날쭉한 겹겹의 찢긴 크림색 성녀 로브, 가슴의 작은 금 십자가들, 먼 어깨에서 허리 매듭으로 가슴을 가로지르는 붉은 띠(넓은 끝은 뒤 엉덩이 뒤, 좁은 끝은 가운데 앞으로 늘어짐), 단 아래 갈색 감은 장화, 가까운 오른손의 짧은 가시 철퇴 한 자루(금띠·금 자루 끝이 달린 짙은 자루, 회색 가시 머리), 슬프지만 다정한 얼굴. 후광·빛 없음. 개성 — 다친 이에게 서둘러 가는 파문 성녀의 미끄러짐: 엉덩이를 3~5px 낮추고 고개를 숙이며, 골반만 돌고(6도) 윗몸은 조용하다(2). 철퇴는 허리 앞에서 흔들지 않고, 빈 손바닥을 낮게 내민다. 명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 0~120도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 33.5px 뒤로 (발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.

## Prompt for GPT

```
TASK: draw the ROBE GLIDE (hurried, purposeful) CYCLE (8 frames, movement class ROBE) of 세라핀 — 파문당한 성녀 (파문 성녀) as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_hero_seraphine_run_a.png  = frames G1 G2 G3 G4
  art/inbox/gait/sheet_hero_seraphine_run_b.png  = frames G5 G6 G7 G8
(the file names say "run" for every movement class: the engine plays them as the sheet's run.)
PAINT the character OVER this folder's 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same
height, limb lengths and stance width) and already moves with this character's personality - copy its pose, depth and
placement; do not take the idle art and bend, shear or rotate it.

REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):
  - art/requests/gait/robe__hero_seraphine/guide_robe_a.png, guide_robe_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the
    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:
    1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/robe__hero_seraphine/guide_robe_plain_a.png, guide_robe_plain_b.png = the same frames without dots / rings / ground line: open
    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.
  - art/requests/gait/robe__hero_seraphine/size_robe_a.png, size_robe_b.png = the same frames with guide lines and planted-toe ticks, and on the left the
    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/requests/gait/robe__hero_seraphine/preview_robe.gif, preview_robe_game_x4.gif = the motion at speed (96 ms a frame).
  - art/inbox/sheet_hero_seraphine.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.
    Same character, same pixel size, same palette.
  - art/requests/phase3/hero_seraphine/portrait.png = the approved portrait (face, hair, colours only).
  - art/requests/gait/robe__hero_seraphine/pose.json = the coordinates of every joint per frame, the stride and the checks the guide passed.

CHARACTER (unchanged from the accepted sheet): Seraphine (세라핀), the excommunicated saint, exactly as on the accepted sheet: a pale young woman with long wavy blonde hair (front strands beside the face down to the collar); a torn cream hood / veil with ragged tails and a small gold cross clip; torn, layered cream saint robes with holes and a jagged uneven hem; small gold cross pendants on the chest; a RED sash crossing the chest from the far shoulder to a knot at the waist, with a broad tail behind the rear hip and a narrow end hanging at the centre front; brown wrapped boots under the hem; ONE short spiked mace (dark haft with gold bands and a gold pommel, grey spiked head) in the near right hand; sorrowful but kind face. No halo, no glow.

HOW TO READ THE 3D GUIDE:
  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far
    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.
    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.
  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers
    it. Paint the character's OWN weapon at its idle size and shape in that place (the ghost only marks it):
    MACE = haft and round head.
  - WRIST RANGE (owner rule): every held weapon's GRIP AXIS (fist -> weapon tip; a bow: grip -> upper tip; a reverse
    grip: the thumb side of the fist) points 0-120 deg UPWARD (thumb side) from the forearm line (elbow -> wrist);
    0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the arm line (no
    dangling blade) nor beyond 120 deg. The guide is inside the range in every frame (G1:65 G2:64 G3:60 G4:56 G5:55 G6:56 G7:59 G8:62 deg).
  - The mannequin's round head is a placeholder: paint the character's own head, hair and headgear at the idle's size on
    its neck. The joints, limbs and torso are fitted to the idle - put the character's own body exactly on them.
  - PAINT OVER EVERY MANNEQUIN PIXEL. add_gait.py refuses a strip in which >= 25% of a frame still has the mannequin's
    colours, and a recoloured mannequin (silhouette IoU > 0.93 with this guide). Clothing, hair, cloth and the real
    weapon change the silhouette - that is the work.
  - FLOOR: the standing sole on y=870; nothing of the body below it. A weapon tip or cloth that would dip below the
    floor line (or below y=852 in a flight frame) is touched up while painting - lift it a little.
  - Samples of other characters are only baselines. Do not recolour another character's strip.

THE MOVE (movement class robe: loose long cloth: running in it looks unnatural. Fastest natural gait = a hurried, purposeful glide (not a stroll): NO flight phase, NO big knee lift, a small forward lean, short quick steps; the hem swings and hides the knees, only the feet flick out at the hem. - with this character's personality on top, already in the mannequin):
  - G1 contact - G2 catch (lowest hips) - G3 push-off (heel up) - G4 push. G5-G8 = the same with the far foot.
  - Lean forward (hip to neck): G1 8, G2 8.5, G3 7.5, G4 6.9, G5 7.5, G6 8.1, G7 7.5, G8 7.2 deg.
  - Height: the mannequin's head top is at y=469/472/465/464 in G1 G2 G3 G4 (the same in G5 G6 G7 G8): G1 +0, G2 +3, G3 -4, G4 -5 px from G1 (+ = lower) - move your head top by the same amounts (bob 8 px).
  - Stride: one step = 134.2 source px = 22.2 game px; 8 frames = two steps, 96 ms a frame in the game.
  - Stride rule: 22.2 game px = the robe class stride: the fitted legs are within 5% of the class mannequin's (leg factor 1.037), so the class stride is kept. The cadence is the class's.
  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by
    exactly step/4 = 33.5 px per frame (the mannequin: 33.5-33.6 px; tolerance 3 px) - the engine moves the unit
    5.5 game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot
    = the yellow tick in size_*.png; x in the 384-px slot:
      near foot: G1 x=273 -> G2 x=240 -> G3 x=206 -> G4 x=172  (-> G5 x=139 as the REAR foot, heel up, toe still on the floor)
      far foot: G5 x=285 -> G6 x=251 -> G7 x=218 -> G8 x=184  (-> G1 x=151 as the REAR foot, heel up, toe still on the floor)

PERSONALITY (this character's own run):
  - A soft, low, hurried glide - a sister running to the wounded: hips 3-5 px lower than the robe class mannequin (softer knees, as in her crouched idle), about 1 deg more lean and the head bowed a little (sorrowful, eyes on the road just ahead). The mannequin already has all of it - follow it.
  - The hips turn more with each short step (pelvis twist 6 deg vs the class's 4) so the torn hem sways from side to side, while the chest stays quiet (counter-rotation 2 vs 3): the upper body is calm, the skirt does the moving. In the passing frames (G3/G7) the swing foot is carried a little further ahead so both boots read under the hem.
  - The mace stays in the near (right) fist at the waist, haft forward-up as in the idle, held steady: it rides with the body and nods only a few px - never swung.
  - The free far (left) hand is OPEN, palm down, low and forward in front of the thigh as in the idle (reaching ahead as if to steady someone or bless): an almost straight arm that swings gently fore-aft with the steps. No glow, no cast.
  - The ragged veil tails and the long wavy hair stream back and lag one frame; the broad rear tail of the red sash lags one frame behind the rear hip, the narrow sash end stays at the centre front between the legs; the jagged hem shows the brown boot wraps at each step. Nothing reaches y=870.
  - Face: exactly as in the idle in every frame.

MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The
body must not be shrunk to fit - change a weapon's angle (inside the wrist range) instead.

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_robe_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - EVERY frame: the lowest pixel of the figure is the standing sole on y=870 (no flight frame);
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross into the next slot, including weapons, cloth and hair);
  - the SCALE of the accepted sheet (0.1654 source -> game: the idle is 65 game px tall); the mannequin is fitted to the idle (the same height and limb lengths), its head top near y=464-472.
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).
NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_seraphine_run_a.png
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_hero_seraphine_run_b.png
  python3 tools/art/add_gait.py sheet/hero/seraphine --gait run --src art/inbox/gait/sheet_hero_seraphine_run_a.png art/inbox/gait/sheet_hero_seraphine_run_b.png --pose art/requests/gait/robe__hero_seraphine/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS. The third must end without an error and write
<temp dir>/sheet_hero_seraphine_preview_x4.png and sheet_hero_seraphine_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at
4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the
planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_hero_seraphine_run - 세라핀 — 파문당한 성녀 (파문 성녀) 이동
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_robe_a/b, guide_robe_plain_a/b, size_robe_a/b, preview_robe.gif, sheet_hero_seraphine.png, portrait.png, pose.json -> ok / FAILED (reason)
  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)
  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the
              PERSONALITY and wrist-range lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request
  ## 판정 — gait/sheet_hero_seraphine_run
  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)
  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)
  고칠 점: (who - GPT/cloud - what, with frame numbers; "없음" if it passes)
  남은 걱정: (what the owner's look should check; "없음" if none)
  캐릭터 메모: (direction for this character's next motions; omit if none)
The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
