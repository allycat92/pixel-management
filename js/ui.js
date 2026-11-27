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
  // 일러스트가 있으면 일러스트, 없으면 도트 초상화
  const artPortrait = (artId, look, cls = 'portrait', scale = 3) => Art.img(artId, `${cls} art-portrait`) || Sprites.clone(Sprites.merc(look, scale, 0), cls);
  // 이벤트 그림 (없으면 null)
  const eventArt = (key) => Art.img(Art.idOf.event(key), 'event-art');
  const mini = (look) => Sprites.clone(Sprites.merc(look, 2, 0), 'mini');
  const bonusText = (b) => Object.entries(b).map(([k, v]) => `${STAT_NAMES[k]}+${v}`).join(' ');
  const signed = (v) => `${v > 0 ? '+' : ''}${v}`;

  // 깃발
  const companyFlag = (c, scale = 2) => Sprites.clone(Sprites.flag(c.color, '#e8e4d8', scale, 2), 'flag');
  const factionFlag = (f, scale = 2) => Sprites.clone(Sprites.flag(FACTIONS[f].color, FACTIONS[f].accent, scale, FACTION_MARK[f] || 0), 'flag');
  const factionTag = (f) => el('span', { class: 'ftag', style: `--fc:${FACTIONS[f].color}` }, factionFlag(f, 1), FACTIONS[f].short);

  const soldierLook = factionSoldierLook;   // js/world.js (출격 편성도 같은 규칙을 쓴다)

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
    const total = Game.heroStoryLength(m);
    return el('div', { class: 'hero-line' },
      el('span', { class: 'hero-title', text: `★ ${Game.guildText(m.title)}` }),
      next ? el('span', { class: 'muted small', text: ` 인연 ${m.bond}/${next.bond}` }) : el('span', { class: 'good small', text: ' 이야기 완결' }),
      el('div', { class: 'small muted', text: `이야기 ${ch}/${total}장 · 레벨 상한 ${HERO_CAPS[ch]} · 성장률 ×${HERO_GROWTH[ch]} · 고유 스킬 ×${1 + ch * 0.25}${next ? ` (다음 장: 상한 ${HERO_CAPS[ch + 1]})` : ''}` }));
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
      m.awakened ? el('div', { class: 'skill-line small' }, el('span', { class: 'skill awake',
        title: Game.battleMode() ? '각성: 전투 체력·공격 +15%' : '각성: 전투력 +15%', text: '각성' })) : null);
  }

  function roleBadge(m) {
    if (Game.isCaptain(m)) return el('span', { class: 'role-badge captain', title: '용병대장: 고유 직업, 높은 성장률, 레벨 상한 40', text: '♛ 대장' });
    if (m.hcls) return el('span', { class: 'role-badge hero', title: '특별 용병: 고유 직업을 가진 대원. 이야기를 진행할수록 강해진다', text: '★ 특별 용병' });
    return el('span', { class: 'role-badge unit', title: '용병 대원: 승급하면서 직업을 선택한다', text: `${UNIT_TIERS[Game.classTier(m)].name} 대원` });
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

  // 전투 능력치 (js/stats.js): 능력치·장비에 개인 컨디션(특성 × 사기 × 피로)을 곱한 체력·공격, 그리고 방어.
  // 전우·지휘·의뢰 적성은 출격할 때 더해진다.
  function battleLine(m) {
    const sh = Stats.sheet(m), p = sh.parts;
    const num = (label, v) => el('span', { class: 'bs' }, el('span', { class: 'muted', text: label }), el('b', { text: Math.round(v) }));
    return el('div', { class: 'battle-line small', title: '전투 능력치: 능력치와 장비에 컨디션을 곱한 값입니다. 방어에는 컨디션이 붙지 않습니다.' },
      el('span', { class: 'bs-title', text: '전투' }),
      num(Game.battleMode() ? '전투 체력' : '체력', sh.hp), num('공격', sh.atk), num('방어', sh.def),
      el('span', { class: `chip cond-chip ${sh.mul > 1.001 ? 'good' : sh.mul < 0.999 ? 'bad' : ''}`,
        title: `컨디션 = 특성·직업 ×${p.trait.toFixed(2)} · 사기 ×${p.morale.toFixed(2)} · 피로 ×${p.fatigue.toFixed(2)}`, text: `컨디션 ×${sh.mul.toFixed(2)}` }));
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
        el('div', { class: 'portrait-wrap' }, artPortrait(Art.idOf.merc(m), m.look)),
        el('div', { class: 'card-title' },
          el('div', { class: 'name' }, m.name, el('span', { class: 'lv', text: ` Lv. ${m.level}` })),
          el('div', { class: 'sub' }, roleBadge(m), ' ', el('span', { class: `cls cls-${m.cls} ${m.adv || m.cap ? 'adv' : ''}`, text: Game.className(m) }), ' ',
            m.trait !== 'none' ? el('span', { class: `trait ${TRAITS[m.trait].unique ? 'unique' : ''}`,
              title: describeTrait(m.trait, Game.battleMode()), text: TRAITS[m.trait].name }) : null),
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
      battleLine(m),
      opts.recruit ? null : el('div', { class: 'exp' },
        el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-exp', style: `width:${(m.exp / Game.expToNext(m)) * 100}%` })),
        el('span', { class: Game.atCap(m) ? 'warn' : '', text: Game.atCap(m)
          ? (Game.isCaptain(m) ? `최고 레벨 ${Game.levelCap(m)}` : m.hcls ? `레벨 상한 ${Game.levelCap(m)} — ${Game.heroCh(m) < Game.heroStoryLength(m) ? '이야기를 진행해야 성장합니다' : '최고 단계'}`
            : `레벨 상한 ${Game.levelCap(m)} — ${Game.classTier(m) < 2 ? '승급해야 성장합니다' : '최고 단계'}`)
          : `경험치 ${m.exp}/${Game.expToNext(m)} · 레벨 상한 ${Game.levelCap(m)}` })),
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
        onclick: () => confirmBox(Game.isCaptain(m) ? `용병대장 ${m.name}${josa(m.name, '을', '를')} 내보낼까요? 대장은 단 한 명뿐인 인물이라 다시는 영입할 수 없습니다.`
          : `${m.name}${josa(m.name, '을', '를')} 해고할까요? 장착한 장비는 창고로 돌아옵니다.`, () => Game.dismiss(m.id)) }));
    }
    openModal(el('div', { class: 'merc-detail' }, mercCard(m, { actions }),
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
    openModal(el('div', { class: 'merc-detail' },
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
    const card = (look, name, skill, desc, bonus, foot, current) => el('div', { class: `promo-card ${current ? 'current' : ''}` },
      el('div', { class: 'portrait-wrap' }, Sprites.clone(Sprites.merc(look, 4, 0), 'promo-portrait')),
      el('div', { class: 'name', text: name }),
      el('div', { class: 'skill act', text: `◆ ${skill}` }),
      el('div', { class: 'small', text: desc }),
      bonus ? el('div', { class: 'small good' }, '즉시',
        Object.entries(bonus).flatMap(([k, v]) => [' ', el('span', { class: 'stat-token', text: `${statName[k]}+${v}` })])) : null,
      foot);
    const baseLook = { ...m.look, adv: undefined, master: undefined };
    const skillText = (c) => `전투: ${describeBattle(c.b)} / 의뢰: ${describeFx(c.fx, Game.battleMode())}`;
    // 계통도: 기본 직업 → 두 갈래 상급 → 각각의 최상급
    const tree = el('div', { class: 'class-tree' },
      el('div', { class: 'tree-col' }, el('div', { class: 'tree-title', text: `기본 (레벨 상한 ${UNIT_TIERS[0].cap})` }),
        card(baseLook, CLASSES[m.cls].name, CLASS_SKILLS[m.cls].name, skillText(CLASS_SKILLS[m.cls]), null, null, !m.adv)),
      el('div', { class: 'tree-col' }, el('div', { class: 'tree-title', text: `상급 · 레벨 ${PROMOTE_LEVEL} · ${PROMOTE_COST} 금화 (상한 ${UNIT_TIERS[1].cap})` }),
        PROMOTIONS[m.cls].map((p) => {
          const can = Game.canPromote(m);
          const locked = m.adv && m.adv !== p.key;
          const foot = m.adv === p.key ? el('div', { class: 'small good', text: '현재 직업 계통' })
            : locked ? el('div', { class: 'small muted', text: '다른 갈래를 골랐습니다' })
            : el('button', { class: 'btn primary small', disabled: !can || s.gold < PROMOTE_COST ? 'disabled' : null,
              title: can ? '' : `레벨 ${PROMOTE_LEVEL}부터 승급할 수 있습니다`, onclick: () => { Game.promote(m.id, p.key); openPromote(m.id); } },
            icon('coin'), ` ${PROMOTE_COST} 승급`);
          const c = card({ ...baseLook, adv: p.key }, p.name, p.skill, skillText(p), p.bonus, foot, m.adv === p.key && !m.master);
          if (locked) c.classList.add('locked');
          return c;
        })),
      el('div', { class: 'tree-col masters' }, el('div', { class: 'tree-title', text: `최상급 · 레벨 ${MASTER_LEVEL} · ${MASTER_COST} 금화 (상한 ${UNIT_TIERS[2].cap})` }),
        PROMOTIONS[m.cls].flatMap((p) => MASTERS[p.key].map((mc) => {
          const mine = m.adv === p.key;
          const foot = m.master === mc.key ? el('div', { class: 'small good', text: '현재 직업' })
            : m.master ? el('div', { class: 'small muted', text: '다른 갈래를 골랐습니다' })
            : !mine ? el('div', { class: 'small muted', text: `${p.name}에서 승급` })
            : el('button', { class: 'btn primary small', disabled: !Game.canMaster(m) || s.gold < MASTER_COST ? 'disabled' : null,
              title: Game.canMaster(m) ? '' : `레벨 ${MASTER_LEVEL}부터 승급할 수 있습니다`, onclick: () => { Game.promoteMaster(m.id, mc.key); openPromote(m.id); } },
            icon('coin'), ` ${MASTER_COST} 승급`);
          const c = card({ ...baseLook, adv: p.key, master: mc.key }, mc.name, mc.skill, skillText(mc), mc.bonus, foot, m.master === mc.key);
          if ((m.adv && !mine) || (m.master && m.master !== mc.key)) c.classList.add('locked');
          return c;
        }))));
    openModal(el('div', {},
      el('h2', {}, mini(m.look), ` ${m.name}의 직업 계통 — 현재 ${Game.className(m)} 레벨 ${m.level}`),
      el('p', { class: 'muted small', text: '대원은 개인 능력치에 편차가 없습니다. 같은 직업·레벨이면 능력치가 같고, 승급할 때마다 두 갈래 중 하나를 골라 역할을 정합니다. 대원은 현재 직업의 액티브 스킬 하나를 씁니다(전투에서는 기본 공격/치유, 의뢰에서는 효과). 레벨 상한에 닿으면 승급해야 더 성장하며, 승급은 되돌릴 수 없습니다.' }),
      tree,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '뒤로', onclick: () => openMerc(m.id) }))));
  }

  function openEquip(mercId) {
    const s = Game.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m) return;
    const body = el('div', { class: 'merc-detail' },
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
  // 보고서·대화·선택지는 플레이어가 끝까지 확인할 때까지 저장의 s.reportSlot 에 남는다 (새로고침하면 그 자리로 돌아온다).
  // s.reportSlot = { item: 보고서, stage: 'battle'|'report' (의뢰), line: 대화 줄, atChoice, chosen: 고른 선택지, notes }
  // 대기열 -> 칸 이동과 칸 비우기는 각각 한 번의 저장이라 같은 보고서가 두 번 나오거나 사라지지 않는다.
  function showReports() {
    const s = Game.state;
    if (modalOpen) return;
    if (!s.reportSlot) {
      // 옛 저장(첫 대장을 고르다 새로고침해 선택 화면이 사라진 경우) 복구
      if (Game.needsStarter() && !s.pendingReports.some((x) => x.special === 'starter')) s.pendingReports.unshift({ special: 'starter' });
      if (!s.pendingReports.length) return;
      const item = s.pendingReports.shift();
      s.reportSlot = { item };
      if (!item.special) s.reportSlot.stage = s.settings.battle ? 'battle' : 'report';
      Game.save();
    }
    presentSlot(s.reportSlot);
  }
  // 칸의 보고서를 다 봤다: 비우고 저장한 뒤 다음 보고서로
  function finishSlot() {
    Game.state.reportSlot = null;
    Game.save();
    closeModal();
  }
  function presentSlot(slot) {
    const r = slot.item;
    if (!r) return finishSlot();
    if (r.special === 'starter') return openStarterChoice();
    if (r.special === 'dialog' || r.special === 'notice') return openDialog(r, slot);
    if (r.special) return openModal(specialReport(r), true);
    if (slot.stage === 'battle') {
      // 전투 연출 중에는 상단 막대·소식줄이 이 보고서 이전 값을 보여 준다 (결과를 미리 알리지 않도록)
      const battle = Battle.play(r, () => {
        if (Game.state.reportSlot !== slot) return;
        slot.stage = 'report';
        Game.save();
        openModal(missionReport(r), true);
        renderTop();
      });
      const head = battle.querySelector('.battle-head');
      head.firstChild.replaceWith(
        el('span', { class: 'battle-title', text: r.quest.title }), ' — ',
        el('span', { class: 'battle-region', text: PROVINCES[r.quest.province].name }));
      openModal(battle, true);
      renderTop();
    } else openModal(missionReport(r), true);
  }

  // ───────── 결과 미리 보기 방지 ─────────
  // 판정 직후 금화·명성·일지가 이미 바뀌어 있으므로, 아직 공개하지 않은 의뢰 보고서(연출 중 + 대기 중)의
  // 몫을 빼서 보여 준다. 게임 상태와 저장은 건드리지 않는다.
  // 보고서 -> { before } : 판정 직전 가장 최근 일지 항목 (소식줄은 이것보다 새 줄을 보여 주지 않는다)
  const reportDeltas = new WeakMap();
  function hookResolve() {
    const orig = Game.resolveMission;
    if (typeof orig !== 'function' || orig.spoilerHook) return;
    const wrapped = function (mission) {
      const s = this.state;
      const gold = s.gold, rep = s.rep, before = s.log[0] || null;
      const queued = new Set(s.pendingReports);
      const out = orig.apply(this, arguments);
      // 구원자 화면의 「살아남은 세력」은 쌓인 그 순간의 명단으로 고정한다 (같은 날 뒤이은 판정의 세력 멸망이 앞당겨 보이지 않게)
      s.pendingReports.forEach((x) => { if (x.special === 'savior' && !queued.has(x) && !x.alive) x.alive = Game.aliveFactions(); });
      const report = s.pendingReports.find((x) => !x.special && x.quest === mission.contract && !reportDeltas.has(x));
      if (report) {
        // 판정 중 보고서보다 먼저 쌓인 소식(구원자·세력 멸망·징조 등)은 그 보고서 바로 뒤로: 전투보다 결과가 먼저 보이지 않게
        const q = s.pendingReports;
        const early = q.slice(0, q.indexOf(report)).filter((x) => !queued.has(x));
        if (early.length) {
          early.forEach((x) => q.splice(q.indexOf(x), 1)); // 같은 배열을 고친다 (다른 곳이 참조를 들고 있을 수 있음)
          q.splice(q.indexOf(report) + 1, 0, ...early);
        }
        reportDeltas.set(report, { before });
        // 실제로 바뀐 금화·명성 (명성 0 하한, 이야기 보상 포함). 표시 전용이라 게임 규칙은 읽지 않는다.
        // pendingReports 와 함께 저장되므로 새로 불러와도 정확하다.
        report.shownDelta = { gold: s.gold - gold, rep: s.rep - rep };
      }
      return out;
    };
    wrapped.spoilerHook = true;
    Game.resolveMission = wrapped;
  }
  function rankAt(rep) {
    let idx = 0;
    RANKS.forEach((r, i) => { if (rep >= r.rep) idx = i; });
    return idx;
  }
  // 상단 막대에 보여 줄 값: { gold, rep, ticker(일지 항목 | null) }
  function shownTop() {
    const s = Game.state;
    const out = { gold: s.gold, rep: s.rep, ticker: s.log[0] || null };
    if (!s.settings.battle) return out;
    const slot = s.reportSlot;
    const playing = slot && slot.stage === 'battle' ? slot.item : null; // 전투 연출 중인 보고서
    const unseen = [playing, ...s.pendingReports].filter((r) => r && !r.special && r.quest);
    if (!unseen.length) return out;
    unseen.forEach((r) => {
      const d = r.shownDelta || { gold: r.gold || 0, rep: r.rep || 0 };
      out.gold -= d.gold || 0;
      out.rep -= d.rep || 0;
    });
    out.rep = Math.max(0, out.rep);
    // 소식줄: 가장 먼저 판정된 미공개 보고서의 판정 직전 줄. 기록이 없는 보고서(저장에서 불러옴)가 있으면 오늘 줄은 모두 숨긴다.
    const first = reportDeltas.get(unseen[0]);
    out.ticker = first ? first.before : null;
    if (!first || unseen.some((r) => !reportDeltas.has(r))) {
      if (!out.ticker || out.ticker.day >= s.day) out.ticker = s.log.find((e) => e.day < s.day) || null;
    }
    return out;
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
            el('div', { class: 'small', text: `경험치 +${m.exp}` }),
            m.levelUp ? el('div', { class: 'good small', text: '레벨 상승!' }) : null,
            // 전투 모드: 전투에서 실제로 쓰러진 단원만 표시한다 (부상은 쓰러졌거나 크게 다친 단원에게만 생긴다)
            m.down ? el('div', { class: 'bad small', text: m.injury ? `쓰러짐 · 부상 ${m.injury}일` : '쓰러짐' })
              : m.injury ? el('div', { class: 'bad small', text: `부상 ${m.injury}일` }) : null)));
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
      // 첫 초점은 제목(확인 버튼이 아니라): 「결과 보기」에서 Enter 를 두 번 눌러도 보고서가 바로 닫히지 않는다
      el('div', { class: `report-banner ${good ? 'good' : 'bad'} ${r.outcome}`, text: titles[r.outcome], tabindex: '-1', 'data-autofocus': '' }),
      el('h3', { text: c.title }),
      el('div', { class: 'small muted', text: `${PROVINCES[c.province].name} · 의뢰주 ${FACTIONS[c.issuer].name}${c.target ? ` · 대상 ${FACTIONS[c.target].name}` : ''}` }),
      r.battle ? el('div', { class: 'small muted', text: `출격 때 예상 「${Stats.BAND_NAMES[r.battle.band]}」 · ${!good && r.battle.end === 'time' ? `시간 초과(${Math.round(r.battle.t)}초)` : `전투 ${Math.round(r.battle.t)}초`} · 쓰러진 단원 ${r.members.filter((m) => m.down).length}명` }) : null,
      members,
      el('div', { class: 'report-rewards' },
        el('span', {}, icon('coin'), ` ${signed(r.gold)}`),
        el('span', {}, icon('star'), ` ${signed(r.rep)}`)),
      r.share ? el('div', { class: 'small muted', text: `외부 용병단 몫 ${r.share} 금화 지급` }) : null,
      effects.length ? el('div', { class: 'chips' }, effects) : null,
      r.notes.length ? el('div', { class: 'small notes' }, r.notes.map((n) => el('div', { text: `• ${n}` }))) : null,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: finishSlot })));
  }

  // 대화 (한 줄씩 타자기 효과), 마지막에 선택지가 있으면 고르게 한다
  // 첫 용병대장 선택: 한 명을 고르면 다른 후보는 떠난다
  function openStarterChoice() {
    if (!Game.needsStarter()) return finishSlot();
    const cards = STARTER_CAPTAINS.map((k) => {
      const C = CAPTAINS[k], CC = CAPTAIN_CLASSES[k];
      return el('div', { class: 'promo-card starter-card' },
        el('div', { class: 'portrait-wrap' }, artPortrait(Art.idOf.captain(k), { cls: CC.style, cap: k, ...C.look }, 'big-portrait', 5)),
        el('div', { class: 'name', text: C.name }),
        el('div', { class: 'small muted', text: C.title }),
        el('div', { class: 'skill adv', text: CC.name }),
        el('div', { class: 'small', text: CC.desc }),
        skillList({ actives: CC.acts.map((b) => ({ name: b.name, battle: describeBattle(b) })),
          passive: { name: CC.lead.name, desc: `지휘: ${describeLead(CC.lead, Game.battleMode())}`, lead: true } }, { compact: true }),
        el('div', { class: 'small muted', text: `힘 ${CC.base.str} · 민첩 ${CC.base.dex} · 지력 ${CC.base.int} · 체력 ${CC.base.hp}` }),
        el('div', { class: 'small pitch', text: `“${C.pitch[0][1]}”` }),
        el('button', { class: 'btn primary', onclick: () => { Game.state.reportSlot = null; Game.chooseStarter(k); finishSlot(); } }, `${C.name}${josa(C.name, '과', '와')} 시작한다`));
    });
    openModal(el('div', {},
      eventArt('start'),
      el('h2', { text: `첫 용병대장을 고르세요 (${cards.length}명)` }),
      el('p', { class: 'muted small', text: `용병단을 이끌 대장입니다. 대장은 고유 직업, 전투 기술 2개와 지휘 능력을 갖춘 단 한 명뿐인 인물이며, 선택받지 못한 ${STARTER_CAPTAINS.length - 1}명은 다시 만날 수 없습니다. 이후 대장은 길드 등급이 오를 때 공개되는 대장별 영입 과제를 달성해 여러 명을 얻을 수 있습니다.` }),
      el('div', { class: 'starter-choices' }, cards)), true);
  }

  // slot: 저장되는 진행 칸 (지금 줄, 선택지 화면인지, 고른 선택지). 새로고침하면 그 자리에서 다시 연다.
  function openDialog(r, slot = {}) {
    const h = r.hero && HEROES[r.hero];
    const calKey = r.enemy && Object.keys(FACTIONS).find((f) => FACTIONS[f].calamity && FACTIONS[f].leader === r.enemy);
    const portraitImg = h
      ? artPortrait(Art.idOf.hero(r.hero), { cls: HERO_CLASSES[h.hcls].style, hcls: h.hcls, ...h.look }, 'big-portrait', 5)
      : r.captain ? artPortrait(Art.idOf.captain(r.captain), { cls: CAPTAIN_CLASSES[r.captain].style, cap: r.captain, ...CAPTAINS[r.captain].look }, 'big-portrait', 5)
      : (calKey && Art.img(Art.idOf.boss(calKey), 'big-portrait art-portrait')) || Sprites.clone(Sprites.monster(r.enemy, 5, 0), 'big-portrait');
    let lines = r.lines.slice(), foot = r.foot;
    let line = 0, timer = null, typing = false, choiceDone = !r.choice;
    // 이미 고른 선택지 (효과는 고를 때 한 번만 적용·저장됨): 그 결과 대사부터
    const chosenOpt = r.choice && slot.chosen != null && HEROES[r.choice.hero].chapters[r.choice.ch].choice.options[slot.chosen];
    if (chosenOpt) { lines = chosenOpt.after.slice(); foot = (slot.notes || []).join(' · '); choiceDone = true; }
    line = Math.max(0, Math.min(lines.length - 1, slot.line | 0));
    const keep = (patch) => { Object.assign(slot, patch); if (Game.state.reportSlot === slot) Game.save(); };
    const speaker = el('div', { class: 'dialog-speaker' });
    const text = el('div', { class: 'dialog-text' });
    const next = el('button', { class: 'btn primary' });
    const footer = el('div', { class: 'dialog-foot small' });
    const choiceBox = el('div', { class: 'choice-box' });
    const portrait = el('div', { class: `dialog-portrait ${h || r.captain ? '' : 'boss'}` }, portraitImg);

    function show() {
      const [who, raw] = lines[line];
      const msg = Game.guildText(raw);
      if (r.captain) portrait.hidden = !who;
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
      footer.textContent = last && foot ? Game.guildText(foot) : '';
    }
    function showChoice() {
      const ch = HEROES[r.choice.hero].chapters[r.choice.ch].choice;
      next.style.display = 'none';
      keep({ atChoice: true });
      choiceBox.replaceChildren(el('div', { class: 'choice-prompt', text: Game.guildText(ch.prompt) }),
        ...ch.options.map((o, i) => el('button', { class: 'btn choice', onclick: () => {
          if (choiceDone || slot.chosen != null) return;
          // 고른 기록을 먼저 칸에 적어 두면 applyChoice 의 저장 한 번에 효과와 기록이 함께 남는다 (새로고침해도 한 번만 적용)
          slot.chosen = i; slot.line = 0; slot.atChoice = false;
          const res = Game.applyChoice(r.choice.hero, r.choice.ch, i);
          keep({ notes: res.notes });
          choiceDone = true;
          choiceBox.replaceChildren();
          lines = res.lines; line = 0; foot = res.notes.join(' · ');
          next.style.display = '';
          show();
          next.focus();
        } }, Game.guildText(o.label))));
      const first = choiceBox.querySelector('button');
      if (first) first.focus();
    }
    const advance = () => {
      if (typing) { clearInterval(timer); typing = false; text.textContent = Game.guildText(lines[line][1]); return; }
      if (line < lines.length - 1) { line++; keep({ line }); show(); return; }
      if (!choiceDone) { showChoice(); return; }
      clearInterval(timer); finishSlot();
    };
    next.addEventListener('click', advance);
    openModal(el('div', { class: 'dialog' },
      el('div', { class: 'dialog-title', text: Game.guildText(r.title) }),
      r.art ? eventArt(r.art) : null,
      el('div', { class: 'dialog-body', onclick: (e) => { if (e.target !== next && choiceDone) advance(); else if (typing) advance(); } },
        portrait,
        el('div', { class: 'dialog-box' }, speaker, text)),
      footer, choiceBox,
      el('div', { class: 'modal-actions' }, next)), true);
    show();
    // 선택지 화면에서 새로고침했다: 마지막 줄을 다 보여 주고 바로 선택지로
    if (!choiceDone && slot.atChoice) { clearInterval(timer); typing = false; text.textContent = Game.guildText(lines[line][1]); showChoice(); }
  }

  // 특별 보고서도 제목에 먼저 초점 (Enter 연타로 바로 닫히지 않게)
  function specialReport(r) {
    const node = specialReportBody(r);
    const banner = node.querySelector('.report-banner');
    if (banner) { banner.tabIndex = -1; banner.dataset.autofocus = ''; }
    return node;
  }
  function specialReportBody(r) {
    const s = Game.state;
    // 게임이 끝나지 않았으면 새 게임은 확인을 거친다 (취소하면 이 보고서가 다시 열린다: 아직 칸에 남아 있으므로)
    const restart = el('button', { class: `btn ${s.over ? 'primary' : 'danger'}`, text: '새 게임',
      onclick: () => (s.over ? startNewGame() : confirmBox('정말 처음부터 다시 시작할까요? 저장된 진행이 지워집니다.', newGameNow)) });
    const cont = el('button', { class: 'btn primary', text: '계속하기', onclick: finishSlot });
    if (r.special === 'news') {
      return el('div', { class: 'report news' },
        el('div', { class: 'report-banner news-banner', text: r.title }),
        r.title.endsWith('멸망') ? eventArt('destroyed') : null,
        el('div', { class: 'news-flags' }, r.factions.map((f) => factionFlag(f, 4))),
        el('p', { text: r.text }),
        el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: finishSlot })));
    }
    if (r.special === 'grace') {
      // 유예 주간에 급료를 미룬 정산 (전투 모드, js/game.js weeklyPayday)
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner bad', text: '유예 주간: 급료를 미뤘습니다' }),
        el('p', { text: `금화가 모자라 ${r.names.join(', ')}의 급료(금화 ${r.owed})를 다음 정산으로 미뤘습니다.` }),
        el('p', { text: `패배 직후의 유예 주간(${r.until}일까지)이라 단원이 떠나지 않습니다. 미룬 급료는 다음 정산에 그 주의 급료와 함께 냅니다. 그때도 못 받는 단원은 떠납니다.` }),
        el('p', { class: 'muted small', text: '미룬 급료는 용병단 화면의 주급 옆에도 보입니다.' }),
        el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: finishSlot })));
    }
    if (r.special === 'win') {
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: 'S 등급 달성!' }),
        eventArt('win'),
        el('p', { text: `${s.day}일 만에 ${s.guildName}${josa(s.guildName, '이', '가')} 대륙 최고의 길드가 되었습니다!` }),
        el('p', { class: 'muted', text: `완수 ${s.stats.completed} · 실패 ${s.stats.failed} · 전사 ${s.stats.fallen}` }),
        el('p', { class: 'muted small', text: '계속 플레이하며 남은 이야기와 세력의 운명을 지켜볼 수 있습니다.' }),
        el('div', { class: 'modal-actions' }, cont, restart));
    }
    if (r.special === 'savior') {
      const F = FACTIONS[r.calamity];
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: '대륙의 구원자' }),
        eventArt('savior') || el('div', { class: 'report-members' }, Sprites.clone(Sprites.monster(F.leader, 4, 0), 'big-portrait dead-boss')),
        el('p', { text: `${s.day}일째, ${s.guildName}의 용병단들이 ${F.leader}${josa(F.leader, '을', '를')} 쓰러뜨렸습니다.` }),
        el('p', { text: `${F.name}${josa(F.name, '은', '는')} 흩어지고, 살아남은 세력들은 폐허 위에서 다시 일어서기 시작합니다. 사람들은 이 시대를 ${s.guildName}의 이름으로 기억할 것입니다.` }),
        el('p', { class: 'muted small', text: `살아남은 세력: ${(r.alive || Game.aliveFactions()).map((f) => FACTIONS[f].name).join(', ') || '없음'} · 이후 전쟁이 아닌 의뢰의 보수가 높아집니다.` }),
        el('div', { class: 'modal-actions' }, cont, restart));
    }
    if (r.special === 'darkness') {
      const F = FACTIONS[s.calamity] || FACTIONS.demons;
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner bad disaster', text: '암흑시대' }),
        eventArt('darkness') || el('div', { class: 'report-members' }, Sprites.clone(Sprites.monster(F.leader, 4, 0), 'big-portrait')),
        el('p', { text: `${F.name}${josa(F.name, '이', '가')} 대륙의 대부분을 집어삼켰습니다. ${F.leader}의 그림자 아래, 길드의 깃발도 꺾였습니다.` }),
        el('p', { class: 'muted', text: `${s.day}일 동안 버텼습니다. 최고 명성 ${s.rep}` }),
        el('div', { class: 'modal-actions' }, restart));
    }
    if (r.special === 'legend') {
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: '전설의 길드' }),
        el('div', { class: 'report-members' }, Object.values(BOSSES).map((b) => Sprites.clone(Sprites.monster(b.enemy, 2, 0), 'mini'))),
        el('p', { text: `${s.day}일째, ${s.guildName}${josa(s.guildName, '은', '는')} 지방을 위협하던 재앙급 괴물 다섯을 모두 토벌했습니다.` }),
        el('p', { text: `음유시인들은 앞으로 수백 년 동안 ${s.guildName}의 이야기를 노래할 것입니다.` }),
        el('div', { class: 'modal-actions' }, cont, restart));
    }
    const msg = r.special === 'bankrupt' ? '빚더미에 올라앉은 길드는 결국 문을 닫았습니다...' : '모든 단원과 계약을 잃고 재기할 자금도 없습니다...';
    return el('div', { class: 'report' },
      el('div', { class: 'report-banner bad disaster', text: '게임 오버' }),
      r.special === 'bankrupt' ? eventArt('bankrupt') : null,
      el('p', { text: msg }),
      el('p', { class: 'muted', text: `${s.day}일 동안 버텼습니다. 최고 명성 ${s.rep}` }),
      el('div', { class: 'modal-actions' }, restart));
  }

  // ───────── 공통 ─────────
  function renderTop() {
    const s = Game.state;
    const shown = shownTop();
    const ri = rankAt(shown.rep);
    const rank = RANKS[ri], next = RANKS[ri + 1] || null;
    $('#guild-name').textContent = s.guildName;
    $('#day').textContent = `${s.day}일차 (${['월', '화', '수', '목', '금', '토', '일'][(s.day - 1) % 7]}) · 정산까지 ${Game.daysToPayday()}일`;
    $('#gold').textContent = shown.gold;
    $('#gold').classList.toggle('neg', shown.gold < 0);
    $('#rep').textContent = shown.rep;
    $('#rank').textContent = rank.name;
    $('#rank').className = `rank rank-${rank.name}`;
    const prog = next ? (shown.rep - rank.rep) / (next.rep - rank.rep) : 1;
    $('#rank-bar').style.width = `${prog * 100}%`;
    $('#rank-next').textContent = next ? `다음 등급(${next.name})까지 명성 ${next.rep - shown.rep}` : '최고 등급!';
    const latest = shown.ticker;
    $('#ticker').textContent = latest ? `[${latest.day}일차] ${Game.guildText(latest.text)}` : '';
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
    // 귀환까지 넘기기: 보낼 수 있는 용병단이 하나도 없을 때만 보인다 (주인 결정 7)
    $('#skip-day').hidden = !Game.waitingForReturn();
    // 유예 주간 표시 (전투 모드, 미룬 급료가 있거나 다음 정산에 돈이 모자랄 때). 아직 보지 않은 의뢰 보고서가 있으면 숨긴다 — 패배를 미리 알리지 않게
    const unseenQuest = (s.reportSlot && s.reportSlot.item && s.reportSlot.item.quest) || s.pendingReports.some((x) => !x.special && x.quest);
    const graceTo = unseenQuest ? 0 : Game.graceShown();
    const chip = $('#grace-chip');
    chip.hidden = !graceTo;
    if (graceTo) {
      chip.textContent = `유예 ~${graceTo}일`;
      chip.title = `패배 뒤 유예 주간(${graceTo}일까지): 급료가 모자라도 단원이 떠나지 않습니다. 못 준 급료${Game.backPayTotal() ? `(${Game.backPayTotal()})` : ''}는 다음 정산에 함께 냅니다.`;
    }
  }

  // ───────── 키보드 초점 ─────────
  const FOCUSABLE = 'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const focusables = (root) => [...root.querySelectorAll(FOCUSABLE)].filter((e) => e.getClientRects().length && !e.closest('.hidden'));
  // 다시 그려도 같은 자리의 컨트롤로 초점을 되돌리기 위한 기록 (data-fkey > id > 같은 순서·같은 글자)
  function describeFocus(node) {
    const app = $('#app');
    if (!node || node === document.body || !app.contains(node)) return null;
    const list = focusables(app);
    return { node, fkey: node.dataset.fkey || null, id: node.id || null, text: node.textContent.trim(), idx: list.indexOf(node) };
  }
  function restoreFocus(d) {
    if (!d) return;
    const app = $('#app');
    if (d.node.isConnected && d.node.getClientRects().length) { if (document.activeElement !== d.node) d.node.focus({ preventScroll: true }); return; }
    const list = focusables(app);
    const byKey = d.fkey && app.querySelector(`[data-fkey="${CSS.escape(d.fkey)}"]`);
    const byId = d.id && document.getElementById(d.id);
    const sameText = list.filter((e) => e.textContent.trim() === d.text);
    const target = (byKey && list.includes(byKey) && byKey) || (byId && list.includes(byId) && byId)
      || (d.idx >= 0 && list[d.idx] && list[d.idx].textContent.trim() === d.text && list[d.idx])
      || sameText[0] || (d.idx >= 0 && list[Math.min(d.idx, list.length - 1)]) || null;
    if (target) target.focus({ preventScroll: true });
  }

  function render() {
    if (!Game.state) return;
    const fd = modalOpen ? null : describeFocus(document.activeElement);
    renderTop();
    const root = $('#panel');
    const scroll = root.scrollTop;
    root.replaceChildren();
    (tabs[tab] || tabs.companies)(root);
    root.scrollTop = scroll;
    if (!modalOpen) restoreFocus(fd);
    showReports();
  }

  let opener = null; // 창을 연 컨트롤 (닫으면 초점을 돌려준다)
  function openModal(content, sticky) {
    const m = $('#modal');
    const body = m.querySelector('.modal-body');
    if (!modalOpen) opener = describeFocus(document.activeElement);
    modalOpen = true;
    body.replaceChildren(content);
    nameDialog(body, content);
    m.classList.remove('hidden');
    m.dataset.sticky = sticky ? '1' : '';
    body.scrollTop = 0;
    focusModal();
  }
  // 화면 읽기용 창 이름: 제목이 있으면 aria-labelledby, 없으면 첫 글(문단·이름)로 aria-label
  let titleSeq = 0;
  function nameDialog(body, content) {
    body.removeAttribute('aria-label');
    body.removeAttribute('aria-labelledby');
    if (!content || !content.querySelector) return;
    const title = content.querySelector('h2, .dialog-title, .report-banner, .battle-head, h3');
    // 전투 제목은 초 단위 시계가 붙어 바뀌므로 시계를 뺀 글을 고정 이름으로
    const clock = title && title.querySelector('.battle-timer');
    if (clock) {
      const text = [...title.childNodes].filter((n) => n !== clock).map((n) => n.textContent).join('').trim();
      if (text) { body.setAttribute('aria-label', text); return; }
    }
    if (title && title.textContent.trim()) {
      if (!title.id) title.id = `modal-title-${++titleSeq}`;
      body.setAttribute('aria-labelledby', title.id);
      return;
    }
    const first = content.querySelector('p, .name, h4') || content;
    const text = first.textContent.replace(/\s+/g, ' ').trim();
    if (text) body.setAttribute('aria-label', text.length > 80 ? `${text.slice(0, 79)}…` : text);
  }
  // 창 안의 첫 컨트롤(또는 data-autofocus)로 초점
  function focusModal() {
    const body = $('#modal .modal-body');
    const list = focusables(body);
    const explicit = body.querySelector('[data-autofocus]:not([disabled])');
    if (!explicit && body.scrollHeight > body.clientHeight) {
      const title = document.getElementById(body.getAttribute('aria-labelledby'));
      if (title) title.tabIndex = -1;
      (title || body).focus({ preventScroll: true });
      return;
    }
    (explicit || list[0] || body).focus({ preventScroll: true });
  }
  function hideModal() {
    modalOpen = false;
    $('#modal').classList.add('hidden');
    const d = opener;
    opener = null;
    if (d && d.node.isConnected) d.node.focus({ preventScroll: true });
    return d;
  }
  function closeModal() {
    Battle.stop();
    const d = hideModal();
    render();
    if (!modalOpen) restoreFocus(d);
  }

  function confirmBox(text, onYes) {
    openModal(el('div', {},
      el('p', { text }),
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn', text: '취소', onclick: closeModal }),
        el('button', { class: 'btn danger', text: '확인', onclick: () => { const d = hideModal(); onYes(); render(); if (!modalOpen) restoreFocus(d); } }))));
  }

  // 새 게임: 옛 게임의 대기 보고서가 새 게임에서 열리지 않도록 상태를 먼저 바꾸고 나서 그린다
  function newGameNow() {
    Battle.stop();
    Game.clearSave();
    Game.newGame();
    // 시험용 주소 ?resolve=battle 로 연 창이면 새 게임도 전투 모드 (js/main.js)
    if (typeof location !== 'undefined' && new URLSearchParams(location.search).get('resolve') === 'battle') Game.setResolve('battle');
    Game.emit();
  }
  function startNewGame() {
    const d = hideModal();
    newGameNow();
    if (!modalOpen) restoreFocus(d);
  }

  // 창이 열려 있으면 Tab/Shift+Tab 이 창 안에서만 돈다
  function trapTab(e) {
    const body = $('#modal .modal-body');
    const list = focusables(body);
    e.preventDefault();
    if (!list.length) { body.focus(); return; }
    const i = list.indexOf(document.activeElement);
    const nextI = i < 0 ? (e.shiftKey ? list.length - 1 : 0) : (i + (e.shiftKey ? -1 : 1) + list.length) % list.length;
    list[nextI].focus();
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
    $('#skip-day').addEventListener('click', () => { if (!modalOpen) Game.skipToReturn(); });
    $('#menu-btn').addEventListener('click', openMenu);
    $('#modal').addEventListener('click', (e) => {
      if (e.target.id === 'modal' && !$('#modal').dataset.sticky) closeModal();
    });
    hookResolve();
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab' && modalOpen) { trapTab(e); return; }
      if (e.key === 'Escape' && modalOpen && !$('#modal').dataset.sticky) closeModal();
      if (e.key === ' ' && !modalOpen && e.target === document.body) { e.preventDefault(); Game.nextDay(); }
    });
    $('#gold-icon').replaceWith(icon('coin'));
    $('#rep-icon').replaceWith(icon('star'));
    Game.onChange(render);
  }

  function openMenu() {
    const s = Game.state;
    const nameInput = el('input', { id: 'guild-name-input', class: 'input', value: s.guildName, maxlength: 16 });
    const battleToggle = el('input', { type: 'checkbox', id: 'opt-battle', checked: s.settings.battle ? 'checked' : null,
      onchange: (e) => { s.settings.battle = e.target.checked; Game.save(); } });
    openModal(el('div', {},
      el('h2', { text: '메뉴' }),
      el('label', { class: 'small muted', for: 'guild-name-input', text: '길드 이름' }),
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
          el('li', { text: '용병단은 소수 정예입니다: 용병대장 1명 + 대원 2명(병영 1단계부터 3명). 병영을 증축하면 용병단을 더 만들 수 있습니다.' }),
          el('li', { text: '의뢰는 용병단 단위로 맡깁니다. 의뢰를 완수하면 의뢰를 낸 세력에서 길드 평판이 오르고, 상대 세력에서는 떨어질 수 있습니다.' }),
          el('li', { text: '의뢰 결과에 따라 지방의 장악도가 바뀌고, 전쟁 중이면 지방이 다른 세력에게 넘어갑니다. 세계는 길드가 개입하지 않아도 움직입니다.' }),
          el('li', { text: '대규모 결전에는 의뢰에 따라 용병단을 최대 2개 또는 3개까지 보낼 수 있습니다. 양쪽 중 한 진영만 선택할 수 있습니다.' }),
          el('li', { text: '평판이 높은 세력은 혜택을 주고, 적대 세력은 의뢰를 끊고 보복합니다.' }),
          el('li', { text: '7일마다 주급과 계약 유지비를 냅니다. 금화가 -300 아래로 떨어지면 파산합니다. 스페이스바로 다음 날로 넘어갑니다.' }))),
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn danger', text: '새 게임', onclick: () => confirmBox('정말 처음부터 다시 시작할까요? 저장된 진행이 지워집니다.', newGameNow) }),
        el('button', { class: 'btn primary', text: '닫기', onclick: closeModal }))));
  }

  return {
    init, render, toast, tabs, setTab,
    h: { el, icon, itemIcon, portrait, artPortrait, eventArt, mini, bonusText, signed, companyFlag, factionFlag, factionTag, soldierLook, condTags, statusLabel, mercCard, roleBadge, skillList },
    openModal, closeModal, confirmBox, openMerc,
  };
})();
