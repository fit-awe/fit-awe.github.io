#!/usr/bin/env python3
"""Generate translated static pages from English; fail on missing translations."""
import json, os, re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup, Comment, Doctype
from publication_common import author_key, lab_author_keys
from publication_dates import format_date
from site_shell import header, footer, favicon, VERSION
ROOT=Path(__file__).resolve().parents[1]
LANGUAGES={'en':'English','zh':'中文','fr':'Français','ar':'العربية','ja':'日本語'}
PAGES=['index.html','allnews.html','members/index.html','alumni/index.html','teams/index.html','projects/index.html','entrepreneurship/index.html','vacancies/index.html','aboutwebsite.html','404.html','vacancies.html','instrumente.html','pictures/index.html','team/index.html']
TITLES=dict(zip(PAGES,['About','News','Members','Alumni','Members','Publications','Entrepreneurship','Open Positions','About this site','Sorry, but the page you were trying to view does not exist.','Redirecting...','Publications','Publications','Members']))
PAGES.append('awards/index.html')
TITLES['awards/index.html']='Paper Awards'
TITLES['vacancies/index.html']='Join Us'
TITLES['entrepreneurship/index.html']='Industry–Academia Collaboration'
INVARIANTS={'FIT-AWE Lab','FIT-AWE','FIT','AWE','HKUST(GZ) ↗','FIT-AWE / HKUST(GZ)','FIT-AWE Lab · HKUST(GZ)','HCI','XR','E1 · 507','Allan Lab','· Bootstrap · Bootswatch'}
TERMS={'zh':{'now':'至今','summer':'暑期','Remote co-supervision':'远程联合指导'},'fr':{'now':'présent','summer':'été','Remote co-supervision':'Codirection à distance'},'ar':{'now':'الآن','summer':'الصيف','Remote co-supervision':'إشراف مشترك عن بُعد'},'ja':{'now':'現在','summer':'夏季','Remote co-supervision':'遠隔共同指導'}}

def translate(text,lang,dictionary,roster):
 text=text.strip()
 if lang=='en' or not text or text in INVARIANTS or re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',text) or author_key(text) in roster or not re.search('[A-Za-z]',text):return text
 if text in dictionary:return dictionary[text]
 if re.fullmatch(r'[\d/ -]+now',text):return text.replace('now',TERMS[lang]['now'])
 m=re.fullmatch(r'(\d+) publications →',text)
 if m:return m[1]+{'zh':' 篇论文 →','fr':' publications →','ar':' منشورًا →','ja':' 件の論文 →'}[lang]
 if text.endswith(' →'):return translate(text[:-2],lang,dictionary,roster)+' →'
 raise ValueError(f'Missing {lang} translation: {text}')

def render(page,lang,missing=None):
 src=ROOT/page;dest=ROOT/('' if lang=='en' else lang)/page
 s=BeautifulSoup(src.read_text(),'html.parser');s.html['lang']=lang
 if lang=='ar':s.html['dir']='rtl'
 else:s.html.attrs.pop('dir',None)
 dictionary={} if lang=='en' else json.loads((ROOT/f'data/locales/{lang}.json').read_text())
 roster=lab_author_keys()
 def tr(text):
  try:return translate(text,lang,dictionary,roster)
  except ValueError:
   if missing is None:raise
   missing.add(text.strip());return text
 # Shared chrome is rendered once, with page-specific destinations.
 for part in s.select('.navbar,.site-footer'):part.clear()
 for old in s.select('.skip-link'):old.decompose()
 for old in s.select('script[src*="jquery"],script[src*="bootstrap"],link[href*="css/main.css"]'):old.decompose()
 for style in s.select('link[href*="refinements.css"],link[href*="publications.css"],script[src*="navigation.js"]'):
  attr='src' if style.name=='script' else 'href'
  style[attr]=style[attr].split('?')[0]+'?v='+VERSION
 if not s.find(id='main-content'):
  main=s.new_tag('main',id='main-content',attrs={'class':'page-shell'})
  for child in list(s.body.children):
   if getattr(child,'name',None)=='script' or ('navbar' in getattr(child,'attrs',{}).get('class',[])) or ('site-footer' in getattr(child,'attrs',{}).get('class',[])):continue
   main.append(child.extract())
  navbar=s.select_one('.navbar')
  if navbar:navbar.insert_after(main)
  else:s.body.insert(0,main)
 for t in s.select('time[datetime]'):t.string=format_date(t['datetime'],lang)
 def bibliographic(tag):
  return tag.has_attr('data-bibliographic') or tag.find_parent(attrs={'data-bibliographic':True}) is not None
 # Bibliographic author names and company names remain as supplied.
 for n in list(s.find_all(string=True)):
  if isinstance(n,(Comment,Doctype)) or n.parent.name in ['script','style','title'] or not n.strip():continue
  if bibliographic(n.parent) or n.find_parent('time'):continue
  if n.find_parent(class_='alumni-list'):
   text=str(n)
   for a,b in TERMS.get(lang,{}).items():text=re.sub(r'\b'+re.escape(a)+r'\b',b,text)
   n.replace_with(text);continue
  original=str(n);new=tr(original)
  n.replace_with(original[:len(original)-len(original.lstrip())]+new+original[len(original.rstrip()):])
 for tag in s.find_all():
  if bibliographic(tag):continue
  for attr in ['alt','title','aria-label','placeholder']:
   if tag.get(attr):tag[attr]=tr(tag[attr])
 # Keep academic year ranges in chronological order within Arabic labels.
 if lang=='ar':
  for node in list(s.select('.academic-meta')):
   for original in list(node.find_all(string=True)):
    parts=re.split(r'(\d{4}–\d{2,4})',str(original))
    if len(parts)==1:continue
    for part in parts:
     if re.fullmatch(r'\d{4}–\d{2,4}',part):
      isolated=s.new_tag('bdi',dir='ltr');isolated.string=part;original.insert_before(isolated)
     elif part:original.insert_before(part)
    original.extract()
 s.title.string=tr(TITLES[page])+' | FIT-AWE Lab'
 description=s.select_one('meta[name="description"]')
 if description:description['content']=tr(TITLES[page])+' · FIT-AWE Lab · HKUST(GZ)'
 def local_url(url):
  parsed=urlsplit(url)
  if parsed.scheme or parsed.netloc or not parsed.path:return url
  target=(src.parent/parsed.path).resolve();relative=target.relative_to(ROOT)
  if relative.as_posix()=='members/haining-liang':
   target=ROOT/('zh' if lang=='zh' else '')/relative
  elif target.suffix=='.html':
   parts=relative.parts
   if parts[0] in LANGUAGES and parts[0]!='en':relative=Path(*parts[1:])
   target=ROOT/('' if lang=='en' else lang)/relative
  path=os.path.relpath(target,dest.parent)
  if parsed.path.endswith('/'):path+='/'
  return urlunsplit(('','',path,parsed.query,parsed.fragment))
 for tag in s.select('[href],[src]'):
  for attr in ['href','src']:
   if tag.get(attr):tag[attr]=local_url(tag[attr])
 for tag in s.select('meta[http-equiv="refresh"]'):
  a,b=tag['content'].split('url=',1);tag['content']=a+'url='+local_url(b.strip())
 for selector,markup in [('.navbar',header(page,lang)),('.site-footer',footer(page,lang))]:
  part=s.select_one(selector)
  rendered=BeautifulSoup(markup,'html.parser')
  if selector=='.navbar':
   if part:part.decompose()
   s.body.insert(0,rendered.select_one(selector))
   s.body.insert(0,rendered.select_one('.skip-link'))
   continue
  replacement=rendered.select_one(selector)
  if part:part.replace_with(replacement)
  else:s.body.append(replacement)
 # Every page uses the same supplied lab mark, including legacy redirects.
 for old in s.select('link[rel="icon"],link[rel="shortcut icon"]'):old.decompose()
 s.head.append(BeautifulSoup(favicon(page,lang),'html.parser').link)
 # Language alternatives are page-specific, never an unrelated page.
 for old in s.select('link[hreflang]'):old.decompose()
 for code in LANGUAGES:
  path=ROOT/('' if code=='en' else code)/page
  s.head.append(s.new_tag('link',rel='alternate',hreflang=code,href=os.path.relpath(path,dest.parent)))
 return str(s).rstrip()+'\n'

def build():
 from build_content import build as build_content
 build_content()
 # Validate every page before writing any translated file.
 outputs={(page,lang):render(page,lang) for lang in LANGUAGES for page in PAGES}
 for (page,lang),text in outputs.items():
  dest=ROOT/('' if lang=='en' else lang)/page;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
 print(f'Rendered {len(outputs)} pages in {len(LANGUAGES)} languages.')
if __name__=='__main__':build()
