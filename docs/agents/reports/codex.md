## C1 — 2026-11-26

V11을 바탕으로 걷는 유닛에 보정을 우선 적용하고, 궤주 유닛은 아군과의 충돌에서 제외했다. 한쪽만 돌진한 경우 돌진한 쪽에 보정량을 모두 적용한다. 제자리 유닛끼리 깊게 겹치면 조금씩 벌린다. 회피와 자리 점유 검사에 좌표 범위 사전 검사를 넣었다.

- 같은 보고서 100개와 결과 4종으로 전후를 비교했다. 승패 불일치와 소프트 미스는 모두 0건이었다.
- `node tools/sim/battle.js 100` 수정 후 결과

```text
reports 100 × 4 outcomes = 400 findBattle calls (game seeds 1..3)
win/lose mismatches: 0
soft misses (great with >25% loss / disaster with <50% loss): 0
slow battles (>=60 s): 0, time-limit (90 s) battles: 0
findBattle avg 34.4 ms, max 315 ms
  great    n=100 miss=0 soft=0 avg 20.1 ms, battle 19.9 s
  success  n=100 miss=0 soft=0 avg 77.0 ms, battle 31.5 s
  fail     n=100 miss=0 soft=0 avg 21.5 ms, battle 25.5 s
  disaster n=100 miss=0 soft=0 avg 18.8 ms, battle 22.5 s
```

- 기준 전투 시간은 같은 순서로 19.1 / 28.8 / 23.6 / 20.5초였다. 탐색 평균·최대는 35.0 / 289 ms에서 34.4 / 315 ms로 변했다.
- `node tools/sim/bot.js` 전후 요약 출력 동일. 12 × 365일, S등급 12회, 파산 0회, 완료 / 실패 / 전사 632 / 33 / 0.
- 선택된 전투 400건을 계측해 자력 이동 없이 충돌 보정으로 위치가 바뀐 비율이 20.07% (573201/2856611)에서 0.04% (1303/3064184)로 줄어든 것을 확인했다.
- 15초 이상 전장에 남아 공격하지 않은 근접 유닛은 1.53% (38/2485)에서 2.08% (53/2544)로 변했다.
- 서 있는 아군끼리 정규화 거리 0.5 미만이 연속된 최장 시간은 0.00초에서 0.30초로 변했다.
- Chrome에서 왕도 크라운홀 습격을 1배속으로 재생해 의뢰 성공 화면까지 확인했다. 교전 중 확인한 화면에서 서 있는 유닛이 아군에게 밀려 미끄러지는 모습은 보이지 않았다. 개발자 콘솔에 JavaScript 오류는 없었고, `favicon.ico` 요청만 404였다.

## C2 — 2026-11-26

1. 첫 대장 카드가 400px에서 한 열로 쌓인다. 1280px에서는 선택창에 스크롤 하나만 남고, 후보 9명 표시와 두 번째 행의 초상화가 보인다.
2. 최종 결전과 만료일 값이 `99999`인 의뢰에 「마감 없음」을 표시한다. 의뢰의 남은 마감일을 표시하는 곳은 의뢰 카드 한 곳이다.
3. 대장 영입은 기존대로 숙소와 무관하게 처리하고, 숙소 점유 수와 일반 고용 조건에서 대장을 뺐다. 7명 합류 상태에서 숙소 점유는 5/6이다. 출격 기록이 8일 넘게 없는 예비 대장의 사기 65가 수정 전에는 63으로 떨어졌고 수정 후에는 65였다.
4. 컷인을 전투 캔버스 영역에 잘랐다. 두 폭에서 바렌의 회전베기 컷인을 확인했다.
5. 아군 대장 대화에 금색 초상화 테두리를 적용하고, 같은 대화의 내레이션 차례에는 초상화를 숨겼다.
6. 모집소 상단에 대원 모집과 용병단 시장을 배치했다. 대장 목록은 아래에서 볼 수 있다.
7. 출격 상태와 직업 계통도에 어절 단위 줄바꿈을 적용했다. 400px에서 「귀환」 두 글자가 함께 표시된다.
8. 받침에 맞는 조사를 적용했다. 파산 도움말을 「금화가 -300 아래로 떨어지면」으로 고쳤고, 첫날 전쟁 경과는 「1일째」, 명성 보정 0%는 「없음」, 마감일 당일은 「오늘 마감」으로 표시한다.
9. 이름이 같은 적 부대에 번호를 붙였다. 두 명을 파견한 고블린 전투의 현황판에서 「2 + 수습 1」과 「고블린 무리 1/2」를 확인했다.
10. 게임 팔레트로 만든 16×16 파비콘을 연결했다. 기존 `/favicon.ico`는 404, 새 링크 `/favicon.png`는 200이며 Chrome에서 16×16 이미지로 로드됐다.
11. 출격 인원 문구를 길드 홀 왼쪽 위에 옮기고 어두운 배경을 넣었다. 400px 탭 바 아래에 가로 스크롤 안내를 표시한다.
12. 지도 지명에 불투명한 어두운 배경과 밝은 글자를 적용했다. 자물쇠는 수도 별에서 오른쪽으로 떨어뜨렸다.

`node tools/sim/battle.js 100`

```text
reports 100 × 4 outcomes = 400 findBattle calls (game seeds 1..3)
win/lose mismatches: 0
soft misses (great with >25% loss / disaster with <50% loss): 0
slow battles (>=60 s): 0, time-limit (90 s) battles: 0
findBattle avg 32.0 ms, max 283 ms
  great    n=100 miss=0 soft=0 avg 19.2 ms, battle 19.9 s
  success  n=100 miss=0 soft=0 avg 71.6 ms, battle 31.5 s
  fail     n=100 miss=0 soft=0 avg 20.1 ms, battle 25.5 s
  disaster n=100 miss=0 soft=0 avg 17.2 ms, battle 22.5 s
```

`SIM_JSON=1` 봇 6회 × 200일 JSON의 전후 MD5는 `ddfdfe7b437fbe9fcf25f166ba542fce`로 동일했다. 기본 `node tools/sim/bot.js`도 실행했다. 12회 × 365일, S등급 12회, 파산 0회, 완료 / 실패 / 전사 632 / 33 / 0.

Chrome 1280×900과 400×800에서 최신 게임 브랜치 `9a30986`과 수정본을 비교했다. 최종 결전, 예비 대장 및 대화는 테스트 저장 상태를 구성해 재현했다. 수정 후 검증 중 브라우저 콘솔 오류는 0건이었다. 파비콘 캡처는 브라우저 탭 대신 리소스 응답 화면이다. [전후 화면](shots/C2/)은 모두 500 KB 미만이다.

## C3 — 2026-11-27

- 숙소가 차면 일반 대원·특별 용병·세력 정예의 모집 버튼을 끄고 버튼 옆에 「숙소가 가득 찼습니다. 숙소를 증축하세요.」를 표시한다. 대장에게는 숙소 제한을 적용하지 않는다.
- 1280px와 400px의 Chrome 테스트 저장 상태에서 카이와 엘프 정예를 확인했다. 6/6에서 비활성 및 안내 표시, 5/6에서 활성 및 안내 숨김, 금화 0에서 비활성이었다. 콘솔 오류 0건. [화면 캡처](shots/C3/)
- 봇 6회 × 200일 JSON의 MD5는 기준과 동일한 `ddfdfe7b437fbe9fcf25f166ba542fce`였다. 기준 브랜치와 봇 입력 파일이 동일함을 확인했다.

```text
reports 100 × 4 outcomes = 400 findBattle calls (game seeds 1..3)
win/lose mismatches: 0
soft misses (great with >25% loss / disaster with <50% loss): 0
  great    n=100 miss=0 soft=0 avg 20.6 ms, battle 19.9 s
  success  n=100 miss=0 soft=0 avg 77.4 ms, battle 31.5 s
  fail     n=100 miss=0 soft=0 avg 21.5 ms, battle 25.5 s
  disaster n=100 miss=0 soft=0 avg 18.5 ms, battle 22.5 s
```

## C5-art-battle-integration-qa — 2026-11-27

게임 기준은 `48dde80c326c881c591fbda5934b2c0f51a04955`다. `git archive`로 적용 전후 임시 복사본을 만들었다. 아래 원본은 모두 `art/inbox/` 상대 경로이며, 해시는 추출한 PNG의 SHA-256이다.

| 원본 커밋 | 파일 | SHA-256 |
|---|---|---|
| `5520f3529df36a81bf496159895fca7f2647bf7f` | `sheet_captain_frostjarl.png` | `c5d251e925d67a73634d41d9f7556db0030536e7084575d131f78d6944e1f881` |
| 같은 커밋 | `sheet_hero_kai.png` | `fa6a379f48c6d7a210a2169b34e1565297f38d7068c99496d77083610771ee77` |
| 같은 커밋 | `sheet_monster_skeleton.png` | `e6b4ff52c0e15bed1e6fffac3eaf2c2ab87ff347a8a5dbd31d26875d85c8ab2d` |
| 같은 커밋 | `sheet_monster_desert-bandit.png` | `686c37be609216fb3f85f6575013815cadd3e593894a3b47f26592ed9e33ed38` |
| `c4cc05408f630628cfcd8bc4fcead5148ff34840` | `sheet_monster_goblin.png` | `2f3b2730aba949b472d2826bbc89391aff9729f190505c9a9fbd04418be9d486` |
| 같은 커밋 | `sheet_monster_frost-troll.png` | `61585b5f4e93ff220f97e342e740b617c4a9de72105b088a6036ce77fa06d17f` |

재현은 임시 복사본에서 각 PNG에 대해 아래 명령을 실행한다. Windows PowerShell 5에서는 Git 바이너리 출력을 `>`로 쓰지 말고 프로세스의 표준 출력을 파일로 리디렉션한다.

```sh
git cat-file blob "<커밋>:art/inbox/<PNG>" > "<임시빌드>/art/inbox/<PNG>"
python tools/art/check_delivery.py "art/inbox/<PNG>"
python tools/art/sheets.py "art/inbox/<PNG>" --id "<manifest 키>"
```

기존 넷의 키는 `sheet/captain/frostjarl`, `sheet/hero/kai`, `sheet/monster/해골 병사`, `sheet/monster/사막 도적`이다. `phase3.json` 기본값이 적용됐으며 해골의 `#ff4a3a`는 네 자세에 2/3/2/2px 남았다. 새 키 `sheet/monster/고블린`과 `sheet/monster/서리 트롤`은 검사에 각각 `--layout 1x4 --cell 96`, `--layout 2x2 --cell 96`을, 변환에 각각 `--grid 4x1 --scale 0.1654 --cell 96`, `--grid 2x2 --scale 0.1800 --cell 96`을 추가했다.

PNG 검사 6/6 통과, 임시 등록 6/6 성공. 비요른 키 경고는 대장 유휴 높이 373px, 카이는 원본 색 111,683개와 마젠타 근접색 809개였다. 기존 넷은 PNG가 교체됐고 manifest 항목은 값까지 동일했다. 파일명, 96×96 셀, 앵커 (48,92), facing 1, 태그 idle(4)/attack(2)/hit(1)을 유지했다. 기존 넷 모두 등록 전부터 walk/run 태그가 없었다. manifest는 새 키 둘만 추가되어 113→115였다. 이 환경에서 Aseprite 실행 파일을 찾지 못해 편집 원본과 PNG의 동일성은 미확인이다. sprite-gen 실행기 부재로 변환기는 내장 idle 들썩임을 사용했다. 아카이브 복사본의 마네킹 대조 범위는 체크아웃에 포함된 가이드였다.

로컬 HTTP와 새 Chrome 프로필, 1280×900 / DPR 1 / 전투 속도 ×1에서 `index.html`의 `UI.openModal(Battle.play(report, ...), true)`로 재현했다. 테스트 보고서는 성공 결과, 3레벨 의뢰, 비요른과 카이가 속한 직속 용병단을 사용했다. 전후 각각 같은 보고서 시드와 리플레이 시드를 사용했고 10회 재생에서 페이지 오류 0건이었다.

| 대상 전투 | 지방 | 보고서 / 재생 시드 |
|---|---|---|
| 해골 병사 | `frost` | 2701 / 3004 |
| 사막 도적 | `oasis` | 2702 / 2904 |
| 고블린 | `royal` | 2703 / 3006 |
| 서리 트롤 | `frost` | 2704 / 2906 |
| 고블린 어두운 배경 추가 재현 | `deepwood` | 2703 / 3208 |

대상 6종 모두 적용 후 실제 전투의 캔버스 그리기에서 지정 PNG와 idle 4칸, 준비·접촉 2칸, 피격 1칸 호출을 관측했다. 고블린과 트롤의 적용 전 manifest에는 해당 키가 없어 기본 도트로 나왔다. 아래 판정은 이 빌드와 관측 장면 기준이다.

| 유닛 | 판정 | 관찰 |
|---|---|---|
| 비요른 | PASS | 아군 방향과 도끼 실루엣을 확인했다. 피격 변환의 발 맞춤은 발바닥 기준보다 -13px로 기록됐다. |
| 카이 | 미확인 | 활 방향과 발사 장면은 확인했다. 1× 전투에서 시위 손의 손가락 단위 접점은 판독하지 못했다. |
| 해골 병사 | PASS | 방패와 돌출된 무기 끝이 보이고 관측 화면에서 끝이 잘리지 않았다. |
| 사막 도적 | FIX | 공격은 읽히나 접촉 칸에서 3px 밀어 넣어 발이 앵커에서 벗어났다. 피격 발 맞춤은 발바닥 기준 -12px다. 공격 자세 폭과 기준 발을 재검토할 것. |
| 고블린 | FIX | 외곽선이 켜진 숲 화면에서는 구분된다. 어두운 녹색·갈색 몸통의 내부 명암과 겹친 실루엣은 읽기 어렵다. 배경 대비를 재검토할 것. |
| 서리 트롤 | 미확인 | 유휴 높이 74px, 설원에서 몸집·대면 방향·피격을 확인했다. 전용 이동 프레임이 없어 보폭 판정은 보류했다. |

최종 반영 전 Aseprite 내보내기 대조, 카이 시위 손 확인, 사막 도적 앵커와 고블린 대비 조정, 트롤 걸음 확인이 남았다. [전후 전투 캡처](shots/C5-art-battle-integration-qa/) 12장은 각 500KB 미만이다.
