#!/usr/bin/env node
// 그림자 전투 보정 도구: 봇이 길드를 운영하는 판을 돌리며, 파견한 의뢰마다 "능력치 전투라면 어떻게 끝났을까"를 모아 표로 낸다.
// 게임의 실제 결과는 여전히 판정(성공 확률)이 정한다 — 여기서 재는 것은 귀환 때 그림자로 돌린 능력치 전투(js/muster.js, Battle.run)다.
//
//   node tools/sim/shadow.js [seeds=6] [days=200] [옵션...]
//     --seed0 N            첫 시드 (기본 1, 또는 SIM_SEED)
//     --set KEY=VALUE      조정값 덮어쓰기 (js/stats.js KN). 여러 번 쓸 수 있다: --set ENEMY_K=0.7 --set KIND_K.boss=1.1 --set ARCH.blob.hp=1.6
//     STAT_KNOBS='{"ENEMY_K":0.7}'   환경 변수로도 같은 일을 한다 (--set 이 나중에 덮는다)
//     --sweep KEY=a,b,c    값마다 한 번씩 돌려 한 줄 요약을 낸다 (여러 개면 모든 조합). 예: --sweep ENEMY_K=0.6,0.7,0.8 --sweep SUPPORT_K=0.4,0.6
//     --offers             봇이 보내지 않은 의뢰(성공 확률이 낮아 포기한 것)도 같은 편성으로 돌려 표에 넣는다
//     --guard              출격 중 장비 잠금을 켠다 (실제 게임과 같다. 봇의 판이 md5 기준과 달라진다)
//     --check              불변 검사: 같은 편성 → 같은 기록(다시 돌리기 / JSON 왕복 / 한 틱씩 돌리기 + 결판 뒤 2.2초), 파티를 바꿔도 같은 적 편성,
//                          굳힌 편성이 귀환 때까지 그대로, 편성·그림자 전투가 Math.random 과 게임 상태를 건드리지 않음. 위반이 있으면 종료 코드 1
//     --jobs N             시드를 N 개 프로세스로 나눠 돌린다 (기본 1)
//     --out FILE.json      파견별 행을 JSON 으로 (기본: 임시 폴더). --csv FILE.csv 로 CSV 도 낸다
//     --resolve battle     3단계 전투 모드로 돌린다 (또는 SIM_RESOLVE=battle): 그림자가 아니라 결과를 정한 실제 전투(js/muster.js battleResolve)를 잰다.
//                          봇은 다섯 단어로 의뢰를 고른다 (tools/sim/bot.js). rolled·chance 열은 이때 뜻이 없다. --offers 는 봇이 살펴보고 보내지 않은 의뢰.
// 표: 성공 확률 십분위별 / 날짜 구간별 / 예상 전력비(R) 구간별 / 적 갈래별 (+ 의뢰 갈래, ★) — docs/plans/battle_stats/feasibility.md 의 표와 같은 꼴
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync, fork } = require('child_process');
const { run, makeScript, ROOT } = require('./bot');

// ───────── 인자 ─────────
function parseArgs(argv) {
  const a = { pos: [], set: [], sweep: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--set' || v === '--sweep') a[v.slice(2)].push(argv[++i]);
    else if (['--seed0', '--jobs', '--out', '--csv', '--resolve'].includes(v)) a.flags[v.slice(2)] = argv[++i];
    else if (v.startsWith('--')) a.flags[v.slice(2)] = true;
    else a.pos.push(v);
  }
  return a;
}
function assignment(input) {
  const i = input ? input.indexOf('=') : -1;
  if (i <= 0 || !input.slice(i + 1).trim()) throw new Error(`expected KEY=VALUE: ${input || '(missing)'}`);
  return [input.slice(0, i), input.slice(i + 1).trim()];
}
function knobValue(v) {
  if (v.startsWith('{') || v.startsWith('[')) return JSON.parse(v);
  return v && !isNaN(+v) ? +v : v === 'true' ? true : v === 'false' ? false : v;
}
const valueType = (v) => v === null ? 'null' : Array.isArray(v) ? 'array' : typeof v;
function validateValue(expected, value, key) {
  const type = valueType(expected);
  if (valueType(value) !== type || (type === 'number' && !Number.isFinite(value))) {
    throw new Error(`invalid knob ${key || 'STAT_KNOBS'}: expected ${type === 'number' ? 'finite number' : type}`);
  }
  if (type === 'object' || type === 'array') {
    if (type === 'array' && value.length !== expected.length) throw new Error(`invalid knob ${key}: expected ${expected.length} entries`);
    Object.entries(value).forEach(([k, v]) => {
      const sub = key ? `${key}.${k}` : k;
      if (!Object.hasOwn(expected, k)) throw new Error(`unknown knob: ${sub}`);
      validateValue(expected[k], v, sub);
    });
  }
}
function validatePath(schema, key, value) {
  let expected = schema;
  for (const k of key.split('.')) {
    if (expected == null || typeof expected !== 'object' || !Object.hasOwn(expected, k) || k === 'length') {
      throw new Error(`unknown knob: ${key}`);
    }
    expected = expected[k];
  }
  validateValue(expected, value, key);
}
function setPath(obj, key, val) {
  const ks = key.split('.');
  let o = obj;
  ks.slice(0, -1).forEach((k) => { o = o[k] = (o[k] && typeof o[k] === 'object') ? o[k] : {}; });
  o[ks[ks.length - 1]] = val;
}

// ───────── 한 판 ─────────
const band = (d) => (d <= 30 ? '001-030' : d <= 60 ? '031-060' : d <= 120 ? '061-120' : d <= 240 ? '121-240' : '241-365');
// 판 하나를 돌려 파견별 행을 모은다. cfg: { knobs, offers, guard, check }
function playSeed(seed, days, cfg) {
  const script = makeScript(['battle.js'], `var STAT_KNOBS = ${JSON.stringify(cfg.knobs || {})};`);
  const rows = [], offers = [], seen = new Set();
  const chk = { battles: 0, rerun: 0, json: 0, stepped: 0, after: 0, roster: 0, rosterN: 0, thawed: 0, random: 0, state: 0, noSpec: 0, err: 0 };
  const frozen = new Map();   // 출격 id → 굳힌 편성(JSON). 귀환할 때까지 한 글자도 바뀌면 안 된다
  let ms = 0;
  const rowOf = (c, spec, est, rec, v, St, extra) => ({
    seed, star: c.level, type: c.type, cat: c.cat, kind: St.kindOf(c), foe: St.foeKind(spec), arch: (spec.groups.find((g) => g.kind === 'foe').units[0].arch) || 'soldier',
    rule: spec.rule, lv: spec.lv, k: spec.k, R: est.R, band: est.band, win: rec.winner === 0 ? 1 : 0, tier: v.outcome, t: rec.t, end: rec.end,
    ours: v.ours, recruits: spec.groups.reduce((a, g) => a + g.units.filter((u) => u.recruit).length, 0), heads: spec.heads, need: spec.need,
    olv: (() => { const lv = spec.groups.filter((g) => g.kind === 'own' || g.kind === 'ext').flatMap((g) => g.units.filter((u) => !u.recruit).map((u) => u.level || g.level || 1)); return lv.length ? +(lv.reduce((a, b) => a + b, 0) / lv.length).toFixed(1) : 0; })(),
    down: v.down, fled: v.fled, low: v.low, downShare: v.ours ? +(v.down / v.ours).toFixed(3) : 0, hash: rec.hash,
    ...(spec.bm && St.killTime ? { tk: +St.killTime(spec.groups).toFixed(2) } : {}), ...extra,   // 4단계: 적을 다 깎는 어림 시간(초), 시간 보정용
  });
  const battle = cfg.resolve === 'battle';
  const sentIds = new Set();   // 전투 모드: 보낸 의뢰 번호 (--offers 에서 뺀다)
  const res = run(seed, days, 'all', {
    script, shadow: !battle, equipGuard: !!cfg.guard, resolve: battle ? 'battle' : 'roll',
    onStart(G, ctx) {
      const St = ctx.Stats, B = ctx.Battle, M = ctx.Math;
      // 편성·그림자 전투가 도는 동안에는 게임의 난수를 세기만 하는 것으로 바꿔 둔다 (--check)
      const guarded = (fn) => {
        if (!cfg.check) return fn();
        const real = M.random, before = JSON.stringify(G.state);
        M.random = () => { chk.random++; return real(); };
        try { return fn(); } finally { M.random = real; if (JSON.stringify(G.state) !== before) chk.state++; }
      };
      const freeze = G.freezeMission;
      G.freezeMission = function (mission, c, units) {
        guarded(() => freeze.call(this, mission, c, units));
        if (!mission.spec) { chk.noSpec++; return; }
        if (!cfg.check) return;
        frozen.set(mission.id, JSON.stringify(mission.spec));
        // 같은 의뢰에 다른 파티를 보내도 적 편성(구성·능력치)은 같아야 한다: 첫 용병단만 / 그 용병단의 한 명만 / 다른 용병단
        const foes = (sp) => JSON.stringify(sp.groups.filter((g) => g.kind === 'foe'));
        const base = foes(mission.spec);
        const alts = [[units[0]]];
        if (units[0].memberIds && units[0].memberIds.length > 1) alts.push([{ companyId: units[0].companyId, memberIds: units[0].memberIds.slice(0, 1) }]);
        const other = G.state.companies.find((co) => !units.some((u) => u.companyId === co.id) && (!co.own || G.members(co).length));
        if (other) alts.push([other.own ? { companyId: other.id, memberIds: G.members(other).map((m) => m.id) } : { companyId: other.id }]);
        alts.forEach((us) => { chk.rosterN++; if (guarded(() => foes(G.muster(c, us))) !== base) chk.roster++; });
        if (JSON.stringify(guarded(() => G.muster(c, units, undefined, mission.id))) !== JSON.stringify(mission.spec)) chk.roster++;   // 같은 입력이면 같은 편성
      };
      // 전투 모드는 결과를 정하는 battleResolve 를, 기본은 그림자 shadowResolve 를 잰다 (둘 다 { spec, rec, verdict } 를 돌려준다)
      const hook = battle ? 'battleResolve' : 'shadowResolve';
      const shadow = G[hook];
      G[hook] = function (mission, report, mods) {
        const t0 = process.hrtime.bigint();
        const out = guarded(() => shadow.call(this, mission, report, mods));
        ms += Number(process.hrtime.bigint() - t0) / 1e6;
        if (!out) { chk.err++; return out; }
        const { spec, rec, verdict } = out, c = mission.contract;
        const est = battle ? out.est : { R: report.shadow.R, band: report.shadow.band };
        sentIds.add(c.id);
        rows.push(rowOf(c, spec, est, rec, verdict, St, {
          id: mission.id, cid: c.id, day: mission.startDay, ret: G.state.day, chance: +mission.chance.toFixed(4), rolled: battle ? verdict.outcome : report.outcome, sent: 1,
          ...(battle ? { foeShare: +out.share.toFixed(3), special: G.specialBattle(c) ? 1 : 0 } : {}) }));
        if (cfg.check) {
          chk.battles++;
          if (frozen.get(mission.id) !== JSON.stringify(mission.spec)) chk.thawed++;
          frozen.delete(mission.id);
          const same = (a, b) => a.hash === b.hash && JSON.stringify(a) === JSON.stringify(b);
          if (!same(B.run(spec), rec)) chk.rerun++;
          const copy = JSON.parse(JSON.stringify(spec));
          if (!same(B.run(copy), rec)) chk.json++;
          // 화면 재생이 하는 것처럼 한 틱씩: 결판이 난 순간의 기록과, 그 뒤 2.2초(44틱)를 더 돌린 뒤의 기록이 모두 같아야 한다
          const st = B.begin(copy);
          while (!st.over) B.step(st);
          if (!same(B.record(st), rec)) chk.stepped++;
          for (let i = 0; i < 44; i++) B.step(st);
          if (!same(B.record(st), rec)) chk.after++;
        }
        return out;
      };
    },
    onOffer: cfg.offers ? (c, units, ch, G, ctx) => {
      if (!battle && ch >= (c.campaign ? 0.55 : 0.6)) return;   // 보낼 의뢰는 귀환 때 잡힌다 (전투 모드는 끝에서 보낸 의뢰를 뺀다)
      const key = `${c.id}:${units.map((u) => u.companyId).join(',')}`;
      if (seen.has(key)) return;
      seen.add(key);
      const St = ctx.Stats, spec = G.muster(c, units), est = G.forecast(spec), rec = ctx.Battle.run(spec);
      const v = G.judge(spec, rec, G.partyMods(G.unitParts(units).allMembers));
      offers.push(rowOf(c, spec, est, rec, v, St, { id: c.id, cid: c.id, day: G.state.day, ret: 0, chance: +ch.toFixed(4), rolled: null, sent: 0 }));
    } : null,
  });
  if (battle) { const keep = offers.filter((o) => !sentIds.has(o.cid)); offers.length = 0; offers.push(...keep); }
  return { seed, res: { day: res.day, over: res.over, rank: res.rank, gold: res.gold, mercs: res.mercs, completed: res.completed, failed: res.failed, fallen: res.fallen },
    rows, offers, chk, ms };
}

// ───────── 표 ─────────
const mean = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN);
const qt = (a, p) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor((s.length - 1) * p)] : NaN; };
const pc = (v, d = 0) => (isNaN(v) ? '-' : `${(v * 100).toFixed(d)}%`);
const P = (s, n) => String(s).padStart(n), E = (s, n) => String(s).padEnd(n);
const TIERS4 = ['great', 'success', 'fail', 'disaster'];
const rolledWin = (r) => (r.rolled === 'great' || r.rolled === 'success' ? 1 : 0);
const tierMix = (x, key) => TIERS4.map((t) => pc(mean(x.map((r) => (r[key] === t ? 1 : 0))))).join('/');
function headline(x) {
  const sent = x.filter((r) => r.sent), def = x.filter((r) => !r.win);
  const t = x.map((r) => r.t);
  return [
    `n ${x.length} | shadow win ${pc(mean(x.map((r) => r.win)), 1)}${sent.length ? ` vs rolled ${pc(mean(sent.map(rolledWin)), 1)} (mean chance ${pc(mean(sent.map((r) => r.chance)), 1)})` : ''}`
      + ` | tiers g/s/f/d shadow ${tierMix(x, 'tier')}${sent.length ? `, rolled ${tierMix(sent, 'rolled')}` : ''}`,
    `battle seconds: p10 ${qt(t, 0.1).toFixed(1)} median ${qt(t, 0.5).toFixed(1)} p90 ${qt(t, 0.9).toFixed(1)} max ${qt(t, 1).toFixed(1)} | >=60 s ${pc(mean(t.map((v) => (v >= 60 ? 1 : 0))), 1)}`
      + ` | time limit ${pc(mean(x.map((r) => (r.end === 'time' ? 1 : 0))), 1)}`,
    `defeats ${def.length} (${pc(def.length / (x.length || 1), 1)}): by retreat ${pc(mean(def.map((r) => (r.end === 'retreat' ? 1 : 0))))} | all of ours down ${pc(mean(def.map((r) => (r.down === r.ours ? 1 : 0))))}`
      + ` | half or more of ours on their feet ${pc(mean(def.map((r) => (r.down <= r.ours / 2 ? 1 : 0))))} | mean share down ${pc(mean(def.map((r) => r.downShare)))}`,
    `wins: mean share of ours down ${pc(mean(x.filter((r) => r.win).map((r) => r.downShare)))} | nobody down ${pc(mean(x.filter((r) => r.win).map((r) => (r.down === 0 ? 1 : 0))))}`,
  ].join('\n  ');
}
function table(x, title, keyOf) {
  const o = {};
  x.forEach((r) => { const k = keyOf(r); if (k != null) (o[k] = o[k] || []).push(r); });
  const out = [`-- ${title}`,
    `${E('bin', 13)} ${P('n', 5)} ${P('chance', 7)} ${P('rolled', 7)} ${P('shadow', 7)} ${P('gap', 5)}  ${E('shadow tiers g/s/f/d', 20)} ${P('down', 5)} ${P('sec', 5)} ${P('R med', 6)}`];
  Object.keys(o).sort((a, b) => (isNaN(parseFloat(a)) || isNaN(parseFloat(b)) ? a.localeCompare(b) : parseFloat(a) - parseFloat(b) || a.localeCompare(b))).forEach((k) => {
    const y = o[k], sent = y.filter((r) => r.sent);
    const ch = mean(y.map((r) => r.chance)), sw = mean(y.map((r) => r.win));
    out.push(`${E(k, 13)} ${P(y.length, 5)} ${P(pc(ch), 7)} ${P(sent.length ? pc(mean(sent.map(rolledWin))) : '-', 7)} ${P(pc(sw), 7)} ${P(((sw - ch) * 100).toFixed(0), 5)}  ${E(tierMix(y, 'tier'), 20)} `
      + `${P(pc(mean(y.map((r) => r.downShare))), 5)} ${P(qt(y.map((r) => r.t), 0.5).toFixed(0), 5)} ${P(qt(y.map((r) => r.R), 0.5).toFixed(2), 6)}`);
  });
  return out.join('\n');
}
const decile = (r) => (r.chance >= 0.97 ? '0.97 (cap)' : r.chance >= 0.90 ? '0.90-0.97' : `${(Math.floor(r.chance * 10) / 10).toFixed(1)}-${((Math.floor(r.chance * 10) + 1) / 10).toFixed(1)}`);
const rBand = (r) => (r.R < 0.6 ? '0 <0.60' : r.R < 0.7 ? '1 0.60-0.70' : r.R < 0.8 ? '2 0.70-0.80' : r.R < 0.9 ? '3 0.80-0.90' : r.R < 1 ? '4 0.90-1.00' : r.R < 1.15 ? '5 1.00-1.15' : r.R < 1.5 ? '6 1.15-1.50' : '7 >=1.50');
const BANDS_KO = ['0 무모', '1 열세', '2 백중', '3 우세', '4 압도'];

// ───────── 여러 판 (필요하면 여러 프로세스로) ─────────
function playAll(seeds, days, cfg, jobs) {
  if (jobs <= 1 || seeds.length <= 1) return Promise.resolve(seeds.map((sd) => playSeed(sd, days, cfg)));
  return new Promise((resolve, reject) => {
    const out = new Array(seeds.length);
    let next = 0, live = 0, failed = false;
    const spawn = () => {
      if (failed) return;
      if (next >= seeds.length) { if (!live) resolve(out); return; }
      const i = next++;
      live++;
      const ch = fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
      ch.on('message', (m) => { out[i] = m; });
      ch.on('exit', (code) => { live--; if (code || !out[i]) { failed = true; reject(new Error(`worker for seed ${seeds[i]} failed (exit ${code})`)); } else spawn(); });
      ch.send({ seed: seeds[i], days, cfg });
    };
    for (let j = 0; j < jobs; j++) spawn();
  });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const ctx = {};
  makeScript().runInNewContext(ctx);
  const { KN, ARCH, REF, RANK } = ctx.Stats;
  // KIND_K is sparse in the game: omitted entries use the documented multiplier of 1.
  const schema = { ...KN, ARCH, REF, RANK,
    KIND_K: { normal: 1, story: 1, capStory: 1, boss: 1, campaign: 1, final: 1, ...KN.KIND_K } };
  const envKnobs = process.env.STAT_KNOBS ? JSON.parse(process.env.STAT_KNOBS) : {};
  validateValue(schema, envKnobs, '');
  const overrides = args.set.map((input) => {
    const [key, raw] = assignment(input);
    const value = knobValue(raw);
    validatePath(schema, key, value);
    return [key, value];
  });
  const axes = args.sweep.map((input) => {
    const [key, raw] = assignment(input);
    const vals = /^[{\[]/.test(raw) ? JSON.parse(`[${raw}]`) : raw.split(',').map((v) => knobValue(v.trim()));
    vals.forEach((value) => validatePath(schema, key, value));
    return { key, vals };
  });
  const knobsFrom = (extra = {}) => {
    const knobs = structuredClone(envKnobs);
    [...overrides, ...Object.entries(extra)].forEach(([key, value]) => setPath(knobs, key, structuredClone(value)));
    return knobs;
  };
  const N = +args.pos[0] || 6, days = +args.pos[1] || 200;
  const seed0 = +args.flags.seed0 || +process.env.SIM_SEED || 1;
  const seeds = Array.from({ length: N }, (_, i) => seed0 + i);
  const jobs = Math.max(1, +args.flags.jobs || 1);
  const resolve = (args.flags.resolve || process.env.SIM_RESOLVE) === 'battle' ? 'battle' : 'roll';
  const base = { offers: !!args.flags.offers, guard: !!args.flags.guard, check: !!args.flags.check, resolve };
  let commit = '?';
  try { commit = execFileSync('git', ['-C', ROOT, 'rev-parse', '--short', 'HEAD'], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch (e) { /* git 없이도 돈다 */ }
  console.log(`command: node tools/sim/shadow.js ${process.argv.slice(2).join(' ')}${process.env.STAT_KNOBS ? `   (STAT_KNOBS=${process.env.STAT_KNOBS})` : ''}`);
  console.log(`root ${ROOT} | commit ${commit} | seeds ${seeds[0]}..${seeds[N - 1]} x ${days} days | equip guard ${base.guard ? 'on' : 'off (same games as the bot md5 baseline)'}`
    + ` | resolve ${resolve}${resolve === 'battle' ? ' (the battle decides; "rolled" = the battle verdict)' : ''}`);
  const t0 = Date.now();

  // 값 훑기: 조합마다 한 줄
  if (axes.length) {
    let combos = [{}];
    axes.forEach((ax) => { combos = combos.flatMap((c) => ax.vals.map((v) => ({ ...c, [ax.key]: v }))); });
    const dayBands = ['001-030', '031-060', '061-120', '121-240', '241-365'].filter((b) => +b.slice(0, 3) <= days);
    console.log(`${E(axes.map((a) => a.key).join(' '), 26)} ${P('n', 5)} ${P('rolled', 7)} ${P('shadow', 7)}  ${E('shadow tiers g/s/f/d', 20)} ${P('sec', 5)} ${P('down', 5)}  ${dayBands.map((b) => P(b, 8)).join('')}  ${P('monster', 8)}${P('soldier', 8)}`);
    for (const combo of combos) {
      const got = await playAll(seeds, days, { ...base, knobs: knobsFrom(combo) }, jobs);
      const x = got.flatMap((g) => g.rows);
      const w = (y) => P(pc(mean(y.map((r) => r.win))), 8);
      console.log(`${E(axes.map((a) => combo[a.key]).join(' '), 26)} ${P(x.length, 5)} ${P(pc(mean(x.map(rolledWin)), 1), 7)} ${P(pc(mean(x.map((r) => r.win)), 1), 7)}  ${E(tierMix(x, 'tier'), 20)} `
        + `${P(qt(x.map((r) => r.t), 0.5).toFixed(1), 5)} ${P(pc(mean(x.map((r) => r.downShare))), 5)}  ${dayBands.map((b) => w(x.filter((r) => band(r.day) === b))).join('')}  ${w(x.filter((r) => r.foe === 'monster'))}${w(x.filter((r) => r.foe === 'soldier'))}`);
    }
    console.log(`run time ${((Date.now() - t0) / 1000).toFixed(1)} s`);
    return;
  }

  const knobs = knobsFrom();
  console.log(`knobs ${JSON.stringify(knobs)} (others: js/stats.js defaults)`);
  const got = await playAll(seeds, days, { ...base, knobs }, jobs);
  const rows = got.flatMap((g) => g.rows), offers = got.flatMap((g) => g.offers);
  const ms = got.reduce((a, g) => a + g.ms, 0);
  console.log(`\nDISPATCHED: ${headline(rows)}`);
  console.log(`  shadow battle ${(ms / (rows.length || 1)).toFixed(1)} ms each (muster is extra, at dispatch)`);
  const all = rows.concat(offers);
  if (offers.length) console.log(`\nNOT SENT (the bot's best party for offers under its threshold): ${headline(offers)}`);
  const lab = offers.length ? 'dispatched + not sent' : 'dispatched';
  console.log(`\n${table(all, `${lab}, by successChance decile`, decile)}`);
  console.log(`\n${table(rows, 'dispatched, by day band (day of dispatch)', (r) => band(r.day))}`);
  console.log(`\n${table(all, `${lab}, by forecast R`, rBand)}`);
  console.log(`\n${table(all, `${lab}, by forecast band (js/stats.js BANDS)`, (r) => BANDS_KO[r.band])}`);
  console.log(`\n${table(rows, 'dispatched, by enemy kind', (r) => r.foe)}`);
  console.log(`\n${table(rows, 'dispatched, by enemy archetype', (r) => r.arch)}`);
  console.log(`\n${table(rows, 'dispatched, by contract kind', (r) => r.kind)}`);
  console.log(`\n${table(rows, 'dispatched, by star', (r) => String(r.star).padStart(2, '0'))}`);
  console.log(`\n-- games: ${got.map((g) => `s${g.seed} day ${g.res.day}${g.res.over ? ` OVER:${g.res.over}` : ''} ${g.res.rank} gold ${g.res.gold} mercs ${g.res.mercs} done ${g.res.completed}/${g.res.failed} fallen ${g.res.fallen}`).join(' | ')}`);

  let bad = 0;
  const chk = got.reduce((a, g) => { Object.keys(g.chk).forEach((k) => { a[k] = (a[k] || 0) + g.chk[k]; }); return a; }, {});
  if (chk.err || chk.noSpec) { bad += chk.err + chk.noSpec; console.log(`\nERRORS: shadow battles that threw ${chk.err}, dispatches without a frozen spec ${chk.noSpec}`); }
  if (base.check) {
    bad += chk.rerun + chk.json + chk.stepped + chk.after + chk.roster + chk.thawed + chk.random + chk.state;
    console.log(`\nCHECK over ${chk.battles} battles: rerun mismatch ${chk.rerun} | JSON round trip mismatch ${chk.json} | stepped mismatch ${chk.stepped} | changed after over (+2.2 s) ${chk.after}`);
    console.log(`  enemy roster changed with the party ${chk.roster} (of ${chk.rosterN} alternative parties) | spec changed between dispatch and return ${chk.thawed}`);
    console.log(`  Math.random calls inside muster/shadow ${chk.random} | game state changed by muster/shadow ${chk.state}`);
    console.log(bad ? `  VIOLATIONS: ${bad}` : '  all 0');
  }

  const outFile = args.flags.out || path.join(os.tmpdir(), `shadow-${seeds[0]}-${N}x${days}-${process.pid}.json`);
  fs.writeFileSync(outFile, JSON.stringify({ command: process.argv.slice(2), commit, seeds, days, knobs, guard: base.guard, games: got.map((g) => g.res), rows, offers }));
  console.log(`\nrows: ${outFile} (${rows.length} dispatched${offers.length ? `, ${offers.length} not sent` : ''})`);
  if (args.flags.csv) {
    const cols = Object.keys(all[0] || {});
    fs.writeFileSync(args.flags.csv, [cols.join(',')].concat(all.map((r) => cols.map((c) => (r[c] == null ? '' : r[c])).join(','))).join('\n') + '\n');
    console.log(`csv:  ${args.flags.csv}`);
  }
  console.log(`run time ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  if (bad) process.exitCode = 1;
}

if (require.main === module) {
  if (process.argv[2] === '--worker') {
    process.on('message', (m) => { process.send(playSeed(m.seed, m.days, m.cfg), () => process.exit(0)); });
  } else main().catch((e) => { console.error(e); process.exit(1); });
}

module.exports = { playSeed };
