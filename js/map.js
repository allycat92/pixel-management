// 대륙 지도 (도트 캔버스)
'use strict';

const WorldMap = (() => {
  const W = 320, H = 180;
  const keys = Object.keys(REGIONS);
  let base = null, masks = null;
  let selected = 'plains';
  let raf = null;

  function px(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }

  function noise(x, y) {
    return Math.sin(x * 0.21 + y * 0.07) * 4 + Math.sin(y * 0.18 - x * 0.05) * 4 + Math.sin((x + y) * 0.5) * 1.5;
  }

  function build() {
    base = document.createElement('canvas'); base.width = W; base.height = H;
    const c = base.getContext('2d');
    const img = c.createImageData(W, H);
    const owner = new Int8Array(W * H).fill(-1);
    const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
    const cols = keys.map((k) => hex(REGIONS[k].color));
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        let best = -1, bd = 1e9;
        keys.forEach((k, i) => {
          const [rx, ry] = REGIONS[k].pos;
          const d = Math.hypot((x - rx) * 0.85, y - ry);
          if (d < bd) { bd = d; best = i; }
        });
        const land = bd < 40 + noise(x, y);
        let col;
        if (land) {
          owner[y * W + x] = best;
          col = cols[best];
          // 지역 경계에 살짝 어두운 점
          if (((x + y) % 2 === 0) && (x * 7 + y * 13) % 11 === 0) col = col.map((v) => v * 0.85);
        } else {
          col = ((x * 3 + y * 5) % 37 === 0 || (x + y * 2) % 53 === 0) ? [51, 68, 122] : [36, 48, 94];
        }
        const o = (y * W + x) * 4;
        img.data[o] = col[0]; img.data[o + 1] = col[1]; img.data[o + 2] = col[2]; img.data[o + 3] = 255;
      }
    }
    // 해안선
    for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) {
      const i = y * W + x;
      if (owner[i] >= 0 && (owner[i - 1] < 0 || owner[i + 1] < 0 || owner[i - W] < 0 || owner[i + W] < 0)) {
        const o = i * 4; img.data[o] = 232; img.data[o + 1] = 213; img.data[o + 2] = 163;
      } else if (owner[i] >= 0 && owner[i - 1] >= 0 && owner[i] !== owner[i - 1] && y % 2) {
        const o = i * 4; img.data[o] *= 0.6; img.data[o + 1] *= 0.6; img.data[o + 2] *= 0.6;
      }
    }
    c.putImageData(img, 0, 0);

    // 지역별 잠금 덮개
    masks = keys.map((k, idx) => {
      const m = document.createElement('canvas'); m.width = W; m.height = H;
      const mc = m.getContext('2d');
      mc.fillStyle = 'rgba(14,10,18,0.72)';
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        if (owner[y * W + x] === idx && (x + y) % 2 === 0) mc.fillRect(x, y, 1, 1);
        else if (owner[y * W + x] === idx) { mc.fillStyle = 'rgba(14,10,18,0.45)'; mc.fillRect(x, y, 1, 1); mc.fillStyle = 'rgba(14,10,18,0.72)'; }
      }
      return m;
    });

    // 길
    REGION_LINKS.forEach(([a, b]) => {
      const [x1, y1] = REGIONS[a].pos, [x2, y2] = REGIONS[b].pos;
      const n = Math.hypot(x2 - x1, y2 - y1) / 3;
      for (let i = 0; i <= n; i++) {
        if (i % 2) continue;
        const x = Math.round(x1 + ((x2 - x1) * i) / n), y = Math.round(y1 + ((y2 - y1) * i) / n);
        px(c, x, y, 1, 1, '#e8d5a3');
      }
    });

    // 지역 장식
    const rnd = (i) => ((Math.sin(i * 91.7) + 1) / 2);
    const scatter = (k, count, fn) => {
      const [rx, ry] = REGIONS[k].pos;
      for (let i = 0; i < count; i++) {
        const a = rnd(i + rx) * Math.PI * 2, d = 10 + rnd(i * 3 + ry) * 22;
        fn(Math.round(rx + Math.cos(a) * d * 1.1), Math.round(ry + Math.sin(a) * d * 0.8), i);
      }
    };
    scatter('forest', 22, (x, y) => { px(c, x, y - 3, 3, 3, '#1f4a1f'); px(c, x + 1, y - 4, 1, 1, '#2f6a2a'); px(c, x + 1, y, 1, 1, '#5a3a20'); });
    scatter('swamp', 14, (x, y, i) => { if (i % 2) px(c, x, y, 4, 1, '#2a3a3a'); else { px(c, x, y - 2, 1, 3, '#8a9a4a'); px(c, x + 2, y - 3, 1, 4, '#8a9a4a'); } });
    scatter('desert', 14, (x, y, i) => { px(c, x, y, 5, 1, '#b08a48'); px(c, x + 1, y - 1, 3, 1, '#e8c87a'); if (i % 4 === 0) { px(c, x + 2, y - 4, 1, 4, '#4a8a3a'); } });
    scatter('frost', 12, (x, y) => { for (let k = 0; k < 4; k++) px(c, x + 3 - k, y - 4 + k, k * 2 + 1, 1, k < 2 ? '#ffffff' : '#8a9ab8'); });
    scatter('dragon', 12, (x, y, i) => {
      for (let k = 0; k < 5; k++) px(c, x + 4 - k, y - 5 + k, k * 2 + 1, 1, k < 1 ? (i % 3 ? '#5a2a20' : '#f39c12') : '#3a1a14');
    });
    scatter('plains', 10, (x, y, i) => { if (i % 2) { px(c, x, y, 2, 1, '#8ac85a'); px(c, x + 3, y + 1, 1, 1, '#f2c94c'); } });
    // 화산 (용의 등뼈)
    const [dx, dy] = REGIONS.dragon.pos;
    for (let k = 0; k < 9; k++) px(c, dx + 2 - k, dy - 14 + k, k * 2 + 4, 1, '#2e1a14');
    px(c, dx + 1, dy - 15, 3, 1, '#f39c12');
  }

  function drawCastle(ctx, x, y) {
    px(ctx, x - 6, y - 8, 13, 9, '#1b1420');
    px(ctx, x - 5, y - 7, 11, 7, '#c9c2b8');
    px(ctx, x - 5, y - 10, 3, 3, '#c9c2b8'); px(ctx, x + 3, y - 10, 3, 3, '#c9c2b8');
    px(ctx, x - 1, y - 12, 3, 5, '#d6dde4');
    px(ctx, x, y - 16, 1, 4, '#1b1420'); px(ctx, x + 1, y - 16, 3, 2, '#d6455d');
    px(ctx, x - 1, y - 4, 3, 4, '#5a3a20');
  }

  function drawLock(ctx, x, y) {
    px(ctx, x - 3, y - 7, 7, 4, '#1b1420'); px(ctx, x - 2, y - 6, 5, 3, 'transparent');
    px(ctx, x - 2, y - 7, 5, 1, '#c9c2b8'); px(ctx, x - 2, y - 6, 1, 3, '#c9c2b8'); px(ctx, x + 2, y - 6, 1, 3, '#c9c2b8');
    px(ctx, x - 4, y - 3, 9, 7, '#1b1420'); px(ctx, x - 3, y - 2, 7, 5, '#d9a441'); px(ctx, x, y - 1, 1, 2, '#1b1420');
  }

  function drawCrown(ctx, x, y) {
    px(ctx, x - 4, y - 5, 9, 6, '#1b1420');
    px(ctx, x - 3, y - 2, 7, 2, '#f2c94c');
    px(ctx, x - 3, y - 4, 1, 2, '#f2c94c'); px(ctx, x, y - 4, 1, 2, '#f2c94c'); px(ctx, x + 3, y - 4, 1, 2, '#f2c94c');
    px(ctx, x, y - 2, 1, 1, '#d6455d');
  }

  function drawSkull(ctx, x, y) {
    px(ctx, x - 4, y - 6, 9, 8, '#1b1420');
    px(ctx, x - 3, y - 5, 7, 5, '#e8e4d8'); px(ctx, x - 2, y, 5, 1, '#e8e4d8');
    px(ctx, x - 2, y - 3, 2, 2, '#1b1420'); px(ctx, x + 1, y - 3, 2, 2, '#1b1420');
  }

  function drawFlag(ctx, x, y) {
    px(ctx, x, y - 9, 1, 9, '#1b1420');
    px(ctx, x + 1, y - 9, 5, 3, '#7a2430'); px(ctx, x + 2, y - 8, 2, 1, '#d6dde4');
  }

  function draw(ctx, now) {
    const s = Game.state;
    ctx.drawImage(base, 0, 0);
    keys.forEach((k, i) => { if (!Game.regionUnlocked(k)) ctx.drawImage(masks[i], 0, 0); });
    drawCastle(ctx, REGIONS.plains.pos[0], REGIONS.plains.pos[1]);
    keys.forEach((k) => {
      const [x, y] = REGIONS[k].pos;
      if (!Game.regionUnlocked(k)) drawLock(ctx, x, y);
      else if (s.outposts[k]) drawFlag(ctx, x + 6, y);
      if (s.bossDefeated && s.bossDefeated[k]) drawCrown(ctx, x - 10, y - 4);
      else if (s.quests.some((q) => q.boss === k) && Math.floor(now / 300) % 2) drawSkull(ctx, x - 10, y - 4);
    });
    // 선택 지역 테두리 (깜빡임)
    if (Math.floor(now / 400) % 2 === 0) {
      const [x, y] = REGIONS[selected].pos;
      for (let a = 0; a < 40; a++) {
        const t = (a / 40) * Math.PI * 2;
        px(ctx, Math.round(x + Math.cos(t) * 20), Math.round(y + Math.sin(t) * 15), 2, 2, '#f2c94c');
      }
    }
    // 의뢰 진행 중인 파티 (본거지 → 목적지 → 본거지)
    s.missions.forEach((mi, i) => {
      const [hx, hy] = REGIONS.plains.pos, [tx, ty] = REGIONS[mi.quest.region].pos;
      const total = Math.max(1, mi.returnDay - mi.startDay);
      let p = clamp((s.day - mi.startDay + 0.5) / total, 0, 1);
      p = p < 0.5 ? p * 2 : (1 - p) * 2;
      if (mi.quest.region === 'plains') p = 0.6;
      const x = hx + (tx - hx) * p + (i % 3) * 5 - 5, y = hy + (ty - hy) * p - 4 - (i % 2) * 4;
      const leader = s.mercs.find((m) => m.id === mi.party[0]);
      if (leader) {
        const bob = Math.floor(now / 250 + i) % 2;
        ctx.drawImage(Sprites.merc(leader.look, 1, bob ? 2 : 0, tx < hx && p > 0), Math.round(x - 8), Math.round(y - 14));
      }
    });
    // 지역 이름
    ctx.font = '8px Galmuri11, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    keys.forEach((k) => {
      const r = REGIONS[k];
      const [x, y] = r.pos;
      const label = Game.regionUnlocked(k) ? r.name : `${r.name} (${RANKS[r.unlock].name})`;
      const w = ctx.measureText(label).width + 6;
      px(ctx, Math.round(x - w / 2), y + 9, Math.round(w), 11, 'rgba(27,20,32,0.8)');
      ctx.fillStyle = k === selected ? '#f2c94c' : (Game.regionUnlocked(k) ? '#efe6d6' : '#a89aa8');
      ctx.fillText(label, x, y + 10);
    });
  }

  function create(onSelect) {
    if (!base) build();
    const cvs = document.createElement('canvas');
    cvs.width = W; cvs.height = H;
    cvs.className = 'world-map';
    const ctx = cvs.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    cvs.addEventListener('click', (e) => {
      const r = cvs.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * W, y = ((e.clientY - r.top) / r.height) * H;
      let best = null, bd = 30;
      keys.forEach((k) => {
        const [rx, ry] = REGIONS[k].pos;
        const d = Math.hypot(rx - x, ry - y);
        if (d < bd) { bd = d; best = k; }
      });
      if (best) { selected = best; onSelect(best); }
    });
    if (raf) cancelAnimationFrame(raf);
    const loop = (now) => {
      if (!cvs.isConnected) { raf = null; return; }
      draw(ctx, now);
      raf = requestAnimationFrame(loop);
    };
    draw(ctx, performance.now());
    raf = requestAnimationFrame(loop);
    return cvs;
  }

  return {
    create,
    get selected() { return selected; },
    set selected(k) { selected = k; },
  };
})();
