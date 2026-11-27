#!/usr/bin/env node
// 헤드리스 밸런스 시뮬레이터: 단순한 봇이 길드를 운영하며 N판을 돌린다.
//   node tools/sim/bot.js [runs=12] [days=365] [mode=all|monster]
//   SIM_ROOT=/path/to/other/checkout node tools/sim/bot.js ...   (다른 체크아웃의 js/ 로 비교)
//   SIM_SEED=1 (기본) — 판마다 seed+i 로 Math.random 을 고정해 재현 가능하게 돌린다.
//   SIM_JSON=1 — 요약 대신 판별 결과를 JSON 으로 출력
//   SIM_SHADOW=1 — 귀환 때의 그림자 능력치 전투(js/muster.js shadowResolve)도 돌린다 (14배쯤 느리다. 결과는 같아야 한다 — 그림자가 게임을
//                  건드리지 않는지 보는 시험. 기본은 끔: 일상 검사(md5)를 빠르게. 측정은 tools/sim/shadow.js)
//   --resolve battle (또는 SIM_RESOLVE=battle) — 3단계 전투 모드로 돌린다 (Game.RESOLVE = 'battle': 굳힌 편성의 전투가 결과를 정한다).
//                  봇은 의뢰를 다섯 단어 예상으로 고른다 (우세·압도는 받고, 백중은 가끔). 요약에 단어별 승률·날짜 구간·부상·사망을 더한다.
//                  기본 'roll' 은 오늘 게임 그대로다 (md5 기준 불변).
//                  4단계: 보낸 인원별 단어 승률, 시간이 다해 진 전투(인원별·유형별), 게시판 폭을 재앙이 일어난 판/아닌 판으로도 나눠 적는다 (stage3_notes.md 「Stage 4」)
//   --jobs N — 판을 N 개 프로세스로 나눠 돌린다 (결과는 같다. 전투 모드는 한 판에 수십 초)
//   --set KEY=VALUE — 조정값 덮어쓰기 (js/stats.js KN 등, 여러 번). 예: --set BOARD_W=[0.05,0.15,0.2,0.3,0.3] --set BM_CAP_AHEAD=3
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
    + '\nthis.Game=Game;this.PROMOTIONS=PROMOTIONS;this.PROMOTE_COST=PROMOTE_COST;this.STARTER_CAPTAINS=STARTER_CAPTAINS;this.MASTERS=MASTERS;this.FACILITIES=FACILITIES;this.CALAMITY_DARKNESS=CALAMITY_DARKNESS;'
    + (HAS_STATS ? 'this.Stats=Stats;' : '')
    + (extra.includes('battle.js') ? 'this.Battle=Battle;' : '');
  return new vm.Script(src, { filename: 'game-bundle.js' });
}
let SCRIPT = null;
// 기본 봇은 게임과 똑같이 그림자 전투까지 돌린다 (battle.js 는 그림 없이도 읽힌다): 그림자가 게임의 난수·상태를 건드리지 않는지 md5 로 지킨다.
const SHADOW = HAS_STATS && process.env.SIM_SHADOW === '1';
// 결과를 정하는 방식: 'roll' (기본) | 'battle' (--resolve battle 또는 SIM_RESOLVE=battle)
const argResolve = process.argv.indexOf('--resolve');
const RESOLVE = (argResolve > 0 ? process.argv[argResolve + 1] : process.env.SIM_RESOLVE) === 'battle' && HAS_STATS ? 'battle' : 'roll';
let SCRIPT_BATTLE = null;
const BAND_NAMES = ['무모', '열세', '백중', '우세', '압도'];
const dayBandOf = (d) => (d <= 30 ? '001-030' : d <= 60 ? '031-060' : d <= 120 ? '061-120' : d <= 240 ? '121-240' : '241-365');

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
const CHECK_DAYS_BM = [30, 60, 90, 120, 180, 240, 300, 365];   // 전투 모드는 90일 금화도 적는다 (중반 경제, 주인 결정 5). 'roll' 의 JSON 은 그대로

// opts.script: makeScript() 결과, opts.onReport(report, Game, ctx): 의뢰 보고서가 나올 때마다
// opts.shadow: false 면 그림자 전투를 끈다 (true 면 SIM_SHADOW 가 꺼져 있어도 켠다), opts.equipGuard: true 면 출격 중 장비 잠금을 켠다
// opts.onStart(Game, ctx): 새 게임을 만든 직후, opts.onOffer(contract, units, chance, Game, ctx): 봇이 의뢰 하나를 저울질할 때마다 (보내기 전)
// opts.resolve: 'battle' 이면 전투 모드 (없으면 --resolve / SIM_RESOLVE)
function run(seed, days, mode, opts = {}) {
  const rnd = mulberry(seed);
  const M = Object.create(Math);
  M.random = rnd;
  const ctx = { localStorage: { setItem() {}, getItem() { return null; }, removeItem() {} }, console, Math: M };
  vm.createContext(ctx);
  const battle = (opts.resolve || RESOLVE) === 'battle';
  const knobbed = opts.knobs && Object.keys(opts.knobs).length ? makeScript(battle || SHADOW ? ['battle.js'] : [], `var STAT_KNOBS = ${JSON.stringify(opts.knobs)};`) : null;
  (opts.script || knobbed || (battle ? (SCRIPT_BATTLE = SCRIPT_BATTLE || makeScript(['battle.js'])) : (SCRIPT = SCRIPT || makeScript(SHADOW ? ['battle.js'] : [])))).runInContext(ctx);
  const G = ctx.Game;
  // 옛 봇은 출격 중인 단원에게도 장비를 갈아 끼운다. 그 판을 그대로 재현해야 md5 기준이 유지되므로 장비 잠금(js/muster.js)을 끈다.
  // opts.equipGuard: true 면 실제 게임처럼 잠근다 (결과가 기준과 달라진다).
  G.equipGuard = !!opts.equipGuard;
  if (opts.shadow === false || (opts.shadow == null && !SHADOW)) G.shadowBattle = false;
  const coin = () => (rnd() < 0.5 ? 0 : 1);
  G.newGame();
  if (battle) G.setResolve('battle');
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
  // 전투 모드 기록: 단어별·날짜 구간별 승패, 등급, 부상, 사망(특별한 전투 / 그 밖)
  const bs = battle ? { byBand: {}, byDay: {}, byKind: {}, byHeads: {}, timeout: {}, tiers: { great: 0, success: 0, fail: 0, disaster: 0 }, memberBattles: 0, downed: 0, injured: 0, injDays: 0,
    deathsSpecial: 0, deathsOther: 0, relief: 0, reliefTaken: 0, lossPay: 0, losses: 0, minMercs: 99, captainOnlyDays: 0, offered: [0, 0, 0, 0, 0], taken: [0, 0, 0, 0, 0], boards: {} } : null;
  const tally = (o, k, win) => { const x = (o[k] = o[k] || [0, 0]); x[0]++; x[1] += win ? 1 : 0; };
  const seenOffer = new Set();
  // 전투 모드 봇: 진 특별 의뢰를 같은 예상으로 바로 다시 받지 않는다 (사람이라면 몇 번 지고 나면 키워서 다시 온다)
  const specialKey = (c) => (c.story ? `h${c.story.hero}:${c.story.ch}` : c.capStory ? `c${c.capStory.key}:${c.capStory.ch}` : c.boss ? `b${c.boss}` : c.final ? 'final' : null);
  const lostSpecial = {};

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
    // 전투 모드: 게시판의 폭 (사흘에 한 번, 봇이 받기 전) — 일반 의뢰를 가장 나은 직속 용병단(단원 전부)의 예상으로 센다. 난수·상태를 건드리지 않는다
    if (bs && s.day % 3 === 0) {
      const cos = G.ownCompanies().filter((co) => G.members(co).length);
      const w = [0, 0, 0, 0, 0];
      s.contracts.filter((q) => ctx.Stats.kindOf(q) === 'normal' && !q.relief).forEach((q) => {
        let best = -1;
        cos.forEach((co) => { const R = G.forecast(G.muster(q, [{ companyId: co.id, memberIds: G.members(co).map((m) => m.id) }])).R; if (R > best) best = R; });
        if (best >= 0) w[ctx.Stats.bandOf(best)]++;
      });
      // 4단계: 재앙이 일어난(lateGame) 판과 아닌 판을 따로도 센다 (재앙 없는 후반 게시판, Q8)
      [dayBandOf(s.day), `${dayBandOf(s.day)} ${G.lateGame() ? 'calamity' : 'no calamity'}`].forEach((key) => {
        const b = (bs.boards[key] = bs.boards[key] || { n: 0, w: [0, 0, 0, 0, 0], hard: 0, easy: 0, both: 0, mid: 0, top: 0 });
        b.n++; w.forEach((x, i) => { b.w[i] += x; });
        if (w[0] + w[1]) b.hard++;
        if (w[0] + w[1] + w[2]) b.mid++;
        b.top += s.contracts.reduce((m, q) => (ctx.Stats.kindOf(q) === 'normal' && !q.relief ? Math.max(m, q.level) : m), 0);
        if (w[3] + w[4]) b.easy++;
        if (w[0] + w[1] && w[3] + w[4]) b.both++;
      });
    }
    // 의뢰: 이야기·보스·결전 우선, 그다음 보상순
    const special = (c) => (c.story || c.boss || c.campaign || c.capStory ? 1e6 : 0);
    s.contracts.forEach((c) => { if (c.campaign && !c.final) seenCamp.add(c.campaign.id); });
    const cs = s.contracts.slice().sort((a, b) => special(b) + b.reward - special(a) - a.reward);
    for (const c of cs) {
      if (!s.contracts.includes(c)) continue;
      if (mode === 'monster' && c.cat !== 'monster') continue;
      // 전투 모드: 대장 혼자인 용병단도 보낸다 (구호 의뢰를 받을 수 있게)
      const minMembers = battle ? 1 : 2;
      const free = s.companies.filter((co) => !co.missionId && (co.own ? G.availableMembers(co).filter((m) => m.fatigue < 80).length >= minMembers : !G.extRefusal(co, c)));
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
      let take = ch >= (c.campaign ? 0.55 : 0.6);
      let takenR = 0;   // 전투 모드: 보낸 편성의 예상 전력비 R ('avg success chance' 줄 대신)
      if (battle) {
        // 다섯 단어로 고른다: 전력 순 상위 두 용병단 중 예상이 나은 쪽 (결전은 상위 slots 개를 함께), 우세·압도는 받고 백중은 3번에 1번
        if (!c.story && !c.campaign) {
          const sorted = free.map((co) => ({ co, u: unitOf(co) })).sort((a, b) => G.unitsPower(c, [b.u]) - G.unitsPower(c, [a.u])).slice(0, 2);
          let bestR = -1;
          sorted.forEach((x) => { const R = G.forecast(G.muster(c, [x.u])).R; if (R > bestR) { bestR = R; units = [x.u]; } });
        }
        const est = G.forecast(G.muster(c, units)), band = est.band;
        takenR = est.R;
        if (!seenOffer.has(c.id)) { seenOffer.add(c.id); bs.offered[band]++; }
        take = band >= 3 || (band === 2 && rnd() < 0.34);
        // 재앙이 암흑시대 문턱(점령 CALAMITY_DARKNESS-2 이상)에 다가오면: 최종 결전과 재앙 상대 결전은 백중이면 받고, 열세도 3번에 1번
        const doom = s.calamity && G.provincesOf(s.calamity).length >= ctx.CALAMITY_DARKNESS - 2 && (c.final || (c.campaign && G.isCalamity(c.target)));
        if (doom && (band === 2 || (band === 1 && rnd() < 0.34))) take = true;
        // 다시 올라온 특별 의뢰(이야기·대장 이야기·보스·최종)에 진 적이 있으면: 예상이 그때보다 나아졌거나 압도일 때만, 아니면 열흘은 쉰다
        const sk = specialKey(c), lost = sk && lostSpecial[sk];
        if (take && lost && band < 4 && band <= lost.band && s.day < lost.day + 10) take = false;
        if (take) bs.taken[band]++;
      }
      if (take) {
        const before = s.missions.length;
        G.dispatch(c.id, units);
        if (s.missions.length > before) {
          chances.push(battle ? takenR : ch);
          units.forEach((u) => groupSizes.push(u.memberIds ? u.memberIds.length : G.company(u.companyId).size));
          if (c.final) { finalTries++; finalChance += battle ? takenR : ch; }
          if (c.campaign && !c.final) takenCamp.add(c.campaign.id);
          if (c.campaign) campaigns++; else if (c.cat === 'monster') monster++; else conflict++;
        }
      }
    }
    G.nextDay();
    s.pendingReports.forEach((r) => {
      if (r.special === 'dialog' && r.choice) G.applyChoice(r.choice.hero, r.choice.ch, coin());
      if (r.quest && opts.onReport) opts.onReport(r, G, ctx);
      if (bs && r.quest && r.battle) {
        const won = r.outcome === 'great' || r.outcome === 'success', q = r.quest;
        if (!won && specialKey(q)) lostSpecial[specialKey(q)] = { day: s.day, band: r.battle.band };
        tally(bs.byBand, r.battle.band, won);
        tally(bs.byDay, dayBandOf(s.day), won);
        tally(bs.byKind, ctx.Stats.kindOf(q), won);
        // 4단계: 보낸 인원(직속 단원)별 단어 승률과, 시간이 다해 진 전투(인원별·의뢰 유형별)
        const nOurs = r.battle.spec ? r.battle.spec.groups.filter((g) => g.kind === 'own' || g.kind === 'ext').reduce((a, g) => a + g.units.filter((u) => !u.recruit).length, 0) : r.members.length;
        const heads = nOurs >= 4 ? '4+' : String(nOurs);
        tally(bs.byHeads, `${heads} ${BAND_NAMES[r.battle.band]}`, won);
        const lostOnTime = !won && r.battle.end === 'time';
        tally(bs.timeout, `heads ${heads}`, lostOnTime); tally(bs.timeout, `type ${q.type}`, lostOnTime);
        if (r.battle.band >= 3) tally(bs.timeout, `≥우세 heads ${heads}`, lostOnTime);
        bs.tiers[r.outcome]++;
        if (!won) { bs.losses++; bs.lossPay += r.gold; }
        if (q.relief) bs.reliefTaken++;
        r.members.forEach((m) => {
          bs.memberBattles++;
          if (m.down) bs.downed++;
          if (m.injury) { bs.injured++; bs.injDays += m.injury; }
          if (m.dead) { if (G.specialBattle(q)) bs.deathsSpecial++; else bs.deathsOther++; }
        });
      }
    });
    if (bs) {
      bs.minMercs = Math.min(bs.minMercs, s.mercs.length);
      if (s.mercs.length && s.mercs.every((m) => G.isCaptain(m))) bs.captainOnlyDays++;
      s.contracts.forEach((c) => { if (c.relief && !seenOffer.has(`r${c.id}`)) { seenOffer.add(`r${c.id}`); bs.relief++; } });
    }
    s.pendingReports = [];
    if (s.calamityDefeated && !calDefDay) calDefDay = s.day;
    if (bs && s.day === 90) goldAt[90] = s.gold;
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
    ...(bs ? { battle: bs } : {}),
  };
}

// --set KEY=VALUE (js/stats.js KN, REF, ARCH, RANK — 점으로 깊이: BM_CAL_SPECIAL.boss=0.9, 배열은 JSON: BOARD_W=[0.05,0.15,0.2,0.3,0.3]).
// 없는 이름은 거부한다 (오타로 기본값을 재는 일이 없게). 자세한 형식 검사는 tools/sim/shadow.js --set 과 같다
function setKnob(knobs, input) {
  const i = input ? input.indexOf('=') : -1;
  if (i <= 0) throw new Error(`expected KEY=VALUE: ${input}`);
  const key = input.slice(0, i), raw = input.slice(i + 1).trim();
  const val = /^[\[{]/.test(raw) ? JSON.parse(raw) : !isNaN(+raw) && raw ? +raw : raw;
  const c = {}; makeScript().runInNewContext(c);
  let o = { ...c.Stats.KN, REF: c.Stats.REF, ARCH: c.Stats.ARCH, RANK: c.Stats.RANK };
  key.split('.').forEach((k) => { if (o == null || typeof o !== 'object' || !Object.hasOwn(o, k)) throw new Error(`unknown knob: ${key}`); o = o[k]; });
  if (typeof o !== typeof val || Array.isArray(o) !== Array.isArray(val) || (Array.isArray(o) && o.length !== val.length)) throw new Error(`invalid knob ${key}: expected ${Array.isArray(o) ? `array of ${o.length}` : typeof o}`);
  const ks = key.split('.');
  let d = knobs;
  ks.slice(0, -1).forEach((k) => { d = d[k] = d[k] || {}; });
  d[ks[ks.length - 1]] = val;
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
    ...(res.every((r) => r.battle) ? CHECK_DAYS_BM : CHECK_DAYS).filter((d) => d <= days).map((d) => [`gold @ day ${d}`, fmt(avg((r) => r.goldAt[d] ?? r.gold))]),
    ['lowest gold (avg of run minima)', fmt(avg((r) => r.minGold))],
    ['weekly wages (end)', fmt(avg((r) => r.wage))],
    ['mercs / own companies / ext (end)', `${fmt(avg((r) => r.mercs), 1)} / ${fmt(avg((r) => r.comps), 1)} / ${fmt(avg((r) => r.ext), 1)}`],
    ...CHECK_DAYS.filter((d) => d <= days).map((d) => [`top-3 company power @ day ${d}`, fmt(avg((r) => r.powerAt[d]))]),
    ['campaigns offered / taken', `${fmt(avg((r) => r.campSeen), 1)} / ${fmt(avg((r) => r.campTaken), 1)}`],
    // 전투 모드: 확률 대신 보낸 편성의 예상 전력비 R 의 평균 (1 = 반반)
    res.every((r) => r.battle) ? ['final battle attempts (avg forecast R)', `${fmt(avg((r) => r.finalTries), 2)} (${fmt(avg((r) => r.finalChance) * N / Math.max(1, res.filter((r) => r.finalTries).length), 2)})`]
      : ['final battle attempts (avg chance)', `${fmt(avg((r) => r.finalTries), 2)} (${fmt(avg((r) => r.finalChance) * 100 * N / Math.max(1, res.filter((r) => r.finalTries).length), 1)}%)`],
    ['avg own company size (end)', fmt(avg((r) => r.avgCompanySize), 2)],
    ['avg dispatched group size', fmt(avg((r) => r.avgGroup), 2)],
    res.every((r) => r.battle) ? ['avg forecast R of taken contracts', fmt(avg((r) => r.avgChance), 2)] : ['avg success chance of taken contracts', `${fmt(avg((r) => r.avgChance) * 100, 1)}%`],
    ['contracts taken: monster / conflict / campaign', `${fmt(avg((r) => r.monster))} / ${fmt(avg((r) => r.conflict))} / ${fmt(avg((r) => r.campaigns))}`],
    ['completed / failed / fallen', `${fmt(avg((r) => r.completed))} / ${fmt(avg((r) => r.failed))} / ${fmt(avg((r) => r.fallen), 1)}`],
    ['bosses slain', fmt(avg((r) => r.bosses), 1)],
    ['calamity rose (avg day)', `${res.filter((r) => r.calDay).length} (${Math.round(avg((r) => r.calDay) * N / Math.max(1, res.filter((r) => r.calDay).length))})`],
    ['calamity defeated (avg day)', `${res.filter((r) => r.calDefeated).length} (${Math.round(avg((r) => r.calDefDay) * N / Math.max(1, res.filter((r) => r.calDefeated).length))})`],
    ['dark age (game over)', res.filter((r) => r.over === 'darkness').length],
  ];
  if (res.every((r) => r.battle)) {
    // 전투 모드 표: 판들을 합친 값
    const sum = (f) => res.reduce((a, r) => a + f(r.battle), 0);
    const merge = (key) => { const o = {}; res.forEach((r) => Object.entries(r.battle[key]).forEach(([k, [n, w]]) => { o[k] = o[k] || [0, 0]; o[k][0] += n; o[k][1] += w; })); return o; };
    const rate = ([n, w]) => `${n ? ((100 * w) / n).toFixed(1) : '-'}% (n=${n})`;
    const byBand = merge('byBand'), byDay = merge('byDay'), byKind = merge('byKind');
    const tiers = ['great', 'success', 'fail', 'disaster'].map((t) => sum((b) => b.tiers[t]));
    const tn = tiers.reduce((a, b) => a + b, 0) || 1;
    const mb = sum((b) => b.memberBattles) || 1;
    rows.push(['-- battle mode (Game.RESOLVE = battle)', '']);
    [0, 1, 2, 3, 4].forEach((b) => rows.push([`win rate, forecast ${BAND_NAMES[b]}`, byBand[b] ? rate(byBand[b]) : '-']));
    ['001-030', '031-060', '061-120', '121-240', '241-365'].forEach((k) => { if (byDay[k]) rows.push([`win rate, days ${k}`, rate(byDay[k])]); });
    Object.keys(byKind).sort().forEach((k) => rows.push([`win rate, ${k}`, rate(byKind[k])]));
    const byHeads = merge('byHeads'), tout = merge('timeout');
    ['1', '2', '3', '4+'].forEach((h) => rows.push([`win rate by heads ${h}: 백중 / 우세 / 압도`, ['백중', '우세', '압도'].map((w) => (byHeads[`${h} ${w}`] ? rate(byHeads[`${h} ${w}`]) : '-')).join(' | ')]));
    Object.keys(tout).sort().forEach((k) => rows.push([`lost on time, ${k}`, rate(tout[k])]));
    rows.push(['tiers great/success/fail/disaster', tiers.map((t) => `${((100 * t) / tn).toFixed(1)}%`).join(' / ')]);
    rows.push(['offers seen by band 무모..압도 (per game)', [0, 1, 2, 3, 4].map((b) => fmt(sum((x) => x.offered[b]) / N, 1)).join(' / ')]);
    // 게시판의 폭: 일반 의뢰를 가장 나은 직속 용병단의 예상으로 (사흘에 한 번)
    const boards = {};
    res.forEach((r) => Object.entries(r.battle.boards || {}).forEach(([k, b]) => { const o = (boards[k] = boards[k] || { n: 0, w: [0, 0, 0, 0, 0], hard: 0, easy: 0, both: 0, mid: 0, top: 0 }); o.n += b.n; b.w.forEach((x, i) => { o.w[i] += x; }); o.hard += b.hard; o.easy += b.easy; o.both += b.both; o.mid += b.mid || 0; o.top += b.top || 0; }));
    Object.keys(boards).sort().forEach((k) => { const b = boards[k]; rows.push([`board days ${k}: per board 무모..압도 | has ≤열세 / ≥우세 / both / ≤백중 | top ★`, `${b.w.map((x) => (x / b.n).toFixed(2)).join(' / ')} | ${Math.round(100 * b.hard / b.n)}% / ${Math.round(100 * b.easy / b.n)}% / ${Math.round(100 * b.both / b.n)}% / ${Math.round(100 * b.mid / b.n)}% | ${(b.top / b.n).toFixed(1)} (n=${b.n})`]); });
    rows.push(['contracts taken by band 무모..압도 (per game)', [0, 1, 2, 3, 4].map((b) => fmt(sum((x) => x.taken[b]) / N, 1)).join(' / ')]);
    rows.push(['downed / injured per member-battle', `${((100 * sum((b) => b.downed)) / mb).toFixed(1)}% / ${((100 * sum((b) => b.injured)) / mb).toFixed(1)}% (avg ${fmt(sum((b) => b.injDays) / Math.max(1, sum((b) => b.injured)), 1)} days)`]);
    rows.push(['deaths per game: special / other', `${fmt(sum((b) => b.deathsSpecial) / N, 2)} / ${fmt(sum((b) => b.deathsOther) / N, 2)}`]);
    rows.push(['avg pay on a lost contract', fmt(sum((b) => b.lossPay) / Math.max(1, sum((b) => b.losses)))]);
    rows.push(['relief contracts offered / taken (total)', `${sum((b) => b.relief)} / ${sum((b) => b.reliefTaken)}`]);
    rows.push(['captain-only days (total) / lowest merc count (avg)', `${sum((b) => b.captainOnlyDays)} / ${fmt(sum((b) => b.minMercs) / N, 1)}`]);
  }
  const w = Math.max(...rows.map((r) => String(r[0]).length));
  return rows.map(([k, v]) => `${String(k).padEnd(w)}  ${v}`).join('\n');
}

if (require.main === module) {
  if (process.argv[2] === '--worker') {
    process.on('message', (m) => { process.send(run(m.seed, m.days, m.mode, { resolve: m.resolve, knobs: m.knobs }), () => process.exit(0)); });
  } else {
    // 위치 인자: [runs] [days] [mode]. --resolve X, --jobs N 은 어디에 두어도 된다
    const argv = process.argv.slice(2), pos = [];
    let jobs = 1;
    const knobs = {};
    for (let i = 0; i < argv.length; i++) {
      if (argv[i] === '--resolve') i++;
      else if (argv[i] === '--jobs') jobs = Math.max(1, +argv[++i] || 1);
      else if (argv[i] === '--set') setKnob(knobs, argv[++i]);
      else pos.push(argv[i]);
    }
    const N = +pos[0] || 12;
    const days = +pos[1] || 365;
    const mode = pos[2] || 'all';
    const seed0 = +process.env.SIM_SEED || 1;
    const done = (res) => {
      if (process.env.SIM_JSON) console.log(JSON.stringify(res, null, 1));
      else console.log(`root: ${ROOT}${RESOLVE === 'battle' ? ' | resolve: battle' : ''}${Object.keys(knobs).length ? ` | knobs ${JSON.stringify(knobs)}` : ''}\n${summarize(res, days)}`);
    };
    if (jobs <= 1) {
      const res = [];
      for (let i = 0; i < N; i++) res.push(run(seed0 + i, days, mode, { knobs }));
      done(res);
    } else {
      const { fork } = require('child_process');
      const res = new Array(N);
      let next = 0, live = 0;
      const spawn = () => {
        if (next >= N) { if (!live) done(res); return; }
        const i = next++;
        live++;
        const ch = fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
        ch.on('message', (m) => { res[i] = m; });
        ch.on('exit', (code) => { live--; if (code || !res[i]) { console.error(`worker ${seed0 + i} failed`); process.exit(1); } spawn(); });
        ch.send({ seed: seed0 + i, days, mode, resolve: RESOLVE, knobs });
      };
      for (let j = 0; j < jobs; j++) spawn();
    }
  }
}

module.exports = { run, summarize, makeScript, ROOT };
