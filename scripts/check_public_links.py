#!/usr/bin/env python3
from __future__ import annotations
import json,os,re,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DOCS=ROOT/'docs'; FETCH=os.environ.get('CHECK_EXTERNAL_LINKS')=='1'; TIME=float(os.environ.get('LINK_CHECK_BASE_TIMEOUT','3')); MAX=int(os.environ.get('LINK_CHECK_MAX_LINKS','1500')); URL=re.compile(r"^https?://[^\s<>\"']+$")
def load(p,d): return json.loads(p.read_text(encoding='utf-8')) if p.exists() else d
links=[]
for item in load(DOCS/'public-index.json',{}).get('items',[]):
    for k in ('url','repoUrl','docsUrl','pageUrl'):
        if item.get(k): links.append({'url':item[k],'source':'public-index','item':item.get('name')})
for l in load(DOCS/'source-link-index.json',{}).get('links',[]):
    if l.get('url','').startswith('http'): links.append({'url':l['url'],'source':'source-link-index','item':l.get('repoName')})
seen=set(); uniq=[]
for l in links:
    u=l['url'].rstrip('/')
    if u not in seen: seen.add(u); uniq.append(l)
results=[]; bad=checked=skipped=0
for l in uniq[:MAX]:
    u=l['url']; status='valid-format'; code=None; err=''
    if not URL.match(u): status='invalid-format'; bad+=1
    elif FETCH:
        try:
            with urllib.request.urlopen(urllib.request.Request(u,method='HEAD',headers={'User-Agent':'TizWildinPublicIndexChecker/1.0'}),timeout=TIME) as r: code=r.status
            checked+=1; status='ok' if code<400 else 'http-warning'; bad+=1 if code>=400 else 0
        except Exception as e: status='fetch-error'; err=str(e)[:180]; bad+=1
    else: skipped+=1
    results.append({**l,'status':status,'statusCode':code,'error':err})
out={'schemaVersion':'1.0','generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'mode':'live' if FETCH else 'offline-format','totalLinks':len(uniq[:MAX]),'checked':checked,'skippedExternal':skipped,'issues':bad,'timeoutPolicy':{'mode':'generation-based','secondsPerLink':TIME,'maxLinks':MAX},'results':results}
(DOCS/'LINK_CHECK_REPORT.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(f"LINK CHECK OK: {out['totalLinks']} links, {bad} issues, mode={out['mode']}")
raise SystemExit(1 if bad and FETCH else 0)
