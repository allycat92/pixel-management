# 고블린 전투 시트 — sheet/monster/goblin

**DOT_READY · Antigravity · 2026-11-27**. 백랑의 대리 운영 지시에 따라 작성. 플레이테스트 A1에서 기존 코드 도트가 전투 시트·배경과 어긋난다고 보고된 건이다. 전투 데이터, 몬스터 이름, 게임 등록은 이번 범위가 아니다.

## DESIGN

일반 고블린. `ENEMIES['고블린']` / `MONSTER_TPL.imp`의 핵심은 **작게 웅크린 녹색 몸, 양옆으로 솟은 뾰족귀, 황금빛 눈, 닳은 갈색 옷과 짧은 둔기 실루엣**이다. 기존 작은 타일의 픽셀이나 덩어리 렌더링을 복제하지 않는다. 고블린 왕의 관·장식·거대한 체격은 넣지 않는다. 피부는 탁한 이끼색 계열, 옷과 둔기는 흙색으로. 귀와 무기를 몸에서 분리해 읽히게 한다. 일반 인간보다 작게: 대기 자세 머리끝~발바닥 약 310–350px(게임 약 51–58px). 네 자세에서 머리·몸·무기 크기를 고정한다.

- 설계 원본: [현행 몬스터 데이터](../../../../js/content.js), [현행 도트 템플릿](../../../../js/sprites.js). [A1 재현과 스크린샷](../../../../docs/agents/reports/antigravity.md)은 기존 화풍 충돌 확인용.
- 스타일/크기 기준: [해골 병사 등록 시트](../../../../assets/art/sheets/sheet_monster_skeleton.png), [사막 도적 등록 시트](../../../../assets/art/sheets/sheet_monster_desert-bandit.png). 외곽과 명암 밀도만 비교하고 픽셀이나 실루엣을 가져오지 않는다. 별도 콘셉트/마네킹은 없다. 아래 포즈와 규격을 기준으로 하며 형태·질감 판단은 Antigravity가 한다.
- 대기: 무릎을 굽히고 짧은 둔기를 몸 옆에 든다. 준비: 무게를 뒷발로 옮기고 둔기를 뒤로 뺀다. 타격: 앞발로 짧게 디디며 둔기를 앞으로 휘두른 순간. 피격: 상체와 귀가 뒤로 젖혀지되 공격으로 오해할 팔 동작은 피한다. 네 자세 모두 같은 방향(오른쪽의 상대를 봄).

## FORMAT

- 1536×1024, 1x4. 한 줄 왼쪽부터 대기 / 준비 / 타격 / 피격. 각 최저 픽셀 y=870. 그림끼리와 외곽 모두 32px 이상 여백.
- 배경은 완전히 평평한 `#FF00FF`. 인물 색은 키 색과 RGB 거리 150 이상. 바닥·투사체·효과·잔상·텍스트 없음.
- art/inbox/sheet_monster_goblin.png 한 장과 편집본 `art/inbox/aseprite/sheet_monster_goblin.aseprite`을 `art-inbox`에만 납품. 게임 에셋 등록이나 코드 수정은 하지 않는다.

## SELF-CHECK

```sh
python3 tools/art/check_delivery.py art/inbox/sheet_monster_goblin.png --layout 1x4 --cell 96
python3 tools/art/sheets.py art/inbox/sheet_monster_goblin.png --id sheet/monster/goblin --grid 4x1 --scale 0.1654 --cell 96 --dry-run --work /tmp/goblin-preview
```

- 검사 FAIL 없이, 변환 시 잘림이나 강제 위치 보정 없는지 확인. 어두운 전장에서 실제 크기와 4배 미리보기로 대기·준비·타격·피격이 분명히 구분되는지 본다.
- `art/inbox/NOTES.md`에 CHECK 결과, CHANGED, `## 판정 — sheet/monster/goblin`와 게임 크기에서 남은 걱정을 적는다. 최종 수령은 클로드 몫이다.
