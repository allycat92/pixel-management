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
  python3 tools/art/portrait_pkgs.py captain SPEC bard --out /tmp/pk                     # write elsewhere (dry run of a change)

Spec file: a JSON list of entries
  {key, en, weapon (bow|staff|none|katana|sword_shield|spear), size_class, hit_weight (heavy|mid|light, default mid),
   character, colours, notes: [...], explain (why a note seals away a portrait weapon / prop, and which owner decision),
   poses: [4 strings, "1 idle: ..." or "idle: ..."], ko_notes}
Lint (the package is NOT written): a pose, note, character or colours text with knee-up hit wording
(handoff.BANNED_POSE_RE: "thrown back", "rear leg", "knee up", "kicked up", "lifts the front knee", "leg up" ...),
a hit pose without the reaction wording of handoff.hit_pose() (both feet flat on the ground + a face change), or a
note that seals a portrait weapon ("stays sheathed", "holstered", "never two", "on her back" ...; handoff.SEAL_RE)
without `explain`.
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


def lint(S):
    """→ problems of one spec entry (see the module doc)."""
    key = S['key']
    poses = list(zip(['idle', 'wind-up', 'strike', 'hit'], [pose_text(p) for p in S['poses']]))
    out = h.lint_request(key, poses, S['notes'], S.get('explain', ''))     # banned wording: poses AND notes
    for fld in ('character', 'colours'):                                     # the other English text that reaches GPT
        for m in h.BANNED_POSE_RE.finditer(S.get(fld) or ''):
            out.append(f'{key}: {fld} contains banned phrase "{m.group(0)}" (knee-up wording)')
    w = S.get('hit_weight', 'mid')
    if w not in h.HIT_WEIGHTS:
        out.append(f'{key}: hit_weight {w!r} is not one of {", ".join(h.HIT_WEIGHTS)}')
    hit = poses[3][1]
    if 'flat on the ground' not in hit or not re.search(r'wince|teeth gritted|eyes squeezed|jaw drops|ducks', hit):
        out.append(f'{key}: the hit pose is not the reaction wording (both feet flat on the ground + face change; build it with '
                   'handoff.hit_pose(weight, detail))')
    return out


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
    # 게임 칸 예산: 칸 96 → 자세 높이 90 게임 px = 원본 544px. 든 무기가 이보다 높으면 등록할 때 줄이거나 칸을 키워야 한다 (아멜리 사례).
    cell = it.get('cell') or 96     # 칸은 요청서(phase3.json ← requests.js CELL_112) 한 곳에서만 정한다
    tall = int((cell - 6) / 0.1654) - 14
    top_y = 870 - tall
    wc = S.get('weapon_confirmed')
    if wc and wc.get('by') == 'pending':
        raise SystemExit(f"{S['key']}: weapon_confirmed is pending - ask the owner before generating the package")
    weapon_line = ''
    if wc:
        over = f" This overrides {' and '.join(wc['overrides'])}." if wc.get('overrides') else ''
        weapon_line = (f"\nWEAPON (CONFIRMED by {wc.get('by', 'owner')} {wc.get('date', '')}): {wc['what']}.{over} "
                       "If you think it is wrong, write it under PROPOSALS in NOTES - do not draw another weapon.")
    for bad in ('to confirm', '확인 필요', '확인 권장'):
        if any(bad in n for n in S['notes']):
            raise SystemExit(f"{S['key']}: a note still says '{bad}' - an open question must not go into the prompt (use weapon_confirmed)")
    size_ko = ''
    explain_ko = f"\n- 초상화 무기·소품을 빼는 근거(explain): {S['explain']}" if S.get('explain') else ''
    if S.get('size_class', 'normal') != 'normal':
        size_ko = f"\n- 체격 등급: `{S['size_class']}` — 4등신·머리 110px 유지, 덩치(어깨·팔)로만 크게. 시트 칸이 더 커야 할 수 있음."
    return f"""# {it['name']} · `{it['id']}`

도트 납품 대기열(`art/requests/dot_queue.md`) 항목. 규칙은 `art/requests/gpt_handoff_notes.md`가 우선이다.

| 파일 | 내용 |
|---|---|
| `guide_strip.png` | **결과물과 같은 배치** — 1536x1024, #FF00FF, 4자세 한 줄, 머리 110px, 발바닥 y=870 (가장 중요) |
| `guide_1_idle.png` … `guide_4_hit.png` | 같은 자세를 크게 (posekit 4등신 마네킹, 무기 `{w}`) |
| `portrait_800.jpg` | 승인된 초상화(긴 변 800px, 가벼운 사본 — **이것을 불러온다**) — 얼굴·머리·옷의 **디자인** 기준 |
| `portrait.png` | 같은 초상화의 원본(약 1MB, 불러오지 못해도 된다) |

- 납품 파일: art-inbox 브랜치 `art/inbox/{fname}` + `art/inbox/NOTES.md`의 「{it['id']} - {ko}」 절.
- 화풍 기준(앵커): art-inbox 의 `art/inbox/sheet_captain_blademaster.png`.
- 요점: {S.get('ko_notes', '').strip()}{size_ko}{shrink_ko}
- 피격 무게: `{S.get('hit_weight', 'mid')}` — {h.HIT_KO[S.get('hit_weight', 'mid')]}. 가이드 피격 = K2-mid 반응(두 발 바닥, 무릎으로 받음).{explain_ko}
- 게임 칸: {cell}px — 어떤 자세도(든 무기·모자 포함) y={top_y} 위로 올라가지 않게 (자세 높이 {tall}px 이하).
- 생성: `python3 {MARK} {kind} {spec_rel} {S['key']}` (고칠 때는 spec JSON 을 고치고 다시 실행).

## Prompt for GPT

```
TASK: draw the battle sprite strip of {name}, {ROLE[kind]}, as ONE new PNG:
art/inbox/{fname} on the art-inbox branch.{weapon_line}

CHARACTER: {sentence(S['character'])}{cls} Colours: {S['colours'].strip()}.
Take the face, hair and outfit design from portrait_800.jpg (design only; not its painting style). If it does not load, do NOT draw from the text - report it under BLOCKED in NOTES.
NOTES: {notes}.

POSES (match guide_strip.png exactly — pose, limb lengths, proportions, position and size; the mannequin weapon is a placeholder for the real weapon):
1 idle: {P[0]}.
2 wind-up: {P[1]}.
3 strike: {P[2]}.
4 hit: {P[3]}.

FORMAT: 1536x1024 PNG, the same character four times in ONE row (1x4), facing RIGHT, front three-quarter view, light from the upper left.
4 heads tall, head = 110 px; the crouched idle is about 400 px from top of head to sole (hair, headgear and weapon not counted).
The lowest pixel (soles) of all four poses on y = 870. At least 32 px of magenta between poses (any direction) and from the border.{shrink_en}
CELL BUDGET (game cell {cell}): no pixel of any pose - weapon tip, hat, plume included - above y = {top_y} (pose height <= {tall} px). A raised weapon that would cross that line is tilted back or held lower, never shrunk.
STYLE: match the approved anchor art/inbox/sheet_captain_blademaster.png (art-inbox): rendering, outline, palette treatment, lighting, scale.
Crisp pixel art: about 40 colours, hard pixel edges, no anti-aliased blending into the background.
BACKGROUND: perfectly flat #FF00FF. No floor, shadow, text, frames, effects (no glow, trails, sparks, projectiles).
MAGENTA RULE: every figure colour must be at RGB distance >= 170 from #FF00FF (hard minimum 150); never merge figure colours with the background when reducing the palette.
WEAPON/PROP READABILITY: in every pose keep the weapon outside the body silhouette, over the background, with a 1px dark outline.

SELF-CHECK before saving: 4 poses in one row · soles on y=870 · highest pixel at or below y={top_y} · head ≈110 px · facing right · weapon matches NOTES and sits outside the body in every pose · no effects ·
flat #FF00FF background · no figure colour within distance 170 of #FF00FF · ~40 colours with hard edges.
{h.HIT_CHECK_EN}.
Run `python3 tools/art/check_delivery.py art/inbox/{fname}` if you can and paste its RESULT line.

DELIVERY: commit art/inbox/{fname} and add a section "## {it['id']} - {ko}" to art/inbox/NOTES.md using the template in art/requests/GPT_STANDING.md
(CHECK / REFERENCES LOADED / DEVIATIONS / RISKS AT GAME SIZE / PROPOSALS). Push to art-inbox only. Do not touch files outside art/inbox/. Then stop.
```
"""


def build(kind, S, items, cache, spec_rel, root_out=OUT):
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
    bad = lint(S)
    if bad:
        raise SystemExit('request lint FAILED (no package written):\n  ' + '\n  '.join(bad))
    out = os.path.join(root_out, f'{kind}_{key}')
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
        _, F, cache[w] = h.builds_for(w)
        cache[w + ':F'] = (F, cache[w])
    builds = cache[w]
    hp = h.hit_problems(h.hit_metrics(*cache[w + ':F'], FRAMES[w][3]), 'mid')
    if hp:
        raise SystemExit(f'{key}: hit guide {FRAMES[w][3]} is not a believable reaction: ' + '; '.join(hp))
    for f, n in zip(FRAMES[w], GUIDES):
        h.save_png(h.guide_frame(builds, f), os.path.join(out, n))
    im, info = h.strip_image(builds, FRAMES[w])
    h.save_png(im, os.path.join(out, 'guide_strip.png'))
    shutil.copyfile(portrait, os.path.join(out, 'portrait.png'))
    # 가벼운 사본: 그림 쪽이 1MB 안팎의 PNG 를 불러오지 못한 일이 있었다 (거대 거미 시안)
    from PIL import Image
    pim = Image.open(portrait).convert('RGB')
    k = 800 / max(pim.size)
    if k < 1:
        pim = pim.resize((round(pim.width * k), round(pim.height * k)), Image.LANCZOS)
    pim.save(os.path.join(out, 'portrait_800.jpg'), quality=88)
    with open(rd, 'w', encoding='utf-8') as fh:
        fh.write(readme(kind, it, S, info, spec_rel))
    return dict(key=key, weapon=w, px_per_head=info['px_per_head'], shrink=info['shrink'], out=os.path.relpath(out, ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('kind', choices=['captain', 'hero'])
    ap.add_argument('spec', help='JSON spec file (list of entries)')
    ap.add_argument('keys', nargs='*', help='only these keys')
    ap.add_argument('--out', default=OUT, help='package root (default art/requests/phase3)')
    ap.add_argument('--lint', action='store_true', help='only lint every (selected) entry and print the problems; write nothing')
    a = ap.parse_args()
    items = {i['id']: i for i in json.load(open(REQ, encoding='utf-8'))['items']}
    specs = json.load(open(a.spec, encoding='utf-8'))
    spec_rel = os.path.relpath(os.path.abspath(a.spec), ROOT).replace(os.sep, '/')
    cache = {}
    done = []
    if a.lint:
        bad = [m for S in specs if not a.keys or S['key'] in a.keys for m in lint(S)]
        print('\n'.join(bad) or 'lint: OK')
        print(f'{len(bad)} problem(s)')
        return 1 if bad else 0
    for S in specs:
        if a.keys and S['key'] not in a.keys:
            continue
        r = build(a.kind, S, items, cache, spec_rel, a.out)
        if r:
            done.append(r)
            flag = f"  SHRUNK x{r['shrink']}" if r['shrink'] < 1 else ''
            print(f"{r['out']}: {r['weapon']} {r['px_per_head']} px/head{flag}")
    print(f'{len(done)} package(s)')


if __name__ == '__main__':
    sys.exit(main())
