# C9 — 이동 그림 요청서 셋째 묶음 (Codex)

## Why
C8 은 잘 됐다. 다만 클라우드가 그림과 대조해 보니 10건 중 8건에서 12곳을 고쳐야 했다(`a5eff5d`).
고친 곳은 아래 다섯 가지 실수에서 나왔다. 이번에는 처음부터 피한다.

1. **phase3 CHARACTER 줄의 「the guide bow / spear」「exactly as the guide draws it」를 그대로 옮겼다.**
   이동 요청서에는 무기 가이드가 없다. 그래서 크기·잡는 법은 늘 「the accepted sheet's idle」 기준으로 적는다.
   - 이제 `--check` 가 이 문구를 잡는다.
2. **양손 무기인데 「마네킹 팔을 관절마다 따르라」는 THE MOVE 문장과 모순됐다.**
   - 양손으로 쥐면 이렇게 적는다: "The mannequin's two separate arm swings do NOT apply to this character (intended, not a deviation)".
   - 앞뒤로 움직이는 한도(약 30–35 px)도 함께 적는다.
   - 예시는 `robe__class_mage`, `run__captain_blademaster`.
3. **긴 무기의 각도를 「slightly」 같은 말로 적었다.**
   - 대기 그림에서 무기 길이를 잰다.
   - `pose.json` 의 손 위치에서 칸 한계(x=32–351, 끝 y≤852)를 지키는 각도를 계산해 숫자로 적는다.
   - 예시는 `run__captain_bard`, `run__captain_tactician`.
4. **머리·옷 움직임을 일괄로 「trail back」이라고 적었다.**
   - 가슴 앞으로 늘어진 땋은 머리처럼 앞에 있는 것은 그 자리에 둔다고 따로 적는다.
5. **분류 설명(`gait_classes.json` 의 `why`)이 그림과 달랐다.**
   - 로브 길이, 부츠가 보이는지 등을 대기 그림에서 보고 맞춘다.
   - 고쳤으면 `--js` 로 다시 만든다.

## Do
1. 요청서를 만든다.
   - 영웅: `sheet/hero/kai`, `grom`, `lyra`, `marisol` (경량), `oswin` (중량), `astel`, `seraphine` (로브)
   - 대장: `sheet/captain/frostjarl` (경량)
   - 괴물: `sheet/monster/해골 병사`, `sheet/monster/산적` (경량)
   - 만드는 명령은 `python3 tools/art/gait_requests.py --write <id...>` 이다.
2. 시트마다 README 의 손·무기·옷 문장을 보강한다.
   - 근거는 phase3 CHARACTER 줄(영웅·괴물은 그 꾸러미 README 또는 `art/requests/` 안의 해당 요청)과 등록된 시트의 대기 칸이다. 대기 칸은 잘라서 확대해 직접 본다.
   - 위 다섯 가지를 하나씩 확인한다.
3. 폴더마다 SELF-CHECK 를 두 입력으로 돌린다.
   - 마네킹 사본은 거부되어야 한다.
   - 그림 사본은 통과해야 한다.
   - `python3 tools/art/gait_requests.py --check` 가 PASS 여야 한다.
4. 크기 판을 직접 본다.

## Do not touch
`art/requests/dot_queue.md`, `assets/`, `art/inbox/`, 게임 코드.

## Deliver
- 브랜치 `agent/codex` 에 올린다.
- 보고서 `## C9 — <날짜>` 를 쓴다. 시트마다 다섯 가지 점검 결과와 잰 숫자를 적는다.
- 이 줄을 REVIEW 로 바꾼다.
