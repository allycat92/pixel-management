// 상단 길드 홀 도트 장면 (애니메이션)
'use strict';

const Scene = (() => {
  const W = 320, H = 120, FLOOR = 74;
  let cvs, ctx, bg;
  const actors = new Map(); // mercId -> {x, y, tx, ty, flip, wait, phase}
  let tick = 0;

  // 덧그림 자리: 코드로 그린 방(code)과 일러스트 배경(art: assets/art bg/guild/day|night, 320x120)은 가구 위치가 다르다.
  //  board: 의뢰 쪽지 [x, y, 가로 간격, 세로 간격], fire: 불꽃 [왼쪽 x, 바닥 y, 빛 중심 x, y], counter: 바텐더 앞에 다시 그릴 카운터 [x, y, w, h],
  //  keep: 바텐더 위치, walk: 돌아다닐 바닥 [x0, x1, 발 y0, 발 y1] 중 하나 (일러스트는 식탁·의자를 피한 앞쪽 띠와 융단 길),
  //  rest: 부상자가 쉬는 벽난로 앞 [x, 발 y]
  const LAYOUT = {
    code: { board: [121, 21, 11, 11], fire: [280, 70, 290, 78], counter: [6, 50, 52, 28], keep: [24, 36],
      walk: [[64, 266, FLOOR + 18, H - 4]], rest: [240, FLOOR + 30] },
    art: { board: [147, 36, 14, 13], fire: [288, 76, 297, 84], counter: [0, 68, 56, 22], keep: [24, 53],
      walk: [[56, 282, 110, 118], [152, 182, 92, 118], [52, 66, 96, 118]], rest: [276, 98] },
  };
  let layoutName = 'code';
  let night = false; // 지금 밤 그림인가 (일러스트 벽난로: 낮에는 꺼져 있고 밤에는 그림 속 불이 타고 있다)
  // 길드 홀 그림: 한 주(7일)의 마지막 이틀(급료일 전야)은 밤 그림. 그림이 없으면 다른 쪽, 그것도 없으면 코드로 그린 방.
  function guildArt() {
    if (typeof Art === 'undefined' || !Art.image || !Game.state) return null;
    const wantNight = Game.state.day % 7 === 6 || Game.state.day % 7 === 0;
    const a = Art.image('bg/guild/day'), b = Art.image('bg/guild/night');
    const pic = wantNight ? b || a : a || b;
    night = !!pic && pic === b;
    return pic;
  }
  function spot(L) {
    const z = L.walk[rand(0, L.walk.length - 1)];
    return { x: rand(z[0], z[1] - 16), y: rand(z[2], z[3]) - 16 };
  }

  function init(canvasEl) {
    cvs = canvasEl; ctx = cvs.getContext('2d');
    cvs.width = W; cvs.height = H;
    ctx.imageSmoothingEnabled = false;
    bg = buildBackground();
    let last = 0;
    const loop = (t) => {
      if (t - last > 110) { last = t; tick++; update(); draw(); }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  function px(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }

  function buildBackground() {
    const b = document.createElement('canvas'); b.width = W; b.height = H;
    const c = b.getContext('2d');
    // 벽: 나무 판자
    px(c, 0, 0, W, FLOOR, '#4e3324');
    for (let y = 0; y < FLOOR; y += 7) {
      px(c, 0, y, W, 1, '#3c2619');
      for (let x = (y / 7) % 2 ? 0 : 20; x < W; x += 40) px(c, x, y, 1, 7, '#3c2619');
    }
    // 기둥
    [0, 104, 212, 316].forEach((x) => { px(c, x, 0, 4, FLOOR, '#2e1d13'); px(c, x + 1, 0, 1, FLOOR, '#5e3e2b'); });
    px(c, 0, 0, W, 4, '#2e1d13');
    // 창문
    [[60, 14], [232, 14]].forEach(([x, y]) => {
      px(c, x - 2, y - 2, 28, 26, '#2e1d13');
      px(c, x, y, 24, 22, '#24305e');
      px(c, x, y + 14, 24, 8, '#33447a');
      px(c, x + 3, y + 3, 2, 2, '#f4f0c8'); px(c, x + 17, y + 6, 1, 1, '#f4f0c8'); px(c, x + 9, y + 9, 1, 1, '#c8d0f0');
      px(c, x + 11, y, 2, 22, '#2e1d13'); px(c, x, y + 10, 24, 2, '#2e1d13');
      px(c, x - 3, y + 22, 30, 3, '#6b4a33');
    });
    // 깃발 (용병단 문장)
    const fx = 168;
    px(c, fx - 2, 6, 28, 2, '#2e1d13');
    px(c, fx, 8, 24, 30, '#7a2430'); px(c, fx, 38, 8, 4, '#7a2430'); px(c, fx + 16, 38, 8, 4, '#7a2430');
    px(c, fx + 1, 9, 22, 1, '#d9a441'); px(c, fx + 1, 36, 22, 1, '#d9a441');
    // 은빛 늑대 머리
    const wolf = ['..W.....W..', '..WW...WW..', '..WWWWWWW..', '.WWKWWWKWW.', '.WWWWWWWWW.', '..WWWWWWW..', '...WWNWW...', '....WWW....'];
    wolf.forEach((row, y) => row.split('').forEach((ch, x) => {
      if (ch === 'W') px(c, fx + 7 + x, 16 + y * 2, 1, 2, '#d6dde4');
      if (ch === 'K') px(c, fx + 7 + x, 16 + y * 2, 1, 2, '#1b1420');
      if (ch === 'N') px(c, fx + 7 + x, 16 + y * 2, 1, 2, '#1b1420');
    }));
    // 바닥 타일
    px(c, 0, FLOOR, W, H - FLOOR, '#6e4c32');
    for (let y = FLOOR; y < H; y += 8) {
      px(c, 0, y, W, 1, '#5a3d28');
      for (let x = ((y - FLOOR) / 8) % 2 ? 0 : 8; x < W; x += 16) px(c, x, y, 1, 8, '#5a3d28');
    }
    px(c, 0, FLOOR, W, 2, '#3c2619');
    // 카펫
    px(c, 120, FLOOR + 14, 80, 22, '#7a2430');
    px(c, 122, FLOOR + 16, 76, 18, '#94303d');
    for (let x = 124; x < 196; x += 6) px(c, x, FLOOR + 24, 3, 2, '#d9a441');
    // 주점 카운터
    px(c, 6, 50, 52, 6, '#7a5236'); px(c, 6, 50, 52, 1, '#9a6a46');
    px(c, 6, 56, 52, 22, '#5a3a26');
    for (let x = 10; x < 56; x += 12) px(c, x, 59, 8, 15, '#4a2f1f');
    // 술통과 선반
    px(c, 8, 22, 48, 2, '#2e1d13');
    [[12, 14, '#c0392b'], [20, 15, '#2e86c1'], [28, 13, '#27ae60'], [40, 14, '#d9a441']].forEach(([x, y, col]) => {
      px(c, x, y, 4, 8, col); px(c, x + 1, y - 2, 2, 2, col); px(c, x + 1, y + 1, 1, 3, '#ffffff55');
    });
    px(c, 46, 40, 10, 10, '#7a5236'); px(c, 46, 43, 10, 1, '#2e1d13'); px(c, 46, 47, 10, 1, '#2e1d13');
    // 의뢰 게시판 프레임
    px(c, 116, 16, 40, 30, '#2e1d13');
    px(c, 118, 18, 36, 26, '#b07c45');
    // 벽난로
    const fx2 = 268;
    px(c, fx2, 30, 44, 46, '#5c5c66');
    for (let y = 30; y < 76; y += 5) for (let x = fx2 + ((y / 5) % 2 ? 0 : 5); x < fx2 + 44; x += 10) px(c, x, y, 1, 5, '#44444c');
    for (let y = 30; y < 76; y += 5) px(c, fx2, y, 44, 1, '#44444c');
    px(c, fx2 - 2, 28, 48, 4, '#3a3a42');
    px(c, fx2 + 8, 46, 28, 30, '#1b1420');
    // 장작
    px(c, fx2 + 11, 70, 22, 3, '#6b4226'); px(c, fx2 + 14, 67, 16, 3, '#8a5a2b');
    return b;
  }

  function drawBoard(quests, L) {
    const n = Math.min(quests, 6), [bx, by, dx, dy] = L.board;
    for (let i = 0; i < n; i++) {
      const x = bx + (i % 3) * dx, y = by + Math.floor(i / 3) * dy;
      px(ctx, x, y, 9, 9, i % 2 ? '#efe2c0' : '#e8d5a3');
      px(ctx, x + 4, y, 1, 1, '#c0392b');
      px(ctx, x + 2, y + 3, 5, 1, '#8a7a5a'); px(ctx, x + 2, y + 5, 4, 1, '#8a7a5a');
    }
  }

  // 일러스트 벽난로: 낮 그림은 불이 꺼져 있으므로 아무것도 덧그리지 않고, 밤 그림은 그림 속 불 위에
  // 따뜻한 빛만 은은하게 일렁이게 한다 (1px 불꽃 막대를 그리면 바코드처럼 보인다)
  function drawHearthGlow(L) {
    if (!night) return;
    const [, , gx, gy] = L.fire;
    const f = 0.5 + 0.5 * Math.sin(tick * 0.9) * Math.sin(tick * 0.37 + 1.3);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    const core = ctx.createRadialGradient(gx, gy - 12, 2, gx, gy - 12, 22 + f * 3);
    core.addColorStop(0, `rgba(255, 170, 70, ${0.10 + f * 0.07})`);
    core.addColorStop(1, 'rgba(255, 140, 50, 0)');
    ctx.fillStyle = core;
    ctx.fillRect(gx - 30, gy - 42, 60, 60);
    ctx.restore();
    // 바닥에 비치는 불빛
    const floor = ctx.createRadialGradient(gx, gy + 6, 4, gx, gy + 6, 56);
    floor.addColorStop(0, `rgba(242, 150, 60, ${0.10 + f * 0.05})`);
    floor.addColorStop(1, 'rgba(242, 150, 60, 0)');
    ctx.fillStyle = floor;
    ctx.fillRect(gx - 60, gy - 20, 120, H - gy + 20);
  }

  function drawFire(L) {
    const [fx, base, gx, gy] = L.fire;
    const cols = ['#f2c94c', '#f39c12', '#e74c3c', '#fff4b0'];
    for (let i = 0; i < 26; i++) {
      const x = fx + Math.floor(Math.random() * 20);
      const h = 4 + Math.floor(Math.random() * 12);
      const y = base - h;
      px(ctx, x, y, 1, h, cols[Math.floor(Math.random() * 3)]);
    }
    px(ctx, fx + 6, base - 8 + (tick % 2), 4, 6, cols[3]);
    // 바닥에 비치는 불빛
    const glow = ctx.createRadialGradient(gx, gy, 4, gx, gy, 60);
    glow.addColorStop(0, `rgba(242, 160, 60, ${0.18 + Math.random() * 0.06})`);
    glow.addColorStop(1, 'rgba(242, 160, 60, 0)');
    ctx.fillStyle = glow;
    ctx.fillRect(220, 70, 100, 50);
  }

  function syncActors(mercs) {
    const present = mercs.filter((m) => m.status !== 'quest');
    const ids = new Set(present.map((m) => m.id));
    for (const id of [...actors.keys()]) if (!ids.has(id)) actors.delete(id);
    present.forEach((m) => {
      if (!actors.has(m.id)) {
        const p = spot(LAYOUT[layoutName]);
        actors.set(m.id, {
          x: p.x, y: p.y, tx: 0, ty: 0, flip: Math.random() < 0.5,
          wait: rand(5, 30), phase: rand(0, 3),
        });
        const a = actors.get(m.id); a.tx = a.x; a.ty = a.y;
      }
    });
  }

  function update() {
    if (!Game.state) return;
    const L = LAYOUT[layoutName];
    syncActors(Game.state.mercs);
    Game.state.mercs.forEach((m) => {
      const a = actors.get(m.id);
      if (!a) return;
      if (m.status === 'injured') {
        // 부상자는 벽난로 앞에서 쉰다
        a.tx = L.rest[0] + (m.id % 3) * 8; a.ty = L.rest[1] - 16 + (m.id % 2) * 8;
      } else if (a.wait > 0) {
        a.wait--;
        return;
      }
      const dx = a.tx - a.x, dy = a.ty - a.y;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) {
        if (m.status !== 'injured') {
          const p = spot(L);
          a.tx = p.x; a.ty = p.y;
          a.wait = rand(8, 40);
        }
        return;
      }
      a.x += Math.sign(dx) * Math.min(Math.abs(dx), 2);
      a.y += Math.sign(dy) * Math.min(Math.abs(dy), 1);
      if (dx !== 0) a.flip = dx < 0;
      a.moving = true;
    });
  }

  function draw() {
    const art = guildArt(), room = art || bg;
    const name = art ? 'art' : 'code';
    if (name !== layoutName) { layoutName = name; actors.clear(); } // 가구 위치가 바뀌면 단원 자리도 새로
    const L = LAYOUT[layoutName];
    ctx.drawImage(room, 0, 0, W, H);
    if (!Game.state) return;
    drawBoard(Game.state.contracts.length, L);
    if (layoutName === 'art') drawHearthGlow(L); else drawFire(L);
    // 주점 주인 NPC
    const barkeep = { cls: 'archer', skin: '#e0ac7e', hair: '#8a5a2b', longHair: false };
    ctx.drawImage(Sprites.merc(barkeep, 1, tick % 8 < 4 ? 0 : 1), L.keep[0], L.keep[1]);
    const [cx, cy, cw, ch] = L.counter;
    ctx.drawImage(room, cx * room.width / W, cy * room.height / H, cw * room.width / W, ch * room.height / H, cx, cy, cw, ch); // 카운터를 앞에 다시 그림

    const list = Game.state.mercs
      .map((m) => ({ m, a: actors.get(m.id) }))
      .filter((o) => o.a)
      .sort((p, q) => p.a.y - q.a.y);
    list.forEach(({ m, a }) => {
      const moving = Math.abs(a.tx - a.x) >= 1 || Math.abs(a.ty - a.y) >= 1;
      let frame = 0;
      if (moving && m.status !== 'injured') frame = tick % 2 ? 2 : 0;
      else frame = (tick + a.phase) % 8 < 4 ? 0 : 1;
      // 그림자
      ctx.fillStyle = 'rgba(0,0,0,0.25)';
      ctx.fillRect(Math.round(a.x) + 3, Math.round(a.y) + 15, 10, 2);
      ctx.drawImage(Sprites.merc(m.look, 1, frame, a.flip), Math.round(a.x), Math.round(a.y));
      if (m.status === 'injured') {
        const bob = tick % 6 < 3 ? 0 : 1;
        ctx.drawImage(Sprites.icon('cross', 1), Math.round(a.x) + 4, Math.round(a.y) - 9 + bob);
      }
    });
    // 의뢰 중 인원 표시
    const away = Game.state.mercs.filter((m) => m.status === 'quest').length;
    if (away) {
      px(ctx, 4, H - 12, 78, 10, 'rgba(27,20,32,0.7)');
      ctx.fillStyle = '#f2c94c';
      ctx.font = '8px Galmuri11, monospace';
      ctx.textBaseline = 'top';
      ctx.fillText(`의뢰 수행 중: ${away}명`, 7, H - 11);
    }
  }

  return { init };
})();
