#!/usr/bin/env python3
"""Build English pages and summaries from the same news, award and paper records."""
import json
from pathlib import Path
from urllib.parse import quote
from publication_common import esc, authors_html
from publication_dates import latest_publications, format_date
from site_shell import ROOT, english_page, asset


def time_tag(value):
    return f'<time datetime="{value}">{format_date(value)}</time>'


def figure(paper, page):
    if not paper.get('image'):
        return ''
    return f'<a class="paper-figure" href="{esc(paper["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(paper["title"])}" data-bibliographic><img src="{asset(page, paper["image"]["path"])}" alt="{esc(paper["title"])}" loading="lazy" decoding="async" width="448" height="296"></a>'


def paper_title(paper, heading='h3'):
    return f'<{heading} class="paper-title" dir="auto" data-bibliographic><a href="{esc(paper["url"])}" target="_blank" rel="noopener noreferrer">{esc(paper["title"])}</a></{heading}>'


def news_list(records, page='index.html'):
    rows = []
    for entry in records:
        href = asset(page, entry['link']) if entry.get('link') else ''
        link = f' <a href="{href}">{esc(entry["link_label"])}</a>' if href else ''
        rows.append(f'<li id="news-{entry["id"]}" data-news-id="{entry["id"]}">{time_tag(entry["date"])}<p>{esc(entry["text"])}{link}</p></li>')
    return '<ul class="news-list">' + ''.join(rows) + '</ul>'


def award_status(award):
    label = {'nomination': 'Nomination', 'finalist': 'Finalist'}.get(award['status'])
    return f'<span class="award-nomination">{label}</span>' if label else ''


def award_summary(records, papers):
    rows=[]
    for award in records[:3]:
        rows.append(f'<li data-award-id="{award["id"]}"><p class="award-meta"><span data-bibliographic>{award["date"][:4]} · {esc(award["venue"])}</span><span class="award-label">{esc(award["name"])}</span></p>{award_status(award)}{paper_title(papers[award["paper_id"]])}</li>')
    return '<ul class="award-summary">' + ''.join(rows) + '</ul>'


def latest_cards(records):
    cards = []
    kinds = {'journal': 'Journal article', 'conference': 'Conference paper', 'preprint': 'Preprint'}
    for p in records:
        info = f'<span>{kinds[p["kind"]]}</span><span data-bibliographic><bdi>{esc(p["venue"])}</bdi></span>'
        value = p.get('published_date', str(p['year']))
        date = time_tag(value)
        if p.get('published_date_source'):
            date = f'<a class="date-source" href="{esc(p["published_date_source"])}" target="_blank" rel="noopener noreferrer" title="Publication date source">{date}</a>'
        cards.append(f'<article class="latest-paper{(" no-figure" if not p.get("image") else "")}" data-paper-id="{p["id"]}">{figure(p,"index.html")}<div class="paper-content"><p class="paper-meta">{info}</p>{paper_title(p)}<p class="paper-authors" dir="auto" data-bibliographic>{authors_html(p)}</p><p class="paper-date">{date}</p></div></article>')
    return ''.join(cards)


def industry_cards():
    return '<div class="industry-grid"><a class="industry-card" href="https://intentreach.ok.kimi.link" target="_blank" rel="noopener noreferrer"><h3 lang="zh-CN">意想触达</h3><span>Visit website ↗</span></a><div class="industry-card"><h3 lang="zh-CN">南曦控股</h3></div><div class="industry-card"><h3 lang="zh-CN">炽枢智域</h3></div></div>'


def build():
    payload = json.loads((ROOT / 'data/publications.json').read_text())
    papers = {p['id']: p for p in payload['publications']}
    news = sorted(json.loads((ROOT / 'data/news.json').read_text()), key=lambda a: a['date'], reverse=True)
    awards = sorted(json.loads((ROOT / 'data/awards.json').read_text()), key=lambda a: a['date'], reverse=True)
    home = (ROOT / 'templates/home.html').read_text()
    for key, value in {'news': news_list(news[:3]), 'awards': award_summary(awards, papers), 'publications': latest_cards(latest_publications(payload['publications'])), 'industry': industry_cards()}.items():
        home = home.replace('{{' + key + '}}', value)
    (ROOT / 'index.html').write_text(english_page('index.html', 'About', home, ('js/carousel.js',)))
    main = '<main id="main-content" class="page-shell news-page"><header class="page-heading"><h1>News</h1></header>' + news_list(news, 'allnews.html') + '</main>'
    (ROOT / 'allnews.html').write_text(english_page('allnews.html', 'News', main))
    cards = []
    for award in awards:
        p = papers[award['paper_id']]
        needs_status = award['status'] == 'finalist' or (award['status'] == 'nomination' and 'nomination' not in award['name'].casefold())
        note = award_status(award) if needs_status else ''
        date = f'<span class="visually-hidden">{time_tag(award["date"])}</span>'
        source = f'<a href="{esc(award["source"])}" target="_blank" rel="noopener noreferrer" title="Award source ↗">{esc(award["name"])} <span class="award-source-mark" aria-hidden="true">↗</span></a>'
        cards.append(f'<article class="award-card" id="award-{award["id"]}" data-award-id="{award["id"]}" data-paper-id="{p["id"]}" data-status="{award["status"]}"><div class="award-venue"><bdi data-bibliographic>{esc(award["venue"])}</bdi>{date}</div><div class="paper-content"><h2 class="award-label">{source}{note}</h2>{paper_title(p)}</div></article>')
    body = '<main id="main-content" class="page-shell awards-page"><header class="page-heading"><h1>Paper Awards</h1></header><div class="award-list">' + ''.join(cards) + '</div></main>'
    (ROOT / 'awards').mkdir(exist_ok=True)
    (ROOT / 'awards/index.html').write_text(english_page('awards/index.html', 'Awards', body))
    body = '<main id="main-content" class="page-shell collaboration-page"><header class="page-heading"><h1>Industry–Academia Collaboration</h1><p>Joint research and technology transfer in interactive technologies.</p></header>' + industry_cards() + '<div class="collaboration-contact"><h2>Get in touch</h2><p><a href="mailto:hainingliang@hkust-gz.edu.cn">hainingliang@hkust-gz.edu.cn</a></p></div></main>'
    (ROOT / 'entrepreneurship/index.html').write_text(english_page('entrepreneurship/index.html', 'Industry–Academia Collaboration', body))
    (ROOT / 'vacancies/index.html').write_text(english_page('vacancies/index.html', 'Join Us', (ROOT / 'templates/join.html').read_text()))


if __name__ == '__main__':
    build()
