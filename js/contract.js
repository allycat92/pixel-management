// 의뢰: 생성, 파견, 판정, 세력 영향, 대규모 결전, 특별 용병 이야기, 보스
'use strict';

// 지방 등급별 의뢰 난이도 범위
const TIER_LEVELS = [[1, 3], [2, 5], [3, 6], [4, 8], [5, 9], [7, 10]];
const LATE_MAX_LEVEL = 14;
// 권장 인원: 용병단 하나가 3~4명이므로 일반 의뢰는 2~4명, 결전은 용병단 수 × 3 + 1, 최종 결전은 3개 용병단 거의 만원
const FINAL_SIZE = 11;

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
  // 재앙이 대두한 뒤에는 의뢰 난이도 상한이 열린다 (★10 → ★14)
  lateGame() { return !!(this.state.calamity || this.state.calamityDefeated); },
  maxContractLevel() { return this.lateGame() ? LATE_MAX_LEVEL : 10; },

  contractLevel(p, bonus = 0) {
    // 전투 모드: 길드 전력에 맞춰 쉬운 것부터 벅찬 것까지 (js/muster.js battleLevel). 용병단이 없으면 아래 옛 규칙
    const bl = this.battleMode && this.battleMode() ? this.battleLevel(p, bonus) : null;
    if (bl) return bl;
    const r = this.rankIndex(), late = this.lateGame();
    const [lo0, hi0] = TIER_LEVELS[PROVINCES[p].tier];
    const hi = late ? Math.min(hi0 + 4, r + 6) : Math.min(hi0, r + 2);
    const lo = Math.min(Math.max(lo0 + (late ? 2 : 0), r), hi);
    return clamp(rand(lo, hi) + bonus + (Math.random() < 0.15 ? 1 : 0), 1, this.maxContractLevel());
  },

  travelDays(p) { return Math.max(1, rand(1, 2) + Math.max(0, (HOPS[p] ?? 2) - 1) - (this.state.branches[p] ? 1 : 0)); },

  monsterEnemy(type, p, level) {
    if (type === 'magic') return MAGIC_ENEMIES[clamp(Math.floor((level - 1) / 2.5), 0, MAGIC_ENEMIES.length - 1)];
    if (type === 'explore' && Math.random() < 0.12) return '미믹';
    return pick(TERRAIN[PROVINCES[p].terrain].enemies);
  },

  // 의뢰를 줄 수 있는 세력인가 (평판 -40 이하면 거래 끊김)
  // 길드 명성이 높으면 다소 껄끄러운 세력도 일을 맡긴다
  willHire(f) {
    if (!f || FACTIONS[f].neutral) return true;
    if (this.isCalamity(f) || this.isDestroyed(f)) return false; // 재앙은 용병을 고용하지 않는다
    return this.standing(f) + this.rankIndex() * 4 > -40;
  },

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
    const issuer = opts.issuer || this.owner(p);
    const target = opts.target || null;
    this._aim = null;
    const level = opts.level || this.contractLevel(p, this.isCalamity(target) ? 1 : 0); // 재앙 토벌은 한 단계 더 험하다
    const aim = this._aim;   // 전투 모드: battleLevel 이 겨냥한 예상 단계 (게시판의 층 나누기)
    const enemy = t.cat === 'monster' ? (opts.enemy || this.monsterEnemy(opts.type, p, level))
      : this.isCalamity(target) ? (opts.enemy || pick(FACTIONS[target].monsters)) : (opts.enemy || null);
    const size = opts.size || ({ monster: rand(2, 3), conflict: { raid: 3, siege: rand(3, 4), sabotage: 2, rescue: 3, warDefense: rand(3, 4), counterspy: 2 }[opts.type], diplomacy: 3 }[t.cat]) || 3;
    const days = opts.days || this.travelDays(p) + (level > 5 ? 1 : 0);
    const title = opts.title || pick(t.titles)
      .replace('{e}', enemy || '').replace('{p}', pick(PROVINCES[p].places))
      .replace('{t}', target ? FACTIONS[target].short : '')
      .replace('{tWith}', target ? josa(FACTIONS[target].short, '과', '와') : '')
      .replace('{i}', FACTIONS[issuer].short);
    // 권장 인원이 용병단 크기에 맞춰 줄었으므로(옛 4~6명 → 2~4명) 요구 전투력은 옛 인원 기준(×1.25)으로 매긴다
    const req = Math.round(24 * Math.pow(1.4, level - 1) * (0.9 + Math.random() * 0.2) * (0.8 + Math.min(size * 1.25, 6) * 0.1));
    // 금화는 전쟁에서 나온다: 전쟁 의뢰 ×1.5, 평시 분쟁 ×0.7, 외교 ×0.6, 괴물·치안 ×0.3
    const war = t.cat === 'campaign' || (!!target && this.atWar(issuer, target));
    let catMul = war ? 1.5 : t.cat === 'conflict' ? 0.7 : t.cat === 'diplomacy' ? 0.6 : 0.3;
    if (s.calamityDefeated && !war) catMul *= 1.8; // 재앙 이후 전후 복구 의뢰
    const mul = (1 + s.facilities.board * 0.08) * (s.branches[p] ? 1.1 : 1) * (s.bossDefeated[p] ? 1.1 : 1)
      * this.standingMul(issuer) * catMul * (FACTIONS[issuer].neutral ? 1 : this.doctrine(issuer).pay);
    const c = {
      id: s.nextId++, type: opts.type, cat: t.cat, war, title, level, size, days, req, province: p, issuer, target, enemy,
      reward: Math.round((40 + level * 30 + level * level * 3) * (0.85 + Math.random() * 0.3) * (1 + days * 0.12) * mul),
      // 큰 의뢰 명성 보너스: 옛 기준(4명 이상)을 줄어든 권장 인원에 맞춰 3명 이상으로 — 이야기·보스·분쟁 의뢰는 예전처럼 받는다.
      // 외교 의뢰는 인원을 줄이지 않았으므로 예전처럼 없고, 괴물 의뢰(옛 2~4명 중 1/3만 받던 것)는 뺀다:
      // 3~4인 편제로 이미 등급이 빨리 오르므로(봇 S등급 79일 → 73일), 괴물 의뢰에 다시 주면 68일로 더 빨라진다.
      rep: Math.round((4 + level * 3 + (size >= 3 && t.cat !== 'diplomacy' && t.cat !== 'monster' ? 2 : 0)) * (t.cat === 'monster' ? 1 : 1.2)),
      expires: s.day + rand(3, 6),
    };
    // 전투 모드: 저장의 소금을 의뢰에 굳혀 둔다 (전투 시드·적 편성. 날마다 바뀌지 않고, 의뢰 번호로 미리 알 수 없다)
    if (s.resolve === 'battle' && s.salt) c.bseed = Stats.mix(s.salt, c.id, 0x5a17);
    if (s.resolve === 'battle' && aim != null) c.aim = aim;
    return c;
  },

  // 세력 분쟁 의뢰 시도: 의뢰 세력이 전쟁 중이거나 적대 세력이 있으면 그 상대를 겨냥
  makeConflictContract(issuer) {
    const s = this.state;
    if (!issuer || FACTIONS[issuer].neutral || !this.willHire(issuer)) return null;
    const doc = this.doctrine(issuer);
    let enemies = this.warsOf(issuer);
    const cal = this.state.calamity;
    if (cal && enemies.includes(cal) && Math.random() < 0.75) enemies = [cal];
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
      type = this.isCalamity(target) ? pick(['raid', 'raid', 'siege', 'rescue', 'warDefense', 'warDefense'])
        : weighted(['raid', 'siege', 'sabotage', 'rescue', 'warDefense', 'envoy']);
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

  campaignSize(slots) { return slots * 3 + 1; },

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
    // 전투 모드: 게시판이 BM_BOARD_EXTRA 칸 넓다 — 벅찬 의뢰가 이길 만한 일감의 자리를 빼앗지 않게 (검증 3·5번)
    const max = 3 + s.facilities.board + (s.resolve === 'battle' ? Stats.KN.BM_BOARD_EXTRA : 0);
    s.contracts = s.contracts.filter((c) => c.expires >= s.day);
    const normal = () => s.contracts.filter((c) => !c.story && !c.boss && !c.campaign).length;
    let guard = 0;
    while (normal() < max && guard++ < 12) {
      if (!force && Math.random() < 0.45) break;
      s.contracts.push(this.makeRandomContract());
    }
    if (s.resolve === 'battle') this.reliefCheck();   // 전투 모드: 대장만 남은 길드에 구호 의뢰
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
    const late = this.lateGame() ? 3 : 0;
    const level = clamp(Math.max(TIER_LEVELS[PROVINCES[p].tier][1], this.rankIndex() + 2) + late, 3, this.maxContractLevel());
    cp.slots = level >= 7 ? 3 : 2;
    const sides = [['attack', attacker, defender], ['defend', defender, attacker]];
    let offered = 0;
    sides.forEach(([side, issuer, target]) => {
      if (!this.willHire(issuer)) return;
      const c = this.makeContract({ province: p, issuer, target, type: 'battle', level, size: this.campaignSize(cp.slots), days: 4 });
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
      this.log(`⚔ 대규모 결전 임박: 「${PROVINCES[p].name}」에서 ${FACTIONS[attacker].name}${josa(FACTIONS[attacker].name, '과', '와')} ${FACTIONS[defender].name}${josa(FACTIONS[defender].name, '이', '가')} 맞붙습니다. 양측이 용병단을 모집합니다! (5일 내 결정)`, 'event');
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

  ownCompanyPower(c, ms, type, contract) {
    const base = ms.reduce((sum, m) => sum + this.power(m, type, ms) * this.memberLeadMul(c, m, ms), 0);
    return Math.round(base * SQUAD_POWER * this.cohesionMul(c) * this.leaderMul(c, type, ms, contract));
  },

  unitsPower(contract, units) {
    const { own, ext } = this.unitParts(units);
    return own.reduce((s, o) => s + this.ownCompanyPower(o.c, o.ms, contract.type, contract), 0)
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
  // 한 의뢰에 보낼 수 있는 용병단 수: 일반 의뢰 1개, 결전은 의뢰에 적힌 수(2~3), 어떤 경우에도 3개까지
  dispatchSlots(contract) { return Math.min(MAX_DISPATCH, contract.campaign ? contract.campaign.slots : 1); },
  dispatch(contractId, units) {
    const s = this.state;
    const c = s.contracts.find((x) => x.id === contractId);
    if (!c || !units.length || this.storyHeroMissing(c, units)) return;
    const slots = this.dispatchSlots(c);
    if (units.length > slots) return this.toast(`이 의뢰에는 용병단을 ${slots}개까지만 보낼 수 있습니다. (직속·외부 합계, 최대 ${MAX_DISPATCH}개)`);
    const { own, ext, allMembers } = this.unitParts(units);
    if (own.some((o) => o.c.missionId || !o.ms.length) || ext.some((e) => e.missionId)) return;
    if (own.some((o) => o.ms.length > SQUAD_MAX || o.ms.some((m) => m.companyId !== o.c.id))) return;
    if (allMembers.some((m) => m.status !== 'idle')) return;
    const refused = ext.find((e) => this.extRefusal(e, c));
    if (refused) return this.toast(`「${refused.name}」: ${this.extRefusal(refused, c)}`);
    const chance = this.successChance(c, units);
    const days = this.contractDays(c, units);
    s.contracts = s.contracts.filter((x) => x.id !== contractId && (!c.campaign || !x.campaign || x.campaign.id !== c.campaign.id));
    const mission = { id: s.nextId++, contract: c, units: units.map((u) => ({ ...u })), startDay: s.day, returnDay: s.day + days, chance };
    // 전투 입력을 지금(출격 피로가 붙기 전) 굳혀 둔다: mission.spec, mission.est (js/muster.js). 아직은 그림자 — 결과는 chance 가 정한다.
    if (this.freezeMission) this.freezeMission(mission, c, units);
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
          report.notes.push(`「${e.name}」${josa(e.name, '이', '가')} 전투 도중 적에게 돌아섰습니다!`);
          this.log(`배신! 「${e.name}」${josa(e.name, '이', '가')} 결전 도중 ${FACTIONS[c.target].name} 편으로 돌아섰습니다.`, 'bad');
          e.betrayed = true;
        }
      });
    }

    const mods = this.partyMods(allMembers.length ? allMembers : []);
    // 전투 모드(Game.RESOLVE === 'battle'): 굳혀 둔 편성의 전투가 결과를 정한다 (js/muster.js battleResolve). 그 밖에는 오늘의 판정 그대로
    // 결과를 정하는 방식은 출격한 때의 것이다 (검증 7번): 전투 모드에서 굳힌 편성(spec.bm)만 전투가 정하고, 'roll' 때 떠난 출격은 모드를 바꿔도 판정으로 끝난다
    const fought = mission.spec && mission.spec.bm ? this.battleResolve(mission, report, mods) : null;
    let outcome;
    if (fought) outcome = fought.verdict.outcome;
    else {
      const roll = Math.random();
      if (roll < chance * 0.25 * mods.great) outcome = 'great';
      else if (roll < chance) outcome = 'success';
      else if (roll > chance + (1 - chance) * 0.75 && chance < 0.6) outcome = mods.noDisaster ? 'fail' : 'disaster';
      else outcome = 'fail';
    }
    const won = outcome === 'great' || outcome === 'success';
    report.outcome = outcome;
    report.seed = rand(1, 1e9); // 전투 연출용 시드 (옛 재생용. 전투 모드는 report.battle.spec 을 그대로 재생한다)
    // 그림자 전투: 굳혀 둔 편성으로 능력치 전투를 한 번 돌려 report.shadow 에 적는다 (결과·화면·난수와 무관, js/muster.js)
    if (!fought && this.shadowResolve) this.shadowResolve(mission, report, mods);
    const fates = fought ? this.fatesOf(fought.spec, fought.rec) : null;
    const KB = Stats.KN;

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
    } else if (fought) {
      // 전투 모드: 무찌른 적 전력만큼 보수를 받는다 (실패 10% + 비율 × 0.5, 대참사는 비율 몫만). 패배 뒤 한 주는 탈주가 없다
      // 질서 있게 물러난 판(end 'retreat')은 우리 단원이 모두 쓰러졌어도(수습만 물러남) 기본 몫을 받는다 (검증 7번)
      const orderly = fought.rec.end === 'retreat';
      report.gold = Math.round(c.reward * ((outcome === 'fail' || orderly ? KB.LOSS_PAY : 0) + KB.LOSS_PAY_SHARE * fought.share));
      report.rep = -Math.round(c.rep * (outcome === 'disaster' ? 0.6 : 0.3));
      if (fought.share >= 0.05) report.notes.push(`적 전력의 ${Math.round(fought.share * 100)}%를 꺾어 보수 일부(금화 ${report.gold})를 받았습니다.`);
      // 유예 주간은 GRACE_EVERY 일에 한 번만 새로 열린다 (연달아 지는 동안 끝없이 이어지지 않게)
      if (!s.graceStart || s.day >= s.graceStart + KB.GRACE_EVERY) { s.graceStart = s.day; s.graceUntil = s.day + KB.GRACE_DAYS; }
      s.stats.failed++;
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
    const special = fought && this.specialBattle(c);
    allMembers.forEach((m) => {
      const r = { id: m.id, name: m.name, cls: m.cls, look: m.look, exp: 0, levelUp: false, injury: 0, dead: false, company: m.companyId };
      m.missionId = null; m.status = 'idle'; m.quests++;
      if (won && m.hero) m.bond += HEROES[m.hero].faction && this.standing(HEROES[m.hero].faction) >= 45 ? 2 : 1;
      // 전투 모드: 실제로 쓰러진 단원만 다치거나(죽거나) 한다. 편성에 들지 못한 단원(옛 저장의 큰 용병단)은 서 있던 것으로 본다
      const f = fates ? (fates.get(m.id) || { fate: 0, hp: 100 }) : null;
      if (f) { r.down = f.fate === 1; r.fled = f.fate === 2; }
      let deathChance = (outcome === 'disaster' ? 0.3 : 0) * mods.death;
      // 전투 모드의 사망: 특별한 전투의 대참사에서 쓰러진 단원만, 용병단마다 한 명까지, 길드 인원이 GUILD_FLOOR 아래로는 안 된다 (설계 6장 + 주인 결정 2)
      if (f) deathChance = special && outcome === 'disaster' && f.fate === 1 && !dead.some((d) => d.company === m.companyId) && s.mercs.length > KB.GUILD_FLOOR ? KB.DEATH_P * mods.death : 0;
      if (this.isCaptain(m)) deathChance = 0; // 용병대장은 쓰러져도 죽지 않는다 (대신 크게 다친다)
      if (m.trait === 'sturdy') deathChance *= 0.6;
      if ((!f || deathChance > 0) && Math.random() < deathChance) {   // 옛 판정은 확률이 0 이어도 굴린다 (난수 순서 유지)
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
      if (f) {
        // 전투 모드의 부상 (설계 6장): 쓰러짐 — 이기면 0.6, 지면 0.9 (대참사 +2일), 서 있었지만 체력 25% 미만 — 0.3 (1~2일), 물러남 — 없음.
        let inj = f.fate === 1 ? (won ? KB.INJ_WIN : KB.INJ_LOSE) : f.fate === 0 && f.hp < 25 ? KB.INJ_LOW : 0;
        inj *= mods.injury;
        if (m.trait === 'sturdy' || m.trait === 'coward' || m.trait === 'northknight') inj *= 0.5;
        // 죽지 않은 단원: 대장이든, 특별하지 않은 전투든, 길드 인원 하한·용병단당 한 명 규칙에 막혔든 (설계 6장 규칙 5) 반드시 다친다
        if (f.fate === 1 && outcome === 'disaster') inj = 1;
        let dm = { great: 6, success: 2, fail: -6, disaster: -12 }[outcome];
        if (!won && fought.rec.end === 'retreat') dm = Math.round(dm * KB.RETREAT_MORALE);   // 질서 있게 물러났다 (대참사도: 남은 수습이 데리고 물러났다)
        if (dm > 0 || !mods.noMoraleLoss) this.changeMorale(m, dm);
        if (inj > 0 && Math.random() < inj) {
          r.injury = f.fate === 1 ? rand(2, 4) + (outcome === 'disaster' ? 2 : 0) : rand(1, 2);
          if (mods.healHalf) r.injury = Math.ceil(r.injury / 2);
          m.status = 'injured'; m.injury = r.injury;
        }
        report.members.push(r);
        return;
      }
      let inj = injuryBase * mods.injury;
      if (m.trait === 'sturdy' || m.trait === 'coward' || m.trait === 'northknight') inj *= 0.5;
      if (this.isCaptain(m) && outcome === 'disaster') inj = 1;
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
        if (before < FRIEND_REL && this.rel(a, b) >= FRIEND_REL) this.log(`${a.name}${josa(a.name, '과', '와')} ${b.name}${josa(b.name, '이', '가')} 전우가 되었습니다!`, 'good');
        if (before > RIVAL_REL && this.rel(a, b) <= RIVAL_REL) this.log(`${a.name}${josa(a.name, '과', '와')} ${b.name}의 사이가 틀어졌습니다.`, 'bad');
      }
    }
    dead.forEach((r) => {
      s.mercs.forEach((m) => {
        const grief = (m.rel && m.rel[r.id]) >= FRIEND_REL;
        this.changeMorale(m, grief ? -25 : -8);
        if (grief) this.log(`${m.name}${josa(m.name, '이', '가')} 전우 ${r.name}의 죽음에 깊이 슬퍼합니다.`, 'bad');
      });
    });
    // 용병단 기록과 결속도
    own.forEach((o) => {
      o.c.missionId = null;
      if (won) o.c.wins++; else o.c.losses++;
      const lostHere = dead.filter((r) => r.company === o.c.id).length;
      o.c.cohesion = clamp(o.c.cohesion + (won ? 5 : 2) - lostHere * 20, 0, 100);
      // 옛 저장에서 출격 중이던 큰 용병단은 귀환 후 정원에 맞춘다
      const moved = this.trimCompany(o.c);
      if (moved.length) {
        const note = `편제 개편: 「${o.c.name}」의 ${moved.map((m) => m.name).join(', ')}${josa(moved.map((m) => m.name).join(', '), '이', '가')} 예비 인원으로 옮겨졌습니다.`;
        report.notes.push(note);
        this.log(note, 'event');
      }
      report.companies.push({
        name: o.c.name, color: o.c.color, own: true,
        members: o.ms.map((m) => ({ id: m.id, name: m.name, look: m.look, cls: m.cls, level: m.level, leader: this.isCaptain(m), unique: this.isCaptain(m) || !!m.hcls, sk: this.battleSkillsOf(m),
          art: m.cap ? `portrait/captain/${m.cap}` : m.hero ? `portrait/hero/${m.hero}` : null,
          capKey: m.cap || null, heroKey: m.hero || null })), // 전투 스프라이트 시트(sheet/captain/<capKey>, sheet/hero/<heroKey>)용
      });
    });
    ext.forEach((e) => {
      const before = e.loyalty;
      // 전투 모드: 잃는 인원은 실제로 쓰러진 단원 (진 전투에서 각자 EXT_KEEP 확률로 돌아오고 최대 EXT_LOST_CAP 명, 이기면 잃지 않는다)
      let lostN;
      if (fought) {
        const downN = this.extDownOf(fought.spec, fought.rec).get(e.id) || 0;
        lostN = 0;
        if (!won) for (let i = 0; i < downN; i++) if (Math.random() >= KB.EXT_KEEP) lostN++;
        lostN = Math.min(KB.EXT_LOST_CAP, lostN);
      }
      const lost = e.betrayed ? 0 : this.extAfterMission(e, outcome, c, lostN);
      if (e.betrayed) { e.missionId = null; this.state.companies = this.state.companies.filter((x) => x.id !== e.id); }
      report.ext.push({ name: e.name, color: e.color, look: e.captain.look, lost, loyalty: e.loyalty - before, betrayed: !!e.betrayed });
      report.companies.push({ name: e.name, color: e.color, own: false, size: e.size + lost, level: e.level, look: e.captain.look, betrayed: !!e.betrayed });
    });

    if (won) s.provClears[c.province] = (s.provClears[c.province] || 0) + 1;
    this.trackMission(mission, won, dead.length);
    const label = { great: '대성공', success: '성공', fail: '실패', disaster: '대실패' }[outcome];
    this.log(`[${c.title}] ${label}! 금화 ${report.gold >= 0 ? '+' : ''}${report.gold}, 명성 ${report.rep >= 0 ? '+' : ''}${report.rep}`, won ? 'good' : 'bad');
    s.pendingReports.push(report);

    if (c.final && !won && s.calamity) s.contracts.unshift({ ...c, id: s.nextId++ });
    if (c.capStory) {
      if (won) this.completeCaptainChapter(c.capStory);
      else s.contracts.unshift({ ...c, id: s.nextId++ });
    }
    if (c.boss) {
      if (won) this.defeatBoss(c.boss);
      else s.contracts.unshift({ ...c, id: s.nextId++ });
    }
    if (c.story) {
      if (won) this.completeStory(c.story);
      else if (!s.heroes[c.story.hero].dead) {
        s.contracts.unshift({ ...c, id: s.nextId++ });
        this.log(`「${c.title}」${josa(c.title, '은', '는')} 다시 도전할 수 있습니다.`);
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

    if (c.final) {
      if (won) this.defeatCalamity();
      return;
    }
    if (c.type === 'battle' && c.campaign) {
      const cp = c.campaign;
      const p = c.province;
      if (won && cp.side === 'attack') {
        if (this.owner(p) === c.target && this.atWar(c.issuer, c.target)) {
          // 패권국의 수도는 장악도를 40 이하로 떨어뜨려 둔 뒤에야 결전으로 함락시킬 수 있다
          if (this.capitalHolds(p, c.issuer)) {
            this.changeControl(p, -CAPITAL_FALL_AT, null, report.control);
            report.notes.push(`${FACTIONS[c.target].name}의 수도는 함락되지 않았지만 크게 흔들렸습니다. (장악도 ${CAPITAL_FALL_AT} 이하에서 결전에 이기면 함락)`);
          } else this.transferProvince(p, c.issuer);
        }
      }
      else if (won && cp.side === 'defend') this.changeControl(p, 40, null, report.control);
      else if (!won && cp.side === 'defend') {
        if (this.owner(p) === c.issuer && this.atWar(c.issuer, c.target)) {
          // 방어전에 져도 같은 보호: 패권국 수도는 장악도 40 초과면 장악도만 -40, 40 이하에서 지면 함락
          if (this.capitalHolds(p, c.target)) {
            this.changeControl(p, -CAPITAL_FALL_AT, null, report.control);
            report.notes.push(`${FACTIONS[c.issuer].name}의 수도는 버텼지만 크게 흔들렸습니다. (장악도 ${CAPITAL_FALL_AT} 이하에서 결전에 지면 함락)`);
          } else this.transferProvince(p, c.target);
        }
      }
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

  // ───────── 최종 결전 ─────────
  // 재앙이 대두하면 수장이 버티는 근거지를 치는 최종 결전이 항상 걸려 있다. 재앙의 세가 클수록 어렵다.
  finalLair() {
    const cal = this.state.calamity;
    if (!cal) return null;
    const lairs = FACTIONS[cal].lairs.filter((p) => this.owner(p) === cal);
    return lairs[0] || this.provincesOf(cal)[0] || null;
  },
  checkFinalBattle() {
    const s = this.state;
    const cal = s.calamity;
    if (!cal) return;
    const lair = this.finalLair();
    const posted = s.contracts.find((c) => c.final);
    if (posted && lair) {
      // 세력이 줄어들면 요구 전투력이 갱신된다
      posted.req = this.finalReq();
      posted.province = lair;
      return;
    }
    if (posted || s.missions.some((mi) => mi.contract.final) || !lair) return;
    const F = FACTIONS[cal];
    const issuer = this.aliveFactions().sort((a, b) => this.strength(b) - this.strength(a))[0] || 'locals';
    const c = this.makeContract({ province: lair, issuer, target: cal, type: 'battle', level: 10, size: FINAL_SIZE, days: 5, enemy: F.leader,
      title: `최종 결전 — ${F.leader}` });
    c.final = true;
    c.campaign = { id: s.nextId++, attacker: issuer, defender: cal, slots: 3, side: 'attack' };
    c.req = this.finalReq();
    c.reward = Math.round(c.reward * 4);
    c.rep = 600;
    c.expires = STORY_EXPIRES;
    s.contracts.unshift(c);
  },
  // 최종 결전의 요구 전투력: 재앙의 국력에 비례 (영토를 빼앗을수록 쉬워진다)
  finalReq() {
    const cal = this.state.calamity;
    return Math.round(this.strength(cal) * 33); // 3개 용병단이 3~4명씩이라 옛(×38)보다 낮춘다
  },

  // ───────── 특별 용병 ─────────
  makeHero(key) {
    const h = HEROES[key];
    // 특별 용병은 이야기와 고유 직업을 가진 용병대장이다
    // 특별 용병은 고유 직업을 가진 대원이다. 이야기가 성장의 열쇠.
    const H = HERO_CLASSES[h.hcls];
    const m = this.baseMerc('unit', H.style, H.base);
    m.hero = key; m.hcls = h.hcls;
    if (!this.state.heroes[key]) this.state.heroes[key] = { appeared: true, hired: false, ch: 0, dead: false };
    for (let i = 1; i < h.level; i++) this.levelUp(m, true);
    m.name = h.name; m.trait = h.trait; m.title = h.title;
    m.look = { cls: H.style, hcls: h.hcls, ...h.look };
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
        this.log(`모집소에 특별한 손님이 찾아왔습니다: 「${h.title}」 ${h.name} (${HERO_CLASSES[h.hcls].name}). 영입하면 그의 이야기가 시작됩니다.`, 'event');
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
      if (!target) issuer = this.isCalamity(owner) || this.isDestroyed(owner) ? 'locals' : owner;
      else if (owner !== target && !FACTIONS[owner].neutral) issuer = owner;
      else if (h.faction && h.faction !== target) issuer = h.faction;
      const level = clamp(Math.max(TIER_LEVELS[PROVINCES[ch.province].tier][0], this.rankIndex() + 2), 1, 10);
      const c = this.makeContract({ province: ch.province, type: ch.type, target, issuer, enemy: ch.enemy, title: ch.title, level, size: 3 });
      c.story = { hero: m.hero, ch: hs.ch };
      c.expires = STORY_EXPIRES;
      c.reward = Math.round(c.reward * 1.5);
      c.rep *= 2;
      s.contracts.unshift(c);
      this.log(`${m.name}의 개인 의뢰 「${ch.title}」${josa(ch.title, '이', '가')} 올라왔습니다!`, 'event');
      s.pendingReports.push({ special: 'dialog', hero: m.hero, title: `개인 의뢰: ${ch.title}`, lines: ch.before, foot: `${m.name}${josa(m.name, '이', '가')} 속한 용병단을 보내야 합니다.` });
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
      const c = this.makeContract({ province: p, type: b.type, enemy: b.enemy, title: b.title, level, size: 4 });
      c.cat = 'monster';
      c.boss = p;
      c.req = Math.round(c.req * 1.3);
      c.reward = Math.round(c.reward * 4);
      c.rep *= 3;
      c.expires = STORY_EXPIRES;
      s.contracts.unshift(c);
      this.log(`재앙 출현! 「${PROVINCES[p].name}」에 「${b.name}」${josa(b.name, '이', '가')} 나타났습니다.`, 'event');
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
