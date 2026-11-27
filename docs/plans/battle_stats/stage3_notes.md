# Battle stats, stage 3: the battle decides, behind a switch

Date 2026-11-27. Base `e33267a` (C7 calibration adopted). Spec: `design.md`, amendments `verify_findings.md`,
owner decisions of 2026-11-27 in `README.md`. Stage 0-1 notes: `stage01_notes.md`.

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
- Switching mid-game is safe in both directions: missions in flight keep their frozen spec (a roll-mode spec is
  played as it is), old missions without a spec are mustered at return, and contracts without `bseed` fall back to
  the save salt.

## What was built

| Item | Where | What |
|---|---|---|
| (a) board | `js/muster.js` `capability`, `battleLevel`; `js/contract.js` `contractLevel` | Each day the strongest `BOARD_TOP` (3) own companies (all members) are forecast against a reference contract (home province, goblin hunt) at every star 1-14. Each new ordinary contract picks one of those companies, draws a forecast word from `BOARD_W`, and takes one of the three highest stars that land in that word, never above the rank cap (rank+2, rank+6 after the calamity, as today). Reward and rep come from `makeContract` unchanged, so harder pays more. Enemies are fixed by star; the board moves, the enemies do not. |
| (b) resolution | `js/muster.js` `battleResolve`; `js/contract.js` `resolveMission` | The frozen `mission.spec` runs once in `Battle.run`; `Game.judge` gives the tier. `report.battle = { v, ver, tab, hash, winner, t, end, R, band, foeShare, spec }`. No roll, no `findBattle`. If the battle cannot run (no `Battle`, an exception) the old roll is used as a fallback. |
| (b) watched = judged | `js/battle.js` `play` | With `report.battle.spec`, playback is `begin(spec)` + the same `step()`: no `findBattle`, no bias. It first reruns the spec headless; if `ver` or `hash` differ (engine changed since the report) it skips straight to the report. `Battle.last()` exposes the played state for tests. |
| (c) loss pay | `js/contract.js` | Lost contract pays `reward × (LOSS_PAY + LOSS_PAY_SHARE × share)` where share = enemy max-hp destroyed (`Stats.foeShare`); disaster pays only the share part. A note tells the player the share. |
| (c) orderly retreat | `js/contract.js` | A fail that ended by retreat costs `-6 × RETREAT_MORALE` = -3 morale instead of -6. |
| (c) grace week | `js/contract.js`, `js/game.js` `weeklyPayday` | A defeat opens a grace week (`GRACE_DAYS`), at most once per `GRACE_EVERY` days. In it unpaid mercs stay (morale -10) instead of leaving, low-morale desertion is off, and unpaid wages (including mercs out on missions) are deferred, not turned into debt. |
| (c) relief contract | `js/muster.js` `reliefCheck`, called from `fillContracts` | When every merc left is a captain, one easy contract (highest unlocked star still 압도 for the best company, reward ×1.5, 5 days) is posted at the home province; never two at once. |
| (c) debt line | `js/game.js` `nextDay` | Battle mode goes bankrupt below `-max(300, DEBT_WEEKS × weekly wages)` instead of -300 (see "Why each constant"). |
| (d) casualties | `js/contract.js` | Fates from the record: downed → injury p 0.6 (won) / 0.9 (lost), 2-4 days, +2 on disaster; standing under 25% hp → p 0.3, 1-2 days; fled → nothing (design §6). Deaths only in special battles (`Game.specialBattle`: boss, final, last chapter of a hero story or a captain story), only on disaster, only downed non-captains, p `DEATH_P` × `mods.death` (× 0.6 sturdy), at most one per company, never with the guild at `GUILD_FLOOR` (3) or fewer. A downed merc on an ordinary disaster is always injured instead. Report members carry `down` / `fled`. External companies lose their downed units, each kept with `EXT_KEEP`, at most `EXT_LOST_CAP`, none on a win (`extAfterMission(…, lostN)`). |
| (e) fill-ins | `js/muster.js` `muster` | Trainee level = lowest level among the company's non-captain members (home or sent); a captain-only company gets level-1 trainees. |
| (e) seed salt | `js/contract.js` `makeContract`, `js/muster.js` | `c.bseed = mix(state.salt, c.id)` at creation. Enemy roster seed `mix(contractSalt, 0xf0e)`, battle seed `mix(contractSalt, 0xb7)`, with `contractSalt = mix(c.bseed, c.id)`, so a reposted copy (new id) is a new battle. No day in the seed. |
| (e) monster attack | `js/stats.js` `monsterSkills`; `js/muster.js` | Battle-mode monsters carry `sk` built from the archetype: only `caster` shoots (projectile look from the sprite template), boss breath for caster/drake/demon bosses. The forecast reads the same `sk`. Changes: 하피, 가고일 (drake) and 마족 전사 (demon) are melee now; 늪의 마녀 (ghost boss) breathes curse. |
| (f) dispatch UI | `js/ui-tabs.js`, `css/style.css` | Battle mode: "예상 전황 「우세」" plus a five-cell scale, the per-company line shows its word instead of power, the contract card shows "예상 「…」" for the best free company instead of 권장 전투력. Removed in battle mode: power/req bar, "예상 성공률 N%", 인원 부족, 피로한 단원, 적대 지역 lines. Kept: slot count, hero-required, campaign consequence. |
| (f) recruitment words | `js/captains.js` | Battle mode counts `mission.est.band` (hardStreak ≤ 백중, gambles ≤ 열세, bigGambles = 무모) and the condition text reads "예상 「백중」 이하 의뢰 연속 성공", "예상 「열세」 이하 의뢰 성공", "예상 「무모」 의뢰 성공". |
| (f) report | `js/ui.js` | Line "출격 때 예상 「…」 · 전투 N초 · 쓰러진 단원 N명"; each downed member shows 쓰러짐 (· 부상 N일). |
| (g) bot | `tools/sim/bot.js` | `--resolve battle` / `SIM_RESOLVE=battle`, `--jobs N`. Battle-mode bot: picks the better forecast of the two strongest free companies, takes 우세/압도, 백중 one time in three; does not retake a special contract it just lost at the same or a worse word within 10 days (unless 압도); near darkness (calamity at `CALAMITY_DARKNESS`-2 provinces) it takes the final and calamity campaigns at 백중, and at 열세 one time in three; captain-only companies may go out. Summary adds win by word, day band, kind, tiers, offers/takes by word, downed/injured, deaths special/other, loss pay, relief, captain-only days. Roll mode is the old bot (md5 unchanged). |
| (g) shadow tool | `tools/sim/shadow.js` | `--resolve battle` measures the deciding battle (`battleResolve`) with the same tables, invariants (`--check`) and CSV; rows add `cid`, `foeShare`, `special`; `--offers` keeps what the bot looked at but did not send. |

## Data shapes (new or changed)

```js
state.resolve = 'battle'            // absent = roll
state.salt = 1..2^31-2              // per save, drawn when battle mode is switched on
state.graceUntil, state.graceStart  // grace week (days)
contract.bseed                      // mix(state.salt, id, 0x5a17), battle mode only
contract.relief = true              // relief contract
mission.spec (battle mode)          // + bm: 1, kind: 'normal'|'story'|…; monster units + sk; seed has no day
report.battle = { v: 1, ver, tab, hash, winner, t, end, R, band, foeShare, spec }   // ~5 KB while the report waits
report.members[i].down / .fled      // battle mode
Game.capability() -> { companyId, tabs: [{ companyId, R: [, R1 … R14] }] }   // cached per day and merc count, not saved
```

## Every constant and why (all in `Stats.KN`, settable with `--set`)

| Constant | Value | Reason |
|---|---|---|
| `BOARD_W` | 0.04 / 0.16 / 0.25 / 0.30 / 0.25 (무모…압도) | Owner decision 1: easy to hard always on the board, with most offers winnable. Measured offers at first look (best free company, per game): 161-187 무모 / 87-92 열세 / 80-92 백중 / 131 우세 / 131-172 압도; the 무모 count is inflated by looking when strong companies are out and by special contracts. |
| `BOARD_TOP` | 3 | With only the best company as reference, weaker companies had nothing winnable and mid-game contract count fell to 17 per 30 days (HEAD 54). |
| `BM_LOW_K` | ★1 0.6, ★2 0.75, ★3 0.9 | A fresh level-1 company forecast R 0.73 (열세) at ★1, so new companies could not work at all. With 0.6 it is 백중-우세. |
| `BM_LATE_STEP` | 3 levels per star from ★8 (ordinary contracts only) | With today's step of 1 the R curve was flat above ★6 and every unlocked star was 압도 from day ~180, so the late board had no hard offers (owner decision 1, "late too easy"). Special contracts keep the old table because their stars come from rank and province. |
| `BM_CAL_ARCH` | soldier 1, grunt 1.087, beast 1.044, brute 1.152, armored 1.202, caster 0.977, blob 0.968 | Inverse R50 per archetype on 8,652 ordinary battles (sent + looked at) with the archetype attack mode. Re-fit after adoption: every archetype R50 0.985-1.007. |
| `BM_CAL_SPECIAL` | boss 0.86, capStory 0.87, story 0.92, final 0.92 | Remaining R50 after the archetype factor (boss 1.08, capStory 1.07-1.14, story 1.07). Small samples (87-224 battles; final 14). Re-fit: boss 0.99, capStory 1.01, story 0.93, campaign 1.00. |
| `LOSS_PAY`, `LOSS_PAY_SHARE` | 0.1, 0.5 | Today's 10% plus pay for what was destroyed; half the enemy beaten → 35%. Measured mean pay on a lost contract 249-285 gold. |
| `RETREAT_MORALE` | 0.5 | Verify amendment 1: an orderly retreat should hurt less. 88-91% of defeats end by retreat. |
| `GRACE_DAYS`, `GRACE_EVERY` | 7, 14 | Amendment 1 (no desertion in the week after a defeat). The first version kept unpaid mercs but still charged debt for mercs on missions, and back-to-back losses kept the grace open forever, which turned desertion into bankruptcy (seed 6 bankrupt on day 127). |
| `DEBT_WEEKS` | 1 | Wages of mercs away on missions are charged at payday; in the leaner mid-game one such payday pushed a guild with 11-18 mercs past -300 (seed 108, day 113) although it recovered income the next days. |
| `BM_FINAL_K` | 0.5 | The calamity rises at day 150-154 in battle mode (184 in HEAD) when the guild is at rank A; the final was R 0.3-0.7 for the three best companies and 2 of 48 games ended in darkness at 0.85 / 1 at 0.6. At 0.5: 0 of 48. |
| `INJ_WIN`, `INJ_LOSE`, `INJ_LOW` | 0.6, 0.9, 0.3 | design §6 table. |
| `DEATH_P`, `GUILD_FLOOR` | 0.3, 3 | Today's death chance and design mercy rule 5, applied only to special battles (owner decision 2). |
| `EXT_KEEP`, `EXT_LOST_CAP` | 0.5, 2 | design §6 rule 7. |
| unchanged | `CAL_KIND`, `BANDS`, `GREAT_HP`, `ENEMY_K`, `SUPPORT_K`, `K` | C7 values; the per-word targets are met with the two battle-mode calibration tables above. |

## Measured results

Commands (all from the repo root):

```
SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum                     # roll: ddfdfe7b437fbe9fcf25f166ba542fce
SIM_JSON=1 SIM_SHADOW=1 node tools/sim/bot.js 6 200 | md5sum        # roll + shadow: same md5
node tools/sim/battle.js 400                                         # legacy replay: miss 0/0/0/0
node tools/sim/shadow.js 6 200 --check --jobs 4                      # roll shadow invariants: all 0 (2,150 battles)
node tools/sim/bot.js 12 365 --resolve battle --jobs 4               # seeds 1-12 (about 60 s on 4 cores)
SIM_SEED=101 node tools/sim/bot.js 12 365 --resolve battle --jobs 4  # seeds 101-112
node tools/sim/shadow.js 6 365 --resolve battle --check --jobs 4     # battle invariants
node tools/sim/shadow.js 12 365 --resolve battle --offers --jobs 4   # word tables and calibration
```

### Roll mode unchanged

- Bot md5 `ddfdfe7b437fbe9fcf25f166ba542fce` with and without the shadow battle; `battle.js 400` miss 0 in all four outcomes.
- Roll shadow rows (3 seeds × 200 days, 1,196 battles) are identical to `e33267a` in hash, R, band and tier.
- `shadow.js 6 200 --check`: 0 violations in 2,150 battles and 6,013 alternative parties.

### Battle mode, 12 × 365 bot games

| | HEAD roll (C4), seeds 1-12 / 101-112 | Battle, seeds 1-12 | Battle, seeds 101-112 |
|---|---|---|---|
| Final rank / game over | S 12 / 0 ; S 12 / 0 | S 12 / 0 | S 12 / 0 |
| Day reaching D / C / B / A / S | 24/36/44/58/73 ; 23/33/42/53/69 | 24/42/68/111/150 | 25/42/66/104/140 |
| Gold day 30 / 60 / 120 | 850 / 5,340 / 19,741 ; 1,193 / 5,637 / 19,434 | 1,035 / 2,316 / 1,944 | 1,006 / 2,207 / 2,980 |
| Gold day 180 / 240 / 300 / 365 | 33,302 / 26,645 / 39,391 / 46,779 ; 26,596 / 31,698 / 41,777 / 51,930 | 11,191 / 11,711 / 31,091 / 49,849 | 23,185 / 39,586 / 61,778 / 69,762 |
| Lowest gold (mean of minima) | 174 ; 248 | 189 | 147 |
| Contracts completed / failed | 632 / 33 ; 680 / 29 | 396 / 71 | 455 / 59 |
| Captains at the end | 5.25 ; 5.42 | 3.67 | 3.08 |
| Calamity rose / defeated (mean day) | 11 (184) / 10 (183) ; 9 (159) / 9 (170) | 12 (154) / 12 (160) | 9 (150) / 9 (159) |
| Win, forecast 백중 | – | 53.0% (n=1,003) | 54.6% (867) |
| Win, forecast 우세 | – | 87.4% (2,870) | 88.8% (2,696) |
| Win, forecast 압도 | – | 99.2% (1,730) | 99.6% (2,606) |
| Win, days 1-30 / 31-60 / 61-120 / 121-240 / 241-365 | – | 87.9 / 79.5 / 77.4 / 86.2 / 86.8% | 83.6 / 87.5 / 78.9 / 89.1 / 91.8% |
| Tiers great / success / fail / disaster | 28 / 67 / 5 / 0% (C4 era) | 34.9 / 50.0 / 15.0 / 0.1% | 45.0 / 43.5 / 11.2 / 0.2% |
| Downed / injured per member-battle | – / 8.5% injured | 13.1% / 7.1% (2.6 days) | 10.2% / 5.1% (2.5 days) |
| Deaths per game, special / other | 0 | 0 / 0 | 0 / 0 |
| Relief contracts | – | 0 (never down to captains) | 0 |

Game-over check over 48 battle-mode games (seeds 1-24 and 101-124): 0 game-overs with the final constants. HEAD
has 0 on the same seeds. Intermediate versions without `GRACE_EVERY` / `DEBT_WEEKS` / `BM_FINAL_K` lost 2-3 games
per 24-48 (bankruptcy on seeds 6 and 108, dark age on seeds 4, 12, 16).

The bot's "avg success chance" and "final battle attempts (avg chance)" lines still print the roll chance; in battle
mode they mean nothing.

### Forecast by word, all battles (sent + looked at, seeds 1-12, 10,257 battles)

| Word | n | Win |
|---|---|---|
| 무모 | 3,319 | 0.5% |
| 열세 | 949 | 17.0% |
| 백중 | 1,365 | 52.5% |
| 우세 | 2,883 | 87.4% |
| 압도 | 1,741 | 99.3% |

Sent only: ordinary 백중 51.7% / 우세 87.4% / 압도 99.2%; special and campaign 백중 58.7% / 우세 86.7% / 압도 100%.
Logistic R50 after calibration: monster 0.987, soldier 1.001; every archetype 0.971-0.992; boss 0.981, capStory
1.006, campaign 1.004, story 0.930. The owner targets (우세 85-90, 백중 about 50) hold for ordinary and special
contracts.

Single-contract error remains: one captain story (2 warriors + 2 clerics against nine ranged 망령) was forecast 우세
(R 1.11-1.20) and won 15 of 100 seeds. `margin` does not model a swarm of ranged casters against a melee-heavy
company; per-archetype calibration only fixes the average. This is why the bot got the "do not retake a lost
special at the same word" rule.

### Determinism: watched battle = judged battle

- `shadow.js 6 365 --resolve battle --check`: 3,001 deciding battles, rerun / JSON round trip / stepped / +2.2 s
  after the end all 0 mismatches; enemy roster changed with the party 0 of 8,670 alternative parties; spec changed
  between dispatch and return 0; `Math.random` calls and state changes inside muster/battle 0.
- Browser (Chrome, 1280×800 and 400×800, `?resolve=battle`, final constants): a won battle at each width (great,
  hash 1613228423 and 2354283017; the played state's `Battle.record` hash equals `report.battle.hash`), a lost battle
  at 1280 (무모 raid, ended by retreat, hash equal, report shows the downed members as "쓰러짐 · 부상 N일" or "쓰러짐",
  85 gold loss pay, grace week opened), and a report whose hash was tampered goes straight to the report with no
  canvas. No page errors, no horizontal overflow. Dispatch shows "예상 전황 「압도」" and the five-cell scale; no %, no
  인원 부족 / 피로한 단원 / 적대 지역; contract cards show "예상 「…」" instead of 권장 전투력.

### Unit checks (scratch `unit.js`)

- Relief: guild reduced to one captain → one relief contract (★2, 압도 for the captain plus two level-1 trainees),
  not duplicated on the next fill.
- Fill-ins: captain level 11 alone → roll-mode trainees 49 / 78 hp (captain-level), battle-mode 15 / 13 hp (level 1).
- Salt: two saves give the same contract id but different `bseed`; battle seed equal after 3 days (roll seed changes
  daily); a reposted copy gets a new seed.
- Attack mode: 하피 / 가고일 / 마족 전사 / 들늑대 melee, 망령 curse shot, 와이번 fire shot, 늪의 마녀 curse breath.
- Grace: 7 broke, demoralised mercs all stay in a grace week; 6 of them leave in an ordinary week.
- Mid-game switch: a roll-mode mission resolved in battle mode is decided by its roll-mode spec; a mission without a
  spec is mustered at return. Both reports carry `report.battle`.
- Deaths: 60 forced ordinary disasters → 0 deaths; 60 forced special disasters → 10 deaths, never more than 1 per company.

## Deviations from design.md

| # | Design | Built | Why |
|---|---|---|---|
| 1 | Flag is a constant in `js/contract.js`, not saved | Saved getter `Game.RESOLVE` (`state.resolve`) | Task: a saved switch with a test param. |
| 2 | Enemy strength from star × req, one ELV table | Battle mode: `BM_LOW_K` for ★1-3 and `BM_LATE_STEP` 3 for ordinary contracts; specials keep the old table | Owner decision 1 and the measured flat late curve; specials' stars are not chosen by the board. |
| 3 | Contract levels from rank and province tier | Battle mode: from the forecast of the top 3 companies, capped by the rank unlock | Owner decision 1. Province tier no longer bounds the star. |
| 4 | Death on any disaster with mercy rules 1-5 | Only special battles; ordinary disasters injure | Owner decision 2. |
| 5 | Forecast = `margin × CAL_KIND` | × `BM_CAL_ARCH` × `BM_CAL_SPECIAL` for battle-mode specs | The archetype attack mode moved R50 per archetype from 0.83 to 1.04. |
| 6 | Fatigue ≥ 80 injury ×1.5 | Dropped in battle mode | Not in the design's casualty table (as feasibility). |
| 7 | Replay reruns headless and compares the hash | Same; on mismatch the report opens at once | – |
| 8 | Betrayal rolled at muster | Still rolled at resolve, marked on a copy of the spec, and that copy is what the report replays | Keeps the roll stream; the replay still equals the judgement. |
| 9 | Recruitment counters on `est` with R edges 1.15 / 0.87 / 0.67 | On `est.band` (C7 edges) | Same words as the screen. |
| 10 | `report.verdict` | Fates are written into `report.members[].down/fled`; `report.battle` holds the record summary | The report UI reads members. |
| 11 | Economic mercy (verify amendment 1) | Built plus two additions found by measurement: grace at most every 14 days without debt, and a debt line of one week of wages | Without them 3 of 48 games ended. |
| 12 | Monster attack by template | By archetype in battle mode only | Task (e); roll-mode shadow stays comparable to C7. |

## What remains

Stage 4 (flip the default to `'battle'`):
- Mid-game economy is lean: gold on day 120 is 2-3k against HEAD's 19k, S is reached on day 140-150 against 69-73,
  and 3-3.7 captains join against 5.3. Decide whether to accept a slower guild or raise early/mid rewards.
- Late gold ends near HEAD (50-70k on day 365) but varies a lot per game (6.5k to 144k).
- Captain-less strength and power displays still use the old power numbers (`js/ui-tabs.js` company tab, final
  battle line "요구 전투력"), and trait/class texts still say "성공률 +N%" (`js/data.js`, `js/classes.js`).
- The merc card shows two 체력 rows (attribute and battle); rename the battle row.
- Forecast error for caster swarms against melee-heavy companies (see above); a composition term in `margin` or a
  `CAL_STYLE` table.
- Special-contract samples are small (boss 80-87, final 14 per 12 games); re-measure `BM_CAL_SPECIAL` and
  `BM_FINAL_K` on more seeds.
- Next-day cost in the browser: one battle per returning contract (about 30 ms each on this machine) plus the daily
  capability table (about 2 ms per company); measure on a phone.
- Recruitment counters for `titan` (1 무모 win) and `shadowqueen` (8 열세 wins) are far harder now (무모 wins 0.5%).
- Antigravity play test of about 100 days in battle mode (design stage 4).
- New md5 baseline for battle mode once the constants settle; flip the default and keep `'roll'` as the undo.

Stage 5 (tactics): synergy bonuses for allies only, measured so that 30-50% of a well-built company's damage dealt
or avoided comes from tactics (owner decision 4); then re-fit `BANDS` / calibration so that a plain company still
wins 85-90% at 우세, and retune the recruitment gamble counters.
