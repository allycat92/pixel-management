// 의뢰 결과 전투 연출 (결과는 이미 정해져 있고, 그것을 도트 애니메이션으로 보여준다)
'use strict';

const Battle = (() => {
  const W = 256, H = 144;
  const STEP = 650, END = 1500;
  const RANGED = { archer: 'arrow', mage: 'fire', cleric: 'holy' };
  const BG = {
    plains: { sky: ['#6fa0e8', '#9cc4f0'], ground: '#6fa84a', dark: '#4a7a30', deco: 'grass' },
    forest: { sky: ['#2f5a4a', '#4a7a5a'], ground: '#2f5a2a', dark: '#1f3a1a', deco: 'tree' },
    swamp:  { sky: ['#4a5a4a', '#6a7a6a'], ground: '#3f4a30', dark: '#2a3320', deco: 'reed' },
    desert: { sky: ['#e8a85a', '#f2d29a'], ground: '#d9b46a', dark: '#b08a48', deco: 'cactus' },
    frost:  { sky: ['#7a9ac8', '#c8dcf0'], ground: '#e8eef2', dark: '#b0bcc8', deco: 'peak' },
    dragon: { sky: ['#3a1414', '#7a2a1a'], ground: '#4a2a20', dark: '#2e1a14', deco: 'lava' },
  };
  const P_POS = [[78, 106], [54, 94], [54, 122], [30, 108]];
  const E_POS = [[178, 106], [204, 92], [206, 122]];

  let raf = null;

  function px(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }

  function background(region) {
    const b = document.createElement('canvas'); b.width = W; b.height = H;
    const c = b.getContext('2d');
    const bg = BG[region] || BG.plains;
    // 하늘 (계단식 그라데이션)
    for (let i = 0; i < 6; i++) px(c, 0, i * 12, W, 12, i < 3 ? bg.sky[0] : bg.sky[1]);
    for (let i = 0; i < 6; i++) px(c, 0, 33 + i * 2, W, 1, bg.sky[1]);
    const horizon = 72;
    // 먼 언덕
    for (let x = 0; x < W; x++) {
      const h = Math.round(8 + Math.sin(x / 23) * 5 + Math.sin(x / 7) * 2);
      px(c, x, horizon - h, 1, h, bg.dark);
    }
    px(c, 0, horizon, W, H - horizon, bg.ground);
    // 바닥 질감
    for (let i = 0; i < 160; i++) {
      const x = (i * 37) % W, y = horizon + ((i * 53) % (H - horizon));
      px(c, x, y, 2, 1, bg.dark);
    }
    // 지역 장식
    for (let i = 0; i < 6; i++) {
      const x = 10 + i * 45 + ((i * 17) % 13), y = horizon;
      if (bg.deco === 'tree') {
        px(c, x + 3, y - 8, 2, 8, '#5a3a20');
        px(c, x, y - 18, 8, 10, '#1f4a1f'); px(c, x + 1, y - 22, 6, 4, '#2f6a2a'); px(c, x + 2, y - 17, 2, 2, '#4a8a3a');
      } else if (bg.deco === 'cactus') {
        if (i % 2) { px(c, x + 3, y - 12, 3, 12, '#4a8a3a'); px(c, x, y - 8, 3, 2, '#4a8a3a'); px(c, x, y - 10, 2, 3, '#4a8a3a'); px(c, x + 6, y - 6, 3, 2, '#4a8a3a'); }
      } else if (bg.deco === 'peak') {
        for (let k = 0; k < 10; k++) px(c, x + 10 - k, y - 18 + k * 2, k * 2 + 1, 2, k < 3 ? '#ffffff' : '#8a9ab8');
      } else if (bg.deco === 'reed') {
        px(c, x, y - 6, 1, 6, '#6a7a3a'); px(c, x + 2, y - 8, 1, 8, '#6a7a3a'); px(c, x + 2, y - 10, 1, 3, '#8a5a2b');
        px(c, x + 12, y + 20, 14, 3, '#2a3a3a');
      } else if (bg.deco === 'lava') {
        px(c, x, y + 30 + (i % 3) * 10, 12, 2, '#e85a20'); px(c, x + 2, y + 31 + (i % 3) * 10, 6, 1, '#f2c94c');
      } else if (i % 2) {
        px(c, x, y + 10, 1, 2, '#8ac85a'); px(c, x + 2, y + 9, 1, 3, '#8ac85a'); px(c, x + 30, y + 40, 2, 2, '#f2c94c');
      }
    }
    return b;
  }

  // 결과에 맞는 전투 각본 만들기
  function buildScript(won, party, enemies) {
    const acts = [];
    const alive = (arr) => arr.filter((e) => !e.willDie);
    const hitParty = (forceDead) => {
      const targets = forceDead ? party.filter((p) => p.dead && !p.willDie) : party.filter((p) => !p.willDie);
      if (!targets.length) return;
      const to = forceDead ? targets[0] : (targets.find((p) => p.injured && !p.hitOnce) || pick(targets));
      to.hitOnce = true;
      const from = pick(enemies.filter((e) => !e.willDie).length ? enemies.filter((e) => !e.willDie) : enemies);
      const kill = !!forceDead;
      if (kill) to.willDie = true;
      to.hpTarget = kill ? 0 : Math.max(0.15, (to.hpTarget ?? 1) - (to.injured ? 0.45 : 0.2));
      acts.push({ from, to, hp: to.hpTarget, kill, dmg: rand(8, 25) * (kill ? 2 : 1) });
    };
    const fighters = party.filter((p) => !p.dead);
    const attackers = fighters.length ? fighters : party;
    if (won) {
      let k = 0;
      enemies.forEach((e) => {
        for (let h = 0; h < 2; h++) {
          const kill = h === 1;
          if (kill) e.willDie = true;
          acts.push({ from: attackers[k++ % attackers.length], to: e, hp: kill ? 0 : 0.45, kill, dmg: rand(20, 45) * (kill ? 2 : 1) });
          if (k % 2 === 0 && alive(enemies).length) hitParty(false);
        }
      });
    } else {
      for (let i = 0; i < 3; i++) {
        const e = pick(enemies);
        e.hpTarget = Math.max(0.35, (e.hpTarget ?? 1) - 0.2);
        acts.push({ from: attackers[i % attackers.length], to: e, hp: e.hpTarget, kill: false, dmg: rand(10, 30) });
        hitParty(false);
      }
      hitParty(false);
      party.filter((p) => p.dead).forEach(() => hitParty(true));
    }
    return acts;
  }

  function drawEntity(ctx, e, t) {
    if (e.alpha <= 0) return;
    ctx.globalAlpha = e.alpha;
    const flash = e.flash > 0;
    let img;
    if (e.kind === 'p') img = Sprites.merc(e.look, 2, e.frame, e.flip);
    else img = Sprites.monster(e.name, e.scale, e.frame, flash);
    const x = Math.round(e.x + e.ox), y = Math.round(e.y - img.height + e.oy);
    // 그림자
    ctx.fillStyle = 'rgba(0,0,0,0.25)';
    ctx.fillRect(x + img.width * 0.2, Math.round(e.y) - 2, img.width * 0.6, 3);
    // 아군이 맞으면 깜빡임
    if (flash && e.kind === 'p' && e.flash % 2) ctx.globalAlpha = 0.25 * e.alpha;
    ctx.drawImage(img, x, y);
    ctx.globalAlpha = 1;
    // 체력 바
    if (e.hpShow !== undefined && e.alpha > 0.3) {
      const bw = e.kind === 'e' ? Math.min(30, img.width - 4) : 22;
      const bx = x + (img.width - bw) / 2, by = y - 5;
      px(ctx, bx - 1, by - 1, bw + 2, 4, '#1b1420');
      px(ctx, bx, by, bw, 2, '#4a2a2a');
      px(ctx, bx, by, Math.round(bw * e.hpShow), 2, e.kind === 'e' ? '#ef6a6a' : '#7ed37e');
    }
  }

  function play(report, onDone) {
    stop();
    const q = report.quest;
    const won = report.outcome === 'great' || report.outcome === 'success';
    const cvs = document.createElement('canvas');
    cvs.width = W; cvs.height = H; cvs.className = 'battle-canvas';
    const ctx = cvs.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const bg = background(q.region);

    const party = report.members.slice(0, 4).map((m, i) => ({
      kind: 'p', look: m.look, cls: m.cls, name: m.name, dead: m.dead, injured: m.injury > 0,
      x: P_POS[i][0] - 16, y: P_POS[i][1], ox: 0, oy: 0, alpha: 1, flash: 0, frame: 0, flip: false, hp: 1, hpShow: 1,
    }));
    const def = ENEMIES[q.enemy] || {};
    const count = def.big ? 1 : (q.level >= 4 ? 3 : 2);
    const enemies = Array.from({ length: count }, (_, i) => {
      const scale = def.boss ? 4 : def.big ? 3 : 2;
      const pos = def.boss ? [190, 122] : def.big ? [186, 116] : E_POS[i];
      return { kind: 'e', name: q.enemy, scale, x: pos[0] - (16 * scale) / 2 + 8, y: pos[1], ox: 0, oy: 0, alpha: 1, flash: 0, frame: 0, hp: 1, hpShow: 1 };
    });
    const acts = buildScript(won, party, enemies);
    const total = acts.length * STEP + END;
    const pops = []; // 데미지 숫자
    const shots = [];

    const wrap = document.createElement('div');
    wrap.className = 'battle';
    const head = document.createElement('div');
    head.className = 'battle-head';
    head.textContent = `${q.title} — ${REGIONS[q.region].name}`;
    const vs = document.createElement('div');
    vs.className = 'battle-vs';
    vs.textContent = `VS ${q.enemy}${count > 1 ? ` ×${count}` : ''}`;
    const skip = document.createElement('button');
    skip.className = 'btn small';
    skip.textContent = '건너뛰기 ▶▶';
    const foot = document.createElement('div');
    foot.className = 'modal-actions';
    foot.append(skip);
    wrap.append(head, cvs, vs, foot);

    let finished = false;
    const finish = () => { if (finished) return; finished = true; stop(); onDone(); };
    skip.addEventListener('click', finish);

    const start = performance.now();
    let applied = -1;
    const loop = (now) => {
      const t = now - start;
      if (t >= total) return finish();
      const idx = Math.floor(t / STEP);
      const local = (t % STEP) / STEP;
      const all = [...party, ...enemies];
      all.forEach((e) => { e.ox = 0; e.oy = 0; e.flash = Math.max(0, e.flash - 1); e.frame = Math.floor((now / 300 + e.x) % 2); });

      // 지난 행동 효과 적용
      for (let i = applied + 1; i < Math.min(idx + (local > 0.42 ? 1 : 0), acts.length); i++) {
        const a = acts[i];
        a.to.hp = a.hp; a.to.flash = 4;
        if (a.kill) a.to.dying = now;
        pops.push({ x: a.to.x + a.to.ox + 12, y: a.to.y - 40, text: String(a.dmg), born: now, crit: a.kill, ally: a.to.kind === 'p' });
        applied = i;
      }
      // 현재 행동 연출
      const a = acts[idx];
      if (a) {
        const dir = a.from.kind === 'p' ? 1 : -1;
        const ranged = a.from.kind === 'p' && RANGED[a.from.cls];
        if (ranged) {
          a.from.ox = local < 0.2 ? -dir * 2 : 0;
          if (local > 0.15 && local < 0.42) {
            const k = (local - 0.15) / 0.27;
            shots.length = 0;
            shots.push({ kind: ranged, x: a.from.x + 28 + (a.to.x + 8 - a.from.x - 28) * k, y: a.from.y - 22 + (a.to.y - a.from.y) * k });
          } else shots.length = 0;
        } else {
          const k = local < 0.42 ? local / 0.42 : Math.max(0, 1 - (local - 0.42) / 0.4);
          const dist = Math.abs(a.to.x - a.from.x) - 34;
          a.from.ox = dir * Math.max(0, dist) * k;
          a.from.oy = -Math.sin(k * Math.PI) * 4;
        }
        if (local > 0.42 && local < 0.6) a.to.ox = dir * 3;
      } else {
        shots.length = 0;
        const k = (t - acts.length * STEP) / END;
        if (won) {
          party.forEach((p, i) => { if (p.alpha > 0.5) p.oy = -Math.abs(Math.sin((t / 160) + i)) * 6; });
        } else {
          party.forEach((p) => { if (!p.dead) { p.flip = true; p.ox = -k * 140; } });
        }
      }
      // 체력 표시 보간, 쓰러짐 처리
      all.forEach((e) => {
        e.hpShow += (e.hp - e.hpShow) * 0.2;
        if (e.dying) {
          const dt = now - e.dying;
          if (e.kind === 'e') e.alpha = dt > 500 ? 0 : (Math.floor(dt / 80) % 2 ? 0.2 : 1);
          else e.alpha = Math.max(0.35, 1 - dt / 600);
        }
      });

      // 그리기
      ctx.drawImage(bg, 0, 0);
      [...all].sort((p, q2) => p.y - q2.y).forEach((e) => drawEntity(ctx, e, t));
      party.forEach((p) => { if (p.dying && now - p.dying > 400) ctx.drawImage(Sprites.icon('skull', 2), p.x + 8, p.y - 52); });
      shots.forEach((s) => {
        if (s.kind === 'arrow') { px(ctx, s.x, s.y, 8, 1, '#e8e4d8'); px(ctx, s.x + 7, s.y - 1, 2, 3, '#d6dde4'); }
        else if (s.kind === 'fire') { px(ctx, s.x, s.y - 2, 5, 5, '#f39c12'); px(ctx, s.x + 1, s.y - 1, 3, 3, '#f2c94c'); px(ctx, s.x - 3, s.y, 3, 1, '#e74c3c'); }
        else { px(ctx, s.x, s.y - 3, 1, 7, '#fff4b0'); px(ctx, s.x - 3, s.y, 7, 1, '#fff4b0'); }
      });
      ctx.font = 'bold 11px Galmuri11, monospace';
      ctx.textAlign = 'center';
      for (let i = pops.length - 1; i >= 0; i--) {
        const pp = pops[i], age = now - pp.born;
        if (age > 700) { pops.splice(i, 1); continue; }
        const y = pp.y - age / 30;
        ctx.fillStyle = '#1b1420';
        ctx.fillText(pp.text, pp.x + 1, y + 1);
        ctx.fillStyle = pp.ally ? '#ef6a6a' : (pp.crit ? '#f2c94c' : '#ffffff');
        ctx.fillText(pp.text, pp.x, y);
      }
      if (!a) {
        const label = { great: '대승리!', success: '승리!', fail: '후퇴...', disaster: '패주...' }[report.outcome];
        ctx.font = 'bold 22px Galmuri11, monospace';
        ctx.fillStyle = '#1b1420';
        ctx.fillText(label, W / 2 + 2, 44);
        ctx.fillStyle = won ? '#f2c94c' : '#ef6a6a';
        ctx.fillText(label, W / 2, 42);
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return wrap;
  }

  function stop() { if (raf) cancelAnimationFrame(raf); raf = null; }

  return { play, stop };
})();
