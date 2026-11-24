#!/usr/bin/env python3
"""GPT handoff packages for battle sprites → art/requests/phase3/<id>/

Each package is everything the GPT image model needs for ONE character (see
art/requests/gpt_handoff_notes.md): the owner's chosen NovelAI design draft (design only), the
approved portrait (face only), four key-pose guides (the posekit 4-head mannequin; see KEY_POSES)
and guide_strip.png — the four guides laid out exactly as the deliverable must be (1536x1024, flat
#FF00FF, soles on y=870 = 85% of the height, 110 px per head for every character so the crouched
idle is ~400 px ≈ 39% of the height, >= 32 px of magenta between figures and from the border).
README.md = the English prompt block for GPT (per-character part first) + Korean notes for the owner.

  python3 tools/art/handoff.py                       # every character in CHARS
  python3 tools/art/handoff.py captain_fixer --check # one package; --check also prints the layout

Needs art/requests/phase3.json (node tools/art/requests.js) for names and game colours.
Deterministic: the same inputs give byte-identical files. Concept and portrait files are copied
byte-for-byte (git stores identical blobs once). To add a character, add a CHARS entry
(weapon / frames from tools/pixelart/posekit.py or KEY_POSES, concept files, notes) and rerun.
"""
import argparse
import copy
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
GAP = 32                       # min px of magenta between two figures, in any direction (2D, not per column:
                               # a weapon may reach over a neighbour's column; sheets.py splits by connected parts)
MARGIN = 32                    # min px between a figure and the image border
HEADS = 4.0
MAGENTA = (255, 0, 255)
ANCHOR_FILE = 'art/inbox/sheet_captain_blademaster.png'
REPO = 'https://github.com/allycat92/pixel-management'
RAW = f'https://raw.githubusercontent.com/allycat92/pixel-management/{BRANCH}'

POSES = [('idle', 'guide_1_idle.png', '대기', 'idle'),
         ('windup', 'guide_2_windup.png', '공격 준비', 'attack wind-up'),
         ('strike', 'guide_3_strike.png', '공격 타격', 'attack strike'),
         ('hit', 'guide_4_hit.png', '피격', 'hit reaction')]

# ───────── key poses (handoff variants of the posekit frames) ─────────
# posekit's generic frames keep one deep lunge for every pose, and some read badly as KEY poses at 64 px
# (katana wind-up blade hanging down behind the back, spear wind-up/strike/hit all level, every hit
# looking like a guard). The handoff uses these variants: wind-up = weight back, more upright; strike =
# step-in lunge with the arms extended; hit = torso thrown back, weight on the rear leg, weapon dropped.
# Same mannequin, bone lengths, IK and checks as posekit (pk.check); values are head units, x is
# absolute, heights come from at(x, h) (h relative to the shoulder line at 2.40, as in posekit.frames).
A_ = 0.12
KEY_BODY = {
    'windup': dict(hip=(-0.30, 1.46), lean=-0.10, footN=(-1.08, A_), footF=(0.72, A_), tilt=0.05, toeN=0.85),
    'strike': dict(hip=(0.42, 1.10), lean=0.30, footN=(-0.88, A_), footF=(1.42, A_), tilt=-0.08, toeN=0.85),
    'hit': dict(hip=(-0.46, 1.36), lean=-0.42, footN=(-1.06, A_), footF=(0.66, A_), tilt=-0.30,
                head_off=(-0.08, -0.02), faF=-10, toeN=0.85, kneeF=(1.0, -0.3)),
}
_ZS = {'shield': 58, 'boss': 58.5}
_ZM = {'blade': 'mid', 'handle': 'mid'}
# weapon → {frame name: (posekit base frame, KEY_BODY key or None, arms(at) → pose overrides)}
KEY_POSES = {
    'katana': {
        'key_windup': ('attack_1', 'windup', lambda a: dict(
            grip=a(-0.45, 3.32), wa=160, handN=('w', -0.12), handF=('w', -0.40), elbN=(-1.0, -0.2), elbF=(0.3, -1.0),
            z={'blade': 'back', 'handle': 'mid', 'farfore': 'back'})),
        'key_strike': ('attack_2', 'strike', lambda a: dict(
            grip=a(1.50, 2.10), wa=-28, handN=('w', -0.12), handF=('w', -0.40), elbN=(0.0, 1.0), elbF=(0.0, 1.0), z={})),
        'key_hit': ('hit_0', 'hit', lambda a: dict(
            grip=a(-0.70, 1.70), wa=-120, handN=('w', -0.12), handF=('p',) + a(0.40, 2.70), elbN=(-1.0, 0.0),
            elbF=(1.0, -0.2), z={'blade': 'back', 'handle': 'back'})),
    },
    'sword_shield': {
        'key_windup': ('attack_1', 'windup', lambda a: dict(
            grip=a(-0.50, 2.80), wa=150, handN=('w', -0.14), handF=('p',) + a(0.80, 2.10), elbN=(-0.4, -1.0),
            elbF=(0.4, 1.0), z={'blade': 'back'})),
        'key_strike': ('attack_2', 'strike', lambda a: dict(
            grip=a(1.30, 2.00), wa=-25, handN=('w', -0.14), handF=('p',) + a(0.55, 2.10), elbN=(0.0, 1.0),
            elbF=(0.4, 1.0), shield_ang=-20, z=dict(_ZS))),
        'key_hit': ('hit_0', 'hit', lambda a: dict(
            grip=a(-0.70, 1.70), wa=-115, handN=('w', -0.14), handF=('p',) + a(0.45, 2.40), elbN=(-1.0, 0.0),
            elbF=(1.0, 0.0), shield_ang=12)),
    },
    'spear': {
        'key_windup': ('attack_1', 'windup', lambda a: dict(      # spear pulled back: rear hand behind the hip
            grip=a(0.10, 1.72), wa=6, handN=('w', -0.62), handF=('w', 0.0), elbN=(-0.6, 1.0), elbF=(0.3, 1.0), z={})),
        'key_strike': ('attack_3', 'strike', lambda a: dict(      # both arms extended in the lunge
            grip=a(1.40, 2.10), wa=2, handN=('w', -0.62), handF=('w', 0.0), elbN=(0.0, 1.0), elbF=(0.0, 1.0), z={})),
        'key_hit': ('hit_0', 'hit', lambda a: dict(               # knocked back, spear tip thrown up
            grip=a(0.05, 2.20), wa=62, handN=('w', -0.62), handF=('w', 0.0), elbN=(-1.0, 0.3), elbF=(1.0, 0.0))),
    },
    'staff': {
        'key_strike': ('cast_2', 'strike', lambda a: dict(        # free arm extended forward (open palm), staff up behind
            grip=a(-0.55, 2.35), wa=96, handN=('w', 0.0), handF=('p',) + a(2.25, 2.45), elbN=(-0.6, 0.6),
            elbF=(0.0, 1.0), z=dict(_ZM))),
        'key_hit': ('hit_0', 'hit', lambda a: dict(
            grip=a(-0.70, 1.90), wa=100, handN=('w', 0.0), handF=('p',) + a(0.45, 2.70), elbN=(-1.0, 0.0),
            elbF=(1.0, -0.2), z=dict(_ZM))),
    },
    'bow': {
        'key_hit': ('hit_0', 'hit', lambda a: dict(
            grip=a(0.35, 1.50), wa=-55, handF=('w', 0.0), handN=('p',) + a(-1.45, 1.95), elbF=(0.5, 1.0),
            elbN=(-1.0, 0.0), nocked=False, draw=0.0)),
    },
    'none': {                                                    # fixer: one reverse-grip dagger in the near hand (drawn by add_dagger)
        'key_idle': ('idle_0', None, lambda a: dict(
            handN=('p',) + a(0.55, 1.95), handF=('p',) + a(0.90, 2.40), elbN=(-0.3, 1.0), elbF=(0.2, 1.0))),
        'key_windup': ('attack_1', 'windup', lambda a: dict(
            handN=('p',) + a(-0.20, 3.40), handF=('p',) + a(0.80, 2.25), elbN=(-1.0, 0.0), elbF=(0.3, 1.0), z={})),
        'key_strike': ('attack_2', 'strike', lambda a: dict(
            handN=('p',) + a(1.50, 1.95), handF=('p',) + a(0.05, 2.00), elbN=(0.0, 1.0), elbF=(-0.3, 1.0),
            z={'farfore': 'back'})),
        'key_hit': ('hit_0', 'hit', lambda a: dict(
            handN=('p',) + a(-1.30, 1.90), handF=('p',) + a(0.45, 2.70), elbN=(-1.0, 0.0), elbF=(1.0, -0.2), z={})),
    },
}


def key_frames(weapon, B, F):
    """KEY_POSES[weapon] as posekit pose dicts (added next to the posekit frames F)."""
    k = B.leg / 1.75
    ka = (B.upper + B.fore) / 1.18
    out = {}
    for name, (base, body, arms) in KEY_POSES.get(weapon, {}).items():
        p = copy.deepcopy(F[base])
        if body:
            b = dict(KEY_BODY[body])
            b['hip'] = (b['hip'][0], b['hip'][1] * k)
            b['footN'] = (b['footN'][0] * k, b['footN'][1])
            b['footF'] = (b['footF'][0] * k, b['footF'][1])
            p.update(b)
        h = p['hip'][1] / k
        p.update(arms(lambda x, y, h=h: (x, h * k + B.torso + (y - 2.40) * ka)))
        out[name] = p
    return out


def add_dagger(J, parts):
    """one short dagger in the near hand, reverse grip: the blade leaves the little-finger side and runs
    back along the forearm, angled a little away from it so it reads as a separate shape."""
    h, e = J['handN'], J['elbN']
    d = pk.rot(pk.norm(e - h), 0.55)
    n = np.array((d[1], -d[0]))
    b0, tip = h + d * 0.10, h + d * 0.66
    blade = pk.poly([b0 + n * 0.055, tip - d * 0.14 + n * 0.04, tip, tip - d * 0.14 - n * 0.04, b0 - n * 0.055])
    out = parts + [('dagger_grip', pk.cap(h - d * 0.16, h + d * 0.04, 0.045), 'wrap', 72.5, 0.03),
                   ('dagger_guard', pk.cap(b0 - n * 0.11, b0 + n * 0.11, 0.035), 'brass', 73.5, 0.03),
                   ('dagger', blade, 'steel', 73.4, 0.03)]
    return sorted(out, key=lambda p: p[3])


# ───────── per character ─────────
# weapon: posekit weapon; frames: posekit or KEY_POSES frame per key pose; concepts: package name → art/concepts path.
# weapon_desc / keep / fix / pose: English (goes to GPT); colours: labelled game colours (per garment, so a single
# "outfit" hex is never misread); ko: short Korean summary for the owner.
CHARS = {
    'captain_blademaster': dict(
        en='Baren', order=1, anchor=True, weapon='katana',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_blademaster/concept_05.png',
                  'concept_pixel.png': 'captain_blademaster/concept_08.png'},
        weapon_desc='ONE katana (slim curved single-edged sword, dark wrapped hilt, small round guard), held with both hands',
        keep=['messy dark-brown hair', 'white headband with two long tails (keep the tails short enough to stay clear of the neighbouring figure)',
              'thin scar across one cheek', 'fitted dark-navy tunic', 'dark-crimson half cape / hip wrap hanging on one side',
              'leather belt and a cross strap', 'dark trousers, brown boots', 'calm, focused expression'],
        colours=[('skin', '#e0ac7e'), ('hair', '#2b1d14'), ('tunic (main garment)', 'dark navy #2a3150'),
                 ('half cape / hip wrap', 'dark crimson #3a1018'), ('headband', 'off-white #e8e4d8')],
        fix=['concept.png is the LOOK reference; concept_pixel.png shows how SIMPLE the shapes must stay: '
             'big clear shapes, few folds, few small details, so it survives downscaling to 64 px',
             'the TUNIC is dark navy; dark crimson is ONLY the half cape / hip wrap (the portrait\'s wine-red coat is not the battle outfit)',
             'portrait.png is for the face and hair only (light stubble as in the portrait is fine); ignore its coat and the sword over its shoulder',
             'exactly one katana: no scabbard, no second sword, no arm wraps or bracers (the drafts add them; leave them out)',
             'this image becomes the STYLE ANCHOR for the eight other captains: keep it clean and exemplary'],
        pose=dict(idle='katana held diagonally up in front, both hands on the hilt',
                  windup='weight on the back leg, more upright; both hands raised above the head, the blade pointing UP and BACK over the head',
                  strike='step-in lunge; both arms extended forward, the blade cutting down and forward',
                  hit='torso thrown back, weight on the rear leg, head snapped back wincing; the katana drops down-back in the near hand, the free hand flies up'),
        ko=dict(keep='헝클어진 짙은 갈색 머리, 꼬리가 긴 흰 머리띠, 뺨의 흉터, 짙은 남색 상의(#2a3150), 한쪽에 늘어진 짙은 진홍 반망토(#3a1018), 가죽 띠, 갈색 장화, 카타나(두 손).',
                fix='concept = 생김새 기준, concept_pixel = 도트로 줄여도 살아남을 만큼 단순한 형태의 기준. 상의는 남색, 진홍은 반망토만. 칼집·두 번째 칼·팔 붕대 없음. 이 그림이 나머지 8명의 화풍 기준(앵커).'),
    ),
    'captain_ironwall': dict(
        en='Briginda', order=2, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_ironwall/concept_08.png'},
        weapon_desc=('a spiked mace (morning star) in the near hand and a tall rectangular tower shield with a gold rim on the far arm; '
                     'the shield is about 2 heads tall (~220 px) and 1 head wide (~110 px), top edge at shoulder height'),
        keep=['open steel helmet', 'long auburn hair in a thick braid', 'scar across the nose',
              'slate-grey plate armour with gold trim', 'grey tabard', 'leather belt', 'dark trousers, brown boots',
              'broad shoulders, sturdy build'],
        colours=[('skin', '#f2c9a0'), ('hair / braid', 'auburn #a8642a'), ('armour and tabard', 'slate grey #4a5a6a'),
                 ('trim and shield rim', 'gold #d9a441 (muted)')],
        fix=['the BRAID hangs down her BACK on the screen-left side (away from the shield) so it shows in the silhouette in every pose',
             'the guide shows a small round shield: draw the tower shield (size above) on the same arm, centred where the round shield is; '
             'it may cover part of the body but never the face, and it must keep the 32 px distance to the neighbouring figures',
             'the guide shows a sword: draw the spiked mace in that hand, same grip and angle'],
        pose=dict(idle='shield raised forward, mace held ready across the body as in the guide',
                  windup='weight on the back leg; mace raised up and back behind the head, shield kept forward',
                  strike='step-in lunge; mace smashing forward and down at full extension, shield pulled in',
                  hit='torso thrown back, weight on the rear leg, wincing; shield up in front of the chest, mace arm dropped down-back'),
        ko=dict(keep='강철 투구, 땋은 적갈색 긴 머리, 콧등 흉터, 금테 두른 회청색 판금갑옷, 회색 겉옷, 금테 탑실드(머리 2개 높이·1개 폭), 철퇴(모닝스타).',
                fix='땋은 머리는 방패 반대쪽 등 뒤로 늘어져 실루엣에서 보이게. 가이드의 작은 원형 방패 → 같은 자리에 탑실드, 칼 → 철퇴.'),
    ),
    'captain_tactician': dict(
        en='Isabel', order=3, weapon='staff',
        frames=dict(idle='cast_0', windup='cast_1', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_tactician/concept_07.png'},
        weapon_desc=("a slim black officer's cane / baton with a gold knob (no orb, no crystal), in the near hand where the guide holds "
                     'the staff, at the same angle, but only about HALF the guide staff\'s length (~1.2 heads, ~130 px)'),
        keep=['black tricorne hat with gold trim', 'long straight dark-indigo hair', 'charcoal long military coat',
              'gold epaulettes and gold buttons', 'leather belt', 'dark trousers, black boots', 'calm, sharp expression'],
        colours=[('skin', '#f5d6b8'), ('hair', 'dark indigo #3a3f6b'), ('coat', 'charcoal #3a3a4a'),
                 ('trim, epaulettes, buttons', 'gold #f2c94c (muted)')],
        fix=['the draft is about 6 heads tall: draw her 4 HEADS tall like everyone else (bigger head, shorter legs and coat, as the guide)',
             'the guide staff is a placeholder for the cane: idle = hand on the gold knob, cane tip on the ground along the LOWER part '
             'of the guide staff; wind-up and strike = cane held by its lower end, pointing along the UPPER part of the guide staff',
             'the coat must not be longer than the knees, so the legs still read in the wide stance'],
        pose=dict(idle='upright commander stance, cane planted at her side',
                  windup='cane raised, free hand lifted (about to give an order)',
                  strike='lunge; free arm extended straight forward, pointing with the index finger at the enemy; cane held up behind',
                  hit='torso thrown back, weight on the rear leg, wincing, hat still on'),
        ko=dict(keep='금테 검은 삼각모, 곧은 짙은 남보라 긴 머리, 숯색 긴 군복 코트, 금 견장·금단추, 검은 장화, 침착한 표정.',
                fix='초안은 약 6등신 → 4등신. 지팡이 → 가이드 지팡이 절반 길이의 장교 지휘봉(금 손잡이), 같은 손·같은 각도. 타격 = 앞으로 뻗은 팔로 손가락 지휘.'),
    ),
    'captain_lancer': dict(
        en='Roderick', order=4, weapon='spear',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_lancer/concept_b_12.png'},
        weapon_desc=('a spear-length infantry lance: straight shaft, slim leaf-shaped steel tip, small blue pennant just below the tip, '
                     'exactly as long as the guide spear; NO cone-shaped jousting lance and no vamplate (hand guard)'),
        keep=['ornate steel helmet with a blue plume, visor raised so the face shows', 'short brown hair, stubble, determined eyes',
              'polished blue plate armour with gold trim', 'worn white surcoat with a simple blue lion emblem',
              'tattered red cape', 'steel greaves'],
        colours=[('skin', '#f2c9a0'), ('hair', 'brown #5a3720'), ('plate armour', 'blue #3d5a9c'),
                 ('surcoat', 'worn off-white #e8e4d8 (shaded, never pure white)'), ('cape', 'dark red')],
        fix=['ON FOOT: he is "the knight who lost his horse" - no horse in this sheet',
             'the plume and the cape stay compact (no huge flowing cape), so nothing reaches the neighbouring figure',
             'simplify the lion emblem to one readable blue shape'],
        pose=dict(idle='lance held diagonally forward with both hands',
                  windup='weight on the back leg; lance pulled back level at hip height, rear hand behind the hip, ready to thrust',
                  strike='step-in lunge; both arms extended, lance thrust straight forward at full extension',
                  hit='torso thrown back, weight on the rear leg, wincing; the lance knocked upward (tip up) in both hands'),
        ko=dict(keep='파란 깃털 장식 투구(얼굴 보이게), 갈색 짧은 머리·수염, 금테 파란 판금, 파란 사자 문장의 낡은 흰 겉옷, 해진 붉은 망토.',
                fix='말 없이 걷는 기사(본 시트). 무기는 창 길이의 보병용 랜스(가는 잎 모양 날, 파란 작은 깃발, 원뿔 마상창·손 보호대 없음). 문장은 단순하게, 망토·깃털은 작게.'),
        mounted=dict(
            file='sheet_captain_lancer_mounted.png', concept='captain_lancer/concept_a_05.png',
            id='sheet/captain/lancer_mounted'),
    ),
    'captain_huntress': dict(
        en='Kiara', order=5, weapon='bow',
        frames=dict(idle='idle_0', windup='attack_2', strike='attack_3', hit='key_hit'),
        concepts={'concept.png': 'captain_huntress/concept_04.png'},
        weapon_desc='a short recurve bow the size of the guide bow, quiver of arrows on the back',
        keep=['long auburn hair in a high ponytail', 'ochre headband', 'freckles', 'olive-green hooded tunic',
              'brown leather vest', 'rope coil on the belt', 'dark trousers, brown boots'],
        colours=[('skin', '#e0ac7e'), ('hair', 'auburn #a8642a'), ('tunic', 'olive green #4a5a2a'),
                 ('headband and accents', 'ochre #c58f1e')],
        fix=['the draft bow is very large: draw a short bow the size of the guide bow',
             'an arrow appears ONLY on the drawn bow in the wind-up; after the release (strike) there is NO flying arrow (the engine draws projectiles)'],
        pose=dict(idle='bow held low in front, ready',
                  windup='full draw: arrow nocked, string pulled back to the cheek',
                  strike='release: bow arm extended, string straight, drawing hand flung back, no arrow',
                  hit='torso thrown back, weight on the rear leg, wincing; bow dropped low-forward, drawing hand flung back'),
        ko=dict(keep='높게 묶은 적갈색 포니테일, 황토색 머리띠, 주근깨, 올리브색 후드 상의, 가죽 조끼, 허리의 밧줄 뭉치, 등의 화살통, 짧은 활.',
                fix='초안의 큰 활 → 가이드 크기의 짧은 활. 화살은 당길 때(준비)만, 쏜 뒤(타격)에는 날아가는 화살 없음(엔진이 그린다).'),
    ),
    'captain_hedgemage': dict(
        en='Felix', order=6, weapon='staff',
        frames=dict(idle='idle_0', windup='cast_1', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_hedgemage/concept_08.png'},
        weapon_desc='a long, slightly crooked wooden staff (plain wooden top instead of the guide\'s blue orb)',
        keep=['short messy blond hair', 'worn, patched pointed wizard hat', 'purple robe', 'rope belt', 'satchel on the hip',
              'dark trousers, brown boots', 'cheerful, young face'],
        colours=[('skin', '#f5d6b8'), ('hair', 'blond #e3c565'), ('robe and hat', 'purple #5a4a7a'),
                 ('trim', 'dull ochre gold (#e8c86a desaturated)')],
        fix=['the draft\'s bright yellow trim must be muted to a dull ochre gold',
             'NO fire, glow or magic effect anywhere: the engine draws the spell VFX; the casting hand is open and empty',
             'the hat must stay inside the figure\'s space (no huge brim that reaches the neighbouring figure)'],
        pose=dict(idle='staff held diagonally in front with both hands',
                  windup='staff raised high in the near hand, free hand lifted, gathering power',
                  strike='lunge; free arm extended straight forward, palm OPEN toward the enemy (casting); staff held upright behind in the near hand',
                  hit='torso thrown back, weight on the rear leg, wincing, hat still on'),
        ko=dict(keep='헝클어진 금발, 기운 자국 있는 낡은 고깔모자, 보라색 로브, 밧줄 허리띠, 허리 가방, 갈색 장화, 나무 지팡이.',
                fix='밝은 노란 테두리 → 탁한 황토 금색. 불꽃·빛 등 효과 금지(엔진이 그린다), 시전하는 손은 앞으로 뻗은 빈 손바닥. 시전 자세(cast).'),
    ),
    'captain_fieldmedic': dict(
        en='Magda', order=7, weapon='staff',
        frames=dict(idle='idle_0', windup='cast_1', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_fieldmedic/concept_03.png'},
        weapon_desc='a long-handled spiked mace (the guide staff is the handle; the spiked iron head goes where the guide staff has its orb)',
        keep=['long black hair tied in a high ponytail', 'tan skin', 'bandage around the forehead', 'long field coat',
              'dark-red scarf', 'dark-red apron / under-dress', 'plain dark-red armband on the upper arm (no symbol)',
              'pouches on the belt', 'dark trousers, brown boots', 'stern, determined expression'],
        colours=[('skin', '#c68a5c'), ('hair', 'black #2b1d14'), ('coat', 'mid warm beige around #c8bca4 (darker than the game\'s #e8e4d8)'),
                 ('scarf, apron, armband', 'dark red #9c3b2e')],
        fix=['REMOVE the white cross on the red apron bib / chest: no cross or symbol anywhere; the armband stays a plain dark-red band',
             'the draft coat is near-white: paint it mid warm beige around #c8bca4 with hue-shifted shading, never white',
             'NO healing glow or orb: the engine draws the heal VFX; the forward hand is open and empty',
             'slots 2-3 are her action / cast poses: the same sheet is used for attacks AND heals'],
        pose=dict(idle='long mace held diagonally in front with both hands',
                  windup='mace raised high in the near hand, free hand lifted',
                  strike='lunge; free arm extended straight forward, palm open; mace held upright behind in the near hand',
                  hit='torso thrown back, weight on the rear leg, wincing'),
        ko=dict(keep='높게 묶은 검은 긴 머리, 갈색 피부, 이마 붕대, 긴 야전 코트, 짙은 빨강 스카프·앞치마, 무늬 없는 짙은 빨강 완장, 허리 주머니, 긴 자루 철퇴.',
                fix='가슴(앞치마 턱받이)의 흰 십자 제거 — 어디에도 십자·무늬 없음, 완장은 무늬 없는 짙은 빨강. 코트는 흰색이 아니라 중간 밝기의 따뜻한 베이지(#c8bca4 쯤). 치유 빛 금지(엔진). 2·3번은 공격·치유 겸용 시전 자세.'),
    ),
    'captain_fixer': dict(
        en='Jin', order=8, weapon='none',
        frames=dict(idle='key_idle', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_fixer/concept_05.png'},
        weapon_desc=('ONE short dagger in the near hand (screen-left arm = the character\'s right), REVERSE grip '
                     '(blade leaving the little-finger side, running back along the forearm), exactly as the guide draws it'),
        keep=['black hood', 'grey scarf over the mouth', 'narrow eyes', 'short black hair', 'black leather jacket with grey trim',
              'leather belt and a cross strap', 'dark trousers, black boots', 'lean, agile build'],
        colours=[('skin', '#e0ac7e'), ('hair', 'black #2b1d14'), ('jacket, hood, trousers', 'charcoal / blue-grey, NOT black (game #2a2a2a lifted)'),
                 ('scarf and trim', 'light grey #c9c2b8')],
        fix=['exactly ONE dagger, reverse grip, in the near hand; the other hand is always empty',
             'the all-black outfit vanishes on the dark battlefield: paint large areas in dark charcoal / blue-grey (not black), '
             'add a clear cool rim light on the upper-left edges and use a slightly LIGHTER outline (dark grey-violet) around the silhouette'],
        pose=dict(idle='low ready stance, dagger hand low in front, free hand up as a guard',
                  windup='weight on the back leg; dagger hand raised high above the head (about to stab down), free hand forward',
                  strike='lunge; dagger arm fully extended forward, free hand pulled back',
                  hit='torso thrown back, weight on the rear leg, wincing; dagger arm flung back, free hand up'),
        ko=dict(keep='검은 후드, 입을 가린 회색 스카프, 가는 눈, 검은 짧은 머리, 회색 테두리 검은 가죽 재킷, 교차 띠, 검은 장화.',
                fix='단검은 하나, 역수로, 가까운 쪽(화면 왼쪽) 손 — 가이드에 그려 두었다. 검정 옷은 짙은 숯색·청회색 + 왼쪽 위 림 라이트 + 조금 밝은 외곽선.'),
    ),
    'captain_veteran': dict(
        en='Harald', order=9, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'captain_veteran/concept_03.png'},
        weapon_desc='an arming sword in the near hand and a round wooden shield with an iron boss on the far arm (the guide shield\'s size)',
        keep=['dented steel helmet', 'short white hair and a full white beard', 'old scars on the face',
              'olive-grey quilted gambeson over chainmail', 'leather belt', 'dark trousers, worn boots', 'kind but tough old face'],
        colours=[('skin', '#f2c9a0'), ('hair and beard', 'white-grey #c9c2b8'), ('gambeson', 'olive grey #5a5a4a'),
                 ('helmet, mail, sword', 'dull steel'), ('shield', 'brown wood, iron boss')],
        fix=['the draft is about 5 heads tall: draw him 4 HEADS tall like everyone else',
             'old but sturdy: slightly stooped shoulders are fine, the stance stays as wide as the guide'],
        pose=dict(idle='shield up, sword ready',
                  windup='weight on the back leg; sword raised up and back behind the head, shield kept forward',
                  strike='step-in lunge; sword cutting forward and down at full extension, shield pulled in',
                  hit='torso thrown back, weight on the rear leg, wincing; shield up in front of the chest, sword arm dropped down-back'),
        ko=dict(keep='찌그러진 강철 투구, 흰 짧은 머리·흰 수염, 얼굴 흉터, 쇠사슬 위 올리브회색 누비 갑옷, 둥근 나무 방패, 한손검.',
                fix='초안은 약 5등신 → 4등신으로. 늙었지만 단단하게, 자세 폭은 가이드 그대로.'),
    ),
}

HEIGHT_EN = (f'head = {HEAD_PX} px for every character. Standing height would be {int(HEADS) * HEAD_PX} px ({int(HEADS)} heads), but the guide '
             'idle pose is crouched, so the measured idle top-of-head to sole is about {idle_px} px. Headgear (hats, helmets, plumes) '
             'and weapons are extra and not counted')
STYLE_EN = [
    'high-quality HD pixel art for a modern 2D fantasy tactics game (crisp pixel clusters, no blur, no painterly rendering)',
    f'{int(HEADS)} heads tall (top of the hair to the chin = 1 head), exactly the proportions and limb lengths of the guide; NOT chibi, NOT realistic',
    'front three-quarter view, facing RIGHT; light from the upper left',
    'muted, desaturated, hue-shifted palette (shadows toward purple/blue, highlights toward warm yellow), flat cel shading with 2-3 tones',
    'dark, desaturated, NON-black outline used selectively (no thick uniform black lineart), soft rim light on one side',
    'readable at 1x game size (the idle figure becomes ~64 px tall on a dark battlefield): big clear shapes, strong silhouette, few tiny details',
]
SPEC_EN = [
    'ONE PNG, 1536x1024 (landscape), the SAME character drawn 4 times in ONE row (1x4, never a 2x2 grid or a single pose), left to right: idle, wind-up, strike, hit',
    'each figure exactly where guide_strip.png has it: same size, same scale, same position, same limb lengths',
    f'the lowest pixel of every figure (its soles) on the line y = {BASELINE} (85% of the height); ' + HEIGHT_EN,
    f'at least {GAP} px of empty magenta between any two figures and between a figure and the image border (a weapon may reach over a '
    'neighbour\'s column as in the guide, but never closer than that)',
    'background: perfectly flat solid magenta #FF00FF everywhere (preferred; a transparent PNG is also accepted) - no gradient, floor, cast shadow or scenery',
    'NO text, labels, numbers, frames, grid lines, watermark; NO effects outside the body (no slash trails, sparks, dust, glow, motion lines, projectiles)',
]
DONT_COPY_EN = ('from the concept draft take ONLY the design (costume pieces, colours, hair, face marks, headgear, weapon/shield type, '
                'silhouette idea). Do NOT copy its proportions, rendering/shading technique, outline weight, saturation, lighting or level of detail '
                '- the NovelAI drafts are not consistent with each other')
CHECK_EN = [
    f'1536x1024, background flat #FF00FF (or transparent), 4 figures in ONE row: idle / wind-up / strike / hit as in the guide',
    f'soles of all four on y = {BASELINE}; same size in all four; head ~{HEAD_PX} px; idle ~{{idle_px}} px without headgear',
    '4 heads tall; front three-quarter view facing right; light from the upper left',
    'same face, hair, outfit, colours and weapon in all four poses; exactly the weapons in CHARACTER (nothing extra)',
    'every FIX applied',
    f'no text, floor, shadow, effects or projectiles; >= {GAP} px of magenta between figures and from the border',
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
    """→ (Body, poses, builds) for every posekit frame plus the KEY_POSES variants of this weapon."""
    B = pk.Body(HEADS)
    F = pk.frames(weapon, B)
    F.update(key_frames(weapon, B, F))
    builds = {n: pk.build(F[n], B, weapon) for n in F}
    if weapon == 'none':
        builds = {n: (J, add_dagger(J, parts)) for n, (J, parts) in builds.items()}
    return B, F, builds


def guide_frame(builds, frame):
    """the 832x1216 guide in the layout of `posekit.py --weapon W` (guide_<frame>.png); one scale for every frame."""
    gs, gox, goy = pk.fit(builds, pk.GW, pk.GH, pk.GH * pk.GUIDE_FEET, pk.GH * pk.GUIDE_BODY, 'idle_0', 0.025 * pk.GW)
    return pk.render_guide(builds[frame][1], pk.Raster(pk.GW, pk.GH, gs, gox[frame], goy, 2), 5.0)


def render_tight(parts, s, outline_px, pad=8):
    """one pose at s px/head on its own canvas, cropped to its pixels. → (rgb array, mask, sole row).
    The sole row is the bottom pixel row (outline included): it goes exactly on BASELINE."""
    x0, y0, x1, y1 = pk.bbox(parts)
    w = int(np.ceil((x1 - x0) * s)) + 2 * pad
    h = int(np.ceil((y1 - y0) * s)) + 2 * pad
    ox, oy = pad - x0 * s, pad - y0 * s
    rgb = np.asarray(pk.render_guide(parts, pk.Raster(w, h, s, ox, oy, 2), outline_px)).copy()
    mask = np.any(rgb != np.array(MAGENTA, np.uint8), axis=-1)
    ys, xs = np.nonzero(mask)
    t, b, l, r = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return rgb[t:b, l:r], mask[t:b, l:r], b - 1 - t


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
    canvas[:, qw - 1:qw + 1] = (40, 36, 48)          # quadrant lines: guide only, never drawn in the deliverable
    canvas[qh - 1:qh + 1, :] = (40, 36, 48)
    img = Image.fromarray(canvas, 'RGB')
    from PIL import ImageDraw
    dr = ImageDraw.Draw(img)
    for i, lab in enumerate(('1 idle', '2 wind-up', '3 strike (silhouette = size)', '4 hit')):
        dr.text(((i % 2) * qw + 12, (i // 2) * qh + 10), lab, fill=(40, 36, 48))
    return img, dict(w=nw, h=nh, box=(x0, y0, x0 + nw, y0 + nh))


# ───────── README ─────────

def colours_line(C, it):
    if C.get('colours'):
        return '; '.join(f'{k} {v}' for k, v in C['colours'])
    c = it.get('colors') or {}
    return ', '.join(f'{k} {v}' for k, v in c.items())


def package_files(cid, C, has_portrait, mounted=False):
    """files of the package in the order an agent should look at them."""
    fs = ['guide_strip.png', 'guide_1_idle.png', 'guide_2_windup.png', 'guide_3_strike.png', 'guide_4_hit.png', 'concept.png']
    if 'concept_pixel.png' in C['concepts']:
        fs.append('concept_pixel.png')
    if has_portrait:
        fs.append('portrait.png')
    if mounted:
        fs += ['concept_mounted.png', 'guide_mounted_layout.png']
    return fs


def readme(cid, C, it, info, has_portrait, mounted_item=None, minfo=None):
    key = cid.split('_', 1)[1]
    name = it['name']
    fr = C['frames']
    pkg = f'art/requests/phase3/{cid}'
    L = [f'# {name} — GPT handoff (`{cid}`)', '',
         '> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.',
         '> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.',
         f'> 모든 자료는 브랜치 `{BRANCH}`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.', '',
         '## Prompt for GPT (English)', '', '```']
    P = []
    P.append(f'TASK: draw the battle-sprite strip of {C["en"]} ({name.split(" — ")[0]}, {key}), a mercenary captain. '
             f'Save it as art/inbox/{it["file"]} on the art-inbox branch (a new file there; do not rename). '
             'In a chat without repository access, return the PNG in the chat instead.')
    P.append(f'CHARACTER: {C["weapon_desc"]}; ' + '; '.join(C['keep']) + '.')
    P.append(f'COLOURS (keep close, muted): {colours_line(C, it)}.')
    P.append('FIX (do not reproduce the draft here):\n' + '\n'.join(f'  - {f}' for f in C['fix']))
    P.append('POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and '
             'fist-shaped hands are placeholders - follow the text for hands and weapon details):\n'
             + '\n'.join(f'  {i + 1}. {en}: {C["pose"][p]}' for i, (p, _, _, en) in enumerate(POSES)))
    refs = [f'{f}' + {'guide_strip.png': ' (layout + poses + size: the most important reference)',
                      'guide_1_idle.png': ' .. guide_4_hit.png (the same four poses, larger)',
                      'concept.png': ' (DESIGN ONLY)',
                      'concept_pixel.png': ' (how simple the shapes must stay)',
                      'portrait.png': ' (face and hair only)'}[f]
            for f in package_files(cid, C, has_portrait) if f not in ('guide_2_windup.png', 'guide_3_strike.png', 'guide_4_hit.png')]
    if not C.get('anchor'):
        refs.insert(0, f'{ANCHOR_FILE} on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE '
                       'ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly')
    P.append(f'REFERENCES (folder {pkg}/ on branch {BRANCH}: {REPO}/tree/{BRANCH}/{pkg} ; in a chat they are the attached images):\n'
             + '\n'.join(f'  - {r}' for r in refs))
    P.append('DO NOT COPY: ' + DONT_COPY_EN + '.')
    P.append('STYLE (same for every character):\n' + '\n'.join(f'  - {s}' for s in STYLE_EN))
    P.append('DELIVERABLE:\n' + '\n'.join(f'  - {s.format(**info)}' for s in SPEC_EN))
    P.append('SELF-CHECK before saving (redraw if any fails):\n' + '\n'.join(f'  [ ] {c.format(**info)}' for c in CHECK_EN))
    L += ['\n\n'.join(P), '```', '']
    L += ['## 주인용 요약 (한국어)', '',
          f'- 순서: **{C["order"]}번째**' + (' — **화풍 기준(앵커)**: 이 그림을 먼저 받아 승인한 뒤 나머지 8명을 맞춘다.' if C.get('anchor') else
                                          f' — 승인된 바렌 그림(`art-inbox` 브랜치의 `{ANCHOR_FILE}`)의 화풍에 맞춘다.'),
          f'- 결과 파일: `art/inbox/{it["file"]}` (id `{it["id"]}`)' + (f', 추가 선택: `art/inbox/{mounted_item["file"]}`' if mounted_item else ''),
          f'- 무기: posekit `{C["weapon"]}` 마네킹 → {C["weapon_desc"]}',
          f'- 자세(가이드 프레임): ① 대기 `{fr["idle"]}` ② 공격 준비 `{fr["windup"]}` ③ 공격 타격 `{fr["strike"]}` ④ 피격 `{fr["hit"]}`'
          + ' (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)',
          f'- 초안에서 가져올 것: {C["ko"]["keep"]}',
          f'- 고칠 것: {C["ko"]["fix"]}',
          '- 초안에서 가져오지 말 것: 비율(등신), 칠하는 방식, 외곽선 굵기, 채도, 조명, 디테일 양 — 모두 4등신·앵커 화풍으로 통일.',
          f'- 가이드 띠: 머리 하나 = {info["px_per_head"]:g} px (모든 캐릭터 같음). 선 키라면 {int(HEADS) * HEAD_PX} px 이지만 대기 자세가 웅크려서 '
          f'정수리~발바닥 약 {info["idle_px"]} px(높이의 {info["idle_pct"]}%). 모자·투구·깃털·무기는 따로. 발바닥(맨 아래 픽셀) y={BASELINE}.',
          '', '### 파일 (ChatGPT 웹이면 이 순서로 첨부)', '',
          '| 파일 | 내용 |', '|---|---|']
    if not C.get('anchor'):
        L.append(f'| (`art-inbox`의 `{ANCHOR_FILE}`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |')
    L.append('| `guide_strip.png` | 4개 가이드를 결과물과 똑같은 배치로 (1536x1024, #FF00FF) |')
    for _, fn, ko, _ in POSES:
        L.append(f'| `{fn}` | 자세 가이드 832x1216 — {ko} |')
    L.append('| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |')
    if 'concept_pixel.png' in C['concepts']:
        L.append('| `concept_pixel.png` | 도트로 줄여도 살아남는 단순한 형태의 기준 |')
    if has_portrait:
        L.append('| `portrait.png` | 승인된 초상화 (얼굴·머리만 참고) |')
    if mounted_item:
        L.append('| `concept_mounted.png` | 기마 초안 (추가 선택 시트용, 디자인만) |')
        L.append('| `guide_mounted_layout.png` | 기마 시트 2x2 칸 나눔·크기 참고 (선·글씨는 가이드에만, 실루엣은 왼쪽 아래 칸) |')
    L += ['', '### 받은 뒤 (Claude Code)', '', '```',
          f'python3 tools/art/sheets.py art/inbox/{it["file"]} --dry-run --work /tmp/sheets   # 미리보기',
          f'python3 tools/art/sheets.py art/inbox/{it["file"]}                                 # 등록']
    if mounted_item:
        L.append(f'python3 tools/art/sheets.py art/inbox/{mounted_item["file"]} --grid 2x2 --dry-run --work /tmp/sheets  # 기마: 미리보기만 (게임 미사용, 등록하지 않는다)')
    L += ['```', '']
    if mounted_item:
        head = max(8, int(round(minfo['h'] / 7)))
        L += ['## 추가 선택: 기마 시트 (게임은 아직 쓰지 않는다)', '',
              '- 이야기는 "말을 잃은 기사"라 본 시트는 걷는 기사다. 기마 그림은 나중에 "군마를 되찾는" 형태가 생길 때를 위한 **추가 시트**다.',
              f'- 파일 `art/inbox/{mounted_item["file"]}` (본 시트와 다른 이름), id `{mounted_item["id"]}`, 1536x1024 **2x2 격자**. 9명이 끝난 **맨 마지막**에 그린다.',
              '- 갑옷은 걷는 시트와 같은 **파란 판금**(초안의 은색 아님). 무기도 걷는 시트와 같은 깃발 달린 랜스(원뿔 마상창 아님).',
              '- 고른 초안의 말 머리 부분은 투구 낀 머리 둘이 나란히 붙은 것처럼 보인다(주인 확인 필요). 그림에서는 **말 머리 정확히 하나**.', '',
              '```',
              f'TASK (OPTIONAL, LAST): a mounted variant of the same knight (Roderick). Save as art/inbox/{mounted_item["file"]} on the art-inbox branch '
              f'(NOT {it["file"]}; in a chat, return the PNG). The game does not use it yet; it is for a possible later "regains a warhorse" form.',
              f'REFERENCES: the style anchor {ANCHOR_FILE} and your art/inbox/{it["file"]} (same knight: same face, BLUE plate armour, '
              f'white surcoat, red cape, plume, colours and style); {pkg}/concept_mounted.png (design only: armoured dark-brown warhorse with '
              f'a blue caparison, couched lance, red cape; its armour is silver - paint it blue as on foot); {pkg}/guide_mounted_layout.png '
              '(quadrants and size only).',
              'WEAPON: the same infantry lance as on foot (slim leaf tip, small blue pennant), couched under the arm; no cone-shaped jousting lance.',
              'LAYOUT: one PNG 1536x1024 as a 2x2 grid of four equal quadrants (768x512), one pose per quadrant: top-left idle (horse standing, '
              'lance upright), top-right wind-up (horse rearing slightly, lance lowering), bottom-left strike (galloping charge, lance couched '
              'forward), bottom-right hit (horse recoiling, rider leaning back). The grey silhouette in the bottom-left quadrant of '
              'guide_mounted_layout.png shows the size of ONE pose; the other three quadrants are empty in the guide - draw each pose there at the '
              'same size. The dividing lines and labels exist only in the guide: do NOT draw lines or text. Hooves on a baseline at 90% of each '
              'quadrant\'s height, nothing crossing into another quadrant or touching the border; horse+rider+lance no wider than 1.6x its height.',
              f'SCALE: the rider is 4 heads tall in proportion to the horse, with a head of about {head} px (the whole group is smaller than the '
              'on-foot figures so it fits a quadrant). The horse has EXACTLY ONE head (the draft\'s horse head looks doubled - draw one), '
              'four legs, one tail.',
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
        B, F, builds = cache[C['weapon']]
        fr = [C['frames'][p] for p, _, _, _ in POSES]
        for f in fr:
            for m in pk.check(f, builds[f][0], B, F[f]):
                print(f'  WARNING {cid} {f}: {m}')
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
