#!/usr/bin/env python3
"""Optional helper: download public GitHub zip archives for source indexing.

This is not required for GitHub Actions when SOURCE_INDEX_FETCH_REMOTE=1 is used.
It is useful for local/offline repeatability after the first hydrate.
"""
from __future__ import annotations
import json, re, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'docs/source-repos.json'
OUT=ROOT/'source_archives'

def parse_github(url: str):
    m=re.match(r'https://github\.com/([^/]+)/([^/#?]+)', url or '')
    if not m: return None
    return m.group(1), m.group(2).removesuffix('.git')

def main():
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)
    count=0
    for repo in cfg.get('repositories',[]):
        gh=parse_github(repo.get('url',''))
        if not gh: continue
        owner,name=gh
        branch=repo.get('branch','main')
        target=OUT/f'{name}-main.zip'
        if target.exists():
            print(f'cached: {target}')
            continue
        url=f'https://github.com/{owner}/{name}/archive/refs/heads/{branch}.zip'
        try:
            print(f'downloading: {url}')
            urllib.request.urlretrieve(url, target)
            count+=1
        except Exception as exc:
            if branch != 'master':
                url=f'https://github.com/{owner}/{name}/archive/refs/heads/master.zip'
                try:
                    print(f'downloading fallback: {url}')
                    urllib.request.urlretrieve(url, target)
                    count+=1
                    continue
                except Exception:
                    pass
            print(f'warning: failed {repo.get("name")}: {exc}')
    print(f'hydrated {count} archives into {OUT}')
if __name__=='__main__': main()
