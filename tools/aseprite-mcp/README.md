# aseprite-mcp 설치 (Windows PC 용)

PC 의 Claude 가 **정품 Aseprite** 를 직접 다루게 해 주는 연결 도구(MCP 서버) [diivi/aseprite-mcp](https://github.com/diivi/aseprite-mcp) 를 설치하는 방법이다.
PC 세션과 클라우드 세션이 어떻게 나눠 일하는지는 [`docs/pc_cloud_protocol.md`](../../docs/pc_cloud_protocol.md) 를 본다.

- 설치하는 버전은 **검토를 마친 커밋 `4bcdb6f5932116bbdbd1b7d3fcc1e8f965f7657a`** (2026-11-04) 로 고정된다. 새 버전은 다시 검토한 뒤에만 올린다.
- 이 폴더의 파일:
  - `setup_windows.ps1` — 설치·등록을 한 번에 하는 스크립트 (여러 번 실행해도 안전, 관리자 권한 필요 없음)
  - `claude_desktop_config.example.json` — Claude Desktop 채팅용 설정 견본 (스크립트가 `-Desktop` 으로 대신 써 준다)
- 납품 전 자체 검사는 `tools/art/check_delivery.py` (아래 「납품 전 검사」).

## 준비물

| 무엇 | 확인 방법 | 없으면 |
|---|---|---|
| Aseprite (Steam 판 또는 설치판) | 한 번 실행해 본다 | 산 곳에서 설치 |
| Git for Windows | PowerShell 에 `git --version` | https://git-scm.com/download/win 또는 `winget install --id Git.Git -e` |
| Claude Code 또는 Claude Desktop | `claude --version` / 앱 실행 | Claude Code: https://claude.com/claude-code |
| 게임 저장소 복사본 | `C:\...\pixel-management` 폴더 | `git clone` 으로 받기 (아래 1번) |

uv(파이썬 도구)와 Python 3.13 은 스크립트가 알아서 받는다.

## 설치 (처음 한 번)

1. **PowerShell 열기**: 시작 메뉴에서 `PowerShell` 을 검색해 연다 (관리자 아님, 그냥 실행).
2. **게임 저장소 폴더로 이동** (저장소가 아직 없으면 먼저 받는다):
   ```powershell
   cd $HOME\Documents
   git clone https://github.com/allycat92/pixel-management.git   # 이미 있으면 건너뜀 (처음이면 GitHub 로그인 창이 뜬다)
   cd pixel-management
   git checkout claude/dot-fantasy-management-game-saupju
   git pull
   ```
3. **스크립트 실행**:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\aseprite-mcp\setup_windows.ps1
   ```
   - Claude Desktop **채팅**에서도 쓰려면 끝에 ` -Desktop` 을 붙인다.
   - Aseprite 를 못 찾는다고 하면 경로를 직접 준다 (Steam: 라이브러리에서 Aseprite 우클릭 → 관리 → 로컬 파일 보기):
     ```powershell
     powershell -ExecutionPolicy Bypass -File .\tools\aseprite-mcp\setup_windows.ps1 -AsepritePath "D:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe"
     ```
   - 읽기 전용 도구(픽셀 읽기·정보 보기)를 매번 묻지 않게 하려면 ` -AllowReadOnly`.
4. 스크립트가 하는 일 (화면에 단계별로 나온다):
   1. git 확인, uv 가 없으면 공식 설치 스크립트(`irm https://astral.sh/uv/install.ps1 | iex`)로 설치
   2. `%USERPROFILE%\tools\aseprite-mcp` 에 받아서 검토한 커밋으로 고정 (커밋을 못 찾으면 멈춤)
   3. Aseprite.exe 찾기 (Program Files, Steam 기본·추가 라이브러리, `%LOCALAPPDATA%\Programs`) → 설치 폴더의 `.env` 작성
   4. `uv sync` (잠금 파일 그대로) → 자체 시험: 파이썬에서 불러오기(도구 수, 막을 도구 5개 확인) + `Aseprite.exe --batch --version`
   5. Claude Code 에 등록: `claude mcp add aseprite --scope user ...` + 위험한 도구 5개를 `%USERPROFILE%\.claude\settings.json` 의 `permissions.deny` 에 추가 (원래 파일은 `.bak-날짜` 로 백업)
   6. `-Desktop` 이면 `%APPDATA%\Claude\claude_desktop_config.json` 에도 추가 (백업 후)
5. **Claude 를 완전히 껐다 켠다** (Desktop 은 트레이 아이콘에서 종료까지; `claude` 창은 닫고 새로).

> "이 시스템에서 스크립트를 실행할 수 없으므로…" 가 나오면 3번 명령을 그대로 쓴다 (`-ExecutionPolicy Bypass` 가 이번 한 번만 허용한다).
> 그래도 막히면 `Unblock-File .\tools\aseprite-mcp\setup_windows.ps1` 후 다시 실행.

## 잘 붙었는지 확인

1. 게임 저장소 폴더에서 `claude` 를 실행하고 `/mcp` 를 입력 → `aseprite` 가 **connected** 이고 도구가 120개 남짓.
   (Desktop 채팅: 입력창 아래 도구(연결) 메뉴에 `aseprite` 가 보이면 된다.)
2. 시험 요청 (경로는 꼭 **절대 경로**):
   > aseprite 도구로 C:\Users\<나>\Documents\pixel-management\art\test\smoke.aseprite 에 64x64 캔버스를 만들고, get_sprite_info 로 정보를 보여 줘. run_lua_script 는 쓰지 마.
3. 파일이 생기고 크기 64x64 가 나오면 끝. `art/test/` 같은 시험 파일은 커밋하지 않는다.

## 업데이트 / 삭제

- **스크립트를 다시 실행**하면 같은 커밋으로 다시 맞추고 등록을 새로 한다 (Aseprite 를 옮겼을 때도 이것만 하면 된다).
- **새 버전으로 올리기**: 스크립트의 `$PinnedCommit` 을 바꾸는 것은 클라우드 세션이 새 버전의 차이(diff)를 검토한 뒤에만 한다. 직접 `git pull` 하지 않는다.
- **등록 해제**: `powershell -ExecutionPolicy Bypass -File .\tools\aseprite-mcp\setup_windows.ps1 -Uninstall`
  (설치 폴더까지 지우려면 `-Uninstall -RemoveFiles`). deny 규칙은 남겨 둔다 — 서버가 없으면 아무 영향이 없다.

## 보안 메모 (2026-11-25 읽기 전용 검토 결과)

- 네트워크를 쓰지 않는다 (외부 전송·텔레메트리 없음). Claude 와는 stdio 로만 이야기한다. 의존성은 해시가 걸린 잠금 파일(`uv.lock`)로 고정.
- Aseprite 실행은 인자 목록으로만 한다 (셸 없음). 대부분의 도구는 Lua 를 만들어 `Aseprite.exe --batch --script` 로 실행하고 **파일을 그 자리에서 저장**한다.
- **막아 둔 도구 5개 (deny)**:

| 도구 | 막는 이유 |
|---|---|
| `run_lua_script` | 아무 Lua 나 실행한다. Aseprite 의 Lua 는 `os`·`io` 를 쓸 수 있어 명령 실행·파일 읽기/쓰기가 모두 된다. |
| `audit_animation`, `animation_sanitize` | 레이어 이름을 이스케이프 없이 Lua 에 넣는 버그(Lua 주입). 악의적인 `.aseprite` 의 레이어 이름으로 명령이 실행될 수 있다. |
| `start_preview_server`, `stop_preview_server` | 미리보기 HTTP 서버가 localhost 가 아닌 **모든 네트워크**에 열리고 폴더 목록을 보여 준다. 끄기는 임시 파일의 PID 를 강제 종료한다(엉뚱한 프로세스일 수 있음). 미리보기는 `python -m http.server` 로 따로 한다. |

- Claude **Desktop 채팅**은 `settings.json` 의 deny 를 읽지 않는다 → 앱의 aseprite 도구 목록에서 위 5개를 꺼 둔다. PC 작업은 가능하면 Claude Code(`claude`, `claude remote-control`, Desktop 의 Code)로 한다.
- 다른 쓰기 도구(`export_*`, `create_canvas`, `copy_sprite`, `render_onion_skin`, `copy_layers_between_sprites` 등)는 **어느 경로에나** 쓸 수 있다 (`..` 만 막음). 그래서 묻기(ask)로 두고, 경로는 게임 저장소 안의 절대 경로만 쓴다.
- `export_frame` 은 결과 파일이 없으면 이름이 비슷한 파일을 옮겨 올 수 있다 → 내보내기 폴더에 다른 파일을 두지 않는다.
- 모르는 사람이 보낸 `.aseprite` 는 열지 않는다 (레이어 이름이 도구 입력으로 들어간다).
- `.env` 에는 Aseprite 경로와 제한 시간만 있다. 비밀번호·토큰은 어디에도 저장하지 않는다. 받아 온 저장소의 `.mcp.json`·Docker 파일은 쓰지 않는다 (그 폴더를 Claude 프로젝트로 열지 말 것).

## 문제 해결

| 증상 | 해결 |
|---|---|
| `aseprite` 가 `/mcp` 에 없음 | Claude 를 완전히 다시 켠다. `claude mcp list` 에 있는지 본다. 없으면 스크립트를 다시 실행하고 마지막에 나온 `claude mcp add ...` 줄을 직접 실행 (스크립트가 끝 코드 2 로 끝났다면 이 경우). npm 으로 설치한 claude 는 PowerShell 에서 `claude.cmd mcp add ...` 로 (`claude.ps1` 은 `--` 를 지워 버린다). |
| `failed` / 연결 끊김 | PowerShell 에서 `& "$env:USERPROFILE\.local\bin\uv.exe" --directory "$env:USERPROFILE\tools\aseprite-mcp" run --frozen --no-dev python -c "import aseprite_mcp.tools"` 로 오류 확인 (도구까지 불러와야 `.env`·의존성 오류가 드러난다). 스크립트 다시 실행. |
| 경로에 빈칸 (`C:\Program Files\...`) | 그대로 괜찮다 (인자 목록으로 넘긴다). JSON 에 직접 쓸 때만 `\` 를 `\\` 로: `"C:\\Program Files\\Aseprite\\Aseprite.exe"`. `.env` 에 직접 쓸 때는 작은따옴표 `'...'` 또는 `/` (큰따옴표 안의 `\t`·`\n` 은 글자가 바뀐다). |
| 도구가 빈 결과만 돌려줌 (Steam 판) | `Aseprite.exe --batch --version` 이 아무것도 안 찍으면 Steam 을 거쳐 다시 실행되는 것. Steam 을 켜 두고 다시 시험, 안 되면 설치판 경로를 `-AsepritePath` 로. |
| 한글 파일·레이어 이름이 깨짐 / `UnicodeEncodeError` | MCP 설정의 env 에 `PYTHONUTF8=1` 이 있는지 (스크립트가 넣는다). 가능하면 파일 이름은 영문 (`sheet_hero_lyra.aseprite`). |
| 파일이 엉뚱한 곳(설치 폴더)에 생김 | 상대 경로를 썼기 때문 (서버는 설치 폴더에서 돈다). 언제나 절대 경로. |
| 시간 초과 | 큰 캔버스(1536x1024)는 느릴 수 있다. 스크립트를 `-TimeoutSeconds 180` 으로 다시 실행. |
| `settings.json` 을 읽을 수 없다고 나옴 | 파일에 주석·쉼표 오류가 있다. 스크립트가 그 파일은 건드리지 않고 넣을 줄을 보여 준다 — 그 줄을 `permissions.deny` 에 직접 넣는다. |
| 실행 정책 오류 | `-ExecutionPolicy Bypass` 를 붙여 실행 (위 3번). 회사 PC 정책으로 막혔으면 관리자에게 문의. |

## Aseprite 바이너리

Aseprite EULA 는 재배포를 금지한다. `Aseprite.exe` 나 그 폴더를 저장소에 올리지 않는다 (`AGENTS.md`). 저장소에는 `.aseprite` 작업 파일과 PNG 만 올린다.
