// 진입점
'use strict';

window.addEventListener('DOMContentLoaded', () => {
  const start = () => {
    if (!Game.load()) Game.newGame();
    UI.init();
    Scene.init(document.getElementById('scene'));
    UI.render();
  };
  // 일러스트 목록을 먼저 받아 온다 (없거나 늦으면 1.5초 뒤 도트로 시작)
  Promise.race([Art.load(), new Promise((r) => setTimeout(r, 1500))]).then(start, start);
});
