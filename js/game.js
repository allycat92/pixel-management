// 게임 핵심: 상태, 저장, 길드 등급·시설, 단원(용병), 장비·상점, 하루 진행
// 용병단은 company.js, 세력·영토는 faction.js, 의뢰는 contract.js 에서 Game 에 기능을 더한다.
'use strict';

const SAVE_KEY = 'pixel-guild-save-v3';
const SAVE_VERSION = 3;

const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const STORY_EXPIRES = 99999;
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
    // 시작 용병단: 단원 3명
    const [a, b, c] = ['warrior', 'archer', 'cleric'].map((cls) => { const m = this.makeMerc(cls, 1); s.mercs.push(m); return m; });
    a.trait = 'brave';
    const co = this.createCompany(true);
    [a, b, c].forEach((m) => { m.companyId = co.id; });
    co.leaderId = a.id;
    co.cohesion = 30;
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
    this.log(`${f.name}을(를) ${s.facilities[key]}단계로 증축했습니다. (-${cost} 금화)`, 'good');
    if (key === 'board') this.fillContracts(true);
    if (key === 'forge') this.refreshShop();
    this.emit();
  },

  // ───────── 용병 ─────────
  makeMerc(cls, level) {
    const c = CLASSES[cls];
    const usedNames = new Set(this.state ? [...this.state.mercs, ...this.state.recruits].map((m) => m.name) : []);
    Object.values(HEROES).forEach((h) => usedNames.add(h.name));
    let name = pick(NAMES), tries = 0;
    while (usedNames.has(name) && tries++ < 40) name = pick(NAMES);
    const m = {
      id: this.state ? this.state.nextId++ : 0,
      name, cls, level: 1, exp: 0,
      str: c.base.str + rand(-1, 2), dex: c.base.dex + rand(-1, 2), int: c.base.int + rand(-1, 2),
      maxHp: c.base.hp + rand(-2, 4),
      trait: pick(TRAIT_POOL),
      status: 'idle', injury: 0, missionId: null, quests: 0, bond: 0, companyId: null,
      fatigue: 0, morale: rand(60, 75), rel: {}, lastQuest: this.state ? this.state.day : 1,
      equip: { weapon: null, armor: null, trinket: null },
      look: { cls, skin: pick(SKIN_TONES), hair: pick(HAIR_COLORS), longHair: Math.random() < 0.4 },
    };
    for (let i = 1; i < level; i++) this.levelUp(m, true);
    return m;
  },

  expToNext(m) { return m.level * 60 + m.level * m.level * 6; },

  levelUp(m, silent) {
    const g = { ...CLASSES[m.cls].growth };
    const adv = m.adv && ADV_CLASSES[m.adv];
    if (adv) Object.entries(adv.growth).forEach(([k, v]) => { g[k] = (g[k] || 0) + v; });
    const roll = (v) => Math.floor(v) + (Math.random() < v % 1 ? 1 : 0);
    m.level++;
    m.str += roll(g.str); m.dex += roll(g.dex); m.int += roll(g.int);
    m.maxHp += roll(g.hp) + rand(0, 2);
    if (!silent) {
      this.changeMorale(m, 5);
      this.log(`${m.name}이(가) 레벨 ${m.level}이 되었습니다!${this.canPromote(m) ? ' 전직할 수 있습니다!' : ''}`, 'good');
    }
  },

  // ───────── 전직 ─────────
  className(m) { return m.adv ? ADV_CLASSES[m.adv].name : CLASSES[m.cls].name; },
  canPromote(m) { return !m.adv && m.level >= PROMOTE_LEVEL; },
  promote(mercId, key) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === mercId);
    const opt = m && PROMOTIONS[m.cls].find((p) => p.key === key);
    if (!m || !opt || !this.canPromote(m) || m.status === 'quest') return;
    if (s.gold < PROMOTE_COST) return this.toast('금화가 부족합니다.');
    s.gold -= PROMOTE_COST;
    this.applyPromotion(m, key);
    this.changeMorale(m, 10);
    this.log(`${m.name}이(가) ${opt.name}(으)로 전직했습니다! 스킬 「${opt.skill}」 습득. (-${PROMOTE_COST} 금화)`, 'good');
    this.emit();
  },
  applyPromotion(m, key) {
    const opt = ADV_CLASSES[key];
    m.adv = key;
    m.look = { ...m.look, adv: key };
    Object.entries(opt.bonus).forEach(([k, v]) => { m[k] += v; });
  },

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
    let w = (12 + m.level * 10 + m.level * m.level * 0.5) * (this.perk && this.state && this.perk('crown') ? 0.9 : 1);
    if (m.trait === 'greedy') w *= 1.3;
    if (m.trait === 'diligent') w *= 0.8;
    return Math.round(w);
  },
  hireCost(m) { return this.wage(m) * (m.hero || m.elite ? 4 : 3); },

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
    // 직업 스킬 / 상급 직업 스킬
    if (m.cls === 'mage' && type === 'magic') p *= 1.2;
    const t = type;
    if (m.adv === 'swordmaster' && (t === 'hunt' || t === 'defense')) p *= 1.3;
    if (m.adv === 'ranger' && (t === 'explore' || t === 'escort')) p *= 1.25;
    if (m.adv === 'elementalist' && (t === 'hunt' || t === 'magic')) p *= 1.3;
    if (m.adv === 'battlepriest') p *= 1.2;
    if (m.adv === 'assassin' && t === 'hunt') p *= 1.3;
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
    if (has((m) => m.cls === 'warrior')) mods.injury *= 0.85;
    if (has((m) => m.cls === 'archer')) mods.success += 0.04;
    if (has((m) => m.cls === 'cleric')) { mods.injury *= 0.5; mods.death *= 0.35; }
    mods.gold += party.filter((m) => m.cls === 'rogue').length * 0.12;
    if (has((m) => m.trait === 'lucky')) mods.success += 0.05;
    if (has((m) => m.trait === 'hawkeye')) mods.success += 0.08;
    if (has((m) => m.trait === 'saint')) { mods.death = 0; mods.injury *= 0.7; }
    if (has((m) => m.trait === 'greedy')) mods.gold += 0.1;
    if (has((m) => m.trait === 'shadow')) mods.gold += 0.25;
    if (has((m) => m.trait === 'captain')) { mods.gold += 0.15; mods.noMoraleLoss = true; }
    if (has((m) => m.trait === 'broker')) mods.gold += 0.1;
    if (has((m) => m.trait === 'blessed')) mods.death *= 0.5;
    if (has((m) => m.trait === 'sylvan')) mods.success += 0.05;
    if (has((m) => m.adv === 'paladin')) { mods.injury *= 0.7; mods.death *= 0.5; }
    if (has((m) => m.adv === 'ranger')) mods.days -= 1;
    if (has((m) => m.adv === 'sniper')) mods.great *= 2;
    if (has((m) => m.adv === 'warder')) { mods.noDisaster = true; mods.injury *= 0.8; }
    if (has((m) => m.adv === 'highpriest')) { mods.death = 0; mods.healHalf = true; }
    if (has((m) => m.adv === 'assassin')) mods.greatGold += 0.3;
    if (has((m) => m.adv === 'thief')) { mods.gold += 0.25; mods.loot = 0.25; }
    return mods;
  },

  hire(id) {
    const s = this.state;
    const m = s.recruits.find((r) => r.id === id);
    if (!m) return;
    if (s.mercs.length >= this.capacity()) return this.toast('숙소가 가득 찼습니다. 숙소를 증축하세요.');
    const cost = this.hireCost(m);
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    s.gold -= cost;
    s.recruits = s.recruits.filter((r) => r.id !== id);
    m.companyId = null;
    s.mercs.push(m);
    if (m.hero) {
      s.heroes[m.hero].hired = true;
      this.log(`특별 용병 「${m.title}」 ${m.name}이(가) 길드에 합류했습니다! 용병단에 배속해 함께 의뢰를 완수하세요. (-${cost} 금화)`, 'good');
    } else {
      this.log(`${CLASSES[m.cls].name} ${m.name}을(를) 고용했습니다. 예비 인원으로 대기합니다. (-${cost} 금화)`);
    }
    this.emit();
  },

  // 단원이 길드를 떠날 때 공통 처리 (장비 회수, 용병단에서 빠짐, 특별 용병은 모집소로)
  removeMerc(m, reason, kind = '') {
    const s = this.state;
    this.returnEquipment(m);
    this.leaveCompany(m, 10);
    s.mercs = s.mercs.filter((x) => x.id !== m.id);
    if (m.hero && !s.heroes[m.hero].dead) {
      s.heroes[m.hero].hired = false;
      m.status = 'idle'; m.injury = 0; m.morale = 55; m.companyId = null;
      s.recruits.unshift(m);
    }
    this.log(`${m.name}이(가) ${reason}`, kind);
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

  refreshRecruits(paid) {
    const s = this.state;
    if (paid) {
      if (s.gold < 30) return this.toast('금화가 부족합니다.');
      s.gold -= 30;
    }
    const lvBonus = s.facilities.tavern;
    const maxLv = 1 + lvBonus + Math.floor(this.rankIndex() * 1.2) + (this.perk('north') ? 2 : 0);
    const count = 3 + lvBonus;
    const heroes = s.recruits.filter((r) => r.hero || r.elite);
    s.recruits = heroes;
    for (let i = 0; i < count; i++) {
      s.recruits.push(this.makeMerc(pick(Object.keys(CLASSES)), rand(Math.max(1, maxLv - 2), maxLv)));
    }
    if (paid) { this.log('모집소에 새로운 지원자들이 찾아왔습니다. (-30 금화)'); this.emit(); }
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
    this.log(`${it.name}을(를) 구입했습니다. (-${price} 금화)`);
    this.emit();
  },

  sell(itemId) {
    const s = this.state;
    const it = s.inventory.find((x) => x.id === itemId);
    if (!it || it.loan) return;
    const price = this.sellPrice(it);
    s.gold += price;
    s.inventory = s.inventory.filter((x) => x.id !== itemId);
    this.log(`${it.name}을(를) 팔았습니다. (+${price} 금화)`);
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
    if (m.equip[it.slot]) s.inventory.push(m.equip[it.slot]);
    m.equip[it.slot] = it;
    s.inventory = s.inventory.filter((x) => x.id !== itemId);
    this.emit();
  },

  unequip(mercId, slot) {
    const m = this.state.mercs.find((x) => x.id === mercId);
    if (!m || !m.equip[slot]) return;
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
      if (m.status !== 'quest' && idleDays > 7) this.changeMorale(m, -2);
      else if (m.morale > 80) this.changeMorale(m, -2);
      else if (m.morale > 70) this.changeMorale(m, -1);
      else if (m.morale < 55) this.changeMorale(m, 1);
      if (m.status === 'injured') {
        m.injury -= heal * (m.trait === 'sturdy' ? 1.5 : 1);
        if (m.injury <= 0) { m.injury = 0; m.status = 'idle'; this.log(`${m.name}이(가) 부상에서 회복했습니다.`); }
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
    this.checkBosses();

    // 파산 판정
    if (s.gold < -300) {
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
      const sorted = s.mercs.filter((m) => m.status !== 'quest').sort((a, b) => this.wage(b) - this.wage(a));
      while (s.gold < owed && sorted.length) {
        const m = sorted.shift();
        owed -= this.wage(m);
        this.removeMerc(m, '주급을 받지 못해 길드를 떠났습니다!', 'bad');
      }
      s.gold -= owed;
      this.log(`주간 정산: 금화 ${owed} 지급.${s.gold < 0 ? ' 길드가 빚을 지고 있습니다!' : ''}`, s.gold < 0 ? 'bad' : '');
    }
    // 사기가 바닥난 단원은 떠날 수 있다
    s.mercs.filter((m) => m.status !== 'quest' && m.morale <= 15).forEach((m) => {
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
