// 용병단: 길드 직속 용병단과 외부 계약 용병단
'use strict';

Object.assign(Game, {
  // ───────── 공통 ─────────
  company(id) { return this.state.companies.find((c) => c.id === id); },
  ownCompanies() { return this.state.companies.filter((c) => c.own); },
  extCompanies() { return this.state.companies.filter((c) => !c.own); },
  members(c) { return this.state.mercs.filter((m) => m.companyId === c.id); },
  reserve() { return this.state.mercs.filter((m) => m.companyId == null); },
  companyBusy(c) { return !!c.missionId; },
  maxCompanies() { return 1 + this.state.facilities.barracks; },
  // 용병단 = 용병대장 1 + 대원 (병영 단계에 따라 4~8명)
  unitSlots() { return 4 + this.state.facilities.barracks; },
  companySize() { return 1 + this.unitSlots(); },
  captainOf(c) { return this.members(c).find((m) => this.isCaptain(m)) || null; },
  unitsOf(c) { return this.members(c).filter((m) => !this.isCaptain(m)); },
  // 이 단원이 이 용병단에 들어갈 자리가 있는가 (없으면 이유)
  slotProblem(m, c) {
    if (this.isCaptain(m)) {
      const cap = this.captainOf(c);
      return cap && cap.id !== m.id ? `이미 용병대장 ${cap.name}이(가) 이끌고 있습니다.` : null;
    }
    return this.unitsOf(c).filter((x) => x.id !== m.id).length >= this.unitSlots() ? `대원 정원이 가득 찼습니다. (최대 ${this.unitSlots()}명)` : null;
  },
  companyCost() { return 80 + this.ownCompanies().length * 120; },

  uniqueCompanyName() {
    const used = new Set([...this.state.companies, ...this.state.market].map((c) => c.name));
    let n = pick(COMPANY_NAME_A), guard = 0;
    while (used.has(`${n} 용병단`) && guard++ < 50) n = pick(COMPANY_NAME_A);
    return `${n} 용병단`;
  },

  // ───────── 직속 용병단 ─────────
  createCompany(free) {
    const s = this.state;
    if (!free) {
      if (this.ownCompanies().length >= this.maxCompanies()) return this.toast('병영을 증축해야 용병단을 더 만들 수 있습니다.');
      const cost = this.companyCost();
      if (s.gold < cost) return this.toast('금화가 부족합니다.');
      s.gold -= cost;
    }
    const used = new Set(s.companies.map((c) => c.color));
    const color = COMPANY_COLORS.find((c) => !used.has(c)) || pick(COMPANY_COLORS);
    const co = { id: s.nextId++, own: true, name: this.uniqueCompanyName(), color, leaderId: null, cohesion: 20, wins: 0, losses: 0, missionId: null };
    s.companies.push(co);
    if (!free) { this.log(`길드 직속 「${co.name}」을(를) 창설했습니다.`, 'good'); this.emit(); }
    return co;
  },

  disbandCompany(id) {
    const s = this.state, c = this.company(id);
    if (!c || !c.own || c.missionId) return;
    this.members(c).forEach((m) => { m.companyId = null; });
    s.companies = s.companies.filter((x) => x.id !== id);
    this.log(`「${c.name}」을(를) 해산했습니다. 단원들은 예비 인원이 됩니다.`);
    this.emit();
  },

  renameCompany(id, name) {
    const c = this.company(id);
    if (c && name) { c.name = name; this.emit(); }
  },

  // 단원을 용병단에 배속 (companyId null 이면 예비 인원으로)
  assign(mercId, companyId) {
    const m = this.state.mercs.find((x) => x.id === mercId);
    if (!m || m.status === 'quest') return;
    if (companyId != null) {
      const c = this.company(companyId);
      if (!c || !c.own || c.missionId) return;
      const why = this.slotProblem(m, c);
      if (why) return this.toast(why);
    }
    this.leaveCompany(m, 8);
    m.companyId = companyId;
    if (companyId != null) {
      const c = this.company(companyId);
      if (c.wins + c.losses > 0) c.cohesion = Math.max(0, c.cohesion - 6); // 손발을 맞춰 온 용병단에 새 얼굴이 들어오면 흔들린다
      if (this.isCaptain(m)) c.leaderId = m.id; // 용병대장이 단장을 맡는다
    }
    this.emit();
  },

  // 용병단에서 빠질 때: 결속도 하락, 단장 교체
  leaveCompany(m, cohesionLoss) {
    const c = m.companyId != null && this.company(m.companyId);
    if (!c) return;
    c.cohesion = Math.max(0, c.cohesion - cohesionLoss);
    m.companyId = null;
    if (c.leaderId === m.id) c.leaderId = null; // 대원은 단장을 대신할 수 없다
  },

  leader(c) { return this.state.mercs.find((m) => m.id === c.leaderId && m.companyId === c.id) || null; },
  cohesionMul(c) { return 0.9 + c.cohesion * 0.002; },
  // 대장의 지휘: 함께 출격한 대장이 없으면 -15%
  leaderMul(c, type, ms) {
    const l = this.leader(c);
    if (!l || (ms && !ms.includes(l))) return 0.85;
    const lead = this.leadOf(l), k = this.leadScale(l);
    return 1 + Math.min(l.level, CAPTAIN_CAP) * 0.004 + ((lead.power || 0) + ((type && lead.types && lead.types[type]) || 0)) * k;
  },
  // 대장의 직업별 지휘 보너스 (해당 기본 직업 대원에게)
  memberLeadMul(c, m, ms) {
    const l = this.leader(c);
    if (!l || l === m || (ms && !ms.includes(l))) return 1;
    const lead = this.leadOf(l);
    return 1 + ((lead.cls && lead.cls[m.cls]) || 0) * this.leadScale(l);
  },

  // 파견 가능한 단원(부상자 제외)
  availableMembers(c) { return this.members(c).filter((m) => m.status === 'idle'); },

  // ───────── 외부 용병단 ─────────
  makeExtCompany() {
    const s = this.state, r = this.rankIndex();
    const late = this.lateGame() ? 4 : 0; // 재앙 이후엔 노련한 용병단도 시장에 나온다
    const level = clamp(rand(Math.max(1, Math.round(r * 1.6)) + late, Math.round(r * 1.6) + 3 + late), 1, 22);
    const size = rand(4, 6);
    const disposition = pick(['gold', 'gold', 'honor', 'faction', 'faction']);
    const sympathy = disposition === 'faction' ? pick(FACTION_KEYS) : null;
    const cap = pick(CAPTAIN_KEYS);
    const cls = CAPTAIN_CLASSES[cap].style;
    const base = (12 + level * 9) * size;
    const share = disposition === 'gold' ? rand(35, 40) : disposition === 'honor' ? rand(22, 28) : rand(20, 30);
    const name = this.uniqueCompanyName();
    return {
      id: s.nextId++, own: false, name, color: pick(COMPANY_COLORS),
      captain: { name: pick(NAMES), cls, cap, look: { cls, cap, skin: pick(SKIN_TONES), hair: pick(HAIR_COLORS), longHair: Math.random() < 0.3 } },
      level, size, maxSize: size, specialty: pick(COMPANY_SPECIALTIES), disposition, sympathy,
      loyalty: rand(50, 65), share, signFee: Math.round(base * 1.4), upkeep: Math.round(base * 0.55),
      contractEnd: 0, wins: 0, losses: 0, missionId: null,
    };
  },

  refreshMarket() {
    const s = this.state;
    const count = 2 + Math.floor(s.facilities.tavern / 2);
    s.market = [];
    for (let i = 0; i < count; i++) s.market.push(this.makeExtCompany());
  },

  extPerMember(c) { return 16 + c.level * 7; },
  extPower(c, type) {
    const spec = c.specialty === type || (c.specialty === 'defense' && type === 'warDefense') ? 1.2 : 1;
    return Math.round(c.size * this.extPerMember(c) * spec * (0.9 + c.loyalty * 0.002));
  },

  // 대상 세력에 동조하는 용병단은 출격을 거부할 수 있다
  extRefusal(c, contract) {
    if (c.disposition === 'faction' && contract.target && c.sympathy === contract.target && c.loyalty < 75) {
      return `「${FACTIONS[c.sympathy].name}」에 동조하는 용병단이라 거부합니다 (충성도 75 필요)`;
    }
    if (c.disposition === 'honor' && (contract.type === 'sabotage') && c.loyalty < 60) {
      return '명예를 중시해 공작 의뢰를 거부합니다 (충성도 60 필요)';
    }
    return null;
  },

  contractCompany(id) {
    const s = this.state;
    const c = s.market.find((x) => x.id === id);
    if (!c) return;
    if (s.gold < c.signFee) return this.toast('금화가 부족합니다.');
    s.gold -= c.signFee;
    s.market = s.market.filter((x) => x.id !== id);
    c.contractEnd = s.day + 28;
    s.companies.push(c);
    this.log(`외부 용병단 「${c.name}」과(와) 4주 계약을 맺었습니다. (계약금 -${c.signFee}, 주간 유지비 ${c.upkeep}, 보상 몫 ${c.share}%)`, 'good');
    this.emit();
  },

  renewCost(c) { return Math.round(c.signFee * (1.3 - c.loyalty / 200)); },
  renewCompany(id) {
    const s = this.state, c = this.company(id);
    if (!c || c.own) return;
    if (c.loyalty < 30) return this.toast('충성도가 낮아 재계약을 거부합니다.');
    const cost = this.renewCost(c);
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    s.gold -= cost;
    c.contractEnd = Math.max(c.contractEnd, s.day) + 28;
    c.loyalty = Math.min(100, c.loyalty + 5);
    this.log(`「${c.name}」과(와) 재계약했습니다. (-${cost} 금화)`);
    this.emit();
  },

  releaseCompany(id, reason = '계약이 끝나 떠났습니다.', kind = '') {
    const s = this.state, c = this.company(id);
    if (!c || c.own || c.missionId) return;
    s.companies = s.companies.filter((x) => x.id !== id);
    this.log(`외부 용병단 「${c.name}」이(가) ${reason}`, kind);
    this.emit();
  },

  weeklyUpkeepTotal() { return this.extCompanies().reduce((sum, c) => sum + c.upkeep, 0); },

  // 주마다: 외부 용병단 충원, 계약 만료
  weeklyCompanies() {
    const s = this.state;
    this.extCompanies().forEach((c) => {
      if (c.size < c.maxSize) c.size++;
      if (s.day >= c.contractEnd && !c.missionId) {
        this.releaseCompany(c.id, c.loyalty >= 30 ? '계약 기간이 끝나 떠났습니다.' : '불만을 품고 계약 종료와 함께 떠났습니다.');
      }
    });
  },

  // 임무 후 외부 용병단 변화
  extAfterMission(c, outcome, contract) {
    const won = outcome === 'great' || outcome === 'success';
    let d = { great: 8, success: 5, fail: -8, disaster: -15 }[outcome];
    if (c.disposition === 'honor' && won && contract.cat === 'conflict' && contract.type !== 'sabotage') d += 3;
    if (c.disposition === 'faction' && c.sympathy === contract.issuer && won) d += 5;
    if (c.disposition === 'faction' && c.sympathy === contract.target) d -= 15;
    c.loyalty = clamp(c.loyalty + d, 0, 100);
    if (won) { c.wins++; if (Math.random() < 0.3) c.level++; } else c.losses++;
    let lost = 0;
    if (outcome === 'fail' && Math.random() < 0.35) lost = 1;
    if (outcome === 'disaster') lost = rand(1, 2);
    c.size = Math.max(0, c.size - lost);
    c.missionId = null;
    if (c.size === 0) {
      this.state.companies = this.state.companies.filter((x) => x.id !== c.id);
      this.log(`외부 용병단 「${c.name}」이(가) 괴멸했습니다.`, 'bad');
    }
    return lost;
  },
});
