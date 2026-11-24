#!/usr/bin/env python3
"""바렌(검귀) 도트 캐릭터 생성기.

부위(머리·머리띠·망토·몸통·다리·팔·검)를 도트 도형으로 겹쳐 그리고, 부위마다 외곽선과
왼쪽 위 광원 음영을 자동으로 넣는다. 동작마다 자세(다리·팔·검 위치)를 프레임별로 새로 찍는다.

출력: <out>/frames/<anim>_<n>.png (1배), <out>/<anim>.gif·sheet.png (확대 미리보기)
실행: python3 tools/pixelart/baren.py <out_dir>
"""
import math
import os
import sys

from PIL import Image

W, H = 40, 48
FOOT = 46

PAL = {
    'O': (27, 20, 32),        # 외곽선
    'H': (43, 29, 20), 'h': (74, 51, 38), 'i': (26, 17, 12),           # 머리카락
    'S': (224, 172, 126), 's': (179, 122, 82), 'z': (240, 200, 160),     # 피부
    'W': (232, 228, 216), 'w': (176, 168, 152),                          # 머리띠·옷깃
    'R': (122, 30, 42), 'r': (74, 16, 26), 'Q': (168, 50, 62),          # 붉은 망토·옷
    'B': (107, 66, 38), 'b': (70, 42, 24),                              # 가죽 띠
    'P': (46, 40, 56), 'p': (31, 26, 38), 'q': (70, 62, 84),            # 바지
    'K': (58, 42, 32), 'k': (36, 26, 20),                               # 장화
    'M': (200, 208, 216), 'm': (130, 138, 150), 'L': (255, 255, 255),   # 칼날
    'G': (200, 154, 64), 'g': (138, 98, 36),                            # 칼자루 금속
    'X': (190, 40, 50),                                                 # 흉터
    'E': (240, 240, 255),                                               # 눈 하이라이트
    'F': (220, 240, 255),                                               # 베기 잔상
}


class Canvas:
    def __init__(self):
        self.g = [[None] * W for _ in range(H)]

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < W and 0 <= y < H else None

    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.g[y][x] = c

    # 부위 하나: 마스크를 외곽선으로 두르고, 음영을 넣어 채운다
    def part(self, mask, base, dark=None, light=None, outline=True, light_dir=(-1, -1)):
        mask = {(x, y) for (x, y) in mask if 0 <= x < W and 0 <= y < H}
        if not mask:
            return
        if outline:
            ring = set()
            for (x, y) in mask:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (x + dx, y + dy)
                    if n not in mask:
                        ring.add(n)
            for (x, y) in ring:
                self.put(x, y, 'O')
        lx, ly = light_dir
        for (x, y) in mask:
            c = base
            # 빛 반대쪽(오른쪽·아래) 가장자리는 어둡게, 빛 쪽 가장자리는 밝게
            if dark and ((x - lx, y) not in mask or (x, y - ly) not in mask):
                c = dark
            elif light and ((x + lx, y) not in mask or (x, y + ly) not in mask) and (x - lx, y) in mask:
                c = light
            self.put(x, y, c)

    def image(self):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        px = im.load()
        for y in range(H):
            for x in range(W):
                c = self.g[y][x]
                if c:
                    px[x, y] = PAL[c] + (255,)
        return im


# ───────── 도형 마스크 ─────────
def ellipse(cx, cy, rx, ry):
    return {(x, y) for y in range(int(cy - ry) - 1, int(cy + ry) + 2) for x in range(int(cx - rx) - 1, int(cx + rx) + 2)
            if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}


def rect(x0, y0, x1, y1):
    return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}


def poly(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    out = set()
    for y in range(int(min(ys)), int(max(ys)) + 1):
        for x in range(int(min(xs)), int(max(xs)) + 1):
            px, py = x + 0.5, y + 0.5
            inside = False
            j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]; xj, yj = pts[j]
                if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi:
                    inside = not inside
                j = i
            if inside:
                out.add((x, y))
    return out


def thick_line(x0, y0, x1, y1, w=1):
    out = set()
    n = int(max(abs(x1 - x0), abs(y1 - y0))) * 2 + 1
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        for dx in range(-(w // 2), w - w // 2):
            for dy in range(-(w // 2), w - w // 2):
                out.add((int(round(x)) + dx, int(round(y)) + dy))
    return out


# ───────── 캐릭터 ─────────
def leg(c, hip_x, hip_y, foot_x, front):
    """엉덩이에서 발까지: 바지 + 장화. foot_x는 발뒤꿈치 x."""
    knee_x = (hip_x + foot_x) / 2 + (1 if front else 0)
    m = thick_line(hip_x, hip_y, knee_x, hip_y + 5, 4) | thick_line(knee_x, hip_y + 5, foot_x + 1, FOOT - 4, 4)
    c.part(m, 'P' if front else 'p', 'p', 'q' if front else None)
    boot = rect(int(foot_x) - 1, FOOT - 4, int(foot_x) + 3, FOOT) | rect(int(foot_x) + 3, FOOT - 2, int(foot_x) + 4, FOOT)
    c.part(boot, 'K' if front else 'k', 'k')


def sword(c, hx, hy, ang, length=17):
    """손(hx,hy)에서 각도 ang(라디안, 0=오른쪽, 아래가 +)으로 뻗는 검."""
    dx, dy = math.cos(ang), math.sin(ang)
    # 칼자루(손 뒤쪽)와 칼날
    grip = thick_line(hx - dx * 3, hy - dy * 3, hx, hy, 2)
    blade = thick_line(hx + dx * 2, hy + dy * 2, hx + dx * length, hy + dy * length, 2)
    guard = thick_line(hx + dx * 1.5 - dy * 3, hy + dy * 1.5 + dx * 3, hx + dx * 1.5 + dy * 3, hy + dy * 1.5 - dx * 3, 1)
    c.part(blade, 'M', 'm', 'L')
    c.part(grip, 'g', 'g')
    c.part(guard, 'G', 'g')
    # 칼끝 반짝임
    c.put(int(round(hx + dx * length)), int(round(hy + dy * length)), 'L')


def draw(pose):
    """pose: bob, lean, legs=(back_foot_x, front_foot_x), hand=(x,y), ang, cloak, band, smear"""
    c = Canvas()
    bob, lean = pose.get('bob', 0), pose.get('lean', 0)
    ox = 19 + lean                     # 몸 중심 x
    top = 3 + bob                      # 머리 꼭대기 y
    sway = pose.get('cloak', 0)
    band = pose.get('band', 0)

    # 1) 머리띠 꼬리 (머리 뒤로 나부낌)
    tail_y = top + 9
    c.part(poly([(ox - 7, tail_y), (ox - 13 - band, tail_y + 1 + band // 2), (ox - 15 - band, tail_y + 4 + band), (ox - 11, tail_y + 3), (ox - 7, tail_y + 3)]), 'W', 'w')
    c.part(poly([(ox - 8, tail_y + 2), (ox - 12 - band, tail_y + 6 + band), (ox - 10 - band, tail_y + 8 + band), (ox - 7, tail_y + 4)]), 'w', 'w')

    # 2) 망토 (등 뒤)
    sh_y = top + 19
    c.part(poly([(ox - 5, sh_y), (ox + 4, sh_y), (ox + 2, sh_y + 8), (ox - 4 - sway, FOOT - 4), (ox - 11 - sway, FOOT - 6), (ox - 8, sh_y + 4)]), 'r', 'r', 'R')

    # 3) 뒷다리, 앞다리
    bf, ff = pose.get('legs', (ox - 3, ox + 2))
    hip_y = top + 30
    leg(c, ox - 2, hip_y, bf, front=False)
    leg(c, ox + 1, hip_y, ff, front=True)

    # 4) 몸통(옷) + 옷깃 + 가죽 띠 + 허리띠
    torso = poly([(ox - 5, sh_y), (ox + 5, sh_y), (ox + 6, hip_y + 1), (ox - 5, hip_y + 1)])
    c.part(torso, 'R', 'r', 'Q')
    for x in range(ox - 3, ox + 4):
        c.put(x, sh_y, 'W')
    for i in range(9):
        c.put(ox - 3 + i, sh_y + 2 + i, 'B')
        c.put(ox - 3 + i, sh_y + 3 + i, 'b')
    for x in range(ox - 4, ox + 6):
        c.put(x, hip_y - 1, 'B')
        c.put(x, hip_y, 'b')
    c.put(ox + 1, hip_y - 1, 'G')

    # 5) 어깨 망토 (앞으로 걸친 부분)
    c.part(poly([(ox - 7, sh_y - 1), (ox + 3, sh_y - 2), (ox + 2, sh_y + 4), (ox - 6, sh_y + 6)]), 'R', 'r', 'Q')

    # 6) 머리: 얼굴 → 머리카락 → 앞머리 → 머리띠 → 눈
    hx, hy = ox + 1, top + 10
    head = ellipse(hx, hy, 9, 8.5)
    c.part(head, 'S', 's', 'z')
    # 머리카락: 정수리·뒷머리 + 위·뒤로 삐친 뻗침
    hair = {(x, y) for (x, y) in head if y <= hy - 4 or x <= hx - 4 or (x <= hx - 1 and y <= hy + 1)}
    for tri in (
        [(hx - 9, hy - 3), (hx - 13, hy - 9), (hx - 4, hy - 8)],
        [(hx - 5, hy - 7), (hx - 6, hy - 12), (hx + 2, hy - 8)],
        [(hx + 1, hy - 8), (hx + 6, hy - 11), (hx + 7, hy - 5)],
        [(hx - 9, hy - 2), (hx - 13, hy + 3), (hx - 7, hy + 4)],
        [(hx - 7, hy + 2), (hx - 9, hy + 7), (hx - 4, hy + 5)],
    ):
        hair |= poly(tri)
    c.part(hair, 'H', 'i', 'h')
    # 머리띠: 이마를 가로지른다
    band_rows = (hy - 4, hy - 3)
    for x in range(hx - 10, hx + 10):
        for y in band_rows:
            if (x, y) in head or (x, y) in hair:
                c.put(x, y, 'W' if y == band_rows[0] else 'w')
    # 앞머리: 머리띠 아래로 흘러내리는 몇 가닥
    for tri in ([(hx, hy - 3), (hx + 3, hy - 3), (hx + 1, hy + 1)], [(hx + 3, hy - 3), (hx + 6, hy - 3), (hx + 5, hy)],
                [(hx - 3, hy - 3), (hx, hy - 3), (hx - 1, hy + 2)]):
        c.part(poly(tri), 'H', 'i', 'h')
    # 눈썹·눈 (오른쪽을 보는 3/4 각도)
    for x in range(hx + 3, hx + 7):
        c.put(x, hy - 1 + (1 if x == hx + 3 else 0), 'i')
    for (x, y) in ((hx + 4, hy + 1), (hx + 5, hy + 1), (hx + 4, hy + 2), (hx + 5, hy + 2), (hx + 4, hy + 3)):
        c.put(x, y, 'O')
    c.put(hx + 5, hy + 1, 'E')
    c.put(hx + 6, hy + 5, 's'); c.put(hx + 7, hy + 5, 's')   # 입
    c.put(hx + 2, hy + 3, 'X'); c.put(hx + 3, hy + 4, 'X')   # 뺨의 흉터
    c.put(hx + 8, hy + 1, 's')                                # 코끝

    # 7) 앞팔 + 검 (검은 팔보다 뒤에 그려 손이 칼자루를 쥔 것처럼)
    hand = pose.get('hand', (ox + 7, top + 29))
    shoulder = (ox + 2, sh_y + 2)
    if pose.get('sword_front'):
        arm = thick_line(shoulder[0], shoulder[1], hand[0], hand[1], 3)
        c.part(arm, 'R', 'r', 'Q')
        sword(c, hand[0], hand[1], pose['ang'])
    else:
        sword(c, hand[0], hand[1], pose['ang'])
        arm = thick_line(shoulder[0], shoulder[1], hand[0], hand[1], 3)
        c.part(arm, 'R', 'r', 'Q')
    c.part(rect(hand[0] - 1, hand[1] - 1, hand[0], hand[1]), 'S', 's')

    # 8) 베기 잔상 (공격 프레임)
    if pose.get('smear'):
        cx, cy, r, a0, a1 = pose['smear']
        for i in range(60):
            a = a0 + (a1 - a0) * i / 59
            for rr in (r, r - 1):
                c.put(int(round(cx + math.cos(a) * rr)), int(round(cy + math.sin(a) * rr)), 'F' if rr == r else 'L')
    return c.image()


# ───────── 동작 ─────────
def poses():
    deg = math.radians
    base = dict(legs=(16, 21), hand=(27, 31), ang=deg(62), sword_front=False)
    anims = {}
    # 대기: 몸을 아주 살짝 들썩이고 망토·머리띠가 흔들린다 (숨쉬기는 sprite-gen breathe로 덧입힌다)
    anims['idle'] = [dict(base, cloak=s, band=b) for s, b in ((0, 0), (1, 1), (1, 2), (0, 1))]
    # 걷기: 4프레임 (앞발 내딛기 → 교차 → 뒷발 내딛기 → 교차)
    walk = []
    for legs, bob, s, b in (((13, 24), 0, 2, 2), ((17, 20), -1, 1, 1), ((22, 15), 0, 2, 2), ((18, 19), -1, 1, 1)):
        hand = (27, 31 + bob)
        walk.append(dict(base, legs=legs, bob=bob, cloak=s, band=b, hand=hand))
    anims['walk'] = walk
    # 공격: 들어 올림 → 정점 → 내려베기(잔상) → 마무리 → 복귀
    anims['attack'] = [
        dict(base, hand=(18, 22), ang=deg(-130), lean=-1, legs=(14, 22), cloak=1, band=1),
        dict(base, hand=(21, 14), ang=deg(-80), lean=-1, legs=(14, 23), cloak=2, band=2, sword_front=True),
        dict(base, hand=(31, 27), ang=deg(15), lean=2, legs=(13, 26), cloak=3, band=3, sword_front=True,
             smear=(25, 24, 17, deg(-100), deg(25))),
        dict(base, hand=(30, 33), ang=deg(55), lean=2, legs=(13, 26), cloak=3, band=3, sword_front=True),
        dict(base, hand=(28, 32), ang=deg(60), lean=1, legs=(15, 22), cloak=1, band=1),
    ]
    # 피격: 뒤로 젖힘
    anims['hit'] = [dict(base, lean=-2, legs=(15, 20), hand=(24, 33), ang=deg(80), cloak=-1, band=3)]
    return anims


def main(out):
    os.makedirs(os.path.join(out, 'frames'), exist_ok=True)
    anims = poses()
    sheet_rows = []
    for name, ps in anims.items():
        frames = [draw(p) for p in ps]
        for i, f in enumerate(frames):
            f.save(os.path.join(out, 'frames', f'{name}_{i}.png'))
        sheet_rows.append((name, frames))
    print('frames:', {k: len(v) for k, v in anims.items()})


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'out-baren')
