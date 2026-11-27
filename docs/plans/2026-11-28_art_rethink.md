# 그래픽 제작 방식 재검토 (2026-11-28)
주인 요청: 「이 방식으로는 그래픽 작업에 너무 많은 리소스가 들어갈 것 같아서 다른 방법을 고민해보고 싶어」. 측정 → 대안 5개 설계 → 세 관점 평가 → 종합. 결정 전까지 그림 납품은 보류(`dot_queue.md` ⏸).

## 주인 결정 (2026-11-28)

1. **가상의 3D 마네킹**을 만들어 동작을 따내고 스프라이트 시트로 만들어 그림을 입힌다.
2. 주인이 **견본 스프라이트 시트**를 구해 오면 그것을 바탕으로 단순화한 뒤 그림을 입힌다 — 하더라도 일부 동작만.
3. **색 바꾸기는 절대 인정하지 않는다.** 세력 표시용으로 게임 안에서 적용되는 것은 괜찮지만, 에셋 단계에서는 존재하면 안 된다. → 아래 추천의 「색 바꾸기·장식 변형」안은 기각.

## 종합 (추천 — 위 결정 전의 안)

PART A — Lead planner recommendation (English)

## 1. Ranked options (mean of the 3 judges: cost / quality / feasibility)

| Rank | Approach | Scores | Mean | Verdict |
|---|---|---|---|---|
| 1 | 4. Scope cut: drawn motion only where it is on screen, plus recolour/overlay variants for the rest | 8.5 / 8 / 8 | **8.2** | Adopt as the backbone |
| 2 | 5. 34 px field figures + big VFX + cut-ins | 6.5 / 4 / 5 | 5.2 | Don't adopt as a cost measure. Take only the cut-in freeze (optional). A 34 px A/B branch is possible later, as a readability redesign |
| 3 | 2. Native-res legs-only run rig per gait class | 5.5 / 4 / 4 | 4.5 | Shelve. It is the fallback only if the owner rejects gliding captains, and then time-boxed to heroes |
| 4 | 1. Paper-doll bodies + part libraries | 4.5 / 4 / 3 | 3.8 | Defer. It only pays if the owner later wants 15+ distinct generic units with motion |
| 5 | 3. Blender 3D-to-pixel | 3 / 2 / 3 | 2.7 | Reject for shipped pixels (toy-like idle/attack, conflicts with "final art by Antigravity"). Underpainting guides remain a possible later experiment |

Why 4 wins:
- It is the only option that leaves every approved pixel unchanged.
- It needs 0 engine lines: Art.sheetFor (js/art.js L98-114) already resolves master → adv → class → monster ids.
- Its cost numbers come from measured rates.
- Every step is reversible: held rows can be un-held, and audited request folders stay on disk.

Core fact behind it:
- Captains + heroes are 4.7% of the units on the field (0-2 per battle), yet they are 38 of the 43 queued rows.
- Classes are 48.8% of units and already run. Monster sheets are 40.1%.
- Run cells are 12-15% of screen time, and at 2x/4x the individual poses can't be told apart.

## 2. Recommended combination

1. **Scope cut (approach 4), now, at no cost:**
   - Move the 38 captain/hero run rows to 보류(범위 밖). Keep their folders.
   - Keep the 3 already-audited high-share humanoid monster runs: skeleton soldier (14.8% of units), bandit, desert bandit. Goblin and frost troll are optional.
   - Park the whole attack/hit expansion, including the 5-class part, until gate 1 can be passed cheaply. The pilot has spent 6.8M tokens and drawn 0 frames. The quality judge would keep the 5-class part, so this goes to the owner as Q3.
2. **Variants for the 19 enemies that have no sheet:**
   - Codex writes tools/art/variant.py (about 400 lines): recolour (hue band / colorize / explicit map), plus an overlay composite through the base's own sheets.py/add_gait parameters, plus delta paste, plus provenance fields.
   - Recolour-only candidates: 숲 트롤 and 지옥견.
   - Overlays are approved only after the one-pilot test in section 4. Any failure falls back to a new 1x4 sheet, which is proven at 1.6-2.2 deliveries.
3. **Quality amendments:**
   - The final boss (마왕 베르녹스) and 고룡 이그니스 get unique sheets.
   - The yeti gets its own sheet (the troll recolour reads as a "white troll").
   - Regional bosses become crown-overlay variants only if the goblin-king pilot reads as a boss at 1x. Otherwise they get unique sheets (about +2.2 deliveries each).
4. **Process overhead cuts:**
   - batched registration commits;
   - one GPT-QA task per 4-6 items;
   - no measured-box audits for variants;
   - far less dot_queue/queue.md churn (139 and 127 commits this week).
5. **Optional (engine-only, no art risk):**
   - The approach-5 cut-in freeze: about 0.5 s view.stop at x1 while a captain or hero special plays. It puts the hand-drawn identity art on screen at the moment that matters and offsets the gliding contrast.
   - It needs a replay-hash check.
6. **Expected result:**
   - About 30-50 Antigravity deliveries (about 60-65 with the unique bosses), about 4-5M new workflow tokens, about 15-20 GPT-QA tasks.
   - About 1-1.5 calendar weeks to a complete enemy roster.
   - The current plan for comparison: about 275 deliveries, 13M+ tokens, about 110 QA tasks, 3-4.5 weeks.
   - A new character afterwards costs about 1.6 deliveries and 0.23M tokens (base sheet, no run). A variant costs about 30-50k tokens.

## 3. Existing assets

- **55 registered sheets:** untouched, all stay registered, no re-derivation.
- **7 drawn runs** (5 classes, ironwall, shadowqueen): keep as they are.
- **43 queued Antigravity rows:** the hold stays. Then:
  - Un-hold and prioritise the skeleton soldier, bandit and desert bandit runs (requests already audited: about 5 deliveries plus registration and QA).
  - Goblin and frost troll runs: optional. Default: hold.
  - 31 captain + 7 hero runs: 보류(범위 밖) with their reason. art/requests/gait/* folders stay as an archive (about 5.5M tokens sunk). The natural first re-activation candidates are the 8 starter captains, about +14 deliveries, if the owner dislikes gliding.
  - Rewrite 「지금 차례」 in the same commit as the decision, so Antigravity cannot pick up old rows.
- **Attack/hit pilot** (guide/atk__*, hit__*): park. The accepted mannequins stay as stance references.
- **Walk:** stays dropped.
- **Base-sheet backlog:**
  - 6 truly new monster sheets (전갈 거인, 마족 전사, 늪 슬라임, 미믹, 와이번, 고룡 이그니스), plus the yeti and 마왕, plus the Marisol redraw, go on today's 1x4 pipeline, one at a time with an idle check.
  - The other enemies become variants, depending on the pilot.
- Nothing is edited until the owner answers Q1-Q3.

## 4. First prototype (2 days, scratch/branch only, nothing on main)

**Day 1: cloud + Codex, no Antigravity time**
- **Codex:**
  - Promote /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/scopecut/recolor_probe.py into a scratch variant.py recolour mode.
  - Output 숲 트롤 (from 서리 트롤) and 지옥견 (from 들늑대). Existing drafts: forest-troll.png and hellhound.png in the same folder.
- **Codex (reproducibility check):**
  - Run sheets.py --dry-run on origin/art-inbox sheet_monster_goblin.png and sheet_class_warrior.png with their phase3.json parameters.
  - Pixel-diff the result against the registered sheets. A diff of 0 means a full re-run works; otherwise use delta paste.
- **Cloud lead:**
  - Build a scratch manifest copy with the 2 recolours.
  - Record a battle capture at 1x and 4x (desktop width plus 360 px width) in which captain ironwall (drawn run) and captain blademaster (glide) move among running class soldiers.
  - Put everything on one owner A/B page.
- **Optional:** the cut-in freeze on a throwaway branch, with `node tools/sim/battle.js 100` confirming the replay hash still equals the judged hash.

**Day 2: Antigravity, one row**
- The owner lifts the hold for this one row only.
- Row: `variant/monster_goblin-king`, crown + cape on the 4 goblin poses, drawn on the original large source. Delivered as art/inbox/variant/monster_goblin-king.aseprite plus an overlay PNG.
- variant.py composites it, re-downscales it at 1.5x for boss scale, and runs the C25 seam check.
- Log Antigravity time and the number of deliveries.
- **GPT-QA:** one batched in-game check of the 3 variants plus the glide capture.

**Success criteria the owner judges by eye:**
1. In the 1x capture, the gliding captain does not bother him next to running soldiers.
2. The forest troll and hellhound look like their own monsters at game size, not "the same monster in another colour".
3. The goblin king reads as a boss at 1x, not "a goblin wearing a hat". The crown does not flicker and has no outline halo.

**Technical gates (lead/QA):**
- Overlay accepted in 2 deliveries or fewer.
- Base pixels outside the overlay footprint unchanged.
- No delta-paste halo; seam check clean.

**Kill/fallback:**
- Overlay fails → those enemies become new 1x4 sheets (about +29 deliveries, still about 1/4 of the current plan).
- Glide rejected → re-activate the 8 starter-captain runs.

## 5. Owner decision questions

**Q1. Captains and heroes moving without drawn run frames (glide, as 48 of 55 sheets do today)**
- (a) Accept glide for all captains and heroes. **[recommended]**
- (b) Glide, but draw runs for the 7 heroes only (about +12 deliveries).
- (c) Glide, but draw runs for the 7 heroes plus the 8 starter captains (about +26 deliveries).
- (d) Keep all 38 runs (current plan, about 1-1.5 extra weeks).

**Q2. Do tool-made variants of Antigravity art count as final art (recolour, accessory overlay)?** Precedent: faction soldier recolours already ship.
- (a) Yes, for both recolours and overlays. **[recommended]**
- (b) Recolours only; every new look is a new drawing.
- (c) No; every enemy gets its own sheet (about +29 deliveries).

**Q3. Attack/hit frame expansion (owner plan 11-26)**
- (a) Park it entirely; keep today's 2 attack + 1 hit frames for everyone. Revisit after the roster is complete. **[recommended]**
- (b) Only the 5 base classes, after gate 1 passes (about 12 deliveries, 2-3 days).
- (c) Full plan for 45 humans and 29 monsters (12-18 days).

---

PART B — 사장님께 (한국어)

**지금 얼마나 들고 있나요**
- 이번 주 커밋 507개 중 절반(247개)이 그림 작업이었습니다. 자동화 작업량(토큰)의 77%(3,670만)도 그림에 들어갔습니다.
- 달리기 동작은 33시간 동안 7명분만 끝났습니다. 그중 5명분(71%)은 다리 잘림 같은 문제로 다시 그려야 했습니다.
- 지금 계획(달리기 43명분, 공격·피격 동작 확장, 새 몬스터)을 다 하려면 Antigravity가 3~4.5주 동안 쉬지 않고 그려야 합니다. 납품은 약 275번입니다.

**측정해 보니 알게 된 것**
- 달리기 장면은 전투 시간의 12~15%뿐입니다. 2배속·4배속에서는 동작 하나하나가 눈에 거의 들어오지 않습니다.
- 대장·영웅은 전장에 나온 유닛의 4.7%뿐입니다. 그런데 대기 중인 43건 가운데 38건이 대장·영웅의 달리기입니다.

**선택지 3가지**
1. 범위 줄이기 (추천)
   - 그림을 새로 그리는 건 자주 보이는 병사·몬스터에만 합니다. 대장·영웅은 지금처럼 그림 그대로 미끄러지듯 이동합니다. 없는 몬스터는 기존 그림에 색만 바꾸거나 왕관 같은 장식만 얹어 만듭니다.
   - 장점: 비용이 지금 계획의 1/5 정도(1~1.5주)입니다. 이미 받은 그림은 하나도 바뀌지 않습니다.
   - 단점: 1배속에서는 뛰는 병사 옆에서 대장이 미끄러져 보일 수 있습니다.
2. 부품 조립·공용 다리
   - 몸통·머리·무기를 따로 그려서 조립하거나, 다리 동작 하나를 여러 캐릭터가 같이 씁니다.
   - 장점: 나중에 캐릭터를 늘리기 쉽습니다.
   - 단점: 이음새가 생길 위험이 큽니다. 11-26에 거절하신 "잘라 붙인 달리기"와 비슷해 보일 수 있습니다.
3. 전장 캐릭터를 절반 크기로 줄이기
   - 장점: 큰 전투에서 진형이 훨씬 잘 보이고, 그림 비용이 크게 줄어듭니다.
   - 단점: 방금 보신 얼굴·장식 같은 디테일이 거의 사라집니다. 휴대폰에서는 아주 작게 보입니다.

(3D 렌더링도 실제로 해봤지만, 장난감처럼 보여서 제외했습니다.)

**추천**
- 1번으로 갑니다. 이미 끝난 55장의 그림과 7개의 달리기는 그대로 둡니다.
- 대기 중인 43건은 지울지 결정하지 않고 보류만 합니다. 언제든 다시 살릴 수 있습니다.
- 해골 병사·산적·사막 도적처럼 자주 나오는 몬스터 3종의 달리기만 먼저 진행합니다.

**먼저 보여드릴 것 (2일)**
1. 뛰는 병사들 사이에서 대장이 미끄러지듯 이동하는 전투 영상 (1배속·4배속)
2. 색만 바꿔 만든 숲 트롤과 지옥견
3. 고블린에 왕관과 망토를 얹은 '고블린 왕' 시험작 1개

보시고 "어색하다/괜찮다"만 말씀해 주시면 됩니다. 그 전에 세 가지만 골라 주세요.
- 대장·영웅 달리기를 생략해도 될지
- 색 변경·장식으로 만든 그림도 정식 그림으로 인정할지
- 공격·피격 동작 확장을 미룰지

## 측정: 비용

COST AUDIT: current art pipeline (base sheet + drawn 8-frame run per character)
All times are UTC. Repo timestamps mix +0000 and +0900, so everything was normalised with `TZ=UTC git log --date=format-local`. Scratch data is in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/cost/ (main_raw.txt, inbox_raw.txt, workflows.csv, chars.py). No repo files were edited.

## 1. Where the effort went this week (11-24 to 11-27)
- **Main branch:** 507 commits. 247 of them touch art/assets/art/tools/art/tools/pixelart (49%), and 133 are motion-specific (gait, run, mannequin or guide files).
  - Per day, art-touching / all: 11-24 43/62, 11-25 100/116, 11-26 73/128, 11-27 31/191.
  - Bookkeeping churn: dot_queue.md changed in 139 commits, docs/agents/queue.md in 127.
- **origin/art-inbox:** 136 commits (allycat92/GPT-PC 89, Antigravity 17, Baeklang Kim 13, Claude 17).
- **Cloud workflows** (source: ~/.claude/projects/-home-user-pixel-management/e0835d66-…/workflows/wf_*.json, field totalTokens): 61 runs, 47.6M tokens.

| Category | Workflows | Tokens | Wall time | Share |
|---|---|---|---|---|
| Base-sheet pipeline (phase3 handoff, captain packages, reviews, registration, sprite-gen vetting, aseprite-mcp kit) | 16 | 12.7M | 7.1h | |
| Motion: run/gait setup and engine | 8 | 6.9M | | |
| Motion: attack/hit frame pilot (mannequins, motion bible) | 8 | 6.8M | | |
| Motion: mixed reviews (animation-and-collab-review, review-anim-and-tools-diff, sprite-forge-audit) | 3 | 3.3M | | |
| Motion: run requests (generator plus image audits) | 8 | 7.0M | 2.2h | |
| **Art total** | **43** | **36.7M** | | **77%** |
| Game code, everything else | 17 | 10.9M | 20.8h | |

- The attack/hit pilot has produced **zero drawn frames** so far. Its mannequins are accepted but still waiting for gate 1 (dot_queue `guide/atk__*`, `hit__*` "첫 관문 대기").
- The main-session transcript (cache reads 18–441M per day) is not split by topic, so it is left out of these numbers. The real cost is higher.
- **Helper agents:** 16 of the 51 task IDs in docs/agents/queue.md are art.
  - Codex/GPT: C5, C8, C9, C10, C15, C17, C25 (seam checker), C26.
  - GPT-QA: Q2, Q3, Q10, Q12, Q15, Q17, Q21, Q22.

## 2. Tooling written just for art (current line counts)
| Area | Lines | Files |
|---|---|---|
| tools/art | 15,574 | |
| – motion-specific | ~11,084 (incl. pixelart gait files and gait_probe) | gait_requests 1,557, add_gait 1,088, check_skeleton 2,003, gate_page 673, run_request_guides 504, check_delivery 605, receive 1,015, specs motion_bible 1,702 / motion_chars 277 / gait_classes 406 |
| – base-sheet | ~5,744 | sheets 1,253, handoff 1,850, requests.js 1,230, captains_batch2.json 591, others |
| tools/pixelart | 3,515 | posekit 1,227; run8/walk8/gait8/lua 1,043; baren/baren_hd 1,166 (procedural experiments) |
| tools/sim/gait_probe.js | 211 | |
| js/gait_classes.js | 133 | |
| tools/aseprite-mcp + tools/aseprite notes | 893 | |

- tools/art, tools/pixelart and gait_probe changed in 114 commits. Several tools have 14–17 revisions each.
- Request artefacts: art/requests holds 878 files (85 MB) and 15,031 lines of .md.
  - gait/: 22 MB, 255 files, 51 request folders (README of about 111 lines plus 4 guide PNGs each).
- Sunk work that was thrown away: walk_base v1/v2 (3 PC rounds plus cross-checks 2 and 3) was dropped when the owner chose run-only on 11-26.

## 3. Per character: base sheet (1x4 key poses)
- 55 sheets registered: captains 33, heroes 7, classes 5, monsters 10.
- 89 inbox deliveries in total, so **1.6 deliveries per accepted sheet**:
  - captains 47/33 = 1.4
  - classes 7/5
  - heroes 13/7 (Antigravity touch-ups)
  - monsters 22/10 = 2.2
- Outliers:
  - Beastmaster: 5 deliveries.
  - Shadowqueen: 4.
  - Desert bandit: 4.
  - Giant spider: 3 deliveries plus an idle check, and 10 request commits.
  - Liberator: idle check, then a quota block (Antigravity image-generator HTTP 429, about 4h reset; art-inbox 4c94300), then the chain sheet roughly 16h after the idle check.
- **GPT era speed:** request to registration usually under 1h (e.g. windhunter: request 13:06, delivered 13:15, registered 13:16 on 11-25). 24 captain sheets were delivered between 13:15 and 22:16 on 11-25, about 2.7 sheets per hour.
- **Workflow cost:** about 0.23M tokens per base sheet (12.7M / 55).

## 4. Per character: drawn run (8 frames over a mannequin)
Seven runs are done. "Request" is when the request was queued.

| Sheet | Class | Request | 1st delivery | Final accept | Deliveries | Fix |
|---|---|---|---|---|---|---|
| class warrior | light | 11-26 05:56 | 06:10 | 08:13 (9da6a32) | 2 | R5 planted foot (cloud) |
| captain shadowqueen | light | 05:56 | 06:11 | 08:13 | 1 | – |
| captain ironwall | heavy | 11-26 23:46 (d01dfa5) | 11-27 05:43 | 06:27 (59ed90e) | 2 | Q12: mace buried, H3/H7 legs merged |
| class mage | robe | 23:46 | 06:05 | 06:27 | 2 | Q12: G3/G7 boots |
| class archer | light | 23:46 | 09:31 | 09:33 | 1 | Q15 start-step slip, fixed in engine (run-start-foot-slip workflow, 0.45M) |
| class cleric | light | 23:46 | 10:24 | 13:32 (f279efd) | 2 | Q17: tabard vanishes R5–R8, mace by face |
| class rogue | light | 23:46 | 14:14 | 15:08 (1e0845d) | 2 | Owner spotted leg seam R4/R8 → registration pulled (d7b296b), C25 seam tool written |

- **Fix rate:** 5 of 7 runs (71%) needed a fix round, 1.7 deliveries per accepted run. Only one of those fixes was caught by the cloud. GPT in-game QA caught three and the owner caught one.
- **Calendar time per run:** 2.3h for the pilot pair. In the Antigravity queue it was 6.7h, 6.7h, 9.8h, 13.8h and 15.4h, because items wait in a serial queue.
- **Throughput:**
  - Overall: 7 runs in 33.4h, about 5 per day.
  - Antigravity steady state: 5 runs plus 3 fixes in 9.4h (11-27 05:43–15:06), but it hits about 4h quota stops.
  - 5 GPT-QA tasks for 7 runs.
- **Request generation and audit:** 48 run requests written (first 5 plus C8 10, C9 9, Björn 1, C15 14, C17 3, C26 6).
  - Six image-audit workflows cost 5.88M tokens, about **0.98M per batch and 137k per request**.
  - Generator build (art-queue-refill plus gait-requests-finish) cost 1.09M.
  - Audits found about 82 corrections in 48 requests, about 1.7 per request, even after the generator (commits a5eff5d 12, 0727ee5 16, 06893d7 ~5, 4805a57 31, 37f23ef ~3, 3332649 11, Q3 4).
- **Motion workflow cost so far: 24.0M tokens for 7 accepted runs (3.4M per finished run, mostly setup).** Marginal cost is about 145k per request in workflows, plus registration and QA work that is not measured.

## 5. What is left in the current plan (sources: dot_queue.md, js/content.js ENEMIES, docs/plans/2026-11-26_motion_frames.md §12)
| Work | Count | Notes |
|---|---|---|
| A. Run requests queued for Antigravity | 43 | Requests already written and audited (sunk) |
| B. New base sheets | 20 | 19 enemy types of 29 have no sheet (7 of them bosses), plus the Marisol redraw. Monsters need an idle check one at a time. About 10 are humanoid and would also need a run, so about 10 more run requests |
| C. Attack/hit frames (owner decision 11-26) | see notes | 45 humans × 2 key strips ≈ 90 strips, plus 4–7 PC in-betweens per character, plus one attack mannequin set per character (~13 base frames plus overrides). Monsters 29 × ~3 ≈ 87 strips. Nothing delivered yet |
| Walk | 0 | Owner dropped walk on 11-26 (dot_queue question 1) |

## 6. Projection at the observed rates
- **A. 43 runs:**
  - about 74 Antigravity deliveries (1.7 each) and about 31 fix rounds (71%)
  - about 31 GPT-QA tasks and about 74 registration commits
  - **5.4–8.6 days** of Antigravity time (5–8 runs per day)
- **B. 20 base sheets plus about 10 runs:**
  - about 44 deliveries (monster rate 2.2)
  - request and audit about 10 × 145k ≈ 1.5M tokens, plus concept packages (about 30–70k per sheet in past workflows)
  - **about 3–5 days**, because monsters go one at a time and the quota stops apply
- **C. Attack/hit sets:** each character is about 1.4 run-equivalents (11 frames vs 8, plus its own mannequin).
  - 45 × 1.4 ≈ 63 units for humans, plus about 29 for monsters ≈ 92 units
  - about 155 deliveries, about 65 fix rounds and about 65 QA tasks
  - request and audit about 74 × 145k ≈ 10.7M tokens
  - **12–18 days**
  - This assumes gate 1 passes. The attack/hit pilot has already used 6.8M tokens with zero frames drawn.
- **Total:** about 165 run-equivalent units, against 7 finished in the first 33h.
  - About 270–280 Antigravity deliveries, about 115 fix rounds, about 110 GPT-QA tasks and about 200 registration commits.
  - Roughly 13M+ new workflow tokens for requests and audits alone, plus unmeasured main-session time.
  - **About 3–4.5 weeks of continuous Antigravity work.**
- **Comparison:** this week delivered 55 base sheets and 7 runs and used 36.7M art workflow tokens, 77% of all workflow spend.

## 7. Cost drivers the data points to
1. Every character needs its own audited request. Audits still find about 1.7 errors each, at about 137k tokens per request.
2. 71% of drawn runs need a fix round, and most defects are caught by GPT QA or the owner, not by the tools. Each defect class has led to new tooling (seam checker C25, a foot-slip engine fix).
3. Antigravity is the only artist: work is serialised, it hits about 4h image-quota stops, and it sat idle once because nothing was queued (art-queue-refill workflow).
4. Motion setup has been rebuilt several times (walk → run → light/heavy/robe classes → attack/hit pilot), at about 17M tokens before the per-character work is even counted.


## 측정: 엔진이 필요로 하는 것

ENGINE NEEDS INVENTORY (pixel-management, read-only; no repo files changed)

1. Which frames the engine reads per battle unit (js/art.js, js/battle.js pose() ~L1689)
- Sheet format (manifest `sheet`): cell [w,h], anchor [x,y] (feet), facing, frames[[x,y]], anims{name:{from,to,ms[]}}, optional tint{outfit,accent}, runStride/walkStride, gait.
- Anims the engine actually uses:
  - idle: 4 frames, 240 ms each. It loops on real time, so it does not speed up with the replay speed.
  - attack: 2 frames (wind-up 150 ms, strike 260 ms). The length is stretched to 0.28-0.5 s. The wind-up frame is also shown about 0.1 s before a melee hit lands.
  - hit: 1 frame (220 ms).
  - run: optional, 8 cells (R1-R4 + R5-R8). Cells advance by distance travelled, not by clock (runCells, runStride).
  - walk: optional. The engine supports it, but no sheet has it yet (0 of 55).
- Fallbacks in Art.anim:
  - cast → attack (all spell and heal casts reuse the attack frames).
  - walk, attack or hit missing → idle.
  - die → hit. A dead unit is drawn as the last hit frame, blinks, then sinks and fades over about 1.4 s.
- When a unit moves without drawn cells (reseat/step/back/trudge, or a sheet with no run), the idle frame slides. For walking gaits a small vertical bob is added; for run gaits it is wbob 0. There is no deformation (owner rule 11-26).
- So the minimum game-ready character is 7 cells: 4 idle + 2 attack + 1 hit. The 8 run cells are the only optional extra.
- Manifest today:
  - 55 sheets: 47 with 96px cells, 8 with 112px cells.
  - 48 have only idle/attack/hit.
  - 7 also have run: 5 classes, plus captains ironwall and shadowqueen. runStride is 45.5 (light), 23.6 (heavy) or 22.2 (robe).

2. On-screen size
- The canvas is 640x360 (sim 320x180 × Z=2). Sheets are drawn 1:1 (sheetK=1); monster bosses that have a sheet are drawn 1.5x.
- .battle-stage has max-width 644px (css/style.css:635), so on desktop 1 canvas px is about 1 CSS px (2 device px on HiDPI). On a 360-wide phone it is about 0.55x.
- Measured opaque bounding box of idle frame 0 across all 55 sheets:
  - Humanoids: 63-79 px tall, median 69 (weapon included). The engine comment says a warrior is about 66 px. Width about 40-65 px.
  - Wolf/spider: about 41 px tall, 69-89 px wide.
- At that height the head is about 15-18 px and the legs about 25-30 px.
- The image agent draws a 384x1024 frame (head 110 px). It is downscaled 0.1654, so about 97% of the drawn pixels are discarded.
- Units on the field: average 19.4, max 24 (tools/sim/battle.js, 40 reports). Battles last about 19-30 s of sim time.

3. Are 8-frame drawn runs perceptible?
I measured this with a scratch copy of tools/sim/gait_probe.js: 6 bot battles, 60 fps, all units given the archer, ironwall or mage sheet.

| Replay speed | Alive unit-time in run cells | Median run episode (p90) | Median time each run cell is on screen |
|---|---|---|---|
| 1x | ~15% | 0.63 s (2.7 s) | light 150 ms, heavy/robe 83 ms |
| 2x | ~14% | 0.35 s (1.4 s) | 50-67 ms |
| 4x | ~12% | 0.30 s (0.87 s) | 33-50 ms (2-3 display frames) |

- At 1x the median episode is about 4 cells, i.e. one step. Only the p90 episodes show the full 8-cell cycle.
- At 4x the median episode is about 6-9 cells' worth of display frames at 33-50 ms per cell, roughly one 8-cell cycle at most. Cells change every 2-3 display frames on a ~66 px figure with ~25 px legs, in a scrum of about 20 units.
- Elsewhere in alive unit-time: idle about 46%, attack 22-34%, hit 9-13%, sliding idle about 7%. Attack and idle carry far more screen time than run.
- My judgement (an inference, not a user test):
  - At 1x, run cells read as running, and pose quality is visible only in the longer approach runs.
  - At 2x and 4x, individual R1-R8 poses cannot be told apart. What reads is "legs alternate plus a bob", so a 4-cell or even a good 2-cell cycle would look nearly the same.
  - Seam and foot-slip precision below about 2 px is invisible at 4x.

4. Distinct unit types that can appear in battle

| Group | Types | Have own sheet | Notes |
|---|---|---|---|
| Unit classes | 35 (5 base, 10 adv, 20 master) | 5 base only | See class/tier mapping below |
| Captains | 33 | 33 | |
| Heroes | 7 | 7 | gait_classes.js hero_class_to_sheet |
| Enemies (js/content.js ENEMIES) | 28 (incl. 7 boss-flagged) | 10 | No sheet for 고블린 왕, 거미 여왕, 늪의 마녀, 모래 폭군, 서리 거인 왕, 마왕 베르녹스, 고룡 이그니스, 숲 트롤, 오크, 설인, 늪 슬라임, 와이번, 리자드맨, 미믹, 마족 전사, 지옥견, 데스 나이트, 전갈 거인, 리치의 망령 |

- Distinct identities are about 103. 55 have sheets; the rest use procedural fallback.
- Gait class table: js/gait_classes.js (light/heavy/robe/none).

5. How classes and tiers map to sheets (Art.sheetFor)
- Lookup order:
  1. u.art (portrait id → sheet id)
  2. monster name
  3. capKey, then heroKey, then look.cap
  4. classes in order look.master → look.adv → u.cls → look.cls
- No sheet/class/<adv|master> exists, so every tier-2 and tier-3 unit reuses its base-class sheet (paladin → warrior sheet, etc.).
- Class sheets are shared by all factions and recoloured at runtime from tint keys (sheetRecolor + toneRamp). Faction soldiers use base classes only (js/world.js soldier.classes).
- Rule: a unit with look.tint uses a class sheet only if the sheet has tint keys. All 5 class sheets do; without them the unit would fall back to procedural.
- Captain, hero and monster sheets are never recoloured.

6. Fallback when no sheet exists (js/sprites.js)
- Humans: Sprites.merc is a code-generated 16x16 chibi from a template:
  - recoloured by look (skin, hair, outfit, accent, headgear, weapon);
  - 2 frames (idle 2, walk 2), no attack/hit frames;
  - drawn at SPR=3 → 48x48, about 42 px body.
- Monsters: Sprites.monster uses 9 16x16 templates (imp/beast/bug/brute/slime/ghost/drake/chest/demon) × palette, 2 frames, scale 3 / 5 (big) / 7 (boss). A boss is about 112 px.
- So the fallback is visibly smaller and cruder than the 66-70 px sheets. The same Sprites output is used for all non-battle UI (portrait fallbacks, guild scene, minis), which needs no new art.

7. tools/pixelart: can it already produce game-ready characters?

| Tool | What it is | Game-ready? |
|---|---|---|
| baren.py (284 lines) | One hard-coded character (Baren/검귀), 40x48, idle 4 / walk 4 / attack 5 / hit 1, mask shapes + auto outline/shading, runs in 0.2 s | No. Chibi and too small. |
| baren_hd.py (882 lines, "work in progress") | One hard-coded character, 80x80 (feet y=76, body ~65 px), same 14 frames. IK skeleton, pseudo-normal lighting, hue-shifted ramps, rim light, selective outline, cape folds, slash smear. Runs in 0.9 s | Closest to game-ready (see below) |
| posekit.py (1227 lines) | Generic 4-head mannequin guides (832x1216 + 80x80 preview + OpenPose stick) for idle/walk/attack/hit/cast, weapons katana/sword_shield/spear/staff/bow/none, exact bone lengths and IK. README says procedural shading "is not good enough for final art" | No: guides only. Per-class/body-type kits are deferred. |
| run8.py / walk8.py / gait8.py (heavy/robe) | 8-frame mannequin skeletons (384x1024/frame, floor y=870) + pose.json + layers/.aseprite | No: pose guides only. Mannequins are refused as deliveries by receive.py. |

baren_hd.py in detail:
- In a scratch side-by-side at game scale it reads at roughly the same size and density as the shipped Antigravity sheets.
- It is a one-off: the head template, palette RAMP, cape, headband and frame pose tables are all specific to Baren.
- There is no parameterisation for other characters, classes or body types, and no run cells.
- It shows the technique works at 80px. Generalising it would need a parametric body/costume/weapon/palette system (a new tool, Codex-sized).
- Under owner policy it would be our own code, which is allowed.
- Owner rules still apply: final art belongs to Antigravity, so a procedural or mannequin-derived output would need an owner decision to ship.

8. Takeaways for the "other methods" discussion (facts above, my reading here)
- The engine needs only 7 cells per character, read at about 66 px, plus optional run cells.
- Run cells account for about 12-15% of screen time, and are mostly unreadable at 2x/4x.
- The cost is concentrated in the per-character 8-frame runs (≈43 queued rows) and their audits. A cheaper run (4 cells, or a shared light/heavy/robe rig) would not be visibly worse at 2x/4x.
- Tier-2/3 classes (30) and 18 enemies already ship with no art of their own (base-class sheet reuse and procedural fallback), and the game works.

Scratch files:
- /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/engine/runshare_probe.js (run-share and cell-hold probe; usage: `node <path> --battles 6 --speed 1|2|4`, run from the repo root)
- /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/engine/compare_x3.png (warrior idle, warrior run R1, blademaster idle, baren.py idle, baren_hd idle, baren_hd attack; game scale ×3)
- /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/engine/baren/ and .../baren_hd/ (generator outputs)

Key repo files: /home/user/pixel-management/js/art.js, /home/user/pixel-management/js/battle.js (L1256-1760 drawing, L1592 sheetK, L1689 pose, L1861 stature), /home/user/pixel-management/js/sprites.js, /home/user/pixel-management/js/gait_classes.js, /home/user/pixel-management/js/classes.js, /home/user/pixel-management/js/content.js, /home/user/pixel-management/assets/art/manifest.json, /home/user/pixel-management/tools/pixelart/

## 대안 설계

### Paper-doll ("doll") characters: shared bodies per gait class plus part libraries, composed into ordinary sheets

- **summary**: Stop drawing whole characters for generic units. Antigravity draws a small library ONCE:
- about 6 base bodies, one per gait class x attack stance;
- about 40 heads, hair and headgear sprites;
- weapons pre-drawn at 8 angles;
- shields, and later capes and tabards.

A new offline tool, tools/art/doll.py (Codex), composes recipes into normal 96px sheets and registers them as sheet/class/<adv|master> or sheet/monster/<name>. The engine already reads these: Art.sheetFor looks up master, then adv, then base class sheets, and recolours tint keys. Phase 1 needs zero engine changes.

The 55 existing hand-drawn sheets and 7 runs stay as they are. Captains, heroes and bosses keep hand-drawn art.

Most of the library does not need to start from scratch. The 5 approved class sheets (light swing / bow / stab / mace, robe cast) and the ironwall heavy run already contain owner-approved, seam-checked, stride-measured motion. Removing the head and weapon from them in Aseprite is a touch-up job.

Estimated cost to cover the long tail: about 25-35 run-equivalent units (about 1-1.5 weeks of Antigravity time plus 1-2 days of Codex), against the current plan's about 165 units (3-4.5 weeks).

Honest limits:
- Most of the saving comes from no longer drawing per-character captain runs and attack/hit sets. That cut is also available without paper-doll.
- Paper-doll's own value is scaling generic content cheaply (30 tier-2/3 classes, about 10 humanoid enemies, optional per-merc faces) and giving all of them run and attack motion.
- It cannot give the 33 hand-drawn captains a run without replacing their art.
- It has one real unknown: whether Antigravity can deliver parts that register to within 1 px. A 2-day prototype decides this.
- **howItWorks**: What I read: js/art.js (sheet(), anim(), sheetFor), js/battle.js L1592-1766 (sheetK, sheetRecolor/toneRamp, pose(), blit), js/sprites.js mercPixels, js/classes.js look data, js/gait_classes.js, tools/art/sheets.py (breathe, assemble, outline, tone_ramp, key-colour handling), tools/pixelart/baren_hd.py, art/requests/guides/run_base/v2/pose.json, and assets/art/manifest.json.

**Why it fits this codebase**

1. The engine consumes only {img, sx, sy, sw, sh, anchor, anims, tint, runStride, gait} per sheet (pose() returns one cell; blit draws it 1:1).
   - A composed sheet is indistinguishable from a hand-drawn one, so Phase 1 is pure baking with no engine change.
   - sheetFor already checks look.master, then look.adv, then the base class (`for (const k of [lk.master, lk.adv, u.cls, lk.cls])`). Registering sheet/class/paladin etc. is enough for 30 tier-2/3 classes to stop borrowing the base sheet.
   - sheetRecolor already turns tint keys into faction colours, provided the doll keeps outfit/accent key ramps.
   - gait_classes.js already assigns every adv class a gait (paladin=heavy, elementalist/highpriest/warder=robe, the rest light). meta.gait plus the body's runStride (45.5 / 23.6 / 22.2) carry over, so movement speed is unchanged.
2. The game already has a paper-doll data model. look = {cls, adv, master, skin, hair, longHair, tint} plus class {outfit, accent, headgear: band|hat|helmet|hood|none, weapon: sword|bow|staff|dagger|mace}. Sprites.merc composes exactly these at 16px.
   - Recipes can be generated from js/classes.js automatically. Only signature parts need hand choices.
3. Anchors mostly already exist. Each run frame in art/requests/guides/*/pose.json has joints in guide px (hip, SN/SF, handN/handF, neck0, elbows, ankles). With scale 0.1654, the floor 870 -> 92 and centre 192 -> 48 transform (the same one add_gait.py uses) maps them to cell coordinates.
   - Idle, attack and hit anchors are marked once per body in an 'anchors' Aseprite layer: one coloured pixel per anchor, read by the tool.

**Data layout (new, on a branch later)**
- art/dolls/bodies/<body>/ holds:
  - body.png: a 96px-cell sheet with the same frame order as today (idle 0-3, attack 4-5, hit 6, run 7-14). The figure is drawn in key ramps (skin, outfit 4 tones, accent 3, metal, leather).
  - anchors.json: per frame `{neck:[x,y], hand_main:[x,y,angle_bucket,'front'|'back'], hand_off:[...], back:[x,y], head_state:'n'|'hit'}`.
  - body.aseprite: the source, kept on the PC.
- art/dolls/parts/<slot>/<id>.png plus a pivot in parts.json. Slots:
  - head_base (skin-ramp face; normal/hit);
  - hair (8 styles x 2 states; masked by headgear);
  - headgear (8 x 2);
  - weapon (8 weapons x 8 angle sprites; each includes its own gripping fist so the hand join hides);
  - shield (3 shapes x 4 positions);
  - later: cape and tabard, per body frame because they swing with the legs.
- art/dolls/recipes.json: `{id:'paladin', body:'heavy_swing', head:'base_a', hair:'short', headgear:'helmet_plume', weapon:'mace', shield:'kite', palette:{outfit:'#c9ced6', accent:'#3d5a9c', skin:..., hair:..., metal:'steel'}, tint_keys:true, register:'sheet/class/paladin'}`.

**Bake (tools/art/doll.py)**

For each of the 15 frames:
1. Take the body cell.
2. Draw back-layer parts first: cape, weapon if anchor says 'back', off-hand shield.
3. Draw the body.
4. Draw the head stack at neck + per-frame offset (head_base, then hair, then headgear; headgear clips hair by a mask).
5. Draw front parts: main weapon at hand_main using the angle_bucket sprite, shield.

Placement is integer translation only. No rotation and no scaling: angles are pre-drawn. This is a lint, because it is what keeps the "never deform drawn art" rule.

Then:
- Map palette slots with sheets.tone_ramp (the same rule as the JS toneRamp).
- Keep outfit/accent as key colours so runtime faction tint still works.
- Run the C25 seam checker and a join lint (neck/hand overlap >= 2 px, no hole pixels between layers).
- Write the sheet with sheets.assemble, plus a 4x preview and a GIF, and register through register_sheet.py with meta.gait, runStride and tint copied from the body.
- Idle breathing: the body's 4 idle cells are already breathed. Heads and weapons follow the per-frame anchor, so they bob with the torso by whole pixels; sprite-gen is not re-run.

**Phase 2 (optional, later)**
- Art.dollSheet(recipe, look) composes the same layers into an offscreen canvas at load time, cached like recolorCache. Every recruit could then show its own skin, hair and longHair: about 120-180 lines in js/art.js, and pose() is unchanged.
- Memory: one 384x384 RGBA canvas is about 0.6 MB. The cache has to be capped at about 32 entries (about 19 MB) for phones.
- **whoDoesWhat**: **Owner**
- Decides go or kill after the prototype.
- Picks the hand-drawn keep list (suggested: 7 heroes, 7 boss enemies, the 33 captains as they are now).
- Approves the part style once, on a single contact sheet, instead of per character.
- Must explicitly accept "composited from Antigravity-drawn parts" as final art. It is the same kind of decision as baren_hd (see constraints).

**Antigravity (all pixels)**
- Body extraction: Aseprite touch-ups of the approved class sheets.
  - warrior -> light_swing, archer -> light_bow, rogue -> light_stab, cleric -> light_mace (or merge with swing), mage -> robe_cast, ironwall -> heavy_swing.
  - In each: remove the head above the collar and the held weapon, keep a 2-px neck stub and a closed fist, convert clothing to key ramps, and mark anchors in an 'anchors' layer.
- Then draw the part libraries in layered .aseprite files and deliver to art/inbox/doll/... on art-inbox, as today.
- Signature parts for specific recipes, on request: an orc head, a lizardman head and tail, a death-knight helm.

**Codex**
- tools/art/doll.py: compositor, lints and preview (about 900-1300 lines, comparable to add_gait.py's 1,088).
- tools/art/test_doll.py.
- A receive.py/check_delivery.py extension for 'doll/' deliveries: anchor layer present, part sizes, key-ramp-only pixels, every angle bucket present.
- A recipe generator from js/classes.js and content.js (outfit, accent, headgear, weapon -> part ids).

**Cloud lead**
- Recipe schema; library request READMEs (about 15 requests in total instead of one per character).
- Registration; dot_queue status.
- Phase 2 engine code, if wanted.
- Moving the 43 run rows to 보류/cancel.

**GPT-QA**
- In-game checks per batch (10 recipes per task) at 1x, 2x and 4x: joins, weapon jitter across angle buckets, crowd monotony, and faction tint on dolls.
- **upfrontCost**: A "unit" is one run-equivalent: an 8-frame full-figure drawing task. Last week's measured cost of a unit: 1.7 deliveries, a 71% fix rate and about 145k request/audit tokens.

**Antigravity**
- Body extraction from 6 approved sheets: 6 x 15 cells, but this is touch-up (erase the head and weapon, fill the neck stub and fist, recolour to key ramps, add the anchors layer). Estimated 0.5 unit each, so **about 3 units**.
  - New full-figure drawing is only needed if a stance is missing (for example a spear thrust or a two-handed heavy swing): about 1.5 units per new 15-cell body.
- Heads: 3 face bases + 8 hair + 8 headgear, each in normal and hit, about 38 sprites of 18x20 px. **About 1.5-2 units.**
- Weapons: 8 types x 8 angles = 64 sprites, small and single-object. **About 2.5-3 units.**
  - Codex could produce rotsprite-style angle drafts from the 0-degree sprite with our own code, offline, as tracing guides only. These are never shipped as-is (the no-deformation rule).
- Shields: 3 x 4. **About 0.5 unit.**
- MVP library total: about 8-9 units of work. At last week's 1.7-deliveries-per-item factor (registration errors are likely on first use), that is **about 13-15 units' worth of Antigravity time, roughly 2-3 days** including 4-hour quota stops.
- Capes and tabards (phase 1b, drawn per body frame because they swing): 2 types x 3 bodies x 15 cells. **About 4-5 more units.**

**Codex**
- doll.py plus the lints, tests and receive extension: 1-2 days.
- Past tool-building workflows suggest 1.5-3M tokens (the gait_requests generator alone was 1.09M).

**Cloud**
- About 15 library requests at about 145k each, about 2.2M tokens, plus the schema and recipe generation, about 0.5M.

**Total upfront:** about 4-6M workflow tokens and about 2-4 days of calendar time for Antigravity and Codex in parallel. That is the price of about 2 drawn captain runs plus audits under the current plan.
- **perCharacterCost**: **Recipe-only character** (any tier-2/3 class, faction soldier variant, generic human enemy):
- About 15 lines of JSON, mostly auto-generated from js/classes.js.
- Bake in seconds.
- Registration plus a 4x preview: about 20-50k cloud tokens.
- QA in batches of 10, so about 0.1 GPT-QA task per character.
- Antigravity work: zero.

**Character needing one signature part:**
- A new head or headgear (normal + hit, 2 tiny sprites): about 0.1-0.2 unit.
- A new weapon (8 angles): about 0.4 unit.
- A new non-human head with an attached tail or wings: about 0.5 unit.
- Compare the current pipeline: a base sheet at about 1.6 deliveries and 0.23M tokens, plus a run at 1.7 deliveries, about 145k request/audit tokens and a QA task, per character.

**Run and attack motion** come free for every doll, because the body carries them.

**Still full cost (not covered by dolls):**
- Non-humanoid monsters (wolf, spider, slime, wyvern, drake, mimic, hellhound, etc.).
- Anyone on the hand-drawn keep list.
- These continue on today's base-sheet pipeline at about 1-2.2 deliveries each. Their runs are not needed: the engine slides idle with gait 'none'.
- **costToFinishAll**: Same scope as the cost audit's sections 5-6: about 165 run-equivalent units, about 270-280 deliveries and 3-4.5 weeks of Antigravity time.

| Item | Paper-doll plan | Units |
|---|---|---|
| Library MVP + capes/tabards | see upfront | about 13-15, plus 4-5 |
| 30 tier-2/3 classes | recipes; about 10 signature parts (paladin kite shield, berserker axe, sniper longbow, assassin mask, ...) | about 3 |
| About 10 humanoid enemies with no sheet (오크, 리자드맨, 데스 나이트, 마족 전사, 숲 트롤?, 설인? ...) | recipes plus signature heads and weapons. Trolls and yetis are too big for the light/heavy bodies and probably need a 'brute' body (about 1.5 units) or hand-drawn sheets | about 3-5 |
| About 9 non-humanoid enemies, plus about 7 boss sheets, plus the Marisol redraw | today's base-sheet pipeline (1x4 key poses), no runs | about 10-16 deliveries, about 3-5 days (monsters go one at a time) |
| 43 queued captain/hero runs | Do not draw. Captains keep the idle slide, as 48 of 55 sheets already do. Optionally keep the 7 hero runs hand-drawn | 0, or about 7 (about 12 deliveries) |
| Attack/hit expansion (90 + 87 strips) | Drop for hand-drawn characters; they keep 2 attack frames + 1 hit. Dolls get stance-specific attacks from the body | 0 |

**Total:** about 25-35 units plus about 10-16 monster base deliveries.
- About 1-1.5 weeks of Antigravity time (about 1.5-2 weeks if the 7 hero runs are kept).
- About 40-60 deliveries instead of about 275.
- About 6-9M new workflow tokens instead of 13M+.
- About 10-15 GPT-QA tasks instead of about 110.

Honest comparison: just cancelling the captain runs and the attack/hit expansion, without paper-doll, costs about 0. That leaves 30 tier-2/3 classes and about 10 humanoid enemies to handle either by borrowing sheets (as today) or by about 40 hand-drawn sheets (about 65 deliveries, 1.5-2 weeks). Paper-doll beats the hand-drawn option at about 15+ characters, and gives those characters run and attack motion that a borrowed sheet cannot.
- **qualityAtGameSize**: Measured context: humanoids are 63-79 px tall (median 69), the head is about 15-18 px, there are about 20 units on the field, and run cells are about 12-15% of screen time.

**Likely good**
- Silhouettes in a 20-unit scrum at 2x/4x read by weapon, headgear and palette, which is exactly what dolls vary.
- Today all warriors across all factions are one identical sheet, and every tier-2/3 unit wears its base-class sheet. Dolls are strictly more varied than what ships now.
- Motion quality equals the approved class runs, because the bodies are those runs: same frames, same runStride, already QA'd for seams and foot slip.

**Likely visible problems**
1. Same-body monotony: every light doll shares the warrior/archer/rogue body silhouette and leg cycle. At 1x, in long approach runs (p90 episodes are 2.7 s), lock-step legs across many identical bodies may show. Mitigation: the engine already offsets phase per unit (r.phase), plus capes and tabards.
2. Joins at 1x: neck and hand joins misregistered by 1 px show as a gap or a double outline. The owner caught a leg seam on rogue R4, so assume they will see these. Mitigation: 2-px overlaps by construction, plus the join lint and C25 seam checker on every composite.
3. Weapon angle buckets: 8 pre-drawn angles mean the weapon snaps up to 22.5 degrees between frames. In run cells shown 33-150 ms this is probably invisible at 2x/4x but may look stiff at 1x. 16 angles doubles weapon cost.
4. Style gap: captains and heroes were drawn about 6x larger and shrunk (about 40 colours per frame, soft clusters). Native-res parts drawn in Aseprite will look crisper and flatter.
   - Mitigation: author parts on the same guide scale (head about 110 px) and shrink them with the same sheets.py path. Every part is shrunk as a full-frame layer with the same transform so pixel grids match.
   - Or accept the gap for generic units only, which is defensible because captains are meant to stand out.
5. Hit and attack heads: the head is a rigid paste, so a recoil reads only through the separate 'hit' head sprite plus the body's hit pose. That is less expressive than a hand-drawn hit.
6. Ceiling: dolls will never match a hand-drawn captain for personality. That is why heroes, bosses and captains stay hand-drawn.
- **ownerConstraintRisks**: **Never deform drawn art (11-26):** respected if the compositor only translates by whole pixels.
- No runtime or bake-time rotation, scaling, shear or squash: weapon angles are pre-drawn by Antigravity, and the lint rejects any transform.
- One grey area: the bodies are made by erasing heads and weapons from approved sheets. That is editing approved art, not deforming it, but tell the owner explicitly.
- Rotsprite angle drafts may be used only as tracing guides, never shipped.

**Gait classes light/heavy/robe, speed unchanged:** bodies are per gait class, and each doll copies meta.gait and runStride (45.5 / 23.6 / 22.2) from its body. Speed is unchanged by construction, and dolls no longer need per-character stride measurement.

**No third-party assets or code:** the obvious temptation is the LPC "Universal Spritesheet Character Generator" (the classic paper-doll library, CC-BY-SA/GPL). It is reference/learning only; never import its parts, layer tables or code. Every part must be drawn by Antigravity, and the compositor is our own code. Aseprite binaries are still never committed.

**Final art by Antigravity:** every pixel is Antigravity's, but the arrangement is machine-made. This is the same question as shipping baren_hd/procedural output, and it needs a recorded owner decision before any doll is registered. Without it, dolls stay previews.

**NovelAI drafts only:** unaffected. It can be used, if the owner asks, for part-catalogue design drafts (helmet and hair ideas), never for parts.

**Agent roles:** unchanged (Antigravity draws, Codex builds the tools, GPT-QA checks, the cloud integrates). The queue is currently on HOLD (ANTIGRAVITY_STANDING step 0), so no in-flight work is disrupted.

**Seam sensitivity (owner 11-27):** paper-doll multiplies joins, so it multiplies seam risk. The seam checker and join lint must be blocking, not advisory.
- **migration**: **55 existing sheets:** untouched and still registered. Captains, heroes and the 10 monster sheets stay hand-drawn. The 5 class sheets also stay registered as the base-class look; their doll bodies are derived copies under art/dolls/bodies/, not replacements. Dolls register only new ids (sheet/class/<adv|master>, sheet/monster/<name without sheet>), so nothing in assets/art/manifest.json changes or disappears.

**7 run sheets:** unchanged in game. They also become the source of the doll bodies:
- warrior, archer, rogue, cleric -> light bodies;
- mage -> robe;
- ironwall -> heavy.

Their seam, foot-slip and stride QA is reused.

**43 queued Antigravity rows (mostly run requests):**
- Set to 보류 (cancel) in dot_queue.md. Captains and heroes keep the idle slide (wbob 0), as 48 sheets do today.
- Keep the request folders under art/requests/gait/ as archive. That is about 6M tokens sunk; the guides and pose.json there are reused for anchors.
- Optional keep list: the 7 hero runs (`sheet/hero/*`), if the owner wants heroes to visibly outclass generic units.

**Attack/hit pilot (guide/atk__*, hit__*, 6.8M tokens, 0 frames):** close it. Its mannequins can serve as stance references for any new doll body (spear thrust, two-hand heavy) and are not wasted as guides.

**Base-sheet rows for missing enemies:**
- Non-humanoids continue on today's 1x4 pipeline.
- Humanoid ones (orc, lizardman, death knight, 마족 전사) move to doll recipes plus signature parts.
- Bosses stay hand-drawn.

**Docs to update later (by the cloud, not now):** AGENTS.md art section, art/README.md, dot_queue rules, ANTIGRAVITY_STANDING (a new 'doll part' delivery type), docs/agents/queue.md (Codex row for doll.py).
- **smallestPrototype**: Goal: prove or kill in 2 days, before writing any request at scale.

Scratch root: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/paperdoll/ (empty today; later on a branch at the repo paths in brackets).

**Day 1**

Antigravity, one request, delivered under art/inbox/doll/proto/ on art-inbox:
1. light_swing body: sheet_class_warrior.png (all 15 cells) with the head above the collar and the sword removed, a 2-px neck stub, a closed fist, clothing in key ramps, and an 'anchors' layer (neck, hand_main with angle bucket and front/back) in body.aseprite.
2. 3 head stacks (bare short hair, hood, open helmet), each in normal and hit: 6 sprites.
3. 2 weapons (sword, mace) x 8 angles: 16 sprites.

Codex, in parallel, writes a 300-line prototype composer (proto_doll.py, later tools/art/doll.py):
- reads body.png, anchors.json (run frames pre-filled from art/requests/guides/run_base/v2/pose.json joints x 0.1654) and parts;
- integer placement only;
- sheets.tone_ramp palette slots;
- outputs a sheet PNG, a manifest snippet, a 4x preview and a GIF;
- runs the C25 seam checker on every cell.

**Day 2**

Compose 6 recipes:
- warrior rebuilt (bare head + sword), to compare against the original warrior;
- paladin-ish (helmet + mace);
- rogue-ish hood + sword;
- three faction-tinted variants.

Register them into a copy of manifest.json on a local branch (sheet/class/paladin, sheet/class/swordmaster, ...) and play bot battles at 1x/2x/4x. Use the existing tools/sim/gait_probe.js / runshare_probe.js for screen-time.

GPT-QA plus the owner do a blind A/B: original warrior vs the rebuilt doll warrior, at 2x and 1x.

**Kill criteria (any one kills or shrinks the plan to "recipes for idle/attack/hit only")**
1. Antigravity's anchors or parts need more than 1 fix round to register within 1 px.
2. More than 1 join or seam flag per sheet after the fix round.
3. The owner can pick the doll in the blind test at 2x as "worse", not just "different".
4. The prototype library took more than about 1.5 run-equivalents of Antigravity time. If extraction plus 22 sprites cost more than 1.5 drawn runs, the library maths fails.

**Pass:** write the MVP library requests (about 15) and the full doll.py.
- **risks**: The core unknown: Antigravity has delivered large drawings shrunk by 0.1654, but has not shown it can make native-res parts that register to within 1 px. If the anchor/registration fix rate looks like the run fix rate (71%), the library maths gets worse, though it is still paid once instead of per character.; Most of the headline saving (165 units down to about 30) comes from dropping per-character captain runs and the attack/hit expansion, which could be done without paper-doll. Paper-doll's own payoff needs about 15 or more generic characters (30 tier-2/3 classes plus about 10 humanoid enemies qualify).; It cannot give the 33 hand-drawn captains a run without replacing their art. Grafting a captain's upper body onto shared legs is a cut at the waist, which is the exact seam class the owner flagged on rogue R4. Not recommended without its own test.; Seams multiply: every doll has neck, hand and shield joins in all 15 cells. The C25 seam checker plus a join lint must block registration, or the owner will find them in game.; Style gap between soft, downscaled hand-drawn captains (about 40 colours per frame) and crisp native-res parts. Authoring parts at guide scale and shrinking them with the same sheets.py path reduces it, at extra cost.; Same-body monotony at 1x in long runs: every light doll shares one leg cycle.; Weapons at 8 angle buckets can snap up to 22.5 degrees between frames and look stiff at 1x. 16 angles doubles weapon cost. Rotating at runtime is forbidden by the no-deformation rule.; The owner has not yet decided whether machine-composed arrangements of Antigravity-drawn parts count as 'final art by Antigravity'. Without that decision nothing can ship.; Large or odd bodies (trolls, yetis, titan-sized, winged or tailed humanoids) don't fit the light/heavy/robe bodies and need extra 'brute' bodies or stay hand-drawn.; Phase 2 runtime per-merc composition costs memory (about 0.6 MB per 384x384 canvas). Its cache must be capped (about 32 entries) for phones. Phase 1 baking has no such cost.; There is a temptation to borrow the LPC universal spritesheet parts or layer conventions to save time. That is forbidden by owner policy (learning only) and must be stated in the requests.

### Native-res motion kit: draw the run once per gait class at game size, composite it under each character's own idle; drop the per-character large drawings for motion

- **summary**: I measured this proposal against the repo. It only pays off in an adapted form. Four findings:
(1) Drawing new characters natively at 48px or ~33px is a loss. 48px shrinks units about 30% on a layout tuned for about 66px. A 33px figure shown at 2x loses faces (see the proxy image). Nobody on the team can hand-place pixels for a whole figure: Antigravity's deliveries are 1536x1024 image-gen and Python composites, not pixel art.
(2) "Fewer frames" saves almost nothing where it was aimed. Idle is already 1 drawn pose plus automatic sprite-gen breathing, so a 2-frame idle saves 0. Attack and hit are already 2+1 cells taken from the single 4-pose drawing. A 4-cell run would need an engine change, and with one stance frame per step the feet slide about 6-12px per stance cell at 1x.
(3) Captains cannot be palette or accessory variants of class bodies. Their idle silhouettes overlap the best-matching class body at a median IoU of 0.69 (0 of 40 reach 0.8). That is no closer than the 5 classes are to each other (0.60-0.77).
(4) The cost is in motion: per-character 8-frame runs, about 145k tokens of request and audit each, 1.7 deliveries, 71% fix rounds, plus the planned attack/hit expansion. Here native resolution plus sharing does work.
The concrete design keeps base key-pose sheets as they are. Antigravity draws one legs-only run rig per gait class (light, heavy, robe; 8 cells at 96px, game size, about 400 px per cell) once in Aseprite. A new tool composites each character's own idle upper body, pixel-identical with an integer bob, over the rig recoloured to that character's leg colours. Antigravity then touches up only the flagged hem and coat pixels at native resolution. Tier-2/3 classes get palette plus accessory variants of the base class sheets; this is the one place variants fit. The attack/hit frame expansion is dropped.
Estimated effect: the art backlog falls from about 3-4.5 weeks to about 1-1.5 weeks. Most of what is left is the 20 new base sheets, which this does not speed up. Run quality matches the drawn runs at 2x/4x and is visibly simpler at 1x (no arm swing or cloth motion).
The main risk: the owner rejected an engine-cut idle run on 11-26, and this needs his explicit decision.
- **howItWorks**: FACTS IT RESTS ON (code read: js/art.js, js/battle.js L1360-1420 runCells and L1592-1760 sheetK/sheetRecolor/pose/blit, js/sprites.js, js/gait_classes.js, tools/art/sheets.py, tools/aseprite-mcp/README.md, art-inbox NOTES.md)
- The engine draws sheets 1:1 (blit, k=1; bosses 1.5). Cells are 96px (8 sheets use 112px). The engine reads idle 4, attack 2, hit 1 and optionally run 8. runCells() hard-codes the 8-cell step structure: R1/R2 stance at ds/4 each, R3/R4 push and flight. The engine has no layer or overlay compositing; Art.sheetFor picks one sheet per unit. Recolouring exists only for sheet/class/* (tint keys plus toneRamp).
- sheets.py makes the idle from ONE drawn pose plus `sprite-gen breathe` (4 cells automatically). Attack (2) and hit (1) come from the same 1x4 drawing. So the base sheet already has the minimum frame count.
- Antigravity's run deliveries are 1536x1024 RGB composites. Its NOTES describe Python surgery (`split_upper_below_sash`, `extract_clean_leg`, -3 deg rotations, far leg darkened 0.72x), downscaled 0.1654 by add_gait.py. Nobody draws pixels at game size today.
- Current art at game size (measured over all 55 sheets, idle frame 0): humanoid median 1,764 opaque px, 69 px tall, 40 colours per frame (40 per sheet), and 53% "isolated" pixels (no same-colour 4-neighbour), i.e. downscale texture. Run cells repaint the image: even with best ±3px shift, 45-74% of upper-body pixels change between consecutive run cells (warrior 0.74, archer 0.67, mage 0.50, ironwall 0.45), and idle0->idle1 changes 31-74%. Pixel-stable native animation would change about 10-25%.

DESIGN (5 parts)
1. Base key-pose sheets: unchanged (Antigravity 1x4 image -> sheets.py -> register). They cost about 0.23M tokens and 1.6 deliveries each and carry the design. Optional, owner A/B only: a native cleanup pass (16-colour palette plus despeckle) cuts isolated pixels from 34-55% to 4-9% with a nearly identical look (compare_native_x3.png column 2). It makes later native edits easier, but it changes colours, so it needs approval.
2. Run rigs (new, one-time): for each gait class (light 32 sheets, heavy 8, robe 10 per js/gait_classes.js), Antigravity draws ONE legs-and-hips rig at game size in Aseprite: 8 cells of 96x96, feet at (48,92), foot positions and runStride from the existing pose.json (light 45.5, heavy 23.6, robe 22.2). Colours are role keys only (trouser 3 shades, boot 3, outline 1; robe: hem 3, boot 2). The top 3 hip rows are identical in all 8 cells, so the waist join is fixed once per character, not per frame. The robe rig includes the swinging hem. It keeps 8 cells because the rig is drawn once, which keeps runCells' foot-plant untouched (no engine change; a 4-cell run would slide the planted foot about ds/4 to ds/2, roughly 6-12px per stance cell at 1x).
3. `tools/art/rig_run.py` (new, Codex): for sheet X it finds the waist row (belt band or anchor-26), samples X's leg colours from the idle lower region into the rig roles (k-means by luminance), and recolours the rig. It pastes X's idle rows above the waist pixel-identical, with the rig's integer bob table (0/-1 px; no rotation or scale). It flags idle pixels below the waist that the leg roles do not explain (coat tails, tabards, sashes, scabbards) and writes `--dry-run` previews (1x in-game strip, 4x GIF, seam check C25). It then attaches run cells through add_gait.py's existing writer (`anims.run`, `runStride`, `gait`), plus provenance `run.rig: light|heavy|robe`.
4. Native touch-up (Antigravity, only flagged characters): open the generated 8-cell .aseprite at 96px and redraw only the flagged hem region (about 50-150 px per cell), plus the one-time waist join. No large drawing and no downscale.
5. Tier-2/3 variants (optional): the 30 adv/master classes currently reuse 5 base sheets. Make sheet/class/<adv> = base class sheet (all 7 + 8 cells) + one native accessory layer per cell (crest, cape edge, weapon swap) composited offline. Art.sheetFor already looks up look.master and look.adv first, and tint keys carry over. Captains keep their own sheets: median IoU 0.69 against the best class body (none ≥0.8) means a captain made as a class variant would lose its silhouette.
6. Attack/hit: keep 2+1 from the key-pose sheet and cancel the frame-expansion pilot (6.8M tokens so far, 0 frames drawn). Attack and idle carry 22-34% and about 46% of screen time and already work.
- **whoDoesWhat**: - Owner: one A/B gate (rig run vs drawn run vs today's sliding idle, in game at 1x/2x/4x). Decides whether a tool-composited run counts as "final art by Antigravity". Precedent: idle breathing is already machine-made by sprite-gen.
- Antigravity (art): draws the 3 legs-only rigs at native resolution in Aseprite (light first). Does native touch-ups of flagged hems and the waist join. Optionally draws accessory layers for tier-2/3 classes. Keeps drawing the 20 new base sheets with the current 1x4 method.
- Codex (tools/tests): rig_run.py (waist detection, role sampling, recolour, composite, flagging, previews, add_gait writer reuse), its tests, and the accessory-overlay compositor.
- GPT-QA: batched review, 1 contact sheet of about 10 characters per task instead of 1 task per run, plus in-game checks of the seam and foot-plant.
- Cloud lead: no core engine change for 8-cell rigs. Registers sheets, owns dot_queue, retires the 43 per-character run requests, and runs gait_probe / runshare_probe to confirm unchanged movement speed and foot-plant.
- **upfrontCost**: - Rigs: 3 x 8 legs-only cells at about 400 px per cell (the median run cell is 1,448 opaque px, so a rig is about a third of one run's pixels per class). About 1 Antigravity day including one fix round. The light rig is enough for the prototype.
- rig_run.py: Codex 1-2 days, estimated 500-800 lines plus tests (comparable to add_gait.py at 1,088 lines, which it reuses).
- Cloud review and registration: about 1-2M workflow tokens. That is about 1/7 of the 6.9M already spent on run setup, and needs no new mannequins or request generator.
- Optional tier-2/3 overlay compositor: about 0.5 Codex day.
- Engine: 0 changes for 8-cell rigs. If the owner insists on 4-cell runs: an n-aware runCells change (about 20-40 lines plus a probe run), with the 1x foot-slip noted above.
- **perCharacterCost**: | | Today (measured) | Native rig (estimate) |
|---|---|---|
| Request and audit | about 145k tokens per request (README of about 111 lines plus 4 guide PNGs; audits still find about 1.7 errors each) | none. Tool run plus flag report, about 10-30k tokens of cloud time |
| Drawing | 8 frames drawn at about 8.3x scale (about 11.6k game px, about 400k drawn px, 97% discarded), 1.7 deliveries | 0 for characters with plain trousers or robes. For flagged ones: hem redraw of about 50-150 game px x 8 cells plus one waist join, at native resolution, est. 10-30 min of Antigravity time |
| Fix rounds | 71% (5 of 7), only 1 caught by the tools | expected much lower: the upper body is pixel-identical and the rig is fixed, so remaining failure modes are recolour mistakes and hem drawing, both caught by the dry-run seam and flag checks. Not yet measured |
| QA | about 0.7 GPT-QA tasks per run | about 0.1 (batched contact sheets of 10) |
| Calendar | 6.7-15.4h in the serial queue; about 5-8 runs per Antigravity day | auto ones the same day in a batch; touch-ups about 15-25 per Antigravity day |
| Tier-2/3 variant (optional) | not done (reuses base) | about 15 small native overlays (7 base + 8 run cells), est. 0.5h Antigravity |
| New base sheet | about 0.23M tokens, 1.6 deliveries (monsters 2.2) | unchanged; its run comes automatically from the rig |
- **costToFinishAll**: Against the cost audit's projection (about 3-4.5 weeks of continuous Antigravity work, about 270-280 deliveries, about 115 fix rounds, about 110 QA tasks, 13M+ new tokens):
- A. Runs for 43 queued plus about 10 new humanoid enemies (about 53): today 5.4-8.6 Antigravity days and about 74+ deliveries. Rig plan: 1 day of rigs plus 1-2 Codex days (parallel), then touch-ups for an estimated 40-60% flagged (about 20-30 characters, at 15-25 per day, so 1-2 Antigravity days). About 3-4 calendar days and about 2-4M tokens in total.
- B. 20 new base sheets: unchanged, about 3-5 days (monsters one at a time, 4h quota stops). This becomes the long pole.
- C. Attack/hit expansion: dropped, saving the projected 12-18 days, about 155 deliveries and about 10.7M request/audit tokens. If the owner later wants one extra attack cell, native in-betweens are a separate, untested option.
- D. Tier-2/3 variants (optional, new value): 30 x about 0.5h, roughly 2 Antigravity days.
- Total: roughly 1-1.5 weeks (2 weeks with D), versus 3-4.5 weeks. About 30-50 deliveries instead of about 275. Workflow tokens about 4-6M instead of 13M+.
- Caveat: every rig-side number is an estimate until the prototype measures the real flag rate and touch-up time.
- **qualityAtGameSize**: Measured or seen in scratch images, with inference marked:
- Size: unchanged. Characters stay at about 63-79px tall (median 69) in 96px cells.
  - Native 48px figures would be about 0.70x on a layout tuned for about 66px, or would need non-integer scaling.
  - About 33px figures shown at 2x lose faces and weapon detail. The downscale proxy is in compare_native_x3.png column 3 and is pessimistic, since a hand-drawn 33px figure would be cleaner, but that style is a different, chibi-like game. Not recommended.
- Base art: identical (same sheets). The optional 16-colour cleanup looks nearly the same and is cleaner (isolated pixels 53% median down to 4-9% on 4 test sheets).
- Run, measured in the prototype (legswap_x4.png, a crude stand-in that uses warrior run legs as the rig): at 4x zoom, plain-trouser characters (fixer, blademaster) read as running.
  - Failures in the crude version: the warrior legs include its tunic hem and scabbard, so luminance recolour scrambled colours (blue boots, red-patched trousers), and the admiral's coat tails and blademaster's sash were cut at the waist. Hence the design's legs-only rig with explicit role keys plus a hem touch-up.
  - Leg-region IoU between the 5 existing light runs is only 0.53-0.73, so costumes below the waist really differ; the flag rate matters.
- Versus a drawn 8-frame run (inference from engine-needs measurements): at 2x/4x each run cell is on screen for 33-67ms on a figure of about 66px among about 20 units, and individual poses are not distinguishable, so the two are equivalent there. At 1x (light cells about 150ms, p90 run episode 2.7s) the rig shows a static torso and no arm swing or cloth motion, which is visibly simpler than the shadowqueen/rogue drawn runs.
  - Gain: today's run cells repaint 45-74% of upper-body pixels per cell (shimmer). The rig keeps 100% of the upper body stable, and keeps the 0px foot-plant because it uses 8 cells.
- Against today's actual fallback for 48 of 55 sheets (idle sliding with bob 0 for run gaits), the rig is strictly better.
- **ownerConstraintRisks**: 1. "Never deform drawn art" (11-26): the rig does no rotation, scaling or squash; the upper body is pixel-identical with an integer bob.
   - BUT the owner rejected on 11-26 a run where "the engine cuts and twists the idle" (dot_queue warrior row), and later spotted the rogue R4/R8 leg seam himself. A waist-cut composite is the closest thing to that rejected look.
   - This is the decisive risk and must go to the owner as an in-game A/B, not be argued on paper.
2. "Final art by Antigravity": the rig, touch-ups and accessories are drawn by Antigravity, but each character's run is composited by a tool.
   - Precedent exists (sheets.py downscale, palette and sprite-gen breathing already make 3 of 4 idle cells), but it needs an explicit owner decision.
3. Gait classes and speed: the rigs are exactly light, heavy and robe, runStride per class is unchanged (45.5/23.6/22.2), and the engine is untouched. If 4-cell runs were chosen instead: an engine change plus 1x foot slip, which is why the design keeps 8.
4. References: rigs are drawn fresh over our own run_base/v2 mannequin and pose.json. No third-party animation, Mixamo or asset store.
5. Aseprite: commit .aseprite rig files only, never binaries. The pinned aseprite-mcp and its 5 denied tools are unchanged.
6. NovelAI: not involved.
7. Palette cleanup changes colours: owner A/B only. Default off.
- **migration**: - 55 registered sheets: untouched. They stay the base for everything, since the rig uses their idle upper bodies.
- 7 drawn runs (warrior, archer, cleric, rogue, mage, ironwall, shadowqueen): keep. They are accepted and better at 1x, and their legs are the reference for drawing the rigs. Do not regenerate them from the rig unless the owner wants uniformity.
- 43 queued Antigravity run rows (art/requests/gait/*, about 22 MB, 51 request folders): keep the ⏸ hold that is already in dot_queue.
  - If the prototype passes, mark them superseded by `rig/run_light|heavy|robe` and replace each with an auto row plus, where flagged, a short "hem touch-up" row (no new README per character).
  - Archive the request folders; the audit work is sunk.
  - If the prototype fails, un-hold them unchanged. Nothing is lost.
- Attack/hit pilot (guide/atk__*, hit__* "첫 관문 대기"): park as 보류 or cancelled, pending the owner decision to keep 2+1.
- 20 missing base sheets (19 enemies plus the Marisol redraw): proceed with the current 1x4 pipeline once the hold lifts. Humanoid ones get runs from the rig automatically.
- Walk: stays dropped. A walk rig could be added later the same way if ever wanted.
- **smallestPrototype**: Goal: within 1-2 days, settle the three open questions (owner accepts the look, flag rate, native touch-up time).

Day 1
- Antigravity draws `art/inbox/rig/run_light.aseprite` plus `run_light.png`: 8 cells of 96x96, legs and hips only, feet at (48,92), foot positions from `art/requests/guides/run_base/v2/pose.json`, 7 role-key colours, top 3 hip rows identical in all cells.
- In parallel, Codex writes `tools/art/rig_run.py` (dry-run only at first), starting from the crude scratch version below.

Day 2
- Run the tool on 6 light sheets without runs: blademaster and fixer (plain trousers), huntress, bard, hero kai, and admiral (coat tails, expected flag).
- Also run class archer, which has a drawn run, as the A/B control.
- Output a 1x in-game strip, a 4x GIF, flag counts and the C25 seam check.
- Antigravity touches up admiral at native resolution and logs the minutes.
- The owner watches the A/B (rig vs drawn archer vs current sliding idle) in battle at 1x/2x/4x, e.g. a dev toggle reading `run.rig`. That is a registration-only change on a scratch branch; no engine edit.

Kill criteria
- The owner says it reads like the rejected 11-26 cut idle.
- More than 60% of the 6 are flagged.
- A touch-up takes more than 45 min or fails the seam check.
- Pass means: run the heavy and robe rigs the same way.

Scratch evidence already produced (no repo files changed), in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/native/:
- `measure.py`: per-sheet px, height, colours and isolated-pixel rate.
- `share.py`: captain vs class silhouette IoU.
- `runshare.py`: cross-sheet leg IoU and frame-to-frame repaint rates.
- `proxy.py`, `compare_native_x3.png`, `compare_native_x1.png`: current vs 16-colour cleanup vs half-res x2 proxy, plus baren_hd.
- `legswap.py`, `legswap_x4.png`: crude rig composite on warrior, blademaster, admiral and fixer, showing why the rig must be legs-only with role keys.
- **risks**: Owner rejection: a waist-cut composite with a static torso is close to the run look the owner rejected on 11-26 ('엔진이 대기 그림을 잘라 비트는 달리기는 찌그러져 보인다'), and he personally caught the rogue leg seam. An in-game A/B is needed before any rollout.; Unproven skill: no evidence yet that Antigravity can draw or edit good pixels at 96px. Its run work so far is image generation plus Python surgery at 1536x1024. The rig and hem touch-ups are exactly what the prototype must time.; Flag rate unknown: leg-region IoU across the 5 existing light runs is only 0.53-0.73. Coats, tabards, sashes and scabbards below the waist are common (admiral, demonhunter, robes), so the 40-60% touch-up estimate may be low.; Recolour by sampled leg colours can pick the wrong roles (seen in the crude prototype: blue boots, red-patched trousers). The tool needs per-sheet overrides like the existing tint and spot keys in phase3.json.; Quality at 1x is lower than drawn runs: no arm swing, cloth motion or weapon bounce. It is invisible at 2x/4x but noticeable in long 1x approach runs (p90 2.7s).; 'Fewer frames' gives little: idle is already 1 drawn pose plus automatic breathing, and attack/hit are already 2+1. A 4-cell run needs an n-aware runCells and brings back 1x foot slip of about 6-12px per stance cell, so the frame-count saving comes only from sharing the rig.; Captain-as-class-variant does not hold (median silhouette IoU 0.69, none of 40 at 0.8 or above). Variants are only viable for tier-2/3 classes, which have no own art today.; The base-sheet pipeline (20 new sheets, monster idle checks, 4h quota stops) is untouched and becomes the remaining bottleneck, about 3-5 days.; Optional palette cleanup changes colours (40 down to 16). It needs owner approval and must not be applied silently by sheets.py.

### 3D-to-pixel pipeline: a shared rig and part meshes, rendered headless in Blender into palette-exact sheets

- **summary**: I built and ran a working prototype in this container. Blender 5.3.0 installs here as a Python module, and it renders in about 1 second per character. A 15-cell sheet in the engine's own format comes out of the prototype (4 idle, 2 attack, 1 hit, 8 run). The cells are 96px and the figure is 62-69px tall, palette-exact, with a 1px outline. Runs are built from the light/heavy/robe pose tables, so foot positions are known exactly.

Once the rig, pose library and part library exist, each further character is a ~50-line spec plus a review. Runs, attack/hit sets, tier-2/3 class variants and humanoid enemies then come almost free. That removes the 43 drawn-run queue, the ~137k-token audit per request and the 71% fix rate.

It has two costs:
1. **Quality.** At this size, idle and attack (about 68% of screen time) look like toys next to the drawn sheets. Costume detail, wide stances and faces come from painting or very careful modelling, not from rendering.
2. **Owner rules.** It conflicts with "final art by Antigravity". A rendered 3D run cannot sit under an existing drawn idle without a visible change of style.

My honest recommendation for this approach:
- Use it as a volume tool, where its weakness matters least: tier-2/3 class variants, enemies that have no sheet, and possibly all motion cells.
- Or use it as an exact per-character underpainting guide that Antigravity paints over. This cuts audits and fix rounds but not drawing time.
- Do not use it to replace the 55 drawn idle sheets.
- It needs an explicit owner decision either way.
- **howItWorks**: The prototype is in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/blender3d/. It is 349 lines in total: proto.py 173, post.py 62, gen_spec.py 85, matcap.py 12, compare.py 17.

**1. Rig.** One shared rig is a forward-kinematics hierarchy: root, hips, chest, neck, head, and per side shoulder, elbow, wrist, thigh, knee, ankle.
- Its proportions are in game pixels (thigh 14, shin 13, torso 18 and so on), so 1 Blender unit = 1 game px.
- The prototype uses empties. Production would use a Blender armature with the same bone names.
- Part meshes are rigidly parented to bones, with no weight painting. At 64px rigid parts are enough.

**2. Parts.** Part meshes are low-poly boxes, cylinders, cones and spheres in the prototype. In production they are authored meshes: heads, hair, helmets, hoods, plate, robes and skirts, boots, shields, and weapons (sword, mace, staff, bow, spear, dagger).
- Each part's material is a flat "part id" colour.
- Far-side limbs get their own `_far` id.

**3. Poses.** Poses are data tables, authored once and shared:
- run, from GAITS light/heavy/robe in gen_spec.py: thigh/knee/arm amplitude, lean and bob, 8 phases;
- idle, 4 cells (a 1px breath);
- attack, 2 cells per weapon family (SWING, CAST);
- hit, 1 cell.

`plant()` drops the root so that the stance foot touches y=92 in every cell. Feet therefore never slip, and runStride can be computed from the known foot travel instead of being measured on a drawing.

**4. Render.** An orthographic camera with 38° yaw and 8° elevation maps the world origin to anchor [48,92] in a 96x96 cell. Each cell is rendered twice with Workbench and anti-aliasing off:
- an ID pass (FLAT light, material colours);
- a shade pass (our own 4-band toon matcap, toon_matcap.png).

Render time: 15 cells × 2 passes takes 0.5-0.8 s per character on 4 CPUs with no GPU.

**5. Post-process (post.py).** For each pixel:
- match the id to its part, compensating for linear-to-sRGB (maximum error 1.8 RGB units);
- pick the shade band from the shade pass, giving one of 4 ramp tones;
- shift far-side parts down one tone;
- set far pixels that touch near pixels to the darkest tone, which gives an overlap contact line;
- add a 1px outside outline.

The output has 16-33 colours per sheet, all of them exact ramp colours.

**6. Sheet.** The sheet is written in the same layout and meta as sheet/class/warrior (frames, anims idle/attack/hit/run, anchor, cell). Tint keys are the outfit/accent ramps, so sheetRecolor in js/battle.js recolours class sheets for factions with no extra work.

Registration would go through tools/art/register_sheet.py, which expects Aseprite json-array input. Production needs either a json-array writer or a small adapter. Nothing in js/ needs changing. Art.anim, sheetFor, runCells and recolor all work as they are.
- **whoDoesWhat**: This depends on an owner decision, because today Antigravity owns ALL art.

**Option 1: Antigravity authors the 3D source, the cloud renders.**
- Antigravity builds part meshes and the class pose library in official Blender on the owner's PC. That needs a Blender MCP, which does not exist in the setup today; it would have to be reviewed like tools/aseprite-mcp, with a pinned commit and denied tools.
- Antigravity pushes .blend files or parts to art-inbox. Blender is GPL; its binaries are never committed, only installed.
- The cloud (lead) owns the render pipeline (tools/art/render3d/), the post-process rules and registration.
- Codex writes the tooling and tests: spec schema validation, an adapter to register_sheet, a golden-image regression test of the post-pass, and a foot-plant/stride check.
- GPT-QA does in-game checks at 1x/2x/4x.

**Option 2: geometry as code.** The cloud or Codex builds parts procedurally in bpy, as the prototype does. This is the same category as baren_hd.py: our own code, which the policy allows. Its output is still "final art not by Antigravity", so the owner must explicitly accept it.

**Option 3, conservative: underpainting.** The pipeline renders each character's 8 run cells (and later its attack/hit cells) as an exact colour-blocked guide. Antigravity paints over it.
- This keeps the rule that Antigravity makes the final art.
- It replaces mannequin plus measured-box requests with a guide that already has the character's proportions, costume blocks and planted feet.
- receive.py could compare the delivery's silhouette with the render (IoU or seam diff) instead of a ~137k-token multi-agent audit.

Per character, in every option:
- The cloud writes the spec: part picks, ramps (taken from the existing drawn sheet's palette where one exists), weapon family and gait class from js/gait_classes.js.
- The owner gives a contact sheet a quick look.
- **upfrontCost**: **Tooling availability (measured):**
- `pip install bpy` gives Blender 5.3.0 for Python 3.13. It takes about 1-2 minutes and a 1.0 GB venv.
- apt also offers blender 4.0.2.
- Workbench renders headless through Mesa EGL (software). It prints harmless EGL_BAD_MATCH warnings.
- Cycles CPU works (0.84 s for a 96px test).
- EEVEE hung until the 120 s timeout, so it is not usable here.
- There is no GPU. None is needed.
- Fresh containers would need the 1 GB install in the setup script.

**Prototype so far:** about 1 hour of one agent and 349 lines, for 3 characters × 15 cells.

**Production estimate.** These are my estimates, calibrated against the audit's motion setup (about 6-7M tokens per sub-area).

Tooling (cloud plus Codex):
- spec schema and validator;
- a proper armature;
- the post-pass, extended with minimum thickness for 1px weapons, face/eye decals, an inner-line rule and a per-material band threshold;
- a register adapter, a contact-sheet/gate page and tests;
- about 1.5-2.5k lines; **3-5M tokens, 2-3 days**.

Pose library:
- run × 3 gait classes;
- idle × 3 stances;
- attack × about 8 weapon families (sword-and-shield, two-hander/mace, spear, dagger, bow, staff cast, fists/beast, dual);
- hit, cast, and optionally die;
- tuning to the owner's taste usually takes several rounds;
- **3-6M tokens, 2-4 days**.

Part library:
- about 40-60 humanoid parts (heads with 1-2 face variants, 8-10 hair styles, 6-8 helmets and hoods, 4 torso types (cloth/leather/plate/robe), skirts and tabards, boots, capes, 8-10 weapons, 3 shields);
- built in Blender by Antigravity, or in code: **3-6 days**.

Non-humanoid rigs, needed for 9 of the 10 existing monster sheets (wolf, spider, harpy and so on) and most missing bosses:
- quadruped, 8-leg, winged, slime/blob, serpent/drake;
- each a rig plus its own pose tables: **about 1-2 days each**, roughly 5-8 days for all.

**Total upfront:** about 10-20M tokens and 1.5-3 weeks of calendar for humanoids. Monsters add another week. Owner style gates come on top of that.
- **perCharacterCost**: Measured: render plus post-process takes about 1-3 s of CPU per character, all 15 cells.

Estimated, for a character built only from existing parts:
- a ~50-line spec (parts, ramps, proportions, weapon family, gait class);
- one look at a contact sheet;
- **about 20-60k tokens and 10-30 minutes**.

A character that needs 1-3 new signature parts (a pirate hat, the beastmaster's pelt, a frost-jarl beard, a boss crown) adds about 0.5-1 day of modelling. I expect 20-40% of captains and heroes to need this.

Attack, hit and run sets cost nothing per character beyond the class or weapon-family tables. The per-character mannequin, the measured-box request, the multi-agent audit and the fix round all disappear. Fix rounds become global: fix the pose table once and every character re-renders.

Underpainting variant (option 3): Antigravity still paints 8 frames (or 11) per character. The saving is mainly the request and audit (about 145k tokens and about 1.7 corrections per request) and part of the fix rounds. I would guess fix rounds fall from 71% to perhaps 30-40%, because the guide already has planted feet and no cut legs; that is unverified. Calendar time stays bound by Antigravity's serial queue and its 4h quota.
- **costToFinishAll**: The current plan, per the audit, still needs about 165 run-equivalent units: about 270-280 Antigravity deliveries, about 115 fix rounds, 13M+ workflow tokens and 3-4.5 weeks of continuous Antigravity work.

**This approach, full version** (everything still missing, rendered):
- **Upfront:** 10-20M tokens and 1.5-3 weeks.
- **Specs:** 55 + 30 tier-2/3 variants + 19 enemies, about 104 specs. At 20-60k tokens each that is about 2-6M tokens; at 10-30 minutes each, about 2-4 days.
- **New signature parts:** about 25-40 parts, 3-6 days.
- **Total:** about 15-28M tokens and 3-5 weeks of calendar.
- **What you get:** every unit has run, attack and hit sets plus variants, which the current plan never reaches for tier-2/3 classes. Later characters cost minutes, not days.
- **Calendar:** not much shorter than the current plan for the first wave.
- **Marginal cost:** about 100× lower.
- **Catch:** it replaces the look of the 55 drawn sheets.

**Scoped version** (keep the 55 drawn sheets as they are; drop or pause the 43 drawn runs; use 3D only for 30 tier-2/3 class variants and 19 missing enemies, plus attack/hit for those):
- **Upfront:** about 8-15M tokens. Monster rigs are included; the scope is narrower on humanoid parts.
- **Specs:** about 49 specs, about 1-3M tokens.
- **Calendar:** about 2.5-4 weeks.
- **Antigravity:** stays free for portraits, events and the drawn heroes and captains.

**Underpainting variant** (keep the Antigravity paint-over):
- **Upfront:** about 6-10M tokens, for the tooling plus the humanoid part library needed to approximate each existing character.
- **Per run:** cost falls from about 145k tokens and 1.7 deliveries to about 30k tokens and an estimated 1.3 deliveries.
- **Calendar:** still about 5-8 runs per day, so roughly 2-3.5 weeks.
- **Overall:** it saves tokens and fix rounds, not much calendar.
- **qualityAtGameSize**: Measured on the prototype (comparison image /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/blender3d/compare_x3.png, game scale ×3, drawn sheet above and 3D render below for warrior, ironwall and mage):
- Rendered figures are 62-69px tall, the same band as the drawn median of 69px. Width is 22-37px against 40-65px for the drawn ones.
- Each sheet uses 16-33 colours.
- Pixels are crisp with no AA noise, the outline is clean, and the far-side limbs read clearly.
- The run cells read as running. Stance feet are planted to the pixel, and nothing gets cut or merged into a seam, because the cells are geometry.

Where it loses:
- **Idle and attack look stiff and toy-like** (Roblox/Habbo-like). The drawn sheets have:
  - wide action stances and turned shoulders;
  - costume layering (tabard trims, pouches, belts, rim light, cloth folds);
  - shaped silhouettes (the hood, the wizard hat brim, the tall shield) and faces under helmets.
- Better poses and properly modelled meshes would close part of the gap. Experience with Dead Cells-style pipelines says the rest needs hand-painted textures or decals and per-frame touch-ups, which the owner rules allow only by Antigravity.
- **Faces:** the head is about 15px. The eye is a modelled 1x2px box. Expressions and character-specific faces need decal parts.
- **Thin weapons:** 1-2px blades flicker or vanish between cells with AA off. This needs a minimum-thickness rule or a weapon line pass; the prototype's sword is barely readable.
- **Faceting:** low-poly spheres alias into lumpy outlines at 14px. Heads need hand-tuned low-poly meshes.
- **Lighting:** the toon bands come from one matcap. Hue-shifted ramps help, but selective outlining, dithering choices and hand-placed highlights do not happen on their own.

Relative to screen time (engine-needs data): idle about 46% and attack 22-34% carry the quality judgement, so the 3D look is most exposed exactly where screen time is highest. In run cells (12-15% of screen time, unreadable at 2x/4x) a 3D run is as good as a drawn one, or better on foot-slip and seams.

Mixed battlefield: rendered units next to drawn captains will look like two art styles. That is acceptable for soldiers and enemies only if the owner accepts it.
- **ownerConstraintRisks**: 1. **"Final art by Antigravity" (11-26): direct conflict for the full and scoped versions.** A cloud render or code-built geometry is not Antigravity art. It needs an explicit owner decision. The compliant path is either Antigravity authoring the meshes and poses in Blender (it would need a Blender MCP that has not been set up or reviewed) or the underpainting variant (Antigravity paints the final pixels).

2. **"Never deform drawn art": no conflict** as long as 3D renders replace or add cells and never warp drawn pixels. A hybrid with a 3D run under a drawn idle does not deform anything, but it swaps the character's look mid-animation. I would treat that as violating the spirit of the rule. To match a drawn character, every captain would also need modelling, which is per-character cost again.

3. **Gait classes and speed: compatible.** The gaits map 1:1 to 3 shared pose tables (GAITS in gen_spec.py). Movement speed stays as it is, because runStride is computed from planted-foot travel in the render (exact) and can be pinned to today's values: 45.5 light, 23.6 heavy, 22.2 robe. The pose tables are scaled to that stride, not the other way around.

4. **Third-party assets: compatible if disciplined.**
   - No Mixamo, mocap, asset-store meshes, rigs or animations.
   - Our own matcap (toon_matcap.png, generated by our script); avoid Blender's bundled matcaps and HDRIs in shipped renders.
   - Blender and bpy are tools (GPL) and fine to use, but they are not committed to the repo: pip/apt install in the setup script.
   - A Blender MCP is third-party tool code and needs the same review as aseprite-mcp.

5. **NovelAI: not involved.**

6. **Role split** (Codex for tools and tests, GPT-QA for QA, cloud lead for core code): fits as described in whoDoesWhat.

7. **Sunk work:** walk_base, run mannequins, gait_requests, check_skeleton and the 48 audited requests become partly obsolete (about 11k lines of motion tooling). The owner has just been through a similar reset (walk dropped 11-26), and another pivot carries morale and coordination cost.
- **migration**: **55 existing sheets:**
- Keep them all registered and unchanged; nothing in js/ changes. Drawn idle, attack and hit stay the canonical look for captains and heroes.
- The 5 class sheets keep serving tier-1 soldiers.
- In the scoped version, 3D sheets are added only as new ids:
  - sheet/class/<adv|master> for the 30 tier-2/3 classes. Art.sheetFor already prefers look.master, then look.adv, then the base class, so the new ids slot in.
  - sheet/monster/<name> for the 19 enemies without a sheet.
- Tint keys come out exact, so faction recolouring works.

**7 sheets with drawn runs:** keep them as they are. Seven characters, 5 classes plus ironwall and shadowqueen, already have accepted drawn runs that match their idle.

**43 queued Antigravity run requests:**
- Pause them. Do not delete: they are audited and sunk.
- Then choose one of three:
  - (a) Drop them. Units without run cells slide their idle with no deformation, which is about 12-15% of screen time and mostly unreadable at 2x/4x per the engine data.
  - (b) Convert them to underpainting requests: render the character's 8 run cells from a spec that approximates its drawn colours and parts, and give Antigravity that as the guide.
  - (c) Keep only the highest-visibility runs (heroes, popular captains) as drawn runs.
- Attack/hit pilot: stop the per-character mannequin route. Either render shared attack/hit poses (full or scoped version) or render them as underpainting guides (variant).

**dot_queue.md and docs/agents/queue.md:** the owner should decide before any queue edits. Nothing was edited by me.
- **smallestPrototype**: **Day 1 (cloud, scratch only; most of it already exists):**
- Replace the empties with a real armature and a skinned or rigid low-poly warrior modelled to match sheet/class/warrior: blue tabard, teal trim, steel helmet, kite shield, sword.
- Add weapon minimum thickness and an eye/face decal to post.py.
- Tune the SWING and run-light pose tables against the drawn warrior's stance width.
- Render the 15 cells.
- Write the sheet with a json-array adapter and register it in a scratch copy of manifest.json as sheet/class/warrior3d.
- Run tools/sim/gait_probe.js and the battle replay in the browser.

**Day 2:**
- Render the same pipeline for one robe and one heavy character, plus one tier-2 variant (paladin = warrior rig + plate parts).
- Run one monster rig if time allows (wolf: quadruped with 4 legs).
- Put drawn and 3D versions side by side in a battle at 1x/2x/4x, with 20 units.
- Produce an owner A/B page and an underpainting sample: the 3D run cells as a guide next to the accepted drawn warrior run.

**Pass or kill criteria:**
- (1) The owner accepts the 3D idle and attack for soldiers and enemies at 1x (style gate). Otherwise kill the full and scoped versions and keep only underpainting.
- (2) A new tier-2 variant takes ≤30 minutes and ≤60k tokens from spec to registered.
- (3) The 3D run cannot be told apart from the drawn run at 2x/4x by GPT-QA in a blind test.
- (4) Zero foot-slip or seam findings from check_delivery.py on the rendered cells.

**Files already in place**, in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/blender3d/:
- proto.py: rig, parts, poses, two-pass Workbench render; also saves rig.blend.
- gen_spec.py: specs and the GAITS light/heavy/robe tables.
- post.py: ID to ramp, far-side darkening, contact line, outline, sheet plus meta JSON.
- matcap.py, which generates toon_matcap.png.
- compare.py, which generates compare_x3.png.
- Outputs: sheet_3d_warrior.png/.json, sheet_3d_ironwall.png/.json, sheet_3d_mage.png/.json, and out_*/rig.blend.
- venv/, the bpy 5.3.0 install.

Run with `venv/bin/python proto.py -- spec_warrior.json out_warrior`, then `python3 post.py spec_warrior.json out_warrior sheet_3d_warrior.png`.
- **risks**: Style gap: at 64px, rendered idle and attack (about 68% of screen time) look stiffer and plainer than the drawn sheets. The prototype comparison shows a toy-like result. Closing the gap needs serious modelling and posing craft or hand-painted decals, which may push the cost back toward per-character art.; Owner rule conflict: 'final art by Antigravity'. Cloud- or code-rendered finals need an explicit owner decision. The compliant alternatives are a Blender MCP for Antigravity (new, unreviewed tool surface) or underpainting, which saves far less.; Mixed-style battlefield: 3D soldiers and enemies next to drawn captains and heroes. A 3D run under a drawn idle changes the character's look mid-animation, and matching drawn characters would require per-character modelling anyway.; Thin features alias with AA off: 1-2px swords, staves and bows flicker or vanish between cells. Heads alias into lumpy shapes at 14-15px. Faces need decal parts. Each needs special-case post rules.; Non-humanoids (9 of the 10 existing monster sheets, and most missing bosses) need their own rigs and pose tables, about 1-2 days each. Slimes, ghosts and wraiths may be easier to keep drawn or procedural.; Pose authoring is the real art job. A shared pose table that looks wrong is wrong for every character at once (good for fixes, bad for the owner's taste rounds), and early style gates may take several iterations.; Environment: a 1 GB bpy install per fresh container (setup script needed). EEVEE does not work headless here; Workbench and Cycles do. Workbench output depends on Mesa software EGL, so it needs a golden-image test to catch drift between Blender versions (I measured 5.3.0; apt has 4.0.2).; Sunk cost and pivot fatigue: about 11k lines of motion tooling and 48 audited run requests become partly obsolete, right after the walk-to-run reset of 11-26. Coordination docs (dot_queue, queue.md, standing instructions) would need rewriting.; Calendar does not shrink much for the first wave: upfront tooling, parts and rigs (1.5-4 weeks) is similar to finishing the current queue. The win is marginal cost and coverage (tier-2/3 variants, attack and hit for everyone), not speed this month.

### Scope cut: drawn motion only where it is on screen; palette-swap and overlay variants for everything else

- **summary**: Keep the current drawing technique but stop paying per-character motion costs for units that are rarely on screen. I measured 80 bot battles (1,651 units). Class sheets are 48.8% of all units on the field, monster sheets 40.1%, procedural-fallback monsters 6.4%, and captains plus heroes only 4.7% (0-2 per battle, mean about 1). Yet 38 of the 43 queued Antigravity rows are captain or hero runs.

The plan:
(1) Drawn 8-frame runs only for the 5 classes (already done) and the humanoid monsters that fill the field. Skeleton soldier alone is 14.8% of all units; with bandit and desert bandit, these three are 20.2%. The 38 captain and hero runs are dropped, and those units keep the engine's existing no-deform glide. 
(2) Attack/hit frame extension only for the 5 classes, not the 45 humans and 29 monsters in the 11-26 plan. 
(3) The 19 enemies with no sheet are made as variants of existing sheets where possible: 2 pure palette swaps, 11 palette swaps plus a small accessory overlay that Antigravity draws, and 6 truly new sheets. 
(4) Optionally, tier-2 classes get overlay variants of their base class sheet. The engine already looks these up via `sheet/class/<adv>`.

The engine needs no changes: variants register as ordinary sheets under ids that `Art.sheetFor` already tries. Core remaining work drops from about 270-280 Antigravity deliveries (3-4.5 weeks) to about 50 deliveries (about 6-8 Antigravity days). New workflow tokens drop from about 13M to about 4M. GPT-QA tasks drop from about 110 to about 20.

The price is the visual trade-off. Captains, heroes and most monsters glide with only a 1-2px bob while the class soldiers around them run, and boss variants read as recolors. The owner has to accept that.
- **howItWorks**: FACTS FROM CODE:
- `Art.sheetFor` (js/art.js L98-114) already resolves units in this order: `u.art` → monster name → `capKey` → `heroKey` → `look.cap` → class `master` → `adv` → `base`, and a tinted soldier is accepted only if the sheet has tint keys.
- `pose()` (js/battle.js L1693) plays the `run` cells only if `m.anims.run` exists. Otherwise it plays idle and sets `walkFx`, and `walkTf`/`glideBob` (L1490-1557) only adds a 0-2px whole-body bob plus dust. That is the existing, owner-approved no-deform behaviour, already used by 48 of 55 sheets.
- `sheetRecolor` (L1650) recolours only `sheet/class/*` sheets with `meta.tint`.
- The battle plan (L538-628) caps each side at 3 groups of at most 4 units. The player side has at most 1 captain per own company, plus hero members.

THE DESIGN, five parts:

1. TIERS, decided by measured screen presence rather than by importance. Probe: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/scopecut/compo.js (80 battles, replica of `sheetFor`). Shares are % of all units on the field.

| Tier | Units | Share of units | What they get |
|---|---|---|---|
| S | 5 base classes | 48.8% | Unique drawn run (done) + attack/hit extension |
| S | Skeleton soldier | 14.8% | Drawn run (request already written) |
| S | Desert bandit | 3.3% | Drawn run (request already written) |
| S | Bandit | 2.1% | Drawn run (request already written) |
| Optional | Goblin, frost troll | 1.1%, 0.8% | Drawn run |
| A | 33 captains, 7 heroes | 4.7% together | Keep existing 7-cell sheets. No new run or attack frames. They glide. Ironwall and shadowqueen keep their runs. |
| B | 19 enemies with no sheet | 6.4% today, as procedural fallback | Variant sheets (part 2) or 6 new sheets |
| C | 30 tier-2/3 classes | 4.4% | Base-class sheet reuse as today. Optional overlay variants for the 10 adv classes; masters fall through to the adv variant through the existing lookup order. |

2. VARIANT SHEETS, built offline and registered as ordinary sheets:
   - **(a) Recolor.** Remap the sheet's 37-40 colours: either a hue band → target hue keeping HLS lightness, or a 'colorize' of grey ramps by lightness, in the spirit of `toneRamp`. Geometry is untouched. Scratch proof: forest-troll.png and hellhound.png in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/scopecut/ (comparisons recolor_compare_x2.png and hellhound_compare_x2.png). Frost troll → forest troll reads well. Grey wolf → hellhound needed colorize mode. Troll → yeti only gives a white troll, so the yeti moves to the overlay group.
   - **(b) Overlay.** Antigravity opens the base character's large source (all exist on art-inbox: 10 monster strips, 5 class strips plus class run_a/run_b). It draws only an accessory layer: crown, helm, tusks, witch hat, fur mantle, shield. That is 4 poses for a monster, or 12 for a class with run. variant.py composites that layer onto the source and re-runs the base's exact `sheets.py` request parameters (scale, cell, layout, tint, spots), and `add_gait` with the base's recorded `gaits.run` parameters (src, pose, center, floor, stride).
     - If the registered base sheet was touched up after conversion (warrior R5 planted foot), variant.py uses 'delta paste'. It converts source and source+overlay the same way and pastes onto the registered sheet only the pixels that differ.
     - For tier-2 classes, the variant gets `meta.tint` copied, so faction recolour still works. An accessory drawn in the outfit key colours deliberately picks up company colours.
   - **(c) Boss scale.** In `sheetK`, a boss lead (scale 3) is drawn at 1x. A boss variant of a 96px-cell goblin would therefore be smaller than a normal goblin leader (drawn at 1.5x). variant.py re-downscales the large source at 1.5x the base scale instead, giving more detail and no upscaling. The fallback is a 3-line `meta.scale` read in `sheetK`.

3. ENEMY ASSIGNMENT for the 19 missing enemies:

| Method | Enemy (base sheet) | Count |
|---|---|---|
| Recolor only | 숲 트롤 (서리 트롤), 지옥견 (들늑대) | 2 |
| Recolor + overlay | 설인 (서리 트롤 + fur) | 11 |
| | 고블린 왕 (고블린 + crown/cape, boss scale) | |
| | 서리 거인 왕 (서리 트롤 + crown) | |
| | 거미 여왕 (거대 거미 + crown/markings) | |
| | 리치의 망령 (망령 + purple/crown) | |
| | 늪의 마녀 (망령 + green/hat) | |
| | 데스 나이트 (해골 병사 + dark plate/helm) | |
| | 오크 (산적 + green skin/tusks) | |
| | 리자드맨 (사막 도적 + green/lizard head) | |
| | 모래 폭군 (전갈 거인 + overlay) | |
| | 마왕 베르녹스 (마족 전사 + horns/cape) | |
| New full sheet | 전갈 거인, 마족 전사, 늪 슬라임, 미믹, 와이번, 고룡 이그니스 | 6 |

The owner may want 마왕 to be unique too, which adds 1 sheet.

4. NO DRAWN RUN FOR TIER A/B. They use the current glide: idle cells, whole-body bob, and dust. That changes no art and no speed, and the gait classes still drive bob and dust. Nothing changes in battle.js.

5. FEWER SIMULTANEOUS UNIQUE SPRITES. The measurement shows this is already true: non-class unique sheets per battle are median 3, max 5. Captain and hero sheets per battle: 0 → 26 battles, 1 → 30, 2 → 24. I do not recommend gameplay changes, such as keeping captains back or capping heroes, to hide gliding. That would move balance.
   - The one cheap lever, if wanted: in `plan()`'s `minion()`, prefer species that have a sheet. That cuts the fallback monsters, which are 6.4% of units, before the variants land. It is a small content-variety cost.

Caveat on the probe: 71 of the 80 bot battles were monster quests, so faction battles and late-game rosters are under-sampled. The hard ceiling is 3 captains plus hero members among at most 24 units.
- **whoDoesWhat**: - **Owner:** approves the tier cut (captains and heroes glide while classes run). Approves that tool-recoloured or overlay-composited derivatives of Antigravity art count as final art; the same kind of runtime recolour already ships for faction soldiers. Picks which bosses must be unique (at least 고룡 이그니스; maybe 마왕 베르녹스).
- **Cloud lead:**
  - Writes the scope decision into art/requests/dot_queue.md. The 38 captain/hero run rows become 보류(범위 밖); their request folders stay.
  - Writes the variant specs: recolour parameters, base id, accessory brief.
  - Reviews variants by in-battle screenshot, registers them, and updates the art/README.md and ANTIGRAVITY_STANDING.md overlay rules.
  - Optionally makes the 3-line `sheetK` `meta.scale` change.
  - Does no other core code.
- **Codex:**
  - tools/art/variant.py, about 350-450 lines: recolour (hue band / colorize / explicit map), overlay composite plus re-run of `sheets.py` and `add_gait` with the base's recorded parameters, delta-paste fallback, boss re-scale, provenance (`variantOf`, `recolor`, `overlay` fields in the manifest entry).
  - Checks: the overlay layer is the only change and differs only inside its own footprint, and accidental tint-key colours are flagged.
  - Tests.
  - `receive.py`/`check_delivery.py` support for `art/inbox/variant/<id>.aseprite` + `<id>_overlay*.png`.
- **Antigravity:**
  - 11 monster overlays (4 poses each); optionally 10 adv-class overlays (12 poses each).
  - 6 new monster sheets.
  - 3 (or 5) monster runs from the already-audited requests.
  - 5 class attack/hit extensions after gate 1.
- **GPT-QA:** batched in-game QA, one task per 4-6 variants or per run pair, instead of one per item.
- **upfrontCost**: - **variant.py + tests + receive support:** 1 Codex task, about 0.5-1 day. Cloud review about 0.5-1M tokens.
- **Reproducibility check** (does re-running `sheets.py` on the art-inbox source reproduce the registered sheet?): about 1 hour cloud.
- **Docs and queue rewrite:** about 0.2M tokens, 2-3 commits.
- **Engine:** 0 lines required; 3 lines optional (`sheetK` `meta.scale`).
- **Pilot:** 1 overlay item for Antigravity (see the prototype).
- **Total upfront:** about 1.5 days elapsed and about 1-1.5M tokens. This is far below the motion setup already spent (about 17M tokens).
- **perCharacterCost**: | Item | Antigravity | Request / tokens | Registration / QA | Calendar |
|---|---|---|---|---|
| Recolor variant | 0 | Cloud chooses parameters and checks a screenshot, about 20-50k tokens | 1 registration commit; QA batched | Minutes |
| Monster overlay variant (4 poses) | Estimated 1.2-1.5 deliveries (unmeasured; the pilot measures it) | Short brief (base id, accessory, colours, avoid-key list), about 30-50k tokens. No measured-box audit: geometry comes from the base, so legs, seams, foot slip and buried weapons (the defects behind 5 of 7 run fixes) cannot occur. | 1 commit | Hours |
| Class adv overlay (12 poses, inherits run cells) | Estimated 1.5 deliveries | About 50k tokens | 1 commit | |
| New monster sheet | 2.2 deliveries (measured monster rate) | About 0.23M tokens (measured average per base sheet) | Idle check one at a time | |
| Kept monster run | 1.7 deliveries, about 71% fix-round chance (measured) | Request already written and audited; only registration and QA, about 0.1-0.2M tokens | | |
| Captain / hero | 0 further | 0 | 0 | |
- **costToFinishAll**: CORE SCOPE

| Work | Antigravity deliveries | QA tasks | Antigravity time | Tokens |
|---|---|---|---|---|
| A'. Monster runs (5: skeleton, bandit, desert bandit, goblin, frost troll) | About 8.5 | About 4 | About 1 day | About 0.6M (registration and QA only) |
| B'. 6 new monster sheets | About 13 | | About 1.5-2 days (one at a time, quota stops) | About 1.4M |
| B'. 11 overlays | About 15 (assumed 1.4) | | About 1.5-2 days | About 0.5M |
| B'. 2 recolors | 0 | | 0 | About 0.1M |
| B'. QA across new sheets, overlays and recolors | | About 5 | | |
| C'. Attack/hit for 5 classes only (5 × 1.4 run-equivalents) | About 12 | About 5 | About 2-3 days, once gate 1 passes | About 1M |
| Tool and setup | | | | About 1-1.5M |

If only 3 runs are kept, A' drops to about 5 deliveries.

**Core total:** about 49 Antigravity deliveries, about 20 fix rounds, about 15-20 GPT-QA tasks, about 60 registration commits, about 4-5M new workflow tokens, about 6-8 Antigravity working days (about 1-1.5 calendar weeks with quota stops).

Current plan for comparison: about 270-280 deliveries, about 115 fix rounds, about 110 QA tasks, 13M+ tokens, 3-4.5 weeks. The core is about 18% of the deliveries and about 30% of the tokens.

**Optional add-ons:**
- 8 starter-captain runs (blademaster, tactician, lancer, huntress, hedgemage, fieldmedic, fixer, veteran; ironwall is done): +about 14 deliveries, +about 6 fix rounds, +about 1.5 days.
- 10 adv-class overlays: +about 15 deliveries, +about 2 days.
- Unique 마왕 sheet: +2.2 deliveries.
- Marisol redraw: +about 2 deliveries.
- With everything: about 80 deliveries, about 2 weeks.

**Sunk cost written off:** 38 audited run requests (about 38 × 145k ≈ 5.5M tokens). They are kept on disk and can be re-activated later.
- **qualityAtGameSize**: - **Classes:** no change. They are 48.8% of units and already have drawn runs; they also get the attack/hit upgrade.
- **Most frequent monsters:** skeleton, bandit and desert bandit (20% of units) get drawn runs.
- **Captains and heroes:** they look exactly as today, gliding with a 0-2px bob. The engine study found pose detail unreadable at 2x/4x and visible mainly in p90 approach runs at 1x. They are 4.7% of units, but they are the units the player watches most.
  - The honest risk is contrast. A gliding leader next to class soldiers with drawn run cycles is noticeable at 1x. A side-by-side capture is part of the prototype.
- **Recolor variants:** read as classic palette swaps at 66px. The forest troll looked convincing in my scratch test. The hellhound is acceptable but would benefit from an ember or eye overlay. The yeti from the troll does not read as a yeti without a fur overlay. These are judged from game-scale PNGs, not a playtest.
- **Overlay variants:**
  - At 66px a helm or crown is about 8-14px. It survives conversion if Antigravity draws it bold, at large scale with a clear outline.
  - Because the overlay goes through the same `sheets.py` pipeline (BOX downscale, 40-colour quantise, outline), the style stays consistent. A game-scale paste would not.
  - A head-replacing overlay (리자드맨) is the weakest case. If the pilot shows the bandit body showing through, it moves to a new sheet.
- **Bosses as variants:** bosses re-downscaled at 1.5x from the source get more detail than their minions. Even so, a recoloured spider queen or goblin king is visibly 'the same model, bigger, with a crown'. That is acceptable for regional bosses, but probably not for the final boss, which is kept unique.
- **Fallback removed:** the 6.4% of units currently drawn as crude 48px procedural monsters get real sheets, which is a visible gain over today.
- **ownerConstraintRisks**: - **Never deform drawn art:**
  - Recolour changes colours only.
  - The overlay is composited; the base pixels are untouched, and variant.py checks this.
  - Boss scale is a re-downscale from the original source, the same operation `sheets.py` already performs.
  - Gliding units use the existing no-deform `glideBob`.
  - So: no violation.
- **Gait classes and speed unchanged:** nothing in battle.js or gait_classes.js changes. Variants inherit or derive their class (`enemy_tpl`, `captain_style`, `adv`).
- **Final art by Antigravity:** overlays and new sheets are Antigravity's. The recolours and composites are derived by our tool from Antigravity art. This is the same principle as the runtime faction recolour that already ships, but the owner should explicitly confirm that derived variants count as final. This is the main approval needed.
- **Owner preference for run motion** ('전투니까 차라리 뛰기 모션만', 11-26): that answer was walk vs run, not run for everyone. Still, dropping the captain and hero runs reverses work the owner saw queued, so it must be asked, not assumed.
- **Third-party assets:** none. All bases are our own sheets and the code is our own.
- **NovelAI:** not involved.
- **Aseprite binaries:** not involved; overlays are delivered as .aseprite and PNG on art-inbox as today.
- **migration**: - **55 existing sheets:** untouched; all stay registered.
- **7 run sheets:** stay as they are (5 classes, ironwall, shadowqueen). No engine change, so behaviour is identical.
- **43 queued Antigravity rows** (the queue is already paused by the owner 11-28):

| Rows | Action |
|---|---|
| 5 monster runs (skeleton, bandit, desert bandit, goblin, frost troll) | Stay, at the top of 「지금 차례」. Goblin and frost troll are optional. |
| 31 captain runs + 7 hero runs (38 rows) | Move to a 보류(범위 밖) section with their reason |

  - The request folders under art/requests/gait/ stay as they are, so any of them can be re-activated later; the starter captains are the natural first candidates.
  - Nothing is deleted or rewritten.
- **Attack/hit pilot:** the plan is cut to the 5 classes. The existing accepted mannequins (`atk__class_archer`, `atk__class_warrior`, `hit__class_warrior`) remain the gate-1 pilot. The captain and monster parts of the 11-26 plan (`docs/plans/2026-11-26_motion_frames.md` §12) are marked deferred.
- **New rows added:** 11 `variant/<id>` overlay rows, 6 new monster sheet rows (one at a time with idle check), and 2 recolour items. The recolours are cloud-only and need no Antigravity row.
- **Manifest:** variants are new `sheet/monster/<name>` entries (optionally `sheet/class/<adv>`) with provenance fields. `process.py` and `register_sheet` already keep entries they did not produce.
- **smallestPrototype**: DAY 1 (cloud + Codex, no Antigravity):

1. **Recolour.** Promote my scratch /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/scopecut/recolor_probe.py into a scratch variant.py recolour mode. Output 숲 트롤 and 지옥견. Outputs already exist: forest-troll.png, hellhound.png, recolor_compare_x2.png, hellhound_compare_x2.png in that folder.
2. **Reproducibility.** Run `sheets.py --dry-run` on `origin/art-inbox:art/inbox/sheet_monster_goblin.png` and `sheet_class_warrior.png` with their phase3 request parameters. Pixel-diff against assets/art/sheets/*.png. If the diff is 0, use full re-run; otherwise implement delta paste.
3. **Boss scale.** Re-downscale the goblin source at 1.5x scale (for 고블린 왕). Compare its on-field height against a goblin group leader drawn at 1.5x.
4. **Battle check.** Load a scratch manifest copy with the 3 variants, plus a battle where captain ironwall (drawn run) and captain blademaster (glide) move among class soldiers. Capture GIF/PNG at 1x and 4x for the owner (run skill or headless).

DAY 2 (Antigravity, one row):
- `variant/class_paladin`: warrior source + helm/shield/tabard overlay on 12 poses (strip + run_a/run_b), delivered as `art/inbox/variant/class_paladin.aseprite` + overlay PNGs.
- If 12 poses is too much for one day, use `variant/monster_goblin-king` (crown and cape on 4 poses) instead.
- Measure Antigravity time, delivery count, conversion result, and battle screenshot.

**KILL CRITERIA:**
- The overlay needs more than 2 deliveries, or is unreadable or misaligned at 66px.
- Delta paste leaves halos at the overlay edges.
- The owner finds gliding captains next to running soldiers unacceptable. Fallback in that case: add the 8 starter-captain runs to the core, about 1.5 days.
- The owner rejects tool-derived variants as final art. Fallback: those 13 enemies become new sheets, about +29 deliveries, still far below the current plan.

Scratch files: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/scopecut/ (compo.js composition probe; run from the repo root with `node <path>/compo.js 80`).
- **risks**: The owner may reject gliding captains and heroes next to running class soldiers. Captains are only 4.7% of units, but they are what the player watches. Mitigation: re-activate the 8 starter-captain runs, whose requests are already audited (+about 14 deliveries).; Tool-derived recolour or overlay variants may not count as 'final art by Antigravity' under the 11-26 rule. This needs an explicit owner ruling before any variant is registered.; Re-running sheets.py on the art-inbox sources may not reproduce the registered sheets byte-for-byte, because of post-registration touch-ups (e.g. warrior R5). Then delta paste is needed, which can leave 1px edge artefacts around the overlay.; The overlay cost per item is an estimate (1.2-1.5 deliveries), not a measurement. Antigravity's image generator may not reliably edit an accessory layer onto existing poses, and it may redraw the whole figure.; Boss variants may read as cheap recolours. Regional bosses (goblin king, spider queen, frost giant king, swamp witch, sand tyrant) may need unique sheets after all, which would add about 2.2 deliveries each.; Pure hue-band recolour fails on low-saturation sources: grey wolf needed a colorize mode, and troll → yeti only gives a white troll. Each recolour needs per-item parameters and a screenshot check.; The composition probe is skewed toward monster quests (71 of 80 battles from bot play). Faction battles and late-game rosters with heroes may show captains and heroes more often than 4.7%. The hard ceiling is 3 captains plus hero members per battle.; If the queue pause and scope change are communicated badly, Antigravity may keep delivering the old captain-run rows. dot_queue 「지금 차례」 must be rewritten in the same commit as the decision.; The 38 audited captain/hero run requests (about 5.5M tokens) are written off. Re-activating them later may need their measured boxes re-checked if those sheets change.

### Small field figures with big VFX and freeze-frame portrait cut-ins (전장 축소 + 컷인)

- **summary**: Keep the battle sim, the 2D field and the 7-cell sheet format as they are. Change only how big things are drawn. Characters become about 34 px tall (48 px cells) instead of about 66 px (96 px cells). The existing VFX keep their current pixel size, so they become large relative to the figures. Captain and hero specials become short cut-ins: the portrait plus the skill name, shown while the view clock is frozen. We already have 42 portraits.

The 55 existing sheets can be re-made from the Antigravity source PNGs, which are all on art-inbox, with the same sheets.py using `--height 34 --cell 48`. This needs no new drawing. I ran it on 5 sheets and it works. The 7 drawn runs can be re-made with `add_gait.py --scale`.

All drawn run work is dropped: the 43 queued run rows, about 10 future runs, and the attack/hit pilot of about 92 units. At 34 px the figure moves with an idle slide plus a rigid hop.

Measured result: I placed sim positions from 6 real battles at 3, 6 and 10 s. Units with more than 25% of their box covered by another unit fall from 78% at today's size to 3% at 34 px. The sim's spacing (SEP_X=SEP_Y=18 sim px = 36 canvas px) was tuned in the era of 32 px figures, before SPR went from 2 to 3. So formations and lines, which now decide 30-50% of results, become readable.

Cost of the rest of the plan falls from about 3-4.5 weeks of Antigravity time and 13M+ request/audit tokens to about 3-5 Antigravity days (20 base sheets only) plus about 2 engine days. The real price is a visible loss of per-character detail on the field: faces become 2-3 px. Identity moves to silhouette, colours, portraits and cut-ins. Phones are the biggest quality risk: figures are about 18 CSS px at 360 px width. The owner must approve the look before anything changes.
- **howItWorks**: 1. **Field layer (js/battle.js)**
   - The sim (W=320, H=180, SEP_*, speeds, gait classes, step(), record hash) is untouched. The canvas is still 640x360 (Z=2).
   - Sheets are registered at a 48 px cell with feet at (24,44) and a body of about 34 px. They have the same anims as today: idle 4, attack 2, hit 1, optional run 8. The engine never resizes drawn art: sheetK stays 1, and the existing boss ×1.5 stays as it is.
   - stature() already measures each sheet, so HP bars, name tags, flags and the target ring follow the smaller height automatically.
   - Hard-coded body heights need retuning:
     - LIFT=10 and about 28 literal offsets such as `y - 12 - LIFT` and `y - 16 - LIFT` in ingest/drawVfx (L2013-2092).
     - These move behind one constant FIELD_K (about 0.52), applied to heights only, not to effect sizes.
   - The procedural fallback goes from SPR=3 to SPR=2 (16x16 → 32 px, body about 28 px). It is then close to sheet size instead of 42 px against 66 px. This helps the 48 unit types with no sheet: tier-2/3 classes and 18 enemies. monScale goes from [3,3,5,7] to [2,2,3,5].
2. **VFX layer**
   - Slashes (L 24/34, R 13-22), smears, bursts, pillars, bolts, quake and xslash keep their current pixel sizes, so relative to a 34 px body they become about 2x stronger.
   - Hit-stop (view.stop) and shake stay. The wind-up frame shown before a melee hit, the 2-frame attack and the 1-frame hit carry the action: per the engine inventory, idle plus attack plus hit are about 85% of screen time.
   - Movement:
     - Run cells are used where they exist (the 7 re-derived runs).
     - Every other sheet slides its idle frame with a rigid hop. This is the existing walkTf bob, turned on for run gaits too: a whole-sprite translate of 1-2 px per stride, with no deformation. Its amplitude and cadence come from gait_classes.js light/heavy/robe.
3. **Cut-in layer (play(), L2855-2875, css .cutin L636-648)**
   - It keeps today's content: portrait, name and skill name. That is not a "crisis caption", which the owner ruled out (dot_queue Q9③).
   - Change: at ×1 the cut-in sets view.stop to about 0.5 s, the same mechanism as hit-stop. The play loop stops feeding `acc`, so the sim does not advance while the band covers 18-52% of the field. Today the sim keeps running under the band for 1.15 s.
   - At ×2 the freeze is about 0.25 s. At ×4 it is skipped, or shown as a thin side strip.
   - Scope widens a little: allied captains' specials and enemy boss specials (portrait/boss/* exists for 2; the rest fall back to the large 96 px strike frame ×2, an integer scale).
   - Optional later: draw the old 96 px strike cell inside the cut-in, so existing big art still gets shown.
4. **Watched == judged**
   - The sim, the frozen spec, run() at resolve and the replay all stay identical. Only draw() constants and the play-loop pause change.
   - Check: tools/sim/battle.js mismatch 0; the Battle.last() record hash equals the judged record. I have not run this check.
5. **Alternatives considered and rejected for this codebase**
   - Token/card battle: rejected. Tactics are spatial (lines, flanks, protecting the backline, 30-50% of the result). Showing their cause without the field would need text, and the owner said "동작으로만".
   - Side-view lanes: rejected. Collapsing y-depth misrepresents flanks and positions in the judged sim.
   - Native 32 px chibi redraw: kept only as an optional later step for heroes and captains (see risks).
- **whoDoesWhat**: - **Owner:** decides from a side-by-side GIF (current vs 34 px, ×1 and ×4, desktop and 360 px phone width). Nothing changes without that yes.
- **Cloud lead (core code):**
  - FIELD_K and the height-offset retune in js/battle.js; SPR and monScale.
  - Cut-in freeze and scope.
  - Registering the 55 re-derived sheets and the 7 re-derived runs, replacing the 96 px entries under the same ids.
  - Updating phase3.json defaults to height 34 / cell 48.
  - Rewriting dot_queue (cancel run rows and the attack/hit pilot).
- **Codex (tools/tests):**
  - A batch script that re-derives all sheets from their art-inbox sources with sheets.py `--height 34 --cell 48 --dry-run --no-register`, plus a contact sheet.
  - Retuning the sprite-gen breathe parameters for 34 px. 1 of my 5 test runs (mage) hit the depth cap and fell back to a simple bob.
  - A determinism test that the replay hash equals the judged hash with the new draw constants.
- **GPT-QA:** one in-game pass at ×1/×2/×4. Checks: readability at 360 px width, VFX not swallowing figures, cut-in freeze not hiding events, procedural units not out of scale.
- **Antigravity:**
  - Nothing for the migration.
  - Afterwards: only new base sheets (19 enemy types plus the Marisol redraw), in the same 1x4 key-pose format. No mannequins, no gait requests, no attack/hit strips.
  - Optional: native Aseprite touch-ups of eyes and faces on the 40 captain and hero 48 px sheets, one file each.
- **upfrontCost**: - **Engine:** about 1.5-2 days of cloud-lead work, roughly 2-4M tokens including review.
  - Constants plus about 28 offset edits.
  - Cut-in freeze and scope.
  - SPR and monScale.
- **Tools:** about half a day of Codex work.
  - Batch re-derivation, contact sheet, breathe retune, determinism test.
  - Compute is small: sheets.py took about 20-40 s per sheet in my runs, so about 30 min for 55.
- **Registration:** 55 re-registered sheets plus 7 add_gait re-runs (`--scale` exists in add_gait.py). Done as one batch commit, not 62 separate ones.
- **QA:** 1 GPT-QA task. Owner review: 1 GIF.
- **New drawing:** 0.
- **Total:** about 2-3 calendar days and about 3-5M tokens. That compares with 36.7M art workflow tokens spent this week.
- **perCharacterCost**: New character:
- 1 base-sheet request and Antigravity delivery, the same as today. Historical rate: 1.6 deliveries per accepted sheet (monsters 2.2), about 0.23M workflow tokens per sheet.
- It should get cheaper. At 0.083 scale, sub-pixel defects (seams, 1-2 px foot drift, buried weapon tips) mostly vanish, so precision audits can be dropped or reduced to a glance. My estimate is about 0.1M tokens per sheet, not measured.
- No run request (today about 145k audit tokens plus 1.7 deliveries plus 71% fix rounds plus a QA task per run).
- No mannequin and no attack/hit strips.
- For a whole character, that is roughly 1.6 deliveries and about 0.1-0.2M tokens, against about 3.3 deliveries, about 0.4M tokens and about 0.7 fix rounds under today's base-plus-run plan, and more again with attack/hit.
- Tier-2/3 classes continue to reuse base-class sheets with tint recolour, at zero cost.
- **costToFinishAll**: - **A. 43 queued runs:** cancelled, so 0 new cost. The 7 finished runs survive, re-derived.
- **B. 20 new base sheets:** about 32-44 deliveries, 3-5 Antigravity days. Monsters go one at a time and the 4h quota stops apply. Requests cost about 2-3M tokens. The roughly 10 humanoid runs that belonged to B are dropped.
- **C. Attack/hit sets (about 92 run-equivalent units):** dropped. Two attack cells plus the wind-up show, plus big smears and hit-stop, carry the action at 34 px.
- **Total:** about 3-5 Antigravity days plus about 2-3 days of engine/tools, and about 5-8M tokens. Today's plan was about 3-4.5 weeks of continuous Antigravity work, about 270-280 deliveries, about 115 fix rounds, about 110 QA tasks and 13M+ request/audit tokens.
- **Optional extras if the owner wants more life later:**
  - 40 native face touch-ups (about 1 short Aseprite pass each).
  - Native 4-cell runs for heroes only (7).
- **qualityAtGameSize**: Measured, in my scratch prototype:
- **Readability of the field:** in 18 snapshots (6 sim battles × t=3/6/10 s, 12-23 units each), the share of units with more than 25% of their bounding box covered by another unit was 0.78 with today's 96 px sheets and 0.03 with the 34 px re-derivations.
  - The 66 px figures form one blob at 11v11; the tactics decision doc already noted "큰 전투는 한 덩어리로 보인다". At 34 px the lines and gaps of the formation are visible.
  - Image: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/field_66_vs_34.png (left column = today, right = 34 px, same sim positions; mixed sheets, every third unit in its strike pose).
- **Per character:** see /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/closeup_66_vs_34_x3.png (warrior, ironwall, mage, Kai, shadowqueen, each 66 px then 34 px, ×3).
  - At 34 px these still read: silhouette, faction tint, shield, staff and hat, bow, cape, hair colour.
  - These are lost: faces (head about 8 px, eyes about 1 px), armour trim, small accessories. The heavy and light distinction stays clear by width.
  - Identity moves to the roster, portraits and cut-ins.
- **Desktop vs phone:** on desktop (about 1 CSS px per canvas px) 34 px is comparable to classic SRPG map sprites. On a 360 px phone the canvas is about 0.55x, so a figure is about 18-19 CSS px (about 37 device px at DPR 2). That is readable as a silhouette and colour but small; it is today's main quality risk.
- **Movement:** run cells re-derived at half scale halve runStride (light 45.5 → about 22.7), while ground speed is unchanged (owner rule). Cadence therefore doubles: each light cell shows about 75 ms at ×1 and about 19-25 ms at ×4. The 7 drawn runs may look frantic. The fallback is the rigid hop slide, which at 2x/4x looks nearly the same as drawn cells (engine inventory).
- **VFX:** existing smears and bursts become about 2x larger relative to the body. That suits "strong VFX", but they may hide the 34 px figures in a scrum. This needs the GIF check.
- **Procedural fallback:** SPR=2 gives a body of about 28 px, which now matches sheets (today 42 px vs 66 px), so units without art stop looking like a different game.
- **Honest summary:** individual art gets clearly worse, the battle as a whole gets clearer, and the art pipeline gets about 5x cheaper. Whether that trade feels right is the owner's call, and the GIF is how to make it.
- **ownerConstraintRisks**: - **Never deform drawn art:**
  - The engine does no squash or twist. Re-derivation goes through the owner-accepted sheets.py path (the same shrink_pose, palette, spots and tint), only at about 0.083 instead of 0.165. The engine keeps sheetK=1; the boss ×1.5 uniform scale is existing precedent.
  - The hop is a whole-sprite translate, like the existing walkTf bob.
  - Risk: the owner may see a mechanical downscale as "making his art worse". Show the comparison image first.
- **Gait classes light/heavy/robe, speed unchanged:** sim speeds are untouched. Classes still drive hop amplitude and cadence, plus runStride for the 7 runs. The cadence doubling of the re-derived runs is a feel risk, not a rule break.
- **Watched battle == judged battle:**
  - Positions, timing and the record are unchanged; only drawing changes.
  - The cut-in now freezes the view (acc stops) instead of covering the field while the sim runs, so it is a strict improvement for "what you see is what was judged".
  - Card, token and lane variants were rejected because they hide the spatial causes of the result.
- **No captions (Q9③, "동작으로만"):** cut-ins carry only portrait, name and skill, as today. No new text. The risk is that the owner feels that smaller figures mean less visible "motion". The compensation is VFX and hit-stop, not words.
- **Run motion wanted (Q1, "전투니까 뛰기 모션"):** most units would hop-slide instead of a drawn run. This needs explicit owner acceptance. Fallback: native 4-cell runs for heroes and captains only.
- **Final art by Antigravity:** all field art is still Antigravity's drawing, derived by our tool exactly as now. No NovelAI, no procedural finals (baren_hd stays an experiment), no third-party assets or code. Aseprite and offline sprite-gen only.
- **Roles:** engine work by the cloud lead, tooling and tests by Codex, QA by GPT-QA. This matches docs/agents.
- **migration**: **55 existing sheets**
- All 55 have their source PNG on origin/art-inbox (checked: 0 missing).
- Re-derive with sheets.py `--height 34 --cell 48`. Per-sheet request data (spots, tint, pose_scale, layout) still comes from phase3.json; `--height` overrides only the request scale.
- Register under the same `sheet/<kind>/<key>` ids, so js/art.js sheetFor needs no change.
- Caveat: check that the art-inbox HEAD version of each file is the one that was registered (fix redeliveries such as beastmaster and giant spider). Pin by the registration commit where needed.
- Keep the 96 px PNGs in git history. Optionally keep them as `sheet96/...` for cut-in stands (strike frame at ×2 integer scale).

**7 run sheets** (warrior, shadowqueen, ironwall, mage, archer, cleric, rogue)
- Re-run add_gait.py from the same art/inbox/gait deliveries with `--scale` about 0.0827 (half of today's). runStride halves automatically.
- If the doubled cadence looks frantic in QA, register them without run cells and use the hop.

**Queue**
- dot_queue's current ⏸ hold (owner 11-28) becomes:
  - Cancel the 43 Antigravity run rows. Their requests stay in art/requests/gait as sunk record.
  - Stop the attack/hit pilot (guide/atk__*, hit__* gate 1).
  - Walk stays dropped.
- The 19 enemy sheets plus the Marisol redraw stay. Same request format and the same large drawing by Antigravity; only the sheets.py target changes (height 34, cell 48 in phase3.json defaults).
- Helper tasks tied to runs (C25 seam checker, gait QA) are retired. The tools stay in the repo, unused.

**Unfinished Antigravity work files** stay on the PC as the hold already says.
- **smallestPrototype**: Day 1 (scratch only, no repo edits): parts 1-2 are already done.
1. Re-derive 5 sheets at 34 px: done, in /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/work/sheet_*/sheet_*/sheet_*.png. All 5 succeeded; mage idle fell back from sprite-gen breathe.
2. Sim-position composites and the overlap metric: done.
   - Script: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/compose.py
   - Inputs and dumper: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/snaps.json, produced by /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/dump.js, run as `OUT=<path> node dump.js --battles 6` from the repo root.
   - Outputs: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/field_66_vs_34.png and /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/artplan/present/closeup_66_vs_34_x3.png.
3. Re-derive all 55 sheets plus the warrior and archer runs (add_gait.py `--scale 0.0827` against a scratch copy of the manifest) into the scratch folder, with a contact sheet.

Day 2 (on a throwaway branch or worktree, never main):
4. Engine flag `?field=34`:
   - js/art.js loads a scratch `manifest_field.json` that points to the 48 px sheets.
   - js/battle.js gets FIELD_K for LIFT and the about-28 height offsets, SPR=2 and monScale [2,2,3,5], the hop for run gaits without cells, and the cut-in view.stop freeze.
   - css/style.css .cutin unchanged.
5. Record GIFs of an 11v11 and a 6v6 battle at ×1 and ×4, at 640 and 360 widths, today vs field=34.
6. Run `node tools/sim/battle.js 100` and compare the replay hash to the judged hash, to show the sim is untouched.

Kill criteria:
- The owner rejects the 34 px look.
- GPT-QA cannot tell units apart at 360 width.
- VFX hide figures during scrums.
- The cut-in freeze feels like stutter at ×1.

Prove criteria: owner yes, plus QA pass at ×1/×4, plus hash equal.
- **risks**: Owner taste: he just saw and liked the 66 px art in the game. Halving it publicly 'throws away' visible detail (faces), even though no drawing is lost. This is the decisive risk, and it needs the side-by-side GIF before anything else.; Phone readability: at 360 px width a 34 px figure is about 18-19 CSS px. A pinch or zoom view, or a larger canvas on mobile, would be extra engine work.; The owner asked for running motion (Q1). Most units would hop-slide instead of showing a drawn run, and the 7 re-derived runs may look frantic because cadence doubles at the same ground speed.; VFX at today's pixel size may swallow 34 px figures in 20-unit scrums. Effect sizes may need a per-type cap, which is a tuning cost.; Re-derivation quality varies by sheet: sprite-gen breathe failed for 1 of 5 (mage), thin weapons may vanish, and the `spots` that save eyes at 0.165 may not survive 0.083. Some sheets may need an Antigravity native touch-up after all (about 40 captains and heroes worst case, one short pass each).; Hard-coded body offsets: about 28 literal y-offsets plus LIFT in the VFX code. A missed one puts an effect at head height of the old 66 px figure (above a 34 px unit), and these only show up in play.; The art-inbox HEAD file for a sheet may not be the exact version that was registered (fix redeliveries). Re-derivation must pin the source to the registration commit.; Sunk cost becomes visible: about 24M tokens of motion setup and 48 audited run requests become unused. The owner may want them used anyway. A cheaper compromise is drawn runs only for the 7 heroes.; Cut-in freeze: pausing the view at ×1 changes battle pacing (about +0.5 s per special). With many captains it could feel choppy, so a minimum interval is needed (today it is 1.3 s).

## 평가

- 4. Scope cut: drawn motion only where it is on screen; recolour/overlay variants for the rest: **8.5** — Under the cost lens this wins clearly. Upfront cost is the smallest: variant.py is about 400 lines, there are zero required engine lines, and it costs about 1-1.5M tokens. I checked the claim that no engine change is needed: js/art.js L98-114 resolves master, then adv, then class, then monster ids, so variants slot in as plain registrations. It reuses the pipeline the measured rates come from. Base sheets cost about 1.6 deliveries and 0.23M tokens each, and runs about 1.7 deliveries and 145k tokens, so its numbers carry the least speculation of the five. Core scope is about 49 deliveries, 4-5M tokens and 1-1.5 weeks, against about 275 deliveries, 13M+ tokens and 3-4.5 weeks. Even the bad case is cheap: if overlays fail, 13 enemies become new sheets for about +29 deliveries. Three points are softer than claimed. (a) The 1.2-1.5 deliveries per overlay is unmeasured, and Antigravity's image generator may redraw the whole figure instead of adding a layer. (b) The re-run reproducibility of sheets.py is unproven, which may force delta paste. (c) The 5-class attack/hit extension still depends on a pilot that has spent 6.8M tokens and drawn 0 frames. I would defer that too, which cuts about 12 deliveries and 1M tokens. After this, a new character costs about 1.6 deliveries, plus a run only if it is a frequent humanoid monster. A variant costs about 30-50k tokens. The roster ends up complete for enemies, but captains and heroes glide. That is the existing behaviour for 48 of 55 sheets, so there is no new cost, only an owner taste risk.
- 5. Small field figures (34 px) with big VFX and cut-ins: **6.5** — Total cost is low: about 3-5 Antigravity days for the 20 base sheets plus 2-3 engine/tool days, about 5-8M tokens. It also lowers future per-character cost, because sub-pixel defects vanish at 0.083 scale and precision audits shrink. That 0.1M tokens per sheet is an estimate, not a measurement. However, most of the saving (dropping runs and the attack/hit expansion) is the same cut that approach 4 makes for free. What it adds on top costs real money. Engine work touches LIFT plus about 28 literal offsets (I count 13 LIFT references in battle.js alone), the cut-in freeze, SPR and monScale. All 55 sheets must be re-derived and re-registered, with source pinning for redelivered files. Breathe failed on 1 of 5 test sheets, and the worst case is about 40 native face touch-ups. The decisive cost risk is the taste gate: the owner just approved the 66 px look. If he rejects 34 px after the engine work, all of it is sunk. Do it only if the owner wants the readability gain for its own sake, not as a cost measure.
- 2. Native-res motion kit (one legs-only run rig per gait class, composited under each idle): **5.5** — This is cheap only compared with drawing 38 captain and hero runs. Approach 4 removes that line for about 0 by letting those units glide, so 2 is an add-on that buys captain runs, not a saving. Its own cost figures are soft. The 40-60% flag rate rests on leg IoU of only 0.53-0.73. Touch-ups assume Antigravity can edit pixels natively at 96 px, which it has never shown: its deliveries are 1536x1024 image generations plus Python surgery. Codex at 1-2 days for rig_run.py is optimistic, given that the comparable tools went through 14-17 revisions. There is a high chance of total loss, because the owner rejected the closely similar 'cut and twisted idle' run on 11-26. Per-character cost afterwards would be very low (10-30k tokens, auto runs) if it passes. Worth keeping as the gated fallback if the owner refuses gliding captains: one light rig plus a 6-sheet prototype, about 1-2 days.
- 1. Paper-doll characters (shared bodies + part libraries): **4.5** — Its total of about 25-35 units, 40-60 deliveries and 6-9M tokens is not cheaper than approach 4's core. The proposal admits that most of the headline saving is the same scope cut. What doll.py adds is coverage: 30 tier-2/3 classes and about 10 humanoid enemies, all with motion. Today these cost 0, because they borrow sheets and the game works. The upfront estimates are optimistic. A library of about 64 weapon-angle sprites plus about 38 head sprites at native resolution with 1 px registration is exactly the skill Antigravity has not shown. A 71%-style fix rate on parts would roughly double the library cost. Codex at 1-2 days for a 900-1300 line compositor with lints and a receive extension is also optimistic. Seams multiply in every cell, which adds blocking QA. Per-character cost afterwards would be near zero for generic humanoids, so it only pays once the owner actually wants 15+ distinct generic characters with motion. Defer it until approach 4's adv-class overlays prove too limited.
- 3. 3D-to-pixel pipeline (Blender rig + part meshes): **3** — Upfront cost is the largest: 10-20M tokens and 1.5-3 weeks for humanoids, plus about a week for 5 non-humanoid rigs. That is roughly the same calendar time as just finishing the current queue, and it adds a 1 GB bpy install per container and golden-image maintenance. Both the full and scoped versions conflict with 'final art by Antigravity'. The style gap probably forces per-character modelling or decals for anything visible, which moves cost back toward per-character work. The compliant underpainting variant saves tokens and some fix rounds (both estimates) but not calendar time, which is still bound by Antigravity's serial queue and 4h quota stops. Marginal cost per character would be tiny (seconds of CPU, about 20-60k tokens), but only after a large, risky up-front bet that owner gates could still kill. It is the worst cost/risk ratio in the set.

고른 조합: Under the cost lens: approach 4 as the base, approach 2 kept as a gated fallback only, and 1, 3 and 5 not adopted now.

1. **Apply approach 4's scope cut first.** It costs nothing and is reversible:
   - Move the 38 captain/hero run rows to 보류. Their audited folders stay on disk, so any of them can be re-activated later.
   - Keep only the high-share humanoid monster runs: skeleton soldier, bandit, desert bandit. These requests are already audited, so what is left is about 5 deliveries plus registration and QA.
   - Park the whole attack/hit expansion. That includes the 5-class part until gate 1 is proven cheaply, because that pilot has used 6.8M tokens and drawn 0 frames.
2. **Build variant.py** (Codex, about 0.5-1 day). It handles 2 recolours and the overlay variants for the 19 missing enemies; 6 truly new sheets go through today's 1x4 pipeline.
   - First pilot one overlay (goblin king), and check that re-running sheets.py reproduces the registered sheet, before queuing the other 10 overlays.
   - If overlays fail, fall back to new sheets (about +29 deliveries). That is still cheap.
3. **Cut process overhead** at the same time:
   - batched registration commits;
   - one GPT-QA task per 4-6 items;
   - no per-character measured-box audits for variants;
   - fewer dot_queue/queue.md churn commits (139 and 127 this week).
4. **Hold approach 2 as the fallback.** Only if the owner rejects gliding captains: prototype one light legs-only rig on 6 sheets (about 1-2 days) before re-activating any drawn captain runs. Kill it on the same criteria the proposal gives.
5. **Expected result:** about 30-50 Antigravity deliveries, about 3-5M new workflow tokens and about 1-1.5 calendar weeks to a complete enemy roster.
   - A new character afterwards costs about 1.6 deliveries and 0.23M tokens as a base sheet with no run. A recolour or overlay variant costs about 30-50k tokens.
   - The current plan for comparison is about 275 deliveries, 13M+ tokens and 3-4.5 weeks.
6. **Not adopted:**
   - Approach 1 (paper-doll): only if the owner later wants many distinct tier-2/3 or generic units with motion.
   - Approach 5 (34 px field): only as a deliberate readability redesign, not as a cost measure.
   - Approach 3 (Blender): skipped.
7. **Owner decisions needed:** 4's cost advantage depends on two owner calls, which should go to him first:
   - accepting that captains and heroes glide while class soldiers run;
   - accepting tool-derived recolours and overlays of Antigravity art as final art.

- 4. Scope cut: drawn motion only where it is on screen; palette-swap/overlay variants for the rest: **8** — Under the quality lens this is the only approach that leaves every pixel the owner has already seen and approved unchanged. The owner just said the art in the game looked fine. 48 of the 55 sheets already glide with the no-deform glideBob, so 'captains glide' is exactly the look he approved, not a new look. Overlays go through the same sheets.py path (same downscale, ~40-colour quantise and outline) on the original large sources, so the style stays consistent across 80+ units. A native-res paste would not. Recolour holds up at game scale: in the scratch recolor_compare_x2.png the forest troll reads well, and the red-eyed wolf works as a hellhound. Defects remain. The yeti made from the troll is just a white troll, as the agent admits. Regional bosses made as 'same model + crown' will read cheap, so under this lens bosses should get unique sheets (about +7 x 2.2 deliveries, still small). Overlay delivery cost (1.2-1.5) is unmeasured. Antigravity's image generator tends to redraw whole figures, and delta paste can leave 1 px halos, so the pilot must check both. The real taste risk is contrast at 1x: a gliding captain next to running class soldiers. The fallback, re-activating the 8 already-audited starter-captain runs, is cheap. No deformation anywhere.
- 1. Paper-doll characters from shared bodies plus part libraries: **4** — The motion would equal the approved class runs, but the figures would not equal them. To make bodies, heads and weapons are erased from approved sheets. That edits art the owner signed off on. Every doll then carries neck, hand and shield joins in all 15 cells, which multiplies exactly the seam class the owner caught himself on rogue R4. Parts drawn natively at about 15-18 px heads will look crisper and flatter than the soft, ~40-colour downscaled hand art. That is a second style on the field. The fix (author parts at guide scale and shrink them through sheets.py) makes 1 px registration even harder: a shrink of 0.1654 does not keep anchors on whole pixels. Eight pre-drawn weapon angles snap by up to 22.5 degrees at 1x. Every light doll shares one leg cycle and silhouette. The cost claim (about 25-35 units) depends on a registration skill Antigravity has never shown, and most of the saving comes from the scope cut it borrows from approach 4.
- 2. Native-res motion kit: one legs-only run rig per gait class under each character's idle: **4** — The scratch legswap_x4.png is a waist-cut composite with a frozen torso. That is visually the run the owner rejected on 11-26 ('엔진이 대기 그림을 잘라 비트는 달리기는 찌그러져 보인다'). The prototype also scrambled colours (blue boots, red-patched trousers), and cut coat tails and sashes at the waist. Leg-region IoU across the existing light runs is only 0.53-0.73, so the 40-60% touch-up estimate is optimistic. There is no evidence that Antigravity can draw good pixels natively at 96 px, so the touch-ups would be a new style patched into downscaled art. At 1x the run shows no arm swing, cloth motion or weapon bounce. It would sit next to 7 drawn runs that have all of these, so the field would be inconsistent. It does avoid shimmer and keeps planted feet, and it beats the plain glide only at 2x/4x, where the engine data says run poses are unreadable anyway. In short, it adds a risky look exactly where it buys the least.
- 3. 3D-to-pixel pipeline (headless Blender, shared rig and part meshes): **2** — The scratch compare_x3.png settles the quality question. The rendered warrior, ironwall and mage are stiff, narrow (22-37 px wide against 40-65 px for drawn sheets), faceless, toy-like Roblox figures with a barely readable sword. They sit directly beside the drawn sheets, and idle plus attack (about 68% of screen time) is where they look worst. The field would mix two clearly different styles. Closing the gap needs per-character modelling or hand-painted decals, which brings back per-character cost. Its final output also directly conflicts with 'final art by Antigravity'. The only use that survives this lens is the underpainting variant: an exact guide (planted feet, costume blocks) for whatever motion Antigravity still draws. That shapes guides, not shipped pixels.
- 5. Small field figures (34 px) with big VFX and freeze-frame portrait cut-ins: **4** — Nothing is deformed: the sheets are re-derived through the same accepted sheets.py path. But closeup_66_vs_34_x3.png shows what the owner would lose. Faces, trim and the detail he just looked at and approved shrink to 2-3 px heads at 0.083 scale. On a 360 px phone a figure is about 18 CSS px. sprite-gen breathe already failed on 1 of 5 sheets, and saved 'spots' may not survive. Re-derived runs double their cadence and may look frantic. The overlap result (78% to 3% of units heavily occluded) is a genuine readability gain for the battle as a whole, and SPR=2 fallbacks would match sheet scale better. On owner taste, though, this approach publicly shrinks art he has just praised, which is the most likely way to get it rejected. The cut-in freeze is separable: it is an engine-only presentation change with no art risk and is worth keeping.

고른 조합: Under the quality and owner-taste lens I would build on approach 4 (scope cut + variants) and add a few pieces from approaches 5, 3 and 4's own fallback.

**Base (approach 4):**
- Keep all 55 drawn sheets and the 7 drawn runs pixel-identical, at today's 66 px size.
- Draw runs only for the 5 classes (done) and the field-filling humanoid monsters (skeleton, bandit, desert bandit).
- Captains and heroes keep the existing no-deform glide that 48 sheets already use.
- The attack/hit expansion goes to the 5 classes only.

**Changes to approach 4 for quality:**
- Bosses get unique 1x4 sheets, not crown-overlay variants. 고블린 왕, 거미 여왕, 서리 거인 왕, 리치, 늪의 마녀 and 마왕 read cheap as 'same model + crown'. This costs about 15 extra deliveries.
- Overlays are allowed only if the pilot shows that Antigravity adds the accessory layer without redrawing the figure, and that delta paste leaves no halo.
- Recolours are used only where they read well (forest troll, hellhound); the yeti gets its own sheet.

**From approach 5, take only the cut-in freeze:**
- When a captain or hero fires a special, the view freezes for about 0.5 s at ×1 under their portrait cut-in.
- It is an engine-only change: no art changes and the judged sim is untouched.
- It puts the highest-identity art on screen at the moment that matters, which offsets the contrast of gliding captains.
- Do not take the 34 px figure shrink.

**From approach 3, take only the underpainting variant, if anything:**
- Rendered guide cells for the few motion strips that are still hand-drawn (monster runs, class attack/hit), aimed at cutting fix rounds.
- Never ship rendered pixels.

**Reserve, from approach 4's own fallback:**
- If the owner dislikes gliding captains at 1x, re-activate the 8 already-audited starter-captain runs (about 14 deliveries).

**Reject outright:** approach 2's waist-cut rig, because it reproduces the look the owner rejected on 11-26. Also reject paper-doll as a final-art path, because its seams and part-style gap break consistency.

**Owner decisions needed before anything changes:**
1. Do tool-derived recolour and overlay sheets count as final Antigravity art?
2. Is a gliding captain next to running soldiers acceptable at 1x? Show him an in-battle 1x/4x capture first.

- 4. Scope cut: drawn motion only where it is on screen; recolour and overlay variants for the rest: **8** — This is the most feasible option and the easiest to undo. Most of it is queue decisions, not new technique: the 38 captain and hero runs go to 보류 with their folders kept, attack/hit shrinks to the 5 classes, and no engine lines change. Art.sheetFor (js/art.js L98-114) already looks up master, then adv, then the base class, then the monster name, so variants are plain manifest entries. The recolour mode has already been shown in scratch, needs no Antigravity work and cannot deform art. The weak part is the overlay variants. Antigravity is an image generator, not a pixel artist: the art-inbox NOTES.md describes 512-1254px generated originals split out of sheets and nearest-upscaled. It may redraw the whole figure instead of adding one accessory layer, so the estimate of 1.2-1.5 deliveries per overlay is unmeasured and optimistic. Two other risks need checking: whether sheets.py reproduces the registered sheets exactly (warrior R5 was touched up after registration, so delta-paste halos are possible), and whether gliding captains next to running soldiers will annoy the owner. Every one of these has a fallback in the plan: a new sheet, re-activating the 8 starter-captain runs, or un-holding the old rows. Nothing irreversible happens. One owner ruling is still needed: whether tool-derived variants count as final art. The runtime faction recolour already ships, which is a precedent.
- 5. Small field figures (34px) with big VFX and freeze-frame cut-ins: **5** — Execution is very feasible: it needs no new drawing, all 55 source PNGs exist on art-inbox (57 sheet_* files), 5 sheets have already been re-derived with sheets.py, and the overlap metric and composites are real measurements. The acceptance and quality risks are high. The owner has just praised the 66px art. Phones would show figures about 18 CSS px tall. sprite-gen breathe already failed on 1 of 5 sheets, eye `spots` may not survive a 0.083 scale, the 7 re-derived runs double their cadence, and the cut-in freeze has not been checked against the replay hash. The engine side means retuning LIFT plus about 28 literal y-offsets, and a missed offset only shows up in play. Re-registering under the same ids replaces what ships, though it can be undone through git or a ?field flag branch. It is worth building as a cheap A/B prototype on a branch (no Antigravity time), but it is risky as a committed direction.
- 2. Native-res motion kit (one legs-only run rig per gait class, composited under each idle): **4** — Its central assumption is the least proven skill on the team: Antigravity drawing good pixels natively at 96px. Its run work so far is image generation plus Python surgery (split_upper_below_sash, rotations, darkening) at 1536x1024, and the art-inbox notes confirm a generator workflow. A waist-cut composite with a static torso is the closest thing to the look the owner rejected on 11-26 ('엔진이 대기 그림을 잘라 비트는'), and the owner personally caught the rogue leg seam. The crude scratch composite already produced wrong-colour boots and cut coat-tails. The flag rate is unknown: leg IoU between existing runs is only 0.53-0.73, so the 40-60% touch-up estimate is likely low. It is reversible, because the hold rows can be un-held unchanged and the engine needs no change, and the prototype is small. As a plan, its success depends on two unproven skills and one taste gate.
- 1. Paper-doll characters (shared bodies plus part libraries): **3** — Every pixel depends on Antigravity delivering many native-res parts that register to within 1 px: 64 weapon angle sprites, about 38 head sprites, and bodies with the head and weapon erased plus an anchors layer. That is exactly what an image-generator artist is worst at. If its fix rate looks like the run fix rate (71%), the library cost grows several times over. Seams multiply: neck, hand and shield joins in all 15 cells. A new 900-1300 line compositor plus receive extensions also becomes yet another tool surface after about 11k lines of motion tooling. It needs an owner ruling on machine-composed finals. The proposal itself admits most of the headline saving comes from cutting captain runs and the attack/hit expansion, which approach 4 does without this risk. It is moderately reversible because it only adds new ids, but a lot of sunk cost would accumulate before the kill criteria could even be tested.
- 3. 3D-to-pixel via headless Blender: **3** — It is technically proven in this container (bpy 5.3 installs, Workbench renders in about 1 s), so the technical risk is low. But it conflicts directly with 'final art by Antigravity' unless one of two things happens. The first is a new Blender MCP on the owner's PC, which would be unreviewed third-party tool code like aseprite-mcp and does not exist yet. The second is the underpainting variant, which saves tokens but not Antigravity's serial-queue calendar time. The prototype output looks toy-like exactly where screen time is highest: idle about 46% and attack 22-34%. Thin weapons flicker and faces need decals. Upfront cost is 10-20M tokens and 1.5-3 weeks, monster rigs are extra, and fresh containers need a 1 GB install and a golden-image drift test. It would add a second art style on the battlefield and a third motion-pipeline pivot in one week. Best kept as an optional underpainting experiment, not a plan.

고른 조합: Use approach 4 as the backbone, test approach 5 only as a prototype, and keep 2 and 3 on the shelf.

1. Do the parts of 4 that need no new technique right away:
   - Move the 38 captain and hero run rows to 보류(범위 밖). Keep their folders so they can be re-activated.
   - Cut the attack/hit expansion to the 5 classes and close the per-character mannequin route.
   - Keep the already-audited runs for skeleton soldier, bandit and desert bandit (about 20% of units on the field).
   - Have Codex write a small variant.py recolour mode (troll to forest troll, wolf to hellhound).
   These steps need no engine change and no Antigravity skill change, and every one can be undone by un-holding rows.
2. Pilot exactly one overlay variant (goblin king: crown and cape on 4 poses) before writing any more overlay rows. Given that Antigravity is an image generator, the default fallback for variants that fail is a new 1x4 sheet on the current pipeline, which is proven at 1.6-2.2 deliveries.
3. Build approach 5 in parallel only as a ?field=34 branch prototype (re-derive sheets, adjust offsets, record GIFs at 1x/4x and 640/360 widths). It costs no Antigravity time. Show it to the owner as an A/B, never as a default.
4. Do not start paper-doll, native rigs or Blender finals. Each rests on an unproven native-pixel or authorship assumption. Revisit approach 2's light rig only if the owner rejects gliding captains, and then as a time-boxed prototype limited to heroes.
5. Owner rulings needed first:
   - (a) Is it acceptable for captains and heroes to glide while class soldiers run?
   - (b) Do tool-derived recolours and overlays count as final art?
