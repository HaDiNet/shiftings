'use strict';
(function () {
  const url = 'https://www.youtube.com/watch?v=AVlzryCQg8s';
  const pattern = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  let hit = 0;
  let timer;

  function keyUp(event) {
    if (event.key === pattern[hit]) {
      hit++;
    } else {
      if (event.key === 'ArrowUp') {
        if (hit !== 2) {
          hit = 1;
        }
      } else {
        hit = 0;
      }
      return;
    }
    if (hit === pattern.length) {
      document.location.href = url;
    }
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => hit = 0, 2000);
  }

  document.addEventListener('keyup', keyUp);
})();