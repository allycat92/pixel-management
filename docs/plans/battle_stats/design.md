# Battle stats skeleton: units get real numbers and the battle decides the contract

Date 2026-11-26. Design only: no repo file was edited and no git write was made.
Merged from three designs (stat sheet, resolution, tactics) and the map report. Their prototypes and
raw numbers are in the scratch folders listed in section 15.

Line anchors are HEAD `607f23d` (C1, C2 and C3 are all merged; `docs/agents/queue.md` has no open task,
so nothing has to "land first" any more). Against the designs' base `9a30986`: the sim part of
`js/battle.js` (:626-1120) is unchanged, `js/contract.js` is +2 lines, `js/game.js` is about +10.

## 0. The skeleton in ten lines

1. A unit has **three numbers** — HP, ATK, DEF — and one multiplier, **condition**. Everything the
   management game already tracks (attributes, level, gear, traits, morale, fatigue, friends, cohesion,
   captain) flows into those four values and nowhere else.
2. Damage is `K · ATK · skill · ATK/(ATK+DEF)`. Ratio defence, no cliffs, one enemy table for every star.
3. Enemies are `reference curve(level) × archetype × rank × k`. Six archetypes, four ranks.
4. Inputs are **frozen at dispatch** into `mission.spec`. The forecast, the judgement and the replay all
   read that one object.
5. On the return day **one deterministic sim** runs on the spec. Its record (who is down, who fled, hp
   left) decides the tier, the injuries and the deaths. No roll, no `findBattle`, no `bias`.
6. The four tiers stay (great / success / fail / disaster), so about 20 settlement consumers do not change.
7. Mercy: death only when nobody of ours is left standing, at most one per company, never a captain,
   never below three mercs; and our side retreats from a lost fight instead of dying in place.
8. The forecast is stats-only and analytic (no sims): a ratio `R` shown as five words.
9. Tactics come from per-unit preferences (role, trait, captain doctrine). Movement lands first and
   changes no result; three earned states (steady fire, brace, flank strike) are **allies-only upside**,
   amplified by captain fit. The forecast never reads them.
10. Seven stages, each shippable; stages 0-3 change no outcome. The switch is one flag and can be undone.

## 1. What the measurements force

| Fact | Number | Source | Consequence |
|---|---|---|---|
| The sim has no real stats | strength = one scalar from level (`plan` :555) | map | everything in section 2 is new input |
| `req` is far below real power | power / effective req median 4.63; 92.5% of dispatches at the 0.97 cap | map | enemy strength must come from star and tables, not from `req` alone |
| Today's sim is not calibrated | natural win 67.5% vs rolled 95.6%; days 1-30 13% | map | calibration is a stage of its own (stage 3) |
| Results are nearly deterministic | win at enemy ×0.9 / ×1.0 / ×1.1 = 96% / 63% / 0% (stat engine); two seeds disagree on 2.3% | stats | a 30-50% tactics effect is far above seed noise; the forecast band will read as the result unless tactics move it |
| Judgement and replay already agree | 288/288 identical, also after a JSON round trip and play-style stepping | resolution | one sim can be both judge and replay |
| One leak | 4/288: a unit's fate changes after `st.over` (shots land in the 2.2 s end hold) | resolution | fix in stage 0 |
| Defeats are near-wipes | 98-99% of defeats have half or more of ours down; 21.5% leave nobody standing | resolution | a retreat rule is a mercy requirement, not polish |
| Support dilutes the roster | support holds 40% of ally hp×atk; own units 53% | resolution | `SUPPORT_K` 0.6 and a sweep on it |
| 20% of dispatches are external-only | 58/288 | resolution | "ours" = own and external company members |
| Cost | one sim 46-50 ms (p99 92-113 ms); up to 7 contracts a day | map, resolution | one sim per contract is fine; a median-of-N forecast is not |
| Movement is outcome-safe today | `tools/sim/battle.js 100`: mismatch 0 with the movement layer on | tactics | movement can ship before the switch |
| A save version bump discards saves | `load()` returns false on mismatch (`js/game.js:71`) | map | stay on v4, lazy defaults only |

## 2. The stat sheet

Shown on the merc card: **체력 HP, 공격 ATK, 방어 DEF** and one chip **컨디션 ×N**. Nothing else is per-unit.
The four attributes (str / dex / int / maxHp), level, gear and growth stay exactly as they are; they are
the ingredients, the sheet is what the battle reads.

| Stat | Formula | Fed by |
|---|---|---|
| HP | `eff(maxHp)` | level, class growth, armour and amulet hp |
| ATK | top + 0.3·mid + 0.1·low of `eff(str, dex, int)` | main attribute, weapon, ring |
| DEF | 0.3·`eff(str)` + 0.1·`eff(maxHp)` + armour | str, hp, armour kind: plate 3, leather 1.5, robe 0.6, × `TIERS.mul` |
| cond | product of the parts below | every % modifier in `power()` today, same values |

Rules:

- **cond multiplies HP and ATK once, at freeze time. DEF is not multiplied.**
- **Level has no term of its own.** `+3·level` in `power()` (`js/game.js:379`) and `0.85 + 0.035·level`
  in `plan()` (`js/battle.js:555`) both go; level works through attributes only.
- **Armour DEF is derived from the item's base and tier, never stored on the item** (uniques and faction
  loans: a small lookup by slot kind). No new saved field.
- **Class constants, not stats:** move speed (`CLASS_STATS.speed`, :41), range and attack interval
  (skill `range` / `cd`). Crit stays a flat 10% ×1.7.
- **Not added:** accuracy, evasion, resist, crit stat, an in-battle morale value.

Parts of cond (all at today's values; names are the keys of `sheet().parts`):

| Part | Values | Scope |
|---|---|---|
| `trait` | brave 1.1, coward 0.9, berserker 1.25, arcane / royalguard / northknight / warcry as today; awakened 1.15; class `fx.self` | personal |
| `morale` | 1.1 / 1 / 0.92 / 0.8 | personal |
| `fatigue` | 1 / 0.9 / 0.75 | personal |
| `bond` | friends +8% each (max 2), rivals ×0.9 each, commander 1.08 | party |
| `lead` | `cohesionMul` × `leaderMul` (0.85 with no captain) × `memberLeadMul` (`js/company.js:104-119`) | company |
| `apt` | quest-type aptitude, **bonus-only 1.00-1.20** from `QUEST_TYPES.weights` (Lv10: mage on magic 1.20, warrior on hunt 1.13) | contract |
| `aid` | `1 + partyMods.success / 0.9` (keeps lucky / hawkeye / sylvan / archer fx alive) | party |

The merc card shows HP / ATK / DEF with the **personal** parts applied (trait × morale × fatigue) and the
chip shows that product. Party, company and contract parts are applied at muster and are visible only
through the forecast.

```js
Stats.sheet(m, {type, party, company, members, contract})
// -> { hp, atk, def, mul, parts:{trait,morale,fatigue,bond,lead,apt,aid}, raw:{hp,atk,def} }
```

Reference values (stats prototype; Lv10, on-tier gear, cond 1):

| Class | HP / ATK / DEF | Role in the numbers |
|---|---|---|
| warrior | 110 / 42 / 28 | takes 16.8 s to die to one on-level enemy |
| archer | 78 / 43 / 16 | range 95, 6.1 dps |
| mage | 59 / 48 / 8 | aoe, pierce 0.5 |
| cleric | 95 / 35 / 21 | heals 5.5 per second |
| rogue | 76 / 43 / 16 | 10.3 dps plus execute |

Lv1 no gear: warrior 32/9/6 … mage 18/10/2. Warrior line: Lv10 110/42/28 → paladin Lv20 241/85/60 →
guardian Lv30 399/130/94. Warrior-style captain: Lv1 62/22/15, Lv20 307/128/78, Lv40 543/230/134.

What is dropped on purpose (and why it is not a loss):

| Dropped | Was | Now carried by |
|---|---|---|
| +2% per distinct class | `successChance` (`js/contract.js:268`) | tactics (composition reward) |
| −6% per missing head | same | fewer units on the field |
| `SQUAD_POWER` 1.3 | `js/company.js:9` | own units have real sheets; externals use generic sheets |

## 3. Damage

```
hit  = K · ATK · skill.dmg · ATK / (ATK + DEF·(1 − pierce)) · U(0.85,1.15) · crit
heal = K · ATK · skill.heal · U(0.9,1.1)
K start value 0.25 (pacing knob only)
pierce by shot kind: fire 0.5, curse 0.5, holy 0.5, bolt 0.3, arrow / dagger / melee 0
```

- Existing def buffs (`defMul` :794), `exec` and `drain` stay multiplicative on top. The tactics layer
  gets exactly three multiplier points: outgoing (`strike` :815), incoming (`damage` :798), cooldown
  (`useSkill` :873).
- **Ratio, not subtractive** — measured, same scenario: Lv10 rogue vs armoured DEF 39 loses 26% of its
  damage under ratio and hits the floor (−75%) under subtractive; composition spread vs armoured enemies
  is 17% under ratio and 35% under subtractive. Subtractive punishes mismatch; ratio leaves the spread to
  tactics, which is the owner's "reward, not punish".
- **K changes pacing, not strength**: K 0.25 / 0.18 / 0.14 gives k50 1.23 / 1.24 / 1.23 and even-odds
  length 27 / 35 / 40 s. Bot-game battles at K 0.25 have median 11.5 s (today 25.9 s). K is set in
  stage 3 from the pacing target in section 11.
- Elasticities (Lv10, company alone): cond ×1.1 → strength ×1.09; ATK ×1.1 → ×1.04; HP ×1.1 → ×1.04;
  DEF ×1.3 → ×1.05; level ±2 → ×1.29 / ×0.89; no captain → ×0.57 (today 0.60).

## 4. Enemies

```js
// E(L), n = L-1: the average geared unit of level L
REF  = { hp:[28, 5.2, 0.085], atk:[10, 3.2, 0.055], def:[5, 1.25, 0.018] }   // base, per level, per level²
ARCH = {                                   // each ENEMIES entry (js/content.js:9-41) gets `arch`
  grunt:   { hp:1.0, atk:1.0,  def:1.0, speed:27 },   // 고블린 산적 오크 리자드맨
  beast:   { hp:0.9, atk:1.25, def:0.6, speed:36 },   // 들늑대 지옥견 하피
  brute:   { hp:1.3, atk:0.85, def:0.7, speed:22 },   // 트롤 설인 전갈 거인
  armored: { hp:1.0, atk:1.0,  def:2.2, speed:23 },   // 해골 병사 가고일 데스 나이트
  caster:  { hp:0.7, atk:1.15, def:0.5, speed:24 },   // 망령 와이번 (ranged, pierce 0.5)
  blob:    { hp:1.9, atk:0.8,  def:0.1, speed:20 },   // 늪 슬라임
}
RANK = { minion:{hp:1,atk:1,def:1}, leader:{hp:1.6,atk:1.15,def:1.1}, big:{hp:2.6,atk:1.4,def:1.2}, boss:{hp:7,atk:2.0,def:1.4} }
ELV  = [0, 1,2,3,5,7,9,11,12,13,14,15,16,17,18]      // star -> enemy level (final: 18)
k    = clamp(effectiveReq / (24·1.4^(star−1)·1.175·(boss ? 1.3 : 1)), 0.7, 1.6) · ENEMY_K · KIND_K[kind]
```

- **Star sets the enemy level; `k` carries the rest of `req`**: the ±10% roll, contract size, hostile
  territory ×1.2 (`effectiveReq`, `js/contract.js:262`), campaign ×1.05. `k` multiplies hp, atk and def.
- **Soldiers** (conflict foes, support, external companies, trainees): `Stats.generic(cls, L, rank, k)`
  from `CLASSES` base and growth plus a gear equivalent. Externals × specialty 1.2 × (0.9 + 0.002·loyalty).
  Trainees: level − 2, ×0.7.
- **Bosses are a rank row** (the ×1.3 in boss `req` is divided out of `k`).
- **Roster rules are unchanged in the skeleton**: 2-3 enemy groups, +1 unit from ★6, support fills ally
  groups (`plan` :580-621). Contract size acts through `k`. Enemy headcount by contract size is a later
  question, after calibration.
- Start values: **`ENEMY_K` 0.8, `SUPPORT_K` 0.6, `KIND_K` all 1.0** (stage 3 fits them).

Sample (minion / big / boss at k 1): ★3 grunt 39/17/8, 101/23/9, 271/33/11; ★6 grunt 75/39/16,
195/55/19, 525/78/23; ★10 armored 110/61/53, 286/85/64, 770/122/75.

Worked check (hunt ★3, 4-man company vs an orc and two goblins): hand arithmetic gives 84% ally hp left;
the sim gives 84%, 11.7 s, 100% wins over 40 seeds.

## 5. Resolution flow

```
dispatch ──> Game.muster(contract, units) ──> mission.spec (frozen)   mission.est = Game.forecast(spec)
return day ─> Battle.run(spec) ──> record ──> Game.judge(spec, record, mods) ──> verdict
            ─> settle (today's consumers, reading tier and real fates) ──> report{…, spec, battle, verdict}
watched ───> Battle.play(report): rerun spec headless, compare hash, then setup(spec) + the same step()
```

- **Freeze at dispatch**, before the dispatch fatigue is added (`js/contract.js:299-327`), so the fight
  uses exactly the numbers the forecast showed. Morale drift, loan recall and standing changes during
  the mission stop mattering.
- **Equip guard**: `Game.equip` / `unequip` (`js/game.js:592`, :603) refuse `status === 'quest'`. Without
  it gear can be moved to a second company after the first is frozen.
- **Enemy roster seed** is per contract (`c.foe`, lazily `c.id·7919 + 17`), so the forecast is stable
  before dispatch and cannot be rerolled. The battle rng seed is drawn at dispatch.
- **Betrayal** (campaign external companies) is rolled at muster and stored as a hidden flag in the spec;
  loyalty change and log line stay at resolve. The forecast ignores it.
- **The sim runs at resolve**, not at dispatch, so the record is produced by the engine that replays it.
- **Replay**: `play()` reruns the spec headless first (one 46 ms run, against `findBattle`'s 131 ms mean)
  and compares `hash`. If `Battle.VER` or the hash differs it goes straight to the report: a battle that
  contradicts the settled result is never shown. Any sim-affecting change bumps `Battle.VER`.
- **The spoiler guard and report slot (`js/ui.js:311-405`) need no change**: state is still mutated at
  resolve and playback still comes later.

```js
mission.spec = {
  v: 1, seed: 482910233, terrain: 'forest', rule: 'field', limit: 90, lv: 5, k: 0.92,
  groups: [
    { side: 0, kind: 'own', companyId: 12, name, color, cohesion: 80,
      units: [{ id: 31, named: '레온', cls: 'warrior', job: 'paladin', trait: 'brave', leader: true, unique: true,
                st: { hp: 252, atk: 41, def: 12 }, sk: [...], look, art, capKey, heroKey }] },
    { side: 0, kind: 'ext', companyId: 40, betray: false, units: [...] },
    { side: 0, kind: 'support', units: [...] },
    { side: 1, kind: 'foe', units: [{ mon: '들늑대', arch: 'beast', rank: 'big', scale: 2, st: {...} }] },
  ],
};
mission.est = { R: 1.34, band: 3 };

report.battle = {
  ver: 3, winner: 0, t: 31.4, end: 'rout',            // 'wipe' | 'rout' | 'retreat' | 'time'
  // one row per unit in spec order: [fate, hp%, downTick, dealt, taken, kills, healed]   fate 0 ok, 1 down, 2 fled
  units: [[0, 42, 0, 812, 301, 2, 0], [1, 0, 412, 96, 180, 0, 0]],
  hash: 0x9a3f11c2,                                   // FNV of winner, end tick, fates
};
report.verdict = { outcome: 'success', won: true, down: 1, standing: 3, mvp: 31 };
```

Tactics preferences are **not stored**: the spec carries their inputs (`cls`, `job`, `trait`, `capKey`,
`cohesion`) and the sim derives them from static tables.

### Win rule per contract type

New field `QUEST_TYPES[type].rule` (`js/data.js:76`):

| rule | types | win when |
|---|---|---|
| `field` | hunt, explore, magic, raid, siege, sabotage, rescue, counterspy, battle, boss, final | the enemy has no active group before the limit; the limit is a loss |
| `hold` | defense, warDefense, escort, envoy | the enemy is broken, or our side is still active at the limit |

This replaces "higher hp sum wins at 90 s" (`js/battle.js:1097-1099`), which favours high-hp bosses once
stats are real. It touches 1.3% of battles today.

## 6. Tiers, casualties, mercy

"Ours" = members of dispatched own and external companies. Support and fill-in trainees never count.

| Tier | Rule |
|---|---|
| great | won, nobody of ours down, every one of ours at ≥ `GREAT_HP` of hp (start 0.5; `mods.great` relaxes it to `0.5 / mods.great`) |
| success | any other win |
| fail | lost, at least one of ours on their feet (standing or fled) |
| disaster | lost and nobody of ours on their feet; `mods.noDisaster` turns it into fail |

Tier multipliers stay as today (exp 1.5 / 1 / 0.5 / 0.3, morale +6 / +2 / −6 / −12, gold, rep, standing,
cohesion), so the consumers in `js/contract.js:364-493` and `js/company.js:268` read the same four words.

Tier mix by capability ratio (resolution sweep, today's engine, n = 230; to be re-measured in stage 3):

| R | great | success | fail | disaster |
|---|---|---|---|---|
| 1.67 | 70% | 30% | 0 | 0 |
| 1.25 | 26% | 72% | 1.2% | 0.8% |
| 1.00 | 3% | 49% | 39% | 9.5% |
| 0.80 | 0 | 2% | 76% | 22% |

Casualties come from what happened:

| Fate | Consequence |
|---|---|
| down, battle won | injury p = 0.6 × `mods.injury` (×0.5 sturdy / coward / northknight), 2-4 days |
| down, battle lost | injury p = 0.9 × `mods.injury`, 2-4 days (+2 on disaster); a downed captain on disaster is always injured |
| standing under 25% hp | light injury p = 0.3 × `mods.injury`, 1-2 days |
| fled | nothing extra |

### Mercy rules (in this order)

1. **Death only on disaster** (nobody of ours on their feet).
2. **Only units that actually went down; never captains** (`js/contract.js:399` stays).
3. p = 0.3 × `mods.death` × 0.6 if sturdy (today's numbers).
4. **At most one death per own company per battle.**
5. **Guild floor**: a death that would leave the guild under 3 mercs becomes an injury (the `empty` game
   over needs this).
6. **Retreat** (new sim rule, our side only): when at least `RETREAT.down` (start 0.5) of ours are down
   and our remaining hp is under `RETREAT.ratio` (start 0.5) of the enemy's remaining hp, everyone of ours
   still up runs for the edge and counts as `fled`; the battle ends as a loss with `end: 'retreat'`. Shown
   by motion only (the routed run already exists, :949-954). It applies to `field` and `hold` contracts
   alike. Enemies keep today's group rout rule (:932-941).
7. External companies: `lost` = their downed units, each kept with 50% on a lost battle, cap 2, none on a
   win (replaces the tier roll in `extAfterMission`).

Measured deaths per defeat on real fates: today's formula applied naively 0.78 (max 6); **rules 1-4:
0.10, at most 1**. Rule 6 is not prototyped; without it 75-78% of ours are injured after any defeat
(today's "fail" is 25%), so it is a gate for the switch (section 11, S4).

## 7. Forecast

`Game.forecast(contract, units)` musters without a battle seed and returns `{ R, band }`.

- `R = Stats.margin(spec.groups) × CAL_KIND[enemy kind]`. `margin` is analytic: per side, Σ dps (with the
  ratio-defence term against the other side's mean DEF) × (Σ effective hp + heals over the expected
  length), solved for the enemy multiplier at parity. Microseconds per call, so the "rough difficulty"
  fallback is not needed.
- **It reads sheets and skill rates only**: no positions, no preferences, no synergy, no seed, no betrayal.
- **R = 1 means a 50% win for a plain company** (captain fit 0). That is the owner's "median".
- Accuracy so far: correlation 0.83 with simulated k50 over 24 scenarios, spread ±15% (1 sd); in bot games
  0.51 against 0.38 for `pw/req`. By captain style it is off by 1.04 (warrior) to 1.23 (mage). Stage 3
  first fixes the skill-shape weights inside `margin` (aoe, ranged uptime); a `CAL_STYLE` table is the
  last resort. Gate: residual log-sd ≤ 0.10, every kind and style median within ±5%.

| Band | R | Win, forecast-blind (today's engine) |
|---|---|---|
| 무모 | < 0.67 | 0.5% |
| 열세 | 0.67-0.87 | 14% |
| 백중 | 0.87-1.15 | 51% |
| 우세 | 1.15-1.5 | 86% |
| 압도 | ≥ 1.5 | 99% |

Band edges are data and are re-fitted in stage 3 (the stat engine's curve is steeper).

Dispatch screen (`js/ui-tabs.js:325-340`): the band word and a bar placed by log R replace "총 전투력 /
권장" and "예상 성공률 N%". The "인원 부족" and "피로한 단원" lines are deleted (owner: no warnings);
fatigue stays on the member chips. "권장 전투력" on the contract card (:181) becomes the enemy level.

Recruitment counters (`js/captains.js:33-37`) read the frozen `mission.est` instead of `mission.chance`:

| Counter | Today | New | Condition text |
|---|---|---|---|
| hardStreak | chance < 0.8 | band ≤ 백중 (R < 1.15) | "예상 「백중」 이하 의뢰 연속 성공" |
| gambles | chance < 0.4 | band ≤ 열세 (R < 0.87) | "예상 「열세」 이하 의뢰 성공" |
| bigGambles | chance < 0.25 | band = 무모 (R < 0.67) | "예상 「무모」 의뢰 성공" |

Visible (the word is on the dispatch screen) and decidable (`est.R` is stored, the edges are constants).
A 무모 fight is won 0.5% of the time before tactics, so `titan` (1 bigGamble) and `shadowqueen`
(8 gambles) are retuned in stage 5 from the measured tactics upside (`js/content.js:391-416`).

## 8. Tactics hooks

Principle: **tactics add, they do not subtract.** A plain company fights at the forecast; a well-built
one beats it. Nothing on the dispatch screen points at a weakness, and nothing in the battle is captioned.

### 8.1 Preference data (`js/tactics.js`, pure tables)

```js
// depth: px behind own line | chase: px ahead of the line it will pursue | hold/protect/flank: 0..1 | pin: foes it can hold
TAC_ROLE = {
  guard:   { depth: 0,  chase: 10, hold: 1.0, protect: 1.0, flank: 0,   pin: 2 },
  bruiser: { depth: 0,  chase: 22, hold: 0.6, protect: 0.4, flank: 0.2, pin: 1 },
  striker: { depth: 0,  chase: 40, hold: 0.1, protect: 0.1, flank: 1.0, pin: 0 },
  shooter: { depth: 30, chase: 0,  hold: 1.0, protect: 0,   flank: 0,   pin: 0 },
  caster:  { depth: 34, chase: 0,  hold: 1.0, protect: 0,   flank: 0,   pin: 0 },
  healer:  { depth: 42, chase: 0,  hold: 1.0, protect: 0,   flank: 0,   pin: 0 },
  brute:   { depth: 0,  chase: 14, hold: 1.0, protect: 0,   flank: 0,   pin: 2 },   // big monsters
  pack:    { depth: 0,  chase: 40, hold: 0.2, protect: 0,   flank: 0.6, pin: 0 },   // beasts
};
TAC_JOB      // class key -> role; unlisted keys fall back to the skill shape
TAC_TRAIT    = { brave: { chase: +8, protect: +0.2 }, coward: { chase: -6, depthBack: +8 }, sturdy: { hold: +0.2 } };
TAC_DOCTRINE // captain style -> roles it brings out; per-captain override CAPTAIN_CLASSES[k].doc
TAC_K        = { steady: 0.30, healSteady: 0.5, cdFloor: 0.5, brace: 0.20, braceCap: 0.5, flank: 0.40, amp: 2.5, ... };
```

Sources of a unit's preference, in order: class (role) → trait (delta) → captain (doctrine). No picker.

### 8.2 Where they plug in

| Hook | Place (`js/battle.js`) | Stage |
|---|---|---|
| Deploy in rows by preferred depth | end of `setup` (:678) | 2 |
| Line cohesion before contact (replaces the pull to the captain) | :1012-1021 | 2 |
| Back line stands, steps up, back-pedals; healer drifts to the hurt | :965-980 and the ranged part of :981-1029 | 2 |
| Melee target score (engaging me, threat to my back-liner, chase limit, flank) | :989 | 2 |
| Engage rule: a passing melee enemy is held for 2 s (target switch only) | new `tacTick`, before :942 | 2 |
| Flankers may use the two rear melee slots | :707, :728-731 (`MELEE_SLOTS` :26) | 2 |
| Steady fire: cooldown multiplier | `useSkill` :873 | 5 |
| Brace: incoming multiplier | `damage` :798 | 5 |
| Flank strike: outgoing multiplier | `strike` :815 | 5 |

Constraints inherited from C1 (walker yields): tactics never displace a unit; they act only through the
unit's own goal point, target choice, or a scale on its own step, and all movement goes through `steer()`
(:744). Measured shoved share with the layer on: 0.00%.

### 8.3 The three earned states (stage 5)

| State | Earned when | Effect | Seen as |
|---|---|---|---|
| Steady fire | back-liner unthreatened for 1 s with an allied front unit ahead; stacks to 4, reset by any threat | cooldown / (1 + 0.30 × amp × stacks/4), floor 0.5 s; healers ×0.5 | planted shooters loose faster |
| Brace | holding front unit, engaged, standing still, covering a back-liner or beside another standing front ally | damage taken × (1 − min(0.5, 0.20 × hold × amp)) | the line stands shoulder to shoulder |
| Flank strike | melee hit on a foe whose target is another ally | × (1 + 0.40 × flank × amp) | rogues circle behind a held enemy |

Captain fit: `W` = sum of the doctrine weights of the non-captain members; `fit = clamp((W − 1) / 1.5, 0, 1)`;
`amp = 1 + 2.5 × fit`. **The first matching member is free**, so the median real company is the plain one
(bot companies: 55% at fit 0, 37% partly fitted, 8% full).

Who earns what:

| Side | Movement and engage rule | Base states | Captain amp |
|---|---|---|---|
| Own company with a captain | yes | yes | yes |
| Own company without a captain, external company | yes | yes | no (amp 1) |
| Support | yes | no | no |
| Enemies | yes | no | no |

Measured (tactics prototype on the stat engine, Lv10, one company vs one group; E = k50 with synergy /
k50 without):

| Company | fit | E at amp 2.5 | Damage share from synergy (dealt / removed, amp 4) |
|---|---|---|---|
| 29 plain companies | 0 | 1.00 (0.96-1.05) | — |
| warrior + W W A | 0.67 | 1.16 | 12% / 47% |
| archer + W A A | 1 | 1.17 | 37% / 19% |
| mage + W M M | 1 | 1.12 | 38% / 17% |
| rogue + W R R | 0.67 | 1.16 | 38% / 1% |
| cleric + W W C | 0.67 | 1.33 | 0% / 43% |

Movement alone changes strength by ×0.86 to ×1.03 (median 0.97) and moves "first ally death is a
back-liner" from 39.9% to 0.0%.

## 9. Conflicts between the designs, and what I chose

| # | Conflict | Chosen | Why |
|---|---|---|---|
| 1 | Frozen input: compact record regenerated by `Stats.fill` (stats) vs a full `mission.spec` (resolution) | **Full spec** | Judge and replay must read identical inputs (accepted GPT note); a regenerated roster changes with any table edit. Cost is 3.3 KB per in-flight mission, and it replaces `report.companies` (2.3 KB). |
| 2 | Freeze moment: "at the freeze point" (stats) vs at dispatch (resolution) | **Dispatch**, before dispatch fatigue | The player fights with the numbers the forecast showed. Needs the equip guard. |
| 3 | Forecast formula: `Stats.margin` (stats) vs `sqrt(Σhp·Σdps)` ratio with K per kind (resolution) | **`margin`, normalised to R by `CAL_KIND`** | `margin` already models DEF, pierce and heals on the stat engine (corr 0.83). Resolution's per-kind constant and band scale are kept. |
| 4 | Band scale: margin bands 0.8 / 0.95 / 1.05 / 1.2 (stats) vs R bands 0.67 / 0.87 / 1.15 / 1.5 (resolution) | **R bands**, R = 1 is 50% | The owner asked for the median; stats' bands were tied to one `ENEMY_K`. Edges re-fitted in stage 3. |
| 5 | Name clash: "fit" = quest-type bonus (stats) and "fit" = captain doctrine (tactics) | Stats' part is renamed **`apt`** | One word, one meaning. |
| 6 | Captain aura ×1.1 (:789-793): keep (stats) vs delete (tactics) | **Keep through stage 4, delete in stage 5** with the amp | It is the same idea as the amp; removing it earlier would need a calibration of its own. |
| 7 | Do enemies earn the synergy states? | **No**: allies only | With enemies on, the worst company is 0.96; allies-only keeps every company ≥ 1.00 before calibration. That is "reward, not punish". |
| 8 | `plan()` stays in `battle.js` (stats, tactics) vs moves to the management side (resolution) | **Moves**: `Game.muster` in new `js/muster.js`; `soldierLook` (`js/ui.js:41`) to `js/world.js` | Forecast and bot need the roster without the renderer or a UI stub. Possible now because C2 is merged. |
| 9 | Unit stat field name and speed: `st {hp, atk, def}` vs `stat {…, spd}` | **`st {hp, atk, def}`**; speed stays a class / archetype constant | Two of three prototypes use `st`; fewer stats. |
| 10 | Three "smallest first slices" (record plumbing, stat shadow, movement) | All three, in the order **plumbing → stats shadow → movement** | Plumbing makes the other two measurable; the owner's ask is stats first; movement must precede calibration because it shifts k50 by up to 14%. |
| 11 | Retreat: resolution needs it for mercy, tactics defers morale | **A minimal side-level retreat ships with the switch**; group morale and momentum stay later | Without it every defeat costs like today's disaster. |
| 12 | Exp extras (MVP, kills, underdog) | **Stage 5, optional** | Not skeleton. Tier multipliers are enough for the switch. |
| 13 | "30-50%": which scale | **Damage share** is the stated target; the difficulty scale is the guard (+15% to +27%, about one band) | Forcing +30-50% on the difficulty scale needs halved cooldowns and halved damage together and makes the forecast unreliable. Owner question 2. |
| 14 | Cond stack (median 1.52, p90 2.02): compress or keep | **Keep 1:1** in the skeleton | Management systems keep their value; late-game ease is handled by `ELV` first. Re-open only if stage 3 gate fails. |

## 10. Save migration (stay on version 4)

| Saved item | Old save has | Handling |
|---|---|---|
| Merc | no new fields needed | sheets are derived, never stored |
| Item | no `def` | derived from base and tier |
| `s.missions[]` | `chance`, no `spec` / `est` | muster at resolve from the current state; counters fall back to the old `chance` thresholds |
| `s.pendingReports[]`, `s.reportSlot` | outcome rolled, no `battle` | legacy `findBattle` replay until stage 6, then straight to the report |
| Contract | no `foe` seed | lazy `c.id·7919 + 17` |
| Engine update with reports pending | `battle.ver` older | skip the replay, show the report |

A fixture save for each row goes into the test tool (invariant I10).

## 11. Measurement plan

Codex runs the sweeps and reports tables; the lead picks the constants. Every sweep prints its command,
seeds, commit and run time. Sweeps run on the shadow engine (stages 1-3), so the game does not change
while numbers are being chosen.

| Sweep | Varies | Reads | Decides | Target |
|---|---|---|---|---|
| S1 pacing | `K` ∈ {0.25, 0.20, 0.18, 0.16} | battle length median / p90, share ≥ 60 s, ms per sim | `K` | median 18-25 s, p90 ≤ 45 s, ≥ 60 s under 2% |
| S2 difficulty | `ENEMY_K` ∈ {0.7 … 1.0}, `SUPPORT_K` ∈ {0.4, 0.6, 0.85}, `ELV` late rows (+1 vs +2 per star from ★8), `KIND_K` per special kind, archetype rows | shadow win rate by day band, star, kind, archetype; own share of ally capability; margin by star | those constants | see gates below |
| S3 forecast | — (fit) | k50 vs `margin` on the panel; win rate and tier mix per band | `CAL_KIND`, skill-shape weights, band edges, `GREAT_HP` | residual log-sd ≤ 0.10; kind and style medians within ±5%; win rate monotonic across bands |
| S4 mercy | `RETREAT.down` ∈ {0.4, 0.5, 0.6}, `RETREAT.ratio` ∈ {0.35, 0.5, 0.7} | share of defeats with half of ours on their feet; injuries per defeat; deaths per defeat; win rate at R ≥ 1.15 | `RETREAT`, injury p | ≥ 60% of defeats keep half of ours up (today 1-2%); disaster ≤ 10% of defeats at R ≥ 0.87; win rate at R ≥ 1.15 moves under 2 points |
| S5 tactics | `TAC_K` (amp 2.5 / 4, healSteady, brace), fit rule | panel: E per company, damage share, cue rates, worst E, length | `TAC_K`, recalibrated `CAL_KIND` | gates G1-G6 below |
| S6 game-level | the chosen set, 12 seeds × 365 days, bot dispatching at band ≥ 우세 (campaigns ≥ 백중) | tier mix, injuries, deaths, rank reached, gold curve, win by special kind | go / no-go for the switch | see gates below |

Gates for the switch (S2 + S6, all with a bot that dispatches at band ≥ 우세). The levels are proposed
targets that keep today's difficulty; owner question 3 confirms or moves them:

| Number | Today | Gate |
|---|---|---|
| Win rate of dispatched contracts | 95.0% | 93-97% |
| Great share | 28.1% | 25-40% (else raise `GREAT_HP`, then harden late stars; cutting the great bonus is the last option) |
| Win rate, days 1-30 | — (shadow: 56-67%) | ≥ 85% |
| Offers in days 1-30 that the starting roster can take at ≥ 우세 | 98.8% of offers are taken today | ≥ 60% |
| Boss / hero story / captain story / campaign win | 92 / 89 / 88 / 96% | each ≥ 85% when dispatched at ≥ 우세, and ≥ 80% of them reachable at 우세 within their window |
| Final contract | 67% | 55-75% |
| Deaths per 365-day game | 0 | median 0, max ≤ 2 |
| Injury rate per own unit per battle | 3.4 / 9.6 / 25.3% by tier | 5-12% overall |
| All 12 seeds reach rank S | yes | yes |
| On-level company three levels under | — | costs ≥ 12% of strength (support must not hide it) |
| ms per battle | 46-50 | mean ≤ 100, max ≤ 300 |

Tactics gates (S5, `tools/sim/tactics.js`; panel = 5 captain styles × 10 member mixes × enemy kinds ×
levels 5 / 10 / 20 × 1-3 groups, about 80 s on 4 cores):

| Gate | Check |
|---|---|
| G1 | plain (fit 0) median E within 0.97-1.03 per enemy kind after calibration |
| G2 | lowest E on the panel ≥ 0.97 |
| G3 | fit ≥ 0.67 companies: damage share from synergy 30-50% (dealt or removed), E within 1.15-1.30 |
| G4 | no doctrine's upside more than 1.5× another's (cleric is 1.33-1.50 now; rogue stat-only strength is the lowest) |
| G5 | cues: brace ≥ 30% of front time, steady ≥ 50% of stacks, first death is a back-liner ≤ 5% |
| G6 | battles ≥ 60 s under 2%; ms per sim reported |

Known numbers that will need a decision from this data: master skills were never balanced as damage
(Lv30 swordsaint 103 dps vs smuggler 8); armoured / beast / blob are easier than grunt (k50 1.67-1.69 vs
1.50); late stars add about 7% per star while `req` grows ×1.4.

## 12. Test invariants (replace "mismatch = 0")

`tools/sim/battle.js` is rewritten around these; each must have 0 violations.

| # | Invariant | From stage |
|---|---|---|
| I1 | Determinism: the same spec gives the same hash run twice, after a JSON round trip, and stepped the way `play()` steps | 0 |
| I2 | No unit's fate changes after `over` | 0 |
| I3 | `report.battle.hash` equals a rerun of `report.spec`; `report.verdict` equals `judge` recomputed | 4 |
| I4 | Casualties: dead ⊆ down; no dead captain; ≤ 1 death per company; injured ⊆ down ∪ low-hp; guild never under 3 by death | 4 |
| I5 | Forecast is monotonic: win rate does not fall from one band to the next; 압도 ≥ 97%, 무모 ≤ 5% | 3 |
| I6 | Forecast purity: `Game.forecast` is identical with `TAC_K` zeroed and with any battle seed; `mission.est` equals the forecast at dispatch | 3 |
| I7 | Freeze: changing morale, gear or standing after dispatch does not change the result hash | 4 |
| I8 | Tactics floor: no panel company under E 0.97; plain median within 0.97-1.03 | 5 |
| I9 | Limits: time-limit battles under 2%; mean ms per battle ≤ 100 | 0 |
| I10 | Old saves: fixtures with a spec-less mission, a battle-less pending report and an open report slot load and resolve without an exception | 4 |

Until stage 6 the old check (`findBattle` reproduces all four outcomes, mismatch 0) keeps running for the
legacy path. The bot md5 gate (`SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum`, `docs/agents/README.md`)
stays a regression gate: unchanged through stage 3, one new baseline at stage 4, one at stage 5.

## 13. Staged plan

Who: **lead** = cloud Claude (core engine). **Codex** = tests, sweeps, small fixes, on `agent/codex`.
**Antigravity** = playtest. GPT-QA verifies Codex's work as today.

### Stage 0 — one record, one input (no behaviour change)

- **0a**: `Battle.run(spec)` returns the full record (per-unit fate, hp%, dealt, taken, kills, healed,
  `end`, `hash`); shots fizzle after `over`; export `setup`, `step`, `VER`.
- **0b**: `plan()` moves to `Game.muster` (`js/muster.js`), `soldierLook` to `js/world.js`; units carry
  `id`, `job`, `trait`; groups carry `kind`, `companyId`, `cohesion`; `report.spec` is built where
  `report.seed` is drawn (`js/contract.js:361`); `play()` reads it.
- Files: `js/battle.js` (:537-623, :1078-1120, :2648, :2791), `js/muster.js` (new), `js/world.js`,
  `js/ui.js:41`, `js/contract.js:361`, `index.html`, `tools/sim/battle.js`, `tools/sim/bot.js:14`.
- Accept: bot md5 identical; `tools/sim/battle.js 100` mismatch 0; I1, I2, I9 at 0; 400 replays hash-equal
  before and after the move.
- Who: lead (0a, 0b); Codex (invariant tool, before / after hash comparison).
- Undo: revert.

### Stage 1 — the stat sheet, in shadow

- `js/stats.js` (about 200 lines, pure): `raw, sheet, enemy, generic, scale, margin` and the constants.
  `ENEMIES[*].arch`. `muster` fills `st` on every unit. `setup` reads `st` and `strike` uses the ratio
  term **only in real mode** (`setup(spec, { real: true })`); the roll still decides and playback stays
  on the old path.
- Merc card shows HP / ATK / DEF and the condition chip (`js/ui.js` :158, :277).
- `tools/sim/probe.js`: for every bot report, what the battle would have decided.
- Files: `js/stats.js` (new), `js/battle.js` (:641-664, :798, :815-840), `js/content.js` (:9-41),
  `js/muster.js`, `js/ui.js`, `index.html`, `tools/sim/bot.js:14`, `tools/sim/probe.js` (new).
- Accept: bot md5 identical; mismatch 0; the worked example reproduces (84% hp left, 11.7 s);
  `Stats.sheet` table matches section 2 for the listed classes; probe prints the shadow win table.
- Who: lead (stats.js, hooks); Codex (probe tool, table tests, card UI check at 1280 and 400 px).
- Undo: revert; nothing saved.

### Stage 2 — movement by preference (visual only)

- `js/tactics.js` roles, doctrine and trait tables; deploy by depth, back line, line cohesion, target
  score, engage rule, flank slots. All synergy coefficients 0. Neighbour culling in `tacTick`.
- Files: `js/tactics.js` (new), `js/battle.js` (hooks in 8.2), `index.html`, tool file lists.
- Accept: mismatch 0 on the legacy path; bot md5 identical; first death is a back-liner ≤ 5% (from about
  40%); shoved share < 0.1%; `findBattle` mean ≤ 1.5× HEAD; ms per battle ≤ 100; no drawn art is deformed
  and movement stays the running gait (back-pedal uses the existing `back` gait).
- Who: lead; Codex (cue counters and the four measurements); Antigravity (playtest: does a line form,
  any jitter or sliding, any unit facing the wrong way).
- Undo: revert, or `TAC_ON = false`.

### Stage 3 — calibration (no player-facing change)

- Retreat rule and `hold` / `field` rule implemented in real mode. `Game.forecast` and `Game.judge`
  exist and run in shadow next to the roll; the bot prints agreement.
- Codex runs S1-S4 and S6; the lead fixes `K`, `ENEMY_K`, `SUPPORT_K`, `ELV`, `KIND_K`, archetype rows,
  `CAL_KIND`, band edges, `GREAT_HP`, `RETREAT`, injury p. Result written to
  `docs/plans/stats/calibration_1.md`.
- Files: `js/stats.js` constants, `js/battle.js` (:932-941 retreat, :1092-1103 end rule), `js/data.js`
  (`rule`), `js/muster.js`, `tools/sim/probe.js`, `tools/sim/bot.js` (shadow columns).
- Accept: every gate in section 11 (switch gates) met in shadow; I5, I6 at 0; bot md5 identical.
- Who: Codex (sweeps); lead (decisions, constants).

### Stage 4 — the switch: the battle decides

- Flag `RESOLVE = 'battle'` (constant in `js/contract.js`, not saved): freeze at dispatch, equip guard,
  `Battle.run` at resolve, `judge`, casualties and mercy from fates, `extAfterMission(lost)`, replay from
  the spec with the hash check, forecast band on the dispatch screen, recruitment counters on `est`, bot
  dispatch by band. The `doomed` weakening and skull are off in real mode.
- Files: `js/contract.js` (:262-327 dispatch, :332-493 resolve), `js/game.js` (:592, :603), `js/company.js`
  (:268), `js/captains.js` (:5, :33-37), `js/content.js` (:386-416 texts), `js/ui-tabs.js` (:181, :222,
  :325-340), `js/battle.js` (`play`), `tools/sim/*`.
- Accept: I1-I7, I9, I10 at 0; S6 gates met with the real path; new bot md5 baseline recorded; with the
  flag at `'roll'` the old md5 still reproduces.
- Who: lead; Codex (invariants I3, I4, I7, I10, fixtures, bot changes); Antigravity (playtest A2: two
  runs of about 100 days — how often it lost, whether the band matched what happened, any merc who looked
  fine in the battle but is listed hurt, or the reverse).
- Undo: flag back to `'roll'` (spec and chance are both stored while the flag exists).

### Stage 5 — tactics upside

- Steady fire, brace, flank strike for own and external companies; captain-fit amp; aura ×1.1 deleted;
  `CAL_KIND` re-fitted so a plain company's median realised / forecast is 1; `tools/sim/tactics.js` with
  G1-G6; recruitment thresholds retuned from the measured upside. Optional: MVP and underdog exp
  (`exp × (1 + 0.15·MVP + 0.10·kill) × clamp(1/R, 1, 1.3)` on a win).
- Files: `js/tactics.js`, `js/battle.js` (:789-793, :798, :815, :873), `js/stats.js` (`CAL_KIND`),
  `js/content.js`, `tools/sim/tactics.js` (new).
- Accept: G1-G6; I8; S6 gates still met; second md5 baseline.
- Who: lead (states, amp); Codex (panel tool, S5); Antigravity (playtest: can the three states be read
  from motion alone, without text).
- Undo: `TAC_K` coefficients to 0.

### Stage 6 — cleanup

- Delete `findBattle`, `bias`, `SLOW_T`, `doomed`, `successChance`, `mission.chance`, the legacy replay,
  `ATK_SCALE`, `HEAL_POWER`, `MONSTER_STATS`, the hp / atk columns of `CLASS_STATS`, and `power()` /
  `unitsPower` once the external gold share (`js/contract.js:366`) and bot sorting read sheets. Update
  `docs/DESIGN.md` (:234-236, :252, :286) and `README.md` (:82-83).
- Accept: all invariants; md5 unchanged against the stage 5 baseline; the old-save fixtures still load.
- Who: Codex (deletions, docs) with lead review.

### Later, outside the skeleton

Group morale and momentum (rout thresholds only), monster pack behaviours, a post-battle "fought above
the forecast" line, master-skill damage rebalance, enemy headcount by contract size, a kill-the-leader
win rule, per-captain doctrine overrides.

## 14. Risks

- **Great inflation.** At R ≥ 1.67 great is 70%, and 65% of today's bot dispatches sit above margin 1.2.
  If late contracts stay easy, gold and rep ×1.5 become the norm. Guarded by the 25-40% gate.
- **The forecast reads as the result** outside about ±10% of parity. The owner's 30-50% only shows if the
  tactics upside survives calibration; G3 is the check.
- **The forecast error (log-sd 0.11) is as large as a plain company's tactics effect.** Until it is under
  0.10, a "fought better than expected" line would mostly show forecast error, so it is not in the plan.
- **Movement lowers back-standing captains.** Against HEAD movement, mage- and cleric-captain companies
  lose up to 14% (×0.86) because the captain now stands back. With a per-kind calibration only, they
  would fight below their forecast, which reads as a punishment. The S3 style gate (±5%) must catch it;
  the fixes are the skill-shape weights in `margin` or a shallower captain depth.
- **Retreat is unprototyped.** If S4 cannot meet its target without costing wins, the fallback is a lower
  injury chance on lost battles (0.9 → 0.5) and the switch still ships; deaths are already capped.
- **Every rule change needs the per-kind calibration rerun**; it is a tool (S3), not a one-off.
- **Cleric doctrine dominates** (E 1.33-1.50, battles 33-36 s). `healSteady` is the knob; G4 is the check.
- **`lead.cls` and the captain amp both reward one-class stacking.** Measured in S5 before either changes.
- **Bot run time** grows from 17 s to about 7 min for 12 × 365. The md5 gate uses `bot.js 6 200` with
  seeds in parallel.
- **Not prototyped at all:** `aid`, derived item DEF for uniques, the retreat rule, trait deltas beyond
  three, UI.

## 15. Evidence

- Map and measurements: /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/map/
- Stat sheet prototype (`stats.js`, `patch_battle.py`, `rating.js`, `t_bot.js`, `out_*.txt`): /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/design_stats/
- Resolution sweeps (`sweep.js`, `analyze*.js`, `sweep_*.json`, `perf.js`): /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/resolution/
- Tactics prototype (`tac_block4.js`, `patch_tac4.py`, `sweep2.js`, `v4_*.jsonl`, `repro_*.txt`): /tmp/claude-0/-home-user-pixel-management/e0835d66-bd95-539c-bed6-4bd85f4f7ab9/scratchpad/stats/tactics/
- Earlier tactics decision: `docs/plans/tactics/2026-11-26_tactics_decision.md`; separation: `docs/plans/jostle/README.md`.

This document re-measured nothing. Every number is quoted from the three designs and the map; the only
new check is the set of HEAD `607f23d` line anchors, found by grep.
