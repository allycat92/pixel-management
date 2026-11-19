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
  const portrait = (look, scale = 3) => Sprites.clone(Sprites.merc(look, scale, 0), 'portrait');

  function statusLabel(m) {
    if (m.status === 'quest') {
      const mi = Game.state.missions.find((x) => x.id === m.missionId);
      return el('span', { class: 'tag tag-quest', text: `의뢰 중 (${mi ? mi.returnDay - Game.state.day : '?'}일)` });
    }
    if (m.status === 'injured') return el('span', { class: 'tag tag-injured', text: `부상 (${Math.ceil(m.injury)}일)` });
    return el('span', { class: 'tag tag-idle', text: '대기' });
  }

  function statBar(label, value, max, cls) {
    return el('div', { class: 'stat' },
      el('span', { class: 'stat-label', text: label }),
      el('div', { class: 'bar' }, el('div', { class: `bar-fill ${cls}`, style: `width:${Math.min(100, (value / max) * 100)}%` })),
      el('span', { class: 'stat-val', text: value }));
  }

  function mercCard(m, opts = {}) {
    const c = CLASSES[m.cls];
    const card = el('div', { class: `card merc-card ${m.status}` },
      el('div', { class: 'card-head' },
        el('div', { class: 'portrait-wrap' }, portrait(m.look)),
        el('div', { class: 'card-title' },
          el('div', { class: 'name' }, m.name, el('span', { class: 'lv', text: ` Lv.${m.level}` })),
          el('div', { class: 'sub' }, el('span', { class: `cls cls-${m.cls}`, text: c.name }), ' ',
            el('span', { class: 'trait', title: TRAITS[m.trait].desc, text: TRAITS[m.trait].name })),
          opts.recruit ? null : statusLabel(m))),
      el('div', { class: 'stats' },
        statBar('힘', m.str, 40, 'f-str'),
        statBar('민첩', m.dex, 40, 'f-dex'),
        statBar('지력', m.int, 40, 'f-int'),
        statBar('체력', m.maxHp, 90, 'f-hp')),
      opts.recruit ? null : el('div', { class: 'exp' },
        el('div', { class: 'bar thin' }, el('div', { class: 'bar-fill f-exp', style: `width:${(m.exp / Game.expToNext(m)) * 100}%` })),
        el('span', { text: `EXP ${m.exp}/${Game.expToNext(m)}` })),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted', text: `주급 ${Game.wage(m)}` }),
        opts.action || null));
    return card;
  }

  // ───────── 탭: 용병단 ─────────
  function renderRoster(root) {
    const s = Game.state;
    root.append(el('div', { class: 'panel-head' },
      el('h2', { text: `단원 명부 (${s.mercs.length}/${Game.capacity()})` }),
      el('span', { class: 'muted', text: `주급 합계 ${Game.weeklyWageTotal()} · 정산까지 ${Game.daysToPayday()}일` })));
    if (!s.mercs.length) root.append(el('p', { class: 'empty', text: '단원이 없습니다. 주점에서 용병을 고용하세요.' }));
    const grid = el('div', { class: 'grid' });
    s.mercs.forEach((m) => {
      const btn = m.status === 'quest' ? null : el('button', {
        class: 'btn small danger', text: '해고',
        onclick: () => confirmBox(`${m.name}을(를) 해고할까요?`, () => Game.dismiss(m.id)),
      });
      grid.append(mercCard(m, { action: btn }));
    });
    root.append(grid);

    if (s.missions.length) {
      root.append(el('h2', { class: 'mt', text: '진행 중인 의뢰' }));
      const list = el('div', { class: 'list' });
      s.missions.forEach((mi) => {
        const party = mi.party.map((id) => s.mercs.find((m) => m.id === id)).filter(Boolean);
        list.append(el('div', { class: 'row mission' },
          icon(QUEST_TYPES[mi.quest.type].icon),
          el('span', { class: 'grow', text: mi.quest.title }),
          el('span', { class: 'party-mini' }, party.map((m) => Sprites.clone(Sprites.merc(m.look, 2, 0), 'mini'))),
          el('span', { class: 'tag tag-quest', text: `${mi.returnDay - s.day}일 후 귀환` })));
      });
      root.append(list);
    }
  }

  // ───────── 탭: 의뢰 게시판 ─────────
  function questCard(q) {
    const t = QUEST_TYPES[q.type];
    const s = Game.state;
    const stars = el('span', { class: 'stars', title: `난이도 ${q.level}` }, `★${q.level}`);
    const idle = s.mercs.filter((m) => m.status === 'idle');
    return el('div', { class: 'card quest-card' },
      el('div', { class: 'card-head' },
        el('div', { class: 'quest-icon' }, icon(t.icon, 4)),
        el('div', { class: 'card-title' },
          el('div', { class: 'name', text: q.title }),
          el('div', { class: 'sub' }, el('span', { class: `qtype q-${q.type}`, text: t.name }), ' ', stars))),
      el('div', { class: 'quest-info' },
        el('div', {}, icon('coin'), ` 보상 ${q.reward}`),
        el('div', {}, icon('star'), ` 명성 +${q.rep}`),
        el('div', { text: `권장 전투력 ${q.req}` }),
        el('div', { text: `소요 ${q.days}일 · 최대 ${q.maxParty}명` }),
        el('div', { class: 'muted', text: `마감까지 ${q.expires - s.day}일` })),
      el('div', { class: 'card-foot' },
        el('span', { class: 'muted small', text: weightHint(q.type) }),
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
    const summary = el('div', { class: 'dispatch-summary' });
    const go = el('button', { class: 'btn primary', text: '출발!', disabled: 'disabled' });

    function refresh() {
      const party = [...selected].map((id) => s.mercs.find((m) => m.id === id));
      const pw = Game.partyPower(party, q.type);
      const c = Game.successChance(q, party);
      const [label, cls] = chanceLabel(c);
      summary.replaceChildren(...[
        el('div', {}, `파티 전투력 `, el('b', { text: pw }), ` / 권장 ${q.req}`),
        el('div', { class: 'bar big' }, el('div', { class: 'bar-fill f-power', style: `width:${Math.min(100, (pw / q.req) * 50)}%` }), el('div', { class: 'bar-mark' })),
        party.length ? el('div', {}, '예상 성공률 ', el('b', { class: cls, text: `${Math.round(c * 100)}% (${label})` })) : el('div', { class: 'muted', text: '단원을 선택하세요.' }),
        party.some((m) => m.cls === 'cleric') ? el('div', { class: 'good small', text: '✚ 성직자 동행: 부상·사망 위험 감소' }) : null,
      ].filter(Boolean));
      go.disabled = !party.length;
      list.querySelectorAll('.pick').forEach((row) => {
        const on = selected.has(Number(row.dataset.id));
        row.classList.toggle('on', on);
        row.classList.toggle('locked', !on && selected.size >= q.maxParty);
      });
    }

    const list = el('div', { class: 'pick-list' });
    idle.forEach((m) => {
      list.append(el('div', {
        class: 'pick', 'data-id': m.id,
        onclick: () => {
          if (selected.has(m.id)) selected.delete(m.id);
          else if (selected.size < q.maxParty) selected.add(m.id);
          refresh();
        },
      },
      Sprites.clone(Sprites.merc(m.look, 2, 0), 'mini'),
      el('span', { class: 'grow' }, `${m.name} `, el('span', { class: 'muted', text: `${CLASSES[m.cls].name} Lv.${m.level}` })),
      el('span', { class: 'trait small', text: TRAITS[m.trait].name }),
      el('b', { class: 'power', text: Game.power(m, q.type) })));
    });

    go.addEventListener('click', () => { closeModal(); Game.dispatch(q.id, [...selected]); });
    openModal(el('div', {},
      el('h2', {}, icon(QUEST_TYPES[q.type].icon, 3), ` ${q.title}`),
      el('p', { class: 'muted', text: `${QUEST_TYPES[q.type].name} · ★${q.level} · ${q.days}일 · 최대 ${q.maxParty}명 · 보상 ${q.reward} 금화` }),
      list, summary,
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn', text: '취소', onclick: closeModal }), go)));
    refresh();
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
      const card = mercCard(m, { recruit: true, action: btn });
      card.insertBefore(el('p', { class: 'muted small desc', text: CLASSES[m.cls].desc }), card.querySelector('.stats'));
      grid.append(card);
    });
    root.append(grid);
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
        const n = { quests: s.quests.length, tavern: s.recruits.length }[b.dataset.tab];
        badge.textContent = n || '';
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
    ({ roster: renderRoster, quests: renderQuests, tavern: renderTavern, facilities: renderFacilities, log: renderLog })[tab](root);
    root.scrollTop = scroll;
    showReports();
  }

  // 의뢰 결과 보고서를 하나씩 띄운다
  function showReports() {
    const s = Game.state;
    if (modalOpen || !s.pendingReports.length) return;
    const r = s.pendingReports.shift();
    Game.save();
    if (r.special) return openModal(specialReport(r), true);
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
    openModal(el('div', { class: 'report' },
      el('div', { class: `report-banner ${good ? 'good' : 'bad'} ${r.outcome}`, text: titles[r.outcome] }),
      el('h3', { text: r.quest.title }),
      members,
      el('div', { class: 'report-rewards' },
        el('span', {}, icon('coin'), ` ${r.gold >= 0 ? '+' : ''}${r.gold}`),
        el('span', {}, icon('star'), ` ${r.rep >= 0 ? '+' : ''}${r.rep}`)),
      el('div', { class: 'modal-actions' }, el('button', { class: 'btn primary', text: '확인', onclick: closeModal }))));
  }

  function specialReport(r) {
    const s = Game.state;
    const restart = el('button', { class: 'btn primary', text: '새 게임', onclick: () => { closeModal(); Game.clearSave(); Game.newGame(); Game.emit(); } });
    if (r.special === 'win') {
      return el('div', { class: 'report' },
        el('div', { class: 'report-banner good great', text: 'S랭크 달성!' }),
        el('p', { text: `${s.day}일 만에 ${s.guildName}이(가) 대륙 최고의 용병단이 되었습니다!` }),
        el('p', { class: 'muted', text: `완수 ${s.stats.completed} · 실패 ${s.stats.failed} · 전사 ${s.stats.fallen}` }),
        el('p', { class: 'muted small', text: '계속 플레이하며 용병단을 키울 수도 있습니다.' }),
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
    const nameInput = el('input', { class: 'input', value: Game.state.guildName, maxlength: 16 });
    openModal(el('div', {},
      el('h2', { text: '메뉴' }),
      el('label', { class: 'small muted', text: '용병단 이름' }),
      el('div', { class: 'row-inline' }, nameInput,
        el('button', { class: 'btn small', text: '변경', onclick: () => {
          const v = nameInput.value.trim();
          if (v) { Game.state.guildName = v; Game.save(); toast('이름을 바꿨습니다.'); renderTop(); }
        } })),
      el('div', { class: 'help' },
        el('h3', { text: '플레이 방법' }),
        el('ul', {},
          el('li', { text: '의뢰 게시판에서 의뢰를 골라 단원을 파견하세요. 의뢰 유형마다 중요한 능력치가 다릅니다.' }),
          el('li', { text: '성공하면 금화와 명성을, 실패하면 부상이나 최악의 경우 단원을 잃습니다.' }),
          el('li', { text: '7일마다 주급을 지급합니다. 금화가 모자라면 단원이 떠나고, 빚이 -200을 넘으면 파산합니다.' }),
          el('li', { text: '명성을 쌓아 등급을 올리면 더 어렵고 보상이 큰 의뢰가 들어옵니다. 목표는 S랭크!' }),
          el('li', { text: '스페이스바로 다음 날로 넘어갈 수 있습니다. 게임은 매일 자동 저장됩니다.' }))),
      el('div', { class: 'modal-actions' },
        el('button', { class: 'btn danger', text: '새 게임', onclick: () => confirmBox('정말 처음부터 다시 시작할까요? 저장된 진행이 지워집니다.', () => { Game.clearSave(); Game.newGame(); Game.emit(); }) }),
        el('button', { class: 'btn primary', text: '닫기', onclick: closeModal }))));
  }

  return { init, render, toast };
})();
