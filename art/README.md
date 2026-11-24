# 그림 작업 우편함 (Art Mailbox)

이 폴더는 **그림을 만드는 쪽(ChatGPT / Codex 등)**과 **게임 코드를 맡은 쪽(Claude Code)**이 GitHub 저장소를 통해 그림을 주고받는 곳이다.

## 진행 방식
그림 쪽(ChatGPT / Codex)은 **그림만** 만든다. 요청서 작성, 후처리, 게임 연결, 화면 확인은 모두 코드 쪽(Claude Code)이 한다.
1. 사람이 그림 쪽에 "요청서의 이 묶음을 그려서 `art-inbox`에 올려 줘"라고 지시한다.
2. 그림 쪽이 `art/inbox/`에 PNG를 넣고 `art-inbox` 브랜치에 푸시한다.
3. 사람이 코드 쪽에 "올렸다"고 알리면, 코드 쪽이 받아서 처리한다.

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
| 1. 디자인 초안 | NovelAI (사용자가 원할 때만, 무료 범위) | `art/concepts/<id>/` — 주인이 고른 것만 (`selections.json`) |
| 2. 자세 가이드 | 코드 `tools/pixelart/posekit.py` | 4등신 마네킹, 무기별 프레임 |
| 3. 꾸러미 | 코드 `python3 tools/art/handoff.py` | `art/requests/phase3/<id>/` — concept · portrait · guide_1..4 · `guide_strip.png` · README(한국어 요약 + GPT용 영어 프롬프트) |
| 4. 최종 그림 | **GPT** (한 화풍) | `art/inbox/sheet_<id>.png` → `art-inbox` 브랜치 |
| 5. 후처리 | 코드 `python3 tools/art/sheets.py` | 80×80 칸 시트 + manifest |

- NovelAI 초안끼리는 화풍·비율이 제각각이다 → **디자인(옷·색·무기·흉터)만** 가져오고, 비율은 posekit(4등신), 화풍은 앵커가 정한다.
- 순서: 바렌(앵커) → 주인 승인 → 나머지 창설 후보 8명 → (선택) 로드릭 기마 → 그 뒤 일반 병과·특별 용병·몬스터·나머지 대장.
- 주인이 그림 쪽에 붙여 넣을 메시지 A(바렌만) / B(승인 후 나머지): **`art/requests/phase3_gpt.md`**.
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
- 작업 폴더의 `preview_x4.png`를 열어 확인한다. 왼쪽을 보고 그려졌으면 `--flip`.
- 가로로 긴 그림은 키가 비슷한 인물이 셋 이상(또는 붙은 인물들로 아주 넓은 덩어리 하나)일 때만 1×4 띠로 보고, 자세는 인물 가운데 위치로 나눈다 (인물끼리 칼끝이 닿으면 경계에서 자른다). 한 사람 옆에 떨어진 불꽃·구슬·늑대가 있는 그림은 한 자세로 본다.
- 칸에 맞추려고 15% 넘게 줄여야 하는 자세, 대기 자세 키의 절반 남짓도 안 되는 자세가 나오면 실패로 끝나고 등록하지 않는다 (`--grid` / `--poses`로 지정해 다시).
- 괴물 id에는 빈칸이 있을 수 있다 (`sheet/monster/사막 도적`). png 이름은 요청서의 파일 이름(`sheet_monster_desert-bandit.png`)을 쓴다.
- 직업 시트(`sheet/class/*`)는 아군·적군이 함께 쓰므로, 제복·장식에 쓴 색을 `register_sheet.py --tint-outfit '#7a1e2a,#4a101a' --tint-accent '#d9a441'`로 적어 두면 전투에서 진영 색으로 바꿔 칠한다. 적지 않으면 제복 색이 있는 병사는 코드 생성 도트로 그린다.
- 이름 뒤에 `@`이 붙은 후보(`sheet_x_y@123.png`)는 직접 지정할 때만 처리한다.
- `process.py`는 `sheet/*` 등 자기가 만들지 않은 manifest 항목을 건드리지 않는다.

### NovelAI (사용자가 원할 때만)
`python3 tools/art/novelai.py --only sheet/captain/ironwall` → `art/inbox/sheet_captain_ironwall.png` (한 자세, 마젠타 배경) → `sheets.py`.
기본값은 무료 범위(넓이 ≤ 1024×1024, 28 steps, 1장)이고, 더 큰 설정은 `--allow-paid` 없이는 거부한다. 한 번에 `--max` 2장.
토큰은 클라우드 세션의 프록시가 넣는다 (로컬에서는 `NOVELAI_TOKEN`). 대량 생성 금지.

## 단계
- **1단계 (완료)**: 용병대장 33명 · 특별 용병 7명 · 재앙 수장 2명 초상화, 이벤트 그림 9장 — 총 51장.
- 2단계 (예정): 전투 배경 7종, 길드 홀, 대륙 지도.
- **3단계 (진행)**: 전투 캐릭터 시트 — 창설 후보 대장 9 (+ 로드릭 기마, 선택) → 일반 병과 5 → 특별 용병 7 → 지역 몬스터 22 → 나머지 대장 24 (`phase3.md`).
  바렌(`sheet/captain/blademaster`)은 임시로 NovelAI 그림이 들어가 있다. GPT 의 승인된 바렌 그림이 오면 바꾼다.
- 4단계 (예정): 깃발·문장, 의뢰서·UI 장식, 장비 아이콘.
