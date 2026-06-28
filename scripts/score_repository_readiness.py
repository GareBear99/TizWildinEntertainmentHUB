#!/usr/bin/env python3
from __future__ import annotations
import html,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'; BASE='https://garebear99.github.io/TizWildinEntertainmentHUB'
def load(p,d): return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
src=load(DOCS/'source-index.json',{}); files=src.get('files',[]); by={}
for f in files: by.setdefault(f.get('repoId'),[]).append(f)
checks=[('readme',18,lambda ps:any(p['path'].lower().endswith('readme.md') or p['path'].lower()=='readme' for p in ps),'README present'),('license',14,lambda ps:any('license' in p['path'].lower() for p in ps),'License present'),('changelog',8,lambda ps:any('changelog' in p['path'].lower() for p in ps),'Changelog present'),('contributing',8,lambda ps:any('contributing' in p['path'].lower() for p in ps),'Contributing guide present'),('security',8,lambda ps:any('security' in p['path'].lower() for p in ps),'Security policy present'),('code_of_conduct',6,lambda ps:any('code_of_conduct' in p['path'].lower() or 'code-of-conduct' in p['path'].lower() for p in ps),'Code of conduct present'),('ci',10,lambda ps:any('.github/workflows' in p['path'].lower() for p in ps),'CI workflow present'),('docs',10,lambda ps:sum(1 for p in ps if p['path'].lower().startswith('docs/'))>=2,'Docs folder indexed'),('links',8,lambda ps:sum(p.get('linkCount',0) for p in ps)>=5,'External/internal links found'),('source_breadth',10,lambda ps:len(ps)>=10,'Meaningful file coverage')]
reports=[]
for r in src.get('repositories',[]):
    ps=by.get(r.get('id'),[]); hydrated=bool(ps); got=[]; missing=[]; score=0; maxs=sum(c[1] for c in checks)
    if not hydrated:
        meta=[('Repository URL present',bool(r.get('url'))),('Docs URL present',bool(r.get('docs'))),('Tags present',bool(r.get('tags'))),('Cluster assigned',bool(r.get('cluster')))]
        score=sum(15 for _,ok in meta if ok); got=[a for a,b in meta if b]; missing=[a for a,b in meta if not b]+['Source hydration pending']; grade='Pending hydration'
    else:
        for _,pts,fn,label in checks:
            ok=bool(fn(ps)); (got if ok else missing).append(label); score+=pts if ok else 0
        grade='A' if score>=90 else 'A-' if score>=82 else 'B+' if score>=74 else 'B' if score>=65 else 'C'
    reports.append({'repoId':r.get('id'),'name':r.get('name'),'cluster':r.get('cluster'),'sourceStatus':r.get('sourceStatus'),'hydrated':hydrated,'score':score,'maxScore':maxs,'grade':grade,'fileCount':len(ps),'linkCount':sum(p.get('linkCount',0) for p in ps),'passed':got,'missing':missing,'recommendation':'Hydrate this repo through GitHub API or local archive to enable file-level readiness scoring.' if not hydrated else ('Add missing credibility files/docs.' if missing else 'Ready for directory/list submission.')})
h=[r for r in reports if r['hydrated']]
out={'schemaVersion':'1.0','generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'repositories':reports,'averageScore':round(sum(r['score'] for r in reports)/max(1,len(reports)),2),'averageHydratedScore':round(sum(r['score'] for r in h)/max(1,len(h)),2),'hydratedRepositories':len(h),'pendingHydration':len(reports)-len(h)}
(DOCS/'REPOSITORY_READINESS_REPORT.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
rows=''.join(f"<tr><td>{html.escape(r['name'] or '')}</td><td>{r['grade']}</td><td>{r['score']}/{r['maxScore']}</td><td>{r['fileCount']}</td><td>{r['linkCount']}</td><td>{html.escape(', '.join(r['missing'][:5]))}</td></tr>" for r in reports)
(DOCS/'repo-readiness.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Repository Readiness Report</title><meta name="description" content="Public credibility and SEO readiness scoring for indexed TizWildin and ARC repositories."><link rel="canonical" href="{BASE}/repo-readiness.html"><style>body{{background:#070914;color:#f3f6ff;font-family:Inter,system-ui,Arial,sans-serif;margin:0}}.wrap{{max-width:1180px;margin:0 auto;padding:32px 18px}}table{{width:100%;border-collapse:collapse;background:#11152a}}td,th{{border:1px solid #28304f;padding:10px;text-align:left}}th{{color:#86efac}}a{{color:#8ea2ff}}</style></head><body><main class="wrap"><h1>Repository Readiness Report</h1><p>Hydrated average score: {out['averageHydratedScore']}. Pending hydration: {out['pendingHydration']}.</p><table><thead><tr><th>Repo</th><th>Grade</th><th>Score</th><th>Files</th><th>Links</th><th>Missing</th></tr></thead><tbody>{rows}</tbody></table><p><a href="REPOSITORY_READINESS_REPORT.json">JSON report</a></p></main></body></html>''',encoding='utf-8')
print(f"READINESS SCORE OK: {len(reports)} repos, hydrated avg {out['averageHydratedScore']}")
