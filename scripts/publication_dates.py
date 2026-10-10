"""Publication dates with their original precision and verifiable sources."""
import calendar
import re
from datetime import date, datetime
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


def valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2})?(?:-\d{2})?', value):
        return False
    parts = [int(x) for x in value.split('-')]
    try:
        date(*parts, *([1] * (3 - len(parts))))
        return True
    except ValueError:
        return False


def crossref_date(item, source):
    # Never use created, indexed or deposited timestamps as publication dates.
    for field in ('published-online', 'published', 'issued', 'published-print'):
        parts = item.get(field, {}).get('date-parts', [[]])[0]
        if not parts or not 1 <= len(parts) <= 3:
            continue
        value = '-'.join(str(x).zfill(4 if i == 0 else 2) for i, x in enumerate(parts))
        if valid_date(value):
            return {'published_date': value, 'published_date_source': source,
                    'published_date_basis': field}
    return {}


def fetch_date(paper, session=None):
    client = session or requests
    doi = paper.get('doi', '')
    arxiv = re.search(r'(\d{4}\.\d{4,5})', doi if 'arxiv' in doi.lower() else paper.get('url', ''))
    if paper['kind'] == 'preprint' and arxiv:
        source = 'https://arxiv.org/abs/' + arxiv[1]
        response = client.get(source, timeout=18)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        history = soup.select_one('.submission-history')
        if history:
            first = re.search(r'\[v1\]\s*(?:[A-Za-z]{3},\s*)?(\d{1,2} [A-Za-z]{3} \d{4})', history.get_text(' ', strip=True))
            if first:
                return {'published_date': datetime.strptime(first[1], '%d %b %Y').date().isoformat(),
                        'published_date_source': source, 'published_date_basis': 'first-submission'}
        return {}
    if doi:
        source = 'https://api.crossref.org/works/' + quote(doi, safe='')
        response = client.get(source, timeout=18)
        response.raise_for_status()
        item = response.json()['message']
        # A DOI must resolve to this work, rather than silently replacing its date.
        if item.get('DOI', '').casefold() != doi.casefold():
            return {}
        return crossref_date(item, source)
    return {}


def publication_sort_key(paper):
    value = paper.get('published_date')
    if value and valid_date(value):
        parts = tuple(int(x) for x in value.split('-'))
        return parts + (0,) * (3 - len(parts))
    return (paper['year'], 0, 0)


def chronological_publications(papers):
    """Order by catalog year, then known online dates; retain every record and tie."""
    def catalog_key(paper):
        value = paper.get('published_date')
        known = value and valid_date(value) and len(value) > 4
        return (paper['year'], publication_sort_key(paper) if known else (0, 0, 0))
    return sorted(papers, key=catalog_key, reverse=True)


def latest_publications(papers, count=6, today=None, *, require_image=False):
    today = today or date.today()
    eligible = []
    for paper in papers:
        if require_image and not paper.get('image'):
            continue
        value = paper.get('published_date')
        if value and valid_date(value):
            parts = tuple(int(x) for x in value.split('-'))
            start = date(*parts, *([1] * (3 - len(parts))))
            if start > today:
                continue
            key = parts + (0,) * (3 - len(parts))
        else:
            if paper['year'] > today.year:
                continue
            key = (paper['year'], 0, 0)
        if paper['kind'] in ('journal', 'conference', 'preprint'):
            eligible.append((key, paper))
    # Python's stable sort retains catalog order for equal dates.
    eligible.sort(key=lambda entry: entry[0], reverse=True)
    return [paper for _, paper in eligible[:count]]


MONTHS = {
    'en': calendar.month_name[1:],
    'zh': [f'{x}月' for x in range(1, 13)],
    'fr': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
    'ar': ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
    'ja': [f'{x}月' for x in range(1, 13)],
}


def format_date(value, lang='en'):
    if not valid_date(value):
        raise ValueError('Invalid publication date: ' + str(value))
    parts = [int(x) for x in value.split('-')]
    if len(parts) == 1:
        return str(parts[0]) + ('年' if lang in ('zh', 'ja') else '')
    year, month = parts[:2]
    name = MONTHS[lang][month - 1]
    if lang in ('zh', 'ja'):
        return f'{year}年{name}' + (f'{parts[2]}日' if len(parts) == 3 else '')
    if len(parts) == 2:
        return f'{name} {year}'
    return f'{name} {parts[2]}, {year}' if lang == 'en' else f'{parts[2]} {name} {year}'
