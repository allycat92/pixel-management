#!/usr/bin/env node
// 헤드리스 밸런스 시뮬레이터: 단순한 봇이 길드를 운영하며 N판을 돌린다.
//   node tools/sim/bot.js [runs=12] [days=365] [mode=all|monster]
//   SIM_ROOT=/path/to/other/checkout node tools/sim/bot.js ...   (다른 체크아웃의 js/ 로 비교)
//   SIM_SEED=1 (기본) — 판마다 seed+i 로 Math.random 을 고정해 재현 가능하게 돌린다.
//   SIM_JSON=1 — 요약 대신 판별 결과를 JSON 으로 출력
//   SIM_SHADOW=0 — 귀환 때의 그림자 능력치 전투(js/muster.js shadowResolve)를 돌리지 않는다 (10배쯤 빠르다. 결과는 같아야 한다)
// 게임 스크립트(js/*.js)를 vm 으로 읽어 들이고, UI·그림 없이 Game 만 돌린다.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = process.env.SIM_ROOT || path.resolve(__dirname, '..', '..');
const FILES = ['data.js', 'classes.js', 'world.js', 'content.js', 'game.js', 'company.js', 'faction.js', 'contract.js', 'captains.js', 'stats.js', 'muster.js']
  .filter((f) => fs.existsSync(path.join(ROOT, 'js', f)));   // 능력치 표가 생기기 전의 체크아웃(SIM_ROOT)도 돌릴 수 있게
const HAS_STATS = FILES.includes('stats.js');
// extra: 뒤에 덧붙일 파일(예: battle.js), prelude: 앞에 둘 코드(예: UI 대역)
function makeScript(extra = [], prelude = '') {
  const src = prelude + '\n' + [...FILES, ...extra].map((f) => fs.readFileSync(path.join(ROOT, 'js', f), 'utf8')).join('\n')
    + '\nthis.Game=Game;this.PROMOTIONS=PROMOTIONS;this.PROMOTE_COST=PROMOTE_COST;this.STARTER_CAPTAINS=STARTER_CAPTAINS;this.MASTERS=MASTERS;this.FACILITIES=FACILITIES;'
    + (HAS_STATS ? 'this.Stats=Stats;' : '')
    + (extra.includes('battle.js') ? 'this.Battle=Battle;' : '');
  return new vm.Script(src, { filename: 'game-bundle.js' });
}
let SCRIPT = null;
// 기본 봇은 게임과 똑같이 그림자 전투까지 돌린다 (battle.js 는 그림 없이도 읽힌다): 그림자가 게임의 난수·상태를 건드리지 않는지 md5 로 지킨다.
const SHADOW = HAS_STATS && process.env.SIM_SHADOW !== '0';

function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const CHECK_DAYS = [30, 60, 120, 180, 240, 300, 365];

// opts.script: makeScript() 결과, opts.onReport(report, Game, ctx): 의뢰 보고서가 나올 때마다
// opts.shadow: false 면 그림자 전투를 끈다 (true 면 SIM_SHADOW=0 이어도 켠다), opts.equipGuard: true 면 출격 중 장비 잠금을 켠다
// opts.onStart(Game, ctx): 새 게임을 만든 직후, opts.onOffer(contract, units, chance, Game, ctx): 봇이 의뢰 하나를 저울질할 때마다 (보내기 전)
function run(seed, days, mode, opts = {}) {
  const rnd = mulberry(seed);
  const M = Object.create(Math);
  M.random = rnd;
  const ctx = { localStorage: { setItem() {}, getItem() { return null; }, removeItem() {} }, console, Math: M };
  vm.createContext(ctx);
  (opts.script || (SCRIPT = SCRIPT || makeScript(SHADOW ? ['battle.js'] : []))).runInContext(ctx);
  const G = ctx.Game;
  // 옛 봇은 출격 중인 단원에게도 장비를 갈아 끼운다. 그 판을 그대로 재현해야 md5 기준이 유지되므로 장비 잠금(js/muster.js)을 끈다.
  // opts.equipGuard: true 면 실제 게임처럼 잠근다 (결과가 기준과 달라진다).
  G.equipGuard = !!opts.equipGuard;
  if (opts.shadow === false || (opts.shadow == null && !SHADOW)) G.shadowBattle = false;
  const coin = () => (rnd() < 0.5 ? 0 : 1);
  G.newGame();
  if (opts.onStart) opts.onStart(G, ctx);
  G.state.pendingReports = [];
  G.chooseStarter(ctx.STARTER_CAPTAINS[Math.floor(rnd() * 3)]);
  const s = G.state;
  const rankAt = {};
  const goldAt = {};
  const chances = [];
  const groupSizes = [];
  let calDefDay = 0, campaigns = 0, conflict = 0, monster = 0;
  let minGold = s.gold;
  const seenCamp = new Set(), takenCamp = new Set();
  const powerAt = {};
  let finalTries = 0, finalChance = 0;

  for (let d = 0; d < days; d++) {
    if (s.over) break;
    const pay = () => (G.weeklyWageTotal() + G.weeklyUpkeepTotal());
    // 시설
    ['barracks', 'dorm', 'training', 'board', 'tavern', 'forge', 'infirmary'].forEach((k) => {
      const c = G.facilityCost(k);
      if (s.gold > c + pay() * 2 + 200 && s.facilities[k] < ctx.FACILITIES[k].max) G.upgrade(k);
    });
    // 용병단 창설
    if (G.ownCompanies().length < G.maxCompanies() && s.gold > G.companyCost() + 300) G.createCompany();
    // 특별 용병·정예 영입
    s.recruits.slice().forEach((r) => { if (s.mercs.length < G.capacity() && s.gold > G.hireCost(r) + G.weeklyWageTotal() + 200) G.hire(r.id); });
    // 대원 모집: 빈 자리만큼, 직업을 돌아가며
    const ORDER = ['warrior', 'archer', 'cleric', 'mage', 'rogue', 'warrior', 'archer', 'mage'];
    G.ownCompanies().forEach((c) => {
      let guard = 0;
      while (guard++ < 10 && !c.missionId && G.unitsOf(c).length + G.reserve().filter((m) => !G.isCaptain(m)).length < G.unitSlots() && s.mercs.length < G.capacity()) {
        const cls = ORDER[G.unitsOf(c).length % ORDER.length];
        const vet = s.gold > G.unitHireCost(cls, true) + G.weeklyWageTotal() * 2 + 300;
        if (s.gold < G.unitHireCost(cls, vet) + G.weeklyWageTotal() + 150) break;
        if (!G.hireUnit(cls, vet)) break;
        G.assign(s.mercs[s.mercs.length - 1].id, c.id);
      }
    });
    // 배속: 예비 인원(대장 포함)을 빈 자리에
    G.reserve().forEach((m) => {
      if (m.status === 'quest') return;
      const c = G.ownCompanies().find((co) => !co.missionId && !G.slotProblem(m, co) && (!G.isCaptain(m) || !G.captainOf(co)));
      if (c) G.assign(m.id, c.id);
    });
    // 외부 계약: 돈 많으면
    if (G.extCompanies().length < 2 && s.market.length && s.gold > 3000) G.contractCompany(s.market[0].id);
    G.extCompanies().forEach((c) => { if (c.contractEnd - s.day <= 3 && s.gold > G.renewCost(c) + 2000) G.renewCompany(c.id); });
    // 전직, 장비, 약초, 연회
    s.mercs.forEach((m) => {
      if (G.canPromote(m) && m.status !== 'quest' && s.gold > ctx.PROMOTE_COST + 300) G.promote(m.id, ctx.PROMOTIONS[m.cls][coin()].key);
      if (G.canMaster(m) && m.status !== 'quest' && s.gold > 1400) G.promoteMaster(m.id, ctx.MASTERS[m.adv][coin()].key);
    });
    s.shop.slice().forEach((it) => { if (s.gold > G.shopPrice(it) + pay() * 2 + 400) G.buy(it.id); });
    const sum = (it) => (it ? Object.values(it.bonus).reduce((a, b) => a + b, 0) : 0);
    s.mercs.forEach((m) => ['weapon', 'armor', 'trinket'].forEach((slot) => {
      const best = s.inventory.filter((i) => i.slot === slot).sort((a, b) => sum(b) - sum(a))[0];
      if (best && sum(best) > sum(m.equip[slot])) G.equip(m.id, best.id);
    }));
    s.mercs.filter((m) => m.status === 'injured' && s.herbs > 0).forEach((m) => G.useHerb(m.id));
    if (G.feastReady() && s.mercs.length && s.mercs.reduce((a, m) => a + m.morale, 0) / s.mercs.length < 60 && s.gold > G.feastCost() + 300) G.feast();
    // 의뢰: 이야기·보스·결전 우선, 그다음 보상순
    const special = (c) => (c.story || c.boss || c.campaign || c.capStory ? 1e6 : 0);
    s.contracts.forEach((c) => { if (c.campaign && !c.final) seenCamp.add(c.campaign.id); });
    const cs = s.contracts.slice().sort((a, b) => special(b) + b.reward - special(a) - a.reward);
    for (const c of cs) {
      if (!s.contracts.includes(c)) continue;
      if (mode === 'monster' && c.cat !== 'monster') continue;
      const free = s.companies.filter((co) => !co.missionId && (co.own ? G.availableMembers(co).filter((m) => m.fatigue < 80).length >= 2 : !G.extRefusal(co, c)));
      if (!free.length) break;
      const unitOf = (co) => (co.own ? { companyId: co.id, memberIds: G.availableMembers(co).filter((m) => m.fatigue < 80).map((m) => m.id) } : { companyId: co.id });
      let units;
      if (c.story) {
        const co = free.find((x) => x.own && G.availableMembers(x).some((m) => m.hero === c.story.hero));
        if (!co) continue;
        units = [unitOf(co)];
      } else {
        const sorted = free.map((co) => ({ co, u: unitOf(co) })).sort((a, b) => G.unitsPower(c, [b.u]) - G.unitsPower(c, [a.u]));
        units = sorted.slice(0, c.campaign ? c.campaign.slots : 1).map((x) => x.u);
      }
      const ch = G.successChance(c, units);
      if (opts.onOffer) opts.onOffer(c, units, ch, G, ctx);
      if (ch >= (c.campaign ? 0.55 : 0.6)) {
        const before = s.missions.length;
        G.dispatch(c.id, units);
        if (s.missions.length > before) {
          chances.push(ch);
          units.forEach((u) => groupSizes.push(u.memberIds ? u.memberIds.length : G.company(u.companyId).size));
          if (c.final) { finalTries++; finalChance += ch; }
          if (c.campaign && !c.final) takenCamp.add(c.campaign.id);
          if (c.campaign) campaigns++; else if (c.cat === 'monster') monster++; else conflict++;
        }
      }
    }
    G.nextDay();
    s.pendingReports.forEach((r) => {
      if (r.special === 'dialog' && r.choice) G.applyChoice(r.choice.hero, r.choice.ch, coin());
      if (r.quest && opts.onReport) opts.onReport(r, G, ctx);
    });
    s.pendingReports = [];
    if (s.calamityDefeated && !calDefDay) calDefDay = s.day;
    if (CHECK_DAYS.includes(s.day)) {
      goldAt[s.day] = s.gold;
      // 가장 강한 용병단 셋의 결전 전투력 합 (최종 결전·결전에 보낼 전력)
      powerAt[s.day] = s.companies.map((co) => (co.own ? G.ownCompanyPower(co, G.members(co), 'battle') : G.extPower(co, 'battle')))
        .sort((a, b) => b - a).slice(0, 3).reduce((a, b) => a + b, 0);
    }
    minGold = Math.min(minGold, s.gold);
    const rn = G.rank().name;
    if (!(rn in rankAt)) rankAt[rn] = s.day;
  }
  const caps = s.mercs.filter((m) => G.isCaptain(m));
  const own = G.ownCompanies();
  return {
    seed, day: s.day, powerAt, campSeen: seenCamp.size, campTaken: takenCamp.size, finalTries, finalChance: finalTries ? finalChance / finalTries : 0, over: s.over, rank: G.rank().name, gold: s.gold, minGold, goldAt, rankAt,
    mercs: s.mercs.length, comps: own.length, ext: G.extCompanies().length,
    avgCompanySize: own.length ? own.reduce((a, c) => a + G.members(c).length, 0) / own.length : 0,
    wage: G.weeklyWageTotal(), caps: caps.length, capNames: caps.map((m) => m.cap),
    avgChance: chances.length ? chances.reduce((a, b) => a + b, 0) / chances.length : 0,
    avgGroup: groupSizes.length ? groupSizes.reduce((a, b) => a + b, 0) / groupSizes.length : 0,
    campaigns, conflict, monster, bosses: Object.keys(s.bossDefeated).length,
    calamity: s.calamity || (s.calamityDefeated ? 'defeated' : null), calDay: s.calamityDay || 0,
    calDefeated: !!s.calamityDefeated, calDefDay, completed: s.stats.completed, failed: s.stats.failed, fallen: s.stats.fallen,
  };
}

function summarize(res, days) {
  const N = res.length;
  const avg = (f) => res.reduce((a, r) => a + (f(r) || 0), 0) / N;
  const fmt = (v, d = 0) => (Math.round(v * 10 ** d) / 10 ** d).toLocaleString('en-US');
  const ranks = {};
  res.forEach((r) => { const k = r.over ? `over:${r.over}` : r.rank; ranks[k] = (ranks[k] || 0) + 1; });
  const rankDay = (k) => { const v = res.map((r) => r.rankAt[k]).filter(Boolean); return v.length ? `${Math.round(v.reduce((a, b) => a + b) / v.length)} (n=${v.length})` : '-'; };
  const rows = [
    ['runs × days', `${N} × ${days}`],
    ['final rank / game over', JSON.stringify(ranks)],
    ...['D', 'C', 'B', 'A', 'S'].map((k) => [`day reaching ${k}`, rankDay(k)]),
    ['bankruptcies', res.filter((r) => r.over === 'bankrupt').length],
    ['captains (avg, end)', fmt(avg((r) => r.caps), 2)],
    ...CHECK_DAYS.filter((d) => d <= days).map((d) => [`gold @ day ${d}`, fmt(avg((r) => r.goldAt[d] ?? r.gold))]),
    ['lowest gold (avg of run minima)', fmt(avg((r) => r.minGold))],
    ['weekly wages (end)', fmt(avg((r) => r.wage))],
    ['mercs / own companies / ext (end)', `${fmt(avg((r) => r.mercs), 1)} / ${fmt(avg((r) => r.comps), 1)} / ${fmt(avg((r) => r.ext), 1)}`],
    ...CHECK_DAYS.filter((d) => d <= days).map((d) => [`top-3 company power @ day ${d}`, fmt(avg((r) => r.powerAt[d]))]),
    ['campaigns offered / taken', `${fmt(avg((r) => r.campSeen), 1)} / ${fmt(avg((r) => r.campTaken), 1)}`],
    ['final battle attempts (avg chance)', `${fmt(avg((r) => r.finalTries), 2)} (${fmt(avg((r) => r.finalChance) * 100 * N / Math.max(1, res.filter((r) => r.finalTries).length), 1)}%)`],
    ['avg own company size (end)', fmt(avg((r) => r.avgCompanySize), 2)],
    ['avg dispatched group size', fmt(avg((r) => r.avgGroup), 2)],
    ['avg success chance of taken contracts', `${fmt(avg((r) => r.avgChance) * 100, 1)}%`],
    ['contracts taken: monster / conflict / campaign', `${fmt(avg((r) => r.monster))} / ${fmt(avg((r) => r.conflict))} / ${fmt(avg((r) => r.campaigns))}`],
    ['completed / failed / fallen', `${fmt(avg((r) => r.completed))} / ${fmt(avg((r) => r.failed))} / ${fmt(avg((r) => r.fallen), 1)}`],
    ['bosses slain', fmt(avg((r) => r.bosses), 1)],
    ['calamity rose (avg day)', `${res.filter((r) => r.calDay).length} (${Math.round(avg((r) => r.calDay) * N / Math.max(1, res.filter((r) => r.calDay).length))})`],
    ['calamity defeated (avg day)', `${res.filter((r) => r.calDefeated).length} (${Math.round(avg((r) => r.calDefDay) * N / Math.max(1, res.filter((r) => r.calDefeated).length))})`],
    ['dark age (game over)', res.filter((r) => r.over === 'darkness').length],
  ];
  const w = Math.max(...rows.map((r) => String(r[0]).length));
  return rows.map(([k, v]) => `${String(k).padEnd(w)}  ${v}`).join('\n');
}

if (require.main === module) {
  const N = +process.argv[2] || 12;
  const days = +process.argv[3] || 365;
  const mode = process.argv[4] || 'all';
  const seed0 = +process.env.SIM_SEED || 1;
  const res = [];
  for (let i = 0; i < N; i++) res.push(run(seed0 + i, days, mode));
  if (process.env.SIM_JSON) console.log(JSON.stringify(res, null, 1));
  else console.log(`root: ${ROOT}\n${summarize(res, days)}`);
}

module.exports = { run, summarize, makeScript, ROOT };
