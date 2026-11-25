# 달리기 뼈대 v1 (8프레임) · `guide/run_base` — 공통 규칙은 `art/requests/guides/SPEC.md` (달리기는 5b절)

**왜 만드나 (주인 결정 2026-11-26)**: "걷기만 남기는건 동의하지 않아. 기본적으로 전투잖아? 차라리 뛰기 모션만 있는게 맞지 걷기만 하는건 어색하지 않을까."
→ 전투에서 유닛은 **달린다**. 걷기 세트(`../walk_base/`)는 참고와 느려진 유닛용으로만 남고, 직업별 이동 프레임은 이 달리기 뼈대 위에 그린다.

## 초안 (이 폴더 `v1/`, 클라우드가 `python3 tools/pixelart/run8.py art/requests/guides/run_base/v1 --aseprite tools/art/ase_headless.sh` 로 만든 것)
- **`v1/run_base.aseprite` — 작업 파일.** 384x1024, 8프레임 x **80ms**, 레이어 Background · arm_far · leg_far · leg_near · torso · head · arm_near · joints(숨김, 관절 점).
  걷기 뼈대와 같은 마네킹·같은 캔버스·같은 바닥 줄(y=870)·같은 관절 점 색이다. 열어서 바로 재생·양파 껍질 보기가 된다.
- `v1/run_base_a.png` (R1~R4) · `v1/run_base_b.png` (R5~R8) · `v1/run_base_preview.gif` (게임 크기, 80ms) · `v1/run_base_review.png` (띠 축소 + 전장 바닥색 위 게임 크기 8프레임)
  · `v1/pose.json` (프레임별 관절 좌표·수치, `"gait": "run"`) · `v1/layers/R<n>_<레이어>.png`
- 프레임: R1 닿음(가까운 발, 몸보다 조금 앞, 무릎 굽힘) · R2 내려앉음(눌림, 엉덩이 가장 낮음) · R3 밀어냄(디딘 다리가 뒤로 뻗고 뒤꿈치 들림) ·
  R4 뜸(**두 발 모두 공중**, 엉덩이 가장 높음, 다리 가위) · R5~R8 같은 것을 먼 발로. **한 번에 한 발만 디딘다.**
- 수치: 한 걸음(몸이 한 걸음에 가는 거리) 275px = 게임 45.5px(`runStride`), 엉덩이 오르내림 37.4px(키의 8.5%), 뜬 프레임의 바닥 틈 41px(R4)·37px(R8),
  상체 기울기 18~21°(걷기 8~11°), 팔꿈치 80~110°, 밀어냄 무릎 16°/18°, 내려앉음 무릎 51°/53°, posekit 경고 0, `check_skeleton.py` PASS(경고 0).
  `check_delivery.py` 는 두 띠 모두 **4번 칸에서만 실패**한다("lowest pixel ... expected 870") — 뜬 프레임이라 당연하다. 그 밖의 항목(크기·배경·색 거리·간격·자세 4개)은 통과.

## PC(Aseprite)가 할 일 — 초안을 그림으로 다듬기
1. `v1/run_base.aseprite` 를 납품 폴더(`../pixel-management-inbox/art/inbox/guides/run_base/run_base.aseprite`)로 복사해 Aseprite 로 열고 재생해 본다(80ms, 양파 껍질 보기).
   띠 PNG 를 잘라 프레임을 만들 필요가 없다 — 이미 프레임·레이어가 나뉘어 있다.
2. 어색한 곳을 손으로 고친다. 클라우드가 보기에 남은 곳: R2·R6(내려앉음)에서 디딘 정강이가 평평한 발 위로 34°(R6 은 39°)나 기울어 발목이 꺾여 보이고 두 다리가 한 덩어리로 뭉친다,
   R1·R5 에서 닿는 발이 가슴 바로 아래라 "내딛는" 느낌이 약하다, R4·R8(뜸)의 앞다리 정강이가 수직이라 뻗는 느낌이 약하다,
   먼 팔은 앞으로 갈 때 아래팔만 가슴 앞으로 나온다(프레임 폭 때문에 줄였다). 그리고 재생했을 때 **무게가 실린 달리기**로 보이는가 — 깡충거리는 걷기처럼 보이면 안 된다.
3. SPEC 3절(캔버스)·4절(레이어)·5b절(달리기 수치)을 지킨다. 뼈 길이는 바꾸지 않는다. **팔다리를 옮기면 `joints` 레이어의 그 관절 점도 같은 만큼 옮긴다**
   (점 색은 SPEC 4절. 레이어 이름·순서·캔버스 크기·프레임 수는 그대로). 지킬 것 넷:
   - R1~R3·R5~R7 의 디딘 발은 y=870 에서 떼지 않고, 그 프레임의 반대 발은 바닥에 대지 않는다(12px 이상 띄움).
   - R4·R8 은 아무것도 바닥에 닿지 않는다(맨 아래 픽셀이 y=852 보다 아래로 내려오지 않게 — 바닥 틈 18px 이상. 초안은 37~41px).
   - 디딘 발의 **발끝**은 R1 → R2 → R3 에서 프레임마다 같은 거리(약 69px)씩 뒤로 간다. 발을 옮기면 세 프레임을 같이 본다(발 미끄럼).
   - 그림은 프레임의 x=32~351 안에 둔다(띠 가장자리에 마젠타 32px 가 남아야 한다).
4. 자체 검사(이 저장소 폴더에서, 한 줄): `uv run --no-project --with pillow --with numpy python tools/art/check_skeleton.py ../pixel-management-inbox/art/inbox/guides/run_base/run_base.aseprite --pose art/requests/guides/run_base/v1/pose.json --base art/requests/guides/run_base/v1/run_base.aseprite`
   — 첫 줄이 `# skeleton run_base (run)` 이어야 한다(달리기 규칙으로 잰다는 뜻). `FAIL` 이 있으면 푸시하지 않는다. `changed against the draft` 줄들과 `RESULT` 줄을 NOTES 에 옮겨 적는다.
   달리기 띠에는 `check_delivery.py` 를 따로 돌리지 않는다(뜬 프레임 때문에 실패가 나온다 — 띠 항목은 위 검사에 들어 있다).
5. 납품: art-inbox `art/inbox/guides/run_base/run_base.aseprite` **하나**(띠·GIF 는 클라우드가 이 파일에서 뽑는다).
   NOTES 절 「뼈대 — 달리기 v1 (Aseprite)」: 바꾼 프레임과 수치(px), 참고한 자료, 검사 줄. 커밋 `Touch up guide run_base (Aseprite)`.
   손댈 곳이 없다고 판단하면 그렇게 적고 초안 `.aseprite` 를 그대로 올려도 된다.

## 참고
- 주인이 준 동작 예시에서 읽은 것(`../attack_notes.md`, `../walk_base/README.md`): 달리기는 상체 기울임·두 발이 뜨는 프레임·오르내림 약 9%.
- 참고 자료(`art/refs/`)는 리듬만 본다. 따라 그리지 않는다.
- 엔진: 달리기 프레임이 있는 시트는 `anims.run` + `runStride`(게임 px, 이 초안 45.5)로 등록한다 — SPEC 9절. 이 걸음 길이를 바꾸면(±14px 초과) 요청을 새로 낸다.
- 수치표는 `tools/pixelart/run8.py` 맨 위에 있다. 받은 다듬기는 걷기 때처럼 이 표에 되돌려 넣는다.
