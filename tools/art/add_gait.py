#!/usr/bin/env python3
"""그려 온 이동 프레임(달리기 run · 걷기 walk)을 이미 등록된 전투 시트에 붙인다.

  python3 tools/art/add_gait.py <시트 id | 시트 png 이름> --gait run|walk
        --src <a.png> <b.png> | --src <파일.aseprite>
        [--stride 게임px | --pose pose.json] [--ms N] [--floor 870] [--center 192] [--scale S]
        [--dry-run --work DIR] [--allow-draft] [--aseprite-bin EXE] [--extra-guides DIR]
  python3 tools/art/add_gait.py <시트> --gait run|walk --remove [--dry-run --work DIR]
  python3 tools/art/add_gait.py <시트> --reattach        # register_sheet.py 가 다시 등록한 뒤 부른다 (손으로 불러도 된다)

  예: python3 tools/art/add_gait.py sheet/class/warrior --gait run \\
          --src art/inbox/gait/sheet_class_warrior_run_a.png art/inbox/gait/sheet_class_warrior_run_b.png \\
          --pose art/requests/guides/run_base/v1/pose.json

원본 (art/requests/guides/SPEC.md 2·3절의 프레임 규격):
  - 띠 png: 한 프레임 384x1024 를 나란히 (<set>_a.png = 1~4번, <set>_b.png = 5~8번), 배경 #FF00FF
  - 또는 프레임마다 384x1024 인 .aseprite 하나 (보이는 레이어만 쓴다 — 숨긴 joints 레이어는 빠진다; Aseprite 실행 파일 필요)
  모든 프레임에서 엉덩이 중심 열 x=192, 바닥 줄 y=870 (디딘 발의 맨 아래 픽셀) 이 같다.

하는 일:
  - 프레임마다 그 시트를 만들 때와 같은 변환을 한다 — sheets.py 의 함수를 그대로 쓴다 (matte → key_label → shrink_pose → outline →
    paint_pose): 요청서(art/requests/phase3.json)의 scale, 배경 키 제거, BOX 축소·알파 이진화, 열쇠 색(tint)·점 색(spots).
    팔레트는 새로 만들지 않고 등록된 시트의 기본 칸에 실제로 있는 색(열쇠 색·점 색 제외)을 쓴다 — 이동 칸이 기본 칸과 같은 색만 쓴다.
  - 자리 맞춤은 **고정된 바닥 줄과 프레임 가운데 열**: 원본 y=870 의 아랫변 → 칸의 anchor y, 원본 x=192 → anchor x.
    맨 아래 픽셀이나 그림 테두리로 맞추지 않는다 (달리기에는 두 발이 다 뜬 프레임이 있고, 프레임마다 몸이 흔들리면 안 된다).
    모든 프레임이 같은 표본 격자(칸 전체에 해당하는 원본 창)로 줄어든다. 칸에 안 들어가는 프레임은 줄이거나 밀지 않고 몇 px 넘는지 알리고 실패한다.
  - 시트 png 아래에 새 줄로 칸을 붙인다 (기본 칸의 픽셀은 그대로; 이동 칸의 줄은 붙인 순서와 상관없이 run → walk). manifest 항목의 sheet 에:
      frames 에 새 칸의 [x, y], anims.<gait> = {from, to, ms:[...]}, <gait>Stride = 한 걸음에 가는 게임 px (n 프레임 = 두 걸음),
      gaits.<gait> = {src, floor, center, stride, ms[, pose, step_px, class]} — 어디서 온 프레임인지 (다시 붙일 때 쓴다)
  - run 칸이면 시트의 이동 부류 sheet.gait = light | heavy | robe 도 쓴다 (--pose pose.json 의 "gait": run → light, heavy, robe;
    tools/art/specs/gait_classes.json 의 세 부류). 엔진(js/battle.js gaitClassOf)은 meta.gait 를 그 표보다 먼저 본다 — 그린 이동 칸이
    어느 마네킹 위에 그려졌는지가 그 칸을 넘기는 방식(경량: 뜬 칸 / 중량·로브: 디딘 채로)을 정한다. 표와 다르면 주의를 찍는다.
    부류를 모르는 pose(walk) 나 --stride 만 주면 쓰지 않는다 (add_gait 가 전에 쓴 값이면 지운다). --remove 로 run 을 빼면 같이 지운다.
  - --stride 가 없으면 --pose (없으면 원본 옆의 pose.json) 의 step_px x 시트 배율.
  - --remove: 그 이동 칸·anims·Stride·기록을 뺀다 (다른 이동 칸은 남는다. 하나도 안 남으면 시트 png 가 붙이기 전과 같아진다).
  - --dry-run: 시트·manifest 를 건드리지 않고 --work DIR 에 새 png · 등록될 항목(<이름>.entry.json) · 미리보기만 쓴다.

기본 시트를 다시 등록하면 (sheets.py → register_sheet.py): register_sheet.py 가 gaits 기록을 새 항목에 옮기고 이 도구를 --reattach 로 불러
기록된 원본에서 다시 변환해 붙인다. 원본이 없으면 기록은 남기고(anims 는 없다 → 게임은 그 시트의 이동 칸 없이 돈다) 다시 붙일 명령을 크게 알린다.

게임에 들어가는 그림만 받는다: 초안 자리(art/concepts/, art/requests/, drafts/, nai_*)의 파일은 sheets.py 와 같은 규칙으로, 뼈대(마네킹)는
  — 경로에 guides 폴더가 있는 파일(art/inbox/guides/<id>/ 포함), 옆에 pose_measured.json 이 있는 띠(check_skeleton --export), joints 레이어가 있는
  .aseprite, 어느 프레임(또는 좌우로 뒤집은 것)의 실루엣이 뼈대 프레임과 자리를 맞춰(그림 상자의 아래 가운데를 맞추고 x, y ±24px 를 더 찾아)
  IoU 0.85 넘게 겹치는 원본 (joints 레이어를 지운 마네킹, 이름을 바꾸거나 몇 px 옮기거나 뒤집은 마네킹) — 모두 거부한다. 크기를 바꾼
  마네킹도 잡도록 원본 프레임을 뼈대 프레임의 그림 상자 높이로 맞춰(가로세로 비 유지) 한 번 더 잰다 (높이 비 0.5..4 안에서 — 작게 줄여 격자로 넣은 마네킹도).
  기울인 마네킹도 잡도록 그대로 잰 IoU 가 0.5 이상인 짝은 원본을 발바닥 가운데로 ±2도부터 2도씩 ±8도까지 IoU 가 오르는 쪽으로 돌려
  (바닥에 다시 세워; 높이를 맞춰 보는 짝은 돌린 뒤 높이를 맞춰) 더 잰다 (±9도 안의 기울기, 크기를 바꾸고 기울인 것도).
  비교하는 뼈대: 클라우드 초안 art/requests/guides/*/<하위 폴더>/ — v*/ 와 draft/ (heavy_base·robe_base 초안) 등 모두 (띠, 레이어를 합친 것)·
  art/requests/guides/*/ 의 띠, PC 가 넘긴 마네킹
  art/inbox/guides/** 의 .aseprite (내보내 파일 해시로 ~/.cache/pixel-management/guide_masks/ 에 캐시)와 띠 — 작업 트리의 것과
  origin/art-inbox 의 것(git show 로 읽는다: 아직 이 브랜치에 들이지 않은 마네킹도), --extra-guides 폴더. joints 레이어가 보이는 .aseprite 는 --allow-draft 로도 받지 않는다 (관절 점이 찍힌다).
  --allow-draft = 파이프라인 시험용, 언제나 --dry-run.
실패로 끝나는 그림: 384px 프레임의 테두리에 닿는 프레임 (띠가 잘리거나 옆 자세가 넘어온 것 — 프레임 번호를 알린다),
  바닥 줄 아래로 내려가는 프레임 (--allow-below 를 주면 받고 기록에 남긴다), 칸에 들어가지 않는 프레임.
최종 이동 프레임이 들어오는 자리: art/inbox/gait/<시트 png 이름>_<gait>.aseprite 또는 _<gait>_a.png / _<gait>_b.png
  (tools/art/receive.py gait/<시트 png 이름>_<gait> 가 검사하고 이 도구의 --dry-run 까지 돌린다).
필요: Pillow + NumPy (+ .aseprite 원본이면 Aseprite: tools/art/ase_headless.sh)
"""
import argparse
import copy
import glob
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheets as sh  # noqa: E402

ROOT = sh.ROOT
MANIFEST = os.path.join(ROOT, 'assets', 'art', 'manifest.json')
HEADLESS = os.path.join(HERE, 'ase_headless.sh')
SLOT = 384                   # 한 프레임의 너비 (SPEC 2절)
FLOOR = 870                  # 바닥 줄: 디딘 발의 맨 아래 픽셀 (SPEC 3절)
GAITS = ('run', 'walk')
DEFAULT_MS = {'run': 80, 'walk': 120}
POSE_CLASS = {'run': 'light', 'heavy': 'heavy', 'robe': 'robe'}   # pose.json "gait" → 시트의 이동 부류 sheet.gait (run 칸만)
GAIT_CLASSES = os.path.join(ROOT, 'tools', 'art', 'specs', 'gait_classes.json')
ALPHA = 0.45                 # sheets.py --alpha 의 기본값
log = sh.log


class Fail(Exception):
    pass


def rnd(v):
    return int(np.floor(v + 0.5))


def rel(path):
    """저장소 안의 파일은 저장소 기준 경로로 (기록·명령에 쓴다)."""
    p = os.path.abspath(path)
    return os.path.relpath(p, ROOT).replace(os.sep, '/') if p.startswith(ROOT + os.sep) else p


def absp(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


# ───────── manifest ─────────

def load_manifest():
    if not os.path.exists(MANIFEST):
        raise Fail(f'{rel(MANIFEST)} 가 없다')
    with open(MANIFEST, encoding='utf-8') as f:
        return json.load(f)


def save_manifest(man):
    """register_sheet.py 와 같은 모양으로 쓴다."""
    tmp = MANIFEST + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    os.replace(tmp, MANIFEST)


def resolve_sheet(arg, man):
    if isinstance(man.get(arg), dict) and 'sheet' in man[arg]:
        return arg
    stem = os.path.basename(arg)
    stem = stem[:-4] if stem.lower().endswith('.png') else stem
    hits = [k for k, v in man.items() if isinstance(v, dict) and 'sheet' in v and os.path.basename(v['file'])[:-4] == stem]
    if len(hits) != 1:
        raise Fail(f'"{arg}" 에 해당하는 등록된 시트가 {"없다" if not hits else "여럿이다: " + ", ".join(hits)} '
                   '(manifest 의 id — 예: sheet/class/warrior — 또는 png 이름 sheet_class_warrior)')
    return hits[0]


def request_for(sid):
    for it in sh.request_map().values():
        if it.get('id') == sid:
            return it
    return {}


def layout(meta):
    """→ (붙어 있는 이동 칸 이름들 (시트에 놓인 순서), 기본 칸 수). add_gait 가 붙인 칸은 언제나 frames 의 끝에 차례로 있다."""
    recs = meta.get('gaits') or {}
    attached = sorted((g for g in recs if g in meta['anims']), key=lambda g: meta['anims'][g]['from'])
    base_n = min((meta['anims'][g]['from'] for g in attached), default=len(meta['frames']))
    pos = base_n
    for g in attached:
        an = meta['anims'][g]
        if an['from'] != pos or an['to'] < an['from']:
            raise Fail(f'manifest 의 {g} 칸 범위({an["from"]}-{an["to"]})가 기본 칸 뒤에 차례로 있지 않다 — 손으로 고친 항목인가')
        pos = an['to'] + 1
    if pos != len(meta['frames']):
        raise Fail(f'manifest 의 frames 가 {len(meta["frames"])}칸인데 기본 {base_n}칸 + 이동 칸의 끝은 {pos} 이다')
    return attached, base_n


def rebuild(entry, img, blocks):
    """기본 칸(그림 그대로) + blocks {이름: (칸 목록, ms 목록)} 을 차례로 새 줄에 놓은 시트 → (그림, 새 항목).
    stride·기록(gaits)은 부르는 쪽이 채운다."""
    meta = entry['sheet']
    cw, ch = meta['cell']
    attached, base_n = layout(meta)
    base_h = meta['frames'][base_n][1] if attached else img.shape[0]
    W = img.shape[1]
    cols = max(1, W // cw)
    new = copy.deepcopy(entry)
    nm = new['sheet']
    nm['frames'] = [list(r) for r in meta['frames'][:base_n]]
    for g in attached:
        del nm['anims'][g]
    parts, y = [img[:base_h]], base_h
    for g, (cells, ms) in blocks.items():
        rows = -(-len(cells) // cols)
        block = np.zeros((rows * ch, W, 4), np.uint8)
        start = len(nm['frames'])
        for i, c in enumerate(cells):
            x, yy = (i % cols) * cw, (i // cols) * ch
            block[yy:yy + ch, x:x + cw] = c
            nm['frames'].append([x, y + yy])
        nm['anims'][g] = {'from': start, 'to': start + len(cells) - 1, 'ms': [int(v) for v in ms]}
        parts.append(block)
        y += rows * ch
    out = np.concatenate(parts, axis=0)
    new['w'], new['h'] = int(out.shape[1]), int(out.shape[0])
    return out, new


def existing_blocks(entry, img, skip=()):
    meta = entry['sheet']
    cw, ch = meta['cell']
    out = {}
    for g in layout(meta)[0]:
        if g in skip:
            continue
        an = meta['anims'][g]
        out[g] = ([img[y:y + ch, x:x + cw].copy() for x, y in meta['frames'][an['from']:an['to'] + 1]], an['ms'])
    return out


# ───────── 원본 프레임 ─────────

def find_aseprite(given):
    for c in (given, os.environ.get('ASEPRITE_PATH'), HEADLESS if os.path.exists(HEADLESS) else None, sh.find_aseprite(None)):
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def ase_env():
    env = dict(os.environ)
    env.pop('DISPLAY', None)
    env.pop('WAYLAND_DISPLAY', None)
    return env


def ase_layers(path, exe):
    """→ (모든 레이어 이름, 보이는 레이어 이름). 마네킹(뼈대 가이드)인지 가리는 데 쓴다."""
    exe = find_aseprite(exe)
    if not exe:
        raise Fail('.aseprite 원본을 읽을 Aseprite 실행 파일이 없다 (--aseprite-bin / tools/art/ase_headless.sh) — 띠 png 두 장을 --src 로 줄 수도 있다')
    out = []
    for extra in (['--all-layers'], []):
        r = subprocess.run([exe, '--batch', *extra, '--list-layers', os.path.abspath(path)], stdin=subprocess.DEVNULL, capture_output=True,
                           timeout=120, env=ase_env())
        out.append([n.strip() for n in r.stdout.decode('utf-8', 'replace').splitlines() if n.strip()])
    if not out[0]:
        raise Fail(f'Aseprite 가 {path} 의 레이어를 읽지 못했다 — 마네킹(joints 레이어)인지 확인할 수 없어 받지 않는다')
    return out[0], out[1]


def frames_from_aseprite(path, exe):
    exe = find_aseprite(exe)
    if not exe:
        raise Fail('.aseprite 원본을 읽을 Aseprite 실행 파일이 없다 (--aseprite-bin / tools/art/ase_headless.sh) — 띠 png 두 장을 --src 로 줄 수도 있다')
    env = ase_env()
    with tempfile.TemporaryDirectory(prefix='gait-ase-') as tmp:
        png, js = os.path.join(tmp, 'frames.png'), os.path.join(tmp, 'frames.json')
        r = subprocess.run([exe, '--batch', os.path.abspath(path), '--sheet', png, '--data', js, '--format', 'json-array'],
                           stdin=subprocess.DEVNULL, capture_output=True, timeout=300, env=env)
        if r.returncode or not os.path.exists(png) or not os.path.exists(js):
            raise Fail(f'Aseprite 가 {path} 를 내보내지 못했다: ' + (r.stderr or r.stdout).decode('utf-8', 'replace').strip()[-300:])
        with open(js, encoding='utf-8') as f:
            data = json.load(f)['frames']
        arr = np.asarray(Image.open(png).convert('RGBA'))
    frames, durs = [], []
    for i, fr in enumerate(data):
        r = fr['frame']
        if r['w'] != SLOT:
            raise Fail(f'{path}: {i + 1}번 프레임 너비 {r["w"]} — 한 프레임은 {SLOT}px 이어야 한다 (SPEC 2절)')
        frames.append(arr[r['y']:r['y'] + r['h'], r['x']:r['x'] + r['w']].copy())
        durs.append(int(fr.get('duration', 0)) or None)
    return frames, (durs if all(durs) else None)


def load_frames(src, exe):
    """→ (RGBA 프레임 목록 (너비 SLOT), 프레임 시간 ms 목록 또는 None)"""
    for p in src:
        if not os.path.exists(p):
            raise Fail(f'원본이 없다: {p}')
    if any(p.lower().endswith(('.aseprite', '.ase')) for p in src):
        if len(src) != 1:
            raise Fail('.aseprite 원본은 하나만 준다 (프레임이 모두 그 안에 있다)')
        return frames_from_aseprite(src[0], exe)
    frames = []
    for p in src:
        if not p.lower().endswith('.png'):
            raise Fail(f'{p}: 띠 png 또는 .aseprite 만 받는다')
        arr = np.asarray(Image.open(p).convert('RGBA'))
        if arr.shape[1] % SLOT:
            raise Fail(f'{p}: 너비 {arr.shape[1]} 가 한 프레임 {SLOT}px 의 배수가 아니다 (띠 = 384x1024 프레임을 나란히)')
        frames += [arr[:, k * SLOT:(k + 1) * SLOT] for k in range(arr.shape[1] // SLOT)]
    return frames, None


# ───────── 변환 ─────────

def sheet_palette(base, keys, spots):
    """등록된 시트의 기본 칸에 실제로 있는 색 (열쇠 색·점 색 제외) — sheets.py 가 그 시트에 쓴 공통 팔레트 중 쓰인 색."""
    px = base[base[..., 3] > 0][:, :3]
    pal = np.unique(px, axis=0).astype(np.float32)
    for c in list(keys) + list(spots):
        pal = pal[~np.all(pal == c, -1)]
    if not len(pal):
        raise Fail('시트의 기본 칸에서 팔레트를 얻지 못했다 (빈 시트?)')
    return pal


def window(c, a, scale):
    """칸의 한 변 c (게임 px, anchor 는 a)에 해당하는 원본 창의 길이 (정수 px) → (길이, 창 안에서 anchor 의 자리).
    c/scale 에 가장 가까운 세 정수 중에서, anchor 가 원본 픽셀 경계에서 벗어나는 양(게임 px) + 배율 오차가 anchor 에서 칸 끝까지
    쌓이는 양(게임 px)이 가장 작은 것 — 96 칸은 580 (가운데 290 딱 맞음), 112 칸의 가로는 678 (677 이면 가운데가 반 픽셀 어긋난다)."""
    def cost(S):
        return abs(a * S / c - rnd(a * S / c)) * c / S + abs(c / (S * scale) - 1) * max(a, c - a)
    S = min((rnd(c / scale) + d for d in (0, -1, 1)), key=cost)
    return S, rnd(a * S / c)


def convert(frames, cell, anchor, scale, pal, keys, roles, spots, floor, center):
    """원본 프레임들 → (칸 목록, 프레임별 잰 값). 모든 프레임이 같은 원본 창(= 칸 전체)에서 같은 격자로 줄어든다."""
    cw, ch = cell
    ax, ay = anchor
    (Sx, ox), (Sy, oy) = window(cw, ax, scale), window(ch, ay, scale)   # 칸 전체에 해당하는 원본 창, 그 안의 가운데 열·바닥 줄 아랫변
    dx, dy = ox - center, oy - (floor + 1)             # 프레임 좌표 → 창 좌표
    eff = (cw / Sx, ch / Sy)
    log(f'  원본 창 {Sx}x{Sy}px → 칸 {cw}x{ch} (실제 배율 {eff[0]:.5f} x {eff[1]:.5f}, 요청 {scale:g}); '
        f'원본 x={center:g} → 칸 x={ox * cw / Sx:.2f} (anchor {ax}), 바닥 줄 y={floor} 아랫변 → 칸 y={oy * ch / Sy:.2f} (anchor {ay})')
    cells, info, bad, edge = [], [], [], []
    for i, arr in enumerate(frames):
        rgb, alpha, _ = sh.matte(np.ascontiguousarray(arr))
        H, W = alpha.shape
        bb = sh.bbox(alpha, 0.5)
        if bb is None:
            raise Fail(f'{i + 1}번 프레임이 비었다')
        x0, y0, x1, y1 = (int(v) for v in bb)
        # 띠는 384px 씩 자른다: 그림이 칸의 가장자리 열(0 / 383)에 닿으면 옆 칸으로 넘어간 것이다 (잘린 그림 또는 옆 자세의 조각)
        touch = [s for s, hit in (('왼쪽(x=0)', x0 <= 0), (f'오른쪽(x={W - 1})', x1 >= W), ('위(y=0)', y0 <= 0), (f'아래(y={H - 1})', y1 >= H)) if hit]
        if touch:
            edge.append(f'{i + 1}번 프레임: 그림이 {SLOT}px 프레임의 {"·".join(touch)} 가장자리에 닿는다 (bbox x {x0}-{x1 - 1}, y {y0}-{y1 - 1})')
            continue
        over = [(side, d) for side, d in (('왼쪽으로', 1 - (x0 + dx) * cw / Sx), ('오른쪽으로', (x1 + dx) * cw / Sx - (cw - 1)),
                                           ('위로', 1 - (y0 + dy) * ch / Sy), ('아래로', (y1 + dy) * ch / Sy - ch)) if d > 1e-6]
        if over:
            bad.append(f'{i + 1}번 프레임: ' + ', '.join(f'{side} {d:.1f}px (원본 {int(np.ceil(d / eff[0]))}px)' for side, d in over))
            continue
        c_rgb = np.zeros((Sy, Sx, 3), np.float32)
        c_a = np.zeros((Sy, Sx), np.float32)
        fx0, fy0, fx1, fy1 = max(0, -dx), max(0, -dy), min(W, Sx - dx), min(H, Sy - dy)
        c_rgb[fy0 + dy:fy1 + dy, fx0 + dx:fx1 + dx] = rgb[fy0:fy1, fx0:fx1]
        c_a[fy0 + dy:fy1 + dy, fx0 + dx:fx1 + dx] = alpha[fy0:fy1, fx0:fx1]
        klab = sh.key_label(c_rgb, c_a, keys) if len(keys) else None
        s_rgb, mask, s_k, s_sp, _, _ = sh.shrink_pose(c_rgb, c_a, klab, len(keys), spots, scale, cw, ch, ALPHA)
        if not mask.any():
            raise Fail(f'{i + 1}번 프레임이 축소 후 비었다')
        s_rgb = sh.outline(s_rgb, mask)
        q = sh.paint_pose(s_rgb, mask, s_k, s_sp, pal, keys, roles, spots)
        c = np.zeros((ch, cw, 4), np.uint8)
        c[..., :3] = np.clip(q, 0, 255).astype(np.uint8)
        c[..., 3] = mask * 255
        c[..., :3][~mask] = 0
        cells.append(c)
        ys, xs = np.nonzero(mask)
        info.append({'frame': i + 1, 'bbox': [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
                     'above_floor': int(ay - 1 - ys.max()), 'src_lowest_y': y1 - 1})
    if edge:
        raise Fail('프레임 칸(384px)의 테두리를 넘는 그림이 있다 — 띠를 384px 씩 자르면 그림이 잘리거나 옆 프레임의 조각이 들어온다. '
                   '자세를 프레임 가운데(엉덩이 x=192)에 두고 테두리와 띄워 다시 그릴 것:\n    ' + '\n    '.join(edge))
    if bad:
        raise Fail(f'칸 {cw}x{ch} (가장자리 1px 여유)에 들어가지 않는 프레임이 있다 — 줄이거나 밀지 않는다. '
                   '그림을 고치거나 더 큰 칸으로 기본 시트를 다시 등록할 것:\n    ' + '\n    '.join(bad))
    return cells, info


# ───────── 붙이기 · 빼기 ─────────

def command_for(sid, gait, rec):
    cmd = ['python3', 'tools/art/add_gait.py', sid, '--gait', gait, '--src', *rec.get('src', ['<원본>'])]
    cmd += ['--pose', rec['pose']] if rec.get('pose') else ['--stride', f'{rec.get("stride", 0):g}']
    ms = rec.get('ms')
    if isinstance(ms, int):
        cmd += ['--ms', str(ms)]
    if rec.get('floor', FLOOR) != FLOOR:
        cmd += ['--floor', str(rec['floor'])]
    if rec.get('center', SLOT // 2) != SLOT // 2:
        cmd += ['--center', str(rec['center'])]
    if rec.get('scale'):
        cmd += ['--scale', f'{rec["scale"]:g}']
    if rec.get('allow_below'):
        cmd += ['--allow-below']
    return ' '.join(shlex.quote(c) for c in cmd)


GUIDES = os.path.join(ROOT, 'art', 'requests', 'guides')
INBOX_GUIDES = os.path.join(ROOT, 'art', 'inbox', 'guides')
DRAFT_IOU = 0.85             # 원본 프레임의 실루엣이 뼈대(마네킹)의 한 프레임과 이만큼 겹치면 마네킹으로 본다
                             # (2026-11-26 0.9 → 0.85: 그린 그림 57장 — GPT 시트 53 + 그린 달리기 띠 4 — 의 가장 높은 값 0.720, 여유 0.13;
                             #  윤곽 덧칠·가늘게·고르지 않은 확대로 0.85~0.9 에 머물던 마네킹 편집도 거부된다)
DRAFT_SEARCH = 24            # 맞춘 뒤 x, y 로 더 찾아보는 범위 (원본 px)
EXTRA_GUIDES = []            # 비교에 더할 폴더 (receive.py 가 origin/art-inbox 의 art/inbox/guides/ 를 꺼내 둔 곳; --extra-guides)
INBOX_REF = 'origin/art-inbox'   # 이 ref 의 art/inbox/guides/** 도 비교한다 (git show; 작업 트리에 아직 없는 PC 마네킹)
NORM_RANGE = (0.5, 4.0)      # 원본 프레임을 뼈대 프레임의 그림 높이로 맞춰 볼 때 허용하는 높이 비 (4: 시트에 1/4 높이로 작게 넣은 마네킹 격자까지)
ROT_STEP, ROT_MAX = 2, 8     # 기울인 마네킹: 원본을 ±2도부터 2도씩 ±8도까지 돌려 다시 잰다 (IoU 가 오르는 쪽으로만 더 돌린다) — ±9도까지 남는 기울기 ≤ 1도
ROT_GATE = 0.5               # 돌려 보는 짝: 그대로 잰 IoU 가 이 이상 (뼈대 프레임을 9도 돌리면 제 프레임과 IoU 가 0.54 까지 떨어진다)
ROT_FINE = 0.8               # 2도 간격으로 찾은 가장 높은 IoU 가 이 이상이면 그 양옆 1도도 잰다 (1도 남은 마네킹이 0.90 언저리까지 떨어진다)
_DRAFT_MASKS = {}


def frame_mask(arr):
    """한 프레임(RGBA)의 실루엣: 배경 키(#FF00FF 등 테두리 색)나 투명을 뺀 곳 — 보이는 레이어를 모두 합친 모양"""
    if arr.shape[-1] == 3:
        arr = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
    return sh.matte(np.ascontiguousarray(arr))[1] > 0.5


def _crop(m):
    """mask → 그림 테두리 상자로 자른 bool 배열 (빈 mask 면 None)"""
    rows, cols = np.flatnonzero(m.any(1)), np.flatnonzero(m.any(0))
    if not len(rows):
        return None
    return np.ascontiguousarray(m[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1])


def _fast(n):
    """n 이상인 가장 작은 2·3·5 의 곱 (FFT 크기)"""
    while True:
        k = n
        for f in (2, 3, 5):
            while k % f == 0:
                k //= f
        if k == 1:
            return n
        n += 1


def aligned_iou(a, b, search=DRAFT_SEARCH):
    """두 실루엣(테두리 상자로 자른 bool 배열)의 IoU 를 자리와 상관없이 잰다:
    상자의 아래 가운데를 맞춘 뒤 x, y 로 ±search px 안에서 가장 많이 겹치는 자리 → (IoU, (dx, dy)).
    겹침은 FFT 상관으로 한 번에 센다 (모든 자리에서 정확한 값; 판 크기 = 큰 상자 + 2 x search 라 감아 돌지 않는다)."""
    ha, wa = a.shape
    hb, wb = b.shape
    H, W = max(ha, hb) + 2 * search, max(wa, wb) + 2 * search
    FH, FW = _fast(H), _fast(W)
    bottom, mid = search + max(ha, hb), search + max(wa, wb) // 2

    def place(m):
        h, w = m.shape
        c = np.zeros((FH, FW), np.float64)
        c[bottom - h:bottom, mid - w // 2:mid - w // 2 + w] = m
        return c
    A, B = place(a), place(b)
    corr = np.fft.irfft2(np.conj(np.fft.rfft2(A)) * np.fft.rfft2(B), s=(FH, FW))   # corr[s] = Σ A(p) B(p+s)
    idx_y = np.arange(-search, search + 1) % FH
    idx_x = np.arange(-search, search + 1) % FW
    win = np.rint(corr[np.ix_(idx_y, idx_x)])
    na, nb = float(a.sum()), float(b.sum())
    iou = win / np.maximum(na + nb - win, 1)
    k = np.unravel_index(int(np.argmax(iou)), iou.shape)
    return float(iou[k]), (int(k[1]) - search, int(k[0]) - search)


def _slots(arr):
    """한 장의 그림(높이 1024, 너비 384 의 배수) → 프레임들; 규격이 아니면 []"""
    if arr.shape[0] != 1024 or arr.shape[1] % SLOT:
        return []
    return [arr[:, k * SLOT:(k + 1) * SLOT] for k in range(arr.shape[1] // SLOT)]


def _cache_dir():
    base = os.environ.get('XDG_CACHE_HOME') or os.path.join(os.path.expanduser('~'), '.cache')
    return os.path.join(base, 'pixel-management', 'guide_masks')


def _ase_guide_masks(path, exe, label=None):
    """마네킹 .aseprite 의 보이는 레이어를 합친 프레임 실루엣들 (한 Aseprite 프레임이 384 의 배수 너비면 384 씩 자른다).
    파일 내용의 sha256 으로 캐시한다 (~/.cache/pixel-management/guide_masks/) — 같은 파일은 Aseprite 를 다시 부르지 않는다.
    label: 오류 문구에 쓸 이름 (git show 로 꺼낸 임시 파일이면 origin/art-inbox:<경로>)"""
    import hashlib
    with open(path, 'rb') as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    cache = os.path.join(_cache_dir(), digest + '.npz')
    label = label or rel(path)
    try:
        z = np.load(cache)
        return [np.unpackbits(z['bits'][i], count=int(z['h']) * int(z['w'])).reshape(int(z['h']), int(z['w'])).astype(bool)
                for i in range(len(z['bits']))]
    except (OSError, KeyError, ValueError):
        pass
    exe2 = find_aseprite(exe)
    if not exe2:
        raise Fail(f'{label}: 마네킹 .aseprite 를 비교 대상으로 읽을 Aseprite 실행 파일이 없다 (--aseprite-bin / tools/art/ase_headless.sh) '
                   '— 비교 없이 받지 않는다')
    with tempfile.TemporaryDirectory(prefix='gait-guide-') as tmp:
        png, js = os.path.join(tmp, 'frames.png'), os.path.join(tmp, 'frames.json')
        r = subprocess.run([exe2, '--batch', os.path.abspath(path), '--sheet', png, '--data', js, '--format', 'json-array'],
                           stdin=subprocess.DEVNULL, capture_output=True, timeout=300, env=ase_env())
        if r.returncode or not os.path.exists(png) or not os.path.exists(js):
            raise Fail(f'{label}: 마네킹 .aseprite 를 비교 대상으로 내보내지 못했다 — 비교 없이 받지 않는다: '
                       + (r.stderr or r.stdout).decode('utf-8', 'replace').strip()[-200:])
        with open(js, encoding='utf-8') as f:
            data = json.load(f)['frames']
        arr = np.asarray(Image.open(png).convert('RGBA'))
    masks = []
    for fr in data:
        q = fr['frame']
        masks += [frame_mask(s) for s in _slots(arr[q['y']:q['y'] + q['h'], q['x']:q['x'] + q['w']])]
    if masks:
        try:
            os.makedirs(_cache_dir(), exist_ok=True)
            h, w = masks[0].shape
            tmpf = cache + f'.{os.getpid()}.npz'
            np.savez_compressed(tmpf, bits=np.stack([np.packbits(m.ravel()) for m in masks]), h=h, w=w)
            os.replace(tmpf, cache)
        except OSError:
            pass
    return masks


def _git(*args):
    r = subprocess.run(['git', '-C', ROOT, *args], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def inbox_ref_guides():
    """origin/art-inbox 의 art/inbox/guides/** 중 .aseprite / .ase / .png → [(경로, blob id)]; ref 가 없으면 None"""
    out = _git('ls-tree', '-r', INBOX_REF, '--', 'art/inbox/guides')
    if out is None:
        return None
    rows = []
    for ln in out.decode('utf-8', 'replace').splitlines():
        meta, _, path = ln.partition('\t')
        parts = meta.split()
        if len(parts) == 3 and parts[1] == 'blob' and path.lower().endswith(('.aseprite', '.ase', '.png')):
            rows.append((path, parts[2]))
    return rows


def draft_masks(exe=None):
    """비교할 뼈대(마네킹) 프레임의 실루엣 → [(이름, 테두리 상자로 자른 mask)] (같은 모양은 한 번만):
      - 클라우드 초안 art/requests/guides/<set>/<하위 폴더>/ (v<n>/, draft/ …): 띠 png(높이 1024, 너비 384 의 배수)와 layers/ 의 레이어 png 를
        프레임마다 합친 것(joints 제외)
      - art/requests/guides/<set>/ 바로 아래의 띠 png
      - PC 가 넘긴 마네킹 art/inbox/guides/**: <id>.aseprite 등 모든 .aseprite (보이는 레이어, 내보내서 캐시)와 띠 png
      - origin/art-inbox 의 art/inbox/guides/** (git show 로 꺼낸다: 이 브랜치에 아직 들이지 않은 PC 마네킹; 이름 origin/art-inbox:<경로>)
      - EXTRA_GUIDES 폴더들 (receive.py 가 꺼내 둔 곳 등) — 같은 규칙"""
    key = tuple(EXTRA_GUIDES)
    if key in _DRAFT_MASKS:
        return _DRAFT_MASKS[key]
    out, seen = [], set()

    def add(name, m):
        c = _crop(m)
        if c is None:
            return
        h = (c.shape, np.packbits(c).tobytes())
        if h not in seen:
            seen.add(h)
            out.append((name, c))

    def strips(pngs):
        for png in pngs:
            try:
                arr = np.asarray(Image.open(png).convert('RGBA'))
            except OSError:
                continue
            for k, fr in enumerate(_slots(arr)):                # 리뷰 그림·미리보기는 규격이 아니라 빠진다
                add(f'{rel(png)} 의 {k + 1}번 프레임', frame_mask(fr))

    for sdir in sorted(glob.glob(os.path.join(GUIDES, '*'))):
        strips(sorted(glob.glob(os.path.join(sdir, '*.png'))))
    for pose_path in sorted(glob.glob(os.path.join(ROOT, 'art', 'requests', 'gait', '*', 'pose.json'))):
        try:
            with open(pose_path, encoding='utf-8') as f:
                pose = json.load(f)
        except (OSError, ValueError) as e:
            log(f'  마네킹 비교: {rel(pose_path)} 읽기 실패, 건너뜀 ({e})')
            continue
        if isinstance(pose, dict) and pose.get('scaled_from'):
            strips(sorted(glob.glob(os.path.join(os.path.dirname(pose_path), 'guide_*_?.png'))))
    # 세트 아래의 하위 폴더 모두: v<n>/ (받아들인 판), draft/ (heavy_base·robe_base 처럼 PC 가 아직 다듬지 않은 클라우드 초안), 앞으로 생길 다른 이름도
    for vdir in sorted(glob.glob(os.path.join(GUIDES, '*', '*'))):
        if not os.path.isdir(vdir):
            continue
        strips(sorted(glob.glob(os.path.join(vdir, '*.png'))))
        groups = {}
        for png in sorted(glob.glob(os.path.join(vdir, 'layers', '*_*.png'))):
            fr, layer = os.path.basename(png)[:-4].split('_', 1)
            if layer != 'joints':
                groups.setdefault(fr, []).append(png)
        for fr, pngs in sorted(groups.items()):
            m = None
            for png in pngs:
                a = np.asarray(Image.open(png).convert('RGBA'))[..., 3] > 0
                m = a if m is None else (m | a) if m.shape == a.shape else m
            if m is not None and m.shape[1] == SLOT:
                add(f'{rel(os.path.join(vdir, "layers"))}/{fr}_*', m)
    def tree(root, label):
        for png in sorted(glob.glob(os.path.join(root, '**', '*.png'), recursive=True)):
            try:
                arr = np.asarray(Image.open(png).convert('RGBA'))
            except OSError:
                continue
            for k, fr in enumerate(_slots(arr)):
                add(f'{label(png)} 의 {k + 1}번 프레임', frame_mask(fr))
        for ase in sorted(glob.glob(os.path.join(root, '**', '*.aseprite'), recursive=True)
                          + glob.glob(os.path.join(root, '**', '*.ase'), recursive=True)):
            for k, m in enumerate(_ase_guide_masks(ase, exe, label(ase))):
                add(f'{label(ase)} 의 {k + 1}번 프레임', m)

    tree(INBOX_GUIDES, rel)
    ref = inbox_ref_guides()
    if ref is None:
        log(f'  마네킹 비교: {INBOX_REF} 가 없다 (git fetch origin art-inbox) — 작업 트리의 art/inbox/guides/ 와 --extra-guides 만 비교한다')
    elif ref:
        with tempfile.TemporaryDirectory(prefix='gait-inbox-guides-') as tmp:
            names = {}
            for path, blob in ref:
                data = _git('cat-file', 'blob', blob)
                if data is None:
                    raise Fail(f'{INBOX_REF}:{path} 를 읽지 못했다 — 비교 없이 받지 않는다')
                dst = os.path.join(tmp, *path[len('art/inbox/guides/'):].split('/'))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as f:
                    f.write(data)
                names[os.path.realpath(dst)] = f'{INBOX_REF}:{path}'
            tree(tmp, lambda q: names.get(os.path.realpath(q), q))
    for root in EXTRA_GUIDES:
        tree(root, lambda q, r=root: f'{os.path.basename(os.path.normpath(r))}/{os.path.relpath(q, r)} ({q})')
    _DRAFT_MASKS[key] = out
    return out


def _to_height(m, h):
    """잘린 실루엣 m 을 그림 높이 h 로 (가로세로 비 유지; 넓이 평균 후 반 이상 = 켬)"""
    k = h / m.shape[0]
    w = max(1, round(m.shape[1] * k))
    im = Image.fromarray(m.astype(np.uint8) * 255, 'L').resize((w, h), Image.BOX)
    return np.ascontiguousarray(np.asarray(im) >= 128)


def _rotate(m, deg):
    """잘린 실루엣 m 을 deg 도(반시계) 돌려 다시 자른 것. 자른 뒤 아래 가운데로 맞추므로(aligned_iou) 발바닥 가운데로 돌려
    바닥에 다시 세운 것과 같다 (돌리는 중심은 옮김만 바꾼다)"""
    im = Image.fromarray(m.astype(np.uint8) * 255, 'L').rotate(deg, resample=Image.BILINEAR, expand=True)
    return _crop(np.asarray(im) >= 128)


def best_guide_match(frames, exe=None, stop=None, masks=None, drafts=None):
    """원본 프레임들 각각(과 좌우를 뒤집은 것)을 모든 뼈대 프레임에 자리를 맞춰 대 본 가장 높은 IoU
    → (IoU, 프레임 번호, 뼈대 이름, 뒤집었나, (dx, dy), 높이 맞춤 배율 또는 None, 돌린 각도(도) 또는 0). 원본 그대로 한 번, 원본을 그
    뼈대 프레임의 그림 상자 높이로 맞춰(가로세로 비 유지, 높이 비 NORM_RANGE 안) 한 번 잰다 — 크기를 바꾼 마네킹. 그렇게 잰 IoU 가
    ROT_GATE 이상인 짝은 원본을 ±ROT_STEP 도 돌려(발바닥 가운데로, 바닥에 다시 세워) 더 재고, IoU 가 오르는 쪽으로 ROT_MAX 까지
    ROT_STEP 씩 더 돌리고, 그렇게 찾은 IoU 가 ROT_FINE 이상이면 그 양옆 1도도 잰다 — 기울인 마네킹 (±9도 안; 높이를 맞춘 짝은 원본을
    돌린 뒤에 높이를 맞춘다 — 크기를 바꾸고 기울인 마네킹).
    넓이 비가 지금까지의 최고보다 낮은 짝은 재지 않는다 (IoU ≤ 넓이 비). stop 을 주면 그보다 높은 짝을 찾는 대로 멈추고, 넓이 비가 stop
    이하인 짝도 재지 않는다 (판정만 필요할 때 — 돌려주는 값은 stop 이하일 수 있다).
    masks: frames 대신 이미 실루엣으로 만든 bool 배열들 (sheets.py 가 split_poses 로 자세를 나눈 그림).
    drafts: 비교할 뼈대 실루엣 [(이름, bool 배열)] (기본: draft_masks — 3D 마네킹은 m3d_masks 로 따로 잰다)."""
    drafts = [(n, d, float(d.sum())) for n, d in (drafts if drafts is not None else draft_masks(exe))]
    best = (0.0, None, None, False, (0, 0), None, 0)
    floor = stop or 0.0
    for i, fr in enumerate(masks if masks is not None else frames):
        c = _crop(fr if masks is not None else frame_mask(fr))
        if c is None:
            continue
        for flip, m in ((False, c), (True, np.ascontiguousarray(c[:, ::-1]))):
            scaled, rots, turned = {}, {}, {}
            na_m, tilts = float(m.sum()), None

            def rot(deg, m=m, rots=rots):
                if deg not in rots:
                    rots[deg] = _rotate(m, deg) if deg else m
                return rots[deg]

            def turn(deg, h, d, turned=turned):
                """원본을 deg 도 돌려(h 를 주면 그 다음 높이 h 로 맞춰) d 에 잰 (IoU, 옮김, 높이 맞춤 배율). 높이 맞춤은 돌린 뒤에 한다 —
                기울어진 채 높이를 맞추면 상자가 커진 만큼 작게 맞는다. 돌리고 맞춘 실루엣은 캐시한다"""
                key = (h, deg)
                if key not in turned:
                    r, kr = rot(deg), None
                    if r is not None and h is not None and r.shape[0] != h:
                        kr = h / r.shape[0]
                        r = _to_height(r, h) if NORM_RANGE[0] <= kr <= NORM_RANGE[1] else None
                    turned[key] = (r, kr)
                r, kr = turned[key]
                return (*aligned_iou(r, d), kr) if r is not None else (0.0, (0, 0), kr)

            for name, d, nb in drafts:
                h = d.shape[0]
                k = h / m.shape[0]
                start = {}                                       # 돌리기 전 값: None(그대로)·h(높이 맞춤) → (IoU, 옮김, 배율)
                if min(na_m, nb) / max(na_m, nb) > max(best[0], floor):    # 그대로 (돌려도 넓이는 같다)
                    iou, sh_ = aligned_iou(m, d)
                    start[None] = (iou, sh_, None)
                    if iou > best[0]:
                        best = (iou, i + 1, name, flip, sh_, None, 0)
                        if stop is not None and iou > stop:
                            return best
                if NORM_RANGE[0] <= k <= NORM_RANGE[1]:          # 높이 맞춤: 넓이는 돌린 상자 높이에 따라 바뀐다 — 돌릴 각도 모두로 넓이 비를 본다
                    if tilts is None:
                        tilts = [r.shape[0] for r in (rot(q) for q in range(-ROT_MAX - 1, ROT_MAX + 2)) if r is not None]
                    if max(min(a, nb) / max(a, nb) for a in (na_m * (h / t) ** 2 for t in tilts)) > max(best[0], floor):
                        if h == m.shape[0]:
                            start[h] = start.get(None) or (*aligned_iou(m, d), None)
                        else:
                            if h not in scaled:
                                scaled[h] = _to_height(m, h)
                            iou, sh_ = aligned_iou(scaled[h], d)
                            start[h] = (iou, sh_, k)
                            if iou > best[0]:
                                best = (iou, i + 1, name, flip, sh_, k, 0)
                                if stop is not None and iou > stop:
                                    return best
                # 기울인 마네킹: 그대로·높이 맞춤 각각, 돌리기 전 IoU 가 ROT_GATE 이상이면 ±ROT_STEP 도 돌려 재고 오르는 쪽으로
                # ROT_MAX 까지 ROT_STEP 씩 더 돌린다 (내려가면 멈춘다). 찾은 IoU 가 ROT_FINE 이상이면 그 양옆 1도도 잰다.
                for kind, (iou0, sh0, k0) in start.items():
                    if iou0 < ROT_GATE:
                        continue
                    got = {0: (iou0, sh0, k0)}
                    got.update({deg: turn(deg, kind, d) for deg in (ROT_STEP, -ROT_STEP)})
                    at = max(got, key=lambda q: got[q][0])
                    if at:
                        sgn = 1 if at > 0 else -1
                        while abs(at) + ROT_STEP <= ROT_MAX:
                            nxt = at + sgn * ROT_STEP
                            got[nxt] = turn(nxt, kind, d)
                            if got[nxt][0] <= got[at][0]:
                                break
                            at = nxt
                    if got[at][0] >= ROT_FINE:
                        for nxt in (at - 1, at + 1):
                            if nxt not in got and abs(nxt) <= ROT_MAX + 1:
                                got[nxt] = turn(nxt, kind, d)
                    for deg, (iou, sh_, kr) in got.items():
                        if iou > best[0]:
                            best = (iou, i + 1, name, flip, sh_, kr, deg)
                    if stop is not None and best[0] > stop:
                        return best
    return best


def match_words(dx, dy, flip, k, deg):
    """best_guide_match 의 맞춘 방법 → 문구"""
    return (f'아래 가운데를 맞추고 {dx:+d},{dy:+d}px 옮겨서{", 좌우를 뒤집어서" if flip else ""}'
            f'{f", 그림 높이를 x{k:.3f} 로 맞춰서" if k else ""}{f", {deg:+d}도 돌려서" if deg else ""}')


def draft_match(p, exe):
    """원본의 어느 프레임(또는 좌우로 뒤집은 것)이 뼈대(마네킹) 프레임과 자리를 맞춰 실루엣 IoU > DRAFT_IOU 로 겹치면 그 이유, 아니면 None.
    joints 레이어를 지운 마네킹, 이름을 바꾼 마네킹 띠, 몇 px 옮기거나 뒤집은 마네킹도 잡는다
    (그린 캐릭터는 옷·머리·무기로 실루엣이 달라진다 — 등록된 시트의 GPT 원본은 자리를 맞춰도 0.72 이하)."""
    try:
        if p.lower().endswith(('.aseprite', '.ase')):
            frames = frames_from_aseprite(p, exe)[0]
        else:
            arr = np.asarray(Image.open(p).convert('RGBA'))
            if arr.shape[1] % SLOT:
                return None                                # load_frames 가 규격 오류로 실패시킨다
            frames = [arr[:, k * SLOT:(k + 1) * SLOT] for k in range(arr.shape[1] // SLOT)]
    except OSError:
        return None
    iou, fi, name, flip, (dx, dy), k, deg = best_guide_match(frames, exe, stop=DRAFT_IOU)
    if iou > DRAFT_IOU:
        return (f'{fi}번 프레임의 실루엣이 뼈대(마네킹)와 겹친다 — 맞은 마네킹: {name}, IoU {iou:.3f} > {DRAFT_IOU} '
                f'({match_words(dx, dy, flip, k, deg)}) '
                '= 마네킹 (joints 레이어를 지웠거나 이름을 바꾸거나 옮기거나 크기를 바꾸거나 기울인 것)')
    return None


def guide_reason(p, exe):
    """뼈대 가이드(마네킹)로 보이면 그 이유, 아니면 None. 마네킹은 PC 가 만드는 자세 가이드이고 게임 프레임이 되지 않는다:
    - 경로에 guides 폴더 (art/requests/guides/<id>/…, PC 가 넘기는 art/inbox/guides/<id>/<id>.aseprite)
    - 옆에 pose_measured.json (check_skeleton.py --export 가 마네킹에서 뽑은 띠)
    - joints 레이어가 있는 .aseprite (관절 점 레이어 = 뼈대 작업 파일)
    - 3D 마네킹(tools/mannequin3d)의 색이 한 프레임의 25% 이상 (mannequin3d_reason — 칠하지 않은 3D 가이드, 위치와 실루엣에 상관없이)
    - 넘긴 3D 마네킹 가이드(pose.json source 에 tools/mannequin3d 인 art/requests/gait/* 폴더)와 IoU > 0.93 (m3d_match — 색만 바꾼 것)
    - 어느 프레임(또는 뒤집은 것)의 실루엣이 뼈대 프레임(draft_masks: 클라우드 초안 + PC 가 넘긴 art/inbox/guides/ 마네킹)과
      자리를 맞춰 IoU > 0.85 (joints 레이어를 지운 마네킹, 이름을 바꾸거나 옮기거나 뒤집거나 크기를 바꾸거나 ±9도 안으로 기울인 마네킹)"""
    real = os.path.realpath(p)
    if 'guides' in real.split(os.sep)[:-1]:
        return 'guides/ 폴더 안의 파일 = 뼈대 가이드'
    if os.path.exists(os.path.join(os.path.dirname(real), 'pose_measured.json')):
        return '옆에 pose_measured.json — check_skeleton.py --export 가 마네킹에서 뽑은 띠'
    if p.lower().endswith(('.aseprite', '.ase')):
        names, visible = ase_layers(p, exe)
        if 'joints' in names:
            if 'joints' in visible:
                raise Fail(f'{p}: joints 레이어가 보인다 — 관절 점이 프레임에 그대로 찍힌다. 이 파일은 뼈대(마네킹)이고 게임 프레임이 아니다')
            return 'joints 레이어가 있는 .aseprite = 뼈대 작업 파일(마네킹)'
    why = mannequin3d_reason(p) or m3d_match(p)
    if why:
        return why
    return draft_match(p, exe)


M3D_IOU = 0.93               # 3D 마네킹(tools/mannequin3d) 가이드와의 실루엣 IoU 문턱 — 캐릭터에 맞춘 3D 몸 위에 칠하는 것이 바로 그 작업이라
                             # 2D 마네킹의 0.85 를 쓰지 않는다 (그린 전사 달리기 vs 맞춘 3D 가이드: 자리를 맞춰 0.78). 색만 바꾼 마네킹은 0.99


def m3d_masks():
    """art/requests/gait/*/ 가운데 pose.json 의 source 에 tools/mannequin3d 가 있는 폴더(3D 마네킹 가이드를 넘긴 요청)의 guide 띠 실루엣"""
    out = []
    for pose_path in sorted(glob.glob(os.path.join(ROOT, 'art', 'requests', 'gait', '*', 'pose.json'))):
        try:
            with open(pose_path, encoding='utf-8') as f:
                pose = json.load(f)
        except (OSError, ValueError):
            continue
        if not (isinstance(pose, dict) and 'mannequin3d' in str(pose.get('source', ''))):
            continue
        for png in sorted(glob.glob(os.path.join(os.path.dirname(pose_path), 'guide_*_?.png'))):
            try:
                arr = np.asarray(Image.open(png).convert('RGBA'))
            except OSError:
                continue
            for k, fr in enumerate(_slots(arr)):
                c = _crop(frame_mask(fr))
                if c is not None:
                    out.append((f'{rel(png)} 의 {k + 1}번 프레임', c))
    return out


def m3d_match(p):
    """넘긴 3D 마네킹 가이드와 실루엣 IoU > M3D_IOU 이면 그 이유 (색을 바꾸거나 덧칠만 한 3D 마네킹)"""
    masks = m3d_masks()
    if not masks or p.lower().endswith(('.aseprite', '.ase')):
        return None
    try:
        arr = np.asarray(Image.open(p).convert('RGBA'))
    except OSError:
        return None
    if arr.shape[1] % SLOT:
        return None
    frames = [arr[:, k * SLOT:(k + 1) * SLOT] for k in range(arr.shape[1] // SLOT)]
    iou, fi, name, flip, (dx, dy), k, deg = best_guide_match(frames, stop=M3D_IOU, drafts=masks)
    if iou > M3D_IOU:
        return (f'{fi}번 프레임의 실루엣이 3D 마네킹 가이드와 거의 같다 — {name}, IoU {iou:.3f} > {M3D_IOU} '
                f'({match_words(dx, dy, flip, k, deg)}) = 색만 바꾼 3D 마네킹')
    return None


def mannequin3d_reason(p):
    """3D 마네킹 가이드(tools/mannequin3d)의 색이 그대로 남은 그림이면 그 이유 — 가이드를 어디에 썼든(스크래치 폴더 포함) 잡는다.
    실루엣 IoU 와 달리 캐릭터에 맞춘 3D 마네킹 위에 제대로 칠한 그림은 걸리지 않는다 (그린 그림 71장: 마네킹 색 0.003% 이하)."""
    if p.lower().endswith(('.aseprite', '.ase')):
        return None
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools', 'mannequin3d'))
        from signature import mannequin3d_reason as m3d
    except ImportError:
        return None
    finally:
        if sys.path and sys.path[0].endswith(os.path.join('tools', 'mannequin3d')):
            sys.path.pop(0)
    return m3d(p)


def draft_guard(src, allow, exe=None):
    """sheets.py 와 같은 규칙 + 뼈대 가이드: 초안·가이드의 그림은 게임 시트에 붙이지 않는다. → 시험 처리(dry-run 강제)인가"""
    forced = False
    for p in src:
        why = sh.novelai_draft_reason(p) or guide_reason(p, exe)
        if not why:
            continue
        if not allow:
            raise Fail(f'{p}: 게임 그림이 아닌 자리의 파일이라 거부 ({why}). 디자인 초안·뼈대 가이드는 게임에 넣지 않는다 — 게임 그림은 GPT 를 거쳐 '
                       'art/inbox/ 로 온다. 파이프라인 시험만이라면 --allow-draft (항상 --dry-run).')
        log(f'  {p}: 초안·가이드 ({why}) — --allow-draft 시험 처리, 시트·manifest 는 바꾸지 않는다')
        forced = True
    return forced


def gait_blocks(sid, entry, img, gait, rec, exe):
    """rec 의 원본을 변환해 → (칸 목록, ms 목록, 한 걸음 게임 px, 잰 값)"""
    meta = entry['sheet']
    req = request_for(sid)
    scale = rec.get('scale') or req.get('scale')
    if not scale:
        raise Fail(f'{sid}: 요청서에 scale 이 없다 (대기 자세 높이로 배율을 정한 시트) — 그 시트를 만든 배율을 --scale 로 줄 것')
    src = [absp(p) for p in rec['src']]
    frames, durs = load_frames(src, exe)
    n = len(frames)
    if n < 2:
        raise Fail(f'프레임이 {n}장뿐이다')
    if n % 2:
        log(f'  주의: 프레임이 {n}장(홀수) — 게임은 n 프레임을 두 걸음으로 본다')
    tint = req.get('tint') or meta.get('tint')
    if sid.startswith('sheet/class/') and 'tint' not in meta:
        tint = None                                   # 열쇠 색 없이 등록한 직업 시트 (--no-tint)
    keys, roles = sh.tint_keys(tint)
    spots = np.array([sh.hex_rgb(h) for h in (req.get('spots') or [])], np.float32).reshape(-1, 3)
    attached, base_n = layout(meta)
    base = img[:meta['frames'][base_n][1]] if attached else img
    pal = sheet_palette(base, keys, spots)
    log(f'  {n} 프레임, 배율 {scale:g}, 칸 {meta["cell"][0]}x{meta["cell"][1]}, anchor {meta["anchor"][0]},{meta["anchor"][1]}, '
        f'팔레트 {len(pal)}색 (시트의 기본 칸에서){", 열쇠 색 %d" % len(keys) if len(keys) else ""}{", 점 색 %d" % len(spots) if len(spots) else ""}')
    cells, info = convert(frames, meta['cell'], meta['anchor'], scale, pal, keys, roles, spots,
                          rec.get('floor', FLOOR), rec.get('center', SLOT // 2))
    # 한 걸음
    pose = None
    if rec.get('pose') and os.path.exists(absp(rec['pose'])):
        with open(absp(rec['pose']), encoding='utf-8') as f:
            pose = json.load(f)
    if rec.get('step_px'):
        stride = round(rec['step_px'] * scale, 1)
    elif rec.get('stride'):
        stride = rec['stride']
    else:
        raise Fail('한 걸음(게임 px)을 알 수 없다 — --stride 또는 step_px 가 든 --pose pose.json')
    if pose:
        pg = pose.get('gait', 'walk')
        if pg != gait and not (gait == 'run' and pg in POSE_CLASS):
            log(f'  주의: {rec["pose"]} 는 {pg} 세트인데 {gait} 로 붙인다')
        if pose.get('frames_per_cycle') and pose['frames_per_cycle'] != n:
            log(f'  주의: {rec["pose"]} 는 {pose["frames_per_cycle"]} 프레임인데 원본은 {n} 프레임')
    # 프레임 시간
    ms = rec.get('ms')
    if isinstance(ms, list) and len(ms) != n:
        ms = None
    if ms is None:
        ms = durs or (pose or {}).get('nominal_ms') or DEFAULT_MS[gait]
    ms = [int(ms)] * n if not isinstance(ms, list) else [int(v) for v in ms]
    touch = [r['frame'] for r in info if r['above_floor'] == 0]
    below = [r for r in info if r['above_floor'] < 0]
    log('  프레임별 맨 아래 픽셀 (바닥 줄 위 게임 px): ' + ' '.join(f'{r["frame"]}:{r["above_floor"]}' for r in info))
    if not touch:
        log(f'  주의: 바닥 줄(y={rec.get("floor", FLOOR)})에 닿는 프레임이 하나도 없다 — 바닥 줄이 다른 그림이면 --floor 로 줄 것')
    if below and not rec.get('allow_below'):
        raise Fail('바닥 줄 아래로 내려가는 프레임이 있다 — 게임에서 발이 땅에 묻힌다:\n    '
                   + '\n    '.join(f'{r["frame"]}번 프레임: 바닥 줄(y={rec.get("floor", FLOOR)}) 아래로 게임 {-r["above_floor"]}px '
                                   f'(원본 맨 아래 y={r["src_lowest_y"]})' for r in below)
                   + '\n    디딘 발의 맨 아래 픽셀을 y=870 에 두고 다시 그릴 것 (바닥 줄이 다른 그림이면 --floor). 일부러 그런 것이면 --allow-below')
    for r in below:
        log(f'  주의 (--allow-below): {r["frame"]}번 프레임이 바닥 줄 아래로 {-r["above_floor"]}px 내려간다 (원본 맨 아래 y={r["src_lowest_y"]})')
    return cells, ms, stride, info


def write_previews(work, name, sheet, entry, gait):
    meta = entry['sheet']
    cw, ch = meta['cell']
    sh.CELL, sh.ANCHOR = ch, tuple(meta['anchor'])
    sh.preview(sheet, os.path.join(work, f'{name}_preview_x4.png'))
    an = meta['anims'].get(gait)
    if not an:
        return
    ims = []
    for x, y in meta['frames'][an['from']:an['to'] + 1]:
        bg = np.zeros((ch, cw, 4), np.uint8)
        bg[..., :3], bg[..., 3] = (44, 40, 48), 255
        bg[meta['anchor'][1], :, :3] = (90, 60, 60)
        im = Image.fromarray(bg)
        im.alpha_composite(Image.fromarray(np.ascontiguousarray(sheet[y:y + ch, x:x + cw])))
        ims.append(im.convert('RGB').resize((cw * 4, ch * 4), Image.Resampling.NEAREST))
    ims[0].save(os.path.join(work, f'{name}_{gait}_x4.gif'), save_all=True, append_images=ims[1:], duration=an['ms'], loop=0, disposal=1)


def finish(sid, man, entry, new, sheet, a, gait=None):
    """새 시트·항목을 쓴다 (dry-run 이면 --work 에만)."""
    name = os.path.basename(entry['file'])[:-4]
    work = a.work
    if a.dry_run and not work:
        work = tempfile.mkdtemp(prefix='gait-')
    if work:
        os.makedirs(work, exist_ok=True)
    if a.dry_run:
        Image.fromarray(sheet).save(os.path.join(work, name + '.png'), optimize=True)
        with open(os.path.join(work, name + '.entry.json'), 'w', encoding='utf-8') as f:
            json.dump({sid: new}, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')
        write_previews(work, name, sheet, new, gait)
        log(f'  --dry-run: 시트·manifest 는 그대로. 새 시트 {os.path.join(work, name + ".png")} · 등록될 항목 {name}.entry.json · 미리보기 {name}_preview_x4.png')
        return
    Image.fromarray(sheet).save(os.path.join(ROOT, entry['file']), optimize=True)
    man[sid] = new
    save_manifest(man)
    if work:
        write_previews(work, name, sheet, new, gait)


def summary(sid, new):
    m = new['sheet']
    parts = [f'{k}({v["to"] - v["from"] + 1})' for k, v in sorted(m['anims'].items(), key=lambda kv: kv[1]['from'])]
    strides = ', '.join(f'{g}Stride {m[g + "Stride"]:g}' for g in GAITS if g + 'Stride' in m)
    return f'{sid}: 시트 {new["w"]}x{new["h"]}, {len(m["frames"])}칸 — {", ".join(parts)}{"; " + strides if strides else ""}'


def pose_class(rec):
    """기록의 pose.json "gait" → 이동 부류 (light / heavy / robe) 또는 None"""
    p = rec.get('pose')
    if not p or not os.path.exists(absp(p)):
        return None
    try:
        with open(absp(p), encoding='utf-8') as f:
            return POSE_CLASS.get(json.load(f).get('gait'))
    except (OSError, ValueError):
        return None


def table_class(sid):
    """tools/art/specs/gait_classes.json 의 sheets.<sid>.gait (없으면 None)"""
    try:
        with open(GAIT_CLASSES, encoding='utf-8') as f:
            return ((json.load(f).get('sheets') or {}).get(sid) or {}).get('gait')
    except (OSError, ValueError):
        return None


def set_gait_class(sid, nm, cls):
    nm['gait'] = cls
    tc = table_class(sid)
    log(f'  sheet.gait = {cls} (run 칸이 그려진 마네킹의 부류)' + ('' if tc in (None, cls) else
        f' — 주의: gait_classes.json 은 {sid} 를 {tc} 로 적는다. 엔진은 sheet.gait 를 먼저 본다: 표를 고치거나 그 부류의 마네킹 위에 다시 그릴 것'))


def attach(sid, man, gait, rec, a):
    entry = man[sid]
    meta = entry['sheet']
    if gait in meta['anims'] and gait not in (meta.get('gaits') or {}):
        raise Fail(f'{sid} 에는 add_gait 가 붙이지 않은 {gait} 칸이 이미 있다 (시트 자체의 태그) — 그대로 둔다')
    img = np.asarray(Image.open(os.path.join(ROOT, entry['file'])).convert('RGBA'))
    cells, ms, stride, _ = gait_blocks(sid, entry, img, gait, rec, a.aseprite_bin)
    blocks = existing_blocks(entry, img)
    blocks[gait] = (cells, ms)
    blocks = {g: blocks[g] for g in GAITS if g in blocks}   # 줄의 순서는 언제나 run → walk: 붙인 순서와 상관없이 같은 결과
    sheet, new = rebuild(entry, img, blocks)
    nm = new['sheet']
    nm[gait + 'Stride'] = stride
    rec = dict(rec, stride=stride, ms=ms[0] if len(set(ms)) == 1 else ms)
    rec.pop('class', None)
    if gait == 'run':
        cls = pose_class(rec)
        if cls:
            rec['class'] = cls
            set_gait_class(sid, nm, cls)
        elif (meta.get('gaits') or {}).get('run', {}).get('class') and 'gait' in nm:
            log(f'  sheet.gait {nm.pop("gait")} 를 지웠다 (전에 add_gait 가 쓴 값; 이번 원본은 부류를 모른다 — 엔진은 gait_classes.json 표를 본다)')
    nm.setdefault('gaits', {})[gait] = rec
    finish(sid, man, entry, new, sheet, a, gait)
    log('  ' + summary(sid, new))
    log(f'  다시 붙이는 명령: {command_for(sid, gait, rec)}')
    return new


def remove(sid, man, gait, a):
    entry = man[sid]
    meta = entry['sheet']
    recs = meta.get('gaits') or {}
    if gait not in recs:
        raise Fail(f'{sid} 에 add_gait 가 붙인 {gait} 칸이 없다' + (' (시트 자체의 태그는 건드리지 않는다)' if gait in meta['anims'] else ''))
    img = np.asarray(Image.open(os.path.join(ROOT, entry['file'])).convert('RGBA'))
    sheet, new = rebuild(entry, img, existing_blocks(entry, img, skip=(gait,)))
    nm = new['sheet']
    nm.pop(gait + 'Stride', None)
    if gait == 'run' and recs[gait].get('class') and 'gait' in nm:
        log(f'  sheet.gait {nm.pop("gait")} 도 뺐다 (run 칸과 같이 add_gait 가 쓴 값 — 엔진은 gait_classes.json 표를 본다)')
    del nm['gaits'][gait]
    if not nm['gaits']:
        del nm['gaits']
    finish(sid, man, entry, new, sheet, a)
    log(f'  {gait} 칸을 뺐다. ' + summary(sid, new))
    return new


def reattach(sid, man, a):
    """기록(gaits)은 있는데 칸(anims)이 없는 이동 동작을 기록된 원본에서 다시 붙인다 — 기본 시트를 다시 등록한 뒤."""
    recs = dict(man[sid]['sheet'].get('gaits') or {})
    pending = [g for g in recs if g not in man[sid]['sheet']['anims']]
    if not pending:
        log(f'{sid}: 다시 붙일 이동 칸이 없다')
        return 0
    failed = 0
    for g in pending:
        rec = recs[g]
        log(f'{sid}: {g} 칸을 기록된 원본에서 다시 붙인다 ({", ".join(rec.get("src", []))})')
        try:
            missing = [p for p in rec.get('src', []) if not os.path.exists(absp(p))]
            if missing or not rec.get('src'):
                raise Fail('원본이 없다: ' + (', '.join(missing) or '(기록에 src 가 없다)'))
            draft_guard([absp(p) for p in rec['src']], False, a.aseprite_bin)
            attach(sid, man, g, rec, a)
        except Fail as e:
            failed += 1
            bar = '!' * 78
            log(f'{bar}\n!!! 경고: {sid} 의 {g} 칸을 다시 붙이지 못했다 — {e}\n'
                f'!!! 지금 이 시트에는 {g} 칸이 없다 (게임은 이 시트를 {g} 동작 없이 그린다). 기록(sheet.gaits.{g})은 남겨 두었다.\n'
                f'!!! 원본을 되돌려 놓고:  python3 tools/art/add_gait.py {shlex.quote(sid)} --reattach\n'
                f'!!! 또는 새 원본으로:    {command_for(sid, g, dict(rec, src=["<a.png>", "<b.png>"]))}\n'
                f'!!! 기록까지 지우려면:   python3 tools/art/add_gait.py {shlex.quote(sid)} --gait {g} --remove\n{bar}')
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sheet', help='manifest id (sheet/class/warrior) 또는 등록된 시트 png 이름 (sheet_class_warrior)')
    ap.add_argument('--gait', choices=GAITS, help='run (전투 이동의 기본) | walk (느린 걸음: 터벅터벅·뒷걸음·한 발짝)')
    ap.add_argument('--src', nargs='+', help='띠 png 들 (프레임 순서대로: <set>_a.png <set>_b.png) 또는 .aseprite 하나')
    ap.add_argument('--stride', type=float, help='한 걸음에 가는 게임 px (n 프레임 = 두 걸음). 없으면 --pose 의 step_px x 시트 배율')
    ap.add_argument('--pose', help='그 세트의 pose.json (step_px, nominal_ms). 기본: 원본 옆의 pose.json')
    ap.add_argument('--ms', type=int, help='프레임 시간 ms (기본: .aseprite 의 프레임 시간 → pose.json nominal_ms → run 80 / walk 120)')
    ap.add_argument('--floor', type=int, default=FLOOR, help=f'원본의 바닥 줄 = 디딘 발의 맨 아래 픽셀 y (기본 {FLOOR}; 모든 프레임에 같은 값)')
    ap.add_argument('--center', type=int, default=SLOT // 2, help=f'한 프레임 안의 엉덩이 중심 열 x (기본 {SLOT // 2})')
    ap.add_argument('--scale', type=float, help='원본 → 게임 배율 (기본: 요청서 phase3.json 의 scale)')
    ap.add_argument('--remove', action='store_true', help='그 이동 칸을 뺀다')
    ap.add_argument('--reattach', action='store_true', help='기록은 있는데 칸이 없는 이동 동작을 기록된 원본에서 다시 붙인다')
    ap.add_argument('--dry-run', action='store_true', help='시트·manifest 를 바꾸지 않고 --work 에 결과만 쓴다')
    ap.add_argument('--work', help='새 시트·항목·미리보기를 둘 폴더 (--dry-run 에서는 여기에만 쓴다)')
    ap.add_argument('--allow-draft', action='store_true', help='시험용: 초안·가이드(뼈대 마네킹 포함) 원본도 처리한다. 언제나 --dry-run')
    ap.add_argument('--allow-below', action='store_true', help='바닥 줄 아래로 내려가는 프레임을 받는다 (기본: 실패). 기록에 남아 다시 붙일 때도 쓴다')
    ap.add_argument('--aseprite-bin', help='Aseprite 실행 파일 (기본: $ASEPRITE_PATH, tools/art/ase_headless.sh, $ASEPRITE, PATH)')
    ap.add_argument('--extra-guides', action='append', default=[], metavar='DIR',
                    help='마네킹 비교에 더할 폴더 (.aseprite·띠 png; receive.py 가 origin/art-inbox 의 art/inbox/guides/ 를 꺼내 넘긴다)')
    a = ap.parse_args(argv)
    EXTRA_GUIDES[:] = [os.path.abspath(d) for d in a.extra_guides]
    try:
        man = load_manifest()
        sid = resolve_sheet(a.sheet, man)
        if a.reattach:
            return reattach(sid, man, a)
        if not a.gait:
            raise Fail('--gait run|walk 가 필요하다')
        if a.remove:
            log(f'{sid}: {a.gait} 칸 빼기')
            remove(sid, man, a.gait, a)
            return 0
        if not a.src:
            raise Fail('--src 가 필요하다 (띠 png 들 또는 .aseprite)')
        log(f'{sid}: {a.gait} ← {", ".join(a.src)}')
        if a.allow_draft:
            a.dry_run = True
        for p in a.src:
            if not os.path.exists(p):
                raise Fail(f'원본이 없다: {p}')
        if draft_guard(a.src, a.allow_draft, a.aseprite_bin):
            a.dry_run = True
        rec = {'src': [rel(p) for p in a.src], 'floor': a.floor, 'center': a.center}
        if a.scale:
            rec['scale'] = a.scale
        if a.allow_below:
            rec['allow_below'] = True
        if a.ms:
            rec['ms'] = a.ms
        pose = a.pose
        if not pose and a.stride is None:
            near = os.path.join(os.path.dirname(os.path.abspath(a.src[0])), 'pose.json')
            if os.path.exists(near):
                pose = near
                log(f'  한 걸음: 원본 옆의 {rel(near)} 에서')
        if a.stride is not None:
            if a.stride <= 0:
                raise Fail('--stride 는 0 보다 커야 한다')
            rec['stride'] = a.stride
            if pose:
                rec['pose'] = rel(pose)
        elif pose:
            try:
                with open(pose, encoding='utf-8') as f:
                    guide = json.load(f)
            except (OSError, ValueError) as e:
                raise Fail(f'{pose}: 읽을 수 없는 pose.json ({e})') from e
            step = guide.get('step_px') if isinstance(guide, dict) else None
            if not step:
                raise Fail(f'{pose} 에 step_px 가 없다 — --stride 로 줄 것')
            rec['pose'], rec['step_px'] = rel(pose), step
        else:
            raise Fail('한 걸음을 알 수 없다: --stride 게임px 또는 --pose pose.json (step_px)')
        attach(sid, man, a.gait, rec, a)
        return 0
    except Fail as e:
        print(f'add_gait: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
