"""3D-mannequin guides for a movement request folder (owner decision 2026-11-28: graphics via a virtual 3D mannequin ->
motion -> sprite strips -> the painter paints the character over them; who paints = specs/carry3d.json `painter.name`,
common.load_painter - GPT until the owner switches back to Antigravity).

  python3 tools/mannequin3d/request.py sheet/captain/blademaster --out DIR [--force]     # guides only (scratch)
  python3 tools/art/gait_requests.py --write sheet/captain/blademaster --guides 3d [--force]   # the whole request + README

Writes the same request-folder files as the 2D path (tools/art/run_request_guides.py build()), from the character's fitted
3D mannequin (specs/carry3d.json entry whose `sheet` is the sheet id; fit.py, motions.py, checks.py):
  guide_<p>_a.png / _b.png        the 3D guide strips with joint dots (SPEC.md colours), the held prop as a see-through ghost
                                  (teal outline, dashed where a body part is in front) and a teal ring on each holding hand;
                                  1536x1024, 4 slots of 384, hip column x=192, standing soles on y=870, #FF00FF
  guide_<p>_plain_a.png / _b.png  the same without dots, rings and ground line (the underlay to paint over)
  size_<p>_a.png / _b.png         the SIZE panel (accepted idle, faint, placed as the engine places it, with the cyan outline of
                                  the 3D mannequin's first frame of the strip at the same scale) + the 4 guide frames with the
                                  floor line, hip columns, 32-px band, planted-toe ticks and the flight line
                                  (run_request_guides.size_panel - the same drawing as the 2D requests)
  pose.json                       the run_base / heavy_base / robe_base schema at the sheet's own scale (phase3.json) plus
                                  `mannequin3d` (marker: carry key, sha256 of the carry entry and of every guide PNG,
                                  camera, personality, check results); `source` names tools/mannequin3d, so add_gait.py
                                  compares deliveries against these guides (m3d_match) and receive.py attaches with it
  preview_<p>.gif                 the 8 frames at guide size, at the class cadence
  preview_<p>_game_x4.gif         the 8 frames as the add_gait window at the sheet scale, x4

Refuses (Fail) when the character has no carry3d.json entry, when its gait does not match the sheet's movement class
(tools/art/specs/gait_classes.json), when the fit falls back to the coarse registered cell, and when any mannequin check
FAILs (checks.py) - a guide that breaks the floor / planted-foot / band / wrist-range rules never reaches a painter.
Writes only into the request folder (or --out). Deterministic: the same inputs give byte-identical files.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'tools', 'art'))

import build  # noqa: E402
import checks  # noqa: E402
import fit as fitmod  # noqa: E402
import run_request_guides as rg  # noqa: E402
from common import CARRY_JSON, CELL, ANCHOR, load_carry, load_painter, sheet_scale, on_bg, save_gif, strip_of  # noqa: E402
from motions import gait_spec, leg_factor, personality  # noqa: E402
from render import Camera, SLOT_W  # noqa: E402

GAIT_OF = {'light': 'run_light', 'heavy': 'run_heavy', 'robe': 'run_robe'}
YAW, CHEST_OPEN = 15.0, 30.0
MARK = 'tools/mannequin3d (request.py) 3D mannequin guide - a MANNEQUIN, never game art (add_gait refuses it)'


def carry_entry(sid, path=CARRY_JSON):
    """(key, entry) of the carry3d.json character whose `sheet` is sid -> Fail when there is none"""
    chars = load_carry(path)
    hits = [(k, v) for k, v in chars.items() if v.get('sheet') == sid]
    if not hits:
        raise rg.Fail(f'{sid}: no entry in {os.path.relpath(path, REPO)} - fit and author the character there first '
                      '(props, arms, weapon_limit, personality), then build its 3D request')
    if len(hits) > 1:
        raise rg.Fail(f'{sid}: {len(hits)} entries in carry3d.json ({", ".join(k for k, _ in hits)})')
    return hits[0]


def carry_sha(entry):
    return hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def file_sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def names(prefix):
    return ([f'guide_{prefix}_{h}.png' for h in 'ab'] + [f'guide_{prefix}_plain_{h}.png' for h in 'ab']
            + [f'size_{prefix}_{h}.png' for h in 'ab'] + ['pose.json', f'preview_{prefix}.gif', f'preview_{prefix}_game_x4.gif'])


def render(sid, cls=None, carry_path=CARRY_JSON):
    """fit + gait + checks for one sheet -> dict (no files written)"""
    cls = cls or rg.movement_class(sid)
    key, entry = carry_entry(sid, carry_path)
    if entry.get('gait') != GAIT_OF[cls]:
        raise rg.Fail(f'{sid}: carry3d.json {key} gait {entry.get("gait")!r} but the sheet is {cls} ({GAIT_OF[cls]}) in '
                      'tools/art/specs/gait_classes.json')
    carry = dict(entry)
    carry.setdefault('chest_open', CHEST_OPEN)
    try:
        pz = personality(carry)
    except ValueError as e:
        raise rg.Fail(f'{sid}: {e}')
    P, rep, _ = fitmod.fit(sid, YAW, override=carry.get('fit_override'))
    if rep['coarse_source']:
        raise rg.Fail(f'{sid}: the fit fell back to the coarse registered cell ({rep["source"]}) - the accepted idle drawing '
                      f'art/inbox/{os.path.basename(rep["source"])} must be in this checkout (git fetch origin art-inbox)')
    scale = sheet_scale(sid)
    cam = Camera(yaw=YAW)
    spec = gait_spec(carry['gait'], scale, leg_factor(P))
    g = build.render_gait(P, carry, spec, cam, scale)
    res = [(checks.OK, f'fit source: {rep["source"]}')]
    res += checks.gait_checks(spec, g['recs'], g['bodies'], g['plain'], cam, carry)
    return {'key': key, 'entry': entry, 'carry': carry, 'personality': pz, 'P': P, 'rep': rep, 'scale': scale, 'cam': cam,
            'spec': spec, 'g': g, 'checks': res, 'cls': cls}


def build_request(sid, outdir, cls=None, man=None, force=False, carry_path=CARRY_JSON, allow_fail=False):
    """write the 3D guide files of one request folder -> geometry dict like run_request_guides.build() (+ 'm3d')"""
    man = man or rg.load_json(rg.MANIFEST)
    geo = rg.geometry(sid, man)
    cls = cls or rg.movement_class(sid)
    p = rg.PREFIX[cls]
    files = names(p)
    os.makedirs(outdir, exist_ok=True)
    if not force:
        there = [n for n in files if os.path.exists(os.path.join(outdir, n))]
        if there:
            raise rg.Fail(f'{outdir}: {", ".join(there)} already there - pass --force to rebuild')
    r = render(sid, cls, carry_path)
    fails = [m for lv, m in r['checks'] if lv == checks.FAIL]
    if fails and not allow_fail:
        raise rg.Fail(f'{sid}: the 3D mannequin fails its checks - fix specs/carry3d.json first:\n    ' + '\n    '.join(fails))
    g, spec = r['g'], r['spec']
    strips = [np.asarray(strip_of(g['slots'][k * 4:(k + 1) * 4])) for k in range(2)]
    plains = [np.asarray(strip_of(g['plain'][k * 4:(k + 1) * 4])) for k in range(2)]
    # files from an older request (2D: a stale scaled pose.json is replaced below; nothing else of the 2D set differs in name)
    for k, half in enumerate('ab'):
        Image.fromarray(strips[k]).save(os.path.join(outdir, f'guide_{p}_{half}.png'), optimize=True)
        Image.fromarray(plains[k]).save(os.path.join(outdir, f'guide_{p}_plain_{half}.png'), optimize=True)
    local_pose = os.path.join(outdir, 'pose.json')
    try:
        pj = os.path.relpath(local_pose, REPO).replace(os.sep, '/')
    except ValueError:
        pj = local_pose.replace(os.sep, '/')
    if pj.startswith('..'):
        pj = local_pose.replace(os.sep, '/')
    frames = g['recs']
    flight_any = any(fr.get('phase') == 'flight' for fr in frames)
    notes = ('3D MANNEQUIN (tools/mannequin3d, fitted to this character): shading = depth - lighter parts are NEARER the viewer, '
             'darker parts farther; keep that depth order when you paint (the nearer part is drawn over the farther one). The '
             'teal see-through shape is the held weapon; the teal ring marks the hand that holds it. PAINT OVER EVERY MANNEQUIN '
             'PIXEL - add_gait.py refuses strips with mannequin colours or a recoloured mannequin silhouette.',)
    for k, half in enumerate('ab'):
        frs = [fr for fr in frames if fr.get('strip') == half]
        rg.size_panel(geo, cls, half, strips[k], frs, flight_any, f'3D {pj}', os.path.join(outdir, f'size_{p}_{half}.png'),
                      outline_strip=plains[k], notes=notes)
    ms = spec['ms']
    save_gif([im.crop((0, 380, SLOT_W, 900)) for im in g['slots']], os.path.join(outdir, f'preview_{p}.gif'), ms)
    save_gif([on_bg(c, floor_y=ANCHOR[1]).resize((CELL * 4, CELL * 4), Image.Resampling.NEAREST) for c in g['cells']],
             os.path.join(outdir, f'preview_{p}_game_x4.gif'), ms)
    pose = build.gait_pose_json(spec, r['P'], r['cam'], r['carry'], frames, r['rep'], r['scale'])
    pose['source'] = MARK
    pose['mannequin3d'] = {
        'tool': 'tools/mannequin3d/request.py',
        'carry': os.path.relpath(carry_path, REPO).replace(os.sep, '/'), 'carry_key': r['key'],
        'carry_sha256': carry_sha(r['entry']),
        'sheet_scale_from': 'art/requests/phase3.json',
        'painter': load_painter(carry_path),
        'weapon_limit': r['carry'].get('weapon_limit', {'min': 0.0, 'max': 120.0}),
        'personality': r['personality'],
        'guides': {n: file_sha(os.path.join(outdir, n)) for n in files if n.endswith('.png') and n.startswith('guide_')},
        'checks': [f'[{lv}] {m}' for lv, m in r['checks']],
        'shading': 'cel shading by depth: lighter = nearer the viewer, darker = farther (near limbs light, far limbs dark)',
    }
    with open(local_pose, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pose, f, ensure_ascii=False, indent=1)
        f.write('\n')
    geo.update(cls=cls, prefix=p, pose=pj, source_pose=pj, scaled=False, strips=[f'guide_{p}_a.png', f'guide_{p}_b.png'],
               idle_offset=rg.idle_panel(geo)[3], files=files,
               m3d={'key': r['key'], 'entry': r['entry'], 'personality': r['personality'], 'checks': r['checks'],
                    'spec': spec, 'fit': r['rep'], 'painter': load_painter(carry_path)})
    return geo


def verify(folder, sid, carry_path=CARRY_JSON):
    """--check of a 3D request folder (no rendering): the marker, the carry entry unchanged since the guides were made, the
    guide PNGs unchanged, every file there -> list of problems"""
    errs = []
    local = os.path.join(folder, 'pose.json')
    try:
        with open(local, encoding='utf-8') as f:
            pose = json.load(f)
    except (OSError, ValueError) as e:
        return [f'pose.json unreadable ({e})']
    m = pose.get('mannequin3d') or {}
    if 'mannequin3d' not in str(pose.get('source', '')) or not m:
        return ['pose.json is not a 3D mannequin guide (no mannequin3d marker)']
    p = os.path.basename(folder).split('__', 1)[0]
    for n in names(p):
        if not os.path.exists(os.path.join(folder, n)):
            errs.append(f'{n} missing')
    for n, h in (m.get('guides') or {}).items():
        fp = os.path.join(folder, n)
        if os.path.exists(fp) and file_sha(fp) != h:
            errs.append(f'{n} changed since the 3D build (sha256) - rebuild with gait_requests.py --write {sid} --guides 3d --force')
    try:
        key, entry = carry_entry(sid, carry_path)
        if key != m.get('carry_key') or carry_sha(entry) != m.get('carry_sha256'):
            errs.append(f'specs/carry3d.json {key} changed since the guides were made - gait_requests.py --write {sid} --guides 3d --force')
    except rg.Fail as e:
        errs.append(str(e))
    try:
        if abs(sheet_scale(sid) - pose.get('scale', 0)) > 1e-9:
            errs.append(f'pose.json scale {pose.get("scale")} != phase3.json scale {sheet_scale(sid)}')
    except SystemExit as e:
        errs.append(str(e))
    bad = [c for c in m.get('checks', []) if c.startswith('[FAIL]')]
    if bad:
        errs.append(f'the guides were built with failing checks: {bad}')
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sheet', help='manifest id, png stem or short id (class_warrior)')
    ap.add_argument('--out', required=True, help='folder to write (the request folder is written by gait_requests.py --write)')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--carry', default=CARRY_JSON)
    a = ap.parse_args(argv)
    man = rg.load_json(rg.MANIFEST)
    try:
        sid = rg.resolve(a.sheet, man)
        geo = build_request(sid, os.path.abspath(a.out), None, man, a.force, a.carry)
    except rg.Fail as e:
        print(f'request.py: {e}', file=sys.stderr)
        return 1
    for lv, msg in geo['m3d']['checks']:
        print(f'   [{lv}] {msg}')
    print(f'{sid} [{geo["cls"]}] 3D -> {a.out}: {" ".join(geo["files"])}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
