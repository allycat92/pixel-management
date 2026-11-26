# C5-art-battle-integration-qa — 납품 시트 6종 게임 반영 및 실제 전투 QA

백랑의 요청(11-27 KST): 이 작업은 **Codex 담당**. 안티그래비티는 새 그림을 진행한다. C4는 취소하지 않되 이 검수를 먼저 한다(이미 진행 중이라면 현재 측정을 안전하게 마무리하고 이어서). 새 그림이나 전투 규칙 변경은 범위 밖이다.

## 소스와 검증 범위

| 원본 art-inbox 커밋 | 파일(art/inbox/) | 실제 게임 manifest 키 |
|---|---|---|
| `5520f3529df36a81bf496159895fca7f2647bf7f` | sheet_captain_frostjarl.png / sheet_hero_kai.png | `sheet/captain/frostjarl` / `sheet/hero/kai` |
| 같은 커밋 | sheet_monster_skeleton.png / sheet_monster_desert-bandit.png | `sheet/monster/해골 병사` / `sheet/monster/사막 도적` |
| `c4cc05408f630628cfcd8bc4fcead5148ff34840` | sheet_monster_goblin.png / sheet_monster_frost-troll.png | `sheet/monster/고블린` / `sheet/monster/서리 트롤` |

1. 최신 게임 브랜치를 기준으로 **별도 임시 worktree/복사본**을 하나 만든다. 원본 PNG를 위 커밋에서만 꺼내고, 각 해시를 기록한다. 기존 `assets/`, 플레이 저장, `art-inbox` 브랜치에는 손대지 않는다. 이 **검증용 복사본 안에서만** 실제 PNG와 manifest를 적용한다. 최종 배포·병합·등록 판정은 Claude에게 남긴다.
2. `tools/art/check_delivery.py`와 `tools/art/sheets.py`로 검사·변환한다. 기존 넷은 `art/requests/phase3.json`의 규격·스팟 색·배율을 유지하고 기존 manifest 파일명, 셀, 앵커, facing, 이동 애니메이션이 사라지지 않는지 비교한다. 기존 결함 대비 필요 시 직전 `ef09ce9638871c9809f52458df8860ba7fc01d15`를 `--base`로 준다. 고블린/트롤은 각각 4x1/2x2, 0.1654/0.1800, 셀 96. **변환 id는 표의 실제 한글 몬스터 이름**(요청서의 영문 미리보기 id는 검증용 별칭뿐)으로 명시한다. `--dry-run`만 하고 끝내지 말고 격리본에 등록 후 앱을 실행한다. Aseprite 실행기나 정상 시트가 없어 실제 결과를 못 본 항목은 대체 이미지로 통과시키지 말고 명시한다.
3. 임시 서버/새 브라우저 프로필에서 전투 화면까지 실제로 실행한다. 가능하면 같은 장소·시드의 적용 전/후로 여섯 캐릭터를 각각 발동시켜 스프라이트가 (fallback이 아닌) 해당 파일로 로드되는지, 방향·발/앵커·클리핑·크기, 대기/준비/접촉/피격의 구분을 확인한다. 비요른 도끼, 카이 시위 손, 해골 무기 끝, 사막 도적 타격 위치, 고블린의 어두운 배경 대비, 트롤의 크기와 보폭을 우선한다. 기본 1×로 보고 필요 시 배속도 짧게 확인한다. 재현에 테스트 상태가 필요하면 격리본에서만 만들고, 브라우저 저장이나 로직 변경을 커밋하지 않는다. 잡히지 않는 자세·유닛은 미확인으로 표시한다.

## 납품

- `docs/agents/reports/codex.md`에 개발 기준 SHA, 원본 SHA/경로, 변환·등록 재현 명령과 manifest의 변경 키, 전투 시드/경로, 유닛별 PASS/FIX/미확인 및 문제를 적는다. 실제 전투 캡처는 `docs/agents/reports/shots/C5-art-battle-integration-qa/`에 각 500KB 미만으로 첨부한다. 비밀·개인 저장 데이터는 제외한다.
- 임시 빌드 등록을 완료하고 이상이 없으면 **그대로 최종 반영 가능한 절차**를 쓰고, 실패/미확인 시 무엇을 고쳐야 하는지 쓴다. 미승인 아트·코드·manifest는 원격에 올리지 않는다. `agent/codex`에 보고/캡처와 이 행의 REVIEW만 커밋·푸시한다. 게임 브랜치/아트 브랜치엔 푸시하지 않는다.
