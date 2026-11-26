# 뼈대(마네킹) 세트 목록

공통 규칙: `SPEC.md` (캔버스·레이어·관절 점·검사). 동작 계획: `docs/plans/2026-11-26_motion_frames.md`. 설계표: `tools/art/specs/motion_bible.json` + `motion_chars.json`.
PC 는 `art/requests/dot_queue.md` 에 `담당: PC(Aseprite)` 줄이 있는 세트만 한다 — 이 목록은 안내일 뿐 일감 표가 아니다.

| 세트 | 무엇 | 상태 (2026-11-26) | 납품 (art-inbox) |
|---|---|---|---|
| `walk_base` | 걷기 8프레임 (v2 초안 + PC 다듬기) | 보류 — 참고용(전투 이동은 달리기, 주인 결정) | `art/inbox/guides/walk_base/` |
| `run_base` | 달리기 8프레임 (v1 초안을 PC 가 완성) | DOT_READY · PC | `guides/run_base/run_base.aseprite` |
| `atk__class_warrior` | 병과 전사 공격 7프레임 — 방패 치기 → 칼 베기 | 요청서 있음, 대기열 줄 아직 없음 · 첫 관문 | `guides/atk__class_warrior/atk__class_warrior.aseprite` |
| `atk__captain_shadowqueen` | 니클라 공격 7프레임 — X 감기 → 낮은 가위 베기(승인 칸에 맞춤) | 요청서 있음, 대기열 줄 아직 없음 · 첫 관문 | `guides/atk__captain_shadowqueen/atk__captain_shadowqueen.aseprite` |
| `atk__captain_ironwall` | 브리긴다 공격 7프레임 — 탑 방패 밀치기 (마네킹만) | 요청서 있음, 대기열 줄 아직 없음 · 첫 관문 | `guides/atk__captain_ironwall/atk__captain_ironwall.aseprite` |
| `atk__class_archer` | 병과 궁수 공격 7프레임 — 당기기 → 놓기 (마네킹만) | 요청서 있음, 대기열 줄 아직 없음 · 첫 관문 | `guides/atk__class_archer/atk__class_archer.aseprite` |
| `hit__class_warrior` | 병과 전사 피격 4프레임 — 보통 무게 | 요청서 있음, 대기열 줄 아직 없음 · 첫 관문 | `guides/hit__class_warrior/hit__class_warrior.aseprite` |
| `hit__captain_shadowqueen` | 니클라 피격 4프레임 — 가벼움, 휘청 한 걸음 | 요청서 있음, 대기열 줄 아직 없음 · 첫 관문 | `guides/hit__captain_shadowqueen/hit__captain_shadowqueen.aseprite` |

## 동작 마네킹의 공통 약속 (6세트 모두)
- 세트 이름 = `<동작>__<시트 파일 이름에서 sheet_ 를 뺀 것>` (`atk__` 공격, `hit__` 피격, `idle__` 대기).
- 요청 = `art/requests/guides/<세트>/README.md` (초안 없음 — 클라우드는 동작 마네킹 초안을 굽지 않는다). 납품 = art-inbox `art/inbox/guides/<세트>/<세트>.aseprite` **하나**(스크립트를 썼으면 옆에 `mannequin_pc.py`).
- 레이어: Background · (weapon_back) · arm_far · (shield) · leg_far · leg_near · torso · head · (weapon_front) · arm_near · joints(숨김). Aseprite 프레임 하나 = 동작 프레임 하나, 프레임 시간 = 설계표 ms, 동작 이름 태그 하나(`attack` / `hit` / `idle`).
- 검사(PC 가 납품 전에, 클라우드가 수령 때): `python3 tools/art/check_skeleton.py <세트>.aseprite --motion <attack|hit|idle> --set <세트>` — 프레임 PNG 는 클라우드가 `receive.py` 로 뽑는다.
- 첫 관문(클라우드): `python3 tools/art/gate_page.py gate1.html <세트.aseprite 또는 프레임 폴더> ...` — 효과 없이 게임 크기·1배속 실제 시간으로 한 번씩 틀고 속임 판을 섞어, 보는 사람이 맞는 순간 프레임을 고르는 한 장짜리 페이지.
  통과 = 5명(또는 주인 혼자 5회) 중 4번 이상 맞는 순간(±1), 속임 판에서도 옮긴 쪽. 대역 시험: `python3 tools/art/gate_page.py /tmp/g.html art/requests/guides/run_base/v1/run_base.aseprite@0 art/requests/guides/walk_base/v2/walk_base.aseprite@0`.

다른 파일: `attack_notes.md` (주인이 준 공격 동작 예시에서 읽은 것).
