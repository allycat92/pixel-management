# 부하 에이전트 — Codex(GPT CLI) · Antigravity

주인이 PC 의 작업 폴더(PowerShell)에서 띄운 두 에이전트다. 클라우드 Claude 가 일을 나누고 검토한다.
연락은 저장소로만 한다.
- 클라우드가 이 폴더의 `queue.md` 「지금 차례」에 줄을 올린다.
- 에이전트는 자기 브랜치에 작업과 보고를 올린다.
- 클라우드가 받아서 검토한 뒤 게임 브랜치에 넣는다.

| 이름 | 실행 | 상시 지시문 | 작업 브랜치 | 잘 맡는 일 |
|---|---|---|---|---|
| Codex | GPT CLI (`codex`) | `docs/agents/CODEX_STANDING.md` | `agent/codex` | 코드(엔진·도구) 수정, 시험, 측정 |
| Antigravity | Antigravity CLI | `docs/agents/ANTIGRAVITY_STANDING.md` | `agent/antigravity` (보고) · `art-inbox` 의 `art/inbox/` (그림·판정) | **도트 애니메이션 헤드**(주인 2026-11-26) + 플레이테스트·화면 검수 |

## 공통 규칙 (두 에이전트 모두)
- **게임 브랜치 `claude/dot-fantasy-management-game-saupju` 에는 절대 푸시하지 않는다.**
  - 그 브랜치에서 갈라 만든 자기 브랜치(`agent/<이름>`)에만 푸시한다.
  - 강제 푸시(`--force`)는 하지 않는다.
  - `art-inbox` 브랜치는 Codex 가 건드리지 않는다. 그곳은 GPT 그림, PC Aseprite, 헤드 Antigravity 의 그림·판정을 받는 곳이다(`art/inbox/` 만).
- 저장소 루트의 `AGENTS.md` 규칙을 지킨다.
  - Aseprite 실행 파일은 올리지 않는다.
  - NovelAI 는 주인이 시킬 때만 쓴다.
  - 남이 만든 완성 에셋이나 코드는 게임에 넣지 않는다.
  - 토큰이나 개인정보는 파일·로그에 남기지 않는다.
- `assets/` 는 고치지 않는다. 그림 등록은 클라우드가 한다(Antigravity 의 그림·판정은 `art-inbox` 의 `art/inbox/` 로만).
- 전투 코드(`js/battle.js`)를 바꾸면 아래 두 시험을 반드시 돌리고, 결과 줄을 보고에 붙인다.
  - `node tools/sim/battle.js 100`
  - `node tools/sim/bot.js`
- 보고와 질문은 한국어로 짧게 쓴다. 코드 주석은 주변 코드의 말을 따른다.
- 막히면 멋대로 방향을 바꾸지 않는다. 보고 파일에 「막힘」으로 적고 멈춘다.

## 도트 애니메이션 헤드 — Antigravity (주인 결정 2026-11-26)
- **판정**: 동작 그림의 통과와 고침은 Antigravity 가 정한다.
  - 대상: 마네킹, GPT 그림, PC 손질, Antigravity 자신의 그림.
  - 게임 속도로 직접 보고 판단한다. 기준은 세 가지다: 자연스러움, 캐릭터다움, 맞는 순간이 읽히는가.
  - 클라우드는 기술 관문만 막는다(검사기 FAIL, 규격, 마네킹 베끼기, 엔진 문제).
  - 판정이 엇갈리면 주인이 정한다.
- **그림**: Antigravity 도 최종 그림을 그릴 수 있다(주인: "최종 그림도 허용").
  - GPT 와 같은 요청서와 규격을 따른다(셀·바닥·열쇠 색).
  - 납품 자리는 GPT 와 같다: `art-inbox` 브랜치의 `art/inbox/`.
  - NovelAI 는 여전히 초안 전용이다.
- **지시**: GPT 와 PC 에게 줄 요청·고칠 점의 *내용*은 헤드가 정한다.
  - 헤드는 그것을 판정 절에 쓴다.
  - 클라우드가 `art/requests/dot_queue.md` 와 요청서에 그대로 옮긴다.
  - 대기열을 고치는 곳을 하나로 둬서 GPT·PC 가 서로 다른 지시를 받지 않게 한다.
- **판정 쓰는 곳**: `art-inbox` 브랜치 `art/inbox/NOTES.md` 에 아래 형식의 절을 단다.
  ```
  ## 판정 — <대기열 id>
  결과: 통과 | 고침 | 다시
  본 방법: (게임 안 1×/4×, 미리보기 GIF, 프레임 — 무엇을 봤는지)
  고칠 점: (누가 — GPT/PC/Antigravity — 무엇을, 프레임 번호와 함께. 통과면 "없음")
  캐릭터 메모: (다음 그림에 이어 갈 방향, 없으면 생략)
  ```
  클라우드의 수령 도구(`receive.py`)가 새 절을 알아채고 대기열에 반영한다.
- **판정 대기 줄**: 클라우드가 납품을 받아 기술 검사를 통과시키면 그 줄을 `HEAD_REVIEW` 로 바꾼다. 헤드는 그 줄들을 판정한다.

## 작업 폴더 (에이전트마다 따로 — 2026-11-26)
- 에이전트마다 **자기 클론을 따로** 쓴다. 같은 폴더를 함께 쓰면 한쪽이 브랜치를 바꾸거나 커밋하지 않은 수정을 남길 때 다른 쪽이 막힌다.
- 폴더는 사용자 홈 아래에 둔다(예: `$HOME\work\pm-codex`, `$HOME\work\pm-antigravity`). `C:\Windows\System32` 아래는 일반 계정에 쓰기 권한이 없어 `git fetch` 가 실패한다.
- PC Aseprite 세션의 `pixel-management-inbox` 폴더(art-inbox)와도 따로 쓴다.
- 만드는 법: `git clone -b claude/dot-fantasy-management-game-saupju https://github.com/allycat92/pixel-management.git <폴더>` 를 실행하고, 에이전트를 그 폴더에서 연다.

## 역할 나누기 (주인 결정 2026-11-26 — 클라우드 Claude = 총괄 기획)
| 누구 | 맡는 일 |
|---|---|
| **클라우드 Claude (총괄 기획)** | 주인과 직접 소통하며 방향을 정리하고 지시한다. 각 에이전트의 보고·피드백을 모아 `docs/agents/STATUS.md` 에 정리한다. 큰 틀의 결정(주인 결정이 필요한 것은 모아서 묻는다)과 **핵심 코딩**(전투 엔진·전술·게임 규칙)을 한다. 밸런싱은 CLI 에게 시험을 시키고 뽑힌 데이터로 판단한다. |
| **Antigravity** | 도트 애니메이션 헤드(판정·지시 내용·최종 그림 가능) + 플레이테스트·화면 QA |
| **Codex** | 자잘한 오류 수정, 도구 손질, 시험·측정 돌리기(밸런스 데이터 뽑기 포함) |
| **GPT (그림)** | 캐릭터 그림(시트·동작 프레임), 교차 검수 |
| **PC Aseprite 세션** | 마네킹 시퀀스, 받은 그림 손질 |

- 클라우드는 에셋 제작·QA·자잘한 수정을 직접 하지 않고 일감으로 내린다(`docs/agents/queue.md`, `art/requests/dot_queue.md`).
- 에이전트의 보고는 모두 저장소로 온다. 클라우드가 받아 검토하고, 주인에게는 취합한 결과와 결정할 것만 올린다.
