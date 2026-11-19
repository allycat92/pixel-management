// 게임 상태와 규칙
'use strict';

const SAVE_KEY = 'pixel-mercenary-guild-save-v1';

const rand = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

const Game = {
  state: null,
  listeners: [],

  onChange(fn) { this.listeners.push(fn); },
  emit() { this.listeners.forEach((fn) => fn()); },

  // ───────── 초기화 / 저장 ─────────
  newGame() {
    this.state = {
      guildName: '은빛 늑대 용병단',
      day: 1, gold: 300, rep: 0, nextId: 1,
      mercs: [], recruits: [], quests: [], missions: [], log: [],
      facilities: { dorm: 0, training: 0, infirmary: 0, tavern: 0, board: 0 },
      stats: { completed: 0, failed: 0, fallen: 0 },
      pendingReports: [], over: null, won: false,
    };
    const s = this.state;
    s.mercs.push(this.makeMerc('warrior', 1));
    s.mercs.push(this.makeMerc('archer', 1));
    s.mercs[0].trait = 'brave';
    this.refreshRecruits();
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
      return true;
    } catch (e) { return false; }
  },
  clearSave() { try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* 무시 */ } },

  log(text, kind = '') {
    this.state.log.unshift({ day: this.state.day, text, kind });
    if (this.state.log.length > 150) this.state.log.length = 150;
  },

  // ───────── 랭크 / 시설 ─────────
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
    this.emit();
  },

  // ───────── 용병 ─────────
  makeMerc(cls, level) {
    const c = CLASSES[cls];
    const usedNames = new Set(this.state ? [...this.state.mercs, ...this.state.recruits].map((m) => m.name) : []);
    let name = pick(NAMES), tries = 0;
    while (usedNames.has(name) && tries++ < 30) name = pick(NAMES);
    const m = {
      id: this.state ? this.state.nextId++ : 0,
      name, cls, level: 1, exp: 0,
      str: c.base.str + rand(-1, 2), dex: c.base.dex + rand(-1, 2), int: c.base.int + rand(-1, 2),
      maxHp: c.base.hp + rand(-2, 4),
      trait: pick(TRAIT_POOL),
      status: 'idle', injury: 0, missionId: null, quests: 0,
      look: { cls, skin: pick(SKIN_TONES), hair: pick(HAIR_COLORS), longHair: Math.random() < 0.4 },
    };
    for (let i = 1; i < level; i++) this.levelUp(m, true);
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

  wage(m) {
    let w = 12 + m.level * 9;
    if (m.trait === 'greedy') w *= 1.3;
    if (m.trait === 'diligent') w *= 0.8;
    return Math.round(w);
  },
  hireCost(m) { return this.wage(m) * 3; },

  power(m, type) {
    const w = type ? QUEST_TYPES[type].weights : { str: 1, dex: 1, int: 1, hp: 0.1 };
    let p = m.str * w.str + m.dex * w.dex + m.int * w.int + m.maxHp * w.hp + m.level * 3;
    if (m.trait === 'brave') p *= 1.1;
    if (m.trait === 'coward') p *= 0.9;
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
    this.log(`${CLASSES[m.cls].name} ${m.name}을(를) 고용했습니다. (-${cost} 금화)`);
    this.emit();
  },

  dismiss(id) {
    const s = this.state;
    const m = s.mercs.find((x) => x.id === id);
    if (!m || m.status === 'quest') return;
    s.mercs = s.mercs.filter((x) => x.id !== id);
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
    s.recruits = [];
    for (let i = 0; i < count; i++) {
      s.recruits.push(this.makeMerc(pick(Object.keys(CLASSES)), rand(Math.max(1, maxLv - 2), maxLv)));
    }
    if (paid) { this.log('주점에 새로운 지원자들이 찾아왔습니다. (-30 금화)'); this.emit(); }
  },

  // ───────── 의뢰 ─────────
  makeQuest() {
    const s = this.state;
    const r = this.rankIndex();
    const type = pick(Object.keys(QUEST_TYPES));
    const t = QUEST_TYPES[type];
    const level = clamp(r + 1 + rand(-1, 1) + (Math.random() < 0.15 ? 1 : 0), 1, 10);
    const title = pick(t.titles)
      .replace('{e}', t.enemies ? pick(t.enemies.slice(Math.max(0, level - 3), level + 1)) : '')
      .replace('{p}', t.places ? pick(t.places) : '');
    const days = rand(1, 3) + (level > 4 ? 1 : 0);
    const party = Math.min(4, 2 + Math.floor(Math.random() * 3));
    const req = Math.round(24 * Math.pow(1.4, level - 1) * (0.9 + Math.random() * 0.2) * (0.8 + party * 0.1));
    const rewardMul = 1 + s.facilities.board * 0.08;
    return {
      id: s.nextId++, type, title, level, days, maxParty: party, req,
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
    while (s.quests.length < max && guard++ < 10) {
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
    return clamp(c, 0.03, 0.97);
  },

  dispatch(questId, mercIds) {
    const s = this.state;
    const q = s.quests.find((x) => x.id === questId);
    const party = mercIds.map((id) => s.mercs.find((m) => m.id === id)).filter((m) => m && m.status === 'idle');
    if (!q || !party.length) return;
    const chance = this.successChance(q, party);
    s.quests = s.quests.filter((x) => x.id !== questId);
    const mission = { id: s.nextId++, quest: q, party: party.map((m) => m.id), returnDay: s.day + q.days, chance };
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

    const report = { quest: q, outcome, gold: 0, rep: 0, members: [] };
    const hasCleric = party.some((m) => m.cls === 'cleric');
    const rogues = party.filter((m) => m.cls === 'rogue').length;
    const greedy = party.some((m) => m.trait === 'greedy');

    if (outcome === 'great' || outcome === 'success') {
      let gold = q.reward * (outcome === 'great' ? 1.5 : 1);
      gold *= 1 + rogues * 0.12 + (greedy ? 0.1 : 0);
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
      const r = { id: m.id, name: m.name, look: m.look, exp: 0, levelUp: false, injury: 0, dead: false };
      m.missionId = null; m.status = 'idle'; m.quests++;
      // 사망 판정 (대실패 때만)
      let deathChance = outcome === 'disaster' ? 0.3 : 0;
      if (hasCleric) deathChance *= 0.35;
      if (m.trait === 'sturdy') deathChance *= 0.6;
      if (Math.random() < deathChance) {
        r.dead = true;
        s.mercs = s.mercs.filter((x) => x.id !== m.id);
        s.stats.fallen++;
        this.log(`${m.name}이(가) [${q.title}]에서 전사했습니다... 영면하길.`, 'bad');
        report.members.push(r);
        return;
      }
      r.exp = Math.round(baseExp * expMul);
      r.levelUp = this.gainExp(m, r.exp);
      let inj = injuryBase;
      if (hasCleric) inj *= 0.5;
      if (m.trait === 'sturdy' || m.trait === 'coward') inj *= 0.5;
      if (Math.random() < inj) {
        r.injury = rand(2, 4) + (outcome === 'disaster' ? 2 : 0);
        m.status = 'injured'; m.injury = r.injury;
      }
      report.members.push(r);
    });

    const label = { great: '대성공', success: '성공', fail: '실패', disaster: '대실패' }[outcome];
    this.log(`[${q.title}] ${label}! 금화 ${report.gold >= 0 ? '+' : ''}${report.gold}, 명성 ${report.rep >= 0 ? '+' : ''}${report.rep}`,
      outcome === 'great' || outcome === 'success' ? 'good' : 'bad');
    s.pendingReports.push(report);
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
    if (s.quests.length === 0) this.fillQuests(true);

    const newRank = this.rankIndex();
    if (newRank > prevRank) {
      this.log(`용병단 등급이 ${RANKS[newRank].name}랭크로 승급했습니다! 더 어려운 의뢰가 들어옵니다.`, 'good');
      if (RANKS[newRank].name === 'S' && !s.won) {
        s.won = true;
        s.pendingReports.push({ special: 'win' });
      }
    }

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
        s.mercs = s.mercs.filter((x) => x.id !== m.id);
        this.log(`주급을 받지 못한 ${m.name}이(가) 용병단을 떠났습니다!`, 'bad');
      }
      s.gold -= owed;
      this.log(`주급 정산: 금화 ${owed} 지급.${s.gold < 0 ? ' 용병단이 빚을 지고 있습니다!' : ''}`, s.gold < 0 ? 'bad' : '');
    }
    this.refreshRecruits();
    this.log('주점에 새로운 지원자들이 찾아왔습니다.');
  },

  weeklyWageTotal() { return this.state.mercs.reduce((sum, m) => sum + this.wage(m), 0); },
  daysToPayday() { const d = (8 - (this.state.day % 7)) % 7; return d === 0 ? 7 : d; },

  toast(msg) { if (typeof UI !== 'undefined') UI.toast(msg); },
};
