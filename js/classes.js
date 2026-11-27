// 직업과 스킬: 범용 대원 직업 계통, 용병대장 고유 직업, 특별 용병 고유 직업
// - 범용 대원: 액티브 스킬 1개 (현재 직업의 것. 전투에서는 사실상 기본 공격/치유)
// - 고유 직업(대장·특별 용병): 액티브 스킬 2개(기본기 + 특기) + 패시브 1개(대장: 지휘, 특별 용병: 고유 패시브)
'use strict';

// ───────── 전투 스킬 정의 ─────────
// 전투 스킬(b) 필드:
//   cd 재사용(초), range 사거리, tgt 'enemy'(적) | 'hurt'(다친 아군) | 'self'(자기 주변),
//   shot 투사체(arrow/fire/holy/curse/bolt/dagger, 없으면 근접), dmg 피해 배율, heal 치유 배율,
//   aoe 범위 반경, hits 동시 대상 수, stun 기절(초), dash 돌진, drain 흡혈 비율, exec 빈사(35% 이하) 추가 피해,
//   buff {atk, def, dur} (치유·버프 대상에게), selfBuff {atk, def, dur} (적중 시 자신에게)
const SK = {
  melee: (name, dmg = 1, cd = 1, x = {}) => ({ name, cd, range: 11, tgt: 'enemy', dmg, ...x }),
  shot: (name, shot, dmg = 1, range = 90, cd = 1.25, x = {}) => ({ name, cd, range, tgt: 'enemy', shot, dmg, ...x }),
  heal: (name, heal = 1, range = 70, cd = 1.6, x = {}) => ({ name, cd, range, tgt: 'hurt', shot: 'holy', heal, ...x }),
  rally: (name, buff, aoe = 50, cd = 10, x = {}) => ({ name, cd, range: 0, tgt: 'self', buff, aoe, ...x }),
};

const pct = (v) => `${Math.round(v * 100)}%`;
function describeBattle(b) {
  const parts = [];
  if (b.tgt === 'hurt') parts.push(`${b.aoe ? '범위 ' : ''}치유 ×${b.heal}`);
  else if (b.tgt === 'self') parts.push(`주변 아군${b.buff.atk ? ` 공격 +${pct(b.buff.atk)}` : ''}${b.buff.def ? ` 받는 피해 -${pct(b.buff.def)}` : ''} ${b.buff.dur}초`);
  else {
    parts.push(`${b.shot ? '원거리' : '근접'}${b.aoe ? ' 범위' : ''}${b.hits ? ` ${b.hits}명` : ''} 공격 ×${b.dmg}`);
    if (b.dash) parts.push('돌진');
    if (b.stun) parts.push(`기절 ${b.stun}초`);
    if (b.drain) parts.push(`흡혈 ${pct(b.drain)}`);
    if (b.exec) parts.push(`빈사 대상 +${pct(b.exec)}`);
  }
  if (b.tgt === 'hurt' && b.buff) parts.push(`대상 ${b.buff.atk ? `공격 +${pct(b.buff.atk)}` : ''}${b.buff.def ? ` 받는 피해 -${pct(b.buff.def)}` : ''} ${b.buff.dur}초`);
  if (b.selfBuff) parts.push(`적중 시 자신 ${b.selfBuff.atk ? `공격 +${pct(b.selfBuff.atk)}` : ''}${b.selfBuff.def ? `받는 피해 -${pct(b.selfBuff.def)}` : ''}`);
  parts.push(`재사용 ${b.cd}초`);
  return parts.join(' · ');
}

// 의뢰 효과(fx): self.all / self.types (본인 전투력), party.* (파티 전체)
function describePartyAttack(success) {
  const bonus = Number(((Stats.aidOf(success) - 1) * 100).toFixed(1));
  return `파티 공격 +${bonus}% (합산 최대 ${pct(Stats.KN.AID_CAP)})`;
}

function describeFx(fx, battle = false) {
  if (!fx) return '';
  const out = [];
  const self = fx.self || {}, p = fx.party || {};
  if (self.all) out.push(`본인 ${battle ? '전투 체력·공격' : '전투력'} +${pct(self.all)}`);
  if (self.types) {
    const groups = {};
    Object.entries(self.types).forEach(([t, v]) => { (groups[v] = groups[v] || []).push(QUEST_TYPES[t].name); });
    Object.entries(groups).forEach(([v, ts]) => out.push(`${ts.join('·')}에서 본인${battle ? ' 전투 체력·공격' : ''} +${pct(Number(v))}`));
  }
  if (p.success) out.push(battle ? describePartyAttack(p.success) : `파티 성공률 +${pct(p.success)}`);
  if (p.injury != null) out.push(`부상 확률 -${pct(1 - p.injury)}`);
  if (p.death != null) out.push(p.death === 0 ? '사망 위험 없음' : `사망 위험 -${pct(1 - p.death)}`);
  if (p.gold) out.push(`보상 금화 +${pct(p.gold)}`);
  if (p.great) out.push(battle ? `대성공 필요 체력 ÷${p.great}` : `대성공 확률 ×${p.great}`);
  if (p.greatGold) out.push(`대성공 보상 +${pct(p.greatGold)}`);
  if (p.days) out.push(`이동 ${p.days}일`);
  if (p.noDisaster) out.push('대실패 방지');
  if (p.healHalf) out.push('부상 기간 절반');
  if (p.loot) out.push(`성공 시 ${pct(p.loot)} 확률로 장비`);
  if (p.noMoraleLoss) out.push('사기 하락 없음');
  return out.join(', ');
}

// 대장의 지휘(패시브)
function describeLead(l, battle = false) {
  const out = [];
  if (l.power) out.push(`용병단 ${battle ? '전투 체력·공격' : '전투력'} +${pct(l.power)}`);
  if (l.types) {
    const groups = {};
    Object.entries(l.types).forEach(([t, v]) => { (groups[v] = groups[v] || []).push(QUEST_TYPES[t].name); });
    Object.entries(groups).forEach(([v, ts]) => out.push(`${ts.join('·')} +${pct(Number(v))}`));
  }
  if (l.cls) {
    const groups = {};
    Object.entries(l.cls).forEach(([c, v]) => { (groups[v] = groups[v] || []).push(CLASSES[c].name); });
    Object.entries(groups).forEach(([v, cs]) => out.push(`${cs.join('·')} 계열 대원 +${pct(Number(v))}`));
  }
  if (l.vsCalamity) out.push(`재앙 세력·재앙급 괴물 상대 +${pct(l.vsCalamity)}`);
  const pf = describeFx({ party: l.party }, battle);
  if (pf) out.push(pf);
  return out.join(', ');
}

// ───────── 범용 대원: 직업 계통 (기본 → 상급 2갈래 → 최상급 2갈래) ─────────
// 대원은 개인 능력치에 편차가 없다. 같은 직업·레벨이면 능력치가 같고, 승급할 때마다 갈래를 골라
// 역할을 정한다. 대원은 현재 직업의 액티브 스킬 하나를 쓴다 (전투: 기본기, 의뢰: fx).
const CLASS_SKILLS = {
  warrior: { name: '방패 치기', b: SK.melee('방패 치기', 1, 1.0), fx: { party: { injury: 0.85 } } },
  archer:  { name: '조준 사격', b: SK.shot('조준 사격', 'arrow', 1, 95, 1.25), fx: { party: { success: 0.04 } } },
  mage:    { name: '화염구', b: SK.shot('화염구', 'fire', 1.3, 85, 1.9, { aoe: 12 }), fx: { self: { types: { magic: 0.2 } } } },
  cleric:  { name: '치유', b: SK.heal('치유', 1, 70, 1.6), fx: { party: { injury: 0.5, death: 0.35 } } },
  rogue:   { name: '기습', b: SK.melee('기습', 1, 0.75, { exec: 0.3 }), fx: { party: { gold: 0.12 } } },
};

// 단계별 레벨 상한: 상한에 닿으면 승급해야 더 성장한다
const UNIT_TIERS = [
  { name: '기본', cap: 10 },
  { name: '상급', cap: 20, at: 10, cost: 350 },
  { name: '최상급', cap: 30, at: 20, cost: 900 },
];
const PROMOTE_LEVEL = UNIT_TIERS[1].at;
const PROMOTE_COST = UNIT_TIERS[1].cost;
const MASTER_LEVEL = UNIT_TIERS[2].at;
const MASTER_COST = UNIT_TIERS[2].cost;

// 상급 직업: 기본 직업마다 두 갈래. bonus: 승급 즉시 능력치, growth: 레벨업 성장 추가
const PROMOTIONS = {
  warrior: [
    { key: 'paladin', name: '성기사', skill: '심판의 방패', b: SK.melee('심판의 방패', 1, 1.0, { drain: 0.25 }),
      bonus: { maxHp: 20, str: 2, int: 3 }, growth: { hp: 2, int: 0.6 }, outfit: '#c9ced6', accent: '#d9a441',
      fx: { party: { injury: 0.7, death: 0.5 } } },
    { key: 'swordmaster', name: '검성', skill: '일섬', b: SK.melee('일섬', 1.3, 0.9, { dash: true }),
      bonus: { str: 6, dex: 3 }, growth: { str: 0.8, dex: 0.5 }, outfit: '#5a2430', accent: '#e8e4d8',
      fx: { self: { types: { hunt: 0.3, defense: 0.3 } } } },
  ],
  archer: [
    { key: 'ranger', name: '레인저', skill: '속사', b: SK.shot('속사', 'arrow', 0.75, 95, 0.7),
      bonus: { dex: 4, maxHp: 8 }, growth: { dex: 0.5, hp: 1 }, outfit: '#2f5a2a', accent: '#d9a441',
      fx: { self: { types: { explore: 0.25, escort: 0.25 } }, party: { days: -1 } } },
    { key: 'sniper', name: '저격수', skill: '급소 사격', b: SK.shot('급소 사격', 'arrow', 1.6, 130, 1.8, { exec: 0.5 }),
      bonus: { dex: 7 }, growth: { dex: 0.8 }, outfit: '#4a4a5a', accent: '#d6455d',
      fx: { party: { great: 2 } } },
  ],
  mage: [
    { key: 'elementalist', name: '원소술사', skill: '원소 폭풍', b: SK.shot('원소 폭풍', 'fire', 1.25, 85, 2.0, { aoe: 18 }),
      bonus: { int: 7 }, growth: { int: 0.8 }, outfit: '#9c3b2e', accent: '#f39c12',
      fx: { self: { types: { hunt: 0.3, magic: 0.3 } } } },
    { key: 'warder', name: '결계술사', skill: '속박탄', b: SK.shot('속박탄', 'bolt', 0.9, 80, 1.6, { stun: 0.4 }),
      bonus: { int: 4, maxHp: 10 }, growth: { int: 0.4, hp: 1.5 }, outfit: '#2e6b7a', accent: '#7fd6e8',
      fx: { party: { noDisaster: true, injury: 0.8 } } },
  ],
  cleric: [
    { key: 'highpriest', name: '대사제', skill: '부활의 기도', b: SK.heal('부활의 기도', 1.3, 70, 1.8, { aoe: 14 }),
      bonus: { int: 5, maxHp: 8 }, growth: { int: 0.6, hp: 1 }, outfit: '#f2ecd8', accent: '#7fd6e8',
      fx: { party: { death: 0, healHalf: true } } },
    { key: 'battlepriest', name: '전투사제', skill: '신성 강타', b: SK.melee('신성 강타', 1.15, 1.0, { drain: 0.2 }),
      bonus: { str: 5, maxHp: 10 }, growth: { str: 0.9, hp: 1 }, outfit: '#a88a4a', accent: '#f2ecd8',
      fx: { self: { all: 0.2 }, party: { injury: 0.8 } } },
  ],
  rogue: [
    { key: 'assassin', name: '암살자', skill: '암살', b: SK.melee('암살', 1.1, 0.8, { exec: 0.8, dash: true }),
      bonus: { dex: 5, str: 3 }, growth: { dex: 0.6, str: 0.4 }, outfit: '#1f1a28', accent: '#d6455d',
      fx: { self: { types: { hunt: 0.3 } }, party: { greatGold: 0.3 } } },
    { key: 'thief', name: '대도', skill: '날치기', b: SK.shot('날치기', 'dagger', 0.9, 45, 0.7),
      bonus: { dex: 4, int: 3 }, growth: { dex: 0.5, int: 0.4 }, outfit: '#5a4a2a', accent: '#f2c94c',
      fx: { party: { gold: 0.25, loot: 0.25 } } },
  ],
};
const ADV_CLASSES = {};
Object.entries(PROMOTIONS).forEach(([cls, list]) => list.forEach((p) => { ADV_CLASSES[p.key] = { ...p, base: cls }; }));

// 최상급 직업: 상급 직업마다 다시 두 갈래 (Lv.20)
const MASTERS = {
  paladin: [
    { key: 'guardian', name: '수호기사', skill: '불굴의 성벽', b: SK.melee('불굴의 성벽', 1, 1.0, { selfBuff: { def: 0.3, dur: 1.5 } }),
      bonus: { maxHp: 30, str: 4, int: 3 }, growth: { hp: 2.5, str: 0.4 }, outfit: '#e8eef2', accent: '#f2c94c',
      fx: { party: { injury: 0.6, death: 0.4 }, self: { types: { defense: 0.3, escort: 0.3, warDefense: 0.3 } } } },
    { key: 'crusader', name: '성전사', skill: '성전의 철퇴', b: SK.melee('성전의 철퇴', 1.2, 1.0, { aoe: 10 }),
      bonus: { str: 7, maxHp: 20 }, growth: { str: 0.8, hp: 1.5 }, outfit: '#d9d0b0', accent: '#9c3b2e',
      fx: { self: { types: { raid: 0.3, siege: 0.3, battle: 0.3 } }, party: { injury: 0.8 } } },
  ],
  swordmaster: [
    { key: 'swordsaint', name: '검신', skill: '천검', b: SK.melee('천검', 1.5, 0.9, { hits: 2 }),
      bonus: { str: 9, dex: 5 }, growth: { str: 1.0, dex: 0.5 }, outfit: '#2a0e18', accent: '#f2c94c',
      fx: { self: { all: 0.35 } } },
    { key: 'berserker', name: '광전사', skill: '피의 난무', b: SK.melee('피의 난무', 1.4, 0.8, { drain: 0.3 }),
      bonus: { str: 10, maxHp: 10 }, growth: { str: 1.1, hp: 1 }, outfit: '#5a1010', accent: '#d6455d',
      fx: { self: { all: 0.25, types: { hunt: 0.15 } } } },
  ],
  ranger: [
    { key: 'pathfinder', name: '대륙 순찰자', skill: '질풍 사격', b: SK.shot('질풍 사격', 'arrow', 0.8, 100, 0.6),
      bonus: { dex: 6, maxHp: 14 }, growth: { dex: 0.7, hp: 1.5 }, outfit: '#1f4a2a', accent: '#e8e4d8',
      fx: { self: { types: { explore: 0.35, escort: 0.35, rescue: 0.35 } }, party: { days: -1 } } },
    { key: 'beastcaller', name: '야수 사냥꾼', skill: '사냥개 풀기', b: SK.shot('사냥개 풀기', 'arrow', 0.85, 95, 0.9, { hits: 2 }),
      bonus: { dex: 7, str: 3 }, growth: { dex: 0.7, str: 0.3 }, outfit: '#4a3a1a', accent: '#a7d26a',
      fx: { self: { types: { hunt: 0.3, explore: 0.2 } } } },
  ],
  sniper: [
    { key: 'skyarcher', name: '천궁', skill: '천리안', b: SK.shot('천리안', 'arrow', 1.9, 140, 1.8, { exec: 0.6 }),
      bonus: { dex: 10 }, growth: { dex: 1.0 }, outfit: '#2a2a3a', accent: '#f2c94c',
      fx: { party: { great: 2, success: 0.05 } } },
    { key: 'arbalest', name: '노궁 대장', skill: '관통 노궁', b: SK.shot('관통 노궁', 'bolt', 1.6, 120, 2.0, { aoe: 8 }),
      bonus: { dex: 7, str: 5 }, growth: { dex: 0.7, str: 0.5 }, outfit: '#3a3a3a', accent: '#c58f1e',
      fx: { self: { types: { siege: 0.35, battle: 0.2 } } } },
  ],
  elementalist: [
    { key: 'archmage', name: '대마도사', skill: '메테오', b: SK.shot('메테오', 'fire', 1.6, 90, 2.2, { aoe: 22 }),
      bonus: { int: 10, maxHp: 6 }, growth: { int: 1.0 }, outfit: '#5a1414', accent: '#f2c94c',
      fx: { self: { types: { hunt: 0.4, magic: 0.4, siege: 0.4, battle: 0.4 } } } },
    { key: 'stormmage', name: '뇌우술사', skill: '연쇄 번개', b: SK.shot('연쇄 번개', 'bolt', 1.0, 90, 1.6, { hits: 3, stun: 0.3 }),
      bonus: { int: 9, dex: 3 }, growth: { int: 0.9, dex: 0.3 }, outfit: '#2a3a6a', accent: '#7fd6e8',
      fx: { self: { types: { raid: 0.3, battle: 0.3, magic: 0.2 } } } },
  ],
  warder: [
    { key: 'sealmaster', name: '봉인술사', skill: '절대 결계', b: SK.shot('절대 결계', 'bolt', 0.8, 85, 1.6, { stun: 0.8 }),
      bonus: { int: 6, maxHp: 16 }, growth: { int: 0.6, hp: 2 }, outfit: '#14404a', accent: '#a7e8f4',
      fx: { party: { noDisaster: true, injury: 0.65, death: 0.6 } } },
    { key: 'chronomancer', name: '시간술사', skill: '시간 정지', b: SK.shot('시간 정지', 'bolt', 0.6, 90, 2.4, { stun: 1.4 }),
      bonus: { int: 8, maxHp: 8 }, growth: { int: 0.8, hp: 1 }, outfit: '#4a3a6a', accent: '#f2d24b',
      fx: { party: { days: -1, success: 0.05, noDisaster: true } } },
  ],
  highpriest: [
    { key: 'saint', name: '성자', skill: '기적', b: SK.heal('기적', 1.5, 75, 1.8, { aoe: 18 }),
      bonus: { int: 7, maxHp: 14 }, growth: { int: 0.8, hp: 1.5 }, outfit: '#ffffff', accent: '#f2c94c',
      fx: { party: { death: 0, healHalf: true, injury: 0.75 } } },
    { key: 'oracle', name: '신탁자', skill: '예언의 빛', b: SK.heal('예언의 빛', 1.0, 80, 1.6, { aoe: 12, buff: { atk: 0.2, dur: 3 } }),
      bonus: { int: 8, dex: 3 }, growth: { int: 0.8, dex: 0.2 }, outfit: '#e8e0f8', accent: '#9b6ad6',
      fx: { party: { success: 0.08, great: 1.3, death: 0.5 } } },
  ],
  battlepriest: [
    { key: 'inquisitor', name: '심판관', skill: '심판의 철퇴', b: SK.melee('심판의 철퇴', 1.3, 1.0, { drain: 0.2, stun: 0.3 }),
      bonus: { str: 7, maxHp: 16 }, growth: { str: 1.0, hp: 1.5 }, outfit: '#6a4a1a', accent: '#ffffff',
      fx: { self: { all: 0.3, types: { counterspy: 0.3 } } } },
    { key: 'templar', name: '성당 기사', skill: '빛의 방패', b: SK.melee('빛의 방패', 1.1, 1.0, { selfBuff: { def: 0.35, dur: 1.5 } }),
      bonus: { str: 5, maxHp: 24 }, growth: { str: 0.6, hp: 2.2 }, outfit: '#d0d8e0', accent: '#3d5a9c',
      fx: { self: { types: { defense: 0.25, warDefense: 0.25 } }, party: { death: 0.5 } } },
  ],
  assassin: [
    { key: 'nightblade', name: '무영', skill: '그림자 처형', b: SK.melee('그림자 처형', 1.3, 0.8, { exec: 1.0, dash: true }),
      bonus: { dex: 8, str: 5 }, growth: { dex: 0.8, str: 0.5 }, outfit: '#0e0a14', accent: '#8f2d4a',
      fx: { self: { types: { hunt: 0.4, raid: 0.4, sabotage: 0.4 } } } },
    { key: 'poisoner', name: '독술사', skill: '맹독 단검', b: SK.shot('맹독 단검', 'dagger', 1.0, 60, 0.9, { exec: 0.5 }),
      bonus: { dex: 7, int: 5 }, growth: { dex: 0.6, int: 0.5 }, outfit: '#1a3a1a', accent: '#7ed37e',
      fx: { self: { types: { hunt: 0.25, sabotage: 0.3 } }, party: { greatGold: 0.2 } } },
  ],
  thief: [
    { key: 'phantom', name: '괴도', skill: '황금 손', b: SK.shot('황금 손', 'dagger', 1.0, 50, 0.7),
      bonus: { dex: 6, int: 5 }, growth: { dex: 0.6, int: 0.5 }, outfit: '#3a2a4a', accent: '#f2c94c',
      fx: { party: { gold: 0.35, loot: 0.4 } } },
    { key: 'smuggler', name: '밀수왕', skill: '연막탄', b: SK.shot('연막탄', 'dagger', 0.5, 60, 1.6, { aoe: 14, stun: 0.6 }),
      bonus: { dex: 6, maxHp: 12 }, growth: { dex: 0.6, hp: 1 }, outfit: '#4a3a2a', accent: '#c9c2b8',
      fx: { party: { gold: 0.2, days: -1 } } },
  ],
};
const MASTER_CLASSES = {};
Object.entries(MASTERS).forEach(([adv, list]) => list.forEach((m) => { MASTER_CLASSES[m.key] = { ...m, from: adv, base: ADV_CLASSES[adv].base }; }));

// ───────── 용병대장: 고유 직업 ─────────
// 대장마다 하나뿐인 고유 직업. 높은 성장률, 레벨 상한 40.
// acts: [기본기, 특기] 액티브 2개, lead: 지휘(패시브) — 자기 용병단 전체에 걸린다.
// lead: power(용병단 전투력 +), types(의뢰 유형별 +), cls(기본 직업별 대원 +), party(파티 효과), vsCalamity(재앙 상대 +)
const CAPTAIN_CAP = 40;
const CAPTAIN_AWAKEN = 20; // 이 레벨부터 지휘 효과 1.5배

// 싸움 방식별 기본 능력치·성장률 (대장 수준)
const CAPTAIN_STYLE = {
  warrior: { base: { str: 12, dex: 6, int: 3, hp: 50 }, growth: { str: 3.4, dex: 1.4, int: 0.6, hp: 10.5 } },
  archer:  { base: { str: 7, dex: 12, int: 5, hp: 36 }, growth: { str: 1.8, dex: 3.5, int: 1.1, hp: 7.5 } },
  mage:    { base: { str: 4, dex: 6, int: 13, hp: 32 }, growth: { str: 0.9, dex: 1.3, int: 3.8, hp: 6.5 } },
  cleric:  { base: { str: 6, dex: 5, int: 11, hp: 44 }, growth: { str: 1.6, dex: 1.1, int: 3.0, hp: 9.5 } },
  rogue:   { base: { str: 7, dex: 12, int: 6, hp: 32 }, growth: { str: 1.7, dex: 3.6, int: 1.4, hp: 6.5 } },
};
// cap(style, 외형, 지휘, 액티브, 보정): tilt는 능력치 쏠림 (기본치 +2, 성장 +0.4)
function cap(name, style, desc, look, lead, acts, tilt = {}) {
  const st = CAPTAIN_STYLE[style];
  const base = { ...st.base }, growth = { ...st.growth };
  Object.entries(tilt).forEach(([k, v]) => { base[k] += v * 2; growth[k] += v * 0.4; });
  return { name, style, desc, base, growth, ...look, lead, acts };
}
const L = (outfit, accent, headgear, weapon) => ({ outfit, accent, headgear, weapon });

const CAPTAIN_CLASSES = {
  // ── 창설 후보 (9) ──
  blademaster: cap('검귀', 'warrior', '전장을 베어 가르는 검의 귀신. 앞장서서 대원들의 투지를 끌어올린다.', L('#3a1018', '#e8e4d8', 'band', 'sword'),
    { name: '선봉의 검', power: 0.06, cls: { warrior: 0.12 } },
    [SK.melee('참격', 1.15, 0.9), SK.melee('회전베기', 1.4, 7, { aoe: 18 })], { str: 1, dex: 0.5 }),
  ironwall: cap('철벽 수호자', 'warrior', '한 번도 진형을 무너뜨린 적 없는 방패. 대원들을 살려서 돌아온다.', L('#4a5a6a', '#d9a441', 'helmet', 'mace'),
    { name: '방진', power: 0.03, types: { defense: 0.12, escort: 0.12, warDefense: 0.12 }, party: { injury: 0.65, death: 0.5 } },
    [SK.melee('방패 밀치기', 1, 1.0, { stun: 0.2 }), SK.rally('철벽 방진', { def: 0.4, dur: 6 }, 45, 12)], { hp: 1.5 }),
  tactician: cap('전술가', 'mage', '판을 읽는 눈을 가진 지휘관. 개인의 무용보다 용병단 전체를 움직인다.', L('#3a3a4a', '#f2c94c', 'hat', 'staff'),
    { name: '전술 지휘', power: 0.1, party: { success: 0.05, great: 1.4 } },
    [SK.shot('지휘 사격', 'bolt', 1.0, 90, 1.4), SK.rally('전술 지시', { atk: 0.25, def: 0.2, dur: 7 }, 60, 12)]),
  lancer: cap('창기병', 'warrior', '말과 창을 잃고도 기사의 돌격만은 잊지 않은 사내.', L('#3d5a9c', '#e8e4d8', 'helmet', 'sword'),
    { name: '돌파', power: 0.03, types: { battle: 0.15, raid: 0.1 }, cls: { warrior: 0.08 } },
    [SK.melee('창 찌르기', 1.1, 1.0, { range: 16 }), SK.melee('랜스 차지', 1.8, 9, { dash: true, stun: 0.5 })], { str: 0.5, hp: 0.5 }),
  huntress: cap('덫사냥꾼', 'archer', '숲을 손바닥처럼 아는 사냥꾼. 덫과 화살로 짐승을 몰아넣는다.', L('#4a5a2a', '#c58f1e', 'band', 'bow'),
    { name: '사냥터의 지혜', power: 0.02, types: { hunt: 0.15, explore: 0.15 }, party: { success: 0.03 } },
    [SK.shot('사냥 화살', 'arrow', 1.0, 95, 1.15), SK.shot('올가미 덫', 'bolt', 0.6, 80, 8, { aoe: 16, stun: 1.0 })]),
  hedgemage: cap('떠돌이 마법사', 'mage', '마탑 문턱도 못 넘었지만 실전으로 마법을 익힌 시골 마법사.', L('#5a4a7a', '#e8c86a', 'hat', 'staff'),
    { name: '실전 마법', power: 0.03, types: { magic: 0.15 }, cls: { mage: 0.12 } },
    [SK.shot('불씨', 'fire', 1.2, 85, 1.7, { aoe: 10 }), SK.shot('번개 폭풍', 'bolt', 1.1, 90, 9, { hits: 3, stun: 0.4 })]),
  fieldmedic: cap('야전 의무관', 'cleric', '수많은 전장에서 부상병을 끌어낸 종군 의무관.', L('#e8e4d8', '#9c3b2e', 'none', 'mace'),
    { name: '야전 의술', power: 0.03, party: { injury: 0.6, death: 0.5 } },
    [SK.heal('응급 처치', 1.25, 70, 1.4), SK.heal('야전 병원', 0.9, 60, 11, { aoe: 40 })], { hp: 0.5 }),
  fixer: cap('해결사', 'rogue', '돈만 주면 무슨 일이든 처리하는 뒷골목의 해결사.', L('#2a2a2a', '#c9c2b8', 'hood', 'dagger'),
    { name: '뒷거래', power: 0.02, types: { sabotage: 0.2, rescue: 0.2 }, cls: { rogue: 0.08 }, party: { gold: 0.15 } },
    [SK.melee('짧은 칼', 1.05, 0.7, { exec: 0.3 }), SK.melee('뒤치기', 2.0, 8, { dash: true, exec: 0.6 })]),
  veteran: cap('노병', 'warrior', '서른 번의 전쟁을 살아 돌아온 백발의 병사. 젊은 대원들이 그를 따른다.', L('#5a5a4a', '#c9c2b8', 'helmet', 'sword'),
    { name: '노병의 관록', power: 0.07, types: { defense: 0.1, warDefense: 0.1 } },
    [SK.melee('노련한 일격', 1.1, 1.0), SK.rally('노병의 호통', { atk: 0.2, def: 0.2, dur: 6 }, 50, 12)], { hp: 1 }),

  // ── 초반 영입 과제 대상 (6) ──
  windhunter: cap('바람 사냥꾼', 'archer', '바람을 읽고 사냥감을 쫓는 명사수. 궁수들을 이끄는 데 능하다.', L('#2a4a3a', '#a7d26a', 'band', 'bow'),
    { name: '사냥 신호', power: 0.03, cls: { archer: 0.15 }, party: { success: 0.04, days: -1 } },
    [SK.shot('바람 화살', 'arrow', 1.05, 100, 1.1), SK.shot('질풍 연사', 'arrow', 0.8, 100, 7, { hits: 4 })], { dex: 0.5 }),
  shadowlord: cap('그림자 두목', 'rogue', '뒷골목을 주름잡던 두목. 돈 냄새를 맡고, 어둠 속 일을 처리한다.', L('#1a1420', '#d9a441', 'hood', 'dagger'),
    { name: '밤의 계약', power: 0.03, cls: { rogue: 0.12 }, types: { sabotage: 0.2, rescue: 0.2, counterspy: 0.2 }, party: { gold: 0.18 } },
    [SK.melee('뒷골목 칼질', 1.05, 0.7, { exec: 0.4 }), SK.shot('독 묻은 투척', 'dagger', 1.2, 60, 7, { hits: 3 })]),
  bard: cap('음유 검객', 'rogue', '노래와 검을 함께 다루는 떠돌이 검객. 그의 노래가 들리면 대원들이 힘을 낸다.', L('#7a2a5a', '#f2c94c', 'hat', 'dagger'),
    { name: '행군가', power: 0.03, party: { success: 0.05, gold: 0.1, noMoraleLoss: true } },
    [SK.melee('춤추는 검', 1.0, 0.7), SK.rally('전투의 노래', { atk: 0.3, dur: 7 }, 60, 12)]),
  beastmaster: cap('야수 조련사', 'archer', '늑대 무리를 거느린 조련사. 사냥에서는 누구보다 빠르다.', L('#5a4a3a', '#d9a441', 'band', 'bow'),
    { name: '무리의 우두머리', power: 0.02, types: { hunt: 0.2 }, cls: { archer: 0.06, warrior: 0.06 } },
    [SK.shot('조련사의 활', 'arrow', 1.0, 90, 1.1), SK.melee('늑대 떼 돌격', 1.3, 9, { hits: 3, dash: true })], { str: 0.5 }),
  runesmith: cap('룬 대장장이', 'warrior', '망치로 룬을 새기는 대장장이 전사. 그가 손본 장비는 부서지지 않는다.', L('#6a4a2a', '#7fd6e8', 'helmet', 'mace'),
    { name: '룬 각인', power: 0.06, cls: { warrior: 0.08 }, party: { injury: 0.85 } },
    [SK.melee('룬 망치', 1.15, 1.05, { stun: 0.2 }), SK.rally('룬의 가호', { def: 0.3, atk: 0.15, dur: 8 }, 50, 13)], { hp: 1 }),
  pilgrim: cap('순례 기사', 'cleric', '맨발로 대륙을 걷는 순례 기사. 길 위의 사람들을 지키는 것이 그녀의 맹세다.', L('#c8b89a', '#3d5a9c', 'none', 'mace'),
    { name: '순례의 맹세', power: 0.03, types: { escort: 0.15 }, party: { death: 0.5 } },
    [SK.heal('순례자의 기도', 1.15, 70, 1.5), SK.melee('맨발의 심판', 1.4, 8, { aoe: 12 })], { str: 0.5 }),

  // ── 중반 영입 과제 대상 1 (6) ──
  spellblade: cap('마검사', 'mage', '검과 마법을 함께 다루는 이단의 기사. 마법사들의 힘을 한데 모은다.', L('#2a2a6a', '#7fd6e8', 'none', 'sword'),
    { name: '마력 공명', power: 0.04, cls: { mage: 0.15 }, types: { magic: 0.2 } },
    [SK.melee('마력검', 1.2, 1.0, { aoe: 8 }), SK.shot('비검', 'bolt', 1.6, 80, 8, { hits: 2 })], { str: 1 }),
  saintknight: cap('성광 기사', 'cleric', '빛의 맹세를 지키는 기사. 그가 있는 한 아무도 버려지지 않는다.', L('#e8e4d8', '#f2c94c', 'helmet', 'mace'),
    { name: '빛의 가호', power: 0.03, cls: { cleric: 0.1 }, party: { death: 0.3, injury: 0.75 } },
    [SK.heal('빛의 손길', 1.15, 70, 1.5), SK.melee('성광 일격', 1.6, 8, { aoe: 14, stun: 0.4 })], { str: 0.5, hp: 0.5 }),
  hexer: cap('저주술사', 'mage', '저주를 사고파는 상인 마녀. 그녀의 저주는 계약서보다 확실하다.', L('#3a1a3a', '#7ed37e', 'hat', 'staff'),
    { name: '저주 거래', power: 0.03, types: { sabotage: 0.2, counterspy: 0.2 }, cls: { mage: 0.1 } },
    [SK.shot('저주탄', 'curse', 1.15, 85, 1.6, { exec: 0.3 }), SK.shot('역병 저주', 'curse', 0.9, 90, 9, { aoe: 22, stun: 0.5 })]),
  liberator: cap('해방 검투사', 'warrior', '투기장의 쇠사슬을 끊고 나온 검투사. 갇힌 자들을 그냥 두지 않는다.', L('#7a4a2a', '#c9c2b8', 'none', 'sword'),
    { name: '쇠사슬을 끊은 자', power: 0.07, types: { rescue: 0.2 }, cls: { warrior: 0.06 } },
    [SK.melee('사슬 휘두르기', 1.05, 0.95, { aoe: 8 }), SK.melee('족쇄 부수기', 1.7, 8, { stun: 0.8 })], { str: 1 }),
  admiral: cap('퇴역 제독', 'archer', '자유 도시 함대를 이끌던 노제독. 바다 위의 전술을 땅에서도 쓴다.', L('#1a2a5a', '#f2c94c', 'hat', 'bow'),
    { name: '함대 지휘', power: 0.03, types: { escort: 0.15, battle: 0.1 }, party: { days: -1 } },
    [SK.shot('석궁 사격', 'bolt', 1.1, 100, 1.3), SK.shot('함포 지원', 'fire', 1.6, 120, 10, { aoe: 22 })], { int: 0.5 }),
  elfwarden: cap('엘프 숲지기', 'archer', '은빛 숲 순찰대를 이끄는 엘프. 숲의 허락 없이는 아무도 지나가지 못한다.', L('#2f6a3a', '#e8e4d8', 'band', 'bow'),
    { name: '숲의 수호대', power: 0.02, cls: { archer: 0.15 }, types: { explore: 0.15 }, party: { success: 0.03 } },
    [SK.shot('은잎 화살', 'arrow', 1.1, 110, 1.1), SK.shot('숲의 분노', 'arrow', 0.9, 110, 8, { hits: 4, stun: 0.3 })], { dex: 0.5 }),

  // ── 중반 영입 과제 대상 2 (6) ──
  warlord: cap('전쟁군주', 'warrior', '수많은 전쟁을 치른 지휘관. 세력 분쟁과 결전에서 진가를 발휘한다.', L('#5a3a1a', '#d6455d', 'helmet', 'sword'),
    { name: '군세 통솔', power: 0.03, types: { raid: 0.15, siege: 0.15, warDefense: 0.15, battle: 0.15 } },
    [SK.melee('전쟁 도끼', 1.1, 1.0), SK.rally('돌격 나팔', { atk: 0.3, dur: 6 }, 50, 11)], { hp: 0.5 }),
  khan: cap('초원의 칸', 'archer', '말 위에서 태어난 유목 군주. 빠르게 치고 빠지는 전쟁을 안다.', L('#8a5a2a', '#e8c86a', 'band', 'bow'),
    { name: '기마 돌격', power: 0.04, types: { raid: 0.15, battle: 0.15 }, cls: { archer: 0.08, warrior: 0.08 }, party: { days: -1 } },
    [SK.shot('기마 사격', 'arrow', 1.05, 95, 1.0), SK.melee('기마 돌격', 1.5, 8, { dash: true, stun: 0.6 })], { str: 0.5, hp: 0.5 }),
  siegemaster: cap('공성 기술자', 'archer', '성벽을 무너뜨리는 법을 아는 기술자. 쇠뇌와 투석기를 끌고 다닌다.', L('#5a4a3a', '#d9a441', 'helmet', 'bow'),
    { name: '공성 설계', power: 0.03, types: { siege: 0.25, battle: 0.1 } },
    [SK.shot('쇠뇌', 'bolt', 1.2, 110, 1.5), SK.shot('투석 사격', 'fire', 1.8, 130, 10, { aoe: 24 })], { str: 0.5, int: 0.5 }),
  inquisitorlord: cap('대심문관', 'cleric', '교단 심문소를 이끄는 냉혹한 사제. 이단과 첩자를 가려내는 데 실수가 없다.', L('#4a1a1a', '#f2c94c', 'hood', 'mace'),
    { name: '심문', power: 0.05, types: { counterspy: 0.25 }, party: { death: 0.6 } },
    [SK.heal('정화', 1.1, 70, 1.6), SK.shot('화형 선고', 'fire', 1.6, 80, 9, { aoe: 16, stun: 0.5 })], { int: 0.5 }),
  pirateking: cap('해적왕', 'rogue', '붉은 돛 함대의 주인. 약탈할 것이 있는 곳이면 어디든 간다.', L('#7a1a1a', '#1b1420', 'hat', 'dagger'),
    { name: '붉은 돛', power: 0.03, types: { raid: 0.15 }, party: { gold: 0.2 } },
    [SK.melee('커틀러스', 1.1, 0.75), SK.shot('갈고리 사슬', 'dagger', 1.3, 70, 8, { hits: 2, stun: 0.6 })], { str: 0.5 }),
  frostjarl: cap('서리 영주', 'warrior', '서리 협곡의 영주. 북부의 겨울처럼 무너지지 않는다.', L('#4a6a8a', '#e8eef2', 'helmet', 'sword'),
    { name: '겨울의 방벽', power: 0.06, types: { defense: 0.2, warDefense: 0.2 }, cls: { warrior: 0.06 } },
    [SK.melee('서리 도끼', 1.15, 1.05, { stun: 0.15 }), SK.melee('빙결 강타', 1.5, 9, { aoe: 18, stun: 0.8 })], { hp: 1 }),

  // ── 후반 영입 과제 대상 (6) ──
  dragonslayer: cap('용살자', 'warrior', '고룡의 비늘을 꿰뚫은 전설의 전사. 재앙 앞에서 물러선 적이 없다.', L('#6a1a14', '#f39c12', 'helmet', 'sword'),
    { name: '용의 목을 벤 자', power: 0.08, types: { hunt: 0.15 }, vsCalamity: 0.25 },
    [SK.melee('용살검', 1.25, 1.0), SK.melee('용의 목 베기', 2.4, 10, { dash: true, exec: 1.0 })], { str: 1.5 }),
  demonhunter: cap('마귀 사냥꾼', 'cleric', '마계의 문 너머까지 다녀왔다는 퇴마사. 죽음의 냄새를 맡는다.', L('#2a2a3a', '#c9c2b8', 'hood', 'mace'),
    { name: '퇴마의 인장', power: 0.06, types: { counterspy: 0.2 }, vsCalamity: 0.2, party: { death: 0.4 } },
    [SK.shot('은탄', 'bolt', 1.05, 80, 1.2), SK.heal('퇴마의 빛', 1.2, 70, 10, { aoe: 24, buff: { def: 0.25, dur: 5 } })], { str: 0.5, dex: 0.5 }),
  archmagus: cap('대현자', 'mage', '세상에 남은 마지막 대현자. 별을 떨어뜨리는 주문을 안다.', L('#1a1a4a', '#f2f2ff', 'hat', 'staff'),
    { name: '대현자의 가르침', power: 0.06, cls: { mage: 0.15 }, types: { magic: 0.2 }, vsCalamity: 0.15 },
    [SK.shot('비전 광선', 'bolt', 1.4, 100, 1.6, { hits: 2 }), SK.shot('별의 낙하', 'fire', 2.4, 110, 11, { aoe: 30 })], { int: 1.5 }),
  lightbearer: cap('빛의 사도', 'cleric', '새벽을 가져온다는 예언의 사도. 그녀 곁에서는 죽음도 머뭇거린다.', L('#f2ecd8', '#f39c12', 'none', 'mace'),
    { name: '새벽의 약속', power: 0.04, vsCalamity: 0.15, party: { death: 0.2, injury: 0.6 } },
    [SK.heal('빛의 숨결', 1.4, 80, 1.4, { aoe: 10 }), SK.heal('새벽의 기적', 2.0, 90, 12, { aoe: 50, buff: { def: 0.3, dur: 5 } })], { int: 1, hp: 0.5 }),
  shadowqueen: cap('밤의 여왕', 'rogue', '대륙 모든 그림자 길드의 정점. 그녀가 원하면 왕도 밤에 잠들지 못한다.', L('#1a0a2a', '#d6455d', 'hood', 'dagger'),
    { name: '밤의 지배', power: 0.04, types: { sabotage: 0.2 }, vsCalamity: 0.1, party: { gold: 0.2, great: 1.4 } },
    [SK.melee('밤의 칼날', 1.2, 0.65, { exec: 0.5 }), SK.melee('그림자 난무', 1.3, 8, { hits: 4, dash: true })], { dex: 1.5 }),
  titan: cap('거인의 피', 'warrior', '거인족의 피를 이은 전사. 그가 땅을 치면 전열이 통째로 무너진다.', L('#5a3a2a', '#e8c86a', 'none', 'mace'),
    { name: '거인의 위압', power: 0.12, types: { hunt: 0.1 }, vsCalamity: 0.1 },
    [SK.melee('거인의 주먹', 1.35, 1.15, { stun: 0.3 }), SK.melee('대지 강타', 1.8, 10, { aoe: 26, stun: 1.0 })], { str: 1, hp: 2 }),
};
Object.values(CAPTAIN_CLASSES).forEach((c) => { c.lead.desc = describeLead(c.lead); });
const CAPTAIN_KEYS = Object.keys(CAPTAIN_CLASSES);

// ───────── 특별 용병: 고유 직업을 가진 대원 ─────────
// 대원처럼 아무 용병단에나 들어가지만 승급 대신 '이야기'로 성장한다.
// 액티브 2개(기본기 + 특기) + 고유 패시브(fx). 장을 마칠수록 레벨 상한·성장률·패시브가 강해진다.
const HERO_CAPS = [15, 22, 30, 40];           // 완료한 장 수별 레벨 상한
const HERO_GROWTH = [0.62, 0.75, 0.88, 1.0];  // 완료한 장 수별 성장률 배율
const HERO_CLASSES = {
  silverscout: { name: '은빛 순찰자', style: 'archer', skill: '숲의 눈',
    base: { str: 6, dex: 13, int: 6, hp: 34 }, growth: { str: 1.6, dex: 3.8, int: 1.2, hp: 7 },
    outfit: '#2f6a4a', accent: '#e8e4d8', headgear: 'band', weapon: 'bow',
    fx: { self: { types: { hunt: 0.2, explore: 0.2, escort: 0.2 } }, party: { success: 0.04 } },
    acts: [SK.shot('은빛 화살', 'arrow', 1.05, 100, 1.1), SK.shot('숲의 비', 'arrow', 0.9, 100, 8, { hits: 4 })] },
  exsaint: { name: '파문 성녀', style: 'cleric', skill: '들판의 미사',
    base: { str: 5, dex: 5, int: 13, hp: 40 }, growth: { str: 1.0, dex: 1.2, int: 3.8, hp: 9 },
    outfit: '#f2ecd8', accent: '#d6455d', headgear: 'none', weapon: 'mace',
    fx: { party: { injury: 0.6, death: 0.5 } },
    acts: [SK.heal('들판의 기도', 1.2, 75, 1.5), SK.heal('성녀의 기적', 1.6, 80, 10, { aoe: 30 })] },
  outlaw: { name: '가면 의적', style: 'rogue', skill: '의적의 신호',
    base: { str: 7, dex: 13, int: 7, hp: 32 }, growth: { str: 1.6, dex: 3.8, int: 1.6, hp: 6 },
    outfit: '#2a1a3a', accent: '#e8e4d8', headgear: 'hood', weapon: 'dagger',
    fx: { self: { types: { rescue: 0.25, sabotage: 0.25 } }, party: { gold: 0.15 } },
    acts: [SK.melee('가면의 칼날', 1.05, 0.7, { exec: 0.3 }), SK.shot('연막과 단검', 'dagger', 1.2, 60, 8, { aoe: 14, stun: 0.8 })] },
  pitchampion: { name: '투기장 패왕', style: 'warrior', skill: '투기장의 함성',
    base: { str: 14, dex: 6, int: 2, hp: 50 }, growth: { str: 4.0, dex: 1.4, int: 0.3, hp: 11 },
    outfit: '#7a2418', accent: '#f2c94c', headgear: 'none', weapon: 'sword',
    fx: { self: { all: 0.15 } },
    acts: [SK.melee('투기장 일격', 1.15, 0.95), SK.melee('피의 함성', 1.0, 9, { aoe: 16, selfBuff: { atk: 0.4, dur: 5 } })] },
  towerheir: { name: '마탑 계승자', style: 'mage', skill: '금지된 강의',
    base: { str: 3, dex: 6, int: 15, hp: 30 }, growth: { str: 0.6, dex: 1.2, int: 4.2, hp: 6 },
    outfit: '#3a1a5a', accent: '#f2d24b', headgear: 'hat', weapon: 'staff',
    fx: { self: { types: { magic: 0.3, hunt: 0.15 } } },
    acts: [SK.shot('비전 화살', 'fire', 1.25, 90, 1.7, { aoe: 10 }), SK.shot('금지된 주문', 'fire', 2.2, 95, 10, { aoe: 26 })] },
  corsair: { name: '해적 선장', style: 'archer', skill: '갑판의 호령',
    base: { str: 8, dex: 11, int: 6, hp: 38 }, growth: { str: 2.0, dex: 3.2, int: 1.2, hp: 8 },
    outfit: '#1a2a4a', accent: '#d6455d', headgear: 'hat', weapon: 'bow',
    fx: { self: { types: { escort: 0.2 } }, party: { gold: 0.1, days: -1 } },
    acts: [SK.shot('권총 사격', 'bolt', 1.1, 85, 1.2), SK.shot('포격 지원', 'fire', 1.5, 110, 10, { aoe: 20, stun: 0.5 })] },
  fallencommander: { name: '몰락 기사단장', style: 'warrior', skill: '기사단 전법',
    base: { str: 12, dex: 5, int: 7, hp: 54 }, growth: { str: 3.2, dex: 1.0, int: 1.6, hp: 11 },
    outfit: '#c9ced6', accent: '#3d5a9c', headgear: 'helmet', weapon: 'sword',
    fx: { self: { types: { defense: 0.25, warDefense: 0.25, battle: 0.25 } }, party: { injury: 0.8 } },
    acts: [SK.melee('기사의 검', 1.05, 1.0), SK.rally('방진 명령', { def: 0.35, dur: 6 }, 45, 11)] },
};
