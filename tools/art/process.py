#!/usr/bin/env python3
"""그림 후처리: art/inbox 의 원본을 게임용으로 정리해 assets/art 에 넣고 manifest.json 을 만든다.

- 단색 배경(투명이 아닌 경우)은 네 모서리 색을 기준으로 지운다 (초상화만).
- 투명 여백을 잘라 내고, 요청서의 '게임 내 크기'에 맞춰 축소한다.
- 팔레트를 줄여(초상화 32색, 이벤트 48색) 도트 느낌을 맞춘다.
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
        im = im.resize((ow, oh), Image.Resampling.BOX)
        im = quantize_rgba(im, 48)
    sub = {'portrait': 'portraits', 'event': 'events', 'background': 'backgrounds'}[item['kind']]
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
    manifest = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding='utf-8') as f:
            manifest = json.load(f)
    done, missing = [], []
    for item in items:
        src = os.path.join(INBOX, item['file'])
        if not os.path.exists(src):
            missing.append(item['file'])
            continue
        manifest[item['id']] = process(item, src)
        done.append(item['file'])
    os.makedirs(OUT, exist_ok=True)
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    print(f'processed {len(done)}, waiting {len(missing)}, manifest {len(manifest)} entries')
    for d in done:
        print('  +', d)


if __name__ == '__main__':
    sys.exit(main())
