# 3단계 전투 캐릭터 — GPT(그림 쪽)에 보낼 메시지

> 손으로 쓴 문서. 규칙은 `art/requests/gpt_handoff_notes.md`, 캐릭터별 자료는 `art/requests/phase3/<id>/`
> (`python3 tools/art/handoff.py`로 만든다), 요청서 목록은 `art/requests/phase3.md`.

## 주인용 사용법 (한국어)

1. **먼저 이 자료가 원격 브랜치에 올라가 있어야 한다.** 그림 쪽은 `claude/dot-fantasy-management-game-saupju` 브랜치에서
   `art/requests/…`를 읽고, 결과 PNG 는 `art-inbox` 브랜치에 올린다. (Claude 에게 "푸시해 줘"라고 하면 올린다.)
2. **메시지 A**를 그림 쪽(Codex / ChatGPT)에 그대로 붙여 넣는다. 바렌 한 장만 그리고 멈춘다.
   - ChatGPT 웹처럼 저장소를 못 읽는 곳이면 `art/requests/phase3/captain_blademaster/`의 그림 파일
     (`guide_strip.png`, `guide_1..4`, `concept.png`, `concept_pixel.png`, `portrait.png`)을 직접 첨부하고,
     `README.md`의 "Prompt for GPT" 블록을 메시지 뒤에 붙인다. 결과 PNG 는 GitHub 웹에서 `art-inbox` 브랜치의 `art/inbox/`에 끌어다 놓는다.
   - 목표 게임 스크린샷(참고 화면)이 있으면 같이 첨부한다. 남의 게임 화면이라 저장소에는 넣지 않았다.
3. 바렌이 올라오면 Claude 에게 "바렌 올렸다"고 알린다. Claude 가 아래 「받은 뒤 처리」로 게임 크기 미리보기를 만들어 보여 준다.
   - 승인 기준: 4등신인가, 오른쪽을 보는 정면 3/4인가, 4자세가 가이드와 같은가, 64px 로 줄여도 읽히는가, 차분한 색·검정 아닌 외곽선인가,
     효과·바닥·글자가 없는가, 이 화풍으로 8명을 더 그려도 좋은가.
   - 마음에 안 들면 **메시지 A2**(다시 그리기)로 고칠 점을 적어 보낸다. 승인될 때까지 B 로 넘어가지 않는다.
4. 승인하면 **메시지 B**를 보낸다. 8명(+ 선택: 로드릭 기마)을 바렌에 맞춰 그린다. 몇 명씩 끊어서 올려도 된다.
5. 올라올 때마다 Claude 에게 알리면 처리·확인하고, 다시 그릴 것은 `art/requests/feedback.md`에 적는다.

### 받은 뒤 처리 (Claude Code 가 한다)

```bash
git fetch origin art-inbox
git checkout origin/art-inbox -- art/inbox/sheet_captain_blademaster.png art/inbox/NOTES.md
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png --dry-run --work /tmp/sheets   # 미리보기: /tmp/sheets/*/preview_x4.png
python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png                                 # 등록 → assets/art/sheets/ + manifest
# 나머지: python3 tools/art/sheets.py art/inbox/sheet_captain_<key>.png  (전부: python3 tools/art/sheets.py)
# 기마(게임 미사용): python3 tools/art/sheets.py art/inbox/sheet_captain_lancer_mounted.png --grid 2x2 --dry-run --work /tmp/sheets
```

`sheets.py`가 자세 4개를 찾아 배경을 지우고, 대기 자세 몸 높이를 64px 로 맞춘 같은 배율로 줄여 80×80 칸 시트(숨쉬기 대기 4칸 + 공격 2칸 + 피격 1칸)를
만들고 `assets/art/manifest.json`에 등록한다. 왼쪽을 보고 그렸으면 `--flip`. 그 뒤 게임 전투 화면에서 확인한다.

### 무기·자세 대응표 (posekit 일반 마네킹, 가장 가까운 무기)

| 순서 | 캐릭터 | posekit 무기 | ① 대기 | ② 준비 | ③ 타격 | ④ 피격 | 그림에서 바꿀 것 |
|---|---|---|---|---|---|---|---|
| 1 | 바렌 `blademaster` (앵커) | katana | idle_0 | attack_1 | attack_2 | hit_0 | — |
| 2 | 브리긴다 `ironwall` | sword_shield | idle_0 | attack_1 | attack_2 | hit_0 | 칼 → 철퇴, 원형 방패 → 탑실드 |
| 3 | 이사벨 `tactician` | staff | cast_0 | cast_1 | cast_2 | hit_0 | 지팡이 → 장교 지휘봉, 타격 = 손가락으로 지휘 |
| 4 | 로드릭 `lancer` | spear | idle_0 | attack_1 | attack_3 | hit_0 | 창 → 깃발 달린 랜스 (걷는 기사) |
| 5 | 키아라 `huntress` | bow | idle_0 | attack_2 | attack_3 | hit_0 | 준비 = 끝까지 당김, 타격 = 쏜 직후(화살 없음) |
| 6 | 펠릭스 `hedgemage` | staff | idle_0 | cast_1 | cast_2 | hit_0 | 구슬 → 나무 끝, 불꽃 없이 빈 손바닥 |
| 7 | 마그다 `fieldmedic` | staff | idle_0 | cast_1 | cast_2 | hit_0 | 지팡이 = 긴 자루 철퇴(구슬 자리에 머리), 치유 빛 없음 |
| 8 | 진 `fixer` | none | idle_0 | attack_1 | attack_2 | hit_0 | 가까운 손에 단검 하나, 역수 |
| 9 | 하랄드 `veteran` | sword_shield | idle_0 | attack_1 | attack_2 | hit_0 | 둥근 나무 방패 + 한손검 |
| 10 | 로드릭 기마 (선택) | — (가이드 없음) | 2×2 격자, `guide_mounted_layout.png`는 크기·기준선 참고 | | | | 말 머리 하나, 게임 미사용 |

---

## 메시지 A — 지금 보낼 것 (바렌만, 화풍 기준)

```
게임 저장소 https://github.com/allycat92/pixel-management 의 전투 캐릭터 그림을 부탁해. 이번에는 바렌 한 장만.

읽을 것 (브랜치 claude/dot-fantasy-management-game-saupju 에 있다):
1. art/requests/gpt_handoff_notes.md — 그림 규칙. 다른 문서와 다르면 이것이 우선이다.
2. art/STYLE.md 의 "전투 캐릭터" 절.
3. art/requests/phase3/captain_blademaster/ 폴더 전부 — README.md 의 "Prompt for GPT" 블록이 실제 지시이고,
   guide_strip.png(자세·배치·크기 견본), guide_1_idle ~ guide_4_hit(같은 자세 크게), concept.png(디자인만),
   concept_pixel.png(도트로 줄여도 살아남는 단순한 형태의 기준), portrait.png(얼굴·머리만).
(스크린샷을 첨부했다면 목표 게임의 화면이다: HD 도트의 밀도·차분한 색감만 참고하고 캐릭터는 베끼지 마.)

그릴 것: 바렌(captain_blademaster) 전투 스프라이트 띠 한 장.
- 1536x1024 PNG, 같은 캐릭터 4번을 한 줄로: 대기 / 공격 준비 / 공격 타격 / 피격. guide_strip.png 와 같은 자세·크기·위치.
- 4등신, 오른쪽을 보는 정면 3/4 시점, 빛은 왼쪽 위. 발은 모두 y=870 가로선 위. 자세끼리·테두리와 닿지 않게.
- 배경은 완전히 평평한 마젠타 #FF00FF. 바닥·그림자·글자·칸 선·효과(검기, 먼지, 빛) 없이.
- NovelAI 초안(concept)에서는 옷·색·머리띠·흉터·카타나 같은 디자인만 가져오고, 비율·칠하는 방식·외곽선·채도는 따라 하지 마.
- 이 그림이 나머지 8명 모두의 "화풍 기준(앵커)"이 된다. 깔끔하고 단순한 큰 형태로, 64px 로 줄여도 읽히게.
- 저장하기 전에 README 의 SELF-CHECK 를 하나씩 확인하고, 틀린 것이 있으면 다시 그려.

저장·올리기:
- art/inbox/sheet_captain_blademaster.png 로 저장 (이름 그대로. 지금 있는 NovelAI 판을 덮어쓴다).
- art/inbox/NOTES.md 에 "3단계 — 바렌 (화풍 기준)" 절을 더해: 만든 파일, 프롬프트·가이드와 다르게 한 점, 다시 그리고 싶은 점.
- art-inbox 브랜치에 커밋해서 푸시. art/inbox/ 밖의 파일은 고치지 마.

그 다음 멈추고 내 승인을 기다려. 다른 캐릭터는 아직 그리지 마.
```

## 메시지 A2 — 바렌을 다시 그릴 때 (필요할 때만)

```
바렌(art/inbox/sheet_captain_blademaster.png)을 다시 그려 줘. 규칙·자료는 지난번과 같다
(art/requests/gpt_handoff_notes.md, art/requests/phase3/captain_blademaster/README.md).
고칠 점:
- <여기에 고칠 점을 적는다. 예: 머리가 너무 크다(4등신으로), 외곽선이 너무 검고 두껍다, 색이 너무 밝다, 2번 자세가 가이드와 다르다>
같은 파일 이름으로 덮어쓰고 NOTES.md 에 고친 점을 적어 art-inbox 에 푸시한 뒤 다시 멈춰.
```

## 메시지 B — 바렌 승인 후 (나머지 8명 + 선택 기마)

```
바렌 승인. art-inbox 브랜치의 art/inbox/sheet_captain_blademaster.png 가 이제 "화풍 기준(앵커)"이다.
나머지 창설 후보 대장 8명을 이 앵커에 맞춰 그려 줘. 캐릭터마다 PNG 한 장.

순서와 자료 (브랜치 claude/dot-fantasy-management-game-saupju 의 art/requests/phase3/<id>/):
1. captain_ironwall   → art/inbox/sheet_captain_ironwall.png
2. captain_tactician  → art/inbox/sheet_captain_tactician.png
3. captain_lancer     → art/inbox/sheet_captain_lancer.png
4. captain_huntress   → art/inbox/sheet_captain_huntress.png
5. captain_hedgemage  → art/inbox/sheet_captain_hedgemage.png
6. captain_fieldmedic → art/inbox/sheet_captain_fieldmedic.png
7. captain_fixer      → art/inbox/sheet_captain_fixer.png
8. captain_veteran    → art/inbox/sheet_captain_veteran.png
(선택, 맨 마지막) captain_lancer README 의 "추가 선택: 기마 시트" → art/inbox/sheet_captain_lancer_mounted.png
   게임은 아직 안 쓰는 여분 그림이다. 2x2 격자, 말 머리는 정확히 하나.

캐릭터마다:
- 그 폴더의 README.md "Prompt for GPT" 블록을 지시로 쓰고, guide_strip.png 와 같은 자세·크기·위치로 그려.
- 화풍은 앵커(바렌)와 똑같이: 4등신 비율, 칠하는 방식, 외곽선, 팔레트 처리, 조명, 캐릭터 크기(머리 하나 110px, 발 y=870).
  각자의 NovelAI 초안은 디자인(옷·색·무기·흉터)만 참고하고 화풍·비율은 따라 하지 마.
- README 의 FIX 를 꼭 지켜: 마그다 완장의 흰 십자 없음(무늬 없는 짙은 빨강), 진은 단검 하나·역수·림 라이트,
  이사벨은 4등신, 브리긴다는 땋은 머리가 보이게, 펠릭스·마그다는 불꽃·치유 빛 없음, 키아라는 쏜 뒤 화살 없음.
- 저장 전 SELF-CHECK 확인, 틀리면 다시 그려.

올리기:
- 2~3명 끝날 때마다 art-inbox 브랜치에 커밋·푸시해도 된다 (빨리 확인할 수 있게).
- art/inbox/NOTES.md 에 "3단계 — 창설 후보 8명" 절: 만든 파일, 다르게 한 점, 다시 그리고 싶은 것.
- art/inbox/ 밖의 파일은 고치지 마. 파일 이름을 바꾸지 마.
```
