// 도트(픽셀) 스프라이트 생성기: 모든 그래픽을 코드로 직접 찍어낸다
'use strict';

const Sprites = (() => {
  const OUTLINE = '#1b1420';
  const cache = new Map();

  function canvas(w, h) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    return c;
  }

  // 16x16 캐릭터 기본 틀
  // O 외곽선, H 머리카락, S 피부, E 눈, B 옷, A 장식, L 다리, F 신발
  const BODY = [
    '................',
    '.....OOOOOO.....',
    '....OHHHHHHO....',
    '...OHHHHHHHHO...',
    '...OHSSSSSSHO...',
    '...OSSESSESSO...',
    '...OSSSSSSSSO...',
    '....OSSSSSSO....',
    '...OBBBAABBBO...',
    '..OSBBBAABBBSO..',
    '..OSOBBBBBBOSO..',
    '....OBBBBBBO....',
    '....OLLLLLLO....',
    '....OLLOOLLO....',
    '...OFFO..OFFO...',
    '................',
  ];

  function shade(hex, amt) {
    const n = parseInt(hex.slice(1), 16);
    const f = (v) => Math.max(0, Math.min(255, Math.round(v + amt)));
    const r = f(n >> 16), g = f((n >> 8) & 255), b = f(n & 255);
    return '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
  }

  // 머리 장식 덮어쓰기
  function applyHeadgear(px, kind, cls) {
    const set = (x, y, c) => { if (y >= 0 && y < 16) px[y][x] = c; };
    if (kind === 'helmet') {
      const m = '#9aa3ad', d = '#6b737c';
      for (let x = 4; x <= 11; x++) { set(x, 2, m); set(x, 3, x % 3 ? m : d); }
      set(4, 4, m); set(11, 4, m); set(3, 4, OUTLINE); set(12, 4, OUTLINE);
      for (let x = 5; x <= 10; x++) set(x, 1, OUTLINE);
      set(7, 1, cls.accent); set(8, 1, cls.accent); set(7, 0, cls.accent);
    } else if (kind === 'hat') {
      const h = cls.outfit, a = cls.accent;
      // 뾰족한 마법사 모자
      set(9, 0, OUTLINE); set(8, 0, h);
      for (let x = 6; x <= 9; x++) set(x, 1, h);
      set(5, 1, OUTLINE); set(10, 1, OUTLINE);
      for (let x = 2; x <= 13; x++) set(x, 3, x === 2 || x === 13 ? OUTLINE : h);
      for (let x = 4; x <= 11; x++) set(x, 2, h);
      set(3, 2, OUTLINE); set(12, 2, OUTLINE);
      set(6, 2, a); set(9, 3, a);
    } else if (kind === 'hood') {
      const h = cls.outfit, hd = shade(cls.outfit, -15);
      for (let y = 2; y <= 7; y++) for (let x = 3; x <= 12; x++) {
        const c = px[y][x];
        if (c === 'H') px[y][x] = h;
      }
      set(4, 5, h); set(11, 5, h); set(4, 6, hd); set(11, 6, hd);
      // 복면
      for (let x = 5; x <= 10; x++) set(x, 7, cls.accent);
    } else if (kind === 'band') {
      for (let x = 4; x <= 11; x++) set(x, 3, cls.accent);
    }
  }

  // 무기 덮어쓰기 (오른손 쪽)
  function applyWeapon(px, kind, cls) {
    const set = (x, y, c) => { if (x >= 0 && x < 16 && y >= 0 && y < 16) px[y][x] = c; };
    const steel = '#d6dde4', wood = '#8a5a2b';
    if (kind === 'sword') {
      for (let y = 3; y <= 9; y++) set(14, y, steel);
      set(15, 4, OUTLINE); set(13, 4, OUTLINE);
      set(13, 10, cls.accent); set(14, 10, wood); set(15, 10, cls.accent); set(14, 11, wood);
    } else if (kind === 'bow') {
      set(14, 5, wood); set(15, 6, wood); set(15, 7, wood); set(15, 8, wood);
      set(15, 9, wood); set(15, 10, wood); set(14, 11, wood);
      for (let y = 6; y <= 10; y++) set(14, y, '#e8e4d8');
    } else if (kind === 'staff') {
      for (let y = 3; y <= 14; y++) set(14, y, wood);
      set(14, 1, cls.accent); set(13, 2, cls.accent); set(15, 2, cls.accent); set(14, 2, '#ffffff');
      set(14, 0, OUTLINE);
    } else if (kind === 'mace') {
      for (let y = 8; y <= 12; y++) set(14, y, wood);
      set(13, 6, cls.accent); set(14, 6, cls.accent); set(15, 6, cls.accent);
      set(13, 7, cls.accent); set(14, 7, '#fff4b0'); set(15, 7, cls.accent);
      // 성직자 옷의 성표
      set(7, 9, cls.accent); set(8, 9, cls.accent); set(7, 10, cls.accent);
    } else if (kind === 'dagger') {
      set(14, 8, steel); set(14, 9, steel); set(14, 10, '#5a3a20');
      set(13, 10, OUTLINE); set(15, 10, OUTLINE);
    }
  }

  // 용병 외형 → 픽셀 배열(색상 문자열)
  function mercPixels(look) {
    const adv = look.adv && ADV_CLASSES[look.adv];
    const cls = adv ? { ...CLASSES[look.cls], outfit: adv.outfit, accent: adv.accent } : CLASSES[look.cls];
    const px = BODY.map((r) => r.split(''));
    applyHeadgear(px, cls.headgear, cls);
    const pal = {
      O: OUTLINE, H: look.hair, S: look.skin, E: '#1b1420',
      B: cls.outfit, A: cls.accent, L: shade(cls.outfit, -45), F: '#3a2a20',
    };
    // 긴 머리
    if (look.longHair && cls.headgear !== 'hood' && cls.headgear !== 'helmet') {
      px[5][4] = 'H'; px[5][11] = 'H'; px[6][4] = 'H'; px[6][11] = 'H'; px[7][4] = 'H'; px[7][11] = 'H';
    }
    applyWeapon(px, cls.weapon, cls);
    return px.map((row) => row.map((ch) => (ch === '.' ? null : (pal[ch] || ch))));
  }

  // frame: 0 기본, 1 숨쉬기(상체 1px 아래), 2 걷기
  function drawPixels(ctx, px, ox, oy, scale, frame, flip) {
    for (let y = 0; y < px.length; y++) {
      for (let x = 0; x < px[y].length; x++) {
        let c = px[y][x];
        if (!c) continue;
        let dy = y;
        if (frame === 1 && y < 12) dy = y + 1;
        let dx = flip ? 15 - x : x;
        if (frame === 2 && y >= 13) dx += (y === 14 ? (x < 8 ? -1 : 1) : 0);
        ctx.fillStyle = c;
        ctx.fillRect(ox + dx * scale, oy + dy * scale, scale, scale);
      }
    }
  }

  function merc(look, scale = 1, frame = 0, flip = false) {
    const key = `${look.cls}|${look.adv || ''}|${look.skin}|${look.hair}|${look.longHair}|${scale}|${frame}|${flip}`;
    if (cache.has(key)) return cache.get(key);
    const c = canvas(16 * scale, 17 * scale);
    const ctx = c.getContext('2d');
    drawPixels(ctx, mercPixels(look), 0, 0, scale, frame, flip);
    cache.set(key, c);
    return c;
  }

  // 작은 8x8 아이콘
  const ICONS = {
    coin: { g: ['..OOOO..', '.OYYYYO.', 'OYWYYYDO', 'OYYDDYDO', 'OYYDDYDO', 'OYYYYDDO', '.ODDDDO.', '..OOOO..'],
      p: { O: OUTLINE, Y: '#f2c94c', W: '#fff4b0', D: '#c58f1e' } },
    star: { g: ['...OO...', '...YO...', '..OYYO..', 'OOYYYYOO', '.OYYYYO.', '..OYYO..', '.OYOOYO.', '.OO..OO.'],
      p: { O: OUTLINE, Y: '#f2c94c' } },
    sword: { g: ['......OW', '.....OWO', '....OWO.', '.O.OWO..', '..OWO...', '..GO....', '.GOG....', 'G..O....'],
      p: { O: OUTLINE, W: '#d6dde4', G: '#d9a441' } },
    shield: { g: ['OOOOOOOO', 'OBBBWBBO', 'OBBWWWBO', 'OBBBWBBO', 'OBBBWBBO', '.OBBBBO.', '..OBBO..', '...OO...'],
      p: { O: OUTLINE, B: '#4a6fa5', W: '#f2c94c' } },
    map: { g: ['OOOOOOOO', 'OPPPPRPO', 'OPRPPPPO', 'OPPRRPPO', 'OPPPPRPO', 'ORPPPPRO', 'OPPXPPPO', 'OOOOOOOO'],
      p: { O: OUTLINE, P: '#e8d5a3', R: '#a0723c', X: '#c0392b' } },
    orb: { g: ['..OOOO..', '.OPPPPO.', 'OPWPPPPO', 'OPPPPPPO', 'OPPPPPPO', '.OPPPPO.', '..OOOO..', '.OGGGGO.'],
      p: { O: OUTLINE, P: '#9b6ad6', W: '#ffffff', G: '#d9a441' } },
    heart: { g: ['........', '.OO..OO.', 'ORRORRRO', 'ORWRRRRO', 'ORRRRRRO', '.ORRRRO.', '..ORRO..', '...OO...'],
      p: { O: OUTLINE, R: '#d6455d', W: '#ffb3c0' } },
    skull: { g: ['.OOOOOO.', 'OWWWWWWO', 'OWOOWOOW', 'OWOOWOOW', 'OWWWOWWO', '.OWWWWO.', '.OWOWOO.', '..OOOO..'],
      p: { O: OUTLINE, W: '#e8e4d8' } },
    cross: { g: ['...OO...', '..ORRO..', 'OOORROOO', 'ORRRRRRO', 'ORRRRRRO', 'OOORROOO', '..ORRO..', '...OO...'],
      p: { O: OUTLINE, R: '#d6455d' } },
    house: { g: ['...OO...', '..ORRO..', '.ORRRRO.', 'ORRRRRRO', '.OWWWWO.', '.OWDDWO.', '.OWDDWO.', '.OOOOOO.'],
      p: { O: OUTLINE, R: '#9c3b2e', W: '#e8d5a3', D: '#6b4226' } },
  };

  function icon(name, scale = 2) {
    const key = `icon|${name}|${scale}`;
    if (cache.has(key)) return cache.get(key);
    const def = ICONS[name];
    const c = canvas(8 * scale, 8 * scale);
    const ctx = c.getContext('2d');
    def.g.forEach((row, y) => row.split('').forEach((ch, x) => {
      if (ch === '.') return;
      ctx.fillStyle = def.p[ch]; ctx.fillRect(x * scale, y * scale, scale, scale);
    }));
    cache.set(key, c);
    return c;
  }

  // DOM에 넣기 위한 복제본 (캔버스는 한 곳에만 붙일 수 있으므로)
  function clone(src, cls) {
    const c = canvas(src.width, src.height);
    c.getContext('2d').drawImage(src, 0, 0);
    if (cls) c.className = cls;
    return c;
  }

  // ───────── 몬스터 ─────────
  const MONSTER_TPL = {
    imp: [
      '................',
      '................',
      '..O..OOOOOO..O..',
      '..OOOMMMMMMOOO..',
      '...OMMMMMMMMO...',
      '...OMEMMMEMMO...',
      '...OMMMMMMMMO...',
      '....OMTMMTMO....',
      '..O..OMMMMO.....',
      '.ODO.OAAAAO.....',
      '.ODOOAAAAAAO....',
      '..OMOAAAAAAMO...',
      '..O.OAAAAAAOMO..',
      '.....ODDODDO....',
      '.....ODO.ODO....',
      '....OOOO.OOOO...',
    ],
    beast: [
      '................',
      '................',
      '................',
      '..O.O...........',
      '.OMOMO..........',
      'OMMMMMO.........',
      'OEMMMMO.......O.',
      'OMMMMMMOOOOOOOMO',
      '.OTTMMMMMMMMMMDO',
      '..OOMMMMLLMMMMDO',
      '....OMMMMMMMMMDO',
      '....OMDDMMMDDMO.',
      '....OMO.OO.OMMO.',
      '....OMO....OMO..',
      '...OOOO...OOOO..',
      '................',
    ],
    bug: [
      '................',
      '................',
      '................',
      '................',
      '.....OOOOOO.....',
      '....OMMLLMMO....',
      '.O.OMMLMMMMMO.O.',
      'O.OOMMMMMMMMOO.O',
      '.OO.OMMMMMMO.OO.',
      'O..OOEMMMMEOO..O',
      '..O.OMMMMMMO.O..',
      '.O..OMTOOTMO..O.',
      'O..O.OOOOOO.O..O',
      '...O........O...',
      '................',
      '................',
    ],
    brute: [
      '................',
      '.....OOOOOO.....',
      '....OMMMMMMO....',
      '...OMEMMMMEMO...',
      '...OMMMMMMMMO...',
      '...OMTMTTMTMO...',
      '.OOOOMMMMMMOOOO.',
      'OMMMMMMMMMMMMMMO',
      'OMMOMMLLLLMMOMMO',
      'OMMOMMMMMMMMOMMO',
      'ODDOMMMMMMMMODDO',
      '.OO.OAAAAAAO.OO.',
      '....OMMOOMMO....',
      '....OMMOOMMO....',
      '...ODDDOODDDO...',
      '...OOOOOOOOOO...',
    ],
    slime: [
      '................',
      '................',
      '................',
      '................',
      '................',
      '................',
      '......OOOO......',
      '....OOMMMMOO....',
      '...OMLLMMMMMO...',
      '..OMLMMMMMMMMO..',
      '..OMMEMMMMEMMO..',
      '.OMMMMMMMMMMMMO.',
      '.OMMMMMDDMMMMMO.',
      '.ODMMMMMMMMMMDO.',
      '..ODDDDDDDDDDO..',
      '...OOOOOOOOOO...',
    ],
    ghost: [
      '................',
      '.....OOOOOO.....',
      '....OMMMMMMO....',
      '...OMLMMMMMMO...',
      '...OMDDMMDDMO...',
      '...OMDEMMDEMO...',
      '...OMMMMMMMMO...',
      '..OMMMMDDMMMMO..',
      '..OMMMMMMMMMMO..',
      '.OMLMMMMMMMMLMO.',
      '.OMMOMMMMMMOMMO.',
      '..OO.OMMMMMO.O..',
      '.....OMMMMDO....',
      '......OMDDO.....',
      '.......OO.......',
      '................',
    ],
    chest: [
    '................',
    '................',
    '................',
    '................',
    '..OOOOOOOOOOOO..',
    '.OAMMMMMMMMMMAO.',
    '.OMMMMMMMMMMMMO.',
    '.OAAAAAAAAAAAAO.',
    '.OTOTOTOTOTOTOO.',
    '.OOEOOOOOOOOEOO.',
    '.OTOTOTOTOTOTOO.',
    '.OAAAAAAAAAAAAO.',
    '.OMMMMMAAMMMMMO.',
    '.OMMMMMAAMMMMMO.',
    '.ODDDDDDDDDDDDO.',
    '..OOOOOOOOOOOO..',
  ],
  drake: [
      '................',
      '..........OO....',
      '.OO......OAAO...',
      'OEMO....OAAAAO..',
      'OMMMO..OAAAAAAO.',
      '.OTMMO.OAAAAAAAO',
      '..OOMMOAAAAAOOO.',
      '....OMMMMAAOO...',
      '....OMMMMMMMO...',
      '...OMMLLMMMMMO..',
      '...OMMLLMMMMMMO.',
      '....OMMMMMMMMDDO',
      '....OMOOMMOOODDO',
      '....OO..OO...OO.',
      '................',
      '................',
    ],
  };

  function monster(name, scale = 2, frame = 0, flash = false) {
    const key = `mon|${name}|${scale}|${frame}|${flash}`;
    if (cache.has(key)) return cache.get(key);
    const def = ENEMIES[name] || ENEMIES['고블린'];
    const rows = MONSTER_TPL[def.tpl];
    const pal = { O: OUTLINE, T: '#ffffff', A: '#7a5236', ...def.pal };
    const c = canvas(16 * scale, 17 * scale);
    const ctx = c.getContext('2d');
    rows.forEach((row, y) => row.split('').forEach((ch, x) => {
      if (ch === '.') return;
      let dy = y;
      if (frame === 1) dy = def.tpl === 'slime' ? y + (y < 10 ? 1 : 0) : (y < 11 ? y + 1 : y);
      ctx.fillStyle = flash ? (ch === 'O' ? '#ffffff' : '#ffe8e8') : (pal[ch] || pal.M);
      ctx.fillRect(x * scale, dy * scale, scale, scale);
    }));
    cache.set(key, c);
    return c;
  }

  // ───────── 장비 아이콘 ─────────
  const ITEM_ICONS = {
    sword:   ['.......M', '......MO', '.....MO.', '....MO..', '.W.MO...', '..WO....', '.WOW....', 'W.......'],
    bow:     ['..WWO...', '.W..S...', 'W...S...', 'W...SMM.', 'W...S...', 'W...S...', '.W..S...', '..WWO...'],
    staff:   ['.....MM.', '....MLLM', '....MLLM', '.....MM.', '....W...', '...W....', '..W.....', '.W......'],
    dagger:  ['........', '......M.', '.....MO.', '....MO..', '..WMO...', '...W....', '..W.....', '........'],
    mace:    ['....MMM.', '....MLM.', '....MMM.', '...W....', '..W.....', '.W......', 'W.......', '........'],
    plate:   ['.MM..MM.', 'MMMMMMMM', 'MMLMMLMM', '.MMMMMM.', '.MMLLMM.', '.MMMMMM.', '.MM..MM.', '........'],
    leather: ['.WW..WW.', 'WWWWWWWW', 'WWMWWMWW', '.WWWWWW.', '.WWMMWW.', '.WWWWWW.', '.WW..WW.', '........'],
    robe:    ['..C..C..', '.CCCCCC.', '.CCMMCC.', '.CCCCCC.', 'CCCMMCCC', 'CCCCCCCC', 'CCCCCCCC', '........'],
    ring:    ['...LL...', '..LMML..', '...MM...', '..M..M..', '.M....M.', '.M....M.', '..M..M..', '...MM...'],
    amulet:  ['.W....W.', '..W..W..', '...WW...', '...MM...', '..MLLM..', '..MLLM..', '...MM...', '........'],
    herb:    ['....G...', '...GLG..', '..GLGLG.', '...GGG..', '....W...', '...GW...', '..G.W...', '....W...'],
  };

  function itemIcon(base, tier = 1, scale = 2) {
    const key = `item|${base}|${tier}|${scale}`;
    if (cache.has(key)) return cache.get(key);
    const metal = tier ? TIERS[tier].color : '#d6dde4';
    const pal = { M: metal, L: '#ffffff', O: shade(metal, -70), W: '#8a5a2b', S: '#e8e4d8', C: tier >= 3 ? '#3d4a9c' : '#6b5a7a', G: '#4fa84a' };
    if (base === 'herb') pal.L = '#a7d26a';
    const c = canvas(8 * scale, 8 * scale);
    const ctx = c.getContext('2d');
    ITEM_ICONS[base].forEach((row, y) => row.split('').forEach((ch, x) => {
      if (ch === '.') return;
      ctx.fillStyle = pal[ch]; ctx.fillRect(x * scale, y * scale, scale, scale);
    }));
    cache.set(key, c);
    return c;
  }

  return { merc, monster, icon, itemIcon, clone, shade, OUTLINE };
})();
