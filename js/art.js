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
  };

  // 캔버스에 그릴 그림 (불러오기가 끝난 것만)
  const image = (id) => (images[id] && images[id].complete && images[id].naturalWidth ? images[id] : null);

  return { load, has, img, image, idOf, count: () => Object.keys(manifest).length };
})();
