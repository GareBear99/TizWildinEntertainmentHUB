#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, time, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
STEPS=[
  ('public-index-build', [sys.executable,'scripts/build_public_index.py'], 120),
  ('public-index-validate', [sys.executable,'scripts/validate_public_index.py'], 60),
  ('branch-map-validate', [sys.executable,'scripts/validate_branch_map.py'], 60),
  ('source-index-build', [sys.executable,'scripts/build_source_repo_index.py'], 180),
  ('source-index-validate', [sys.executable,'scripts/validate_source_index.py'], 60),
  ('search-index-build', [sys.executable,'scripts/build_search_index.py'], 90),
  ('public-links-check', [sys.executable,'scripts/check_public_links.py'], 90),
  ('repo-readiness-score', [sys.executable,'scripts/score_repository_readiness.py'], 90),
  ('index-health-build', [sys.executable,'scripts/build_index_health.py'], 60),
]
results=[]; start=time.perf_counter(); failures=0
for name, cmd, timeout in STEPS:
    t=time.perf_counter()
    p=subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    seconds=round(time.perf_counter()-t,3)
    failures += 0 if p.returncode == 0 else 1
    results.append({'name':name,'seconds':seconds,'timeoutSeconds':timeout,'returncode':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()})
total=round(time.perf_counter()-start,3)
# Production grading prioritizes correctness first, then speed/headroom.
if failures:
    grade='F - validation failures must be fixed before release'
elif total <= 18:
    grade='A - fast, validated, and production-ready for current repo graph'
elif total <= 30:
    grade='A- - validated and production-ready; monitor as repo graph grows'
elif total <= 45:
    grade='B+ - validated but should be split into parallel CI jobs as graph grows'
else:
    grade='B - valid but too slow for top-tier growth without CI parallelization'
out={'schemaVersion':'2.0','generatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),'results':results,'totalSeconds':total,'grade':grade,'recommendation':'Keep public-index, branch validation, source-index, search-index, link-check, and readiness scoring as separate CI jobs once the graph passes 25 repositories.'}
(DOCS/'PUBLIC_INDEX_BENCHMARK.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
sys.exit(1 if failures else 0)
