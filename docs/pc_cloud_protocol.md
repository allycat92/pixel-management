# PC 세션 ↔ 클라우드 세션 작업 약속 (pc_cloud_protocol)

주인이 산 **Aseprite 는 Windows PC** 에 있고, 클라우드 세션은 그 PC 에 닿지 못한다.
그래서 일을 둘로 나누고, 둘은 **GitHub 저장소로만** 파일을 주고받는다.

```
 PC 세션 (Windows, 정품 Aseprite + aseprite-mcp)          클라우드 세션 (게임 코드)
 ─────────────────────────────────────────────          ───────────────────────────────
 읽기: 게임 브랜치의 dot_queue·요청서·가이드·feedback  ◀──  게임 브랜치에 요청서·대기열·피드백을 올림
 그리기: Aseprite 로 도트 작업                                    │
 쓰기: art-inbox 브랜치 art/inbox/ 에 .aseprite + PNG  ──▶  art-inbox 를 받아 검사 → 시트 등록
                                                              dot_queue·feedback 갱신 → 게임 브랜치
```

## 1. 역할

| | PC 세션 | 클라우드 세션 |
|---|---|---|
| 어디서 | 주인 PC 의 게임 저장소 폴더. Claude Desktop(Code) 또는 `claude` / `claude remote-control` | claude.ai 클라우드 컨테이너 |
| 도구 | 정품 Aseprite + aseprite-mcp (`tools/aseprite-mcp/README.md`, 위험 도구 5개 deny) | 게임 코드, `tools/art/*`, 머리 없는(headless) Aseprite 빌드 |
| 하는 일 | `dot_queue.md` 의 차례인 항목을 Aseprite 로 그리거나 손봐서 납품 | 요청서·가이드·대기열 관리, 납품 검사, `sheets.py` 등록, 게임 연결, 피드백, 코드 리뷰 |
| 쓰는 곳 | **`art-inbox` 브랜치의 `art/inbox/` 만** | 게임 브랜치 `claude/dot-fantasy-management-game-saupju` (그리고 art-inbox 는 읽기만) |
| 하지 않는 일 | 게임 브랜치에 푸시, `dot_queue.md`·`feedback.md`·`js/`·`assets/`·`tools/` 수정, 시트 등록 | PC 의 파일·프로그램을 직접 만지는 일 (닿지 않는다) |

- 어떤 항목을 PC 가 맡을지(처음부터 그리기 / GPT 납품 손질하기)는 **주인이 정하고**, 클라우드가 `dot_queue.md` 메모 칸에 `담당: PC(Aseprite)` 처럼 적는다.
  메모에 담당이 없으면 PC 는 위에서부터 `DOT_READY` 를 맡는다.
- `AGENTS.md` 의 그림 규칙은 그대로다: **NovelAI 그림은 디자인 초안 전용** — 픽셀을 가져오거나 레이어로 넣지 않는다 (`concept.png` 는 눈으로 보는 참고만).

## 2. 브랜치와 폴더

PC 에는 같은 저장소를 **폴더 두 개**로 둔다 (git worktree — 한 번만 만들면 된다):

```powershell
cd $HOME\Documents\pixel-management                     # 게임 브랜치 (읽기 전용으로 쓴다)
git checkout claude/dot-fantasy-management-game-saupju
git fetch origin art-inbox
git worktree add ..\pixel-management-inbox art-inbox    # 납품용 폴더 (art-inbox 브랜치)
```

| 폴더 | 브랜치 | PC 세션이 하는 일 |
|---|---|---|
| `pixel-management` | `claude/dot-fantasy-management-game-saupju` | `git pull` 로 최신 대기열·요청서를 읽는다. **커밋·푸시하지 않는다.** |
| `pixel-management-inbox` | `art-inbox` | `art/inbox/` 에 납품 파일을 쓰고 커밋·푸시한다. |

- art-inbox 에는 다른 그림 쪽(GPT 등)도 푸시한다 → 푸시 전 언제나 `git pull --rebase origin art-inbox`. **강제 푸시(`--force`) 금지.**
- 클라우드는 art-inbox 를 읽기만 하고, 결과(시트·manifest·대기열·피드백)는 게임 브랜치에 올린다.

## 3. 파일 이름

납품 이름은 `dot_queue.md` 표의 **납품 PNG 이름 그대로** 쓴다. 그 이름에서 `.png` 를 뺀 것을 `<stem>` 이라 한다.

| 무엇 | 경로 (art-inbox) | 예 (`sheet/hero/lyra`) |
|---|---|---|
| 납품 PNG | `art/inbox/<stem>.png` | `art/inbox/sheet_hero_lyra.png` |
| Aseprite 원본 | `art/inbox/aseprite/<stem>.aseprite` | `art/inbox/aseprite/sheet_hero_lyra.aseprite` |
| 납품 메모 | `art/inbox/NOTES.md` 의 절 | 「3단계 — 리라 (Aseprite)」, 다시 그리면 「리라 — 다시 그림 (Aseprite)」 |

**PNG 규격** (요청서 README 의 DELIVERABLE·SELF-CHECK 와 같다):
1536×1024 RGB, 평평한 `#FF00FF` 배경, 자세 4개 한 줄(README 가 2x2 라고 하면 768×512 칸 4개), 발바닥(가장 아래 픽셀) y=870 (2x2 는 칸마다 y=461),
자세 사이·가장자리 32px 이상, 인물 색은 `#FF00FF` 와 거리 150 이상(170 이상 권장), 40색 안팎의 또렷한 픽셀(부드러운 가장자리 없음),
무기·소품은 64px 로 줄여도 보이게 몸 실루엣 바깥 배경 위에 (feedback.md 의 공통 규칙).

**`.aseprite` 원본 규칙**:
- 캔버스 1536×1024, RGB, 프레임 1개. 내보내면 **납품 PNG 와 픽셀 하나까지 같아야** 한다 (클라우드가 비교한다).
- 맨 아래 배경 레이어(Aseprite 의 `Background`) = 불투명 `#FF00FF` 로 꽉 채움. 그 위에 인물 레이어 (예: `pose1_idle`, `pose2_windup`, `pose3_strike`, `pose4_hit`).
- 가이드·참고 그림 레이어는 작업 중에만 쓰고 **커밋 전에 지운다** (파일이 가벼워지고, NovelAI 초안이 원본에 섞이지 않는다).
- 파일·레이어 이름은 영문.

## 4. dot_queue 상태 — 누가 무엇을

`art/requests/dot_queue.md` (게임 브랜치) 가 차례를 정한다. **상태는 클라우드만 바꾼다.**

| 상태 | PC 세션 | 클라우드 세션 |
|---|---|---|
| `QUEUED` | 그리지 않는다 | 차례가 되면 `DOT_READY` 로 올린다 |
| `DOT_READY` | 위에서부터 하나씩 그려 납품 | 납품이 오면 `DELIVERED` |
| `DELIVERED` | 건드리지 않는다 (검사 중) | 검사 → `ACCEPTED` 또는 `NEEDS_FIX` |
| `NEEDS_FIX` | `feedback.md` 의 해당 절을 읽고 같은 이름으로 다시 납품 (`.aseprite` 도 함께 갱신) | 다시 검사 |
| `ACCEPTED` | 건드리지 않는다 | 등록 끝 |

- PC 가 고를 때: 메모에 `담당: PC(Aseprite)` 인 항목 → 없으면 위에서부터 `DOT_READY` → 그다음 `NEEDS_FIX`.
- art-inbox 에 그 이름의 PNG 가 마지막 피드백보다 **새로 올라와 있으면** 다른 그림 쪽이 이미 납품한 것 → 건너뛴다.
- `DOT_READY`·`NEEDS_FIX` 가 없으면 멈추고 주인에게 알린다.
- PC 는 납품 뒤 주인에게 "올렸다(커밋 해시)" 라고 말한다. 주인이 클라우드에 전하거나, 클라우드가 art-inbox 를 주기적으로 확인한다.

## 5. 커밋 메시지

**PC (art-inbox)** — 첫 줄은 영어, 짧게:
```
Deliver Lyra battle sheet (Aseprite)
Redeliver Lyra battle sheet (Aseprite): dagger outside the silhouette
```
본문: dot_queue id (`sheet/hero/lyra`), 넣은 파일, 자체 검사 결과 줄(`RESULT: PASS ...`).

**클라우드 (게임 브랜치)** — 지금처럼: `Dot loop: <무엇> ...`, `Accept and register <누구> ...`, 도구 변경은 그 내용대로.

## 6. PC 가 푸시하기 전에 할 일

1. Aseprite 에서 PNG 를 내보낸다 (보이는 레이어만 합쳐진다):
   ```powershell
   $INBOX = "$HOME\Documents\pixel-management-inbox"     # 납품 폴더 (2절에서 만든 worktree)
   & "C:\Program Files\Aseprite\Aseprite.exe" -b "$INBOX\art\inbox\aseprite\sheet_hero_lyra.aseprite" --save-as "$INBOX\art\inbox\sheet_hero_lyra.png"
   ```
   (Steam 판은 Aseprite 경로를 바꾼다: `setup_windows.ps1` 이 찾아 준 경로.)
2. **자체 검사** (게임 브랜치 폴더에서; 마젠타 거리·크기·자세 수·발 높이·여백·색 수·원본과 PNG 가 같은지):
   ```powershell
   cd $HOME\Documents\pixel-management
   uv run --no-project --with pillow python tools\art\check_delivery.py "$INBOX\art\inbox\sheet_hero_lyra.png" `
     --aseprite "$INBOX\art\inbox\aseprite\sheet_hero_lyra.aseprite" --aseprite-exe "C:\Program Files\Aseprite\Aseprite.exe"
   ```
   2x2 몬스터는 `--layout 2x2`. **`RESULT: FAIL` 이면 푸시하지 않는다.** `WARN` 은 메모에 이유를 적으면 된다.
3. 게임 크기로 줄여 보기: `view_sprite` 나 Aseprite 에서 1/6 크기(약 64px 키)로 보고, 무기·얼굴이 읽히는지 본다.
4. `art/inbox/NOTES.md` 에 절 추가: 만든 파일, 가이드와 다르게 한 점, 다시 그리고 싶은 점, 검사 결과 줄.
5. `git status` 로 **`art/inbox/` 안의 파일만** 바뀌었는지 확인 → 커밋 → `git pull --rebase origin art-inbox` → `git push origin art-inbox`.

## 7. 클라우드가 받은 납품을 처리하는 법

클라우드에는 머리 없는 Aseprite 빌드가 있다 (`/home/user/aseprite-build/src/build/bin/aseprite`, 만드는 법 `tools/aseprite/README.md`;
저장소에 없고 컨테이너가 바뀌면 다시 빌드). aseprite-mcp 는 클라우드에서 쓰지 않는다 — Aseprite 명령줄만 쓴다.

```bash
git fetch origin art-inbox
T=<스크래치 폴더>; mkdir -p $T/ase $T/in
git show origin/art-inbox:art/inbox/sheet_hero_lyra.png > $T/in/sheet_hero_lyra.png
git show origin/art-inbox:art/inbox/aseprite/sheet_hero_lyra.aseprite > $T/in/sheet_hero_lyra.aseprite
ASE=/home/user/aseprite-build/src/build/bin/aseprite
export HOME=$T/ase XDG_CONFIG_HOME=$T/ase/c ASEPRITE_USER_FOLDER=$T/ase/a; unset DISPLAY WAYLAND_DISPLAY   # 버리는 프로필
# 원본 살펴보기 (레이어·태그·크기)
$ASE -b --list-layers --list-tags $T/in/sheet_hero_lyra.aseprite --data $T/in/info.json --format json-array --sheet $T/in/flat.png
# 규격 + 원본==PNG
python3 tools/art/check_delivery.py $T/in/sheet_hero_lyra.png --aseprite $T/in/sheet_hero_lyra.aseprite --aseprite-exe $ASE
```
- 검사가 통과하면 평소대로: `sheets.py ... --dry-run` 으로 미리보기 → 검토 → 등록 (`art/README.md` 「전투 캐릭터 시트」) → `dot_queue.md` 상태와 `feedback.md` 갱신 → 게임 브랜치에 푸시.
- PNG 와 원본이 다르면 `NEEDS_FIX` ("PNG 를 원본에서 다시 내보낼 것"). PNG 가 빠졌으면 클라우드가 원본에서 내보내 검사해도 되지만, 피드백에 적어 다음부터 둘 다 올리게 한다.
- `.aseprite` 원본은 art-inbox 에만 둔다 (게임 브랜치로 옮기지 않는다). 피드백에서 레이어 이름으로 고칠 곳을 가리킬 수 있다.

## 8. PC 세션에 처음 붙여 넣을 지시

PC 의 게임 저장소 폴더에서 Claude 를 연 뒤 첫 메시지로 붙여 넣는다.
(매번 붙이기 번거로우면 같은 내용을 그 폴더의 `CLAUDE.local.md` 로 저장하고, `.git\info\exclude` 에 `CLAUDE.local.md` 한 줄을 넣어 커밋되지 않게 한다.)

```markdown
# 너의 역할: pixel-management 의 PC 도트 담당 (Aseprite)

- 이 PC(Windows)에는 정품 Aseprite 와 aseprite-mcp(MCP 서버 이름 `aseprite`)가 있다. 게임 코드는 클라우드의 다른 Claude 세션이 맡는다.
  그 세션은 이 PC 에 닿지 못한다. 서로는 GitHub 저장소로만 주고받는다. 약속 전체: docs/pc_cloud_protocol.md.
- 폴더: 게임 브랜치 = 이 폴더(`claude/dot-fantasy-management-game-saupju`, 읽기만, 커밋·푸시 금지),
  납품 = `..\pixel-management-inbox` (art-inbox 브랜치 worktree; 없으면 docs/pc_cloud_protocol.md 2절대로 만든다).

## 시작할 때마다
1. 이 폴더에서 `git pull`, 납품 폴더에서 `git pull --rebase origin art-inbox`.
2. 읽기: AGENTS.md, art/README.md, art/requests/dot_queue.md, art/requests/gpt_handoff_notes.md, art/requests/feedback.md(최근 절),
   맡을 항목의 art/requests/phase3/<id>/README.md 와 guide_strip.png, portrait.png, 화풍 기준(앵커) 시트.
3. 맡을 항목 고르기: 메모에 `담당: PC(Aseprite)` → 없으면 위에서부터 `DOT_READY` → 그다음 `NEEDS_FIX`(feedback.md 의 고칠 점만).
   QUEUED·DELIVERED·ACCEPTED 는 건드리지 않는다. 할 것이 없으면 멈추고 알려 준다.
   어떤 항목을 고를지·무엇을 그릴지 애매하면 시작 전에 묻는다.

## 작업
- 원본: `<납품폴더>\art\inbox\aseprite\<stem>.aseprite` (stem = 대기열의 납품 PNG 이름에서 .png 뺀 것).
  1536x1024 RGB, 프레임 1개, 맨 아래 `Background` 레이어를 불투명 #FF00FF 로, 그 위에 자세별 레이어. 영문 이름.
- 규격: 요청서 README 의 DELIVERABLE·SELF-CHECK 그대로 (1x4 또는 README 가 말하면 2x2, 발 y=870, 여백 32px+,
  #FF00FF 와 거리 170 이상, 40색 안팎·또렷한 가장자리, 무기는 몸 실루엣 바깥 배경 위).
- aseprite 도구에는 언제나 **절대 경로**. 게임 저장소 밖에 파일을 쓰지 않는다.
- 쓰지 않는 도구: run_lua_script, audit_animation, animation_sanitize, start_preview_server, stop_preview_server (막혀 있다 — 우회하지 말 것).
- NovelAI 그림(concept.png, nai_*)은 보기만 한다. 픽셀을 가져오거나 레이어로 넣지 않는다.
- 가이드·참고 레이어는 작업 중에만, 커밋 전에 지운다.

## 납품 (docs/pc_cloud_protocol.md 6절)
1. Aseprite 명령줄로 PNG 내보내기: `Aseprite.exe -b <원본> --save-as <납품폴더>\art\inbox\<stem>.png`
2. 자체 검사: 이 폴더에서
   `uv run --no-project --with pillow python tools\art\check_delivery.py <PNG> --aseprite <원본> --aseprite-exe <Aseprite.exe>`
   (2x2 는 --layout 2x2). FAIL 이면 고친다 — 푸시하지 않는다.
3. 게임 크기(약 1/6)로 줄여 보고 무기·얼굴이 읽히는지 확인.
4. art/inbox/NOTES.md 에 「3단계 — <이름> (Aseprite)」 절: 만든 파일, 가이드와 다른 점, 다시 그리고 싶은 점, 검사 결과 줄.
5. 납품 폴더에서 art/inbox/ 안만 바뀌었는지 확인 → 커밋 (`Deliver <Name> battle sheet (Aseprite)`) →
   `git pull --rebase origin art-inbox` → `git push origin art-inbox`. 강제 푸시 금지.
6. 주인에게 "올렸다 (커밋 해시, 파일)" 라고 알리고, DOT_READY 가 더 있으면 다음 항목으로.

## 하지 않는 것
- 게임 브랜치 커밋·푸시, art/inbox/ 밖 수정, dot_queue.md·feedback.md 수정 (상태는 클라우드가 바꾼다).
- Aseprite 프로그램 파일을 저장소에 넣기 (EULA). 토큰·비밀번호를 파일에 쓰기.
- tools/aseprite-mcp 의 고정 커밋 바꾸기, aseprite-mcp 업데이트 (클라우드가 검토한 뒤에만).
```
