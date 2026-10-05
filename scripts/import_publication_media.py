#!/usr/bin/env python3
"""Import verified local paper PDFs and visually reviewed figure crops.

Optional dependencies: PyMuPDF and Pillow. The site build does not need them.
Run with --library PATH, then add --apply to save the catalog and assets.
"""
import argparse
import hashlib
import json
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalized(value):
    return re.sub(r'[^a-z0-9]', '', (value or '').lower())


def matched_items(library, papers):
    items = json.loads((library / 'manifest.json').read_text())['items']
    groups, unmatched = defaultdict(list), []
    for item in items:
        if not item.get('file'):
            continue
        source = 'https://dblp.org/rec/' + item['key']
        doi = (item.get('doi') or '').lower()
        matches = [p for p in papers if source in p['sources']
                   or (doi and doi == p.get('doi', '').lower())
                   or normalized(item['title']) == normalized(p['title'])]
        if len(matches) != 1:
            unmatched.append({'key': item['key'], 'matches': len(matches)})
            continue
        groups[matches[0]['id']].append(item)
    selected = {}
    for paper in papers:
        if paper['id'] not in groups:
            continue
        # Prefer the record's own DOI when formal and preprint entries were merged.
        selected[paper['id']] = max(groups[paper['id']], key=lambda i: (
            bool(i.get('doi')) and i['doi'].lower() == paper.get('doi', '').lower(),
            normalized(i['title']) == normalized(paper['title']),
            i.get('version') in ['publishedVersion', 'acceptedVersion', 'author_manuscript']))
    return selected, unmatched


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(doc):
    return hashlib.sha256('\0'.join(page.get_text() for page in doc).encode()).hexdigest()


def save_pdf(source, destination):
    import fitz
    destination.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(source) as original:
        expected_pages, expected_text = len(original), text_digest(original)
        original.save(destination, garbage=4, deflate=True, use_objstms=1, no_new_id=True)
    if destination.stat().st_size >= source.stat().st_size:
        shutil.copyfile(source, destination)
    with fitz.open(destination) as saved:
        if len(saved) != expected_pages or text_digest(saved) != expected_text:
            raise ValueError('PDF content changed: ' + source.name)
    return expected_pages


def save_figure(source, entry, destination):
    import fitz
    from PIL import Image
    with fitz.open(source) as doc:
        page = doc[entry['page'] - 1]
        clip = fitz.Rect(entry['bbox'])
        if not page.rect.contains(clip) or clip.width < 30 or clip.height < 25:
            raise ValueError('Invalid reviewed figure crop: ' + entry['paper_id'])
        scale = min(1200 / clip.width, 900 / clip.height, 3)
        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
        destination.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(
            destination, 'WEBP', quality=90, method=6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--figures', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    payload = json.loads((ROOT / 'data/publications.json').read_text())
    papers = payload['publications']
    selected, unmatched = matched_items(args.library, papers)
    document_reviews = {entry['paper_id']: entry for entry in json.loads(
        (ROOT / 'data/publication-pdf-review.json').read_text())}
    reviewed = {}
    if args.figures:
        reviewed = {entry['paper_id']: entry for entry in json.loads(args.figures.read_text())
                    if entry.get('approved')}
    report = {'matched_records': len(selected), 'unmatched': unmatched,
              'added_pdfs': [], 'source_pdf_links': [], 'added_images': [], 'assets': []}
    saved, checked = {}, set()
    for paper in papers:
        item = selected.get(paper['id'])
        if not item:
            continue
        source = args.library / item['file']
        original_sha = item['sha256']
        document_review = document_reviews.get(paper['id'], {})
        if document_review and document_review['pdf_sha256'] != original_sha:
            raise ValueError('Reviewed document version changed: ' + paper['id'])
        if original_sha not in checked:
            if digest(source) != original_sha:
                raise ValueError('Library checksum mismatch: ' + item['key'])
            checked.add(original_sha)
        if document_review.get('delivery') == 'source':
            paper['pdf_url'] = item['source_url']
            paper['pdf'] = None
            paper['pdf_metadata'] = dict(source=item['source_url'], version=item['version'],
                original_sha256=original_sha, library_key=item['key'], document_kind='article')
            report['source_pdf_links'].append(paper['id'])
        elif not paper.get('pdf'):
            relative = 'downloads/publication/papers/' + original_sha[:20] + '.pdf'
            if args.apply and original_sha not in saved:
                destination = ROOT / relative
                pages = save_pdf(source, destination)
                saved[original_sha] = {'path': relative, 'sha256': digest(destination),
                                       'bytes': destination.stat().st_size, 'pages': pages}
            paper['pdf'] = relative
            if args.apply:
                paper['pdf_metadata'] = dict(saved[original_sha],
                    source=item.get('source_url') or paper['url'], version=item['version'],
                    original_sha256=original_sha, library_key=item['key'],
                    document_kind=document_review.get('document_kind', 'article'))
            report['added_pdfs'].append(paper['id'])
        entry = reviewed.get(paper['id'])
        if entry and not paper.get('image'):
            if entry['pdf_sha256'] != original_sha:
                raise ValueError('Figure source changed: ' + paper['id'])
            relative = 'images/papers/' + paper['id'] + '.webp'
            if args.apply:
                save_figure(source, entry, ROOT / relative)
            paper['image'] = dict(path=relative, kind=entry.get('kind', 'figure-1'),
                source=item.get('source_url') or paper['url'], page=entry['page'],
                bbox=entry['bbox'], caption=entry.get('caption', ''), pdf_sha256=original_sha)
            report['added_images'].append(paper['id'])
    if args.apply:
        payload['updated'] = date.today().isoformat()
        (ROOT / 'data/publications.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        report['assets'] = list(saved.values())
        report['new_pdf_bytes'] = sum(asset['bytes'] for asset in saved.values())
        (ROOT / 'data/publication-media-import.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: len(value) if isinstance(value, list) else value
                      for key, value in report.items()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
