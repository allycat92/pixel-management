# 니클라 달리기 · `sheet/captain/shadowqueen` → `gait/sheet_captain_shadowqueen_run`

**상태: 요청 (2026-11-26, 클라우드).** GPT 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이고 구부리는 코드 달리기는 쓰지 않는다. **확정된 달리기 마네킹(`art/requests/guides/run_base/v2/`) 8프레임 위에 캐릭터를 프레임마다 덧그린다.**
그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js` 의 `anims.run`)이 코드 달리기와 같은 박자(80ms)로 넘긴다.

| 파일 | 내용 |
|---|---|
| `guide_run_a.png` / `guide_run_b.png` | **자세·자리 가이드** = 확정 마네킹 띠 그대로(R1~R4 / R5~R8). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870, R4·R8 은 공중 |
| `size_run_a.png` / `size_run_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게) 위에 마네킹 R1/R5 윤곽(하늘색) — **같은 배율**임을 보여 준다. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선 |
| `art/requests/phase3/captain_shadowqueen/portrait_800.jpg` | 승인된 초상화(가벼운 사본) — 얼굴·머리·옷의 디자인 기준 |
| `art/inbox/sheet_captain_shadowqueen.png` | **승인된 전투 시트 원본**(이 브랜치와 art-inbox 에 있다; 쌍검 `aa0687e`·타격 `0cc6046`·대기 `e4df48d`) — 디자인·색·크기의 기준. 1번 자세가 대기(두 칼 아래로) |

- 납품: art-inbox `art/inbox/gait/sheet_captain_shadowqueen_run_a.png` (R1~R4) + `..._run_b.png` (R5~R8) + `art/inbox/NOTES.md` 절 「## gait/sheet_captain_shadowqueen_run - 니클라 달리기」.
- 팔·무기: 쌍검은 대기처럼 **바로 쥐고(forward grip) 낮게**, 칼날은 **뒤-아래로 끌린다** — 몸 앞을 가로지르지 않는다. 먼 칼은 대기처럼 몸·망토 뒤에 거의 가려진다.
  망토·머리카락·코트 자락은 **한 프레임 늦게** 뒤로 날린다. 후드는 늘 쓴 채, 얼굴은 집중(입 다묾).
- 클라우드가 받은 뒤: `python3 tools/art/receive.py gait/sheet_captain_shadowqueen_run` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다.

## Prompt for GPT

```
TASK: draw the RUN CYCLE (8 frames) of Nikla (니클라), queen of the shadow guilds, as TWO new PNG strips on the art-inbox branch:
  art/inbox/gait/sheet_captain_shadowqueen_run_a.png  = frames R1 R2 R3 R4
  art/inbox/gait/sheet_captain_shadowqueen_run_b.png  = frames R5 R6 R7 R8
Draw the character OVER the accepted run mannequin, frame by frame - like a sprite sheet traced over a skeleton.
Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the run look squashed.

REFERENCES (load all; if the sheet or the portrait does not load, do not draw - report BLOCKED):
  - art/requests/gait/run__captain_shadowqueen/guide_run_a.png, guide_run_b.png = THE POSE AND PLACEMENT GUIDE for every frame
    (the accepted run mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).
  - art/requests/gait/run__captain_shadowqueen/size_run_a.png, size_run_b.png = the same frames with guide lines, and on the
    left the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.
  - art/inbox/sheet_captain_shadowqueen.png (pose 1 = idle with both blades down) = the accepted battle sheet: design, colours,
    outline, rendering and SIZE. Same character, same pixel size, same palette.
  - art/requests/phase3/captain_shadowqueen/portrait_800.jpg = the approved portrait (design only).

CHARACTER (unchanged from the accepted sheet): lithe woman in her thirties, deep plum-black HOOD and long cloak with crimson trim
and a gold emblem clasp, long wavy blue-black hair falling out of the hood, tan skin, dark-red eyes, ruby earring and pendant,
dark corset and trousers with gold-buckled leather belts and a belt pouch, brown boots; TWIN SHORT SWORDS, one in EACH hand
(straight bright neutral-steel blades about 2 heads long, red-wrapped grips, gold crossguards, round gold pommels).

THE RUN (owner's rhythm, already in the mannequin - copy it, do not invent another):
  - Each frame: the legs, the torso lean and the arm swing of that mannequin frame. Joint for joint: hips, knees, ankles, feet,
    shoulders, elbows. The mannequin's big round head is a placeholder: draw Nikla's own hooded head on the mannequin's neck,
    at her own size (as in the sheet).
  - R1 contact (near foot lands a little ahead, knee bent) - R2 catch (body drops onto the foot, lowest) - R3 push-off (stance
    leg extends behind, heel up) - R4 FLIGHT (both feet clearly off the ground, legs scissored, body pressed forward and leaning
    the most). R5-R8 = the same with the far foot.
  - Lean forward: about 24 deg (R1/R5), 19 (R2/R6), 29 (R3/R7), 31 (R4/R8). She leans most in flight and rises a little once
    the landing is caught. The hips stay nearly level: the top of the hood stays within about 10 px of the same height in all
    8 frames. NO hopping, no bouncing up and down.
  - Feet: copy the mannequin's feet exactly (the standing foot moves back about 69 px per frame from R1 to R3 - that is the
    stride; do not shorten it).

ARMS AND WEAPONS:
  - Both swords in FORWARD grip as in her idle (blade out of the thumb side of the fist), hands LOW (between belt and hip
    height), swinging with the mannequin's arms (near arm forward in R2-R5, back in R6-R8/R1; far arm the opposite).
  - The blades TRAIL BACK and DOWN from the hands: about 35-45 deg below horizontal while the hand is forward, steeper
    (55-70 deg) while the hand is back. Never point a blade forward, never hold one across the chest or across the other arm,
    and the two blades never overlap each other.
  - Near blade: in front of the body (1 px dark outline); its tip and most of the blade show on the magenta behind her hip /
    rear thigh. It may overlap the near hip or thigh in the forward-swing frames, never the torso.
  - Far blade: mostly hidden behind her body and cloak, as in the idle; where it shows, only its lower part and tip behind
    her back or rear leg.
  - Never shorten a blade to fit - change its angle or lift the hand a little instead (see FORMAT for the limits).
  - Cloak, hair and coat-tails trail back and lag the body by ONE frame: they lift and stream back most in R1/R5 (right after
    the flight), and settle in R3/R7. The hood stays UP in every frame with the face visible. Keep the cloak and hair within
    about 150 px behind the hip column (inside the slot).
  - Face: focused, eyes forward along the run, mouth closed (no smile, no open mouth).

MUST NOT CHANGE: outfit, colours, proportions, hood, hair, both sword shapes and sizes, and the SCALE of the accepted sheet.
The body must not be shrunk to fit. Colour notes from the sheet: blades bright neutral steel (~#d8dde3, no blue or violet tint);
the dark outfit is dark charcoal-violet with a cool rim light on the upper-left edges (not black); the crimson trim stays red
(highlights toward orange-red, never pink).

FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,
front three-quarter view, light from the upper left, exactly the placement of guide_run_a/b.png:
  - the hip centre of every frame on the slot's column x=192 (the body stays in place, the feet move);
  - R1 R2 R3 / R5 R6 R7: the sole of the standing foot on y=870 (lowest pixel), the other foot well above it;
  - R4 / R8 (FLIGHT): NOTHING touches y=870 - the lowest pixel of the whole figure (boots, blade tips, cloak hem) at or above
    y=852;
  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - nothing may cross
    into the next slot; this includes the cloak, the hair and the blade tips);
  - head 110 px scale = the scale of the accepted sheet; the figure about as tall as the mannequin (top of the hood near
    y=450-460).
STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.
BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150) - careful with the
plum and crimson: never merge them with the background when reducing the palette.
NO effects: no shadow smoke, afterimages, dust, speed lines, motion blur, floor, text or guide lines in the delivery.

SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_shadowqueen_run_a.png --flight-slots 4
  python3 tools/art/check_delivery.py art/inbox/gait/sheet_captain_shadowqueen_run_b.png --flight-slots 4
  python3 tools/art/add_gait.py sheet/captain/shadowqueen --gait run --src art/inbox/gait/sheet_captain_shadowqueen_run_a.png art/inbox/gait/sheet_captain_shadowqueen_run_b.png --pose art/requests/guides/run_base/v2/pose.json --dry-run --work <temp dir>
The first two must print RESULT: PASS. The third must end without an error and write
<temp dir>/sheet_captain_shadowqueen_preview_x4.png and sheet_captain_shadowqueen_run_x4.gif - LOOK at them (the bottom two rows
of the preview are your 8 frames at 4x game size): Nikla must look like her idle self running, not squashed or shrunk, and both
blades must read. (add_gait refuses mannequin pixels: the frames must be your drawing.)

DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:
  ## gait/sheet_captain_shadowqueen_run - 니클라 달리기
  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")
  REFERENCES LOADED: guide_run_a/b, size_run_a/b, sheet_captain_shadowqueen.png, portrait_800.jpg -> ok / FAILED (reason)
  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet/portrait design (c) from the ARMS AND WEAPONS
              lines - write "none" explicitly for each
  RISKS AT GAME SIZE: what you could not verify at ~64 px
  PROPOSALS: optional
Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
