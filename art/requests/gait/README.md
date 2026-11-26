# 직업별 달리기 요청 (GPT 가 마네킹 위에 덧그림)

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이는 코드 달리기 대신, 확정 달리기 마네킹 `art/requests/guides/run_base/v2/` (8프레임 x 80ms) 위에 캐릭터를 프레임마다 그린다.

| 요청 | 시트 | 납품 (art-inbox) | 상태 |
|---|---|---|---|
| [`run__class_warrior/`](run__class_warrior/README.md) | `sheet/class/warrior` (방패 앞, 칼 낮게 뒤로) | `art/inbox/gait/sheet_class_warrior_run_a.png` + `_b.png` | 요청 2026-11-26 |
| [`run__captain_shadowqueen/`](run__captain_shadowqueen/README.md) | `sheet/captain/shadowqueen` 니클라 (쌍검 낮게 뒤로, 망토·머리 늦게 따라옴) | `art/inbox/gait/sheet_captain_shadowqueen_run_a.png` + `_b.png` | 요청 2026-11-26 |

폴더마다 같은 구성: `README.md` (한국어 머리말 + 「Prompt for GPT」 영어 블록), `guide_run_a.png` / `guide_run_b.png` (= `run_base/v2/run_base_a.png` / `_b.png` 사본, 자세·자리 가이드),
`size_run_a.png` / `size_run_b.png` (읽기용 1920x1024: 왼쪽 = 승인된 대기 자세를 흐리게 + 마네킹 R1/R5 하늘색 윤곽, 같은 배율 · 오른쪽 = 마네킹 4칸 + 바닥 줄 y=870·엉덩이 열 x=192·x=32/351 선).

받는 쪽 (클라우드): `python3 tools/art/receive.py gait/<시트 png 이름>_run` → 미리보기 확인 →
`python3 tools/art/add_gait.py <시트 id> --gait run --src <..._run_a.png> <..._run_b.png> --pose art/requests/guides/run_base/v2/pose.json`
(규격·검사: `tools/art/add_gait.py --help`, `art/requests/guides/SPEC.md` 5b절. 마네킹 픽셀은 `add_gait.py` 가 거부한다).
첫 두 캐릭터의 결과를 주인이 본 뒤 다른 시트로 넓힌다.
