// 탭 화면: 용병단, 의뢰(+파견 창), 지도, 세력, 모집소, 상점, 시설, 일지
'use strict';

(() => {
  const { el, icon, itemIcon, mini, bonusText, signed, companyFlag, factionFlag, factionTag, condTags, mercCard } = UI.h;
  const T = UI.tabs;

  // ───────── 용병단 ─────────
  function memberRow(m, c) {
    const isLeader = c && c.leaderId === m.id;
    return el('div', { class: `mrow ${m.status}`, onclick: () => UI.openMerc(m.id) },
      mini(m.look),
      el('div', { class: 'grow' },
        el('div', { class: 'mname' }, isLeader ? el('span', { class: 'crown', title: '단장', text: '♛' }) : null, m.name,
          el('span', { class: 'lv', text: ` Lv.${m.level}` }), m.hero ? el('span', { class: 'hero-mark', text: ' ★' }) : null),
        el('div', { class: 'small muted' }, `${Game.className(m)} · ${TRAITS[m.trait].name}`)),
      el('div', { class: 'mtags' },
        m.status === 'injured' ? el('span', { class: 'tag tag-injured', text: `부상 ${Math.ceil(m.injury)}일` }) : null,
        m.status === 'quest' ? el('span', { class: 'tag tag-quest', text: '출격' }) : null,
        Game.canPromote(m) && m.status !== 'quest' ? el('span', { class: 'tag tag-promo', text: '전직 가능' }) : null,
        ...condTags(m)));
  }

  function ownCompanyPanel(c) {
    const s = Game.state;
    const ms = Game.members(c);
    const mi = c.missionId && s.missions.find((x) => x.id === c.missionId);
    const pw = ms.reduce((a, m) => a + Game.power(m, null, ms), 0);
    const leader = Game.leader(c);
    return el('div', { class: 'company-panel', style: `--cc:${c.color}` },
      el('div', { class: 'company-head' },
        companyFlag(c, 3),
        el('div', { class: 'grow' },
          el('div', { class: 'cname', text: c.name }),
          el('div', { class: 'small muted', text: `단장 ${leader ? leader.name : '없음'} · ${ms.length}/${Game.companySize()}명 · 전적 ${c.wins}승 ${c.losses}패 · 기본 전투력 ${Math.round(pw * Game.cohesionMul(c) * Game.leaderMul(c))}` }),
          el('div', { class: 'cohesion' }, el('span', { class: 'small muted', text: '결속도' }),
            el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-cohesion', style: `width:${c.cohesion}%` })),
            el('span', { class: 'small', text: c.cohesion }))),
        el('div', { class: 'company-status' },
          mi ? el('span', { class: 'tag tag-quest', text: `출격 중 · ${mi.returnDay - s.day}일 후 귀환` }) : el('span', { class: 'tag tag-idle', text: '대기' }),
          mi ? el('div', { class: 'small muted', text: mi.contract.title }) : null)),
      el('div', { class: 'members' }, ms.length ? ms.map((m) => memberRow(m, c)) : el('div', { class: 'muted small pad', text: '단원이 없습니다. 예비 인원을 배속하세요.' })),
      el('div', { class: 'company-foot' },
        el('select', { class: 'input small', disabled: c.missionId ? 'disabled' : null, onchange: (e) => Game.setLeader(c.id, Number(e.target.value)) },
          ms.map((m) => el('option', { value: m.id, selected: m.id === c.leaderId ? 'selected' : null }, `단장: ${m.name}`))),
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
          el('div', { class: 'small muted', text: `단장 ${c.captain.name} · Lv.${c.level} · ${c.size}/${c.maxSize}명 · 기본 전투력 ${Game.extPower(c, null)}` }),
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
    const open = Game.ownCompanies().filter((c) => !c.missionId && Game.members(c).length < Game.companySize());
    if (open.length === 1) Game.assign(m.id, open[0].id);
    else if (!open.length) UI.toast('빈 자리가 있는 대기 중인 용병단이 없습니다.');
    else UI.openMerc(m.id);
  }

  // ───────── 의뢰 ─────────
  function effectPreview(c) {
    const kind = c.cat === 'monster' ? 'monster' : c.type;
    const eff = CONTRACT_EFFECTS[kind].win;
    const parts = [];
    if (eff.issuer && !FACTIONS[c.issuer].neutral) parts.push(el('span', { class: 'chip good' }, factionFlag(c.issuer, 1), ` ${FACTIONS[c.issuer].short} ${signed(eff.issuer)}`));
    if (eff.target && c.target) parts.push(el('span', { class: 'chip bad' }, factionFlag(c.target, 1), ` ${FACTIONS[c.target].short} ${signed(eff.target)}`));
    if (c.type === 'battle' && c.campaign) parts.push(el('span', { class: 'chip warn', text: c.campaign.side === 'attack' ? `승리 시 ${PROVINCES[c.province].name} 점령` : `패배 시 ${PROVINCES[c.province].name} 함락` }));
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
    const banner = c.campaign ? el('div', { class: 'story-banner campaign-banner' }, `⚔ 대규모 결전 · 용병단 ${c.campaign.slots}개 투입 · ${c.campaign.side === 'attack' ? '공격측' : '방어측'}`)
      : story ? el('div', { class: 'story-banner' }, `★ ${story.name}의 이야기 ${c.story.ch + 1}장`)
        : c.boss ? el('div', { class: 'story-banner boss-banner' }, `☠ 재앙 · ${BOSSES[c.boss].name}`) : null;
    return el('div', { class: `card quest-card cat-${c.cat} ${story ? 'story' : ''} ${c.boss ? 'boss' : ''} ${c.campaign ? 'campaign' : ''}` },
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
        el('div', {}, icon('coin'), ` 보상 ${c.reward}`),
        el('div', {}, icon('star'), ` 명성 +${c.rep}`),
        el('div', { text: `권장 전투력 ${Game.effectiveReq(c)}` }),
        el('div', { text: `권장 ${c.size}명 · ${c.days}일` }),
        el('div', { class: 'muted', text: story || c.boss ? '마감 없음' : `마감까지 ${c.expires - s.day}일` })),
      effectPreview(c),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted small', text: story ? `${story.name} 필수` : weightHint(c.type) }),
        el('button', { class: 'btn', text: '파견', disabled: free ? null : 'disabled', onclick: () => openDispatch(c) })));
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
      el('span', { class: 'muted small', text: '세력 분쟁 의뢰는 의뢰주의 평판을 올리는 대신 대상 세력의 평판을 떨어뜨립니다.' })));
    const groups = [
      ['특별', s.contracts.filter((c) => c.campaign || c.story || c.boss)],
      ['세력 분쟁', s.contracts.filter((c) => !c.campaign && !c.story && !c.boss && c.cat !== 'monster')],
      ['괴물·치안', s.contracts.filter((c) => !c.campaign && !c.story && !c.boss && c.cat === 'monster')],
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
    const slots = c.campaign ? c.campaign.slots : 1;
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
        if (sel.size >= slots) return;
        sel.set(co.id, co.own ? defaultMembers(co) : true);
      }
      refresh();
    }

    function refresh() {
      listBox.replaceChildren(...comps.map((co) => {
        const refusal = !co.own && Game.extRefusal(co, c);
        const avail = co.own ? Game.availableMembers(co) : null;
        const disabled = refusal || (co.own && !avail.length);
        const on = sel.has(co.id);
        const u = co.own ? { companyId: co.id, memberIds: [...(on ? sel.get(co.id) : defaultMembers(co))] } : { companyId: co.id };
        return el('div', { class: `pick ${on ? 'on' : ''} ${disabled ? 'locked' : ''}`, onclick: () => { if (!disabled) toggle(co); } },
          co.own ? companyFlag(co) : Sprites.clone(Sprites.merc(co.captain.look, 2, 0), 'mini'),
          el('div', { class: 'grow' },
            el('div', {}, co.name, co.own ? null : el('span', { class: 'chip small', text: '외부' })),
            el('div', { class: `small ${refusal ? 'bad' : 'muted'}`, text: refusal || (co.own
              ? `출격 가능 ${avail.length}/${Game.members(co).length}명 · 결속도 ${co.cohesion}`
              : `${co.size}명 · 충성도 ${co.loyalty} · 몫 ${co.share}%${co.sympathy === c.target && c.target ? ' · 동조 세력 공격(충성도 하락)' : ''}`) })),
          el('b', { class: 'power', text: Game.unitsPower(c, [u]) }));
      }));
      if (!comps.length) listBox.append(el('div', { class: 'muted small', text: '대기 중인 용병단이 없습니다.' }));

      // 선택된 직속 용병단의 출격 단원
      memberBox.replaceChildren(...[...sel.entries()].filter(([, v]) => v !== true).map(([id, set]) => {
        const co = Game.company(id);
        return el('div', { class: 'member-pick' },
          el('div', { class: 'small muted', text: `${co.name} 출격 단원 (눌러서 제외/포함)` }),
          el('div', { class: 'chips' }, Game.availableMembers(co).map((m) => el('span', {
            class: `mchip ${set.has(m.id) ? 'on' : ''} ${m.fatigue >= 80 ? 'tired' : ''}`,
            onclick: () => { if (set.has(m.id)) set.delete(m.id); else set.add(m.id); refresh(); },
          }, mini(m.look), `${m.name}${m.fatigue >= 50 ? ` (${Game.fatigueState(m).label})` : ''}`))));
      }));

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
          : el('div', { class: 'muted', text: c.campaign ? `용병단을 최대 ${slots}개까지 고르세요.` : '용병단을 고르세요.' }),
        head < c.size && us.length ? el('div', { class: 'bad small', text: `권장 인원보다 ${c.size - head}명 부족해 성공률이 떨어집니다.` }) : null,
        hostile ? el('div', { class: 'bad small', text: `${FACTIONS[owner].name}의 적대 지역: 난이도 상승` }) : null,
        tired.length ? el('div', { class: 'bad small', text: `피로한 단원: ${tired.map((m) => m.name).join(', ')}` }) : null,
        missingHero ? el('div', { class: 'bad small', text: `${HEROES[c.story.hero].name}이(가) 출격 단원에 있어야 합니다.` }) : null,
        c.campaign ? el('div', { class: 'small warn', text: '이 결전을 맡으면 반대 진영의 제안은 사라집니다.' }) : null,
      ].filter(Boolean));
      go.disabled = !us.length || missingHero;
    }

    go.addEventListener('click', () => { const us = units(); UI.closeModal(); Game.dispatch(c.id, us); });
    UI.openModal(el('div', { class: 'dispatch' },
      el('h2', { text: c.title }),
      el('div', { class: 'parties' }, el('span', { class: 'small muted', text: `${PROVINCES[c.province].name} · ${QUEST_TYPES[c.type].name} · ★${c.level} · 의뢰주` }),
        factionTag(c.issuer), c.target ? el('span', { class: 'small muted', text: 'vs' }) : null, c.target ? factionTag(c.target) : null),
      el('div', { class: 'small' }, '성공 시: ', effectPreview(c)),
      listBox, memberBox, summary,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '취소', onclick: UI.closeModal }), go)));
    refresh();
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
      const wars = Game.warsOf(owner).filter((f) => ADJACENCY[p].some((q) => Game.owner(q) === f));
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
  T.factions = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '세력' }),
      el('span', { class: 'muted small', text: '평판 45 이상(신뢰)이면 혜택, -40 이하면 의뢰가 끊기고, -60 이하면 보복이 시작됩니다.' })));
    if (s.wars.length) {
      root.append(el('h3', { class: 'group-title', text: '진행 중인 전쟁' }));
      root.append(el('div', { class: 'list' }, s.wars.map((w) => {
        const pct = 50 + clamp(w.score, -100, 100) / 2;
        return el('div', { class: 'row war-row' },
          factionFlag(w.a, 2), el('div', { class: 'grow' },
            el('div', {}, `${FACTIONS[w.a].name} vs ${FACTIONS[w.b].name}`),
            el('div', { class: 'war-bar' }, el('div', { class: 'war-fill', style: `width:${pct}%;background:${FACTIONS[w.a].color}` }),
              el('div', { class: 'war-rest', style: `background:${FACTIONS[w.b].color}` })),
            el('div', { class: 'small muted', text: `${s.day - w.start}일째 · 전쟁 피로 ${Math.round(w.weariness)} · 전선 ${Game.frontOf(w.a, w.b).length + Game.frontOf(w.b, w.a).length}곳` })),
          factionFlag(w.b, 2));
      })));
    }
    root.append(el('h3', { class: 'group-title', text: '세력 목록' }));
    root.append(el('div', { class: 'faction-grid' }, FACTION_KEYS.map((f) => {
      const F = FACTIONS[f];
      const v = Game.standing(f);
      const ss = Game.standingState(v);
      const provs = Game.provincesOf(f);
      return el('div', { class: 'card faction-card', style: `--fc:${F.color}` },
        el('div', { class: 'card-head' }, factionFlag(f, 4),
          el('div', { class: 'card-title' },
            el('div', { class: 'name', text: F.name }),
            el('div', { class: 'small muted', text: `국력 ${Game.strength(f)} · 영토 ${provs.length}곳${provs.length ? '' : ' (망명)'}` }))),
        el('p', { class: 'small muted desc', text: F.desc }),
        el('div', { class: 'standing' },
          el('span', { class: 'small', text: '평판' }),
          el('div', { class: 'stand-bar' }, el('div', { class: 'stand-mid' }),
            el('div', { class: `stand-fill ${v >= 0 ? 'pos' : 'neg'}`, style: v >= 0 ? `left:50%;width:${v / 2}%` : `left:${50 + v / 2}%;width:${-v / 2}%` })),
          el('span', { class: `stand-label ${ss.cls}`, text: `${ss.label} ${v}` })),
        el('div', { class: `small ${Game.perk(f) ? 'good' : 'muted'}`, text: `${Game.perk(f) ? '✔' : '○'} 신뢰 혜택: ${F.perk.desc}` }),
        el('div', { class: 'chips rel-chips' }, FACTION_KEYS.filter((g) => g !== f).map((g) => {
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
  T.recruit = (root) => {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: '모집소 — 개인 지원자' }),
      el('div', { class: 'row-inline' },
        el('span', { class: 'muted small', text: `고용한 단원은 예비 인원이 됩니다 · 길드 정원 ${s.mercs.length}/${Game.capacity()}` }),
        el('button', { class: 'btn small', text: '지원자 새로 부르기 (30)', onclick: () => Game.refreshRecruits(true) }))));
    const grid = el('div', { class: 'grid' });
    s.recruits.forEach((m) => {
      const cost = Game.hireCost(m);
      const btn = el('button', { class: 'btn primary small', disabled: s.gold < cost ? 'disabled' : null, onclick: () => Game.hire(m.id) }, icon('coin'), ` ${cost} 고용`);
      const card = mercCard(m, { recruit: true, actions: [btn] });
      const h = m.hero && HEROES[m.hero];
      const desc = h
        ? el('p', { class: 'small desc hero-desc' }, `특별 용병 · ${TRAITS[m.trait].name}: ${TRAITS[m.trait].desc}`, h.faction ? el('span', { class: 'muted' }, ` · 연고: ${FACTIONS[h.faction].name}`) : null)
        : el('p', { class: 'muted small desc', text: CLASSES[m.cls].desc });
      card.insertBefore(desc, card.querySelector('.stats'));
      grid.append(card);
    });
    if (!s.recruits.length) root.append(el('p', { class: 'empty', text: '오늘은 지원자가 없습니다.' }));
    root.append(grid);
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
        el('div', { class: `item-name tier-text-${it.tier}`, text: it.name }),
        el('div', { class: 'small' }, el('span', { class: 'muted', text: `${SLOT_NAMES[it.slot]} · ` }), bonusText(it.bonus))),
      el('button', { class: 'btn small', disabled: disabled ? 'disabled' : null, onclick: onClick }, icon('coin'), ` ${price} ${label}`));
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
