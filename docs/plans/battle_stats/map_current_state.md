MAP: unit stats / "battle decides the result" (label: map)

All line numbers are HEAD 9a30986. js/ is identical to 88af12d. No repo files were edited and no git writes were made.

## 0. Three things that change the design premises

- **C1 "walker yields" is already merged.** HEAD moved during this run (f1f0c2c -> 88af12d "Merge agent/codex: C1" -> 9a30986). The only js change is js/battle.js: new `steer` :744, `crowdedAt` :778, rewritten separation :1032-1077; `plan` :537 and `setup` :628 are untouched. Codex's next task, C2 (docs/agents/tasks/C2-playtest-fixes.md), may touch group names in `plan()` (:609/:619), the trainee marker (:557), view-only battle code, and roster capacity / reserve-captain morale in game.js.
- **The sim has no real stats today.** A unit's strength is one scalar `str` from level only. Enemy strength does not depend on contract level or `req` at all; `bias` does all the scaling.
- **`req` is far below real party power.** In the bot's games, power / effective req has median 4.63, and 92.5% of dispatched contracts sit at the 0.97 chance cap.

## 1. Mercenary data model

**Per-merc fields** (`baseMerc`, js/game.js:110-121):
- Identity and progress: `id, name, role('unit'|'captain'), cls, level, exp, quests, bond, companyId`.
- Stats: `str, dex, int, maxHp`, plus `grow{}` (fraction carry for deterministic unit growth).
- Condition: `status('idle'|'quest'|'injured'), injury` (days), `missionId, fatigue` 0-100, `morale` 0-100 (starts 60-75), `lastQuest`.
- Social: `rel{otherId: -100..100}`, `trait`.
- Gear and look: `equip{weapon, armor, trinket}`, `look{}`.
- Optional: `cap` (captain key), `hero, hcls, title, awakened`, `adv, master`, `elite` (faction).
- There is no per-merc loyalty, defence, speed or personality field. "Personality" today is `trait` only.

**Stats and growth**
- Only four stats exist. Units of the same class and level are identical (game.js:122-127, 175-178).
- Captains grow by `floor(g) + P(frac) + 15% extra` per stat per level (:171-173).
- Equipment adds flat str/dex/int/hp (`eff` :339). Items are `ITEM_BASES` x `TIERS` mul 1..6.5 (js/content.js:81-99), plus uniques and faction loans. Equipment is about 30% of dispatched stats in bot games.
- Level caps (:143-147): unit 10/20/30 by tier (`UNIT_TIERS` js/classes.js:94-98), captain 40, hero 15/22/30/40 by story chapter.
- `expToNext = 60L + 6L^2` (:141). Wage :341-347.

Deterministic stat table (scratch `tables.js`):

| Unit | Lv | str | dex | int | hp | power(null) |
|---|---|---|---|---|---|---|
| warrior | 1 | 8 | 4 | 2 | 32 | 20 |
| warrior | 10 | 27 | 13 | 4 | 86 | 83 |
| paladin | 20 | 51 | 23 | 16 | 186 | 169 |
| guardian | 30 | 81 | 33 | 28 | 321 | 264 |
| mage | 1 | 2 | 4 | 9 | 18 | 20 |
| archmage | 30 | 10 | 30 | 127 | 111 | 268 |
| swordsaint | 30 | 112 | 56 | 10 | 206 | 390 |

Expected captain stats by style:

| Style | Lv | main stat | hp |
|---|---|---|---|
| warrior | 1 | str 12 | 50 |
| warrior | 20 | str 79 | 252 |
| warrior | 40 | str 150 | 465 |
| mage | 40 | int 167 | 291 |

**Traits** (js/data.js:39-64): power multipliers for brave/coward/berserker/arcane/royalguard/northknight/warcry/commander; the rest are party modifiers. `TRAIT_CLASH` game.js:14. All 33 named captains carry one of brave/diligent/genius/greedy/lucky/sturdy (js/content.js:419+).

**Condition multipliers**: morale 1.1/1/0.92/0.8 (game.js:282-287); fatigue 1/0.9/0.75 (:288-292). Friends +8% each (max 2), rivals x0.9 each (:391-397). `FRIEND_REL` 30, `RIVAL_REL` -20 (:12).

**Power** (game.js:369-399):
- `power(m, type, party)` = str·w + dex·w + int·w + maxHp·w.hp + 3·level, with weights per quest type (`QUEST_TYPES.weights`, js/data.js:79-140).
- Then trait multipliers, awakened x1.15, class `fx.self` (all / types), morale x fatigue, friends / rivals / commander.
- Company: `ownCompanyPower` = sum(power x `memberLeadMul`) x `SQUAD_POWER` 1.3 x `cohesionMul` (0.9 + 0.002·cohesion) x `leaderMul` (js/contract.js:244-247; js/company.js:9, 104-119).
- `leaderMul` = 0.85 with no captain present; otherwise 1 + 0.004·level + (lead.power + lead.types[type] + vsCalamity) x 1.5 from Lv20.
- External company: `extPower` = size x (16 + 7·level) x 1.4 x specialty 1.2 x (0.9 + 0.002·loyalty) (company.js:202-206).
- `partyMods` (game.js:402-441): `success, injury, death, gold, great, greatGold, days, noDisaster, healHalf, loot, noMoraleLoss`.

**Captains** (js/classes.js:240-371): 33 `CAPTAIN_CLASSES`.
- Each has `style` (warrior 10, archer 7, cleric 6, mage 5, rogue 5), base/growth from `CAPTAIN_STYLE` :244-250 plus tilt, `lead{name, power 0.02..0.12, types, cls, party, vsCalamity}`, and `acts[basic, special]`.
- Basics: 16 melee, 12 shot, 5 heal. Specials: 12 melee, 12 shot, 6 rally, 3 heal.
- Captains never die (contract.js:397).

**Heroes** (classes.js:376-414; content.js:109-365): 7 `HERO_CLASSES` with `acts[2]` and passive `fx`, scaled x(1 + 0.25·chapters). Story rewards add stats / awaken (contract.js:657-664).

**Class tree** (classes.js:85-234): 5 base (`CLASS_SKILLS` :85-91), 10 adv (`PROMOTIONS` :105-146, each with `bonus` and `growth`), 20 master (`MASTERS` :151-232). Each class has exactly one battle skill `b` and one contract `fx`.

**Battle skill schema** (classes.js:7-17): `cd, range` (melee 11), `tgt` enemy|hurt|self, `shot, dmg, heal, aoe, hits, stun, dash, drain, exec, buff/selfBuff{atk, def, dur}`.

## 2. Enemy data

- **`ENEMIES`** (content.js:9-41): 31 entries with only `{tpl, pal, big?, boss?}`. There are no stats.
- **A contract's enemy** (`makeContract`, contract.js:80-111): `{type, cat, level 1..10 (14 late), size, days, req, province, issuer, target, enemy (name or null), reward, rep, expires}`.
  - Monster contracts take `enemy` from the province terrain list (`TERRAIN[].enemies`, js/world.js:84-92) or `MAGIC_ENEMIES`.
  - Conflict contracts have `enemy = null`; the foe is the target faction's soldiers (`FACTIONS[f].soldier.classes`, world.js:11-41).
  - Calamity targets use `FACTIONS[cal].monsters`.
- **`req`** = 24 x 1.4^(L-1) x U(0.9, 1.1) x (0.8 + min(size x 1.25, 6) x 0.1) (:95). Medians: ★1 27, ★5 103, ★8 282, ★10 550, ★12 1075. Hostile territory x1.2 (`effectiveReq` :260-264).
- **Special contracts**:
  - Campaign: `offerCampaign` :197-227 — size slots x 3 + 1, 2-3 companies, req x1.05. Untaken campaigns are settled by `autoResolveCampaign` (js/faction.js:423) on the strength ratio, with no battle.
  - Final: :562-591 — req = strength(cal) x 33, size 11, 3 slots.
  - Bosses: `BOSSES` content.js:45-76, `checkBosses` :696-714 — req x1.3, size 4.
  - Hero story: :608-641. Captain story: js/captains.js:133-153.

## 3. Resolution flow, and everything that assumes "outcome first"

**Dispatch** (contract.js:297-327)
- Guards, then `chance = successChance()` is frozen into `mission{id, contract, units[{companyId, memberIds}], startDay, returnDay, chance}` (:309-312).
- Fatigue +10 + 7·days is applied at dispatch (:322).
- `successChance` (:266-279) = 0.5 + 0.9·(pw - req)/req + 0.02·(distinct classes - 1) + `partyMods.success` - 0.06·missing heads, clamped to 0.03..0.97.

**What can drift between dispatch and return**
- Morale: daily drift (game.js:623-626) and grief (contract.js:435-441).
- Equipment: loan recall (faction.js:112-116). `Game.equip` has no status guard (game.js:582); only the UI hides it (js/ui.js:182).
- Faction standing, which feeds the hostile x1.2.
- Today `chance` uses dispatch-time values, while the external gold share uses resolve-time `unitsPower` (:364).

**Resolve** (`nextDay` game.js:609-611 -> `resolveMission` contract.js:330-492)
1. Betrayal roll for campaign external companies: chance -0.25 (:337-348).
2. Roll (:351-356): great if roll < chance x 0.25 x `mods.great`; success if < chance; disaster only if chance < 0.6 and roll is in the top 25% of the fail band (unless `noDisaster`); otherwise fail.
3. `report.seed = rand(1, 1e9)` (:359).

**Consumers of `outcome` / `won`**
- Gold: x1.5 x `greatGold` on great, 10% on fail, 0 on disaster; external share; `mods.gold` (:362-381).
- Reputation: x1.5 on great, -0.3 / -0.6 on fail / disaster.
- `stats.completed` / `failed`; loot roll (:371).
- `applyContractEffects` (:495-552): standing (x1.3 on great), control, war score, weariness, province transfer, capital rule, `defeatCalamity` on a final win.
- Exp x1.5 / 1 / 0.5 / 0.3 (:389).
- Injury base 0.05 / 0.15 / 0.4 / 0.7 x mods (:390, 410-420).
- Death only on disaster, 0.3 x `mods.death` (:396-407), leading to `removeMerc`, hero dead flag, grief.
- Morale +6 / +2 / -6 / -12 (:414).
- Hero `bond` (:395); relations +8 / 5 / 3 (:429).
- Company wins / losses and cohesion +5 / +2, -20 per death (:443-447).
- `extAfterMission` (company.js:268-286): loyalty, level-up, members lost.
- `provClears`, which unlocks bosses (:470).
- `trackMission` (:471).
- Reposts on loss for final / capStory / boss / story (:476-491); chapter and boss completion on win.

**Recruitment counters** (captains.js:28-45; conditions content.js:388-415)
- `streak`; `hardStreak` (win with `mission.chance` < 0.8); `gambles` (< 0.4); `bigGambles` (< 0.25); per-type counts; `lastDeath`.
- These read the frozen dispatch chance, so they need a decidable replacement.
- Bot games: 18.6 wins per game under 0.8; zero under 0.4.

**Report shape** (:334, 393, 455-467)
- `{quest, outcome, gold, rep, share, seed, members[{id, name, cls, look, exp, levelUp, injury, dead, company}], ext[], standing[], control[], notes[], companies[...]}`.
- Own company entry: `members[{id, name, look, cls, level, leader, unique, sk, art, capKey, heroKey}]`. External entry: `{size (before losses), level, look, betrayed}`.
- Skill objects (`sk`) are serialized into the save.

**Saved slot and spoiler guard** (ui.js)
- `showReports` :311 moves `pendingReports[0]` into `s.reportSlot{item, stage 'battle'|'report'}`. `presentSlot` :331 plays `Battle.play` and then `missionReport` :420.
- `hookResolve` :355 wraps `Game.resolveMission`: it records `shownDelta{gold, rep}` and the last log line, and reorders news that was queued early. It finds the report by `x.quest === mission.contract` identity (:365).
- `shownTop` :390 subtracts unseen deltas. The guard is only active when `settings.battle` is on (:393).
- The guard assumes state is already mutated at resolve and playback comes later. That stays true if the battle is simulated headlessly inside `resolveMission`.

**Playback** (battle.js `play` :2647-2776)
- `plan(report)` -> `findBattle(groups, report.outcome, seed)` :1122-1148 -> `setup(groups, found.bias, found.seed)`, then the same `step` at fixed DT.
- `findBattle` runs up to 16 sims (seed + i·101), bisecting `bias` in 0.1..6, starting at 0.7 / 0.95 / 1.15 / 1.35.
- It rejects battles of 60 s or longer, great with loss > 25%, and disaster with loss < 50%.

**Places that assume the outcome is known before the battle**
- battle.js:3-4 header comment.
- `plan()` `deadIds` -> `doomed` (:545, 552-555), then str x0.6 (:654) and the skull icon (:2251).
- `betray` flag: the group flips at t > 7 (:926).
- End label taken from `report.outcome` (:2723) and `won` (:2650).
- `findBattle` / `bias` in `setup(groups, bias, seed)` (:652).
- tools/sim/battle.js.
- docs/DESIGN.md:234-236 and 286; README.md:82-83.
- Dispatch UI: exact "예상 성공률 N% (label)" (js/ui-tabs.js:324-334, `chanceLabel` :222); "권장 전투력" (:181); "인원 부족" and "피로한 단원" lines (:337-340), which act as dispatch warnings.
- Bot thresholds (tools/sim/bot.js:126-127).

## 4. The sim's unit model (battle.js)

**`plan(report)`** (:537-623) is deterministic from the report, `rng(report.seed)` and static tables.
- Own members: `str = (0.85 + 0.035·level) x 1.15 if leader` (:555); max 4 per group; trainees `str 0.7` fill up to 3 (:557).
- External: captain 0.9 + 0.03·level, others 0.8 + 0.025·level (:561-562).
- Support groups fill ally groups up to the enemy group count: issuer soldiers `str 0.85`, or villagers 0.65 (:580-591).
- Enemy: 2 groups, or 3 if level >= 5 / campaign / final / boss (:534); +1 unit at level >= 6 (:546).
  - Monster group: bigMon leader `str 1.1` (boss 1.4, scale 3) plus 2-3 minions `str 1` (:595-610).
  - Soldier group: 3-4 at `str 1` using the faction class list (:611-621).
- Max 3v3 groups, 24 units. Bot plans: median 22 units; 87% are 3v3.

**`setup`** (:628-679)
- Base stats (`CLASS_STATS` :41-47): warrior 130 hp / 13 atk / 24 speed; rogue 90/15/34; archer 75/11/26; mage 65/14/22; cleric 90/9/24. `MONSTER_STATS` 110/12/27 (:48).
- bigMon: hp x2.6, atk x1.6. Boss: hp x7, atk x2.4. Both: speed x0.85 (:642).
- `str` = `ud.str` x (`bias` if enemy) x 1.15 if group captain x 0.6 if doomed (:652-654).
- `hp` = base.hp x str x 1.6 (human captain) x 1.15 (unique) (:655).
- `atk` = base.atk x str x `ATK_SCALE` 0.55. `healPow` = 16 x str x 0.55. `speed` = base x U(0.9, 1.1) (:664).
- Per-unit state: `x, y, hp, maxHp, atk, healPow, speed, skills[{...sk, left}], buffs[], stunUntil, slowUntil, alive, fled, target, retarget, face, healer, reach`, plus slot/steer fields.
- Skills come from the report's `sk`; otherwise the class basic (+ `GENERIC_SPECIAL` for group captains, :55-61) or `monsterSkills` (:63-72).

**Damage** (`strike` :815-838)
- `atk x (1 + atk buffs) x aura 1.1` (own captain alive within 60, :789-793) `x sk.dmg x U(0.85, 1.15) x crit` (10%, x1.7).
- AoE secondary targets x0.7. `exec`: x(1 + exec) when the target is under 35% hp.
- Target's `defMul` = 1 - min(0.6, sum of def buffs) (:794).
- Stun and slow are shortened on bigMon / boss. `drain` heals the attacker.
- `mend` :840: healPow x heal x U(0.9, 1.1).
- There is no base defence, armour, accuracy, evasion, damage type or resist, and no use of str/dex/int.

**Rout** (:932-941): a group routs below 30% alive, or below 55% with its captain down. There is no morale value.

**End** (:1092-1103): one side has no active group, or t >= 90 s (then the higher total hp wins). `simulate` returns `{won, loss (player dead / player units), t}` (:1113-1117).

**Tick and RNG**: DT 0.05, own mulberry `rng(seed)` (:78).

**Management data that reaches the sim**: level, cls (base/style), leader, unique, the skill objects, look, art keys; external size / level / betrayed; quest enemy / target / issuer / province / level / flags.

**Management data that does not reach it**: str/dex/int/maxHp, equipment, traits, morale, fatigue, relations, cohesion, lead bonuses, class fx, quest-type weights, external specialty / loyalty, hostile territory, `req`, terrain effects (terrain is view-only, :2661).

## 5. Numbers

Bot: `node tools/sim/bot.js 12 365`, seeds 1-12 — 17 s, all 12 reach S, completed/failed/fallen 632/33/0.

**Contracts**
- 665 per game (range 476-850), 1.82 per day (0.79 in days 1-30, about 2 later).
- Up to 7 resolve on one day (3 or more on 32% of resolving days).
- Per game: 472 monster, 117 conflict, 32 diplomacy, 18 campaign, 5.4 boss, 10.6 hero story, 9.7 captain story, 1.3 final.

**Outcome mix**: success 67.0%, great 28.1%, fail 5.0%, disaster 0, deaths 0. The bot only sends at chance >= 0.6, which makes disaster impossible. Injury rate: great 3.4%, success 9.6%, fail 25.3%.

**Chance and power**
- Chance: 92.5% of dispatches are exactly 0.97; only 6% are below 0.9.
- Of evaluated offers, 98.8% were taken.
- pw / effective req: p10 1.6, median 4.63, p90 13.2.
- Median pw / req by day band: 146/38 (days 1-30), 294/91, 680/159, 1258/207, 1598/242 (days 241-365).

| Kind | pw / req median | Won |
|---|---|---|
| boss | 2.09 | 92% |
| hero story | 1.85 | 89% |
| captain story | 1.98 | 88% |
| campaign | 3.23 | 96% |
| final | 0.81 (chance median 0.64) | 67% |

**Party at dispatch**
- 23.1% of dispatches include an external company; 14.1% of own dispatches have no captain; 1.9% field fewer than 3.
- Cohesion median 100; `leaderMul` median 1.10; the captain supplies about 29% of company power.
- Class mix: warrior 38%, archer 30%, cleric 26%, mage 4%, rogue 2% (the bot's hiring order).

| Role | Days | Lv median | hp median | main stat median |
|---|---|---|---|---|
| unit | 1-30 | 3 | 36 | 10 |
| unit | 61-120 | 9 | 94 | 36 |
| unit | 241-365 | 16 | 193 (max 296) | 63 (max 101) |
| captain | 1-30 | 4 | 71 | 23 |
| captain | 241-365 | 18 | 257 (max 342) | 91 (max 121) |

**Battle cost** (this machine, node 22, HEAD with C1; 799 sampled reports)
- One headless `simulate()`: mean 49.6 ms, median 45.7, p99 113, max 145 — about 1.74 ms per sim-second.
- Battle length at bias 1: median 25.9 s, p90 41 s, max 90 s (the time limit).
- `findBattle` today: mean 131 ms on rolled outcomes; `tools/sim/battle.js 100` gives avg 80 ms, max 645 ms. Codex's machine reported 34 ms.
- If every contract runs one sim, that is about 50 ms per contract: about 90 ms per average day, about 0.35 s on a 7-contract day, and about 33 s more per bot game (12 x 365 goes from 17 s to roughly 7 min).
- A median-of-N forecast on the dispatch screen would cost N x 50 ms per refresh.

**Today's sim at bias 1 is not calibrated**
- Natural win rate is 67.5% against a rolled 95.6%. A 3-seed majority agrees with the roll 68% of the time.

| Days | Natural win |
|---|---|
| 1-30 | 13% |
| 31-60 | 36% |
| 61-120 | 48% |
| 121-240 | 75% |
| 241-365 | 83% |

- By enemy: boss 22%, soldiers 59.5%, monsters 71%.
- corr(pw / req, natural win) = 0.26.
- `findBattle` bias: great 0.70; success median 0.95 (p10 0.72, p90 1.20); fail 1.15 and up.
- Earlier tactics measurement, pre-C1 (scratch tactics/map/tac30.log): at x0.8 / x0.9 / x1.1 / x1.25 of the 50/50 enemy strength, win rate is 1.00 / 0.96 / 0.06 / 0.00. A ±10% strength change flips the result, so seed variance is small next to a 30-50% tactics effect.

**Save format** (game.js:5-6, 54-67; js/main.js:6)
- One localStorage key, `pixel-guild-save-v4`, holding the whole state as JSON; `version` 4.
- `load()` returns false on any version mismatch and main.js then starts a new game. A version bump therefore discards saves; there is no migration ladder.
- Existing migration style keeps v4: a flag plus an idempotent `normalizeCompanies()` on load (`squadRule`, company.js:136-166); lazy defaults (`s.track` captains.js:105, `s.loans`, `m.morale ?? 65`, `lastFeast ?? -99`); and a compat branch in `plan()` for old reports without `companies` (battle.js:566-571).
- In-flight items a new format must handle: `s.missions[]` (which have `chance` but no stat snapshot), and `s.pendingReports[]` / `s.reportSlot` (stage 'battle', outcome already rolled, no battle record).

## 6. Tests and tools that pin today's behaviour, and what breaks

- **tools/sim/battle.js**: takes every 4th bot report and all 4 outcomes, and asserts `findBattle` reproduces each (mismatch must be 0); it also reports slow battles and timing. It depends on the `Battle.plan` / `findBattle` API, the report shape, and a `UI.h.soldierLook` stub (:12-15). Its premise disappears once the battle decides. The natural replacement is a determinism check: the same frozen input gives the same result in judgement and replay.
- **tools/sim/bot.js**: loads 9 files without battle.js (:14); dispatches on `successChance` >= 0.6 / 0.55 (:126-127); sorts by `unitsPower` (:123); prints avgChance / completed / failed / fallen. `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` is the regression gate in docs/agents/README.md:27-28 and the C1 / C2 task docs.
  - If `resolveMission` calls the sim, the bot must load battle.js plus the UI stub, its runtime grows about 20x, and every md5 and summary baseline changes.
  - Determinism still holds: the bot patches `Math.random` (:39-42), and the battle seed is drawn from it.
- **Docs to update**: DESIGN.md §3 (battle) :234-236, §5 :252 and :286 with the bot tables; README.md:82-83.
- **Not pinned by any test**: the renderer (the sim tools run with `Art = undefined`), and the UI spoiler guard / reportSlot (browser only).

## Scratch files

All under /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/map/

- repo/ — `git archive` of 88af12d (js identical to HEAD)
- repo_f1f0c2c/ — pre-C1 copy
- measure.js — bot plus dispatch/resolve hooks plus natural sims
- an_mgmt.js, an_battle.js, tables.js — analysis scripts
- rows_mgmt.json — 7,982 contracts with per-member stats
- rows_battle.json — the 799 sampled battle rows