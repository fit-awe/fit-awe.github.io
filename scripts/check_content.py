#!/usr/bin/env python3
"""Verify shared summaries, award links and highlighted authors in all five languages."""
import json
from bs4 import BeautifulSoup
from publication_common import ROOT, author_key, lab_author_keys
from publication_dates import latest_publications, format_date
from site_shell import LANGUAGES, text as localized

papers=json.loads((ROOT/'data/publications.json').read_text())['publications']
by_id={p['id']:p for p in papers}
news=sorted(json.loads((ROOT/'data/news.json').read_text()),key=lambda a:a['date'],reverse=True)
awards=sorted(json.loads((ROOT/'data/awards.json').read_text()),key=lambda a:a['date'],reverse=True)
roster=lab_author_keys()
source_members=BeautifulSoup((ROOT/'members/index.html').read_text(),'html.parser')
member_names=[c.h4.text for c in source_members.select('.member-card')]
alumni_count=len(source_members.select('.members-alumni .alumni-list li'))
assert len({a['id'] for a in awards})==len(awards)
for award in awards:
 assert award['paper_id'] in by_id
 assert award['status'] in ['award','nomination','finalist']
 assert award['source'].startswith('https://') and award['affiliation_sources']

badge_text={
 'en':{'nomination':'Nomination','finalist':'Finalist'},
 'zh':{'nomination':'提名','finalist':'决赛入围'},
 'fr':{'nomination':'Nomination','finalist':'Finaliste'},
 'ar':{'nomination':'ترشيح','finalist':'متأهل للنهائيات'},
 'ja':{'nomination':'ノミネート','finalist':'ファイナリスト'},
}

def check_award_status(card,award,lang,compact=False):
 badge=card.select_one('.award-nomination')
 labelled_in_name=compact and award['status']=='nomination' and 'nomination' in award['name'].casefold()
 if award['status']=='award' or labelled_in_name:assert badge is None
 else:assert badge and badge.text==badge_text[lang][award['status']],(award['id'],lang,'incorrect award status')

for lang in LANGUAGES:
 base=ROOT/('' if lang=='en' else lang)
 home=BeautifulSoup((base/'index.html').read_text(),'html.parser')
 latest=home.select('.latest-paper')
 assert [c['data-paper-id'] for c in latest]==[p['id'] for p in latest_publications(papers)]
 assert [c['data-news-id'] for c in home.select('[data-news-id]')]==[n['id'] for n in news[:3]]
 assert [c['data-award-id'] for c in home.select('[data-award-id]')]==[a['id'] for a in awards[:3]]
 for card,award in zip(home.select('[data-award-id]'),awards[:3]):check_award_status(card,award,lang)
 fullnews=BeautifulSoup((base/'allnews.html').read_text(),'html.parser')
 assert [c['data-news-id'] for c in fullnews.select('[data-news-id]')]==[n['id'] for n in news]
 assert [c.text for c in fullnews.select('time')]==[format_date(n['date'],lang) for n in news]
 full=BeautifulSoup((base/'awards/index.html').read_text(),'html.parser')
 cards=full.select('.award-card')
 assert [c['data-award-id'] for c in cards]==[a['id'] for a in awards]
 for card,award in zip(cards,awards):
  assert card['data-paper-id']==award['paper_id']
  assert card['data-status']==award['status']
  assert award['source'] in [a['href'] for a in card.select('a')]
  source=card.select_one('.award-label > a')
  assert source['href']==award['source']
  assert ''.join(source.find_all(string=True,recursive=False)).strip()==localized(award['name'],lang)
  assert card.select_one('.award-venue bdi').text==award['venue']
  assert not card.select('.paper-figure,.paper-authors'), 'Awards should prioritize venue, prize and paper'
  assert card.select_one('time').text==format_date(award['date'],lang)
  check_award_status(card,award,lang,compact=True)
 for card in latest+cards:
  p=by_id[card['data-paper-id']]
  assert card.select_one('.paper-title a').text==p['title']
  assert card.select_one('.paper-title a')['href']==p['url']
 for card in latest:
  p=by_id[card['data-paper-id']]
  authors=card.select_one('.paper-authors')
  assert authors.text==', '.join(p['authors'])
  assert [a.text for a in authors.select('strong')]==[a for a in p['authors'] if author_key(a) in roster]
  figure=card.select_one('.paper-figure')
  assert bool(figure)==bool(p.get('image'))
  if figure:assert figure['href']==p['url']
 members=BeautifulSoup((base/'members/index.html').read_text(),'html.parser')
 assert not members.select('img[src$="rock.jpg"]')
 assert [c.h4.text for c in members.select('.member-card')]==member_names
 assert len(members.select('.members-alumni .alumni-list li'))==alumni_count
print(f'PASS: shared news, {len(awards)} sourced awards, latest 6 papers and member/alumni highlighting in 5 languages; {len(member_names)} members and {alumni_count} alumni entries.')
