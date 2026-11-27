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


PATH_RE = re.compile(r'(?<![\w/])((?:art|tools|assets|docs|js)/[\w./-]+\.(?:png|json|gif|aseprite|md|py|jpg|js))')


def check_requests(spec, man):
    """art/requests/gait/*__*/: 머리 줄의 시트가 등록·분류되어 있고, README 가 가리키는 파일이 있고(납품 art/inbox/gait/ 는 빼고),
    --write 로 만든 폴더는 guide_<p>_a/b.png 가 지금 부류 마네킹 띠와 바이트까지 같고 size_<p>_a/b.png 가 있는지 본다."""
    import filecmp
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
        g, _ = guide_of(cls, spec)
        pose = load(g)
        sheet_scale = phase3_item(sid).get('scale')
        if not sheet_scale:
            from run_request_guides import geometry
            sheet_scale = geometry(sid, man)['scale']
        scaled = abs(sheet_scale / pose['scale'] - 1) > 0.01
        local = os.path.join(folder, 'pose.json')
        if scaled:
            from run_request_guides import scale_pose, scale_strip
            expected = scale_pose(g, pose, sheet_scale)
            if not os.path.isfile(local) or load(local) != expected:
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
                    matches = np.array_equal(np.asarray(Image.open(gp).convert('RGB')),
                                             scale_strip(original, pose['scale'] / sheet_scale))
                else:
                    matches = filecmp.cmp(gp, src, shallow=False)
            if not matches:
                errs.append(f'{name}: guide_{REQ_PREFIX[cls]}_{h}.png 가 {rel(src)} 와 다르다 — gait_requests.py --write {sid} --force')
            if not os.path.exists(os.path.join(folder, f'size_{REQ_PREFIX[cls]}_{h}.png')):
                errs.append(f'{name}: size_{REQ_PREFIX[cls]}_{h}.png 가 없다')
        for m2 in re.finditer(r'the guide (bow|spear|lance|sword|staff|mace|blade|draws)|as long as the guide', text):
            errs.append(f'{name}/README.md: 「{m2.group(0)}」 - phase3 CHARACTER 줄을 그대로 옮긴 말이다. 이 요청에는 무기 가이드가 없으니 「the idle」 기준으로 바꿀 것')
        expected_path = rel(local) if scaled else g
        if f'--pose {expected_path}' not in text:
            errs.append(f'{name}/README.md: 마네킹 {expected_path} 를 가리키지 않는다 — --force 로 다시 만들 것')
    return errs


# ───────── --write: 요청 폴더 만들기 ─────────
# 캐릭터가 이동하는 동안 손에 든 것·천·얼굴 (phase3 꾸러미 README 의 CHARACTER 줄과 승인된 대기 그림을 보고 적었다).
# title = 한국어 제목, name = 프롬프트의 이름, character = 영어 CHARACTER, carry = ARMS AND WEAPONS 줄들, cloth = 천·머리의 늦음,
# face = 얼굴, ko = 한국어 머리말의 팔·무기 요약, refs = 꾸러미에서 더 넣을 참고 그림 (concept 는 늘 넣는다).
CARRY = {
    'sheet/captain/frostjarl': {
        'title': '비요른 달리기', 'name': '비요른', 'refs': ['portrait.png'],
        'character': 'Bjorn: blond frost jarl with two front braids, blond beard, slate-blue armoured tunic, snowflake '
                     'pauldron, pale fur mantle and fur-trimmed boots. Copy the long-hafted bearded axe and its two-handed '
                     'grip from the accepted idle.',
        'carry': [
            'Keep both hands on the axe: near right hand lower by the hip, far left hand higher toward the head. '
            'The mannequin\'s two separate arm swings do NOT apply to this character (intended, not a deviation). '
            'Keep the lower grip at x=198–228 and y=640–675 in each slot (at most 30 px fore-aft). The axe head spans '
            'about 245 px from that grip to its top. Carry the shaft forward and up at 70–80 deg above horizontal; '
            'the projected upper end stays left of x=312 before the blade width. Keep the outer edge inside x=351 '
            'and the butt above y=852 (no planted axe, no swing).',
        ],
        'cloth': [
            'Both gold-bound braids stay over the FRONT of the chest and bounce lightly. Keep the fur mantle across '
            'the shoulders; small trailing locks and the rear tunic hem settle one frame late. Leave the thighs and boots free.',
        ],
        'face': 'Face and beard: exactly as in the accepted idle.',
        'ko': '양손 도끼는 아래 손을 x=198–228에 두고 위쪽으로 70–80° 세운다. 앞머리 두 갈래는 가슴 앞에 남긴다.',
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


def write_request(sid, out=None, force=False, date=None, spec=None, man=None):
    """요청 폴더 하나 → (폴더 rel, CARRY 표에서 왔는가)"""
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
              f'python3 tools/art/add_gait.py {sid} --gait run --src {dl[0]} {dl[1]} --pose {geo["pose"]} --dry-run --work {work}']
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
    toe_lines = []
    for leg, seq, rear in rows:
        s = ' -> '.join(f'{fr} x={fmt_x(x)}' for fr, x in seq)
        if rear:
            s += f'  (-> {rear[0]} x={fmt_x(rear[1])} as the REAR foot, heel up, toe still on the floor)'
        toe_lines.append(f'      {leg} foot: {s}')
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
                  f'tall); the figure about as tall as the idle stood up (the mannequin\'s head top is near y={min(tops)}-{max(tops)}).']
    receive = f'python3 tools/art/receive.py gait/{stem}_run'
    notes_h = f'## gait/{stem}_run - {c["title"]}'
    refs_list = [f'guide_{p}_a/b', f'size_{p}_a/b', f'{stem}.png'] + [os.path.basename(r) for r, _ in refs_pkg] + ['pose.json']
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
    ko_files.append(f'| `art/inbox/{stem}.png` | **승인된 전투 시트 원본** — 디자인·색·크기의 기준. 1번 자세가 대기 |')
    ko_files.append(f'| `{gdir}/` (`pose.json`, `{pose["set"]}_preview.gif`, `{pose["set"]}.aseprite`) | 마네킹 원본 — 숫자·움직임 확인용 |')
    lines = [
        f'# {c["title"]} · `{sid}` → `gait/{stem}_run`',
        '',
        f'**상태: 요청 ({date}, 클라우드 — `python3 tools/art/gait_requests.py --write {sid}` 로 만듦).** Antigravity 가 이 README 하나와 아래 '
        '그림만으로 끝낼 수 있게 적었다. 규칙 충돌 시 `art/requests/gpt_handoff_notes.md` 「Rules changed」가 우선.',
        '',
        f'**왜 (주인 2026-11-26)**: {WHY_KO}',
        f'→ 대기 그림을 잘라 기울이고 구부리는 코드 이동은 쓰지 않는다. **이동 부류 {ko_cls}({cls})의 확정 마네킹(`{gdir}/`) 8프레임 위에 '
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
        f'  - art/inbox/{stem}.png (pose 1 = idle) = the accepted battle sheet: design, colours, outline, rendering and SIZE.',
        '    Same character, same pixel size, same palette.',
        *[f'  - {r} = {what}.' for r, what in refs_pkg],
        f'  - {geo["pose"]} (the numbers below come from it), {gif} (the motion at speed), {ase} (the mannequin source -',
        '    you may open it as an underlay and draw on your own layers, but the delivered PNGs contain ONLY your drawing).',
        '',
        f'CHARACTER (unchanged from the accepted sheet): {c["character"]}',
        '',
        f'THE MOVE (owner\'s three movement classes; {cls}: {clsd["summary"]} It is already in the mannequin - copy it, do not invent another):',
        '  - Each frame: the legs, the torso lean and the arm swing of that mannequin frame. Joint for joint: hips, knees, ankles, feet,',
        '    shoulders, elbows (hands: see ARMS - where the text moves a hand, that is intended, not a deviation).',
        '    The mannequin\'s big round head is a placeholder: draw the character\'s own head on the mannequin\'s neck, at its own size',
        '    (as in the sheet).',
        *phase_lines,
        f'  - Lean forward (hip to neck): {lean} deg.',
        (f'  - Height: the mannequin\'s head top is at y={"/".join(str(t) for t in tops[:4])} in {fa} (the same in {fb}): '
         if tops[:4] == tops[4:] else
         f'  - Height: the mannequin\'s head top is at y={"/".join(str(t) for t in tops[:4])} in {fa} and '
         f'{"/".join(str(t) for t in tops[4:])} in {fb}: ')
        + f'{dtop} px from {frames[0]["frame"]} (+ = lower) - move your head top by the same amounts (bob {bob} px).',
        f'  - Stride: one step = {step:g} source px = {step * sc:.1f} game px; 8 frames = two steps, {ms} ms a frame in the game.',
        f'  - PLANTED FOOT (the rule the class warrior\'s R5 needed a fix for): a foot on the floor never slides in the drawing. From its',
        f'    contact frame on, the SAME boot moves LEFT by exactly step/4 = {q:.1f} px per frame (the mannequin: {rmin:.0f}-{rmax:.0f} px;',
        f'    tolerance 3 px) - the engine moves the unit {q * sc:.1f} game px per frame, so the boot stays still on the ground.',
        '    Toe tip of the planted boot = its FRONT-MOST pixel (the toe; on a tapered boot it may sit a few px above y=870, as on the '
        '    mannequin) = the yellow tick in size_*.png; x in the 384-px slot:',
        *toe_lines,
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
        stem = r.get('stem', '')
        if r.get('state') == 'done':
            state = '그려짐 · 등록'
        elif r.get('state') == 'redraw':
            state = f'다시 (지금 칸은 {r.get("drawn")})'
        else:
            state = '요청'
        folder = os.path.basename(os.path.dirname(d))
        rows.append(f'| [`{folder}/`]({folder}/README.md) | `{sid}` {title} | {KO.get(cls, cls)} · `{g}` | '
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
                folder, from_table, geo, checks = write_request(s, os.path.abspath(a.out) if a.out else None, a.force, a.date, spec, man)
            except rg.Fail as e:
                print(f'FAIL {s}: {e}', file=sys.stderr)
                rc = 1
                continue
            print(f'{geo["sheet"]} [{geo["cls"]}] → {folder}/ README.md {" ".join(geo["files"])}')
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
