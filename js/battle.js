// 실시간 집단 전투
// 용병대장 1 + 대원 2~3으로 이루어진 부대가 양쪽 최대 3개씩(3vs3) 전장에서 스스로 판단해 싸운다.
// 의뢰의 결과(대성공/성공/실패/대실패)는 판정에서 정해지고, 전투는 시드를 바꿔 가며 실제로
// 시뮬레이션해 그 결과가 나오는 판을 찾아 재생한다. 연출을 위해 짜 맞춘 각본은 없다.
// 능력치 전투(run): 출격 때 굳힌 편성(spec, js/muster.js)의 체력·공격·방어로 한 판을 그대로 돌려 기록을 낸다.
// 기본(Game.RESOLVE 'roll')에서는 그림자로만 쓴다 — 화면의 전투와 의뢰 결과는 위의 옛 방식 그대로다 (docs/plans/battle_stats/stage01_notes.md).
// 전투 모드('battle')에서는 이 전투가 결과를 정하고, 화면은 같은 편성으로 같은 판을 재생한다 (stage3_notes.md).
'use strict';

const Battle = (() => {
  // 근접 공격의 연출 갈래 (그림만 — 전투 계산과 무관): 찌르기는 곧은 줄, 내려치기는 위에서 아래로 + 바닥 먼지, 나머지는 초승달 베기.
  // 스킬에 fx 가 있으면 그대로, 없으면 이름으로 고른다.
  const THRUST_RE = /찌르기|랜스|기마 돌격|암살|뒤치기|기습/;
  const SMASH_RE = /망치|철퇴|강타|주먹|도끼/;   // 방패 치기(일반 전사 기본기)는 칼을 든 그림이라 베기 그대로
  function meleeStyle(sk) {
    if (sk.fx) return sk.fx;
    return THRUST_RE.test(sk.name) ? 'thrust' : SMASH_RE.test(sk.name) ? 'smash' : 'slash';
  }
  const W = 320, H = 180;
  const TOP = 80, BOTTOM = 170;      // 전장의 위·아래 경계 (유닛 발 위치). 유닛은 발 위로 약 32 단위 높이로 그려진다
  // 몸집: 캐릭터를 약 32(높이)×16(너비) 논리 단위(화면 64px 안팎)로 그리므로 서로 이만큼 떨어져 선다.
  // 깊이(세로)로 10만 떨어지면 몸의 2/3가 겹쳐 한 덩어리로 보이므로, 같은 편은 깊이로 넉넉히 벌리고 엇갈려 선다.
  const SEP_X = 18, SEP_Y = 18;      // 같은 편끼리 최소 간격 (가로·깊이)
  const SEP_FOE_X = 13, SEP_FOE_Y = 16; // 맞붙은 적과의 최소 간격 (근접 사거리보다 짧아야 한다)
  const BODY = 6;                    // 근접 공격이 닿는 거리에 더하는 몸 폭
  const DEPTH = 0.6;                 // 근접 거리에서 깊이(세로) 차이를 덜 센다: 비스듬히 위·아래에서 붙어도 닿는다
  // 근접 교전 자리: 목표 앞(정면)과 비스듬히 위·아래, 큰 적은 뒤쪽 위·아래까지. [가로(공격자 쪽으로), 깊이]
  // 모두 사거리(11+BODY, 깊이 DEPTH 배) 안쪽이라 자리에 서면 바로 칠 수 있다.
  const MELEE_SLOTS = [[15, 0], [12, -18], [12, 18], [-12, -18], [-12, 18]];
  const EDGE = 14;                   // 싸우는 유닛이 화면 가장자리에 반쯤 잘려 서지 않게 (몸 폭의 절반 남짓)
  // 큰 괴물(우두머리는 시트를 1.5배로, 코드 생성 도트는 5·7배로 그린다)은 날개·몸통이 95~140px 이라 그만큼 더 안쪽에 선다:
  // scale 2 → 34, scale 3 → 44 (몸 폭 절반 ≈ 70px). 그림 폭이 남는 만큼은 그리는 쪽이 화면 안으로 당긴다 (screenX).
  const EDGE_BIG = 2.5;
  // 한 목표에 동시에 붙는 근접 공격자 수와 쓸 수 있는 자리 수. 보통은 앞 세 자리 중 둘만 차서 대열이 엉키지 않는다.
  // 넘치는 공격자는 다른 적을 찾거나, 한 걸음 물러서 자리가 나기를 기다린다.
  const meleeCap = (t) => (t.boss ? 5 : t.bigMon ? 3 : 2);
  const slotCount = (t) => (t.boss ? 5 : 3);
  const DT = 0.05;                   // 시뮬레이션 한 틱(초)
  const MAX_TIME = 90;               // 시간 제한(초)
  const END_HOLD = 2.2;              // 결판 후 화면 유지(초)
  const ATK_SCALE = 0.55;            // 전투가 너무 빨리 끝나지 않게

  // 직업(싸움 방식)별 기본 능력치 (강도 1 기준). 공격 방식·사거리·재사용은 스킬이 정한다.
  const CLASS_STATS = {
    warrior: { hp: 130, atk: 13, speed: 24 },
    rogue:   { hp: 90,  atk: 15, speed: 34 },
    archer:  { hp: 75,  atk: 11, speed: 26 },
    mage:    { hp: 65,  atk: 14, speed: 22 },
    cleric:  { hp: 90,  atk: 9,  speed: 24 },
  };
  const MONSTER_STATS = { hp: 110, atk: 12, speed: 27 };
  const RANGED_TPL = { ghost: 'curse', drake: 'fire', demon: 'curse' };
  const HEAL_POWER = 16;
  const SLOW_MUL = 0.5;   // 느려짐(거미줄): 이동 속도 배율
  const SHOT_COLOR = { arrow: '#e8e4d8', fire: '#ff9a3c', curse: '#b47aff', bolt: '#7fd6ff', dagger: '#e0e8f0', holy: '#fff2a8', web: '#e4e4ec' };

  // 범용 부대장(외부 용병단 단장, 세력 부대장)이 쓰는 특기
  const GENERIC_SPECIAL = {
    warrior: SK.melee('돌격', 1.5, 9, { dash: true, stun: 0.4 }),
    archer: SK.shot('일제 사격', 'arrow', 0.8, 95, 8, { hits: 3 }),
    mage: SK.shot('화염 폭발', 'fire', 1.4, 85, 9, { aoe: 20 }),
    cleric: SK.heal('집단 치유', 0.9, 60, 10, { aoe: 35 }),
    rogue: SK.melee('급소 찌르기', 1.8, 8, { exec: 0.6, dash: true }),
  };
  // 괴물 스킬
  function monsterSkills(ud) {
    const tpl = ENEMIES[ud.mon] && ENEMIES[ud.mon].tpl;
    const basic = RANGED_TPL[tpl] && !ud.boss ? SK.shot('공격', RANGED_TPL[tpl], 1, 70, 1.4) : SK.melee('공격', 1, 1.0, { range: ud.bigMon ? 16 : 11 });
    if (ud.boss) return [basic, (tpl === 'drake' || tpl === 'demon') ? SK.shot('파멸의 숨결', tpl === 'demon' ? 'curse' : 'fire', 1.6, 70, 7, { aoe: 26, stun: 0.6 })
      : SK.melee('대지 분쇄', 1.8, 7, { aoe: 24, stun: 0.6, range: 18 })];
    if (ud.bigMon) return [basic, SK.melee('포효', 1.1, 9, { aoe: 20, stun: 0.4, range: 16 })];
    // 거대 거미: 꽁무니에서 거미줄을 뿜어 표적을 잠시 느리게 한다 (주인 요청 2026-11-25)
    if (ud.mon === '거대 거미') return [basic, SK.shot('거미줄 뿜기', 'web', 0.4, 70, 8, { slow: 2.5 })];
    return [basic];
  }


  let raf = null;
  let lastSt = null;   // 마지막으로 재생한 전투 상태 (Battle.last)

  // ───────── 시드 난수 ─────────
  function rng(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rInt = (r, a, b) => a + Math.floor(r() * (b - a + 1));
  const rPick = (r, arr) => arr[Math.floor(r() * arr.length)];

  // ───────── 배경 ─────────
  // 화면은 시뮬레이션 좌표(320×180)의 2배 해상도로 그린다
  const Z = 2, CW = W * Z, CH = H * Z;
  function px(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }

  // 도트 베기 잔상: 매끈한 선 대신 칸 단위로 칠한 초승달 — 가운데가 두껍고 양끝이 가늘다.
  // 60ms 마다 한 단계씩(프레임처럼 끊어서): 0 휘두르는 중 → 1 다 그은 초승달 + 바깥 잔줄 → 2 가늘어지며 잔줄 → 3 잔줄 조각만.
  function mixHex(a, b, k) {
    const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
    const A = p(a), B = p(b);
    return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * k).toString(16).padStart(2, '0')).join('');
  }
  function smearArc(ctx, cx, cy, R, th0, th1, wMax, col, rim, dashed) {
    const n = Math.max(6, Math.ceil(Math.abs(th1 - th0) * R * 1.6));
    for (let i = 0; i <= n; i++) {
      const u = i / n;
      if (dashed && Math.floor(u * 7) % 2) continue;
      const th = th0 + (th1 - th0) * u;
      const w = Math.max(1, Math.round(wMax * Math.pow(Math.sin(Math.PI * u), 0.8)));
      const c = Math.cos(th), sn = Math.sin(th);
      for (let r = 0; r < w; r++) {
        const rr = R - r;
        px(ctx, Math.round(cx + c * rr), Math.round(cy + sn * rr * 0.85), 1, 1, r === 0 && w > 2 ? rim : col);
      }
    }
  }
  // 도트 폭발: 60ms 단계로 끊어서 — 0~1 뾰족한 별꼴 섬광 → 2~4 불꽃 조각이 퍼짐 → 5~8 불티가 흩어지며 사라짐.
  // 바닥에는 점선 고리. (주인이 준 마법사 예시: 별꼴 한 번 → 조각 → 불티, 부드러운 원형 빛이 아니라 칸 단위 모양)
  function drawBurst(ctx, s, r) {
    const step = Math.min(8, Math.floor(s.t / 0.06));
    const cx = Math.round(s.x), cy = Math.round(s.y), R = Math.max(10, Math.round(s.r * 0.9 + 8));
    let seed = (Math.round(s.x) * 73856093 ^ Math.round(s.y) * 19349663) >>> 0;
    const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    const N = 10, ang = [], len = [];
    for (let i = 0; i < N; i++) { ang.push((i + rnd() * 0.5) * (Math.PI * 2 / N)); len.push(i % 2 ? 0.45 + rnd() * 0.15 : 0.8 + rnd() * 0.2); }
    const hot = mixHex(s.color, '#ffffff', 0.65), dark = mixHex(s.color, '#3a2a2a', 0.45);
    const a0 = ctx.globalAlpha;
    if (step <= 1) {
      const sc = step === 0 ? 1 : 0.7;
      for (let i = 0; i < N; i++) {
        const L = Math.round(R * len[i] * sc), c = Math.cos(ang[i]), sn = Math.sin(ang[i]);
        for (let d = 0; d <= L; d++) {
          const w = d < L * 0.3 ? 2 : 1;
          px(ctx, Math.round(cx + c * d), Math.round(cy + sn * d * 0.8), w, w, d < L * 0.2 ? hot : s.color);
        }
      }
      const core = Math.round(R * (step === 0 ? 0.17 : 0.11));
      for (let y = -core; y <= core; y++) {
        const hw = Math.round(Math.sqrt(core * core - y * y));
        px(ctx, cx - hw, cy + Math.round(y * 0.8), hw * 2 + 1, 1, step === 0 ? '#ffffff' : hot);
      }
    } else if (step <= 4) {
      ctx.globalAlpha = a0 * (1 - (step - 2) * 0.18);
      const dist = R * (0.35 + (step - 2) * 0.22);
      for (let i = 0; i < N + 4; i++) {
        const a = rnd() * Math.PI * 2, dd = dist * (0.7 + rnd() * 0.5), sz = step === 2 ? 3 : 2;
        px(ctx, Math.round(cx + Math.cos(a) * dd), Math.round(cy + Math.sin(a) * dd * 0.8), sz, sz, i % 3 ? s.color : hot);
        if (step === 2) px(ctx, Math.round(cx + Math.cos(a) * dd * 0.8), Math.round(cy + Math.sin(a) * dd * 0.64), 2, 1, dark);
      }
    } else {
      ctx.globalAlpha = a0 * Math.max(0.15, 0.7 - (step - 5) * 0.16);
      const dist = R * (0.9 + (step - 5) * 0.15);
      for (let i = 0; i < N + 6; i++) {
        const a = rnd() * Math.PI * 2, dd = dist * (0.6 + rnd() * 0.6);
        if ((i + step) % 2) continue;
        px(ctx, Math.round(cx + Math.cos(a) * dd), Math.round(cy + Math.sin(a) * dd * 0.8 - (step - 5)), 1, 1, i % 4 ? s.color : dark);
      }
    }
    // 바닥 점선 고리 (전과 같은 크기 r 로 퍼짐)
    ctx.globalAlpha = a0 * Math.max(0, 1 - s.t / 0.5);
    const rx = Math.round(r * 1.1), ry = Math.round(r * 0.45), n = Math.max(12, Math.round(rx * 0.9));
    for (let i = 0; i < n; i++) {
      if (i % 3 === 2) continue;
      const a = i / n * Math.PI * 2;
      px(ctx, Math.round(s.x + Math.cos(a) * rx), Math.round(s.y + 10 + Math.sin(a) * ry), 1, 1, s.color);
    }
    ctx.globalAlpha = a0;
  }
  // ── 타격 불꽃·쓰러짐 먼지 (pixelfx 의 견본을 보고 원리만 가져와 새로 짠 것: 색 사다리를 따라 식는 불꽃, 한쪽으로 긴 십자 섬광,
  //    중력·바닥 튕김이 있는 짧은 줄 모양 불티, 두 톤 그늘의 둥근 먼지 덩이. 코드는 이 게임용으로 직접 썼다.) ──
  const WARM_RAMP = ['#ffffff', '#fff3b0', '#ffd060', '#ff9a3c', '#d4502a', '#6a2418'];
  const rampCache = {};
  function rampOf(col) {
    return rampCache[col] || (rampCache[col] = ['#ffffff', mixHex(col, '#ffffff', 0.55), mixHex(col, '#ffffff', 0.2), col,
      mixHex(col, '#2a2030', 0.45), mixHex(col, '#2a2030', 0.72)]);
  }
  const rampAt = (ramp, k) => ramp[Math.min(ramp.length - 1, Math.max(0, Math.floor(k * ramp.length)))];
  // 맞은 자리: 한쪽(공격 방향)으로 긴 십자 섬광 2단계 + 그 방향 부채꼴로 튀는 불티 (위로 조금, 바닥에서 한 번 튕김)
  function hitSpark(view, x, y, dir, floor, big, ramp) {
    view.flares.push({ x: Math.round(x), y: Math.round(y), dir: dir < 0 ? -1 : 1, t: 0, big, ramp });
    const n = big ? 9 : 5;
    for (let i = 0; i < n && view.sparks.length < 300; i++) {
      const a = (dir < 0 ? Math.PI : 0) + rnd(-0.9, 0.5) * (dir < 0 ? -1 : 1), sp = rnd(60, big ? 170 : 120);
      view.sparks.push({ x, y, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - rnd(10, 50), t: -rnd(0, 0.03), max: rnd(0.25, big ? 0.55 : 0.4),
        floor, bounced: false, ramp });
    }
  }
  // 쓰러진 자리: 발밑에서 먼지 덩이 3~5개가 부풀었다 작아지며 살짝 떠오른다
  function downPuff(view, x, foot, big) {
    const n = big ? 5 : 3;
    for (let i = 0; i < n; i++) {
      view.puffs.push({ x: x + rnd(-8, 8) * (big ? 1.6 : 1), y: foot - rnd(0, 3), r: rnd(3, 5) * (big ? 1.4 : 1), t: -i * 0.03, max: rnd(0.45, 0.7),
        vx: rnd(-14, 14), vy: -rnd(4, 12) });
    }
  }
  function updateSparks(view, dt) {
    view.sparks.forEach((p) => {
      p.t += dt;
      if (p.t < 0) return;
      p.px = p.x; p.py = p.y;
      p.vy += 320 * dt; p.x += p.vx * dt; p.y += p.vy * dt;
      if (!p.bounced && p.y > p.floor && p.vy > 0) { p.y = p.floor; p.vy *= -0.35; p.vx *= 0.55; p.bounced = true; }
      else if (p.bounced && p.y > p.floor) { p.y = p.floor; p.vy = 0; p.vx *= 0.8; }
    });
    view.sparks = view.sparks.filter((p) => p.t < p.max);
    view.flares.forEach((f) => { f.t += dt; });
    view.flares = view.flares.filter((f) => f.t < 0.1);
    view.puffs.forEach((p) => { p.t += dt; if (p.t > 0) { p.x += p.vx * dt; p.y += p.vy * dt; p.vx *= 0.9; } });
    view.puffs = view.puffs.filter((p) => p.t < p.max);
  }
  // ── 거미줄 (직접 짠 도트): 꽁무니에서 표적까지 늘어진 가는 실 + 날아가는 실뭉치, 맞은 몸에 들러붙은 거미줄 ──
  const WEB = '#e4e4ec', WEB_D = '#a8a8b8';
  function pxLine(ctx, x0, y0, x1, y1, col, every) {
    const n = Math.max(1, Math.round(Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0))));
    for (let i = 0; i <= n; i++) {
      if (every && i % every) continue;
      px(ctx, Math.round(x0 + (x1 - x0) * i / n), Math.round(y0 + (y1 - y0) * i / n), 1, 1, col);
    }
  }
  function drawWebShot(ctx, s, X, Y, dx, dy) {
    const op = ctx.globalCompositeOperation;
    ctx.globalCompositeOperation = 'source-over';
    const f = s.from, face = f ? (f.face || 1) : 1;
    // 꽁무니(몸 뒤쪽 위)에서 나온 실: 등 위로 넘어 휘어 날아간다 — 실은 점선으로 늘어진다
    const ax = (s.sx * Z) - face * 14, ay = s.sy * Z - LIFT - 4;
    const mx = (ax + X) / 2, my = Math.min(ay, Y) - 18;
    ctx.globalAlpha = 0.95;
    for (let i = 0; i < 12; i++) {
      const t0 = i / 12, t1 = (i + 1) / 12, q = (t) => [(1 - t) * (1 - t) * ax + 2 * (1 - t) * t * mx + t * t * X, (1 - t) * (1 - t) * ay + 2 * (1 - t) * t * my + t * t * Y];
      const [x0, y0] = q(t0), [x1, y1] = q(t1);
      pxLine(ctx, x0, y0, x1, y1, i % 2 ? WEB_D : WEB, 0);
    }
    // 실뭉치: 흰 덩이 + 네 갈래 짧은 실
    ctx.globalAlpha = 1;
    const x = Math.round(X), y = Math.round(Y);
    px(ctx, x - 3, y - 2, 6, 4, WEB_D); px(ctx, x - 2, y - 3, 4, 6, WEB_D); px(ctx, x - 2, y - 2, 4, 4, WEB); px(ctx, x - 1, y - 1, 2, 2, '#ffffff');
    pxLine(ctx, x, y, x - dx * 7 - dy * 3, y - dy * 7 + dx * 3, WEB_D, 0);
    pxLine(ctx, x, y, x - dx * 7 + dy * 3, y - dy * 7 - dx * 3, WEB_D, 0);
    pxLine(ctx, x, y, x + dy * 4, y - dx * 4, WEB_D, 0); pxLine(ctx, x, y, x - dy * 4, y + dx * 4, WEB_D, 0);
    ctx.globalCompositeOperation = op;
  }
  function drawWebOn(ctx, x, y, h, left, seed) {
    const r = Math.max(8, Math.round(h * 0.32)), a0 = (seed % 7) * 0.3;
    ctx.globalAlpha = left < 0.4 ? left / 0.4 * 0.75 : 0.75;
    const sp = [];
    for (let i = 0; i < 6; i++) { const a = a0 + i * Math.PI / 3 + (i % 2) * 0.18; sp.push([Math.cos(a), Math.sin(a) * 0.8, i % 2 ? 0.8 : 1]); }
    sp.forEach(([c, sn, k]) => pxLine(ctx, x, y, x + c * r * k, y + sn * r * k, WEB, 0));
    [0.45, 0.8].forEach((rr, j) => {
      for (let i = 0; i < 6; i++) {
        const [c0, s0, k0] = sp[i], [c1, s1, k1] = sp[(i + 1) % 6];
        pxLine(ctx, x + c0 * r * rr * k0, y + s0 * r * rr * k0, x + c1 * r * rr * k1, y + s1 * r * rr * k1, j ? WEB_D : WEB, j ? 2 : 0);
      }
    });
    ctx.globalAlpha = 1;
  }
  function drawSparks(ctx, view) {
    // 섬광: 0~50ms 크게(흰 핵 + 긴 빛줄기), 50~100ms 작게 식은 색
    view.flares.forEach((f) => {
      const k = f.t < 0.05 ? 0 : 1, L = (f.big ? 13 : 9) - k * 4, s = f.big ? 4 : 3;
      ctx.globalAlpha = 0.5 - k * 0.25;
      ctx.drawImage(glow(f.ramp[2], f.big ? 10 : 7), f.x - (f.big ? 10 : 7), f.y - (f.big ? 10 : 7));
      ctx.globalAlpha = 1;
      const hot = k ? f.ramp[2] : '#ffffff', mid = k ? f.ramp[3] : f.ramp[1];
      px(ctx, f.x + (f.dir > 0 ? 0 : -L), f.y, L + 1, 1, mid);                 // 공격 방향으로 긴 줄기
      px(ctx, f.x - (f.dir > 0 ? 3 : -1) * 1, f.y, 3, 1, mid);                  // 뒤로 짧게
      px(ctx, f.x, f.y - s, 1, s * 2 + 1, mid);                                // 위아래 짧게
      px(ctx, f.x - 1, f.y - 1, 3, 3, hot); if (!k) px(ctx, f.x, f.y - 2, 1, 5, hot);
    });
    // 불티: 지나온 길로 2~4px 짧은 줄, 식는 색
    view.sparks.forEach((p) => {
      if (p.t < 0 || p.px == null) return;
      const col = rampAt(p.ramp, p.t / p.max);
      const dx = p.x - p.px, dy = p.y - p.py, len = Math.min(4, Math.max(1, Math.round(Math.hypot(dx, dy))));
      for (let i = 0; i < len; i++) px(ctx, Math.round(p.x - dx * i / len), Math.round(p.y - dy * i / len), 1, 1, i ? rampAt(p.ramp, Math.min(1, p.t / p.max + 0.2)) : col);
    });
    // 먼지 덩이: 두 톤(왼쪽 위 밝게, 오른쪽 아래 그늘), 부풀었다가 작아진다
    view.puffs.forEach((p) => {
      if (p.t < 0) return;
      const k = p.t / p.max, r = Math.max(1, Math.round(p.r * (k < 0.3 ? 0.6 + k * 1.3 : 1 - (k - 0.3) * 0.9)));
      ctx.globalAlpha = k < 0.6 ? 0.9 : 0.9 * (1 - (k - 0.6) / 0.4);
      const cx = Math.round(p.x), cy = Math.round(p.y);
      for (let yy = -r; yy <= r; yy++) {
        const hw = Math.round(Math.sqrt(r * r - yy * yy));
        px(ctx, cx - hw, cy + yy, hw * 2 + 1, 1, yy < 0 ? '#c9bca4' : '#9a8c76');
      }
      px(ctx, cx - Math.round(r * 0.5), cy - Math.round(r * 0.6), Math.max(1, Math.round(r * 0.5)), 1, '#ddd2bc');
    });
    ctx.globalAlpha = 1;
  }

  // 찌르기: 공격자 쪽에서 표적으로 곧게 뻗는 줄 — 끝(표적 쪽)이 두껍고 뒤가 가늘다, 위아래로 가는 속도선, 끝에 작은 별.
  function drawThrust(ctx, s) {
    const step = Math.min(3, Math.floor(s.t / 0.055));
    const d = s.dir < 0 ? -1 : 1, L = s.big ? 34 : 24, W = s.big ? 3 : 2;
    const tipX = Math.round(s.x + d * 3), y = Math.round(s.y);
    const rim = mixHex(s.color, '#5a7a98', 0.5), soft = mixHex(s.color, '#8aa8c4', 0.35);
    // 교차 검수 1(GPT) #3: 눈밭에서 흰 줄이 묻히지 않게 첫 두 단계의 핵심선·끝점에만 짙은 청회색 1px 윤곽
    const EDGE = '#3a4a66';
    const line = (from, to, w, col, dashed, edge) => {
      for (let i = from; i <= to; i++) {
        if (dashed && Math.floor(i / 3) % 2) continue;
        const k = i / L, ww = Math.max(1, Math.round(w * (1 - k)));
        if (edge) px(ctx, tipX - d * i, y - (ww >> 1) - 1, 1, ww + 2, EDGE);
        px(ctx, tipX - d * i, y - (ww >> 1), 1, ww, col);
      }
    };
    const tipEdge = () => { px(ctx, tipX - 2, y - 3, 5, 7, EDGE); px(ctx, tipX - 3, y - 2, 7, 5, EDGE); };
    if (step === 0) {
      ctx.globalAlpha = 1; line(0, Math.round(L * 0.5), W, s.color, false, true);
      tipEdge(); px(ctx, tipX - 1, y - 2, 3, 5, '#ffffff'); px(ctx, tipX - 2, y - 1, 5, 3, '#ffffff');
    } else if (step === 1) {
      ctx.globalAlpha = 1; line(0, L, W, s.color, false, true);
      line(Math.round(L * 0.2), Math.round(L * 0.8), 1, soft, false);
      for (let i = 4; i < L * 0.7; i++) { px(ctx, tipX - d * i, y - 4, 1, 1, soft); px(ctx, tipX - d * (i + 3), y + 4, 1, 1, rim); }
      px(ctx, tipX + d, y - 3, 1, 7, s.color); px(ctx, tipX - 2, y, 6, 1, s.color);
    } else if (step === 2) {
      ctx.globalAlpha = 0.8; line(Math.round(L * 0.25), L, Math.max(1, W - 1), soft);
      for (let i = 8; i < L * 0.9; i += 2) { px(ctx, tipX - d * i, y - 5, 1, 1, soft); px(ctx, tipX - d * (i + 4), y + 5, 1, 1, soft); }
    } else {
      ctx.globalAlpha = 0.5; line(Math.round(L * 0.4), L + 4, 1, soft, true);
    }
  }
  // 내려치기: 머리 위에서 앞쪽 아래로 짧고 두꺼운 반원 → 바닥(발)에 부딪힌 자리에 먼지 고리와 튀는 조각.
  function drawSmash(ctx, s) {
    const step = Math.min(3, Math.floor(s.t / 0.055));
    const d = s.dir < 0 ? -1 : 1, R = s.big ? 18 : 13, W = s.big ? 6 : 4;
    const cx = Math.round(s.x - d * 4), cy = Math.round(s.y - 2), fy = Math.round(s.foot);
    const rim = mixHex(s.color, '#5a7a98', 0.5), soft = mixHex(s.color, '#8aa8c4', 0.35);
    const dust = '#b8a890', dustD = '#7e705e';
    // 위(-π/2)에서 앞쪽 아래(앞으로 약 70°)까지: 오른쪽을 보면 -1.75 → 1.2, 왼쪽은 거울
    const arc = (u0, u1) => d > 0 ? [-1.75 + u0 * 2.95, -1.75 + u1 * 2.95] : [Math.PI + 1.75 - u0 * 2.95, Math.PI + 1.75 - u1 * 2.95];
    let seed = (Math.round(s.x) * 2654435761 ^ fy * 40503) >>> 0;
    const rnd = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    if (step === 0) {
      ctx.globalAlpha = 1; const [a, b] = arc(0, 0.7); smearArc(ctx, cx, cy, R, a, b, W, s.color, rim, false);
    } else {
      ctx.globalAlpha = step === 1 ? 1 : step === 2 ? 0.75 : 0.45;
      if (step < 3) { const [a, b] = arc(0.3, 1); smearArc(ctx, cx, cy, R, a, b, step === 1 ? W : Math.ceil(W / 2), step === 1 ? s.color : soft, rim, false); }
      // 바닥 먼지: 납작한 점선 고리가 퍼지고, 조각이 위로 튄다
      const rx = 6 + step * 5, ry = 2 + step;
      for (let i = 0; i < 18; i++) {
        if ((i + step) % 3 === 0) continue;
        const a = i / 18 * Math.PI * 2;
        px(ctx, Math.round(s.x + Math.cos(a) * rx), Math.round(fy + Math.sin(a) * ry), 2, 1, i % 4 ? dust : dustD);
      }
      for (let i = 0; i < 6; i++) {
        const dx = (rnd() - 0.5) * (8 + step * 6), up = Math.round((rnd() * 6 + 3) * (step === 3 ? 0.6 : step / 2));
        px(ctx, Math.round(s.x + dx), fy - up, step === 1 ? 2 : 1, step === 1 ? 2 : 1, i % 2 ? dust : dustD);
      }
    }
  }
  function drawSmear(ctx, s) {
    const step = Math.min(3, Math.floor(s.t / 0.055));
    const R = s.big ? 22 : 15, W = s.big ? 5 : 3, S = 2.1;
    const d = s.dir < 0 ? -1 : 1;
    const cx = Math.round(s.x - d * 6), cy = Math.round(s.y);
    // 교차 검수 1(GPT) #1: 핵심 초승달은 늘 흰색, 일반/특수기는 둘째 프레임부터의 잔상색으로 가른다
    const tint = s.color === '#ffffff' ? '#b8c4d4' : s.color;
    const rim = mixHex(tint, '#5a7a98', 0.5), soft = mixHex(tint, '#8aa8c4', 0.2);
    const arc = (u0, u1) => d > 0 ? [-1.4 + u0 * S, -1.4 + u1 * S] : [Math.PI + 1.4 - u0 * S, Math.PI + 1.4 - u1 * S];
    if (step === 0) {
      ctx.globalAlpha = 1;
      const [a, b] = arc(0, 0.6); smearArc(ctx, cx, cy, R, a, b, W, '#ffffff', rim, false);
    } else if (step === 1) {
      ctx.globalAlpha = 1;
      let [a, b] = arc(0, 1); smearArc(ctx, cx, cy, R, a, b, W, '#ffffff', rim, false);
      [a, b] = arc(0.15, 0.9); smearArc(ctx, cx, cy, R + 3, a, b, 1, soft, soft, false);
    } else if (step === 2) {
      ctx.globalAlpha = 0.8;
      let [a, b] = arc(0.25, 1); smearArc(ctx, cx, cy, R, a, b, Math.ceil(W / 2), soft, rim, false);
      [a, b] = arc(0.1, 0.85); smearArc(ctx, cx, cy, R + 4, a, b, 1, soft, soft, true);
    } else {
      ctx.globalAlpha = 0.5;
      const [a, b] = arc(0.3, 1); smearArc(ctx, cx, cy, R + 5, a, b, 1, soft, soft, true);
    }
  }
  // 지형별 색: 하늘 위/아래, 먼 산, 중경, 땅, 땅 어두움, 땅 밝음, 앞쪽 수풀
  const PAL = {
    plains: { sky: ['#3a5a8a', '#8fb0d8'], far: '#4a6a7a', mid: '#2f5a3a', ground: '#5a7a3a', dark: '#3f5a2a', light: '#7a9a4a', fore: '#1f3a1f', deco: 'grass' },
    forest: { sky: ['#1f3a3a', '#4a6a5a'], far: '#233a2f', mid: '#1a3020', ground: '#4a4a2a', dark: '#33331c', light: '#6a6a3a', fore: '#142414', deco: 'tree' },
    swamp:  { sky: ['#2a3330', '#5a6a60'], far: '#34403a', mid: '#2a3328', ground: '#3f4a30', dark: '#2a3320', light: '#566040', fore: '#1a2218', deco: 'reed' },
    desert: { sky: ['#a85a3a', '#f0b878'], far: '#a86a48', mid: '#8a4a30', ground: '#c89a5a', dark: '#a07840', light: '#e0b878', fore: '#6a3a20', deco: 'rock' },
    frost:  { sky: ['#4a6a9a', '#c8dcf0'], far: '#8aa0c0', mid: '#5a7090', ground: '#d8e2ea', dark: '#a8b8c8', light: '#f4f8fc', fore: '#3a4a5a', deco: 'pine' },
    mountain: { sky: ['#2a0e0e', '#7a2a1a'], far: '#3a1a18', mid: '#2a1410', ground: '#4a2a20', dark: '#2e1a14', light: '#6a3a28', fore: '#1a0c0a', deco: 'lava' },
    holy:   { sky: ['#6a5a8a', '#f0d8a8'], far: '#8a7a8a', mid: '#6a6a5a', ground: '#8a8a5a', dark: '#6a6a40', light: '#aaa878', fore: '#3a3a28', deco: 'ruin' },
    coast:  { sky: ['#3a6a9a', '#a8d0f0'], far: '#5a8ab0', mid: '#3a6a8a', ground: '#7a8a5a', dark: '#5a6a40', light: '#9aa878', fore: '#2a3a2a', deco: 'sea' },
  };
  const HORIZON = 62 * Z;

  // 간단한 값 잡음 (결정적)
  const hash = (x, y) => { const n = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return n - Math.floor(n); };
  function noise(x, y) {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const a = hash(xi, yi), b = hash(xi + 1, yi), c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1);
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }

  // 배경: 일러스트가 있으면 일러스트, 없으면 층을 쌓아 코드로 그린다
  function background(terrain) {
    const b = document.createElement('canvas'); b.width = CW; b.height = CH;
    const c = b.getContext('2d');
    c.imageSmoothingEnabled = false;
    const art = typeof Art !== 'undefined' && Art.image && Art.image(`bg/battle/${terrain}`);
    if (art) { c.drawImage(art, 0, 0, CW, CH); return b; }
    const P = PAL[terrain] || PAL.plains;
    // 하늘: 계단식 그라데이션
    for (let i = 0; i < 10; i++) {
      const k = i / 9;
      px(c, 0, Math.round((HORIZON * i) / 10), CW, Math.ceil(HORIZON / 10) + 1, mix(P.sky[0], P.sky[1], k));
    }
    // 먼 산·숲 실루엣 두 겹
    [[P.far, 34, 90, 0.6], [P.mid, 20, 47, 1.3]].forEach(([col, amp, per, seed]) => {
      c.fillStyle = col;
      for (let x = 0; x < CW; x += 2) {
        const h = Math.round(amp * (0.5 + 0.5 * Math.sin(x / per + seed)) + amp * 0.6 * noise(x / 30 + seed * 10, seed) + 8);
        c.fillRect(x, HORIZON - h, 2, h + 2);
      }
    });
    // 지형 장식 (중경)
    decorate(c, P, terrain);
    // 땅: 위쪽은 어둡게(멀리), 얼룩과 흙길
    // 땅: 비슷한 톤 4단계를 잔잔하게 섞고, 체크 무늬 디더로 경계를 부드럽게
    const tones = [P.dark, mix(P.dark, P.ground, 0.55), P.ground, mix(P.ground, P.light, 0.45)];
    for (let y = HORIZON; y < CH; y += 2) {
      const depth = (y - HORIZON) / (CH - HORIZON);
      for (let x = 0; x < CW; x += 2) {
        const n = noise(x / 70, y / 30) * 0.55 + noise(x / 16, y / 9) * 0.3 + noise(x / 5, y / 4) * 0.15;
        let v = (n - 0.25) * 2.2 + (((x + y) / 2) % 2 ? 0.12 : -0.12) - (depth < 0.15 ? 0.6 : 0);
        const col = tones[Math.max(0, Math.min(3, Math.floor(v * 2 + 1.5)))];
        c.fillStyle = col; c.fillRect(x, y, 2, 2);
      }
    }
    // 흙길 띠
    c.fillStyle = 'rgba(0,0,0,0.10)';
    for (let x = 0; x < CW; x += 2) {
      const y = Math.round(CH * 0.66 + Math.sin(x / 70) * 10 + noise(x / 20, 3) * 8);
      c.fillRect(x, y, 2, 22);
    }
    // 잔디 포기·돌멩이
    for (let i = 0; i < 140; i++) {
      const x = Math.floor(hash(i, 1) * CW), y = HORIZON + 10 + Math.floor(hash(i, 2) * (CH - HORIZON - 10));
      if (hash(i, 3) < 0.7) { px(c, x, y, 2, 4, P.light); px(c, x + 3, y + 1, 2, 3, P.light); px(c, x + 1, y + 4, 4, 1, P.dark); }
      else { px(c, x, y, 6, 4, P.far); px(c, x + 1, y, 3, 1, P.light); }
    }
    // 아래쪽 가장자리를 어둡게 (깊이감)
    const g = c.createLinearGradient(0, HORIZON, 0, CH);
    g.addColorStop(0, 'rgba(0,0,0,0.25)'); g.addColorStop(0.3, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.18)');
    c.fillStyle = g; c.fillRect(0, HORIZON, CW, CH - HORIZON);
    return b;
  }

  function decorate(c, P, terrain) {
    for (let i = 0; i < 9; i++) {
      const x = Math.floor(10 + i * 72 + hash(i, 7) * 30), y = HORIZON;
      const big = hash(i, 8) * 0.6 + 0.7;
      if (P.deco === 'tree' || P.deco === 'pine') {
        const h = Math.round(60 * big), w = Math.round(26 * big);
        px(c, x + w / 2 - 3, y - h * 0.4, 6, h * 0.4 + 4, '#2a1a10');
        for (let k = 0; k < 4; k++) {
          const ww = w - k * (P.deco === 'pine' ? 6 : 3), yy = y - h * 0.35 - k * h * 0.17;
          px(c, x + (w - ww) / 2, yy - h * 0.18, ww, h * 0.2, k % 2 ? P.mid : P.fore);
        }
        if (P.deco === 'pine') px(c, x + w / 2 - 4, y - h * 0.9, 8, 6, '#e8eef2');
      } else if (P.deco === 'reed') {
        for (let k = 0; k < 5; k++) px(c, x + k * 4, y - 14 - (k % 3) * 4, 2, 16 + (k % 3) * 4, '#4a5a2a');
        px(c, x - 10, y + 30 + (i % 3) * 40, 50, 6, '#1f2a28');
      } else if (P.deco === 'rock') {
        px(c, x, y - 22 * big, 40 * big, 22 * big, P.mid); px(c, x + 4, y - 22 * big, 30 * big, 4, P.light);
      } else if (P.deco === 'lava') {
        px(c, x, y + 40 + (i % 3) * 50, 30, 3, '#e85a20'); px(c, x + 6, y + 41 + (i % 3) * 50, 14, 1, '#f2c94c');
        px(c, x + 10, y - 30 * big, 14, 30 * big, P.mid);
      } else if (P.deco === 'ruin') {
        px(c, x, y - 40 * big, 10, 40 * big, '#c8c0b0'); px(c, x - 4, y - 44 * big, 18, 6, '#e0d8c8');
      } else if (P.deco === 'sea') {
        if (i === 0) { px(c, 0, y - 10, CW, 10, '#3a6a9a'); for (let k = 0; k < 40; k++) px(c, hash(k, 9) * CW, y - 8 + hash(k, 10) * 6, 6, 1, '#a8d0f0'); }
      } else if (i % 2) {
        px(c, x, y - 18 * big, 30 * big, 18 * big, P.mid);
      }
    }
  }

  // 앞쪽 수풀 (유닛 위에 겹쳐 그려 깊이를 준다). 일러스트 배경에는 앞쪽 모서리 장식이 이미 그려져 있어 쓰지 않는다 (null)
  function foreground(terrain) {
    if (typeof Art !== 'undefined' && Art.image && Art.image(`bg/battle/${terrain}`)) return null;
    const f = document.createElement('canvas'); f.width = CW; f.height = CH;
    const c = f.getContext('2d');
    const P = PAL[terrain] || PAL.plains;
    // 잎 덩어리: 도트 원을 겹쳐 수풀 실루엣을 만든다
    const blob = (cx, cy, r, col) => {
      c.fillStyle = col;
      for (let yy = -r; yy <= r; yy += 2) for (let xx = -r; xx <= r; xx += 2) {
        if (xx * xx + yy * yy <= r * r) c.fillRect(Math.round((cx + xx) / 2) * 2, Math.round((cy + yy) / 2) * 2, 2, 2);
      }
    };
    const dark = mix(P.fore, '#000000', 0.35), hi = mix(P.fore, P.light, 0.35);
    [[0, 1], [CW, -1]].forEach(([edge, dir], side) => {
      for (let i = 0; i < 9; i++) {
        const cx = edge + dir * (hash(i, 11 + side) * 110 - 10), cy = CH - hash(i, 12 + side) * 40 + 6;
        const r = 10 + Math.floor(hash(i, 13 + side) * 14);
        blob(cx, cy, r, dark);
        blob(cx - dir * 3, cy - 4, r - 4, P.fore);
        blob(cx - dir * 5, cy - r + 6, Math.max(3, r / 3), hi);
      }
    });
    return f;
  }

  function mix(a, b, k) {
    const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
    const ch = (sh) => Math.round(((pa >> sh) & 255) * (1 - k) + ((pb >> sh) & 255) * k);
    return `rgb(${ch(16)},${ch(8)},${ch(0)})`;
  }

  // 빛 번짐용 원형 그라데이션 (색·크기별 캐시)
  const glowCache = new Map();
  function glow(color, r) {
    const key = `${color}|${r}`;
    if (glowCache.has(key)) return glowCache.get(key);
    const c = document.createElement('canvas'); c.width = c.height = r * 2;
    const g = c.getContext('2d');
    const gr = g.createRadialGradient(r, r, 0, r, r, r);
    gr.addColorStop(0, color); gr.addColorStop(0.35, color); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.globalAlpha = 1; g.fillStyle = gr; g.fillRect(0, 0, r * 2, r * 2);
    glowCache.set(key, c);
    return c;
  }

  // ───────── 부대 편성 ─────────
  // 양쪽 최대 3개 부대, 부대마다 3~4명(대장 1 + 2~3). 큰 도트(약 32×16 논리 단위)로 그려도 읽히는 규모.
  const MAX_GROUPS = 3;              // 한 진영의 최대 부대 수
  const GROUP_MIN = 3, GROUP_MAX = 4; // 부대 인원 (대장 포함)
  // 적 부대 수: 낮은 난이도 2개, ★5 이상·결전·최종 결전·보스 3개
  const enemyGroupsFor = (q) => (q.campaign || q.final || q.boss || q.level >= 5 ? 3 : 2);

  // report → 부대 설계도 (시드에 따라 결정적)
  function plan(report) {
    const q = report.quest;
    const r = rng(report.seed || q.id * 7919);
    const groups = [];
    const looksFor = (color, n) => Array.from({ length: n }, () => {
      const cls = rPick(r, Object.keys(CLASSES));
      return { cls, skin: rPick(r, SKIN_TONES), hair: rPick(r, HAIR_COLORS), longHair: r() < 0.3, tint: { outfit: color, accent: '#d9a441' } };
    });
    const deadIds = new Set((report.members || []).filter((m) => m.dead).map((m) => m.id));
    const extra = q.level >= 6 ? 1 : 0; // 높은 난이도일수록 꽉 찬 부대가 나온다

    // 아군: 파견된 용병단 (직속 → 외부, 최대 3개)
    (report.companies || []).forEach((c) => {
      if (groups.length >= MAX_GROUPS) return;
      if (c.own && c.members) {
        // 대장 → 이번에 쓰러진 단원 → 레벨 순. 옛 저장의 큰 용병단(5~9명)도 전사자는 반드시 전장에 나온다.
        const ms = [...c.members].sort((a, b) => (b.leader ? 1 : 0) - (a.leader ? 1 : 0)
          || (deadIds.has(b.id) ? 1 : 0) - (deadIds.has(a.id) ? 1 : 0) || b.level - a.level);
        const units = ms.slice(0, GROUP_MAX).map((m) => ({ look: m.look, cls: m.cls, str: (0.85 + m.level * 0.035) * (m.leader ? 1.15 : 1), named: m.name, doomed: deadIds.has(m.id), sk: m.sk, unique: m.unique, art: m.art, capKey: m.capKey || (m.look && m.look.cap) || null, heroKey: m.heroKey || null }));
        // 출격 인원이 셋이 안 되면 수습 용병이 머릿수를 채운다
        looksFor(c.color, Math.max(0, GROUP_MIN - units.length)).forEach((lk) => units.push({ look: lk, cls: lk.cls, str: 0.7, recruit: true }));
        groups.push({ side: 0, name: c.name, color: c.color, player: true, units });
      } else if (!c.own) {
        const n = clamp(c.size || GROUP_MIN, GROUP_MIN, GROUP_MAX);
        const units = [{ look: c.look, cls: c.look.cls, str: 0.9 + c.level * 0.03 }];
        looksFor(c.color, n - 1).forEach((lk) => units.push({ look: lk, cls: lk.cls, str: 0.8 + c.level * 0.025 }));
        groups.push({ side: 0, name: c.name, color: c.color, player: true, ext: true, betray: c.betrayed, units });
      }
    });
    if (!groups.length) {
      // 옛 보고서 호환: 단원 목록만 있는 경우
      const units = [...(report.members || [])].sort((a, b) => (b.dead ? 1 : 0) - (a.dead ? 1 : 0)).slice(0, GROUP_MAX).map((m) => ({ look: m.look, cls: m.cls, str: 1, named: m.name, doomed: m.dead }));
      looksFor('#3d5a9c', Math.max(0, GROUP_MIN - units.length)).forEach((lk) => units.push({ look: lk, cls: lk.cls, str: 0.7, recruit: true }));
      groups.push({ side: 0, name: '길드 용병단', color: '#3d5a9c', player: true, units });
    }

    // 배신할 외부 용병단은 전투 중에 적 진영으로 넘어가므로 적 부대 수에 미리 셈한다 (넘어간 뒤에도 양쪽 최대 3부대)
    const groupsN = Math.min(MAX_GROUPS, enemyGroupsFor(q));
    const traitors = groups.filter((g) => g.betray).length;
    const enemyN = Math.max(1, groupsN - traitors);
    const allyFill = Math.max(0, groupsN - groups.length);

    // 아군 지원 부대: 의뢰주 세력의 병사들 (진영 부대 수를 적과 맞춘다)
    const issuer = q.issuer;
    const ally = FACTIONS[issuer] && !FACTIONS[issuer].neutral ? issuer : null;
    for (let i = 0; i < allyFill; i++) {
      const f = ally || 'locals';
      const n = rInt(r, GROUP_MIN, GROUP_MAX);
      const base = rInt(r, 0, 99); // 부대마다 한 번: 세력의 병과 순서대로 섞인다 (사제만 넷인 부대가 없게)
      const units = Array.from({ length: n }, (_, k) => {
        const lk = UI.h.soldierLook(f, base + k);
        return { look: lk, cls: lk.cls, str: ally ? 0.85 : 0.65 };
      });
      groups.push({ side: 0, name: ally ? `${FACTIONS[f].short} ${FACTIONS[f].unitName}` : '마을 자경단', color: FACTIONS[f].color, units });
    }

    // 적군: 2~3개 부대, 부대마다 우두머리 + 2~3
    if (q.enemy) {
      const def = ENEMIES[q.enemy] || {};
      const cal = FACTIONS[q.target] && FACTIONS[q.target].calamity ? q.target : null;
      const pool = (cal ? FACTIONS[cal].monsters : TERRAIN[PROVINCES[q.province].terrain].enemies).filter((n) => ENEMIES[n] && !ENEMIES[n].boss);
      const small = pool.filter((n) => !ENEMIES[n].big);
      const minion = () => (def.big ? rPick(r, small.length ? small : pool) : (r() < 0.75 ? q.enemy : rPick(r, small.length ? small : [q.enemy])));
      for (let i = 0; i < enemyN; i++) {
        const lead = i === 0 ? q.enemy : (def.boss ? rPick(r, pool) : q.enemy);
        const ldef = ENEMIES[lead] || {};
        const units = [{ mon: lead, scale: ldef.boss ? 3 : 2, str: ldef.boss ? 1.4 : 1.1, boss: !!ldef.boss, bigMon: true }];
        const n = ldef.boss ? rInt(r, 2, 3) : Math.min(GROUP_MAX - 1, rInt(r, GROUP_MIN - 1, GROUP_MAX - 1) + extra);
        for (let k = 0; k < n; k++) {
          const m = minion();
          units.push({ mon: m, scale: ENEMIES[m] && ENEMIES[m].big ? 2 : 1, str: 1, bigMon: !!(ENEMIES[m] && ENEMIES[m].big) });
        }
        groups.push({ side: 1, name: ldef.boss ? lead : `${lead} 무리`, color: cal ? FACTIONS[cal].color : '#7a2430', units });
      }
    } else {
      const f = q.target || q.issuer;
      for (let i = 0; i < enemyN; i++) {
        const n = Math.min(GROUP_MAX, rInt(r, GROUP_MIN, GROUP_MAX) + extra);
        const base = rInt(r, 0, 99);
        const units = Array.from({ length: n }, (_, k) => {
          const lk = UI.h.soldierLook(f, base + k);
          return { look: lk, cls: lk.cls, str: 1 };
        });
        groups.push({ side: 1, name: `${FACTIONS[f].short} ${FACTIONS[f].unitName} ${i + 1}대`, color: FACTIONS[f].color, units });
      }
    }
    return groups;
  }

  // ───────── 시뮬레이션 ─────────
  // groups: plan() 결과, bias: 적 강도 배율, seed: 전투 난수
  // real: 능력치 전투일 때의 편성(spec). 유닛마다 굳혀 둔 st { hp, atk, def } 를 그대로 쓰고 강도(str)·bias 는 쓰지 않는다.
  function setup(groups, bias, seed, real) {
    const r = rng(seed);
    const units = [];
    const gs = groups.map((g, gi) => ({ ...g, id: gi, side: g.side, units: [], routed: false, captain: null, flipped: false }));
    const bySide = [gs.filter((g) => g.side === 0), gs.filter((g) => g.side === 1)];
    bySide.forEach((list, side) => {
      list.forEach((g, i) => {
        // 부대는 한 줄로 위아래에 늘어선다 (진영당 최대 3개). 가운데 부대는 조금 뒤에 서서 겹쳐 보이지 않게 한다.
        const cy = TOP + ((BOTTOM - TOP) * (i + 0.5)) / list.length;
        const back = list.length === 3 && i === 1 ? 14 : 0;
        const cx = side === 0 ? 58 - back : W - 58 + back;
        g.units = groups[g.id].units.map((ud, k) => {
          const captain = k === 0;
          const base = ud.mon ? { ...MONSTER_STATS } : { ...(CLASS_STATS[ud.cls] || CLASS_STATS.warrior) };
          if (ud.mon && ud.bigMon) { base.hp *= ud.boss ? 7 : 2.6; base.atk *= ud.boss ? 2.4 : 1.6; base.speed *= 0.85; }
          // 스킬: 직속 단원은 자기 스킬, 그 밖에는 직업 기본기 (+ 부대장은 범용 특기)
          let skills = ud.sk;
          if (!skills) {
            if (ud.mon) skills = monsterSkills(ud);
            else {
              const basic = (CLASS_SKILLS[ud.cls] || CLASS_SKILLS.warrior).b;
              skills = captain ? [basic, GENERIC_SPECIAL[ud.cls] || GENERIC_SPECIAL.warrior] : [basic];
            }
          }
          let str = ud.str * (side === 1 ? bias : 1);
          if (captain) str *= 1.15;
          if (ud.doomed) str *= 0.6;
          const S = real ? ud.st : null;
          if (S && ud.mon && Stats.ARCH[ud.arch]) base.speed = Stats.ARCH[ud.arch].speed;   // 괴물의 속도는 틀이 정한다
          const hp = S ? S.hp : base.hp * str * (captain && !ud.mon ? 1.6 : 1) * (ud.unique ? 1.15 : 1);
          // 대형: 대장이 뒤 가운데, 대원 둘이 앞 위아래, 셋째는 맨 앞 (큰 도트끼리 겹치지 않는 간격: SEP_X·SEP_Y 타원 밖)
          const fwd = side === 0 ? 1 : -1;
          const SLOT = [[-8, 0], [10, -10], [10, 10], [28, 0]];
          const [sx, sy] = SLOT[k] || [-8 - 18 * (k - 3), k % 2 ? -10 : 10];
          const ox = fwd * sx, oy = sy;
          const unit = {
            g, side, captain, ...ud,
            x: cx + ox + (r() - 0.5) * 4, y: clamp(cy + oy + (r() - 0.5) * 4, TOP, BOTTOM),
            hp, maxHp: hp, atk: S ? S.atk : base.atk * str * ATK_SCALE, def: S ? S.def : 0,
            healPow: S ? S.atk * Stats.KN.HEAL_K : HEAL_POWER * str * ATK_SCALE, speed: base.speed * (0.9 + r() * 0.2),
            dealt: 0, taken: 0, healed: 0, kills: 0,   // 전투 기록용 (계산에는 쓰지 않는다)
            skills: skills.map((sk, i) => ({ ...sk, left: i === 0 ? r() * sk.cd : sk.cd * (0.3 + r() * 0.5) })),
            buffs: [], stunUntil: 0, slowUntil: 0,
            alive: true, fled: false, target: null, retarget: r() * 0.5, face: side === 0 ? 1 : -1,
            moving: false, lunge: 0, flash: 0, downAt: 0, walk: r() * 10,
          };
          unit.healer = unit.skills[0].tgt === 'hurt';
          unit.reach = unit.skills[0].range;
          units.push(unit);
          return unit;
        });
        g.captain = g.units[0];
      });
    });
    return { r, units, groups: gs, shots: [], fx: [], t: 0, over: false, winner: null, endT: 0, events: [], cutins: [],
      real: !!real, rule: real ? real.rule || 'field' : null, limit: real && real.limit ? real.limit : MAX_TIME, end: null };
  }

  const groupAlive = (g) => g.units.filter((u) => u.alive && !u.fled);
  const sideActive = (st, side) => st.groups.some((g) => g.side === side && !g.routed && groupAlive(g).length);
  // Math.hypot 은 느려서 (전투 찾기가 한 판을 여러 번 시뮬레이션한다) 제곱근으로 직접 잰다
  const { sqrt, max, min, abs } = Math;
  const dist = (a, b) => { const dx = a.x - b.x, dy = a.y - b.y; return sqrt(dx * dx + dy * dy); };
  const len2 = (x, y) => sqrt(x * x + y * y);
  const meleeDist = (a, b) => { const dx = a.x - b.x, dy = (a.y - b.y) * DEPTH; return sqrt(dx * dx + dy * dy); };
  const sizeOf = (u) => (u.scale > 1 ? u.scale * 4 : 0);
  const isMelee = (u) => !u.healer && !u.skills[0].shot;

  // 근접 교전 자리 배정: 목표마다 자리(MELEE_SLOTS)를 나눠 쥐어, 여럿이 한 점에 겹쳐 서지 않게 한다.
  // 자리 주인은 그 목표를 계속 노리는 동안만 유효하다 (목표를 바꾸거나 쓰러지면 자리가 빈다).
  const holdsSlot = (a, t, i) => a.alive && !a.fled && !a.g.routed && a.target === t && a.slotOf === t && a.slot === i;
  const slotFree = (t, i, u) => { const a = t.slots[i]; return !a || a === u || !holdsSlot(a, t, i); };
  const slotAt = (t, i, s) => {
    const [ox, oy] = MELEE_SLOTS[i];
    const y = clamp(t.y + oy, TOP, BOTTOM), ny = (y - t.y) / (SEP_FOE_Y + sizeOf(t) * 0.5);
    // 위·아래 경계에 눌려 자리가 목표에 가까워지면 그만큼 옆으로 물린다 (적과의 간격 타원 밖)
    const ax = max(abs(ox) + sizeOf(t), (SEP_FOE_X + sizeOf(t) * 0.75) * sqrt(max(0, 1.08 - ny * ny)));
    return { x: t.x + (ox >= 0 ? s : -s) * ax, y };
  };
  // 목표 곁에 이미 붙은 다른 근접 공격자 수 (다 찼으면 Infinity)
  function crowdOf(t, u) {
    if (!t.slots) return 0;
    let n = 0;
    for (let i = 0; i < slotCount(t); i++) if (!slotFree(t, i, u)) n++;
    return n >= meleeCap(t) ? Infinity : n;
  }
  // 자리를 고를 때, 이미 다른 몸이 서 있는 자리는 건너뛴다 (가 봐야 비켜 달라고 밀 수밖에 없다)
  function spotTaken(p, u, t, live) {
    for (const o of live) {
      if (o.x <= p.x - 29 || o.x >= p.x + 29 || o.y <= p.y - 24 || o.y >= p.y + 24 || o === u || o === t || !o.alive || o.moving) continue;
      const same = o.side === u.side, big = sizeOf(u) + sizeOf(o);
      const mx = (same ? SEP_X : SEP_FOE_X) + big * 0.75, my = (same ? SEP_Y : SEP_FOE_Y) + big * 0.5;
      const dx = (o.x - p.x) / mx, dy = (o.y - p.y) / my;
      if (dx * dx + dy * dy < 0.64) return true;
    }
    return false;
  }
  // u 가 t 를 칠 자리 (자리가 다 찼으면 null)
  function slotPos(t, u, live) {
    if (!t.slots) t.slots = [];
    if (u.slotOf !== t || u.slot < 0 || t.slots[u.slot] !== u) {
      // 새로 자리를 잡는다: 빈자리 중 가장 가까운 곳. 다가오는 쪽(왼쪽/오른쪽)은 이때 정해 둔다.
      const s = u.x <= t.x ? -1 : 1;
      const full = crowdOf(t, u) === Infinity;
      let best = -1, bd = Infinity;
      for (let i = 0; i < slotCount(t) && !full; i++) {
        if (!slotFree(t, i, u)) continue;
        const p = slotAt(t, i, s);
        const d = len2(p.x - u.x, p.y - u.y) + (spotTaken(p, u, t, live) ? 1000 : 0);
        if (d < bd) { bd = d; best = i; }
      }
      u.slotOf = t; u.slot = best; u.slotSide = s;
      if (best < 0) return null;
      t.slots[best] = u;
    }
    return slotAt(t, u.slot, u.slotSide);
  }

  // 길 비키기: 가는 길 앞에 서 있는 몸(아군·적, 내 목표는 빼고)이 있으면 그 옆을 겨눠 돌아간다 (밀고 지나가지 않게).
  // 피할 쪽은 한 번 정하면 같은 몸을 지날 때까지 유지한다 (좌우로 떨지 않게). 위·아래 경계 밖으로는 돌지 않는다.
  const STEER_LOOK = 2.2, STEER_CLR = 1.2;
  function steer(u, live, mx, my, gx, gy, tg) {
    const ml = len2(mx, my) || 1, dx = mx / ml, dy = my / ml;
    let best = null, bA = Infinity, bLat = 0, bMX = 0, bMY = 0, bnx = 0, bny = 0;
    const rxMax = STEER_LOOK * (SEP_X + (sizeOf(u) + 12) * 0.75);
    const ryMax = STEER_LOOK * (SEP_Y + (sizeOf(u) + 12) * 0.5);
    for (const o of live) {
      if (o.x <= u.x - rxMax || o.x >= u.x + rxMax || o.y <= u.y - ryMax || o.y >= u.y + ryMax) continue;
      if (o === u || o === tg || !o.alive || o.fled || (o.side === u.side && (u.g.routed || o.g.routed))) continue;
      if (u.sq && o.side === u.side && !o.moving) continue;   // 비집고 지나가는 중 (SQUEEZE): 서 있는 아군은 돌아가지 않는다
      if (o.moving && (o.vx || 0) * dx + (o.vy || 0) * dy > 0.7 * u.speed * DT) continue;  // 같은 쪽으로 비슷하게 가는 몸은 따라간다
      const same = o.side === u.side, big = sizeOf(u) + sizeOf(o);
      const MX = (same ? SEP_X : SEP_FOE_X) + big * 0.75, MY = (same ? SEP_Y : SEP_FOE_Y) + big * 0.5;
      const rx = (o.x - u.x) / MX, ry = (o.y - u.y) / MY;
      if (rx > STEER_LOOK || rx < -STEER_LOOK || ry > STEER_LOOK || ry < -STEER_LOOK) continue;
      let nx = dx / MX, ny = dy / MY; const nl = len2(nx, ny) || 1; nx /= nl; ny /= nl;
      const along = rx * nx + ry * ny;
      if (along <= 0 || along > STEER_LOOK || along >= bA) continue;
      const lat = -rx * ny + ry * nx;
      if (lat >= 1 || lat <= -1) continue;
      const gAlong = ((gx - u.x) / MX) * nx + ((gy - u.y) / MY) * ny;
      if (gAlong < along - 0.6) continue;           // 목적지가 그 몸보다 앞이면 피할 것 없다
      best = o; bA = along; bLat = lat; bMX = MX; bMY = MY; bnx = nx; bny = ny;
    }
    if (!best) { u.avoid = null; return null; }
    let s = u.avoid && u.avoid.o === best ? u.avoid.s : (bLat > 0.08 ? -1 : bLat < -0.08 ? 1 : (u.y < (TOP + BOTTOM) / 2 ? 1 : -1) * (bny >= 0 ? 1 : -1) || 1);
    const way = (k) => ({ x: best.x + k * -bny * STEER_CLR * bMX, y: best.y + k * bnx * STEER_CLR * bMY });
    let w = way(s);
    if (w.y < TOP || w.y > BOTTOM) { const w2 = way(-s); if (w2.y >= TOP && w2.y <= BOTTOM) { s = -s; w = w2; } else w.y = clamp(w.y, TOP, BOTTOM); }
    u.avoid = { o: best, s };
    let ax = w.x - u.x, ay = w.y - u.y; const al = len2(ax, ay) || 1; ax /= al; ay /= al;
    if (ax * dx + ay * dy < 0) { ax = s * -dy; ay = s * dx; }   // 뒤로 돌지는 않는다: 옆으로 비킨다
    return [ax, ay];
  }
  const GHOST_FAR = 20;
  const SQUEEZE = 2;                 // 거듭 막힌 걸음이 서 있는 아군을 지나갈 수 있는 시간(초)
  const GAIN = 2, STALL = 3;         // 닿지 못한 걸음이 목표와의 거리를 GAIN(px)도 못 줄인 채 STALL 초를 걸으면 막힌 것으로 친다
  // 원거리·치유: 서 있는 아군과 몸이 깊이 겹친 채로는 멈추지 않는다 (조금 더 걸어 나가 선다)
  function crowdedAt(u, live) {
    for (const o of live) {
      if (o.x <= u.x - 28 || o.x >= u.x + 28 || o.y <= u.y - 24 || o.y >= u.y + 24) continue;
      if (o === u || !o.alive || o.moving || o.side !== u.side) continue;
      const big = sizeOf(u) + sizeOf(o), mx = SEP_X + big * 0.75, my = SEP_Y + big * 0.5;
      const dx = (o.x - u.x) / mx, dy = (o.y - u.y) / my;
      if (dx * dx + dy * dy < 0.6) return true;
    }
    return false;
  }
  const buffSum = (u, k, t) => u.buffs.reduce((a, b) => a + (b.until > t ? (b[k] || 0) : 0), 0);
  const atkMul = (u, t) => {
    const cap = u.g.captain;
    const aura = cap.alive && cap !== u && len2(cap.x - u.x, cap.y - u.y) < 60 ? 1.1 : 1; // 대장 곁의 대원은 힘이 난다
    return (1 + buffSum(u, 'atk', t)) * aura;
  };
  const defMul = (u, t) => 1 - min(0.6, buffSum(u, 'def', t));

  function addBuff(st, u, b) { if (b) u.buffs.push({ atk: b.atk || 0, def: b.def || 0, until: st.t + b.dur }); }

  function damage(st, target, dmg, crit, src) {
    if (!target.alive) return 0;
    dmg *= defMul(target, st.t);
    if (src) src.dealt += min(dmg, target.hp);
    target.taken += dmg;
    target.hp -= dmg;
    target.flash = 0.18;
    st.fx.push({ kind: 'pop', x: target.x, y: target.y - 18, text: String(Math.round(dmg)), crit, ally: target.side === 0,
      mine: !!(src && src.side === 0 && src.unique), named: !!target.named, t: 0 });
    if (target.hp <= 0) {
      target.alive = false;
      target.hp = 0;
      target.downAt = st.t;
      if (src) src.kills++;
      if (target.captain) st.events.push({ t: st.t, text: `${target.g.name}의 대장이 쓰러졌다!`, side: target.side });
    }
    return dmg;
  }

  // 공격 스킬 한 번이 대상에 닿았을 때
  function strike(st, u, t, sk) {
    if (!t.alive) return;
    const crit = st.r() < 0.1;
    const A = u.atk * atkMul(u, st.t);
    const base = A * sk.dmg * (0.85 + st.r() * 0.3) * (crit ? 1.7 : 1);
    const victims = sk.aoe ? st.units.filter((e) => e.alive && !e.fled && e.side !== u.side && dist(e, t) <= sk.aoe + sizeOf(e)) : [t];
    if (!victims.includes(t)) victims.push(t);
    let dealt = 0;
    victims.forEach((e) => {
      let d = base * (e === t ? 1 : 0.7);
      // 능력치 전투: 비율 방어 — K · 공격 / (공격 + 방어 × (1 - 관통)). 방어가 높아도 피해가 0 이 되지는 않는다.
      if (st.real) {
        const pierce = sk.pierce != null ? sk.pierce : (Stats.KN.PIERCE[sk.shot] || 0);
        d *= Stats.KN.K * A / (A + e.def * (1 - pierce));
      }
      if (sk.exec && e.hp / e.maxHp < 0.35) d *= 1 + sk.exec;
      dealt += damage(st, e, d, crit && e === t, u);
      if (sk.stun && e.alive) e.stunUntil = max(e.stunUntil, st.t + sk.stun * (e.boss ? 0.3 : e.bigMon ? 0.6 : 1));
      if (sk.slow && e.alive) e.slowUntil = max(e.slowUntil || 0, st.t + sk.slow * (e.boss ? 0.4 : e.bigMon ? 0.7 : 1));
    });
    const special = sk !== u.skills[0];
    st.fx.push({ kind: 'hit', x: t.x, y: t.y - 8, dir: u.face, melee: !sk.shot, style: sk.shot ? null : meleeStyle(sk), big: crit || special, special, t: 0,
      color: SHOT_COLOR[sk.shot] || (u.side === 0 ? '#bfe8ff' : '#ffb0a0') });
    if (sk.aoe) st.fx.push({ kind: 'boom', x: t.x, y: t.y - 8, r: sk.aoe, t: 0, color: SHOT_COLOR[sk.shot] || '#f39c12' });
    if (sk.drain && u.alive) {
      u.hp = min(u.maxHp, u.hp + dealt * sk.drain);
      if (dealt > 0) st.fx.push({ kind: 'drain', x: t.x, y: t.y, tx: u.x, ty: u.y, t: 0 });
    }
    if (sk.selfBuff) addBuff(st, u, sk.selfBuff);
  }

  function mend(st, u, t, sk) {
    const list = sk.aoe ? st.units.filter((a) => a.alive && !a.fled && a.side === u.side && dist(a, t) <= sk.aoe) : [t];
    list.forEach((a) => {
      if (!a.alive) return;
      const before = a.hp;
      a.hp = min(a.maxHp, a.hp + u.healPow * sk.heal * (0.9 + st.r() * 0.2));
      u.healed += a.hp - before;
      st.fx.push({ kind: 'heal', x: a.x, y: a.y - 14, t: 0, named: !!a.named });
      if (sk.buff) addBuff(st, a, sk.buff);
    });
    if (sk.aoe) st.fx.push({ kind: 'ring', x: t.x, y: t.y - 6, r: sk.aoe, t: 0, color: '#7ed37e' });
  }

  // 스킬을 쓸 대상 찾기 (없으면 null)
  function pickTarget(st, u, sk, live) {
    if (sk.tgt === 'self') return live.some((e) => e.side !== u.side && !e.g.routed && dist(e, u) < 70) ? u : null;
    if (sk.tgt === 'hurt') {
      let best = null, worst = sk === u.skills[0] ? 0.9 : 0.7;
      for (const a of live) {
        if (a.side !== u.side) continue;
        const ratio = a.hp / a.maxHp;
        if (ratio < worst && dist(a, u) <= sk.range) { worst = ratio; best = a; }
      }
      return best;
    }
    const reach = (sk.dash ? max(sk.range, 60) : sk.range + (sk.shot ? 0 : BODY));
    let best = null, bd = Infinity;
    for (const e of live) {
      if (e.side === u.side || e.g.routed) continue;
      const d = (sk.shot ? dist(e, u) : meleeDist(e, u)) - sizeOf(e);
      if (d <= reach && d < bd) { bd = d; best = e; }
    }
    return best;
  }

  function useSkill(st, u, sk, t, live) {
    sk.left = sk.cd * (0.9 + st.r() * 0.2);
    if (sk !== u.skills[0] && (u.named || u.captain || u.boss)) st.fx.push({ kind: 'label', x: u.x, y: u.y - 26, text: sk.name, t: 0, side: u.side });
    if (sk !== u.skills[0]) st.fx.push({ kind: 'cast', x: u.x, y: u.y, t: 0, r: max(12, sk.aoe || 12), color: sk.tgt === 'hurt' ? '#7ed37e' : SHOT_COLOR[sk.shot] || (sk.buff ? '#f2c94c' : '#ffffff') });
    // 아군 대장·특별 용병의 특기는 컷인으로 보여 준다
    if (sk !== u.skills[0] && u.unique && u.side === 0) st.cutins.push({ t: st.t, name: u.named, skill: sk.name, art: u.art, look: u.look });
    if (sk.tgt === 'self') {
      st.fx.push({ kind: 'skill', type: 'rally', x: u.x, y: u.y, r: sk.aoe, def: !!sk.buff.def, t: 0 });
      st.units.filter((a) => a.alive && !a.fled && a.side === u.side && dist(a, u) <= sk.aoe).forEach((a) => addBuff(st, a, sk.buff));
      st.fx.push({ kind: 'ring', x: u.x, y: u.y - 6, r: sk.aoe, t: 0, color: sk.buff.def ? '#7fd6e8' : '#ef6a6a' });
      return;
    }
    if (sk.tgt === 'hurt') {
      const healed = sk.aoe ? live.filter((a) => a.side === u.side && dist(a, t) <= sk.aoe) : [t];
      st.fx.push({ kind: 'skill', type: 'heal', special: sk !== u.skills[0], aoe: sk.aoe || 0, x: t.x, y: t.y,
        targets: healed.slice(0, 8).map((a) => [a.x, a.y]), t: 0 });
      if (sk.shot && !sk.aoe) st.shots.push({ kind: 'holy', from: u, to: t, x: u.x, y: u.y - 9, sk, speed: 170, heal: true });
      else mend(st, u, t, sk);
      return;
    }
    // 공격: 여러 대상이면 가까운 순으로
    let targets = [t];
    if (sk.hits > 1) {
      targets = live.filter((e) => e.side !== u.side && !e.g.routed && dist(e, u) - sizeOf(e) <= max(sk.range, 30) + 20)
        .sort((a, b) => dist(a, u) - dist(b, u)).slice(0, sk.hits);
      if (!targets.length) targets = [t];
    }
    const fromX = u.x, fromY = u.y;
    if (sk.dash) {
      // 돌진: 대상 곁으로 뛰어든다
      const d = dist(u, t) || 1;
      const stop = MELEE_SLOTS[0][0] + sizeOf(t); // 정면 자리 거리에서 멈춘다
      if (d > stop) { u.x = t.x - ((t.x - u.x) / d) * stop; u.y = t.y - ((t.y - u.y) / d) * stop; }
      u.dashed = u.x !== fromX || u.y !== fromY;
      st.fx.push({ kind: 'dash', x: u.x, y: u.y - 6, t: 0 });
    }
    u.face = t.x >= u.x ? 1 : -1;
    const special = sk !== u.skills[0];
    st.fx.push({ kind: 'skill', type: 'atk', special, boss: !!u.boss, side: u.side, look: u.look, mon: u.mon, scale: u.scale,
      shot: sk.shot || null, aoe: sk.aoe || 0, hits: sk.hits || 1, stun: !!sk.stun, dash: !!sk.dash, exec: !!sk.exec,
      x: u.x, y: u.y, fx0: fromX, fy0: fromY, face: u.face, targets: targets.slice(0, 6).map((e) => [e.x, e.y]), t: 0 });
    targets.forEach((e) => {
      if (sk.shot) st.shots.push({ kind: sk.shot, from: u, to: e, x: u.x, y: u.y - 9, sx: u.x, sy: u.y - 9, sk, speed: 170,
        meteor: special && sk.shot === 'fire' && (sk.aoe || 0) >= 20 });
      else { u.lunge = 0.15; strike(st, u, e, sk); }
    });
  }

  function step(st) {
    const { r, units } = st;
    st.t += DT;
    // 능력치 전투는 결판이 난 뒤로 아무것도 더 정하지 않는다 (배신·패주 판정도 멈춘다): 결판 순간의 기록이 화면 유지 시간 동안 바뀌지 않게
    const done = st.real && st.over;
    // 배신: 충성도가 바닥난 외부 용병단이 전투 도중 적으로 돌아선다
    st.groups.forEach((g) => {
      if (g.betray && !g.flipped && st.t > 7 && !done) {
        g.flipped = true; g.side = 1;
        g.units.forEach((u) => { u.side = 1; u.target = null; });
        st.events.push({ t: st.t, text: `「${g.name}」${josa(g.name, '이', '가')} 적에게 돌아섰다!`, side: 1 });
      }
    });
    // 후퇴 (능력치 전투, 우리 쪽만): 우리 단원의 절반이 쓰러지고 남은 체력이 적의 절반에 못 미치면, 서 있는 아군이 모두 물러난다.
    // 진 싸움에서 끝까지 버티다 다 쓰러지지 않게 하는 최소한의 규칙 — 패배로 끝난다 (end: 'retreat').
    if (st.real && !st.over && !st.end && Stats.KN.RETREAT) {
      let n = 0, dn = 0, hpA = 0, hpB = 0;
      for (const u of units) {
        if ((u.g.kind === 'own' || u.g.kind === 'ext') && !u.g.betray && !u.recruit) { n++; if (!u.alive) dn++; }
        if (u.alive && !u.fled && !u.g.routed) { if (u.side === 0) hpA += u.hp; else hpB += u.hp; }
      }
      if (n && dn / n >= Stats.KN.RETREAT_DOWN && hpA < Stats.KN.RETREAT_RATIO * hpB) {
        st.end = 'retreat';
        st.groups.forEach((g) => { if (g.side === 0) g.routed = true; });
      }
    }
    // 사기: 병력 대부분을 잃거나 대장을 잃고 크게 꺾이면 패주
    st.groups.forEach((g) => {
      if (g.routed || done) return;
      const alive = groupAlive(g).length, n = g.units.length;
      if (!alive) { g.routed = true; return; }
      if (alive / n < 0.3 || (!g.captain.alive && alive / n < 0.55)) {
        g.routed = true;
        st.events.push({ t: st.t, text: `${g.name} 패주!`, side: g.side });
      }
    });
    const live = units.filter((u) => u.alive && !u.fled);
    for (const u of live) { u.ox = u.x; u.oy = u.y; u.dashed = false; }
    for (const u of live) {
      u.flash = max(0, u.flash - DT); u.lunge = max(0, u.lunge - DT);
      u.skills.forEach((sk) => { sk.left -= DT; });
      u.moving = false; u.wantStep = 0; u.far = false; u.short = false; u.sq = false;
      const SPD = u.speed * (u.slowUntil > st.t ? SLOW_MUL : 1);   // 거미줄에 걸리면 느리게
      if (u.g.routed) {
        // 자기 진영 쪽 가장자리로 도주
        const dir = u.g.side === 0 && !u.g.flipped ? -1 : 1;
        const sv = steer(u, live, dir, 0, dir * 1000, u.y, null);
        u.x += (sv ? sv[0] : dir) * SPD * 1.25 * DT; u.y += (sv ? sv[1] : 0) * SPD * 1.25 * DT; u.face = dir; u.moving = true;
        if (u.x < -12 || u.x > W + 12) u.fled = true;
        continue;
      }
      if (st.over || u.stunUntil > st.t) continue;
      // 특기: 준비되면 먼저 쓴다
      const special = u.skills[1];
      if (special && special.left <= 0) {
        const t = pickTarget(st, u, special, live);
        if (t) { useSkill(st, u, special, t, live); continue; }
      }
      const basic = u.skills[0];
      // 치유형: 다친 아군이 있으면 치유, 없으면 전열 뒤를 따라간다
      if (u.healer) {
        const t = pickTarget(st, u, basic, live);
        if (t && basic.left <= 0) { useSkill(st, u, basic, t, live); continue; }
        if (!t) {
          let foe = null, fd = Infinity;
          for (const e of live) { if (e.side !== u.side && !e.g.routed) { const d = dist(e, u); if (d < fd) { fd = d; foe = e; } } }
          if (foe && fd > basic.range * 0.9) {
            const dx = foe.x - u.x, dy = foe.y - u.y, d = len2(dx, dy) || 1;
            const sv = steer(u, live, dx / d, dy / d, foe.x, foe.y, foe);
            const hx = sv ? sv[0] : dx / d, hy = sv ? sv[1] : dy / d;
            u.x += hx * SPD * DT; u.y += hy * SPD * DT; u.moving = true; u.face = dx >= 0 ? 1 : -1; u.wantStep = SPD * DT; u.far = true;
          }
        }
        continue;
      }
      // 목표 재선정: 가까운 적, 같은 높이(전열)를 조금 더 선호. 근접은 자리가 다 찬 적을 피한다 (한 명에게 우르르 몰리지 않게)
      u.retarget -= DT;
      const crowd = isMelee(u);
      if (!u.target || !u.target.alive || u.target.fled || u.target.side === u.side || u.target.g.routed || u.retarget <= 0) {
        u.retarget = 0.4 + r() * 0.3;
        let best = null, bd = Infinity;
        for (const e of live) {
          if (e.side === u.side || e.g.routed) continue;
          const d = abs(e.x - u.x) + abs(e.y - u.y) * 1.4 + (e.captain ? -6 : 0) + (crowd ? min(48, crowdOf(e, u) * 16) : 0);
          if (d < bd) { bd = d; best = e; }
        }
        u.target = best;
      }
      const tg = u.target;
      if (!tg) continue;
      const dx = tg.x - u.x, dy = tg.y - u.y, d = len2(dx, dy) || 1;
      u.face = dx >= 0 ? 1 : -1;
      const reach = basic.range + sizeOf(tg) + (basic.shot ? 0 : BODY);
      // 근접: 목표 곁의 자기 자리로 간다 (정면·비스듬히 위아래). 자리가 다 찼으면 한 걸음 물러서 기다린다.
      const melee = !basic.shot;
      const md = melee ? meleeDist(u, tg) : d;
      let gx = tg.x, gy = tg.y;
      if (melee) {
        const p = slotPos(tg, u, live);
        if (p) { gx = p.x; gy = p.y; } else { gx = tg.x + u.slotSide * (reach + 14); gy = u.y; }
      }
      const ex = gx - u.x, ey = gy - u.y, ed = len2(ex, ey);
      u.sq = u.squeeze > st.t; u.short = md > reach; u.md = md;
      u.far = md > reach + GHOST_FAR || u.sq;   // 거듭 막혔던 걸음은 잠깐 서 있는 아군 사이를 비집고 지나간다 (아래 stuckN)
      if (md > reach || (melee && ed > 3) || (!melee && crowdedAt(u, live))) {
        // 대장 근처로 모이려는 힘을 약간 섞는다 (부대 대형 유지) — 목표에 닿기 전까지만
        let mx = ex / (ed || 1), my = ey / (ed || 1);
        const cap = u.g.captain;
        if (md > reach && !u.captain && cap.alive) {
          const cx = cap.x - u.x, cy = cap.y - u.y, cd = len2(cx, cy);
          if (cd > 32) { mx += (cx / cd) * 0.45; my += (cy / cd) * 0.45; }
        }
        const sv = steer(u, live, mx, my, gx, gy, tg);
        if (sv) { mx = sv[0]; my = sv[1]; }
        const ml = len2(mx, my) || 1;
        // 이미 닿은 채 자리를 고쳐 서는 중이면 천천히
        const v = SPD * DT * (md > reach ? 1 : 0.5);
        const stepLen = min(v, ed || v);
        u.x += (mx / ml) * stepLen; u.y += (my / ml) * stepLen;
        u.moving = stepLen > 0.2; u.wantStep = stepLen;
      } else if (basic.shot && d < reach * 0.45) {
        // 원거리 유닛은 너무 붙으면 물러난다
        u.x -= (dx / d) * SPD * 0.6 * DT; u.y -= (dy / d) * SPD * 0.3 * DT;
        u.moving = true; u.wantStep = len2(dx * 0.6, dy * 0.3) / d * SPD * DT;
      }
      if (md <= reach && basic.left <= 0) useSkill(st, u, basic, tg, live);
    }
    // 겹침 방지: 가로로 넓고 깊이(세로)로 얕은 타원 간격. 큰 도트가 한 덩어리로 뭉개지지 않게 한다.
    // 이번 틱에 제 발로 움직인 쪽(걷기·물러서기·도주·돌진)이 비켜 선다: 서 있는 유닛은 지나가는 유닛에게 밀리지 않는다.
    // 둘 다 움직였으면 반씩, 둘 다 서 있으면 깊이 겹친 만큼만 천천히 벌린다 (서서 싸우는 유닛이 질질 밀리지 않게).
    for (const u of live) u.own = u.x !== u.ox || u.y !== u.oy;
    for (let i = 0; i < live.length; i++) {
      const a = live[i];
      if (!a.alive) continue;
      for (let j = i + 1; j < live.length; j++) {
        const b = live[j];
        if (b.x <= a.x - 36 || b.x >= a.x + 36 || b.y <= a.y - 30 || b.y >= a.y + 30) continue;
        const same = a.side === b.side;
        if (!b.alive || a.fled || b.fled || (same && (a.g.routed || b.g.routed))) continue;
        const big = sizeOf(a) + sizeOf(b);
        const mx = (same ? SEP_X : SEP_FOE_X) + big * 0.75, my = (same ? SEP_Y : SEP_FOE_Y) + big * 0.5;
        const ddx = (b.x - a.x) || (j % 2 ? 0.01 : -0.01), ddy = b.y - a.y;
        if (abs(ddx) >= mx || abs(ddy) >= my) continue;
        const nx = ddx / mx, ny = ddy / my;
        const nd2 = nx * nx + ny * ny;
        if (nd2 >= 1) continue;
        const nd = sqrt(nd2);
        const ux = nx / nd, uy = ny / nd;
        let pa, pb;
        if (a.dashed !== b.dashed) {
          pa = a.dashed ? 1 - nd : 0; pb = b.dashed ? 1 - nd : 0;
        } else if (a.own !== b.own) {
          // 서 있는 아군 곁은 걷는 쪽이 조금 겹쳐 지나가도 된다 (몸 사이를 빠져나가는 정도): 그보다 깊을 때만 걷는 쪽을 물린다
          const lim = same ? ((a.own ? a : b).far || (a.own ? a : b).g.routed ? 0 : 0.85) : 1;
          if (nd >= lim) continue;
          const p = lim - nd; pa = a.own ? p : 0; pb = a.own ? 0 : p;
        }
        else if (a.own) pa = pb = (1 - nd) * 0.5;
        else { if (nd >= 0.6) continue; pa = pb = min(0.6 - nd, DT * 0.9) * 0.5; }
        a.x -= ux * pa * mx; a.y -= uy * pa * my * 0.8;
        b.x += ux * pb * mx; b.y += uy * pb * my * 0.8;
      }
    }
    live.forEach((u) => { u.y = clamp(u.y, TOP, BOTTOM); if (!u.g.routed) { const e = EDGE + sizeOf(u) * EDGE_BIG; u.x = clamp(u.x, e, W - e); } });
    // 앞이 막혀 한 걸음의 3할도 못 나아갔으면 그 자리에 선다 (서 있는 몸에 대고 제자리 달리기하지 않게: 비킬 때까지 기다린다)
    for (const u of live) {
      if (!u.moving || u.g.routed || !u.wantStep || u.dashed) { if (!u.blocked) { u.stuckN = 0; u.jit = 0; u.gt = null; } continue; }
      const frozen = len2(u.x - u.ox, u.y - u.oy) < u.wantStep * 0.3;
      if (frozen) { u.x = u.ox; u.y = u.oy; u.moving = false; u.blocked = (u.blocked || 0) + DT; }
      else {
        u.blocked = 0;
        // 걸음마다 3할은 나아가도 두 아군 사이를 피할 쪽만 번갈아 바꾸며 제자리에서 떨 수 있다 (대치의 다른 꼴: 1~5px 왕복).
        // 목표에 닿지 못한 채 같은 목표와의 거리를 GAIN 만큼도 줄이지 못하면 그 시간도 막힌 시간으로 센다. 줄여야 '걸었다'로 친다
        if (u.short && u.gt === u.target && u.md > u.gd - GAIN) u.jit += DT;
        else { u.gt = u.target; u.gd = u.md; u.jit = 0; u.stuckN = 0; }
      }
      // 1초 넘게 막혀 있거나 STALL 초 동안 목표에 다가가지 못했으면 자리를 내놓고 다시 고른다 (줄이 얼어붙지 않게).
      // 다시 골라도 같은 자리·같은 길이라 한 걸음도 못 떼고 또 막히면 (stuckN ≥ 2): 서 있는 아군(치유사·수습)이 목표와의 사이를
      // 벽처럼 막은 것이다 — 양쪽이 30px 거리에서 90초까지 멈춰 섰다 (4단계 미해결 '대치'). 그때는 SQUEEZE 초 동안 멀리서 걸어올 때처럼
      // 서 있는 아군을 지나가게 하고 (u.far), 막은 것이 적이면 (적은 지나갈 수 없다) 지금 닿는 적을 목표로 삼는다
      if (u.blocked > 1 || u.jit > STALL) {
        u.blocked = 0; u.jit = 0;
        if (u.slotOf && u.slotOf.slots && u.slotOf.slots[u.slot] === u) u.slotOf.slots[u.slot] = null; u.slotOf = null; u.slot = -1;
        if ((u.stuckN = (u.stuckN || 0) + 1) >= 2) {
          u.squeeze = st.t + SQUEEZE;
          const near = u.healer ? null : pickTarget(st, u, u.skills[0], live);
          if (near && near !== u.target) { u.target = near; u.retarget = SQUEEZE; }
        }
      }
    }
    for (const u of live) { u.vx = u.x - u.ox; u.vy = u.y - u.oy; }
    // 투사체
    for (let i = st.shots.length - 1; i >= 0; i--) {
      const s = st.shots[i];
      const tx = s.to.x, ty = s.to.y - 9;
      const dd = len2(tx - s.x, ty - s.y);
      const stepLen = s.speed * DT;
      if (dd <= stepLen) {
        if (st.real && st.over) { /* 능력치 전투: 결판이 난 뒤에 닿는 투사체는 아무 일도 하지 않는다 (기록이 바뀌지 않게) */ }
        else if (s.heal) mend(st, s.from, s.to, s.sk);
        else strike(st, s.from, s.to, s.sk);
        st.shots.splice(i, 1);
      } else {
        s.x += ((tx - s.x) / dd) * stepLen; s.y += ((ty - s.y) / dd) * stepLen;
      }
    }
    // 결판
    if (!st.over) {
      const a = sideActive(st, 0), b = sideActive(st, 1);
      if (!a || !b || st.t >= st.limit) {
        st.over = true; st.endT = st.t;
        if (a && b && st.real) {
          // 능력치 전투의 시간 제한: 버티는 의뢰(hold)는 끝까지 서 있으면 승리, 그 밖(field)은 적을 못 무너뜨렸으면 패배
          st.winner = st.rule === 'hold' ? 0 : 1; st.end = 'time';
        } else if (a && b) {
          const hpOf = (side) => units.filter((u) => u.side === side && u.alive && !u.fled).reduce((sum, u) => sum + u.hp, 0);
          st.winner = hpOf(0) >= hpOf(1) ? 0 : 1;
        } else st.winner = a ? 0 : 1;
        st.groups.forEach((g) => { if (g.side !== st.winner) g.routed = true; });
      }
    }
  }

  // 플레이어 용병단의 손실 비율
  function playerLoss(st) {
    const us = st.units.filter((u) => u.g.player && !u.g.betray);
    if (!us.length) return 0;
    return us.filter((u) => !u.alive).length / us.length;
  }

  function simulate(groups, bias, seed) {
    const st = setup(groups, bias, seed);
    while (!st.over) step(st);
    return { won: st.winner === 0, loss: playerLoss(st), t: st.t };
  }

  // 판정 결과와 맞는 전투를 찾는다: 적의 강도를 조정하며 시뮬레이션
  // 시간 제한까지 버틴 전투(전멸·궤주 없이 남은 체력으로 승패가 갈림)는 화면에서 줄이 멈춘 채 오래 끌다 갑자기 끝나므로 받지 않는다
  const SLOW_T = 60;                 // 이보다 오래 걸린 전투는 '늘어진' 것으로 보고 다른 시드·강도를 찾는다
  function findBattle(groups, outcome, seed) {
    const want = outcome === 'great' || outcome === 'success';
    let bias = want ? (outcome === 'great' ? 0.7 : 0.95) : outcome === 'fail' ? 1.15 : 1.35;
    let lo = 0.1, hi = 6;
    let best = null;
    // 대안 순위: 승패가 맞는 것 > 늘어지지 않은 것 (같으면 나중 것)
    const rank = (res) => (res.won === want ? 2 : 0) + (res.t < SLOW_T ? 1 : 0);
    for (let i = 0; i < 16; i++) {
      const s = seed + i * 101;
      const res = simulate(groups, bias, s);
      const slow = res.t >= SLOW_T;
      const ok = res.won === want && !slow
        && (outcome !== 'great' || res.loss <= 0.25)
        && (outcome !== 'success' || res.loss > 0.05 || i > 4)
        && (outcome !== 'disaster' || res.loss >= 0.5);
      if (ok) return { bias, seed: s, res };
      if (!best || rank(res) >= rank(best.res)) best = { bias, seed: s, res };
      // 아군이 이겨야 하는데 졌거나, 대성공인데 피해가 크거나, 늘어졌으면 적을 약하게 (져야 하면 반대로)
      const weaker = want ? (!res.won || (outcome === 'great' && res.loss > 0.25) || slow) : false;
      const stronger = !want ? (res.won || (outcome === 'disaster' && res.loss < 0.5) || slow) : (outcome === 'success' && res.loss <= 0.05);
      if (weaker) hi = bias; else if (stronger) lo = bias;
      bias = sqrt(lo * hi);
    }
    return best;
  }

  // ───────── 능력치 전투 (그림자) ─────────
  // spec(js/muster.js 가 출격 때 굳힌 편성) 하나로 한 판을 끝까지 돌린다. 같은 spec 이면 언제나 같은 기록이 나온다.
  // 전투 계산을 바꾸면 VER 을 올린다. 편성 밖에서 읽는 표(스킬·속도·조정값)는 tab 요약값으로 따로 지킨다.
  const VER = 1;
  const fnv = (h, v) => { for (let i = 0; i < 4; i++) { h ^= (v >>> (i * 8)) & 0xff; h = Math.imul(h, 0x01000193) >>> 0; } return h; };
  let fixedTables = null;
  let tabSource = null, tabCache = null;
  function tablesDigest() {
    if (fixedTables === null) {
      const monsterTable = Object.keys(ENEMIES).map((mon) => [mon, ENEMIES[mon].tpl,
        monsterSkills({ mon }), monsterSkills({ mon, bigMon: true }), monsterSkills({ mon, boss: true, bigMon: true })]);
      fixedTables = JSON.stringify([VER, DT, CLASS_STATS, MONSTER_STATS.speed, GENERIC_SPECIAL, SLOW_MUL,
        Object.keys(CLASS_SKILLS).map((k) => CLASS_SKILLS[k].b), monsterTable]);
    }
    const src = JSON.stringify([Stats.KN, Stats.ARCH, Stats.REF, Stats.RANK]);
    if (src === tabSource) return tabCache;
    tabSource = src;
    let h = 0x811c9dc5;
    for (const table of [fixedTables, src]) {
      for (let i = 0; i < table.length; i++) { h ^= table.charCodeAt(i) & 0xff; h = Math.imul(h, 0x01000193) >>> 0; h ^= table.charCodeAt(i) >>> 8; h = Math.imul(h, 0x01000193) >>> 0; }
    }
    return (tabCache = h);
  }
  const begin = (spec) => setup(spec.groups, 1, spec.seed, spec);
  const END_CODE = { wipe: 1, rout: 2, retreat: 3, time: 4 };
  // 결판이 난 상태 → 기록. units 는 편성 순서대로 한 줄씩 [결말, 체력%, 쓰러진 틱, 준 피해, 받은 피해, 처치, 치유] (모두 정수)
  // 결말: 0 무사, 1 쓰러짐, 2 물러남(도주했거나 부대가 패주). hash 는 판정이 읽는 값을 모두 덮는다 (승패·끝난 틱·끝난 까닭·줄 전부).
  function record(st) {
    const rows = [];
    st.groups.forEach((g) => g.units.forEach((u) => rows.push([
      !u.alive ? 1 : (u.fled || g.routed) ? 2 : 0, Math.round(100 * max(0, u.hp) / u.maxHp), u.alive ? 0 : Math.round(u.downAt / DT),
      Math.round(u.dealt), Math.round(u.taken), u.kills, Math.round(u.healed)])));
    const ticks = Math.round(st.endT / DT);
    const end = st.end || (st.units.some((u) => u.side !== st.winner && u.alive) ? 'rout' : 'wipe');
    let h = fnv(fnv(fnv(0x811c9dc5, st.winner), ticks), END_CODE[end]);
    rows.forEach((row) => row.forEach((v) => { h = fnv(h, v); }));
    return { ver: VER, tab: tablesDigest(), winner: st.winner, t: +st.endT.toFixed(2), ticks, end, units: rows, hash: h };
  }
  function run(spec) {
    const st = begin(spec);
    while (!st.over) step(st);
    return record(st);
  }

  // ───────── 그리기 ─────────
  // 인물은 두 가지로 그린다.
  //  1) 스프라이트 시트(assets/art/manifest.json 의 sheet/...): 640x360 캔버스에 1:1, 발(anchor)을 유닛 위치에 맞춘다.
  //  2) 시트가 없으면 코드 생성 도트(Sprites.*)를 SPR 배율로 키워서 그린다 (시트 캐릭터 ~64px 와 크기를 맞춘다).
  // 한 칸(frame)은 { img, sx, sy, sw, sh, ax, ay, face, key } 로 다룬다. face: 그림이 바라보는 방향.
  const SPR = 3;                     // 코드 생성 도트 배율 (예전 Z=2 의 1.5배)
  const LIFT = 10;                   // 투사체·타격 효과를 몸통 높이로 올리는 양(px)
  // 괴물 도트 배율: 보통 3, 대형 5, 우두머리 7 (예전 Z×scale 을 그대로 키우면 우두머리가 화면을 덮는다)
  const monScale = (u) => [SPR, SPR, 5, 7][Math.max(1, Math.min(3, u.scale || 1))];
  const useArt = () => typeof Art !== 'undefined' && !!Art.sheetFor;

  // 생성된 캔버스마다 고유 번호 (색 입힌 사본·외곽 계산 캐시의 열쇠)
  const canvasIds = new WeakMap();
  let canvasSeq = 0;
  const keyOfCanvas = (c) => { let k = canvasIds.get(c); if (!k) { k = `c${++canvasSeq}`; canvasIds.set(c, k); } return k; };

  // 유닛별 연출 상태 (시뮬레이션과 분리: view 에만 둔다)
  function rsOf(view, u) {
    let r = view.rs.get(u);
    if (!r) {
      r = { atkAt: -99, atkDur: 0.4, atkAnim: 'attack', hitAt: -99, prevFlash: 0, prevLunge: 0, phase: ((u.walk || 0) * 0.731) % 10, statKey: null, stat: null };
      view.rs.set(u, r);
    }
    return r;
  }

  // 공격 동작 시작 (같은 순간 여러 번 불려도 한 번만)
  function triggerAttack(view, u, kind, onImpact) {
    const r = rsOf(view, u), c = view.clock;
    if (c - (r.trigAt == null ? -9 : r.trigAt) < 0.12) return;
    r.trigAt = c;
    r.atkAnim = kind || 'attack';
    r.atkMelee = false;
    const sh = useArt() && Art.sheetFor(u);
    // 시트의 동작 길이를 휘두르는 시간(0.28~0.5초)에 맞춰 늘이거나 줄인다
    const a = sh && Art.anim(sh.meta, r.atkAnim);
    r.atkDur = a ? Math.max(0.28, Math.min(0.5, a.total / 1000)) : 0.3;
    // 준비 자세를 이미 보여 줬으면(windAt) 타격 칸부터 시작한다 → 맞는 순간(피해·불꽃·멈춤)과 휘두르는 그림이 겹친다.
    // 미리 보여 주지 못한 원거리 공격·시전은 전처럼 준비 칸부터 (쏘는 순간이 타격 칸).
    const wShare = a && a.ms && a.ms.length > 1 ? a.ms[0] / a.total : 0.35;
    // onImpact: 근접 공격(기본·특기)이 맞는 틱에 불린 것 — 준비를 미리 못 보여 줬어도 타격 칸부터 (맞은 뒤에 준비 자세가 나오지 않게)
    const pre = !!onImpact || c - (r.windAt == null ? -9 : r.windAt) < 0.3;
    // 2ms 더 당긴다: 딱 경계에 놓으면 소수 오차로 절반쯤은 준비 칸(149.99ms)이 한 프레임 더 보였고, 타격 멈춤이 그 칸에서 얼었다
    r.atkAt = pre ? c - wShare * r.atkDur - 0.002 : c;
    r.strikeAt = pre ? c : c + wShare * r.atkDur;
    r.windAt = -9;
  }

  // ── 걸음 (연출 전용: 전투 계산과 무관) ──
  // 주인 결정(2026-11-26): 전투에서는 걷지 않고 뛴다. 나아갈 때 = run, 적에게 달려들 때 = charge, 패주 = flee.
  // 걷는 것은 거미줄에 걸렸을 때(trudge)·뒷걸음(back)·맞붙은 채 자리 고치기(reseat)와, 제 발로 가지 않는데 밀리거나 아주 느리게 옮겨질 때(step)뿐이다.
  // 전투 계산이 유닛을 몰고 가는 동안(u.moving)은 느려도 달린다 — 보폭이 빠르기만큼 줄어든다(strideOf).
  // 값은 키(S.h)에 대한 비율:
  //   sl 한 걸음 거리 · wbob 걷기의 몸 오르내림(그려진 칸이 없는 시트 — glideBob, 2% 가 한계) · air 시트 없는 코드 도트가 두 발이 다 뜬 동안 솟는 높이
  //   duty 한 발이 땅에 붙어 있는 길이(걸음 단위): 1 = 걷기(늘 한 발은 땅), 1 미만 = 걸음마다 (1 - duty) 만큼 두 발이 다 뜬다(달리기)
  // 주인 결정(2026-11-26): 서 있는 그림을 잘라·기울여·꺾는 걸음(다리 가르기·무릎·윗몸 숙이기·온몸 기울기)은 없앴다 — 실제 캐릭터가 찌그러져 보였다.
  // 달리기·걷기 동작은 뼈대·마네킹 위에 덧그린 시트 칸(run·walk)이 맡는다 (tools/art/add_gait.py).
  const GAITS = {
    run:    { sl: 0.31, wbob: 0, air: 0.01, duty: 0.62 },        // 달리기 (기본 이동)
    charge: { sl: 0.30, wbob: 0, air: 0.012, duty: 0.56 },       // 적이 가까울 때 달려들기 (근접)
    flee:   { sl: 0.36, wbob: 0, air: 0.014, duty: 0.54 },       // 도주
    trudge: { sl: 0.27, wbob: 0.035, air: 0, duty: 1 },          // 거미줄에 걸려 무겁게 걷기
    back:   { sl: 0.25, wbob: 0.015, air: 0, duty: 1 },          // 적을 보며 뒷걸음
    step:   { sl: 0.25, wbob: 0.02, air: 0, duty: 1 },           // 천천히 자리 옮기기 (달릴 빠르기가 안 될 때)
    reseat: { sl: 0.22, wbob: 0.012, air: 0, duty: 1 },          // 맞붙은 채 자리 고치기
  };
  const RUN_KIND = { run: 1, charge: 1, flee: 1 };                      // 달리는 걸음 (시트의 달리기 칸을 쓰는 걸음)
  const HOVER_MON = { '망령': 1, '하피': 1, '리치의 망령': 1 };          // 떠 있는 몸: 발을 디디지 않는다
  const QUAD_TPL = { beast: 1, bug: 1 };                                // 네발·다족: 앞뒤 반으로 (네발 짐승은 달릴 때 뛰어오른다)
  function gaitType(u, fr) {
    const w = fr.sheet && fr.sheet.meta.walk;
    if (w && w.gait) return w.gait;
    if (!u.mon) return 'biped';
    if (HOVER_MON[u.mon]) return 'hover';
    const e = ENEMIES[u.mon];
    return e && QUAD_TPL[e.tpl] ? 'quad' : 'biped';
  }
  const RESEAT_NEAR = 1.5;                                        // 느리게 몰리는 근접 유닛을 reseat 로 치는 거리 (사거리 배수, + BODY)
  function gaitKind(st, u, r) {
    const slow = u.slowUntil > st.t;                           // 거미줄: 뛰지 못한다
    if (u.g.routed) return slow ? 'trudge' : 'flee';
    let k = 'run', fd = Infinity;
    if (u.skills && isMelee(u)) {
      for (const e of st.units) if (e.alive && !e.fled && e.side !== u.side) { const d = meleeDist(e, u) - sizeOf(e); if (d < fd) fd = d; }
      // 맞붙은 채 밀려나는 것은 뒷걸음이 아니라 자리 고치기다 (뒷걸음으로 치면 걸음이 거꾸로 돌고 준비 자세도 빠졌다)
      if (fd <= (u.reach || 11) * 1.3 + BODY) return 'reseat';
      if (fd < 70) k = 'charge';
    }
    if (r.fwd < 0) return 'back';
    if (slow) return 'trudge';
    // 전투 계산이 몰고 가는 중(u.moving)이면 제 빠르기보다 느려도(대장 곁으로 모이기·겹침에 밀리며 다가가기) 달린다: 보폭을 빠르기 비율만큼 줄여
    // (strideOf) 초당 걸음 수를 지킨다. 걷는 step 은 제 발로 가지 않는데 밀려 움직일 때(!u.moving)와 제 빠르기의 4할도 안 되는 아주 느린 움직임뿐
    // (달리기 → 걷기는 0.4 아래, 걷기 → 달리기는 0.5 위: 경계에서 오락가락하지 않게)
    const vr = r.vr == null ? 1 : r.vr;
    r.slowMove = !u.moving || vr < (r.slowMove ? 0.5 : 0.4);
    // 적 가까이(사거리 RESEAT_NEAR 배 안)에서 전투 계산이 아주 느리게 모는 근접 유닛은 막혀서 자리를 찾는 중이다: 걷지 않고 자리 고치기(reseat) 잔걸음
    if (r.slowMove && u.moving && fd <= (u.reach || 11) * RESEAT_NEAR + BODY) return 'reseat';
    return r.slowMove ? 'step' : k;
  }
  // 한 걸음 거리(px): 걸음 종류의 값 × 키. 빠른 유닛은 걸음 수보다 보폭이 먼저 늘어난다 (도적이 종종걸음 치지 않게).
  // 달리는 걸음(run·charge·flee)은 실제 빠르기 ÷ 제 빠르기(r.vr, 0.55..1)만큼 보폭을 줄인다: 느리게 다가가도 초당 걸음 수가 그대로다
  // (vr 0.55 이상이면 그대로, 0.4..0.55 에서는 조금 느려진다).
  // 측정(1배속 화면): 전사 62px/초·키 66px → 달리기 초당 약 3걸음.
  const runSf = (r) => RUN_KIND[r.kind] ? Math.max(0.55, Math.min(1, r.vr == null ? 1 : r.vr)) : 1;
  const strideOf = (u, r, H) => Math.max(5, r.gp.sl * H * Math.max(0.85, Math.min(1.4, Math.pow((u.speed || 25) / 25, 0.75))) * runSf(r));
  // 시트에 그려진 걸음 칸의 한 걸음 거리(화면 px): 시트의 runStride / walkStride(시트 px) × 그리는 배율(sheetK — 우두머리 1.5배). 없으면 0.
  function drawnStrideOf(u, name) {
    const sh = useArt() && Art.sheetFor(u);
    if (!sh || !sh.meta.anims[name]) return 0;
    return (sh.meta[name + 'Stride'] || 0) * sheetK(u, sh);
  }
  // 그려진 달리기 칸(8칸 = 두 걸음: R1 닿음 · R2 디딤 · R3 밀기 · R4 뜸, R5..R8 반대 발)을 간 거리로 넘긴다 (r.rq = 지금 칸 위치 0..8, 소수).
  // 주인 결정(2026-11-26, 그려진 달리기의 발 미끄러짐 — "그대로 둠 (B만)"): 유닛의 빠르기는 그대로 두고 칸의 박자만 고친다.
  //   경량(뜨는 때가 있다, GAIT_CLASS.hop): 디딘 칸 R1·R2(R5·R6)는 칸마다 그려진 보폭의 1/4(ds/4) — 그림 속 디딘 발이 뒤로 가는 만큼이라 발이 땅에 붙는다.
  //     밀기·뜸 R3·R4(R7·R8)가 한 걸음의 나머지를 나눠 맡는다: 칸마다 f = (S − ds/2)/2, 한 걸음 S = max(코드 보폭 × 배속 규칙, ds/2 + 2 × ds/8)
  //     (뜨는 칸도 적어도 ds/8 거리를 맡아 2배속에서도 보인다). 걸음 수 = 빠르기 ÷ S — 그려진 보폭이 코드 보폭보다 길면 그만큼 적게 디딘다.
  //   중량·로브(뜨는 때가 없다 — 늘 한 발이 땅에): 모든 칸이 ds/4 (발이 붙는다; 그 부류의 runStride 는 약 22~24px).
  //   뒤로 가면(r.fwd < 0) 칸 너비를 고르게 (한 걸음 거리 ÷ 4).
  // ds = drawnStrideOf(u, 'run') (화면 px, 배율 포함), slf = 코드 달리기 보폭 strideOf × 배속 규칙(4배속 2).
  // 측정(전사·니클라, ds 45.5px; 디딘 칸이 처음 보일 때의 발바닥 중심, 화면 px): 칸마다 미끄러짐 1배속 0.0/0.0, 2배속 0.0/−0.6, 4배속 −1.8/+0.5
  // (예전 약 −7/−6, −7/−7, −2.8/−2.0). 초당 걸음 1배속 약 1.7(예전 2.9), 2배속 3.1(5.4), 4배속 4.4(그대로). 뜨는 칸은 1배속 60ms 이상, 2배속 대개 40~60ms.
  const RUN_FLY_MIN = 1 / 8;
  function runCells(u, r, dd, ds, slf) {
    if (r.rq == null) r.rq = (r.rp == null ? r.phase : r.rp) * 4;
    // 뜸이 없는 부류(중량·로브): 모든 칸이 ds/4 — 다만 4배속은 걸음 수를 2배속 수준까지만(slf = 보폭×fast 가 더 크면 그만큼 칸을 넓힌다, 그때만 약간 미끄러짐).
    const C = gaitClassFor(u, r, useArt() && Art.sheetFor(u)), c = C.hop ? ds / 4 : Math.max(ds, slf) / 4;
    const f = C.hop ? (Math.max(slf, ds / 2 + 2 * ds * RUN_FLY_MIN) - ds / 2) / 2 : c;
    if (dd < 0) r.rq += dd / (2 * c + 2 * f) * 4;
    else {
      let left = dd;
      for (let g = 0; left > 1e-9 && g < 64; g++) {
        const fl = Math.floor(r.rq), wj = (((fl % 4) + 4) % 4) < 2 ? c : f;
        const room = (fl + 1 - r.rq) * wj;
        if (left < room) { r.rq += left / wj; left = 0; } else { r.rq = fl + 1; left -= room; }
      }
    }
    r.rq = ((r.rq % 8) + 8) % 8;
  }
  // 유닛이 화면에서 실제로 움직인 만큼 걸음을 나아가게 하고(시계가 아니라 거리), 걷는 정도(gait 0..1)를 부드럽게 올리고 내린다.
  // 한두 틱짜리 자리 밀림은 걸음으로 치지 않는다(세 틱 이상 이어져야 걷기 시작) — 난전에서 걸음이 깜빡이지 않게.
  function gaitUpdate(view, st, u, r, H, face) {
    const c = view.clock, bx = u.x * Z, by = u.y * Z;
    const dtc = r.gC == null ? 0 : Math.max(0, Math.min(0.1, c - r.gC));
    r.gC = c; r.sh = H;
    if (r.gx == null) { r.gx = bx; r.gy = by; r.gait = 0; r.wp = r.phase; r.rp = r.phase; r.run = 0; r.moveC = -9; r.dirX = face; r.fwd = 1; r.kind = 'run'; r.gp = { ...GAITS.run }; }
    const dx = bx - r.gx, dy = by - r.gy, d = Math.hypot(dx, dy);
    if (d > 0.05) {
      // 문턱은 연출 시계 기준이라 화면이 느리면(프레임 하나가 길면) 같이 늘린다 — 고정 0.09초면 30fps 아래의 2·4배속에서 걷기가 시작되지 않았다
      r.run = c - r.moveC < Math.max(0.09, dtc * 2.2) ? r.run + 1 : 1;
      if (r.run === 1) r.vr = null;                            // 새로 움직이기 시작: 빠르기 어림을 처음부터
      r.moveC = c; r.gx = bx; r.gy = by;
      if (Math.abs(dx) > 0.3) r.dirX = dx > 0 ? 1 : -1;
      r.fwd = (Math.abs(dx) > Math.abs(dy) * 0.5 && dx * face < 0) ? -1 : 1;   // 보는 쪽과 반대로 가면 뒷걸음 (걸음이 거꾸로 돈다)
      // 실제 빠르기 ÷ 제 빠르기 (전투 시간 기준, 0.15초에 걸쳐 고르게): 달릴 만한 빠르기인지 gaitKind 가 본다
      const dts = st.t - (r.gT == null ? st.t : r.gT);
      if (dts > 0) { const v = d / Z / dts / Math.max(1, u.speed || 25); r.vr = r.vr == null ? v : r.vr + (v - r.vr) * Math.min(1, dts / 0.15); }
      r.kind = gaitKind(st, u, r);
      const fast = view.speedK > 2 ? view.speedK / 2 : 1;      // 4배속: 걸음 수는 2배속 수준까지만
      const dd = Math.min(d, 14) * r.fwd;                      // 돌진처럼 한 틱에 멀리 간 것은 한 걸음 남짓까지만
      const sl = strideOf(u, r, H);
      r.wp += dd / (sl * fast);
      r.walkDist = (r.walkDist || 0) + dd / fast;              // 그려진 걷기 칸이 쓰는 거리 (같은 배속 규칙)
      // 그려진 달리기 칸의 걸음(pose): 시트 보폭(runStride × 배율)이 있으면 칸마다 간 거리로 넘긴다(runCells, r.rq). 없으면 위의 보폭(r.rp).
      const ds = drawnStrideOf(u, 'run');
      if (ds > 0) runCells(u, r, dd, ds, sl * fast);
      else r.rp = (r.rp == null ? r.phase : r.rp) + dd / (sl * fast);
    }
    r.gT = st.t;
    const want = u.alive && r.run >= 3 && c - r.moveC < Math.max(0.11, dtc * 1.5);
    r.gait = want ? Math.min(1, r.gait + dtc / 0.10) : Math.max(0, r.gait - dtc / 0.16);
    const T = GAITS[r.kind] || GAITS.run, a = Math.min(1, dtc / 0.15);
    for (const k in T) r.gp[k] += (T[k] - r.gp[k]) * a;
  }
  // 시트 칸에 얹는 몸 오르내림의 무게(0..1): 공격·피격·준비 칸(fr.act)이 뜨면 BODY_FADE 초에 걸쳐 0으로, 대기 칸으로 돌아오면 같은 시간에 1로. 연출 시계 기준.
  const BODY_FADE = 0.08;
  function bodyW(view, r, act) {
    const c = view.clock, dt = r.bwC == null ? 0 : Math.max(0, Math.min(0.1, c - r.bwC)), want = act ? 0 : 1;
    r.bwC = c;
    r.bw = r.bw == null ? want : want > r.bw ? Math.min(want, r.bw + dt / BODY_FADE) : Math.max(want, r.bw - dt / BODY_FADE);
    return r.bw;
  }
  const isBug = (u) => !!(u.mon && typeof ENEMIES !== 'undefined' && ENEMIES[u.mon] && ENEMIES[u.mon].tpl === 'bug');   // 다족(거미·전갈): 뛰어오르지 않는다
  // ── 이동 부류 (주인 2026-11-26: "달리기(이동)에 대해 3가지 부류를 정하고 싶어. 경량, 중량, 로브") ──
  //   light 경량: 확정 달리기(run_base/v2 — 앞으로 기울고, 뜬 동안 누르고, 받아낸 뒤 조금 오른다)
  //   heavy 중량: 판금·큰 방패·아주 큰 무기 — 뜨는 칸 없이(한 발은 늘 땅) 거의 선 몸으로 무겁게 디디는 달음박질(heavy_base)
  //   robe  로브: 발목까지 오는 긴 옷 — 뜨지 않고 무릎을 크게 들지 않는 종종걸음·미끄러짐, 옷자락이 다리를 가린다(robe_base)
  // 그려진 이동 칸은 부류와 상관없이 시트의 anims.run 하나다 (add_gait --gait run; 덧그리는 마네킹만 부류별) — 엔진의 박자 코드는 그대로 쓴다.
  // 시트의 부류: 시트 meta.gait (add_gait 가 등록할 때 적는다 — 앞으로) → js/gait_classes.js (tools/art/specs/gait_classes.json 에서
  // `python3 tools/art/gait_requests.py --js` 로 만든 표: 시트별, 시트 없는 유닛은 직업·대장 방식·괴물 틀별) → 경량.
  // 그려진 칸이 없는 시트는 그림을 바꾸지 않고 몸 전체 높이만 부류대로 오르내린다(glideBob). 값:
  //   k·min·max 높이(키 비율, px 한계) · lo 가장 낮은 때 · hi 가장 높은 때(걸음 단위, 0 = 앞발이 닿는 순간) · drop 1 = 높은 데서 가속해 떨어지다 툭 멈춘다(무게가 실림)
  //   sl 몸 높이의 한 걸음 거리(키 비율, 0 = 코드 걸음 r.wp 그대로; 달리는 걸음은 코드 걸음처럼 runSf 만큼 줄인다)
  //   hop 뜨는 때가 있는가 (시트 없는 코드 도트가 뜨는 칸에 솟는다 · 그려진 달리기 칸의 뜸 칸이 거리를 맡는다 — runCells) · dust 디딜 때 먼지 톨
  // heavy: 마네킹(heavy_base 초안 v2) 엉덩이 180/173/178/179.5(닿음·내려앉음·지남·밀기) → 디딜 때마다 내려앉는다. 경량 달리기의 느낌을 넘지 않게(검증 지적): 닿는 순간의 높이가 가장 높고
  //        (그 위로 솟지 않는다) 디딘 뒤 1px 만 툭 내려앉았다(0.22, 가속해 떨어지다 멈춤) 천천히 닿는 높이로 돌아온다 — 키와 상관없이 0..1px.
  //        보폭 23.5 게임px(키 66 의 0.356), 칸 101ms.
  // robe:  마네킹(robe_base 초안 v2) 엉덩이 182/180.5/185/185.5, 출렁임 작다 → 0..1px 부드럽게. 보폭 22.2 게임px(0.34), 칸 96ms.
  const GAIT_CLASS = {
    light: { k: 0.02, min: 1, max: 2, lo: 0.12, hi: 0.55, drop: 0, sl: 0, hop: 1, dust: 1 },
    heavy: { k: 0.02, min: 1, max: 1, lo: 0.22, hi: 1, drop: 1, sl: 0.356, hop: 0, dust: 2 },
    robe:  { k: 0.015, min: 0, max: 1, lo: 0.25, hi: 0.7, drop: 0, sl: 0.34, hop: 0, dust: 1 },
  };
  // 유닛의 이동 부류 (시트가 있으면 그 시트의 것 — 상위 직업이 기본 직업 시트를 빌려 쓰면 그 시트의 부류). 표에 없으면 경량.
  function gaitClassOf(u, sh) {
    if (sh && GAIT_CLASS[sh.meta.gait]) return sh.meta.gait;
    const T = typeof GAIT_CLASSES !== 'undefined' ? GAIT_CLASSES : null;
    if (!T) return 'light';
    const S = T.sheets, lk = u.look || {};
    if (sh && S[sh.id]) return S[sh.id];
    // 시트가 없거나(코드 생성 도트) 표에 아직 없는 시트: 시트를 고르는 순서(Art.sheetFor)대로 표를 본다
    const ids = [u.art && u.art.startsWith('portrait/') ? 'sheet/' + u.art.slice(9) : null, u.mon ? 'sheet/monster/' + u.mon : null,
      u.capKey ? 'sheet/captain/' + u.capKey : null, u.heroKey ? 'sheet/hero/' + u.heroKey : null, lk.cap ? 'sheet/captain/' + lk.cap : null,
      T.hero_class_to_sheet[u.cls] || null];
    for (const id of ids) if (id && S[id]) return S[id];
    if (u.mon) { const e = typeof ENEMIES !== 'undefined' && ENEMIES[u.mon]; return T.enemy_override[u.mon] || (e && T.enemy_tpl[e.tpl]) || 'light'; }
    const ck = u.capKey || lk.cap;
    if (ck && typeof CAPTAIN_CLASSES !== 'undefined' && CAPTAIN_CLASSES[ck]) return T.captain_style[CAPTAIN_CLASSES[ck].style] || 'light';
    for (const k of [lk.master, lk.adv, u.cls, lk.cls]) { const c = k && (T.master[k] || T.adv[k] || T.base[k]); if (c) return c; }
    return 'light';
  }
  // 부류 값 (유닛마다 한 번, 시트가 바뀌면 — 불러오기가 끝나면 — 다시). 부류가 없는 것(none: 네발·다족·떠 있는 몸)은 경량 값.
  function gaitClassFor(u, r, sh) {
    const key = sh ? sh.id : '-';
    if (r.gcKey !== key) { r.gcKey = key; r.gcls = gaitClassOf(u, sh); }
    return GAIT_CLASS[r.gcls] || GAIT_CLASS.light;
  }
  // 걸음 칸이 그려지지 않은 시트의 몸 높이(화면 px, 0 이상 — 발이 땅 아래로 들어가지 않는다).
  // 주인 결정(2026-11-26): 서 있는 그림을 잘라·기울여·꺾어 달리게 하면 찌그러져 보인다 — 달리기·걷기는 뼈대·마네킹 위에 덧그린 칸(시트의 run·walk)이 맡는다.
  // 그 칸이 없는 시트는 그림을 전혀 바꾸지 않고(다리 가르기·기울이기·무릎 꺾기·윗몸 숙이기 없음) 대기 자세 그대로 미끄러지며, 몸 전체만 1px 남짓 오르내린다.
  //   달리기(duty < 1): 주인 박자 — 디딘 직후(받아낸 순간, 걸음의 0.12)에 가장 낮고, 밀어내기 전 디딘 동안(0.55)에 가장 높다. 뜬 동안은 그대로 조금씩 내려온다(살짝 뜬 느낌만).
  //   걷기(duty 1): 디딜 때 낮고 디딘 다리 위에서 높다. 다족(거미·전갈)은 오르내리지 않는다.
  //   높이: 키의 2%(1..2px). 키 66px 전사는 0 또는 1px, 1.5배 우두머리는 0..2px.
  //   이동 부류(C = GAIT_CLASS)마다 높이·때가 다르다: 경량은 위 그대로, 중량은 디딜 때마다 툭 내려앉고(1..2px) 천천히 올라오며, 로브는 0..1px 부드럽게.
  function glideBob(P, H, g, p, d, C) {
    if (!(g > 0)) return 0;
    C = C || GAIT_CLASS.light;
    const runK = Math.max(0, Math.min(1, (1 - d) / 0.3));     // 달리는 정도 (걸음 종류가 섞이는 동안 0..1)
    const A = Math.max(C.min, Math.min(C.max, C.k * H)), Aw = Math.min(A, P.wbob * H);
    const LO = C.lo, HI = C.hi, s = (((p - LO) % 1) + 1) % 1, up = HI - LO, t = (s - up) / (1 - up);
    // 달리기 0..1 (LO 에서 0, HI 에서 1). 내려오기: 부드럽게(cos) 또는 drop — 가속해 떨어지다 가장 낮은 데서 툭 멈춘다
    const xr = s < up ? (1 - Math.cos(Math.PI * s / up)) / 2 : C.drop ? 1 - t * t : (1 + Math.cos(Math.PI * t)) / 2;
    const xw = (1 - Math.cos(2 * Math.PI * p)) / 2;                                                           // 걷기 0..1
    return Math.max(0, Math.round(g * (runK * A * xr + (1 - runK) * Aw * xw)));
  }
  // 움직이는 유닛의 그리기 변형 (blit 의 tf: { bob } — 그림자·발 디딤은 땅에 둔 채 몸 전체만 올린다).
  // 시트: 그림은 그대로 두고 몸 높이(glideBob)와 발 디딤 먼지만. 그려진 걸음 칸이 있으면 그 칸에 몸 움직임이 그려져 있으므로 얹지 않는다.
  // 떠 있는 몸(hover 시트): 천천히 떠오르내린다(모든 칸에, 기울이지 않는다).
  // 시트가 없는 코드 생성 도트: 다리는 두 칸 그림이 맡고(걸음에 맞춰 바뀐다 — pose), 달릴 때 두 발이 다 뜨는 구간에만 몸이 통째로 떠오른다.
  function walkTf(view, st, u, r, fr, S, X, Y) {
    const gt = gaitType(u, fr), P = r.gp;
    const dir = r.dirX || 1;
    if (gt === 'hover') {
      if (!fr.sheet) return null;
      const ic = view.idleClock != null ? view.idleClock : view.clock;
      return { bob: Math.round(1.5 + 1.5 * Math.sin((ic + r.phase) * 2 * Math.PI / 1.1)) };
    }
    const H = S.h, quad = gt === 'quad', spider = isBug(u);
    // 이동 부류(두 발 짐승만): 경량은 코드 걸음(r.wp) 그대로, 중량·로브는 몸 높이의 걸음을 간 거리 ÷ 부류의 한 걸음(키 × C.sl × 빠르기 × runSf)으로 센다
    // (걸음 수가 경량보다 적다 — 마네킹 박자; 느리게 다가가면 경량처럼 보폭이 줄어 초당 걸음 수가 그대로). 한 걸음 거리가 runSf 로 바뀌므로 걸음은 쌓아 센다(r.cwq).
    // 그려진 달리기 칸의 박자(r.rq)와는 상관없다: 그 칸이 있으면 몸 높이를 얹지 않는다.
    const C = gt === 'biped' ? gaitClassFor(u, r, fr.sheet) : GAIT_CLASS.light;
    let wq = r.wp;
    if (C.sl > 0) {
      const wd = r.walkDist || 0, csl = Math.max(5, C.sl * H * Math.max(0.85, Math.min(1.4, Math.pow((u.speed || 25) / 25, 0.75))) * runSf(r));
      if (r.cwq == null) r.cwq = wd / csl + r.phase;
      else r.cwq += (wd - r.cwD) / csl;
      r.cwD = wd; wq = r.cwq;
    }
    const p = ((wq % 1) + 1) % 1;
    const d = Math.max(0.4, Math.min(1, P.duty));
    if (!fr.sheet) {
      // 다족(bug: 거미·전갈)은 뛰어오르지 않고, 네발 짐승(beast)은 반만. 중량·로브는 뜨는 칸이 없다 (코드 도트의 다리 두 칸은 그대로).
      if (!C.hop || !((r.gait || 0) > 0) || d >= 1 || p < d || spider) return null;
      const e = u.mon && typeof ENEMIES !== 'undefined' && ENEMIES[u.mon];
      const hop = Math.round(P.air * H * r.gait * (e && e.tpl === 'beast' ? 0.5 : 1) * Math.sin(Math.PI * (p - d) / (1 - d)));
      return hop > 0 ? { bob: hop } : null;
    }
    const w = bodyW(view, r, fr.act), g = (r.gait || 0) * w;
    if (!fr.walkFx) {
      // 공격·피격·준비 칸: 걷던 몸 높이가 BODY_FADE 에 걸쳐 0으로 내려온다. 그려진 걸음 칸을 쓰는 시트(지금 걸음 종류의 run·walk 칸)는 얹지 않는다.
      if (!fr.act || !(g > 0) || gaitAnimOf(fr.sheet.meta, r.kind)) return null;
      r.stepI = Math.floor(wq);                                 // 돌아왔을 때 먼지가 한꺼번에 나지 않게
      const b = spider ? 0 : glideBob(P, H, g, p, d, C);
      return b ? { bob: b } : null;
    }
    // 발이 땅에 닿는 순간의 먼지: 달려들 때·도주·큰 괴물은 크게, 보통 달리기는 한 톨 (걷는 걸음은 없음). 달리는 네발 짐승은 두 걸음에 한 번(한 도약).
    const runK = Math.max(0, Math.min(1, (1 - d) / 0.3));
    // 중량은 디딜 때마다 무게가 실려 두 톨 (C.dust)
    const stepI = Math.floor(wq);
    if (r.stepI != null && stepI !== r.stepI && g > 0.6 && !(quad && !spider && runK > 0.5 && (stepI & 1))) {
      const big = u.bigMon || u.boss, hard = r.kind === 'charge' || r.kind === 'flee';
      if (big || hard) spawn(view, big ? 4 : 2, X - dir * 5, Y - 1, { sp: [6, 20], life: [0.18, 0.32], color: '#a89a80', size: 2, add: false, rise: -8 });
      else if (r.kind === 'run') spawn(view, C.dust, X - dir * 4, Y - 1, { sp: [4, 12], life: [0.12, 0.2], color: '#a89a80', size: 2, add: false, rise: -6 });
    }
    r.stepI = stepI;
    const b = spider ? 0 : glideBob(P, H, g, p, d, C);
    return b ? { bob: b } : null;
  }
  // 공격할 때 몸이 앞뒤로 움직이는 정도(px): 준비 때 살짝 뒤로, 타격 칸이 뜨는 순간 앞으로 뻗고 천천히 돌아온다
  function lungeOf(view, u, r, fr) {
    const c = view.clock;
    let o = 0;
    if (r.atkMelee && r.strikeAt != null) {
      const t = c - r.strikeAt, K = 10 * Math.min(1.5, fr.k || 1);
      if (t >= 0 && t < 0.26) o = (t < 0.04 ? t / 0.04 : t < 0.11 ? 1 : 1 - (t - 0.11) / 0.15) * K;
      else if (t < 0 && c >= r.atkAt) o = -3 * Math.min(1, (c - r.atkAt) / 0.1);
    }
    if (!o && r.windAt != null && c - r.windAt < 0.1) o = -3 * Math.min(1, (c - (r.windStart || c)) / 0.12);
    return o;
  }
  // 곧 기본 공격이 나갈 것 같은가 (연출용 짐작: 틀리면 준비 자세를 풀고 만다 — 속임 동작처럼 보인다)
  function aboutToStrike(st, u, r) {
    const b = u.skills && u.skills[0];
    if (!b || !u.alive || u.healer || u.g.routed || u.stunUntil > st.t) return false;
    // 걸어가는 중에는 짐작하지 않는다 — 단, 맞붙은 채 자리를 고치는 잔걸음(reseat)은 싸우는 중이므로 예외
    if (!(b.left > 0 && b.left <= 0.2) || ((r.gait || 0) > 0.3 && r.kind !== 'reseat')) return false;
    // 전투 계산이 쓰는 것과 같은 표적·거리로 본다 (근접은 세로 차이를 덜 세는 meleeDist: 비스듬히 붙은 자리에서도 맞는다)
    const tg = u.target;
    if (!tg || !tg.alive || tg.fled || tg.side === u.side) return false;
    return (b.shot ? dist(tg, u) : meleeDist(u, tg)) <= b.range + sizeOf(tg) + (b.shot ? 0 : BODY) + 2;
  }

  // 애니메이션 안의 몇 번째 칸인가 (ms: 애니 시작부터 흐른 시간)
  function frameAt(a, ms, once) {
    let t = once ? Math.min(a.total - 1, Math.max(0, ms)) : ((ms % a.total) + a.total) % a.total;
    for (let j = 0; j < a.ms.length; j++) {
      if (t < a.ms[j]) return a.from + j;
      t -= a.ms[j];
    }
    return a.to;
  }

  // 괴물 시트: 우두머리(같은 종의 부하보다 큰 scale)는 시트 칸을 1.5배로 키워 그린다 (코드 생성 도트의 5배 대 3배와 같은 구별).
  // 칸 크기(80·96·112)와 상관없이 같은 배율 — 부하는 같은 시트를 1배로 그리므로 우두머리가 늘 1.5배 크다.
  // (직업·대장 시트는 괴물이 아니라 해당 없음)
  function sheetK(u, sh) {
    if (!u.mon || !(u.scale > 1) || !sh.id.startsWith('sheet/monster/')) return 1;
    const d = (typeof ENEMIES !== 'undefined' && ENEMIES[u.mon]) || {};
    return u.scale > (d.boss ? 3 : d.big ? 2 : 1) ? 1.5 : 1;
  }

  // 직업 시트(sheet/class/*)를 진영 색으로 바꿔 칠한 사본. 시트의 열쇠 색(meta.tint.outfit/accent)을
  // look.tint 색으로 옮기되, 열쇠 색끼리의 밝기 비(명암 단계)는 그대로 둔다 (toneRamp). (시트·색 조합마다 한 번만 만든다)
  const recolorCache = new Map();
  const hexRgb = (h) => { const n = parseInt(String(h).replace('#', '').slice(0, 6), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const lumOf = (c) => 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2];
  // 병사가 입을 제복 색: 세력 병사는 look.tint, 제복 색이 없는 병사(우리 길드의 일반 단원 등)는 소속 용병단 색을 입힌다.
  // 장식 색은 놋쇠색 — 용병단 색이 이미 금빛·주황이면 묻히지 않게 은색. 용병단 색도 없으면 무난한 회갈색 제복.
  const NEUTRAL_OUTFIT = '#5f5a52', BRASS = '#d9a441', SILVER = '#c3c7cf';
  const uniformCache = new Map();
  function tintOf(u) {
    const lt = u.look && u.look.tint;
    if (lt) return lt;
    const outfit = (u.g && /^#[0-9a-f]{6}$/i.test(u.g.color || '') && u.g.color) || NEUTRAL_OUTFIT;
    let t = uniformCache.get(outfit);
    if (!t) {
      const [r, g, b] = hexRgb(outfit), mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      let hue = 0;
      if (mx !== mn) hue = mx === r ? (60 * (g - b) / (mx - mn) + 360) % 360 : mx === g ? 60 * (b - r) / (mx - mn) + 120 : 60 * (r - g) / (mx - mn) + 240;
      const warm = mx - mn > 50 && hue >= 20 && hue <= 70;
      t = { outfit, accent: warm ? SILVER : BRASS };
      uniformCache.set(outfit, t);
    }
    return t;
  }
  // 열쇠 색 단계(명암) → 진영 색 단계. 진영 색의 밝기를 역할별 기준 밝기로 누르고(무릎 knee 위는 slope 만큼만 밝아진다, 아주 어두운 색은
  // floor 까지 올린다) 그 밝기에 열쇠 색끼리의 밝기 비(명암 대비)를 곱한다. 밝은 단계는 TONE_HI 위에서 TONE_MAX 로 부드럽게 눌러
  // (순서·간격은 남기고) 255 를 넘는 채널은 자르지 않고 같은 밝기의 회색 쪽으로 채도를 줄여 넣는다 — 예전처럼 곱한 뒤 자르면 밝은 두 단계가
  // 같은 노랑으로 뭉개졌다 (금빛 용병단 #c58f1e, 자유도시 장식 #f2c94c). 채도도 TONE_CHROMA 까지.
  // 장식(accent)은 얼굴 가리개(궁수 복면·도적 두건)에도 쓰이므로 무릎을 더 낮게: 밝은 장식 색이 얼굴을 노란 덩어리로 만들지 않게.
  // tools/art/sheets.py tone_ramp 와 같은 규칙.
  const TONE = { outfit: { floor: 50, knee: 130, slope: 0.5 }, accent: { floor: 64, knee: 100, slope: 0.4 } };
  const TONE_HI = 170, TONE_MAX = 240, TONE_CHROMA = 150;
  function toneRamp(list, target, role) {
    const t = TONE[role] || TONE.outfit;
    const lt = lumOf(target);
    const base = lt > t.knee ? t.knee + (lt - t.knee) * t.slope : Math.max(lt, t.floor);
    const mean = list.reduce((a, k) => a + lumOf(k), 0) / list.length || 1;
    return list.map((k) => {
      let want = base * lumOf(k) / mean;
      if (want > TONE_HI) want = TONE_MAX - (TONE_MAX - TONE_HI) * Math.exp(-(want - TONE_HI) / (TONE_MAX - TONE_HI));
      let c = lt > 1 ? target.map((v) => v * want / lt) : [want, want, want];
      const mx = Math.max(...c), mn = Math.min(...c);
      let f = mx - mn > TONE_CHROMA ? TONE_CHROMA / (mx - mn) : 1;          // 채도 한도
      if (mx > 255) f = Math.min(f, (255 - want) / Math.max(1e-6, mx - want)); // 색 영역 안으로 (밝기 유지)
      if (f < 1) c = c.map((v) => want + (v - want) * Math.max(0, f));
      return c.map((v) => Math.max(0, Math.min(255, Math.round(v))));
    });
  }
  function sheetRecolor(sh, u) {
    const keys = sh.meta.tint;
    if (!keys || !sh.id.startsWith('sheet/class/')) return null;
    const lt = tintOf(u);
    const ck = `${sh.id}|${lt.outfit || ''}|${lt.accent || ''}`;
    if (recolorCache.has(ck)) return recolorCache.get(ck);
    let out = null;
    try {
      const W0 = sh.img.naturalWidth || sh.img.width, H0 = sh.img.naturalHeight || sh.img.height;
      const c = document.createElement('canvas');
      c.width = W0; c.height = H0;
      const x = c.getContext('2d');
      x.drawImage(sh.img, 0, 0);
      const id = x.getImageData(0, 0, W0, H0), d = id.data;
      const map = new Map();
      ['outfit', 'accent'].forEach((role) => {
        const list = (keys[role] || []).map(hexRgb);
        if (!list.length || !lt[role]) return;
        const ramp = toneRamp(list, hexRgb(lt[role]), role);
        list.forEach((k, j) => map.set((k[0] << 16) | (k[1] << 8) | k[2], ramp[j]));
      });
      for (let i = 0; i < d.length; i += 4) {
        if (!d[i + 3]) continue;
        const to = map.get((d[i] << 16) | (d[i + 1] << 8) | d[i + 2]);
        if (to) { d[i] = to[0]; d[i + 1] = to[1]; d[i + 2] = to[2]; }
      }
      x.putImageData(id, 0, 0);
      out = { img: c, key: ck };
    } catch (e) { out = null; /* 픽셀을 읽을 수 없으면 원본 그대로 */ }
    if (recolorCache.size > 64) recolorCache.clear();
    recolorCache.set(ck, out);
    return out;
  }

  // 지금 걸음에 쓸 그려진 동작: 달리는 걸음(run·charge·flee)은 시트의 run, 걷는 걸음(trudge·back·step)은 walk.
  // 맞붙은 채 잔걸음(reseat)에는 쓰지 않는다 (대기↔동작 칸의 키·자세 차이로 튄다). 없으면 null → 대기 칸 그대로 미끄러지며 몸 높이만(walkTf).
  function gaitAnimOf(m, kind) {
    if (kind === 'reseat') return null;
    const name = RUN_KIND[kind] ? 'run' : 'walk';
    return m.anims[name] ? name : null;
  }

  // 지금 그릴 칸
  function pose(view, u, force) {
    const r = rsOf(view, u), c = view.clock;
    const sh = useArt() && Art.sheetFor(u);
    if (sh) {
      const m = sh.meta;
      let i, ga, walkFx = false, act = null; // walkFx: 지금 걸음에 쓸 동작 칸이 없는 시트가 움직이는 중 → 그릴 때 몸 높이(walkTf: 그림은 그대로)만 얹는다
      // act: 공격·피격·준비 칸 — 걷던 몸이면 walkTf 가 몸 높이를 BODY_FADE 에 걸쳐 푼다
      if (force) { const a = force === 'walk' && m.anims.run ? m.anims.run : Art.anim(m, force); i = Math.min(a.to, a.from + 1); }   // 돌진 잔상('walk')은 달리기 칸이 있으면 그것으로
      else if (!u.alive) i = Art.anim(m, 'hit').to;
      else if (c - r.atkAt < r.atkDur) { const a = Art.anim(m, r.atkAnim); i = frameAt(a, ((c - r.atkAt) / r.atkDur) * a.total, true); act = 'atk'; }
      else if (c - r.hitAt < 0.22) { const a = Art.anim(m, 'hit'); i = frameAt(a, ((c - r.hitAt) / 0.22) * a.total, true); act = 'hit'; }
      else if (c - (r.windAt == null ? -9 : r.windAt) < 0.1) { i = Art.anim(m, 'attack').from; act = 'wind'; }   // 곧 칠 것이 보일 때: 준비 자세 먼저 (연출만)
      else if (r.gait > 0.05 && (ga = gaitAnimOf(m, r.kind))) {
        // 달리기·걷기 동작이 그려진 시트: 프레임을 걸음에 묶는다 (n 프레임 = 두 걸음).
        const a = m.anims[ga], n = a.to - a.from + 1;
        let q;
        if (ga === 'run') {
          // 달리기 칸: 시트 보폭(runStride)이 있으면 gaitUpdate 의 r.rq (runCells — 디딘 칸은 그려진 보폭대로 넘겨 발이 땅에 붙고, 뜨는 칸이 나머지 거리를 맡는다).
          // 시트 보폭이 없으면 r.rp (한 걸음 = 코드 달리기 보폭 strideOf, 4배속 규칙도 같다).
          q = m.runStride > 0 && r.rq != null ? r.rq * n / 8 : (r.rp == null ? r.phase : r.rp) * n / 2;
        } else {
          // 걷기 칸: 간 거리 ÷ (walkStride × 그리는 배율), 없으면 키에서 어림한다 (28.5%; r.sh 는 이미 배율을 곱한 키)
          const k = sheetK(u, sh), hh = r.sh || m.cell[1] * 0.7 * k;
          const sl = Math.max(2, (m.walkStride || 0) * k || hh * 0.285);
          q = ((r.walkDist || 0) / sl + r.phase) * n / 2;
        }
        i = a.from + ((Math.floor(q) % n) + n) % n;
      } else {
        // 숨쉬기는 실제 시간으로 (배속에 헐떡이지 않게). 걷는 중이면 그릴 때 몸 높이만 얹는다(그림은 그대로)
        i = frameAt(Art.anim(m, 'idle'), ((view.idleClock != null ? view.idleClock : c) + r.phase) * 1000, false);
        walkFx = r.gait > 0.05;
      }
      const f = m.frames[i] || m.frames[0];
      const rc = sheetRecolor(sh, u);
      return { img: rc ? rc.img : sh.img, sx: f[0], sy: f[1], sw: m.cell[0], sh: m.cell[1], ax: m.anchor[0], ay: m.anchor[1], face: m.facing,
        key: `${rc ? rc.key : sh.id}#${i}`, sheet: sh, k: sheetK(u, sh), walkFx, act };
    }
    const walking = (u.moving && u.alive) || force === 'walk';
    const t = (c + r.phase) * 1000;
    // 걷는 두 칸은 걸음(간 거리)에 맞춰 바꾼다 — 걸음이 켜지기 전·강제 자세에서는 전처럼 시계로
    const stepF = !force && r.gait > 0.05 ? Math.floor(r.wp) & 1 : -1;
    if (u.mon) {
      const s = monScale(u);
      const frame = walking ? (stepF >= 0 ? stepF : Math.floor(t / 180) % 2) : Math.floor(t / 420) % 2;
      const img = Sprites.monster(u.mon, s, frame, false);
      // 괴물 도안은 대부분 왼쪽을 본다
      return { img, sx: 0, sy: 0, sw: img.width, sh: img.height, ax: Math.round(img.width / 2), ay: 16 * s, face: -1, key: keyOfCanvas(img), unit: s };
    }
    const frame = walking ? ((stepF >= 0 ? stepF : Math.floor(t / 160) % 2) ? 2 : 0) : Math.floor(t / 450) % 2;
    const img = Sprites.merc(u.look, SPR, frame, false);
    return { img, sx: 0, sy: 0, sw: img.width, sh: img.height, ax: 8 * SPR, ay: 15 * SPR, face: 1, key: keyOfCanvas(img), unit: SPR };
  }

  // 한 칸 그리기: (X, Y) 가 발 위치, flip 이면 좌우 반전
  // fr.k: 그리는 배율 (괴물 우두머리 시트 1.5 등, 기본 1)
  // tf: 걸음 변형 { bob: 몸 높이(px) } — 그림은 그대로, 그림자·발 디딤은 땅에 둔 채 몸 전체만 올린다 (walkTf)
  function blit(ctx, fr, X, Y, flip, img, tf) {
    const src = img || fr.img, sx = img ? 0 : fr.sx, sy = img ? 0 : fr.sy;
    const k = fr.k || 1, dw = Math.round(fr.sw * k), dh = Math.round(fr.sh * k), ax = Math.round(fr.ax * k), ay = Math.round(fr.ay * k);
    if (tf && tf.bob) Y -= tf.bob;
    if (!flip) { ctx.drawImage(src, sx, sy, fr.sw, fr.sh, Math.round(X) - ax, Math.round(Y) - ay, dw, dh); return; }
    ctx.save();
    ctx.translate(Math.round(X), 0);
    ctx.scale(-1, 1);
    ctx.drawImage(src, sx, sy, fr.sw, fr.sh, -ax, Math.round(Y) - ay, dw, dh);
    ctx.restore();
  }

  // 한 칸을 단색 실루엣으로 (맞았을 때 번쩍임 등)
  const tintCache = new Map();
  function tinted(fr, color) {
    const key = `${fr.key}|${color}`;
    let c = tintCache.get(key);
    if (c) return c;
    c = document.createElement('canvas');
    c.width = fr.sw; c.height = fr.sh;
    const x = c.getContext('2d');
    x.drawImage(fr.img, fr.sx, fr.sy, fr.sw, fr.sh, 0, 0, fr.sw, fr.sh);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = color; x.fillRect(0, 0, fr.sw, fr.sh);
    if (tintCache.size > 600) tintCache.clear();
    tintCache.set(key, c);
    return c;
  }

  // 한 칸의 1px 테두리 (실루엣을 밀어 그린 뒤 원래 실루엣을 지운다). 칸마다 한 번만 만든다.
  //  mode 'ring': 사방 외곽선, 'tl': 그림 좌표의 왼쪽·위 가장자리만 (빛 받는 쪽 테두리), 'tr': 오른쪽·위 (좌우 반전해 그릴 때)
  const edgeCache = new Map();
  const EDGE_OFF = { ring: [[1, 0], [-1, 0], [0, 1], [0, -1]], tl: [[-1, 0], [0, -1], [-1, -1]], tr: [[1, 0], [0, -1], [1, -1]] };
  function edgeOf(fr, color, mode) {
    const key = `${fr.key}|${color}|${mode}`;
    let c = edgeCache.get(key);
    if (c) return c;
    const sil = tinted(fr, color);
    c = document.createElement('canvas');
    c.width = fr.sw; c.height = fr.sh;
    const x = c.getContext('2d');
    EDGE_OFF[mode].forEach(([dx, dy]) => x.drawImage(sil, dx, dy));
    x.globalCompositeOperation = 'destination-out';
    x.drawImage(sil, 0, 0);
    if (edgeCache.size > 600) edgeCache.clear();
    edgeCache.set(key, c);
    return c;
  }

  // 시트 인물의 테두리: 어두운 땅(화산·늪 등)에서는 빛 받는 쪽(화면 왼쪽 위)에 밝은 테두리, 밝은 땅에서는 옅은 어두운 외곽선.
  // 어두운 갑옷의 대장이 어두운 땅에 묻히지 않게 한다. 사방 외곽선은 아주 옅게 (2배로 키운 화면에서 스티커처럼 떠 보이지 않게),
  // 빛 받는 쪽 테두리가 주로 윤곽을 살린다.
  // 인물과 땅의 밝기 차이가 RIM_LOW 보다 작으면(회색·짙은 보라 제복이 어두운 화산 땅에, 모래색 도적이 사막에) 그만큼 테두리를 진하게:
  // low 0(차이 충분) ~ 1(같은 밝기). 인물 밝기 = 지금 칸(바꿔 칠한 제복 포함)의 불투명 픽셀 평균 (opaqueBox 가 칸마다 한 번 잰다).
  const RIM_LOW = 32;
  function rimLow(view, fr) {
    const lum = opaqueBox(fr).lum;
    if (lum == null) return 0;
    return Math.max(0, Math.min(1, (RIM_LOW - Math.abs(lum - view.groundLum)) / RIM_LOW));
  }
  function drawRim(ctx, view, fr, X, Y, flip, tf) {
    if (!fr.sheet) return;
    const low = rimLow(view, fr);
    if (view.groundLum < 95) {
      ctx.globalAlpha = 0.5 + 0.35 * low;
      blit(ctx, fr, X, Y, flip, edgeOf(fr, '#ffe8c8', flip ? 'tr' : 'tl'), tf);
      ctx.globalAlpha = 0.12 + 0.2 * low;
      blit(ctx, fr, X, Y, flip, edgeOf(fr, '#ffe8c8', 'ring'), tf);
    } else {
      ctx.globalAlpha = 0.3 + 0.3 * low;
      blit(ctx, fr, X, Y, flip, edgeOf(fr, '#120a16', 'ring'), tf);
    }
    ctx.globalAlpha = 1;
  }

  // 그림이 실제로 차지하는 영역 (투명 여백 제외)과 평균 밝기
  const boxCache = new Map();
  function opaqueBox(fr) {
    let b = boxCache.get(fr.key);
    if (b) return b;
    b = { top: 0, bottom: fr.sh, left: 0, right: fr.sw };
    try {
      const c = document.createElement('canvas');
      c.width = fr.sw; c.height = fr.sh;
      const x = c.getContext('2d');
      x.drawImage(fr.img, fr.sx, fr.sy, fr.sw, fr.sh, 0, 0, fr.sw, fr.sh);
      const d = x.getImageData(0, 0, fr.sw, fr.sh).data;
      let t = fr.sh, bo = -1, l = fr.sw, ri = -1, ls = 0, n = 0;
      for (let y = 0; y < fr.sh; y++) for (let xx = 0; xx < fr.sw; xx++) {
        const i = (y * fr.sw + xx) * 4;
        if (d[i + 3] < 40) continue;
        if (y < t) t = y; if (y > bo) bo = y; if (xx < l) l = xx; if (xx > ri) ri = xx;
        ls += 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]; n++;
      }
      if (bo >= 0) b = { top: t, bottom: bo + 1, left: l, right: ri + 1, lum: ls / n };  // lum: 불투명 픽셀 평균 밝기 (drawRim)
    } catch (e) { /* 읽을 수 없는 그림이면 칸 전체로 */ }
    boxCache.set(fr.key, b);
    return b;
  }

  // 눈에 잘 보여야 하는 인물: 아군 부대장(대장)과 직속 단원(특별 용병)
  const keepVisible = (u) => (u.captain && u.side === 0) || !!u.unique;

  // 유닛의 키·너비 (발에서 머리 꼭대기까지): 체력바·이름표·깃발 위치에 쓴다. 기본 서 있는 칸 기준이라 흔들리지 않는다.
  function stature(view, u) {
    const r = rsOf(view, u);
    const sh = useArt() && Art.sheetFor(u);
    const key = sh ? sh.id : 'proc';
    if (r.statKey === key && r.stat) return r.stat;
    let fr, k = 1;
    if (sh) {
      const m = sh.meta, i = Art.anim(m, 'idle').from, f = m.frames[i] || m.frames[0];
      fr = { img: sh.img, sx: f[0], sy: f[1], sw: m.cell[0], sh: m.cell[1], ax: m.anchor[0], ay: m.anchor[1], key: `${sh.id}#${i}` };
      k = sheetK(u, sh);
    } else {
      const s = u.mon ? monScale(u) : SPR;
      const img = u.mon ? Sprites.monster(u.mon, s, 0, false) : Sprites.merc(u.look, SPR, 0, false);
      fr = { img, sx: 0, sy: 0, sw: img.width, sh: img.height, ax: u.mon ? Math.round(img.width / 2) : 8 * SPR, ay: u.mon ? 16 * s : 15 * SPR, key: keyOfCanvas(img) };
    }
    const b = opaqueBox(fr);
    r.stat = { h: Math.max(12, (fr.ay - b.top) * k), w: Math.max(10, (b.right - b.left) * k), cx: ((b.left + b.right) / 2 - fr.ax) * k };
    r.statKey = key;
    return r.stat;
  }

  // 그림이 차지하는 가로 폭 (앵커 기준 왼쪽 l·오른쪽 r, 그리는 px): 시트는 모든 칸(공격·피격 포함)을 합친 폭이라
  // 동작이 바뀌어도 변하지 않는다. 코드 생성 도트는 지금 칸.
  const spanCache = new Map();
  function spanOf(fr) {
    const k = fr.k || 1;
    if (!fr.sheet) { const b = opaqueBox(fr); return { l: (fr.ax - b.left) * k, r: (b.right - fr.ax) * k }; }
    const sh = fr.sheet, ck = `${sh.id}|${k}`;
    let sp = spanCache.get(ck);
    if (sp) return sp;
    const m = sh.meta;
    let l = 0, r = 0;
    m.frames.forEach((f, i) => {
      const b = opaqueBox({ img: sh.img, sx: f[0], sy: f[1], sw: m.cell[0], sh: m.cell[1], key: `${sh.id}#${i}` });
      l = Math.max(l, m.anchor[0] - b.left); r = Math.max(r, b.right - m.anchor[0]);
    });
    sp = { l: l * k, r: r * k };
    spanCache.set(ck, sp);
    return sp;
  }

  // 화면에 그릴 발 x (px): 그림 전체가 640px 화면 안에 들도록 안쪽으로 당긴다 (시뮬레이션 위치는 그대로).
  // 넓은 괴물(날개 편 하피·가고일)이 가장자리에서 잘리지 않게. 당기는 양은 r.edx 에 두고, 더 당겨야 할 때는 바로,
  // 풀어 줄 때(패주해 화면 밖으로 달아날 때 등)는 서서히 (초당 120px) — 그림이 튀지 않게.
  const SCREEN_PAD = 2;
  function screenX(view, u, fr, flip, lunge = 0) {
    const r = rsOf(view, u), X = u.x * Z + lunge;
    let want = 0;
    if (!u.g.routed) {
      const sp = spanOf(fr), left = flip ? sp.r : sp.l, right = flip ? sp.l : sp.r;
      if (left + right < CW - 2 * SCREEN_PAD) want = Math.max(SCREEN_PAD + left - X, Math.min(0, CW - SCREEN_PAD - right - X));
    }
    const cur = r.edx || 0, dt = Math.max(0, view.clock - (r.edxAt == null ? view.clock : r.edxAt));
    r.edxAt = view.clock;
    if ((want > 0 && want >= cur) || (want < 0 && want <= cur)) r.edx = want;
    else r.edx = cur + Math.max(-120 * dt, Math.min(120 * dt, want - cur));
    return X + r.edx;   // (lunge 포함: 앞으로 내딛는 몸도 화면 밖으로 나가지 않게)
  }
  // 체력바·글자처럼 유닛을 따라가는 것의 x 보정 (지난 그리기의 당김)
  const edxOf = (view, u) => (u && view.rs.has(u) ? view.rs.get(u).edx || 0 : 0);

  // 효과가 가리키는 유닛 찾기 (x, y 는 논리 좌표의 발 위치)
  function nearestUnit(st, x, y, pred) {
    let best = null, bd = 10;
    for (const u of st.units) {
      if (pred && !pred(u)) continue;
      const d = Math.abs(u.x - x) + Math.abs(u.y - y);
      if (d < bd) { bd = d; best = u; }
    }
    return best;
  }

  // 렌더러 상태: 입자, 화면 흔들림, 타격 멈춤
  function makeView(terrain) {
    const bg = background(terrain);
    return { bg, fg: foreground(terrain), parts: [], sparks: [], flares: [], puffs: [], downSeen: new Set(), sigils: [], slashes: [], vfx: [], amb: [], terrain, shake: 0, stop: 0, flash: 0, flashColor: '#ffffff',
      clock: 0, rs: new Map(), groundLum: groundLum(bg) };  // clock: 연출 시계(초) — 타격 멈춤 동안은 서 있다
  }

  // 싸움터(인물이 서는 띠)의 평균 밝기 0~255: 인물 테두리 색을 고른다
  function groundLum(bg) {
    try {
      const y0 = Math.round(CH * 0.45), h = Math.round(CH * 0.5);
      const d = bg.getContext('2d').getImageData(0, y0, CW, h).data;
      let sum = 0, n = 0;
      for (let i = 0; i < d.length; i += 4 * 37) { sum += 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]; n++; }
      return n ? sum / n : 128;
    } catch (e) { return 128; }
  }

  const rnd = (a, b) => a + Math.random() * (b - a);
  function spawn(view, n, x, y, o) {
    for (let i = 0; i < n && view.parts.length < 500; i++) {
      const ang = o.ang != null ? o.ang + rnd(-o.spread, o.spread) : rnd(0, Math.PI * 2);
      const sp = rnd(o.sp[0], o.sp[1]);
      view.parts.push({ x, y, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp, life: 0, max: rnd(o.life[0], o.life[1]),
        size: o.size || 2, color: o.color, add: o.add !== false, grav: o.grav || 0, rise: o.rise || 0 });
    }
  }

  // 새로 생긴 효과 이벤트를 입자·궤적·마법진으로 바꾼다
  function ingest(view, st) {
    // 새로 쓰러진 유닛: 발밑 먼지
    st.units.forEach((u) => {
      if (u.alive || u.downAt == null || view.downSeen.has(u)) return;
      view.downSeen.add(u);
      downPuff(view, u.x * Z + edxOf(view, u), u.y * Z, !!(u.bigMon || u.boss));
    });
    // 새로 날아가기 시작한 투사체: 쏜 유닛이 공격(마법은 시전) 동작을 한다
    st.shots.forEach((s) => {
      if (s.seen) return;
      s.seen = true;
      if (s.from && s.from.alive) triggerAttack(view, s.from, s.kind === 'arrow' || s.kind === 'dagger' ? 'attack' : 'cast');
    });
    st.fx.forEach((f) => {
      if (f.seen) return;
      f.seen = true;
      // 글자·타격 효과를 실제 그림 높이에 맞추기 위해 대상 유닛의 키를 기억해 둔다
      const off = { hit: 8, boom: 8, pop: 18, heal: 14, label: 26 }[f.kind];
      if (off != null) {
        const u = nearestUnit(st, f.x, f.y + off);
        f.foot = (f.y + off) * Z;
        f.tall = u ? stature(view, u).h : 34;
        // 대장 위에 뜨는 숫자·치유 표시는 몸 옆으로 비켜 그린다 (가슴을 덮지 않게)
        if (u && keepVisible(u)) { f.capW = stature(view, u).w; f.capFace = u.face || (u.side === 0 ? 1 : -1); }
        f.who = u; // 글자의 주인 (다른 대장 몸통을 비킬 때 자기 몸은 빼고 본다)
      }
      if (f.kind === 'skill' && f.type === 'atk') {
        const u = st.units.find((e) => e.alive && (f.look ? e.look === f.look : e.mon === f.mon && Math.abs(e.x - f.x) + Math.abs(e.y - f.y) < 4));
        // 근접(shot 없음)은 이 틱에 이미 맞았다 → 타격 칸부터. 여기서 먼저 불리므로 그리기 쪽의 같은 호출은 중복 방지에 걸린다
        // (예전에는 여기서 '맞는 순간' 표시 없이 불러, 미리 준비 자세를 못 보여 준 근접 공격의 12~21% 가 맞은 뒤에 준비 칸을 보였다)
        if (u) {
          triggerAttack(view, u, f.shot && f.shot !== 'arrow' && f.shot !== 'dagger' ? 'cast' : 'attack', !f.shot);
          if (!f.shot) rsOf(view, u).atkMelee = true;
        }
      } else if (f.kind === 'cast') {
        const u = nearestUnit(st, f.x, f.y, (e) => e.alive);
        // 근접 특기(돌격·급소 찌르기 등)는 시전 동작이 아니라 뒤따르는 공격 동작을 쓴다
        const atk = u && st.fx.find((g) => !g.seen && g.kind === 'skill' && g.type === 'atk' && (g.look ? g.look === u.look : g.mon === u.mon));
        if (u && !(atk && (!atk.shot || atk.shot === 'arrow' || atk.shot === 'dagger'))) triggerAttack(view, u, 'cast');
      }
      const X = f.x * Z + edxOf(view, f.who);
      // 몸통 높이: 타격·폭발은 그림 키의 절반쯤
      const Y = f.foot != null && (f.kind === 'hit' || f.kind === 'boom') ? f.foot - Math.round(f.tall * 0.5) : f.y * Z;
      if (f.kind === 'hit') {
        hitSpark(view, X, Y, f.dir || 1, f.foot != null ? f.foot : Y + 14, f.big, f.melee ? WARM_RAMP : rampOf(f.color));
        // 맞은 쪽이 살짝 밀렸다 돌아온다 (큰 괴물·보스는 꿈쩍하지 않는다)
        if (f.who && f.who.alive && !f.who.boss && !f.who.bigMon) { const rr = rsOf(view, f.who); rr.kickAt = view.clock; rr.kickDir = f.dir < 0 ? -1 : 1; rr.kickPx = f.big ? 5 : 3; }
        if (f.melee) view.slashes.push({ x: X, y: Y, foot: f.foot != null ? f.foot : Y + 12, dir: f.dir, t: 0, big: f.big, style: f.style, color: f.special ? '#9fd8ff' : '#ffffff' });
        if (f.big) { view.shake = Math.max(view.shake, f.special ? 5 : 3); view.stop = Math.max(view.stop, f.special ? 0.09 : 0.05); }
      } else if (f.kind === 'boom') {
        view.slashes.push({ x: X, y: Y, t: 0, boom: true, r: f.r * Z, color: f.color });
        spawn(view, 22, X, Y, { sp: [60, 220], life: [0.3, 0.7], color: f.color, size: 3, grav: 260 });
        spawn(view, 10, X, Y, { sp: [10, 50], life: [0.5, 0.9], color: '#5a4a48', size: 4, add: false, rise: -30 });
        view.shake = Math.max(view.shake, 6); view.stop = Math.max(view.stop, 0.08);
      } else if (f.kind === 'heal') {
        spawn(view, 6, X, Y + 10, { ang: -Math.PI / 2, spread: 0.5, sp: [20, 50], life: [0.5, 0.9], color: '#9cff9c', size: 2 });
      } else if (f.kind === 'ring') {
        view.sigils.push({ x: X, y: Y + 6 * Z, r: f.r * Z, t: 0, max: 0.9, color: f.color, ring: true });
        spawn(view, 14, X, Y, { ang: -Math.PI / 2, spread: 1.2, sp: [20, 70], life: [0.4, 0.8], color: f.color, size: 2 });
      } else if (f.kind === 'cast') {
        view.sigils.push({ x: X, y: Y, r: Math.min(60, f.r * Z * 0.8), t: 0, max: 0.8, color: f.color });
      } else if (f.kind === 'dash') {
        view.slashes.push({ x: X, y: Y, t: 0, dash: true, color: '#ffffff' });
      } else if (f.kind === 'drain') {
        // 흡혈: 붉은 알갱이가 대상에서 시전자에게 흘러간다
        for (let i = 0; i < 6; i++) view.vfx.push({ type: 'mote', t: -i * 0.04, max: 0.45, x: X + rnd(-6, 6), y: Y + rnd(-6, 6), tx: f.tx * Z, ty: (f.ty - 9) * Z, color: '#ff4a5a' });
      } else if (f.kind === 'skill') {
        recipe(view, f, st);
      }
    });
  }

  // 스킬 성격별 연출
  function recipe(view, f, st) {
    const X = f.x * Z, Y = f.y * Z;
    const T = (f.targets || []).map(([x, y]) => [x * Z, y * Z]);
    if (f.type === 'rally') {
      const col = f.def ? '#6ac8ff' : '#ffb04a';
      view.vfx.push({ type: 'burst', t: 0, max: 0.7, x: X, y: Y, r: f.r * Z, color: col });
      spawn(view, 30, X, Y - 10, { ang: -Math.PI / 2, spread: 1.4, sp: [40, 120], life: [0.5, 1.0], color: col, size: 3 });
      view.flash = Math.max(view.flash, 0.12); view.flashColor = col;
      return;
    }
    if (f.type === 'heal') {
      T.forEach(([x, y], i) => view.vfx.push({ type: 'pillar', t: -i * 0.05, max: 0.7, x, y, w: f.special ? 14 : 8, color: '#a8ffb0' }));
      if (f.aoe) view.vfx.push({ type: 'burst', t: 0, max: 0.8, x: X, y: Y, r: f.aoe * Z, color: '#7ed37e' });
      return;
    }
    // 공격
    const sp = f.special;
    // 시전자 (잔상·숨결 위치에 쓴다)
    const who = st && st.units.find((e) => (f.look ? e.look === f.look : e.mon === f.mon && Math.abs(e.x - f.x) + Math.abs(e.y - f.y) < 4));
    if (sp && (f.aoe >= 20 || f.boss)) { view.flash = Math.max(view.flash, 0.15); view.flashColor = '#ffffff'; }
    if (f.dash) {
      // 잔상: 출발점에서 도착점까지 반투명한 분신
      const x0 = f.fx0 * Z, y0 = f.fy0 * Z;
      if (who) {
        const fr = pose(view, who, 'walk'), flip = (f.face || 1) !== fr.face;
        for (let i = 1; i <= 5; i++) view.vfx.push({ type: 'ghost', t: 0, max: 0.35, x: x0 + (X - x0) * (i / 6), y: y0 + (Y - y0) * (i / 6), fr, flip, a: 0.15 + i * 0.08 });
      }
      view.vfx.push({ type: 'streak', t: 0, max: 0.25, x0, y0: y0 - 12 - LIFT, x1: X, y1: Y - 12 - LIFT });
    }
    if (!f.shot) {
      if (sp && f.aoe) view.vfx.push({ type: 'whirl', t: 0, max: 0.45, x: X, y: Y - 12 - LIFT, r: Math.max(24, f.aoe * Z), color: '#cfe8ff' });
      if (sp && f.stun) T.forEach(([x, y]) => {
        view.vfx.push({ type: 'quake', t: 0, max: 0.6, x, y, r: 26 + (f.aoe || 0) * Z * 0.6, seed: Math.random() * 10 });
        spawn(view, 12, x, y, { ang: -Math.PI / 2, spread: 1.2, sp: [40, 120], life: [0.3, 0.6], color: '#b0987a', size: 3, add: false, grav: 300 });
      });
      if (sp && f.exec) T.forEach(([x, y]) => view.vfx.push({ type: 'xslash', t: 0, max: 0.35, x, y: y - 14 - LIFT }));
      if (f.hits > 1) T.forEach(([x, y], i) => view.slashes.push({ x, y: y - 14 - LIFT, dir: f.face, t: -i * 0.05, big: true, color: '#ffe8a8' }));
      if (f.boss && sp) view.vfx.push({ type: 'quake', t: 0, max: 0.7, x: T[0] ? T[0][0] : X, y: T[0] ? T[0][1] : Y, r: 60, seed: 3 });
      return;
    }
    if (f.shot === 'arrow' && f.hits >= 3) {
      // 화살비: 대상들 위로 화살이 쏟아진다
      T.forEach(([x, y]) => { for (let i = 0; i < 4; i++) view.vfx.push({ type: 'fall', t: -rnd(0, 0.25), max: 0.32, x: x + rnd(-10, 10), y: y - 8, color: '#f4f0e0' }); });
    }
    if (f.shot === 'bolt') {
      // 번개: 시전자에서 대상으로, 대상끼리 이어지는 연쇄
      let px0 = X, py0 = Y - 18 - LIFT * 2;
      T.forEach(([x, y]) => { view.vfx.push({ type: 'bolt', t: 0, max: sp ? 0.3 : 0.16, x0: px0, y0: py0, x1: x, y1: y - 16 - LIFT, w: sp ? 3 : 2 }); px0 = x; py0 = y - 16 - LIFT; });
    }
    if (f.shot === 'curse' && sp) T.forEach(([x, y]) => view.vfx.push({ type: 'swirl', t: 0, max: 0.8, x, y: y - 12 - LIFT, r: 18 + (f.aoe || 0) * Z * 0.5, color: '#b47aff' }));
    if (f.boss && sp && (f.shot === 'fire' || f.shot === 'curse')) {
      // 보스의 숨결: 부채꼴로 쏟아지는 불길
      const [tx, ty] = T[0] || [X - 80, Y];
      const by = Y - Math.round((who ? stature(view, who).h : 34) * 0.6);
      const ang = Math.atan2(ty - LIFT - by, tx - X);
      for (let i = 0; i < 40; i++) {
        view.parts.length < 500 && view.parts.push({ x: X, y: by, vx: Math.cos(ang + rnd(-0.35, 0.35)) * rnd(160, 320), vy: Math.sin(ang + rnd(-0.35, 0.35)) * rnd(160, 320),
          life: -rnd(0, 0.3), max: rnd(0.4, 0.7), size: 4, color: f.shot === 'fire' ? (Math.random() < 0.5 ? '#ff7a2a' : '#ffd84a') : '#c07aff', add: true, grav: 0, rise: 0 });
      }
    }
  }

  // 지형별 분위기 입자
  const AMBIENT = {
    forest: { color: '#d8ff7a', n: 2, glow: true, drift: [-6, 6], fall: [-6, 6], life: 3 },     // 반딧불
    swamp: { color: '#9ab0a0', n: 3, glow: false, drift: [4, 14], fall: [-2, 2], life: 4, size: 4, alpha: 0.25 }, // 안개
    desert: { color: '#e8c088', n: 6, glow: false, drift: [60, 120], fall: [-4, 8], life: 2 },  // 모래바람
    frost: { color: '#ffffff', n: 6, glow: false, drift: [-10, 10], fall: [18, 40], life: 4 },  // 눈
    mountain: { color: '#ff8a3a', n: 4, glow: true, drift: [-8, 8], fall: [-40, -15], life: 3 }, // 불티
    holy: { color: '#fff2a8', n: 3, glow: true, drift: [-4, 4], fall: [-14, -4], life: 3 },     // 빛 알갱이
    plains: { color: '#ffd0e0', n: 2, glow: false, drift: [14, 30], fall: [6, 16], life: 4 },   // 꽃잎
    coast: { color: '#e8f4ff', n: 2, glow: false, drift: [20, 40], fall: [-2, 6], life: 3 },    // 물보라
  };
  function updateAmbient(view, dt) {
    const A = AMBIENT[view.terrain] || AMBIENT.plains;
    if (Math.random() < A.n * dt * 8 && view.amb.length < 80) {
      view.amb.push({ x: rnd(-20, CW), y: rnd(0, CH), vx: rnd(A.drift[0], A.drift[1]), vy: rnd(A.fall[0], A.fall[1]), life: 0, max: A.life * rnd(0.7, 1.3), ph: rnd(0, 6) });
    }
    view.amb.forEach((p) => { p.life += dt; p.x += p.vx * dt + Math.sin(p.life * 2 + p.ph) * 6 * dt; p.y += p.vy * dt; });
    view.amb = view.amb.filter((p) => p.life < p.max && p.x < CW + 20 && p.y < CH + 20 && p.y > -20);
  }
  function drawAmbient(ctx, view) {
    const A = AMBIENT[view.terrain] || AMBIENT.plains;
    ctx.globalCompositeOperation = A.glow ? 'lighter' : 'source-over';
    view.amb.forEach((p) => {
      const k = p.life / p.max, a = (k < 0.2 ? k / 0.2 : k > 0.8 ? (1 - k) / 0.2 : 1) * (A.alpha || 0.8);
      ctx.globalAlpha = a * (A.glow ? 0.6 + 0.4 * Math.sin(p.life * 6 + p.ph) : 1);
      if (A.glow) ctx.drawImage(glow(A.color, 6), p.x - 6, p.y - 6);
      px(ctx, Math.round(p.x), Math.round(p.y), A.size || 2, A.size || 2, A.color);
    });
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  }

  // 효과 목록 그리기 (빛 번짐 위주)
  // 아군 대장·특별 용병의 몸통 위에서 터지는 큰 빛·고리 효과는 조금 옅게 (타격감은 남기고 인물은 가리지 않게)
  const CAP_DIM = 0.6;
  function capDim(view, x, y) {
    return (view.capBodies || []).some((b) => x > b.x0 - 4 && x < b.x1 + 4 && y > b.y0 - 4 && y < b.y1 + 4) ? CAP_DIM : 1;
  }

  function drawVfx(ctx, view, now) {
    view.vfx.forEach((v) => {
      if (v.t < 0) return;
      const k = v.t / v.max;
      const dim = v.type === 'bolt' ? capDim(view, v.x1, v.y1) : v.x != null ? capDim(view, v.x, v.y) : 1;
      if (v.type === 'ghost') {
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, v.a * (1 - k));
        blit(ctx, v.fr, v.x, v.y, v.flip);
      } else if (v.type === 'streak') {
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, 1 - k);
        ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(v.x0, v.y0); ctx.lineTo(v.x1, v.y1); ctx.stroke();
        ctx.lineWidth = 8; ctx.globalAlpha *= 0.25; ctx.stroke();
      } else if (v.type === 'whirl') {
        // 회전 베기: 시전자 둘레를 도는 궤적 세 줄
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, 1 - k) * dim;
        ctx.strokeStyle = v.color;
        for (let i = 0; i < 3; i++) {
          ctx.lineWidth = 4 - i;
          const a0 = k * 9 + (i * Math.PI * 2) / 3;
          ctx.beginPath(); ctx.ellipse(v.x, v.y, v.r - i * 4, (v.r - i * 4) * 0.42, 0, a0, a0 + 2.2); ctx.stroke();
        }
        ctx.drawImage(glow(v.color, 30), v.x - 30, v.y - 30);
      } else if (v.type === 'quake') {
        // 지면 강타: 금 간 땅 + 충격파
        ctx.globalCompositeOperation = 'source-over';
        ctx.globalAlpha = Math.max(0, 1 - k);
        ctx.strokeStyle = '#1a120c'; ctx.lineWidth = 2;
        for (let i = 0; i < 7; i++) {
          const a = (i / 7) * Math.PI * 2 + v.seed;
          ctx.beginPath(); ctx.moveTo(v.x, v.y);
          let x = v.x, y = v.y;
          for (let j = 1; j <= 3; j++) { x += Math.cos(a + Math.sin(j * 3 + v.seed) * 0.5) * v.r / 3; y += Math.sin(a) * v.r * 0.13; ctx.lineTo(x, y); }
          ctx.stroke();
        }
        ctx.globalCompositeOperation = 'lighter';
        ctx.strokeStyle = '#ffd8a0'; ctx.lineWidth = 3;
        const r = v.r * (0.3 + k * 1.3);
        ctx.beginPath(); ctx.ellipse(v.x, v.y, r, r * 0.38, 0, 0, Math.PI * 2); ctx.stroke();
      } else if (v.type === 'xslash') {
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, 1 - k) * (dim < 1 ? 0.75 : 1);
        const L = 22 * Math.min(1, k * 4);
        ctx.strokeStyle = '#ff4a6a'; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(v.x - L, v.y - L); ctx.lineTo(v.x + L, v.y + L); ctx.moveTo(v.x + L, v.y - L); ctx.lineTo(v.x - L, v.y + L); ctx.stroke();
        ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5; ctx.stroke();
        ctx.globalAlpha = Math.max(0, 1 - k) * dim;
        ctx.drawImage(glow('#ff4a6a', 26), v.x - 26, v.y - 26);
      } else if (v.type === 'fall') {
        // 하늘에서 떨어지는 화살
        const y = v.y - 120 * (1 - k);
        ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.95;
        ctx.strokeStyle = v.color; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(v.x - 3, y - 16); ctx.lineTo(v.x, y); ctx.stroke();
        if (k > 0.9 && !v.hit) { v.hit = true; spawn(view, 4, v.x, v.y, { sp: [30, 80], life: [0.15, 0.3], color: '#ffffff', size: 2 }); }
      } else if (v.type === 'bolt') {
        // 지그재그 번개
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, 1 - k) * (Math.floor(now / 40) % 2 ? 1 : 0.7);
        const seg = 7;
        ctx.beginPath(); ctx.moveTo(v.x0, v.y0);
        for (let i = 1; i < seg; i++) {
          const q = i / seg;
          ctx.lineTo(v.x0 + (v.x1 - v.x0) * q + rnd(-8, 8), v.y0 + (v.y1 - v.y0) * q + rnd(-8, 8));
        }
        ctx.lineTo(v.x1, v.y1);
        ctx.strokeStyle = '#7fd6ff'; ctx.lineWidth = v.w + 4; ctx.globalAlpha *= 0.5; ctx.stroke();
        ctx.globalAlpha /= 0.5; ctx.strokeStyle = '#ffffff'; ctx.lineWidth = v.w; ctx.stroke();
        ctx.globalAlpha *= dim;
        ctx.drawImage(glow('#7fd6ff', 16), v.x1 - 16, v.y1 - 16);
      } else if (v.type === 'swirl') {
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, 1 - k) * dim;
        for (let i = 0; i < 10; i++) {
          const a = k * 10 + i * 0.63, rr = v.r * (1 - k * 0.6) * (0.4 + (i % 3) * 0.3);
          px(ctx, Math.round(v.x + Math.cos(a) * rr) - 2, Math.round(v.y + Math.sin(a) * rr * 0.6) - 2, 4, 4, v.color);
        }
        ctx.drawImage(glow(v.color, 22), v.x - 22, v.y - 22);
      } else if (v.type === 'pillar') {
        // 치유의 빛기둥
        ctx.globalCompositeOperation = 'lighter';
        const a = k < 0.2 ? k / 0.2 : 1 - (k - 0.2) / 0.8;
        ctx.globalAlpha = Math.max(0, a) * 0.8 * (dim < 1 ? 0.8 : 1);
        const g = ctx.createLinearGradient(0, v.y - 90, 0, v.y);
        g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, v.color);
        ctx.fillStyle = g; ctx.fillRect(Math.round(v.x - v.w / 2), Math.round(v.y - 90), v.w, 90);
        ctx.drawImage(glow(v.color, 16), v.x - 16, v.y - 16);
        if (Math.random() < 0.3) spawn(view, 1, v.x + rnd(-v.w, v.w), v.y, { ang: -Math.PI / 2, spread: 0.2, sp: [40, 80], life: [0.3, 0.6], color: '#e8ffe8', size: 2 });
      } else if (v.type === 'burst') {
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = Math.max(0, 1 - k) * dim;
        ctx.strokeStyle = v.color; ctx.lineWidth = 3;
        const r = v.r * (0.2 + k);
        ctx.beginPath(); ctx.ellipse(v.x, v.y, r, r * 0.4, 0, 0, Math.PI * 2); ctx.stroke();
        ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(v.x, v.y, r * 0.8, r * 0.32, 0, 0, Math.PI * 2); ctx.stroke();
      } else if (v.type === 'mote') {
        const x = v.x + (v.tx - v.x) * k, y = v.y + (v.ty - v.y) * k - Math.sin(k * Math.PI) * 20;
        ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.9;
        ctx.drawImage(glow(v.color, 6), x - 6, y - 6);
        px(ctx, Math.round(x) - 1, Math.round(y) - 1, 3, 3, '#ffd0d0');
      }
    });
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  }

  function updateView(view, dt) {
    view.parts.forEach((p) => {
      p.life += dt;
      if (p.life < 0) return;
      p.x += p.vx * dt; p.y += p.vy * dt + p.rise * dt;
      p.vy += p.grav * dt; p.vx *= 0.92; p.vy *= p.grav ? 1 : 0.92;
    });
    view.parts = view.parts.filter((p) => p.life < p.max);
    updateSparks(view, dt);
    view.slashes.forEach((s) => { s.t += dt; });
    view.slashes = view.slashes.filter((s) => s.t < (s.boom ? 0.5 : 0.22));
    view.sigils.forEach((s) => { s.t += dt; });
    view.sigils = view.sigils.filter((s) => s.t < s.max);
    view.vfx.forEach((v) => { v.t += dt; });
    view.vfx = view.vfx.filter((v) => v.t < v.max);
    view.flash = Math.max(0, view.flash - dt);
    updateAmbient(view, dt);
    view.shake = Math.max(0, view.shake - dt * 30);
  }

  function text(ctx, str, x, y, size, color, bold = true) {
    ctx.font = `${bold ? 'bold ' : ''}${size}px Galmuri11, monospace`;
    ctx.lineWidth = Math.max(2, size / 4); ctx.strokeStyle = '#140e18'; ctx.lineJoin = 'round';
    ctx.strokeText(str, x, y);
    ctx.fillStyle = color; ctx.fillText(str, x, y);
  }

  // 칸으로 나뉜 체력바
  function segBar(ctx, x, y, w, ratio, color, segs) {
    px(ctx, x - 1, y - 1, w + 2, 6, '#140e18');
    const sw = (w - (segs - 1)) / segs;
    for (let i = 0; i < segs; i++) {
      const fill = Math.max(0, Math.min(1, ratio * segs - i));
      px(ctx, Math.round(x + i * (sw + 1)), y, Math.round(sw), 4, '#3a2228');
      if (fill > 0) px(ctx, Math.round(x + i * (sw + 1)), y, Math.round(sw * fill), 4, color);
      if (fill > 0) px(ctx, Math.round(x + i * (sw + 1)), y, Math.round(sw * fill), 1, '#ffffff55');
    }
  }

  function brackets(ctx, x, y, w, h, color) {
    ctx.fillStyle = color;
    const L = 5;
    [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(([bx, by, sx, sy]) => {
      ctx.fillRect(bx - (sx < 0 ? 2 : 0), by - (sy < 0 ? 2 : 0), L * sx, 2);
      ctx.fillRect(bx - (sx < 0 ? 2 : 0), by - (sy < 0 ? 2 : 0), 2, L * sy);
    });
  }

  function draw(ctx, view, st, now, label) {
    const shx = view.shake ? rnd(-view.shake, view.shake) : 0, shy = view.shake ? rnd(-view.shake, view.shake) * 0.6 : 0;
    ctx.save();
    ctx.translate(Math.round(shx), Math.round(shy));
    ctx.drawImage(view.bg, 0, 0);

    // 바닥 마법진·고리
    ctx.globalCompositeOperation = 'lighter';
    view.sigils.forEach((s) => {
      const k = s.t / s.max, a = k < 0.2 ? k / 0.2 : 1 - (k - 0.2) / 0.8;
      ctx.globalAlpha = Math.max(0, a) * 0.9;
      ctx.strokeStyle = s.color; ctx.lineWidth = 2;
      const r = s.ring ? s.r * (0.4 + k * 0.8) : s.r;
      ctx.beginPath(); ctx.ellipse(s.x, s.y, r, r * 0.4, 0, 0, Math.PI * 2); ctx.stroke();
      if (!s.ring) {
        ctx.beginPath(); ctx.ellipse(s.x, s.y, r * 0.7, r * 0.28, 0, 0, Math.PI * 2); ctx.stroke();
        for (let i = 0; i < 6; i++) {
          const ang = s.t * 3 + (i * Math.PI) / 3;
          ctx.fillStyle = s.color;
          ctx.fillRect(Math.round(s.x + Math.cos(ang) * r * 0.85) - 2, Math.round(s.y + Math.sin(ang) * r * 0.34) - 2, 4, 4);
        }
        ctx.drawImage(glow(s.color, 24), s.x - 24, s.y - 34);
      }
    });
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';

    // 아군 대장·특별 용병이 노리는 적: 조준 표시 (발밑)
    st.units.forEach((u) => {
      if (!u.alive || u.fled || u.side !== 0 || !u.unique || !u.target || !u.target.alive) return;
      const t = u.target, w = Math.round(stature(view, t).w * 0.9) + 12;
      brackets(ctx, Math.round(t.x * Z + edxOf(view, t) - w / 2), Math.round(t.y * Z - 10), w, 14, '#ff5a7a');
    });

    // 유닛: 쓰러진 유닛 먼저, 그다음 발 위치(y) 순으로 — 아래쪽(앞쪽) 인물이 위에 그려진다
    const sorted = st.units.filter((u) => !u.fled).sort((a, b) => (a.alive - b.alive) || a.y - b.y || a.x - b.x);
    // 대장은 바로 앞(발 위치가 조금 아래)에 겹쳐 선 자기 편 대원보다 나중에 그린다 → 난전에서 대원 머리에 가려지지 않는다
    sorted.filter((u) => u.alive && u.captain).forEach((c) => {
      const i = sorted.indexOf(c);
      let j = -1;
      for (let k = i + 1; k < sorted.length; k++) {
        const o = sorted[k];
        if (o.alive && o.side === c.side && !o.captain && o.y - c.y < 9 && Math.abs(o.x - c.x) < 12) j = k;
      }
      if (j > i) { sorted.splice(i, 1); sorted.splice(j, 0, c); }
    });
    const drawn = []; // 그린 순서대로 몸통 영역 (대장이 가려졌는지 판단)
    for (const u of sorted) {
      const r = rsOf(view, u);
      // 연출 상태 갱신: 근접 공격(앞으로 내딛기)·피격 번쩍임이 새로 시작됐는지
      if (u.lunge > r.prevLunge + 0.01) { triggerAttack(view, u, 'attack', true); r.atkMelee = true; }
      if (u.flash > r.prevFlash + 0.01) r.hitAt = view.clock;
      r.prevLunge = u.lunge; r.prevFlash = u.flash;
      const S = stature(view, u);
      const face = u.face || (u.side === 0 ? 1 : -1);
      gaitUpdate(view, st, u, r, S.h, face);
      if (view.clock - r.atkAt > r.atkDur && aboutToStrike(st, u, r)) {
        if (view.clock - (r.windAt == null ? -9 : r.windAt) > 0.25) r.windStart = view.clock;
        r.windAt = view.clock;
      }
      const fr = pose(view, u);
      const flip = face !== fr.face;
      // 몸의 앞뒤 움직임: 공격(준비 때 뒤로·타격 때 앞으로) + 맞았을 때 밀림
      const kt = r.kickAt != null ? view.clock - r.kickAt : 9;
      const push = face * lungeOf(view, u, r, fr) + (kt >= 0 && kt < 0.18 ? r.kickDir * r.kickPx * (1 - kt / 0.18) : 0);
      const X = Math.round(screenX(view, u, fr, flip, push)), Y = Math.round(u.y * Z);
      if (!u.alive) {
        // 쓰러짐: 잠깐 깜빡인 뒤 땅으로 가라앉으며 사라진다
        const dt = st.t - u.downAt;
        if (!u.puffed) { u.puffed = true; spawn(view, 8, X, Y - 6, { sp: [10, 40], life: [0.4, 0.8], color: '#8a7a70', size: 3, add: false, rise: -20 }); }
        ctx.fillStyle = 'rgba(30,10,10,0.25)';
        ctx.beginPath(); ctx.ellipse(X, Y, Math.max(8, S.w * 0.4), 4, 0, 0, Math.PI * 2); ctx.fill();
        const k = Math.max(0, Math.min(1, (dt - 0.35) / 1.4));
        if (k < 1) {
          ctx.save();
          const fk = fr.k || 1;
          ctx.beginPath(); ctx.rect(X - fr.sw * fk, Y - fr.sh * fk - 40, fr.sw * fk * 2, fr.sh * fk + 42); ctx.clip();
          ctx.globalAlpha = dt < 0.35 ? (Math.floor(dt * 14) % 2 ? 0.35 : 0.95) : 0.85 * (1 - k);
          blit(ctx, fr, X, Y + Math.round(k * S.h * 0.5), flip);
          ctx.restore();
        }
        if (u.doomed && dt > 0.4) ctx.drawImage(Sprites.icon('skull', 2), Math.round(X - 8), Y - 22);
        continue;
      }
      // 그림자
      ctx.fillStyle = 'rgba(0,0,0,0.35)';
      ctx.beginPath(); ctx.ellipse(X + (flip ? -S.cx : S.cx), Y - 1, Math.max(9, S.w * 0.42), 4 + Math.min(6, S.w / 16), 0, 0, Math.PI * 2); ctx.fill();
      // 강화 오라
      if (buffSum(u, 'atk', st.t) > 0 || buffSum(u, 'def', st.t) > 0) {
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = 0.35 + 0.15 * Math.sin(now / 120);
        const gc = buffSum(u, 'atk', st.t) > 0 ? '#ff6a4a' : '#5ab8ff';
        const gr = Math.round(Math.max(20, S.h * 0.45));
        ctx.drawImage(glow(gc, gr), X - gr, Y - Math.round(S.h * 0.45) - gr);
        ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
      }
      // 걸음 (walkTf): 걸음 칸이 그려지지 않은 시트는 그림을 바꾸지 않고 몸 전체만 1px 남짓 오르내린다 (주인 11-26), 코드 도트는 뜰 때만 떠오른다
      const tf = walkTf(view, st, u, r, fr, S, X, Y);
      blit(ctx, fr, X, Y, flip, null, tf);
      drawRim(ctx, view, fr, X, Y, flip, tf);
      // 맞은 순간 하얗게 번쩍 (흰 실루엣을 짧게 덧그린다: 연타를 맞아도 계속 하얗지 않게 처음 0.08초만)
      //  (아군 대장·특별 용병은 조금 옅게: 얼굴·갑옷이 하얗게 날아가지 않게)
      if (u.flash > 0.1) {
        ctx.globalAlpha = (0.25 + 0.45 * Math.min(1, (u.flash - 0.1) / 0.08)) * (keepVisible(u) ? 0.7 : 1);
        blit(ctx, fr, X, Y, flip, tinted(fr, '#ffffff'), tf);
        ctx.globalAlpha = 1;
      }
      {
        const bx = X + (flip ? -S.cx : S.cx);
        drawn.push({ u, fr, X, Y, flip, tf, x0: bx - S.w * 0.42, x1: bx + S.w * 0.42, y0: Y - S.h + 2, y1: Y - 2 });
      }
      const top = Y - S.h;
      // 부대 깃발: 대장 등 뒤
      if (u.captain) {
        const fl = Sprites.flag(u.g.color, u.g.side === 0 ? '#f2c94c' : '#1b1420', 2);
        const fx = face > 0 ? X - Math.round(S.w * 0.5) - 10 : X + Math.round(S.w * 0.5) - 4;
        ctx.drawImage(fl, fx, Math.max(2, top - 4));
      }
      // 기절 별
      if (u.stunUntil > st.t) {
        for (let i = 0; i < 3; i++) {
          const ang = now / 160 + (i * Math.PI * 2) / 3;
          px(ctx, Math.round(X + Math.cos(ang) * 11) - 2, Math.round(top + 2 + Math.sin(ang) * 3) - 2, 4, 4, '#ffe066');
        }
      }
      // 거미줄에 걸림: 몸통에 들러붙은 거미줄 (남은 시간이 0.4초 아래면 옅어진다)
      if (u.slowUntil > st.t) drawWebOn(ctx, X, Y - Math.round(S.h * 0.45), S.h, u.slowUntil - st.t, u.webSeed || (u.webSeed = 1 + Math.floor(Math.random() * 7)));
      if (u.g.routed && Math.floor(now / 250) % 2) text(ctx, '!', X, top - 2, 14, '#ffffff');
    }
    // 큰 괴물(1.5배 우두머리·거대 괴물·보스)의 몸이 먼저(뒤쪽에) 그린 아군 단원을 덮으면, 그 괴물 몸 자리 안에서만 단원을 반투명하게
    // 덧그린다 — 괴물이 그 자리만 살짝 비쳐 보이는 셈. 난전에서 단원이 이름표만 남지 않게. (대장·특별 용병은 아래 윤곽선이 맡는다)
    // 켜고 끌 때는 연출 시계로 0.2초 동안 서서히 (깜빡이지 않게)
    drawn.forEach((d, i) => {
      if (d.u.side !== 0 || keepVisible(d.u)) return;
      const r = rsOf(view, d.u), area = (d.x1 - d.x0) * (d.y1 - d.y0);
      const clips = [];
      let cover = 0;
      for (let k = i + 1; k < drawn.length; k++) {
        const o = drawn[k];
        if (o.u.side === 0 || !(o.u.bigMon || o.u.boss || (o.fr.k || 1) > 1)) continue;
        const w = Math.min(d.x1, o.x1) - Math.max(d.x0, o.x0), h = Math.min(d.y1, o.y1) - Math.max(d.y0, o.y0);
        if (w > 0 && h > 0) { cover += w * h; clips.push([o.x0, o.y0, o.x1 - o.x0, o.y1 - o.y0]); }
      }
      const want = cover >= area * 0.2 ? 1 : 0;
      const step = Math.max(0, view.clock - (r.seeAt == null ? view.clock : r.seeAt)) / 0.2;
      r.seeAt = view.clock;
      r.see = want > (r.see || 0) ? Math.min(want, (r.see || 0) + step) : Math.max(want, (r.see || 0) - step);
      if (clips.length) r.seeClips = clips;
      if (r.see <= 0.01 || !r.seeClips) return;
      ctx.save();
      ctx.beginPath();
      r.seeClips.forEach((c) => ctx.rect(...c));
      ctx.clip();
      ctx.globalAlpha = 0.55 * r.see;
      blit(ctx, d.fr, d.X, d.Y, d.flip, null, d.tf);
      ctx.globalAlpha = 1;
      ctx.restore();
    });
    view.capBodies = drawn.filter((d) => keepVisible(d.u)).map((d) => ({ u: d.u, x0: d.x0, x1: d.x1, y0: d.y0, y1: d.y1 }));
    // 그래도 앞쪽 인물에 몸이 꽤 가려진 아군 대장·특별 용병: 윤곽선과 옅은 몸을 그 위에 덧그려 자리를 알린다
    drawn.forEach((d, i) => {
      if (!keepVisible(d.u)) return;
      const area = (d.x1 - d.x0) * (d.y1 - d.y0);
      let cover = 0;
      for (let k = i + 1; k < drawn.length; k++) {
        const o = drawn[k];
        const w = Math.min(d.x1, o.x1) - Math.max(d.x0, o.x0), h = Math.min(d.y1, o.y1) - Math.max(d.y0, o.y0);
        if (w > 0 && h > 0) cover += w * h;
      }
      // 켜고 끌 때 깜빡이지 않게 연출 시계로 0.15초 동안 서서히 (타격 멈춤 동안은 그대로)
      const r = rsOf(view, d.u), want = cover >= area * 0.12 ? 1 : 0;
      const step = Math.max(0, view.clock - (r.occAt || view.clock)) / 0.15;
      r.occAt = view.clock;
      r.occ = want > (r.occ || 0) ? Math.min(want, (r.occ || 0) + step) : Math.max(want, (r.occ || 0) - step);
      if (r.occ <= 0.01) return;
      ctx.globalAlpha = 0.24 * r.occ;
      blit(ctx, d.fr, d.X, d.Y, d.flip, null, d.tf);
      ctx.globalAlpha = 0.8 * r.occ;
      blit(ctx, d.fr, d.X, d.Y, d.flip, edgeOf(d.fr, d.u.side === 0 ? '#ffe27a' : '#ff8a8a', 'ring'), d.tf);
      ctx.globalAlpha = 1;
    });

    // 투사체 (빛 번짐)
    ctx.globalCompositeOperation = 'lighter';
    st.shots.forEach((s) => {
      let X = s.x * Z, Y = s.y * Z - LIFT;
      const col = SHOT_COLOR[s.kind] || '#ffffff';
      if (s.meteor) {
        // 메테오: 실제 궤적은 수평이지만 하늘에서 떨어지듯 그린다
        const d0 = Math.hypot(s.to.x - s.sx, s.to.y - 9 - s.sy) || 1, d1 = Math.hypot(s.to.x - s.x, s.to.y - 9 - s.y);
        const k = 1 - d1 / d0;
        X = s.to.x * Z + 60 * (1 - k); Y = (s.to.y - 9) * Z - LIFT - 200 * (1 - k);
        const r = 26;
        ctx.globalAlpha = 1; ctx.drawImage(glow('#ff7a2a', r), X - r, Y - r);
        ctx.drawImage(glow('#ffe08a', 12), X - 12, Y - 12);
        spawn(view, 2, X, Y, { ang: -Math.PI / 3, spread: 0.4, sp: [30, 80], life: [0.2, 0.5], color: '#ff9a3a', size: 3 });
        return;
      }
      const tx = s.to.x * Z, ty = (s.to.y - 9) * Z - LIFT, d = Math.hypot(tx - X, ty - Y) || 1;
      const dx = (tx - X) / d, dy = (ty - Y) / d;
      if (s.kind === 'web') {
        drawWebShot(ctx, s, X, Y, dx, dy);
        return;
      }
      if (s.kind === 'arrow' || s.kind === 'dagger') {
        ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.globalAlpha = 0.9;
        ctx.beginPath(); ctx.moveTo(X - dx * 12, Y - dy * 12); ctx.lineTo(X, Y); ctx.stroke();
        ctx.globalAlpha = 0.4; ctx.beginPath(); ctx.moveTo(X - dx * 26, Y - dy * 26); ctx.lineTo(X - dx * 12, Y - dy * 12); ctx.stroke();
      } else {
        const r = s.kind === 'fire' ? 14 : 11;
        ctx.globalAlpha = 0.9; ctx.drawImage(glow(col, r), X - r, Y - r);
        ctx.globalAlpha = 0.5; ctx.drawImage(glow(col, r), X - dx * 10 - r, Y - dy * 10 - r);
        px(ctx, Math.round(X) - 2, Math.round(Y) - 2, 4, 4, '#ffffff');
        if (Math.random() < 0.5) spawn(view, 1, X, Y, { sp: [5, 30], life: [0.15, 0.3], color: col, size: 2 });
      }
    });
    ctx.globalAlpha = 1;

    // 베기 궤적·폭발
    view.slashes.forEach((s) => {
      if (s.t < 0) return;
      if (s.boom) {
        const k = s.t / 0.5, dim = capDim(view, s.x, s.y);
        // 은은한 빛은 남기되 옅게 — 폭발의 모양은 도트 폭발(drawBurst)이 맡는다
        ctx.globalAlpha = Math.max(0, 1 - k) * dim * 0.5;
        const r = Math.round(s.r * (0.5 + k * 1.2) + 10);
        ctx.drawImage(glow(s.color, r), s.x - r, s.y - r);
        ctx.globalAlpha = dim;
        drawBurst(ctx, s, r);
      } else if (s.dash) {
        ctx.globalAlpha = Math.max(0, 1 - s.t / 0.22);
        px(ctx, Math.round(s.x) - 30, Math.round(s.y), 60, 2, '#ffffff');
        px(ctx, Math.round(s.x) - 20, Math.round(s.y) - 6, 40, 1, '#ffffff');
      } else if (s.style === 'thrust') {
        drawThrust(ctx, s);
      } else if (s.style === 'smash') {
        drawSmash(ctx, s);
      } else {
        drawSmear(ctx, s);
      }
    });
    ctx.globalAlpha = 1;

    drawVfx(ctx, view, now);

    drawSparks(ctx, view);

    // 입자
    view.parts.forEach((p) => {
      if (p.life < 0) return;
      const a = 1 - p.life / p.max;
      ctx.globalCompositeOperation = p.add ? 'lighter' : 'source-over';
      ctx.globalAlpha = Math.max(0, a);
      px(ctx, Math.round(p.x), Math.round(p.y), p.size, p.size, p.color);
    });
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';

    // 분위기 입자, 앞쪽 수풀
    drawAmbient(ctx, view);
    if (view.fg) ctx.drawImage(view.fg, 0, 0);

    // 체력바·이름표
    //  - 아군 대장·특별 용병의 몸통 위에는 다른 유닛의 체력바·이름표를 놓지 않는다 (옆으로 비키고, 자리가 없으면 감춘다)
    //  - 대장의 체력바·이름표는 맨 나중에 (맨 위에) 그린다
    ctx.textAlign = 'center';
    ctx.font = '11px Galmuri11, monospace';
    const live = st.units.filter((u) => u.alive && !u.fled).sort((a, b) => b.y - a.y);
    const bodies = drawn.filter((d) => keepVisible(d.u)).map((d) => ({ u: d.u, x0: d.x0 - 2, x1: d.x1 + 2, y0: d.y0 + 2, y1: d.y1 - 4 }));
    const onBody = (u, x, y, w, h) => bodies.some((b) => b.u !== u && x < b.x1 && x + w > b.x0 && y < b.y1 && y + h > b.y0);
    const tags = [];
    const bars = []; // 칸 체력바 자리 (다른 유닛의 이름표가 덮지 않게)
    // loose: 일반 단원의 체력바는 무시하고 이름표·대장 체력바만 본다 (빈자리가 없을 때 두 번째로 찾는 기준)
    const tagHit = (u, x, y, w, loose) => tags.some((t) => x < t.x + t.w && x + w > t.x && y < t.y + 15 && y + 15 > t.y) ||
      bars.some((b) => b.u !== u && (!loose || keepVisible(b.u)) && x < b.x + b.w && x + w > b.x && y < b.y + b.h && y + 14 > b.y);
    // 대장 몸통을 피하는 가로 비킴 (없으면 null)
    const dodge = (u, x, y, w, h, max) => {
      for (let d = 0; d <= max; d += 4) {
        if (!onBody(u, x + d, y, w, h)) return d;
        if (d && !onBody(u, x - d, y, w, h)) return -d;
      }
      return null;
    };
    // 이름표는 자기 유닛 머리 위에 붙어 있어야 한다: 제자리 → 한 칸 살짝 위 → 옆으로 조금씩 (체력바처럼).
    // 빈자리가 없으면 다른 단원의 체력바는 덮어도 되는 것으로 보고 한 번 더 찾는다. 그래도 대장 몸통·이름표와 겹치면
    // 일반 단원의 이름표는 그동안 감춘다 (대장 이름표는 제자리에 그대로 그린다).
    const TAG_UP = 8, TAG_SIDE = 20;
    const tagOf = (u, X, top) => {
      const name = u.named || '';
      const tw = Math.ceil(ctx.measureText(name).width) + 8, key = keepVisible(u), y0 = top - 24;
      const free = (dx, dy, loose) => !tagHit(u, X + dx - tw / 2, y0 + dy, tw, loose) && (key || !onBody(u, X + dx - tw / 2, y0 + dy, tw, 14));
      let at = null;
      for (const loose of [false, true]) {
        for (let d = 0; d <= TAG_SIDE && !at; d += 4) {
          for (const [dx, dy] of d ? [[d, 0], [-d, 0], [d, -TAG_UP], [-d, -TAG_UP]] : [[0, 0], [0, -TAG_UP]]) {
            if (free(dx, dy, loose)) { at = [dx, dy]; break; }
          }
        }
        if (at) break;
      }
      if (!at) { if (!key) return null; at = [0, 0]; }
      const t = { u, x: X + at[0] - tw / 2, y: y0 + at[1], w: tw, name, X: X + at[0], unique: u.unique };
      tags.push(t);
      return t;
    };
    const drawTag = (t) => {
      px(ctx, t.x, t.y, t.w, 14, t.unique ? '#2a3a7a' : '#2a2a3a');
      px(ctx, t.x, t.y, t.w, 1, '#8aa0ff');
      ctx.fillStyle = '#ffffff'; ctx.fillText(t.name, t.X, t.y + 11);
    };
    const geo = (u) => ({ X: Math.round(u.x * Z + edxOf(view, u)), top: Math.round(u.y * Z - stature(view, u).h) - 2, color: u.side === 0 ? '#7ee07e' : '#ff6a6a' });
    const barW = (u) => (u.boss ? 60 : 32);
    // 대장 체력바·이름표 자리를 먼저 잡아 둔다 (다른 이름표가 그 자리를 피한다)
    live.forEach((u) => { if (keepVisible(u)) { const { X, top } = geo(u); bars.push({ u, x: X - barW(u) / 2 - 1, y: top - 9, w: barW(u) + 2, h: 6 }); } });
    const keyTags = live.filter((u) => keepVisible(u) && u.side === 0 && (u.unique || u.named)).map((u) => { const g = geo(u); return tagOf(u, g.X, g.top); });
    // 일반 단원·적 부대장의 체력바와 이름표: 이미 자리 잡은 체력바·이름표(대장 것 먼저)와 겹치면 그동안 서서히 감춘다.
    // 난전에서 이름표·체력바가 한 덩어리로 쌓이지 않게. 지난 그리기에 보이던 것이 자리를 지키고(먼저 자리를 잡는다),
    // 한 번 감춘 것은 0.35초 동안 감춘 채로 둔다 — 두 유닛이 비슷한 자리를 오가도 깜빡이지 않는다.
    const shown = bars.map((b) => ({ x: b.x, y: b.y, w: b.w, h: b.h })).concat(keyTags.filter(Boolean).map((t) => ({ x: t.x, y: t.y, w: t.w, h: 14 })));
    const clash = (x, y, w, h) => shown.some((b) => x < b.x + b.w && x + w > b.x && y < b.y + b.h && y + h > b.y);
    const labOf = (u, kind) => { const r = rsOf(view, u); r.lab = r.lab || {}; return r.lab[kind] || (r.lab[kind] = { a: 0, want: 1, at: view.clock, hold: -1 }); };
    const fadeLab = (L, want) => {
      if (!want && L.want) L.hold = view.clock + 0.35;
      if (want && view.clock < L.hold) want = 0;
      const dt = Math.max(0, view.clock - L.at);
      L.at = view.clock; L.want = want;
      L.a = Math.max(0, Math.min(1, L.a + Math.max(-dt / 0.18, Math.min(dt / 0.18, want - L.a))));
      return L.a;
    };
    const order = (kind, rank) => (a, b) => labOf(b, kind).want - labOf(a, kind).want || rank(b) - rank(a) || st.units.indexOf(a) - st.units.indexOf(b);
    // 1) 적 부대장·우두머리·이름 있는 병사 (대장이 아닌 쪽): 체력바 → 이름표
    const mid = [];
    live.filter((u) => !keepVisible(u) && (u.captain || u.named || u.boss)).sort(order('bar', (u) => (u.boss ? 2 : u.captain ? 1 : 0))).forEach((u) => {
      const { X, top, color } = geo(u);
      const w = barW(u), L = labOf(u, 'bar');
      const d = dodge(u, X - w / 2, top - 8, w, 6, 24);
      const ok = d != null && !clash(X + d - w / 2 - 1, top - 9, w + 2, 6);
      if (ok) { L.dx = d; bars.push({ u, x: X + d - w / 2 - 1, y: top - 9, w: w + 2, h: 6 }); shown.push(bars[bars.length - 1]); }
      const a = fadeLab(L, ok ? 1 : 0);
      if (a > 0.02 && L.dx != null) mid.push({ u, X: X + L.dx, top, color, w, a });
    });
    mid.forEach((m) => { ctx.globalAlpha = m.a; segBar(ctx, m.X - m.w / 2, m.top - 8, m.w, m.u.hp / m.u.maxHp, m.color, m.u.boss ? 10 : 5); });
    ctx.globalAlpha = 1;
    live.filter((u) => !keepVisible(u) && u.side === 0 && u.named).sort(order('tag', () => 0)).forEach((u) => {
      const { X, top } = geo(u), L = labOf(u, 'tag');
      const t = tagOf(u, X + (u.captain || u.named || u.boss ? labOf(u, 'bar').dx || 0 : 0), top);
      const ok = !!t && !clash(t.x, t.y, t.w, 14);
      if (ok) { L.t = { dx: t.x - X, dy: t.y - top, w: t.w, name: t.name, unique: t.unique }; shown.push({ x: t.x, y: t.y, w: t.w, h: 14 }); }
      const a = fadeLab(L, ok ? 1 : 0);
      if (a > 0.02 && L.t) {
        ctx.globalAlpha = a;
        drawTag({ x: X + L.t.dx, y: top + L.t.dy, w: L.t.w, name: L.t.name, X: X + L.t.dx + L.t.w / 2, unique: L.t.unique });
        ctx.globalAlpha = 1;
      }
    });
    // 2) 일반 병사의 작은 체력바 (맞은 병사만)
    live.filter((u) => !(u.captain || u.named || u.boss || keepVisible(u) || u.hp >= u.maxHp)).sort(order('bar', () => 0)).forEach((u) => {
      const { X, top, color } = geo(u), L = labOf(u, 'bar');
      const d = dodge(u, X - 12, top - 5, 24, 4, 20);
      const ok = d != null && !clash(X + d - 12, top - 5, 24, 4);
      if (ok) { L.dx = d; shown.push({ x: X + d - 12, y: top - 5, w: 24, h: 4 }); }
      const a = fadeLab(L, ok ? 1 : 0);
      if (a <= 0.02 || L.dx == null) return;
      ctx.globalAlpha = a;
      px(ctx, X + L.dx - 12, top - 5, 24, 4, '#140e18');
      px(ctx, X + L.dx - 11, top - 4, Math.max(0, Math.round(22 * (u.hp / u.maxHp))), 2, color);
      ctx.globalAlpha = 1;
    });
    // 3) 아군 대장·특별 용병: 맨 위에
    live.forEach((u) => {
      if (!keepVisible(u)) return;
      const { X, top, color } = geo(u);
      const w = barW(u);
      segBar(ctx, X - w / 2, top - 8, w, u.hp / u.maxHp, color, u.boss ? 10 : 5);
    });
    keyTags.forEach((t) => { if (t) drawTag(t); });

    // 글자(피해 숫자·스킬 이름)가 다른 아군 대장·특별 용병의 몸통이나 이름표에 얹히면 옆이나 위로 비킨다.
    // 비킨 거리는 f 에 기억해 두고, 그 자리가 다시 막힐 때만 새로 찾는다 (글자가 흔들리지 않게).
    const marks = bodies.concat(tags.map((t) => ({ u: t.u, x0: t.x, x1: t.x + t.w, y0: t.y, y1: t.y + 14 })));
    const bodyAt = (who, x, y, w, h) => marks.find((b) => b.u !== who && x < b.x1 && x + w > b.x0 && y < b.y1 && y + h > b.y0);
    const avoid = (f, who, x, y, w, h) => {
      if (f.ax != null && !bodyAt(who, x + f.ax, y + f.ay, w, h)) return;
      let ax = 0, ay = 0;
      for (let i = 0; i < 3; i++) {
        const b = bodyAt(who, x + ax, y + ay, w, h);
        if (!b) break;
        const side = x + ax + w / 2 < (b.x0 + b.x1) / 2 ? b.x0 - (x + ax + w) - 2 : b.x1 - (x + ax) + 2;
        const up = b.y0 - (y + ay + h) - 2;
        if (Math.abs(side) <= Math.abs(up)) ax += side; else ay += up;
      }
      f.ax = ax; f.ay = ay;
    };
    const textW = (str, size) => { ctx.font = `bold ${size}px Galmuri11, monospace`; return Math.ceil(ctx.measureText(str).width) + 4; };
    // 피해 숫자·스킬 이름·치유
    st.fx.forEach((f) => {
      const X = f.x * Z + edxOf(view, f.who);
      // 글자는 그 유닛 그림의 머리 위 쪽에 (ingest 에서 기억한 키 기준)
      const head = f.foot != null ? f.foot - f.tall : f.y * Z;
      const Y = f.kind === 'pop' ? head + 26 : f.kind === 'heal' ? head + 18 : f.kind === 'label' ? head - 30 : f.y * Z;
      if (f.kind === 'pop') {
        if (!(f.crit || f.ally && f.named || f.mine)) return; // 화면이 어지럽지 않게
        if (f.merged) return;
        if (f.jx == null) {
          // 난전에서 숫자가 쌓이지 않게: 같은 유닛이 방금 맞아 아직 떠 있는 숫자가 있으면 그 숫자에 더하고(합친 피해),
          // 가까운 무리(가로 44px·세로 30px 안)에 이미 떠 있는 숫자 위로 한 줄씩 올려 놓는다. 세 줄이 차면 치명타만 네 번째 줄에.
          const fresh = st.fx.filter((o) => o !== f && o.kind === 'pop' && o.jx != null && !o.merged && o.t < 0.45);
          const twin = f.who && fresh.find((o) => o.who === f.who && o.ally === f.ally);
          if (twin) { twin.sum = (twin.sum != null ? twin.sum : +twin.text) + +f.text; twin.big = twin.big || f.crit; f.merged = true; return; }
          const near = fresh.filter((o) => Math.abs(o.x - f.x) * Z < 44 && Math.abs(o.y - f.y) * Z < 30);
          let lane = 0;
          while (lane < 3 && near.some((o) => (o.lane || 0) === lane)) lane++;
          if (lane >= 3 && !f.crit) { f.merged = true; return; }
          f.lane = lane;
          f.jx = rnd(-14, 14) * (near.length ? 0.4 : 1); f.jy = rnd(-6, 6) - lane * 15;
          // 대장이 맞은 숫자: 가슴 대신 등 뒤 옆으로 (몸 너비의 절반 + 여유)
          if (f.capW) { f.jx = -f.capFace * (f.capW * 0.5 + rnd(6, 14)); f.jy = rnd(-14, -4) - lane * 15; }
        }
        const up = Math.min(1, f.t * 5), str = f.sum != null ? String(Math.round(f.sum)) : f.text, big = f.crit || f.big;
        const y = Y - 6 - up * 10 - f.t * 14 + f.jy, size = big ? 20 : 15;
        if (marks.length) { const w = textW(str, size); avoid(f, f.who, X + f.jx - w / 2, y - size + 2, w, size); }
        ctx.globalAlpha = f.t > 0.5 ? Math.max(0, 1 - (f.t - 0.5) * 5) : 1;
        text(ctx, str, X + f.jx + (f.ax || 0), y + (f.ay || 0), size, f.ally ? '#ff7a96' : big ? '#ffd84a' : '#ffffff');
        ctx.globalAlpha = 1;
      } else if (f.kind === 'heal' && f.named) {
        ctx.globalAlpha = Math.max(0, 1 - f.t * 1.4);
        text(ctx, '+', X + (f.capW ? f.capFace * (f.capW * 0.5 + 6) : 0), Y - f.t * 30, 16, '#8cff8c');
        ctx.globalAlpha = 1;
      } else if (f.kind === 'label') {
        const y = Math.round(Y - f.t * 16);
        if (marks.length) { const w = textW(f.text, 14); avoid(f, f.who, X - w / 2, y - 12, w, 15); }
        ctx.globalAlpha = f.t > 0.9 ? Math.max(0, 1 - (f.t - 0.9) * 3.3) : 1;
        text(ctx, f.text, X + (f.ax || 0), y + (f.ay || 0), 14, f.side === 0 ? '#ffe066' : '#ffb0b0');
        ctx.globalAlpha = 1;
      }
    });
    ctx.restore();

    // 가장자리 어둡게 (비네트)
    if (!view.vignette) {
      const v = document.createElement('canvas'); v.width = CW; v.height = CH;
      const vc = v.getContext('2d');
      const g = vc.createRadialGradient(CW / 2, CH / 2, CH * 0.35, CW / 2, CH / 2, CW * 0.62);
      g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(10,4,16,0.55)');
      vc.fillStyle = g; vc.fillRect(0, 0, CW, CH);
      view.vignette = v;
    }
    ctx.drawImage(view.vignette, 0, 0);
    // 큰 기술의 섬광
    if (view.flash > 0) {
      ctx.globalCompositeOperation = 'lighter';
      // 밝은 지형(설원·성역)에서는 하얗게 날아가지 않게 약하게
      ctx.globalAlpha = Math.min(view.terrain === 'frost' || view.terrain === 'holy' ? 0.08 : 0.18, view.flash * 1.4);
      ctx.fillStyle = view.flashColor; ctx.fillRect(0, 0, CW, CH);
      ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
    }

    if (label) {
      ctx.textAlign = 'center';
      text(ctx, label.text, CW / 2, 108, 40, label.good ? '#ffd84a' : '#ff6a6a');
    }
  }

  // 부대 현황판 (HTML)
  function rosterRow(g, name, trainees) {
    const row = document.createElement('div');
    row.className = 'troop';
    const sw = document.createElement('span'); sw.className = 'troop-sw'; sw.style.background = g.color;
    const nm = document.createElement('span'); nm.className = 'troop-name'; nm.textContent = name;
    const bar = document.createElement('span'); bar.className = 'troop-bar';
    const fill = document.createElement('i'); bar.append(fill);
    const cnt = document.createElement('span'); cnt.className = 'troop-cnt';
    if (trainees) nm.textContent += ` (${g.units.length - trainees} + 수습 ${trainees})`;
    row.append(sw, nm, bar, cnt);
    if (g.player) row.classList.add('mine');
    return { row, fill, cnt, nm };
  }

  function play(report, onDone) {
    stop();
    const q = report.quest;
    const won = report.outcome === 'great' || report.outcome === 'success';
    // 전투 모드(3단계): 결과를 정한 바로 그 전투를 재생한다 — 굳힌 편성(report.battle.spec)으로 같은 setup·step. 찾기(findBattle)는 없다.
    // 먼저 화면 없이 한 번 돌려 해시를 맞춰 본다: 엔진이 바뀌어 다른 판이 나오는 옛 보고서는 재생하지 않고 바로 보고서로 간다.
    // 이 세션에서 방금 판정한 전투(Game.judgedHere)는 같은 엔진이 돌린 것이라 다시 돌리지 않는다 (휴대폰에서 전투 한 판 몫을 아낀다, 검증 6번)
    const real = report.battle && report.battle.spec;
    if (real) {
      const fresh = typeof Game !== 'undefined' && Game.judgedHere && Game.judgedHere.has(report.battle);
      const rec = fresh ? null : run(real);
      if (rec && (rec.ver !== report.battle.ver || rec.hash !== report.battle.hash)) {
        const skip = document.createElement('div');
        setTimeout(onDone, 0);
        return skip;
      }
    }
    const groups = real ? real.groups : plan(report);
    let st;
    if (real) st = begin(real);
    else {
      const seed = report.seed || q.id * 7919 + 17;
      const found = findBattle(groups, report.outcome, seed);
      st = setup(groups, found.bias, found.seed);
    }
    lastSt = st;   // 시험용: 화면에서 재생한 판의 기록을 판정과 맞춰 볼 수 있게 (Battle.last() → Battle.record)

    const cvs = document.createElement('canvas');
    cvs.width = CW; cvs.height = CH; cvs.className = 'battle-canvas';
    const ctx = cvs.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const view = makeView(PROVINCES[q.province].terrain);

    const wrap = document.createElement('div');
    wrap.className = 'battle';
    const head = document.createElement('div');
    head.className = 'battle-head';
    head.textContent = `${q.title} — ${PROVINCES[q.province].name}`;
    const timer = document.createElement('span');
    timer.className = 'battle-timer';
    head.append(timer);

    // 현황판: 아군 / 적군
    const roster = document.createElement('div');
    roster.className = 'battle-roster';
    const cols = [document.createElement('div'), document.createElement('div')];
    cols[0].className = 'troops side-ally'; cols[1].className = 'troops side-enemy';
    const t0 = document.createElement('div'); t0.className = 'troops-title'; t0.textContent = '아군';
    const t1 = document.createElement('div'); t1.className = 'troops-title'; t1.textContent = q.enemy ? '적 (괴물)' : `적 (${FACTIONS[q.target || q.issuer].name})`;
    cols[0].append(t0); cols[1].append(t1);
    const enemyNames = new Map();
    const rows = st.groups.map((g) => {
      let name = g.name;
      if (g.side === 1 && st.groups.filter((other) => other.side === 1 && other.name === name).length > 1) {
        const number = (enemyNames.get(name) || 0) + 1;
        enemyNames.set(name, number);
        name += ` ${number}`;
      }
      const trainees = groups[g.id].units.filter((u) => u.recruit).length;
      const r = rosterRow(g, name, trainees);
      cols[g.side].append(r.row);
      return r;
    });
    roster.append(...cols);

    const speedBtn = document.createElement('button');
    speedBtn.className = 'btn small';
    const speeds = [1, 2, 4];
    let speedIdx = 0;
    const setSpeed = () => { speedBtn.textContent = `속도 ×${speeds[speedIdx]}`; };
    setSpeed();
    speedBtn.addEventListener('click', () => { speedIdx = (speedIdx + 1) % speeds.length; setSpeed(); });
    const skip = document.createElement('button');
    skip.className = 'btn small';
    skip.textContent = '결과 보기 ▶▶';
    const foot = document.createElement('div');
    foot.className = 'modal-actions';
    foot.append(speedBtn, skip);
    const ticker = document.createElement('div');
    ticker.className = 'battle-ticker';
    const stage = document.createElement('div');
    stage.className = 'battle-stage';
    const cutin = document.createElement('div');
    cutin.className = 'cutin';
    stage.append(cvs, cutin);
    wrap.append(head, stage, ticker, roster, foot);
    let cutShown = 0, lastCut = -1e9;
    const showCutin = (c) => {
      const pic = (typeof Art !== 'undefined' && Art.img(c.art, 'cutin-pic')) || Sprites.clone(Sprites.merc(c.look, 6, 0), 'cutin-pic');
      const txt = document.createElement('div');
      txt.className = 'cutin-text';
      txt.innerHTML = '';
      const n = document.createElement('div'); n.className = 'cutin-name'; n.textContent = c.name || '';
      const k = document.createElement('div'); k.className = 'cutin-skill'; k.textContent = c.skill;
      txt.append(n, k);
      cutin.replaceChildren(pic, txt);
      cutin.classList.remove('play');
      void cutin.offsetWidth; // 애니메이션 다시 시작
      cutin.classList.add('play');
    };
    let shownEvents = 0;

    let finished = false;
    const finish = () => { if (finished) return; finished = true; stop(); onDone(); };
    skip.addEventListener('click', finish);

    const labelText = { great: '대승리!', success: '승리!', fail: '후퇴...', disaster: '패주...' }[report.outcome];
    let last = performance.now(), acc = 0, rosterTick = 0;
    const loop = (now) => {
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      // 큰 타격 순간에는 잠깐 멈춘다 (타격감)
      // 연출 시계(view.clock)도 함께 멈춘다 → 동작 애니메이션이 그 순간에 얼어붙는다
      if (view.stop > 0) view.stop = Math.max(0, view.stop - dt);
      else { acc += dt * speeds[speedIdx] * 1.3; view.clock += dt * Math.min(2, speeds[speedIdx]) * 1.3; view.idleClock = (view.idleClock || 0) + dt; }
      view.speedK = speeds[speedIdx];
      while (acc >= DT) {
        acc -= DT;
        step(st);
        st.fx.forEach((f) => { f.t += DT; });
        st.fx = st.fx.filter((f) => f.t < (f.kind === 'label' ? 1.2 : 0.7));
        ingest(view, st);
      }
      updateView(view, dt);
      // 컷인: 너무 잦지 않게 1.3초 간격
      if (st.cutins.length > cutShown && now - lastCut > 1300) {
        showCutin(st.cutins[st.cutins.length - 1]);
        cutShown = st.cutins.length; lastCut = now;
      } else if (st.cutins.length > cutShown && now - lastCut <= 1300) cutShown = st.cutins.length;
      const ended = st.over && st.t - st.endT > 0.6;
      draw(ctx, view, st, now, ended ? { text: labelText, good: won } : null);
      if (now - rosterTick > 200) {
        rosterTick = now;
        rows.forEach((r, i) => {
          const g = st.groups[i];
          const alive = groupAlive(g).length;
          r.fill.style.width = `${Math.round((alive / g.units.length) * 100)}%`;
          r.cnt.textContent = g.routed && alive ? '패주' : `${alive}/${g.units.length}`;
          r.row.classList.toggle('broken', g.routed);
          if (g.flipped && r.row.parentNode !== cols[1]) { cols[1].append(r.row); r.row.classList.add('traitor'); }
        });
        timer.textContent = ` ${Math.floor(st.t)}초`;
        if (st.events.length !== shownEvents) {
          shownEvents = st.events.length;
          ticker.replaceChildren(...st.events.slice(-2).map((e) => {
            const d = document.createElement('div');
            d.className = e.side === 0 ? 'bad' : 'good';
            d.textContent = e.text;
            return d;
          }));
        }
      }
      if (st.over && st.t - st.endT > END_HOLD) return finish();
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return wrap;
  }

  function stop() { if (raf) cancelAnimationFrame(raf); raf = null; }

  return { play, stop, plan, simulate, findBattle, VER, setup, step, begin, record, run, last: () => lastSt };
})();
