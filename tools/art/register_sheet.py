#!/usr/bin/env python3
"""전투용 스프라이트 시트를 게임에 등록한다.

Aseprite 의 json-array 출력(--list-tags 포함)을 읽어 assets/art/manifest.json 에
'sheet' 항목을 추가하거나 갱신한다. 다른 항목(초상화·이벤트·배경)은 그대로 둔다.

  python3 tools/art/register_sheet.py --id sheet/captain/blademaster \\
      --png out/baren_sheet.png --json out/baren_sheet.json [--anchor 40,76] [--facing 1]

- png 는 assets/art/sheets/<id 의 / 를 _ 로 바꾼 이름>.png 로 복사된다.
- anchor: 칸(cell) 안에서 발바닥 가운데 위치. 기본은 80x80 칸 기준 40,76.
- facing: 그림이 바라보는 방향 (1 = 오른쪽, -1 = 왼쪽).
- 태그 이름(idle/walk/attack/hit/cast ...)이 그대로 애니메이션 이름이 된다. idle 은 꼭 있어야 한다.
Aseprite 내보내기 예:
  aseprite -b in.aseprite --sheet out.png --data out.json --format json-array \\
      --list-tags --sheet-type rows --sheet-columns 8
(잘라내기 --trim 은 쓰지 않는다: 모든 칸의 크기와 발 위치가 같아야 한다.)
필요: 파이썬 표준 라이브러리 + Pillow
"""
import argparse
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
MANIFEST = os.path.join(ROOT, 'assets', 'art', 'manifest.json')
SHEETS = os.path.join(ROOT, 'assets', 'art', 'sheets')
ID_RE = re.compile(r'^sheet/(captain|hero|class|monster)/[^/\s]+$')


def fail(msg):
    print(f'register_sheet: {msg}', file=sys.stderr)
    sys.exit(1)


def pair(text, kind=int):
    try:
        a, b = (kind(v) for v in text.split(','))
    except ValueError:
        fail(f'"{text}" 는 X,Y 형식이어야 한다')
    return a, b


def read_frames(data):
    frames = data.get('frames')
    if isinstance(frames, dict):  # json-hash 도 받아 준다 (순서는 파일 순서)
        frames = list(frames.values())
    if not frames:
        fail('json 에 frames 가 없다')
    return frames


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--id', required=True, help='sheet/captain/<key> | sheet/hero/<key> | sheet/class/<key> | sheet/monster/<이름>')
    ap.add_argument('--png', required=True, help='Aseprite 가 내보낸 시트 png')
    ap.add_argument('--json', required=True, help='Aseprite json-array 데이터 (--list-tags)')
    ap.add_argument('--anchor', help='칸 안의 발 위치 X,Y (기본 40,76)')
    ap.add_argument('--facing', type=int, default=1, choices=[1, -1], help='그림이 보는 방향 (1 오른쪽)')
    ap.add_argument('--dry-run', action='store_true', help='manifest 를 쓰지 않고 결과만 출력')
    a = ap.parse_args()

    if not ID_RE.match(a.id):
        fail(f'id "{a.id}" 형식이 틀렸다 (예: sheet/captain/blademaster)')
    with open(a.json, encoding='utf-8') as f:
        data = json.load(f)
    frames = read_frames(data)
    im = Image.open(a.png)
    W, H = im.size

    cw, ch = frames[0]['frame']['w'], frames[0]['frame']['h']
    rects = []
    for i, fr in enumerate(frames):
        r = fr['frame']
        if (r['w'], r['h']) != (cw, ch):
            fail(f'{i}번 칸 크기 {r["w"]}x{r["h"]} 가 첫 칸 {cw}x{ch} 와 다르다 (모든 칸 크기가 같아야 한다)')
        if fr.get('rotated'):
            fail(f'{i}번 칸이 회전되어 있다 (회전 없이 내보낼 것)')
        if fr.get('trimmed'):
            fail(f'{i}번 칸이 잘려 있다 (--trim 없이 내보낼 것)')
        if r['x'] + cw > W or r['y'] + ch > H:
            fail(f'{i}번 칸이 png({W}x{H}) 밖으로 나간다')
        rects.append([r['x'], r['y']])
    durs = [int(fr.get('duration', 100)) for fr in frames]

    anims = {}
    for tag in data.get('meta', {}).get('frameTags', []):
        lo, hi = int(tag['from']), int(tag['to'])
        if not (0 <= lo <= hi < len(frames)):
            fail(f'태그 {tag["name"]} 범위 {lo}-{hi} 가 칸 수 {len(frames)} 를 벗어난다')
        if tag.get('direction', 'forward') != 'forward':
            print(f'  주의: 태그 {tag["name"]} 의 방향 {tag["direction"]} 은 무시하고 앞으로 재생한다')
        anims[tag['name']] = {'from': lo, 'to': hi, 'ms': durs[lo:hi + 1]}
    if 'idle' not in anims:
        if data.get('meta', {}).get('frameTags'):
            fail('idle 태그가 없다 (idle 은 꼭 필요하다)')
        anims['idle'] = {'from': 0, 'to': len(frames) - 1, 'ms': durs}
        print('  주의: 태그가 없어 모든 칸을 idle 로 쓴다')

    if a.anchor:
        anchor = list(pair(a.anchor))
    elif (cw, ch) == (80, 80):
        anchor = [40, 76]
    else:
        anchor = [cw // 2, ch - 4]
        print(f'  주의: 칸이 80x80 이 아니라 기준 발 위치를 {anchor[0]},{anchor[1]} 로 잡았다 (--anchor 로 지정 가능)')
    if not (0 <= anchor[0] <= cw and 0 <= anchor[1] <= ch):
        fail(f'anchor {anchor} 가 칸 {cw}x{ch} 밖이다')

    rel = f'assets/art/sheets/{a.id.replace("/", "_")}.png'
    entry = {'file': rel, 'w': W, 'h': H,
             'sheet': {'cell': [cw, ch], 'anchor': anchor, 'facing': a.facing, 'frames': rects, 'anims': anims}}
    if a.dry_run:
        print(json.dumps({a.id: entry}, ensure_ascii=False, indent=2))
        return 0

    os.makedirs(SHEETS, exist_ok=True)
    dst = os.path.join(ROOT, rel)
    if os.path.abspath(a.png) != os.path.abspath(dst):
        shutil.copyfile(a.png, dst)
    manifest = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding='utf-8') as f:
            manifest = json.load(f)
    before = len(manifest)
    manifest[a.id] = entry
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')
    print(f'{a.id}: {len(frames)} 칸 {cw}x{ch}, anchor {anchor[0]},{anchor[1]}, '
          f'애니 {", ".join(f"{k}({v["to"] - v["from"] + 1})" for k, v in sorted(anims.items()))} -> {rel}'
          f' (manifest {before} -> {len(manifest)} 항목)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
