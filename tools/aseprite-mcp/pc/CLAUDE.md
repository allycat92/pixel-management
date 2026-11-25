# PC 세션 지침 — pixel-management 도트 손질·뼈대 담당 (Aseprite)

지침 판: 2026-11-26b  (보고할 때 이 판을 함께 말한다 — 클라우드가 PC 가 낡은 지침으로 일하는지 알 수 있다)

**모든 답변·질문·보고는 한국어로 한다.** 영어 문서를 읽더라도 주인에게는 한국어로 말한다. 짧고 쉽게.

## 너의 역할
맡는 일은 두 가지뿐이다.
1. **손질**: 이미 받은 전투 시트 PNG 를 정품 Aseprite 로 지시된 만큼만 고친다.
2. **뼈대**: `art/requests/guides/<id>/README.md` 가 시킨 자세 가이드(마네킹)를 만들거나 다듬는다 (`art/requests/guides/SPEC.md`).
캐릭터 그림을 처음부터 그리는 일은 하지 않는다 (GPT 담당).

## 할 일 고르기
1. 이 폴더에서 `git pull`. 납품 폴더는 `git -C ../pixel-management-inbox pull --rebase origin art-inbox`.
   - `git pull` 결과에 `tools/aseprite-mcp/pc/CLAUDE.md` 가 바뀌었다고 나오면 이 파일을 다시 읽는다. `settings.local.json` 이 바뀌었으면 주인에게 "설정 파일을 다시 복사해 달라"고 한 줄 알린다.
2. `art/requests/pc_notes.md` 를 처음부터 끝까지 읽는다 (짧다. 늘 지키는 규칙). 「한 번만 할 일」이 있으면 그것부터.
3. `art/requests/dot_queue.md` 에서 상태 칸에 **`담당: PC(Aseprite)`** 가 붙은 항목만, 위에서부터 하나씩 (DOT_READY·NEEDS_FIX 둘 다).
   - 표시가 없는 항목은 상태가 무엇이든 GPT 몫이라 **건드리지 않는다**.
   - 손질 항목은 메모 칸의 `바탕: art-inbox <해시>` 가 지금 그 파일의 마지막 커밋과 같은지 본다:
     `git -C ../pixel-management-inbox log -1 --format=%h -- art/inbox/<파일>.png`. 다르면 손대지 않고 알린다.
   - 표시된 항목이 없으면 "할 일 없음" 이라고 한 줄 알리고 멈춘다.
4. 무엇을 할지는 그 줄의 「요청서」 칸과 「메모」 칸이 가리키는 파일에 있다. 다른 문서와 다르면 대기열 줄이 우선한다.
   (지난 납품에 대한 클라우드의 답이 궁금하면 `art/requests/feedback.md` 에서 제목에 「PC」 가 든 맨 아래 절 — 지시는 아니다.)

## 두 가지 일의 이름 규칙
| 일 | 파일 (납품 폴더 안) | NOTES 절 제목 | 커밋 첫 줄 (영어, 본문 없음) |
|---|---|---|---|
| 손질 | `art/inbox/<stem>.png` + `art/inbox/aseprite/<stem>.aseprite` | 「손질 — <이름> (Aseprite)」 | `Touch up <stem> (Aseprite)` |
| 뼈대 | `art/inbox/guides/<id>/` 안에 PNG·`.aseprite`·GIF 모두 | 「뼈대 — <이름> (Aseprite)」 | `Add guide <id> (Aseprite)` / 고칠 때 `Touch up guide <id> (Aseprite)` |
`<stem>` 은 파일 이름에서 `.png` 를 뺀 것 그대로 (예: `sheet_monster_desert-bandit`).

## 명령 습관 (허가 창 줄이기)
- 납품 폴더의 git 은 항상 `git -C ../pixel-management-inbox <명령>` 꼴로, 경로는 `/` 로 쓴다 (`\` 는 Git Bash 에서 깨진다).
- `cd`·셸 변수(`S=...`, `$A`)·반복문(`for`)·`&&` 로 잇기·`python -c "..."` 긴 코드는 쓰지 않는다 — 허가 창이 뜬다. 한 줄에 명령 하나.
- Aseprite 실행 파일을 직접 부르지 않는다. 내보내기와 검사는 아래 한 줄이 같이 한다 (`ASEPRITE_PATH` 는 설정에 들어 있다).

## 작업 방법
- 손질의 바탕: 납품 폴더의 `art/inbox/<stem>.png` (지금 들어가 있는 그림). 자세·윤곽·크기·위치는 **그대로** 두고 지시된 것만 고친다.
- 규칙: 발 기준선·여백 유지, 인물 색은 #FF00FF 와 RGB 거리 170 이상, 40색 안팎·또렷한 가장자리, 무기는 몸 실루엣 바깥.
- 레이어·점 색·보이는 크기·물어야 하는 것: `art/requests/pc_notes.md`.
- 스크립트·중간 그림은 `~/Documents/pm-pc-scratch/` 에만 둔다. aseprite 도구에는 항상 **절대 경로**(납품 폴더와 그 스크래치 폴더 안). 막혀 있는 도구(run_lua_script, audit_animation, animation_sanitize, start/stop_preview_server)는 쓰지 않는다.
- NovelAI 그림(concept.png)과 `art/refs` 의 참고 그림은 눈으로만 본다. 픽셀을 가져오거나 레이어로 넣지 않는다.

## 납품
1. 내보내기 + 자체 검사를 한 줄로 (이 폴더에서; 2x2·점 색·칸 크기는 도구가 요청서에서 스스로 찾는다):
   `uv run --no-project --with pillow python tools/art/check_delivery.py ../pixel-management-inbox/art/inbox/<stem>.png --aseprite ../pixel-management-inbox/art/inbox/aseprite/<stem>.aseprite --export --base-rev <바탕 해시>`
   - **새로 생긴 FAIL 이 있으면 푸시하지 않는다.** `pre-existing`(받은 그림에도 있던 것)은 NOTES 에 "원래부터" 라고 적고 그대로 둔다.
   - 맨 아래 `against the base:` 줄(윤곽·색이 몇 px 바뀌었나)과 `RESULT` 줄을 NOTES 에 옮겨 적는다.
   - **뼈대**는 원본이 PNG 옆에 있고 바탕 해시가 없다. 띠마다: `uv run --no-project --with pillow python tools/art/check_delivery.py ../pixel-management-inbox/art/inbox/guides/<id>/<파일>.png --aseprite ../pixel-management-inbox/art/inbox/guides/<id>/<파일>.aseprite --export`
2. `art/inbox/NOTES.md` 에 절을 붙인다 (제목과 줄 순서: `pc_notes.md` 맨 아래).
3. `git -C ../pixel-management-inbox status` 로 `art/inbox/` 안만 바뀌었는지 확인 → `add art/inbox` → `commit -m "<위 표의 첫 줄>"` → `pull --rebase origin art-inbox` → `push origin art-inbox`.
   - `pull --rebase` 가 충돌로 멈추면: NOTES.md 뿐이면 양쪽 절을 모두 남기고 `rebase --continue`.
     (`art/inbox/.gitattributes` 의 합치기 설정 덕에 NOTES.md 는 대개 저절로 합쳐진다.)
     **PNG·.aseprite 가 충돌하면 풀지 않는다** — `rebase --abort` 하고 "○○ 파일을 다른 쪽이 먼저 바꿨음" 이라고 알리고 멈춘다.
4. 주인에게 한국어로 한 줄 보고 ("○○ 손질 올림, 커밋 abc1234, 지침 판 2026-11-26b") 후 다음 항목.

## 하지 않는 것
- 게임 브랜치(이 폴더) 커밋·푸시, `art/inbox/` 밖 수정, dot_queue.md·feedback.md·pc_notes.md 수정 (클라우드가 바꾼다).
- 강제 푸시, Aseprite 프로그램 파일을 저장소에 넣기, 토큰·비밀번호를 파일에 쓰기, aseprite-mcp 업데이트.
- 확실하지 않을 때의 기준은 `pc_notes.md` 「스스로 정해도 되는 것 / 물어야 하는 것」.
