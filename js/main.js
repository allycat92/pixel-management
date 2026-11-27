// 진입점
'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const start = () => {
    if (!Game.load()) Game.newGame();
    // 시험용 스위치: 주소에 ?resolve=battle 이면 전투가 결과를 정하는 모드, ?resolve=roll 이면 오늘의 판정 (저장에 남는다)
    const rq = new URLSearchParams(location.search).get('resolve');
    if (rq === 'battle' || rq === 'roll') { Game.setResolve(rq); Game.save(); }
    UI.init();
    Scene.init(document.getElementById('scene'));
    UI.render();
  };
  // 일러스트 목록을 먼저 받아 온다 (없거나 늦으면 1.5초 뒤 도트로 시작)
  Promise.race([Art.load(), new Promise((r) => setTimeout(r, 1500))]).then(start, start);
});
