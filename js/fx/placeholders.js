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
    // 가르는 선: 1px 상아 심 + 그 아래 1px 붉은 가장자리, 끝은 50% 머리카락 선. 0 그은 순간 → 1 줄어듦 → 2 끊긴 조각
    cutline: {
      size: [64, 3], origin: [32, 1], frames: 3,
      draw(f, px, run) {
        if (f === 0) {
          run(4, 7, 1, 'key', true); run(56, 59, 1, 'key', true);
          run(8, 55, 1, 'key');
          run(10, 53, 2, 'accent');
          run(14, 49, 0, 'key', true);
        } else if (f === 1) {
          run(12, 51, 1, 'key');
          run(12, 49, 2, 'accent'); run(50, 53, 2, 'body');
        } else {
          [[16, 23], [28, 37], [42, 47]].forEach(([a, b]) => { run(a, b, 1, 'key'); run(a + 1, b, 2, 'accent', true); });
        }
      },
    },
    // 늦게 열리는 갈라짐: 선이 벌어져 어두운 틈이 렌즈 모양으로 열렸다가 조각만 남는다
    split: {
      size: [24, 24], origin: [12, 12], frames: 4,
      draw(f, px, run) {
        const cy = 12;
        if (f === 0) {
          run(2, 21, cy - 1, 'key'); run(3, 20, cy, 'tone'); run(2, 21, cy + 1, 'accent');
          return;
        }
        const hMax = f === 1 ? 2 : f === 2 ? 3 : 4;
        for (let x = 1; x <= 22; x++) {
          const h = Math.round(hMax * Math.sin((Math.PI * (x - 0.5)) / 22));
          const broken = f >= 2 && x % (f === 2 ? 6 : 3) === 0;
          if (f < 3) for (let y = cy - h; y <= cy + h; y++) px(x, y, 'tone', f === 2);
          if (!broken) { px(x, cy - h - 1, 'key', f === 3); px(x, cy + h + 1, 'accent', f === 3); }
        }
        // 양끝 파편
        const s = f;
        px(0 - s + 1, cy - 2 - s, 'key'); px(1 - s + 1, cy - 1 - s, 'key', true);
        px(23 + s - 1, cy + 2 + s, 'key'); px(22 + s - 1, cy + 1 + s, 'key', true);
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
