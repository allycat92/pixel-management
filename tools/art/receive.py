#!/usr/bin/env python3
"""Cloud-side receipt of one art-inbox delivery: fetch, check, diff against the previous version, dry-run convert.

  python3 tools/art/receive.py sheet_monster_wolf            # or the .png name
  python3 tools/art/receive.py sheet_captain_pilgrim --work /tmp/rcv --aseprite-exe /path/to/aseprite

It does the steps the reviewer otherwise repeats by hand (and has got wrong by hand):
  1. git fetch origin art-inbox; copy the PNG (and aseprite/<stem>.aseprite when present) out of origin/art-inbox
  2. find the previous version of the PNG on art-inbox (the base of a touch-up) unless --no-base
  3. check_delivery.py with the layout / cell / spots of art/requests/phase3.json, --base and --aseprite
  4. sheets.py --dry-run for the new file (and the base), with the scale and cell the registered sheet uses,
     and count the game-size pixels that changed per frame (a touch-up nobody can see changes 0)
  5. list every path the delivery commits touched (they must all be under art/inbox/)
Nothing is registered or committed: after reading the previews, run sheets.py without --dry-run yourself.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
REVIEWED = os.path.join(ROOT, 'art', 'requests', 'inbox_reviewed.txt')


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
    if it.get('scale'):
        return [], it
    cell = 96
    try:
        man = json.load(open(os.path.join(ROOT, 'assets', 'art', 'manifest.json'), encoding='utf-8'))
        for v in man.values():
            if isinstance(v, dict) and str(v.get('file', '')).endswith('/' + name) and v.get('sheet'):
                cell = v['sheet']['cell'][0]
    except (OSError, ValueError):
        pass
    return ['--scale', '0.1654', '--cell', str(cell)], it


def dry_run(png, work, extra):
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'art', 'sheets.py'), png, '--dry-run', '--work', work, *extra],
                       capture_output=True)
    out = r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
    keep = ('주의', '실패', '점 색 ', '배율', 'idle:', 'windup:', 'strike:', 'hit:', '완료', '열쇠 색 픽셀')
    notes = [ln.strip() for ln in out.splitlines() if any(k in ln for k in keep)]
    sheet = None
    for d, _, files in os.walk(work):
        for f in files:
            if f.startswith('sheet_') and f.endswith('.png') and 'pose_' not in f and 'preview' not in f:
                sheet = os.path.join(d, f)
    prev = [os.path.join(d, f) for d, _, files in os.walk(work) for f in files if f.startswith('preview')]
    return sheet, sorted(prev), notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('stem')
    ap.add_argument('--work', help='scratch folder (default: a new temp folder)')
    ap.add_argument('--no-base', action='store_true', help='a first delivery: do not look for a previous version')
    ap.add_argument('--aseprite-exe', default=os.environ.get('ASEPRITE_PATH', 'aseprite'))
    ap.add_argument('--no-fetch', action='store_true')
    a = ap.parse_args()
    stem = os.path.basename(a.stem)[:-4] if a.stem.endswith('.png') else os.path.basename(a.stem)
    work = a.work or tempfile.mkdtemp(prefix='receive-')
    os.makedirs(work, exist_ok=True)
    if not a.no_fetch:
        git('fetch', '-q', 'origin', 'art-inbox')
    tip = git('rev-parse', 'origin/art-inbox')
    path = f'art/inbox/{stem}.png'
    new = os.path.join(work, 'new', stem + '.png')
    os.makedirs(os.path.dirname(new), exist_ok=True)
    if not show('origin/art-inbox', path, new):
        print(f'{path} is not on origin/art-inbox')
        return 2
    revs = (git('log', '--format=%h', 'origin/art-inbox', '--', path) or '').split()
    print(f'# {stem} — art-inbox {revs[0] if revs else "?"} (tip {tip[:7]})')
    # paths touched since the last reviewed commit
    last = open(REVIEWED).read().strip() if os.path.exists(REVIEWED) else None
    if last and git('cat-file', '-e', last) is not None:
        touched = (git('diff', '--name-only', last, 'origin/art-inbox') or '').split('\n')
        outside = [p for p in touched if p and not p.startswith('art/inbox/')]
        print(f'- paths changed since {last[:7]}: {len([p for p in touched if p])}' + (f' — OUTSIDE art/inbox/: {outside}' if outside else ' (all under art/inbox/)'))
    base = None
    if not a.no_base and len(revs) > 1:
        base = os.path.join(work, 'base', stem + '.png')
        os.makedirs(os.path.dirname(base), exist_ok=True)
        if show(revs[1], path, base):
            print(f'- base: previous version {revs[1]}')
        else:
            base = None
    ase = os.path.join(work, 'new', stem + '.aseprite')
    has_ase = show('origin/art-inbox', f'art/inbox/aseprite/{stem}.aseprite', ase)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_delivery.py'), new]
    if base:
        cmd += ['--base', base]
    if has_ase:
        cmd += ['--aseprite', ase, '--aseprite-exe', a.aseprite_exe]
    r = subprocess.run(cmd, capture_output=True)
    print(r.stdout.decode('utf-8', 'replace').rstrip())
    extra, _ = sheet_args(stem)
    sheet, previews, notes = dry_run(new, os.path.join(work, 'sheet_new'), extra)
    print('- convert (dry run' + (', ' + ' '.join(extra) if extra else ', phase3.json settings') + '):')
    for n in notes:
        print('    ' + n)
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
    for p in previews:
        print('- preview: ' + p)
    print(f'- work folder: {work}')
    print(f'- after accepting: write {tip} to art/requests/inbox_reviewed.txt')
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
