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
  guides/<set>/<set>.aseprite     a skeleton (mannequin) from the PC: check_skeleton.py with the request's pose.json and draft (the
                                  newest v<n>/ of the set, else its draft/), strips exported and checked (run sets: check_delivery
                                  --flight-slots 4, the flight frame R4 / R8 is in the air; heavy / robe sets and walks: no flight slot)
  gait/<sheet stem>_<run|walk>.aseprite, gait/<sheet stem>_<run|walk>_a.png + _b.png
                                  final gait frames for a registered sheet. The run frames follow the sheet's movement class
                                  (tools/art/specs/gait_classes.json sheets.<id>.gait): light -> guides/run_base (newest v<n>/: v2),
                                  heavy -> guides/heavy_base, robe -> guides/robe_base (newest v<n>/, else draft/); only a light run has
                                  a flight frame. Strips checked (light run: --flight-slots 4), the .aseprite checked
                                  for a mannequin (add_gait guide_reason: joints layer, or a frame whose silhouette matches a skeleton
                                  frame at IoU > 0.85 after alignment - bottom-centre + a +-24 px search, mirrored too - against the cloud
                                  drafts, art/inbox/guides/ here AND the mannequins on origin/art-inbox - add_gait reads those itself with
                                  git, and receive also passes its extracted copy as --extra-guides; a refusal names the matched mannequin)
                                  and its export compared with the PNGs, then add_gait.py --dry-run (stride from guides/<gait>_<sheet>,
                                  else the class's base set above; walk: walk_base); the register command is printed only when everything
                                  passed
  guides/<motion>__<stem>/<motion>__<stem>.aseprite   (motion = atk | hit | idle; stem = the sheet png stem without 'sheet_')
                                  a per-character motion mannequin from the PC (docs/plans/2026-11-26_motion_frames.md): the .aseprite
                                  is the whole delivery (plus mannequin_pc.py when the PC built it with a script: it is checked out with
                                  it, SPEC section 1). The cloud exports one PNG per frame itself (f<NN>_<frame name>.png, names and
                                  planned ms from tools/art/specs/motion_bible.json + motion_chars.json) with pose_measured.json beside
                                  them (set id, durations_ms from the file, plan ms, contact / hold: gate_page.py and requests.js --motion
                                  read the set and the times from it), runs check_skeleton.py <set>.aseprite --motion <attack|hit|idle>
                                  --set <set>, compares the frames with the other characters' mannequins (aligned silhouette IoU at source
                                  size: FAIL > 0.98 on any frame of the same motion = a copied mannequin; "DO NOT ACCEPT until ..." (exit 1,
                                  no plain accept line) at >= 0.8 between the hold / contact frames of characters of the same archetype (hit:
                                  same hit weight) - requests.js --motion owns the game-size FAIL > 0.8 for attack sets, and every accept
                                  line of an attack set names the exact `node tools/art/requests.js --motion --frames <frames>` to run first),
                                  keeps the frames at <git common dir>/art-received/<set>/ ($ART_RECEIVED_DIR) where requests.js --motion
                                  reads them without --frames, writes review_<set>.png (frames at source size reduced + at game size on
                                  the dark floor, frame name and ms under each) and prints the next step
  python3 tools/art/receive.py guides/run_base/run_base
  python3 tools/art/receive.py guides/atk__class_warrior/atk__class_warrior
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
            ms_ = MOTION_SET_RE.match(r.split('/')[1]) if r.count('/') >= 2 else None
            kind = (f'  [motion mannequin {ms_.group(0)}: python3 tools/art/receive.py guides/{ms_.group(0)}/{ms_.group(0)}]' if ms_
                    else '  [skeleton guide: never game frames]')
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
    """draft < v2 < v10 (folder names of request drafts): the newest v<n>/ wins, a folder with another name (draft/: a cloud draft
    the PC has not touched up yet) only when there is no v<n>/"""
    m = re.match(r'v(\d+)$', d)
    return (1, int(m.group(1)), d) if m else (0, 0, d)


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


MOTION_SET_RE = re.compile(r'^(atk|hit|idle)__([a-z0-9][a-z0-9_-]*)$')    # <motion>__<sheet stem without 'sheet_'>
MOTIONS = {'atk': 'attack', 'hit': 'hit', 'idle': 'idle'}                   # set prefix -> check_skeleton --motion
SPECS = os.path.join(ROOT, 'tools', 'art', 'specs')
SIMILAR_WARN, SIMILAR_FAIL = 0.8, 0.98     # aligned silhouette IoU against another character's mannequin of the same motion
FLOOR_Y, HIP_X = 870, 192


def _add_gait():
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'art'))
    import add_gait
    return add_gait


def _json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def inbox_guides(work):
    """origin/art-inbox's art/inbox/guides/ (mannequins this branch may not have taken in yet) -> a folder under work, or None.
    add_gait compares gait frames with these too, and a motion mannequin is compared with the other characters' sets here."""
    names = git('ls-tree', '-r', '--name-only', 'origin/art-inbox', '--', 'art/inbox/guides')
    if not names:
        return None
    out = os.path.join(work, 'inbox_guides')
    for n in names.split('\n'):
        if n.lower().endswith(('.aseprite', '.ase', '.png')):
            dst = os.path.join(out, *n[len('art/inbox/guides/'):].split('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            show('origin/art-inbox', n, dst)
    return out if os.path.isdir(out) else None


def received_root():
    """where receive.py keeps the frames it exported from every motion set it received (accepted or not):
    $ART_RECEIVED_DIR, else <git common dir>/art-received/<set>/ (inside .git: never committed, survives a wiped scratch folder,
    shared by worktrees). requests.js --motion reads them from the same place, so its game-size similarity check (section 4) sees a
    received delivery without --frames and before the .aseprite is checked out on this branch."""
    env = os.environ.get('ART_RECEIVED_DIR')
    if env:
        return os.path.abspath(env)
    g = git('rev-parse', '--git-common-dir')
    return os.path.join(g if os.path.isabs(g) else os.path.join(ROOT, g), 'art-received') if g else None


def keep_received(set_name, fdir):
    """copy frames/ (f<NN>_<name>.png + pose_measured.json) to received_root()/<set> -> that path, or None"""
    root = received_root()
    if not root:
        return None
    dst = os.path.join(root, set_name)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(fdir, dst)
    return dst


def sheet_id(stem):
    """'class_warrior' -> the manifest id whose file is sheet_class_warrior.png ('sheet/class/warrior'), or None"""
    man = _json(os.path.join(ROOT, 'assets', 'art', 'manifest.json'))
    return next((k for k, v in man.items() if k.startswith('sheet/') and os.path.basename(v.get('file', '')) == f'sheet_{stem}.png'), None)


def motion_plan(sid, motion):
    """the planned sequence of a character's motion -> ([(frame name, ms)], contact index or None, where it comes from, hold index
    or None, group). group = what characters must differ within: the archetype (attack), the hit weight (hit), the idle kind.
    Frame names and ms only label the review; check_skeleton.py --motion --set is what judges them."""
    bible = _json(os.path.join(SPECS, 'motion_bible.json'))
    chars = _json(os.path.join(SPECS, 'motion_chars.json'))
    ch = (chars.get('chars') or {}).get(sid) or {}
    archs = bible.get('archetypes') or {}
    arch = ch.get('arch') or next((a for a, v in archs.items() if sid in (v.get('users') or [])), None)
    over = {}
    if motion == 'attack':
        seq, where = (archs.get(arch) or {}).get('attack') or {}, f'motion_bible archetypes.{arch}.attack'
        over = (ch.get('timing') or {}).get('ms') or {}
        group = f'archetype {arch}' 
    elif motion == 'hit':
        w = ((chars.get('hit') or {}).get('sheets') or {}).get(sid) or (archs.get(arch) or {}).get('hit_default')
        seq, where = ((bible.get('hit') or {}).get('weights') or {}).get(w) or {}, f'motion_bible hit.weights.{w}'
        group = f'hit weight {w}'
    else:
        idle = bible.get('idle') or {}
        kind = next((k for k, v in idle.items() if isinstance(v, dict) and sid in (v.get('users') or [])), 'humanoid')
        seq, where = idle.get(kind) or {}, f'motion_bible idle.{kind}'
        group = f'idle {kind}'
    frames = [(f.get('name', f'f{i}'), int(over.get(f.get('name'), f.get('ms', 0)))) for i, f in enumerate(seq.get('frames') or [])]
    if over and motion == 'attack':
        where += ' + motion_chars timing.ms ' + ', '.join(f'{k} {v}' for k, v in over.items())
    return frames, seq.get('contact'), where, seq.get('hold'), group


def export_frames(src, exe, out):
    """the visible layers of every Aseprite frame -> ([RGBA arrays], [ms], [tags (name, from, to)], problem)"""
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    env.pop('WAYLAND_DISPLAY', None)
    png, js = os.path.join(out, 'frames.png'), os.path.join(out, 'frames.json')
    try:
        r = subprocess.run([exe, '--batch', src, '--sheet', png, '--sheet-type', 'horizontal', '--data', js, '--format', 'json-array',
                            '--list-tags'], stdin=subprocess.DEVNULL, capture_output=True, timeout=300, env=env)
    except (OSError, subprocess.SubprocessError) as e:
        return [], [], [], f'Aseprite could not be run ({exe}): {e}'
    if r.returncode or not os.path.exists(png) or not os.path.exists(js):
        return [], [], [], 'Aseprite export failed: ' + (r.stderr or r.stdout).decode('utf-8', 'replace')[-300:]
    with open(js, encoding='utf-8') as f:
        data = json.load(f)
    im = Image.open(png).convert('RGBA')
    frames, durs = [], []
    for fr in data['frames']:
        q = fr['frame']
        frames.append(im.crop((q['x'], q['y'], q['x'] + q['w'], q['y'] + q['h'])))
        durs.append(int(fr.get('duration') or 0))
    tags = [(t.get('name'), t.get('from'), t.get('to')) for t in (data.get('meta') or {}).get('frameTags') or []]
    bad = sorted({f.size for f in frames if f.size != (384, 1024)})
    return frames, durs, tags, (f'frame size {bad}: a mannequin frame is 384x1024 (art/requests/guides/SPEC.md section 2)' if bad else None)


def game_size(fr, scale, ag):
    """one source frame -> (game-size RGBA image, source RGBA with the key colour removed): sheets.py matte, premultiplied BOX
    reduction, alpha cut at 0.45 (like the sheet conversion, without palette / outline)"""
    import numpy as np
    rgb, a, _ = ag.sh.matte(np.asarray(fr.convert('RGBA')).copy())
    clean = Image.fromarray(np.dstack([rgb, a * 255]).round().clip(0, 255).astype('uint8'), 'RGBA')
    w, h = fr.size
    small = clean.convert('RGBa').resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.BOX).convert('RGBA')
    arr = np.asarray(small).copy()
    arr[..., 3] = np.where(arr[..., 3] >= 0.45 * 255, 255, 0)
    return Image.fromarray(arr, 'RGBA'), clean


def motion_review(set_name, frames, labels, scale, work, ag):
    """review_<set>.png: per frame one column - the source frame reduced (key removed, red line = sole line y=870, blue = hip x=192),
    under it the game-size frame x2 on the dark battle floor, then the frame name and ms"""
    from PIL import ImageDraw, ImageFont
    import numpy as np
    masks = [np.asarray(f.convert('RGBA')) for f in frames]
    tops, bots = [], []
    for m in masks:
        mk = ag.frame_mask(m)
        rows = np.flatnonzero(mk.any(1))
        if len(rows):
            tops.append(rows[0])
            bots.append(rows[-1])
    y0 = max(0, (min(tops) if tops else 300) - 16)
    y1 = min(1024, max([FLOOR_Y] + bots) + 24)
    red = 3                                         # source reduction
    z = 2                                           # game-size magnification
    col = 384 // red
    gh = round((y1 - y0) * scale) * z
    sh_ = (y1 - y0) // red
    font = ImageFont.load_default()
    lab_h = 14 * 3 + 6
    head = 18
    out = Image.new('RGB', (len(frames) * (col + 8) + 8, head + sh_ + 8 + gh + 8 + lab_h), (20, 20, 20))
    d = ImageDraw.Draw(out)
    d.text((8, 3), f'{set_name}: source /{red} (red = sole line y={FLOOR_Y}, blue = hip x={HIP_X}) | game size x{scale:g} shown x{z} on the dark floor',
           fill=(220, 220, 220), font=font)
    for i, fr in enumerate(frames):
        x = 8 + i * (col + 8)
        small, clean = game_size(fr, scale, ag)
        src = Image.new('RGBA', (384, y1 - y0), (60, 60, 60, 255))
        src.alpha_composite(clean.crop((0, y0, 384, y1)))
        src = src.convert('RGB').resize((col, sh_), Image.LANCZOS)
        sd = ImageDraw.Draw(src)
        sd.line([(0, (FLOOR_Y - y0) // red), (col, (FLOOR_Y - y0) // red)], fill=(220, 60, 60))
        sd.line([(HIP_X // red, 0), (HIP_X // red, sh_)], fill=(70, 110, 220))
        out.paste(src, (x, head))
        g = small.crop((0, round(y0 * scale), small.size[0], round(y0 * scale) + gh // z))
        bg = Image.new('RGBA', g.size, (46, 58, 46, 255))
        fl = round((FLOOR_Y - y0) * scale)
        if 0 <= fl < g.size[1]:
            ImageDraw.Draw(bg).rectangle([0, fl + 1, g.size[0], g.size[1]], fill=(38, 48, 38, 255))
        bg.alpha_composite(g)
        gx = x + (col - g.size[0] * z) // 2
        out.paste(bg.convert('RGB').resize((g.size[0] * z, g.size[1] * z), Image.NEAREST), (gx, head + sh_ + 8))
        ty = head + sh_ + 8 + gh + 6
        for k, (txt, colr) in enumerate(labels[i]):
            d.text((x, ty + k * 14), txt, fill=colr, font=font)
    path = os.path.join(work, f'review_{set_name}.png')
    out.save(path)
    return path


def motion_skeleton(rel, name, work, exe, tip):
    """a per-character motion mannequin (guides/<motion>__<stem>/<motion>__<stem>.aseprite, the whole delivery): export the frames,
    check_skeleton.py --motion --set, similarity to the other characters' mannequins of the same motion, review sheet, next step"""
    m = MOTION_SET_RE.match(name)
    motion, stem = MOTIONS[m.group(1)], m.group(2)
    path = f'art/inbox/{rel}.aseprite'
    new = os.path.join(work, 'new', name + '.aseprite')
    os.makedirs(os.path.dirname(new), exist_ok=True)
    if not show('origin/art-inbox', path, new):
        print(f'{path} is not on origin/art-inbox')
        return 2
    revs = (git('log', '--format=%h', 'origin/art-inbox', '--', path) or '').split()
    print(f'# {name} (motion mannequin: {motion} of sheet_{stem}) — art-inbox {revs[0] if revs else "?"} (tip {tip[:7]})')
    rc = 0
    if revs:
        touched = [p for p in (git('show', '--name-only', '--format=', revs[0]) or '').split('\n') if p]
        outside = [p for p in touched if not p.startswith('art/inbox/')]
        if outside:
            print(f'  FAIL: commit {revs[0]} touched paths OUTSIDE art/inbox/: {outside} (the PC writes art/inbox/ only)')
            rc = 1
    script = f'art/inbox/guides/{name}/mannequin_pc.py'
    others = [p for p in (git('ls-tree', '-r', '--name-only', 'origin/art-inbox', '--', f'art/inbox/guides/{name}') or '').split('\n')
              if p and p not in (path, script)]
    has_script = git('cat-file', '-e', f'origin/art-inbox:{script}') is not None
    print('- mannequin_pc.py: ' + (f'{script} is on art-inbox - read it; it is checked out with the delivery (SPEC section 1: keep the script)'
                                    if has_script else 'none (the README asks for it when the PC built the frames with a script)'))
    if others:
        print(f'- WARN: only {name}.aseprite (+ mannequin_pc.py) is the delivery (the cloud exports the frames itself); ignored: {others}')
    take = f'{path}' + (f' {script}' if has_script else '') + ' art/inbox/NOTES.md' 
    sid = sheet_id(stem)
    req = os.path.join(ROOT, 'art', 'requests', 'guides', name, 'README.md')
    print(f'- sheet: {sid or "NOT REGISTERED (no manifest entry with file sheet_" + stem + ".png)"}; request: '
          + (os.path.relpath(req, ROOT) if os.path.exists(req) else f'NONE at art/requests/guides/{name}/README.md'))
    plan, contact, where, hold, group = motion_plan(sid, motion) if sid else ([], None, 'no sheet id', None, None)
    print(f'- plan: {len(plan)} frames from {where}' + (f', contact = frame {contact}' if contact is not None else '')
          + (': ' + ', '.join(f'{n} {v}' for n, v in plan) if plan else ''))
    # 1. check_skeleton (the shared interface: the same command the PC runs before delivering)
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'check_skeleton.py'), new, '--motion', motion, '--set', name, '--aseprite-exe', exe]
    print(f'- check_skeleton.py {name}.aseprite --motion {motion} --set {name}:')
    r = subprocess.run(cmd, capture_output=True)
    txt = (r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')).rstrip()
    if r.returncode == 2 and ('unrecognized arguments' in txt or 'invalid choice' in txt):
        print('  FAIL: this check_skeleton.py does not know --motion / --set yet (another job adds them): the mannequin is NOT checked')
        print('    ' + txt.splitlines()[-1][:300])
        rc = 1
    else:
        for ln in txt.splitlines():
            print('    ' + ln[:300])
        if r.returncode:
            print(f'  FAIL: check_skeleton.py exit {r.returncode}')
            rc = 1
    # 2. frames: export, sizes, ms against the plan
    frames, durs, tags, problem = export_frames(new, exe, os.path.join(work, 'export'))
    if problem:
        print(f'  FAIL: {name}.aseprite: {problem}')
        return 1
    if len(frames) != len(plan):
        print(f'- frames: {len(frames)} in the file, {len(plan)} planned (check_skeleton decides whether a droppable frame may be left out)')
    print('- tags: ' + (', '.join(f'{t} {a}-{b}' for t, a, b in tags) or 'none') + f' (one tag per motion: {motion})')
    fdir = os.path.join(work, 'frames')
    shutil.rmtree(fdir, ignore_errors=True)
    os.makedirs(fdir)
    names, labels = [], []
    for i, (fr, ms) in enumerate(zip(frames, durs)):
        pn, pms = plan[i] if i < len(plan) and len(frames) == len(plan) else (None, None)
        fn = f'f{i:02d}' + (f'_{re.sub(r"[^A-Za-z0-9]+", "_", pn).strip("_")}' if pn else '') + '.png'
        fr.save(os.path.join(fdir, fn))
        names.append(fn)
        lab = [(f'f{i:02d} {pn or "?"}', (230, 230, 230)), (f'{ms} ms' + (f' (plan {pms})' if pms is not None and pms != ms else ''),
                                                             (230, 230, 230) if pms in (None, ms) else (240, 170, 60))]
        if contact is not None and i == contact and len(frames) == len(plan):
            lab.append(('CONTACT', (240, 80, 80)))
        labels.append(lab)
    with open(os.path.join(fdir, 'pose_measured.json'), 'w', encoding='utf-8') as f:
        # gate_page.py takes the set id and the frame times from here (the folder name is a work folder, not a set id); requests.js
        # --motion takes the set, hold and contact from here. Beside these frames it also marks them as mannequin frames for add_gait.
        json.dump(dict(set=name, motion=motion, sheet=sid, source=f'{name}.aseprite', art_inbox=revs[0] if revs else None, tip=tip,
                       files=names, names=[n for n, _ in plan] if len(frames) == len(plan) else None, durations_ms=[int(d) for d in durs],
                       plan_ms=[v for _, v in plan] if len(frames) == len(plan) else None,
                       contact=contact if len(frames) == len(plan) else None, hold=hold if len(frames) == len(plan) else None,
                       tags=[list(t) for t in tags]), f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'- frames exported (visible layers, joints hidden): {fdir}/ ' + ' '.join(names) + ' + pose_measured.json (set id, durations_ms)')
    kept = keep_received(name, fdir)
    print(f'- received frames kept at {kept}/ (node tools/art/requests.js --motion reads them there without --frames)' if kept
          else '  WARN: no git dir here: the frames are NOT kept for requests.js --motion - pass --frames yourself')
    off = [f'{n} {d} ms (plan {p})' for n, d, (_, p) in zip(names, durs, plan) if len(frames) == len(plan) and d != p]
    if off:
        print('- ms differ from the plan: ' + ', '.join(off))
    # 3. two characters must not share a guide frame. FAIL: any frame of another character's mannequin of the same motion at aligned
    # silhouette IoU > 0.98 (a copy). WARN: only the hold / contact frames of characters in the same group (attack: archetype; hit: hit
    # weight) above 0.8 - near-idle frames (in, settle, recover) of any two characters are alike and say nothing.
    ag = _add_gait()
    import numpy as np
    extra = inbox_guides(work)
    mine = [ag._crop(ag.frame_mask(np.asarray(f))) for f in frames]
    keyed = len(frames) == len(plan)
    my_keys = {k: v for k, v in (('hold', hold), ('contact', contact)) if v is not None and keyed and v < len(frames)}
    seen, worst, warns = set(), (0.0, None, None, None), []
    for root in [os.path.join(ROOT, 'art', 'inbox', 'guides')] + ([extra] if extra else []):
        for other in sorted(os.listdir(root)) if os.path.isdir(root) else []:
            om = MOTION_SET_RE.match(other)
            f = os.path.join(root, other, other + '.aseprite')
            if not om or other == name or om.group(1) != m.group(1) or other in seen or not os.path.exists(f):
                continue
            seen.add(other)
            try:
                theirs = [ag._crop(x) for x in ag._ase_guide_masks(f, exe)]
            except ag.Fail as e:
                print(f'  FAIL: {other}: {e}')
                rc = 1
                continue
            for i, a_ in enumerate(mine):
                for j, b_ in enumerate(theirs):
                    if a_ is not None and b_ is not None and min(a_.sum(), b_.sum()) / max(a_.sum(), b_.sum()) > worst[0]:
                        v = ag.aligned_iou(a_, b_)[0]
                        if v > worst[0]:
                            worst = (v, names[i], other, j)
            osid = sheet_id(om.group(2))
            oplan, ocontact, _, ohold, ogroup = motion_plan(osid, motion) if osid else ([], None, '', None, None)
            if not my_keys or group is None or ogroup != group or len(theirs) != len(oplan):
                continue
            for key, i in my_keys.items():
                j = {'hold': ohold, 'contact': ocontact}[key]
                if j is None or j >= len(theirs) or mine[i] is None or theirs[j] is None:
                    continue
                v = ag.aligned_iou(mine[i], theirs[j])[0]
                warns.append((v, key, other, i, j))
    if worst[1]:
        msg = f'{worst[1]} vs {worst[2]} frame {worst[3]:02d}: aligned silhouette IoU {worst[0]:.3f} (source size)'
        if worst[0] > SIMILAR_FAIL:
            print(f'  FAIL: same guide frame as another character ({msg} > {SIMILAR_FAIL}): every character moves in their own way')
            rc = 1
        else:
            print(f'- closest frame of any other {m.group(1)} mannequin: {msg} (FAIL only above {SIMILAR_FAIL}: a copy)')
    else:
        print(f'- no other {m.group(1)}__* mannequin to compare with (art/inbox/guides/ here and on art-inbox)')
    # the game-size verdict on hold / contact of the same archetype belongs to requests.js --motion (section 4, attack sets);
    # receive prints the exact command, and a source-size IoU >= 0.8 here blocks the accept line until that check has been run
    rq = f'node tools/art/requests.js --motion --frames {kept or fdir}'
    blocked = []
    if warns:
        for v, key, other, i, j in sorted(warns, reverse=True):
            line = f'{key}: {names[i]} vs {other} frame {j:02d}, aligned silhouette IoU {v:.3f} (source size; same {group})'
            if v >= SIMILAR_WARN:
                until = (f'`{rq}` shows {key} of {other} vs {name} <= {SIMILAR_WARN} at game size (section 4) - if it FAILs there, '
                         'send it back to the PC' if motion == 'attack' else
                         f'the PC redraws the {key} frame apart from {other} (requests.js has no game-size check for {motion} sets: this is it)')
                print(f'  DO NOT ACCEPT until {until}: {line} >= {SIMILAR_WARN}, close to another character of the same {group}')
                blocked.append(line)
            else:
                print(f'- {line}')
    elif my_keys and group:
        print(f'- hold / contact: no other mannequin of the same {group} delivered yet')
    # 4. review sheet
    item = sheet_args(f'sheet_{stem}')[1]
    scale = item.get('scale') or 0.1654
    rp = motion_review(name, frames, labels, scale, work, ag)
    print(f'- review sheet (source /3 | game size x{scale:g} on the dark floor, name and ms under each frame): {rp}')
    print(f'- work folder: {work}')
    sim = (f'run `{rq}` and read section 4 (game-size hold / contact IoU of {name} against every character of the same archetype: '
           'any FAIL there = reject)' if motion == 'attack' else
           f'requests.js --motion has no game-size similarity check for {motion} sets: the hold / contact lines above are the check')
    if rc:
        print(f'- NOT accepted: send the FAIL lines above to the PC (dot_queue row of {name}; art/requests/pc_notes.md) and wait for a redelivery.')
        print(f'  after judging: git checkout {tip[:7]} -- {take}   (it then counts as reviewed)')
    elif blocked:
        print(f'- NOT accepted yet: {len(blocked)} DO NOT ACCEPT line(s) above (hold / contact >= {SIMILAR_WARN} against a character of the '
              f'same {group}).')
        if motion == 'attack':
            print(f'    first: {rq}')
            print(f'    accept only if section 4 shows no FAIL for {name}: git checkout {tip[:7]} -- {take}, set the dot_queue row of {name} '
                  f'to done (frames for gate 1: python3 tools/art/gate_page.py OUT.html {fdir})')
            print(f'    if it FAILs: write what to change in the dot_queue row of {name} for the PC, then the same git checkout (it counts as reviewed)')
        else:
            print(f'    reject: write which frame to redraw in the dot_queue row of {name} for the PC, then git checkout {tip[:7]} -- {take} '
                  '(it counts as reviewed)')
    else:
        print('- next: judge the review sheet by eye (the contact frame must read on its own at game size; hit: feet planted, '
              'head and shoulders snap away and come back), and ' + sim + '. Then:')
        print(f'    accept (only after `{rq}` shows no FAIL in section 4): ' if motion == 'attack' else '    accept: ', end='')
        print(f'git checkout {tip[:7]} -- {take}, set the dot_queue row of {name} to done; the frames in '
              f'{fdir}/ (f<NN>_<name>.png + pose_measured.json) are this character\'s guide frames for the GPT strip and gate 1 '
              f'(python3 tools/art/gate_page.py OUT.html {fdir})')
        print(f'    reject: write what to change in the dot_queue row of {name} for the PC, then the same git checkout (it counts as reviewed)')
    return rc or (1 if blocked else 0)


GAIT_RE = re.compile(r'^gait/(sheet_[^/]+?)_(run|walk)(?:_([ab]))?(?:\.aseprite)?$')


GAIT_CLASSES = os.path.join(ROOT, 'tools', 'art', 'specs', 'gait_classes.json')
CLASS_BASE = {'light': 'run_base', 'heavy': 'heavy_base', 'robe': 'robe_base'}   # movement class -> the mannequin set of its run frames


def gait_class(sheet):
    """the sheet's movement class from tools/art/specs/gait_classes.json (sheets.<sheet id>.gait: light / heavy / robe / none), or None"""
    body = sheet[len('sheet_'):]
    sid = 'sheet/' + body.replace('_', '/', 1)
    try:
        with open(GAIT_CLASSES, encoding='utf-8') as f:
            return ((json.load(f).get('sheets') or {}).get(sid) or {}).get('gait')
    except (OSError, ValueError):
        return None


def gait_pose(sheet, gait):
    """the request whose stride (and, for run, whose movement class) the gait frames follow: guides/<gait>_<sheet without 'sheet_'>,
    <gait>_<last name part>, else - run - the base set of the sheet's class in gait_classes.json (light run_base, heavy heavy_base,
    robe robe_base; newest v<n>/, else draft/) or - walk - walk_base"""
    body = sheet[len('sheet_'):]
    cls = gait_class(sheet) or 'light'
    base = CLASS_BASE.get(cls, 'run_base') if gait == 'run' else f'{gait}_base'
    if gait == 'run' and cls in CLASS_BASE:
        prefix = 'run' if cls == 'light' else cls
        requested = os.path.join(ROOT, 'art', 'requests', 'gait', f'{prefix}__{body}', 'pose.json')
        if os.path.isfile(requested):
            with open(requested, encoding='utf-8') as f:
                pose = json.load(f)
            if pose.get('scaled_from'):
                return requested, pose
    for set_name in (f'{gait}_{body}', f'{gait}_{body.split("_")[-1]}', base):
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
    cls = gait_class(sheet)
    pose_path, pose = gait_pose(sheet, gait)
    # only the light run has a flight frame (slot 4 in the air); heavy / robe run frames stand on y=870 in every slot
    lifted = gait == 'run' and (pose.get('gait') == 'run' if pose_path else cls not in ('heavy', 'robe'))
    flight = ['--flight-slots', '4'] if lifted else []
    if gait == 'run':
        print(f'- movement class (tools/art/specs/gait_classes.json): {cls or "not in the table (light)"} -> mannequin '
              + (os.path.relpath(pose_path, ROOT) if pose_path else 'none found')
              + (f' (gait {pose.get("gait")})' if pose_path else '')
              + ('; strips checked with --flight-slots 4 (the light run is in the air in slot 4)' if flight else
                 '; strips checked without --flight-slots (no flight: every slot stands on y=870)'))
        if pose_path and cls in CLASS_BASE and pose.get('gait') != ('run' if cls == 'light' else cls):
            print(f'  WARN: {sheet} is {cls} in gait_classes.json but the request it follows is a {pose.get("gait")} set')
    _, item = sheet_args(sheet)
    cellarg = ['--cell', str(item['cell'])] if item.get('cell') else []
    strips = [got[s] for s in ('_a.png', '_b.png') if s in got]
    # mannequins on art-inbox that this branch has not taken in yet are compared too (add_gait --extra-guides)
    extra = inbox_guides(work)
    if '.aseprite' in got:
        # the dry run below reads the PNG strips when both are there, so the .aseprite itself is checked for a mannequin here
        # (joints layer, or frames that match a skeleton: a mannequin with its joints layer deleted, moved or mirrored)
        add_gait = _add_gait()
        add_gait.EXTRA_GUIDES[:] = [extra] if extra else []
        try:
            why = add_gait.guide_reason(got['.aseprite'], exe)
        except add_gait.Fail as e:
            why = str(e)
        if why:
            print(f'  FAIL: {stem}.aseprite is a skeleton (mannequin), not game frames: {why}')
            rc = 1
        else:
            print(f'- {stem}.aseprite: no joints layer, no frame matches a skeleton (art/requests/guides/, art/inbox/guides/ here and on art-inbox; '
                  f'aligned, mirrored too, IoU <= {add_gait.DRAFT_IOU})')
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
    src = [got['_a.png'], got['_b.png']] if '_a.png' in got and '_b.png' in got else ([got['.aseprite']] if '.aseprite' in got else [])
    if src:
        cmd = [sys.executable, os.path.join(ROOT, 'tools', 'art', 'add_gait.py'), sheet, '--gait', gait, '--src', *src,
               '--dry-run', '--work', os.path.join(work, 'add_gait'), '--aseprite-bin', exe] + (['--extra-guides', extra] if extra else [])
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
                # a refusal names the matched mannequin in full (path, frame, IoU, shift): never cut it
                print('    ' + (ln.strip() if '거부' in ln or '마네킹' in ln else ln.strip()[:300]))
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
        if MOTION_SET_RE.match(stem):
            return motion_skeleton(rel, stem, work, a.aseprite_exe, tip)
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
