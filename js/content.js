// 확장 콘텐츠: 지역, 몬스터, 장비, 특별 용병(이야기)
'use strict';

// ───────── 지역 ─────────
// unlock: 필요한 랭크 인덱스, levels: 의뢰 난이도 범위, travel: 추가 이동일
const REGIONS = {
  plains: {
    name: '왕도 평원', unlock: 0, levels: [1, 3], travel: 0, outpostCost: 0,
    pos: [150, 118], color: '#6fa84a',
    desc: '용병단 본거지가 있는 평화로운 평원. 초보 용병의 일거리가 많다.',
    enemies: ['고블린', '들늑대', '산적'],
    places: ['왕도 외곽', '밀밭 마을', '오래된 풍차', '국경 검문소'],
  },
  forest: {
    name: '은빛 숲', unlock: 1, levels: [2, 5], travel: 0, outpostCost: 250,
    pos: [78, 76], color: '#3f7a3a',
    desc: '엘프의 옛 영토. 최근 숲이 병들어 괴물이 늘고 있다.',
    enemies: ['들늑대', '거대 거미', '숲 트롤'],
    places: ['은빛 숲 마을', '고대 숲', '엘프 유적', '거미 골짜기'],
  },
  swamp: {
    name: '안개 늪지', unlock: 2, levels: [3, 6], travel: 1, outpostCost: 400,
    pos: [62, 140], color: '#4f6b4a',
    desc: '짙은 안개에 덮인 늪. 망령과 저주의 소문이 끊이지 않는다.',
    enemies: ['늪 슬라임', '거대 거미', '망령', '리자드맨'],
    places: ['안개 늪지', '마녀의 오두막', '가라앉은 수도원', '마탑 폐허'],
  },
  desert: {
    name: '사막 교역로', unlock: 3, levels: [4, 8], travel: 1, outpostCost: 600,
    pos: [246, 138], color: '#c9a45a',
    desc: '금과 향신료가 오가는 교역로. 그만큼 도적과 괴물도 많다.',
    enemies: ['사막 도적', '전갈 거인', '오크'],
    places: ['사막 교역소', '오아시스 도시', '피의 투기장', '모래 묻힌 신전'],
  },
  frost: {
    name: '서리 협곡', unlock: 4, levels: [5, 9], travel: 1, outpostCost: 850,
    pos: [138, 36], color: '#b8d4e8',
    desc: '만년설로 뒤덮인 협곡. 북부 요새가 마지막 방어선이다.',
    enemies: ['서리 트롤', '설인', '해골 병사', '하피'],
    places: ['북부 요새', '서리 협곡', '얼어붙은 지하묘지', '빙하 동굴'],
  },
  dragon: {
    name: '용의 등뼈 산맥', unlock: 5, levels: [7, 10], travel: 2, outpostCost: 1200,
    pos: [254, 52], color: '#7a3a3a',
    desc: '용이 잠든다는 화산 산맥. 대륙 최강의 용병만이 발을 들인다.',
    enemies: ['와이번', '리치의 망령', '오크', '가고일'],
    places: ['용의 등뼈 산맥', '용암 동굴', '고대 용의 둥지', '불타는 성채'],
  },
};
const REGION_LINKS = [['plains', 'forest'], ['plains', 'swamp'], ['forest', 'swamp'], ['plains', 'desert'],
  ['forest', 'frost'], ['frost', 'dragon'], ['desert', 'dragon']];

// 마법 조사 의뢰에 나오는 적 (난이도 순)
const MAGIC_ENEMIES = ['늪 슬라임', '망령', '해골 병사', '리치의 망령'];

// ───────── 몬스터 ─────────
// tpl: 스프라이트 틀, pal: 색, big: 거대 몬스터(크게 그려짐)
const ENEMIES = {
  '고블린':     { tpl: 'imp', pal: { M: '#6fa84a', D: '#4a7a30', A: '#7a5236', E: '#f2c94c' } },
  '산적':       { tpl: 'imp', pal: { M: '#e0ac7e', D: '#a8764e', A: '#8f2d3a', E: '#1b1420' } },
  '사막 도적':  { tpl: 'imp', pal: { M: '#c68a5c', D: '#8d5a3b', A: '#e8d5a3', E: '#1b1420' } },
  '해골 병사':  { tpl: 'imp', pal: { M: '#e8e4d8', D: '#a8a49a', A: '#5c606a', E: '#d6455d' } },
  '들늑대':     { tpl: 'beast', pal: { M: '#8a8f99', D: '#5c606a', E: '#f2c94c' } },
  '거대 거미':  { tpl: 'bug', pal: { M: '#3b3346', D: '#241b29', L: '#5a4a66', E: '#d6455d' } },
  '전갈 거인':  { tpl: 'bug', pal: { M: '#c58f1e', D: '#8a6210', L: '#f2c94c', E: '#1b1420' }, big: true },
  '숲 트롤':    { tpl: 'brute', pal: { M: '#5a7a5a', D: '#3e5a3e', L: '#7a9a6a', A: '#6b4226', E: '#f2c94c' }, big: true },
  '오크':       { tpl: 'brute', pal: { M: '#5f8a3a', D: '#456a28', L: '#7aa84a', A: '#5c606a', E: '#d6455d' } },
  '서리 트롤':  { tpl: 'brute', pal: { M: '#9fc4dc', D: '#6f94ac', L: '#d0e8f4', A: '#3a4a6b', E: '#3d4a9c' }, big: true },
  '설인':       { tpl: 'brute', pal: { M: '#e8eef2', D: '#b0bcc8', L: '#ffffff', A: '#8a9aa8', E: '#3d4a9c' }, big: true },
  '늪 슬라임':  { tpl: 'slime', pal: { M: '#6fbf6f', D: '#3f8a3f', L: '#b8f0b8', E: '#1b1420' } },
  '망령':       { tpl: 'ghost', pal: { M: '#b8c8e8', D: '#7a8ab0', L: '#e8f0ff', E: '#6ff0f0' } },
  '리치의 망령': { tpl: 'ghost', pal: { M: '#9b6ad6', D: '#6b3d9c', L: '#d0b0f0', E: '#7ed37e' }, big: true },
  '와이번':     { tpl: 'drake', pal: { M: '#9c3b2e', D: '#6b2418', L: '#e8a14f', A: '#c25a3a', E: '#f2c94c' }, big: true },
  '리자드맨':   { tpl: 'imp', pal: { M: '#4f9a7a', D: '#2f6a50', A: '#8a6a3a', E: '#f2c94c' } },
  '하피':       { tpl: 'drake', pal: { M: '#e0ac7e', D: '#a8764e', L: '#f5d6b8', A: '#8a6aa8', E: '#d6455d' } },
  '가고일':     { tpl: 'drake', pal: { M: '#6b737c', D: '#44494f', L: '#9aa3ad', A: '#5c606a', E: '#d6455d' } },
  '미믹':       { tpl: 'chest', pal: { M: '#8a5a2b', D: '#5a3a1a', A: '#d9a441', E: '#f2c94c' } },
  // ── 지역 보스 ──
  '고블린 왕':   { tpl: 'imp', pal: { M: '#5a9a3a', D: '#3a6a20', A: '#d9a441', E: '#d6455d' }, big: true, boss: true },
  '거미 여왕':   { tpl: 'bug', pal: { M: '#5a2a6a', D: '#3a1a4a', L: '#9b6ad6', E: '#f2c94c' }, big: true, boss: true },
  '늪의 마녀':   { tpl: 'ghost', pal: { M: '#5a8a4a', D: '#3a5a2a', L: '#a7d26a', E: '#f2c94c' }, big: true, boss: true },
  '모래 폭군':   { tpl: 'bug', pal: { M: '#b0402a', D: '#7a2418', L: '#e8a14f', E: '#f2c94c' }, big: true, boss: true },
  '서리 거인 왕': { tpl: 'brute', pal: { M: '#7fb4dc', D: '#4f84ac', L: '#e8f4ff', A: '#d9a441', E: '#ffffff' }, big: true, boss: true },
  '고룡 이그니스': { tpl: 'drake', pal: { M: '#2a2a3a', D: '#14141e', L: '#d6455d', A: '#7a2430', E: '#f39c12' }, big: true, boss: true },
};

// ───────── 지역 보스 ─────────
// 지역 의뢰를 clears번 성공하면 보스 의뢰가 게시된다. 처치하면 그 지역 의뢰 보상 +10%.
const BOSSES = {
  plains: {
    enemy: '고블린 왕', name: '고블린 왕 그릭스', type: 'hunt', title: '고블린 왕의 요새 습격', clears: 4,
    intro: '평원의 고블린들이 「왕」을 자처하는 거대한 고블린 아래 모여들고 있습니다. 녀석을 쓰러뜨리면 평원에 평화가 찾아올 것입니다.',
    outro: '고블린 왕이 쓰러지자 무리는 뿔뿔이 흩어졌습니다. 왕도 사람들이 은빛 늑대의 이름을 연호합니다.',
    reward: { base: 'mace', name: '그릭스의 황금 왕홀', bonus: { str: 8, int: 8 } },
  },
  forest: {
    enemy: '거미 여왕', name: '거미 여왕 아라크네아', type: 'hunt', title: '거미 여왕의 둥지', clears: 5,
    intro: '은빛 숲 깊은 곳, 수백 년을 산 거미 여왕이 깨어났습니다. 숲의 모든 거미가 그녀의 명령을 따릅니다.',
    outro: '여왕의 둥지가 무너졌습니다. 숲에 다시 새소리가 들립니다.',
    reward: { base: 'leather', name: '여왕의 비단 갑옷', bonus: { hp: 20, dex: 10 } },
  },
  swamp: {
    enemy: '늪의 마녀', name: '늪의 마녀 모르가나', type: 'magic', title: '늪의 마녀를 봉인하라', clears: 5,
    intro: '안개 늪지의 저주는 모두 한 마녀의 원한에서 비롯되었습니다. 죽어서도 늪을 떠나지 못한 마녀를 봉인해야 합니다.',
    outro: '마녀의 원한이 풀리며 늪의 안개가 옅어졌습니다.',
    reward: { base: 'robe', name: '마녀의 안개 로브', bonus: { hp: 12, int: 14 } },
  },
  desert: {
    enemy: '모래 폭군', name: '모래 폭군 사르칸', type: 'defense', title: '모래 폭군의 진격을 막아라', clears: 6,
    intro: '교역로를 집어삼키는 거대한 전갈 「모래 폭군」이 오아시스 도시로 향하고 있습니다. 도시를 지켜야 합니다.',
    outro: '폭군의 껍질이 모래 위에 쓰러졌습니다. 교역로가 다시 활기를 되찾습니다.',
    reward: { base: 'plate', name: '폭군의 갑각 갑옷', bonus: { hp: 32, str: 8 } },
  },
  frost: {
    enemy: '서리 거인 왕', name: '서리 거인 왕 위르겔', type: 'defense', title: '북부 요새 최후의 방어전', clears: 6,
    intro: '서리 거인 왕이 거인 군단을 이끌고 북부 요새로 내려옵니다. 요새가 무너지면 왕국 북부 전체가 위험합니다.',
    outro: '거인 왕이 무릎을 꿇었습니다. 북부 요새의 종이 승리를 알립니다.',
    reward: { base: 'ring', name: '서리 왕관 반지', bonus: { str: 10, dex: 10, int: 10 } },
  },
  dragon: {
    enemy: '고룡 이그니스', name: '고룡 이그니스', type: 'hunt', title: '용의 등뼈, 고룡 토벌', clears: 7,
    intro: '천 년의 잠에서 깨어난 고룡 이그니스. 대륙 최강의 용병단만이 이 전설에 도전할 수 있습니다.',
    outro: '고룡이 쓰러졌습니다. 은빛 늑대 용병단의 이름은 이제 전설이 되었습니다.',
    reward: { base: 'sword', name: '용살검 이그니스', bonus: { str: 18, dex: 8, hp: 15 } },
  },
};

// ───────── 장비 ─────────
const STAT_NAMES = { str: '힘', dex: '민첩', int: '지력', hp: '체력' };
const SLOT_NAMES = { weapon: '무기', armor: '방어구', trinket: '장신구' };
const TIERS = [
  null,
  { name: '낡은', mul: 1, price: 60, color: '#9a8a7a' },
  { name: '강철', mul: 2, price: 170, color: '#d6dde4' },
  { name: '미스릴', mul: 3.2, price: 400, color: '#7fd6e8' },
  { name: '룬', mul: 4.6, price: 820, color: '#b48ae8' },
  { name: '전설의', mul: 6.5, price: 1600, color: '#f2c94c' },
];
const ITEM_BASES = {
  sword:   { slot: 'weapon', name: '장검', bonus: { str: 3, dex: 1 } },
  bow:     { slot: 'weapon', name: '장궁', bonus: { dex: 3, str: 1 } },
  staff:   { slot: 'weapon', name: '지팡이', bonus: { int: 3.5 } },
  dagger:  { slot: 'weapon', name: '단검', bonus: { dex: 2, str: 1.5 } },
  mace:    { slot: 'weapon', name: '철퇴', bonus: { str: 2, int: 1.5 } },
  plate:   { slot: 'armor', name: '판금 갑옷', bonus: { hp: 8, str: 1 } },
  leather: { slot: 'armor', name: '가죽 갑옷', bonus: { hp: 5, dex: 1 } },
  robe:    { slot: 'armor', name: '로브', bonus: { hp: 3, int: 1.5 } },
  ring:    { slot: 'trinket', name: '반지', bonus: { any: 2.5 } },
  amulet:  { slot: 'trinket', name: '부적', bonus: { hp: 4, any: 1 } },
};
// 직업별로 잘 맞는 무기 (상점 추천 표시용)
const CLASS_WEAPON = { warrior: 'sword', archer: 'bow', mage: 'staff', cleric: 'mace', rogue: 'dagger' };
const HERB_PRICE = 35;

// ───────── 특별 용병 ─────────
// 랭크 조건을 만족하면 주점에 나타나고, 인연(함께 성공한 의뢰 수)이 쌓이면 개인 의뢰가 열린다.
const HEROES = {
  kai: {
    name: '카이', cls: 'archer', title: '숲을 떠난 엘프 정찰병', unlock: 1, level: 3, trait: 'hawkeye',
    look: { skin: '#f5d6b8', hair: '#e3c565', longHair: true },
    intro: [
      [null, '뾰족한 귀의 궁수가 창가 자리에서 화살깃을 다듬고 있습니다.'],
      ['카이', '은빛 숲이 병들고 있어. 장로들은 인간의 도움을 거절했지.'],
      ['카이', '난 생각이 달라. 너희 용병단, 실력이 있다고 들었다.'],
    ],
    chapters: [
      {
        bond: 3, region: 'forest', type: 'hunt', enemy: '거대 거미', title: '병든 숲의 근원',
        before: [['카이', '숲 깊은 곳 거미 둥지에서 검은 독이 퍼지고 있어.'], ['카이', '장로들 몰래 가자. 내가 길을 안내하지.']],
        after: [['카이', '둥지를 태웠다. 숲이 다시 숨을 쉬는군.'], ['카이', '장로께서 이 활을 보내셨다. 인간에게 주는 건 처음이라더군.']],
        reward: { item: { base: 'bow', name: '은빛 숲의 장궁', bonus: { dex: 13, str: 4 } } },
      },
      {
        bond: 8, region: 'swamp', type: 'explore', enemy: '망령', title: '검은 독의 배후',
        before: [['카이', '독은 자연적인 게 아니었다. 늪지의 주술사가 퍼뜨린 거야.'], ['카이', '끝을 내자, 단장.']],
        after: [['카이', '주술사는 사라졌다. 숲과 늪 모두 평화를 되찾을 거다.'], ['카이', '장로들이 날 정식 숲의 수호자로 인정했다. 하지만 내 자리는 여기야.']],
        reward: { stats: { dex: 5, hp: 8 }, rep: 80, newTitle: '숲의 수호자' },
      },
      {
        bond: 14, region: 'dragon', type: 'hunt', enemy: '와이번', title: '세계수의 씨앗',
        before: [['카이', '장로들이 전설로만 전하던 세계수의 씨앗이 용의 산맥에 있다고 한다.'], ['카이', '와이번들이 그 씨앗을 둥지에 품고 있다. 숲의 미래를 위해 되찾아야 해.']],
        after: [['카이', '씨앗을 숲에 심었다. 백 년 뒤엔 은빛 숲이 다시 하늘을 가리겠지.'], ['카이', '그때도 엘프들은 은빛 늑대 용병단을 노래할 거다. 약속하지.']],
        reward: { stats: { dex: 6 }, rep: 150, newTitle: '세계수의 수호자', awaken: true },
      },
    ],
  },
  seraphine: {
    name: '세라핀', cls: 'cleric', title: '파문당한 성녀', unlock: 2, level: 4, trait: 'saint',
    look: { skin: '#f2c9a0', hair: '#e3c565', longHair: true },
    intro: [
      [null, '주점 구석, 낡은 수녀복 차림의 여인이 조용히 다가옵니다.'],
      ['세라핀', '교단은 저를 버렸지만, 저는 아직 사람들을 버리지 않았어요.'],
      ['세라핀', '치유의 손이 필요하다면… 저를 써 주세요.'],
    ],
    chapters: [
      {
        bond: 3, region: 'swamp', type: 'magic', enemy: '늪 슬라임', title: '가라앉은 수도원의 역병',
        before: [['세라핀', '늪지의 수도원에 역병이 돈대요. 교단은… 모른 척하고 있고요.'], ['세라핀', '제가 쫓겨난 이유도 거기 있어요. 함께 가 주시겠어요?']],
        after: [['세라핀', '역병의 근원은 고위 사제가 숨겨 둔 저주받은 성물이었어요.'], ['세라핀', '이 묵주는 수도원장님이 주신 거예요. 이제 당신들 거예요.']],
        reward: { item: { base: 'amulet', name: '성녀의 묵주', bonus: { int: 8, hp: 12 } } },
      },
      {
        bond: 8, region: 'plains', type: 'escort', enemy: '산적', title: '이단 심문관의 추격',
        before: [['세라핀', '심문관들이 저를 찾아냈어요. 도망치는 것도 이제 지쳤어요.'], ['세라핀', '이번엔 피하지 않겠어요. 진실을 왕도에 전할 거예요.']],
        after: [['세라핀', '왕도의 대신관께서 제 결백을 인정하셨어요!'], ['세라핀', '저는 이제 파문당한 성녀가 아니에요. 은빛 늑대의 성녀예요.']],
        reward: { stats: { int: 4, hp: 12 }, rep: 80, newTitle: '은빛 늑대의 성녀' },
      },
      {
        bond: 14, region: 'frost', type: 'magic', enemy: '리치의 망령', title: '타락한 사제의 의식',
        before: [['세라핀', '역병 성물을 숨긴 진짜 배후는 대신관 직속의 사제였어요. 그가 북쪽 지하묘지에서 금지된 의식을 치르고 있어요.'], ['세라핀', '이번엔 제가 앞장설게요.']],
        after: [['세라핀', '의식은 막았어요. 그 사람도… 마지막엔 용서를 빌었어요.'], ['세라핀', '이제 알겠어요. 제 신앙은 교단이 아니라 곁에 있는 사람들에게 있었다는 걸요.']],
        reward: { stats: { int: 6, hp: 10 }, rep: 150, newTitle: '빛을 되찾은 성녀', awaken: true },
      },
    ],
  },
  lyra: {
    name: '리라', cls: 'rogue', title: '가면 쓴 의적', unlock: 3, level: 5, trait: 'shadow',
    look: { skin: '#f5d6b8', hair: '#8c2f2f', longHair: true },
    intro: [
      [null, '주머니가 가벼워진 느낌… 돌아보니 붉은 머리 소녀가 금화를 흔들고 있습니다.'],
      ['리라', '경비가 허술하네, 단장님? 그래서 여기가 마음에 들어.'],
      ['리라', '부자들 금고만 터는 의적, 리라야. 고용하면 안 훔칠게. 아마도.'],
    ],
    chapters: [
      {
        bond: 3, region: 'desert', type: 'explore', enemy: '사막 도적', title: '세금 징수관의 금고',
        before: [['리라', '교역소 징수관이 마을 세금을 두 배로 떼어먹고 있대.'], ['리라', '증거는 그 녀석 금고 안에 있어. 같이 털러 가자고!']],
        after: [['리라', '장부 확보! 마을 사람들 돈은 전부 돌려줬어.'], ['리라', '이건 덤으로 챙긴 거. 단장님 몫이야.']],
        reward: { item: { base: 'dagger', name: '그림자 단검', bonus: { dex: 12, str: 5 } } },
      },
      {
        bond: 8, region: 'frost', type: 'explore', enemy: '해골 병사', title: '가면 뒤의 이름',
        before: [['리라', '사실… 난 몰락한 백작가의 딸이야. 우리 집안을 무너뜨린 놈이 북부 요새에 있어.'], ['리라', '복수 말고, 진실을 원해.']],
        after: [['리라', '아버지는 반역자가 아니었어. 이제 증명했어.'], ['리라', '가면은 벗을게. 그래도 손버릇은 못 고쳐, 헤헤.']],
        reward: { stats: { dex: 5, int: 3 }, rep: 80, newTitle: '백작가의 의적' },
      },
      {
        bond: 14, region: 'desert', type: 'explore', enemy: '미믹', title: '재상의 비밀 금고',
        before: [['리라', '아버지를 모함한 진짜 흑막은 왕의 재상이야. 증거가 사막 신전의 비밀 금고에 있어.'], ['리라', '함정투성이라던데… 뭐, 내가 있잖아?']],
        after: [['리라', '재상은 체포됐고 우리 가문 이름도 되찾았어.'], ['리라', '백작 아가씨 노릇은 따분하겠지만… 은빛 늑대 일은 계속할 거야. 당연하지!']],
        reward: { stats: { dex: 6, int: 3 }, rep: 150, newTitle: '돌아온 백작 영애', awaken: true },
      },
    ],
  },
  grom: {
    name: '그롬', cls: 'warrior', title: '피의 투기장 챔피언', unlock: 3, level: 5, trait: 'berserker',
    look: { skin: '#8fae6a', hair: '#2b1d14', longHair: false },
    intro: [
      [null, '덩치 큰 혼혈 오크가 테이블을 쾅 내리칩니다.'],
      ['그롬', '투기장에서 백 번 이겼다. 이제 지겹다.'],
      ['그롬', '진짜 싸움을 원한다. 돈은 술값이면 된다.'],
    ],
    chapters: [
      {
        bond: 3, region: 'desert', type: 'hunt', enemy: '오크', title: '투기장주의 사냥개',
        before: [['그롬', '투기장주 바락스가 내 목에 현상금을 걸었다. 도망친 노예라나.'], ['그롬', '그놈 사냥개들부터 부숴 버리자.']],
        after: [['그롬', '바락스의 사냥개들은 끝났다.'], ['그롬', '이 대검은 투기장 시절 죽은 동료의 것이다. 네가 맡아라.']],
        reward: { item: { base: 'sword', name: '투사의 대검', bonus: { str: 13, hp: 8 } } },
      },
      {
        bond: 8, region: 'desert', type: 'hunt', enemy: '전갈 거인', title: '사슬을 끊어라',
        before: [['그롬', '투기장엔 아직 내 형제들이 갇혀 있다.'], ['그롬', '단장, 한 번만 내 싸움에 함께해 다오.']],
        after: [['그롬', '사슬은 끊어졌다. 형제들이 자유를 얻었다.'], ['그롬', '이제 내 무리는 이곳이다. 은빛 늑대를 위해 싸우겠다.']],
        reward: { stats: { str: 5, hp: 15 }, rep: 90, newTitle: '해방자' },
      },
      {
        bond: 14, region: 'dragon', type: 'hunt', enemy: '오크', title: '부족장과의 결투',
        before: [['그롬', '오크 부족들이 용의 산맥에 모여 전쟁을 준비한다. 내 피의 절반이 그들이다.'], ['그롬', '싸우지 않고 끝낼 방법이 있다면… 족장과 결투하겠다.']],
        after: [['그롬', '족장은 내게 졌다. 부족들은 산으로 돌아갔다.'], ['그롬', '오크도 인간도 아닌 나를 받아준 건 이곳뿐이다. 고맙다, 단장.']],
        reward: { stats: { str: 6, hp: 15 }, rep: 150, newTitle: '두 피의 족장', awaken: true },
      },
    ],
  },
  astel: {
    name: '아스텔', cls: 'mage', title: '마탑의 마지막 제자', unlock: 4, level: 6, trait: 'arcane',
    look: { skin: '#f2c9a0', hair: '#c9c2b8', longHair: true },
    intro: [
      [null, '책 더미를 짊어진 은발의 청년이 주점에 들어섭니다.'],
      ['아스텔', '마탑이 무너진 지 10년. 살아남은 제자는 저 하나뿐입니다.'],
      ['아스텔', '스승님의 연구를 이어가려면 돈과… 믿을 만한 호위가 필요해요.'],
    ],
    chapters: [
      {
        bond: 3, region: 'swamp', type: 'magic', enemy: '망령', title: '무너진 마탑의 서고',
        before: [['아스텔', '마탑 폐허 지하에 스승님의 서고가 남아 있을 거예요.'], ['아스텔', '단, 마탑을 무너뜨린 마력 폭주의 잔재가 아직 그곳을 떠돌고 있죠.']],
        after: [['아스텔', '찾았다… 스승님의 마지막 연구 노트.'], ['아스텔', '이 지팡이도요. 스승님께서 쓰시던 겁니다.']],
        reward: { item: { base: 'staff', name: '대마도사의 지팡이', bonus: { int: 15, dex: 4 } } },
      },
      {
        bond: 8, region: 'dragon', type: 'magic', enemy: '리치의 망령', title: '폭주의 진실',
        before: [['아스텔', '마탑 붕괴는 사고가 아니었어요. 누군가 용의 심장으로 마력을 폭주시켰죠.'], ['아스텔', '그 심장이 용의 등뼈 산맥에 있습니다.']],
        after: [['아스텔', '용의 심장을 봉인했어요. 다시는 그런 비극이 없을 겁니다.'], ['아스텔', '언젠가 이 용병단 안에 새 마탑을 세우고 싶네요.']],
        reward: { stats: { int: 6, dex: 2 }, rep: 100, newTitle: '새 마탑의 주인' },
      },
      {
        bond: 14, region: 'frost', type: 'magic', enemy: '서리 트롤', title: '새 마탑의 초석',
        before: [['아스텔', '새 마탑을 세울 터를 찾았어요. 서리 협곡의 고대 마력 샘이요.'], ['아스텔', '하지만 샘을 지키는 서리의 괴물들이 쉽게 허락하진 않겠죠.']],
        after: [['아스텔', '샘의 주인이 우리를 인정했어요. 이곳에 은빛 늑대의 마탑을 세울 거예요.'], ['아스텔', '스승님, 보고 계신가요?']],
        reward: { stats: { int: 7 }, rep: 150, newTitle: '은빛 마탑의 대마도사', awaken: true },
      },
    ],
  },
  marisol: {
    name: '마리솔', cls: 'archer', title: '닻을 잃은 해적 선장', unlock: 4, level: 9, trait: 'captain',
    look: { skin: '#c68a5c', hair: '#2b1d14', longHair: true },
    intro: [
      [null, '짠내 나는 외투를 걸친 여인이 주점 문을 발로 차고 들어옵니다.'],
      ['마리솔', '배는 가라앉았고 선원들은 흩어졌지. 남은 건 이 활 한 자루뿐이야.'],
      ['마리솔', '당분간 육지에서 일 좀 하자고. 보수만 확실하면 돼, 단장.'],
    ],
    chapters: [
      {
        bond: 3, region: 'desert', type: 'escort', enemy: '사막 도적', title: '흩어진 선원들',
        before: [['마리솔', '내 선원들이 사막 교역소에서 노예로 팔렸다는 소문이 있어.'], ['마리솔', '선장이 선원을 버릴 순 없지. 데리러 가자.']],
        after: [['마리솔', '다 데려왔어. 한 놈도 빠짐없이.'], ['마리솔', '이건 우리 배의 나침반이야. 길을 잃지 않게 해 줄 거야.']],
        reward: { item: { base: 'amulet', name: '선장의 나침반', bonus: { dex: 9, int: 6, hp: 6 } } },
      },
      {
        bond: 8, region: 'dragon', type: 'hunt', enemy: '와이번', title: '배를 가라앉힌 날개',
        before: [['마리솔', '내 배를 가라앉힌 건 폭풍이 아니었어. 용의 산맥에서 날아온 와이번 떼였지.'], ['마리솔', '빚은 갚아야겠지?']],
        after: [['마리솔', '복수는 끝났어. 생각보다 후련하진 않네.'], ['마리솔', '이제 바다 대신 이 용병단이 내 배야. 잘 부탁해, 단장.']],
        reward: { stats: { dex: 5, hp: 10 }, rep: 100, newTitle: '은빛 늑대호의 선장' },
      },
    ],
  },
  oswin: {
    name: '오스윈', cls: 'warrior', adv: 'paladin', title: '몰락한 기사단장', unlock: 5, level: 10, trait: 'commander',
    look: { skin: '#e0ac7e', hair: '#c9c2b8', longHair: false },
    intro: [
      [null, '녹슨 갑옷의 노기사가 정중하게 고개를 숙입니다.'],
      ['오스윈', '한때 왕국 기사단을 이끌었으나, 지금은 이름뿐인 늙은이일세.'],
      ['오스윈', '자네 용병단의 소문을 들었네. 남은 검을 의미 있는 곳에 쓰고 싶군.'],
    ],
    chapters: [
      {
        bond: 3, region: 'frost', type: 'defense', enemy: '해골 병사', title: '북부 요새의 망령들',
        before: [['오스윈', '내가 지키지 못한 북부 요새… 전사한 기사들이 망령이 되어 떠돈다고 하네.'], ['오스윈', '그들을 편히 보내주는 게 단장으로서 내 마지막 의무일세.']],
        after: [['오스윈', '모두 잠들었네. 고맙네, 젊은 단장.'], ['오스윈', '이 갑옷은 요새 깃발 아래 묻혀 있던 것일세. 자네들이 쓰게.']],
        reward: { item: { base: 'plate', name: '기사단장의 백은 갑옷', bonus: { hp: 30, str: 6 } } },
      },
      {
        bond: 8, region: 'dragon', type: 'magic', enemy: '리치의 망령', title: '요새를 무너뜨린 자',
        before: [['오스윈', '요새를 함락시킨 건 리치였네. 놈이 용의 산맥에 숨어 있다는 걸 알아냈지.'], ['오스윈', '늙은 검이지만 아직 한 번은 더 휘두를 수 있네.']],
        after: [['오스윈', '끝났네. 이제야 기사단의 이름을 되찾았어.'], ['오스윈', '왕국이 기사단 재건을 제안했지만 거절했네. 내 기사단은 여기 있으니까.']],
        reward: { stats: { str: 4, hp: 20 }, rep: 120, newTitle: '은빛 늑대의 기사단장' },
      },
    ],
  },
};
