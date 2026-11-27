# 서리 트롤 전투 시트 — sheet/monster/frost-troll

**DOT_READY · Antigravity · 2026-11-27**. 백랑의 대리 운영 지시에 따라 작성. 플레이테스트 A1에서 기존 코드 도트가 전투 시트·배경과 어긋난다고 보고된 건이다. 전투 데이터, 몬스터 이름, 게임 등록은 이번 범위가 아니다.

## DESIGN

일반 서리 트롤. `ENEMIES['서리 트롤']` / `MONSTER_TPL.brute`의 핵심은 **넓은 어깨, 긴 맨팔과 큰 손, 얼음색 피부, 드러난 송곳니, 어두운 남청색 허리천**이다. 작고 날랜 고블린과 달리 덩치가 무겁고 위협적이어야 하며, 기존 타일의 픽셀을 복제하지 않는다. 새 무기·갑옷·얼음 뿔·마법 발광은 추가하지 않는다. 서리 트롤은 `big: true`: 사람보다 넓고 조금 더 크게 읽히게. 대기 자세 머리끝~발바닥 약 400–425px(게임 약 72–77px); 각 자세의 높이는 칸 여백 범위 내에서 조절하되 캐릭터의 배율 자체는 바꾸지 않는다.

- 설계 원본: [현행 몬스터 데이터](../../../../js/content.js), [현행 도트 템플릿](../../../../js/sprites.js). [A1 재현과 스크린샷](../../../../docs/agents/reports/antigravity.md)은 기존 화풍 충돌 확인용.
- 스타일/크기 기준: [해골 병사 등록 시트](../../../../assets/art/sheets/sheet_monster_skeleton.png), [사막 도적 등록 시트](../../../../assets/art/sheets/sheet_monster_desert-bandit.png). 외곽과 명암 밀도만 비교하고 픽셀이나 실루엣을 가져오지 않는다. 별도 콘셉트/마네킹은 없다. 아래 포즈와 규격을 기준으로 하며 형태·질감 판단은 Antigravity가 한다.
- 대기: 어깨와 팔을 낮추고 무게를 바닥에 둔다. 준비: 치는 팔을 뒤로 당기고 어깨를 틀어 힘을 모은다. 타격: 큰 맨손을 앞·아래로 내리치는 순간, 손이 몸과 분리된다. 피격: 몸 중심은 뒤로 물러나고 양팔을 다르게 반응시킨다. 네 자세 모두 같은 방향(오른쪽의 상대를 봄).

## FORMAT

- 1536×1024, 2x2. 2×2의 각 칸 768×512. 왼쪽 위 대기, 오른쪽 위 준비, 왼쪽 아래 타격, 오른쪽 아래 피격. 각 칸의 로컬 최저 픽셀 y=461 (아래 두 칸의 전체 캔버스 y=973). 칸 경계에서 사방 32px 이상 여백.
- 배경은 완전히 평평한 `#FF00FF`. 인물 색은 키 색과 RGB 거리 150 이상. 바닥·투사체·효과·잔상·텍스트 없음.
- art/inbox/sheet_monster_frost-troll.png 한 장과 편집본 `art/inbox/aseprite/sheet_monster_frost-troll.aseprite`을 `art-inbox`에만 납품. 게임 에셋 등록이나 코드 수정은 하지 않는다.

## SELF-CHECK

```sh
python3 tools/art/check_delivery.py art/inbox/sheet_monster_frost-troll.png --layout 2x2 --cell 96
python3 tools/art/sheets.py art/inbox/sheet_monster_frost-troll.png --id sheet/monster/frost-troll --grid 2x2 --scale 0.1800 --cell 96 --dry-run --work /tmp/frost-troll-preview
```

- 검사 FAIL 없이, 변환 시 잘림이나 강제 위치 보정 없는지 확인. 어두운 전장에서 실제 크기와 4배 미리보기로 대기·준비·타격·피격이 분명히 구분되는지 본다.
- `art/inbox/NOTES.md`에 CHECK 결과, CHANGED, `## 판정 — sheet/monster/frost-troll`와 게임 크기에서 남은 걱정을 적는다. 최종 수령은 클로드 몫이다.
