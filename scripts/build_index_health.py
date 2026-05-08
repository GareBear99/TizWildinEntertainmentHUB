#!/usr/bin/env python3
from __future__ import annotations
import json,time,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'; BASE='https://garebear99.github.io/TizWildinEntertainmentHUB'
def load(name,d):
    p=DOCS/name
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
pub=load('public-index.json',{}); src=load('source-index.json',{}); search=load('search-index.json',{}); bench=load('PUBLIC_INDEX_BENCHMARK.json',{}); links=load('LINK_CHECK_REPORT.json',{}); ready=load('REPOSITORY_READINESS_REPORT.json',{}); seo=load('SEO_BUILD_REPORT.json',{})
su=seo.get('sitemapUrls',0); su=su if isinstance(su,int) else len(su)
metrics={'publicRoutes':len(pub.get('items',[])),'sitemapUrls':su,'sourceRepos':len(src.get('repositories',[])),'indexedFiles':len(src.get('files',[])),'extractedLinks':len(load('source-link-index.json',{}).get('links',[])),'searchRecords':search.get('documentCount',0),'searchTokens':search.get('tokenCount',0),'readinessAverage':ready.get('averageHydratedScore',ready.get('averageScore',0)),'pendingHydration':ready.get('pendingHydration',0),'linkIssues':links.get('issues',0),'benchmarkGrade':bench.get('grade','not run')}
score=100
if metrics['linkIssues']: score-=10
if metrics['readinessAverage'] and metrics['readinessAverage']<75: score-=10
if 'F' in str(metrics['benchmarkGrade']): score-=40
elif 'B' in str(metrics['benchmarkGrade']): score-=6
grade='A+' if score>=96 else 'A' if score>=90 else 'A-' if score>=84 else 'B+' if score>=76 else 'B'
out={'schemaVersion':'1.0','generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'qualityGrade':grade,'qualityScore':score,'metrics':metrics,'nextImprovements':['Keep GitHub API hydration enabled in scheduled CI when tokens are available.','Review readiness report for repos below A-.','Run live link checks before major release tags.','Keep adding repo entries through docs/source-repos.json only.']}
(DOCS/'index-health.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
rows=''.join(f'<tr><th>{html.escape(k)}</th><td>{html.escape(str(v))}</td></tr>' for k,v in metrics.items())
(DOCS/'index-health.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Public Index Health Dashboard</title><meta name="description" content="Health dashboard for the TizWildin / ARC public ecosystem index, source graph, search index, link graph, and readiness reports."><link rel="canonical" href="{BASE}/index-health.html"><style>body{{margin:0;background:#070914;color:#f3f6ff;font-family:Inter,system-ui,Arial,sans-serif}}.wrap{{max-width:1060px;margin:0 auto;padding:32px 18px}}.hero{{border:1px solid #28304f;background:#11152a;border-radius:22px;padding:22px}}.grade{{font-size:64px;color:#86efac;font-weight:900}}table{{width:100%;border-collapse:collapse;margin-top:20px;background:#11152a}}td,th{{border:1px solid #28304f;padding:12px;text-align:left}}a{{color:#8ea2ff}}</style></head><body><main class="wrap"><section class="hero"><h1>Public Index Health</h1><div class="grade">{grade}</div><p>Quality score: {score}/100. Generated {out['generatedAt']}.</p><p><a href="search.html">Search</a> · <a href="repo-readiness.html">Readiness</a> · <a href="repo-file-search.html">File Search</a> · <a href="public-index.json">Public Index JSON</a></p></section><table>{rows}</table><h2>Next Improvements</h2><ul>{''.join('<li>'+html.escape(x)+'</li>' for x in out['nextImprovements'])}</ul></main></body></html>''',encoding='utf-8')
print(f"INDEX HEALTH OK: {grade} ({score}/100)")
