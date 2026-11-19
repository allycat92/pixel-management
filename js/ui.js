// 화면(DOM) 렌더링과 입력 처리
'use strict';

const UI = (() => {
  let tab = 'roster';
  let modalOpen = false;
  const $ = (sel) => document.querySelector(sel);

  function el(tag, attrs = {}, ...children) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (v !== false && v != null) e.setAttribute(k, v);
    }
    children.flat().forEach((c) => { if (c != null) e.append(c instanceof Node ? c : document.createTextNode(c)); });
    return e;
  }

  const icon = (name, scale = 2) => Sprites.clone(Sprites.icon(name, scale), 'icon');
  const itemIcon = (base, tier, scale = 2) => Sprites.clone(Sprites.itemIcon(base, tier, scale), 'icon');
  const portrait = (look, scale = 3) => Sprites.clone(Sprites.merc(look, scale, 0), 'portrait');
  const bonusText = (b) => Object.entries(b).map(([k, v]) => `${STAT_NAMES[k]}+${v}`).join(' ');

  function statusLabel(m) {
    if (m.status === 'quest') {
      const mi = Game.state.missions.find((x) => x.id === m.missionId);
      return el('span', { class: 'tag tag-quest', text: `의뢰 중 (${mi ? mi.returnDay - Game.state.day : '?'}일)` });
    }
    if (m.status === 'injured') return el('span', { class: 'tag tag-injured', text: `부상 (${Math.ceil(m.injury)}일)` });
    return el('span', { class: 'tag tag-idle', text: '대기' });
  }

  function statBar(label, base, bonus, max, cls) {
    const total = base + bonus;
    return el('div', { class: 'stat' },
      el('span', { class: 'stat-label', text: label }),
      el('div', { class: 'bar' },
        el('div', { class: `bar-fill ${cls}`, style: `width:${Math.min(100, (base / max) * 100)}%` }),
        bonus ? el('div', { class: 'bar-fill bar-bonus', style: `width:${Math.min(100 - Math.min(100, (base / max) * 100), (bonus / max) * 100)}%` }) : null),
      el('span', { class: `stat-val ${bonus ? 'boosted' : ''}`, text: total }));
  }

  function heroLine(m) {
    if (!m.hero) return null;
    const hs = Game.state.heroes[m.hero];
    const h = HEROES[m.hero];
    const next = h.chapters[hs ? hs.ch : 0];
    return el('div', { class: 'hero-line' },
      el('span', { class: 'hero-title', text: `★ ${m.title}` }),
      next ? el('span', { class: 'muted small', text: ` 인연 ${m.bond}/${next.bond}` }) : el('span', { class: 'good small', text: ' 이야기 완결' }));
  }

  function equipRow(m) {
    return el('div', { class: 'equip-row' }, ['weapon', 'armor', 'trinket'].map((slot) => {
      const it = m.equip && m.equip[slot];
      return el('div', { class: `slot ${it ? `tier-${it.tier}` : ''}`, title: it ? `${it.name} (${bonusText(it.bonus)})` : `${SLOT_NAMES[slot]} 없음` },
        it ? itemIcon(it.base, it.tier) : el('span', { class: 'slot-empty', text: SLOT_NAMES[slot][0] }));
    }));
  }

  function skillLine(m) {
    const base = CLASS_SKILLS[m.cls];
    const adv = m.adv && ADV_CLASSES[m.adv];
    return el('div', { class: 'skill-line small' },
      el('span', { class: 'skill', title: base.desc, text: base.name }),
      adv ? el('span', { class: 'skill adv', title: adv.desc, text: adv.skill }) : null,
      m.awakened ? el('span', { class: 'skill awake', title: '각성: 전투력 +15%', text: '각성' }) : null);
  }

  function conditionLine(m) {
    const ms = Game.moraleState(m), fs = Game.fatigueState(m);
    return el('div', { class: 'cond-line small' },
      el('span', { class: 'muted', text: '피로' }),
      el('div', { class: 'bar thin cond-bar' }, el('div', { class: `bar-fill ${fs.cls}`, style: `width:${m.fatigue}%` })),
      el('span', { class: `cond ${fs.cls}`, text: fs.label }),
      el('span', { class: 'muted', text: '사기' }),
      el('span', { class: `cond ${ms.cls}`, title: `사기 ${m.morale}/100`, text: `${ms.label} ${m.morale}` }));
  }

  function relationLine(m) {
    const f = Game.friendsOf(m), r = Game.rivalsOf(m);
    if (!f.length && !r.length) return null;
    return el('div', { class: 'rel-line small' },
      f.length ? el('span', { class: 'good', text: `전우: ${f.map((x) => x.name).join(', ')}` }) : null,
      r.length ? el('span', { class: 'bad', text: `불화: ${r.map((x) => x.name).join(', ')}` }) : null);
  }

  function mercCard(m, opts = {}) {
    const c = CLASSES[m.cls];
    const card = el('div', { class: `card merc-card ${m.status} ${m.hero ? 'hero' : ''}` },
      el('div', { class: 'card-head' },
        el('div', { class: 'portrait-wrap' }, portrait(m.look)),
        el('div', { class: 'card-title' },
          el('div', { class: 'name' }, m.name, el('span', { class: 'lv', text: ` Lv.${m.level}` })),
          el('div', { class: 'sub' }, el('span', { class: `cls cls-${m.cls} ${m.adv ? 'adv' : ''}`, text: Game.className(m) }), ' ',
            el('span', { class: `trait ${TRAITS[m.trait].unique ? 'unique' : ''}`, title: TRAITS[m.trait].desc, text: TRAITS[m.trait].name })),
          opts.recruit ? null : statusLabel(m))),
      heroLine(m),
      skillLine(m),
      opts.recruit ? null : conditionLine(m),
      el('div', { class: 'stats' },
        statBar('힘', m.str, Game.equipBonus(m, 'str'), 40, 'f-str'),
        statBar('민첩', m.dex, Game.equipBonus(m, 'dex'), 40, 'f-dex'),
        statBar('지력', m.int, Game.equipBonus(m, 'int'), 40, 'f-int'),
        statBar('체력', m.maxHp, Game.equipBonus(m, 'maxHp'), 90, 'f-hp')),
      opts.recruit ? null : el('div', { class: 'exp' },
        el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-exp', style: `width:${(m.exp / Game.expToNext(m)) * 100}%` })),
        el('span', { text: `EXP ${m.exp}/${Game.expToNext(m)}` })),
      opts.recruit ? null : equipRow(m),
      opts.recruit ? null : relationLine(m),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted', text: `주급 ${Game.wage(m)}` }),
        el('div', { class: 'btns' }, opts.actions || [])));
    return card;
  }

  // ───────── 탭: 용병단 ─────────
  function renderRoster(root) {
    const s = Game.state;
    const feastBtn = el('button', {
      class: 'btn small', disabled: Game.feastReady() && s.gold >= Game.feastCost() ? null : 'disabled',
      title: '대기 중인 단원 사기 +15, 피로 -15, 서로 친밀도 상승 (주 1회)', onclick: () => Game.feast(),
    }, Game.feastReady() ? `🍖 연회 열기 (${Game.feastCost()})` : `연회 (${7 - (s.day - s.lastFeast)}일 후)`);
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: `단원 명부 (${s.mercs.length}/${Game.capacity()})` }),
      el('div', { class: 'row-inline' },
        el('span', { class: 'muted', text: `주급 합계 ${Game.weeklyWageTotal()} · 정산까지 ${Game.daysToPayday()}일 · 약초 ${s.herbs}개` }),
        feastBtn)));
    if (!s.mercs.length) root.append(el('p', { class: 'empty', text: '단원이 없습니다. 주점에서 용병을 고용하세요.' }));
    const grid = el('div', { class: 'grid' });
    s.mercs.forEach((m) => {
      const actions = [];
      if (m.status === 'injured') {
        actions.push(el('button', { class: 'btn small', disabled: s.herbs > 0 ? null : 'disabled', title: '부상 3일 회복', onclick: () => Game.useHerb(m.id) },
          itemIcon('herb', 0), ` 약초`));
      }
      if (m.status !== 'quest' && Game.canPromote(m)) {
        actions.push(el('button', { class: 'btn small primary', text: '전직', onclick: () => openPromote(m.id) }));
      }
      if (m.status !== 'quest') {
        actions.push(el('button', { class: 'btn small', text: '장비', onclick: () => openEquip(m.id) }));
        actions.push(el('button', {
          class: 'btn small danger', text: '해고',
          onclick: () => confirmBox(`${m.name}을(를) 해고할까요? 장착한 장비는 창고로 돌아옵니다.`, () => Game.dismiss(m.id)),
        }));
      }
      grid.append(mercCard(m, { actions }));
    });
    root.append(grid);

    if (s.missions.length) {
      root.append(el('h2', { class: 'mt', text: '진행 중인 의뢰' }));
      const list = el('div', { class: 'list' });
      s.missions.forEach((mi) => {
        const party = mi.party.map((id) => s.mercs.find((m) => m.id === id)).filter(Boolean);
        list.append(el('div', { class: 'row mission' },
          Sprites.clone(Sprites.monster(mi.quest.enemy, 2, 0), 'mini'),
          el('span', { class: 'grow' }, mi.quest.title, el('span', { class: 'muted small', text: ` · ${REGIONS[mi.quest.region].name}` })),
          el('span', { class: 'party-mini' }, party.map((m) => Sprites.clone(Sprites.merc(m.look, 2, 0), 'mini'))),
          el('span', { class: 'tag tag-quest', text: `${mi.returnDay - s.day}일 후 귀환` })));
      });
      root.append(list);
    }
  }

  // ───────── 전직 창 ─────────
  function openPromote(mercId) {
    const s = Game.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m) return;
    const statName = { str: '힘', dex: '민첩', int: '지력', maxHp: '체력' };
    const choices = PROMOTIONS[m.cls].map((p) => el('div', { class: 'promo-card' },
      el('div', { class: 'portrait-wrap' }, Sprites.clone(Sprites.merc({ ...m.look, adv: p.key }, 4, 0), 'promo-portrait')),
      el('div', { class: 'name', text: p.name }),
      el('div', { class: 'skill adv', text: `스킬: ${p.skill}` }),
      el('div', { class: 'small', text: p.desc }),
      el('div', { class: 'small good', text: `즉시 ${Object.entries(p.bonus).map(([k, v]) => `${statName[k]}+${v}`).join(' ')}` }),
      el('button', {
        class: 'btn primary small', disabled: s.gold < PROMOTE_COST ? 'disabled' : null,
        onclick: () => { closeModal(); Game.promote(m.id, p.key); },
      }, icon('coin'), ` ${PROMOTE_COST} 전직`)));
    openModal(el('div', {},
      el('h2', {}, Sprites.clone(Sprites.merc(m.look, 2, 0), 'mini'), ` ${m.name}의 전직`),
      el('p', { class: 'muted small', text: `전직은 되돌릴 수 없습니다. 기존 스킬 「${CLASS_SKILLS[m.cls].name}」은 유지됩니다.` }),
      el('div', { class: 'promo-choices' }, choices),
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '취소', onclick: closeModal }))));
  }

  // ───────── 장비 창 ─────────
  function openEquip(mercId) {
    const s = Game.state;
    const m = s.mercs.find((x) => x.id === mercId);
    if (!m) return;
    const body = el('div', {},
      el('h2', {}, Sprites.clone(Sprites.merc(m.look, 2, 0), 'mini'), ` ${m.name}의 장비`),
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
        const diff = Object.keys(STAT_NAMES).map((k) => (it.bonus[k] || 0) - (cur && cur.bonus[k] ? cur.bonus[k] : 0));
        const diffText = Object.keys(STAT_NAMES).map((k, i) => (diff[i] ? `${STAT_NAMES[k]}${diff[i] > 0 ? '+' : ''}${diff[i]}` : null)).filter(Boolean).join(' ');
        body.append(el('div', { class: 'row item-row' },
          itemIcon(it.base, it.tier, 2),
          el('div', { class: 'grow' },
            el('div', { class: `item-name tier-text-${it.tier}`, text: it.name }),
            el('div', { class: 'small muted', text: bonusText(it.bonus) }),
            diffText ? el('div', { class: 'small diff', text: `변화: ${diffText}` }) : null),
          el('button', { class: 'btn small primary', text: '장착', onclick: () => { Game.equip(m.id, it.id); openEquip(m.id); } })));
      });
    });
    body.append(el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '닫기', onclick: closeModal })));
    openModal(body);
  }

  // ───────── 탭: 의뢰 게시판 ─────────
  function questCard(q) {
    const t = QUEST_TYPES[q.type];
    const s = Game.state;
    const idle = s.mercs.filter((m) => m.status === 'idle');
    const story = q.story ? HEROES[q.story.hero] : null;
    return el('div', { class: `card quest-card ${story ? 'story' : ''}` },
      story ? el('div', { class: 'story-banner' }, `★ ${story.name}의 이야기 ${q.story.ch + 1}장`) : null,
      el('div', { class: 'card-head' },
        el('div', { class: 'quest-icon' }, Sprites.clone(Sprites.monster(q.enemy, 3, 0), 'monster')),
        el('div', { class: 'card-title' },
          el('div', { class: 'name', text: q.title }),
          el('div', { class: 'sub' }, el('span', { class: `qtype q-${q.type}`, text: t.name }), ' ',
            el('span', { class: 'stars', title: `난이도 ${q.level}`, text: `★${q.level}` })),
          el('div', { class: 'small muted' }, icon('map', 1), ` ${REGIONS[q.region].name} · ${q.enemy}`))),
      el('div', { class: 'quest-info' },
        el('div', {}, icon('coin'), ` 보상 ${q.reward}`),
        el('div', {}, icon('star'), ` 명성 +${q.rep}`),
        el('div', { text: `권장 전투력 ${q.req}` }),
        el('div', { text: `소요 ${q.days}일 · 최대 ${q.maxParty}명` }),
        el('div', { class: 'muted', text: story ? '마감 없음' : `마감까지 ${q.expires - s.day}일` })),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted small', text: story ? `${story.name} 필수` : weightHint(q.type) }),
        el('button', { class: 'btn', text: '파견', disabled: idle.length ? null : 'disabled', onclick: () => openDispatch(q) })));
  }

  function weightHint(type) {
    const w = QUEST_TYPES[type].weights;
    const names = { str: '힘', dex: '민첩', int: '지력' };
    const best = Object.keys(names).sort((a, b) => w[b] - w[a])[0];
    return `${names[best]} 중시`;
  }

  function renderQuests(root) {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '의뢰 게시판' }),
      el('span', { class: 'muted', text: '매일 새 의뢰가 붙고, 마감이 지난 의뢰는 사라집니다.' })));
    if (!s.quests.length) root.append(el('p', { class: 'empty', text: '지금은 게시된 의뢰가 없습니다. 내일 다시 확인하세요.' }));
    const grid = el('div', { class: 'grid' });
    s.quests.forEach((q) => grid.append(questCard(q)));
    root.append(grid);
  }

  function chanceLabel(c) {
    if (c >= 0.9) return ['확실', 'c-great'];
    if (c >= 0.7) return ['안정', 'c-good'];
    if (c >= 0.5) return ['보통', 'c-mid'];
    if (c >= 0.3) return ['위험', 'c-bad'];
    return ['매우 위험', 'c-worst'];
  }

  function openDispatch(q) {
    const s = Game.state;
    const selected = new Set();
    const idle = s.mercs.filter((m) => m.status === 'idle')
      .sort((a, b) => Game.power(b, q.type) - Game.power(a, q.type));
    if (q.story) {
      const hero = idle.find((m) => m.hero === q.story.hero);
      if (hero) selected.add(hero.id);
    }
    const summary = el('div', { class: 'dispatch-summary' });
    const go = el('button', { class: 'btn primary', text: '출발!', disabled: 'disabled' });
    const list = el('div', { class: 'pick-list' });

    function refresh() {
      const party = [...selected].map((id) => s.mercs.find((m) => m.id === id));
      const pw = Game.partyPower(party, q.type);
      const c = Game.successChance(q, party);
      const [label, cls] = chanceLabel(c);
      const missingHero = Game.storyHeroMissing(q, party);
      const pairs = [];
      for (let i = 0; i < party.length; i++) for (let j = i + 1; j < party.length; j++) pairs.push([party[i], party[j]]);
      const friends = pairs.filter(([a, b]) => Game.rel(a, b) >= FRIEND_REL);
      const rivals = pairs.filter(([a, b]) => Game.rel(a, b) <= RIVAL_REL);
      const clashes = pairs.filter(([a, b]) => Game.traitsClash(a, b));
      const days = Game.questDays(q, party);
      const tired = party.filter((m) => m.fatigue >= 50);
      summary.replaceChildren(...[
        el('div', {}, `파티 전투력 `, el('b', { text: pw }), ` / 권장 ${q.req}`),
        el('div', { class: 'bar big' }, el('div', { class: 'bar-fill f-power', style: `width:${Math.min(100, (pw / q.req) * 50)}%` }), el('div', { class: 'bar-mark' })),
        party.length ? el('div', {}, '예상 성공률 ', el('b', { class: cls, text: `${Math.round(c * 100)}% (${label})` })) : el('div', { class: 'muted', text: '단원을 선택하세요.' }),
        party.some((m) => m.cls === 'cleric') ? el('div', { class: 'good small', text: '✚ 성직자 동행: 부상·사망 위험 감소' }) : null,
        party.some((m) => m.trait === 'saint') ? el('div', { class: 'good small', text: '✚ 성녀의 가호: 사망 위험 없음' }) : null,
        missingHero ? el('div', { class: 'bad small', text: `${HEROES[q.story.hero].name}이(가) 파티에 있어야 합니다.` }) : null,
        friends.length ? el('div', { class: 'good small', text: `♥ 전우 시너지: ${friends.map(([a, b]) => `${a.name}·${b.name}`).join(', ')}` }) : null,
        rivals.length ? el('div', { class: 'bad small', text: `✖ 불화: ${rivals.map(([a, b]) => `${a.name}·${b.name}`).join(', ')} (전투력 감소)` }) : null,
        clashes.length ? el('div', { class: 'muted small', text: `성격이 안 맞는 조합: ${clashes.map(([a, b]) => `${a.name}·${b.name}`).join(', ')} (관계 악화)` }) : null,
        tired.length ? el('div', { class: 'bad small', text: `피로한 단원: ${tired.map((m) => m.name).join(', ')} (전투력 감소, 부상 위험)` }) : null,
        party.length && days !== q.days ? el('div', { class: 'good small', text: `레인저의 길잡이: 소요 ${days}일` }) : null,
      ].filter(Boolean));
      go.disabled = !party.length || missingHero;
      list.querySelectorAll('.pick').forEach((row) => {
        const on = selected.has(Number(row.dataset.id));
        row.classList.toggle('on', on);
        row.classList.toggle('locked', !on && selected.size >= q.maxParty);
      });
    }

    idle.forEach((m) => {
      list.append(el('div', {
        class: `pick ${m.hero ? 'hero' : ''}`, 'data-id': m.id,
        onclick: () => {
          if (selected.has(m.id)) selected.delete(m.id);
          else if (selected.size < q.maxParty) selected.add(m.id);
          refresh();
        },
      },
      Sprites.clone(Sprites.merc(m.look, 2, 0), 'mini'),
      el('span', { class: 'grow' }, `${m.name} `, el('span', { class: 'muted', text: `${Game.className(m)} Lv.${m.level}` })),
      el('span', { class: `cond small ${Game.fatigueState(m).cls}`, title: `피로 ${m.fatigue}`, text: Game.fatigueState(m).label }),
      el('span', { class: `cond small ${Game.moraleState(m).cls}`, title: `사기 ${m.morale}`, text: Game.moraleState(m).label }),
      el('b', { class: 'power', text: Game.power(m, q.type) })));
    });
    if (!idle.length) list.append(el('div', { class: 'muted small', text: '대기 중인 단원이 없습니다.' }));

    go.addEventListener('click', () => { closeModal(); Game.dispatch(q.id, [...selected]); });
    openModal(el('div', {},
      el('h2', {}, Sprites.clone(Sprites.monster(q.enemy, 2, 0), 'mini'), ` ${q.title}`),
      el('p', { class: 'muted', text: `${REGIONS[q.region].name} · ${QUEST_TYPES[q.type].name} · ★${q.level} · ${q.days}일 · 최대 ${q.maxParty}명 · 보상 ${q.reward} 금화` }),
      list, summary,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '취소', onclick: closeModal }), go)));
    refresh();
  }

  // ───────── 탭: 지도 ─────────
  function renderMap(root) {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '대륙 지도' }),
      el('span', { class: 'muted', text: '지역을 눌러 정보를 확인하세요. 랭크가 오르면 새 지역이 열립니다.' })));
    const info = el('div', { class: 'region-info' });
    const fillInfo = (key) => {
      const r = REGIONS[key];
      const open = Game.regionUnlocked(key);
      const quests = s.quests.filter((q) => q.region === key);
      const away = s.missions.filter((mi) => mi.quest.region === key);
      let outpost = null;
      if (open && r.outpostCost) {
        outpost = s.outposts[key]
          ? el('div', { class: 'good small', text: '⚑ 전초기지 운영 중: 의뢰 증가, 이동 -1일, 보상 +15%' })
          : el('button', { class: 'btn small', disabled: s.gold < r.outpostCost ? 'disabled' : null, onclick: () => Game.buildOutpost(key) },
            '⚑ 전초기지 건설 ', icon('coin'), ` ${r.outpostCost}`);
      }
      info.replaceChildren(...[
        el('h3', { class: 'region-name', text: r.name }),
        el('p', { class: 'small', text: r.desc }),
        el('div', { class: 'small muted', text: open
          ? `의뢰 난이도 ★${r.levels[0]}~${r.levels[1]} · 추가 이동 ${r.travel}일`
          : `잠김 — ${RANKS[r.unlock].name}랭크 필요` }),
        el('div', { class: 'enemy-list' }, r.enemies.map((e) => el('div', { class: 'enemy' },
          Sprites.clone(Sprites.monster(e, 2, 0), 'mini'), el('span', { class: 'small', text: e })))),
        outpost,
        away.length ? el('div', { class: 'small', text: `이 지역에서 의뢰 수행 중: ${away.map((mi) => mi.quest.title).join(', ')}` }) : null,
        open ? el('h3', { text: `게시된 의뢰 (${quests.length})` }) : null,
        open ? el('div', { class: 'list' }, quests.length ? quests.map((q) => el('div', { class: 'row' },
          Sprites.clone(Sprites.monster(q.enemy, 2, 0), 'mini'),
          el('div', { class: 'grow' }, el('div', { text: q.title }), el('div', { class: 'small muted', text: `★${q.level} · 보상 ${q.reward} · ${q.days}일` })),
          el('button', { class: 'btn small', text: '파견', onclick: () => openDispatch(q) }))) : el('div', { class: 'muted small', text: '이 지역 의뢰가 없습니다.' })) : null,
      ].filter(Boolean));
    };
    const cvs = WorldMap.create((k) => fillInfo(k));
    fillInfo(WorldMap.selected);
    root.append(el('div', { class: 'map-layout' }, el('div', { class: 'map-wrap' }, cvs), info));
  }

  // ───────── 탭: 주점 ─────────
  function renderTavern(root) {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '주점 - 용병 지원자' }),
      el('div', { class: 'row-inline' },
        el('span', { class: 'muted', text: `매주 지원자가 바뀝니다 · 숙소 ${s.mercs.length}/${Game.capacity()}` }),
        el('button', { class: 'btn small', text: '지원자 새로 부르기 (30)', onclick: () => Game.refreshRecruits(true) }))));
    if (!s.recruits.length) root.append(el('p', { class: 'empty', text: '오늘은 지원자가 없습니다.' }));
    const grid = el('div', { class: 'grid' });
    s.recruits.forEach((m) => {
      const cost = Game.hireCost(m);
      const btn = el('button', {
        class: 'btn primary small', disabled: s.gold < cost ? 'disabled' : null, onclick: () => Game.hire(m.id),
      }, icon('coin'), ` ${cost} 고용`);
      const card = mercCard(m, { recruit: true, actions: [btn] });
      const desc = m.hero
        ? el('p', { class: 'small desc hero-desc', text: `특별 용병 · ${TRAITS[m.trait].name}: ${TRAITS[m.trait].desc}` })
        : el('p', { class: 'muted small desc', text: CLASSES[m.cls].desc });
      card.insertBefore(desc, card.querySelector('.stats'));
      grid.append(card);
    });
    root.append(grid);
  }

  // ───────── 탭: 상점 ─────────
  function itemRow(it, price, btnLabel, onClick, disabled) {
    return el('div', { class: `row item-row tier-${it.tier}` },
      el('div', { class: 'item-icon' }, itemIcon(it.base, it.tier, 3)),
      el('div', { class: 'grow' },
        el('div', { class: `item-name tier-text-${it.tier}`, text: it.name }),
        el('div', { class: 'small' }, el('span', { class: 'muted', text: `${SLOT_NAMES[it.slot]} · ` }), bonusText(it.bonus))),
      el('button', { class: 'btn small', disabled: disabled ? 'disabled' : null, onclick: onClick }, icon('coin'), ` ${price} ${btnLabel}`));
  }

  function renderShop(root) {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '상점' }),
      el('span', { class: 'muted', text: `매주 새 물건이 들어옵니다 · 최대 ${TIERS[Game.shopMaxTier()].name} 등급` })));
    root.append(el('div', { class: 'list' },
      el('div', { class: 'row item-row' },
        el('div', { class: 'item-icon' }, itemIcon('herb', 0, 3)),
        el('div', { class: 'grow' }, el('div', { class: 'item-name', text: '치료 약초' }),
          el('div', { class: 'small muted', text: `부상 3일 즉시 회복 · 보유 ${s.herbs}개` })),
        el('button', { class: 'btn small', disabled: s.gold < HERB_PRICE ? 'disabled' : null, onclick: () => Game.buyHerb() }, icon('coin'), ` ${HERB_PRICE} 구입`))));
    root.append(el('h2', { class: 'mt', text: '진열대' }));
    const shop = el('div', { class: 'list' });
    if (!s.shop.length) shop.append(el('p', { class: 'empty', text: '모두 팔렸습니다. 다음 주를 기다리세요.' }));
    s.shop.forEach((it) => {
      const price = Game.shopPrice(it);
      shop.append(itemRow(it, price, '구입', () => Game.buy(it.id), s.gold < price));
    });
    root.append(shop);
    root.append(el('h2', { class: 'mt', text: `창고 (${s.inventory.length})` }));
    const inv = el('div', { class: 'list' });
    if (!s.inventory.length) inv.append(el('p', { class: 'empty', text: '창고가 비어 있습니다.' }));
    s.inventory.forEach((it) => {
      inv.append(itemRow(it, Game.sellPrice(it), '판매', () => confirmBox(`${it.name}을(를) ${Game.sellPrice(it)} 금화에 팔까요?`, () => Game.sell(it.id))));
    });
    root.append(inv);
    root.append(el('p', { class: 'muted small', text: '장비는 용병단 탭에서 각 단원의 「장비」 버튼으로 장착합니다.' }));
  }

  // ───────── 탭: 시설 ─────────
  function renderFacilities(root) {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' }, el('h2', { text: '길드 시설' }),
      el('span', { class: 'muted', text: '시설을 증축해 용병단을 키우세요.' })));
    const list = el('div', { class: 'list' });
    Object.entries(FACILITIES).forEach(([key, f]) => {
      const lv = s.facilities[key];
      const maxed = lv >= f.max;
      const cost = Game.facilityCost(key);
      list.append(el('div', { class: 'row facility' },
        icon('house', 3),
        el('div', { class: 'grow' },
          el('div', { class: 'name' }, `${f.name} `, el('span', { class: 'lv', text: `${lv}/${f.max}단계` })),
          el('div', { class: 'pips' }, Array.from({ length: f.max }, (_, i) => el('span', { class: i < lv ? 'pip on' : 'pip' }))),
          el('div', { class: 'muted small', text: `현재: ${f.desc(lv)}` }),
          maxed ? null : el('div', { class: 'good small', text: `다음: ${f.desc(lv + 1)}` })),
        maxed ? el('span', { class: 'tag tag-idle', text: '최대' })
          : el('button', { class: 'btn small', disabled: s.gold < cost ? 'disabled' : null, onclick: () => Game.upgrade(key) }, icon('coin'), ` ${cost}`)));
    });
    root.append(list);

    const st = s.stats;
    root.append(el('h2', { class: 'mt', text: '용병단 기록' }),
      el('div', { class: 'list' },
        el('div', { class: 'row' }, `완수한 의뢰: ${st.completed} · 실패한 의뢰: ${st.failed} · 전사자: ${st.fallen}`)));
  }

  // ───────── 탭: 기록 ─────────
  function renderLog(root) {
    root.append(el('h2', { text: '용병단 일지' }));
    const list = el('div', { class: 'log' });
    Game.state.log.forEach((l) => list.append(el('div', { class: `log-line ${l.kind}` },
      el('span', { class: 'log-day', text: `${l.day}일차` }), l.text)));
    root.append(list);
  }

  // ───────── 공통 ─────────
  function renderTop() {
    const s = Game.state;
    const rank = Game.rank(), next = Game.nextRank();
    $('#guild-name').textContent = s.guildName;
    $('#day').textContent = `${s.day}일차 (${['월', '화', '수', '목', '금', '토', '일'][(s.day - 1) % 7]})`;
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
      if (badge) {
        const n = { quests: s.quests.length, tavern: s.recruits.length, shop: s.shop.length }[b.dataset.tab];
        badge.textContent = n || '';
        badge.classList.toggle('star', (b.dataset.tab === 'quests' && s.quests.some((q) => q.story)) || (b.dataset.tab === 'tavern' && s.recruits.some((r) => r.hero)));
      }
    });
    $('#next-day').disabled = !!s.over;
  }

  function render() {
    if (!Game.state) return;
    renderTop();
    const root = $('#panel');
    const scroll = root.scrollTop;
    root.replaceChildren();
    ({ roster: renderRoster, quests: renderQuests, map: renderMap, tavern: renderTavern, shop: renderShop, facilities: renderFacilities, log: renderLog })[tab](root);
    root.scrollTop = scroll;
    showReports();
  }

  // 보고서(전투 → 결과, 대화, 특별 이벤트)를 하나씩 띄운다
  function showReports() {
    const s = Game.state;
    if (modalOpen || !s.pendingReports.length) return;
    const r = s.pendingReports.shift();
    Game.save();
    if (r.special === 'dialog') return openDialog(r);
    if (r.special) return openModal(specialReport(r), true);
    if (s.settings.battle) {
      openModal(Battle.play(r, () => openModal(missionReport(r), true)), true);
    } else {
      openModal(missionReport(r), true);
    }
  }

  function missionReport(r) {
    const titles = { great: '대성공!', success: '의뢰 성공', fail: '의뢰 실패', disaster: '대실패...' };
    const good = r.outcome === 'great' || r.outcome === 'success';
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
    return el('div', { class: 'report' },
      el('div', { class: `report-banner ${good ? 'good' : 'bad'} ${r.outcome}`, text: titles[r.outcome] }),
      el('h3', { text: r.quest.title }),
      members,
      el('div', { class: 'report-rewards' },
        el('span', {}, icon('coin'), ` ${r.gold >= 0 ? '+' : ''}${r.gold}`),
        el('span', {}, icon('star'), ` ${r.rep >= 0 ? '+' : ''}${r.rep}`)),
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: closeModal })));
  }

  // 특별 용병 대화 (한 줄씩 타자기 효과)
  function openDialog(r) {
    const h = HEROES[r.hero];
    const look = { cls: h.cls, ...h.look };
    let line = 0, timer = null, typing = false;
    const speaker = el('div', { class: 'dialog-speaker' });
    const text = el('div', { class: 'dialog-text' });
    const next = el('button', { class: 'btn primary' });
    const footer = el('div', { class: 'dialog-foot small' });

    function show() {
      const [who, msg] = r.lines[line];
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
      }, 28);
      const last = line === r.lines.length - 1;
      next.textContent = last ? '확인' : '다음 ▶';
      footer.textContent = last && r.foot ? r.foot : '';
    }
    const advance = () => {
      if (typing) { clearInterval(timer); typing = false; text.textContent = r.lines[line][1]; return; }
      if (line < r.lines.length - 1) { line++; show(); } else { clearInterval(timer); closeModal(); }
    };
    next.addEventListener('click', advance);
    openModal(el('div', { class: 'dialog' },
      el('div', { class: 'dialog-title', text: r.title }),
      el('div', { class: 'dialog-body', onclick: (e) => { if (e.target !== next) advance(); } },
        el('div', { class: 'dialog-portrait' }, Sprites.clone(Sprites.merc(look, 5, 0), 'big-portrait')),
        el('div', { class: 'dialog-box' }, speaker, text)),
      footer,
      el('div', { class: 'modal-actions' }, next)), true);
    show();
  }

  function specialReport(r) {
    const s = Game.state;
    const restart = el('button', { class: 'btn primary', text: '새 게임', onclick: () => { closeModal(); Game.clearSave(); Game.newGame(); Game.emit(); } });
    if (r.special === 'win') {
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: 'S랭크 달성!' }),
        el('p', { text: `${s.day}일 만에 ${s.guildName}이(가) 대륙 최고의 용병단이 되었습니다!` }),
        el('p', { class: 'muted', text: `완수 ${s.stats.completed} · 실패 ${s.stats.failed} · 전사 ${s.stats.fallen}` }),
        el('p', { class: 'muted small', text: '계속 플레이하며 남은 이야기를 마저 볼 수도 있습니다.' }),
        el('div', { class: 'modal-actions' }, restart, el('button', { class: 'btn', text: '계속하기', onclick: closeModal })));
    }
    const msg = r.special === 'bankrupt' ? '빚더미에 올라앉은 용병단은 결국 해산되었습니다...' : '모든 단원을 잃고 재기할 자금도 없습니다...';
    return el('div', { class: 'report' },
      el('div', { class: 'report-banner bad disaster', text: '게임 오버' }),
      el('p', { text: msg }),
      el('p', { class: 'muted', text: `${s.day}일 동안 버텼습니다. 최고 명성 ${s.rep}` }),
      el('div', { class: 'modal-actions' }, restart));
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
        el('button', { class: 'btn danger', text: '확인', onclick: () => { modalOpen = false; $('#modal').classList.add('hidden'); onYes(); } }))));
  }

  let toastTimer;
  function toast(msg) {
    const t = $('#toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 1800);
  }

  function init() {
    document.querySelectorAll('.tab').forEach((b) => b.addEventListener('click', () => { tab = b.dataset.tab; $('#panel').scrollTop = 0; render(); }));
    $('#next-day').addEventListener('click', () => { if (!modalOpen) Game.nextDay(); });
    $('#menu-btn').addEventListener('click', openMenu);
    $('#modal').addEventListener('click', (e) => {
      if (e.target.id === 'modal' && !$('#modal').dataset.sticky) closeModal();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modalOpen && !$('#modal').dataset.sticky) closeModal();
      if (e.key === ' ' && !modalOpen && e.target === document.body) { e.preventDefault(); Game.nextDay(); }
    });
    // 아이콘 장식
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
      el('label', { class: 'small muted', text: '용병단 이름' }),
      el('div', { class: 'row-inline' }, nameInput,
        el('button', { class: 'btn small', text: '변경', onclick: () => {
          const v = nameInput.value.trim();
          if (v) { s.guildName = v; Game.save(); toast('이름을 바꿨습니다.'); renderTop(); }
        } })),
      el('label', { class: 'row-inline option', for: 'opt-battle' }, battleToggle, '의뢰 결과 전투 연출 보기'),
      el('div', { class: 'help' },
        el('h3', { text: '플레이 방법' }),
        el('ul', {},
          el('li', { text: '의뢰 게시판에서 의뢰를 골라 단원을 파견하세요. 의뢰 유형마다 중요한 능력치가 다릅니다.' }),
          el('li', { text: '성공하면 금화와 명성을, 실패하면 부상이나 최악의 경우 단원을 잃습니다.' }),
          el('li', { text: '상점에서 장비를 사서 단원에게 장착하면 능력치가 오릅니다.' }),
          el('li', { text: '랭크가 오르면 지도에 새 지역이 열리고, 특별 용병이 주점에 찾아옵니다. 함께 의뢰를 완수하면 그들의 이야기가 펼쳐집니다.' }),
          el('li', { text: '7일마다 주급을 지급합니다. 금화가 모자라면 단원이 떠나고, 빚이 -200을 넘으면 파산합니다.' }),
          el('li', { text: '스페이스바로 다음 날로 넘어갈 수 있습니다. 게임은 매일 자동 저장됩니다.' }))),
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn danger', text: '새 게임', onclick: () => confirmBox('정말 처음부터 다시 시작할까요? 저장된 진행이 지워집니다.', () => { Game.clearSave(); Game.newGame(); Game.emit(); }) }),
        el('button', { class: 'btn primary', text: '닫기', onclick: closeModal }))));
  }

  return { init, render, toast };
})();
