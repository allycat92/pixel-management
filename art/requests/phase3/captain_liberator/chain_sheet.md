# 카토 — 주먹과 사슬 전투 시트 · sheet/captain/liberator/chain-sheet

## THIS ROUND · Antigravity
대기 1컷 `2391081bb9d50b58faad3253980f91766aee9940`은 PNG 규격 검사와 1× 판독을 통과했다. 첫 칸 대기는 픽셀 그대로. 새로 그리는 건 준비·접촉·피격 세 자세만이다. 주인의 기존 디자인(사슬과 주먹, 등에 고정된 장검)을 유지한다. 옛 손 장검 시트나 가이드의 팔·무기 지시는 적용하지 않는다.

- 디자인: [portrait_800.jpg](portrait_800.jpg), art-inbox `2391081`의 `art/inbox/check_sheet_captain_liberator_idle.png` 및 Aseprite 원본. [화풍 기준](../../../../assets/art/sheets/sheet_captain_blademaster.png)은 명암·외곽 참고만. 초상화나 대기 컷을 못 열면 그리지 말고 막힘을 적는다.
- 같은 4등신 체격·크기·발 기준, 오른쪽 3/4, 양손 족쇄와 사슬, 등의 장검. 손에 든 검·방패 없음. 준비는 무게를 뒤로 모으고 대기와 구분, 접촉은 주먹을 몸 밖에서 읽히게, 피격은 체중이 뒤로 빠지는 비대칭 반응. 사슬 배치는 헤드 판단으로 하되 1×에서 얇은 실선이 되지 않게. 잔상·투사체·효과·글자 없음. 전투 규칙/구현은 변경하지 않는다.
- 1536×1024, 1×4, 대기·준비·접촉·피격 순, y=870, 칸과 바깥 사방 32px 이상, 단색 #FF00FF. 게임 미리보기는 0.18/셀 112(대기 51×76px, 비교 0.1654/47×69px). 실제 등록 배율은 이후 전투 QA에서 비교하고 결정한다.
- 새 파일만 납품: `art/inbox/sheet_captain_liberator_chain.png` 및 `art/inbox/aseprite/sheet_captain_liberator_chain.aseprite`. 대기 시안/옛 시트/게임 에셋은 덮어쓰지 않는다.
- `python tools/art/check_delivery.py art/inbox/sheet_captain_liberator_chain.png --layout 1x4 --cell 112 --aseprite art/inbox/aseprite/sheet_captain_liberator_chain.aseprite`
- `python tools/art/sheets.py art/inbox/sheet_captain_liberator_chain.png --id sheet/captain/liberator --grid 4x1 --cell 112 --scale 0.18 --dry-run --work .qa-kato-chain`
- 대기 원본과 첫 칸 일치, FAIL/잘림 0, 1×에서 사슬·주먹·등검과 준비↔접촉을 직접 비교한다. `art/inbox/NOTES.md`에 CHECK, 바뀐 세 자세, `## 판정 — sheet/captain/liberator/chain-sheet`를 남긴다. 실제 게임 QA는 별도 Codex 일감이다.
