// 진입점
'use strict';

window.addEventListener('DOMContentLoaded', () => {
  if (!Game.load()) Game.newGame();
  UI.init();
  Scene.init(document.getElementById('scene'));
  UI.render();
});
