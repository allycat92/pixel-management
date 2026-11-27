#!/usr/bin/env node
// 그려진 달리기 칸의 발 미끄러짐 측정 (화면 없이): 실제 전투(봇 보고서 → Battle.plan/findBattle/setup/step)를 재생 고리(play)와 같은
// 시계로 돌리며, 그리기와 같은 gaitUpdate → pose → screenX 를 불러 칸마다 디딘 발끝의 화면 x(640px 캔버스)를 잰다.
// 잔차 = (다음 디딘 칸이 처음 보일 때의 발끝 x − 이 칸이 처음 보일 때의 발끝 x) × 나아가는 쪽 (0 = 발이 땅에 붙음, − = 뒤로 미끄러짐).
// "첫 걸음" = 달리기 칸이 (대기·공격 등 다른 칸 뒤에) 처음 보인 묶음의 첫 디딘 칸 넘김, "달리는 중" = 그 뒤의 넘김.
//   node tools/sim/gait_probe.js [battle.js 경로=js/battle.js] [--battles 8] [--speed 1] [--fps 60] [--json]
// 모든 유닛에 한 시트(경량 archer · 중량 ironwall · 로브 mage)를 입혀 같은 움직임으로 부류마다 잰다. 그림·속도는 건드리지 않는다.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const zlib = require('zlib');
const { run, ROOT } = require('./bot');

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const SRC = argv[0] && !argv[0].startsWith('--') ? argv[0] : path.join(ROOT, 'js', 'battle.js');
const NB = +opt('--battles', 8), SPEED = +opt('--speed', 1), FPS = +opt('--fps', 60), JSON_OUT = argv.includes('--json');
const SHEETS = [['light', 'sheet/class/archer'], ['heavy', 'sheet/captain/ironwall'], ['robe', 'sheet/class/mage']];

// ── PNG (RGBA 8비트, 비월 없음) ──
function readPng(file) {
  const b = fs.readFileSync(file);
  let p = 8, w = 0, h = 0, ct = 0;
  const idat = [];
  while (p < b.length) {
    const len = b.readUInt32BE(p), type = b.toString('ascii', p + 4, p + 8), d = b.subarray(p + 8, p + 8 + len);
    if (type === 'IHDR') { w = d.readUInt32BE(0); h = d.readUInt32BE(4); ct = d[9]; if (d[8] !== 8 || ct !== 6 || d[12]) throw new Error('RGBA8 only'); }
    else if (type === 'IDAT') idat.push(d);
    p += 12 + len;
  }
  const raw = zlib.inflateSync(Buffer.concat(idat)), bpp = 4, st = w * bpp, out = Buffer.alloc(w * h * bpp);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (st + 1)], row = raw.subarray(y * (st + 1) + 1, (y + 1) * (st + 1));
    for (let x = 0; x < st; x++) {
      const a = x >= bpp ? out[y * st + x - bpp] : 0, up = y ? out[(y - 1) * st + x] : 0, c = y && x >= bpp ? out[(y - 1) * st + x - bpp] : 0;
      let v = row[x];
      if (f === 1) v += a; else if (f === 2) v += up; else if (f === 3) v += (a + up) >> 1;
      else if (f === 4) { const q = a + up - c, pa = Math.abs(q - a), pb = Math.abs(q - up), pc = Math.abs(q - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? up : c; }
      out[y * st + x] = v & 255;
    }
  }
  return { width: w, height: h, data: out };
}
// 그리기 쪽 opaqueBox·spanOf 가 쓰는 만큼의 가짜 캔버스 (drawImage 는 배율 없이 복사, getImageData)
function fakeCanvas() {
  const c = { width: 0, height: 0, _d: null };
  const ctx = {
    drawImage(src, sx, sy, sw, sh, dx = 0, dy = 0) {
      if (!c._d) c._d = new Uint8ClampedArray(c.width * c.height * 4);
      const sd = src.data || src._d, W = src.width;
      for (let y = 0; y < sh; y++) for (let x = 0; x < sw; x++) {
        const tx = dx + x, ty = dy + y; if (tx < 0 || ty < 0 || tx >= c.width || ty >= c.height) continue;
        const si = ((sy + y) * W + sx + x) * 4, ti = (ty * c.width + tx) * 4;
        for (let k = 0; k < 4; k++) c._d[ti + k] = sd[si + k];
      }
    },
    getImageData(x, y, w, h) { if (!c._d) c._d = new Uint8ClampedArray(c.width * c.height * 4); return { data: c._d }; },
    putImageData() {}, fillRect() {}, save() {}, restore() {}, translate() {}, scale() {},
  };
  c.getContext = () => ctx;
  return c;
}

// 시트의 디딘 발끝 x (칸 px, 맨 아래 줄): 걸음마다 첫 칸은 가장 앞 발끝, 다음 칸은 (앞 칸 발끝 − 보폭/4) 에 가장 가까운 발 덩어리의 앞끝
function toeTable(img, m, cls) {
  const a = m.anims.run, ds = m.runStride, y = m.anchor[1] - 1, toes = {};
  const plantN = cls === 'light' ? 3 : 4;
  const segs = (j) => {
    const [fx, fy] = m.frames[a.from + j], s = [];
    let st = -1;
    for (let x = 0; x <= m.cell[0]; x++) {
      const on = x < m.cell[0] && img.data[((fy + y) * img.width + fx + x) * 4 + 3] >= 40;
      if (on && st < 0) st = x; if (!on && st >= 0) { s.push([st, x - 1]); st = -1; }
    }
    return s;
  };
  for (const base of [0, 4]) {
    let prev = null;
    for (let j = base; j < base + plantN; j++) {
      const s = segs(j);
      if (!s.length) break;
      const t = prev == null ? Math.max(...s.map((q) => q[1])) : s.map((q) => q[1]).sort((p, q) => Math.abs(p - (prev - ds / 4)) - Math.abs(q - (prev - ds / 4)))[0];
      toes[j] = t; prev = t;
    }
  }
  return { toes, plantN };
}

const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets/art/manifest.json'), 'utf8'));
function loadSheet(id) {
  const e = manifest[id], meta = e.sheet, anims = {};
  Object.entries(meta.anims).forEach(([k, a]) => { const ms = a.ms; anims[k] = { from: a.from, to: a.to, ms, total: ms.reduce((x, y) => x + y, 0) }; });
  return { id, img: readPng(path.join(ROOT, e.file)), meta: { ...meta, facing: meta.facing || 1, anims } };
}

// battle.js 를 그리기 내부 함수가 보이게 읽는다 (시험용으로 return 에만 덧붙임 — 원본 파일은 그대로)
const bsrc = fs.readFileSync(SRC, 'utf8').replace('return { play, stop, plan,',
  'return { _probe: { gaitUpdate, pose, rsOf, stature, lungeOf, screenX, ingest, updateView, aboutToStrike, triggerAttack, DT, Z }, play, stop, plan,');
if (!bsrc.includes('_probe')) throw new Error('return 줄을 못 찾음');
const PRELUDE = `var UI = { h: { soldierLook(f, i) { const sd = FACTIONS[f].soldier || FACTIONS.crown.soldier;
  return { cls: sd.classes[i % sd.classes.length], skin: sd.skins[i % sd.skins.length], hair: sd.hairs[(i * 7) % sd.hairs.length], longHair: i % 3 === 1, tint: { outfit: FACTIONS[f].color, accent: FACTIONS[f].accent } }; } } };
var Sprites = {}; var Art = undefined;`;
// tools/sim/bot.js makeScript 와 같은 묶음에 덧붙인 battle.js (와 이동 부류 표)를 붙인다
const gaitJs = fs.readFileSync(path.join(ROOT, 'js', 'gait_classes.js'), 'utf8');
const script = new vm.Script((PRELUDE + '\n'
  + ['data.js', 'classes.js', 'world.js', 'content.js', 'game.js', 'company.js', 'faction.js', 'contract.js', 'captains.js', 'stats.js', 'muster.js']
    .map((f) => fs.readFileSync(path.join(ROOT, 'js', f), 'utf8')).join('\n')
  + '\n' + gaitJs + '\n' + bsrc
  + '\nthis.Game=Game;this.PROMOTIONS=PROMOTIONS;this.PROMOTE_COST=PROMOTE_COST;this.STARTER_CAPTAINS=STARTER_CAPTAINS;this.MASTERS=MASTERS;this.FACILITIES=FACILITIES;this.CALAMITY_DARKNESS=CALAMITY_DARKNESS;this.Stats=Stats;this.Battle=Battle;this.GAIT_CLASSES=GAIT_CLASSES;'),
  { filename: 'probe-bundle.js' });

// 전투 모으기: 봇 판에서 보고서를 고루 골라 plan → findBattle → setup
const battles = [];
for (let seed = 1; battles.length < NB && seed < 20; seed++) {
  let seen = 0;
  try {
    run(seed, 400, 'all', {
      script, shadow: false,
      onReport(report, G, ctx) {
        if (++seen % 7 || battles.length >= NB) { if (battles.length >= NB) throw new Error('enough'); return; }
        battles.push({ rep: JSON.parse(JSON.stringify(report)), ctx });
      },
    });
  } catch (e) { if (e.message !== 'enough') throw e; }
}

function measure(cls, sheetId) {
  const res = { first: [], firstMid: [], mid: [], episodes: 0, startCells: {} };
  for (const { rep, ctx } of battles) {
    const B = ctx.Battle, P = B._probe;
    const sh = loadSheet(sheetId);
    const m = sh.meta, a = m.anims.run, { toes, plantN } = toeTable(sh.img, m, cls);
    if (process.env.PROBE_TOES) console.error(cls, JSON.stringify(toes));
    ctx.document = { createElement: () => fakeCanvas() };
    ctx.Art = { sheetFor: () => sh, anim: (mm, n) => mm.anims[n] || mm.anims.idle, img: () => null, image: () => null };
    const groups = B.plan(rep), found = B.findBattle(groups, rep.outcome, rep.seed || rep.quest.id * 7919 + 17);
    const st = B.setup(groups, found.bias, found.seed);
    const view = { parts: [], sparks: [], flares: [], puffs: [], downSeen: new Set(), sigils: [], slashes: [], vfx: [], amb: [], shake: 0, stop: 0, flash: 0, flashColor: '#fff', clock: 0, rs: new Map(), groundLum: 128, speedK: SPEED };
    const tr = new Map();   // 유닛 → { cell, X0, s, epFirst, nInEp, toeAt }
    const dt = 1 / FPS;
    let acc = 0;
    for (let f = 0; f < FPS * 90 && !(st.over && st.t - st.endT > 0.6); f++) {
      if (view.stop > 0) view.stop = Math.max(0, view.stop - dt);
      else { acc += dt * SPEED * 1.3; view.clock += dt * Math.min(2, SPEED) * 1.3; view.idleClock = (view.idleClock || 0) + dt; }
      while (acc >= P.DT) { acc -= P.DT; B.step(st); st.fx.forEach((x) => { x.t += P.DT; }); st.fx = st.fx.filter((x) => x.t < (x.kind === 'label' ? 1.2 : 0.7)); try { P.ingest(view, st); } catch (e) { /* 효과 그리기 준비만 실패 */ } }
      try { P.updateView(view, dt); } catch (e) { /* 입자 */ }
      for (const u of st.units.filter((x) => !x.fled)) {
        const r = P.rsOf(view, u);
        if (u.lunge > r.prevLunge + 0.01) { P.triggerAttack(view, u, 'attack', true); r.atkMelee = true; }
        if (u.flash > r.prevFlash + 0.01) r.hitAt = view.clock;
        r.prevLunge = u.lunge; r.prevFlash = u.flash;
        const S = P.stature(view, u), face = u.face || (u.side === 0 ? 1 : -1);
        P.gaitUpdate(view, st, u, r, S.h, face);
        if (view.clock - r.atkAt > r.atkDur && P.aboutToStrike(st, u, r)) {
          if (view.clock - (r.windAt == null ? -9 : r.windAt) > 0.25) r.windStart = view.clock;
          r.windAt = view.clock;
        }
        const fr = P.pose(view, u), flip = face !== fr.face;
        const kt = r.kickAt != null ? view.clock - r.kickAt : 9;
        const push = face * P.lungeOf(view, u, r, fr) + (kt >= 0 && kt < 0.18 ? r.kickDir * r.kickPx * (1 - kt / 0.18) : 0);
        const X = Math.round(P.screenX(view, u, fr, flip, push));
        const fi = m.frames.findIndex((q) => q[0] === fr.sx && q[1] === fr.sy);
        const cell = u.alive && fi >= a.from && fi <= a.to ? fi - a.from : -1;
        let T = tr.get(u);
        if (!T) tr.set(u, T = { cell: -1 });
        if (cell < 0) { T.cell = -1; continue; }
        const s = flip ? -1 : 1, toeX = toes[cell] == null ? null : (flip ? X + m.anchor[0] - toes[cell] : X - m.anchor[0] + toes[cell]);
        if (T.cell < 0) {   // 새 달리기 묶음
          res.episodes++; res.startCells[cell] = (res.startCells[cell] || 0) + 1;
          T.ep = true; T.firstCell = cell; T.planted = 0; T.cell = cell; T.toe = toeX; T.s = s; T.push = push !== 0;
          continue;
        }
        if (cell === T.cell) { if (push !== 0) T.push = true; continue; }
        // 칸 넘김
        const same = toes[T.cell] != null && toeX != null && cell === T.cell + 1 && Math.floor(cell / 4) === Math.floor(T.cell / 4) && (cell % 4) < plantN;
        if (same && !T.push && s === T.s) {
          const v = +(s * (toeX - T.toe)).toFixed(2);
          if (T.planted === 0) (T.firstCell === T.cell ? res.first : res.firstMid).push(v); else res.mid.push(v);
          T.planted++;
        }
        T.cell = cell; T.toe = toeX; T.s = s; T.push = push !== 0;
      }
    }
  }
  return res;
}

const stat = (xs) => {
  if (!xs.length) return { n: 0 };
  const s = [...xs].sort((p, q) => p - q), mean = xs.reduce((p, q) => p + q, 0) / xs.length;
  const within2 = xs.filter((v) => Math.abs(v) <= 2).length / xs.length;
  const hist = {}; xs.forEach((v) => { const k = Math.round(v); hist[k] = (hist[k] || 0) + 1; });
  return { hist, n: xs.length, mean: +mean.toFixed(2), min: s[0], p10: s[Math.floor(s.length * 0.1)], p90: s[Math.floor(s.length * 0.9)], max: s[s.length - 1], within2: +(within2 * 100).toFixed(1) };
};
const out = { src: path.relative(ROOT, SRC), speed: SPEED, fps: FPS, battles: battles.length, classes: {} };
for (const [cls, id] of SHEETS) {
  const r = measure(cls, id);
  out.classes[cls] = { sheet: id, episodes: r.episodes, startCells: r.startCells, firstStep: stat(r.first), firstFullCell: stat(r.firstMid), midRun: stat(r.mid) };
}
if (JSON_OUT) console.log(JSON.stringify(out, null, 1));
else {
  console.log(`src ${out.src}  speed x${SPEED}  ${FPS}fps  battles ${out.battles}`);
  console.log('class  sheet                    | first step (episode starts in that cell): n mean min..max  |±2|%  | mid-run: n mean min..max |±2|%');
  for (const [cls, c] of Object.entries(out.classes)) {
    const f = c.firstStep, md = c.midRun;
    console.log(`${cls.padEnd(6)} ${c.sheet.padEnd(24)} | ${String(f.n).padStart(4)} ${String(f.mean).padStart(6)} ${f.min}..${f.max} ${f.within2}% | ${String(md.n).padStart(5)} ${String(md.mean).padStart(6)} ${md.min}..${md.max} ${md.within2}%`);
  }
}
