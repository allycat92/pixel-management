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
| 하는 일 | `dot_queue.md` 에서 `담당: PC(Aseprite)` 가 붙은 항목만: 받은 시트 손질, 자세 뼈대 만들기·다듬기 | 요청서·가이드·대기열 관리, 납품 검사, `sheets.py` 등록, 게임 연결, 피드백, 코드 리뷰 |
| 쓰는 곳 | **`art-inbox` 브랜치의 `art/inbox/` 만** | 게임 브랜치 `claude/dot-fantasy-management-game-saupju` (그리고 art-inbox 는 읽기만) |
| 하지 않는 일 | 게임 브랜치에 푸시, `dot_queue.md`·`feedback.md`·`js/`·`assets/`·`tools/` 수정, 시트 등록 | PC 의 파일·프로그램을 직접 만지는 일 (닿지 않는다) |

- **역할 나눔 (2026-11-25 주인 결정)**: GPT 도트 = 새로 그리기·다시 그리기, PC = 이미 받은 그림을 Aseprite 로 손질(색·소품) + 자세 뼈대(`art/requests/guides/SPEC.md`). 클라우드가 손질 항목에 `담당: PC(Aseprite)` 를 붙이고, PC 는 **그 항목만** 한다 (담당 표시가 없는 DOT_READY 는 GPT 몫).
- **PC 지침의 원본은 `tools/aseprite-mcp/pc/CLAUDE.md` 하나뿐이다** (판 번호가 맨 위에 있다; 늘 지키는 규칙은 `art/requests/pc_notes.md`). `git pull` 로 따라온다.
  PC 에는 한 번만 복사한다: `tools/aseprite-mcp/pc/CLAUDE.local.md`(본문을 불러오는 세 줄 + 이 PC 의 경로) → 게임 폴더 루트, `settings.local.json` → 게임 폴더의 `.claude\settings.local.json`
  (둘 다 `.git\info\exclude` 에 적어 커밋되지 않게). 설정 파일의 허용 목록이 바뀌면 그때만 다시 복사한다.
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
- 레이어 약속은 `art/requests/pc_notes.md` 「`.aseprite` 레이어」(손질) 와 `art/requests/guides/SPEC.md` 4절(뼈대). 숨긴 레이어는 `original_ref` 하나만 —
  클라우드는 숨긴 레이어까지 모두 살펴본다 (`check_delivery.py` 가 레이어 이름과 `original_ref` == 받은 그림을 검사).
- NovelAI 초안·`art/refs` 참고 그림은 숨긴 레이어로도 넣지 않는다. 파일·레이어 이름은 영문.

## 4. dot_queue 상태 — 누가 무엇을

`art/requests/dot_queue.md` (게임 브랜치) 가 차례를 정한다. **상태는 클라우드만 바꾼다.**

| 상태 | PC 세션 | 클라우드 세션 |
|---|---|---|
| `QUEUED` | 하지 않는다 | 차례가 되면 `DOT_READY` 로 올린다 |
| `DOT_READY` | `담당: PC` 표시가 있을 때만 한다 | 납품이 오면 검사 |
| `NEEDS_FIX` | `담당: PC` 표시가 있을 때만: 그 줄의 메모·요청서대로 같은 이름으로 다시 납품 (`.aseprite` 도 함께) | 다시 검사 |
| `DELIVERED`·`ACCEPTED` | 건드리지 않는다 | 검사 중 / 등록 끝 |

- PC 가 고를 때: **상태 칸에 `담당: PC(Aseprite)` 가 붙은 항목만**, 위에서부터 하나씩. 표시가 없는 항목은 상태가 무엇이든 GPT 몫이다.
  표시된 항목이 없으면 "할 일 없음" 이라고 알리고 멈춘다.
- 손질 항목에는 클라우드가 `바탕: art-inbox <해시>` 를 적는다. 그 파일의 마지막 커밋이 다르면(그 사이 GPT 가 다시 올림) PC 는 손대지 않고 알린다.
- PC 는 납품 뒤 주인에게 "올렸다(커밋 해시, 지침 판)" 라고 말한다. 클라우드는 art-inbox 를 주기적으로 확인한다.

## 5. 커밋 메시지

**PC (art-inbox)** — 첫 줄만, 영어, 본문 없음 (검사 결과는 NOTES 에 적는다):
`Touch up <stem> (Aseprite)` / `Add guide <id> (Aseprite)` / `Touch up guide <id> (Aseprite)`. `<stem>` 은 파일 이름 그대로.

**클라우드 (게임 브랜치)** — 지금처럼: `Accept <누구> ...`, 도구 변경은 그 내용대로.

## 6. PC 가 푸시하기 전에 할 일

`tools/aseprite-mcp/pc/CLAUDE.md` 「납품」 그대로 (여기에 따로 적지 않는다 — 두 벌이 어긋났었다). 요점: 내보내기와 자체 검사는
`check_delivery.py ... --aseprite <원본> --export --base-rev <바탕 해시>` 한 줄, 새로 생긴 FAIL 이 있으면 푸시하지 않는다, `art/inbox/` 안만 커밋,
NOTES.md 충돌은 양쪽 절을 모두 남기고 PNG·`.aseprite` 충돌은 풀지 않고 멈춘다.

## 7. 클라우드가 받은 납품을 처리하는 법

클라우드에는 머리 없는 Aseprite 빌드가 있다 (`/home/user/aseprite-build/src/build/bin/aseprite`, 만드는 법 `tools/aseprite/README.md`;
저장소에 없고 컨테이너가 바뀌면 다시 빌드). aseprite-mcp 는 클라우드에서 쓰지 않는다 — Aseprite 명령줄만 쓴다.

### 클라우드 수령 절차 (정기 점검도 이 절차를 따른다)

```bash
python3 tools/art/receive.py --list                       # 새로 올라온 파일·NOTES 절 (이 브랜치의 art/inbox 와 다른 것 = 아직 안 본 것)
python3 tools/art/receive.py <stem> --work <스크래치 폴더>   # 한 파일 검사 (Aseprite 는 tools/art/ase_headless.sh 가 버리는 프로필로 부른다)
```
1. `--list` 에 아무것도 없으면 끝. 새 NOTES 절(제안·막힘·교차 검수 답)이 있으면 읽고 처리한다(`dot_queue.md` 「운영 규칙」).
2. 파일마다 `receive.py <stem>` → **`review_<stem>.png` 를 눈으로 본다** (왼쪽 디자인 기준 = 초상화·시안, 오른쪽 게임 크기 x3 을 어두운 바닥·모래·눈 위에).
   세는 것(다리·눈·무기 종류)은 게임 크기에서 직접 센다. 시안이 기준인 항목은 시안과 나란히 보지 않고는 통과시키지 않는다.
3. 통과: `python3 tools/art/sheets.py art/inbox/<stem>.png` (배율·칸·배치·점 색은 `phase3.json` 에서 — 플래그 없이) → 대기열 ACCEPTED → feedback.md 기록.
   결함: 대기열 NEEDS_FIX + 그 줄 메모(GPT 는 꾸러미 README 의 THIS ROUND 로, PC 는 `바탕:` 해시와 함께) → feedback.md 기록.
4. 통과든 결함이든 `git checkout <그 해시> -- <납품 경로들>` 로 이 브랜치에 가져온다 (이것이 "봤다"는 표시다 — 따로 상태 파일이 없다).
   **한 번의 점검은 한 커밋에 고정한다**: `--list` 가 보여 준 art-inbox 끝 커밋의 해시를 적어 두고, 그 뒤의 `receive.py` 는 `--no-fetch` 로,
   가져오기도 그 해시로 한다. `NOTES.md` 는 `--list` 가 보여 준 새 절(납품 메모·제안·막힘)을 **모두** 처리했거나 대기열에 옮겨 적은 뒤에만 가져온다
   (PNG 한 장만 보고 NOTES 를 통째로 가져오면 같은 파일에 있던 다른 제안이 목록에서 사라진다 — GPT 제안 `9e3939e`).
5. 대기열 「지금 차례」를 고치고, 사람형 대장 DOT_READY 가 5개 아래면 다음 QUEUED 를 올린다. 커밋·푸시, 주인에게 미리보기와 함께 짧게 보고.
- `dot_queue.md` 에 DOT_READY·NEEDS_FIX·DELIVERED 가 하나라도 있으면 감시(`tools/art/watch_inbox.sh` — 60초 폴링, 30분마다 다시 켬)와 한 시간 정기 점검을 켜 둔다.
  감시가 꺼져 있던 것을 발견하면 다시 켜기 전에 `--list` 부터 돌린다.
`receive.py` 가 한 번에 한다: art-inbox 에서 PNG·원본 꺼내기 → 이전 판을 바탕으로 찾기 → `check_delivery.py`(배치·칸·점 색은 `phase3.json` 에서,
바탕과의 윤곽·색 차이, 원본==PNG, 레이어 이름, 숨긴 `original_ref` == 바탕) → `sheets.py --dry-run`(등록된 시트와 같은 배율·칸) →
게임 크기에서 실제로 바뀐 픽셀 수 → 그 납품이 `art/inbox/` 밖을 건드렸는지. 등록·커밋은 하지 않는다 (미리보기를 본 뒤 사람이 판단).
- 검사가 통과하면 평소대로: `sheets.py ... --dry-run` 으로 미리보기 → 검토 → 등록 (`art/README.md` 「전투 캐릭터 시트」) → `dot_queue.md` 상태와 `feedback.md` 갱신 → 게임 브랜치에 푸시.
- PNG 와 원본이 다르면 `NEEDS_FIX` ("PNG 를 원본에서 다시 내보낼 것"). PNG 가 빠졌으면 클라우드가 원본에서 내보내 검사해도 되지만, 피드백에 적어 다음부터 둘 다 올리게 한다.
- `.aseprite` 원본도 4번처럼 이 브랜치의 `art/inbox/` 로 가져온다 ("봤다"는 표시 — 게임은 쓰지 않는다). 피드백에서 레이어 이름으로 고칠 곳을 가리킬 수 있다.

## 8. PC 세션에 처음 붙여 넣을 지시

따로 없다. PC 의 게임 폴더에 `CLAUDE.local.md`(1절)가 있으면 Claude 가 지침을 스스로 읽는다. 주인은 "다음 손질 진행해" 처럼 한 줄만 말하면 된다.
(예전에 여기 있던 긴 지시문은 지웠다 — `CLAUDE.md` 와 내용이 어긋나 표시 없는 DOT_READY 까지 그리라고 적혀 있었다.)
