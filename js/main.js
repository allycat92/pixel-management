// 진입점
'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const start = () => {
    // 주소 스위치: ?resolve=battle 이면 전투가 결과를 정하는 모드, ?resolve=roll 이면 예전 확률 판정 (저장에 남는다)
    const params = new URLSearchParams(location.search);
    const rq = params.get('resolve');
    // 새 게임은 전투 판정으로 시작한다 (주인 2026-11-27: 통과한 것들을 본게임에). 이어 하는 저장은 저장된 방식 그대로
    if (!Game.load()) { Game.newGame(rq === 'roll' ? 'roll' : 'battle'); Game.save(); }
    if (rq === 'battle' || rq === 'roll') {
      Game.setResolve(rq); Game.save();
      // 주소 스위치는 한 번만 적용하고 주소에서 지운다: 다시 불러와도 메뉴에서 바꾼 방식이 되돌아가지 않게
      params.delete('resolve');
      const q = params.toString();
      try { history.replaceState(null, '', location.pathname + (q ? `?${q}` : '') + location.hash); } catch (e) { /* 주소를 못 바꿔도 게임은 그대로 */ }
    }
    // 이 창에서 '새 게임'을 누를 때의 방식 (주소 ?resolve=roll 로 연 창만 예전 확률 판정)
    UI.init({ newMode: rq === 'roll' ? 'roll' : 'battle' });
    Scene.init(document.getElementById('scene'));
    UI.render();
  };
  // 일러스트 목록을 먼저 받아 온다 (없거나 늦으면 1.5초 뒤 도트로 시작)
  Promise.race([Art.load(), new Promise((r) => setTimeout(r, 1500))]).then(start, start);
});
