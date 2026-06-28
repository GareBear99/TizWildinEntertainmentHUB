#!/usr/bin/env python3
"""Build the Hub source-repository index.

Add one entry to docs/source-repos.json and this script generates:
- docs/source-index.json
- docs/source-link-index.json
- docs/repo-file-search.html
- docs/SOURCE_REPOSITORY_INDEX.md
- docs/pages/source-<repo-id>.html

The builder supports local folders, zip archives, remote GitHub records, and optional
GitHub API ingestion. Network access is never required for CI; set
SOURCE_INDEX_FETCH_REMOTE=1 or pass --fetch-remote to hydrate remote repositories.
"""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, shutil, sys, tempfile, time, zipfile, urllib.request, urllib.error
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PAGES = DOCS / "pages"
BASE = os.environ.get("PUBLIC_BASE_URL", "https://garebear99.github.io/TizWildinEntertainmentHUB").rstrip("/")
CONFIG = DOCS / "source-repos.json"
LINK_RE = re.compile(r"(?P<url>https?://[^\s)\]\"'<>]+)|\[[^\]]+\]\((?P<md>[^)]+)\)")
SKIP_DIRS = {'.git','node_modules','__pycache__','.pytest_cache','.mypy_cache','dist','build','.venv','venv','.idea','.vscode','.next','.cache','coverage'}
SKIP_EXTS = {'.png','.jpg','.jpeg','.gif','.webp','.ico','.zip','.7z','.rar','.mp3','.wav','.flac','.aiff','.ogg','.mp4','.mov','.sqlite','.sqlite3','.db','.pyc','.pyo','.dylib','.dll','.so','.exe','.pdf'}
TEXT_EXTS = {'.md','.txt','.rst','.py','.js','.ts','.tsx','.jsx','.html','.css','.json','.yml','.yaml','.toml','.xml','.svg','.c','.cpp','.h','.hpp','.mm','.m','.rs','.go','.sh','.ps1','.bat','.cmake','.gradle','.java','.kt','.swift','.php','.rb','.sql'}
MAX_FILE_BYTES = int(os.environ.get('SOURCE_INDEX_MAX_FILE_BYTES','262144'))
MAX_REMOTE_FILES = int(os.environ.get('SOURCE_INDEX_MAX_REMOTE_FILES','350'))
PUBLIC_REPLACEMENTS = [
    (re.compile('d'+'arpa', re.I), 'production-grade'),
]

def public_clean(value: str) -> str:
    out = str(value or '')
    for pat, repl in PUBLIC_REPLACEMENTS:
        out = pat.sub(repl, out)
    return out

def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def slug(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+','-',str(s).lower()).strip('-') or 'item'

def is_allowed(rel: Path | str, size: int) -> bool:
    rel = Path(str(rel))
    if any(part in SKIP_DIRS for part in rel.parts): return False
    if size > MAX_FILE_BYTES: return False
    if rel.suffix.lower() in SKIP_EXTS: return False
    if rel.name.startswith('.DS_Store'): return False
    return rel.suffix.lower() in TEXT_EXTS or rel.name in {'README','LICENSE','Makefile','Dockerfile','CMakeLists.txt'}

def extract_links(text: str):
    out=[]
    for m in LINK_RE.finditer(text):
        url=(m.group('url') or m.group('md') or '').strip()
        if not url or url.startswith('#') or url.startswith('mailto:') or url.startswith('javascript:'): continue
        out.append(public_clean(url.rstrip('.,;')))
    return sorted(set(out))[:250]

def summarize_text(text: str, n=220):
    clean=re.sub(r'\s+',' ', re.sub(r'[#*`>_~\-]+',' ', text)).strip()
    return public_clean(clean[:n])

def make_file_record(repo, rel, text, size, file_links):
    public_path = public_clean(str(rel).replace('\\','/'))
    h=hashlib.sha256(text.encode('utf-8',errors='ignore')).hexdigest()
    ext=Path(str(rel)).suffix.lower() or '[none]'
    summary=summarize_text(text)
    query=' '.join([repo['name'], repo.get('cluster',''), public_path, summarize_text(text,800), ' '.join(file_links[:80]), ' '.join(repo.get('tags',[]))]).lower()
    return {
        'repoId':repo['id'],'repoName':public_clean(repo['name']),'cluster':public_clean(repo.get('cluster','')),
        'path':public_path,'extension':ext,'bytes':size,'sha256':h,'summary':summary,
        'linkCount':len(file_links),'queryText':public_clean(query),
        'repoUrl':repo.get('url',''), 'docsUrl':repo.get('docs','')
    }

def scan_tree(repo, base: Path, started: float, budget: float):
    files=[]; links=[]; exts=Counter(); dirs=Counter(); total_bytes=0; skipped=0
    for path in base.rglob('*'):
        if time.monotonic() - started > budget:
            raise TimeoutError(f"source indexing budget exceeded after {budget:.1f}s while scanning {repo['name']}")
        if path.is_dir(): continue
        rel=path.relative_to(base)
        try: size=path.stat().st_size
        except OSError: continue
        if not is_allowed(rel,size):
            skipped += 1; continue
        try:
            text=path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            skipped += 1; continue
        file_links=extract_links(text)
        rec=make_file_record(repo, rel, text, size, file_links)
        exts[rec['extension']]+=1; dirs[rec['path'].split('/')[0] if '/' in rec['path'] else '.'] += 1; total_bytes += size
        files.append(rec)
        for u in file_links:
            domain=re.sub(r'^https?://([^/]+).*', r'\1', u) if u.startswith('http') else ''
            links.append({'repoId':repo['id'],'repoName':public_clean(repo['name']),'sourcePath':rec['path'],'url':u,'domain':domain,'queryText':(' '.join([repo['name'], rec['path'], u, domain])).lower()})
    return {'files':files,'links':links,'stats':{'fileCount':len(files),'skippedFiles':skipped,'totalBytes':total_bytes,'extensions':dict(exts),'topDirectories':dict(dirs.most_common(25))}}

def parse_github(url: str):
    m = re.match(r'https://github\.com/([^/]+)/([^/#?]+)', url or '')
    if not m: return None
    return m.group(1), m.group(2).removesuffix('.git')

def http_json(url: str, timeout: float):
    req = urllib.request.Request(url, headers={'User-Agent':'TizWildin-Hub-Source-Indexer/1.0','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def http_text(url: str, timeout: float):
    req = urllib.request.Request(url, headers={'User-Agent':'TizWildin-Hub-Source-Indexer/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(MAX_FILE_BYTES+1).decode('utf-8', errors='ignore')

def scan_github_repo(repo, started: float, budget: float):
    gh = parse_github(repo.get('url',''))
    if not gh:
        return {'files': [], 'links': [], 'stats': {'fileCount':0,'skippedFiles':0,'totalBytes':0,'extensions':{},'topDirectories':{}}, 'remoteFetchStatus': 'not-github'}
    owner, name = gh
    per_req = float(os.environ.get('SOURCE_INDEX_REMOTE_REQUEST_TIMEOUT','12'))
    branch = repo.get('branch') or os.environ.get('SOURCE_INDEX_DEFAULT_BRANCH','main')
    try:
        tree = http_json(f'https://api.github.com/repos/{owner}/{name}/git/trees/{branch}?recursive=1', per_req)
    except Exception as exc:
        # Try master for older repos.
        try:
            branch = 'master'
            tree = http_json(f'https://api.github.com/repos/{owner}/{name}/git/trees/{branch}?recursive=1', per_req)
        except Exception as exc2:
            return {'files': [], 'links': [], 'stats': {'fileCount':0,'skippedFiles':0,'totalBytes':0,'extensions':{},'topDirectories':{}}, 'remoteFetchStatus': f'github-fetch-failed: {public_clean(exc2)}'}
    entries = [e for e in tree.get('tree',[]) if e.get('type') == 'blob' and is_allowed(e.get('path',''), int(e.get('size') or 0))]
    entries = sorted(entries, key=lambda e: (0 if Path(e.get('path','')).name.lower() in {'readme.md','license'} else 1, e.get('path','')))[:MAX_REMOTE_FILES]
    files=[]; links=[]; exts=Counter(); dirs=Counter(); total_bytes=0; skipped=0
    for e in entries:
        if time.monotonic() - started > budget:
            raise TimeoutError(f"source indexing budget exceeded after {budget:.1f}s while remote scanning {repo['name']}")
        rel=e['path']; size=int(e.get('size') or 0)
        raw=f'https://raw.githubusercontent.com/{owner}/{name}/{branch}/{rel}'
        try:
            text=http_text(raw, per_req)
        except Exception:
            skipped += 1; continue
        file_links=extract_links(text)
        rec=make_file_record(repo, rel, text, size, file_links)
        exts[rec['extension']]+=1; dirs[rec['path'].split('/')[0] if '/' in rec['path'] else '.'] += 1; total_bytes += size
        files.append(rec)
        for u in file_links:
            domain=re.sub(r'^https?://([^/]+).*', r'\1', u) if u.startswith('http') else ''
            links.append({'repoId':repo['id'],'repoName':public_clean(repo['name']),'sourcePath':rec['path'],'url':u,'domain':domain,'queryText':(' '.join([repo['name'], rec['path'], u, domain])).lower()})
    return {'files':files,'links':links,'stats':{'fileCount':len(files),'skippedFiles':skipped,'totalBytes':total_bytes,'extensions':dict(exts),'topDirectories':dict(dirs.most_common(25))}, 'remoteFetchStatus': f'github-api:{branch}'}

def resolve_sources(config, cli_repos):
    overrides={}
    for item in cli_repos or []:
        if '=' not in item: raise SystemExit('--repo must be NAME_OR_ID=/path/to/repo-or-zip')
        k,v=item.split('=',1); overrides[k.lower()] = Path(v).expanduser().resolve()
    resolved=[]
    for repo in config['repositories']:
        r=dict(repo); key=repo['id'].lower(); name=repo['name'].lower()
        if key in overrides: r['resolvedPath']=str(overrides[key])
        elif name in overrides: r['resolvedPath']=str(overrides[name])
        elif repo.get('path') == '.': r['resolvedPath']=str(ROOT)
        elif repo.get('path'):
            p=(ROOT/repo['path']).resolve()
            if p.exists(): r['resolvedPath']=str(p)
        resolved.append(r)
    return resolved

def estimate_budget(repo_count:int, expected_files:int):
    pol=read_json(CONFIG).get('timeoutPolicy',{}) if CONFIG.exists() else {}
    if os.environ.get('SOURCE_INDEX_TIMEOUT_SECONDS'):
        return float(os.environ['SOURCE_INDEX_TIMEOUT_SECONDS'])
    base=float(pol.get('baseSeconds',20)); per=float(pol.get('secondsPerThousandFiles',8)); maxs=float(pol.get('maxSeconds',240)); per_repo=float(pol.get('secondsPerRepo',2))
    return min(maxs, base + repo_count*per_repo + (max(1, expected_files)/1000.0)*per)

def repo_page(repo, stats, files, links):
    file_rows='\n'.join(f'<li><code>{html.escape(f["path"])}</code> <span>{f["bytes"]} bytes · {f["linkCount"]} links</span></li>' for f in files[:500])
    link_rows='\n'.join(f'<li><a href="{html.escape(l["url"])}">{html.escape(l["url"])}</a> <span>{html.escape(l.get("sourcePath",""))}</span></li>' for l in links[:250])
    desc=html.escape('Queryable source file and link index for '+public_clean(repo['name']))
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>{html.escape(public_clean(repo['name']))} Source Index</title><meta name='description' content='{desc}'><link rel='canonical' href='{BASE}/pages/source-{slug(repo['id'])}.html'><style>body{{font-family:system-ui;background:#080a12;color:#ecf2ff;margin:0;padding:24px}}main{{max-width:1120px;margin:auto}}a{{color:#8ea2ff}}code{{color:#86efac}}li{{margin:8px 0}}span{{color:#9fb0d8}}</style></head><body><main><h1>{html.escape(public_clean(repo['name']))} Source Index</h1><p>{desc}</p><p><a href='{html.escape(repo.get('url',''))}'>Repository</a> · <a href='{html.escape(repo.get('docs',''))}'>Docs</a> · <a href='../repo-file-search.html'>Search all indexed files</a></p><dl><dt>Cluster</dt><dd>{html.escape(public_clean(repo.get('cluster','')))}</dd><dt>Indexed files</dt><dd>{stats.get('fileCount',0)}</dd><dt>Extracted links</dt><dd>{stats.get('linkCount',0)}</dd></dl><h2>Indexed files</h2><ol>{file_rows}</ol><h2>Extracted links</h2><ol>{link_rows}</ol></main></body></html>"""

def search_page():
    return """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Repository File Search | TizWildin Hub</title><meta name='description' content='Static searchable index of public Hub source files, repository manifests, docs, and extracted links.'><link rel='canonical' href='https://garebear99.github.io/TizWildinEntertainmentHUB/repo-file-search.html'><style>body{font-family:system-ui;background:#080a12;color:#ecf2ff;margin:0;padding:24px}main{max-width:1180px;margin:auto}input,select{padding:12px;border-radius:12px;border:1px solid #38507e;background:#11182b;color:#fff}input{width:100%;box-sizing:border-box}.grid{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:10px}article{border:1px solid #26385f;border-radius:14px;padding:14px;margin:12px 0;background:#10172a}code{color:#86efac}.meta{color:#9fb0d8}.tabs button{margin:10px 8px 10px 0;padding:10px 14px;border-radius:12px;border:1px solid #38507e;background:#11182b;color:#fff}.tabs button.active{border-color:#86efac}a{color:#8ea2ff}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style></head><body><main><h1>Repository File Search</h1><p>Search the generated static source index. Add another repository in <code>docs/source-repos.json</code>, run <code>python scripts/build_source_repo_index.py</code>, and it appears here with files, route pages, and extracted links.</p><div class='grid'><input id='q' placeholder='Search repo, file path, docs, links, topic...' autofocus><select id='repo'><option value=''>All repos</option></select><select id='cluster'><option value=''>All clusters</option></select><select id='ext'><option value=''>All file types</option></select></div><div class='tabs'><button id='filesBtn' class='active'>Files</button><button id='linksBtn'>Links</button></div><div id='count' class='meta'></div><section id='results'></section></main><script>
let files=[], links=[], mode='files'; const $=id=>document.getElementById(id); const q=$('q'), out=$('results'), count=$('count'), repo=$('repo'), cluster=$('cluster'), ext=$('ext');
Promise.all([fetch('source-index.json').then(r=>r.json()), fetch('source-link-index.json').then(r=>r.json())]).then(([fi,li])=>{files=fi.files||[]; links=li.links||[]; fillFilters(); const p=new URLSearchParams(location.search); if(p.get('q')) q.value=p.get('q'); render();});
function fill(sel, vals){vals.forEach(v=>{const o=document.createElement('option'); o.value=v; o.textContent=v; sel.appendChild(o);});}
function fillFilters(){fill(repo,[...new Set(files.map(f=>f.repoName).filter(Boolean))].sort()); fill(cluster,[...new Set(files.map(f=>f.cluster).filter(Boolean))].sort()); fill(ext,[...new Set(files.map(f=>f.extension).filter(Boolean))].sort());}
function matchCommon(x, term){return (!repo.value || x.repoName===repo.value) && (!cluster.value || x.cluster===cluster.value) && (!term || (x.queryText||JSON.stringify(x).toLowerCase()).includes(term));}
function render(){const term=q.value.trim().toLowerCase(); const params=new URLSearchParams(location.search); if(term) params.set('q',term); else params.delete('q'); history.replaceState(null,'',location.pathname+(params.toString()?('?'+params):'')); if(mode==='files'){let rows=files.filter(f=>matchCommon(f,term)&&(!ext.value||f.extension===ext.value)).slice(0,300); count.textContent=`${rows.length} shown / ${files.length} indexed files`; out.innerHTML=rows.map(f=>`<article><h3>${esc(f.repoName)} · <code>${esc(f.path)}</code></h3><div class='meta'>${esc(f.cluster)} · ${esc(f.extension)} · ${f.bytes} bytes · ${f.linkCount} links</div><p>${esc(f.summary||'')}</p></article>`).join('');} else {let rows=links.filter(l=>(!repo.value||l.repoName===repo.value)&&(!term||(l.queryText||JSON.stringify(l).toLowerCase()).includes(term))).slice(0,300); count.textContent=`${rows.length} shown / ${links.length} extracted links`; out.innerHTML=rows.map(l=>`<article><h3>${esc(l.repoName)} · <a href='${esc(l.url)}'>${esc(l.domain||l.url)}</a></h3><div class='meta'><code>${esc(l.sourcePath||'')}</code></div><p>${esc(l.url)}</p></article>`).join('');}}
function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));} q.addEventListener('input',render); repo.addEventListener('change',render); cluster.addEventListener('change',render); ext.addEventListener('change',render); $('filesBtn').onclick=()=>{mode='files'; $('filesBtn').classList.add('active'); $('linksBtn').classList.remove('active'); ext.disabled=false; render();}; $('linksBtn').onclick=()=>{mode='links'; $('linksBtn').classList.add('active'); $('filesBtn').classList.remove('active'); ext.disabled=true; render();};
</script></body></html>"""

def merge_source_urls_into_sitemap(repo_records):
    sitemap = DOCS / 'sitemap.xml'
    urls = [f"{BASE}/repo-file-search.html"] + [r['pageUrl'] for r in repo_records]
    if not sitemap.exists():
        body=''.join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        write(sitemap, "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"+body+"</urlset>\n")
        return
    text=sitemap.read_text(encoding='utf-8')
    additions=''.join(f"  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.72</priority></url>\n" for u in urls if u not in text)
    if additions:
        text=text.replace('</urlset>', additions+'</urlset>')
        sitemap.write_text(text, encoding='utf-8', newline='\n')

def append_source_llms(repo_records):
    path = DOCS / 'llms.txt'
    block = ['\n## Source Repository Search Index', '- Repository file search: '+BASE+'/repo-file-search.html']
    block += [f"- {r['name']} source index: {r['pageUrl']}" for r in repo_records]
    text = path.read_text(encoding='utf-8') if path.exists() else '# TizWildin Entertainment Hub\n'
    marker='## Source Repository Search Index'
    if marker in text:
        text = text.split(marker)[0].rstrip()+"\n"+'\n'.join(block)+"\n"
    else:
        text = text.rstrip()+"\n"+'\n'.join(block)+"\n"
    path.write_text(public_clean(text), encoding='utf-8', newline='\n')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo', action='append', help='Override/add source path: repo-id=/path/to/archive-or-folder')
    ap.add_argument('--fetch-remote', action='store_true', help='Fetch remote GitHub repo trees/files through the public GitHub API')
    args=ap.parse_args()
    config=read_json(CONFIG)
    repos=resolve_sources(config,args.repo)
    fetch_remote = args.fetch_remote or os.environ.get('SOURCE_INDEX_FETCH_REMOTE') == '1'
    started=time.monotonic(); budget=estimate_budget(len(repos), 2000)
    all_files=[]; all_links=[]; repo_records=[]; errors=[]; tmpdirs=[]
    try:
      for repo in repos:
        source_status='remote-record-only'; work=None; remote_status='not-requested'
        rp=Path(repo['resolvedPath']) if repo.get('resolvedPath') else None
        try:
          if rp and rp.exists():
            if rp.is_file() and rp.suffix.lower()=='.zip':
              td=Path(tempfile.mkdtemp(prefix='source-index-')); tmpdirs.append(td)
              with zipfile.ZipFile(rp) as z: z.extractall(td)
              kids=[p for p in td.iterdir()]
              work=kids[0] if len(kids)==1 and kids[0].is_dir() else td
              source_status='indexed-archive'
            elif rp.is_dir():
              work=rp; source_status='indexed-folder'
          if work:
            result=scan_tree(repo, work, started, budget); files=result['files']; links=result['links']; stats=result['stats']
          elif fetch_remote and parse_github(repo.get('url','')):
            result=scan_github_repo(repo, started, budget); files=result['files']; links=result['links']; stats=result['stats']; remote_status=result.get('remoteFetchStatus','unknown')
            source_status='indexed-github-api' if files else 'remote-record-only'
          else:
            files=[]; links=[]; stats={'fileCount':0,'skippedFiles':0,'totalBytes':0,'extensions':{},'topDirectories':{}}
          stats['linkCount']=len(links)
          rec={k:public_clean(repo.get(k,'')) if isinstance(repo.get(k,''), str) else repo.get(k) for k in ['id','name','cluster','url','docs','sourceType','priority','tags']}
          rec.update({'sourceStatus':source_status,'remoteFetchStatus':remote_status,'fileCount':stats['fileCount'],'linkCount':stats['linkCount'],'stats':stats,'page':f"pages/source-{slug(repo['id'])}.html",'pageUrl':f"{BASE}/pages/source-{slug(repo['id'])}.html"})
          repo_records.append(rec); all_files.extend(files); all_links.extend(links)
          write(PAGES/f"source-{slug(repo['id'])}.html", repo_page(repo, stats, files, links))
        except Exception as exc:
          errors.append({'repoId':repo['id'],'error':public_clean(str(exc))})
      domains=Counter([l.get('domain','') for l in all_links if l.get('domain')])
      clusters=Counter([f.get('cluster','') for f in all_files])
      out={'schemaVersion':'2.0','generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),'timeoutBudgetSeconds':budget,'remoteFetchEnabled':fetch_remote,'repositories':repo_records,'files':all_files,'summary':{'repoCount':len(repo_records),'indexedRepoCount':sum(1 for r in repo_records if r['fileCount']>0),'fileCount':len(all_files),'linkCount':len(all_links),'topDomains':dict(domains.most_common(50)),'clusters':dict(clusters)},'errors':errors}
      write(DOCS/'source-index.json', json.dumps(out, indent=2))
      write(DOCS/'source-link-index.json', json.dumps({'schemaVersion':'2.0','links':all_links,'summary':{'linkCount':len(all_links),'domains':dict(domains.most_common(100))}}, indent=2))
      write(DOCS/'repo-file-search.html', search_page())
      rows='\n'.join(f"- [{r['name']}]({r['page']}) — {r['fileCount']} files, {r['linkCount']} links, {r['sourceStatus']}" for r in repo_records)
      merge_source_urls_into_sitemap(repo_records)
      append_source_llms(repo_records)
      write(DOCS/'SOURCE_REPOSITORY_INDEX.md', public_clean(f"# Source Repository Index\n\nThis file is generated from `docs/source-repos.json`. Add a repository entry and run `python scripts/build_source_repo_index.py` to rebuild the static file/link search index. To hydrate remote GitHub repos, run with `SOURCE_INDEX_FETCH_REMOTE=1`.\n\n{rows}\n"))
      print(f"SOURCE INDEX OK: {len(repo_records)} repos, {len(all_files)} files, {len(all_links)} links, budget {budget:.1f}s")
      if errors: print('SOURCE INDEX WARNINGS:', json.dumps(errors[:5]))
    finally:
      for d in tmpdirs: shutil.rmtree(d, ignore_errors=True)
if __name__=='__main__': main()
