#!/usr/bin/env python3
"""Check image identity, responsive URLs, dimensions and transfer sizes."""
import json
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from PIL import Image
from optimize_images import ROOT, MANIFEST, pages, image_source

manifest = json.loads(MANIFEST.read_text())['images']
papers = {p['id']: p for p in json.loads((ROOT / 'data/publications.json').read_text())['publications']}
for source, record in manifest.items():
    assert (ROOT / source).stat().st_size == record['original_bytes'], source
    assert record['variants'], source
    for variant in record['variants']:
        path = ROOT / variant['path']
        assert path.stat().st_size == variant['bytes'] <= record['original_bytes'], path
        with Image.open(path) as image:
            assert image.size == (variant['width'], variant['height']), path
            image.verify()
        assert variant['width'] <= record['width'], f'Upscaled image: {path}'
        assert abs(variant['height'] - record['height'] * variant['width'] / record['width']) <= 1, path

count = 0
for page in pages():
    soup = BeautifulSoup(page.read_text(), 'html.parser')
    for image in soup.select('img[data-image-source]'):
        source = image_source(image, page)
        record = manifest[source]
        def resolve(value):
            return (page.parent / unquote(urlsplit(value).path)).resolve().relative_to(ROOT).as_posix()
        variants = {v['path']: v for v in record['variants']}
        assert resolve(image['src']) in variants, (page, source)
        fallback = variants[resolve(image['src'])]
        assert (int(image['width']), int(image['height'])) == (fallback['width'], fallback['height']), page
        expected = {(v['path'], v['width']) for v in record['variants']}
        actual = {(resolve(url), int(width.removesuffix('w')))
                  for url, width in (item.strip().rsplit(' ', 1) for item in image['srcset'].split(','))}
        assert actual == expected and image['sizes'], (page, source, 'Incorrect responsive candidates')
        assert image.get('fetchpriority') == 'high' or image.get('loading') == 'lazy', page
        count += 1
    for card in soup.select('.paper-card, .latest-paper'):
        image = card.select_one('.paper-figure img')
        if image:
            paper_id = card.get('data-paper-id', card.get('id', '').removeprefix('paper-'))
            original = papers[paper_id]['image']['path']
            assert image['data-image-source'] == original, (page, paper_id, 'Wrong paper image')

before = sum(record['original_bytes'] for record in manifest.values())
after = sum(record['variants'][-1]['bytes'] for record in manifest.values())
assert after < before
print(f'PASS: {len(manifest)} source images and {count} image placements; originals retained, correct responsive candidates, no upscaling or wrong paper images; maximum image payload reduced by {100 * (1 - after / before):.1f}%.')
