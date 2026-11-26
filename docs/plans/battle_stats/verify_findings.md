# Adversarial review: battle stats skeleton (label: verify)

## Verdict

The plumbing is sound, and the feasibility numbers reproduce exactly. The design and owner documents were not updated with what feasibility found, though. They still present start constants, a "백중 = 50%" forecast and a "great 25-40%" gate that the measurements contradict.

The largest unhandled problem is economic collapse without deaths, which the mercy rules do not touch. Three further holes are new: free allies scale with the enemy, the enemy roster can be rerolled by changing the party, and several stage-order mistakes.

No repo file was edited and no git write was made. HEAD is now `7f6d017`; `js/` and `tools/sim/` are unchanged from `607f23d`, so the design's anchors hold.

## What I re-ran

All runs used a fresh `git archive HEAD` copy with the feasibility patch applied.

| Check | Result |
|---|---|
| Shadow mode vs HEAD bot, seeds 1-3 × 365 days | byte-identical 3/3 |
| Determinism (rerun, JSON round trip, stepped, 2.2 s after `over`) | 0 violations in 2,320 battles |
| Battle-decided game loops, seeds 1-6 at `ENEMY_K` 0.8 old bot, 0.8 R bot, 0.6 old bot | 18/18 result lines identical to feasibility |
| `an.js base` | reproduces 89.0% vs 94.9% win, tiers 73/16/11/0, day bands, R bands |
| Great share by `GREAT_HP` 0.5 / 0.8 / 0.9 / 0.95 | 72/54/39/23% at K 0.8 and 86/72/59/40% at K 0.6, as reported |

Two small errors in the feasibility report:
- **K 0.8 R bot, game over:** the logs show 4 (seeds 6, 8, 11, 12), not 5. Seeds 3 and 4 survive with 1 merc.
- **K 0.8 old bot, reached S:** 6 seeds reached S; seed 6 then lost to darkness. The report says 5.

One deviation it did not list: the final contract uses `req / 3000`, not the design's `k` formula.

## Owner decisions

| Decision | Result | Passage and evidence |
|---|---|---|
| Real stats; the battle decides; skeleton | Pass | §2-§6, stage 4 flag. Not playable at the written start values (6/12 games over). |
| Tactics decide 30-50% | Fail as measured | §9 row 13 redefines it as damage share. At the chosen amp 2.5, strength gain is +12% to +33%. After day 120 the win rate is 98-100% before tactics, so tactics cannot change a result there. |
| No picker; preferences from class, role, captain, personality | Pass, thin on personality | §8.1. Only brave, coward and sturdy have a delta; four of the six traits that named captains carry have none. |
| Reward, not punish | Partial | Allies-only synergy was never run. Movement costs mage- and cleric-captain companies up to 14% (§14). Captain-less strength is ×0.57 (§3) against −15% today. |
| No weakness warnings on dispatch | Pass | §7 deletes both lines. |
| No captions | Pass | §6 rule 6, §8.3. |
| Forecast stats-only, median | Structure passes, numbers do not | §7, I6. Measured: band 0.87-1.15 wins 89%; the 50% point is R ≈ 0.82 (soldiers 0.95, monsters 0.80). |
| Running, three movement classes, no art deformation | Pass on paper | Stage 2 acceptance line. Nothing was run in a browser. |
| Freeze inputs once (GPT note) | Pass with gaps | §5. See findings 4, 6 and 7. |
| Recruitment conditions visible and decidable (GPT note) | Pass | §7 table. 무모 wins are 4-5%, so `titan` is unreachable until the stage 5 retune. |

## Findings, most severe first

### 1. Losses compound into collapse, and the mercy rules do not address it
- **Collapse happens with zero deaths.** K 0.8 R bot, seed 8: 16 mercs on day 120, 1 on day 150. Seed 6: 19 to 4 in 30 days. The cause is unpaid wages and low-morale desertion (`js/game.js:697-720`) after 10% pay on failed contracts.
- **Soft lock.** Seed 4 sits at rank F with one captain and zero contracts from day 60 to 366. The `empty` game over needs 0 mercs (`js/game.js:675`), and captains never leave.
- **Losses cluster.** At K 0.6 (the playable setting), days 61-120: loss rate is 22.2% after two or more losses in the prior 5 days (n=508), against 5.9% after none (n=505). Days 121-365: 13.6% against 0.2%. HEAD shows no clustering (6.0% against 6.3%). I did not separate persistent weakness from compounding.
- **Deaths are already near zero** (0.001 per defeat with retreat), so the five death rules solve a problem that barely exists.
- **Every defeat is heavy.** 66% of defeats have 50-75% of ours down; none has under 25%.
- **The opposite spiral also exists.** At K 0.6 great is 87-92%, gold is 2-4 times HEAD, and great adds morale, which raises HP and ATK again.

### 2. No constant set works, and the design has no mechanism for it
- Feasibility showed the same star goes from R 0.80 (days 31-60) to 2.07 (days 241+). The design still lists `ENEMY_K` 0.8 and treats calibration as constant fitting.
- A progress-tied enemy term is a new rule, not a constant. If it follows roster level, levelling stops mattering; if it follows the calendar, it adds time pressure. This needs an owner decision.
- Without it, tactics have nothing to decide after day 120.

### 3. Free allies scale with the enemy, so leaving units home pays early
My probe ran 4 seeds on single-company contracts, 757 offers per setting.
- **Own units are 58% of ally hp×atk in days 1-60** (own level 4.3 against enemy level 6.0). Fill-in trainees are enemy level − 2 and support is enemy level × 0.6.
- **Dropping the weakest member, days 1-60 (n=92):** forecast R stays within 5% in 38% of offers and is equal or higher in 22%. At K 0.6, win is 84% against 83% and great is 64% against 51%.
- **Sending only the strongest merc, days 1-60 (n=102):** R is equal or higher in 25%; great is 60% against 49%. Today's chance for the same choice is 43% against 84%.
- **A lone captain, days 121-365 at K 0.6 (n=383):** wins 99% with great 93%. Captains cannot die.
- **Campaigns with one company instead of all:** R equal or higher in 5 of 14. Too few to conclude.
- The great rule counts only "ours", so fewer and tougher units raise the ×1.5 payout.

### 4. The enemy roster can be rerolled by changing the party
- `plan()` draws trainee, external and support looks from the same rng before the enemies (`js/battle.js:540-621`).
- In 215 of 271 contracts (79%), sending 2 members instead of the full party changed the enemy roster. Example: contract 12 (★1) went from 6 foes with 154 hp to 8 foes with 202 hp.
- §5 claims the forecast "cannot be rerolled". As prototyped, it can.

### 5. The tactics numbers do not come from one configuration
I recomputed from `v4_*.jsonl` (amp 2.5) and `v4a4_*.jsonl` (amp 4).

| | amp 2.5 | amp 4 |
|---|---|---|
| Strength gain, five fitted companies | 1.12-1.33 | 1.19-1.50 |
| Damage dealt from synergy (archer / rogue / mage) | 27 / 33 / 27% | 37 / 38 / 38% |
| Damage removed (cleric / warrior) | 33 / 37% | 43 / 47% |

- The owner file's "27~38%" and "33~47%" take the low end from amp 2.5 and the high end from amp 4, next to the amp 2.5 strength figure.
- At amp 2.5 two of five doctrines miss the 30% floor of gate G3. At amp 4 cleric reaches 1.50, which breaks G3 and G4.
- "More matching members, bigger bonus" is false in the data: archer captain with three archers is 0.973, and warrior with three warriors is 1.065.
- That data had enemy synergy on. "벌은 없습니다" for allies-only is unmeasured.

### 6. Stage-order mistakes
- **S6 cannot run in shadow.** Rank, gold curve and deaths need the battle to decide. The flag and casualty code must exist in stage 3, tool-only, as feasibility did.
- **Freeze at dispatch belongs in stage 1.** Stage 0b builds the spec at resolve, after dispatch fatigue and morale drift, so stage 3 would calibrate on different inputs from stage 4. Feasibility showed a dispatch-time freeze is md5-neutral when the seed is derived.
- **Stage 0b's acceptance check will fail.** `report.companies` is built after `gainExp` (`js/contract.js:410` then `:457`); building at `:361` uses pre-level-up levels, so replays with a level-up will not be hash-equal.
- **S1 sweeps K 0.25-0.16.** Feasibility puts the pacing target near 0.10-0.12.
- **Recruitment thresholds are retuned in stage 5**, one stage after they become unreachable.

### 7. Consumers the design does not list
- **Power displays:** `js/ui-tabs.js:38` ("대장 없음 (전투력 -15%)", 기본 전투력), `:71`, and `:303` (the per-company power chip on the dispatch list).
- **Final contract:** `:466` and `finalReq` (`js/contract.js:590`). The design's `k` clamp would saturate, so weakening the calamity stops mattering. Shadow win was 100% (n=10) against 67% today.
- **Texts:** trait and class lines saying "전투력 +N%", "파티 성공률 +N%", "대성공 확률 ×N" (`js/data.js:38-61`, `js/classes.js:42-65`).
- **Injury ×1.5 at fatigue ≥ 80** is dropped without a decision.

### 8. Dead data and double counting
- **Dead or nearly dead:**
  - Contract `size`: the −6% per missing head is gone, and trainees fill for free.
  - External company `size`: `plan()` clamps to 3-4 units, so losses do not reduce what it fields.
  - Injury systems on wins: 0.5-2.3% per member-battle against 7.7% today.
  - `mods.death` and `noDisaster`: disaster is 0.05% of battles.
  - `mods.great`: irrelevant at 87-92% great.
- **Captain counted four times:** `leaderMul` on every member's HP and ATK, aura ×1.1, own sheet, and the rout rule; the amp is added later.
- **`aid` over-values lucky:** it turns "+5% chance" into ×1.056 HP and ATK for the whole party, close to the unique commander trait (+8%). Today it is worth nothing at the 0.97 cap.
- **Condition against tactics:** the condition stack (median 1.52, p90 2.02) moves strength more than tactics (1.12-1.33), which sits badly with "tactics decide 30-50%".

### 9. Smaller determinism gaps
- The design's hash covers winner, end tick and fates, but `great` and light injury read hp%. The prototype hashes hp; the design should too.
- `Battle.VER` is bumped by hand, while foe and support skills, class speed and tactics tables are read at sim time.

### 10. Owner file: honesty
- Line 3 says the numbers come from running the prototype. Several are targets: 백중 = 반반, 95% at 우세, 대성공 서너 번에 한 번, 첫 30일 85%.
- It omits the feasibility results: collapse at start values, great 73-92%, early win 52-58%, and no constant fitting both ends.
- "후퇴 규칙은 아직 시험하지 않았고" is out of date. Retreat cut wipes from 27% to 0.2% of defeats, but only 33% of defeats keep half standing.
- Costs not stated: next-day pause (about 30 ms per contract on this machine, up to 7 a day, slower on phones), bot checks going from 17 s to about 4 min, and a full rebalance of gold and recruitment.
- The four questions are real owner questions. Question 3's default is not reachable with the hp-threshold rule.

## Amendments

1. Add an economic mercy layer before the switch:
   - pay on a lost contract by enemy share destroyed;
   - smaller morale loss on an orderly retreat;
   - no wage desertion in the week after a defeat;
   - a relief contract when the guild is down to captains.
   Gate it on loss clustering and the lowest merc count.
2. Decide the progress rule for enemy strength first, and add it as owner question 5: should late contracts keep pace with the roster, or stay easy as today?
3. Key trainees to the company's own lowest level, or drop them in real mode. Lower support's share, and make great require the contract's headcount.
4. Give `Game.muster` separate rng streams for foes, support and ally looks. Add an invariant that the enemy roster is identical for any party.
5. Reorder the stages: freeze at dispatch and derive the seed from stage 1; put the tool-only resolve flag in stage 3; build the stage 0 spec where `report.companies` is built today.
6. Rewrite the owner file from the feasibility table, with tactics numbers from one amp, and remove "more matching members is better".
7. Extend the stage 4 file list with `js/ui-tabs.js:38, :71, :303, :466`, `js/data.js:38-61`, `js/classes.js:42-65`, and a separate final-contract scale.
8. Hash every value `judge` reads, and derive `Battle.VER` from a digest of the sim tables.
9. Replace the great rule's single hp threshold with a second axis (for example time, or enemy leader killed), since 0.95 still gives 40% at K 0.6.
10. Apply `aid` once, to ATK only or capped at +8%, and measure captain-less strength against the −15% the UI promises.

## Files

Everything is in `/tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/verify/`:
- `ident.js` — identity and determinism check
- `probe.js`, `probe_an.js` — roster-variant exploit probe
- `reroll.js` — enemy roster reroll test
- `snow.js` — loss clustering and collapse timelines
- `out/` — raw results
- `repo/` — patched scratch copy
- `repo_head/` — untouched copy
