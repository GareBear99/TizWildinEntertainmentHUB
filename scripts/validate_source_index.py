#!/usr/bin/env python3
from pathlib import Path
import json, sys, re
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
BAD=re.compile('d'+'arpa', re.I)

def fail(msg):
    print('SOURCE VALIDATION FAILED:', msg)
    sys.exit(1)

def load(p):
    if not p.exists(): fail(f'missing {p}')
    return json.loads(p.read_text(encoding='utf-8'))
idx=load(DOCS/'source-index.json')
links=load(DOCS/'source-link-index.json')
if not idx.get('repositories'): fail('no repositories')
if 'files' not in idx: fail('missing files array')
if 'links' not in links: fail('missing links array')
if BAD.search((DOCS/'source-index.json').read_text(encoding='utf-8')): fail('public source-index contains non-public audit branding')
if BAD.search((DOCS/'source-link-index.json').read_text(encoding='utf-8')): fail('public source-link-index contains non-public audit branding')
if BAD.search((DOCS/'repo-file-search.html').read_text(encoding='utf-8')): fail('repo search page contains non-public audit branding')
for r in idx['repositories']:
    page=DOCS/r.get('page','')
    if not page.exists(): fail(f'missing source page for {r.get("name")}')
    txt=page.read_text(encoding='utf-8')
    if BAD.search(txt): fail(f'source page for {r.get("name")} contains non-public audit branding')
    if 'Search all indexed files' not in txt: fail(f'source page missing search backlink for {r.get("name")}')
for f in idx['files'][:20]:
    for k in ('repoId','repoName','path','summary','queryText'):
        if k not in f: fail(f'missing {k} on file record')
print(f"SOURCE VALIDATION OK: {len(idx['repositories'])} repos, {len(idx.get('files',[]))} files, {len(links.get('links',[]))} links")
