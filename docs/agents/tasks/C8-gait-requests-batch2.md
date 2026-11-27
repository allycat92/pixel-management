# C8 — 이동 그림 요청서 둘째 묶음 만들기 (Codex)

## Why
Antigravity 가 그릴 이동 그림 요청서는 생성기로 찍어 낸다. `python3 tools/art/gait_requests.py --write <시트 id...>` 와 `art/requests/gait/README.md` 「더 만드는 법」을 본다.
첫 다섯 건은 클라우드가 만들어 대기열에 올렸다. 생성기는 검증까지 마쳤다(`d01dfa5`). 남은 시트는 `python3 tools/art/gait_requests.py` 가 보여 준다.

## Do
1. 다음 시트들로 요청서를 만든다.
   - 경량: 대장 `blademaster`, `huntress`, `bard`, `fixer`, `veteran`, `tactician`
   - 중량: `lancer`, `saintknight`
   - 로브: `archmagus`, `lightbearer`
2. 생성기가 「검토」 표시를 붙이는 시트(CARRY 표에 없는 시트)는 README 의 손·무기·옷 문장을 직접 보강한다.
   - 근거는 그 대장의 `art/requests/phase3/captain_<key>/README.md` CHARACTER 줄과, 등록된 시트의 대기 칸이다. 대기 칸은 잘라서 직접 보고 확인한다.
   - 무기가 무엇이고 어느 손에 있는지, 뛰면서 어떻게 드는지, 망토·옷자락이 어떻게 움직이는지를 적는다.
3. 폴더마다 README 의 SELF-CHECK 명령을 아래 두 입력으로 돌려 확인한다.
   - 마네킹 사본을 넣으면 `add_gait` 가 거부해야 한다.
   - 그림 사본을 넣으면 통과해야 한다.
4. `python3 tools/art/gait_requests.py --check` 가 PASS 여야 한다.
5. 크기 판(`size_*.png`)을 직접 본다. 대기 그림과 마네킹의 크기가 같고, 발이 땅선에 붙어 있어야 한다.

## Do not touch
`art/requests/dot_queue.md`(클라우드가 대기열에 올린다), `assets/`, `art/inbox/`, 게임 코드.

## Deliver
- 브랜치 `agent/codex` 에 새 요청 폴더들과 보고서 `## C8 — <날짜>` 를 올린다. 보고서에는 시트마다 보강한 문장과 확인 결과를 적는다.
- 이 줄을 REVIEW 로 바꾼다.
