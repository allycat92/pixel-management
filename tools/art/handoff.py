#!/usr/bin/env python3
"""GPT handoff packages for battle sprites → art/requests/phase3/<id>/

Each package is everything the GPT image model needs for ONE character (see
art/requests/gpt_handoff_notes.md): the owner's chosen NovelAI design draft (design only), the
approved portrait (face only), posekit pose guides for the four key poses, and guide_strip.png —
the four guides laid out exactly as the deliverable must be (1536x1024, flat #FF00FF, feet on a
common baseline at 85% of the height, idle figure 55% of the height, figures never touching).
README.md = Korean notes for the owner + the English prompt block for GPT.

  python3 tools/art/handoff.py                       # every character in CHARS
  python3 tools/art/handoff.py captain_fixer --check # one package; --check also prints the layout

Needs art/requests/phase3.json (node tools/art/requests.js) for names and game colours.
Deterministic: the same inputs give byte-identical files. Concept and portrait files are copied
byte-for-byte (git stores identical blobs once). To add a character, add a CHARS entry
(weapon / frames from tools/pixelart/posekit.py, concept files, notes) and rerun.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'pixelart'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'art'))
import posekit as pk  # noqa: E402

REQ = os.path.join(ROOT, 'art', 'requests', 'phase3.json')
OUT = os.path.join(ROOT, 'art', 'requests', 'phase3')
CONCEPTS = os.path.join(ROOT, 'art', 'concepts')
BRANCH = 'claude/dot-fantasy-management-game-saupju'

SW_, SH_ = 1536, 1024          # deliverable size
BASELINE = round(0.85 * SH_)   # feet baseline y (870)
HEAD_PX = 110                  # px per head unit in the strip, the same for every character (4 heads = 440 px standing;
                               # the idle crouch is ~39% of the height). 55% does not fit 4 wide-stance poses + weapons.
GAP = 32                       # min px between two figures (any row within GAP rows)
MARGIN = 24                    # min px between a figure and the image border
HEADS = 4.0
MAGENTA = (255, 0, 255)
ANCHOR_FILE = 'art/inbox/sheet_captain_blademaster.png'

POSES = [('idle', 'guide_1_idle.png', '대기', 'idle'),
         ('windup', 'guide_2_windup.png', '공격 준비', 'attack wind-up'),
         ('strike', 'guide_3_strike.png', '공격 타격', 'attack strike'),
         ('hit', 'guide_4_hit.png', '피격', 'hit reaction')]

# ───────── per character ─────────
# weapon: posekit weapon; frames: posekit frame per key pose; concepts: package name → art/concepts path.
# keep / fix: English (goes to GPT); ko: short Korean summary for the owner; pose: per-pose English notes.
CHARS = {
    'captain_blademaster': dict(
        en='Baren', order=1, anchor=True, weapon='katana',
        frames=dict(idle='idle_0', windup='attack_1', strike='attack_2', hit='hit_0'),
        concepts={'concept.png': 'captain_blademaster/concept_05.png',
                  'concept_pixel.png': 'captain_blademaster/concept_08.png'},
        weapon_desc='a katana (slim curved single-edged sword, dark wrapped hilt, small round guard), held with both hands',
        keep=['messy dark-brown hair', 'white headband with two long tails (keep the tails short enough to stay clear of the neighbouring figure)',
              'thin scar across one cheek', 'fitted dark-navy tunic', 'dark-crimson half cape / hip wrap hanging on one side',
              'leather belt and a cross strap', 'dark trousers, brown boots', 'calm, focused expression'],
        fix=['concept.png (#5) is the LOOK reference; concept_pixel.png (#8) shows how SIMPLE the shapes must stay: '
             'big clear shapes, few folds, few small details, so it survives downscaling to 64 px',
             'this image becomes the STYLE ANCHOR for the eight other captains: keep it clean and exemplary'],
        pose=dict(idle='katana held diagonally in front, both hands on the hilt, as in the guide',
                  windup='katana raised high behind the head with both hands, as in the guide',
                  strike='diagonal downward cut, arms and blade fully extended forward, as in the guide',
                  hit='recoiling backwards, wincing, katana still in hand'),
        ko=dict(keep='헝클어진 짙은 갈색 머리, 꼬리가 긴 흰 머리띠, 뺨의 흉터, 짙은 남색 상의, 한쪽에 늘어진 짙은 진홍 반망토, 가죽 띠, 갈색 장화, 카타나(두 손).',
                fix='#5 = 생김새 기준, #8 = 도트로 줄여도 살아남을 만큼 단순한 형태의 기준. 이 그림이 나머지 8명의 화풍 기준(앵커)이 된다.'),
    ),
    'captain_ironwall': dict(
        en='Briginda', order=2, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='attack_1', strike='attack_2', hit='hit_0'),
        concepts={'concept.png': 'captain_ironwall/concept_08.png'},
        weapon_desc='a spiked mace (morning star) in the near hand and a large tower shield on the far arm',
        keep=['open steel helmet', 'long auburn hair in a thick braid', 'scar across the nose',
              'slate-grey plate armour with gold trim', 'grey tabard', 'leather belt', 'dark trousers, brown boots',
              'tall rectangular tower shield with a gold rim', 'spiked mace (morning star)', 'broad shoulders, sturdy build'],
        fix=['make the BRAID clearly visible (over the near shoulder or hanging down the back so it shows in the silhouette)',
             'the guide shows a small round shield: draw the tall tower shield instead, on the same arm and in the same place; '
             'it may cover part of the body but never the face',
             'the guide shows a sword: draw the spiked mace in that hand, same grip and angle'],
        pose=dict(idle='shield raised forward, mace ready, as in the guide',
                  windup='mace raised high behind the head, shield kept forward',
                  strike='mace smashing down and forward at full extension, shield pulled in',
                  hit='recoiling backwards behind the shield, wincing'),
        ko=dict(keep='강철 투구, 땋은 적갈색 긴 머리, 콧등 흉터, 금테 두른 회청색 판금갑옷, 회색 겉옷, 금테 탑실드, 철퇴(모닝스타).',
                fix='땋은 머리가 실루엣에서 보이게. 가이드의 작은 원형 방패 → 같은 팔·같은 자리에 큰 탑실드, 칼 → 철퇴.'),
    ),
    'captain_tactician': dict(
        en='Isabel', order=3, weapon='staff',
        frames=dict(idle='cast_0', windup='cast_1', strike='cast_2', hit='hit_0'),
        concepts={'concept.png': 'captain_tactician/concept_07.png'},
        weapon_desc="a slim black officer's cane / baton with a gold knob (no orb, no crystal)",
        keep=['black tricorne hat with gold trim', 'long straight dark-indigo hair', 'charcoal long military coat',
              'gold epaulettes and gold buttons', 'leather belt', 'dark trousers, black boots', 'calm, sharp expression'],
        fix=['the draft is about 6 heads tall: draw her 4 HEADS tall like everyone else (bigger head, shorter legs and coat, as the guide)',
             'the guide staff is a placeholder: draw a slim officer\'s cane instead; it may be shorter than the guide staff, '
             'but the hand that holds it stays exactly where the guide hand is',
             'the coat must not be longer than the knees, so the legs still read in the wide stance'],
        pose=dict(idle='upright commander stance, cane planted at her side, as in the guide',
                  windup='cane raised, free hand lifted (about to give an order)',
                  strike='commanding gesture: free arm thrust forward, pointing with the index finger at the enemy',
                  hit='recoiling backwards, wincing, hat still on'),
        ko=dict(keep='금테 검은 삼각모, 곧은 짙은 남보라 긴 머리, 숯색 긴 군복 코트, 금 견장·금단추, 검은 장화, 침착한 표정.',
                fix='초안은 약 6등신 → 4등신으로. 지팡이는 가늘고 짧은 장교 지휘봉(금 손잡이)으로, 손 위치는 가이드 그대로. 시전 자세(cast)로 지휘.'),
    ),
    'captain_lancer': dict(
        en='Roderick', order=4, weapon='spear',
        frames=dict(idle='idle_0', windup='attack_1', strike='attack_3', hit='hit_0'),
        concepts={'concept.png': 'captain_lancer/concept_b_12.png'},
        weapon_desc='a straight knight\'s lance with a small blue pennant near the tip',
        keep=['ornate steel helmet with a blue plume, visor raised so the face shows', 'short brown hair, stubble, determined eyes',
              'polished blue plate armour with gold trim', 'worn white surcoat with a simple blue lion emblem',
              'tattered red cape', 'steel greaves'],
        fix=['ON FOOT: he is "the knight who lost his horse" - no horse in this sheet',
             'keep the lance exactly as long as the guide spear so it never touches the neighbouring figure or the border',
             'simplify the lion emblem to one readable blue shape; the cape stays compact (no huge flowing cape)'],
        pose=dict(idle='lance held diagonally forward with both hands, as in the guide',
                  windup='lance drawn back level at the hip, ready to thrust',
                  strike='deep lunge, lance thrust forward at full extension',
                  hit='recoiling backwards, wincing, lance still in hand'),
        ko=dict(keep='파란 깃털 장식 투구(얼굴 보이게), 갈색 짧은 머리·수염, 금테 파란 판금, 파란 사자 문장의 낡은 흰 겉옷, 해진 붉은 망토, 파란 깃발 달린 랜스.',
                fix='말 없이 걷는 기사(본 시트). 랜스 길이는 가이드 창과 같게, 문장은 단순하게, 망토는 작게.'),
        mounted=dict(
            file='sheet_captain_lancer_mounted.png', concept='captain_lancer/concept_a_05.png',
            id='sheet/captain/lancer_mounted'),
    ),
    'captain_huntress': dict(
        en='Kiara', order=5, weapon='bow',
        frames=dict(idle='idle_0', windup='attack_2', strike='attack_3', hit='hit_0'),
        concepts={'concept.png': 'captain_huntress/concept_04.png'},
        weapon_desc='a short recurve bow, quiver of arrows on the back',
        keep=['long auburn hair in a high ponytail', 'ochre headband', 'freckles', 'olive-green hooded tunic',
              'brown leather vest', 'rope coil on the belt', 'quiver on the back', 'dark trousers, brown boots'],
        fix=['the draft bow is very large: draw a short bow the size of the guide bow',
             'an arrow appears ONLY on the drawn bow in the wind-up; after the release (strike) there is NO flying arrow (the engine draws projectiles)'],
        pose=dict(idle='bow held low in front, ready, as in the guide',
                  windup='full draw: arrow nocked, string pulled back to the cheek',
                  strike='release: bow arm extended, string straight, drawing hand flung back, no arrow',
                  hit='recoiling backwards, wincing, bow still in hand'),
        ko=dict(keep='높게 묶은 적갈색 포니테일, 황토색 머리띠, 주근깨, 올리브색 후드 상의, 가죽 조끼, 허리의 밧줄 뭉치, 등의 화살통, 짧은 활.',
                fix='초안의 큰 활 → 가이드 크기의 짧은 활. 화살은 당길 때(준비)만, 쏜 뒤(타격)에는 날아가는 화살 없음(엔진이 그린다).'),
    ),
    'captain_hedgemage': dict(
        en='Felix', order=6, weapon='staff',
        frames=dict(idle='idle_0', windup='cast_1', strike='cast_2', hit='hit_0'),
        concepts={'concept.png': 'captain_hedgemage/concept_08.png'},
        weapon_desc='a long, slightly crooked wooden staff (plain wooden top instead of the guide\'s blue orb)',
        keep=['short messy blond hair', 'worn, patched pointed wizard hat', 'purple robe', 'rope belt', 'satchel on the hip',
              'dark trousers, brown boots', 'cheerful, young face'],
        fix=['the draft\'s bright yellow trim must be muted to a dull ochre gold (the game accent #e8c86a, desaturated)',
             'NO fire, glow or magic effect anywhere: the engine draws the spell VFX; keep the casting hand open and empty',
             'the hat must stay inside the figure\'s space (no huge brim that reaches the neighbouring figure)'],
        pose=dict(idle='staff held diagonally at his side, as in the guide',
                  windup='staff raised high, free hand lifted, gathering power',
                  strike='free hand thrust forward, palm open toward the enemy (casting), staff held up behind',
                  hit='recoiling backwards, wincing, hat still on'),
        ko=dict(keep='헝클어진 금발, 기운 자국 있는 낡은 고깔모자, 보라색 로브, 밧줄 허리띠, 허리 가방, 갈색 장화, 나무 지팡이.',
                fix='밝은 노란 테두리 → 탁한 황토 금색. 불꽃·빛 등 효과 금지(엔진이 그린다), 시전하는 손은 빈 손바닥. 시전 자세(cast).'),
    ),
    'captain_fieldmedic': dict(
        en='Magda', order=7, weapon='staff',
        frames=dict(idle='idle_0', windup='cast_1', strike='cast_2', hit='hit_0'),
        concepts={'concept.png': 'captain_fieldmedic/concept_03.png'},
        weapon_desc='a long-handled spiked mace (the guide staff is the handle; the orb end of the guide staff is where the spiked iron head goes)',
        keep=['long black hair tied in a high ponytail', 'tan skin', 'bandage around the forehead', 'long field coat',
              'dark-red scarf', 'dark-red apron / under-dress', 'pouches on the belt', 'dark trousers, brown boots',
              'stern, determined expression'],
        fix=['REMOVE the white cross: the armband is a PLAIN dark-red armband, no symbol on it (also not on anything else)',
             'the draft coat is near-white: paint it warm grey-beige (game colour #e8e4d8 with hue-shifted shading), never pure white',
             'NO healing glow or orb: the engine draws the heal VFX; the raised hand is open and empty'],
        pose=dict(idle='mace held at her side, ready, as in the guide',
                  windup='mace raised, free hand lifted (gathering a heal)',
                  strike='free hand pushed forward, palm open (healing / blessing), mace held up behind',
                  hit='recoiling backwards, wincing'),
        ko=dict(keep='높게 묶은 검은 긴 머리, 갈색 피부, 이마 붕대, 긴 야전 코트, 짙은 빨강 스카프·앞치마, 허리 주머니, 긴 자루 철퇴.',
                fix='완장의 흰 십자 제거(무늬 없는 짙은 빨강 완장). 코트는 흰색이 아니라 따뜻한 회베이지. 치유 빛 금지(엔진). 시전 자세(cast).'),
    ),
    'captain_fixer': dict(
        en='Jin', order=8, weapon='none',
        frames=dict(idle='idle_0', windup='attack_1', strike='attack_2', hit='hit_0'),
        concepts={'concept.png': 'captain_fixer/concept_05.png'},
        weapon_desc='ONE short dagger in the near (character\'s right) hand, REVERSE grip (blade pointing down out of the little-finger side)',
        keep=['black hood', 'grey scarf over the mouth', 'narrow eyes', 'short black hair', 'black leather jacket with grey trim',
              'leather belt and a cross strap', 'dark trousers, black boots', 'lean, agile build'],
        fix=['exactly ONE dagger, reverse grip, in the near hand; the other hand is empty',
             'the all-black outfit vanishes on the dark battlefield: paint large areas in dark charcoal / blue-grey (not black), '
             'add a clear cool rim light on the upper-left edges and use a slightly LIGHTER outline (dark grey-violet) around the silhouette',
             'the guide is unarmed (hands together where a sword grip would be): put the dagger in the near hand at that spot'],
        pose=dict(idle='low ready stance, dagger hand in front, as in the guide',
                  windup='dagger hand raised high (about to stab down)',
                  strike='lunging slash forward and down, dagger arm fully extended',
                  hit='recoiling backwards, wincing'),
        ko=dict(keep='검은 후드, 입을 가린 회색 스카프, 가는 눈, 검은 짧은 머리, 회색 테두리 검은 가죽 재킷, 교차 띠, 검은 장화.',
                fix='단검은 하나, 역수로, 가까운 쪽 손. 검정 옷이 어두운 전장에 묻히지 않게 짙은 숯색·청회색 + 왼쪽 위 림 라이트 + 조금 밝은 외곽선.'),
    ),
    'captain_veteran': dict(
        en='Harald', order=9, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='attack_1', strike='attack_2', hit='hit_0'),
        concepts={'concept.png': 'captain_veteran/concept_03.png'},
        weapon_desc='an arming sword in the near hand and a round wooden shield on the far arm',
        keep=['dented steel helmet', 'short white hair and a full white beard', 'old scars on the face',
              'olive-grey quilted gambeson over chainmail', 'leather belt', 'dark trousers, worn boots',
              'round wooden shield with an iron boss', 'kind but tough old face'],
        fix=['the draft is about 5 heads tall: draw him 4 HEADS tall like everyone else',
             'old but sturdy: slightly stooped shoulders are fine, the stance stays as wide as the guide'],
        pose=dict(idle='shield up, sword ready, as in the guide',
                  windup='sword raised high behind the head, shield kept forward',
                  strike='sword cutting down and forward at full extension',
                  hit='recoiling backwards behind the shield, wincing'),
        ko=dict(keep='찌그러진 강철 투구, 흰 짧은 머리·흰 수염, 얼굴 흉터, 쇠사슬 위 올리브회색 누비 갑옷, 둥근 나무 방패, 한손검.',
                fix='초안은 약 5등신 → 4등신으로. 늙었지만 단단하게, 자세 폭은 가이드 그대로.'),
    ),
}

STYLE_EN = [
    'high-quality HD pixel art for a modern 2D fantasy tactics game (crisp pixel clusters, no blur, no painterly rendering)',
    f'{int(HEADS)} heads tall (head = 1/4 of the standing height), exactly the proportions and limb lengths of the guide; NOT chibi, NOT realistic',
    'front three-quarter view, facing RIGHT; light from the upper left',
    'muted, desaturated, hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones',
    'dark, desaturated, NON-black outline used selectively (no thick uniform black lineart), soft rim light on one side',
    'readable at 1x game size (the idle figure becomes ~64 px tall on a dark battlefield): big clear shapes, strong silhouette, few tiny details',
]
SPEC_EN = [
    'ONE PNG, 1536x1024 (landscape), the SAME character drawn 4 times in one row, left to right: idle, wind-up, strike, hit',
    'each figure exactly where guide_strip.png has it: same size, same scale, same pose, same limb lengths',
    f'all four pairs of feet on one common baseline at y = {BASELINE} (85% of the height); the idle figure is about {{idle_px}} px tall '
    f'({{idle_pct}}% of the height, {HEAD_PX} px per head) - the same size for every character',
    f'figures and weapons never touch each other or the image border (keep >= {GAP} px between figures)',
    'background: perfectly flat solid magenta #FF00FF everywhere (or transparent) - no gradient, floor, cast shadow or scenery',
    'NO text, labels, numbers, frames, grid lines, watermark; NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles)',
]
DONT_COPY_EN = ('from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, '
                'silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail '
                '- the NovelAI drafts are not consistent with each other')
CHECK_EN = [
    'image is 1536x1024, background exactly #FF00FF (or transparent), nothing else on it',
    '4 figures in one row, idle / wind-up / strike / hit, matching the guide poses',
    'feet of all four on the same baseline (~85% height); same size in all four; idle ~{idle_pct}% of the height (~{idle_px} px)',
    '4 heads tall; front three-quarter view facing right; light from the upper left',
    'same face, hair, outfit, colours and weapon in all four poses; exactly the weapons listed (no extra weapons)',
    'every "fix" above applied',
    'no text, no floor, no shadow, no effects, no projectiles; figures do not touch each other or the border',
    'reads clearly when shrunk to 64 px tall on a dark background',
]


# ───────── rendering ─────────

def save_png(im, path):
    """lossless; palette PNG when the image has <= 256 colours (posekit guides do), else RGB."""
    arr = np.asarray(im.convert('RGB'))
    cols, inv = np.unique(arr.reshape(-1, 3), axis=0, return_inverse=True)
    if len(cols) <= 256:
        p = Image.fromarray(inv.reshape(arr.shape[:2]).astype(np.uint8), 'P')
        p.putpalette(cols.astype(np.uint8).ravel().tolist())
        p.save(path, optimize=True)
    else:
        Image.fromarray(arr, 'RGB').save(path, optimize=True)


def builds_for(weapon):
    B = pk.Body(HEADS)
    F = pk.frames(weapon, B)
    return B, {n: pk.build(F[n], B, weapon) for n in pk.ALL_FRAMES}


def guide_frame(builds, frame):
    """the 832x1216 guide exactly as `posekit.py --weapon W` writes guide_<frame>.png."""
    gs, gox, goy = pk.fit(builds, pk.GW, pk.GH, pk.GH * pk.GUIDE_FEET, pk.GH * pk.GUIDE_BODY, 'idle_0', 0.025 * pk.GW)
    return pk.render_guide(builds[frame][1], pk.Raster(pk.GW, pk.GH, gs, gox[frame], goy, 2), 5.0)


def render_tight(parts, s, outline_px, pad=8):
    """one pose at s px/head on its own canvas. → (rgb array, mask, floor row)."""
    x0, y0, x1, y1 = pk.bbox(parts)
    w = int(np.ceil((x1 - x0) * s)) + 2 * pad
    h = int(np.ceil((y1 - y0) * s)) + 2 * pad
    ox, oy = pad - x0 * s, pad - y0 * s
    rgb = np.asarray(pk.render_guide(parts, pk.Raster(w, h, s, ox, oy, 2), outline_px)).copy()
    mask = np.any(rgb != np.array(MAGENTA, np.uint8), axis=-1)
    ys, xs = np.nonzero(mask)
    t, b, l, r = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return rgb[t:b, l:r], mask[t:b, l:r], oy - t


def profiles(mask, floor, gap):
    """per strip row: leftmost / rightmost pixel (strip rows, pose-local x), dilated by gap rows."""
    L = np.full(SH_, np.inf)
    R = np.full(SH_, -np.inf)
    top = int(round(BASELINE - floor))
    for y in range(mask.shape[0]):
        xs = np.nonzero(mask[y])[0]
        yy = top + y
        if len(xs) and 0 <= yy < SH_:
            L[yy], R[yy] = xs[0], xs[-1]
    Ld, Rd = L.copy(), R.copy()
    for d in range(1, gap + 1):
        Ld[d:] = np.minimum(Ld[d:], L[:-d]); Ld[:-d] = np.minimum(Ld[:-d], L[d:])
        Rd[d:] = np.maximum(Rd[d:], R[:-d]); Rd[:-d] = np.maximum(Rd[:-d], R[d:])
    return L, R, Ld, Rd, top


def layout(poses):
    """x offsets: pack left→right with >= GAP px between any two figures, then spread the spare
    width evenly over the gaps between figures (outer margins stay MARGIN).
    → (xs, spare) or (None, spare<0) if it cannot fit."""
    prof = [profiles(m, fl, GAP) for _, m, fl in poses]
    xs = [0.0]
    for j in range(1, len(poses)):
        need = 0.0
        for i in range(j):
            d = prof[i][3] - prof[j][0]          # dilated right of i - left of j
            d = d[np.isfinite(d)]
            if len(d):
                need = max(need, xs[i] + d.max() + GAP)
        xs.append(need)
    left = min(xs[k] + 0 for k in range(len(poses)))
    right = max(xs[k] + poses[k][1].shape[1] for k in range(len(poses)))
    spare = SW_ - 2 * MARGIN - (right - left)
    if spare < 0:
        return None, spare
    step = spare / max(len(poses) - 1, 1)
    return [MARGIN - left + x + step * k for k, x in enumerate(xs)], spare


def strip_image(builds, frames):
    """guide_strip.png: the 4 key poses at one scale on 1536x1024 magenta. → (image, info)."""
    s = HEAD_PX
    shrink = 1.0
    while True:
        ss = s * shrink
        poses = [render_tight(builds[f][1], ss, max(2.0, 5.0 * ss / 243.7)) for f in frames]
        xs, spare = layout(poses)
        if xs is not None:
            break
        shrink *= 0.97
    if shrink < 1:
        print(f'  WARNING: the four poses do not fit at {HEAD_PX} px/head; this strip is drawn at {ss:.1f} px/head')
    canvas = np.empty((SH_, SW_, 3), np.uint8)
    canvas[:] = MAGENTA
    boxes = []
    for (rgb, m, fl), x in zip(poses, xs):
        x0 = int(round(x))
        y0 = int(round(BASELINE - fl))
        h, w = m.shape
        assert x0 >= MARGIN - 1 and x0 + w <= SW_ - MARGIN + 1 and y0 >= MARGIN - 1 and y0 + h <= SH_, (x0, y0, w, h)
        view = canvas[y0:y0 + h, x0:x0 + w]
        view[m] = rgb[m]
        boxes.append((x0, y0, x0 + w, y0 + h))
    idle_h = -pk.bbox(builds['idle_0'][1], pk.is_body)[1] * ss
    info = dict(px_per_head=round(ss, 1), idle_px=int(round(idle_h)), idle_pct=round(100 * idle_h / SH_), shrink=round(shrink, 3),
                boxes=boxes, spare=int(spare))
    return Image.fromarray(canvas, 'RGB'), info


def mounted_layout(concept_path):
    """guide_mounted_layout.png: 1536x1024 2x2 grid; the concept's silhouette (flat grey) in the strike
    quadrant (bottom-left) only, as a size / baseline reference. Hooves at 90% of each quadrant."""
    from sheets import matte
    arr = np.asarray(Image.open(concept_path).convert('RGBA'))
    _, a, _ = matte(arr)
    m = a > 0.5
    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    qw, qh = SW_ // 2, SH_ // 2
    sc = min((qw - 2 * MARGIN) / m.shape[1], 0.62 * qh / m.shape[0])
    nw, nh = int(round(m.shape[1] * sc)), int(round(m.shape[0] * sc))
    sm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((nw, nh), Image.Resampling.BOX)) > 127
    canvas = np.empty((SH_, SW_, 3), np.uint8)
    canvas[:] = MAGENTA
    x0 = (qw - nw) // 2
    y0 = qh + int(round(0.9 * qh)) - nh
    canvas[y0:y0 + nh, x0:x0 + nw][sm] = (88, 80, 104)
    return Image.fromarray(canvas, 'RGB'), dict(w=nw, h=nh, box=(x0, y0, x0 + nw, y0 + nh))


# ───────── README ─────────

def colours_line(it):
    c = it.get('colors') or {}
    return ', '.join(f'{k} {v}' for k, v in c.items())


def readme(cid, C, it, info, has_portrait, mounted_item=None, minfo=None):
    key = cid.split('_', 1)[1]
    name = it['name']
    fr = C['frames']
    concept_files = list(C['concepts'])
    L = [f'# {name} — GPT handoff (`{cid}`)', '',
         '> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.',
         '> 공통 규칙: `art/requests/gpt_handoff_notes.md`, `art/STYLE.md`(전투 캐릭터). 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.', '',
         '## 주인용 요약 (한국어)', '',
         f'- 순서: **{C["order"]}번째**' + (' — **화풍 기준(앵커)**: 이 그림을 먼저 받아 승인한 뒤 나머지 8명을 맞춘다.' if C.get('anchor') else
                                         f' — 승인된 바렌 그림(`{ANCHOR_FILE}`)의 화풍에 맞춘다.'),
         f'- 결과 파일: `art/inbox/{it["file"]}` (id `{it["id"]}`)' + (f', 추가 선택: `art/inbox/{mounted_item["file"]}`' if mounted_item else ''),
         f'- 무기: posekit `{C["weapon"]}` 마네킹 → {C["weapon_desc"]}',
         f'- 자세(posekit 프레임): ① 대기 `{fr["idle"]}` ② 공격 준비 `{fr["windup"]}` ③ 공격 타격 `{fr["strike"]}` ④ 피격 `{fr["hit"]}`',
         f'- 초안에서 가져올 것: {C["ko"]["keep"]}',
         f'- 고칠 것: {C["ko"]["fix"]}',
         '- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.',
         f'- 가이드 띠: 머리 하나 = {info["px_per_head"]} px (모든 캐릭터 같음), 대기 자세 키 약 {info["idle_px"]} px = 그림 높이의 {info["idle_pct"]}%, 발 기준선 y={BASELINE}.',
         '', '### 파일', '',
         '| 파일 | 내용 |', '|---|---|']
    L.append('| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |')
    if 'concept_pixel.png' in concept_files:
        L.append('| `concept_pixel.png` | #8 — 도트로 줄여도 살아남는 단순한 형태의 기준 |')
    if has_portrait:
        L.append('| `portrait.png` | 승인된 초상화 (얼굴·머리만 참고) |')
    for _, fn, ko, _ in POSES:
        L.append(f'| `{fn}` | posekit 가이드 832x1216 — {ko} |')
    L.append('| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |')
    if mounted_item:
        L.append('| `concept_mounted.png` | 기마 초안 #5 (추가 선택 시트용) |')
        L.append('| `guide_mounted_layout.png` | 기마 시트 2x2 배치·크기 참고 (왼쪽 아래 칸에만 실루엣) |')
    L += ['', '### 받은 뒤 (Claude Code)', '', '```',
          f'python3 tools/art/sheets.py art/inbox/{it["file"]} --dry-run --work /tmp/sheets   # 미리보기',
          f'python3 tools/art/sheets.py art/inbox/{it["file"]}                                 # 등록']
    if mounted_item:
        L.append(f'python3 tools/art/sheets.py art/inbox/{mounted_item["file"]} --grid 2x2 --dry-run --work /tmp/sheets  # 기마(게임 미사용)')
    L += ['```', '', '## Prompt for GPT (English)', '', '```']
    P = []
    P.append(f'TASK: draw the battle-sprite strip of {C["en"]} ({name.split(" — ")[0]}, {key}), a mercenary captain. '
             f'Save it as art/inbox/{it["file"]} (do not rename).')
    refs = [f'art/requests/phase3/{cid}/guide_strip.png (layout + poses, the most important reference)',
            f'art/requests/phase3/{cid}/guide_1_idle.png .. guide_4_hit.png (the same poses, larger)',
            f'art/requests/phase3/{cid}/concept.png (DESIGN ONLY)']
    if 'concept_pixel.png' in concept_files:
        refs.append(f'art/requests/phase3/{cid}/concept_pixel.png (how simple the shapes must stay)')
    if has_portrait:
        refs.append(f'art/requests/phase3/{cid}/portrait.png (face and hair only)')
    if not C.get('anchor'):
        refs.insert(0, f'{ANCHOR_FILE} on the art-inbox branch = the APPROVED STYLE ANCHOR (Baren). Match its proportions, '
                       'rendering, outline, palette treatment, lighting and character scale exactly')
    P.append('REFERENCES:\n' + '\n'.join(f'  - {r}' for r in refs))
    P.append(f'CHARACTER: {C["weapon_desc"]}; ' + '; '.join(C['keep']) + '.')
    if colours_line(it):
        P.append(f'GAME COLOURS (keep close, muted): {colours_line(it)}.')
    P.append('FIX (do not reproduce the draft here):\n' + '\n'.join(f'  - {f}' for f in C['fix']))
    P.append('DO NOT COPY: ' + DONT_COPY_EN + '.')
    P.append('POSES (match the guide mannequin exactly; it only fixes pose, proportions, size and position - '
             'its colours, round head and plain clothes are placeholders):\n'
             + '\n'.join(f'  {i + 1}. {en}: {C["pose"][p]}' for i, (p, _, _, en) in enumerate(POSES)))
    P.append('STYLE:\n' + '\n'.join(f'  - {s}' for s in STYLE_EN))
    P.append('DELIVERABLE:\n' + '\n'.join(f'  - {s.format(**info)}' for s in SPEC_EN))
    P.append('SELF-CHECK before saving (redraw if any fails):\n' + '\n'.join(f'  [ ] {c.format(**info)}' for c in CHECK_EN))
    L += ['\n\n'.join(P), '```', '']
    if mounted_item:
        L += ['## 추가 선택: 기마 시트 (게임은 아직 쓰지 않는다)', '',
              '- 이야기는 "말을 잃은 기사"라 본 시트는 걷는 기사다. 기마 그림은 나중에 "군마를 되찾는" 형태가 생길 때를 위한 **추가 시트**다.',
              f'- 파일 `art/inbox/{mounted_item["file"]}`, id `{mounted_item["id"]}`, 1536x1024 **2x2 격자**, 넓은 칸 '
              f'({mounted_item.get("out", "")}). 9명이 끝난 **맨 마지막**에 그린다.',
              '- 초안 #5는 깨끗하지만 다른 기마 초안 다수는 말 머리가 둘이었다: **말 머리는 정확히 하나**.', '',
              '```',
              f'TASK (OPTIONAL, LAST): a mounted variant of the same knight (Roderick). Save as art/inbox/{mounted_item["file"]}. '
              'The game does not use it yet; it is for a possible later "regains a warhorse" form.',
              f'REFERENCES: {ANCHOR_FILE} (style anchor) and your approved art/inbox/{it["file"]} (same knight, same armour, colours and style); '
              f'art/requests/phase3/{cid}/concept_mounted.png (design only: armoured dark-brown warhorse with a blue caparison, couched lance, red cape); '
              f'art/requests/phase3/{cid}/guide_mounted_layout.png (size and baseline only).',
              'LAYOUT: one PNG 1536x1024 as a 2x2 grid of four equal quadrants (768x512), one pose per quadrant: top-left idle (horse standing, '
              'lance upright), top-right wind-up (horse rearing slightly, lance lowering), bottom-left strike (galloping charge, lance couched '
              'forward - like the silhouette), bottom-right hit (horse recoiling, rider leaning back). Every pose the same scale as the silhouette, '
              'hooves on a baseline at 90% of its quadrant height, nothing crossing into another quadrant or touching the border; the whole '
              'horse+rider+lance no wider than 1.6x its height.',
              'The horse has EXACTLY ONE head, four legs, one tail. The rider is 4 heads tall in proportion to the horse (the whole group is '
              'smaller than the on-foot sheet\'s figures so it fits a quadrant). '
              'Front three-quarter view facing right. Background flat #FF00FF, no floor, shadow, dust, text or effects. Same STYLE rules as above.',
              '```', '']
    return '\n'.join(L)


# ───────── main ─────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='*', help='package ids (default: all of CHARS)')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--check', action='store_true', help='print the strip layout of every package')
    a = ap.parse_args()
    with open(REQ, encoding='utf-8') as f:
        items = {it['file']: it for it in json.load(f)['items']}
    ids = a.ids or sorted(CHARS, key=lambda k: CHARS[k]['order'])
    cache = {}
    for cid in ids:
        if cid not in CHARS:
            sys.exit(f'unknown id {cid} (have {", ".join(CHARS)})')
        C = CHARS[cid]
        it = items.get(f'sheet_{cid}.png')
        if not it:
            sys.exit(f'sheet_{cid}.png is not in {os.path.relpath(REQ, ROOT)} — run node tools/art/requests.js')
        d = os.path.join(a.out, cid)
        os.makedirs(d, exist_ok=True)
        for dst, src in C['concepts'].items():
            shutil.copyfile(os.path.join(CONCEPTS, src), os.path.join(d, dst))
        portrait = os.path.join(ROOT, 'art', 'inbox', f'{cid}.png')
        if os.path.exists(portrait):
            shutil.copyfile(portrait, os.path.join(d, 'portrait.png'))
        if C['weapon'] not in cache:
            cache[C['weapon']] = builds_for(C['weapon'])
        _, builds = cache[C['weapon']]
        fr = [C['frames'][p] for p, _, _, _ in POSES]
        for (p, fn, _, _), f in zip(POSES, fr):
            save_png(guide_frame(builds, f), os.path.join(d, fn))
        strip, info = strip_image(builds, fr)
        save_png(strip, os.path.join(d, 'guide_strip.png'))
        mit = minfo = None
        if C.get('mounted'):
            M = C['mounted']
            mit = items.get(M['file'])
            if not mit:
                sys.exit(f'{M["file"]} is not in phase3.json — run node tools/art/requests.js')
            shutil.copyfile(os.path.join(CONCEPTS, M['concept']), os.path.join(d, 'concept_mounted.png'))
            mimg, minfo = mounted_layout(os.path.join(CONCEPTS, M['concept']))
            save_png(mimg, os.path.join(d, 'guide_mounted_layout.png'))
        with open(os.path.join(d, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme(cid, C, it, info, os.path.exists(portrait), mit, minfo))
        size = sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d))
        print(f'{cid}: {C["weapon"]} {"/".join(fr)}  {info["px_per_head"]} px/head, idle {info["idle_pct"]}%, '
              f'spare {info["spare"]} px, {size // 1024} KB')
        if a.check:
            print('   boxes', info['boxes'], ' mounted' if minfo else '', minfo or '')
    return 0


if __name__ == '__main__':
    sys.exit(main())
