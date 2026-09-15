#!/usr/bin/env python3
"""Check publication data, generated pages, and local assets before upload."""
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs
from bs4 import BeautifulSoup
from build_publications import author_key, lab_author_keys
roster=lab_author_keys()
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/publications.json').read_text())
topics=json.loads((ROOT/'data/research-topics.json').read_text())
topic_ids={topic['id'] for topic in topics}
assert len(topic_ids)==6
papers=data['publications'];ids=[p['id'] for p in papers]
assert len(ids)==len(set(ids)), 'Duplicate publication IDs'
dois=[p['doi'].lower() for p in papers if p.get('doi')]
assert len(dois)==len(set(dois)), 'Duplicate DOIs'
dblp={s for p in papers for s in p['sources'] if s.startswith('https://dblp.org/rec/')}
assert len(dblp)==data['sources']['dblp']['records'], 'Incomplete DBLP import'
for paper in papers:
 assert isinstance(paper['topics'],list) and set(paper['topics'])<=topic_ids
 assert len(paper['topics'])==len(set(paper['topics']))
 assert paper['title'] and paper['authors'] and 1900<paper['year']<2100
 assert urlsplit(paper['url']).scheme in ['https','http'], paper['title']
 if paper.get('image'):assert (ROOT/paper['image']['path']).is_file(), paper['title']
 if paper.get('pdf'):assert (ROOT/paper['pdf']).is_file(), paper['title']
for lang in ['', 'zh', 'fr', 'ar', 'ja']:
 path=ROOT/lang/'publications/index.html';soup=BeautifulSoup(path.read_text(),'html.parser')
 cards=soup.select('.paper-card');assert len(cards)==len(papers)
 assert len(soup.select('#citation-dialog'))==1
 for card,paper in zip(cards,papers):
  assert card['id']=='paper-'+paper['id']
  assert set(card['data-topics'].split())==set(paper['topics'])
  assert card.select_one('.paper-title a')['href']==paper['url']
  authors=card.select_one('.paper-authors')
  assert authors.get_text()==', '.join(paper['authors']), 'Author spelling/order changed'
  assert [a.text for a in authors.select('strong')]==[a for a in paper['authors'] if author_key(a) in roster], 'Member/alumni highlighting mismatch'
  image=card.select_one('.paper-figure')
  if image:assert image['href']==paper['url']
 project=BeautifulSoup((ROOT/lang/'projects/index.html').read_text(),'html.parser')
 links=project.select('.project-topic-link')
 assert len(links)==6
 for link,topic in zip(links,topics):
  assert parse_qs(urlsplit(link['href']).query)['topic']==[topic['id']]
  expected=sum(topic['id'] in paper['topics'] for paper in papers)
  assert str(expected) in link.select_one('.project-topic-count').text
  assert (ROOT/lang/'projects'/urlsplit(link['href']).path).resolve()==path.resolve()
 for tag in soup.select('[src], [href]'):
  url=tag.get('src',tag.get('href'));parsed=urlsplit(url)
  if parsed.scheme or parsed.netloc or not parsed.path:continue
  assert (path.parent/unquote(parsed.path)).exists(), str(path)+': '+url
assert BeautifulSoup((ROOT/'index.html').read_text(),'html.parser').html['lang']=='en', 'Default homepage must be English'
print(f'PASS: {len(papers)} publications, {len(dblp)} DBLP source records, 5 languages, matching title/image destinations, no missing local assets.')
