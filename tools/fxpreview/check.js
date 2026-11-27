#!/usr/bin/env node
// FX 파일럿 검사 (작은 것만): node tools/fxpreview/check.js
// 1) js/fx/skel.js 에 색 리터럴·그림 경로·Math.random 이 없는가 (§1.2-1: 뼈대는 보이지 않는 구조만)
// 2) 시그니처 스펙의 style 매개변수가 전부 직접 적혔는가 (§1.2-4)
// 3) 스펙이 참조하는 조각이 키트 pieces 안에 있는가, 색 이름이 키트에 있는가
// 4) 같은 시드 → 같은 배치(결정론)
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..', '..');
const rd = (p) => fs.readFileSync(path.join(root, p), 'utf8');
let bad = 0;
const fail = (m) => { bad++; console.log(`FAIL ${m}`); };
const ok = (m) => console.log(`ok   ${m}`);

// 1
const skelSrc = rd('js/fx/skel.js');
const code = skelSrc.split('\n').map((l) => l.replace(/\/\/.*$/, '')).join('\n');
const lits = [/#[0-9a-fA-F]{3,8}\b/, /rgba?\(/, /hsla?\(/, /'fx\//, /assets\//, /Math\.random/];
const hits = lits.filter((re) => re.test(code));
hits.length ? fail(`skel.js has forbidden literals: ${hits.join(' ')}`) : ok('skel.js: no colour / art-path literals, no Math.random');

// 2
const ctx = { console, module: undefined };
vm.createContext(ctx);
vm.runInContext(`${skelSrc}\n;${rd('js/fx/player.js')}\n;this.FxSkel = FxSkel; this.FxPlayer = FxPlayer;`, ctx);
const specP = 'assets/fx/sig/captain/blademaster/hoejeon-begi.json';
const spec = JSON.parse(rd(specP));
const kit = JSON.parse(rd('assets/fx/kits/captain/blademaster.json'));
const miss = ctx.FxPlayer.lint(spec);
miss.length ? fail(`${specP}: style params left to defaults: ${miss.join(', ')}`) : ok(`${specP}: every style param written out`);

// 3
const pieces = new Set(kit.pieces.map((p) => p.id));
const cols = new Set([...Object.keys(kit.colours), ...Object.keys((kit.ultimate && kit.ultimate.colours) || {})]);
spec.layers.forEach((L) => {
  if (L.piece && !pieces.has(L.piece)) fail(`layer ${L.id}: piece ${L.piece} not in kit`);
  if (L.colour && !cols.has(L.colour)) fail(`layer ${L.id}: colour ${L.colour} not in kit`);
});
Object.entries(spec.screen || {}).forEach(([k, v]) => { if (v && v.colour && !cols.has(v.colour)) fail(`screen.${k}: colour ${v.colour} not in kit`); });
const scr = Object.keys(spec.screen || {}).map((k) => (k === 'shake' ? 'shake.x' : k === 'freeze' ? 'hitstop' : k));
const allowed = new Set([...(kit.screen.allowed || []), ...((spec.tier || '').startsWith('ultimate') ? kit.ultimate.allowed : [])]);
const off = scr.filter((s) => !allowed.has(s));
off.length ? fail(`screen beats outside the kit vocabulary: ${off.join(', ')}`) : ok(`screen beats within kit vocabulary (${spec.tier})`);
if (!bad) ok('pieces and colour names resolve in the kit');

// 4
const scene = {
  caster: { x: 100, y: 100, face: 1, box: { x0: 90, y0: 40, x1: 112, y1: 100 }, tip: [130, 80] },
  victims: [0, 1, 2, 3, 4, 5].map((i) => ({ x: 140 + i * 20, y: 90 + (i % 3) * 10, box: { x0: 130 + i * 20, y0: 30, x1: 150 + i * 20, y1: 90 + (i % 3) * 10 } })),
};
const a = ctx.FxPlayer.create(spec, kit, scene, { seed: 7 }), b = ctx.FxPlayer.create(spec, kit, scene, { seed: 7 }), c = ctx.FxPlayer.create(spec, kit, scene, { seed: 8 });
const sig = (x) => JSON.stringify([x.marks, x.timeline().events, x.camera(0.72 / x.rate)]);
sig(a) === sig(b) ? ok('same seed → same marks/timing/shake') : fail('same seed gave different output');
sig(a) !== sig(c) ? ok('different seed → different variation') : fail('seed has no effect');
const ys = a.marks.map((m) => m.y - 0);
new Set(a.marks.map((m, i) => (m.y - scene.victims[i].box.y0) / (scene.victims[i].box.y1 - scene.victims[i].box.y0)).map((k) => k.toFixed(2))).size === ys.length
  ? ok('each victim cut at a different body height') : fail('two victims share a cut height');

console.log(bad ? `\n${bad} problem(s)` : '\nall checks passed');
process.exitCode = bad ? 1 : 0;
