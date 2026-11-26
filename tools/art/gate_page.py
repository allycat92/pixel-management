#!/usr/bin/env python3
"""Gate 1 of the motion plan: one self-contained HTML page that asks viewers to find the contact frame of mannequin sequences.

  python3 tools/art/gate_page.py OUT.html SET [SET ...] [--reps N] [--no-decoy] [--speed 1] [--zoom 3] [--title TEXT]

SET is one mannequin sequence, optionally followed by @<contact frame index, 0-based>:
  art/inbox/guides/atk__class_warrior/atk__class_warrior.aseprite        a delivered set: frames, durations from the file,
                                                                         frame names + contact from motion_bible.json / motion_chars.json
  /work/frames                                                           a folder of frame PNGs (f<NN>_<name>.png as receive.py and
                                                                         check_skeleton.py --export write them) with the
                                                                         pose_measured.json they write beside them: the set id
                                                                         and durations_ms come from that file (not the folder name)
  art/requests/guides/run_base/v1/run_base.aseprite@0                    a stand-in (no bible entry): name the contact frame yourself
  art/requests/guides/run_base/v1/layers@0                               a run8.py / walk8.py layers folder (R<n>_<layer>.png); its
                                                                         frame time is nominal_ms of the pose.json one folder up
A folder whose frame times are unknown (no pose_measured.json durations, no pose.json nominal_ms, no motion plan for its set id)
is a FAIL unless --ms gives the time: the page never plays a guessed 100 ms.
The .aseprite is exported with the headless Aseprite (tools/art/ase_headless.sh, or --aseprite-exe / ASEPRITE_PATH): visible
layers only, so the hidden joints layer is left out. #FF00FF and transparent pixels are the background.

What the page does (docs/plans/2026-11-26_motion_frames.md section 6 (2) "첫 관문"):
  - every frame at game size (x --scale 0.1654, box-filtered, alpha cut at 50 % so edges stay crisp), shown x --zoom with
    image-rendering: pixelated on a dark floor; no VFX, no shake, no flash; planned ms / 1.3 (1x real time; --speed scales it)
  - trials in a random order per session: each set once as planned and once as a DECOY (the contact frame swapped with a
    neighbour, so its silhouette arrives one frame early or late, and every duration scaled by a random 0.8-1.25). A trial plays
    the sequence once (--reps N: 1..N times, random 0.4-1.4 s pauses between plays) after a random 0.6-1.4 s lead-in on a NEUTRAL
    frame: the settle frame (else the last frame, else frame 0), never the contact frame or a frame next to it (those are the
    frames a decoy moves); with no such frame the floor stays empty during the lead-in. The lead-in frame is the same frame in the
    planned play and in the decoy, so it tells nothing about the contact (a hit set's frame 0 IS the contact K1)
  - then the frames are laid out as a strip at game size (played order, numbered, no names) with a slider / arrow keys, and the
    viewer picks the frame where the blow landed
  - at the end: the viewer's picks, a JSON blob to copy (page id, set, decoy or not, played order, expected and picked index), and a
    box that merges blobs of several viewers into a verdict per set. Only PAIRED sessions count: per set, a session counts when it
    has BOTH a planned and a decoy answer for that set (a planned answer alone cannot tell a silhouette reader from a viewer who
    follows the beat, so stripping decoys from the pasted JSON cannot pass a set); the others are listed as "not counted (no
    decoy answer)". PASS when at least 5 paired sessions took part and >= 80 % of them (4 of 5) got BOTH plays right in the
    same session - the contact frame or a neighbour on the planned play and the moved side on the decoy (they read the
    silhouette, not the beat; GPT QA 29c4235: two half-right sessions must not add up to a pass); fewer
    than 5 paired sessions is FAIL "not enough paired sessions" (the picks are listed). A set without a decoy (--no-decoy, or a
    one-frame set) counts planned answers as before. Blobs are counted once per session id AND once per trials content: the same
    blob pasted twice, or pasted again with its session id (or viewer) edited, is one viewer.
  - the page id is a hash of the sets (id, ms, contact, frames); a --no-decoy page adds "-nodecoy" to it, so its blobs never count
    on a gate-1 page (with decoys) made from the same sets and the other way round, and every verdict of a --no-decoy page says
    "no decoys - not a gate-1 result" (it measures only whether the contact frame is found, not whether the silhouette is read).
Exit code 1 when a set cannot be read.
"""
import argparse
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPECS = os.path.join(ROOT, 'tools', 'art', 'specs')
HEADLESS = os.path.join(ROOT, 'tools', 'art', 'ase_headless.sh')
KEY = (255, 0, 255)
FLOOR = 870                     # the sole line of a 384x1024 mannequin frame (art/requests/guides/SPEC.md section 3)
SET_RE = re.compile(r'^(atk|hit|idle)__([a-z0-9][a-z0-9_-]*)$')
LAYER_ORDER = ('Background', 'cloth_back', 'weapon_back', 'arm_far', 'shield', 'leg_far', 'leg_near', 'torso', 'cloth_front', 'head',
               'weapon_front', 'arm_near')


class Fail(Exception):
    pass


def aseprite(exe, *args):
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    env.pop('WAYLAND_DISPLAY', None)
    r = subprocess.run([exe, '--batch', *args], stdin=subprocess.DEVNULL, capture_output=True, timeout=300, env=env)
    if r.returncode:
        raise Fail(f'{exe} {" ".join(args[:2])}: exit {r.returncode}: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:])
    return r


def load_aseprite(src, exe, work):
    """-> (frames RGBA, durations ms, frame tags [(name, from, to)]); visible layers only (the joints layer is hidden)"""
    data = os.path.join(work, 'data.json')
    aseprite(exe, src, '--list-tags', '--sheet', os.path.join(work, 'sheet.png'), '--data', data, '--format', 'json-array')
    with open(data, encoding='utf-8') as f:
        meta = json.load(f)
    durs = [int(fr['duration']) for fr in meta['frames']]
    tags = [(t['name'], int(t['from']), int(t['to'])) for t in meta.get('meta', {}).get('frameTags', [])]
    aseprite(exe, src, '--save-as', os.path.join(work, 'f{frame}.png'))
    frames = []
    for i in range(len(durs)):
        p = os.path.join(work, f'f{i}.png')
        if not os.path.exists(p) and len(durs) == 1:
            p = os.path.join(work, 'f.png')
        if not os.path.exists(p):
            raise Fail(f'Aseprite did not export frame {i} of {src}')
        frames.append(Image.open(p).convert('RGBA'))
    return frames, durs, tags


def load_folder(src, ms):
    """f<NN>_<name>.png files, a run8.py / walk8.py layers folder (R<n>_<layer>.png / W<n>_<layer>.png), or any *.png in name order
    -> (frames, durations, names, durations known, pose_measured.json contents or {}).
    Durations are known from pose_measured.json durations_ms (receive.py / check_skeleton.py --export), a layers folder's
    ../pose.json nominal_ms, or --ms (which wins)."""
    files = sorted(fn for fn in os.listdir(src) if fn.lower().endswith('.png'))
    layered = {}
    for fn in files:
        m = re.match(r'^([RW])(\d+)_([a-z_]+)\.png$', fn)
        if m and m.group(3) in LAYER_ORDER + ('joints',):
            layered.setdefault((m.group(1), int(m.group(2))), {})[m.group(3)] = fn
    durs_file = os.path.join(src, 'pose_measured.json')
    meta = {}
    if os.path.exists(durs_file):
        with open(durs_file, encoding='utf-8') as f:
            meta = json.load(f)
    known = meta.get('durations_ms')
    if layered:
        frames, names = [], []
        for (t, n) in sorted(layered):
            parts = layered[(t, n)]
            im = Image.new('RGBA', Image.open(os.path.join(src, next(iter(parts.values())))).size, (0, 0, 0, 0))
            for ln in LAYER_ORDER:                      # joints is never drawn
                if ln in parts:
                    im.alpha_composite(Image.open(os.path.join(src, parts[ln])).convert('RGBA'))
            frames.append(im)
            names.append(f'{t}{n}')
        nominal = None
        pose = os.path.join(os.path.dirname(os.path.normpath(src)), 'pose.json')
        if os.path.exists(pose):
            with open(pose, encoding='utf-8') as f:
                nominal = json.load(f).get('nominal_ms')
        if ms or nominal:
            return frames, [int(ms or nominal)] * len(frames), names, True, meta
        return frames, [0] * len(frames), names, False, meta
    framed = [fn for fn in files if re.match(r'^f\d\d', fn)] or files
    if not framed:
        raise Fail(f'{src}: no PNG frames')
    frames = [Image.open(os.path.join(src, fn)).convert('RGBA') for fn in framed]
    names = [re.sub(r'^f\d\d_?', '', os.path.splitext(fn)[0]).replace('_', ' ') or f'{i}' for i, fn in enumerate(framed)]
    if ms:
        return frames, [ms] * len(frames), names, True, meta
    if known and len(known) == len(frames):
        return frames, [int(d) for d in known], names, True, meta
    if known:
        raise Fail(f'{durs_file}: {len(known)} durations_ms for {len(frames)} frame PNGs')
    return frames, [0] * len(frames), names, False, meta


def plan_of(set_id):
    """frame names and the contact index from motion_bible.json + motion_chars.json for a set id (None when it is no motion set)"""
    m = SET_RE.match(set_id or '')
    if not m:
        return None
    motion = {'atk': 'attack', 'hit': 'hit', 'idle': 'idle'}[m.group(1)]
    kind, _, key = m.group(2).partition('_')
    sheet = f'sheet/{kind}/{key}'
    with open(os.path.join(SPECS, 'motion_bible.json'), encoding='utf-8') as f:
        bible = json.load(f)
    with open(os.path.join(SPECS, 'motion_chars.json'), encoding='utf-8') as f:
        chars = json.load(f)
    char = chars.get('chars', {}).get(sheet) or {}
    arch = char.get('arch') or next((a for a, v in bible['archetypes'].items() if sheet in v.get('users', [])), None)
    if motion == 'attack' and arch in bible['archetypes']:
        E = bible['archetypes'][arch]['attack']
        over = (char.get('timing') or {}).get('ms') or {}
        return dict(motion=motion, sheet=sheet, names=[fr['name'] for fr in E['frames']], contact=E['contact'],
                    ms=[over.get(fr['name'], fr['ms']) for fr in E['frames']])
    if motion == 'hit':
        w = chars.get('hit', {}).get('sheets', {}).get(sheet) or (bible['archetypes'].get(arch) or {}).get('hit_default')
        E = bible['hit']['weights'].get(w)
        if E:
            return dict(motion=motion, sheet=sheet, weight=w, names=[fr['name'] for fr in E['frames']], contact=E['contact'],
                        ms=[fr['ms'] for fr in E['frames']])
    return dict(motion=motion, sheet=sheet, names=None, contact=None, ms=None)


def key_out(im):
    a = np.asarray(im.convert('RGBA')).copy()
    a[(a[..., 0] == KEY[0]) & (a[..., 1] == KEY[1]) & (a[..., 2] == KEY[2]), 3] = 0
    a[a[..., 3] < 128, 3] = 0
    a[a[..., 3] >= 128, 3] = 255
    return a


def game_size(arrs, scale, margin=8):
    """crop every frame to the union box (one box: the frames keep their places against each other, as on the floor) and reduce
    it to game size: premultiplied box filter, alpha cut at 50 % (crisp edges, as a registered sheet)"""
    ys, xs = [], []
    for a in arrs:
        y, x = np.nonzero(a[..., 3])
        if len(x):
            ys += [y.min(), y.max()]
            xs += [x.min(), x.max()]
    if not xs:
        raise Fail('every frame is empty (only #FF00FF / transparent pixels)')
    h, w = arrs[0].shape[:2]
    x0, x1 = max(0, min(xs) - margin), min(w, max(xs) + 1 + margin)
    y0, y1 = max(0, min(ys) - margin), min(h, max(ys) + 1 + margin)
    if (w, h) == (384, 1024) and max(ys) <= FLOOR:          # a SPEC mannequin frame: the box ends on the floor line y=870
        y1 = FLOOR + 1
    tw, th = max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))
    out = []
    for a in arrs:
        im = Image.fromarray(a[y0:y1, x0:x1], 'RGBA').convert('RGBa').resize((tw, th), Image.BOX).convert('RGBA')
        b = np.asarray(im).copy()
        b[..., 3] = np.where(b[..., 3] >= 128, 255, 0)
        out.append(Image.fromarray(b, 'RGBA'))
    return out, (x0, y0, x1, y1)


def data_uri(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


def read_set(arg, exe, ms, scale, work):
    src, _, at = arg.rpartition('@') if re.search(r'@\d+$', arg) else (arg, '', '')
    src = os.path.normpath(src)
    if not os.path.exists(src):
        raise Fail(f'{src}: not found')
    stem = os.path.splitext(os.path.basename(src))[0]
    meta = {}
    if os.path.isdir(src):
        frames, durs, names, timed, meta = load_folder(src, ms)
        set_id, up = stem, src                      # layers / frames / export / v<N> folders take the set name above them
        while re.match(r'^(layers|frames|export|v\d+)$', set_id) and os.path.dirname(up) != up:
            up = os.path.dirname(up)
            set_id = os.path.basename(up)
        if meta.get('set'):                         # receive.py / check_skeleton.py --export name the set in pose_measured.json
            set_id = meta['set']
    else:
        if not src.lower().endswith('.aseprite'):
            raise Fail(f'{src}: give an .aseprite or a folder of frame PNGs')
        sub = os.path.join(work, re.sub(r'[^A-Za-z0-9_.-]+', '_', stem) + '_' + hashlib.md5(src.encode()).hexdigest()[:6])
        os.makedirs(sub, exist_ok=True)
        frames, durs, tags = load_aseprite(src, exe, sub)
        timed = True
        names = [None] * len(frames)
        for t, a, b in tags:
            if a == b and a < len(names):
                names[a] = t
        set_id = stem
    plan = plan_of(set_id)
    notes = []
    if plan and plan['names']:
        if len(plan['names']) == len(frames):
            names = plan['names']
        else:
            notes.append(f'{len(frames)} frames, the plan has {len(plan["names"])} ({", ".join(plan["names"])})')
        if plan['ms'] and len(plan['ms']) == len(durs) and not timed:
            durs = list(plan['ms'])                         # PNG frames without durations: the planned ms
            timed = True
            notes.append(f'no frame times in the folder: playing the planned ms {durs}')
        elif plan['ms'] and len(plan['ms']) == len(durs) and plan['ms'] != list(durs):
            notes.append(f'file durations {list(durs)} differ from the plan {plan["ms"]} - the page plays the file')
    if not timed:
        raise Fail(f'{src}: frame times unknown - no pose_measured.json durations_ms beside the PNGs, no motion plan for "{set_id}" '
                   '(set id from pose_measured.json "set" or the folder name) and no --ms. Take the frames receive.py exported '
                   '(it writes pose_measured.json), the .aseprite itself, or give --ms')
    gait = re.match(r'^(run|walk)_', set_id)                  # run / walk drafts as stand-ins: R1..R8 / W1..W8
    names = [n or (f'{"R" if gait.group(1) == "run" else "W"}{i + 1}' if gait else f'{i}') for i, n in enumerate(names)]
    if at != '':
        contact = int(at)
        source = 'given with @'
    elif plan and plan['contact'] is not None and len(frames) == len(plan['names'] or []):
        contact = plan['contact']
        source = f'{plan["motion"]} plan of {plan["sheet"]}'
    else:
        guess = [i for i, n in enumerate(names) if re.match(r'^(contact|release|fire|K1\b)', n)]
        if len(guess) != 1:
            raise Fail(f'{src}: no contact frame known (no motion_bible entry for "{set_id}") - append @<frame index>, e.g. {arg}@0')
        contact, source = guess[0], f'the frame named {names[guess[0]]}'
    if not 0 <= contact < len(frames):
        raise Fail(f'{src}: contact {contact} is outside frames 0-{len(frames) - 1}')
    lead = lead_frame(names, contact)
    small, box = game_size([key_out(f) for f in frames], scale)
    return dict(id=set_id, source=os.path.relpath(src, ROOT) if src.startswith(ROOT) else src, names=names, ms=[int(d) for d in durs],
                contact=contact, contact_source=source, lead=lead, w=small[0].width, h=small[0].height, crop=list(map(int, box)),
                frames=[data_uri(s) for s in small], notes=notes)


def lead_frame(names, contact):
    """the frame shown still during the lead-in before each play: a neutral one - the settle frame, else the last, else frame 0 -
    never the contact frame or a neighbour of it (the decoy swaps the contact with a neighbour; a hit's frame 0 is the contact K1).
    None: no such frame, the floor stays empty during the lead-in."""
    n = len(names)
    settle = [i for i, nm in enumerate(names) if re.search(r'settle', nm or '', re.I)]
    for i in settle[-1:] + [n - 1, 0]:
        if abs(i - contact) > 1:
            return i
    return None


PAGE = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#16181c;--panel:#1f232a;--floor:#2c3029;--line:#3d443b;--text:#e7e9ec;--muted:#9aa3ad;--accent:#e0b44c;--ok:#6cc08b;--bad:#e2706a;--sel:#f2d16b}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI","Noto Sans KR",sans-serif}
main{max-width:860px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:16px;margin:24px 0 8px}
p{margin:6px 0}
.muted{color:var(--muted)}
.panel{background:var(--panel);border-radius:8px;padding:14px 16px;margin:12px 0}
button{font:inherit;color:#111;background:var(--accent);border:0;border-radius:6px;padding:8px 16px;cursor:pointer}
button.ghost{background:transparent;color:var(--text);border:1px solid var(--line)}
button:disabled{opacity:.4;cursor:default}
input[type=text]{font:inherit;background:#111418;color:var(--text);border:1px solid var(--line);border-radius:6px;padding:6px 8px;width:220px}
textarea{width:100%;min-height:110px;background:#111418;color:var(--text);border:1px solid var(--line);border-radius:6px;font:12px/1.4 ui-monospace,Menlo,Consolas,monospace;padding:8px}
.stage{position:relative;height:var(--stageh);background:linear-gradient(#1b1e23 0,#1b1e23 78%,var(--floor) 78%);border-radius:8px;overflow:hidden}
.stage img{position:absolute;left:50%;bottom:calc(22% - var(--sink));transform:translateX(-50%);image-rendering:pixelated;image-rendering:crisp-edges}
.stage .cue{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--muted)}
.strip{display:flex;flex-wrap:wrap;gap:6px;padding:8px;background:var(--floor);border-radius:8px}
.cell{flex:0 0 auto;display:flex;flex-direction:column;align-items:center;border:2px solid transparent;border-radius:6px;padding:4px;cursor:pointer;background:#252a24}
.cell img{image-rendering:pixelated;image-rendering:crisp-edges;display:block}
.cell span{font-size:12px;color:var(--muted)}
.cell.on{border-color:var(--sel)}
.cell.on span{color:var(--sel)}
.big{display:flex;justify-content:center;margin:10px 0}
.big img{image-rendering:pixelated;image-rendering:crisp-edges}
input[type=range]{width:100%}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}
.ok{color:var(--ok)} .bad{color:var(--bad)}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
[hidden]{display:none!important}
</style>
</head>
<body>
<main>
<h1>__TITLE__</h1>
<p class="muted" id="meta"></p>

<section id="intro" class="panel">
<p><b>무엇을 하나</b>: 마네킹(뼈대) 동작을 게임 크기로 한 번씩 봅니다. 동작이 끝나면 그 동작의 프레임을 늘어놓은 띠에서 <b>무기가 맞은 순간(타격·발사·피격이 일어난 프레임)</b>을 고릅니다.</p>
<p>몇 번은 일부러 바꾼 판(속임 판)이 섞여 있습니다. 박자를 외우지 말고 본 모양으로 고르세요. 다시 보기는 없습니다.</p>
<p class="muted">게임 크기 ×<span class="z"></span> 확대, 1배속 실제 시간(설계 ms ÷ 1.3<span id="spd"></span>), 효과·화면 흔들림·섬광 없음. 시도 <span id="ntr"></span>번, 매번 순서가 바뀝니다.</p>
<div class="row"><label>이름(선택) <input type="text" id="viewer" maxlength="40" placeholder="보는 사람"></label><button id="start">시작</button></div>
</section>

<section id="play" hidden>
<p class="muted" id="trialno"></p>
<div class="stage" id="stage"><div class="cue" id="cue">준비</div><img id="sprite" alt=""></div>
</section>

<section id="pick" hidden>
<p><b>맞은 순간은 몇 번 프레임이었나요?</b> <span class="muted">(띠를 누르거나 슬라이더·← → 로 넘겨 보고 Enter. 위 그림 = 게임 크기 ×<span class="z"></span>, 띠 = ×<span id="sz"></span>)</span></p>
<div class="big"><img id="bigimg" alt=""></div>
<input type="range" id="scrub" min="0" value="0">
<div class="strip" id="strip"></div>
<div class="row" style="margin-top:10px"><button id="confirm">이 프레임</button><span class="muted" id="picked"></span></div>
</section>

<section id="done" hidden>
<h2>내 답</h2>
<div class="panel" id="mine"></div>
<h2>결과 JSON (복사해서 모아 주세요)</h2>
<textarea id="blob" readonly></textarea>
<div class="row"><button id="copy" class="ghost">복사</button><button id="again" class="ghost">다시 하기 (순서 새로)</button></div>
</section>

<section id="merge">
<h2>여러 사람 결과 합치기</h2>
<p class="muted">각 사람의 결과 JSON 을 아래에 붙여 넣습니다(한 줄에 하나, 또는 이어서). 세트마다 그 세트의 계획대로 판과 속임 판 답이 둘 다 있는 세션만 셉니다(속임 판 답이 없는 세션은 "not counted (no decoy answer)" 로 따로 적고 세지 않음). 통과: 그런 세션 5개 이상, 그중 80 %(5명 중 4명) 이상이 <b>같은 세션에서 두 판을 다</b> 맞힘 — 계획대로 재생한 판에서 맞는 순간 프레임이나 바로 옆 프레임, 속임 판에서 옮긴 쪽 프레임. 5개 미만이면 FAIL (not enough paired sessions). 주인 혼자 5회(매번 다른 순서)도 5명으로 셉니다.</p>
<p class="muted">같은 결과(같은 세션)를 여러 번 붙여도 한 번만 셉니다.</p>
<textarea id="pasted" placeholder='{"tool":"gate_page", ...}'></textarea>
<div class="row"><button id="score" class="ghost">채점</button><span class="muted" id="scoremsg"></span></div>
<div id="verdict"></div>
</section>
</main>

<script id="data" type="application/json">__DATA__</script>
<script>
(function () {
  'use strict';
  var D = JSON.parse(document.getElementById('data').textContent);
  var $ = function (id) { return document.getElementById(id); };
  var Z = D.zoom, SPEED = D.speed;
  var rnd = function () { var a = new Uint32Array(1); (window.crypto || window.msCrypto).getRandomValues(a); return a[0] / 4294967296; };
  var between = function (a, b) { return a + (b - a) * rnd(); };
  var shuffle = function (arr) { for (var i = arr.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)); var t = arr[i]; arr[i] = arr[j]; arr[j] = t; } return arr; };
  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); };
  var maxW = 0, maxH = 0;
  D.sets.forEach(function (s) { maxW = Math.max(maxW, s.w); maxH = Math.max(maxH, s.h); });
  document.documentElement.style.setProperty('--stageh', Math.max(240, Math.round(maxH * Z / 0.78) + 24) + 'px');
  document.documentElement.style.setProperty('--sink', '0px');
  Array.prototype.forEach.call(document.querySelectorAll('.z'), function (e) { e.textContent = Z; });
  $('spd').textContent = SPEED !== 1 ? ', 속도 ×' + SPEED : '';
  $('sz').textContent = D.stripZoom;
  $('meta').textContent = D.sets.length + '세트 · 페이지 ' + D.page + ' · ' + D.made;

  // a trial: the planned play or a decoy (the contact frame swapped with a neighbour, durations scaled)
  function makeTrials() {
    var out = [];
    D.sets.forEach(function (s, si) {
      var n = s.frames.length, order = [], i;
      for (i = 0; i < n; i++) order.push(i);
      out.push({set: si, decoy: false, order: order, ms: s.ms.slice(), expected: s.contact, shift: 0, factor: 1});
      if (D.decoy && n >= 2) {
        var sides = [];
        if (s.contact + 1 < n) sides.push(1);
        if (s.contact - 1 >= 0) sides.push(-1);
        var d = sides[Math.floor(rnd() * sides.length)], o = order.slice(), f = Math.round(between(0.8, 1.25) * 100) / 100;
        o[s.contact] = s.contact + d; o[s.contact + d] = s.contact;
        out.push({set: si, decoy: true, order: o, ms: s.ms.map(function (m) { return Math.round(m * f); }), expected: s.contact + d, shift: d, factor: f});
      }
    });
    return shuffle(out);
  }

  var trials = [], cur = 0, started = '', viewer = '';
  var img = $('sprite');

  function show(s, k) { img.src = s.frames[k]; img.width = s.w * Z; img.height = s.h * Z; }

  async function play(t) {
    var s = D.sets[t.set];
    $('cue').hidden = false; $('cue').textContent = '준비'; img.hidden = true;
    await sleep(between(500, 900));
    $('cue').hidden = true; img.hidden = false;
    var reps = 1 + Math.floor(rnd() * D.reps), played = [];
    for (var r = 0; r < reps; r++) {
      // lead-in on a neutral frame (settle / last / first, never the contact or its neighbours; the same frame in the decoy)
      if (s.lead === null || s.lead === undefined) img.hidden = true; else show(s, s.lead);
      var idle = between(600, 1400); played.push(Math.round(idle));
      await sleep(idle);
      img.hidden = false;
      for (var i = 0; i < t.order.length; i++) {
        show(s, t.order[i]);
        await sleep(t.ms[i] / 1.3 / SPEED);
      }
      await sleep(350);
      if (r + 1 < reps) { img.hidden = true; var pause = between(400, 1400); played.push(Math.round(pause)); await sleep(pause); img.hidden = false; }
    }
    img.hidden = true;
    t.reps = reps; t.pauses_ms = played;
  }

  var sel = 0;
  function pickUI(t) {
    var s = D.sets[t.set], strip = $('strip');
    strip.innerHTML = '';
    t.order.forEach(function (k, i) {
      var c = document.createElement('div');
      c.className = 'cell'; c.dataset.i = i;
      var im = document.createElement('img');
      im.src = s.frames[k]; im.width = s.w * D.stripZoom; im.height = s.h * D.stripZoom; im.alt = String(i + 1);
      var lab = document.createElement('span'); lab.textContent = String(i + 1);
      c.appendChild(im); c.appendChild(lab);
      c.addEventListener('click', function () { choose(i); });
      strip.appendChild(c);
    });
    $('scrub').max = t.order.length - 1;
    choose(0, true);
  }
  function choose(i, quiet) {
    var t = trials[cur], s = D.sets[t.set];
    sel = Math.max(0, Math.min(t.order.length - 1, i));
    $('scrub').value = sel;
    var b = $('bigimg'); b.src = s.frames[t.order[sel]]; b.width = s.w * Z; b.height = s.h * Z;
    Array.prototype.forEach.call($('strip').children, function (c) { c.classList.toggle('on', +c.dataset.i === sel); });
    $('picked').textContent = (sel + 1) + '번 / ' + t.order.length;
    if (!quiet) { var on = $('strip').children[sel]; if (on && on.scrollIntoView) on.scrollIntoView({block: 'nearest', inline: 'nearest'}); }
  }
  $('scrub').addEventListener('input', function () { choose(+this.value); });
  document.addEventListener('keydown', function (e) {
    if ($('pick').hidden) return;
    if (e.key === 'ArrowLeft') { choose(sel - 1); e.preventDefault(); }
    else if (e.key === 'ArrowRight') { choose(sel + 1); e.preventDefault(); }
    else if (e.key === 'Enter') { $('confirm').click(); e.preventDefault(); }
  });

  async function runTrial() {
    var t = trials[cur];
    $('intro').hidden = true; $('done').hidden = true; $('pick').hidden = true; $('play').hidden = false; $('merge').hidden = true;
    $('trialno').textContent = (cur + 1) + ' / ' + trials.length;
    t.t0 = performance.now();
    await play(t);
    $('play').hidden = true; $('pick').hidden = false;
    t.shown = performance.now();
    pickUI(t);
  }
  $('confirm').addEventListener('click', function () {
    var t = trials[cur];
    t.pick = sel; t.rt_ms = Math.round(performance.now() - t.shown);
    cur++;
    if (cur < trials.length) runTrial(); else finish();
  });

  function hitReal(t) { return Math.abs(t.pick - t.expected) <= 1; }
  function hitDecoy(t) { return (t.pick - (t.expected - t.shift)) * t.shift >= 1; }

  function blobOf() {
    return {tool: 'gate_page', version: 1, page: D.page, viewer: viewer, session: D.page + '-' + Math.floor(rnd() * 1e9).toString(36),
      started: started, finished: new Date().toISOString(),
      sets: D.sets.map(function (s) { return {id: s.id, frames: s.frames.length, contact: s.contact, lead: s.lead}; }),
      trials: trials.map(function (t) {
        return {set: D.sets[t.set].id, decoy: t.decoy, shift: t.shift, factor: t.factor, order: t.order, ms_planned: t.ms,
          expected: t.expected, pick: t.pick, pick_frame: t.order[t.pick], hit: t.decoy ? hitDecoy(t) : hitReal(t),
          reps: t.reps, pauses_ms: t.pauses_ms, rt_ms: t.rt_ms};
      })};
  }

  function finish() {
    $('pick').hidden = true; $('play').hidden = true; $('done').hidden = false; $('merge').hidden = false;
    var b = blobOf(), rows = b.trials.map(function (t) {
      return '<tr><td>' + esc(t.set) + '</td><td>' + (t.decoy ? '속임 판 (맞는 순간 ' + (t.shift > 0 ? '한 프레임 늦게' : '한 프레임 일찍') + ', 시간 ×' + t.factor + ')' : '계획대로') +
        '</td><td>' + (t.pick + 1) + '번</td><td>' + (t.expected + 1) + '번</td><td class="' + (t.hit ? 'ok' : 'bad') + '">' + (t.hit ? (t.decoy ? '옮긴 쪽' : '맞음 (±1)') : (t.decoy ? '박자 쪽' : '빗나감')) + '</td></tr>';
    });
    $('mine').innerHTML = '<table><tr><th>세트</th><th>판</th><th>고른 것</th><th>맞는 순간</th><th></th></tr>' + rows.join('') + '</table>' +
      '<p class="muted">한 사람의 답만으로는 통과를 정하지 않습니다. 아래 칸에 5명(또는 5회)의 JSON 을 모아 채점합니다.</p>';
    $('blob').value = JSON.stringify(b);
    if ($('pasted').value.indexOf(b.session) < 0) $('pasted').value = ($('pasted').value ? $('pasted').value + '\n' : '') + JSON.stringify(b);
    score();
  }

  $('start').addEventListener('click', function () {
    viewer = $('viewer').value.trim(); started = new Date().toISOString();
    trials = makeTrials(); cur = 0; runTrial();
  });
  $('again').addEventListener('click', function () { $('done').hidden = true; $('intro').hidden = false; });
  $('copy').addEventListener('click', function () {
    var ta = $('blob'); ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    if (navigator.clipboard) navigator.clipboard.writeText(ta.value).then(function () { $('copy').textContent = '복사됨'; }, function () {});
    else if (ok) $('copy').textContent = '복사됨';
  });

  function parseBlobs(text) {
    var out = [], depth = 0, start = -1, inStr = false, escp = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (inStr) { if (escp) escp = false; else if (c === '\\') escp = true; else if (c === '"') inStr = false; continue; }
      if (c === '"') inStr = true;
      else if (c === '{') { if (depth === 0) start = i; depth++; }
      else if (c === '}') { depth--; if (depth === 0 && start >= 0) { try { out.push(JSON.parse(text.slice(start, i + 1))); } catch (e) {} start = -1; } }
    }
    return out.filter(function (b) { return b && b.tool === 'gate_page' && b.trials; });
  }

  function score() {
    var blobs = parseBlobs($('pasted').value), other = blobs.filter(function (b) { return b.page !== D.page; }).length;
    // one viewer (session) counts once: the same blob pasted twice is not two viewers
    // (by session id AND by the trials themselves: a copied blob with an edited session id / viewer is still one viewer - the random
    // order, decoy timing factors and picks of two real sessions never match)
    var seen = {}, dup = 0;
    blobs = blobs.filter(function (b) {
      if (b.page !== D.page) return false;
      var ks = ['T:' + JSON.stringify(b.trials)];
      if (b.session) ks.push('S:' + b.session);
      if (ks.some(function (k) { return seen[k]; })) { dup++; return false; }
      ks.forEach(function (k) { seen[k] = true; }); return true;
    });
    $('scoremsg').textContent = blobs.length + '명(회) 결과' + (other ? ', 다른 페이지의 결과 ' + other + '개는 뺌' : '') +
      (dup ? ', 같은 세션(또는 같은 답)을 두 번 붙인 결과 ' + dup + '개는 뺌' : '') +
      (D.decoy ? '' : ' — no decoys - not a gate-1 result (속임 판 없는 페이지: 첫 관문 결과가 아님)');
    if (!blobs.length) { $('verdict').innerHTML = ''; return; }
    var html = '<table><tr><th>세트</th><th>보는 사람</th><th>계획대로: 맞는 순간 ±1 (피격은 첫 프레임만)</th><th>속임 판: 옮긴 쪽</th><th>둘 다 맞힌 세션</th><th>판정</th></tr>';
    // planned play: the contact frame or a neighbour - but when the contact is the FIRST frame (hit sets: K1), only the contact itself
    // counts: there the decoy can only move the contact to frame 2, so a viewer who always answers "frame 2" would pass both plays
    // (GPT QA fb286cb).
    var hitR = function (t) { return t.expected === 0 ? t.pick === 0 : Math.abs(t.pick - t.expected) <= 1; };
    var hitD = function (t) { return (t.pick - (t.expected - t.shift)) * t.shift >= 1; };
    var who = function (b) { return esc(b.viewer || b.session || '?'); };
    D.sets.forEach(function (s) {
      var real = [], dec = [], skipped = [], verdict, n, k, kd, m, both = null;
      if (D.decoy && s.frames.length >= 2) {
        // a page with decoys counts PAIRED sessions only: a session counts for this set when it answered BOTH the planned play and
        // the decoy of it. A planned answer without its decoy says nothing about beat-following (a beat-follower picks the planned
        // contact too), so it is listed, never counted - leaving decoys out of the pasted JSON cannot turn a FAIL into a PASS.
        blobs.forEach(function (b) {
          var r = null, d = null;
          b.trials.forEach(function (t) { if (t.set !== s.id) return; if (t.decoy) { if (!d) d = t; } else if (!r) r = t; });
          if (r && d) { real.push(r); dec.push(d); }
          else if (r) skipped.push(who(b) + ' (not counted (no decoy answer): 속임 판 답 없음)');
          else if (d) skipped.push(who(b) + ' (not counted (no planned answer): 계획대로 답 없음)');
        });
        n = real.length; k = real.filter(hitR).length; kd = dec.filter(hitD).length; m = n;
        // PASS counts the SAME session reading both plays (GPT QA 29c4235): a viewer who gets the planned play but follows the beat
        // on the decoy, and another who does the opposite, must not add up to two passes.
        both = real.filter(function (t, i) { return hitR(t) && hitD(dec[i]); }).length;
        if (n < 5) verdict = '<b class="bad">FAIL</b> — not enough paired sessions: 짝(계획대로 + 속임 판)이 다 있는 세션 ' + n + '/5' +
          (n ? '<br><span class="muted">고른 프레임: ' + real.map(function (t) { return t.pick + 1; }).join(', ') +
            ' / 속임 판: ' + dec.map(function (t) { return (t.pick + 1) + '(정답 ' + (t.expected + 1) + ')'; }).join(', ') + '</span>' : '');
        else if (both >= 0.8 * n) verdict = '<b class="ok">PASS</b>';
        else verdict = '<b class="bad">FAIL</b> — ' + (k < 0.8 * n ? '맞는 순간이 읽히지 않음' : kd < 0.8 * n ? '속임 판에서 박자를 따라감' : '두 판을 다 맞힌 세션이 80 % 아래 (' + both + '/' + n + ')');
      } else {
        // no decoy for this set (a --no-decoy page, or a one-frame set): planned answers only, as before
        blobs.forEach(function (b) { b.trials.forEach(function (t) { if (t.set === s.id) (t.decoy ? dec : real).push(t); }); });
        n = real.length; k = real.filter(hitR).length; m = dec.length; kd = dec.filter(hitD).length;
        if (n < 5) verdict = '<span class="muted">사람 부족 (' + n + '/5) — 고른 프레임: ' + real.map(function (t) { return t.pick + 1; }).join(', ') + '</span>';
        else if (k >= 0.8 * n && (m === 0 || kd >= 0.8 * m)) verdict = '<b class="ok">PASS</b>';
        else verdict = '<b class="bad">FAIL</b> — ' + (k < 0.8 * n ? '맞는 순간이 읽히지 않음' : '속임 판에서 박자를 따라감');
      }
      if (!D.decoy) verdict += ' <span class="muted">(no decoys - not a gate-1 result: 속임 판 없는 페이지)</span>';
      if (skipped.length) verdict += '<br><span class="muted">' + skipped.join('<br>') + '</span>';
      html += '<tr><td>' + esc(s.id) + '<br><span class="muted">맞는 순간 ' + (s.contact + 1) + '번 (' + esc(s.names[s.contact]) + ')</span></td><td>' + n +
        '</td><td>' + k + ' / ' + n + '</td><td>' + (m ? kd + ' / ' + m : '-') + '</td><td>' + (both == null ? '-' : both + ' / ' + n) + '</td><td>' + verdict + '</td></tr>';
    });
    $('verdict').innerHTML = html + '</table>';
  }
  $('score').addEventListener('click', score);
  $('ntr').textContent = D.sets.reduce(function (a, s) { return a + 1 + (D.decoy && s.frames.length >= 2 ? 1 : 0); }, 0);
})();
</script>
</body>
</html>
'''


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out', help='the HTML page to write')
    ap.add_argument('sets', nargs='+', help='SET.aseprite[@contact] or FRAMES_DIR[@contact]')
    ap.add_argument('--reps', type=int, default=1, help='each trial plays the sequence 1..N times (random), random pauses between (default 1)')
    ap.add_argument('--no-decoy', action='store_true', help='no decoy trials (not a gate-1 run: the plan asks for decoys)')
    ap.add_argument('--speed', type=float, default=1.0, help='playback speed on top of the 1x real time (ms / 1.3); default 1')
    ap.add_argument('--zoom', type=int, default=3, help='nearest-neighbour view zoom of the game-size frames (default 3)')
    ap.add_argument('--scale', type=float, default=0.1654, help='source -> game size (default 0.1654, the class / captain sheets)')
    ap.add_argument('--ms', type=int, help='frame duration for every frame of a PNG folder (overrides pose_measured.json / pose.json; '
                    'needed when the folder has no times and its set id has no motion plan)')
    ap.add_argument('--title', default='첫 관문: 맞는 순간 찾기', help='page title')
    ap.add_argument('--aseprite-exe', default=os.environ.get('ASEPRITE_PATH') or (HEADLESS if os.path.exists(HEADLESS) else 'aseprite'))
    a = ap.parse_args(argv)
    sets = []
    with tempfile.TemporaryDirectory(prefix='gate-page-') as work:
        for arg in a.sets:
            try:
                s = read_set(arg, a.aseprite_exe, a.ms, a.scale, work)
            except (Fail, OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
                print(f'FAIL: {arg}: {e}')
                return 1
            if any(o['id'] == s['id'] for o in sets):
                s['id'] = f'{s["id"]}#{len(sets) + 1}'
            sets.append(s)
            print(f'- {s["id"]}: {len(s["frames"])} frames, {s["w"]}x{s["h"]} game px, ms {s["ms"]}, contact {s["contact"]} '
                  f'({s["names"][s["contact"]]}; {s["contact_source"]}), lead-in '
                  + (f'on frame {s["lead"]} ({s["names"][s["lead"]]})' if s['lead'] is not None else 'on the empty floor (no neutral frame)')
                  + f', source {s["source"]}')
            for n in s['notes']:
                print(f'  WARN: {n}')
    # a --no-decoy page never shares its id with the gate-1 page of the same sets (blobs are matched on the page id)
    page_id = hashlib.sha1(json.dumps([[s['id'], s['ms'], s['contact'], s['frames']] for s in sets]).encode()).hexdigest()[:10] \
        + ('-nodecoy' if a.no_decoy else '')
    data = dict(page=page_id, made=__import__('datetime').date.today().isoformat(), zoom=a.zoom, stripZoom=max(1, a.zoom - 1), speed=a.speed,
                reps=max(1, a.reps),
                decoy=not a.no_decoy, scale=a.scale,
                sets=[{k: s[k] for k in ('id', 'source', 'names', 'ms', 'contact', 'lead', 'w', 'h', 'frames')} for s in sets])
    html = (PAGE.replace('__TITLE__', a.title.replace('&', '&amp;').replace('<', '&lt;'))
            .replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'wrote {a.out}: {len(sets)} set(s), page id {page_id}, {os.path.getsize(a.out) / 1024:.1f} KB'
          + ('' if not a.no_decoy else ' (no decoys: not a gate-1 run)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
