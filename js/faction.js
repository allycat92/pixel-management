// 세력, 영토, 전쟁, 세계 진행
'use strict';

const relKey = (a, b) => (a < b ? `${a}|${b}` : `${b}|${a}`);

Object.assign(Game, {
  initWorld() {
    const s = this.state;
    s.factions = {};
    FACTION_KEYS.forEach((f) => { s.factions[f] = { standing: f === 'crown' ? 10 : 0, mod: 0 }; });
    CALAMITY_KEYS.forEach((f) => { s.factions[f] = { standing: -100, mod: 0 }; });
    s.calamity = null;
    s.destroyed = [];
    s.relations = {};
    for (let i = 0; i < FACTION_KEYS.length; i++) {
      for (let j = i + 1; j < FACTION_KEYS.length; j++) {
        const a = FACTION_KEYS[i], b = FACTION_KEYS[j];
        s.relations[relKey(a, b)] = INITIAL_RELATIONS[`${a}|${b}`] ?? INITIAL_RELATIONS[`${b}|${a}`] ?? 0;
      }
    }
    s.provinces = {};
    PROVINCE_KEYS.forEach((k) => { s.provinces[k] = { owner: PROVINCES[k].owner, control: 70 }; });
    s.wars = [];
    INITIAL_WARS.forEach(([a, b]) => this.startWar(a, b, true));
  },

  // ───────── 세력 생존 ─────────
  isDestroyed(f) { return (this.state.destroyed || []).includes(f); },
  isCalamity(f) { return !!(f && FACTIONS[f] && FACTIONS[f].calamity); },
  aliveFactions() { return FACTION_KEYS.filter((f) => !this.isDestroyed(f)); },
  // 전쟁·관계 계산에 참여하는 세력 (살아 있는 6세력 + 대두한 재앙)
  activeFactions() { return this.state.calamity ? [...this.aliveFactions(), this.state.calamity] : this.aliveFactions(); },

  // ───────── 평판 ─────────
  standing(f) { return f && this.state.factions[f] ? this.state.factions[f].standing : 0; },
  standingState(v) {
    if (v <= -60) return { label: '적대', cls: 's-hostile' };
    if (v <= -20) return { label: '냉담', cls: 's-cold' };
    if (v < 20) return { label: '중립', cls: 's-neutral' };
    if (v < 45) return { label: '우호', cls: 's-friendly' };
    if (v < 75) return { label: '신뢰', cls: 's-trusted' };
    return { label: '맹우', cls: 's-ally' };
  },
  perk(f) { return this.standing(f) >= 45; },
  standingMul(f) { return f && !FACTIONS[f].neutral && !this.isCalamity(f) ? 1 + this.standing(f) / 250 : 1; },

  // 평판 변경. 반환값: 실제 변화 목록 [{f, d}]
  // 평판 가중치: 깊이 떨어진 평판은 잘 오르지 않고, 높은 평판은 쉽게 깎인다. 길드 명성은 하락을 덜어 준다.
  fameShield() { return 1 - this.rankIndex() * 0.06; },
  standingWeights(f) {
    const v = this.standing(f);
    const gain = v <= -70 ? 0.3 : v <= -40 ? 0.5 : v < 0 ? 0.8 : v > 50 ? Math.round((1 - (v - 50) / 100) * 100) / 100 : 1;
    const loss = (1 + Math.max(0, v) / 100) * this.fameShield();
    return { gain, loss };
  },
  changeStanding(f, d, out, raw) {
    if (!f || !this.state.factions[f] || !d || this.isCalamity(f) || this.isDestroyed(f)) return;
    const st = this.state.factions[f];
    const before = st.standing;
    if (!raw) {
      const w = this.standingWeights(f);
      const sign = Math.sign(d);
      d = d * (d > 0 ? w.gain : w.loss);
      d = sign * Math.max(1, Math.round(Math.abs(d)));
    }
    st.standing = clamp(Math.round(st.standing + d), -100, 100);
    if (out) out.push({ f, d: st.standing - before });
    if (before > -60 && st.standing <= -60) this.log(`${FACTIONS[f].name}이(가) 길드를 적으로 간주하기 시작했습니다!`, 'bad');
    if (before < 45 && st.standing >= 45) this.log(`${FACTIONS[f].name}의 신뢰를 얻었습니다! 혜택: ${FACTIONS[f].perk.desc}`, 'good');
  },

  // 대상 세력의 맹방도 불쾌해한다
  changeStandingWithAllies(f, d, out) {
    this.changeStanding(f, d, out);
    if (d >= 0) return;
    this.aliveFactions().forEach((g) => {
      if (g !== f && this.relation(f, g) >= 50) this.changeStanding(g, Math.round(d / 2), out);
    });
  },

  // ───────── 평판 혜택: 장비 대여 / 정예 용병 ─────────
  loanKey(f, i) { return `${f}:${i}`; },
  findLoan(f, i) {
    const s = this.state, key = this.loanKey(f, i);
    const inInv = s.inventory.find((it) => it.loanKey === key);
    if (inInv) return { item: inInv };
    for (const m of s.mercs) for (const slot of Object.keys(m.equip)) {
      if (m.equip[slot] && m.equip[slot].loanKey === key) return { item: m.equip[slot], merc: m, slot };
    }
    return null;
  },
  checkFactionRewards() {
    const s = this.state;
    s.loans = s.loans || {};
    this.aliveFactions().forEach((f) => {
      const v = this.standing(f);
      FACTION_LOANS[f].forEach((def, i) => {
        const key = this.loanKey(f, i);
        if (!s.loans[key] && v >= def.at) {
          const it = this.makeUniqueItem(def);
          it.tier = i === 0 ? 4 : 5;
          if (i >= 2) it.legendary = true;
          it.loan = f; it.loanKey = key;
          s.inventory.push(it);
          s.loans[key] = true;
          this.log(`${FACTIONS[f].name}이(가) 길드에 「${it.name}」을(를) 대여했습니다. (평판이 ${def.at - LOAN_RECALL_MARGIN} 아래로 떨어지면 회수)`, 'good');
          s.pendingReports.push({ special: 'news', title: '장비 대여', factions: [f],
            text: `${FACTIONS[f].name}의 무기고에서 「${it.name}」(${Object.entries(it.bonus).map(([k, b]) => `${STAT_NAMES[k]}+${b}`).join(' ')})을(를) 보내왔습니다. 평판이 떨어지면 회수됩니다.` });
        } else if (s.loans[key] && v < def.at - LOAN_RECALL_MARGIN) {
          const found = this.findLoan(f, i);
          if (found) {
            if (found.merc) found.merc.equip[found.slot] = null;
            else s.inventory = s.inventory.filter((x) => x !== found.item);
            this.log(`${FACTIONS[f].name}이(가) 대여했던 「${found.item.name}」을(를) 회수해 갔습니다.`, 'bad');
          }
          delete s.loans[key];
        }
      });
    });
  },
  makeElite(f) {
    const sd = FACTIONS[f].soldier;
    const cls = pick(sd.classes);
    const level = clamp(Math.round(this.rankIndex() * 1.6) + rand(3, 5) + (ELITE_LEVEL_BONUS[f] || 0), 3, 26);
    // 세력 정예는 이미 수련을 마친 대원: 레벨에 맞는 상급·최상급 직업을 갖고 온다
    const m = this.makeUnit(cls, Math.min(level, UNIT_TIERS[0].cap));
    if (level > UNIT_TIERS[0].cap) {
      this.applyPromotion(m, pick(PROMOTIONS[cls]).key);
      while (m.level < Math.min(level, UNIT_TIERS[1].cap)) this.levelUp(m, true);
      if (level > UNIT_TIERS[1].cap) { this.applyMaster(m, pick(MASTERS[m.adv]).key); while (m.level < level) this.levelUp(m, true); }
    }
    m.trait = FACTION_TRAITS[f];
    m.elite = f;
    m.title = `${FACTIONS[f].short} 정예`;
    m.look = { ...m.look, cls, skin: pick(sd.skins), hair: pick(sd.hairs), longHair: Math.random() < 0.3, tint: { outfit: FACTIONS[f].color, accent: FACTIONS[f].accent } };
    m.str += 2; m.dex += 2; m.int += 2; m.maxHp += 6;
    return m;
  },
  weeklyElites() {
    const s = this.state;
    s.recruits = s.recruits.filter((r) => !r.elite || (!this.isDestroyed(r.elite) && this.standing(r.elite) >= ELITE_AT));
    this.aliveFactions().forEach((f) => {
      if (this.standing(f) >= ELITE_AT && !s.recruits.some((r) => r.elite === f)) {
        s.recruits.unshift(this.makeElite(f));
        this.log(`${FACTIONS[f].name}이(가) 정예 용병을 모집소로 보냈습니다.`, 'good');
      }
    });
    // 관계가 틀어지면 정예 용병은 본국으로 소환된다
    s.mercs.filter((m) => m.elite && m.status !== 'quest' && this.standing(m.elite) < 0).forEach((m) => {
      this.removeMerc(m, `${FACTIONS[m.elite].name}의 소환 명령을 받고 길드를 떠났습니다.`, 'bad');
    });
  },

  // ───────── 세력 관계 ─────────
  relation(a, b) {
    if (!a || !b || a === b || FACTIONS[a].neutral || FACTIONS[b].neutral) return 0;
    if (this.isCalamity(a) || this.isCalamity(b)) return -100;
    return this.state.relations[relKey(a, b)] ?? 0;
  },
  changeRelation(a, b, d) {
    if (!a || !b || a === b || FACTIONS[a].neutral || FACTIONS[b].neutral || this.isCalamity(a) || this.isCalamity(b)) return;
    const k = relKey(a, b);
    this.state.relations[k] = clamp((this.state.relations[k] ?? 0) + d, -100, 100);
  },
  relationState(a, b) {
    if (this.atWar(a, b)) return { label: '전쟁', cls: 'r-war' };
    const v = this.relation(a, b);
    if (v <= -40) return { label: '적대', cls: 'r-hostile' };
    if (v < 0) return { label: '긴장', cls: 'r-tense' };
    if (v < 50) return { label: '평화', cls: 'r-peace' };
    return { label: '동맹', cls: 'r-ally' };
  },

  // ───────── 영토 ─────────
  owner(p) { return this.state.provinces[p].owner; },
  provincesOf(f) { return PROVINCE_KEYS.filter((k) => this.owner(k) === f); },
  strength(f) {
    if (!f || FACTIONS[f].neutral) return 0;
    const n = this.provincesOf(f).length;
    const desperate = n <= 2 && !this.isCalamity(f) ? 1.2 : 1; // 궁지에 몰린 세력은 결사 항전한다
    return Math.max(5, Math.round((FACTIONS[f].strength * 0.5 + n * 12 + this.state.factions[f].mod) * desperate));
  },
  isCapital(p) { return Object.entries(CAPITALS).some(([f, c]) => c === p && this.owner(p) === f); },
  // 패권국의 수도는 길드가 개입하거나 재앙이 쳐들어오지 않는 한 함락되지 않는다
  isGuardedCapital(p, attacker) { return this.isCapital(p) && FACTIONS[this.owner(p)].hegemon && !this.isCalamity(attacker); },
  provinceOpen(p) { return PROVINCES[p].tier <= this.rankIndex(); },
  // a 세력과 b 세력이 맞닿은 지방 (a 소유 지방 중 b와 인접한 곳)
  frontOf(a, b) {
    return this.provincesOf(a).filter((p) => ADJACENCY[p].some((q) => this.owner(q) === b));
  },
  doctrine(f) { return DOCTRINES[f] || DOCTRINES.cities; },
  // att 세력이 칠 수 있는 def 세력의 지방 (원정 거리 안)
  reachable(att, def) {
    const reach = this.doctrine(att).reach;
    const mine = this.provincesOf(att);
    return this.provincesOf(def).filter((p) => mine.some((q) => PROV_DIST[q][p] <= reach));
  },
  // 공세 쪽 고르기: 국력 × 호전성
  pickAttacker(a, b) {
    const wa = this.strength(a) * this.doctrine(a).aggression, wb = this.strength(b) * this.doctrine(b).aggression;
    return Math.random() < wa / (wa + wb) ? a : b;
  },

  changeControl(p, d, attacker, out) {
    const pr = this.state.provinces[p];
    const before = pr.control;
    if (d < 0 && attacker) d *= this.doctrine(pr.owner).defense; // 숲의 엘프, 북부 귀족은 끈질기게 버틴다
    pr.control = clamp(Math.round(pr.control + d), 0, 100);
    if (pr.control <= 0 && this.isGuardedCapital(p, attacker)) pr.control = 1; // 패권국의 수도는 결전 없이는 무너지지 않는다
    if (out) out.push({ p, d: pr.control - before });
    if (pr.control <= 0 && attacker && attacker !== pr.owner && this.atWar(attacker, pr.owner)) {
      this.transferProvince(p, attacker);
    } else if (pr.control <= 0) {
      pr.control = 5; // 전쟁 중이 아니면 지방이 넘어가지는 않는다
    }
  },
  transferProvince(p, to) {
    const pr = this.state.provinces[p];
    const from = pr.owner;
    pr.owner = to;
    pr.control = 35;
    const war = this.war(from, to);
    if (war) { war.score += war.a === to ? 15 : -15; war.weariness += 6; }
    this.log(`⚔ ${FACTIONS[to].name}이(가) ${FACTIONS[from].name}로부터 「${PROVINCES[p].name}」을(를) 빼앗았습니다!`, 'world');
    // 그 지방의 기존 의뢰 중 의뢰주가 바뀐 것은 무효
    this.state.contracts = this.state.contracts.filter((c) => c.story || c.boss || c.campaign || c.final || c.province !== p || c.issuer === to || c.cat === 'conflict');
    if (FACTION_KEYS.includes(from) && !this.provincesOf(from).length) this.destroyFaction(from, to);
  },

  // ───────── 전쟁 ─────────
  war(a, b) { return this.state.wars.find((w) => (w.a === a && w.b === b) || (w.a === b && w.b === a)); },
  atWar(a, b) { return !!this.war(a, b); },
  warsOf(f) { return this.state.wars.filter((w) => w.a === f || w.b === f).map((w) => (w.a === f ? w.b : w.a)); },
  startWar(a, b, silent) {
    if (this.atWar(a, b)) return;
    const s = this.state;
    s.wars.push({ a, b, score: 0, weariness: 0, start: s.day, nextCampaign: s.day + rand(6, 10) });
    this.state.relations[relKey(a, b)] = Math.min(this.relation(a, b), -60);
    if (!silent) {
      this.log(`⚔ ${FACTIONS[a].name}이(가) ${FACTIONS[b].name}에 전쟁을 선포했습니다!`, 'world');
      const da = this.doctrine(a);
      s.pendingReports.push({ special: 'news', title: '전쟁 발발', factions: [a, b],
        text: `「${da.motto}」 — ${FACTIONS[a].name}이(가) ${da.name}의 기치 아래 ${FACTIONS[b].name}에 전쟁을 선포했습니다. 양측 모두 용병을 찾기 시작할 것입니다.` });
    }
  },
  endWar(a, b, reason) {
    const s = this.state;
    const w = this.war(a, b);
    if (!w) return;
    s.wars = s.wars.filter((x) => x !== w);
    s.relations[relKey(a, b)] = Math.max(this.relation(a, b), -30);
    // 진행 중인 결전 의뢰 취소
    s.contracts = s.contracts.filter((c) => !(c.campaign && ((c.issuer === a && c.target === b) || (c.issuer === b && c.target === a))));
    const winner = w.score >= 60 ? w.a : w.score <= -60 ? w.b : null;
    const text = winner
      ? `${FACTIONS[winner].name}의 우세 속에 ${FACTIONS[a].name}과(와) ${FACTIONS[b].name}이(가) 강화 조약을 맺었습니다.`
      : `${FACTIONS[a].name}과(와) ${FACTIONS[b].name}이(가) ${reason || '전쟁에 지쳐'} 휴전했습니다.`;
    this.log(`🕊 ${text}`, 'world');
    s.pendingReports.push({ special: 'news', title: '강화 조약', factions: [a, b], text });
  },

  // ───────── 멸망과 재앙 ─────────
  destroyFaction(f, by) {
    const s = this.state;
    if (this.isDestroyed(f)) return;
    s.destroyed.push(f);
    s.wars.filter((w) => w.a === f || w.b === f).forEach((w) => { s.wars = s.wars.filter((x) => x !== w); });
    s.contracts = s.contracts.filter((c) => c.issuer !== f && c.target !== f);
    // 대여 장비 회수, 정예 용병은 고국을 잃고 떠난다
    (FACTION_LOANS[f] || []).forEach((def, i) => {
      const found = this.findLoan(f, i);
      if (found) { if (found.merc) found.merc.equip[found.slot] = null; else s.inventory = s.inventory.filter((x) => x !== found.item); }
      if (s.loans) delete s.loans[this.loanKey(f, i)];
    });
    s.recruits = s.recruits.filter((r) => r.elite !== f);
    s.mercs.filter((m) => m.elite === f && m.status !== 'quest').forEach((m) => this.removeMerc(m, '고국이 멸망하자 길을 떠났습니다.', 'bad'));
    const text = `${FACTIONS[f].name}이(가) ${by ? `${FACTIONS[by].name}에 의해 ` : ''}멸망했습니다. 「${DOCTRINES[f].motto}」 — 그 외침은 이제 역사 속으로 사라집니다.`;
    this.log(`☠ ${text}`, 'world');
    s.pendingReports.push({ special: 'news', title: `${FACTIONS[f].name} 멸망`, factions: [f], text });
    this.checkCalamity();
  },

  // 재앙 대두 판정: 패권국이 무너지면 그 봉인에 묶여 있던 재앙이, 세력이 셋 이상 멸망하면 약해진 패권국 쪽의 재앙이 깨어난다
  checkCalamity() {
    const s = this.state;
    if (s.calamity || s.calamityDefeated) return;
    const n = s.destroyed.length;
    let key = null;
    if (this.isDestroyed('crown')) key = 'beasts';
    else if (this.isDestroyed('church')) key = 'demons';
    else if (n >= CALAMITY_TRIGGER) key = this.weakerSeal();
    if (key) { this.riseCalamity(key); return; }
    if (n === CALAMITY_TRIGGER - 1 && !s.omen) {
      s.omen = this.weakerSeal();
      this.log(`불길한 징조: ${FACTIONS[s.omen].omen}`, 'world');
      s.pendingReports.push({ special: 'notice', enemy: FACTIONS[s.omen].leader, title: '불길한 징조', lines: [[null, FACTIONS[s.omen].omen]],
        foot: `세력이 하나만 더 멸망하면 재앙이 깨어납니다. (멸망 ${n}/${CALAMITY_TRIGGER})` });
    }
  },

  // 약해진 패권국 쪽 봉인이 깨질 가능성이 크다 (국력 비율에 따른 확률)
  weakerSeal() {
    if (this.state.omen) return this.state.omen;
    const a = this.strength('crown'), b = this.strength('church');
    return Math.random() < b / (a + b) ? 'beasts' : 'demons';
  },

  riseCalamity(key) {
    const s = this.state;
    const F = FACTIONS[key];
    s.calamity = key;
    s.calamityDay = s.day;
    s.factions[key].mod = 0;
    s.calamityOrigin = {};
    // 근거지와 그 주변을 장악하며 출현
    const spawn = [...F.lairs];
    F.lairs.forEach((p) => ADJACENCY[p].forEach((q) => { if (spawn.length < F.lairs.length + 1 && !this.isCapital(q) && !spawn.includes(q)) spawn.push(q); }));
    spawn.forEach((p) => {
      const from = this.owner(p);
      s.calamityOrigin[p] = from;
      s.provinces[p].owner = key;
      s.provinces[p].control = 80;
      if (FACTION_KEYS.includes(from) && !this.provincesOf(from).length) this.destroyFaction(from, key);
    });
    // 대동맹: 세력들 사이의 전쟁이 멈추고, 모두가 재앙과 싸운다
    s.wars = [];
    const alive = this.aliveFactions();
    alive.forEach((a) => alive.forEach((b) => { if (a < b) this.changeRelation(a, b, 30); }));
    alive.forEach((f) => s.wars.push({ a: key, b: f, score: 0, weariness: 0, start: s.day, nextCampaign: s.day + rand(4, 8), calamity: true }));
    s.contracts = s.contracts.filter((c) => !c.campaign);
    this.log(`☠ ${F.name} 대두! ${F.leaderTitle} ${F.leader}이(가) 대륙 전체에 전쟁을 선포했습니다. 모든 세력이 칼을 거두고 대동맹을 맺습니다.`, 'world');
    s.pendingReports.push({ special: 'notice', enemy: F.leader, title: `${F.name} 대두`, lines: [[null, F.rise], [null, F.desc]],
      foot: `모든 세력이 ${F.name}과(와) 전쟁에 들어갑니다. ${F.name}이(가) 지방 ${CALAMITY_DARKNESS}곳을 차지하면 대륙은 암흑시대에 빠집니다. 최종 결전으로 ${F.leader}을(를) 쓰러뜨리세요.` });
  },

  defeatCalamity() {
    const s = this.state;
    const key = s.calamity;
    if (!key) return;
    const F = FACTIONS[key];
    // 재앙이 차지했던 지방은 원래 주인(살아 있다면)이나 이웃 세력, 주민에게 돌아간다
    this.provincesOf(key).forEach((p) => {
      const orig = (s.calamityOrigin || {})[p];
      let to = orig && !this.isDestroyed(orig) && !this.isCalamity(orig) ? orig : null;
      if (!to) {
        const near = ADJACENCY[p].map((q) => this.owner(q)).filter((o) => FACTION_KEYS.includes(o) && !this.isDestroyed(o));
        to = near.length ? near.sort((a, b) => this.strength(b) - this.strength(a))[0] : 'locals';
      }
      s.provinces[p].owner = to;
      s.provinces[p].control = 50;
    });
    s.wars = s.wars.filter((w) => !w.calamity);
    s.calamity = null;
    s.calamityDefeated = key;
    this.log(`☀ ${F.leader} 토벌! ${F.name}이(가) 무너지고 대륙에 다시 아침이 찾아옵니다.`, 'world');
    s.pendingReports.push({ special: 'savior', calamity: key });
  },

  // ───────── 매일: 전선 압박, 결전 생성·자동 결판 ─────────
  worldDaily() {
    const s = this.state;
    // 전쟁 중이 아닌 지방은 장악도가 조금씩 회복된다
    PROVINCE_KEYS.forEach((p) => {
      const o = this.owner(p);
      if (!this.warsOf(o).length && s.provinces[p].control < 70) s.provinces[p].control += 1;
    });
    const press = (att, def, w) => {
      const fronts = this.reachable(att, def);
      if (!fronts.length) return;
      const p = pick(fronts);
      const ratio = this.strength(att) / this.strength(def);
      const hit = -rand(1, 3) * clamp(ratio, 0.5, 2);
      if (this.isGuardedCapital(p, att)) this.changeControl(p, -rand(0, 2), null); // 패권국 수도는 일상 압박으로 함락되지 않음
      else if (this.isCapital(p)) this.changeControl(p, hit * 0.6, att);       // 약소국의 수도는 끈질기게 버티지만 결국 무너진다
      else this.changeControl(p, hit, att);
      if (w) w.score += att === w.a ? 1 : -1;
    };
    s.wars.forEach((w) => {
      w.weariness += 0.7;
      if (w.calamity) {
        // 동맹 세력의 반격 (재앙의 공세는 아래에서 하루 한 번)
        const ally = w.b;
        if (Math.random() < 0.3) press(ally, w.a, w);
      } else if (Math.random() < 0.6) {
        // 양측이 번갈아 상대 전선을 압박
        const att = this.pickAttacker(w.a, w.b);
        press(att, att === w.a ? w.b : w.a, w);
      }
      // 결전 의뢰 제안
      if (s.day >= w.nextCampaign) {
        w.nextCampaign = s.day + rand(9, 14);
        this.offerCampaign(w);
      }
      if (Math.abs(w.score) >= 100 && !w.calamity) this.endWar(w.a, w.b);
    });
    // 재앙은 날마다 세를 불리고, 하루에 한 곳을 덮친다
    if (s.calamity) {
      s.factions[s.calamity].mod += 0.3;
      const victims = this.warsOf(s.calamity).filter((f) => this.reachable(s.calamity, f).length);
      if (victims.length && Math.random() < 0.85) press(s.calamity, pick(victims), this.war(s.calamity, pick(victims)));
      if (this.provincesOf(s.calamity).length >= CALAMITY_DARKNESS && !s.over) {
        s.over = 'darkness';
        s.pendingReports.push({ special: 'darkness' });
      }
    }
    // 아무도 맡지 않은 결전은 국력대로 결판
    const seen = new Set();
    s.contracts.filter((c) => c.campaign && c.expires < s.day).forEach((c) => {
      if (seen.has(c.campaign.id)) return;
      seen.add(c.campaign.id);
      this.autoResolveCampaign(c.campaign, c.province);
    });
    s.contracts = s.contracts.filter((c) => !(c.campaign && c.expires < s.day));
  },

  autoResolveCampaign(cp, p) {
    const att = cp.attacker, def = cp.defender;
    if (!this.atWar(att, def)) return;
    const sa = this.strength(att), sb = this.strength(def);
    if (Math.random() < sa / (sa + sb)) {
      // 수도는 길드가 개입하지 않은 결전으로는 함락되지 않는다 (포위만 된다)
      if (this.owner(p) === def && this.isGuardedCapital(p, att)) { this.changeControl(p, -30); this.log(`「${PROVINCES[p].name}」 결전: ${FACTIONS[att].name}이(가) 수도를 포위했지만 함락시키지 못했습니다.`, 'world'); return; }
      // 길드가 빠진 결전은 결정타가 되지 못한다: 장악도를 크게 깎을 뿐
      this.log(`「${PROVINCES[p].name}」 결전: ${FACTIONS[att].name}의 승리 (길드는 참전하지 않았습니다)`, 'world');
      if (this.owner(p) === def) this.changeControl(p, this.isCapital(p) ? -20 : -35, att);
    } else {
      this.changeControl(p, 20);
      const w = this.war(att, def);
      if (w) w.score += w.a === def ? 10 : -10;
      this.log(`「${PROVINCES[p].name}」 결전: ${FACTIONS[def].name}이(가) 방어에 성공 (길드는 참전하지 않았습니다)`, 'world');
    }
  },

  // ───────── 매주: 관계 변화, 선전포고와 강화, 적대 세력의 보복 ─────────
  worldWeekly() {
    const s = this.state;
    const alive = this.aliveFactions();
    for (let i = 0; i < alive.length; i++) {
      for (let j = i + 1; j < alive.length; j++) {
        const a = alive[i], b = alive[j];
        if (!this.provincesOf(a).length || !this.provincesOf(b).length) continue;
        const da = this.doctrine(a), db = this.doctrine(b);
        this.changeRelation(a, b, rand(-4, 3) + (da.drift[b] || 0) + (db.drift[a] || 0) - (this.atWar(a, b) ? 2 : 0));
        // 서로를 주적으로 두지 않은 세력끼리는 시간이 지나면 앙금이 누그러진다
        if (!da.targets[b] && !db.targets[a] && !this.atWar(a, b) && this.relation(a, b) < -20) this.changeRelation(a, b, 3);
      }
    }
    // 강령에 따른 선전포고: 호전적인 세력이 주적을 먼저 친다
    const decl = [];
    // 재앙이 대두하면 세력들은 서로 칼을 겨누지 않는다
    if (!s.calamity) alive.forEach((a) => alive.forEach((b) => { if (a !== b) decl.push([a, b]); }));
    decl.sort(() => Math.random() - 0.5).forEach(([a, b]) => {
      if (s.wars.length >= 3 || this.atWar(a, b) || !this.provincesOf(a).length || !this.provincesOf(b).length) return;
      if (this.warsOf(a).length >= 2) return;
      const d = this.doctrine(a);
      const t = d.targets[b] || 1;
      const threshold = d.warAt + (d.targets[b] ? 10 : -15); // 주적이 아니면 웬만해선 먼저 치지 않는다
      if (this.relation(a, b) > threshold || !this.reachable(a, b).length) return;
      if (Math.random() < clamp(0.08 * d.aggression * t, 0, 0.6)) this.startWar(a, b);
    });
    // 강화: 두 세력의 강화 성향 평균. 공세 측이 크게 이기고 있으면 버틴다
    s.wars.slice().forEach((w) => {
      if (w.calamity) return;
      const need = (this.doctrine(w.a).peaceAt + this.doctrine(w.b).peaceAt) / 2;
      const aggressorWinning = w.score > 40 && this.doctrine(w.a).aggression >= 1.2;
      if (w.weariness >= need && !aggressorWinning && Math.random() < 0.3) this.endWar(w.a, w.b);
    });
    // 국경 분쟁: 맞닿은 두 세력 사이에 사건이 터진다
    if (Math.random() < 0.5) {
      const pairs = [];
      if (!s.calamity) alive.forEach((a) => alive.forEach((b) => { if (a < b && !this.atWar(a, b) && this.frontOf(a, b).length) pairs.push([a, b]); }));
      if (pairs.length) {
        const [a, b] = pick(pairs);
        this.changeRelation(a, b, -rand(10, 20));
        this.log(`국경 분쟁: ${FACTIONS[a].name}과(와) ${FACTIONS[b].name} 사이에 충돌이 일어났습니다. (관계 악화)`, 'world');
      }
    }
    alive.forEach((f) => {
      const st = s.factions[f];
      st.mod = Math.round(st.mod * 0.7); // 공작 피해는 서서히 회복
      // 높은 평판은 관리하지 않으면 서서히 식는다
      if (st.standing >= 75) st.standing -= 4;
      else if (st.standing >= 50) st.standing -= 2;
      else if (st.standing >= 30) st.standing -= 1;
      if (st.standing <= -60 && this.provincesOf(f).length && Math.random() < 0.35 * (1 - this.rankIndex() * 0.08)) this.retaliate(f);
    });
  },

  // 적대 세력의 보복
  retaliate(f) {
    const s = this.state;
    if (Math.random() < 0.5 && s.gold > 0) {
      const v = Math.min(s.gold, 40 + this.rankIndex() * 30);
      s.gold -= v;
      this.log(`${FACTIONS[f].name}의 첩자들이 길드 금고를 털어 갔습니다! (금화 -${v})`, 'bad');
    } else {
      const idle = s.mercs.filter((m) => m.status === 'idle');
      if (!idle.length) return;
      const m = pick(idle);
      m.status = 'injured'; m.injury = rand(2, 4);
      this.log(`${FACTIONS[f].name}의 자객이 ${m.name}을(를) 습격했습니다! (부상 ${m.injury}일)`, 'bad');
    }
  },

  // ───────── 길드 지부 ─────────
  branchCost(p) { return 180 + PROVINCES[p].tier * 140; },
  canBranch(p) {
    const o = this.owner(p);
    return this.provinceOpen(p) && !PROVINCES[p].home && !this.state.branches[p] && (FACTIONS[o].neutral || this.standing(o) >= 0);
  },
  buildBranch(p) {
    const s = this.state;
    if (!this.canBranch(p)) return this.toast('이 지방에는 지부를 세울 수 없습니다. (소유 세력 평판 0 이상 필요)');
    const cost = this.branchCost(p);
    if (s.gold < cost) return this.toast('금화가 부족합니다.');
    s.gold -= cost;
    s.branches[p] = true;
    this.log(`「${PROVINCES[p].name}」에 길드 지부를 열었습니다! 이 지방 의뢰가 늘고 이동이 빨라집니다. (-${cost} 금화)`, 'good');
    this.emit();
  },
});
