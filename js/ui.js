// 화면 공통: DOM 도우미, 단원 상세·장비·전직 창, 대화/선택지, 보고서, 메뉴
// 각 탭 화면은 ui-tabs.js 에서 UI.tabs 에 등록한다.
'use strict';

const FACTION_MARK = { crown: 3, north: 1, cities: 0, church: 1, elves: 2, clans: 3, beasts: 2, demons: 1, locals: 0 };

const UI = (() => {
  let tab = 'companies';
  let modalOpen = false;
  const tabs = {};
  const $ = (sel) => document.querySelector(sel);

  function el(tag, attrs = {}, ...children) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (v !== false && v != null) e.setAttribute(k, v);
    }
    children.flat().forEach((c) => { if (c != null && c !== false) e.append(c instanceof Node ? c : document.createTextNode(c)); });
    return e;
  }

  const icon = (name, scale = 2) => Sprites.clone(Sprites.icon(name, scale), 'icon');
  const itemIcon = (base, tier, scale = 2) => Sprites.clone(Sprites.itemIcon(base, tier, scale), 'icon');
  const portrait = (look, scale = 3) => Sprites.clone(Sprites.merc(look, scale, 0), 'portrait');
  const mini = (look) => Sprites.clone(Sprites.merc(look, 2, 0), 'mini');
  const bonusText = (b) => Object.entries(b).map(([k, v]) => `${STAT_NAMES[k]}+${v}`).join(' ');
  const signed = (v) => `${v > 0 ? '+' : ''}${v}`;

  // 깃발
  const companyFlag = (c, scale = 2) => Sprites.clone(Sprites.flag(c.color, '#e8e4d8', scale, 2), 'flag');
  const factionFlag = (f, scale = 2) => Sprites.clone(Sprites.flag(FACTIONS[f].color, FACTIONS[f].accent, scale, FACTION_MARK[f] || 0), 'flag');
  const factionTag = (f) => el('span', { class: 'ftag', style: `--fc:${FACTIONS[f].color}` }, factionFlag(f, 1), FACTIONS[f].short);

  function soldierLook(f, i) {
    const sd = FACTIONS[f].soldier || FACTIONS.crown.soldier;
    const cls = sd.classes[i % sd.classes.length];
    return { cls, skin: sd.skins[i % sd.skins.length], hair: sd.hairs[(i * 7) % sd.hairs.length], longHair: i % 3 === 1, tint: { outfit: FACTIONS[f].color, accent: FACTIONS[f].accent } };
  }

  function statusLabel(m) {
    if (m.status === 'quest') {
      const mi = Game.state.missions.find((x) => x.id === m.missionId);
      return el('span', { class: 'tag tag-quest', text: `출격 중 (${mi ? mi.returnDay - Game.state.day : '?'}일)` });
    }
    if (m.status === 'injured') return el('span', { class: 'tag tag-injured', text: `부상 (${Math.ceil(m.injury)}일)` });
    return el('span', { class: 'tag tag-idle', text: '대기' });
  }

  function statBar(label, base, bonus, max, cls) {
    return el('div', { class: 'stat' },
      el('span', { class: 'stat-label', text: label }),
      el('div', { class: 'bar' },
        el('div', { class: `bar-fill ${cls}`, style: `width:${Math.min(100, (base / max) * 100)}%` }),
        bonus ? el('div', { class: 'bar-fill bar-bonus', style: `width:${Math.min(100 - Math.min(100, (base / max) * 100), (bonus / max) * 100)}%` }) : null),
      el('span', { class: `stat-val ${bonus ? 'boosted' : ''}`, text: base + bonus }));
  }

  function heroLine(m) {
    if (!m.hero) return null;
    const hs = Game.state.heroes[m.hero];
    const next = HEROES[m.hero].chapters[hs ? hs.ch : 0];
    const ch = Game.heroCh(m);
    return el('div', { class: 'hero-line' },
      el('span', { class: 'hero-title', text: `★ ${m.title}` }),
      next ? el('span', { class: 'muted small', text: ` 인연 ${m.bond}/${next.bond}` }) : el('span', { class: 'good small', text: ' 이야기 완결' }),
      el('div', { class: 'small muted', text: `이야기 ${ch}/3장 · 레벨 상한 ${HERO_CAPS[ch]} · 성장률 ×${HERO_GROWTH[ch]} · 고유 스킬 ×${1 + ch * 0.25}${ch < 3 ? ` (다음 장: 상한 ${HERO_CAPS[ch + 1]})` : ''}` }));
  }

  // 스킬 목록: 액티브(◆, 전투 + 의뢰 효과)와 패시브(◇)
  function skillList(sk, opts = {}) {
    const rows = sk.actives.map((a, i) => el('div', { class: 'sk-row' },
      el('span', { class: `skill act ${i ? 'special' : ''}`, text: `◆ ${a.name}` }),
      el('span', { class: 'sk-desc', text: `${i === 0 && sk.actives.length > 1 ? '[기본기] ' : i ? '[특기] ' : ''}${a.battle}${a.mission ? ` / 의뢰: ${a.mission}` : ''}` })));
    if (sk.passive) rows.push(el('div', { class: 'sk-row' },
      el('span', { class: `skill passive ${sk.passive.lead ? 'lead' : ''}`, text: `◇ ${sk.passive.name}` }),
      el('span', { class: 'sk-desc', text: sk.passive.desc })));
    return el('div', { class: `skill-list small ${opts.compact ? 'compact' : ''}` }, rows);
  }

  function skillLine(m) {
    return el('div', {}, skillList(Game.skillsOf(m)),
      m.awakened ? el('div', { class: 'skill-line small' }, el('span', { class: 'skill awake', title: '각성: 전투력 +15%', text: '각성' })) : null);
  }

  function roleBadge(m) {
    if (Game.isCaptain(m)) return el('span', { class: 'role-badge captain', title: '용병대장: 고유 직업, 높은 성장률, 레벨 상한 40', text: '♛ 대장' });
    if (m.hcls) return el('span', { class: 'role-badge hero', title: '특별 용병: 고유 직업을 가진 대원. 이야기를 진행할수록 강해진다', text: '★ 특별 대원' });
    return el('span', { class: 'role-badge unit', title: '용병 대원: 직업과 전직으로 역할을 정한다', text: `${UNIT_TIERS[Game.classTier(m)].name} 대원` });
  }

  function leadBox(m) {
    if (!Game.isCaptain(m)) return null;
    return el('div', { class: 'lead-box small' }, el('div', { class: 'muted', text: CAPTAIN_CLASSES[m.cap].desc }));
  }

  function condTags(m) {
    const ms = Game.moraleState(m), fs = Game.fatigueState(m);
    return [
      el('span', { class: `cond ${fs.cls}`, title: `피로 ${m.fatigue}/100`, text: fs.label }),
      el('span', { class: `cond ${ms.cls}`, title: `사기 ${m.morale}/100`, text: ms.label }),
    ];
  }

  function conditionLine(m) {
    const fs = Game.fatigueState(m), ms = Game.moraleState(m);
    return el('div', { class: 'cond-line small' },
      el('span', { class: 'muted', text: '피로' }),
      el('div', { class: 'bar thin cond-bar' }, el('div', { class: `bar-fill ${fs.cls}`, style: `width:${m.fatigue}%` })),
      el('span', { class: `cond ${fs.cls}`, text: fs.label }),
      el('span', { class: 'muted', text: '사기' }),
      el('span', { class: `cond ${ms.cls}`, title: `사기 ${m.morale}/100`, text: `${ms.label} ${m.morale}` }));
  }

  function equipRow(m) {
    return el('div', { class: 'equip-row' }, ['weapon', 'armor', 'trinket'].map((slot) => {
      const it = m.equip && m.equip[slot];
      return el('div', { class: `slot ${it ? `tier-${it.tier}` : ''}`, title: it ? `${it.name} (${bonusText(it.bonus)})` : `${SLOT_NAMES[slot]} 없음` },
        it ? itemIcon(it.base, it.tier) : el('span', { class: 'slot-empty', text: SLOT_NAMES[slot][0] }));
    }));
  }

  function relationLine(m) {
    const f = Game.friendsOf(m), r = Game.rivalsOf(m);
    if (!f.length && !r.length) return null;
    return el('div', { class: 'rel-line small' },
      f.length ? el('span', { class: 'good', text: `전우: ${f.map((x) => x.name).join(', ')}` }) : null,
      r.length ? el('span', { class: 'bad', text: `불화: ${r.map((x) => x.name).join(', ')}` }) : null);
  }

  // 단원 카드 (모집소 지원자, 단원 상세 창)
  function mercCard(m, opts = {}) {
    const co = m.companyId != null && Game.company(m.companyId);
    const statMax = Math.max(40, Math.round(m.level * 4.2)), hpMax = Math.max(90, m.level * 12);
    return el('div', { class: `card merc-card ${m.status} ${m.hero ? 'hero' : ''} ${Game.isCaptain(m) ? 'captain' : ''}` },
      el('div', { class: 'card-head' },
        el('div', { class: 'portrait-wrap' }, portrait(m.look)),
        el('div', { class: 'card-title' },
          el('div', { class: 'name' }, m.name, el('span', { class: 'lv', text: ` Lv.${m.level}` })),
          el('div', { class: 'sub' }, roleBadge(m), ' ', el('span', { class: `cls cls-${m.cls} ${m.adv || m.cap ? 'adv' : ''}`, text: Game.className(m) }), ' ',
            m.trait !== 'none' ? el('span', { class: `trait ${TRAITS[m.trait].unique ? 'unique' : ''}`, title: TRAITS[m.trait].desc, text: TRAITS[m.trait].name }) : null),
          opts.recruit ? null : el('div', { class: 'row-inline small' }, statusLabel(m), co ? el('span', { class: 'muted', text: co.name }) : el('span', { class: 'muted', text: '예비 인원' })))),
      heroLine(m),
      m.elite ? el('div', { class: 'hero-line' }, factionFlag(m.elite, 1), el('span', { class: 'hero-title', text: ` ${m.title}` })) : null,
      skillLine(m),
      leadBox(m),
      opts.recruit ? null : conditionLine(m),
      el('div', { class: 'stats' },
        statBar('힘', m.str, Game.equipBonus(m, 'str'), statMax, 'f-str'),
        statBar('민첩', m.dex, Game.equipBonus(m, 'dex'), statMax, 'f-dex'),
        statBar('지력', m.int, Game.equipBonus(m, 'int'), statMax, 'f-int'),
        statBar('체력', m.maxHp, Game.equipBonus(m, 'maxHp'), hpMax, 'f-hp')),
      opts.recruit ? null : el('div', { class: 'exp' },
        el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-exp', style: `width:${(m.exp / Game.expToNext(m)) * 100}%` })),
        el('span', { class: Game.atCap(m) ? 'warn' : '', text: Game.atCap(m)
          ? (Game.isCaptain(m) ? `최고 레벨 ${Game.levelCap(m)}` : m.hcls ? `레벨 상한 ${Game.levelCap(m)} — ${Game.heroCh(m) < 3 ? '이야기를 진행해야 성장합니다' : '최고 단계'}`
            : `레벨 상한 ${Game.levelCap(m)} — ${Game.classTier(m) < 2 ? '전직해야 성장합니다' : '최고 단계'}`)
          : `EXP ${m.exp}/${Game.expToNext(m)} · 상한 Lv.${Game.levelCap(m)}` })),
      opts.recruit ? null : equipRow(m),
      opts.recruit ? null : relationLine(m),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted', text: `주급 ${Game.wage(m)}` }),
        el('div', { class: 'btns' }, opts.actions || [])));
  }

  // ───────── 단원 상세 ─────────
  function openMerc(mercId) {
    const s = Game.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m) return closeModal();
    const actions = [];
    if (m.status === 'injured') {
      actions.push(el('button', { class: 'btn small', disabled: s.herbs > 0 ? null : 'disabled', title: '부상 3일 회복', onclick: () => { Game.useHerb(m.id); openMerc(m.id); } },
        itemIcon('herb', 0), ` 약초 (${s.herbs})`));
    }
    if (m.status !== 'quest') {
      if (Game.canPromote(m) || Game.canMaster(m)) actions.push(el('button', { class: 'btn small primary', text: Game.canMaster(m) ? '최상급 승급' : '승급', onclick: () => openPromote(m.id) }));
      else if (!Game.isCaptain(m) && !m.hcls) actions.push(el('button', { class: 'btn small', text: '직업 계통', onclick: () => openPromote(m.id) }));
      actions.push(el('button', { class: 'btn small', text: '장비', onclick: () => openEquip(m.id) }));
      actions.push(el('button', { class: 'btn small', text: '이동', onclick: () => openTransfer(m.id) }));
      actions.push(el('button', { class: 'btn small danger', text: '해고',
        onclick: () => confirmBox(Game.isCaptain(m) ? `용병대장 ${m.name}을(를) 내보낼까요? 대장은 단 한 명뿐인 인물이라 다시는 영입할 수 없습니다.`
          : `${m.name}을(를) 해고할까요? 장착한 장비는 창고로 돌아옵니다.`, () => Game.dismiss(m.id)) }));
    }
    openModal(el('div', {}, mercCard(m, { actions }),
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '닫기', onclick: closeModal }))));
  }

  // 배속 이동
  function openTransfer(mercId) {
    const m = Game.state.mercs.find((x) => x.id === mercId);
    if (!m) return;
    const rows = Game.ownCompanies().map((c) => {
      const here = m.companyId === c.id;
      const why = Game.slotProblem(m, c);
      const cap = Game.captainOf(c);
      return el('div', { class: 'row' }, companyFlag(c),
        el('div', { class: 'grow' }, el('div', { text: c.name }),
          el('div', { class: `small ${why && !here ? 'bad' : 'muted'}`, text: why && !here ? why : `대장 ${cap ? cap.name : '없음'} · 대원 ${Game.unitsOf(c).length}/${Game.unitSlots()} · 결속도 ${c.cohesion}${c.missionId ? ' · 출격 중' : ''}` })),
        el('button', { class: 'btn small', disabled: here || c.missionId || why ? 'disabled' : null,
          onclick: () => { Game.assign(m.id, c.id); closeModal(); } }, here ? '현재 소속' : Game.isCaptain(m) ? '지휘 맡기기' : '배속'));
    });
    rows.push(el('div', { class: 'row' }, el('div', { class: 'grow', text: '예비 인원 (출격하지 않음)' }),
      el('button', { class: 'btn small', disabled: m.companyId == null ? 'disabled' : null, onclick: () => { Game.assign(m.id, null); closeModal(); } }, '빼기')));
    openModal(el('div', {},
      el('h2', {}, mini(m.look), ` ${m.name} 배속 이동`),
      el('p', { class: 'muted small', text: '용병단을 옮기면 양쪽 용병단의 결속도가 조금 떨어집니다.' }),
      el('div', { class: 'list' }, rows),
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '취소', onclick: closeModal }))));
  }

  // 직업 계통도와 전직: 기본 → 상급(Lv.10) → 최상급(Lv.20)
  function openPromote(mercId) {
    const s = Game.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m || Game.isCaptain(m) || m.hcls) return;
    const statName = { str: '힘', dex: '민첩', int: '지력', maxHp: '체력' };
    const bonusTxt = (b) => Object.entries(b).map(([k, v]) => `${statName[k]}+${v}`).join(' ');
    const card = (look, name, skill, desc, bonus, foot, current) => el('div', { class: `promo-card ${current ? 'current' : ''}` },
      el('div', { class: 'portrait-wrap' }, Sprites.clone(Sprites.merc(look, 4, 0), 'promo-portrait')),
      el('div', { class: 'name', text: name }),
      el('div', { class: 'skill act', text: `◆ ${skill}` }),
      el('div', { class: 'small', text: desc }),
      bonus ? el('div', { class: 'small good', text: `즉시 ${bonusTxt(bonus)}` }) : null,
      foot);
    const baseLook = { ...m.look, adv: undefined, master: undefined };
    const skillText = (c) => `전투: ${describeBattle(c.b)} / 의뢰: ${describeFx(c.fx)}`;
    // 계통도: 기본 직업 → 두 갈래 상급 → 각각의 최상급
    const tree = el('div', { class: 'class-tree' },
      el('div', { class: 'tree-col' }, el('div', { class: 'tree-title', text: `기본 (상한 Lv.${UNIT_TIERS[0].cap})` }),
        card(baseLook, CLASSES[m.cls].name, CLASS_SKILLS[m.cls].name, skillText(CLASS_SKILLS[m.cls]), null, null, !m.adv)),
      el('div', { class: 'tree-col' }, el('div', { class: 'tree-title', text: `상급 · Lv.${PROMOTE_LEVEL} · ${PROMOTE_COST}금화 (상한 Lv.${UNIT_TIERS[1].cap})` }),
        PROMOTIONS[m.cls].map((p) => {
          const can = Game.canPromote(m);
          const locked = m.adv && m.adv !== p.key;
          const foot = m.adv === p.key ? el('div', { class: 'small good', text: '현재 직업 계통' })
            : locked ? el('div', { class: 'small muted', text: '다른 갈래를 골랐습니다' })
            : el('button', { class: 'btn primary small', disabled: !can || s.gold < PROMOTE_COST ? 'disabled' : null,
              title: can ? '' : `Lv.${PROMOTE_LEVEL}부터 승급할 수 있습니다`, onclick: () => { Game.promote(m.id, p.key); openPromote(m.id); } },
            icon('coin'), ` ${PROMOTE_COST} 승급`);
          const c = card({ ...baseLook, adv: p.key }, p.name, p.skill, skillText(p), p.bonus, foot, m.adv === p.key && !m.master);
          if (locked) c.classList.add('locked');
          return c;
        })),
      el('div', { class: 'tree-col masters' }, el('div', { class: 'tree-title', text: `최상급 · Lv.${MASTER_LEVEL} · ${MASTER_COST}금화 (상한 Lv.${UNIT_TIERS[2].cap})` }),
        PROMOTIONS[m.cls].flatMap((p) => MASTERS[p.key].map((mc) => {
          const mine = m.adv === p.key;
          const foot = m.master === mc.key ? el('div', { class: 'small good', text: '현재 직업' })
            : m.master ? el('div', { class: 'small muted', text: '다른 갈래를 골랐습니다' })
            : !mine ? el('div', { class: 'small muted', text: `${p.name}에서 승급` })
            : el('button', { class: 'btn primary small', disabled: !Game.canMaster(m) || s.gold < MASTER_COST ? 'disabled' : null,
              title: Game.canMaster(m) ? '' : `Lv.${MASTER_LEVEL}부터 승급할 수 있습니다`, onclick: () => { Game.promoteMaster(m.id, mc.key); openPromote(m.id); } },
            icon('coin'), ` ${MASTER_COST} 승급`);
          const c = card({ ...baseLook, adv: p.key, master: mc.key }, mc.name, mc.skill, skillText(mc), mc.bonus, foot, m.master === mc.key);
          if ((m.adv && !mine) || (m.master && m.master !== mc.key)) c.classList.add('locked');
          return c;
        }))));
    openModal(el('div', {},
      el('h2', {}, mini(m.look), ` ${m.name}의 직업 계통 — 현재 ${Game.className(m)} Lv.${m.level}`),
      el('p', { class: 'muted small', text: '대원은 개인 능력치에 편차가 없습니다. 같은 직업·레벨이면 능력치가 같고, 승급할 때마다 두 갈래 중 하나를 골라 역할을 정합니다. 대원은 현재 직업의 액티브 스킬 하나를 씁니다(전투에서는 기본 공격/치유, 의뢰에서는 효과). 레벨 상한에 닿으면 승급해야 더 성장하며, 승급은 되돌릴 수 없습니다.' }),
      tree,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '뒤로', onclick: () => openMerc(m.id) }))));
  }

  function openEquip(mercId) {
    const s = Game.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m) return;
    const body = el('div', {},
      el('h2', {}, mini(m.look), ` ${m.name}의 장비`),
      el('p', { class: 'muted small', text: `힘 ${Game.eff(m, 'str')} · 민첩 ${Game.eff(m, 'dex')} · 지력 ${Game.eff(m, 'int')} · 체력 ${Game.eff(m, 'maxHp')} (장비 포함)` }));
    ['weapon', 'armor', 'trinket'].forEach((slot) => {
      const cur = m.equip[slot];
      body.append(el('h3', { text: SLOT_NAMES[slot] }));
      body.append(el('div', { class: 'row item-row current' },
        cur ? itemIcon(cur.base, cur.tier, 3) : el('span', { class: 'slot-empty big', text: '—' }),
        el('div', { class: 'grow' },
          el('div', { class: `item-name tier-text-${cur ? cur.tier : 0}`, text: cur ? cur.name : '장착 안 함' }),
          cur ? el('div', { class: 'small muted', text: bonusText(cur.bonus) }) : null),
        cur ? el('button', { class: 'btn small', text: '해제', onclick: () => { Game.unequip(m.id, slot); openEquip(m.id); } }) : null));
      const options = s.inventory.filter((it) => it.slot === slot);
      if (!options.length) body.append(el('div', { class: 'muted small pad', text: '창고에 해당 장비가 없습니다. 상점에서 구입하세요.' }));
      options.forEach((it) => {
        const diffText = Object.keys(STAT_NAMES).map((k) => {
          const d = (it.bonus[k] || 0) - (cur && cur.bonus[k] ? cur.bonus[k] : 0);
          return d ? `${STAT_NAMES[k]}${signed(d)}` : null;
        }).filter(Boolean).join(' ');
        body.append(el('div', { class: 'row item-row' },
          itemIcon(it.base, it.tier, 2),
          el('div', { class: 'grow' },
            el('div', { class: `item-name tier-text-${it.tier}` }, it.name, it.loan ? el('span', { class: 'chip loan' }, factionFlag(it.loan, 1), ' 대여') : null),
            el('div', { class: 'small muted', text: bonusText(it.bonus) }),
            diffText ? el('div', { class: 'small diff', text: `변화: ${diffText}` }) : null),
          el('button', { class: 'btn small primary', text: '장착', onclick: () => { Game.equip(m.id, it.id); openEquip(m.id); } })));
      });
    });
    body.append(el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '뒤로', onclick: () => openMerc(m.id) })));
    openModal(body);
  }

  // ───────── 보고서 ─────────
  function showReports() {
    const s = Game.state;
    if (modalOpen || !s.pendingReports.length) return;
    const r = s.pendingReports.shift();
    Game.save();
    if (r.special === 'starter') return openStarterChoice();
    if (r.special === 'dialog' || r.special === 'notice') return openDialog(r);
    if (r.special) return openModal(specialReport(r), true);
    if (s.settings.battle) openModal(Battle.play(r, () => openModal(missionReport(r), true)), true);
    else openModal(missionReport(r), true);
  }

  function effectLines(r) {
    const lines = [];
    r.standing.forEach(({ f, d }) => { if (d) lines.push(el('span', { class: `chip ${d > 0 ? 'good' : 'bad'}` }, factionFlag(f, 1), ` ${FACTIONS[f].short} 평판 ${signed(d)}`)); });
    r.control.forEach(({ p, d }) => { if (d) lines.push(el('span', { class: 'chip' }, `${PROVINCES[p].name} 장악도 ${signed(d)}`)); });
    return lines;
  }

  function missionReport(r) {
    const titles = { great: '대성공!', success: '의뢰 성공', fail: '의뢰 실패', disaster: '대실패...' };
    const good = r.outcome === 'great' || r.outcome === 'success';
    const c = r.quest;
    const members = el('div', { class: 'report-members' });
    r.members.forEach((m) => {
      members.append(el('div', { class: `report-member ${m.dead ? 'dead' : ''}` },
        Sprites.clone(Sprites.merc(m.look, 3, 0), 'portrait'),
        el('div', { class: 'name', text: m.name }),
        m.dead ? el('div', { class: 'bad' }, icon('skull'), ' 전사')
          : el('div', {},
            el('div', { class: 'small', text: `EXP +${m.exp}` }),
            m.levelUp ? el('div', { class: 'good small', text: 'LEVEL UP!' }) : null,
            m.injury ? el('div', { class: 'bad small', text: `부상 ${m.injury}일` }) : null)));
    });
    r.ext.forEach((e) => {
      members.append(el('div', { class: `report-member ext ${e.betrayed ? 'dead' : ''}` },
        Sprites.clone(Sprites.merc(e.look, 3, 0), 'portrait'),
        el('div', { class: 'name small', text: e.name }),
        e.betrayed ? el('div', { class: 'bad small', text: '배신' }) : el('div', {},
          el('div', { class: `small ${e.loyalty >= 0 ? 'good' : 'bad'}`, text: `충성도 ${signed(e.loyalty)}` }),
          e.lost ? el('div', { class: 'bad small', text: `인원 -${e.lost}` }) : null)));
    });
    const effects = effectLines(r);
    return el('div', { class: 'report' },
      el('div', { class: `report-banner ${good ? 'good' : 'bad'} ${r.outcome}`, text: titles[r.outcome] }),
      el('h3', { text: c.title }),
      el('div', { class: 'small muted', text: `${PROVINCES[c.province].name} · 의뢰주 ${FACTIONS[c.issuer].name}${c.target ? ` · 대상 ${FACTIONS[c.target].name}` : ''}` }),
      members,
      el('div', { class: 'report-rewards' },
        el('span', {}, icon('coin'), ` ${signed(r.gold)}`),
        el('span', {}, icon('star'), ` ${signed(r.rep)}`)),
      r.share ? el('div', { class: 'small muted', text: `외부 용병단 몫 ${r.share} 금화 지급` }) : null,
      effects.length ? el('div', { class: 'chips' }, effects) : null,
      r.notes.length ? el('div', { class: 'small notes' }, r.notes.map((n) => el('div', { text: `• ${n}` }))) : null,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: closeModal })));
  }

  // 대화 (한 줄씩 타자기 효과), 마지막에 선택지가 있으면 고르게 한다
  // 첫 용병대장 선택: 셋 중 하나, 나머지 둘은 영영 떠난다
  function openStarterChoice() {
    if (!Game.needsStarter()) return closeModal();
    const cards = STARTER_CAPTAINS.map((k) => {
      const C = CAPTAINS[k], CC = CAPTAIN_CLASSES[k];
      return el('div', { class: 'promo-card starter-card' },
        el('div', { class: 'portrait-wrap' }, Sprites.clone(Sprites.merc({ cls: CC.style, cap: k, ...C.look }, 5, 0), 'big-portrait')),
        el('div', { class: 'name', text: C.name }),
        el('div', { class: 'small muted', text: C.title }),
        el('div', { class: 'skill adv', text: CC.name }),
        el('div', { class: 'small', text: CC.desc }),
        skillList({ actives: CC.acts.map((b) => ({ name: b.name, battle: describeBattle(b) })), passive: { name: CC.lead.name, desc: `지휘: ${CC.lead.desc}`, lead: true } }, { compact: true }),
        el('div', { class: 'small muted', text: `힘 ${CC.base.str} · 민첩 ${CC.base.dex} · 지력 ${CC.base.int} · 체력 ${CC.base.hp}` }),
        el('div', { class: 'small pitch', text: `“${C.pitch[0][1]}”` }),
        el('button', { class: 'btn primary', onclick: () => { Game.chooseStarter(k); closeModal(); showReports(); } }, `${C.name}와(과) 시작한다`));
    });
    openModal(el('div', {},
      el('h2', { text: '첫 용병대장을 고르세요' }),
      el('p', { class: 'muted small', text: `용병단을 이끌 대장입니다. 대장은 고유 직업, 액티브 스킬 2개, 지휘(패시브)를 가진 단 한 명뿐인 인물이며, 선택받지 못한 ${STARTER_CAPTAINS.length - 1}명은 다시 만날 수 없습니다. 이후 대장은 길드 등급이 오를 때 찾아오는 갈림길(후보 6명)에서 한 명씩만 얻을 수 있습니다.` }),
      el('div', { class: 'starter-choices' }, cards)), true);
  }

  function openDialog(r) {
    const h = r.hero && HEROES[r.hero];
    const portraitImg = h
      ? Sprites.clone(Sprites.merc({ cls: HERO_CLASSES[h.hcls].style, hcls: h.hcls, ...h.look }, 5, 0), 'big-portrait')
      : r.captain ? Sprites.clone(Sprites.merc({ cls: CAPTAIN_CLASSES[r.captain].style, cap: r.captain, ...CAPTAINS[r.captain].look }, 5, 0), 'big-portrait')
      : Sprites.clone(Sprites.monster(r.enemy, 5, 0), 'big-portrait');
    let lines = r.lines.slice();
    let line = 0, timer = null, typing = false, choiceDone = !r.choice;
    const speaker = el('div', { class: 'dialog-speaker' });
    const text = el('div', { class: 'dialog-text' });
    const next = el('button', { class: 'btn primary' });
    const footer = el('div', { class: 'dialog-foot small' });
    const choiceBox = el('div', { class: 'choice-box' });

    function show() {
      const [who, msg] = lines[line];
      speaker.textContent = who || '';
      speaker.style.visibility = who ? 'visible' : 'hidden';
      text.classList.toggle('narration', !who);
      text.textContent = '';
      typing = true;
      let i = 0;
      clearInterval(timer);
      timer = setInterval(() => {
        text.textContent = msg.slice(0, ++i);
        if (i >= msg.length) { clearInterval(timer); typing = false; }
      }, 26);
      const last = line === lines.length - 1;
      next.textContent = last ? (choiceDone ? '확인' : '선택하기') : '다음 ▶';
      footer.textContent = last && r.foot ? r.foot : '';
    }
    function showChoice() {
      const ch = HEROES[r.choice.hero].chapters[r.choice.ch].choice;
      next.style.display = 'none';
      choiceBox.replaceChildren(el('div', { class: 'choice-prompt', text: ch.prompt }),
        ...ch.options.map((o, i) => el('button', { class: 'btn choice', onclick: () => {
          const res = Game.applyChoice(r.choice.hero, r.choice.ch, i);
          choiceDone = true;
          choiceBox.replaceChildren();
          lines = res.lines; line = 0; r.foot = res.notes.join(' · ');
          next.style.display = '';
          show();
        } }, o.label)));
    }
    const advance = () => {
      if (typing) { clearInterval(timer); typing = false; text.textContent = lines[line][1]; return; }
      if (line < lines.length - 1) { line++; show(); return; }
      if (!choiceDone) { showChoice(); return; }
      clearInterval(timer); closeModal();
    };
    next.addEventListener('click', advance);
    openModal(el('div', { class: 'dialog' },
      el('div', { class: 'dialog-title', text: r.title }),
      el('div', { class: 'dialog-body', onclick: (e) => { if (e.target !== next && choiceDone) advance(); else if (typing) advance(); } },
        el('div', { class: `dialog-portrait ${h ? '' : 'boss'}` }, portraitImg),
        el('div', { class: 'dialog-box' }, speaker, text)),
      footer, choiceBox,
      el('div', { class: 'modal-actions' }, next)), true);
    show();
  }

  function specialReport(r) {
    const s = Game.state;
    const restart = el('button', { class: `btn ${s.over ? 'primary' : 'danger'}`, text: '새 게임', onclick: () => { closeModal(); Game.clearSave(); Game.newGame(); Game.emit(); } });
    const cont = el('button', { class: 'btn primary', text: '계속하기', onclick: closeModal });
    if (r.special === 'news') {
      return el('div', { class: 'report news' },
        el('div', { class: 'report-banner news-banner', text: r.title }),
        el('div', { class: 'news-flags' }, r.factions.map((f) => factionFlag(f, 4))),
        el('p', { text: r.text }),
        el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: closeModal })));
    }
    if (r.special === 'win') {
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: 'S랭크 달성!' }),
        el('p', { text: `${s.day}일 만에 ${s.guildName}이(가) 대륙 최고의 길드가 되었습니다!` }),
        el('p', { class: 'muted', text: `완수 ${s.stats.completed} · 실패 ${s.stats.failed} · 전사 ${s.stats.fallen}` }),
        el('p', { class: 'muted small', text: '계속 플레이하며 남은 이야기와 세력의 운명을 지켜볼 수 있습니다.' }),
        el('div', { class: 'modal-actions' }, restart, cont));
    }
    if (r.special === 'savior') {
      const F = FACTIONS[r.calamity];
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: '대륙의 구원자' }),
        el('div', { class: 'report-members' }, Sprites.clone(Sprites.monster(F.leader, 4, 0), 'big-portrait dead-boss')),
        el('p', { text: `${s.day}일째, ${s.guildName}의 용병단들이 ${F.leaderTitle} ${F.leader}을(를) 쓰러뜨렸습니다.` }),
        el('p', { text: `${F.name}은(는) 흩어지고, 살아남은 세력들은 폐허 위에서 다시 일어서기 시작합니다. 사람들은 이 시대를 은빛 늑대의 이름으로 기억할 것입니다.` }),
        el('p', { class: 'muted small', text: `살아남은 세력: ${Game.aliveFactions().map((f) => FACTIONS[f].name).join(', ') || '없음'} · 이후 한동안 전후 복구 의뢰의 보수가 높아집니다.` }),
        el('div', { class: 'modal-actions' }, restart, cont));
    }
    if (r.special === 'darkness') {
      const F = FACTIONS[s.calamity] || FACTIONS.demons;
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner bad disaster', text: '암흑시대' }),
        el('div', { class: 'report-members' }, Sprites.clone(Sprites.monster(F.leader, 4, 0), 'big-portrait')),
        el('p', { text: `${F.name}이(가) 대륙의 대부분을 집어삼켰습니다. ${F.leaderTitle} ${F.leader}의 그림자 아래, 길드의 깃발도 꺾였습니다.` }),
        el('p', { class: 'muted', text: `${s.day}일 동안 버텼습니다. 최고 명성 ${s.rep}` }),
        el('div', { class: 'modal-actions' }, restart));
    }
    if (r.special === 'legend') {
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: '전설의 길드' }),
        el('div', { class: 'report-members' }, Object.values(BOSSES).map((b) => Sprites.clone(Sprites.monster(b.enemy, 2, 0), 'mini'))),
        el('p', { text: `${s.day}일째, ${s.guildName}은(는) 대륙의 모든 재앙을 물리쳤습니다.` }),
        el('p', { text: '음유시인들은 앞으로 수백 년 동안 은빛 늑대의 이야기를 노래할 것입니다.' }),
        el('div', { class: 'modal-actions' }, restart, cont));
    }
    const msg = r.special === 'bankrupt' ? '빚더미에 올라앉은 길드는 결국 문을 닫았습니다...' : '모든 단원과 계약을 잃고 재기할 자금도 없습니다...';
    return el('div', { class: 'report' },
      el('div', { class: 'report-banner bad disaster', text: '게임 오버' }),
      el('p', { text: msg }),
      el('p', { class: 'muted', text: `${s.day}일 동안 버텼습니다. 최고 명성 ${s.rep}` }),
      el('div', { class: 'modal-actions' }, restart));
  }

  // ───────── 공통 ─────────
  function renderTop() {
    const s = Game.state;
    const rank = Game.rank(), next = Game.nextRank();
    $('#guild-name').textContent = s.guildName;
    $('#day').textContent = `${s.day}일차 (${['월', '화', '수', '목', '금', '토', '일'][(s.day - 1) % 7]}) · 정산까지 ${Game.daysToPayday()}일`;
    $('#gold').textContent = s.gold;
    $('#gold').classList.toggle('neg', s.gold < 0);
    $('#rep').textContent = s.rep;
    $('#rank').textContent = rank.name;
    $('#rank').className = `rank rank-${rank.name}`;
    const prog = next ? (s.rep - rank.rep) / (next.rep - rank.rep) : 1;
    $('#rank-bar').style.width = `${prog * 100}%`;
    $('#rank-next').textContent = next ? `다음 ${next.name}랭크까지 ${next.rep - s.rep}` : '최고 등급!';
    const latest = s.log[0];
    $('#ticker').textContent = latest ? `[${latest.day}일차] ${latest.text}` : '';
    $('#ticker').className = `ticker ${latest ? latest.kind : ''}`;
    document.querySelectorAll('.tab').forEach((b) => {
      b.classList.toggle('active', b.dataset.tab === tab);
      const badge = b.querySelector('.badge');
      if (!badge) return;
      const n = {
        contracts: s.contracts.length,
        recruit: s.recruits.length,
        factions: s.wars.length,
      }[b.dataset.tab];
      badge.textContent = n || '';
      badge.classList.toggle('star',
        (b.dataset.tab === 'contracts' && s.contracts.some((c) => c.story || c.campaign || c.boss))
        || (b.dataset.tab === 'recruit' && s.recruits.some((r) => r.hero)));
    });
    $('#next-day').disabled = !!s.over;
  }

  function render() {
    if (!Game.state) return;
    renderTop();
    const root = $('#panel');
    const scroll = root.scrollTop;
    root.replaceChildren();
    (tabs[tab] || tabs.companies)(root);
    root.scrollTop = scroll;
    showReports();
  }

  function openModal(content, sticky) {
    modalOpen = true;
    const m = $('#modal');
    m.querySelector('.modal-body').replaceChildren(content);
    m.classList.remove('hidden');
    m.dataset.sticky = sticky ? '1' : '';
  }
  function closeModal() {
    Battle.stop();
    modalOpen = false;
    $('#modal').classList.add('hidden');
    render();
  }

  function confirmBox(text, onYes) {
    openModal(el('div', {},
      el('p', { text }),
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn', text: '취소', onclick: closeModal }),
        el('button', { class: 'btn danger', text: '확인', onclick: () => { modalOpen = false; $('#modal').classList.add('hidden'); onYes(); render(); } }))));
  }

  let toastTimer;
  function toast(msg) {
    const t = $('#toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
  }

  function setTab(t) { tab = t; $('#panel').scrollTop = 0; render(); }

  function init() {
    document.querySelectorAll('.tab').forEach((b) => b.addEventListener('click', () => setTab(b.dataset.tab)));
    $('#next-day').addEventListener('click', () => { if (!modalOpen) Game.nextDay(); });
    $('#menu-btn').addEventListener('click', openMenu);
    $('#modal').addEventListener('click', (e) => {
      if (e.target.id === 'modal' && !$('#modal').dataset.sticky) closeModal();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalOpen && !$('#modal').dataset.sticky) closeModal();
      if (e.key === ' ' && !modalOpen && e.target === document.body) { e.preventDefault(); Game.nextDay(); }
    });
    $('#gold-icon').replaceWith(icon('coin'));
    $('#rep-icon').replaceWith(icon('star'));
    Game.onChange(render);
  }

  function openMenu() {
    const s = Game.state;
    const nameInput = el('input', { class: 'input', value: s.guildName, maxlength: 16 });
    const battleToggle = el('input', { type: 'checkbox', id: 'opt-battle', checked: s.settings.battle ? 'checked' : null,
      onchange: (e) => { s.settings.battle = e.target.checked; Game.save(); } });
    openModal(el('div', {},
      el('h2', { text: '메뉴' }),
      el('label', { class: 'small muted', text: '길드 이름' }),
      el('div', { class: 'row-inline' }, nameInput,
        el('button', { class: 'btn small', text: '변경', onclick: () => {
          const v = nameInput.value.trim();
          if (v) { s.guildName = v; Game.save(); toast('이름을 바꿨습니다.'); renderTop(); }
        } })),
      el('label', { class: 'row-inline option', for: 'opt-battle' }, battleToggle, '의뢰 결과 전투 연출 보기'),
      el('div', { class: 'help' },
        el('h3', { text: '플레이 방법' }),
        el('ul', {},
          el('li', { text: '당신은 길드 운영자입니다. 단원을 고용해 직속 용병단에 배속하고, 부족한 전력은 외부 용병단과 계약해 채우세요.' }),
          el('li', { text: '의뢰는 용병단 단위로 맡깁니다. 세력 분쟁 의뢰를 맡으면 의뢰 세력의 평판은 오르고, 대상 세력의 평판은 떨어집니다.' }),
          el('li', { text: '의뢰 결과에 따라 지방의 장악도가 바뀌고, 전쟁 중이면 지방이 다른 세력에게 넘어갑니다. 세계는 길드가 개입하지 않아도 움직입니다.' }),
          el('li', { text: '대규모 결전은 여러 용병단을 동시에 보내야 하며, 양 진영 중 한쪽만 고를 수 있습니다.' }),
          el('li', { text: '평판이 높은 세력은 혜택을 주고, 적대 세력은 의뢰를 끊고 보복합니다.' }),
          el('li', { text: '7일마다 주급과 계약 유지비를 냅니다. 빚이 -300을 넘으면 파산합니다. 스페이스바로 다음 날로 넘어갑니다.' }))),
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn danger', text: '새 게임', onclick: () => confirmBox('정말 처음부터 다시 시작할까요? 저장된 진행이 지워집니다.', () => { Game.clearSave(); Game.newGame(); Game.emit(); }) }),
        el('button', { class: 'btn primary', text: '닫기', onclick: closeModal }))));
  }

  return {
    init, render, toast, tabs, setTab,
    h: { el, icon, itemIcon, portrait, mini, bonusText, signed, companyFlag, factionFlag, factionTag, soldierLook, condTags, statusLabel, mercCard, roleBadge, skillList },
    openModal, closeModal, confirmBox, openMerc,
  };
})();
