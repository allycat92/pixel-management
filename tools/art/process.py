#!/usr/bin/env python3
"""그림 후처리: art/inbox 의 원본을 게임용으로 정리해 assets/art 에 넣고 manifest.json 을 만든다.

- 단색 배경(투명이 아닌 경우)은 네 모서리 색을 기준으로 지운다 (초상화만).
- 투명 여백을 잘라 내고, 요청서의 '게임 내 크기'에 맞춰 축소한다.
- 팔레트를 줄여(초상화 32색, 이벤트 48색) 도트 느낌을 맞춘다. 이미 색을 줄여 그린 배경(<=256색)은
  원본 자신의 팔레트로 맞춘다 (드문 색이 사라지지 않게).
- manifest.json 은 덮어쓰지 않고 고친다: 이 스크립트가 만든 항목만 갱신하고, 다른 항목
  (전투 시트 sheet/*, register_sheet.py·sheets.py 가 넣은 것 등)은 그대로 둔다.
- 전투 캐릭터 시트(요청서 kind 'sheet')는 여기서 처리하지 않는다 → tools/art/sheets.py
실행: python3 tools/art/process.py   (Pillow 필요)
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
REQ_DIR = os.path.join(ROOT, 'art', 'requests')
INBOX = os.path.join(ROOT, 'art', 'inbox')
OUT = os.path.join(ROOT, 'assets', 'art')
MANIFEST = os.path.join(OUT, 'manifest.json')


def remove_flat_background(im, tol=28):
    """네 모서리가 같은 색이면 그 색(허용 오차 tol)을 투명으로 만든다."""
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    if any(c[3] < 250 for c in corners):
        return im  # 이미 투명 배경
    base = corners[0]
    if any(sum(abs(a - b) for a, b in zip(c[:3], base[:3])) > tol for c in corners):
        return im  # 배경이 단색이 아니면 건드리지 않는다
    # 모서리에서 이어진 영역만 지운다 (인물 안쪽의 같은 색은 남긴다)
    seen = set()
    stack = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        c = px[x, y]
        if sum(abs(a - b) for a, b in zip(c[:3], base[:3])) > tol:
            continue
        px[x, y] = (0, 0, 0, 0)
        stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    return im


def quantize_rgba(im, colors):
    """알파를 유지한 채 색 수를 줄인다."""
    alpha = im.getchannel('A')
    rgb = im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    out = rgb.convert('RGBA')
    out.putalpha(alpha.point(lambda a: 255 if a >= 128 else 0))  # 반투명 가장자리 정리
    return out


def to_palette(im, colors):
    """불투명 그림을 주어진 색 목록(<=256)에 디더 없이 맞춘다."""
    pal = Image.new('P', (1, 1))
    flat = [v for c in colors for v in c[:3]]
    pal.putpalette(flat + flat[:3] * (256 - len(colors)))
    return im.convert('RGB').quantize(palette=pal, dither=Image.Dither.NONE).convert('RGBA')


HANDLED = {'portrait': 'portraits', 'event': 'events', 'background': 'backgrounds'}


def process(item, src):
    im = Image.open(src).convert('RGBA')
    ow, oh = (int(v) for v in item['out'].split('x'))
    if item['kind'] == 'portrait':
        im = remove_flat_background(im)
        bbox = im.getchannel('A').getbbox()
        if bbox:
            im = im.crop(bbox)
        # 정사각형 캔버스 가운데 아래쪽에 맞춘다
        side = max(im.size)
        canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        canvas.paste(im, ((side - im.width) // 2, side - im.height))
        im = canvas.resize((ow, oh), Image.Resampling.BOX)
        im = quantize_rgba(im, 32)
    else:
        # 이벤트 그림·배경: 목표 비율로 가운데 자르고 축소
        w, h = im.size
        target = ow / oh
        if w / h > target:
            nw = int(h * target)
            im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / target)
            im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        src_pal = im.convert('RGB').getcolors(256) if item['kind'] == 'background' else None
        im = im.resize((ow, oh), Image.Resampling.BOX)
        if src_pal:
            # 이미 색을 줄여 그린 배경(<=256색): 축소한 그림을 원본 자신의 팔레트에 맞춘다.
            # median-cut 으로 다시 줄이면 창밖 하늘·덩굴·성의 분홍 같은 드문 색이 회색·갈색으로 사라진다.
            im = to_palette(im, [c for _, c in src_pal])
        else:
            im = quantize_rgba(im, 48)
    sub = HANDLED[item['kind']]
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)
    rel = f'assets/art/{sub}/{item["file"]}'
    im.save(os.path.join(ROOT, rel), optimize=True)
    return {'file': rel, 'w': ow, 'h': oh}


def main():
    items = []
    for name in sorted(os.listdir(REQ_DIR)):
        if name.startswith('phase') and name.endswith('.json'):
            with open(os.path.join(REQ_DIR, name), encoding='utf-8') as f:
                items += json.load(f)['items']
    skipped = sum(1 for it in items if it.get('kind') not in HANDLED)
    items = [it for it in items if it.get('kind') in HANDLED]
    manifest = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding='utf-8') as f:
            manifest = json.load(f)
    before = dict(manifest)
    done, missing = [], []
    for item in items:
        src = os.path.join(INBOX, item['file'])
        if not os.path.exists(src):
            missing.append(item['file'])
            continue
        manifest[item['id']] = process(item, src)
        done.append(item['file'])
    # 안전장치: 이 스크립트가 만들지 않은 항목(sheet/* 등)은 한 글자도 바뀌면 안 된다
    mine = {it['id'] for it in items}
    for k, v in before.items():
        assert k in manifest and (k in mine or manifest[k] == v), f'manifest 항목 {k} 이 바뀌었다'
    kept = sum(1 for k in manifest if k not in mine)
    os.makedirs(OUT, exist_ok=True)
    tmp = MANIFEST + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    os.replace(tmp, MANIFEST)
    print(f'processed {len(done)}, waiting {len(missing)}, manifest {len(manifest)} entries '
          f'({kept} kept untouched, e.g. sheet/*); {skipped} sheet requests skipped -> tools/art/sheets.py')
    for d in done:
        print('  +', d)


if __name__ == '__main__':
    sys.exit(main())
