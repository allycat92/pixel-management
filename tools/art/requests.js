// 그림 요청서 생성기: 게임 데이터(외형·직업·사연)에서 그림 요청서를 만든다.
// 실행: node tools/art/requests.js  → art/requests/phase1.json, art/requests/phase1.md
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
const D = vm.runInContext('({ CAPTAINS, CAPTAIN_CLASSES, HEROES, HERO_CLASSES, FACTIONS, CLASSES })', ctx);

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
  seraphine: 'young woman, pale, brown hair, torn white saint robes with a red sash, sorrowful but kind',
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
