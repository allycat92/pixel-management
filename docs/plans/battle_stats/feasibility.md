# Feasibility of the battle-stats skeleton (stage 0/1 prototype, HEAD `607f23d`)

## Verdict

The skeleton is mechanically sound, but the design's start constants do not survive the game loop.

- **Stage 0/1 plumbing holds.** With the spec frozen at dispatch and one shadow battle run at every resolve, the bot result is byte-identical to HEAD for 12 of 12 seeds × 365 days.
- **Determinism holds.** 0 violations in 1,231 battles: rerun, JSON round trip, `setup`+`step` stepping, and no fate change in the 2.2 s after `over`.
- **With `ENEMY_K` 0.8 / `SUPPORT_K` 0.6 the economy collapses.** 6 to 7 of 12 seeds fail to reach rank S; 5 to 6 end in game over.
- **With `ENEMY_K` 0.6 the economy survives but inflates.** All 12 seeds reach S, with 87-92% great results and 2 to 4 times HEAD's gold.
- **No single enemy constant fits both ends.** At the same star, forecast R roughly doubles between days 31-60 and days 241+.

Nothing in the repo was edited and no git write was made (`git status` is clean).

## What was built

Everything is in `/tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/feasibility/`.

- **`repo/`**: `git archive HEAD` plus the prototype. `repo_head/` is an untouched copy.
- **`repo/js/stats.js`**: the design's sheet (HP / ATK / DEF, cond with `apt` and `aid`), REF × ARCH × RANK enemy tables, `generic`, `scale`, analytic `margin`, and `judge`.
- **`repo/js/muster.js`**: `Game.muster` freezes the full spec at dispatch, before dispatch fatigue, with a derived seed and no `Math.random`. `Game.forecast` returns R.
- **`patch.py`**: asserted text patches to the scratch copy.
  - `battle.js`: reads `st`, ratio defence, `Battle.run(spec)` returning the record and hash, shots fizzle after `over`, field/hold end rule, and a minimal retreat rule.
  - `contract.js`: flag `RESOLVE = 'roll' | 'battle'`; casualties come from fates with mercy rules 1-5 and 7.
  - `company.js`: `extAfterMission` takes the lost count.
  - `tools/sim/bot.js`: three hooks.
- **`drv.js`, `runset.sh`, `an.js`, `cmp.js`, `peek.js`**: driver, parallel runner, calibration tables, game-level comparison, spec printer. Raw results are in `out/` (61 MB).

There is no bias search anywhere on the new path: one run per contract.

## Calibration against today's `successChance`

Design start values, 6 seeds × 365 days. Dispatched contracts: n = 3,871.

| | Battle decides | Today's roll |
|---|---|---|
| Win rate | 89.0% | 94.9% |
| Tiers great / success / fail / disaster | 73 / 16 / 11 / 0% | 28 / 67 / 5 / 0% |

By chance decile, for the bot's real dispatches plus 2,648 offers it did not take (n = 6,519). The rolled column covers dispatched contracts only.

| successChance | n | Battle win | Rolled win | Share of ours down |
|---|---|---|---|---|
| 0.0-0.1 | 130 | 17% | – | 51% |
| 0.1-0.2 | 81 | 40% | – | 43% |
| 0.2-0.3 | 105 | 58% | – | 34% |
| 0.3-0.4 | 112 | 68% | – | 28% |
| 0.4-0.5 | 136 | 68% | – | 26% |
| 0.5-0.6 | 146 | 69% | – | 24% |
| 0.6-0.7 | 250 | 63% | 63% (n=80) | 28% |
| 0.7-0.8 | 308 | 65% | 78% (n=102) | 27% |
| 0.8-0.9 | 264 | 66% | 84% (n=90) | 26% |
| 0.9-0.97 | 191 | 77% | 96% (n=67) | 18% |
| 0.97 (cap) | 4,796 | 92% | 96% (n=3,528) | 7% |

- **`successChance` carries almost no information between 0.3 and 0.9**: the battle win rate is flat at 63-69%.
- **Inside the cap, results still vary with power/req**: 70% at 1.52-2, 81% at 2-3, 95% at 3-5, 100% at 5 and above.
- **Correlation with the battle result**: chance 0.38, log R 0.57. On uncapped rows only (n = 1,633): chance 0.13, log R 0.76.

The mismatch is mostly about time. Same dispatches, design start values:

| Days | n | Rolled win | Battle win | Median R |
|---|---|---|---|---|
| 1-30 | 155 | 95% | 58% | 0.95 |
| 31-60 | 328 | 95% | 52% | 0.84 |
| 61-120 | 717 | 95% | 76% | 1.02 |
| 121-240 | 1,361 | 94% | 98% | 1.46 |
| 241-365 | 1,310 | 96% | 100% | 1.70 |

- Contract stars rise with guild rank (S by day 73) while roster levels lag, then the roster outgrows a capped star range.
- Example: ★6 has median R 0.80 on days 31-60 and 2.07 on days 241+.
- HEAD has the same drift (power/req 2.8 → 4.5), hidden by the 0.97 cap.

By kind, design start values: story 28% (n=60), campaign 54% (82), boss 56% (32), captain story 60% (47), final 100% (10). Soldier enemies 74%, monsters 93%.

## The forecast R

It is much sharper than chance, but it is not centred where the design assumes.

| R | n | Win | Great |
|---|---|---|---|
| < 0.60 | 307 | 0% | 0% |
| 0.60-0.70 | 284 | 12% | 3% |
| 0.70-0.80 | 355 | 36% | 9% |
| 0.80-0.90 | 415 | 62% | 26% |
| 0.90-1.00 | 481 | 84% | 40% |
| 1.00-1.15 | 758 | 95% | 56% |
| 1.15-1.50 | 1,522 | 100% | 79% |
| ≥ 1.50 | 2,397 | 100% | 95% |

- **The 10 / 50 / 90% win points are roughly R 0.68 / 0.82 / 0.98.** R = 1 is about 90%, not 50%, so the bands need a calibration factor of about 1.2.
- **The 50% point differs by enemy kind**: about 0.95 against soldiers, about 0.80 against monsters. `CAL_KIND` is needed, as the design expected.
- **From R ≥ 1.15 nothing is lost**: 0 defeats in 3,919. The "우세" band already means a certain win before tactics.

## Battle length, wipes, deaths, cost

- **Length at K 0.25**: p10 6.5 s, median 11.1 s, p90 19.5 s; 0.2% run 60 s or longer; 0.1% hit the time limit. The design's target is a median of 18-25 s. K 0.18 gives 14.0 s.
- **Whole party down, retreat off**: 27% of defeats, which is 2.9% of all battles. On days 1-60 it is 14-15% of all battles.
- **Whole party down, retreat on** (≥ 50% of ours down and our hp under 0.5× the enemy's): 0.2% of defeats, 0.05% of all battles. 97% of defeats end by retreat. Retreat costs 0.4 points of win rate.
- **Retreat fires too late for the design's target**: only 33% of defeats keep half of ours on their feet (target ≥ 60%); mean share down in a defeat is 61%.
- **Expected deaths per defeat**:

| | Today's 0.3 on every downed non-captain | Mercy rules 1-4 |
|---|---|---|
| Retreat off | 0.59 | 0.15 |
| Retreat on | 0.47 | 0.001 |

- **Deaths in the battle-decided game loops**: mean 0 to 0.25 per 365-day game, max 1, over 96 games.
- **Cost per battle**: mean 31.5 ms, p99 115 ms, max 235 ms, with 21.5 units on the field on average (n = 7,982).
- **Bot run time**: one seed × 365 days goes from 1.7 s (HEAD) to 19.6 s, so 12 × 365 is about 4 min on one core.
- **Spec size**: 4.2 KB JSON on average (the design said 3.3 KB).

## Knobs, ranked by effect on overall win rate

Baseline 89.0%.

| Knob | Values | Win rate |
|---|---|---|
| `ENEMY_K` | 1.0 / 0.8 / 0.7 / 0.6 | 79.2 / 89.0 / 93.6 / 96.7% |
| `SUPPORT_K` | 0.4 / 0.6 / 0.85 | 83.5 / 89.0 / 95.3% |
| Condition stack compressed (exponent 0.5) | – | 86.5% |
| `aid` and `apt` off | – | 87.7% |
| Stars 8+ gain 2 or 3 enemy levels per star | – | 93.0% at `ENEMY_K` 0.7; 96.4 / 95.7% at 0.6 |
| K 0.18 | – | 88.8% (pacing only) |
| Retreat off | – | 89.4% |

- **None of these changes the early-to-late slope.** At `ENEMY_K` 0.6, days 1-60 are still 81-84% and days 121+ are 100%.
- **`GREAT_HP` is not a usable lever.** Offline, thresholds 0.5 / 0.8 / 0.9 / 0.95 give great shares of 72 / 54 / 39 / 23% at `ENEMY_K` 0.8, and 86 / 72 / 59 / 40% at 0.6.

## Game loop with battle-decided outcomes

It was feasible. 12 seeds × 365 days each. "Old bot" dispatches at `successChance` ≥ 0.6. "R bot" dispatches at R ≥ 1.15 (campaigns ≥ 0.87).

| | HEAD | K 0.8, old bot | K 0.8, R bot | K 0.6, old bot | K 0.6, R bot | Probe, old bot | Probe, R bot |
|---|---|---|---|---|---|---|---|
| Reached S | 12/12 | 5/12 | 6/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| Game over | 0 | 6 | 5 | 0 | 0 | 0 | 0 |
| Day reaching S | 73 | 204 (n=6) | 191 (n=6) | 87 | 86 | 110 | 119 |
| Gold at day 120 | 19,741 | 1,098 | 677 | 24,068 | 28,547 | 8,991 | 10,666 |
| Gold at day 365 | 46,779 | 30,693 | 29,023 | 90,756 | 188,713 | 20,709 | 57,911 |
| Gold at end, median | 10,410 | 1,305 | 247 | 58,260 | 138,461 | 8,131 | 12,699 |
| Mercs at day 60 / 365 | 21.2 / 20.8 | 10.8 / 15.3 | 12.0 / 12.3 | 18.3 / 21.7 | 19.3 / 21.6 | 15.7 / 20.8 | 16.2 / 17.8 |
| Contracts per game | 665 | 400 | 196 | 720 | 710 | 706 | 421 |
| Win rate | 95.0% | 60.7% | 98.1% | 95.3% | 99.6% | 88.9% | 99.1% |
| Great share | 28% | 42% | 78% | 87% | 92% | 45% | 45% |
| Win rate, days 1-30 | 94% | 58% | 99% | 82% | 96% | 81% | 97% |
| Injured per member-battle | 8.5% | 12.4% | 1.6% | 1.8% | 0.5% | 4.0% | 1.1% |
| Deaths per game, mean / max | 0 / 0 | 0.17 / 1 | 0 / 0 | 0.08 / 1 | 0 / 0 | 0.25 / 1 | 0 / 0 |
| Calamity defeated | 10/12 | 5/12 | 6/12 | 7/12 | 7/12 | 5/12 | 10/12 |

"Probe" is `ENEMY_K` 0.6, enemy strength rising by 60% between day 100 and day 300, and `GREAT_HP` 0.9. The calendar ramp is my stand-in to test whether a flat curve exists; it is not a proposal.

- **K 0.8**: the R bot starves early. On days 1-30 only 44% (days 1-15) and 18% (days 16-30) of contracts reach R ≥ 1.15 for the best company. One seed finished 365 days at rank F with zero contracts.
- **K 0.6**: playable, but injuries nearly vanish and gold runs away through the ×1.5 great bonus.
- **Probe with the R bot**: lands in HEAD's range for end gold and calamity, with slower early progression (S at day 119 against 73).
- **A stronger ramp overshoots**: +75% from day 0 killed 6 of 12 games with the old bot and bankrupted 1 of 12 with the R bot.

## What this means for the plan

1. **Enemy strength needs a term tied to progress**, not only star and `req`. The star-to-level table cannot do it alone.
2. **The great rule needs another axis, or late contracts must get harder.** The hp threshold cannot bring great down to the 25-40% gate at any playable setting.
3. **Everything that reads `successChance` must move to R at the switch**: bot dispatch, recruitment counters and the dispatch screen. Keeping the old bot costs 6 to 35 points of win rate.
4. **Special contracts need `KIND_K`.** At `ENEMY_K` 0.6 in shadow: story 67%, campaign 74%, boss 91%, captain story 96%.
5. **Retreat should fire earlier than 50% down** if the design's "half still standing" target matters; at 0.5 it prevents wipes but not heavy injuries.
6. **K must drop to about 0.10-0.12** for the 18-25 s pacing target. That is my extrapolation from two points, not a measurement.

## Not done, or deviating from the design

- **Replay and renderer**: `Battle.play` was not wired to the spec and nothing was run in a browser. Movement (stage 2) and tactics are not in; the captain aura ×1.1 is kept.
- **`plan()` stays in `battle.js`**: `muster` calls it. The UI stub needed a `toast()` as well as `soldierLook`, which supports moving the roster code out as the design says.
- **Betrayal** is rolled at resolve as in HEAD, not at muster.
- **Injury rule**: HEAD's ×1.5 for fatigue ≥ 80 is dropped in battle mode, because the design's table has no such term.
- **Recruitment counters** still read `mission.chance`. The equip guard is not implemented.
- **Unique items**: armour DEF comes from the base-kind lookup only, so a unique outside plate / leather / robe gets 0.
- **Offer sample**: bot-best company plus single-company alternatives, deduplicated per contract and company; capped-chance offers sampled 1 in 5.
- **Sample sizes**: shadow tables use 6 seeds, game loops 12. Small cells (final n=10, boss n=32) are indicative only.

To reproduce a set: `./runset.sh <tag> <roll|battle> <chance|R:1.15:0.87> '<knobs JSON>' <offers 0|1> [days] ["seeds"]`, then `node an.js <tag>` or `node cmp.js <tag> ...`, all in the feasibility folder above.
