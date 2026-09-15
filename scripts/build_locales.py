#!/usr/bin/env python3
"""Generate translated static pages from English; fail on missing translations."""
import json, os, re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup, Comment, Doctype
from build_publications import author_key, lab_author_keys
ROOT=Path(__file__).resolve().parents[1]
LANGUAGES={'en':'English','zh':'中文','fr':'Français','ar':'العربية','ja':'日本語'}
PAGES=['index.html','allnews.html','members/index.html','alumni/index.html','teams/index.html','projects/index.html','entrepreneurship/index.html','vacancies/index.html','aboutwebsite.html','404.html','vacancies.html','instrumente.html','pictures/index.html','team/index.html']
TITLES=dict(zip(PAGES,['About','News','Members','Alumni','Teams','Projects','Entrepreneurship','Open Positions','About this site','Sorry, but the page you were trying to view does not exist.','Redirecting...','Projects','Projects','Members']))
INVARIANTS={'FIT-AWE Lab','FIT-AWE','FIT-AWE / HKUST(GZ)','FIT-AWE Lab · HKUST(GZ)','HCI','XR','E1 · 507','Allan Lab','· Bootstrap · Bootswatch'}
TERMS={'zh':{'now':'至今','summer':'暑期','Remote co-supervision':'远程联合指导'},'fr':{'now':'présent','summer':'été','Remote co-supervision':'Codirection à distance'},'ar':{'now':'الآن','summer':'الصيف','Remote co-supervision':'إشراف مشترك عن بُعد'},'ja':{'now':'現在','summer':'夏季','Remote co-supervision':'遠隔共同指導'}}

def translate(text,lang,dictionary,roster):
 text=text.strip()
 if lang=='en' or not text or text in INVARIANTS or '@' in text or author_key(text) in roster or not re.search('[A-Za-z]',text):return text
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
 dropdown=s.select_one('.navbar .dropdown')
 if dropdown:dropdown.clear()
 # Bibliographic author names and company names remain as supplied.
 for n in list(s.find_all(string=True)):
  if isinstance(n,(Comment,Doctype)) or n.parent.name in ['script','style','title'] or not n.strip():continue
  if n.find_parent(class_='alumni-list'):
   text=str(n)
   for a,b in TERMS.get(lang,{}).items():text=re.sub(r'\b'+re.escape(a)+r'\b',b,text)
   n.replace_with(text);continue
  original=str(n);new=tr(original)
  n.replace_with(original[:len(original)-len(original.lstrip())]+new+original[len(original.rstrip()):])
 for tag in s.find_all():
  for attr in ['alt','title','aria-label','placeholder']:
   if tag.get(attr):tag[attr]=tr(tag[attr])
 s.title.string=tr(TITLES[page])+' | FIT-AWE Lab'
 description=s.select_one('meta[name="description"]')
 if description:description['content']=tr(TITLES[page])+' · FIT-AWE Lab · HKUST(GZ)'
 def local_url(url):
  parsed=urlsplit(url)
  if parsed.scheme or parsed.netloc or not parsed.path:return url
  target=(src.parent/parsed.path).resolve();relative=target.relative_to(ROOT)
  if target.suffix=='.html':
   parts=relative.parts
   if parts[0] in LANGUAGES and parts[0]!='en':relative=Path(*parts[1:])
   target=ROOT/('' if lang=='en' else lang)/relative
  return urlunsplit(('','',os.path.relpath(target,dest.parent),parsed.query,parsed.fragment))
 for tag in s.select('[href],[src]'):
  for attr in ['href','src']:
   if tag.get(attr):tag[attr]=local_url(tag[attr])
 for tag in s.select('meta[http-equiv="refresh"]'):
  a,b=tag['content'].split('url=',1);tag['content']=a+'url='+local_url(b.strip())
 if dropdown:
  toggle=s.new_tag('a',href='#',attrs={'class':'dropdown-toggle','data-toggle':'dropdown','role':'button','aria-haspopup':'true','aria-expanded':'false'})
  toggle.append(LANGUAGES[lang]+' ');toggle.append(s.new_tag('span',attrs={'class':'caret'}));dropdown.append(toggle)
  menu=s.new_tag('ul',attrs={'class':'dropdown-menu'})
  for code,label in LANGUAGES.items():
   path=ROOT/('' if code=='en' else code)/page
   li=s.new_tag('li');a=s.new_tag('a',href=os.path.relpath(path,dest.parent),hreflang=code,lang=code);a.string=label
   if code==lang:a['aria-current']='page'
   li.append(a);menu.append(li)
  dropdown.append(menu)
 # Language alternatives are page-specific, never an unrelated page.
 for old in s.select('link[hreflang]'):old.decompose()
 for code in LANGUAGES:
  path=ROOT/('' if code=='en' else code)/page
  s.head.append(s.new_tag('link',rel='alternate',hreflang=code,href=os.path.relpath(path,dest.parent)))
 return str(s).rstrip()+'\n'

def build():
 # Validate every page before writing any translated file.
 outputs={(page,lang):render(page,lang) for lang in LANGUAGES for page in PAGES}
 for (page,lang),text in outputs.items():
  dest=ROOT/('' if lang=='en' else lang)/page;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
 for lang in LANGUAGES:
  home=ROOT/('' if lang=='en' else lang)/'index.html'
  dest=home.parent/'publications/index.html'
  doc=BeautifulSoup((dest if dest.exists() else ROOT/'publications/index.html').read_text(),'html.parser')
  template=BeautifulSoup(outputs[('index.html',lang)],'html.parser')
  for selector in ['.navbar','.site-footer']:
   part=template.select_one(selector)
   for a in part.select('a[href]'):
    if a['href']=='#':continue
    if a.get('hreflang'):
     target=ROOT/('' if a['hreflang']=='en' else a['hreflang'])/'publications/index.html'
    else:
     parsed=urlsplit(a['href']);target=(home.parent/parsed.path).resolve()
    fragment=urlsplit(a['href']).fragment
    a['href']=os.path.relpath(target,dest.parent)+('#'+fragment if fragment else '')
    if not a.get('hreflang'):
     a.attrs.pop('aria-current',None)
     if target==dest:a['aria-current']='page'
   doc.select_one(selector).replace_with(part)
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(str(doc)+'\n')
 print(f'Rendered {len(outputs)} pages in {len(LANGUAGES)} languages.')
if __name__=='__main__':build()
