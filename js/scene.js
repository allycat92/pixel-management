// 상단 길드 홀 도트 장면 (애니메이션)
'use strict';

const Scene = (() => {
  const W = 320, H = 120, FLOOR = 74;
  let cvs, ctx, bg;
  const actors = new Map(); // mercId -> {x, y, tx, ty, flip, wait, phase}
  let tick = 0;

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

  function drawBoard(quests) {
    const n = Math.min(quests, 6);
    for (let i = 0; i < n; i++) {
      const x = 121 + (i % 3) * 11, y = 21 + Math.floor(i / 3) * 11;
      px(ctx, x, y, 9, 9, i % 2 ? '#efe2c0' : '#e8d5a3');
      px(ctx, x + 4, y, 1, 1, '#c0392b');
      px(ctx, x + 2, y + 3, 5, 1, '#8a7a5a'); px(ctx, x + 2, y + 5, 4, 1, '#8a7a5a');
    }
  }

  function drawFire() {
    const fx = 268 + 10;
    const cols = ['#f2c94c', '#f39c12', '#e74c3c', '#fff4b0'];
    for (let i = 0; i < 26; i++) {
      const x = fx + 2 + Math.floor(Math.random() * 20);
      const h = 4 + Math.floor(Math.random() * 12);
      const y = 70 - h;
      px(ctx, x, y, 1, h, cols[Math.floor(Math.random() * 3)]);
    }
    px(ctx, fx + 8, 62 + (tick % 2), 4, 6, cols[3]);
    // 바닥에 비치는 불빛
    const glow = ctx.createRadialGradient(290, 78, 4, 290, 78, 60);
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
        actors.set(m.id, {
          x: rand(70, 250), y: rand(FLOOR + 2, H - 20), tx: 0, ty: 0, flip: Math.random() < 0.5,
          wait: rand(5, 30), phase: rand(0, 3),
        });
        const a = actors.get(m.id); a.tx = a.x; a.ty = a.y;
      }
    });
  }

  function update() {
    if (!Game.state) return;
    syncActors(Game.state.mercs);
    Game.state.mercs.forEach((m) => {
      const a = actors.get(m.id);
      if (!a) return;
      if (m.status === 'injured') {
        // 부상자는 벽난로 앞에서 쉰다
        a.tx = 240 + (m.id % 3) * 8; a.ty = FLOOR + 14 + (m.id % 2) * 8;
      } else if (a.wait > 0) {
        a.wait--;
        return;
      }
      const dx = a.tx - a.x, dy = a.ty - a.y;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) {
        if (m.status !== 'injured') {
          a.tx = rand(64, 250); a.ty = rand(FLOOR + 2, H - 20);
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
    ctx.drawImage(bg, 0, 0);
    if (!Game.state) return;
    drawBoard(Game.state.quests.length);
    drawFire();
    // 주점 주인 NPC
    const barkeep = { cls: 'archer', skin: '#e0ac7e', hair: '#8a5a2b', longHair: false };
    ctx.drawImage(Sprites.merc(barkeep, 1, tick % 8 < 4 ? 0 : 1), 24, 36);
    ctx.drawImage(bg, 6, 50, 52, 28, 6, 50, 52, 28); // 카운터를 앞에 다시 그림

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
