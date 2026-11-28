// FX 미리보기 무대: 게임 그림(manifest 시트·배경)을 읽기만 해서 작은 장면을 세우고 FxPlayer 로 스펙을 재생한다.
// js/battle.js 는 불러오지 않는다(독립 페이지). 몸 시트는 battle.js 의 blit 과 같은 방식(1:1, 발 기준점, 좌우 반전)으로 그린다.
// 캡처 도구(tools/fxpreview/capture.js)는 window.FXP 로 정해진 시각을 그린다.
'use strict';

(() => {
  const SPEC_URL = 'assets/fx/sig/captain/blademaster/hoejeon-begi.json';
  const KIT_URL = 'assets/fx/kits/captain/blademaster.json';
  const OWNER = 'captain/blademaster';
  const STEP = 1 / 60;          // 한 프레임 넘기기
  const TAIL = 0.6;             // 반복 사이 쉬는 시간(초)

  // 장면: 발 위치(화면 px). 시트는 오른쪽을 본다 — face -1 이면 뒤집어 그린다.
  const CASTER = { id: 'sheet/captain/blademaster', x: 320, y: 264, face: 1 };
  // 키 이미지처럼 양쪽에 셋씩. (실제 aoe 18 = 반경 36px 보다 넓게 벌려 선이 서로 겹치지 않게 — 미리보기 배치)
  const VICTIMS_WIDE = [
    { id: 'sheet/monster/산적', x: 388, y: 234, face: -1 },
    { id: 'sheet/monster/사막 도적', x: 414, y: 272, face: -1 },
    { id: 'sheet/class/warrior', x: 374, y: 308, face: -1 },
    { id: 'sheet/monster/사막 도적', x: 254, y: 236, face: 1 },
    { id: 'sheet/class/warrior', x: 228, y: 276, face: 1 },
    { id: 'sheet/monster/산적', x: 268, y: 310, face: 1 },
  ];
  // 실제 aoe 18(반경 36px) 안에 몰아 세운 배치 — 선 간격 규칙(place.minGap, lineK) 시험용
  const VICTIMS_TIGHT = [
    { id: 'sheet/monster/산적', x: 350, y: 246, face: -1 },
    { id: 'sheet/monster/사막 도적', x: 358, y: 268, face: -1 },
    { id: 'sheet/class/warrior', x: 348, y: 290, face: -1 },
    { id: 'sheet/monster/사막 도적', x: 290, y: 248, face: 1 },
    { id: 'sheet/class/warrior', x: 282, y: 270, face: 1 },
    { id: 'sheet/monster/산적', x: 294, y: 288, face: 1 },
  ];
  const LAYOUTS = { wide: VICTIMS_WIDE, tight: VICTIMS_TIGHT };
  let VICTIMS = VICTIMS_WIDE;
  // 범위 밖 (맞지 않는다)
  const BYSTANDERS = [
    { id: 'sheet/class/archer', x: 548, y: 228, face: -1 },
    { id: 'sheet/monster/해골 병사', x: 584, y: 292, face: -1 },
  ];
  const BGS = ['plains', 'mountain', 'forest', 'desert', 'frost', 'coast', 'swamp', 'holy'];

  const cv = document.getElementById('stage'), ctx = cv.getContext('2d');
  const tlc = document.getElementById('tl'), tctx = tlc.getContext('2d');
  ctx.imageSmoothingEnabled = false;

  const state = { t: 0, playing: true, loop: true, speed: 1, seed: 7, zoom: 2, bg: 'plains', layout: 'wide', anchors: false, hidden: {} };
  let spec, kit, inst, scene, ready = false;

  // ───── 시트 도우미 ─────
  const frameAt = (a, ms, once) => {
    let t = once ? Math.min(a.total - 1, Math.max(0, ms)) : ((ms % a.total) + a.total) % a.total;
    for (let j = 0; j < a.ms.length; j++) { if (t < a.ms[j]) return a.from + j; t -= a.ms[j]; }
    return a.to;
  };
  const boxCache = new Map();
  // 칸 안 불투명 상자 (+ 가장 오른쪽 불투명 열의 y: 칼끝 찾기)
  function cellBox(sh, i) {
    const key = `${sh.id}#${i}`;
    if (boxCache.has(key)) return boxCache.get(key);
    const m = sh.meta, f = m.frames[i], [w, h] = m.cell;
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); g.drawImage(sh.img, f[0], f[1], w, h, 0, 0, w, h);
    const d = g.getImageData(0, 0, w, h).data;
    let x0 = w, y0 = h, x1 = -1, y1 = -1, rx = -1, ry = 0;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (d[(y * w + x) * 4 + 3] < 128) continue;
      if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
      if (x > rx) { rx = x; ry = y; }
    }
    const b = { x0, y0, x1: x1 + 1, y1: y1 + 1, rx, ry };
    boxCache.set(key, b);
    return b;
  }
  // 칸 좌표 → 화면 좌표 (battle.js blit 과 같은 반전 규칙)
  function toWorld(u, sh, cx, cy) {
    const [ax, ay] = sh.meta.anchor;
    const x = u.face * sh.meta.facing < 0 ? u.x + ax - cx - 1 : u.x - ax + cx;
    return [x, u.y - ay + cy];
  }
  function worldBox(u, sh, i) {
    const b = cellBox(sh, i);
    const [a0, b0] = toWorld(u, sh, b.x0, b.y0), [a1, b1] = toWorld(u, sh, b.x1 - 1, b.y1 - 1);
    return { x0: Math.min(a0, a1), y0: b0, x1: Math.max(a0, a1) + 1, y1: b1 + 1 };
  }

  // 칸 → 한 색 실루엣(+ 1px 위 테두리) / 윤곽만(시전자 위·왼쪽 테두리). 모양 없는 빛: 몸 칸의 알파만 쓴다.
  const tintCache = new Map();
  function cellPixels(sh, i) {
    const m = sh.meta, f = m.frames[i], [w, h] = m.cell;
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); g.drawImage(sh.img, f[0], f[1], w, h, 0, 0, w, h);
    return { c, g, w, h, d: g.getImageData(0, 0, w, h) };
  }
  const hexRGB = (col) => [1, 3, 5].map((k) => parseInt(col.slice(k, k + 2), 16));
  // look.mode 'silhouette': fill 로 채우고, 위가 비어 있는 칸은 rim 색 / 'tint': fill 로 덮기 / 'rim': 화면 기준 위·왼쪽 가장자리만
  function lookImage(sh, i, look, flip) {
    const key = `${sh.id}#${i}#${look.mode}#${look.fill || ''}#${look.rim || ''}#${look.colour || ''}#${flip}`;
    let c = tintCache.get(key);
    if (c) return c;
    const P = cellPixels(sh, i), { w, h } = P, src = P.d.data;
    const out = P.g.createImageData(w, h), o = out.data;
    const A = (x, y) => (x < 0 || y < 0 || x >= w || y >= h ? 0 : src[(y * w + x) * 4 + 3]);
    const put = (x, y, rgb) => { const k = (y * w + x) * 4; o[k] = rgb[0]; o[k + 1] = rgb[1]; o[k + 2] = rgb[2]; o[k + 3] = 255; };
    const fill = look.fill && hexRGB(look.fill), rim = look.rim && hexRGB(look.rim), col = look.colour && hexRGB(look.colour);
    const leftDx = flip ? 1 : -1;     // 뒤집어 그리면 화면 왼쪽 = 칸 오른쪽
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      if (A(x, y) < 128) continue;
      const top = A(x, y - 1) < 128;
      if (look.mode === 'rim') { if (top || A(x + leftDx, y) < 128) put(x, y, col); }
      else put(x, y, look.mode === 'silhouette' && top && rim ? rim : fill);
    }
    P.g.clearRect(0, 0, w, h); P.g.putImageData(out, 0, 0);
    tintCache.set(key, P.c);
    return P.c;
  }
  // clip: { above: true|false, y } — 세계 y 기준으로 위쪽(y 미만)만 / 아래쪽(y 이상)만 그린다
  function blitCell(sh, i, X, Y, flip, img, alpha, clip) {
    const m = sh.meta, f = m.frames[i] || m.frames[0], [w, h] = m.cell, [ax, ay] = m.anchor;
    const src = img || sh.img, sx = img ? 0 : f[0], sy = img ? 0 : f[1];
    ctx.save();
    if (clip) { ctx.beginPath(); if (clip.above) ctx.rect(X - 200, clip.y - 400, 400, 400); else ctx.rect(X - 200, clip.y, 400, 400); ctx.clip(); }
    if (alpha != null) ctx.globalAlpha = alpha;
    if (!flip) ctx.drawImage(src, sx, sy, w, h, Math.round(X) - ax, Math.round(Y) - ay, w, h);
    else { ctx.translate(Math.round(X), 0); ctx.scale(-1, 1); ctx.drawImage(src, sx, sy, w, h, -ax, Math.round(Y) - ay, w, h); }
    ctx.restore();
  }
  const stepA = (a) => (a < 0.25 ? 0 : a < 0.75 ? 0.5 : 1);   // 윤곽 알파는 0/50/100% 단계만
  function shadow(x, y, rx) {
    ctx.save(); ctx.globalAlpha = 0.28; ctx.fillStyle = '#000';
    for (let dy = -3; dy <= 3; dy++) {
      const half = Math.round(rx * Math.sqrt(1 - (dy / 3.6) ** 2));
      ctx.fillRect(Math.round(x) - half, Math.round(y) + dy, half * 2, 1);
    }
    ctx.restore();
  }

  // 조각 시트(fx/sig/<owner>/<piece>)가 manifest 에 등록되면 그것을 쓴다. 없으면 null → PLACEHOLDER.
  function sheetFor(piece) {
    const sh = Art.sheet(`fx/sig/${OWNER}/${piece}`);
    if (!sh) return null;
    return { img: sh.img, frames: sh.meta.frames, cell: sh.meta.cell, origin: sh.meta.anchor };
  }

  // ───── 장면·인스턴스 ─────
  function build() {
    const cSh = Art.sheet(CASTER.id);
    const fol = (spec.actor.poses.follow || ['attack', 1]);
    const folI = Art.anim(cSh.meta, fol[0]).from + fol[1];
    const cb = cellBox(cSh, folI);
    const tip = toWorld(CASTER, cSh, cb.rx, cb.ry);
    scene = {
      caster: { ...CASTER, sheet: cSh, box: worldBox(CASTER, cSh, Art.anim(cSh.meta, 'idle').from), tip },
      victims: (VICTIMS = LAYOUTS[state.layout] || VICTIMS_WIDE).map((v) => { const sh = Art.sheet(v.id); return { ...v, sheet: sh, box: worldBox(v, sh, Art.anim(sh.meta, 'idle').from) }; }),
      bystanders: BYSTANDERS.map((v) => ({ ...v, sheet: Art.sheet(v.id) })).filter((v) => v.sheet),
    };
    inst = FxPlayer.create(spec, kit, scene, { seed: state.seed, speed: state.speed, sheetFor, hidden: state.hidden });
    const sc = document.getElementById('scrub');
    sc.max = String(Math.round(inst.duration * 1000));
    drawTimeline();
  }

  // ───── 한 장 그리기 ─────
  function render(t) {
    const W = cv.width, H = cv.height;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    const [sx, sy] = inst.camera(t);
    const v = inst.view(t, W, H);
    // 정수 확대(punch-in) + 정수 흔들림. imageSmoothing 꺼져 있어 nearest 그대로.
    ctx.setTransform(v.z, 0, 0, v.z, Math.round(W / 2 - v.z * v.cx + sx), Math.round(H / 2 - v.z * v.cy + sy));
    const bg = Art.image(`bg/battle/${state.bg}`);
    if (bg) ctx.drawImage(bg, 0, 0, W, H);
    inst.draw(ctx, 'ground', t);

    const uc = inst.unitClock(t);
    const units = [];
    const C = scene.caster;
    units.push({ u: C, role: 'caster' });
    scene.victims.forEach((v, i) => units.push({ u: v, role: 'victim', i }));
    scene.bystanders.forEach((v) => units.push({ u: v, role: 'other' }));
    // 궁극기 연출 중에는 시전자를 맨 앞에 (actor.frontWhileStaged) — 실루엣 무리에 가리지 않게
    const front = spec.actor.frontWhileStaged && inst.unitLook(t, 'other');
    const key = (x) => x.u.y + (front && x.role === 'caster' ? 10000 : 0);
    units.sort((a, b) => key(a) - key(b));

    // 그림자 먼저
    units.forEach(({ u }) => shadow(u.x, u.y, 13));
    units.forEach(({ u, role, i }, k) => {
      const sh = u.sheet, m = sh.meta;
      let fi, flip = u.face * m.facing < 0, dx = 0;
      if (role === 'caster') {
        const p = inst.casterPose(t);
        if (p.cell == null) fi = frameAt(Art.anim(m, 'idle'), uc * 1000, false);
        else fi = Art.anim(m, p.anim).from + p.cell;
        if (p.flip) flip = !flip;
      } else {
        const v = role === 'victim' ? inst.victim(i, t) : { hit: false, dx: 0 };
        dx = v.dx;
        fi = v.hit ? Art.anim(m, 'hit').from : frameAt(Art.anim(m, 'idle'), (uc + k * 0.37) * 1000, false);
      }
      const look = inst.unitLook(t, role === 'caster' ? 'caster' : 'other');
      const img = look ? lookImage(sh, fi, look, flip) : null;
      const sp = role === 'victim' ? inst.victim(i, t).split : null;
      // 한 몸을 그리는 두 번(원래 + 실루엣/윤곽) — 쪼개짐이면 아래는 제자리, 위는 선을 따라 미끄러진다
      const body = (X, Y, clip) => {
        if (!(look && look.mode !== 'rim' && look.alpha >= 0.999)) blitCell(sh, fi, X, Y, flip, null, null, clip);
        if (img) blitCell(sh, fi, X, Y, flip, img, look.alpha >= 0.999 ? 1 : (look.mode === 'rim' ? stepA(look.alpha) : look.alpha), clip);
      };
      if (sp) { body(u.x + dx, u.y, { above: false, y: sp.y }); body(u.x + dx + sp.dx, u.y + sp.dy, { above: true, y: sp.y + sp.dy }); }
      else body(u.x + dx, u.y, null);
      if (role === 'victim') { inst.draw(ctx, 'sorted', t, i); inst.draw(ctx, 'over', t, i); }
    });
    inst.draw(ctx, 'front', t);

    if (state.anchors) {
      ctx.save(); ctx.globalAlpha = 0.9;
      const dot = (x, y, col) => { ctx.fillStyle = col; ctx.fillRect(Math.round(x) - 1, Math.round(y) - 1, 3, 3); };
      dot(C.tip[0], C.tip[1], '#00ffff');
      scene.victims.forEach((v, i) => {
        ctx.strokeStyle = '#ff00ff'; ctx.lineWidth = 1;
        ctx.strokeRect(v.box.x0 + 0.5, v.box.y0 + 0.5, v.box.x1 - v.box.x0 - 1, v.box.y1 - v.box.y0 - 1);
        dot(inst.marks[i].x, inst.marks[i].y, '#ffff00');
      });
      ctx.restore();
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    inst.draw(ctx, 'screen', t);
  }

  // ───── 타임라인 막대 (fx 시계) ─────
  const PH_COL = ['#2d3550', '#3d2d50', '#50402d', '#7a2c34', '#5a2d2d', '#2d5040', '#2d4050', '#30303a'];
  function drawTimeline() {
    const W = tlc.width, H = tlc.height, tl = inst.timeline(), D = tl.duration, X = (t) => (t / D) * W;
    tctx.fillStyle = '#1d1f29'; tctx.fillRect(0, 0, W, H);
    tl.phases.forEach(([n, a, b], k) => {
      tctx.fillStyle = PH_COL[k % PH_COL.length]; tctx.fillRect(X(a), 0, Math.max(1, X(b) - X(a)), 16);
      tctx.fillStyle = '#ddd'; tctx.font = '10px sans-serif';
      if (X(b) - X(a) > 26) tctx.fillText(n, X(a) + 2, 11);
    });
    tl.freeze.forEach((f) => { tctx.fillStyle = 'rgba(255,255,255,0.18)'; tctx.fillRect(X(f.at), 16, X(f.dur), 8); });
    const rows = {};
    let r = 0;
    tl.events.forEach((e) => {
      if (rows[e.id] == null) rows[e.id] = r++;
      tctx.fillStyle = e.id.startsWith('cut') ? '#e8e4d8' : e.id.startsWith('split') ? '#b8323c' : '#8a8aa0';
      tctx.fillRect(Math.round(X(e.t)), 26 + (rows[e.id] % 5) * 4, 1, 3);
    });
    tl.shakes.forEach((s) => { tctx.fillStyle = '#f0b25a'; tctx.fillRect(Math.round(X(s.at)), 16, 2, 8); });
    if (tl.punch) { tctx.fillStyle = '#6a8cff'; tctx.fillRect(X(tl.punch.at), 44, X(tl.punch.dur), 2); }
  }
  function drawPlayhead(tr) {
    drawTimeline();
    const x = Math.round((inst.fxT(tr) / inst.timeline().duration) * tlc.width);
    tctx.fillStyle = '#fff'; tctx.fillRect(x, 0, 1, tlc.height);
  }

  function readout(t) {
    const ft = inst.fxT(t);
    const tl = inst.timeline();
    const ph = (tl.phases.find(([, a, b]) => ft >= a && ft < b) || ['-'])[0];
    document.getElementById('readout').textContent =
      `real ${t.toFixed(3)}s / ${inst.duration.toFixed(2)}s · fx ${ft.toFixed(3)}s · frame ${Math.round(t * 60)} · phase ${ph}` +
      `${inst.frozen(t) ? ' · FROZEN' : ''}${inst.view(t, 640, 360).z > 1 ? ` · ZOOM ×${inst.view(t, 640, 360).z}` : ''} · speed ${state.speed}× (fx ×${inst.rate.toFixed(2)})`;
    document.getElementById('scrub').value = String(Math.round(t * 1000));
  }

  function frame(t) { render(t); drawPlayhead(t); readout(t); }

  // ───── 조작 ─────
  let last = null;
  function tick(now) {
    if (ready && state.playing) {
      const dt = last == null ? 0 : Math.min(0.1, (now - last) / 1000);
      state.t += dt;
      if (state.t > inst.duration + TAIL) {
        if (state.loop) state.t = 0; else { state.t = inst.duration; state.playing = false; syncPlay(); }
      }
      frame(Math.min(state.t, inst.duration));
    }
    last = now;
    requestAnimationFrame(tick);
  }
  const $ = (id) => document.getElementById(id);
  function syncPlay() { $('play').textContent = state.playing ? '일시정지' : '재생'; }
  function setZoom(z) {
    state.zoom = z;
    cv.style.width = `${640 * z}px`; cv.style.height = `${360 * z}px`;
    tlc.style.width = `${640 * z}px`;
    document.querySelectorAll('[data-zoom]').forEach((b) => b.classList.toggle('on', +b.dataset.zoom === z));
  }
  function wire() {
    $('play').onclick = () => { state.playing = !state.playing; syncPlay(); };
    $('restart').onclick = () => { state.t = 0; state.playing = true; syncPlay(); };
    $('back').onclick = () => { state.playing = false; syncPlay(); state.t = Math.max(0, state.t - STEP); frame(state.t); };
    $('fwd').onclick = () => { state.playing = false; syncPlay(); state.t = Math.min(inst.duration, state.t + STEP); frame(state.t); };
    $('loop').onchange = (e) => { state.loop = e.target.checked; };
    $('scrub').oninput = (e) => { state.playing = false; syncPlay(); state.t = +e.target.value / 1000; frame(state.t); };
    document.querySelectorAll('[data-speed]').forEach((b) => (b.onclick = () => {
      const frac = state.t / inst.duration;
      state.speed = +b.dataset.speed; build(); state.t = frac * inst.duration;
      document.querySelectorAll('[data-speed]').forEach((x) => x.classList.toggle('on', x === b));
      frame(state.t);
    }));
    document.querySelectorAll('[data-zoom]').forEach((b) => (b.onclick = () => setZoom(+b.dataset.zoom)));
    $('seed').onchange = (e) => { state.seed = +e.target.value || 0; build(); frame(state.t); };
    $('reseed').onclick = () => { state.seed = (state.seed * 7919 + 13) % 100000; $('seed').value = state.seed; build(); frame(state.t); };
    const sel = $('bg');
    BGS.forEach((b) => { const o = document.createElement('option'); o.value = b; o.textContent = b; sel.appendChild(o); });
    sel.onchange = (e) => { state.bg = e.target.value; frame(state.t); };
    $('layout').onchange = (e) => { state.layout = e.target.value; build(); frame(state.t); };
    $('anchors').onchange = (e) => { state.anchors = e.target.checked; frame(state.t); };
    const lay = $('layers');
    inst.layerIds().forEach((id) => {
      const L = spec.layers.find((x) => x.id === id);
      const row = document.createElement('div'); row.className = 'row';
      const ph = L.piece && inst.usesPlaceholder(L.piece);
      row.innerHTML = `<label><input type="checkbox" checked> <span class="mono">${id}</span></label>` +
        (L.piece ? ` <span class="mono ${ph ? 'ph' : ''}">${L.piece}${ph ? ' — PLACEHOLDER (code)' : ' — sheet'}</span>` : L.light ? ' <span class="mono">code light</span>' : '');
      row.querySelector('input').onchange = (e) => { state.hidden[id] = !e.target.checked; build(); frame(state.t); };
      lay.appendChild(row);
    });
    setZoom(state.zoom);
  }
  function notes() {
    const ul = $('notes'), add = (html) => { const li = document.createElement('li'); li.innerHTML = html; ul.appendChild(li); };
    const miss = FxPlayer.lint(spec);
    add(miss.length ? `<span class="ph">style 기본값 사용 ${miss.length}개: ${miss.join(', ')}</span>` : 'style 매개변수: 전부 직접 적음 (§1.2-4)');
    const ph = kit.pieces.filter((p) => !sheetFor(p.id)).map((p) => `${p.id} ${p.size.join('×')}×${p.frames}f`);
    if (ph.length) add(`<span class="ph">PLACEHOLDER 조각 (코드로 찍음, Antigravity 그림으로 교체 예정): ${ph.join(', ')}</span>`);
    add('코드 빛: 화면 어둡게(dim), 유닛 어둡게, 칼끝·선 둘레의 부드러운 가산 빛 — 모양 없는 빛만.');
    add('키 이미지: NovelAI 디자인 초안(참고용, 출시·등록 안 함).');
    add(spec.fastForward ? `궁극기 빨리감기: fx 시계 상한 ×${spec.fastForward.cap}, 남색 배경·실루엣·띠·확대는 4×에서도 유지 (§6.2 예외, 전투당 1회).` : '4×: fx 시계 ×2.6 상한, dim·띠는 1×에서만 (§6.2).');
    add('<span class="ph">키트 충돌(주인 승인 대기): 키트 screen.forbidden 에 dim 이 있는데 궁극기 블록이 덮어쓴다.</span>');
    add('코드 쪼개짐: 맞은 몸을 가른 선에서 잘라 윗부분을 선 따라 밀어 그린다(조각 split 은 이음매 빛만).');
  }

  async function boot() {
    await Art.load();
    [spec, kit] = await Promise.all([fetch(SPEC_URL, { cache: 'no-cache' }).then((r) => r.json()), fetch(KIT_URL, { cache: 'no-cache' }).then((r) => r.json())]);
    const need = [CASTER.id, ...VICTIMS.map((v) => v.id), ...BYSTANDERS.map((v) => v.id), ...BGS.map((b) => `bg/battle/${b}`)];
    for (let k = 0; k < 200 && need.some((id) => Art.has(id) && !Art.image(id)); k++) await new Promise((r) => setTimeout(r, 25));
    build();
    wire();
    notes();
    ready = true;
    frame(0);
  }

  // 캡처용
  window.FXP = {
    ready: boot().then(() => true),
    set(o) {
      Object.assign(state, o);
      if (o.speed != null || o.seed != null || o.hidden || o.layout) build();
      if (o.zoom) setZoom(o.zoom);
      state.playing = false; syncPlay();
    },
    renderAt(t) { state.t = t; frame(t); return true; },
    duration: () => inst.duration,
    timeline: () => inst.timeline(),
  };
  requestAnimationFrame(tick);
})();
