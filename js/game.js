// 게임 상태와 규칙
'use strict';

const SAVE_KEY = 'pixel-mercenary-guild-save-v1';
const SAVE_VERSION = 2;

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
      guildName: '은빛 늑대 용병단',
      day: 1, gold: 300, rep: 0, nextId: 1,
      mercs: [], recruits: [], quests: [], missions: [], log: [],
      facilities: { dorm: 0, training: 0, infirmary: 0, tavern: 0, board: 0, forge: 0 },
      stats: { completed: 0, failed: 0, fallen: 0 },
      inventory: [], shop: [], herbs: 1,
      heroes: {}, outposts: {},
      settings: { battle: true },
      pendingReports: [], over: null, won: false,
    };
    const s = this.state;
    s.mercs.push(this.makeMerc('warrior', 1));
    s.mercs.push(this.makeMerc('archer', 1));
    s.mercs[0].trait = 'brave';
    this.refreshRecruits();
    this.refreshShop();
    this.fillQuests(true);
    this.log('용병단이 창설되었습니다! 의뢰를 수행해 명성을 쌓고 S랭크를 목표로 하세요.', 'good');
  },

  save() {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(this.state)); return true; } catch (e) { return false; }
  },
  load() {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) return false;
      this.state = JSON.parse(raw);
      this.migrate();
      return true;
    } catch (e) { return false; }
  },
  clearSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* 무시 */ } },

  // 예전 저장 데이터에 새 항목 채워 넣기
  migrate() {
    const s = this.state;
    s.facilities = { dorm: 0, training: 0, infirmary: 0, tavern: 0, board: 0, forge: 0, ...s.facilities };
    s.inventory = s.inventory || [];
    s.shop = s.shop || [];
    if (s.herbs == null) s.herbs = 1;
    s.heroes = s.heroes || {};
    s.outposts = s.outposts || {};
    s.settings = { battle: true, ...(s.settings || {}) };
    const fixMerc = (m) => {
      m.equip = m.equip || { weapon: null, armor: null, trinket: null };
      m.bond = m.bond || 0;
      if (m.fatigue == null) m.fatigue = 0;
      if (m.morale == null) m.morale = 65;
      m.rel = m.rel || {};
      if (m.lastQuest == null) m.lastQuest = s.day;
    };
    s.mercs.forEach(fixMerc); s.recruits.forEach(fixMerc);
    const fixQuest = (q) => {
      q.region = q.region || 'plains';
      q.enemy = q.enemy || pick(REGIONS[q.region].enemies);
    };
    s.quests.forEach(fixQuest);
    s.missions.forEach((mi) => { fixQuest(mi.quest); mi.startDay = mi.startDay || mi.returnDay - mi.quest.days; });
    if (!s.shop.length) this.refreshShop();
    s.version = SAVE_VERSION;
  },

  log(text, kind = '') {
    this.state.log.unshift({ day: this.state.day, text, kind });
    if (this.state.log.length > 150) this.state.log.length = 150;
  },

  // ───────── 랭크 / 시설 / 지역 ─────────
  rankIndex() {
    let idx = 0;
    RANKS.forEach((r, i) => { if (this.state.rep >= r.rep) idx = i; });
    return idx;
  },
  rank() { return RANKS[this.rankIndex()]; },
  nextRank() { return RANKS[this.rankIndex() + 1] || null; },
  capacity() { return 4 + this.state.facilities.dorm * 2; },
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
    if (key === 'board') this.fillQuests(true);
    if (key === 'forge') this.refreshShop();
    this.emit();
  },

  regionUnlocked(key) { return this.rankIndex() >= REGIONS[key].unlock; },
  unlockedRegions() { return Object.keys(REGIONS).filter((k) => this.regionUnlocked(k)); },
  buildOutpost(key) {
    const s = this.state, r = REGIONS[key];
    if (s.outposts[key] || !this.regionUnlocked(key) || !r.outpostCost) return;
    if (s.gold < r.outpostCost) return this.toast('금화가 부족합니다.');
    s.gold -= r.outpostCost;
    s.outposts[key] = true;
    this.log(`${r.name}에 전초기지를 세웠습니다! 이 지역 의뢰가 늘고 이동이 빨라집니다. (-${r.outpostCost} 금화)`, 'good');
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
      status: 'idle', injury: 0, missionId: null, quests: 0, bond: 0,
      fatigue: 0, morale: rand(60, 75), rel: {}, lastQuest: this.state ? this.state.day : 1,
      equip: { weapon: null, armor: null, trinket: null },
      look: { cls, skin: pick(SKIN_TONES), hair: pick(HAIR_COLORS), longHair: Math.random() < 0.4 },
    };
    for (let i = 1; i < level; i++) this.levelUp(m, true);
    return m;
  },

  makeHero(key) {
    const h = HEROES[key];
    const m = this.makeMerc(h.cls, h.level);
    const g = CLASSES[h.cls].growth;
    m.name = h.name; m.hero = key; m.trait = h.trait; m.title = h.title;
    m.look = { cls: h.cls, ...h.look };
    // 특별 용병은 주력 능력치가 조금 더 높다
    const main = Object.keys(g).filter((k) => k !== 'hp').sort((a, b) => g[b] - g[a])[0];
    m[main] += 3; m.maxHp += 4;
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
    let w = 12 + m.level * 9;
    if (m.trait === 'greedy') w *= 1.3;
    if (m.trait === 'diligent') w *= 0.8;
    return Math.round(w);
  },
  hireCost(m) { return this.wage(m) * (m.hero ? 4 : 3); },

  // party를 넘기면 전우/불화/지휘 효과까지 반영
  power(m, type, party) {
    const w = type ? QUEST_TYPES[type].weights : { str: 1, dex: 1, int: 1, hp: 0.1 };
    let p = this.eff(m, 'str') * w.str + this.eff(m, 'dex') * w.dex + this.eff(m, 'int') * w.int
      + this.eff(m, 'maxHp') * w.hp + m.level * 3;
    if (m.trait === 'brave') p *= 1.1;
    if (m.trait === 'coward') p *= 0.9;
    if (m.trait === 'berserker') p *= 1.25;
    if (m.trait === 'arcane') p *= type === 'magic' ? 1.35 : 1.1;
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
    s.mercs.push(m);
    if (m.hero) {
      s.heroes[m.hero].hired = true;
      this.log(`특별 용병 「${m.title}」 ${m.name}이(가) 합류했습니다! 함께 의뢰를 완수해 인연을 쌓으세요. (-${cost} 금화)`, 'good');
    } else {
      this.log(`${CLASSES[m.cls].name} ${m.name}을(를) 고용했습니다. (-${cost} 금화)`);
    }
    this.emit();
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
    this.returnEquipment(m);
    s.mercs = s.mercs.filter((x) => x.id !== id);
    if (m.hero) {
      // 특별 용병은 떠나도 주점에 다시 찾아온다
      s.heroes[m.hero].hired = false;
      m.status = 'idle'; m.injury = 0;
      s.recruits.unshift(m);
    }
    this.log(`${m.name}이(가) 용병단을 떠났습니다.`);
    this.emit();
  },

  refreshRecruits(paid) {
    const s = this.state;
    if (paid) {
      if (s.gold < 30) return this.toast('금화가 부족합니다.');
      s.gold -= 30;
    }
    const lvBonus = s.facilities.tavern;
    const maxLv = 1 + lvBonus + Math.floor(this.rankIndex() * 1.2);
    const count = 3 + lvBonus;
    const heroes = s.recruits.filter((r) => r.hero);
    s.recruits = heroes;
    for (let i = 0; i < count; i++) {
      s.recruits.push(this.makeMerc(pick(Object.keys(CLASSES)), rand(Math.max(1, maxLv - 2), maxLv)));
    }
    if (paid) { this.log('주점에 새로운 지원자들이 찾아왔습니다. (-30 금화)'); this.emit(); }
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
  shopPrice(item) { return Math.round(item.price * (1 - this.state.facilities.forge * 0.04)); },
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
    if (!it) return;
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

  // ───────── 의뢰 ─────────
  pickRegion() {
    const s = this.state, r = this.rankIndex();
    const regions = this.unlockedRegions();
    const weights = regions.map((k) => {
      const [lo, hi] = REGIONS[k].levels;
      return 1 + (s.outposts[k] ? 1.5 : 0) + (r + 1 >= lo && r + 1 <= hi ? 2 : 0);
    });
    let x = Math.random() * weights.reduce((a, b) => a + b, 0);
    for (let i = 0; i < regions.length; i++) { x -= weights[i]; if (x <= 0) return regions[i]; }
    return regions[0];
  },

  questEnemy(type, region, level) {
    if (type === 'magic') return MAGIC_ENEMIES[clamp(Math.floor((level - 1) / 2.5), 0, MAGIC_ENEMIES.length - 1)];
    return pick(REGIONS[region].enemies);
  },

  makeQuest(opts = {}) {
    const s = this.state;
    const r = this.rankIndex();
    const region = opts.region || this.pickRegion();
    const reg = REGIONS[region];
    const type = opts.type || pick(Object.keys(QUEST_TYPES));
    const t = QUEST_TYPES[type];
    let level = opts.level;
    if (!level) {
      const hi = Math.min(reg.levels[1], r + 2);
      const lo = Math.min(Math.max(reg.levels[0], r), hi);
      level = clamp(rand(lo, hi) + (Math.random() < 0.15 ? 1 : 0), 1, 10);
    }
    const enemy = opts.enemy || this.questEnemy(type, region, level);
    const title = opts.title || pick(t.titles).replace('{e}', enemy).replace('{p}', pick(reg.places));
    const days = Math.max(1, rand(1, 3) + (level > 4 ? 1 : 0) + reg.travel - (s.outposts[region] ? 1 : 0));
    const party = opts.party || Math.min(4, 2 + Math.floor(Math.random() * 3));
    const req = Math.round(24 * Math.pow(1.4, level - 1) * (0.9 + Math.random() * 0.2) * (0.8 + party * 0.1));
    const rewardMul = (1 + s.facilities.board * 0.08) * (s.outposts[region] ? 1.15 : 1);
    return {
      id: s.nextId++, type, title, level, days, maxParty: party, req, region, enemy,
      reward: Math.round((35 + level * 28 + level * level * 6) * (0.85 + Math.random() * 0.3) * (1 + days * 0.15) * rewardMul),
      rep: Math.round(4 + level * 3 + (party >= 4 ? 2 : 0)),
      expires: s.day + rand(3, 6),
    };
  },

  fillQuests(force) {
    const s = this.state;
    const max = 3 + s.facilities.board;
    s.quests = s.quests.filter((q) => q.expires >= s.day);
    let guard = 0;
    while (s.quests.filter((q) => !q.story).length < max && guard++ < 10) {
      if (!force && Math.random() < 0.45) break;
      s.quests.push(this.makeQuest());
    }
  },

  partyPower(party, type) { return party.reduce((sum, m) => sum + this.power(m, type, party), 0); },

  successChance(quest, party) {
    if (!party.length) return 0;
    const pw = this.partyPower(party, quest.type);
    let c = 0.5 + ((pw - quest.req) / quest.req) * 0.9;
    // 직업 조합 보너스: 서로 다른 직업 수
    const kinds = new Set(party.map((m) => m.cls)).size;
    c += (kinds - 1) * 0.03;
    c += this.partyMods(party).success;
    return clamp(c, 0.03, 0.97);
  },

  // 이야기 의뢰는 해당 특별 용병이 파티에 있어야 한다
  storyHeroMissing(quest, party) {
    if (!quest.story) return false;
    return !party.some((m) => m.hero === quest.story.hero);
  },

  questDays(q, party) { return Math.max(1, q.days + (party.length ? this.partyMods(party).days : 0)); },

  dispatch(questId, mercIds) {
    const s = this.state;
    const q = s.quests.find((x) => x.id === questId);
    const party = mercIds.map((id) => s.mercs.find((m) => m.id === id)).filter((m) => m && m.status === 'idle');
    if (!q || !party.length || this.storyHeroMissing(q, party)) return;
    const chance = this.successChance(q, party);
    const days = this.questDays(q, party);
    s.quests = s.quests.filter((x) => x.id !== questId);
    const mission = { id: s.nextId++, quest: q, party: party.map((m) => m.id), startDay: s.day, returnDay: s.day + days, chance };
    s.missions.push(mission);
    party.forEach((m) => {
      m.status = 'quest'; m.missionId = mission.id; m.lastQuest = s.day;
      m.fatigue = Math.min(100, m.fatigue + 10 + days * 8);
    });
    this.log(`[${q.title}] 의뢰에 ${party.map((m) => m.name).join(', ')} 파견. (${days}일 소요)`);
    this.emit();
  },

  resolveMission(mission) {
    const s = this.state;
    const q = mission.quest;
    const party = mission.party.map((id) => s.mercs.find((m) => m.id === id)).filter(Boolean);
    const roll = Math.random();
    const chance = mission.chance;
    const mods = this.partyMods(party);
    let outcome;
    if (roll < chance * 0.25 * mods.great) outcome = 'great';
    else if (roll < chance) outcome = 'success';
    else if (roll > chance + (1 - chance) * 0.75 && chance < 0.6) outcome = mods.noDisaster ? 'fail' : 'disaster';
    else outcome = 'fail';
    const won = outcome === 'great' || outcome === 'success';

    const report = { quest: q, outcome, gold: 0, rep: 0, members: [] };

    if (won) {
      const gold = q.reward * (outcome === 'great' ? 1.5 * mods.greatGold : 1) * mods.gold;
      report.gold = Math.round(gold);
      if (Math.random() < mods.loot) {
        const it = this.makeItem(pick(Object.keys(ITEM_BASES)), this.shopMaxTier());
        s.inventory.push(it);
        report.loot = it.name;
        this.log(`보물 사냥! 「${it.name}」을(를) 손에 넣었습니다.`, 'good');
      }
      report.rep = Math.round(q.rep * (outcome === 'great' ? 1.5 : 1));
      s.stats.completed++;
    } else {
      report.gold = outcome === 'fail' ? Math.round(q.reward * 0.15) : 0;
      report.rep = -Math.round(q.rep * (outcome === 'disaster' ? 0.6 : 0.3));
      s.stats.failed++;
    }
    s.gold += report.gold;
    s.rep = Math.max(0, s.rep + report.rep);

    const baseExp = 15 + q.level * 18;
    const expMul = { great: 1.5, success: 1, fail: 0.5, disaster: 0.3 }[outcome];
    const injuryBase = { great: 0.05, success: 0.15, fail: 0.4, disaster: 0.7 }[outcome];

    party.forEach((m) => {
      const r = { id: m.id, name: m.name, cls: m.cls, look: m.look, exp: 0, levelUp: false, injury: 0, dead: false };
      m.missionId = null; m.status = 'idle'; m.quests++;
      if (won && m.hero) m.bond++;
      // 사망 판정 (대실패 때만)
      let deathChance = (outcome === 'disaster' ? 0.3 : 0) * mods.death;
      if (m.trait === 'sturdy') deathChance *= 0.6;
      if (Math.random() < deathChance) {
        r.dead = true;
        this.returnEquipment(m);
        s.mercs = s.mercs.filter((x) => x.id !== m.id);
        s.stats.fallen++;
        if (m.hero) s.heroes[m.hero].dead = true;
        this.log(`${m.name}이(가) [${q.title}]에서 전사했습니다... 유품(장비)은 창고로 돌아왔습니다.`, 'bad');
        report.members.push(r);
        return;
      }
      r.exp = Math.round(baseExp * expMul);
      r.levelUp = this.gainExp(m, r.exp);
      let inj = injuryBase * mods.injury;
      if (m.trait === 'sturdy' || m.trait === 'coward') inj *= 0.5;
      if (m.fatigue >= 80) inj *= 1.5;
      // 사기
      const dm = { great: 6, success: 2, fail: -6, disaster: -12 }[outcome];
      if (dm > 0 || !mods.noMoraleLoss) this.changeMorale(m, dm);
      if (Math.random() < inj) {
        r.injury = rand(2, 4) + (outcome === 'disaster' ? 2 : 0);
        if (mods.healHalf) r.injury = Math.ceil(r.injury / 2);
        m.status = 'injured'; m.injury = r.injury;
      }
      report.members.push(r);
    });

    // 함께 다녀온 단원끼리 관계 변화, 전사자 애도
    const survivors = party.filter((m) => s.mercs.includes(m));
    for (let i = 0; i < survivors.length; i++) {
      for (let j = i + 1; j < survivors.length; j++) {
        const a = survivors[i], b = survivors[j];
        const before = this.rel(a, b);
        const d = this.traitsClash(a, b) ? -6 : (outcome === 'great' ? 8 : won ? 5 : 3);
        this.addRel(a, b, d);
        if (before < FRIEND_REL && this.rel(a, b) >= FRIEND_REL) this.log(`${a.name}와(과) ${b.name}이(가) 전우가 되었습니다! 함께 출격하면 전투력이 오릅니다.`, 'good');
        if (before > RIVAL_REL && this.rel(a, b) <= RIVAL_REL) this.log(`${a.name}와(과) ${b.name}의 사이가 틀어졌습니다. 함께 보내면 전투력이 떨어집니다.`, 'bad');
      }
    }
    report.members.filter((r) => r.dead).forEach((r) => {
      s.mercs.forEach((m) => {
        const grief = (m.rel && m.rel[r.id]) >= FRIEND_REL;
        this.changeMorale(m, grief ? -25 : -8);
        if (grief) this.log(`${m.name}이(가) 전우 ${r.name}의 죽음에 깊이 슬퍼합니다.`, 'bad');
      });
    });

    const label = { great: '대성공', success: '성공', fail: '실패', disaster: '대실패' }[outcome];
    this.log(`[${q.title}] ${label}! 금화 ${report.gold >= 0 ? '+' : ''}${report.gold}, 명성 ${report.rep >= 0 ? '+' : ''}${report.rep}`,
      won ? 'good' : 'bad');
    s.pendingReports.push(report);

    if (q.story) {
      if (won) this.completeStory(q.story);
      else if (!s.heroes[q.story.hero].dead) {
        s.quests.unshift({ ...q, id: s.nextId++ });
        this.log(`「${q.title}」은(는) 다시 도전할 수 있습니다.`);
      }
    }
  },

  // ───────── 특별 용병 이야기 ─────────
  checkHeroes() {
    const s = this.state, r = this.rankIndex();
    Object.entries(HEROES).forEach(([key, h]) => {
      if (!s.heroes[key]) s.heroes[key] = { appeared: false, hired: false, ch: 0, dead: false };
      const hs = s.heroes[key];
      if (!hs.appeared && r >= h.unlock) {
        hs.appeared = true;
        s.recruits.unshift(this.makeHero(key));
        this.log(`주점에 특별한 손님이 찾아왔습니다: 「${h.title}」 ${h.name}`, 'event');
        s.pendingReports.push({ special: 'dialog', hero: key, title: `${h.title} ${h.name}`, lines: h.intro, foot: '주점에서 고용할 수 있습니다.' });
      }
    });
    // 인연이 쌓이면 개인 의뢰 게시
    s.mercs.filter((m) => m.hero).forEach((m) => {
      const hs = s.heroes[m.hero], h = HEROES[m.hero];
      const ch = h.chapters[hs.ch];
      if (!ch || m.bond < ch.bond || !this.regionUnlocked(ch.region)) return;
      const posted = s.quests.some((q) => q.story && q.story.hero === m.hero)
        || s.missions.some((mi) => mi.quest.story && mi.quest.story.hero === m.hero);
      if (posted) return;
      const level = clamp(Math.max(REGIONS[ch.region].levels[0], this.rankIndex() + 2), 1, 10);
      const q = this.makeQuest({ region: ch.region, type: ch.type, enemy: ch.enemy, title: ch.title, level, party: 4 });
      q.story = { hero: m.hero, ch: hs.ch };
      q.expires = STORY_EXPIRES;
      q.reward = Math.round(q.reward * 1.5);
      q.rep = q.rep * 2;
      s.quests.unshift(q);
      this.log(`${m.name}의 개인 의뢰 「${ch.title}」이(가) 게시판에 올라왔습니다!`, 'event');
      s.pendingReports.push({ special: 'dialog', hero: m.hero, title: `개인 의뢰: ${ch.title}`, lines: ch.before, foot: `${m.name}을(를) 반드시 파티에 넣어야 합니다.` });
    });
  },

  completeStory(story) {
    const s = this.state;
    const h = HEROES[story.hero], hs = s.heroes[story.hero];
    const ch = h.chapters[story.ch];
    const m = s.mercs.find((x) => x.hero === story.hero);
    hs.ch = story.ch + 1;
    const rw = ch.reward;
    const gains = [];
    if (rw.item) {
      const it = this.makeUniqueItem(rw.item);
      s.inventory.push(it);
      gains.push(`전설 장비 「${it.name}」 획득`);
    }
    if (rw.stats && m) {
      Object.entries(rw.stats).forEach(([k, v]) => { m[k === 'hp' ? 'maxHp' : k] += v; });
      gains.push(`${m.name} 능력치 상승 (${Object.entries(rw.stats).map(([k, v]) => `${STAT_NAMES[k]}+${v}`).join(', ')})`);
    }
    if (rw.rep) { s.rep += rw.rep; gains.push(`명성 +${rw.rep}`); }
    if (rw.newTitle && m) { m.title = rw.newTitle; gains.push(`새 칭호 「${rw.newTitle}」`); }
    this.log(`${h.name}의 이야기 「${ch.title}」 완료! ${gains.join(', ')}`, 'good');
    s.pendingReports.push({ special: 'dialog', hero: story.hero, title: `${ch.title} - 완료`, lines: ch.after, foot: gains.join(' · ') });
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

    // 부상 회복 / 훈련
    const heal = 1 + s.facilities.infirmary * 0.5;
    s.mercs.forEach((m) => {
      const idleDays = s.day - (m.lastQuest ?? s.day);
      if (m.status !== 'quest') m.fatigue = Math.max(0, m.fatigue - (m.status === 'injured' ? 10 : 15 + s.facilities.dorm * 3));
      if (m.status !== 'quest' && idleDays > 7) this.changeMorale(m, -2); // 너무 오래 놀면 지루해한다
      else if (m.morale > 80) this.changeMorale(m, -2); // 들뜬 기분은 서서히 가라앉는다
      else if (m.morale > 70) this.changeMorale(m, -1);
      else if (m.morale < 55) this.changeMorale(m, 1);
      if (m.status === 'injured') {
        m.injury -= heal * (m.trait === 'sturdy' ? 1.5 : 1);
        if (m.injury <= 0) { m.injury = 0; m.status = 'idle'; this.log(`${m.name}이(가) 부상에서 회복했습니다.`); }
      } else if (m.status === 'idle' && s.facilities.training > 0) {
        const amt = s.facilities.training * 5 * (m.trait === 'lazy' ? 0.5 : 1);
        this.gainExp(m, Math.round(amt));
      }
    });

    // 주간 정산
    if (s.day % 7 === 1) this.weeklyPayday();

    // 무작위 이벤트
    if (Math.random() < 0.22) {
      const ev = pick(RANDOM_EVENTS);
      const res = ev.run(this);
      this.log(`${ev.text} (${res})`, 'event');
    }

    this.fillQuests(false);
    if (!s.quests.some((q) => !q.story)) this.fillQuests(true);

    const newRank = this.rankIndex();
    if (newRank > prevRank) {
      this.log(`용병단 등급이 ${RANKS[newRank].name}랭크로 승급했습니다! 더 어려운 의뢰가 들어옵니다.`, 'good');
      Object.entries(REGIONS).forEach(([k, r]) => {
        if (r.unlock > prevRank && r.unlock <= newRank) this.log(`새 지역 「${r.name}」이(가) 열렸습니다! 지도를 확인하세요.`, 'event');
      });
      this.refreshShop();
      if (RANKS[newRank].name === 'S' && !s.won) {
        s.won = true;
        s.pendingReports.push({ special: 'win' });
      }
    }
    this.checkHeroes();

    // 파산 판정
    if (s.gold < -200) {
      s.over = 'bankrupt';
      s.pendingReports.push({ special: 'bankrupt' });
    } else if (s.mercs.length === 0 && s.gold < 40) {
      s.over = 'empty';
      s.pendingReports.push({ special: 'empty' });
    }

    this.save();
    this.emit();
  },

  weeklyPayday() {
    const s = this.state;
    const total = s.mercs.reduce((sum, m) => sum + this.wage(m), 0);
    if (s.gold >= total) {
      s.gold -= total;
      s.mercs.forEach((m) => this.changeMorale(m, 3));
      this.log(`주급 정산: 단원 ${s.mercs.length}명에게 금화 ${total}을 지급했습니다.`);
    } else {
      // 돈이 모자라면 대기 중인 단원부터 떠나고, 남은 금액은 빚이 된다
      const sorted = [...s.mercs].filter((m) => m.status !== 'quest').sort((a, b) => this.wage(b) - this.wage(a));
      let owed = total;
      while (s.gold < owed && sorted.length) {
        const m = sorted.shift();
        owed -= this.wage(m);
        this.returnEquipment(m);
        s.mercs = s.mercs.filter((x) => x.id !== m.id);
        if (m.hero) { s.heroes[m.hero].hired = false; m.status = 'idle'; m.injury = 0; s.recruits.unshift(m); }
        this.log(`주급을 받지 못한 ${m.name}이(가) 용병단을 떠났습니다!`, 'bad');
      }
      s.gold -= owed;
      this.log(`주급 정산: 금화 ${owed} 지급.${s.gold < 0 ? ' 용병단이 빚을 지고 있습니다!' : ''}`, s.gold < 0 ? 'bad' : '');
    }
    // 사기가 바닥난 단원은 떠날 수 있다
    s.mercs.filter((m) => m.status !== 'quest' && m.morale <= 15).forEach((m) => {
      if (Math.random() < 0.4) {
        this.returnEquipment(m);
        s.mercs = s.mercs.filter((x) => x.id !== m.id);
        if (m.hero) { s.heroes[m.hero].hired = false; m.status = 'idle'; m.injury = 0; m.morale = 50; s.recruits.unshift(m); }
        this.log(`불만이 쌓인 ${m.name}이(가) 짐을 싸서 용병단을 떠났습니다!`, 'bad');
      }
    });
    this.refreshRecruits();
    this.refreshShop();
    this.log('주점에 새 지원자가, 상점에 새 물건이 들어왔습니다.');
  },

  weeklyWageTotal() { return this.state.mercs.reduce((sum, m) => sum + this.wage(m), 0); },
  daysToPayday() { const d = (8 - (this.state.day % 7)) % 7; return d === 0 ? 7 : d; },

  toast(msg) { if (typeof UI !== 'undefined') UI.toast(msg); },
};
