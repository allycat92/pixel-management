// FxSkel — 연출 뼈대(staging skeleton) 프리셋. docs/plans/effects_design.md §1.1 종류 A, §4.
// 보이지 않는 구조만 담는다: 곡선, 프레임 시계, 단계 틀, 배치, 방출기 물리, 화면 패턴, 앵커.
// 규칙 (§1.2): 이 파일에는 색 리터럴도, 그림 id·경로도 없다. 모든 함수는 (params, t, rng) → 숫자.
// 난수는 넘겨받은 rng 에서만 얻는다(Math.random 금지). tools/fxpreview/check.js 가 이 규칙을 검사한다.
// 매개변수 태그: physics(공유·기본값 있음) / style(눈에 보임 — 시그니처 스펙은 직접 적어야 한다, §1.2-4).
'use strict';

const FxSkel = (() => {
  const REG = {};

  // ───────── 결정론 난수 (mulberry32 + fnv1a) ─────────
  function fnv(...parts) {
    let h = 0x811c9dc5;
    const s = parts.join('|');
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return h >>> 0;
  }
  function mulberry32(a) {
    return function () {
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // 인스턴스 rng: (seed, layer, target, salt) 마다 독립 — 같은 시드면 몇 번을 그려도 같다
  const rng = (...parts) => mulberry32(fnv(...parts));
  const pick = (r, v) => (Array.isArray(v) && v.length === 2 && typeof v[0] === 'number' ? v[0] + (v[1] - v[0]) * r() : v);

  const clamp01 = (k) => (k < 0 ? 0 : k > 1 ? 1 : k);
  const lerp = (a, b, k) => a + (b - a) * k;

  // ───────── 등록 ─────────
  function def(name, d) { REG[name] = { name, ...d }; return REG[name]; }
  const get = (name) => REG[name] || null;
  const list = () => Object.keys(REG);

  // 스펙 값 + 스키마 → 실제 값. signature 면 style 기본값을 쓰지 않는다(빠진 이름을 missing 에 모은다).
  // 숫자 매개변수는 값, [min,max](rng 로 뽑음) 둘 다 받는다.
  function resolve(name, given, opt = {}) {
    const d = REG[name];
    if (!d) throw new Error(`FxSkel: unknown preset ${name}`);
    const out = {}, missing = [];
    const r = opt.rng || (() => 0.5);
    Object.entries(d.params || {}).forEach(([k, p]) => {
      if (given && given[k] !== undefined) out[k] = p.type === 'num' ? pick(r, given[k]) : given[k];
      else if (p.tag === 'style' && opt.signature) missing.push(k);
      else out[k] = p.def;
    });
    if (missing.length && opt.missing) opt.missing.push(...missing.map((m) => `${name}.${m}`));
    return out;
  }

  // ───────── 곡선 (k ∈ [0,1] → 값) ─────────
  def('curve.linear', { kind: 'curve', params: {}, fn: (p, k) => clamp01(k) });
  def('curve.easeOut', { kind: 'curve', params: { pow: { type: 'num', def: 2, tag: 'physics' } }, fn: (p, k) => 1 - Math.pow(1 - clamp01(k), p.pow) });
  def('curve.easeIn', { kind: 'curve', params: { pow: { type: 'num', def: 2, tag: 'physics' } }, fn: (p, k) => Math.pow(clamp01(k), p.pow) });
  // 들어오기-유지-나가기 봉투: t(초) → 0..1
  def('curve.envelope', {
    kind: 'curve',
    params: { in: { type: 'num', def: 0.2, tag: 'style' }, hold: { type: 'num', def: 1, tag: 'style' }, out: { type: 'num', def: 0.3, tag: 'style' } },
    fn: (p, t) => {
      if (t < 0) return 0;
      if (t < p.in) return p.in > 0 ? t / p.in : 1;
      if (t < p.in + p.hold) return 1;
      const k = (t - p.in - p.hold) / Math.max(1e-6, p.out);
      return k >= 1 ? 0 : 1 - k;
    },
  });
  // 순간 솟고 지수로 꺼짐: t(초) → 0..1
  def('curve.attackDecay', {
    kind: 'curve',
    params: { rise: { type: 'num', def: 0.02, tag: 'style' }, decay: { type: 'num', def: 0.15, tag: 'style' } },
    fn: (p, t) => (t < 0 ? 0 : t < p.rise ? t / Math.max(1e-6, p.rise) : Math.exp(-(t - p.rise) / Math.max(1e-6, p.decay))),
  });

  // ───────── 프레임 시계 ─────────
  // clock.hold: 프레임 목록 + 칸별 ms. once 면 마지막 칸 뒤 -1(끝), holdLast 면 마지막 칸 유지, loop 면 반복.
  def('clock.hold', {
    kind: 'clock',
    params: { frames: { type: 'list', def: [0], tag: 'style' }, ms: { type: 'list', def: [60], tag: 'style' }, mode: { type: 'enum', def: 'once', tag: 'style' } },
    fn: (p, t) => {
      if (t < 0) return -1;
      const ms = p.frames.map((_, i) => p.ms[Math.min(i, p.ms.length - 1)]);
      const total = ms.reduce((a, b) => a + b, 0);
      let x = t * 1000;
      if (p.mode === 'loop') x %= total;
      else if (x >= total) return p.mode === 'holdLast' ? p.frames[p.frames.length - 1] : -1;
      for (let i = 0; i < ms.length; i++) { if (x < ms[i]) return p.frames[i]; x -= ms[i]; }
      return p.frames[p.frames.length - 1];
    },
  });
  // 칸 길이 합(초)
  const clockLen = (p) => p.frames.reduce((a, _, i) => a + p.ms[Math.min(i, p.ms.length - 1)], 0) / 1000;

  // ───────── 단계 틀 ─────────
  // tl.phases: [[이름, 시작, 끝], ...] → t 의 단계와 단계 안 k
  def('tl.phases', {
    kind: 'timeline',
    params: { phases: { type: 'list', def: [], tag: 'style' } },
    fn: (p, t) => {
      for (const [name, a, b] of p.phases) if (t >= a && t < b) return { name, k: (t - a) / Math.max(1e-6, b - a) };
      return { name: null, k: 0 };
    },
  });

  // ───────── 시전자 동작 ─────────
  // actor.spin: 그려진 몸 칸으로 도는 것처럼 — 좌우 반전을 step 초마다 바꾼다. 끝에서 원래 방향(end 쪽)으로 멈춘다.
  def('actor.spin', {
    kind: 'actor',
    params: { at: { type: 'num', def: 0, tag: 'style' }, dur: { type: 'num', def: 0.3, tag: 'style' }, step: { type: 'num', def: 0.06, tag: 'style' } },
    fn: (p, t) => {
      if (t < p.at || t >= p.at + p.dur) return { spinning: false, flip: false };
      const n = Math.floor((t - p.at) / p.step);
      const last = Math.floor((p.dur - 1e-6) / p.step);
      // 마지막 칸은 늘 정면(flip false)으로 끝나게 홀짝을 맞춘다
      return { spinning: true, flip: ((last - n) & 1) === 1, step: n };
    },
  });

  // ───────── 배치 ─────────
  // place.stagger: 표적마다 지연. order 'nearest'(시전자에 가까운 순) | 'given'. 시드 흔들림 jit(초).
  def('place.stagger', {
    kind: 'place',
    params: { dt: { type: 'num', def: 0.05, tag: 'physics' }, jit: { type: 'num', def: 0, tag: 'style' }, order: { type: 'enum', def: 'nearest', tag: 'style' } },
    fn: (p, targets, origin, r) => {
      const idx = targets.map((_, i) => i);
      if (p.order === 'nearest') idx.sort((a, b) => Math.hypot(targets[a].x - origin.x, targets[a].y - origin.y) - Math.hypot(targets[b].x - origin.x, targets[b].y - origin.y));
      const out = new Array(targets.length);
      idx.forEach((ti, rank) => { out[ti] = Math.max(0, rank * p.dt + (r() * 2 - 1) * p.jit); });
      return out;
    },
  });
  // place.spreadHeights: 표적마다 서로 다른 높이(몸 높이 비율 lo..hi). n 칸으로 나눠 시드로 섞는다 → 둘이 같은 높이에 오지 않는다.
  def('place.spreadHeights', {
    kind: 'place',
    params: { lo: { type: 'num', def: 0.3, tag: 'style' }, hi: { type: 'num', def: 0.8, tag: 'style' }, jit: { type: 'num', def: 0.3, tag: 'style' } },
    fn: (p, n, r) => {
      const perm = Array.from({ length: n }, (_, i) => i);
      for (let i = n - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
      return perm.map((slot) => lerp(p.lo, p.hi, (slot + 0.5 + (r() * 2 - 1) * 0.5 * p.jit) / n));
    },
  });

  // place.minGap: 가로로 겹치는 선끼리 세로 간격을 gap px 이상으로 벌린다(각 선은 자기 [ymin,ymax] 안에서만 움직임).
  // items: [{ x0, x1, y, ymin, ymax }] → 새 y 목록. 결정론(정렬·반복 횟수 고정). 못 벌리면(몸이 너무 겹침) 남은 채로 둔다.
  def('place.minGap', {
    kind: 'place',
    params: { gap: { type: 'num', def: 5, tag: 'style' }, iters: { type: 'num', def: 24, tag: 'physics' } },
    fn: (p, items) => {
      const y = items.map((it) => it.y);
      const ov = (a, b) => items[a].x0 < items[b].x1 && items[b].x0 < items[a].x1;
      for (let k = 0; k < p.iters; k++) {
        let moved = false;
        const ord = y.map((_, i) => i).sort((a, b) => y[a] - y[b] || a - b);
        for (let a = 0; a < ord.length; a++) for (let b = a + 1; b < ord.length; b++) {
          const i = ord[a], j = ord[b];
          if (!ov(i, j)) continue;
          const d = y[j] - y[i];
          if (d >= p.gap) continue;
          const push = (p.gap - d) / 2;
          const ni = Math.max(items[i].ymin, y[i] - push), nj = Math.min(items[j].ymax, y[j] + push);
          // 한쪽이 벽에 막히면 다른 쪽이 나머지를 진다
          const left = p.gap - (nj - ni);
          y[i] = left > 0 ? Math.max(items[i].ymin, ni - left) : ni;
          y[j] = left > 0 && y[i] === items[i].ymin ? Math.min(items[j].ymax, y[i] + p.gap) : nj;
          moved = true;
        }
        if (!moved) break;
      }
      return y.map((v) => Math.round(v));
    },
  });

  // ───────── 표적 반응 ─────────
  // victim.slide: 베인 표적의 윗부분이 가른 선을 따라 미끄러진다. steps: [[dx,dy],...] 칸별 ms. 끝나면 null(통째 몸으로 돌아감).
  def('victim.slide', {
    kind: 'actor',
    params: { steps: { type: 'list', def: [[2, -1]], tag: 'style' }, ms: { type: 'list', def: [120], tag: 'style' }, spinDir: { type: 'num', def: 1, tag: 'style' } },
    fn: (p, u) => {
      if (u < 0) return null;
      let x = u * 1000;
      for (let i = 0; i < p.steps.length; i++) { const m = p.ms[Math.min(i, p.ms.length - 1)]; if (x < m) return p.steps[i]; x -= m; }
      return null;
    },
    len: (p) => p.steps.reduce((a, _, i) => a + p.ms[Math.min(i, p.ms.length - 1)], 0) / 1000,
  });

  // ───────── 방출기 (닫힌 식: 어느 t 든 바로 계산 → 되감기·한 칸 넘기기가 같은 그림) ─────────
  // emit.fan: 방향 dir(라디안) ± spread/2 로 n 개. 가로는 공기 저항(drag, 1/s), 세로는 중력. sway: 나풀거림(px, Hz).
  def('emit.fan', {
    kind: 'emit',
    params: {
      n: { type: 'num', def: 3, tag: 'style' }, spread: { type: 'num', def: 0.9, tag: 'style' },
      sp: { type: 'num', def: [30, 60], tag: 'style' }, life: { type: 'num', def: [0.5, 0.8], tag: 'style' },
      up: { type: 'num', def: 0, tag: 'style' }, sway: { type: 'num', def: 0, tag: 'style' }, swayHz: { type: 'num', def: 2, tag: 'style' },
      grav: { type: 'num', def: 120, tag: 'physics' }, drag: { type: 'num', def: 3, tag: 'physics' }, floor: { type: 'num', def: 0, tag: 'physics' },
    },
    // spawn: 한 번만 (시드로) 뽑는 입자 초기값
    spawn: (p, dir, r) => Array.from({ length: Math.round(p.n) }, () => {
      const a = dir + (r() - 0.5) * p.spread;
      const sp = pick(r, p.sp);
      return { vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - p.up, life: pick(r, p.life), ph: r() * Math.PI * 2, f0: Math.floor(r() * 3) };
    }),
    // 입자 하나의 t 초 뒤 상태: 위치 변화량(dx, dy), 남은 수명 비율
    fn: (p, q, t) => {
      if (t < 0 || t > q.life) return null;
      const d = Math.max(1e-6, p.drag);
      const dx = (q.vx * (1 - Math.exp(-d * t))) / d + Math.sin(q.ph + t * p.swayHz * Math.PI * 2) * p.sway * Math.min(1, t * 4);
      let dy = (q.vy * (1 - Math.exp(-d * t))) / d + 0.5 * p.grav * t * t;
      if (p.floor > 0 && dy > p.floor) dy = p.floor;
      return { dx, dy, k: t / q.life };
    },
  });

  // ───────── 화면 ─────────
  // screen.freeze: [at, at+dur) 동안 유닛 시계를 멈춘다 (hitstop, 정적 hold 둘 다)
  def('screen.freeze', {
    kind: 'screen',
    params: { at: { type: 'num', def: 0, tag: 'style' }, dur: { type: 'num', def: 0.08, tag: 'style' } },
    fn: (p, t) => t >= p.at && t < p.at + p.dur,
  });
  // 멈춘 시간을 뺀 유닛 시계
  function frozenClock(windows, t) {
    let lost = 0;
    windows.forEach((w) => { if (t > w.at) lost += Math.min(t, w.at + w.dur) - w.at; });
    return t - lost;
  }
  // screen.shake: 정수 px, step 초마다 부호를 바꾸며 지수 감쇠. axis 'x' | 'y'. (시드로 첫 부호)
  def('screen.shake', {
    kind: 'screen',
    params: { at: { type: 'num', def: 0, tag: 'style' }, amp: { type: 'num', def: 3, tag: 'style' }, decay: { type: 'num', def: 0.12, tag: 'style' },
      step: { type: 'num', def: 0.033, tag: 'physics' }, axis: { type: 'enum', def: 'x', tag: 'style' } },
    fn: (p, t, sign = 1) => {
      const u = t - p.at;
      if (u < 0) return [0, 0];
      const n = Math.floor(u / p.step);
      const a = Math.round(p.amp * Math.exp(-(n * p.step) / Math.max(1e-6, p.decay)));
      if (a <= 0) return [0, 0];
      const v = (n & 1 ? -1 : 1) * sign * a;
      return p.axis === 'y' ? [0, v] : [v, 0];
    },
  });
  // screen.letterbox: 위·아래 띠 높이(px) — 들어오고, 머물고, 나간다 (컷인 'horizontal slit')
  def('screen.letterbox', {
    kind: 'screen',
    params: { at: { type: 'num', def: 0, tag: 'style' }, h: { type: 'num', def: 24, tag: 'style' }, in: { type: 'num', def: 0.15, tag: 'style' },
      hold: { type: 'num', def: 1, tag: 'style' }, out: { type: 'num', def: 0.25, tag: 'style' } },
    fn: (p, t) => {
      const u = t - p.at;
      if (u < 0) return 0;
      let k;
      if (u < p.in) k = 1 - Math.pow(1 - u / p.in, 3);
      else if (u < p.in + p.hold) k = 1;
      else k = 1 - clamp01((u - p.in - p.hold) / Math.max(1e-6, p.out));
      return Math.round(p.h * k);
    },
  });

  // screen.punch: 정수 배율 확대(컷인 '당겨 붙기'). [at, at+dur) 동안 zoom, 앞뒤는 1 — 사이 값 없이 끊어 바꾼다(snap).
  def('screen.punch', {
    kind: 'screen',
    params: { at: { type: 'num', def: 0, tag: 'style' }, dur: { type: 'num', def: 0.5, tag: 'style' }, zoom: { type: 'num', def: 2, tag: 'style' } },
    fn: (p, t) => (t >= p.at && t < p.at + p.dur ? Math.max(1, Math.round(p.zoom)) : 1),
  });
  // 확대 중심을 화면 안으로 묶는다 (정수)
  function clampView(cx, cy, z, W, H) {
    const hw = W / (2 * z), hh = H / (2 * z);
    return [Math.round(Math.min(W - hw, Math.max(hw, cx))), Math.round(Math.min(H - hh, Math.max(hh, cy)))];
  }

  // ───────── 앵커 (몸 칸의 불투명 상자 → 이름 붙은 점) ─────────
  // box: {x0,y0,x1,y1} (화면 px, 발 기준으로 이미 옮긴 값). which: feet/chest/head/ground/center
  function anchorFromBox(box, which, k) {
    const h = box.y1 - box.y0, cx = (box.x0 + box.x1) / 2;
    switch (which) {
      case 'feet': case 'ground': return [cx, box.y1];
      case 'head': return [cx, box.y0 + h * 0.1];
      case 'chest': return [cx, box.y1 - h * 0.5];
      case 'body': return [cx, box.y1 - h * (k == null ? 0.5 : k)];
      default: return [cx, (box.y0 + box.y1) / 2];
    }
  }

  return { def, get, list, resolve, rng, fnv, pick, clamp01, lerp, clockLen, frozenClock, anchorFromBox, clampView };
})();

if (typeof module !== 'undefined') module.exports = FxSkel;
