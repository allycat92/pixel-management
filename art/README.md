# 그림 작업 우편함 (Art Mailbox)

이 폴더는 **그림을 만드는 쪽(ChatGPT / Codex 등)**과 **게임 코드를 맡은 쪽(Claude Code)**이 GitHub 저장소를 통해 그림을 주고받는 곳이다.

## 자동 왕복 (PR 창구)

그림 쪽과 코드 쪽은 **Draft PR 「Art mailbox」**를 창구로 쓴다. 이 PR은 병합하지 않는다.
1. 코드 쪽이 PR에 `@codex` 댓글로 다음 묶음(파일 목록)을 요청한다.
2. 그림 쪽은 그 묶음을 생성해 `art/inbox/`에 넣고, **이 PR의 브랜치(`claude/dot-fantasy-management-game-saupju`)에 커밋·푸시**한 뒤 PR에 납품 댓글을 단다.
3. 푸시가 일어나면 코드 쪽이 자동으로 깨어나 후처리·게임 연결·화면 확인을 하고, 피드백과 다음 묶음을 다시 `@codex` 댓글로 남긴다.
4. 51장이 끝나면 코드 쪽이 완료 댓글을 남기고 왕복을 멈춘다.

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
5. 커밋해서 **PR 브랜치에 푸시**하고, PR에 짧은 납품 댓글을 단다.
   - **`art/inbox/` 밖의 파일은 고치지 않는다.** (`js/`, `css/`, `index.html`, `assets/`, `tools/`, `art/requests/` 모두 코드 쪽 담당)
   - 푸시 전에 브랜치를 최신으로 받아(pull) 충돌을 피한다.

> 이미지를 직접 생성할 수 없는 환경이라면, PR에 그 사실을 댓글로 남긴다. 사람이 ChatGPT 이미지 생성으로 만든 파일을 같은 이름으로 `art/inbox/`에 올려도 된다.

## 코드 쪽(Claude Code)이 할 일

1. PR 브랜치에 들어온 `art/inbox/`의 새 그림을 확인한다.
2. `python3 tools/art/process.py`로 후처리한다.
   - 배경 제거(단색 배경일 때), 여백 자르기, 축소, 팔레트 정리.
   - `assets/art/`에 저장하고 `assets/art/manifest.json`을 갱신한다.
3. 게임은 `manifest.json`에 있는 그림을 쓰고, 없는 그림은 기존 코드 생성 도트로 대신한다. 그래서 일부만 들어와도 게임이 깨지지 않는다.
4. 화면에서 확인한 뒤 고칠 점과 다음 묶음을 `art/requests/feedback.md`에 적어 푸시하고, PR에 `@codex` 댓글로 요청한다.

## 단계
- **1단계 (현재)**: 용병대장 33명 · 특별 용병 7명 · 재앙 수장 2명 초상화, 이벤트 그림 9장 — 총 51장.
- 2단계 (예정): 전투 배경 7종, 길드 홀, 대륙 지도.
- 3단계 (예정): 깃발·문장, 의뢰서·UI 장식, 장비 아이콘.
