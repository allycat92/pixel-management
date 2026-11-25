# 도트 납품 대기열 (dot_queue)

게임 브랜치(`claude/dot-fantasy-management-game-saupju`)의 이 파일이 **무엇을 그릴 차례인지**를 정한다.
그림 쪽은 아래 「지금 차례」의 자기 줄만 하고, 결과는 **`art-inbox` 브랜치의 `art/inbox/`** 에 PNG + 납품 메모(`art/inbox/NOTES.md`)로 올린다.
Claude Code 가 받아서 확인한 결과는 `art/requests/feedback.md`에 남기고, 이 표의 상태를 바꾼다.

## 상태

| 상태 | 뜻 | 누가 바꾸나 |
|---|---|---|
| `QUEUED` | 요청서·가이드는 있지만 아직 차례가 아님 — 그리지 말 것 | Claude Code |
| `DOT_READY` | 요청서·가이드 준비 완료, 그려도 됨 | Claude Code |
| `DELIVERED` | art-inbox 에 PNG·메모가 올라옴, 확인 중 | Claude Code (수령 시) |
| `ACCEPTED` | 확인 통과 → 게임에 등록됨 | Claude Code (검토 통과 시 바로 — 주인이 위임함, 2026-11-25) |
| `NEEDS_FIX` | 고칠 점이 있음 → 「지금 차례」의 그 줄과 꾸러미 README 의 THIS ROUND 대로 같은 이름으로 다시 납품 | Claude Code |

## 지금 차례 (그림 쪽은 이 절만 보면 된다 — 위에서부터)

| 누구 | 종류 | id | 할 일 (자세한 것은 그 줄의 요청서) |
|---|---|---|---|
| GPT | fix | `sheet/monster/거대 거미` | 꾸러미 README 맨 위 **THIS ROUND**: 통과한 대기 컷(`555007c`)을 바탕으로 네 자세, 눈을 선명한 빨강으로·몸 색 차갑게 |
| GPT | new | `sheet/captain/beastmaster` | 오르가 — **막힘 답(ab4b3cd)**: 지금 초안을 그대로 납품한다. 피격 자세의 활·다리 겹침은 NOTES 의 DEVIATIONS 에 적으면 PC 가 그 자세의 활만 손질한다 |
| GPT | new | `sheet/captain/liberator` | 카토 — **막힘 답(ab4b3cd)**: 지금 초안을 그대로 납품한다. 대기 자세의 장검·의상 겹침은 DEVIATIONS 에 적으면 PC 가 그 자세의 검만 손질한다 |
| GPT | new | `sheet/captain/frostjarl` | 비요른 — 확정 무기: 양손 수염도끼 |
| GPT | new | `sheet/captain/dragonslayer` | 지크린데 |
| GPT | new | `sheet/captain/demonhunter` | 모르데카이 — 머리 110px·대기 약 400px 크기를 지킨다(크림슨이 12% 작게 왔다) |
| GPT | 검수 | `review/xcheck_03` | 걷기 뼈대 v2 확정판 3문항 (`art/requests/review/xcheck_03/README.md`) — 그림 없음, NOTES 에 OK/FIX 로 답 |

## 주인에게 물을 것 (모아서 — 답이 없으면 「기본」대로 진행한다)

| # | 질문 | 고를 것 | 기본 | 물은 날 |
|---|---|---|---|---|
| 1 | 걷기 그림의 범위 | A: 대장·특별 용병은 4자세 + 엔진 걷기, 그려 주는 것은 일반 병과 5종의 달리기·돌격 4프레임부터 / B: 모든 캐릭터에 걷기 띠 | A | 11-26 |
| 2 | 거대 거미 시안에서 꼭 남길 것 | Claude 가 읽은 여섯 가지(땅높이 옆모습 · 등보다 높은 다리 아치 · 큰 털 배 · 털 실루엣 · 반짝이는 붉은 눈 · 검보라 덩어리)가 맞는지, 빠진 것 | 여섯 가지 그대로 | 11-26 |
| 3 | 이사벨의 모자 | 초상화의 장교모 유지 / 요청서의 삼각모로 손질 | 유지 | 11-24 |
| 4 | 뼈대 만드는 방식 | 클라우드가 수치표로 초안을 만들고 PC 가 Aseprite 로 다듬기 (11-25 에는 "PC 가 따로 만들게"였다) | 이 방식으로 | 11-26 |
| 5 | 남은 대장의 무기 | 초상화·스킬 이름·이야기가 다를 때 스킬·이야기 이름을 따를지(지금까지 세 번 모두 그렇게 정하셨다) | 스킬·이야기 이름 | 11-26 |

종류: `new` 새 시트 · `fix` 같은 파일을 적힌 만큼만 · `idle-check` 대기 한 자세만 먼저 · `review` 글로만 답(교차 검수) · `뼈대`/`손질` PC 작업.
GPT 는 `art/requests/GPT_STANDING.md`, PC 는 `tools/aseprite-mcp/pc/CLAUDE.md` 대로 일한다.

## 대기열

| id | 상태 | 납품 PNG (art-inbox) | 요청서 | 포즈 가이드 | 메모 |
|---|---|---|---|---|---|
| `sheet/hero/kai` | **ACCEPTED** (2026-11-25 등록: `sheet/hero/kai`) | `art/inbox/sheet_hero_kai.png` | `art/requests/phase3/hero_kai/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_kai/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 납품 시운전 1호. 디자인 기준 `portrait.png`(승인된 초상화), 화풍 기준 art-inbox 의 `art/inbox/sheet_captain_blademaster.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 카이 (시운전)」. 수령: art-inbox `09d981f`, 검토 결과 `art/requests/feedback.md` 「도트 납품 시운전 1호」 |
| `sheet/hero/seraphine` | **ACCEPTED** (2026-11-25 등록, art-inbox `6505e61`) | `art/inbox/sheet_hero_seraphine.png` | `art/requests/phase3/hero_seraphine/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_seraphine/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 세라핀. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 세라핀」. 무기는 짧은 플랜지 철퇴 |
| `sheet/hero/lyra` | **ACCEPTED** (2026-11-25 재납품 `926c195` 등록) | `art/inbox/sheet_hero_lyra.png` | `art/requests/phase3/hero_lyra/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_lyra/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 리라. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 리라」. 단검 하나(역수), 반가면 유지 |
| `sheet/hero/grom` | **ACCEPTED** (2026-11-25 등록, art-inbox `7a86b4a`) | `art/inbox/sheet_hero_grom.png` | `art/requests/phase3/hero_grom/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_grom/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 그롬. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 그롬」 |
| `sheet/hero/astel` | **ACCEPTED** (2026-11-25 등록, art-inbox `67fc9a4`) | `art/inbox/sheet_hero_astel.png` | `art/requests/phase3/hero_astel/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_astel/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 아스텔. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 아스텔」 |
| `sheet/hero/marisol` | **ACCEPTED** (2026-11-25 등록, art-inbox `838857f`) | `art/inbox/sheet_hero_marisol.png` | `art/requests/phase3/hero_marisol/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_marisol/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 마리솔. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 마리솔」 |
| `sheet/hero/oswin` | **ACCEPTED** (2026-11-25 등록, art-inbox `cd09ed7`) | `art/inbox/sheet_hero_oswin.png` | `art/requests/phase3/hero_oswin/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/hero_oswin/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 특별 용병 오스윈. 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 오스윈」 |
| `sheet/monster/거대 거미` | **NEEDS_FIX** | `art/inbox/sheet_monster_giant-spider.png` | `art/requests/phase3/monster_giant-spider/README.md` 맨 위 **THIS ROUND** (대기 컷 `555007c` 조건부 통과 — 눈을 선명한 빨강으로·몸 색을 차갑게+림 라이트, 나머지 세 자세) | `art/requests/phase3/monster_giant-spider/guide_layout.png` | 다시 그리기 2(주인 피드백): `77c9e8f` 는 시안의 좋은 점이 빠짐(위에서 본 납작한 장난감 거미·회색 다리·매끈한 몸). 시안처럼 땅높이 옆모습·높이 휜 털 많은 검보라 다리·큰 털 배·붉은 눈 무리로 돌아가고, 다리는 디딘 채 몸·독니로 위협→물기. 같은 이름으로 덮어쓰기 (그때까지 지금 것을 임시로 씀) |
| `sheet/class/archer` | **ACCEPTED** (2026-11-25 PC 손질 `9b72e75` 등록) | `art/inbox/sheet_class_archer.png` | `art/requests/phase3/class_archer/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/class_archer/guide_strip.png` | 손보기: 후드 앞 가장자리 → 제복 열쇠 색, 마스크는 어두운 단계 #263459/#394b78 로 (평평한 판 금지). 메시지 F 2번 + feedback.md 「메시지 F 보충」. 같은 이름으로 덮어쓰기 |
| `sheet/class/rogue` | **ACCEPTED** (2026-11-25 PC 손질 `a9d92aa` 등록) | `art/inbox/sheet_class_rogue.png` | `art/requests/phase3/class_rogue/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/class_rogue/guide_strip.png` | 손보기: 스카프 → 제복 열쇠 색 어두운 단계 #263459/#394b78 + 외곽선. 메시지 F 3번 + 보충. 같은 이름으로 덮어쓰기 |
| `sheet/monster/해골 병사` | **ACCEPTED** (2026-11-25 PC 손질 `ea6fe20` 등록) | `art/inbox/sheet_monster_skeleton.png` | `art/requests/phase3/monster_skeleton/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/monster_skeleton/guide_strip.png` | 손보기: 뼈·강철·천 재질 분리, 밝은 빨강 눈. 메시지 F 4번. 같은 이름으로 덮어쓰기 |
| `sheet/monster/들늑대` | **ACCEPTED** (2026-11-25 PC 손질 `66aca5a` 등록, 점 색 눈) | `art/inbox/sheet_monster_wolf.png` | `art/requests/phase3/monster_wolf/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/monster_wolf/guide_layout.png` | 손보기: 호박색 눈, 적갈색 입안. 메시지 F 5번. 같은 이름으로 덮어쓰기 |
| `sheet/monster/가고일` | **ACCEPTED** (2026-11-25 PC 손질 `cea8630` 등록, 점 색 눈) | `art/inbox/sheet_monster_gargoyle.png` | `art/requests/phase3/monster_gargoyle/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/monster_gargoyle/guide_layout.png` | 손보기: 빨간 눈. 메시지 F 6번. 같은 이름으로 덮어쓰기 |
| `sheet/monster/사막 도적` | **ACCEPTED** (2026-11-25 PC 손질 `87744c1` 등록) | `art/inbox/sheet_monster_desert-bandit.png` | `art/requests/phase3/monster_desert-bandit/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/monster_desert-bandit/guide_strip.png` | 손보기: 굵은 짙은 외곽선, 어두운 포인트. 메시지 F 7번. 같은 이름으로 덮어쓰기 |
| `sheet/monster/하피` | **ACCEPTED** (2026-11-25 PC 손질 `597cd69` 등록) | `art/inbox/sheet_monster_harpy.png` | `art/requests/phase3/monster_harpy/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/monster_harpy/guide_layout.png` | 손보기: 외곽선, 피부보다 어두운 깃털 상의. 메시지 F 8번. 같은 이름으로 덮어쓰기 |
| `sheet/monster/망령` | **ACCEPTED** (2026-11-25 PC 손질 `cd0d963` 등록) | `art/inbox/sheet_monster_wraith.png` | `art/requests/phase3/monster_wraith/README.md` + `art/requests/phase3_gpt.md` 「메시지 F」 | `art/requests/phase3/monster_wraith/guide_layout.png` | 손보기(새로): 눈밭에서 묻힘 → feedback.md 「메시지 F 보충」. 같은 이름으로 덮어쓰기 |
| `sheet/captain/windhunter` | **ACCEPTED** (2026-11-25 등록, art-inbox `a9b4ddc`) | `art/inbox/sheet_captain_windhunter.png` | `art/requests/phase3/captain_windhunter/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_windhunter/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 나린 (초반·early, 가이드 무기 `bow`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 나린」. |
| `sheet/captain/shadowlord` | **ACCEPTED** (2026-11-25 등록, art-inbox `33c3340`) | `art/inbox/sheet_captain_shadowlord.png` | `art/requests/phase3/captain_shadowlord/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_shadowlord/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 모로 (초반·early, 가이드 무기 `none`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 모로」. |
| `sheet/captain/bard` | **ACCEPTED** (2026-11-25 등록, art-inbox `fb47d45`) | `art/inbox/sheet_captain_bard.png` | `art/requests/phase3/captain_bard/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_bard/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 리코 (초반·early, 가이드 무기 `sword_shield`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 리코」. |
| `sheet/captain/beastmaster` | **DOT_READY** | `art/inbox/sheet_captain_beastmaster.png` | `art/requests/phase3/captain_beastmaster/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_beastmaster/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 오르가 (초반·early, 가이드 무기 `bow`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 오르가」. |
| `sheet/captain/runesmith` | **ACCEPTED** (2026-11-25 `27e7a9d` 등록) | `art/inbox/sheet_captain_runesmith.png` | `art/requests/phase3/captain_runesmith/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_runesmith/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 브로크 (초반·early, 가이드 무기 `katana`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 브로크」. |
| `sheet/captain/pilgrim` | **ACCEPTED** (2026-11-25 `df2301b` 등록, 칸 112) | `art/inbox/sheet_captain_pilgrim.png` | `art/requests/phase3/captain_pilgrim/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_pilgrim/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 아멜리 (초반·early, 가이드 무기 `staff`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 아멜리」. |
| `sheet/captain/spellblade` | **ACCEPTED** (2026-11-25 `8d35af1` 등록) | `art/inbox/sheet_captain_spellblade.png` | `art/requests/phase3/captain_spellblade/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_spellblade/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 카시안 (중반·mid1, 가이드 무기 `sword_shield`, 방패 없음). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 카시안」. 무기 확정(2026-11-25 주인): 청록 룬 **한손** 장검(빈 손은 펼친 손) — 초상화의 수정 지팡이는 쓰지 않음. |
| `sheet/captain/saintknight` | **ACCEPTED** (2026-11-25 PC 손질 `88d31af` 재등록) | `art/inbox/sheet_captain_saintknight.png` | `art/requests/phase3/captain_saintknight/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_saintknight/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 손보기(주인 결정, 교차 검수 1 #6): 별 철퇴가 64px 에서 지팡이로 읽힌다 → 네 자세 모두 **손 위 자루를 약 1/4 줄이고**(별 머리를 손 쪽으로 당김) **별 머리를 좌우 1px(원본 약 6px)씩 넓힌다**. 자세·몸·색은 그대로, 줄인 자루 자리는 마젠타로. 같은 이름으로 덮어쓰기 + `aseprite/sheet_captain_saintknight.aseprite`. **걷기 뼈대 시범보다 먼저** 한다. |
| `sheet/captain/hexer` | **ACCEPTED** (2026-11-25 `4c7c185` 등록) | `art/inbox/sheet_captain_hexer.png` | `art/requests/phase3/captain_hexer/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_hexer/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 벨라도나 (중반·mid1, 가이드 무기 `staff`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 벨라도나」. |
| `sheet/captain/liberator` | **DOT_READY** | `art/inbox/sheet_captain_liberator.png` | `art/requests/phase3/captain_liberator/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_liberator/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 카토 (중반·mid1, 가이드 무기 `sword_shield`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 카토」. |
| `sheet/captain/admiral` | **ACCEPTED** (2026-11-26 `3604e08` 등록) | `art/inbox/sheet_captain_admiral.png` | `art/requests/phase3/captain_admiral/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_admiral/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 마렌 (중반·mid1, 가이드 무기 `bow`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 마렌」. |
| `sheet/captain/elfwarden` | **ACCEPTED** (2026-11-26 `fedb529` 등록) | `art/inbox/sheet_captain_elfwarden.png` | `art/requests/phase3/captain_elfwarden/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_elfwarden/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 세레니엘 (중반·mid1, 가이드 무기 `bow`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 세레니엘」. |
| `sheet/captain/warlord` | **ACCEPTED** (2026-11-26 `70220ed` 등록) | `art/inbox/sheet_captain_warlord.png` | `art/requests/phase3/captain_warlord/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_warlord/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 가르마크 (중반·mid2, 가이드 무기 `katana`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 가르마크」. 무기 확정(2026-11-25 주인): 양손 전쟁 도끼 — 초상화의 대검은 그리지 않음. |
| `sheet/captain/khan` | **ACCEPTED** (2026-11-26 `20f5ff5` 등록) | `art/inbox/sheet_captain_khan.png` | `art/requests/phase3/captain_khan/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_khan/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 테무르 (중반·mid2, 가이드 무기 `bow`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 테무르」. |
| `sheet/captain/siegemaster` | **ACCEPTED** (2026-11-26 `0cd6d7e` 등록) | `art/inbox/sheet_captain_siegemaster.png` | `art/requests/phase3/captain_siegemaster/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_siegemaster/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 오토 (중반·mid2, 가이드 무기 `bow`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 오토」. |
| `sheet/captain/inquisitorlord` | **ACCEPTED** (2026-11-26 `09cff2c` 등록) | `art/inbox/sheet_captain_inquisitorlord.png` | `art/requests/phase3/captain_inquisitorlord/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_inquisitorlord/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 발타자르 (중반·mid2, 가이드 무기 `staff`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 발타자르」. |
| `sheet/captain/pirateking` | **ACCEPTED** (2026-11-26 `9124b86` 등록 — 작게 그려져 변환 배율 0.185·칸 112 로 맞춤) | `art/inbox/sheet_captain_pirateking.png` | `art/requests/phase3/captain_pirateking/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_pirateking/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 크림슨 (중반·mid2, 가이드 무기 `sword_shield`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 크림슨」. |
| `sheet/captain/frostjarl` | **DOT_READY** | `art/inbox/sheet_captain_frostjarl.png` | `art/requests/phase3/captain_frostjarl/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_frostjarl/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 비요른 (중반·mid2, 가이드 무기 `katana`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 비요른」. 무기 확정(2026-11-25 주인): 양손 수염도끼 — 초상화 등의 칼자루는 그리지 않음. |
| `sheet/captain/dragonslayer` | **DOT_READY** | `art/inbox/sheet_captain_dragonslayer.png` | `art/requests/phase3/captain_dragonslayer/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_dragonslayer/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 지크린데 (후반·late, 가이드 무기 `katana`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 지크린데」. |
| `sheet/captain/demonhunter` | **DOT_READY** | `art/inbox/sheet_captain_demonhunter.png` | `art/requests/phase3/captain_demonhunter/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_demonhunter/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 모르데카이 (후반·late, 가이드 무기 `staff`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 모르데카이」. |
| `sheet/captain/archmagus` | **QUEUED** | `art/inbox/sheet_captain_archmagus.png` | `art/requests/phase3/captain_archmagus/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_archmagus/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 에우리아 (후반·late, 가이드 무기 `staff`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 에우리아」. |
| `sheet/captain/lightbearer` | **QUEUED** | `art/inbox/sheet_captain_lightbearer.png` | `art/requests/phase3/captain_lightbearer/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_lightbearer/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 루치아 (후반·late, 가이드 무기 `staff`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 루치아」. |
| `sheet/captain/shadowqueen` | **QUEUED** | `art/inbox/sheet_captain_shadowqueen.png` | `art/requests/phase3/captain_shadowqueen/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_shadowqueen/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 니클라 (후반·late, 가이드 무기 `none`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 니클라」. |
| `sheet/captain/titan` | **QUEUED** | `art/inbox/sheet_captain_titan.png` | `art/requests/phase3/captain_titan/README.md` ("Prompt for GPT" 블록) | `art/requests/phase3/captain_titan/guide_strip.png` (배치·크기 견본), `guide_1_idle.png` ~ `guide_4_hit.png` | 대장 우르그 (후반·late, 가이드 무기 `katana`). 디자인 기준 `portrait.png`. 납품 메모: `art/inbox/NOTES.md` 「3단계 — 우르그」. 체격 large — 시트 칸 112 필요할 수 있음. |
| `guide/walk_base` | **ACCEPTED** (2026-11-25 PC 손질 `4feb568` — 클라우드 측정 + GPT 교차 검수 2 통과) | `art/inbox/guides/walk_base/walk_strip.png` (+ `walk_base.aseprite`) | `art/requests/guides/walk_base/README.md` | `art/requests/guides/walk_base/start_guide_walk_0..3.png` (posekit 출발점) | 손보기(교차 검수 2 #3): ②·④ 지나가기에서 **든 발만** 골반 아래쪽으로 앞당긴다 — 원본 약 6~12px(게임 1~2px). 특히 ④의 들린 장화가 디딘 발 뒤에 길게 남아 뒤로 차는 듯 보인다. 들림 높이 22px·디딘 발 위치·몸·팔은 그대로, 팔다리 길이 일정 유지(정강이·넓적다리 레이어). 같은 이름으로 덮어쓰기 |
| `guide/walk_base` v2 | **GPT 교차 검수 중** (2026-11-26 PC 다듬기 `2c31b96` 수용 — 세 수치를 `walk8.py` 에 넣고 클라우드가 확정판을 다시 구움) | `art/requests/guides/walk_base/v2/walk_base.aseprite` (확정판: 레이어 나뉜 8프레임) · PC 납품 `art/inbox/guides/walk_base/` | `art/requests/guides/walk_base/README.md` + `art/requests/guides/SPEC.md` | `art/requests/review/xcheck_03/` | 걷기 뼈대 v2 — 8프레임. PC 가 고친 것: 지나감 든 발목 (0.13, 0.45) · 뒤로 가는 팔 팔꿈치 30°·어깨 0.92 · 올라섬 뒤꿈치 22°. 클라우드가 더한 것: 모든 프레임 같은 바닥선(`check_skeleton.py` 가 잡은 초안 결함). GPT 3문항 통과하면 ACCEPTED. |
| `review/xcheck_03` | **DOT_READY** | `art/inbox/NOTES.md` 「교차 검수 3」 (그림 없음) | `art/requests/review/xcheck_03/README.md` | `art/requests/review/xcheck_03/*.png` | 교차 검수 — 걷기 뼈대 v2 확정판 3문항에 OK/FIX 로 답한다. PC 세션은 손대지 않는다. |
| `review/xcheck_01` | **ACCEPTED** (2026-11-25 `3a04482` 답 받음·반영) | `art/inbox/NOTES.md` 「교차 검수 1」 (그림 없음) | `art/requests/review/xcheck_01/README.md` + `art/requests/phase3_gpt.md` 「메시지 G」 | `art/requests/review/xcheck_01/*.png` | 교차 검수 — 새 전투 효과 4종·애매한 납품 판단 8문항에 OK/FIX 로 답한다. PC 세션은 손대지 않는다. |
| `review/xcheck_02` | **ACCEPTED** (2026-11-25 `dee1cab` 답 받음·반영) | `art/inbox/NOTES.md` 「교차 검수 2」 (그림 없음) | `art/requests/review/xcheck_02/README.md` + `art/requests/phase3_gpt.md` 「메시지 H」 | `art/requests/review/xcheck_02/walk_review.png` | 걷기 뼈대 시범 5문항에 OK/FIX 로 답한다. |

## 납품 규칙 (요약)

- 읽기: 이 브랜치(`claude/dot-fantasy-management-game-saupju`). 쓰기: `art-inbox` 브랜치의 `art/inbox/`만. 파일 이름은 표의 이름 그대로.
- **지시가 있는 곳은 두 군데뿐**: 이 표의 그 줄(메모·요청서 칸)과 꾸러미 README(맨 위 THIS ROUND 가 우선). 늘 지키는 규칙은
  `gpt_handoff_notes.md`「Rules changed」(GPT) · `pc_notes.md`(PC). `feedback.md` 는 Claude 의 검토 기록이라 그림 쪽이 읽을 필요가 없다.
- **역할 나눔**: GPT = 새로 그리기·다시 그리기·교차 검수(글) / PC(Aseprite) = 받은 그림 손질 + 자세 뼈대. 상태 칸에 **`담당: PC(Aseprite)`** 가 붙은 항목만 PC 가 한다.
- 납품 메모: `art/inbox/NOTES.md` 에 항목별 절 (GPT: `GPT_STANDING.md` 의 양식 / PC: `pc_notes.md` 맨 아래).
- Claude Code 가 art-inbox 를 감시해 수령·검토한다 (`tools/art/receive.py --list`, 절차는 `docs/pc_cloud_protocol.md` 7절). 본 납품은 통과든 반려든 이 브랜치의 `art/inbox/` 로 가져온다.

## 운영 규칙 (Claude 가 지키는 것 — 2026-11-26 검토에서 정리)

- **판정**: 통과하면 바로 ACCEPTED (주인 위임). 수치(검사 결과)는 그림 쪽 것을 그대로 믿되, **개수·판독(다리 수, 무기 종류, 눈이 보이는가)은 게임 크기 변환본에서 직접 센다.**
  NOTES 의 DEVIATIONS 에 디자인(b)·확정 사항(c) 이탈이 있으면 시안·초상화와 게임 크기로 나란히 본 뒤에만 통과.
- **GPT 제안 처리 (주인 위임 2026-11-25)**: GPT 가 NOTES 에 올린 제안·질문은 Claude 가 판단해 처리하고(수용·일부·거절과 이유를 feedback.md 에), 디자인 방향을 크게 바꾸거나 주인이 고른 것을 뒤집는 것만 주인에게 묻는다.
- **교차 검수(xcheck)**: 양식과 "반드시 하는 경우"는 `art/requests/review/TEMPLATE.md`. Claude 와 GPT 가 갈릴 때 — GPT 의 FIX 가 PC 손질 한 건(자세·디자인은 그대로, 색·소품 크기만)으로 끝나면 묻지 않고 고친다(엘리노어 사례). 다시 그리기가 필요하거나 주인이 고른 디자인이 바뀌면 둘 다 적어 주인에게 묻는다.
- **대기 한 자세 먼저(idle-check)**: 마네킹 가이드가 없는 몬스터, 보스·큰 괴물, 주인 반려 뒤의 다시 그리기, 새 체형·새 종류의 첫 시트. 초상화 기반 사람형 대장에는 쓰지 않는다(14/15 가 첫 납품 통과).
- **시안에서 꼭 남길 것**: 주인이 시안 번호를 고르면 "이 시안에서 꼭 남길 것 2~3가지"를 물어 꾸러미의 MUST SURVIVE 에 주인의 말 그대로 적는다.
  Claude 의 가독성 제안(FIX)은 그것을 지우지 못한다. 비어 있으면 그 항목은 DOT_READY 로 올리지 않는다. (거대 거미: 우리 FIX 가 시안의 털·검은 다리를 지웠다)
- **무기**: 초상화·스킬 이름·이야기가 서로 다르면 주인에게 한 번에 물어 `weapon_confirmed` 로 적는다. 열린 질문("확인 필요")이 든 요청서는 만들지 않는다(도구가 거부한다).
- **PC 손질 요청 쓰는 법**: 메모 칸 맨 앞에 `바탕: art-inbox <해시>`. 변화는 게임 px 과 원본 px 을 함께 적는다("좌우 1px(원본 약 6px)"). 원본 6px 미만의 변화는 요청하지 않는다.
  PC 가 다음에도 지켜야 할 것은 feedback.md 가 아니라 `pc_notes.md` 에 한 줄로.
- **걷기·달리기 그림**: `walk_<직업>`·`run_<직업>` 세트는 주인이 아래 「주인에게 물을 것」 1번에 답할 때까지 열지 않는다 (`walk_base` v2 다듬기만 진행).
- **한 번에 열어 두는 수**: 사람형 대장(초상화 기반) DOT_READY 5개까지, 몬스터·보스는 하나씩(idle-check 부터). 5개 아래로 줄면 QUEUED 다음 것을 올린다.
- **건너뛰어진 항목**: 위 항목이 건너뛰어진 채 아래 항목이 두 번 납품되면 「지금 차례」에 이유를 묻는 줄을 넣는다(오르가는 다섯 번 건너뛰어진 뒤에야 물었다).
- **뒤집힌 판정**: feedback.md 의 앞 절 제목에 "(뒤집힘 → 아래 ○○)" 를 덧붙인다.

## 나중 손질 (PC) — 통과시켰지만 적어 둔 것 (PC 대기열이 비면 위에서부터 올린다)

| 파일 | 손볼 것 | 상태 |
|---|---|---|
| `sheet_captain_bard.png` (리코) | 레이피어 날이 1px 짙은 회색이라 어두운 전장에서 흐리다 → 밝은 강철색(#c8ccd2 근처) 2px(원본 약 12px) | LATER |
| `sheet_hero_kai.png` (카이) | 타격 자세에서 시위 당긴 손이 뒤로 빠지는 폭이 작아 준비·타격이 덜 구분된다 | LATER |
| `sheet_monster_giant-spider.png` | 다시 그리기 2 가 통과하면 피격 자세가 대기와 구분되는지 확인 | 다시 그리기 뒤 |
| `sheet_monster_skeleton.png` | 찌르기 자세가 칸 오른쪽 끝에 닿아 2px 밀려 들어간다 (자세를 약간 좁히기) | LATER |
| `sheet_monster_desert-bandit.png` | 타격 칼끝과 피격 자세 사이가 32px 안(검사 FAIL, 원래부터 — 변환은 정상). 피격 자세를 오른쪽으로 원본 12px | LATER (알려진 FAIL) |
| 그 밖의 메모 | feedback.md 의 "급하지 않음·다음 손질 때" 줄들(세라핀·그롬·아스텔·오스윈·진·이사벨) — 올리기 전에 게임 화면에서 다시 확인 | 확인 필요 |
