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
  instead of ~132, day 60 and 121+ rewards unchanged.
- The reckless strategy (takes every offer, including 무모) can now go broke (1 of 12) or fall to darkness; decide
  whether 무모 failures should cost less or the board should show fewer of them.
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
keep day-365 gold from ballooning. Decision 6: 무모 offers unchanged (nothing here touches the board, the words,
calibration, casualties or the loss cushion).

### The lever

`js/contract.js` `makeContract`: in battle mode a contract **created** on day d gets

```
gold reward × (1 + BM_MID_PAY × midBoost(d))      reputation (명성) × (1 + BM_MID_REP × midBoost(d))
midBoost(d) = 0 up to day 59, rises linearly to 1 on day 72, 1 until day 110, falls linearly to 0 on day 121
```

`midBoost` is `Game.midBoost(day)` (`BM_MID_DAYS` = the four corners of the trapezoid). The factor goes into the
contract's own `reward` and `rep` when it is made, before the special multipliers (story ×1.3, campaign ×1.8 / rep ×2,
boss ×4, relief ×1.5), so the contract card shows exactly what is paid, a posted contract never changes its price
afterwards, and the loss pay (a share of `reward`) and the rep lost on a failure (30% / 60% of `rep`) follow the same
numbers. Values on day 60 / 65 / 72-110 / 115 / 120 / 121: 0.08 / 0.46 / 1 / 0.55 / 0.09 / 0. Roll mode never calls it
(`s.resolve === 'battle'` first).

Why this lever:
- **Rank is reputation only** (`RANKS` in `js/data.js`: S at 3,200 rep). Gold does not move S: gold ×1.5 alone on days
  60-120 left S at 140 (141) and raised day-365 gold by 44% (seeds 1-12). So the S target needs a rep term; gold gets a
  small one so the mid-game purse is a bit less lean, as the decision asks ("rewards").
- Both numbers are printed on the card ("보상 N", "명성 +N"), so the player sees what the contract gives; there is no
  hidden multiplier on payout. A day ramp, not a rank ramp: a rank ramp would cut pay at the moment of promotion to S
  (a punishment for success) and would move with the player, while the owner's window is in days.
- Trapezoid, not a step: 13 days in (59 → 72), 11 days out (110 → 121), so no cliff at day 60 or 120. The hold runs
  to day 110 because S lands around day 100: with the hold ending on day 105 (`[59,72,105,121]`) S came on day 112.

### Constants (all in `Stats.KN`, settable with `--set` in `bot.js` and `shadow.js`)

| Constant | Value | Reason |
|---|---|---|
| `BM_MID_PAY` | 0.25 (gold ×1.25 at the peak) | Day-120 gold 5.2k → 8.4k (roll mode 19k, so still slower than roll). 0.5 did not move S and only added late gold. |
| `BM_MID_REP` | 2 (rep ×3 at the peak) | The value that puts S into 90-110. Sweep on seeds 1-12 below: ×2.5 S 111-117, ×3 107-112, ×3.5 103. |
| `BM_MID_DAYS` | [59, 72, 110, 121] | Days 1-59 and 121+ unchanged (factor exactly 1); ramps of 13 / 11 days. |

Sweep (seeds 1-12 only, 12 × 365; baseline S 141, gold day 120 6,412, day 365 62,243):

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
| **0.25 / 2 / [59,72,110,121]** (chosen) | 66 / 87 / 107 | 8,804 / 88,914 |
| 0.25 / 2.5 / [59,72,108,121] | 66 / 83 / 103 | 9,486 / 121,800 |

The second tuning set (13-24) was run only with the chosen values (S 101).

### Before → after (sensible bot, 12 × 365 per set, `SIM_RESOLVE=battle`)

Tuning sets: 1-12 and 13-24. **Check sets not used while tuning**: 501, 601, 701, 801, 901, 1001 (12 games each).
"Before" is the same code with `--set BM_MID_PAY=0 --set BM_MID_REP=0` (identical games to the stage-3 code: seeds 1-12
and 13-24 reproduce the stage-3 table above exactly).

| Seeds | 1-12 | 13-24 | 501-512 | 601-612 | 701-712 | 801-812 | 901-912 | 1001-1012 |
|---|---|---|---|---|---|---|---|---|
| Final rank / game overs | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 12 | S 12 → S 11, dark 1 | S 12 → S 12 | S 12 → S 12 |
| Day reaching B / A / S | 75 / 108 / 141 → 66 / 87 / 107 | 70 / 98 / 130 → 66 / 84 / 101 | 63 / 95 / 125 → 61 / 79 / 97 | 69 / 104 / 136 → 65 / 83 / 102 | 70 / 98 / 133 → 68 / 84 / 101 | 68 / 104 / 134 → 64 / 85 / 104 | 64 / 102 / 127 → 60 / 78 / 97 | 75 / 105 / 132 → 69 / 85 / 107 |
| Gold day 60 / 90 / 120 | 1,852 / 3,934 / 6,412 → 1,852 / 4,613 / 8,804 | 2,037 / 4,178 / 3,427 → 2,037 / 3,139 / 4,793 | 2,214 / 4,381 / 6,147 → 2,214 / 4,430 / 9,492 | 2,318 / 3,114 / 3,823 → 2,318 / 3,846 / 6,242 | 1,949 / 3,756 / 2,844 → 1,949 / 3,993 / 3,850 | 2,345 / 4,043 / 2,995 → 2,345 / 4,701 / 9,762 | 2,296 / 4,063 / 7,025 → 2,296 / 4,434 / 16,145 | 1,918 / 4,432 / 8,677 → 1,918 / 3,763 / 8,463 |
| Gold day 180 / 365 | 16,116 / 62,243 → 14,633 / 88,914 | 22,037 / 86,676 → 20,160 / 57,079 | 16,528 / 90,315 → 28,280 / 121,964 | 16,336 / 123,807 → 24,344 / 103,067 | 16,554 / 47,466 → 14,514 / 57,854 | 18,596 / 88,024 → 24,190 / 75,962 | 27,684 / 109,348 → 33,656 / 112,067 | 23,776 / 103,641 → 27,556 / 143,343 |
| Captains at the end | 6.25 → 6.33 | 6.83 → 6.25 | 6.67 → 6.5 | 6.75 → 6.92 | 5.75 → 5.83 | 6.75 → 6 | 7 → 6.67 | 6.42 → 6.5 |
| Contracts completed / failed | 402 / 75 → 422 / 74 | 407 / 76 → 442 / 76 | 460 / 68 → 437 / 66 | 436 / 67 → 458 / 71 | 407 / 79 → 426 / 81 | 446 / 76 → 408 / 66 | 452 / 67 → 465 / 75 | 424 / 70 → 422 / 69 |
| Deaths per game special / other | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 | 0 / 0 → 0 / 0 |
| Win 백중 / 우세 / 압도 | 48.3 / 86.4 / 99.6 → 48.2 / 86.3 / 99.4 | 47.3 / 86.9 / 99.8 → 46.7 / 87.7 / 99.8 | 51.2 / 89.1 / 99.8 → 52.9 / 89.9 / 99.7 | 53.7 / 89.5 / 99.6 → 51.8 / 88.8 / 99.7 | 44.5 / 86.4 / 99.8 → 42.9 / 86.7 / 99.6 | 47.3 / 86.6 / 99.6 → 49.7 / 88.2 / 99.7 | 53.9 / 89.5 / 99.8 → 48.2 / 88.4 / 99.6 | 48.4 / 88.8 / 99.8 → 50.1 / 88.9 / 99.8 |
| Win days 1-30 / 31-60 / 61-120 / 121-240 / 241-365 | 90 / 86 / 85 / 84 / 82 → 90 / 86 / 85 / 85 / 83 | 88 / 88 / 85 / 85 / 81 → 88 / 88 / 86 / 85 / 84 | 90 / 90 / 87 / 87 / 86 → 90 / 90 / 85 / 89 / 83 | 90 / 87 / 86 / 86 / 86 → 90 / 87 / 86 / 86 / 86 | 86 / 87 / 86 / 84 / 81 → 86 / 87 / 85 / 83 / 83 | 90 / 90 / 85 / 85 / 83 → 90 / 90 / 83 / 87 / 84 | 89 / 91 / 85 / 86 / 87 → 89 / 91 / 86 / 86 / 84 | 90 / 88 / 86 / 87 / 83 → 90 / 88 / 88 / 85 / 85 |

Means over the sets (before → after):

| | Tuning (24 games) | Check (72 games) | All (96 games) |
|---|---|---|---|
| Day reaching B / A / S | 73 / 103 / 136 → 66 / 86 / 104 | 68 / 101 / 131 → 65 / 82 / 101 | 69 / 102 / 132 → 65 / 83 / 102 |
| Gold day 60 | 1,945 → 1,945 | 2,173 → 2,173 | 2,116 → 2,116 |
| Gold day 90 / 120 | 4,056 / 4,920 → 3,876 / 6,799 | 3,965 / 5,252 → 4,195 / 8,992 | 3,988 / 5,169 → 4,115 / 8,444 |
| Gold day 180 / 365 | 19,077 / 74,460 → 17,397 / 72,997 (-2%) | 19,912 / 93,767 → 25,423 / 102,376 (+9%) | 19,703 / 88,940 → 23,417 / 95,031 (+7%) |
| Captains at the end | 6.5 → 6.3 | 6.6 → 6.4 | 6.6 → 6.4 |
| Game overs | 0 → 0 | 0 → 1 (darkness) | 0 → 1 |

Reading:
- **S on day 97-107 in every set** (was 125-141); per game it is 74-144 after (seeds 701-1012, where the per-game data was kept; before 87-188). A comes
  ~19 days earlier, B ~4 days earlier (the ramp starts on day 60, B is at ~65-70). Roll mode stays faster (S ~73).
- Day 60 gold is identical in every set (nothing before day 60 changed). Day 90 gold barely moves (+3%): the extra pay
  is spent on hires and wages as it comes. Day 120 gold +63% (5.2k → 8.4k), still well under roll mode's 19k.
- **Day-365 gold**: +7% over all 96 games, +9% over the 72 check games. Per set it moves -34% to +43% (1-12 +43%,
  13-24 -34%, 501 +35%, 601 -17%, 701 +22%, 801 -14%, 901 +2%, 1001 +38%) — that is noise, not the lever: per-game
  standard deviation of day-365 gold is 47-146k, so the standard error of one 12-game set mean is 14-42k (17-45%),
  and any change to the economy reshuffles every later game (the gold-only run with S unchanged moved set 1 by +44%).
  Two of eight sets are above +25%, four are below 0; the pooled change is within the +25% bound.
- Word win rates unchanged (우세 86-90%, 백중 43-53%, 압도 99.4-99.8% in every set, before and after); win by day band
  unchanged within ±2 points. Deaths 0 in all 192 games. Contracts completed 402-460 → 408-465.
- **One darkness** (seed 811, after): the calamity rose on day 101 (the calamity is world-driven — a hegemon falls or
  3 factions die, `checkCalamity` in `js/faction.js` — not tied to rank), the guild was still at A with 2 captains at the
  end, and the bot lost the final twice at R 1.05 (백중). The same seed before the change also had an early calamity
  (day 112) and won the final on the third try at R 1.12 on day 143. 1 of 96 games against 0 of 96; stage 3 measured
  0 of 72 at `BM_FINAL_K` 0.5. Worth watching in the next batch; no change made for it.
- Side effect a player may notice: a ★6 contract gives about three times the 명성 on day 90 that it gives on day 130
  (gold ×1.25). The star still rises with rank (cap rank + 4), so later contracts pay back part of the drop.

### Roll mode unchanged

- `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` = `ddfdfe7b437fbe9fcf25f166ba542fce`, also with `SIM_SHADOW=1`.
- `node tools/sim/battle.js 100`: miss 0 in all four outcomes.
- `bot.js` now also records gold on day 90 (`goldAt[90]`), in battle mode only, so roll JSON is byte-identical.

### Commands

```
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4                     # after (defaults)
SIM_SEED=1 SIM_RESOLVE=battle node tools/sim/bot.js 12 365 --jobs 4 --set BM_MID_PAY=0 --set BM_MID_REP=0   # before
# also SIM_SEED=13, 501, 601, 701, 801, 901, 1001 (about 3.3 min per 12 games on 4 cores)
```

