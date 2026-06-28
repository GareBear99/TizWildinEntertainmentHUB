from __future__ import annotations
import hashlib
import json
from pathlib import Path

def digest(seed: str) -> str:
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()

root = Path(__file__).resolve().parent.parent
catalog = json.loads((root / 'manifests' / 'products.catalog.json').read_text())
out = {}
for p in catalog['products']:
    product_id = p['productId']
    version = '0.1.0' if p.get('status') == 'coming_soon' else '1.0.0-demo'
    out[product_id] = {
        'productId': product_id,
        'channel': 'stable',
        'latestVersion': version,
        'artifactMode': 'source',
        'artifactUrl': f'https://github.com/GareBear99/{product_id}',
        'sha256': digest(product_id + version),
        'signature': 'arc-demo-generated'
    }
(root / 'arc_service' / 'app' / 'data' / 'release_manifests.mock.json').write_text(json.dumps(out, indent=2))
print('generated release_manifests.mock.json')
