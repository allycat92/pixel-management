#!/usr/bin/env python3
"""NovelAI 이미지 생성 (사용자가 요청했을 때만 쓴다). **디자인 초안 전용** — 게임 그림이 되는 길은 없다.

주인 결정: NovelAI 로는 최종본을 만들지 않는다. 게임에 들어가는 그림은 언제나 GPT 를 거친다
(art/requests/gpt_handoff_notes.md). 그래서 이 도구는:
  - 기본으로 art/concepts/<id>/drafts/nai_<id>_s<seed>.png 에 쓴다 (<id> = 요청서 파일 이름에서 sheet_ 와 .png 를 뺀 것,
    예: sheet/class/warrior → art/concepts/class_warrior/drafts/nai_class_warrior_s21149.png). drafts/ 는 git 에 올리지 않는다.
  - art/inbox/, assets/, art/requests/ 아래에는 어떤 옵션으로도 쓰지 않는다 (sheet_*.png 이름도 만들지 않는다).
  - 결과 PNG 에는 NovelAI 메타데이터(Software: NovelAI)가 남는다. tools/art/sheets.py 는 이것을 보고 거부한다.
주인이 고른 초안만 art/concepts/<id>/concept_NN.png 로 옮기고(selections.json), handoff.py 꾸러미의 concept.png(디자인 참고)가 된다.

  # 요청서(art/requests/phase3.json)의 nai 프롬프트·시드·크기로 (--seed/--width/--height 를 주면 그것이 우선)
  python3 tools/art/novelai.py --only sheet/class/warrior
  # 직접 만든 프롬프트 파일로 ({"prompt", "negative", "out", "seed"?} 하나 또는 목록; out 은 이름만 쓴다)
  python3 tools/art/novelai.py --prompt-file my_prompt.json --outdir /tmp/nai
  # 보내지 않고 파라미터만 확인
  python3 tools/art/novelai.py --only sheet/class/warrior --dry-run

무료 범위(Opus 구독의 무료 생성)를 기본으로 지킨다: 넓이 <= 1024x1024 픽셀, steps <= 28, 1장씩.
넘는 설정은 --allow-paid 없이는 거부한다. 한 번에 만드는 장 수는 --max (기본 2) 로 막는다.

토큰: 클라우드 세션에서는 프록시가 image.novelai.net 요청에 넣어 준다 (Bearer proxy-injected).
로컬에서는 환경 변수 NOVELAI_TOKEN 을 쓴다. 토큰을 파일이나 로그에 남기지 않는다.
필요: 파이썬 표준 라이브러리만.
"""
import argparse
import io
import json
import os
import random
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CONCEPTS = os.path.join(ROOT, 'art', 'concepts')
# NovelAI 초안이 게임 그림 경로로 들어가지 않게 막는 폴더 (art/inbox = sheets.py·process.py 입력, assets = 게임 그림)
FORBIDDEN = [os.path.join(ROOT, *p) for p in (('art', 'inbox'), ('assets',), ('art', 'requests'))]
REQS = os.path.join(ROOT, 'art', 'requests', 'phase3.json')
URL = 'https://image.novelai.net/ai/generate-image'
FREE_AREA = 1024 * 1024
FREE_STEPS = 28
DEFAULTS = {'model': 'nai-diffusion-4-5-full', 'width': 832, 'height': 1216, 'steps': 28, 'scale': 5.5,
            'sampler': 'k_euler_ancestral'}


def body(prompt, neg, p, seed):
    return {'input': prompt, 'model': p['model'], 'action': 'generate', 'parameters': {
        'params_version': 3, 'width': p['width'], 'height': p['height'], 'scale': p['scale'],
        'sampler': p['sampler'], 'steps': p['steps'], 'n_samples': 1, 'ucPreset': 0, 'qualityToggle': True,
        'seed': seed, 'sm': False, 'sm_dyn': False, 'dynamic_thresholding': False, 'controlnet_strength': 1,
        'legacy': False, 'add_original_image': True, 'cfg_rescale': 0, 'noise_schedule': 'karras',
        'legacy_v3_extend': False, 'skip_cfg_above_sigma': None, 'use_coords': False, 'characterPrompts': [],
        'v4_prompt': {'caption': {'base_caption': prompt, 'char_captions': []}, 'use_coords': False, 'use_order': True},
        'v4_negative_prompt': {'caption': {'base_caption': neg, 'char_captions': []}, 'legacy_uc': False},
        'negative_prompt': neg, 'deliberate_euler_ancestral_bug': False, 'prefer_brownian': True}}


def generate(payload):
    token = os.environ.get('NOVELAI_TOKEN', 'proxy-injected')
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers={
        'Content-Type': 'application/json', 'Authorization': f'Bearer {token}',
        # Cloudflare 가 기본 Python-urllib User-Agent 를 막는다 (error 1010)
        'User-Agent': 'pixel-guild-art/1.0'})
    try:
        data = urllib.request.urlopen(req, timeout=240).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code}: {e.read()[:300]!r}')
    z = zipfile.ZipFile(io.BytesIO(data))
    return z.read(z.namelist()[0])


def draft_stem(out):
    """요청서 파일 이름 → 초안 id: sheet_class_warrior.png → class_warrior (경로는 버린다)."""
    stem = os.path.splitext(os.path.basename(out))[0].split('@')[0]
    stem = stem[len('sheet_'):] if stem.startswith('sheet_') else stem
    stem = stem[len('nai_'):] if stem.startswith('nai_') else stem
    return stem or 'draft'


def draft_path(outdir, out, seed):
    """초안 저장 경로. 기본은 art/concepts/<id>/drafts/. 게임 그림 폴더(art/inbox, assets, art/requests)는 거부."""
    stem = draft_stem(out)
    d = os.path.realpath(outdir or os.path.join(CONCEPTS, stem, 'drafts'))
    for f in FORBIDDEN:
        f = os.path.realpath(f)
        if d == f or d.startswith(f + os.sep):
            raise SystemExit(f'{os.path.relpath(d, ROOT)} 에는 쓰지 않는다: NovelAI 는 디자인 초안 전용이다 '
                             '(게임 그림은 GPT 를 거친다; 기본 art/concepts/<id>/drafts/ 또는 작업 폴더를 --outdir 로)')
    return os.path.join(d, f'nai_{stem}_s{seed}.png')


def jobs_from_args(a):
    jobs = []
    if a.prompt_file:
        with open(a.prompt_file, encoding='utf-8') as f:
            d = json.load(f)
        for j in d if isinstance(d, list) else [d]:
            out = j.get('out') or j.get('file')
            if not out:
                raise SystemExit('prompt-file 항목에 out 이 없다')
            jobs.append({'label': out, 'prompt': j['prompt'], 'negative': j.get('negative') or j.get('neg', ''),
                         'out': out, 'seed': j.get('seed'), 'size': j.get('size')})
    if a.only:
        with open(a.requests, encoding='utf-8') as f:
            items = {it['id']: it for it in json.load(f)['items']}
        for sid in a.only.split(','):
            it = items.get(sid.strip())
            if not it:
                raise SystemExit(f'요청서에 {sid} 가 없다')
            if 'nai' not in it:
                raise SystemExit(f'{sid} 에 nai 프롬프트가 없다')
            jobs.append({'label': sid, 'prompt': it['nai']['prompt'], 'negative': it['nai']['negative'],
                         'out': it['file'], 'seed': it['nai'].get('seed'), 'size': it['nai'].get('size')})
    return jobs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--only', help='요청서 id (쉼표로 여럿): sheet/captain/ironwall,...')
    ap.add_argument('--requests', default=REQS, help='요청서 json (기본 art/requests/phase3.json)')
    ap.add_argument('--prompt-file', help='{"prompt","negative","out","seed"} 하나 또는 목록인 json')
    ap.add_argument('--seed', type=int, help='시드 (기본: 무작위, 출력에 찍힌다)')
    ap.add_argument('--width', type=int, help=f'기본: 요청서의 nai.size, 없으면 {DEFAULTS["width"]}')
    ap.add_argument('--height', type=int, help=f'기본: 요청서의 nai.size, 없으면 {DEFAULTS["height"]}')
    ap.add_argument('--steps', type=int, default=DEFAULTS['steps'])
    ap.add_argument('--scale', type=float, default=DEFAULTS['scale'], help='프롬프트 강도 (CFG)')
    ap.add_argument('--model', default=DEFAULTS['model'])
    ap.add_argument('--sampler', default=DEFAULTS['sampler'])
    ap.add_argument('--max', type=int, default=2, help='이번 실행에서 만들 최대 장 수 (기본 2, 대량 생성 방지)')
    ap.add_argument('--allow-paid', action='store_true', help='무료 범위를 넘는 설정 허용 (Anlas 소모)')
    ap.add_argument('--force', action='store_true', help='같은 이름(같은 id·시드)의 초안을 덮어쓴다')
    ap.add_argument('--outdir', help='저장 폴더 (기본 art/concepts/<id>/drafts/; art/inbox·assets·art/requests 는 거부)')
    ap.add_argument('--dry-run', action='store_true', help='보내지 않고 파라미터만 출력')
    a = ap.parse_args()

    def params(j):
        """this job's parameters: --width/--height > the request's nai.size > DEFAULTS."""
        p = {k: getattr(a, k) for k in DEFAULTS}
        size = j.get('size') or (DEFAULTS['width'], DEFAULTS['height'])
        p['width'] = a.width if a.width is not None else int(size[0])
        p['height'] = a.height if a.height is not None else int(size[1])
        if p['width'] % 64 or p['height'] % 64:
            raise SystemExit('width/height 는 64 의 배수여야 한다')
        paid = []
        if p['width'] * p['height'] > FREE_AREA:
            paid.append(f'넓이 {p["width"]}x{p["height"]} > 1024x1024')
        if p['steps'] > FREE_STEPS:
            paid.append(f'steps {p["steps"]} > {FREE_STEPS}')
        if paid and not a.allow_paid:
            raise SystemExit(f'[{j["label"]}] 무료 범위를 넘는다: ' + ', '.join(paid) + ' (정말 쓰려면 --allow-paid)')
        return p, paid

    jobs = jobs_from_args(a)
    if not jobs:
        raise SystemExit('--only 또는 --prompt-file 이 필요하다')
    if len(jobs) > a.max:
        raise SystemExit(f'{len(jobs)}장 요청 > --max {a.max} (대량 생성은 사용자가 원할 때만, --max 로 늘린다)')
    plans = [params(j) for j in jobs]   # 보내기 전에 전부 검사
    seeds = [a.seed if a.seed is not None else (j['seed'] if j['seed'] is not None else random.randrange(1, 2 ** 32 - 1))
             for j in jobs]
    outs = [draft_path(a.outdir, j['out'], seed) for j, seed in zip(jobs, seeds)]   # 금지 폴더도 보내기 전에 검사

    for j, (p, paid), seed, out in zip(jobs, plans, seeds, outs):
        if os.path.exists(out) and not a.force:
            print(f'[{j["label"]}] {out} 가 이미 있다 — 건너뜀 (--force 로 덮어쓰기)')
            continue
        print(f'[{j["label"]}] model={p["model"]} size={p["width"]}x{p["height"]} steps={p["steps"]} '
              f'scale={p["scale"]} sampler={p["sampler"]} n_samples=1 seed={seed}'
              f'{"  (PAID)" if paid else "  (free tier)"}')
        print(f'  prompt: {j["prompt"]}')
        print(f'  negative: {j["negative"]}')
        print(f'  -> {os.path.relpath(out, ROOT) if out.startswith(ROOT + os.sep) else out}')
        if a.dry_run:
            continue
        png = generate(body(j['prompt'], j['negative'], p, seed))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'wb') as f:
            f.write(png)
        print(f'  saved {len(png)} bytes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
