#!/usr/bin/env python3
"""Dot-queue packages from a JSON spec → art/requests/phase3/<kind>_<key>/

For characters whose DESIGN comes from an approved portrait (no NovelAI concept): captains after the
starter nine, and special mercenaries (heroes). Each package has the same layout as the hero packages:

  guide_1_idle.png .. guide_4_hit.png   the four key poses, large (posekit 4-head mannequin, tools/art/handoff.py)
  guide_strip.png                       the deliverable layout: 1536x1024, #FF00FF, 1x4, head 110 px, soles on y=870
  portrait.png                          byte copy of art/inbox/<kind>_<key>.png (the approved portrait)
  README.md                             Korean header + the English "Prompt for GPT" block

  python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json            # every entry
  python3 tools/art/portrait_pkgs.py captain tools/art/specs/captains_batch2.json bard titan # only these keys

Spec file: a JSON list of entries
  {key, en, weapon (bow|staff|none|katana|sword_shield|spear), size_class, character, colours,
   notes: [...], poses: [4 strings, "1 idle: ..." or "idle: ..."], ko_notes}
Names and the delivery file name come from art/requests/phase3.json (sheet/<kind>/<key>).

Safety: a package folder that already exists and was NOT written by this script (e.g. the nine starter
captains from handoff.py, or the hand-made hero packages) is never touched; the key is skipped with an error.
Deterministic: same inputs → byte-identical files.
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'pixelart'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'art'))
_spec = importlib.util.spec_from_file_location('handoff', os.path.join(ROOT, 'tools', 'art', 'handoff.py'))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

REQ = os.path.join(ROOT, 'art', 'requests', 'phase3.json')
OUT = os.path.join(ROOT, 'art', 'requests', 'phase3')
INBOX = os.path.join(ROOT, 'art', 'inbox')
MARK = 'tools/art/portrait_pkgs.py'   # written into every README; folders without it are not ours

FRAMES = {
    'bow': ['idle_0', 'attack_2', 'attack_3', 'key_hit'],
    'staff': ['idle_0', 'cast_1', 'key_strike', 'key_hit'],
    'none': ['key_idle', 'key_windup', 'key_strike', 'key_hit'],
    'katana': ['idle_0', 'key_windup', 'key_strike', 'key_hit'],
    'sword_shield': ['idle_0', 'key_windup', 'key_strike', 'key_hit'],
    'spear': ['idle_0', 'key_windup', 'key_strike', 'key_hit'],
}
GUIDES = ['guide_1_idle.png', 'guide_2_windup.png', 'guide_3_strike.png', 'guide_4_hit.png']
POSE_LABELS = ['idle', 'wind-up', 'strike', 'hit']
ROLE = {'captain': 'a mercenary captain of the guild', 'hero': 'a special mercenary of the guild'}
KO_ROLE = {'captain': '대장', 'hero': '특별 용병'}


def pose_text(s):
    """'1 idle: x.' / 'idle: x' / 'x' → 'x' (number and pose label stripped, no trailing period)."""
    s = s.strip()
    s = re.sub(r'^\d+\s*', '', s)
    s = re.sub(r'^(idle|wind-up|windup|strike|hit)\s*:\s*', '', s, flags=re.I)
    return s.rstrip(' .')


def display_name(en, ko):
    """'Narin (나린) — Wind-Chasing Hunter (...)' → 'Narin (나린)'; 'Otto' + '오토' → 'Otto (오토)'."""
    latin = re.split(r'\s*[(—]', en, maxsplit=1)[0].strip()
    return f'{latin} ({ko})' if ko and ko != latin else latin


def sentence(s):
    s = s.strip()
    return s if s.endswith(('.', '!', '?')) else s + '.'


def readme(kind, it, S, info, spec_rel):
    w = S['weapon']
    fname = it['file']
    ko = it['name'].split(' — ')[0]
    name = display_name(S['en'], ko)
    m = re.search(r'Class: ([^.]*)\.', it.get('prompt', ''))
    cls = f" Class: {m.group(1)}." if m else ''
    notes = ' / '.join(n.strip().rstrip('.') for n in S['notes'])
    P = [pose_text(p) for p in S['poses']]
    shrink_ko = ''
    shrink_en = ''
    if info['shrink'] < 1:
        shrink_ko = (f"\n- **주의**: 네 자세가 머리 110px 로는 한 줄에 들어가지 않아 `guide_strip.png` 은 머리 {info['px_per_head']}px 로 "
                     f"축소됨(×{info['shrink']}). 결과물은 그래도 머리 110px 기준을 따른다.")
        shrink_en = (f"\nNOTE: guide_strip.png is drawn at {info['px_per_head']} px/head (the four guide poses did not fit at 110); "
                     "keep head = 110 px anyway and use the spare magenta.")
    size_ko = ''
    if S.get('size_class', 'normal') != 'normal':
        size_ko = f"\n- 체격 등급: `{S['size_class']}` — 4등신·머리 110px 유지, 덩치(어깨·팔)로만 크게. 시트 칸이 더 커야 할 수 있음."
    return f"""# {it['name']} · `{it['id']}`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `{w}`) |
| `portrait.png` | 승인된 초상화 — 얼굴·머리·옷의 **디자인** 기준 (NovelAI 초안 없음) |

- 납품 파일: art-inbox 브랜치 `art/inbox/{fname}` + `art/inbox/NOTES.md`의 「3단계 — {ko}」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: {S.get('ko_notes', '').strip()}{size_ko}{shrink_ko}
- 생성: `python3 {MARK} {kind} {spec_rel} {S['key']}` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of {name}, {ROLE[kind]}, as ONE new PNG:
art/inbox/{fname} on the art-inbox branch.

CHARACTER: {sentence(S['character'])}{cls} Colours: {S['colours'].strip()}.
Take the face, hair and outfit design from portrait.png (design only; not its painting style).
NOTES: {notes}.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: {P[0]}.
2 wind-up: {P[1]}.
3 strike: {P[2]}.
4 hit: {P[3]}.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.{shrink_en}
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.
WEAPON/PROP READABILITY: in every pose keep the weapon outside the body silhouette, over the background, with a 1px dark outline.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · head ≈110 px · facing right · weapon matches NOTES and sits outside the body in every pose · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.

DELIVERY: commit art/inbox/{fname} and add a section "3단계 — {ko}" to art/inbox/NOTES.md
(what you made, where you deviated from the guide, what you would redraw). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
"""


def build(kind, S, items, cache, spec_rel):
    key = S['key']
    iid = f'sheet/{kind}/{key}'
    if iid not in items:
        raise SystemExit(f'{iid}: not in art/requests/phase3.json (run node tools/art/requests.js)')
    it = items[iid]
    w = S['weapon']
    if w not in FRAMES:
        raise SystemExit(f'{key}: unknown weapon {w!r}')
    if len(S['poses']) != 4:
        raise SystemExit(f'{key}: needs exactly 4 poses')
    out = os.path.join(OUT, f'{kind}_{key}')
    rd = os.path.join(out, 'README.md')
    if os.path.isdir(out) and os.listdir(out):
        if not (os.path.exists(rd) and MARK in open(rd, encoding='utf-8').read()):
            print(f'  SKIP {kind}_{key}: folder exists and was not made by {MARK} (not overwritten)', file=sys.stderr)
            return None
    portrait = os.path.join(INBOX, f'{kind}_{key}.png')
    if not os.path.exists(portrait):
        raise SystemExit(f'{key}: missing portrait {portrait}')
    os.makedirs(out, exist_ok=True)
    if w not in cache:
        cache[w] = h.builds_for(w)[2]
    builds = cache[w]
    for f, n in zip(FRAMES[w], GUIDES):
        h.save_png(h.guide_frame(builds, f), os.path.join(out, n))
    im, info = h.strip_image(builds, FRAMES[w])
    h.save_png(im, os.path.join(out, 'guide_strip.png'))
    shutil.copyfile(portrait, os.path.join(out, 'portrait.png'))
    with open(rd, 'w', encoding='utf-8') as fh:
        fh.write(readme(kind, it, S, info, spec_rel))
    return dict(key=key, weapon=w, px_per_head=info['px_per_head'], shrink=info['shrink'], out=os.path.relpath(out, ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('kind', choices=['captain', 'hero'])
    ap.add_argument('spec', help='JSON spec file (list of entries)')
    ap.add_argument('keys', nargs='*', help='only these keys')
    a = ap.parse_args()
    items = {i['id']: i for i in json.load(open(REQ, encoding='utf-8'))['items']}
    specs = json.load(open(a.spec, encoding='utf-8'))
    spec_rel = os.path.relpath(os.path.abspath(a.spec), ROOT).replace(os.sep, '/')
    cache = {}
    done = []
    for S in specs:
        if a.keys and S['key'] not in a.keys:
            continue
        r = build(a.kind, S, items, cache, spec_rel)
        if r:
            done.append(r)
            flag = f"  SHRUNK x{r['shrink']}" if r['shrink'] < 1 else ''
            print(f"{r['out']}: {r['weapon']} {r['px_per_head']} px/head{flag}")
    print(f'{len(done)} package(s)')


if __name__ == '__main__':
    main()
