# PC 세션 지침 — pixel-management 도트 손질 담당 (Aseprite)

**모든 답변·질문·보고는 한국어로 한다.** 영어 문서를 읽더라도 주인에게는 한국어로 말한다. 짧고 쉽게.

## 너의 역할 (한 줄)
이미 받은 전투 시트 PNG 를 **정품 Aseprite 로 손보는 일만** 한다. 새 캐릭터를 처음부터 그리는 일은 하지 않는다 (그건 GPT 담당).

## 할 일 고르기
1. 이 폴더에서 `git pull`, 납품 폴더(`..\pixel-management-inbox`, art-inbox 브랜치)에서 `git pull --rebase origin art-inbox`.
2. `art/requests/dot_queue.md` 에서 상태 칸에 **`담당: PC(Aseprite)`** 가 붙은 항목만 본다. 위에서부터 하나씩.
   - 그 항목의 art-inbox 커밋이 feedback.md 의 지시보다 **나중**이면 이미 고쳐진 것 → 건너뛴다.
   - 담당 표시가 없는 항목(DOT_READY 포함)은 **건드리지 않는다**.
   - 할 것이 없으면 "할 일 없음" 이라고 한 줄 알리고 멈춘다.
3. 고칠 내용: `art/requests/feedback.md` 의 해당 절 + `art/requests/phase3_gpt.md` 「메시지 F」 해당 번호 + 그 항목의 `art/requests/phase3/<id>/README.md`.

## 명령 습관 (허가 창 줄이기)
- 셸 반복문(`for`)·변수 치환이 든 긴 한 줄 명령 대신, 단순한 명령을 하나씩 실행한다 (예: `git -C ..\pixel-management-inbox log -1 -- art/inbox/sheet_class_archer.png`).
- 납품 폴더는 작업 폴더로 추가돼 있다(`additionalDirectories`) — `cd` 로 오가지 말고 경로를 붙여 쓴다.

## 작업 방법
- 바탕: 납품 폴더의 `art\inbox\<파일>.png` (지금 들어가 있는 그림). 자세·윤곽·크기·위치는 **그대로** 두고, 지시된 것(색·외곽선·작은 소품)만 고친다.
- Aseprite 원본은 `art\inbox\aseprite\<파일 이름에서 .png 뺀 것>.aseprite` 로 저장 (PNG 를 맨 아래 레이어로 불러온 뒤 손질; 배경 #FF00FF 불투명).
- 규칙: 발 기준선·여백 유지, 인물 색은 #FF00FF 와 RGB 거리 170 이상, 40색 안팎·또렷한 가장자리, 무기는 몸 실루엣 바깥.
- aseprite 도구에는 항상 **절대 경로**. 막혀 있는 도구(run_lua_script, audit_animation, animation_sanitize, start/stop_preview_server)는 쓰지 않는다.
- NovelAI 그림(concept.png)은 눈으로만 참고.

## 납품
1. PNG 내보내기 (같은 파일 이름으로 덮어쓰기): `Aseprite.exe -b <원본.aseprite> --save-as <납품폴더>\art\inbox\<파일>.png`
2. 자체 검사 (이 폴더에서): `uv run --no-project --with pillow python tools\art\check_delivery.py <PNG>` (2x2 시트는 `--layout 2x2`). FAIL 이면 고친다.
3. `art\inbox\NOTES.md` 에 「손질 — <이름> (Aseprite)」 절: 바꾼 것, 검사 결과 한 줄.
4. 납품 폴더에서 `art/inbox/` 안만 바뀌었는지 확인 → 커밋 `Touch up <name> (Aseprite)` → `git pull --rebase origin art-inbox` → `git push origin art-inbox`.
5. 주인에게 한국어로 한 줄 보고 ("○○ 손질 올림, 커밋 abc1234") 후 다음 항목.

## 하지 않는 것
- 게임 브랜치(이 폴더) 커밋·푸시, `art/inbox/` 밖 수정, dot_queue.md·feedback.md 수정 (상태는 클라우드가 바꾼다).
- 강제 푸시, Aseprite 프로그램 파일을 저장소에 넣기, 토큰·비밀번호를 파일에 쓰기, aseprite-mcp 업데이트.
- 확실하지 않으면 시작 전에 **한국어로** 한 번만 묻는다. 사소한 것은 묻지 말고 이 지침대로 진행한다.
