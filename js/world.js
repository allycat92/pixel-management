// 세계 데이터: 세력, 지방(영토), 용병단 이름·성향
'use strict';

// ───────── 세력 ─────────
// strength: 기본 국력, soldier: 전투 연출에 쓰는 병사 외형
const FACTIONS = {
  crown: {
    name: '아스트라 왕국', short: '왕국', color: '#3d5a9c', accent: '#d9a441', strength: 135, hegemon: true, unitName: '왕국군',
    desc: '대륙의 패권국. 고대의 용과 맺은 맹약으로 마물을 봉인해 왔으며, 그 힘을 바탕으로 대륙 전체를 한 왕관 아래 두려 한다.',
    perk: { key: 'tax', desc: '주급 -10% (세금 감면)' },
    soldier: { skins: ['#f2c9a0', '#e0ac7e', '#c68a5c'], hairs: ['#2b1d14', '#5a3720', '#a8642a'], classes: ['warrior', 'warrior', 'archer', 'mage'] },
  },
  north: {
    name: '북부 귀족 연합', short: '북부', color: '#6b3d7a', accent: '#c9c2b8', strength: 70, unitName: '공작가 기사단',
    desc: '발렌 공작가를 중심으로 뭉친 북부 귀족들. 왕권 강화에 반발하며 자치를 요구한다.',
    perk: { key: 'recruit', desc: '모집소 지원자 레벨 +2' },
    soldier: { skins: ['#f5d6b8', '#f2c9a0'], hairs: ['#c9c2b8', '#e3c565', '#2b1d14'], classes: ['warrior', 'warrior', 'archer', 'cleric'] },
  },
  cities: {
    name: '자유 도시 연맹', short: '자유 도시', color: '#2e8a8a', accent: '#f2c94c', strength: 55, unitName: '도시 경비대',
    desc: '항구와 교역로를 쥔 상인 의회. 돈으로 군대를 사고, 돈으로 전쟁을 끝낸다.',
    perk: { key: 'shop', desc: '상점 가격 -15%' },
    soldier: { skins: ['#e0ac7e', '#c68a5c', '#8d5a3b'], hairs: ['#2b1d14', '#8c2f2f', '#3a3f6b'], classes: ['archer', 'warrior', 'rogue', 'mage'] },
  },
  church: {
    name: '성광 교단', short: '교단', color: '#d8cfb0', accent: '#b8862a', strength: 120, hegemon: true, unitName: '성광 기사단',
    desc: '대륙의 또 다른 패권. 성광의 봉인으로 마계의 문을 막아 왔다고 전해진다. 자비를 설교하지만, 이종족과 이단에게는 성전을 선포한다.',
    perk: { key: 'heal', desc: '부상 회복 속도 +50%' },
    soldier: { skins: ['#f2c9a0', '#f5d6b8'], hairs: ['#c9c2b8', '#e3c565'], classes: ['cleric', 'warrior', 'cleric', 'mage'] },
  },
  elves: {
    name: '은빛 숲 엘프', short: '엘프', color: '#3f8a3a', accent: '#a7d26a', strength: 40, unitName: '숲 순찰대',
    desc: '고대 숲을 지키는 엘프들. 인간의 개척과 벌목에 날을 세우고 있다.',
    perk: { key: 'forest', desc: '숲 지형 의뢰 이동 -1일' },
    soldier: { skins: ['#f5d6b8'], hairs: ['#e3c565', '#c9c2b8', '#a7d26a'], classes: ['archer', 'archer', 'mage', 'rogue'] },
  },
  clans: {
    name: '붉은 모래 부족 연합', short: '부족 연합', color: '#a8402a', accent: '#e8d5a3', strength: 75, unitName: '부족 전사단',
    desc: '오크와 사막 부족들의 느슨한 연합. 왕국의 동진과 자유 도시의 노예 무역에 맞서 싸운다.',
    perk: { key: 'exp', desc: '의뢰 경험치 +20%' },
    soldier: { skins: ['#8fae6a', '#6f8e4a', '#c68a5c'], hairs: ['#2b1d14', '#5a3720'], classes: ['warrior', 'warrior', 'rogue', 'archer'] },
  },
  // ── 재앙 세력: 패권국이 무너지거나 세력이 셋 이상 멸망하면 대두한다 ──
  beasts: {
    name: '마물 군단', short: '마물군', color: '#5a1a10', accent: '#f39c12', strength: 170, calamity: true, unitName: '마물 군단',
    leader: '고룡 이그니스', leaderTitle: '용왕', lairs: ['dragon'],
    desc: '왕국과 맺은 고대의 맹약이 깨지자, 천 년을 잠든 고룡 이그니스가 깨어나 마물들을 이끌고 대륙을 집어삼키려 한다.',
    monsters: ['와이번', '오크', '숲 트롤', '하피', '가고일', '서리 트롤'],
    omen: '용의 등뼈 산맥에서 땅울림이 그치지 않습니다. 맹약의 힘이 약해지고 있습니다.',
    rise: '맹약이 깨졌습니다. 용의 등뼈 산맥이 불을 뿜고, 고룡 이그니스가 하늘을 가르며 깨어났습니다. 대륙의 마물들이 그 포효에 응답합니다.',
  },
  demons: {
    name: '마왕군', short: '마왕군', color: '#3a0a4a', accent: '#d6455d', strength: 170, calamity: true, unitName: '악마와 언데드 군단',
    leader: '마왕 베르녹스', leaderTitle: '마계의 군주', lairs: ['mist', 'frost'],
    desc: '성광의 봉인이 무너지자 안개 늪 아래 잠들어 있던 마계의 문이 열렸다. 마왕 베르녹스가 악마와 언데드를 이끌고 산 자의 땅을 노린다.',
    monsters: ['마족 전사', '지옥견', '해골 병사', '망령', '데스 나이트', '리치의 망령'],
    omen: '안개 늪의 밤이 길어지고, 묘지의 망자들이 뒤척입니다. 성광의 봉인이 약해지고 있습니다.',
    rise: '봉인이 무너졌습니다. 안개 늪 한가운데 마계의 문이 열리고, 마왕 베르녹스가 악마와 언데드의 군세를 이끌고 걸어 나왔습니다.',
  },
  locals: {
    name: '지역 주민', short: '주민', color: '#7a7a6a', accent: '#c9c2b8', strength: 0, neutral: true, unitName: '주민',
    desc: '어느 세력에도 속하지 않은 마을과 순례자들.',
  },
};

// 세력 병사의 외형: 세력의 병과·피부·머리색을 i 번째 순서대로 (전투 연출, 출격 편성 js/muster.js)
function factionSoldierLook(f, i) {
  const sd = FACTIONS[f].soldier || FACTIONS.crown.soldier;
  const cls = sd.classes[i % sd.classes.length];
  return { cls, skin: sd.skins[i % sd.skins.length], hair: sd.hairs[(i * 7) % sd.hairs.length], longHair: i % 3 === 1, tint: { outfit: FACTIONS[f].color, accent: FACTIONS[f].accent } };
}

const FACTION_KEYS = ['crown', 'north', 'cities', 'church', 'elves', 'clans'];
const CALAMITY_KEYS = ['beasts', 'demons'];
const CALAMITY_TRIGGER = 3;        // 이만큼 세력이 멸망하면 재앙이 대두
const CALAMITY_DARKNESS = 9;       // 재앙이 이만큼 지방을 차지하면 암흑시대 (게임 오버)
// 세력의 수도: 일상적인 전선 압박으로는 함락되지 않는다 (결전·공성으로만)
const CAPITALS = { crown: 'royal', north: 'valen', cities: 'port', church: 'sanctum', elves: 'silverwood', clans: 'redsand' };

// 시작 시 세력 관계 (-100 ~ 100)
const INITIAL_RELATIONS = {
  'crown|north': -65, 'crown|cities': 20, 'crown|church': 40, 'crown|elves': -25, 'crown|clans': -35,
  'north|cities': -10, 'north|church': 5, 'north|elves': -5, 'north|clans': -20,
  'cities|church': -10, 'cities|elves': 0, 'cities|clans': -45,
  'church|elves': -45, 'church|clans': -55,
  'elves|clans': -10,
};
const INITIAL_WARS = [['crown', 'north'], ['cities', 'clans']];

// ───────── 지방 ─────────
// tier: 활동에 필요한 길드 등급, terrain: 지형(몬스터·배경)
const TERRAIN = {
  plains:   { name: '평원', color: '#6fa84a', bg: 'plains', enemies: ['고블린', '들늑대', '산적'] },
  forest:   { name: '숲', color: '#3f7a3a', bg: 'forest', enemies: ['들늑대', '거대 거미', '숲 트롤'] },
  swamp:    { name: '늪지', color: '#4f6b4a', bg: 'swamp', enemies: ['늪 슬라임', '리자드맨', '망령'] },
  desert:   { name: '사막', color: '#c9a45a', bg: 'desert', enemies: ['사막 도적', '전갈 거인', '하피'] },
  frost:    { name: '설원', color: '#b8d4e8', bg: 'frost', enemies: ['서리 트롤', '설인', '해골 병사'] },
  mountain: { name: '화산 산맥', color: '#7a3a3a', bg: 'dragon', enemies: ['와이번', '가고일', '리치의 망령'] },
  holy:     { name: '성역', color: '#a8b87a', bg: 'plains', enemies: ['해골 병사', '망령', '산적'] },
  coast:    { name: '해안', color: '#7aa86a', bg: 'plains', enemies: ['산적', '리자드맨', '늪 슬라임'] },
};

const PROVINCES = {
  royal:      { short: '왕도', name: '왕도 크라운홀', terrain: 'plains', owner: 'crown', tier: 0, pos: [150, 112], home: true,
    places: ['왕도 외곽', '왕궁 지하수로', '상업 지구', '왕립 창고'] },
  wheat:      { short: '밀밭', name: '금빛 밀밭', terrain: 'plains', owner: 'crown', tier: 0, pos: [110, 142],
    places: ['밀밭 마을', '오래된 풍차', '곡물 창고', '강변 나루'] },
  border:     { short: '국경령', name: '동부 국경령', terrain: 'plains', owner: 'crown', tier: 0, pos: [196, 112],
    places: ['국경 요새', '동부 검문소', '국경 마을', '감시탑'] },
  silverwood: { short: '은빛 숲', name: '은빛 숲', terrain: 'forest', owner: 'elves', tier: 1, pos: [84, 84],
    places: ['은빛 숲 마을', '엘프 유적', '달빛 샘', '벌목 야영지'] },
  deepwood:   { short: '고대 숲', name: '고대 숲 심부', terrain: 'forest', owner: 'elves', tier: 3, pos: [42, 54],
    places: ['세계수 그루터기', '거미 골짜기', '고대 숲 사원', '이끼 낀 폐허'] },
  mist:       { short: '안개 늪', name: '안개 늪지', terrain: 'swamp', owner: 'church', tier: 2, pos: [50, 144],
    places: ['가라앉은 수도원', '마녀의 오두막', '마탑 폐허', '늪지 마을'] },
  valen:      { short: '발렌', name: '발렌 공작령', terrain: 'plains', owner: 'north', tier: 2, pos: [144, 66],
    places: ['발렌 성', '공작령 영지', '북부 가도', '기사 훈련장'] },
  frost:      { short: '서리 협곡', name: '서리 협곡', terrain: 'frost', owner: 'north', tier: 4, pos: [104, 24],
    places: ['북부 요새', '빙하 동굴', '얼어붙은 지하묘지', '서리 고개'] },
  sanctum:    { short: '대성당령', name: '성광 대성당령', terrain: 'holy', owner: 'church', tier: 2, pos: [206, 66],
    places: ['성광 대성당', '순례자의 길', '심문소', '수도원 서고'] },
  port:       { short: '세렌', name: '항구 도시 세렌', terrain: 'coast', owner: 'cities', tier: 1, pos: [230, 154],
    places: ['세렌 항구', '의회 회관', '조선소', '밀수꾼 부두'] },
  oasis:      { short: '오아시스', name: '오아시스 교역로', terrain: 'desert', owner: 'cities', tier: 3, pos: [290, 150],
    places: ['오아시스 도시', '피의 투기장', '사막 교역소', '노예 시장'] },
  redsand:    { short: '붉은 모래', name: '붉은 모래 황야', terrain: 'desert', owner: 'clans', tier: 3, pos: [262, 104],
    places: ['붉은 모래 야영지', '부족 회합지', '바위 요새', '모래 신전'] },
  dragon:     { short: '용의 등뼈', name: '용의 등뼈 산맥', terrain: 'mountain', owner: 'clans', tier: 5, pos: [270, 40],
    places: ['용암 동굴', '고대 용의 둥지', '불타는 성채', '오크 산채'] },
};
const PROVINCE_KEYS = Object.keys(PROVINCES);
const MAP_W = 320, MAP_H = 180;

// 지도 좌표 → 지방 (바다면 null). 지도 그리기와 인접 계산이 같은 규칙을 쓴다.
function mapNoise(x, y) {
  return Math.sin(x * 0.21 + y * 0.07) * 4 + Math.sin(y * 0.18 - x * 0.05) * 4 + Math.sin((x + y) * 0.5) * 1.5;
}
function provinceAt(x, y) {
  let best = null, bd = 1e9;
  for (const k of PROVINCE_KEYS) {
    const [px, py] = PROVINCES[k].pos;
    const d = Math.hypot((x - px) * 0.85, y - py);
    if (d < bd) { bd = d; best = k; }
  }
  return bd < 34 + mapNoise(x, y) ? best : null;
}

// 인접 지방 계산 (육지로 맞닿은 지방)
const ADJACENCY = (() => {
  const adj = {};
  PROVINCE_KEYS.forEach((k) => { adj[k] = new Set(); });
  const step = 2;
  const grid = [];
  for (let y = 0; y < MAP_H; y += step) {
    const row = [];
    for (let x = 0; x < MAP_W; x += step) row.push(provinceAt(x, y));
    grid.push(row);
  }
  for (let y = 0; y < grid.length; y++) {
    for (let x = 0; x < grid[y].length; x++) {
      const a = grid[y][x];
      if (!a) continue;
      [[1, 0], [0, 1]].forEach(([dx, dy]) => {
        const b = grid[y + dy] && grid[y + dy][x + dx];
        if (b && b !== a) { adj[a].add(b); adj[b].add(a); }
      });
    }
  }
  const out = {};
  PROVINCE_KEYS.forEach((k) => { out[k] = [...adj[k]]; });
  return out;
})();

// ───────── 용병단 ─────────
const COMPANY_NAME_A = ['철벽', '붉은 매', '잿빛 늑대', '서리 칼날', '황혼', '검은 방패', '은빛 창', '폭풍', '늑대 이빨',
  '강철 장미', '무쇠 발굽', '바람칼', '흑요석', '들불', '까마귀', '푸른 사자', '모래 전갈', '새벽 종', '쇠사슬', '백랑'];
const COMPANY_COLORS = ['#9c3b2e', '#3d5a9c', '#3f7a3a', '#6b3d7a', '#c58f1e', '#2e8a8a', '#5a5a6a', '#8f2d4a', '#b0702a', '#3a3f6b'];

// 외부 용병단 성향
const DISPOSITIONS = {
  gold:    { name: '돈 우선', desc: '보상 몫이 크지만, 결과만 좋으면 불평하지 않는다.' },
  honor:   { name: '명예', desc: '공작·구출 같은 뒷일은 싫어한다. 명예로운 승리에 충성도가 오른다.' },
  faction: { name: '세력 동조', desc: '동조하는 세력을 공격하는 의뢰는 거부하거나 크게 반발한다.' },
};
const COMPANY_SPECIALTIES = ['hunt', 'defense', 'raid', 'siege', 'sabotage', 'escort', 'explore'];

// ───────── 평판 혜택 ─────────
// 신뢰(45)·맹우(75)에 닿으면 세력 무기고의 장비를 대여한다. 평판이 기준보다 10 이상 떨어지면 회수된다.
const LOAN_RECALL_MARGIN = 10;
const FACTION_LOANS = {
  crown: [
    { at: 45, base: 'sword', name: '왕실 근위 장검', bonus: { str: 12, dex: 5, hp: 6 } },
    { at: 75, base: 'plate', name: '아스트라 기사 판금', bonus: { hp: 34, str: 6 } },
  ],
  north: [
    { at: 45, base: 'leather', name: '북부 늑대 망토', bonus: { hp: 18, dex: 8 } },
    { at: 75, base: 'ring', name: '발렌 공작가 인장 반지', bonus: { str: 8, dex: 8, int: 8 } },
  ],
  cities: [
    { at: 45, base: 'dagger', name: '의회 인장 단검', bonus: { dex: 12, str: 6 } },
    { at: 75, base: 'amulet', name: '황금 돛 부적', bonus: { hp: 12, dex: 7, int: 7 } },
  ],
  church: [
    { at: 45, base: 'mace', name: '성광 철퇴', bonus: { str: 8, int: 10 } },
    { at: 75, base: 'robe', name: '대신관의 백색 로브', bonus: { hp: 16, int: 14 } },
  ],
  elves: [
    { at: 45, base: 'bow', name: '달빛 장궁', bonus: { dex: 16, str: 5 } },
    { at: 75, base: 'amulet', name: '세계수 잎 부적', bonus: { hp: 18, int: 12, dex: 4 } },
    { at: 90, base: 'sword', name: '엘프 왕의 성검', bonus: { str: 16, dex: 12, int: 8 } },
  ],
  clans: [
    { at: 45, base: 'sword', name: '부족장의 도끼', bonus: { str: 15, hp: 8 } },
    { at: 75, base: 'leather', name: '붉은 모래 전사 갑옷', bonus: { hp: 24, dex: 8 } },
  ],
};
// 평판 60 이상이면 매주 세력 정예 용병이 모집소에 온다. 평판이 0 아래로 떨어지면 본국으로 소환된다.
const ELITE_AT = 60;
const ELITE_LEVEL_BONUS = { elves: 4 }; // 엘프 정예는 수백 년을 산 숙련자다
const FACTION_TRAITS = { crown: 'royalguard', north: 'northknight', cities: 'broker', church: 'blessed', elves: 'sylvan', clans: 'warcry' };

// ───────── 세력 행동강령 ─────────
// aggression: 호전성(선전포고·공세 빈도), warAt: 이 관계 이하에서 선전포고를 고려, peaceAt: 이 전쟁 피로에서 강화를 고려
// reach: 원정 거리(지방 단위), defense: 자기 영토 장악도 손실 배율, targets: 주적(가중치), drift: 매주 관계 경향
// activity: 분쟁 의뢰를 내는 빈도, bias: 선호하는 의뢰 유형, pay: 보수 배율
const DOCTRINES = {
  crown: {
    name: '왕권 확립', motto: '반역자는 왕의 검을 받으리라.',
    desc: '왕국은 하나의 왕관 아래 통일되어야 한다. 자치를 외치는 북부 귀족과 국경을 넘보는 부족을 용납하지 않는다.',
    aggression: 1.3, warAt: -45, peaceAt: 65, reach: 1, defense: 0.8,
    targets: { north: 2.5, clans: 1.2 }, drift: { north: -3, church: 1 },
    activity: 1.1, bias: { siege: 2, raid: 1.5, counterspy: 1.5 }, pay: 1,
  },
  north: {
    name: '자치 수호', motto: '북부는 굴복하지 않는다.',
    desc: '북부는 왕의 영지가 아니다. 먼저 칼을 뽑기보다는 버티며, 왕권이 손을 뻗으면 공작과 방어로 맞선다.',
    aggression: 0.8, warAt: -60, peaceAt: 45, reach: 1, defense: 1,
    targets: { crown: 1.6 }, drift: { crown: -1, cities: 1 },
    activity: 1, bias: { sabotage: 2, warDefense: 2, rescue: 1.2 }, pay: 1,
  },
  cities: {
    name: '이윤 추구', motto: '금화는 피보다 진하다.',
    desc: '전쟁은 장사에 해롭다. 먼저 전쟁을 걸지 않고 강화를 서두른다. 다만 노예 무역을 방해하는 부족에게는 용병을 아끼지 않는다.',
    aggression: 0.35, warAt: -70, peaceAt: 30, reach: 1, defense: 1,
    targets: { clans: 1.5 }, drift: { clans: -1, crown: 1, north: 1, elves: 1 },
    activity: 1, bias: { envoy: 3, sabotage: 2, counterspy: 1.2 }, pay: 1.2,
  },
  church: {
    name: '성전', motto: '빛이 닿지 않는 곳은 불로 밝힌다.',
    desc: '빛을 모르는 이종족은 정화되어야 한다. 엘프와 오크를 향한 성전을 멈추지 않으며, 성전군은 먼 땅까지 원정한다.',
    aggression: 1.5, warAt: -40, peaceAt: 80, reach: 2, defense: 0.8,
    targets: { elves: 2.6, clans: 1.2 }, drift: { elves: -3, clans: -1, crown: 1 },
    activity: 1.15, bias: { raid: 2, siege: 1.5, counterspy: 2, rescue: 0.5 }, pay: 1,
  },
  elves: {
    name: '숲의 침묵', motto: '숲은 기다린다.',
    desc: '엘프는 숲 밖의 일에 관여하지 않는다. 먼저 전쟁을 걸지 않지만, 숲에 들어온 적에게는 끈질기게 저항한다.',
    aggression: 0.15, warAt: -85, peaceAt: 25, reach: 1, defense: 0.95,
    targets: {}, drift: {},
    activity: 0.55, bias: { warDefense: 3, envoy: 2, counterspy: 1, siege: 0.2, raid: 0.5 }, pay: 1,
  },
  clans: {
    name: '피의 맹세', motto: '모래는 피를 기억한다.',
    desc: '빼앗긴 땅과 사슬에 묶인 형제들을 잊지 않는다. 습격으로 적을 지치게 하고, 사막의 유목민답게 흩어졌다가도 다시 모인다.',
    aggression: 1.2, warAt: -50, peaceAt: 55, reach: 1, defense: 0.7,
    targets: { cities: 1.8, crown: 1.5, church: 1.4 }, drift: { cities: -2, church: -1 },
    activity: 1.1, bias: { raid: 3, rescue: 2 }, pay: 1,
  },
  beasts: {
    name: '포식', motto: '모든 것은 불타고, 먹힌다.', desc: '마물 군단은 협상하지 않는다. 대륙의 모든 세력과 싸우며 끝없이 세를 불린다.',
    aggression: 3, warAt: 0, peaceAt: 9999, reach: 2, defense: 0.85, targets: {}, drift: {}, activity: 0, bias: {}, pay: 1,
  },
  demons: {
    name: '멸망', motto: '산 자의 시대는 끝났다.', desc: '마왕군은 협상하지 않는다. 쓰러진 자를 언데드로 일으켜 세우며 끝없이 세를 불린다.',
    aggression: 3, warAt: 0, peaceAt: 9999, reach: 2, defense: 0.85, targets: {}, drift: {}, activity: 0, bias: {}, pay: 1,
  },
};

// 지방 사이 거리 (인접 단계)
const PROV_DIST = (() => {
  const d = {};
  PROVINCE_KEYS.forEach((a) => {
    d[a] = { [a]: 0 };
    const q = [a];
    while (q.length) {
      const p = q.shift();
      ADJACENCY[p].forEach((n) => { if (d[a][n] == null) { d[a][n] = d[a][p] + 1; q.push(n); } });
    }
  });
  return d;
})();
