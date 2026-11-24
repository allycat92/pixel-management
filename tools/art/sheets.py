#!/usr/bin/env python3
"""전투 캐릭터 시트 파이프라인: art/inbox/sheet_*.png → 80x80 칸 스프라이트 시트 → manifest 등록.

입력 (그림 모델이 그린 것, 배경은 단색 크로마 #FF00FF 권장 / 투명도 가능):
  - 한 장에 한 자세 (전신 1명)            → idle (숨쉬기 루프는 여기서 만든다)
  - 1x4 가로 띠 또는 2x2 격자 (핵심 자세 4개) → idle, 공격 준비, 공격 타격, 피격
    (자세가 2개면 idle·타격, 3개면 idle·타격·피격)
  자세 수와 배치는 그림 덩어리의 위치로 자동으로 찾는다 (--grid 4x1 / 2x2 / 1x1 로 강제 가능).

처리 (칸마다):
  배경 제거(테두리 색을 키로 한 부드러운 알파 + 색 번짐 제거) → 자르기
  → idle 자세 높이를 기준으로 모든 자세를 같은 배율로 축소 (캐릭터 키 약 64px)
  → 알파 0.45 기준 이진화, 외톨이 점 제거·1px 구멍 메우기
  → 가장자리 1px 를 어두운 보라(18,16,26) 쪽으로 → 외곽까지 포함한 시트 전체 공통 팔레트(--colors, 기본 40색)로 한 번 양자화
  → 80x80 칸에 발바닥 가운데를 (40,76)에 맞춰 배치
  → idle 은 sprite-gen breathe --mode pixel 로 4칸 숨쉬기 루프 (없으면 간단한 1px 들썩임)
  → 시트 png + Aseprite json-array(태그 idle/attack/hit) → tools/art/register_sheet.py 로 등록.

실행:
  python3 tools/art/sheets.py                          # art/inbox/sheet_*.png 전부
  python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png
  옵션: --id ID  --grid CxR  --flip  --height 64  --colors 40  --work DIR
        --dry-run (manifest 를 건드리지 않음)  --no-register  --aseprite OUT.aseprite
필요: Pillow + NumPy (sprite-gen venv 가 있으면 숨쉬기 루프에 쓴다)
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
INBOX = os.path.join(ROOT, 'art', 'inbox')
REQ_DIR = os.path.join(ROOT, 'art', 'requests')
REGISTER = os.path.join(ROOT, 'tools', 'art', 'register_sheet.py')
SG_LOCAL = os.path.join(ROOT, 'tools', 'sprite-gen', '.venv', 'bin', 'sprite-gen')

CELL = 80                    # 칸 크기 (큰 괴물은 요청서의 cell 로 키운다)
ANCHOR = (40, 76)            # 칸 안의 발바닥 가운데 = (CELL/2, CELL-4)
OUTLINE = np.array([18, 16, 26], dtype=np.float32)
POSES = {1: ['idle'], 2: ['idle', 'strike'], 3: ['idle', 'strike', 'hit'], 4: ['idle', 'windup', 'strike', 'hit']}
DUR = {'idle': 240, 'windup': 150, 'strike': 260, 'hit': 220}
FILE_RE = re.compile(r'^sheet_(captain|hero|class|monster)_([A-Za-z0-9-]+?)(?:@[A-Za-z0-9-]+)?\.png$')


def log(*a):
    print(*a, flush=True)


# ───────── 배경 제거 ─────────

def key_color(arr):
    """테두리 픽셀의 중앙값 색. 테두리가 대부분 투명이면 None (이미 투명 배경)."""
    border = np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]])
    if (border[:, 3] < 128).mean() > 0.5:
        return None
    opaque = border[border[:, 3] >= 128, :3]
    return np.median(opaque, axis=0)


def matte(arr, lo=60.0, hi=140.0):
    """RGBA uint8 → (rgb float 0..255 un-premultiplied, alpha float 0..1)."""
    rgb = arr[..., :3].astype(np.float32)
    a0 = arr[..., 3].astype(np.float32) / 255.0
    key = key_color(arr)
    if key is None:
        return rgb, a0, None
    dist = np.sqrt(((rgb - key) ** 2).sum(-1))
    a = np.clip((dist - lo) / (hi - lo), 0, 1) * a0
    # 키 색이 섞여 있던 반투명 가장자리의 색을 되돌린다 (un-premultiply / despill)
    safe = np.maximum(a, 1e-3)[..., None]
    rgb = np.clip((rgb - (1 - a)[..., None] * key) / safe, 0, 255)
    rgb[a <= 0] = 0
    return rgb, a, key


# ───────── 자세 나누기 ─────────

def _dilate(m, r):
    out = m.copy()
    for _ in range(r):
        o = out.copy()
        o[1:] |= out[:-1]; o[:-1] |= out[1:]; o[:, 1:] |= out[:, :-1]; o[:, :-1] |= out[:, 1:]
        out = o
    return out


def _label(m):
    """4-연결 성분 번호 매기기 (작은 격자용, scipy 없이)."""
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if lab[y0, x0]:
            continue
        n += 1
        stack = [(y0, x0)]
        lab[y0, x0] = n
        while stack:
            y, x = stack.pop()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    stack.append((yy, xx))
    return lab, n


def _merge(intervals):
    out = []
    for lo, hi in sorted(intervals):
        if out and lo <= out[-1][1]:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return out


def _fit_bands(bands, want, proj):
    """한 줄 배치에서 띠 수를 want 에 맞춘다: 많으면 가장 가까운 둘을 합치고,
    적으면 가장 넓은 띠를 가운데 부근의 가장 옅은 열에서 자른다."""
    bands = [list(b) for b in bands]
    while len(bands) > want:
        gaps = [bands[i + 1][0] - bands[i][1] for i in range(len(bands) - 1)]
        i = int(np.argmin(gaps))
        bands[i:i + 2] = [[bands[i][0], bands[i + 1][1]]]
    while len(bands) < want:
        i = int(np.argmax([b[1] - b[0] for b in bands]))
        lo, hi = bands[i]
        a, b = lo + int((hi - lo) * 0.2), lo + int((hi - lo) * 0.8)
        if b - a < 2:
            break
        cut = a + int(np.argmin(proj[a:b]))
        bands[i:i + 1] = [[lo, cut], [cut + 1, hi]]
    return bands


def _cluster_bands(row_big, want, lo, hi):
    """한 줄의 큰 덩어리들을 가운데 x 로 정렬해 가장 큰 틈 (want-1)곳에서 나눈다.
    덩어리의 x 범위가 사슬처럼 겹쳐도(넓게 벌린 자세 넷이 1536px 에 빠듯하게 선 띠) 자세별로 갈린다.
    띠 경계는 이웃한 두 무리의 오른쪽 끝·왼쪽 끝 가운데 (겹치면 겹친 곳의 가운데)."""
    cs = sorted(row_big, key=lambda c: c['cx'])
    k = min(want, len(cs))
    gaps = [cs[i + 1]['cx'] - cs[i]['cx'] for i in range(len(cs) - 1)]
    cuts = sorted(int(i) for i in np.argsort(gaps)[::-1][:k - 1]) if k > 1 else []
    groups, start = [], 0
    for i in cuts:
        groups.append(cs[start:i + 1])
        start = i + 1
    groups.append(cs[start:])
    edges = [lo]
    for g0, g1 in zip(groups, groups[1:]):
        edges.append((max(c['x1'] for c in g0) + min(c['x0'] for c in g1)) / 2)
    edges.append(hi)
    return [[edges[i], edges[i + 1]] for i in range(len(groups))]


def split_poses(alpha, grid=None, expect=None, guess=False):
    """alpha(HxW float) → 자세별 마스크 목록 (행 우선 순서).
    grid=(cols, rows) 이면 그 격자, expect=N 이면 한 줄 띠를 N 개로 맞춘다.
    guess=True 는 expect 가 그림 비율로 짐작한 값이라는 뜻: 키가 비슷한 큰 덩어리가 3개 이상일 때만 띠로 본다
    (전신 1명 + 떨어진 불꽃·구슬·늑대 같은 그림을 자세 여럿으로 쪼개지 않게)."""
    H, W = alpha.shape
    f = max(1, int(np.ceil(max(H, W) / 640)))
    h, w = -(-H // f), -(-W // f)
    pad = np.zeros((h * f, w * f), bool)
    pad[:H, :W] = alpha > 0.5
    small = pad.reshape(h, f, w, f).any(axis=(1, 3))
    lab, n = _label(_dilate(small, 1))
    if n == 0:
        return []
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero((lab == i) & small)
        if len(ys) == 0:
            continue
        comps.append({'id': i, 'area': len(ys), 'cx': xs.mean(), 'cy': ys.mean(),
                      'x0': xs.min(), 'x1': xs.max() + 1, 'y0': ys.min(), 'y1': ys.max() + 1})
    big_area = max(c['area'] for c in comps)
    comps = [c for c in comps if c['area'] >= 0.003 * big_area]  # 먼지·점 제거
    big = [c for c in comps if c['area'] >= 0.08 * big_area]
    if guess and expect and expect > 1:
        tall = max(c['y1'] - c['y0'] for c in big)
        alike = [c for c in big if (c['y1'] - c['y0']) >= 0.7 * tall]
        wide = any((c['x1'] - c['x0']) >= 2.2 * (c['y1'] - c['y0']) for c in alike)  # 자세 여럿이 칼끝 등으로 붙은 한 덩어리
        if len(alike) < 3 and not wide:
            log(f'  가로로 긴 그림이지만 키가 비슷한 덩어리가 {len(alike)}개뿐 — 한 자세로 본다 (여러 자세면 --poses 4 / --grid 4x1)')
            expect = 1
    def slot(v, bands):
        for i, (lo, hi) in enumerate(bands):
            if lo <= v < hi:
                return i
        return int(np.argmin([min(abs(v - lo), abs(v - hi)) for lo, hi in bands]))

    if grid:
        cols, rows = grid
        rowb = [[h * i / rows, h * (i + 1) / rows] for i in range(rows)]
        colbs = [[[w * i / cols, w * (i + 1) / cols] for i in range(cols)]] * rows
    else:
        rowb = _merge([[c['y0'], c['y1']] for c in big])
        colbs = []
        for r, (lo, hi) in enumerate(rowb):  # 줄마다 따로 열을 찾는다 (2x2 격자에서 위아래 칸이 어긋나도 된다)
            row_big = [c for c in big if slot(c['cy'], rowb) == r]
            colb = _merge([[c['x0'], c['x1']] for c in row_big])
            want = expect if len(rowb) == 1 else (expect // len(rowb) if expect and expect % len(rowb) == 0 else None)
            if want and want > 1 and len(colb) != want and (len(row_big) >= 2 or len(rowb) == 1):
                # 덩어리 가운데 x 로 묶는다 (x 범위가 겹쳐 한 띠로 합쳐진 경우도). 덩어리가 모자라면(서로 붙은 자세) 가장 넓은 띠를 가장 옅은 열에서 더 자른다.
                log(f'  {r + 1}번째 줄에서 자세 {len(colb)}개를 찾았지만 {want}개를 기대 — 덩어리 {len(row_big)}개를 가운데 위치로 다시 나눈다')
                colb = _cluster_bands(row_big, want, 0, w)
                if len(colb) < want:
                    colb = _fit_bands([[max(lo_, min(c['x0'] for c in row_big)), min(hi_, max(c['x1'] for c in row_big))] if len(colb) == 1 else [lo_, hi_] for lo_, hi_ in colb],
                                      want, small[int(lo):int(hi)].sum(0))
            elif want and len(colb) not in (1, want) or (want and len(colb) == 1 and len(rowb) > 1 and want > 1):
                log(f'  {r + 1}번째 줄에서 자세 {len(colb)}개를 찾았지만 {want}개를 기대 — 띠를 다시 나눈다')
                colb = _fit_bands(colb, want, small[int(lo):int(hi)].sum(0))
            colbs.append(colb)
        layout = [len(c) for c in colbs]
        if expect == 1 or (expect is None and layout != [2, 2]) or (expect and len(rowb) > 2):
            if sum(layout) > 1:
                log(f'  덩어리 배치 {layout} — 한 자세로 본다 (여러 자세면 --grid 4x1 / 2x2)')
            rowb, colbs = [[0, h]], [[[0, w]]]

    # 덩어리 하나가 띠 여럿의 가운데를 덮으면(자세끼리 칼끝·머리띠로 붙은 경우) 띠 경계에서 세로로 자른다.
    # 그 밖의 덩어리는 가운데 x 가 든 띠에 통째로 들어간다 (옆 칸으로 삐친 칼끝도 제 자세에 남는다).
    groups, cuts = {}, {}
    for c in comps:
        r = slot(c['cy'], rowb)
        bands = colbs[r]
        covered = [i for i, (lo_, hi_) in enumerate(bands) if c['x0'] <= (lo_ + hi_) / 2 < c['x1']]
        if len(bands) > 1 and len(covered) > 1:
            for i in covered:
                groups.setdefault((r, i), [])
                cuts.setdefault((r, i), []).append(c['id'])
        else:
            groups.setdefault((r, slot(c['cx'], bands)), []).append(c['id'])
    lab_full = np.repeat(np.repeat(lab, f, 0), f, 1)[:H, :W]
    xs_full = np.arange(W)[None, :]
    masks = []
    for key in sorted(groups):
        m = np.isin(lab_full, groups[key])
        if key in cuts:
            lo_, hi_ = colbs[key[0]][key[1]]
            m |= np.isin(lab_full, cuts[key]) & (xs_full >= lo_ * f) & (xs_full < hi_ * f)
        masks.append(m)
    log(f'  배치: {"+".join(str(len(c)) for c in colbs)}열 x {len(rowb)}행 → 자세 {len(masks)}개')
    return masks


# ───────── 축소 · 정리 ─────────

def bbox(a, t=0.02):
    ys, xs = np.nonzero(a > t)
    if len(ys) == 0:
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def body_height(a):
    """몸 높이: 가장 큰 덩어리(떠 있는 구슬·이펙트 조각은 뺀다)에서, 불투명 폭이 가장 넓은 줄의
    12% 이상인 줄들의 위아래 끝 (머리 위로 솟은 가는 칼끝·창끝도 뺀다)."""
    m = a > 0.5
    H, W = m.shape
    f = max(1, int(np.ceil(max(H, W) / 256)))
    h, w = -(-H // f), -(-W // f)
    pad = np.zeros((h * f, w * f), bool)
    pad[:H, :W] = m
    small = pad.reshape(h, f, w, f).any(axis=(1, 3))
    lab, n = _label(_dilate(small, 1))
    if n > 1:
        sizes = np.bincount((lab * small).ravel())[1:]
        keep = np.repeat(np.repeat(lab == (int(sizes.argmax()) + 1), f, 0), f, 1)[:H, :W]
        m = m & keep
    rows = m.sum(1)
    ys = np.nonzero(rows >= rows.max() * 0.12)[0]
    return int(ys.max() - ys.min() + 1)


def box_resize(rgb, a, nw, nh):
    """premultiplied BOX 축소 → (rgb, alpha)."""
    def rs(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), 'F').resize((nw, nh), Image.Resampling.BOX))
    pa = rs(a)
    prgb = np.stack([rs(rgb[..., i] * a) for i in range(3)], -1)
    out = prgb / np.maximum(pa, 1e-4)[..., None]
    return np.clip(out, 0, 255), pa


def neighbours(m):
    p = np.pad(m, 1)
    n8 = sum(p[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]].astype(np.int32)
             for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    n4 = sum(p[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]].astype(np.int32)
             for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
    return n8, n4


def cleanup(rgb, mask):
    """외톨이 점 제거, 1px 구멍 메우기."""
    n8, _ = neighbours(mask)
    mask = mask & (n8 >= 1)
    n8, n4 = neighbours(mask)
    hole = (~mask) & (n4 == 4)
    if hole.any():
        p = np.pad(rgb * mask[..., None], ((1, 1), (1, 1), (0, 0)))
        s = sum(p[1 + dy:1 + dy + mask.shape[0], 1 + dx:1 + dx + mask.shape[1]] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
        rgb = np.where(hole[..., None], s / 4, rgb)
        mask = mask | hole
    return rgb, mask


def feet_x(mask):
    """가장 아래 6줄에서 불투명 픽셀의 왼쪽 끝·오른쪽 끝의 가운데."""
    ys, xs = np.nonzero(mask)
    band = ys >= ys.max() - 5
    return (xs[band].min() + xs[band].max() + 1) / 2


MAX_SHRINK = 0.85            # 칸에 맞추려고 이보다 더 줄여야 하면 실패 (자세가 잘못 나뉘었거나 여럿이 한 칸에 들어간 것)


def place(rgb, mask, label):
    """80x80 칸에 발 위치를 맞춰 넣는다. 조금 크면 줄이고, 15% 넘게 줄여야 하면 None (실패)."""
    h, w = mask.shape
    max_w, max_h = CELL - 2, ANCHOR[1] - 2
    if w > max_w or h > max_h:
        s = min(max_w / w, max_h / h)
        nw, nh = max(1, int(w * s)), max(1, int(h * s))
        if s < MAX_SHRINK:
            log(f'  실패: {label} 자세가 칸보다 훨씬 커서({w}x{h}) {nw}x{nh} 로 줄여야 한다 — 자세 나누기가 틀렸을 수 있다 (--grid / --poses 로 지정)')
            return None
        log(f'  주의: {label} 자세가 칸보다 커서({w}x{h}) {nw}x{nh} 로 줄였다')
        rgb = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((nw, nh), Image.Resampling.NEAREST)).astype(np.float32)
        mask = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((nw, nh), Image.Resampling.NEAREST)) > 127
        h, w = mask.shape
    fx = feet_x(mask)
    x0 = int(round(ANCHOR[0] - fx))
    x0 = min(max(x0, 1), CELL - 1 - w)
    ys = np.nonzero(mask.any(1))[0]
    y0 = ANCHOR[1] - 1 - ys.max()
    cell = np.zeros((CELL, CELL, 4), np.uint8)
    cell[y0:y0 + h, x0:x0 + w, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    cell[y0:y0 + h, x0:x0 + w, 3] = mask * 255
    cell[..., :3][cell[..., 3] == 0] = 0
    return cell


def build_palette(pixels, colors):
    pix = pixels.astype(np.uint8).reshape(1, -1, 3)
    q = Image.fromarray(pix, 'RGB').quantize(colors=colors, method=Image.Quantize.FASTOCTREE, kmeans=3,
                                             dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:3 * colors], np.float32).reshape(-1, 3)
    used = np.unique(np.asarray(q))
    return pal[used]


def snap(rgb, pal):
    flat = rgb.reshape(-1, 3)
    idx = np.empty(len(flat), np.int64)
    for i in range(0, len(flat), 20000):
        d = ((flat[i:i + 20000, None, :] - pal[None]) ** 2).sum(-1)
        idx[i:i + 20000] = d.argmin(1)
    return pal[idx].reshape(rgb.shape)


def outline(rgb, mask):
    """투명과 맞닿은 가장자리 1px 를 어두운 보라 쪽으로 (선택적 외곽선)."""
    _, n4 = neighbours(mask)
    edge = mask & (n4 < 4)
    rgb = rgb.copy()
    rgb[edge] = rgb[edge] * 0.45 + OUTLINE * 0.55
    return rgb


# ───────── 숨쉬기 ─────────

def sprite_gen_bin():
    if os.path.exists(SG_LOCAL):
        return SG_LOCAL
    return shutil.which('sprite-gen')


def breathe(cell, work, n=4):
    src, dst = os.path.join(work, 'idle_src'), os.path.join(work, 'idle_breathe')
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(src)
    for i in range(n):
        Image.fromarray(cell).save(os.path.join(src, f'idle_{i}.png'))
    sg = sprite_gen_bin()
    if sg:
        r = subprocess.run([sg, 'breathe', src, dst, '--mode', 'pixel'], capture_output=True, text=True)
        if r.returncode == 0:
            return [np.asarray(Image.open(os.path.join(dst, f'idle_{i}.png')).convert('RGBA')) for i in range(n)]
        log('  주의: sprite-gen breathe 실패 — 간단한 들썩임으로 대신한다:', (r.stderr or r.stdout).strip()[-300:])
    else:
        log('  주의: sprite-gen 이 없다 (tools/sprite-gen/.venv) — 간단한 들썩임으로 대신한다')
    # 대체: 허리 위를 1px 내렸다 올린다
    ys = np.nonzero(cell[..., 3].any(1))[0]
    waist = ys.min() + int((ys.max() - ys.min()) * 0.55)
    out = []
    for i in range(n):
        c = cell.copy()
        if i in (1, 2):
            top = cell[:waist].copy()
            c[:waist] = 0
            c[1:waist + 1][top[:waist][..., 3] > 0] = top[top[..., 3] > 0]
        out.append(c)
    return out


# ───────── 시트 · json · aseprite ─────────

def assemble(frames, tags, name):
    cols = 4
    rows = -(-len(frames) // cols)
    sheet = np.zeros((rows * CELL, cols * CELL, 4), np.uint8)
    fr_json = []
    for i, (img, dur) in enumerate(frames):
        x, y = (i % cols) * CELL, (i // cols) * CELL
        sheet[y:y + CELL, x:x + CELL] = img
        fr_json.append({'filename': f'{name} {i}.aseprite', 'frame': {'x': x, 'y': y, 'w': CELL, 'h': CELL},
                        'rotated': False, 'trimmed': False,
                        'spriteSourceSize': {'x': 0, 'y': 0, 'w': CELL, 'h': CELL},
                        'sourceSize': {'w': CELL, 'h': CELL}, 'duration': dur})
    colors = {'idle': '#5aa05aff', 'walk': '#5a78c8ff', 'attack': '#c85046ff', 'hit': '#dcc850ff', 'cast': '#9b6ad6ff'}
    data = {'frames': fr_json, 'meta': {
        'app': 'tools/art/sheets.py', 'version': '1', 'image': f'{name}.png', 'format': 'RGBA8888',
        'size': {'w': sheet.shape[1], 'h': sheet.shape[0]}, 'scale': '1',
        'frameTags': [{'name': t, 'from': a, 'to': b, 'direction': 'forward', 'color': colors.get(t, '#888888ff')}
                      for t, a, b in tags]}}
    return sheet, data


def preview(sheet, path, z=4):
    h, w = sheet.shape[:2]
    bg = np.zeros((h, w, 4), np.uint8)
    bg[..., :3] = (44, 40, 48)
    bg[..., 3] = 255
    yy, xx = np.mgrid[0:h, 0:w]
    bg[((xx // 8 + yy // 8) % 2 == 0), :3] = (54, 50, 58)
    bg[(yy % CELL) == ANCHOR[1], :3] = (90, 60, 60)  # 발 기준선
    im = Image.fromarray(bg)
    im.alpha_composite(Image.fromarray(sheet))
    im.resize((w * z, h * z), Image.Resampling.NEAREST).save(path)


def find_aseprite(given):
    for c in (given, os.environ.get('ASEPRITE'), shutil.which('aseprite'),
              os.path.expanduser('~/aseprite-build/src/build/bin/aseprite')):
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def save_aseprite(frames, tags, out, work, binary):
    exe = find_aseprite(binary)
    if not exe:
        log('  --aseprite: Aseprite 실행 파일이 없어 건너뛴다 (ASEPRITE=경로 또는 --aseprite-bin)')
        return
    fdir = os.path.join(work, 'ase_frames')
    os.makedirs(fdir, exist_ok=True)
    for i, (img, _) in enumerate(frames):
        Image.fromarray(img).save(os.path.join(fdir, f'f{i:02d}.png'))
    durs = ','.join(f'{d / 1000:.3f}' for _, d in frames)
    tag_lua = '\n'.join(f'tag({a + 1},{b + 1},"{t}")' for t, a, b in tags)
    lua = f'''local src = app.params["src"]; local out = app.params["out"]
local spr = Sprite({CELL}, {CELL}, ColorMode.RGB)
local layer = spr.layers[1]; layer.name = "body"
local durs = {{{durs}}}
for i = 1, {len(frames)} do
  if i > 1 then spr:newEmptyFrame(i) end
  local img = Image{{ fromFile = string.format("%s/f%02d.png", src, i-1) }}
  spr:newCel(layer, i, img, Point(0,0))
  spr.frames[i].duration = durs[i]
end
local function tag(a,b,name) local t = spr:newTag(a,b); t.name = name end
{tag_lua}
spr:saveAs(out)
'''
    script = os.path.join(work, 'assemble.lua')
    with open(script, 'w') as f:
        f.write(lua)
    home = tempfile.mkdtemp(prefix='ase-home-')
    env = dict(os.environ, HOME=home, XDG_CONFIG_HOME=os.path.join(home, 'c'), ASEPRITE_USER_FOLDER=os.path.join(home, 'a'))
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run([exe, '-b', '--script-param', f'src={fdir}', '--script-param', f'out={out}', '--script', script],
                       capture_output=True, text=True, env=env, timeout=120)
    shutil.rmtree(home, ignore_errors=True)
    if r.returncode == 0 and os.path.exists(out):
        log(f'  aseprite: {out}')
    else:
        log('  --aseprite 실패:', (r.stderr or r.stdout).strip()[-300:])


# ───────── 요청서 → id ─────────

def request_map():
    """phase*.json 의 sheet 항목: 파일 이름 → {id, flip, grid}."""
    out = {}
    for p in sorted(glob.glob(os.path.join(REQ_DIR, 'phase*.json'))):
        with open(p, encoding='utf-8') as f:
            for it in json.load(f).get('items', []):
                if it.get('kind') == 'sheet':
                    out[it['file']] = it
    return out


def id_for(path, reqs):
    name = os.path.basename(path)
    base = re.sub(r'@[A-Za-z0-9-]+(?=\.png$)', '', name)  # sheet_x_y@nai1.png → 같은 요청
    if base in reqs:
        return reqs[base]['id']
    m = FILE_RE.match(name)
    if m and m.group(1) != 'monster':
        return f'sheet/{m.group(1)}/{m.group(2)}'
    return None


# ───────── 한 장 처리 ─────────

def process(path, sid, a, reqs):
    global CELL, ANCHOR
    log(f'{os.path.relpath(path, ROOT) if path.startswith(ROOT) else path} → {sid}')
    im = Image.open(path).convert('RGBA')
    if a.flip:
        im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    arr = np.asarray(im)
    rgb, alpha, key = matte(arr)
    log(f'  배경 키 색: {"투명" if key is None else "#%02x%02x%02x" % tuple(int(v) for v in key)}  ({im.width}x{im.height})')
    req = reqs.get(re.sub(r'@[A-Za-z0-9-]+(?=\.png$)', '', os.path.basename(path)), {})
    grid = tuple(int(v) for v in a.grid.lower().split('x')) if a.grid else None
    CELL = a.cell or req.get('cell') or 80
    ANCHOR = (CELL // 2, CELL - 4)
    height = a.height or req.get('height') or 64
    expect = a.poses
    guess = False
    if not grid and not expect and im.width >= 1.3 * im.height:
        expect, guess = 4, True  # 가로로 긴 그림 = 요청서의 1x4 띠 (키 비슷한 덩어리가 3개 이상일 때만)
    masks = split_poses(alpha, grid, expect if not grid else None, guess=guess)
    if not masks:
        log('  실패: 그림을 찾지 못했다')
        return False
    if len(masks) > 4:
        log(f'  주의: 자세가 {len(masks)}개 — 앞의 4개만 쓴다 (--grid 로 지정 가능)')
        masks = masks[:4]
    names = POSES[len(masks)]

    crops = []
    for m in masks:
        aa = alpha * m
        x0, y0, x1, y1 = bbox(aa)
        crops.append((rgb[y0:y1, x0:x1], aa[y0:y1, x0:x1]))
    # 모든 자세에 같은 배율: idle 의 몸 높이 → height
    body = body_height(crops[0][1])
    scale = height / body
    log(f'  배율 {scale:.4f} (idle 몸 높이 {body}px → {height}px, 칸 {CELL}x{CELL}; 머리 위로 솟은 가는 무기 끝은 빼고 잰다)')
    small = []
    for (c_rgb, c_a), nm in zip(crops, names):
        hh = body_height(c_a) * scale
        if nm != 'idle' and hh < height * 0.55:
            log(f'  실패: {nm} 자세 몸 높이 {hh:.0f}px 가 idle({height}px)의 절반 남짓도 안 된다 — 떨어진 조각(불꽃·구슬 등)이 자세로 잘린 듯하다 (--poses 1 / --grid 로 지정)')
            return False
        if nm != 'idle' and abs(hh - height) > height * 0.3 and nm != 'hit':
            log(f'  주의: {nm} 자세 높이 {hh:.0f}px — 칸마다 캐릭터 크기가 다르게 그려졌을 수 있다')
        nw = max(1, int(round(c_a.shape[1] * scale)))
        nh = max(1, int(round(c_a.shape[0] * scale)))
        s_rgb, s_a = box_resize(c_rgb, c_a, nw, nh)
        mask = s_a > a.alpha
        s_rgb, mask = cleanup(s_rgb, mask)
        bb = bbox(mask.astype(np.float32), 0.5)
        if bb is None:
            log(f'  실패: {nm} 자세가 축소 후 비었다')
            return False
        x0, y0, x1, y1 = bb
        small.append((s_rgb[y0:y1, x0:x1], mask[y0:y1, x0:x1]))

    # 외곽선(가장자리 어둡게)을 먼저 입힌 뒤 팔레트를 만들고 한 번만 양자화한다: 외곽 색도 공통 팔레트 안에 든다 (--colors 이하)
    if not a.no_outline:
        small = [(outline(r, m), m) for r, m in small]
    pal = build_palette(np.concatenate([r[m] for r, m in small]), a.colors)
    cells = {}
    for (s_rgb, mask), nm in zip(small, names):
        q = snap(s_rgb, pal)
        q[~mask] = 0
        cell = place(q, mask, nm)
        if cell is None:
            return False
        cells[nm] = cell
        hh = mask.shape[0]
        log(f'  {nm}: {mask.shape[1]}x{hh}px')

    work = a.work or tempfile.mkdtemp(prefix='sheet-')
    tag_name = re.sub(r'\s+', '-', sid.replace('/', '_'))
    wdir = os.path.join(work, tag_name)
    os.makedirs(wdir, exist_ok=True)
    for nm, c in cells.items():
        Image.fromarray(c).save(os.path.join(wdir, f'pose_{nm}.png'))

    frames, tags = [], []
    idle = breathe(cells['idle'], wdir)
    frames += [(f, DUR['idle']) for f in idle]
    tags.append(('idle', 0, len(idle) - 1))
    atk = [n for n in ('windup', 'strike') if n in cells]
    if atk:
        tags.append(('attack', len(frames), len(frames) + len(atk) - 1))
        frames += [(cells[n], DUR[n]) for n in atk]
    if 'hit' in cells:
        tags.append(('hit', len(frames), len(frames)))
        frames.append((cells['hit'], DUR['hit']))

    sheet, data = assemble(frames, tags, tag_name)
    png = os.path.join(wdir, f'{tag_name}.png')
    js = os.path.join(wdir, f'{tag_name}.json')
    Image.fromarray(sheet).save(png, optimize=True)
    with open(js, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
    prev = os.path.join(wdir, 'preview_x4.png')
    preview(sheet, prev)
    ncol = len(np.unique(sheet[sheet[..., 3] > 0][:, :3], axis=0))
    log(f'  시트 {sheet.shape[1]}x{sheet.shape[0]}, {len(frames)}칸, {ncol}색, 태그 '
        + ', '.join(f'{t}({b - a_ + 1})' for t, a_, b in tags))
    log(f'  작업 폴더: {wdir}  (미리보기 {prev})')

    if a.aseprite:
        out = a.aseprite
        if len(a.inputs) != 1 or os.path.isdir(out) or out.endswith('/'):
            out = os.path.join(out, f'{tag_name}.aseprite')
        save_aseprite(frames, tags, out, wdir, a.aseprite_bin)

    if a.no_register:
        return True
    cmd = [sys.executable, REGISTER, '--id', sid, '--png', png, '--json', js,
           '--anchor', f'{ANCHOR[0]},{ANCHOR[1]}', '--facing', '1']
    if req.get('file') and req.get('id') == sid:
        cmd += ['--file', req['file']]  # 요청서의 파일 이름 (괴물 id 에는 한글·빈칸이 있어 그대로 파일 이름으로 쓰지 않는다)
    if a.dry_run:
        cmd.append('--dry-run')
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if a.dry_run:
        out = '\n'.join(out.splitlines()[:3] + ['  ...'])
    log('  ' + out.replace('\n', '\n  '))
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('inputs', nargs='*', help='처리할 png (기본: art/inbox/sheet_*.png 전부)')
    ap.add_argument('--id', help='manifest id (입력이 하나일 때). 기본은 요청서/파일 이름에서 찾는다')
    ap.add_argument('--grid', help='자세 배치를 강제: 4x1 (가로 띠), 2x2, 1x1')
    ap.add_argument('--poses', type=int, choices=[1, 2, 3, 4], help='한 줄 띠의 자세 수 (기본: 가로로 긴 그림은 4, 아니면 자동)')
    ap.add_argument('--flip', action='store_true', help='왼쪽을 보고 그려진 그림을 뒤집는다')
    ap.add_argument('--height', type=int, help='idle 자세의 몸 높이 px (기본: 요청서, 없으면 64)')
    ap.add_argument('--cell', type=int, help='칸 크기 (기본: 요청서, 없으면 80; 발 위치는 칸 가운데·바닥 4px 위)')
    ap.add_argument('--colors', type=int, default=40, help='시트 공통 팔레트 색 수 (기본 40)')
    ap.add_argument('--alpha', type=float, default=0.45, help='축소 후 알파 기준 (기본 0.45)')
    ap.add_argument('--no-outline', action='store_true', help='가장자리 어둡게 하기를 끈다')
    ap.add_argument('--work', help='중간 결과·미리보기를 둘 폴더 (기본: 임시 폴더)')
    ap.add_argument('--dry-run', action='store_true', help='시트는 만들되 manifest 는 바꾸지 않는다')
    ap.add_argument('--no-register', action='store_true', help='register_sheet.py 를 부르지 않는다')
    ap.add_argument('--aseprite', metavar='PATH', help='태그가 붙은 .aseprite 도 저장 (Aseprite 가 있을 때만)')
    ap.add_argument('--aseprite-bin', help='Aseprite 실행 파일 경로 (기본: $ASEPRITE, PATH)')
    a = ap.parse_args()

    if not os.path.exists(REGISTER) and not a.no_register:
        sys.exit('tools/art/register_sheet.py 가 없다 (--no-register 로 시트만 만들 수 있다)')
    # 기본: art/inbox/sheet_*.png. 이름에 @ 가 붙은 후보(sheet_x_y@123.png)는 직접 지정할 때만.
    inputs = a.inputs or sorted(p for p in glob.glob(os.path.join(INBOX, 'sheet_*.png')) if '@' not in os.path.basename(p))
    a.inputs = inputs
    if not inputs:
        log('art/inbox/sheet_*.png 가 없다')
        return 0
    if a.id and len(inputs) != 1:
        sys.exit('--id 는 입력이 하나일 때만 쓸 수 있다')
    reqs = request_map()
    ok = bad = 0
    for p in inputs:
        sid = a.id or id_for(p, reqs)
        if not sid:
            log(f'{p}: id 를 알 수 없다 (요청서에 없는 파일 이름) — --id 로 지정할 것')
            bad += 1
            continue
        if process(os.path.abspath(p), sid, a, reqs):
            ok += 1
        else:
            bad += 1
    log(f'완료 {ok}, 실패 {bad}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
