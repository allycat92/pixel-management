// 게임 핵심: 상태, 저장, 길드 등급·시설, 단원(용병), 장비·상점, 하루 진행
// 용병단은 company.js, 세력·영토는 faction.js, 의뢰는 contract.js 에서 Game 에 기능을 더한다.
'use strict';

const SAVE_KEY = 'pixel-guild-save-v4';
const SAVE_VERSION = 4;

const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const STORY_EXPIRES = 99999;

function josa(word, withBatchim, withoutBatchim) {
  const last = String(word).match(/[가-힣0-9](?=[^가-힣0-9]*$)/)?.[0];
  if (!last) return withoutBatchim;
  const hasBatchim = /[0-9]/.test(last)
    ? '013678'.includes(last)
    : (last.charCodeAt(0) - 0xac00) % 28 !== 0;
  return hasBatchim ? withBatchim : withoutBatchim;
}
const FRIEND_REL = 30, RIVAL_REL = -20;
// 함께 다니면 사이가 틀어지는 특성 조합
const TRAIT_CLASH = [['brave', 'coward'], ['greedy', 'diligent'], ['genius', 'lazy']];

const Game = {
  state: null,
  listeners: [],

  onChange(fn) { this.listeners.push(fn); },
  emit() { this.listeners.forEach((fn) => fn()); },

  // ───────── 초기화 / 저장 ─────────
  newGame() {
    this.state = {
      version: SAVE_VERSION,
      squadRule: 1, // 3~4인 용병단 규칙으로 만든 저장 (normalizeCompanies 참고)
      guildName: '은빛 늑대 길드',
      day: 1, gold: 450, rep: 0, nextId: 1,
      mercs: [], recruits: [], companies: [], market: [],
      contracts: [], missions: [], log: [],
      facilities: { dorm: 0, barracks: 0, training: 0, infirmary: 0, tavern: 0, board: 0, forge: 0 },
      stats: { completed: 0, failed: 0, fallen: 0 },
      inventory: [], shop: [], herbs: 1,
      heroes: {}, branches: {}, provClears: {}, bossDefeated: {},
      settings: { battle: true },
      pendingReports: [], over: null, won: false,
    };
    const s = this.state;
    this.initWorld();
    // 시작 용병단: 대원 2명 (용병대장과 합쳐 3명). 첫 용병대장은 후보 셋 중에서 고른다.
    const units = ['warrior', 'cleric'].map((cls) => { const m = this.makeUnit(cls, 1); s.mercs.push(m); return m; });
    const co = this.createCompany(true);
    units.forEach((m) => { m.companyId = co.id; });
    co.cohesion = 30;
    this.initCaptains();
    this.refreshRecruits();
    this.refreshMarket();
    this.refreshShop();
    this.fillContracts(true);
    this.log('길드가 문을 열었습니다! 용병단을 꾸려 의뢰를 맡고, 세력들 사이에서 길드의 이름을 높이세요.', 'good');
  },

  save() {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(this.state)); return true; } catch (e) { return false; }
  },
  load() {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) return false;
      const st = JSON.parse(raw);
      if (st.version !== SAVE_VERSION) return false;
      this.state = st;
      this.normalizeCompanies(); // 용병단이 4~9명이던 저장: 정원을 넘는 대원은 예비 인원으로
      return true;
    } catch (e) { return false; }
  },
  clearSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* 무시 */ } },

  log(text, kind = '') {
    this.state.log.unshift({ day: this.state.day, text, kind });
    if (this.state.log.length > 200) this.state.log.length = 200;
  },

  // ───────── 길드 등급 / 시설 ─────────
  rankIndex() {
    let idx = 0;
    RANKS.forEach((r, i) => { if (this.state.rep >= r.rep) idx = i; });
    return idx;
  },
  rank() { return RANKS[this.rankIndex()]; },
  nextRank() { return RANKS[this.rankIndex() + 1] || null; },
  bedsUsed() { return this.state.mercs.filter((m) => !this.isCaptain(m)).length; },
  capacity() { return 6 + this.state.facilities.dorm * 3; },
  facilityCost(key) {
    const lv = this.state.facilities[key];
    return Math.round(FACILITIES[key].baseCost * Math.pow(1.8, lv));
  },
  upgrade(key) {
    const s = this.state, f = FACILITIES[key];
    if (s.facilities[key] >= f.max) return;
    const cost = this.facilityCost(key);
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    s.gold -= cost;
    s.facilities[key]++;
    this.log(`${f.name}${josa(f.name, '을', '를')} ${s.facilities[key]}단계로 증축했습니다. (-${cost} 금화)`, 'good');
    if (key === 'board') this.fillContracts(true);
    if (key === 'forge') this.refreshShop();
    this.emit();
  },

  // ───────── 용병: 대장과 대원 ─────────
  uniqueMercName() {
    const usedNames = new Set(this.state ? [...this.state.mercs, ...this.state.recruits].map((m) => m.name) : []);
    Object.values(HEROES).forEach((h) => usedNames.add(h.name));
    Object.values(CAPTAINS).forEach((c) => usedNames.add(c.name));
    let name = pick(NAMES), tries = 0;
    while (usedNames.has(name) && tries++ < 40) name = pick(NAMES);
    return name;
  },
  baseMerc(role, cls, stats) {
    return {
      id: this.state ? this.state.nextId++ : 0,
      name: this.uniqueMercName(), role, cls, level: 1, exp: 0,
      str: stats.str, dex: stats.dex, int: stats.int, maxHp: stats.hp,
      trait: 'none', grow: { str: 0, dex: 0, int: 0, hp: 0 },
      status: 'idle', injury: 0, missionId: null, quests: 0, bond: 0, companyId: null,
      fatigue: 0, morale: rand(60, 75), rel: {}, lastQuest: this.state ? this.state.day : 1,
      equip: { weapon: null, armor: null, trinket: null },
      look: { cls, skin: pick(SKIN_TONES), hair: pick(HAIR_COLORS), longHair: Math.random() < 0.4 },
    };
  },
  // 용병 유닛: 같은 직업·레벨이면 능력치가 같다
  makeUnit(cls, level = 1) {
    const m = this.baseMerc('unit', cls, CLASSES[cls].base);
    for (let i = 1; i < level; i++) this.levelUp(m, true);
    return m;
  },
  makeMerc(cls, level) { return this.makeUnit(cls, level); },
  // 용병대장: 고유 직업, 높은 성장성
  makeCaptain(cap, level = 1) {
    const cc = CAPTAIN_CLASSES[cap];
    const m = this.baseMerc('captain', cc.style, cc.base);
    m.cap = cap;
    m.trait = pick(TRAIT_POOL);
    m.look.cap = cap;
    for (let i = 1; i < level; i++) this.levelUp(m, true);
    return m;
  },
  isCaptain(m) { return m && m.role === 'captain'; },

  expToNext(m) { return m.level * 60 + m.level * m.level * 6; },
  heroCh(m) { const hs = m.hero && this.state && this.state.heroes[m.hero]; return hs ? Math.min(hs.ch, 3) : 0; },
  levelCap(m) {
    if (this.isCaptain(m)) return CAPTAIN_CAP;
    if (m.hcls) return HERO_CAPS[this.heroCh(m)];
    return UNIT_TIERS[this.classTier(m)].cap;
  },
  classTier(m) { return m.master ? 2 : m.adv ? 1 : 0; },
  atCap(m) { return m.level >= this.levelCap(m); },
  growthOf(m) {
    if (this.isCaptain(m)) return { ...CAPTAIN_CLASSES[m.cap].growth };
    if (m.hcls) {
      // 특별 용병: 이야기를 진행할수록 성장률이 대장 수준으로 오른다
      const k = HERO_GROWTH[this.heroCh(m)], g = {};
      Object.entries(HERO_CLASSES[m.hcls].growth).forEach(([key, v]) => { g[key] = v * k; });
      return g;
    }
    const g = { ...CLASSES[m.cls].growth };
    [m.adv && ADV_CLASSES[m.adv], m.master && MASTER_CLASSES[m.master]].filter(Boolean)
      .forEach((c) => Object.entries(c.growth).forEach(([k, v]) => { g[k] = (g[k] || 0) + v; }));
    return g;
  },

  levelUp(m, silent) {
    const g = this.growthOf(m);
    m.level++;
    m.grow = m.grow || { str: 0, dex: 0, int: 0, hp: 0 };
    ['str', 'dex', 'int', 'hp'].forEach((k) => {
      const key = k === 'hp' ? 'maxHp' : k;
      let gain;
      if (this.isCaptain(m)) {
        // 대장: 성장률이 보장되고, 운이 좋으면 더 오른다
        gain = Math.floor(g[k]) + (Math.random() < g[k] % 1 ? 1 : 0) + (Math.random() < 0.15 ? 1 : 0);
      } else {
        // 대원: 직업 성장률대로 정확히 오른다
        m.grow[k] += g[k] || 0;
        gain = Math.floor(m.grow[k]);
        m.grow[k] -= gain;
      }
      m[key] += gain;
    });
    if (!silent) {
      this.changeMorale(m, 5);
      const note = this.canPromote(m) ? ' 전직할 수 있습니다!' : this.canMaster(m) ? ' 최상급 직업으로 전직할 수 있습니다!'
        : this.isCaptain(m) && m.level === CAPTAIN_AWAKEN ? ` 지휘가 무르익었습니다! (「${CAPTAIN_CLASSES[m.cap].lead.name}」 효과 ×1.5)` : '';
      this.log(`${m.name}${josa(m.name, '이', '가')} 레벨 ${m.level}이 되었습니다!${note}`, 'good');
    }
  },

  // ───────── 직업 / 전직 ─────────
  className(m) {
    if (this.isCaptain(m)) return CAPTAIN_CLASSES[m.cap].name;
    if (m.hcls) return HERO_CLASSES[m.hcls].name;
    return m.master ? MASTER_CLASSES[m.master].name : m.adv ? ADV_CLASSES[m.adv].name : CLASSES[m.cls].name;
  },
  // 대원의 현재 직업 (기본/상급/최상급): 액티브 스킬 하나와 의뢰 효과(fx)
  currentClass(m) {
    if (m.master) return { key: m.master, ...MASTER_CLASSES[m.master] };
    if (m.adv) return { key: m.adv, ...ADV_CLASSES[m.adv] };
    const C = CLASS_SKILLS[m.cls];
    return { key: m.cls, name: CLASSES[m.cls].name, skill: C.name, b: C.b, fx: C.fx };
  },
  // 의뢰 판정에 쓰는 스킬 효과 목록
  //  범용 대원: 현재 직업의 액티브 스킬 효과 하나
  //  특별 용병: 고유 패시브 (장을 마칠 때마다 25%씩 강해진다)
  //  대장: 없음 (지휘는 용병단 단위로 따로 계산)
  classChain(m) {
    if (this.isCaptain(m)) return [];
    if (m.hcls) {
      const H = HERO_CLASSES[m.hcls];
      return [{ key: `hero:${m.hcls}`, name: H.name, skill: H.skill, fx: H.fx, scale: 1 + this.heroCh(m) * 0.25 }];
    }
    const c = this.currentClass(m);
    return [{ key: c.key, name: c.name, skill: c.skill, fx: c.fx }];
  },
  // 화면에 보여줄 스킬: 액티브(전투 + 의뢰 효과)와 패시브
  skillsOf(m) {
    if (this.isCaptain(m)) {
      const C = CAPTAIN_CLASSES[m.cap], k = this.leadScale(m);
      return { actives: C.acts.map((b) => ({ name: b.name, battle: describeBattle(b) })),
        passive: { name: C.lead.name, desc: `지휘: ${C.lead.desc}${k > 1 ? ' (×1.5)' : ` — Lv.${CAPTAIN_AWAKEN}부터 ×1.5`}`, lead: true } };
    }
    if (m.hcls) {
      const H = HERO_CLASSES[m.hcls], sc = 1 + this.heroCh(m) * 0.25;
      return { actives: H.acts.map((b) => ({ name: b.name, battle: describeBattle(b) })),
        passive: { name: H.skill, desc: `${describeFx(H.fx)}${sc > 1 ? ` (효과 ×${sc})` : ''}` } };
    }
    const c = this.currentClass(m);
    return { actives: [{ name: c.skill, battle: describeBattle(c.b), mission: describeFx(c.fx) }], passive: null };
  },
  // 전투에서 쓰는 액티브 스킬 [기본기, 특기?]
  battleSkillsOf(m) {
    if (this.isCaptain(m)) return CAPTAIN_CLASSES[m.cap].acts;
    if (m.hcls) return HERO_CLASSES[m.hcls].acts;
    return [this.currentClass(m).b];
  },
  canPromote(m) { return !this.isCaptain(m) && !m.hcls && !m.adv && m.level >= PROMOTE_LEVEL; },
  canMaster(m) { return !this.isCaptain(m) && !m.hcls && m.adv && !m.master && m.level >= MASTER_LEVEL; },
  promote(mercId, key) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === mercId);
    const opt = m && !this.isCaptain(m) && PROMOTIONS[m.cls].find((p) => p.key === key);
    if (!m || !opt || !this.canPromote(m) || m.status === 'quest') return;
    if (s.gold < PROMOTE_COST) return this.toast('금화가 부족합니다.');
    s.gold -= PROMOTE_COST;
    this.applyPromotion(m, key);
    this.changeMorale(m, 10);
    this.log(`${m.name}${josa(m.name, '이', '가')} ${opt.name}(으)로 승급했습니다! 스킬 「${opt.skill}」, 레벨 상한 ${this.levelCap(m)}. (-${PROMOTE_COST} 금화)`, 'good');
    this.emit();
  },
  promoteMaster(mercId, key) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === mercId);
    const mc = m && m.adv && MASTERS[m.adv].find((x) => x.key === key);
    if (!m || !mc || !this.canMaster(m) || m.status === 'quest') return;
    if (s.gold < MASTER_COST) return this.toast('금화가 부족합니다.');
    s.gold -= MASTER_COST;
    this.applyMaster(m, key);
    this.changeMorale(m, 15);
    this.log(`${m.name}${josa(m.name, '이', '가')} 최상급 직업 ${mc.name}에 올랐습니다! 스킬 「${mc.skill}」, 레벨 상한 ${this.levelCap(m)}. (-${MASTER_COST} 금화)`, 'good');
    this.emit();
  },
  applyPromotion(m, key) {
    const opt = ADV_CLASSES[key];
    m.adv = key;
    m.look = { ...m.look, adv: key };
    Object.entries(opt.bonus).forEach(([k, v]) => { m[k] += v; });
  },
  applyMaster(m, key) {
    const mc = MASTER_CLASSES[key];
    m.master = key;
    m.look = { ...m.look, master: key };
    Object.entries(mc.bonus).forEach(([k, v]) => { m[k] += v; });
  },

  // 대장의 지휘: 레벨 20부터 1.5배
  leadOf(m) { return this.isCaptain(m) ? CAPTAIN_CLASSES[m.cap].lead : null; },
  leadScale(m) { return m.level >= CAPTAIN_AWAKEN ? 1.5 : 1; },

  // ───────── 컨디션: 피로 / 사기 / 관계 ─────────
  changeMorale(m, d) { m.morale = clamp(Math.round((m.morale ?? 65) + d), 0, 100); },
  moraleState(m) {
    if (m.morale >= 80) return { label: '의욕적', cls: 'm-high', mul: 1.1 };
    if (m.morale >= 45) return { label: '보통', cls: 'm-mid', mul: 1 };
    if (m.morale >= 25) return { label: '불만', cls: 'm-low', mul: 0.92 };
    return { label: '절망', cls: 'm-worst', mul: 0.8 };
  },
  fatigueState(m) {
    if (m.fatigue >= 80) return { label: '탈진', cls: 'f-worst', mul: 0.75 };
    if (m.fatigue >= 50) return { label: '피곤', cls: 'f-tired', mul: 0.9 };
    return { label: '양호', cls: 'f-fresh', mul: 1 };
  },
  rel(a, b) { return (a.rel && a.rel[b.id]) || 0; },
  addRel(a, b, d) {
    a.rel = a.rel || {}; b.rel = b.rel || {};
    const v = clamp(this.rel(a, b) + d, -100, 100);
    a.rel[b.id] = v; b.rel[a.id] = v;
  },
  friendsOf(m) { return this.state.mercs.filter((x) => x.id !== m.id && this.rel(m, x) >= FRIEND_REL); },
  rivalsOf(m) { return this.state.mercs.filter((x) => x.id !== m.id && this.rel(m, x) <= RIVAL_REL); },
  traitsClash(a, b) { return TRAIT_CLASH.some(([x, y]) => (a.trait === x && b.trait === y) || (a.trait === y && b.trait === x)); },

  feastCost() { return 20 + 15 * this.state.mercs.filter((m) => m.status !== 'quest').length; },
  feastReady() { return this.state.day - (this.state.lastFeast ?? -99) >= 7; },
  feast() {
    const s = this.state;
    if (!this.feastReady()) return this.toast('연회는 일주일에 한 번만 열 수 있습니다.');
    const cost = this.feastCost();
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    const present = s.mercs.filter((m) => m.status !== 'quest');
    if (!present.length) return this.toast('연회에 참석할 단원이 없습니다.');
    s.gold -= cost;
    s.lastFeast = s.day;
    present.forEach((m) => { this.changeMorale(m, 15); m.fatigue = Math.max(0, m.fatigue - 15); });
    for (let i = 0; i < present.length; i++) for (let j = i + 1; j < present.length; j++) this.addRel(present[i], present[j], 4);
    this.log(`길드 홀에서 연회를 열었습니다! 단원 ${present.length}명의 사기가 오르고 피로가 풀렸습니다. (-${cost} 금화)`, 'good');
    this.emit();
  },

  // 레벨업 했으면 true
  gainExp(m, amount) {
    if (m.trait === 'genius') amount = Math.round(amount * 1.5);
    m.exp += amount;
    let leveled = false;
    while (m.exp >= this.expToNext(m)) {
      if (this.atCap(m)) { m.exp = this.expToNext(m) - 1; break; } // 레벨 상한: 전직해야 더 자란다
      m.exp -= this.expToNext(m);
      this.levelUp(m);
      leveled = true;
    }
    return leveled;
  },

  // 장비 포함 능력치
  equipBonus(m, stat) {
    const key = stat === 'maxHp' ? 'hp' : stat;
    return Object.values(m.equip || {}).reduce((sum, it) => sum + (it && it.bonus[key] ? it.bonus[key] : 0), 0);
  },
  eff(m, stat) { return m[stat] + this.equipBonus(m, stat); },

  wage(m) {
    const L = m.level;
    let w = (this.isCaptain(m) ? 20 + L * 12 + L * L * 0.45 : 8 + L * 7 + L * L * 0.3) * (this.perk && this.state && this.perk('crown') ? 0.9 : 1);
    if (m.trait === 'greedy') w *= 1.3;
    if (m.trait === 'diligent') w *= 0.8;
    return Math.round(w);
  },
  hireCost(m) { return this.wage(m) * (m.hero || m.elite ? 4 : m.level > 1 ? 3 : 2); },
  // 대원 모집: 직업을 골라 신병(Lv.1) 또는 숙련병으로 뽑는다
  veteranLevel() {
    return clamp(2 + this.state.facilities.tavern + Math.floor(this.rankIndex() * 1.2) + (this.perk('north') ? 2 : 0), 2, UNIT_TIERS[0].cap);
  },
  unitHireCost(cls, veteran) { return this.hireCost({ role: 'unit', cls, level: veteran ? this.veteranLevel() : 1, trait: 'none' }); },
  hireUnit(cls, veteran) {
    const s = this.state;
    if (!CLASSES[cls]) return;
    if (this.bedsUsed() >= this.capacity()) return this.toast('숙소가 가득 찼습니다. 숙소를 증축하세요.');
    const cost = this.unitHireCost(cls, veteran);
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    s.gold -= cost;
    const m = this.makeUnit(cls, veteran ? this.veteranLevel() : 1);
    s.mercs.push(m);
    this.log(`${veteran ? '숙련' : '신병'} ${CLASSES[cls].name} ${m.name}(Lv.${m.level})${josa(m.name, '을', '를')} 모집했습니다. 예비 인원으로 대기합니다. (-${cost} 금화)`);
    this.emit();
    return m;
  },

  // party를 넘기면 전우/불화/지휘 효과까지 반영
  power(m, type, party) {
    const w = type ? QUEST_TYPES[type].weights : { str: 1, dex: 1, int: 1, hp: 0.1 };
    let p = this.eff(m, 'str') * w.str + this.eff(m, 'dex') * w.dex + this.eff(m, 'int') * w.int
      + this.eff(m, 'maxHp') * w.hp + m.level * 3;
    if (m.trait === 'brave') p *= 1.1;
    if (m.trait === 'coward') p *= 0.9;
    if (m.trait === 'berserker') p *= 1.25;
    if (m.trait === 'arcane') p *= type === 'magic' ? 1.35 : 1.1;
    if (m.trait === 'royalguard' && ['defense', 'warDefense', 'battle'].includes(type)) p *= 1.2;
    if (m.trait === 'northknight') p *= 1.05;
    if (m.trait === 'warcry') p *= 1.15;
    if (m.awakened) p *= 1.15;
    // 직업 계통 스킬
    let bonus = 0;
    this.classChain(m).forEach((c) => {
      const self = c.fx && c.fx.self;
      if (!self) return;
      bonus += ((self.all || 0) + ((type && self.types && self.types[type]) || 0)) * (c.scale || 1);
    });
    p *= 1 + bonus;
    // 컨디션
    p *= this.moraleState(m).mul * this.fatigueState(m).mul;
    if (party) {
      const others = party.filter((x) => x.id !== m.id);
      const friends = others.filter((x) => this.rel(m, x) >= FRIEND_REL).length;
      const rivals = others.filter((x) => this.rel(m, x) <= RIVAL_REL).length;
      p *= (1 + 0.08 * Math.min(friends, 2)) * Math.pow(0.9, rivals);
      if (party.some((x) => x.trait === 'commander')) p *= 1.08;
    }
    return Math.round(p);
  },

  // 파티 전체에 걸리는 직업·특성 효과
  partyMods(party) {
    const has = (f) => party.some(f);
    const mods = { success: 0, injury: 1, death: 1, gold: 1, great: 1, greatGold: 1, days: 0, noDisaster: false, healHalf: false, loot: 0, noMoraleLoss: false };
    // 직업 계통 효과 (같은 직업은 한 번만)
    const applied = new Set();
    const applyFx = (fx, scale = 1) => {
      if (!fx) return;
      if (fx.success) mods.success += fx.success * scale;
      if (fx.injury != null) mods.injury *= 1 - (1 - fx.injury) * scale;
      if (fx.death != null) mods.death *= Math.max(0, 1 - (1 - fx.death) * scale);
      if (fx.gold) mods.gold += fx.gold * scale;
      if (fx.great) mods.great *= 1 + (fx.great - 1) * scale;
      if (fx.greatGold) mods.greatGold += fx.greatGold * scale;
      if (fx.days) mods.days += fx.days;
      if (fx.noDisaster) mods.noDisaster = true;
      if (fx.healHalf) mods.healHalf = true;
      if (fx.noMoraleLoss) mods.noMoraleLoss = true;
      if (fx.loot) mods.loot = Math.max(mods.loot, fx.loot);
    };
    party.forEach((m) => {
      this.classChain(m).forEach((c) => {
        if (applied.has(c.key) || !c.fx || !c.fx.party) return;
        applied.add(c.key);
        applyFx(c.fx.party, c.scale || 1);
      });
      const lead = this.leadOf(m);
      if (lead && lead.party) applyFx(lead.party, this.leadScale(m));
    });
    mods.days = Math.max(-2, mods.days);
    if (has((m) => m.trait === 'lucky')) mods.success += 0.05;
    if (has((m) => m.trait === 'hawkeye')) mods.success += 0.08;
    if (has((m) => m.trait === 'saint')) { mods.death = 0; mods.injury *= 0.7; }
    if (has((m) => m.trait === 'greedy')) mods.gold += 0.1;
    if (has((m) => m.trait === 'shadow')) mods.gold += 0.25;
    if (has((m) => m.trait === 'captain')) { mods.gold += 0.15; mods.noMoraleLoss = true; }
    if (has((m) => m.trait === 'broker')) mods.gold += 0.1;
    if (has((m) => m.trait === 'blessed')) mods.death *= 0.5;
    if (has((m) => m.trait === 'sylvan')) mods.success += 0.05;
    return mods;
  },

  hire(id) {
    const s = this.state;
    const m = s.recruits.find((r) => r.id === id);
    if (!m) return;
    if (!this.isCaptain(m) && this.bedsUsed() >= this.capacity()) return this.toast('숙소가 가득 찼습니다. 숙소를 증축하세요.');
    const cost = this.hireCost(m);
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    s.gold -= cost;
    s.recruits = s.recruits.filter((r) => r.id !== id);
    m.companyId = null;
    s.mercs.push(m);
    if (m.hero) {
      s.heroes[m.hero].hired = true;
      this.log(`특별 용병 「${m.title}」 ${m.name}${josa(m.name, '이', '가')} 길드에 합류했습니다! 함께 의뢰를 완수하면 이야기가 이어집니다. (-${cost} 금화)`, 'good');
      // 특별 용병의 서사는 영입한 순간부터 시작된다
      s.pendingReports.push({ special: 'dialog', hero: m.hero, title: `${m.title} ${m.name}`, lines: HEROES[m.hero].intro,
        foot: `이야기를 진행할수록 레벨 상한(${HERO_CAPS.join('→')})과 성장률, 고유 스킬이 강해집니다.` });
    } else if (this.isCaptain(m)) {
      this.log(`용병대장 ${m.name}(${this.className(m)})${josa(m.name, '을', '를')} 영입했습니다. 용병단을 맡기세요. (-${cost} 금화)`, 'good');
    } else {
      this.log(`${this.className(m)} ${m.name}${josa(m.name, '을', '를')} 고용했습니다. 예비 인원으로 대기합니다. (-${cost} 금화)`);
    }
    this.emit();
  },

  // 단원이 길드를 떠날 때 공통 처리 (장비 회수, 용병단에서 빠짐, 특별 용병은 모집소로)
  removeMerc(m, reason, kind = '') {
    const s = this.state;
    this.returnEquipment(m);
    this.leaveCompany(m, 10);
    s.mercs = s.mercs.filter((x) => x.id !== m.id);
    if (this.isCaptain(m) && s.captains && s.captains[m.cap]) s.captains[m.cap].status = 'lost';
    if (m.hero && !s.heroes[m.hero].dead) {
      s.heroes[m.hero].hired = false;
      m.status = 'idle'; m.injury = 0; m.morale = 55; m.companyId = null;
      s.recruits.unshift(m);
    }
    this.log(`${m.name}${josa(m.name, '이', '가')} ${reason}`, kind);
  },

  returnEquipment(m) {
    Object.keys(m.equip).forEach((slot) => {
      if (m.equip[slot]) { this.state.inventory.push(m.equip[slot]); m.equip[slot] = null; }
    });
  },

  dismiss(id) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === id);
    if (!m || m.status === 'quest') return;
    this.removeMerc(m, '길드를 떠났습니다.');
    this.emit();
  },

  // 모집소의 개인 지원자: 특별 용병과 세력 정예만 남는다 (대장은 서사로, 대원은 직업을 골라 모집)
  refreshRecruits() {
    const s = this.state;
    s.recruits = s.recruits.filter((r) => r.hero || r.elite);
  },

  // ───────── 장비 / 상점 ─────────
  makeItem(base, tier) {
    const b = ITEM_BASES[base], t = TIERS[tier];
    const bonus = {};
    let anyStat = null;
    Object.entries(b.bonus).forEach(([k, v]) => {
      const stat = k === 'any' ? (anyStat = pick(['str', 'dex', 'int'])) : k;
      bonus[stat] = (bonus[stat] || 0) + Math.max(1, Math.round(v * t.mul * (0.9 + Math.random() * 0.2)));
    });
    const name = base === 'ring' ? `${t.name} ${STAT_NAMES[anyStat]}의 반지` : `${t.name} ${b.name}`;
    return { id: this.state.nextId++, base, slot: b.slot, tier, name, bonus, price: Math.round(t.price * (0.9 + Math.random() * 0.2)) };
  },

  makeUniqueItem(def) {
    return { id: this.state.nextId++, base: def.base, slot: ITEM_BASES[def.base].slot, tier: 5, name: def.name, bonus: { ...def.bonus }, price: 1500, unique: true };
  },

  shopMaxTier() {
    return clamp(1 + Math.floor(this.rankIndex() * 0.6) + (this.state.facilities.forge >= 3 ? 1 : 0), 1, 5);
  },
  shopPrice(item) { return Math.round(item.price * (1 - this.state.facilities.forge * 0.04 - (this.perk('cities') ? 0.15 : 0))); },
  sellPrice(item) { return Math.round(item.price * 0.4); },

  refreshShop() {
    const s = this.state;
    const maxTier = this.shopMaxTier();
    const count = 4 + s.facilities.forge;
    s.shop = [];
    // 단원 직업에 맞는 무기를 하나는 꼭 진열
    const classes = s.mercs.map((m) => m.cls);
    for (let i = 0; i < count; i++) {
      const base = i === 0 && classes.length ? CLASS_WEAPON[pick(classes)] : pick(Object.keys(ITEM_BASES));
      const tier = clamp(rand(maxTier - 1, maxTier), 1, 5);
      s.shop.push(this.makeItem(base, tier));
    }
  },

  buy(itemId) {
    const s = this.state;
    const it = s.shop.find((x) => x.id === itemId);
    if (!it) return;
    const price = this.shopPrice(it);
    if (s.gold < price) return this.toast('금화가 부족합니다.');
    s.gold -= price;
    s.shop = s.shop.filter((x) => x.id !== itemId);
    s.inventory.push(it);
    this.log(`${it.name}${josa(it.name, '을', '를')} 구입했습니다. (-${price} 금화)`);
    this.emit();
  },

  sell(itemId) {
    const s = this.state;
    const it = s.inventory.find((x) => x.id === itemId);
    if (!it || it.loan) return;
    const price = this.sellPrice(it);
    s.gold += price;
    s.inventory = s.inventory.filter((x) => x.id !== itemId);
    this.log(`${it.name}${josa(it.name, '을', '를')} 팔았습니다. (+${price} 금화)`);
    this.emit();
  },

  buyHerb() {
    const s = this.state;
    if (s.gold < HERB_PRICE) return this.toast('금화가 부족합니다.');
    s.gold -= HERB_PRICE; s.herbs++;
    this.emit();
  },

  useHerb(mercId) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m || m.status !== 'injured' || s.herbs <= 0) return;
    s.herbs--;
    m.injury -= 3;
    if (m.injury <= 0) { m.injury = 0; m.status = 'idle'; }
    this.log(`${m.name}에게 약초를 썼습니다.${m.status === 'idle' ? ' 완전히 회복했습니다!' : ''}`);
    this.emit();
  },

  equip(mercId, itemId) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === mercId);
    const it = s.inventory.find((x) => x.id === itemId);
    if (!m || !it) return;
    if (m.status === 'quest' && this.equipGuard !== false) return;   // 출격 중인 단원의 장비는 못 바꾼다: 전투 입력은 출격 때 굳는다 (js/muster.js)
    if (m.equip[it.slot]) s.inventory.push(m.equip[it.slot]);
    m.equip[it.slot] = it;
    s.inventory = s.inventory.filter((x) => x.id !== itemId);
    this.emit();
  },

  unequip(mercId, slot) {
    const m = this.state.mercs.find((x) => x.id === mercId);
    if (!m || !m.equip[slot]) return;
    if (m.status === 'quest' && this.equipGuard !== false) return;
    this.state.inventory.push(m.equip[slot]);
    m.equip[slot] = null;
    this.emit();
  },

  // ───────── 하루 진행 ─────────
  nextDay() {
    const s = this.state;
    if (s.over) return;
    const prevRank = this.rankIndex();
    s.day++;

    // 의뢰 귀환
    const due = s.missions.filter((mi) => mi.returnDay <= s.day);
    s.missions = s.missions.filter((mi) => mi.returnDay > s.day);
    due.forEach((mi) => this.resolveMission(mi));

    // 세계 진행 (전쟁 압박, 전역 결판)
    this.worldDaily();
    this.checkFactionRewards();
    this.checkFinalBattle();

    // 단원 회복 / 훈련 / 사기
    const heal = (1 + s.facilities.infirmary * 0.5) * (this.perk('church') ? 1.5 : 1);
    s.mercs.forEach((m) => {
      const idleDays = s.day - (m.lastQuest ?? s.day);
      if (m.status !== 'quest') m.fatigue = Math.max(0, m.fatigue - (m.status === 'injured' ? 10 : 15 + s.facilities.dorm * 2));
      if (m.status !== 'quest' && idleDays > 7 && (!this.isCaptain(m) || this.company(m.companyId))) this.changeMorale(m, -2);
      else if (m.morale > 80) this.changeMorale(m, -2);
      else if (m.morale > 70) this.changeMorale(m, -1);
      else if (m.morale < 55) this.changeMorale(m, 1);
      if (m.status === 'injured') {
        m.injury -= heal * (m.trait === 'sturdy' ? 1.5 : 1);
        if (m.injury <= 0) { m.injury = 0; m.status = 'idle'; this.log(`${m.name}${josa(m.name, '이', '가')} 부상에서 회복했습니다.`); }
      } else if (m.status === 'idle' && s.facilities.training > 0) {
        this.gainExp(m, Math.round(s.facilities.training * 5 * (m.trait === 'lazy' ? 0.5 : 1)));
      }
    });

    // 주간 정산과 세계 외교
    if (s.day % 7 === 1) { this.weeklyPayday(); this.worldWeekly(); }

    // 무작위 사건
    if (Math.random() < 0.2) {
      const ev = pick(RANDOM_EVENTS);
      const res = ev.run(this);
      this.log(`${ev.text} (${res})`, 'event');
    }

    this.fillContracts(false);
    if (!s.contracts.some((c) => !c.story && !c.boss && !c.campaign)) this.fillContracts(true);

    const newRank = this.rankIndex();
    if (newRank > prevRank) {
      this.log(`길드 등급이 ${RANKS[newRank].name}랭크로 승급했습니다! 더 먼 지방과 큰 의뢰가 열립니다.`, 'good');
      PROVINCE_KEYS.forEach((k) => {
        if (PROVINCES[k].tier > prevRank && PROVINCES[k].tier <= newRank) this.log(`활동 범위 확대: 「${PROVINCES[k].name}」의 의뢰를 맡을 수 있습니다.`, 'event');
      });
      this.refreshShop();
      if (RANKS[newRank].name === 'S' && !s.won) { s.won = true; s.pendingReports.push({ special: 'win' }); }
    }
    this.checkHeroes();
    this.checkCaptains();
    this.checkBosses();

    // 파산 판정
    // 전투 모드는 빚이 한 주 급료(DEBT_WEEKS)까지는 버틴다 (기본 'roll' 은 오늘처럼 -300)
    if (s.gold < (s.resolve === 'battle' ? -Math.max(300, Stats.KN.DEBT_WEEKS * this.weeklyWageTotal()) : -300)) {
      s.over = 'bankrupt';
      s.pendingReports.push({ special: 'bankrupt' });
    } else if (s.mercs.length === 0 && !s.companies.some((c) => !c.own) && s.gold < 60) {
      s.over = 'empty';
      s.pendingReports.push({ special: 'empty' });
    }

    this.save();
    this.emit();
  },

  weeklyPayday() {
    const s = this.state;
    const wages = this.weeklyWageTotal();
    const upkeep = this.weeklyUpkeepTotal();
    const total = wages + upkeep;
    if (s.gold >= total) {
      s.gold -= total;
      s.mercs.forEach((m) => this.changeMorale(m, 3));
      this.log(`주간 정산: 단원 주급 ${wages}, 계약 용병단 유지비 ${upkeep} 지급.`);
    } else {
      // 돈이 모자라면 계약 용병단부터 떠나고, 대기 중인 단원도 떠난다. 남은 금액은 빚.
      let owed = total;
      s.companies.filter((c) => !c.own && !c.missionId).forEach((c) => {
        if (s.gold >= owed) return;
        owed -= c.upkeep;
        this.releaseCompany(c.id, '유지비를 받지 못해 계약을 파기했습니다!', 'bad');
      });
      const sorted = s.mercs.filter((m) => m.status !== 'quest' && !this.isCaptain(m)).sort((a, b) => this.wage(b) - this.wage(a)); // 대장은 길드를 떠나지 않는다
      // 전투 모드: 패배 뒤 한 주(graceUntil, js/contract.js)는 주급을 못 받아도 떠나지 않는다 — 급료를 미루고(빚이 되지 않는다) 실망만 한다
      const grace = s.resolve === 'battle' && s.day <= (s.graceUntil || 0);
      while (s.gold < owed && sorted.length) {
        const m = sorted.shift();
        owed -= this.wage(m);
        if (grace) { this.changeMorale(m, -10); this.log(`${m.name}${josa(m.name, '이', '가')} 급료를 받지 못했지만, 패배 직후라 길드 곁에 남았습니다. (사기 -10)`, 'bad'); }
        else this.removeMerc(m, '주급을 받지 못해 길드를 떠났습니다!', 'bad');
      }
      // 대장은 떠나지 않는 대신 급료를 미루고 크게 실망한다
      const caps = s.mercs.filter((m) => this.isCaptain(m)).sort((a, b) => this.wage(b) - this.wage(a));
      while (s.gold < owed && caps.length) {
        const m = caps.shift();
        owed -= this.wage(m);
        this.changeMorale(m, -25);
        this.log(`용병대장 ${m.name}${josa(m.name, '이', '가')} 급료를 받지 못했습니다. 떠나지는 않았지만 몹시 실망했습니다. (사기 -25)`, 'bad');
      }
      // 전투 모드의 유예 주간: 못 준 급료(출격 중인 단원 몫 포함)는 미뤄 두고 빚으로 넘기지 않는다
      if (grace && owed > Math.max(0, s.gold)) owed = Math.max(0, s.gold);
      s.gold -= owed;
      this.log(`주간 정산: 금화 ${owed} 지급.${s.gold < 0 ? ' 길드가 빚을 지고 있습니다!' : ''}`, s.gold < 0 ? 'bad' : '');
    }
    // 사기가 바닥난 단원은 떠날 수 있다 (전투 모드: 패배 뒤 한 주는 떠나지 않는다)
    if (!(s.resolve === 'battle' && s.day <= (s.graceUntil || 0))) s.mercs.filter((m) => m.status !== 'quest' && m.morale <= 15 && !this.isCaptain(m)).forEach((m) => {
      if (Math.random() < 0.4) this.removeMerc(m, '불만이 쌓여 짐을 싸서 떠났습니다!', 'bad');
    });
    this.weeklyCompanies();
    this.refreshRecruits();
    this.weeklyElites();
    this.refreshShop();
    if (Math.floor(s.day / 7) % 2 === 0) this.refreshMarket();
    this.log('모집소에 새 지원자가, 상점에 새 물건이 들어왔습니다.');
  },

  weeklyWageTotal() { return this.state.mercs.reduce((sum, m) => sum + this.wage(m), 0); },
  daysToPayday() { const d = (8 - (this.state.day % 7)) % 7; return d === 0 ? 7 : d; },

  toast(msg) { if (typeof UI !== 'undefined') UI.toast(msg); },
};
