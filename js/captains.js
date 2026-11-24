// 용병대장 영입: 창설 시 선택, 갈림길(둘 중 하나), 영입 의뢰(서사)
'use strict';

Object.assign(Game, {
  // s.captains[key] = { status: 'candidate' | 'locked' | 'offered' | 'pursuing' | 'joined' | 'lost', ch, phase }
  initCaptains() {
    const s = this.state;
    s.captains = {};
    STARTER_CAPTAINS.forEach((k) => { s.captains[k] = { status: 'candidate', ch: 0, phase: 'start' }; });
    CAPTAIN_PHASES.forEach((ph) => ph.pair.forEach((k) => { s.captains[k] = { status: 'locked', ch: 0, phase: ph.key }; }));
    s.phases = {};
    CAPTAIN_PHASES.forEach((ph) => { s.phases[ph.key] = 'locked'; });
    s.pendingReports.unshift({ special: 'starter' });
  },

  captainState(key) { return this.state.captains[key]; },
  captainPhase(key) { return CAPTAIN_PHASES.find((ph) => ph.pair.includes(key)); },
  rivalOf(key) { const ph = this.captainPhase(key); return ph ? ph.pair.find((k) => k !== key) : null; },
  needsStarter() { return STARTER_CAPTAINS.some((k) => this.state.captains[k].status === 'candidate'); },

  // 실제 용병대장 단원 만들기 (이름·외형·성격이 정해져 있다)
  makeNamedCaptain(key, level) {
    const C = CAPTAINS[key];
    const m = this.makeCaptain(key, level);
    m.name = C.name; m.title = C.title; m.trait = C.trait || m.trait;
    m.look = { cls: m.cls, cap: key, ...C.look };
    return m;
  },

  // 창설 후보 셋 중 하나를 고른다. 나머지 둘은 영영 떠난다.
  chooseStarter(key) {
    const s = this.state;
    if (!STARTER_CAPTAINS.includes(key) || s.captains[key].status !== 'candidate') return;
    STARTER_CAPTAINS.forEach((k) => { s.captains[k].status = k === key ? 'joined' : 'lost'; });
    const m = this.makeNamedCaptain(key, 2);
    s.mercs.push(m);
    const co = this.ownCompanies()[0];
    if (co) { m.companyId = co.id; co.leaderId = m.id; }
    const lost = STARTER_CAPTAINS.filter((k) => k !== key).map((k) => CAPTAINS[k].name).join('·');
    this.log(`${CAPTAINS[key].title} ${m.name}이(가) 첫 용병대장이 되었습니다. ${lost}은(는) 다른 길을 찾아 떠났습니다.`, 'good');
    this.emit();
  },

  // 대장 영입 조건 (세력 평판). 그 세력이 멸망했다면 조건은 사라진다.
  captainRequirement(key) {
    const req = CAPTAINS[key].require;
    if (!req) return { ok: true, text: '' };
    const checks = Object.entries(req.standing).map(([f, v]) => this.isDestroyed(f) || this.standing(f) >= v);
    const ok = req.any ? checks.some(Boolean) : checks.every(Boolean);
    return { ok, text: req.text };
  },

  // 갈림길에서 한 명을 택한다: 상대는 영입 불가
  pursueCaptain(key) {
    const s = this.state;
    const ph = this.captainPhase(key);
    if (!ph || s.phases[ph.key] !== 'open' || s.captains[key].status !== 'offered') return;
    const rival = this.rivalOf(key);
    s.phases[ph.key] = 'chosen';
    s.captains[key].status = 'pursuing';
    s.captains[rival].status = 'lost';
    this.log(`${CAPTAINS[key].title} ${CAPTAINS[key].name}의 길을 택했습니다. ${CAPTAINS[rival].name}은(는) 길드를 떠났습니다. 영입 의뢰를 완수하면 합류합니다.`, 'event');
    this.checkCaptains();
    this.emit();
  },

  checkCaptains() {
    const s = this.state, r = this.rankIndex();
    if (!s.captains) return;
    // 등급이 오르면 갈림길이 열린다
    CAPTAIN_PHASES.forEach((ph) => {
      if (s.phases[ph.key] !== 'locked' || r < ph.rank) return;
      s.phases[ph.key] = 'open';
      ph.pair.forEach((k) => { s.captains[k].status = 'offered'; });
      const [a, b] = ph.pair.map((k) => CAPTAINS[k]);
      this.log(`갈림길(${ph.name}): ${a.title} ${a.name}와(과) ${b.title} ${b.name}이(가) 길드를 찾아왔습니다. 한 사람만 택할 수 있습니다. (모집소)`, 'event');
      s.pendingReports.push({ special: 'dialog', captain: ph.pair[0], title: `갈림길 — ${a.title} ${a.name}`, lines: a.intro, foot: '' });
      s.pendingReports.push({ special: 'dialog', captain: ph.pair[1], title: `갈림길 — ${b.title} ${b.name}`, lines: b.intro,
        foot: `두 사람 중 한 명만 택할 수 있습니다. 택하지 않은 쪽은 다시 오지 않습니다. 모집소에서 결정하세요.` });
    });
    // 택한 대장의 영입 의뢰를 올린다
    Object.entries(s.captains).forEach(([key, cs]) => {
      if (cs.status !== 'pursuing') return;
      const C = CAPTAINS[key];
      const ch = C.chapters[cs.ch];
      if (!ch || !this.provinceOpen(ch.province) || !this.captainRequirement(key).ok) return;
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
