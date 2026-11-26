#!/usr/bin/env python3
"""이동 부류(경량·중량·로브)별 그려진 이동 칸 요청 현황 + 엔진 표(js/gait_classes.js) 만들기.

주인 (2026-11-26): "달리기(이동)에 대해 3가지 부류를 정하고 싶어. 경량, 중량, 로브.
펑퍼짐한 천 복장을 입고 뛰는것도 좀 부자연스러울거고, 중장비를 갖추면 당연히 뛰는건 물론이고 몸이 저렇게 땅에서 떨어지거나
몸을 앞으로 기울인 채로 가누기도 어려울테니까."

분류의 원본은 tools/art/specs/gait_classes.json (시트마다 light / heavy / robe / none). 이 도구는
  (기본)    부류마다 아직 그려진 이동 칸이 없는(또는 다른 부류 마네킹으로 그려진) 시트와, 그 요청 폴더·마네킹·납품 이름·붙이는 명령을 보여 준다.
  --js      엔진이 읽는 표 js/gait_classes.js 를 다시 만든다 (index.html 이 battle.js 보다 먼저 싣는다).
  --check   js/gait_classes.js 가 JSON 과 같은지, JSON 이 등록된 전투 시트를 빠짐없이 덮는지 본다 (다르면 종료 코드 1).
  --json    현황을 JSON 으로.

요청 폴더: art/requests/gait/<요청>__<시트 png 이름에서 sheet_ 뺀 것>/ — 경량 run__, 중량 heavy__, 로브 robe__
(이미 있는 run__class_warrior, run__captain_shadowqueen 과 같은 꼴). 부류와 상관없이 엔진에는 시트의 anims.run 한 줄로 붙는다:
납품 art/inbox/gait/<시트 png 이름>_run_a.png + _b.png, 붙이기 add_gait.py <시트> --gait run --pose <부류 마네킹 pose.json>.
엔진(js/battle.js gaitClassOf)은 시트 meta.gait → 이 표 → 경량 순으로 부류를 안다.

이 도구는 assets/ 와 art/inbox/ 를 쓰지 않는다 (--js 만 js/gait_classes.js 를 쓴다).
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPEC = 'tools/art/specs/gait_classes.json'
MANIFEST = 'assets/art/manifest.json'
JS_OUT = 'js/gait_classes.js'
CLASSES = ('light', 'heavy', 'robe')
# 부류 → 요청 폴더 머리 · 마네킹 세트 (art/requests/guides/<세트>/)
REQ_PREFIX = {'light': 'run', 'heavy': 'heavy', 'robe': 'robe'}
GUIDE_SET = {'light': 'run_base', 'heavy': 'heavy_base', 'robe': 'robe_base'}
KO = {'light': '경량', 'heavy': '중량', 'robe': '로브', 'none': '해당 없음'}


def rel(p):
    return os.path.relpath(p, ROOT)


def load(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f:
        return json.load(f)


def guide_of(cls, spec):
    """부류의 마네킹 pose.json 과 상태 (final = 확정 v<n>, draft = 클라우드 초안 — PC 가 확정 세트를 만들 때까지)."""
    if cls == 'light':
        g = spec.get('classes', {}).get('light', {}).get('guide') or 'art/requests/guides/run_base/v2/pose.json'
        return g, 'final'
    base = os.path.join(ROOT, 'art/requests/guides', GUIDE_SET[cls])
    vs = sorted(glob.glob(os.path.join(base, 'v*', 'pose.json')),
                key=lambda p: int(re.sub(r'\D', '', os.path.basename(os.path.dirname(p))) or 0))
    if vs:
        return rel(vs[-1]), 'final'
    d = os.path.join(base, 'draft', 'pose.json')
    return (rel(d), 'draft') if os.path.exists(d) else (None, 'missing')


def pose_class(pose_path):
    """그려진 run 칸이 어느 부류 마네킹 위에 그려졌는가 (pose.json 의 movement_class, 없고 gait 가 run 이면 경량)."""
    if not pose_path or not os.path.exists(os.path.join(ROOT, pose_path)):
        return None
    try:
        pj = load(pose_path)
    except (OSError, ValueError):
        return None
    return pj.get('movement_class') or ('light' if pj.get('gait') == 'run' else None)


def drawn_class(meta):
    """시트에 붙은 그려진 run 칸의 부류: meta.gait (add_gait 가 적을 때) → 붙인 기록의 pose.json → 알 수 없음."""
    if 'run' not in (meta.get('anims') or {}):
        return None
    if meta.get('gait') in CLASSES:
        return meta['gait']
    rec = (meta.get('gaits') or {}).get('run') or {}
    return pose_class(rec.get('pose')) or 'unknown'


def status(spec, man):
    sheets = spec['sheets']
    reg = {k: v for k, v in man.items() if k.startswith('sheet/') and isinstance(v, dict) and 'sheet' in v}
    rows = []
    for sid in sorted(set(sheets) | set(reg)):
        cls = (sheets.get(sid) or {}).get('gait')
        e = reg.get(sid)
        stem = os.path.splitext(os.path.basename(e['file']))[0] if e else 'sheet_' + sid[len('sheet/'):].replace('/', '_')
        short = stem[len('sheet_'):] if stem.startswith('sheet_') else stem
        row = {'sheet': sid, 'class': cls, 'registered': bool(e), 'stem': stem}
        if not cls:
            row['state'] = 'unclassified'
        elif cls == 'none':
            row['state'] = 'none'
        else:
            dc = drawn_class(e['sheet']) if e else None
            row['drawn'] = dc
            row['state'] = 'done' if dc == cls else ('redraw' if dc else 'needed')
            folder = f'art/requests/gait/{REQ_PREFIX[cls]}__{short}'
            g, gs = guide_of(cls, spec)
            row.update(request=folder, request_exists=os.path.isdir(os.path.join(ROOT, folder)), guide=g, guide_state=gs,
                       delivery=[f'art/inbox/gait/{stem}_run_a.png', f'art/inbox/gait/{stem}_run_b.png'],
                       receive=f'python3 tools/art/receive.py gait/{stem}_run',
                       attach=f'python3 tools/art/add_gait.py {sid} --gait run --src art/inbox/gait/{stem}_run_a.png '
                              f'art/inbox/gait/{stem}_run_b.png --pose {g}')
        rows.append(row)
    return rows


def js_table(spec):
    cd = spec['class_defaults']
    sheets = {k: v['gait'] for k, v in sorted(spec['sheets'].items())}
    for k, v in sorted((spec.get('pending_packages') or {}).items()):
        sheets.setdefault(k, v['gait'])
    t = {
        'sheets': sheets,
        'base': cd['base'], 'adv': cd['adv'], 'master': cd['master'],
        'captain_style': cd['captain_style'],
        'hero_class_to_sheet': cd['hero_class_to_sheet'],
        'enemy_tpl': cd['enemy_tpl'], 'enemy_override': cd['enemy_override'],
    }
    body = json.dumps(t, ensure_ascii=False, indent=1, sort_keys=True)
    return ('// 이동 부류 표 (경량 light · 중량 heavy · 로브 robe · none = 네발·다족·떠 있는 몸) — 손으로 고치지 말 것.\n'
            f'// 만든 곳: python3 tools/art/gait_requests.py --js  (원본 {SPEC}, 검사: --check)\n'
            '// 엔진(js/battle.js gaitClassOf)은 시트 meta.gait → 이 표의 sheets → (시트 없는 유닛) 괴물 이름·틀, 대장 방식, 직업(master → adv → base) 순으로 본다.\n'
            f'const GAIT_CLASSES = {body};\n')


def check(spec, man):
    errs = []
    reg = {k for k, v in man.items() if k.startswith('sheet/') and isinstance(v, dict) and 'sheet' in v}
    cls = set(spec['sheets'])
    for k in sorted(reg - cls):
        errs.append(f'등록된 시트가 {SPEC} 에 없다: {k}')
    for k in sorted(cls - reg):
        errs.append(f'{SPEC} 의 시트가 등록되어 있지 않다: {k} (등록 전이면 pending_packages 로)')
    for k, v in spec['sheets'].items():
        if v.get('gait') not in CLASSES + ('none',):
            errs.append(f'{k}: 모르는 부류 {v.get("gait")!r}')
    p = os.path.join(ROOT, JS_OUT)
    cur = open(p, encoding='utf-8').read() if os.path.exists(p) else None
    if cur != js_table(spec):
        errs.append(f'{JS_OUT} 가 {SPEC} 와 다르다 — python3 tools/art/gait_requests.py --js')
    for m in man.values():
        meta = m.get('sheet') if isinstance(m, dict) else None
        if meta and meta.get('gait') not in (None,) + CLASSES:
            errs.append(f'{m.get("file")}: meta.gait {meta.get("gait")!r} 는 light/heavy/robe 가 아니다')
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--js', action='store_true', help=f'{JS_OUT} 를 다시 만든다')
    ap.add_argument('--check', action='store_true', help='표·분류 검사 (다르면 종료 코드 1)')
    ap.add_argument('--json', action='store_true', help='현황을 JSON 으로')
    ap.add_argument('--all', action='store_true', help='다 그려진 시트와 none 도 보여 준다')
    a = ap.parse_args()
    spec, man = load(SPEC), load(MANIFEST)
    if a.js:
        with open(os.path.join(ROOT, JS_OUT), 'w', encoding='utf-8') as f:
            f.write(js_table(spec))
        print(f'{JS_OUT} 를 썼다 ({len(spec["sheets"])} 시트 + 대기 {len(spec.get("pending_packages") or {})})')
        return 0
    if a.check:
        errs = check(spec, man)
        for e in errs:
            print('FAIL', e)
        print('RESULT:', 'FAIL' if errs else 'PASS', f'({len(spec["sheets"])} 시트 분류, {JS_OUT} 동기)')
        return 1 if errs else 0
    rows = status(spec, man)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    for cls in CLASSES:
        rs = [r for r in rows if r['class'] == cls]
        g, gs = guide_of(cls, spec)
        need = [r for r in rs if r['state'] in ('needed', 'redraw')]
        done = [r for r in rs if r['state'] == 'done']
        print(f'== {cls} ({KO[cls]}): 시트 {len(rs)} · 그려짐 {len(done)} · 필요 {len(need)}  마네킹 {g} [{gs}]')
        if gs == 'draft':
            print(f'   마네킹이 아직 클라우드 초안이다 — PC 세션이 확정 세트(art/requests/guides/{GUIDE_SET[cls]}/v1/)를 만든 뒤 요청한다')
        for r in (rs if a.all else need):
            extra = ''
            if r['state'] == 'redraw':
                extra = f'  (지금 run 칸은 {r["drawn"]} 마네킹으로 그려졌다 → 다시)'
            elif r['state'] == 'done':
                extra = '  (그려짐)'
            mark = '있음' if r.get('request_exists') else '없음'
            print(f'   {r["sheet"]:32s} {r["request"]}/ [{mark}]{extra}')
    nn = [r for r in rows if r['state'] == 'none']
    un = [r for r in rows if r['state'] == 'unclassified']
    print(f'== none (해당 없음, 네발·다족·떠 있는 몸): {", ".join(r["sheet"] for r in nn) or "-"}')
    if un:
        print(f'== 분류 안 됨 ({SPEC} 에 넣을 것): {", ".join(r["sheet"] for r in un)}')
    print('납품 이름은 부류와 상관없이 art/inbox/gait/<시트 png 이름>_run_a.png + _b.png, 붙이기는 add_gait.py <시트> --gait run --pose <부류 마네킹>'
          ' (--json 에 시트마다 receive/attach 명령).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
