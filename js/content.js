// 콘텐츠: 몬스터, 보스, 장비, 특별 용병(이야기)
'use strict';

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
  // ── 마왕군 ──
  '마족 전사':   { tpl: 'demon', pal: { M: '#8a2430', D: '#5a1420', L: '#c25a5a', A: '#3a2a2a', E: '#f2c94c' } },
  '지옥견':     { tpl: 'beast', pal: { M: '#7a2418', D: '#4a140c', E: '#f39c12' } },
  '데스 나이트': { tpl: 'imp', pal: { M: '#4a4a5a', D: '#2a2a36', A: '#6b2a6b', E: '#7ed3c8' } },
  '마왕 베르녹스': { tpl: 'demon', pal: { M: '#4a1a3a', D: '#22081a', L: '#8a3a6a', A: '#d6455d', E: '#f2c94c' }, big: true, boss: true },
  '고룡 이그니스': { tpl: 'drake', pal: { M: '#2a2a3a', D: '#14141e', L: '#d6455d', A: '#7a2430', E: '#f39c12' }, big: true, boss: true },
};

// ───────── 재앙급 괴물 (보스) ─────────
// 지방 의뢰를 clears번 성공하면 등장. 처치하면 그 지방 소유 세력의 평판이 크게 오르고 지방 보상 +10%.
const BOSSES = {
  wheat: {
    enemy: '고블린 왕', name: '고블린 왕 그릭스', type: 'hunt', title: '고블린 왕의 요새 습격', clears: 4,
    intro: '밀밭 일대의 고블린들이 「왕」을 자처하는 거대한 고블린 아래 모여들고 있습니다. 왕국군은 국경 전쟁에 묶여 손을 쓰지 못합니다.',
    outro: '고블린 왕이 쓰러지자 무리는 뿔뿔이 흩어졌습니다. 농민들이 은빛 늑대의 이름을 연호합니다.',
    reward: { base: 'mace', name: '그릭스의 황금 왕홀', bonus: { str: 8, int: 8 } },
  },
  silverwood: {
    enemy: '거미 여왕', name: '거미 여왕 아라크네아', type: 'hunt', title: '거미 여왕의 둥지', clears: 5,
    intro: '은빛 숲 깊은 곳, 수백 년을 산 거미 여왕이 깨어났습니다. 엘프 순찰대만으로는 감당하지 못합니다.',
    outro: '여왕의 둥지가 무너졌습니다. 숲에 다시 새소리가 들립니다.',
    reward: { base: 'leather', name: '여왕의 비단 갑옷', bonus: { hp: 20, dex: 10 } },
  },
  mist: {
    enemy: '늪의 마녀', name: '늪의 마녀 모르가나', type: 'magic', title: '늪의 마녀를 봉인하라', clears: 5,
    intro: '안개 늪지의 저주는 모두 한 마녀의 원한에서 비롯되었습니다. 어느 세력도 늪을 원하지 않기에, 주민들은 길드에 매달립니다.',
    outro: '마녀의 원한이 풀리며 늪의 안개가 옅어졌습니다.',
    reward: { base: 'robe', name: '마녀의 안개 로브', bonus: { hp: 12, int: 14 } },
  },
  oasis: {
    enemy: '모래 폭군', name: '모래 폭군 사르칸', type: 'defense', title: '모래 폭군의 진격을 막아라', clears: 6,
    intro: '교역로를 집어삼키는 거대한 전갈 「모래 폭군」이 오아시스 도시로 향하고 있습니다.',
    outro: '폭군의 껍질이 모래 위에 쓰러졌습니다. 교역로가 다시 활기를 되찾습니다.',
    reward: { base: 'plate', name: '폭군의 갑각 갑옷', bonus: { hp: 32, str: 8 } },
  },
  frost: {
    enemy: '서리 거인 왕', name: '서리 거인 왕 위르겔', type: 'defense', title: '북부 요새 최후의 방어전', clears: 6,
    intro: '서리 거인 왕이 거인 군단을 이끌고 북부 요새로 내려옵니다. 요새가 무너지면 북부 전체가 위험합니다.',
    outro: '거인 왕이 무릎을 꿇었습니다. 북부 요새의 종이 승리를 알립니다.',
    reward: { base: 'ring', name: '서리 왕관 반지', bonus: { str: 10, dex: 10, int: 10 } },
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
// 길드 등급이 오르면 모집소에 나타난다. faction: 연고 세력(평판이 -30 이하면 찾아오지 않음).
// 장(chapter): province 지방, type 의뢰 유형, target 대상 세력(분쟁 의뢰), enemy 괴물(괴물 의뢰)
// choice: 완료 후 선택지. effects = { standing: {세력: 변화}, relations: {'a|b': 변화}, peace: 'a|b', gold }
const HEROES = {
  kai: {
    name: '카이', cap: 'silverscout', cls: 'archer', title: '숲을 떠난 엘프 정찰병', unlock: 1, level: 3, trait: 'hawkeye', faction: 'elves',
    look: { skin: '#f5d6b8', hair: '#e3c565', longHair: true },
    intro: [
      [null, '뾰족한 귀의 궁수가 창가 자리에서 화살깃을 다듬고 있습니다.'],
      ['카이', '왕국은 숲을 베고, 장로회의 강경파는 전쟁을 하자고 하지. 둘 다 숲을 지키는 방법은 아니야.'],
      ['카이', '난 인간 쪽에서 길을 찾아보려고 한다. 너희 길드, 실력이 있다고 들었다.'],
    ],
    chapters: [
      {
        bond: 3, province: 'silverwood', type: 'raid', target: 'crown', title: '벌목 야영지 습격',
        before: [['카이', '왕국 벌목단이 허락도 없이 은빛 숲 경계를 넘었다. 경비병까지 붙여서.'], ['카이', '피를 보자는 게 아니야. 야영지를 무너뜨리고 쫓아내기만 하면 돼.']],
        after: [['카이', '벌목꾼들은 돌아갔다. 장로들이 처음으로 인간에게 고맙다고 하더군.'], ['카이', '이 활은 장로회가 보낸 선물이다.']],
        reward: { item: { base: 'bow', name: '은빛 숲의 장궁', bonus: { dex: 13, str: 4 } } },
      },
      {
        bond: 8, province: 'silverwood', type: 'envoy', target: 'crown', title: '숲의 경계 회담',
        before: [['카이', '왕국이 회담을 제안했다. 강경파는 함정이라며 전쟁을 원하고.'], ['카이', '회담장까지 사절을 지켜 다오. 결론은… 네 생각도 듣고 싶다, 단장.']],
        after: [['카이', '회담은 무사히 열렸다. 이제 정해야 해.']],
        choice: {
          prompt: '회담에서 은빛 늑대 길드는 어느 안을 지지할까요?',
          options: [
            { label: '엘프의 주장 — 숲 경계 확정', effects: { standing: { elves: 25, crown: -15 }, relations: { 'crown|elves': -10 } },
              after: [['카이', '숲은 숲으로 남는다. 고맙다, 단장.']] },
            { label: '왕국의 중재안 — 일부 개방과 공동 순찰', effects: { standing: { crown: 15, elves: 5, cities: 10 }, relations: { 'crown|elves': 30 } },
              after: [['카이', '완벽한 답은 아니지만… 피는 흐르지 않겠지. 장로들은 내가 설득하마.']] },
          ],
        },
        reward: { stats: { dex: 5, hp: 8 }, rep: 80, newTitle: '숲의 수호자' },
      },
      {
        bond: 14, province: 'dragon', type: 'hunt', enemy: '와이번', title: '세계수의 씨앗',
        before: [['카이', '전설로만 전하던 세계수의 씨앗이 용의 산맥에 있다고 한다.'], ['카이', '와이번들이 그 씨앗을 둥지에 품고 있다. 숲의 미래를 위해 되찾아야 해.']],
        after: [['카이', '씨앗을 숲에 심었다. 백 년 뒤엔 은빛 숲이 다시 하늘을 가리겠지.'], ['카이', '그때도 엘프들은 은빛 늑대를 노래할 거다. 약속하지.']],
        reward: { stats: { dex: 6 }, rep: 150, newTitle: '세계수의 수호자', awaken: true, standing: { elves: 20 } },
      },
    ],
  },
  seraphine: {
    name: '세라핀', cap: 'exsaint', cls: 'cleric', title: '파문당한 성녀', unlock: 2, level: 4, trait: 'saint', faction: null,
    look: { skin: '#f2c9a0', hair: '#e3c565', longHair: true },
    intro: [
      [null, '주점 구석, 낡은 수녀복 차림의 여인이 조용히 다가옵니다.'],
      ['세라핀', '교단은 저를 파문했어요. 진실을 말했다는 이유로요.'],
      ['세라핀', '치유의 손이 필요하다면… 저를 써 주세요. 대신, 언젠가 제 싸움도 도와주세요.'],
    ],
    chapters: [
      {
        bond: 3, province: 'mist', type: 'magic', enemy: '늪 슬라임', title: '가라앉은 수도원의 역병',
        before: [['세라핀', '늪지의 수도원에 역병이 돈대요. 교단은 모른 척하고 있고요.'], ['세라핀', '제가 파문당한 이유도 거기 있어요. 함께 가 주시겠어요?']],
        after: [['세라핀', '역병의 근원은 교단 고위 사제가 숨겨 둔 저주받은 성물이었어요.'], ['세라핀', '이 묵주는 수도원장님이 주신 거예요. 이제 당신들 거예요.']],
        reward: { item: { base: 'amulet', name: '성녀의 묵주', bonus: { int: 8, hp: 12 } } },
      },
      {
        bond: 8, province: 'sanctum', type: 'rescue', target: 'church', title: '심문소의 수녀들',
        before: [['세라핀', '역병의 진실을 말한 수녀들이 이단 혐의로 심문소에 갇혔어요.'], ['세라핀', '교단과 척을 지게 되겠지만… 그들을 두고 볼 수는 없어요.']],
        after: [['세라핀', '모두 무사해요. 교단은 이제 저를 이단으로 공표하겠죠.'], ['세라핀', '괜찮아요. 제가 믿는 빛은 심문소 안에 있지 않으니까요.']],
        reward: { stats: { int: 4, hp: 12 }, rep: 80, newTitle: '은빛 늑대의 성녀' },
      },
      {
        bond: 14, province: 'sanctum', type: 'sabotage', target: 'church', title: '타락한 대신관의 장부',
        before: [['세라핀', '역병 성물도, 심문도, 모두 한 사람의 지시였어요. 대신관 직속의 사제 바르톨로.'], ['세라핀', '그가 숨긴 장부만 있으면… 교단을 바꿀 수 있어요.']],
        after: [['세라핀', '장부를 손에 넣었어요. 이걸 어떻게 쓸지는… 함께 정해요.']],
        choice: {
          prompt: '바르톨로의 장부를 어떻게 할까요?',
          options: [
            { label: '교단 개혁파에게 넘긴다 — 안에서 바로잡기', effects: { standing: { church: 30, crown: 5 } },
              after: [['세라핀', '개혁파가 바르톨로를 파면했어요. 교단이… 조금은 나아지겠죠.']] },
            { label: '왕국에 폭로한다 — 교단의 권위를 꺾기', effects: { standing: { crown: 25, church: -30, north: 5 }, relations: { 'crown|church': -35 } },
              after: [['세라핀', '왕이 교단의 특권을 박탈했어요. 이 결정이 옳았기를 기도할게요.']] },
          ],
        },
        reward: { stats: { int: 6, hp: 10 }, rep: 150, newTitle: '빛을 되찾은 성녀', awaken: true },
      },
    ],
  },
  lyra: {
    name: '리라', cap: 'outlaw', cls: 'rogue', title: '가면 쓴 의적', unlock: 3, level: 5, trait: 'shadow', faction: 'north',
    look: { skin: '#f5d6b8', hair: '#8c2f2f', longHair: true },
    intro: [
      [null, '주머니가 가벼워진 느낌… 돌아보니 붉은 머리 소녀가 금화를 흔들고 있습니다.'],
      ['리라', '경비가 허술하네, 단장님? 그래서 여기가 마음에 들어.'],
      ['리라', '왕의 관리들 금고만 터는 의적, 리라야. 고용하면 안 훔칠게. 아마도.'],
    ],
    chapters: [
      {
        bond: 3, province: 'border', type: 'sabotage', target: 'crown', title: '세금 징수관의 금고',
        before: [['리라', '국경령 징수관이 마을 세금을 두 배로 떼어먹고 있대. 왕의 이름을 팔아서.'], ['리라', '증거는 그 녀석 금고 안에 있어. 같이 털러 가자고!']],
        after: [['리라', '장부 확보! 마을 사람들 돈은 전부 돌려줬어.'], ['리라', '이건 덤으로 챙긴 거. 단장님 몫이야.']],
        reward: { item: { base: 'dagger', name: '그림자 단검', bonus: { dex: 12, str: 5 } } },
      },
      {
        bond: 8, province: 'frost', type: 'explore', enemy: '해골 병사', title: '가면 뒤의 이름',
        before: [['리라', '사실… 난 몰락한 북부 백작가의 딸이야. 우리 집안의 마지막 기록이 북부 요새 지하에 있어.'], ['리라', '아버지가 정말 반역자였는지, 이제는 알아야겠어.']],
        after: [['리라', '아버지는 반역자가 아니었어. 누군가 왕도에서 꾸민 일이야.'], ['리라', '이름이 하나 나왔어. 왕의 재상.']],
        reward: { stats: { dex: 5, int: 3 }, rep: 80, newTitle: '백작가의 의적', standing: { north: 10 } },
      },
      {
        bond: 14, province: 'royal', type: 'sabotage', target: 'crown', title: '재상의 비밀 금고',
        before: [['리라', '아버지를 반역자로 몰아 죽인 건 재상이야. 증거가 왕도 지하 금고에 있어.'], ['리라', '왕도 한복판이야. 들키면 끝장이지만… 할 거지?']],
        after: [['리라', '문서는 손에 넣었어. 이제 누구에게 넘길지가 문제야.']],
        choice: {
          prompt: '재상의 음모를 증명할 문서를 누구에게 넘길까요?',
          options: [
            { label: '국왕에게 — 왕국 안에서 정의를', effects: { standing: { crown: 20, north: -5 } },
              after: [['리라', '재상은 체포됐고 우리 가문 이름도 되찾았어. 왕도 썩 나쁜 사람은 아니더라.']] },
            { label: '북부 귀족 연합에 — 왕권의 부패를 알리기', effects: { standing: { north: 30, crown: -25 }, relations: { 'crown|north': -25 } },
              after: [['리라', '북부가 들끓고 있어. 전쟁이 날지도 몰라… 그래도 진실은 알려졌어.']] },
          ],
        },
        reward: { stats: { dex: 6, int: 3 }, rep: 150, newTitle: '돌아온 백작 영애', awaken: true },
      },
    ],
  },
  grom: {
    name: '그롬', cap: 'pitchampion', cls: 'warrior', title: '피의 투기장 챔피언', unlock: 3, level: 5, trait: 'berserker', faction: 'clans',
    look: { skin: '#8fae6a', hair: '#2b1d14', longHair: false },
    intro: [
      [null, '덩치 큰 혼혈 오크가 테이블을 쾅 내리칩니다.'],
      ['그롬', '자유 도시의 투기장에서 백 번 이겼다. 백한 번째에 사슬을 끊고 나왔지.'],
      ['그롬', '돈은 술값이면 된다. 대신 내 형제들 일에 언젠가 손을 빌려줘라.'],
    ],
    chapters: [
      {
        bond: 3, province: 'oasis', type: 'raid', target: 'cities', title: '투기장주의 사냥꾼들',
        before: [['그롬', '투기장주 바락스가 내 목에 현상금을 걸었다. 그놈은 의회 의원이기도 하지.'], ['그롬', '놈의 노예 사냥꾼 부대부터 부숴 버리자.']],
        after: [['그롬', '사냥꾼들은 끝났다.'], ['그롬', '이 대검은 투기장 시절 죽은 동료의 것이다. 네가 맡아라.']],
        reward: { item: { base: 'sword', name: '투사의 대검', bonus: { str: 13, hp: 8 } } },
      },
      {
        bond: 8, province: 'oasis', type: 'rescue', target: 'cities', title: '사슬을 끊어라',
        before: [['그롬', '투기장엔 아직 내 형제들이 갇혀 있다. 오크도, 사막 부족도, 인간도.'], ['그롬', '단장, 한 번만 내 싸움에 함께해 다오.']],
        after: [['그롬', '사슬은 끊어졌다. 형제들이 자유를 얻었다.'], ['그롬', '부족들이 내 이름을 부르기 시작했다. 기분이 묘하군.']],
        reward: { stats: { str: 5, hp: 15 }, rep: 90, newTitle: '해방자', standing: { clans: 15 } },
      },
      {
        bond: 14, province: 'redsand', type: 'envoy', target: 'crown', title: '부족장 회합',
        before: [['그롬', '부족들이 회합을 연다. 왕국과 끝까지 싸울지, 칼을 내려놓을지.'], ['그롬', '나는 족장 자리에 도전한다. 회합장까지 함께 가 다오.']],
        after: [['그롬', '…이겼다. 이제 내 말이 곧 부족의 뜻이다.']],
        choice: {
          prompt: '족장이 된 그롬이 묻습니다. 「단장, 부족은 어디로 가야 하나?」',
          options: [
            { label: '왕국과 휴전하라', effects: { standing: { clans: 15, crown: 20 }, relations: { 'crown|clans': 50 }, peace: 'crown|clans' },
              after: [['그롬', '칼을 내려놓는다. 쉽지 않겠지만… 아이들이 전쟁을 모르고 자라길 바란다.']] },
            { label: '빼앗긴 땅을 되찾아라', effects: { standing: { clans: 30, crown: -25 }, relations: { 'crown|clans': -20 } },
              after: [['그롬', '부족이 하나로 뭉쳤다. 왕국은 이제 진짜 전쟁을 보게 될 거다.']] },
          ],
        },
        reward: { stats: { str: 6, hp: 15 }, rep: 150, newTitle: '두 피의 족장', awaken: true },
      },
    ],
  },
  astel: {
    name: '아스텔', cap: 'towerheir', cls: 'mage', title: '마탑의 마지막 제자', unlock: 4, level: 6, trait: 'arcane', faction: null,
    look: { skin: '#f2c9a0', hair: '#c9c2b8', longHair: true },
    intro: [
      [null, '책 더미를 짊어진 은발의 청년이 주점에 들어섭니다.'],
      ['아스텔', '마탑이 불탄 지 10년. 살아남은 제자는 저 하나뿐입니다.'],
      ['아스텔', '모두 마력 폭주 사고라고 하더군요. 저는 믿지 않습니다.'],
    ],
    chapters: [
      {
        bond: 3, province: 'mist', type: 'magic', enemy: '망령', title: '무너진 마탑의 서고',
        before: [['아스텔', '마탑 폐허 지하에 스승님의 서고가 남아 있을 거예요.'], ['아스텔', '폐허엔 그날 죽은 이들의 망령이 떠돈다더군요.']],
        after: [['아스텔', '찾았다… 스승님의 마지막 연구 노트.'], ['아스텔', '이 지팡이도요. 스승님께서 쓰시던 겁니다.']],
        reward: { item: { base: 'staff', name: '대마도사의 지팡이', bonus: { int: 15, dex: 4 } } },
      },
      {
        bond: 8, province: 'sanctum', type: 'sabotage', target: 'church', title: '불탄 서고의 명령서',
        before: [['아스텔', '노트에 적혀 있었어요. 마탑을 불태운 건 사고가 아니라 교단 심문관들이었다고.'], ['아스텔', '심문소 기록 보관소에 그날의 명령서가 있을 거예요.']],
        after: [['아스텔', '명령서를 찾았어요. 대신관의 인장이 찍혀 있네요.'], ['아스텔', '복수는 하지 않을 거예요. 하지만 잊지도 않을 겁니다.']],
        reward: { stats: { int: 6, dex: 2 }, rep: 100, newTitle: '진실을 쥔 마도사' },
      },
      {
        bond: 14, province: 'frost', type: 'magic', enemy: '서리 트롤', title: '새 마탑의 초석',
        before: [['아스텔', '새 마탑을 세울 터를 찾았어요. 서리 협곡의 고대 마력 샘이요.'], ['아스텔', '샘을 지키는 괴물들부터 정리해야겠죠.']],
        after: [['아스텔', '샘을 확보했어요. 이제 마탑을 세울 돈과… 후원자가 필요해요.']],
        choice: {
          prompt: '새 마탑의 후원자를 누구로 할까요?',
          options: [
            { label: '성광 교단과 협약 — 감시받는 대신 안전을', effects: { standing: { church: 25, cities: -5 } },
              after: [['아스텔', '교단이 마탑을 인정했어요. 다시는 불타지 않겠죠.']] },
            { label: '자유 도시 연맹의 후원 — 학문의 자유를', effects: { standing: { cities: 25, church: -20 } },
              after: [['아스텔', '자유 도시의 돈으로 마탑이 올라가요. 교단은 못마땅하겠지만요.']] },
          ],
        },
        reward: { stats: { int: 7 }, rep: 150, newTitle: '은빛 마탑의 대마도사', awaken: true },
      },
    ],
  },
  marisol: {
    name: '마리솔', cap: 'corsair', cls: 'archer', title: '닻을 잃은 해적 선장', unlock: 4, level: 9, trait: 'captain', faction: null,
    look: { skin: '#c68a5c', hair: '#2b1d14', longHair: true },
    intro: [
      [null, '짠내 나는 외투를 걸친 여인이 주점 문을 발로 차고 들어옵니다.'],
      ['마리솔', '배는 가라앉았고 선원들은 노예 시장으로 팔려 갔지. 남은 건 이 활 한 자루뿐이야.'],
      ['마리솔', '당분간 육지에서 일 좀 하자고. 보수만 확실하면 돼, 단장.'],
    ],
    chapters: [
      {
        bond: 3, province: 'oasis', type: 'rescue', target: 'cities', title: '흩어진 선원들',
        before: [['마리솔', '내 선원들이 오아시스 노예 시장에 있대. 자유 도시가 허가한 시장이지.'], ['마리솔', '선장이 선원을 버릴 순 없지. 데리러 가자.']],
        after: [['마리솔', '다 데려왔어. 한 놈도 빠짐없이.'], ['마리솔', '이건 우리 배의 나침반이야. 길을 잃지 않게 해 줄 거야.']],
        reward: { item: { base: 'amulet', name: '선장의 나침반', bonus: { dex: 9, int: 6, hp: 6 } } },
      },
      {
        bond: 8, province: 'port', type: 'sabotage', target: 'cities', title: '배를 가라앉힌 계약서',
        before: [['마리솔', '내 배를 가라앉힌 건 폭풍이 아니었어. 의회가 해상 독점을 위해 고용한 사략선이었지.'], ['마리솔', '의회 회관에 그 계약서가 있어. 빚은 갚아야겠지?']],
        after: [['마리솔', '계약서야. 의원 셋의 서명이 있어. 자, 이걸로 뭘 할까?']],
        choice: {
          prompt: '의회의 사략 계약서를 어떻게 할까요?',
          options: [
            { label: '항구에 공개한다 — 의회를 망신 주기', effects: { standing: { cities: -25, crown: 10, north: 5 } },
              after: [['마리솔', '선원들이 의회 앞에서 들고일어났어. 속이 다 시원하네!']] },
            { label: '의회와 거래한다 — 침묵의 대가로 금화', effects: { standing: { cities: 15 }, gold: 800 },
              after: [['마리솔', '복수보단 실리지. …그래도 새 배엔 은빛 늑대 깃발을 걸 거야.']] },
          ],
        },
        reward: { stats: { dex: 5, hp: 10 }, rep: 100, newTitle: '은빛 늑대호의 선장' },
      },
    ],
  },
  oswin: {
    name: '오스윈', cap: 'fallencommander', cls: 'warrior', title: '몰락한 기사단장', unlock: 5, level: 10, trait: 'commander', faction: 'crown',
    look: { skin: '#e0ac7e', hair: '#c9c2b8', longHair: false },
    intro: [
      [null, '녹슨 갑옷의 노기사가 정중하게 고개를 숙입니다.'],
      ['오스윈', '북부 요새가 함락된 날, 나는 기사단과 이름을 함께 잃었네.'],
      ['오스윈', '자네 길드의 소문을 들었네. 남은 검을 의미 있는 곳에 쓰고 싶군.'],
    ],
    chapters: [
      {
        bond: 3, province: 'frost', type: 'defense', enemy: '해골 병사', title: '북부 요새의 망령들',
        before: [['오스윈', '요새에서 죽은 내 기사들이 망령이 되어 떠돈다고 하네.'], ['오스윈', '그들을 편히 보내주는 게 단장으로서 내 마지막 의무일세.']],
        after: [['오스윈', '모두 잠들었네. 고맙네, 젊은 단장.'], ['오스윈', '이 갑옷은 요새 깃발 아래 묻혀 있던 것일세. 자네들이 쓰게.']],
        reward: { item: { base: 'plate', name: '기사단장의 백은 갑옷', bonus: { hp: 30, str: 6 } } },
      },
      {
        bond: 8, province: 'valen', type: 'siege', target: 'north', title: '배신의 성',
        before: [['오스윈', '요새가 함락된 날, 성문을 연 건 발렌 공작의 기사였네. 공작은 북부의 자치를 위해 왕국을 팔았지.'], ['오스윈', '그 기사가 아직 발렌 성에 있네. 진실을 들어야겠어.']],
        after: [['오스윈', '배신자를 붙잡았네. …자네가 정해 주게.']],
        choice: {
          prompt: '배신한 기사를 어떻게 할까요?',
          options: [
            { label: '왕에게 압송한다 — 반역을 고발', effects: { standing: { crown: 25, north: -30 }, relations: { 'crown|north': -30 } },
              after: [['오스윈', '반역의 증거가 왕궁에 닿았네. 이제 북부와의 전쟁은 피할 수 없겠지.']] },
            { label: '용서하고 돌려보낸다 — 더 이상의 피는 없다', effects: { standing: { north: 20, crown: 5 }, relations: { 'crown|north': 20 } },
              after: [['오스윈', '…자네 말이 맞네. 복수는 죽은 기사들을 돌려주지 않아.']] },
          ],
        },
        reward: { stats: { str: 4, hp: 20 }, rep: 120, newTitle: '은빛 늑대의 기사단장' },
      },
    ],
  },
};
