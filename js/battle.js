// 실시간 집단 전투
// 용병대장 1 + 대원 3~8로 이루어진 부대 6~10개가 전장에서 스스로 판단해 싸운다.
// 의뢰의 결과(대성공/성공/실패/대실패)는 판정에서 정해지고, 전투는 시드를 바꿔 가며 실제로
// 시뮬레이션해 그 결과가 나오는 판을 찾아 재생한다. 연출을 위해 짜 맞춘 각본은 없다.
'use strict';

const Battle = (() => {
  const W = 320, H = 180;
  const TOP = 84, BOTTOM = 172;      // 전장의 위·아래 경계 (유닛 발 위치)
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

  const BG = {
    plains: { sky: ['#6fa0e8', '#9cc4f0'], ground: '#6fa84a', dark: '#4a7a30', deco: 'grass' },
    forest: { sky: ['#2f5a4a', '#4a7a5a'], ground: '#2f5a2a', dark: '#1f3a1a', deco: 'tree' },
    swamp:  { sky: ['#4a5a4a', '#6a7a6a'], ground: '#3f4a30', dark: '#2a3320', deco: 'reed' },
    desert: { sky: ['#e8a85a', '#f2d29a'], ground: '#d9b46a', dark: '#b08a48', deco: 'cactus' },
    frost:  { sky: ['#7a9ac8', '#c8dcf0'], ground: '#e8eef2', dark: '#b0bcc8', deco: 'peak' },
    dragon: { sky: ['#3a1414', '#7a2a1a'], ground: '#4a2a20', dark: '#2e1a14', deco: 'lava' },
  };

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
  function px(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }

  function background(region) {
    const b = document.createElement('canvas'); b.width = W; b.height = H;
    const c = b.getContext('2d');
    const bg = BG[region] || BG.plains;
    for (let i = 0; i < 5; i++) px(c, 0, i * 12, W, 12, i < 3 ? bg.sky[0] : bg.sky[1]);
    for (let i = 0; i < 5; i++) px(c, 0, 30 + i * 2, W, 1, bg.sky[1]);
    const horizon = 62;
    for (let x = 0; x < W; x++) {
      const h = Math.round(8 + Math.sin(x / 23) * 5 + Math.sin(x / 7) * 2);
      px(c, x, horizon - h, 1, h, bg.dark);
    }
    px(c, 0, horizon, W, H - horizon, bg.ground);
    for (let i = 0; i < 260; i++) {
      const x = (i * 37) % W, y = horizon + ((i * 53) % (H - horizon));
      px(c, x, y, 2, 1, bg.dark);
    }
    for (let i = 0; i < 8; i++) {
      const x = 8 + i * 40 + ((i * 17) % 13), y = horizon;
      if (bg.deco === 'tree') {
        px(c, x + 3, y - 8, 2, 8, '#5a3a20');
        px(c, x, y - 18, 8, 10, '#1f4a1f'); px(c, x + 1, y - 22, 6, 4, '#2f6a2a'); px(c, x + 2, y - 17, 2, 2, '#4a8a3a');
      } else if (bg.deco === 'cactus') {
        if (i % 2) { px(c, x + 3, y - 12, 3, 12, '#4a8a3a'); px(c, x, y - 8, 3, 2, '#4a8a3a'); px(c, x, y - 10, 2, 3, '#4a8a3a'); px(c, x + 6, y - 6, 3, 2, '#4a8a3a'); }
      } else if (bg.deco === 'peak') {
        for (let k = 0; k < 10; k++) px(c, x + 10 - k, y - 18 + k * 2, k * 2 + 1, 2, k < 3 ? '#ffffff' : '#8a9ab8');
      } else if (bg.deco === 'reed') {
        px(c, x, y - 6, 1, 6, '#6a7a3a'); px(c, x + 2, y - 8, 1, 8, '#6a7a3a'); px(c, x + 2, y - 10, 1, 3, '#8a5a2b');
        px(c, x + 12, y + 40, 14, 3, '#2a3a3a');
      } else if (bg.deco === 'lava') {
        px(c, x, y + 30 + (i % 3) * 25, 12, 2, '#e85a20'); px(c, x + 2, y + 31 + (i % 3) * 25, 6, 1, '#f2c94c');
      } else if (i % 2) {
        px(c, x, y + 10, 1, 2, '#8ac85a'); px(c, x + 2, y + 9, 1, 3, '#8ac85a'); px(c, x + 30, y + 70, 2, 2, '#f2c94c');
      }
    }
    return b;
  }

  // ───────── 부대 편성 ─────────
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

    // 아군: 파견된 용병단
    (report.companies || []).forEach((c) => {
      if (c.own && c.members) {
        const ms = [...c.members].sort((a, b) => (b.leader ? 1 : 0) - (a.leader ? 1 : 0) || b.level - a.level);
        const units = ms.map((m) => ({ look: m.look, cls: m.cls, str: (0.85 + m.level * 0.035) * (m.leader ? 1.15 : 1), named: m.name, doomed: deadIds.has(m.id), sk: m.sk, unique: m.unique, art: m.art }));
        // 대원이 셋이 안 되면 수습 용병이 머릿수를 채운다
        looksFor(c.color, Math.max(0, 4 - units.length)).forEach((lk) => units.push({ look: lk, cls: lk.cls, str: 0.7, recruit: true }));
        groups.push({ side: 0, name: c.name, color: c.color, player: true, units: units.slice(0, 9) });
      } else if (!c.own) {
        const n = clamp(c.size || 5, 4, 9);
        const units = [{ look: c.look, cls: c.look.cls, str: 0.9 + c.level * 0.03 }];
        looksFor(c.color, n - 1).forEach((lk) => units.push({ look: lk, cls: lk.cls, str: 0.8 + c.level * 0.025 }));
        groups.push({ side: 0, name: c.name, color: c.color, player: true, ext: true, betray: c.betrayed, units });
      }
    });
    if (!groups.length) {
      // 옛 보고서 호환: 단원 목록만 있는 경우
      const units = (report.members || []).map((m) => ({ look: m.look, cls: m.cls, str: 1, named: m.name, doomed: m.dead }));
      looksFor('#3d5a9c', Math.max(0, 4 - units.length)).forEach((lk) => units.push({ look: lk, cls: lk.cls, str: 0.7, recruit: true }));
      groups.push({ side: 0, name: '길드 용병단', color: '#3d5a9c', player: true, units });
    }

    // 부대 수: 6~10 (결전·최종전은 많게)
    const big = q.campaign || q.final;
    const total = clamp(6 + Math.floor(q.level / 4) + (big ? 2 : 0) + (q.boss ? 1 : 0), 6, 10);
    const enemyN = Math.ceil(total / 2);
    const allyFill = Math.max(0, total - enemyN - groups.length);

    // 아군 지원 부대: 의뢰주 세력의 병사들
    const issuer = q.issuer;
    const ally = FACTIONS[issuer] && !FACTIONS[issuer].neutral ? issuer : null;
    for (let i = 0; i < allyFill; i++) {
      const f = ally || 'locals';
      const n = rInt(r, 4, 7);
      const units = Array.from({ length: n }, (_, k) => {
        const lk = UI.h.soldierLook(f, rInt(r, 0, 99) + k);
        return { look: lk, cls: lk.cls, str: ally ? 0.85 : 0.65 };
      });
      groups.push({ side: 0, name: ally ? `${FACTIONS[f].short} ${FACTIONS[f].unitName}` : '마을 자경단', color: FACTIONS[f].color, units });
    }

    // 적군
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
        const n = rInt(r, 3, Math.min(8, 3 + Math.floor(q.level / 2)));
        for (let k = 0; k < n; k++) {
          const m = minion();
          units.push({ mon: m, scale: ENEMIES[m] && ENEMIES[m].big ? 2 : 1, str: 1, bigMon: !!(ENEMIES[m] && ENEMIES[m].big) });
        }
        groups.push({ side: 1, name: ldef.boss ? lead : `${lead} 무리`, color: cal ? FACTIONS[cal].color : '#7a2430', units });
      }
    } else {
      const f = q.target || q.issuer;
      for (let i = 0; i < enemyN; i++) {
        const n = rInt(r, 4, Math.min(9, 4 + Math.floor(q.level / 2)));
        const units = Array.from({ length: n }, (_, k) => {
          const lk = UI.h.soldierLook(f, rInt(r, 0, 99) + k);
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
        // 부대가 넷 이상이면 앞뒤 두 줄로 포진
        const cols = list.length > 3 ? 2 : 1;
        const col = i % cols, rowIdx = Math.floor(i / cols), inCol = Math.ceil((list.length - col) / cols);
        const cy = TOP + 6 + ((BOTTOM - TOP - 12) * (rowIdx + 0.5)) / inCol;
        const cx = side === 0 ? 66 - col * 38 : W - 66 + col * 38;
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
          // 대형: 대장이 가운데, 대원은 3열로 앞뒤에 선다
          const fwd = side === 0 ? 1 : -1;
          const fcol = captain ? 0 : Math.floor((k - 1) / 3);
          const row = captain ? 1 : (k - 1) % 3;
          const ox = captain ? -fwd * 4 : fwd * (8 - fcol * 12);
          const oy = (row - 1) * 10;
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
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  const sizeOf = (u) => (u.scale > 1 ? u.scale * 4 : 0);
  const buffSum = (u, k, t) => u.buffs.reduce((a, b) => a + (b.until > t ? (b[k] || 0) : 0), 0);
  const atkMul = (u, t) => {
    const cap = u.g.captain;
    const aura = cap.alive && cap !== u && Math.hypot(cap.x - u.x, cap.y - u.y) < 60 ? 1.1 : 1; // 대장 곁의 대원은 힘이 난다
    return (1 + buffSum(u, 'atk', t)) * aura;
  };
  const defMul = (u, t) => 1 - Math.min(0.6, buffSum(u, 'def', t));

  function addBuff(st, u, b) { if (b) u.buffs.push({ atk: b.atk || 0, def: b.def || 0, until: st.t + b.dur }); }

  function damage(st, target, dmg, crit) {
    if (!target.alive) return 0;
    dmg *= defMul(target, st.t);
    target.hp -= dmg;
    target.flash = 0.18;
    st.fx.push({ kind: 'pop', x: target.x, y: target.y - 18, text: String(Math.round(dmg)), crit, ally: target.side === 0, t: 0 });
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
      dealt += damage(st, e, d, crit && e === t);
      if (sk.stun && e.alive) e.stunUntil = Math.max(e.stunUntil, st.t + sk.stun * (e.boss ? 0.3 : e.bigMon ? 0.6 : 1));
    });
    if (sk.aoe) st.fx.push({ kind: 'boom', x: t.x, y: t.y - 8, r: sk.aoe, t: 0, color: sk.shot === 'curse' ? '#9b6ad6' : sk.shot === 'bolt' ? '#7fd6e8' : '#f39c12' });
    if (sk.drain && u.alive) u.hp = Math.min(u.maxHp, u.hp + dealt * sk.drain);
    if (sk.selfBuff) addBuff(st, u, sk.selfBuff);
  }

  function mend(st, u, t, sk) {
    const list = sk.aoe ? st.units.filter((a) => a.alive && !a.fled && a.side === u.side && dist(a, t) <= sk.aoe) : [t];
    list.forEach((a) => {
      if (!a.alive) return;
      a.hp = Math.min(a.maxHp, a.hp + u.healPow * sk.heal * (0.9 + st.r() * 0.2));
      st.fx.push({ kind: 'heal', x: a.x, y: a.y - 14, t: 0 });
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
    const reach = (sk.dash ? Math.max(sk.range, 60) : sk.range);
    let best = null, bd = Infinity;
    for (const e of live) {
      if (e.side === u.side || e.g.routed) continue;
      const d = dist(e, u) - sizeOf(e);
      if (d <= reach && d < bd) { bd = d; best = e; }
    }
    return best;
  }

  function useSkill(st, u, sk, t, live) {
    sk.left = sk.cd * (0.9 + st.r() * 0.2);
    if (sk !== u.skills[0] && (u.named || u.captain || u.boss)) st.fx.push({ kind: 'label', x: u.x, y: u.y - 26, text: sk.name, t: 0, side: u.side });
    // 아군 대장·특별 용병의 특기는 컷인으로 보여 준다
    if (sk !== u.skills[0] && u.unique && u.side === 0) st.cutins.push({ t: st.t, name: u.named, skill: sk.name, art: u.art, look: u.look });
    if (sk.tgt === 'self') {
      st.units.filter((a) => a.alive && !a.fled && a.side === u.side && dist(a, u) <= sk.aoe).forEach((a) => addBuff(st, a, sk.buff));
      st.fx.push({ kind: 'ring', x: u.x, y: u.y - 6, r: sk.aoe, t: 0, color: sk.buff.def ? '#7fd6e8' : '#ef6a6a' });
      return;
    }
    if (sk.tgt === 'hurt') {
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
    if (sk.dash) {
      // 돌진: 대상 곁으로 뛰어든다
      const d = dist(u, t) || 1;
      const stop = 8 + sizeOf(t);
      if (d > stop) { u.x = t.x - ((t.x - u.x) / d) * stop; u.y = t.y - ((t.y - u.y) / d) * stop; }
      st.fx.push({ kind: 'dash', x: u.x, y: u.y - 6, t: 0 });
    }
    u.face = t.x >= u.x ? 1 : -1;
    targets.forEach((e) => {
      if (sk.shot) st.shots.push({ kind: sk.shot, from: u, to: e, x: u.x, y: u.y - 9, sk, speed: 170 });
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
            const dx = foe.x - u.x, dy = foe.y - u.y, d = Math.hypot(dx, dy) || 1;
            u.x += (dx / d) * u.speed * DT; u.y += (dy / d) * u.speed * DT; u.moving = true; u.face = dx >= 0 ? 1 : -1;
          }
        }
        continue;
      }
      // 목표 재선정: 가까운 적, 같은 높이(전열)를 조금 더 선호
      u.retarget -= DT;
      if (!u.target || !u.target.alive || u.target.fled || u.target.side === u.side || u.target.g.routed || u.retarget <= 0) {
        u.retarget = 0.4 + r() * 0.3;
        let best = null, bd = Infinity;
        for (const e of live) {
          if (e.side === u.side || e.g.routed) continue;
          const d = Math.abs(e.x - u.x) + Math.abs(e.y - u.y) * 1.4 + (e.captain ? -6 : 0);
          if (d < bd) { bd = d; best = e; }
        }
        u.target = best;
      }
      const tg = u.target;
      if (!tg) continue;
      const dx = tg.x - u.x, dy = tg.y - u.y, d = Math.hypot(dx, dy) || 1;
      u.face = dx >= 0 ? 1 : -1;
      const reach = basic.range + sizeOf(tg);
      if (d > reach) {
        // 대장 근처로 모이려는 힘을 약간 섞는다 (부대 대형 유지)
        let mx = dx / d, my = dy / d;
        const cap = u.g.captain;
        if (!u.captain && cap.alive) {
          const cx = cap.x - u.x, cy = cap.y - u.y, cd = Math.hypot(cx, cy);
          if (cd > 26) { mx += (cx / cd) * 0.45; my += (cy / cd) * 0.45; }
        }
        const ml = Math.hypot(mx, my) || 1;
        u.x += (mx / ml) * u.speed * DT; u.y += (my / ml) * u.speed * DT;
        u.moving = true;
      } else if (basic.shot && d < reach * 0.45) {
        // 원거리 유닛은 너무 붙으면 물러난다
        u.x -= (dx / d) * u.speed * 0.6 * DT; u.y -= (dy / d) * u.speed * 0.3 * DT;
        u.moving = true;
      }
      if (d <= reach && basic.left <= 0) useSkill(st, u, basic, tg, live);
    }
    // 겹침 방지
    for (let i = 0; i < live.length; i++) {
      const a = live[i];
      if (!a.alive) continue;
      for (let j = i + 1; j < live.length; j++) {
        const b = live[j];
        if (!b.alive) continue;
        const ddx = b.x - a.x, ddy = b.y - a.y;
        const min = 7 + sizeOf(a) * 0.75 + sizeOf(b) * 0.75;
        if (Math.abs(ddx) > min || Math.abs(ddy) > min) continue;
        const dd = Math.hypot(ddx, ddy) || 0.01;
        if (dd >= min) continue;
        const push = (min - dd) * 0.5;
        const nx = ddx / dd, ny = ddy / dd;
        a.x -= nx * push; a.y -= ny * push * 0.8;
        b.x += nx * push; b.y += ny * push * 0.8;
      }
    }
    live.forEach((u) => { u.y = clamp(u.y, TOP, BOTTOM); if (!u.g.routed) u.x = clamp(u.x, 6, W - 6); });
    // 투사체
    for (let i = st.shots.length - 1; i >= 0; i--) {
      const s = st.shots[i];
      const tx = s.to.x, ty = s.to.y - 9;
      const dd = Math.hypot(tx - s.x, ty - s.y);
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
  function findBattle(groups, outcome, seed) {
    const want = outcome === 'great' || outcome === 'success';
    let bias = want ? (outcome === 'great' ? 0.7 : 0.95) : outcome === 'fail' ? 1.15 : 1.35;
    let lo = 0.1, hi = 6;
    let best = null;
    for (let i = 0; i < 16; i++) {
      const s = seed + i * 101;
      const res = simulate(groups, bias, s);
      const ok = res.won === want
        && (outcome !== 'great' || res.loss <= 0.25)
        && (outcome !== 'success' || res.loss > 0.05 || i > 4)
        && (outcome !== 'disaster' || res.loss >= 0.5);
      if (ok) return { bias, seed: s, res };
      if (!best || res.won === want) best = { bias, seed: s, res };
      // 아군이 이겨야 하는데 졌거나, 대성공인데 피해가 크면 적을 약하게
      const weaker = want ? (!res.won || (outcome === 'great' && res.loss > 0.25)) : false;
      const stronger = !want ? (res.won || (outcome === 'disaster' && res.loss < 0.5)) : (outcome === 'success' && res.loss <= 0.05);
      if (weaker) hi = bias; else if (stronger) lo = bias;
      bias = Math.sqrt(lo * hi);
    }
    return best;
  }

  // ───────── 그리기 ─────────
  function spriteOf(u, now) {
    const walking = u.moving && u.alive;
    if (u.mon) {
      const frame = walking ? Math.floor(now / 180 + u.walk) % 2 : Math.floor(now / 420 + u.walk) % 2;
      return Sprites.monster(u.mon, u.scale || 1, frame, u.flash > 0.08);
    }
    const frame = walking ? (Math.floor(now / 160 + u.walk) % 2 ? 2 : 0) : Math.floor(now / 450 + u.walk) % 2;
    return Sprites.merc(u.look, 1, frame, u.face < 0);
  }

  function draw(ctx, bg, st, now, label) {
    ctx.drawImage(bg, 0, 0);
    // 쓰러진 유닛 먼저
    const sorted = [...st.units].filter((u) => !u.fled).sort((a, b) => (a.alive - b.alive) || a.y - b.y);
    for (const u of sorted) {
      const img = spriteOf(u, now);
      const lx = u.lunge > 0 ? u.face * 3 : 0;
      const x = Math.round(u.x - img.width / 2 + lx), y = Math.round(u.y - img.height);
      if (!u.alive) {
        const dt = st.t - u.downAt;
        ctx.globalAlpha = dt < 0.4 ? (Math.floor(dt * 12) % 2 ? 0.3 : 0.9) : 0.28;
        ctx.drawImage(img, x, y + 3);
        ctx.globalAlpha = 1;
        if (u.doomed && dt > 0.4) ctx.drawImage(Sprites.icon('skull', 1), Math.round(u.x - 4), y - 6);
        continue;
      }
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fillRect(Math.round(u.x - img.width * 0.3), Math.round(u.y) - 1, Math.round(img.width * 0.6), 2);
      if (u.flash > 0 && !u.mon && Math.floor(u.flash * 30) % 2) ctx.globalAlpha = 0.4;
      ctx.drawImage(img, x, y);
      ctx.globalAlpha = 1;
      // 대장: 부대 깃발
      if (u.captain) {
        const fl = Sprites.flag(u.g.color, u.g.side === 0 ? '#f2c94c' : '#1b1420', 1);
        ctx.drawImage(fl, Math.round(u.x + (u.mon ? img.width / 2 - 6 : 3)), y - 9);
      }
      // 체력 바 (대장, 또는 다친 유닛)
      if (u.captain || u.hp < u.maxHp) {
        const bw = u.captain ? 14 : 10;
        const bx = Math.round(u.x - bw / 2), by = y - 3;
        px(ctx, bx - 1, by - 1, bw + 2, 3, '#1b1420');
        px(ctx, bx, by, Math.max(0, Math.round(bw * (u.hp / u.maxHp))), 1, u.side === 0 ? '#7ed37e' : '#ef6a6a');
      }
      // 기절·강화 표시
      if (u.stunUntil > st.t) { const k = Math.floor(now / 120) % 3; px(ctx, Math.round(u.x) - 4 + k * 3, y - 6, 2, 2, '#f2c94c'); }
      if (buffSum(u, 'atk', st.t) > 0) px(ctx, Math.round(u.x) + 5, y + 2, 2, 2, '#ef6a6a');
      if (buffSum(u, 'def', st.t) > 0) px(ctx, Math.round(u.x) - 7, y + 2, 2, 2, '#7fd6e8');
      // 패주 표시
      if (u.g.routed && Math.floor(now / 250) % 2) px(ctx, Math.round(u.x) - 1, y - 7, 2, 4, '#ffffff');
    }
    // 투사체
    st.shots.forEach((s) => {
      const dir = s.to.x >= s.x ? 1 : -1;
      if (s.kind === 'arrow') { px(ctx, s.x - 3, s.y, 6, 1, '#e8e4d8'); px(ctx, dir > 0 ? s.x + 2 : s.x - 3, s.y - 1, 1, 3, '#d6dde4'); }
      else if (s.kind === 'fire') { px(ctx, s.x - 2, s.y - 2, 4, 4, '#f39c12'); px(ctx, s.x - 1, s.y - 1, 2, 2, '#f2c94c'); px(ctx, s.x - 2 - dir * 3, s.y, 3, 1, '#e74c3c'); }
      else if (s.kind === 'curse') { px(ctx, s.x - 2, s.y - 2, 4, 4, '#9b6ad6'); px(ctx, s.x - 1, s.y - 1, 2, 2, '#d0b0f0'); }
      else if (s.kind === 'bolt') { px(ctx, s.x - 3, s.y - 1, 6, 2, '#7fd6e8'); px(ctx, s.x - 1, s.y - 1, 2, 2, '#ffffff'); }
      else if (s.kind === 'dagger') { px(ctx, s.x - 2, s.y, 4, 1, '#d6dde4'); px(ctx, s.x - dir * 2, s.y - 1, 1, 3, '#8a5a2b'); }
      else { px(ctx, s.x, s.y - 2, 1, 5, '#fff4b0'); px(ctx, s.x - 2, s.y, 5, 1, '#fff4b0'); }
    });
    // 효과
    ctx.font = '8px Galmuri11, monospace';
    ctx.textAlign = 'center';
    st.fx.forEach((f) => {
      if (f.kind === 'pop') {
        if (!f.crit && !f.ally) return; // 화면이 어지럽지 않게 치명타와 아군 피해만
        const y = f.y - f.t * 18;
        ctx.fillStyle = '#1b1420'; ctx.fillText(f.text, f.x + 1, y + 1);
        ctx.fillStyle = f.ally ? '#ef6a6a' : '#f2c94c'; ctx.fillText(f.text, f.x, y);
      } else if (f.kind === 'heal') {
        const y = Math.round(f.y - f.t * 12);
        px(ctx, f.x - 1, y - 3, 2, 6, '#7ed37e'); px(ctx, f.x - 3, y - 1, 6, 2, '#7ed37e');
      } else if (f.kind === 'boom') {
        const k = Math.round(Math.min(f.r || 12, 2 + f.t * 40));
        ctx.globalAlpha = Math.max(0, 1 - f.t * 2.5);
        px(ctx, f.x - k, f.y - k / 2, k * 2, k, f.color || '#f39c12');
        px(ctx, f.x - k / 2, f.y - k / 4, k, k / 2, '#f2c94c');
        ctx.globalAlpha = 1;
      } else if (f.kind === 'ring') {
        const k = Math.round(f.r * Math.min(1, 0.3 + f.t * 3));
        ctx.globalAlpha = Math.max(0, 1 - f.t * 1.6);
        ctx.strokeStyle = f.color; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.ellipse(f.x, f.y + 6, k, k * 0.45, 0, 0, Math.PI * 2); ctx.stroke();
        ctx.globalAlpha = 1;
      } else if (f.kind === 'dash') {
        ctx.globalAlpha = Math.max(0, 1 - f.t * 4);
        px(ctx, f.x - 8, f.y, 16, 1, '#ffffff');
        ctx.globalAlpha = 1;
      } else if (f.kind === 'label') {
        const y = Math.round(f.y - f.t * 10);
        ctx.fillStyle = '#1b1420'; ctx.fillText(f.text, f.x + 1, y + 1);
        ctx.fillStyle = f.side === 0 ? '#f2c94c' : '#ef9a9a'; ctx.fillText(f.text, f.x, y);
      }
    });
    if (label) {
      ctx.font = 'bold 20px Galmuri11, monospace';
      ctx.fillStyle = '#1b1420'; ctx.fillText(label.text, W / 2 + 2, 54);
      ctx.fillStyle = label.good ? '#f2c94c' : '#ef6a6a'; ctx.fillText(label.text, W / 2, 52);
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
    cvs.width = W; cvs.height = H; cvs.className = 'battle-canvas';
    const ctx = cvs.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const bg = background(TERRAIN[PROVINCES[q.province].terrain].bg);

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
      acc += dt * speeds[speedIdx] * 1.3;
      while (acc >= DT) {
        acc -= DT;
        step(st);
        st.fx.forEach((f) => { f.t += DT; });
        st.fx = st.fx.filter((f) => f.t < (f.kind === 'label' ? 1.2 : 0.7));
      }
      // 컷인: 너무 잦지 않게 1.3초 간격
      if (st.cutins.length > cutShown && now - lastCut > 1300) {
        showCutin(st.cutins[st.cutins.length - 1]);
        cutShown = st.cutins.length; lastCut = now;
      } else if (st.cutins.length > cutShown && now - lastCut <= 1300) cutShown = st.cutins.length;
      const ended = st.over && st.t - st.endT > 0.6;
      draw(ctx, bg, st, now, ended ? { text: labelText, good: won } : null);
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
