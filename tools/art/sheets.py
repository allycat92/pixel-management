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
  → 80x80 칸에 발바닥 가운데를 (40,76)에 맞춰 배치 (발이 다 닿지 않은 공격·피격 자세와 네발짐승은 몸 무게중심을 idle 의 자리에: pose_feet_x)
  → idle 은 sprite-gen breathe --mode pixel 로 4칸 숨쉬기 루프 (없으면 간단한 1px 들썩임)
  → 시트 png + Aseprite json-array(태그 idle/attack/hit) → tools/art/register_sheet.py 로 등록.
  직업 시트(요청서 항목에 tint 가 있으면): 제복·장식 열쇠 색에 가까운 픽셀(RGB 거리 <= KEY_TOL)을 원본 해상도에서 찾아
  축소 뒤에도 열쇠 색 그대로 남기고(다른 색은 열쇠 색이 되지 않는다), 열쇠 색을 register_sheet.py --tint-* 로 넘긴다.
  작업 폴더의 preview_tint_x4.png = 전투처럼 시험 색(빨강 제복·노랑 장식)으로 바꿔 칠한 미리보기.

실행:
  python3 tools/art/sheets.py                          # art/inbox/sheet_*.png 전부
  python3 tools/art/sheets.py art/inbox/sheet_captain_blademaster.png
  python3 tools/art/sheets.py --realign [--dry-run] [sheet/monster/들늑대 ...]   # 등록된 시트의 공격·피격 칸 발 맞추기만 다시
  옵션: --id ID  --grid CxR  --flip  --height 64 | --scale 0.1654  --cell 96  --colors 40  --work DIR
        --dry-run (manifest 를 건드리지 않음)  --no-register  --aseprite OUT.aseprite  --no-tint
  요청서 항목의 scale · cell · height · layout(2x2) · tint · spots(눈처럼 작아도 남길 점 색) 를 기본값으로 쓴다 (명령줄 옵션이 우선).
NovelAI 그림은 거부한다 (주인 결정: NovelAI 는 디자인 초안 전용, 게임 그림은 언제나 GPT 를 거친다):
  PNG 메타데이터의 NovelAI 표시, art/concepts/·art/requests/·drafts/ 안의 파일, nai_*.png 이름.
  --allow-draft = 파이프라인 시험용, 언제나 --dry-run 이라 manifest 에 등록할 수 없다.
뼈대(마네킹) 그림도 거부한다 (마네킹은 PC 가 만드는 자세 가이드, 게임 그림이 아니다 — add_gait.py 와 같은 규칙): 경로에 guides 폴더,
  옆에 pose_measured.json (check_skeleton --export / receive.py 가 마네킹에서 뽑은 프레임), 또는 어느 자세(좌우로 뒤집은 것도)의 실루엣이
  뼈대 프레임(art/requests/guides/ 초안, art/inbox/guides/ 와 origin/art-inbox 의 PC 마네킹)과 그림 상자의 아래 가운데를 맞추고
  ±24px 더 찾아(그림 높이를 뼈대 프레임에 맞춘 것도) IoU > 0.9. 높이 1024·너비 384 의 배수인 그림은 384 칸으로, 그 밖의 그림은
  split_poses 로 나눈 자세로 잰다. --allow-draft 로만 (언제나 --dry-run) 처리한다.
달리기·걷기 프레임은 tools/art/add_gait.py 가 등록된 시트에 붙인다 (이 파일의 shrink_pose · paint_pose 를 같이 쓴다).
  시트를 다시 등록하면 register_sheet.py 가 그 칸을 기록된 원본에서 다시 붙인다 (원본이 없으면 크게 경고). --realign 은 그 칸을 밀지 않는다.
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
KEY_TOL = 34.0               # 열쇠 색으로 볼 RGB 거리 (열쇠 색끼리는 43 이상, 다른 재질과는 그보다 멀게 고른다: art/requests/archive/phase3_gpt_log.md 메시지 D)
SPOT_TOL = 40.0              # 점 색(눈 등)으로 볼 RGB 거리 — spot_layer
SPOT_MIN = 0.3               # 게임 px 하나에서 점 색이 이만큼 덮으면 그 px 를 점 색으로
SPOT_BLOB_MIN = 0.08         # 게임 해상도에서 이어진 점 색 덩어리의 덮인 넓이 합이 이보다 작으면 티끌로 보고 버린다 (원본 ~3px)
KEY_SPECK_R = 0.33           # 열쇠 색 점 지우기: 몸통으로 볼 최소 두께의 절반 (게임 px) — clean_key_specks
KEY_SPECK_REACH = 0.66       # 몸통에서 이만큼(게임 px) 안의 가는 열쇠 선은 남긴다
LONE_KEY_N8 = 1              # 게임 해상도: 8 이웃 중 열쇠 픽셀이 이 수 이하인 열쇠 픽셀은 뺀다 (외톨이·두 점짜리 부스러기)
KEY_MIN_SHARE = 0.04         # 대기 자세에서 제복 열쇠 색이 이 비율보다 적으면 경고 (열쇠 색으로 칠하지 않은 그림)
TINT_TEST = {'outfit': '#b03a2e', 'accent': '#e0b040'}   # preview_tint_x4.png 의 시험 색


def log(*a):
    print(*a, flush=True)


# ───────── NovelAI 초안 막기 ─────────
# 주인 결정: NovelAI 는 디자인 초안 전용, 게임 그림은 언제나 GPT 를 거친다. NovelAI 그림은 시트로 등록하지 않는다.
DRAFT_DIRS = [os.path.join(ROOT, 'art', 'concepts'), os.path.join(ROOT, 'art', 'requests')]


def novelai_draft_reason(path):
    """NovelAI 초안으로 보이면 그 이유, 아니면 None.
    - PNG 메타데이터에 NovelAI 흔적 (NovelAI 가 넣는 Software: NovelAI / Source: NovelAI Diffusion ..., 프롬프트 json 의 nai-diffusion)
    - 초안 자리: art/concepts/ (고른 초안·drafts/), art/requests/ (꾸러미의 concept.png), 경로에 drafts 폴더
    - 이름: nai_*.png (tools/art/novelai.py 가 만드는 이름)"""
    real = os.path.realpath(path)
    for d in DRAFT_DIRS:
        d = os.path.realpath(d)
        if real.startswith(d + os.sep):
            return f'초안 폴더 {os.path.relpath(d, ROOT)}/ 안의 파일'
    parts = real.split(os.sep)
    if 'drafts' in parts[:-1]:
        return 'drafts/ 폴더 안의 파일'
    if os.path.basename(real).lower().startswith('nai_'):
        return '이름이 nai_ (novelai.py 초안)'
    try:
        with Image.open(path) as im:
            meta = ' '.join(str(v) for v in im.info.values() if isinstance(v, (str, bytes)))
    except OSError:
        return None
    if 'novelai' in meta.lower() or 'nai-diffusion' in meta.lower():
        return 'PNG 메타데이터에 NovelAI 생성 표시'
    return None


def mannequin_reason(path, exe=None):
    """뼈대(마네킹) 그림으로 보이면 그 이유, 아니면 None (add_gait.py 의 마네킹 막기를 시트 원본에도):
    - 경로에 guides 폴더 (art/requests/guides/<id>/…, art/inbox/guides/<id>/…)
    - 옆에 pose_measured.json (check_skeleton.py --export · receive.py 가 마네킹 .aseprite 에서 뽑은 프레임 png)
    - 어느 자세(또는 좌우로 뒤집은 것)의 실루엣이 뼈대 프레임과 자리를 맞춰(크기를 뼈대 프레임의 그림 높이로 맞춘 것도) IoU > 0.9
      (add_gait.best_guide_match / draft_masks: 클라우드 초안, 작업 트리와 origin/art-inbox 의 art/inbox/guides/ 마네킹)
    Aseprite 가 없어 마네킹 .aseprite 를 비교 대상으로 읽지 못하면 그 이유를 돌려준다 (비교 없이 받지 않는다)."""
    real = os.path.realpath(path)
    if 'guides' in real.split(os.sep)[:-1]:
        return 'guides/ 폴더 안의 파일 = 뼈대 가이드(마네킹)'
    if os.path.exists(os.path.join(os.path.dirname(real), 'pose_measured.json')):
        return '옆에 pose_measured.json — 마네킹 .aseprite 에서 뽑은 프레임 (check_skeleton.py --export / receive.py)'
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import add_gait as ag
    try:
        arr = np.asarray(Image.open(path).convert('RGBA'))
    except OSError:
        return None
    if arr.shape[0] == 1024 and arr.shape[1] % ag.SLOT == 0:      # 뼈대 규격의 띠: 384 칸 그대로 (add_gait 와 같은 자르기)
        frames, masks = [arr[:, k * ag.SLOT:(k + 1) * ag.SLOT] for k in range(arr.shape[1] // ag.SLOT)], None
    else:                                                          # 그 밖의 시트: 자세를 나눠 실루엣으로
        alpha = matte(arr)[1]
        g = globals()
        say, g['log'] = g['log'], (lambda *a_: None)                # 자세 나누기 기록은 처리 때 한 번만
        try:
            wide = arr.shape[1] >= 1.3 * arr.shape[0]
            parts = split_poses(alpha, None, 4 if wide else None, guess=wide)
        finally:
            g['log'] = say
        frames, masks = None, [m & (alpha > 0.5) for m in parts]
    try:
        iou, fi, name, flip, (dx, dy), k = ag.best_guide_match(frames, exe, stop=ag.DRAFT_IOU, masks=masks)
    except ag.Fail as e:
        return f'마네킹 비교를 하지 못했다 ({e})'
    if iou > ag.DRAFT_IOU:
        return (f'{fi}번 자세의 실루엣이 뼈대(마네킹)와 겹친다 — 맞은 마네킹: {name}, IoU {iou:.3f} > {ag.DRAFT_IOU} '
                f'(아래 가운데를 맞추고 {dx:+d},{dy:+d}px 옮겨서{", 좌우를 뒤집어서" if flip else ""}'
                f'{f", 그림 높이를 x{k:.3f} 로 맞춰서" if k else ""})')
    return None


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


def _label(m, diag=False):
    """4-연결(diag=True 면 8-연결) 성분 번호 매기기 (작은 격자용, scipy 없이)."""
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
            nb = ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))
            if diag:
                nb += ((y + 1, x + 1), (y + 1, x - 1), (y - 1, x + 1), (y - 1, x - 1))
            for yy, xx in nb:
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


def feet_band(mask):
    """가장 아래 6줄에서 불투명 픽셀의 왼쪽 끝·오른쪽 끝 (x0, x1)."""
    ys, xs = np.nonzero(mask)
    band = ys >= ys.max() - 5
    return xs[band].min(), xs[band].max() + 1


def feet_x(mask):
    """가장 아래 6줄에서 불투명 픽셀의 왼쪽 끝·오른쪽 끝의 가운데."""
    x0, x1 = feet_band(mask)
    return (x0 + x1) / 2


def mass_x(mask):
    """불투명 픽셀의 가로 무게중심."""
    return float(np.nonzero(mask)[1].mean())


# 자세별 발 맞추기 (idle 이 아닌 자세):
#  보통은 가장 아래 줄(발바닥)의 가운데를 앵커에 둔다. 그런데 발이 다 땅에 닿지 않은 자세는 '가장 아래 픽셀'이 발이 아니다 —
#  덮치는 늑대는 뒷발 끝만, 뒷발로 선 늑대는 뒷발만, 한 발로 선 피격 자세는 그 발끝이나 늘어뜨린 칼끝만 남는다.
#  그 가운데를 앵커에 맞추면 몸 전체가 앞으로 몇십 px 튀어 나간다 (전투에서 늑대가 '뛰어오르는' 것처럼 보였다).
#  그런 자세와 네발짐승(가로로 긴 몸)의 모든 자세는 몸의 무게중심을 idle 의 무게중심 자리에 둔다:
#  몸은 제자리에서 웅크리고 뻗고, 앞으로 내딛는 움직임은 게임이 공격 순간에 몸을 앞으로 밀어 그린다 (battle.js lunge).
NARROW_BASE = 0.5            # 자세의 발바닥 띠가 idle 띠의 이 배보다 좁으면 '발이 다 닿지 않은 자세'


def align_ref(idle_mask):
    """idle 자세의 기준: (네발짐승인가, 발바닥 띠 너비, 무게중심 - 발 가운데)."""
    ys, xs = np.nonzero(idle_mask)
    w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    x0, x1 = feet_band(idle_mask)
    return {'quad': bool(w >= WIDE_BREATHE * h), 'band': x1 - x0, 'off': mass_x(idle_mask) - (x0 + x1) / 2}


def pose_feet_x(mask, ref, label=''):
    """앵커에 올릴 x (자세 그림 좌표). ref 가 없으면(idle) 발바닥 가운데."""
    fx = feet_x(mask)
    if ref is None:
        return fx
    x0, x1 = feet_band(mask)
    why = '네발짐승' if ref['quad'] else (f'발바닥 띠 {x1 - x0}px < idle {ref["band"]}px 의 {NARROW_BASE:g}배'
                                       if x1 - x0 < NARROW_BASE * ref['band'] else None)
    if not why:
        return fx
    cx = mass_x(mask) - ref['off']
    if label and abs(cx - fx) >= 1:
        log(f'  {label}: 무게중심으로 발 맞춤 ({why}) — 발바닥 기준보다 {fx - cx:+.0f}px')
    return cx


WIDE_BREATHE = 1.3           # 대기 자세 너비가 키의 이 배 이상이면 네발짐승 숨쉬기 (breathe)
WIDE_BREATHE_DEPTH = 0.04    # 그때 몸이 오르내리는 폭 (몸 높이의 비율, 41px 늑대 → 약 1.5px)
MAX_SHRINK = 0.85            # 칸에 맞추려고 이보다 더 줄여야 하면 실패 (자세가 잘못 나뉘었거나 여럿이 한 칸에 들어간 것)


def place(rgb, mask, label, ref=None, spot=None):
    """80x80 칸에 발 위치를 맞춰 넣는다. 조금 크면 줄이고, 15% 넘게 줄여야 하면 None (실패).
    ref: idle 자세의 align_ref (idle 이 아닌 자세의 발 맞추기 — pose_feet_x).
    spot: 점 색 자리(>= 0) — 줄일 때 NEAREST 가 건너뛴 줄에 걸려도 점 색이 사라지지 않게 줄인 뒤 다시 찍는다."""
    h, w = mask.shape
    max_w, max_h = CELL - 2, ANCHOR[1] - 2
    if w > max_w or h > max_h:
        s = min(max_w / w, max_h / h)
        nw, nh = max(1, int(w * s)), max(1, int(h * s))
        if s < MAX_SHRINK:
            log(f'  실패: {label} 자세가 칸보다 훨씬 커서({w}x{h}) {nw}x{nh} 로 줄여야 한다 — 자세 나누기가 틀렸을 수 있다 (--grid / --poses 로 지정)')
            return None
        log(f'  주의: {label} 자세가 칸보다 커서({w}x{h}) {nw}x{nh} 로 줄였다')
        sy, sx = np.nonzero(spot >= 0) if spot is not None else (np.zeros(0, int), np.zeros(0, int))
        scol = rgb[sy, sx].copy()
        rgb = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((nw, nh), Image.Resampling.NEAREST)).astype(np.float32)
        mask = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((nw, nh), Image.Resampling.NEAREST)) > 127
        if len(sy):
            ny = np.minimum(nh - 1, (sy * nh // h)).astype(int)
            nx = np.minimum(nw - 1, (sx * nw // w)).astype(int)
            rgb[ny, nx] = scol
            mask[ny, nx] = True
        h, w = mask.shape
    fx = pose_feet_x(mask, ref, label)
    x0 = int(round(ANCHOR[0] - fx))
    if not 1 <= x0 <= CELL - 1 - w:
        log(f'  주의: {label} 자세가 칸 밖으로 나가 {x0 - min(max(x0, 1), CELL - 1 - w):+d}px 만큼 밀어 넣었다 (발이 앵커에서 비켜난다)')
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


def spot_layer(c_rgb, c_a, spots, nw, nh):
    """점 색(눈·보석처럼 작지만 꼭 보여야 하는 색)이 축소·팔레트에서 사라지지 않게 — 게임 해상도의 점 색 번호(-1 = 없음).
    원본에서 점 색(거리 SPOT_TOL 안) 픽셀을 찾아 BOX 축소로 게임 px 마다 덮인 비율을 잰다. SPOT_MIN 이상 덮인 px 는 점 색으로,
    그 밖에는 게임 해상도에서 8-연결로 이어진 덩어리(원본에서 여러 조각으로 갈라진 눈도 하나로)마다 가장 많이 덮인 px 하나만 —
    덩어리의 덮인 넓이 합이 SPOT_BLOB_MIN 보다 작으면 티끌로 보고 찍지 않는다."""
    out = np.full((nh, nw), -1, np.int64)
    if not len(spots):
        return out
    d = np.sqrt(((c_rgb[..., None, :] - spots[None, None]) ** 2).sum(-1))
    near = (d.min(-1) <= SPOT_TOL) & (c_a >= 0.5)
    if not near.any():
        return out
    which = d.argmin(-1)
    cov = np.stack([np.asarray(Image.fromarray(((near & (which == i)) * 1.0).astype(np.float32), 'F')
                               .resize((nw, nh), Image.Resampling.BOX)) for i in range(len(spots))])
    tot = cov.sum(0)
    best = cov.argmax(0)
    out[tot >= SPOT_MIN] = best[tot >= SPOT_MIN]
    lab, n = _label(tot > 1e-6, diag=True)
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if (out[ys, xs] >= 0).any() or tot[ys, xs].sum() < SPOT_BLOB_MIN:
            continue
        t = int(tot[ys, xs].argmax())
        out[ys[t], xs[t]] = best[ys[t], xs[t]]
    return out


# ───────── 직업 시트 열쇠 색 (진영 색으로 바꿔 칠할 제복·장식) ─────────

def hex_rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def tint_keys(tint):
    """{'outfit': [...], 'accent': [...]} → (열쇠 색 배열 Kx3, 역할 이름 목록 K)."""
    cols, roles = [], []
    for role in ('outfit', 'accent'):
        for h in (tint or {}).get(role, []):
            cols.append(hex_rgb(h))
            roles.append(role)
    return (np.array(cols, np.float32).reshape(-1, 3), roles)


def key_label(rgb, a, keys):
    """원본 해상도: 열쇠 색 번호(가장 가까운 열쇠 색이 KEY_TOL 안이고 불투명할 때), 아니면 -1."""
    d = np.sqrt(((rgb[..., None, :] - keys[None, None]) ** 2).sum(-1))
    lab = d.argmin(-1)
    lab[(d.min(-1) > KEY_TOL) | (a < 0.5)] = -1
    return lab


def _sq_shift_reduce(m, r, op):
    p = np.pad(m, r)
    out = np.ones_like(m) if op is np.logical_and else np.zeros_like(m)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out = op(out, p[r + dy:r + dy + m.shape[0], r + dx:r + dx + m.shape[1]])
    return out


def clean_key_specks(lab, scale):
    """원본 해상도: 열쇠 색 중 덩어리에 붙지 않은 점·그물(사슬 갑옷 고리에 섞인 푸른 점 등)을 열쇠 색에서 뺀다.
    열쇠 픽셀(역할 무관)을 (2r+1) 정사각형으로 열어(침식 후 팽창) 남는 '몸통'을 찾고, 몸통에서 reach px 안의 열쇠 픽셀만 남긴다
    (제복 가장자리·장식 띠처럼 몸통에 붙은 가는 선은 남는다). r·reach 는 게임 픽셀 1/3·2/3 에 해당하는 원본 px.
    빠진 픽셀은 fill_from_neighbours 로 둘레의 열쇠 색이 아닌 색(사슬 갑옷의 회색 등)을 받는다 (전투에서 진영 색으로 바뀌지 않는다).
    → (새 번호, 뺀 픽셀 마스크)"""
    if lab is None:
        return lab, None
    m = lab >= 0
    r = max(1, int(round(KEY_SPECK_R / scale)))
    reach = max(1, int(round(KEY_SPECK_REACH / scale)))
    core = _sq_shift_reduce(_sq_shift_reduce(m, r, np.logical_and), r, np.logical_or) & m
    keep = _sq_shift_reduce(core, reach, np.logical_or) & m
    drop = m & ~keep
    out = lab.copy()
    out[drop] = -1
    return out, drop


def fill_from_neighbours(rgb, fill, ok, iters=12):
    """fill 픽셀의 색을 둘레(8 이웃) ok 픽셀 색의 평균으로 바꾼다. 안쪽 픽셀은 바깥부터 차례로 (iters 번까지; 남으면 원래 색)."""
    rgb = rgb.copy()
    fill, ok = fill.copy(), ok & ~fill
    H, W = fill.shape
    for _ in range(iters):
        if not fill.any():
            break
        p = np.pad(rgb * ok[..., None], ((1, 1), (1, 1), (0, 0)))
        q = np.pad(ok, 1).astype(np.float32)
        acc = np.zeros_like(rgb)
        cnt = np.zeros(fill.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    acc += p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
                    cnt += q[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
        now = fill & (cnt > 0)
        rgb[now] = acc[now] / cnt[now][:, None]
        ok |= now
        fill &= ~now
    return rgb


def drop_lone_keys(klab):
    """게임 해상도: 8 이웃 중 열쇠 픽셀이 LONE_KEY_N8 개 이하인 외톨이·두 점짜리 열쇠 부스러기를 뺀다 (진영 색 점 하나가 튀지 않게)."""
    m = klab >= 0
    n8, _ = neighbours(m)
    lone = m & (n8 <= LONE_KEY_N8)
    out = klab.copy()
    out[lone] = -1
    return out, lone


def key_resize(lab, a, nk, nw, nh):
    """열쇠 색 번호를 BOX 축소: 알파 가중으로 절반 이상이 열쇠 색이면 가장 많은 열쇠 색, 아니면 -1."""
    def rs(ch):
        return np.asarray(Image.fromarray(ch.astype(np.float32), 'F').resize((nw, nh), Image.Resampling.BOX))
    pa = np.maximum(rs(a), 1e-4)
    frac = np.stack([rs((lab == k) * a) / pa for k in range(nk)], -1)
    out = frac.argmax(-1)
    out[frac.sum(-1) < 0.5] = -1
    return out


def apply_keys(rgb, mask, klab, keys, roles):
    """열쇠 픽셀을 열쇠 색 그대로 칠한다. 실루엣 가장자리(투명과 맞닿은 1px)의 열쇠 픽셀은
    같은 역할의 가장 어두운 열쇠 색으로 (외곽선 구실을 하면서 바꿔 칠하기에 그대로 따라간다)."""
    _, n4 = neighbours(mask)
    edge = mask & (n4 < 4)
    lum = keys @ np.array([0.299, 0.587, 0.114], np.float32)
    darkest = {r: min((i for i in range(len(roles)) if roles[i] == r), key=lambda i: lum[i]) for r in set(roles)}
    out = rgb.copy()
    for k in range(len(keys)):
        m = mask & (klab == k)
        out[m & ~edge] = keys[k]
        out[m & edge] = keys[darkest[roles[k]]]
    return out


TONE = {'outfit': dict(floor=50, knee=130, slope=0.5), 'accent': dict(floor=64, knee=100, slope=0.4)}
TONE_HI, TONE_MAX, TONE_CHROMA = 170.0, 240.0, 150.0
LUM_W = np.array([0.299, 0.587, 0.114], np.float32)


def tone_ramp(keys, target, role):
    """js/battle.js toneRamp 와 같은 규칙: 진영 색의 밝기를 역할별 기준(무릎 위는 완만하게, 아주 어두우면 바닥까지)으로 누르고
    열쇠 색끼리의 밝기 비를 곱한다. TONE_HI 위의 밝은 단계는 TONE_MAX 로 부드럽게 누르고, 255 를 넘는 채널은 자르지 않고
    같은 밝기의 회색 쪽으로 채도를 줄인다 (채도 한도 TONE_CHROMA)."""
    t = TONE.get(role, TONE['outfit'])
    lt = float(target @ LUM_W)
    base = t['knee'] + (lt - t['knee']) * t['slope'] if lt > t['knee'] else max(lt, t['floor'])
    mean = float(np.mean([k @ LUM_W for k in keys])) or 1.0
    out = []
    for k in keys:
        want = base * float(k @ LUM_W) / mean
        if want > TONE_HI:
            want = TONE_MAX - (TONE_MAX - TONE_HI) * float(np.exp(-(want - TONE_HI) / (TONE_MAX - TONE_HI)))
        c = target * want / lt if lt > 1 else np.full(3, want, np.float32)
        mx, mn = float(c.max()), float(c.min())
        f = TONE_CHROMA / (mx - mn) if mx - mn > TONE_CHROMA else 1.0
        if mx > 255:
            f = min(f, (255 - want) / max(1e-6, mx - want))
        if f < 1:
            c = want + (c - want) * max(0.0, f)
        out.append(np.clip(np.round(c), 0, 255).astype(np.uint8))
    return out


def recolor_preview(sheet, keys, roles, test=TINT_TEST):
    """js/battle.js sheetRecolor 와 같은 규칙 (tone_ramp): 열쇠 색 → 시험 색의 명암 단계."""
    out = sheet.copy()
    for role in set(roles):
        idx = [i for i in range(len(roles)) if roles[i] == role]
        ramp = tone_ramp([keys[i] for i in idx], hex_rgb(test[role]), role)
        for i, to in zip(idx, ramp):
            m = (out[..., 3] > 0) & np.all(out[..., :3] == keys[i].astype(np.uint8), -1)
            out[m, :3] = to
    return out


def outline(rgb, mask):
    """투명과 맞닿은 가장자리 1px 를 어두운 보라 쪽으로 (선택적 외곽선)."""
    _, n4 = neighbours(mask)
    edge = mask & (n4 < 4)
    rgb = rgb.copy()
    rgb[edge] = rgb[edge] * 0.45 + OUTLINE * 0.55
    return rgb


# ───────── 한 자세: 축소 → 칠하기 (process 와 tools/art/add_gait.py 가 함께 쓴다) ─────────

def shrink_pose(c_rgb, c_a, klab, nk, spots, scale, nw, nh, alpha=0.45, keep_key_specks=False):
    """원본 해상도의 한 자세(rgb, 알파, 열쇠 색 번호 또는 None)를 nw x nh 게임 px 로 줄인다:
    열쇠 색 점 지우기 → premultiplied BOX 축소 → 점 색 층 → 알파 이진화·정리 → 열쇠 색 번호 축소 → 외톨이 열쇠 픽셀 빼기.
    → (rgb, mask, 열쇠 색 번호(-1 = 없음), 점 색 번호(-1 = 없음), 원본에서 뺀 열쇠 px 수, 게임 해상도에서 뺀 열쇠 px 수)"""
    speck = lone = 0
    if klab is not None and not keep_key_specks:
        klab, drop = clean_key_specks(klab, scale)
        speck = int(drop.sum())
        if speck:
            # 뺀 점은 둘레의 열쇠 색이 아닌 색으로 (축소 전에: 사슬 갑옷의 푸른 점 → 회색 고리)
            c_rgb = fill_from_neighbours(c_rgb, drop, (c_a >= 0.5) & (klab < 0))
    s_rgb, s_a = box_resize(c_rgb, c_a, nw, nh)
    s_sp = spot_layer(c_rgb, c_a, spots, nw, nh)
    mask = s_a > alpha
    s_rgb, mask = cleanup(s_rgb, mask)
    s_k = key_resize(klab, c_a, nk, nw, nh) if klab is not None else np.full(mask.shape, -1)
    s_k[~mask] = -1
    if klab is not None and not keep_key_specks:
        s_k, lone_m = drop_lone_keys(s_k)
        lone = int(lone_m.sum())
        if lone:
            s_rgb = fill_from_neighbours(s_rgb, lone_m, mask & (s_k < 0))
    s_sp[~mask | (s_k >= 0)] = -1
    return s_rgb, mask, s_k, s_sp, speck, lone


def paint_pose(s_rgb, mask, klab, sp, pal, keys, roles, spots):
    """줄인 자세를 시트 공통 팔레트에 맞추고 열쇠 색·점 색을 제 색 그대로 칠한다 (투명 자리는 0)."""
    q = snap(s_rgb, pal)
    if len(keys):
        q = apply_keys(q, mask, klab, keys, roles)
    if len(spots):
        q[sp >= 0] = spots[sp[sp >= 0]]
    q[~mask] = 0
    return q


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
        cmd = [sg, 'breathe', src, dst, '--mode', 'pixel']
        ys, xs = np.nonzero(cell[..., 3])
        fw, fh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if fw >= WIDE_BREATHE * fh:
            # 가로로 긴 네발짐승(늑대 등): sprite-gen 은 사람처럼 '머리 아래 몸통'을 찾다가 아래쪽 다리 부근을 머리로 잡아
            # 다리만 1px 남짓 움직인다 (네 칸이 거의 같다). 몸 윗부분부터 등 전체가 오르내리게 강체 경계를 위쪽에 둔다.
            rigid = max(1, int(round(fh * 0.1)))
            cmd += ['--rigid-row', str(rigid), '--depth', str(WIDE_BREATHE_DEPTH)]
            log(f'  숨쉬기: 가로로 긴 몸({fw}x{fh}) — 등 전체가 오르내리게 (--rigid-row {rigid} --depth {WIDE_BREATHE_DEPTH})')
        r = subprocess.run(cmd, capture_output=True, text=True)
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
    if not grid and not a.poses and req.get('layout') == '2x2':
        grid = (2, 2)   # 요청서가 2x2 격자 (넓은 몬스터·기마): 가로로 긴 그림이라도 1x4 띠로 짐작하지 않는다
        log('  배치: 요청서의 2x2 격자')
    CELL = a.cell or req.get('cell') or 80
    ANCHOR = (CELL // 2, CELL - 4)
    height = a.height or req.get('height') or 64
    req_scale = None if (a.scale or a.height) else req.get('scale')
    tint = None if a.no_tint else req.get('tint')
    keys, roles = tint_keys(tint)
    spot_hex = [h.strip() for h in (a.spot.split(',') if a.spot is not None else (req.get('spots') or []))]
    spot_hex = [h for h in spot_hex if h]          # --spot '' = 점 색 끄기 (요청서의 spots 도 쓰지 않음)
    bad = [h for h in spot_hex if not re.fullmatch(r'#?[0-9A-Fa-f]{6}', h)]
    if bad:
        log(f'  실패: 점 색은 #rrggbb 이어야 한다: {", ".join(bad)}')
        return False
    spots = np.array([hex_rgb(h) for h in spot_hex], np.float32).reshape(-1, 3)
    if len(spots):
        log(f'  점 색 (축소 뒤에도 남김): {", ".join(spot_hex)} (거리 {SPOT_TOL:g} 안)')
    if tint:
        log(f'  열쇠 색: 제복 {", ".join(tint.get("outfit", []))} / 장식 {", ".join(tint.get("accent", []))} (거리 {KEY_TOL:g} 안)')
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
    klabs = [key_label(c_rgb, c_a, keys) if len(keys) else None for c_rgb, c_a in crops]
    # 모든 자세에 같은 배율: idle 의 몸 높이 → height
    body = body_height(crops[0][1])
    if a.scale or req_scale:
        # 같은 가이드 격자(발바닥 y=870, 머리 110px)에 그린 캐릭터들은 같은 배율로 줄여야 크기가 서로 맞는다.
        # (idle 높이로 맞추면 모자·큰 머리숱까지 64px 에 들어가 그 캐릭터만 작아진다)
        scale = a.scale or req_scale
        height = body * scale
        log(f'  배율 {scale:.4f} 고정 ({"--scale" if a.scale else "요청서"}; idle 몸 높이 {body}px → {height:.1f}px, 칸 {CELL}x{CELL})')
    else:
        scale = height / body
        log(f'  배율 {scale:.4f} (idle 몸 높이 {body}px → {height}px, 칸 {CELL}x{CELL}; 머리 위로 솟은 가는 무기 끝은 빼고 잰다)')
    # 자세별 배율 보정 (요청서 pose_scale / --pose-scale): GPT 가 2x2 격자의 칸을 상자 크기에 맞추려고 한 자세만 몸까지 크게 그린 경우
    pose_scale = dict(req.get('pose_scale') or {})
    if a.pose_scale:
        pose_scale = {k.strip(): float(v) for k, v in (kv.split('=') for kv in a.pose_scale.split(','))}
    small = []
    spot_small = []
    for (c_rgb, c_a), klab, nm in zip(crops, klabs, names):
        hh = body_height(c_a) * scale
        if nm != 'idle' and hh < height * 0.55:
            log(f'  실패: {nm} 자세 몸 높이 {hh:.0f}px 가 idle({height}px)의 절반 남짓도 안 된다 — 떨어진 조각(불꽃·구슬 등)이 자세로 잘린 듯하다 (--poses 1 / --grid 로 지정)')
            return False
        if nm != 'idle' and abs(hh - height) > height * 0.3 and nm != 'hit':
            log(f'  주의: {nm} 자세 높이 {hh:.0f}px — 칸마다 캐릭터 크기가 다르게 그려졌을 수 있다')
        ps = pose_scale.get(nm, 1.0)
        if ps != 1.0:
            log(f'  {nm}: 자세 배율 x{ps:g} (그림이 이 자세만 크게 그려졌다 — {"--pose-scale" if a.pose_scale else "요청서 pose_scale"})')
        nw = max(1, int(round(c_a.shape[1] * scale * ps)))
        nh = max(1, int(round(c_a.shape[0] * scale * ps)))
        s_rgb, mask, s_k, s_sp, speck, lone = shrink_pose(c_rgb, c_a, klab, len(keys), spots, scale, nw, nh, a.alpha, a.keep_key_specks)
        if speck or lone:
            log(f'  {nm}: 열쇠 색 점 지움 — 원본 {speck}px (덩어리에서 떨어진 점·그물), 게임 해상도 외톨이 {lone}px → 둘레 색으로')
        bb = bbox(mask.astype(np.float32), 0.5)
        if bb is None:
            log(f'  실패: {nm} 자세가 축소 후 비었다')
            return False
        x0, y0, x1, y1 = bb
        small.append((s_rgb[y0:y1, x0:x1], mask[y0:y1, x0:x1], s_k[y0:y1, x0:x1]))
        sp = s_sp[y0:y1, x0:x1].copy()
        spot_small.append(sp)
        if len(spots):
            log(f'  {nm}: 점 색 {int((sp >= 0).sum())}px')
        if len(keys):
            share = {r: float(np.isin(s_k, [i for i in range(len(roles)) if roles[i] == r]).sum()) / max(1, int(mask.sum()))
                     for r in ('outfit', 'accent')}
            log(f'  {nm}: 열쇠 색 픽셀 제복 {share["outfit"]:.0%}, 장식 {share["accent"]:.0%}')
            if nm == 'idle' and share['outfit'] < KEY_MIN_SHARE:
                log(f'  주의: 대기 자세에 제복 열쇠 색이 {share["outfit"]:.1%} 뿐이다 — 열쇠 색으로 칠하지 않은 그림 같다 (진영 색으로 바뀌지 않는다)')

    # 외곽선(가장자리 어둡게)을 먼저 입힌 뒤 팔레트를 만들고 한 번만 양자화한다: 외곽 색도 공통 팔레트 안에 든다 (--colors 이하)
    if not a.no_outline:
        small = [(outline(r, m), m, k) for r, m, k in small]
    # 팔레트는 열쇠 색이 아닌 픽셀로만 만든다 (열쇠 색 자리는 비워 둔다). 우연히 열쇠 색과 똑같은 팔레트 색은 1 만큼 비켜서,
    # 열쇠 색이 아닌 픽셀이 전투에서 바꿔 칠해지지 않게 한다.
    rest = np.concatenate([r[m & (k < 0)] for r, m, k in small])
    pal = build_palette(rest if len(rest) else np.zeros((1, 3), np.float32), max(8, a.colors - len(keys) - len(spots)))
    for kc in keys:
        same = np.all(pal == kc, -1)
        pal[same, 0] = np.where(kc[0] > 0, kc[0] - 1, 1)
    cells = {}
    ref = None
    for (s_rgb, mask, klab), sp, nm in zip(small, spot_small, names):
        q = paint_pose(s_rgb, mask, klab, sp, pal, keys, roles, spots)
        cell = place(q, mask, nm, ref, spot=sp if len(spots) else None)
        if cell is None:
            return False
        if nm == 'idle':
            ref = align_ref(mask)
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
    if len(keys):
        preview(recolor_preview(sheet, keys, roles), os.path.join(wdir, 'preview_tint_x4.png'))
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
    if tint and sid.startswith('sheet/class/'):
        for role in ('outfit', 'accent'):
            if tint.get(role):
                cmd += [f'--tint-{role}', ','.join(tint[role])]
    if a.dry_run:
        cmd.append('--dry-run')
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if a.dry_run:
        out = '\n'.join(out.splitlines()[:3] + ['  ...'])
    log('  ' + out.replace('\n', '\n  '))
    return r.returncode == 0


def realign(ids, a):
    """이미 등록된 시트의 idle 이 아닌 칸을 pose_feet_x 규칙으로 다시 맞춘다 (원본 그림 없이, 칸 안에서 가로로만 민다).
    manifest 는 그대로 (칸 위치·앵커가 같다). ids 가 비면 등록된 시트 전부를 검사한다."""
    mpath = os.path.join(ROOT, 'assets', 'art', 'manifest.json')
    with open(mpath, encoding='utf-8') as f:
        man = json.load(f)
    ids = ids or sorted(k for k, v in man.items() if k.startswith('sheet/') and isinstance(v, dict) and 'sheet' in v)
    changed = 0
    for sid in ids:
        ent = man.get(sid)
        if not ent or 'sheet' not in ent:
            log(f'{sid}: manifest 에 시트가 없다')
            continue
        m = ent['sheet']
        cw, ch = m['cell']
        ax = m['anchor'][0]
        path = os.path.join(ROOT, ent['file'])
        im = np.array(Image.open(path).convert('RGBA'))
        idle = m['anims']['idle']
        cell = lambda i: im[m['frames'][i][1]:m['frames'][i][1] + ch, m['frames'][i][0]:m['frames'][i][0] + cw]
        ref = align_ref(cell(idle['from'])[..., 3] > 0)
        names = {i: n for n, an in m['anims'].items() for i in range(an['from'], an['to'] + 1)}
        # 달리기·걷기 칸(tools/art/add_gait.py)은 발바닥이 아니라 고정된 바닥 줄·프레임 가운데 열에 맞춰 놓은 것이다 — 밀지 않는다
        gait = {i for i, n in names.items() if n in set(m.get('gaits') or {}) | {'run', 'walk'}}
        moves = []
        for i in range(len(m['frames'])):
            if idle['from'] <= i <= idle['to'] or i in gait:
                continue
            c = cell(i)
            mask = c[..., 3] > 0
            if not mask.any():
                continue
            fx = pose_feet_x(mask, ref)
            if fx == feet_x(mask):
                continue   # 발바닥 기준 그대로인 칸
            xs = np.nonzero(mask.any(0))[0]
            dx = int(round(ax - fx))
            dx = min(max(dx, 1 - xs.min()), cw - 1 - (xs.max() + 1))
            if not dx:
                continue
            moves.append((i, dx))
            log(f'{sid}: 칸 {i} ({names.get(i, "?")}) {dx:+d}px (발바닥 띠 가운데 {feet_x(mask) - ax:+.0f} → 무게중심 기준)')
            if not a.dry_run:
                fx0, fy0 = m['frames'][i]
                out = np.zeros_like(c)
                if dx > 0:
                    out[:, dx:] = c[:, :cw - dx]
                else:
                    out[:, :cw + dx] = c[:, -dx:]
                im[fy0:fy0 + ch, fx0:fx0 + cw] = out
        if moves and not a.dry_run:
            Image.fromarray(im).save(path, optimize=True)
            changed += 1
    log(f'다시 맞춘 시트 {changed}개{" (--dry-run: 저장하지 않음)" if a.dry_run else ""}')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('inputs', nargs='*', help='처리할 png (기본: art/inbox/sheet_*.png 전부)')
    ap.add_argument('--id', help='manifest id (입력이 하나일 때). 기본은 요청서/파일 이름에서 찾는다')
    ap.add_argument('--grid', help='자세 배치를 강제: 4x1 (가로 띠), 2x2, 1x1')
    ap.add_argument('--poses', type=int, choices=[1, 2, 3, 4], help='한 줄 띠의 자세 수 (기본: 가로로 긴 그림은 4, 아니면 자동)')
    ap.add_argument('--flip', action='store_true', help='왼쪽을 보고 그려진 그림을 뒤집는다')
    ap.add_argument('--height', type=int, help='idle 자세의 몸 높이 px (기본: 요청서, 없으면 64)')
    ap.add_argument('--scale', type=float, help='원본 → 게임 배율을 고정 (--height 대신). 같은 가이드 격자에 그린 시트끼리 크기를 맞출 때: '
                    '대장 1x4 띠는 앵커 바렌의 0.1654')
    ap.add_argument('--cell', type=int, help='칸 크기 (기본: 요청서, 없으면 80; 발 위치는 칸 가운데·바닥 4px 위)')
    ap.add_argument('--colors', type=int, default=40, help='시트 공통 팔레트 색 수 (기본 40)')
    ap.add_argument('--alpha', type=float, default=0.45, help='축소 후 알파 기준 (기본 0.45)')
    ap.add_argument('--no-outline', action='store_true', help='가장자리 어둡게 하기를 끈다')
    ap.add_argument('--no-tint', action='store_true', help='요청서의 열쇠 색(tint)을 쓰지 않는다 (직업 시트를 바꿔 칠하지 않는 그림으로)')
    ap.add_argument('--pose-scale', help='자세별 배율 보정, 예: windup=0.9,strike=0.88 (기본: 요청서의 pose_scale). '
                    'idle 과 같은 배율로 그려지지 않은 자세(몸·머리까지 커진 공격 자세)를 idle 크기에 맞춘다')
    ap.add_argument('--spot', help="축소 뒤에도 꼭 남길 작은 점 색(눈 등), 예: #d6455d,#f2c94c (기본: 요청서의 spots; --spot '' 이면 끈다)")
    ap.add_argument('--keep-key-specks', action='store_true',
                    help='열쇠 색 점 지우기(clean_key_specks · drop_lone_keys)를 끈다 — 비교용')
    ap.add_argument('--work', help='중간 결과·미리보기를 둘 폴더 (기본: 임시 폴더)')
    ap.add_argument('--dry-run', action='store_true', help='시트는 만들되 manifest 는 바꾸지 않는다')
    ap.add_argument('--no-register', action='store_true', help='register_sheet.py 를 부르지 않는다')
    ap.add_argument('--aseprite', metavar='PATH', help='태그가 붙은 .aseprite 도 저장 (Aseprite 가 있을 때만)')
    ap.add_argument('--aseprite-bin', help='Aseprite 실행 파일 경로 (기본: $ASEPRITE, PATH)')
    ap.add_argument('--allow-draft', action='store_true',
                    help='시험용: NovelAI 초안도 처리한다. 언제나 --dry-run (manifest 등록 불가) — 게임 그림은 GPT 를 거친다')
    ap.add_argument('--realign', action='store_true',
                    help='원본 없이 이미 등록된 시트(입력 = manifest id, 없으면 전부)의 공격·피격 칸을 발 맞추기 규칙(pose_feet_x)으로 '
                    '다시 맞춘다. --dry-run 이면 보고만')
    a = ap.parse_args()
    if a.realign:
        return realign(a.inputs, a)
    if a.allow_draft:
        a.dry_run = True   # 초안은 미리보기까지만. 등록 경로는 없다.

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
        why = novelai_draft_reason(p)
        if why:
            if not a.allow_draft:
                log(f'{p}: NovelAI 디자인 초안이라 거부 ({why}). NovelAI 는 디자인 초안 전용이고 게임 그림은 GPT 를 거친다 '
                    '(art/requests/gpt_handoff_notes.md). 파이프라인 시험만이라면 --allow-draft (항상 --dry-run).')
                bad += 1
                continue
            log(f'{p}: NovelAI 초안 ({why}) — --allow-draft 시험 처리, manifest 는 바꾸지 않는다')
        why = mannequin_reason(p, a.aseprite_bin)
        if why:
            if not a.allow_draft:
                log(f'{p}: 뼈대(마네킹) 그림이라 거부 ({why}). 마네킹은 PC 가 만드는 자세 가이드이고 게임 그림이 아니다 — 게임 그림은 GPT 를 거쳐 '
                    'art/inbox/ 로 온다. 파이프라인 시험만이라면 --allow-draft (항상 --dry-run).')
                bad += 1
                continue
            log(f'{p}: 뼈대(마네킹) ({why}) — --allow-draft 시험 처리, manifest 는 바꾸지 않는다')
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
