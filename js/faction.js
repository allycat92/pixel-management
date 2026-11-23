// 세력, 영토, 전쟁, 세계 진행
'use strict';

const relKey = (a, b) => (a < b ? `${a}|${b}` : `${b}|${a}`);

Object.assign(Game, {
  initWorld() {
    const s = this.state;
    s.factions = {};
    FACTION_KEYS.forEach((f) => { s.factions[f] = { standing: f === 'crown' ? 10 : 0, mod: 0 }; });
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
  standingMul(f) { return f && !FACTIONS[f].neutral ? 1 + this.standing(f) / 250 : 1; },

  // 평판 변경. 반환값: 실제 변화 목록 [{f, d}]
  changeStanding(f, d, out) {
    if (!f || !this.state.factions[f] || !d) return;
    const st = this.state.factions[f];
    const before = st.standing;
    st.standing = clamp(Math.round(st.standing + d), -100, 100);
    if (out) out.push({ f, d: st.standing - before });
    if (before > -60 && st.standing <= -60) this.log(`${FACTIONS[f].name}이(가) 길드를 적으로 간주하기 시작했습니다!`, 'bad');
    if (before < 45 && st.standing >= 45) this.log(`${FACTIONS[f].name}의 신뢰를 얻었습니다! 혜택: ${FACTIONS[f].perk.desc}`, 'good');
  },

  // 대상 세력의 맹방도 불쾌해한다
  changeStandingWithAllies(f, d, out) {
    this.changeStanding(f, d, out);
    if (d >= 0) return;
    FACTION_KEYS.forEach((g) => {
      if (g !== f && this.relation(f, g) >= 50) this.changeStanding(g, Math.round(d / 2), out);
    });
  },

  // ───────── 세력 관계 ─────────
  relation(a, b) {
    if (!a || !b || a === b || FACTIONS[a].neutral || FACTIONS[b].neutral) return 0;
    return this.state.relations[relKey(a, b)] ?? 0;
  },
  changeRelation(a, b, d) {
    if (!a || !b || a === b || FACTIONS[a].neutral || FACTIONS[b].neutral) return;
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
    const desperate = n <= 2 ? 1.5 : 1; // 궁지에 몰린 세력은 결사 항전한다
    return Math.max(5, Math.round((FACTIONS[f].strength * 0.5 + n * 12 + this.state.factions[f].mod) * desperate));
  },
  isCapital(p) { return Object.entries(CAPITALS).some(([f, c]) => c === p && this.owner(p) === f); },
  provinceOpen(p) { return PROVINCES[p].tier <= this.rankIndex(); },
  // a 세력과 b 세력이 맞닿은 지방 (a 소유 지방 중 b와 인접한 곳)
  frontOf(a, b) {
    return this.provincesOf(a).filter((p) => ADJACENCY[p].some((q) => this.owner(q) === b));
  },
  changeControl(p, d, attacker, out) {
    const pr = this.state.provinces[p];
    const before = pr.control;
    pr.control = clamp(Math.round(pr.control + d), 0, 100);
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
    this.state.contracts = this.state.contracts.filter((c) => c.story || c.boss || c.campaign || c.province !== p || c.issuer === to || c.cat === 'conflict');
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
      s.pendingReports.push({ special: 'news', title: '전쟁 발발', factions: [a, b],
        text: `${FACTIONS[a].name}이(가) ${FACTIONS[b].name}에 전쟁을 선포했습니다. 양측 모두 용병을 찾기 시작할 것입니다.` });
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

  // ───────── 매일: 전선 압박, 결전 생성·자동 결판 ─────────
  worldDaily() {
    const s = this.state;
    // 전쟁 중이 아닌 지방은 장악도가 조금씩 회복된다
    PROVINCE_KEYS.forEach((p) => {
      const o = this.owner(p);
      if (!this.warsOf(o).length && s.provinces[p].control < 70) s.provinces[p].control += 1;
    });
    s.wars.forEach((w) => {
      w.weariness += 0.7;
      // 양측이 번갈아 상대 전선을 압박
      const sa = this.strength(w.a), sb = this.strength(w.b);
      const att = Math.random() < sa / (sa + sb) ? w.a : w.b;
      const def = att === w.a ? w.b : w.a;
      const fronts = this.frontOf(def, att);
      if (fronts.length && Math.random() < 0.6) {
        const p = pick(fronts);
        const ratio = this.strength(att) / this.strength(def);
        if (this.isCapital(p)) this.changeControl(p, -rand(0, 2), null); // 수도는 일상 압박으로 함락되지 않음
        else this.changeControl(p, -rand(1, 4) * clamp(ratio, 0.5, 2), att);
        w.score += att === w.a ? 1 : -1;
      }
      // 결전 의뢰 제안
      if (s.day >= w.nextCampaign) {
        w.nextCampaign = s.day + rand(9, 14);
        this.offerCampaign(w);
      }
      if (Math.abs(w.score) >= 100) this.endWar(w.a, w.b);
    });
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
      if (this.owner(p) === def) this.transferProvince(p, att);
      this.log(`「${PROVINCES[p].name}」 결전: ${FACTIONS[att].name}의 승리 (길드는 참전하지 않았습니다)`, 'world');
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
    for (let i = 0; i < FACTION_KEYS.length; i++) {
      for (let j = i + 1; j < FACTION_KEYS.length; j++) {
        const a = FACTION_KEYS[i], b = FACTION_KEYS[j];
        if (!this.provincesOf(a).length || !this.provincesOf(b).length) continue;
        this.changeRelation(a, b, rand(-5, 3) - (this.atWar(a, b) ? 2 : 0));
        const border = this.frontOf(a, b).length > 0;
        if (!this.atWar(a, b) && border && this.relation(a, b) <= -50 && Math.random() < 0.3 && s.wars.length < 3) {
          Math.random() < 0.5 ? this.startWar(a, b) : this.startWar(b, a);
        }
      }
    }
    s.wars.slice().forEach((w) => {
      if (w.weariness >= 50 && Math.random() < 0.3) this.endWar(w.a, w.b);
    });
    // 국경 분쟁: 맞닿은 두 세력 사이에 사건이 터진다
    if (Math.random() < 0.5) {
      const pairs = [];
      FACTION_KEYS.forEach((a) => FACTION_KEYS.forEach((b) => { if (a < b && !this.atWar(a, b) && this.frontOf(a, b).length) pairs.push([a, b]); }));
      if (pairs.length) {
        const [a, b] = pick(pairs);
        this.changeRelation(a, b, -rand(10, 20));
        this.log(`국경 분쟁: ${FACTIONS[a].name}과(와) ${FACTIONS[b].name} 사이에 충돌이 일어났습니다. (관계 악화)`, 'world');
      }
    }
    FACTION_KEYS.forEach((f) => {
      const st = s.factions[f];
      st.mod = Math.round(st.mod * 0.7); // 공작 피해는 서서히 회복
      // 높은 평판은 관리하지 않으면 서서히 식는다
      if (st.standing > 30) st.standing -= 2;
      if (st.standing <= -60 && this.provincesOf(f).length && Math.random() < 0.35) this.retaliate(f);
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
