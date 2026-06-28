from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from app.services.store import load_release_manifests, save_release_manifests


def _read_source(source: str) -> dict:
    if source.startswith("http://") or source.startswith("https://") or source.startswith("file://"):
        with urlopen(source) as resp:
            return json.loads(resp.read().decode("utf-8"))
    return json.loads(Path(source).read_text())


def import_release_manifests(source: str, replace_existing: bool = False, channel_override: str | None = None) -> dict:
    incoming = _read_source(source)
    if isinstance(incoming, list):
        normalized = {item["productId"]: item for item in incoming if isinstance(item, dict) and item.get("productId")}
    else:
        normalized = incoming
    manifests = {} if replace_existing else load_release_manifests()
    imported = []
    for product_id, manifest in normalized.items():
        entry = dict(manifest)
        entry.setdefault("productId", product_id)
        if channel_override:
            entry["channel"] = channel_override
        manifests[product_id] = entry
        imported.append(product_id)
    save_release_manifests(manifests)
    return {"approved": True, "imported": sorted(imported), "count": len(imported), "source": source}
