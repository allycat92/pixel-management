// 외부 그림(일러스트) 불러오기: assets/art/manifest.json 에 등록된 그림만 쓰고,
// 없는 그림은 각 화면이 기존 코드 생성 도트로 대신한다. (그림 작업 절차는 art/README.md)
'use strict';

const Art = (() => {
  let manifest = {};
  const images = {};

  async function load() {
    try {
      const res = await fetch('assets/art/manifest.json', { cache: 'no-cache' });
      if (res.ok) manifest = await res.json();
    } catch (e) { manifest = {}; }
    // 전투 컷인처럼 캔버스·즉시 표시에 쓰는 그림은 미리 받아 둔다
    Object.entries(manifest).forEach(([id, a]) => {
      const im = new Image();
      im.src = a.file;
      images[id] = im;
    });
  }

  const has = (id) => !!(id && manifest[id]);
  // <img> 요소 (없으면 null)
  function img(id, cls = '') {
    if (!has(id)) return null;
    const i = document.createElement('img');
    i.src = manifest[id].file;
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
  function sheetFor(u) {
    if (!u) return null;
    if (u.art) { const s = sheet(idOf.sheet.fromArt(u.art)); if (s) return s; }
    if (u.mon) return sheet(idOf.sheet.monster(u.mon));
    if (u.capKey) { const s = sheet(idOf.sheet.captain(u.capKey)); if (s) return s; }
    if (u.heroKey) { const s = sheet(idOf.sheet.hero(u.heroKey)); if (s) return s; }
    const lk = u.look || {};
    if (lk.cap) { const s = sheet(idOf.sheet.captain(lk.cap)); if (s) return s; }
    for (const k of [lk.master, lk.adv, u.cls, lk.cls]) {
      if (!k) continue;
      const s = sheet(idOf.sheet.class(k));
      if (s) return s;
    }
    return null;
  }

  return { load, has, img, image, idOf, sheet, anim, sheetFor, count: () => Object.keys(manifest).length };
})();
