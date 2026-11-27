#!/usr/bin/env node
// FX 미리보기 캡처 (고정 시드 → 같은 GIF). 서버를 먼저 띄운다: python3 tools/serve.py 8765
// 사용: node tools/fxpreview/capture.js OUT_DIR [--url http://localhost:8765/tools/fxpreview/] [--seed 7] [--bg plains] [--fps 50]
// 결과: OUT_DIR/frames_1x/*.png, frames_4x/*.png, fx_1x.gif, fx_4x.gif (+ _x2 확대본), keys/*.png (주요 순간, fx 시각 기준)
'use strict';
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const out = path.resolve(args[0] || 'fxcapture');
const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
const url = opt('url', 'http://localhost:8765/tools/fxpreview/');
const seed = +opt('seed', 7), bg = opt('bg', 'plains'), fps = +opt('fps', 50);

// 주요 순간 (fx 시계 초, 1× 기준) — 스펙 hoejeon-begi 의 단계에 맞춘 이름
const KEYS = [
  ['00_rest', 0.02], ['01_dim_ready', 0.14], ['02_spin', 0.30], ['03_still_gleam', 0.49], ['04_cut', 0.605],
  ['05_hitstop', 0.66], ['06_split_open', 0.745], ['07_split_wide', 0.84], ['08_scraps', 1.15], ['09_release', 1.95],
];

async function grab(page, file) {
  const data = await page.evaluate(() => document.getElementById('stage').toDataURL('image/png'));
  fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
}
function gif(dir, outFile, scale) {
  const vf = `${scale > 1 ? `scale=iw*${scale}:ih*${scale}:flags=neighbor,` : ''}split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=none`;
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(dir, 'f%04d.png'), '-vf', vf, '-loop', '0', outFile]);
  if (r.status !== 0) throw new Error(`ffmpeg failed: ${r.stderr}`);
}

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1500, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(() => window.FXP.ready);
  await page.screenshot({ path: path.join(out, 'page.png') });

  for (const speed of [1, 4]) {
    await page.evaluate((o) => window.FXP.set(o), { speed, seed, bg });
    const dur = await page.evaluate(() => window.FXP.duration());
    const dir = path.join(out, `frames_${speed}x`);
    fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const n = Math.ceil((dur + 0.4) * fps);
    for (let k = 0; k < n; k++) {
      await page.evaluate((t) => window.FXP.renderAt(t), Math.min(dur, k / fps));
      await grab(page, path.join(dir, `f${String(k).padStart(4, '0')}.png`));
    }
    gif(dir, path.join(out, `fx_${speed}x.gif`), 1);
    gif(dir, path.join(out, `fx_${speed}x_x2.gif`), 2);
    console.log(`speed ${speed}x: ${n} frames, ${dur.toFixed(3)}s real`);
  }

  await page.evaluate((o) => window.FXP.set(o), { speed: 1, seed, bg });
  const kd = path.join(out, 'keys');
  fs.mkdirSync(kd, { recursive: true });
  for (const [name, t] of KEYS) {
    await page.evaluate((x) => window.FXP.renderAt(x), t);
    await grab(page, path.join(kd, `${name}.png`));
  }
  await browser.close();
  if (errors.length) { console.error('page errors:\n' + errors.join('\n')); process.exitCode = 1; }
  console.log(`done → ${out}`);
})();
