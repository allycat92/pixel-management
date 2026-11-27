// FxPlayer — 스펙 JSON(assets/fx/sig/**) 을 캔버스에 레이어로 그린다. docs/plans/effects_design.md §4.3-4.4, §6.1-6.2.
// - 구조(시간·배치·물리·화면 패턴)는 FxSkel 프리셋에서, 색은 키트에서, 그림은 조각 시트(fx/sig/<owner>/<piece>)에서 얻는다.
//   조각 시트가 아직 없으면 FxPlaceholders(코드로 찍은 PLACEHOLDER)가 같은 크기·칸·기준점으로 대신 그린다.
// - 코드 빛은 '모양 없는 빛'만: 화면 어둡게(dim), 유닛 어둡게, 부드러운 가산 빛. 모양이 보이는 선·갈라짐은 조각이 그린다.
// - 결정론: 모든 흔들림·배치·입자는 FxSkel.rng(seed, layer, target) — 같은 시드·같은 t 면 같은 그림 (되감기·한 칸 넘기기 OK).
// - 시계: 스펙의 시간은 fx 시계(초). 배속 speed 에서 fx 시계는 min(speed, 2.6) 배로 간다(§6.2 cap).
//   only1x 표시가 붙은 화면 연출(dim, 띠)은 1배속에서만 (§6.2 "dim/freeze only at 1×").
// 게임(js/battle.js)에는 아직 연결하지 않았다 — 지금은 tools/fxpreview 미리보기 전용.
'use strict';

const FxPlayer = (() => {
  const S = () => FxSkel;
  const FX_CAP = 2.6;

  // 시그니처 스펙: style 매개변수가 전부 직접 적혔는지 (§1.2-4)
  function lint(spec) {
    const missing = [];
    const sig = String(spec.tier || '') !== 'generic';
    const chk = (obj) => { if (obj && obj.preset) S().resolve(obj.preset, obj, { signature: sig, missing }); };
    (spec.layers || []).forEach((L) => { chk(L.clock); chk(L.stagger); chk(L.emitter); chk(L.pieceClock); chk(L.light); });
    if (spec.marks) chk(spec.marks.heights);
    if (spec.actor) chk(spec.actor.spin);
    const sc = spec.screen || {};
    chk(sc.dim); chk(sc.unitDim); chk(sc.letterbox);
    (sc.freeze || []).forEach(chk); (sc.shake || []).forEach(chk);
    return missing;
  }

  function create(spec, kit, scene, opt = {}) {
    const seed = opt.seed == null ? 1 : opt.seed;
    const speed = opt.speed || 1;
    const rate = Math.min(speed, FX_CAP);
    const at1x = speed <= 1;
    const pal = Object.assign({}, kit.colours, (kit.ultimate && kit.ultimate.colours) || {});
    const R = (...p) => S().rng(seed, spec.id, ...p);
    const res = (o, ...salt) => (o && o.preset ? S().resolve(o.preset, o, { rng: R('param', o.preset, ...salt) }) : null);
    const fn = (o) => S().get(o.preset).fn;
    const sheetFor = opt.sheetFor || (() => null);
    const C = scene.caster, V = scene.victims;

    // ───── 표적별 표식(가르는 선이 지나는 점) ─────
    const mk = spec.marks || {};
    const hp = res(mk.heights);
    const heights = hp ? fn(mk.heights)(hp, V.length, R('heights')) : V.map(() => 0.5);
    const marks = V.map((v, i) => {
      const [x, y] = S().anchorFromBox(v.box, 'body', heights[i]);
      return { x: Math.round(x), y: Math.round(y), mirror: v.x < C.x };
    });

    // ───── 레이어별 시작 시각 (fx 시계) ─────
    const startOf = {};   // id → [표적별 시작] 또는 [시작]
    const layers = (spec.layers || []).map((L) => {
      const n = L.per === 'victim' ? V.length : 1;
      let st;
      if (L.after) st = startOf[L.after].map((t) => t + (L.delay || 0));
      else if (L.stagger && L.per === 'victim') {
        const sp = res(L.stagger, L.id);
        st = fn(L.stagger)(sp, V, C, R('stagger', L.id)).map((d) => L.at + d);
      } else st = Array.from({ length: n }, () => L.at);
      startOf[L.id] = st;
      const out = { L, st, clk: res(L.clock, L.id), pclk: res(L.pieceClock, L.id), light: res(L.light, L.id) };
      if (L.emitter) {
        const ep = res(L.emitter, L.id);
        out.ep = ep;
        out.parts = st.map((_, i) => {
          const src = L.per === 'victim' ? V[i] : C;
          let dir = -Math.PI / 2;
          if (L.dir === 'away') dir = Math.atan2(0, src.x - C.x || 1);
          return S().get(L.emitter.preset).spawn(ep, dir, R('emit', L.id, i));
        });
      }
      return out;
    });

    // ───── 화면 ─────
    const sc = spec.screen || {};
    const freeze = (sc.freeze || []).map((f) => res(f));
    const shakes = (sc.shake || []).map((s, i) => ({ p: res(s), sign: R('shake', i)() < 0.5 ? -1 : 1 }));
    const dimP = at1x && sc.dim ? res(sc.dim) : null;
    const udimP = at1x && sc.unitDim ? res(sc.unitDim) : null;
    const lbP = at1x && sc.letterbox ? res(sc.letterbox) : null;
    const env = (o, p, t) => S().get(o.preset).fn(p, t - (o.at || 0));
    const react = spec.victimReact;
    const reactAt = react ? startOf[react.after] : null;

    const fxT = (tr) => tr * rate;

    // 앵커 이름 → 점
    function anchorPt(name, i) {
      if (name === 'mark') return [marks[i].x, marks[i].y];
      if (name === 'self.tip') return C.tip;
      if (name === 'self.chest') return S().anchorFromBox(C.box, 'chest');
      if (name === 'victim.chest') return S().anchorFromBox(V[i].box, 'chest');
      return [C.x, C.y];
    }

    // 조각 한 칸: 등록된 시트가 있으면 그것, 없으면 PLACEHOLDER
    function pieceFrame(id, f) {
      const sh = sheetFor(id);
      if (sh) {
        const fr = sh.frames[Math.min(f, sh.frames.length - 1)];
        return { img: sh.img, sx: fr[0], sy: fr[1], w: sh.cell[0], h: sh.cell[1], ox: sh.origin[0], oy: sh.origin[1], placeholder: false };
      }
      return FxPlaceholders.frame(id, f, pal);
    }
    function blit(ctx, pf, x, y, mirror) {
      const X = Math.round(x), Y = Math.round(y);
      if (!mirror) { ctx.drawImage(pf.img, pf.sx, pf.sy, pf.w, pf.h, X - pf.ox, Y - pf.oy, pf.w, pf.h); return; }
      // 같은 상자 안에서 좌우만 뒤집는다 (기준점 상자가 그대로라 대칭 조각이 1px 밀리지 않는다)
      ctx.save(); ctx.translate(X, 0); ctx.scale(-1, 1);
      ctx.drawImage(pf.img, pf.sx, pf.sy, pf.w, pf.h, -(pf.w - pf.ox), Y - pf.oy, pf.w, pf.h);
      ctx.restore();
    }
    function glow(ctx, x, y, r, a, col) {
      if (a <= 0.004) return;
      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = Math.min(1, a);
      ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
      ctx.restore();
    }

    // 레이어 하나의 표적 i 를 그린다
    function drawLayer(ctx, o, i, t) {
      const L = o.L, t0 = o.st[i], u = t - t0;
      if (u < 0) return;
      const [ax, ay] = anchorPt(L.anchor, i);
      const blend = L.blend || 'source-over';
      if (o.light) {
        const a = S().get(L.light.preset).fn(o.light, u) * L.alpha;
        glow(ctx, ax, ay, L.radius, a, pal[L.colour]);
        return;
      }
      ctx.save();
      ctx.globalCompositeOperation = blend;
      if (o.parts) {
        const ef = S().get(L.emitter.preset).fn;
        o.parts[i].forEach((q, j) => {
          const s = ef(o.ep, q, u);
          if (!s) return;
          if (s.k > 0.82 && (Math.floor(u * 25) + j) % 2) return;   // 끝에서 깜빡이며 사라짐(알파 단계 없이)
          const f = S().get(L.pieceClock.preset).fn(o.pclk, u + q.f0 * 0.09);
          if (f < 0) return;
          blit(ctx, pieceFrame(L.piece, f), ax + s.dx, ay + s.dy, (q.vx < 0) !== (j % 2 === 1));
        });
      } else {
        const f = S().get(L.clock.preset).fn(o.clk, u);
        if (f >= 0) blit(ctx, pieceFrame(L.piece, f), ax, ay, L.per === 'victim' ? marks[i].mirror : C.face < 0);
      }
      ctx.restore();
    }

    const inst = {
      spec, seed, speed, rate, marks,
      duration: spec.duration / rate,
      fxT,
      // 시전자 자세: { pose, flip } — flip 은 시트 기본 방향 대비 반전
      casterPose(tr) {
        const t = fxT(tr), A = spec.actor || {};
        let pose = 'idle';
        (A.track || []).forEach((k) => { if (t >= k.at) pose = k.pose; });
        let flip = false;
        if (A.spin) { const s = S().get('actor.spin').fn(res(A.spin), t); if (s.spinning) flip = s.flip; }
        const map = (A.poses || {})[pose] || ['idle', null];
        return { pose, anim: map[0], cell: map[1], flip };
      },
      // 유닛 숨쉬기 시계 (정지·hitstop 동안 멈춤)
      unitClock(tr) { return S().frozenClock(freeze, fxT(tr)); },
      frozen(tr) { const t = fxT(tr); return freeze.some((f) => t >= f.at && t < f.at + f.dur); },
      victim(i, tr) {
        const t = fxT(tr);
        if (!react) return { hit: false, dx: 0 };
        const u = t - reactAt[i];
        if (u < 0 || u > react.dur) return { hit: false, dx: 0 };
        const away = V[i].x < C.x ? -1 : 1;
        return { hit: true, dx: away * Math.round(react.push * Math.min(1, u / 0.05)) };
      },
      // 유닛 어둡게: role 'caster' | 'other'
      unitDim(tr, role) {
        if (!udimP || role === 'caster') return null;
        const a = env(sc.unitDim, udimP, fxT(tr)) * sc.unitDim.alpha;
        return a > 0.01 ? { colour: pal[sc.unitDim.colour], alpha: a } : null;
      },
      camera(tr) {
        const t = fxT(tr);
        let x = 0, y = 0;
        shakes.forEach((s) => { const [dx, dy] = S().get('screen.shake').fn(s.p, t, s.sign); x += dx; y += dy; });
        return [x, y];
      },
      // slot: 'ground' | 'sorted' | 'over' | 'front' | 'screen'. sorted/over 는 표적 i 마다 그 유닛 바로 뒤에 부른다.
      draw(ctx, slot, tr, i) {
        const t = fxT(tr), W = ctx.canvas.width, H = ctx.canvas.height;
        if (slot === 'ground' && dimP) {
          const a = env(sc.dim, dimP, t) * sc.dim.alpha;
          if (a > 0.004) { ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = pal[sc.dim.colour]; ctx.fillRect(-8, -8, W + 16, H + 16); ctx.restore(); }
        }
        if (slot === 'screen' && lbP) {
          const h = S().get('screen.letterbox').fn(lbP, t);
          if (h > 0) {
            ctx.save(); ctx.fillStyle = pal[sc.letterbox.colour];
            ctx.fillRect(0, 0, W, h); ctx.fillRect(0, H - h, W, h);
            const e = sc.letterbox.edge;
            if (e && t >= e.at && t < e.at + e.dur) { ctx.fillStyle = pal[e.colour]; ctx.fillRect(0, h, W, 1); ctx.fillRect(0, H - h - 1, W, 1); }
            ctx.restore();
          }
        }
        layers.forEach((o) => {
          if (o.L.slot !== slot || (opt.hidden && opt.hidden[o.L.id])) return;
          if (slot === 'sorted' || slot === 'over') { if (o.L.per === 'victim' && i != null) drawLayer(ctx, o, i, t); return; }
          for (let k = 0; k < o.st.length; k++) drawLayer(ctx, o, k, t);
        });
      },
      // 미리보기용: 단계와 사건 (fx 시계, 초)
      timeline() {
        const ev = [];
        layers.forEach((o) => o.st.forEach((s, i) => ev.push({ t: s, id: o.L.id, i })));
        return { phases: (spec.timeline && spec.timeline.phases) || [], events: ev, freeze, shakes: shakes.map((s) => s.p), duration: spec.duration };
      },
      layerIds: () => layers.map((o) => o.L.id),
      usesPlaceholder: (id) => !sheetFor(id),
    };
    return inst;
  }

  return { create, lint, FX_CAP };
})();
