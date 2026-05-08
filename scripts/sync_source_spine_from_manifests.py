#!/usr/bin/env python3
"""Synchronize docs/source-repos.json from the public Hub manifests.

Purpose:
- The Hub's public pages are driven by plugins.json, packs.json, and lists.json.
- This sync step turns every manifest item with a GitHub repo into a source-spine record.
- After that, build_source_repo_index.py can hydrate files/links from local archives,
  local folders, or the GitHub API.

This makes adding another ecosystem entry a data-only workflow:
1. Add the project to plugins.json, packs.json, or lists.json.
2. Run this script.
3. Run the public/source/search index builders.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
OWNER = 'GareBear99'
GH = f'https://github.com/{OWNER}'
SOURCE_CONFIG = DOCS / 'source-repos.json'

CATEGORY_CLUSTER = {
    'flagship': 'TizWildin Audio Plugins',
    'instruments': 'TizWildin Audio Plugins',
    'maid_suite': 'TizWildin Audio Plugins',
    'sound_design': 'TizWildin Audio Plugins',
    'experimental': 'TizWildin Audio Plugins',
    'tizwildin_packs': 'TizWildin Sample Packs',
    'producer_kits': 'TizWildin Sample Packs',
    'deconstructed_loops': 'TizWildin Sample Packs',
    'start_here': 'Discovery Lists and Public Routes',
    'hub_lists': 'Discovery Lists and Public Routes',
    'audio_dev': 'Discovery Lists and Public Routes',
    'artist_platforms': 'Discovery Lists and Public Routes',
    'project_anchors': 'Discovery Lists and Public Routes',
    'python_audio_science': 'Discovery Lists and Public Routes',
    'arc_source_spine': 'ARC Source Spine',
}

def read_json(rel: str):
    p = ROOT / rel
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding='utf-8'))

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def slug(value: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', str(value).lower()).strip('-') or 'repo'

def repo_url(repo: str) -> str:
    repo = str(repo or '').strip()
    if not repo:
        return ''
    if repo.startswith('http://') or repo.startswith('https://'):
        return repo
    return f'{GH}/{repo}'

def docs_url(item: dict, repo: str, explicit_url: str = '') -> str:
    if item.get('docs'):
        return item['docs']
    if item.get('website'):
        return item['website']
    if explicit_url and 'github.com' not in explicit_url:
        return explicit_url
    if repo:
        return repo_url(repo) + '#readme'
    return explicit_url

def tags_for(item: dict, extra: list[str]) -> list[str]:
    tags = []
    for k in ('tags', 'formats'):
        tags.extend([str(x).lower().replace(' ', '-') for x in item.get(k, [])])
    tags.extend(extra)
    seen = []
    for t in tags:
        t = slug(t)
        if t and t not in seen:
            seen.append(t)
    return seen[:16]

def manifest_entries():
    plugins = read_json('plugins.json').get('plugins', [])
    for item in plugins:
        repo = item.get('repo')
        if not repo: continue
        yield {
            'id': slug(item.get('id') or item.get('name') or repo),
            'name': item.get('name') or repo,
            'cluster': CATEGORY_CLUSTER.get(item.get('category'), 'TizWildin Audio Plugins'),
            'url': repo_url(repo),
            'docs': docs_url(item, repo),
            'sourceType': 'github-api',
            'priority': 20 if item.get('id') in {'freeeq8','therum','xylocore','freevox8'} else 40,
            'tags': tags_for(item, ['audio-plugin','music-production','tizwildin'])
        }
    packs = read_json('packs.json').get('packs', [])
    for item in packs:
        repo = item.get('repo')
        if not repo: continue
        yield {
            'id': slug(item.get('id') or item.get('name') or repo),
            'name': item.get('name') or repo,
            'cluster': CATEGORY_CLUSTER.get(item.get('category'), 'TizWildin Sample Packs'),
            'url': repo_url(repo),
            'docs': docs_url(item, repo),
            'sourceType': 'github-api',
            'priority': 55,
            'tags': tags_for(item, ['sample-pack','producer-tools','tizwildin'])
        }
    lists = read_json('lists.json').get('lists', [])
    for item in lists:
        repo = item.get('repo')
        url = item.get('url') or repo_url(repo)
        # Non-GitHub external pages are public index routes, not source repos.
        if not repo or 'github.com' not in repo_url(repo):
            continue
        yield {
            'id': slug(item.get('id') or item.get('name') or repo),
            'name': item.get('name') or repo,
            'cluster': CATEGORY_CLUSTER.get(item.get('category'), 'Discovery Lists and Public Routes'),
            'url': url,
            'docs': docs_url(item, repo, item.get('url','')),
            'sourceType': 'github-api',
            'priority': int(item.get('priority', 70)),
            'tags': tags_for(item, ['discovery','seo','public-index'])
        }

def main():
    config = json.loads(SOURCE_CONFIG.read_text(encoding='utf-8'))
    repos = config.setdefault('repositories', [])
    existing = {r.get('id'): r for r in repos}
    added = 0
    updated = 0
    for entry in manifest_entries():
        rid = entry['id']
        if rid in existing:
            # Preserve local-path/local archive setup while refreshing public metadata.
            cur = existing[rid]
            for key in ('name','cluster','url','docs','priority','tags'):
                if entry.get(key):
                    cur[key] = entry[key]
            updated += 1
        else:
            repos.append(entry)
            existing[rid] = entry
            added += 1
    # Keep deterministic order: priority first, then id.
    repos.sort(key=lambda r: (int(r.get('priority', 999)), r.get('id','')))
    config['repositoryCount'] = len(repos)
    config['lastSyncNote'] = 'Generated from plugins.json, packs.json, and lists.json. Add entries there, run sync, then rebuild public/source/search indexes.'
    write_json(SOURCE_CONFIG, config)
    print(f'SOURCE SPINE SYNC OK: {len(repos)} repos ({added} added, {updated} refreshed)')

if __name__ == '__main__':
    main()
