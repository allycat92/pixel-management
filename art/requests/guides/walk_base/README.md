# 걷기 뼈대 v2 (8프레임) · `guide/walk_base` — 공통 규칙은 `art/requests/guides/SPEC.md`

**상태**: v1(4프레임, `4feb568`)은 시범으로 끝났다. 검토에서 v1 이 뻣뻣한 이유가 확인됐다 — 요청서가 몸 오르내림을 4~8px 로 묶어
디딘 다리가 34° 굽은 채였고, 두 발이 모두 평평했으며(뒤꿈치 닿기·발끝 밀기 없음), 팔꿈치가 펴진 채였다. v1 의 잘못은 요청서(클라우드)에 있었다.

## 초안 (이 폴더 `v2/`, 클라우드가 `python3 tools/pixelart/walk8.py art/requests/guides/walk_base/v2 --aseprite tools/art/ase_headless.sh` 로 만든 것)
- **`v2/walk_base.aseprite` — 작업 파일.** 384x1024, 8프레임 x 120ms, 레이어 Background · arm_far · leg_far · leg_near · torso · head · arm_near · joints(숨김, 관절 점).
  열어서 바로 재생·양파 껍질 보기가 된다. (2026-11-26 확정판: PC 다듬기 `2c31b96` 의 세 수치 + 모든 프레임이 같은 바닥선, 닿는 발뒤꿈치가 바닥에, 가까운 팔 앞 흔들기 +7°)
- `v2/walk_base_a.png` (W1~W4) · `v2/walk_base_b.png` (W5~W8) · `v2/walk_base_preview.gif` (게임 크기, 120ms) · `v2/pose.json` (프레임별 관절 좌표·수치)
- 수치: 한 걸음 143px, 엉덩이 오르내림 15.4px, 지나감 무릎 굽힘 8°/12°, posekit 경고 0, `check_skeleton.py` PASS(경고 0), `check_delivery.py` PASS

## PC(Aseprite)가 할 일 — 초안을 그림으로 다듬기
**(2026-11-26: PC 다듬기 `2c31b96` 를 받아 반영했다. 지금은 GPT 교차 검수 3 을 기다리는 중 — PC 가 할 일은 없다. 아래는 다음 뼈대 세트에도 쓰는 절차다.)**
1. `v2/walk_base.aseprite` 를 납품 폴더(`../pixel-management-inbox/art/inbox/guides/walk_base/walk_base.aseprite`)로 복사해 Aseprite 로 열고 재생해 본다(120ms, 양파 껍질 보기).
   띠 PNG 를 잘라 프레임을 만들 필요가 없다 — 이미 프레임·레이어가 나뉘어 있다.
2. 어색한 곳을 손으로 고친다. 특히: W3·W7(지나감)에서 든 다리의 무릎이 앞서 보이는가, W7 에서 먼 팔이 몸통에 묻히지 않는가,
   W1·W5 의 뒤꿈치 닿기와 W4·W8 의 발끝 밀기가 게임 크기에서 읽히는가, 머리가 쪼는 것처럼 보이지 않는가.
3. SPEC 3절(캔버스)·4절(레이어)·5절(수치)을 지킨다. 뼈 길이는 바꾸지 않는다. **팔다리를 옮기면 `joints` 레이어의 그 관절 점도 같은 만큼 옮긴다**
   (점 색은 SPEC 4절. 레이어 이름·순서·캔버스 크기·프레임 수는 그대로). 디딘 발은 y=870 에서 떼지 않는다.
4. 자체 검사(이 저장소 폴더에서, 한 줄): `uv run --no-project --with pillow --with numpy python tools/art/check_skeleton.py ../pixel-management-inbox/art/inbox/guides/walk_base/walk_base.aseprite --pose art/requests/guides/walk_base/v2/pose.json --base art/requests/guides/walk_base/v2/walk_base.aseprite`
   — `FAIL` 이 있으면 푸시하지 않는다. `changed against the draft` 줄들과 `RESULT` 줄을 NOTES 에 옮겨 적는다.
5. 납품: art-inbox `art/inbox/guides/walk_base/walk_base.aseprite` **하나**(띠·GIF 는 클라우드가 이 파일에서 뽑는다. v1 의 `walk_strip.png` 등은 그대로 둔다).
   NOTES 절 「뼈대 — 걷기 v2 (Aseprite)」: 바꾼 프레임과 수치(px), 참고한 자료, 검사 줄. 커밋 `Touch up guide walk_base (Aseprite)`.
   손댈 곳이 없다고 판단하면 그렇게 적고 초안 `.aseprite` 를 그대로 올려도 된다.

## 참고
- 주인이 준 동작 예시에서 읽은 것: 걷기 8프레임 x 120ms, 오르내림은 키의 약 2%(이 초안은 3.2% — 다리 길이에서 나온 값), 달리기는 상체 기울임·두 발이 뜨는 프레임·오르내림 약 9%.
- 참고 자료(`art/refs/`)는 리듬만 본다. 따라 그리지 않는다.
- v1 납품물과 v1 요청서는 git 기록에 있다(`4feb568`, 이 파일의 이전 판).
