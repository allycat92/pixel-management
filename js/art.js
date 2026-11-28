// 외부 그림(일러스트) 불러오기: assets/art/manifest.json 에 등록된 그림만 쓰고,
// 없는 그림은 각 화면이 기존 코드 생성 도트로 대신한다. (그림 작업 절차는 art/README.md)
'use strict';

const Art = (() => {
  let manifest = {}, manifestPending = false;
  const images = {};
  // 시트 PNG 는 같은 이름으로 덮어쓴다. manifest 만 새로 받으면 브라우저가 옛 PNG 를 새 칸 정보로 그릴 수 있다(달리기 칸이 비어 보임).
  // 그래서 그림 주소에 항목 내용의 짧은 해시(?v=)를 붙인다 — 항목(크기·동작)이 바뀌면 주소도 바뀐다.
  // 항목이 그대로인 다시 그리기(같은 크기·칸)는 주소가 같으므로 tools/serve.py(no-cache)나 강력 새로고침이 있어야 새 PNG 가 보인다.
  function verOf(entry) {
    const str = JSON.stringify(entry) || '';
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    return h.toString(36);
  }
  const urlOf = (entry) => (entry && typeof entry.file === 'string' ? `${entry.file}${entry.file.includes('?') ? '&' : '?'}v=${verOf(entry)}` : '');

  // 처음 받은 시트가 실패하면 두 번만 다시 받는다. 그동안 실패한 Image 를
  // 남겨 두어 beforeBattle 의 첫 프레임 대기를 늘리지 않는다.
  const RETRY_MS = [1000, 3000];
  function retrySheet(id, url, failed, n = 0) {
    if (n >= RETRY_MS.length || images[id] !== failed) return;
    setTimeout(() => {
      if (images[id] !== failed) return;
      const next = new Image();
      next.addEventListener('load', () => {
        if (images[id] !== failed) return;
        images[id] = next;
        delete sheetCache[id];
      }, { once: true });
      next.addEventListener('error', () => retrySheet(id, url, failed, n + 1), { once: true });
      next.src = url + '&r=' + (n + 1);
    }, RETRY_MS[n]);
  }

  async function load() {
    manifestPending = true;
    try {
      try {
        const res = await fetch('assets/art/manifest.json', { cache: 'no-cache' });
        if (res.ok) manifest = await res.json();
      } catch (e) { manifest = {}; }
      // 전투 컷인처럼 캔버스·즉시 표시에 쓰는 그림은 미리 받아 둔다
      Object.entries(manifest).forEach(([id, a]) => {
        const im = new Image(), url = urlOf(a);
        images[id] = im;
        if (a?.sheet && url) {
          im.addEventListener('error', () => retrySheet(id, url, im), { once: true });
        }
        im.src = url;
      });
    } finally { manifestPending = false; }
  }

  const has = (id) => !!(id && manifest[id]);
  // <img> 요소 (없으면 null)
  function img(id, cls = '') {
    if (!has(id)) return null;
    const i = document.createElement('img');
    i.src = urlOf(manifest[id]);
    i.alt = '';
    i.className = `art ${cls}`;
    i.draggable = false;
    return i;
  }

  // 인물별 그림 id
  const idOf = {
    merc: (m) => (m.cap ? `portrait/captain/${m.cap}` : m.hero ? `portrait/hero/${m.hero}` : null),
    look: (look) => (look && look.cap ? `portrait/captain/${look.cap}` : look && look.hcls ? null : null),
    captain: (key) => `portrait/captain/${key}`,
    hero: (key) => `portrait/hero/${key}`,
    boss: (cal) => `portrait/boss/${cal}`,
    event: (key) => `event/${key}`,
    // 전투용 스프라이트 시트 id
    sheet: {
      captain: (key) => `sheet/captain/${key}`,
      hero: (key) => `sheet/hero/${key}`,
      class: (key) => `sheet/class/${key}`,
      monster: (name) => `sheet/monster/${name}`,
      // 'portrait/captain/x' → 'sheet/captain/x'
      fromArt: (art) => (art && art.startsWith('portrait/') ? `sheet/${art.slice(9)}` : null),
    },
  };

  // 캔버스에 그릴 그림 (불러오기가 끝난 것만)
  const image = (id) => (images[id] && images[id].complete && images[id].naturalWidth ? images[id] : null);

  // ───────── 스프라이트 시트 ─────────
  // manifest 의 sheet 항목: { cell:[w,h], anchor:[x,y], facing, frames:[[x,y]...], anims:{ idle:{from,to,ms[]}, ... } }
  //   tint (직업 시트만, 선택): { outfit:['#rrggbb'...], accent:[...] } — 제복·장식에 쓴 열쇠 색. 전투에서 진영 색으로 바꿔 칠한다.
  // 불러오기가 끝난 시트만 { img, meta } 로 돌려준다 (없으면 null → 코드 생성 도트로 대신)
  const sheetCache = {};
  function sheet(id) {
    if (!id || !manifest[id] || !manifest[id].sheet) return null;
    const im = image(id);
    if (!im) return null;
    let s = sheetCache[id];
    if (!s) {
      const meta = manifest[id].sheet;
      const anims = {};
      Object.entries(meta.anims || {}).forEach(([k, a]) => {
        const ms = a.ms && a.ms.length ? a.ms : Array.from({ length: a.to - a.from + 1 }, () => 120);
        anims[k] = { from: a.from, to: a.to, ms, total: ms.reduce((x, y) => x + y, 0) };
      });
      if (!anims.idle) anims.idle = { from: 0, to: 0, ms: [1000], total: 1000 };
      s = sheetCache[id] = { id, img: im, meta: { ...meta, facing: meta.facing || 1, anims } };
    }
    return s;
  }
  // 애니메이션 고르기: 없는 동작은 비슷한 것으로 (walk/attack/hit → idle, cast → attack)
  const ANIM_FALLBACK = { cast: 'attack', walk: 'idle', attack: 'idle', hit: 'idle', die: 'hit' };
  function anim(meta, name) {
    let n = name;
    for (let i = 0; i < 4 && n; i++) {
      if (meta.anims[n]) return meta.anims[n];
      n = ANIM_FALLBACK[n];
    }
    return meta.anims.idle;
  }
  // 전투 유닛 → 시트: 직속 단원은 초상화 id 에서, 일반 병사는 직업(상위 → 기본), 괴물은 이름으로
  function matchSheet(u, read) {
    if (!u) return null;
    if (u.art) { const s = read(idOf.sheet.fromArt(u.art)); if (s) return s; }
    if (u.mon) return read(idOf.sheet.monster(u.mon));
    if (u.capKey) { const s = read(idOf.sheet.captain(u.capKey)); if (s) return s; }
    if (u.heroKey) { const s = read(idOf.sheet.hero(u.heroKey)); if (s) return s; }
    const lk = u.look || {};
    if (lk.cap) { const s = read(idOf.sheet.captain(lk.cap)); if (s) return s; }
    // 제복 색이 필요한 직업 시트는 바꿔 칠할 열쇠 색(sheet.tint)이 있는 것만 허용한다.
    for (const k of [lk.master, lk.adv, u.cls, lk.cls]) {
      if (!k) continue;
      const id = idOf.sheet.class(k);
      if (lk.tint && !manifest[id]?.sheet?.tint) continue;
      const s = read(id);
      if (s) return s;
    }
    return null;
  }
  const sheetFor = (u) => matchSheet(u, sheet);

  // 준비 여부에는 가장 먼저 등록된 후보를 쓴다. 대장 시트가 아직 오는데
  // 일반 직업 시트만 준비됐다고 시작하지 않는다. 실패한 그림은 다음 후보로 넘긴다.
  const PENDING_SHEET = Symbol('pending sheet');
  function sheetReadyState(id) {
    const im = images[id];
    if (!im || !manifest[id]?.sheet) return null;
    return im.complete ? (im.naturalWidth ? im : null) : PENDING_SHEET;
  }

  // 첫 프레임 하나의 기한: manifest도 같은 1.5초 안에서 기다린다.
  // 관련 시트만 지켜보고, 이미 준비됐거나 그릴 것이 없으면 즉시 시작한다.
  // 반환한 함수는 결과 보기·새 게임에서 아직 기다리는 관전을 취소한다.
  function beforeBattle(units, start) {
    const pending = () => manifestPending || units.some((u) => matchSheet(u, sheetReadyState) === PENDING_SHEET);
    const deadline = performance.now() + 1500;
    if (!pending()) { start(); return null; }
    let timer;
    const check = () => {
      const left = deadline - performance.now();
      if (left <= 0 || !pending()) start();
      else timer = setTimeout(check, Math.min(30, left));
    };
    timer = setTimeout(check, 30);
    return () => clearTimeout(timer);
  }

  return { load, has, img, image, idOf, sheet, anim, sheetFor, beforeBattle, count: () => Object.keys(manifest).length };
})();
