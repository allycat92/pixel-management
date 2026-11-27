# C26 — 마지막 이동 요청서 묶음 + 카토 분류 (GPT — Codex 가 C27 을 하는 동안 넘김)

## Why
요청서가 아직 없는 시트가 남았다.
- 경량: `sheet/captain/warlord`
- 중량: `titan`
- 로브: `demonhunter`, `hexer`, `inquisitorlord`
- 카토(`sheet/captain/liberator`, `90d7e0c` 새 등록): 아직 이동 부류 분류(`tools/art/specs/gait_classes.json`)에도 없다.

## Do
1. 카토의 이동 부류를 대기 그림을 보고 정한다. 맨몸에 사슬과 맨주먹이라 경량이 유력하다. `gait_classes.json` 에 근거와 함께 넣고 `--js` 를 돌린다.
2. 6건의 요청서를 만든다(`gait_requests.py --write`).
   - C15 「Do」 2번의 점검 항목을 그대로 적용한다.
     - 무기가 얼굴을 지나지 않는가
     - 날 폭까지 칸 안에 드는가
     - 팔이 닿는 손 위치인가
     - 앞에 늘어진 천·머리를 앞에 두는가
     - 분류 설명이 그림과 맞는가
   - **키가 다른 캐릭터:** 거인(titan)처럼 키가 다르면 룬 대장장이·고블린처럼 `height`/`joints` CARRY 키를 쓴다.
   - **배율:** 배율이 다른 시트는 phase3 배율이 있을 때만 만든다.
3. SELF-CHECK 를 돌린다. 마네킹 사본은 거부, 그림 사본은 통과해야 한다. `--check` 는 PASS 여야 한다.
4. **C25 의 이음매 검사**: 크기 판이나 가이드에서 WARN 이 뜨지 않는지 본다.

## Deliver
- 브랜치 `agent/gpt-qa` 에 올린다. 보고서는 `docs/agents/reports/gpt-qa.md` 에 쓴다.
- 보고서 `## C26 — <날짜>` 를 쓴다.
- 이 줄을 REVIEW 로 바꾼다.
- 클라우드가 그림 대조를 한 뒤에 대기열에 올린다.
