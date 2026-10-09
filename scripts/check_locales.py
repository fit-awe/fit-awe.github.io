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
 members=BeautifulSoup((ROOT/'members/index.html').read_text(),'html.parser')
 alumni_names=[li.get_text(' ',strip=True).split(',')[0] for li in members.select('.members-alumni .alumni-list li')]
 assert alumni_names,'Members must include the alumni roster'
 retired={'teams/index.html':('members/index.html',''),'projects/index.html':('publications/index.html',''),'alumni/index.html':('members/index.html','alumni')}
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
    assert len(nav.select('.navbar-nav > li > a'))==6,(path,'incomplete navigation')
    language_links=nav.select('.dropdown-menu a');assert len(language_links)==5,path
    for a in language_links:
     code=a['hreflang'];target=ROOT/('' if code=='en' else code)/page
     assert (path.parent/urlsplit(a['href']).path).resolve()==target.resolve(),(path,'language switch destination')
    for a in s.select('.navbar-nav > li > a[href],.site-footer a[href]'):
     if a['href']=='#':continue
     target=(path.parent/urlsplit(a['href']).path).resolve()
     assert target not in [(ROOT/('' if lang=='en' else lang)/p).resolve() for p in retired],(path,'retired navigation entry')
     assert BeautifulSoup(target.read_text(),'html.parser').html['lang']==lang,(path,'cross-language navigation')
   if page=='members/index.html':
    assert s.select_one('h2#faculty') and not s.select_one('h2#staff'),(path,'Faculty section missing')
    assert [li.get_text(' ',strip=True).split(',')[0] for li in s.select('.members-alumni .alumni-list li')]==alumni_names,(path,'alumni roster changed')
    assert s.select_one('.members-section-nav a[href="#alumni"]'),(path,'Alumni entry missing')
   if page=='index.html':
    assert len(s.select('.latest-paper'))==6,(path,'latest publications missing')
    assert len(s.select('.news-list li'))==3,(path,'news preview missing')
    updates=s.select_one('main.home-page > aside.home-updates')
    assert updates and len(updates.select('[data-news-id]'))==3,(path,'updates sidebar missing')
    assert updates.find_previous_sibling().get('class')==['about-hero'] and 'home-awards' in updates.find_next_sibling().get('class',[]),(path,'updates must follow photos before awards on narrow screens')
    assert not s.select('.about-media .news-list'),(path,'updates still nested beneath the photo')
    assert len(s.select('.award-summary li'))==3,(path,'award preview missing')
    assert not s.select('.member-card,#newsid'),(path,'retired homepage members/sidebar')
    assert len(s.select('[data-slide]'))==2 and s.select_one('[data-carousel]'),(path,'carousel missing')
    assert not s.select('[data-pause],.carousel-caption'),(path,'retired slideshow labels')
   if page in retired:
    redirect=s.select_one('meta[http-equiv="refresh"]');assert redirect,(path,'legacy redirect missing')
    url=urlsplit(redirect['content'].split('url=',1)[1])
    target,fragment=retired[page]
    assert (path.parent/url.path).resolve()==(ROOT/('' if lang=='en' else lang)/target).resolve(),(path,'wrong redirect destination')
    assert url.fragment==fragment,(path,'wrong redirect section')
   for tag in s.select('[src],[href]'):
    url=urlsplit(tag.get('src',tag.get('href')))
    if url.scheme or url.netloc or not url.path:continue
    target=(path.parent/unquote(url.path)).resolve();assert target.exists(),(path,'missing local asset',target)
    if url.fragment and target.suffix=='.html':
     assert BeautifulSoup(target.read_text(),'html.parser').find(id=url.fragment),(path,'missing anchor',url.fragment)
   count+=1
 print(f'PASS: {count} pages, 5 languages, translation coverage, same-page language switching, navigation and local links.')
if __name__=='__main__':main()
