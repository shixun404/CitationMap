"""
Standalone script to extract the full author list for each citing paper via CrossRef.

For each paper in unique_citing_papers_deduped.csv:
  - Queries CrossRef by title to get the complete author list (full names,
    affiliations, and ORCID where available).
  - If CrossRef has no match, writes a single row with author_name='GS_ONLY'
    as a placeholder for manual completion.

No browser / Google Scholar requests are made.

Supports checkpoint/resume: if interrupted, re-run and it picks up where it left off.

Output columns: citing_paper, author_name, affiliation, orcid, author_scholar_url
"""

import csv
import os
import time

import requests

INPUT_CSV     = 'unique_citing_papers_deduped.csv'
OUTPUT_CSV    = 'citing_paper_full_authors.csv'
CROSSREF_BASE = 'https://api.crossref.org/works'
HEADERS       = {'User-Agent': 'CitationMap/1.0 (mailto:user@example.com)'}


def crossref_authors(title: str) -> list:
    """
    Query CrossRef for `title`.
    Returns a list of (full_name, affiliation_str, orcid_str) tuples,
    or [] if nothing useful is found.
    affiliation_str is semicolon-separated when an author has multiple affiliations.
    """
    try:
        params = {
            'query.bibliographic': title,
            'rows': 5,
            'select': 'title,author',
        }
        resp = requests.get(CROSSREF_BASE, params=params, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        items = resp.json().get('message', {}).get('items', [])
    except Exception as exc:
        print(f"  [CrossRef ERROR] {exc}")
        return []

    title_lower = title.lower().strip()
    for item in items:
        cr_titles = item.get('title', [])
        if not cr_titles:
            continue
        cr_title = cr_titles[0].lower().strip()
        if title_lower[:60] in cr_title or cr_title[:60] in title_lower:
            authors = []
            for a in item.get('author', []):
                given  = a.get('given', '').strip()
                family = a.get('family', '').strip()
                if not family:
                    continue
                name        = f"{given} {family}".strip() if given else family
                affiliations = '; '.join(aff['name'] for aff in a.get('affiliation', []) if aff.get('name'))
                orcid        = a.get('ORCID', 'None') or 'None'
                authors.append((name, affiliations or 'None', orcid))
            if authors:
                return authors

    return []


def load_done_papers(path) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, encoding='utf-8') as f:
        return {row['citing_paper'] for row in csv.DictReader(f)}


def main():
    with open(INPUT_CSV, encoding='utf-8') as f:
        papers = [r['citing_paper'].strip() for r in csv.DictReader(f) if r['citing_paper'].strip()]

    done      = load_done_papers(OUTPUT_CSV)
    remaining = [p for p in papers if p not in done]
    print(f"Papers total: {len(papers)} | Done: {len(done)} | Remaining: {len(remaining)}\n")

    if not remaining:
        print("All papers already processed. Output is at:", OUTPUT_CSV)
        return

    write_header = not os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['citing_paper', 'author_name', 'affiliation', 'orcid', 'author_scholar_url'])

        for i, paper in enumerate(remaining, 1):
            print(f"[{i}/{len(remaining)}] {paper[:80]}...")
            authors = crossref_authors(paper)

            if authors:
                for name, affiliation, orcid in authors:
                    writer.writerow([paper, name, affiliation, orcid, 'None'])
                print(f"  -> {len(authors)} author(s) found.")
            else:
                writer.writerow([paper, 'GS_ONLY', 'None', 'None', 'None'])
                print(f"  -> Not in CrossRef — marked GS_ONLY.")

            f.flush()
            time.sleep(0.5)   # be polite to CrossRef

    print(f"\nDone. Results saved to {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
