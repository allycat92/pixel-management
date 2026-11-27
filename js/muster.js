// 출격 편성 동결: 파견하는 순간의 전투 입력(아군 능력치·지형·지원 부대·적 편성·시드)을 한 덩어리(spec)로 굳힌다.
// 예상(forecast)·판정(judge)·전투(Battle.run)가 모두 이 spec 하나만 읽는다. 여기서는 Math.random 을 쓰지 않고 상태도 바꾸지 않는다.
// 지금은 '그림자' 단계: 의뢰 결과는 여전히 판정(성공 확률)이 정하고, 능력치 전투는 귀환 때 한 번 돌려 report.shadow 에 적기만 한다.
// 설계: docs/plans/battle_stats/design.md 5장, 만든 것: stage01_notes.md
// 3단계(스위치 뒤): Game.RESOLVE === 'battle' 이면 굳힌 편성의 전투가 결과를 정한다 (battleResolve). 기본 'roll' 은 오늘 게임 그대로 — stage3_notes.md
'use strict';

// 결과를 정하는 방식: 'roll' (기본, 오늘의 성공 확률 판정) | 'battle' (출격 때 굳힌 편성의 능력치 전투).
// 저장에 남는다(state.resolve). 새 게임은 아무것도 묻지 않고 'roll' 로 시작한다. 시험용: 주소 ?resolve=battle (js/main.js), Game.setResolve('battle').
Object.defineProperty(Game, 'RESOLVE', {
  configurable: true,
  get() { return this.state && this.state.resolve === 'battle' ? 'battle' : 'roll'; },
  set(v) { this.setResolve(v); },
});

Object.assign(Game, {
  // 귀환 때 능력치 전투를 그림자로 돌릴지 (저장하지 않는다). 브라우저에서는 끈다 — 아무도 보지 않는 기록 때문에 하루 넘기기가 휴대폰에서
  // 0.5초까지 늘었다(0~1단계 검증). 측정 도구(tools/sim/shadow.js, bot.js 의 SIM_SHADOW=1)만 켠다. 편성 굳히기(muster)는 늘 한다.
  shadowBattle: typeof window === 'undefined',
  // 출격 중인 단원의 장비 잠금 (Game.equip / unequip). 봇(tools/sim/bot.js)만 끈다: 옛 봇은 출격 중인 단원에게도 장비를 갈아 끼우므로,
  // 그 판을 그대로 재현해야 하는 회귀 기준(md5)을 전투가 결과를 정하는 단계까지 지키려는 것이다.
  equipGuard: true,

  // 이 세션에서 battleResolve 가 돌린 report.battle (저장하지 않는다. 다시 불러온 보고서는 재생 전에 한 번 다시 돌려 해시를 맞춰 본다)
  judgedHere: typeof WeakSet !== 'undefined' ? new WeakSet() : { add() {}, has() { return false; } },

  battleMode() { return !!(this.state && this.state.resolve === 'battle'); },
  // 전투 모드를 켜거나 끈다. 켤 때 저장마다 하나인 비밀 소금(salt)을 정한다 — 의뢰가 생길 때 전투 시드에 굳혀 넣는다 (예측할 수 없고, 날마다 바뀌지 않는다)
  setResolve(mode) {
    const s = this.state;
    if (!s) return;
    if (mode === 'battle') {
      s.resolve = 'battle';
      if (!s.salt) s.salt = 1 + Math.floor(Math.random() * 0x7ffffffe);
    } else delete s.resolve;
  },
  // 의뢰의 전투 소금: 만들 때 굳힌 c.bseed (없으면 저장의 소금) × 의뢰 번호. 다시 올라온 의뢰(번호가 새것)는 다른 전투가 된다
  contractSalt(c) { return Stats.mix(c.bseed || (this.state && this.state.salt) || 1, c.id); },
  // 특별한 전투: 보스, 최종 결전, 특별 용병·대장 이야기의 마지막 장. 전투 모드에서 사망은 여기서만 생긴다 (주인 결정 2)
  specialBattle(c) {
    if (c.boss || c.final) return true;
    if (c.story && HEROES[c.story.hero]) return c.story.ch >= HEROES[c.story.hero].chapters.length - 1;
    if (c.capStory && CAPTAINS[c.capStory.key]) return c.capStory.ch >= CAPTAINS[c.capStory.key].chapters.length - 1;
    return false;
  },

  // 편성 규칙은 옛 전투의 plan() (js/battle.js) 과 같다: 양쪽 최대 3부대, 부대마다 3~4명.
  // 다른 점: 적·지원 부대·아군 외형이 저마다 따로 난수를 쓴다 — 누구를 보내든 적 편성은 같다 (다시 굴릴 수 없다).
  // day: 전투 시드에 섞는 날 (기본 오늘. 옛 저장의 출격은 출발한 날)
  // missionId: 실제 출격에서만 주는 번호. 의뢰판 예상에는 배신을 아직 드러내지 않는다.
  muster(c, units, day, missionId) {
    const s = this.state;
    const MAX_GROUPS = 3, GROUP_MIN = 3, GROUP_MAX = 4;
    const { own, ext, allMembers } = this.unitParts(units);
    // 전투 모드: 적 편성과 전투 시드가 저장의 소금에서 나온다 (의뢰 번호만으로는 예측할 수 없고, 날짜를 섞지 않아 하루가 지나도 같다)
    const bm = this.battleMode(), salt = bm ? this.contractSalt(c) : 0;
    const sc = Stats.scale(c, this.effectiveReq(c), bm);
    const foeSeed = bm ? Stats.mix(salt, 0xf0e) : c.foe || c.id * 7919 + 17;   // 의뢰마다 하나
    const rInt = (r, a, b) => a + Math.floor(r() * (b - a + 1));
    const rPick = (r, arr) => arr[Math.floor(r() * arr.length)];
    const looksFor = (r, color, n) => Array.from({ length: n }, () => {
      const cls = rPick(r, Object.keys(CLASSES));
      return { cls, skin: rPick(r, SKIN_TONES), hair: rPick(r, HAIR_COLORS), longHair: r() < 0.3, tint: { outfit: color, accent: '#d9a441' } };
    });
    const groups = [];

    // 아군: 파견된 용병단 (직속 → 외부, 최대 3개). 능력치는 지금(출격 피로가 붙기 전)의 값으로 굳힌다.
    const aid = allMembers.length ? Stats.aidOf(this.partyMods(allMembers).success) : 1;
    own.forEach((o) => {
      if (groups.length >= MAX_GROUPS || !o.ms.length) return;
      const ms = [...o.ms].sort((a, b) => (this.isCaptain(b) ? 1 : 0) - (this.isCaptain(a) ? 1 : 0) || b.level - a.level);
      const us = ms.slice(0, GROUP_MAX).map((m) => {
        const sh = Stats.sheet(m, { type: c.type, party: o.ms, company: o.c, members: o.ms, contract: c, aid });
        return { id: m.id, named: m.name, look: m.look, cls: m.cls, job: m.master || m.adv || m.hcls || m.cap || m.cls, trait: m.trait, level: m.level,
          leader: this.isCaptain(m), unique: this.isCaptain(m) || !!m.hcls, sk: this.battleSkillsOf(m),
          art: m.cap ? `portrait/captain/${m.cap}` : m.hero ? `portrait/hero/${m.hero}` : null, capKey: m.cap || null, heroKey: m.hero || null,
          st: { hp: sh.hp, atk: sh.atk, def: sh.def }, mul: sh.mul };
      });
      // 출격 인원이 셋이 안 되면 수습 용병이 머릿수를 채운다: 그 용병단에서 가장 낮은 단원의 레벨 (집에 두고 온 단원 포함)
      // 전투 모드: 대장은 빼고 실제 대원의 레벨만 본다 — 대장 혼자인 용병단에 대장 레벨의 수습이 붙지 않게 (대원이 없으면 1레벨)
      const kin = bm ? this.members(o.c).concat(o.ms).filter((m) => !this.isCaptain(m)) : this.members(o.c).concat(o.ms);
      const lowest = kin.length ? Math.max(1, Math.min(...kin.map((m) => m.level))) : 1;
      const r = Stats.rng(Stats.mix(foeSeed, 0xa11, o.c.id));
      looksFor(r, o.c.color, Math.max(0, GROUP_MIN - us.length)).forEach((lk) => us.push({ look: lk, cls: lk.cls, recruit: true, st: Stats.generic(lk.cls, lowest, 'minion', Stats.KN.TRAINEE_K) }));
      groups.push({ side: 0, kind: 'own', companyId: o.c.id, name: o.c.name, color: o.c.color, player: true, cohesion: o.c.cohesion, units: us });
    });
    ext.forEach((e) => {
      if (groups.length >= MAX_GROUPS) return;
      const k = ((e.specialty === c.type || (e.specialty === 'defense' && c.type === 'warDefense')) ? 1.2 : 1) * (0.9 + e.loyalty * 0.002) * Stats.KN.EXT_K;
      const n = clamp(e.size || GROUP_MIN, GROUP_MIN, GROUP_MAX);
      const r = Stats.rng(Stats.mix(foeSeed, 0xa11, e.id));
      const cap = e.captain.look;
      const us = [{ look: cap, cls: cap.cls, leader: true, st: Stats.generic(cap.cls, e.level, 'leader', k) }];
      looksFor(r, e.color, n - 1).forEach((lk) => us.push({ look: lk, cls: lk.cls, st: Stats.generic(lk.cls, e.level, 'minion', k) }));
      groups.push({ side: 0, kind: 'ext', companyId: e.id, name: e.name, color: e.color, player: true, ext: true, level: e.level, units: us });
    });

    // 아군 지원 부대: 의뢰주 세력의 병사들 (진영 부대 수를 적과 맞춘다). 부대마다 제 시드를 쓴다.
    const groupsN = Math.min(MAX_GROUPS, c.campaign || c.final || c.boss || c.level >= 5 ? 3 : 2);
    const ally = FACTIONS[c.issuer] && !FACTIONS[c.issuer].neutral ? c.issuer : null;
    const fill = Math.max(0, groupsN - groups.length);
    for (let i = 0; i < fill; i++) {
      const f = ally || 'locals';
      const r = Stats.rng(Stats.mix(foeSeed, 0x5a9, i));
      const n = rInt(r, GROUP_MIN, GROUP_MAX), base = rInt(r, 0, 99);
      const k = Stats.KN.SUPPORT_K * (ally ? 1 : Stats.KN.VILLAGER_K);
      const us = Array.from({ length: n }, (_, j) => {
        const lk = factionSoldierLook(f, base + j);
        return { look: lk, cls: lk.cls, st: Stats.generic(lk.cls, sc.lv, j === 0 ? 'leader' : 'minion', k) };
      });
      groups.push({ side: 0, kind: 'support', name: ally ? `${FACTIONS[f].short} ${FACTIONS[f].unitName}` : '마을 자경단', color: FACTIONS[f].color, units: us });
    }

    // 적군: 2~3개 부대, 부대마다 우두머리 + 2~3. 의뢰에만 달린 난수 — 보낸 용병단과 무관하다.
    const r = Stats.rng(foeSeed);
    const extra = c.level >= 6 ? 1 : 0;   // 높은 난이도일수록 꽉 찬 부대가 나온다
    if (c.enemy) {
      const def = ENEMIES[c.enemy] || {};
      const cal = FACTIONS[c.target] && FACTIONS[c.target].calamity ? c.target : null;
      const pool = (cal ? FACTIONS[cal].monsters : TERRAIN[PROVINCES[c.province].terrain].enemies).filter((n) => ENEMIES[n] && !ENEMIES[n].boss);
      const small = pool.filter((n) => !ENEMIES[n].big);
      const minion = () => (def.big ? rPick(r, small.length ? small : pool) : (r() < 0.75 ? c.enemy : rPick(r, small.length ? small : [c.enemy])));
      const mon = (name, lead) => {
        const d = ENEMIES[name] || {}, boss = lead && !!d.boss, big = lead || !!d.big;
        const arch = d.arch || 'grunt', rank = boss ? 'boss' : big ? 'big' : 'minion';
        const u = { mon: name, arch, rank, scale: boss ? 3 : big ? 2 : 1, boss, bigMon: big, st: Stats.enemy(arch, sc.lv, rank, sc.k) };
        if (bm) u.sk = Stats.monsterSkills(u);   // 전투 모드: 공격 방식은 틀이 정한다 (주술만 원거리). 예상(forecast)도 이 스킬을 읽는다
        return u;
      };
      for (let i = 0; i < groupsN; i++) {
        const lead = i === 0 ? c.enemy : (def.boss ? rPick(r, pool) : c.enemy);
        const ldef = ENEMIES[lead] || {};
        const us = [mon(lead, true)];
        const n = ldef.boss ? rInt(r, 2, 3) : Math.min(GROUP_MAX - 1, rInt(r, GROUP_MIN - 1, GROUP_MAX - 1) + extra);
        for (let j = 0; j < n; j++) us.push(mon(minion(), false));
        groups.push({ side: 1, kind: 'foe', name: ldef.boss ? lead : `${lead} 무리`, color: cal ? FACTIONS[cal].color : '#7a2430', units: us });
      }
    } else {
      const f = c.target || c.issuer;
      for (let i = 0; i < groupsN; i++) {
        const n = Math.min(GROUP_MAX, rInt(r, GROUP_MIN, GROUP_MAX) + extra);
        const base = rInt(r, 0, 99);
        const us = Array.from({ length: n }, (_, j) => {
          const lk = factionSoldierLook(f, base + j), rank = j === 0 ? 'leader' : 'minion';
          return { look: lk, cls: lk.cls, rank, st: Stats.generic(lk.cls, sc.lv, rank, sc.k) };
        });
        groups.push({ side: 1, kind: 'foe', name: `${FACTIONS[f].short} ${FACTIONS[f].unitName} ${i + 1}대`, color: FACTIONS[f].color, units: us });
      }
    }
    const spec = {
      v: 1, seed: bm ? Stats.mix(salt, 0xb7) : Stats.mix(foeSeed, day == null ? s.day : day, 0xb7), terrain: PROVINCES[c.province] ? PROVINCES[c.province].terrain : null,
      rule: Stats.ruleOf(c), limit: Stats.KN.LIMIT, lv: sc.lv, k: +sc.k.toFixed(3), need: c.size, heads: this.unitsHeadcount(units),
      ...(bm ? { bm: 1, kind: Stats.kindOf(c) } : {}), groups,   // 전투 모드 편성 표시 (예상 보정이 읽는다)
    };
    return bm && c.campaign && missionId != null ? this.battleBetrayalSpec(spec, c, missionId, ext, true) : spec;
  },

  // 굳힌 편성의 예상 전력비 { R, band } — 능력치와 스킬 빈도만 읽는다 (위치·시드·배신 없음)
  forecast(spec) { return Stats.forecast(spec); },
  // 전투 기록 → 결과 등급 { outcome, won, ours, down, standing, fled, low, mvp }
  judge(spec, rec, mods) { return Stats.judge(spec, rec, mods); },

  // 파견할 때: 전투 입력을 굳혀 출격 기록에 붙인다. 지금은 그림자라, 실패해도 파견은 그대로 간다.
  freezeMission(mission, c, units) {
    try {
      mission.spec = this.muster(c, units, undefined, mission.id);
      mission.est = this.forecast(mission.spec);
    } catch (e) {
      delete mission.spec; delete mission.est;
      if (typeof console !== 'undefined') console.error('[muster]', e);
    }
  },

  // 편성의 전투 시드와 출격·외부단 번호를 섞되 세계 난수는 쓰지 않는다.
  // 새 출격은 동조 세력에 따른 충성도 차감을 미리 반영한다. 옛 출격은 이미 차감했다.
  battleBetrayalSpec(spec, c, missionId, ext, dispatching = false) {
    const traitors = new Set(ext.filter((e) => {
      const loss = dispatching && e.disposition === 'faction' && e.sympathy === c.target ? 10 : 0;
      return e.loyalty - loss < 25 && Stats.rng(Stats.mix(spec.seed, 0xbe7a, missionId, e.id))() < 0.35;
    }).map((e) => e.id));
    return { ...spec, betrayalsFixed: true, groups: spec.groups.map((g) =>
      g.kind === 'ext' && traitors.has(g.companyId) ? { ...g, betray: true } : g) };
  },

  // 귀환할 때: 굳혀 둔 편성으로 능력치 전투를 한 번 돌리고 등급을 매겨 report.shadow 에 짧게 적는다.
  // 실제 결과(report.outcome)와 게임 상태에는 손대지 않는다. 도구용으로 { spec, rec, verdict } 를 돌려준다.
  shadowResolve(mission, report, mods) {
    if (!this.shadowBattle || typeof Battle === 'undefined' || !Battle.run) return null;
    try {
      // 옛 저장의 출격(굳힌 편성이 없다)은 지금 상태로 편성한다
      let spec = mission.spec || this.muster(mission.contract, mission.units, mission.startDay);
      const est = mission.est || this.forecast(spec);
      // 배신은 아직 귀환 때 굴린다 (판정의 난수 순서를 바꾸지 않으려고): 굴려진 결과를 편성 사본에 표시만 한다
      const traitors = new Set(mission.units.map((u) => this.company(u.companyId)).filter((e) => e && !e.own && e.betrayed).map((e) => e.id));
      if (traitors.size) spec = { ...spec, groups: spec.groups.map((g) => (g.kind === 'ext' && traitors.has(g.companyId) ? { ...g, betray: true } : g)) };
      const rec = Battle.run(spec);
      const verdict = this.judge(spec, rec, mods);
      report.shadow = { v: 1, ver: rec.ver, tab: rec.tab, seed: spec.seed, hash: rec.hash, winner: rec.winner, t: rec.t, end: rec.end,
        outcome: verdict.outcome, ours: verdict.ours, down: verdict.down, fled: verdict.fled, low: verdict.low, R: est.R, band: est.band };
      return { spec, rec, verdict };
    } catch (e) {
      report.shadow = { v: 1, err: String((e && e.message) || e) };
      if (typeof console !== 'undefined') console.error('[shadow]', e);
      return null;
    }
  },
  // ───────── 3단계: 전투가 결과를 정하는 모드 ─────────
  // 귀환할 때: 굳혀 둔 편성으로 전투를 한 번 돌려 결과를 정한다. 기록과 편성을 report.battle 에 남긴다 — 화면에서 보는 전투가 이 전투다 (Battle.play).
  // -> { spec, rec, verdict, est, share } 또는 null (전투를 돌릴 수 없으면 옛 판정으로 간다)
  battleResolve(mission, report, mods) {
    if (typeof Battle === 'undefined' || !Battle.run) return null;
    try {
      const spec = mission.spec || this.muster(mission.contract, mission.units, mission.startDay);
      const est = mission.est || this.forecast(spec);
      const rec = Battle.run(spec);
      const verdict = this.judge(spec, rec, mods);
      const share = Stats.foeShare(spec, rec);
      report.battle = { v: 1, ver: rec.ver, tab: rec.tab, hash: rec.hash, winner: rec.winner, t: rec.t, end: rec.end,
        R: est.R, band: est.band, foeShare: +share.toFixed(3), spec };
      this.judgedHere.add(report.battle);   // 이 화면에서 방금 판정한 전투: 재생 전에 다시 돌려 보지 않는다 (Battle.play, 검증 6번)
      return { spec, rec, verdict, est, share };
    } catch (e) {
      if (typeof console !== 'undefined') console.error('[battle]', e);
      return null;
    }
  },
  // 우리 단원 id → { fate, hp } (편성에 들지 못한 단원은 없다 — 서 있던 것으로 본다)
  fatesOf(spec, rec) {
    const out = new Map();
    Stats.oursOf(spec, rec).forEach((o) => { if (o.id && !o.ext) out.set(o.id, { fate: o.fate, hp: o.hp }); });
    return out;
  },
  // 외부 용병단마다 쓰러진 인원
  extDownOf(spec, rec) {
    const out = new Map();
    Stats.oursOf(spec, rec).forEach((o) => { if (o.ext && o.fate === 1) out.set(o.companyId, (out.get(o.companyId) || 0) + 1); });
    return out;
  },

  // 길드 전력 눈금: 전력이 높은 직속 용병단 (최대 BOARD_TOP 개, 단원 전부)이 별 등급마다 받을 예상 전력비 R. 기준 의뢰는 본거지의 고블린 토벌.
  // 하루에 한 번 잰다 (단원 수가 바뀌면 다시). -> { companyId(가장 강한 용병단), tabs: [{ companyId, R: [, R1 … R14] }] (강한 순) }
  capability() {
    const s = this.state;
    const c0 = this._cap;
    if (c0 && c0.st === s && c0.day === s.day && c0.n === s.mercs.length) return c0;
    const out = { st: s, day: s.day, n: s.mercs.length, companyId: 0, tabs: [] };
    const home = PROVINCE_KEYS.find((k) => PROVINCES[k].home) || PROVINCE_KEYS[0];
    const cos = this.ownCompanies().filter((co) => this.members(co).length)
      .map((co) => ({ co, p: this.ownCompanyPower(co, this.members(co), 'hunt') })).sort((a, b) => b.p - a.p).slice(0, Stats.KN.BOARD_TOP);
    cos.forEach(({ co }) => {
      const units = [{ companyId: co.id, memberIds: this.members(co).map((m) => m.id) }];
      const R = [];
      for (let L = 1; L <= LATE_MAX_LEVEL; L++) {
        const ref = { id: 0, bseed: 0x5eed, foe: 0x5eed, type: 'hunt', cat: 'monster', level: L, size: 3, days: 2, req: Math.round(Stats.nominalReq({ level: L })),
          province: home, issuer: this.owner(home), target: null, enemy: '고블린' };
        R[L] = Stats.forecast(this.muster(ref, units)).R;
      }
      out.tabs.push({ companyId: co.id, R });
    });
    out.companyId = out.tabs.length ? out.tabs[0].companyId : 0;
    this._cap = out;
    return out;
  },
  // 전투 모드의 별 상한: 길드 등급 + BM_CAP_AHEAD (재앙 뒤에는 LATE_MAX_LEVEL 까지). 등급이 오르면 더 높은 별이 열린다.
  // 오늘의 +2 는 상한 별까지 모두 압도라 게시판에 벅찬 의뢰가 없었다 (검증 3번: 1~30일 열세 이하 0%)
  // 4단계: 재앙이 일어나지 않아도 후반에는 높은 별이 열린다 (bmMaxLevel). 재앙이 없던 판은 240일 뒤 가장 강한 용병단에게 일반 의뢰가 모두 압도였다 (Q8)
  battleCap() {
    const top = this.bmMaxLevel();
    return clamp(this.lateGame() || top > 10 ? top : this.rankIndex() + Stats.KN.BM_CAP_AHEAD, 1, top);
  },
  // 전투 모드 일반 의뢰의 가장 높은 별: 재앙이 일어난 뒤에는 LATE_MAX_LEVEL (오늘과 같다). 재앙이 없어도 S 등급이면
  // BM_LATE_OPEN = [첫날, 간격] — 첫날에 ★11, 그 뒤 간격(일)마다 별 하나씩 ★14 까지 (간격 0 이면 끈다: 옛 ★10).
  // 적은 별이 정한다 (주인 결정 1) — 열리는 때는 날짜와 등급이고, 용병단의 힘을 따라가지 않는다. 특별한 의뢰는 옛 maxContractLevel 그대로
  bmMaxLevel() {
    if (this.lateGame()) return LATE_MAX_LEVEL;
    const [d0, per] = Stats.KN.BM_LATE_OPEN, day = this.state.day;
    if (!(per > 0) || this.rankIndex() < RANKS.length - 1 || day < d0) return this.maxContractLevel();
    return Math.min(LATE_MAX_LEVEL, 11 + Math.floor((day - d0) / per));
  },
  // 전투 모드의 의뢰 별 등급. 게시판이 쉬운 것부터 벅찬 것까지 늘 펼쳐지도록 층을 나눠 뽑는다:
  //  1) 게시판의 일반 의뢰가 이미 겨냥한 단계(c.aim)를 세어, BOARD_W 비율에 가장 모자란 단계를 (모자란 만큼의 가중치로) 하나 뽑는다
  //  2) 백중·열세·무모(어려운 쪽)는 가장 강한 용병단의 눈금으로, 우세·압도(쉬운 쪽)는 상위 BOARD_TOP 중 하나의 눈금으로 별을 고른다
  //     — 어려운 의뢰는 가장 강한 용병단에게도 어렵고, 약한 용병단에게도 이길 만한 의뢰가 오른다
  //  3) 그 단계에 드는 별 가운데 높은 쪽 셋 중 하나. 상한(battleCap)을 넘지 않는다
  // 적은 별 등급이 정한다 — 용병단을 따라 세지지 않는다. 용병단이 크면 같은 별이 쉬워지고, 더 높은 별이 게시판에 오른다.
  // 고른 단계는 this._aim 에 남긴다 (makeContract 가 c.aim 으로 굳힌다)
  battleLevel(p, bonus = 0) {
    const cap = this.battleCap();
    const cp = this.capability();
    if (!cp.tabs.length) return null;
    const w = Stats.KN.BOARD_W;
    const aims = this.state.contracts.filter((c) => c.aim != null && !c.relief).map((c) => c.aim);
    const need = w.map((x, b) => Math.max(0, x * (aims.length + 1) - aims.filter((a) => a === b).length));
    const tot = need.reduce((a, b) => a + b, 0);
    let x = Math.random() * tot, band = 0;
    for (; band < w.length - 1; band++) { x -= need[band]; if (x <= 0 && need[band] > 0) break; }
    const tab = band <= 2 ? cp.tabs[0] : cp.tabs[Math.floor(Math.random() * cp.tabs.length)];
    const levels = [];
    for (let L = 1; L <= cap; L++) levels.push(L);
    const inBand = levels.filter((L) => Stats.bandOf(tab.R[L]) === band);
    let L;
    if (inBand.length) L = pick(inBand.slice(-3));
    else if (band > Stats.bandOf(tab.R[1])) L = 1;                       // 가장 쉬운 별도 그 단계보다 어렵다
    else L = pick(levels.slice(-2));                                     // 열린 별이 모두 그 단계보다 쉽다: 열린 가장 높은 별 둘 중 하나
    this._aim = band;
    return clamp(L + bonus, 1, this.bmMaxLevel());
  },
  // 구호 의뢰: 길드에 대장만 남으면, 대장 혼자서도 이길 만한 쉬운 의뢰를 하나 걸어 둔다 (보수 ×1.5, 5일)
  reliefCheck() {
    const s = this.state;
    if (!s.mercs.length || s.mercs.some((m) => !this.isCaptain(m))) return;
    if (s.contracts.some((c) => c.relief) || s.missions.some((mi) => mi.contract.relief)) return;
    const cp = this.capability();
    if (!cp.tabs.length) return;
    const tab = cp.tabs[0];
    const cap = this.battleCap();
    let level = 1;
    for (let L = 1; L <= cap; L++) if (tab.R[L] >= Stats.KN.BANDS[3]) level = L;
    const home = PROVINCE_KEYS.find((k) => PROVINCES[k].home) || PROVINCE_KEYS[0];
    const c = this.makeContract({ province: home, type: 'hunt', issuer: this.owner(home), level, size: 2 });
    c.relief = true;
    c.reward = Math.round(c.reward * 1.5);
    c.expires = s.day + 5;
    c.title = `구호 의뢰: ${c.title}`;
    s.contracts.unshift(c);
    this.log(`길드에 대장만 남았습니다. 왕도에서 손쉬운 구호 의뢰를 맡겼습니다: 「${c.title}」`, 'event');
  },
});
