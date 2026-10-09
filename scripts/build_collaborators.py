"""Render verified faculty collaborators; derive joint papers from the live catalog."""
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from publication_common import ROOT, author_key, esc
from site_shell import asset


def joint_publications(person, papers):
    names = {author_key(name) for name in person['author_names']}
    lead = author_key('Hai-Ning Liang')
    return [paper for paper in papers if paper['title'].strip().casefold() != 'list of contributors'
            and lead in {author_key(a) for a in paper['authors']}
            and names.intersection(author_key(a) for a in paper['authors'])]


def ordered_collaborators(people, papers):
    """Lead with frequent collaborators and selected established field leaders.

    The featured flag is editorial curation, not a citation or impact score.
    Recompute counts on every build so new frequent collaborators move forward.
    """
    def order(person):
        count = len(joint_publications(person, papers))
        priority = count >= 8 or person.get('featured', False)
        return (not priority, -count, person['name'].casefold())
    return sorted(people, key=order)


def build():
    people = json.loads((ROOT / 'data/international-collaborators.json').read_text())['collaborators']
    papers = json.loads((ROOT / 'data/publications.json').read_text())['publications']
    cards = []
    for person in ordered_collaborators(people, papers):
        matches = joint_publications(person, papers)
        if not matches:
            raise ValueError(f'No joint publication for {person["name"]}')
        portrait = person['portrait']
        if portrait:
            visual = f'<img src="{asset("members/index.html", portrait["path"])}" alt="{esc(person["name"])}" width="{portrait["width"]}" height="{portrait["height"]}" loading="lazy" decoding="async">'
        else:
            initials = ''.join(part[0] for part in person['name'].split() if part[0].isalpha())[:2]
            visual = f'<span class="collaborator-initials" aria-hidden="true">{esc(initials)}</span>'
        href = '../publications/index.html?' + urlencode({'q': person['author_names'][0]})
        cards.append(f'''<article class="collaborator-card" data-collaborator-id="{esc(person['id'])}">
<a class="collaborator-photo" href="{esc(person['profile_url'])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(person['name'])}" data-bibliographic>{visual}</a>
<h3 dir="auto" data-bibliographic><a href="{esc(person['profile_url'])}" target="_blank" rel="noopener noreferrer">{esc(person['name'])} <span class="profile-arrow" aria-hidden="true">↗</span></a></h3>
<p class="collaborator-role">{esc(person['role'])}</p>
<p class="collaborator-institution" dir="auto" data-bibliographic>{esc(person['institution'])}</p>
<p class="collaborator-country">{esc(person['country'])}</p>
<a class="collaborator-papers" href="{href}"><bdi data-bibliographic>{len(matches)}</bdi> <span>Joint publications</span> <span aria-hidden="true">→</span></a>
</article>''')
    section = BeautifulSoup('''<section class="members-collaborators" id="international-collaborators" aria-labelledby="collaborators-heading">
<h2 id="collaborators-heading">International Collaborators</h2>
<div class="collaborator-grid">''' + ''.join(cards) + '</div></section>', 'html.parser').section
    source = ROOT / 'members/index.html'
    soup = BeautifulSoup(source.read_text(), 'html.parser')
    existing = soup.find(id='international-collaborators')
    if existing:
        existing.replace_with(section)
    else:
        soup.select_one('.members-alumni').insert_before(section)
    nav = soup.select_one('.members-section-nav')
    if not nav.select_one('a[href="#international-collaborators"]'):
        link = soup.new_tag('a', href='#international-collaborators')
        link.string = 'International Collaborators'
        nav.select_one('a[href="#alumni"]').insert_before(link)
    source.write_text(str(soup).rstrip() + '\n')
    print(f'Rendered {len(people)} international faculty collaborators.')


if __name__ == '__main__':
    build()
