# 그림 작업 우편함 (Art Mailbox)

이 폴더는 **그림을 만드는 쪽(ChatGPT / Codex 등)**과 **게임 코드를 맡은 쪽(Claude Code)**이 GitHub 저장소를 통해 그림을 주고받는 곳이다.

## 진행 방식
그림 쪽(ChatGPT / Codex)은 **그림만** 만든다. 요청서 작성, 후처리, 게임 연결, 화면 확인은 모두 코드 쪽(Claude Code)이 한다.
1. 사람이 그림 쪽에 "요청서의 이 묶음을 그려서 `art-inbox`에 올려 줘"라고 지시한다.
2. 그림 쪽이 `art/inbox/`에 PNG를 넣고 `art-inbox` 브랜치에 푸시한다.
3. 사람이 코드 쪽에 "올렸다"고 알리면, 코드 쪽이 받아서 처리한다.

> **PC Aseprite 세션**: 주인 PC(Windows)의 Claude 가 정품 Aseprite + aseprite-mcp 로 받은 도트를 손질하고 자세 뼈대를 만들어 같은 길(`art-inbox`의 `art/inbox/`)로 납품한다.
> PNG 와 함께 원본 `art/inbox/aseprite/<stem>.aseprite`를 올리고, 푸시 전 `tools/art/check_delivery.py`로 자체 검사한다.
> 설치: `tools/aseprite-mcp/README.md`, 역할·브랜치·이름·PC 첫 지시문: `docs/pc_cloud_protocol.md`.

## 그림을 만드는 쪽이 할 일

1. `art/STYLE.md`(화풍 기준), 지시받은 단계의 요청서 `art/requests/phaseN.md`, `art/requests/feedback.md`(피드백)를 읽는다.
   - 같은 내용의 기계용 목록은 `art/requests/phaseN.json`.
   - **3단계(전투 캐릭터)**는 `art/requests/gpt_handoff_notes.md`(가장 우선)와 캐릭터 꾸러미 `art/requests/phase3/<id>/README.md`를 따른다:
     캐릭터마다 1536×1024 한 장에 핵심 자세 4개를 한 줄로, 꾸러미의 `guide_strip.png`와 같은 배치, 마젠타 `#FF00FF` 배경.
     **바렌을 먼저** 그리고 승인을 기다린다. 승인된 바렌 그림이 나머지 모두의 화풍 기준(앵커)이다 (아래 「GPT handoff」).
   - 초상화(1단계)는 승인된 그림 `art/inbox/captain_blademaster.png`, `captain_ironwall.png`, `captain_tactician.png`를 화풍 기준 그림으로 쓴다.
2. 요청받은 묶음의 그림을 프롬프트로 생성한다.
   - 프롬프트는 화풍 기준을 지키는 범위에서 다듬어도 된다.
   - 초상화는 **배경 투명 PNG**. 전투 캐릭터는 **평평한 마젠타 배경**(투명도 됨).
3. 결과물을 **`art/inbox/<요청서의 파일 이름>`**으로 저장한다. (예: `art/inbox/captain_lancer.png`)
   - 파일 이름을 바꾸지 말 것. 이름으로 어느 요청인지 찾는다.
4. `art/inbox/NOTES.md`에 만든 파일 목록, 다시 그리고 싶은 것, 요청서와 다르게 한 점을 적는다.
5. 커밋해서 **`art-inbox` 브랜치에 푸시**한다.
   - **`art/inbox/` 밖의 파일은 고치지 않는다.** (`js/`, `css/`, `index.html`, `assets/`, `tools/`, `art/requests/` 모두 코드 쪽 담당)

> 사람이 ChatGPT 이미지 생성으로 만든 파일을 같은 이름으로 `art/inbox/`에 올려도 된다 (GitHub 웹에서 끌어다 놓기 가능).

## 코드 쪽(Claude Code)이 할 일

1. `art-inbox` 브랜치의 새 그림을 가져와 확인한다.
2. `python3 tools/art/process.py`로 후처리한다.
   - 배경 제거(단색 배경일 때), 여백 자르기, 축소, 팔레트 정리.
   - `assets/art/`에 저장하고 `assets/art/manifest.json`을 갱신한다.
   - 전투 캐릭터(`sheet_*.png`)는 `python3 tools/art/sheets.py`로 처리한다 (아래 「전투 캐릭터 시트」).
3. 게임은 `manifest.json`에 있는 그림을 쓰고, 없는 그림은 기존 코드 생성 도트로 대신한다. 그래서 일부만 들어와도 게임이 깨지지 않는다.
4. 화면에서 확인한 뒤 고칠 점과 다음 묶음을 `art/requests/feedback.md`에 적어 푸시한다.

## GPT handoff — 3단계 전투 캐릭터 (주인과 합의한 흐름)

| 단계 | 누가 | 결과 |
|---|---|---|
| 1. 디자인 초안 | NovelAI (사용자가 원할 때만, 무료 범위) — **초안 전용** | `art/concepts/<id>/` — 주인이 고른 것만 (`selections.json`) |
| 2. 자세 가이드 | 코드 `tools/pixelart/posekit.py` | 4등신 마네킹, 무기별 프레임 |
| 3. 꾸러미 | 코드 `python3 tools/art/handoff.py` | `art/requests/phase3/<id>/` — concept · portrait · guide_1..4 · `guide_strip.png` · README(한국어 요약 + GPT용 영어 프롬프트) |
| 4. 최종 그림 | **Antigravity** (2026-11-26 부터 그림 전담 — 그 전의 그림은 GPT) | `art/inbox/sheet_<id>.png` → `art-inbox` 브랜치 |
| 5. 후처리 | 코드 `python3 tools/art/sheets.py` | 80×80 칸 시트 + manifest |

- **NovelAI 는 디자인 초안 전용이다 (주인 결정).** 게임에 들어가는 최종 그림은 Antigravity 가 그린다(주인 2026-11-26; 그 전의 그림은 GPT) — NovelAI 로 최종본을 만들거나 시트로 등록하지 않는다.
- NovelAI 초안끼리는 화풍·비율이 제각각이다 → **디자인(옷·색·무기·흉터)만** 가져오고, 비율은 posekit(4등신), 화풍은 앵커가 정한다.
- 일반 병과(`class_<key>`)는 한 그림을 서로 다른 여러 사람이 같이 쓰므로 **얼굴이 가려지는 복장** (면갑·후드와 마스크·눌러쓴 모자 챙과 높은 깃·두건과 베일·깊은 후드). 상급 직업은 어울릴 때만.
- 순서: 바렌(앵커) → 주인 승인 → 나머지 창설 후보 8명 → (선택) 로드릭 기마 → 펠릭스 색 고치기(메시지 C) → 펠릭스 승인 → 일반 병과 5(메시지 D)·1차 몬스터 8(메시지 E) → 납품 검토: 승인 13장 등록, 거대 거미 다시 그리기 + 일곱 장 손보기(메시지 F) → 그 뒤 특별 용병·나머지 몬스터·보스·나머지 대장·상급 직업.
- **마젠타 규칙**: 그림의 모든 색은 배경 키 `#FF00FF`와 RGB 거리 150 이상 (펠릭스 첫 납품은 로브 밝은 면이 `#FF00FF`라 구멍이 뚫렸다).
- 일반 병과(`class_<key>/`)·몬스터(`monster_<key>/`) 꾸러미도 `handoff.py`가 만든다. 사람이 아닌 몬스터는 posekit 대신 `guide_layout.png`(배치·크기 상자)와 `guide_scale.png`(같은 배율의 사람과 비교).
- 그림 쪽(GPT)이 일하는 법: **`art/requests/GPT_STANDING.md`**(한 번 붙여 넣는 상시 지침) + `art/requests/dot_queue.md` 「지금 차례」. 옛 항목별 메시지 A~I 는 `art/requests/archive/phase3_gpt_log.md`.
- 꾸러미 다시 만들기: `node tools/art/requests.js && python3 tools/art/handoff.py` (같은 입력 → 같은 파일).
  새 캐릭터는 `handoff.py`의 `CHARS`에 무기(posekit)·프레임·초안·고칠 점을 더한다. 직업·캐릭터별 posekit 자세 세트는 미뤘다 (일반 마네킹 + 가장 가까운 무기).

## 전투 캐릭터 시트 (코드 쪽)

```bash
python3 tools/art/sheets.py                       # art/inbox/sheet_*.png 전부 → assets/art/sheets/ + manifest
python3 tools/art/sheets.py art/inbox/sheet_hero_kai.png --dry-run --work /tmp/sheets   # 미리보기만
# GPT 대장 1×4 띠(가이드 격자: 발바닥 y=870, 머리 110px)는 하나씩, 앵커 바렌과 같은 배율·96 칸으로:
python3 tools/art/sheets.py art/inbox/sheet_captain_ironwall.png --scale 0.1654 --cell 96
python3 tools/art/sheets.py art/inbox/sheet_captain_lancer.png --scale 0.1654 --cell 112   # 창을 앞으로 뻗는 타격이 96 칸보다 넓다
```
- `--scale`: 같은 가이드 격자에 그린 시트는 같은 배율로 줄인다. 기본(`--height 64`)은 대기 자세의 모자·머리숱까지 64px에 넣으므로
  모자가 높은 이사벨·머리숱이 큰 키아라가 바렌보다 9~11% 작아진다. `--cell 96`: 무기를 치켜든 준비 자세(마그다 89px)가 80 칸에 들어가지 않아 줄어드는 것을 막는다.
  칸 크기는 시트마다 달라도 된다 (전투 화면은 manifest의 cell·anchor를 그대로 쓴다).
- `sheet_captain_lancer_mounted.png`(2×2 기마 예비 그림)는 게임에서 쓰지 않으므로 **등록하지 않는다** (인자 없이 `sheets.py`를 돌리면 함께 처리되니 파일을 하나씩 지정할 것).
- 입력: 1×4 띠(대기·준비·타격·피격), 2×2 격자, 또는 전신 한 장(대기만). 자세 수는 자동으로 찾는다 (`--grid 4x1`로 강제).
- 칸마다 배경 제거 → 대기 자세 몸 높이를 64px로 맞춘 같은 배율로 축소 → 알파 정리 → 1px 어두운 가장자리 → 가장자리까지 포함한 시트 공통 팔레트(`--colors`, 기본 40색)
  → 80×80 칸, 발 (40,76) → 대기는 `sprite-gen breathe --mode pixel` 숨쉬기 4칸 → 시트 png + Aseprite json-array(태그 idle/attack/hit)
  → `tools/art/register_sheet.py`로 `manifest.json`의 `sheet/<kind>/<key>` 항목 등록. `--aseprite OUT`이면 태그 붙은 .aseprite 도 (Aseprite 있을 때만).
- 발 맞추기: 보통은 가장 아래 줄(발바닥)의 가운데를 앵커에. 발이 다 닿지 않은 공격·피격 자세(발바닥 띠가 대기 자세의 절반보다 좁다: 덮치는 늑대의
  뒷발 끝, 한 발로 선 피격, 늘어뜨린 칼끝)와 네발짐승(대기 자세 너비 ≥ 키×1.3)의 모든 자세는 몸 무게중심을 대기 자세의 무게중심 자리에 둔다
  (`pose_feet_x`). 예전에는 늑대가 공격·피격 때 앞으로 7~21px 튀어 나갔다. 이미 등록된 시트는 원본 없이
  `python3 tools/art/sheets.py --realign [--dry-run] [id ...]`로 같은 규칙에 맞춰 칸 안에서 민다 (manifest 는 그대로, 두 번 돌려도 같다).
- 작업 폴더의 `preview_x4.png`를 열어 확인한다. 왼쪽을 보고 그려졌으면 `--flip`.
- 가로로 긴 그림은 키가 비슷한 인물이 셋 이상(또는 붙은 인물들로 아주 넓은 덩어리 하나)일 때만 1×4 띠로 보고, 자세는 인물 가운데 위치로 나눈다 (인물끼리 칼끝이 닿으면 경계에서 자른다). 한 사람 옆에 떨어진 불꽃·구슬·늑대가 있는 그림은 한 자세로 본다.
- 칸에 맞추려고 15% 넘게 줄여야 하는 자세, 대기 자세 키의 절반 남짓도 안 되는 자세가 나오면 실패로 끝나고 등록하지 않는다 (`--grid` / `--poses`로 지정해 다시).
- 괴물 id에는 빈칸이 있을 수 있다 (`sheet/monster/사막 도적`). png 이름은 요청서의 파일 이름(`sheet_monster_desert-bandit.png`)을 쓴다.
- 직업 시트(`sheet/class/*`)는 아군·적군이 함께 쓰므로, 제복·장식에 쓴 열쇠 색을 `register_sheet.py --tint-outfit/--tint-accent`로 적어 두면 전투에서 진영 색으로 바꿔 칠한다. 적지 않으면 제복 색이 있는 병사는 코드 생성 도트로 그린다.
  제복 색(`look.tint`)이 없는 병사(우리 길드의 일반 단원)는 소속 용병단 색을 제복에, 놋쇠색(용병단 색이 금빛·주황이면 은색)을 장식에 입힌다. 용병단 색도 없으면 회갈색 `#5f5a52`.
  일반 병과의 열쇠 색은 요청서(`phase3.json`의 `tint`: 제복 `#263459 #394b78 #52679c #7489be`, 장식 `#3f7a6c #5ea590 #96d1bb`)에 있고, `sheets.py`가 원본 해상도에서 가까운 색(거리 34)을 열쇠 색으로 되돌려 축소 뒤에도 남기고 `--tint-*`를 자동으로 넘긴다. `preview_tint_x4.png` = 시험 색으로 바꿔 칠한 미리보기.
- 열쇠 색 점 지우기: 덩어리(몸통)에서 떨어진 열쇠 색 점·그물(사슬 갑옷에 섞인 푸른 점 등)은 원본 해상도에서, 이웃 열쇠 픽셀이 1개 이하인 부스러기는 게임 해상도에서 열쇠 색에서 빼고 둘레 색으로 칠한다 (진영 색 점이 튀지 않게; 비교용 `--keep-key-specks`).
- 전투의 바꿔 칠하기(`js/battle.js` `toneRamp`, 미리보기는 `sheets.py` `tone_ramp`)는 진영 색 밝기를 눌러 쓴다: 밝은 색은 무릎 위를 완만하게, 밝은 단계는 부드럽게 눌러 255 에서 잘리지 않게(금빛·자유도시 노랑이 평평한 덩어리가 되지 않게), 장식 색은 얼굴 가리개에도 쓰이므로 더 어둡게. 인물과 땅의 밝기가 비슷하면 테두리를 진하게 (`rimLow`).
- `pose_scale`(요청서) / `--pose-scale windup=0.9,strike=0.88`: GPT 가 큰 자세 상자를 채우려고 한 자세만 몸까지 키워 그린 경우 그 자세만 줄인다 (가고일 첫 납품). 가로로 긴 대기 자세(너비 ≥ 키 x1.3, 늑대 등)는 숨쉬기가 등 전체를 오르내리게 sprite-gen breathe 에 강체 경계를 위쪽으로 넘긴다.
- 요청서 항목에 `scale`·`cell`·`layout`(2x2)이 있으면 `sheets.py`가 기본값으로 쓴다 (일반 병과·1차 몬스터는 대장과 같은 0.1654 배율). 명령줄 옵션이 우선.
- 이름 뒤에 `@`이 붙은 후보(`sheet_x_y@123.png`)는 직접 지정할 때만 처리한다.
- `process.py`는 `sheet/*` 등 자기가 만들지 않은 manifest 항목을 건드리지 않는다.

### 달리기·걷기 프레임 붙이기 (`tools/art/add_gait.py`)
전투에서 유닛은 달린다 (주인 결정 2026-11-26) — 그려 온 **달리기(run)** 프레임을 이미 등록된 시트에 붙인다. **걷기(walk)** 도 같은 방법이다:
걷기 칸은 걷는 걸음 — 거미줄에 걸려 무겁게 걷기(trudge)·뒷걸음(back)·밀리거나 아주 느리게 옮겨질 때의 한 발짝(step) — 에 쓰인다 (`js/battle.js`; 둔화된 유닛만이 아니다).
최종 프레임은 `art/inbox/gait/<시트 png 이름>_<gait>` 로 들어온다: `gait/sheet_class_warrior_run.aseprite` 또는 `gait/sheet_class_warrior_run_a.png` + `_b.png`
(`python3 tools/art/receive.py gait/sheet_class_warrior_run` 이 검사하고 `--dry-run` 까지 돌린다. 인자 없는 `sheets.py` 는 `art/inbox/sheet_*.png` 만 보고 `gait/` 안으로 들어가지 않는다).
```
python3 tools/art/add_gait.py sheet/class/warrior --gait run \
        --src art/inbox/gait/sheet_class_warrior_run_a.png art/inbox/gait/sheet_class_warrior_run_b.png \
        --pose art/requests/guides/run_base/v1/pose.json            # 한 걸음 = pose.json 의 step_px x 시트 배율 (run_base 275px → 45.5)
python3 tools/art/add_gait.py sheet_class_warrior --gait run --src art/inbox/gait/sheet_class_warrior_run.aseprite --stride 45.5 --ms 80
python3 tools/art/add_gait.py sheet/class/warrior --gait walk --src art/inbox/gait/sheet_class_warrior_walk_a.png art/inbox/gait/sheet_class_warrior_walk_b.png \
        --pose art/requests/guides/walk_base/v2/pose.json
python3 tools/art/add_gait.py sheet/class/warrior --gait run --src ... --pose ... --dry-run --work /tmp/gait   # 새 png · 등록될 항목 · 미리보기만
python3 tools/art/add_gait.py sheet/class/warrior --gait run --remove                              # 다시 뺀다
```
- 원본은 `art/requests/guides/SPEC.md` 의 프레임 규격: 한 프레임 384×1024, 띠 `_a.png`(1~4번)·`_b.png`(5~8번) 또는 프레임이 든 `.aseprite` 하나(보이는 레이어만).
  **모든 프레임에서 엉덩이 중심 x=192, 바닥 줄 y=870.** 납품된 파일 옆에는 pose.json 이 없으므로 `--pose <요청의 pose.json>` 또는 `--stride` 를 꼭 준다.
- 변환은 그 시트를 만들 때와 같다 (`sheets.py` 의 함수 `matte`·`shrink_pose`·`outline`·`paint_pose` 를 그대로 부른다: 요청서의 scale, 키 제거, 열쇠 색·점 색).
  팔레트는 등록된 시트의 기본 칸에 있는 색을 쓴다 — 이동 칸에 새 색이 생기지 않는다.
- 자리 맞춤은 맨 아래 픽셀이 아니라 **바닥 줄 y=870 → anchor y, x=192 → anchor x** (달리기의 뜬 프레임이 바닥에 내려앉지 않고, 프레임마다 몸이 흔들리지 않는다).
  바닥 줄·가운데 열이 다른 그림이면 `--floor` / `--center` (모든 프레임에 같은 값).
- 결과: 시트 png 아래에 새 줄(기본 7칸의 픽셀은 그대로, 줄 순서는 run → walk), manifest 의 `sheet` 에 `frames` 추가 · `anims.run = {from, to, ms}` ·
  `runStride`(한 걸음의 게임 px, n 프레임 = 두 걸음) · `gaits.run`(원본·바닥 줄·걸음 기록). 걷기는 `anims.walk` / `walkStride` / `gaits.walk`. `js/art.js` 는 그대로 읽는다.
- **기본 시트를 다시 등록해도 잃지 않는다**: `register_sheet.py`(= `sheets.py` 의 마지막 단계)가 `gaits` 기록을 새 항목에 옮기고 `add_gait.py <id> --reattach` 로
  기록된 원본에서 다시 변환해 붙인다 (새 팔레트·새 칸 크기로). 원본이 없으면 `!!! 경고` 와 다시 붙일 명령을 찍고 기록만 남긴다 (그동안 게임은 그 시트를 이동 칸 없이 그린다).
  그래서 붙인 원본은 `art/inbox/` 에 그대로 둔다. `sheets.py --realign` 은 이동 칸을 밀지 않는다.
- 거부하는 원본 (게임 그림이 아니다 — `--allow-draft` 는 시험용이고 언제나 `--dry-run`):
  - 초안 자리: `art/requests/`, `art/concepts/`, `drafts/`, `nai_*`, NovelAI 메타데이터 (`sheets.py` 와 같은 규칙).
  - 뼈대(마네킹): 경로에 `guides/` 폴더가 있는 파일 (`art/requests/guides/…`, PC 가 넘기는 `art/inbox/guides/<id>/`), 옆에 `pose_measured.json` 이 있는 띠
    (`check_skeleton.py --export`), `joints` 레이어가 있는 `.aseprite` (그 레이어가 보이면 `--allow-draft` 로도 받지 않는다 — 관절 점이 찍힌다).
  - 초안과 같은 실루엣: 어느 프레임이든 클라우드 뼈대 초안(`art/requests/guides/*/v*/` 의 띠, 또는 `layers/` 를 프레임마다 합친 것; joints 제외)과
    실루엣이 IoU 0.85 넘게 겹치면 거부한다(회전 ±11°·2×2 배치·좌우 뒤집기·크기 ±10%·외곽선까지 맞춰 본다; 실제 그림 58장의 최고 0.72) — joints 레이어를 지운 마네킹, 이름을 바꿔 옮긴 마네킹 띠. 그린 캐릭터는 옷·머리·무기로 실루엣이 달라진다
    (시험: 마네킹 실루엣을 원본 3px 키우면 0.91 로 거부, 6px 키우면 0.83 으로 통과).
- 실패로 끝나는 그림:
  - 384px 프레임 칸의 테두리(x=0 / 383, y=0 / 1023)에 닿는 프레임 — 띠를 384px 씩 자르면 그림이 잘리거나 옆 자세의 조각이 들어온다 (프레임 번호를 알린다).
  - 바닥 줄 아래로 내려가는 프레임 (게임 px 로 1px 이상; 발이 땅에 묻힌다). 일부러 그런 것이면 `--allow-below` (기록에 남아 다시 붙일 때도 쓴다).
  - 칸에 안 들어가는 프레임 — 줄이거나 밀지 않고 몇 px 넘는지 알린다.
- `receive.py gait/<시트 png 이름>_<gait>` 의 검사: 띠마다 `check_delivery.py` (run 은 `--flight-slots 4`: 4번 칸 = 뜬 프레임, 바닥 줄 위 18px 이상),
  `.aseprite` 가 있으면 마네킹 검사(위의 joints 레이어·초안 실루엣)와 PNG = `.aseprite` 내보내기 비교, 그다음 `add_gait.py --dry-run`.
  등록 명령(`register after judging: …`)은 **모든 검사가 통과했을 때만** 찍힌다.

### NovelAI (사용자가 원할 때만, 디자인 초안 전용)
`python3 tools/art/novelai.py --only sheet/class/warrior` → `art/concepts/class_warrior/drafts/nai_class_warrior_s21149.png` (한 자세, 마젠타 배경; `drafts/`는 git 에 올리지 않는다).
**NovelAI 그림은 게임 그림이 되지 않는다** (주인 결정: 최종 그림은 Antigravity). `novelai.py`는 `art/inbox/`·`assets/`·`art/requests/`에 쓰지 못하고
`sheet_*.png` 이름도 만들지 않는다. `sheets.py`는 NovelAI 그림(PNG 메타데이터 `Software: NovelAI`, `art/concepts/`·`art/requests/`·`drafts/` 안, `nai_*` 이름)을 거부한다
(`--allow-draft` = 파이프라인 시험용, 언제나 `--dry-run`이라 등록할 수 없다). 주인이 고른 초안만 `art/concepts/<id>/concept_NN.png`로 옮겨 꾸러미의 `concept.png`(디자인 참고)가 된다.
기본값은 무료 범위(넓이 ≤ 1024×1024, 28 steps, 1장)이고, 더 큰 설정은 `--allow-paid` 없이는 거부한다. 한 번에 `--max` 2장.
토큰은 클라우드 세션의 프록시가 넣는다 (로컬에서는 `NOVELAI_TOKEN`). 대량 생성 금지.

## 단계
- **1단계 (완료)**: 용병대장 33명 · 특별 용병 7명 · 재앙 수장 2명 초상화, 이벤트 그림 9장 — 총 51장.
- 2단계 (예정): 전투 배경 7종, 길드 홀, 대륙 지도.
- **3단계 (진행)**: 전투 캐릭터 시트 — 창설 후보 대장 9 (+ 로드릭 기마, 선택; 펠릭스 다시) → 일반 병과 5 + 1차 몬스터 8 (꾸러미 준비, 초안 대기) → 특별 용병 7 → 나머지 몬스터 14·보스 → 나머지 대장 24 (`phase3.md`).
  바렌(`sheet/captain/blademaster`)은 승인된 GPT 그림으로 바뀌었다 (예전 임시 NovelAI 판은 교체; 등록된 시트 중 NovelAI 그림은 없다).
- 4단계 (예정): 깃발·문장, 의뢰서·UI 장식, 장비 아이콘.
