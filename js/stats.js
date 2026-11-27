// 전투 능력치 표: 단원의 체력·공격·방어·컨디션, 적 능력치 표(틀 × 등급 × 의뢰 난이도), 예상 전력비, 전투 기록 판정.
// 순수 계산만 한다 — 화면도, Math.random 도, 게임 상태 변경도 없다 (Game 은 읽기만 한다).
// 지금은 '그림자' 단계: 의뢰 결과는 여전히 판정(성공 확률)이 정하고, 이 표로 돌린 전투는 기록만 남긴다.
// 설계: docs/plans/battle_stats/design.md (2~7장), 고친 점: verify_findings.md, 만든 것: stage01_notes.md
'use strict';

const Stats = (() => {
  // ───────── 조정값 ─────────
  // 시작값은 설계서 그대로다. 실제 게임에 맞는 값은 다음 작업(보정)에서 tools/sim/shadow.js 로 재서 정한다.
  // 도구는 스크립트 앞머리에 var STAT_KNOBS = { ENEMY_K: 0.7, KIND_K: { boss: 1.1 }, ARCH: { blob: { hp: 1.6 } } } 처럼 두어 덮어쓴다.
  const KN = {
    K: 0.25,            // 피해 배율 (전투 길이만 바꾼다). 시험: 0.25 는 중앙값 11초 — 목표 18~25초는 0.10~0.12 근처
    HEAL_K: 0.25,       // 치유 배율 (설계: K 와 같은 값)
    ENEMY_K: 0.8,       // 적 전체 배율. 시험: 0.8 은 초반(1~60일) 승률 52~58%, 0.6 은 후반이 너무 쉽다 — 한 값으로는 안 맞는다
    SUPPORT_K: 0.4,     // 지원 부대(의뢰주 병사) 배율. 설계 시작값 0.6 → 검증 3번에 따라 낮춤 (공짜 아군의 몫을 줄인다)
    VILLAGER_K: 0.76,   // 마을 자경단은 지원 병사보다 약하다 (옛 전투의 0.65 / 0.85)
    TRAINEE_K: 0.7,     // 머릿수를 채우는 수습 용병 배율 (레벨은 그 용병단에서 가장 낮은 단원 — 검증 3번)
    EXT_K: 1,           // 외부 용병단 배율
    KIND_K: {},         // 의뢰 갈래별 적 배율: normal / story / capStory / boss / campaign / final (없으면 1)
    CAL_KIND: { monster: 1.291, soldier: 1.1 },   // 예상 전력비 보정 (적 갈래별): 반반 지점(R50) 의 역수 — Codex C7 측정(12판×365일, 8,598전): 괴물 0.774, 병사 0.909
    BANDS: [0.81, 0.93, 1.06, 1.38],        // 예상 단계 경계: 무모 < 열세 < 백중 < 우세 < 압도 (C7: 무모 0.7% · 열세 21% · 백중 52% · 우세 85% · 압도 99.7% 승 — 주인 목표: 우세 85~90, 백중 반반)
    GREAT_HP: 0.65,     // 대성공: 우리 단원 모두 체력이 이 비율 이상 (C7: 우세의 대성공 약 32%)
    GREAT_HEADS: 1,     // 대성공: 의뢰의 권장 인원을 채워 보냈을 때만 (검증 3번). 0 이면 끈다
    RETREAT: 1,         // 후퇴 규칙 (우리 쪽만). 0 이면 끈다
    RETREAT_DOWN: 0.5,  // 우리 단원의 이만큼이 쓰러지고
    RETREAT_RATIO: 0.5, // 남은 체력이 적의 이 비율 아래면 물러난다
    AID_CAP: 0.08,      // 파티 성공률 보정(행운·매의 눈…)이 공격에 주는 덤의 상한 (검증 10번)
    APT_MAX: 1.2,       // 의뢰 유형 적성 상한 (덤만 있다: 1.00~1.20)
    COND_EXP: 1,        // 컨디션 곱을 누르는 지수 (1 = 그대로)
    ELV_SHIFT: 0,       // 적 레벨 전체 이동
    LATE_STEP: 1,       // ★8 부터 별 하나에 오르는 적 레벨
    FINAL_REQ: 3000,    // 최종 결전은 요구 전투력을 이 값으로 나눠 배율을 삼는다 (요구 전투력 공식이 다르다)
    LIMIT: 90,          // 전투 시간 제한(초)
    PIERCE: { fire: 0.5, curse: 0.5, holy: 0.5, bolt: 0.3 },   // 투사체별 방어 관통 (화살·단검·근접은 0)
    // ── 3단계: 전투가 결과를 정하는 모드(Game.RESOLVE === 'battle')에서만 읽는 값. 'roll' 모드에서는 아무 데서도 읽지 않는다 ──
    // 설명과 근거: docs/plans/battle_stats/stage3_notes.md
    BOARD_W: [0.05, 0.12, 0.16, 0.34, 0.33],   // 새 의뢰의 예상 단계 비율 (무모 열세 백중 우세 압도): 쉬운 것부터 벅찬 것까지 늘 보이게
    BOARD_TOP: 3,       // 길드 전력 눈금을 재는 용병단 수 (전력 순 상위). 의뢰마다 그중 하나에 맞춘다 — 약한 용병단에게도 맞는 의뢰가 오른다
    LOSS_PAY: 0.1,      // 실패한 의뢰의 기본 보수 비율 (오늘과 같다)
    LOSS_PAY_SHARE: 0.5,  // + 무찌른 적 전력 비율 × 이 값 (적의 절반을 꺾고 물러나면 보수의 35%)
    RETREAT_MORALE: 0.5,  // 질서 있게 물러난 실패의 사기 하락 배율 (-6 → -3)
    GRACE_DAYS: 7,      // 패배 뒤 이 날수 동안은 주급 탈주·불만 탈주가 없고, 못 준 급료는 빚이 되지 않는다 (유예 주간)
    GRACE_EVERY: 14,    // 유예 주간은 이 날수에 한 번만 새로 열린다
    DEBT_WEEKS: 1,      // 전투 모드의 파산선: 빚이 주급 이만큼(주)을 넘을 때 (최소 300, 오늘의 선). 출격 중인 단원의 주급 한 번으로 파산하지 않게
    BM_FINAL_K: 0.5,    // 전투 모드: 최종 결전의 적 배율 (재앙이 오늘보다 이른 길드 단계에 일어난다 — 길드 성장이 느려서)
    INJ_WIN: 0.6,       // 이긴 전투에서 쓰러진 단원이 다칠 확률 (설계 6장)
    INJ_LOSE: 0.9,      // 진 전투에서 쓰러진 단원이 다칠 확률
    INJ_LOW: 0.3,       // 서 있었지만 체력이 25% 아래인 단원의 가벼운 부상 확률 (1~2일)
    DEATH_P: 0.3,       // 특별한 전투(보스·최종 결전·이야기의 마지막 장)의 대참사에서 쓰러진 단원의 사망 확률 (오늘 값)
    GUILD_FLOOR: 3,     // 사망으로 길드 인원이 이 아래로 내려가지 않는다
    EXT_KEEP: 0.5,      // 진 전투에서 쓰러진 외부 용병단원이 돌아올 확률 (최대 EXT_LOST_CAP 명 잃는다, 이기면 잃지 않는다)
    EXT_LOST_CAP: 2,
    BM_LATE_STEP: 3,    // 전투 모드(일반 의뢰): ★8 부터 별 하나에 오르는 적 레벨 (기본 표는 1 — 후반에는 가장 높은 별도 쉬워 어려운 의뢰가 없었다)
    BM_LOW_K: [1, 0.6, 0.75, 0.9],   // 전투 모드(일반 의뢰): ★1·★2·★3 적 배율 (갓 만든 1레벨 용병단도 ★1 은 이길 만하게. ★4 부터 1)
    // 전투 모드의 예상 보정 (CAL_KIND 에 더 곱한다). 2차 맞춤(stage3 fix): 시드 1~24 × 365일 23,743전(보낸 것 + 살펴본 것)에서, 갈래마다
    // 우세 승률 87%·백중 50% (약하게 열세 17%·압도 99%)에 가장 가까운 곱을 차원(머릿수·적 레벨·틀·갈래)을 번갈아 맞췄다 (표본이 작은 갈래는 1 쪽으로 줄인다)
    BM_CAL_ARCH: { soldier: 0.99, grunt: 1.102, beast: 1.053, brute: 1.162, armored: 1.208, caster: 0.963, blob: 0.983 },
    // 특별한 의뢰 갈래 (표본: 보스 228, 대장 이야기 267, 이야기 455, 결전 2,347, 최종 27)
    BM_CAL_SPECIAL: { boss: 0.894, capStory: 0.982, story: 1.005, final: 1.015, campaign: 0.995 },
    // 머릿수 보정 (검증 1번): 우리 단원(수습·지원 부대 빼고) 1·2·3명일 때 R 에 곱한다 (4명 이상 1). 후퇴 규칙은 우리 단원의 절반이 쓰러지면 물러나므로
    // 한두 명이 나간 판은 한 명만 쓰러져도 끝난다 — 능력치만 보는 margin 은 그것을 모른다 (맞춤 전 R50: 1명 1.07, 2명 1.14, 3명 1.02, 4명 1.00)
    BM_CAL_HEADS: [1, 0.912, 0.909, 1, 1],
    // 적 레벨 보정 (검증 4번 초반): [이 레벨 이하, 곱] 의 계단. 낮은 레벨의 판은 같은 R 에서 더 졌다 (맞춤 전 R50: 레벨 2~9 1.03~1.07, 26~32 0.97~0.98)
    BM_CAL_LV: [[3, 0.937], [9, 0.947], [13, 0.981], [23, 1.005], [999, 1]],
    BM_BOARD_EXTRA: 3,  // 전투 모드: 게시판의 일반 의뢰 칸 + 이만큼 (오늘 3 + 게시판 시설)
    BM_CAP_AHEAD: 4,    // 전투 모드의 별 상한: 길드 등급 + 이 값 (오늘은 +2. 재앙 뒤에는 LATE_MAX_LEVEL 까지) — 상한 안에 벅찬 의뢰가 들게 (검증 3번)
  };
  // 능력치 공식의 계수
  const ATK_W = [1, 0.3, 0.1];            // 공격 = 가장 높은 능력치 + 0.3·둘째 + 0.1·셋째
  const DEF_STR = 0.3, DEF_HP = 0.1;      // 방어 = 0.3·힘 + 0.1·체력 + 방어구
  const ARMOR_DEF = { plate: 3, leather: 1.5, robe: 0.6 };   // 방어구 종류별 방어 (× 등급 배율). 물건에 저장하지 않는다
  // 적 기준 곡선: 레벨 L 의 평균적인 장비 갖춘 병사 [기본, 레벨당, 레벨²당] (n = L - 1)
  const REF = { hp: [28, 5.2, 0.085], atk: [10, 3.2, 0.055], def: [5, 1.25, 0.018] };
  // 괴물 틀 (js/content.js ENEMIES[*].arch)
  const ARCH = {
    grunt:   { hp: 1.0, atk: 1.0,  def: 1.0, speed: 27 },   // 고블린 산적 오크 리자드맨
    beast:   { hp: 0.9, atk: 1.25, def: 0.6, speed: 36 },   // 들늑대 지옥견 하피 거미
    brute:   { hp: 1.3, atk: 0.85, def: 0.7, speed: 22 },   // 트롤 설인 전갈 거인
    armored: { hp: 1.0, atk: 1.0,  def: 2.2, speed: 23 },   // 해골 병사 가고일 데스 나이트
    caster:  { hp: 0.7, atk: 1.15, def: 0.5, speed: 24 },   // 망령 와이번 (원거리, 관통)
    blob:    { hp: 1.9, atk: 0.8,  def: 0.1, speed: 20 },   // 늪 슬라임
  };
  const RANK = {
    minion: { hp: 1,   atk: 1,    def: 1 },
    leader: { hp: 1.6, atk: 1.15, def: 1.1 },   // 병사 부대의 부대장
    big:    { hp: 2.6, atk: 1.4,  def: 1.2 },   // 큰 괴물, 괴물 무리의 우두머리
    boss:   { hp: 7,   atk: 2.0,  def: 1.4 },
  };
  const ELV0 = [0, 1, 2, 3, 5, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18];   // 의뢰 ★ → 적 레벨 (최종 결전 18)
  const GEAR_EQ = { hp: 1.3, atk: 1.3, def: 1.65 };   // 병사의 장비 몫 (레벨 9 에서 다 찬다)
  const BAND_NAMES = ['무모', '열세', '백중', '우세', '압도'];

  const merge = (dst, src) => {
    Object.keys(src || {}).forEach((k) => {
      if (src[k] && typeof src[k] === 'object' && !Array.isArray(src[k]) && dst[k] && typeof dst[k] === 'object') merge(dst[k], src[k]);
      else dst[k] = src[k];
    });
  };
  const KNOBS = Object.keys(KN).concat(['REF', 'ARCH', 'RANK']);   // 덮어쓸 수 있는 이름 (도구가 오타를 잡는 데 쓴다)
  if (typeof STAT_KNOBS !== 'undefined' && STAT_KNOBS) {
    const { REF: r, ARCH: a, RANK: k, ...rest } = STAT_KNOBS;
    merge(KN, rest); merge(REF, r); merge(ARCH, a); merge(RANK, k);
  }
  const ELV = ELV0.map((v, i) => (i <= 7 ? v : ELV0[7] + (i - 7) * KN.LATE_STEP) + (i ? KN.ELV_SHIFT : 0));
  const ELV_BM = ELV0.map((v, i) => (i <= 7 ? v : ELV0[7] + (i - 7) * KN.BM_LATE_STEP) + (i ? KN.ELV_SHIFT : 0));   // 전투 모드의 별 → 적 레벨

  // ───────── 시드 난수 (전투와 같은 mulberry32) ─────────
  function rng(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // 정수 여러 개를 섞어 시드 하나로 (FNV-1a). 0 은 내지 않는다.
  function mix(...xs) {
    let h = 0x811c9dc5;
    xs.forEach((x) => {
      const v = Math.round(x) >>> 0;
      for (let i = 0; i < 4; i++) { h ^= (v >>> (i * 8)) & 0xff; h = Math.imul(h, 0x01000193) >>> 0; }
    });
    return h || 1;
  }
  const clampN = (v, a, b) => Math.max(a, Math.min(b, v));

  // ───────── 단원 능력치 표 ─────────
  const atkOf = (str, dex, int) => { const a = [str, dex, int].sort((x, y) => y - x); return a[0] * ATK_W[0] + a[1] * ATK_W[1] + a[2] * ATK_W[2]; };
  // 방어구의 방어: 종류(base)와 등급(tier)에서 그때그때 계산한다 (고유 장비·세력 대여품도 base 와 tier 가 있다)
  const armorDef = (m) => Object.values(m.equip || {}).reduce((s, it) => s + (it ? (ARMOR_DEF[it.base] || 0) * (TIERS[it.tier] ? TIERS[it.tier].mul : 1) : 0), 0);
  // 컨디션을 곱하기 전의 값
  function raw(m) {
    const str = Game.eff(m, 'str'), dex = Game.eff(m, 'dex'), int = Game.eff(m, 'int'), hp = Game.eff(m, 'maxHp');
    return { hp, atk: atkOf(str, dex, int), def: DEF_STR * str + DEF_HP * hp + armorDef(m) };
  }
  // 의뢰 유형 적성: 그 유형이 높이 치는 능력치를 가진 단원에게 주는 덤 (1.00 ~ APT_MAX, 벌은 없다)
  const WAVG = (() => {
    const ks = Object.keys(QUEST_TYPES), o = { str: 0, dex: 0, int: 0 };
    ks.forEach((k) => ['str', 'dex', 'int'].forEach((a) => { o[a] += QUEST_TYPES[k].weights[a] / ks.length; }));
    return o;
  })();
  function aptOf(m, type) {
    const w = QUEST_TYPES[type].weights, a = { str: Game.eff(m, 'str'), dex: Game.eff(m, 'dex'), int: Game.eff(m, 'int') };
    const num = a.str * w.str + a.dex * w.dex + a.int * w.int, den = a.str * WAVG.str + a.dex * WAVG.dex + a.int * WAVG.int;
    return clampN(1 + ((den ? num / den : 1) - 1) * 0.5, 1, KN.APT_MAX);
  }
  // 파티 성공률 보정(행운, 매의 눈, 숲의 가호, 궁수 계통 효과…)을 전투의 덤으로: 공격에만 한 번, 상한이 있다
  const aidOf = (success) => 1 + clampN((success || 0) / 0.9, 0, KN.AID_CAP);
  // 컨디션의 부분들: Game.power() 의 모든 % 보정을 같은 값으로 옮긴다.
  // ctx 가 없으면 개인 몫(특성·사기·피로)만, 있으면 파티(bond)·용병단(lead)·의뢰(apt)·파티 효과(aid)까지.
  function parts(m, ctx = {}) {
    const type = ctx.type || null, party = ctx.party || null, p = {};
    let t = 1;
    if (m.trait === 'brave') t *= 1.1;
    if (m.trait === 'coward') t *= 0.9;
    if (m.trait === 'berserker') t *= 1.25;
    if (m.trait === 'arcane') t *= type === 'magic' ? 1.35 : 1.1;
    if (m.trait === 'royalguard' && ['defense', 'warDefense', 'battle'].includes(type)) t *= 1.2;
    if (m.trait === 'northknight') t *= 1.05;
    if (m.trait === 'warcry') t *= 1.15;
    if (m.awakened) t *= 1.15;
    let bonus = 0;
    Game.classChain(m).forEach((c) => {
      const self = c.fx && c.fx.self;
      if (self) bonus += ((self.all || 0) + ((type && self.types && self.types[type]) || 0)) * (c.scale || 1);
    });
    p.trait = t * (1 + bonus);
    p.morale = Game.moraleState(m).mul;
    p.fatigue = Game.fatigueState(m).mul;
    p.bond = 1;
    if (party) {
      const others = party.filter((x) => x.id !== m.id);
      const friends = others.filter((x) => Game.rel(m, x) >= FRIEND_REL).length;
      const rivals = others.filter((x) => Game.rel(m, x) <= RIVAL_REL).length;
      p.bond = (1 + 0.08 * Math.min(friends, 2)) * Math.pow(0.9, rivals) * (party.some((x) => x.trait === 'commander') ? 1.08 : 1);
    }
    p.lead = ctx.company ? Game.cohesionMul(ctx.company) * Game.leaderMul(ctx.company, type, ctx.members, ctx.contract) * Game.memberLeadMul(ctx.company, m, ctx.members) : 1;
    p.apt = type ? aptOf(m, type) : 1;
    p.aid = ctx.aid || 1;
    return p;
  }
  // 능력치 표: 체력·공격에는 컨디션(mul)을 한 번 곱하고, 방어에는 곱하지 않는다. aid 는 공격에만 따로 곱한다.
  // -> { hp, atk, def, mul, parts: { trait, morale, fatigue, bond, lead, apt, aid }, raw: { hp, atk, def } }
  function sheet(m, ctx) {
    const r = raw(m), p = parts(m, ctx);
    let mul = p.trait * p.morale * p.fatigue * p.bond * p.lead * p.apt;
    if (KN.COND_EXP !== 1) mul = Math.pow(mul, KN.COND_EXP);
    return { hp: Math.round(r.hp * mul), atk: +(r.atk * mul * p.aid).toFixed(1), def: +r.def.toFixed(1), mul: +mul.toFixed(3), parts: p, raw: r };
  }

  // ───────── 적 · 병사 ─────────
  const ref = (L) => { const n = L - 1, q = (c) => c[0] + c[1] * n + c[2] * n * n; return { hp: q(REF.hp), atk: q(REF.atk), def: q(REF.def) }; };
  // 괴물: 기준 곡선(레벨) × 틀 × 등급 × k
  function enemy(arch, L, rank = 'minion', k = 1) {
    const e = ref(L), a = ARCH[arch] || ARCH.grunt, r = RANK[rank] || RANK.minion;
    return { hp: Math.round(e.hp * a.hp * r.hp * k), atk: +(e.atk * a.atk * r.atk * k).toFixed(1), def: +(e.def * a.def * r.def * k).toFixed(1) };
  }
  // 병사(분쟁 의뢰의 적, 지원 부대, 외부 용병단, 수습 용병): 직업의 기본·성장 + 장비 몫. 11레벨부터는 전직 갈래의 평균.
  function generic(cls, L, rank = 'minion', k = 1) {
    const C = CLASSES[cls] || CLASSES.warrior, a = { str: C.base.str, dex: C.base.dex, int: C.base.int, hp: C.base.hp };
    const add = (g, n, w = 1) => Object.keys(a).forEach((key) => { a[key] += (g[key === 'hp' && g.maxHp != null ? 'maxHp' : key] || 0) * n * w; });
    add(C.growth, L - 1);
    if (L > 10 && PROMOTIONS[cls]) {
      PROMOTIONS[cls].forEach((p) => {
        add(p.bonus, 1, 0.5); add(p.growth, Math.min(L, 20) - 10, 0.5);
        if (L > 20) MASTERS[p.key].forEach((m) => { add(m.bonus, 1, 0.25); add(m.growth, L - 20, 0.25); add(p.growth, L - 20, 0.125); });
      });
    }
    const R = RANK[rank] || RANK.minion, g = Math.min(1, (L - 1) / 8), ge = (x) => 1 + (x - 1) * g;
    return { hp: Math.round(a.hp * ge(GEAR_EQ.hp) * R.hp * k), atk: +(atkOf(a.str, a.dex, a.int) * ge(GEAR_EQ.atk) * R.atk * k).toFixed(1),
      def: +((DEF_STR * a.str + DEF_HP * a.hp) * ge(GEAR_EQ.def) * R.def * k).toFixed(1) };
  }
  // 괴물의 공격 방식 (3단계 전투 모드): 그림 틀(tpl)이 아니라 능력치 틀(arch)이 정한다 — 주술(caster)만 원거리.
  // 옛 방식(js/battle.js monsterSkills)은 그림 틀을 따라 하피·가고일(drake)·마족 전사(demon)가 불·저주를 쏘고, 늪의 마녀(ghost 보스)는 근접이었다.
  const SHOT_OF_TPL = { ghost: 'curse', drake: 'fire', demon: 'curse' };   // 원거리일 때 투사체 모양만 그림 틀을 따른다
  function monsterSkills(u) {
    const d = ENEMIES[u.mon] || {}, tpl = d.tpl, arch = u.arch || d.arch || 'grunt';
    const shot = SHOT_OF_TPL[tpl] || 'curse';
    // 보스도 틀을 따른다 (검증 7번): 주술 보스(늪의 마녀)는 기본 공격부터 쏘고 숨결도 쏜다. 주술이 아닌 보스의 큰 기술은 가까이서 휩쓰는 범위 공격이다 —
    // 이름만 그림 틀을 따른다 (고룡 이그니스·마왕 베르녹스는 brute 라 숨결을 멀리서 쏘지 않는다)
    const basic = arch === 'caster' ? SK.shot('공격', shot, 1, 70, 1.4) : SK.melee('공격', 1, 1.0, { range: u.bigMon ? 16 : 11 });
    if (u.boss) return [basic, arch === 'caster' ? SK.shot('파멸의 숨결', shot === 'fire' ? 'fire' : 'curse', 1.6, 70, 7, { aoe: 26, stun: 0.6 })
      : SK.melee(tpl === 'drake' ? '화염 숨결' : tpl === 'demon' ? '마왕의 강타' : '대지 분쇄', 1.8, 7, { aoe: 24, stun: 0.6, range: 18 })];
    if (u.bigMon) return [basic, SK.melee('포효', 1.1, 9, { aoe: 20, stun: 0.4, range: 16 })];
    if (u.mon === '거대 거미') return [basic, SK.shot('거미줄 뿜기', 'web', 0.4, 70, 8, { slow: 2.5 })];
    return [basic];
  }
  // 의뢰 갈래 (KIND_K, 표 묶음용)
  const kindOf = (q) => (q.final ? 'final' : q.campaign ? 'campaign' : q.boss ? 'boss' : q.story ? 'story' : q.capStory ? 'capStory' : 'normal');
  const nominalReq = (q) => 24 * Math.pow(1.4, q.level - 1) * 1.175 * (q.boss ? 1.3 : 1);
  // 의뢰 → 적 레벨과 배율: ★ 이 레벨을 정하고, 요구 전투력의 나머지(±10% 굴림, 규모, 적대 영토 ×1.2, 결전 ×1.05)가 k 로 간다.
  // bm: 전투 모드 (일반 의뢰만: ★8+ 의 레벨 간격 BM_LATE_STEP, ★1~3 배율 BM_LOW_K)
  function scale(q, effReq, bm) {
    const req = effReq || q.req;
    const base = clampN(q.final ? req / KN.FINAL_REQ : req / nominalReq(q), 0.7, 1.6);
    const star = q.final ? 14 : clampN(q.level, 1, 14);
    // 전투 모드의 별 표는 일반 의뢰에만: 특별한 의뢰(이야기·보스·결전·최종)의 별은 등급·지방이 정하므로 옛 표 그대로 둔다
    const normal = bm && kindOf(q) === 'normal';
    const lv = Math.max(1, (normal ? ELV_BM : ELV)[star]);
    const low = normal ? (KN.BM_LOW_K[star] || 1) : bm && q.final ? KN.BM_FINAL_K : 1;
    return { lv, k: base * KN.ENEMY_K * (KN.KIND_K[kindOf(q)] || 1) * low, kraw: base };
  }
  // 이긴 것으로 치는 조건: field = 제한 시간 안에 적을 무너뜨려야 한다, hold = 끝까지 버텨도 이긴다
  const ruleOf = (q) => (q.boss || q.final ? 'field' : (QUEST_TYPES[q.type] && QUEST_TYPES[q.type].rule) || 'field');

  // ───────── 예상 전력비 (전술·위치·시드 없이 능력치와 스킬 빈도만으로) ─────────
  const skillsOf = (u) => u.sk || (u.mon
    ? [{ tgt: 'enemy', dmg: 1, cd: 1.0 }].concat(u.boss ? [{ tgt: 'enemy', dmg: 1.7, cd: 7, aoe: 24 }] : u.bigMon ? [{ tgt: 'enemy', dmg: 1.1, cd: 9, aoe: 20 }] : [])
    : [CLASS_SKILLS[u.cls || 'warrior'].b]);
  function unitRates(u) {
    let dmg = 0, heal = 0, pierce = 0, w = 0;
    skillsOf(u).forEach((sk) => {
      if (sk.tgt === 'enemy') { const r = sk.dmg * (sk.hits || 1) * (sk.aoe ? 1.4 : 1) / sk.cd; dmg += r; pierce += (KN.PIERCE[sk.shot] || 0) * r; w += r; }
      else if (sk.tgt === 'hurt') heal += sk.heal * (sk.aoe ? 1.8 : 1) / sk.cd;
    });
    return { dmg, heal, pierce: w ? pierce / w : 0 };
  }
  function sideOf(us, foes, kFoe, kSelf) {
    const hpF = foes.reduce((a, f) => a + f.st.hp, 0) || 1;
    const defF = foes.reduce((a, f) => a + f.st.def * f.st.hp, 0) / hpF * kFoe;
    const atkF = foes.reduce((a, f) => a + f.st.atk, 0) / (foes.length || 1) * kFoe;
    let dps = 0, ehp = 0, hps = 0;
    us.forEach((u) => {
      const r = u.r, A = u.st.atk * kSelf, D = u.st.def * kSelf;
      dps += KN.K * A * r.dmg * 1.07 * (A / (A + defF * (1 - r.pierce)));
      hps += KN.HEAL_K * A * r.heal;
      ehp += u.st.hp * kSelf / (atkF / (atkF + D));
    });
    return { dps, ehp, hps };
  }
  // 적을 몇 배로 키워야 반반이 되는가 (1 보다 크면 우리가 세다)
  function margin(groups) {
    const sideUnits = (side) => groups.filter((g) => g.side === side).flatMap((g) => g.units).map((u) => ({ st: u.st, r: unitRates(u) }));
    const A = sideUnits(0), B = sideUnits(1);
    if (!A.length || !B.length) return A.length ? 20 : 0.05;
    const rho = (k) => {
      const a = sideOf(A, B, k, 1), b = sideOf(B, A, 1, k);
      const T = clampN(Math.min(b.ehp / Math.max(1e-6, a.dps), a.ehp / Math.max(1e-6, b.dps)), 6, 60);
      return (a.dps * (a.ehp + a.hps * T * 0.6)) / (b.dps * (b.ehp + b.hps * T * 0.6));
    };
    let lo = 0.05, hi = 20;
    for (let i = 0; i < 30; i++) { const k = Math.sqrt(lo * hi); if (rho(k) >= 1) lo = k; else hi = k; }
    return Math.sqrt(lo * hi);
  }
  const foeKind = (spec) => (spec.groups.some((g) => g.kind === 'foe' && g.units[0] && g.units[0].mon) ? 'monster' : 'soldier');
  const bandOf = (R) => KN.BANDS.filter((e) => R >= e).length;   // 0 무모 … 4 압도
  // 굳힌 편성 → { R, band }. R = 1 이 '반반'이 되도록 CAL_KIND 로 맞춘다 (보정 전에는 1).
  // 전투 모드의 편성(spec.bm)은 적 틀·의뢰 갈래·머릿수·적 레벨 보정을 더한다 (BM_CAL_ARCH, BM_CAL_SPECIAL, BM_CAL_HEADS, BM_CAL_LV)
  function forecast(spec) {
    let cal = KN.CAL_KIND[foeKind(spec)] || 1;
    if (spec.bm) {
      const foe = spec.groups.find((g) => g.kind === 'foe'), lead = foe && foe.units[0];
      cal *= KN.BM_CAL_ARCH[(lead && lead.arch) || 'soldier'] || 1;
      cal *= KN.BM_CAL_SPECIAL[spec.kind] || 1;
      const n = spec.groups.filter((g) => g.kind === 'own' || g.kind === 'ext').reduce((a, g) => a + g.units.filter((u) => !u.recruit).length, 0);
      cal *= KN.BM_CAL_HEADS[Math.min(n, KN.BM_CAL_HEADS.length - 1)] || 1;
      const lvStep = KN.BM_CAL_LV.find(([x]) => (spec.lv || 1) <= x);
      cal *= lvStep ? lvStep[1] : 1;
    }
    const R = +(margin(spec.groups) * cal).toFixed(3);
    return { R, band: bandOf(R) };
  }

  // ───────── 전투 기록 판정 ─────────
  // '우리' = 출격한 직속·외부 용병단의 단원. 지원 부대, 머릿수를 채운 수습 용병, 배신한 용병단은 세지 않는다.
  // rec.units 는 편성(spec) 순서대로 한 줄씩 [결말, 체력%, 쓰러진 틱, 준 피해, 받은 피해, 처치, 치유]. 결말: 0 무사, 1 쓰러짐, 2 물러남
  function oursOf(spec, rec) {
    const out = [];
    let i = 0;
    spec.groups.forEach((g) => g.units.forEach((u) => {
      const row = rec.units[i++];
      if ((g.kind === 'own' || g.kind === 'ext') && !g.betray && !u.recruit) {
        out.push({ id: u.id || 0, companyId: g.companyId, ext: g.kind === 'ext', leader: !!u.leader, fate: row[0], hp: row[1], dealt: row[3] });
      }
    }));
    return out;
  }
  // -> { outcome: 'great'|'success'|'fail'|'disaster', won, ours, down, standing, fled, low, mvp }
  function judge(spec, rec, mods = {}) {
    const ours = oursOf(spec, rec), won = rec.winner === 0;
    const down = ours.filter((o) => o.fate === 1).length, standing = ours.length - down;
    const greatHp = 100 * KN.GREAT_HP / (mods.great || 1);
    const full = !KN.GREAT_HEADS || spec.need == null || spec.heads >= spec.need;
    let outcome;
    if (won) outcome = down === 0 && full && ours.every((o) => o.hp >= greatHp) ? 'great' : 'success';
    else outcome = standing > 0 || mods.noDisaster ? 'fail' : 'disaster';
    const best = ours.filter((o) => o.id).sort((a, b) => b.dealt - a.dealt)[0];
    return { outcome, won, ours: ours.length, down, standing, fled: ours.filter((o) => o.fate === 2).length,
      low: ours.filter((o) => o.fate === 0 && o.hp < 25).length, mvp: best ? best.id : 0 };
  }

  // 무찌른 적 전력 비율 (0~1): 적의 최대 체력 가중, 쓰러진 적은 전부, 서 있거나 달아난 적은 깎인 만큼 (3단계: 실패한 의뢰의 보수)
  function foeShare(spec, rec) {
    let tot = 0, gone = 0, i = 0;
    spec.groups.forEach((g) => g.units.forEach((u) => {
      const row = rec.units[i++];
      if (g.side !== 1) return;   // 적 부대만 (배신한 용병단은 편성에서 아군 쪽이라 세지 않는다)
      const hp = u.st.hp;
      tot += hp; gone += row[0] === 1 ? hp : hp * (1 - row[1] / 100);
    }));
    return tot ? clampN(gone / tot, 0, 1) : 0;
  }

  return { KN, KNOBS, REF, ARCH, RANK, ELV, ELV_BM, ARMOR_DEF, BAND_NAMES, rng, mix, raw, parts, sheet, aptOf, aidOf, armorDef, ref, enemy, generic,
    kindOf, nominalReq, scale, ruleOf, margin, foeKind, bandOf, forecast, oursOf, judge, monsterSkills, foeShare };
})();
