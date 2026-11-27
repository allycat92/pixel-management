# Battle stats, stage 3: the battle decides, behind a switch

Date 2026-11-27. Base `e33267a` (C7 calibration adopted). Spec: `design.md`, amendments `verify_findings.md`,
owner decisions of 2026-11-27 in `README.md`. Stage 0-1 notes: `stage01_notes.md`.

This file describes the code after the **fix round** (same day): an adversarial verify found 7 findings, and every
one is either fixed or rejected with a reason in "Verify findings and what was done". The tables below are the
measurements of the fixed code; the first implementation's numbers are kept only where they are compared.

## The switch

`Game.RESOLVE` is `'roll'` (default) or `'battle'`.

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
| `BM_CAL_OWNLV` | ≤3 0.879, ≤6 0.928, ≤9 0.946, ≤12 1, ≤16 1.005, more 1.034 | 0.887, 0.944, 0.969, 0.99, 0.983, 0.977 | Refitted jointly: part of the old high-level step (1.034) was the ranged captains that late parties have more of. |

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
  missions out, no own company with an idle member, no free external company). `Game.skipToReturn()` (`js/game.js`) runs `nextDay`
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
- **Top-bar chip** 「유예 ~N일」 (`#grace-chip`, title explains) while the grace week is open and it matters (deferred pay, or gold below
  the next payday: `Game.graceShown()`). Hidden while a mission report is still unseen, so it does not give a defeat away during the
  battle replay.

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

### Results (evaluation seeds 1, 3101, 4101 — 3101 and 4101 untouched by any fit; 5001 for the starters)

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

Final rank S in all 36 games before and after; no bankruptcy, no darkness, deaths 0 / 0. By captain style (seed 3101, sent): melee
백중 / 우세 34 / 79% → 44 / 86%, ranged 71 / 96% → 59 / 92%, ranged + rally 66 / 94% → 39 / 86% (n 85). By day (seed 3101, sent): days
61-120 56 / 87% → 41 / 83%, days 241-365 45 / 88% → 49 / 91%.

### Checks

- Roll: `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` = `11cadc0cceafa5e4262773fdadf780f9` with and without `SIM_SHADOW=1`;
  12 × 365 `ffee253e5364a3e6f882f9aed77254b0` before and after.
- `node tools/sim/battle.js 100`: miss 0 / soft 0.
- `node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4`: 2,943 battles, 8,624 alternative parties, every invariant 0.
- `--set BM_CAL_LEAD.melee=1`, `--set 'BM_CAL_LEAD={…}'`, `--set 'BM_CAL_HEADS=[…]'` accepted; `BM_CAL_LEAD.foo` refused.
- Browser (400 × 800, `?resolve=battle`): the skip button appears when the only company is out and jumps to the return day's report;
  the wait hint shows; the grace popup and the 「유예 ~N일」 chip render; no console error, no horizontal overflow.

### Open issues

- **Days 61-120 for the many-company bot lean optimistic after the refit** (seed 3101 sent: 백중 41%, 우세 83%; all sent battles on
  days 61-120 win 83% against 88% before), while late days moved the other way (241-365 86% against 82%). The one-company bot on the
  same days reads 50 / 89%. In the offline fit the mid-level step (≤ 9) carried this: `BM_CAL_OWNLV` ≤ 9 between 0.946 and 0.969 is the
  knob if the owner prefers the many-company mid-game safe. S moved from day 92.7 to 98.3 (decision 5 target 90-110).
- **The one-company early game still reads a little safe** (probe 백중 56-61%, 우세 91-95% on days 1-120). A day term would fix it but
  the per-starter spread was the larger error and is gone (바렌 백중 32 → 49% sent).
- **Boss contracts** stay below target at 우세 (74% pooled, n 243); the ranged captains of strong late companies read easier now.
  Same open issue as stage 3/4 (boss-scale enemies need their own term).
- **Captains recruited** 7.2 → 6.3 per game (the gamble conditions read the word at dispatch); stage 4 measured 6.35, so before may
  have been the high one.
- **Ranged + rally in the many-company bot** over-corrects (백중 39%, n 85) while the one-company tactician is right (53-55%):
  `rally` is a compromise between the two populations.

### Commands

```
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4        # also SIM_SEED=3101, 4101; before = SIM_ROOT of ea5304a
node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4
SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum                             # 11cadc0cceafa5e4262773fdadf780f9
# scratch (not in the repo): one.js (one-company bot: human / human2 / sens1, --probe, --starter), collect2.js (many-company bot,
#   every looked-at offer fought headless), fit2.js (joint target matching, PARAM=1), ana.js / stt.js (tables), bosscheck.js
```
