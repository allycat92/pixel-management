# 도트 납품 대기열 (dot_queue)

게임 브랜치(`claude/dot-fantasy-management-game-saupju`)의 이 파일이 **무엇을 그릴 차례인지**를 정한다.
그림 쪽(도트)은 `DOT_READY` 항목만 그리고, 결과는 **`art-inbox` 브랜치의 `art/inbox/`** 에 PNG + 납품 메모(`art/inbox/NOTES.md`)로 올린다.
Claude Code 가 받아서 확인한 결과는 `art/requests/feedback.md`에 남기고, 이 표의 상태를 바꾼다.

## 상태

| 상태 | 뜻 | 누가 바꾸나 |
|---|---|---|
| `QUEUED` | 요청서·가이드는 있지만 아직 차례가 아님 — 그리지 말 것 | Claude Code |
| `DOT_READY` | 요청서·가이드 준비 완료, 그려도 됨 | Claude Code |
| `DELIVERED` | art-inbox 에 PNG·메모가 올라옴, 확인 중 | Claude Code (수령 시) |
| `ACCEPTED` | 확인 통과 → 게임에 등록됨 | Claude Code (검토 통과 시 바로 — 주인이 위임함, 2026-11-25) |
| `NEEDS_FIX` | 고칠 점이 있음 → feedback.md 참고 후 같은 이름으로 다시 납품 | Claude Code |

## 대기열

| id | 상태 | 납품 PNG (art-inbox) | 요청서 | 포즈 가이드 | 메모 |
|---|---|---|---|---|---|
| `sheet/hero/kai` | **ACCEPTED** (2026-11-25 등록: `sheet/hero/kai`) | `art/inbox/sheet_hero_kai.png` | `art/requests/phase3/hero_kai/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_kai/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 납품 시운전 1호. 디자인 기준 `portrait.png`(승인된 초상화), 화풍 기준 art-inbox 의 `art/inbox/sheet_captain_blademaster.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 카이 (시운전)」. 수령: art-inbox `09d981f`, 검토 결과 `art/requests/feedback.md` 「도트 납품 시운전 1호」 |
| `sheet/hero/seraphine` | **ACCEPTED** (2026-11-25 등록, art-inbox `6505e61`) | `art/inbox/sheet_hero_seraphine.png` | `art/requests/phase3/hero_seraphine/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_seraphine/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 세라핀. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 세라핀」. 무기는 짧은 플랜지 철퇴 |
| `sheet/hero/lyra` | **NEEDS_FIX** (단검이 대기·준비에서 안 보임 — feedback.md 「리라」) | `art/inbox/sheet_hero_lyra.png` | `art/requests/phase3/hero_lyra/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_lyra/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 리라. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 리라」. 단검 하나(역수), 반가면 유지 |
| `sheet/hero/grom` | **ACCEPTED** (2026-11-25 등록, art-inbox `7a86b4a`) | `art/inbox/sheet_hero_grom.png` | `art/requests/phase3/hero_grom/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_grom/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 그롬. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 그롬」 |
| `sheet/hero/astel` | **ACCEPTED** (2026-11-25 등록, art-inbox `67fc9a4`) | `art/inbox/sheet_hero_astel.png` | `art/requests/phase3/hero_astel/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_astel/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 아스텔. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 아스텔」 |
| `sheet/hero/marisol` | **DOT_READY** | `art/inbox/sheet_hero_marisol.png` | `art/requests/phase3/hero_marisol/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_marisol/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 마리솔. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 마리솔」 |
| `sheet/hero/oswin` | **DOT_READY** | `art/inbox/sheet_hero_oswin.png` | `art/requests/phase3/hero_oswin/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_oswin/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 오스윈. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 오스윈」 |

## 납품 규칙 (요약)

- 읽기: 이 브랜치(`claude/dot-fantasy-management-game-saupju`)의 요청서·가이드·`art/requests/gpt_handoff_notes.md`.
- 쓰기: `art-inbox` 브랜치의 `art/inbox/`만. 파일 이름은 표의 이름 그대로. `art/inbox/` 밖은 고치지 않는다.
- 납품 메모: `art/inbox/NOTES.md`에 항목별 절 — 만든 파일, 가이드와 다르게 한 점, 다시 그리고 싶은 점.
- `DOT_READY` 항목을 위에서부터 하나씩 그린다. 하나를 올릴 때마다 커밋·푸시하고, `DOT_READY`가 남아 있으면 다음 것으로 넘어가도 된다.
- `QUEUED`·`NEEDS_FIX`(고칠 점이 feedback.md 에 있을 때만 다시 그림)·`DELIVERED`·`ACCEPTED`는 건드리지 않는다. `DOT_READY`가 없으면 멈춘다.
- Claude Code 가 art-inbox 를 주기적으로 확인해서 수령·검토하고 feedback.md 와 이 표를 갱신한다.
