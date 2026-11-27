# Q3 — 첫 이동 요청서 다섯 건을 그림과 대조하기 (GPT-QA)

## Why
아래 다섯 요청서는 Antigravity 가 지금 그리고 있거나 곧 그린다.
- `heavy__captain_ironwall`, `robe__class_mage`, `run__class_archer`, `run__class_cleric`, `run__class_rogue`

이것들은 클라우드가 만들었고, 그림과의 이미지 대조는 아직 하지 않았다. C8 묶음은 대조해 보니 10건 중 8건에서 틀린 문장이 나왔다. 틀린 문장이 그대로 그림이 되기 전에 사람 눈으로 다시 본다.

C8 에서 나온 실수 다섯 가지는 `docs/agents/tasks/C9-gait-requests-batch3.md` 「Why」에 있다.

## Do
1. 폴더마다 다음을 본다.
   - `art/requests/gait/<폴더>/README.md`
   - `guide_*.png`, `size_*.png`
   - 등록된 시트의 대기·공격 칸: `assets/art/manifest.json` 에서 찾는다. 잘라서 4배로 키워 본다.
   - 원래 캐릭터 요청서(`art/requests/phase3/…` 또는 병과 요청서)
2. 다섯 가지 실수와 아래 항목을 하나씩 확인한다.
   - 무기는 무엇이고 어느 손에 있는가
   - 다른 손은 어디에 있는가
   - 등·허리에 무엇을 지고 있는가
   - 옷·머리는 어떻게 움직이는가
   - 크기 판에서 대기 그림과 마네킹의 크기가 같은가
3. 틀린 문장마다 다음 셋을 적는다.
   - 인용
   - 근거: 어느 그림의 어느 좌표에서 무엇이 보이는가
   - 대신 쓸 영어 문장

## Do not touch
요청서 파일 자체. 고치는 일은 클라우드가 한다.

## Deliver
- 브랜치 `agent/gpt-qa` 에 보고서 `## Q3 — <날짜>` 를 올린다. 폴더마다 OK / FIX 로 적는다.
- 근거 확대 그림은 `docs/agents/reports/shots/Q3/` 에 넣는다(각 500KB 이하).
- 이 줄을 REVIEW 로 바꾼다.
