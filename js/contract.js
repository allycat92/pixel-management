// 의뢰: 생성, 파견, 판정, 세력 영향, 대규모 결전, 특별 용병 이야기, 보스
'use strict';

// 지방 등급별 의뢰 난이도 범위
const TIER_LEVELS = [[1, 3], [2, 5], [3, 6], [4, 8], [5, 9], [7, 10]];

// 의뢰 결과가 세계에 주는 영향 (평판, 장악도, 전쟁 판세)
const CONTRACT_EFFECTS = {
  monster:    { win: { issuer: 1 }, lose: { issuer: -2 } },
  raid:       { win: { issuer: 6, target: -8, control: -12, score: 8 }, lose: { issuer: -3 } },
  siege:      { win: { issuer: 10, target: -15, control: -35, score: 12 }, lose: { issuer: -5, target: 2 } },
  sabotage:   { win: { issuer: 7, target: -3, control: -6, mod: -10 }, lose: { issuer: -3, target: -15 } },
  rescue:     { win: { issuer: 8, target: -6, control: -4 }, lose: { issuer: -3, target: -4 } },
  counterspy: { win: { issuer: 5, target: -5, mod: -4 }, lose: { issuer: -2 } },
  warDefense: { win: { issuer: 7, target: -6, control: 20, score: 6 }, lose: { issuer: -4, control: -12, score: -4 } },
  envoy:      { win: { issuer: 6, target: 6, relation: 15, weariness: 25 }, lose: { issuer: -3 } },
  battle:     { win: { issuer: 18, target: -22, score: 30 }, lose: { issuer: -10, target: 3, score: -20 } },
};

// 본거지에서 지방까지 거리(인접 단계)
const HOPS = (() => {
  const d = { royal: 0 };
  const q = ['royal'];
  while (q.length) {
    const p = q.shift();
    ADJACENCY[p].forEach((n) => { if (d[n] == null) { d[n] = d[p] + 1; q.push(n); } });
  }
  return d;
})();

Object.assign(Game, {
  contractLevel(p, bonus = 0) {
    const r = this.rankIndex();
    const [lo0, hi0] = TIER_LEVELS[PROVINCES[p].tier];
    const hi = Math.min(hi0, r + 2);
    const lo = Math.min(Math.max(lo0, r), hi);
    return clamp(rand(lo, hi) + bonus + (Math.random() < 0.15 ? 1 : 0), 1, 10);
  },

  travelDays(p) { return Math.max(1, rand(1, 2) + Math.max(0, (HOPS[p] ?? 2) - 1) - (this.state.branches[p] ? 1 : 0)); },

  monsterEnemy(type, p, level) {
    if (type === 'magic') return MAGIC_ENEMIES[clamp(Math.floor((level - 1) / 2.5), 0, MAGIC_ENEMIES.length - 1)];
    if (type === 'explore' && Math.random() < 0.12) return '미믹';
    return pick(TERRAIN[PROVINCES[p].terrain].enemies);
  },

  // 의뢰를 줄 수 있는 세력인가 (평판 -40 이하면 거래 끊김)
  // 길드 명성이 높으면 다소 껄끄러운 세력도 일을 맡긴다
  willHire(f) { return !f || FACTIONS[f].neutral || this.standing(f) + this.rankIndex() * 4 > -40; },

  // 의뢰가 열릴 지방 고르기
  pickProvince() {
    const s = this.state, r = this.rankIndex();
    const list = PROVINCE_KEYS.filter((p) => this.provinceOpen(p) && this.willHire(this.owner(p)));
    if (!list.length) return 'royal';
    const w = list.map((p) => {
      const [lo, hi] = TIER_LEVELS[PROVINCES[p].tier];
      return 1 + (PROVINCES[p].home ? 1 : 0) + (s.branches[p] ? 2 : 0) + (r + 1 >= lo && r + 1 <= hi ? 1.5 : 0)
        + (this.warsOf(this.owner(p)).length ? 1 : 0);
    });
    let x = Math.random() * w.reduce((a, b) => a + b, 0);
    for (let i = 0; i < list.length; i++) { x -= w[i]; if (x <= 0) return list[i]; }
    return list[0];
  },

  // ───────── 의뢰 만들기 ─────────
  // opts: { province, issuer, target, type, enemy, title, level, size, ... }
  makeContract(opts) {
    const s = this.state;
    const p = opts.province;
    const t = QUEST_TYPES[opts.type];
    const level = opts.level || this.contractLevel(p);
    const issuer = opts.issuer || this.owner(p);
    const target = opts.target || null;
    const enemy = t.cat === 'monster' ? (opts.enemy || this.monsterEnemy(opts.type, p, level)) : null;
    const size = opts.size || ({ monster: rand(2, 4), conflict: { raid: rand(3, 4), siege: rand(4, 6), sabotage: rand(2, 3), rescue: rand(3, 4), warDefense: rand(4, 5), counterspy: rand(2, 3) }[opts.type], diplomacy: 3 }[t.cat]) || 4;
    const days = opts.days || this.travelDays(p) + (level > 5 ? 1 : 0);
    const title = opts.title || pick(t.titles)
      .replace('{e}', enemy || '').replace('{p}', pick(PROVINCES[p].places))
      .replace('{t}', target ? FACTIONS[target].short : '').replace('{i}', FACTIONS[issuer].short);
    const req = Math.round(24 * Math.pow(1.4, level - 1) * (0.9 + Math.random() * 0.2) * (0.8 + Math.min(size, 6) * 0.1));
    // 금화는 전쟁에서 나온다: 전쟁 의뢰 ×1.5, 평시 분쟁 ×0.7, 외교 ×0.6, 괴물·치안 ×0.3
    const war = t.cat === 'campaign' || (!!target && this.atWar(issuer, target));
    const catMul = war ? 1.5 : t.cat === 'conflict' ? 0.7 : t.cat === 'diplomacy' ? 0.6 : 0.3;
    const mul = (1 + s.facilities.board * 0.08) * (s.branches[p] ? 1.1 : 1) * (s.bossDefeated[p] ? 1.1 : 1)
      * this.standingMul(issuer) * catMul * (FACTIONS[issuer].neutral ? 1 : this.doctrine(issuer).pay);
    return {
      id: s.nextId++, type: opts.type, cat: t.cat, war, title, level, size, days, req, province: p, issuer, target, enemy,
      reward: Math.round((40 + level * 30 + level * level * 3) * (0.85 + Math.random() * 0.3) * (1 + days * 0.12) * mul),
      rep: Math.round((4 + level * 3 + (size >= 4 ? 2 : 0)) * (t.cat === 'monster' ? 1 : 1.2)),
      expires: s.day + rand(3, 6),
    };
  },

  // 세력 분쟁 의뢰 시도: 의뢰 세력이 전쟁 중이거나 적대 세력이 있으면 그 상대를 겨냥
  makeConflictContract(issuer) {
    const s = this.state;
    if (!issuer || FACTIONS[issuer].neutral || !this.willHire(issuer)) return null;
    const doc = this.doctrine(issuer);
    const enemies = this.warsOf(issuer);
    // 주적은 관계가 조금만 나빠도 평시 공작 대상이 된다
    const rivals = FACTION_KEYS.filter((f) => f !== issuer && !enemies.includes(f) && this.provincesOf(f).length
      && this.relation(issuer, f) <= (doc.targets[f] ? 10 : -15));
    const weighted = (list) => {
      const w = list.map((t) => doc.bias[t] ?? 1);
      let x = Math.random() * w.reduce((a, b) => a + b, 0);
      for (let i = 0; i < list.length; i++) { x -= w[i]; if (x <= 0) return list[i]; }
      return list[0];
    };
    const pickTarget = (list) => {
      const w = list.map((f) => doc.targets[f] || 1);
      let x = Math.random() * w.reduce((a, b) => a + b, 0);
      for (let i = 0; i < list.length; i++) { x -= w[i]; if (x <= 0) return list[i]; }
      return list[0];
    };
    let target, type, p;
    if (enemies.length && Math.random() < 0.8) {
      target = pickTarget(enemies);
      type = weighted(['raid', 'siege', 'sabotage', 'rescue', 'warDefense', 'envoy']);
    } else if (rivals.length) {
      target = pickTarget(rivals);
      type = weighted(['sabotage', 'rescue', 'counterspy', 'envoy']);
    } else return null;
    if (type === 'warDefense') {
      const fr = this.frontOf(issuer, target).filter((q) => this.provinceOpen(q));
      if (!fr.length) return null;
      p = pick(fr);
    } else if (type === 'envoy') {
      const own = this.provincesOf(issuer).filter((q) => this.provinceOpen(q));
      if (!own.length) return null;
      p = pick(own);
    } else {
      // 상대 지방 중 의뢰 세력이 닿는 곳(원정 거리), 아니면 아무 상대 지방
      let cand = this.reachable(issuer, target).filter((q) => this.provinceOpen(q));
      if (!cand.length) cand = this.provincesOf(target).filter((q) => this.provinceOpen(q));
      if (!cand.length) {
        // 상대 땅에 닿을 수 없으면 의뢰 세력의 땅에서 상대의 첩자를 잡는다
        const own = this.provincesOf(issuer).filter((q) => this.provinceOpen(q));
        if (!own.length || Math.random() < 0.5) return null;
        return this.makeContract({ province: pick(own), issuer, target, type: 'counterspy' });
      }
      p = pick(cand);
    }
    return this.makeContract({ province: p, issuer, target, type });
  },

  makeRandomContract() {
    const p = this.pickProvince();
    const owner = this.owner(p);
    const conflictChance = (this.warsOf(owner).length ? 0.6 : 0.35) * (FACTIONS[owner].neutral ? 1 : this.doctrine(owner).activity);
    if (Math.random() < conflictChance) {
      // 이 지방 소유 세력, 또는 그와 싸우는 세력이 의뢰주
      const issuer = Math.random() < 0.6 ? owner : pick([owner, ...this.warsOf(owner)]);
      const c = this.makeConflictContract(issuer);
      if (c) return c;
    }
    const type = pick(['hunt', 'hunt', 'escort', 'explore', 'magic', 'defense']);
    return this.makeContract({ province: p, type, issuer: owner });
  },

  fillContracts(force) {
    const s = this.state;
    const max = 3 + s.facilities.board;
    s.contracts = s.contracts.filter((c) => c.expires >= s.day);
    const normal = () => s.contracts.filter((c) => !c.story && !c.boss && !c.campaign).length;
    let guard = 0;
    while (normal() < max && guard++ < 12) {
      if (!force && Math.random() < 0.45) break;
      s.contracts.push(this.makeRandomContract());
    }
  },

  // ───────── 대규모 결전 ─────────
  offerCampaign(w) {
    const s = this.state;
    const attacker = this.pickAttacker(w.a, w.b);
    const defender = attacker === w.a ? w.b : w.a;
    const fronts = this.reachable(attacker, defender);
    if (!fronts.length) return;
    const p = pick(fronts);
    const cp = { id: s.nextId++, attacker, defender, slots: 2 };
    // 길드가 아직 그 지방에 닿지 못하면 국력대로 바로 결판
    if (PROVINCES[p].tier > this.rankIndex() + 1 || this.rankIndex() < 1) { this.autoResolveCampaign(cp, p); return; }
    const level = clamp(Math.max(TIER_LEVELS[PROVINCES[p].tier][1], this.rankIndex() + 2), 3, 10);
    cp.slots = level >= 7 ? 3 : 2;
    const sides = [['attack', attacker, defender], ['defend', defender, attacker]];
    let offered = 0;
    sides.forEach(([side, issuer, target]) => {
      if (!this.willHire(issuer)) return;
      const c = this.makeContract({ province: p, issuer, target, type: 'battle', level, size: 4 * cp.slots, days: 4 });
      c.req = Math.round(c.req * 1.05);
      c.reward = Math.round(c.reward * 1.8);
      c.rep = c.rep * 2;
      c.expires = s.day + 5;
      c.title = `${PROVINCES[p].name} ${side === 'attack' ? '공략전' : '방어전'}`;
      c.campaign = { ...cp, side };
      s.contracts.unshift(c);
      offered++;
    });
    if (offered) {
      this.log(`⚔ 대규모 결전 임박: 「${PROVINCES[p].name}」에서 ${FACTIONS[attacker].name}과(와) ${FACTIONS[defender].name}이(가) 맞붙습니다. 양측이 용병단을 모집합니다! (5일 내 결정)`, 'event');
    }
  },

  // ───────── 전력 계산 ─────────
  // units: [{ companyId, memberIds? }]
  unitParts(units) {
    const own = [], ext = [];
    units.forEach((u) => {
      const c = this.company(u.companyId);
      if (!c) return;
      if (c.own) {
        const ms = (u.memberIds || []).map((id) => this.state.mercs.find((m) => m.id === id)).filter(Boolean);
        own.push({ c, ms });
      } else ext.push(c);
    });
    return { own, ext, allMembers: own.flatMap((o) => o.ms) };
  },

  ownCompanyPower(c, ms, type) {
    const base = ms.reduce((sum, m) => sum + this.power(m, type, ms), 0);
    return Math.round(base * this.cohesionMul(c) * this.leaderMul(c));
  },

  unitsPower(contract, units) {
    const { own, ext } = this.unitParts(units);
    return own.reduce((s, o) => s + this.ownCompanyPower(o.c, o.ms, contract.type), 0)
      + ext.reduce((s, c) => s + this.extPower(c, contract.type), 0);
  },
  unitsHeadcount(units) {
    const { allMembers, ext } = this.unitParts(units);
    return allMembers.length + ext.reduce((s, c) => s + c.size, 0);
  },

  // 적대 세력 영토에서는 더 어렵다
  effectiveReq(contract) {
    const o = this.owner(contract.province);
    const hostile = o !== contract.issuer && !FACTIONS[o].neutral && this.standing(o) <= -50;
    return Math.round(contract.req * (hostile ? 1.2 : 1));
  },

  successChance(contract, units) {
    if (!units.length) return 0;
    const { allMembers } = this.unitParts(units);
    const pw = this.unitsPower(contract, units);
    const req = this.effectiveReq(contract);
    let c = 0.5 + ((pw - req) / req) * 0.9;
    if (allMembers.length) {
      c += (new Set(allMembers.map((m) => m.cls)).size - 1) * 0.02;
      c += this.partyMods(allMembers).success;
    }
    const missing = Math.max(0, contract.size - this.unitsHeadcount(units));
    c -= missing * 0.06;
    return clamp(c, 0.03, 0.97);
  },

  contractDays(contract, units) {
    const { allMembers } = this.unitParts(units);
    let d = contract.days;
    if (allMembers.length) d += this.partyMods(allMembers).days;
    if (PROVINCES[contract.province].terrain === 'forest' && this.perk('elves')) d -= 1;
    return Math.max(1, d);
  },

  storyHeroMissing(contract, units) {
    if (!contract.story) return false;
    return !this.unitParts(units).allMembers.some((m) => m.hero === contract.story.hero);
  },

  // ───────── 파견 ─────────
  dispatch(contractId, units) {
    const s = this.state;
    const c = s.contracts.find((x) => x.id === contractId);
    if (!c || !units.length || this.storyHeroMissing(c, units)) return;
    const { own, ext, allMembers } = this.unitParts(units);
    if (own.some((o) => o.c.missionId || !o.ms.length) || ext.some((e) => e.missionId)) return;
    if (allMembers.some((m) => m.status !== 'idle')) return;
    const refused = ext.find((e) => this.extRefusal(e, c));
    if (refused) return this.toast(`「${refused.name}」: ${this.extRefusal(refused, c)}`);
    const chance = this.successChance(c, units);
    const days = this.contractDays(c, units);
    s.contracts = s.contracts.filter((x) => x.id !== contractId && (!c.campaign || !x.campaign || x.campaign.id !== c.campaign.id));
    const mission = { id: s.nextId++, contract: c, units: units.map((u) => ({ ...u })), startDay: s.day, returnDay: s.day + days, chance };
    s.missions.push(mission);
    own.forEach((o) => { o.c.missionId = mission.id; });
    ext.forEach((e) => {
      e.missionId = mission.id;
      // 동조 세력을 치는 의뢰는 마지못해 따른다
      if (e.disposition === 'faction' && e.sympathy === c.target) e.loyalty = Math.max(0, e.loyalty - 10);
    });
    allMembers.forEach((m) => {
      m.status = 'quest'; m.missionId = mission.id; m.lastQuest = s.day;
      m.fatigue = Math.min(100, m.fatigue + 10 + days * 7);
    });
    const names = [...own.map((o) => o.c.name), ...ext.map((e) => e.name)].join(', ');
    this.log(`[${c.title}] ${names} 출격. (${days}일 소요)`);
    this.emit();
  },

  // ───────── 판정 ─────────
  resolveMission(mission) {
    const s = this.state;
    const c = mission.contract;
    const { own, ext, allMembers } = this.unitParts(mission.units);
    const report = { quest: c, outcome: null, gold: 0, rep: 0, members: [], ext: [], standing: [], control: [], notes: [], companies: [] };

    // 결전에서 충성도가 바닥난 외부 용병단은 배신할 수 있다
    let chance = mission.chance;
    if (c.campaign) {
      ext.forEach((e) => {
        if (e.loyalty < 25 && Math.random() < 0.35) {
          chance -= 0.25;
          e.loyalty = 0;
          report.notes.push(`「${e.name}」이(가) 전투 도중 적에게 돌아섰습니다!`);
          this.log(`배신! 「${e.name}」이(가) 결전 도중 ${FACTIONS[c.target].name} 편으로 돌아섰습니다.`, 'bad');
          e.betrayed = true;
        }
      });
    }

    const mods = this.partyMods(allMembers.length ? allMembers : []);
    const roll = Math.random();
    let outcome;
    if (roll < chance * 0.25 * mods.great) outcome = 'great';
    else if (roll < chance) outcome = 'success';
    else if (roll > chance + (1 - chance) * 0.75 && chance < 0.6) outcome = mods.noDisaster ? 'fail' : 'disaster';
    else outcome = 'fail';
    const won = outcome === 'great' || outcome === 'success';
    report.outcome = outcome;

    // 금화: 외부 용병단 몫을 전력 비율대로 떼어 준다
    if (won) {
      let gold = c.reward * (outcome === 'great' ? 1.5 * mods.greatGold : 1) * mods.gold;
      const total = this.unitsPower(c, mission.units) || 1;
      let share = 0;
      ext.filter((e) => !e.betrayed).forEach((e) => { share += gold * (this.extPower(e, c.type) / total) * (e.share / 100); });
      report.share = Math.round(share);
      report.gold = Math.round(gold - share);
      report.rep = Math.round(c.rep * (outcome === 'great' ? 1.5 : 1));
      s.stats.completed++;
      if (Math.random() < mods.loot) {
        const it = this.makeItem(pick(Object.keys(ITEM_BASES)), this.shopMaxTier());
        s.inventory.push(it);
        report.notes.push(`보물 사냥: 「${it.name}」 획득`);
      }
    } else {
      report.gold = outcome === 'fail' ? Math.round(c.reward * 0.1) : 0;
      report.rep = -Math.round(c.rep * (outcome === 'disaster' ? 0.6 : 0.3));
      s.stats.failed++;
    }
    s.gold += report.gold;
    s.rep = Math.max(0, s.rep + report.rep);

    // 세력 영향
    this.applyContractEffects(c, outcome, report);

    // 직속 단원
    const baseExp = (15 + c.level * 18) * (this.perk('clans') ? 1.2 : 1);
    const expMul = { great: 1.5, success: 1, fail: 0.5, disaster: 0.3 }[outcome];
    const injuryBase = { great: 0.05, success: 0.15, fail: 0.4, disaster: 0.7 }[outcome];
    const dead = [];
    allMembers.forEach((m) => {
      const r = { id: m.id, name: m.name, cls: m.cls, look: m.look, exp: 0, levelUp: false, injury: 0, dead: false, company: m.companyId };
      m.missionId = null; m.status = 'idle'; m.quests++;
      if (won && m.hero) m.bond += HEROES[m.hero].faction && this.standing(HEROES[m.hero].faction) >= 45 ? 2 : 1;
      let deathChance = (outcome === 'disaster' ? 0.3 : 0) * mods.death;
      if (m.trait === 'sturdy') deathChance *= 0.6;
      if (Math.random() < deathChance) {
        r.dead = true;
        dead.push(r);
        s.stats.fallen++;
        if (m.hero) s.heroes[m.hero].dead = true;
        this.removeMerc(m, `[${c.title}]에서 전사했습니다... 유품(장비)은 창고로 돌아왔습니다.`, 'bad');
        report.members.push(r);
        return;
      }
      r.exp = Math.round(baseExp * expMul);
      r.levelUp = this.gainExp(m, r.exp);
      let inj = injuryBase * mods.injury;
      if (m.trait === 'sturdy' || m.trait === 'coward' || m.trait === 'northknight') inj *= 0.5;
      if (m.fatigue >= 80) inj *= 1.5;
      const dm = { great: 6, success: 2, fail: -6, disaster: -12 }[outcome];
      if (dm > 0 || !mods.noMoraleLoss) this.changeMorale(m, dm);
      if (Math.random() < inj) {
        r.injury = rand(2, 4) + (outcome === 'disaster' ? 2 : 0);
        if (mods.healHalf) r.injury = Math.ceil(r.injury / 2);
        m.status = 'injured'; m.injury = r.injury;
      }
      report.members.push(r);
    });
    // 관계
    const survivors = allMembers.filter((m) => s.mercs.includes(m));
    for (let i = 0; i < survivors.length; i++) {
      for (let j = i + 1; j < survivors.length; j++) {
        const a = survivors[i], b = survivors[j];
        const before = this.rel(a, b);
        const d = this.traitsClash(a, b) ? -6 : (outcome === 'great' ? 8 : won ? 5 : 3) * (a.companyId === b.companyId ? 1 : 0.5);
        this.addRel(a, b, d);
        if (before < FRIEND_REL && this.rel(a, b) >= FRIEND_REL) this.log(`${a.name}와(과) ${b.name}이(가) 전우가 되었습니다!`, 'good');
        if (before > RIVAL_REL && this.rel(a, b) <= RIVAL_REL) this.log(`${a.name}와(과) ${b.name}의 사이가 틀어졌습니다.`, 'bad');
      }
    }
    dead.forEach((r) => {
      s.mercs.forEach((m) => {
        const grief = (m.rel && m.rel[r.id]) >= FRIEND_REL;
        this.changeMorale(m, grief ? -25 : -8);
        if (grief) this.log(`${m.name}이(가) 전우 ${r.name}의 죽음에 깊이 슬퍼합니다.`, 'bad');
      });
    });
    // 용병단 기록과 결속도
    own.forEach((o) => {
      o.c.missionId = null;
      if (won) o.c.wins++; else o.c.losses++;
      const lostHere = dead.filter((r) => r.company === o.c.id).length;
      o.c.cohesion = clamp(o.c.cohesion + (won ? 5 : 2) - lostHere * 20, 0, 100);
      report.companies.push({ name: o.c.name, color: o.c.color, own: true });
    });
    ext.forEach((e) => {
      const before = e.loyalty;
      const lost = e.betrayed ? 0 : this.extAfterMission(e, outcome, c);
      if (e.betrayed) { e.missionId = null; this.state.companies = this.state.companies.filter((x) => x.id !== e.id); }
      report.ext.push({ name: e.name, color: e.color, look: e.captain.look, lost, loyalty: e.loyalty - before, betrayed: !!e.betrayed });
      report.companies.push({ name: e.name, color: e.color, own: false });
    });

    if (won) s.provClears[c.province] = (s.provClears[c.province] || 0) + 1;
    const label = { great: '대성공', success: '성공', fail: '실패', disaster: '대실패' }[outcome];
    this.log(`[${c.title}] ${label}! 금화 ${report.gold >= 0 ? '+' : ''}${report.gold}, 명성 ${report.rep >= 0 ? '+' : ''}${report.rep}`, won ? 'good' : 'bad');
    s.pendingReports.push(report);

    if (c.boss) {
      if (won) this.defeatBoss(c.boss);
      else s.contracts.unshift({ ...c, id: s.nextId++ });
    }
    if (c.story) {
      if (won) this.completeStory(c.story);
      else if (!s.heroes[c.story.hero].dead) {
        s.contracts.unshift({ ...c, id: s.nextId++ });
        this.log(`「${c.title}」은(는) 다시 도전할 수 있습니다.`);
      }
    }
  },

  // ───────── 세력 영향 적용 ─────────
  applyContractEffects(c, outcome, report) {
    const won = outcome === 'great' || outcome === 'success';
    const eff = (CONTRACT_EFFECTS[c.cat === 'monster' ? 'monster' : c.type] || CONTRACT_EFFECTS.monster)[won ? 'win' : 'lose'];
    const boost = outcome === 'great' ? 1.3 : 1;
    const out = report.standing;
    if (eff.issuer) this.changeStanding(c.issuer, Math.round(eff.issuer * (eff.issuer > 0 ? boost : 1)), out);
    if (eff.target && c.target) this.changeStandingWithAllies(c.target, eff.target, out);
    // 공작은 성공해도 정체가 드러날 수 있다
    if (c.type === 'sabotage' && won && c.target && Math.random() < 0.3) {
      this.changeStanding(c.target, -9, out);
      report.notes.push(`${FACTIONS[c.target].name}에 길드의 개입이 드러났습니다.`);
    }
    if (eff.mod && c.target) this.state.factions[c.target].mod += eff.mod;
    const w = c.target ? this.war(c.issuer, c.target) : null;
    const scoreFor = (d) => { if (w) w.score += w.a === c.issuer ? d : -d; };

    if (c.type === 'battle' && c.campaign) {
      const cp = c.campaign;
      const p = c.province;
      if (won && cp.side === 'attack') { if (this.owner(p) === c.target && this.atWar(c.issuer, c.target)) this.transferProvince(p, c.issuer); }
      else if (won && cp.side === 'defend') this.changeControl(p, 40, null, report.control);
      else if (!won && cp.side === 'defend') { if (this.owner(p) === c.issuer && this.atWar(c.issuer, c.target)) this.transferProvince(p, c.target); }
      else this.changeControl(p, 15, null, report.control);
      scoreFor(eff.score);
      if (w) w.weariness += 10;
      return;
    }
    if (eff.control) {
      const p = c.province;
      const o = this.owner(p);
      if (eff.control < 0 && o === c.target) this.changeControl(p, eff.control, c.issuer, report.control);
      if (eff.control > 0 && o === c.issuer) this.changeControl(p, eff.control, null, report.control);
      if (c.type === 'warDefense' && !won && o === c.issuer) this.changeControl(p, eff.control, c.target, report.control);
    }
    if (eff.score) scoreFor(eff.score);
    if (eff.relation && c.target) this.changeRelation(c.issuer, c.target, eff.relation);
    if (eff.weariness && w) w.weariness += eff.weariness;
  },

  // ───────── 특별 용병 ─────────
  makeHero(key) {
    const h = HEROES[key];
    const m = this.makeMerc(h.cls, h.level);
    const g = CLASSES[h.cls].growth;
    m.name = h.name; m.hero = key; m.trait = h.trait; m.title = h.title;
    m.look = { cls: h.cls, ...h.look };
    if (h.adv) this.applyPromotion(m, h.adv);
    const main = Object.keys(g).filter((k) => k !== 'hp').sort((a, b) => g[b] - g[a])[0];
    m[main] += 3; m.maxHp += 4;
    return m;
  },

  checkHeroes() {
    const s = this.state, r = this.rankIndex();
    Object.entries(HEROES).forEach(([key, h]) => {
      if (!s.heroes[key]) s.heroes[key] = { appeared: false, hired: false, ch: 0, dead: false };
      const hs = s.heroes[key];
      if (!hs.appeared && r >= h.unlock && (!h.faction || this.standing(h.faction) > -30)) {
        hs.appeared = true;
        s.recruits.unshift(this.makeHero(key));
        this.log(`모집소에 특별한 손님이 찾아왔습니다: 「${h.title}」 ${h.name}`, 'event');
        s.pendingReports.push({ special: 'dialog', hero: key, title: `${h.title} ${h.name}`, lines: h.intro, foot: '모집소에서 고용할 수 있습니다.' });
      }
    });
    s.mercs.filter((m) => m.hero).forEach((m) => {
      const hs = s.heroes[m.hero], h = HEROES[m.hero];
      const ch = h.chapters[hs.ch];
      if (!ch || m.bond < ch.bond || !this.provinceOpen(ch.province)) return;
      const posted = s.contracts.some((c) => c.story && c.story.hero === m.hero)
        || s.missions.some((mi) => mi.contract.story && mi.contract.story.hero === m.hero);
      if (posted) return;
      const owner = this.owner(ch.province);
      const target = ch.target && ch.target !== owner && !this.provincesOf(ch.target).length ? null : ch.target;
      let issuer = 'locals';
      if (!target) issuer = owner;
      else if (owner !== target && !FACTIONS[owner].neutral) issuer = owner;
      else if (h.faction && h.faction !== target) issuer = h.faction;
      const level = clamp(Math.max(TIER_LEVELS[PROVINCES[ch.province].tier][0], this.rankIndex() + 2), 1, 10);
      const c = this.makeContract({ province: ch.province, type: ch.type, target, issuer, enemy: ch.enemy, title: ch.title, level, size: 4 });
      c.story = { hero: m.hero, ch: hs.ch };
      c.expires = STORY_EXPIRES;
      c.reward = Math.round(c.reward * 1.5);
      c.rep *= 2;
      s.contracts.unshift(c);
      this.log(`${m.name}의 개인 의뢰 「${ch.title}」이(가) 올라왔습니다!`, 'event');
      s.pendingReports.push({ special: 'dialog', hero: m.hero, title: `개인 의뢰: ${ch.title}`, lines: ch.before, foot: `${m.name}이(가) 속한 용병단을 보내야 합니다.` });
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
      gains.push(`전설 장비 「${it.name}」`);
    }
    if (rw.stats && m) {
      Object.entries(rw.stats).forEach(([k, v]) => { m[k === 'hp' ? 'maxHp' : k] += v; });
      gains.push(`${m.name} ${Object.entries(rw.stats).map(([k, v]) => `${STAT_NAMES[k]}+${v}`).join(' ')}`);
    }
    if (rw.rep) { s.rep += rw.rep; gains.push(`명성 +${rw.rep}`); }
    if (rw.standing) Object.entries(rw.standing).forEach(([f, d]) => { this.changeStanding(f, d); gains.push(`${FACTIONS[f].short} 평판 ${d > 0 ? '+' : ''}${d}`); });
    if (rw.newTitle && m) { m.title = rw.newTitle; gains.push(`칭호 「${rw.newTitle}」`); }
    if (rw.awaken && m) { m.awakened = true; gains.push(`${m.name} 각성 (전투력 +15%)`); }
    this.log(`${h.name}의 이야기 「${ch.title}」 완료! ${gains.join(', ')}`, 'good');
    s.pendingReports.push({ special: 'dialog', hero: story.hero, title: `${ch.title} — 완료`, lines: ch.after, foot: gains.join(' · '),
      choice: ch.choice ? { hero: story.hero, ch: story.ch } : null });
  },

  // 이야기 선택지 결과 적용 (UI에서 호출)
  applyChoice(heroKey, chIdx, optIdx) {
    const ch = HEROES[heroKey].chapters[chIdx];
    const opt = ch.choice.options[optIdx];
    const notes = this.applyEffects(opt.effects);
    this.log(`${HEROES[heroKey].name}의 선택 — ${opt.label}${notes.length ? ` (${notes.join(', ')})` : ''}`, 'event');
    this.save();
    return { lines: opt.after, notes };
  },

  // 공통 효과 묶음 적용: { standing, relations, peace, gold }
  applyEffects(e) {
    const notes = [];
    if (!e) return notes;
    if (e.standing) Object.entries(e.standing).forEach(([f, d]) => { this.changeStanding(f, d); notes.push(`${FACTIONS[f].short} 평판 ${d > 0 ? '+' : ''}${d}`); });
    if (e.relations) Object.entries(e.relations).forEach(([k, d]) => {
      const [a, b] = k.split('|');
      this.changeRelation(a, b, d);
      notes.push(`${FACTIONS[a].short}↔${FACTIONS[b].short} 관계 ${d > 0 ? '+' : ''}${d}`);
    });
    if (e.peace) { const [a, b] = e.peace.split('|'); if (this.atWar(a, b)) { this.endWar(a, b, '그롬의 중재로'); notes.push('휴전 성립'); } }
    if (e.gold) { this.state.gold += e.gold; notes.push(`금화 +${e.gold}`); }
    return notes;
  },

  // ───────── 재앙급 괴물 ─────────
  checkBosses() {
    const s = this.state;
    Object.entries(BOSSES).forEach(([p, b]) => {
      if (s.bossDefeated[p] || !this.provinceOpen(p)) return;
      if ((s.provClears[p] || 0) < b.clears) return;
      if (s.contracts.some((c) => c.boss === p) || s.missions.some((mi) => mi.contract.boss === p)) return;
      const level = TIER_LEVELS[PROVINCES[p].tier][1];
      const c = this.makeContract({ province: p, type: b.type, enemy: b.enemy, title: b.title, level, size: 5 });
      c.cat = 'monster';
      c.boss = p;
      c.req = Math.round(c.req * 1.3);
      c.reward = Math.round(c.reward * 4);
      c.rep *= 3;
      c.expires = STORY_EXPIRES;
      s.contracts.unshift(c);
      this.log(`재앙 출현! 「${PROVINCES[p].name}」에 「${b.name}」이(가) 나타났습니다.`, 'event');
      s.pendingReports.push({ special: 'notice', enemy: b.enemy, title: `재앙 출현: ${b.name}`, lines: [[null, b.intro]], foot: '의뢰 목록에 토벌 의뢰가 올라왔습니다. 마감은 없습니다.' });
    });
  },

  defeatBoss(p) {
    const s = this.state, b = BOSSES[p];
    s.bossDefeated[p] = true;
    const it = this.makeUniqueItem(b.reward);
    s.inventory.push(it);
    const o = this.owner(p);
    const notes = [`전설 장비 「${it.name}」`, `${PROVINCES[p].name} 의뢰 보상 +10%`];
    if (!FACTIONS[o].neutral) { this.changeStanding(o, 20); notes.push(`${FACTIONS[o].short} 평판 +20`); }
    this.log(`「${b.name}」 토벌! ${notes.join(', ')}`, 'good');
    s.pendingReports.push({ special: 'notice', enemy: b.enemy, title: `${b.name} 토벌!`, lines: [[null, b.outro]], foot: notes.join(' · ') });
    if (Object.keys(BOSSES).every((k) => s.bossDefeated[k])) s.pendingReports.push({ special: 'legend' });
  },
});
