// 그림 요청서 생성기: 게임 데이터(외형·직업·사연)에서 그림 요청서를 만든다.
// 실행: node tools/art/requests.js  → art/requests/phase{1,2,3}.json / .md
//   1단계 초상화·이벤트, 2단계 배경, 3단계 전투 캐릭터 시트 (tools/art/sheets.py 가 처리)
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..', '..');
const ctx = { console };
vm.createContext(ctx);
['data', 'classes', 'world', 'content'].forEach((f) => {
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'js', `${f}.js`), 'utf8').replace("'use strict';", ''), ctx, { filename: f });
});
const D = vm.runInContext('({ CAPTAINS, CAPTAIN_CLASSES, HEROES, HERO_CLASSES, FACTIONS, CLASSES, STARTER_CAPTAINS, ENEMIES })', ctx);

// 인물의 체형·나이대 설정 (그림 일관성을 위한 아트 설정)
const FIGURE = {
  blademaster: 'lean man in his thirties, a thin scar across one cheek, headband, calm killer eyes',
  ironwall: 'broad-shouldered woman in her forties, braided auburn hair, carries a huge tower shield',
  tactician: 'sharp-eyed woman in her thirties, long dark-blue hair, officer hat, holds a baton-like staff',
  lancer: 'weathered man in his late thirties, dented knight helmet under his arm or on, long lance',
  huntress: 'wiry woman in her twenties, freckles, ponytail, snare ropes on her belt, short bow',
  hedgemage: 'young man in his twenties, messy blond hair, patched wizard hat, holds a crooked staff with a small flame',
  fieldmedic: 'stern woman in her forties, dark hair tied back, bandage roll and satchel, red-cross-like armband',
  fixer: 'slick man in his thirties, slicked-back black hair, half-hood, twirls a short knife',
  veteran: 'old man in his sixties, white hair and beard, battered helmet, many old scars, kind but tough',
  windhunter: 'tanned woman in her twenties, long black hair blowing in the wind, green headband, longbow',
  shadowlord: 'cunning man in his forties, rat-like grin, hood, gold rings, dagger',
  bard: 'flamboyant young man, long red hair, feathered hat, lute on his back and a rapier',
  beastmaster: 'dark-skinned woman in her thirties, long black hair, wolf-fur mantle, a grey wolf beside her',
  runesmith: 'stout bearded man in his forties, orange beard, glowing blue runes on his hammer and armor',
  pilgrim: 'gentle young woman, long blonde hair, barefoot pilgrim robes, holy mace and a prayer charm',
  spellblade: 'elegant man in his thirties, long silver hair, sword glowing with blue magic',
  saintknight: 'noble woman knight in her twenties, long golden hair, white and gold plate armor, holy mace',
  hexer: 'pale woman in her thirties, long dark-blue hair, wide witch hat, green curse flames in her palm',
  liberator: 'dark-skinned muscular man, shaved head, broken shackles still on his wrists, chain weapon',
  admiral: 'elderly woman in her sixties, short grey hair, navy admiral coat with gold trim, crossbow',
  elfwarden: 'tall elf woman, long silver hair, pointed ears, green leaf-patterned cloak, elegant longbow',
  warlord: 'huge man in his forties, red hair and beard, horned helmet, war axe, battle scars',
  khan: 'nomad man in his thirties, long black braids, fur-trimmed coat, composite bow, steppe warrior',
  siegemaster: 'engineer man in his forties, brass goggles on his helmet, soot-stained, heavy crossbow',
  inquisitorlord: 'severe man in his fifties, black hair, deep red hooded inquisitor robes, burning brand',
  pirateking: 'confident woman in her thirties, long crimson hair, tricorn hat, cutlass and hook chain',
  frostjarl: 'tall man in his thirties, long blond hair and braided beard, frost-covered armor, axe',
  dragonslayer: 'battle-hardened woman in her thirties, long blonde hair, dragon-scale armor, greatsword',
  demonhunter: 'grizzled man in his fifties, grey stubble, dark hood, silver bullets and a holy mace',
  archmagus: 'ancient wise woman, very long white hair, star-embroidered robes, glowing staff',
  lightbearer: 'radiant young woman, long golden hair, white robes, soft light around her hands',
  shadowqueen: 'dangerous elegant woman in her thirties, long black hair, dark hood, twin daggers',
  titan: 'giant man with giant-blood, long brown hair, enormous build, stone-like skin, huge maul',
};
const HERO_FIGURE = {
  kai: 'young elf man, pointed ears, long blond hair, green ranger cloak, silver longbow',
  seraphine: 'young woman, pale, blonde hair, torn white saint robes with a red sash, sorrowful but kind',
  lyra: 'young woman in a white half-mask, dark violet outfit, hood, quick daggers, mischievous smile',
  grom: 'massive clan warrior man, brown skin, scarred, arena champion belt, greatsword',
  astel: 'young man scholar-mage, glasses, purple robes with gold embroidery, floating spellbook',
  marisol: 'woman pirate captain in her thirties, tricorn hat, navy coat, flintlock pistol and bow',
  oswin: 'old knight commander, grey hair, rusted silver plate armor with a faded royal crest',
};

const STYLE_TAIL = 'Pixel art portrait in a 16-bit fantasy JRPG style. Bust shot (head and shoulders), facing slightly to the left, three-quarter view. Limited palette (about 32 colors), clean dark outline (#1b1420), flat cel shading with light from the top-left, no anti-aliasing, no gradients, no text, no watermark, no frame. Transparent background (if transparency is not possible, use a flat #2a2033 background).';

const hex = (h) => h;
function lookText(look, cls) {
  return `skin ${hex(look.skin)}, hair ${hex(look.hair)}${look.longHair ? ' (long)' : ''}, outfit main color ${cls.outfit}, accent color ${cls.accent}`;
}

const items = [];
// 용병대장 33명
Object.entries(D.CAPTAINS).forEach(([key, C]) => {
  const CC = D.CAPTAIN_CLASSES[key];
  items.push({
    id: `portrait/captain/${key}`, file: `captain_${key}.png`, kind: 'portrait', size: '1024x1024', out: '128x128',
    name: `${C.name} — ${C.title} (${CC.name})`,
    prompt: `${FIGURE[key]}. Class: ${CC.name} (${CC.style}-type mercenary captain). ${CC.desc} Colors: ${lookText(C.look, CC)}. Weapon: ${CC.weapon}. ${STYLE_TAIL}`,
  });
});
// 특별 용병 7명
Object.entries(D.HEROES).forEach(([key, h]) => {
  const H = D.HERO_CLASSES[h.hcls];
  items.push({
    id: `portrait/hero/${key}`, file: `hero_${key}.png`, kind: 'portrait', size: '1024x1024', out: '128x128',
    name: `${h.name} — ${h.title} (${H.name})`,
    prompt: `${HERO_FIGURE[key]}. Class: ${H.name} (${H.style}-type). Colors: ${lookText(h.look, H)}. Weapon: ${H.weapon}. ${STYLE_TAIL}`,
  });
});
// 재앙 수장 2
items.push({ id: 'portrait/boss/beasts', file: 'boss_beasts.png', kind: 'portrait', size: '1024x1024', out: '128x128',
  name: '고룡 이그니스 (마물 군단 수장)',
  prompt: `Ignis, an ancient black dragon with crimson glowing cracks in its scales and burning orange eyes, head and neck bust, menacing. ${STYLE_TAIL}` });
items.push({ id: 'portrait/boss/demons', file: 'boss_demons.png', kind: 'portrait', size: '1024x1024', out: '128x128',
  name: '마왕 베르녹스 (마왕군 수장)',
  prompt: `Vernox the Demon Lord, dark purple skin, great curved horns, crown of black iron, glowing golden eyes, cape of shadow, bust. ${STYLE_TAIL}` });

// 이벤트 그림
const EV_TAIL = 'Wide 16:9 pixel art illustration in a 16-bit fantasy JRPG style, cinematic composition, limited palette (about 48 colors), clean pixel clusters, no anti-aliasing, no text, no watermark, no UI.';
const EVENTS = [
  ['start', '길드 창설 (새 게임)', 'A modest mercenary guild hall at dusk in a medieval town, a wolf-head banner (silver wolf on dark red) hanging over the door, warm light from windows, a few mercenaries gathering.'],
  ['win', '길드 등급 S 달성', 'Triumphant mercenary guild hall decorated with banners of many factions, crowds cheering, golden morning light, the silver wolf banner raised high.'],
  ['rise_beasts', '재앙 대두 — 마물 군단', 'An ancient black dragon with crimson cracks rising from a volcanic mountain range (the Dragon Spine), wyverns and monsters pouring down the slopes, red sky.'],
  ['rise_demons', '재앙 대두 — 마왕군', 'A gate to the demon realm tearing open in a misty swamp monastery, the Demon Lord stepping out with demons and undead legions, purple and green sky.'],
  ['destroyed', '세력 멸망', 'A fallen castle burning at night, torn faction banners on the ground, refugees leaving along a road, somber mood.'],
  ['final', '최종 결전', 'Three mercenary companies charging up toward a colossal dark lair under a stormy sky, banners flying, the final battle of the age.'],
  ['savior', '엔딩 — 대륙의 구원자', 'Dawn breaking over a recovering continent, the mercenary guild standing on a hill with their banners, people celebrating in the valley below.'],
  ['darkness', '엔딩 — 암흑시대', 'The continent swallowed by darkness, the sky blotted out by dragon wings or demon smoke, ruined towns, the last torch going out.'],
  ['bankrupt', '엔딩 — 파산', 'An empty guild hall with dust and cobwebs, a closed sign on the door, a lone wolf banner fallen to the floor, rainy grey light.'],
];
EVENTS.forEach(([key, name, desc]) => items.push({
  id: `event/${key}`, file: `event_${key}.png`, kind: 'event', size: '1536x864', out: '480x270', name, prompt: `${desc} ${EV_TAIL}`,
}));

// ───────── 2단계: 배경 ─────────
const BG_TAIL = 'Pixel art background in a 16-bit fantasy JRPG style, limited palette (about 48 colors), clean pixel clusters, no anti-aliasing, no text, no watermark, no UI, NO characters or creatures.';
const BATTLE_BGS = [
  ['plains', '평원', 'Open green grassland under a bright blue sky, distant rolling hills, a few wildflowers'],
  ['forest', '숲', 'Edge of a dense old forest, tall dark trees at the back, mossy clearing in front'],
  ['swamp', '늪지', 'Murky swamp with dead trees, reeds and shallow dark water at the back, foggy grey-green sky'],
  ['desert', '사막', 'Red-orange desert with dunes and sandstone mesas, hot orange sky'],
  ['frost', '설원', 'Snowy canyon with icy cliffs and pine trees, pale blue sky'],
  ['mountain', '화산 산맥', 'Volcanic mountain range with lava cracks and smoke, dark red sky (the Dragon Spine)'],
  ['holy', '성역', 'Sacred pilgrimage grounds with white stone ruins, a distant cathedral spire, calm golden sky'],
  ['coast', '해안', 'Rocky seashore with a harbor town in the distance, sea horizon, blue sky with gulls far away'],
];
const phase2 = BATTLE_BGS.map(([key, name, desc]) => ({
  id: `bg/battle/${key}`, file: `bg_battle_${key}.png`, kind: 'background', size: '1536x864', out: '640x360',
  name: `전투 배경 — ${name}`,
  prompt: `${desc}. Moody, richly painted HD pixel-art battlefield in a modern indie 2D game style, slightly dark and atmospheric. Layered depth: distant scenery and tree line in the top third, a mid layer of bushes, rocks, ruins or fences along the horizon, and a wide, FLAT, open, walkable ground area in the lower two thirds seen from a slight high angle (textured soil, scattered grass tufts and small stones, a faint dirt path). Keep the center of the ground calm and low-contrast so small character sprites stay readable; put denser foliage only near the left and right edges. ${BG_TAIL}`,
}));
phase2.push({
  id: 'bg/guild/day', file: 'bg_guild_day.png', kind: 'background', size: '1536x576', out: '320x120',
  name: '길드 홀 실내 — 낮',
  prompt: 'Interior of a cozy medieval mercenary guild hall, wide side view: wooden bar counter with bottles on the left, a quest board with paper notices in the middle, a dark red banner with a silver wolf head, a stone fireplace on the right, wooden plank floor occupying the bottom third, warm daylight from windows. Empty room. ' + BG_TAIL,
});
phase2.push({
  id: 'bg/guild/night', file: 'bg_guild_night.png', kind: 'background', size: '1536x576', out: '320x120',
  name: '길드 홀 실내 — 밤',
  prompt: 'The same mercenary guild hall interior at night (same layout: bar on the left, quest board in the middle, wolf banner, fireplace on the right, wooden floor in the bottom third), lit by fireplace and candles, windows show a starry night. Empty room. ' + BG_TAIL,
});

const out = { version: 1, phase: 1, inbox: 'art/inbox/', items };
fs.writeFileSync(path.join(ROOT, 'art/requests/phase1.json'), JSON.stringify(out, null, 2) + '\n');

const md = [
  '# 그림 요청서 — 1단계 (초상화 + 이벤트 그림)',
  '',
  '> 이 파일은 `node tools/art/requests.js`로 게임 데이터에서 자동 생성된다. 직접 고치지 말고 생성기를 고칠 것.',
  '> 공통 규칙은 `art/STYLE.md`, 작업 절차는 `art/README.md`를 따른다.',
  '',
  `총 ${items.length}장 · 결과물은 \`art/inbox/<file>\`에 PNG로 넣는다.`,
  '',
];
let cur = '';
items.forEach((it) => {
  const sec = it.id.startsWith('portrait/captain') ? '## 용병대장 초상화' : it.id.startsWith('portrait/hero') ? '## 특별 용병 초상화'
    : it.id.startsWith('portrait/boss') ? '## 재앙 수장 초상화' : '## 이벤트 그림';
  if (sec !== cur) { md.push(sec, ''); cur = sec; }
  md.push(`### ${it.name}`, `- 파일: \`${it.file}\` · 생성 크기: ${it.size} · 게임 내 크기: ${it.out}`, '', '```', it.prompt, '```', '');
});
fs.writeFileSync(path.join(ROOT, 'art/requests/phase1.md'), md.join('\n'));
console.log(`requests: ${items.length} items`);

fs.writeFileSync(path.join(ROOT, 'art/requests/phase2.json'), JSON.stringify({ version: 1, phase: 2, inbox: 'art/inbox/', items: phase2 }, null, 2) + '\n');
const md2 = [
  '# 그림 요청서 — 2단계 (배경)',
  '',
  '> `node tools/art/requests.js`로 자동 생성된다. 공통 규칙은 `art/STYLE.md`, 작업 절차는 `art/README.md`.',
  '> 배경에는 **인물·괴물을 넣지 않는다.** 게임이 그 위에 유닛을 그린다.',
  '',
  `총 ${phase2.length}장 · 결과물은 \`art/inbox/<file>\`에 PNG로 넣는다. 배경은 투명이 아니라 꽉 찬 그림.`,
  '',
];
phase2.forEach((it) => md2.push(`### ${it.name}`, `- 파일: \`${it.file}\` · 생성 크기: ${it.size} · 게임 내 크기: ${it.out}`, '', '```', it.prompt, '```', ''));
fs.writeFileSync(path.join(ROOT, 'art/requests/phase2.md'), md2.join('\n'));
console.log(`phase2 requests: ${phase2.length} items`);

// ───────── 3단계: 전투 캐릭터 시트 ─────────
// 그림 모델은 "핵심 자세 4개(1x4 가로 띠)"만 크게 그린다. 칸 맞추기·축소·팔레트·숨쉬기 idle·시트 조립·등록은
// tools/art/sheets.py 가, 걷기·돌진·번쩍임·VFX 는 게임 엔진이 맡는다. 규격은 art/STYLE.md '전투 캐릭터'.
const SHEET_TAIL = [
  'FORMAT: one PNG, 1536x1024 (landscape). The SAME character drawn FOUR times in ONE horizontal row, evenly spaced, left to right:',
  '(1) idle battle-ready stance, (2) attack wind-up (weapon drawn back / spell gathering), (3) attack strike at full extension, (4) hit reaction (recoiling backwards, wincing).',
  'Every copy: full body head to toe, SAME size and SAME scale, all four pairs of feet standing on ONE common horizontal baseline at about 85% of the image height,',
  'each figure about 40% of the image height (the same character scale as the style anchor), generous empty space around each figure; figures and weapons never touch or overlap each other or the image border.',
  'All four face RIGHT in a front three-quarter view.',
  'STYLE: high-quality HD pixel art for a modern 2D fantasy tactics game; humanoids are 4 heads tall (head = 1/4 of the standing height; NOT chibi),',
  'creatures keep natural proportions at the same pixel scale; wide dynamic stance with bent knees, light from the upper left,',
  'readable silhouette, muted hue-shifted palette (shadows shift toward purple/blue, highlights toward warm yellow), dark desaturated (NOT pure black) outline used selectively,',
  'soft rim light on one side, flat cel shading with 2-3 tones, crisp pixel clusters, no anti-aliasing blur.',
  'BACKGROUND: perfectly flat solid magenta #FF00FF everywhere (chroma key), no gradient, no floor, no cast shadow, no scenery.',
  'NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines).',
].join(' ');
const ANCHOR_NOTE = 'Match the approved style anchor art/inbox/sheet_captain_blademaster.png on the art-inbox branch: its rendering, outline, palette treatment, lighting and character scale.';
const NAI_TAIL = 'four heads tall, full body, three-quarter view, facing right, wide stance, bent knees, fighting stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow';
const NAI_MONSTER_TAIL = 'full body, three-quarter view, facing right, battle stance, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow';
const NAI_NEG = 'lowres, bad anatomy, bad hands, text, watermark, signature, logo, multiple views, reference sheet, cropped, out of frame, blurry, background scenery, floor, ground shadow, drop shadow, extra arms, extra legs, gradient background';

// 색 이름 (NovelAI 태그용): 16진수 → 가장 가까운 이름
const COLOR_NAMES = {
  black: '#1b1420', 'dark brown': '#2b1d14', brown: '#5a3720', auburn: '#a8642a', blonde: '#e3c565', grey: '#c9c2b8',
  white: '#f2ecd8', red: '#8c2f2f', crimson: '#7a2418', 'dark crimson': '#3a1018', 'dark blue': '#3a3f6b', navy: '#1a2a4a',
  blue: '#3d5a9c', teal: '#2e8a8a', green: '#3f7a3a', 'dark green': '#2a4a3a', olive: '#4a5a2a', purple: '#5a4a7a',
  'dark purple': '#3a1a5a', 'lime green': '#a7d26a', magenta: '#7a2a5a', gold: '#d9a441', yellow: '#f2c94c', orange: '#c58f1e', 'slate grey': '#4a5a6a',
  charcoal: '#2a2a2a', 'dark grey': '#3a3a4a', 'olive grey': '#5a5a4a', tan: '#c68a5c', silver: '#c9ced6', 'brown leather': '#5a4a3a',
};
const rgbOf = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
function colorName(hexv) {
  const c = rgbOf(hexv);
  let best = 'grey', bd = 1e9;
  Object.entries(COLOR_NAMES).forEach(([n, h]) => {
    const d = rgbOf(h).reduce((s, v, i) => s + (v - c[i]) ** 2, 0);
    if (d < bd) { bd = d; best = n; }
  });
  return best;
}
const HEADGEAR_TAG = { band: 'headband', helmet: 'helmet', hat: 'hat', hood: 'hood', none: '' };
const WEAPON_TAG = { sword: 'holding sword', bow: 'holding bow, quiver', staff: 'holding staff', mace: 'holding mace', dagger: 'holding dagger' };
const genderTag = (text) => (/\b(woman|girl)\b/i.test(text) ? '1girl' : '1boy');

// 손으로 쓴 인물 묘사(figure)가 머리·무기를 이미 말하면 게임 데이터에서 만든 태그를 덧붙이지 않는다
// (예: 'war axe' 뒤에 'holding sword', 'shaved head' 뒤에 'dark brown hair' 가 붙어 NovelAI 가 섞어 그리던 문제)
const FIG_HAIR_RE = /hair|bald|shaved/i;
const FIG_HAIR_LEN_RE = /long|short|bald|shaved|ponytail|braid|bun\b/i;
const FIG_WEAPON_RE = /sword|blade|axe|bow|crossbow|staff|wand|mace|dagger|rapier|cutlass|lance|spear|halberd|maul|hammer|chain|knife|flail|scythe|whip|claw/i;
function naiFromFigure(figure, look, cls) {
  const len = look.longHair ? 'long hair' : 'short hair';
  const hair = !FIG_HAIR_RE.test(figure) ? `${colorName(look.hair)} hair, ${len}`
    : /hair/i.test(figure) && !FIG_HAIR_LEN_RE.test(figure) ? len : null;
  const parts = [genderTag(figure), 'solo', figure.replace(/\.$/, ''), hair,
    `${colorName(cls.outfit)} outfit`, `${colorName(cls.accent)} trim`, HEADGEAR_TAG[cls.headgear],
    FIG_WEAPON_RE.test(figure) ? null : WEAPON_TAG[cls.weapon]];
  return parts.filter(Boolean).join(', ');
}
const nai = (charTags, tail = NAI_TAIL) => ({ prompt: `${charTags}, ${tail}`, negative: NAI_NEG });

const phase3 = [];
const sheetItem = (o) => ({ kind: 'sheet', size: '1536x1024', out: `${o.cell || 80}x${o.cell || 80} cells, body ~${o.height || 64}px`, ...o });

// 1) 창설 후보 대장 9명 — GPT handoff 꾸러미(art/requests/phase3/captain_<key>/, tools/art/handoff.py)를 따른다.
//    주인이 고른 NovelAI 초안(art/concepts/selections.json)은 디자인 참고만, 자세·비율은 posekit 가이드, 화풍은 바렌(앵커).
const SEL = JSON.parse(fs.readFileSync(path.join(ROOT, 'art/concepts/selections.json'), 'utf8'));
const ANCHOR = 'art/inbox/sheet_captain_blademaster.png';
// 앵커는 art-inbox 브랜치에 올라온 GPT 그림이다 (claude 브랜치의 같은 경로도 이제 같은 GPT 판; 예전 NovelAI 판은 교체됐다).
const ANCHOR_REF = `${ANCHOR} on the art-inbox branch`;
const PKG = (key) => `art/requests/phase3/captain_${key}`;
const GUIDES = ['guide_1_idle.png', 'guide_2_windup.png', 'guide_3_strike.png', 'guide_4_hit.png'];
const GUIDED_TAIL = [
  'FORMAT: one PNG, 1536x1024 (landscape), the SAME character four times in ONE row, left to right: (1) idle, (2) attack wind-up, (3) attack strike, (4) hit reaction.',
  'Match guide_strip.png of the package EXACTLY: same poses, limb lengths, proportions, size and position of each figure;',
  'the lowest pixel of every figure (the soles) on y=870 (85% of the height); head = 110 px for every character (standing height would be 440 px, but the guide idle pose is crouched, so idle top-of-head to sole is about 400 px; headgear and weapons are extra);',
  'at least 32 px of empty magenta between figures and from the border. Deliver the 1x4 row only (no 2x2 grid, no single pose).',
  'STYLE: 4 heads tall (head = 1/4 of the standing height, NOT chibi), front three-quarter view facing RIGHT, light from the upper left,',
  'high-quality HD pixel art, muted hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones,',
  'dark desaturated NON-black outline used selectively, soft rim light, readable at 1x (~64 px tall) on a dark battlefield.',
  'The concept draft is a DESIGN reference only (costume, colours, hair, marks, weapon) - never copy its proportions, rendering, outline, saturation or lighting.',
  'BACKGROUND: perfectly flat solid magenta #FF00FF (preferred; transparent PNG also accepted), no gradient, floor, cast shadow or scenery.',
  'NO text, labels, numbers, frames, grid lines, watermark, and NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles).',
].join(' ');
// 게임 색 하나(outfit)가 여러 옷에 나뉘는 대장: 옷마다 이름을 붙인다 (바렌: 상의는 남색, #3a1018 은 반망토만).
const COLOR_ROLES = {
  blademaster: 'skin #e0ac7e, hair #2b1d14, tunic dark navy #2a3150 (main garment), dark-crimson half cape / hip wrap #3a1018 (the game outfit colour), headband off-white #e8e4d8',
};
const colorsOf = (look, cls) => ({ skin: look.skin, hair: look.hair, outfit: cls.outfit, accent: cls.accent });
const selPick = (key) => {
  const s = SEL[`captain_${key}`];
  if (key === 'lancer') return { ...s, ...s.variants.find((v) => v.job === '04b_lancer_noble') };
  return { ...s, ...s.picks[0] };
};
D.STARTER_CAPTAINS.forEach((key, i) => {
  const C = D.CAPTAINS[key], CC = D.CAPTAIN_CLASSES[key];
  const sel = selPick(key);
  const anchor = key === 'blademaster';
  phase3.push(sheetItem({
    id: `sheet/captain/${key}`, file: `sheet_captain_${key}.png`, priority: 1, group: '창설 후보 대장',
    name: `${C.name} — ${C.title} (${CC.name})`, ref: `art/inbox/captain_${key}.png`,
    order: anchor ? 1 : i + 1, heads: 4, ...(anchor ? { style_anchor_role: 'draw first, wait for owner approval' } : { style_anchor: ANCHOR_REF }),
    package: PKG(key), readme: `${PKG(key)}/README.md`, concept: `${PKG(key)}/concept.png`,
    concept_source: `art/concepts/captain_${key}/${sel.file}`,
    guides: GUIDES.map((g) => `${PKG(key)}/${g}`), guide_strip: `${PKG(key)}/guide_strip.png`,
    colors: colorsOf(C.look, CC), ...(COLOR_ROLES[key] ? { color_roles: COLOR_ROLES[key] } : {}),
    prompt: `Battle sprite of ${C.name} (${key}), a mercenary captain. Class: ${CC.name} (${CC.style}). `
      + `Design (what to keep and what to fix), weapon and per-pose notes: ${PKG(key)}/README.md; concept draft ${PKG(key)}/concept.png (design only), `
      + `portrait ${PKG(key)}/portrait.png (face only). Game colors: ${COLOR_ROLES[key] || lookText(C.look, CC)}. `
      + (anchor ? 'This image is the STYLE ANCHOR for every other character: draw it first, then stop for approval. '
        : `Match the approved style anchor ${ANCHOR_REF} (proportions, rendering, outline, palette, lighting, scale). `)
      + GUIDED_TAIL,
    nai: { prompt: sel.prompt, negative: sel.negative, seed: sel.seed, size: sel.size, source: `art/concepts/selections.json (#${sel.n})` },
  }));
});
// 1+) 로드릭 기마 (추가 선택, 게임은 아직 쓰지 않는다): 넓은 칸, 2x2 격자, 9명 다음 맨 마지막
{
  const C = D.CAPTAINS.lancer, CC = D.CAPTAIN_CLASSES.lancer;
  const m = SEL.captain_lancer.variants.find((v) => v.job === '04a_lancer_mounted');
  phase3.push(sheetItem({
    id: 'sheet/captain/lancer_mounted', file: 'sheet_captain_lancer_mounted.png', priority: 1, group: '창설 후보 대장',
    name: `${C.name} — 기마 (추가 선택, 게임 미사용)`, ref: 'art/inbox/captain_lancer.png',
    order: 10, heads: 4, optional: true, unused: true, layout: '2x2', cell: 160, height: 96, style_anchor: ANCHOR_REF,
    package: PKG('lancer'), readme: `${PKG('lancer')}/README.md`, concept: `${PKG('lancer')}/concept_mounted.png`,
    concept_source: `art/concepts/captain_lancer/${m.file}`, guide_strip: `${PKG('lancer')}/guide_mounted_layout.png`,
    colors: colorsOf(C.look, CC),
    prompt: `OPTIONAL, LAST. Mounted variant of ${C.name} (lancer) for a possible later "regains a warhorse" form; the game does not use it yet. `
      + `Same knight, BLUE plate armour (not the draft's silver), colours and style as your art/inbox/sheet_captain_lancer.png and the style anchor ${ANCHOR_REF}; the same infantry lance with a blue pennant. `
      + `Design: ${PKG('lancer')}/concept_mounted.png (design only; its horse head looks doubled - draw one). The horse has EXACTLY ONE head. `
      + `FORMAT: one PNG 1536x1024 as a 2x2 grid of equal quadrants (top: idle, wind-up; bottom: strike, hit), layout and size per ${PKG('lancer')}/guide_mounted_layout.png and ${PKG('lancer')}/README.md. `
      + 'Rider 4 heads tall with a head of about 45 px, front three-quarter view facing right, flat #FF00FF background, no lines, floor, shadow, text or effects.',
    nai: { prompt: m.prompt, negative: m.negative, seed: m.seed, size: m.size, source: `art/concepts/selections.json (#${m.n})` },
  }));
}
// 2) 일반 병과 5종 — 이름 없는 용병·세력 병사 전부가 쓰는 기본 그림 (상급·최상급 직업도 이 시트로 대신한다).
//    아군·적군·세력마다 같은 시트를 쓰고 전투에서 제복·장식만 진영 색으로 바꿔 칠한다 (js/battle.js sheetRecolor):
//    열쇠 색과 정확히 같은 픽셀만, 대상 색 x (열쇠 밝기 / 같은 역할 열쇠 평균 밝기)로. 그래서 제복은 아래 열쇠 색으로만,
//    평평하게(디더링·그라데이션 없이) 칠하고, 열쇠 색은 다른 곳에 쓰지 않는다. sheets.py 가 가까운 색(거리 34 안)을
//    열쇠 색으로 되돌리고 register_sheet.py --tint-* 로 manifest 에 적는다. 꾸러미: art/requests/phase3/class_<key>/ (handoff.py).
// 열쇠 색 (art/requests/phase3_gpt.md 메시지 D 와 같아야 한다):
//   제복 = 차분한 청회색 4단(어둠 → 밝음), 장식 = 옅은 청록 3단. 서로 43 이상, 금속(중성 회색)·가죽·피부와는 더 멀다.
const CLASS_KEYS = {
  outfit: ['#263459', '#394b78', '#52679c', '#7489be'],
  accent: ['#3f7a6c', '#5ea590', '#96d1bb'],
};
const GPT_SCALE = 0.1654;   // 앵커 바렌과 같은 배율 (가이드 격자 머리 110px → 게임 약 18px)
const CLASS_PKG = (key) => `art/requests/phase3/class_${key}`;
// NovelAI 디자인 초안 (주인이 고를 후보; 실행은 주인이 원할 때만). 제복은 말로만 "무늬 없는 청회색 + 옅은 청록 테두리".
// NovelAI 는 디자인 초안 전용이다: 게임에 들어가는 그림은 언제나 GPT 를 거친다 (novelai.py 는 art/concepts/<id>/drafts/ 에만 쓰고,
// sheets.py 는 NovelAI 그림을 등록하지 않는다).
const NAI_USE = 'design draft only (never game art: the final sheet is drawn by GPT; novelai.py writes art/concepts/<id>/drafts/, sheets.py refuses NovelAI images)';
const NAI_STYLE = 'three-quarter view, facing right, muted colors, desaturated, dark fantasy, game sprite, pixel art, simple background, flat magenta background, no shadow';
const NAI_NEG_BASE = 'lowres, bad anatomy, bad hands, text, watermark, signature, multiple views, cropped, blurry, background scenery, ground shadow, extra arms';
const NAI_ONE_HEAD = ', two heads, multiple heads, conjoined, extra head';
// 얼굴 가림 (주인 요청): 일반 병과 그림 한 장을 서로 다른 여러 사람이 같이 쓰므로, 직업에 어울리게 얼굴을 가리거나 그늘지게 한다
// (전사 면갑, 궁수 후드 + 천 마스크, 마법사 눌러쓴 모자 챙 + 높은 깃, 성직자 두건 + 베일, 도적 깊은 후드). 상급 직업은 어울릴 때만.
const NAI_FACE_HIDDEN_NEG = ', visible face details, detailed face, smile';
const CLASS_DRAFT = {
  warrior: { seed: 21001, tags: '1boy, solo, full body, four heads tall, young mercenary soldier, face hidden, closed great helm, visor down, eye slit, chainmail, plain slate blue tabard, pale teal trim, leather belt, brown gloves, dark trousers, brown boots, holding sword, round wooden shield, wide stance, bent knees, fighting stance' },
  archer: { seed: 22001, tags: '1girl, solo, full body, four heads tall, young mercenary archer, face hidden, hood up, slate blue cloth mask covering lower face, shadowed eyes, plain slate blue hooded tunic, brown leather vest, leather bracers, quiver on back, dark trousers, brown boots, holding bow, short bow, wide stance, bent knees, ready stance' },
  cleric: { seed: 23001, tags: '1girl, solo, full body, four heads tall, young war priest, face shadowed, deep cowl, veil, plain slate blue tabard over chainmail, pale teal trim, round sun disc emblem, leather belt, small book on belt, dark trousers, brown boots, holding mace, open hand raised, wide stance, bent knees' },
  mage: { seed: 24001, tags: '1boy, solo, full body, four heads tall, young battle mage, face hidden in shadow, wide-brimmed pointed hat pulled low, high collar covering mouth, plain slate blue robe, pale teal trim, pale teal sash, belt pouches, brown boots, holding wooden staff, small amber crystal, open hand raised, wide stance, bent knees' },
  rogue: { seed: 25001, tags: '1boy, solo, full body, four heads tall, young rogue, face hidden, deep hood, shadowed face, plain slate blue hood and short cape, pale teal scarf over mouth, dark brown leather armor, many straps, dark trousers, black boots, holding dagger, reverse grip, single dagger, crouching, wide stance, bent knees' },
};
// 주인이 고른 초안 (art/concepts/selections.json: picks[0]) → 꾸러미의 concept.png. 없으면 아직 고르지 않은 것 (pending).
const pickOf = (id) => {
  const s = SEL[id];
  return s && s.picks && s.picks.length ? { ...s, ...s.picks[0] } : null;
};
Object.entries(D.CLASSES).forEach(([key, K], i) => {
  const dr = CLASS_DRAFT[key];
  if (!dr) throw new Error(`no CLASS_DRAFT for class ${key}`);
  const pick = pickOf(`class_${key}`);
  phase3.push(sheetItem({
    id: `sheet/class/${key}`, file: `sheet_class_${key}.png`, priority: 2, group: '일반 병과', order: i + 1, heads: 4,
    after: 'the 9 starter captains (priority 1)', style_anchor: ANCHOR_REF,
    name: `일반 병과 — ${K.name}`, cell: 96, scale: GPT_SCALE, tint: CLASS_KEYS,
    package: CLASS_PKG(key), readme: `${CLASS_PKG(key)}/README.md`,
    concept: pick ? `${CLASS_PKG(key)}/concept.png` : `${CLASS_PKG(key)}/concept.png (pending: the owner picks a NovelAI draft first)`,
    ...(pick ? { concept_source: `art/concepts/class_${key}/${pick.file}` } : {}),
    guides: GUIDES.map((g) => `${CLASS_PKG(key)}/${g}`), guide_strip: `${CLASS_PKG(key)}/guide_strip.png`,
    game_colors: { outfit: K.outfit, accent: K.accent, note: 'not painted: the engine recolours the key colours to these (own guild) or to the faction / company colours' },
    prompt: `Battle sprite of a generic ${K.name} (${key}) used by every nameless mercenary and faction soldier of this class. `
      + `Design, weapon, per-pose notes (incl. what to keep and fix from the draft) and the KEY COLOURS: ${CLASS_PKG(key)}/README.md. `
      + (pick ? `Concept draft ${CLASS_PKG(key)}/concept.png = design only; its slate-blue / teal uniform only marks where the key colours go. ` : '')
      + `The uniform (tabard / robe / hood / cape) is painted ONLY with the outfit keys ${CLASS_KEYS.outfit.join(' ')} and its trim ONLY with the accent keys ${CLASS_KEYS.accent.join(' ')}, flat, `
      + 'and those seven colours appear nowhere else (the game recolours them to each faction\'s colours). '
      + 'One sprite stands for many different people, so the face is covered or in shadow (helm visor / hood and mask / low hat brim and high collar / cowl and veil / deep hood, as the README says) in all four poses. '
      + `Match the approved style anchor ${ANCHOR_REF} (proportions, rendering, outline, palette, lighting, scale). ` + GUIDED_TAIL,
    nai: pick ? { prompt: pick.prompt, negative: pick.negative, seed: pick.seed, size: pick.size, use: NAI_USE, source: `art/concepts/selections.json (#${pick.n})` }
      : { prompt: `${dr.tags}, ${NAI_STYLE}`, negative: NAI_NEG_BASE + NAI_ONE_HEAD + NAI_FACE_HIDDEN_NEG, seed: dr.seed, size: [832, 1216],
        use: NAI_USE, source: 'design-draft job: scratchpad nai/picks/jobs_classes.json; seed = first sample, samples use seed + i*37' },
  }));
});
// 3) 특별 용병 7명
Object.entries(D.HEROES).forEach(([key, h]) => {
  const H = D.HERO_CLASSES[h.hcls];
  phase3.push(sheetItem({
    id: `sheet/hero/${key}`, file: `sheet_hero_${key}.png`, priority: 3, group: '특별 용병', heads: 4, after: 'the 9 starter captains (priority 1)', style_anchor: ANCHOR_REF,
    name: `${h.name} — ${h.title} (${H.name})`, ref: `art/inbox/hero_${key}.png`,
    prompt: `Battle sprite of ${h.name}: ${HERO_FIGURE[key]}. Class: ${H.name} (${H.style}). Colors: ${lookText(h.look, H)}. Weapon: ${H.weapon}. Keep the face, hair and outfit of the reference portrait. ${ANCHOR_NOTE} ${SHEET_TAIL}`,
    nai: nai(naiFromFigure(HERO_FIGURE[key], h.look, H)),
  }));
});
// 4) 자주 나오는 몬스터 (지역 적). [게임 이름, 파일 키, 모습, 몸 높이 px, 칸(큰 몬스터)]
const MONSTERS = [
  ['고블린', 'goblin', 'small green goblin raider with big ears, crude leather armor, rusty short sword', 44],
  ['산적', 'bandit', 'human bandit, red bandana, patched leather jerkin, short axe', 60],
  ['사막 도적', 'desert-bandit', 'desert raider, sand-colored head wrap and veil, curved scimitar', 60],
  ['해골 병사', 'skeleton', 'skeleton soldier, cracked bones, rusty helmet and round shield, notched sword, glowing red eye sockets', 60],
  ['들늑대', 'wolf', 'grey wild wolf, four legs, snarling, walking to the right', 40],
  ['거대 거미', 'giant-spider', 'giant dark purple spider, eight legs, red eyes', 40],
  ['오크', 'orc', 'muscular green orc warrior, iron pauldron, big cleaver', 66],
  ['늪 슬라임', 'slime', 'green translucent slime blob with a simple face', 30],
  ['망령', 'wraith', 'pale blue floating ghost in tattered robes, glowing cyan eyes, no legs', 56],
  ['리자드맨', 'lizardman', 'teal-green lizardman warrior, scaly tail, spear and hide shield', 62],
  ['하피', 'harpy', 'harpy, woman with feathered purple wings for arms and bird talons', 56],
  ['가고일', 'gargoyle', 'grey stone gargoyle with bat wings and horns, crouching', 56],
  ['미믹', 'mimic', 'mimic treasure chest monster with teeth and a long tongue, gold trim', 40],
  ['마족 전사', 'demon-warrior', 'red-skinned demon warrior with horns, black armor, flaming eyes, jagged sword', 68],
  ['지옥견', 'hellhound', 'black-red hellhound, four legs, burning orange eyes and a mane of fire', 44],
  ['데스 나이트', 'death-knight', 'undead death knight in dark iron plate, purple tattered cape, teal ghost flames in the visor', 70],
  ['숲 트롤', 'forest-troll', 'huge mossy green forest troll, long arms, tree-branch club', 92, 112],
  ['서리 트롤', 'frost-troll', 'huge pale blue frost troll with icicles, ice club', 92, 112],
  ['설인', 'yeti', 'huge white-furred yeti, blue face, big fists', 92, 112],
  ['전갈 거인', 'giant-scorpion', 'giant golden desert scorpion, raised stinger tail, big pincers', 72, 112],
  ['와이번', 'wyvern', 'red wyvern dragon, two legs, wings half spread, long tail', 84, 112],
  ['리치의 망령', 'lich-wraith', 'large purple lich ghost in a crown and robes, green soul fire in its hands', 88, 112],
];
// 4-1) 1차 몬스터 8종: 전투에 가장 자주 나오는 보통 몬스터 (보스·재앙 수장 제외). 근거: tools/sim/bot.js 12판 x 365일의
//      의뢰 보고서 8315건을 Battle.plan 으로 펼쳐 센 몬스터 수 (art/requests/phase3_gpt.md 메시지 E). 상위 7종 + 늪지를 덮는 망령
//      (8위 고블린 3746 < 해골 병사 … 거대 거미 5343, 망령은 전체 2646이지만 첫 90일에는 699 > 고블린 504). 고블린은 다음 묶음 맨 앞.
//      사람형(해골 병사·사막 도적·산적)은 대장과 같은 posekit 가이드 띠, 나머지는 크기 상자 가이드(handoff.py). 모두 대장과 같은 배율.
//      [이름, 순서, 배치, 칸, NovelAI 초안 시드, 초안 크기, 초안 태그(사람형이면 four heads tall), 머리 둘 금지(한 머리 생물), 덧붙일 부정어]
const MONSTER_BATCH1 = [
  ['해골 병사', 1, '1x4', 96, 31001, [832, 1216], 'no humans, solo, full body, four heads tall, skeleton soldier, undead, chunky bones, cracked skull, red glowing eye sockets, rusty open-faced helmet, tattered dark cloth scraps, notched sword, round wooden shield, iron rim, wide stance, bent knees, fighting stance'],
  ['들늑대', 2, '2x2', 112, 32001, [1216, 832], 'no humans, solo, full body, animal focus, wolf, grey wolf, wild wolf, shaggy grey fur, amber eyes, snarling, bared fangs, four legs, tail, standing, head lowered', ', extra legs'],
  ['사막 도적', 3, '1x4', 96, 33001, [832, 1216], '1boy, solo, full body, four heads tall, desert bandit, raider, tan skin, sand-colored head wrap, face veil, only eyes visible, loose sand-colored robes, brown leather vest, sash, baggy trousers, leather boots, holding scimitar, curved sword, one-handed, wide stance, bent knees, fighting stance'],
  ['하피', 4, '2x2', 112, 34001, [1216, 832], '1girl, solo, full body, four heads tall, monster girl, harpy, winged arms, purple feathered wings, bird legs, talons, feathered tail, wild auburn hair, red eyes, hovering, wings spread'],
  ['산적', 5, '1x4', 96, 35001, [832, 1216], '1boy, solo, full body, four heads tall, bandit, stubble, sneer, red bandana, patched leather jerkin, rope belt, dark trousers, worn boots, holding axe, hand axe, small round wooden buckler, wide stance, bent knees, fighting stance'],
  ['가고일', 6, '2x2', 112, 36001, [1216, 832], 'no humans, solo, full body, monster, gargoyle, grey stone skin, cracked stone, bat wings, curved horns, red eyes, claws, tail, crouching, hunched, wings half spread'],
  ['거대 거미', 7, '2x2', 112, 37001, [1216, 832], 'no humans, solo, full body, monster, giant spider, eight legs, dark purple carapace, hairy legs, red eyes, fangs, crouching, front legs raised'],
  ['망령', 8, '1x4', 96, 38001, [832, 1216], 'no humans, solo, full body, monster, wraith, ghost, floating, pale blue tattered robes, hood, skeletal hands, claws, glowing cyan eyes, no legs, wispy tail'],
];
// 자세별 배율 보정 (sheets.py pose_scale): GPT 가 2x2 격자의 큰 자세 상자(공격 준비 520x420·타격 560x340 대 대기 380x330)를 채우려고
// 날개·팔다리만이 아니라 머리·몸까지 키워 그린 자세. 같은 그림의 고정된 부분(꼬리 끝 삽 모양, 머리·뿔)으로 잰 대기와의 크기 비의 역수.
const MON_POSE_SCALE = {
  '가고일': { windup: 0.9, strike: 0.88 },   // 꼬리 끝 1.05·1.14배, 머리·뿔 1.15~1.3배 (첫 납품 art/inbox/sheet_monster_gargoyle.png)
};
// 점 색 (sheets.py spots): 눈처럼 원본에서 몇 px 뿐이라 0.1654 축소·팔레트에서 사라지는 색 — 축소 뒤에도 그 색 그대로 남긴다.
const MON_SPOTS = {
  '해골 병사': ['#ff4a3a'],              // 빨간 눈 (PC 손질 ea6fe20)
  '들늑대': ['#f2c94c', '#b8862a'],      // 호박색 눈 (PC 손질 66aca5a)
  '가고일': ['#d6455d'],                 // 빨간 눈 (PC 손질 cea8630)
  '거대 거미': ['#d6455d'],              // 빨간 눈 무리 (다시 그리기 2: 대기 컷에서 눈이 0px 이었다)
};
const MON_HUMANOID = new Set(['해골 병사', '사막 도적', '산적']);   // 사람 골격: 대장과 같은 posekit 가이드 띠
const MON_KEY = Object.fromEntries(MONSTERS.map(([enemy, key]) => [enemy, key]));
const MON_PKG = (key) => `art/requests/phase3/monster_${key}`;
MONSTER_BATCH1.forEach(([enemy, order, layout, cell, seed, size, tags, negExtra]) => {
  const key = MON_KEY[enemy];
  const E = D.ENEMIES[enemy];
  if (!key || !E || E.boss) throw new Error(`MONSTER_BATCH1: ${enemy} is not a non-boss enemy in MONSTERS`);
  const human = MON_HUMANOID.has(enemy);
  const pick = pickOf(`monster_${key}`);
  phase3.push(sheetItem({
    id: `sheet/monster/${enemy}`, file: `sheet_monster_${key}.png`, priority: 4, group: '지역 몬스터 1차', order, after: 'the 9 starter captains (priority 1)', style_anchor: ANCHOR_REF,
    name: `몬스터 — ${enemy}`, layout, cell, scale: GPT_SCALE, ...(MON_POSE_SCALE[enemy] ? { pose_scale: MON_POSE_SCALE[enemy] } : {}), ...(MON_SPOTS[enemy] ? { spots: MON_SPOTS[enemy] } : {}), humanoid: human,
    package: MON_PKG(key), readme: `${MON_PKG(key)}/README.md`,
    concept: pick ? `${MON_PKG(key)}/concept.png` : `${MON_PKG(key)}/concept.png (pending: the owner picks a NovelAI draft first)`,
    ...(pick ? { concept_source: `art/concepts/monster_${key}/${pick.file}` } : {}),
    ...(human ? { guides: GUIDES.map((g) => `${MON_PKG(key)}/${g}`), guide_strip: `${MON_PKG(key)}/guide_strip.png` }
      : { guide_layout: `${MON_PKG(key)}/guide_layout.png`, guide_scale: `${MON_PKG(key)}/guide_scale.png` }),
    colors: E.pal,
    prompt: `Battle sprite of a monster (${enemy}). Design brief, size relative to the 4-head humans, the four poses, the layout and what to keep and fix from the draft: ${MON_PKG(key)}/README.md. `
      + (pick ? `Concept draft ${MON_PKG(key)}/concept.png = design only. ` : '')
      + `${layout === '2x2' ? 'FORMAT: one PNG 1536x1024 as a 2x2 grid of equal 768x512 quadrants (top: idle, wind-up; bottom: strike, hit), lowest pixel of each pose on y=461 of its quadrant, per guide_layout.png. ' : ''}`
      + `Same pixel scale as the humans (head 110 px), so it can stand next to them. Match the approved style anchor ${ANCHOR_REF}. `
      + (layout === '2x2' ? 'Front three-quarter view facing RIGHT, flat #FF00FF background, no lines, labels, floor, shadow, text or effects.' : GUIDED_TAIL),
    nai: pick ? { prompt: pick.prompt, negative: pick.negative, seed: pick.seed, size: pick.size, use: NAI_USE, source: `art/concepts/selections.json (#${pick.n})` }
      : { prompt: `${tags}, ${NAI_STYLE}`, negative: NAI_NEG_BASE + NAI_ONE_HEAD + (negExtra || ''), seed, size,
        use: NAI_USE, source: 'design-draft job: scratchpad nai/picks/jobs_monsters.json; seed = first sample, samples use seed + i*37' },
  }));
});
// 4-2) 나머지 보통 몬스터 (다음 묶음; 보스·재앙 수장은 그 뒤)
const BATCH1 = new Set(MONSTER_BATCH1.map((m) => m[0]));
MONSTERS.forEach(([enemy, key, look, height, cell]) => {
  if (!D.ENEMIES[enemy]) throw new Error(`unknown enemy ${enemy}`);
  if (BATCH1.has(enemy)) return;
  const pal = D.ENEMIES[enemy].pal;
  phase3.push(sheetItem({
    id: `sheet/monster/${enemy}`, file: `sheet_monster_${key}.png`, priority: 4, group: '지역 몬스터 (다음 묶음)', after: 'the 9 starter captains (priority 1)', style_anchor: ANCHOR_REF,
    name: `몬스터 — ${enemy}`, height, ...(cell ? { cell } : {}),
    prompt: `Battle sprite of a monster: ${look}. Main color ${pal.M}, dark ${pal.D}${pal.A ? `, accent ${pal.A}` : ''}, eyes ${pal.E}.${cell ? ' A large monster: draw it bigger and heavier than a human (it is shown about 1.5x human height).' : ''} ${ANCHOR_NOTE} ${SHEET_TAIL}`,
    nai: nai(`no humans, solo, monster, ${look}`, NAI_MONSTER_TAIL),
  }));
});
// 5) 나머지 대장 (나중 묶음)
Object.entries(D.CAPTAINS).forEach(([key, C]) => {
  if (D.STARTER_CAPTAINS.includes(key)) return;
  const CC = D.CAPTAIN_CLASSES[key];
  phase3.push(sheetItem({
    id: `sheet/captain/${key}`, file: `sheet_captain_${key}.png`, priority: 5, group: '나머지 대장', heads: 4, after: 'the 9 starter captains (priority 1)', style_anchor: ANCHOR_REF,
    name: `${C.name} — ${C.title} (${CC.name})`, ref: `art/inbox/captain_${key}.png`,
    prompt: `Battle sprite of ${C.name}, a mercenary captain: ${FIGURE[key]}. Class: ${CC.name} (${CC.style}). Colors: ${lookText(C.look, CC)}. Weapon: ${CC.weapon}. Keep the face, hair and outfit of the reference portrait. ${ANCHOR_NOTE} ${SHEET_TAIL}`,
    nai: nai(naiFromFigure(FIGURE[key], C.look, CC)),
  }));
});

// 대장·특별 용병 시트의 배율·칸: 예전에는 등록할 때마다 손으로 `--scale 0.1654 --cell 96` 을 붙였고, 아멜리의 칸 112 는 manifest 에만 있었다.
// 여기 적어 두면 sheets.py · check_delivery.py · receive.py 가 플래그 없이 같은 결과를 낸다.
// 그림이 가이드보다 작게 그려진 시트의 변환 배율 (원본이 6배 크므로 다시 그리지 않고 변환에서 맞춘다; 몸 크기를 다른 대장과 같게).
//   pirateking: 대기 실루엣 363px(모자 포함) — 다른 대장 400~435px 보다 12~15% 작게 그려졌다 (art-inbox 9124b86)
const DRAWN_SMALL = { pirateking: 0.185, frostjarl: 0.18 };   // frostjarl: 대기 370px (b476149)
const CELL_112 = new Set(['lancer', 'pilgrim', 'titan', 'pirateking']);   // 든 무기·덩치가 96칸(자세 높이 90px)을 넘는 대장
phase3.forEach((it) => {
  const m = /^sheet\/(captain|hero)\/([a-z_]+)$/.exec(it.id);
  if (!m || m[2].endsWith('_mounted')) return;
  if (it.scale == null) it.scale = DRAWN_SMALL[m[2]] || GPT_SCALE;
  if (it.cell == null) it.cell = CELL_112.has(m[2]) ? 112 : 96;
});
fs.writeFileSync(path.join(ROOT, 'art/requests/phase3.json'), JSON.stringify({ version: 1, phase: 3, inbox: 'art/inbox/', items: phase3 }, null, 2) + '\n');
const md3 = [
  '# 그림 요청서 — 3단계 (전투 캐릭터 스프라이트 시트)',
  '',
  '> `node tools/art/requests.js`로 자동 생성된다. 규격은 `art/STYLE.md`의 **전투 캐릭터**, 절차는 `art/README.md`,',
  '> GPT 에 넘기는 규칙은 `art/requests/gpt_handoff_notes.md` (이 문서보다 우선).',
  '> 그림 쪽은 **핵심 자세 4개를 한 줄로** 크게 그리기만 한다. 칸 자르기·축소·팔레트·숨쉬기 루프·시트 조립·게임 등록은',
  '> 코드 쪽이 `python3 tools/art/sheets.py`로 한다. 걷기·돌진·피격 번쩍임·스킬 효과는 게임 엔진이 그린다.',
  '',
  `총 ${phase3.length}장 · 결과물은 \`art/inbox/<file>\`에 PNG로 넣는다.`,
  '',
  '## 진행 순서 (주인과 합의한 것)',
  '',
  '| 단계 | 누가 | 결과 |',
  '|---|---|---|',
  '| 디자인 초안 | NovelAI | `art/concepts/` (주인이 고른 것만, 디자인 참고용 — 게임 그림으로 쓰지 않는다) |',
  '| 자세 가이드 | 코드 (`tools/pixelart/posekit.py`) | 4등신 마네킹, 캐릭터마다 `guide_strip.png` |',
  '| 최종 그림 | **GPT** | 한 화풍으로 통일한 1536x1024 띠 한 장씩 |',
  '| 후처리 | `tools/art/sheets.py` | 80x80 칸 시트 + manifest |',
  '',
  '1. **바렌(`captain_blademaster`)을 먼저** 그리고 멈춘다 → 주인이 승인하면 그 그림이 **화풍 기준(앵커)** 이 된다.',
  '2. 나머지 창설 후보 8명을 앵커에 맞춰 그린다 (아래 순서). 로드릭 기마(추가 선택, 게임 미사용)는 맨 마지막.',
  '3. 그 다음: **일반 병과 5종**(메시지 D)과 **1차 몬스터 8종**(메시지 E). 주인이 NovelAI 디자인 초안을 골랐고(`art/concepts/selections.json`),',
  '   꾸러미(`class_<key>/`, `monster_<key>/`)에 `concept.png`와 초안별 가져올 것·고칠 것(README 의 FROM concept.png / FIX)이 들어 있다 — 보낼 준비 완료.',
  '   일반 병과는 **얼굴이 가려지는 복장** (한 그림을 서로 다른 여러 사람이 같이 쓴다; 전사 면갑, 궁수 후드 + 마스크, 마법사 모자 챙 + 높은 깃, 성직자 두건 + 베일, 도적 깊은 후드).',
  '4. 그 뒤 묶음(특별 용병·나머지 몬스터·보스·나머지 대장·상급/최상급 직업)은 아직 디자인 초안이 없어 초상화(ref)와 아래 프롬프트만 있다.',
  '',
  `- **일반 병과 열쇠 색**: 제복 ${CLASS_KEYS.outfit.map((c) => `\`${c}\``).join(' ')} / 장식 ${CLASS_KEYS.accent.map((c) => `\`${c}\``).join(' ')} —`,
  '  이 7색은 제복·장식에만 평평하게 쓰고 다른 곳에는 쓰지 않는다. 전투에서 진영 색으로 바꿔 칠한다 (`sheets.py`가 가까운 색을 되돌려 `--tint-*`로 등록).',
  '- 일반 병과·1차 몬스터는 요청서에 `scale`(0.1654, 대장과 같은 배율)·`cell`·`layout`이 있어 `sheets.py`가 그대로 쓴다.',
  '',
  '- **모두 4등신** (머리 = 선 키의 1/4). 예전의 "3등신 치비" 규칙은 폐기.',
  '- 창설 후보 9명은 캐릭터마다 꾸러미 `art/requests/phase3/captain_<key>/` (concept.png · portrait.png · guide_1..4 · guide_strip.png · README.md)를 쓴다.',
  '  꾸러미는 `python3 tools/art/handoff.py`로 다시 만든다.',
  '- 그림 쪽에 붙여 넣을 메시지: **`art/requests/phase3_gpt.md`** (메시지 A = 바렌만, B = 승인 후 나머지, C = 펠릭스 색 고치기, D = 일반 병과, E = 1차 몬스터).',
  '',
  '## NovelAI로 만들 때 (코드 쪽, 사용자가 원할 때만)',
  '',
  '**NovelAI 는 디자인 초안 전용이다 (주인 결정).** 게임에 들어가는 최종 그림은 언제나 GPT 를 거친다 — NovelAI 로 최종본을 요청하지 않는다.',
  '`novelai.py`는 `art/concepts/<id>/drafts/nai_*.png`(또는 `--outdir`로 준 작업 폴더)에만 쓰고 `art/inbox/`·`assets/`에는 쓰지 못한다.',
  '`sheets.py`는 NovelAI 그림(PNG 메타데이터 `Software: NovelAI`, `art/concepts/`·`drafts/` 경로, `nai_` 이름)을 거부한다 (`--allow-draft`는 미리보기 시험용, 등록 불가).',
  '창설 후보 9명·일반 병과 5종·1차 몬스터 8종의 NovelAI 프롬프트·시드·크기는 주인이 고른 초안 그대로다 (`art/concepts/selections.json`; `--only`가 `nai.seed`·`nai.size`를 쓴다). 나머지는 한 장에 한 자세(전투 대기 자세).',
  '무료 범위(넓이 <= 1024x1024, 28 steps, 1장)로, 한 번에 몇 장씩만:',
  '',
  '```',
  'python3 tools/art/novelai.py --only sheet/class/warrior   # → art/concepts/class_warrior/drafts/nai_class_warrior_s21149.png (고른 초안 다시 만들기, 초안만)',
  '```',
  '',
];
let cur3 = '';
phase3.forEach((it) => {
  const sec = `## ${it.priority}. ${it.group}${it.after ? ' (창설 후보 9명 다음)' : ''}`;
  if (sec !== cur3) { md3.push(sec, ''); cur3 = sec; }
  md3.push(`### ${it.order ? `${it.order}. ` : ''}${it.name}`,
    `- 파일: \`${it.file}\` · id: \`${it.id}\` · 생성: ${it.size} ${it.layout || '1x4'} ${it.layout === '2x2' ? '격자' : '띠'} · 게임: ${it.out}${it.ref ? ` · 참고: \`${it.ref}\`` : ''}`,
    ...(it.package ? [`- 꾸러미: \`${it.package}/\` (README · concept · ${it.guide_layout ? 'guide_layout · guide_scale' : 'guide_strip'})${it.style_anchor ? ` · 화풍 기준: \`${it.style_anchor}\`` : ' · **화풍 기준(앵커): 먼저 그리고 승인 대기**'}`] : []),
    ...(it.tint ? [`- 열쇠 색: 제복 ${it.tint.outfit.join(' ')} · 장식 ${it.tint.accent.join(' ')} (전투에서 진영 색으로 바꿔 칠함)`] : []),
    ...(it.scale ? [`- 후처리: \`python3 tools/art/sheets.py art/inbox/${it.file}\` (요청서의 scale ${it.scale} · cell ${it.cell}${it.layout === '2x2' ? ' · 2x2' : ''}를 그대로 쓴다)`] : []),
    '', '```', it.prompt, '```', '',
    '<details><summary>NovelAI 디자인 초안 (한 자세, 게임 그림 아님)</summary>', '', '```', it.nai.prompt, '', `Negative: ${it.nai.negative}`,
    ...(it.nai.seed ? ['', `Seed: ${it.nai.seed}${it.nai.size ? ` · size ${it.nai.size.join('x')}` : ''}`] : []), '```', '', '</details>', '');
});
fs.writeFileSync(path.join(ROOT, 'art/requests/phase3.md'), md3.join('\n'));
console.log(`phase3 requests: ${phase3.length} items`);
