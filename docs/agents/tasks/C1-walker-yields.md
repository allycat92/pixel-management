# C1 — 유닛 밀림 고치기: 걷는 쪽이 비켜 가고, 서 있는 유닛은 밀리지 않는다 (Codex)

## Why (owner, 2026-11-26 playtest)
"전투중에 유닛끼리 충돌해서 어색하게 질질 밀리는 부분은 좀 별로였어." Investigation: `docs/plans/jostle/README.md`.
The pairwise separation in `js/battle.js` (around lines 961-983, the loop after movement) pushes BOTH units of an overlapping
pair by half the overlap every tick, with no priority, so a standing unit is shoved by allies walking past (17% of unit-ticks).

## What to do
1. Start from the prototype diff `docs/plans/jostle/V11_walker_yields.diff`. It targets the battle.js of commit 9cb577c, so line
   numbers may drift; apply it by hand where needed. Rule:
   - a unit that is walking takes the correction (it steers around / yields);
   - a standing unit is never pushed by an ally;
   - routed units pass through allies;
   - a dash puts the whole correction on the dashing unit.
2. Fix the two problems the judge found in V11 (`docs/plans/jostle/README.md`):
   - (a) findBattle got ~2x slower: max 0.62 s -> 1.37 s, because the new steering and spot checks scan all pairs. Add a cheap
     near-neighbour pre-check (grid buckets or a sorted-x sweep) so the average and max findBattle time are back within
     +15% of the current numbers.
   - (b) two standing allies can stay drawn on top of each other: deep overlap (nd < 0.5) lasting >= 1 s. Add a slow
     standing-vs-standing separation so no pair stays deeply overlapped for more than 1 s.
3. Do not change anything else in the battle rules (targets, damage, skills, morale). This is step 1 of the tactics work
   (`docs/plans/tactics/2026-11-26_tactics_decision.md`). The line/formation behaviour comes later.

## Checks (paste the result lines into your report)
- `node tools/sim/battle.js 100`: all four outcomes must stay at `miss=0`. Report soft misses and battle durations
  (now 19.1 / 28.8 / 23.6 / 20.5 s).
- `node tools/sim/bot.js` (or `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum`): it must be identical to before, because the
  bot does not use battle.js. If it differs, explain why.
- Standing-push measurement, before and after: % of unit-ticks where a unit that did not move itself gets displaced.
  Target < 1% (now ~17%).
- Stuck melee: melee units alive >= 15 s that never attacked (now 3.1%; V11 had 5.0%) - keep it <= 5%.
- findBattle timing: average and max, before and after.
- Browser: `python -m http.server 8000`, play one battle at 1x. Confirm no page errors and that units no longer slide while
  standing.

## Deliver
- Branch `agent/codex`, cut from `origin/claude/dot-fantasy-management-game-saupju`. Commit only `js/battle.js` (plus a
  measurement script under `tools/sim/` if you wrote one).
- Report `docs/agents/reports/codex.md` on the same branch, as a new section `## C1 — <date>`. It holds the numbers above,
  what you changed, and anything you could not do.
- Push `agent/codex`. Set this task's row in `docs/agents/queue.md` to `REVIEW` on your branch.
