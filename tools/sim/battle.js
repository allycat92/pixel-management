#!/usr/bin/env node
// 전투 판정 일치 검사: 봇이 실제로 받은 의뢰 보고서로 Battle.plan → findBattle 을 돌려,
// 시뮬레이션 결과(승패)가 이미 정해진 판정 결과와 맞는지 확인한다. 보고서마다 네 가지 결과를 모두 시험한다.
//   node tools/sim/battle.js [reports=200] [seed=1]
'use strict';
const { run, makeScript } = require('./bot');

const N = +process.argv[2] || 200;
const seed0 = +process.argv[3] || 1;
const PER_GAME = 40; // 한 판에서 고르는 보고서 수 (초반·중반·후반이 고루 섞이게 여러 판에서 모은다)
// 그림 없이 plan()이 쓰는 UI.h.soldierLook 만 흉내 낸다 (js/ui.js 와 같은 규칙)
const PRELUDE = `var UI = { h: { soldierLook(f, i) { const sd = FACTIONS[f].soldier || FACTIONS.crown.soldier;
  return { cls: sd.classes[i % sd.classes.length], skin: sd.skins[i % sd.skins.length], hair: sd.hairs[(i * 7) % sd.hairs.length], longHair: i % 3 === 1, tint: { outfit: FACTIONS[f].color, accent: FACTIONS[f].accent } }; } } };
var Sprites = {}; var Art = undefined;`;
const script = makeScript(['battle.js'], PRELUDE);
const OUTS = ['great', 'success', 'fail', 'disaster'];
const want = (o) => o === 'great' || o === 'success';

const stats = { reports: 0, trials: 0, mismatch: 0, soft: 0, slow: 0, timeout: 0, ms: 0, maxMs: 0, groups: {}, sizes: {}, perOutcome: {}, units: 0, maxUnits: 0 };
const mismatches = [];
let seed = seed0;
while (stats.reports < N && seed < seed0 + 50) {
  let taken = 0, seen = 0;
  run(seed++, 400, 'all', {
    script, shadow: false,   // 옛 재생 경로(findBattle)만 본다: 그림자 능력치 전투는 tools/sim/shadow.js 가 본다
    onReport(report, G, ctx) {
      seen++;
      if (stats.reports >= N || taken >= PER_GAME || seen % 4) return; // 네 번째 보고서마다 하나씩
      taken++;
      stats.reports++;
      const B = ctx.Battle;
      const rep = JSON.parse(JSON.stringify(report));
      OUTS.forEach((outcome) => {
        const groups = B.plan(rep);
        const sides = [0, 1].map((sd) => groups.filter((g) => g.side === sd).length);
        stats.groups[sides.join('v')] = (stats.groups[sides.join('v')] || 0) + 1;
        groups.forEach((g) => { stats.sizes[g.units.length] = (stats.sizes[g.units.length] || 0) + 1; });
        const nUnits = groups.reduce((a, g) => a + g.units.length, 0);
        stats.units += nUnits; stats.maxUnits = Math.max(stats.maxUnits, nUnits);
        const t0 = process.hrtime.bigint();
        const f = B.findBattle(groups, outcome, rep.seed);
        const ms = Number(process.hrtime.bigint() - t0) / 1e6;
        stats.trials++; stats.ms += ms; stats.maxMs = Math.max(stats.maxMs, ms);
        const po = stats.perOutcome[outcome] = stats.perOutcome[outcome] || { n: 0, miss: 0, soft: 0, ms: 0, t: 0 };
        po.n++; po.ms += ms; po.t += f.res.t;
        if (f.res.t >= 60) stats.slow++;
        if (f.res.t >= 90 - 0.05) stats.timeout++;
        if (f.res.won !== want(outcome)) {
          stats.mismatch++; po.miss++;
          if (mismatches.length < 10) mismatches.push(`${outcome} ${rep.quest.type} ★${rep.quest.level} groups ${sides.join('v')} bias ${f.bias.toFixed(2)} loss ${f.res.loss.toFixed(2)}`);
        } else if ((outcome === 'great' && f.res.loss > 0.25) || (outcome === 'disaster' && f.res.loss < 0.5)) { stats.soft++; po.soft++; }
      });
    },
  });
}
console.log(`reports ${stats.reports} × 4 outcomes = ${stats.trials} findBattle calls (game seeds ${seed0}..${seed - 1})`);
console.log(`win/lose mismatches: ${stats.mismatch}`);
console.log(`soft misses (great with >25% loss / disaster with <50% loss): ${stats.soft}`);
console.log(`slow battles (>=60 s): ${stats.slow}, time-limit (90 s) battles: ${stats.timeout}`);
console.log(`findBattle avg ${(stats.ms / stats.trials).toFixed(1)} ms, max ${stats.maxMs.toFixed(0)} ms`);
console.log(`units on field avg ${(stats.units / stats.trials).toFixed(1)}, max ${stats.maxUnits}`);
Object.entries(stats.perOutcome).forEach(([o, v]) => console.log(`  ${o.padEnd(8)} n=${v.n} miss=${v.miss} soft=${v.soft} avg ${(v.ms / v.n).toFixed(1)} ms, battle ${(v.t / v.n).toFixed(1)} s`));
console.log('groups per side (ally v enemy):', JSON.stringify(stats.groups));
console.log('group sizes:', JSON.stringify(stats.sizes));
mismatches.forEach((m) => console.log('  MISMATCH', m));
