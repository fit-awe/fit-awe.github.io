#!/usr/bin/env python3
"""Render the shared publication catalog into five ready-to-host HTML pages.
Requires beautifulsoup4 for preserving the existing site navigation.
"""
import html
import json
import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/publications.json'
LABELS = {
 'ja': dict(topic='研究分野',all_topics='すべての研究分野',topic_count='{count} 件の論文',title='研究論文',description='FIT-AWE 研究室の研究成果を年代別に紹介します。',search='論文を検索',placeholder='タイトル、著者、掲載誌、キーワード',year='発表年',all='すべての年',kind='種類',all_types='すべての種類',journal='学術誌論文',conference='国際会議論文',preprint='プレプリント',other='その他の研究',count='{total} 件中 {shown} 件を表示',reset='絞り込みを解除',empty='該当する論文はありません。キーワードや条件を変更してください。',library='論文を見る',pdf='PDF',close='閉じる',copy='BibTeX をコピー',copied='コピーしました。',failed='自動コピーできません。選択された引用情報を手動でコピーしてください。',updated='更新日',figure='論文の図：'),
 'en': dict(topic='Research area',all_topics='All research areas',topic_count='{count} publications',title='Publications',description='Research from FIT-AWE Lab, across the years.',search='Search publications',placeholder='Title, author, venue or keyword',year='Year',all='All years',kind='Type',all_types='All publications',journal='Journal articles',conference='Conference papers',preprint='Preprints',other='Other research',count='{shown} of {total} publications',reset='Clear filters',empty='No matching publications. Try another keyword or clear the filters.',library='View publication',pdf='PDF',close='Close',copy='Copy BibTeX',copied='Copied.',failed='Copy unavailable. The citation is selected; copy it manually.',updated='Updated',figure='Figure from'),
 'zh': dict(topic='研究方向',all_topics='全部方向',topic_count='{count} 篇论文',title='全部论文',description='按年份浏览 FIT-AWE 实验室的研究成果。',search='搜索论文',placeholder='输入标题、作者、期刊或关键词',year='年份',all='全部年份',kind='类型',all_types='全部类型',journal='期刊论文',conference='会议论文',preprint='预印本',other='其他研究',count='显示 {shown} / {total} 篇论文',reset='清除筛选',empty='没有找到匹配的论文，请更换关键词或清除筛选。',library='查看论文',pdf='PDF',close='关闭',copy='复制 BibTeX',copied='已复制。',failed='暂时无法自动复制，引用内容已选中，可手动复制。',updated='更新于',figure='论文配图：'),
 'fr': dict(topic='Axe de recherche',all_topics='Tous les axes',topic_count='{count} publications',title='Publications',description='Les travaux du laboratoire FIT-AWE, au fil des années.',search='Rechercher',placeholder='Titre, auteur, revue ou mot-clé',year='Année',all='Toutes les années',kind='Type',all_types='Tous les types',journal='Articles de revue',conference='Articles de conférence',preprint='Prépublications',other='Autres travaux',count='{shown} publications sur {total}',reset='Effacer les filtres',empty='Aucune publication trouvée. Essayez un autre mot-clé.',library='Voir la publication',pdf='PDF',close='Fermer',copy='Copier le BibTeX',copied='Copié.',failed='Copie indisponible. Copiez manuellement le texte sélectionné.',updated='Mise à jour',figure='Figure de'),
 'ar': dict(topic='مجال البحث',all_topics='جميع المجالات',topic_count='{count} منشورًا',title='جميع المنشورات',description='أبحاث مختبر FIT-AWE عبر السنوات.',search='البحث في المنشورات',placeholder='العنوان أو المؤلف أو المجلة أو كلمة مفتاحية',year='السنة',all='جميع السنوات',kind='النوع',all_types='جميع الأنواع',journal='مقالات المجلات',conference='أوراق المؤتمرات',preprint='المطبوعات الأولية',other='أبحاث أخرى',count='عرض {shown} من {total} منشورًا',reset='مسح الفلاتر',empty='لا توجد نتائج مطابقة. جرّب كلمة أخرى أو امسح الفلاتر.',library='عرض المنشور',pdf='PDF',close='إغلاق',copy='نسخ BibTeX',copied='تم النسخ.',failed='النسخ غير متاح. انسخ النص المحدد يدويًا.',updated='آخر تحديث',figure='شكل من'),
}
from publication_common import esc, author_key, lab_author_keys, bibtex, collaborator_search_names, collaborator_queries, paper_collaborators
from publication_dates import chronological_publications, format_date
from site_shell import header, footer, favicon, stylesheets, text, VERSION

SHORT_VENUES = {
 'IEEE Trans. Vis. Comput. Graph.': 'IEEE TVCG',
 'IEEE Transactions on Visualization and Computer Graphics': 'IEEE TVCG',
 'CHI Extended Abstracts': 'CHI EA',
 'Proc. ACM Hum. Comput. Interact.': 'PACM HCI',
 'Proc. ACM Comput. Graph. Interact. Tech.': 'PACM CGIT',
 'Int. J. Hum. Comput. Interact.': 'IJHCI',
 'International Journal of Human-Computer Interaction': 'IJHCI',
 'International Journal of Human–Computer Interaction': 'IJHCI',
 'Int. J. Hum. Comput. Stud.': 'IJHCS',
 'EdMedia: World Conference on Educational Media and Technology': 'EdMedia',
 'The Journal of Interactive Learning Research': 'JILR',
 'VISIGRAPP (1): GRAPP, HUCAPP, IVAPP': 'VISIGRAPP',
 'CoRR': 'arXiv',
 'arXiv (Cornell University)': 'arXiv',
}
COMPACT_LABELS = {
 'en': dict(all_topics='All', more='More filters'),
 'zh': dict(all_topics='全部', more='更多筛选'),
 'fr': dict(all_topics='Tous', more='Plus de filtres'),
 'ar': dict(all_topics='الكل', more='فلاتر إضافية'),
 'ja': dict(all_topics='すべて', more='詳細フィルター'),
}
DOWNLOAD_LABELS = {
 'en': 'Download PDF', 'zh': '下载 PDF', 'fr': 'Télécharger le PDF',
 'ar': 'تنزيل PDF', 'ja': 'PDF をダウンロード',
}
OPEN_PDF_LABELS = {
 'en': 'Open PDF', 'zh': '打开 PDF', 'fr': 'Ouvrir le PDF',
 'ar': 'فتح PDF', 'ja': 'PDF を開く',
}
SUPPLEMENT_LABELS = {
 'en': 'Supplementary PDF', 'zh': '补充材料 PDF', 'fr': 'PDF complémentaire',
 'ar': 'PDF تكميلي', 'ja': '補足資料 PDF',
}

def build():
 from build_locales import build as build_pages
 build_pages()
 payload=json.loads(DATA.read_text());papers=chronological_publications(payload['publications'])
 lab_authors=lab_author_keys()
 years=sorted({p['year'] for p in papers},reverse=True)
 topics=json.loads((ROOT/'data/research-topics.json').read_text())
 for lang,c in LABELS.items():
  compact=COMPACT_LABELS[lang]
  dest=ROOT/('' if lang=='en' else lang)/'publications/index.html'
  dest.parent.mkdir(parents=True,exist_ok=True)
  navbar=header('publications/index.html',lang);site_footer=footer('publications/index.html',lang)
  def asset(path):return quote(os.path.relpath(ROOT/path,dest.parent),safe='/')
  def filter_group(key,legend,entries,compact=False):
   buttons=''.join(f'<button type="button" data-filter="{key}" data-value="{esc(value)}" aria-pressed="{str(not value).lower()}">{esc(label)}</button>' for value,label in entries)
   legend_attrs=' class="visually-hidden"' if compact else ''
   return f'<fieldset class="filter-group" id="publication-{key}"><legend{legend_attrs}>{esc(legend)}</legend><div class="filter-options">{buttons}</div></fieldset>'
  primary=filter_group('topic',c['topic'],[('',compact['all_topics'])]+[(t['id'],t.get('short_labels',t['labels'])[lang]) for t in topics],compact=True)
  filters=filter_group('year',c['year'],[('',c['all'])]+[(str(y),str(y)) for y in years])
  filters+=filter_group('type',c['kind'],[('',c['all_types'])]+[(k,c[k]) for k in ['journal','conference','preprint','other']])
  profile_label={'en':'Publication profiles','zh':'学术资料页','fr':'Profils de recherche','ar':'الملفات البحثية','ja':'学術プロフィール'}[lang]
  alternates=''.join('<link rel="alternate" hreflang="'+code+'" href="'+asset(('' if code=='en' else code+'/')+'publications/index.html')+'">' for code in LABELS)
  cards=[]
  queries=esc(json.dumps(collaborator_queries(),ensure_ascii=False,separators=(',',':')))
  for p in papers:
    year=p['year']
    url=esc(p['url']);title=esc(p['title']);figure=''
    if p.get('image'):
     figure=f'<a class="paper-figure" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{title}"><img src="{asset(p["image"]["path"])}" alt="{esc(c["figure"])} {title}" loading="lazy" decoding="async" width="448" height="296"></a>'
    authors=[]
    for author in p['authors']:
     a=esc(author)
     if author_key(author) in lab_authors:a=f'<strong>{a}</strong>'
     authors.append(a)
    pdf=''
    pdf_label=SUPPLEMENT_LABELS[lang] if p.get('pdf_metadata',{}).get('document_kind')=='supplement' else 'PDF'
    if p.get('pdf_url'):
     pdf=f'<a class="paper-pdf" href="{esc(p["pdf_url"])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(OPEN_PDF_LABELS[lang])}: {title}">{esc(pdf_label)} ↗</a>'
    elif p.get('pdf'):
     filename=f'{year}-'+re.sub(r'[^a-zA-Z0-9]+','-',p['title']).strip('-')[:100]+'.pdf'
     pdf=f'<a class="paper-pdf" href="{asset(p["pdf"])}" download="{esc(filename)}" aria-label="{esc(DOWNLOAD_LABELS[lang])}: {title}">{esc(pdf_label)} ↓</a>'
    search=esc(' '.join([p['title'],' '.join(p['authors']),p['venue'],str(year),*collaborator_search_names(p)]))
    kindkey={'journal':'Journal article','conference':'Conference paper','preprint':'Preprint'}.get(p['kind'])
    kindlabel=text(kindkey,lang) if kindkey else c['other']
    short_venue=SHORT_VENUES.get(p['venue'],p['venue']) or kindlabel
    publication_date=''
    if p.get('published_date'):
     publication_date=f'<time class="visually-hidden" datetime="{p["published_date"]}">{esc(format_date(p["published_date"],lang))}</time>'
    venue_detail=f'<bdi>{esc(p["venue"])}</bdi> · ' if p['venue'] and short_venue!=p['venue'] else ''
    collaborators=esc(' '.join(person['id'] for person in paper_collaborators(p)))
    cards.append(f'''<article class="paper-card{' no-figure' if not figure else ''}" id="paper-{p['id']}" data-year="{year}" data-kind="{p['kind']}" data-topics="{esc(' '.join(p.get('topics',[])))}" data-search="{search}" data-collaborators="{collaborators}">
<div class="paper-venue"><bdi title="{esc(p['venue'])}">{esc(short_venue)}</bdi> <span class="venue-year">{year}</span>{publication_date}</div>
{figure}<div class="paper-content">
<h2 class="paper-title" dir="auto"><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h2>
<p class="paper-authors" dir="auto">{', '.join(authors)}</p>
<p class="paper-meta">{venue_detail}{esc(kindlabel)}</p>
<div class="paper-actions"><a href="{url}" target="_blank" rel="noopener noreferrer">{esc(c['library'])} ↗</a>{pdf}<button type="button" data-citation="{esc(bibtex(p))}">BibTeX</button></div></div></article>''')
  document=f'''<!DOCTYPE html>
<html lang="{lang}"{' dir="rtl"' if lang=='ar' else ''}>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{c['title']} | FIT-AWE Lab</title><meta name="description" content="{esc(c['description'])}">{favicon('publications/index.html',lang)}{stylesheets('publications/index.html',lang)}{alternates}</head>
<body>{navbar}
<main id="main-content" class="publication-catalog page-shell" data-publication-catalog data-default-title="{esc(c['title'])}" data-count-template="{esc(c['count'])}" data-collaborator-queries="{queries}">
<header class="catalog-header"><h1 id="catalog-title">{c['title']}</h1><nav class="catalog-sources" aria-label="{profile_label}"><a href="https://scholar.google.com/citations?user=UJPH5ioAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a><a href="https://dblp.org/pid/55/1198.html" target="_blank" rel="noopener noreferrer">DBLP ↗</a></nav></header>
<div class="catalog-controls">{primary}<div class="catalog-tools"><div class="catalog-search"><label class="visually-hidden" for="publication-search">{c['search']}</label><input id="publication-search" type="search" placeholder="{esc(c['placeholder'])}" autocomplete="off"></div><details class="catalog-extra-filters"><summary>{compact['more']}</summary><div class="extra-filter-options">{filters}</div></details></div></div>
<div class="catalog-status"><p id="publication-count" role="status" aria-live="polite">{c['count'].replace('{shown}',str(len(papers))).replace('{total}',str(len(papers)))}</p><button id="publication-reset" type="button" hidden>{c['reset']}</button></div>
<p id="publication-empty" hidden>{c['empty']}</p><div class="publication-list">{''.join(cards)}</div>
<p class="catalog-footnote">{c['updated']} {format_date(payload['updated'],lang)}</p></main>
{site_footer}
<dialog id="citation-dialog" aria-labelledby="citation-heading"><h2 id="citation-heading">BibTeX</h2><pre tabindex="0"></pre><div class="citation-actions"><button type="button" data-copy data-success="{esc(c['copied'])}" data-failure="{esc(c['failed'])}">{c['copy']}</button><button type="button" data-close autofocus>{c['close']}</button></div><p role="status"></p></dialog>
<script src="{asset('js/publications.js')}?v={VERSION}" defer></script><script src="{asset('js/navigation.js')}?v={VERSION}" defer></script></body></html>'''
  dest.write_text(document+'\n')
 print(f'Rendered {len(papers)} publications in {len(LABELS)} languages.')
if __name__=='__main__':build()
