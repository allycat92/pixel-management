#!/usr/bin/env python3
"""이동 부류(경량·중량·로브)별 그려진 이동 칸 요청 현황 + 엔진 표(js/gait_classes.js) 만들기.

주인 (2026-11-26): "달리기(이동)에 대해 3가지 부류를 정하고 싶어. 경량, 중량, 로브.
펑퍼짐한 천 복장을 입고 뛰는것도 좀 부자연스러울거고, 중장비를 갖추면 당연히 뛰는건 물론이고 몸이 저렇게 땅에서 떨어지거나
몸을 앞으로 기울인 채로 가누기도 어려울테니까."

분류의 원본은 tools/art/specs/gait_classes.json (시트마다 light / heavy / robe / none). 이 도구는
  (기본)    부류마다 아직 그려진 이동 칸이 없는(또는 다른 부류 마네킹으로 그려진) 시트와, 그 요청 폴더·마네킹·납품 이름·붙이는 명령을 보여 준다.
  --js      엔진이 읽는 표 js/gait_classes.js 를 다시 만든다 (index.html 이 battle.js 보다 먼저 싣는다).
  --check   js/gait_classes.js 가 JSON 과 같은지, JSON 이 등록된 전투 시트를 빠짐없이 덮는지, art/requests/gait/ 의 요청 폴더가
            가리키는 파일이 있고 (--write 로 만든 폴더는) 가이드가 부류 마네킹 띠와 같은지 본다 (다르면 종료 코드 1).
  --json    현황을 JSON 으로.
  --write <시트 id...>  시트마다 요청 폴더 하나를 통째로 만든다 (README + guide_<p>_a/b.png + size_<p>_a/b.png, p = run/heavy/robe):
            부류(gait_classes.json) → 그 부류의 확정 마네킹(pose.json 의 기울기·오르내림·뜸 여부·보폭·디딘 발 자리),
            시트(manifest + art/inbox/<stem>.png + phase3.json: 배율·열쇠 색·꾸러미), 캐릭터가 든 것(아래 CARRY 표 —
            없으면 phase3 꾸러미 README 의 CHARACTER 줄 + 부류 기본 문장으로 만들고 「검토」를 알린다).
            그림은 tools/art/run_request_guides.py 의 build() 가 만든다. 이미 있는 폴더는 --force 없이는 건드리지 않는다.
            --out DIR 로 다른 곳(시험용)에 쓸 수 있다 (시트 하나). 끝나면 art/requests/gait/README.md 의 목록을 다시 쓴다.
  --index   art/requests/gait/README.md 의 요청 목록(표시 줄 사이)만 다시 쓴다.
  --write <시트> --guides 3d   (주인 2026-11-28) 부류 공용 2D 마네킹 대신 그 캐릭터의 대기 그림에 맞춘 3D 마네킹
            (tools/mannequin3d/request.py; tools/mannequin3d/specs/carry3d.json 에 그 시트의 항목 — 든 것·팔·손목 범위·개성 — 이
            있어야 한다)으로 같은 폴더를 만든다: guide_<p>_a/b.png(관절 점·무기 유령) + guide_<p>_plain_a/b.png(밑그림) +
            size_<p>_a/b.png + pose.json(mannequin3d 표시, 시트 배율) + preview_<p>.gif / preview_<p>_game_x4.gif + 3D 용 README.
            이미 3D 로 만든 폴더는 --guides 없이 --force 해도 3D 로 다시 만든다 (--guides 2d 로 되돌릴 수 있다).
            --check 는 3D 폴더를 부류 마네킹 띠와 비교하지 않고, carry3d.json 항목과 가이드 PNG 가 만든 때와 같은지(sha256) 본다.

요청 폴더: art/requests/gait/<요청>__<시트 png 이름에서 sheet_ 뺀 것>/ — 경량 run__, 중량 heavy__, 로브 robe__
(이미 있는 run__class_warrior, run__captain_shadowqueen 과 같은 꼴). 부류와 상관없이 엔진에는 시트의 anims.run 한 줄로 붙는다:
납품 art/inbox/gait/<시트 png 이름>_run_a.png + _b.png, 붙이기 add_gait.py <시트> --gait run --pose <부류 마네킹 pose.json>.
엔진(js/battle.js gaitClassOf)은 시트 meta.gait → 이 표 → 경량 순으로 부류를 안다.

이 도구는 assets/ 와 art/inbox/ 를 쓰지 않는다 (--js 만 js/gait_classes.js 를, --write/--index 만 art/requests/gait/ 를 쓴다).
"""
import argparse
import datetime
import glob
import json
import os
import re
import shlex
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
    return os.path.relpath(p, ROOT).replace(os.sep, '/')   # README 와 manifest 는 늘 / (Windows 에서도)


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
            local = f'{folder}/pose.json'
            if os.path.isfile(os.path.join(ROOT, local)):
                g = local
            row.update(request=folder, request_exists=os.path.isdir(os.path.join(ROOT, folder)), guide=g, guide_state=gs,
                       delivery=[f'art/inbox/gait/{stem}_run_a.png', f'art/inbox/gait/{stem}_run_b.png'],
                       receive=f'python3 tools/art/receive.py gait/{stem}_run',
                       attach=f'python3 tools/art/add_gait.py {shlex.quote(sid)} --gait run --src art/inbox/gait/{stem}_run_a.png '
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


PATH_RE = re.compile(r'(?<![\w/])((?:art|tools|assets|docs|js)/[\w./-]+\.(?:png|json|gif|aseprite|md|py|jpg|js))')


def check_requests(spec, man):
    """art/requests/gait/*__*/: 머리 줄의 시트가 등록·분류되어 있고, README 가 가리키는 파일이 있고(납품 art/inbox/gait/ 는 빼고),
    --write 로 만든 폴더는 guide_<p>_a/b.png 가 지금 부류 마네킹 띠와 바이트까지 같고 size_<p>_a/b.png 가 있는지 본다."""
    import filecmp
    from run_request_guides import Fail, scale_pose, scale_strip, sheet_scale
    errs = []
    for d in sorted(glob.glob(os.path.join(ROOT, 'art', 'requests', 'gait', '*__*', 'README.md'))):
        folder = os.path.dirname(d)
        name = rel(folder)
        text = open(d, encoding='utf-8').read()
        m = re.match(r'#\s*(.+?)\s*·\s*`(sheet/[^`]+)`', text.split('\n', 1)[0])
        if not m:
            errs.append(f'{name}/README.md: 첫 줄에 「제목 · `sheet/...`」가 없다')
            continue
        sid = m.group(2)
        cls = (spec['sheets'].get(sid) or {}).get('gait')
        if sid not in man:
            errs.append(f'{name}: {sid} 가 등록되어 있지 않다')
        if cls not in CLASSES:
            errs.append(f'{name}: {sid} 의 부류 {cls!r} 는 그린 이동 칸을 받지 않는다')
            continue
        for ref in sorted(set(PATH_RE.findall(text))):
            if not ref.startswith('art/inbox/gait/') and not os.path.exists(os.path.join(ROOT, ref)):
                errs.append(f'{name}/README.md: 없는 파일 {ref}')
        if 'gait_requests.py --write' not in text.split('\n', 3)[2]:
            continue                                   # 손으로 쓴 요청 (run__class_warrior, run__captain_shadowqueen)
        want = os.path.basename(folder).split('__', 1)[0]
        if want != REQ_PREFIX[cls]:
            errs.append(f'{name}: 폴더 머리 {want}__ 인데 {sid} 는 {cls} ({REQ_PREFIX[cls]}__)')
            continue
        if is_3d_folder(folder):                       # 3D 마네킹 가이드 (--guides 3d): 부류 마네킹 띠와 비교하지 않는다
            try:
                sc = sheet_scale(sid)
            except Fail as e:
                errs.append(f'{name}: {e}')
                continue
            errs += check_request_3d(name, folder, sid, text, sc)
            continue
        g, _ = guide_of(cls, spec)
        pose = load(g)
        try:
            sc = sheet_scale(sid)
        except Fail as e:
            errs.append(f'{name}: {e}')
            continue
        scaled = abs(sc / pose['scale'] - 1) > 0.01
        local = os.path.join(folder, 'pose.json')
        expected = pose
        if scaled:
            expected = scale_pose(g, pose, sc)
            try:
                saved = load(local)
            except (OSError, ValueError):
                saved = None
            if saved != expected:
                errs.append(f'{name}: 요청 폴더 pose.json 이 없거나 오래됐다 — --force 로 다시 만들 것')
        elif os.path.isfile(local):
            errs.append(f'{name}: 표준 배율 요청에 별도 pose.json 이 있다')
        for h in 'ab':
            gp = os.path.join(folder, f'guide_{REQ_PREFIX[cls]}_{h}.png')
            src = os.path.join(ROOT, os.path.dirname(g), f'{pose["set"]}_{h}.png')
            matches = False
            if os.path.exists(gp):
                if scaled:
                    import numpy as np
                    from PIL import Image
                    original = np.asarray(Image.open(src).convert('RGB'))
                    try:
                        matches = np.array_equal(np.asarray(Image.open(gp).convert('RGB')),
                                                 scale_strip(original, pose['scale'] / sc))
                    except (Fail, OSError) as e:
                        errs.append(f'{name}: {e}')
                else:
                    matches = filecmp.cmp(gp, src, shallow=False)
            if not matches:
                errs.append(f'{name}: guide_{REQ_PREFIX[cls]}_{h}.png 가 {rel(src)} 와 다르다 — gait_requests.py --write {sid} --force')
            if not os.path.exists(os.path.join(folder, f'size_{REQ_PREFIX[cls]}_{h}.png')):
                errs.append(f'{name}: size_{REQ_PREFIX[cls]}_{h}.png 가 없다')
        for m2 in re.finditer(r'the guide (bow|spear|lance|sword|staff|mace|blade|draws)|as long as the guide', text):
            errs.append(f'{name}/README.md: 「{m2.group(0)}」 - phase3 CHARACTER 줄을 그대로 옮긴 말이다. 이 요청에는 무기 가이드가 없으니 「the idle」 기준으로 바꿀 것')
        expected_path = rel(local) if scaled else g
        poses = re.findall(r"""--pose\s+["']?([^\s`"'<>]+)""", text)
        if not poses or any(p != expected_path for p in poses):
            errs.append(f'{name}/README.md: 마네킹 {expected_path} 를 가리키지 않는다 — --force 로 다시 만들 것')
        actual = [line.strip() for line in text.splitlines()
                  if line.lstrip().startswith(('- Stride:', 'near foot:', 'far foot:'))]
        if actual != [stride_line(expected, sc).strip(), *(line.strip() for line in toe_lines(expected))]:
            errs.append(f'{name}/README.md: 보폭 또는 디딤 발끝 숫자가 pose.json 과 다르다')
    return errs


# ───────── --write: 요청 폴더 만들기 ─────────
# 캐릭터가 이동하는 동안 손에 든 것·천·얼굴 (phase3 꾸러미 README 의 CHARACTER 줄과 승인된 대기 그림을 보고 적었다).
# title = 한국어 제목, name = 프롬프트의 이름, character = 영어 CHARACTER, carry = ARMS AND WEAPONS 줄들, cloth = 천·머리의 늦음,
# face = 얼굴, ko = 한국어 머리말의 팔·무기 요약, refs = 꾸러미에서 더 넣을 참고 그림 (concept 는 늘 넣는다),
# height = (있으면) FORMAT 의 「the figure about as tall as ...」 문장 대신 쓸 키 문장.
# joints = (있으면) THE MOVE 의 「Each frame ... Joint for joint ... head on the mannequin's neck」 줄들 대신 쓸 줄들
#          (마네킹과 키·어깨 폭이 크게 달라 관절을 관절에 올릴 수 없는 캐릭터).
CARRY = {
    'sheet/captain/warlord': {
        'title': '가르마크 이동', 'name': 'Garmak', 'refs': ['portrait.png'],
        'character': ('Broad red-haired, red-bearded warlord in a horned iron helmet, grey wolf-fur mantle, '
                      'crimson rear cloak, leather harness, lion clasp, open trousers and boots. One two-handed crescent war axe, no sword.'),
        'carry': [
            'Carry the same DOUBLE-BITTED axe (two crescent blades back to back on an iron socket, short top spike, red-wrapped '
            'haft, iron butt cap; do not shorten it) nearly level across the belly, haft within ±5° of horizontal at about '
            'y=645–655. Put the NEAR (rear) hand at x≈125–140 and the FAR hand 60–75 px further up the same haft at the same '
            'height. Slide the grip up the haft so the butt sticks out about 60 px behind the near hand (to x≈65), rather than '
            'shortening the axe. Put the socket centre at about x=299, y=650, and keep the WHOLE head (both bits) within '
            'x=249–349, y=598–708. That keeps the lower bit above the leading knee (R3 277,730; R4 270,740; R7 269,722; '
            'R8 251,746) and clear of the flight shins, and the upper bit below the beard-braid tips.',
            "Where the haft crosses the harness below the ribs, draw it over the harness (intended). The mannequin's two separate "
            'arm swings do NOT apply to this character (intended, not a deviation). Both hands stay on the haft with a slight '
            'bend in each elbow, and the axe only follows the torso\'s bob and lean, at most about 10 px between frames. It never swings.',
        ],
        'cloth': ['Keep lion clasp, fur mantle edge, diagonal harness and any front red corner in front. Only the cape behind the shoulders and rear hair ends trail.'],
        'face': 'Face: helmet horns, scar and braided red beard stay clear of the axe, without converting broad shoulders into armour.',
        'ko': ('경량: 갑옷 없이 무릎이 자유롭다. 양날 도끼를 배 앞에 거의 수평(±5°)으로 y≈650. 가까운 손 x125–140, 먼 손은 '
               '같은 자루 60–75px 앞. 도끼머리 전체 x249–349/y598–708: 앞무릎 위, 수염 끝 아래. 자루 끝은 가까운 손 뒤로 약 60px. '
               '두 팔은 가이드 팔 흔들기 대신 자루를 쥔다. 한 칸에 10px 이내로만 움직인다. 몸 앞 사자 걸쇠와 가죽띠 유지.'),
    },
    'sheet/captain/titan': {
        'title': '우르그 이동', 'name': 'Urg', 'refs': ['portrait.png'],
        'character': ('Enormous giant-blooded Urg, bare muscular arms, brown swept hair and beard, white fur collar, '
                      'leather and gold harness, rune medallion, split front tunic, fur boots and one two-handed stone maul with a gold spiral rune.'),
        'carry': [
            'Lower the two-handed stone maul from its idle diagonal to a short, braced carry across the low torso (intentional). '
            'NEAR hand to the rear x=123–136, y=688–702; FAR hand forward x=207–223, y=666–679, on the same haft. '
            'Aim for the stone head center x≈298, y≈638–654: keep the full head within x=249–351 and entirely below y=585 '
            '(larger y), above the lead knee. Keep the whole handle above the floor and preserve the gold spiral side. The shaft '
            'may cross the low harness in front; the stone must not cover the head or fur collar.',
            'Both arms are exempt from the mannequin arm swing (intended). Bend the elbows from Urg’s own wider shoulders, '
            'which are not interchangeable with the mannequin’s; keep the weight large, braced and close rather than swinging it.',
        ],
        'joints': [
            '  - Take the heavy mannequin’s leg ANGLES, lean, small bob, planted toe x and ground line. Keep Urg’s own longer torso and',
            '    wide shoulders. Do NOT place his head, shoulders, elbows, hips or knees on the mannequin’s joints; see FORMAT and ARMS.',
        ],
        'height': ('Urg’s accepted idle is about 413 source px head to sole (about 69 game px at 0.1654 / cell 112). Keep its own '
                   'wide shoulders and long trunk. As a starting landmark at contact: hair around y≈455–470, shoulders around y≈550–580 '
                   'and hips about y≈690–720 before the prescribed body drop. No taller mannequin head, stretched limbs, or shrinking the maul.'),
        'cloth': ['The white fur collar and the round gold rune medallion on the centre of the chest (where the harness straps '
                  'cross below the beard, about x=206-244, y=570-600 in the idle) stay on the body and in view; the front belt and '
                  'the split tunic stay in front. Only the loose hair behind the shoulder and rear tips lag.'],
        'face': 'Face: keep cheek marks, short beard, hairline and earring visible. Do not replace the loose hair behind him with a hood.',
        'ko': ('중량: 거대한 몸과 돌망치. 대기·준비 x 투영은 겹치므로 분리한 실제 대기(약 413px·게임 69px) 기준. '
               '자기 몸의 폭·길이로, 발끝·각도만 복사. 뒤손 x123–136/y688–702, 앞손 x207–223/y666–679, 돌 전체 x249–351·'
               'y≥585, 얼굴·모피·앞무릎 분리. 금빛 룬·가슴 가운데 금 룬 메달(어깨 아님)·앞 허리띠와 튜닉 유지.'),
    },
    'sheet/captain/demonhunter': {
        'title': '모르데카이 이동', 'name': 'Mordecai', 'refs': ['portrait.png'],
        'character': ('Grey-bearded witch hunter in a charcoal hood and long grey-trimmed cloak, silver cartridge bandolier, '
                      'front cross pendant and cross tabard, dark leather boots; holy mace with a spiked round cross head.'),
        'carry': [
            'One FAR hand on the holy mace (not a firearm), as in the idle: the fist wraps the shaft at about x=252–289, '
            'y=552–600 (size-panel coordinates), and the pale pommel sits just below the fist at about x=242–267, y=610–630. '
            'Nothing holds the shaft below the pommel. Keep the mace upright at the far (front) side of the body as in the idle, '
            'about 12–15° top-forward. Head centre about x=288–296, y≈440–455; the whole spiked head (about 80 px wide) within '
            'about x=250–335, y≈405–490, to the right of the hood and off the face. The shaft runs beside the body, just right '
            'of the bandolier, and does not cross the chest, pendant or bandolier. The pommel is the lowest point of the mace, '
            'at about y≈620–630.',
            'The NEAR hand is an empty gloved fist in front of the belly beside the belt buckle (about x=150–207, y=600–650) and '
            'stays empty. Give it only a small swing (about 10–15 px), not the full mannequin arm swing; this is intended, not a '
            'deviation. The far arm keeps the mace steady and does not swing.',
        ],
        'cloth': ['Grey piping on the open front and the long narrow cross tabard stay in front; only the rear hood/cape edge lags. '
                  'Keep the brown leather boots with their buckled straps and cuffs distinct from the dark-plum trousers and the cloak.'],
        'face': 'Face: keep the hood low and the grey beard readable inside it; no spike across the brow.',
        'ko': ('로브, 앞 십자 천과 탄띠는 앞에. 먼 손 하나로 성철퇴, 주먹 x252–289/y552–600, 손잡이 끝 y≈610–630; '
               '가까운 손은 배 앞 빈 주먹, 작게만 흔듦. 머리 전체 x250–335/y405–490, 철퇴는 두건 오른쪽, 몸 옆에 서서 '
               '가슴·탄띠를 가로지르지 않는다. 갈색 가죽 장화. 총이나 광원 추가 안 함.'),
    },
    'sheet/captain/hexer': {
        'title': '벨라도나 이동', 'name': 'Belladonna', 'refs': ['portrait.png'],
        'character': ('Belladonna in long plum panels with green embroidered trim, wide bent plum witch hat with skull charm '
                      'and gold crescent, long dark-blue hair, gold earrings, and a curved wooden staff clasping one green gem.'),
        'carry': [
            'One far hand on the staff as in the idle, fist (fingers wrapping the staff) at about x=260–286, y=612–640; the '
            'wrist and sleeve go below and to the left of it. Its top tilts slightly forward: head '
            'center x=310–317, y≈463–482, with all the carved ring and gem within x=282–351. Keep the ring forward of the '
            'hat brim, not in front of the face. Keep the long carved length and the butt above y=795. No magic or glow.',
            'The near hand stays low by the near waist or the belt line as in the idle (idle palm is open, no second staff '
            'hand); allow only a small change from that carry, not the full mannequin arm swing.',
        ],
        'cloth': ['Front lapels, brooch, embroidered green front panels and the curl already lying over her chest stay in front. Only the hair and coat tips already behind trail. Keep the bent brim and attachments.'],
        'face': 'Face: keep the smirk and cheek mark visible below the brim; no staff or hair crosses the face.',
        'ko': ('로브. 먼 손 하나 x260–286/y612–640에 굽은 지팡이, 머리 전체 x282–351, 모자 앞쪽; 가까운 빈 손은 허리. '
               '앞머리·앞 초록 자수와 브로치 앞에, 뒤쪽 끝만 움직임. 보석은 불투명 색, 빛 효과 없음.'),
    },
    'sheet/captain/inquisitorlord': {
        'title': '발타자르 이동', 'name': 'Balthazar', 'refs': ['portrait.png'],
        'character': ('Severe grand inquisitor in a split deep-crimson hooded robe with a gold-edged shoulder capelet and round '
                      'gold throat clasp, an ornate gold chest cross (no cord on the sheet), '
                      'dark gloves and boots; one long iron mace with an open spiked cage head.'),
        'carry': [
            'The far hand grips the cage mace in one fist at about x=290–326, y=580–622, with the shaft passing through it at '
            'x≈305–312, as in the idle. Keep it upright with '
            'a slight forward rake, the head center around x=310–314, y≈460–475 and its full rim/spikes within x=270–351 '
            'to the right of the hood. Keep the open cage silhouette and its bright rim; the lower end stays above y=792. '
            'No flames inside the cage and no shaft in front of the chest cross.',
            'The near empty gloved fist stays by the near hip with the short robe swing. The far arm bends to keep the '
            'shaft steady and does not follow the full empty-hand mannequin swing (intended).',
        ],
        'cloth': ['The gold-edged shoulder capelet with its round gold throat clasp, the gold chest cross and the split gold-edged '
                  'front panels of the robe stay in front. No cord is drawn on the sheet, so do not add one even though the portrait '
                  'shows one. Keep the gap between the boots; only the rear hem lags.'],
        'face': 'Face: hood and old cheek scars stay visible; keep the cage head away from brow and nose at all phases.',
        'ko': ('로브. 먼 손 하나 x290–326/y580–622 주먹에 열린 철제 격자 철퇴, 자루 x≈305–312. 머리 전체 x270–351, 두건 오른쪽, '
               '불꽃 없음. 가까운 손 빈 주먹, 금테 어깨 망토·둥근 금 고리·금 십자가·갈라진 앞 로브는 앞에; 끈은 시트에 없음, 그리지 말 것.'),
    },
    'sheet/captain/liberator': {
        'title': '카토 이동', 'name': 'Kato', 'refs': ['portrait_800.jpg'],
        'character': ('Kato from the registered chains-and-fists sheet (not the old sword-in-hand sheet): shaved scarred head, '
                      'bare dark scarred torso, diagonal buckled strap, leather gladiator kilt over trousers, wrapped calves, '
                      'an iron cuff and broken chain on each clenched wrist, and the longsword strapped to his back.'),
        'carry': [
            'Both clenched fists pump without a hand-held weapon or shield. Preserve both separate dangling chain stubs. '
            'Use the light timing and the character’s own elbow bend. The fist sets the forward limit, not the chain: the '
            'front-most knuckle pixel stays at x≤349. With the fist tipped up as in the idle guard (idle cuff centre x≈317, '
            'fist edge x≈340) the cuff may sit at x≈323. Where the far fist points forward along the mannequin forearm (R1, R6, '
            'R7, R8: mannequin hand x=322–336, forearm 2–31° above horizontal), the fist reaches about 55 px past the cuff '
            'centre. There, keep the far cuff centre at x≤295, or tip the fist up as in the idle (intended, not a deviation). '
            'The chain hangs about 100 px straight down below that cuff. Keep links below and just behind the wrist, not raised or wrapped around the fingers. '
            'Whole chain/sword outlines x=32–351 and clear of the face, legs and feet; in flight nothing below y=852.',
            'The back longsword stays strapped on one diagonal: hilt visible behind the rear shoulder, sheath beside the far '
            'hip. It does not move into the hand, swing into the face, or turn into a sword trail.',
        ],
        'cloth': ['Keep the diagonal chest strap, the belt with its square buckle and the long clean-edged centre leather apron '
                  '(it hangs between the thighs to about the knees) as the front layers. The apron may swing slightly with the legs. '
                  'Only the short layered leather side flaps at the hips and the chain links lag slightly. Add no tears, rags or '
                  'shoulder cloth (none on the accepted sheet).'],
        'face': 'Face: bald head, brow and cheek scars unobstructed by either cuff, chain or the back sword.',
        'ko': ('경량: 맨상체·가죽 앞자락, 무릎 자유. 채택 사슬·주먹 시트만 기준. 두 손 주먹·각 손목 끊긴 사슬, '
               '먼 주먹 앞끝 x≤349. 주먹을 앞으로 뻗는 R1·R6·R7·R8 은 수갑 중심 x≤295, 아니면 대기처럼 주먹을 세운다. '
               '사슬·등검 전체 x32–351, 도약 y≤852. 등 장검은 고정, 손 검·방패 없음.'),
    },
    'sheet/monster/고블린': {
        'title': '고블린 이동', 'name': '고블린', 'refs': [],
        'character': ('Small green goblin: oversized pointed ears and amber eyes, diagonal leather strap, wrist wraps, '
                      'ragged front waistcloth, wrapped ankles and bare green toes. The weapon is a knotted wooden club, not a blade.'),
        'carry': [
            'Keep the club in the near hand at his own low waist: x=142–147 in each 384-px slot, about 35–45 px above his '
            'hips (y≈700–715; see the height line in FORMAT - the mannequin-height box y=668–682 would sit at his chest). '
            'The idle holds it about 22° ABOVE horizontal. For the run, lower it to about 5–10° BELOW horizontal (intended '
            'change, not a deviation), knob centre about 165–170 px ahead of the grip and 15–30 px below it. Keep the whole '
            'knob above and ahead of the leading knee in the push and flight frames R3, R4, R7 and R8, clear of the face and '
            'ears, and within x=105–350. The shaft may cross the near hip (intended). Where the far claw passes the shaft '
            '(R3–R5), draw the club over the claw, never the claw over the club. Do not let the club touch either boot or knee.',
            'The fixed carry replaces the near-hand and elbow swing. Bend the elbow as needed from his own shoulder (not the '
            "mannequin's); keep the far claw free and following its light arm swing. Do not let the club flip between hands.",
        ],
        'cloth': ['Keep the diagonal strap and the ragged front waistcloth in front. Only the free ends at the sides lag, '
                  'without merging the feet.'],
        'face': 'Face: keep both ears, brow and amber eyes readable, with no club in front of them.',
        # 마네킹보다 약 90px 작고 다리가 짧다: 관절을 관절에 올리지 않고 각도만 따른다 (브로크처럼 절대 y 를 준다)
        'joints': [
            '  - Each frame: the leg and arm ANGLES, the torso lean, the foot placement, the planted-toe x and the bob of that',
            '    mannequin frame, drawn with HIS OWN limb lengths (hands: see ARMS - where the text moves a hand, that is intended,',
            '    not a deviation). NOT joint for joint: the goblin is about 90 px shorter than the mannequin, so his head does NOT',
            "    go on the mannequin's neck and his hips, knees and shoulders do NOT go on its joints - see the height line in FORMAT.",
        ],
        'height': (
            'The goblin is about 90 px shorter than the mannequin and has much shorter legs (hip about 125 px above the sole '
            "when straight, against the mannequin's 176). Do NOT put his head on the mannequin's neck or his joints on its "
            "joints. Copy the mannequin's joint ANGLES, torso lean, foot placement, planted-toe x and bob with his own limb "
            'lengths. His hips sit near y≈740–750 (not 690), his shoulders near y≈620–630 (not 570), and his ear tips near '
            'y≈520–535 in R1, plus the 9-px bob. Do not stretch his legs, torso or neck to reach the mannequin\'s height; he '
            'stays about 55–57 game px'
        ),
        'ko': ('몽둥이(칼 아님)는 가까운 손, 자기 낮은 허리(x=142–147, 엉덩이보다 35–45px 위 y≈700–715 — 마네킹 높이 y=668–682 는 '
               '가슴이다)에서 수평보다 5–10° 아래로 (대기는 약 22° 위 — 의도한 바꿈). 옹이 중심은 손에서 165–170px 앞·15–30px 아래, '
               'R3·R4·R7·R8 앞 무릎보다 위·앞, x=105–350 안, 얼굴·귀·장화·무릎과 분리; R3–R5 먼 손톱이 자루를 지날 때 몽둥이가 위. '
               '키: 마네킹보다 약 90px 작고 다리가 짧다 — 머리를 마네킹 목에, 관절을 관절에 두지 않고 각도·기울기·발자리·디딘 발끝·'
               '출렁임만 따른다 (R1 엉덩이 y≈740–750, 어깨 y≈620–630, 귀 끝 y≈520–535). 다리·몸·목을 늘이지 않는다 (게임 55–57px). '
               '앞 가죽띠·허리천은 앞에.'),
    },
    'sheet/monster/서리 트롤': {
        'title': '서리 트롤 이동', 'name': '서리 트롤', 'refs': [],
        'character': ('Bare-handed pale-blue frost troll: bald head, heavy brow, protruding tusks, huge shoulders, '
                      'low massive fists, ragged dark front loincloth and bare feet. No club or ice weapon in any accepted pose.'),
        'carry': [
            'Use both bare fists, not a club. Keep the fists low, below the ribs, and clear of the brow, tusks and knee silhouettes.',
            "The mannequin's shoulders and elbows (x≈156/232) are far narrower than his, so they do NOT give the troll's arm "
            "positions (intended, not a deviation). Keep the idle's wide shoulders and long arms hanging outside the torso: the "
            'near fist beside the near thigh (idle x≈35–110, y≈710–780) and the far fist beside the far thigh (idle x≈277–330). '
            'From the guide take only the small fore-aft swing (its hands move about 10–20 px per cycle) and the body bob, '
            'bending the elbows a little. The near fist never crosses in front of the loincloth and stays at x>=32 (see the '
            'near-arm line).',
            "The NEAR arm (left in the picture, drawn over the body) is the one at the slot's rear edge. In the idle its elbow "
            'and forearm already reach x≈26 (y≈630–700), and the near fist reaches x≈33 (y≈710–770). Tuck that arm in by at '
            'least 6–8 px with a slightly more bent elbow, hanging a little closer to the torso, so its whole outline stays at '
            'x>=32 in every frame, including the frames where it swings back. Do not narrow the shoulders or shrink the fist. '
            'The far fist (idle right edge x≈330) has about 20 px of room and must stay at x<=351.',
            'Do not narrow his shoulders or shrink the fists to fit. Adjust the forearm turn before changing the silhouette; '
            'keep the planted heavy foot and torso positions from the scaled guide.',
        ],
        'cloth': ['The dark ragged loincloth wraps the whole waist: a band from hip to hip, with short ragged tatters over the '
                  'tops of both thighs and a longer pointed front flap hanging between the thighs. It stays in front. Only its '
                  'free ragged tips lag a little as the thighs move; keep both blue feet separate.'],
        # 마네킹 어깨가 그보다 훨씬 좁다: 다리만 관절대로, 팔 자리는 ARMS
        'joints': [
            '  - Each frame: the legs, the torso lean and the body bob of that mannequin frame. Joint for joint: hips, knees, ankles,',
            "    feet. Shoulders, elbows and fists: see ARMS - the mannequin's shoulders are far narrower than his, so they do NOT give",
            '    his arm positions (intended, not a deviation); take only its small fore-aft arm swing.',
            "    The mannequin's big round head is a placeholder: draw the character's own head on the mannequin's neck, at its own size",
            '    (as in the sheet).',
        ],
        'face': 'Face: keep the bald skull, projecting brow and both tusks unobstructed.',
        'height': 'Keep the bare-footed troll about as tall as the upper-left idle of the accepted 2×2 sheet (~75 game pixels); '
                  'retain its broad shoulders and oversized fists.',
        'ko': ('승인 2×2 왼쪽 위가 대기. 곤봉 없이 맨주먹, 주먹은 늑골 아래. 마네킹 어깨·팔꿈치(x≈156/232)는 그보다 훨씬 좁아 '
               '팔 자리로 쓰지 않는다(의도): 넓은 어깨, 몸통 밖으로 늘어진 긴 팔 — 가까운 주먹은 가까운 허벅지 옆(x≈35–110, '
               'y≈710–780), 먼 주먹은 먼 허벅지 옆(x≈277–330); 가이드에서는 작은 앞뒤 흔들림(10–20px)과 출렁임만. 칸 뒤 끝에 닿는 것은 '
               '가까운 팔(그림 왼쪽, 대기에서 이미 x≈26): 팔꿈치를 조금 더 굽혀 6–8px 이상 안으로, 모든 칸 x>=32. 먼 주먹은 x<=351. '
               '어두운 허리천은 허리를 두른 띠 + 두 허벅지 위 짧은 너덜 + 가운데 긴 뾰족한 앞자락, 앞에. 맨발.'),
    },
    'sheet/monster/사막 도적': {
        'title': '사막 도적 이동', 'name': '사막 도적', 'refs': [],
        'character': ('Desert bandit in a wrapped sand-coloured headcloth and face veil, brown vest, wrapped wrists, '
                      'front sash, separate baggy trousers and dark boots. The weapon is the accepted curved scimitar.'),
        'carry': [
            'Carry the scimitar low in the near hand at x=158–168, y=673–687. The idle holds the blade forward and up across '
            'the vest. For the run, the blade POINTS back and down at 49–53° below horizontal, pommel and guard forward of the '
            'hand (intended change, not a deviation; this is the blade\'s direction, not a 49–53° rotation from the idle). Keep '
            'its curve and length (about 184 px from grip to tip); the whole weapon stays within x=32–210, y=640–840 and below '
            'the veiled face. In R1, R2, R4, R5, R6 and R8 the back half of the blade crosses the trailing shin and boot (ankle '
            'at about x=98,y=730 / x=129,y=722 / x=84,y=796). Draw the blade OVER that boot with its full dark outline and '
            'light edge, so blade and boot stay separate shapes at 64 px; never hide the blade behind the boot. In R3 and R7 '
            'the blade runs clear, behind the push-off shin.',
            'The near elbow follows the shoulder but the steady grip replaces its swing; adjust the elbow bend, not arm length. '
            'The empty far hand follows the free light arm swing and stays separated from the blade.',
        ],
        'cloth': ['Keep the face veil, vest fronts and the vertical sash in their original front layers. Only short rear headwrap '
                  'tails and loose tips lag. The baggy trousers separate across both knees and boots; this is light, not robe.'],
        'face': 'Face: keep the same narrow eye slit and veil; do not uncover the nose or mouth.',
        'ko': ('가까운 손 허리 높이(x=158–168, y=673–687), 굽은 칼날은 수평보다 49–53° 아래로 뒤를 향한다 (대기는 앞위 — 의도한 '
               '바꿈; 대기에서 49–53° 돌리라는 뜻이 아니다), 자루머리·코등이는 손 앞. 굽음·길이(손에서 끝까지 약 184px) 그대로, '
               '칼 전체 x=32–210, y=640–840 안, 얼굴 아래. R1·R2·R4·R5·R6·R8 은 칼날 뒤쪽 절반이 뒤 정강이·장화를 가로지른다 — '
               '칼날을 장화 위에 짙은 외곽선·밝은 날까지 그려 둘이 따로 읽히게 (장화 뒤로 숨기지 않는다). R3·R7 은 칼날이 비어 있다. '
               '얼굴 베일과 긴 앞 허리띠는 앞으로.'),
    },
    'sheet/captain/admiral': {
        'title': '마렌 이동', 'name': '마렌', 'refs': ['portrait.png'],
        'character': (
            'Maren, silver-haired admiral in a navy coat with gold trim, epaulettes, cream cravat, trousers and '
            'tall boots. Keep the accepted wooden crossbow and its steel prod.'
        ),
        'carry': [
            'Use both hands as in the idle. Rotate the idle crossbow down to a level low carry at hip height: near '
            'hand on the trigger grip at x=145–150, y=685–692, the far hand under the fore-stock about 95 px ahead '
            'of it. Keep the full prod and stock within x=100–344 and y=625–780. The near arm is almost straight, '
            'reaching down and back from the shoulder. Do not put the grip further back or lower, because the arm '
            "cannot reach it in the leaning frames R3/R4/R7/R8. The mannequin's two separate arm swings and elbow "
            'locations do NOT apply to this character (intended, not a deviation). Let the shoulders follow the '
            'torso, keep both hands attached to the weapon, and limit fore-aft travel to 10 px.',
            'The level stock now crosses the navy coat at the belt (intended, not a deviation from the sheet). '
            "Keep the wood's dark 1-px outline and a light top edge where it lies over the coat, so stock and coat "
            'stay separate at 64 px. The prod and the front of the stock stay on the background in front of the body.',
        ],
        'cloth': [
            'The cravat and front gold-braided coat panels stay against the chest and thighs. Only the back tails '
            'lag one frame; keep each boot distinct.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '양손 수평 노궁은 허리 높이, 가까운 손 x=145–150, y=685–692 (더 뒤·아래는 R3/R4/R7/R8 에서 팔이 닿지 않는다). '
            '먼 손은 약 95px 앞 총몸 아래. 개머리는 코트 허리를 가로지른다(의도, 윤곽선 유지). 앞 코트와 크라바트는 제자리에 둔다.'
        ),
    },
    'sheet/captain/beastmaster': {
        'title': '오르가 이동', 'name': '오르가', 'refs': ['portrait.png'],
        'character': (
            'The accepted leather-clad beastmaster has long loose wavy dark-brown hair (no headband) with ONE braid '
            'that starts behind the ear and hangs down the front of her neck to the gold wolf medallion. She also '
            'has gold earrings, white face-paint stripes, a pale grey-and-cream fur shoulder mantle, short front '
            'leather panels, a back quiver and a dark longbow with gold tips.'
        ),
        'carry': [
            'Bow in the FAR hand, gripped exactly as in the idle: fist x≈313–349, y≈673–705, wrapped round the bow '
            'handle (x≈330–345). The bow stands upright with the string toward the body (string x≈300–309, top tip '
            'y≈517, bottom gold tip y≈845). The bow hand stays at this idle spot in all 8 frames and does NOT follow '
            "the mannequin's far-arm swing (intended, not a deviation). At face height (R3/R4/R7/R8, where the head "
            'leans forward to the neck at x≈248–252) every bow and string pixel stays at x≥300, clear of the face '
            'and front hair curl. The whole bow fits x=253–349, y=502–845. Keep the free near hand clear of the '
            'string, with a short relaxed swing.'
        ],
        'cloth': [
            'The fur stays across both shoulders, and the hanging front leather stays over the leading thigh. The '
            'front braid stays on the chest beside the medallion: it may sway a few px but never flies back. Only '
            'the loose rear hair and the rear fur tips lag a little. The back quiver stays fixed.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '한 손 장궁은 먼 손에 대기 그대로(주먹 x≈313–349, y≈673–705), 세워 앞쪽에 든다. 활 손은 마네킹 팔 흔들기를 따르지 '
            '않는다. 얼굴 높이의 활·시위는 x≥300. 앞 땋은 머리는 가슴 메달 옆, 앞 가죽 자락은 허벅지에 남긴다.'
        ),
    },
    'sheet/captain/elfwarden': {
        'title': '세레니엘 이동', 'name': '세레니엘', 'refs': ['portrait.png'],
        'character': (
            'Sereniel, pale-haired elf with very long silver hair, a side braid hanging in front, a gold circlet and '
            'a green leaf hair ornament. Over the shoulders a short leaf-patterned capelet, over a long dark-green '
            'cream-trimmed cloak that hangs behind her to about the boot tops. A green tunic with short front flaps '
            'to mid-thigh over dark trousers, brown boots, back quiver. No hood is drawn up. Match the sharply '
            'recurved bow.'
        ),
        'carry': [
            'Bow in the FAR (forward) hand, as in the idle. The idle arm is straight, but at that reach the bow '
            'would leave the slot. So in every frame bend the far elbow (down and slightly back, beside the ribs) '
            "and hold the bow grip about a forearm's length in front of the stomach, fist at x=288–298, y=649–662. "
            "The mannequin's far-arm swing does not apply to this hand (intended, not a deviation). Straighten the "
            'diagonal idle tilt enough that the upper recurve sits around x=315–343 at face height; do not shorten '
            'the bow. Let the lower recurve return toward x=242–280, below the waist. Whole bow and string inside '
            'x=235–350, y=477–810. Keep the free near fist at the rear hip by the belt, as in the idle, with a short '
            'swing. '
            'The left SIZE panel crops the end of the idle weapon after aligning the hip. Use the original '
            'accepted sheet for its complete silhouette and dimensions.',
        ],
        'cloth': [
            'Keep the capelet seated on the shoulders. In every frame keep the side braid hanging in front of the '
            'chest to the belt, and the short front tunic flap over the advancing thigh. The long loose back hair '
            'and the long back cloak (hem near the boot tops) trail a little behind the body and swing with the '
            'step. In R4/R8 their lowest pixel stays at or above y=852. The quiver stays fixed on the back.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '한 손 반곡궁은 먼 손: 팔꿈치를 굽혀 배 앞에 든다(손 x=288–298, y=649–662, 마네킹 팔 흔들기 안 따름). 대기보다 '
            '세워 윗부분을 x=315–343에 둔다. 앞 땋은 머리와 앞 튜닉 자락 유지, 긴 뒷머리·긴 뒷망토는 조금 뒤따른다.'
        ),
    },
    'sheet/captain/fieldmedic': {
        'title': '마그다 이동', 'name': '마그다', 'refs': ['portrait.png'],
        'character': (
            'The accepted medic has black hair in a high ponytail with a red tie, a white bandage around the '
            'forehead, a dark-red scarf, a warm-beige (never white) long field coat with a plain dark-red armband on '
            'the near upper arm, a dark-red front apron, a brown belt with two pouches, dark trousers, brown boots, '
            'and a long-handled mace whose head is a round iron ball with conical spikes.'
        ),
        'carry': [
            'Keep the idle two-hand grip on the mace: the lower near hand (the armband arm) holds near the butt and '
            'the far hand about 85 px up the shaft. In the idle the lower hand is at x≈190–211, y≈690–720 with the '
            'head up and FORWARD (about 62°). In the run, move the lower near hand forward to x=225–235, y=693–706 '
            'and tip the shaft UP AND BACK, 53–57° above horizontal toward the left, so the far hand sits above-left '
            'of it at about x≈181, y≈630. Keep the spiked ball head and shaft inside x=44–280, y=475–780; above '
            "y=590 they pass behind the head, with the entire weapon left of x=176 there. The mannequin's two "
            'separate arm swings and elbow locations do NOT apply to this character (intended, not a deviation). '
            'Let the shoulders follow the torso, keep both hands attached to the weapon, and limit fore-aft travel '
            'to 10 px.'
        ],
        'cloth': [
            'The scarf stays on the neck and the dark-red apron hangs in front between the moving knees. The two '
            'brown belt pouches (one behind the hip, one in front by the buckle) stay on the belt and may bounce a '
            'frame. The tied ponytail and the warm-beige rear coat tails can lag a frame.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '양손 철퇴(가시 쇠공 머리)는 뒤로 53–57° 들어 머리 뒤로 보낸다. 아래 손은 대기(x≈190–211)보다 앞 x=225–235, '
            'y=693–706. 스카프와 짙은 붉은 앞치마는 앞에, 허리 주머니 둘은 허리띠에 둔다.'
        ),
    },
    'sheet/captain/khan': {
        'title': '테무르 이동', 'name': '테무르', 'refs': ['portrait.png'],
        'character': (
            'The accepted steppe archer has a fur collar, decorated brown deel split over wide trousers, boots, '
            'back quiver and recurved composite bow.'
        ),
        'carry': [
            'Bow in the FAR hand, gripped exactly as in the idle: fist x≈305–341, y≈625–665 round the handle '
            '(x≈314–333). The recurved bow stands upright with curled tips and the string toward the body (string '
            'x≈291–294, top curl y≈468, bottom curl y≈812). The bow hand stays at this idle spot in all 8 frames '
            "and does NOT follow the mannequin's far-arm swing (intended, not a deviation). In R3/R4/R7/R8 the head "
            'leans forward onto the mannequin neck at x≈248–252, and no part of the face or front hair may cross '
            'the string. If it does, move the whole bow forward by up to 8 px, and the stave never goes past '
            'x=349. The whole bow and string fit x=255–349, y=465–845. The near hand stays an empty fist at the '
            'chest, clear of the string.'
        ],
        'cloth': [
            'Keep the two gold-ringed braids hanging down the chest on both sides of the gold medallion, inside the '
            'cream fur collar: they may sway a few px but never fly back. The fur collar stays round the shoulders. '
            'The open deel stays split: the long embroidered near panel hangs over the near thigh and between the '
            'legs to about the knee, the short far panel sits on the far thigh, and the wide trousers show between '
            'them. Only the loose rear hair locks and the rear coat hem may lift and lag. The back quiver stays '
            'fixed, with fletchings above the near shoulder.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '한 손 합성궁은 먼 손에 대기 그대로(주먹 x≈305–341, y≈625–665), 마네킹 팔 흔들기를 따르지 않는다. 얼굴·앞 머리는 '
            '시위를 넘지 않는다. 가슴 앞 금고리 땋은 머리 두 가닥과 갈라진 델 자락은 제자리.'
        ),
    },
    'sheet/captain/shadowlord': {
        'title': '모로 이동', 'name': '모로', 'refs': ['portrait.png'],
        'character': (
            'The accepted wiry rogue has a dark gold-edged hooded cloak over a fitted tunic, with trousers, '
            'boots, and a single dagger.'
        ),
        'carry': [
            'Keep the dagger in the near hand with the idle grip (gold crossguard just under the fist, blade back '
            'and down). In the idle the hand is held out behind the hip at x≈72–107, y≈687–725. In the run the arm '
            'cannot reach that far, so bring the hand in to x=140–157, y=685–710, just behind the hip. Keep the '
            'full-length light-steel blade (≈80 px from guard to tip, as in the idle; do not shorten it) pointed '
            'back and down at 45–55° below horizontal, with all dagger pixels within x=48–184, y=659–825. Keep it '
            'readable as in the idle: lift the back cloak edge behind and above the blade so the blade shows on '
            'magenta wherever possible. Where it crosses the cloak or the trailing leg, keep its 1-px dark outline '
            'and the light steel #d8dde3 so it never merges into the dark cloak. The free far fist may take the '
            'short forward swing.'
        ],
        'cloth': [
            'The hood and its front gold edge stay around the face, with the wavy brown hair spilling out. Keep the '
            'short brown-trimmed tunic skirt under the belt, and keep the long gold-edged front cloak panel hanging '
            'between the knees (down to about y≈840 in the idle). Only the back cloak edge lifts with the step.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '단검은 가까운 손을 엉덩이 바로 뒤 x=140–157, y=685–710 으로 당겨 날을 뒤아래 45–55° (날 길이 그대로, 어두운 망토와 '
            '섞이지 않게). 앞 금테 두건, 짧은 튜닉 치마, 무릎 사이 금테 앞 망토 자락 유지.'
        ),
    },
    'sheet/captain/siegemaster': {
        'title': '오토 이동', 'name': '오토', 'refs': ['portrait.png'],
        'character': (
            'Otto wears an engineer helmet with goggles and a long brown leather coat over trousers and boots. '
            'Keep the full heavy, hand-held crossbow.'
        ),
        'carry': [
            'Keep the idle grip shapes (near hand closed on the rear trigger grip, far hand under the fore-stock '
            'about 93 px ahead of it). Move the whole crossbow back to a level low carry: near hand at x=140–146, '
            'y=683–688, at hip height. The near arm is almost straight, reaching down and back from the shoulder. '
            'Do not go further back or lower, because the arm cannot reach in R3/R4/R7/R8. Do not go further '
            'forward, or the loaded bolt tip (about 203 px ahead of the near hand) passes x=350. Keep the stock '
            'level and the wide prod visible, with the whole crossbow inside x=125–350, y=615–760. The '
            "mannequin's two separate arm swings and elbow locations do NOT apply to this character (intended, not "
            'a deviation). Let the shoulders follow the torso, keep both hands attached to the weapon, and limit '
            'fore-aft travel to 12 px. '
            'The left SIZE panel crops the end of the idle weapon after aligning the hip; take its full silhouette '
            'and size from the original accepted sheet.',
            'The level stock now crosses the brown coat at the belt (intended, not a deviation from the sheet). '
            'Keep its dark 1-px outline and the brass/ochre highlights where it lies over the coat, so stock and '
            'coat separate at 64 px. The prod and the bolt tip stay on the background in front of the body.',
        ],
        'cloth': [
            'Goggles, helmet, ochre neckerchief and front lapels stay seated. The steel wrench on its chest strap '
            'stays visible on the chest in every frame. The leather pouch on the near back hip stays; the near hand '
            'and forearm pass over or just above its front edge, but do not drop it. The loaded bolt stays in the '
            'groove as in the idle. The moving leg pushes the front coat edge; only the back coat tail lags.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '양손 대형 노궁은 허리 높이에 수평, 가까운 손 x=140–146, y=683–688 (볼트 끝은 x≤350). 개머리는 코트 허리를 '
            '가로지른다(의도, 윤곽선 유지). 고글·가슴 렌치·뒤 허리 주머니·앞깃 유지, 뒷자락만 늦게.'
        ),
    },
    'sheet/captain/spellblade': {
        'title': '카시안 이동', 'name': '카시안', 'refs': ['portrait.png'],
        'character': (
            'The accepted silver-haired spellblade has a high collar, blue-edged coat split over trousers and '
            'boots, and the single straight blue sword.'
        ),
        'carry': [
            "Sword in the NEAR (right) hand only, with the idle's gold cross-guard, dark grip, gold pommel and full "
            "pale-steel runed blade unchanged. The near arm does NOT follow the mannequin's pump: the mannequin's "
            'near elbow and hand positions do not apply to this arm (intended, not a deviation). The shoulder '
            'follows the torso lean, the elbow stays above and behind the fist, and the fist sits low in front of '
            'the hips at x=250–264, y=675–695 in all 8 frames. This is about 70 px further forward and 35 px lower '
            'than the idle fist, so that the turned blade stays in the slot. Turn the fist so the blade leaves its '
            'thumb side pointing BACK and down 19–24° below horizontal and passes under the elbow, tip to the rear. '
            'The cross-guard sits just behind the fist and the pommel just in front of it. All sword pixels stay in '
            "x=33–300, y=650–812. The FAR (left) hand stays open and follows the mannequin's far arm. In R2–R5 that "
            'hand passes behind the hips at x=230–265, y=697–707, behind the sword fist, so the near fist and the '
            'coat hide it. Draw only the part that shows, and never on the hilt.'
        ],
        'cloth': [
            'Hair locks over the front shoulder and the front blue-edged coat lining stay on their own sides. '
            'Only rear hair and coat tails lag; preserve the split and visible boots.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '외손 검은 가까운 손, 마네킹 팔 흔들기를 따르지 않는다: 주먹은 엉덩이 앞 x=250–264, y=675–695, 검끝 뒤아래 19–24°. '
            '먼 손은 펴서 마네킹을 따르되 R2–R5 에서는 검 주먹·코트 뒤에 가린다. 앞 머리와 파란 앞선은 제자리.'
        ),
    },
    'sheet/captain/windhunter': {
        'title': '나린 이동', 'name': '나린', 'refs': ['portrait.png'],
        'character': (
            'The accepted green-cloaked archer has a green head wrap, long rear hair, shoulder mantle, back '
            'quiver, trousers and boots. Preserve the idle longbow.'
        ),
        'carry': [
            'Bow in the FAR (forward) hand, as in the idle. In every frame the centre of the bow-hand fist (the bow '
            'spine runs through it) is at x=326–334, y=672–680, about 60 px in front of the far shoulder, with the '
            "elbow slightly bent. The mannequin's far-arm swing does not apply to this hand (intended, not a "
            'deviation). Tilt the same bow about 5–8° top-forward from the idle so that at face height (y≤565) the '
            'upper limb and string stay at x≥300, clear of the face. The bottom limb curves back below the knee. '
            'The whole bow stays inside x=265–350, y=515–825. Keep the near hand open or in its relaxed idle grip, '
            'without drawing the string.'
        ],
        'cloth': [
            'Keep the shoulder mantle, with its folded-down hood collar, gold toggle clasp and lime leaf brooch, '
            'seated against the body (there is no scarf). The long rear hair, the two lime headband tails and the '
            'rear coat tip lag behind. The short front tunic flap tracks the leading thigh.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '활은 먼 손, 주먹 중심 x=326–334, y=672–680 (마네킹 팔 흔들기 안 따름). 대기보다 5–8° 앞으로 기울여 얼굴 높이에서 '
            '활·시위 x≥300. 망토 깃·단추·잎 브로치 유지(스카프 없음), 앞 튜닉 자락은 허벅지를 따른다.'
        ),
    },
    'sheet/captain/dragonslayer': {
        'title': '지크린데 이동', 'name': '지크린데', 'refs': ['portrait.png'],
        'character': (
            'Sieglinde, bare-headed in dark crimson layered dragon-scale armour, with long wild blond hair and a '
            'side braid over her chest, separate armoured coat panels and a huge two-handed greatsword.'
        ),
        'carry': [
            'Carry the sword forward and up, 74–77° above horizontal. Lower grip x=249–254, y=704–714 in front of '
            'the hips; the other hand stays above it on the same hilt, at the idle spacing. Keep the leading '
            'blade edge and its width in x=230–350, y=420–775; between y=440 and y=582 the left blade edge stays '
            "at x≥267, ahead of the face. The mannequin's two separate arm swings and elbow locations do NOT "
            'apply to this character (intended, not a deviation). Let the shoulders follow the torso, keep both '
            'hands attached to the weapon, and limit fore-aft travel to 5 px.'
        ],
        'cloth': [
            'Her thick blond side braid (gold tip) hangs from the near side of her head over the near scale '
            'pauldron and down the FRONT of her chest, drawn on top of the armour (slot x≈160–185, y≈560–640 in '
            'the idle): keep it lying on the chest in every frame. It moves only with the torso and never swings '
            'back. Scale plates and the front coat overlap stay over their original body areas; do not blow the '
            'front guards behind her. Only the rear tips of the big blond mane and the rear coat panels sway '
            'slightly.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '양손 대검은 앞위 74–77°, 아래 손 y=704–714. 얼굴 높이는 날 왼쪽도 x≥267. 가슴 앞 땋은 머리, 앞 비늘갑과 앞자락 유지.'
        ),
    },
    'sheet/captain/runesmith': {
        'title': '브로크 이동', 'name': '브로크', 'refs': ['portrait.png'],
        'character': (
            'Brok, a stout, barrel-chested, bare-headed man (4 heads tall, short thick legs exactly as in the idle) '
            'with swept-back copper-orange hair and a huge braided orange beard bound with gold rings, dark-brown '
            'leather-and-steel armour with big rounded grey steel pauldrons and cyan-engraved plates, holding a '
            'heavy two-handed rune warhammer (grey steel block head with a cyan rune, dark wrapped haft, gold '
            'collar).'
        ),
        'carry': [
            'Keep the two idle hammer grips, lower hand x=220–229, y=678–695, near his belt. Keep the shaft at the '
            'idle angle (about 70° above horizontal; 67–72° is fine) and move the whole hammer about 16 px left: '
            'the head (about 98 px wide at this angle, never shrink it) centred at x≈300, its full width inside '
            'x=251–350, and its left corner at least 6 px ahead of his nose/brow (x≈244 at y=520–560). Keep the '
            'shaft ahead of the face above y=580, and the entire hammer within x=190–350, y=452–765. The '
            "mannequin's two separate arm swings and elbow locations do NOT apply to this character (intended, not "
            'a deviation). Let the shoulders follow the torso, keep both hands attached to the weapon, and limit '
            'fore-aft travel to 8 px.'
        ],
        'cloth': [
            'Keep his beard, front apron and armoured front flaps over his chest and thighs. Shoulder plates ride '
            'with the torso; back tips sway only slightly.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        # FORMAT 의 키 문장 대신 (마네킹 머리보다 머리가 작고 목이 거의 없다)
        'height': (
            "the figure about as tall as the idle stood up: Brok has almost no neck and his head is smaller than the "
            "mannequin's placeholder, so his hair top stays near y≈490–500 (the idle's 499 plus the 7-px bob), about "
            "50 px BELOW the mannequin's head top (y=440–447). His shoulders/pauldron tops go on the mannequin's "
            'shoulders (y≈570–585), and his face and beard sit where the mannequin\'s neck is. Do not stretch his '
            "torso or add a neck to reach the mannequin's height"
        ),
        'ko': (
            '양손 룬 망치는 대기 각도(약 70°)로 약 16px 왼쪽에: 머리 x≈300, 전폭 x=251–350 (머리 폭 약 98px, 줄이지 않는다). '
            '키는 마네킹 머리보다 약 50px 아래(머리 위 y≈490–500), 목을 늘이지 않는다. 앞 수염·앞치마·갑옷은 제자리.'
        ),
    },
    'sheet/captain/hedgemage': {
        'title': '펠릭스 이동', 'name': '펠릭스', 'refs': ['portrait.png'],
        'character': (
            'The accepted young mage has a floppy purple hat, belted violet robe to the shins, leather pouch, and '
            'a tall crooked wooden staff.'
        ),
        'carry': [
            'Keep both idle staff grips: the lower fist is at x≈195–237, y≈668–700, and the staff passes through it '
            'at x≈213–222; the upper fist is at x≈220–252, y≈610–645. Carry the staff at the idle angle, about 77° '
            'up and forward (74–78° allowed). At brim height (y≈495–510) the idle staff spans x≈258–280, just in '
            'front of the brim tip (x≈253–255). Keep that small gap in every frame, so the staff passes in front of '
            'the brim and never behind it or through it. If the leaned hat comes further forward, move both hands '
            'and the staff forward together (within the 10 px fore-aft limit). This shift is intended, not a '
            "deviation. Guide the full staff within x=183–326, y=401–815. Do not plant it. The mannequin's two "
            'separate arm swings and elbow locations do NOT apply to this character (intended, not a deviation). '
            'Let the shoulders follow the torso, keep both hands attached to the weapon, and limit fore-aft '
            'travel to 10 px.'
        ],
        'cloth': [
            'Keep rope belt and front robe panel below it; the loose hem follows the leading step, settles one '
            'frame late and leaves boots visible below it. The rear pouch and hat tip may bob.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '양손 지팡이는 대기 그립·각도(앞위 약 77°, 74–78°) 그대로, 모자 챙 높이에서 챙 끝(x≈253–255) 바로 앞(x≈258–280)을 '
            '지난다. 허리끈과 앞 로브는 앞쪽 유지.'
        ),
    },
    'sheet/captain/pilgrim': {
        'title': '아멜리 이동', 'name': '아멜리', 'refs': ['portrait.png'],
        'character': (
            'Amelie wears a cream hood and mantle over a long navy gold-trimmed tunic with bare feet. Copy her '
            'long-hafted star-headed mace and the exposed idle grip.'
        ),
        'carry': [
            'Use the exposed idle weapon hand at x=250–258, y=630–645, above the hip. Only the mace hand shows in '
            'the accepted idle. Keep the other arm hidden under the cream mantle in every frame and do not draw a '
            'second hand. The prayer beads and gold cross hang free at the chest over the navy tunic. Hold the '
            'staff-like mace steeply forward at the idle angle, about 82° above horizontal (80–84°). Keep the star '
            'head where the idle has it. It is about 88 px wide and 73 px tall: spikes at x≈231–318, y≈404–476, '
            'with the gold collar below down to y≈506. Its lower-left spike stays just above the hood (the hood '
            'reaches about x≈245 at y≈500). If the leaned hood comes forward under the star, tip the mace a few '
            'degrees further forward (no lower than about 77°) so the star stays above and in front of the hood. '
            'Do not shrink the star or let it overlap the hood. Keep the lower shaft inside x=202–267 down to '
            'y≤824. Carry it off the floor and move the grip fore-aft by at most 8 px.'
        ],
        'cloth': [
            'The braid stays OVER the front of the cream mantle. Keep the navy front panel in front of the legs, '
            'allow the rear mantle edge to lag, and show bare toes below the hem.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '긴 별머리 철퇴는 대기 각도(약 82°)로 세워 들고 손 y=630–645, 별(x≈231–318, y≈404–476)은 두건 위·앞, 줄이지 '
            '않는다. 다른 손은 망토 속(그리지 않는다). 가슴 앞 땋은 머리·묵주, 남색 앞자락, 맨발 유지.'
        ),
    },
    'sheet/captain/pirateking': {
        'title': '크림슨 이동', 'name': '크림슨', 'refs': ['portrait.png'],
        'character': (
            'Crimson has a feathered gold-edged tricorne, long red hair, a red long coat with cream lapels, '
            'trousers, tall boots, and a curved basket-hilt cutlass.'
        ),
        'carry': [
            "Cutlass in the NEAR (right) gloved hand only, with the idle's gold basket guard, gold pommel ball and "
            "curved blade unchanged. The near arm does NOT follow the mannequin's pump: the mannequin's near elbow "
            'and hand positions do not apply to this arm (intended, not a deviation). The shoulder follows the '
            'torso lean and the fist stays low at the near hip, x=213–230, y=699–719, in all 8 frames. Turn the '
            'fist so the curved blade leaves it pointing BACK and down 20–28° below horizontal, tip to the rear, '
            'with the gold knuckle bow still wrapped round the fist and the pommel ball just in front of it. The '
            'whole cutlass fits inside x=64–270, y=675–824. The FAR (left) gloved hand stays open and follows the '
            "mannequin's far arm. In R2–R5 that hand passes behind the hips at x=226–258, y=715–725, behind the "
            'cutlass fist, so the near fist and the coat hide it. Draw only the part that shows, and never on the '
            'hilt or the face.'
        ],
        'cloth': [
            'Keep the cream lapels, the ruffled shirt and the gold-buttoned waistcoat on the chest exactly as in the '
            'idle; no hair lies over the chest. The strand under the hat brim in front of the ear stays with the '
            'face, and the gold hoop earring stays on. The long wavy crimson hair mass behind the near shoulder and '
            'down the back lags by one frame, together with the long rear coat tails. The front coat edges stay at '
            'the front, never thrown back. The black gold-trimmed tricorne with its skull and its cream-and-red '
            'feather keeps the accepted silhouette.'
        ],
        'face': 'Face: match the accepted idle in every frame.',
        'ko': (
            '외손 커틀러스는 가까운 손, 마네킹 팔 흔들기를 따르지 않는다: 주먹 x=213–230, y=699–719, 날은 뒤아래 20–28°. '
            '먼 손은 R2–R5 에서 주먹·코트 뒤에 가린다. 앞깃·셔츠·조끼는 가슴에(가슴 위 머리 없음), 긴 머리와 뒷자락만 늦게.'
        ),
    },
    'sheet/captain/frostjarl': {
        'title': '비요른 달리기', 'name': '비요른', 'refs': ['portrait.png'],
        'character': 'Bjorn: blond frost jarl with two front braids, blond beard, slate-blue armoured tunic, snowflake '
                     'pauldron, pale fur mantle and fur-trimmed boots. Copy the long-hafted bearded axe and its two-handed '
                     'grip from the accepted idle.',
        'carry': [
            'Keep both hands on the axe, about 70 px apart on the shaft as in the idle, but carry it sloped BACK '
            'across the body (port arms): the near right hand low in front of the belly at x=225–245, y=680–700 (at '
            'most 30 px fore-aft), the shaft rising up and BACK (toward the left) at 50–60 deg above horizontal over '
            'the near shoulder, and the far left hand about 70 px up the shaft at the chest (about x=180–210, '
            'y=620–645). The axe head rides above and behind the back of the head (all axe pixels between x=60 and '
            'x=351, top at or below y=445, butt about 40 px forward-down of the lower hand). The shaft and blade '
            "never cross the face, beard or braids; they may overlap only the back hair and the mantle. The idle's "
            'forward-up angle does not fit: at any angle it runs the shaft through the running head, which leans '
            "forward (intended, not a deviation). The mannequin's two separate arm swings and elbow positions do NOT "
            'apply to this character (intended, not a deviation): the shoulders follow the torso lean and the grip '
            'rides with the torso, no arm pump, no swing.',
        ],
        'cloth': [
            'Both gold-bound braids stay over the FRONT of the chest (the far forearm passes under their tips) and '
            'bounce lightly. Keep the white fur mantle across the shoulders. The long wavy back hair streams back a '
            'little and settles one frame late, as do the side and rear tunic panels. The front centre flap hangs '
            'between the thighs and swings with the leading thigh; never let it trail back. Leave the trousers and '
            'boots free.',
        ],
        'face': 'Face and beard: exactly as in the accepted idle.',
        'ko': "양손으로 도끼를 쥐되 대기와 달리 몸을 가로질러 뒤로 기울여(받들어총처럼) 들고, 도끼 머리는 머리 뒤 위쪽에 둔다 (아래 손 x=225–245, y=680–700 배 앞, 자루는 뒤쪽으로 50–60°). 자루·날은 얼굴·수염·땋은 머리를 지나지 않는다. 두 팔을 따로 흔들지 않는다. 앞머리 두 갈래는 가슴 앞에 남긴다.",
    },
    'sheet/captain/ironwall': {
        'title': '브리긴다 이동 (중량)', 'name': 'Briginda (브리긴다), the iron-wall brigade commander', 'refs': ['portrait.png'],
        'character': 'sturdy, broad-shouldered woman; open steel helmet with gold trim; long auburn hair in a thick braid hanging down '
                     'her BACK on the screen-left side; scar across the nose; slate-grey plate armour with gold trim (pauldrons, '
                     'breastplate, tassets); grey tabard; leather belt; dark trousers, brown boots; a spiked MACE (morning star) in '
                     'the NEAR hand; a tall rectangular TOWER SHIELD with a gold rim on the FAR arm (about 2 heads tall, ~220 px, and '
                     '1 head wide, ~110 px).',
        'carry': [
            'Tower shield (far arm): held UP in front of the chest in EVERY frame, exactly as in the idle: its top edge where the '
            'idle has it relative to her helmet and belt (about chin height), its bottom edge about 80-110 px above the floor '
            '(y 760-790) so the knees and boots show below it, face toward the viewer\'s right. It does NOT swing: it moves up and down with the body (lowest in H2/H6) and '
            'at most about 10 px fore-aft. Front edge left of x=345 in every slot. The far forearm stays across the front at chest '
            'height, as in the mannequin.',
            'Mace (near hand): held ready at the belt/hip with the spiked head UP and a little forward, as in the idle (haft about 50 deg from vertical, '
            'head about chest height beside the shield). The near hand follows the mannequin\'s near hand (it moves only '
            '7-18 px fore-aft); the mace never swings, never hangs down and never crosses the face. Whole mace inside the slot.',
            'The shield may cover part of the torso and the far thigh, never the face; the mace head stays readable beside the '
            'shield edge.',
        ],
        'cloth': ['The braid swings a little behind her back and lags the body by ONE frame; the tabard and tassets sway slightly '
                  'with each footfall (the weight drop in H2/H6) - no flapping.'],
        'face': 'Face: set and determined, eyes forward, mouth closed; the helmet sits steady.',
        'ko': '탑 방패는 먼 팔에 **가슴 앞에 세운 채**(위 끝 턱 높이, 아래 끝 y 760~790 — 흔들지 않고 몸과 함께만 오르내림), 철퇴는 가까운 손에 '
              '**허리 높이로, 머리를 위로** 쥔다 — 휘두르지 않는다. 땋은 머리·타바드는 한 칸 늦게 조금 흔들린다.',
    },
    'sheet/class/mage': {
        'title': '병과 마법사 이동 (로브)', 'name': 'the generic class mage (마법사)',
        'character': 'face hidden in shadow under a wide-brimmed pointed HAT pulled low (compact cone about one head tall, brim no '
                     'wider than the shoulders, accent hat band) and a HIGH COLLAR over the mouth and chin; long ROBE to the shins '
                     'with a shoulder capelet, an accent front trim line, accent hem and cuff trim and an accent SASH; brown belt '
                     'pouches; brown boots; a straight wooden STAFF with a small AMBER crystal on top (warm orange-yellow, no glow).',
        'carry': [
            'Staff: held diagonally in front of the body with BOTH hands, as in the idle (upper hand at the chest, lower hand at the '
            'belt), the top tilted forward, the crystal above the hat brim. It is CARRIED, not planted: it moves only with the hands '
            '(the mannequin\'s small hand swing, at most ~35 px fore-aft), its lower end never goes below y=840, never touches the '
            'floor and never passes between the feet; the crystal stays inside x<=351 of the slot.',
            'Robe class: both hands KEEP THE IDLE\'S GRIP on the staff; the grip rides with the torso and swings at most about 35 px '
            'fore-aft. The mannequin\'s two separate hand positions do NOT apply to this character (intended, not a deviation).',
            'Volume: keep the idle\'s robe volume - skirt flaring to about the idle\'s hem width, the capelet, the wide sleeves. The '
            'mannequin\'s narrow skirt is only a placement guide; drawing it as narrow as the mannequin makes add_gait refuse the '
            'frames as a mannequin copy. If add_gait still refuses a frame at IoU <= ~0.9, write 막힘 in NOTES - do not distort the drawing.',
        ],
        'cloth': [
            'HEM: the robe hides the knees and thighs in EVERY frame (like the mannequin\'s cloth_front layer); only the boots flick '
            'out at the hem - the front boot ahead of / below the hem at contact, the back boot peeking out behind. The hem is pushed '
            'out at once by the stepping leg and falls back ONE FRAME LATE (G2/G6 still keep the contact hem shape). Keep the robe '
            'length of the idle: the hem trim\'s lowest point about y 840-850 at the front (about 20-30 px above the floor), higher '
            'at the sides; it never touches y=870.',
            'The capelet and the sleeves sway a little and lag one frame. The visible sash end hangs on the FRONT of the robe as in the idle and keeps hanging there, with only a small swing across the front panel - never thrown back behind the body.',
        ],
        'face': 'Face: in shadow between the brim and the collar in every frame (no eyes, no skin); the hat stays on and steady.',
        'ko': '지팡이는 대기처럼 **두 손으로 몸 앞에 비스듬히**(수정이 위·앞) 들고 다닌다 — 짚지 않는다. 로브 자락은 **한 칸 늦게** '
              '흔들리며 **무릎을 늘 가리고**, 장화 끝만 자락 밖으로 나온다.',
    },
    'sheet/class/archer': {
        'title': '병과 궁수 달리기', 'name': 'the generic class archer (궁수)',
        'character': 'face hidden - the HOOD of the tunic is UP and a cloth MASK covers the lower face up to the nose (only a narrow '
                     'warm-dark shadow strip at eye level); knee-length HOODED TUNIC with accent hem trim; small brown leather vest '
                     'with crossing straps; leather bracers and gloves; belt pouch; dark trousers, brown boots; a short recurve BOW '
                     '(brown wood, ONE clean string) in the FAR hand; a brown leather QUIVER of arrows on the back (fletchings above '
                     'the near shoulder); lean build.',
        'carry': [
            'Bow (far hand): carried LOW in the far hand, roughly upright with the string toward the body, as in the idle. It moves '
            'with the far arm (forward in R6-R8/R1, back toward the hip in R2-R5) but stays in front of the far hip/thigh: never '
            'behind the body, never above the shoulder, no arrow nocked. Its lower tip stays above y=852 in R4/R8 and its front edge '
            'left of x=345.',
            'Near hand: an empty gloved fist pumping with the mannequin\'s near arm; the forearm may drop to belt height as in the '
            'idle - intended, not a deviation.',
            'Quiver: fixed on the back, fletchings above the near shoulder; it bounces at most a few px with the body, no arrow '
            'falls out.',
        ],
        'cloth': ['The hood and the tunic skirt trail back and lag the body by ONE frame: they lift most in R1/R5 (right after the '
                  'flight) and settle in R3/R7. The hood stays UP and the mask on (the mask in the dark outfit keys, as in the sheet).'],
        'face': 'Face: in shadow (hood + mask) in every frame, as in the idle.',
        'ko': '활은 **먼 손에 낮게, 몸 앞에 세워** 들고(화살은 메기지 않는다) 먼 팔과 함께 흔든다. 가까운 손은 빈 주먹으로 흔든다. '
              '화살통은 등에 붙어 있다. 후드·튜닉 자락은 한 칸 늦게 뒤로.',
    },
    'sheet/class/cleric': {
        'title': '병과 성직자 달리기', 'name': 'the generic class cleric (성직자)',
        'character': 'face hidden in shadow - a deep COWL pulled low over the brow (accent front edge) and a short VEIL of the same '
                     'cloth across the lower face; grey chainmail; knee-length TABARD over the mail with accent border trim and ONE '
                     'plain filled accent disc on the chest (no symbol); a small brown leather book on the belt; dark trousers, '
                     'brown boots; a one-handed flanged steel MACE with a wooden handle (about 190 px from pommel to flange tip - keep the sheet\'s length) in the NEAR hand.',
        'carry': [
            'Mace (near hand): held at the LOWER grip with the flanged head UP (haft about 20-45 deg forward of vertical), as in the '
            'idle - the head between chest and shoulder height. The near arm pumps with the mannequin, but the forearm drops so the '
            'fist sits at about y 660-700 (belt to hip; dropping it is intended, not a deviation). The mace rides along: it never '
            'hangs down toward the floor, never points backward, never swings. Never shorten it - change its angle instead.',
            'Far hand: free, open or loosely closed (calm, no claw fingers), pumping with the mannequin\'s far arm.',
            'The book stays on the belt.',
        ],
        'cloth': ['The tabard skirt and the cowl trail back and lag the body by ONE frame (they lift most in R1/R5 and settle in '
                  'R3/R7); the chest disc stays visible.'],
        'face': 'Face: in shadow under the cowl, veil on, in every frame.',
        'ko': '철퇴는 가까운 손에 **아래쪽을 쥐고 머리를 위로**(가슴~어깨 높이) 세운 채 팔과 함께 흔든다 — 늘어뜨리거나 휘두르지 '
              '않는다. 먼 손은 빈손으로 흔든다. 타바드·두건은 한 칸 늦게 뒤로.',
    },
    'sheet/class/rogue': {
        'title': '병과 도적 달리기', 'name': 'the generic class rogue (도적)',
        'character': 'face hidden - a deep HOOD pulled low (at most two small eye glints) with a short SHOULDER CAPE and a SCARF over '
                     'the mouth and nose; dark-brown leather armour with straps and ONE thin accent belt SASH; dark trousers, '
                     'dark-brown boots; lean, agile build; ONE short DAGGER in the NEAR hand in REVERSE grip (the blade leaves the '
                     'little-finger side and runs back along the forearm).',
        'carry': [
            'Dagger (near hand): REVERSE grip in EVERY frame, as in the idle - the blade lies back along the outside of the forearm, '
            'so when the near arm pumps forward (R2-R5) the blade trails behind the fist, and when the arm swings back (R6-R8/R1) '
            'it points back and a little down behind the hip. Never a forward grip, never pointing at the viewer or across the '
            'body; 1 px dark outline, the blade on the magenta where possible.',
            'Far hand: an empty fist (the idle\'s guard hand) pumping with the mannequin\'s far arm, elbow bent.',
        ],
        'cloth': ['The shoulder cape and the hood point trail back and lag the body by ONE frame (they lift most in R1/R5 and settle '
                  'in R3/R7); the sash ends flick back; the scarf stays over the mouth and nose (in the dark outfit keys, as in the sheet).'],
        'face': 'Face: in shadow under the hood in every frame (at most two small eye glints), scarf on.',
        'ko': '단검은 가까운 손에 **역수(칼날이 팔뚝을 따라 뒤로)** 그대로 쥐고 팔과 함께 흔든다 — 바로 쥐기로 바꾸지 않는다. '
              '먼 손은 빈 주먹으로 흔든다. 어깨 망토·후드 끝은 한 칸 늦게 뒤로.',
    },
}
# CARRY 에 없는 시트: 부류 기본 문장 (꾸러미의 CHARACTER 줄과 함께) — 만든 뒤 사람이 읽고 고칠 것
GENERIC_CARRY = {
    'light': ['Hands: hold exactly what the idle holds, in the same grip. Shoulders and elbows follow the mannequin; the forearm '
              'may drop so a weapon hand sits at belt height. A weapon rides along low and trails back/down (never raised, never '
              'swung); a shield stays in front of the chest.'],
    'heavy': ['Heavy class: arms close and high. A shield (if any) stays UP in front of the chest in every frame and only rides the '
              'body\'s bob; a weapon is held close at the belt; the hands move only 7-18 px fore-aft.'],
    'robe': ['Robe class: hands close to the body (at the waist or on a staff), small swing (at most ~35 px fore-aft); a staff is '
             'carried, never planted.'],
}
GENERIC_CLOTH = {
    'light': ['Loose cloth (cloak, skirt, hair) trails back and lags the body by ONE frame: it lifts most in R1/R5 and settles in '
              'R3/R7.'],
    'heavy': ['Hair and cloth sway slightly with each footfall and lag one frame - no flapping.'],
    'robe': ['HEM: the cloth hides the knees and thighs in EVERY frame; only the boots flick out at the hem. The hem is pushed out '
             'at once by the stepping leg and falls back ONE FRAME LATE; it never touches y=870.'],
}
WHY_KO = ('"달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는\n'
          '스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"')
SLOT_PX, HIP_X, FLOOR_Y = 384, 192, 870
INDEX_START, INDEX_END = '<!-- index:start (gait_requests.py --index) -->', '<!-- index:end -->'


def phase3_item(sid):
    for it in load('art/requests/phase3.json')['items']:
        if it.get('id') == sid:
            return it
    return {}


def character_line(pkg):
    """phase3 꾸러미 README 의 CHARACTER: 줄 (없으면 None)"""
    p = os.path.join(ROOT, pkg or '', 'README.md')
    if not pkg or not os.path.exists(p):
        return None
    for line in open(p, encoding='utf-8'):
        if line.startswith('CHARACTER:'):
            return line[len('CHARACTER:'):].strip()
    return None


def pairs(frames, key, fmt='{:g}'):
    """프레임 1..4 와 5..8 이 같으면 'R1/R5 a, R2/R6 b ...', 다르면 하나씩"""
    vals = [f.get(key) for f in frames]
    if len(vals) == 8 and vals[:4] == vals[4:]:
        return ', '.join(f'{frames[i]["frame"]}/{frames[i + 4]["frame"]} {fmt.format(vals[i])}' for i in range(4))
    return ', '.join(f'{f["frame"]} {fmt.format(v)}' for f, v in zip(frames, vals))


def planted_rows(pose):
    """디딘 발의 발끝 x (칸 좌표) 줄들: [(다리, [(프레임, x)], 마지막 프레임에서 뒷발이 된 자리 또는 None)]"""
    frames = pose['frames']
    names = [f['frame'] for f in frames]
    rows = []
    if pose.get('planted_toes'):
        for k, pt in enumerate(pose['planted_toes']):
            xs = pt['toe_x_px']
            start = 0 if pt['leg'] == 'near' else 4
            seq = [(names[(start + i) % 8], HIP_X + xs[i]) for i in range(len(xs))]
            rows.append((pt['leg'], seq[:4], seq[4] if len(seq) > 4 else None))
        return rows
    for leg, start in (('near', 0), ('far', 4)):        # light run: toe_x_px of the stance frames (no planted_toes block)
        seq = [(f['frame'], HIP_X + f['toe_x_px']) for f in frames[start:start + 4]
               if isinstance(f.get('toe_x_px'), (int, float)) and f.get('phase') != 'flight']
        rows.append((leg, seq, None))
    return rows


def fmt_x(v):
    return f'{v:.0f}'


def toe_lines(pose):
    lines = []
    for leg, seq, rear in planted_rows(pose):
        s = ' -> '.join(f'{fr} x={fmt_x(x)}' for fr, x in seq)
        if rear:
            s += f'  (-> {rear[0]} x={fmt_x(rear[1])} as the REAR foot, heel up, toe still on the floor)'
        lines.append(f'      {leg} foot: {s}')
    return lines


def stride_line(pose, scale):
    step = pose['step_px']
    return (f'  - Stride: one step = {step:g} source px = {step * scale:.1f} game px; '
            f'8 frames = two steps, {pose["nominal_ms"]} ms a frame in the game.')


def is_3d_folder(folder):
    """요청 폴더가 3D 마네킹 가이드로 만들어졌는가 (pose.json 의 mannequin3d 표시)"""
    try:
        pj = load(os.path.join(folder, 'pose.json'))
    except (OSError, ValueError):
        return False
    return isinstance(pj, dict) and bool(pj.get('mannequin3d')) and 'mannequin3d' in str(pj.get('source', ''))


def m3d_module():
    """tools/mannequin3d/request.py (3D 가이드)"""
    d = os.path.join(ROOT, 'tools', 'mannequin3d')
    if d not in sys.path:
        sys.path.insert(0, d)
    import request as m3d_request
    return m3d_request


def write_request(sid, out=None, force=False, date=None, spec=None, man=None, guides=None):
    """요청 폴더 하나 → (폴더 rel, CARRY 표에서 왔는가, geo, 자체 검사 명령).
    guides = '2d' (부류 확정 마네킹 띠, 기본) | '3d' (tools/mannequin3d — 캐릭터에 맞춘 3D 마네킹, carry3d.json 항목 필요) |
    None (이미 3D 로 만든 폴더면 3d, 아니면 2d)."""
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'art'))
    import run_request_guides as rg
    spec = spec or load(SPEC)
    man = man or load(MANIFEST)
    sid = rg.resolve(sid, man)
    cls = (spec['sheets'].get(sid) or {}).get('gait')
    if cls not in CLASSES:
        raise rg.Fail(f'{sid}: 부류 {cls!r} — light/heavy/robe 시트만 그린 이동 칸을 받는다')
    stem = os.path.splitext(os.path.basename(man[sid]['file']))[0]
    short = stem[len('sheet_'):]
    p = REQ_PREFIX[cls]
    folder = out or os.path.join(ROOT, 'art', 'requests', 'gait', f'{p}__{short}')
    old = os.path.join(folder, 'README.md')
    if os.path.exists(old):
        if not force:
            raise rg.Fail(f'{rel(folder)}/README.md 가 이미 있다 (그려 받은 요청일 수 있다) — 다시 만들려면 --force')
        if 'gait_requests.py --write' not in open(old, encoding='utf-8').read():
            raise rg.Fail(f'{rel(folder)}/README.md 는 손으로 쓴 요청이다 (run__class_warrior 같은 본보기) — --force 로도 덮어쓰지 않는다')
    if guides is None:
        guides = '3d' if is_3d_folder(folder) else '2d'
    if guides == '3d':
        return write_request_3d(sid, folder, cls, stem, short, p, date, spec, man)
    if is_3d_folder(folder):
        # 3D 요청을 2D 로 되돌린다: 3D 만의 파일을 지운다 (2D 와 이름이 같은 guide/size 는 아래에서 덮어쓴다)
        for n in m3d_module().names(p):
            if n not in (f'guide_{p}_a.png', f'guide_{p}_b.png', f'size_{p}_a.png', f'size_{p}_b.png'):
                fp = os.path.join(folder, n)
                if os.path.exists(fp):
                    os.remove(fp)
    geo = rg.build(sid, folder, cls, man, force=True)
    pose = load(geo['pose'])
    frames = pose['frames']
    item = phase3_item(sid)
    pkg = item.get('package') or geo.get('package')
    if not pkg and os.path.isdir(os.path.join(ROOT, 'art', 'requests', 'phase3', short)):
        pkg = f'art/requests/phase3/{short}'        # 꾸러미 칸이 없는 phase3 항목 (특별 용병 등)
    c = CARRY.get(sid)
    generic = c is None
    if generic:
        ch = character_line(pkg)
        c = {'title': f'{item.get("name", sid)} 이동', 'name': item.get('name', sid), 'refs': ['portrait.png'],
             'character': ch or (re.sub(r'^Battle sprite of\s*', '', item.get('prompt', '')).split(' Design,')[0].strip()
                                 or '(no CHARACTER line found - describe the idle of the accepted sheet)'),
             'carry': GENERIC_CARRY[cls], 'cloth': GENERIC_CLOTH[cls], 'face': 'Face: exactly as in the idle in every frame.',
             'ko': '(CARRY 표에 없음 — 부류 기본 문장. 손에 든 것·천을 확인하고 tools/art/gait_requests.py 의 CARRY 에 적은 뒤 다시 만들 것)'}
    gdir = os.path.dirname(geo['source_pose'])
    fa = ' '.join(f['frame'] for f in frames[:4])
    fb = ' '.join(f['frame'] for f in frames[4:])
    flight = [f['frame'] for f in frames if f.get('phase') == 'flight']
    step = pose['step_px']
    q = step / 4
    sc = geo['scale']
    ms = pose['nominal_ms']
    dl = [f'art/inbox/gait/{stem}_run_a.png', f'art/inbox/gait/{stem}_run_b.png']
    work = '<temp dir>'
    fl = ' --flight-slots 4' if flight else ''
    checks = [f'python3 tools/art/check_delivery.py {dl[0]}{fl}', f'python3 tools/art/check_delivery.py {dl[1]}{fl}',
              f'python3 tools/art/add_gait.py {shlex.quote(sid)} --gait run --src {dl[0]} {dl[1]} --pose {shlex.quote(geo["pose"])} --dry-run --work {work}']
    clsd = spec['classes'][cls]
    ko_cls = KO[cls]
    rel_folder = rel(folder) if folder.startswith(ROOT) else folder
    reqdir = f'art/requests/gait/{p}__{short}'
    refs_pkg = []
    if pkg and os.path.exists(os.path.join(ROOT, pkg, 'concept.png')):
        refs_pkg.append((f'{pkg}/concept.png', 'the design draft (design only - not proportions or rendering)'))
    for r in c.get('refs') or []:
        if pkg and os.path.exists(os.path.join(ROOT, pkg, r)):
            refs_pkg.append((f'{pkg}/{r}', 'the approved portrait (face, hair, colours only)' if 'portrait' in r else 'design reference'))
    ase = f'{gdir}/{pose["set"]}.aseprite'
    gif = f'{gdir}/{pose["set"]}_preview.gif'
    tops = [f.get('top_px') for f in frames]
    t0 = tops[0]
    dtop = ', '.join(f'{f["frame"]} {t - t0:+d}' for f, t in zip(frames[:4], tops[:4]))
    bob = max(tops) - min(tops)
    rows = planted_rows(pose)
    retreats = []
    for leg, seq, rear in rows:
        xs = [x for _, x in seq] + ([rear[1]] if rear else [])
        retreats += [a - b for a, b in zip(xs, xs[1:])]
    rmin, rmax = (min(retreats), max(retreats)) if retreats else (q, q)
    tint = geo.get('tint')
    colours = []
    if tint:
        o, a = tint.get('outfit', []), tint.get('accent', [])
        colours.append(f'KEY COLOURS (the engine recolours them per faction): the uniform cloth uses ONLY the exact sheet keys '
                       f'{" ".join(o)} (outfit, dark to light) and the trim ONLY {" ".join(a)} (accent), flat fills, on the SAME '
                       f'areas as in the sheet; these {len(o) + len(a)} colours nowhere else (not on metal, skin, leather, wood, outline or '
                       'shadows). Steel neutral grey, leather and wood warm brown, outline and shadows warm/neutral dark (as in the sheet).')
    elif item.get('colors'):
        cs = '; '.join(f'{k} {v}' for k, v in item['colors'].items())
        colours.append(f'COLOURS: take every colour from the accepted sheet (same palette, ~40 colours); the design colours were {cs}.')
    if item.get('spots'):
        colours.append(f'SPOT COLOURS (tiny must-show colours, keep them exactly): {", ".join(item["spots"])}.')
    lean = pairs(frames, 'lean_deg')
    move_word = 'RUN' if cls == 'light' else ('HEAVY TRUDGE (fast, purposeful)' if cls == 'heavy' else 'ROBE GLIDE (hurried, purposeful)')
    lifted = [f.get('other_sole_height_px') for f in frames if f.get('other_sole_height_px')]
    lift = f'{min(lifted)}-{max(lifted)}' if lifted else '5-13'
    catch_head = (', but the torso straightens, so the head top is the HIGHEST of the cycle - see Height'
                  if tops[1] == min(tops) else '')
    phase_lines = {
        'light': [f'  - {frames[0]["frame"]} contact (near foot lands a little ahead, knee bent) - {frames[1]["frame"]} catch (the hips drop '
                  f'onto the foot: lowest hips{catch_head}) - {frames[2]["frame"]} push-off (stance leg extends behind, heel up) - {frames[3]["frame"]} FLIGHT (both '
                  f'feet clearly off the ground, legs scissored, body pressed forward and leaning the most). {frames[4]["frame"]}-'
                  f'{frames[7]["frame"]} = the same with the far foot.',
                  f'  - The hips stay nearly level: the top of the head stays within about 10 px of the same height in all 8 frames. NO '
                  'hopping, no bouncing up and down.'],
        'heavy': [f'  - {frames[0]["frame"]} contact (BOTH feet on the floor: the near foot lands ahead, the far foot still behind, heel '
                  f'up) - {frames[1]["frame"]} down (the weight drops onto the near foot: lowest frame, knees bent most) - '
                  f'{frames[2]["frame"]} passing (the far foot swings low past the standing foot, only {lift} px off the floor) - '
                  f'{frames[3]["frame"]} push (the standing heel lifts, the body rises back). {frames[4]["frame"]}-{frames[7]["frame"]} = '
                  'the same with the far foot.',
                  f'  - NO FLIGHT: one sole is on y=870 in EVERY frame (both in {frames[0]["frame"]}/{frames[4]["frame"]}). The torso is '
                  'almost upright and the head stays level; the weight shows ONLY as the drop in the down frame, then it comes back '
                  'up slowly (the push is never higher than the contact). Knees low, stride short - heavy, grounded footfalls at a '
                  'quick cadence, not a stroll.'],
        'robe': [f'  - {frames[0]["frame"]} contact (BOTH feet on the floor under the hem) - {frames[1]["frame"]} down (a small settle '
                 f'onto the near foot) - {frames[2]["frame"]} passing (the far foot slides past just above the floor, {lift} px) - '
                 f'{frames[3]["frame"]} push. {frames[4]["frame"]}-{frames[7]["frame"]} = the same with the far foot.',
                 f'  - NO FLIGHT, no big knee lift: one sole is on y=870 in EVERY frame (both in {frames[0]["frame"]}/'
                 f'{frames[4]["frame"]}). A smooth, nearly level glide with a small forward lean and short quick steps - hurried, '
                 'not a stroll.'],
    }[cls]
    # CARRY 의 'height' = 시트마다 키 문장 (머리·목이 마네킹과 많이 다른 캐릭터)
    height = c.get('height') or (f'the figure about as tall as the idle stood up (the mannequin\'s head top is near '
                                 f'y={min(tops)}-{max(tops)})')
    fmt_lines = [f'  - the hip centre of every frame on the slot\'s column x={HIP_X} (the body stays in place, the feet move);']
    if flight:
        fmt_lines += [f'  - {" ".join(f["frame"] for f in frames if f.get("phase") != "flight")}: the sole of the standing foot on '
                      f'y={FLOOR_Y} (lowest pixel), the other foot well above it;',
                      f'  - {" / ".join(flight)} (FLIGHT): NOTHING touches y={FLOOR_Y} - the lowest pixel of the whole figure (boots, '
                      'weapon, cloth) at or above y=852;']
    else:
        fmt_lines += [f'  - EVERY frame: the lowest pixel of the figure is the standing sole on y={FLOOR_Y} (no flight frame); in '
                      f'{frames[0]["frame"]}/{frames[4]["frame"]} both soles are on y={FLOOR_Y}; the lifted sole 3-'
                      f'{pose.get("other_foot_max_px", 13)} px above it; nothing below y={FLOOR_Y} (no weapon tip, no hem);']
    fmt_lines += ['  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - '
                  'nothing may cross into the next slot, including weapons, cloth and hair);',
                  f'  - head {pose.get("head_px", 110):g} px scale = the scale of the accepted sheet ({sc:g} source -> game: the idle is {geo["game_idle_h"]} game px '
                  f'tall); {height}.']
    receive = f'python3 tools/art/receive.py gait/{stem}_run'
    notes_h = f'## gait/{stem}_run - {c["title"]}'
    refs_list = [f'guide_{p}_a/b', f'size_{p}_a/b', os.path.basename(geo['source'])] + [os.path.basename(r) for r, _ in refs_pkg] + ['pose.json']
    ko_files = [
        f'| `guide_{p}_a.png` / `guide_{p}_b.png` | **자세·자리 가이드** = 확정 {ko_cls} 마네킹 띠'
        f'{"를 시트 배율에 맞춰 조정" if geo["scaled"] else " 그대로"}({frames[0]["frame"]}'
        f'~{frames[3]["frame"]} / {frames[4]["frame"]}~{frames[7]["frame"]}). 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 '
        f'y=870{", " + "·".join(flight) + " 은 공중" if flight else ", 뜨는 칸 없음"} |',
        f'| `size_{p}_a.png` / `size_{p}_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 마네킹 '
        f'{frames[0]["frame"]}/{frames[4]["frame"]} 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 마네킹 + 바닥 줄·엉덩이 열·x=32/351 선·'
        '디딘 발끝 자리(노란 눈금) |',
    ]
    for r, what in refs_pkg:
        ko_files.append(f'| `{r}` | {"승인된 초상화 — 얼굴·머리·색" if "portrait" in r else "디자인 초안 — 디자인만"} |')
    ko_files.append(f'| `{geo["source"]}` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |')
    if geo['scaled']:
        ko_files.append(f'| `{geo["pose"]}`, `{gif}` | 이 요청의 좌표·보폭과 원본 움직임. 덧그리기는 이 폴더의 '
                        f'`guide_{p}_a.png` / `guide_{p}_b.png` 위에만 한다. |')
    else:
        ko_files.append(f'| `{gdir}/` (`pose.json`, `{pose["set"]}_preview.gif`, `{pose["set"]}.aseprite`) | 마네킹 원본 — 숫자·움직임 확인용 |')
    lines = [
        f'# {c["title"]} · `{sid}` → `gait/{stem}_run`',
        '',
        f'**상태: 요청 ({date}, 클라우드 — `python3 tools/art/gait_requests.py --write {sid}` 로 만듦).** Antigravity 가 이 README 하나와 아래 '
        '그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.',
        '',
        f'**왜 (주인 2026-11-26)**: {WHY_KO}',
        f'→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 {ko_cls}({cls})의 '
        f'{"이 폴더의 조정된 가이드" if geo["scaled"] else f"확정 마네킹(`{gdir}/`)"} 8프레임 위에 '
        '캐릭터를 프레임마다 덧그린다.** 그린 그림은 찌그러뜨리지 않는다(엔진은 칸을 그대로 넘긴다).',
        f'그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 {ms}ms 박자로 넘긴다'
        f'{" (뜬 칸 포함)" if flight else " (디딘 발이 붙어 있게: 칸마다 한 걸음의 1/4)"}.',
        '',
        '| 파일 | 내용 |',
        '|---|---|',
        *ko_files,
        '',
        f'- 부류: **{ko_cls}** — {(spec["sheets"].get(sid) or {}).get("why", "")} ({SPEC})',
        f'- 납품: art-inbox `{dl[0]}` ({fa.split()[0]}~{frames[3]["frame"]}) + `{dl[1]}` ({frames[4]["frame"]}~{frames[7]["frame"]}) + '
        f'`art/inbox/NOTES.md` 절 「{notes_h[3:]}」 + 「## 판정 — gait/{stem}_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).',
        f'- 팔·무기: {c["ko"]}',
        f'- 디딘 발: 한 걸음 원본 {step:g}px(게임 {step * sc:.1f}px) → 디딘 발은 칸마다 **정확히 {q:.1f}px**(±3, 게임 {q * sc:.1f}px) 뒤로 — 발끝 x 는 '
        'Prompt 의 PLANTED FOOT 표. (병과 전사 R5 는 디딘 발이 30px 앞에 그려져 한 번 고쳤다.)',
        f'- 클라우드가 받은 뒤: `{receive}` (검사 + `add_gait.py --dry-run`) → 미리보기를 보고 `add_gait.py` 로 붙인다 (`--pose {geo["pose"]}`).',
    ]
    if generic:
        lines.append('- **검토 필요**: 이 시트는 `tools/art/gait_requests.py` 의 CARRY 표에 없어 손에 든 것·천 문장이 부류 기본값이다.')
    P = [
        f'TASK: draw the {move_word} CYCLE (8 frames, movement class {cls.upper()}) of {c["name"]} as TWO new PNG strips on the '
        'art-inbox branch:',
        f'  {dl[0]}  = frames {fa}',
        f'  {dl[1]}  = frames {fb}',
        '(the file names say "run" for every movement class: the engine plays them as the sheet\'s run.)',
        f'Draw the character OVER the accepted {cls} mannequin, frame by frame - like a sprite sheet traced over a skeleton.',
        'Do NOT take the standing/idle art and bend, shear or rotate it: that is exactly what made the moves look squashed.',
        '',
        'REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):',
        f'  - {reqdir}/guide_{p}_a.png, guide_{p}_b.png = THE POSE AND PLACEMENT GUIDE for every frame',
        '    (the accepted mannequin, same canvas as your delivery: 1536x1024, 4 frames per strip in 384-px slots).',
        f'  - {reqdir}/size_{p}_a.png, size_{p}_b.png = the same frames with guide lines and the planted-toe ticks, and on the left',
        '    the accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.',
        f'  - {geo["source"]} (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.',
        '    Same character, same pixel size, same palette.',
        *[f'  - {r} = {what}.' for r, what in refs_pkg],
        *([f'  - {geo["pose"]} (the scaled coordinates and stride), {gif} (motion reference only).',
           f'    Draw only over this folder\'s guide_{p}_a.png and guide_{p}_b.png.']
          if geo['scaled'] else
          [f'  - {geo["pose"]} (the numbers below come from it), {gif} (the motion at speed), {ase} (the mannequin source -',
           '    you may open it as an underlay and draw on your own layers, but the delivered PNGs contain ONLY your drawing).']),
        '',
        f'CHARACTER (unchanged from the accepted sheet): {c["character"]}',
        '',
        f'THE MOVE (owner\'s three movement classes; {cls}: {clsd["summary"]} It is already in the mannequin - copy it, do not invent another):',
        *(c.get('joints') or [
            '  - Each frame: the legs, the torso lean and the arm swing of that mannequin frame. Joint for joint: hips, knees, ankles, feet,',
            '    shoulders, elbows (hands: see ARMS - where the text moves a hand, that is intended, not a deviation).',
            '    The mannequin\'s big round head is a placeholder: draw the character\'s own head on the mannequin\'s neck, at its own size',
            '    (as in the sheet).']),
        *phase_lines,
        f'  - Lean forward (hip to neck): {lean} deg.',
        (f'  - Height: the mannequin\'s head top is at y={"/".join(str(t) for t in tops[:4])} in {fa} (the same in {fb}): '
         if tops[:4] == tops[4:] else
         f'  - Height: the mannequin\'s head top is at y={"/".join(str(t) for t in tops[:4])} in {fa} and '
         f'{"/".join(str(t) for t in tops[4:])} in {fb}: ')
        + f'{dtop} px from {frames[0]["frame"]} (+ = lower) - move your head top by the same amounts (bob {bob} px).',
        stride_line(pose, sc),
        f'  - PLANTED FOOT (the rule the class warrior\'s R5 needed a fix for): a foot on the floor never slides in the drawing. From its',
        f'    contact frame on, the SAME boot moves LEFT by exactly step/4 = {q:.1f} px per frame (the mannequin: {rmin:.0f}-{rmax:.0f} px;',
        f'    tolerance 3 px) - the engine moves the unit {q * sc:.1f} game px per frame, so the boot stays still on the ground.',
        '    Toe tip of the planted boot = its FRONT-MOST pixel (the toe; on a tapered boot it may sit a few px above y=870, as on the '
        '    mannequin) = the yellow tick in size_*.png; x in the 384-px slot:',
        *toe_lines(pose),
        *([f'      ({" / ".join(flight)}: flight - no foot on the floor; the next contact lands ahead again)'] if flight else []),
        '    Draw the planted boot once, then copy it from frame to frame and only shift it (lift the heel in the push frame); measure',
        '    YOUR toe tip against these numbers (the size_* images mark them with yellow ticks).',
        '',
        'ARMS AND WEAPONS:',
        *[f'  - {s}' for s in c['carry']],
        *[f'  - {s}' for s in c['cloth']],
        f'  - {c["face"]}',
        '',
        'MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon and shield shapes and sizes, and the SCALE of the accepted',
        'sheet. The body must not be shrunk to fit - change a weapon\'s angle instead.',
        *colours,
        '',
        'FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,',
        f'front three-quarter view, light from the upper left, exactly the placement of guide_{p}_a/b.png:',
        *fmt_lines,
        'STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.',
        'BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).',
        'NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text or guide lines in the delivery.',
        '',
        'SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):',
        *[f'  {cmd}' for cmd in checks],
        ('The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). '
         if flight else 'The first two must print RESULT: PASS (NO --flight-slots: every pose must stand on y=870). ')
        + f'The third must end without an error and write',
        f'{work}/{stem}_preview_x4.png and {stem}_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at',
        '4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the',
        'planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your drawing.)',
        '',
        'DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:',
        f'  {notes_h}',
        '  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")',
        f'  REFERENCES LOADED: {", ".join(refs_list)} -> ok / FAILED (reason)',
        '  CHANGED: what you drew, frame by frame where it matters (planted toe x per frame as you measured it)',
        '  DEVIATIONS: (a) from the mannequin pose/position per frame (b) from the sheet design (c) from the ARMS AND WEAPONS',
        '              lines - write "none" explicitly for each',
        '  RISKS AT GAME SIZE: what you could not verify at ~64 px',
        f'  ## 판정 — gait/{stem}_run',
        '  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)',
        '  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)',
        '  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)',
        '  남은 걱정: (what the QA cross-check should look at; "없음" if none)',
        '  캐릭터 메모: (direction for this character\'s next motions; omit if none)',
        'Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.',
    ]
    lines += ['', '## Prompt for Antigravity', '', '```', *P, '```', '']
    with open(os.path.join(folder, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return rel_folder, not generic, geo, checks


# ───────── --write --guides 3d: 3D 마네킹 가이드 요청 (주인 2026-11-28) ─────────
# 주인 결정 2026-11-28: 가상 3D 마네킹 → 동작 → 스프라이트 띠 → Antigravity 가 그 위에 캐릭터를 덧그린다. 무기 손목 범위는
# 아래팔에 대해 0~120도(위든 아래든 그 안이면 된다), 무기·몸·얼굴이 겹쳐도 가까운 쪽이 먼 쪽 위에 그려지면 된다(깊이 순서),
# 바닥 줄 아래로 내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 부류·캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다,
# 그림 판정은 주인이 직접 한다(리드가 그림을 통과·탈락시키지 않는다).
OWNER_3D_KO = ('"가상의 3D 마네킹 → 동작 → 스프라이트 띠 → Antigravity 가 그 위에 캐릭터를 덧그린다" (주인 2026-11-28). '
               '무기 손목은 아래팔 기준 0~120도 안(위·아래 상관없음), 겹침은 가까운 쪽이 위에 그려지면 괜찮다, 바닥 아래로 '
               '내려간 소품은 그릴 때 손본다, 견본은 기준선일 뿐, 캐릭터마다 자기 움직임 개성, 색만 바꾼 자산은 없다, '
               '그림 판정은 주인이 직접 한다.')


KIND_KO = {'sword': '칼', 'mace': '철퇴', 'staff': '지팡이'}


def write_request_3d(sid, folder, cls, stem, short, p, date, spec, man):
    """3D 마네킹 가이드 요청 폴더 (tools/mannequin3d/request.py 의 그림 + 3D 용 README) → write_request 와 같은 꼴"""
    m3d = m3d_module()
    geo = m3d.build_request(sid, folder, cls, man, force=True)
    pose = load(geo['pose'])           # rel to the repo, or an absolute --out path (os.path.join keeps it)
    frames = pose['frames']
    item = phase3_item(sid)
    entry = geo['m3d']['entry']
    pz = geo['m3d']['personality']
    look = (entry.get('request') or {}).get('look')
    look_ko = (entry.get('request') or {}).get('look_ko')
    pkg = item.get('package') or geo.get('package')
    if not pkg and os.path.isdir(os.path.join(ROOT, 'art', 'requests', 'phase3', short)):
        pkg = f'art/requests/phase3/{short}'
    name = item.get('name', sid)
    title = f'{name} 이동 (3D 마네킹)'
    if not look:
        look = character_line(pkg) or '(no look in carry3d.json request.look - describe the idle of the accepted sheet)'
    fa = ' '.join(f['frame'] for f in frames[:4])
    fb = ' '.join(f['frame'] for f in frames[4:])
    flight = [f['frame'] for f in frames if f.get('phase') == 'flight']
    step = pose['step_px']
    q = step / 4
    sc = geo['scale']
    ms = pose['nominal_ms']
    dl = [f'art/inbox/gait/{stem}_run_a.png', f'art/inbox/gait/{stem}_run_b.png']
    work = '<temp dir>'
    fl = ' --flight-slots 4' if flight else ''
    checks = [f'python3 tools/art/check_delivery.py {dl[0]}{fl}', f'python3 tools/art/check_delivery.py {dl[1]}{fl}',
              f'python3 tools/art/add_gait.py {shlex.quote(sid)} --gait run --src {dl[0]} {dl[1]} --pose {shlex.quote(geo["pose"])} --dry-run --work {work}']
    clsd = spec['classes'][cls]
    ko_cls = KO[cls]
    rel_folder = rel(folder) if folder.startswith(ROOT) else folder
    reqdir = f'art/requests/gait/{p}__{short}'
    refs_pkg = []
    if pkg and os.path.exists(os.path.join(ROOT, pkg, 'concept.png')):
        refs_pkg.append((f'{pkg}/concept.png', 'the design draft (design only - not proportions or rendering)'))
    if pkg and os.path.exists(os.path.join(ROOT, pkg, 'portrait.png')):
        refs_pkg.append((f'{pkg}/portrait.png', 'the approved portrait (face, hair, colours only)'))
    tops = [f.get('top_px') for f in frames]
    t0 = tops[0]
    dtop = ', '.join(f'{f["frame"]} {t - t0:+d}' for f, t in zip(frames[:4], tops[:4]))
    bob = max(tops) - min(tops)
    rows = planted_rows(pose)
    retreats = []
    for leg, seq, rear in rows:
        xs = [x for _, x in seq] + ([rear[1]] if rear else [])
        retreats += [a - b for a, b in zip(xs, xs[1:])]
    rmin, rmax = (min(retreats), max(retreats)) if retreats else (q, q)
    lean = pairs(frames, 'lean_deg')
    wl = (entry.get('weapon_limit') or {'min': 0.0, 'max': 120.0})
    wmin, wmax = float(wl.get('min', 0.0)), float(wl.get('max', 120.0))
    wang = [(f['frame'], w) for f in frames for w in (f.get('weapon_angle') or [])]
    held = sorted({(w['kind'], 'near' if w['hand'] == 'N' else 'far') for _, w in wang})
    held_txt = ', '.join(f'{KIND_KO.get(k, k)} ({"가까운" if h == "near" else "먼"} 손)' for k, h in held) or '없음'
    wang_txt = ' '.join(f'{fr}:{w["deg"]:.0f}' for fr, w in wang)
    colours = []
    if geo.get('tint'):
        o, a = geo['tint'].get('outfit', []), geo['tint'].get('accent', [])
        colours.append(f'KEY COLOURS (the engine recolours them per faction): the uniform cloth uses ONLY the exact sheet keys '
                       f'{" ".join(o)} (outfit) and the trim ONLY {" ".join(a)} (accent), on the SAME areas as in the sheet.')
    elif item.get('colors'):
        cs = '; '.join(f'{k} {v}' for k, v in item['colors'].items())
        colours.append(f'COLOURS: take every colour from the accepted sheet (same palette, ~40 colours); the design colours were {cs}.')
    if item.get('spots'):
        colours.append(f'SPOT COLOURS (tiny must-show colours, keep them exactly): {", ".join(item["spots"])}.')
    move_word = 'RUN' if cls == 'light' else ('HEAVY TRUDGE (fast, purposeful)' if cls == 'heavy' else 'ROBE GLIDE (hurried, purposeful)')
    fmt_lines = [f'  - the hip centre of every frame on the slot\'s column x={HIP_X} (the body stays in place, the feet move);']
    if flight:
        fmt_lines += [f'  - {" ".join(f["frame"] for f in frames if f.get("phase") != "flight")}: the sole of the standing foot on '
                      f'y={FLOOR_Y} (lowest pixel), the other foot well above it;',
                      f'  - {" / ".join(flight)} (FLIGHT): NOTHING touches y={FLOOR_Y} - the lowest pixel of the whole figure (boots, '
                      'weapon, cloth) at or above y=852;']
    else:
        fmt_lines += [f'  - EVERY frame: the lowest pixel of the figure is the standing sole on y={FLOOR_Y} (no flight frame);']
    fmt_lines += ['  - every pixel of a frame between x=32 and x=351 of its slot (at least 32 px of magenta to the slot edges - '
                  'nothing may cross into the next slot, including weapons, cloth and hair);',
                  f'  - the SCALE of the accepted sheet ({sc:g} source -> game: the idle is {geo["game_idle_h"]} game px tall); the '
                  f'mannequin is fitted to the idle (the same height and limb lengths), its head top near y={min(tops)}-{max(tops)}.']
    receive = f'python3 tools/art/receive.py gait/{stem}_run'
    notes_h = f'## gait/{stem}_run - {name} 이동'
    refs_list = [f'guide_{p}_a/b', f'guide_{p}_plain_a/b', f'size_{p}_a/b', f'preview_{p}.gif', os.path.basename(geo['source'])] \
        + [os.path.basename(r) for r, _ in refs_pkg] + ['pose.json']
    pnotes = pz.get('notes') or []
    pnotes_ko = pz.get('notes_ko') or []
    lines = [
        f'# {title} · `{sid}` → `gait/{stem}_run`',
        '',
        f'**상태: 요청 ({date}, 클라우드 — `python3 tools/art/gait_requests.py --write {sid} --guides 3d` 로 만듦; 3D 마네킹 시범).** '
        'Antigravity 가 이 README 하나와 아래 그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` '
        '「Rules changed」가 우선.',
        '',
        f'**왜**: {OWNER_3D_KO}',
        f'→ 이 폴더의 가이드는 부류 공용 2D 마네킹이 아니라 **이 캐릭터의 승인된 대기 그림에 맞춘 3D 마네킹**(`tools/mannequin3d`, '
        f'`tools/mannequin3d/specs/carry3d.json` 의 `{geo["m3d"]["key"]}`)이 {ko_cls}({cls}) 달리기를 하는 8프레임이다. 그 위에 캐릭터를 '
        '프레임마다 덧그리고, 마네킹 픽셀은 하나도 남기지 않는다.',
        f'그려 온 띠는 `tools/art/add_gait.py` 가 시트 아래에 `anims.run` 칸으로 붙이고, 엔진(`js/battle.js`)이 {ms}ms 박자로 넘긴다'
        f'{" (뜬 칸 포함)" if flight else ""}. 보폭·박자·디딘 발 규칙은 {ko_cls} 부류 그대로다 (엔진의 runCells).',
        '',
        '| 파일 | 내용 |',
        '|---|---|',
        f'| `guide_{p}_a.png` / `guide_{p}_b.png` | **자세·자리·깊이 가이드** = 3D 마네킹 {frames[0]["frame"]}~{frames[3]["frame"]} / '
        f'{frames[4]["frame"]}~{frames[7]["frame"]}. 관절 점(SPEC.md 색), 든 무기는 청록 반투명(앞에 몸이 있으면 점선), 무기를 쥔 손에 '
        f'청록 고리. 1536x1024, 384px 칸 4개, 칸마다 엉덩이 열 x=192, 디딘 발바닥 y=870{", " + "·".join(flight) + " 은 공중" if flight else ""} |',
        f'| `guide_{p}_plain_a.png` / `guide_{p}_plain_b.png` | 같은 프레임, 점·고리·바닥 줄 없음 — 밑그림(언더레이)용 |',
        f'| `size_{p}_a.png` / `size_{p}_b.png` | 읽기용: 왼쪽 칸 = 승인된 대기 자세(흐리게, 게임처럼 앵커 열을 x=192 에) 위에 3D 마네킹 '
        f'{frames[0]["frame"]}/{frames[4]["frame"]} 윤곽(하늘색) — **같은 배율**. 오른쪽 4칸 = 가이드 + 바닥 줄·엉덩이 열·x=32/351 선·'
        '디딘 발끝 자리(노란 눈금) |',
        f'| `preview_{p}.gif` / `preview_{p}_game_x4.gif` | 움직임 미리보기: 가이드 크기 / 게임 크기 x4, {ms}ms 박자 |',
        f'| `pose.json` | 이 요청의 좌표·보폭·관절(시트 배율 {sc:g}, `mannequin3d` 표시 + 검사 결과). `add_gait.py --pose` 에 쓴다 |',
        *[f'| `{r}` | {"승인된 초상화 — 얼굴·머리·색" if "portrait" in r else "디자인 초안 — 디자인만"} |' for r, _ in refs_pkg],
        f'| `{geo["source"]}` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |',
        '',
        f'- 부류: **{ko_cls}** — {(spec["sheets"].get(sid) or {}).get("why", "")} ({SPEC}). 개성은 그 위에 얹는다 (아래 「개성」).',
        f'- 납품: art-inbox `{dl[0]}` ({frames[0]["frame"]}~{frames[3]["frame"]}) + `{dl[1]}` ({frames[4]["frame"]}~{frames[7]["frame"]}) + '
        f'`art/inbox/NOTES.md` 절 「{notes_h[3:]}」 + 「## 판정 — gait/{stem}_run」. 파일 이름은 부류와 상관없이 `_run_` (엔진의 `anims.run`).',
        f'- 무기: {held_txt} — 아래팔에 대한 손목 각도 {wmin:g}~{wmax:g}도 안 (가이드: {wang_txt}).',
        f'- 디딘 발: 한 걸음 원본 {step:g}px(게임 {step * sc:.1f}px) → 디딘 발은 칸마다 **정확히 {q:.1f}px**(±3, 게임 {q * sc:.1f}px) 뒤로 — 발끝 x 는 '
        'Prompt 의 PLANTED FOOT 표.',
        f'- 클라우드가 받은 뒤: `{receive}` (검사 + `add_gait.py --dry-run`) → 미리보기를 주인께 보이고, 붙이는 것은 `add_gait.py` '
        f'(`--pose {geo["pose"]}`). 그림이 좋은지는 주인이 직접 판정한다.',
        '',
        '## 3D 가이드 읽는 법',
        '',
        '- **명암 = 깊이**: 밝은 부분이 보는 사람에게 **가깝고**, 어두운 부분이 **멀다** (가까운 팔·다리는 밝은 베이지, 먼 팔·다리는 '
        '어두운 회청색). 덧그릴 때 이 앞뒤 순서를 지킨다 — **가까운 쪽이 먼 쪽 위에** 그려진다. 무기·몸·얼굴이 겹쳐도 그 순서만 맞으면 괜찮다.',
        '- **청록 반투명 = 든 무기**: 실선 윤곽은 무기가 앞에 있는 곳, 점선은 몸이 무기 앞을 가리는 곳. 무기는 대기 그림의 **실제 크기·모양**'
        '으로 그 선을 따라 그린다 (가이드의 길이는 자리 표시).',
        f'- **손목 범위**: 무기 방향은 아래팔(팔꿈치→손목) 선에서 위쪽(엄지 쪽)으로 {wmin:g}~{wmax:g}도 안. 0 = 팔과 일직선. 그 밖으로 꺾어 '
        '늘어뜨리지 않는다 (덜렁거리는 칼 금지). 위로 들든 아래로 내리든 이 범위 안이면 된다.',
        '- **바닥**: 디딘 발바닥은 y=870, 공중 프레임은 y=852 위. 무기 끝·천 같은 소품이 바닥 줄 아래로 내려가면 그릴 때 손본다 '
        '(각도를 조금 바꿔 올린다) — 몸과 발의 바닥 규칙은 그대로.',
        '- **마네킹 픽셀은 전부 덮는다**: 3D 마네킹의 색이 한 프레임의 25% 이상 남거나, 실루엣이 가이드와 거의 같으면(색만 바꾼 마네킹, '
        'IoU > 0.93) `add_gait.py` 가 받지 않는다. 마네킹 머리는 자리 표시 — 캐릭터의 머리·머리카락·머리띠를 대기 그림 크기로 그린다.',
        '- 견본(다른 캐릭터의 달리기)은 기준선일 뿐 — 이 캐릭터의 움직임은 아래 개성대로. 색만 바꾼 다른 캐릭터의 띠는 받지 않는다.',
        '',
        '## 개성',
        '',
        *[f'- {s}' for s in pnotes_ko],
        '',
        '## 요약 (한국어)',
        '',
        f'{name}의 {ko_cls} 달리기 8프레임(R1~R8)을 이 폴더의 3D 마네킹 가이드 위에 덧그려 `{dl[0]}`·`{dl[1]}` 두 띠로 art-inbox 에 올린다. '
        f'모습 — {look_ko or "승인된 시트의 대기 그림 그대로 (carry3d.json request.look_ko 없음)"} '
        '명암은 깊이(밝음 = 가까움)이고 그 앞뒤 순서를 지킨다. 무기 손목은 아래팔 기준 '
        f'{wmin:g}~{wmax:g}도 안. 바닥 아래 소품은 손본다. 마네킹 픽셀은 하나도 남기지 않는다. 디딘 발은 칸마다 {q:.1f}px 뒤로 '
        '(발끝 x 는 PLANTED FOOT 표). 끝나면 NOTES.md 에 절과 「판정」 절을 적고 멈춘다. 그림이 좋은지는 주인이 직접 본다.',
    ]
    P = [
        f'TASK: draw the {move_word} CYCLE (8 frames, movement class {cls.upper()}) of {name} as TWO new PNG strips on the '
        'art-inbox branch:',
        f'  {dl[0]}  = frames {fa}',
        f'  {dl[1]}  = frames {fb}',
        '(the file names say "run" for every movement class: the engine plays them as the sheet\'s run.)',
        'PAINT the character OVER this folder\'s 3D MANNEQUIN, frame by frame. The mannequin is fitted to the accepted idle (same',
        'height, limb lengths and stance width) and already moves with this character\'s personality - copy its pose, depth and',
        'placement; do not take the idle art and bend, shear or rotate it.',
        '',
        'REFERENCES (load all; if the sheet or a guide does not load, do not draw - write "## 막힘" in NOTES.md and stop):',
        f'  - {reqdir}/guide_{p}_a.png, guide_{p}_b.png = THE POSE, PLACEMENT AND DEPTH GUIDE for every frame (joint dots, the',
        '    held weapon as a teal see-through ghost, a teal ring on the hand that holds it; same canvas as your delivery:',
        '    1536x1024, 4 frames per strip in 384-px slots).',
        f'  - {reqdir}/guide_{p}_plain_a.png, guide_{p}_plain_b.png = the same frames without dots / rings / ground line: open',
        '    them as an UNDERLAY and paint on your own layers - the delivered PNGs contain ONLY your painting.',
        f'  - {reqdir}/size_{p}_a.png, size_{p}_b.png = the same frames with guide lines and planted-toe ticks, and on the left the',
        '    accepted idle (faint) with the mannequin outline on top: the two are the SAME SCALE.',
        f'  - {reqdir}/preview_{p}.gif, preview_{p}_game_x4.gif = the motion at speed ({ms} ms a frame).',
        f'  - {geo["source"]} (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.',
        '    Same character, same pixel size, same palette.',
        *[f'  - {r} = {what}.' for r, what in refs_pkg],
        f'  - {geo["pose"]} = the coordinates of every joint per frame, the stride and the checks the guide passed.',
        '',
        f'CHARACTER (unchanged from the accepted sheet): {look}',
        '',
        'HOW TO READ THE 3D GUIDE:',
        '  - SHADING = DEPTH: lighter parts are NEARER the viewer, darker parts are FARTHER (near arm / near leg light beige, far',
        '    arm / far leg dark slate). KEEP THAT DEPTH ORDER when you paint: the nearer part is always drawn over the farther one.',
        '    Weapon, body and face may overlap - that is fine as long as the nearer part is on top.',
        '  - The teal see-through shape is the held weapon: a solid outline where it is in front, dashed where a body part covers',
        '    it. Paint the character\'s OWN weapon at its idle size and shape along that line (the ghost only marks the line).',
        f'  - WRIST RANGE (owner rule): every held weapon points {wmin:g}-{wmax:g} deg UPWARD (thumb side) from the forearm line',
        '    (elbow -> wrist); 0 = straight along the forearm. Up or down on screen does not matter, but never bend it past the',
        f'    arm line (no dangling blade) nor beyond {wmax:g} deg. The guide is inside the range in every frame ({wang_txt} deg).',
        '  - The mannequin\'s round head is a placeholder: paint the character\'s own head, hair and headgear at the idle\'s size on',
        '    its neck. The joints, limbs and torso are fitted to the idle - put the character\'s own body exactly on them.',
        '  - PAINT OVER EVERY MANNEQUIN PIXEL. add_gait.py refuses a strip in which >= 25% of a frame still has the mannequin\'s',
        '    colours, and a recoloured mannequin (silhouette IoU > 0.93 with this guide). Clothing, hair, cloth and the real',
        '    weapon change the silhouette - that is the work.',
        f'  - FLOOR: the standing sole on y={FLOOR_Y}; nothing of the body below it. A weapon tip or cloth that would dip below the',
        '    floor line (or below y=852 in a flight frame) is touched up while painting - lift it a little.',
        '  - Samples of other characters are only baselines. Do not recolour another character\'s strip.',
        '',
        f'THE MOVE (movement class {cls}: {clsd["summary"]} - with this character\'s personality on top, already in the mannequin):',
        f'  - {frames[0]["frame"]} contact - {frames[1]["frame"]} catch (lowest hips) - {frames[2]["frame"]} push-off (heel up) - '
        f'{frames[3]["frame"]} {"FLIGHT (both feet off the ground)" if frames[3].get("phase") == "flight" else frames[3].get("phase")}. '
        f'{frames[4]["frame"]}-{frames[7]["frame"]} = the same with the far foot.',
        f'  - Lean forward (hip to neck): {lean} deg.',
        f'  - Height: the mannequin\'s head top is at y={"/".join(str(t) for t in tops[:4])} in {fa}'
        + (f' (the same in {fb})' if tops[:4] == tops[4:] else f' and {"/".join(str(t) for t in tops[4:])} in {fb}')
        + f': {dtop} px from {frames[0]["frame"]} (+ = lower) - move your head top by the same amounts (bob {bob} px).',
        stride_line(pose, sc),
        '  - PLANTED FOOT: a foot on the floor never slides in the drawing. From its contact frame on, the SAME boot moves LEFT by',
        f'    exactly step/4 = {q:.1f} px per frame (the mannequin: {rmin:.1f}-{rmax:.1f} px; tolerance 3 px) - the engine moves the unit',
        f'    {q * sc:.1f} game px per frame, so the boot stays still on the ground. Toe tip = the FRONT-MOST pixel of the planted boot',
        '    = the yellow tick in size_*.png; x in the 384-px slot:',
        *toe_lines(pose),
        *([f'      ({" / ".join(flight)}: flight - no foot on the floor; the next contact lands ahead again)'] if flight else []),
        '',
        'PERSONALITY (this character\'s own run):',
        *[f'  - {s}' for s in pnotes],
        '  - Face: exactly as in the idle in every frame.',
        '',
        'MUST NOT CHANGE: outfit, colours, proportions, headgear, weapon shape and size, and the SCALE of the accepted sheet. The',
        'body must not be shrunk to fit - change a weapon\'s angle (inside the wrist range) instead.',
        *colours,
        '',
        'FORMAT (each strip): 1536x1024 PNG, 4 frames in ONE row, frame n in the 384-px slot n (x = 384*(n-1) .. 384*n-1), facing RIGHT,',
        f'front three-quarter view, light from the upper left, exactly the placement of guide_{p}_a/b.png:',
        *fmt_lines,
        'STYLE: crisp pixel art like the accepted sheet - about 40 colours, hard pixel edges, no anti-aliasing into the background.',
        'BACKGROUND: perfectly flat #FF00FF. Every figure colour at RGB distance >= 170 from #FF00FF (hard minimum 150).',
        'NO effects: no dust, speed lines, motion blur, afterimages, shadows, floor, text, joint dots or guide lines in the delivery.',
        '',
        'SELF-CHECK (repository root; on Windows without Python: uv run --no-project --with pillow --with numpy python ...):',
        *[f'  {cmd}' for cmd in checks],
        ('The first two must print RESULT: PASS (with --flight-slots 4: slot 4 is the flight frame). '
         if flight else 'The first two must print RESULT: PASS. ')
        + 'The third must end without an error and write',
        f'{work}/{stem}_preview_x4.png and {stem}_run_x4.gif - LOOK at them (the bottom two rows of the preview are your 8 frames at',
        '4x game size) and at the GIF at game speed: the character must look like its idle self moving, not squashed or shrunk; the',
        'planted boot must not slide. (add_gait refuses mannequin pixels: the frames must be your painting.)',
        '',
        'DELIVERY: commit only the two PNGs under art/inbox/gait/ and add to art/inbox/NOTES.md:',
        f'  {notes_h}',
        '  CHECK: the RESULT lines of both check_delivery.py runs and the last lines of add_gait.py --dry-run, verbatim (or "not run")',
        f'  REFERENCES LOADED: {", ".join(refs_list)} -> ok / FAILED (reason)',
        '  CHANGED: what you painted, frame by frame where it matters (planted toe x per frame as you measured it)',
        '  DEVIATIONS: (a) from the 3D mannequin pose / position / depth order per frame (b) from the sheet design (c) from the',
        '              PERSONALITY and wrist-range lines - write "none" explicitly for each',
        '  RISKS AT GAME SIZE: what you could not verify at ~64 px',
        '  3D GUIDE: what helped, what was unclear (shading, ghost weapon, plain underlay) - this is the first 3D-mannequin request',
        f'  ## 판정 — gait/{stem}_run',
        '  결과: 통과 | 고침 | 다시   (your own verdict as animation head: natural? in character? does the contact frame read?)',
        '  본 방법: (game 1x/4x, the preview GIF, frames - what you looked at)',
        '  고칠 점: (who - Antigravity/cloud - what, with frame numbers; "없음" if it passes)',
        '  남은 걱정: (what the owner\'s look should check; "없음" if none)',
        '  캐릭터 메모: (direction for this character\'s next motions; omit if none)',
        'The owner judges the result himself. Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.',
    ]
    lines += ['', '## Prompt for Antigravity', '', '```', *P, '```', '']
    with open(os.path.join(folder, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return rel_folder, True, geo, checks


def check_request_3d(name, folder, sid, text, sc):
    """--check 의 3D 요청 폴더 몫: 표시·carry3d 항목·가이드 해시·파일 (tools/mannequin3d/request.py verify) + README 의 --pose·보폭·발끝"""
    errs = [f'{name}: {e}' for e in m3d_module().verify(folder, sid)]
    local = os.path.join(folder, 'pose.json')
    try:
        pose = load(local)
    except (OSError, ValueError):
        return errs
    expected_path = rel(local)
    poses = re.findall(r"""--pose\s+["']?([^\s`"'<>]+)""", text)
    if not poses or any(p_ != expected_path for p_ in poses):
        errs.append(f'{name}/README.md: 3D 마네킹 {expected_path} 를 가리키지 않는다 — --write {sid} --guides 3d --force')
    actual = [line.strip() for line in text.splitlines()
              if line.lstrip().startswith(('- Stride:', 'near foot:', 'far foot:'))]
    if actual != [stride_line(pose, sc).strip(), *(line.strip() for line in toe_lines(pose))]:
        errs.append(f'{name}/README.md: 보폭 또는 디딤 발끝 숫자가 pose.json 과 다르다')
    for m2 in re.finditer(r'the guide (bow|spear|lance|sword|staff|mace|blade|draws)|as long as the guide', text):
        errs.append(f'{name}/README.md: 「{m2.group(0)}」 - 「the idle」 기준으로 바꿀 것')
    return errs


INDEX_HDR = ['| 요청 | 시트 | 부류 · 마네킹 | 납품 (art-inbox) | 상태 |', '|---|---|---|---|---|']


def index_rows(spec=None, man=None):
    """art/requests/gait/*__*/README.md 에서 목록 줄을 만든다 (상태는 시트의 그려진 run 칸)"""
    spec = spec or load(SPEC)
    man = man or load(MANIFEST)
    st = {r['sheet']: r for r in status(spec, man)}
    rows = []
    for d in sorted(glob.glob(os.path.join(ROOT, 'art', 'requests', 'gait', '*__*', 'README.md'))):
        head = open(d, encoding='utf-8').readline().strip()
        m = re.match(r'#\s*(.+?)\s*·\s*`(sheet/[^`]+)`', head)
        if not m:
            continue
        title, sid = m.group(1), m.group(2)
        r = st.get(sid, {})
        cls = r.get('class') or '?'
        g = os.path.dirname(r.get('guide') or '') or '?'
        mq = f'3D 마네킹 `{g}/`' if is_3d_folder(os.path.dirname(d)) else f'`{g}`'
        stem = r.get('stem', '')
        if r.get('state') == 'done':
            state = '그려짐 · 등록'
        elif r.get('state') == 'redraw':
            state = f'다시 (지금 칸은 {r.get("drawn")})'
        else:
            state = '요청'
        folder = os.path.basename(os.path.dirname(d))
        rows.append(f'| [`{folder}/`]({folder}/README.md) | `{sid}` {title} | {KO.get(cls, cls)} · {mq} | '
                    f'`art/inbox/gait/{stem}_run_a.png` + `_b.png` | {state} |')
    return rows


def write_index():
    p = os.path.join(ROOT, 'art', 'requests', 'gait', 'README.md')
    text = open(p, encoding='utf-8').read()
    if INDEX_START not in text or INDEX_END not in text:
        raise SystemExit(f'{rel(p)}: 목록 표시 줄({INDEX_START} … {INDEX_END})이 없다')
    a, rest = text.split(INDEX_START, 1)
    _, b = rest.split(INDEX_END, 1)
    rows = index_rows()
    new = a + INDEX_START + '\n' + '\n'.join(INDEX_HDR + rows) + '\n' + INDEX_END + b
    if new != text:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(new)
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--js', action='store_true', help=f'{JS_OUT} 를 다시 만든다')
    ap.add_argument('--check', action='store_true', help='표·분류 검사 (다르면 종료 코드 1)')
    ap.add_argument('--json', action='store_true', help='현황을 JSON 으로')
    ap.add_argument('--all', action='store_true', help='다 그려진 시트와 none 도 보여 준다')
    ap.add_argument('--write', nargs='+', metavar='SHEET', help='요청 폴더를 만든다 (시트 id, png 이름 또는 class_archer 같은 짧은 이름)')
    ap.add_argument('--force', action='store_true', help='--write: 이미 있는 요청 폴더도 다시 만든다')
    ap.add_argument('--out', help='--write: 이 폴더에 쓴다 (시트 하나, 시험용 — 목록은 고치지 않는다)')
    ap.add_argument('--date', default=datetime.date.today().isoformat(), help='--write: README 의 요청 날짜 (기본 오늘)')
    ap.add_argument('--index', action='store_true', help='art/requests/gait/README.md 의 요청 목록만 다시 쓴다')
    ap.add_argument('--guides', choices=('2d', '3d'),
                    help='--write: 2d = 부류 확정 마네킹 띠 / 3d = 캐릭터에 맞춘 3D 마네킹 (tools/mannequin3d, carry3d.json 항목 필요). '
                         '기본: 이미 3D 로 만든 폴더는 3d, 나머지는 2d')
    a = ap.parse_args()
    spec, man = load(SPEC), load(MANIFEST)
    if a.write:
        if a.out and len(a.write) > 1:
            print('--out 은 시트 하나만', file=sys.stderr)
            return 2
        sys.path.insert(0, os.path.join(ROOT, 'tools', 'art'))
        import run_request_guides as rg
        rc = 0
        for s in a.write:
            try:
                folder, from_table, geo, checks = write_request(s, os.path.abspath(a.out) if a.out else None, a.force, a.date, spec, man,
                                                                 a.guides)
            except rg.Fail as e:
                print(f'FAIL {s}: {e}', file=sys.stderr)
                rc = 1
                continue
            print(f'{geo["sheet"]} [{geo["cls"]}{" 3D" if geo.get("m3d") else ""}] → {folder}/ README.md {" ".join(geo["files"])}')
            for lv, msg in (geo.get('m3d') or {}).get('checks', []):
                print(f'   3D [{lv}] {msg}')
            print(f'   대기 x {geo["idle_x"][0]}-{geo["idle_x"][1]}, 앵커 열 {geo["anchor_col"]}, 배율 {geo["scale"]} ({geo["scale_src"]}; '
                  f'등록된 대기 높이로 {geo["scale_registered"]}), 마네킹 {geo["pose"]}')
            if not from_table:
                print('   검토: CARRY 표에 없는 시트 — 손에 든 것·천 문장이 부류 기본값이다. 읽고 CARRY 에 적은 뒤 --force 로 다시')
            for cmd in checks:
                print(f'   SELF-CHECK  {cmd}')
        if not a.out:
            print(f'art/requests/gait/README.md 목록 {write_index()} 줄')
        return rc
    if a.index:
        print(f'art/requests/gait/README.md 목록 {write_index()} 줄')
        return 0
    if a.js:
        with open(os.path.join(ROOT, JS_OUT), 'w', encoding='utf-8') as f:
            f.write(js_table(spec))
        print(f'{JS_OUT} 를 썼다 ({len(spec["sheets"])} 시트 + 대기 {len(spec.get("pending_packages") or {})})')
        return 0
    if a.check:
        errs = check(spec, man)
        rq = check_requests(spec, man)
        errs += rq
        for e in errs:
            print('FAIL', e)
        nreq = len(glob.glob(os.path.join(ROOT, 'art', 'requests', 'gait', '*__*', 'README.md')))
        print('RESULT:', 'FAIL' if errs else 'PASS', f'({len(spec["sheets"])} 시트 분류, {JS_OUT} 동기, 이동 요청 폴더 {nreq})')
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
