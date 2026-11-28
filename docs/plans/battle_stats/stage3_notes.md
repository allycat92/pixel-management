# Battle stats, stage 3: the battle decides, behind a switch

Date 2026-11-27. Base `e33267a` (C7 calibration adopted). Spec: `design.md`, amendments `verify_findings.md`,
owner decisions of 2026-11-27 in `README.md`. Stage 0-1 notes: `stage01_notes.md`.

This file describes the code after the **fix round** (same day): an adversarial verify found 7 findings, and every
one is either fixed or rejected with a reason in "Verify findings and what was done". The tables below are the
measurements of the fixed code; the first implementation's numbers are kept only where they are compared.

## The switch

`Game.RESOLVE` is `'roll'` or `'battle'`. **Since 2026-11-27 (owner: ship the passed work) a new browser game starts in `'battle'`** (`Game.newGame('battle')`, before the first board is filled); `?resolve=roll` starts/switches to roll; existing saves keep their stored mode. `Game.newGame()` with no argument is still roll, so bots/sims and the roll md5 are unchanged.

- It is a getter/setter on `Game` (`js/muster.js`) backed by `state.resolve`, so it is saved with the game. A new game
  asks nothing and starts in `'roll'`; `state.resolve` is absent in roll saves, so roll saves are byte-for-byte the
  same shape as before.
- Turning it on: open the game with `?resolve=battle` (`js/main.js`, also kept for "new game" in that tab, `js/ui.js`),
  or call `Game.setResolve('battle')` in the console. `?resolve=roll` switches back. Tools: `--resolve battle` or
  `SIM_RESOLVE=battle` (`tools/sim/bot.js`, `tools/sim/shadow.js`).
- Entering battle mode draws the per-save salt once (`state.salt`, the only `Math.random` the switch uses).
- Everything listed below runs only when `state.resolve === 'battle'`. In roll mode no new code path draws a random
  number or changes state; the roll-mode shadow battle is also unchanged (see "Roll mode unchanged").
- Switching mid-game is safe in both directions, and **the mode at dispatch decides** (fix round, verify 7): a
  mission whose frozen spec was made in battle mode (`spec.bm`) is decided by its battle even if the switch is
  turned off before it returns; a mission sent in roll mode (or without a spec) is decided by the roll even if the
  switch is turned on. Contracts without `bseed` fall back to the save salt.

## What was built

| Item | Where | What |
|---|---|---|
| (a) board | `js/muster.js` `capability`, `battleCap`, `battleLevel`; `js/contract.js` `contractLevel`, `fillContracts` | Each day the strongest `BOARD_TOP` (3) own companies (all members) are forecast against a reference contract (home province, goblin hunt) at every star 1-14. **The board is stratified**: a new ordinary contract counts the words already aimed at on the board (`c.aim`) and draws the word that is most short of `BOARD_W`, weighted by the shortfall. Hard words (백중, 열세, 무모) are aimed at the **best** company's curve, easy words (우세, 압도) at one of the top 3 (so weaker companies still get work). The star is one of the three highest in that word, never above the cap `battleCap()` = rank + `BM_CAP_AHEAD` (4), or `LATE_MAX_LEVEL` after the calamity. The board has `BM_BOARD_EXTRA` (3) more ordinary slots in battle mode, so the hard offers do not take the places of winnable work. Reward and rep come from `makeContract` unchanged, so harder pays more. Enemies are fixed by star; the board moves, the enemies do not. |
| (b) resolution | `js/muster.js` `battleResolve`; `js/contract.js` `resolveMission` | Missions whose spec has `bm` run that spec once in `Battle.run`; `Game.judge` gives the tier. `report.battle = { v, ver, tab, hash, winner, t, end, R, band, foeShare, spec }`. No roll, no `findBattle`. If the battle cannot run (no `Battle`, an exception) the old roll is used as a fallback. |
| (b) watched = judged | `js/battle.js` `play` | With `report.battle.spec`, playback is `begin(spec)` + the same `step()`: no `findBattle`, no bias. A report judged in this session (`Game.judgedHere`, a WeakSet, not saved) plays at once; a report that came back from a save is first rerun headless, and if `ver` or `hash` differ (engine changed since the report) it skips straight to the report. `Battle.last()` exposes the played state for tests. |
| (c) loss pay | `js/contract.js` | Lost contract pays `reward × (LOSS_PAY + LOSS_PAY_SHARE × share)` where share = enemy max-hp destroyed (`Stats.foeShare`); a disaster pays only the share part, unless it ended by retreat (then it also gets the base 10%). A note tells the player the share. |
| (c) orderly retreat | `js/contract.js` | A lost battle that ended by retreat (`rec.end === 'retreat'`) costs `RETREAT_MORALE` × the usual morale loss: -3 instead of -6 on a fail, -6 instead of -12 on a disaster whose trainees carried the fallen away. |
| (c) grace week | `js/contract.js`, `js/game.js` `weeklyPayday`, `backPayTotal` | A defeat opens a grace week (`GRACE_DAYS`), at most once per `GRACE_EVERY` days. In it an unpaid merc stays (morale -10) instead of leaving, low-morale desertion is off, and **the unpaid wage is deferred, not forgiven**: it is kept on the merc (`m.owed`, including mercs out on missions) and charged at the next payday together with that week's wages; a merc who cannot be paid then leaves as usual, taking the claim with him. The guild screen shows "(+미룬 급료 N)". Captains' unpaid wages are skipped as they are today in both modes. |
| (c) relief contract | `js/muster.js` `reliefCheck`, called from `fillContracts` | When every merc left is a captain, one easy contract (highest unlocked star still 압도 for the best company, reward ×1.5, 5 days) is posted at the home province; never two at once. |
| (c) debt line | `js/game.js` `nextDay` | Battle mode goes bankrupt below `-max(300, DEBT_WEEKS × weekly wages)` instead of -300. |
| (d) casualties | `js/contract.js` | Fates from the record: downed → injury p 0.6 (won) / 0.9 (lost), 2-4 days, +2 on disaster; standing under 25% hp → p 0.3, 1-2 days; fled → nothing (design §6). Deaths only in special battles (`Game.specialBattle`: boss, final, last chapter of a hero story or a captain story), only on disaster, only downed non-captains, p `DEATH_P` × `mods.death` (× 0.6 sturdy), at most one per company, never with the guild at `GUILD_FLOOR` (3) or fewer. **Every downed merc on a disaster who does not die is injured** (captain, ordinary battle, or a death stopped by the floor or the one-per-company rule; design rule 5). Report members carry `down` / `fled`. External companies lose their downed units, each kept with `EXT_KEEP`, at most `EXT_LOST_CAP`, none on a win. |
| (e) fill-ins | `js/muster.js` `muster` | Trainee level = lowest level among the company's non-captain members (home or sent); a captain-only company gets level-1 trainees. |
| (e) seed salt | `js/contract.js` `makeContract`, `js/muster.js` | `c.bseed = mix(state.salt, c.id)` at creation. Enemy roster seed `mix(contractSalt, 0xf0e)`, battle seed `mix(contractSalt, 0xb7)`, with `contractSalt = mix(c.bseed, c.id)`, so a reposted copy (new id) is a new battle. No day in the seed. |
| (e) monster attack | `js/stats.js` `monsterSkills`; `js/muster.js` | Battle-mode monsters carry `sk` built from the archetype: only `caster` shoots, **bosses included** (fix round): 늪의 마녀 (caster) shoots its basic attack and its curse breath; non-caster bosses use a close area attack whose name follows the sprite (고룡 이그니스 "화염 숨결", 마왕 베르녹스 "마왕의 강타", others "대지 분쇄") — they no longer breathe from range. The forecast reads the same `sk`. 하피, 가고일 (drake) and 마족 전사 (demon) are melee. |
| (f) dispatch UI | `js/ui-tabs.js`, `css/style.css` | Battle mode: "예상 전황 「우세」" plus a five-cell scale, the per-company line shows its word instead of power, the contract card shows "예상 「…」" for the best free company instead of 권장 전투력. Removed in battle mode: power/req bar, "예상 성공률 N%", 인원 부족, 피로한 단원, 적대 지역 lines. Kept: slot count, hero-required, campaign consequence. The headcount warning is gone because the word now carries it (`BM_CAL_HEADS`). |
| (f) recruitment words | `js/captains.js` | Missions decided by battle count `mission.est.band`, mapped by win rate to the old thresholds (fix round): hardStreak (chance < 80%) → 「백중」 이하 연속, gambles (< 40%) → 「백중」 이하, bigGambles (< 25%) → 「열세」 이하. Texts "예상 「백중」 이하 의뢰 연속 성공", "예상 「백중」 이하 의뢰 성공", "예상 「열세」 이하 의뢰 성공". The first mapping (열세 / 무모) asked 거인 and 그림자 여왕 for wins at 0.5-17%. |
| (f) report | `js/ui.js` | Line "출격 때 예상 「…」 · 전투 N초 · 쓰러진 단원 N명"; each downed member shows 쓰러짐 (· 부상 N일). |
| (g) bot | `tools/sim/bot.js` | `--resolve battle` / `SIM_RESOLVE=battle`, `--jobs N`, **`--set KEY=VALUE`** (fix round; unknown names refused). Battle-mode bot: picks the better forecast of the two strongest free companies, takes 우세/압도, 백중 one time in three; does not retake a special contract it just lost at the same or a worse word within 10 days (unless 압도); near darkness (calamity at `CALAMITY_DARKNESS`-2 provinces) it takes the final and calamity campaigns at 백중, and at 열세 one time in three; captain-only companies may go out. Summary adds win by word, day band, kind, tiers, offers/takes by word, **board width** (every 3rd day, before the bot takes anything: ordinary offers by the best own company's word, share of boards with a 열세-or-harder offer, with a 우세-or-easier offer, with both), downed/injured, deaths special/other, loss pay, relief, captain-only days. The "avg success chance" and "final battle" lines print the mean forecast R in battle mode. Roll mode is the old bot (md5 unchanged). |
| (g) shadow tool | `tools/sim/shadow.js` | `--resolve battle` measures the deciding battle (`battleResolve`) with the same tables, invariants (`--check`) and CSV; rows add `cid`, `foeShare`, `special`, `recruits`, `heads`, `need`, `olv` (mean level of ours); `--offers` keeps what the bot looked at but did not send. |

## Data shapes (new or changed)

```js
state.resolve = 'battle'            // absent = roll
state.salt = 1..2^31-2              // per save, drawn when battle mode is switched on
state.graceUntil, state.graceStart  // grace week (days)
contract.bseed                      // mix(state.salt, id, 0x5a17), battle mode only
contract.aim = 0..4                 // the word battleLevel aimed at (board stratification), battle mode only
merc.owed                           // wages deferred in a grace week, charged at the next payday (battle mode)
contract.relief = true              // relief contract
mission.spec (battle mode)          // + bm: 1, kind: 'normal'|'story'|…; monster units + sk; seed has no day
report.battle = { v: 1, ver, tab, hash, winner, t, end, R, band, foeShare, spec }   // ~5 KB while the report waits
report.members[i].down / .fled      // battle mode
Game.capability() -> { companyId, tabs: [{ companyId, R: [, R1 … R14] }] }   // cached per day and merc count, not saved
Game.judgedHere                     // WeakSet of report.battle judged in this session (playback skips the rerun), not saved
```

## Every constant and why (all in `Stats.KN`, settable with `--set` in both tools)

| Constant | Value | Reason |
|---|---|---|
| `BOARD_W` | 0.05 / 0.12 / 0.16 / 0.34 / 0.33 (무모…압도) | Owner decision 1. Sweep (12 × 365, sensible bot): .04/.16/.25/.30/.25 stratified cost the economy (S on day 180, 1 game at A); .05/.12/.16/.34/.33 with 3 extra slots gave the widest board that still reached S on day ~150 in the sweep. |
| `BOARD_TOP` | 3 | Easy offers aim at one of the top 3 so weaker companies have work (with only the best company as reference mid-game contracts fell to 17 per 30 days). Hard offers aim at the best company (verify 3). |
| `BM_BOARD_EXTRA` | 3 | Hard offers no longer replace winnable ones. Sweep (seeds 1-12, day reaching S / gold on day 365): cap +3 with 0 extra slots 162 / 52k, with 2 146 / 63k; cap +4 with 2 161 / 66k, with 3 151 / 81k. |
| `BM_CAP_AHEAD` | 4 | With today's rank + 2 every unlocked star was 압도 for the best company most of the game (capability probe, best company: at rank E every unlocked star ★1-3 압도; at rank B ★1-5 압도 and ★6 우세), so no hard offer could exist (verify 3). +3 left days 1-30 with 8% hard boards; +4 gives 53-69%. |
| `BM_LOW_K` | ★1 0.6, ★2 0.75, ★3 0.9 | A fresh level-1 company forecast R 0.73 (열세) at ★1, so new companies could not work at all. With 0.6 it is 백중-우세. |
| `BM_LATE_STEP` | 3.5 levels per star from ★8 (rounded; ordinary contracts only) | Step 1 made every unlocked star 압도 from day ~180. Step 3 left days 241-365 with hard offers on 26-38% of boards; 3.5 gives 37-56% with gold on day 365 still above HEAD (62k vs 47k, seeds 1-12); 4 gave 65% but 36k. Special contracts keep the old table because their stars come from rank and province. |
| `BM_CAL_ARCH` | soldier 0.98, grunt 1.091, beast 1.048, brute 1.14, armored 1.185, caster 0.945, blob 1.02 | Fitted (see "Calibration"). |
| `BM_CAL_SPECIAL` | boss 0.912, capStory 0.952, story 1.021, final 0.966, campaign 1.009 | Fitted; campaign had no entry before (verify 4). Small samples (boss 304, capStory 499, story 664, final 38 battles). |
| `BM_CAL_HEADS` | 1 member 0.95, 2 members 0.984, 3+ 1 | Verify 1: the retreat rule ends a battle when half of ours are down, so a party of one or two loses as soon as one falls; `margin` does not know that (R50 before: 1.07 / 1.14 / 1.02 / 1.00 for 1 / 2 / 3 / 4 members). The values are small because the level term below took most of the early bias in the joint fit. |
| `BM_CAL_OWNLV` | mean level of ours ≤3 0.879, ≤6 0.928, ≤9 0.946, ≤12 1, ≤16 1.005, above 1.034 | Verify 4 (early game): low-level parties lose more at the same R (R50 before: 1.08 at levels 1-3, 1.02-1.03 at 4-9, 1.00 at 10-16, 0.98 above). A first fit on the enemy level left days 1-30 at 우세 78% on new seeds; the party's own level fixed it (90%). |
| `LOSS_PAY`, `LOSS_PAY_SHARE` | 0.1, 0.5 | Today's 10% plus pay for what was destroyed; half the enemy beaten → 35%. |
| `RETREAT_MORALE` | 0.5 | Verify amendment 1: an orderly retreat should hurt less. Applies to every lost battle that ended by retreat (fix round: also the disaster where only trainees fled). |
| `GRACE_DAYS`, `GRACE_EVERY` | 7, 14 | Amendment 1 (no desertion in the week after a defeat). Back-to-back losses kept the first version's grace open forever. Wages in the week are deferred (fix round, verify 2). |
| `DEBT_WEEKS` | 1 | Wages of mercs away on missions are charged at payday; in the lean mid-game one such payday pushed a guild with 11-18 mercs past -300 (seed 108, day 113, first implementation) although it recovered the next days. |
| `BM_FINAL_K` | 0.5 | The calamity rises around day 160-170 in battle mode (184 in HEAD); the final was R 0.3-0.7 for the three best companies at 0.85 and 2 of 48 games ended in darkness. At 0.5: 0 of 72 (fix round). |
| `INJ_WIN`, `INJ_LOSE`, `INJ_LOW` | 0.6, 0.9, 0.3 | design §6 table. |
| `DEATH_P`, `GUILD_FLOOR` | 0.3, 3 | Today's death chance and design mercy rule 5, applied only to special battles (owner decision 2). |
| `EXT_KEEP`, `EXT_LOST_CAP` | 0.5, 2 | design §6 rule 7. |
| unchanged | `CAL_KIND`, `BANDS`, `GREAT_HP`, `ENEMY_K`, `SUPPORT_K`, `K` | C7 values; the per-word targets are met with the battle-mode calibration tables above. |

### Calibration (fix round)

Scripts in the scratch folder `stage3/fix/tools/`: `fit.js` (logistic R50 and win by word per slice), `calib.js`
(target matching). For each slice of a dimension, `calib.js` picks the factor that brings the slice's win rates
closest to 우세 87% and 백중 50% (weights 2 and 1; 열세 17% and 압도 99% weakly), shrunk towards 1 by n / (n + 150),
alternating the dimensions (heads, our level, archetype, kind) five times. Fitted on seeds 1-24 and 201-212
(36,855 battles: sent + looked at, `shadow.js --resolve battle --offers`), checked on seeds 301-312 and 401-412,
which were not used (23,982 battles). Out of sample, by word:

| Slice | 무모 | 열세 | 백중 | 우세 | 압도 |
|---|---|---|---|---|---|
| all (23,982) | 1% | 16% | 48% | 88% | 100% |
| sent only | – | – | 48% (1,919) | 88% (5,430) | 100% (4,969) |
| days 1-30 / 31-60 (sent) | – | – | 51% / 58% | 90% / 90% | 100% / 99% |
| 1 / 2 / 3 / 4+ members | | | 33% / 33% / 41% / 50% | 94% (18) / 85% (65) / 86% / 88% | |
| caster / soldier / grunt | | | 54% / 50% / 43% | 84% / 85% / 91% | |
| campaign / capStory | | | 50% / 55% | 84% (124) / 88% (178) | |
| story / boss | | | 46% / 56% | 78% (214) / 74% (93) | |

Before the fix round the same out-of-sample check (verify, seeds 201-212) read: days 1-30 우세 67%, caster 77%,
campaign 78%, captain alone or with one member 74%. Story and boss stay below target: their outcome curves are
flat (logistic slope 6-9 against 13 for ordinary contracts, a boss has 7× hp and wide swings), so one factor
cannot hold both 우세 and 백중, and the in-sample and out-of-sample fits pull in opposite directions (boss 1.02 vs
0.985, story 1.016 vs 0.973). Left for stage 4.

## Measured results (fix round, final constants)

Commands (all from the repo root; outputs in the scratch folder `stage3/fix/acc2/`):

```
SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum                     # roll: ddfdfe7b437fbe9fcf25f166ba542fce
SIM_JSON=1 SIM_SHADOW=1 node tools/sim/bot.js 6 200 | md5sum        # roll + shadow: same md5
node tools/sim/battle.js 400                                         # legacy replay: miss 0/0/0/0
node tools/sim/shadow.js 6 200 --check --jobs 4                      # roll shadow invariants: all 0 (2,150 battles)
node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4     # battle invariants: all 0 (2,955 battles)
SIM_SEED=1 node tools/sim/bot.js 12 365 --resolve battle --jobs 4    # also 13, 101, 113, 201, 301 (72 games, about 70 s per 12 on 4 cores)
node tools/sim/shadow.js 12 365 --seed0 301 --resolve battle --offers --jobs 4   # word tables and calibration
```

### Roll mode unchanged

- Bot md5 `ddfdfe7b437fbe9fcf25f166ba542fce` with and without the shadow battle; `battle.js 400` miss 0 in all four outcomes.
- `shadow.js 6 200 --check`: 0 violations in 2,150 battles and 6,013 alternative parties.
- Every new path is gated by `state.resolve === 'battle'` or by a battle-mode spec (`spec.bm`); `m.owed` and
  `backPayTotal()` are 0 in roll saves, so the payday arithmetic is the same.

### Battle mode, sensible bot, 72 games of 365 days

| Seeds | 1-12 | 13-24 | 101-112 | 113-124 | 201-212 | 301-312 |
|---|---|---|---|---|---|---|
| Final rank / game overs | S 12 / 0 | S 12 / 0 | S 12 / 0 | S 12 / 0 | S 12 / 0 | S 12 / 0 |
| Day reaching B / S | 75 / 141 | 70 / 130 | 62 / 120 | 73 / 142 | 70 / 130 | 71 / 137 |
| Gold day 60 / 120 | 1,852 / 6,412 | 2,037 / 3,427 | 2,399 / 5,177 | 1,602 / 2,394 | 2,015 / 6,804 | 1,631 / 3,122 |
| Gold day 240 / 365 | 26,418 / 62,243 | 34,445 / 86,676 | 23,920 / 60,815 | 15,301 / 42,582 | 45,797 / 112,658 | 39,191 / 112,757 |
| Captains at the end | 6.25 | 6.83 | 6.08 | 5.42 | 6.42 | 6.67 |
| Contracts completed / failed | 402 / 75 | 407 / 76 | 432 / 66 | 417 / 77 | 451 / 67 | 435 / 71 |
| Win 백중 / 우세 / 압도 | 48.3 / 86.4 / 99.6 | 47.3 / 86.9 / 99.8 | 54.0 / 89.2 / 99.7 | 44.4 / 86.3 / 99.6 | 46.8 / 90.0 / 99.8 | 47.7 / 87.8 / 99.7 |
| Win days 1-30 / 31-60 / 61-120 / 121-240 / 241-365 | 90 / 87 / 86 / 85 / 83 | 88 / 88 / 86 / 86 / 81 | 94 / 87 / 88 / 88 / 84 | 87 / 87 / 85 / 85 / 83 | 88 / 87 / 87 / 88 / 86 | 88 / 90 / 87 / 86 / 84 |
| Board with a ≤열세 and a ≥우세 offer, days 1-30 / 61-120 / 241-365 | 53 / 64 / 46% | 59 / 63 / 43% | 57 / 64 / 36% | 48 / 66 / 44% | 57 / 63 / 28% | 53 / 57 / 35% |
| Downed / injured per member-battle | 14.4 / 7.4% | 12.7 / 6.4% | 12.4 / 6.4% | 12.9 / 6.4% | 11.3 / 5.8% | 12.2 / 6.5% |
| Deaths per game, special / other | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Reference: HEAD roll mode (C4, `docs/agents/reports/codex.md`) seeds 1-12: S on day 73, gold 5,340 / 19,741 on
days 60 / 120 and 46,779 on day 365, 5.25 captains; seeds 101-112: S 69, 5,637 / 19,434 / 51,930, 5.42. The first
stage-3 implementation (seeds 1-12 / 101-112): S 150 / 140, gold day 120 1,944 / 2,980, day 365 49,849 / 69,762,
3.67 / 3.08 captains; verify measured it on seeds 201-212 / 301-312 at S 153 / 148, day 365 41,330 / 19,434.

Board width (seeds 1-12, ordinary offers by the best own company's word, every 3rd day before the bot takes any):
offers per board 무모 / 열세 / 백중 / 우세 / 압도 = 0.34 / 0.49 / 0.53 / 0.86 / 1.73 on days 1-30 and
0.28 / 0.66 / 0.76 / 1.34 / 1.92 on days 241-365; boards with a 열세-or-harder offer 59 / 65 / 84 / 72 / 56% by
day band (verify, first implementation: 0 / 8 / 27 / 25 / 17%).

The early game is no longer hard for a sensible player: days 1-30 are won 87-94% (feasibility: 35-47%).
Mid-game gold is still well below roll mode (day 120: 2.4-6.8k vs 19k), and S comes 50-70 days later; late gold
is above HEAD (42-113k vs 47-52k on day 365).

### Other strategies (seeds 201-212, verify's `vbot.js`, before → after the fix round)

| Strategy | Final ranks | 우세 win | Notes |
|---|---|---|---|
| captains only (verify 1) | S 3, A 7, dark 2 → S 9, A 1, dark 2 | 75.7% → 89.3% | the word now holds for small parties |
| only 압도 (verify 2) | S 11, A 1 → S 11, dark 1 | – | never takes the final at a lower word |
| takes every offer | S 11, B 1 → S 3, B 1, E 1, D 1, F 4, bankrupt 1, dark 1 | 84.0% → 88.8% | the wider board puts 0.3-1.0 무모 offers on the board every day; this bot takes them all and loses them |

The last row is the price of the wide board: a player who ignores the words and takes every 「무모」 offer loses
most of them and can go broke. Roll mode's reckless bot ends S 12 / 0. Whether a 무모 loss should cost less, or the
board show fewer of them, is an owner decision for stage 4.

### Determinism: watched battle = judged battle

- `shadow.js 6 365 --resolve battle --check`: 2,955 deciding battles, rerun / JSON round trip / stepped / +2.2 s
  after the end all 0 mismatches; enemy roster changed with the party 0 of 8,477 alternative parties; spec changed
  between dispatch and return 0; `Math.random` calls and state changes inside muster/battle 0.
- Browser (Chrome, `?resolve=battle`, final constants, scratch `stage3/fix/tools/br.js` and `browser2.js`):
  - 1280×800: a win judged in this session plays without the rerun (`judgedHere`); played hash 3873381435 = judged.
  - 400×800: page reloaded in the middle of playback, so the report came back from the save and was rerun first;
    played hash 1123605686 = judged = the hash computed right after dispatch.
  - 1280: a 무모 raid lost by retreat; played hash = judged; the report shows "쓰러짐 · 부상 3일" for both downed
    members, 88 gold loss pay (7% of the enemy beaten) and the grace week opened.
  - A report whose `report.battle` was replaced by a copy with a wrong hash (an old report after an engine change)
    goes straight to the report with no canvas.
  - No page errors, no horizontal overflow. Dispatch shows "예상 전황 「압도」" and the five-cell scale; no %,
    성공률 or 전투력. Contract cards read "예상 「…」" (one day-4 board at 400: 압도 ×4, 백중, 무모).

### Next-day cost

Node, unthrottled, the day-200 save of verify: `capability()` 12-23 ms (once a day), `fillContracts` 8 ms, one
returning battle 29 ms on average over 2,955 battles (shadow tool) and 88 ms for the long one in that save.
Playback no longer reruns the battle for a report judged in the same session. Verify measured 261 ms for a
next day with one returning battle under Chrome CPU ×4 throttling; a phone measurement is still open.

### Unit checks (scratch `stage3/fix/tools/unit.js`, all pass)

- Grace defers: 7 broke mercs all stay, 158 gold of wages is deferred; at the next payday, with the money, the
  guild pays the week plus the 158 (362 in all) and the claims are cleared. With only one week's money the mercs
  who cannot be paid in full leave (7 → 4).
- Exploit probe (verify's `grace.js`, 15 days from the day-200 save): opening the grace week as a defeat would
  ends exactly like no defeat a week later (−1000 gold: 2 mercs left in both; −3000: bankrupt on day 204 without,
  day 211 with).
- A captain alone whose trainees fled: disaster, morale -6 (not -12), 25 gold (10% + share) on a 60-gold contract.
- 30 forced special disasters with a 3-merc guild (floor): 0 deaths, 90 of 90 downed members injured.
- A roll-mode mission returning in battle mode is decided by the roll; a battle-mode mission returning in roll
  mode by its battle.
- 늪의 마녀: caster, basic shot + 파멸의 숨결 shot; 고룡 이그니스 / 마왕 베르녹스 / 고블린 왕: melee + melee area attack.
- `battleCap()` = 4 at rank F; 60 boards of 8 ordinary slots: every board has a hard and an easy aim.
- Recruitment: wins at 백중, 열세, 우세 → hardStreak 2, gambles 2, bigGambles 1.
- `judgedHere` holds the report judged in this session and not a JSON copy of it.
- From the first implementation (`stage3/implement/unit.js`, still valid): relief contract, fill-in levels, salt
  stability, attack mode of ordinary monsters, deaths only in special battles and at most one per company.

## Deviations from design.md

| # | Design | Built | Why |
|---|---|---|---|
| 1 | Flag is a constant in `js/contract.js`, not saved | Saved getter `Game.RESOLVE` (`state.resolve`) | Task: a saved switch with a test param. |
| 2 | Enemy strength from star × req, one ELV table | Battle mode: `BM_LOW_K` for ★1-3 and `BM_LATE_STEP` 3.5 for ordinary contracts; specials keep the old table | Owner decision 1 and the measured flat late curve; specials' stars are not chosen by the board. |
| 3 | Contract levels from rank and province tier | Battle mode: a stratified board on the forecast of the top 3 companies (hard words on the best one), capped at rank + 4, three more ordinary slots | Owner decision 1. Province tier no longer bounds the star. |
| 4 | Death on any disaster with mercy rules 1-5 | Only special battles; ordinary disasters injure | Owner decision 2. |
| 5 | Forecast = `margin × CAL_KIND` | × `BM_CAL_ARCH` × `BM_CAL_SPECIAL` × `BM_CAL_HEADS` × `BM_CAL_OWNLV` for battle-mode specs | The archetype attack mode moved R50 per archetype; small parties and low-level parties lose more at the same R (verify 1, 4). |
| 6 | Fatigue ≥ 80 injury ×1.5 | Dropped in battle mode | Not in the design's casualty table (as feasibility). |
| 7 | Replay reruns headless and compares the hash | Same; on mismatch the report opens at once | – |
| 8 | Betrayal rolled at muster | Still rolled at resolve, marked on a copy of the spec, and that copy is what the report replays | Keeps the roll stream; the replay still equals the judgement. |
| 9 | Recruitment counters on `est` with R edges 1.15 / 0.87 / 0.67 | On `est.band` (C7 edges) | Same words as the screen. |
| 10 | `report.verdict` | Fates are written into `report.members[].down/fled`; `report.battle` holds the record summary | The report UI reads members. |
| 11 | Economic mercy (verify amendment 1) | Built plus two additions found by measurement: grace at most every 14 days without debt, and a debt line of one week of wages | Without them 3 of 48 games ended. |
| 12 | Monster attack by template | By archetype in battle mode only, bosses included | Task (e); roll-mode shadow stays comparable to C7. |
| 13 | – | The mode at dispatch decides a mission | Verify 7: a roll-era spec judged as a battle read 무모 and lost. |
| 14 | Recruitment counters with R edges | Word edges chosen by win rate (≤백중, ≤백중, ≤열세) | The literal mapping made two captains unreachable. |
| 15 | Grace week: no desertion | Plus deferred wages (`m.owed`) | Verify 2: forgiveness made a well-timed defeat pay. |

## Verify findings and what was done

| # | Finding | Done |
|---|---|---|
| 1 | Word too optimistic for parties of 1-2 (우세 64-74%) | **Fixed**: `BM_CAL_HEADS` and `BM_CAL_OWNLV`. Out of sample 우세 94% (1 member, n=18), 85% (2, n=65); the captains-only bot 89.3% (was 75.7%). |
| 2 | Grace week forgave wages; a defeat at the right moment paid | **Fixed**: unpaid wages are deferred on the merc and charged at the next payday; probe shows the same end state one week later. Not changed: mercy only after a defeat (the owner rule); a guild that never loses gets the relief contract and the debt line. |
| 3 | Board seldom wide (0-27% with a hard offer) | **Fixed**: stratified board, hard words on the best company, cap rank + 4, 3 extra slots, `BM_LATE_STEP` 3.5. Boards with a 열세-or-harder offer 37-85% by day band and seed set, both kinds 28-66%. Late boards are the narrowest (★14 is the ceiling). |
| 4 | Calibration off by slice out of sample | **Fixed for** early game, caster, campaign, small parties (see "Calibration"); **open for** story and boss (flat outcome curves). |
| 5 | Economy leaner than reported | **Improved** by the extra board slots and the higher cap (more paying work): day 365 gold 42-113k vs HEAD 47-52k, S on day 120-142, 5.4-6.8 captains (first implementation 2.8-3.7). Day 60-120 gold is still 3-6× below roll mode; left as an owner decision (stage 4). |
| 6 | Next-day cost on a phone | **Partly fixed**: playback skips the rerun for a report judged in this session. The deciding battle itself (29 ms mean in node) is the stage's cost; phone measurement open. |
| 7a | Disaster after an orderly retreat | **Fixed**: retreat cushion (morale, base pay) for every lost battle that ended by retreat; the tier stays disaster because nobody of ours stood (design §5). |
| 7b | Old roll-era mission judged as a battle after the switch | **Fixed**: the mode at dispatch decides. |
| 7c | Bosses follow the template | **Fixed**: caster boss shoots, non-caster bosses use a close area attack. |
| 7d | Floor-stopped death only 90% injured | **Fixed**: every downed merc on a disaster who does not die is injured. |
| 7e | Waiting a day changes the battle | **Rejected**: only the party's fatigue / morale changed, the enemy and seed did not (0 of 147 + 67), equal spec gives equal hash, and the outcome is hidden before dispatch, so there is nothing to exploit; freezing the party a day early would show stale numbers. |
| 7f | Board cards read the best free company only | **Rejected**: the card answers "can I win this now with who is home", which is what the player can act on; with the strong companies out it should read hard. |

## What remains

Stage 4 (flip the default to `'battle'`):
- Mid-game economy: **done** (owner decision 5, see "Mid-game economy (owner decision 5)" below): S on day ~102
  instead of ~132 (every one of 14 sets on day 95-108), day 1-59 and 121+ rewards unchanged. Owner call still open:
  the faster rank puts more 무모 offers on the day 61-120 boards (see "Side effect on 무모 offers" there).
- The reckless strategy (takes every offer, including 무모) can go broke or fall to darkness. Owner decision 6 keeps
  무모 offers and their loss cost as they are (the word is the warning); after decision 5 the reckless bot ends
  S 1, A 2, B 4, D 1, F 2, bankrupt 2 (seeds 201-212).
- Forecast for story and boss contracts: 우세 wins 74-82%; needs a term for boss-scale enemies or a stricter
  mapping for special kinds. Special samples are small (boss 67-96, final 10-13 per 12 games).
- Late boards are the narrowest (hard offers on 37-56% of boards on days 241-365): the strongest companies outgrow
  ★14; owner decision 1 says enemies do not follow the roster, so the remedy would be content (higher stars).
- Captain-less strength and power displays still use the old power numbers (`js/ui-tabs.js` company tab, final
  battle line "요구 전투력"), and trait/class texts still say "성공률 +N%" (`js/data.js`, `js/classes.js`).
- The merc card shows two 체력 rows (attribute and battle); rename the battle row.
- Next-day cost on a phone (one battle per returning contract plus the daily capability table).
- Antigravity play test of about 100 days in battle mode (design stage 4; queued as Q5).
- New md5 baseline for battle mode once the constants settle; flip the default and keep `'roll'` as the undo.

Stage 5 (tactics): synergy bonuses for allies only, measured so that 30-50% of a well-built company's damage dealt
or avoided comes from tactics (owner decision 4); then re-fit `BANDS` / calibration so that a plain company still
wins 85-90% at 우세, and retune the recruitment gamble counters.

## Mid-game economy (owner decision 5)

Owner decision 5 (2026-11-27): in battle mode raise only the rewards of days 60-120 a little, so that S is reached
around day 90-110 (bot average), keep days 1-59 and 121+ as they are, do not go back to roll mode's speed (S ~73), and
keep day-365 gold from ballooning (per-set average within about +25%). Decision 6: 무모 offers stay as they are
(frequency and loss cost). Forecast words, `BANDS`, calibration, the board code, casualty rules and the loss cushion
are not touched.

### The lever

`js/contract.js` `makeContract`: in battle mode a contract **with a deadline** created on day d gets

```
gold reward × (1 + BM_MID_PAY × midBoost(d))      reputation (명성) × (1 + BM_MID_REP × midBoost(d))
midBoost(d) = 0 up to day 59, rises linearly to 1 on day 72, 1 until day 110, falls linearly to 0 on day 121
```

- `midBoost` is `Game.midBoost(day)` (`BM_MID_DAYS` = the four corners of the trapezoid). Values on day
  59 / 60 / 65 / 72-110 / 115 / 120 / 121: 0 / 0.08 / 0.46 / 1 / 0.55 / 0.09 / 0 (at most 0.09 a day: no cliff).
- The factor goes into the contract's own `reward` and `rep` when it is made, before the special multipliers
  (campaign ×1.8 / rep ×2, relief ×1.5). The card shows exactly what is paid on a win ("보상 N", "명성 +N";
  `js/ui-tabs.js`), and a posted contract never changes its price.
- **No-deadline contracts get no boost** (`opts.noDeadline`: hero story, captain story, boss, final — the four
  callers that set `expires = STORY_EXPIRES`). Otherwise a story or boss contract posted inside the window could be
  held and paid after day 121 (verify found boosted story / boss contracts paid on days 124-196). Normal contracts
  expire after 3-6 days and campaigns after 5, so a boosted contract is always taken by day ~127.
- **A failure costs the unboosted 명성** (owner decision 6): the contract stores `repMul` (battle mode, window
  only) and the rep lost on a failure is 30% / 60% of `rep / repMul`, the same as without the change. The extra
  명성 is paid only for a win. The loss cushion (gold on a lost fight, `LOSS_PAY` + `LOSS_PAY_SHARE` × share of the
  posted `reward`) keeps its rule; it is a payment, not a cost, and its share of the card is unchanged.
- Roll mode never reaches any of this (`s.resolve === 'battle'` first; `repMul` is never set, so the failure line
  computes `c.rep` exactly as before).

Why this lever:
- **Rank is reputation only** (`RANKS` in `js/data.js`: S at 3,200 rep). Gold does not move S: gold ×1.5 alone on days
  60-120 left S at 140 (141) and raised day-365 gold by 44% (seeds 1-12). So the S target needs a rep term; gold gets a
  small one so the mid-game purse is a bit less lean, as the decision asks ("rewards").
- Both numbers are printed on the card, so the player sees what the contract gives; there is no hidden multiplier on
  payout. A day ramp, not a rank ramp: a rank ramp would cut pay at the moment of promotion to S (a punishment for
  success) and would move with the player, while the owner's window is in days.
- Trapezoid, not a step: 13 days in (59 → 72), 11 days out (110 → 121). The hold runs to day 110 because S lands
  around day 100: with the hold ending on day 105 (`[59,72,105,121]`) S came on day 112.
- **"A little" is gold, not 명성**: gold is ×1.25 at the peak, 명성 ×3.25. Moving S by ~30 days with a 60-day window
  needs a large rep factor; this is the visible cost (see "What a player sees").

### Constants (all in `Stats.KN`, settable with `--set` in `bot.js` and `shadow.js`; unknown names, wrong types and wrong array lengths are refused)

| Constant | Value | Reason |
|---|---|---|
| `BM_MID_PAY` | 0.25 (gold ×1.25 at the peak) | Day-120 gold 4.8k → 7.3k (roll mode 19k, so still slower than roll). 0.5 did not move S and only added late gold. |
| `BM_MID_REP` | 2.25 (rep ×3.25 at the peak) | Puts S into 90-110. With the no-deadline exemption and the unboosted loss: 2 gave S 112 / 108, 2.25 gave 105 / 105, 2.5 gave 107 / 101 (seeds 1-12 / 13-24). |
| `BM_MID_DAYS` | [59, 72, 110, 121] | Days 1-59 and 121+ unchanged (factor exactly 1); ramps of 13 / 11 days. |

Sweep, first round (seeds 1-12 only, 12 × 365, before the no-deadline exemption and the unboosted loss; baseline S 141,
gold day 120 6,412, day 365 62,243):

| PAY / REP / days | B / A / S | Gold day 120 / 365 |
|---|---|---|
| 0.5 / 0 / [59,75,105,121] | 74 / 105 / 140 | 10,686 / 89,809 |
| 0.5 / 0.5 / same | 71 / 96 / 123 | 10,729 / 106,604 |
| 0.3 / 0.8 / same | 71 / 97 / 126 | 7,687 / 87,731 |
| 0 / 1 / same | 69 / 98 / 127 | 4,788 / 103,170 |
| 0 / 1.5 / same | 68 / 91 / 111 | 3,729 / 88,699 |
| 0 / 2 / same | 67 / 86 / 109 | 5,749 / 77,659 |
| 0 / 1.5 / [59,70,108,121] | 67 / 87 / 117 | 6,579 / 67,761 |
| 0.25 / 1.5 / [59,72,105,121] | 69 / 88 / 112 | 7,187 / 98,958 |
| 0.25 / 2 / [59,75,105,121] | 69 / 86 / 112 | 7,330 / 73,780 |
| 0.25 / 2 / [59,72,110,121] | 66 / 87 / 107 | 8,804 / 88,914 |
| 0.25 / 2.5 / [59,72,108,121] | 66 / 83 / 103 | 9,486 / 121,800 |

Second round (final code; seeds 1-12 / 13-24, PAY 0.25, days [59,72,110,121]):

| REP | Day S | Gold day 365 |
|---|---|---|
| 2 | 112 / 108 | 76,155 / 45,857 |
| **2.25 (chosen)** | 105 / 105 | 73,432 / 55,724 |
| 2.5 | 107 / 101 | 87,602 / 34,049 |

### Before → after (sensible bot, 12 × 365 per set, `SIM_RESOLVE=battle`)

- Tuning sets: 1-12 and 13-24.
- **Never used while tuning by anyone**: 6001, 7001, 8001 (36 games, run once with the final values).
- Earlier check sets (used to check the first round, not to tune it or the second round): 501, 601, 701, 801, 901,
  1001, 2001, 3001, 4001.
- "Before" = the same code with `--set BM_MID_PAY=0 --set BM_MID_REP=0`: the factor is then exactly 1, `repMul` is 1,
  and the games are identical to the stage-3 code (seeds 1-12 and 13-24 reproduce the stage-3 table above; 2001
  reproduces verify's run).
- Deaths: 0 special / 0 other per game in every set, before and after.

| | 1 | 13 | 6001 | 7001 | 8001 | 2001 | 3001 |
|---|---|---|---|---|---|---|---|
| Final rank | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 11, bankrupt 1 → S 12 | S 12 → S 12 | S 12 → S 12 |
| Day B / A / S | 75 / 108 / 141 → 67 / 86 / 105 | 70 / 98 / 130 → 66 / 85 / 105 | 64 / 95 / 125 → 62 / 80 / 95 | 69 / 103 / 135 → 64 / 82 / 103 | 74 / 111 / 139 → 68 / 84 / 105 | 70 / 105 / 139 → 65 / 84 / 108 | 62 / 91 / 123 → 61 / 76 / 95 |
| Gold d60 / d90 / d120 | 1,852 / 3,934 / 6,412 → 1,852 / 4,356 / 7,034 | 2,037 / 4,178 / 3,427 → 2,037 / 3,925 / 5,349 | 1,960 / 4,178 / 6,408 → 1,960 / 5,255 / 8,051 | 2,047 / 3,533 / 2,873 → 2,047 / 4,484 / 6,159 | 2,177 / 3,545 / 4,145 → 2,177 / 3,848 / 8,066 | 2,046 / 3,362 / 3,559 → 2,046 / 5,250 / 6,743 | 2,083 / 3,914 / 5,540 → 2,083 / 3,793 / 8,145 |
| Gold d180 / d365 | 16,116 / 62,243 → 21,772 / 73,432 | 22,037 / 86,676 → 17,459 / 55,724 | 25,005 / 106,205 → 22,013 / 109,444 | 12,404 / 55,227 → 16,831 / 57,730 | 14,012 / 49,376 → 13,964 / 72,794 | 14,459 / 61,287 → 17,839 / 65,938 | 26,181 / 76,332 → 23,892 / 67,468 |
| Captains | 6.25 → 5.75 | 6.83 → 6.25 | 6.92 → 7.17 | 6.67 → 6.25 | 5.00 → 5.92 | 5.75 → 5.75 | 6.83 → 6.92 |
| Completed / failed | 402 / 75 → 443 / 73 | 407 / 76 → 423 / 74 | 461 / 73 → 492 / 69 | 434 / 59 → 423 / 72 | 376 / 65 → 435 / 72 | 420 / 74 → 414 / 75 | 465 / 64 → 460 / 72 |
| Deaths sp/other | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 |
| Win 백중 / 우세 / 압도 | 48.3 / 86.4 / 99.6 → 46.5 / 88.4 / 99.7 | 47.3 / 86.9 / 99.8 → 46.5 / 86.4 / 99.7 | 47.0 / 88.2 / 99.8 → 49.3 / 89.1 / 99.8 | 55.3 / 89.8 / 99.9 → 49.1 / 88.6 / 99.8 | 49.0 / 88.2 / 99.5 → 47.8 / 88.3 / 99.6 | 48.1 / 87.3 / 99.7 → 46.3 / 86.4 / 99.6 | 52.0 / 90.8 / 99.6 → 50.0 / 88.7 / 99.5 |
| Win days 1-30/31-60/61-120/121-240/241-365 | 90 / 86 / 86 / 85 / 83 → 90 / 86 / 88 / 87 / 83 | 88 / 88 / 86 / 86 / 81 → 88 / 88 / 86 / 84 / 84 | 93 / 92 / 87 / 84 / 86 → 93 / 92 / 87 / 88 / 86 | 91 / 89 / 86 / 89 / 88 → 91 / 89 / 84 / 85 / 86 | 89 / 88 / 86 / 86 / 83 → 89 / 88 / 86 / 86 / 85 | 88 / 93 / 86 / 86 / 83 → 88 / 93 / 84 / 86 / 82 | 92 / 90 / 87 / 88 / 88 → 92 / 90 / 86 / 86 / 86 |
| 무모 per board d61-120 / 무모 offers per game | 1.04 / 221 → 1.05 / 230 | 0.93 / 222 → 1.27 / 225 | 0.63 / 244 → 1.02 / 251 | 0.87 / 234 → 1.03 / 220 | 1.07 / 198 → 1.18 / 211 | 0.92 / 224 → 1.08 / 240 | 0.64 / 239 → 1.00 / 247 |

| | 4001 | 501 | 601 | 701 | 801 | 901 | 1001 |
|---|---|---|---|---|---|---|---|
| Final rank | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 |
| Day B / A / S | 74 / 106 / 135 → 67 / 84 / 108 | 63 / 95 / 125 → 61 / 79 / 97 | 69 / 104 / 136 → 64 / 82 / 103 | 70 / 98 / 133 → 67 / 83 / 102 | 68 / 104 / 134 → 64 / 83 / 105 | 64 / 102 / 127 → 60 / 78 / 95 | 75 / 105 / 132 → 69 / 84 / 105 |
| Gold d60 / d90 / d120 | 1,969 / 3,598 / 3,720 → 1,969 / 3,460 / 3,814 | 2,214 / 4,381 / 6,147 → 2,214 / 4,424 / 9,671 | 2,318 / 3,114 / 3,823 → 2,318 / 3,736 / 5,165 | 1,949 / 3,756 / 2,844 → 1,949 / 3,836 / 5,277 | 2,345 / 4,043 / 2,995 → 2,345 / 4,694 / 6,582 | 2,296 / 4,063 / 7,025 → 2,296 / 4,104 / 11,930 | 1,918 / 4,432 / 8,677 → 1,918 / 3,443 / 10,021 |
| Gold d180 / d365 | 16,769 / 71,071 → 15,497 / 72,945 | 16,528 / 90,315 → 28,785 / 101,532 | 16,336 / 123,807 → 23,175 / 123,970 | 16,554 / 47,466 → 15,975 / 69,208 | 18,596 / 88,024 → 16,747 / 72,347 | 27,684 / 109,348 → 29,081 / 131,238 | 23,776 / 103,641 → 26,383 / 68,809 |
| Captains | 6.33 → 6.67 | 6.67 → 6.25 | 6.75 → 6.42 | 5.75 → 5.67 | 6.75 → 6.58 | 7.00 → 6.58 | 6.42 → 6.25 |
| Completed / failed | 428 / 68 → 414 / 74 | 460 / 68 → 454 / 73 | 436 / 67 → 451 / 76 | 407 / 79 → 410 / 83 | 446 / 76 → 435 / 65 | 452 / 67 → 454 / 73 | 424 / 70 → 434 / 67 |
| Deaths sp/other | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 |
| Win 백중 / 우세 / 압도 | 49.5 / 88.0 / 99.7 → 45.5 / 86.6 / 99.8 | 51.2 / 89.1 / 99.8 → 52.3 / 88.8 / 99.5 | 53.7 / 89.5 / 99.6 → 52.5 / 87.0 / 99.4 | 44.5 / 86.4 / 99.8 → 43.9 / 86.9 / 99.6 | 47.3 / 86.6 / 99.6 → 50.9 / 87.8 / 99.6 | 53.9 / 89.5 / 99.8 → 53.1 / 89.3 / 99.6 | 48.4 / 88.8 / 99.8 → 49.2 / 88.1 / 99.8 |
| Win days 1-30/31-60/61-120/121-240/241-365 | 88 / 88 / 86 / 87 / 85 → 88 / 88 / 85 / 85 / 84 | 91 / 91 / 88 / 87 / 86 → 91 / 91 / 86 / 87 / 84 | 90 / 88 / 86 / 87 / 86 → 90 / 88 / 87 / 86 / 84 | 86 / 88 / 87 / 84 / 81 → 86 / 88 / 86 / 85 / 80 | 91 / 91 / 85 / 86 / 84 → 91 / 91 / 85 / 86 / 87 | 89 / 91 / 86 / 87 / 87 → 89 / 91 / 87 / 86 / 85 | 90 / 88 / 86 / 87 / 83 → 90 / 88 / 88 / 85 / 87 |
| 무모 per board d61-120 / 무모 offers per game | 0.85 / 223 → 1.14 / 235 | 0.90 / 238 → 1.01 / 221 | 0.73 / 222 → 1.18 / 242 | 1.05 / 228 → 1.23 / 200 | 0.74 / 230 → 1.02 / 233 | 0.92 / 234 → 1.07 / 218 | 0.97 / 235 → 0.88 / 230 |

Day-365 gold change per set: 1 +18%, 13 −36%, 6001 +3%, 7001 +5%, 8001 +47%, 2001 +8%, 3001 −12%, 4001 +3%,
501 +12%, 601 0%, 701 +46%, 801 −18%, 901 +20%, 1001 −34%.

Means over the sets (before → after):

| | Tuning (24 games) | Never used (36) | Earlier check (108) | All (168) |
|---|---|---|---|---|
| Day reaching B / A / S | 73 / 103 / 136 → 67 / 86 / 105 | 69 / 103 / 133 → 65 / 82 / 101 | 68 / 101 / 132 → 64 / 81 / 102 | 69 / 102 / 132 → 65 / 82 / 102 |
| Gold day 60 | 1,945 → 1,945 | 2,061 → 2,061 | 2,126 → 2,126 | 2,087 → 2,087 |
| Gold day 90 / 120 | 4,056 / 4,920 → 4,141 / 6,192 | 3,752 / 4,475 → 4,529 / 7,425 | 3,851 / 4,926 → 4,082 / 7,483 | 3,859 / 4,828 → 4,186 / 7,286 |
| Gold day 180 | 19,077 → 19,616 | 17,140 → 17,603 | 19,654 → 21,930 | 19,033 → 20,672 |
| Gold day 365 | 74,460 → 64,578 (−13%) | 70,269 → 79,989 (+14%) | 85,699 → 85,939 (+0.3%) | 80,787 → 81,613 (+1.0%) |
| Captains at the end | 6.5 → 6.0 | 6.2 → 6.4 | 6.5 → 6.3 | 6.4 → 6.3 |
| Game overs | 0 → 0 | 1 (bankrupt) → 0 | 0 → 0 | 1 → 0 |
| Win 백중 / 우세 / 압도 | 47.8 / 86.7 / 99.7 → 46.5 / 87.4 / 99.7 | 50.4 / 88.7 / 99.7 → 48.7 / 88.7 / 99.7 | 49.8 / 88.4 / 99.7 → 49.3 / 87.7 / 99.6 | 49.7 / 88.2 / 99.7 → 48.8 / 87.9 / 99.6 |
| Win days 1-30 / 31-60 / 61-120 / 121-240 / 241-365 | 89.2 / 87.4 / 85.7 / 85.1 / 82.0 → 89.2 / 87.4 / 86.5 / 85.9 / 83.8 | 90.9 / 89.7 / 86.2 / 86.5 / 85.7 → 90.9 / 89.7 / 85.4 / 86.2 / 85.7 | 89.4 / 89.7 / 86.2 / 86.4 / 84.8 → 89.4 / 89.7 / 85.9 / 85.8 / 84.3 | 89.7 / 89.4 / 86.1 / 86.3 / 84.6 → 89.7 / 89.4 / 85.9 / 85.9 / 84.6 |
| 무모 per board, days 61-120 / 무모 offers per game | 0.99 / 222 → 1.16 / 228 | 0.86 / 225 → 1.08 / 227 | 0.86 / 230 → 1.07 / 230 | 0.88 / 228 → 1.08 / 229 |

Reading:
- **S on day 95-108 in every one of the 14 sets** (was 123-141); 102 over all 168 games, 101 on the 36 never-used
  games. A comes ~20 days earlier, B ~4 days earlier (the ramp starts on day 60, B is at ~65-70). Roll mode stays
  faster (S ~73). Per game S still spreads widely (74-174 after).
- Day 60 gold and the day 1-30 / 31-60 win rates are identical in every set (nothing before day 60 changed). Day 90
  gold +8%, day 120 gold +51% (4.8k → 7.3k), still well under roll mode's 19k.
- **Day-365 gold**: +1.0% over all 168 games, +14% on the never-used sets, −13% on the tuning sets. Per set it moves
  −36% to +47%; 2 of 14 sets are above +25% (701 +46%; 8001 +47%, whose "before" includes a game that went bankrupt
  and stopped earning), 2 are below −25% (13 −36%, 1001 −34%). This is noise, not the lever: per-game standard deviation of day-365 gold is
  43-160k, so a 12-game set mean has a standard error of 13-46k (15-45% of the mean), and any change to the economy
  reshuffles every later game (the gold-only run with S unchanged moved set 1 by +44%). The per-set bound read
  strictly is missed on 2 of 14 sets; the pooled change is well inside it.
- Word win rates do not move pooled (백중 49.7 → 48.8, 우세 88.2 → 87.9, 압도 99.7 → 99.6). Per set 백중 moves up to
  −6.2 points (7001: 55.3 → 49.1; with n ≈ 900 per set the standard error of a before/after difference is ~2.4 points) and 우세 up to −2.5
  (601). Win by day band moves −4.0 to +3.6 points per set (7001 days 121-240 −4.0, 6001 days 121-240 +3.6),
  at most 0.8 pooled.
- Game overs 1 → 0 (the first round had one darkness on seed 811; with the final code seed 801-812 end S 12).

### Side effect on 무모 offers (owner call)

The change does not touch the board code, `BOARD_W`, the words or the 무모 loss. But the guild now reaches each rank
earlier and therefore **weaker**, while the star cap is rank + `BM_CAP_AHEAD` (`battleCap`, `js/muster.js`) and
provinces open by rank. A board slot that aims at 무모 then finds a 무모 star more often (before, with the low cap, it
fell back to the cap's top stars).
- Per board on days 61-120: 0.88 → 1.08 무모 offers (+23%; up in 13 of 14 sets, down in 1001). Days 1-60 identical; days 121-365
  slightly fewer; per game 228 → 229 (unchanged).
- Share of new board contracts that are 무모 for the strongest company (6 games from seed 6001, creation-time probe
  `scratchpad/fix/mprobe.js`): by rank B 10.5 → 16.4%, A 7.8 → 17.5%, S 3.4 → 3.2%; by day 61-120 9.8 → 15.5%,
  121-240 5.3 → 3.9%, 241-365 2.3 → 1.4%.
- Reckless bot (verify's `vbot.js`, `STRAT=reckless`, seeds 201-212 × 365): final ranks S 3, A 0, B 1, D 1, E 1, F 4,
  bankrupt 1, dark 1 → S 1, A 2, B 4, D 1, F 2, bankrupt 2; 무모 offers seen per game 241 → 282; failures per game
  309 → 359; win rate on days 61-120 / 121-240 / 241-365 33.5 / 32.2 / 38.0 → 29.5 / 27.6 / 30.6%.
- Not fixed here, because every fix changes something the owner's decisions fix: tying the cap and province opening
  to an "unboosted" rank would make the displayed rank lie and changes the board (excluded); a smaller cap ahead
  changes the board too. A third option was tried in a scratch copy: extra experience in the window (×2 at the peak)
  so the guild keeps pace with its rank. It brought the day 61-120 무모 share back near the old value (15.5 → 11.0%)
  but raised day-365 gold on seeds 1-12 to 114k (+83%), so it breaks the gold bound.
- **Owner question**: is "무모 offers unchanged" met by "the same rules, the same number per game", or should the
  share per board on days 61-120 also stay at today's 0.88? If the latter, the cleanest lever is to raise the guild's
  strength with its rank (experience or recruits in the window) and pay back the gold elsewhere.

### What a player sees

- Mean card 명성 for a normal contract (first round, seeds 5001-5006, verify's probe): ~17 on days 50-59, 33 in the
  60s, 51-63 on days 70-109, 45 in the 110s, 23 in the 120s (before: 17-22 throughout). With 2.25 the peak is ~8%
  higher. The fall over days 110-121 is gradual (at most 0.09 of the factor a day) but adds up to about −60% while the
  stars on the board keep rising with rank.
- Gold per contract moves little (×1.25 at the peak). Story, captain-story, boss and final contracts show the same
  numbers as before.
- A failed contract inside the window costs the same 명성 as it would outside it.

### Roll mode and checks

- `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` = `ddfdfe7b437fbe9fcf25f166ba542fce`, also with `SIM_SHADOW=1`.
- `node tools/sim/battle.js 100`: miss 0, soft 0 in all four outcomes.
- `node tools/sim/shadow.js 6 200 --check` (roll, 2,150 battles) and `node tools/sim/shadow.js 6 365 --resolve battle
  --check` (3,128 battles): all 0.
- Unit probe (seed 5001, 160 days, `scratchpad/fix/unit.js`): 104 of 104 normal contracts made in the window carry
  `repMul`, 0 of 13 no-deadline contracts do; 219 of 219 wins paid exactly the card 명성 (×1.5 on great); 9 of 9
  failures of boosted contracts lost exactly 30% / 60% of the unboosted 명성.
- `bot.js` also records gold on day 90 (`goldAt[90]`), in battle mode only, so roll JSON is byte-identical.

### Commands

```
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4                     # after (defaults)
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4 --set BM_MID_PAY=0 --set BM_MID_REP=0   # before
# also SIM_SEED=13, 501, 601, 701, 801, 901, 1001, 2001, 3001, 4001, 6001, 7001, 8001 (about 1 min per 12 games on 4 cores)
```

## Stage 4: time limit and late board

Date 2026-11-27. Two problems from the play tests, battle mode only. This section was revised after an adversarial review of the
first draft (see "Review of the first draft" at the end): the first time term over-corrected and has been replaced.

Roll mode is unchanged: `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` = `21b6184246abf071a0f40918718244b6` with and without
`SIM_SHADOW=1` (the roll baseline moved from `db19b56e…` to `21b61842…` with C13 in `ab0dec5`, before this revision; the stage-4
code does not touch it). Not touched: the battle engine and its 90 s limit, `BANDS`, `CAL_KIND`, every `BM_CAL_*`, `BOARD_W`
(무모 weight, decision 6), `BM_MID_*` (decision 5).

### A. Time limit: the forecast did not know the clock

**Cause.** `margin()` asks "how many times stronger must the enemy be for an even fight" from dps × effective hp; it has no time
in it. A field battle (everything but escort / defense / warDefense / envoy) is lost when the clock runs out with the enemy
standing, and a small party against 2-3 enemy groups (siege, raid, rescue, sabotage …) can win every exchange and still not finish
(Q5 #224, Q6 #721: 0 of ours down, 51-62% of the enemy destroyed).

**What the data says** (`Stats.killTime`: total enemy hp / (our whole side's dps against their defence − 0.6 × their healing), both
sides at full strength; R-factor = how much the stage-3 R must be scaled for a logit fit with slope 13 to match the wins, stars
with R 0.75-1.6):

| killTime | probe R-factor | bot R-factor | probe timeouts | bot timeouts |
|---|---|---|---|---|
| 9-12 s | 1.024 | 1.030 | 0% | 0% |
| 12-15 s | 1.028 | 1.040 | 0.1% | 0% |
| 15-20 s | 0.991 | 1.017 | 0.4% | 0.2% |
| 20-25 s | 0.954 | 0.990 | 0.9% | 0.3% |
| 25-30 s | 0.933 | 0.998 | 2.1% | 2.2% |
| 30-40 s | 0.925 | 0.953 | 3.9% | 1.2% |
| 40-60 s | 0.904 | (n 38) | 13% | 5% |
| > 60 s | 0.827 | - | 54% | - |

Probe = small-party probe (below), seeds 8101-8112 + 8301-8312; bot = sensible bot's sent + looked-at battles, seeds 8501-8512.
Two things are going on: (1) the stage-3 calibration was fitted on all field battles together, so fights that end fast read a
little low and slow fights read high, and most of the slow-fight losses at 20-40 s are lost exchanges, not timeouts (old 백중 at
20-30 s: 30% won, 2% timeouts); (2) real timeouts only take over past ~45 s.

**First draft and why it was replaced.** The first draft multiplied R by `(0.22·LIMIT / killTime)^1.5` above 20 s. Tuned on
우세/압도 timeouts, it pushed slow fights more than a word down: in the review's probe (which also samples stars that now read
무모), slow field fights (killTime > 20 s) won 무모 17% / 열세 46% / 백중 70%; the bot's 백중 went 45 → 53% because the
fast part's under-reading was left alone.

**Change** (`js/stats.js`, `forecast()`, battle-mode specs, rule ≠ `hold`; `Stats.killTime` and the `sideUnitsOf` factoring
are kept from the first draft):
1. Speed factor, both ways: `R1 = R × (MID·LIMIT / max(killTime, EDGE·LIMIT))^BIAS` — 1 at 18 s, ×1.035 at 12 s or less,
   ×0.96 at 30 s, ×0.93 at 45 s. Centred on the bot's typical fight, so the pooled stage-3 calibration does not move.
2. Timeout, in probability: `p0 = R1^b / (1 + R1^b)` (b = `BM_TIME_SLOPE`), `S = 1 / (1 + ((killTime − EDGE·LIMIT)/(TAU·LIMIT))^K)`,
   `p = p0·S`, `R = (p / (1 − p))^(1/b)` (never above R1). An easy fight (압도) loses most when the clock is short; a fight that
   is already hard loses little — so a slow fight cannot read 압도, and a slow 백중 does not fall to 무모. `S` = 0.93 at 30 s,
   0.80 at 45 s, 0.51 at 80 s.
3. The board's capability table uses the same forecast, so card, dispatch and board aim read the same word. `BM_TIME_K=0`
   switches 1 and 2 off (stage-3 forecast).

| Constant | Value | Reason |
|---|---|---|
| `BM_TIME_EDGE` | 0.13 (≈ 12 s) | Lower clamp of the speed factor and start of the timeout term. Below it the bins are flat. |
| `BM_TIME_MID` | 0.2 (18 s) | Speed factor 1 here. ML fit 0.202. |
| `BM_TIME_BIAS` | 0.08 (0 = speed factor off) | ML fit 0.067 (probe and bot weighted equally); 0.08-0.10 read the same in every slice. |
| `BM_TIME_TAU` | 0.77 (≈ 69 s past EDGE) | ML fit. |
| `BM_TIME_K` | 1.9 (0 = whole time term off) | ML fit. |
| `BM_TIME_SLOPE` | 13 | Slope of logit(win) on ln R; fits on the same data gave 12.7-14 (hold battles 14.7). |
| `BM_TIME_HEAL` | 0.6 | Enemy healing in `killTime`, the same 0.6 as in `margin`'s `rho`. |

Fit: maximum likelihood of `σ(13·ln R1)·S` on probe seeds 8101-8112 (20,152 field battles) and bot seeds 8501-8512 (9,212 field
battles, both populations weighted equally). One-sided forms were also fitted (pure probability term; probability term with
a one-sided bias 0.12; `TAU` scaled by R^c): each matched the probe but read the bot's fights 6-12 points safe at 백중, or the
reverse. The two-sided form was the only one that kept both.

**Small-party probe** (scratch `fix/probe3.js`): every 20th day of a bot game, for each company and each subset (top 1-4 members
by level and a random 1 and 2), three synthetic ordinary contracts of random type; for each, one star drawn with the old word
stratified 무모-압도 (old R ≥ 0.5) and one star drawn from the slow field stars (killTime > 15 s). Both forecasts are recorded on
the same battle. Unlike the first draft's probe, stars that read 무모 are sampled.

**Out of sample, in the game** (new code, probe seeds 8401-8412, never used; 26,440 battles; "old" = the stage-3 forecast of
the same battle). Win rate by word 무모 / 열세 / 백중 / 우세 / 압도, and timeout losses among ≥우세:

| Slice | old | new | timeout ≥우세 old → new |
|---|---|---|---|
| all (incl. hold) | 0 / 14 / 46 / 88 / 99% | 1 / 15 / 47 / 88 / 100% | 1.2 → 0.7% |
| field, killTime ≤ 12 s | 11 / 15 / 53 / 94 / 100% | 0 / 11 / 42 / 90 / 100% | 0.1 → 0.1% |
| field, killTime > 20 s | 0 / 12 / 34 / 75 / 88% | 1 / 16 / 43 / 85 / – | 10.5 → 6.9% |
| field, 1 member | 0 / 20 / 52 / 88 / 98% | 1 / 21 / 52 / 89 / 100% | 2.8 → 1.8% |
| field, 2 members | 0 / 11 / 43 / 84 / 99% | 0 / 12 / 43 / 86 / 99% | 1.8 → 1.1% |
| field, 3 members | 0 / 13 / 48 / 91 / 100% | 0 / 14 / 49 / 90 / 100% | 0.6 → 0.4% |
| field, 4 members | 1 / 14 / 37 / 84 / 100% | 1 / 15 / 36 / 82 / 100% | 0.1 → 0.1% |
| slow (> 20 s), 1 member | 0 / 15 / 41 / 74 / 82% | 1 / 19 / 48 / 83 / – | 15.4 → 9.9% |
| slow, 2 members | 0 / 8 / 28 / 73 / 90% | 0 / 12 / 39 / 85 / – | 8.7 → 5.6% |
| slow, 3+ members | 0 / 12 / 31 / 81 / 100% | 0 / 15 / 40 / 88 / – | 4.3 → 3.6% |
| siege (all) / siege with 1-2 members | 0 / 16 / 44 / 85 / 99% · 0 / 15 / 48 / 85 / 99% | 0 / 16 / 44 / 85 / 99% · 0 / 14 / 45 / 87 / 99% | 1.3 → 0.9% · 1.4 → 0.9% |
| raid / rescue / sabotage / counterspy (백중 · 우세) | 47·86 / 42·88 / 44·83 / 43·86% | 47·87 / 42·87 / 41·83 / 40·87% | 1.5→0.7 / 1.9→1.1 / 1.8→1.4 / 2.8→1.6% |
| hunt / explore / magic (백중 · 우세) | 47 · 88% | 50 · 88% | 1.4 → 0.9% |
| hold types | unchanged | unchanged | 0 |
| Q6 class (old R 1.20-1.35, killTime > 20 s) | 우세 88% (166) | 우세 90% (163) | 9.0 → 7.4% |

The probe's 4-member subsets (top four by level) read 백중 36-37% before and after: that is a stage-3 calibration matter of these
synthetic parties (the bot's 4+ parties read 45%), not time.

**Out of sample, bot battles** (new code, seeds 8601-8612, never used, 12,765 sent + looked-at battles):

| Slice | old | new | timeout ≥우세 |
|---|---|---|---|
| all | 1 / 16 / 48 / 89 / 100% | 1 / 16 / 46 / 87 / 100% | 0.19 → 0.14% |
| field, killTime ≤ 12 s | 33 / 33 / 65 / 91 / 99% | 0 / 29 / 56 / 87 / 99% | 0.11 → 0.10% |
| field, killTime > 20 s | 0 / 10 / 39 / 83 / 100% (33) | 0 / 15 / 45 / 87 / – | 2.0 → 1.4% |
| field 3 / 4+ members (백중 · 우세) | 45·86 / 49·89% | 44·87 / 45·87% | 0.70→0.55 / 0.16→0.11% |
| siege / rescue / sabotage / raid (백중 · 우세) | 59·79 / 41·87 / 51·86 / 52·86% | 55·81 / 33·83 / 46·83 / 49·85% | 1.4→1.3 / 0.5→0.4 / 0.4→0.0 / 0.8→0.8% |

The review's own probe file (seeds 8001-8008, which over-samples stars whose word the first draft changed), re-worded offline,
field killTime > 20 s: old – / 7 / 31 / 64 / 86%, first draft 17 / 46 / 70 / 91 / 96%, now 4 / 12 / 39 / 77 / –; timeout ≥우세
11% / 5% / 9%. The words are no longer on the safe side there; they still lean a little optimistic in that sample.

**Sensible bot, 6 sets × 12 games × 365 days** (sets 1, 13, 5001, 6001, 7101, 9201; none used for this fit. Before =
`--set BM_TIME_K=0 --set 'BM_LATE_OPEN=[150,0]'`, i.e. stage 3):

| | before | after |
|---|---|---|
| Win 백중 / 우세 / 압도 (pooled) | 45.4 / 87.1 / 99.7% | 46.1 / 86.4 / 99.6% |
| 우세 by members 1 / 2 / 3 / 4+ | 84 (55) / 90 (307) / 88 / 87% | 97 (60) / 91 (237) / 89 / 86% |
| 백중 by members 2 / 3 / 4+ (1 member: n 6-7) | 41 (85) / 47 / 45% | 37 (68) / 52 / 45% |
| Lost on time, all sent, by members 1 / 2 / 3 / 4+ | 0.0 / 0.3 / 0.4 / 0.2% | 0.0 / 0.0 / 0.3 / 0.1% |
| Lost on time at ≥우세, members 2 / 3 / 4+ | 0.4 / 0.3 / 0.2% | 0.0 / 0.2 / 0.1% |
| Lost on time by type: siege / sabotage / rescue / raid / campaign | 0.7 / 0.9 / 0.8 / 0.6 / 0.9% | 0.6 / 0.6 / 0.7 / 0.2 / 0.5% |

**Single-member bot** (review's `sbot.js`, STRAT=single, seeds 201-212): 1-member 백중 62.1% (311) → 65.0% (306), 우세 90.6 →
91.7%, 압도 99.9 → 99.8%; lost on time 0.3 → 0.1%. The 62% before is stage 3's; the time term adds about 3 points (the first
draft added 7). In the probe, where single members are drawn at random, 1-member 백중 reads 51% (seeds 8101-8401 pooled), so the
lean belongs to the bot's choice of who goes alone, not to time (see open issues).

### B. Late board: the high stars waited for a calamity

**Cause.** `battleCap()` was `lateGame() ? 14 : rank + BM_CAP_AHEAD`, clamped to `maxContractLevel()` (10 unless a calamity has
risen). At rank S that is ★10. In a game where no calamity rises the best company outgrows ★10 by day ~200 and every ordinary
offer reads 압도 for it (Q8: 13 of 14 boards after day 240).

**Change** (`js/muster.js`, unchanged from the first draft): `Game.bmMaxLevel()` = 14 after a calamity (as before); otherwise, at
rank S, ★11 opens on day `BM_LATE_OPEN[0]` and one more star every `BM_LATE_OPEN[1]` days up to ★14; else `maxContractLevel()`
(10). `battleCap()` and the clamp in `battleLevel` use it. Ordinary battle-mode contracts only: special contracts, roll mode and
`lateGame()` itself (market, recovery pay) are unchanged. The enemies still come from the star (decision 1).

| Constant | Value | Reason |
|---|---|---|
| `BM_LATE_OPEN` | [150, 30] (★11 day 150, ★12 180, ★13 210, ★14 240; interval 0 = off) | S comes on day ~100; the no-calamity board narrows after ~180 and was all-easy from ~240. |
| `BM_TOP_STEP` | 3.5 (= `BM_LATE_STEP`: the stage-3 table, no change) | Enemy levels per star for ★11-14. A lever, not used: see below. |

Late board, ordinary offers for the best own company, every 3rd day — share of boards with a ≤열세 offer / with both ≤열세 and
≥우세 / with a ≤백중 offer, and the top star:

| Case | before | after |
|---|---|---|
| 6 normal sets, days 241-365, no calamity (558 boards each) | 5 / 4 / 8%, ★9.8 | 53 / 43 / 74%, ★13.5 |
| 6 normal sets, days 241-365, after a calamity | 54 / 43 / 78%, ★13.6 | 47 / 37 / 74%, ★13.7 |
| 6 normal sets, days 121-240, no calamity | 48 / 40 / 63%, ★9.7 | 66 / 54 / 83%, ★10.7 |
| 6 normal sets, days 121-240, after a calamity | 79 / 63 / 93% | 76 / 60 / 92% |
| Calamity suppressed, seeds 1-12, days 241-365 | 22 / 18 / 35%, ★9.8 | 66 / 51 / 83%, ★13.4 |
| Calamity suppressed, seeds 9001-9012, days 241-365 | 32 / 26 / 48%, ★9.7 | 63 / 48 / 83%, ★13.4 |
| Calamity suppressed, seeds 1 / 9001, days 121-240 | 55 / 44 / 70% · 55 / 47 / 71% | 74 / 59 / 85% · 74 / 59 / 92% |

No-calamity late boards now match calamity games'. The small drop in calamity games (54 → 47%) comes from A, which lifts fast
fights' R by up to 3.5%, so a given star reads a little easier. With the calamity suppressed, late 무모 offers per board rise from
0.10-0.18 to 0.42-0.43 (`BOARD_W` untouched: before, a 무모 slot found no 무모 star under ★10).

`BM_TOP_STEP` = 5 (steeper ★11-14) was tried with the calamity suppressed (seeds 1-12, days 241-365, with an interim version of A): ≤열세 56 → 69%, ≤백중
74 → 86%, but day-365 gold 15.9k → 5.5k (same pay per star for harder enemies). Not adopted; it is the knob if the owner wants
the late board wider without new content.

### Economy and safety (sensible bot, 12 × 365 per set, `SIM_RESOLVE=battle`)

| Set | 1 | 13 | 5001 | 6001 | 7101 | 9201 | mean |
|---|---|---|---|---|---|---|---|
| Day reaching S | 105 → 96 | 105 → 95 | 98 → 101 | 95 → 98 | 100 → 101 | 108 → 101 | 101.8 → 98.7 |
| Gold day 120 | 6.9k → 6.7k | 5.3k → 12.5k | 7.2k → 4.4k | 7.7k → 5.6k | 3.6k → 4.4k | 3.0k → 6.7k | 5.6k → 6.7k |
| Gold day 365 | 82.5k → 59.4k | 50.1k → 72.2k | 83.4k → 73.8k | 86.1k → 44.4k | 92.3k → 96.3k | 34.0k → 107.5k | 71.4k → 75.6k |
| Completed / failed | 432/73 → 407/76 | 420/81 → 437/77 | 471/79 → 415/82 | 478/74 → 422/78 | 427/74 → 408/85 | 402/77 → 416/78 | 438/76 → 418/79 |

- Day-365 gold +6% on the mean, 3 sets up and 3 down; per-set swings of −48% to +216% are noise (stage 3 saw ±15-45% per set,
  and 9201 alone goes 34k → 107k). A only (`--set 'BM_LATE_OPEN=[150,0]'`) on 5001 / 7101 / 9201: 67.2k / 103.9k / 85.9k. No sign
  of an explosion; Q8's human play (290-400k) remains far above any bot set.
- Final rank S 12 of 12 in every set; game overs 0; deaths 0 special / 0 other; captains 6.37 → 6.35. Boss wins 57-81% → 70-72%,
  final battle 90-100% → 82-100% (n 9-12 per set).
- **No-calamity games are poorer in gold, richer in guild.** Calamity suppressed, seeds 1-12 / 9001-9012: day-365 gold 20.0k →
  7.1k / 30.1k → 6.9k, S on day 107 → 96 / 122 → 103, captains 5.2 → 6.3 / 5.3 → 5.8, top-3 company power 5,191 → 5,931 /
  4,629 → 5,832, failures 56 → 76 / 61 → 77, no bankruptcy (lowest gold per run averages 16 after, 91 before). A causes it (A
  only: 9.1k; B only: 25.1k): the bot reaches S sooner and spends on a larger guild. Q8 already found these games poor (no war pay,
  no recovery ×1.8).
- Odd strategies (review's `sbot.js`, seeds 201-212): single members — ranks S 10 / A 2 → S 9 / A 2 plus one darkness game over
  (the first draft showed the same one; the calamity is defeated in 7 of 12 games in both); reckless (takes every offer) — final
  ranks get worse (F 2 → 5) and the final battle is attempted 2.4 → 4.8 times per game at R 0.85 (win 41 → 11%); 무모 wins
  0.4 → 0.6%. The reckless bot ignores the words; it only feels A through the board, which now places a word's stars a little
  higher for fast fights.

### Checks

- Roll md5 `21b6184246abf071a0f40918718244b6` with and without `SIM_SHADOW=1`.
- `node tools/sim/battle.js 100`: miss 0 / soft 0.
- `node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4` (2,764 battles, 8,004 alternative parties) and the roll-mode
  run (3,944 battles): every invariant 0.
- `--set` takes the new knobs in `bot.js` and `shadow.js` and refuses unknown names (e.g. the first draft's `BM_TIME_EXP`), wrong
  types and wrong array lengths.
- The in-game forecast matches the offline formula used for the fit (median difference 0.0002 in R on 26,440 probe rows).

### Commands

```
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4                                                # after
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4 --set BM_TIME_K=0 --set 'BM_LATE_OPEN=[150,0]'   # before (stage 3)
#   also SIM_SEED=13, 5001, 6001, 7101, 9201; A only: --set 'BM_LATE_OPEN=[150,0]'; B only: --set BM_TIME_K=0
node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4                                                    # all 0
# scratch (not in the repo): fix/probe3.js (small-party probe incl. 무모 stars), fix/collect2.js (bot sent + looked-at rows with
#   the old R and killTime), tools/nocal.js (calamity suppressed), fix/fit2-5.js (ML fits), fix/ev.js, evn.js, bins.js (re-wording)
```

### Review of the first draft (findings and what was done)

1. **The time term over-corrected in its own slice** (slow field fights: 무모 17%, 열세 46%, 백중 70%). Fixed: the term was
   replaced by the two-part form above, refitted on a probe that samples 무모 stars and on bot battles. Slow fights in the new
   probe: 열세 16%, 백중 43%, 우세 85%, no 압도.
2. **One-member parties read on the safe side.** Mostly fixed: the single-member bot reads 백중 62.1% before and 65.0% after (the
   first draft: 68.7%); in the probe 1 member reads 52% before and after. The remaining lean is stage 3's and shows only in the
   bot's own single-member choices (open issue).
3. **"+42% gold comes from A" did not reproduce.** Agreed; the claim is withdrawn. With the new term the 6-set mean is +6% and the
   per-set direction is mixed.
4. **B is partial.** Days 241-365 without a calamity: 5% → 53% of boards with a ≤열세 offer, now as wide as calamity games
   (47%). What is left is the ★14 ceiling, shared with calamity games (`BM_TOP_STEP` measured above, not adopted).
5. **≥우세 timeouts remain in the slow slice.** Accepted: in the slow slice 우세 now wins 85% with the timeouts counted as losses.
   A word without any timeout there would have to read 우세 at 90%+, which is the safe-side error of finding 1.
6. **Reckless bot.** Informational; re-measured above.
7. **HEAD moved during the review.** The roll baseline is now `21b61842…` (C13); re-checked here.

### Open issues

- **Engine stand-offs**: a few timeouts happen at a short `killTime` (≈ 0.03% of probe battles): every unit of both sides stops
  moving from t ≈ 10 s, 30 px apart, and nothing hits until 90 s (probe seed 202, day 270, rescue ★1, 철벽 수호자 alone with two
  trainee clerics). An AI / slot bug in `js/battle.js`; no forecast can see it.
- **Single-member 백중 reads safe for the single-member bot** (62% at stage 3, 65% now) but not in the probe (51%). A
  `BM_CAL_HEADS[1]` change would trade one for the other; left as it is (calibration constraint).
- **Slow small-party fights still lean a little optimistic** in the probe (2 members, > 20 s: 백중 39%), while the bot's slow fights
  read honestly (45%). The probe's synthetic subsets fight slow battles worse than the bot's own parties; the fit splits the
  difference.
- **★14 ceiling**: the strongest guilds outgrow ★14 late, with or without a calamity (47-53% of late boards have a ≤열세 offer).
  `BM_TOP_STEP` or content above ★14 (`LATE_MAX_LEVEL`) would widen it; both are owner calls (gold, see above).
- **No-calamity economy**: day-365 gold 20-30k → 7k in calamity-suppressed games (larger guild instead). Worth a look if the owner
  wants those games to feel richer.
- **No UI reason for a lower word**: a slow fight now reads lower, but the card does not say why (e.g. "시간이 빠듯함").
- **Q6 #721 not replayed**: the seed 582702 day-150 save is not in the repo; the probe's Q6 class (old R 1.20-1.35, killTime
  > 20 s) is measured instead.

## One-company polish (owner decision 7)

Date 2026-11-27. Base `ea5304a` (roll md5 `11cadc0cceafa5e4262773fdadf780f9`). Owner decision 7: before battle mode becomes the
default, fix the one-company early game that Q16 played (seed 582702, 바렌, one direct company, 120 days): 우세 lost 4 of 17 early,
백중 won 3 of 15, 37 of 61 days in days 60-120 were spent waiting for the only company, the grace week was only in the journal, and
the partial pay on a loss was explained inconsistently. Plus QA Q18 item 2 (a boss contract issued by the active calamity).

Battle-mode gameplay only, except the boss-contract issuer (a real bug in both modes). Not touched: `js/battle.js`, the board code,
`BANDS`, `CAL_KIND`, `BM_CAL_ARCH`, `BM_CAL_SPECIAL`, `BOARD_W`, `BM_MID_*`, the time term, casualty rules.

### What the measurement said (before the change)

A scratch one-company bot (`one.js`, "human" strategy: first direct company only, barracks first, one facility a week, picks by
(reward + 6·명성) × word weight ÷ days with 압도 1 / 우세 .85 / 백중 .7, 열세 only when rich, never 무모; `--probe` also fights every
board offer headless with the day's party) took the same word mix as Q16 (압도 40 / 우세 30 / 백중 26 / 열세 3%).

- **Q16's 우세 losses were mostly bad luck**: 바렌 with one company won 89-91% at 우세 on days 1-30 (13 or fewer wins in 17 has an
  8-14% chance at that rate). Nothing is missing for early or small rosters as such; one-company forecasts were on average
  *pessimistic* (probe 백중 61-68%, 우세 94-96%).
- **The missing term was the captain's fighting style.** Same word, one company, by first captain (probe, 3-4 members): 백중 won
  39% (fixer), 48% (lancer), 51% (blademaster = 바렌) … 78% (fieldmedic), 87% (tactician). `margin` counts only skills that hit an enemy
  and heals: a melee captain walks into the front and is downed first (with 3-4 members one downed captain is half the retreat
  rule), and rally buffs (전술 지시 공격 +25% / 방어 +20%, 철벽 방진 방어 +40%, 노병의 호통 ±20%) are invisible. The many-company bot shows
  the same split (melee captains 백중 33-34% / 우세 79-82%, ranged 68-71% / 95-96%). Stage 3 fitted the mix, so each starter carried a
  fixed ±10-20% error in R from day 1.
- **2-member parties** (a member injured or exhausted) read optimistic: 백중 39-42%.
- **Waiting is structural**: a company redispatched the day it returns waits 1 − 1/length of the time; mission length grows from
  1.5 days (days 1-30) to 2.5-2.7 (days 61+) because ★6+ adds a day. Q16's 37 of 61 matches the bots exactly.

### A. Forecast: captain style, 2 members, our-level steps (`js/stats.js`)

`forecast()` (battle-mode specs only) multiplies the calibration by `leadCal(spec)`: for each own company group its captain's
factor — `ranged` if the captain's first skill has range ≥ `RANGE_MIN` (bows, magic, heals), else `melee` (the lancer's 16-range
spear is melee) — times `rally` if any captain skill is a self-side buff (`tgt 'self'` + `buff`); groups without a captain and
external companies count 1; groups are averaged by their non-recruit members. `Stats.leadStyle(sk)` / `Stats.leadCal(spec)` are
exported. The board's capability table uses the same forecast, so card, dispatch and board aim keep reading the same word.

| Constant | Before | After | Reason |
|---|---|---|---|
| `BM_CAL_LEAD` (new) | – | melee 0.98, ranged 1.082, rally 1.035, `RANGE_MIN` 40 | Fit below. All 1 = off. `--set BM_CAL_LEAD.ranged=1` etc. |
| `BM_CAL_HEADS[2]` | 0.984 | 0.94 | 2-member parties, refitted together with the style term. |
| `BM_CAL_HEADS[1]` | 0.95 | 0.9 | Review fix: a lone fighter read 백중 33% / 우세 76% (one-company probe, about 1,300 offers). |
| `BM_CAL_OWNLV` | ≤3 0.879, ≤6 0.928, ≤9 0.946, ≤12 1, ≤16 1.005, more 1.034 | 0.887, 0.944, **0.958**, 0.99, 0.983, 0.977 | Refitted jointly: part of the old high-level step (1.034) was the ranged captains that late parties have more of. ≤9 was 0.969 in the first draft; the review moved it (below). |

**Fit.** Stage 3's target matching (per slice the factor closest to 우세 87% and 백중 50%, weakly 열세 17% / 압도 99%, shrunk by
n / (n + 150), alternating dimensions five times), parametrised as melee, ranged, rally, the 2-member factor and the six level
steps, offline re-banding of R. Two populations with equal weight, both *every offer looked at*, fought headless (not only sent):
the many-company sensible bot (seeds 201-212, 301-312, 401-412 × 365 days, 24,383 battles) and the one-company probe (9 first
captains, seeds 1001 / 2001 × 120 days plus the human bot on seeds 201-212, 35,109 battles). None of the evaluation seeds below.

**First draft and why it was replaced.** A first fit that used the bot's *sent* battles (it never sends 열세, so re-banding a ranged
captain's 열세 up into 백중 had no rows to move) gave ranged 1.119 / rally 1.044. In the game the sensible bot's pooled 백중 fell
46.8 → 41.1% and 우세 87.4 → 86.3% (3 sets). Refitted on looked-at offers it is the table above.

Offline, in sample: many-company probe 백중 / 우세 50 / 90% → 49 / 90% (days 241-365 44 / 87 → 48 / 90; melee captains 33 / 82 →
46 / 88; ranged 68 / 96 → 53 / 92); one-company probe 61 / 94 → 50 / 91% (days 1-30 59 / 94 → 48 / 91).

### B. Waiting days: a skip button and the second-company hint (UI only)

The data does not support shortening missions or moving the second company earlier:
- **Shorter missions** (dropping the ★6+ extra day in battle mode) would cut days 61-120 waiting from about 61% to 48%, but raise
  명성 per day by about 30% for every guild (a decision-5 retune) and cut rewards 7-10% through the (1 + 0.12·days) factor.
- **A second company is already reachable early**: barracks 1 allows two direct companies (`maxCompanies` = 1 + barracks) and one
  costs `companyCost()` = 200. A "human2" bot that opens it when the new hint would (only one company, room for another, gold for it
  plus 4 weeks of pay + 600) opened it on day 10-35 (median 16) — and that removes about half the waiting (table below). What Q16 lacked
  was the reason to do it.

So:
- **「귀환까지 ▶▶」** (top bar, `index.html` `#skip-day`, `js/ui.js`): shown only when no company can be sent (`Game.waitingForReturn()`:
  missions out, no own company with an idle member, no free external company). A company at home with nobody fit to go (all injured,
  or a new empty company) counts as unable; the contract-tab hint then says so instead of 「모든 용병단이 의뢰에 나가 있습니다」
  (`Game.allAway()` tells the two apart), and the skip stops when a member recovers. `Game.skipToReturn()` (`js/game.js`) runs `nextDay`
  until a report or notice is queued (a return included), payday, a new special contract, a company becomes free, or the game ends;
  at most 30 days. Same rules and random numbers as pressing 「다음 날」 that many times; no bot calls it, so both modes' md5 hold.
  Shown in both modes (it changes no rule).
- **Hint lines**: on the contract tab while waiting (`waitHint()` in `js/ui-tabs.js`: the skip button, and with one company either
  "build another company here (금화 N)" or "upgrade the barracks to have another"), and on the company tab when there is one company
  and room for another.

### C. Grace week, visible (battle mode)

- **Report note when a defeat opens the grace week** (`js/contract.js`) and gold after the loss pay is below the next payday
  (`Game.paydayTotal()` = wages + upkeep + deferred pay): 「유예 주간(N일까지): 급료가 모자라도 단원이 떠나지 않습니다. 못 준 급료는
  다음 정산에 함께 냅니다.」
- **Popup when a payday defers wages** (`js/game.js` `weeklyPayday`): a new report `{ special: 'grace', until, owed, names }` drawn by
  `specialReportBody` in `js/ui.js` (「유예 주간: 급료를 미뤘습니다」, who, how much, until when, what happens at the next payday).
  The journal line stays. The bots ignore it (no `quest`).
- **Top-bar chip** 「유예 ~N일」 (`#grace-chip`, title explains) while the *next payday* falls inside the grace week and it matters
  (deferred pay, or gold below the next payday: `Game.graceShown()`; `Game.nextPaydayDay()` = day + `daysToPayday()`). Grace only acts
  on paydays, so after the last in-grace payday the chip no longer claims protection: if deferred pay is still owed it turns into
  「미룬 급료 N」 (`Game.backPayShown()`, title: paid with the next payday on day D, members who are not paid then leave). Both are hidden
  while a mission report is still unseen, so they do not give a defeat away during the battle replay.
- **Two paydays in one grace week.** A defeat resolved on a payday (day % 7 = 1) defers that payday and, because the week runs to
  day + 7 inclusive, the next one too. The popup carries `next` (the next payday) and `nextGrace` (whether it is still inside the
  grace week) and says so: 「그 정산도 유예 주간 안이라 그때 모자라도 다시 미룹니다. 그다음 정산부터는 못 받는 단원이 떠납니다.」 instead of
  「그때도 못 받는 단원은 떠납니다.」 (which was false there). Two popups in that window are correct (two paydays deferred); the rule is
  unchanged. Popups saved before this change lack the fields and keep the old sentence.

### D. Loss pay, always explained (battle mode)

Every battle-mode loss now writes the split (before: only when ≥ 5% of the enemy was beaten, and the whole sum was labelled
「적 전력의 N%를 꺾어」):
- fail or orderly retreat: 「패배 보수 금화 X = 기본 10% (a) + 꺾은 적 전력 N%의 몫 (b)」 (a = reward × `LOSS_PAY`, b = X − a);
- disaster without a retreat: 「패배 보수 금화 X: 전멸이라 기본 몫은 없고 꺾은 적 전력 N%의 몫만 받았습니다.」

### E. Boss contract issuer (QA Q18 item 2, both modes)

`checkBosses()` now passes `issuer`: the province owner, or `'locals'` if the owner is the active calamity or destroyed (the rule of
`js/captains.js:148` and `js/contract.js:734`). Missions already out are not touched. `makeContract` draws the same random numbers
either way (level, enemy and title are given). 12 × 365, HEAD: one calamity-issued boss contract per mode (sent in roll); after: 0.
Roll md5: 6 × 200 `11cadc0c…` and 12 × 365 `ffee253e5364a3e6f882f9aed77254b0` are both unchanged (the one roll game that sent such a
contract ends with the same summary JSON).

This is more than a label. `effectiveReq` treats a province whose owner is not the issuer as hostile (calamity standing −100), so
such a boss contract now has req × 1.2 (roll mode, seed 9, day 80, frost province held by the demons: effective req 572 → 686), and in
battle mode the support group is villagers instead of the calamity's own soldiers. The reward does not change (`doctrine.pay` is 1
either way). This is the same rule every other contract in a calamity-held province already follows (`js/captains.js:148`,
`js/contract.js:734`), so it is intended: a calamity does not post bounties on itself, and fighting in its land is harder.

### Results (evaluation seeds 1, 3101, 4101 — 3101 and 4101 untouched by any fit; 5001 for the starters)

These are the **first draft** ("v1": ≤9 step 0.969, 1 member 0.95). The QA re-check changed both; the numbers after that, on six
many-company and five one-company seed sets, are in "Review fixes" below. The many-company gold and S-day columns here are inside
seed-set noise (see there) and are not findings.

**One-company human bot, 3 × 12 games × 365 days, before → after** (sent battles; probe = every board offer, days 1-120):

| | 백중 | 우세 | 압도 |
|---|---|---|---|
| sent, days 1-30 | 75% (109) → 61% (116) | 92% (212) → 90% (221) | 100% → 100% |
| sent, days 31-60 | 76% (101) → 59% (85) | 97% (174) → 96% (185) | 100% → 100% |
| sent, days 61-120 | 58% (158) → 50% (137) | 88% (257) → 89% (283) | 100% → 100% |
| sent, days 121-365 | 46% (645) → 54% (684) | 90% (1180) → 92% (1169) | 100% → 100% |
| probe, days 1-30 / 31-60 / 61-120 | 67 / 76 / 63% → 58 / 61 / 56% | 95 / 96 / 92% → 93 / 95 / 91% | 100% |
| sent, 2 members | 32% (129) → 59% (149) | 84% (206) → 94% (228) | 100% |
| sent, blademaster (바렌) | 32% (315) → 49% (332) | 84% (540) → 88% (570) | 100% |
| sent, ironwall | 52% (271) → 58% (266) | 91% (504) → 94% (487) | 100% |
| sent, tactician | 71% (427) → 55% (424) | 96% (779) → 93% (801) | 100% |

Rank days C / B / A / S: 42 / 74 / 106 / 165 (35 of 36 reach S) → 43 / 74 / 103 / 175 (36 of 36); rank on day 120: A 30 → 32 of 36;
losses 16.7 → 16.8% of missions; no bankruptcy; gold on day 30 / 60 / 120: 2.8k / 6.1k / 10.8k → 3.0k / 6.0k / 11.2k.

**By first captain** (one company, probe, 3-4 members, seed 5001 × 8 games × 120 days, never used):

| starter | 백중 | 우세 | 열세 |
|---|---|---|---|
| fixer | 44% → 43% | 88% → 87% | 10% → 15% |
| lancer | 54% → 47% | 92% → 93% | 23% → 18% |
| blademaster (바렌) | 51% → 56% | 91% → 92% | 14% → 18% |
| hedgemage | 73% → 33% | 96% → 89% | 24% → 11% |
| veteran | 53% → 56% | 92% → 94% | 32% → 23% |
| ironwall | 61% → 54% | 97% → 97% | 29% → 19% |
| huntress | 64% → 44% | 97% → 88% | 33% → 11% |
| fieldmedic | 81% → 61% | 98% → 95% | 48% → 16% |
| tactician | 87% → 53% | 100% → 96% | 62% → 22% |
| all (n ≈ 1,250 / 2,540 / 1,000) | 64% → 50% | 95% → 92% | 31% → 17% |

The spread of 백중 across starters goes from 44-87% to 33-61% (hedgemage and huntress now read a little optimistic, n 116-131).

**Waiting** (per game; "clicks" = clicks needed to get through the waiting days with 「귀환까지 ▶▶」, which stops at returns and paydays):

| days | human: waiting | sent | clicks with the button | human2 (opens a 2nd company): waiting | sent |
|---|---|---|---|---|---|
| 1-30 | 9.4 | 20.0 | 8.2 | 6.4 | 21.8 |
| 31-60 | 14.2 | 13.1 | 9.5 | 6.3 | 20.8 |
| 61-120 | 32.8 | 20.1 | 18.9 | 18.0 | 35.0 |
| 121-365 | 135 | 79 | 79 | 73 | 133 |

Most waiting runs are 1-2 days, so the button saves about 40% of the waiting clicks (61-120: 33 → 19). Opening the second company
halves the waiting and brings S from day 175 to 114 (human2: C 37, B 61, A 84; S by day 120 in 27 of 36 games); losses rise from 11
to 21% on days 31-60 (the second company starts without a captain). That is why the hint points there.

**Sensible bot (many companies), 3 × 12 × 365, before → after:**

| | 1 | 3101 | 4101 | pooled |
|---|---|---|---|---|
| win 백중 | 43.8 → 47.7% | 48.8 → 48.2% | 47.8 → 49.5% | 46.8 → 48.4% (n ≈ 3,000) |
| win 우세 | 86.1 → 89.4% | 87.6 → 89.0% | 88.3 → 87.6% | 87.4 → 88.7% (n ≈ 9,000) |
| win 압도 | 99.7 → 99.5% | 99.3 → 99.7% | 99.8 → 99.4% | 99.6 → 99.5% |
| win, all sent, days 1-30 / 61-120 / 241-365 | 94 / 87 / 79 → 92 / 84 / 85% | 93 / 86 / 84 → 90 / 81 / 86% | 93 / 90 / 82 → 88 / 84 / 85% | 93 / 88 / 82 → 90 / 83 / 86% |
| day reaching S | 92 → 98 | 100 → 100 | 86 → 97 | 92.7 → 98.3 |
| gold day 120 / 365 | 8.1k / 50.9k → 8.3k / 64.3k | 10.1k / 93.3k → 8.7k / 114.3k | 11.9k / 65.6k → 5.1k / 90.2k | 10.0k / 69.9k → 7.4k / 89.6k |
| boss / final won | 83 / 100% → 76 / 85% | 69 / 100% → 72 / 100% | 85 / 100% → 73 / 100% | 78 / 100% → 74 / 94% (n 230-243 / 27-34) |
| captains at the end | 7.3 → 6.4 | 6.8 → 6.6 | 7.3 → 5.8 | 7.2 → 6.3 |

Final rank S in all 36 games before and after; no bankruptcy, no darkness, deaths 1 / 0 (the one death is on seed set 3101 before:
0.08 per game; the first write-up said 0 / 0). By captain style (seed 3101, sent): melee
백중 / 우세 34 / 79% → 44 / 86%, ranged 71 / 96% → 59 / 92%, ranged + rally 66 / 94% → 39 / 86% (n 85). By day (seed 3101, sent): days
61-120 56 / 87% → 41 / 83%, days 241-365 45 / 88% → 49 / 91%.

### Review fixes (QA re-check of the first draft)

QA re-checked the first draft ("v1") on fresh seeds and raised seven points. "v2" is the code after this section. Before = `ea5304a`.

1. **Days 61-120 백중 optimistic** — *confirmed for the many-company bot, not for one company; fixed in part.* More fresh data,
   all with v1 code: the many-company bot's every looked-at offer (seeds 7101-7601, 6 × 12 games × 365 days, 48,207 offers) and the
   one-company probe (seeds 7101-7301 × 12 × 120 plus 9 starters × 6 on 7401, 16,610 offers). Days 61-120, 백중 / 우세 / 열세:
   many-company 45% (n 767) / 86% / 13%; one company 55% (n 328) / 92% / 23% (sent 51%, n 180). QA's one-company 37% sent (6101/6201)
   is one seed set: the same games under v2 read 53%, and with the evaluation sets pooled v1 read 45% sent / 53% probe. The two
   populations disagree at the same level — at average level 6-9 the one-company probe reads 52-57% and the many-company one 43-45% —
   so no level step fixes both, and the equal-weight joint fit stays at 0.969. Changes:
   - `BM_CAL_OWNLV` ≤ 9: 0.969 → **0.958**, tilting half-way to the safe side (offline on all probe rows: many-company 61-120 백중
     45 → 47%, level 6-9 45 → 49%; one company 51 → 53%, level 6-9 52 → 56%).
   - `BM_CAL_HEADS[1]`: 0.95 → **0.9**. QA's "1 member 34%" was real: a lone fighter read 백중 33% / 우세 76% (one-company probe,
     about 1,300 offers); now 53% / 85%.
   What is left (open issues): the many-company bot's rally captains (ranged + rally 백중 35-37% against 60-62% for the one-company
   tactician) and multi-company campaign parties (61-120 probe 백중 34%, n 120; the best single multi-company factor is only 0.985).
2. **Economy and S-day claims inside noise** — *accepted.* The results above are now labelled first draft and not findings; the
   table below has six many-company sets with the per-set ranges.
3. **Grace chip claimed protection that had ended** — *fixed* (§C): the chip shows only while the next payday is inside the grace
   week; after that, owed back pay shows as 「미룬 급료 N」 with the true consequence. Forced-poverty check (`grace2.js`, seeds 11-14):
   52 chip days, 0 with the next payday outside the grace week (QA's v1 count: 39 of 84); 61 back-pay chip days, 0 wrong.
4. **Popup wrong when one grace week covers two paydays** — *fixed* (§C): `next` / `nextGrace` and the matching sentence; 9 popups,
   1 of them with the next payday still in grace, 0 mismatches. Two popups in such a window are kept (two paydays were deferred).
5. **The issuer fix changes req and support, not only the label** — *accepted, documented* (§E). No code change: it is the rule
   every other contract in a calamity-held province follows.
6. **Wait hint untrue with an unfit company at home** — *fixed* (§B): `Game.allAway()` picks the sentence; 286 waiting days in the
   forced-poverty runs, 0 mismatches.
7. **Losing ★10 campaign battles pays 3-5k and drains 명성** — *not changed here (pre-existing, outside decision 7).* The battle seed is
   fixed per contract (`contractSalt`, so waiting does not reroll it): re-sending a near-identical party to the same campaign battle
   replays nearly the same fight, so nine losses in a row are one bad seed replayed by a bot that does not learn. Loss pay is reward ×
   (10% + `LOSS_PAY_SHARE` × share), large for ★10 campaigns, and each loss costs 30-60% of the contract's 명성, which the bot's
   rank F on day 120 shows; a player farming it loses rank. Whether a loss may out-pay ordinary wins is a loss-pay (stage 3)
   decision for the owner; listed under open issues.

**One company, before / v1 / v2, days 1-120** (human bot; five seed sets pooled: 1, 3101, 4101 × 12 × 365, QA's 6101 × 12 and
6201 × 16 × 120, new 8201 × 12 × 120; none used by a fit):

| | before | v1 | v2 |
|---|---|---|---|
| sent 백중, days 1-30 | 73% (234) | 61% (222) | 61% (225) |
| sent 백중, days 31-60 | 71% (218) | 58% (193) | 60% (198) |
| sent 백중, days 61-120 | 58% (360) | 45% (319) | 53% (330) |
| sent 우세, days 1-60 / 61-120 | 95 / 90% | 93 / 89% | 94 / 89% (n 850 / 579) |
| sent 열세, days 61-120 | 27% (113) | 14% (101) | 14% (106) |
| probe 백중, days 1-60 / 61-120 | 70 / 63% | 60 / 53% | 61 / 55% (n 686 / 629) |
| probe 우세 / 열세, days 61-120 | 93 / 29% | 92 / 22% | 93 / 25% |
| probe, 1 member: 백중 / 우세 | 52 / 79% | 37 / 81% | 53 / 87% (n 87 / 92) |
| probe, 2 members: 백중 | 46% | 55% | 59% (n 126) |
| missions lost | 11.9% | 14.4% | 13.8% |

Sent 백중 on days 61-120 by set, v1 → v2: evaluation 50 → 58%, QA 6101/6201 37 → 53%, 8201 54 → 43% (n 58-145 each: one set
moves ±8 points). Evaluation sets over 365 days: S on day 175 → 176 (36 of 36), rank A or better on day 120 in 32 → 34 of 36.

**Many companies, before / v1 / v2** (sensible bot, six sets × 12 games × 365 days: 8101 new, QA's 9101 and 9001, and 1, 3101,
4101; sent battles):

| | before | v1 | v2 |
|---|---|---|---|
| 백중, all days | 47% (6184) | 48% (5975) | 48% (6031) |
| 우세, all days | 87% | 88% | 89% (17,411) |
| 백중, days 1-60 | 62% (496) | 51% (468) | 52% (499) |
| 백중, days 61-120 | 57% (940) | 42% (876) | 45% (899) |
| 백중, days 121-240 / 241-365 | 47 / 39% | 47 / 49% | 48 / 47% (n 2188 / 2420) |
| 우세, days 61-120 | 87% (2197) | 85% (2039) | 85% (2081) |
| all sent, days 61-120 | 87% | 84% | 84% |
| boss sent at 우세 or 압도, won | 88% (285) | 85% (307) | 83% (325) |
| final / campaign won | 98 / 87% | 94 / 77% | 94 / 82% |
| day reaching S (set means) | 95.2 (86.1-101.3) | 99.7 (96.8-104.7) | 98.5 (96.6-101.6) |
| gold day 120 / 180 / 365 | 7.4k / 21.9k / 69.4k | 5.7k / 16.6k / 75.3k | 5.4k / 19.0k / 85.5k |
| gold day 365, set range | 46-94k | 54-114k | 48-134k |
| captains at the end | 6.8 | 6.1 | 6.5 |
| bankrupt / dark age / deaths | 0 / 0 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |

Final rank S in all 72 games for each version. The gold sets overlap so widely (one set's day-365 mean goes 93.5k → 53.7k under v1,
another 65.6k → 90.2k) that none of the gold changes is a result; S stays inside decision 5's 90-110 in every set and version except
before's 86.1.

**By first captain, before / v1 / v2** (one company, probe, 3-4 members, seed 5001 × 8 games × 120 days, never used by a fit):

| starter | 백중 | 우세 | 열세 |
|---|---|---|---|
| fixer | 44 / 43 / 49% | 88 / 87 / 87% | 10 / 15 / 16% |
| lancer | 54 / 47 / 48% | 92 / 93 / 94% | 23 / 18 / 19% |
| blademaster (바렌) | 51 / 56 / 53% | 91 / 92 / 94% | 14 / 18 / 21% |
| hedgemage | 73 / 33 / 36% | 96 / 89 / 89% | 24 / 11 / 10% |
| veteran | 53 / 56 / 52% | 92 / 94 / 95% | 32 / 23 / 19% |
| ironwall | 61 / 54 / 57% | 97 / 97 / 97% | 29 / 19 / 24% |
| huntress | 64 / 44 / 45% | 97 / 88 / 89% | 33 / 11 / 12% |
| fieldmedic | 81 / 61 / 61% | 98 / 95 / 95% | 48 / 16 / 17% |
| tactician | 87 / 53 / 58% | 100 / 96 / 97% | 62 / 22 / 22% |
| all (v2 n 1,139 / 2,544 / 979) | 64 / 50 / 51% | 95 / 92 / 93% | 31 / 17 / 18% |

The starter spread at 백중 stays 36-61% (before 44-87%); hedgemage and huntress still read a little optimistic (open issue of v1).

### Checks

v2 (after the review fixes):
- Roll: `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` = `11cadc0cceafa5e4262773fdadf780f9` with and without `SIM_SHADOW=1`;
  12 × 365 `ffee253e5364a3e6f882f9aed77254b0`, the same as before the change.
- `node tools/sim/battle.js 100`: miss 0 / soft 0 for all four outcomes.
- `node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4`: 2,867 battles, 8,335 alternative parties, every invariant 0
  (v1: 2,943 / 8,624; the forecast changes which offers the bots take).
- `node --check` on every `js/*.js`.
- `--set BM_CAL_LEAD.melee=1`, `--set 'BM_CAL_LEAD={…}'`, `--set 'BM_CAL_HEADS=[…]'`, `--set 'BM_CAL_OWNLV=[[…]]'` accepted;
  `BM_CAL_LEAD.foo` and `BM_CAL_HEADS.9` refused.
- Browser (400 × 800, `?resolve=battle`): the skip button appears when the only company is out and jumps to the return day's report;
  the wait hint shows, and reads 「지금 보낼 수 있는 용병단이 없습니다 …」 with an all-injured second company at home; 「유예 ~N일」 while
  the next payday is in grace, 「미룬 급료 N」 after it; the grace popup's two sentences; no console error, no horizontal overflow.

### Open issues

- **Many-company days 61-120 still read a little optimistic** (v2 sent 백중 45%, 우세 85%; before 57 / 87%). The remaining error is
  population-specific and no level step fixes it without making the one-company game read safer still: the many-company bot's
  ranged + rally captains (백중 35-37% against 60-62% for the one-company tactician; `rally` is a compromise) and multi-company
  campaign parties (probe 백중 34% on days 61-120, n 120; a whole-game multi-company factor would only be 0.985). A per-captain or
  multi-group term needs the captain key in the rows, which this measurement does not record.
- **The one-company game reads a little safe** (v2 probe 백중 61% on days 1-60 and 55% on days 61-120, 우세 93%), on purpose at the ≤ 9
  step (above). The per-starter spread, which was the larger error, stays small (table above).
- **Sent battles read worse than looked-at offers** (one company, days 61-120: sent 53% against probe 55%; many companies 45% against
  about 47%). Part of it is persistent contracts: a campaign or boss battle that was lost stays on the board with the same seed, and
  the bots re-send nearly the same party into it.
- **Losing a ★10 campaign battle can pay more than most wins** (3-4k gold, QA game 6104; pre-existing): loss pay is a share of the
  contract reward. It is self-limiting through the 명성 loss, but whether a loss may out-pay an ordinary win is the owner's call.
- **Boss contracts** stay below target at 우세 (v2 83% won when sent at 우세 or 압도, n 325). Same open issue as stage 3/4.
- **Captains recruited** 6.8 → 6.5 per game (v1 6.1); inside set noise (5.5-7.3 per set).

### Commands

```
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4        # also SIM_SEED=3101, 4101; before = SIM_ROOT of ea5304a
node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4
SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum                             # 11cadc0cceafa5e4262773fdadf780f9
# scratch (not in the repo): one.js (one-company bot: human / human2 / sens1, --probe, --starter), collect2.js (many-company bot,
#   every looked-at offer fought headless), fit2.js (joint target matching, PARAM=1), ana.js / stt.js (tables), bosscheck.js
# review fixes: collect3.js (as collect2, with star), collect4.js (many-company sent rows + summary, NOPROBE=1), fit3.js (refit
#   relative to the current constants; EVAL='{…}' to score a candidate), fin1.js / fin2.js (the review tables), grace2.js, ui2.js
```

## Calibration v3 (C21 data)

Date 2026-11-27. Base `ce63492` (the C21 data commit); the code was later rebased onto upstream commits that touched
`js/company.js`, `js/contract.js`, `js/muster.js` and `js/ui-tabs.js` (campaign betrayal fixed at dispatch). Only `js/stats.js`
changed here. Battle mode only. In the C21 data, the open issues were 3-company campaigns (백중 22-29%, 우세 80%), per-captain
spreads (many-company bot: blademaster 32-35%, tactician 34-41%, pilgrim 우세 54-64%, hexer 우세 80%; windhunter, bard and
demonhunter pessimistic, while the same tactician read 62-68% in the one-company bot), and bosses forecast 우세 or better winning
82.7% (mist 69.6%) against 98.8% for the human bot.

### Method

- **Data with specs.** C21 stores the forecast and the outcome, but not the battle. A scratch copy of
  `tools/sim/collect-calibration.js` (scratch `c3/coll.js`) ran the C21 seeds again and also saved the frozen spec of every row.
  The rows match C21 exactly: seed 1 diffs to 0 lines and all 128,126 forecasts are reproduced. From each spec, `feat2.js` recomputes
  every calibration ingredient (margin, time terms, captain style per group, each member's role, the support share, own level, boss
  archetype). `m2.py` rebuilds the forecast from these ingredients exactly (max |ΔR| = 0 on all 128k rows, before and after), so any
  candidate can be scored offline without bands drifting.
- **Fit** on C21 seeds only (sensible 1/3101/4101 × 12 × 365, human 1/3101 × 12 × 365, every offer looked at). Weighted maximum
  likelihood of p(win) = σ(13·ln R_pre)·S, where 13 is `BM_TIME_SLOPE`, R = 1 means 50%, and S is the time term. Rows have
  0.7 < R < 1.8, the two bots get equal weight, and bosses are excluded (their terms come from a band-target grid, below).
- **Out of sample** on new seeds, never fitted: sensible 5101 and 6101 × 12 × 365, human 5101 × 12 × 365. Two checks:
  (a) offline, the same battles re-forecast; (b) live, the collector run again with the new code, so the bots choose by the new
  words. "Before" = base code; "after" = base + this `js/stats.js` (scratch `c3/v3`).

### Drivers found

1. **Not the captain key: the members' fighting style.** A melee member's strength counts in `margin` the same as a ranged member's.
   In the battle, melee members walk into the front line, take the hits and fall first, and the retreat rule counts fallen heads.
   Ranged members fire from behind until the end. Residuals with the old forecast (ln R error, + = pessimistic; one company,
   0.8 < R < 1.6, by captain style | member roles):
   sensible `M|RRR` +0.12, `M|RR` +0.16, `R|MRR` +0.10 against `-|MMM` −0.10, `M|MMM` −0.08, `H|HMM` −0.10.
   The two bots field different companies:
   - The many-company bot's first company is two clerics and a warrior (hiring order plus reassignment). That company is what the
     starters blademaster, ironwall and tactician lead.
   - The one-company bot always fields warrior, cleric and archer.
   With the same members the two bots agree within about 3%: `M|MRH` reads +0.05 in human and +0.02 in sensible. The captain key
   only stood in for the roster, so a per-key table would have fitted the roster of one bot and broken the other: tactician needs
   −4% in the sensible bot and +6% in the human bot.
2. **Support soldiers count for less than their stats.** After the forecast, the share of the allied side's strength
   (Σ hp × atk) held by the client's support groups had logit coefficients of −2.8 (sensible) and −6.8 (human); a level-gap proxy
   does not explain it (gap coefficient 0.00 once the share is in). The support soldiers fight in their own row and rout when their
   leader falls. The battle is lost when half of *ours* are down, whatever the support still does. This share was also most of
   the human bot's general pessimism at high levels: it fields fewer support-heavy fights than the sensible bot.
3. **Three companies.** With the role and support terms in, 3-company battles still read optimistic (−0.07 in ln R, and −0.12 to
   −0.16 with an external company in them). On the new seeds the old forecast gave the same picture (백중 30%, 우세 73%), so this is
   not noise. Two companies are noise: 백중 69% on the C21 seeds against 41% on the new ones (campaign battles repeat the same
   seed, so the effective n is small). They get no factor.
4. **Bosses: the archetype counts twice, and the curve is flat.** Per-boss R50 with the old forecast: frost 0.86, oasis 0.87,
   wheat 0.905, silverwood 0.96, mist 1.05. That is the boss's own `BM_CAL_ARCH` factor once more (1.14, 1.185, 1.091, 1.048,
   0.945). A boss holds close to half the enemy's strength, so its archetype weighs more than an ordinary leader's. The outcome
   slope is 9.1 for bosses against 15.7 for ordinary contracts, so one factor cannot hold 백중 and 우세 together. The human bot's 98.8%
   is the same curve: it sends bosses late and at 압도 or high 우세.
5. **Healer captains** (fieldmedic, saintknight, pilgrim) behave differently from the other "ranged" captains. They get their own
   value, kept near the old one (below).

### Changes (`js/stats.js`, all in `Stats.KN`, all settable with `--set`)

| Knob | Before | After | Meaning |
|---|---|---|---|
| `BM_CAL_ROLE` (new) | – | melee 1, ranged 1.284, heal 1.101 | Each non-recruit own or external unit except the captain of an own company: its first skill sets its role (heal; range ≥ `RANGE_MIN`; else melee). Geometric mean over all our units, with the captain's place at 1. All 1 = off. |
| `BM_CAL_ALLY` (new) | – | 0.541 | R × ALLY^(support groups' share of Σ hp·atk on our side). 1 = off. |
| `BM_CAL_GROUPS` (new) | – | [1, 1, 1, 0.91] | By number of own + external groups. |
| `BM_CAL_BOSS` (new) | – | arch 1.5, sure 0.65 | Boss: `BM_CAL_ARCH`^arch for the boss's archetype; ln R × sure (pulls toward 1) before the time term ②. 1 / 1 = off. |
| `BM_CAL_LEAD` | melee 0.98, ranged 1.082, rally 1.035 | melee 1, ranged 1.109, **heal 1.08** (new), rally 1.068 | Same group-weighted form; healer captains (first skill heals) now use `heal`. |
| `BM_CAL_HEADS` | [1, 0.9, 0.94, 1, 1] | [1, 0.965, 0.972, 1, 1] | Most of the old 1- and 2-member factor was roles: a reduced party has usually lost its archer or cleric. |
| `BM_CAL_OWNLV` | 0.887 / 0.944 / 0.958 / 0.99 / 0.983 / 0.977 | 0.876 / 0.926 / 0.966 / 1.009 / 1.015 / 1.024 | Refitted with the role term. |
| `BM_CAL_SPECIAL` | boss 0.912, capStory 0.952, story 1.021, campaign 1.009 | boss 0.866, capStory 0.967, story 0.956, campaign 0.94 | Refitted (`final` unchanged). Campaign 1.009 had been fitted on multi-company campaigns, which `BM_CAL_GROUPS` now carries. One-company campaigns read 46% / 84%. |

`Stats.roleCal(spec)` is exported next to `leadCal`. `leadStyle` also returns `heal`. Not changed: `margin`, the battle, `BANDS`,
`CAL_KIND`, `BM_CAL_ARCH`, the time term and the board code.

- **Boss values** come from a grid over arch ∈ {1.5, 2, 2.5} × sure 1 − {0.15 … 0.45} × boss factor {0.95, 1, 1.05} on the C21 sensible
  offers. The pick is arch 1.5, sure 0.65, factor 0.95, folded into `BM_CAL_SPECIAL.boss` as 0.912 × 0.95: boss 백중 54%, 우세 89%,
  우세 or better 89.7%. Maximum likelihood over all R had given 79% at 우세 or better, so it is not used for bosses.
- **`BM_CAL_LEAD.heal`**: the fit gave 1.117, but on the live new seeds saintknight then read 33% / 75%. 1.08, about the old value
  for healers (they were counted as ranged), gives saintknight 54% / 91% sent. The one-company fieldmedic becomes a little
  pessimistic (57 → 61%).
- **Rejected:**
  - A concentration term (Herfindahl or top-group share). It replaced the support term but overshot multi-company battles to
    69-81% 백중.
  - Lane margins (each of our groups against its own enemy group), heal saturation and the rally buff value as an explicit kit term.
    None was significant after the role term.
  - A per-captain table: confounded, see driver 1.
  - A 2-company factor: noise, see driver 3.

### Results

Cells are 백중 / 우세 win %, before → after; after the arrow, (n at 백중 / n at 우세). Four views:
- **fit**: the C21 offers, in sample.
- **re-forecast**: the new seeds, the same battles under the new forecast (out of sample, offline).
- **live sent**: the new seeds, battles the bots actually sent under each forecast.
- **live offers**: the new seeds, every offer looked at in the live games.

#### sensible bot

*All*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| all | 48 / 89 → 47 / 87 (8038/9018) | 45 / 88 → 46 / 86 (5520/5786) | 44 / 89 → 46 / 86 (1803/5354) | 45 / 88 → 46 / 85 (5558/5645) |

*Companies sent together*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| 1 | 48 / 89 → 47 / 87 (7810/8852) | 45 / 88 → 46 / 86 (5381/5685) | 44 / 89 → 46 / 86 (1752/5221) | 45 / 88 → 46 / 85 (5414/5508) |
| 2 | 69 / 88 → 61 / 88 (112/76) | 41 / 94 → 35 / 97 (71/38) | 53 / 94 → 60 / 88 (25/59) | 41 / 94 → 50 / 88 (66/59) |
| 3 | 29 / 81 → 43 / 83 (116/90) | 30 / 73 → 37 / 90 (68/63) | 36 / 73 → 65 / 85 (26/74) | 30 / 73 → 55 / 86 (78/78) |

*Campaign battles by companies*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| 2 co. | 68 / 88 → 61 / 88 (112/73) | 41 / 94 → 35 / 97 (71/37) | 53 / 94 → 60 / 88 (25/59) | 41 / 94 → 50 / 88 (66/59) |
| 3 co. | 29 / 80 → 43 / 84 (114/82) | 29 / 72 → 36 / 90 (67/59) | 36 / 72 → 65 / 85 (26/67) | 29 / 72 → 53 / 85 (73/67) |

*Captain key (top 10 by n in C21, then the keys named in the task; rows with n ≥ 40 somewhere)*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| shadowlord | 45 / 87 → 47 / 83 (1100/1112) | 51 / 89 → 43 / 81 (582/665) | 48 / 90 → 41 / 84 (236/630) | 51 / 89 → 42 / 84 (691/644) |
| pirateking | 51 / 86 → 47 / 82 (800/993) | 40 / 86 → 42 / 83 (407/409) | 40 / 87 → 45 / 83 (196/467) | 40 / 86 → 42 / 80 (575/524) |
| windhunter | 68 / 96 → 63 / 94 (768/933) | 50 / 93 → 49 / 92 (482/470) | 50 / 93 → 59 / 94 (113/454) | 50 / 93 → 60 / 94 (424/459) |
| tactician | 32 / 85 → 33 / 85 (746/737) | 49 / 88 → 48 / 91 (46/47) | 50 / 88 → 29 / 88 (17/52) | 49 / 88 → 35 / 89 (43/53) |
| multi | 47 / 84 → 53 / 85 (224/165) | 35 / 80 → 36 / 93 (137/100) | 47 / 80 → 63 / 86 (51/132) | 35 / 80 → 52 / 87 (143/136) |
| ironwall | 42 / 85 → 44 / 83 (466/511) | 43 / 87 → 43 / 85 (776/775) | 40 / 87 → 47 / 86 (240/672) | 43 / 87 → 49 / 86 (711/733) |
| blademaster | 34 / 83 → 45 / 85 (452/466) | 40 / 78 → 45 / 80 (317/378) | 36 / 80 → 47 / 82 (115/338) | 40 / 78 → 45 / 81 (366/368) |
| saintknight | 42 / 93 → 51 / 94 (340/423) | 49 / 93 → 51 / 91 (298/353) | 48 / 93 → 54 / 91 (87/313) | 49 / 93 → 48 / 88 (269/327) |
| elfwarden | 60 / 94 → 58 / 95 (261/340) | 50 / 94 → 56 / 91 (257/270) | 44 / 94 → 54 / 94 (101/365) | 50 / 94 → 56 / 94 (328/371) |
| khan | 59 / 95 → 46 / 91 (256/360) | 62 / 91 → 58 / 90 (233/244) | 57 / 91 → 59 / 88 (68/189) | 62 / 91 → 57 / 87 (183/201) |
| pilgrim | 33 / 52 → 43 / 56 (21/32) | – / – → – / – (0/0) | – / – → – / – (0/0) | – / – → – / – (0/0) |
| hexer | 43 / 80 → 42 / 77 (99/119) | 47 / 79 → 51 / 78 (79/81) | 44 / 78 → 45 / 87 (58/136) | 47 / 79 → 45 / 86 (172/142) |
| bard | 73 / 93 → 52 / 90 (132/150) | – / – → – / – (0/0) | – / – → 48 / 80 (23/59) | – / – → 49 / 80 (55/60) |
| demonhunter | 85 / 96 → 85 / 97 (20/29) | – / – → – / – (0/0) | – / – → – / – (0/0) | – / – → – / – (0/0) |
| liberator | 50 / 85 → 40 / 82 (282/369) | 31 / 83 → 29 / 77 (238/273) | 28 / 84 → 36 / 81 (89/251) | 31 / 83 → 31 / 81 (278/265) |

*Boss key*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| frost | 85 / 81 → 76 / 86 (74/49) | 57 / 95 → 57 / 96 (46/24) | 75 / 93 → 57 / 100 (7/18) | 57 / 95 → 52 / 100 (29/18) |
| mist | 38 / 66 → 37 / 82 (124/49) | 35 / 72 → 36 / 78 (89/45) | 38 / 60 → 41 / 82 (17/17) | 35 / 72 → 52 / 86 (64/22) |
| oasis | 76 / 92 → 72 / 96 (89/28) | 64 / 100 → 49 / 100 (85/27) | 64 / 100 → 67 / 100 (6/20) | 64 / 100 → 67 / 100 (39/20) |
| silverwood | 44 / 74 → 40 / 74 (220/35) | 52 / 76 → 40 / 82 (170/22) | 46 / 73 → 53 / 67 (19/21) | 52 / 76 → 43 / 58 (130/38) |
| wheat | 78 / 93 → 65 / 93 (43/30) | 65 / 87 → 63 / 89 (30/27) | 57 / 81 → 80 / 84 (5/19) | 65 / 87 → 54 / 91 (13/32) |

*Day band*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| (0, 30] | 43 / 90 → 47 / 90 (285/486) | 48 / 88 → 51 / 88 (196/308) | 39 / 88 → 48 / 89 (65/293) | 48 / 88 → 52 / 89 (186/297) |
| (30, 60] | 53 / 87 → 52 / 86 (481/504) | 45 / 86 → 42 / 85 (287/323) | 43 / 87 → 46 / 86 (104/274) | 45 / 86 → 48 / 86 (342/300) |
| (60, 120] | 44 / 84 → 44 / 83 (1416/1157) | 46 / 86 → 48 / 87 (928/724) | 48 / 87 → 51 / 85 (257/673) | 46 / 86 → 49 / 83 (852/728) |
| (120, 240] | 49 / 87 → 51 / 87 (2866/3158) | 45 / 88 → 51 / 88 (1888/2057) | 45 / 89 → 49 / 87 (643/1932) | 45 / 88 → 48 / 85 (2028/2082) |
| (240, 365] | 48 / 91 → 45 / 87 (2990/3713) | 45 / 90 → 41 / 85 (2221/2374) | 43 / 89 → 42 / 86 (734/2182) | 45 / 90 → 43 / 86 (2150/2238) |

Boss contracts forecast 우세 or 압도, won: fit: 80.2% (222) → 86.3% (204); re-forecast: 84.1% (151) → 88.2% (152); live sent: 82.5% (103) → 87.4% (103); live offers: 84.1% (151) → 84.1% (138)

#### human bot

*All*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| all | 59 / 94 → 50 / 91 (2993/6932) | 57 / 94 → 48 / 91 (1596/3490) | 55 / 94 → 43 / 89 (421/813) | 57 / 94 → 46 / 91 (1543/3410) |

*Companies sent together*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| 1 | 59 / 94 → 50 / 91 (2993/6932) | 57 / 94 → 48 / 91 (1596/3490) | 55 / 94 → 43 / 89 (421/813) | 57 / 94 → 46 / 91 (1543/3410) |

*Campaign battles by companies*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| 1 co. | 46 / 84 → 44 / 83 (252/275) | 42 / 86 → 38 / 87 (156/137) | 45 / 91 → 23 / 83 (47/58) | 42 / 86 → 36 / 85 (118/130) |

*Captain key (top 10 by n in C21, then the keys named in the task; rows with n ≥ 40 somewhere)*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| blademaster | 60 / 95 → 53 / 92 (538/1216) | 63 / 93 → 58 / 89 (233/609) | 57 / 90 → 39 / 80 (54/114) | 63 / 93 → 44 / 89 (213/456) |
| fixer | 55 / 92 → 50 / 90 (353/917) | – / – → – / – (0/0) | – / – → – / – (0/0) | – / – → – / – (0/0) |
| fieldmedic | 57 / 97 → 61 / 97 (339/925) | – / – → – / – (0/0) | – / – → – / – (0/0) | – / – → – / – (0/0) |
| veteran | 71 / 97 → 55 / 92 (386/923) | – / – → – / – (0/0) | – / – → – / – (0/0) | – / – → – / – (0/0) |
| huntress | 53 / 90 → 47 / 87 (331/693) | 54 / 95 → 45 / 93 (286/521) | 49 / 96 → 45 / 88 (64/114) | 54 / 95 → 50 / 90 (239/478) |
| ironwall | 65 / 95 → 46 / 90 (247/573) | – / – → – / – (0/0) | – / – → – / – (0/0) | – / – → – / – (0/0) |
| lancer | 57 / 96 → 41 / 94 (227/463) | 63 / 95 → 51 / 93 (260/577) | 60 / 96 → 38 / 88 (47/130) | 63 / 95 → 47 / 91 (258/575) |
| tactician | 68 / 97 → 50 / 92 (210/628) | 76 / 97 → 59 / 95 (206/628) | 75 / 98 → 49 / 97 (53/132) | 76 / 97 → 45 / 94 (226/703) |
| hedgemage | 43 / 92 → 38 / 90 (123/261) | 47 / 92 → 42 / 90 (523/1038) | 51 / 92 → 42 / 91 (133/230) | 47 / 92 → 46 / 91 (490/1014) |

*Boss key*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| silverwood | 100 / 94 → 93 / 95 (15/21) | 75 / 95 → 78 / 96 (9/24) | – / 100 → 80 / 67 (5/6) | 75 / 95 → 80 / 75 (5/12) |
| wheat | 80 / 100 → 83 / 100 (6/18) | 100 / 100 → 100 / 100 (2/9) | 100 / 100 → 100 / 86 (3/7) | 100 / 100 → 50 / 91 (6/11) |

*Day band*

| slice | fit | re-forecast | live sent | live offers |
|---|---|---|---|---|
| (0, 30] | 45 / 92 → 42 / 90 (196/483) | 47 / 86 → 48 / 86 (93/273) | 58 / 92 → 56 / 90 (34/79) | 47 / 86 → 35 / 84 (109/262) |
| (30, 60] | 49 / 92 → 48 / 89 (220/570) | 51 / 94 → 53 / 90 (94/229) | 55 / 97 → 55 / 87 (33/68) | 51 / 94 → 48 / 87 (114/279) |
| (60, 120] | 53 / 93 → 47 / 90 (565/1287) | 50 / 91 → 42 / 89 (326/625) | 49 / 89 → 39 / 88 (71/111) | 50 / 91 → 42 / 86 (271/526) |
| (120, 240] | 59 / 94 → 54 / 91 (913/2019) | 55 / 95 → 50 / 93 (459/1021) | 53 / 95 → 40 / 88 (147/261) | 55 / 95 → 49 / 93 (519/1107) |
| (240, 365] | 66 / 97 → 50 / 94 (1099/2573) | 65 / 96 → 50 / 93 (624/1342) | 59 / 95 → 41 / 91 (136/294) | 65 / 96 → 47 / 94 (530/1236) |

Boss contracts forecast 우세 or 압도, won: fit: 98.8% (169) → 98.8% (171); re-forecast: 98.8% (80) → 98.8% (82); live sent: 100.0% (48) → 92.1% (38); live offers: 98.8% (80) → 93.8% (64)

**Sensible bot, seeds 7101-7112 × 365 days** (`bot.js --resolve battle`; this measures the current tree with and without this
`js/stats.js`; seeds used by no fit):

| | before | after |
|---|---|---|
| sent 백중 / 우세 / 압도 won | 47.6% (1035) / 88.8% (3025) / 100% | 47.5% (905) / 86.0% (2805) / 99.8% |
| days 241-365, all sent, won | 85.0% | 81.8% |
| boss / campaign / story, all sent, won | 84.5% (71) / 84.8% / 70.9% | 72.3% (83) / 91.0% / 79.3% |
| day reaching S, final rank | 91, 12 × S | 93, 12 × S |
| gold day 120 / 365 | 8.4k / 88k | 8.9k / 103k |
| bankrupt, deaths, captains at the end | 0, 0, 7.2 | 0, 0, 6.7 |

- **Bosses.** Every boss send counts, at any word. Boss forecasts are now pulled toward 백중, so the bot, which takes 백중 one time
  in three and retries lost specials, makes more boss attempts at 백중 (83 against 71). 우세 or better still wins 87-88% (above).
- **Economy.** Gold and S day are inside the seed-set noise measured in "One-company polish".

### Gates

- Roll md5, `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum`, with and without `SIM_SHADOW=1`:
  - `11cadc0cceafa5e4262773fdadf780f9` on the base `ce63492` plus this `js/stats.js`.
  - `f1712f75dd50877f69a65caf254be083` on the current tree. That is the same as the current HEAD without this change: the upstream
    `extAfterMission` change (`js/company.js`) moved the roll md5, not this work.
- `node tools/sim/battle.js 100`: miss 0 / soft 0 for all four outcomes.
- `node tools/sim/shadow.js 6 365 --resolve battle --check`: 3,021 battles, every invariant 0.
- `node --check js/stats.js`.
- `--set` checks:
  - Accepted: `BM_CAL_ROLE.ranged=1`, `'BM_CAL_GROUPS=[1,1,1,1]'`, `BM_CAL_BOSS.sure=1`, `BM_CAL_ALLY=1`, `BM_CAL_LEAD.heal=1.08`.
  - Refused: `BM_CAL_ROLE.foo` and `'BM_CAL_GROUPS=[1,1]'`.
- Forecast cost (mid-game save, day 150, 3 companies, 200 cold `capability()` calls): 5.2-6.5 ms per call before and after; a single
  `forecast()` costs 46-54 µs against 46-51 µs before. The added unit loop is noise next to `margin`'s 30 bisection steps.

### Remaining misses (open)

- **The sensible bot's tactician** still reads 백중 33% / 우세 85% on the C21 seeds, and 29-35% at small n on the new seeds. The human
  bot's tactician reads 49-59% under the same forecast, so a per-key constant would trade one for the other. The roster explains
  part of it: two clerics, sometimes a cleric with a melee first skill. The rest is not found.
- **우세 for some sensible captains is at 80-84%**: shadowlord, pirateking, liberator (77-82%), blademaster (80-85%), shadowqueen.
  These are melee rogue and warrior captains. In-sample `BM_CAL_LEAD.melee` fitted to 1.0 against the old 0.98.
- **Late game, sensible bot**: days 241-365 at 41-45% / 85-87%, a little optimistic. The human bot reads 47-50% / 93-94% at the same
  levels. The two bots still disagree at high levels after roles and support share; the level step sits between them.
- **Human bot, sent battles**: 43% / 89%, against 46% / 91% for every offer looked at. This is the known gap between sent and
  looked-at battles (lost campaign and special battles keep their seed). One-company campaign battles sent: 23% (n 47).
- **Bosses per key**: the per-boss 백중 is still spread (frost 52-76%, silverwood 40-53%, at small n). Silverwood (beast) 우세
  58-82% is the weakest. A beast boss is fast and has 0.6 def, and the boss's archetype exponent fits the other four better.
- **Pilgrim, demonhunter, bard**: 20-60 battles per word on the C21 seeds and none or few on the new seeds, so no conclusion.
  On the C21 offers, bard 73 → 52% and pilgrim 33 → 43% / 52 → 56%.

### Commands and scratch

```
# scratch (not in the repo): c3/coll.js (collector + spec per row), feat2.js (exact ingredients), m2.py (exact offline forecast
#   model + fit), r4.py (fit), a33.py (boss grid), final_tables.py (tables above), bench.js (capability timing)
node c3/coll.js --strategy sensible --seeds 1,3101,4101 --jobs 4      # SIM_ROOT = base snapshot; also human 1,3101
OUT=… node c3/coll.js --strategy sensible --seeds 5101,6101           # before (base) and after (base + this stats.js); human 5101
SIM_SEED=7101 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 2
```

### Review fixes (v3.1, after the adversarial review)

Date 2026-11-27, same session. An adversarial review of the v3 values above, on fresh seeds, found six things:
1. melee captain + 1 melee + 2 ranged members (`M|MRR`) now read optimistic;
2. small and captain-less parties in the one-company bot regressed;
3. story contracts were missed (sensible 우세 71% in and out of sample);
4. smaller over-corrections (beastmaster, capStory, support share ≥ 0.3);
5. the sensible tactician was unresolved;
6. the economy gain did not replicate.

Only `js/stats.js` changed again. The values in the tables above (the v3 section) are superseded by the ones below.

#### How

- **Richer per-row ingredients.** Scratch `v4/feat3.js` reads the spec of every row (the C21 seeds with specs from `c3/data`, the
  new seeds from `c3/before`, plus new seeds 8101 for both bots collected on the base for this fix). For every one of our units it
  records role, `dps`, `ehp` and `hps` (k = 1 `sideOf` against the real enemies), and for the enemy it records role counts, the
  power share of the top unit and the enemy `sideOf`.
- **Exact offline model.** `v4/m4.py` + `fx.py` + `fin.py` rebuild the old, the v3 and the new forecast from these ingredients. Old
  and v3 match the JS exactly (|ΔR| = 0 on all rows). The new one matches to 0.001, which is the R rounding.
- **Fit** as before: C21 offers only, bosses excluded, both bots weighted the same, likelihood with slope 13. Then the boss terms
  are picked from a small grid against the 백중 / 우세 targets (likelihood over all R again gave about 76% at 우세 for bosses).
- **Driver search.** With the current forecast fixed as an offset, I ran one-variable logits in each bot separately. A driver
  counts only if its coefficient has the same sign and size in both bots. Level, star, day, enemy count, support share and the
  concentration terms all flip sign between the bots. Three quantities do not flip.
- **Out of sample:**
  - (a) Re-forecast of the same battles on new seeds (sensible 5101, 6101 and 8101, human 5101 and 8101; 128,970 rows, all from
    the base code).
  - (b) Live games on seeds 10101 (sensible and human × 12 × 365), run three times: on the base `ce63492`, on base + the v3
    `stats.js`, and on base + this `stats.js`.

#### What the review findings turned out to be

Three of the drivers do not flip sign between the bots. The first two were not in the forecast at all.

1. **Enemy healing.** When the enemy's healing per second is a large share of our damage per second, the forecast is far too
   optimistic.
   - These are soldier contracts with two clerics in the enemy roster, or a cleric leader.
   - Old forecast, enemy healing ≥ 0.4 of our damage: 백중 11-22% / 우세 58-68% (sensible) and 5-9% / 56-59% (human), n of
     about 40-150 per cell. v3 was no better.
   - ln R error −0.15 to −0.20 once the enemy heals more than about 0.3 of our damage.
   - Q25 measured the same battles: enemy healing returned 80% of the damage taken. `margin` adds healing to hp only through
     `hps·T·0.6` with T clamped to 6-60 s.
2. **Our healing, by amount.** v3 counted it by head (`ROLE.heal` 1.101 per healer). The amount matters instead.
   - As an offset logit, our healing per our damage gets +0.07 (sensible) and +0.09 (human), the same in both bots. In the fit,
     healing over the *enemy's* damage works better: out-of-sample log-loss 267.5 against 272.1.
   - This is also why the bots disagreed at high level. The human bot's healing per damage grows with level (0.24 → 0.38). The
     sensible bot's falls (0.22 → 0.14).
   - The v3 level steps (1.009 / 1.015 / 1.024 above level 9) were carrying this. With heal amounts in, they return to about 1.
3. **Enemy ranged share.** Enemy archers and mages also out-perform `margin`, for the same reason ours do.
   - ln R −0.18 per unit of enemy ranged share in both bots, with dnll −1,158 (sensible) and −470 (human). This is the
     strongest single term found.
   - Story contracts field 39% ranged enemies (normal 17%). That is the story miss (finding 3), not a curve shape: the story
     losses at 우세 were retreats.
4. **Our ranged share.** The per-member geometric mean of v3 was the wrong shape.
   - The comp table (one company, both bots) is convex in the ranged share: 0, 1, 2, 3 of 4 ranged give −0.02, +0.03, +0.08,
     +0.20.
   - A ranged captain is worth about +0.08 more than a ranged member.
   - A lone archer earned only about a third of the full-party effect (`-|R` +0.10 against `-|RRR` +0.32).
   - The new form counts ranged heads, captain included, over max(heads, 3). It has a linear and a square term.

Finding by finding:
- **1, `M|MRR`: fixed** by 4 and 2. Re-forecast 36/73 → 40/83, live offers 33/78 → 40/88.
- **2, small and captain-less human parties: partly.**
  - The lone archer is fixed by `MIN_N`: `-|R` no longer gets the full bonus.
  - Captain-less human parties still read optimistic: ln R −0.02 to −0.05 at 1-3 heads, while the sensible bot's captain-less
    trios read +0.03. Opposite signs, so no single knob fits; this is listed under open issues.
- **3, story: fixed** by 3. Re-forecast 우세 79 → 83.
- **4, smaller ones:**
  - Support share ≥ 0.3 is now 56/92 (v3 60/93), slightly pessimistic.
  - capStory 76 → 80.
  - beastmaster 81 → 89.
- **5, tactician: fixed in the re-forecast** (sensible 43/86 → 47/89). Live 35/78 → 52/93 offers (n 176/204).
  - The sensible tactician leads two clerics and a melee member (`R|HHM`, `R|HMM`). Those are the rosters the heal-amount term
    moves most.
- **6, economy:** re-measured below; inside seed noise.

#### Changes (v3 → v3.1, all in `Stats.KN`, commented, `--set`-able)

| Knob | v3 | v3.1 | Meaning |
|---|---|---|---|
| `BM_CAL_ROLE` | melee 1, ranged 1.284, heal 1.101 (per member, geometric mean) | ranged 1.1774, ranged2 1.268, MIN_N 3 | s = ranged heads (captain included; first skill not a heal and range ≥ `RANGE_MIN`) / max(heads, MIN_N); R × ranged^s × ranged2^(s²) |
| `BM_CAL_FOE` (new) | – | ranged2 0.7022 | e = enemy units with a ranged first skill / enemy units; R × ranged2^(e²) |
| `BM_CAL_HEAL` (new) | – | ours 1.7248, foe 0.353, FREE 0.2, boss 1.18, CAP 1 | R × ours^min(CAP, our hps / enemy dps) × foe^max(0, min(CAP, enemy hps / our dps) − FREE); bosses use `boss` instead of `ours` |
| `BM_CAL_LEAD` | 1 / 1.109 / 1.08 / 1.068 | 1.029 / 1.056 / 1.066 / 1.063 | melee / ranged / heal / rally captains, against no captain |
| `BM_CAL_HEADS` | [1, 0.965, 0.972, 1, 1] | [1, 1.048, 1.005, 1, 1] | refitted with `MIN_N` |
| `BM_CAL_OWNLV` | .876 .926 .966 1.009 1.015 1.024 | .862 .915 .968 .994 .988 .994 | the high-level steps were heal amount |
| `BM_CAL_SPECIAL` | boss .866, capStory .967, story .956, campaign .94 | boss .87, capStory .95, story 1, campaign .961 | `final` unchanged |
| `BM_CAL_ALLY` | 0.541 | 0.506 | |
| `BM_CAL_GROUPS` | [1, 1, 1, 0.91] | [1, 1, 1, 0.914] | |
| `BM_CAL_BOSS` | arch 1.5, sure 0.65 | arch 1.5, sure 0.6 | with boss .87 and `HEAL.boss` |

- **Code.** New `sidesK1(groups)` computes the k = 1 `sideOf` pair once. `killTime(groups, sd)` and the new `healCal` share it,
  so the heal term costs no extra pass. `roleCal` now also counts enemy ranged units.
- **No per-captain table.**
- **`HEAL.boss`:** against a boss, our healing is worth about a third as much. The boss fit gave ln coefficient 0.165 against
  0.545; the boss stuns and hits big.
- **`CAP`** stops R growing into the thousands against weak enemies. It is neutral on the log-loss (fit 247.08 → 247.06).
- **Rejected:**
  - A support-share hinge: small gain, collinear with `ALLY`.
  - A front-line shortfall term (melee heads < half the heads): coefficient about +0.02 on the per-comp offsets, no gain.
  - An ordered, retreat-truncated strength term (front units fall first, stop at half the heads): its sign was not the same in
    the two bots.
  - A healer-count term: `ROLE.heal` fitted to 0.92 once heal amount was in.
  - Enemy-heal thresholds 0.25 and 0.3: 0.2 was best out of sample.
  - A linear enemy-ranged term next to the square one: its coefficient was +0.09, and dropping it moved the out-of-sample
    log-loss by 0.25.

#### Fit quality (log-loss × 1000 over every row, slope 13; lower is better)

| rows | old | v3 | v3.1 |
|---|---|---|---|
| C21 offers, sensible (fit) | 199.9 | 183.9 | 164.0 |
| C21 offers, human (fit) | 194.0 | 173.5 | 139.0 |
| new-seed offers, sensible (re-forecast) | 196.9 | 189.7 | 165.1 |
| new-seed offers, human | 196.7 | 174.1 | 150.1 |
| new-seed sent, sensible | 273.4 | 265.8 | 228.0 |
| new-seed sent, human | 260.1 | 232.7 | 196.7 |

#### Results: 백중 / 우세 win %, old → v3 → v3.1 (n at 백중 / 우세 for v3.1)

Offline: the same battles under each forecast. Fit = C21 offers; re-forecast = new seeds 5101/6101/8101 (sensible) and 5101/8101
(human), all collected on the base code.

##### Offline, sensible bot

| slice | fit: C21 offers | re-forecast: new-seed offers | re-forecast: new-seed sent |
|---|---|---|---|
| all | 48/89 → 47/87 → 47/88 (7538/8702) | 46/88 → 47/86 → 48/88 (7547/8458) | 45/88 → 52/88 → 54/91 (2409/6586) |
| 1 co. | 48/89 → 47/87 → 47/88 (7364/8512) | 46/88 → 47/86 → 48/88 (7359/8316) | 45/89 → 52/88 → 54/91 (2346/6463) |
| 2 co. | 69/88 → 61/88 → 58/94 (89/95) | 41/90 → 38/89 → 41/91 (87/64) | 49/92 → 51/92 → 50/96 (20/53) |
| 3 co. | 29/81 → 43/83 → 44/83 (85/95) | 33/74 → 42/89 → 47/85 (101/78) | 38/74 → 39/89 → 53/84 (43/70) |
| story | 40/71 → 45/71 → 44/76 (850/600) | 39/76 → 45/79 → 43/83 (916/601) | 41/82 → 54/87 → 52/87 (165/261) |
| capStory | 52/83 → 44/81 → 45/83 (245/309) | 51/80 → 50/76 → 48/80 (294/355) | 55/84 → 60/81 → 53/84 (60/203) |
| campaign | 45/84 → 52/86 → 52/89 (176/182) | 36/79 → 40/90 → 43/88 (191/136) | 44/79 → 44/90 → 52/89 (63/118) |
| (0, 30] | 43/90 → 51/90 → 50/90 (272/437) | 49/87 → 52/89 → 51/87 (281/413) | 42/87 → 51/89 → 54/89 (105/372) |
| (30, 60] | 53/87 → 52/86 → 49/87 (464/508) | 48/86 → 47/86 → 44/85 (439/503) | 47/87 → 47/87 → 51/88 (126/360) |
| (60, 120] | 44/84 → 44/84 → 45/83 (1410/1133) | 45/85 → 48/85 → 47/87 (1367/1126) | 47/86 → 54/87 → 57/90 (348/794) |
| (120, 240] | 49/87 → 51/87 → 50/88 (2663/3048) | 45/87 → 51/86 → 51/89 (2670/2966) | 44/89 → 55/89 → 57/92 (956/2318) |
| (240, 365] | 48/91 → 45/87 → 45/90 (2729/3576) | 46/89 → 43/85 → 46/88 (2790/3450) | 45/89 → 48/88 → 50/91 (874/2742) |
| foe heal >= 0.4 of our dmg | 22/58 → 23/55 → 53/67 (100/91) | 11/68 → 11/58 → 53/86 (103/70) | 11/66 → 14/65 → 60/86 (68/58) |
| foe ranged share >= 0.35 | 33/73 → 32/70 → 41/84 (1448/1313) | 31/71 → 31/69 → 42/83 (1501/1282) | 28/73 → 31/71 → 46/86 (565/994) |
| support share >= 0.3 | 34/79 → 59/94 → 55/87 (346/68) | 35/75 → 60/93 → 56/92 (352/73) | 36/75 → 62/92 → 69/92 (121/49) |
| 1 head | 80/94 → 75/100 → 62/93 (13/27) | 59/92 → 75/91 → 57/85 (23/20) | 50/92 → 76/91 → 71/89 (14/18) |
| 2 heads | 49/98 → 65/99 → 58/95 (62/84) | 66/94 → 63/95 → 53/94 (49/96) | 72/94 → 73/94 → 79/95 (19/79) |
| no captain | 46/90 → 49/88 → 48/88 (1538/1590) | 49/91 → 52/90 → 51/90 (1628/1805) | 51/91 → 59/92 → 65/94 (488/1340) |
| M|MRR | 49/85 → 37/76 → 41/82 (733/757) | 47/86 → 36/73 → 40/83 (795/865) | 43/88 → 42/80 → 35/87 (178/628) |
| M|HMR | 53/92 → 51/89 → 49/88 (603/713) | 47/88 → 45/83 → 44/88 (574/587) | 46/88 → 46/85 → 42/88 (150/456) |
| R|MRR | 78/97 → 64/93 → 59/95 (482/708) | 65/93 → 61/83 → 54/93 (202/270) | 69/94 → 62/89 → 54/94 (54/194) |
| -|HMM | 49/93 → 65/96 → 69/95 (103/107) | 43/80 → 53/85 → 77/89 (112/79) | 50/81 → 61/85 → 67/86 (45/65) |
| -|MMM | 16/68 → 47/85 → 61/92 (36/37) | 15/79 → 66/91 → 77/94 (62/86) | 22/79 → 66/91 → 77/94 (56/86) |
| tactician | 32/85 → 33/85 → 36/88 (621/686) | 47/85 → 43/86 → 47/89 (168/216) | 48/84 → 47/85 → 52/90 (64/175) |
| blademaster | 34/83 → 45/85 → 43/84 (442/431) | 37/79 → 45/81 → 41/84 (523/563) | 33/80 → 49/83 → 45/85 (211/463) |
| pilgrim | 33/52 → 43/56 → 17/65 (23/40) | -/- → -/- → -/- (0/0) | -/- → -/- → -/- (0/0) |
| hexer | 43/80 → 43/77 → 46/85 (82/108) | 53/86 → 57/82 → 53/88 (163/184) | 48/87 → 53/85 → 54/89 (48/140) |
| bard | 73/93 → 52/90 → 42/85 (114/171) | 46/83 → 42/66 → 43/83 (44/53) | 55/83 → 55/73 → 33/86 (9/42) |
| windhunter | 68/96 → 63/94 → 65/95 (702/929) | 55/94 → 54/94 → 61/95 (628/671) | 52/94 → 54/95 → 63/96 (230/563) |
| demonhunter | 85/96 → 85/97 → 48/97 (25/34) | -/- → -/- → -/- (0/0) | -/- → -/- → -/- (0/0) |
| saintknight | 42/93 → 50/94 → 47/90 (306/427) | 49/92 → 54/91 → 48/87 (389/481) | 51/92 → 63/93 → 61/91 (110/345) |
| shadowlord | 45/87 → 47/83 → 49/86 (1024/1080) | 49/88 → 45/81 → 48/88 (824/921) | 44/89 → 53/85 → 50/90 (236/699) |
| pirateking | 51/86 → 47/82 → 48/87 (806/881) | 42/85 → 42/82 → 44/86 (632/670) | 43/87 → 46/87 → 43/89 (171/509) |
| liberator | 50/85 → 40/82 → 45/87 (239/346) | 33/85 → 27/78 → 40/88 (268/310) | 26/85 → 32/80 → 39/89 (98/272) |
| shadowqueen | 43/84 → 38/80 → 42/85 (178/238) | 44/87 → 48/82 → 41/84 (222/277) | 39/88 → 53/87 → 51/89 (65/202) |
| beastmaster | 49/93 → 40/88 → 35/88 (160/185) | 35/84 → 37/81 → 42/89 (270/292) | 42/84 → 43/84 → 47/91 (105/247) |
| khan | 59/95 → 46/91 → 40/90 (227/381) | 61/93 → 58/92 → 58/92 (274/325) | 58/93 → 54/92 → 62/95 (65/238) |
| ironwall | 42/85 → 44/83 → 40/83 (440/484) | 41/86 → 43/84 → 41/83 (858/951) | 38/87 → 47/87 → 47/87 (271/732) |
| elfwarden | 60/94 → 58/95 → 58/95 (247/322) | 51/92 → 54/90 → 58/94 (351/470) | 49/92 → 58/92 → 63/95 (129/386) |
| boss frost | 85/81 → 76/86 → 71/86 (80/51) | 65/91 → 57/92 → 57/92 (76/38) | 75/88 → 75/88 → 75/88 (12/26) |
| boss mist | 38/66 → 37/82 → 40/88 (121/43) | 31/70 → 32/77 → 35/84 (144/43) | 44/63 → 54/70 → 47/83 (30/24) |
| boss oasis | 76/92 → 72/96 → 69/97 (93/31) | 64/86 → 47/91 → 47/91 (135/57) | 65/85 → 56/90 → 59/89 (17/28) |
| boss silverwood | 44/74 → 40/74 → 39/81 (217/52) | 51/74 → 41/82 → 41/87 (250/39) | 49/72 → 48/80 → 45/85 (42/20) |
| boss wheat | 78/93 → 65/93 → 67/96 (46/26) | 65/85 → 61/86 → 59/88 (71/32) | 58/79 → 67/81 → 65/83 (17/24) |
| boss >=우세 | 80.2 → 86.3 → 88.9 (216) | 81.4 → 86.2 → 89.1 (221) | 80.0 → 83.6 → 87.3 (134) |

##### Offline, human bot

| slice | fit: C21 offers | re-forecast: new-seed offers | re-forecast: new-seed sent |
|---|---|---|---|
| all | 59/94 → 51/92 → 47/93 (2556/6360) | 59/94 → 51/91 → 46/91 (2736/6366) | 56/93 → 51/91 → 53/92 (526/1410) |
| 1 co. | 59/94 → 51/92 → 47/93 (2556/6360) | 59/94 → 51/91 → 46/91 (2736/6366) | 56/93 → 51/91 → 53/92 (526/1410) |
| capStory | 67/99 → 52/98 → 48/92 (82/329) | 61/98 → 44/93 → 38/92 (64/224) | 55/98 → 35/97 → 38/89 (21/57) |
| campaign | 46/84 → 44/83 → 47/90 (207/284) | 42/85 → 40/85 → 40/90 (240/267) | 45/87 → 46/86 → 54/92 (63/83) |
| (0, 30] | 45/92 → 43/90 → 39/90 (160/458) | 50/88 → 50/87 → 46/88 (186/467) | 59/93 → 61/92 → 69/93 (51/140) |
| (30, 60] | 49/92 → 50/89 → 47/89 (198/538) | 51/93 → 47/90 → 47/90 (189/463) | 51/92 → 41/91 → 55/89 (42/91) |
| (60, 120] | 53/93 → 48/90 → 47/91 (444/1184) | 53/91 → 47/89 → 44/89 (501/1110) | 50/87 → 46/85 → 48/87 (81/207) |
| (120, 240] | 59/94 → 56/91 → 46/94 (777/1856) | 56/94 → 52/92 → 44/92 (787/1890) | 55/92 → 55/90 → 53/92 (167/443) |
| (240, 365] | 66/97 → 50/94 → 50/94 (977/2324) | 67/97 → 54/93 → 49/93 (1073/2436) | 61/96 → 51/93 → 51/94 (185/529) |
| foe heal >= 0.4 of our dmg | 9/59 → 1/53 → 38/86 (150/155) | 8/58 → 5/50 → 40/82 (84/102) | 5/56 → 8/50 → 47/79 (43/39) |
| foe ranged share >= 0.35 | 44/83 → 36/79 → 45/90 (534/750) | 45/85 → 34/80 → 46/92 (580/838) | 54/88 → 42/87 → 60/91 (156/224) |
| support share >= 0.3 | 25/69 → 41/100 → 51/88 (55/8) | 27/92 → 45/91 → 44/81 (93/21) | 18/100 → 43/100 → 41/100 (17/6) |
| 1 head | 55/88 → 61/85 → 58/77 (77/119) | 56/94 → 62/88 → 46/82 (63/145) | 56/89 → 58/87 → 53/85 (19/66) |
| 2 heads | 59/91 → 61/89 → 52/87 (176/294) | 59/92 → 63/89 → 45/84 (174/270) | 58/92 → 55/90 → 48/84 (40/108) |
| no captain | 47/87 → 50/86 → 42/81 (202/333) | 45/90 → 47/88 → 35/84 (153/285) | 48/89 → 48/89 → 42/85 (50/147) |
| M|HMR | 62/95 → 50/92 → 47/94 (1170/3041) | 62/94 → 53/89 → 49/92 (902/2016) | 54/91 → 48/88 → 53/92 (169/390) |
| R|HMR | 59/94 → 46/90 → 42/92 (407/1131) | 58/95 → 48/93 → 45/92 (1093/2727) | 59/93 → 52/92 → 53/95 (221/561) |
| -|R | 59/89 → 82/82 → 76/83 (21/12) | 80/100 → 80/91 → 42/88 (12/25) | 89/100 → 100/94 → 100/95 (3/19) |
| -|MR | 57/86 → 50/84 → 58/88 (12/17) | 64/87 → 69/82 → 60/90 (15/21) | 73/91 → 67/92 → 71/92 (7/12) |
| tactician | 68/97 → 50/92 → 47/94 (192/562) | 77/98 → 61/96 → 58/96 (466/1410) | 72/96 → 62/94 → 66/98 (83/285) |
| blademaster | 60/95 → 53/92 → 51/94 (456/1097) | 61/93 → 56/89 → 48/92 (430/1020) | 52/91 → 49/87 → 52/91 (73/194) |
| fieldmedic | 57/97 → 61/97 → 52/95 (285/905) | 63/96 → 66/96 → 61/93 (94/301) | 68/92 → 67/92 → 67/89 (12/71) |
| veteran | 71/97 → 55/93 → 52/96 (321/832) | 60/93 → 47/86 → 49/90 (156/366) | 47/86 → 41/77 → 47/88 (38/69) |
| huntress | 53/90 → 47/87 → 46/88 (269/624) | 49/94 → 44/91 → 36/90 (391/757) | 49/93 → 50/91 → 45/93 (75/172) |
| ironwall | 65/95 → 47/90 → 51/95 (228/520) | -/- → -/- → -/- (0/0) | -/- → -/- → -/- (0/0) |
| lancer | 57/96 → 42/94 → 47/95 (168/423) | 62/94 → 53/91 → 51/92 (494/1017) | 62/94 → 54/93 → 57/95 (89/216) |
| hedgemage | 43/92 → 39/90 → 27/89 (104/241) | 47/91 → 43/90 → 39/87 (552/1210) | 50/92 → 45/91 → 52/90 (106/256) |
| fixer | 55/92 → 51/90 → 42/92 (331/823) | -/- → -/- → -/- (0/0) | -/- → -/- → -/- (0/0) |
| boss frost | 100/100 → -/100 → -/100 (0/10) | 100/100 → -/100 → -/100 (0/16) | -/100 → -/100 → -/100 (0/10) |
| boss mist | 100/86 → 100/88 → 100/89 (2/9) | 0/100 → 0/100 → 0/100 (4/6) | -/- → -/100 → -/100 (0/3) |
| boss oasis | -/100 → -/100 → -/100 (0/9) | -/100 → -/100 → -/100 (0/9) | -/100 → -/100 → -/100 (0/6) |
| boss silverwood | 100/94 → 93/95 → 92/96 (13/24) | 57/91 → 57/89 → 58/87 (19/39) | 62/92 → 62/92 → 57/92 (7/13) |
| boss wheat | 80/100 → 83/100 → 80/100 (5/19) | 80/100 → 80/100 → 88/100 (8/24) | 100/100 → 100/100 → 100/100 (3/16) |
| boss >=우세 | 98.8 → 98.8 → 98.8 (173) | 98.3 → 97.8 → 97.3 (184) | 98.9 → 98.9 → 98.9 (90) |

Live: seeds 10101 × 12 × 365 for each bot, run three times (base `ce63492`; base + v3 `stats.js`; base + this `stats.js`). The bots
choose by each forecast's own words, so the battles differ between columns.

##### Live, sensible bot

| slice | live 10101: sent | live 10101: offers |
|---|---|---|
| all | 48/89 → 47/87 → 48/89 (841/2770) | 47/88 → 47/86 → 50/88 (2629/2916) |
| 1 co. | 49/89 → 47/87 → 47/89 (815/2704) | 48/88 → 46/86 → 50/88 (2552/2850) |
| 2 co. | 55/95 → 70/89 → 58/96 (12/25) | 52/95 → 73/89 → 58/96 (36/25) |
| 3 co. | 9/85 → 32/91 → 43/88 (14/41) | 31/85 → 43/91 → 54/88 (41/41) |
| story | 31/76 → 40/83 → 49/75 (57/93) | 31/70 → 42/82 → 53/77 (302/188) |
| capStory | 50/81 → 52/88 → 62/81 (13/63) | 50/71 → 54/89 → 62/79 (65/90) |
| campaign | 29/90 → 49/90 → 50/91 (26/64) | 36/90 → 55/90 → 56/91 (77/64) |
| (0, 30] | 57/86 → 45/91 → 61/92 (33/145) | 50/86 → 52/91 → 56/92 (93/145) |
| (30, 60] | 46/90 → 59/87 → 48/87 (50/154) | 45/91 → 54/87 → 51/87 (179/156) |
| (60, 120] | 45/85 → 51/87 → 48/86 (113/314) | 51/80 → 53/87 → 52/85 (400/354) |
| (120, 240] | 48/88 → 48/86 → 47/90 (288/1002) | 42/86 → 46/86 → 51/89 (935/1059) |
| (240, 365] | 49/92 → 42/86 → 46/89 (357/1155) | 52/92 → 43/86 → 48/88 (1022/1202) |
| foe heal >= 0.4 of our dmg | 7/63 → 16/54 → 44/79 (16/19) | 11/54 → 15/64 → 33/83 (51/23) |
| foe ranged share >= 0.35 | 33/70 → 33/73 → 41/85 (153/414) | 34/67 → 35/72 → 47/83 (571/489) |
| support share >= 0.3 | 34/75 → 55/88 → 52/83 (50/23) | 36/75 → 62/88 → 54/83 (127/23) |
| 1 head | 50/100 → 100/83 → 0/100 (1/6) | 60/100 → 100/83 → 67/100 (3/6) |
| 2 heads | 89/94 → 50/84 → 80/96 (5/25) | 85/94 → 64/84 → 71/96 (17/26) |
| no captain | 47/89 → 48/85 → 51/86 (158/471) | 48/88 → 49/85 → 52/85 (444/505) |
| M|MRR | 56/92 → 42/78 → 36/88 (96/323) | 55/90 → 33/78 → 40/88 (354/350) |
| M|HMR | 57/91 → 37/78 → 53/85 (85/238) | 45/89 → 37/78 → 52/85 (287/240) |
| R|MRR | 94/100 → 65/93 → 56/99 (16/126) | 88/100 → 63/93 → 73/99 (70/126) |
| -|HMM | 17/74 → 57/82 → 75/87 (4/23) | 24/74 → 58/82 → 64/91 (11/33) |
| -|MMM | 11/72 → 40/77 → 33/100 (6/10) | 8/66 → 44/77 → 44/100 (9/10) |
| tactician | 30/84 → 33/78 → 57/92 (61/199) | 39/84 → 35/78 → 52/93 (176/204) |
| blademaster | 31/84 → 38/82 → 36/78 (76/213) | 32/84 → 37/83 → 37/78 (220/229) |
| hexer | 47/95 → 46/89 → 50/92 (18/36) | 33/95 → 36/88 → 52/92 (56/37) |
| windhunter | 36/96 → 62/95 → 60/95 (92/397) | 41/97 → 64/95 → 65/94 (321/400) |
| saintknight | 42/85 → 50/88 → 32/89 (59/239) | 32/79 → 41/88 → 41/88 (210/274) |
| shadowlord | 56/91 → 56/88 → 50/87 (156/404) | 53/89 → 49/88 → 48/87 (526/409) |
| pirateking | 53/90 → 45/83 → 36/84 (42/171) | 52/90 → 42/81 → 39/84 (146/180) |
| liberator | 71/95 → 32/77 → 54/96 (28/127) | 63/95 → 33/78 → 58/96 (72/133) |
| shadowqueen | 70/92 → 67/89 → 48/93 (29/128) | 66/91 → 70/88 → 56/93 (103/141) |
| beastmaster | 14/59 → 45/82 → 48/91 (21/81) | 5/68 → 31/80 → 58/90 (78/89) |
| khan | 75/94 → 29/92 → 43/100 (14/38) | 67/93 → 45/92 → 58/100 (45/38) |
| ironwall | 40/88 → 34/91 → 44/90 (39/124) | 41/84 → 36/91 → 47/90 (104/126) |
| elfwarden | 68/97 → 52/90 → 32/90 (22/77) | 70/97 → 54/90 → 41/88 (51/86) |
| boss frost | 100/100 → 67/91 → 33/89 (6/9) | 88/100 → 50/94 → 50/89 (32/9) |
| boss mist | 33/62 → 67/86 → 25/90 (8/10) | 39/77 → 45/86 → 44/87 (32/15) |
| boss oasis | 50/83 → 100/100 → 33/100 (3/11) | 57/87 → 86/100 → 50/100 (28/11) |
| boss silverwood | 40/73 → 33/64 → 43/86 (14/7) | 52/80 → 44/67 → 45/86 (66/7) |
| boss wheat | 50/88 → 25/89 → 100/100 (1/7) | 38/82 → 44/89 → 14/100 (7/7) |
| boss >=우세 | 83.9 → 85.7 → 94.1 (51) | 85.9 → 84.4 → 92.9 (56) |

##### Live, human bot

| slice | live 10101: sent | live 10101: offers |
|---|---|---|
| all | 56/91 → 44/89 → 49/92 (354/749) | 60/94 → 51/92 → 48/93 (1427/3501) |
| 1 co. | 56/91 → 44/89 → 49/92 (354/749) | 60/94 → 51/92 → 48/93 (1427/3501) |
| capStory | 61/100 → 56/98 → 0/85 (3/27) | 75/100 → 58/97 → 44/92 (27/116) |
| campaign | 57/81 → 44/83 → 45/91 (64/55) | 47/83 → 43/81 → 41/91 (150/108) |
| (0, 30] | 50/92 → 71/96 → 59/89 (32/79) | 48/87 → 58/92 → 65/93 (103/256) |
| (30, 60] | 62/92 → 37/88 → 52/89 (29/45) | 61/91 → 46/89 → 37/91 (89/224) |
| (60, 120] | 52/84 → 34/84 → 44/94 (55/106) | 59/92 → 45/90 → 42/92 (252/611) |
| (120, 240] | 54/90 → 52/88 → 46/92 (129/207) | 54/94 → 51/90 → 45/94 (471/873) |
| (240, 365] | 60/94 → 38/91 → 51/92 (109/312) | 67/96 → 54/94 → 51/93 (512/1537) |
| foe heal >= 0.4 of our dmg | 11/59 → 8/42 → 60/88 (15/26) | 9/61 → 3/41 → 44/88 (48/67) |
| foe ranged share >= 0.35 | 45/83 → 36/82 → 53/94 (77/118) | 43/81 → 37/79 → 45/90 (280/442) |
| support share >= 0.3 | 50/100 → 23/100 → 50/100 (12/2) | 31/87 → 47/83 → 57/94 (37/16) |
| 1 head | 59/81 → 47/82 → 45/81 (20/16) | 58/86 → 44/83 → 43/82 (30/28) |
| 2 heads | 65/93 → 62/83 → 24/82 (29/38) | 67/92 → 66/90 → 37/88 (65/118) |
| no captain | 59/87 → 47/85 → 34/85 (47/55) | 52/87 → 46/86 → 42/85 (93/101) |
| M|HMR | 46/91 → 40/88 → 52/91 (151/336) | 56/93 → 47/91 → 46/92 (718/1659) |
| R|HMR | 65/90 → 49/89 → 57/97 (81/176) | 67/96 → 55/93 → 57/95 (306/889) |
| -|R | 67/100 → 20/85 → 55/100 (11/6) | 76/100 → 38/81 → 50/90 (18/10) |
| -|MR | 57/100 → 71/100 → 33/80 (3/5) | 62/100 → 53/100 → 50/75 (4/8) |
| tactician | 70/94 → 48/92 → 59/98 (75/182) | 73/97 → 59/94 → 59/97 (304/974) |
| blademaster | 41/90 → 47/88 → 56/94 (48/122) | 50/92 → 51/89 → 47/93 (240/631) |
| fieldmedic | 70/98 → 47/92 → 36/87 (28/62) | 67/98 → 66/94 → 44/93 (99/295) |
| lancer | 55/91 → 41/93 → 44/90 (52/104) | 65/95 → 43/94 → 40/95 (236/489) |
| hedgemage | 55/80 → 50/84 → 41/90 (27/58) | 46/89 → 49/89 → 44/87 (106/253) |
| fixer | 47/91 → 38/88 → 55/89 (77/166) | 56/91 → 47/90 → 48/89 (349/758) |
| boss frost | -/100 → 0/100 → -/100 (0/1) | -/100 → 0/100 → -/100 (0/1) |
| boss mist | 100/0 → 100/100 → -/100 (0/2) | 50/50 → 100/100 → 100/100 (1/2) |
| boss oasis | -/- → 0/100 → -/100 (0/5) | -/100 → 33/96 → -/100 (0/22) |
| boss silverwood | 100/100 → 0/100 → 100/83 (3/6) | 100/100 → 0/100 → 100/92 (3/13) |
| boss wheat | -/100 → -/100 → -/100 (0/7) | 100/100 → -/100 → 100/100 (1/12) |
| boss >=우세 | 97.7 → 100.0 → 97.6 (42) | 98.6 → 98.9 → 98.9 (94) |

#### Economy (many-company bot, `SIM_SEED=9301 SIM_RESOLVE=battle node tools/sim/bot.js 12 365`, same seeds for all three)

| | old (base) | v3 | v3.1 |
|---|---|---|---|
| games reaching S / day | 12 / 101 | 12 / 99 | 12 / 102 |
| bankruptcies, deaths, game-overs | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| gold day 240 / 365 | 29.9k / 69.6k | 19.2k / 60.2k | 23.2k / 65.4k |
| completed / failed | 418 / 67 | 423 / 67 | 403 / 63 |
| sent battles won at 백중 / 우세 / 압도 | 47.4 / 90.1 / 99.7% | 50.5 / 88.5 / 99.6% | 46.9 / 88.0 / 100% |
| wins: boss / campaign / capStory / story | 64.5 / 77.1 / 81.3 / 66.8% | 75.0 / 84.9 / 82.6 / 75.5% | 69.0 / 88.8 / 89.3 / 74.2% |

Gold and S day are inside the seed noise measured in "One-company polish": per-set day-365 gold swings of −48% to +216% with
the same code (9201 alone went 34k → 107k). Half of the v3 gold drop the review found came back. Neither direction is a robust
effect of the forecast.

#### Gates (v3.1)

- Roll md5, `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum`, with and without `SIM_SHADOW=1`:
  `11cadc0cceafa5e4262773fdadf780f9` on the base `ce63492` plus this `js/stats.js`. The current working tree gives
  `f1712f75dd50877f69a65caf254be083`, as before this change (upstream edits moved it, see above).
- `node tools/sim/battle.js 100`: miss 0 / soft 0 for all four outcomes, on the base + this file and on the current tree.
- `node tools/sim/shadow.js 6 365 --resolve battle --check`: 2,762 battles, every invariant 0. Run on the base + this file and on the
  current working tree, which includes other sessions' uncommitted edits.
- `--set`: accepted `BM_CAL_HEAL.CAP=0.8`, `BM_CAL_HEAL.boss=1`, `BM_CAL_FOE.ranged2=1`, `BM_CAL_ROLE.MIN_N=2`,
  `BM_CAL_ROLE.ranged2=1`. Refused `BM_CAL_ROLE.melee` (the old key is gone), `BM_CAL_FOE.melee` and `'BM_CAL_HEAL=[1,2]'`.
  No other file reads `BM_CAL_ROLE` or `roleCal`.
- Forecast cost (day-150 game, 200 cold `capability()` calls, idle machine, 3 runs each): `capability()` takes 5.3-5.9 ms on the
  base, 5.3-5.4 ms with v3 and 4.9-5.0 ms with v3.1. One `forecast()` takes 47-52 µs on all three. The extra k = 1 `sideOf` pair is
  shared with `killTime`, so nothing is computed twice.
- The offline model reproduces the JS forecast to 0.001 (R rounding) on 47,792 rows.

#### Open issues (v3.1)

- **Captain-less parties: opposite signs in the two bots.**
  - Human bot, 1-3 heads with no captain: ln R −0.02 to −0.05, optimistic. Re-forecast offers 35% / 84%; live 42% / 85% (n 93/101).
  - Sensible bot, captain-less trios (hired companies, `-|HMM`, `-|MMM`): +0.03, pessimistic.
  - In the human bot these parties are what remains while the captain recovers; in the sensible bot they are full hired
    companies. No term in the specs separates them yet, so this is left.
- **Human 2-head parties** read optimistic: 45% / 84% re-forecast, 37% / 88% live (n 65/118). Mostly the captain-less case above.
- **Sensible blademaster** reads 41-43% / 84% offline and 37% / 78% live (n 220/229). Pirateking reads 39-44% / 84-86%. Both are
  melee captains whose companies have a cleric and melee members.
- **Story contracts, live:** 우세 77% (n 188) on 10101, against 83% re-forecast. Better than old (70%), still under 85%.
- **Two companies** read slightly pessimistic at 우세 (94-96%, small n). That is noise-level and gets no factor.
- **Bosses:**
  - Many-company bot at 우세 or better: 87-89% offline, 93-94% live (n about 50).
  - Per key, mist and silverwood are still the weakest at 백중 (35-45%).
  - The human bot's 97-99% is unchanged. Its boss battles are at 압도 or high 우세; its 우세 cells have under 30 rows per boss.
- **Overall level:** the human bot is now slightly optimistic at 백중 (46-49%, against v3 51%). The sensible bot is at 47-50%.
- **Too few battles to judge:** pilgrim, demonhunter and bard (under 60 rows per word on the new seeds).

#### Commands and scratch (v3.1)

```
# scratch (not in the repo), under the session scratchpad v4/:
#   coll.js (collector with spec, TREE=… OUT=…), feat3.js (per-unit dps/ehp/hps, enemy roles), m4.py + fx.py + fin.py (exact offline
#   model, fits f1-f6.py, boss grid fb4.py), mktabs.py / mklive.py (tables above), rf.js (JS forecast for the exactness check),
#   bench.js, live.sh (10101 × 3 trees), econ.sh (9301 × 3 trees)
TREE=<base> OUT=oosb node coll.js --strategy sensible --seeds 8101 --jobs 3      # new re-forecast seeds; also human 8101
TREE=<tree> OUT=live_<tree> node coll.js --strategy sensible --seeds 10101 --jobs 4   # live; also human
```


## Engine VER 2 — melee no longer carries ranged units (2026-11-28)

**History note:** the VER 1→2 engine change (`HOLD` after an attack, `backOff()` for ranged units, `BACK_ROOM` near edges) landed by accident inside commit `d16be70`, whose message says "Merge C29 (display only)". The lead staged `js/battle.js` while the push-fix workflow was writing it. Anyone bisecting a win-rate or calibration shift: the movement change is in `d16be70`, not a later commit. Old battle-mode reports with VER 1 no longer replay (they open the written report directly; C30 `e3e10f3` removed the TypeError on that path).

Measured (push-fix workflow, 6 seeds × 200 days of judged battles): edge episodes 440 → 0, "carried" ticks 14.9% → 1.4%, backwards idle-glide ticks 130,711 → 1,509; roll md5 unchanged (roll never reads the engine for state), battle.js 100 miss 0, shadow --check 0. Paired win rates: all 백중 50.9→49.2%, 우세 88.0→88.1%. **But bosses:** 백중 50.0→38.7% (n 62), 우세 88.5→85.4% (n 96) → boss calibration and the retreat look are being reworked (round 2).

### Round 2 — one retreat run instead of 6 px hops; boss bands re-measured (2026-11-28)

**Owner review of round 1:**
- The retreat started on the impact tick. The ranged unit flashed from the hit inside the attacker's swing pose and came out about 6 px further back; the attacker then stepped 6 px and hit again. It read as being knocked back step by step.
- Facing flipped twice per retreat (one mage: about 30 flips in 11 s).

**Change (`js/battle.js`, still `VER = 2`):** a ranged unit's retreat is now one run (`u.run` = start time, `u.runDir`, `u.runNext`).
- **Start.** A run starts only when the hit reaction has played in place (`RUN_DELAY` 0.2 s ≥ the 0.18 s flash and hit-kick).
  - Every enemy melee that targets the unit from close by must be in recovery: `RUN_DELAY` has passed since its last attack and its next attack is more than `RUN_SAFE` 0.3 s away. A stunned melee also counts.
  - The running body leaves melee reach within about 0.1 s, so it is not hit while running (115 hits-while-running in 6,777 runs, mostly arrows).
  - The run direction points away from all near melee units and the target, then bends halfway toward the allies. When melee units stand on both sides, the vectors cancel and the unit does not run.
  - A run does not start when a body stands `RUN_LOOK` 10 px ahead (`clearAhead`).
- **Duration.** The direction is fixed for the whole run, so the unit no longer turns mid-run when its target changes.
  - Minimum: `RUN_MIN` 0.55 s. After that, the run stops once the gap beyond the chaser's reach reaches `RUN_GAP_OK` 16 px, or the unit is ready to shoot.
  - Maximum: `RUN_MAX` 0.8 s.
  - The run also stops when the unit is blocked or makes less than 30% of a step's progress in the run direction. This prevents a glide against facing.
  - It also stops at `BACK_ROOM` from an edge, when caught by a moving chaser, or when stunned. Using a special skill ends the run.
- **While running.** The unit does not shoot; it turns back once at the end and shoots. The next run waits `RUN_REST` 2.5 s.
- **Chasers.** An enemy melee within `RUN_NEAR` 30 px of a running target stands until the run ends, then chases. The chaser never moves together with its target. If its attack comes ready while the target is still in reach, it swings.
- **Retargeting.** A ranged unit now keeps its current target unless another target scores `RETARGET_KEEP` 12 points closer on the target score. Before this, a ranged unit standing between enemies on both sides turned left and right every 0.4–0.7 s.
- **Unchanged.** Movement speed, `HOLD`, `BACK_ROOM`, and separation.
- **Replays.** `VER` is not bumped. The replay already re-runs the spec and compares `ver` and `hash`, so a report written by round 1 (also `VER 2`) gets a hash mismatch. It opens the written report directly instead of a replay, exactly as a `VER` bump would make it do. Round-1 reports therefore no longer replay.

**Probe:** 6 seeds × 200 days of judged battles, our ranged units in contact. Columns are VER 1 base (`d16be70^`) / round 1 (HEAD) / round 2.

| | VER 1 | round 1 | round 2 |
|---|---|---|---|
| edge episodes | 440 | 0 | 0 |
| carried ticks | 14.88% | 1.40% | 0.55% |
| backwards glide ticks | 130,711 | 1,509 | 204 |
| retreat episodes per contact-minute | 47.1 (backpedal) | 56.9 | 14.2 |
| retreat length, median (p10–p90) | 1.8 px (0.6–18.5) | 3.1 px (1.1–10.8) | 13.7 px (6.3–16.8) |
| retreat time, median | 0.1 s | 0.15 s | 0.55 s |
| retreats under 8 px | 73% | 81% | 12% |
| start after the chaser's attack, median (p10) | – | 0 s (0) | 0.35 s (0.15) |
| facing flips per contact-second | 0.08 | 0.58 | 0.15 |

The probe battles differ in number (1,492 / 1,552 / 1,366) because each engine changes the bot's trajectory.

Gates:
- Roll md5 `f1712f75dd50877f69a65caf254be083`, with and without `SIM_SHADOW=1`.
- `node tools/sim/battle.js 100`: miss 0, soft 0.
- `node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 3`: all 0 (2,682 battles).

**Bands, paired:** the same specs through all three engines; win % listed as VER 1 / round 1 / round 2.
- Specs came from the battle-mode bot over 80 seeds × 365 days (101–180).
  - Bosses: every distinct boss offer, plus every other free company mustered alone against the same boss. Rows with R < 0.55 were dropped; they cannot reach 열세 under any grid point.
  - Non-boss: seeds 101–112 only. All sent battles, plus 12% of the distinct offers.

| population | 열세 | 백중 | 우세 | 압도 |
|---|---|---|---|---|
| boss offers | 16.4/15.2/18.0 (1356) | 47.5/50.7/**50.0** (970) | 91.5/89.5/**88.8** (447) | 100 (66) |
| boss sent | – | 43.2/46.2/**45.7** (199) | 93.3/91.3/**92.0** (300) | 100 (45) |
| non-boss offers | 12.9/13.6/17.8 (286) | 50.7/55.8/54.8 (217) | 91.1/89.1/91.5 (293) | 100/99.6/100 (247) |
| non-boss sent | – | 50.9/52.1/**50.6** (727) | 89.5/89.3/**89.8** (2638) | 99.8/100/100 (2215) |

**Round 1's boss drop was mostly sample noise.**
- On round 1's own boss specs (61 / 91 sent battles from `push/fix/specs_*`), 백중 reads 49.2 / 39.3 / 47.5 and 우세 89.0 / 85.7 / 85.7.
- On the 15× larger set above, round 1 itself reads 50.7 / 89.5.

**Boss refit:**
- **Grid.** `BM_CAL_SPECIAL.boss` 0.70–0.90, `BM_CAL_BOSS.sure` 0.45–0.8, `arch` 1 / 1.5 / 2, `BM_CAL_HEAL.boss` 1 / 1.18. Fitted on round-2 winners of the boss offers.
- **Score.** Distance to 백중 50% / 우세 87.5%, with n ≥ 150 per band.
- **Result.**
  - Best: sure 0.7 → offers 50.2 / 87.7 (823 / 472), sent 47.2 / 91.1.
  - sure 0.65 → offers 50.2 / 87.9, sent 46.2 / 91.4; log-loss 0.2400 against 0.2404 now.
  - The current values give 50.0 / 88.8 and 45.7 / 92.0.
- **Decision.** All of these are inside the target and within one standard error of each other (about 1.7 pp at 백중, 1.5 pp at 우세). **The boss knobs stay as they are** (`BM_CAL_BOSS` arch 1.5, sure 0.6; `SPECIAL.boss` 0.87; `HEAL.boss` 1.18), and the tab digest is unchanged.
- **Still open.** Sent boss 우세 is 92.0% (n 300), slightly above 90%. VER 1 read 93.3% on the same specs, so this is not new.

**Owner GIFs** (game's own `Battle.play` in Chromium, deviceScaleFactor 1, upscaled ×2, virtual 25 fps clock so the GIFs play at true speed):
- Location: the push-fix workflow's `push2/gif/` scratch folder.
- Cases: archer vs bandits, mage vs bandits, and a boss (모래 폭군 against an archer). Each has a 1× clip and a 4× full battle.
- Side-by-side crops of the same case in VER 1 / round 1 / round 2, as `sbs_*.gif` and `_strip.png`.

**Seen, not changed:** when a standing ranged unit overlaps an ally that dashed into it, and then takes one step, separation moves it out up to about 9 px in one tick. This predates VER 2; the largest one-tick separation in contact is 25 px in VER 1 and 31 px in round 1, against 24 px now. It is not part of the retreat.

### Round 3 (2026-11-28)
- A run is refused while the runner's own last hit is < `RUN_DELAY` old (`u.hitT`), while any enemy melee in reach (whatever its target) or a nearby melee special is about to strike, and (lead) while an incoming shot aimed at the runner will land within `RUN_DELAY`.
- `runStep()` lookahead: no run (and no turn) unless the first step really moves; a near-zero first tick cancels and restores facing; edge room checked 10 px ahead; no run while the unit's own special is about to be ready.
- Probe (same 1,366 battles, round 2 → round 3): carried ticks 0.55% → 0.31%; runs starting under the hit flash 54 → 0 (melee); zero-motion runs (<0.5 px) 65 → 0; facing flips per contact-second 0.150 → 0.120; runs < 8 px 801 → 244. Independent scan seeds 51–53 × 365 d (1,323 battles): runs starting on a hit tick 23 → 11 of 6,830, all 11 from a projectile in flight (0.16%), stand-offs 0.
- Paired bands vs round 2 within noise (pooled −0.48 pp, SE 0.31): boss offers 백중 50.3 / 우세 88.1, non-boss sent 48.7 / 89.9. Boss knobs unchanged.
- Gates: roll md5 f1712f75 (also SIM_SHADOW=1), battle.js 100 miss 0, shadow --check all 0. VER stays 2 (round-2 reports open their written result directly).
