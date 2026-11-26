# 직업별 달리기 요청 (GPT 가 마네킹 위에 덧그림)

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이는 코드 달리기 대신, 확정 달리기 마네킹 `art/requests/guides/run_base/v2/` (8프레임 x 80ms) 위에 캐릭터를 프레임마다 그린다.

## 이동 부류 세 가지 (주인 2026-11-26)
> "달리기(이동)에 대해 3가지 부류를 정하고 싶어. 경량, 중량, 로브. 펑퍼짐한 천 복장을 입고 뛰는것도 좀 부자연스러울거고,
> 중장비를 갖추면 당연히 뛰는건 물론이고 몸이 저렇게 땅에서 떨어지거나 몸을 앞으로 기울인 채로 가누기도 어려울테니까."

세 부류 모두 **그 몸이 낼 수 있는 가장 빠른 이동**이다(전투 이동은 달리기 — 산책이 아니다). 캐릭터는 늘 **부류의 마네킹 위에 프레임마다 덧그린다**(대기 그림을 조작하지 않는다).
시트마다 부류 하나 — 원본 `tools/art/specs/gait_classes.json` (경량 30 · 중량 7 · 로브 10 · 해당 없음 5, 시트마다 까닭과 경계 사례). 현황: `python3 tools/art/gait_requests.py`.

| 부류 | 몸 | 덧그리는 마네킹 | 요청 폴더 | 느낌 |
|---|---|---|---|---|
| **경량** light | 가죽·천(무릎까지)·사슬 셔츠+겉옷, 다리가 보이는 망토·열린 긴 외투 | `art/requests/guides/run_base/v2/` (R1~R8, 80ms, 한 걸음 게임 45.5px) **확정** | `run__<시트>/` | 앞으로 기울고, 뜬 동안 누르고, 받아낸 뒤 조금 오른다. 엉덩이는 거의 수평, 살짝 뜬 느낌, 깡충거리지 않는다 |
| **중량** heavy | 판금·온몸 금속·비늘 갑옷, 탑 방패, 아주 큰 무기를 든 몸 | `art/requests/guides/heavy_base/` (H1~H8, 110ms, 한 걸음 22.0px) **초안 `draft/` — PC 확정(`v1/`) 기다림** | `heavy__<시트>/` | 뜨는 칸이 없다(늘 한 발은 땅), 몸은 거의 선다, 디딜 때마다 무게로 가라앉는다, 무릎을 낮게, 보폭 짧게 |
| **로브** robe | 무릎 아래까지 오는 긴 로브·사제복·긴 망토로 무릎·허벅지가 가려진 몸 | `art/requests/guides/robe_base/` (G1~G8, 90ms, 한 걸음 24.0px, `cloth_front` 옷자락 레이어) **초안 `draft/` — PC 확정(`v1/`) 기다림** | `robe__<시트>/` | 서서 서두르는 종종걸음·미끄러짐, 뜨지 않음, 무릎은 옷 속에서 살짝 밀 뿐, 옷자락이 한 칸 늦게 흔들리며 다리를 가린다 |
| 해당 없음 none | 네발·다족·떠 있는 몸 (들늑대·거대 거미·가고일·망령·하피) | — (엔진의 quad·hover 움직임) | — | — |

- **엔진에는 부류와 상관없이 시트의 `anims.run` 한 줄로 붙는다**: 납품 `art/inbox/gait/<시트 png 이름>_run_a.png` + `_b.png`,
  붙이기 `add_gait.py <시트 id> --gait run --src … --pose <부류 마네킹 pose.json>` (`gait_requests.py --json` 에 시트마다 명령). 요청 폴더 머리(`run__`/`heavy__`/`robe__`)는 사람이 부류를 알아보라고 붙인 것이다.
- 엔진(`js/battle.js` `gaitClassOf`)은 시트 `meta.gait` → `js/gait_classes.js`(JSON 에서 `python3 tools/art/gait_requests.py --js` 로 만든 표) → 경량 순으로 부류를 안다.
  그려진 칸이 아직 없는 시트는 그림을 바꾸지 않고 몸 전체만 부류대로 오르내린다: 경량 0..1px(지금 그대로) · 중량 디딜 때마다 1..2px 툭 내려앉고 천천히 올라오며 걸음 수는 약 3/4 · 로브 0..1px 부드럽게.
- 중량·로브의 그려진 보폭(22~24px)은 코드 걸음(1배속 약 20px)과 거의 같아 디딘 발이 붙어 있다(칸마다 약 0.4~0.9px). 경량(45.5px)은 칸마다 약 6px 미끄러진다 — 다른 작업이 고치는 중.
- 중량·로브 요청은 마네킹이 확정(`v1/`)된 뒤에 만든다. 첫 요청은 주인이 경량 두 캐릭터를 본 뒤.

## 요청 목록

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
