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
  6. write review.png: the design reference (portrait / concept) beside the game-size sheet on three floors (dark, sand, snow),
     and print how much of the sprite is within +-25 luminance of each floor (it vanishes there)
Nothing is registered or committed: after reading review.png, run sheets.py <file> yourself (settings come from phase3.json).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
FLOORS = (('dark', (46, 58, 46)), ('sand', (201, 164, 90)), ('snow', (226, 232, 238)))
HEADLESS = os.path.join(ROOT, 'tools', 'art', 'ase_headless.sh')


def unreviewed():
    out = git('diff', '--name-only', 'HEAD', 'origin/art-inbox', '--', 'art/inbox') or ''
    return [p for p in out.split('\n') if p]


def list_new():
    files = unreviewed()
    if not files:
        print('nothing new: art/inbox on origin/art-inbox matches this branch')
        return 0
    print(f'{len(files)} path(s) differ from this branch (unreviewed):')
    for f in files:
        h = git('log', '-1', '--format=%h %ci %s', 'origin/art-inbox', '--', f) or '?'
        who = 'PC' if '(Aseprite)' in h else 'GPT'
        print(f'  [{who}] {f}  ←  {h}')
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
    path = os.path.join(work, 'review.png')
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


def skeleton(rel, name, work, exe, tip):
    """a skeleton set delivered as one layered .aseprite (guides/<set>/<set>.aseprite): measure it, list what changed against
    the draft of the request, and make the strips + preview from it (the Aseprite session does not have to export them)."""
    path = f'art/inbox/{rel}.aseprite'
    new = os.path.join(work, 'new', name + '.aseprite')
    os.makedirs(os.path.dirname(new), exist_ok=True)
    if not show('origin/art-inbox', path, new):
        print(f'{path} is not on origin/art-inbox')
        return 2
    revs = (git('log', '--format=%h', 'origin/art-inbox', '--', path) or '').split()
    print(f'# {name} (skeleton) — art-inbox {revs[0] if revs else "?"} (tip {tip[:7]})')
    req = os.path.join(ROOT, 'art', 'requests', 'guides', name)
    drafts = sorted(d for d in (os.listdir(req) if os.path.isdir(req) else []) if os.path.exists(os.path.join(req, d, name + '.aseprite')))
    out = os.path.join(work, 'skeleton')
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_skeleton.py'), new, '--export', out, '--aseprite-exe', exe]
    if drafts:
        cmd += ['--base', os.path.join(req, drafts[-1], name + '.aseprite'), '--pose', os.path.join(req, drafts[-1], 'pose.json')]
        print(f'- draft of the request: art/requests/guides/{name}/{drafts[-1]}/')
    r = subprocess.run(cmd, capture_output=True)
    print(r.stdout.decode('utf-8', 'replace').rstrip() or r.stderr.decode('utf-8', 'replace')[-400:])
    rc = r.returncode
    for s in 'ab':
        strip = os.path.join(out, f'{name}_{s}.png')
        if os.path.exists(strip):
            c = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_delivery.py'), strip], capture_output=True)
            lines = [ln for ln in c.stdout.decode('utf-8', 'replace').splitlines() if ln.startswith(('RESULT', 'FAIL', 'WARN', 'ERROR'))]
            print(f'- strip {s}: ' + ' | '.join(lines))
            rc = rc or c.returncode
    print(f'- work folder: {work} (strips, {name}_preview.gif and pose_measured.json under skeleton/)')
    print('- after judging: git checkout origin/art-inbox -- <the delivered paths> art/inbox/NOTES.md')
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
    if not a.no_fetch:
        git('fetch', '-q', 'origin', 'art-inbox')
    if a.list or not a.stem:
        return list_new()
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
    base = None
    want = a.base_rev or (revs[1] if len(revs) > 1 else None)
    if a.base_rev and len(revs) > 1 and not (revs[1].startswith(a.base_rev[:7]) or a.base_rev.startswith(revs[1][:7])):
        print(f'- BASE MISMATCH: the queue says {a.base_rev}, but the version before this delivery is {revs[1]} '
              '(someone redelivered in between - the touch-up may sit on old art)')
    if not a.no_base and want:
        base = os.path.join(work, 'base', stem + '.png')
        os.makedirs(os.path.dirname(base), exist_ok=True)
        if show(want, path, base):
            print(f'- base: version at {want}')
        else:
            base = None
    ase = os.path.join(work, 'new', stem + '.aseprite')
    # touch-ups keep the source under aseprite/, guides beside the PNG
    has_ase = show('origin/art-inbox', f'art/inbox/{rel}.aseprite', ase) or show('origin/art-inbox', f'art/inbox/aseprite/{stem}.aseprite', ase)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_delivery.py'), new]
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
    extra, _ = sheet_args(stem)
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
              + ('   ← the OUTLINE melts into a bright floor: look at review.png'
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
