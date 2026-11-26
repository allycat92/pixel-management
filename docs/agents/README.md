# 부하 에이전트 — Codex(GPT CLI) · Antigravity

주인이 PC 의 작업 폴더(PowerShell)에서 띄운 두 에이전트다. 클라우드 Claude 가 일을 나누고 검토한다.
연락은 저장소로만 한다.
- 클라우드가 이 폴더의 `queue.md` 「지금 차례」에 줄을 올린다.
- 에이전트는 자기 브랜치에 작업과 보고를 올린다.
- 클라우드가 받아서 검토한 뒤 게임 브랜치에 넣는다.

| 이름 | 실행 | 상시 지시문 | 작업 브랜치 | 잘 맡는 일 |
|---|---|---|---|---|
| Codex | GPT CLI (`codex`) | `docs/agents/CODEX_STANDING.md` | `agent/codex` | 코드(엔진·도구) 수정, 시험, 측정 |
| Antigravity | Antigravity CLI | `docs/agents/ANTIGRAVITY_STANDING.md` | `agent/antigravity` | 브라우저로 직접 해 보는 플레이테스트·화면 검수, 재현 보고 |

## 공통 규칙 (두 에이전트 모두)
- **게임 브랜치 `claude/dot-fantasy-management-game-saupju` 에는 절대 푸시하지 않는다.**
  - 그 브랜치에서 갈라 만든 자기 브랜치(`agent/<이름>`)에만 푸시한다.
  - 강제 푸시(`--force`)는 하지 않는다.
  - `art-inbox` 브랜치는 건드리지 않는다. 그곳은 GPT 그림과 PC Aseprite 담당이다.
- 저장소 루트의 `AGENTS.md` 규칙을 지킨다.
  - Aseprite 실행 파일은 올리지 않는다.
  - NovelAI 는 주인이 시킬 때만 쓴다.
  - 남이 만든 완성 에셋이나 코드는 게임에 넣지 않는다.
  - 토큰이나 개인정보는 파일·로그에 남기지 않는다.
- `assets/` 와 `art/inbox/` 는 고치지 않는다. 그림 등록은 클라우드가 한다.
- 전투 코드(`js/battle.js`)를 바꾸면 아래 두 시험을 반드시 돌리고, 결과 줄을 보고에 붙인다.
  - `node tools/sim/battle.js 100`
  - `node tools/sim/bot.js`
- 보고와 질문은 한국어로 짧게 쓴다. 코드 주석은 주변 코드의 말을 따른다.
- 막히면 멋대로 방향을 바꾸지 않는다. 보고 파일에 「막힘」으로 적고 멈춘다.
