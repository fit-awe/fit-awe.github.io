#!/usr/bin/env python3
"""Fail on missing/stale translations, wrong-language links or inconsistent navigation."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup,Comment,Doctype
from build_locales import ROOT, LANGUAGES, PAGES, render

def visible(soup):
 return [str(n).strip() for n in soup.find_all(string=True) if str(n).strip() and not isinstance(n,(Comment,Doctype)) and n.parent.name not in ['script','style']]
def main():
 count=0
 for lang in LANGUAGES:
  for page in PAGES+['publications/index.html']:
   path=ROOT/('' if lang=='en' else lang)/page;s=BeautifulSoup(path.read_text(),'html.parser')
   assert s.html['lang']==lang,(path,'wrong document language')
   assert (s.html.get('dir')=='rtl')==(lang=='ar'),path
   if page in PAGES:
    expected=BeautifulSoup(render(page,lang),'html.parser')
    assert visible(s)==visible(expected),(path,'stale or mixed-language content; rebuild locales')
    for actual,wanted in zip(s.find_all(),expected.find_all()):
     for attr in ['alt','title','aria-label','placeholder']:
      assert actual.get(attr)==wanted.get(attr),(path,attr,'untranslated attribute')
   nav=s.select_one('.navbar')
   if nav:
    assert len(nav.select('.industry-nav-link'))==1,path
    language_links=nav.select('.dropdown-menu a');assert len(language_links)==5,path
    for a in language_links:
     code=a['hreflang'];target=ROOT/('' if code=='en' else code)/page
     assert (path.parent/urlsplit(a['href']).path).resolve()==target.resolve(),(path,'language switch destination')
    for a in s.select('.navbar-nav > li > a[href],.site-footer a[href]'):
     if a['href']=='#':continue
     target=(path.parent/urlsplit(a['href']).path).resolve()
     assert BeautifulSoup(target.read_text(),'html.parser').html['lang']==lang,(path,'cross-language navigation')
   for tag in s.select('[src],[href]'):
    url=urlsplit(tag.get('src',tag.get('href')))
    if url.scheme or url.netloc or not url.path:continue
    target=(path.parent/unquote(url.path)).resolve();assert target.exists(),(path,'missing local asset',target)
    if url.fragment and target.suffix=='.html':
     assert BeautifulSoup(target.read_text(),'html.parser').find(id=url.fragment),(path,'missing anchor',url.fragment)
   count+=1
 print(f'PASS: {count} pages, 5 languages, translation coverage, same-page language switching, navigation and local links.')
if __name__=='__main__':main()
