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
    name: '카이', hcls: 'silverscout', cls: 'archer', title: '숲을 떠난 엘프 정찰병', unlock: 1, level: 3, trait: 'hawkeye', faction: 'elves',
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
    name: '세라핀', hcls: 'exsaint', cls: 'cleric', title: '파문당한 성녀', unlock: 2, level: 4, trait: 'saint', faction: null,
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
    name: '리라', hcls: 'outlaw', cls: 'rogue', title: '가면 쓴 의적', unlock: 3, level: 5, trait: 'shadow', faction: 'north',
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
    name: '그롬', hcls: 'pitchampion', cls: 'warrior', title: '피의 투기장 챔피언', unlock: 3, level: 5, trait: 'berserker', faction: 'clans',
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
    name: '아스텔', hcls: 'towerheir', cls: 'mage', title: '마탑의 마지막 제자', unlock: 4, level: 6, trait: 'arcane', faction: null,
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
    name: '마리솔', hcls: 'corsair', cls: 'archer', title: '닻을 잃은 해적 선장', unlock: 4, level: 9, trait: 'captain', faction: null,
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
    name: '오스윈', hcls: 'fallencommander', cls: 'warrior', title: '몰락한 기사단장', unlock: 5, level: 10, trait: 'commander', faction: 'crown',
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

// ───────── 용병대장: 영입 서사 ─────────
// 용병대장은 이름과 사연을 가진 단 한 명뿐인 인물이다.
// - 시작할 때 후보 아홉 중 하나를 고른다. 고르지 않은 여덟은 다시 만날 수 없다.
// - 이후 길드 등급에 따라 시기별 대장들의 '영입 과제'가 공개된다. 과제를 달성하면 그 대장의 영입 의뢰(2장)가 열리고,
//   완수하면 합류한다. 과제끼리 서로 부딪혀서 한꺼번에 이루기 어렵지만, 효율적이거나 과감한 플레이로 여러 명을 얻을 수 있다.
const STARTER_CAPTAINS = ['blademaster', 'ironwall', 'tactician', 'lancer', 'huntress', 'hedgemage', 'fieldmedic', 'fixer', 'veteran'];
// 시기별 대장 묶음: 등급(rank)에 이르면 그 시기 대장들의 '영입 과제'가 공개된다.
const CAPTAIN_PHASES = [
  { key: 'early', name: '초반', rank: 1, level: 5, list: ['windhunter', 'shadowlord', 'bard', 'beastmaster', 'runesmith', 'pilgrim'] },
  { key: 'mid1', name: '중반', rank: 3, level: 9, list: ['spellblade', 'saintknight', 'hexer', 'liberator', 'admiral', 'elfwarden'] },
  { key: 'mid2', name: '중반', rank: 4, level: 12, list: ['warlord', 'khan', 'siegemaster', 'inquisitorlord', 'pirateking', 'frostjarl'] },
  { key: 'late', name: '후반', rank: 5, level: 16, list: ['dragonslayer', 'demonhunter', 'archmagus', 'lightbearer', 'shadowqueen', 'titan'] },
];

// ───────── 대장 영입 과제 ─────────
// 과제의 조건을 '한순간에 모두' 만족하면 그 대장이 길드를 찾아오고, 영입 의뢰(2장)가 시작된다.
// 조건끼리 서로 부딪히도록 짰다: 연승·무사고 vs 도박, 교단 우호 vs 교단 적대, 소수 정예 vs 대군, 금화 비축 vs 투자.
// 기한(dayMax)을 넘기거나 조건이 불가능해지면(세력 멸망 등) 그 대장은 떠난다.
// 조건 종류:
//   rank / rep / gold(보유 금화) / standing(f, min|max) / alive(f) / dayMax(기한) / mercsMax(길드 인원 상한) / companies(직속 용병단 수)
//   stat(k, min): streak 연속 성공, hardStreak 성공률 80% 미만 의뢰의 연속 성공(실패하면 0), gambles 성공률 40% 미만 의뢰 성공, bigGambles 25% 미만 성공, monster/magic/raid/siege/counterspy/campaign/calamity 의뢰 성공
//   noDeath(days): 최근 n일 전사자 없음 / adv·masters: 상급·최상급 대원 수 / bosses: 재앙급 괴물 토벌 수 / calamity: 재앙이 대두한 적 있음
const CAPTAIN_CHALLENGES = {
  // 초반 (등급 E부터)
  windhunter: { name: '질풍 같은 성장', conds: [{ t: 'rank', min: 2 }, { t: 'dayMax', v: 22 }] },
  shadowlord: { name: '도박꾼의 눈', conds: [{ t: 'stat', k: 'gambles', min: 3 }, { t: 'dayMax', v: 80 }] },
  bard: { name: '작은 극단', conds: [{ t: 'rep', min: 300 }, { t: 'mercsMax', v: 7 }] },
  beastmaster: { name: '사냥 시즌', conds: [{ t: 'stat', k: 'monster', min: 18 }, { t: 'dayMax', v: 40 }] },
  runesmith: { name: '장인의 금고', conds: [{ t: 'gold', min: 4000 }, { t: 'dayMax', v: 40 }] },
  pilgrim: { name: '무사한 순례', conds: [{ t: 'stat', k: 'hardStreak', min: 6 }, { t: 'noDeath', days: 40 }, { t: 'dayMax', v: 70 }] },
  // 중반 1 (등급 C부터)
  spellblade: { name: '금기 연구', conds: [{ t: 'stat', k: 'magic', min: 10 }, { t: 'adv', min: 6 }, { t: 'dayMax', v: 80 }] },
  saintknight: { name: '빛의 증명', conds: [{ t: 'standing', f: 'church', min: 50 }, { t: 'noDeath', days: 60 }, { t: 'standing', f: 'clans', max: -10 }] },
  hexer: { name: '이단의 거래', conds: [{ t: 'standing', f: 'church', max: -20 }, { t: 'standing', f: 'cities', min: 10 }] },
  liberator: { name: '쇠사슬 끊기', conds: [{ t: 'standing', f: 'clans', min: 30 }, { t: 'standing', f: 'church', max: 0 }, { t: 'alive', f: 'clans' }] },
  admiral: { name: '의회의 신임', conds: [{ t: 'standing', f: 'cities', min: 50 }, { t: 'gold', min: 12000 }, { t: 'dayMax', v: 90 }] },
  elfwarden: { name: '숲의 맹우', conds: [{ t: 'standing', f: 'elves', min: 50 }, { t: 'standing', f: 'church', max: 0 }, { t: 'alive', f: 'elves' }] },
  // 중반 2 (등급 B부터)
  warlord: { name: '군세의 증명', conds: [{ t: 'stat', k: 'campaign', min: 9 }, { t: 'companies', min: 4 }, { t: 'dayMax', v: 75 }] },
  khan: { name: '초원의 약탈', conds: [{ t: 'stat', k: 'raid', min: 8 }, { t: 'standing', f: 'clans', min: 20 }, { t: 'alive', f: 'clans' }] },
  siegemaster: { name: '무너진 성벽들', conds: [{ t: 'stat', k: 'siege', min: 6 }, { t: 'dayMax', v: 130 }] },
  inquisitorlord: { name: '심문소의 신뢰', conds: [{ t: 'standing', f: 'church', min: 60 }, { t: 'standing', f: 'elves', max: -20 }, { t: 'stat', k: 'counterspy', min: 4 }, { t: 'alive', f: 'church' }] },
  pirateking: { name: '해적왕의 판돈', conds: [{ t: 'gold', min: 10000 }, { t: 'stat', k: 'gambles', min: 5 }] },
  frostjarl: { name: '겨울을 지킨 자', conds: [{ t: 'standing', f: 'north', min: 40 }, { t: 'standing', f: 'crown', max: 0 }, { t: 'alive', f: 'north' }] },
  // 후반 (등급 A부터)
  dragonslayer: { name: '괴물 사냥의 끝', conds: [{ t: 'bosses', min: 6 }, { t: 'dayMax', v: 120 }] },
  demonhunter: { name: '재앙과 싸운 자', conds: [{ t: 'calamity' }, { t: 'stat', k: 'calamity', min: 8 }, { t: 'noDeath', days: 30 }] },
  archmagus: { name: '대가의 제자들', conds: [{ t: 'masters', min: 5 }, { t: 'dayMax', v: 140 }] },
  lightbearer: { name: '새벽의 순례', conds: [{ t: 'stat', k: 'hardStreak', min: 12 }, { t: 'noDeath', days: 90 }] },
  shadowqueen: { name: '밤의 대도박', conds: [{ t: 'stat', k: 'gambles', min: 8 }, { t: 'gold', min: 15000 }] },
  titan: { name: '거인의 시험', conds: [{ t: 'stat', k: 'bigGambles', min: 1 }, { t: 'standing', f: 'clans', min: 20 }] },
};

const CAPTAINS = {
  // ── 창설 후보 ──
  blademaster: {
    name: '바렌', title: '떠돌이 검귀', trait: 'brave', look: { skin: '#e0ac7e', hair: '#2b1d14', longHair: false },
    pitch: [['바렌', '검 한 자루면 충분하다. 앞은 내가 연다. 너는 뒤에서 판을 짜라.']],
  },
  ironwall: {
    name: '브리긴다', title: '철벽의 여단장', trait: 'sturdy', look: { skin: '#f2c9a0', hair: '#a8642a', longHair: true },
    pitch: [['브리긴다', '내 방패 뒤에 선 녀석은 아무도 죽지 않았다. 앞으로도 그럴 거다.']],
  },
  tactician: {
    name: '이사벨', title: '퇴역 참모', trait: 'genius', look: { skin: '#f5d6b8', hair: '#3a3f6b', longHair: true },
    pitch: [['이사벨', '싸움은 칼을 뽑기 전에 이미 끝나 있어요. 저와 함께라면 지는 싸움은 하지 않을 겁니다.']],
  },

  lancer: {
    name: '로드릭', title: '말을 잃은 기사', trait: 'brave', look: { skin: '#f2c9a0', hair: '#5a3720', longHair: false },
    pitch: [['로드릭', '말도 영지도 빚쟁이에게 넘어갔지만, 창끝은 아직 내 것이오. 돌격할 길만 열어 주시오.']],
  },
  huntress: {
    name: '키아라', title: '숲의 덫꾼', trait: 'lucky', look: { skin: '#e0ac7e', hair: '#a8642a', longHair: true },
    pitch: [['키아라', '짐승이든 사람이든, 덫에 걸리면 똑같이 울어. 사냥감 몰이는 나한테 맡겨.']],
  },
  hedgemage: {
    name: '펠릭스', title: '시골 마법사', trait: 'diligent', look: { skin: '#f5d6b8', hair: '#e3c565', longHair: false },
    pitch: [['펠릭스', '마탑 졸업장은 없지만, 우리 마을 늑대들은 제 불꽃을 무서워하죠. 써 보시면 압니다.']],
  },
  fieldmedic: {
    name: '마그다', title: '종군 의무관', trait: 'sturdy', look: { skin: '#c68a5c', hair: '#2b1d14', longHair: true },
    pitch: [['마그다', '전쟁에서 사람을 제일 많이 살린 건 칼이 아니라 붕대였어. 내 대원은 내가 데리고 돌아간다.']],
  },
  fixer: {
    name: '진', title: '뒷골목 해결사', trait: 'greedy', look: { skin: '#e0ac7e', hair: '#2b1d14', longHair: false },
    pitch: [['진', '깔끔하게, 조용하게, 확실하게. 값만 맞으면 어떤 일이든 해결해 드리죠.']],
  },
  veteran: {
    name: '하랄드', title: '백발의 노병', trait: 'sturdy', look: { skin: '#f2c9a0', hair: '#c9c2b8', longHair: false },
    pitch: [['하랄드', '서른 번 전쟁에 나가 서른 번 살아 돌아왔지. 애송이들 살려 보내는 법은 내가 안다.']],
  },

  // ── 초반 갈림길 ──
  windhunter: {
    name: '나린', title: '바람을 쫓는 사냥꾼', trait: 'lucky', look: { skin: '#c68a5c', hair: '#2b1d14', longHair: true },
    intro: [['나린', '밀밭에 늑대왕이 돌아왔어. 녀석을 잡을 때까진 어느 깃발 아래에도 서지 않을 거야.'], ['나린', '도와준다면… 그다음엔 네 깃발 아래서 활을 당겨 주지.']],
    chapters: [
      { province: 'wheat', type: 'hunt', enemy: '들늑대', title: '늑대왕의 흔적',
        before: [['나린', '발자국이 밀밭을 가로질러 숲으로 이어져. 무리부터 흩어 놓자.']], after: [['나린', '무리는 흩어졌어. 이제 녀석 혼자야.']] },
      { province: 'silverwood', type: 'hunt', enemy: '숲 트롤', title: '숲 끝의 사냥',
        before: [['나린', '늑대왕이 트롤 굴로 숨었어. 둘 다 한꺼번에 끝내자.']], after: [['나린', '끝났다. 약속은 약속이지.']] },
    ],
    join: [['나린', '사냥꾼은 빚을 지고 살지 않아. 오늘부터 네 용병단의 바람이 되어 주지.']],
  },
  shadowlord: {
    name: '모로', title: '항구의 쥐왕', trait: 'greedy', look: { skin: '#e0ac7e', hair: '#5a3720', longHair: false },
    intro: [['모로', '세렌 뒷골목에서 나를 모르면 간첩이지. 요즘 내 구역에 눈치 없는 산적들이 들어왔어.'], ['모로', '청소 좀 해 주면, 내 사람들째로 길드에 붙어 주마. 계산은 확실하게.']],
    chapters: [
      { province: 'port', type: 'escort', enemy: '산적', title: '밀수선 호위',
        before: [['모로', '오늘 밤 배가 들어온다. 화물이 뭔지는 묻지 마.']], after: [['모로', '깔끔했어. 이제 놈들 소굴이다.']] },
      { province: 'royal', type: 'defense', enemy: '산적', title: '빈민가 소탕',
        before: [['모로', '산적 두목이 왕도 빈민가에 숨었다. 내 구역 사람들 다치지 않게 끝내.']], after: [['모로', '훌륭해. 돈 냄새가 나는 길드군.']] },
    ],
    join: [['모로', '거래 성립. 내 정보와 내 칼, 이제 네 거다. 몫만 잘 챙겨 줘.']],
  },

  // ── 중반 갈림길 1 ──
  spellblade: {
    name: '카시안', title: '파문당한 마검사', trait: 'genius', look: { skin: '#f5d6b8', hair: '#c9c2b8', longHair: true },
    intro: [['카시안', '검에 마법을 싣는다는 이유로 기사단에서 쫓겨났지. 그 덕에 이제야 제대로 된 연구를 하고 있어.'], ['카시안', '늪과 고대 숲에서 마력이 미쳐 날뛰고 있다. 같이 가 주면 내 검을 빌려 주지.']],
    chapters: [
      { province: 'mist', type: 'magic', title: '늪지 마력 폭주',
        before: [['카시안', '늪의 마력이 뒤틀려 괴물이 쏟아진다. 근원을 찾아야 해.']], after: [['카시안', '근원은 늪이 아니었어. 더 깊은 곳이다.']] },
      { province: 'deepwood', type: 'magic', title: '고대 숲의 봉인석',
        before: [['카시안', '고대 숲 봉인석에 금이 갔다. 다시 묶지 못하면 숲 전체가 미친다.']], after: [['카시안', '봉인은 버텼다. …나 혼자였다면 못 했겠지.']] },
    ],
    join: [['카시안', '좋아, 이번엔 내가 빚을 졌군. 마검사 카시안, 네 용병단의 칼끝이 되겠다.']],
  },
  saintknight: {
    name: '엘리노어', title: '성광의 기사', trait: 'diligent', look: { skin: '#f2c9a0', hair: '#e3c565', longHair: true },
    intro: [['엘리노어', '교단은 용병을 믿지 않아요. 하지만 저는 당신들이 지켜 낸 사람들을 봤습니다.'], ['엘리노어', '대성당령의 망자들을 잠재우는 일을 함께해 주세요. 교단이 허락한다면, 제 검은 당신 것입니다.']],
    chapters: [
      { province: 'sanctum', type: 'defense', enemy: '망령', title: '성당 묘지의 밤',
        before: [['엘리노어', '묘지의 망령들이 순례자를 해칩니다. 오늘 밤 지켜야 해요.']], after: [['엘리노어', '순례자들은 무사합니다. 다음은 늪이에요.']] },
      { province: 'mist', type: 'escort', enemy: '해골 병사', title: '늪을 건너는 순례',
        before: [['엘리노어', '늪 수도원까지 순례단을 호위합니다. 해골 병사들이 길을 막고 있어요.']], after: [['엘리노어', '순례는 끝났습니다. 이제 제 맹세를 지킬 차례군요.']] },
    ],
    join: [['엘리노어', '빛의 이름으로 맹세합니다. 당신의 용병단에서 누구도 버려지지 않게 하겠습니다.']],
  },

  // ── 중반 갈림길 2 ──
  warlord: {
    name: '가르마크', title: '백전의 전쟁군주', trait: 'brave', look: { skin: '#c68a5c', hair: '#8c2f2f', longHair: false },
    intro: [['가르마크', '왕국과 북부, 어느 쪽 전쟁이든 나가 봤다. 이제는 누구 편도 아닌 전쟁을 하고 싶군.'], ['가르마크', '북부 변경을 휩쓰는 오크 군단을 함께 꺾는다면, 내 군세를 네 깃발 아래 두지.']],
    chapters: [
      { province: 'valen', type: 'hunt', enemy: '오크', title: '변경의 오크 군단',
        before: [['가르마크', '오크들이 발렌 마을들을 불태우고 있다. 정면으로 부순다.']], after: [['가르마크', '잔당이 협곡으로 달아났다. 끝까지 쫓는다.']] },
      { province: 'frost', type: 'defense', enemy: '서리 트롤', title: '협곡 요새 사수',
        before: [['가르마크', '놈들이 서리 트롤을 끌고 요새로 온다. 사흘만 버티면 이긴다.']], after: [['가르마크', '버텼다. 좋은 전쟁이었어.']] },
    ],
    join: [['가르마크', '전쟁군주 가르마크, 오늘부터 네 길드의 군세다. 큰 판에 불러라.']],
  },
  khan: {
    name: '테무르', title: '초원의 칸', trait: 'lucky', look: { skin: '#8d5a3b', hair: '#2b1d14', longHair: true },
    intro: [['테무르', '부족 연합은 내 말을 들으려 하지 않는다. 사막의 교역로가 끊기면 다 굶는데도.'], ['테무르', '교역로를 다시 열어 주면, 부족들도 나도 너를 형제라 부를 거다.']],
    chapters: [
      { province: 'oasis', type: 'escort', enemy: '사막 도적', title: '끊긴 교역로',
        before: [['테무르', '대상단을 오아시스까지 지킨다. 도적 떼가 모래 언덕 뒤에 숨어 있어.']], after: [['테무르', '길은 열렸다. 하지만 도적들이 기대는 괴물이 있다.']] },
      { province: 'redsand', type: 'hunt', enemy: '전갈 거인', title: '모래 아래의 거인',
        before: [['테무르', '도적들이 전갈 거인을 길들였다더군. 놈만 쓰러뜨리면 황야가 조용해진다.']], after: [['테무르', '황야가 숨을 쉰다. 칸은 약속을 지킨다.']] },
    ],
    join: [['테무르', '오늘부터 너는 초원의 형제다. 내 기병들이 네 용병단과 함께 달린다.']],
  },

  // ── 후반 갈림길 ──
  dragonslayer: {
    name: '지크린데', title: '용살자', trait: 'brave', look: { skin: '#f2c9a0', hair: '#e3c565', longHair: true },
    intro: [['지크린데', '용의 등뼈에서 다시 날개 소리가 들린다. 고룡이 깨어나기 전에 새끼들부터 베어야 해.'], ['지크린데', '나와 함께 산을 오른다면, 남은 생은 네 용병단에서 용을 베며 보내겠다.']],
    chapters: [
      { province: 'dragon', type: 'hunt', enemy: '와이번', title: '등뼈 산맥의 날개',
        before: [['지크린데', '와이번 둥지가 산맥 남쪽 절벽에 있다. 알까지 전부 부순다.']], after: [['지크린데', '둥지는 끝났다. 하지만 더 큰 것이 깨어나려 하고 있어.']] },
      { province: 'dragon', type: 'explore', enemy: '가고일', title: '고룡의 잠자리',
        before: [['지크린데', '고룡이 잠든 동굴을 확인해야 한다. 돌의 파수꾼들이 지키고 있지.']], after: [['지크린데', '봤다. 놈은 아직 잔다. 깨어나면… 그땐 함께 베자.']] },
    ],
    join: [['지크린데', '용살자 지크린데, 네 용병단의 칼이 된다. 재앙이 오면 맨 앞에 세워라.']],
  },
  demonhunter: {
    name: '모르데카이', title: '마귀 사냥꾼', trait: 'sturdy', look: { skin: '#e0ac7e', hair: '#c9c2b8', longHair: false },
    intro: [['모르데카이', '안개 늪 아래 문이 숨을 쉰다. 교단은 아직 모르는 척하고 있지.'], ['모르데카이', '문틈으로 새어 나온 것들을 같이 사냥한다면, 내 인장을 네 용병단에 걸어 주마.']],
    chapters: [
      { province: 'mist', type: 'magic', enemy: '리치의 망령', title: '문틈의 리치',
        before: [['모르데카이', '리치 하나가 문틈에서 망자를 부르고 있다. 의식이 끝나기 전에 끊는다.']], after: [['모르데카이', '의식은 끊었다. 그런데 문 너머에서 무언가 대답했어.']] },
      { province: 'frost', type: 'defense', enemy: '데스 나이트', title: '협곡의 죽음 기사',
        before: [['모르데카이', '문이 보낸 죽음의 기사가 서리 협곡을 넘는다. 여기서 막지 못하면 북부가 무덤이 된다.']], after: [['모르데카이', '막았다. 다음에 문이 열리면, 우리가 먼저 들어간다.']] },
    ],
    join: [['모르데카이', '퇴마의 인장은 이제 네 용병단의 것이다. 마귀가 오면 나를 불러라.']],
  },
  // ── 초반 갈림길 (추가) ──
  bard: {
    name: '리코', title: '노래하는 검', trait: 'lucky', look: { skin: '#f2c9a0', hair: '#8c2f2f', longHair: true },
    intro: [['리코', '내 노래는 공짜, 내 검은 비싸지. 그런데 요즘 왕도 극장에 협박장이 날아들어서 말이야.'], ['리코', '극장을 지켜 주면 내 노래와 검을 몽땅 네 용병단에 걸겠어.']],
    chapters: [
      { province: 'royal', type: 'defense', enemy: '산적', title: '극장의 밤',
        before: [['리코', '공연 날 밤에 놈들이 쳐들어온대. 막이 내릴 때까지 버텨 줘.']], after: [['리코', '앵콜까지 무사히! 이제 협박장을 보낸 놈을 찾자.']] },
      { province: 'wheat', type: 'hunt', enemy: '고블린', title: '협박꾼의 정체',
        before: [['리코', '협박꾼이 고블린 떼를 부리는 산적이었어. 밀밭 소굴로 가자.']], after: [['리코', '이 이야기, 노래로 만들어야겠어.']] },
    ],
    join: [['리코', '은빛 늑대의 노래는 이제 내가 부른다. 행군할 때 박자는 맡겨 둬.']],
  },
  beastmaster: {
    name: '오르가', title: '늑대 무리의 어미', trait: 'brave', look: { skin: '#8d5a3b', hair: '#2b1d14', longHair: true },
    intro: [['오르가', '내 늑대들이 국경령 덫에 걸려 죽어 가고 있다. 덫을 놓은 건 밀렵꾼들이지.'], ['오르가', '내 새끼들을 구해 준다면, 무리째로 네 사냥에 따라가겠다.']],
    chapters: [
      { province: 'border', type: 'explore', enemy: '들늑대', title: '덫이 깔린 숲길',
        before: [['오르가', '덫을 피해 늑대들을 찾아야 한다. 겁에 질린 녀석들이 사람을 물 수도 있어.']], after: [['오르가', '몇 마리는 구했다. 밀렵꾼 소굴이 남았어.']] },
      { province: 'silverwood', type: 'hunt', enemy: '거대 거미', title: '밀렵꾼의 소굴',
        before: [['오르가', '밀렵꾼들이 거미굴 옆에 숨어 있다. 둘 다 쓸어버리자.']], after: [['오르가', '무리는 무사하다. 이제 네가 우리 무리의 일부다.']] },
    ],
    join: [['오르가', '나와 내 늑대들은 이제 네 용병단과 함께 달린다. 사냥감은 놓치지 않아.']],
  },
  runesmith: {
    name: '브로크', title: '룬 새기는 대장장이', trait: 'diligent', look: { skin: '#e0ac7e', hair: '#a8642a', longHair: false },
    intro: [['브로크', '내 대장간 룬석을 도적들이 훔쳐 갔다. 그게 없으면 망치질을 할 수가 없어.'], ['브로크', '되찾아 주면 내 망치를 들고 네 용병단에 들어가지. 장비 손질은 덤이다.']],
    chapters: [
      { province: 'border', type: 'escort', enemy: '산적', title: '룬석 운반로',
        before: [['브로크', '새 룬석을 광산에서 실어 와야 한다. 놈들이 또 노릴 거야.']], after: [['브로크', '한 덩이는 지켰다. 훔쳐 간 것도 되찾아야지.']] },
      { province: 'port', type: 'hunt', enemy: '리자드맨', title: '항구의 장물 창고',
        before: [['브로크', '훔친 룬석이 세렌 항구 창고에 있다더군. 도마뱀 놈들이 지킨다.']], after: [['브로크', '다 찾았다. 이 은혜는 망치로 갚겠다.']] },
    ],
    join: [['브로크', '오늘부터 네 용병단 장비는 내가 손본다. 그리고 앞줄도 내가 선다.']],
  },
  pilgrim: {
    name: '아멜리', title: '맨발의 순례자', trait: 'diligent', look: { skin: '#f5d6b8', hair: '#e3c565', longHair: true },
    intro: [['아멜리', '순례길에 도적이 들끓어 아무도 길을 나서지 못해요.'], ['아멜리', '순례자들을 지켜 주신다면, 이 발로 당신의 용병단과 함께 걷겠습니다.']],
    chapters: [
      { province: 'wheat', type: 'escort', enemy: '산적', title: '밀밭 순례길',
        before: [['아멜리', '순례단이 밀밭을 지나요. 앞뒤를 지켜 주세요.']], after: [['아멜리', '모두 무사합니다. 다음은 숲길이에요.']] },
      { province: 'silverwood', type: 'escort', enemy: '들늑대', title: '숲의 성소',
        before: [['아멜리', '숲속 옛 성소까지가 순례의 끝이에요. 늑대가 많아요.']], after: [['아멜리', '순례는 끝났습니다. 이제 당신과 함께 걷겠어요.']] },
    ],
    join: [['아멜리', '길 위의 사람들을 지키는 것, 그게 제 맹세입니다. 당신의 대원들도요.']],
  },

  // ── 중반 갈림길 1 (추가) ──
  hexer: {
    name: '벨라도나', title: '저주 거래상', trait: 'greedy', look: { skin: '#f5d6b8', hair: '#3a3f6b', longHair: true },
    intro: [['벨라도나', '저주를 팔다 보면 원한도 사지. 경쟁 마녀가 늪에서 내 고객들을 저주하고 있어.'], ['벨라도나', '그 마녀의 표식을 부숴 주면, 내 저주는 앞으로 네 적에게만 걸어 주지.']],
    chapters: [
      { province: 'mist', type: 'magic', title: '늪에 박힌 저주 표식',
        before: [['벨라도나', '표식이 늪 곳곳에 박혀 있어. 건드리면 괴물이 깨어난다.']], after: [['벨라도나', '표식은 부쉈어. 이제 주인을 만나러 가자.']] },
      { province: 'redsand', type: 'magic', title: '황야의 저주 시장',
        before: [['벨라도나', '그 마녀는 붉은 모래 황야의 저주 시장에 숨었어.']], after: [['벨라도나', '거래 끝. 이제 내 저주는 네 편이야.']] },
    ],
    join: [['벨라도나', '좋은 거래였어. 앞으로 네 적의 불운은 전부 내 작품일 거야.']],
  },
  liberator: {
    name: '카토', title: '쇠사슬을 끊은 자', trait: 'brave', look: { skin: '#8d5a3b', hair: '#2b1d14', longHair: false },
    intro: [['카토', '노예 상인들이 아직도 황야에서 사람을 사고판다. 나도 그 쇠사슬에 묶여 있었지.'], ['카토', '갇힌 자들을 풀어 준다면, 이 주먹을 네 용병단을 위해 쓰겠다.']],
    chapters: [
      { province: 'oasis', type: 'escort', enemy: '사막 도적', title: '탈출한 노예들',
        before: [['카토', '도망친 사람들이 오아시스로 향하고 있다. 추격대를 막아야 한다.']], after: [['카토', '모두 살았다. 이제 노예 시장을 부술 차례다.']] },
      { province: 'redsand', type: 'hunt', enemy: '전갈 거인', title: '노예 시장 붕괴',
        before: [['카토', '노예 상인들이 전갈 거인을 경비로 쓴다. 놈부터 쓰러뜨린다.']], after: [['카토', '쇠사슬은 끊어졌다. 이제 내가 갚을 차례다.']] },
    ],
    join: [['카토', '나는 자유롭게 싸운다. 그리고 그 싸움을 네 용병단에 건다.']],
  },
  admiral: {
    name: '마렌', title: '퇴역 제독', trait: 'genius', look: { skin: '#f2c9a0', hair: '#c9c2b8', longHair: false },
    intro: [['마렌', '자유 도시 의회가 나를 퇴역시켰지만, 바다는 아직 날 부르고 있소.'], ['마렌', '연안을 어지럽히는 놈들을 함께 정리해 준다면, 남은 함대 전술을 그대에게 넘기겠소.']],
    chapters: [
      { province: 'port', type: 'defense', enemy: '리자드맨', title: '세렌 부두 방어',
        before: [['마렌', '도마뱀 해적들이 부두를 노리고 있소. 상륙 지점을 막아야 하오.']], after: [['마렌', '부두는 지켰소. 놈들의 기지가 오아시스 쪽에 있소.']] },
      { province: 'oasis', type: 'explore', enemy: '하피', title: '해적 기지 정찰',
        before: [['마렌', '하피가 지키는 해안 절벽 뒤에 기지가 있소. 정찰을 부탁하오.']], after: [['마렌', '기지 위치를 의회에 넘겼소. 이제 그대의 제독이 되겠소.']] },
    ],
    join: [['마렌', '함대는 없어도 전술은 남았소. 그대의 용병단을 함대처럼 움직여 보이겠소.']],
  },
  elfwarden: {
    name: '세레니엘', title: '숲의 수호대장', trait: 'diligent', look: { skin: '#f5d6b8', hair: '#c9c2b8', longHair: true },
    intro: [['세레니엘', '장로회는 인간을 믿지 않아요. 하지만 당신들이 숲을 위해 싸운 것을 봤습니다.'], ['세레니엘', '고대 숲 깊은 곳의 위협을 함께 걷어 낸다면, 순찰대를 이끌고 당신 곁에 서겠어요.']],
    chapters: [
      { province: 'silverwood', type: 'defense', enemy: '거대 거미', title: '순찰로 사수',
        before: [['세레니엘', '거미 떼가 순찰로를 끊었어요. 길을 되찾아야 해요.']], after: [['세레니엘', '길은 열렸어요. 근원은 더 깊은 숲에 있어요.']] },
      { province: 'deepwood', type: 'hunt', enemy: '숲 트롤', title: '고대 숲의 트롤',
        before: [['세레니엘', '트롤들이 고대 숲의 신성한 나무를 베고 있어요.']], after: [['세레니엘', '숲이 당신을 기억할 거예요. 저도요.']] },
    ],
    join: [['세레니엘', '은빛 숲 순찰대는 오늘부터 당신의 용병단과 함께합니다.']],
  },

  // ── 중반 갈림길 2 (추가) ──
  siegemaster: {
    name: '오토', title: '성벽 파괴자', trait: 'genius', look: { skin: '#e0ac7e', hair: '#5a3720', longHair: false },
    intro: [['오토', '내가 설계한 투석기를 시험할 상대가 필요하오. 마침 발렌 외곽에 오크 요새가 있지.'], ['오토', '시험을 도와준다면 내 공성 기술을 전부 그대의 용병단에 바치겠소.']],
    chapters: [
      { province: 'valen', type: 'hunt', enemy: '오크', title: '오크 요새 시험 포격',
        before: [['오토', '투석기를 지켜 주시오. 오크들이 성벽 밖으로 몰려나올 것이오.']], after: [['오토', '명중률 팔 할! 하지만 더 단단한 성벽이 필요하오.']] },
      { province: 'frost', type: 'defense', enemy: '서리 트롤', title: '얼어붙은 성벽',
        before: [['오토', '서리 협곡의 얼음 성벽이야말로 최고의 시험대요. 트롤들이 막아서겠지만.']], after: [['오토', '완벽하오. 이제 어떤 성벽이든 무너뜨릴 수 있소.']] },
    ],
    join: [['오토', '공성 기술자 오토, 그대의 용병단에 합류하오. 성문이 보이면 불러 주시오.']],
  },
  inquisitorlord: {
    name: '발타자르', title: '심문관장', trait: 'diligent', look: { skin: '#f2c9a0', hair: '#2b1d14', longHair: false },
    intro: [['발타자르', '대성당령에 첩자가 숨어 있다. 교단은 용병에게 이 일을 맡기는 것을 수치로 여기지.'], ['발타자르', '그러나 나는 결과만 본다. 첩자를 찾아내면, 심문소의 힘을 그대에게 빌려주겠다.']],
    chapters: [
      { province: 'sanctum', type: 'defense', enemy: '망령', title: '심문소의 망령',
        before: [['발타자르', '첩자가 심문소 지하의 망령을 풀어 놓았다. 증거를 지켜라.']], after: [['발타자르', '증거는 지켰다. 첩자는 늪으로 달아났다.']] },
      { province: 'mist', type: 'hunt', enemy: '리자드맨', title: '늪으로 달아난 첩자',
        before: [['발타자르', '첩자가 리자드맨 부락에 숨었다. 놓치지 마라.']], after: [['발타자르', '자백을 받았다. 그대는 신뢰할 만하다.']] },
    ],
    join: [['발타자르', '심문관장 발타자르, 그대의 용병단에 서겠다. 배신자는 내가 가려낸다.']],
  },
  pirateking: {
    name: '크림슨', title: '붉은 돛의 해적왕', trait: 'greedy', look: { skin: '#c68a5c', hair: '#8c2f2f', longHair: true },
    intro: [['크림슨', '내 보물섬 지도를 하피 놈들이 물고 갔다. 해적왕 체면이 말이 아니지.'], ['크림슨', '지도를 되찾아 주면, 내 선원들과 금고 열쇠를 네 용병단에 맡기지.']],
    chapters: [
      { province: 'oasis', type: 'hunt', enemy: '하피', title: '하피 둥지의 지도',
        before: [['크림슨', '하피 둥지가 해안 절벽에 있다. 지도 조각을 전부 찾아야 해.']], after: [['크림슨', '반쪽은 찾았다. 나머지는 사막 도적 손에 있어.']] },
      { province: 'redsand', type: 'escort', enemy: '사막 도적', title: '보물섬으로 가는 길',
        before: [['크림슨', '도적들한테서 지도를 되찾고, 보물 운반을 지켜 줘.']], after: [['크림슨', '보물은 네 몫도 있다. 해적왕은 의리가 있지.']] },
    ],
    join: [['크림슨', '붉은 돛은 이제 네 깃발 옆에서 펄럭인다. 약탈할 곳만 알려 줘.']],
  },
  frostjarl: {
    name: '비요른', title: '서리 협곡의 영주', trait: 'sturdy', look: { skin: '#f5d6b8', hair: '#e3c565', longHair: true },
    intro: [['비요른', '협곡의 겨울이 길어지고, 설인들이 마을로 내려온다. 내 영지 사람들이 얼어 죽고 있다.'], ['비요른', '겨울을 함께 버텨 준다면, 서리 영주의 도끼를 네 용병단에 걸겠다.']],
    chapters: [
      { province: 'frost', type: 'hunt', enemy: '설인', title: '설인 사냥',
        before: [['비요른', '설인들이 곡물 창고를 노린다. 겨울 식량을 지켜야 한다.']], after: [['비요른', '창고는 지켰다. 하지만 놈들을 몰아낸 건 더 큰 놈이다.']] },
      { province: 'frost', type: 'defense', enemy: '서리 트롤', title: '긴 겨울의 끝',
        before: [['비요른', '서리 트롤 무리가 영지로 내려온다. 여기서 끝낸다.']], after: [['비요른', '봄이 오겠군. 북부는 은혜를 잊지 않는다.']] },
    ],
    join: [['비요른', '서리 영주 비요른, 네 용병단의 방벽이 되겠다. 겨울처럼 무너지지 않는.']],
  },

  // ── 후반 갈림길 (추가) ──
  archmagus: {
    name: '에우리아', title: '마지막 대현자', trait: 'genius', look: { skin: '#f5d6b8', hair: '#ffffff', longHair: true },
    intro: [['에우리아', '마탑이 무너진 뒤로 대현자는 나 하나 남았어요. 그리고 재앙의 기척을 느끼는 것도 나뿐이죠.'], ['에우리아', '고대의 봉인 서고를 지켜 준다면, 내 모든 지식을 당신의 용병단에 쓰겠어요.']],
    chapters: [
      { province: 'deepwood', type: 'magic', enemy: '리치의 망령', title: '봉인 서고의 리치',
        before: [['에우리아', '리치가 서고의 금서를 노려요. 책 한 권이라도 넘어가면 안 돼요.']], after: [['에우리아', '서고는 지켰어요. 마지막 금서는 용의 산맥에 있어요.']] },
      { province: 'dragon', type: 'explore', enemy: '가고일', title: '산맥의 마지막 금서',
        before: [['에우리아', '가고일들이 지키는 고대 도서관이에요. 조심해서 들어가요.']], after: [['에우리아', '이제 별을 떨어뜨리는 주문을 쓸 수 있어요. 재앙에게요.']] },
    ],
    join: [['에우리아', '마지막 대현자 에우리아, 당신의 용병단과 함께 재앙에 맞서겠어요.']],
  },
  lightbearer: {
    name: '루치아', title: '빛을 든 사도', trait: 'lucky', look: { skin: '#f2c9a0', hair: '#e3c565', longHair: true },
    intro: [['루치아', '예언에 따르면 어둠이 오기 전에 빛을 든 자가 용병들과 함께 선다고 해요. 그게 저래요.'], ['루치아', '어둠에 잠식된 땅을 함께 정화해 주세요. 그러면 예언대로 당신 곁에 서겠어요.']],
    chapters: [
      { province: 'mist', type: 'defense', enemy: '망령', title: '어둠에 잠긴 수도원',
        before: [['루치아', '늪 수도원이 망령들에게 잠식됐어요. 빛을 되찾아야 해요.']], after: [['루치아', '수도원에 다시 빛이 들어요. 하지만 어둠은 북쪽에도 있어요.']] },
      { province: 'frost', type: 'magic', enemy: '해골 병사', title: '협곡의 검은 제단',
        before: [['루치아', '협곡에 검은 제단이 세워졌어요. 해골 병사들이 지키고 있어요.']], after: [['루치아', '예언은 이루어졌어요. 이제 당신의 빛이 될게요.']] },
    ],
    join: [['루치아', '빛의 사도 루치아, 당신의 대원들 곁에서 새벽을 가져오겠어요.']],
  },
  shadowqueen: {
    name: '니클라', title: '그림자 길드의 여왕', trait: 'greedy', look: { skin: '#e0ac7e', hair: '#1b1420', longHair: true },
    intro: [['니클라', '그림자 길드 안에 반역자가 생겼어. 여왕으로서 체면이 안 서지.'], ['니클라', '반역자를 처리해 주면, 대륙 모든 그림자가 네 용병단을 위해 움직일 거야.']],
    chapters: [
      { province: 'port', type: 'defense', enemy: '산적', title: '여왕의 은신처',
        before: [['니클라', '반역자들이 내 은신처를 덮친대. 손님 대접을 해 줘.']], after: [['니클라', '훌륭해. 이제 반역자 두목 차례야.']] },
      { province: 'oasis', type: 'hunt', enemy: '사막 도적', title: '반역자의 최후',
        before: [['니클라', '두목은 사막 도적들 사이에 숨었어. 조용히 끝내.']], after: [['니클라', '그림자는 이제 네 편이야. 여왕의 약속이지.']] },
    ],
    join: [['니클라', '밤의 여왕 니클라, 네 용병단에 그림자를 드리우지. 적들은 잠들지 못할 거야.']],
  },
  titan: {
    name: '우르그', title: '거인의 피', trait: 'brave', look: { skin: '#c68a5c', hair: '#5a3720', longHair: true },
    intro: [['우르그', '거인의 피를 이은 부족은 이제 나 하나다. 용의 산맥에 조상의 무덤이 있지.'], ['우르그', '무덤을 지키는 것을 도와주면, 거인의 힘을 네 용병단에 빌려주겠다.']],
    chapters: [
      { province: 'redsand', type: 'hunt', enemy: '전갈 거인', title: '조상의 길',
        before: [['우르그', '무덤으로 가는 길목을 전갈 거인이 막았다. 힘으로 연다.']], after: [['우르그', '길은 열렸다. 무덤은 와이번 소굴 옆이다.']] },
      { province: 'dragon', type: 'defense', enemy: '와이번', title: '거인의 무덤',
        before: [['우르그', '와이번들이 조상의 뼈를 노린다. 무덤을 지킨다.']], after: [['우르그', '조상들이 편히 잠든다. 이제 네 전쟁을 돕겠다.']] },
    ],
    join: [['우르그', '거인의 피 우르그, 네 용병단의 맨 앞에 선다. 전열은 내가 부순다.']],
  },
};
