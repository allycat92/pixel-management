# C6 — 그림자 측정 도구 손질 (Codex)

## Why
전투 수치 뼈대 0~1단계(그림자 방식: 게임 결과는 그대로, 능력치 전투는 뒤에서 기록만)가 들어갔다. 설계와 노트는 `docs/plans/battle_stats/`
(특히 `stage01_notes.md`)에 있다. 다음 일은 대량 측정으로 숫자를 맞추는 것(C7)이다. 그 전에 0~1단계 검증에서 나온 도구 결함을 고친다.

## Fix
1. `tools/sim/shadow.js` 의 `--set` / `--sweep` / `STAT_KNOBS` 는 지금 맨 위 이름만 검사한다.
   - 점 경로(`KIND_K.bos`, `ARCH.blobb.hp`, `PIERCE.fier`)에 오타가 있어도 받아들이고 아무것도 바꾸지 않는다.
   - 숫자 자리에 `abc` 가 오면 NaN 으로 계산해 멀쩡해 보이는 표를 찍는다.
   - 경로 전체가 `Stats.KN` 에 있는지, 값이 원래 값과 같은 형(유한한 숫자 / 객체 / 불)인지 검사한다. 틀리면 오류로 멈춘다.
2. `Battle.run` 기록의 `tab` digest 가 처음 쓸 때 고정된다. 실행 중에 `Stats.KN.K` 를 바꿔도 그대로다.
   - 노브가 바뀌면 다시 계산하게 한다.
   - `monsterSkills()` 의 상수도 digest 에 넣는다.
3. `shadow.js` 표 이름: `0.9-1.0` 칸은 실제로 0.90~0.97 이다. 이름을 고친다.
4. 문서: `docs/DESIGN.md` 의 시험 절에 `tools/sim/shadow.js` 를 짧게 적는다. 적을 것은 셋이다.
   - 무엇을 재는가
   - `--check`, `--set`, `--sweep`, `--out`/`--csv`
   - `SIM_SHADOW=1`(봇에서 그림자 전투를 켜는 스위치, 기본은 끔)

## Do not touch
게임 규칙과 수치(`Stats.KN` 의 값), `js/battle.js` 의 판정 경로.

## Checks
- `node tools/sim/battle.js 100`: miss=0 ×4
- `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` 와 `SIM_SHADOW=1` 판 모두 `ddfdfe7b437fbe9fcf25f166ba542fce`
- `node tools/sim/shadow.js 6 200 --check`: 모두 0
- 오타·형 오류 노브가 오류로 멈추는 것을 보여 줄 것

## Deliver
- 브랜치 `agent/codex` 에 올린다. 먼저 게임 브랜치를 합친다.
- 보고서 `## C6 — <날짜>` 절을 쓴다.
- 이 줄을 REVIEW 로 바꾼다.
