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

