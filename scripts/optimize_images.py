#!/usr/bin/env python3
"""Create cached, responsive image derivatives while retaining original sources."""
import hashlib
import io
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from bs4 import BeautifulSoup
from PIL import Image, ImageOps, features
from build_locales import ROOT, PAGES, LANGUAGES

MANIFEST = ROOT / 'data/image-variants.json'
OUTPUT = ROOT / 'images/optimized'
IMAGE_TAG = re.compile(r'<img\b[^>]*>', re.IGNORECASE)
SETTINGS = {
    'hero': ((480, 960, 1440), 84),
    'paper': ((480, 960), 90),
    'portrait': ((160, 320, 640), 86),
    'logo': ((480, 960), 95),
    'other': ((640, 1280), 88),
}


def pages():
    result = [ROOT / ('' if lang == 'en' else lang) / page
              for lang in LANGUAGES for page in PAGES + ['publications/index.html']]
    result += [ROOT / prefix / 'members/haining-liang/index.html' for prefix in ('', 'zh')]
    return result


def image_source(tag, page):
    if tag.get('data-image-source'):
        source = ROOT / tag['data-image-source']
    else:
        url = urlsplit(tag.get('src', ''))
        if url.scheme or url.netloc or not url.path:
            return None
        source = page.parent / unquote(url.path)
    source = source.resolve()
    if not source.is_relative_to(ROOT) or source.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        return None
    if not source.is_file():
        raise FileNotFoundError(f'{page.relative_to(ROOT)}: {source}')
    return source.relative_to(ROOT).as_posix()


def classes(tag):
    return set(tag.get('class', [])) | {
        value for parent in tag.parents if getattr(parent, 'attrs', None)
        for value in parent.get('class', [])
    }


def role(tag):
    names = classes(tag)
    if 'lab-carousel' in names:
        return 'hero'
    if 'paper-figure' in names:
        return 'paper'
    if names & {'member-photo', 'collaborator-photo', 'portrait'}:
        return 'portrait'
    if 'institution-logo' in names:
        return 'logo'
    return 'other'


def sizes(tag):
    names = classes(tag)
    if 'lab-carousel' in names:
        return '(max-width: 719px) calc(100vw - 40px), (max-width: 1099px) calc((100vw - 80px) / 2.1), (max-width: 1247px) calc((100vw - 332px) / 2.1), 437px'
    if 'latest-paper' in names:
        return '(max-width: 719px) calc(100vw - 40px), (max-width: 1099px) calc((100vw - 76px) / 2), (max-width: 1247px) calc((100vw - 332px) / 2), 458px'
    if 'paper-figure' in names:
        return '(max-width: 719px) calc(100vw - 40px), (max-width: 999px) 176px, 280px'
    if 'portrait' in names:
        return '(max-width: 999px) 114px, 212px'
    if names & {'member-photo', 'collaborator-photo'}:
        return '(max-width: 719px) 112px, 132px'
    if 'institution-logo--cma' in names:
        return '(max-width: 719px) 330px, 408px'
    if 'institution-logo' in names:
        return '(max-width: 719px) 160px, 230px'
    return '(max-width: 719px) calc(100vw - 40px), 640px'


def variants(source, category, previous):
    raw = (ROOT / source).read_bytes()
    widths, quality = SETTINGS[category]
    digest = hashlib.sha256(raw + repr((widths, quality, 1)).encode()).hexdigest()
    cached = previous.get(source)
    if cached and cached['fingerprint'] == digest and all((ROOT / v['path']).is_file() for v in cached['variants']):
        return source, cached
    with Image.open(io.BytesIO(raw)) as opened:
        if getattr(opened, 'n_frames', 1) != 1:
            return source, None
        image = ImageOps.exif_transpose(opened)
        image = image.convert('RGBA' if 'A' in image.getbands() or 'transparency' in image.info else 'RGB')
        original = dict(path=source, width=image.width, height=image.height, bytes=len(raw))
        records = {}
        for width in sorted({min(w, image.width) for w in widths}):
            height = max(1, round(image.height * width / image.width))
            resized = image.resize((width, height), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            resized.save(output, format='WEBP', quality=quality, method=6, exact=True,
                         icc_profile=opened.info.get('icc_profile', b''))
            data = output.getvalue()
            if len(data) >= len(raw):
                records[source] = original
                continue
            filename = f'{digest[:16]}-{width}.webp'
            path = OUTPUT / filename
            path.write_bytes(data)
            relative = path.relative_to(ROOT).as_posix()
            records[relative] = dict(path=relative, width=width, height=height, bytes=len(data))
        return source, dict(fingerprint=digest, role=category, original_bytes=len(raw),
                            width=image.width, height=image.height,
                            variants=sorted(records.values(), key=lambda v: v['width']))


def optimize():
    if not features.check('webp'):
        raise RuntimeError('Image optimization requires Pillow with WebP support.')
    documents = {}
    sources = {}
    for page in pages():
        markup = page.read_text()
        tags = BeautifulSoup(markup, 'html.parser').find_all('img')
        assert len(tags) == len(IMAGE_TAG.findall(markup)), page
        documents[page] = (markup, tags)
        for tag in tags:
            source = image_source(tag, page)
            if source:
                category = role(tag)
                previous = sources.get(source)
                if previous is None or max(SETTINGS[category][0]) > max(SETTINGS[previous][0]):
                    sources[source] = category
    previous = json.loads(MANIFEST.read_text()).get('images', {}) if MANIFEST.exists() else {}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = [pool.submit(variants, source, category, previous) for source, category in sorted(sources.items())]
        for job in jobs:
            source, record = job.result()
            if record:
                manifest[source] = record
    for page, (markup, tags) in documents.items():
        replacements = iter(tags)
        def replace(match):
            tag = next(replacements)
            source = image_source(tag, page)
            record = manifest.get(source)
            if not record:
                return match.group()
            def relative(path):
                return quote(os.path.relpath(ROOT / path, page.parent), safe='/')
            choices = record['variants']
            fallback = choices[-1]
            tag['src'] = relative(fallback['path'])
            tag['srcset'] = ', '.join(f'{relative(v["path"])} {v["width"]}w' for v in choices)
            tag['sizes'] = sizes(tag)
            tag['width'], tag['height'] = fallback['width'], fallback['height']
            tag['data-image-source'] = source
            tag['decoding'] = 'async'
            if tag.get('fetchpriority') != 'high':
                tag['loading'] = 'lazy'
            return str(tag)
        updated = IMAGE_TAG.sub(replace, markup)
        if updated != markup:
            page.write_text(updated)
    MANIFEST.write_text(json.dumps(dict(version=1, images=manifest), ensure_ascii=False, indent=2) + '\n')
    before = sum(record['original_bytes'] for record in manifest.values())
    after = sum(record['variants'][-1]['bytes'] for record in manifest.values())
    print(f'Optimized {len(manifest)} source images: {before / 1024**2:.2f} → {after / 1024**2:.2f} MiB at maximum display resolution.', flush=True)


if __name__ == '__main__':
    optimize()
