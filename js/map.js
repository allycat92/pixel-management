// 대륙 지도: 지방을 다스리는 세력 색으로 칠하고, 지형 장식·전선·수도·지부·출격 중인 용병단을 그린다
'use strict';

const WorldMap = (() => {
  const W = MAP_W, H = MAP_H;
  let owner = null;     // 픽셀별 지방 키
  let terrainLayer = null;
  let baseKey = '', base = null;
  let selected = 'royal';
  let raf = null;

  function px(c, x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }
  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];

  function buildOwner() {
    owner = new Array(W * H);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) owner[y * W + x] = provinceAt(x, y);
  }

  // 지형 장식 (세력이 바뀌어도 그대로)
  function buildTerrain() {
    terrainLayer = document.createElement('canvas'); terrainLayer.width = W; terrainLayer.height = H;
    const c = terrainLayer.getContext('2d');
    const rnd = (i) => (Math.sin(i * 91.7) + 1) / 2;
    PROVINCE_KEYS.forEach((k, idx) => {
      const [rx, ry] = PROVINCES[k].pos;
      const t = PROVINCES[k].terrain;
      for (let i = 0; i < 16; i++) {
        const a = rnd(i + idx * 13) * Math.PI * 2, d = 6 + rnd(i * 3 + idx) * 18;
        const x = Math.round(rx + Math.cos(a) * d * 1.1), y = Math.round(ry + Math.sin(a) * d * 0.8);
        if (owner[y * W + x] !== k) continue;
        if (t === 'forest') { px(c, x, y - 3, 3, 3, 'rgba(20,50,20,0.75)'); px(c, x + 1, y, 1, 1, '#5a3a20'); }
        else if (t === 'swamp') { if (i % 2) px(c, x, y, 4, 1, 'rgba(30,50,50,0.7)'); else px(c, x, y - 2, 1, 3, '#8a9a4a'); }
        else if (t === 'desert') { px(c, x, y, 5, 1, 'rgba(150,110,50,0.7)'); px(c, x + 1, y - 1, 3, 1, 'rgba(240,210,140,0.7)'); }
        else if (t === 'frost' || t === 'mountain') {
          for (let q = 0; q < 4; q++) px(c, x + 3 - q, y - 4 + q, q * 2 + 1, 1, q < 1 ? (t === 'frost' ? '#ffffff' : '#f39c12') : 'rgba(40,30,30,0.6)');
        } else if (t === 'holy') { if (i % 3 === 0) { px(c, x, y - 3, 1, 4, '#f2ecd8'); px(c, x - 1, y - 2, 3, 1, '#f2ecd8'); } }
        else if (i % 2) { px(c, x, y, 2, 1, 'rgba(200,240,150,0.6)'); }
      }
    });
  }

  // 정치 지도 (소유 세력이 바뀔 때마다 다시 그림)
  function buildBase() {
    const s = Game.state;
    base = document.createElement('canvas'); base.width = W; base.height = H;
    const c = base.getContext('2d');
    const img = c.createImageData(W, H);
    const colOf = {};
    PROVINCE_KEYS.forEach((k) => {
      const f = s.provinces[k].owner;
      const fc = hex(FACTIONS[f].color), tc = hex(TERRAIN[PROVINCES[k].terrain].color);
      colOf[k] = fc.map((v, i) => Math.round(v * 0.85 + tc[i] * 0.15));
    });
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < W; x++) {
        const i = y * W + x, o = i * 4;
        const p = owner[i];
        let col;
        if (!p) col = ((x * 3 + y * 5) % 37 === 0 || (x + y * 2) % 53 === 0) ? [51, 68, 122] : [36, 48, 94];
        else {
          col = colOf[p];
          const l = x > 0 ? owner[i - 1] : p, u = y > 0 ? owner[i - W] : p;
          const coast = !l || !u || (x < W - 1 && !owner[i + 1]) || (y < H - 1 && !owner[i + W]);
          if (coast) col = [232, 213, 163];
          else if ((l && l !== p) || (u && u !== p)) {
            const fl = s.provinces[l !== p ? l : u].owner;
            col = fl !== s.provinces[p].owner ? [27, 20, 32] : col.map((v) => v * 0.7); // 세력 경계는 진하게
          }
        }
        img.data[o] = col[0]; img.data[o + 1] = col[1]; img.data[o + 2] = col[2]; img.data[o + 3] = 255;
      }
    }
    c.putImageData(img, 0, 0);
    c.drawImage(terrainLayer, 0, 0);
  }

  function drawStar(ctx, x, y) {
    [[0, -3], [-1, -2], [0, -2], [1, -2], [-3, -1], [-2, -1], [-1, -1], [0, -1], [1, -1], [2, -1], [3, -1], [-1, 0], [0, 0], [1, 0], [-2, 1], [-1, 1], [1, 1], [2, 1]]
      .forEach(([dx, dy]) => px(ctx, x + dx, y + dy, 1, 1, '#f2c94c'));
  }
  function drawSwords(ctx, x, y) {
    for (let i = 0; i < 6; i++) { px(ctx, x - 3 + i, y - 3 + i, 1, 1, '#ffffff'); px(ctx, x + 2 - i, y - 3 + i, 1, 1, '#ffffff'); }
    px(ctx, x - 3, y + 1, 2, 1, '#d9a441'); px(ctx, x + 2, y + 1, 2, 1, '#d9a441');
  }
  function drawLock(ctx, x, y) {
    px(ctx, x - 2, y - 6, 5, 1, '#c9c2b8'); px(ctx, x - 2, y - 5, 1, 2, '#c9c2b8'); px(ctx, x + 2, y - 5, 1, 2, '#c9c2b8');
    px(ctx, x - 3, y - 3, 7, 5, '#1b1420'); px(ctx, x - 2, y - 2, 5, 3, '#d9a441');
  }
  function drawFlag(ctx, x, y, col) {
    px(ctx, x, y - 8, 1, 8, '#1b1420'); px(ctx, x + 1, y - 8, 4, 3, col); px(ctx, x + 2, y - 7, 1, 1, '#ffffff');
  }

  function draw(ctx, now) {
    const s = Game.state;
    const key = PROVINCE_KEYS.map((k) => s.provinces[k].owner).join(',');
    if (key !== baseKey) { buildBase(); baseKey = key; }
    ctx.drawImage(base, 0, 0);
    const blink = Math.floor(now / 400) % 2 === 0;
    PROVINCE_KEYS.forEach((k) => {
      const [x, y] = PROVINCES[k].pos;
      const o = s.provinces[k].owner;
      if (!Game.provinceOpen(k)) drawLock(ctx, x + 9, y + 2);
      if (Game.isCapital(k)) drawStar(ctx, x, y - 2);
      const atWarFront = !FACTIONS[o].neutral && Game.warsOf(o).some((f) => Game.reachable(f, o).includes(k));
      if (atWarFront && blink) drawSwords(ctx, x - 9, y - 2);
      if (s.branches[k]) drawFlag(ctx, x + 6, y - 1, '#7a2430');
      if (s.contracts.some((c) => c.province === k && (c.boss || c.campaign)) && !blink) px(ctx, x - 1, y - 9, 3, 3, '#ef6a6a');
    });
    // 선택 지방
    if (blink) {
      const [x, y] = PROVINCES[selected].pos;
      for (let a = 0; a < 36; a++) {
        const t = (a / 36) * Math.PI * 2;
        px(ctx, Math.round(x + Math.cos(t) * 16), Math.round(y + Math.sin(t) * 12), 2, 2, '#f2c94c');
      }
    }
    // 출격 중인 용병단 (본부 → 목적지 → 본부)
    s.missions.forEach((mi, i) => {
      const [hx, hy] = PROVINCES.royal.pos, [tx, ty] = PROVINCES[mi.contract.province].pos;
      const total = Math.max(1, mi.returnDay - mi.startDay);
      let p = clamp((s.day - mi.startDay + 0.5) / total, 0, 1);
      p = p < 0.5 ? p * 2 : (1 - p) * 2;
      if (mi.contract.province === 'royal') p = 0.5;
      const x = hx + (tx - hx) * p + (i % 3) * 4 - 4, y = hy + (ty - hy) * p - 4 - (i % 2) * 3;
      const co = Game.company(mi.units[0].companyId);
      if (co) ctx.drawImage(Sprites.flag(co.color, '#e8e4d8', 1, 2), Math.round(x - 4), Math.round(y - 10 + (Math.floor(now / 300 + i) % 2)));
    });
    // 지방 이름
    ctx.font = '8px Galmuri11, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    PROVINCE_KEYS.forEach((k) => {
      const [x, y] = PROVINCES[k].pos;
      const label = PROVINCES[k].short;
      const w = ctx.measureText(label).width + 4;
      px(ctx, Math.round(x - w / 2), y + 5, Math.round(w), 10, 'rgba(27,20,32,0.75)');
      ctx.fillStyle = k === selected ? '#f2c94c' : Game.provinceOpen(k) ? '#efe6d6' : '#a89aa8';
      ctx.fillText(label, x, y + 6);
    });
  }

  function create(onSelect) {
    if (!owner) { buildOwner(); buildTerrain(); }
    const cvs = document.createElement('canvas');
    cvs.width = W; cvs.height = H;
    cvs.className = 'world-map';
    const ctx = cvs.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    cvs.addEventListener('click', (e) => {
      const r = cvs.getBoundingClientRect();
      const x = Math.floor(((e.clientX - r.left) / r.width) * W), y = Math.floor(((e.clientY - r.top) / r.height) * H);
      const p = owner[y * W + x];
      if (p) { selected = p; onSelect(p); }
    });
    if (raf) cancelAnimationFrame(raf);
    let last = 0;
    const loop = (now) => {
      if (!cvs.isConnected) { raf = null; return; }
      if (now - last > 120) { last = now; draw(ctx, now); }
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
