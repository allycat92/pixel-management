# C15 — 이동 그림 요청서 넷째 묶음 (Codex)

## Why
Antigravity 가 이동 그림을 납품하기 시작했다. 브리긴다(중량)와 마법사(로브)가 등록됐다.
남은 대장들의 요청서를 미리 만들어 둔다. 대상은 경량 9명과 중량·로브 각 2명이다.

## Do
1. 요청서를 만든다(`python3 tools/art/gait_requests.py --write <id...>`).
   - 경량: `sheet/captain/admiral`, `beastmaster`, `elfwarden`, `fieldmedic`, `khan`, `shadowlord`, `siegemaster`, `spellblade`, `windhunter`
   - 중량: `sheet/captain/dragonslayer`, `runesmith`
   - 로브: `sheet/captain/hedgemage`, `pilgrim`
   - 해적왕(배율 0.185)·서리 트롤·고블린은 phase3 배율이 없으면 만들지 않는다. 보고서에 「막힘」으로 적는다.
2. C9 「Why」의 다섯 가지 실수와 C10 비요른 대조에서 나온 교훈을 하나씩 확인한다.
   - **무기가 얼굴을 지나지 않는가.** 뛸 때 머리가 앞으로 기울어지니 대기와 같은 각도가 맞지 않을 수 있다. `pose.json` 의 머리·목 좌표로 계산해서 확인한다.
   - **무기 날 폭까지 넣어 칸 한계 안에 드는가.** 칸 한계는 x=32–351, 끝 y≤852 다.
   - **손 높이가 대기 그림과 맞는가.** 엉덩이 높이를 기준으로 본다.
   - **앞에 늘어진 천·머리를 「뒤로 날린다」고 쓰지 않았는가.**
   - **분류 설명(`why`)이 그림과 맞는가.**
3. SELF-CHECK 를 두 입력(마네킹 사본은 거부, 그림 사본은 통과)으로 돌리고 `--check` 를 PASS 로 만든다.

## Do not touch
`art/requests/dot_queue.md`, `assets/`, `art/inbox/`, 게임 코드.

## Deliver
- 브랜치 `agent/codex` 에 올린다.
- 보고서 `## C15 — <날짜>` 를 쓴다. 시트마다 점검 결과와 잰 숫자를 적는다.
- 이 줄을 REVIEW 로 바꾼다.
- 클라우드가 그림 대조 검증을 한 뒤에 Antigravity 대기열에 올린다.
