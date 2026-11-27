// FxPlaceholders — PLACEHOLDER 조각. 코드로 찍은 임시 픽셀이며, 출시용 그림이 아니다.
// ==========================================================================================
//  PLACEHOLDER ONLY. Antigravity 가 그린 키트 조각(art/inbox/fx/captain/blademaster/kit/<piece>)이
//  fx/sig/<owner>/<piece> 시트로 등록되면 FxPlayer 가 그 시트를 쓰고, 여기 것은 더 이상 그려지지 않는다.
//  크기·칸 수·기준점은 키트(docs/plans/effects_design.md §2.2 pieces)와 같다:
//    cutline 64x3 x3f, split 24x24 x4f, band_tail 10x6 x3f, gleam 5x5 x2f.
//  색은 키트 이름(key/body/accent/tone)으로만 받는다. 알파는 0/255 와 50% 단계만 쓴다(§5.4).
// ==========================================================================================
'use strict';

const FxPlaceholders = (() => {
  const cache = new Map();

  // 칸 하나를 찍는 작은 도우미: px(x, y, 색이름, 반투명?)
  function canvasOf(w, h, pal, draw) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const g = c.getContext('2d');
    const px = (x, y, col, half) => {
      if (x < 0 || y < 0 || x >= w || y >= h) return;
      g.globalAlpha = half ? 0.5 : 1;
      g.fillStyle = pal[col];
      g.fillRect(x, y, 1, 1);
    };
    const run = (x0, x1, y, col, half) => { for (let x = x0; x <= x1; x++) px(x, y, col, half); };
    draw(px, run);
    g.globalAlpha = 1;
    return c;
  }

  // 조각 정의: size, origin(그릴 기준점), frames, draw(f, px, run)
  const PIECES = {
    // 가르는 선: 0 지나가는 한 획(칸 전체 머리카락 선, 1~2 프레임) → 1 몸 폭만큼 남은 선(1px 상아 심 + 그 아래 1px 붉은 가장자리, 50% 끝)
    //          → 2 끊긴 조각
    cutline: {
      size: [64, 3], origin: [32, 1], frames: 3,
      draw(f, px, run) {
        if (f === 0) {
          run(0, 3, 1, 'key', true); run(60, 63, 1, 'key', true);
          run(4, 59, 1, 'key');
          run(16, 47, 2, 'accent', true);
        } else if (f === 1) {
          run(10, 13, 1, 'key', true); run(50, 53, 1, 'key', true);
          run(14, 49, 1, 'key');
          run(15, 47, 2, 'accent'); run(48, 50, 2, 'body');
        } else {
          [[16, 23], [28, 37], [42, 47]].forEach(([a, b]) => { run(a, b, 1, 'key'); run(a + 1, b, 2, 'accent', true); });
        }
      },
    },
    // 늦게 열리는 갈라짐: 선의 위 입술(상아)과 아래 입술(붉은색)이 서로 반대로 미끄러지며 어두운 틈이 1~2px 벌어진다
    // (눈 모양 렌즈가 아니라 '어긋나는 단면' — 키트 형태 언어 linear/lateral)
    split: {
      size: [24, 24], origin: [12, 12], frames: 4,
      draw(f, px, run) {
        const cy = 12;
        if (f === 0) { run(2, 21, cy - 1, 'key'); run(3, 20, cy, 'tone'); run(2, 21, cy + 1, 'accent'); return; }
        const sh = f === 1 ? 2 : f === 2 ? 3 : 4;      // 미끄러진 거리
        const gap = f === 1 ? 2 : f === 2 ? 2 : 1;     // 틈 높이
        for (let x = 0; x < 24; x++) {
          const up = x - sh, lo = x + sh;               // 위 입술은 오른쪽, 아래 입술은 왼쪽으로
          const brokenU = f >= 2 && x % (f === 2 ? 7 : 3) === 0, brokenL = f >= 2 && x % (f === 2 ? 5 : 3) === 1;
          if (up >= 2 && up <= 21 && !brokenU) px(x, cy - 1, 'key', f === 3);
          if (lo >= 2 && lo <= 21 && !brokenL) px(x, cy + gap, 'accent', f === 3);
          if (f < 3 && x >= 4 && x <= 19) for (let y = cy; y < cy + gap; y++) px(x, y, 'tone', f === 2);
        }
        // 끝에서 튀는 상아 파편 두 점
        px(23 - (3 - f), cy - 2 - f, 'key', f === 3); px(f - 1 < 0 ? 0 : f - 1, cy + gap + 1 + f, 'key', true);
      },
    },
    // 찢긴 천 조각: 붉은 몸 + 와인 그늘 + 너덜한 끝. 3칸 나풀거림
    band_tail: {
      size: [10, 6], origin: [5, 3], frames: 3,
      draw(f, px, run) {
        if (f === 0) {
          run(1, 7, 2, 'accent'); run(2, 8, 3, 'body'); run(3, 5, 1, 'accent', true); px(9, 4, 'body'); px(8, 4, 'body', true);
        } else if (f === 1) {
          run(3, 6, 1, 'accent'); run(2, 5, 2, 'accent'); run(2, 5, 3, 'body'); run(1, 3, 4, 'body'); px(0, 5, 'body', true);
        } else {
          run(1, 8, 3, 'accent'); run(3, 6, 2, 'accent', true); px(9, 3, 'body');
        }
      },
    },
    // 칼끝 번뜩임: 0 십자 → 1 작은 X
    gleam: {
      size: [5, 5], origin: [2, 2], frames: 2,
      draw(f, px) {
        if (f === 0) {
          px(2, 2, 'key'); px(1, 2, 'key'); px(3, 2, 'key'); px(2, 1, 'key'); px(2, 3, 'key');
          px(0, 2, 'key', true); px(4, 2, 'key', true); px(2, 0, 'key', true); px(2, 4, 'key', true);
        } else {
          px(2, 2, 'key'); px(1, 1, 'key', true); px(3, 3, 'key', true); px(1, 3, 'key', true); px(3, 1, 'key', true);
        }
      },
    },
  };

  function frame(id, f, pal) {
    const d = PIECES[id];
    if (!d) return null;
    const ff = Math.max(0, Math.min(d.frames - 1, f));
    const key = `${id}#${ff}#${pal.key}${pal.body}${pal.accent}${pal.tone}`;
    let c = cache.get(key);
    if (!c) {
      c = canvasOf(d.size[0], d.size[1], pal, (px, run) => d.draw(ff, px, run));
      cache.set(key, c);
    }
    return { img: c, sx: 0, sy: 0, w: d.size[0], h: d.size[1], ox: d.origin[0], oy: d.origin[1], placeholder: true };
  }

  return { frame, has: (id) => !!PIECES[id], spec: (id) => PIECES[id] && { size: PIECES[id].size, origin: PIECES[id].origin, frames: PIECES[id].frames } };
})();
