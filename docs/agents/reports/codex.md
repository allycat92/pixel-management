## C1 — 2026-11-26

WIP. V11을 바탕으로 걷는 유닛에 보정을 우선 적용하고, 궤주 유닛은 아군과의 충돌에서 제외했다. 한쪽만 돌진한 경우 돌진한 쪽에 보정량을 모두 적용한다. 제자리 유닛끼리 깊게 겹치면 조금씩 벌린다. 회피와 자리 점유 검사에 좌표 범위 사전 검사를 넣었다.

- 같은 보고서 100개와 결과 4종으로 전후를 비교했다. 승패 불일치와 소프트 미스는 모두 0건이었다.
- `node tools/sim/battle.js 100` 수정 후 결과

```text
reports 100 × 4 outcomes = 400 findBattle calls (game seeds 1..3)
win/lose mismatches: 0
soft misses (great with >25% loss / disaster with <50% loss): 0
slow battles (>=60 s): 0, time-limit (90 s) battles: 0
findBattle avg 34.4 ms, max 315 ms
  great    n=100 miss=0 soft=0 avg 20.1 ms, battle 19.9 s
  success  n=100 miss=0 soft=0 avg 77.0 ms, battle 31.5 s
  fail     n=100 miss=0 soft=0 avg 21.5 ms, battle 25.5 s
  disaster n=100 miss=0 soft=0 avg 18.8 ms, battle 22.5 s
```

- 기준 전투 시간은 같은 순서로 19.1 / 28.8 / 23.6 / 20.5초였다. 탐색 평균·최대는 35.0 / 289 ms에서 34.4 / 315 ms로 변했다.
- `node tools/sim/bot.js` 전후 요약 출력 동일. 12 × 365일, S등급 12회, 파산 0회, 완료 / 실패 / 전사 632 / 33 / 0.
- 선택된 전투 400건을 계측해 자력 이동 없이 충돌 보정으로 위치가 바뀐 비율이 20.07% (573201/2856611)에서 0.04% (1303/3064184)로 줄어든 것을 확인했다.
- 15초 이상 전장에 남아 공격하지 않은 근접 유닛은 1.53% (38/2485)에서 2.08% (53/2544)로 변했다.
- 서 있는 아군끼리 정규화 거리 0.5 미만이 연속된 최장 시간은 0.00초에서 0.30초로 변했다.
- 브라우저 검증 미완료. 루프백 서버는 HTTP 200을 반환했다. Chrome 시크릿 창을 열었으나 사용자 Esc로 조작이 중단됐다. 실제 전투 1배속 화면과 페이지 오류는 확인이 남아 있다.
