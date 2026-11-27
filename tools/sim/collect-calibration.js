#!/usr/bin/env node
// Record the offers seen by each strategy and the actual reports for its dispatches.
// node tools/sim/collect-calibration.js --strategy sensible --seeds 1,3101,4101 --jobs 6
// node tools/sim/collect-calibration.js --strategy human --seeds 1,3101 --jobs 6
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { gzipSync } = require('node:zlib');
const { fork } = require('node:child_process');
const { run, makeScript, ROOT } = require('./bot.js');

function teamsOf(spec, Stats) {
  return spec.groups.filter((group) => group.kind === 'own' || group.kind === 'ext').map((group) => {
    const captain = group.units.find((unit) => unit.leader);
    const members = group.units.filter((unit) => !unit.recruit);
    const levels = members.map((unit) => unit.level ?? group.level).filter(Number.isFinite);
    const style = captain && Stats.leadStyle(captain.sk);
    return {
      company_id: group.companyId,
      kind: group.kind,
      captain_key: captain?.capKey ?? null,
      captain_class: captain?.cls ?? null,
      style: style ? (style.ranged ? 'ranged' : 'melee') + (style.rally ? '+rally' : '') : null,
      members: members.length,
      avg_level: levels.length ? levels.reduce((a, b) => a + b, 0) / levels.length : null,
      trainees: group.units.length - members.length,
      betrayed: !!group.betray,
    };
  });
}

function row(seed, strategy, source, day, contract, spec, estimate, outcome, winner, end, Stats) {
  const foes = spec.groups.filter((group) => group.side === 1).flatMap((group) => group.units);
  const archetypes = {};
  for (const enemy of foes) {
    const arch = enemy.arch || 'soldier';
    archetypes[arch] = (archetypes[arch] || 0) + 1;
  }
  const teams = teamsOf(spec, Stats);
  return {
    seed, strategy, source, day, id: contract.id, type: contract.type, kind: Stats.kindOf(contract),
    star: contract.level, province: contract.province, terrain: spec.terrain, rule: spec.rule,
    R: estimate.R, band: estimate.band, forecast: Stats.BAND_NAMES[estimate.band],
    outcome, won: outcome === 'success' || outcome === 'great', battle_winner: winner, timed_out: end === 'time', end,
    companies: teams.length, teams, enemies: foes.length, enemy_archetypes: archetypes,
    lead_enemy_archetype: foes.find((enemy) => enemy.boss || enemy.bigMon || enemy.rank === 'leader')?.arch
      || foes[0]?.arch || 'soldier',
    boss_key: contract.boss || null,
    boss_enemy: contract.boss ? contract.enemy : null,
  };
}

function collector(seed, strategy) {
  const rows = [];
  const departures = new Map();
  return {
    rows,
    attach(Game) {
      const dispatch = Game.dispatch;
      Game.dispatch = function (id, units) {
        const count = this.state.missions.length;
        const result = dispatch.call(this, id, units);
        if (this.state.missions.length > count) departures.set(id, this.state.day);
        return result;
      };
    },
    offer(contract, units, spec, estimate, Game, { Stats, Battle }) {
      const rec = Battle.run(spec);
      const outcome = Game.judge(spec, rec, Game.partyMods(Game.unitParts(units).allMembers)).outcome;
      rows.push(row(seed, strategy, 'offer', Game.state.day, contract, spec, estimate, outcome, rec.winner, rec.end, Stats));
    },
    report(report, Game, { Stats }) {
      if (!report.battle) throw new Error(`Missing battle record: seed ${seed}, contract ${report.quest.id}`);
      const { spec, R, band, winner, end } = report.battle;
      const day = departures.get(report.quest.id);
      if (day == null) throw new Error(`Missing departure: seed ${seed}, contract ${report.quest.id}`);
      departures.delete(report.quest.id);
      rows.push(row(seed, strategy, 'sent', day, report.quest, spec, { R, band }, report.outcome, winner, end, Stats));
    },
  };
}

function runHuman(seed, days, collector) {
  const context = vm.createContext({ console, localStorage: { setItem() {}, getItem() { return null; } } });
  makeScript(['battle.js']).runInContext(context);
  const { Game, Stats, STARTER_CAPTAINS, FACILITIES, PROMOTIONS, PROMOTE_COST, MASTERS } = context;
  const random = Stats.rng(seed);
  vm.runInContext('Math.random = this.simRandom', Object.assign(context, { simRandom: random }));
  Game.equipGuard = true;
  Game.newGame();
  Game.setResolve('battle');
  Game.state.pendingReports = [];
  Game.chooseStarter(STARTER_CAPTAINS[Math.floor(random() * STARTER_CAPTAINS.length)]);
  collector.attach(Game);
  const s = Game.state;
  const co = Game.ownCompanies()[0];
  const equipmentScore = (item) => Object.values(item?.bonus || {}).reduce((a, b) => a + b, 0);
  const pay = () => Game.weeklyWageTotal();
  const wordWeight = [0, 0.30, 0.70, 0.85, 1];
  let lastUpgrade = -6;

  for (let d = 0; d < days && !s.over; d++) {
    if (s.day - lastUpgrade >= 7) {
      const order = s.facilities.barracks ? ['training', 'board', 'infirmary', 'forge', 'tavern', 'dorm'] : ['barracks'];
      const facility = order.find((key) => s.facilities[key] < FACILITIES[key].max);
      if (facility && s.gold >= Game.facilityCost(facility) + pay() * 2 + 100) {
        Game.upgrade(facility);
        lastUpgrade = s.day;
      }
    }
    if (!co.missionId) {
      for (const member of Game.reserve()) {
        if (member.status === 'idle' && !Game.slotProblem(member, co)) Game.assign(member.id, co.id);
      }
      while (Game.unitsOf(co).length < Game.unitSlots()) {
        const cls = ['warrior', 'cleric', 'archer'][Game.unitsOf(co).length];
        const vet = s.gold >= Game.unitHireCost(cls, true) + pay() * 2 + 300;
        if (s.gold < Game.unitHireCost(cls, vet) + pay() + 100 || !Game.hireUnit(cls, vet)) break;
        Game.assign(s.mercs.at(-1).id, co.id);
      }
      for (const member of Game.members(co)) {
        if (Game.canPromote(member) && s.gold > PROMOTE_COST + pay() + 100) Game.promote(member.id, PROMOTIONS[member.cls][0].key);
        if (Game.canMaster(member) && s.gold > pay() * 2 + 1200) Game.promoteMaster(member.id, MASTERS[member.adv][0].key);
        if (member.status === 'injured' && s.herbs > 0) Game.useHerb(member.id);
        for (const slot of ['weapon', 'armor', 'trinket']) {
          const equipped = equipmentScore(member.equip[slot]);
          const best = s.inventory.filter((item) => item.slot === slot).sort((a, b) => equipmentScore(b) - equipmentScore(a))[0];
          if (best && equipmentScore(best) > equipped) Game.equip(member.id, best.id);
          const upgrade = s.shop.filter((item) => item.slot === slot && equipmentScore(item) > equipmentScore(member.equip[slot]))
            .sort((a, b) => equipmentScore(b) - equipmentScore(a))[0];
          if (upgrade && s.gold > Game.shopPrice(upgrade) + pay() * 2 + 300) {
            Game.buy(upgrade.id);
            Game.equip(member.id, upgrade.id);
          }
        }
      }
      let best = null;
      for (const contract of s.contracts) {
        const members = Game.availableMembers(co).filter((member) => member.fatigue < 80 || member.hero && member.hero === contract.story?.hero);
        if (!members.length || Game.deadTarget(contract)) continue;
        const units = [{ companyId: co.id, memberIds: members.map((member) => member.id) }];
        if (Game.storyHeroMissing(contract, units)) continue;
        const spec = Game.muster(contract, units);
        const estimate = Game.forecast(spec);
        collector.offer(contract, units, spec, estimate, Game, context);
        if (!estimate.band || (estimate.band === 1 && s.gold < 3000)) continue;
        const score = (contract.reward + 6 * contract.rep) * wordWeight[estimate.band] / Game.contractDays(contract, units);
        if (!best || score > best.score) best = { contract, units, score };
      }
      if (best) Game.dispatch(best.contract.id, best.units);
    }
    Game.nextDay();
    for (const report of s.pendingReports) {
      if (report.quest) collector.report(report, Game, context);
      else if (report.special === 'dialog' && report.choice) Game.applyChoice(report.choice.hero, report.choice.ch, 0);
    }
    s.pendingReports = [];
  }
  return { day: s.day, over: s.over, rank: Game.rank().name };
}

function collect(seed, days, strategy) {
  const sink = collector(seed, strategy);
  const result = strategy === 'human' ? runHuman(seed, days, sink) : run(seed, days, 'all', {
    resolve: 'battle',
    onStart: sink.attach,
    onBattleOffer: sink.offer,
    onReport: sink.report,
  });
  return { rows: sink.rows, day: result.day, over: result.over, rank: result.rank };
}

function options(argv) {
  const settings = { strategy: 'sensible', seeds: '1,3101,4101', jobs: 6, runs: 12, days: 365, out: path.join(ROOT, 'data', 'C21') };
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i].slice(2);
    if (!argv[i].startsWith('--') || !Object.hasOwn(settings, key) || argv[i + 1] == null) throw new Error(`Unknown or incomplete option: ${argv[i]}`);
    settings[key] = typeof settings[key] === 'number' ? Number(argv[i + 1]) : argv[i + 1];
  }
  settings.seeds = settings.seeds.split(',').map(Number);
  const positive = (n) => Number.isSafeInteger(n) && n > 0;
  if (!['sensible', 'human'].includes(settings.strategy)
      || ![settings.jobs, settings.runs, settings.days, ...settings.seeds].every(positive)
      || new Set(settings.seeds).size !== settings.seeds.length) throw new Error('Expected sensible/human and distinct positive seed sets, jobs, runs, days');
  return settings;
}

function worker(settings, partial) {
  return new Promise((resolve, reject) => {
    const child = fork(__filename, ['--worker', JSON.stringify(settings), partial], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
    child.on('message', (summary) => process.stderr.write(JSON.stringify(summary) + '\n'));
    child.on('error', reject);
    child.on('exit', (code) => code === 0 ? resolve() : reject(new Error(`Seed ${settings.seed} exited with ${code}`)));
  });
}

async function main(argv) {
  if (argv[0] === '--worker') {
    const { seed, strategy, days } = JSON.parse(argv[1]);
    const { rows, day, over, rank } = collect(seed, days, strategy);
    const text = rows.map((item) => JSON.stringify(item) + '\n').join('');
    fs.writeFileSync(argv[2], gzipSync(text));
    process.send({ seed, strategy, rows: rows.length, day, over, rank });
    return;
  }
  const settings = options(argv);
  fs.mkdirSync(settings.out, { recursive: true });
  const scratch = fs.mkdtempSync(path.join(path.resolve(settings.out), '.collect-'));
  for (const start of settings.seeds) {
    const partials = Array.from({ length: settings.runs }, (_, i) => path.join(scratch, `${start + i}.gz`));
    let next = 0;
    await Promise.all(Array.from({ length: Math.min(settings.jobs, settings.runs) }, async () => {
      while (next < partials.length) {
        const i = next++;
        await worker({ seed: start + i, strategy: settings.strategy, days: settings.days }, partials[i]);
      }
    }));
    const data = Buffer.concat(partials.map((file) => fs.readFileSync(file)));
    if (data.length > 20_000_000) throw new Error(`Seed set ${start} exceeds the 20 MB limit; use smaller sets`);
    const out = path.join(settings.out, `${settings.strategy}-${start}-${start + settings.runs - 1}.jsonl.gz`);
    fs.writeFileSync(out, data);
    console.log(out, data.length);
    partials.forEach((file) => fs.unlinkSync(file));
  }
  fs.rmdirSync(scratch);
}

main(process.argv.slice(2)).catch((error) => { console.error(error); process.exitCode = 1; });
