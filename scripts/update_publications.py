#!/usr/bin/env python3
"""Monthly, additive bibliography sync. No scraping bypass and no deletion on failure."""
import argparse, hashlib, json, re, time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlsplit, quote
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
PROFILE='https://scholar.google.com/citations?hl=en&user=UJPH5ioAAAAJ'
QUERY='''PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT DISTINCT ?pub ?title ?year ?venue ?kind ?doi ?url ?author ?position WHERE {
 ?pub dblp:authoredBy <https://dblp.org/pid/55/1198>; dblp:title ?title;
      dblp:yearOfPublication ?year; dblp:bibtexType ?kind; dblp:hasSignature ?sig .
 ?sig a dblp:AuthorSignature; dblp:signatureDblpName ?author; dblp:signatureOrdinal ?position .
 OPTIONAL {?pub dblp:publishedIn ?venue} OPTIONAL {?pub dblp:doi ?doi}
 OPTIONAL {?pub dblp:primaryDocumentPage ?url}
} ORDER BY ?pub ?position'''

def normalized(text):return re.sub(r'[^\w]','',text.casefold())
def doi_key(value):return re.sub(r'^https?://(?:dx\.)?doi.org/','',value or '',flags=re.I).lower().strip()
def base_record(title,authors,year,venue,kind,url,source,doi=''):
 return dict(id=hashlib.sha256(source.encode()).hexdigest()[:12],title=title.rstrip('.'),authors=authors,year=int(year),venue=venue,kind=kind,doi=doi_key(doi),url=url,sources=[source],urls=[url],image=None,pdf=None,oa_pdfs=[],topics=[])
def topic_tags(title):
 # Conservative title-based suggestions; curated tags are never overwritten.
 rules={'eye-tracking':r'eye.?track|gaze|fixation|saccad','accessibility':r'accessib|disabil|older adult|elder|cybersick|motion sickness|visually impair','games':r'\bgame|gaming|exergam|gamif','web3d':r'web.?based.{0,25}(3d|virtual)|webxr|webgl','experience':r'virtual reality|augmented reality|mixed reality|user experience|interaction|immersive|\bVR\b','applications':r'education|learning|rehabilit|health|medical|training|driv|museum|therapy'}
 return [key for key,pattern in rules.items() if re.search(pattern,title,re.I)]

def parse_dblp(payload):
 groups={}
 for row in payload['results']['bindings']:
  row={k:v['value'] for k,v in row.items()};source=row['pub'];kind=row['kind'].rsplit('#',1)[-1]
  if kind not in ['Article','Inproceedings','InProceedings','Phdthesis','PhdThesis','Mastersthesis','Book','Incollection']:continue
  g=groups.setdefault(source,{'row':row,'authors':{}});g['authors'][int(row['position'])]=re.sub(r' \d{4}$','',row['author'])
 records=[]
 for source,g in groups.items():
  r=g['row'];positions=sorted(g['authors'])
  if positions!=list(range(1,len(positions)+1)):raise ValueError('Incomplete DBLP author order: '+source)
  url=r.get('doi') or r.get('url') or source
  typ=r['kind'].rsplit('#',1)[-1].lower();kind='conference' if typ=='inproceedings' else 'journal' if typ=='article' else 'other'
  if '/journals/corr/' in source:kind='preprint'
  paper=base_record(r['title'],[g['authors'][p] for p in positions],r['year'],r.get('venue',''),kind,url,source,r.get('doi',''))
  paper['topics']=topic_tags(paper['title']);records.append(paper)
 if not records:raise ValueError('DBLP returned no valid records; existing catalog is protected')
 return records

def fetch_dblp(session):
 r=session.get('https://sparql.dblp.org/sparql',params={'query':QUERY,'format':'json'},headers={'Accept':'application/sparql-results+json'},timeout=90);r.raise_for_status()
 return parse_dblp(r.json())

def scholar_rows(html):
 soup=BeautifulSoup(html,'html.parser')
 if not soup.select_one('#gsc_a_b'):raise ValueError('Scholar blocked or unexpected page; no records removed')
 return soup,soup.select('#gsc_a_b .gsc_a_tr')

def verify_scholar_record(session,paper):
 """Require matching Crossref metadata before automatically publishing Scholar-only items."""
 if paper['doi']:
  response=session.get('https://api.crossref.org/works/'+quote(paper['doi'],safe=''),timeout=25)
 else:
  response=session.get('https://api.crossref.org/works',params={'query.title':paper['title'],'rows':3},timeout=25)
 response.raise_for_status();message=response.json()['message']
 candidates=[message] if paper['doi'] else message.get('items',[])
 for item in candidates:
  title=(item.get('title') or [''])[0]
  if normalized(title)!=normalized(paper['title']):continue
  types={'journal-article':'journal','proceedings-article':'conference','posted-content':'preprint','book-chapter':'other'}
  if item.get('type') not in types:continue
  authors=[' '.join(filter(None,[a.get('given'),a.get('family')])) for a in item.get('author',[])]
  if not authors or any(not a for a in authors):continue
  # Exclude unrelated records accidentally attached to the Scholar profile.
  if not any(normalized(a)=='hainingliang' for a in authors):continue
  canonical=base_record(title,authors,item['published']['date-parts'][0][0],(item.get('container-title') or [''])[0],types[item['type']],'https://doi.org/'+item['DOI'],paper['sources'][0],item['DOI'])
  canonical['sources'].append('https://api.crossref.org/works/'+quote(item['DOI'],safe=''))
  canonical['topics']=topic_tags(title)
  return canonical
 return None

def fetch_scholar(session,existing,report):
 known={normalized(p['title']) for p in existing};records=[];seen=set()
 for offset in range(0,2000,100):
  r=session.get(PROFILE,params={'cstart':offset,'pagesize':100},timeout=30);r.raise_for_status();soup,rows=scholar_rows(r.text)
  if not rows:break
  for row in rows:
   a=row.select_one('.gsc_a_at')
   if not a:continue
   title=a.get_text(' ',strip=True);source=urljoin(PROFILE,a['href'])
   if source in seen:raise ValueError('Scholar repeated a page; pagination incomplete')
   seen.add(source)
   if normalized(title) in known:continue
   time.sleep(1)
   detail=session.get(source,timeout=30);detail.raise_for_status();doc=BeautifulSoup(detail.text,'html.parser')
   fields={}
   for item in doc.select('.gs_scl'):
    field=item.select_one('.gsc_oci_field');value=item.select_one('.gsc_oci_value')
    if field and value:fields[field.get_text(' ',strip=True)]=value.get_text(' ',strip=True)
   link=doc.select_one('a.gsc_oci_title_link');authors=fields.get('Authors','');year=re.search(r'\b(?:19|20)\d{2}\b',fields.get('Publication date',''))
   if not link or not year or not authors or '...' in authors or '…' in authors:
    report['pending'].append({'title':title,'source':source,'reason':'Incomplete Scholar metadata'});continue
   url=link['href'];host=urlsplit(url).hostname or ''
   if urlsplit(url).scheme not in ['http','https'] or host.endswith('google.com'):
    report['pending'].append({'title':title,'source':source,'reason':'Missing external publication destination'});continue
   kind='journal' if 'Journal' in fields else 'conference' if 'Conference' in fields else 'other'
   venue=fields.get('Journal',fields.get('Conference',fields.get('Publisher','')))
   paper=base_record(title,[a.strip() for a in authors.split(',')],year[0],venue,kind,url,source,url if 'doi.org/' in url else '')
   try:verified=verify_scholar_record(session,paper)
   except (requests.RequestException,ValueError,KeyError,TypeError):verified=None
   if verified:
    records.append(verified);known.add(normalized(verified['title']))
   else:report['pending'].append({'title':title,'source':source,'reason':'No matching scholarly Crossref record with complete author metadata'})
  more=soup.select_one('#gsc_bpf_more')
  if len(rows)<100 or (more and more.has_attr('disabled')):break
  time.sleep(1)
 else:raise ValueError('Scholar exceeded pagination bound')
 return records

def merge(existing,incoming):
 added=[]
 for new in incoming:
  match=next((p for p in existing if set(p['sources'])&set(new['sources']) or (new['doi'] and doi_key(p.get('doi'))==new['doi']) or normalized(p['title'])==normalized(new['title'])),None)
  if match:
   match['sources']=list(dict.fromkeys(match['sources']+new['sources']))
   match['urls']=list(dict.fromkeys(match.get('urls',[])+new['urls']))
   # Promote a known preprint to its publisher record, keeping images and curated tags.
   if match['kind']=='preprint' and new['kind'] in ['journal','conference']:
    for field in ['title','authors','year','venue','kind','doi','url']:match[field]=new[field]
  else:existing.append(new);added.append(new['id'])
 return added

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
 path=ROOT/'data/publications.json';payload=json.loads(path.read_text());before=json.dumps(payload,sort_keys=True);papers=payload['publications']
 report={'checked':date.today().isoformat(),'sources':{},'added':[],'pending':[]}
 session=requests.Session();session.headers['User-Agent']='FIT-AWE-Website-Monthly-Sync/1.0'
 valid=0
 for name,fetch in [('dblp',lambda:fetch_dblp(session)),('google_scholar',lambda:fetch_scholar(session,papers,report))]:
  try:
   incoming=fetch();added=merge(papers,incoming);report['added']+=added;valid+=1
   report['sources'][name]={'status':'ok','records':len(incoming),'added':len(added)}
  except (requests.RequestException,ValueError,KeyError,TypeError) as e:
   # No credentials or fetched HTML in logs.
   report['sources'][name]={'status':'unavailable','reason':type(e).__name__+': '+str(e).split('?')[0][:160]}
 reportdir=ROOT/'reports';reportdir.mkdir(exist_ok=True)
 report['new_publications']=[p for p in papers if p['id'] in report['added']]
 (reportdir/'publication-update.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report['sources'],ensure_ascii=False))
 if not valid:raise SystemExit('Both sources unavailable. No catalog update was written.')
 payload['sources']['dblp']['records']=len({s for p in papers for s in p['sources'] if s.startswith('https://dblp.org/rec/')})
 if json.dumps(payload,sort_keys=True)!=before:
  papers.sort(key=lambda p:(-p['year'],p['title'].casefold()));payload['updated']=date.today().isoformat()
  if not args.dry_run:path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
 print(f"{'DRY RUN: ' if args.dry_run else ''}{len(report['added'])} new publications; {len(papers)} total")
if __name__=='__main__':main()
