#!/usr/bin/env python3
"""GPT handoff packages for battle sprites → art/requests/phase3/<id>/

Each package is everything the GPT image model needs for ONE character (see
art/requests/gpt_handoff_notes.md): the owner's chosen NovelAI design draft (design only), the
approved portrait (face only), four key-pose guides (the posekit 4-head mannequin; see KEY_POSES)
and guide_strip.png — the four guides laid out exactly as the deliverable must be (1536x1024, flat
#FF00FF, soles on y=870 = 85% of the height, 110 px per head for every character so the crouched
idle is ~400 px ≈ 39% of the height, >= 32 px of magenta between figures and from the border).
README.md = the English prompt block for GPT (per-character part first) + Korean notes for the owner.

  python3 tools/art/handoff.py                       # every package in CHARS and CREATURES
  python3 tools/art/handoff.py captain_fixer --check # one package; --check also prints the layout

Kinds: captains (CHARS, concept + portrait), generic class sheets (CHARS kind 'class': KEY COLOURS block from
phase3.json item.tint, the engine recolours the uniform per faction), humanoid monsters (CHARS kind 'monster', posekit
guides) and non-humanoid monsters (CREATURES: no mannequin; guide_layout.png = 2x2 / 1x4 layout with a size box per pose,
guide_scale.png = the idle box next to a 4-head human at the same scale). concepts={} = the owner has not picked a NovelAI
draft yet: the package has no concept.png and its README says so (add the pick and rerun). draft=dict(keep, fix) = notes on the
chosen draft itself (what to take from it, its defects; fix is appended to FIX), ko['draft_keep'/'draft_fix'] the Korean summary.

Needs art/requests/phase3.json (node tools/art/requests.js) for names and game colours.
Deterministic: the same inputs give byte-identical files. Concept and portrait files are copied
byte-for-byte (git stores identical blobs once). To add a character, add a CHARS entry
(weapon / frames from tools/pixelart/posekit.py or KEY_POSES, concept files, notes) and rerun.
"""
import argparse
import copy
import json
import os
import re
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
        colours=[('skin', '#f5d6b8'), ('hair', 'blond #e3c565'),
                 ('robe and hat', 'blue-purple #5a4a7a, shades #3a3052 / #4a3e66 / #5a4a7a / #74679a / #8f84b0 (never pink or magenta)'),
                 ('trim', 'dull ochre gold (#e8c86a desaturated)')],
        fix=['the robe and hat stay in the dark blue-purple #5a4a7a family, lit side included: the first delivery painted the lit robe and hat '
             'exactly #FF00FF, the background key, so the background removal punched holes in them (see the magenta rule)',
             'the draft\'s bright yellow trim must be muted to a dull ochre gold',
             'NO fire, glow or magic effect anywhere: the engine draws the spell VFX; the casting hand is open and empty',
             'the hat must stay inside the figure\'s space (no huge brim that reaches the neighbouring figure)'],
        pose=dict(idle='staff held diagonally in front with both hands',
                  windup='staff raised high in the near hand, free hand lifted, gathering power',
                  strike='lunge; free arm extended straight forward, palm OPEN toward the enemy (casting); staff held upright behind in the near hand',
                  hit='torso thrown back, weight on the rear leg, wincing, hat still on'),
        ko=dict(keep='헝클어진 금발, 기운 자국 있는 낡은 고깔모자, 보라색 로브, 밧줄 허리띠, 허리 가방, 갈색 장화, 나무 지팡이.',
                fix='로브·모자는 밝은 면까지 짙은 청보라 #5a4a7a 계열(첫 납품은 밝은 면이 배경 키 #FF00FF 와 같아 구멍이 뚫렸다). '
                    '밝은 노란 테두리 → 탁한 황토 금색. 불꽃·빛 등 효과 금지(엔진이 그린다), 시전하는 손은 앞으로 뻗은 빈 손바닥. 시전 자세(cast).'),
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

# ───────── generic class sheets (kind 'class') ─────────
# One sheet per base class, used by EVERY nameless mercenary and faction soldier of that class (promoted classes fall
# back to it, js/art.js sheetFor). The engine recolours the uniform per faction / company by replacing EXACT key colours
# (js/battle.js sheetRecolor: key -> target x key luminance / mean luminance of that role's keys). So the uniform is painted
# ONLY with the key ramps of phase3.json item.tint (= CLASS_KEYS in tools/art/requests.js), flat, and the keys are used
# nowhere else; sheets.py snaps colours within KEY_TOL back to the keys and registers them (--tint-outfit / --tint-accent).
# concepts = the owner's NovelAI pick (art/concepts/selections.json); {} would mean no pick yet (the package then has no concept.png).
# Face coverage (owner request): one sheet stands for many DIFFERENT people, so the base-class outfits hide or shade the face
# where it suits the class (warrior visor, archer hood + mask, mage hat brim + high collar, cleric cowl + veil, rogue hood).
# Later promoted / master classes only where natural - never forced.
CLASS_COMMON_KEEP = ['the FACE is covered or in shadow (see the headgear below), because this one sprite stands for hundreds of '
                     'different soldiers; whatever little of the face shows is generic, with no scars, marks or distinctive features']
CLASS_COMMON_FIX = ['the face stays covered / shadowed the SAME way in ALL FOUR poses: the visor, hood, mask, brim or veil never '
                    'slips, opens or falls back, not even in the hit pose; the shadowed face is a warm or neutral dark '
                    '(e.g. #3a2e2a), never blue and never a key colour']
# Owner review of the first class delivery: the archer's hood edge around the face and the rogue's scarf were ACCENT keys, so a
# bright faction accent (cities #f2c94c, elves lime, clans cream) painted the face as a solid yellow block. Cloth over or around
# the face is OUTFIT keys (the archer's mask already was); the accent keys stay on trim away from the face.
FACE_CLOTH_FIX = ('NO accent key on or around the face: {what} use the OUTFIT keys (never the accent keys), because a bright faction '
                  'accent such as yellow would turn the whole face into one solid block')
# draft notes (owner's NovelAI pick, concept.png): `draft` = what to take from the drawing (keep) and its defects (fix, appended
# to FIX). The class drafts were prompted "plain slate blue ... pale teal trim": that only marks the key-colour SLOT.
CLASS_DRAFT_FIX = ('the draft\'s slate-blue / teal / cyan cloth only marks WHERE the key colours go: repaint those areas with the exact '
                   'KEY COLOURS ramps above (flat), never with the draft\'s own blues, teals or cyans')
DRAFT_VOID_FIX = ('the draft\'s face opening is a flat pure-black void: paint it as the warm / neutral face shadow (#3a2e2a family), '
                  'not pure black')
ONE_HEAD_FIX = 'exactly ONE head (sibling drafts of this design came out with a duplicated head): one head, one neck'


def head_fix(cover, extra=''):
    """class FIX line: covered heads keep the 110 px scale (the headgear encloses the head, it does not enlarge the figure)."""
    return (f'HEAD SIZE: {cover} enclose the {HEAD_PX} px head (outer silhouette about 115-125 px from crown to chin{extra}); do not draw a '
            f'{HEAD_PX} px head and then a bigger helm / hood around it, and do not enlarge the figure (this overrides "headgear is extra" '
            'in DELIVERABLE for this sheet)')


FACE_KO = ('- **얼굴 가림** (주인 요청): 이 그림 한 장을 서로 다른 여러 사람이 같이 쓰므로 얼굴이 가려지는 복장 — {face}. '
           '네 자세 모두 같은 만큼 가린다(피격 때도 벗겨지지 않음). 가려진 얼굴 그늘은 따뜻하거나 중성인 어두운 색(파랑·열쇠 색 금지). '
           '상급·최상급 직업은 어울릴 때만, 억지로 하지 않는다.')
CHARS.update({
    'class_warrior': dict(
        kind='class', en='Warrior', order=11, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'class_warrior/concept_05.png'},
        draft=dict(keep=('the plain foot-soldier look: closed steel helm with the visor down and one dark eye slit (its small top spike may '
                         'stay, small), mail coif and mail sleeves under a sleeveless knee-length tabard split at the front, brown belt with a '
                         'square buckle, brown gloves, grey trousers, tall brown boots, a plain round shield on the far arm and a straight arming sword'),
                   fix=[CLASS_DRAFT_FIX,
                        'the draft shield is bare wood grain: its FACE uses the outfit keys (flat, no wood texture) with one accent-key band, '
                        'and a plain iron rim and boss (see CHARACTER)',
                        'the draft tabard has no trim: add the accent-key border trim',
                        'the draft\'s ochre-yellow boot cuffs become plain warm brown (nothing yellow on the figure)',
                        'the draft helm is bright polished silver with white glints: neutral mid steel grey, small highlights only',
                        'the draft\'s rear leg crosses awkwardly behind the front one: legs and stance come ONLY from the guide']),
        head=head_fix('the closed helm IS the head: its outline and the mail coif', ', the small top spike extra'),
        weapon_desc=('a plain one-handed arming sword in the near hand and a round wooden shield (the guide shield\'s size) on the far arm; '
                     'the shield FACE is painted with the outfit keys (it shows the faction colour), its rim and boss are plain iron'),
        keep=CLASS_COMMON_KEEP + ['closed steel great helm with the VISOR DOWN: no face shows, only a dark horizontal eye slit '
                                  '(hair fully hidden)', 'grey chainmail shirt', 'knee-length sleeveless TABARD over the mail', 'leather belt, brown gloves',
                                  'dark trousers, brown boots', 'sturdy, ordinary soldier build'],
        roles=dict(outfit='the tabard and the shield face', accent='the tabard\'s border trim and one plain band across the shield face'),
        colours=[('eye slit', 'warm near-black #2a2220'),
                 ('helmet, mail, sword, shield rim and boss', 'NEUTRAL steel grey (no blue tint), e.g. #c8c6c0 / #8a8a86 / #5a5652'),
                 ('leather and wood', 'warm browns')],
        fix=CLASS_COMMON_FIX + ['the helm stays readable as a helmet at 64 px: a clear visor line and eye slit, NEUTRAL grey (no blue sheen)',
                                'no emblem, crest or heraldry: the faction colour comes from the recoloured keys only'],
        pose=dict(idle='shield up, sword ready',
                  windup='weight on the back leg; sword raised up and back behind the head, shield kept forward',
                  strike='step-in lunge; sword cutting forward and down at full extension, shield pulled in',
                  hit='torso thrown back, weight on the rear leg, head jerked back; shield up in front of the chest, sword arm dropped down-back'),
        ko=dict(keep='면갑을 내린 강철 그레이트 헬름(눈 틈만 보임), 사슬 갑옷, 무릎 길이 민소매 겉옷(제복), 가죽 띠, 갈색 장갑·장화, 한손검 + 둥근 나무 방패.',
                fix='겉옷·방패 면 = 제복 열쇠 색, 겉옷 테두리·방패의 띠 하나 = 장식 열쇠 색. 금속은 푸른 기 없는 중성 회색. 문장·무늬 없음. 면갑은 네 자세 모두 내린 채.',
                face='전사는 면갑을 내린 투구(눈 틈만)',
                draft_keep='면갑 내린 투구(눈 틈 하나, 위의 작은 뿔은 작게 둬도 됨), 사슬 두건·사슬 소매, 앞이 갈라진 무릎 길이 민소매 겉옷, 네모 버클 갈색 띠, 갈색 장갑, 회색 바지, 갈색 긴 장화, 둥근 방패 + 곧은 한손검.',
                draft_fix='초안의 청회색·청록은 열쇠 색 자리 표시일 뿐 → 정확한 열쇠 색으로. 나무결 방패 → 방패 면은 제복 열쇠 색(평평하게) + 장식 띠 하나, 쇠 테·쇠 돌기. '
                          '겉옷에 장식 테두리 추가. 노란 장화 끝단 → 갈색. 번쩍이는 은색 투구 → 중성 회색. 꼬인 뒷다리 → 자세는 가이드대로.'),
    ),
    'class_archer': dict(
        kind='class', en='Archer', order=12, weapon='bow',
        frames=dict(idle='idle_0', windup='attack_2', strike='attack_3', hit='key_hit'),
        concepts={'concept.png': 'class_archer/concept_10.png'},
        draft=dict(keep=('the hood up with the face mask running down into a short cowl over the shoulders (hood, mask and cowl one cloth), '
                         'long-sleeved knee-length tunic with a flared skirt, small brown leather bodice-vest with one diagonal strap, brown belt '
                         'with pouches, long brown gloves / bracers, tall brown boots with turned-down cuffs, a quiver of arrows on the back'),
                   fix=[CLASS_DRAFT_FIX,
                        'the draft face opening is a pure-black void with no eyes: a narrow warm-dark shadow strip at eye level (#3a2e2a family, '
                        'at most two tiny eye glints); the mask still covers everything below the nose',
                        'the draft bow is a long bow whose string line breaks and crosses the body: a short recurve bow the size of the guide bow '
                        'with ONE clean string; an arrow only on the drawn bow in the wind-up',
                        'the draft has no trim: accent keys on the tunic hem (the hood\'s front edge around the face stays OUTFIT keys)',
                        'the draft trousers are blue-purple grey: warm dark grey-brown (nothing blue outside the keys)']),
        head=head_fix('the hood and the mask'),
        weapon_desc='a short recurve bow the size of the guide bow (brown wood), a brown leather quiver of arrows on the back',
        keep=CLASS_COMMON_KEEP + ['the HOOD of the tunic is UP, and a cloth MASK covers the lower face up to the nose, so only a '
                                  'narrow warm-dark shadow strip at eye level shows, no skin (hair hidden)',
                                  'knee-length HOODED TUNIC', 'brown leather vest over the tunic', 'leather bracers', 'dark trousers, brown boots', 'lean build'],
        roles=dict(outfit='the hooded tunic (hood with its front edge around the face, sleeves, skirt of the tunic) and the face mask',
                   accent='the tunic\'s hem trim only'),
        colours=[('eye strip', 'warm-dark shadow #3a2e2a with at most two tiny eye glints - no skin visible (gloved hands, no skin anywhere)'),
                 ('vest, bracers, quiver, bow', 'warm browns'),
                 ('arrowheads', 'NEUTRAL steel grey')],
        fix=CLASS_COMMON_FIX + [FACE_CLOTH_FIX.format(what='the mask, the hood and the hood\'s front edge around the face (a fold in the darkest outfit key #263459 may mark the edge)'),
             'an arrow appears ONLY on the drawn bow in the wind-up; after the release (strike) there is NO flying arrow (the engine draws projectiles)',
             'the leather vest stays brown and small, so the tunic underneath still shows clearly on the chest, sleeves and skirt'],
        pose=dict(idle='bow held low in front, ready',
                  windup='full draw: arrow nocked, string pulled back to the cheek',
                  strike='release: bow arm extended, string straight, drawing hand flung back, no arrow',
                  hit='torso thrown back, weight on the rear leg, head jerked back, hood and mask still in place; bow dropped low-forward, drawing hand flung back'),
        ko=dict(keep='후드를 쓰고 천 마스크로 코 아래를 가린 얼굴(눈 둘레만 그늘 속에), 무릎 길이 후드 상의(제복), 갈색 가죽 조끼·팔 보호대, 등의 화살통, 짧은 활.',
                fix='후드 상의·마스크·얼굴 둘레의 후드 앞 가장자리 = 제복 열쇠 색, 상의 밑단만 장식 열쇠 색 (얼굴 둘레에 장식 색 금지 — 밝은 진영 장식 색이 얼굴을 노란 덩어리로 만든다). 화살은 당길 때만, 쏜 뒤에는 없음.',
                face='궁수는 후드 + 코 아래를 가린 천 마스크',
                draft_keep='후드와 마스크가 어깨의 짧은 두건 망토로 이어지는 한 장의 천, 긴 소매 무릎 길이 상의(밑자락 퍼짐), 대각선 띠 하나 있는 작은 가죽 조끼, 주머니 달린 갈색 띠, 긴 갈색 장갑, 끝단 접힌 갈색 장화, 등의 화살통.',
                draft_fix='초안의 청회색은 열쇠 색 자리 표시 → 정확한 열쇠 색. 눈 없는 새까만 얼굴 구멍 → 눈높이의 좁은 따뜻한 어둠(눈빛 두 점까지), 코 아래는 마스크. '
                          '긴 활·끊긴 시위 → 가이드 크기 짧은 활, 시위 하나. 상의 밑단에 장식 열쇠 색 추가(후드 앞 가장자리는 제복 열쇠 색). 청보라 바지 → 따뜻한 짙은 회갈색.'),
    ),
    'class_cleric': dict(
        kind='class', en='Cleric', order=14, weapon='staff',
        frames=dict(idle='idle_0', windup='cast_1', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'class_cleric/concept_04.png'},
        draft=dict(keep=('the deep cowl falling to the shoulders with the veil across the lower face (one cloth), a mail shirt with brown '
                         'leather sleeves under it, a long tabard with a border trim and a chest disc, brown belt with a round buckle, a small '
                         'brown book at the hip, grey trousers, tall brown boots, the free hand raised open'),
                   fix=[CLASS_DRAFT_FIX + ' (the draft even uses two different blues: cowl, veil and tabard are all the same outfit keys)',
                        DRAFT_VOID_FIX,
                        'the draft chest mark is a glowing white starburst: the plain flat filled accent-key disc of CHARACTER - no rays, no glow, no white',
                        'the draft weapon is a long-handled spiked ball (morning star): the short flanged mace of CHARACTER (~1.3 heads)',
                        'the draft tabard reaches the ankles: knee length, so the legs read in the wide stance',
                        'the draft\'s book is a pouch with a gold stud: a small plain closed brown book, no symbol',
                        'the draft\'s raised hand has spread, claw-like fingers: a calm open palm']),
        head=head_fix('the cowl and the veil'),
        weapon_desc=('a one-handed flanged steel mace with a wooden handle about 1.3 heads long (~140 px), in the near hand where the guide holds '
                     'the staff and at the same angle; it is SHORTER than the guide staff (its head sits about halfway up the guide staff)'),
        keep=CLASS_COMMON_KEEP + ['a deep COWL (hood) pulled low over the brow and a short VEIL of the same cloth across the lower face, '
                                  'so the face is in shadow (hair hidden)', 'grey chainmail', 'knee-length TABARD over the mail',
                                  'one plain filled round disc in the accent keys on the chest (the ONLY allowed shape on this sheet and not an emblem: '
                                  'a simple filled circle, no cross, no rays, no symbol inside)',
                                  'a small brown leather book on the belt', 'dark trousers, brown boots'],
        roles=dict(outfit='the tabard, the cowl and the veil', accent='the tabard\'s border trim, the cowl\'s front edge and the plain chest disc'),
        colours=[('skin (hands, a sliver of the face in shadow)', '#c68a5c'), ('mail and mace head', 'NEUTRAL steel grey'), ('book, belt, boots', 'warm browns')],
        fix=CLASS_COMMON_FIX + ['NO cross anywhere and NO healing glow or light: the engine draws the heal VFX; the forward hand is open and empty',
             'slots 2-3 are the action / cast poses: the same sheet is used for attacks AND heals'],
        pose=dict(idle=('the near (screen-left, front) hand holds the mace at the guide\'s LOWER grip, by the belt, the mace pointing up '
                        'along the guide staff\'s line (its head about halfway up the staff); the far hand leaves the staff and rests open on '
                        'the belt'),
                  windup='mace raised high in the near hand, free hand lifted (praying / gathering)',
                  strike='lunge; free arm extended straight forward, palm OPEN (blessing or striking); mace held up behind in the near hand',
                  hit='torso thrown back, weight on the rear leg, head jerked back, cowl and veil still in place'),
        ko=dict(keep='이마까지 깊게 내린 두건(카울)과 아래 얼굴을 가린 베일(얼굴은 그늘), 사슬 갑옷 위 무릎 길이 겉옷(제복), 가슴의 무늬 없는 둥근 원판(장식 열쇠 색, 이 시트에서 유일하게 허용된 모양 — 문장이 아님), 허리의 작은 책, 한손 철퇴.',
                fix='겉옷·두건·베일 = 제복 열쇠 색, 테두리·두건 앞 가장자리·가슴 원판 = 장식 열쇠 색. 십자·치유 빛 없음. 2·3번은 공격·치유 겸용 자세(마그다와 같은 틀, 철퇴는 짧게).',
                face='성직자는 깊은 두건 + 베일, 얼굴은 그늘',
                draft_keep='어깨까지 내려오는 깊은 두건과 아래 얼굴의 베일(한 장의 천), 갈색 가죽 소매 위 사슬 갑옷, 테두리와 가슴 원판이 있는 겉옷, 둥근 버클 갈색 띠, 허리의 작은 갈색 책, 회색 바지, 갈색 긴 장화, 들어 올린 빈 손.',
                draft_fix='초안의 두 가지 파랑(두건 청록·겉옷 파랑)은 열쇠 색 자리 표시 → 두건·베일·겉옷 모두 같은 제복 열쇠 색. 새까만 얼굴 → 따뜻한 어둠. '
                          '빛나는 흰 별 문양 → 장식 열쇠 색의 무늬 없는 둥근 원판(빛·햇살 없음). 긴 자루 가시 철퇴 → 짧은 플랜지 철퇴. 발목까지 오는 겉옷 → 무릎 길이. '
                          '금 장식 주머니 → 무늬 없는 작은 책. 갈퀴 같은 손가락 → 차분하게 편 손바닥.'),
    ),
    'class_mage': dict(
        kind='class', en='Mage', order=13, weapon='staff',
        frames=dict(idle='idle_0', windup='cast_1', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'class_mage/concept_09.png'},
        draft=dict(keep=('the pointed hat with its brim pulled down over the eyes, the high stand-up collar hiding mouth and chin, a small '
                         'shoulder capelet, the long robe with wide bell sleeves and one trim line down the front, brown belt with pouches, '
                         'brown boots, the free hand raised open'),
                   fix=[CLASS_DRAFT_FIX + ' (the draft trim is bright cyan: the front line, cuffs, capelet edge and hem are accent keys)',
                        DRAFT_VOID_FIX,
                        'the draft has a second amber crystal FLOATING above the open hand: delete it - the raised hand is open and EMPTY; '
                        'the only crystal is the small one on top of the staff',
                        'the draft staff is a thin cane held low with its crystal at hand height: a straight staff the length of the guide staff, '
                        'crystal at its top',
                        'the draft has no hat band and no sash: add both, in the accent keys',
                        'the draft hat is very tall with a very wide brim: compact (cone about one head tall, brim no wider than the shoulders)']),
        head=head_fix('the hat brim and the high collar frame and', '; only the hat cone above the brim is extra'),
        weapon_desc=('a straight wooden staff the length of the guide staff with a small AMBER crystal at the top instead of the guide\'s blue orb '
                     '(warm orange-yellow, no glow; never a blue or teal crystal)'),
        keep=CLASS_COMMON_KEEP + ['wide-brimmed pointed HAT (compact brim) pulled LOW, its brim hiding the eyes, and a HIGH COLLAR '
                                  'covering the mouth and chin, so the face between them is in shadow (hair hidden)',
                                  'long ROBE to the shins with a sash', 'brown belt pouches', 'brown boots'],
        roles=dict(outfit='the hat, the robe with its shoulder capelet and its high collar',
                   accent='the hat band, the front trim line, the capelet edge, the robe\'s hem / cuff trim and the sash'),
        colours=[('skin (hands, a sliver of the face in shadow)', '#f2c9a0'), ('staff, pouches, boots', 'warm browns'), ('crystal', 'amber #d9a441 (muted)')],
        fix=CLASS_COMMON_FIX + ['NO fire, glow or magic effect anywhere: the engine draws the spell VFX; the casting hand is open and empty',
             'the hat stays inside the figure\'s space (no huge brim reaching the neighbouring figure)'],
        pose=dict(idle='staff held diagonally in front with both hands',
                  windup='staff raised high in the near hand, free hand lifted, gathering power',
                  strike='lunge; free arm extended straight forward, palm OPEN toward the enemy (casting); staff held upright behind in the near hand',
                  hit='torso thrown back, weight on the rear leg, head jerked back, hat still on and still low'),
        ko=dict(keep='깊게 눌러쓴 챙 넓은 고깔모자(챙이 눈을 가림) + 입·턱을 가린 높은 깃(얼굴은 그늘), 정강이까지 오는 로브와 허리띠 천, 갈색 주머니, 호박색 작은 수정이 달린 곧은 나무 지팡이.',
                fix='모자·로브(어깨 망토 포함)·높은 깃 = 제복 열쇠 색, 모자 띠·앞섶 테두리 선·어깨 망토 가장자리·로브 밑단·소맷부리·허리띠 천 = 장식 열쇠 색. 수정은 따뜻한 호박색(파랑·청록 금지), 효과 없음. 펠릭스와 같은 시전 틀.',
                face='마법사는 깊게 눌러쓴 모자 챙 + 높은 깃, 얼굴은 그늘',
                draft_keep='눈을 가리게 눌러쓴 고깔모자, 입·턱을 가린 높은 깃, 작은 어깨 망토, 넓은 종 모양 소매의 긴 로브와 앞섶의 테두리 선 하나, 주머니 달린 갈색 띠, 갈색 장화, 들어 올린 빈 손.',
                draft_fix='초안의 청회색·밝은 시안 테두리는 열쇠 색 자리 표시 → 정확한 열쇠 색(앞섶·소맷부리·어깨 망토 끝·밑단 = 장식). 새까만 얼굴 → 따뜻한 어둠. '
                          '손 위에 떠 있는 두 번째 수정 삭제 — 든 손은 빈 손, 수정은 지팡이 끝의 작은 것 하나뿐. 낮게 든 가는 지팡이 → 가이드 길이의 곧은 지팡이, 수정은 끝에. '
                          '모자 띠·허리 천 추가(장식). 너무 큰 모자 → 작게(뿔 높이 머리 하나, 챙은 어깨 너비 이하).'),
    ),
    'class_rogue': dict(
        kind='class', en='Rogue', order=15, weapon='none',
        frames=dict(idle='key_idle', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'class_rogue/concept_02.png'},
        draft=dict(keep=('the deep hood with its cloth wrapped over the mouth and nose (only a dark eye slit), the wary, ready attitude (attitude '
                         'only: legs, crouch depth and size exactly as guide_strip.png), dark-brown '
                         'leather chest armour, many brown leather straps around the thighs and shins, soft boots, ONE dagger'),
                   fix=[CLASS_DRAFT_FIX,
                        'the draft draws hood and scarf as ONE bright cyan piece: the hood, the short shoulder cape (which the draft lacks) '
                        'and the scarf over mouth and nose all use the OUTFIT keys, the scarf kept a clearly separate piece by a warm-dark '
                        'outline / the darkest outfit key #263459 along its edge',
                        'the draft sleeves, trousers and boots are navy blue: warm dark brown / warm dark grey (nothing blue outside the keys)',
                        'the draft\'s head is sunk into the chest and the arms are knotted across the belly with the blade poking out behind the hip: '
                        'normal 4-head anatomy with the head clearly above the shoulders, the dagger only in the near hand, reverse grip, as the guide draws it',
                        'the draft eye slit is pure black: warm-dark shadow, at most two small eye glints']),
        head=head_fix('the hood and the scarf'),
        weapon_desc=('ONE short dagger in the near hand (screen-left arm = the character\'s right), REVERSE grip '
                     '(blade leaving the little-finger side, running back along the forearm), exactly as the guide draws it'),
        keep=CLASS_COMMON_KEEP + ['deep HOOD pulled low so the face is in shadow (at most two small eye glints) and a short SHOULDER CAPE',
                                  'a SCARF over the mouth and nose',
                                  'dark-brown leather armour with straps', 'dark trousers, dark-brown boots', 'lean, agile build'],
        roles=dict(outfit='the hood, the shoulder cape and the scarf over the mouth and nose', accent='one thin belt sash only'),
        colours=[('skin (hands only; the face is in shadow)', '#e0ac7e'), ('leather armour, straps, boots', 'warm dark brown #4a3a2e (NOT black, NOT blue-grey)'),
                 ('dagger', 'NEUTRAL steel grey')],
        fix=CLASS_COMMON_FIX + [FACE_CLOTH_FIX.format(what='the scarf over the mouth and nose and the hood'),
             'exactly ONE dagger, reverse grip, in the near hand; the other hand is always empty',
             'the dark leather stays WARM brown (never blue-grey), so it never comes close to the uniform keys; add a warm rim light on the '
             'upper-left edges so it reads on the dark battlefield'],
        pose=dict(idle='low ready stance, dagger hand low in front, free hand up as a guard',
                  windup='weight on the back leg; dagger hand raised high above the head (about to stab down), free hand forward',
                  strike='lunge; dagger arm fully extended forward, free hand pulled back',
                  hit='torso thrown back, weight on the rear leg, head jerked back, hood and scarf still in place; dagger arm flung back, free hand up'),
        ko=dict(keep='깊게 눌러쓴 후드(얼굴은 그늘, 눈빛 두 점까지만) + 짧은 어깨 망토, 입·코를 가린 스카프, 끈 많은 짙은 갈색 가죽 갑옷, 역수 단검 하나.',
                fix='후드·어깨 망토·입과 코를 가린 스카프 = 제복 열쇠 색(스카프는 따뜻한 어둠 외곽선으로 후드와 나눔), 가는 허리 천만 장식 열쇠 색 (얼굴에 장식 색 금지). 가죽은 따뜻한 짙은 갈색(청회색 금지) + 왼쪽 위 따뜻한 림 라이트. 진과 같은 틀.',
                face='도적은 깊은 후드 + 스카프, 얼굴은 그늘',
                draft_keep='입·코까지 감싼 깊은 후드(어두운 눈 틈만), 경계하는 태도(태도만 — 다리·웅크린 깊이·크기는 guide_strip.png 그대로), 짙은 갈색 가죽 가슴 갑옷, 허벅지·정강이를 감은 갈색 가죽 끈 여럿, 부드러운 장화, 단검 하나.',
                draft_fix='초안은 후드와 스카프가 한 덩어리의 밝은 시안 → 후드 + (초안에 없는) 짧은 어깨 망토 + 입·코의 스카프 = 모두 제복 열쇠 색, 스카프는 따뜻한 어둠 외곽선으로 따로 보이게. '
                          '남색 소매·바지·장화 → 따뜻한 짙은 갈색·회색(열쇠 색 밖에 파랑 없음). 가슴에 파묻힌 머리·배 앞에 꼬인 팔·엉덩이 뒤로 삐져나온 칼 → '
                          '정상 4등신, 머리는 어깨 위, 단검은 가까운 손에 역수로(가이드대로). 새까만 눈 틈 → 따뜻한 어둠, 눈빛 두 점까지.'),
    ),
})

# ───────── first monster batch: humanoids (kind 'monster', posekit guides like the captains) ─────────
MONSTER_COMMON_FIX = ['a common monster seen in large numbers: an ordinary member of its kind, no unique features, no crown, banner or trophy']
CHARS.update({
    'monster_skeleton': dict(
        kind='monster', en='Skeleton soldier', enemy='해골 병사', order=21, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'monster_skeleton/concept_01.png'},
        draft=dict(keep=('the bowl-shaped open-faced helmet over a grinning skull (its colour from COLOURS: neutral grey steel, not rusty '
                         'brown), two red eye points, the big ribcage, pale bones, tattered cloth hanging from the shoulders and as a ragged '
                         'loincloth, the round wooden shield with an iron rim, bare bony feet'),
                   fix=[ONE_HEAD_FIX + ': one skull inside one helmet',
                        'the draft sword is a hooked, machete-like blade: a straight, notched one-handed sword in the near hand as the guide holds it',
                        'the draft faces the viewer and fills the far leg and forearm solid black: three-quarter view facing right, every limb '
                        'drawn as bone (no black silhouette limbs)',
                        'the draft spine is thin and leaves a hole of background at the waist: a chunky spine and pelvis, no background showing '
                        'through the torso',
                        'the draft cloth is blue-black: dark desaturated red or cold grey (COLOURS)',
                        'the draft eyes glow with a halo: two small red clusters, no halo']),
        brief=dict(silhouette='a human-sized undead soldier: the same 4-head build as the captains (the helmeted skull is the 110 px head), round shield and sword',
                   size='SMALL (human scale, the same height as a captain)', attack='melee: sword slash',
                   where='frost and holy-ground battles, magic-investigation contracts, the demon calamity army (the most frequent monster in battle)'),
        weapon_desc='a notched one-handed sword (neutral grey steel) in the near hand and a battered round wooden shield with an iron rim on the far arm (the guide shield\'s size)',
        keep=['skull under a dented open-faced steel helmet', 'two small red points of light in the eye sockets (just two small red pixel clusters, no halo)',
              'CHUNKY simplified bones: the ribcage as one shape, thick limb bones, big hands and feet', 'tattered dark cloth scraps at the hips',
              'no skin, no hair'],
        colours=[('bone', 'pale ivory #e8e2cc, shaded #b4ad98 / #7e786a (never pure white)'),
                 ('helmet, sword, shield rim', 'NEUTRAL grey steel #8a8a86 / #5a5652, light #c8c6c0 (no rust brown)'),
                 ('cloth scraps', 'dark desaturated red #5e2f2c / #3e2220 or cold grey #4a4e56'), ('shield wood', 'warm brown'),
                 ('eyes', 'bright red #ff4a3a (two small clusters, no halo)'), ('outline', 'dark neutral #2e2a28 around the bones')],
        fix=MONSTER_COMMON_FIX + ['bones must stay chunky: thin realistic bones vanish at 64 px', 'no green fire, glow or aura',
                                  'four separate materials, not one warm-brown mass: ivory bone, grey steel, dark red / cold grey cloth, '
                                  'brown wood; the dark outline keeps the pale bones readable on snow, and the bright red eyes read in '
                                  'the dark eye sockets'],
        pose=dict(idle='shield up, sword ready, slightly hunched',
                  windup='weight on the back leg; sword raised up and back behind the head, shield kept forward',
                  strike='step-in lunge; sword cutting forward and down at full extension, shield pulled in',
                  hit='torso thrown back, weight on the rear leg, skull snapped back, jaw open; shield up, sword arm dropped down-back'),
        ko=dict(keep='찌그러진 회색 강철 개방형 투구 아래 해골, 눈구멍의 밝은 붉은 점 둘, 굵게 단순화한 뼈, 허리의 해진 천, 이 빠진 한손검 + 쇠테 두른 둥근 나무 방패.',
                fix='재질을 나눈다: 뼈 = 옅은 상아색, 투구·칼 = 중성 회색 강철(녹슨 갈색 아님), 천 = 탁한 짙은 빨강 또는 찬 회색, 눈 = 밝은 빨강 #ff4a3a — 온통 따뜻한 갈색 덩어리 금지, '
                    '눈 위에서도 보이게 뼈 둘레에 어두운 외곽선. 뼈는 굵게(가는 뼈는 64px 에서 사라진다), 순백 금지, 초록 불꽃·빛 없음. 사람과 같은 크기.',
                draft_keep='사발 모양 개방형 투구(색은 회색 강철)와 이를 드러낸 해골, 붉은 눈 점 둘, 큰 갈비뼈, 때 묻은 흰 뼈, 어깨와 허리에 걸친 해진 검은 천, 쇠테 두른 둥근 나무 방패, 맨발 뼈.',
                draft_fix='머리는 정확히 하나(같은 초안의 다른 장들은 머리가 둘). 갈고리 진 마체테 같은 칼 → 곧고 이 빠진 한손검(가이드 손). 정면을 보며 먼 다리·팔이 새까만 덩어리 → '
                          '오른쪽 보는 3/4, 모든 팔다리를 뼈로. 가는 척추·허리에 뚫린 배경 구멍 → 굵은 척추·골반, 몸통에 구멍 없음. 청흑색 천 → 탁한 짙은 빨강 또는 찬 회색. 눈의 빛 번짐 없이 작은 붉은 점.'),
    ),
    'monster_desert-bandit': dict(
        kind='monster', en='Desert bandit', enemy='사막 도적', order=23, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'monster_desert-bandit/concept_05.png'},
        draft=dict(keep=('the sand head wrap and face veil, the loose sand tunic with wrapped forearms, an open vest, a sash with a long cloth '
                         'flap hanging at the front, very baggy trousers gathered at the shins, dark wrapped boots, the alert fighting attitude '
                         'with the free hand raised as a guard (attitude only: legs, stance width, crouch depth and size exactly as guide_strip.png)'),
                   fix=[ONE_HEAD_FIX,
                        'the draft scimitar is a huge sickle-like crescent: a normal scimitar about as long as the guide sword with a moderate '
                        'curve, in the near hand as the guide holds the sword',
                        'the draft eye gap reads like dark goggles: a narrow skin-coloured gap between wrap and veil with two eyes, no goggles',
                        'the draft vest and sash are dark wine-red: dark brown #5e3a26 (COLOURS)']),
        brief=dict(silhouette='a human raider in loose desert robes and a head wrap, one curved sword',
                   size='SMALL (human scale)', attack='melee: scimitar slash', where='desert battles (the two desert provinces)'),
        weapon_desc=('a curved scimitar in the near hand (where the guide holds the sword, same angle). NO shield: the guide\'s round shield is a '
                     'placeholder - the far hand is EMPTY and held up open as a guard where the shield is'),
        keep=['sand-coloured head wrap and a face veil (only the eyes show)', 'loose sand-coloured robe-tunic', 'brown leather vest and a sash',
              'baggy trousers tucked into leather boots', 'tan skin on the hands'],
        colours=[('skin', '#c68a5c'), ('head wrap, robe', 'sand #e8d5a3 (muted; shade steps #b89c6e / #7e6648, never white)'),
                 ('vest, sash, boots', 'dark brown #5e3a26 / #3e261a (clearly darker than the sand cloth)'), ('scimitar', 'NEUTRAL steel grey'),
                 ('outline', 'a strong dark warm-brown #2e2018 all around the figure')],
        fix=MONSTER_COMMON_FIX + ['exactly one weapon (the scimitar); no shield, no second blade',
                                  'the sand robe must not merge with the desert sand background: a strong dark outline all around the '
                                  'figure, the deep shade steps on the robe, and the dark-brown vest, sash and boots as dark value accents'],
        pose=dict(idle='scimitar held ready in front, free hand up as a guard',
                  windup='weight on the back leg; scimitar raised up and back behind the head, free hand forward',
                  strike='step-in lunge; scimitar slashing forward and down at full extension, free hand pulled back',
                  hit='torso thrown back, weight on the rear leg, wincing; scimitar arm dropped down-back, free hand up'),
        ko=dict(keep='모래색 머리 두건과 얼굴 가리개(눈만 보임), 헐렁한 모래색 겉옷, 갈색 가죽 조끼·허리 천, 통 넓은 바지와 장화, 곡도(시미터) 하나.',
                fix='방패 없음 — 가이드의 둥근 방패 자리는 빈손(막는 자세). 모래색이 사막 모래 배경에 묻히지 않게 둘레에 진한 짙은 갈색 외곽선, 겉옷의 깊은 그늘, 짙은 갈색 조끼·허리 천·장화(어두운 명암 포인트).',
                draft_keep='모래색 머리 두건과 얼굴 가리개, 팔뚝을 감은 헐렁한 모래색 상의, 앞이 열린 조끼, 앞에 긴 천이 늘어진 허리 천, 정강이에서 모인 아주 헐렁한 바지, 감싼 짙은 장화, 싸울 태세와 막는 빈손(태도만 — 다리·자세 폭·크기는 guide_strip.png 그대로).',
                draft_fix='머리는 정확히 하나(같은 초안의 다른 장들은 머리가 둘). 낫 같은 거대한 초승달 칼 → 가이드 칼 길이의 보통 곡도(적당히 휨), 가이드 손. '
                          '고글처럼 보이는 눈 틈 → 피부색 좁은 틈과 두 눈(고글 없음). 와인빛 조끼·허리 천 → 짙은 갈색 #5e3a26.'),
    ),
    'monster_bandit': dict(
        kind='monster', en='Bandit', enemy='산적', order=25, weapon='sword_shield',
        frames=dict(idle='idle_0', windup='key_windup', strike='key_strike', hit='key_hit'),
        concepts={'concept.png': 'monster_bandit/concept_01.png'},
        draft=dict(keep=('the red bandana with two short tails at the back, long dark hair, stubble and a sneer, a torn short-sleeved shirt '
                         'under a sleeveless jerkin, a rope belt wound several times, dark trousers, worn boots folded down at the top, '
                         'a short hand axe'),
                   fix=[ONE_HEAD_FIX,
                        'the draft holds a second wooden handle / club in the far hand and has NO buckler: the far arm carries ONLY the small '
                        'round wooden buckler of CHARACTER; exactly one axe, nothing else in the hands',
                        'the draft holds the axe across the belly: the axe only in the near hand, as the guide holds the sword',
                        'the draft jerkin is black and the build bulky and muscle-heavy: a patched brown leather jerkin (COLOURS) on a wiry build',
                        'the draft bandana is bright red: muted dark red #8f2d3a']),
        brief=dict(silhouette='a scruffy human outlaw with a hand axe and a small buckler', size='SMALL (human scale)',
                   attack='melee: axe chop', where='plains, holy-ground and coast battles (the starting region)'),
        weapon_desc=('a short hand axe in the near hand (where the guide holds the sword, same angle) and a SMALL round wooden buckler on the far arm '
                     '(about 0.6 heads across, smaller than the guide shield)'),
        keep=['red bandana on the head', 'stubble and a sneer', 'patched brown leather jerkin', 'rope belt', 'dark trousers, worn boots', 'wiry build'],
        colours=[('skin', '#e0ac7e'), ('bandana', 'dark red #8f2d3a'), ('jerkin', 'brown leather #a8764e / #6b4a32'),
                 ('axe head', 'NEUTRAL steel grey')],
        fix=MONSTER_COMMON_FIX + ['he must read differently from the desert bandit: red bandana, bare face, axe and buckler'],
        pose=dict(idle='buckler forward, axe ready',
                  windup='weight on the back leg; axe raised up and back behind the head, buckler kept forward',
                  strike='step-in lunge; axe chopping forward and down at full extension, buckler pulled in',
                  hit='torso thrown back, weight on the rear leg, wincing; buckler up, axe arm dropped down-back'),
        ko=dict(keep='붉은 두건, 수염 자국·비웃는 얼굴, 기운 가죽 조끼, 밧줄 허리띠, 짧은 손도끼 + 작은 둥근 나무 버클러.',
                fix='사막 도적과 확실히 다르게(붉은 두건·드러난 얼굴·도끼·버클러). 버클러는 가이드 방패보다 작게.',
                draft_keep='뒤로 짧은 꼬리 둘이 늘어진 붉은 두건, 검은 긴 머리, 수염 자국과 비웃음, 찢어진 반소매 셔츠 위 민소매 조끼, 여러 번 감은 밧줄 허리띠, 짙은 바지, 끝을 접은 낡은 장화, 짧은 손도끼.',
                draft_fix='머리는 정확히 하나(같은 초안의 다른 장들은 머리가 둘). 먼 손의 두 번째 나무 자루(곤봉)를 없애고 버클러만(초안에는 버클러가 없다) — 도끼 하나뿐. '
                          '배 앞에 가로로 든 도끼 → 가까운 손(가이드 손). 검은 조끼·우람한 근육 → 기운 갈색 가죽 조끼, 마른 체격. 새빨간 두건 → 탁한 짙은 빨강 #8f2d3a.'),
    ),
})

# ───────── first monster batch: non-humanoids (kind 'creature', size-box guides, no posekit) ─────────
# Same pixel scale as the humans (head 110 px; crouched human idle ~400 px). layout '2x2' = four 768x512 quadrants
# (top: idle, wind-up; bottom: strike, hit), lowest pixel of each pose on y=QBASE of its quadrant (as the mounted sheet);
# '1x4' = the captains' row, lowest pixel on BASELINE. boxes = (w, h) px of each pose (a size guide only, drawn as an outline).
QBASE = round(0.9 * (SH_ // 2))   # 461
CREATURES = {
    'monster_wolf': dict(
        en='Wild wolf', enemy='들늑대', order=22, layout='2x2',
        concepts={'concept.png': 'monster_wolf/concept_06.png'},
        draft=dict(keep=('the head held below the shoulder line with a snarl and bared fangs, a thick darker ruff over the neck and shoulders, '
                         'pale cheeks and muzzle, pale lower legs and paws, a long bushy tail, a lean long-legged build'),
                   fix=['the draft fur is a noise of thin hatching strokes: a few big fur clumps in 2-3 tones',
                        'the draft fur is olive / khaki grey: neutral-cool grey as in COLOURS, darker back, lighter belly',
                        'the draft eye is orange-red: amber',
                        'the draft has four legs and one tail - keep exactly that; paint the two far legs a tone darker so all four read separately',
                        'the draft holds the tail out level and the ears up: the tail hangs low and the ears are laid back (as in DESIGN / POSES)']),
        boxes=dict(idle=(420, 250), windup=(400, 220), strike=(540, 260), hit=(400, 280)),
        brief=dict(silhouette='a lean grey wild wolf in side three-quarter view, head low, tail down: a long horizontal shape',
                   size='SMALL: shoulder about half a standing human, nose to tail about one human height (idle ~420 x 250 px)',
                   attack='melee: lunging bite', where='plains and forest battles (the most frequent beast)'),
        design=['shaggy grey fur with a darker back and a lighter belly', 'amber eyes', 'bared fangs, ears back', 'four legs, ONE tail, ONE head'],
        colours=[('fur', 'grey #8a8f99, dark #5c606a, light grey-beige belly'), ('eyes', 'amber #f2c94c (never grey)'),
                 ('mouth interior', 'dark red-brown #5a2a24 / #3e1e1a (no magenta, pink or purple)'), ('fangs', 'off-white')],
        fix=['a real wolf (not a werewolf, never standing up)',
             'the eyes are AMBER #f2c94c and the open mouth is dark red-brown, in every pose', 'exactly four legs, one tail and one head in every pose',
             'the PAWS are the lowest pixels (on the baseline, as DELIVERABLE says); the low-hanging tail tip always stays above the paw line'],
        pose=dict(idle='standing on all fours, head lowered, snarling, tail down',
                  windup='crouched back on the haunches, front low, ready to pounce, ears flat',
                  strike='leaping lunge to the right: body stretched, forelegs reaching forward, jaws wide open; one hind paw still touches the baseline',
                  hit='recoiling backward: head thrown up and back, yelping, hind legs bent, front paws lifted'),
        ko=dict(brief='회색 들늑대, 머리 낮추고 으르렁, 꼬리 아래. 작은 몬스터(대기 상자 약 420x250px). 물기 근접 공격.',
                pose='① 네 발로 서서 으르렁 ② 뒷다리에 웅크려 덮칠 준비 ③ 오른쪽으로 덮치며 문다(뒷발 하나는 바닥) ④ 머리를 젖히며 뒤로 물러남',
                draft_keep='어깨선 아래로 낮춘 머리와 드러낸 송곳니, 목·어깨의 짙은 갈기, 밝은 뺨·주둥이, 밝은 다리 끝·발, 굵고 긴 꼬리, 다리가 긴 마른 체격.',
                draft_fix='가는 빗금 털(노이즈) → 큰 털 덩어리 2~3단. 올리브·카키빛 회색 → 중성·찬 회색(등 짙게, 배 밝게). 주황빛 붉은 눈 → 호박색. 다리 넷·꼬리 하나 그대로, 먼 쪽 다리 둘은 한 단계 어둡게. '
                          '초안은 꼬리를 수평으로 들고 귀를 세웠다 → 꼬리는 낮게 늘어뜨리고 귀는 뒤로 젖힌다(DESIGN·POSES 대로). 바닥선에는 발, 꼬리 끝은 발보다 위.'),
    ),
    'monster_harpy': dict(
        en='Harpy', enemy='하피', order=24, layout='2x2',
        concepts={'concept.png': 'monster_harpy/concept_09.png'},
        draft=dict(keep=('two large blue-purple feathered wings in place of arms, wild spiky brown-auburn hair, red eyes, brown feathered '
                         'thighs, scaly bird legs ending in big curved talons, the hovering pose with the talons hanging down (legs kept short, see BRIEF)'),
                   fix=['the draft is too revealing (fur bandeau, bare shoulders and bare midriff): cover the WHOLE torso - shoulders, chest '
                        'and belly - with a DARK BROWN feather bodice (#7a5236 family, continuous with the brown feathered thighs; purple only on '
                        'the wings and the tail); no exposed chest or skin anywhere except the face and neck',
                        'the draft shows a third wing-shaped mass behind the hips: exactly TWO wings; behind the hips only the short fan of tail feathers',
                        'the draft blurs the wing roots with human shoulders: the wings grow from the shoulders INSTEAD of arms (three small claws '
                        'at the wing bend), no human arms or hands',
                        'the draft wingspan fills the whole canvas: fold the wings enough that each pose fits its box',
                        'the draft legs are yellow-green: brown as in COLOURS',
                        'the draft is a blank-faced anime girl facing the viewer: three-quarter view facing right, a fierce, wild face']),
        boxes=dict(idle=(440, 400), windup=(420, 420), strike=(560, 340), hit=(480, 400)),
        brief=dict(silhouette='a hovering bird-woman: human head and torso at the captains\' scale (head 110 px, torso like a 4-head human\'s), '
                              'wings instead of arms, SHORT scaly bird legs with the knees drawn up and talons, a feather tail - wide because of the wings',
                   size=('SMALL: body like a human but with short tucked bird legs, so talon tip to crown is about 330 px; the half-raised wing '
                         'tips add the rest of the idle box (~440 x 400 px). If they conflict, the 110 px head wins: keep the legs short and '
                         'tucked, never shrink the head to fit the box (the box may grow to ~430 px tall)'),
                   attack='ranged in the game data (template "drake": the engine shoots a fire bolt): a shrieking pose, no projectile drawn',
                   where='desert battles and the beast calamity army'),
        design=['wild auburn hair', 'red eyes, a fierce face', 'purple feathered wings instead of arms (three small claws at the wing bend)',
                'a brown feather bodice covering the shoulders, chest and belly (no bare skin except the face and neck)',
                'short scaly bird legs with big talons, knees drawn up while hovering', 'a short fan of purple tail feathers'],
        colours=[('skin', '#e0ac7e (muted)'),
                 ('wing and tail feathers', 'muted purple #8a6aa8 shaded with #5a4a7a (blue-purple, never pink or magenta); their highlights stay '
                  'cool or neutral (toward grey-lavender such as #a898c0), never warm - warming purple drifts toward pink (this overrides '
                  '"highlights toward warm yellow" for the purple feathers)'),
                 ('bodice feathers, thigh feathers', 'darker brown #7a5236 / #563a26 (clearly darker than the skin, so the bodice never reads as bare skin)'),
                 ('legs and talons', 'brown #8a6040 family, dark talons'), ('eyes', 'red #d6455d'),
                 ('outline', 'a strong dark outline #2e2420 all around the figure (it fights over desert sand)')],
        fix=['tasteful: the chest is covered with brown feathers, darker than the skin',
             'reads on the desert sand background: the strong dark outline and the dark-brown bodice give dark value accents',
             'the feathers stay blue-purple and dark enough: no pixel may come close to the #FF00FF background (see the magenta rule)',
             'the engine draws the projectile and the glow: no fire, light or effect in the drawing'],
        pose=dict(idle='hovering low with the wings half raised; short legs with the knees drawn up, talons hanging below them, the lowest talon on the baseline',
                  windup='wings raised high and back, head drawn back, mouth open (about to shriek), talons drawn up',
                  strike='lunging forward: head and chest thrust forward, mouth wide open shrieking, wings flung forward, talons reaching forward-down',
                  hit='knocked back: wings flung up and out, body jerked back, feathers ruffled, wincing'),
        ko=dict(brief='공중에 뜬 새 여인. 사람 머리·몸통(대장과 같은 배율, 머리 110px), 팔 대신 보라 날개, 무릎을 당긴 짧은 새 다리·발톱(발톱~정수리 약 330px, '
                      '나머지 높이는 반쯤 든 날개 끝). 날개 때문에 넓다(대기 약 440x400px). 상자와 맞지 않으면 머리 110px 가 우선(다리를 짧게, 머리를 줄이지 않음). '
                      '몸통 깃털은 갈색(허벅지와 이어짐), 보라는 날개·꼬리만, 보라의 밝은 면은 차갑게(분홍 쪽 금지). 게임에서는 원거리(엔진이 불덩이를 그림).',
                pose='① 날개 반쯤 들고 낮게 떠 있음(발톱 끝이 바닥선) ② 날개를 높이 뒤로, 입 벌림 ③ 머리·가슴을 앞으로 내밀며 비명, 날개 앞으로 ④ 날개가 위로 젖혀지며 뒤로 밀림',
                draft_keep='팔 대신 큰 청보라 깃털 날개 둘, 삐죽한 갈색·적갈색 머리, 붉은 눈, 깃털 덮인 갈색 허벅지, 큰 굽은 발톱의 비늘 새 다리, 발톱을 늘어뜨리고 떠 있는 자세.',
                draft_fix='초안은 노출이 심하다(털 가슴띠·맨 어깨·맨 배) → 어깨·가슴·배 전체를 허벅지 깃털과 이어지는 깃털 상의·갈색 가죽으로 덮는다, 얼굴·목 말고 맨살 없음. '
                          '엉덩이 뒤 세 번째 날개 같은 덩어리 → 날개는 정확히 둘, 뒤에는 짧은 꼬리 깃털만. 날개는 팔 대신(사람 팔·손 없음, 날개 꺾임에 작은 발톱 셋). '
                          '화면을 가득 채운 날개 → 자세마다 상자 안에 들게 접는다. 연두색 다리 → 갈색. 정면을 보는 무표정 애니 소녀 → 오른쪽 보는 3/4, 사나운 얼굴.'),
    ),
    'monster_gargoyle': dict(
        en='Gargoyle', enemy='가고일', order=26, layout='2x2',
        concepts={'concept.png': 'monster_gargoyle/concept_02.png'},
        draft=dict(keep=('the blue-grey stone body with crack lines, the beaked snout with a red eye, stone wing bones with dark membranes, the '
                         'crouch on all fours with big hooked claws, the long thin tail ending in a spade tip'),
                   fix=['the draft wings span the whole canvas: in idle fold them half open so the pose fits its box (~380 x 330); only the '
                        'wind-up spreads them wide',
                        'the draft has no readable horns: add two clear curved horns',
                        'the draft runs the wing bones down into the front claws (wing and arm merged): two separate stone arms with claws, and '
                        'two wings growing from the back - exactly two wings, four limbs, one tail, one head',
                        'the draft cracks cover every surface: only a few big cracks',
                        'the draft wing membranes are near-black: dark stone grey #44494f so they read on the dark battlefield']),
        boxes=dict(idle=(380, 330), windup=(520, 420), strike=(560, 340), hit=(460, 360)),
        brief=dict(silhouette='a hunched stone demon statue come alive: crouching on clawed hands and feet, bat wings, curved horns, a tail',
                   size='SMALL: crouched about 0.8 of a human idle height (idle ~380 x 330 px); wider when the wings spread',
                   attack='ranged in the game data (template "drake": the engine shoots a fire bolt): a roaring / spitting pose, no projectile drawn',
                   where='the volcanic mountains and the beast calamity army'),
        design=['grey stone skin with a few big cracks and chipped edges', 'curved horns', 'bat wings of stone', 'red eyes (two small red clusters)',
                'big claws, a pointed tail'],
        colours=[('stone', 'grey #6b737c, dark #44494f, light #9aa3ad'), ('eyes', 'red #d6455d (never purple)'), ('mouth', 'dark')],
        fix=['stone texture only as a few big cracks, not noise', 'the eyes are RED #d6455d in every pose, not purple', 'the engine draws the fire: no flames, glow or dust in the drawing'],
        pose=dict(idle='crouched like a statue on all fours, wings folded half open, head low',
                  windup='rearing up on the hind legs, wings spread wide, claws raised, head pulled back',
                  strike='lunging forward low: head thrust forward with the jaws wide open (spitting), claws reaching forward, wings swept back',
                  hit='knocked back onto the haunches: head thrown back, wings flung up, one claw raised to guard'),
        ko=dict(brief='살아 움직이는 돌 악마상: 웅크린 몸, 박쥐 날개, 굽은 뿔, 꼬리. 웅크린 대기 약 380x330px. 게임에서는 원거리(엔진이 불덩이를 그림).',
                pose='① 석상처럼 네 발로 웅크림 ② 뒷다리로 일어서며 날개 펼침 ③ 낮게 앞으로 덮치며 입을 크게 벌림 ④ 주저앉듯 뒤로 밀리며 날개가 젖혀짐',
                draft_keep='금 간 청회색 돌 몸, 부리 같은 주둥이와 붉은 눈, 돌 날개 뼈와 어두운 날개막, 큰 갈고리 발톱으로 네 발 웅크림, 끝이 삽 모양인 가는 긴 꼬리.',
                draft_fix='화면을 가로지르는 날개 → 대기에서는 반쯤 접어 상자(약 380x330)에 들게, 펼치는 것은 공격 준비뿐. 뿔이 안 보임 → 굽은 뿔 둘. '
                          '날개 뼈가 앞발로 이어져 팔과 날개가 붙음 → 발톱 달린 팔 둘 + 등에서 나온 날개 둘(날개 둘·다리 넷·꼬리 하나·머리 하나). 온몸의 잔금 → 큰 금 몇 개. 새까만 날개막 → 짙은 돌 회색 #44494f.'),
    ),
    'monster_giant-spider': dict(
        en='Giant spider', enemy='거대 거미', order=27, layout='2x2',
        concepts={'concept.png': 'monster_giant-spider/concept_03.png'},
        draft=dict(keep=('the big round abdomen behind a smaller head, the cluster of glossy red eyes (two big, several small) on the front of '
                         'the head, short pedipalps at the mouth, long jointed legs in a wide arch, the low crouch'),
                   fix=['exactly EIGHT legs, four per side, in every pose (count them); the short pedipalps at the mouth are not legs and stay short',
                        'the draft body and legs are near-black on a dark ground: dark purple carapace as in COLOURS plus a clear cool rim light '
                        'along the top edges of the abdomen, the head and every leg',
                        'the draft is covered in fine hair noise: a smooth carapace and only a few short spikes on the legs',
                        'the draft legs are very long and thin: thicker, shorter legs so the idle fits about 520 x 220 px and every leg survives '
                        'downscaling',
                        'the draft fangs are hidden in the hair: two clear fangs']),
        boxes=dict(idle=(520, 220), windup=(480, 320), strike=(600, 260), hit=(500, 240)),
        brief=dict(silhouette='a low, wide eight-legged spider in side three-quarter view; the body about knee-to-chest height of a human',
                   size='SMALL in the data but WIDE: about 520 x 220 px in idle (legs spread)', attack='melee: lunging bite with the fangs',
                   where='forest battles (the elf woods)'),
        design=['dark purple carapace with a lighter purple sheen on the top edges', 'hairy, segmented legs', 'a cluster of red eyes', 'two big fangs'],
        colours=[('carapace', 'dark purple #3b3346, darker #241b29, sheen #5a4a66'), ('eyes', 'red #d6455d')],
        fix=['exactly eight legs, one body, one head', 'very dark: add a clear cool rim light along the top edges so it reads on the dark battlefield',
             'side three-quarter view: the four near legs in front of the body, the four FAR legs visible above and behind the body, one tone '
             'darker, so all eight can be counted',
             'REDRAW (message F): the first delivery\'s design, colours and rim light are approved (glossy dark purple body, grey segmented '
             'legs, red eye cluster, pale fangs, cool rim along the top edges) - keep them; only the legs change',
             'COUNT the legs in every pose before saving: 4 near + 4 far, each leg one clear unbroken line from body to tip, no leg hidden '
             'behind another, no two legs crossing or merging, gaps of magenta between neighbouring legs',
             'no web, no poison drip, no effect'],
        pose=dict(idle='crouched on eight legs, all eight planted and spread evenly like a fan, each one separately visible',
                  windup='rearing up: ONLY the front two legs (the first leg on each side) raised high, the other 6 planted on the ground, fangs bared',
                  strike='lunging forward: body low and stretched, front legs stabbing forward-down, fangs open',
                  hit='recoiling backward: body tipped back, the legs splayed stiffly outward (NOT curled under), all eight still countable'),
        ko=dict(brief='낮고 넓은 다리 여덟 개 거미, 짙은 보라 등껍질, 붉은 눈 무리, 큰 독니. 대기 약 520x220px. 물기 근접 공격.',
                pose='① 여덟 다리로 웅크림(여덟 개 모두 바닥에, 부채처럼 고르게 벌려 하나하나 보이게) ② 앞다리 둘(양쪽 첫 다리)만 높이 들고 일어섬, 나머지 여섯은 바닥 '
                     '③ 낮게 앞으로 덮치며 앞다리로 찍음 ④ 몸이 뒤로 젖혀지며 다리를 뻣뻣하게 벌림(오므리지 않음, 여덟 개가 보이게). 먼 쪽 다리 넷은 몸 위·뒤로 보이게 한 단계 어둡게.',
                draft_keep='작은 머리 뒤의 크고 둥근 배, 머리 앞의 반짝이는 붉은 눈 무리(큰 눈 둘 + 작은 눈 여럿), 입가의 짧은 더듬이다리, 넓게 휜 긴 마디 다리, 낮게 웅크린 자세.',
                draft_fix='다리는 모든 자세에서 정확히 여덟(한쪽에 넷) — 입가의 짧은 더듬이다리는 다리가 아니고 짧게. 어두운 바닥에 묻히는 새까만 몸 → 짙은 보라 등껍질 + 배·머리·다리 윗선의 찬 림 라이트. '
                          '온몸의 잔털 노이즈 → 매끈한 등껍질, 다리에 짧은 가시 몇 개. 아주 길고 가는 다리 → 굵고 짧게(대기 약 520x220px, 줄여도 다리가 보이게). 털에 묻힌 독니 → 큰 독니 둘이 보이게.'),
    ),
    'monster_wraith': dict(
        en='Wraith', enemy='망령', order=28, layout='1x4',
        concepts={'concept.png': 'monster_wraith/concept_07.png'},
        draft=dict(keep=('the deep hood over a dark face with two small cyan eyes, the heavy draped hood and shoulder cloth, the long ragged '
                         'hem in strips, thin skeletal hands with long claws reaching forward, the forward-leaning hovering posture'),
                   fix=['the draft robes are teal / mint: pale blue as in COLOURS',
                        'the draft robe dissolves into a dark semi-transparent smear with a separate curly tendril at its side: a fully opaque '
                        'tattered robe that narrows into ONE wispy tail, its tip the lowest point, on the baseline',
                        'the draft face is pure black: dark grey-blue as in COLOURS, the cyan eyes small with no halo',
                        'the draft hides the near hand in the robe folds: both skeletal hands clearly readable in every pose']),
        boxes=dict(idle=(240, 360), windup=(260, 380), strike=(320, 340), hit=(280, 350)),
        brief=dict(silhouette='a hooded floating ghost in long tattered robes that thin into a wispy tail; skeletal clawed hands; no legs',
                   size='SMALL: about a human idle height (idle ~240 x 360 px)',
                   attack='ranged in the game data (template "ghost": the engine shoots a curse bolt): a casting / wailing pose, no projectile drawn',
                   where='swamp and holy-ground battles, magic-investigation contracts, the demon calamity army'),
        design=['a deep hood with a dark face and two cyan eyes (small clusters, no halo)', 'long tattered pale-blue robes',
                'thin skeletal hands with long claws', 'the robe ends in a wispy, tattered tail (no legs, no feet)'],
        colours=[('robes', 'pale blue #b8c8e8, shade #7a8ab0, light #e8f0ff (muted)'), ('eyes', 'cyan #6ff0f0'), ('face, hands', 'dark grey-blue')],
        fix=['the tail tip is the lowest point and sits on the baseline (the engine places that point on the ground)',
             'paint it fully opaque (no semi-transparency): the ghostly look comes from the colours and the tattered edges',
             'no glow halo, smoke or particles around it'],
        pose=dict(idle='hovering, arms hanging, the robe tail wisping down to the baseline',
                  windup='arms raised up and back, claws spread, robe billowing back',
                  strike='lunging forward: both clawed hands thrust forward, hood forward, mouth open wailing (casting)',
                  hit='recoiling: body bent back, arms flung up, robe torn and fluttering backward'),
        ko=dict(brief='후드 쓴 떠다니는 유령, 해진 긴 연청색 로브가 가는 꼬리로 끝남, 앙상한 손톱, 다리 없음. 대기 약 240x360px. 게임에서는 원거리(엔진이 저주탄을 그림).',
                pose='① 팔을 늘어뜨리고 떠 있음(꼬리 끝이 바닥선) ② 팔을 위·뒤로 들고 로브가 뒤로 부풂 ③ 두 손을 앞으로 내밀며 울부짖음(시전) ④ 몸이 뒤로 꺾이며 팔이 위로',
                draft_keep='어두운 얼굴에 작은 청록 눈 둘이 있는 깊은 후드, 무겁게 늘어진 후드·어깨 천, 갈래갈래 찢어진 긴 밑단, 앞으로 뻗은 긴 손톱의 앙상한 손, 앞으로 기운 채 떠 있는 자세.',
                draft_fix='청록·민트빛 로브 → 연청색. 반투명하게 번지며 사라지는 밑단과 옆의 따로 떨어진 꼬불 꼬리 → 불투명한 해진 로브가 가는 꼬리 하나로 좁아지고 그 끝이 바닥선. '
                          '새까만 얼굴 → 짙은 청회색, 눈은 작게 번짐 없이. 로브 주름에 묻힌 가까운 손 → 두 손 모두 잘 보이게.'),
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
# the background key: sheets.py removes every colour near #FF00FF, so a figure colour there punches holes (Felix, 1st delivery)
MAGENTA_EN = ('NO figure pixel may be magenta-like: every colour of the figure must stay clearly away from the background key #FF00FF, '
              'RGB distance sqrt((255-R)^2 + G^2 + (255-B)^2) >= 150 (no hot pink, magenta or bright violet; purples stay dark blue-purple such as '
              '#5a4a7a). If you reduce the palette, reduce the FIGURE colours only and never merge a figure colour into the background colour')
MAGENTA_CHECK_EN = 'no figure pixel is #FF00FF or magenta-like (every figure colour at RGB distance >= 150 from #FF00FF)'
SPEC_EN = [
    'ONE PNG, 1536x1024 (landscape), the SAME character drawn 4 times in ONE row (1x4, never a 2x2 grid or a single pose), left to right: idle, wind-up, strike, hit',
    'each figure exactly where guide_strip.png has it: same size, same scale, same position, same limb lengths',
    f'the lowest pixel of every figure (its soles) on the line y = {BASELINE} (85% of the height); ' + HEIGHT_EN,
    f'at least {GAP} px of empty magenta between any two figures and between a figure and the image border (a weapon may reach over a '
    'neighbour\'s column as in the guide, but never closer than that)',
    'background: perfectly flat solid magenta #FF00FF everywhere (preferred; a transparent PNG is also accepted) - no gradient, floor, cast shadow or scenery',
    MAGENTA_EN,
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
    MAGENTA_CHECK_EN,
    'reads clearly when shrunk to 64 px tall on a dark background',
]
KEYS_CHECK_EN = ('the uniform ({outfit}) uses ONLY the four outfit keys and the trim ({accent}) ONLY the three accent keys, exact hex, flat; '
                 'the seven keys appear nowhere else and nothing else on the figure is blue, slate, teal or mint; every other figure colour '
                 '(outline and shadows included) is at RGB distance >= {near} from all seven keys: the key check prints 0 near-key pixels')
KEY_TOL_PX = 34                # tools/art/sheets.py KEY_TOL: colours this close to a key are snapped onto it (and recoloured)
KEY_NEAR = 50                  # every non-key figure colour stays at least this far from every key
# warm / neutral dark ramp for the outline and the shadows outside the uniform on class sheets (all >= KEY_NEAR from the keys).
# The anchor's own dark violet-navy outline / shadow colours (#474269, #2c2840, #28253c, #444061 ...: ~25% of Baren's figure
# pixels) lie within KEY_TOL of #263459 / #394b78, so copying them would recolour every outline with the faction colour.
CLASS_DARKS = ('#2a2220', '#3a2e2a', '#4a3a2e')


def key_check_cmd(tint, fname):
    """one-line python check of a class sheet: pixel count per exact key + near-key non-key figure pixels (target 0)."""
    keys = ','.join(f"'{c[1:]}'" for c in tint['outfit'] + tint['accent'])
    return ('python3 -c "from PIL import Image; import numpy as np; '
            f'K=[{keys}]; k=np.array([[int(h[i:i+2],16) for i in (0,2,4)] for h in K]); '
            f"a=np.asarray(Image.open('art/inbox/{fname}').convert('RGBA')).astype(int); "
            'p=a[...,:3][(a[...,3]>127)&(np.sqrt(((a[...,:3]-[255,0,255])**2).sum(-1))>=150)]; '
            'd=np.sqrt(((p[:,None,:]-k[None])**2).sum(-1)); m=d.min(1); '
            "print('exact key pixels:', {'#'+h: int((d[:,i]==0).sum()) for i,h in enumerate(K)}); "
            f"print('near-key non-key pixels (distance 1-{KEY_NEAR - 1}, target 0):', int(((m>0)&(m<{KEY_NEAR})).sum()))\"")


def keys_en(tint, roles, fname):
    """the KEY COLOURS block of a class package (tint = phase3.json item.tint)."""
    o, a = tint['outfit'], tint['accent']
    dk = CLASS_DARKS
    return ('KEY COLOURS (the most important rule of this sheet): ONE sheet is shared by every faction and company, and the game recolours '
            'the uniform at runtime by replacing these EXACT colours with the faction colours, keeping their light/dark steps.\n'
            f'  - OUTFIT keys = {roles["outfit"]}, darkest to lightest: {o[0]} (deep shadow, folds), {o[1]} (shadow), {o[2]} (base), {o[3]} (lit side)\n'
            f'  - ACCENT keys = {roles["accent"]}, darkest to lightest: {a[0]} (shadow), {a[1]} (base), {a[2]} (lit)\n'
            '  - cloth over the face (mask, scarf, veil) is OUTFIT keys, never ACCENT keys: some factions use a bright accent '
            '(yellow, lime, cream) that would turn the face into one solid block\n'
            '  - flat fills only on these areas: no dithering, gradient, noise, texture, soft blending or in-between shades; '
            'their shading uses only these steps\n'
            '  - these seven colours appear NOWHERE else (not on metal, skin, hair, leather, eyes, outline or background), and nothing else on '
            'the figure is blue, slate, teal or mint: steel is NEUTRAL grey, leather and wood are warm browns, shadows on the other parts are '
            'warm or neutral, never blue (this overrides the general "shadows toward purple/blue" style rule for this sheet)\n'
            f'  - every NON-key colour on the figure (outline, shadows, metal, leather, skin, eyes ...) must be at RGB distance '
            f'sqrt(dR^2 + dG^2 + dB^2) >= {KEY_NEAR} from all seven keys: the pipeline snaps colours within {KEY_TOL_PX} of a key ONTO the key '
            f'(so they get recoloured), and shades {KEY_TOL_PX}-{KEY_NEAR} away stay as untinted blue islands\n'
            f'  - outline and shadows: use a warm / neutral dark ramp, e.g. outline {dk[0]}, shadows {dk[1]} / {dk[2]}, and outline the uniform '
            f'with that same warm dark (never a key colour). Do NOT reuse the anchor (Baren)\'s dark violet-navy outline and shadow colours '
            '(#474269, #2c2840, #28253c, #444061 ...) on this sheet: they are within the snap distance of the outfit keys, so the game '
            'would recolour every outline and shadow with the faction colour. Match the anchor\'s outline WEIGHT and placement, not its hue\n'
            '  - anti-aliased, blended or compressed in-between shades of the keys are failures. A final palette pass that snaps every pixel '
            'of the uniform areas to its nearest key is allowed (figure only; never snap other parts or the background onto a key)\n'
            '  - after export, run this check from the repository root (in a chat, run it on your PNG if you can run Python): '
            f'{key_check_cmd(tint, fname)} - it prints the pixel count of each exact key (each key you used > 0) and the near-key '
            'non-key pixels (target 0)')


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
    fs = ['guide_strip.png', 'guide_1_idle.png', 'guide_2_windup.png', 'guide_3_strike.png', 'guide_4_hit.png']
    if 'concept.png' in C['concepts']:
        fs.append('concept.png')
    if 'concept_pixel.png' in C['concepts']:
        fs.append('concept_pixel.png')
    if has_portrait:
        fs.append('portrait.png')
    if mounted:
        fs += ['concept_mounted.png', 'guide_mounted_layout.png']
    return fs


CONCEPT_PENDING_EN = ('concept.png - NOT IN THE FOLDER YET: it is added after the owner picks a NovelAI design draft. '
                      'Do not start this sheet before concept.png is there')
CONCEPT_PENDING_KO = ('**초안 대기**: 주인이 NovelAI 초안(`jobs_{jobs}.json`)을 고르면 `art/concepts/{cid}/`에 두고 `handoff.py`의 '
                      '`{table}[\'{cid}\'][\'concepts\']`에 `{{\'concept.png\': \'{cid}/concept_NN.png\'}}`를 넣어 다시 실행한다. 그 전에는 그림 쪽에 보내지 않는다.')


def brief_en(b):
    return ('BRIEF: ' + b['silhouette'] + f'. Size: {b["size"]}. Attack: {b["attack"]}. Appears in: {b["where"]}.')


def draft_pick(C):
    """→ (art/concepts path, sample number) of concept.png, or (None, None)."""
    src = C.get('concepts', {}).get('concept.png')
    if not src:
        return None, None
    m = re.search(r'concept_(?:[a-z]_)?(\d+)\.png$', src)
    return src, int(m.group(1)) if m else None


def draft_en(C):
    """the 'take from the draft' line of the prompt (None without draft notes)."""
    if not C.get('draft'):
        return None
    _, n = draft_pick(C)
    return f'FROM concept.png (the owner\'s pick, NovelAI draft #{n}; design only) TAKE: {C["draft"]["keep"]}.'


def fixes(C, common=()):
    return list(common) + C['fix'] + ([C['head']] if C.get('head') else []) + (C['draft']['fix'] if C.get('draft') else [])


def draft_ko(C):
    """Korean owner-summary lines about the chosen draft."""
    src, n = draft_pick(C)
    if not src or not C.get('draft'):
        return []
    return [f'- **초안** `concept.png` = `art/concepts/{src}` (주인이 고른 #{n}, 디자인만) — 가져올 것: {C["ko"]["draft_keep"]}',
            f'- **초안에서 고칠 것** (영어 블록 FIX 끝부분): {C["ko"]["draft_fix"]}']


def task_en(cid, C, it):
    key = cid.split('_', 1)[1]
    kind = C.get('kind', 'captain')
    save = (f'Save it as art/inbox/{it["file"]} on the art-inbox branch (a new file there; do not rename). '
            'In a chat without repository access, return the PNG in the chat instead.')
    if kind == 'class':
        return (f'TASK: draw the battle-sprite strip of the GENERIC {C["en"].lower()} class sprite ({it["name"].split(" — ")[-1]}). This ONE sheet is shared by every '
                'nameless mercenary and faction soldier of this class, friend and foe, and the game recolours its uniform per faction '
                '(see KEY COLOURS). ' + save)
    if kind == 'monster':
        return f'TASK: draw the battle-sprite strip of a {C["en"].lower()} ({C["enemy"]}), a common monster. ' + save
    return f'TASK: draw the battle-sprite strip of {C["en"]} ({it["name"].split(" — ")[0]}, {key}), a mercenary captain. ' + save


def readme(cid, C, it, info, has_portrait, mounted_item=None, minfo=None):
    key = cid.split('_', 1)[1]
    name = it['name']
    kind = C.get('kind', 'captain')
    fr = C['frames']
    pkg = f'art/requests/phase3/{cid}'
    L = [f'# {name} — GPT handoff (`{cid}`)', '',
         '> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CHARS`를 고치고 다시 실행.',
         '> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md`.',
         f'> 모든 자료는 브랜치 `{BRANCH}`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.', '',
         '## Prompt for GPT (English)', '', '```']
    P = []
    P.append(task_en(cid, C, it))
    if C.get('brief'):
        P.append(brief_en(C['brief']))
    P.append(f'CHARACTER: {C["weapon_desc"]}; ' + '; '.join(C['keep']) + '.')
    if kind == 'class':
        P.append(keys_en(it['tint'], C['roles'], it['file']))
        P.append(f'COLOURS of everything else (keep close, muted): {colours_line(C, it)}.')
    else:
        P.append(f'COLOURS (keep close, muted): {colours_line(C, it)}.')
    if draft_en(C):
        P.append(draft_en(C))
    P.append('FIX (do not reproduce the draft here):\n' + '\n'.join(f'  - {f}' for f in fixes(C)))
    P.append('POSES (the guide mannequin fixes pose, proportions, size and position; its colours, round head, plain clothes and '
             'fist-shaped hands are placeholders - follow the text for hands and weapon details):\n'
             + '\n'.join(f'  {i + 1}. {en}: {C["pose"][p]}' for i, (p, _, _, en) in enumerate(POSES)))
    refs = [f'{f}' + {'guide_strip.png': ' (layout + poses + size: the most important reference)',
                      'guide_1_idle.png': ' .. guide_4_hit.png (the same four poses, larger)',
                      'concept.png': ' (DESIGN ONLY)',
                      'concept_pixel.png': ' (how simple the shapes must stay)',
                      'portrait.png': ' (face and hair only)'}[f]
            for f in package_files(cid, C, has_portrait) if f not in ('guide_2_windup.png', 'guide_3_strike.png', 'guide_4_hit.png')]
    if 'concept.png' not in C['concepts']:
        refs.append(CONCEPT_PENDING_EN)
    if not C.get('anchor'):
        refs.insert(0, f'{ANCHOR_FILE} on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE '
                       'ANCHOR. Match its proportions, rendering, outline, palette treatment, lighting and character scale exactly'
                       + (' - EXCEPT its dark violet-navy outline and shadow colours: on this sheet they would turn into key colours '
                          f'(use the warm dark ramp {" / ".join(CLASS_DARKS)}, see KEY COLOURS)' if kind == 'class' else ''))
    P.append(f'REFERENCES (folder {pkg}/ on branch {BRANCH}: {REPO}/tree/{BRANCH}/{pkg} ; in a chat they are the attached images):\n'
             + '\n'.join(f'  - {r}' for r in refs))
    P.append('DO NOT COPY: ' + DONT_COPY_EN + '.')
    P.append('STYLE (same for every character):\n' + '\n'.join(f'  - {s}' for s in STYLE_EN))
    P.append('DELIVERABLE:\n' + '\n'.join(f'  - {s.format(**info)}' for s in SPEC_EN))
    checks = [c.format(**info) for c in CHECK_EN]
    if kind == 'class':
        checks.insert(4, KEYS_CHECK_EN.format(near=KEY_NEAR, **C['roles']))
    P.append('SELF-CHECK before saving (redraw if any fails):\n' + '\n'.join(f'  [ ] {c}' for c in checks))
    L += ['\n\n'.join(P), '```', '']
    style_ko = f' — 승인된 바렌 그림(`art-inbox` 브랜치의 `{ANCHOR_FILE}`)의 화풍에 맞춘다.'
    order_ko = {'class': f'- 순서: 일반 병과 **{C["order"] - 10}번째** (메시지 D, 대장 9명 다음){style_ko}',
                'monster': f'- 순서: 1차 몬스터 **{C["order"] - 20}번째** (메시지 E){style_ko}'}.get(
        kind, f'- 순서: **{C["order"]}번째**' + (' — **화풍 기준(앵커)**: 이 그림을 먼저 받아 승인한 뒤 나머지 8명을 맞춘다.' if C.get('anchor') else style_ko))
    L += ['## 주인용 요약 (한국어)', '', order_ko]
    if 'concept.png' not in C['concepts']:
        L.append('- ' + CONCEPT_PENDING_KO.format(cid=cid, jobs='classes' if kind == 'class' else 'monsters', table='CHARS'))
    if kind == 'class':
        L.append(FACE_KO.format(face=C['ko']['face']))
        t = it['tint']
        L.append(f'- **열쇠 색** (전투에서 진영 색으로 바뀐다): 제복 {" ".join(f"`{c}`" for c in t["outfit"])}, '
                 f'장식 {" ".join(f"`{c}`" for c in t["accent"])} — 이 7색은 그 자리에만, 평평하게. 다른 곳에는 파랑·청회색·청록을 쓰지 않는다.')
        L.append(f'- **열쇠 색 거리**: 열쇠 색이 아닌 모든 색(외곽선·그늘 포함)은 7색 모두와 RGB 거리 {KEY_NEAR} 이상 — `sheets.py`는 거리 {KEY_TOL_PX} 안을 '
                 f'열쇠 색으로 붙인다. 바렌의 남보라 외곽선·그늘(#474269 등)은 그 안이라 쓰지 않고 따뜻한 어둠 {" / ".join(f"`{c}`" for c in CLASS_DARKS)}을 쓴다. '
                 '영어 블록 KEY COLOURS 의 확인 한 줄이 열쇠 색별 픽셀 수와 「열쇠 색 근처 픽셀」(목표 0)을 센다.')
        L.append(f'- **머리 크기**: 투구·후드·두건·모자 챙과 깃이 {HEAD_PX}px 머리를 감싼다(바깥 실루엣 약 115~125px). 머리 {HEAD_PX}px 위에 더 큰 투구를 씌워 인물을 키우지 않는다.')
    if C.get('brief'):
        b = C['brief']
        L.append(f'- 몬스터 설계: {C["enemy"]} — {b["size"]}; 공격 {b["attack"]}; 나오는 곳 {b["where"]}.')
    L += [f'- 결과 파일: `art/inbox/{it["file"]}` (id `{it["id"]}`)' + (f', 추가 선택: `art/inbox/{mounted_item["file"]}`' if mounted_item else ''),
          f'- 무기: posekit `{C["weapon"]}` 마네킹 → {C["weapon_desc"]}',
          f'- 자세(가이드 프레임): ① 대기 `{fr["idle"]}` ② 공격 준비 `{fr["windup"]}` ③ 공격 타격 `{fr["strike"]}` ④ 피격 `{fr["hit"]}`'
          + ' (`key_*` = handoff.py 의 KEY_POSES: 준비는 체중 뒤로, 타격은 내딛는 런지, 피격은 상체가 뒤로 젖혀짐)',
          f'- 초안에서 가져올 것: {C["ko"]["keep"]}',
          f'- 고칠 것: {C["ko"]["fix"]}',
          *draft_ko(C),
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
    if 'concept.png' in C['concepts']:
        L.append('| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |')
    else:
        L.append('| (`concept.png`) | **대기** — 주인이 NovelAI 초안을 고르면 들어간다 |')
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


# ───────── creatures (non-humanoid monsters): size-box guides ─────────
GUIDE_INK = (40, 36, 48)       # guide-only lines and labels
GUIDE_BOX = (88, 80, 104)
GUIDE_FILL = (150, 146, 160)
QPOS_EN = {'idle': 'top-left', 'windup': 'top-right', 'strike': 'bottom-left', 'hit': 'bottom-right'}
QPOS_KO = {'idle': '왼쪽 위', 'windup': '오른쪽 위', 'strike': '왼쪽 아래', 'hit': '오른쪽 아래'}


def creature_slots(C):
    """→ [(pose, baseline y, box (x0, y0, x1, y1), area (x0, y0, x1, y1))] in deliverable px."""
    out = []
    if C['layout'] == '2x2':
        qw, qh = SW_ // 2, SH_ // 2
        for i, (p, _, _, _) in enumerate(POSES):
            qx, qy = (i % 2) * qw, (i // 2) * qh
            w, h = C['boxes'][p]
            base, cx = qy + QBASE, qx + qw // 2
            assert w <= qw - 2 * MARGIN and h <= QBASE - MARGIN, (C['en'], p, w, h)
            out.append((p, base, (cx - w // 2, base - h, cx - w // 2 + w, base), (qx, qy, qx + qw, qy + qh)))
    else:
        slot = (SW_ - 2 * MARGIN) / 4
        for i, (p, _, _, _) in enumerate(POSES):
            w, h = C['boxes'][p]
            cx = int(round(MARGIN + slot * (i + 0.5)))
            assert w <= slot - GAP and h <= BASELINE - MARGIN, (C['en'], p, w, h)
            x0 = int(round(MARGIN + slot * i))
            out.append((p, BASELINE, (cx - w // 2, BASELINE - h, cx - w // 2 + w, BASELINE), (x0, 0, int(round(x0 + slot)), SH_)))
    return out


def _dashed(dr, x0, x1, y, col, dash=12):
    for x in range(x0, x1, 2 * dash):
        dr.line([(x, y), (min(x + dash, x1), y)], fill=col, width=2)


def layout_guide(C, slots):
    """guide_layout.png: the deliverable layout (2x2 quadrants or the 1x4 row), each pose's baseline and size box.
    Lines, boxes and labels are guide-only."""
    from PIL import ImageDraw
    img = Image.new('RGB', (SW_, SH_), MAGENTA)
    dr = ImageDraw.Draw(img)
    if C['layout'] == '2x2':
        dr.rectangle([SW_ // 2 - 1, 0, SW_ // 2, SH_], fill=GUIDE_INK)
        dr.rectangle([0, SH_ // 2 - 1, SW_, SH_ // 2], fill=GUIDE_INK)
    for i, (p, base, (x0, y0, x1, y1), (ax0, ay0, ax1, ay1)) in enumerate(slots):
        _dashed(dr, ax0 + 16, ax1 - 16, base, GUIDE_INK)
        dr.rectangle([x0, y0, x1 - 1, y1 - 1], outline=GUIDE_BOX, width=3)
        dr.text((x0 + 8, y0 + 8), f'{i + 1} {POSES[i][3]}', fill=GUIDE_INK)
        dr.text((x0 + 8, y0 + 22), f'~{x1 - x0}x{y1 - y0} px', fill=GUIDE_INK)
        dr.text((ax0 + 16, base + 8), f'baseline y={base}', fill=GUIDE_INK)
    dr.text((12, 10), 'guide only: do NOT draw lines, boxes or text', fill=GUIDE_INK)
    return img


def scale_guide(C, human_parts):
    """guide_scale.png: a grey 4-head human (the posekit idle mannequin at 110 px/head, as in every captain strip) next to
    the creature's idle size box, both on y=BASELINE: the scale reference only."""
    from PIL import ImageDraw
    rgb, m, floor = render_tight(human_parts, HEAD_PX, 2.0)
    canvas = np.empty((SH_, SW_, 3), np.uint8)
    canvas[:] = MAGENTA
    hx0, hy0 = 2 * MARGIN + 60, int(round(BASELINE - floor))
    canvas[hy0:hy0 + m.shape[0], hx0:hx0 + m.shape[1]][m] = GUIDE_FILL
    img = Image.fromarray(canvas, 'RGB')
    dr = ImageDraw.Draw(img)
    w, h = C['boxes']['idle']
    bx0 = hx0 + m.shape[1] + 120
    assert bx0 + w <= SW_ - MARGIN
    dr.rectangle([bx0, BASELINE - h, bx0 + w - 1, BASELINE - 1], outline=GUIDE_BOX, width=3)
    _dashed(dr, MARGIN, SW_ - MARGIN, BASELINE, GUIDE_INK)
    dr.text((hx0, BASELINE + 12), f'human captain, idle (4 heads, head {HEAD_PX} px, ~{m.shape[0]} px tall)', fill=GUIDE_INK)
    dr.text((bx0, BASELINE + 12), f'{C["en"].lower()}, idle: ~{w}x{h} px', fill=GUIDE_INK)
    dr.text((12, 10), 'scale reference only (same pixel scale as the captains) - not a layout, do NOT draw the human', fill=GUIDE_INK)
    return img, dict(human_px=int(m.shape[0]))


def readme_creature(cid, C, it, slots, sinfo):
    pkg = f'art/requests/phase3/{cid}'
    two = C['layout'] == '2x2'
    L = [f'# {it["name"]} — GPT handoff (`{cid}`)', '',
         '> `python3 tools/art/handoff.py`로 자동 생성된다. 고칠 때는 `tools/art/handoff.py`의 `CREATURES`를 고치고 다시 실행.',
         '> 공통 규칙: `art/requests/gpt_handoff_notes.md`. 전체 순서·붙여 넣을 메시지: `art/requests/phase3_gpt.md` (메시지 E).',
         f'> 모든 자료는 브랜치 `{BRANCH}`에서 읽고, 결과 PNG 는 `art-inbox` 브랜치에만 올린다.', '',
         '## Prompt for GPT (English)', '', '```']
    P = [task_en(cid, dict(C, kind='monster'), it), brief_en(C['brief']),
         'DESIGN: ' + '; '.join(C['design']) + '.',
         'COLOURS (keep close, muted): ' + '; '.join(f'{k} {v}' for k, v in C['colours']) + '.',
         *([draft_en(C)] if draft_en(C) else []),
         'FIX (do not reproduce the draft here):\n' + '\n'.join(f'  - {f}' for f in fixes(C, MONSTER_COMMON_FIX))]
    pos = (lambda p: f' ({QPOS_EN[p]} quadrant)') if two else (lambda p: '')
    P.append('POSES (no posekit mannequin for this creature: the text gives the pose, guide_layout.png the place and size):\n'
             + '\n'.join(f'  {i + 1}. {en}{pos(p)}: {C["pose"][p]}' for i, (p, _, _, en) in enumerate(POSES)))
    refs = [f'{ANCHOR_FILE} on the art-inbox branch (in a chat: the attached approved Baren sheet) = the APPROVED STYLE ANCHOR: match its '
            'rendering, outline, palette treatment and lighting',
            'guide_layout.png (layout, baseline and the SIZE BOX of each pose - the lines, boxes and labels are guide-only)',
            'guide_scale.png (the same pixel scale as a 4-head human captain; the grey human is NOT drawn)']
    refs.append('concept.png (DESIGN ONLY)' if 'concept.png' in C.get('concepts', {}) else CONCEPT_PENDING_EN)
    P.append(f'REFERENCES (folder {pkg}/ on branch {BRANCH}: {REPO}/tree/{BRANCH}/{pkg} ; in a chat they are the attached images):\n'
             + '\n'.join(f'  - {r}' for r in refs))
    P.append('DO NOT COPY: ' + DONT_COPY_EN + '.')
    style = [STYLE_EN[0],
             f'natural creature proportions at the SAME pixel scale as the {int(HEADS)}-head humans (head {HEAD_PX} px; see guide_scale.png); NOT chibi',
             'three-quarter view facing RIGHT (four-legged and eight-legged creatures mostly from the side with the head turned slightly toward '
             'the viewer); light from the upper left',
             *STYLE_EN[3:5],
             'readable at 1x game size (the drawing is shrunk to about 16.5%: a 300 px pose becomes ~50 px) on a dark battlefield: big clear '
             'shapes, strong silhouette, few tiny details']
    P.append('STYLE (same as every character):\n' + '\n'.join(f'  - {x}' for x in style))
    if two:
        spec = ['ONE PNG, 1536x1024 (landscape), a 2x2 grid of four equal 768x512 quadrants, one pose per quadrant: top-left idle, '
                'top-right wind-up, bottom-left strike, bottom-right hit (as guide_layout.png); never a 1x4 row or a single pose',
                f'the lowest pixel of each pose (feet, paws, talons or tail tip) on y = {QBASE} of its quadrant (y = {QBASE} in the top row, '
                f'y = {SH_ // 2 + QBASE} in the bottom row); ALL FOUR AT THE SAME SCALE: the head, body, claws and tail keep their idle size in '
                f'every pose; a bigger box only leaves room for spread wings, reaching limbs or a rearing/lunging pose - never enlarge the creature '
                f'to fill its box',
                f'at least {GAP} px of empty magenta between the creature and its quadrant\'s edges; nothing crosses into another quadrant']
    else:
        spec = ['ONE PNG, 1536x1024 (landscape), the same creature 4 times in ONE row, left to right: idle, wind-up, strike, hit, each centred '
                'on its slot of guide_layout.png; never a 2x2 grid or a single pose',
                f'the lowest pixel of every pose on y = {BASELINE}; ALL FOUR AT THE SAME SCALE: the head, body, claws and tail keep their idle size '
                f'in every pose; a bigger box only leaves room for spread wings, reaching limbs or a rearing/lunging pose - never enlarge the '
                f'creature to fill its box',
                f'at least {GAP} px of empty magenta between poses and from the border']
    spec += ['background: perfectly flat solid magenta #FF00FF everywhere (preferred; a transparent PNG is also accepted) - no gradient, floor, '
             'cast shadow or scenery', MAGENTA_EN,
             'NO text, labels, numbers, guide lines or boxes, watermark; NO effects outside the body (no trails, sparks, dust, glow, motion lines, projectiles)']
    P.append('DELIVERABLE:\n' + '\n'.join(f'  - {x}' for x in spec))
    hb = C['boxes']['idle']
    checks = [f'1536x1024, flat #FF00FF (or transparent), {"2x2 quadrants" if two else "ONE row"}: idle / wind-up / strike / hit as in guide_layout.png',
              'the lowest pixel of every pose on its baseline; each pose about its box size; the same scale as guide_scale.png',
              'the same creature, colours and proportions in all four poses; every FIX applied',
              'no text, guide lines, boxes, floor, shadow, effects or projectiles', MAGENTA_CHECK_EN,
              f'reads clearly when shrunk to game size (idle ~{round(hb[1] * 0.1654)} px tall) on a dark background']
    P.append('SELF-CHECK before saving (redraw if any fails):\n' + '\n'.join(f'  [ ] {c}' for c in checks))
    L += ['\n\n'.join(P), '```', '']
    b = C['brief']
    L += ['## 주인용 요약 (한국어)', '',
          f'- 순서: 1차 몬스터 **{C["order"] - 20}번째** (메시지 E) — 승인된 바렌 그림(`art-inbox` 브랜치의 `{ANCHOR_FILE}`)의 화풍에 맞춘다.',
          *(['- ' + CONCEPT_PENDING_KO.format(cid=cid, jobs='monsters', table='CREATURES')] if 'concept.png' not in C.get('concepts', {})
            else draft_ko(C) or ['- 초안: `concept.png` (디자인만)']),
          f'- 설계: {C["ko"]["brief"]}',
          f'- 자세: {C["ko"]["pose"]}',
          '- 배치: ' + ('1536x1024 **2x2 격자** (768x512 네 칸: ' + ', '.join(f'{QPOS_KO[p]} {ko}' for p, _, ko, _ in POSES)
                       + f'), 칸마다 맨 아래 픽셀 y={QBASE}' if two else f'1536x1024 **한 줄 4자세**, 맨 아래 픽셀 y={BASELINE}')
          + '. posekit 마네킹 없음(사람 골격이 아니다) — 자세는 글로, 자리·크기는 `guide_layout.png`의 상자로.',
          '- 크기: 대장과 같은 배율(머리 110px). 자세별 상자 ' + ', '.join(f'{ko} {C["boxes"][p][0]}x{C["boxes"][p][1]}' for p, _, ko, _ in POSES)
          + f' px. `guide_scale.png` = 같은 배율의 4등신 사람(대기 약 {sinfo["human_px"]} px) 옆에 대기 상자. 게임에서는 약 16.5% (대기 약 {round(hb[1] * 0.1654)} px 높이).',
          f'- 공격: {b["attack"]}',
          f'- 결과 파일: `art/inbox/{it["file"]}` (id `{it["id"]}`; 이름은 게임의 몬스터 이름 그대로)',
          '', '### 파일 (ChatGPT 웹이면 이 순서로 첨부)', '',
          '| 파일 | 내용 |', '|---|---|',
          f'| (`art-inbox`의 `{ANCHOR_FILE}`) | 승인된 바렌 시트 — 화풍 기준, 꼭 같이 첨부 |',
          '| `guide_layout.png` | 결과물 배치: ' + ('2x2 칸' if two else '한 줄 네 자리') + ', 바닥선, 자세별 크기 상자 (선·상자·글씨는 가이드에만) |',
          '| `guide_scale.png` | 같은 배율의 사람(회색, 그리지 않음)과 대기 상자 — 크기 비교 |',
          ('| `concept.png` | 주인이 고른 NovelAI 디자인 초안 (디자인만 참고) |' if 'concept.png' in C.get('concepts', {}) else
           '| (`concept.png`) | **대기** — 주인이 NovelAI 초안을 고르면 들어간다 |'),
          '', '### 받은 뒤 (Claude Code)', '', '```',
          f'python3 tools/art/sheets.py art/inbox/{it["file"]} --dry-run --work /tmp/sheets   # 미리보기 (요청서의 scale·cell·layout 을 쓴다)',
          f'python3 tools/art/sheets.py art/inbox/{it["file"]}                                 # 등록',
          '```', '']
    return '\n'.join(L)


# ───────── main ─────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('ids', nargs='*', help='package ids (default: all of CHARS and CREATURES)')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--check', action='store_true', help='print the strip layout of every package')
    a = ap.parse_args()
    with open(REQ, encoding='utf-8') as f:
        items = {it['file']: it for it in json.load(f)['items']}
    every = {**CHARS, **CREATURES}
    ids = a.ids or sorted(every, key=lambda k: every[k]['order'])
    cache = {}
    for cid in ids:
        if cid not in every:
            sys.exit(f'unknown id {cid} (have {", ".join(every)})')
        C = every[cid]
        it = items.get(f'sheet_{cid}.png')
        if not it:
            sys.exit(f'sheet_{cid}.png is not in {os.path.relpath(REQ, ROOT)} — run node tools/art/requests.js')
        if C.get('enemy') and it['id'] != f'sheet/monster/{C["enemy"]}':
            sys.exit(f'{cid}: phase3.json id {it["id"]} != sheet/monster/{C["enemy"]}')
        if C.get('kind') == 'class' and not it.get('tint'):
            sys.exit(f'{cid}: phase3.json item has no tint (key colours) — run node tools/art/requests.js')
        d = os.path.join(a.out, cid)
        os.makedirs(d, exist_ok=True)
        for dst, src in C.get('concepts', {}).items():
            shutil.copyfile(os.path.join(CONCEPTS, src), os.path.join(d, dst))
        if cid in CREATURES:
            if 'sword_shield' not in cache:
                cache['sword_shield'] = builds_for('sword_shield')
            slots = creature_slots(C)
            save_png(layout_guide(C, slots), os.path.join(d, 'guide_layout.png'))
            simg, sinfo = scale_guide(C, cache['sword_shield'][2]['idle_0'][1])
            save_png(simg, os.path.join(d, 'guide_scale.png'))
            with open(os.path.join(d, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(readme_creature(cid, C, it, slots, sinfo))
            size = sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d))
            print(f'{cid}: creature {C["layout"]}  boxes ' + ' '.join(f'{p}{C["boxes"][p][0]}x{C["boxes"][p][1]}' for p, _, _, _ in POSES)
                  + f', human idle {sinfo["human_px"]} px, {size // 1024} KB')
            if a.check:
                print('   slots', [(p, base, box) for p, base, box, _ in slots])
            continue
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
