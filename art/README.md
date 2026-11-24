# 그림 작업 우편함 (Art Mailbox)

이 폴더는 **그림을 만드는 쪽(ChatGPT / Codex 등)**과 **게임 코드를 맡은 쪽(Claude Code)**이 GitHub 저장소를 통해 그림을 주고받는 곳이다.

## 진행 방식
그림 쪽(ChatGPT / Codex)은 **그림만** 만든다. 요청서 작성, 후처리, 게임 연결, 화면 확인은 모두 코드 쪽(Claude Code)이 한다.
1. 사람이 그림 쪽에 "요청서의 이 묶음을 그려서 `art-inbox`에 올려 줘"라고 지시한다.
2. 그림 쪽이 `art/inbox/`에 PNG를 넣고 `art-inbox` 브랜치에 푸시한다.
3. 사람이 코드 쪽에 "올렸다"고 알리면, 코드 쪽이 받아서 처리한다.

## 그림을 만드는 쪽이 할 일

1. `art/STYLE.md`(화풍 기준), `art/requests/phase1.md`(그림 요청서), `art/requests/feedback.md`(피드백)를 읽는다.
   - 같은 내용의 기계용 목록은 `art/requests/phase1.json`.
   - 승인된 그림 `art/inbox/captain_blademaster.png`, `captain_ironwall.png`, `captain_tactician.png`를 화풍 기준 그림으로 쓴다.
2. 요청받은 묶음의 그림을 프롬프트로 생성한다.
   - 프롬프트는 화풍 기준을 지키는 범위에서 다듬어도 된다.
   - 초상화는 **배경 투명 PNG**.
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
3. 게임은 `manifest.json`에 있는 그림을 쓰고, 없는 그림은 기존 코드 생성 도트로 대신한다. 그래서 일부만 들어와도 게임이 깨지지 않는다.
4. 화면에서 확인한 뒤 고칠 점과 다음 묶음을 `art/requests/feedback.md`에 적어 푸시한다.

## 단계
- **1단계 (완료)**: 용병대장 33명 · 특별 용병 7명 · 재앙 수장 2명 초상화, 이벤트 그림 9장 — 총 51장.
- 2단계 (예정): 전투 배경 7종, 길드 홀, 대륙 지도.
- 3단계 (예정): 깃발·문장, 의뢰서·UI 장식, 장비 아이콘.
