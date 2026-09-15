#!/usr/bin/env python3
"""Render the shared publication catalog into four ready-to-host HTML pages.
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
def esc(value): return html.escape(str(value), quote=True)
def author_key(name):
 # Ignore typographic differences and parenthetical nicknames, not name order.
 name=re.sub(r'\([^)]*\)', '', name)
 return ''.join(c for c in unicodedata.normalize('NFKD',name).casefold() if c.isalpha())
def lab_author_keys():
 members=BeautifulSoup((ROOT/'members/index.html').read_text(),'html.parser')
 alumni=BeautifulSoup((ROOT/'alumni/index.html').read_text(),'html.parser')
 names=[tag.get_text(' ',strip=True) for tag in members.select('#gridid h4')]
 names.extend(tag.get_text(' ',strip=True).split(',')[0] for tag in alumni.select('.alumni-list li'))
 return {author_key(name) for name in names if name.strip()}
def bibtex(p):
 typ='inproceedings' if p['kind']=='conference' else ('misc' if p['kind']=='preprint' else 'article')
 def safe(t):return str(t).replace('\\','\\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
 fields=[('title',p['title']),('author',' and '.join(p['authors'])),('year',p['year'])]
 if p['venue']:fields.append(('booktitle' if typ=='inproceedings' else 'journal',p['venue']))
 if p.get('doi'):fields.append(('doi',p['doi']))
 fields.append(('url',p['url']))
 return '@'+typ+'{fitawe'+p['id']+',\n'+',\n'.join('  '+k+' = {'+(str(v) if k in ['doi','url'] else safe(v))+'}' for k,v in fields)+'\n}'
def build():
 payload=json.loads(DATA.read_text());papers=payload['publications']
 lab_authors=lab_author_keys()
 years=sorted({p['year'] for p in papers},reverse=True)
 topics=json.loads((ROOT/'data/research-topics.json').read_text())
 for lang,c in LABELS.items():
  dest=ROOT/('' if lang=='en' else lang)/'publications/index.html'
  old=BeautifulSoup(dest.read_text(),'html.parser')
  navbar=str(old.select_one('.navbar'));footer=str(old.select_one('.site-footer'))
  def asset(path):return quote(os.path.relpath(ROOT/path,dest.parent),safe='/')
  options=''.join(f'<option value="{year}">{year}</option>' for year in years)
  kinds=''.join(f'<option value="{kind}">{c[kind]}</option>' for kind in ['journal','conference','preprint','other'])
  topic_options=''.join(f'<option value="{t["id"]}">{esc(t["labels"][lang])}</option>' for t in topics)
  profile_label={'en':'Publication profiles','zh':'学术资料页','fr':'Profils de recherche','ar':'الملفات البحثية','ja':'学術プロフィール'}[lang]
  research_label={'en':'RESEARCH','zh':'研究成果','fr':'RECHERCHE','ar':'الأبحاث','ja':'研究成果'}[lang]
  alternates=''.join('<link rel="alternate" hreflang="'+code+'" href="'+asset(('' if code=='en' else code+'/')+'publications/index.html')+'">' for code in LABELS)
  sections=[]
  for year in years:
   cards=[]
   for p in [p for p in papers if p['year']==year]:
    url=esc(p['url']);title=esc(p['title']);figure=''
    if p.get('image'):
     figure=f'<a class="paper-figure" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{title}"><img src="{asset(p["image"]["path"])}" alt="{esc(c["figure"])} {title}" loading="lazy" decoding="async" width="448" height="296"></a>'
    authors=[]
    for author in p['authors']:
     a=esc(author)
     if author_key(author) in lab_authors:a=f'<strong>{a}</strong>'
     authors.append(a)
    pdf=f'<a href="{asset(p["pdf"])}" target="_blank" rel="noopener noreferrer">PDF ↓</a>' if p.get('pdf') else ''
    search=esc(' '.join([p['title'],' '.join(p['authors']),p['venue'],str(year)]))
    kindlabel=c.get(p['kind'],c['other'])
    cards.append(f'''<article class="paper-card{' no-figure' if not figure else ''}" id="paper-{p['id']}" data-year="{year}" data-kind="{p['kind']}" data-topics="{esc(' '.join(p.get('topics',[])))}" data-search="{search}">
{figure}<div class="paper-content"><p class="paper-meta">{esc(kindlabel)} · <bdi>{esc(p['venue'])}</bdi></p>
<h3 class="paper-title" dir="auto"><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
<p class="paper-authors" dir="auto">{', '.join(authors)}</p>
<div class="paper-actions"><a href="{url}" target="_blank" rel="noopener noreferrer">{esc(c['library'])} ↗</a>{pdf}<button type="button" data-citation="{esc(bibtex(p))}">BibTeX</button></div></div></article>''')
   sections.append(f'<section class="publication-year-group" aria-labelledby="year-{year}"><h2 id="year-{year}" class="publication-year-title">{year}</h2>'+''.join(cards)+'</section>')
  document=f'''<!DOCTYPE html>
<html lang="{lang}"{' dir="rtl"' if lang=='ar' else ''}>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{c['title']} | FIT-AWE Lab</title><meta name="description" content="{esc(c['description'])}"><link rel="stylesheet" href="{asset('css/main.css')}"><link rel="stylesheet" href="{asset('css/refinements.css')}?v=20260915-nav2"><link rel="stylesheet" href="{asset('css/publications.css')}">{alternates}</head>
<body>{navbar}
<main class="publication-catalog" data-publication-catalog data-default-title="{esc(c['title'])}" data-count-template="{esc(c['count'])}">
<header class="catalog-header"><div><p class="catalog-eyebrow">FIT-AWE / {research_label}</p><h1 id="catalog-title">{c['title']}</h1><p class="catalog-description">{c['description']}</p></div><nav class="catalog-sources" aria-label="{profile_label}"><a href="https://scholar.google.com/citations?user=UJPH5ioAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a><a href="https://dblp.org/pid/55/1198.html" target="_blank" rel="noopener noreferrer">DBLP ↗</a></nav></header>
<div class="catalog-controls"><div class="catalog-search"><label for="publication-search">{c['search']}</label><input id="publication-search" type="search" placeholder="{esc(c['placeholder'])}" autocomplete="off"></div><div class="catalog-topic"><label for="publication-topic">{c['topic']}</label><select id="publication-topic"><option value="">{c['all_topics']}</option>{topic_options}</select></div><div><label for="publication-year">{c['year']}</label><select id="publication-year"><option value="">{c['all']}</option>{options}</select></div><div><label for="publication-kind">{c['kind']}</label><select id="publication-kind"><option value="">{c['all_types']}</option>{kinds}</select></div></div>
<div class="catalog-status"><p id="publication-count" role="status" aria-live="polite">{c['count'].replace('{shown}',str(len(papers))).replace('{total}',str(len(papers)))}</p><button id="publication-reset" type="button" hidden>{c['reset']}</button></div>
<p id="publication-empty" hidden>{c['empty']}</p>{''.join(sections)}
<p class="catalog-footnote">{c['updated']} {payload['updated']}</p></main>
{footer}
<dialog id="citation-dialog" aria-labelledby="citation-heading"><h2 id="citation-heading">BibTeX</h2><pre tabindex="0"></pre><div class="citation-actions"><button type="button" data-copy data-success="{esc(c['copied'])}" data-failure="{esc(c['failed'])}">{c['copy']}</button><button type="button" data-close autofocus>{c['close']}</button></div><p role="status"></p></dialog>
<script src="{asset('js/jquery.min.js')}"></script><script src="{asset('js/bootstrap.min.js')}"></script><script src="{asset('js/publications.js')}" defer></script><script src="{asset('js/navigation.js')}?v=20260915-nav2" defer></script></body></html>'''
  dest.write_text(document+'\n')
  project_path=dest.parent.parent/'projects/index.html'
  project=BeautifulSoup(project_path.read_text(),'html.parser')
  topic_list=project.select_one('.project-topics')
  topic_list.clear()
  for topic in topics:
   total=sum(topic['id'] in paper.get('topics',[]) for paper in papers)
   item=project.new_tag('li')
   link=project.new_tag('a',href='../publications/index.html?topic='+topic['id'])
   link['class']='project-topic-link'
   title=project.new_tag('strong');title.string=topic['labels'][lang];link.append(title)
   count=project.new_tag('span');count['class']='project-topic-count';count.string=c['topic_count'].replace('{count}',str(total))+' →';link.append(count)
   item.append(link);topic_list.append(item)
  project_path.write_text(str(project).rstrip()+'\n')
 print(f'Rendered {len(papers)} publications in {len(LABELS)} languages.')
if __name__=='__main__':build()
