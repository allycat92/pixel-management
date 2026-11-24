// 게임 데이터 정의: 직업, 특성, 의뢰, 시설, 랭크 등
'use strict';

const CLASSES = {
  warrior: {
    name: '전사', desc: '튼튼한 근접 전투 요원. 토벌과 호위에 강하다.',
    base: { str: 8, dex: 4, int: 2, hp: 32 },
    growth: { str: 2.2, dex: 1.0, int: 0.3, hp: 6 },
    outfit: '#9c3b2e', accent: '#d9a441', headgear: 'helmet', weapon: 'sword',
  },
  archer: {
    name: '궁수', desc: '날렵한 원거리 사수. 탐사와 토벌 모두 무난하다.',
    base: { str: 5, dex: 8, int: 3, hp: 24 },
    growth: { str: 1.2, dex: 2.2, int: 0.6, hp: 4 },
    outfit: '#3f7a3a', accent: '#a7d26a', headgear: 'band', weapon: 'bow',
  },
  mage: {
    name: '마법사', desc: '강력한 마법을 다룬다. 마법 조사 의뢰의 핵심.',
    base: { str: 2, dex: 4, int: 9, hp: 18 },
    growth: { str: 0.3, dex: 0.9, int: 2.6, hp: 3 },
    outfit: '#3d4a9c', accent: '#f2d24b', headgear: 'hat', weapon: 'staff',
  },
  cleric: {
    name: '성직자', desc: '파티원의 부상과 사망 위험을 크게 줄여준다.',
    base: { str: 4, dex: 3, int: 7, hp: 26 },
    growth: { str: 0.9, dex: 0.7, int: 1.9, hp: 5 },
    outfit: '#e8e4d8', accent: '#d9a441', headgear: 'none', weapon: 'mace',
  },
  rogue: {
    name: '도적', desc: '재빠르고 손버릇이 나쁘다. 의뢰 보상 금화가 늘어난다.',
    base: { str: 5, dex: 9, int: 4, hp: 22 },
    growth: { str: 1.0, dex: 2.3, int: 1.0, hp: 4 },
    outfit: '#3b3346', accent: '#8f2d4a', headgear: 'hood', weapon: 'dagger',
  },
};

const TRAITS = {
  brave:    { name: '용맹', desc: '전투력 +10%' },
  coward:   { name: '겁쟁이', desc: '전투력 -10%, 부상 확률 절반' },
  sturdy:   { name: '강골', desc: '부상 확률 절반, 회복 빠름' },
  lucky:    { name: '행운아', desc: '파티 성공률 +5%' },
  greedy:   { name: '탐욕', desc: '주급 +30%, 보상 금화 +10%' },
  genius:   { name: '천재', desc: '획득 경험치 +50%' },
  lazy:     { name: '게으름', desc: '훈련장 경험치 절반' },
  diligent: { name: '성실', desc: '주급 -20%' },
  none:     { name: '평범', desc: '특별한 점은 없다' },
  // 특별 용병 전용 특성
  hawkeye:   { name: '매의 눈', desc: '파티 성공률 +8%', unique: true },
  saint:     { name: '성녀의 가호', desc: '파티 사망 위험 없음, 부상 확률 -30%', unique: true },
  shadow:    { name: '그림자 걸음', desc: '보상 금화 +25%', unique: true },
  berserker: { name: '광전사', desc: '전투력 +25%', unique: true },
  arcane:    { name: '마탑의 유산', desc: '전투력 +10%, 마법 조사에서 추가 +25%', unique: true },
  captain:   { name: '선장의 호령', desc: '파티 사기 하락 없음, 보상 금화 +15%', unique: true },
  commander: { name: '지휘', desc: '파티 전원 전투력 +8%', unique: true },
  // 세력 정예 용병 특성
  royalguard:  { name: '왕실 근위', desc: '방어·방어전·결전에서 전투력 +20%', unique: true },
  northknight: { name: '북부 기사도', desc: '전투력 +5%, 부상 확률 절반', unique: true },
  broker:      { name: '계약 전문가', desc: '보상 금화 +10%', unique: true },
  blessed:     { name: '성광의 축복', desc: '파티 사망 위험 -50%', unique: true },
  sylvan:      { name: '숲의 사수', desc: '파티 성공률 +5%', unique: true },
  warcry:      { name: '전쟁 함성', desc: '전투력 +15%', unique: true },
};
const TRAIT_POOL = ['brave', 'coward', 'sturdy', 'lucky', 'greedy', 'genius', 'lazy', 'diligent', 'none', 'none'];

const NAMES = [
  '레온', '아리아', '카엘', '세릴', '브란', '미라', '토린', '엘리스', '가렌', '루나',
  '하른', '실비아', '드레이크', '이벨', '오스카', '리안', '페이', '볼드', '니아', '케인',
  '로웬', '에단', '시엘', '마르타', '그림', '벨라', '다리우스', '테오', '일레인', '자크',
  '카라', '울프', '셀레네', '바르크', '에린', '모건', '노아', '헬가', '키릴', '아델',
];

const SKIN_TONES = ['#f2c9a0', '#e0ac7e', '#c68a5c', '#8d5a3b', '#f5d6b8'];
const HAIR_COLORS = ['#2b1d14', '#5a3720', '#a8642a', '#e3c565', '#c9c2b8', '#8c2f2f', '#3a3f6b'];

// 의뢰 유형: 스탯 가중치가 다르다
const QUEST_TYPES = {
  hunt: {
    cat: 'monster', name: '토벌', icon: 'sword', weights: { str: 1.3, dex: 0.8, int: 0.6, hp: 0.12 },
    titles: ['{e} 토벌', '{e} 소굴 소탕', '{e} 무리 퇴치', '날뛰는 {e} 처치'],
  },
  escort: {
    cat: 'monster', name: '호위', icon: 'shield', weights: { str: 1.0, dex: 0.9, int: 0.6, hp: 0.2 },
    titles: ['{p}까지 상단 호위', '{p}행 순례자 호위', '귀족 마차 호위 ({p})', '{p} 보급품 수송 호위'],
  },
  explore: {
    cat: 'monster', name: '탐사', icon: 'map', weights: { str: 0.5, dex: 1.3, int: 1.0, hp: 0.08 },
    titles: ['{p} 지도 작성', '{p} 실종자 수색', '{p}의 유적 탐사', '{p} 정찰 임무'],
  },
  magic: {
    cat: 'monster', name: '마법 조사', icon: 'orb', weights: { str: 0.3, dex: 0.6, int: 1.5, hp: 0.06 },
    titles: ['{p}의 저주 해제', '{p} 마력 이상 조사', '{p} 봉인 강화', '{p}의 유령 퇴마'],
  },
  defense: {
    cat: 'monster', name: '방어', icon: 'shield', weights: { str: 1.1, dex: 0.6, int: 0.7, hp: 0.3 },
    titles: ['{p} 방어전', '{e}의 습격 저지', '{p} 성벽 수비', '{p} 피난민 보호'],
  },
  // ── 세력 분쟁 의뢰: {t} 대상 세력, {i} 의뢰 세력, {p} 장소 ──
  raid: {
    cat: 'conflict', name: '습격', icon: 'sword', weights: { str: 1.2, dex: 1.0, int: 0.5, hp: 0.15 },
    titles: ['{t}의 보급대 습격', '{p}의 {t} 군량고 기습', '{t} 정찰대 섬멸', '{p} 인근 {t} 야영지 기습'],
  },
  siege: {
    cat: 'conflict', name: '거점 공략', icon: 'shield', weights: { str: 1.2, dex: 0.6, int: 0.8, hp: 0.25 },
    titles: ['{p} 요새 공략', '{t}의 {p} 거점 탈환', '{p} 성채 공성전'],
  },
  sabotage: {
    cat: 'conflict', name: '공작', icon: 'map', weights: { str: 0.4, dex: 1.4, int: 1.1, hp: 0.05 },
    titles: ['{t} 군수 창고 방화', '{p}의 {t} 밀서 탈취', '{t} 지휘관 동선 정탐', '{p}에 거짓 소문 퍼뜨리기'],
  },
  rescue: {
    cat: 'conflict', name: '구출', icon: 'heart', weights: { str: 0.8, dex: 1.2, int: 0.8, hp: 0.12 },
    titles: ['{t}에 잡힌 포로 구출', '{p} 감옥 습격', '{t} 진영의 인질 구출'],
  },
  warDefense: {
    cat: 'conflict', name: '방어전', icon: 'shield', weights: { str: 1.1, dex: 0.6, int: 0.7, hp: 0.3 },
    titles: ['{t}의 침공으로부터 {p} 방어', '{p} 성벽 수비 ({t} 공세)', '{p} 피난민 호송 ({t} 추격)'],
  },
  counterspy: {
    cat: 'conflict', name: '방첩', icon: 'map', weights: { str: 0.6, dex: 1.1, int: 1.2, hp: 0.08 },
    titles: ['{p}에 잠입한 {t} 첩자 색출', '{t} 밀정 체포', '{p}의 {t} 선동꾼 추적'],
  },
  envoy: {
    cat: 'diplomacy', name: '사절 호위', icon: 'star', weights: { str: 0.9, dex: 0.9, int: 1.0, hp: 0.15 },
    titles: ['{t}와(과)의 강화 사절 호위', '{p} 회담장 경호', '{t}행 밀사 호위'],
  },
  battle: {
    cat: 'campaign', name: '결전', icon: 'sword', weights: { str: 1.1, dex: 0.8, int: 0.8, hp: 0.2 },
    titles: ['{p} 회전', '{p} 결전', '{p} 공방전'],
  },
};

const FACILITIES = {
  dorm:      { name: '숙소', max: 5, baseCost: 120, desc: (l) => `길드 소속 단원 최대 ${6 + l * 3}명` },
  barracks:  { name: '병영', max: 4, baseCost: 220, desc: (l) => `직속 용병단 최대 ${1 + l}개, 용병단당 대장 1 + 대원 ${4 + l}명` },
  training:  { name: '훈련장', max: 5, baseCost: 150, desc: (l) => l ? `대기 단원 매일 경험치 +${l * 5}` : '아직 없음 (대기 단원 성장 불가)' },
  infirmary: { name: '의무실', max: 5, baseCost: 130, desc: (l) => `부상 회복 속도 ${100 + l * 50}%` },
  tavern:    { name: '모집소', max: 5, baseCost: 140, desc: (l) => `숙련병 레벨 +${l}, 용병단 시장 ${2 + Math.floor(l / 2)}곳` },
  board:     { name: '정보망', max: 5, baseCost: 160, desc: (l) => `게시 의뢰 최대 ${4 + l}개, 보상 +${l * 8}%` },
  forge:     { name: '대장간', max: 5, baseCost: 200, desc: (l) => l ? `상점 물품 최대 등급 +${l >= 3 ? 1 : 0}, 진열 ${4 + l}개, 가격 -${l * 4}%` : '상점 진열 4개' },
};

const RANKS = [
  { name: 'F', rep: 0 },
  { name: 'E', rep: 80 },
  { name: 'D', rep: 260 },
  { name: 'C', rep: 600 },
  { name: 'B', rep: 1100 },
  { name: 'A', rep: 1900 },
  { name: 'S', rep: 3200 },
];

const RANDOM_EVENTS = [
  {
    text: '떠돌이 상인이 잡동사니를 비싸게 사 갔습니다.',
    run: (g) => { const v = 20 + g.rankIndex() * 15; g.state.gold += v; return `금화 +${v}`; },
  },
  {
    text: '익명의 후원자가 길드에 기부금을 보냈습니다.',
    run: (g) => { const v = 40 + g.rankIndex() * 25; g.state.gold += v; return `금화 +${v}`; },
  },
  {
    text: '음유시인이 길드 용병단들의 무용담을 노래로 퍼뜨렸습니다.',
    run: (g) => { const v = 5 + g.rankIndex() * 4; g.state.rep += v; return `명성 +${v}`; },
  },
  {
    text: '주점에서 난투극이 벌어졌습니다!',
    run: (g) => {
      const idle = g.state.mercs.filter((m) => m.status === 'idle');
      if (!idle.length) return '다행히 단원은 없었습니다.';
      const m = idle[Math.floor(Math.random() * idle.length)];
      m.status = 'injured'; m.injury = 2;
      const fine = 15; g.state.gold -= fine;
      return `${m.name} 부상(2일), 배상금 -${fine}`;
    },
  },
  {
    text: '단원들끼리 대련을 하며 실력을 갈고닦았습니다.',
    run: (g) => {
      const idle = g.state.mercs.filter((m) => m.status === 'idle');
      if (!idle.length) return '하지만 대련할 단원이 없었습니다.';
      const m = idle[Math.floor(Math.random() * idle.length)];
      const lv = g.gainExp(m, 25);
      return `${m.name} 경험치 +25${lv ? ' (레벨 업!)' : ''}`;
    },
  },
  {
    text: '단원 둘이 사소한 일로 크게 말다툼을 벌였습니다.',
    run: (g) => {
      const idle = g.state.mercs.filter((m) => m.status !== 'quest');
      if (idle.length < 2) return '다행히 금방 화해했습니다.';
      const [a, b] = idle.sort(() => Math.random() - 0.5);
      g.addRel(a, b, -15); g.changeMorale(a, -5); g.changeMorale(b, -5);
      return `${a.name}·${b.name} 관계 악화`;
    },
  },
  {
    text: '단원 둘이 밤새 술잔을 기울이며 속 얘기를 나눴습니다.',
    run: (g) => {
      const idle = g.state.mercs.filter((m) => m.status !== 'quest');
      if (idle.length < 2) return '하지만 술친구가 없었습니다.';
      const [a, b] = idle.sort(() => Math.random() - 0.5);
      g.addRel(a, b, 12); g.changeMorale(a, 4); g.changeMorale(b, 4);
      return `${a.name}·${b.name} 관계 개선`;
    },
  },
];

// ───────── 용병 유닛: 직업 계통 (기본 → 상급 → 최상급) ─────────
// 용병 유닛은 개인 능력치에 편차가 없다. 같은 직업·같은 레벨이면 능력치가 같고,
// 어떤 직업으로 전직시키느냐(와 장비)로 용병단 안에서의 역할을 정한다.
// fx: self.all(본인 전투력 +), self.types(의뢰 유형별 본인 전투력 +),
//     party: success(+), injury(×), death(×), gold(+), great(×), greatGold(+), days(+), noDisaster, healHalf, loot, noMoraleLoss
const CLASS_SKILLS = {
  warrior: { name: '방패막이', desc: '파티 부상 확률 -15%', fx: { party: { injury: 0.85 } } },
  archer:  { name: '정찰', desc: '파티 성공률 +4%', fx: { party: { success: 0.04 } } },
  mage:    { name: '마력 해석', desc: '마법 조사에서 본인 전투력 +20%', fx: { self: { types: { magic: 0.2 } } } },
  cleric:  { name: '치유', desc: '파티 부상 확률 -50%, 사망 위험 -65%', fx: { party: { injury: 0.5, death: 0.35 } } },
  rogue:   { name: '약탈', desc: '보상 금화 +12%', fx: { party: { gold: 0.12 } } },
};

// 단계별 레벨 상한: 상한에 닿으면 전직해야 더 성장한다
const UNIT_TIERS = [
  { name: '기본', cap: 10 },
  { name: '상급', cap: 20, at: 10, cost: 350 },
  { name: '최상급', cap: 30, at: 20, cost: 900 },
];
const PROMOTE_LEVEL = UNIT_TIERS[1].at;
const PROMOTE_COST = UNIT_TIERS[1].cost;
const MASTER_LEVEL = UNIT_TIERS[2].at;
const MASTER_COST = UNIT_TIERS[2].cost;

// 직업마다 두 갈래 상급 직업, 그 끝에 최상급 직업 하나씩.
// bonus: 전직 즉시 능력치, growth: 레벨업 성장 추가
const PROMOTIONS = {
  warrior: [
    { key: 'paladin', name: '성기사', skill: '수호의 맹세', desc: '파티 부상 확률 -30%, 사망 위험 -50%',
      bonus: { maxHp: 20, str: 2, int: 3 }, growth: { hp: 2, int: 0.6 }, outfit: '#c9ced6', accent: '#d9a441',
      fx: { party: { injury: 0.7, death: 0.5 } } },
    { key: 'swordmaster', name: '검성', skill: '일섬', desc: '토벌·방어 의뢰에서 본인 전투력 +30%',
      bonus: { str: 6, dex: 3 }, growth: { str: 0.8, dex: 0.5 }, outfit: '#5a2430', accent: '#e8e4d8',
      fx: { self: { types: { hunt: 0.3, defense: 0.3 } } } },
  ],
  archer: [
    { key: 'ranger', name: '레인저', skill: '길잡이', desc: '탐사·호위에서 본인 전투력 +25%, 파티 이동 -1일',
      bonus: { dex: 4, maxHp: 8 }, growth: { dex: 0.5, hp: 1 }, outfit: '#2f5a2a', accent: '#d9a441',
      fx: { self: { types: { explore: 0.25, escort: 0.25 } }, party: { days: -1 } } },
    { key: 'sniper', name: '저격수', skill: '급소 사격', desc: '파티 대성공 확률 2배',
      bonus: { dex: 7 }, growth: { dex: 0.8 }, outfit: '#4a4a5a', accent: '#d6455d',
      fx: { party: { great: 2 } } },
  ],
  mage: [
    { key: 'elementalist', name: '원소술사', skill: '원소 폭풍', desc: '토벌·마법 조사에서 본인 전투력 +30%',
      bonus: { int: 7 }, growth: { int: 0.8 }, outfit: '#9c3b2e', accent: '#f39c12',
      fx: { self: { types: { hunt: 0.3, magic: 0.3 } } } },
    { key: 'warder', name: '결계술사', skill: '방어 결계', desc: '파티의 대실패를 실패로 막고, 부상 확률 -20%',
      bonus: { int: 4, maxHp: 10 }, growth: { int: 0.4, hp: 1.5 }, outfit: '#2e6b7a', accent: '#7fd6e8',
      fx: { party: { noDisaster: true, injury: 0.8 } } },
  ],
  cleric: [
    { key: 'highpriest', name: '대사제', skill: '부활의 기도', desc: '파티 사망 위험 없음, 귀환 시 부상 기간 절반',
      bonus: { int: 5, maxHp: 8 }, growth: { int: 0.6, hp: 1 }, outfit: '#f2ecd8', accent: '#7fd6e8',
      fx: { party: { death: 0, healHalf: true } } },
    { key: 'battlepriest', name: '전투사제', skill: '신성 강타', desc: '본인 전투력 +20% (치유 효과는 유지)',
      bonus: { str: 5, maxHp: 10 }, growth: { str: 0.9, hp: 1 }, outfit: '#a88a4a', accent: '#f2ecd8',
      fx: { self: { all: 0.2 } } },
  ],
  rogue: [
    { key: 'assassin', name: '암살자', skill: '암살', desc: '토벌에서 본인 전투력 +30%, 대성공 시 보상 +30%',
      bonus: { dex: 5, str: 3 }, growth: { dex: 0.6, str: 0.4 }, outfit: '#1f1a28', accent: '#d6455d',
      fx: { self: { types: { hunt: 0.3 } }, party: { greatGold: 0.3 } } },
    { key: 'thief', name: '대도', skill: '보물 사냥', desc: '보상 금화 +25%, 성공 시 25% 확률로 장비 획득',
      bonus: { dex: 4, int: 3 }, growth: { dex: 0.5, int: 0.4 }, outfit: '#5a4a2a', accent: '#f2c94c',
      fx: { party: { gold: 0.25, loot: 0.25 } } },
  ],
};
const ADV_CLASSES = {};
Object.entries(PROMOTIONS).forEach(([cls, list]) => list.forEach((p) => { ADV_CLASSES[p.key] = { ...p, base: cls }; }));

// 최상급 직업: 상급 직업 하나에 하나씩 (Lv.20)
const MASTERS = {
  paladin: { key: 'guardian', name: '수호기사', skill: '불굴의 성벽', desc: '파티 부상 확률 -40%, 사망 위험 -60%, 방어·호위·방어전에서 본인 전투력 +30%',
    bonus: { maxHp: 30, str: 4, int: 3 }, growth: { hp: 2.5, str: 0.4 }, outfit: '#e8eef2', accent: '#f2c94c',
    fx: { party: { injury: 0.6, death: 0.4 }, self: { types: { defense: 0.3, escort: 0.3, warDefense: 0.3 } } } },
  swordmaster: { key: 'swordsaint', name: '검신', skill: '천검', desc: '모든 의뢰에서 본인 전투력 +35%',
    bonus: { str: 9, dex: 5 }, growth: { str: 1.0, dex: 0.5 }, outfit: '#2a0e18', accent: '#f2c94c',
    fx: { self: { all: 0.35 } } },
  ranger: { key: 'pathfinder', name: '대륙 순찰자', skill: '질풍 행군', desc: '탐사·호위·구출에서 본인 전투력 +35%, 파티 이동 -1일',
    bonus: { dex: 6, maxHp: 14 }, growth: { dex: 0.7, hp: 1.5 }, outfit: '#1f4a2a', accent: '#e8e4d8',
    fx: { self: { types: { explore: 0.35, escort: 0.35, rescue: 0.35 } }, party: { days: -1 } } },
  sniper: { key: 'skyarcher', name: '천궁', skill: '천리안', desc: '파티 대성공 확률 ×1.5, 성공률 +5%',
    bonus: { dex: 10 }, growth: { dex: 1.0 }, outfit: '#2a2a3a', accent: '#f2c94c',
    fx: { party: { great: 1.5, success: 0.05 } } },
  elementalist: { key: 'archmage', name: '대마도사', skill: '메테오', desc: '토벌·마법 조사·공성·결전에서 본인 전투력 +40%',
    bonus: { int: 10, maxHp: 6 }, growth: { int: 1.0 }, outfit: '#5a1414', accent: '#f2c94c',
    fx: { self: { types: { hunt: 0.4, magic: 0.4, siege: 0.4, battle: 0.4 } } } },
  warder: { key: 'sealmaster', name: '봉인술사', skill: '절대 결계', desc: '대실패 방지, 파티 부상 확률 -35%, 사망 위험 -40%',
    bonus: { int: 6, maxHp: 16 }, growth: { int: 0.6, hp: 2 }, outfit: '#14404a', accent: '#a7e8f4',
    fx: { party: { noDisaster: true, injury: 0.65, death: 0.6 } } },
  highpriest: { key: 'saint', name: '성자', skill: '기적', desc: '파티 사망 위험 없음, 부상 기간 절반, 부상 확률 -25%',
    bonus: { int: 7, maxHp: 14 }, growth: { int: 0.8, hp: 1.5 }, outfit: '#ffffff', accent: '#f2c94c',
    fx: { party: { death: 0, healHalf: true, injury: 0.75 } } },
  battlepriest: { key: 'inquisitor', name: '심판관', skill: '심판의 철퇴', desc: '본인 전투력 +30%, 방첩에서 추가 +30%',
    bonus: { str: 7, maxHp: 16 }, growth: { str: 1.0, hp: 1.5 }, outfit: '#6a4a1a', accent: '#ffffff',
    fx: { self: { all: 0.3, types: { counterspy: 0.3 } } } },
  assassin: { key: 'nightblade', name: '무영', skill: '그림자 처형', desc: '토벌·습격·공작에서 본인 전투력 +40%',
    bonus: { dex: 8, str: 5 }, growth: { dex: 0.8, str: 0.5 }, outfit: '#0e0a14', accent: '#8f2d4a',
    fx: { self: { types: { hunt: 0.4, raid: 0.4, sabotage: 0.4 } } } },
  thief: { key: 'phantom', name: '괴도', skill: '황금 손', desc: '보상 금화 +35%, 성공 시 40% 확률로 장비 획득',
    bonus: { dex: 6, int: 5 }, growth: { dex: 0.6, int: 0.5 }, outfit: '#3a2a4a', accent: '#f2c94c',
    fx: { party: { gold: 0.35, loot: 0.4 } } },
};
const MASTER_CLASSES = {};
Object.entries(MASTERS).forEach(([adv, m]) => { MASTER_CLASSES[m.key] = { ...m, from: adv, base: ADV_CLASSES[adv].base }; });

// ───────── 용병대장: 고유 직업 ─────────
// 대장마다 하나뿐인 고유 직업을 갖고 등장한다. 성장률이 높고 레벨 상한이 높으며,
// 지휘 스킬(lead)로 자기 용병단 전체를 끌어올린다.
// style: 전투에서의 싸움 방식(기본 직업), lead: power(용병단 전투력 +), types(의뢰 유형별 +),
//        cls(해당 기본 직업 대원 전투력 +), party(파티 효과)
const CAPTAIN_CAP = 40;
const CAPTAIN_AWAKEN = 20; // 이 레벨부터 지휘 효과 1.5배
const CAPTAIN_CLASSES = {
  blademaster: { name: '검귀', style: 'warrior', desc: '전장을 베어 가르는 검의 귀신. 앞장서서 대원들의 투지를 끌어올린다.',
    base: { str: 12, dex: 7, int: 3, hp: 44 }, growth: { str: 3.6, dex: 1.8, int: 0.5, hp: 9 },
    outfit: '#3a1018', accent: '#e8e4d8', headgear: 'band', weapon: 'sword',
    lead: { name: '선봉의 검', desc: '용병단 전투력 +6%, 전사 계열 대원 +12%', power: 0.06, cls: { warrior: 0.12 } } },
  warlord: { name: '전쟁군주', style: 'warrior', desc: '수많은 전쟁을 치른 지휘관. 세력 분쟁과 결전에서 진가를 발휘한다.',
    base: { str: 11, dex: 5, int: 5, hp: 48 }, growth: { str: 3.2, dex: 1.2, int: 1.2, hp: 10 },
    outfit: '#5a3a1a', accent: '#d6455d', headgear: 'helmet', weapon: 'sword',
    lead: { name: '군세 통솔', desc: '습격·공성·방어전·결전에서 용병단 전투력 +15%', power: 0.03, types: { raid: 0.15, siege: 0.15, warDefense: 0.15, battle: 0.15 } } },
  ironwall: { name: '철벽 수호자', style: 'warrior', desc: '한 번도 진형을 무너뜨린 적 없는 방패. 대원들을 살려서 돌아온다.',
    base: { str: 10, dex: 4, int: 4, hp: 56 }, growth: { str: 2.8, dex: 1.0, int: 1.0, hp: 12 },
    outfit: '#4a5a6a', accent: '#d9a441', headgear: 'helmet', weapon: 'mace',
    lead: { name: '방진', desc: '파티 부상 확률 -35%, 사망 위험 -50%, 방어·호위 +12%', power: 0.03, types: { defense: 0.12, escort: 0.12, warDefense: 0.12 }, party: { injury: 0.65, death: 0.5 } } },
  windhunter: { name: '바람 사냥꾼', style: 'archer', desc: '바람을 읽고 사냥감을 쫓는 명사수. 궁수들을 이끄는 데 능하다.',
    base: { str: 6, dex: 12, int: 5, hp: 34 }, growth: { str: 1.6, dex: 3.6, int: 1.0, hp: 7 },
    outfit: '#2a4a3a', accent: '#a7d26a', headgear: 'band', weapon: 'bow',
    lead: { name: '사냥 신호', desc: '궁수 계열 대원 +15%, 파티 성공률 +4%, 이동 -1일', power: 0.03, cls: { archer: 0.15 }, party: { success: 0.04, days: -1 } } },
  spellblade: { name: '마검사', style: 'mage', desc: '검과 마법을 함께 다루는 이단의 기사. 마법사들의 힘을 한데 모은다.',
    base: { str: 8, dex: 6, int: 11, hp: 36 }, growth: { str: 1.8, dex: 1.2, int: 3.6, hp: 7 },
    outfit: '#2a2a6a', accent: '#7fd6e8', headgear: 'none', weapon: 'staff',
    lead: { name: '마력 공명', desc: '마법사 계열 대원 +15%, 마법 조사 +20%', power: 0.04, cls: { mage: 0.15 }, types: { magic: 0.2 } } },
  saintknight: { name: '성광 기사', style: 'cleric', desc: '빛의 맹세를 지키는 기사. 그가 있는 한 아무도 버려지지 않는다.',
    base: { str: 8, dex: 4, int: 9, hp: 46 }, growth: { str: 2.0, dex: 1.0, int: 2.8, hp: 10 },
    outfit: '#e8e4d8', accent: '#f2c94c', headgear: 'helmet', weapon: 'mace',
    lead: { name: '빛의 가호', desc: '파티 사망 위험 -70%, 부상 확률 -25%, 성직자 계열 대원 +10%', power: 0.03, cls: { cleric: 0.1 }, party: { death: 0.3, injury: 0.75 } } },
  shadowlord: { name: '그림자 두목', style: 'rogue', desc: '뒷골목을 주름잡던 두목. 돈 냄새를 맡고, 어둠 속 일을 처리한다.',
    base: { str: 7, dex: 12, int: 6, hp: 32 }, growth: { str: 1.6, dex: 3.6, int: 1.4, hp: 6 },
    outfit: '#1a1420', accent: '#d9a441', headgear: 'hood', weapon: 'dagger',
    lead: { name: '밤의 계약', desc: '보상 금화 +18%, 공작·구출·방첩 +20%, 도적 계열 대원 +12%', power: 0.03, cls: { rogue: 0.12 }, types: { sabotage: 0.2, rescue: 0.2, counterspy: 0.2 }, party: { gold: 0.18 } } },
  tactician: { name: '전술가', style: 'mage', desc: '판을 읽는 눈을 가진 지휘관. 개인의 무용보다 용병단 전체를 움직인다.',
    base: { str: 5, dex: 7, int: 12, hp: 34 }, growth: { str: 1.2, dex: 1.6, int: 3.6, hp: 7 },
    outfit: '#3a3a4a', accent: '#f2c94c', headgear: 'hat', weapon: 'staff',
    lead: { name: '전술 지휘', desc: '용병단 전투력 +10%, 파티 성공률 +5%, 대성공 확률 ×1.4', power: 0.1, party: { success: 0.05, great: 1.4 } } },

  // 중·후반 영입 대장
  khan: { name: '초원의 칸', style: 'archer', desc: '말 위에서 태어난 유목 군주. 빠르게 치고 빠지는 전쟁을 안다.',
    base: { str: 9, dex: 11, int: 4, hp: 42 }, growth: { str: 2.4, dex: 3.2, int: 0.8, hp: 9 },
    outfit: '#8a5a2a', accent: '#e8c86a', headgear: 'band', weapon: 'bow',
    lead: { name: '기마 돌격', desc: '습격·결전 +15%, 궁수·전사 계열 대원 +8%, 이동 -1일', power: 0.04, types: { raid: 0.15, battle: 0.15 }, cls: { archer: 0.08, warrior: 0.08 }, party: { days: -1 } } },
  dragonslayer: { name: '용살자', style: 'warrior', desc: '고룡의 비늘을 꿰뚫은 전설의 전사. 재앙 앞에서 물러선 적이 없다.',
    base: { str: 15, dex: 7, int: 4, hp: 60 }, growth: { str: 4.0, dex: 1.6, int: 0.8, hp: 12 },
    outfit: '#6a1a14', accent: '#f39c12', headgear: 'helmet', weapon: 'sword',
    lead: { name: '용의 목을 벤 자', desc: '용병단 전투력 +8%, 토벌 +15%, 재앙 세력·재앙급 괴물 상대 +25%', power: 0.08, types: { hunt: 0.15 }, vsCalamity: 0.25 } },
  demonhunter: { name: '마귀 사냥꾼', style: 'cleric', desc: '마계의 문 너머까지 다녀왔다는 퇴마사. 죽음의 냄새를 맡는다.',
    base: { str: 10, dex: 9, int: 12, hp: 50 }, growth: { str: 2.4, dex: 2.0, int: 3.4, hp: 10 },
    outfit: '#2a2a3a', accent: '#c9c2b8', headgear: 'hood', weapon: 'mace',
    lead: { name: '퇴마의 인장', desc: '용병단 전투력 +6%, 사망 위험 -60%, 방첩 +20%, 재앙 세력·재앙급 괴물 상대 +20%', power: 0.06, types: { counterspy: 0.2 }, vsCalamity: 0.2, party: { death: 0.4 } } },
};

// ───────── 특별 용병: 고유 직업을 가진 대원 ─────────
// 대원처럼 아무 용병단에나 들어가지만 전직 대신 '이야기'로 성장한다.
// 장(章)을 마칠수록 레벨 상한·성장률·고유 스킬이 강해져, 끝까지 가면 대장 못지않다.
const HERO_CAPS = [15, 22, 30, 40];           // 완료한 장 수별 레벨 상한
const HERO_GROWTH = [0.62, 0.75, 0.88, 1.0];  // 완료한 장 수별 성장률 배율
const HERO_CLASSES = {
  silverscout: { name: '은빛 순찰자', style: 'archer', skill: '숲의 눈', desc: '토벌·탐사·호위에서 본인 전투력 +20%, 파티 성공률 +4%',
    base: { str: 6, dex: 13, int: 6, hp: 34 }, growth: { str: 1.6, dex: 3.8, int: 1.2, hp: 7 },
    outfit: '#2f6a4a', accent: '#e8e4d8', headgear: 'band', weapon: 'bow',
    fx: { self: { types: { hunt: 0.2, explore: 0.2, escort: 0.2 } }, party: { success: 0.04 } } },
  exsaint: { name: '파문 성녀', style: 'cleric', skill: '들판의 미사', desc: '파티 부상 확률 -40%, 사망 위험 -50%',
    base: { str: 5, dex: 5, int: 13, hp: 40 }, growth: { str: 1.0, dex: 1.2, int: 3.8, hp: 9 },
    outfit: '#f2ecd8', accent: '#d6455d', headgear: 'none', weapon: 'mace',
    fx: { party: { injury: 0.6, death: 0.5 } } },
  outlaw: { name: '가면 의적', style: 'rogue', skill: '의적의 신호', desc: '보상 금화 +15%, 구출·공작에서 본인 전투력 +25%',
    base: { str: 7, dex: 13, int: 7, hp: 32 }, growth: { str: 1.6, dex: 3.8, int: 1.6, hp: 6 },
    outfit: '#2a1a3a', accent: '#e8e4d8', headgear: 'hood', weapon: 'dagger',
    fx: { self: { types: { rescue: 0.25, sabotage: 0.25 } }, party: { gold: 0.15 } } },
  pitchampion: { name: '투기장 패왕', style: 'warrior', skill: '투기장의 함성', desc: '모든 의뢰에서 본인 전투력 +15%',
    base: { str: 14, dex: 6, int: 2, hp: 50 }, growth: { str: 4.0, dex: 1.4, int: 0.3, hp: 11 },
    outfit: '#7a2418', accent: '#f2c94c', headgear: 'none', weapon: 'sword',
    fx: { self: { all: 0.15 } } },
  towerheir: { name: '마탑 계승자', style: 'mage', skill: '금지된 강의', desc: '마법 조사에서 본인 전투력 +30%, 토벌 +15%',
    base: { str: 3, dex: 6, int: 15, hp: 30 }, growth: { str: 0.6, dex: 1.2, int: 4.2, hp: 6 },
    outfit: '#3a1a5a', accent: '#f2d24b', headgear: 'hat', weapon: 'staff',
    fx: { self: { types: { magic: 0.3, hunt: 0.15 } } } },
  corsair: { name: '해적 선장', style: 'archer', skill: '갑판의 호령', desc: '호위에서 본인 전투력 +20%, 보상 금화 +10%, 이동 -1일',
    base: { str: 8, dex: 11, int: 6, hp: 38 }, growth: { str: 2.0, dex: 3.2, int: 1.2, hp: 8 },
    outfit: '#1a2a4a', accent: '#d6455d', headgear: 'hat', weapon: 'bow',
    fx: { self: { types: { escort: 0.2 } }, party: { gold: 0.1, days: -1 } } },
  fallencommander: { name: '몰락 기사단장', style: 'warrior', skill: '기사단 전법', desc: '방어·방어전·결전에서 본인 전투력 +25%, 파티 부상 확률 -20%',
    base: { str: 12, dex: 5, int: 7, hp: 54 }, growth: { str: 3.2, dex: 1.0, int: 1.6, hp: 11 },
    outfit: '#c9ced6', accent: '#3d5a9c', headgear: 'helmet', weapon: 'sword',
    fx: { self: { types: { defense: 0.25, warDefense: 0.25, battle: 0.25 } }, party: { injury: 0.8 } } },
};
const CAPTAIN_KEYS = Object.keys(CAPTAIN_CLASSES);
