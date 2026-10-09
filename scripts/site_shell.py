"""One navigation and footer for every page and language."""
import json
import os
from pathlib import Path
from urllib.parse import quote
from functools import lru_cache
from publication_common import esc

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {'en': 'English', 'zh': '中文', 'fr': 'Français', 'ar': 'العربية', 'ja': '日本語'}
VERSION = '20261009-readable-type'
NAV = [('About', 'index.html'), ('Members', 'members/index.html'),
       ('Awards', 'awards/index.html'), ('Publications', 'publications/index.html'),
       ('Collaboration', 'index.html#industry'),
       ('Join Us', 'vacancies/index.html')]


@lru_cache(None)
def dictionary(lang):
    return {} if lang == 'en' else json.loads((ROOT / f'data/locales/{lang}.json').read_text())


def text(value, lang='en'):
    return value if lang == 'en' else dictionary(lang)[value]


def link(page, target, lang='en', target_lang=None):
    prefix = '' if lang == 'en' else lang
    dest = ROOT / prefix / page
    path, sep, fragment = target.partition('#')
    code = target_lang or lang
    source = ROOT / ('' if code == 'en' else code) / path
    return quote(os.path.relpath(source, dest.parent), safe='/') + (sep + fragment if sep else '')


def asset(page, path, lang='en'):
    dest = ROOT / ('' if lang == 'en' else lang) / page
    return quote(os.path.relpath(ROOT / path, dest.parent), safe='/')


def favicon(page, lang='en'):
    return f'<link rel="icon" type="image/svg+xml" href="{asset(page, "images/brand/fit-awe-icon.svg", lang)}?v={VERSION}">'


def header(page, lang='en'):
    entries = []
    for label, target in NAV:
        current = ' aria-current="page"' if target == page else ''
        extra = ' class="industry-nav-link"' if '#industry' in target else ''
        entries.append(f'<li><a href="{link(page, target, lang)}"{current}{extra}>{esc(text(label, lang))}</a></li>')
    languages = []
    for code, label in LANGUAGES.items():
        current = ' aria-current="page"' if code == lang else ''
        languages.append(f'<li><a href="{link(page, page, lang, code)}" hreflang="{code}" lang="{code}"{current}>{label}</a></li>')
    return f'''<a class="skip-link" href="#main-content">{esc(text('Skip to content', lang))}</a>
<header class="navbar site-header"><div class="container-fluid header-inner">
<div class="navbar-header"><a class="navbar-brand" href="{link(page, 'index.html', lang)}" title="{esc(text('HKUST(GZ) · Computational Media and Arts', lang))}"><img class="brand-mark" src="{asset(page, 'images/brand/fit-awe-icon.svg', lang)}?v={VERSION}" alt="" aria-hidden="true" width="1020" height="500"><span class="brand-wordmark">FIT-AWE<span> Lab</span></span></a>
<button class="navbar-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-navigation" aria-label="{esc(text('Toggle navigation', lang))}"><span></span><span></span><span></span></button></div>
<nav class="navbar-collapse" id="site-navigation" aria-label="{esc(text('Main navigation', lang))}"><ul class="navbar-nav">{''.join(entries)}
<li class="dropdown"><button class="language-toggle" type="button" aria-expanded="false" aria-controls="language-menu" aria-label="{esc(text('Choose language', lang))}">{LANGUAGES[lang]} <span aria-hidden="true">⌄</span></button><ul class="dropdown-menu" id="language-menu" hidden>{''.join(languages)}</ul></li>
</ul></nav></div></header>'''


def footer(page, lang='en'):
    return '<footer class="site-footer"><div class="container-fluid"><span>FIT-AWE Lab · HKUST(GZ)</span></div></footer>'


def english_page(page, title, body, scripts=()):
    styles = f'<link rel="stylesheet" href="{asset(page, "css/refinements.css")}?v={VERSION}"><link rel="stylesheet" href="{asset(page, "css/publications.css")}?v={VERSION}">'
    # All pages use native navigation, with no dependency on the old Bootstrap scripts.
    js = ''.join(f'<script src="{asset(page, s)}?v={VERSION}" defer></script>' for s in ('js/navigation.js',) + tuple(scripts))
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | FIT-AWE Lab</title><meta name="description" content="{esc(title)} · FIT-AWE Lab · HKUST(GZ)">{styles}</head><body><header class="navbar"></header>{body}<footer class="site-footer"></footer>{js}</body></html>\n'''
