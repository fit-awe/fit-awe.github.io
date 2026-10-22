"""Stable, portable PDF download names. Existing URLs and PDF bytes are untouched."""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

VENUES = {
    '32nd ACM Symposium on Virtual Reality Software and Technology': 'VRST',
    'ACM Trans. Comput. Hum. Interact.': 'TOCHI', 'ACM Trans. Graph.': 'TOG',
    'Artif. Intell. Rev.': 'AIR', 'Behav. Inf. Technol.': 'BIT',
    'CHI Extended Abstracts': 'CHIEA', 'CHI PLAY': 'CHIPlay',
    'CHI PLAY (Companion)': 'CHIPlayCompanion', 'CHIRA (2)': 'CHIRA',
    'CoRR': 'arXiv', 'Comput. Animat. Virtual Worlds': 'CAVW',
    'Creativity & Cognition': 'CC', 'E-HEALTH': 'EHealth',
    'Frontiers Virtual Real.': 'FrontVR', 'HCI (47)': 'HCII',
    'Hum. centric Comput. Inf. Sci.': 'HCIS',
    'IEEE Computer Graphics and Applications': 'CGandA',
    'IEEE Trans. Games': 'TGames', 'IEEE Trans. Haptics': 'ToH',
    'IEEE Trans. Vis. Comput. Graph.': 'TVCG', 'Inf. Fusion': 'InformationFusion',
    'Int. J. Hum. Comput. Interact.': 'IJHCI', 'Int. J. Hum. Comput. Stud.': 'IJHCS',
    'Intelligent Buildings International': 'IBI',
    'International Journal of Human-Computer Interaction': 'IJHCI',
    'J. Multimodal User Interfaces': 'JMUI', 'J. Univers. Comput. Sci.': 'JUCS',
    'J. Vis.': 'JOV', 'Mobile HCI': 'MobileHCI',
    'Multimodal Technol. Interact.': 'MTI', 'New Ideas in Psychology': 'NIP',
    'PG (Short Papers, Posters, and Work-in-Progress Papers)': 'PGShort',
    'Pers. Ubiquitous Comput.': 'PUC',
    'Proc. ACM Comput. Graph. Interact. Tech.': 'PACMCGIT',
    'Proc. ACM Hum. Comput. Interact.': 'PACMHCI', 'Proc. IEEE': 'PIEEE',
    'RO-MAN': 'ROMAN', 'SAXR@CHI': 'SAXRCHI',
    "SIGGRAPH ASIA Educator's Forum": 'SIGGRAPHAsiaEF',
    'Smart Learn. Environ.': 'SLE', 'Univers. Access Inf. Soc.': 'UAIS',
    'VISIGRAPP (1): GRAPP, HUCAPP, IVAPP': 'VISIGRAPP',
    'VLDB Workshops': 'VLDBW', 'VR Workshops': 'VRW',
    'Virtual Real.': 'VirtualReality', 'Vis. Comput.': 'VisualComputer',
    'ISMAR Adjunct': 'ISMARAdjunct', 'ISMAR-Adjunct': 'ISMARAdjunct',
}
STOP = set('a an the of for and in on to with by from as at through using based '
           'exploring exploration evaluation evaluating empirical analysis study '
           'design development effects effect impact investigating understanding '
           'new approach towards techniques technique methods method'.split())
OVERRIDES = {
    'xr-window-placement-2026': ('ISS', 'WindowPlacement'),
    'scalecue-wim-2026': ('VRST', 'ScaleCueWIM'),
}
LABEL_RE = re.compile(r'[A-Za-z][A-Za-z0-9]*-[A-Za-z][A-Za-z0-9]*\d{2}-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*')

def ascii_text(value):
    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode()

def compact(value):
    return ''.join(w if w.isupper() or any(c.isupper() for c in w[1:]) else w[:1].upper()+w[1:]
                   for w in re.findall(r'[A-Za-z0-9]+', ascii_text(value)))

def candidate(paper):
    override = OVERRIDES.get(paper['id'])
    venue = override[0] if override else VENUES.get(paper['venue'], paper['venue'])
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', venue):
        raise ValueError('Add a verified venue code: '+paper['venue'])
    # Source author order/spelling stays intact. Override unusual family names explicitly.
    name = paper.get('download_surname') or paper['authors'][0].split(',')[0].split()[-1]
    surname = compact(name)
    if not surname or not surname[0].isalpha():
        raise ValueError('Provide download_surname: '+paper['id'])
    title = paper['title']
    prefix = title.split(':', 1)[0]
    if override:
        short = override[1]
    elif ':' in title and len(prefix.split()) <= 3 and len(prefix) <= 28 and prefix.lower() not in {'editorial', 'correction to'}:
        short = compact(prefix)
    else:
        words = [w for w in re.findall(r'[A-Za-z0-9]+', ascii_text(title)) if w.lower() not in STOP]
        short = compact(' '.join(words[:5]))
    label = f'{surname}-{venue}{paper["year"] % 100:02d}-{short}'
    if paper.get('pdf_metadata', {}).get('document_kind') == 'supplement':
        label += '-Supplement'
    if not LABEL_RE.fullmatch(label):
        raise ValueError('Invalid download label: '+label)
    return label

def assign_labels(papers):
    downloadable = [p for p in papers if p.get('pdf') or p.get('pdf_url')]
    used = set()
    for p in downloadable:
        label = p.get('download_label')
        if label:
            if not LABEL_RE.fullmatch(label) or label.casefold() in used:
                raise ValueError('Invalid or duplicate saved label: '+label)
            used.add(label.casefold())
    for p in downloadable:
        if p.get('download_label'):
            continue
        label = candidate(p)
        if label.casefold() in used:
            label += '-'+hashlib.sha256(p['id'].encode()).hexdigest()[:8]
        if label.casefold() in used:
            raise ValueError('Download label collision: '+p['id'])
        p['download_label'] = label
        used.add(label.casefold())
    return downloadable

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parents[1]/'data/publications.json')
    parser.add_argument('--write', action='store_true', help='Save missing labels; existing labels remain stable')
    args = parser.parse_args()
    payload = json.loads(args.data.read_text())
    papers = assign_labels(payload['publications'])
    if args.write:
        args.data.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n')
    for p in papers:
        print(p['id']+'\t'+p['download_label']+'.pdf')
