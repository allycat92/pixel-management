# 3단계 전투 캐릭터 — GPT(그림 쪽)에 보낼 메시지

> 손으로 쓴 문서. 규칙은 `art/requests/gpt_handoff_notes.md`, 캐릭터별 자료는 `art/requests/phase3/<id>/`
> (`python3 tools/art/handoff.py`로 만든다), 요청서 목록은 `art/requests/phase3.md`.

## 브랜치 규칙 (그림 쪽에도 그대로 전한다)

- **읽기**: 모든 자료(규칙·가이드·초안·README)는 `claude/dot-fantasy-management-game-saupju` 브랜치에서 읽는다.
  웹 주소: <https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3>
  (파일 하나는 `https://raw.githubusercontent.com/allycat92/pixel-management/claude/dot-fantasy-management-game-saupju/<경로>`).
- **쓰기**: 결과 PNG 와 `art/inbox/NOTES.md`는 **`art-inbox` 브랜치에만** 올린다. `art-inbox`에 있는 예전 `art/STYLE.md`·`art/requests/`는
  옛 규칙이므로 읽지 않는다. `sheet_captain_*.png`는 `art-inbox`에서는 **새 파일**이다
  (claude 브랜치의 `art/inbox/sheet_captain_blademaster.png`도 이제 승인된 GPT 판이다 — 예전 NovelAI 판은 교체됐다. 그림 쪽은 claude 브랜치 쪽을 건드리지 않는다).
- **NovelAI 는 디자인 초안 전용이다 (주인 결정).** 게임에 들어가는 최종 그림은 언제나 GPT 를 거친다. NovelAI 로 최종본·시트를 요청하지 않고,
  NovelAI 그림을 `art/inbox/sheet_*.png`로 올리지 않는다 (`sheets.py`가 NovelAI 그림을 거부한다).

## 주인용 사용법 (한국어)

1. **먼저 이 자료가 원격 브랜치에 올라가 있는지 확인한다.** 지금 커밋들은 로컬에만 있을 수 있다 — Claude 에게 "푸시해 줘"라고 하면 올린다.
   확인: `git fetch origin && git status -sb`가 `ahead`를 보이지 않고, 아래 주소가 열려야 한다.
   - <https://github.com/allycat92/pixel-management/blob/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_blademaster/README.md>
   - <https://github.com/allycat92/pixel-management/blob/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_blademaster/guide_strip.png>
   - 또는 `git ls-remote origin claude/dot-fantasy-management-game-saupju`의 해시가 `git rev-parse HEAD`와 같아야 한다.
2. **메시지 A**를 그림 쪽에 그대로 붙여 넣는다. 바렌 한 장만 그리고 멈춘다.
   - 저장소를 읽고 푸시할 수 있는 에이전트(Codex 등) → 메시지 A.
   - ChatGPT 웹처럼 저장소를 못 읽는 곳 → **메시지 A-웹** + 그 아래 적힌 첨부 파일.
   - 목표 게임 스크린샷(참고 화면)은 저장소에 없다(남의 게임 화면). 어느 쪽이든 **직접 첨부**한다 — 앵커 화풍 기준의 일부다.
3. 바렌이 올라오면(웹이면 받은 PNG 를 GitHub 웹에서 `art-inbox` 브랜치의 `art/inbox/`에 올린 뒤) Claude 에게 "바렌 올렸다"고 알린다.
   Claude 가 아래 「받은 뒤 처리」로 게임 크기 미리보기를 만들어 보여 준다.
   - 승인 기준: 4등신인가, 오른쪽을 보는 정면 3/4인가, 4자세가 가이드와 같은가, 64px 로 줄여도 읽히는가, 차분한 색·검정 아닌 외곽선인가,
     상의가 남색이고 진홍은 반망토뿐인가, 효과·바닥·글자가 없는가, 이 화풍으로 8명을 더 그려도 좋은가.
   - 마음에 안 들면 **메시지 A2**(다시 그리기)로 고칠 점을 적어 보낸다. 승인될 때까지 B 로 넘어가지 않는다.
   - 승인하면 Claude 가 승인된 바렌을 claude 브랜치에도 커밋·푸시한다(예전 NovelAI 판을 바꾼다 — 완료). 그 뒤 두 브랜치의 앵커가 같다.
4. **메시지 B**(웹이면 **메시지 B-웹**)를 보낸다. 8명(+ 선택: 로드릭 기마)을 바렌에 맞춰 그린다. 몇 명씩 끊어서 올려도 된다.
5. 올라올 때마다 Claude 에게 알리면 처리·확인하고, 다시 그릴 것은 `art/requests/feedback.md`에 적는다.
6. **지금 (8명 납품 뒤)**: 펠릭스만 다시 — **메시지 C**(웹이면 **C-웹**). 자세는 그대로, 로브·모자 색만 고친다.
7. **다음 묶음 (초안부터)**: 일반 병과 5종(**메시지 D**)과 1차 몬스터 8종(**메시지 E**). 꾸러미(`class_<key>/`, `monster_<key>/`)는 만들어 두었지만
   `concept.png`가 비어 있다. 순서: 주인이 원하면 Claude 가 NovelAI **디자인 초안** 후보를 만든다(작업 목록 `jobs_classes.json`·`jobs_monsters.json`, 무료 범위)
   → 주인이 고른다 → Claude 가 `art/concepts/<id>/`에 넣고 `handoff.py`의 `concepts`를 채워 다시 만든다 → 그 다음 D·E 를 보낸다.
   NovelAI 는 여기까지(디자인 참고)만 한다. 최종 그림은 D·E 로 GPT 가 그린다 — NovelAI 로 게임에 바로 넣을 최종본을 만들지 않는다.
   일반 병과는 **얼굴이 가려지는 복장**으로 뽑는다 (주인 요청, 아래 「일반 병과 — 얼굴 가림」).

### 받은 뒤 처리 (Claude Code 가 한다)

```bash
git fetch origin art-inbox
git checkout origin/art-inbox -- art/inbox/sheet_captain_blademaster.png art/inbox/NOTES.md
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png --dry-run --work /tmp/sheets   # 미리보기: /tmp/sheets/*/preview_x4.png
# 주인 승인 후:
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png                                 # 등록 → assets/art/sheets/ + manifest
git add art/inbox/sheet_captain_blademaster.png art/inbox/NOTES.md assets/art && git commit && git push   # claude 브랜치에도 승인된 앵커
# 나머지는 파일을 하나씩 이름으로 준다 (인자 없이 돌리면 art/inbox/sheet_*.png 전부라 기마 시트까지 등록된다):
#   python3 tools/art/sheets.py art/inbox/sheet_captain_<key>.png
# 기마(게임 미사용, 미리보기만, 등록하지 않는다):
#   python3 tools/art/sheets.py art/inbox/sheet_captain_lancer_mounted.png --grid 2x2 --dry-run --work /tmp/sheets
```

`sheets.py`가 자세 4개를 찾아 배경을 지우고, 대기 자세 몸 높이를 64px 로 맞춘 같은 배율로 줄여 80×80 칸 시트(숨쉬기 대기 4칸 + 공격 2칸 + 피격 1칸)를
만들고 `assets/art/manifest.json`에 등록한다. 왼쪽을 보고 그렸으면 `--flip`. 그 뒤 게임 전투 화면에서 확인한다.

### 무기·자세 대응표 (posekit 일반 마네킹 + `handoff.py`의 `KEY_POSES`)

준비 = 체중을 뒤로 싣고 조금 선 자세, 타격 = 앞으로 내딛는 런지에 팔을 뻗음, 피격 = 상체가 뒤로 젖혀지고 체중이 뒷다리에, 무기가 떨어짐.

| 순서 | 캐릭터 | posekit 무기 | ① 대기 | ② 준비 | ③ 타격 | ④ 피격 | 그림에서 바꿀 것 |
|---|---|---|---|---|---|---|---|
| 1 | 바렌 `blademaster` (앵커) | katana | idle_0 | key_windup | key_strike | key_hit | 상의 남색, 진홍은 반망토만 |
| 2 | 브리긴다 `ironwall` | sword_shield | idle_0 | key_windup | key_strike | key_hit | 칼 → 철퇴, 원형 방패 → 탑실드(머리 2개 높이·1개 폭) |
| 3 | 이사벨 `tactician` | staff | cast_0 | cast_1 | key_strike | key_hit | 지팡이 → 절반 길이 장교 지휘봉, 타격 = 뻗은 팔로 손가락 지휘 |
| 4 | 로드릭 `lancer` | spear | idle_0 | key_windup | key_strike | key_hit | 창 → 창 길이의 보병용 랜스(잎 모양 날, 파란 작은 깃발) |
| 5 | 키아라 `huntress` | bow | idle_0 | attack_2 | attack_3 | key_hit | 준비 = 끝까지 당김, 타격 = 쏜 직후(화살 없음) |
| 6 | 펠릭스 `hedgemage` | staff | idle_0 | cast_1 | key_strike | key_hit | 구슬 → 나무 끝, 타격 = 뻗은 빈 손바닥, 효과 없음 |
| 7 | 마그다 `fieldmedic` | staff | idle_0 | cast_1 | key_strike | key_hit | 지팡이 = 긴 자루 철퇴, 가슴의 흰 십자 제거, 치유 빛 없음 |
| 8 | 진 `fixer` | none (+단검) | key_idle | key_windup | key_strike | key_hit | 가까운 손에 역수 단검 하나 (가이드에 그려 둠) |
| 9 | 하랄드 `veteran` | sword_shield | idle_0 | key_windup | key_strike | key_hit | 둥근 나무 방패 + 한손검 |
| 10 | 로드릭 기마 (선택) | — | 2×2 격자, `guide_mounted_layout.png`는 칸 나눔·크기 참고 | | | | 파란 판금, 말 머리 하나, 게임 미사용 |

---

## 메시지 A — 지금 보낼 것 (바렌만, 화풍 기준; 저장소를 읽고 푸시할 수 있는 에이전트용)

```
게임 저장소 https://github.com/allycat92/pixel-management 의 전투 캐릭터 그림을 부탁해. 이번에는 바렌 한 장만.

브랜치 규칙:
- 읽기: 모든 자료는 브랜치 claude/dot-fantasy-management-game-saupju 에서 읽어.
  https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/captain_blademaster
- 쓰기: 결과는 art-inbox 브랜치에만 올려. art-inbox 에 있는 예전 art/STYLE.md 와 art/requests/ 는 옛 규칙이니 읽지 마.
  art/inbox/sheet_captain_blademaster.png 는 art-inbox 에서 새 파일이다 (claude 브랜치의 같은 이름 파일은 예전 NovelAI 판이니 보지도 복사하지도 마).

읽을 것 (claude/dot-fantasy-management-game-saupju 브랜치):
1. art/requests/gpt_handoff_notes.md — 그림 규칙. 다른 문서와 다르면 이것이 우선이다.
2. art/requests/phase3/captain_blademaster/README.md 의 "Prompt for GPT" 블록 — 실제 지시. 그 폴더의 그림 전부:
   guide_strip.png(자세·배치·크기 견본, 가장 중요), guide_1_idle ~ guide_4_hit(같은 자세 크게), concept.png(디자인만),
   concept_pixel.png(도트로 줄여도 살아남는 단순한 형태의 기준), portrait.png(얼굴·머리만).
3. art/STYLE.md 의 "전투 캐릭터" 절 (참고). 거기 적힌 "한 자세만" / "2×2 격자"는 예비 형식이니 무시하고 1×4 한 줄만 그려.
첨부한 스크린샷은 목표 게임의 화면이다: HD 도트의 밀도·차분한 색감만 참고하고 캐릭터는 베끼지 마.

그릴 것: 바렌(captain_blademaster) 전투 스프라이트 띠 한 장.
- 1536x1024 PNG, 같은 캐릭터 4번을 한 줄로(1×4): 대기 / 공격 준비 / 공격 타격 / 피격. guide_strip.png 와 같은 자세·크기·위치.
- 4등신, 머리 하나 110px. 대기 자세는 웅크려서 정수리~발바닥 약 400px (머리띠 꼬리·무기는 따로). 오른쪽을 보는 정면 3/4, 빛은 왼쪽 위.
- 네 자세 모두 맨 아래 픽셀(발바닥)이 y=870. 자세끼리·테두리와 어느 방향으로든 마젠타 32px 이상 떨어지게.
- 배경은 완전히 평평한 마젠타 #FF00FF. 바닥·그림자·글자·칸 선·효과(검기, 먼지, 빛) 없이.
- 상의는 짙은 남색(#2a3150), 짙은 진홍(#3a1018)은 한쪽 반망토·허리 천에만. 카타나 하나, 칼집·두 번째 칼·팔 붕대 없음.
- NovelAI 초안(concept)에서는 옷·색·머리띠·흉터·카타나 같은 디자인만 가져오고, 비율·칠하는 방식·외곽선·채도는 따라 하지 마.
- 이 그림이 나머지 8명 모두의 "화풍 기준(앵커)"이 된다. 깔끔하고 단순한 큰 형태로, 64px 로 줄여도 읽히게.
- 저장하기 전에 README 의 SELF-CHECK 를 하나씩 확인하고, 틀린 것이 있으면 다시 그려.

저장·올리기 (art-inbox 브랜치):
- art/inbox/sheet_captain_blademaster.png 로 저장 (이름 그대로).
- art/inbox/NOTES.md 에 "3단계 — 바렌 (화풍 기준)" 절을 더해: 만든 파일, 프롬프트·가이드와 다르게 한 점, 다시 그리고 싶은 점.
- art-inbox 브랜치에 커밋해서 푸시. art/inbox/ 밖의 파일은 고치지 마.

그 다음 멈추고 내 승인을 기다려. 다른 캐릭터는 아직 그리지 마.
```

## 메시지 A-웹 — ChatGPT 웹처럼 저장소를 못 읽는 곳

첨부 (이 순서로): 목표 게임 스크린샷, `art/requests/phase3/captain_blademaster/`의 `guide_strip.png`, `guide_1_idle.png`,
`guide_2_windup.png`, `guide_3_strike.png`, `guide_4_hit.png`, `concept.png`, `concept_pixel.png`, `portrait.png`.
메시지 뒤에 그 폴더 `README.md`의 "Prompt for GPT" 블록을 통째로 붙인다.

```
전투 캐릭터 그림을 부탁해. 이번에는 바렌 한 장만. 아래 영어 블록이 실제 지시다.

첨부 파일: 1) 목표 게임 스크린샷 — HD 도트의 밀도·차분한 색감만 참고, 캐릭터는 베끼지 마.
2) guide_strip.png — 자세·배치·크기 견본 (가장 중요). 3) guide_1_idle ~ guide_4_hit — 같은 자세 크게.
4) concept.png — 디자인만. 5) concept_pixel.png — 도트로 줄여도 살아남는 단순한 형태. 6) portrait.png — 얼굴·머리만.

- 1536x1024 PNG 한 장, 1×4 한 줄 (2×2 격자나 한 자세만 그리는 것 아님). 머리 하나 110px, 발바닥 y=870, 배경 #FF00FF.
- 상의는 남색, 진홍은 반망토만. 카타나 하나, 칼집·두 번째 칼·팔 붕대 없음.
- 저장소 경로(art/inbox/…)·NOTES.md·커밋·푸시는 하지 말고, 완성된 PNG 를 이 대화에 돌려줘.
  가이드와 다르게 한 점이 있으면 짧게 적어 줘.
- 저장하기 전에 블록의 SELF-CHECK 를 확인하고, 틀리면 다시 그려. 그 다음 멈추고 내 승인을 기다려.

<여기에 README.md 의 Prompt for GPT 블록>
```

## 메시지 A2 — 바렌을 다시 그릴 때 (필요할 때만)

```
바렌(art/inbox/sheet_captain_blademaster.png)을 다시 그려 줘. 규칙·자료는 지난번과 같다
(claude/dot-fantasy-management-game-saupju 브랜치의 art/requests/gpt_handoff_notes.md, art/requests/phase3/captain_blademaster/README.md).
고칠 점:
- <여기에 고칠 점을 적는다. 예: 머리가 너무 크다(4등신으로), 외곽선이 너무 검고 두껍다, 색이 너무 밝다, 2번 자세가 가이드와 다르다>
같은 파일 이름으로 art-inbox 브랜치에 덮어쓰고 NOTES.md 에 고친 점을 적어 푸시한 뒤 다시 멈춰.
(웹이면: 고친 PNG 를 이 대화에 돌려주고 멈춰.)
```

## 메시지 B — 바렌 승인 후 (나머지 8명 + 선택 기마; 저장소용)

```
바렌 승인. art-inbox 브랜치의 art/inbox/sheet_captain_blademaster.png 가 이제 "화풍 기준(앵커)"이다.
나머지 창설 후보 대장 8명을 이 앵커에 맞춰 그려 줘. 캐릭터마다 PNG 한 장 (1×4 한 줄).

브랜치 규칙은 지난번과 같다: 자료는 claude/dot-fantasy-management-game-saupju 에서 읽고, 결과는 art-inbox 에만 올린다.

순서와 자료 (claude/dot-fantasy-management-game-saupju 브랜치의 art/requests/phase3/<id>/):
1. captain_ironwall   → art/inbox/sheet_captain_ironwall.png
2. captain_tactician  → art/inbox/sheet_captain_tactician.png
3. captain_lancer     → art/inbox/sheet_captain_lancer.png
4. captain_huntress   → art/inbox/sheet_captain_huntress.png
5. captain_hedgemage  → art/inbox/sheet_captain_hedgemage.png
6. captain_fieldmedic → art/inbox/sheet_captain_fieldmedic.png
7. captain_fixer      → art/inbox/sheet_captain_fixer.png
8. captain_veteran    → art/inbox/sheet_captain_veteran.png
(선택, 맨 마지막) captain_lancer README 의 "추가 선택: 기마 시트" → art/inbox/sheet_captain_lancer_mounted.png
   (sheet_captain_lancer.png 와 다른 파일). 게임은 아직 안 쓰는 여분 그림이다. 2x2 격자, 파란 판금, 말 머리는 정확히 하나.

캐릭터마다:
- 그 폴더의 README.md "Prompt for GPT" 블록을 지시로 쓰고, guide_strip.png 와 같은 자세·크기·위치로 그려.
- 화풍은 앵커(바렌)와 똑같이: 4등신 비율, 칠하는 방식, 외곽선, 팔레트 처리, 조명, 캐릭터 크기
  (머리 하나 110px, 웅크린 대기 자세 정수리~발바닥 약 400px — 모자·투구·무기는 따로, 발바닥 y=870).
  각자의 NovelAI 초안은 디자인(옷·색·무기·흉터)만 참고하고 화풍·비율은 따라 하지 마. STYLE.md 의 "한 자세만"/"2×2"는 무시.
- README 의 FIX 를 꼭 지켜: 마그다 가슴(앞치마 턱받이)의 흰 십자 없음 — 어디에도 십자·무늬 없음, 완장은 무늬 없는 짙은 빨강,
  진은 단검 하나·역수·림 라이트, 이사벨은 4등신, 브리긴다는 땋은 머리가 보이게, 펠릭스·마그다는 불꽃·치유 빛 없음,
  키아라는 쏜 뒤 화살 없음, 로드릭은 원뿔 마상창이 아니라 깃발 달린 보병용 랜스.
- 저장 전 SELF-CHECK 확인, 틀리면 다시 그려.

올리기 (art-inbox 브랜치):
- 2~3명 끝날 때마다 커밋·푸시해도 된다 (빨리 확인할 수 있게).
- art/inbox/NOTES.md 에 "3단계 — 창설 후보 8명" 절: 만든 파일, 다르게 한 점, 다시 그리고 싶은 것.
- art/inbox/ 밖의 파일은 고치지 마. 파일 이름을 바꾸지 마.
```

## 메시지 B-웹 — 저장소를 못 읽는 곳 (한 번에 한 캐릭터)

캐릭터마다 새 메시지로 보낸다. 첨부 (이 순서로): **승인된 바렌 PNG**(앵커), 목표 게임 스크린샷, 그 캐릭터 폴더의
`guide_strip.png`, `guide_1_idle.png` ~ `guide_4_hit.png`, `concept.png`, `portrait.png`
(로드릭 기마는 `concept_mounted.png`, `guide_mounted_layout.png`와 승인된 로드릭 PNG). 캐릭터 폴더 `README.md`의 파일 표에 같은 순서가 있다.

```
첫 번째 첨부(바렌)가 승인된 "화풍 기준(앵커)"이다. 이 화풍에 맞춰 <이름>을 그려 줘. 아래 영어 블록이 실제 지시다.
- 앵커와 똑같이: 4등신 비율, 칠하는 방식, 외곽선, 팔레트 처리, 조명, 캐릭터 크기(머리 하나 110px, 발바닥 y=870).
- concept.png 는 디자인만, portrait.png 는 얼굴·머리만. guide_strip.png 와 같은 자세·크기·위치, 1×4 한 줄, 배경 #FF00FF.
- 저장소 경로·NOTES.md·커밋·푸시는 하지 말고 완성된 PNG 를 이 대화에 돌려줘. SELF-CHECK 확인 후 멈춰.

<여기에 그 캐릭터 README.md 의 Prompt for GPT 블록>
```

---

## 메시지 C — 펠릭스 다시 그리기 (지금 보낼 것; 저장소용)

받은 뒤 처리는 그대로다: `python3 tools/art/sheets.py art/inbox/sheet_captain_hedgemage.png --scale 0.1654 --cell 96 --dry-run --work /tmp/sheets`로
미리보기 → 로브·모자에 구멍이 없으면 등록. (`sheets.py`는 #FF00FF 에 가까운 색을 모두 배경으로 지운다.)

```
펠릭스(captain_hedgemage) 시트를 다시 내보내 줘. 자세·소품·고칠 점은 모두 통과했으니 그대로 두고, 로브·모자 색만 고친다.

문제: art-inbox 브랜치의 art/inbox/sheet_captain_hedgemage.png 에서 로브·모자의 밝은 면 색이 정확히 배경 키 색 #FF00FF 로 저장되었다
(팔레트를 줄일 때 배경색과 합쳐진 것 같다). 배경을 지우면 로브에 구멍이 수백 개 뚫리고 모자 윗부분이 사라진다.

브랜치 규칙은 같다: 자료는 claude/dot-fantasy-management-game-saupju 에서 읽고, 결과는 art-inbox 에만 올린다.
규칙·자료: art/requests/gpt_handoff_notes.md, art/requests/phase3/captain_hedgemage/README.md (FIX·COLOURS 에 이번 고칠 점이 들어 있다).

할 일:
1. 바탕은 지금 art-inbox 에 있는 art/inbox/sheet_captain_hedgemage.png 다. 네 자세의 윤곽·자세·위치·크기(발바닥 y=870)·지팡이·가방·장화·얼굴·머리는
   그대로 둔다. 가능하면 새로 그리지 말고 로브·모자만 다시 칠해서(색 편집) 자세가 달라지지 않게 해.
2. 로브와 모자 전체(밝은 면 포함)를 요청서의 짙은 청보라 #5a4a7a 계열로 칠한다. 예: 가장 어두운 면 #3a3052, 그늘 #4a3e66, 바탕 #5a4a7a,
   밝은 면 #74679a, 가장 밝은 테 #8f84b0. 지금의 와인빛 자주(#5e3c53, #744d60 등)도 이 청보라 계열로 옮긴다. 테두리는 지금처럼 탁한 황토 금색.
3. 마젠타 규칙 (모든 그림 공통): 인물의 모든 색은 배경 키 #FF00FF 와 확실히 달라야 한다 —
   RGB 거리 sqrt((255-R)^2 + G^2 + (255-B)^2) >= 150. 분홍·자홍·밝은 보라 금지 (최소한 R<200 이거나 G>60 이거나 B<200 이어야 하고, 거리 기준이 우선).
   팔레트를 줄일 때는 인물 색만 줄이고 배경색과 절대 합치지 마. 투명 배경 PNG 로 내보내도 되지만 이 규칙은 그대로다.
4. 저장 전에 확인 (저장소 루트에서):
   python3 -c "from PIL import Image, ImageDraw; import numpy as np; im=Image.open('art/inbox/sheet_captain_hedgemage.png').convert('RGB'); ImageDraw.floodfill(im,(0,0),(0,255,0),thresh=0); a=np.asarray(im).astype(int); m=np.sqrt((255-a[...,0])**2+a[...,1]**2+(255-a[...,2])**2)<150; Image.fromarray((m*255).astype(np.uint8)).save('/tmp/hedgemage_magenta.png'); print('magenta-like pixels inside the figures:', int(m.sum()))"
   바깥 배경을 초록으로 채운 뒤 남은 마젠타 같은 픽셀을 센다. 첫 납품은 약 24000 이었다. /tmp/hedgemage_magenta.png 의 흰 부분은
   팔·다리·지팡이 사이의 진짜 빈틈뿐이어야 하고, 로브·모자 위에는 하나도 없어야 한다.
5. README 의 SELF-CHECK 를 다시 확인한다.

저장·올리기 (art-inbox 브랜치):
- 같은 이름 art/inbox/sheet_captain_hedgemage.png 로 덮어쓴다 (이름을 바꾸지 마).
- art/inbox/NOTES.md 에 "3단계 — 펠릭스 다시 그리기" 절: 로브·모자를 어떤 색으로 바꿨는지, 자세를 건드렸는지, 4번 확인 결과(숫자).
- 커밋해서 art-inbox 에 푸시. art/inbox/ 밖의 파일은 고치지 마. 그 다음 멈춰.
```

## 메시지 C-웹 — 펠릭스 다시 그리기 (저장소를 못 읽는 곳)

첨부 (이 순서로): `art-inbox`의 지금 `art/inbox/sheet_captain_hedgemage.png`(고칠 그림), 승인된 바렌 PNG(앵커), `art/requests/phase3/captain_hedgemage/guide_strip.png`.
받은 PNG 는 GitHub 웹에서 `art-inbox` 브랜치의 `art/inbox/sheet_captain_hedgemage.png`로 덮어 올리고 Claude 에게 알린다.

```
첫 번째 첨부(펠릭스 전투 시트)를 고쳐 줘. 자세·위치·크기·소품·얼굴은 그대로 두고 로브와 모자 색만 바꾼다. 가능하면 새로 그리지 말고 색만 다시 칠해.

문제: 로브·모자의 밝은 면이 정확히 배경 색 #FF00FF 로 저장되어, 배경을 지우면 로브에 구멍이 뚫리고 모자 윗부분이 사라진다.

- 로브·모자 전체(밝은 면 포함)를 짙은 청보라 #5a4a7a 계열로: 가장 어두운 면 #3a3052, 그늘 #4a3e66, 바탕 #5a4a7a, 밝은 면 #74679a, 가장 밝은 테 #8f84b0.
  지금의 와인빛 자주도 이 청보라로 옮긴다. 테두리는 지금처럼 탁한 황토 금색.
- 인물의 어떤 픽셀도 배경 #FF00FF 와 가까우면 안 된다: RGB 거리 sqrt((255-R)^2 + G^2 + (255-B)^2) >= 150. 분홍·자홍·밝은 보라 금지.
  팔레트를 줄일 때 인물 색을 배경색과 합치지 마.
- 1536x1024, 배경은 평평한 #FF00FF (투명 PNG 도 됨), 발바닥 y=870, 글자·바닥·그림자·효과 없음.
- 완성된 PNG 를 이 대화에 돌려주고 멈춰. 바꾼 색을 짧게 적어 줘.
```

---

## 일반 병과 열쇠 색 (메시지 D 의 핵심 규칙)

일반 병과 시트 5장(`sheet/class/<key>`)은 이름 없는 용병·세력 병사 **모두가** 같이 쓴다 (상급·최상급 직업도 이 시트로 대신한다).
전투는 아군·적군·세력을 색으로 구별하므로, 게임이 제복만 진영 색으로 바꿔 칠한다 (`js/battle.js` `sheetRecolor`):

- **정확히 같은 색**의 픽셀만 바꾼다. 새 색 = 진영 색 × (그 열쇠 색의 밝기 ÷ 같은 역할 열쇠 색들의 평균 밝기) → 명암 단계는 유지된다.
- 그래서 그림 쪽은 제복을 **정해진 열쇠 색으로만, 평평하게** 칠하고, 열쇠 색을 **다른 곳에 쓰지 않는다**. 금속은 푸른 기 없는 중성 회색, 가죽·나무는 따뜻한 갈색.
- 코드 쪽 `sheets.py`는 요청서(`phase3.json`의 `tint`)를 읽어 원본 해상도에서 열쇠 색과 RGB 거리 34 안의 픽셀을 찾고, 축소 뒤에도 열쇠 색 그대로 남긴다
  (다른 색은 열쇠 색이 되지 않게 팔레트에서 비켜 둔다). `register_sheet.py --tint-outfit/--tint-accent`로 manifest 에 적는다.
  작업 폴더의 `preview_tint_x4.png` = 빨강 제복·노랑 장식으로 바꿔 칠한 미리보기 (바뀌지 않은 파란 조각이 없어야 통과).

| 역할 | 열쇠 색 (어둠 → 밝음) | 밝기 비율 | 어디에 |
|---|---|---|---|
| 제복 outfit | `#263459` `#394b78` `#52679c` `#7489be` | 0.57 · 0.82 · 1.12 · 1.49 | 겉옷·로브와 높은 깃·후드 상의와 마스크·두건과 베일·후드와 망토, 전사의 방패 면 |
| 장식 accent | `#3f7a6c` `#5ea590` `#96d1bb` | 0.71 · 0.98 · 1.31 | 테두리, 허리 천, 후드·두건 앞 가장자리, 모자 띠, 사제의 가슴 원판, 도적의 스카프 |

- 제복 = 차분한 청회색, 장식 = 옅은 청록. 열쇠 색끼리 RGB 거리 43 이상, 중성 회색 금속(#8a8a86 등)과도 그보다 멀다.
- 우리 길드의 이름 없는 용병은 지금 제복 색(look.tint)이 없어 **열쇠 색 그대로(청회색·청록)** 보인다 — 주인 확인 필요.

## 일반 병과 — 얼굴 가림 (주인 요청)

> "일반직업쪽 시안 관련해서인데, 서로 다른 인물이어도 어색하지 않게 가급적 얼굴이 가려지는 복장 위주로 뽑으면 좋을 것 같아.
> 하위 클래스에서는 어려울 수 있다는 점은 이해하니까 너무 억지로는 말고."

한 그림을 서로 다른 여러 사람이 같이 쓰므로, 직업에 어울리는 만큼 얼굴을 가리거나 그늘지게 한다.

| 직업 | 얼굴 가림 | 가린 천의 색 |
|---|---|---|
| 전사 | 면갑을 내린 강철 그레이트 헬름 — 눈 틈만 보인다 | 투구는 중성 회색 금속 |
| 궁수 | 후드를 쓰고 천 마스크로 코 아래를 가림 — 눈 둘레만 그늘 속에 | 후드·마스크 = 제복 열쇠 색, 후드 앞 가장자리 = 장식 |
| 마법사 | 챙 넓은 모자를 깊게 눌러씀(챙이 눈을 가림) + 입·턱을 가린 높은 깃 — 얼굴은 그늘 | 모자·높은 깃 = 제복, 모자 띠 = 장식 |
| 성직자 | 이마까지 내린 깊은 두건 + 아래 얼굴의 베일 — 얼굴은 그늘 | 두건·베일 = 제복, 두건 앞 가장자리 = 장식 |
| 도적 | 깊게 눌러쓴 후드(눈빛 두 점까지만) + 입·코를 가린 스카프 | 후드 = 제복, 스카프 = 장식 |

- 네 자세 모두 같은 만큼 가린다 — 피격 자세에서도 면갑·후드·마스크·베일이 벗겨지거나 내려가지 않는다 (진의 피격 자세에서 복면이 내려간 것 같은 일 없게).
- 그늘진 얼굴은 따뜻하거나 중성인 어두운 색(예: `#3a2e2a`) — 파랑이나 열쇠 색이 아니다.
- 상급·최상급 직업(나중 묶음)은 그 직업에 자연스러울 때만 가린다. 억지로 하지 않는다.
- NovelAI 초안 프롬프트(`phase3.json`의 `nai`, `jobs_classes.json`)에도 같은 내용이 들어갔다 (`face hidden`, 부정어 `visible face details, detailed face, smile`).

## 1차 몬스터 8종 — 고른 근거

`tools/sim/bot.js` 12판 × 365일(시드 1..12, mode all)의 의뢰 보고서 8315건을 `Battle.plan`으로 펼쳐 센 전투 속 몬스터 수 (보스 제외, 상위 12).

| 순위 | 몬스터 | 전투 속 수 | 나온 전투 | 첫 90일 | 지형 목록 (지방 수) | 1차 |
|---|---|---|---|---|---|---|
| 1 | 해골 병사 | 13633 | 1472 | 1386 | 설원(1)·성역(1) + 마법 조사·마왕군 | ✅ |
| 2 | 들늑대 | 9302 | 1814 | 1214 | 평원(4)·숲(2) | ✅ |
| 3 | 사막 도적 | 7049 | 1273 | 723 | 사막(2) | ✅ |
| 4 | 하피 | 6996 | 1299 | 713 | 사막(2) + 마물군 | ✅ |
| 5 | 산적 | 6149 | 1264 | 923 | 평원(4)·성역(1)·해안(1) | ✅ |
| 6 | 가고일 | 5998 | 659 | 310 | 화산 산맥(1) + 마물군 | ✅ |
| 7 | 거대 거미 | 5343 | 967 | 740 | 숲(2) | ✅ |
| 8 | 고블린 | 3746 | 821 | 504 | 평원(4) | 다음 묶음 맨 앞 |
| 9 | 망령 | 2646 | 509 | 699 | 늪지(1)·성역(1) + 마법 조사·마왕군 | ✅ (늪지) |
| 10 | 늪 슬라임 | 2430 | 487 | 588 | 늪지(1)·해안(1) + 마법 조사 | |
| 11 | 리자드맨 | 2015 | 404 | 426 | 늪지(1)·해안(1) | |
| 12 | 리치의 망령 | 1316 | 439 | 21 | 화산 산맥(1) + 마왕군 (큰 몬스터) | |

- 상위 7종이 늪지를 빼고 모든 지형을 덮는다. 8번째 자리는 늪지를 덮는 **망령**(첫 90일에는 고블린보다 많다: 699 > 504). 고블린의 평원은 늑대·산적이 이미 덮는다.
- 8종 모두 보통 크기(`big` 아님). 사람형 셋(해골 병사·사막 도적·산적)은 대장과 같은 posekit 가이드 띠, 나머지 다섯은 크기 상자 가이드
  (`guide_layout.png` + 같은 배율의 사람과 비교하는 `guide_scale.png`). 넓은 넷(늑대·하피·가고일·거미)은 **2x2 격자**, 망령은 1x4 띠.
- 모두 대장과 같은 배율(가이드 머리 110px → 게임 0.1654배)로 줄인다. 요청서에 `scale`·`cell`(96 / 넓은 것 112)·`layout`이 있어 `sheets.py`가 그대로 쓴다.
- 보스·재앙 수장(고블린 왕 … 고룡 이그니스)과 나머지 보통 몬스터 14종은 다음 묶음.

| 순서 | 몬스터 (id) | 파일 | 배치 · 칸 | 크기 (대기 상자, 가이드 px) | 공격 |
|---|---|---|---|---|---|
| 1 | 해골 병사 `sheet/monster/해골 병사` | `sheet_monster_skeleton.png` | 1x4 posekit · 96 | 사람과 같음 (머리 110) | 근접 검 |
| 2 | 들늑대 `sheet/monster/들늑대` | `sheet_monster_wolf.png` | 2x2 · 112 | 420x250 | 근접 물기 |
| 3 | 사막 도적 `sheet/monster/사막 도적` | `sheet_monster_desert-bandit.png` | 1x4 posekit · 96 | 사람과 같음 | 근접 곡도 |
| 4 | 하피 `sheet/monster/하피` | `sheet_monster_harpy.png` | 2x2 · 112 | 440x400 (날개 포함) | 원거리 (엔진: 불덩이) |
| 5 | 산적 `sheet/monster/산적` | `sheet_monster_bandit.png` | 1x4 posekit · 96 | 사람과 같음 | 근접 도끼 |
| 6 | 가고일 `sheet/monster/가고일` | `sheet_monster_gargoyle.png` | 2x2 · 112 | 380x330 (웅크림) | 원거리 (엔진: 불덩이) |
| 7 | 거대 거미 `sheet/monster/거대 거미` | `sheet_monster_giant-spider.png` | 2x2 · 112 | 520x220 | 근접 물기 |
| 8 | 망령 `sheet/monster/망령` | `sheet_monster_wraith.png` | 1x4 · 96 | 240x360 | 원거리 (엔진: 저주탄) |

## NovelAI 초안 작업 목록 (디자인 초안 전용, 주인이 원할 때만)

**NovelAI 는 디자인 초안만 만든다.** 게임에 넣는 최종 그림은 언제나 GPT(메시지 D·E)를 거친다 — NovelAI 로 최종본을 요청하지 않는다 (주인 결정:
NovelAI 최종본은 오류가 계속 나고, GPT 를 거치면 쉽게 끝난다). `novelai.py`는 `art/concepts/<id>/drafts/`(git 에 올리지 않음)나 작업 폴더에만 쓰고,
`art/inbox/`·`assets/`에는 쓰지 못한다. `sheets.py`는 NovelAI 그림을 거부한다 (`--allow-draft` = 시험용, 항상 `--dry-run`).

- 일반 병과 5: `jobs_classes.json` (c1_warrior … c5_rogue, 832x1216), 1차 몬스터 8: `jobs_monsters.json` (m1_skeleton … m8_wraith; 늑대·하피·가고일·거미는 1216x832).
  Claude 세션 작업 폴더의 `nai/picks/`에 있고, 같은 프롬프트·시드·크기가 `phase3.json`의 `nai`에 있다
  (`python3 tools/art/novelai.py --only sheet/class/warrior`도 같은 첫 장 → `art/concepts/class_warrior/drafts/nai_class_warrior_s21001.png`).
- 일반 병과 5종의 프롬프트는 **얼굴 가림**으로 바뀌었다 (전사 `closed great helm, visor down`, 궁수 `hood up, … cloth mask`, 마법사 `hat pulled low, high collar`,
  성직자 `deep cowl, veil`, 도적 `deep hood, shadowed face`; 부정어에 `visible face details, detailed face, smile`).
- 무료 범위(넓이 ≤ 1024x1024, 28 steps, 1장씩). 후보 수는 주인이 정한다 (지난번처럼 12장씩이면 13 x 12 = 156장).
- 초안의 제복은 말로만 "plain slate blue … pale teal trim" — 정확한 열쇠 색은 GPT 단계에서 지킨다.

---

## 메시지 D — 일반 병과 5종 (초안: 주인이 초안을 고른 뒤에 보낸다; 저장소용)

> 보내기 전: 다섯 꾸러미 모두 `concept.png`가 있어야 한다 (README 에 "초안 대기"가 없어야 한다).

```
대장 9명은 끝났다. 다음은 일반 병과 5종 — 이름 없는 용병과 세력 병사 전부가 같이 쓰는 기본 그림이다. 직업마다 PNG 한 장 (1×4 한 줄).

브랜치 규칙은 같다: 자료는 claude/dot-fantasy-management-game-saupju 에서 읽고, 결과는 art-inbox 에만 올린다.
화풍 기준(앵커)은 그대로 art-inbox 의 art/inbox/sheet_captain_blademaster.png.

순서와 자료 (claude/dot-fantasy-management-game-saupju 브랜치의 art/requests/phase3/<id>/):
1. class_warrior → art/inbox/sheet_class_warrior.png
2. class_archer  → art/inbox/sheet_class_archer.png
3. class_mage    → art/inbox/sheet_class_mage.png
4. class_cleric  → art/inbox/sheet_class_cleric.png
5. class_rogue   → art/inbox/sheet_class_rogue.png

가장 중요한 규칙 — 열쇠 색 (README 의 KEY COLOURS):
- 이 그림 한 장을 모든 진영이 같이 쓰고, 게임이 제복 색을 진영 색으로 바꿔 칠한다. 정확히 같은 색의 픽셀만 바뀐다.
- 제복(겉옷·로브와 높은 깃·후드 상의와 마스크·두건과 베일·후드와 망토, 전사의 방패 면)은 이 네 색으로만: #263459(가장 어두운 그늘·주름) #394b78(그늘) #52679c(바탕) #7489be(밝은 면).
- 장식(테두리·허리 천·후드와 두건의 앞 가장자리·모자 띠·사제의 가슴 원판·도적의 스카프)은 이 세 색으로만: #3f7a6c(그늘) #5ea590(바탕) #96d1bb(밝은 면).
- 그 자리는 평평하게: 디더링·그라데이션·노이즈·질감·부드러운 섞임·중간 색 없이, 명암은 이 단계만으로.
- 이 7색은 다른 곳(금속·피부·머리·가죽·눈·외곽선·배경)에 쓰지 않는다. 그 밖에는 파랑·청회색·청록·민트를 쓰지 않는다:
  금속은 푸른 기 없는 중성 회색, 가죽·나무는 따뜻한 갈색, 그 밖의 그늘도 따뜻하거나 중성 (이 시트에서는 "그늘은 보라·파랑 쪽" 규칙보다 이것이 우선).
- 제복의 외곽선은 보통의 어두운 외곽선 (열쇠 색 아님). 내보낸 뒤 색 고르개로 제복 픽셀이 정확히 이 16진수인지 확인.

캐릭터마다:
- 그 폴더 README.md 의 "Prompt for GPT" 블록이 지시다. guide_strip.png 와 같은 자세·크기·위치 (머리 110px, 발바닥 y=870).
- 얼굴은 가린다 (주인 요청): 한 그림이 서로 다른 수백 명을 대신하므로 전사 = 면갑 내린 투구(눈 틈만), 궁수 = 후드 + 코 아래 천 마스크,
  마법사 = 깊게 눌러쓴 모자 챙 + 높은 깃(얼굴은 그늘), 성직자 = 깊은 두건 + 베일(얼굴은 그늘), 도적 = 깊은 후드 + 스카프(얼굴은 그늘).
  네 자세 모두 같은 만큼 가리고(피격 때도 벗겨지지 않음), 얼굴 그늘은 따뜻하거나 중성인 어두운 색(파랑·열쇠 색 금지). 보이는 부분은 특징 없이. 문장·무늬 없음.
- concept.png 는 디자인만. 화풍·비율은 앵커(바렌)와 똑같이.
- 마젠타 규칙: 인물의 어떤 색도 #FF00FF 와 RGB 거리 150 미만이면 안 된다. 팔레트를 줄일 때 배경색과 합치지 마.
- 저장 전 SELF-CHECK 확인, 틀리면 다시 그려.

올리기 (art-inbox 브랜치):
- 2~3장마다 커밋·푸시해도 된다. art/inbox/NOTES.md 에 "3단계 — 일반 병과" 절: 만든 파일, 열쇠 색을 어디에 썼는지, 다르게 한 점.
- art/inbox/ 밖의 파일은 고치지 마. 파일 이름을 바꾸지 마. 다섯 장이 끝나면 멈춰.
```

## 메시지 D-웹 — 저장소를 못 읽는 곳 (한 번에 한 직업)

첨부 (이 순서로): 승인된 바렌 PNG(앵커), 그 직업 폴더의 `guide_strip.png`, `guide_1_idle.png` ~ `guide_4_hit.png`, `concept.png`.

```
첫 번째 첨부(바렌)가 승인된 화풍 기준이다. 이 화풍으로 일반 병과 <직업> 그림을 그려 줘. 아래 영어 블록이 실제 지시다 (특히 KEY COLOURS).
- 1536x1024, 1×4 한 줄, guide_strip.png 와 같은 자세·크기·위치, 배경 #FF00FF. concept.png 는 디자인만.
- 제복은 #263459 #394b78 #52679c #7489be 로만, 장식은 #3f7a6c #5ea590 #96d1bb 로만, 평평하게. 이 7색은 다른 곳에 쓰지 않는다.
- 얼굴은 블록의 CHARACTER 대로 가린다 (면갑·후드·마스크·모자 챙과 높은 깃·두건과 베일). 네 자세 모두 같은 만큼, 피격 때도 벗겨지지 않게.
- 저장소 경로·커밋은 하지 말고 완성된 PNG 를 이 대화에 돌려줘. SELF-CHECK 확인 후 멈춰.

<여기에 그 직업 README.md 의 Prompt for GPT 블록>
```

## 메시지 E — 1차 몬스터 8종 (초안: 주인이 초안을 고른 뒤에 보낸다; 저장소용)

> 보내기 전: 여덟 꾸러미 모두 `concept.png`가 있어야 한다. D 와 같은 대화에 이어 보내도 되고 따로 보내도 된다.

```
다음은 전투에 가장 자주 나오는 보통 몬스터 8종이다. 몬스터마다 PNG 한 장.

브랜치 규칙은 같다: 자료는 claude/dot-fantasy-management-game-saupju 에서 읽고, 결과는 art-inbox 에만 올린다.
화풍 기준(앵커)은 art-inbox 의 art/inbox/sheet_captain_blademaster.png — 칠하는 방식·외곽선·팔레트 처리·조명·픽셀 배율을 맞춘다.

순서와 자료 (claude/dot-fantasy-management-game-saupju 브랜치의 art/requests/phase3/<id>/):
1. monster_skeleton      → art/inbox/sheet_monster_skeleton.png       (1×4 한 줄, 사람 가이드 guide_strip.png)
2. monster_wolf          → art/inbox/sheet_monster_wolf.png           (2×2 격자, guide_layout.png)
3. monster_desert-bandit → art/inbox/sheet_monster_desert-bandit.png  (1×4 한 줄, guide_strip.png)
4. monster_harpy         → art/inbox/sheet_monster_harpy.png          (2×2 격자)
5. monster_bandit        → art/inbox/sheet_monster_bandit.png         (1×4 한 줄, guide_strip.png)
6. monster_gargoyle      → art/inbox/sheet_monster_gargoyle.png       (2×2 격자)
7. monster_giant-spider  → art/inbox/sheet_monster_giant-spider.png   (2×2 격자)
8. monster_wraith        → art/inbox/sheet_monster_wraith.png         (1×4 한 줄, guide_layout.png)

몬스터마다:
- 그 폴더 README.md 의 "Prompt for GPT" 블록이 지시다 (BRIEF = 실루엣·크기·공격, DESIGN, COLOURS, FIX, POSES).
- 사람형(해골 병사·사막 도적·산적)은 대장처럼 guide_strip.png 와 같은 자세·크기·위치 (머리 110px, 발바닥 y=870). 가이드의 방패는
  README 대로 바꾼다 (사막 도적 = 방패 없이 빈손, 산적 = 작은 버클러).
- 사람형이 아닌 것은 posekit 마네킹이 없다: 자세는 글로, 자리·크기는 guide_layout.png 의 상자로 (상자·선·글씨는 그리지 마).
  guide_scale.png = 같은 배율의 4등신 사람 옆에 대기 크기 — 모두 사람과 같은 픽셀 배율이다 (크게 그리지 마).
  2×2 격자는 768x512 네 칸 (왼쪽 위 대기, 오른쪽 위 공격 준비, 왼쪽 아래 공격 타격, 오른쪽 아래 피격), 칸마다 맨 아래 픽셀이 칸 위에서 y=461.
- 다리·머리·꼬리 수를 지킨다 (늑대 네 다리·머리 하나, 거미 여덟 다리). 원거리 몬스터(하피·가고일·망령)도 투사체·빛·효과는 그리지 않는다 (엔진이 그린다).
- 마젠타 규칙: 어떤 색도 #FF00FF 와 RGB 거리 150 미만이면 안 된다 (하피의 보라 깃털은 짙은 청보라로).
- 저장 전 SELF-CHECK 확인, 틀리면 다시 그려.

올리기 (art-inbox 브랜치):
- 2~3장마다 커밋·푸시해도 된다. art/inbox/NOTES.md 에 "3단계 — 1차 몬스터" 절: 만든 파일, 다르게 한 점, 다시 그리고 싶은 것.
- art/inbox/ 밖의 파일은 고치지 마. 파일 이름을 바꾸지 마. 여덟 장이 끝나면 멈춰.
```

## 메시지 E-웹 — 저장소를 못 읽는 곳 (한 번에 한 몬스터)

첨부 (이 순서로): 승인된 바렌 PNG(앵커), 사람형이면 `guide_strip.png`·`guide_1_idle.png` ~ `guide_4_hit.png`, 아니면 `guide_layout.png`·`guide_scale.png`, 그리고 `concept.png`.

```
첫 번째 첨부(바렌)가 승인된 화풍 기준이다. 이 화풍과 같은 픽셀 배율로 몬스터 <이름>을 그려 줘. 아래 영어 블록이 실제 지시다.
- 배치는 블록의 DELIVERABLE 대로 (2×2 격자 또는 1×4 한 줄), 배경 #FF00FF, 가이드의 선·상자·글씨·회색 사람은 그리지 마.
- concept.png 는 디자인만. 투사체·빛·효과 없음.
- 저장소 경로·커밋은 하지 말고 완성된 PNG 를 이 대화에 돌려줘. SELF-CHECK 확인 후 멈춰.

<여기에 그 몬스터 README.md 의 Prompt for GPT 블록>
```

### 받은 뒤 처리 (D·E, Claude Code)

받은 파일만 `art-inbox`에서 가져와 하나씩 미리보기 → 확인 후 등록한다. 직업·1차 몬스터는 요청서의 `scale`·`cell`·`layout`·`tint`를 쓰므로 옵션이 필요 없다.

```
python3 tools/art/sheets.py art/inbox/sheet_class_warrior.png --dry-run --work /tmp/sheets   # preview_x4.png + preview_tint_x4.png, 열쇠 색 비율 출력
python3 tools/art/sheets.py art/inbox/sheet_monster_wolf.png --dry-run --work /tmp/sheets    # 2x2 격자·배율·칸은 요청서에서
python3 tools/art/sheets.py art/inbox/sheet_class_warrior.png                                # 등록 (--tint-outfit/--tint-accent 자동)
```
