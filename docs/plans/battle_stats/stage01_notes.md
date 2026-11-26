# Battle stats, stages 0 and 1: what is in the tree (shadow mode)

Date 2026-11-26. Base commit `a884fb4`. Spec: `design.md`; where it disagrees with `verify_findings.md`, the
amendments were followed.

## State

The skeleton is in and runs in shadow. The contract result is still the roll (`successChance`), and the watched
battle is still the `findBattle` replay. The only thing a player can see is one new line on the merc card.

- Bot md5 (`SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum`) is `ddfdfe7b437fbe9fcf25f166ba542fce`, the same as
  before, with the shadow battle running at every resolve.
- The legacy replay path is bit-identical: 126 reports × 3 sims give the same bias, seed, result and length as HEAD.
- 3,871 shadow battles (6 seeds × 365 days): 0 determinism violations, 0 enemy rosters changed by the party,
  0 `Math.random` calls and 0 state changes inside muster or the shadow battle.
- With the feasibility knobs (`SUPPORT_K=0.6 GREAT_HEADS=0 AID_CAP=1`) the tables of `feasibility.md` come back:
  win 89.0% (89.0%), tiers 72/17/11/0 (73/16/11/0), day bands 57/51/79/98/100% (58/52/76/98/100%).
- The design's worked example reproduces: 100% wins, 11.7 s, 84% ally hp left over 40 seeds.

The start constants are known to be off and were kept on purpose. With the defaults below the shadow win rate is
83.4% over 365 days and 47 / 36 / 65% in days 1-30 / 31-60 / 61-120. Calibration is the next task.

## What was built

| File | What |
|---|---|
| `js/stats.js` (new, pure) | `Stats.sheet / raw / parts`, enemy tables `REF × ARCH × RANK`, `enemy`, `generic`, `scale`, `ruleOf`, `margin`, `forecast`, `judge`, `rng`, `mix`, knobs `Stats.KN` |
| `js/muster.js` (new) | `Game.muster` (freeze), `Game.forecast`, `Game.judge`, `Game.freezeMission` (dispatch hook), `Game.shadowResolve` (resolve hook), flags `shadowBattle`, `equipGuard` |
| `js/battle.js` | `setup(groups, bias, seed, real)`; ratio defence, retreat, fizzling shots and the field/hold end rule, all only when `real`; `Battle.run / begin / record / step / setup / VER` |
| `js/contract.js` | two hook lines: `freezeMission` in `dispatch`, `shadowResolve` in `resolveMission` |
| `js/game.js` | `equip` / `unequip` refuse a merc with `status === 'quest'` |
| `js/content.js`, `js/data.js`, `js/world.js` | `ENEMIES[*].arch`; `QUEST_TYPES[*].rule = 'hold'` on defense, warDefense, escort, envoy; `factionSoldierLook` (moved from `js/ui.js`) |
| `js/ui.js`, `css/style.css` | merc card line: 전투 체력 · 공격 · 방어 and the chip 컨디션 ×N |
| `tools/sim/shadow.js` (new) | sweep and invariant tool |
| `tools/sim/bot.js`, `tools/sim/battle.js` | load the new files; hooks `onStart`, `onOffer`; options `shadow`, `equipGuard` |

## Data shapes

```js
mission.spec = {                 // frozen in dispatch(), before the dispatch fatigue; about 4.5 KB of JSON
  v: 1, seed, terrain, rule: 'field' | 'hold', limit: 90, lv, k,      // lv, k: enemy level and multiplier
  need, heads,                   // contract.size and heads sent (the great rule reads them)
  groups: [
    { side: 0, kind: 'own', companyId, name, color, player: true, cohesion,
      units: [{ id, named, look, cls, job, trait, level, leader, unique, sk, art, capKey, heroKey,
                st: { hp, atk, def }, mul }, { look, cls, recruit: true, st }] },      // recruit = fill-in trainee
    { side: 0, kind: 'ext', companyId, name, color, player: true, ext: true, level, units: [{ look, cls, leader, st }] },
    { side: 0, kind: 'support', name, color, units: [{ look, cls, st }] },
    { side: 1, kind: 'foe', name, color, units: [{ mon, arch, rank, scale, boss, bigMon, st } | { look, cls, rank, st }] },
  ],
};
mission.est = { R, band };       // band 0-4: 무모 열세 백중 우세 압도

Battle.run(spec) -> {            // the record
  ver: 1, tab,                   // Battle.VER and a digest of the tables read outside the spec
  winner: 0 | 1, t, ticks, end: 'wipe' | 'rout' | 'retreat' | 'time',
  units: [[fate, hp%, downTick, dealt, taken, kills, healed], ...],   // spec order, integers; fate 0 ok, 1 down, 2 fled
  hash,                          // FNV-1a of winner, ticks, end and every row value
};
Stats.judge(spec, rec, mods) -> { outcome, won, ours, down, standing, fled, low, mvp };

report.shadow = { v: 1, ver, tab, seed, hash, winner, t, end,          // about 170 bytes, never shown
                  outcome, ours, down, fled, low, R, band };           // or { v: 1, err } if the shadow threw
```

A mission from an old save has no `spec`; `shadowResolve` musters it at resolve from the current state, with
`startDay` in the seed.

## How to run the sweep

```
node tools/sim/shadow.js [seeds=6] [days=200] [--jobs N] [--check] [--offers] [--guard]
     [--set KEY=VALUE]... [--sweep KEY=a,b,c]... [--out rows.json] [--csv rows.csv]
```

- Tables: by `successChance` decile, day band, forecast R, forecast band, enemy kind, archetype, contract kind, star.
- `--set ENEMY_K=0.7 --set KIND_K.story=0.8 --set ARCH.blob.hp=1.6`, or `STAT_KNOBS='{"ENEMY_K":0.7}'`.
  Every key of `Stats.KN` and every cell of `REF`, `ARCH`, `RANK` can be set.
- `--sweep ENEMY_K=0.6,0.7,0.8 --sweep SUPPORT_K=0.4,0.6` prints one summary line per combination.
- `--offers` adds the offers the bot turned down (needed for the deciles under 0.6).
- `--check` runs the invariants and exits 1 on any violation.
- Each row holds: seed, day, ret, star, type, kind, foe, arch, rule, lv, k, chance, rolled, R, band, win, tier,
  t, end, ours, down, fled, low, downShare, hash.
- Cost: about 30 ms per battle; 6 × 365 with `--jobs 4` takes about 45 s.

Other checks: `node tools/sim/battle.js 100` (legacy replay, unchanged), the bot md5 above
(`SIM_SHADOW=0` skips the shadow battle and gives the same md5 in 3 s instead of 60 s).

## Deviations from design.md

| # | Design | Built | Why |
|---|---|---|---|
| 1 | `plan()` moves to `Game.muster`; `play()` reads the spec | `plan()` and `play()` untouched; `muster` has its own copy of the roster rules | Shadow mode must not disturb the replay. The copy goes when `plan()` is deleted in stage 6. |
| 2 | Spec built at resolve in stage 0, frozen at dispatch in stage 4; battle seed drawn with `Math.random` | Frozen at dispatch now; seed = `mix(contract seed, day)` | Amendment 5. A drawn seed would change the bot md5. |
| 3 | One rng for the whole roster | Three streams: foes (contract only), each support group, each company's looks | Amendment 4. The enemy roster is the same for any party. |
| 4 | Betrayal rolled at muster | Still rolled at resolve; the shadow marks a copy of the spec | Rolling earlier would reorder the game's random stream. The enemy group count is not reduced for a traitor. |
| 5 | `aid` is a part of cond (HP and ATK) | `aid` multiplies ATK only, capped at +8% (`AID_CAP`) | Amendment 10. |
| 6 | Trainees: enemy level − 2, ×0.7 | Lowest level among all members of that company, ×0.7 | Amendment 3. |
| 7 | `SUPPORT_K` 0.6 | 0.4 | Amendment 3 (lower the free allies' share). |
| 8 | Great: nobody down and hp ≥ `GREAT_HP` | Also needs `heads >= need` (`GREAT_HEADS`) | Amendment 3. |
| 9 | Hash of winner, end tick, fates | Hash of every row value plus `end`; record carries `tab` | Amendment 8. |
| 10 | Fate "fled" | 2 = the unit fled or its group routed, also on the winning side | Does not depend on how far the unit got before the end. |
| 11 | Rout and betrayal keep running after `over` | Stopped after `over` in stat battles | Without it 2 of 2,150 records changed in the 2.2 s end hold (invariant I2). |
| 12 | Final contract uses the `k` formula | `k = req / 3000` (`FINAL_REQ`) | The design formula saturates at the clamp; amendment 7 asks for a separate scale. |
| 13 | Big monsters keep ×0.85 speed | The archetype speed replaces it | As in the feasibility prototype, so its numbers stay comparable. |
| 14 | `Game.forecast(contract, units)` | `Game.forecast(spec)`; `CAL_KIND` is 1 | The dispatch screen does not call it yet. |
| 15 | Equip guard always on | On in the game; the bot turns it off (`opts.equipGuard`) | HEAD's bot re-equips mercs in flight. With the guard the bot md5 becomes `79f36081…`. |
| 16 | `tools/sim/probe.js`; `tools/sim/battle.js` rewritten around invariants | `tools/sim/shadow.js` holds the tables and the invariants; `battle.js` still checks the legacy path | The legacy check stays until stage 6. |
| 17 | Card shows 체력 공격 방어 and the chip | Same, with a row title 전투 | The card already has an attribute bar named 체력. |
| 18 | apt: mage on magic 1.20, warrior on hunt 1.13 (Lv10) | 1.17 and 1.11 | The feasibility prototype's formula was kept. |

Not built here: `report.spec`, `report.battle`, casualties and mercy from fates, the forecast on the dispatch
screen, recruitment counters on `est`, replay from the spec. `mission.chance` and the roll are unchanged.

## Open points for calibration

- Start constants: `ENEMY_K` 0.8 and `K` 0.25 are the design's values; `feasibility.md` says no single `ENEMY_K`
  fits both ends and that `K` should be near 0.10-0.12.
- Special contracts at the defaults: story 7%, boss 38%, captain story 38%, campaign 46% shadow wins.
- Retreat: 38% of defeats keep half of ours standing (target 60%).
- Trainees keyed to the company's lowest level give a lone high-level captain two strong fill-ins. Not measured.
