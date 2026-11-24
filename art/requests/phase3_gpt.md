# 3단계 전투 캐릭터 — GPT(그림 쪽)에 보낼 메시지

> 손으로 쓴 문서. 규칙은 `art/requests/gpt_handoff_notes.md`, 캐릭터별 자료는 `art/requests/phase3/<id>/`
> (`python3 tools/art/handoff.py`로 만든다), 요청서 목록은 `art/requests/phase3.md`.

## 브랜치 규칙 (그림 쪽에도 그대로 전한다)

- **읽기**: 모든 자료(규칙·가이드·초안·README)는 `claude/dot-fantasy-management-game-saupju` 브랜치에서 읽는다.
  웹 주소: <https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3>
  (파일 하나는 `https://raw.githubusercontent.com/allycat92/pixel-management/claude/dot-fantasy-management-game-saupju/<경로>`).
- **쓰기**: 결과 PNG 와 `art/inbox/NOTES.md`는 **`art-inbox` 브랜치에만** 올린다. `art-inbox`에 있는 예전 `art/STYLE.md`·`art/requests/`는
  옛 규칙이므로 읽지 않는다. `sheet_captain_*.png`는 `art-inbox`에서는 **새 파일**이다
  (claude 브랜치의 `art/inbox/sheet_captain_blademaster.png`는 예전 NovelAI 판이고, 그림 쪽은 건드리지도 복사하지도 않는다).

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
   - 승인하면 Claude 가 승인된 바렌을 claude 브랜치에도 커밋·푸시한다(예전 NovelAI 판을 바꾼다). 그 뒤 두 브랜치의 앵커가 같다.
4. **메시지 B**(웹이면 **메시지 B-웹**)를 보낸다. 8명(+ 선택: 로드릭 기마)을 바렌에 맞춰 그린다. 몇 명씩 끊어서 올려도 된다.
5. 올라올 때마다 Claude 에게 알리면 처리·확인하고, 다시 그릴 것은 `art/requests/feedback.md`에 적는다.

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
