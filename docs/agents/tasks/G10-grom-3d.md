# G10 — 그롬 이동 8프레임, 3D 마네킹 위에 그리기 (GPT, 그림)

주인 11-28: 「안티그래비티 한도를 확인하고 바꾸자는 지시 전까진 GPT 에 위임」, 「싹 다 저렇게(3D 마네킹) 돌리자」. 허용 범위: `docs/agents/GPT_QA_STANDING.md` ART EXCEPTION. 방법은 G1(바렌, 주인 「저정도면 훌륭해」)과 같다.

- 요청서: `art/requests/gait/run__hero_grom/README.md` — 그대로 따른다(개성·무기 드는 법·보폭·손목 범위·원근·바닥 후보정·마네킹 픽셀 전부 덮어 그리기).
- 모습 자료: `art/requests/phase3/hero_grom/` (concept.png, portrait.png), 등록 시트 `assets/art/sheets/sheet_hero_grom.png`, art-inbox 원본 `art/inbox/sheet_hero_grom.png`.
- 납품: art-inbox 에 `art/inbox/gait/sheet_hero_grom_run_a.png` + `_b.png` (파일 이름은 부류와 상관없이 `_run_`), `art/inbox/NOTES.md` 에 그 캐릭터 절 + 「3D GUIDE: 도움 된 점 / 헷갈린 점」 한 줄. 요청서 README 의 이름·명령을 그대로 쓴다.
- 스스로 검사: 요청서의 `check_delivery.py` / `add_gait.py --dry-run` 명령.
- 판단은 주인이 한다. 이 줄을 REVIEW 로, `gpt-qa.md` 에 G10 절.


## 다시 그리기 (11-28, 주인: 「마네킹 개정판은 괜찮아 보여」)
처음 납품은 주인이 돌려보냈다(창끝 휨·대검/철퇴 휘청·뒷발 튐·발만 뒤로 빠짐). 원인은 마네킹 걸음과 요청서 문구였고 둘 다 고쳤다 — **안내 그림과 README 가 새것이다. 처음부터 다시 그린다(예전 납품을 고쳐 쓰지 말 것).** 특히:
- 중량·로브의 칸 이름은 **닿기(CONTACT) – 내려앉기(DOWN) – 지나가기(PASSING) – 앞으로 뻗기(REACH)**. 4·8번째 칸에서 흔드는 발은 **엉덩이보다 앞**이다(뒤로 밀지 말 것). 어떤 픽셀도 칸 가장자리 x=32/351 에 닿지 않는다.
- README 의 「머리 꼭대기 높이」는 **머리만**이다 — 무기는 그보다 위로 가도 된다. 무기를 그 줄 아래로 구겨 넣지 말 것.
- **무기는 하나의 단단한 물체**: 곧게, 매 칸 같은 길이, README 표의 각도대로. 대기 그림의 무기를 쥔 주먹을 축으로 통째로 돌려 쓴다. 두 손 무기는 두 주먹이 같은 자루 선 위.
- 납품 전에 `python3 tools/mannequin3d/delivery.py`(receive.py 가 부른다) 결과를 NOTES 에 붙인다 — 4/8칸 발이 엉덩이 뒤면 FAIL.
