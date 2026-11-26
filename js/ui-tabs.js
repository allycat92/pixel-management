// 탭 화면: 용병단, 의뢰(+파견 창), 지도, 세력, 모집소, 상점, 시설, 일지
'use strict';

(() => {
  const { el, icon, itemIcon, mini, bonusText, signed, companyFlag, factionFlag, factionTag, condTags, mercCard } = UI.h;
  const T = UI.tabs;

  // ───────── 용병단 ─────────
  function memberRow(m, c) {
    const cap = Game.isCaptain(m);
    return el('div', { class: `mrow ${m.status} ${cap ? 'captain-row' : ''}`, onclick: () => UI.openMerc(m.id) },
      mini(m.look),
      el('div', { class: 'grow' },
        el('div', { class: 'mname' }, cap ? el('span', { class: 'crown', title: '용병대장', text: '♛' }) : null, m.name,
          el('span', { class: 'lv', text: ` Lv.${m.level}` }), m.hero ? el('span', { class: 'hero-mark', text: ' ★' }) : null),
        el('div', { class: 'small muted' }, cap
          ? `${Game.className(m)} · 지휘 「${Game.leadOf(m).name}」${m.trait !== 'none' ? ` · ${TRAITS[m.trait].name}` : ''}`
          : `${Game.className(m)} (${m.hcls ? `특별 · 이야기 ${Game.heroCh(m)}장` : UNIT_TIERS[Game.classTier(m)].name})${m.trait !== 'none' ? ` · ${TRAITS[m.trait].name}` : ''}`)),
      el('div', { class: 'mtags' },
        m.status === 'injured' ? el('span', { class: 'tag tag-injured', text: `부상 ${Math.ceil(m.injury)}일` }) : null,
        m.status === 'quest' ? el('span', { class: 'tag tag-quest', text: '출격' }) : null,
        (Game.canPromote(m) || Game.canMaster(m)) && m.status !== 'quest' ? el('span', { class: 'tag tag-promo', text: Game.canMaster(m) ? '최상급 전직 가능' : '전직 가능' })
          : !cap && Game.atCap(m) && (m.hcls ? Game.heroCh(m) < 3 : Game.classTier(m) < 2) ? el('span', { class: 'tag tag-promo', text: m.hcls ? '상한 — 이야기 필요' : '상한 도달' }) : null,
        ...condTags(m)));
  }

  function ownCompanyPanel(c) {
    const s = Game.state;
    const leader = Game.leader(c);
    const units = Game.unitsOf(c);
    const ms = leader ? [leader, ...units] : units;
    const mi = c.missionId && s.missions.find((x) => x.id === c.missionId);
    return el('div', { class: 'company-panel', style: `--cc:${c.color}` },
      el('div', { class: 'company-head' },
        companyFlag(c, 3),
        el('div', { class: 'grow' },
          el('div', { class: 'cname', text: c.name }),
          el('div', { class: `small ${leader ? 'muted' : 'bad'}`, text: `${leader ? `대장 ${leader.name}(${Game.className(leader)})` : '대장 없음 (전투력 -15%)'} · 대원 ${units.length}/${Game.unitSlots()}${Game.unitSlots() < 3 ? '(병영 1단계부터 3명)' : ''} · 전적 ${c.wins}승 ${c.losses}패 · 기본 전투력 ${ms.length ? Game.ownCompanyPower(c, ms, null) : 0}` }),
          leader ? el('div', { class: 'small lead-line', title: Game.leadOf(leader).desc }, '지휘 ', el('b', { text: `「${Game.leadOf(leader).name}」` }), ` ${Game.leadOf(leader).desc}${Game.leadScale(leader) > 1 ? ' (×1.5)' : ''}`) : null,
          el('div', { class: 'cohesion' }, el('span', { class: 'small muted', text: '결속도' }),
            el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-cohesion', style: `width:${c.cohesion}%` })),
            el('span', { class: 'small', text: c.cohesion }))),
        el('div', { class: 'company-status' },
          mi ? el('span', { class: 'tag tag-quest', text: `출격 중 · ${mi.returnDay - s.day}일 후 귀환` }) : el('span', { class: 'tag tag-idle', text: '대기' }),
          mi ? el('div', { class: 'small muted', text: mi.contract.title }) : null)),
      el('div', { class: 'members' }, ms.length ? ms.map((m) => memberRow(m, c)) : el('div', { class: 'muted small pad', text: '단원이 없습니다. 예비 인원 중 용병대장 1명과 대원을 배속하세요.' })),
      el('div', { class: 'company-foot' },
        el('button', { class: 'btn small', text: '이름 변경', onclick: () => renameCompany(c) }),
        el('button', { class: 'btn small danger', text: '해산', disabled: c.missionId ? 'disabled' : null,
          onclick: () => UI.confirmBox(`「${c.name}」을(를) 해산할까요? 단원들은 예비 인원이 됩니다.`, () => Game.disbandCompany(c.id)) })));
  }

  function renameCompany(c) {
    const input = el('input', { class: 'input', value: c.name, maxlength: 14 });
    UI.openModal(el('div', {},
      el('h2', { text: '용병단 이름 변경' }), input,
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn', text: '취소', onclick: UI.closeModal }),
        el('button', { class: 'btn primary', text: '변경', onclick: () => { Game.renameCompany(c.id, input.value.trim()); UI.closeModal(); } }))));
  }

  function extCompanyPanel(c, market) {
    const s = Game.state;
    const mi = c.missionId && s.missions.find((x) => x.id === c.missionId);
    const left = c.contractEnd - s.day;
    return el('div', { class: `company-panel ext ${market ? 'market' : ''}`, style: `--cc:${c.color}` },
      el('div', { class: 'company-head' },
        el('div', { class: 'portrait-wrap' }, Sprites.clone(Sprites.merc(c.captain.look, 3, 0), 'portrait')),
        el('div', { class: 'grow' },
          el('div', { class: 'cname' }, companyFlag(c, 1), ` ${c.name}`),
          el('div', { class: 'small muted', text: `단장 ${c.captain.name}${c.captain.cap ? `(${CAPTAIN_CLASSES[c.captain.cap].name})` : ""} · Lv.${c.level} · ${c.size}/${c.maxSize}명 · 기본 전투력 ${Game.extPower(c, null)}` }),
          el('div', { class: 'small' },
            el('span', { class: 'chip', text: `특기: ${QUEST_TYPES[c.specialty].name}` }), ' ',
            el('span', { class: 'chip', title: DISPOSITIONS[c.disposition].desc, text: `성향: ${DISPOSITIONS[c.disposition].name}` }), ' ',
            c.sympathy ? el('span', { class: 'chip' }, factionFlag(c.sympathy, 1), ` ${FACTIONS[c.sympathy].short} 동조`) : null),
          market ? null : el('div', { class: 'cohesion' }, el('span', { class: 'small muted', text: '충성도' }),
            el('div', { class: 'bar thin' }, el('div', { class: `bar-fill ${c.loyalty < 30 ? 'f-worst' : 'f-loyal'}`, style: `width:${c.loyalty}%` })),
            el('span', { class: 'small', text: c.loyalty }))),
        el('div', { class: 'company-status' },
          market ? null : mi ? el('span', { class: 'tag tag-quest', text: `출격 중 · ${mi.returnDay - s.day}일` }) : el('span', { class: 'tag tag-idle', text: '대기' }),
          market ? null : el('div', { class: `small ${left <= 7 ? 'bad' : 'muted'}`, text: `계약 ${Math.max(0, left)}일 남음` }))),
      el('div', { class: 'small muted pad', text: `보상 몫 ${c.share}% · 주간 유지비 ${c.upkeep}${market ? ` · 계약금 ${c.signFee}` : ''} · 전적 ${c.wins}승 ${c.losses}패` }),
      el('div', { class: 'company-foot' }, market
        ? el('button', { class: 'btn primary small', disabled: s.gold < c.signFee ? 'disabled' : null, onclick: () => Game.contractCompany(c.id) }, icon('coin'), ` ${c.signFee} 4주 계약`)
        : [
          el('button', { class: 'btn small', disabled: c.loyalty < 30 || s.gold < Game.renewCost(c) ? 'disabled' : null, onclick: () => Game.renewCompany(c.id) }, icon('coin'), ` ${Game.renewCost(c)} 재계약 (+4주)`),
          el('button', { class: 'btn small danger', text: '계약 해지', disabled: c.missionId ? 'disabled' : null,
            onclick: () => UI.confirmBox(`「${c.name}」과(와)의 계약을 해지할까요? 계약금은 돌려받지 못합니다.`, () => Game.releaseCompany(c.id, '계약 해지로 떠났습니다.')) }),
        ]));
  }

  T.companies = (root) => {
    const s = Game.state;
    const own = Game.ownCompanies(), ext = Game.extCompanies(), reserve = Game.reserve();
    const feast = el('button', { class: 'btn small', disabled: Game.feastReady() && s.gold >= Game.feastCost() ? null : 'disabled',
      title: '길드에 있는 단원 사기 +15, 피로 -15, 서로 친밀도 상승 (주 1회)', onclick: () => Game.feast() },
    Game.feastReady() ? `연회 열기 (${Game.feastCost()})` : `연회 (${7 - (s.day - s.lastFeast)}일 후)`);
    const create = el('button', { class: 'btn small primary', disabled: own.length >= Game.maxCompanies() || s.gold < Game.companyCost() ? 'disabled' : null,
      title: own.length >= Game.maxCompanies() ? '병영을 증축하면 더 만들 수 있습니다' : '', onclick: () => Game.createCompany() },
    `용병단 창설 (${Game.companyCost()})`);
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: `직속 용병단 (${own.length}/${Game.maxCompanies()})` }),
      el('div', { class: 'row-inline' },
        el('span', { class: 'muted small', text: `단원 ${s.mercs.length}/${Game.capacity()} · 주급 ${Game.weeklyWageTotal()} · 유지비 ${Game.weeklyUpkeepTotal()} · 약초 ${s.herbs}` }),
        feast, create)));
    const grid = el('div', { class: 'company-grid' });
    own.forEach((c) => grid.append(ownCompanyPanel(c)));
    root.append(grid);

    root.append(el('h2', { class: 'mt', text: `예비 인원 (${reserve.length})` }));
    root.append(reserve.length
      ? el('div', { class: 'members reserve' }, reserve.map((m) => el('div', { class: 'reserve-item' }, memberRow(m, null),
        el('button', { class: 'btn small', text: '배속', disabled: m.status === 'quest' ? 'disabled' : null,
          onclick: (e) => { e.stopPropagation(); quickAssign(m); } }))))
      : el('p', { class: 'muted small', text: '모집소에서 고용한 단원은 여기서 대기합니다. 용병단에 배속해야 출격할 수 있습니다.' }));

    root.append(el('h2', { class: 'mt', text: `외부 계약 용병단 (${ext.length})` }));
    root.append(ext.length ? el('div', { class: 'company-grid' }, ext.map((c) => extCompanyPanel(c))) :
      el('p', { class: 'muted small', text: '모집소의 용병단 시장에서 외부 용병단과 계약할 수 있습니다.' }));
  };

  function quickAssign(m) {
    const open = Game.ownCompanies().filter((c) => !c.missionId && !Game.slotProblem(m, c));
    if (open.length === 1) Game.assign(m.id, open[0].id);
    else if (!open.length) UI.toast(Game.isCaptain(m) ? '대장 자리가 빈 용병단이 없습니다. 용병단을 새로 창설하세요.' : '대원 자리가 빈 대기 중인 용병단이 없습니다.');
    else UI.openMerc(m.id);
  }

  // ───────── 의뢰 ─────────
  // 결전의 판돈: 패권국 수도는 지금 장악도가 40 초과면 이기거나(공략) 져도(방어) 장악도만 -40 (실제 판정과 같은 규칙)
  function campaignStakes(c) {
    const name = PROVINCES[c.province].name;
    const attack = c.campaign.side === 'attack';
    const [verb, fall] = attack ? ['승리 시', '점령'] : ['패배 시', '함락'];
    if (Game.capitalHolds(c.province, attack ? c.issuer : c.target)) return `${verb} ${name} 장악도 -${CAPITAL_FALL_AT} · 수도 유지 (${CAPITAL_FALL_AT} 이하에서 ${fall})`;
    return `${verb} ${name} ${fall}`;
  }
  function effectPreview(c) {
    const kind = c.cat === 'monster' ? 'monster' : c.type;
    const eff = CONTRACT_EFFECTS[kind].win;
    const parts = [];
    if (eff.issuer && !FACTIONS[c.issuer].neutral) parts.push(el('span', { class: 'chip good' }, factionFlag(c.issuer, 1), ` ${FACTIONS[c.issuer].short} ${signed(eff.issuer)}`));
    if (eff.target && c.target) parts.push(el('span', { class: 'chip bad' }, factionFlag(c.target, 1), ` ${FACTIONS[c.target].short} ${signed(eff.target)}`));
    if (c.final) parts.push(el('span', { class: 'chip warn', text: `승리 시 ${FACTIONS[c.target].leader} 토벌 — 재앙 종식` }));
    else if (c.type === 'battle' && c.campaign) parts.push(el('span', { class: 'chip warn', text: campaignStakes(c) }));
    else if (eff.control) parts.push(el('span', { class: 'chip', text: `장악도 ${signed(eff.control)}` }));
    if (eff.relation) parts.push(el('span', { class: 'chip good', text: '양 세력 관계 개선' }));
    if (c.type === 'sabotage') parts.push(el('span', { class: 'chip warn', text: '정체 노출 위험' }));
    return el('div', { class: 'chips' }, parts);
  }

  function contractCard(c) {
    const s = Game.state;
    const t = QUEST_TYPES[c.type];
    const story = c.story ? HEROES[c.story.hero] : null;
    const free = s.companies.some((co) => !co.missionId);
    const visual = c.enemy
      ? Sprites.clone(Sprites.monster(c.enemy, 3, 0), 'monster')
      : Sprites.clone(Sprites.merc(UI.h.soldierLook(c.target || c.issuer, c.id), 3, 0, true), 'monster');
    const banner = c.final ? el('div', { class: 'story-banner final-banner' }, `☠ 최종 결전 · 용병단 ${c.campaign.slots}개 투입 · ${FACTIONS[c.target].name}`)
      : c.campaign ? el('div', { class: 'story-banner campaign-banner' }, `⚔ 대규모 결전 · 용병단 ${c.campaign.slots}개 투입 · ${c.campaign.side === 'attack' ? '공격측' : '방어측'}`)
      : story ? el('div', { class: 'story-banner' }, `★ ${story.name}의 이야기 ${c.story.ch + 1}장`)
      : c.capStory ? el('div', { class: 'story-banner captain-banner' }, `♛ 대장 영입 · ${CAPTAINS[c.capStory.key].name} ${c.capStory.ch + 1}/${CAPTAINS[c.capStory.key].chapters.length}장`)
        : c.boss ? el('div', { class: 'story-banner boss-banner' }, `☠ 재앙 · ${BOSSES[c.boss].name}`) : null;
    return el('div', { class: `card quest-card cat-${c.cat} ${story ? 'story' : ''} ${c.boss ? 'boss' : ''} ${c.campaign ? 'campaign' : ''} ${c.final ? 'final' : ''}` },
      banner,
      el('div', { class: 'card-head' },
        el('div', { class: 'quest-icon' }, visual),
        el('div', { class: 'card-title' },
          el('div', { class: 'name', text: c.title }),
          el('div', { class: 'sub' }, el('span', { class: `qtype q-${c.type}`, text: t.name }), ' ',
            el('span', { class: 'stars', title: `난이도 ${c.level}`, text: `★${c.level}` })),
          el('div', { class: 'small muted' }, `${PROVINCES[c.province].name}`))),
      el('div', { class: 'parties' },
        el('span', { class: 'small muted', text: '의뢰주' }), factionTag(c.issuer),
        c.target ? el('span', { class: 'small muted', text: 'vs' }) : null, c.target ? factionTag(c.target) : null,
        c.enemy ? el('span', { class: 'small muted', text: `· ${c.enemy}` }) : null),
      el('div', { class: 'quest-info' },
        el('div', { class: c.war ? 'war-gold' : '' }, icon('coin'), ` 보상 ${c.reward}`, c.war ? el('span', { class: 'chip war', text: '전쟁' }) : null),
        el('div', {}, icon('star'), ` 명성 +${c.rep}`),
        el('div', { text: `권장 전투력 ${Game.effectiveReq(c)}` }),
        el('div', { text: `권장 ${c.size}명 · ${c.days}일` }),
        el('div', { class: 'muted', text: story || c.boss || c.capStory ? '마감 없음' : `마감까지 ${c.expires - s.day}일` })),
      effectPreview(c),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted small', text: story ? `${story.name} 필수` : weightHint(c.type) }),
        el('button', { class: 'btn', text: '파견', 'data-fkey': `dispatch-${c.id}`, disabled: free ? null : 'disabled', onclick: () => openDispatch(c) })));
  }

  function weightHint(type) {
    const w = QUEST_TYPES[type].weights;
    const names = { str: '힘', dex: '민첩', int: '지력' };
    return `${names[Object.keys(names).sort((a, b) => w[b] - w[a])[0]]} 중시`;
  }

  T.contracts = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '의뢰' }),
      el('span', { class: 'muted small', text: '금화는 전쟁 의뢰에서 나옵니다. 괴물·치안 의뢰는 보수가 적은 대신 명성과 경험을 쌓기 좋습니다.' })));
    const groups = [
      ['특별', s.contracts.filter((c) => c.campaign || c.story || c.boss || c.capStory)],
      ['세력 분쟁', s.contracts.filter((c) => !c.campaign && !c.story && !c.boss && !c.capStory && c.cat !== 'monster')],
      ['괴물·치안', s.contracts.filter((c) => !c.campaign && !c.story && !c.boss && !c.capStory && c.cat === 'monster')],
    ];
    if (!s.contracts.length) root.append(el('p', { class: 'empty', text: '지금은 의뢰가 없습니다. 내일 다시 확인하세요.' }));
    groups.forEach(([name, list]) => {
      if (!list.length) return;
      root.append(el('h3', { class: 'group-title', text: `${name} (${list.length})` }));
      root.append(el('div', { class: 'grid' }, list.map(contractCard)));
    });
    const missions = s.missions;
    if (missions.length) {
      root.append(el('h3', { class: 'group-title', text: `진행 중 (${missions.length})` }));
      root.append(el('div', { class: 'list' }, missions.map((mi) => el('div', { class: 'row' },
        mi.units.map((u) => { const co = Game.company(u.companyId); return co ? companyFlag(co) : null; }),
        el('div', { class: 'grow' }, el('div', { text: mi.contract.title }), el('div', { class: 'small muted', text: PROVINCES[mi.contract.province].name })),
        el('span', { class: 'tag tag-quest', text: `${mi.returnDay - s.day}일 후 귀환` })))));
    }
  };

  function chanceLabel(c) {
    if (c >= 0.9) return ['확실', 'c-great'];
    if (c >= 0.7) return ['안정', 'c-good'];
    if (c >= 0.5) return ['보통', 'c-mid'];
    if (c >= 0.3) return ['위험', 'c-bad'];
    return ['매우 위험', 'c-worst'];
  }

  // 파견 창: 용병단 고르기 (결전이면 여러 개), 직속 용병단은 출격 단원 고르기
  function openDispatch(c) {
    const s = Game.state;
    const slots = Game.dispatchSlots(c); // 일반 의뢰 1개, 결전 2~3개 (직속·외부 합쳐 최대 MAX_DISPATCH)
    const sel = new Map(); // companyId -> Set(memberIds) | true
    const comps = s.companies.filter((co) => !co.missionId);
    const defaultMembers = (co) => new Set(Game.availableMembers(co).filter((m) => m.fatigue < 80).map((m) => m.id));
    // 이야기 의뢰: 특별 용병이 있는 용병단을 자동 선택
    if (c.story) {
      const co = comps.find((x) => x.own && Game.availableMembers(x).some((m) => m.hero === c.story.hero));
      if (co) sel.set(co.id, defaultMembers(co));
    }
    const listBox = el('div', { class: 'pick-list' });
    const memberBox = el('div', {});
    const summary = el('div', { class: 'dispatch-summary' });
    const go = el('button', { class: 'btn primary', text: '출격!' });

    const units = () => [...sel.entries()].map(([id, v]) => (v === true ? { companyId: id } : { companyId: id, memberIds: [...v] }))
      .filter((u) => !u.memberIds || u.memberIds.length);

    function toggle(co) {
      if (sel.has(co.id)) sel.delete(co.id);
      else {
        if (slots === 1) sel.clear();
        if (sel.size >= slots) return UI.toast(`이 의뢰에는 용병단을 ${slots}개까지만 보낼 수 있습니다. 다른 용병단을 먼저 빼세요.`);
        sel.set(co.id, co.own ? defaultMembers(co) : true);
      }
      refresh();
    }

    // 키보드: 하나만 고르는 의뢰는 라디오 묶음(화살표로 이동·선택), 여러 개면 체크박스. Space/Enter 로 켜고 끈다.
    const single = slots === 1;
    listBox.setAttribute('role', single ? 'radiogroup' : 'group');
    listBox.setAttribute('aria-label', single ? '보낼 용병단 (하나)' : `보낼 용병단 (최대 ${slots}개)`);
    const lockedOf = (co) => !!((!co.own && Game.extRefusal(co, c)) || (co.own && !Game.availableMembers(co).length));
    const focusKey = (key) => { const t = document.querySelector(`.dispatch [data-fkey="${key}"]`); if (t) t.focus(); };
    function pickKey(e, co) {
      // 라디오는 키보드로 해제되지 않는다 (이미 고른 것은 그대로). 체크박스는 켜고 끈다. 마우스 클릭은 그대로 토글.
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); if (!lockedOf(co) && !(single && sel.has(co.id))) { toggle(co); focusKey(`co-${co.id}`); } return; }
      if (!single) return;
      const dir = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      const open = comps.filter((x) => !lockedOf(x));
      if (!open.length || (!dir && e.key !== 'Home' && e.key !== 'End')) return;
      e.preventDefault();
      const i = open.indexOf(co);
      const target = e.key === 'Home' ? open[0] : e.key === 'End' ? open[open.length - 1] : open[((i < 0 ? 0 : i) + dir + open.length) % open.length];
      if (!sel.has(target.id)) toggle(target);
      focusKey(`co-${target.id}`);
    }

    function refresh() {
      const active = document.activeElement;
      const keep = active && active.closest && active.closest('.dispatch') && active.dataset.fkey;
      // 라디오 묶음은 Tab 정지점이 하나: 고른 것, 없으면 첫 번째로 고를 수 있는 것
      const tabStop = single ? (comps.find((co) => sel.has(co.id) && !lockedOf(co)) || comps.find((co) => !lockedOf(co))) : null;
      listBox.replaceChildren(...comps.map((co) => {
        const refusal = !co.own && Game.extRefusal(co, c);
        const avail = co.own ? Game.availableMembers(co) : null;
        const disabled = refusal || (co.own && !avail.length);
        const on = sel.has(co.id);
        const u = co.own ? { companyId: co.id, memberIds: [...(on ? sel.get(co.id) : defaultMembers(co))] } : { companyId: co.id };
        return el('div', { class: `pick ${on ? 'on' : ''} ${disabled ? 'locked' : ''}`,
          role: single ? 'radio' : 'checkbox', 'aria-checked': on ? 'true' : 'false', 'aria-disabled': disabled ? 'true' : null,
          tabindex: disabled ? '-1' : single ? (co === tabStop ? '0' : '-1') : '0',
          'data-fkey': `co-${co.id}`, 'data-autofocus': co === tabStop || (!single && !disabled && co === comps.find((x) => !lockedOf(x))) ? '' : null,
          onkeydown: (e) => pickKey(e, co),
          onclick: () => { if (!disabled) toggle(co); } },
          co.own ? companyFlag(co) : Sprites.clone(Sprites.merc(co.captain.look, 2, 0), 'mini'),
          el('div', { class: 'grow' },
            el('div', {}, co.name, co.own ? null : el('span', { class: 'chip small', text: '외부' })),
            el('div', { class: `small ${refusal ? 'bad' : 'muted'}`, text: refusal || (co.own
              ? `출격 가능 ${avail.length}/${Game.members(co).length}명 · 결속도 ${co.cohesion}`
              : `${co.size}명 · 충성도 ${co.loyalty} · 몫 ${co.share}%${co.sympathy === c.target && c.target ? ' · 동조 세력 공격(충성도 하락)' : ''}`) })),
          el('b', { class: 'power' }, el('span', { class: 'sr-only', text: '전력 ' }), String(Game.unitsPower(c, [u]))));
      }));
      if (!comps.length) listBox.append(el('div', { class: 'muted small', text: '대기 중인 용병단이 없습니다.' }));

      // 선택된 직속 용병단의 출격 단원
      memberBox.replaceChildren(...[...sel.entries()].filter(([, v]) => v !== true).map(([id, set]) => {
        const co = Game.company(id);
        const labelId = `mp-${c.id}-${id}`;
        return el('div', { class: 'member-pick' },
          el('div', { class: 'small muted', id: labelId, text: `${co.name} 출격 단원 (눌러서 제외/포함)` }),
          el('div', { class: 'chips', role: 'group', 'aria-labelledby': labelId }, Game.availableMembers(co).map((m) => el('button', {
            type: 'button', role: 'checkbox', 'aria-checked': set.has(m.id) ? 'true' : 'false', 'data-fkey': `m-${m.id}`,
            class: `mchip ${set.has(m.id) ? 'on' : ''} ${m.fatigue >= 80 ? 'tired' : ''}`,
            onclick: () => { if (set.has(m.id)) set.delete(m.id); else set.add(m.id); refresh(); },
          }, mini(m.look), `${Game.isCaptain(m) ? '♛' : ''}${m.name}${m.fatigue >= 50 ? ` (${Game.fatigueState(m).label})` : ''}`))));
      }));
      if (keep && document.activeElement !== active) focusKey(keep);

      const us = units();
      const pw = Game.unitsPower(c, us);
      const req = Game.effectiveReq(c);
      const ch = Game.successChance(c, us);
      const [label, cls] = chanceLabel(ch);
      const head = Game.unitsHeadcount(us);
      const missingHero = Game.storyHeroMissing(c, us);
      const owner = Game.owner(c.province);
      const hostile = req > c.req;
      const { allMembers } = Game.unitParts(us);
      const tired = allMembers.filter((m) => m.fatigue >= 50);
      summary.replaceChildren(...[
        el('div', {}, '총 전투력 ', el('b', { text: pw }), ` / 권장 ${req}`, el('span', { class: `small ${head < c.size ? 'bad' : 'muted'}`, text: ` · 인원 ${head}/${c.size}` })),
        el('div', { class: 'bar big' }, el('div', { class: 'bar-fill f-power', style: `width:${Math.min(100, (pw / req) * 50)}%` }), el('div', { class: 'bar-mark' })),
        us.length ? el('div', {}, '예상 성공률 ', el('b', { class: cls, text: `${Math.round(ch * 100)}% (${label})` }), el('span', { class: 'small muted', text: ` · 소요 ${Game.contractDays(c, us)}일` }))
          : el('div', { class: 'muted', text: c.campaign ? `용병단을 최대 ${slots}개까지 고르세요. (직속·외부 합계)` : '용병단을 하나 고르세요.' }),
        us.length && slots > 1 ? el('div', { class: `small ${us.length >= slots ? 'warn' : 'muted'}`, text: `용병단 ${us.length}/${slots}개${us.length >= slots ? ' · 더 보내려면 하나를 빼야 합니다' : ''} (한 전장에 아군 부대는 최대 ${MAX_DISPATCH}개)` }) : null,
        head < c.size && us.length ? el('div', { class: 'bad small', text: `권장 인원보다 ${c.size - head}명 부족해 성공률이 떨어집니다.` }) : null,
        hostile ? el('div', { class: 'bad small', text: `${FACTIONS[owner].name}의 적대 지역: 난이도 상승` }) : null,
        tired.length ? el('div', { class: 'bad small', text: `피로한 단원: ${tired.map((m) => m.name).join(', ')}` }) : null,
        missingHero ? el('div', { class: 'bad small', text: `${HEROES[c.story.hero].name}이(가) 출격 단원에 있어야 합니다.` }) : null,
        c.campaign ? el('div', { class: 'small warn', text: '이 결전을 맡으면 반대 진영의 제안은 사라집니다.' }) : null,
      ].filter(Boolean));
      go.disabled = !us.length || missingHero;
    }

    go.addEventListener('click', () => {
      const us = units();
      UI.closeModal();
      Game.dispatch(c.id, us);
      // 키보드: 다른 의뢰의 「파견」이 남아 있으면 그쪽, 없으면 「다음 날」로
      const a = document.activeElement;
      if (!a || a.textContent !== '파견') document.getElementById('next-day').focus();
    });
    refresh(); // 창을 열기 전에 채워 두어야 첫 컨트롤로 초점이 간다
    UI.openModal(el('div', { class: 'dispatch' },
      el('h2', { text: c.title }),
      el('div', { class: 'parties' }, el('span', { class: 'small muted', text: `${PROVINCES[c.province].name} · ${QUEST_TYPES[c.type].name} · ★${c.level} · 의뢰주` }),
        factionTag(c.issuer), c.target ? el('span', { class: 'small muted', text: 'vs' }) : null, c.target ? factionTag(c.target) : null),
      el('div', { class: 'small' }, '성공 시: ', effectPreview(c)),
      listBox, memberBox, summary,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '취소', onclick: UI.closeModal }), go)));
  }
  UI.openDispatch = openDispatch;

  // ───────── 지도 ─────────
  T.map = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '대륙 에르덴' }),
      el('span', { class: 'muted small', text: '색은 지방을 다스리는 세력입니다. ⚔는 전쟁 중인 전선, ★는 수도입니다.' })));
    const info = el('div', { class: 'region-info' });
    const fill = (p) => {
      const pr = PROVINCES[p], st = s.provinces[p];
      const owner = st.owner;
      const open = Game.provinceOpen(p);
      const contracts = s.contracts.filter((c) => c.province === p);
      const wars = Game.warsOf(owner).filter((f) => Game.reachable(f, owner).includes(p));
      const boss = BOSSES[p];
      info.replaceChildren(...[
        el('h3', { class: 'region-name', text: pr.name }),
        el('div', { class: 'parties' }, factionTag(owner), el('span', { class: 'small muted', text: `${TERRAIN[pr.terrain].name}${Game.isCapital(p) ? ' · 수도' : ''}${pr.home ? ' · 길드 본부' : ''}` })),
        el('div', { class: 'cohesion' }, el('span', { class: 'small muted', text: '장악도' }),
          el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-cohesion', style: `width:${st.control}%` })), el('span', { class: 'small', text: st.control })),
        wars.length ? el('div', { class: 'small bad' }, '⚔ 전선: ', wars.map((f) => FACTIONS[f].name).join(', ')) : null,
        el('div', { class: 'small muted', text: open ? `활동 가능 · 의뢰 난이도 ★${TIER_LEVELS[pr.tier][0]}~${TIER_LEVELS[pr.tier][1]}` : `잠김 — 길드 ${RANKS[pr.tier].name}랭크 필요` }),
        el('div', { class: 'enemy-list' }, TERRAIN[pr.terrain].enemies.map((e) => el('div', { class: 'enemy' },
          Sprites.clone(Sprites.monster(e, 2, 0), 'mini'), el('span', { class: 'small', text: e })))),
        s.branches[p] ? el('div', { class: 'good small', text: '⚑ 길드 지부 운영 중: 의뢰 증가, 이동 -1일, 보상 +10%' })
          : Game.canBranch(p) ? el('button', { class: 'btn small', disabled: s.gold < Game.branchCost(p) ? 'disabled' : null, onclick: () => Game.buildBranch(p) },
            '⚑ 길드 지부 개설 ', icon('coin'), ` ${Game.branchCost(p)}`) : null,
        boss && open ? el('div', { class: `row boss-row ${s.bossDefeated[p] ? 'done' : ''}` },
          Sprites.clone(Sprites.monster(boss.enemy, 2, 0), 'mini'),
          el('div', { class: 'grow' }, el('div', { class: 'small bad', text: `재앙: ${boss.name}` }),
            el('div', { class: 'small muted', text: s.bossDefeated[p] ? '토벌 완료 (보상 +10%)' : `이 지방 의뢰 ${Math.min(s.provClears[p] || 0, boss.clears)}/${boss.clears}회 성공 시 출현` }))) : null,
        open ? el('h3', { text: `이 지방의 의뢰 (${contracts.length})` }) : null,
        open ? el('div', { class: 'list' }, contracts.length ? contracts.map((c) => el('div', { class: 'row' },
          factionFlag(c.issuer),
          el('div', { class: 'grow' }, el('div', { text: c.title }), el('div', { class: 'small muted', text: `${QUEST_TYPES[c.type].name} · ★${c.level} · 보상 ${c.reward}` })),
          el('button', { class: 'btn small', text: '파견', onclick: () => openDispatch(c) }))) : el('div', { class: 'muted small', text: '의뢰가 없습니다.' })) : null,
      ].filter(Boolean));
    };
    const cvs = WorldMap.create((p) => fill(p));
    fill(WorldMap.selected);
    root.append(el('div', { class: 'map-layout' }, el('div', { class: 'map-wrap' }, cvs), info));
  };

  // ───────── 세력 ─────────
  const perkLine = (on, text) => el('div', { class: `small ${on ? 'good' : 'muted'}`, text: `${on ? '✔' : '○'} ${text}` });
  function standingWeightLine(f) {
    const w = Game.standingWeights(f);
    const parts = [];
    if (w.gain < 1) parts.push(el('span', { class: 'chip bad', text: `상승 ×${w.gain}` }));
    parts.push(el('span', { class: `chip ${w.loss > 1 ? 'bad' : 'good'}`, title: '높은 평판일수록 쉽게 깎이고, 길드 명성이 하락을 덜어 줍니다', text: `하락 ×${w.loss.toFixed(2)}` }));
    return el('div', { class: 'chips' }, el('span', { class: 'small muted', text: '평판 변화' }), parts);
  }

  function doctrineBox(f) {
    const d = DOCTRINES[f];
    const level = (v, lo, hi, labels) => (v >= hi ? labels[2] : v >= lo ? labels[1] : labels[0]);
    const aggr = level(d.aggression, 0.7, 1.2, ['소극적', '보통', '호전적']);
    const peace = level(d.peaceAt, 40, 60, ['빠름', '보통', '완강']);
    const foes = Object.keys(d.targets).sort((a, b) => d.targets[b] - d.targets[a]);
    const likes = Object.entries(d.bias).filter(([, v]) => v >= 1.5).sort((a, b) => b[1] - a[1]).map(([k]) => QUEST_TYPES[k].name);
    return el('div', { class: 'doctrine' },
      el('div', { class: 'doctrine-head' }, el('span', { class: 'doctrine-name', text: `강령: ${d.name}` }), el('span', { class: 'doctrine-motto', text: `「${d.motto}」` })),
      el('div', { class: 'small', text: d.desc }),
      el('div', { class: 'chips' },
        el('span', { class: `chip ${aggr === '호전적' ? 'bad' : aggr === '소극적' ? 'good' : ''}`, text: `호전성 ${aggr}` }),
        el('span', { class: 'chip', text: `강화 ${peace}` }),
        d.reach > 1 ? el('span', { class: 'chip warn', text: `원정 ${d.reach}지방` }) : null,
        d.defense < 1 ? el('span', { class: 'chip good', text: `수비 ×${d.defense}` }) : null,
        d.pay > 1 ? el('span', { class: 'chip good', text: `보수 ×${d.pay}` }) : null,
        foes.length ? el('span', { class: 'chip bad' }, '주적 ', foes.map((g) => factionFlag(g, 1))) : el('span', { class: 'chip', text: '주적 없음' }),
        likes.length ? el('span', { class: 'chip', text: `주로 ${likes.join('·')} 의뢰` }) : null));
  }

  // 재앙 세력 / 봉인 상태
  function calamityPanel() {
    const s = Game.state;
    const cal = s.calamity;
    if (!cal) {
      const n = (s.destroyed || []).length;
      const text = s.calamityDefeated
        ? `${FACTIONS[s.calamityDefeated].leader}은(는) 쓰러졌습니다. 대륙에 다시 아침이 찾아왔습니다.`
        : `왕국은 용의 맹약으로 마물을, 교단은 성광의 봉인으로 마계의 문을 막고 있습니다. 패권국이 무너지거나 세력이 ${CALAMITY_TRIGGER}개 멸망하면 봉인이 깨집니다.`;
      return el('div', { class: `seal-panel ${s.omen ? 'omen' : ''}` },
        el('div', { class: 'seal-head' }, el('b', { text: s.calamityDefeated ? '봉인 회복' : '봉인 상태' }),
          s.calamityDefeated ? null : el('span', { class: `chip ${n >= CALAMITY_TRIGGER - 1 ? 'bad' : ''}`, text: `멸망한 세력 ${n}/${CALAMITY_TRIGGER}` }),
          s.omen && !s.calamityDefeated ? el('span', { class: 'chip bad', text: `징조: ${FACTIONS[s.omen].name}` }) : null),
        el('div', { class: 'small', text: text }));
    }
    const F = FACTIONS[cal];
    const provs = Game.provincesOf(cal);
    const fin = s.contracts.find((c) => c.final);
    return el('div', { class: 'calamity-panel', style: `--fc:${F.color}` },
      el('div', { class: 'portrait-wrap' }, Art.img(Art.idOf.boss(cal), 'big-portrait art-portrait') || Sprites.clone(Sprites.monster(F.leader, 4, 0), 'big-portrait')),
      el('div', { class: 'grow' },
        el('div', { class: 'cal-name' }, factionFlag(cal, 2), ` ${F.name} — ${F.leaderTitle} ${F.leader}`),
        el('div', { class: 'small', text: F.desc }),
        el('div', { class: 'chips' },
          el('span', { class: 'chip bad', text: `국력 ${Game.strength(cal)} (매일 증가)` }),
          el('span', { class: `chip ${provs.length >= CALAMITY_DARKNESS - 2 ? 'bad' : 'warn'}`, text: `점령 ${provs.length}/${CALAMITY_DARKNESS} (도달 시 암흑시대)` }),
          el('span', { class: 'chip', text: `${s.day - s.calamityDay}일째` })),
        fin ? el('div', { class: 'row-inline' },
          el('span', { class: 'small', text: `최종 결전 요구 전투력 ${fin.req} — 재앙의 영토를 빼앗을수록 낮아집니다.` }),
          el('button', { class: 'btn small primary', text: '최종 결전', onclick: () => openDispatch(fin) })) : null));
  }

  T.factions = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '세력' }),
      el('span', { class: 'muted small', text: `평판이 높을수록 혜택이 커지지만 쉽게 깎이고, 깊이 떨어진 평판은 잘 오르지 않습니다. 길드 명성 보정: 평판 하락 -${Math.round((1 - Game.fameShield()) * 100)}%` })));
    root.append(calamityPanel());
    if (s.wars.length) {
      root.append(el('h3', { class: 'group-title', text: '진행 중인 전쟁' }));
      root.append(el('div', { class: 'list' }, s.wars.map((w) => {
        const pct = 50 + clamp(w.score, -100, 100) / 2;
        return el('div', { class: 'row war-row' },
          factionFlag(w.a, 2), el('div', { class: 'grow' },
            el('div', {}, `${FACTIONS[w.a].name} vs ${FACTIONS[w.b].name}`),
            el('div', { class: 'war-bar' }, el('div', { class: 'war-fill', style: `width:${pct}%;background:${FACTIONS[w.a].color}` }),
              el('div', { class: 'war-rest', style: `background:${FACTIONS[w.b].color}` })),
            el('div', { class: 'small muted', text: `${s.day - w.start}일째 · 전쟁 피로 ${Math.round(w.weariness)} · 전선 ${new Set([...Game.reachable(w.a, w.b), ...Game.reachable(w.b, w.a)]).size}곳` })),
          factionFlag(w.b, 2));
      })));
    }
    root.append(el('h3', { class: 'group-title', text: '세력 목록' }));
    root.append(el('div', { class: 'faction-grid' }, FACTION_KEYS.map((f) => {
      const F = FACTIONS[f];
      const v = Game.standing(f);
      const ss = Game.standingState(v);
      const provs = Game.provincesOf(f);
      if (Game.isDestroyed(f)) {
        return el('div', { class: 'card faction-card destroyed', style: `--fc:${F.color}` },
          el('div', { class: 'card-head' }, factionFlag(f, 4),
            el('div', { class: 'card-title' }, el('div', { class: 'name', text: F.name }), el('div', { class: 'small bad', text: '☠ 멸망' }))),
          el('p', { class: 'small muted desc', text: `「${DOCTRINES[f].motto}」 — 그 외침은 이제 역사 속으로 사라졌습니다.` }));
      }
      return el('div', { class: `card faction-card ${F.hegemon ? 'hegemon' : ''}`, style: `--fc:${F.color}` },
        el('div', { class: 'card-head' }, factionFlag(f, 4),
          el('div', { class: 'card-title' },
            el('div', { class: 'name' }, F.name, F.hegemon ? el('span', { class: 'chip hegemon-chip', text: '패권국' }) : null),
            el('div', { class: 'small muted', text: `국력 ${Game.strength(f)} · 영토 ${provs.length}곳` }))),
        el('p', { class: 'small muted desc', text: F.desc }),
        doctrineBox(f),
        el('div', { class: 'standing' },
          el('span', { class: 'small', text: '평판' }),
          el('div', { class: 'stand-bar' }, el('div', { class: 'stand-mid' }),
            el('div', { class: `stand-fill ${v >= 0 ? 'pos' : 'neg'}`, style: v >= 0 ? `left:50%;width:${v / 2}%` : `left:${50 + v / 2}%;width:${-v / 2}%` })),
          el('span', { class: `stand-label ${ss.cls}`, text: `${ss.label} ${v}` })),
        standingWeightLine(f),
        el('div', { class: 'perks' },
          perkLine(v >= 45, `45 신뢰: ${F.perk.desc}`),
          perkLine(v >= FACTION_LOANS[f][0].at, `${FACTION_LOANS[f][0].at} 대여: ${FACTION_LOANS[f][0].name}`),
          perkLine(v >= ELITE_AT, `${ELITE_AT} 매주 정예 용병 (${TRAITS[FACTION_TRAITS[f]].name})`),
          perkLine(v >= FACTION_LOANS[f][1].at, `${FACTION_LOANS[f][1].at} 대여: ${FACTION_LOANS[f][1].name}`),
          FACTION_LOANS[f][2] ? perkLine(v >= FACTION_LOANS[f][2].at, `${FACTION_LOANS[f][2].at} 전설 대여: ${FACTION_LOANS[f][2].name}`) : null),
        el('div', { class: 'chips rel-chips' }, FACTION_KEYS.filter((g) => g !== f && !Game.isDestroyed(g)).map((g) => {
          const rs = Game.relationState(f, g);
          return el('span', { class: `chip ${rs.cls}`, title: `관계 ${Game.relation(f, g)}` }, factionFlag(g, 1), ` ${FACTIONS[g].short} ${rs.label}`);
        })));
    })));
    const news = s.log.filter((l) => l.kind === 'world').slice(0, 12);
    if (news.length) {
      root.append(el('h3', { class: 'group-title', text: '대륙 소식' }));
      root.append(el('div', { class: 'log' }, news.map((l) => el('div', { class: 'log-line world' }, el('span', { class: 'log-day', text: `${l.day}일차` }), l.text))));
    }
  };

  // ───────── 모집소 ─────────
  // 용병대장 한 명의 카드 (영입 현황판용)
  function captainCard(key) {
    const s = Game.state, C = CAPTAINS[key], CC = CAPTAIN_CLASSES[key], cs = s.captains[key];
    const statusText = {
      candidate: '창설 후보', locked: '아직 소문이 없음', challenge: '영입 과제 진행 중', pursuing: `영입 의뢰 진행 중 (${cs.ch}/${(C.chapters || []).length}장)`,
      joined: '합류', lost: cs.why ? `떠남 — ${cs.why}` : '영입 불가',
    }[cs.status];
    const lookOf = { cls: CC.style, cap: key, ...C.look };
    const ch = CAPTAIN_CHALLENGES[key] && (cs.status === 'challenge' || cs.status === 'locked') ? Game.challengeOf(key) : null;
    return el('div', { class: `card cap-card st-${cs.status}` },
      el('div', { class: 'card-head' },
        el('div', { class: 'portrait-wrap' }, UI.h.artPortrait(Art.idOf.captain(key), lookOf)),
        el('div', { class: 'card-title' },
          el('div', { class: 'name' }, C.name, el('span', { class: 'muted small', text: ` ${C.title}` })),
          el('div', { class: 'sub' }, el('span', { class: 'role-badge captain', text: '♛ 대장' }), ' ', el('span', { class: 'cls adv', text: CC.name })),
          el("div", { class: `small cap-status s-${cs.status}`, text: statusText }))),
      ch ? el('div', { class: 'challenge small' },
        el('div', { class: 'challenge-name' }, el('b', { text: `과제 「${ch.name}」` }), ch.ok ? el('span', { class: 'good', text: ' 달성!' }) : null),
        ch.conds.map((c) => el('div', { class: c.ok ? 'good' : c.dead ? 'bad' : 'muted', text: `${c.ok ? '✔' : c.dead ? '✘' : '·'} ${c.text}` }))) : null,
      el('div', { class: 'small muted', text: CC.desc }),
      UI.h.skillList({ actives: CC.acts.map((b) => ({ name: b.name, battle: describeBattle(b) })), passive: { name: CC.lead.name, desc: `지휘: ${CC.lead.desc}`, lead: true } }, { compact: true }),
      cs.status === 'pursuing' && C.chapters[cs.ch] ? el('div', { class: 'small warn', text: `다음: 「${C.chapters[cs.ch].title}」 — ${PROVINCES[C.chapters[cs.ch].province].name}` }) : null);
  }

  // 용병대장 영입 현황: 창설 + 시기별 영입 과제
  function captainRoster() {
    const s = Game.state, r = Game.rankIndex();
    const box = el('div', { class: 'cap-roster' });
    box.append(el('div', { class: 'cap-phase done' },
      el('div', { class: 'cap-phase-head' }, el('b', { text: '창설' }), el('span', { class: 'small muted', text: ` 첫 용병대장 (${STARTER_CAPTAINS.length}명 중 하나)` })),
      el('div', { class: 'cap-pair' }, STARTER_CAPTAINS.filter((k) => s.captains[k].status !== 'lost').map((k) => captainCard(k))),
      el('div', { class: 'small muted', text: `떠난 후보: ${STARTER_CAPTAINS.filter((k) => s.captains[k].status === 'lost').map((k) => `${CAPTAINS[k].name}(${CAPTAIN_CLASSES[k].name})`).join(', ')}` })));
    CAPTAIN_PHASES.forEach((ph) => {
      const st = s.phases[ph.key];
      const joined = ph.list.filter((k) => s.captains[k].status === 'joined').length;
      const head = el('div', { class: 'cap-phase-head' }, el('b', { text: `${ph.name} 영입 과제` }),
        el('span', { class: 'small muted', text: st === 'locked' ? ` 길드 등급 ${RANKS[ph.rank].name} 달성 시 공개 (현재 ${RANKS[r].name})` : ` 합류 ${joined}/${ph.list.length}명 · 과제는 서로 부딪히니 어떤 대장을 노릴지 고르세요` }));
      // 진행 중 → 영입 의뢰 중 → 합류 → 떠남 순
      const order = { pursuing: 0, challenge: 1, locked: 1, joined: 2, lost: 3 };
      const list = [...ph.list].sort((a, b) => order[s.captains[a].status] - order[s.captains[b].status]);
      box.append(el('div', { class: `cap-phase ${st}` }, head, el('div', { class: 'cap-pair' }, list.map((k) => captainCard(k)))));
    });
    return box;
  }

  T.recruit = (root) => {
    const s = Game.state;
    const joined = Object.values(s.captains || {}).filter((c) => c.status === 'joined').length;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: `용병대장 (합류 ${joined}명)` }),
      el('span', { class: 'muted small', text: '대장은 고유 직업·높은 성장률·지휘 스킬을 지닌 단 한 명뿐인 인물입니다. 대장마다 영입 과제가 있고, 조건을 한순간에 모두 만족하면 찾아옵니다. 그 뒤 영입 의뢰를 완수하면 합류합니다.' })));
    root.append(captainRoster());

    // 특별 용병과 세력 정예
    root.append(el('div', { class: 'panel-head mt' },
      el('h2', { text: '모집소 — 특별 용병 · 세력 정예' }),
      el('span', { class: 'muted small', text: `특별 용병은 고유 직업을 가진 대원입니다. 영입하면 이야기가 시작되고, 장을 마칠수록 대장 못지않게 강해집니다 · 길드 정원 ${s.mercs.length}/${Game.capacity()}` })));
    const grid = el('div', { class: 'grid' });
    s.recruits.forEach((m) => {
      const cost = Game.hireCost(m);
      const btn = el('button', { class: 'btn primary small', disabled: s.gold < cost ? 'disabled' : null, onclick: () => Game.hire(m.id) }, icon('coin'), ` ${cost} 영입`);
      const card = mercCard(m, { recruit: true, actions: [btn] });
      const h = m.hero && HEROES[m.hero];
      const desc = m.elite
        ? el('p', { class: 'small desc hero-desc' }, factionFlag(m.elite, 1), ` ${FACTIONS[m.elite].name} 정예 대원 · ${TRAITS[m.trait].name}: ${TRAITS[m.trait].desc} · 평판이 0 아래로 떨어지면 소환됨`)
        : h
        ? el('p', { class: 'small desc hero-desc' }, `특별 용병 · ${TRAITS[m.trait].name}: ${TRAITS[m.trait].desc}`, h.faction ? el('span', { class: 'muted' }, ` · 연고: ${FACTIONS[h.faction].name}`) : null)
        : null;
      if (desc) card.insertBefore(desc, card.querySelector('.stats'));
      grid.append(card);
    });
    if (!s.recruits.length) root.append(el('p', { class: 'empty', text: '지금은 찾아온 특별 용병이 없습니다. 길드 등급이 오르면 사연 있는 용병들이 찾아옵니다.' }));
    root.append(grid);

    // 대원 모집: 직업을 골라 뽑는다
    const vl = Game.veteranLevel();
    root.append(el('div', { class: 'panel-head mt' },
      el('h2', { text: '모집소 — 대원 모집' }),
      el('span', { class: 'muted small', text: `대원은 능력치 편차가 없는 범용 용병입니다. 직업을 골라 뽑고, 전직으로 역할을 정하세요. 숙련병 레벨은 모집소 단계와 길드 등급에 따라 오릅니다 (현재 Lv.${vl}).` })));
    root.append(el('div', { class: 'unit-grid' }, Object.entries(CLASSES).map(([cls, C]) => {
      const lv1 = { ...C.base, maxHp: C.base.hp };
      const costN = Game.unitHireCost(cls, false), costV = Game.unitHireCost(cls, true);
      const full = s.mercs.length >= Game.capacity();
      return el('div', { class: 'card unit-card' },
        el('div', { class: 'card-head' },
          el('div', { class: 'portrait-wrap' }, UI.h.portrait({ cls, skin: '#f2c9a0', hair: '#5a3720' })),
          el('div', { class: 'card-title' },
            el('div', { class: 'name', text: C.name }),
            el('div', { class: 'small muted', text: `힘 ${lv1.str} · 민첩 ${lv1.dex} · 지력 ${lv1.int} · 체력 ${lv1.maxHp}` }))),
        el('p', { class: 'small', text: C.desc }),
        UI.h.skillList({ actives: [{ name: CLASS_SKILLS[cls].name, battle: describeBattle(CLASS_SKILLS[cls].b), mission: describeFx(CLASS_SKILLS[cls].fx) }] }, { compact: true }),
        el('div', { class: 'small muted', text: `승급: ${PROMOTIONS[cls].map((p) => `${p.name} → ${MASTERS[p.key].map((x) => x.name).join('/')}`).join(' · ')}` }),
        el('div', { class: 'card-foot' },
          el('button', { class: 'btn small', disabled: full || s.gold < costN ? 'disabled' : null, onclick: () => Game.hireUnit(cls, false) }, icon('coin'), ` ${costN} 신병 Lv.1`),
          el('button', { class: 'btn primary small', disabled: full || s.gold < costV ? 'disabled' : null, onclick: () => Game.hireUnit(cls, true) }, icon('coin'), ` ${costV} 숙련병 Lv.${vl}`)));
    })));

    root.append(el('div', { class: 'panel-head mt' },
      el('h2', { text: '용병단 시장' }),
      el('span', { class: 'muted small', text: '2주마다 새 용병단이 찾아옵니다. 외부 용병단은 보상 몫을 떼어 가고, 성향에 따라 의뢰를 거부하기도 합니다.' })));
    root.append(s.market.length ? el('div', { class: 'company-grid' }, s.market.map((c) => extCompanyPanel(c, true)))
      : el('p', { class: 'empty', text: '지금은 계약할 수 있는 용병단이 없습니다.' }));
  };

  // ───────── 상점 ─────────
  function itemRow(it, price, label, onClick, disabled) {
    return el('div', { class: `row item-row tier-${it.tier}` },
      el('div', { class: 'item-icon' }, itemIcon(it.base, it.tier, 3)),
      el('div', { class: 'grow' },
        el('div', { class: `item-name tier-text-${it.tier}` }, it.name, it.loan ? el('span', { class: 'chip loan' }, factionFlag(it.loan, 1), ' 대여') : null),
        el('div', { class: 'small' }, el('span', { class: 'muted', text: `${SLOT_NAMES[it.slot]} · ` }), bonusText(it.bonus))),
      it.loan ? el('span', { class: 'small muted', text: '판매 불가' })
        : el('button', { class: 'btn small', disabled: disabled ? 'disabled' : null, onclick: onClick }, icon('coin'), ` ${price} ${label}`));
  }

  T.shop = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' }, el('h2', { text: '상점' }),
      el('span', { class: 'muted small', text: `매주 새 물건 · 최대 ${TIERS[Game.shopMaxTier()].name} 등급${Game.perk('cities') ? ' · 자유 도시 할인 적용' : ''}` })));
    root.append(el('div', { class: 'list' }, el('div', { class: 'row item-row' },
      el('div', { class: 'item-icon' }, itemIcon('herb', 0, 3)),
      el('div', { class: 'grow' }, el('div', { class: 'item-name', text: '치료 약초' }), el('div', { class: 'small muted', text: `부상 3일 즉시 회복 · 보유 ${s.herbs}개` })),
      el('button', { class: 'btn small', disabled: s.gold < HERB_PRICE ? 'disabled' : null, onclick: () => Game.buyHerb() }, icon('coin'), ` ${HERB_PRICE} 구입`))));
    root.append(el('h3', { class: 'group-title', text: '진열대' }));
    root.append(el('div', { class: 'list' }, s.shop.length ? s.shop.map((it) => {
      const price = Game.shopPrice(it);
      return itemRow(it, price, '구입', () => Game.buy(it.id), s.gold < price);
    }) : el('p', { class: 'empty', text: '모두 팔렸습니다.' })));
    root.append(el('h3', { class: 'group-title', text: `창고 (${s.inventory.length})` }));
    root.append(el('div', { class: 'list' }, s.inventory.length ? s.inventory.map((it) =>
      itemRow(it, Game.sellPrice(it), '판매', () => UI.confirmBox(`${it.name}을(를) ${Game.sellPrice(it)} 금화에 팔까요?`, () => Game.sell(it.id)))) :
      el('p', { class: 'empty', text: '창고가 비어 있습니다.' })));
    root.append(el('p', { class: 'muted small', text: '장비는 용병단 탭에서 단원을 눌러 장착합니다.' }));
  };

  // ───────── 시설 ─────────
  T.facilities = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' }, el('h2', { text: '길드 시설' }), el('span', { class: 'muted small', text: '시설을 증축해 길드를 키우세요.' })));
    root.append(el('div', { class: 'list' }, Object.entries(FACILITIES).map(([key, f]) => {
      const lv = s.facilities[key], maxed = lv >= f.max, cost = Game.facilityCost(key);
      return el('div', { class: 'row facility' }, icon('house', 3),
        el('div', { class: 'grow' },
          el('div', { class: 'name' }, `${f.name} `, el('span', { class: 'lv', text: `${lv}/${f.max}단계` })),
          el('div', { class: 'pips' }, Array.from({ length: f.max }, (_, i) => el('span', { class: i < lv ? 'pip on' : 'pip' }))),
          el('div', { class: 'muted small', text: `현재: ${f.desc(lv)}` }),
          maxed ? null : el('div', { class: 'good small', text: `다음: ${f.desc(lv + 1)}` })),
        maxed ? el('span', { class: 'tag tag-idle', text: '최대' })
          : el('button', { class: 'btn small', disabled: s.gold < cost ? 'disabled' : null, onclick: () => Game.upgrade(key) }, icon('coin'), ` ${cost}`));
    })));
    const st = s.stats;
    root.append(el('h3', { class: 'group-title', text: '길드 기록' }),
      el('div', { class: 'row' }, `완수 ${st.completed} · 실패 ${st.failed} · 전사 ${st.fallen} · 지부 ${Object.keys(s.branches).length}곳`));
  };

  // ───────── 일지 ─────────
  T.log = (root) => {
    root.append(el('h2', { text: '길드 일지' }));
    root.append(el('div', { class: 'log' }, Game.state.log.map((l) => el('div', { class: `log-line ${l.kind}` },
      el('span', { class: 'log-day', text: `${l.day}일차` }), l.text))));
  };
})();
