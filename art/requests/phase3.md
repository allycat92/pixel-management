# 그림 요청서 — 3단계 (전투 캐릭터 스프라이트 시트)

> `node tools/art/requests.js`로 자동 생성된다. 규격은 `art/STYLE.md`의 **전투 캐릭터**, 절차는 `art/README.md`,
> GPT 에 넘기는 규칙은 `art/requests/gpt_handoff_notes.md` (이 문서보다 우선).
> 그림 쪽은 **핵심 자세 4개를 한 줄로** 크게 그리기만 한다. 칸 자르기·축소·팔레트·숨쉬기 루프·시트 조립·게임 등록은
> 코드 쪽이 `python3 tools/art/sheets.py`로 한다. 걷기·돌진·피격 번쩍임·스킬 효과는 게임 엔진이 그린다.

총 68장 · 결과물은 `art/inbox/<file>`에 PNG로 넣는다.

## 진행 순서 (주인과 합의한 것)

| 단계 | 누가 | 결과 |
|---|---|---|
| 디자인 초안 | NovelAI | `art/concepts/` (주인이 고른 것만, 디자인 참고용) |
| 자세 가이드 | 코드 (`tools/pixelart/posekit.py`) | 4등신 마네킹, 캐릭터마다 `guide_strip.png` |
| 최종 그림 | **GPT** | 한 화풍으로 통일한 1536x1024 띠 한 장씩 |
| 후처리 | `tools/art/sheets.py` | 80x80 칸 시트 + manifest |

1. **바렌(`captain_blademaster`)을 먼저** 그리고 멈춘다 → 주인이 승인하면 그 그림이 **화풍 기준(앵커)** 이 된다.
2. 나머지 창설 후보 8명을 앵커에 맞춰 그린다 (아래 순서). 로드릭 기마(추가 선택, 게임 미사용)는 맨 마지막.
3. 그 다음 묶음(일반 병과·특별 용병·몬스터·나머지 대장)은 **9명이 끝난 뒤**. 아직 디자인 초안이 없어서 초상화(ref)와 아래 프롬프트를 쓴다.

- **모두 4등신** (머리 = 선 키의 1/4). 예전의 "3등신 치비" 규칙은 폐기.
- 창설 후보 9명은 캐릭터마다 꾸러미 `art/requests/phase3/captain_<key>/` (concept.png · portrait.png · guide_1..4 · guide_strip.png · README.md)를 쓴다.
  꾸러미는 `python3 tools/art/handoff.py`로 다시 만든다.
- 그림 쪽에 붙여 넣을 메시지: **`art/requests/phase3_gpt.md`** (메시지 A = 바렌만, 메시지 B = 승인 후 나머지).

## NovelAI로 만들 때 (코드 쪽, 사용자가 원할 때만)

창설 후보 9명의 **NovelAI** 프롬프트는 주인이 고른 초안의 프롬프트·시드 그대로다 (`art/concepts/selections.json`). 나머지는 한 장에 한 자세(전투 대기 자세).
무료 범위(넓이 <= 1024x1024, 28 steps, 1장)로, 한 번에 몇 장씩만:

```
python3 tools/art/novelai.py --only sheet/captain/ironwall      # → art/inbox/sheet_captain_ironwall.png
python3 tools/art/sheets.py art/inbox/sheet_captain_ironwall.png  # → assets/art/sheets/ + manifest
```

## 1. 창설 후보 대장

### 1. 바렌 — 떠돌이 검귀 (검귀)
- 파일: `sheet_captain_blademaster.png` · id: `sheet/captain/blademaster` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_blademaster.png`
- 꾸러미: `art/requests/phase3/captain_blademaster/` (README · concept · guide_strip) · **화풍 기준(앵커): 먼저 그리고 승인 대기**

```
Battle sprite of 바렌 (blademaster), a mercenary captain. Class: 검귀 (warrior). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_blademaster/README.md; concept draft art/requests/phase3/captain_blademaster/concept.png (design only), portrait art/requests/phase3/captain_blademaster/portrait.png (face only). Game colors: skin #e0ac7e, hair #2b1d14, outfit main color #3a1018, accent color #e8e4d8. This image is the STYLE ANCHOR for every other character: draw it first, then stop for approval. FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, full body, four heads tall, young swordsman, messy dark brown hair, white headband, long headband tails, scar on cheek, dark crimson half cape, dark navy tunic, leather belt, cross strap, dark trousers, brown boots, holding katana with both hands, sword held diagonally, wide stance, bent knees, fighting stance, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 2. 브리긴다 — 철벽의 여단장 (철벽 수호자)
- 파일: `sheet_captain_ironwall.png` · id: `sheet/captain/ironwall` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_ironwall.png`
- 꾸러미: `art/requests/phase3/captain_ironwall/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 브리긴다 (ironwall), a mercenary captain. Class: 철벽 수호자 (warrior). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_ironwall/README.md; concept draft art/requests/phase3/captain_ironwall/concept.png (design only), portrait art/requests/phase3/captain_ironwall/portrait.png (face only). Game colors: skin #f2c9a0, hair #a8642a (long), outfit main color #4a5a6a, accent color #d9a441. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, full body, four heads tall, adult female brigade commander, long auburn hair, braided hair, steel helmet, scar across nose, slate grey plate armor, gold trim, leather belt, gray tabard, dark trousers, brown boots, large tower shield, holding mace, shield raised forward, wide stance, bent knees, defensive stance, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 3. 이사벨 — 퇴역 참모 (전술가)
- 파일: `sheet_captain_tactician.png` · id: `sheet/captain/tactician` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_tactician.png`
- 꾸러미: `art/requests/phase3/captain_tactician/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 이사벨 (tactician), a mercenary captain. Class: 전술가 (mage). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_tactician/README.md; concept draft art/requests/phase3/captain_tactician/concept.png (design only), portrait art/requests/phase3/captain_tactician/portrait.png (face only). Game colors: skin #f5d6b8, hair #3a3f6b (long), outfit main color #3a3a4a, accent color #f2c94c. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, full body, four heads tall, young female officer, long dark indigo hair, straight hair, black tricorne hat, charcoal military coat, gold epaulettes, gold buttons, leather belt, dark trousers, black boots, holding staff in one hand, pointing forward with other hand, giving orders, calm expression, standing, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 4. 로드릭 — 말을 잃은 기사 (창기병)
- 파일: `sheet_captain_lancer.png` · id: `sheet/captain/lancer` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_lancer.png`
- 꾸러미: `art/requests/phase3/captain_lancer/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 로드릭 (lancer), a mercenary captain. Class: 창기병 (warrior). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_lancer/README.md; concept draft art/requests/phase3/captain_lancer/concept.png (design only), portrait art/requests/phase3/captain_lancer/portrait.png (face only). Game colors: skin #f2c9a0, hair #5a3720, outfit main color #3d5a9c, accent color #e8e4d8. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, full body, four heads tall, young noble knight, short brown hair, stubble, determined eyes, ornate steel helmet with blue plume, visor raised, polished blue plate armor, gold trim, worn white surcoat with blue lion emblem, tattered red cape, steel greaves, holding lance with blue pennant, lance pointed right, lunging, wide stance, bent knees, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 5. 키아라 — 숲의 덫꾼 (덫사냥꾼)
- 파일: `sheet_captain_huntress.png` · id: `sheet/captain/huntress` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_huntress.png`
- 꾸러미: `art/requests/phase3/captain_huntress/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 키아라 (huntress), a mercenary captain. Class: 덫사냥꾼 (archer). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_huntress/README.md; concept draft art/requests/phase3/captain_huntress/concept.png (design only), portrait art/requests/phase3/captain_huntress/portrait.png (face only). Game colors: skin #e0ac7e, hair #a8642a (long), outfit main color #4a5a2a, accent color #c58f1e. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, full body, four heads tall, young huntress, long auburn hair, ponytail, ochre headband, freckles, olive green hooded tunic, leather vest, rope coil on belt, quiver on back, dark trousers, brown boots, holding bow, drawing bow, arrow nocked, aiming, wide stance, bent knees, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 6. 펠릭스 — 시골 마법사 (떠돌이 마법사)
- 파일: `sheet_captain_hedgemage.png` · id: `sheet/captain/hedgemage` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_hedgemage.png`
- 꾸러미: `art/requests/phase3/captain_hedgemage/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 펠릭스 (hedgemage), a mercenary captain. Class: 떠돌이 마법사 (mage). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_hedgemage/README.md; concept draft art/requests/phase3/captain_hedgemage/concept.png (design only), portrait art/requests/phase3/captain_hedgemage/portrait.png (face only). Game colors: skin #f5d6b8, hair #e3c565, outfit main color #5a4a7a, accent color #e8c86a. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, full body, four heads tall, young country mage, short messy blonde hair, worn wizard hat, patched hat, purple robe, yellow trim, rope belt, satchel, dark trousers, brown boots, holding wooden staff, fire in hand, casting spell, arm extended forward, wide stance, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 7. 마그다 — 종군 의무관 (야전 의무관)
- 파일: `sheet_captain_fieldmedic.png` · id: `sheet/captain/fieldmedic` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_fieldmedic.png`
- 꾸러미: `art/requests/phase3/captain_fieldmedic/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 마그다 (fieldmedic), a mercenary captain. Class: 야전 의무관 (cleric). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_fieldmedic/README.md; concept draft art/requests/phase3/captain_fieldmedic/concept.png (design only), portrait art/requests/phase3/captain_fieldmedic/portrait.png (face only). Game colors: skin #c68a5c, hair #2b1d14 (long), outfit main color #e8e4d8, accent color #9c3b2e. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, full body, four heads tall, adult female field medic, long black hair, tied hair, tan skin, bandage on forehead, off-white coat, plain dark red armband, dark red scarf, apron, pouches on belt, dark trousers, brown boots, holding mace, other hand raised, healing glow, determined expression, standing, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 8. 진 — 뒷골목 해결사 (해결사)
- 파일: `sheet_captain_fixer.png` · id: `sheet/captain/fixer` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_fixer.png`
- 꾸러미: `art/requests/phase3/captain_fixer/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 진 (fixer), a mercenary captain. Class: 해결사 (rogue). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_fixer/README.md; concept draft art/requests/phase3/captain_fixer/concept.png (design only), portrait art/requests/phase3/captain_fixer/portrait.png (face only). Game colors: skin #e0ac7e, hair #2b1d14, outfit main color #2a2a2a, accent color #c9c2b8. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, full body, four heads tall, young rogue, short black hair, black hood, grey scarf over mouth, narrow eyes, black leather jacket, grey trim, leather belt, cross strap, dark trousers, black boots, holding single dagger, reverse grip, low crouch, wide stance, bent knees, ready to dash, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 9. 하랄드 — 백발의 노병 (노병)
- 파일: `sheet_captain_veteran.png` · id: `sheet/captain/veteran` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_veteran.png`
- 꾸러미: `art/requests/phase3/captain_veteran/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
Battle sprite of 하랄드 (veteran), a mercenary captain. Class: 노병 (warrior). Design (what to keep and what to fix), weapon and per-pose notes: art/requests/phase3/captain_veteran/README.md; concept draft art/requests/phase3/captain_veteran/concept.png (design only), portrait art/requests/phase3/captain_veteran/portrait.png (face only). Game colors: skin #f2c9a0, hair #c9c2b8, outfit main color #5a5a4a, accent color #c9c2b8. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (proportions, rendering, outline, palette, lighting, scale). FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction. Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure; feet on one common baseline at y=870 (85% of the height), the idle figure about 400 px tall (39% of the height, 110 px per head - the same for every character); figures and weapons never touch each other or the border. STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left, high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones, dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield. The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting. BACKGROUND: perfectly flat solid magenta #FF00FF, no gradient, floor, cast shadow or scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, full body, four heads tall, old man, veteran soldier, short white hair, white beard, dented steel helmet, scars on face, olive grey gambeson, chainmail, leather belt, round wooden shield, dark trousers, worn boots, holding sword, shield raised, steady guard stance, wide stance, bent knees, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, two heads, multiple heads, conjoined, extra head
```

</details>

### 10. 로드릭 — 기마 (추가 선택, 게임 미사용)
- 파일: `sheet_captain_lancer_mounted.png` · id: `sheet/captain/lancer_mounted` · 생성: 1536x1024 2x2 격자 · 게임: 160x160 cells, body ~96px · 참고: `art/inbox/captain_lancer.png`
- 꾸러미: `art/requests/phase3/captain_lancer/` (README · concept · guide_strip) · 화풍 기준: `art/inbox/sheet_captain_blademaster.png`

```
OPTIONAL, LAST. Mounted variant of 로드릭 (lancer) for a possible later "regains a warhorse" form; the game does not use it yet. Same knight, armour, colours and style as the approved art/inbox/sheet_captain_lancer.png and the style anchor art/inbox/sheet_captain_blademaster.png. Design: art/requests/phase3/captain_lancer/concept_mounted.png (design only). The horse has EXACTLY ONE head. FORMAT: one PNG 1536x1024 as a 2x2 grid of equal quadrants (top: idle, wind-up; bottom: strike, hit), layout and size per art/requests/phase3/captain_lancer/guide_mounted_layout.png and art/requests/phase3/captain_lancer/README.md. Rider 4 heads tall, front three-quarter view facing right, flat #FF00FF background, no floor, shadow, text or effects.
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, full body, knight riding a horse, four heads tall, young knight, short brown hair, stubble, determined eyes, steel helmet with blue plume, visor raised, blue plate armor, white surcoat with blue emblem, red cape, armored warhorse, dark brown horse, blue caparison, holding lance, couched lance, charging, galloping, three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms, extra legs, two riders, multiple horses, conjoined
```

</details>

## 2. 일반 병과 (창설 후보 9명 다음)

### 일반 병과 — 전사
- 파일: `sheet_class_warrior.png` · id: `sheet/class/warrior` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px

```
Battle sprite of a generic young mercenary soldier, open-face helmet hiding most of the hair, padded armor with a breastplate, round wooden shield on the back, one-handed sword. Main outfit color #9c3b2e, accent #d9a441. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young mercenary soldier, open-face helmet hiding most of the hair, padded armor with a breastplate, round wooden shield on the back, one-handed sword, red outfit, gold trim, holding sword, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 일반 병과 — 궁수
- 파일: `sheet_class_archer.png` · id: `sheet/class/archer` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px

```
Battle sprite of a generic young mercenary archer, cloth headband, light leather armor, quiver on the back, short bow. Main outfit color #3f7a3a, accent #a7d26a. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young mercenary archer, cloth headband, light leather armor, quiver on the back, short bow, green outfit, lime green trim, holding bow, quiver, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 일반 병과 — 마법사
- 파일: `sheet_class_mage.png` · id: `sheet/class/mage` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px

```
Battle sprite of a generic young battle mage, wide-brimmed pointed hat hiding the hair, long robe with a belt and pouches, wooden staff with a crystal. Main outfit color #3d4a9c, accent #f2d24b. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young battle mage, wide-brimmed pointed hat hiding the hair, long robe with a belt and pouches, wooden staff with a crystal, blue outfit, yellow trim, holding staff, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 일반 병과 — 성직자
- 파일: `sheet_class_cleric.png` · id: `sheet/class/cleric` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px

```
Battle sprite of a generic young war priest, short hair, simple white tabard with a gold sun emblem over chainmail, holy mace and a small book on the belt. Main outfit color #e8e4d8, accent #d9a441. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young war priest, short hair, simple white tabard with a gold sun emblem over chainmail, holy mace and a small book on the belt, white outfit, gold trim, holding mace, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 일반 병과 — 도적
- 파일: `sheet_class_rogue.png` · id: `sheet/class/rogue` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px

```
Battle sprite of a generic young rogue, deep hood shading the face, dark leather armor with many straps, scarf over the mouth, two daggers. Main outfit color #3b3346, accent #8f2d4a. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young rogue, deep hood shading the face, dark leather armor with many straps, scarf over the mouth, two daggers, dark grey outfit, magenta trim, holding dagger, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

## 3. 특별 용병 (창설 후보 9명 다음)

### 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자)
- 파일: `sheet_hero_kai.png` · id: `sheet/hero/kai` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_kai.png`

```
Battle sprite of 카이: young elf man, pointed ears, long blond hair, green ranger cloak, silver longbow. Class: 은빛 순찰자 (archer). Colors: skin #f5d6b8, hair #e3c565 (long), outfit main color #2f6a4a, accent color #e8e4d8. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young elf man, pointed ears, long blond hair, green ranger cloak, silver longbow, green outfit, white trim, headband, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 세라핀 — 파문당한 성녀 (파문 성녀)
- 파일: `sheet_hero_seraphine.png` · id: `sheet/hero/seraphine` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_seraphine.png`

```
Battle sprite of 세라핀: young woman, pale, blonde hair, torn white saint robes with a red sash, sorrowful but kind. Class: 파문 성녀 (cleric). Colors: skin #f2c9a0, hair #e3c565 (long), outfit main color #f2ecd8, accent color #d6455d. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, young woman, pale, blonde hair, torn white saint robes with a red sash, sorrowful but kind, long hair, white outfit, tan trim, holding mace, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 리라 — 가면 쓴 의적 (가면 의적)
- 파일: `sheet_hero_lyra.png` · id: `sheet/hero/lyra` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_lyra.png`

```
Battle sprite of 리라: young woman in a white half-mask, dark violet outfit, hood, quick daggers, mischievous smile. Class: 가면 의적 (rogue). Colors: skin #f5d6b8, hair #8c2f2f (long), outfit main color #2a1a3a, accent color #e8e4d8. Weapon: dagger. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, young woman in a white half-mask, dark violet outfit, hood, quick daggers, mischievous smile, red hair, long hair, charcoal outfit, white trim, hood, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 그롬 — 피의 투기장 챔피언 (투기장 패왕)
- 파일: `sheet_hero_grom.png` · id: `sheet/hero/grom` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_grom.png`

```
Battle sprite of 그롬: massive clan warrior man, brown skin, scarred, arena champion belt, greatsword. Class: 투기장 패왕 (warrior). Colors: skin #8fae6a, hair #2b1d14, outfit main color #7a2418, accent color #f2c94c. Weapon: sword. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, massive clan warrior man, brown skin, scarred, arena champion belt, greatsword, dark brown hair, short hair, crimson outfit, yellow trim, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 아스텔 — 마탑의 마지막 제자 (마탑 계승자)
- 파일: `sheet_hero_astel.png` · id: `sheet/hero/astel` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_astel.png`

```
Battle sprite of 아스텔: young man scholar-mage, glasses, purple robes with gold embroidery, floating spellbook. Class: 마탑 계승자 (mage). Colors: skin #f2c9a0, hair #c9c2b8 (long), outfit main color #3a1a5a, accent color #f2d24b. Weapon: staff. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, young man scholar-mage, glasses, purple robes with gold embroidery, floating spellbook, grey hair, long hair, dark purple outfit, yellow trim, hat, holding staff, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 마리솔 — 닻을 잃은 해적 선장 (해적 선장)
- 파일: `sheet_hero_marisol.png` · id: `sheet/hero/marisol` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_marisol.png`

```
Battle sprite of 마리솔: woman pirate captain in her thirties, tricorn hat, navy coat, flintlock pistol and bow. Class: 해적 선장 (archer). Colors: skin #c68a5c, hair #2b1d14 (long), outfit main color #1a2a4a, accent color #d6455d. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, woman pirate captain in her thirties, tricorn hat, navy coat, flintlock pistol and bow, dark brown hair, long hair, navy outfit, tan trim, hat, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 오스윈 — 몰락한 기사단장 (몰락 기사단장)
- 파일: `sheet_hero_oswin.png` · id: `sheet/hero/oswin` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/hero_oswin.png`

```
Battle sprite of 오스윈: old knight commander, grey hair, rusted silver plate armor with a faded royal crest. Class: 몰락 기사단장 (warrior). Colors: skin #e0ac7e, hair #c9c2b8, outfit main color #c9ced6, accent color #3d5a9c. Weapon: sword. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, old knight commander, grey hair, rusted silver plate armor with a faded royal crest, short hair, silver outfit, blue trim, helmet, holding sword, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

## 4. 지역 몬스터 (창설 후보 9명 다음)

### 몬스터 — 고블린
- 파일: `sheet_monster_goblin.png` · id: `sheet/monster/고블린` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~44px

```
Battle sprite of a monster: small green goblin raider with big ears, crude leather armor, rusty short sword. Main color #6fa84a, dark #4a7a30, accent #7a5236, eyes #f2c94c. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, small green goblin raider with big ears, crude leather armor, rusty short sword, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 산적
- 파일: `sheet_monster_bandit.png` · id: `sheet/monster/산적` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~60px

```
Battle sprite of a monster: human bandit, red bandana, patched leather jerkin, short axe. Main color #e0ac7e, dark #a8764e, accent #8f2d3a, eyes #1b1420. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, human bandit, red bandana, patched leather jerkin, short axe, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 사막 도적
- 파일: `sheet_monster_desert-bandit.png` · id: `sheet/monster/사막 도적` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~60px

```
Battle sprite of a monster: desert raider, sand-colored head wrap and veil, curved scimitar. Main color #c68a5c, dark #8d5a3b, accent #e8d5a3, eyes #1b1420. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, desert raider, sand-colored head wrap and veil, curved scimitar, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 해골 병사
- 파일: `sheet_monster_skeleton.png` · id: `sheet/monster/해골 병사` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~60px

```
Battle sprite of a monster: skeleton soldier, cracked bones, rusty helmet and round shield, notched sword, glowing red eye sockets. Main color #e8e4d8, dark #a8a49a, accent #5c606a, eyes #d6455d. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, skeleton soldier, cracked bones, rusty helmet and round shield, notched sword, glowing red eye sockets, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 들늑대
- 파일: `sheet_monster_wolf.png` · id: `sheet/monster/들늑대` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~40px

```
Battle sprite of a monster: grey wild wolf, four legs, snarling, walking to the right. Main color #8a8f99, dark #5c606a, eyes #f2c94c. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, grey wild wolf, four legs, snarling, walking to the right, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 거대 거미
- 파일: `sheet_monster_giant-spider.png` · id: `sheet/monster/거대 거미` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~40px

```
Battle sprite of a monster: giant dark purple spider, eight legs, red eyes. Main color #3b3346, dark #241b29, eyes #d6455d. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, giant dark purple spider, eight legs, red eyes, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 오크
- 파일: `sheet_monster_orc.png` · id: `sheet/monster/오크` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~66px

```
Battle sprite of a monster: muscular green orc warrior, iron pauldron, big cleaver. Main color #5f8a3a, dark #456a28, accent #5c606a, eyes #d6455d. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, muscular green orc warrior, iron pauldron, big cleaver, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 늪 슬라임
- 파일: `sheet_monster_slime.png` · id: `sheet/monster/늪 슬라임` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~30px

```
Battle sprite of a monster: green translucent slime blob with a simple face. Main color #6fbf6f, dark #3f8a3f, eyes #1b1420. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, green translucent slime blob with a simple face, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 망령
- 파일: `sheet_monster_wraith.png` · id: `sheet/monster/망령` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~56px

```
Battle sprite of a monster: pale blue floating ghost in tattered robes, glowing cyan eyes, no legs. Main color #b8c8e8, dark #7a8ab0, eyes #6ff0f0. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, pale blue floating ghost in tattered robes, glowing cyan eyes, no legs, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 리자드맨
- 파일: `sheet_monster_lizardman.png` · id: `sheet/monster/리자드맨` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~62px

```
Battle sprite of a monster: teal-green lizardman warrior, scaly tail, spear and hide shield. Main color #4f9a7a, dark #2f6a50, accent #8a6a3a, eyes #f2c94c. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, teal-green lizardman warrior, scaly tail, spear and hide shield, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 하피
- 파일: `sheet_monster_harpy.png` · id: `sheet/monster/하피` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~56px

```
Battle sprite of a monster: harpy, woman with feathered purple wings for arms and bird talons. Main color #e0ac7e, dark #a8764e, accent #8a6aa8, eyes #d6455d. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, harpy, woman with feathered purple wings for arms and bird talons, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 가고일
- 파일: `sheet_monster_gargoyle.png` · id: `sheet/monster/가고일` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~56px

```
Battle sprite of a monster: grey stone gargoyle with bat wings and horns, crouching. Main color #6b737c, dark #44494f, accent #5c606a, eyes #d6455d. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, grey stone gargoyle with bat wings and horns, crouching, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 미믹
- 파일: `sheet_monster_mimic.png` · id: `sheet/monster/미믹` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~40px

```
Battle sprite of a monster: mimic treasure chest monster with teeth and a long tongue, gold trim. Main color #8a5a2b, dark #5a3a1a, accent #d9a441, eyes #f2c94c. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, mimic treasure chest monster with teeth and a long tongue, gold trim, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 마족 전사
- 파일: `sheet_monster_demon-warrior.png` · id: `sheet/monster/마족 전사` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~68px

```
Battle sprite of a monster: red-skinned demon warrior with horns, black armor, flaming eyes, jagged sword. Main color #8a2430, dark #5a1420, accent #3a2a2a, eyes #f2c94c. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, red-skinned demon warrior with horns, black armor, flaming eyes, jagged sword, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 지옥견
- 파일: `sheet_monster_hellhound.png` · id: `sheet/monster/지옥견` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~44px

```
Battle sprite of a monster: black-red hellhound, four legs, burning orange eyes and a mane of fire. Main color #7a2418, dark #4a140c, eyes #f39c12. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, black-red hellhound, four legs, burning orange eyes and a mane of fire, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 데스 나이트
- 파일: `sheet_monster_death-knight.png` · id: `sheet/monster/데스 나이트` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~70px

```
Battle sprite of a monster: undead death knight in dark iron plate, purple tattered cape, teal ghost flames in the visor. Main color #4a4a5a, dark #2a2a36, accent #6b2a6b, eyes #7ed3c8. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, undead death knight in dark iron plate, purple tattered cape, teal ghost flames in the visor, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 숲 트롤
- 파일: `sheet_monster_forest-troll.png` · id: `sheet/monster/숲 트롤` · 생성: 1536x1024 1x4 띠 · 게임: 112x112 cells, body ~92px

```
Battle sprite of a monster: huge mossy green forest troll, long arms, tree-branch club. Main color #5a7a5a, dark #3e5a3e, accent #6b4226, eyes #f2c94c. A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height). Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, huge mossy green forest troll, long arms, tree-branch club, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 서리 트롤
- 파일: `sheet_monster_frost-troll.png` · id: `sheet/monster/서리 트롤` · 생성: 1536x1024 1x4 띠 · 게임: 112x112 cells, body ~92px

```
Battle sprite of a monster: huge pale blue frost troll with icicles, ice club. Main color #9fc4dc, dark #6f94ac, accent #3a4a6b, eyes #3d4a9c. A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height). Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, huge pale blue frost troll with icicles, ice club, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 설인
- 파일: `sheet_monster_yeti.png` · id: `sheet/monster/설인` · 생성: 1536x1024 1x4 띠 · 게임: 112x112 cells, body ~92px

```
Battle sprite of a monster: huge white-furred yeti, blue face, big fists. Main color #e8eef2, dark #b0bcc8, accent #8a9aa8, eyes #3d4a9c. A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height). Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, huge white-furred yeti, blue face, big fists, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 전갈 거인
- 파일: `sheet_monster_giant-scorpion.png` · id: `sheet/monster/전갈 거인` · 생성: 1536x1024 1x4 띠 · 게임: 112x112 cells, body ~72px

```
Battle sprite of a monster: giant golden desert scorpion, raised stinger tail, big pincers. Main color #c58f1e, dark #8a6210, eyes #1b1420. A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height). Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, giant golden desert scorpion, raised stinger tail, big pincers, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 와이번
- 파일: `sheet_monster_wyvern.png` · id: `sheet/monster/와이번` · 생성: 1536x1024 1x4 띠 · 게임: 112x112 cells, body ~84px

```
Battle sprite of a monster: red wyvern dragon, two legs, wings half spread, long tail. Main color #9c3b2e, dark #6b2418, accent #c25a3a, eyes #f2c94c. A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height). Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, red wyvern dragon, two legs, wings half spread, long tail, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 몬스터 — 리치의 망령
- 파일: `sheet_monster_lich-wraith.png` · id: `sheet/monster/리치의 망령` · 생성: 1536x1024 1x4 띠 · 게임: 112x112 cells, body ~88px

```
Battle sprite of a monster: large purple lich ghost in a crown and robes, green soul fire in its hands. Main color #9b6ad6, dark #6b3d9c, eyes #7ed37e. A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height). Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
no humans, solo, monster, large purple lich ghost in a crown and robes, green soul fire in its hands, full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

## 5. 나머지 대장 (창설 후보 9명 다음)

### 나린 — 바람을 쫓는 사냥꾼 (바람 사냥꾼)
- 파일: `sheet_captain_windhunter.png` · id: `sheet/captain/windhunter` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_windhunter.png`

```
Battle sprite of 나린, a mercenary captain: tanned woman in her twenties, long black hair blowing in the wind, green headband, longbow. Class: 바람 사냥꾼 (archer). Colors: skin #c68a5c, hair #2b1d14 (long), outfit main color #2a4a3a, accent color #a7d26a. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, tanned woman in her twenties, long black hair blowing in the wind, green headband, longbow, dark green outfit, lime green trim, headband, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 모로 — 항구의 쥐왕 (그림자 두목)
- 파일: `sheet_captain_shadowlord.png` · id: `sheet/captain/shadowlord` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_shadowlord.png`

```
Battle sprite of 모로, a mercenary captain: cunning man in his forties, rat-like grin, hood, gold rings, dagger. Class: 그림자 두목 (rogue). Colors: skin #e0ac7e, hair #5a3720, outfit main color #1a1420, accent color #d9a441. Weapon: dagger. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, cunning man in his forties, rat-like grin, hood, gold rings, dagger, brown hair, short hair, black outfit, gold trim, hood, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 카시안 — 파문당한 마검사 (마검사)
- 파일: `sheet_captain_spellblade.png` · id: `sheet/captain/spellblade` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_spellblade.png`

```
Battle sprite of 카시안, a mercenary captain: elegant man in his thirties, long silver hair, sword glowing with blue magic. Class: 마검사 (mage). Colors: skin #f5d6b8, hair #c9c2b8 (long), outfit main color #2a2a6a, accent color #7fd6e8. Weapon: staff. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, elegant man in his thirties, long silver hair, sword glowing with blue magic, dark blue outfit, silver trim, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 엘리노어 — 성광의 기사 (성광 기사)
- 파일: `sheet_captain_saintknight.png` · id: `sheet/captain/saintknight` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_saintknight.png`

```
Battle sprite of 엘리노어, a mercenary captain: noble woman knight in her twenties, long golden hair, white and gold plate armor, holy mace. Class: 성광 기사 (cleric). Colors: skin #f2c9a0, hair #e3c565 (long), outfit main color #e8e4d8, accent color #f2c94c. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, noble woman knight in her twenties, long golden hair, white and gold plate armor, holy mace, white outfit, yellow trim, helmet, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 가르마크 — 백전의 전쟁군주 (전쟁군주)
- 파일: `sheet_captain_warlord.png` · id: `sheet/captain/warlord` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_warlord.png`

```
Battle sprite of 가르마크, a mercenary captain: huge man in his forties, red hair and beard, horned helmet, war axe, battle scars. Class: 전쟁군주 (warrior). Colors: skin #c68a5c, hair #8c2f2f, outfit main color #5a3a1a, accent color #d6455d. Weapon: sword. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, huge man in his forties, red hair and beard, horned helmet, war axe, battle scars, short hair, brown outfit, tan trim, helmet, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 테무르 — 초원의 칸 (초원의 칸)
- 파일: `sheet_captain_khan.png` · id: `sheet/captain/khan` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_khan.png`

```
Battle sprite of 테무르, a mercenary captain: nomad man in his thirties, long black braids, fur-trimmed coat, composite bow, steppe warrior. Class: 초원의 칸 (archer). Colors: skin #8d5a3b, hair #2b1d14 (long), outfit main color #8a5a2a, accent color #e8c86a. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, nomad man in his thirties, long black braids, fur-trimmed coat, composite bow, steppe warrior, dark brown hair, long hair, auburn outfit, blonde trim, headband, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 지크린데 — 용살자 (용살자)
- 파일: `sheet_captain_dragonslayer.png` · id: `sheet/captain/dragonslayer` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_dragonslayer.png`

```
Battle sprite of 지크린데, a mercenary captain: battle-hardened woman in her thirties, long blonde hair, dragon-scale armor, greatsword. Class: 용살자 (warrior). Colors: skin #f2c9a0, hair #e3c565 (long), outfit main color #6a1a14, accent color #f39c12. Weapon: sword. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, battle-hardened woman in her thirties, long blonde hair, dragon-scale armor, greatsword, crimson outfit, orange trim, helmet, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 모르데카이 — 마귀 사냥꾼 (마귀 사냥꾼)
- 파일: `sheet_captain_demonhunter.png` · id: `sheet/captain/demonhunter` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_demonhunter.png`

```
Battle sprite of 모르데카이, a mercenary captain: grizzled man in his fifties, grey stubble, dark hood, silver bullets and a holy mace. Class: 마귀 사냥꾼 (cleric). Colors: skin #e0ac7e, hair #c9c2b8, outfit main color #2a2a3a, accent color #c9c2b8. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, grizzled man in his fifties, grey stubble, dark hood, silver bullets and a holy mace, grey hair, short hair, charcoal outfit, grey trim, hood, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 리코 — 노래하는 검 (음유 검객)
- 파일: `sheet_captain_bard.png` · id: `sheet/captain/bard` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_bard.png`

```
Battle sprite of 리코, a mercenary captain: flamboyant young man, long red hair, feathered hat, lute on his back and a rapier. Class: 음유 검객 (rogue). Colors: skin #f2c9a0, hair #8c2f2f (long), outfit main color #7a2a5a, accent color #f2c94c. Weapon: dagger. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, flamboyant young man, long red hair, feathered hat, lute on his back and a rapier, magenta outfit, yellow trim, hat, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 오르가 — 늑대 무리의 어미 (야수 조련사)
- 파일: `sheet_captain_beastmaster.png` · id: `sheet/captain/beastmaster` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_beastmaster.png`

```
Battle sprite of 오르가, a mercenary captain: dark-skinned woman in her thirties, long black hair, wolf-fur mantle, a grey wolf beside her. Class: 야수 조련사 (archer). Colors: skin #8d5a3b, hair #2b1d14 (long), outfit main color #5a4a3a, accent color #d9a441. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, dark-skinned woman in her thirties, long black hair, wolf-fur mantle, a grey wolf beside her, brown leather outfit, gold trim, headband, holding bow, quiver, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 브로크 — 룬 새기는 대장장이 (룬 대장장이)
- 파일: `sheet_captain_runesmith.png` · id: `sheet/captain/runesmith` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_runesmith.png`

```
Battle sprite of 브로크, a mercenary captain: stout bearded man in his forties, orange beard, glowing blue runes on his hammer and armor. Class: 룬 대장장이 (warrior). Colors: skin #e0ac7e, hair #a8642a, outfit main color #6a4a2a, accent color #7fd6e8. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, stout bearded man in his forties, orange beard, glowing blue runes on his hammer and armor, auburn hair, short hair, brown leather outfit, silver trim, helmet, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 아멜리 — 맨발의 순례자 (순례 기사)
- 파일: `sheet_captain_pilgrim.png` · id: `sheet/captain/pilgrim` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_pilgrim.png`

```
Battle sprite of 아멜리, a mercenary captain: gentle young woman, long blonde hair, barefoot pilgrim robes, holy mace and a prayer charm. Class: 순례 기사 (cleric). Colors: skin #f5d6b8, hair #e3c565 (long), outfit main color #c8b89a, accent color #3d5a9c. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, gentle young woman, long blonde hair, barefoot pilgrim robes, holy mace and a prayer charm, grey outfit, blue trim, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 벨라도나 — 저주 거래상 (저주술사)
- 파일: `sheet_captain_hexer.png` · id: `sheet/captain/hexer` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_hexer.png`

```
Battle sprite of 벨라도나, a mercenary captain: pale woman in her thirties, long dark-blue hair, wide witch hat, green curse flames in her palm. Class: 저주술사 (mage). Colors: skin #f5d6b8, hair #3a3f6b (long), outfit main color #3a1a3a, accent color #7ed37e. Weapon: staff. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, pale woman in her thirties, long dark-blue hair, wide witch hat, green curse flames in her palm, charcoal outfit, lime green trim, hat, holding staff, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 카토 — 쇠사슬을 끊은 자 (해방 검투사)
- 파일: `sheet_captain_liberator.png` · id: `sheet/captain/liberator` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_liberator.png`

```
Battle sprite of 카토, a mercenary captain: dark-skinned muscular man, shaved head, broken shackles still on his wrists, chain weapon. Class: 해방 검투사 (warrior). Colors: skin #8d5a3b, hair #2b1d14, outfit main color #7a4a2a, accent color #c9c2b8. Weapon: sword. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, dark-skinned muscular man, shaved head, broken shackles still on his wrists, chain weapon, red outfit, grey trim, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 마렌 — 퇴역 제독 (퇴역 제독)
- 파일: `sheet_captain_admiral.png` · id: `sheet/captain/admiral` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_admiral.png`

```
Battle sprite of 마렌, a mercenary captain: elderly woman in her sixties, short grey hair, navy admiral coat with gold trim, crossbow. Class: 퇴역 제독 (archer). Colors: skin #f2c9a0, hair #c9c2b8, outfit main color #1a2a5a, accent color #f2c94c. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, elderly woman in her sixties, short grey hair, navy admiral coat with gold trim, crossbow, navy outfit, yellow trim, hat, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 세레니엘 — 숲의 수호대장 (엘프 숲지기)
- 파일: `sheet_captain_elfwarden.png` · id: `sheet/captain/elfwarden` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_elfwarden.png`

```
Battle sprite of 세레니엘, a mercenary captain: tall elf woman, long silver hair, pointed ears, green leaf-patterned cloak, elegant longbow. Class: 엘프 숲지기 (archer). Colors: skin #f5d6b8, hair #c9c2b8 (long), outfit main color #2f6a3a, accent color #e8e4d8. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, tall elf woman, long silver hair, pointed ears, green leaf-patterned cloak, elegant longbow, green outfit, white trim, headband, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 오토 — 성벽 파괴자 (공성 기술자)
- 파일: `sheet_captain_siegemaster.png` · id: `sheet/captain/siegemaster` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_siegemaster.png`

```
Battle sprite of 오토, a mercenary captain: engineer man in his forties, brass goggles on his helmet, soot-stained, heavy crossbow. Class: 공성 기술자 (archer). Colors: skin #e0ac7e, hair #5a3720, outfit main color #5a4a3a, accent color #d9a441. Weapon: bow. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, engineer man in his forties, brass goggles on his helmet, soot-stained, heavy crossbow, brown hair, short hair, brown leather outfit, gold trim, helmet, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 발타자르 — 심문관장 (대심문관)
- 파일: `sheet_captain_inquisitorlord.png` · id: `sheet/captain/inquisitorlord` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_inquisitorlord.png`

```
Battle sprite of 발타자르, a mercenary captain: severe man in his fifties, black hair, deep red hooded inquisitor robes, burning brand. Class: 대심문관 (cleric). Colors: skin #f2c9a0, hair #2b1d14, outfit main color #4a1a1a, accent color #f2c94c. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, severe man in his fifties, black hair, deep red hooded inquisitor robes, burning brand, short hair, dark crimson outfit, yellow trim, hood, holding mace, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 크림슨 — 붉은 돛의 해적왕 (해적왕)
- 파일: `sheet_captain_pirateking.png` · id: `sheet/captain/pirateking` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_pirateking.png`

```
Battle sprite of 크림슨, a mercenary captain: confident woman in her thirties, long crimson hair, tricorn hat, cutlass and hook chain. Class: 해적왕 (rogue). Colors: skin #c68a5c, hair #8c2f2f (long), outfit main color #7a1a1a, accent color #1b1420. Weapon: dagger. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, confident woman in her thirties, long crimson hair, tricorn hat, cutlass and hook chain, crimson outfit, black trim, hat, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 비요른 — 서리 협곡의 영주 (서리 영주)
- 파일: `sheet_captain_frostjarl.png` · id: `sheet/captain/frostjarl` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_frostjarl.png`

```
Battle sprite of 비요른, a mercenary captain: tall man in his thirties, long blond hair and braided beard, frost-covered armor, axe. Class: 서리 영주 (warrior). Colors: skin #f5d6b8, hair #e3c565 (long), outfit main color #4a6a8a, accent color #e8eef2. Weapon: sword. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, tall man in his thirties, long blond hair and braided beard, frost-covered armor, axe, blue outfit, white trim, helmet, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 에우리아 — 마지막 대현자 (대현자)
- 파일: `sheet_captain_archmagus.png` · id: `sheet/captain/archmagus` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_archmagus.png`

```
Battle sprite of 에우리아, a mercenary captain: ancient wise woman, very long white hair, star-embroidered robes, glowing staff. Class: 대현자 (mage). Colors: skin #f5d6b8, hair #ffffff (long), outfit main color #1a1a4a, accent color #f2f2ff. Weapon: staff. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, ancient wise woman, very long white hair, star-embroidered robes, glowing staff, navy outfit, white trim, hat, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 루치아 — 빛을 든 사도 (빛의 사도)
- 파일: `sheet_captain_lightbearer.png` · id: `sheet/captain/lightbearer` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_lightbearer.png`

```
Battle sprite of 루치아, a mercenary captain: radiant young woman, long golden hair, white robes, soft light around her hands. Class: 빛의 사도 (cleric). Colors: skin #f2c9a0, hair #e3c565 (long), outfit main color #f2ecd8, accent color #f39c12. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, radiant young woman, long golden hair, white robes, soft light around her hands, white outfit, orange trim, holding mace, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 니클라 — 그림자 길드의 여왕 (밤의 여왕)
- 파일: `sheet_captain_shadowqueen.png` · id: `sheet/captain/shadowqueen` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_shadowqueen.png`

```
Battle sprite of 니클라, a mercenary captain: dangerous elegant woman in her thirties, long black hair, dark hood, twin daggers. Class: 밤의 여왕 (rogue). Colors: skin #e0ac7e, hair #1b1420 (long), outfit main color #1a0a2a, accent color #d6455d. Weapon: dagger. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1girl, solo, dangerous elegant woman in her thirties, long black hair, dark hood, twin daggers, black outfit, tan trim, hood, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>

### 우르그 — 거인의 피 (거인의 피)
- 파일: `sheet_captain_titan.png` · id: `sheet/captain/titan` · 생성: 1536x1024 1x4 띠 · 게임: 80x80 cells, body ~64px · 참고: `art/inbox/captain_titan.png`

```
Battle sprite of 우르그, a mercenary captain: giant man with giant-blood, long brown hair, enormous build, stone-like skin, huge maul. Class: 거인의 피 (warrior). Colors: skin #c68a5c, hair #5a3720 (long), outfit main color #5a3a2a, accent color #e8c86a. Weapon: mace. Keep the face, hair and outfit of the reference portrait. Match the approved style anchor art/inbox/sheet_captain_blademaster.png (art-inbox branch): its rendering, outline, palette treatment, lighting and character scale. FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right: (1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing). Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height, each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border. All four face RIGHT in a front three-quarter view. STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi), creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left, readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively, soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur. BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery. NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).
```

<details><summary>NovelAI (한 자세)</summary>

```
1boy, solo, giant man with giant-blood, long brown hair, enormous build, stone-like skin, huge maul, brown outfit, blonde trim, four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow

Negative: lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background
```

</details>
