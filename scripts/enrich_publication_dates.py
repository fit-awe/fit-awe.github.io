#!/usr/bin/env python3
"""Add sourced dates without changing bibliography fields or inventing precision."""
import argparse
import json
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from publication_dates import fetch_date

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--since', type=int, default=0)
    args = parser.parse_args()
    path = ROOT / 'data/publications.json'
    payload = json.loads(path.read_text())
    papers = [p for p in payload['publications'] if p['year'] >= args.since and not p.get('published_date')]
    results, unavailable = {}, []
    def lookup(paper):
        try:
            return paper['id'], fetch_date(paper)
        except Exception as error:
            return paper['id'], {'error': type(error).__name__}
    with ThreadPoolExecutor(max_workers=5) as pool:
        for done, future in enumerate(as_completed(pool.submit(lookup, p) for p in papers), 1):
            key, result = future.result()
            if result and 'error' not in result:
                results[key] = result
            else:
                unavailable.append(key)
            if done % 25 == 0:
                print(f'Checked {done}/{len(papers)} dates; {len(results)} verified', flush=True)
    # Reread so independent edits to other fields are preserved.
    payload = json.loads(path.read_text())
    for paper in payload['publications']:
        if paper['id'] in results:
            paper.update(results[paper['id']])
    if results:
        payload['updated'] = date.today().isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    Path('/tmp/fitawe-date-enrichment.json').write_text(json.dumps({'checked': len(papers), 'verified': len(results), 'unavailable': unavailable}, indent=2))
    print(f'Added {len(results)} sourced dates. {len(unavailable)} records retain their existing year.', flush=True)


if __name__ == '__main__':
    main()
