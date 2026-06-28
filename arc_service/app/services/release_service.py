from __future__ import annotations
from app.services.artifact_service import ensure_demo_artifact
from app.services.store import load_release_manifests, save_release_manifests


def get_release_manifest(product_id: str | None = None, channel: str | None = None) -> dict:
    manifests = load_release_manifests()
    if product_id is not None:
        manifest = manifests.get(product_id, {})
        if channel and manifest and manifest.get("channel", "stable") != channel:
            return {}
        return manifest
    if channel is None:
        return manifests
    return {pid: manifest for pid, manifest in manifests.items() if manifest.get("channel", "stable") == channel}



def stage_local_artifacts(channel: str | None = None) -> dict:
    manifests = load_release_manifests()
    mutated = {}
    for product_id, manifest in manifests.items():
        if channel and manifest.get("channel", "stable") != channel:
            continue
        staged = ensure_demo_artifact(product_id, manifest.get("latestVersion", "0.0.0"))
        manifest.update(staged)
        mutated[product_id] = manifest
    save_release_manifests(manifests)
    return mutated
