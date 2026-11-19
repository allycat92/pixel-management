// 게임 상태와 규칙
'use strict';

const SAVE_KEY = 'pixel-mercenary-guild-save-v1';
const SAVE_VERSION = 2;

const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const STORY_EXPIRES = 99999;

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
    const fixMerc = (m) => { m.equip = m.equip || { weapon: null, armor: null, trinket: null }; m.bond = m.bond || 0; };
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
    const g = CLASSES[m.cls].growth;
    const roll = (v) => Math.floor(v) + (Math.random() < v % 1 ? 1 : 0);
    m.level++;
    m.str += roll(g.str); m.dex += roll(g.dex); m.int += roll(g.int);
    m.maxHp += roll(g.hp) + rand(0, 2);
    if (!silent) this.log(`${m.name}이(가) 레벨 ${m.level}이 되었습니다!`, 'good');
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

  power(m, type) {
    const w = type ? QUEST_TYPES[type].weights : { str: 1, dex: 1, int: 1, hp: 0.1 };
    let p = this.eff(m, 'str') * w.str + this.eff(m, 'dex') * w.dex + this.eff(m, 'int') * w.int
      + this.eff(m, 'maxHp') * w.hp + m.level * 3;
    if (m.trait === 'brave') p *= 1.1;
    if (m.trait === 'coward') p *= 0.9;
    if (m.trait === 'berserker') p *= 1.25;
    if (m.trait === 'arcane') p *= type === 'magic' ? 1.35 : 1.1;
    return Math.round(p);
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

  partyPower(party, type) { return party.reduce((sum, m) => sum + this.power(m, type), 0); },

  successChance(quest, party) {
    if (!party.length) return 0;
    const pw = this.partyPower(party, quest.type);
    let c = 0.5 + ((pw - quest.req) / quest.req) * 0.9;
    // 직업 조합 보너스: 서로 다른 직업 수
    const kinds = new Set(party.map((m) => m.cls)).size;
    c += (kinds - 1) * 0.03;
    if (party.some((m) => m.trait === 'lucky')) c += 0.05;
    if (party.some((m) => m.trait === 'hawkeye')) c += 0.08;
    return clamp(c, 0.03, 0.97);
  },

  // 이야기 의뢰는 해당 특별 용병이 파티에 있어야 한다
  storyHeroMissing(quest, party) {
    if (!quest.story) return false;
    return !party.some((m) => m.hero === quest.story.hero);
  },

  dispatch(questId, mercIds) {
    const s = this.state;
    const q = s.quests.find((x) => x.id === questId);
    const party = mercIds.map((id) => s.mercs.find((m) => m.id === id)).filter((m) => m && m.status === 'idle');
    if (!q || !party.length || this.storyHeroMissing(q, party)) return;
    const chance = this.successChance(q, party);
    s.quests = s.quests.filter((x) => x.id !== questId);
    const mission = { id: s.nextId++, quest: q, party: party.map((m) => m.id), startDay: s.day, returnDay: s.day + q.days, chance };
    s.missions.push(mission);
    party.forEach((m) => { m.status = 'quest'; m.missionId = mission.id; });
    this.log(`[${q.title}] 의뢰에 ${party.map((m) => m.name).join(', ')} 파견. (${q.days}일 소요)`);
    this.emit();
  },

  resolveMission(mission) {
    const s = this.state;
    const q = mission.quest;
    const party = mission.party.map((id) => s.mercs.find((m) => m.id === id)).filter(Boolean);
    const roll = Math.random();
    const chance = mission.chance;
    let outcome;
    if (roll < chance * 0.25) outcome = 'great';
    else if (roll < chance) outcome = 'success';
    else if (roll > chance + (1 - chance) * 0.75 && chance < 0.6) outcome = 'disaster';
    else outcome = 'fail';
    const won = outcome === 'great' || outcome === 'success';

    const report = { quest: q, outcome, gold: 0, rep: 0, members: [] };
    const hasCleric = party.some((m) => m.cls === 'cleric');
    const hasSaint = party.some((m) => m.trait === 'saint');
    const rogues = party.filter((m) => m.cls === 'rogue').length;
    const greedy = party.some((m) => m.trait === 'greedy');
    const shadow = party.some((m) => m.trait === 'shadow');

    if (won) {
      let gold = q.reward * (outcome === 'great' ? 1.5 : 1);
      gold *= 1 + rogues * 0.12 + (greedy ? 0.1 : 0) + (shadow ? 0.25 : 0);
      report.gold = Math.round(gold);
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
      let deathChance = outcome === 'disaster' ? 0.3 : 0;
      if (hasCleric) deathChance *= 0.35;
      if (hasSaint) deathChance = 0;
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
      let inj = injuryBase;
      if (hasCleric) inj *= 0.5;
      if (hasSaint) inj *= 0.7;
      if (m.trait === 'sturdy' || m.trait === 'coward') inj *= 0.5;
      if (Math.random() < inj) {
        r.injury = rand(2, 4) + (outcome === 'disaster' ? 2 : 0);
        m.status = 'injured'; m.injury = r.injury;
      }
      report.members.push(r);
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
    this.refreshRecruits();
    this.refreshShop();
    this.log('주점에 새 지원자가, 상점에 새 물건이 들어왔습니다.');
  },

  weeklyWageTotal() { return this.state.mercs.reduce((sum, m) => sum + this.wage(m), 0); },
  daysToPayday() { const d = (8 - (this.state.day % 7)) % 7; return d === 0 ? 7 : d; },

  toast(msg) { if (typeof UI !== 'undefined') UI.toast(msg); },
};
