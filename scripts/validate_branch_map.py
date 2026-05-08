#!/usr/bin/env python3
"""Validate branch governance map for the public-index operating system."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BRANCH_MAP = ROOT / "docs" / "branch-map.json"
REQUIRED_DOCS = ["docs/BRANCHING_STRATEGY.md","docs/BRANCH_EXECUTION_QUEUE.md","docs/BRANCH_PROTECTION_RULES.md","docs/BRANCH_RELEASE_LADDER.md"]
ALLOWED_PREFIXES=("seo/","submission/","route/","arc/","audio/","release/","hotfix/")
def fail(msg): print(f"FAIL: {msg}"); sys.exit(1)
def check(cond,msg):
    if not cond: fail(msg)
def main():
    check(BRANCH_MAP.exists(),"missing docs/branch-map.json")
    for rel in REQUIRED_DOCS:
        p=ROOT/rel; check(p.exists(),f"missing {rel}"); check(len(p.read_text(encoding='utf-8').strip())>350,f"{rel} is too thin")
    data=json.loads(BRANCH_MAP.read_text(encoding='utf-8'))
    check(data.get('schemaVersion')=='1.0','branch-map schemaVersion must be 1.0')
    check(data.get('defaultBranch')=='main','defaultBranch must be main')
    check(data.get('integrationBranch')=='develop','integrationBranch must be develop')
    rules=data.get('rules',{})
    for key in ['main','develop','route/*','submission/*','seo/*','arc/*','audio/*','release/*','hotfix/*']:
        check(key in rules,f'missing branch rule: {key}')
    branches=data.get('activeBranches',[])
    check(len(branches)>=8,'expected at least 8 branch records')
    seen=set()
    for b in branches:
        name=b.get('name',''); check(name,'branch missing name'); check(name not in seen,f'duplicate branch: {name}'); seen.add(name)
        check(name.startswith(ALLOWED_PREFIXES),f'branch uses unapproved prefix: {name}')
        check(b.get('cluster'),f'branch missing cluster: {name}')
        check(b.get('purpose') and len(b['purpose'])>=30,f'branch purpose too short: {name}')
        check(b.get('status'),f'branch missing status: {name}')
        check(isinstance(b.get('mustPass'),list) and b.get('mustPass'),f'branch missing mustPass: {name}')
    policy=data.get('mergePolicy',[])
    check(len(policy)>=4,'mergePolicy too thin')
    check(any('public index' in p.lower() for p in policy),'mergePolicy must mention public index')
    check(any('evidence' in p.lower() for p in policy),'mergePolicy must mention evidence')
    pub=ROOT/'docs'/'public-index.json'
    if pub.exists():
        idx=json.loads(pub.read_text(encoding='utf-8'))
        names={x.get('name') for x in idx.get('items',[])}
        check('Branching Strategy Route' in names,'public index missing Branching Strategy Route; rerun build_public_index.py')
    print(f"BRANCH MAP VALIDATION OK: {len(branches)} tracked branches")
if __name__=='__main__': main()
