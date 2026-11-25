// 실시간 집단 전투
// 용병대장 1 + 대원 2~3으로 이루어진 부대가 양쪽 최대 3개씩(3vs3) 전장에서 스스로 판단해 싸운다.
// 의뢰의 결과(대성공/성공/실패/대실패)는 판정에서 정해지고, 전투는 시드를 바꿔 가며 실제로
// 시뮬레이션해 그 결과가 나오는 판을 찾아 재생한다. 연출을 위해 짜 맞춘 각본은 없다.
'use strict';

const Battle = (() => {
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
  const SHOT_COLOR = { arrow: '#e8e4d8', fire: '#ff9a3c', curse: '#b47aff', bolt: '#7fd6ff', dagger: '#e0e8f0', holy: '#fff2a8' };

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
    return [basic];
  }


  let raf = null;

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
  function setup(groups, bias, seed) {
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
          const hp = base.hp * str * (captain && !ud.mon ? 1.6 : 1) * (ud.unique ? 1.15 : 1);
          // 대형: 대장이 뒤 가운데, 대원 둘이 앞 위아래, 셋째는 맨 앞 (큰 도트끼리 겹치지 않는 간격: SEP_X·SEP_Y 타원 밖)
          const fwd = side === 0 ? 1 : -1;
          const SLOT = [[-8, 0], [10, -10], [10, 10], [28, 0]];
          const [sx, sy] = SLOT[k] || [-8 - 18 * (k - 3), k % 2 ? -10 : 10];
          const ox = fwd * sx, oy = sy;
          const unit = {
            g, side, captain, ...ud,
            x: cx + ox + (r() - 0.5) * 4, y: clamp(cy + oy + (r() - 0.5) * 4, TOP, BOTTOM),
            hp, maxHp: hp, atk: base.atk * str * ATK_SCALE, healPow: HEAL_POWER * str * ATK_SCALE, speed: base.speed * (0.9 + r() * 0.2),
            skills: skills.map((sk, i) => ({ ...sk, left: i === 0 ? r() * sk.cd : sk.cd * (0.3 + r() * 0.5) })),
            buffs: [], stunUntil: 0,
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
    return { r, units, groups: gs, shots: [], fx: [], t: 0, over: false, winner: null, endT: 0, events: [], cutins: [] };
  }

  const groupAlive = (g) => g.units.filter((u) => u.alive && !u.fled);
  const sideActive = (st, side) => st.groups.some((g) => g.side === side && !g.routed && groupAlive(g).length);
  // Math.hypot 은 느려서 (전투 찾기가 한 판을 여러 번 시뮬레이션한다) 제곱근으로 직접 잰다
  const dist = (a, b) => { const dx = a.x - b.x, dy = a.y - b.y; return Math.sqrt(dx * dx + dy * dy); };
  const len2 = (x, y) => Math.sqrt(x * x + y * y);
  const meleeDist = (a, b) => { const dx = a.x - b.x, dy = (a.y - b.y) * DEPTH; return Math.sqrt(dx * dx + dy * dy); };
  const sizeOf = (u) => (u.scale > 1 ? u.scale * 4 : 0);
  const isMelee = (u) => !u.healer && !u.skills[0].shot;

  // 근접 교전 자리 배정: 목표마다 자리(MELEE_SLOTS)를 나눠 쥐어, 여럿이 한 점에 겹쳐 서지 않게 한다.
  // 자리 주인은 그 목표를 계속 노리는 동안만 유효하다 (목표를 바꾸거나 쓰러지면 자리가 빈다).
  const holdsSlot = (a, t, i) => a.alive && !a.fled && !a.g.routed && a.target === t && a.slotOf === t && a.slot === i;
  const slotFree = (t, i, u) => { const a = t.slots[i]; return !a || a === u || !holdsSlot(a, t, i); };
  const slotAt = (t, i, s) => {
    const [ox, oy] = MELEE_SLOTS[i];
    return { x: t.x + (ox >= 0 ? s : -s) * (Math.abs(ox) + sizeOf(t)), y: clamp(t.y + oy, TOP, BOTTOM) };
  };
  // 목표 곁에 이미 붙은 다른 근접 공격자 수 (다 찼으면 Infinity)
  function crowdOf(t, u) {
    if (!t.slots) return 0;
    let n = 0;
    for (let i = 0; i < slotCount(t); i++) if (!slotFree(t, i, u)) n++;
    return n >= meleeCap(t) ? Infinity : n;
  }
  // u 가 t 를 칠 자리 (자리가 다 찼으면 null)
  function slotPos(t, u) {
    if (!t.slots) t.slots = [];
    if (u.slotOf !== t || u.slot < 0 || t.slots[u.slot] !== u) {
      // 새로 자리를 잡는다: 빈자리 중 가장 가까운 곳. 다가오는 쪽(왼쪽/오른쪽)은 이때 정해 둔다.
      const s = u.x <= t.x ? -1 : 1;
      const full = crowdOf(t, u) === Infinity;
      let best = -1, bd = Infinity;
      for (let i = 0; i < slotCount(t) && !full; i++) {
        if (!slotFree(t, i, u)) continue;
        const p = slotAt(t, i, s);
        const d = len2(p.x - u.x, p.y - u.y);
        if (d < bd) { bd = d; best = i; }
      }
      u.slotOf = t; u.slot = best; u.slotSide = s;
      if (best < 0) return null;
      t.slots[best] = u;
    }
    return slotAt(t, u.slot, u.slotSide);
  }
  const buffSum = (u, k, t) => u.buffs.reduce((a, b) => a + (b.until > t ? (b[k] || 0) : 0), 0);
  const atkMul = (u, t) => {
    const cap = u.g.captain;
    const aura = cap.alive && cap !== u && len2(cap.x - u.x, cap.y - u.y) < 60 ? 1.1 : 1; // 대장 곁의 대원은 힘이 난다
    return (1 + buffSum(u, 'atk', t)) * aura;
  };
  const defMul = (u, t) => 1 - Math.min(0.6, buffSum(u, 'def', t));

  function addBuff(st, u, b) { if (b) u.buffs.push({ atk: b.atk || 0, def: b.def || 0, until: st.t + b.dur }); }

  function damage(st, target, dmg, crit, src) {
    if (!target.alive) return 0;
    dmg *= defMul(target, st.t);
    target.hp -= dmg;
    target.flash = 0.18;
    st.fx.push({ kind: 'pop', x: target.x, y: target.y - 18, text: String(Math.round(dmg)), crit, ally: target.side === 0,
      mine: !!(src && src.side === 0 && src.unique), named: !!target.named, t: 0 });
    if (target.hp <= 0) {
      target.alive = false;
      target.hp = 0;
      target.downAt = st.t;
      if (target.captain) st.events.push({ t: st.t, text: `${target.g.name}의 대장이 쓰러졌다!`, side: target.side });
    }
    return dmg;
  }

  // 공격 스킬 한 번이 대상에 닿았을 때
  function strike(st, u, t, sk) {
    if (!t.alive) return;
    const crit = st.r() < 0.1;
    const base = u.atk * atkMul(u, st.t) * sk.dmg * (0.85 + st.r() * 0.3) * (crit ? 1.7 : 1);
    const victims = sk.aoe ? st.units.filter((e) => e.alive && !e.fled && e.side !== u.side && dist(e, t) <= sk.aoe + sizeOf(e)) : [t];
    if (!victims.includes(t)) victims.push(t);
    let dealt = 0;
    victims.forEach((e) => {
      let d = base * (e === t ? 1 : 0.7);
      if (sk.exec && e.hp / e.maxHp < 0.35) d *= 1 + sk.exec;
      dealt += damage(st, e, d, crit && e === t, u);
      if (sk.stun && e.alive) e.stunUntil = Math.max(e.stunUntil, st.t + sk.stun * (e.boss ? 0.3 : e.bigMon ? 0.6 : 1));
    });
    const special = sk !== u.skills[0];
    st.fx.push({ kind: 'hit', x: t.x, y: t.y - 8, dir: u.face, melee: !sk.shot, big: crit || special, special, t: 0,
      color: SHOT_COLOR[sk.shot] || (u.side === 0 ? '#bfe8ff' : '#ffb0a0') });
    if (sk.aoe) st.fx.push({ kind: 'boom', x: t.x, y: t.y - 8, r: sk.aoe, t: 0, color: SHOT_COLOR[sk.shot] || '#f39c12' });
    if (sk.drain && u.alive) {
      u.hp = Math.min(u.maxHp, u.hp + dealt * sk.drain);
      if (dealt > 0) st.fx.push({ kind: 'drain', x: t.x, y: t.y, tx: u.x, ty: u.y, t: 0 });
    }
    if (sk.selfBuff) addBuff(st, u, sk.selfBuff);
  }

  function mend(st, u, t, sk) {
    const list = sk.aoe ? st.units.filter((a) => a.alive && !a.fled && a.side === u.side && dist(a, t) <= sk.aoe) : [t];
    list.forEach((a) => {
      if (!a.alive) return;
      a.hp = Math.min(a.maxHp, a.hp + u.healPow * sk.heal * (0.9 + st.r() * 0.2));
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
    const reach = (sk.dash ? Math.max(sk.range, 60) : sk.range + (sk.shot ? 0 : BODY));
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
    if (sk !== u.skills[0]) st.fx.push({ kind: 'cast', x: u.x, y: u.y, t: 0, r: Math.max(12, sk.aoe || 12), color: sk.tgt === 'hurt' ? '#7ed37e' : SHOT_COLOR[sk.shot] || (sk.buff ? '#f2c94c' : '#ffffff') });
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
      targets = live.filter((e) => e.side !== u.side && !e.g.routed && dist(e, u) - sizeOf(e) <= Math.max(sk.range, 30) + 20)
        .sort((a, b) => dist(a, u) - dist(b, u)).slice(0, sk.hits);
      if (!targets.length) targets = [t];
    }
    const fromX = u.x, fromY = u.y;
    if (sk.dash) {
      // 돌진: 대상 곁으로 뛰어든다
      const d = dist(u, t) || 1;
      const stop = MELEE_SLOTS[0][0] + sizeOf(t); // 정면 자리 거리에서 멈춘다
      if (d > stop) { u.x = t.x - ((t.x - u.x) / d) * stop; u.y = t.y - ((t.y - u.y) / d) * stop; }
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
    // 배신: 충성도가 바닥난 외부 용병단이 전투 도중 적으로 돌아선다
    st.groups.forEach((g) => {
      if (g.betray && !g.flipped && st.t > 7) {
        g.flipped = true; g.side = 1;
        g.units.forEach((u) => { u.side = 1; u.target = null; });
        st.events.push({ t: st.t, text: `「${g.name}」이(가) 적에게 돌아섰다!`, side: 1 });
      }
    });
    // 사기: 병력 대부분을 잃거나 대장을 잃고 크게 꺾이면 패주
    st.groups.forEach((g) => {
      if (g.routed) return;
      const alive = groupAlive(g).length, n = g.units.length;
      if (!alive) { g.routed = true; return; }
      if (alive / n < 0.3 || (!g.captain.alive && alive / n < 0.55)) {
        g.routed = true;
        st.events.push({ t: st.t, text: `${g.name} 패주!`, side: g.side });
      }
    });
    const live = units.filter((u) => u.alive && !u.fled);
    for (const u of live) {
      u.flash = Math.max(0, u.flash - DT); u.lunge = Math.max(0, u.lunge - DT);
      u.skills.forEach((sk) => { sk.left -= DT; });
      u.moving = false;
      if (u.g.routed) {
        // 자기 진영 쪽 가장자리로 도주
        const dir = u.g.side === 0 && !u.g.flipped ? -1 : 1;
        u.x += dir * u.speed * 1.25 * DT; u.face = dir; u.moving = true;
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
            u.x += (dx / d) * u.speed * DT; u.y += (dy / d) * u.speed * DT; u.moving = true; u.face = dx >= 0 ? 1 : -1;
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
          const d = Math.abs(e.x - u.x) + Math.abs(e.y - u.y) * 1.4 + (e.captain ? -6 : 0) + (crowd ? Math.min(48, crowdOf(e, u) * 16) : 0);
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
        const p = slotPos(tg, u);
        if (p) { gx = p.x; gy = p.y; } else { gx = tg.x + u.slotSide * (reach + 14); gy = u.y; }
      }
      const ex = gx - u.x, ey = gy - u.y, ed = len2(ex, ey);
      if (md > reach || (melee && ed > 3)) {
        // 대장 근처로 모이려는 힘을 약간 섞는다 (부대 대형 유지) — 목표에 닿기 전까지만
        let mx = ex / (ed || 1), my = ey / (ed || 1);
        const cap = u.g.captain;
        if (md > reach && !u.captain && cap.alive) {
          const cx = cap.x - u.x, cy = cap.y - u.y, cd = len2(cx, cy);
          if (cd > 32) { mx += (cx / cd) * 0.45; my += (cy / cd) * 0.45; }
        }
        const ml = len2(mx, my) || 1;
        // 이미 닿은 채 자리를 고쳐 서는 중이면 천천히
        const v = u.speed * DT * (md > reach ? 1 : 0.5);
        const stepLen = Math.min(v, ed || v);
        u.x += (mx / ml) * stepLen; u.y += (my / ml) * stepLen;
        u.moving = stepLen > 0.2;
      } else if (basic.shot && d < reach * 0.45) {
        // 원거리 유닛은 너무 붙으면 물러난다
        u.x -= (dx / d) * u.speed * 0.6 * DT; u.y -= (dy / d) * u.speed * 0.3 * DT;
        u.moving = true;
      }
      if (md <= reach && basic.left <= 0) useSkill(st, u, basic, tg, live);
    }
    // 겹침 방지: 가로로 넓고 깊이(세로)로 얕은 타원 간격. 큰 도트가 한 덩어리로 뭉개지지 않게 한다.
    // 맞붙은 적끼리는 근접 사거리 안에 들어올 만큼만 떨어진다.
    for (let i = 0; i < live.length; i++) {
      const a = live[i];
      if (!a.alive) continue;
      for (let j = i + 1; j < live.length; j++) {
        const b = live[j];
        if (!b.alive) continue;
        const big = sizeOf(a) + sizeOf(b);
        const same = a.side === b.side;
        const mx = (same ? SEP_X : SEP_FOE_X) + big * 0.75, my = (same ? SEP_Y : SEP_FOE_Y) + big * 0.5;
        const ddx = (b.x - a.x) || (j % 2 ? 0.01 : -0.01), ddy = b.y - a.y;
        if (Math.abs(ddx) >= mx || Math.abs(ddy) >= my) continue;
        const nx = ddx / mx, ny = ddy / my;
        const nd2 = nx * nx + ny * ny;
        if (nd2 >= 1) continue;
        const nd = Math.sqrt(nd2);
        const push = (1 - nd) * 0.5;
        const ux = nx / nd, uy = ny / nd;
        a.x -= ux * push * mx; a.y -= uy * push * my * 0.8;
        b.x += ux * push * mx; b.y += uy * push * my * 0.8;
      }
    }
    live.forEach((u) => { u.y = clamp(u.y, TOP, BOTTOM); if (!u.g.routed) { const e = EDGE + sizeOf(u) * EDGE_BIG; u.x = clamp(u.x, e, W - e); } });
    // 투사체
    for (let i = st.shots.length - 1; i >= 0; i--) {
      const s = st.shots[i];
      const tx = s.to.x, ty = s.to.y - 9;
      const dd = len2(tx - s.x, ty - s.y);
      const stepLen = s.speed * DT;
      if (dd <= stepLen) {
        if (s.heal) mend(st, s.from, s.to, s.sk);
        else strike(st, s.from, s.to, s.sk);
        st.shots.splice(i, 1);
      } else {
        s.x += ((tx - s.x) / dd) * stepLen; s.y += ((ty - s.y) / dd) * stepLen;
      }
    }
    // 결판
    if (!st.over) {
      const a = sideActive(st, 0), b = sideActive(st, 1);
      if (!a || !b || st.t >= MAX_TIME) {
        st.over = true; st.endT = st.t;
        if (a && b) {
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
      bias = Math.sqrt(lo * hi);
    }
    return best;
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
  function triggerAttack(view, u, kind) {
    const r = rsOf(view, u);
    if (view.clock - r.atkAt < 0.12) return;
    r.atkAt = view.clock;
    r.atkAnim = kind || 'attack';
    const sh = useArt() && Art.sheetFor(u);
    // 시트의 동작 길이를 휘두르는 시간(0.28~0.5초)에 맞춰 늘이거나 줄인다
    r.atkDur = sh ? Math.max(0.28, Math.min(0.5, Art.anim(sh.meta, r.atkAnim).total / 1000)) : 0.3;
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

  // 지금 그릴 칸
  function pose(view, u, force) {
    const r = rsOf(view, u), c = view.clock;
    const sh = useArt() && Art.sheetFor(u);
    if (sh) {
      const m = sh.meta;
      let i, walkFx = false; // walkFx: 걷기 동작이 없는 시트가 걷는 중 → 그릴 때 걸음 흔들림을 덧붙인다
      if (force) { const a = Art.anim(m, force); i = Math.min(a.to, a.from + 1); }
      else if (!u.alive) i = Art.anim(m, 'hit').to;
      else if (c - r.atkAt < r.atkDur) { const a = Art.anim(m, r.atkAnim); i = frameAt(a, ((c - r.atkAt) / r.atkDur) * a.total, true); }
      else if (c - r.hitAt < 0.22) { const a = Art.anim(m, 'hit'); i = frameAt(a, ((c - r.hitAt) / 0.22) * a.total, true); }
      else if (u.moving) { i = frameAt(Art.anim(m, 'walk'), (c + r.phase) * 1000, false); walkFx = !m.anims.walk; }
      else i = frameAt(Art.anim(m, 'idle'), (c + r.phase) * 1000, false);
      const f = m.frames[i] || m.frames[0];
      const rc = sheetRecolor(sh, u);
      return { img: rc ? rc.img : sh.img, sx: f[0], sy: f[1], sw: m.cell[0], sh: m.cell[1], ax: m.anchor[0], ay: m.anchor[1], face: m.facing,
        key: `${rc ? rc.key : sh.id}#${i}`, sheet: sh, k: sheetK(u, sh), walkFx };
    }
    const walking = (u.moving && u.alive) || force === 'walk';
    const t = (c + r.phase) * 1000;
    if (u.mon) {
      const s = monScale(u);
      const frame = walking ? Math.floor(t / 180) % 2 : Math.floor(t / 420) % 2;
      const img = Sprites.monster(u.mon, s, frame, false);
      // 괴물 도안은 대부분 왼쪽을 본다
      return { img, sx: 0, sy: 0, sw: img.width, sh: img.height, ax: Math.round(img.width / 2), ay: 16 * s, face: -1, key: keyOfCanvas(img), unit: s };
    }
    const frame = walking ? (Math.floor(t / 160) % 2 ? 2 : 0) : Math.floor(t / 450) % 2;
    const img = Sprites.merc(u.look, SPR, frame, false);
    return { img, sx: 0, sy: 0, sw: img.width, sh: img.height, ax: 8 * SPR, ay: 15 * SPR, face: 1, key: keyOfCanvas(img), unit: SPR };
  }

  // 한 칸 그리기: (X, Y) 가 발 위치, flip 이면 좌우 반전
  // fr.k: 그리는 배율 (괴물 우두머리 시트 1.5 등, 기본 1)
  // tf: 걸음 흔들림 { bob: 들썩임(px), lean: 앞으로 기울기(발 기준 기울임), sx/sy: 눌림 } — 발은 땅에 붙인 채 몸만 움직인다
  function blit(ctx, fr, X, Y, flip, img, tf) {
    const src = img || fr.img, sx = img ? 0 : fr.sx, sy = img ? 0 : fr.sy;
    const k = fr.k || 1, dw = Math.round(fr.sw * k), dh = Math.round(fr.sh * k), ax = Math.round(fr.ax * k), ay = Math.round(fr.ay * k);
    if (tf) {
      ctx.save();
      ctx.translate(Math.round(X), Math.round(Y) - (tf.bob || 0));
      if (tf.lean) ctx.transform(1, 0, tf.lean, 1, 0, 0);
      ctx.scale((flip ? -1 : 1) * (tf.sx || 1), tf.sy || 1);
      ctx.drawImage(src, sx, sy, fr.sw, fr.sh, -ax, -ay, dw, dh);
      ctx.restore();
      return;
    }
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
    return { bg, fg: foreground(terrain), parts: [], sigils: [], slashes: [], vfx: [], amb: [], terrain, shake: 0, stop: 0, flash: 0, flashColor: '#ffffff',
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
        if (u) triggerAttack(view, u, f.shot && f.shot !== 'arrow' && f.shot !== 'dagger' ? 'cast' : 'attack');
      } else if (f.kind === 'cast') {
        const u = nearestUnit(st, f.x, f.y, (e) => e.alive);
        if (u) triggerAttack(view, u, 'cast');
      }
      const X = f.x * Z + edxOf(view, f.who);
      // 몸통 높이: 타격·폭발은 그림 키의 절반쯤
      const Y = f.foot != null && (f.kind === 'hit' || f.kind === 'boom') ? f.foot - Math.round(f.tall * 0.5) : f.y * Z;
      if (f.kind === 'hit') {
        spawn(view, f.big ? 12 : 4, X, Y, { sp: [40, f.big ? 160 : 90], life: [0.15, 0.35], color: f.color, size: f.big ? 3 : 2 });
        if (f.melee) view.slashes.push({ x: X, y: Y, dir: f.dir, t: 0, big: f.big, color: f.special ? '#9fd8ff' : '#ffffff' });
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
      if (u.lunge > r.prevLunge + 0.01) triggerAttack(view, u, 'attack');
      if (u.flash > r.prevFlash + 0.01) r.hitAt = view.clock;
      r.prevLunge = u.lunge; r.prevFlash = u.flash;
      const fr = pose(view, u);
      const S = stature(view, u);
      const face = u.face || (u.side === 0 ? 1 : -1);
      const flip = face !== fr.face;
      const X = Math.round(screenX(view, u, fr, flip, u.lunge > 0 ? face * 8 : 0)), Y = Math.round(u.y * Z);
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
      // 걷기 동작이 없는 시트: 두 걸음마다 1~2px 들썩이고, 발이 닿는 순간 살짝 눌리며, 가는 쪽으로 조금 기운다
      // (연출 시계 기준이라 타격 멈춤 동안은 함께 멈춘다)
      let tf = null;
      if (fr.walkFx) {
        const step = (((view.clock + r.phase) / 0.27) % 1 + 1) % 1;
        const land = step < 0.14 || step > 0.9;
        tf = { bob: Math.round(Math.sin(step * Math.PI) * 2), lean: -face * 0.05, sx: land ? 1.03 : 1, sy: land ? 0.97 : 1 };
      }
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
        ctx.globalAlpha = Math.max(0, 1 - k) * dim;
        const r = Math.round(s.r * (0.5 + k * 1.2) + 10);
        ctx.drawImage(glow(s.color, r), s.x - r, s.y - r);
        // 흰 섬광 핵: 대장 몸 위라면 더 옅게 (색 번짐·고리로 타격은 충분히 읽힌다)
        if (k < 0.3) {
          const w = Math.round(r * 0.8), a = ctx.globalAlpha;
          ctx.globalAlpha = a * (dim < 1 ? 0.55 : 1);
          ctx.drawImage(glow('#ffffff', w), s.x - w, s.y - w);
          ctx.globalAlpha = a;
        }
        ctx.strokeStyle = s.color; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.ellipse(s.x, s.y + 10, r * 1.1, r * 0.45, 0, 0, Math.PI * 2); ctx.stroke();
      } else if (s.dash) {
        ctx.globalAlpha = Math.max(0, 1 - s.t / 0.22);
        px(ctx, Math.round(s.x) - 30, Math.round(s.y), 60, 2, '#ffffff');
        px(ctx, Math.round(s.x) - 20, Math.round(s.y) - 6, 40, 1, '#ffffff');
      } else {
        // 초승달 모양 베기 궤적
        const k = s.t / 0.22, R = s.big ? 22 : 15;
        ctx.globalAlpha = Math.max(0, 1 - k);
        ctx.strokeStyle = s.color; ctx.lineWidth = s.big ? 4 : 2;
        const a0 = s.dir > 0 ? -1.4 : Math.PI - 0.6, sweep = 2.0 * Math.min(1, k * 3);
        ctx.beginPath(); ctx.arc(s.x - s.dir * 6, s.y, R, a0, a0 + sweep * (s.dir > 0 ? 1 : 1)); ctx.stroke();
        ctx.lineWidth = 1; ctx.globalAlpha *= 0.6;
        ctx.beginPath(); ctx.arc(s.x - s.dir * 6, s.y, R - 4, a0 + 0.2, a0 + sweep); ctx.stroke();
      }
    });
    ctx.globalAlpha = 1;

    drawVfx(ctx, view, now);

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
  function rosterRow(g) {
    const row = document.createElement('div');
    row.className = 'troop';
    const sw = document.createElement('span'); sw.className = 'troop-sw'; sw.style.background = g.color;
    const nm = document.createElement('span'); nm.className = 'troop-name'; nm.textContent = g.name;
    const bar = document.createElement('span'); bar.className = 'troop-bar';
    const fill = document.createElement('i'); bar.append(fill);
    const cnt = document.createElement('span'); cnt.className = 'troop-cnt';
    row.append(sw, nm, bar, cnt);
    if (g.player) row.classList.add('mine');
    return { row, fill, cnt, nm };
  }

  function play(report, onDone) {
    stop();
    const q = report.quest;
    const won = report.outcome === 'great' || report.outcome === 'success';
    const groups = plan(report);
    const seed = report.seed || q.id * 7919 + 17;
    const found = findBattle(groups, report.outcome, seed);
    const st = setup(groups, found.bias, found.seed);

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
    const rows = st.groups.map((g) => { const r = rosterRow(g); cols[g.side].append(r.row); return r; });
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
      else { acc += dt * speeds[speedIdx] * 1.3; view.clock += dt * Math.min(2, speeds[speedIdx]) * 1.3; }
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

  return { play, stop, plan, simulate, findBattle };
})();
