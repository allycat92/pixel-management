// 세계 데이터: 세력, 지방(영토), 용병단 이름·성향
'use strict';

// ───────── 세력 ─────────
// strength: 기본 국력, soldier: 전투 연출에 쓰는 병사 외형
const FACTIONS = {
  crown: {
    name: '아스트라 왕국', short: '왕국', color: '#3d5a9c', accent: '#d9a441', strength: 90, unitName: '왕국군',
    desc: '대륙 중앙의 왕정. 질서와 확장을 내세우며 국경 너머로 세력을 넓히려 한다.',
    perk: { key: 'tax', desc: '주급 -10% (세금 감면)' },
    soldier: { skins: ['#f2c9a0', '#e0ac7e', '#c68a5c'], hairs: ['#2b1d14', '#5a3720', '#a8642a'], classes: ['warrior', 'warrior', 'archer', 'mage'] },
  },
  north: {
    name: '북부 귀족 연합', short: '북부', color: '#6b3d7a', accent: '#c9c2b8', strength: 65, unitName: '공작가 기사단',
    desc: '발렌 공작가를 중심으로 뭉친 북부 귀족들. 왕권 강화에 반발하며 자치를 요구한다.',
    perk: { key: 'recruit', desc: '모집소 지원자 레벨 +2' },
    soldier: { skins: ['#f5d6b8', '#f2c9a0'], hairs: ['#c9c2b8', '#e3c565', '#2b1d14'], classes: ['warrior', 'warrior', 'archer', 'cleric'] },
  },
  cities: {
    name: '자유 도시 연맹', short: '자유도시', color: '#2e8a8a', accent: '#f2c94c', strength: 55, unitName: '도시 경비대',
    desc: '항구와 교역로를 쥔 상인 의회. 돈으로 군대를 사고, 돈으로 전쟁을 끝낸다.',
    perk: { key: 'shop', desc: '상점 가격 -15%' },
    soldier: { skins: ['#e0ac7e', '#c68a5c', '#8d5a3b'], hairs: ['#2b1d14', '#8c2f2f', '#3a3f6b'], classes: ['archer', 'warrior', 'rogue', 'mage'] },
  },
  church: {
    name: '성광 교단', short: '교단', color: '#d8cfb0', accent: '#b8862a', strength: 55, unitName: '성광 기사단',
    desc: '대륙 최대의 종교. 자비를 설교하지만, 이단 심문관들은 마법사와 이교도를 가차 없이 단죄한다.',
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
    name: '붉은 모래 부족 연합', short: '부족연합', color: '#a8402a', accent: '#e8d5a3', strength: 60, unitName: '부족 전사단',
    desc: '오크와 사막 부족들의 느슨한 연합. 왕국의 동진과 자유 도시의 노예 무역에 맞서 싸운다.',
    perk: { key: 'exp', desc: '의뢰 경험치 +20%' },
    soldier: { skins: ['#8fae6a', '#6f8e4a', '#c68a5c'], hairs: ['#2b1d14', '#5a3720'], classes: ['warrior', 'warrior', 'rogue', 'archer'] },
  },
  locals: {
    name: '지역 주민', short: '주민', color: '#7a7a6a', accent: '#c9c2b8', strength: 0, neutral: true, unitName: '주민',
    desc: '어느 세력에도 속하지 않은 마을과 순례자들.',
  },
};
const FACTION_KEYS = ['crown', 'north', 'cities', 'church', 'elves', 'clans'];
// 세력의 수도: 일상적인 전선 압박으로는 함락되지 않는다 (결전·공성으로만)
const CAPITALS = { crown: 'royal', north: 'valen', cities: 'port', church: 'sanctum', elves: 'silverwood', clans: 'redsand' };

// 시작 시 세력 관계 (-100 ~ 100)
const INITIAL_RELATIONS = {
  'crown|north': -45, 'crown|cities': 20, 'crown|church': 40, 'crown|elves': -25, 'crown|clans': -70,
  'north|cities': -10, 'north|church': 5, 'north|elves': -5, 'north|clans': -20,
  'cities|church': -10, 'cities|elves': 0, 'cities|clans': -45,
  'church|elves': -30, 'church|clans': -40,
  'elves|clans': -10,
};
const INITIAL_WARS = [['crown', 'clans']];

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
  mist:       { short: '안개 늪', name: '안개 늪지', terrain: 'swamp', owner: 'locals', tier: 2, pos: [50, 144],
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
