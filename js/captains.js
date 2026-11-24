// 용병대장 영입: 창설 시 선택, 대장별 영입 과제, 영입 의뢰(서사)
'use strict';

const STAT_NAMES_CAP = {
  streak: '연속 성공', hardStreak: '성공률 80% 미만 의뢰 연속 성공', gambles: '성공률 40% 미만 의뢰 성공', bigGambles: '성공률 25% 미만 의뢰 성공',
  monster: '괴물·치안 의뢰 성공', magic: '마법 조사 성공', raid: '습격 성공', siege: '거점 공략 성공',
  counterspy: '방첩 성공', campaign: '대규모 결전 승리', calamity: '재앙 세력 상대 의뢰 성공',
};

Object.assign(Game, {
  // s.captains[key] = { status: 'candidate' | 'locked' | 'challenge' | 'pursuing' | 'joined' | 'lost', ch, phase, why }
  initCaptains() {
    const s = this.state;
    s.captains = {};
    STARTER_CAPTAINS.forEach((k) => { s.captains[k] = { status: 'candidate', ch: 0, phase: 'start' }; });
    CAPTAIN_PHASES.forEach((ph) => ph.list.forEach((k) => { s.captains[k] = { status: 'locked', ch: 0, phase: ph.key }; }));
    s.phases = {};
    CAPTAIN_PHASES.forEach((ph) => { s.phases[ph.key] = 'locked'; });
    s.track = { streak: 0, hardStreak: 0, gambles: 0, bigGambles: 0, monster: 0, magic: 0, raid: 0, siege: 0, counterspy: 0, campaign: 0, calamity: 0, lastDeath: 0 };
    s.pendingReports.unshift({ special: 'starter' });
  },

  captainState(key) { return this.state.captains[key]; },
  captainPhase(key) { return CAPTAIN_PHASES.find((ph) => ph.list.includes(key)); },
  needsStarter() { return STARTER_CAPTAINS.some((k) => this.state.captains[k].status === 'candidate'); },

  // 의뢰 결과를 과제용 기록에 남긴다 (resolveMission에서 호출)
  trackMission(mission, won, deaths) {
    const t = this.state.track;
    if (!t) return;
    const c = mission.contract;
    if (deaths) t.lastDeath = this.state.day;
    if (!won) { t.streak = 0; t.hardStreak = 0; return; }
    t.streak++;
    if (mission.chance < 0.8) t.hardStreak = (t.hardStreak || 0) + 1;
    if (mission.chance < 0.4) t.gambles++;
    if (mission.chance < 0.25) t.bigGambles++;
    if (c.cat === 'monster') t.monster++;
    if (c.type === 'magic') t.magic++;
    if (c.type === 'raid') t.raid++;
    if (c.type === 'siege') t.siege++;
    if (c.type === 'counterspy') t.counterspy++;
    if (c.campaign) t.campaign++;
    if (this.isCalamity(c.target) || c.final) t.calamity++;
  },

  // 과제 조건 하나 평가: { ok, text, dead(더는 이룰 수 없음) }
  evalCond(cd) {
    const s = this.state, t = s.track || {};
    const own = (v, min) => `${v}/${min}`;
    switch (cd.t) {
      case 'rank': return { ok: this.rankIndex() >= cd.min, text: `길드 등급 ${RANKS[cd.min].name} 이상 (현재 ${this.rank().name})` };
      case 'rep': return { ok: s.rep >= cd.min, text: `명성 ${cd.min} 이상 (${own(s.rep, cd.min)})` };
      case 'gold': return { ok: s.gold >= cd.min, text: `금화 ${cd.min} 보유 (현재 ${s.gold})` };
      case 'standing': {
        const v = this.standing(cd.f), F = FACTIONS[cd.f].short;
        const ok = cd.min != null ? v >= cd.min : v <= cd.max;
        return { ok, dead: this.isDestroyed(cd.f), text: `${F} 평판 ${cd.min != null ? `${cd.min} 이상` : `${cd.max} 이하`} (현재 ${v})` };
      }
      case 'alive': return { ok: !this.isDestroyed(cd.f), dead: this.isDestroyed(cd.f), text: `${FACTIONS[cd.f].name} 존속` };
      case 'dayMax': return { ok: s.day <= cd.v, dead: s.day > cd.v, text: `${cd.v}일차 안에 (현재 ${s.day}일차)` };
      case 'mercsMax': return { ok: s.mercs.length <= cd.v, text: `길드 인원 ${cd.v}명 이하 (현재 ${s.mercs.length}명)` };
      case 'companies': return { ok: this.ownCompanies().length >= cd.min, text: `직속 용병단 ${cd.min}개 이상 (현재 ${this.ownCompanies().length})` };
      case 'stat': { const v = t[cd.k] || 0; return { ok: v >= cd.min, text: `${STAT_NAMES_CAP[cd.k]} ${cd.k.endsWith('treak') ? '' : '누적 '}${own(v, cd.min)}` }; }
      case 'noDeath': { const v = s.day - (t.lastDeath || 0); return { ok: v >= cd.days, text: `최근 ${cd.days}일간 전사자 없음 (${Math.min(v, cd.days)}/${cd.days}일)` }; }
      case 'adv': { const v = s.mercs.filter((m) => m.adv).length; return { ok: v >= cd.min, text: `상급 이상 대원 ${own(v, cd.min)}` }; }
      case 'masters': { const v = s.mercs.filter((m) => m.master).length; return { ok: v >= cd.min, text: `최상급 대원 ${own(v, cd.min)}` }; }
      case 'bosses': { const v = Object.keys(s.bossDefeated).length; return { ok: v >= cd.min, text: `재앙급 괴물 토벌 ${own(v, cd.min)}` }; }
      case 'calamity': return { ok: !!(s.calamity || s.calamityDefeated), text: '재앙 세력이 대두함' };
      default: return { ok: false, text: '?' };
    }
  },
  challengeOf(key) {
    const ch = CAPTAIN_CHALLENGES[key];
    if (!ch) return null;
    const conds = ch.conds.map((cd) => this.evalCond(cd));
    return { name: ch.name, conds, ok: conds.every((c) => c.ok), dead: conds.some((c) => c.dead) };
  },

  // 실제 용병대장 단원 만들기 (이름·외형·성격이 정해져 있다)
  makeNamedCaptain(key, level) {
    const C = CAPTAINS[key];
    const m = this.makeCaptain(key, level);
    m.name = C.name; m.title = C.title; m.trait = C.trait || m.trait;
    m.look = { cls: m.cls, cap: key, ...C.look };
    return m;
  },

  // 창설 후보 중 하나를 고른다. 나머지는 영영 떠난다.
  chooseStarter(key) {
    const s = this.state;
    if (!STARTER_CAPTAINS.includes(key) || s.captains[key].status !== 'candidate') return;
    STARTER_CAPTAINS.forEach((k) => { s.captains[k].status = k === key ? 'joined' : 'lost'; });
    const m = this.makeNamedCaptain(key, 2);
    s.mercs.push(m);
    const co = this.ownCompanies()[0];
    if (co) { m.companyId = co.id; co.leaderId = m.id; }
    this.log(`${CAPTAINS[key].title} ${m.name}이(가) 첫 용병대장이 되었습니다. 다른 후보 ${STARTER_CAPTAINS.length - 1}명은 각자의 길을 찾아 떠났습니다.`, 'good');
    this.emit();
  },

  checkCaptains() {
    const s = this.state, r = this.rankIndex();
    if (!s.captains) return;
    if (!s.track) s.track = { streak: 0, hardStreak: 0, gambles: 0, bigGambles: 0, monster: 0, magic: 0, raid: 0, siege: 0, counterspy: 0, campaign: 0, calamity: 0, lastDeath: 0 };
    // 등급이 오르면 그 시기 대장들의 영입 과제가 공개된다
    CAPTAIN_PHASES.forEach((ph) => {
      if (s.phases[ph.key] !== 'locked' || r < ph.rank) return;
      s.phases[ph.key] = 'open';
      ph.list.forEach((k) => { if (s.captains[k].status === 'locked') s.captains[k].status = 'challenge'; });
      this.log(`새 영입 과제(${ph.name}): 용병대장 ${ph.list.length}명의 소문이 들려옵니다. 과제를 달성하면 그들이 길드를 찾아옵니다. (모집소)`, 'event');
      s.pendingReports.push({ special: 'dialog', captain: ph.list[0], title: `영입 과제 — ${ph.name}`,
        lines: [[null, `길드의 명성이 퍼지자 이름난 용병대장들의 소문이 들려옵니다: ${ph.list.map((k) => `${CAPTAINS[k].title} ${CAPTAINS[k].name}`).join(', ')}.`],
          [null, '그들은 아무 길드에나 몸을 맡기지 않습니다. 저마다 길드가 증명해야 할 것이 있습니다.']],
        foot: '모집소에서 대장별 영입 과제를 확인하세요. 조건을 한순간에 모두 만족하면 그 대장이 찾아옵니다. 기한을 넘기거나 불가능해지면 떠납니다.' });
    });
    // 과제 판정: 달성 → 대장이 찾아오고 영입 의뢰 시작 / 불가능 → 떠남
    Object.entries(s.captains).forEach(([key, cs]) => {
      if (cs.status !== 'challenge') return;
      const ch = this.challengeOf(key);
      if (ch.ok) {
        cs.status = 'pursuing';
        this.log(`영입 과제 「${ch.name}」 달성! ${CAPTAINS[key].title} ${CAPTAINS[key].name}이(가) 길드를 찾아왔습니다. 영입 의뢰를 완수하면 합류합니다.`, 'good');
        s.pendingReports.push({ special: 'dialog', captain: key, title: `${CAPTAINS[key].title} ${CAPTAINS[key].name}`, lines: CAPTAINS[key].intro,
          foot: `영입 과제 「${ch.name}」 달성 — 영입 의뢰가 의뢰 목록에 올라옵니다.` });
      } else if (ch.dead) {
        cs.status = 'lost';
        cs.why = ch.conds.find((c) => c.dead).text;
        this.log(`${CAPTAINS[key].title} ${CAPTAINS[key].name}의 영입 과제를 이룰 수 없게 되었습니다. (${cs.why})`, 'bad');
      }
    });
    // 택한 대장의 영입 의뢰를 올린다
    Object.entries(s.captains).forEach(([key, cs]) => {
      if (cs.status !== 'pursuing') return;
      const C = CAPTAINS[key];
      const ch = C.chapters[cs.ch];
      if (!ch || !this.provinceOpen(ch.province)) return;
      const posted = s.contracts.some((c) => c.capStory && c.capStory.key === key)
        || s.missions.some((mi) => mi.contract.capStory && mi.contract.capStory.key === key);
      if (posted) return;
      const owner = this.owner(ch.province);
      const issuer = FACTIONS[owner].neutral || this.isCalamity(owner) || this.isDestroyed(owner) ? 'locals' : owner;
      const ph = this.captainPhase(key);
      const level = clamp(Math.max(TIER_LEVELS[PROVINCES[ch.province].tier][0], r + 2, ph.level - 3) + cs.ch, 1, this.maxContractLevel());
      const c = this.makeContract({ province: ch.province, type: ch.type, issuer, enemy: ch.enemy, title: ch.title, level, size: 4 });
      c.capStory = { key, ch: cs.ch };
      c.expires = STORY_EXPIRES;
      c.reward = Math.round(c.reward * 1.3);
      c.rep *= 2;
      s.contracts.unshift(c);
      this.log(`영입 의뢰 「${ch.title}」 (${C.name} ${cs.ch + 1}/${C.chapters.length}장)이(가) 올라왔습니다.`, 'event');
      s.pendingReports.push({ special: 'dialog', captain: key, title: `영입 의뢰: ${ch.title}`, lines: ch.before, foot: '아무 용병단이나 보낼 수 있습니다. 마감은 없습니다.' });
    });
  },

  completeCaptainChapter(story) {
    const s = this.state, C = CAPTAINS[story.key], cs = s.captains[story.key];
    const ch = C.chapters[story.ch];
    cs.ch = story.ch + 1;
    if (cs.ch >= C.chapters.length) return this.captainJoin(story.key, ch.after);
    this.log(`${C.name}의 영입 의뢰 「${ch.title}」 완료! (${cs.ch}/${C.chapters.length})`, 'good');
    s.pendingReports.push({ special: 'dialog', captain: story.key, title: `${ch.title} — 완료`, lines: ch.after, foot: '' });
  },

  captainJoin(key, before = []) {
    const s = this.state, C = CAPTAINS[key], cs = s.captains[key];
    const ph = this.captainPhase(key);
    const level = Math.max(ph ? ph.level : 2, this.rankIndex() * 2 + 2);
    const m = this.makeNamedCaptain(key, level);
    cs.status = 'joined';
    s.mercs.push(m);
    this.log(`용병대장 ${C.title} ${m.name}(${this.className(m)}, Lv.${m.level})이(가) 길드에 합류했습니다! 용병단을 맡기세요.`, 'good');
    s.pendingReports.push({ special: 'dialog', captain: key, title: `${C.title} ${C.name} 합류`, lines: [...before, ...C.join],
      foot: `예비 인원으로 대기합니다. 대장 자리가 빈 용병단에 배속하거나, 용병단을 새로 창설하세요.` });
  },
});
