# 일반 병과 — 궁수 — GPT handoff (`class_archer`)

> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.
> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.
> 모든 자료는 브랜치 `claude/dot-fantasy-management-game-saupju`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.

## Prompt for GPT (English)

```
TASK: draw the battle-sprite strip of the GENERIC archer class sprite (궁수). This ONE sheet is shared by every nameless mercenary and faction soldier of this class, friend and foe, and the game recolours its uniform per faction (see KEY COLOURS). Save it as art/inbox/sheet_class_archer.png on the art-inbox branch (a new file there; do not rename). In a chat without repository access, return the PNG in the chat instead.

CHARACTER: a short recurve bow the size of the guide bow (brown wood), a brown leather quiver of arrows on the back; the FACE is covered or in shadow (see the headgear below), because this one sprite stands for hundreds of different soldiers; whatever little of the face shows is generic, with no scars, marks or distinctive features; the HOOD of the tunic is UP, and a cloth MASK covers the lower face up to the nose, so only a narrow warm-dark shadow strip at eye level shows, no skin (hair hidden); knee-length HOODED TUNIC; brown leather vest over the tunic; leather bracers; dark trousers, brown boots; lean build.

KEY COLOURS (the most important rule of this sheet): ONE sheet is shared by every faction and company, and the game recolours the uniform at runtime by replacing these EXACT colours with the faction colours, keeping their light/dark steps.
  - OUTFIT keys = the hooded tunic (hood, sleeves, skirt of the tunic) and the face mask, darkest to lightest: #263459 (deep shadow, folds), #394b78 (shadow), #52679c (base), #7489be (lit side)
  - ACCENT keys = the hood's front edge and the tunic's hem trim, darkest to lightest: #3f7a6c (shadow), #5ea590 (base), #96d1bb (lit)
  - flat fills only on these areas: no dithering, gradient, noise, texture, soft blending or in-between shades; their shading uses only these steps
  - these seven colours appear NOWHERE else (not on metal, skin, hair, leather, eyes, outline or background), and nothing else on the figure is blue, slate, teal or mint: steel is NEUTRAL grey, leather and wood are warm browns, shadows on the other parts are warm or neutral, never blue (this overrides the general "shadows toward purple/blue" style rule for this sheet)
  - every NON-key colour on the figure (outline, shadows, metal, leather, skin, eyes ...) must be at RGB distance sqrt(dR^2 + dG^2 + dB^2) >= 50 from all seven keys: the pipeline snaps colours within 34 of a key ONTO the key (so they get recoloured), and shades 34-50 away stay as untinted blue islands
  - outline and shadows: use a warm / neutral dark ramp, e.g. outline #2a2220, shadows #3a2e2a / #4a3a2e, and outline the uniform with that same warm dark (never a key colour). Do NOT reuse the anchor (Baren)'s dark violet-navy outline and shadow colours (#474269, #2c2840, #28253c, #444061 ...) on this sheet: they are within the snap distance of the outfit keys, so the game would recolour every outline and shadow with the faction colour. Match the anchor's outline WEIGHT and placement, not its hue
  - anti-aliased, blended or compressed in-between shades of the keys are failures. A final palette pass that snaps every pixel of the uniform areas to its nearest key is allowed (figure only; never snap other parts or the background onto a key)
  - after export, run this check from the repository root (in a chat, run it on your PNG if you can run Python): python3 -c "from PIL import Image; import numpy as np; K=['263459','394b78','52679c','7489be','3f7a6c','5ea590','96d1bb']; k=np.array([[int(h[i:i+2],16) for i in (0,2,4)] for h in K]); a=np.asarray(Image.open('art/inbox/sheet_class_archer.png').convert('RGBA')).astype(int); p=a[...,:3][(a[...,3]>127)&(np.sqrt(((a[...,:3]-[255,0,255])**2).sum(-1))>=150)]; d=np.sqrt(((p[:,None,:]-k[None])**2).sum(-1)); m=d.min(1); print('exact key pixels:', {'#'+h: int((d[:,i]==0).sum()) for i,h in enumerate(K)}); print('near-key non-key pixels (distance 1-49, target 0):', int(((m>0)&(m<50)).sum()))" - it prints the pixel count of each exact key (each key you used > 0) and the near-key non-key pixels (target 0)

COLOURS of everything else (keep close, muted): eye strip warm-dark shadow #3a2e2a with at most two tiny eye glints - no skin visible (gloved hands, no skin anywhere); vest, bracers, quiver, bow warm browns; arrowheads NEUTRAL steel grey.

FROM concept.png (the owner's pick, NovelAI draft #10; design only) TAKE: the hood up with the face mask running down into a short cowl over the shoulders (hood, mask and cowl one cloth), long-sleeved knee-length tunic with a flared skirt, small brown leather bodice-vest with one diagonal strap, brown belt with pouches, long brown gloves / bracers, tall brown boots with turned-down cuffs, a quiver of arrows on the back.

FIX (do not reproduce the draft here):
  - the face stays covered / shadowed the SAME way in ALL FOUR poses: the visor, hood, mask, brim or veil never slips, opens or falls back, not even in the hit pose; the shadowed face is a warm or neutral dark (e.g. #3a2e2a), never blue and never a key colour
  - an arrow appears ONLY on the drawn bow in the wind-up; after the release (strike) there is NO flying arrow (the engine draws projectiles)
  - the leather vest stays brown and small, so the tunic underneath still shows clearly on the chest, sleeves and skirt
  - HEAD SIZE: the hood and the mask enclose the 110 px head (outer silhouette about 115-125 px from crown to chin); do not draw a 110 px head and then a bigger helm / hood around it, and do not enlarge the figure (this overrides "headgear is extra" in DELIVERABLE for this sheet)
  - the draft's slate-blue / teal / cyan cloth only marks WHERE the key colours go: repaint those areas with the exact KEY COLOURS ramps above (flat), never with the draft's own blues, teals or cyans
  - the draft face opening is a pure-black void with no eyes: a narrow warm-dark shadow strip at eye level (#3a2e2a family, at most two tiny eye glints); the mask still covers everything below the nose
  - the draft bow is a long bow whose string line breaks and crosses the body: a short recurve bow the size of the guide bow with ONE clean string; an arrow only on the drawn bow in the wind-up
  - the draft has no trim: accent keys on the hood's front edge and the tunic hem
  - the draft trousers are blue-purple grey: warm dark grey-brown (nothing blue outside the keys)

POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and fist-shaped hands are placeholders - follow the text for hands and weapon details):
  1. idle: bow held low in front, ready
  2. attack wind-up: full draw: arrow nocked, string pulled back to the cheek
  3. attack strike: release: bow arm extended, string straight, drawing hand flung back, no arrow
  4. hit reaction: torso thrown back, weight on the rear leg, head jerked back, hood and mask still in place; bow dropped low-forward, drawing hand flung back

REFERENCES (folder art/requests/phase3/class_archer/ on branch claude/dot-fantasy-management-game-saupju: https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3/class_archer ; in a chat they are the attached images):
  - art/inbox/sheet_captain_blademaster.png on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly - EXCEPT its dark violet-navy outline and shadow colours: on this sheet they would turn into key colours (use the warm dark ramp #2a2220 / #3a2e2a / #4a3a2e, see KEY COLOURS)
  - guide_strip.png (layout + poses + size: the most important reference)
  - guide_1_idle.png .. guide_4_hit.png (the same four poses, larger)
  - concept.png (DESIGN ONLY)

DO NOT COPY: from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail - the NovelAI drafts are not consistent with each other.

STYLE (same for every character):
  - high-quality HD pixel art for a modern 2D fantasy tactics game (crisp pixel clusters, no blur, no painterly rendering)
  - 4 heads tall (top of the hair to the chin = 1 head), exactly the proportions and limb lengths of the guide; NOT chibi, NOT realistic
  - front three-quarter view, facing RIGHT; light from the upper left
  - muted, desaturated, hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones
  - dark, desaturated, NON-black outline used selectively (no thick uniform black lineart), soft rim light on one side
  - readable at 1x game size (the idle figure becomes ~64 px tall on a dark battlefield): big clear shapes, strong silhouette, few tiny details

DELIVERABLE:
  - ONE PNG, 1536x1024 (landscape), the SAME character drawn 4 times in ONE row (1x4, never a 2x2 grid or a single pose), left to right: idle, wind-up, strike, hit
  - each figure exactly where guide_strip.png has it: same size, same scale, same position, same limb lengths
  - the lowest pixel of every figure (its soles) on the line y = 870 (85% of the height); head = 110 px for every character. Standing height would be 440 px (4 heads), but the guide idle pose is crouched, so the measured idle top-of-head to sole is about 401 px. Headgear (hats, helmets, plumes) and weapons are extra and not counted
  - at least 32 px of empty magenta between any two figures and between a figure and the image border (a weapon may reach over a neighbour's column as in the guide, but never closer than that)
  - background: perfectly flat solid magenta #FF00FF everywhere (preferred; a transparent PNG is also accepted) - no gradient, floor, cast shadow or scenery
  - NO figure pixel may be magenta-like: every colour of the figure must stay clearly away from the background key #FF00FF, RGB distance sqrt((255-R)^2 + G^2 + (255-B)^2) >= 150 (no hot pink, magenta or bright violet; purples stay dark blue-purple such as #5a4a7a). If you reduce the palette, reduce the FIGURE colours only and never merge a figure colour into the background colour
  - NO text, labels, numbers, frames, grid lines, watermark; NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles)

SELF-CHECK before saving (redraw if any fails):
  [ ] 1536x1024, background flat #FF00FF (or transparent), 4 figures in ONE row: idle / wind-up / strike / hit as in the guide
  [ ] soles of all four on y = 870; same size in all four; head ~110 px; idle ~401 px without headgear
  [ ] 4 heads tall; front three-quarter view facing right; light from the upper left
  [ ] same face, hair, outfit, colours and weapon in all four poses; exactly the weapons in CHARACTER (nothing extra)
  [ ] the uniform (the hooded tunic (hood, sleeves, skirt of the tunic) and the face mask) uses ONLY the four outfit keys and the trim (the hood's front edge and the tunic's hem trim) ONLY the three accent keys, exact hex, flat; the seven keys appear nowhere else and nothing else on the figure is blue, slate, teal or mint; every other figure colour (outline and shadows included) is at RGB distance >= 50 from all seven keys: the key check prints 0 near-key pixels
  [ ] every FIX applied
  [ ] no text, floor, shadow, effects or projectiles; >= 32 px of magenta between figures and from the border
  [ ] no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)
  [ ] reads clearly when shrunk to 64 px tall on a dark background
```

## 주인용 요약 (한국어)

- 순서: 일반 병과 **2번째** (메시지 D, 대장 9명 다음) — 승인된 바렌 그림(`art-inbox` 브랜치의 `art/inbox/sheet_captain_blademaster.png`)의 화풍에 맞춘다.
- **얼굴 가림** (주인 요청): 이 그림 한 장을 서로 다른 여러 사람이 같이 쓰므로 얼굴이 가려지는 복장 — 궁수는 후드 + 코 아래를 가린 천 마스크. 네 자세 모두 같은 만큼 가린다(피격 때도 벗겨지지 않음). 가려진 얼굴 그늘은 따뜻하거나 중성인 어두운 색(파랑·열쇠 색 금지). 상급·최상급 직업은 어울릴 때만, 억지로 하지 않는다.
- **열쇠 색** (전투에서 진영 색으로 바뀐다): 제복 `#263459` `#394b78` `#52679c` `#7489be`, 장식 `#3f7a6c` `#5ea590` `#96d1bb` — 이 7색은 그 자리에만, 평평하게. 다른 곳에는 파랑·청회색·청록을 쓰지 않는다.
- **열쇠 색 거리**: 열쇠 색이 아닌 모든 색(외곽선·그늘 포함)은 7색 모두와 RGB 거리 50 이상 — `sheets.py`는 거리 34 안을 열쇠 색으로 붙인다. 바렌의 남보라 외곽선·그늘(#474269 등)은 그 안이라 쓰지 않고 따뜻한 어둠 `#2a2220` / `#3a2e2a` / `#4a3a2e`을 쓴다. 영어 블록 KEY COLOURS 의 확인 한 줄이 열쇠 색별 픽셀 수와 「열쇠 색 근처 픽셀」(목표 0)을 센다.
- **머리 크기**: 투구·후드·두건·모자 챙과 깃이 110px 머리를 감싼다(바깥 실루엣 약 115~125px). 머리 110px 위에 더 큰 투구를 씌워 인물을 키우지 않는다.
- 결과 파일: `art/inbox/sheet_class_archer.png` (id `sheet/class/archer`)
- 무기: posekit `bow` 마네킹 → a short recurve bow the size of the guide bow (brown wood), a brown leather quiver of arrows on the back
- 자세(가이드 프레임): ① 대기 `idle_0` ② 공격 준비 `attack_2` ③ 공격 타격 `attack_3` ④ 피격 `key_hit` (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)
- 초안에서 가져올 것: 후드를 쓰고 천 마스크로 코 아래를 가린 얼굴(눈 둘레만 그늘 속에), 무릎 길이 후드 상의(제복), 갈색 가죽 조끼·팔 보호대, 등의 화살통, 짧은 활.
- 고칠 것: 후드 상의·마스크 = 제복 열쇠 색, 후드 앞 가장자리·상의 밑단 = 장식 열쇠 색. 화살은 당길 때만, 쏜 뒤에는 없음.
- **초안** `concept.png` = `art/concepts/class_archer/concept_10.png` (주인이 고른 #10, 디자인만) — 가져올 것: 후드와 마스크가 어깨의 짧은 두건 망토로 이어지는 한 장의 천, 긴 소매 무릎 길이 상의(밑자락 퍼짐), 대각선 띠 하나 있는 작은 가죽 조끼, 주머니 달린 갈색 띠, 긴 갈색 장갑, 끝단 접힌 갈색 장화, 등의 화살통.
- **초안에서 고칠 것** (영어 블록 FIX 끝부분): 초안의 청회색은 열쇠 색 자리 표시 → 정확한 열쇠 색. 눈 없는 새까만 얼굴 구멍 → 눈높이의 좁은 따뜻한 어둠(눈빛 두 점까지), 코 아래는 마스크. 긴 활·끊긴 시위 → 가이드 크기 짧은 활, 시위 하나. 후드 앞 가장자리·상의 밑단에 장식 열쇠 색 추가. 청보라 바지 → 따뜻한 짙은 회갈색.
- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.
- 가이드 띠: 머리 하나 = 110 px (모든 캐릭터 같음). 선 키라면 440 px 이지만 대기 자세가 웅크려서 정수리~발바닥 약 401 px(높이의 39%). 모자·투구·깃털·무기는 따로. 발바닥(맨 아래 픽셀) y=870.

### 파일 (ChatGPT 웹이면 이 순서로 첨부)

| 파일 | 내용 |
|---|---|
| (`art-inbox`의 `art/inbox/sheet_captain_blademaster.png`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |
| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |
| `guide_1_idle.png` | 자세 가이드 832x1216 — 대기 |
| `guide_2_windup.png` | 자세 가이드 832x1216 — 공격 준비 |
| `guide_3_strike.png` | 자세 가이드 832x1216 — 공격 타격 |
| `guide_4_hit.png` | 자세 가이드 832x1216 — 피격 |
| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |

### 받은 뒤 (Claude Code)

```
python3 tools/art/sheets.py art/inbox/sheet_class_archer.png --dry-run --work /tmp/sheets   # 미리보기
python3 tools/art/sheets.py art/inbox/sheet_class_archer.png                                 # 등록
```
