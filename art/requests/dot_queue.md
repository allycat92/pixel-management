# 도트 납품 대기열 (dot_queue)

게임 브랜치(`claude/dot-fantasy-management-game-saupju`)의 이 파일이 **무엇을 그릴 차례인지**를 정한다.
그림 쪽(도트)은 `DOT_READY` 항목만 그리고, 결과는 **`art-inbox` 브랜치의 `art/inbox/`** 에 PNG + 납품 메모(`art/inbox/NOTES.md`)로 올린다.
Claude Code 가 받아서 확인한 결과는 `art/requests/feedback.md`에 남기고, 이 표의 상태를 바꾼다.

## 상태

| 상태 | 뜻 | 누가 바꾸나 |
|---|---|---|
| `DOT_READY` | 요청서·가이드 준비 완료, 그려도 됨 | Claude Code |
| `DELIVERED` | art-inbox 에 PNG·메모가 올라옴, 확인 중 | Claude Code (수령 시) |
| `ACCEPTED` | 확인 통과 → 게임에 등록됨 | Claude Code (주인 승인 후) |
| `NEEDS_FIX` | 고칠 점이 있음 → feedback.md 참고 후 같은 이름으로 다시 납품 | Claude Code |

## 대기열

| id | 상태 | 납품 PNG (art-inbox) | 요청서 | 포즈 가이드 | 메모 |
|---|---|---|---|---|---|
| `sheet/hero/kai` | **DELIVERED** (확인 통과 — 주인 승인 후 등록) | `art/inbox/sheet_hero_kai.png` | `art/requests/phase3/hero_kai/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_kai/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 납품 시운전 1호. 디자인 기준 `portrait.png`(승인된 초상화), 화풍 기준 art-inbox 의 `art/inbox/sheet_captain_blademaster.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 카이 (시운전)」. 수령: art-inbox `09d981f`, 검토 결과 `art/requests/feedback.md` 「도트 납품 시운전 1호」 |

## 납품 규칙 (요약)

- 읽기: 이 브랜치(`claude/dot-fantasy-management-game-saupju`)의 요청서·가이드·`art/requests/gpt_handoff_notes.md`.
- 쓰기: `art-inbox` 브랜치의 `art/inbox/`만. 파일 이름은 표의 이름 그대로. `art/inbox/` 밖은 고치지 않는다.
- 납품 메모: `art/inbox/NOTES.md`에 항목별 절 — 만든 파일, 가이드와 다르게 한 점, 다시 그리고 싶은 점.
- 한 항목을 끝내면 멈춘다 (다음 항목은 이 표에 `DOT_READY`가 붙을 때).
