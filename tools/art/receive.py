#!/usr/bin/env python3
"""Cloud-side receipt of art-inbox deliveries: what is new, and for one file: fetch, check, diff, dry-run convert, review sheet.

  python3 tools/art/receive.py --list                        # files on art-inbox that differ from this branch + new NOTES sections
  python3 tools/art/receive.py sheet_monster_wolf            # or the .png name
  python3 tools/art/receive.py sheet_captain_pilgrim --work /tmp/rcv --aseprite-exe /path/to/aseprite

"Reviewed" has no state file: a delivery counts as reviewed once its files are copied into this branch's art/inbox/
(git checkout origin/art-inbox -- <paths>, done for accepted AND rejected deliveries, NOTES.md included). So the unreviewed set is
`git diff --name-only HEAD origin/art-inbox -- art/inbox`, which survives a wiped scratchpad and cannot skip a commit.

It does the steps the reviewer otherwise repeats by hand (and has got wrong by hand):
  1. git fetch origin art-inbox; copy the PNG (and aseprite/<stem>.aseprite when present) out of origin/art-inbox
  2. find the previous version of the PNG on art-inbox (the base of a touch-up) unless --no-base
  3. check_delivery.py with the layout / cell / spots of art/requests/phase3.json, --base and --aseprite
  4. sheets.py --dry-run for the new file (and the base), with the scale and cell the registered sheet uses,
     and count the game-size pixels that changed per frame (a touch-up nobody can see changes 0)
  5. check that the commit which last changed the file touched nothing outside art/inbox/
  6. write review_<stem>.png: the design reference (portrait / concept) beside the game-size sheet on three floors (dark, sand, snow),
     and print how much of the sprite is within +-25 luminance of each floor (it vanishes there)
Nothing is registered or committed: after reading it, run sheets.py <file> yourself (settings come from phase3.json).

Two kinds of delivery are not base sheets and never go to sheets.py:
  guides/<set>/<set>.aseprite     a skeleton (mannequin) from the PC: check_skeleton.py with the request's pose.json and draft, strips
                                  exported and checked (run sets: check_delivery --flight-slots 4, the flight frame R4 / R8 is in the air)
  gait/<sheet stem>_<run|walk>.aseprite, gait/<sheet stem>_<run|walk>_a.png + _b.png
                                  final gait frames for a registered sheet: strips checked (run: --flight-slots 4), the .aseprite checked
                                  for a mannequin (add_gait guide_reason: joints layer, frames matching a cloud skeleton draft) and its
                                  export compared with the PNGs, then add_gait.py --dry-run (stride from guides/<gait>_<class> or
                                  <gait>_base); the register command is printed only when everything passed
  python3 tools/art/receive.py guides/run_base/run_base
  python3 tools/art/receive.py gait/sheet_class_warrior_run
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
FLOORS = (('dark', (46, 58, 46)), ('sand', (201, 164, 90)), ('snow', (226, 232, 238)))
HEADLESS = os.path.join(ROOT, 'tools', 'art', 'ase_headless.sh')


def unreviewed():
    """paths under art/inbox that differ between this branch and origin/art-inbox; None when git cannot tell"""
    if git('rev-parse', '--verify', '-q', 'origin/art-inbox') is None:
        return None
    out = git('diff', '--name-only', 'HEAD', 'origin/art-inbox', '--', 'art/inbox')
    return None if out is None else [p for p in out.split('\n') if p]


def list_new():
    files = unreviewed()
    if files is None:
        print('CANNOT TELL: origin/art-inbox is not available here (fetch it first) - this is NOT "nothing new"')
        return 2
    if not files:
        print('nothing new: art/inbox on origin/art-inbox matches this branch')
        return 0
    print(f'{len(files)} path(s) differ from this branch (unreviewed):')
    gaits = {}
    for f in files:
        h = git('log', '-1', '--format=%h %ci %s', 'origin/art-inbox', '--', f) or '?'
        who = 'PC' if '(Aseprite)' in h else 'GPT'
        r = f[len('art/inbox/'):]
        m = GAIT_RE.match(r[:-4] if r.endswith('.png') else r)
        kind = ''
        if r.startswith('gait/'):
            kind = '  [gait frames: add_gait.py, NOT a base sheet]' if m else '  [gait/ but not named <sheet>_<run|walk>[_a|_b]]'
            if m:
                gaits.setdefault(f'{m.group(1)}_{m.group(2)}', []).append(os.path.basename(f))
        elif r.startswith('guides/'):
            kind = '  [skeleton guide: never game frames]'
        print(f'  [{who}] {f}  ←  {h}{kind}')
    for k, names in gaits.items():
        print(f'  gait set {k}: {", ".join(sorted(names))}  →  python3 tools/art/receive.py gait/{k}')
    if 'art/inbox/NOTES.md' in files:
        diff = git('diff', 'HEAD', 'origin/art-inbox', '--', 'art/inbox/NOTES.md') or ''
        heads = [ln[1:].strip() for ln in diff.split('\n') if ln.startswith('+## ')]
        removed = [ln for ln in diff.split('\n') if ln.startswith('-') and not ln.startswith('---')]
        print('  new NOTES sections: ' + (' | '.join(heads) if heads else '(none)'))
        print(f'  pin this check to {git("rev-parse", "--short", "origin/art-inbox")}: run the per-file checks with --no-fetch and check out by that hash')
        if removed:
            print(f'  WARNING: NOTES.md lost {len(removed)} line(s) that this branch has - a section may have been dropped in a rebase')
    return 0


def review_sheet(sheet, stem, work):
    """review.png + per floor: the share of the silhouette's EDGE pixels (and of all pixels) that nearly match the floor's
    brightness. The edge is what keeps a sprite readable: a pale interior inside a dark outline is fine (all 44 sheets registered
    on 2026-11-26 measured 0-0.4% on the edge for sand and snow, while their interiors went up to 24%)."""
    im = Image.open(sheet).convert('RGBA')
    cell = im.size[0] // 4
    frames = [im.crop(((i % 4) * cell, (i // 4) * cell, (i % 4 + 1) * cell, (i // 4 + 1) * cell)) for i in (0, 4, 5, 6)]
    ref = None
    for d in os.listdir(os.path.join(ROOT, 'art', 'requests', 'phase3')):
        if stem.replace('sheet_', '') == d:
            for name in ('concept_800.jpg', 'portrait_800.jpg', 'concept.png', 'portrait.png'):
                q = os.path.join(ROOT, 'art', 'requests', 'phase3', d, name)
                if os.path.exists(q):
                    ref = Image.open(q).convert('RGB')
                    break
    z = 3
    rows = len(FLOORS)
    rw = 0
    if ref:
        k = (cell * z * rows) / ref.height
        ref = ref.resize((max(1, round(ref.width * k)), cell * z * rows), Image.LANCZOS)
        rw = ref.width + 8
    out = Image.new('RGB', (rw + cell * z * 4, cell * z * rows), (20, 20, 20))
    if ref:
        out.paste(ref, (0, 0))
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]  # noqa: E731
    shares = []
    px, edge = [], []
    for f in frames:
        w, h = f.size
        d = list(getattr(f, 'get_flattened_data', f.getdata)())
        for y in range(h):
            for x in range(w):
                p = d[y * w + x]
                if p[3] > 0:
                    px.append(p)
                    if x in (0, w - 1) or y in (0, h - 1) or not (d[y * w + x - 1][3] and d[y * w + x + 1][3] and d[(y - 1) * w + x][3] and d[(y + 1) * w + x][3]):
                        edge.append(p)
    for r, (name, col) in enumerate(FLOORS):
        for i, f in enumerate(frames):
            bg = Image.new('RGBA', f.size, col + (255,))
            bg.alpha_composite(f)
            out.paste(bg.convert('RGB').resize((cell * z, cell * z), Image.NEAREST), (rw + i * cell * z, r * cell * z))
        near = sum(1 for p in px if abs(lum(p) - lum(col)) <= 25) / max(1, len(px))
        near_edge = sum(1 for p in edge if abs(lum(p) - lum(col)) <= 25) / max(1, len(edge))
        shares.append((name, near_edge, near))
    path = os.path.join(work, f'review_{stem}.png')   # per file: a reused --work must not show another sheet's review
    out.save(path)
    return path, shares


def git(*args, binary=False):
    r = subprocess.run(['git', '-C', ROOT, *args], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace').strip()


def show(rev, path, out):
    data = git('show', f'{rev}:{path}', binary=True)
    if data is None:
        return False
    with open(out, 'wb') as f:
        f.write(data)
    return True


def sheet_args(stem):
    """scale / cell for the dry run: phase3.json decides for classes and monsters; captains and heroes use the anchor
    scale and the cell of the already registered sheet (96 unless it was registered bigger)."""
    name = stem + '.png'
    try:
        items = json.load(open(os.path.join(ROOT, 'art', 'requests', 'phase3.json'), encoding='utf-8')).get('items', [])
    except (OSError, ValueError):
        items = []
    it = next((i for i in items if i.get('file') == name), {})
    if it.get('scale') or not name.startswith(('sheet_captain_', 'sheet_hero_')):
        return [], it          # phase3.json carries scale / cell / layout (captains and heroes too since 2026-11-26)
    return ['--scale', '0.1654', '--cell', '96'], it


def notes_spots(stem, item):
    """spot colours the artist declared in the newest NOTES section of this file (`SPOT: #rrggbb` / `- 점 색: #rrggbb`)
    that the request does not carry yet. Without this a declared eye colour is checked by nobody until requests.js is edited."""
    import re
    text = git('show', 'origin/art-inbox:art/inbox/NOTES.md') or ''
    keys = [k for k in (item.get('id'), stem, stem + '.png') if k]
    found = []
    for sec in re.split(r'(?m)^## ', text)[1:]:
        if any(k in sec.split('\n', 1)[0] or k in sec for k in keys):
            found = re.findall(r'(?im)^\s*(?:-\s*)?(?:SPOT|점 색)\s*:\s*(.+)$', sec) or found
    cols = []
    for line in found:
        cols += [c.lower() for c in re.findall(r'#[0-9a-fA-F]{6}', line)]
    known = {str(c).lower() for c in (item.get('spots') or [])}
    return [c for c in dict.fromkeys(cols) if c not in known]


def dry_run(png, work, extra):
    # one fresh folder per file: with a reused --work the walk below used to pick up another file's (or an older run's) sheet
    work = os.path.join(work, os.path.splitext(os.path.basename(png))[0])
    shutil.rmtree(work, ignore_errors=True)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'art', 'sheets.py'), png, '--dry-run', '--work', work, *extra],
                       capture_output=True)
    out = r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
    keep = ('주의', '실패', '점 색 ', '배율', 'idle:', 'windup:', 'strike:', 'hit:', '완료', '열쇠 색 픽셀')
    notes = [ln.strip() for ln in out.splitlines() if any(k in ln for k in keep)]
    sheet = None
    if r.returncode != 0:
        return None, [], notes + ['sheets.py failed: ' + out.strip().splitlines()[-1][:200] if out.strip() else 'sheets.py failed']
    for d, _, files in os.walk(work):
        for f in files:
            if f.startswith('sheet_') and f.endswith('.png') and 'pose_' not in f and 'preview' not in f:
                sheet = os.path.join(d, f)
    prev = [os.path.join(d, f) for d, _, files in os.walk(work) for f in files if f.startswith('preview')]
    return sheet, sorted(prev), notes


def version_key(d):
    """v2 < v10 (folder names of request drafts)"""
    m = re.match(r'v(\d+)$', d)
    return (0, int(m.group(1)), d) if m else (1, 0, d)


def latest_pose(set_name):
    """art/requests/guides/<set>/<newest vN>/pose.json -> (path, dict) or (None, {})"""
    req = os.path.join(ROOT, 'art', 'requests', 'guides', set_name)
    for d in sorted((d for d in (os.listdir(req) if os.path.isdir(req) else []) if os.path.exists(os.path.join(req, d, 'pose.json'))),
                    key=version_key, reverse=True):
        p = os.path.join(req, d, 'pose.json')
        try:
            with open(p, encoding='utf-8') as f:
                return p, json.load(f)
        except (OSError, ValueError):
            continue
    return None, {}


def strip_check(strip, label, extra):
    """check_delivery.py on one 1x4 strip -> return code (prints the RESULT / FAIL / WARN lines)"""
    c = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_delivery.py'), strip, '--layout', '1x4', *extra], capture_output=True)
    lines = [ln.strip() for ln in c.stdout.decode('utf-8', 'replace').splitlines()
             if ln.strip().startswith(('RESULT', 'FAIL', 'WARN', 'ERROR')) or '(flight)' in ln]
    print(f'- {label}: ' + (' | '.join(lines) or c.stdout.decode('utf-8', 'replace').strip()[-300:]))
    return c.returncode


def skeleton(rel, name, work, exe, tip):
    """a skeleton set delivered as one layered .aseprite (guides/<set>/<set>.aseprite): measure it, list what changed against
    the draft of the request, and make the strips + preview from it (the Aseprite session does not have to export them).
    The gait (walk / run) comes from the request's pose.json: a run strip has a flight frame in slot 4, so check_delivery runs
    with --flight-slots 4 (it must be 18 px or more above the floor instead of on it)."""
    path = f'art/inbox/{rel}.aseprite'
    new = os.path.join(work, 'new', name + '.aseprite')
    os.makedirs(os.path.dirname(new), exist_ok=True)
    if not show('origin/art-inbox', path, new):
        print(f'{path} is not on origin/art-inbox')
        return 2
    revs = (git('log', '--format=%h', 'origin/art-inbox', '--', path) or '').split()
    req = os.path.join(ROOT, 'art', 'requests', 'guides', name)
    drafts = sorted((d for d in (os.listdir(req) if os.path.isdir(req) else []) if os.path.exists(os.path.join(req, d, name + '.aseprite'))),
                    key=version_key)
    pose = {}
    if drafts and os.path.exists(os.path.join(req, drafts[-1], 'pose.json')):
        with open(os.path.join(req, drafts[-1], 'pose.json'), encoding='utf-8') as f:
            pose = json.load(f)
    gait = pose.get('gait', 'walk')
    print(f'# {name} (skeleton, {gait}) — art-inbox {revs[0] if revs else "?"} (tip {tip[:7]})')
    out = os.path.join(work, 'skeleton')
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_skeleton.py'), new, '--export', out, '--aseprite-exe', exe]
    if drafts:
        cmd += ['--base', os.path.join(req, drafts[-1], name + '.aseprite'), '--pose', os.path.join(req, drafts[-1], 'pose.json')]
        print(f'- draft of the request: art/requests/guides/{name}/{drafts[-1]}/')
    else:
        print(f'- NO draft of the request under art/requests/guides/{name}/: no --pose / --base (gait guessed from the file name)')
    r = subprocess.run(cmd, capture_output=True)
    print(r.stdout.decode('utf-8', 'replace').rstrip() or r.stderr.decode('utf-8', 'replace')[-400:])
    rc = r.returncode
    flight = ['--flight-slots', '4'] if gait == 'run' else []
    for s in 'ab':
        strip = os.path.join(out, f'{name}_{s}.png')
        if os.path.exists(strip):
            rc = rc or strip_check(strip, f'strip {s}' + (' (check_delivery --flight-slots 4: R4 / R8 are in the air)' if flight else ''), flight)
    print(f'- work folder: {work} (strips, {name}_preview.gif and pose_measured.json under skeleton/)')
    print('- a skeleton is a pose guide for the request, never game frames: add_gait.py refuses it (guides/ path, joints layer)')
    print('- after judging: git checkout origin/art-inbox -- <the delivered paths> art/inbox/NOTES.md')
    return rc


GAIT_RE = re.compile(r'^gait/(sheet_[^/]+?)_(run|walk)(?:_([ab]))?(?:\.aseprite)?$')


def gait_pose(sheet, gait):
    """the request whose stride the gait frames follow: guides/<gait>_<sheet without 'sheet_'>, <gait>_<last name part>, else <gait>_base"""
    body = sheet[len('sheet_'):]
    for set_name in (f'{gait}_{body}', f'{gait}_{body.split("_")[-1]}', f'{gait}_base'):
        p, d = latest_pose(set_name)
        if p:
            return p, d
    return None, {}


def export_ase_strips(src, exe, out, stem):
    """the visible layers of an n-frame .aseprite -> <stem>_a.png (frames 1-4), <stem>_b.png (5-8) -> (paths, frame count, problem)"""
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    env.pop('WAYLAND_DISPLAY', None)
    png, js = os.path.join(out, 'frames.png'), os.path.join(out, 'frames.json')
    try:
        r = subprocess.run([exe, '--batch', src, '--sheet', png, '--sheet-type', 'horizontal', '--data', js, '--format', 'json-array'],
                           stdin=subprocess.DEVNULL, capture_output=True, timeout=300, env=env)
    except (OSError, subprocess.SubprocessError) as e:
        return [], 0, f'Aseprite could not be run ({exe}): {e}'
    if r.returncode or not os.path.exists(png) or not os.path.exists(js):
        return [], 0, 'Aseprite export failed: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:]
    with open(js, encoding='utf-8') as f:
        frames = [fr['frame'] for fr in json.load(f)['frames']]
    im = Image.open(png)
    im.load()
    if im.mode in ('RGBA', 'LA', 'P'):
        rgba = im.convert('RGBA')
        # an opaque Background layer exports as RGBA with alpha 255 everywhere: save RGB; real transparency stays for check_delivery
        im = rgba.convert('RGB') if rgba.getchannel('A').getextrema()[0] == 255 else rgba
    cut = [im.crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h'])) for fr in frames]
    if any(c.size != (384, 1024) for c in cut):
        return [], len(cut), f'frame size {sorted({c.size for c in cut})}, a gait frame is 384x1024 (art/requests/guides/SPEC.md section 2)'
    paths = []
    for k, s in enumerate('ab'):
        part = cut[k * 4:(k + 1) * 4]
        if not part:
            break
        strip = Image.new(im.mode, (384 * 4, 1024))
        for j, c in enumerate(part):
            strip.paste(c, (j * 384, 0))
        p = os.path.join(out, f'{stem}_{s}.png')
        strip.save(p)
        paths.append(p)
    return paths, len(cut), None


def gait_delivery(rel, work, exe, tip):
    """final gait frames for a registered sheet: art/inbox/gait/<sheet png stem>_<gait>.aseprite and/or _<gait>_a.png + _<gait>_b.png.
    They are NOT a base sheet (sheets.py never sees them): check the strips (run: --flight-slots 4), then add_gait.py --dry-run
    shows what the sheet would become. Nothing is registered."""
    m = GAIT_RE.match(rel)
    if not m:
        print(f'art/inbox/{rel}: under gait/ a delivery is named <sheet png stem>_<run|walk>.aseprite or _<run|walk>_a.png / _b.png '
              '(e.g. gait/sheet_class_warrior_run_a.png) - not checked')
        return 2
    sheet, gait = m.group(1), m.group(2)
    stem = f'{sheet}_{gait}'
    out = os.path.join(work, 'gait')
    os.makedirs(out, exist_ok=True)
    got = {}
    for suffix in ('.aseprite', '_a.png', '_b.png'):
        dst = os.path.join(out, stem + suffix)
        if show('origin/art-inbox', f'art/inbox/gait/{stem}{suffix}', dst):
            got[suffix] = dst
    print(f'# {stem} (gait frames for {sheet}, {gait}) — tip {tip[:7]}')
    if not got:
        print(f'art/inbox/gait/{stem}.aseprite / {stem}_a.png / {stem}_b.png: none is on origin/art-inbox')
        return 2
    rc = 0
    for suffix in got:
        path = f'art/inbox/gait/{stem}{suffix}'
        revs = (git('log', '--format=%h', 'origin/art-inbox', '--', path) or '').split()
        touched = [p for p in (git('show', '--name-only', '--format=', revs[0]) or '').split('\n') if p] if revs else []
        outside = [p for p in touched if not p.startswith('art/inbox/')]
        print(f'- {path}: art-inbox {revs[0] if revs else "?"}' + (f' — commit touched OUTSIDE art/inbox/: {outside}' if outside else ''))
    print('- not a base sheet: sheets.py is never run on these; they are attached to the registered sheet with add_gait.py')
    if ('_a.png' in got) != ('_b.png' in got):
        print('  FAIL: only one strip delivered - a gait set is _a.png (frames 1-4) AND _b.png (frames 5-8)')
        rc = 1
    flight = ['--flight-slots', '4'] if gait == 'run' else []
    _, item = sheet_args(sheet)
    cellarg = ['--cell', str(item['cell'])] if item.get('cell') else []
    strips = [got[s] for s in ('_a.png', '_b.png') if s in got]
    if '.aseprite' in got:
        # the dry run below reads the PNG strips when both are there, so the .aseprite itself is checked for a mannequin here
        # (joints layer, or frames that match a cloud skeleton draft: a mannequin with its joints layer deleted)
        sys.path.insert(0, os.path.join(ROOT, 'tools', 'art'))
        import add_gait
        try:
            why = add_gait.guide_reason(got['.aseprite'], exe)
        except add_gait.Fail as e:
            why = str(e)
        if why:
            print(f'  FAIL: {stem}.aseprite is a skeleton (mannequin), not game frames: {why}')
            rc = 1
        else:
            print(f'- {stem}.aseprite: no joints layer, no frame matches a skeleton draft under art/requests/guides/*/v*/')
        exp, n, problem = export_ase_strips(got['.aseprite'], exe, os.path.join(out, 'from_aseprite'), stem)
        if problem:
            print(f'  FAIL: {stem}.aseprite: {problem}')
            rc = 1
        else:
            print(f'- {stem}.aseprite: {n} frames exported (visible layers) to {os.path.dirname(exp[0])}' + ('' if n == 8 else '  ← a cycle is 8 frames'))
            if n != 8:
                rc = 1
            for p, q in zip(exp, strips):
                a_, b_ = Image.open(p).convert('RGB'), Image.open(q).convert('RGB')
                same = a_.size == b_.size and ImageChops.difference(a_, b_).getbbox() is None
                print(f'- {os.path.basename(q)} ' + ('== the .aseprite export' if same else '≠ the .aseprite export: re-export the PNG from the .aseprite'))
                rc = rc or (0 if same else 1)
            if not strips:
                strips = exp
    for p in strips:
        rc = strip_check(p, os.path.basename(p) + (' (--flight-slots 4)' if flight else ''), flight + cellarg) or rc
    pose_path, pose = gait_pose(sheet, gait)
    src = [got['_a.png'], got['_b.png']] if '_a.png' in got and '_b.png' in got else ([got['.aseprite']] if '.aseprite' in got else [])
    if src:
        cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'add_gait.py'), sheet, '--gait', gait, '--src', *src,
               '--dry-run', '--work', os.path.join(work, 'add_gait'), '--aseprite-bin', exe]
        if pose_path:
            cmd += ['--pose', pose_path]
            print(f'- stride from {os.path.relpath(pose_path, ROOT)} (step_px {pose.get("step_px")})')
        else:
            print(f'- no request pose.json for {gait} (guides/{gait}_<class> or {gait}_base): add_gait needs --stride')
        r = subprocess.run(cmd, capture_output=True)
        txt = (r.stdout + r.stderr).decode('utf-8', 'replace')
        print('- add_gait.py --dry-run' + (' FAILED' if r.returncode else '') + ':')
        for ln in txt.splitlines():
            if ln.strip() and '원본 창' not in ln:
                print('    ' + ln.strip()[:300])
        rc = rc or r.returncode
        if rc:
            print('- NOT ready to register: fix the FAIL lines above and deliver again')
        else:
            print(f'- register after judging (copy the files in first): python3 tools/art/add_gait.py {sheet} --gait {gait} --src art/inbox/gait/'
                  + (f'{stem}_a.png art/inbox/gait/{stem}_b.png' if len(src) == 2 else f'{stem}.aseprite')
                  + (f' --pose {os.path.relpath(pose_path, ROOT)}' if pose_path else ' --stride <game px>'))
    print(f'- work folder: {work}')
    print(f'- after judging (pass or fail): git checkout {tip[:7]} -- <the delivered paths>   (it then counts as reviewed)')
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('stem', nargs='?')
    ap.add_argument('--list', action='store_true', help='show what is new on art-inbox and stop')
    ap.add_argument('--work', help='scratch folder (default: a new temp folder)')
    ap.add_argument('--no-base', action='store_true', help='a first delivery: do not look for a previous version')
    ap.add_argument('--base-rev', help='touch-ups: the 바탕 hash of the queue row (warns when the delivery was not made on it)')
    ap.add_argument('--aseprite-exe', default=os.environ.get('ASEPRITE_PATH') or (HEADLESS if os.path.exists(HEADLESS) else 'aseprite'))
    ap.add_argument('--no-fetch', action='store_true')
    a = ap.parse_args()
    stale = False
    if not a.no_fetch and git('fetch', '-q', 'origin', 'art-inbox') is None:
        stale = True
        print('FETCH FAILED: origin/art-inbox could not be fetched - everything below is the LAST FETCHED state, new deliveries may be missing')
    if a.list or not a.stem:
        return list_new() or (2 if stale else 0)
    # a name under art/inbox: "sheet_monster_wolf", "guides/walk_base/walk_base_a", "check_sheet_monster_giant-spider_idle"
    rel = a.stem[len('art/inbox/'):] if a.stem.startswith('art/inbox/') else a.stem
    rel = rel[:-4] if rel.endswith('.png') else rel
    stem = os.path.basename(rel)
    sub = os.path.dirname(rel)
    work = a.work or tempfile.mkdtemp(prefix='receive-')
    os.makedirs(work, exist_ok=True)
    tip = git('rev-parse', 'origin/art-inbox')
    if sub.startswith('guides/') and stem == os.path.basename(sub):
        return skeleton(rel, stem, work, a.aseprite_exe, tip)
    if rel.startswith('gait/'):
        return gait_delivery(rel, work, a.aseprite_exe, tip)
    path = f'art/inbox/{rel}.png'
    new = os.path.join(work, 'new', stem + '.png')
    os.makedirs(os.path.dirname(new), exist_ok=True)
    if not show('origin/art-inbox', path, new):
        print(f'{path} is not on origin/art-inbox')
        return 2
    revs = (git('log', '--format=%h', 'origin/art-inbox', '--', path) or '').split()
    print(f'# {stem} — art-inbox {revs[0] if revs else "?"} (tip {tip[:7]})')
    if revs:
        touched = [p for p in (git('show', '--name-only', '--format=', revs[0]) or '').split('\n') if p]
        outside = [p for p in touched if not p.startswith('art/inbox/')]
        print(f'- commit {revs[0]} touched {len(touched)} path(s)' + (f' — OUTSIDE art/inbox/: {outside}' if outside else ', all under art/inbox/'))
    # the base of a touch-up or redelivery is the last REVIEWED version = the copy on this branch. (The previous art-inbox commit
    # may be a delivery nobody looked at: its failures would be excused as "pre-existing" and the frame diff would compare
    # against it.) --base-rev names another version on purpose (the 바탕 hash of the queue row).
    base = None
    head_blob = git('rev-parse', '-q', '--verify', f'HEAD:{path}')
    new_blob = git('rev-parse', '-q', '--verify', f'origin/art-inbox:{path}')
    want = a.base_rev or ('HEAD' if head_blob and head_blob != new_blob else None)
    if a.base_rev and head_blob:
        rev_blob = git('rev-parse', '-q', '--verify', f'{a.base_rev}:{path}')
        if rev_blob != head_blob:
            print(f'- BASE MISMATCH: the queue says {a.base_rev}, but the reviewed copy on this branch is a different version '
                  '(someone redelivered in between, or the hash is wrong - the touch-up may sit on old art)')
    if not a.no_base and want:
        base = os.path.join(work, 'base', stem + '.png')
        os.makedirs(os.path.dirname(base), exist_ok=True)
        if show(want, path, base):
            print('- base: ' + ('the reviewed copy on this branch' if want == 'HEAD' else f'version at {want}'))
        else:
            base = None
            if a.base_rev:
                print(f'- base {a.base_rev} could not be read for {path}: NO base comparison was made')
    ase = os.path.join(work, 'new', stem + '.aseprite')
    # touch-ups keep the source under aseprite/, guides beside the PNG
    has_ase = show('origin/art-inbox', f'art/inbox/{rel}.aseprite', ase) or show('origin/art-inbox', f'art/inbox/aseprite/{stem}.aseprite', ase)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_delivery.py'), new]
    extra, item = sheet_args(stem)
    spots = [] if (sub.startswith('guides') or stem.startswith('check_')) else notes_spots(stem, item)
    if spots:
        both = ','.join([str(c) for c in (item.get('spots') or [])] + spots)
        cmd += ['--spot', both]
        extra = extra + ['--spot', both]
        print(f'- spot colour(s) from NOTES, not in the request yet: {" ".join(spots)} - used for this check; '
              'add them to MON_SPOTS in tools/art/requests.js before registering')
    if base:
        cmd += ['--base', base]
    if has_ase:
        cmd += ['--aseprite', ase, '--aseprite-exe', a.aseprite_exe]
    r = subprocess.run(cmd, capture_output=True)
    print(r.stdout.decode('utf-8', 'replace').rstrip())
    if sub.startswith('guides') or stem.startswith('check_'):
        # pose guides and one-pose idle checks are not game sheets: checks only, then look at the PNG itself
        print(f'- not a game sheet (guide / idle check): no conversion. Look at {new}')
        print(f'- work folder: {work}')
        print('- after judging: git checkout origin/art-inbox -- <the delivered paths> art/inbox/NOTES.md')
        return r.returncode
    sheet, previews, notes = dry_run(new, os.path.join(work, 'sheet_new'), extra)
    print('- convert (dry run' + (', ' + ' '.join(extra) if extra else ', phase3.json settings') + '):')
    for n in notes:
        print('    ' + n + ('   ← a declared spot colour is GONE at game size' if '점 색 0px' in n else ''))
    if base and sheet:
        bsheet, _, _ = dry_run(base, os.path.join(work, 'sheet_base'), extra)
        if bsheet:
            x, y = Image.open(sheet).convert('RGBA'), Image.open(bsheet).convert('RGBA')
            if x.size == y.size:
                cell = x.size[0] // 4
                counts = []
                for i in range(7):
                    box = ((i % 4) * cell, (i // 4) * cell, (i % 4 + 1) * cell, (i // 4 + 1) * cell)
                    # clearly different pixels only (any channel off by more than 32): the shared palette is rebuilt for every
                    # conversion, so unchanged areas shift by a few levels
                    d = ImageChops.difference(x.crop(box), y.crop(box))
                    m = Image.eval(d, lambda v: 255 if v > 32 else 0).convert('L').point(lambda v: 255 if v else 0)
                    counts.append(m.histogram()[255])
                print(f'- game-size pixels clearly changed per frame (idle x4, wind-up, strike, hit): {counts}'
                      + ('  ← some frames show NO visible change' if min(counts) == 0 else ''))
            else:
                print(f'- game sheet size changed: {y.size} -> {x.size}')
    if sheet:
        rp, shares = review_sheet(sheet, stem, work)
        print('- silhouette edge within +-25 luminance of the floor (all pixels in brackets): '
              + ', '.join(f'{n} {100 * e:.1f}% ({100 * v:.0f}%)' for n, e, v in shares)
              + ('   ← the OUTLINE melts into a bright floor: look at the review sheet'
                 if max(e for n, e, v in shares if n != 'dark') > 0.08 else '')
              + '  (dark: outlines always match a dark floor - judge by eye; the engine adds a rim)')
        print('- review sheet (design reference | game size x3 on dark / sand / snow): ' + rp)
    for p in previews:
        print('- preview: ' + p)
    print(f'- work folder: {work}')
    print(f'- after judging (pass or fail): git checkout {tip[:7]} -- <the delivered paths>   (it then counts as reviewed)')
    print('  NOTES.md: take it (same hash) only after EVERY new section that --list showed has been handled or moved to the queue')
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
