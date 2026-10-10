#!/usr/bin/env python3
"""Verify shared summaries, award links and highlighted authors in all five languages."""
import json
from urllib.parse import parse_qs, urlsplit, unquote
from bs4 import BeautifulSoup
from publication_common import ROOT, author_key, lab_author_keys
from build_collaborators import joint_publications, ordered_collaborators
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
collaborators=json.loads((ROOT/'data/international-collaborators.json').read_text())['collaborators']
image_manifest=ROOT/'data/image-variants.json'
image_variants=json.loads(image_manifest.read_text())['images'] if image_manifest.exists() else {}
assert len({c['id'] for c in collaborators})==len(collaborators)
assert len({author_key(c['name']) for c in collaborators})==len(collaborators)
ordered_people=ordered_collaborators(collaborators,papers)
for person in collaborators:
 assert person['profile_url'].startswith('https://') and person['appointment_source'].startswith('https://')
 assert person['checked_on'] and person['author_names'] and person['evidence_paper_ids']
 matches=joint_publications(person,papers)
 assert matches,(person['id'],'missing coauthor evidence')
 assert set(person['evidence_paper_ids']).issubset(p['id'] for p in matches)
 photo=person['portrait']
 if photo:
  assert (ROOT/photo['path']).is_file() and (ROOT/photo['path']).stat().st_size>0
  assert photo['width']>0 and photo['height']>0 and photo['source_url'] and photo['source_page']
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

def check_award_status(card,award,lang):
 badge=card.select_one('.award-nomination')
 labelled_in_name=award['status']=='nomination' and 'nomination' in award['name'].casefold()
 if labelled_in_name:assert localized(award['name'],lang) in card.select_one('.award-label').get_text(' ',strip=True),(award['id'],lang,'nomination label missing')
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
  check_award_status(card,award,lang)
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
 assert members.select_one('.members-section-nav a[href="#international-collaborators"]')
 collaborators_cards=members.select('.collaborator-card')
 assert [c['data-collaborator-id'] for c in collaborators_cards]==[p['id'] for p in ordered_people]
 catalog=BeautifulSoup((base/'publications/index.html').read_text(),'html.parser')
 query_map=json.loads(catalog.select_one('[data-publication-catalog]')['data-collaborator-queries'])
 for card,person in zip(collaborators_cards,ordered_people):
  assert card.h3.get_text(' ',strip=True).replace(' ↗','')==person['name']
  assert card.select_one('.collaborator-role').text==localized(person['role'],lang)
  assert card.select_one('.collaborator-country').text==localized(person['country'],lang)
  assert card.select_one('.collaborator-institution').text==person['institution']
  assert card.h3.a['href']==person['profile_url'] and card.h3.a.get('target')=='_blank'
  assert {'noopener','noreferrer'}.issubset(card.h3.a['rel'])
  assert bool(card.select_one('img'))==bool(person['portrait'])
  if person['portrait']:
   src=(base/'members'/unquote(urlsplit(card.img['src']).path)).resolve()
   source=person['portrait']['path']
   if card.img.get('data-image-source'):
    assert card.img['data-image-source']==source
    assert src in {(ROOT/v['path']).resolve() for v in image_variants[source]['variants']}
   else:assert src==(ROOT/source).resolve()
   assert card.img['alt']==person['name']
  action=card.select_one('.collaborator-papers')
  assert int(action.bdi.text)==len(joint_publications(person,papers))
  url=urlsplit(action['href'])
  assert (base/'members'/url.path).resolve()==(base/'publications/index.html').resolve()
  assert parse_qs(url.query)['q']==[person['author_names'][0]]
  for name in person['author_names']:assert query_map[name]==person['id']
  actual={c['id'].removeprefix('paper-') for c in catalog.select('.paper-card') if person['id'] in c['data-collaborators'].split()}
  assert actual=={p['id'] for p in joint_publications(person,papers)},(person['id'],lang,'author filter or count mismatch')
print(f'PASS: shared news, {len(awards)} sourced awards, latest 6 papers and member/alumni highlighting in 5 languages; {len(member_names)} members, {alumni_count} alumni entries and {len(collaborators)} sourced faculty collaborators with exact author filters.')
