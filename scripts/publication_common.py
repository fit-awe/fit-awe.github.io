"""Shared citation and member highlighting for every publication view."""
import html, json, re, unicodedata
from pathlib import Path
from functools import lru_cache
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
def esc(value): return html.escape(str(value), quote=True)
def author_key(name):
 # Ignore typographic differences and parenthetical nicknames, not name order.
 name=re.sub(r'\([^)]*\)', '', name)
 return ''.join(c for c in unicodedata.normalize('NFKD',name).casefold() if c.isalpha())
@lru_cache(None)
def collaborator_records():
 path=ROOT/'data/international-collaborators.json'
 if not path.exists():return []
 return json.loads(path.read_text())['collaborators']
def collaborator_queries():
 return {name:person['id'] for person in collaborator_records() for name in person['author_names']}
def paper_collaborators(paper):
 if paper['title'].strip().casefold()=='list of contributors':return []
 keys={author_key(a) for a in paper['authors']}
 if author_key('Hai-Ning Liang') not in keys:return []
 return [person for person in collaborator_records() if keys.intersection(author_key(a) for a in person['author_names'])]
def collaborator_search_names(paper):
 return [person['author_names'][0] for person in paper_collaborators(paper)]
def lab_author_keys():
 members=BeautifulSoup((ROOT/'members/index.html').read_text(),'html.parser')
 names=[tag.get_text(' ',strip=True) for tag in members.select('.member-card h4')]
 names.extend(tag.get_text(' ',strip=True).split(',')[0] for tag in members.select('.members-alumni .alumni-list li'))
 return {author_key(name) for name in names if name.strip()}
def bibtex(p):
 typ='inproceedings' if p['kind']=='conference' else ('misc' if p['kind']=='preprint' else 'article')
 def safe(t):return str(t).replace('\\','\\textbackslash{}').replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
 fields=[('title',p['title']),('author',' and '.join(p['authors'])),('year',p['year'])]
 if p['venue']:fields.append(('booktitle' if typ=='inproceedings' else 'journal',p['venue']))
 if p.get('doi'):fields.append(('doi',p['doi']))
 fields.append(('url',p['url']))
 return '@'+typ+'{fitawe'+p['id']+',\n'+',\n'.join('  '+k+' = {'+(str(v) if k in ['doi','url'] else safe(v))+'}' for k,v in fields)+'\n}'

def authors_html(paper):
 roster=lab_author_keys()
 return ", ".join(f"<strong>{esc(a)}</strong>" if author_key(a) in roster else esc(a) for a in paper["authors"])
