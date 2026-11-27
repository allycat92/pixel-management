# C17 — 고블린·서리 트롤·사막 도적 이동 요청서 (Codex)

## Why
C10 FIX 이후 배율은 phase3.json 의 명시값만 믿는다. 고블린과 서리 트롤은 phase3.json 에 배율이 없어서 요청서를 만들 수 없었다. 사막 도적도 아직 요청서가 없다.

두 시트를 등록한 실제 배율은 기록에 남아 있다.
- 고블린: `sheets.py ... --grid 4x1 --scale 0.1654 --cell 96`
  - 근거: 클라우드 등록 커밋 `db6e860`, `9e2628c`(`--scale 0.1654`)
- 서리 트롤: `--grid 2x2 --scale 0.1800 --cell 96`(`db6e860`)

## Do
1. `art/requests/phase3.json` 의 `sheet/monster/고블린`·`sheet/monster/서리 트롤` 항목에 실제 등록값을 적는다. 적을 값은 scale·cell·layout(grid)이다.
   - 서리 트롤처럼 원본이 2×2 면 `run_request_guides.geometry()` 가 2×2 원본을 1x4 로 잘못 읽는다. layout 을 보고 대기 칸을 제대로 고르게 고친다.
   - 같은 값으로 `sheets.py --dry-run` 을 돌린 결과가 지금 등록된 시트와 같아야 한다. 대기 크기와 바닥 위치를 비교한다.
2. 요청서를 만든다.
   - `sheet/monster/고블린`(경량)
   - `sheet/monster/서리 트롤`(중량, 배율 0.18 → 배율 가이드)
   - `sheet/monster/사막 도적`(경량)
3. C15 의 점검 항목을 그대로 적용한다.
   - 무기가 얼굴을 지나지 않는가
   - 날 폭까지 칸 안에 드는가
   - 팔이 닿는 손 위치인가: 마네킹 팔 길이 약 140px, 어깨에서 손까지
   - 앞에 늘어진 천·머리는 앞에 두는가
   - 분류 설명이 그림과 맞는가
4. SELF-CHECK 두 입력으로 돌린다.
   - 마네킹 사본은 거부되어야 한다.
   - 그림 사본은 통과해야 한다.
   - `--check` 는 PASS 여야 한다.

## Do not touch
`assets/`, 등록된 시트, `art/inbox/`, `dot_queue.md`, 게임 코드.

## Deliver
- 브랜치 `agent/codex` 에 올린다.
- 보고서 `## C17 — <날짜>` 를 쓴다.
- 이 줄을 REVIEW 로 바꾼다.
- 대기열에는 클라우드가 그림 대조 검증을 한 뒤에 올린다.
