# 전투 이펙트 설계서: 범용 이펙트, 연출 뼈대, 캐릭터 시그니처

작성 2026-11-27. 클라우드 세션이 정리한 설계안이다. 아직 게임 코드는 아무것도 바꾸지 않았다.
근거 자료는 세 가지다. 현재 VFX 코드 지도(`js/battle.js`), 엔진 쪽 설계안과 작가 쪽 설계안, 그리고 "판에 박힘" 관점의 반대 검토.
줄 번호는 따로 적지 않으면 `js/battle.js` 기준이다.

---

## 0. 주인 결정 사항 (구속력 있음)

주인이 직접 한 말:

> 1. 이건 이해했고 동의해.
> 2. 이건 좀 신중하게 접근하고 싶기는 하네. 말만 고유성이고 결국 '판에 박혔다'는 느낌이 드는건 원하지 않으니까.
> 이 부분도 '완성된 이펙트'로서의 범용 에셋과 '연출의 뼈대'로서의 범용 에셋을 구분해서 만들던가 하자. 아니면 그런 코드값을 몇가지 정의해두었다가 이펙트 작업의 기초로 삼거나.

이 설계가 따르는 결정 (앞선 대화에서 확정된 것 포함):

| # | 결정 | 이 문서에서 반영한 곳 |
|---|---|---|
| D1 | **두 등급.** 일반 유닛용 범용 이펙트는 계열별로 만든다(베기, 찌르기, 타격, 화살 적중, 치유, 불, 번개, 저주). 순서는 이미지 우선: 승인된 키 이미지 1장 → 픽셀 키 프레임 → Antigravity가 그리는 3~6프레임 애니메이션, 여기에 코드 광원과 입자를 더한다. | §1, §8 1단계 |
| D2 | **시그니처 이펙트.** 캡틴, 특수 캐릭터(영웅), 적 보스가 대상이다. 비용이 들어도 화려하게 만든다. 캐릭터는 앞으로 스킬이 여러 개로 늘어난다. | §3, §8 |
| D3 | **이펙트 정체성 키트.** 캐릭터마다 먼저 키트를 만든다: 색 2~3개, 모티프(사자, 사슬, 룬, 서리, 그림자…), 형태 언어. 키트에서 그린 모티프 에셋은 그 캐릭터의 모든 스킬이 재사용한다. ("1. 동의") | §2 |
| D4 | **판에 박힌 느낌 금지.** 범용 에셋을 둘로 나눈다. (a) **완성된 범용 이펙트**: 일반 유닛 전용이다. (b) **연출 뼈대**: 보이지 않는 구조를 코드값과 프리셋으로 정의한 것이고, 이펙트 작업의 기초가 된다. 구조는 타이밍·이징 곡선, 공간 경로, 레이어 슬롯(차지 → 이동 → 적중 → 잔상, 화면 레이어), 카메라·히트스톱·섬광 패턴, 방출기 동작이다. 시그니처는 뼈대를 빌려 쓸 수 있지만 **눈에 보이는 픽셀은 전부 그 캐릭터 전용으로 그린 그림**이다. | §1, §4, §5 |
| D5 | **재채색 에셋은 절대 만들지 않는다.** 세력 색은 런타임 틴트로만 입힌다. 남의 이펙트는 공부용 참고로만 쓴다. NovelAI는 주인이 요청할 때 디자인 초안으로만 쓴다. 최종 그림은 Antigravity가 그린다. | §1.4, §5, §7 |

---

## 1. 두 등급, 그리고 "완성된 범용 이펙트"와 "연출 뼈대" 사이의 엄격한 선

### 1.1 세 가지 콘텐츠 종류

에셋 종류는 세 가지다. 섞이지 않게 각각 폴더, 로더, 검사기를 따로 둔다.

| 종류 | 무엇인가 | 눈에 보이는가 | 누가 쓰는가 | 위치 |
|---|---|---|---|---|
| **A. 연출 뼈대** (skeleton) | 곡선, 프레임 시계, 타임라인(단계 틀), 경로, 배치 패턴, 방출기 물리, 잔상 동작, 화면·카메라 패턴, 이름 붙은 앵커 | **보이지 않는다.** (params, t, rng)를 받아 숫자(위치, 알파, 크기, 프레임 번호, 생성 목록)를 돌려주는 순수 함수다. 색 리터럴도 이미지 id도 없다. | 모두 (범용과 시그니처) | `js/fx/skel.js` |
| **B. 완성된 범용 이펙트** | 계열별 승인 키 이미지 → 픽셀 3~6프레임 + 코드 광원·입자 | 보인다. 틴트 키 색으로 그려서 런타임에 진영·세력 색을 입힌다. | **일반 유닛만** (병사, 몬스터, `GENERIC_SPECIAL`을 쓰는 라이벌·세력 캡틴) | `assets/fx/generic/*.json` + `assets/art/fx/generic/` |
| **C. 시그니처** | 캐릭터 키트 + (캐릭터, 스킬)마다 하나씩인 스펙 | 보인다. 그 주인의 `fx/sig/<owner>/*` 시트와 키트 색만 쓴다. 재채색도 공유도 하지 않는다. | 캡틴 33, 영웅 7, 보스 7, 그리고 이들이 앞으로 얻을 스킬 | `assets/fx/kits/<owner>.json`, `assets/fx/sig/<owner>/<skill>.json` + `assets/art/fx/sig/<owner>/` |

주인이 말한 두 방법을 **둘 다** 쓴다. 종류 B가 "완성된 이펙트로서의 범용 에셋"이고, 종류 A가 "코드값을 정의해 두고 이펙트 작업의 기초로 삼는 것"이다.

### 1.2 선을 지키는 규칙 (기억이 아니라 도구로 강제)

1. **뼈대에는 색이 없다.** `js/fx/skel.js` 안에 `#hex`, `rgb(`, `'fx/`, `assets/` 리터럴이 하나라도 있으면 `tools/fx/check.js`가 실패한다.
2. **범용 이펙트는 소유자 유닛에게 기본적으로 거부된다(deny-by-default).** 리졸버는 `capKey`/`heroKey`/`boss`가 있는 유닛에게 종류 B를 절대 돌려주지 않는다. 스펙의 `suppress` 목록에 무엇이 적혀 있든 상관없다. 시그니처가 아직 없으면 §6.6의 중립 placeholder가 나간다.
3. **시그니처 스펙은 자기 주인의 그림만 참조한다.** 모든 `src`/`particle` 시트는 `fx/sig/<bind.owner>/…`여야 한다. `fx/generic/*`을 참조하면 등록이 거부된다.
4. **뼈대의 매개변수는 두 종류로 나뉜다.**
   - `physics`: 공유해도 된다. 중력, 바닥 원근 0.4, 감쇠, 앵커, 적중 동기화가 여기에 든다. 기본값이 있다.
   - `style`: 눈에 보인다. 개수, 간격, 진입 각도, 프레임 간격, 차지 길이, 화면 강도가 여기에 든다.
   - **시그니처 스펙에서는 `style` 매개변수에 기본값이 없다.** 검사기는 하나하나 직접 적은 값을 요구한다. 범용 스펙만 기본값을 쓸 수 있다. 판에 박힘은 대개 "바빠서 기본값을 그대로 둔" 데서 생기는데, 이 규칙이 그 길을 막는다.
5. **뼈대를 쓸지는 그림이 정한다.** 시그니처는 키 이미지를 먼저 승인받는다. 뼈대는 그 그림에 맞춰 고르거나 덮어쓰고, 맞는 게 없으면 `custom`으로 새로 짠다. Antigravity가 받는 가이드에는 프리셋 경로나 슬롯 상자를 그리지 않는다(§7.3). 그려 주면 따라 그리게 되기 때문이다.

### 1.3 "보이지 않는 구조"와 "보이는 구조"의 경계

반대 검토에서 지적된 점이 있다. 일부 "뼈대"는 사실상 실루엣이라서, 플레이어가 여러 번 보면 같은 기술로 알아본다. 그래서 프리셋마다 등급을 붙인다.

| 자유롭게 공유 (보이지 않음) | 공유하되 주인별로 직접 작성하고 사용 상한을 둠 (보이는 구조) |
|---|---|
| 모든 `curve.*`, `clock.sheet`, 바닥 원근 0.4, 중력·튕김·감쇠, 앵커, 적중 동기화, `place.stagger`, `residue.linger`(상태 추적만 함) | `place.ringGround`, `place.radial`, `place.alongPath`, `path.orbit`, `path.skyDrop`, `path.shotRemap`, `path.zigzag`, `path.cone`, 땅 고리로 쓰는 `curve.expand`, `emit.spiralIn`, 차지 길이가 고정된 `tl.windupStrike`, `clock.stepped`, `screen.*` 조합 전부, 컷인 |

오른쪽 열의 프리셋은 시그니처에서 쓸 때 모든 `style` 값을 직접 적어야 한다. 또 §5의 구조 구별 규칙을 통과해야 한다.

### 1.4 재채색 금지와 세력 틴트

- 범용 시트는 class 시트의 `sheet.tint`와 같은 방식으로 키 색을 선언한다. `FxPal`이 런타임에 세력 램프로 바꿔 캐시한다. 파일은 하나뿐이다.
- 시그니처 시트에는 틴트가 없다. 다른 색 버전이 필요해도 파일로 만들지 않는다.
- 등록할 때 마스크 재사용 검사를 한다(§5.4). 다른 주인의 프레임이나 범용 프레임과 알파 마스크가 너무 닮았으면 "X의 재채색"으로 보고 거부한다.

---

## 2. 정체성 키트 템플릿

### 2.1 키트가 정하는 것

키트는 캐릭터마다 한 번 만든다. 그 캐릭터의 **모든** 스킬이 키트를 공유한다. 지금 스킬 1개에도, 앞으로 늘어날 스킬에도 쓴다.

| 항목 | 내용 | 비고 |
|---|---|---|
| 색 (2~3) | `key`, `body`, `accent`. 색마다 흰 심을 포함해 4단 이하로 그린다. 그림자는 보라·남색 쪽, 빛은 따뜻한 노랑 쪽으로 기운다(`art/STYLE.md`). | **색은 구별의 근거로 세지 않는다**(§5). 캡틴 강조색 33개 중 14개가 금색·노랑 계열이라 색만으로는 구별되지 않는다. |
| 모티프 계열 | 닫힌 분류표에서 하나 고르고, 그 안의 **하위 형태**를 정한다(§5.2) | 예: 신성광 계열 → 기둥 / 파편 / 후광고리 / 종 / 경전 |
| 형태 언어 | 닫힌 어휘로 고른다. 기하(angular/round/linear/organic/crystalline/radial), 움직임(down/up/inward/outward/lateral/orbit/hop/static), 리듬(snap/heavy/flutter/stutter/sustain/delayed), 밀도(one/few/swarm), 테두리(hard/dithered/soft) | 자유 서술은 비고로만 쓴다 |
| 금지 형태 | 이 캐릭터가 **절대** 쓰지 않는 모양 | 이웃 키트와 겹치지 않게 막는 장치 |
| 움직임 동사 | 3~4개 | 예: "내리꽂힌다, 맞물린다, 버틴다" |
| 프레임 박자 | 캐릭터 고유의 리듬. stutter, 100~150ms 느린 잔상, 2프레임씩(on twos) 등 | 55~80ms 고정 규칙은 범용 이펙트에만 적용한다 |
| 화면 박자 | 이 캐릭터의 화면 연출 어휘. 예: 세로 흔들림만, 섬광 없음 | dim·stop·shake·flash 네 가지를 다 쓰는 조합은 궁극기 전용 |
| 컷인 | 진입 방향, 프레임 모양, 모티프 배경, 타이밍 곡선 | 모든 캐릭터가 같은 CSS 슬라이드를 쓰는 지금 방식을 없앤다 |
| 키트 조각 | 3~6개. 게임 픽셀 1:1로 그린다(문장/엠블럼, 입자 스프라이트, 궤적 타일, 적중 핵, 잔상 데칼) | 스킬은 키트 조각을 하나 이상 재사용하고, 새 "결정 프레임"도 하나 이상 가져와야 한다 |
| 기본공격 조각 | 3프레임 적중 1개 | 캡틴이 가장 자주 보이는 순간이 기본공격이다(§9 Q3) |
| 가장 가까운 키트 | 이웃 2~3개와, 그들과 다른 점 | 검사기와 비교 페이지가 이 정보를 쓴다 |

파일 위치: `art/requests/fx/<owner>/kit.md`(사람용), `assets/fx/kits/<owner>.json`(기계용). `owner`는 `captain/<capKey>`, `hero/<heroKey>`, `boss/<slug>` 중 하나다. 보스 slug는 `u.mon` 이름(예: '서리 거인 왕')에서 만든 ASCII 이름이다. `tpl`은 쓰지 않는다. 거미 여왕과 모래 폭군이 같은 `bug` 템플릿이기 때문이다.

### 2.2 채운 예시 1: 바렌, 떠돌이 검귀 (`captain/blademaster`)

데이터 출처: `js/classes.js:273`, `js/content.js:422`.
- 외형 `L('#3a1018', '#e8e4d8', 'band', 'sword')`. 짙은 와인색 옷, 상아색 강조, 머리띠, 검.
- 스킬 [`참격` 근접 1.15배 cd 0.9, `회전베기` 근접 1.4배 cd 7 aoe 18].
- 대사: "검 한 자루면 충분하다. 앞은 내가 연다."

```json
{
  "owner": "captain/blademaster", "name": "바렌", "approved": null,
  "colours": { "key": "#e8e4d8", "body": "#3a1018", "accent": "#b8323c" },
  "motif": { "family": "blade", "subform": "single long cut-line that splits the air; torn cloth band ends" },
  "shape": { "geometry": "linear", "motion": "lateral", "rhythm": "delayed",
             "density": "one", "edge": "hard" },
  "never": ["glow rings", "orbiting dots", "multiple parallel arcs", "sparks fans"],
  "verbs": ["벤다", "늦게 갈라진다", "펄럭인다"],
  "cadence": "long still hold (120-160ms) then 1-frame cut, the split appears 2 frames late",
  "screen": { "allowed": ["hitstop", "shake.x"], "forbidden": ["dim", "flash"], "note": "a horizontal micro-shake; silence before the cut" },
  "cutin": { "enter": "horizontal slit opening", "frame": "letterbox bar", "backdrop": "kit/band_tail" },
  "pieces": [
    { "id": "cutline",   "size": [64, 3],  "frames": 3, "use": "the visible slash, drawn with 1px core + 1px ivory edge" },
    { "id": "split",     "size": [24, 24], "frames": 4, "use": "air/flesh split that opens late on the target" },
    { "id": "band_tail", "size": [10, 6],  "frames": 3, "use": "wine cloth scrap particle" },
    { "id": "gleam",     "size": [5, 5],   "frames": 2, "use": "edge gleam at the blade tip before the cut" }
  ],
  "basic": { "piece": "cutline_short", "frames": 3, "note": "참격: one short cutline, no split" },
  "nearest": {
    "captain/pitchampion": "arena brute: wide blunt arcs, blood, crowd roar - round/heavy",
    "captain/dragonslayer": "fire + execution X, dash - diagonal/heavy",
    "captain/shadowqueen": "black petals, staccato multi-hits - swarm/stutter"
  }
}
```

- **회전베기를 어떻게 다르게 만드나.** 같은 "회전 베기" 군집에는 pilgrim, saintknight, pitchampion, frostjarl, titan이 있다. 다른 캐릭터들은 원형 스윕이나 고리를 쓴다. 바렌은 **보이는 원을 그리지 않는다.** 정지한 뒤 aoe 반경 18(게임 36px) 안의 적마다 "가르는 선"이 수평으로 한 번에 나타난다. 그리고 2프레임 늦게 `split`이 열린다.
- 축으로 정리하면 이렇다. 적중 발자국은 "적마다 표식"이고 원판(disc)이 아니다. 움직임은 lateral, 박자는 delayed, 화면 박자는 hitstop + x축 흔들림이다.

### 2.3 채운 예시 2: 브리긴다, 철벽의 여단장 (`captain/ironwall`)

데이터 출처: `js/classes.js:276`, `js/content.js:427`.
- 외형 `L('#4a5a6a', '#d9a441', 'helmet', 'mace')`. 강철 회청색, 놋쇠 강조, 투구, 철퇴.
- 스킬 [`방패 밀치기` 근접 cd 1.0 stun 0.2, `철벽 방진` rally def +40% 6초 aoe 45 cd 12].
- 대사: "내 방패 뒤에 선 녀석은 아무도 죽지 않았다."

```json
{
  "owner": "captain/ironwall", "name": "브리긴다", "approved": null,
  "colours": { "key": "#d9a441", "body": "#4a5a6a", "accent": "#f4ead0" },
  "motif": { "family": "fortification", "subform": "tower-shield plates with brass rims that slam down and interlock" },
  "shape": { "geometry": "angular", "motion": "down", "rhythm": "heavy",
             "density": "few", "edge": "hard" },
  "never": ["expanding rings", "spirals", "rising sparkles", "soft glow domes"],
  "verbs": ["내리꽂힌다", "맞물린다", "버틴다", "먼지를 턴다"],
  "cadence": "slow gather (2 frames 120ms), hard snap (1 frame 40ms), long hold on the locked wall",
  "screen": { "allowed": ["shake.y", "hitstop"], "forbidden": ["flash", "grade"], "note": "one heavy vertical thud when plates lock" },
  "cutin": { "enter": "drops from top like a gate", "frame": "riveted plate border", "backdrop": "kit/plate_wall_bg" },
  "pieces": [
    { "id": "plate",      "size": [12, 16], "frames": 1, "use": "single shield plate" },
    { "id": "plate_slam", "size": [16, 24], "frames": 4, "use": "plate falling + impact squash" },
    { "id": "rivet_mote", "size": [3, 3],   "frames": 2, "use": "brass rivet particle" },
    { "id": "dust_decal", "size": [40, 12], "frames": 4, "use": "ground dust at plate feet (ground slot)" },
    { "id": "rim_line",   "size": [24, 3],  "frames": 3, "use": "brass rim flash along a locked plate edge" }
  ],
  "basic": { "piece": "plate_bash", "frames": 3, "note": "방패 밀치기: a plate face pushes forward, rivets pop" },
  "nearest": {
    "hero/fallencommander": "knight banners + sword wall, vertical cloth",
    "captain/runesmith": "rune glyphs stamped on allies",
    "captain/veteran": "shout shock + scar marks"
  }
}
```

- **철벽 방진을 어떻게 다르게 만드나.** 같은 rally 군집에는 7명이 있다. 지금은 모두 주황 또는 파랑의 땅 고리다.
- 브리긴다는 **고리를 쓰지 않는다.** 아군 앞쪽(적 방향)으로 방패판이 세로로 내리꽂힌다. 판은 aoe 45 안의 아군 수만큼 3~6장이다. 판들이 맞물려 "벽"이 되고, 버프 6초 동안 각 아군 발밑에 작은 `plate` 잔상이 남는다(`residue.linger until:buff`). 지금은 버프가 아예 보이지 않는다.
- 축으로 정리하면 이렇다. 발자국은 "벽(wall)", 움직임은 down, 박자는 heavy, 화면 박자는 y축 흔들림 한 번이다.

---

## 3. 스킬 등급과 레이어별로 그리는 것

### 3.1 등급 정의

| 등급 | 쓰는 곳 | 단계 | 화면·컷인 | 새로 그리는 프레임 (추정) |
|---|---|---|---|---|
| **궁극기** (ultimate) | 캐릭터의 대표 기술 1개. 기본안은 "앞으로 생길 세 번째 스킬"(§9 Q2) | 차지 → 발동 → 이동 → 적중 → 잔상 + 화면 + 컷인 | dim/grade/freeze 허용(1×에서만), 키트 컷인 배경 | 18~30 + 컷인 배경 |
| **시그니처 표준** | 캐릭터의 일반 특수기. 지금 있는 특수기 40개가 여기에 든다 | 발동 → (이동) → 적중 → 잔상. 차지는 큐 시트가 있을 때만 | 키트의 화면 박자만. 풀 콤보 금지 | 8~14 (키트 조각 1개 이상 재사용) |
| **시그니처 기본공격** | 캡틴·영웅의 skills[0] | 적중만 | 없음 (큰 치명타 때 hitstop은 범용 값) | 3 |
| **보스 예고** (telegraph) | 보스 특수기 직전 | 예고(바닥 표시·오라 루프) → 적중 → 잔상 | 보스 전용 컷인 변형 | 루프 6~10 + 적중 4~6 |
| **보스 페이즈 전환** | 엔진에 페이즈가 생기면 | 변신 폭발 1회 + 잔상 | dim/grade | 12~20 (외형이 바뀌면 몸 프레임은 별도) |
| **범용 완성 이펙트** | 일반 유닛, 계열별 | 적중 (+이동) | 범용 값 | 계열당 3~6 |

### 3.2 레이어마다 무엇을 그리나

| 단계 / 슬롯 | 궁극기 | 시그니처 표준 | 보스 예고 / 페이즈 | 범용 |
|---|---|---|---|---|
| **차지** (`behind`/`ground`, 시전자) | 키트 모티프가 모이는 그림(그림자 위 무늬, 손끝 문장). 몸에 cast 정지 포즈가 있어야 손에 붙인다 | 큐 시트가 있을 때만 짧은 1~2프레임 | 정확한 aoe 타원 바닥 예고(루프). 보스 몸 오라 | 없음 |
| **발동** (시전자 앞) | 무기 끝 섬광, 문장 펼침 | 키트 조각 재사용 | 포효나 몸짓 이펙트 | 없음 |
| **이동** (`front`, 발사체) | 스킬 전용 발사체 시트(지금은 shot 종류별 공용 광구) | 키트 궤적 타일 + 스킬 전용 머리 | 브레스 등 보스 전용 | 계열 발사체 (화살·광구) |
| **적중** (`sorted`/`front`, 피격자) | 새 "결정 프레임" 시트. 적중 칸이 피해 틱에 맞는다 | 새 적중 시트 1개 이상 | 보스 전용 적중 | 3~6프레임 + 코드 불꽃 |
| **잔상** (`ground`/`over`) | 데칼, 불씨, 상태 표시(기절·둔화·버프) | 데칼 또는 상태 표시 1개 | 대형 데칼 | 없음, 또는 짧은 먼지 |
| **화면** (`screen`) | 키트 화면 박자 + 궁극기 조합 | 키트 화면 박자 | 보스 화면 박자 | 범용 shake/stop 값 |
| **컷인** (DOM) | 키트 배경, 프리즈 선택 | 전투당 첫 사용 때만 (§9 Q3) | 보스 컷인 변형 | 없음 |

### 3.3 크기 예산 (640×360 기준, 몸 높이 ~64px)

- 범용 적중: 16~32px
- 시그니처 적중: 32~72px
- 궁극기: ~160×96px까지, 여기에 화면 레이어
- 예고: 정확한 aoe 타원. 반경은 `aoe × Z(2)` px이므로 aoe 24는 반경 48px다.
- 궁극기 화면 레이어를 빼면, 피격자 머리 위로 몸 높이 하나를 넘기지 않는다. 아군 캡틴 몸 위에서는 `capDim`을 유지한다.
- 팔레트: 스킬당 12색 이하, 모두 키트 램프 안에서 고른다.

---

## 4. 뼈대 프리셋 라이브러리와 데이터 형식

### 4.1 등록 형식

```js
// js/fx/skel.js  (색 없음, 이미지 id 없음)
FxSkel.def('path.skyDrop', {
  kind: 'path',
  params: {
    h:     { type: 'num', min: 40, max: 240, def: 120, tag: 'style' },
    slant: { type: 'num', min: -0.6, max: 0.6, def: 0.19, tag: 'style' },  // 3/16
    grav:  { type: 'num', def: 0, tag: 'physics' } },
  fn: (p, k, rng) => ({ x: p.x1 - p.slant * p.h * (1 - k), y: p.y1 - p.h * (1 - k), ang: Math.atan2(1, -p.slant) }),
});
```

- 모든 함수는 순수하다. 난수는 인스턴스 rng에서만 얻는다.
- 숫자 매개변수는 세 가지 형태로 받는다: 값, `[min,max]`(인스턴스 rng로 뽑음), 인라인 `track: [[k,v],…]`.
- 결과는 언제든 `"custom": "<owner>/<name>"`(`js/fx/custom/<owner>.js`)으로 바꿀 수 있다. custom도 구조만 돌려준다. 이것은 툴박스이지 틀이 아니다.
- `def` 값은 **범용 스펙에만** 적용된다. 시그니처는 `tag:'style'`인 값을 전부 직접 적어야 한다(§1.2-4).

### 4.2 프리셋 목록 (지금 코드에서 뽑은 기본값)

| 묶음 | 프리셋 | 주요 매개변수 (기본값) | 지금 코드의 출처 | 등급 |
|---|---|---|---|---|
| 곡선 | `curve.linear`, `curve.easeIn/Out`(p 2), `curve.attackDecay`(rise 0.2), `curve.grow`(until 0.25), `curve.expand`(from 0.2, to 1.2), `curve.pulse`(n, depth), `curve.anticipate`(back 0.15, overshoot 0.1), `curve.bezier` | 괄호 안 | 기둥·시길 L2222/L2304, xslash, burst/quake | 보이지 않음 |
| 프레임 시계 | `clock.stepped`(ms 60), `clock.sheet`(시트의 ms[]), `clock.hold`(frames, holdLast) | ms는 style | 베기·찌르기·타격·burst의 단계 진행 | 보이는 구조 |
| 타임라인 | `tl.strike`, `tl.windupStrike`(charge 0.45), `tl.castTravel`, `tl.volley`, `tl.etaDrop`(dropDur 0.32), `tl.chain`, `tl.dash`, `tl.aura`, `tl.channel`(n), `tl.telegraph`(lead), `tl.phaseBurst` | charge, lead, dropDur는 style | meteor의 진행 재매핑, 볼트, 대시 | 보이는 구조 |
| 경로 | `path.line`, `path.arc`(height 24), `path.chain`, `path.zigzag`(seg 7, jitter 8, rejitterMs 40), `path.skyDrop`(h 120, slant 3/16), `path.shotRemap`(dx +60, dy −200), `path.orbit`(r, squash 0.42, turns), `path.spiralIn`(shrink 0.6), `path.returnArc`(hump 20), `path.cone`(half 0.35, speed 160~320) | squash는 physics, 나머지는 style | streak, bolt L2197, fall L2190, meteor L2483, whirl L2154, swirl L2212, mote L2237, breath L2094 | 보이는 구조 |
| 배치 | `place.perTarget`, `place.scatter`(r 10), `place.stagger`(dt 0.05), `place.alongPath`(n 5), `place.ringGround`(n 7, squash 0.4), `place.radial`(n, jitter) | n, r은 style | 기둥, fall, 잔상 5개, quake 균열 | stagger는 보이지 않음, 나머지는 보이는 구조 |
| 방출기 | `emit.radial`(drag 0.92), `emit.fan`(grav 320, bounce 1), `emit.rise`(spread 0.5), `emit.cone`, `emit.groundPuff`, `emit.drift`, `emit.spiralIn`, `emit.riseFromGround`, `emit.condenseLine`, `emit.flickerIn` | grav/drag/bounce는 physics, n/spread는 style | `spawn` L1956, `hitSpark` L196, `downPuff` L206, AMBIENT | 혼합 |
| 잔상 | `residue.decal`(hold 1.2, fade 0.4), `residue.embers`(rate, life, area), `residue.linger`(follow, until: stun/slow/buff), `residue.dissolve`(steps) | hold는 style | 새로 만듦 (quake 균열을 이쪽으로 옮김) | linger는 보이지 않음 |
| 화면 | `screen.shake`(amp 3/5/6, decay 30, axis), `screen.hitstop`(dur 0.05/0.09/0.08, scope), `screen.flash`(peak 0.12~0.15, decay 1, terrainClamp 0.18/0.08), `screen.dim`(alpha, in, hold, out), `screen.grade`(mode), `screen.cutin`(in 0.18, hold 0.75, dur 1.15, freeze, queue) | 전부 style | shake/stop/flash, `play` L2855 + `css/style.css:637-649` | 보이는 구조 |
| 앵커 | `anchor.resolve(u, 'feet/chest/head/hand/tip/ground')` | 시트의 `points`/`anchors`. 없으면 `stature()`로 추정(chest = foot − 0.5h, head = foot − 0.9h) | `LIFT=10` 등 리터럴 약 28개를 대체 | 보이지 않음 |

### 4.3 스펙 JSON 예시: 실제 스킬 바렌 `회전베기`

```json
{
  "id": "sig/captain/blademaster/hoejeon-begi",
  "tier": "ultimate-pilot",
  "bind": { "owner": "captain/blademaster", "skill": "회전베기" },
  "kit": "captain/blademaster",
  "keyImage": "art/requests/fx/captain/blademaster/s1/key_approved.png",
  "timeline": { "preset": "tl.windupStrike", "charge": 0.30, "residue": 0.9, "chargeSource": "cue" },
  "layers": [
    { "id": "gleam", "phase": "charge", "per": "cast",
      "src": { "sheet": "fx/sig/captain/blademaster/gleam", "anim": "loop" },
      "anchor": "self.tip", "slot": "front", "blend": "lighter",
      "clock": { "preset": "clock.hold", "frames": [0, 1], "ms": [160, 120] }, "core": true },
    { "id": "cut", "phase": "impact", "per": "victim",
      "src": { "sheet": "fx/sig/captain/blademaster/cutline", "anim": "once" },
      "anchor": "victim.chest", "facing": "attacker", "slot": "sorted", "zBias": 2, "blend": "source-over",
      "sync": { "frame": "hit", "preroll": "compress" },
      "place": { "preset": "place.stagger", "dt": 0.0 }, "jitter": { "ang": [-0.12, 0.12], "mirror": true }, "core": true },
    { "id": "split", "phase": "impact", "per": "victim", "delay": 0.11,
      "src": { "sheet": "fx/sig/captain/blademaster/split", "anim": "once" },
      "anchor": "victim.chest", "slot": "over", "blend": "source-over",
      "clock": { "preset": "clock.stepped", "ms": 70 }, "core": true },
    { "id": "cloth", "phase": "residue", "per": "victim",
      "emitter": { "preset": "emit.fan", "n": 3, "dir": "attacker", "spread": 0.9, "sp": [30, 60], "life": [0.5, 0.8], "grav": 120, "bounce": 0 },
      "particle": { "sheet": "fx/sig/captain/blademaster/band_tail", "anim": "flutter" }, "slot": "front" }
  ],
  "screen": [
    { "at": "impact", "preset": "screen.hitstop", "dur": 0.10, "scope": "units+fx" },
    { "at": "impact+0.11", "preset": "screen.shake", "amp": 3, "decay": 40, "axis": "x" }
  ],
  "cutin": { "when": "firstUsePerBattle", "enter": "slit", "backdrop": "fx/sig/captain/blademaster/band_tail" },
  "axes": { "footprint": "per-victim-mark", "motion": "lateral", "beat": "1 accent, late echo +0.11",
            "cadence": "slow-then-snap", "screen": ["hitstop", "shake.x"], "density": "one" },
  "budget": { "priority": "signature", "phone": { "drop": ["cloth"], "residueK": 0.5 } }
}
```

- `core:true`가 붙은 레이어는 폰 LOD에서도 절대 빼지 않는다. 폰 화면에서 정체성이 사라지면 안 되기 때문이다.
- `axes`는 작가가 직접 적고 검사기가 다시 계산해서 대조한다(§5.3).
- 범용 스펙은 같은 형식에 `tier:"generic"`, `family`, `tint:"faction"`, `variants`(big/special)를 쓴다. 범용 바인딩은 `assets/fx/generic/_rules.json`의 순서 규칙(처음 맞는 것 적용)이 정하고, 지금의 `recipe()` 플래그 사다리(L2039)를 대체한다.

### 4.4 레이어 필드 요약

| 필드 | 값 |
|---|---|
| `phase` | `charge`, `release`, `travel`, `impact`, `residue` |
| `per` | `cast`, `target`, `primary`, `victim`, `shot` |
| `src` / `emitter`+`particle` / `place` / `code` | 시트와 anim. `code` 렌더러는 종류 B에서만 쓰고, 시그니처에서는 §9 Q1 결정에 따른다 |
| `anchor` | `self.*`, `target.*`, `victim.*`, `between`, `screen.*` × `feet/chest/head/hand/tip/ground` |
| `slot` | `ground`, `behind`, `sorted`, `over`, `front`, `screen`, `ui` |
| `blend` | `source-over`, `lighter`, `screen`, `multiply` (`screen`/`multiply`는 폰 실측 후 허용) |
| `clock` | `anim`(기본), `sim`, `real`. `freeze` 기본값 true |
| `sync` | `frame:'hit'`, `preroll: lookahead / skip / compress` |
| `tint` | `faction`(종류 B 전용) 또는 없음 |
| `core` | 폰 LOD에서도 유지 |

---

## 5. 판에 박힘 방지 규칙과 검토 체크리스트

### 5.1 원칙

1. **색은 구별의 근거가 아니다.** 모든 구별·정체성 검사는 **흑백 모드**와 **블롭 모드**로 한다. 블롭 모드는 레이어 알파 마스크를 회색으로 칠하고 모티프 스프라이트를 bbox로 바꾼 화면이다. 컬러는 마지막에 주인이 보는 용도로만 쓴다.
2. **같은 메커니즘이 같은 리듬을 뜻하지 않게 한다.** 시뮬레이션 타이밍이 같은 군집(rally 7, 내려찍기 8, 대시 6, 낙하 5, 광역 치유 4, 화살 3, 볼트 3, 단검 3)은 군집 안에서 구조가 서로 달라야 한다.
3. **그림이 먼저, 구조는 나중.** §1.2-5.
4. **같은 기술의 반복도 판에 박힘이다.** 인스턴스마다 시드로 변주를 준다(좌우 반전, 배치 흔들림, 자주 쓰는 스킬은 대체 적중 프레임 2장).

### 5.2 로스터 전체 모티프 배정 (키트 그리기 전에 한 번)

- 47명(캡틴 33, 영웅 7, 보스 7)을 **표 하나**에 놓고 모티프 계열과 하위 형태를 먼저 배정한다. 개별 키트는 그다음이다. 하나씩 만들면 먼저 만든 키트가 뻔한 모티프를 다 가져가고, 나중 키트는 같은 테마로 몰린다.
- **닫힌 모티프 계열**과 계열별 상한: binding, holy-light, shadow, fire, frost, earth, nature/wind, arcane/rune/star, naval, sound, blood, beast, fortification, blade, poison/plague.
- 이미 알려진 충돌은 표에서 먼저 정리한다.
  - 서리 영주(frostjarl) vs 서리 거인 왕: 같은 원소, 같은 메커니즘이라 가장 어려운 쌍이다.
  - 해방 검투사(liberator)의 부서진 사슬 vs 해적왕(pirateking)의 갈고리 사슬.
  - 성직자 7명(fieldmedic, pilgrim, saintknight, inquisitorlord, demonhunter, lightbearer, exsaint)이 신성광 계열에 몰려 있다. 하위 형태를 기둥·파편·후광고리·종·경전·불꽃·새벽선으로 나눈다.
  - 그림자 계열 로그 4명(fixer, shadowlord, shadowqueen, outlaw)과 그 근처의 hexer.
  - 불 계열: inquisitorlord, Ignis, dragonslayer, towerheir, 포격 3인방.
  - 해양 계열: admiral, corsair, pirateking.
  - 대지 계열: titan vs 모래 폭군·고블린 왕.
  - 자연 궁수 5명.
  - rally에서 원형 고리 모티프 3개(veteran, bard, fallencommander)가 겹치는 문제.
- 하위 형태가 같으면 안 된다. "사슬"과 "족쇄"처럼 단어만 다르고 계열이 같은 경우도 충돌로 본다.

### 5.3 구조 구별 규칙 (`tools/fx/check.js`)

시그니처마다 7개 축을 잰다. 값은 정확한 수치가 아니라 **양자화된 구간(bucket)**으로 비교한다.

| # | 축 | 구간 예 |
|---|---|---|
| 1 | 적중 발자국 | point, line, column, wall, ring, disc, cone, arc, grid, scatter, per-victim mark |
| 2 | 주된 움직임 방향 | down, up, inward, outward, lateral, orbit, hop, static |
| 3 | 박자 지도 | 강세 수, 간격 패턴, 예비동작 구간, 잔상 구간 |
| 4 | 프레임 박자 | even, stutter, slow, on-twos, mixed |
| 5 | 화면 박자 | 사용 조합과 강도 구간 |
| 6 | 밀도와 크기 | one / few / swarm × 크기 구간 |
| 7 | 흑백 모티프 실루엣 | 블롭·흑백 비교 |

규칙:
- **같은 군집 안에서는** 축 1~6 중 **3개 이상**, 그리고 축 7이 달라야 한다.
- **로스터 전체에서** 축 1~5가 모두 같은 두 주인이 있으면 안 된다.
- **한 캐릭터의 스킬끼리는** (모티프와 색은 일부러 공유하므로) 축 1~4 중 2개 이상이 달라야 하고, 새 스킬마다 새 결정 프레임 조각을 하나 이상 가져와야 한다.
- 구간이 달라졌다고 인정하는 최소 차이: 진입 각도 20° 이상, 지속시간 30% 이상 또는 2프레임 이상, 개수 ±2 이상.
- 정확히 같은 (발자국, 움직임, 박자 지도) 조합은 로스터 전체에서 최대 2명까지만 허용하고, 같은 군집 안에서는 금지한다.
- 예외(`sharedSkeletonOk`)는 `assets/fx/approvals.json`에 **주인 승인**이 기록되어 있을 때만 통과한다.

### 5.4 기술 검사 (`tools/fx/check_fx.py`, 등록 전)

- 게임 픽셀 1:1 격자. 알파는 0/255에 선택적 50% 단계만 허용한다.
- 팔레트는 키트 램프의 부분집합이어야 한다. 크기 예산, 프레임 수, ms가 브리프와 일치해야 한다.
- 가이드 픽셀이 남아 있으면 안 된다. 슬롯 레이어 이름이 맞아야 한다.
- **마스크 재사용 거부.** 다른 주인과 범용의 모든 FX 프레임과 비교한다. 하단 중앙을 맞추고 ±8px 범위를 탐색하며 좌우 반전도 포함한다. IoU > 0.85면 거부한다. 면적이 작은 조각(예: 6×6 이하 입자, 직선 빔)은 면제하고, 대신 블롭 모드의 구성 비교와 짝지어 판단한다.

### 5.5 검토 체크리스트 (스킬마다)

| # | 질문 | 누가 / 어떻게 |
|---|---|---|
| 1 | 컬러 없이(흑백) 봐도 이 캐릭터의 기술로 읽히는가? | GPT-QA. 같은 군집 쌍을 흑백·블롭으로 놓고 "같다 / 다르다?"를 쌍마다 묻는다. 모두 "다르다"여야 통과 |
| 2 | 같은 군집의 가장 가까운 3개와 나란히 놓아도 헷갈리지 않는가? | 미리보기 페이지의 군집 행렬 |
| 3 | 0.3초 안에 읽기 테스트를 통과하는가? (브리프의 한 줄) | Antigravity 판정 + 주인 |
| 4 | 적중 칸이 피해 숫자와 같은 틱에 나오는가? | 타임라인 바에 빨간 표시가 없어야 함. 미끼 프레임 테스트(`gate_page.py` 방식) |
| 5 | 키트 조각을 재사용하고, 새 결정 프레임이 있는가? | check.js |
| 6 | style 매개변수를 전부 직접 적었는가? 기본값이 남아 있지 않은가? | check.js |
| 7 | 화면 박자가 키트 어휘 안에 있는가? 풀 콤보는 궁극기만 쓰는가? | check.js |
| 8 | 같은 스킬을 5번 연속 써도 똑같아 보이지 않는가? | 미리보기 "반복 실행" |
| 9 | 폰 등급에서도 `core` 레이어가 남아 정체성이 보이는가? | 미리보기 폰 토글 + 같은 구별 검사 |
| 10 | 실전 밀도(10초 안에 특수기 8~10개, 1×와 4×)에서 화면 연출과 컷인이 지겹지 않은가? | 미리보기 "밀도 실행" |
| 11 | 재채색, 남의 에셋, NovelAI 최종본이 아닌가? | check_fx.py 마스크 검사, 출처 기록 |
| 12 | 해시가 그대로인가? | §6.2 회귀 명령 |

---

## 6. 엔진 작업 (기술 상세는 영어 혼용)

### 6.1 파일과 함수

| 파일 | 역할 |
|---|---|
| `js/fx/skel.js` → `FxSkel` | Class A preset registry + param schema (`tag: physics/style`). Colourless (lint). |
| `js/fx/pal.js` → `FxPal` | `rampOf`, `mixHex` moved out of battle.js; faction tint map + cache (`tintCache` pattern). |
| `js/fx/player.js` → `FxPlayer` | Instances, clocks, slots, sheet playback (`frameAt` semantics, once/loop/pingpong/holdLast, integer scale), seeded rng, budget/LOD, event sync, screen arbitration, cut-in queue. |
| `js/fx/legacy.js` → `FxLegacy` | Today's `recipe()` L2039-2110, `drawVfx` L2139-2245, `drawSmear/Thrust/Smash/Burst`, `hitSpark`, moved unchanged. Placeholders in neither tier, labelled `legacy.*`. |
| `js/fx/custom/<owner>.js` | Optional bespoke structure functions (still colourless). |
| `assets/fx/kits/*.json`, `assets/fx/sig/**.json`, `assets/fx/generic/*.json`, `assets/fx/approvals.json` | Data. Fetched at boot like the manifest. |
| `tools/fx/check.js` (node) | Schema, separation, binding (loads `classes.js`/`content.js` in a vm like `tools/sim/bot.js`), style-default ban, 7-axis distinctness, colour-literal lint on skel.js. |
| `tools/fx/check_fx.py` | Pixel checks + mask-reuse refusal (§5.4). |
| `tools/art/register_fx.py` | Writes `fx/...` entries into `assets/art/manifest.json` (same `sheet` shape `Art.sheet` parses, `js/art.js:67-96`, plus an `fx` block: owner, tier, `hit` cell, blend, `lazy`, tint key or null). |
| `tools/art/receive.py` | New route `fx/<owner>/…` → `check_fx.py`; `sheets.py` refuses `art/inbox/fx/`. |
| `tools/fx/guide.py` | Effect guide renderer (§7.3). |
| `fxlab.html` + `js/fx/lab.js`; `tools/fx/gallery_page.py` | Preview page (§6.7). |
| `index.html` | Load `pal.js`, `skel.js`, `legacy.js`, `player.js` before `battle.js`. battle.js guards with `typeof FxPlayer !== 'undefined'` so headless `tools/sim/*` (battle.js only) keep working. |

Changes inside `js/battle.js`:
- **`useSkill` (L901):** `const cid = ++st.castSeq;` adds `cid`, `own: ownerOf(u)`, `skn: sk.name`, `si` (skill index) and `uid` to the `label`/`cast`/`skill` pushes. Shots get `cid` and `ti`.
- **`strike`/`mend`** get an optional `cid` arg. Shot arrival (L1146-1147) passes `s.cid`. `hit`/`boom`/`heal`/`ring`/`drain` gain `cid`, `kill`, `crit`, `stun`, `slow`.
- **`ownerOf(u)`:** `hero/<heroKey>`, else `captain/<capKey>`, else `boss/<slug(u.mon)>` when `u.boss`, else null. Rival enemy captains with a real `capKey` resolve too (§9 default).
- **`ingest` (L1966):** if a `cid` is owned by a spec, skip the generic smear, boom and sigil (`view.fxSuppress`). Owner units never fall through to Class B regardless.
- **`draw` (L2295):** slot insertion points.
  - `ground` after `drawImage(view.bg)`, before sigils.
  - `behind` per unit before shadow/aura.
  - `sorted` proxies `{y: footY+zBias}` merged after the captain reorder (L2330).
  - `over` after sprite/rim/hit flash.
  - `front` = today's `drawVfx` position.
  - `screen` after vignette, before the flash.
  - `ui` after labels.
- **`Art.load`** skips `fx.lazy` entries. `Art.want(ids)` loads and `img.decode()`s before the RAF loop starts (`FxPlayer.assetsFor(st.units)`), never mid-fight. Missing sheet → legacy for that layer, never throws.

### 6.2 표시 전용·결정론 보장

- **Simulation untouched.** No new `st.r()` call. `st.castSeq` and all event fields are write-only from the sim's point of view. `record()` (L1241) hashes only `alive/fled/routed/hp/downAt/dealt/taken/kills/healed`.
- **`tablesDigest()` (L1221) untouched.** Nothing visual goes into `GENERIC_SPECIAL`, `CLASS_SKILLS`, `monsterSkills()` or captain/hero `acts` (frozen into `report.battle.spec`). All mappings live in `assets/fx/*` keyed by owner + skill name.
- **Renderer randomness.** `FxPlayer.rng(cid, ti, salt)` = mulberry32(fnv(cid, ti, salt, battle seed)).
  - Port the `Math.random` uses (L1955, 2071, 2096, 2114, 2229, 2421, 2508) step by step. This stops the drift in the management RNG that seeded QA sees (`docs/agents/reports/gpt-qa.md:1323`).
  - Emission is time-based, not "50% per frame".
  - Bolt re-jitter is keyed to a quantised clock, so GIFs reproduce at any frame rate.
- **Regression gate** after each engine step (M0, M2, M6) and at every G4:
  - `node tools/sim/battle.js 100`, `node tools/sim/shadow.js`, `node tools/sim/bot.js`: md5 unchanged.
  - `Battle.run(spec)` hash over stored specs, before and after.
- **Charge timing uses a cue sheet, not a cooldown prediction.**
  - Why: a special with `left <= 0` waits for `pickTarget` (L1003-1006), and cooldowns tick during stun (L989 vs L1000). So "cooldown ready" does not mean "fires now".
  - `play` already re-runs the battle headlessly to verify the hash (L2781-2788). `run()` gets an optional, unhashed, in-memory cue list `{tick, uid, si, targets}`.
  - The cues are kept with `Game.judgedHere` for battles judged this session.
  - Dev assertion: each display release must match its cue. On a mismatch, charge is disabled and a log line is written. This doubles as a tripwire for any renderer code that touches sim state.
  - No cue (legacy `plan` + `findBattle` path, L2791-2796) means no charge, and `preroll` falls back to `skip`/`compress`.
- **Clocks.** Start and stop are anchored in sim time (`view.simT = st.t + acc`). Frames play on `view.clock` (anim), so they freeze during hit-stop and are capped at 2.6×. Screen flash, UI and cut-in run on real time. This fixes FX moving while units are frozen and FX piling up at 4×.
- **Impact sync.** Each FX sheet declares its hit cell (`fx.hit`). The player starts the layer so the hit cell lands on the impact event.
  - Ranged impacts fire on **shot arrival**, not at cast. This fixes the bolt chain, curse swirl and breath firing early.
  - `tl.etaDrop` generalises the meteor trick (start the fall at ETA − dropDur).
  - When a spec owns the cast, `s.meteor` is ignored. This fixes the Ignis meteor-plus-breath double.
- **Pacing / arbitration.**
  - One screen-layer owner at a time, by priority. Hit-stop takes the max of overlapping requests, never the sum.
  - dim/freeze only at 1×; holds scale with `1/min(speed,2)`.
  - Cut-in: a queue with a 1.3s gap; entries more than 1.5s stale are dropped. Synced to `view.clock`. Enemy boss variant.

### 6.3 성능 (폰)

- **Budget priority:** own signature > enemy boss signature > generic special > generic basic > ambient.
- **Per-slot caps.** Today `vfx`, slashes, sigils and flares are uncapped.
- **Phone tier.** Detected from `hardwareConcurrency`/width, then confirmed by a 2s moving average of frame time > 20ms. On phone tier: apply `budget.phone`, never drop `core` layers, halve particles.
- **Cheaper drawing.**
  - Pre-rendered sheets via `drawImage` replace fillRect loops (a big smear or boom is ~370–400 rects per frame).
  - Particles are batched by blend mode, which fixes the per-particle composite switch at L2546.
  - Pillar gradients are cached.
- **Measure first.** Full-screen `multiply`/`screen` composites are measured on a real phone before `screen.grade` is allowed.
- **Dev overlay.** drawImage/fillRect counts and ms per frame.

### 6.4 미리보기 페이지 (`fxlab.html`)

- **무대.** 640×360 픽셀 캔버스, 1/2/3배 확대. 지형 배경은 `Battle.labStage(terrain)`으로 띄운다. 공격자와 표적은 진짜 캐릭터 시트를 쓴다(`Art.sheetFor`). 폰 폭 토글이 있다.
- **조작.**
  - 등급, 주인, 계열, 스킬로 찾아보기.
  - 재생과 반복, 속도 0.25/1/2/4×, 한 프레임씩 넘기기, 시드 입력.
  - 세력 틴트(범용만), 좌우 반전, 표적 수 1~6, 거리 슬라이더(ETA 동기화 확인용).
- **뼈대 보기.** 경로·배치·앵커 오버레이. 단계 타임라인 바에 피해 틱과 레이어별 적중 칸을 표시하고, 어긋나면 빨간색. 레이어별 켜기·끄기.
- **판에 박힘 점검.**
  - 군집 행렬: 컬러, 흑백, 블롭 3가지 보기.
  - "무작위 6": 주인이 비슷해 보이는 쌍을 표시한다.
  - 밀도 실행, 반복 실행, 폰 버전 나란히 보기.
  - 7축 유사도 행렬.
  - 진행 현황표: 47명 × 스킬마다 없음 / 임시(legacy) / 초안 / 승인. 임시 상태는 "판에 박힘 부채"로 센다.
- **승인.** 스펙마다 승인 / 수정 + 메모를 남기면 JSON으로 내보낸다. 클라우드가 이를 `assets/fx/approvals.json`에 기록한다.
  - 참조한 시트의 해시가 바뀌면 그 스펙은 `pending`으로 돌아간다.
  - 게임은 승인된 시그니처만 재생하고, `?fxdev=1`이면 초안도 재생한다.
  - 폰 검토용으로는 `tools/fx/gallery_page.py`가 시트, 스펙, 플레이어를 한 파일로 묶는다(`gate_page.py` 방식).

### 6.5 단계별 엔진 마일스톤

- **M0 배관.** 이벤트 신원 필드, `castSeq`, FX rng, 큐 시트. 보이는 변화는 없고, 해시 회귀 검사를 한다.
- **M1 추출.** `skel.js`, `FxLegacy`, 지금 레시피를 legacy 스펙과 `_rules.json`으로 옮긴다. 고정 시드 GIF로 화면이 똑같은지 비교한다. 레거시 세트를 띄운 `fxlab.html`도 이 단계에서 만든다.
- **M2 플레이어.** 시계, 슬롯(quake 균열을 `ground`로), 도착 기준 적중, `tl.etaDrop`/`tl.chain`, Ignis 중복 수정, 상한.
- **M3 시트.** manifest `fx` 항목, `Art.want`, `register_fx.py`, `receive.py fx/`, 적중 칸 동기화.
- **M6 차지·잔상·화면.** 큐 기반 차지, `residue.linger`(기절, 둔화, 버프 표시), `screen.dim`, 컷인 큐.
- **M7 성능.** 폰 등급, 합성 모드 묶기, 그림이 들어온 자리부터 fillRect 경로 퇴역.

### 6.6 시그니처가 생기기 전의 임시 표시

- 지금의 공용 레시피를 그대로 두면 "rally 7명이 같다", "보스 5명이 같은 대지 분쇄" 같은 모습이 굳어진다.
- 그래서 소유자 유닛의 특수기는 **중립 최소 표시**로 줄인다: 범용 적중 + 짧은 시전 표시. 회전 베기 고리나 운석처럼 개성인 척하는 공용 연출은 빼고, 시그니처가 들어오면 교체한다.
- 화면이 일시적으로 수수해지므로 기본안으로 제안하고, 주인이 반대하면 되돌린다.

---

## 7. 제작 파이프라인, 에이전트, 승인 관문

### 7.1 역할

| 역할 | 하는 일 |
|---|---|
| 주인 | 모티프 배정표, 키트, 궁극기 키 이미지, 궁극기·보스 최종 승인. 범용 계열 키 이미지는 묶음으로 한 번에 승인 |
| 클라우드 (이 세션) | 브리프·가이드 생성, 검사, 등록, 엔진, 미리보기, `dot_queue.md` 상태 관리 |
| Antigravity | 모든 그림. 키 이미지, 픽셀 키 프레임, 애니메이션, aseprite-mcp 손질. `art-inbox`의 `art/inbox/fx/…`에만 쓴다 |
| GPT-QA (Codex) | 흑백·블롭 쌍 비교, 해시 회귀, 타이밍 검사, 버그 |
| NovelAI | 주인이 요청할 때만 디자인 초안. `art/concepts/<owner>/fx_drafts/`(git 무시)에 둔다. 최종본으로 등록할 수 없다 |

### 7.2 흐름과 관문

| 단계 | 담당 | 산출물 | 관문 |
|---|---|---|---|
| F0 모티프 배정표 | 클라우드 초안 | `art/requests/fx/_roster.md` (47명 × 계열·하위 형태·형태 어휘·이웃) | **G0 주인**: 한 번에 승인 |
| F1 키트 브리프 | 클라우드 | `art/requests/fx/<owner>/kit.md` + `kit.json` 초안 | 없음 |
| F2 키트 키 이미지 | Antigravity (또는 주인 요청 NovelAI 초안) | `art/inbox/fx/<owner>/kit_key.png` (참고용, 출시 안 함) | **G1 주인**: 키트 승인 (`kit.json approved`). 이웃 3개 키트와 나란히 놓고 본다(`tools/fx/kit_page.py`) |
| F3 키트 조각 | Antigravity | `art/inbox/fx/<owner>/kit/<piece>.aseprite` + png, 게임 픽셀 1:1 | G2 기술 검사 |
| F4 스킬 브리프 | 클라우드 | `art/requests/fx/<owner>/s<n>/README.md` + `brief.json` (§7.4) | 없음 |
| F5 스킬 키 이미지 | Antigravity | 적중 순간의 "결정 프레임" 1장 | **G3**: 궁극기·보스 페이즈는 주인, 표준은 Antigravity 판정 + GPT-QA 흑백 쌍 비교 |
| F6 픽셀 키 프레임 → 애니메이션 | Antigravity | `s<n>.aseprite` (슬롯 이름 레이어, `hit` 태그) + png 스트립 | G2 + **G4 애니메이션**: `art/inbox/NOTES.md`에 `## 판정 — fx/<owner>/s<n>`, 1×/4× 단독 확인, GPT-QA 쌍 비교, 적중 프레임 미끼 테스트 |
| F7 뼈대 구성과 통합 | 클라우드 | 스펙 JSON (그림에 맞춰 뼈대를 고르거나 custom), `register_fx.py` | **G5 엔진**: 고정 시드 GIF 1×/4×, 지형 세 가지(어두움, 모래, 눈), 해시 불변, 성능 예산, 군집 행렬 |
| F8 최종 승인 | 주인 | 미리보기 링크 | **G6 주인**: 궁극기와 보스 페이즈만. 표준은 G5 통과로 승인 |

`dot_queue.md` 상태 흐름: `FX_READY → DELIVERED → HEAD_REVIEW → XCHECK → ACCEPTED`. 주인 대기 항목은 「주인에게 물을 것」에 올린다.

### 7.3 이펙트 가이드 (`tools/fx/guide.py`)

- **넣는 것: 게임플레이 제약만.**
  - 바닥선, 원근 타원(0.4).
  - 몸 높이 자.
  - 시전자 cast 포즈. `tools/mannequin3d/motions.py`에 `cast_keys`(raise / thrust_focus / slam / draw_loose / channel / throw)를 추가해 얻는다.
  - 표적 더미를 실제 거리에 둔다: 근접 22px, 원거리 ~180px.
  - aoe 발자국.
  - 앵커 점(hand, tip, chest, head, ground).
  - 시뮬레이션 이벤트 표시(cast, release, arrive/hit)와 크기 예산 상자.
- **넣지 않는 것:** 프리셋 경로, 슬롯 타이밍 상자, `skeleton_affinity`. 그려 주면 따라 그리게 된다.
- **형식.**
  - 1×와 ×4 nearest 두 가지.
  - `.aseprite`에 잠긴 `guide` 레이어 + 빈 슬롯 레이어.
  - `check_fx.py`가 가이드 픽셀이 남은 납품을 거부한다(관절 레이어 거부와 같은 방식).
- **그리는 해상도.** 이펙트는 몸 시트처럼 1536px로 그려 축소하지 **않는다.** 1px 선과 단계 섬광은 축소하면 망가진다. 게임 픽셀 1:1로 그리고 ×4로 확대해서 작업한다.

### 7.4 스킬 브리프 템플릿 (`brief.json` + README)

```markdown
# fx/<owner>/s<n> — <스킬 이름>   (등급: ultimate | signature | basic | telegraph | phase)

## 데이터 (자동)
shot / aoe / hits / stun / dash / exec / drain / buff / range / cd, 메커니즘 군집, 같은 군집 멤버

## 판타지 (한 줄)
## 0.3초 읽기 테스트
예: "아군 앞에 벽이 선다"

## 키트
색 3, 모티프 하위 형태, 형태 어휘, 금지 형태, 재사용할 키트 조각 id

## 이웃과 다른 점 (G3 이후 채움)
같은 군집의 가장 가까운 2개와, 축 1~6 중 다른 3개를 쓴다. 색은 축이 아니다.

## 스토리보드 (한 줄 = 한 레이어)
| 단계 | 슬롯 | 조각 (키트 id / 새로) | 프레임 | ms | 크기 px | 앵커 | 블렌드 | 키트 색 이름 | 동기 | core |

## 화면 박자 (키트 어휘 안에서)
## 컷인 (첫 사용 / 매번 / 없음)
## 예산
동시 인스턴스, 새 프레임 수, 폰에서 버릴 레이어 순서(잔상 → 차지 → 방출기). core는 버리지 않는다.

## 납품
art/inbox/fx/<owner>/s<n>.aseprite (+ png)
자체 검사: python3 tools/fx/check_fx.py art/inbox/fx/<owner>/s<n>.aseprite --brief brief.json
NOTES.md에 `CHECK: RESULT PASS` 줄을 붙인다.
```

---

## 8. 단계별 계획과 대략적 비용

비용 기준은 `docs/plans/2026-11-28_art_rethink.md`의 실측이다. 몸 시트 1장을 승인받는 데 클라우드 토큰 약 0.23M, 납품 1.6회가 들었다.
Antigravity의 처리 속도는 아직 **측정한 적이 없다.** 아래 숫자는 추정이고, 1~2단계에서 실측해서 고친다.
`2026-11-28_art_rethink.md`의 미술 보류가 풀리기 전에는 엔진 M0~M2와 문서·도구 작업만 진행한다.

| 단계 | 내용 | 그리는 프레임 (추정) | 클라우드 토큰 (추정) | 주인이 볼 것 |
|---|---|---|---|---|
| **0. 기반** | 엔진 M0~M2, `skel.js`(지금 코드에서 뽑은 프리셋), `check.js`/`check_fx.py`/`register_fx.py`, `fxlab.html` 레거시 세트, 모티프 배정표 초안 | 0 | 1.5~3M | G0 모티프 배정표 |
| **1. 범용 파일럿 '베기'** | 베기 계열 하나. 키 이미지 → 주인 승인 → 픽셀 키 프레임 → 3~6프레임(일반·큰 변형) + 코드 불꽃(`emit.fan`). 일반 유닛의 `legacy.smear`만 대체한다. 이 과정에서 `clock.stepped`, `emit.fan`, `screen.shake/hitstop`의 범용 기본값을 확정한다 | 4~8 | 0.1~0.2M | 키 이미지 1장, GIF |
| **2. 캡틴 궁극기 파일럿** | 바렌 키트 + `회전베기`를 궁극기 등급으로 (§2.2, §4.3). 같은 회전 군집(pilgrim, pitchampion)의 임시 표시와 나란히 군집 행렬 검사. 엔진 M3, M6(큐 차지, 컷인 큐) | 키트 6~12 + 18~30 | 0.5~0.8M | G1 키트, G3 키 이미지, G6 최종 |
| **2b. 어려운 쌍 검증** | 철벽 방진(브리긴다) 표준 등급 + rally 고리 3인방 중 1명의 키트 초안으로 "고리 없이 rally" 증명. 서리 영주 vs 서리 거인 왕 키트 쌍 초안(그림은 키 이미지까지만) | 8~14 + 키 이미지 2 | 0.4~0.6M | 쌍 비교 페이지 |
| **3. 나머지 범용 계열** | 찌르기, 타격, 화살 적중, 치유, 불, 번개, 저주 (7계열, 키 이미지는 한 번에 묶어 승인) | 21~42 | 0.7~1M | 키 이미지 묶음 1회 |
| **4. 창설 캡틴 9명** | 키트 9 + 특수기 9(표준) + 기본공격 9 | 9×(6~12 + 8~14 + 3) ≈ 150~260 | 9×0.3~0.5 ≈ 3~4.5M | 키트 9 (G1) |
| **5. 영웅 7명** | 같은 구성 | ≈ 120~200 | ≈ 2~3.5M | 키트 7 |
| **6. 스토리 보스 7명** | 키트 + 예고 + 적중 (대지 분쇄 5명은 여기서 다섯 갈래로 나뉜다). 순서: 고블린 왕 → 거미 여왕 → 늪의 마녀 → 모래 폭군 → 서리 거인 왕 → 베르녹스 → 이그니스. 페이즈 전환은 엔진에 페이즈가 생긴 뒤 | 7×(6~12 + 10~16) ≈ 110~200 | ≈ 3~4M | 키트 7, 보스 컷인 |
| **7. 나머지 캡틴 24명** | 영입 순서대로(초기 → 중기 → 후기) | ≈ 400~700 | ≈ 7~12M | 키트 24 |
| **이후** | 캐릭터별 세 번째 스킬(궁극기)이 생길 때마다 궁극기 등급 | 스킬당 18~30 | 스킬당 0.3~0.5M | 궁극기마다 G3/G6 |

- 1~6단계 합계는 클라우드 약 11~17M 토큰, 그림 약 400~750프레임이다(이펙트 프레임은 몸 스트립보다 훨씬 작다).
- 특수기 40개를 전부 궁극기로 만들면 비용이 2~3배다(§9 Q2).

---

## 9. 주인에게 묻는 것 (3개)

**Q1. 시그니처의 코드 빛.** 시그니처 이펙트에 키트 색으로 물든 코드 광원(부드러운 가산 빛, 화면 섬광·어둡게)과 공용 방출기 물리를 써도 될까? 입자 그림 자체는 그 캐릭터가 그린 조각만 쓴다는 조건이다. 엔진은 두 방식을 다 지원한다.
- 제안: 허용. 다만 모양을 가진 빛은 그림만 쓰고, 코드 빛은 "모양 없는 조명"으로 한정한다.

**Q2. 지금 특수기의 등급과 기본공격.** 지금 특수기 40개를 "시그니처 표준"으로 만들고, 궁극기는 앞으로 생길 세 번째 스킬에 아껴 둘까? 아니면 지금 전부 궁극기로 할까(비용 2~3배)? 같이 정할 것: 캡틴·영웅 기본공격에 키트 조각 3프레임을 지금 넣을지(캐릭터당 프레임 3장 추가, 가장 자주 보이는 순간), 나중으로 미룰지.
- 제안: 표준 + 기본공격 지금 넣기. 바렌 파일럿만 궁극기 등급으로 해서 최고 등급의 비용을 잰다.

**Q3. 연출이 속도를 끊는 정도.** 컷인과 화면 정지·어둡게를 언제 보여줄까?
- 제안: 컷인은 캐릭터마다 전투당 첫 사용(그리고 궁극기)에만. 정지·어둡게는 1× 속도에서만 하고 2×/4×에서는 짧게 줄인다. 적 보스도 컷인 변형을 받는다.

**반대가 없으면 적용할 기본안** (질문 아님):
- 실제 캡틴 캐릭터인 라이벌 적 캡틴은 자기 시그니처를 쓴다.
- 시그니처가 생기기 전의 캡틴 특수기는 중립 최소 표시로 줄인다(§6.6).
- 키트보다 모티프 배정표(47명)를 먼저 한 번에 승인한다(§5.2).
