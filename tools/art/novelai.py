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

참고 그림 (프롬프트 파일에서만, 선택; 없으면 예전과 똑같이 글만으로 만든다):
  "char_ref": "그림.png" 또는 {"image", "type": "character"|"character&style"|"style", "strength": 0~1, "fidelity": 0~1}
      → Precise Reference(예전 이름 Character Reference, v4.5 전용; 한 장만). 1024x1536 / 1536x1024 / 1472x1472 중
        비율이 가장 가까운 칸에 비율을 지켜 줄이고 검은 여백을 붙여 보낸다. 장당 Anlas 가 더 든다.
  "vibe": "그림.png" 또는 목록 (항목은 경로 또는 {"image", "info": 0~1, "strength": 0~1})
      → Vibe Transfer. v4 이상은 먼저 /ai/encode-vibe 로 바꾼 값을 보낸다 (그림마다 Anlas 조금). char_ref 와 같이 못 쓴다.
  "init_image": "그림.png", "strength": 0~1 (기본 0.7), "noise": 0~1 (기본 0), "init_fit": "pad"|"cover"|"stretch"
      → img2img. 결과 크기(width x height)에 맞춘다 (pad = 비율 유지 + init_pad 색 여백, 기본 #000000).
  투명한 곳은 여백 색으로 채운다. 참고 그림 모드는 Pillow 가 필요하다 (글만 쓰는 기본 모드는 표준 라이브러리만).
  --dry-run 은 어떤 참고 모드인지만 찍고 그림 바이트는 찍지 않는다.

무료 범위(Opus 구독의 무료 생성)를 기본으로 지킨다: 넓이 <= 1024x1024 픽셀, steps <= 28, 1장씩.
넘는 설정은 --allow-paid 없이는 거부한다. 한 번에 만드는 장 수는 --max (기본 2) 로 막는다.

토큰: 클라우드 세션에서는 프록시가 image.novelai.net 요청에 넣어 준다 (Bearer proxy-injected).
로컬에서는 환경 변수 NOVELAI_TOKEN 을 쓴다. 토큰을 파일이나 로그에 남기지 않는다.
필요: 파이썬 표준 라이브러리만.
"""
import argparse
import base64
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
VIBE_URL = 'https://image.novelai.net/ai/encode-vibe'
# Precise(Character) Reference 가 받는 크기: 비율이 가장 가까운 칸에 검은 여백으로 맞춘다
REF_CANVASES = ((1024, 1536), (1536, 1024), (1472, 1472))
FREE_AREA = 1024 * 1024
FREE_STEPS = 28
DEFAULTS = {'model': 'nai-diffusion-4-5-full', 'width': 832, 'height': 1216, 'steps': 28, 'scale': 5.5,
            'sampler': 'k_euler_ancestral'}


def body(prompt, neg, p, seed, refs=None):
    """요청 본문. refs (prepare_refs 결과) 가 없으면 예전과 똑같은 글만 생성."""
    b = {'input': prompt, 'model': p['model'], 'action': 'generate', 'parameters': {
        'params_version': 3, 'width': p['width'], 'height': p['height'], 'scale': p['scale'],
        'sampler': p['sampler'], 'steps': p['steps'], 'n_samples': 1, 'ucPreset': 0, 'qualityToggle': True,
        'seed': seed, 'sm': False, 'sm_dyn': False, 'dynamic_thresholding': False, 'controlnet_strength': 1,
        'legacy': False, 'add_original_image': True, 'cfg_rescale': 0, 'noise_schedule': 'karras',
        'legacy_v3_extend': False, 'skip_cfg_above_sigma': None, 'use_coords': False, 'characterPrompts': [],
        'v4_prompt': {'caption': {'base_caption': prompt, 'char_captions': []}, 'use_coords': False, 'use_order': True},
        'v4_negative_prompt': {'caption': {'base_caption': neg, 'char_captions': []}, 'legacy_uc': False},
        'negative_prompt': neg, 'deliberate_euler_ancestral_bug': False, 'prefer_brownian': True}}
    if refs:
        q = b['parameters']
        if refs.get('char_ref'):
            r = refs['char_ref']
            q['director_reference_images'] = [r['b64']]
            q['director_reference_descriptions'] = [
                {'caption': {'base_caption': r['type'], 'char_captions': []}, 'legacy_uc': False}]
            q['director_reference_information_extracted'] = [1]
            q['director_reference_strength_values'] = [r['strength']]
            q['director_reference_secondary_strength_values'] = [round(1 - r['fidelity'], 2)]   # 1 - fidelity
        if refs.get('vibe'):
            q['reference_image_multiple'] = [v['b64'] for v in refs['vibe']]   # encode-vibe 결과
            q['reference_strength_multiple'] = [v['strength'] for v in refs['vibe']]
            q['normalize_reference_strength_multiple'] = True
        if refs.get('init'):
            r = refs['init']
            b['action'] = 'img2img'
            q.update({'image': r['b64'], 'strength': r['strength'], 'noise': r['noise'],
                      'extra_noise_seed': r['noise_seed'], 'add_original_image': True})
    return b


def post(url, payload):
    """POST json, 응답 바이트. 토큰은 헤더에만 있고 어디에도 찍지 않는다 (오류에는 서버 응답 본문만)."""
    token = os.environ.get('NOVELAI_TOKEN', 'proxy-injected')
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={
        'Content-Type': 'application/json', 'Authorization': f'Bearer {token}',
        # Cloudflare 가 기본 Python-urllib User-Agent 를 막는다 (error 1010)
        'User-Agent': 'pixel-guild-art/1.0'})
    try:
        return urllib.request.urlopen(req, timeout=240).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f'HTTP {e.code} ({url.rsplit("/", 1)[-1]}): {e.read()[:500]!r}')


def generate(payload):
    z = zipfile.ZipFile(io.BytesIO(post(URL, payload)))
    return z.read(z.namelist()[0])


# ---------- 참고 그림 (Pillow 필요; 글만 쓰는 기본 모드에서는 불러오지 않는다) ----------

def _pil():
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit('참고 그림(char_ref/vibe/init_image)에는 Pillow 가 필요하다 (pip install pillow)')
    return Image


def _hex(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def load_rgb(path, pad='#000000'):
    """그림을 RGB 로. 투명한 곳은 pad 색으로 채운다."""
    Image = _pil()
    im = Image.open(path)
    im.load()
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        bg = Image.new('RGBA', im.size, _hex(pad) + (255,))
        im = Image.alpha_composite(bg, im)
    return im.convert('RGB')


def fit(im, size, how='pad', pad='#000000'):
    """size 로 맞춘다: pad = 비율 유지 + 가운데 + 여백, cover = 비율 유지 + 넘치는 곳 자르기, stretch = 늘이기."""
    Image = _pil()
    W, H = size
    w, h = im.size
    if how == 'stretch':
        return im.resize((W, H), Image.LANCZOS)
    k = (max if how == 'cover' else min)(W / w, H / h)
    nw, nh = max(1, round(w * k)), max(1, round(h * k))
    r = im.resize((nw, nh), Image.LANCZOS)
    out = Image.new('RGB', (W, H), _hex(pad))
    out.paste(r, ((W - nw) // 2, (H - nh) // 2))
    return out


def png_b64(im):
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('ascii')


def ref_canvas(size):
    """Precise Reference 칸: 비율이 가장 가까운 것."""
    w, h = size
    return min(REF_CANVASES, key=lambda c: abs((c[0] / c[1]) / (w / h) - 1))


def resolve(path, base):
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def ref_spec(j):
    """작업의 참고 그림 설정 (그림 바이트 없이). 없으면 None. 잘못된 조합은 보내기 전에 거부."""
    base = j.get('base') or os.getcwd()
    spec = {}
    if j.get('char_ref'):
        c = j['char_ref']
        c = {'image': c} if isinstance(c, str) else dict(c)
        if c.get('type', 'character&style') not in ('character', 'character&style', 'style'):
            raise SystemExit(f'[{j["label"]}] char_ref.type 은 character / character&style / style')
        spec['char_ref'] = {'image': resolve(c['image'], base), 'type': c.get('type', 'character&style'),
                            'strength': float(c.get('strength', 1)), 'fidelity': float(c.get('fidelity', 1)),
                            'pad': c.get('pad', '#000000')}
    if j.get('vibe'):
        vs = j['vibe'] if isinstance(j['vibe'], list) else [j['vibe']]
        spec['vibe'] = []
        for v in vs:
            v = {'image': v} if isinstance(v, str) else dict(v)
            spec['vibe'].append({'image': resolve(v['image'], base), 'info': float(v.get('info', 1)),
                                 'strength': float(v.get('strength', 0.6))})
    if j.get('init_image'):
        spec['init'] = {'image': resolve(j['init_image'], base), 'strength': float(j.get('strength', 0.7)),
                        'noise': float(j.get('noise', 0)), 'fit': j.get('init_fit', 'pad'),
                        'pad': j.get('init_pad', '#000000')}
        if spec['init']['fit'] not in ('pad', 'cover', 'stretch'):
            raise SystemExit(f'[{j["label"]}] init_fit 은 pad / cover / stretch')
    if 'char_ref' in spec and 'vibe' in spec:
        raise SystemExit(f'[{j["label"]}] char_ref 와 vibe 는 같이 못 쓴다 (NovelAI 가 둘 중 하나만 받는다)')
    for k, v in spec.items():
        for it in (v if isinstance(v, list) else [v]):
            if not os.path.isfile(it['image']):
                raise SystemExit(f'[{j["label"]}] {k} 그림이 없다: {it["image"]}')
    return spec or None


def describe_refs(spec, p):
    """--dry-run 등에 찍는 한 줄씩 (그림 바이트 없음)."""
    lines = []
    if 'char_ref' in spec:
        c = spec['char_ref']
        Image = _pil()
        with Image.open(c['image']) as im:
            cw, ch = ref_canvas(im.size)
            src = f'{im.size[0]}x{im.size[1]}'
        lines.append(f'mode=char_ref (precise reference) image={c["image"]} ({src} -> pad {cw}x{ch} {c["pad"]}) '
                     f'type={c["type"]} strength={c["strength"]} fidelity={c["fidelity"]} '
                     f'(secondary={round(1 - c["fidelity"], 2)})')
    for v in spec.get('vibe', []):
        lines.append(f'mode=vibe image={v["image"]} info_extracted={v["info"]} strength={v["strength"]} '
                     f'(encode-vibe with model {p["model"]})')
    if 'init' in spec:
        i = spec['init']
        lines.append(f'mode=img2img image={i["image"]} -> {i["fit"]} {p["width"]}x{p["height"]} '
                     f'strength={i["strength"]} noise={i["noise"]}')
    return lines


def prepare_refs(spec, p, seed):
    """그림을 읽고 크기를 맞춰 base64 로 (vibe 는 encode-vibe 를 부른다). 보낼 때만 부른다."""
    if not spec:
        return None
    out = {}
    if 'char_ref' in spec:
        c = spec['char_ref']
        im = load_rgb(c['image'], c['pad'])
        out['char_ref'] = dict(c, b64=png_b64(fit(im, ref_canvas(im.size), 'pad', c['pad'])))
    if 'vibe' in spec:
        out['vibe'] = []
        for v in spec['vibe']:
            raw = png_b64(load_rgb(v['image']))
            enc = post(VIBE_URL, {'image': raw, 'information_extracted': v['info'], 'model': p['model']})
            print(f'  encode-vibe ok: {os.path.basename(v["image"])} -> {len(enc)} bytes')
            out['vibe'].append(dict(v, b64=base64.b64encode(enc).decode('ascii')))
    if 'init' in spec:
        i = spec['init']
        im = fit(load_rgb(i['image'], i['pad']), (p['width'], p['height']), i['fit'], i['pad'])
        out['init'] = dict(i, b64=png_b64(im), noise_seed=(seed + 1) % (2 ** 32 - 8))
    return out


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
        base = os.path.dirname(os.path.abspath(a.prompt_file))   # 참고 그림의 상대 경로 기준
        for j in d if isinstance(d, list) else [d]:
            out = j.get('out') or j.get('file')
            if not out:
                raise SystemExit('prompt-file 항목에 out 이 없다')
            job = {'label': out, 'prompt': j['prompt'], 'negative': j.get('negative') or j.get('neg', ''),
                   'out': out, 'seed': j.get('seed'), 'size': j.get('size'), 'base': base}
            for k in ('char_ref', 'vibe', 'init_image', 'strength', 'noise', 'init_fit', 'init_pad'):
                if k in j:
                    job[k] = j[k]
            jobs.append(job)
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
    ap.add_argument('--prompt-file', help='{"prompt","negative","out","seed", 선택: "char_ref"|"vibe"|"init_image"} '
                    '하나 또는 목록인 json')
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
    specs = [ref_spec(j) for j in jobs]
    seeds = [a.seed if a.seed is not None else (j['seed'] if j['seed'] is not None else random.randrange(1, 2 ** 32 - 1))
             for j in jobs]
    outs = [draft_path(a.outdir, j['out'], seed) for j, seed in zip(jobs, seeds)]   # 금지 폴더도 보내기 전에 검사

    for j, (p, paid), seed, out, spec in zip(jobs, plans, seeds, outs, specs):
        if os.path.exists(out) and not a.force:
            print(f'[{j["label"]}] {out} 가 이미 있다 — 건너뜀 (--force 로 덮어쓰기)')
            continue
        print(f'[{j["label"]}] model={p["model"]} size={p["width"]}x{p["height"]} steps={p["steps"]} '
              f'scale={p["scale"]} sampler={p["sampler"]} n_samples=1 seed={seed}'
              f'{"  (PAID)" if paid else "  (free tier)"}'
              f'{"  (+Anlas: precise reference)" if spec and "char_ref" in spec else ""}'
              f'{"  (+Anlas: encode-vibe)" if spec and "vibe" in spec else ""}')
        print(f'  prompt: {j["prompt"]}')
        print(f'  negative: {j["negative"]}')
        for line in describe_refs(spec, p) if spec else ['mode=text only']:
            print(f'  {line}')
        print(f'  -> {os.path.relpath(out, ROOT) if out.startswith(ROOT + os.sep) else out}')
        if a.dry_run:
            continue
        png = generate(body(j['prompt'], j['negative'], p, seed, prepare_refs(spec, p, seed)))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'wb') as f:
            f.write(png)
        print(f'  saved {len(png)} bytes')
    return 0


if __name__ == '__main__':
    sys.exit(main())
