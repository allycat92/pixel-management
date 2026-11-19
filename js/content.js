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
    enemies: ['늪 슬라임', '거대 거미', '망령'],
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
    enemies: ['서리 트롤', '설인', '해골 병사'],
    places: ['북부 요새', '서리 협곡', '얼어붙은 지하묘지', '빙하 동굴'],
  },
  dragon: {
    name: '용의 등뼈 산맥', unlock: 5, levels: [7, 10], travel: 2, outpostCost: 1200,
    pos: [254, 52], color: '#7a3a3a',
    desc: '용이 잠든다는 화산 산맥. 대륙 최강의 용병만이 발을 들인다.',
    enemies: ['와이번', '리치의 망령', '오크'],
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
    ],
  },
};
