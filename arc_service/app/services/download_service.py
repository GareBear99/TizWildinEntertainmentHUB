from __future__ import annotations
from datetime import datetime, UTC
import uuid
from app.models.domain import DownloadPlanRequest
from app.services.entitlement_service import get_entitlement, resolve_product_access
from app.services.install_plan_service import build_install_plan
from app.services.release_service import get_release_manifest
from app.services.store import load_install_receipts, save_install_receipts


def build_download_plan(request: DownloadPlanRequest) -> dict:
    entitlement = get_entitlement(request.accountId)
    if not entitlement:
        return {"approved": False, "reason": "unknown_account", "downloads": []}

    plan = build_install_plan(request)
    manifests = get_release_manifest(channel=request.channel)
    downloads = []
    for action in plan.get("actions", []):
        product_id = action.get("productId")
        manifest = manifests.get(product_id, {})
        access = resolve_product_access(entitlement, product_id)
        if action.get("action") not in {"install_free_source", "build_from_source", "update_available"}:
            continue
        if not access.get("allowed") and action.get("action") != "install_free_source":
            continue
        downloads.append({
            "productId": product_id,
            "action": action.get("action"),
            "targetVersion": manifest.get("latestVersion"),
            "artifactMode": manifest.get("artifactMode", "source"),
            "artifactUrl": manifest.get("artifactUrl", ""),
            "artifactPath": manifest.get("artifactPath", ""),
            "sha256": manifest.get("sha256", ""),
            "signature": manifest.get("signature", "unsigned"),
            "channel": request.channel,
            "verificationRequired": True,
            "steps": [
                "download_artifact",
                "verify_sha256",
                "verify_signature_marker",
                "expand_or_clone",
                "record_receipt",
            ],
        })

    return {
        "approved": True,
        "accountId": request.accountId,
        "machineId": request.machineId,
        "channel": request.channel,
        "downloads": downloads,
    }


def record_install_receipt(account_id: str, machine_id: str, download: dict, status: str = "planned", verification_passed: bool = False, installed_path: str = "") -> dict:
    receipts = load_install_receipts()
    receipt = {
        "receiptId": f"rcpt_{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(UTC).isoformat(),
        "accountId": account_id,
        "machineId": machine_id,
        "productId": download.get("productId"),
        "action": download.get("action"),
        "targetVersion": download.get("targetVersion"),
        "artifactMode": download.get("artifactMode"),
        "sha256": download.get("sha256", ""),
        "status": status,
        "channel": download.get("channel", "stable"),
        "verificationPassed": verification_passed,
        "installedPath": installed_path,
    }
    receipts.append(receipt)
    save_install_receipts(receipts)
    return receipt


def list_receipts(account_id: str) -> list[dict]:
    return [r for r in load_install_receipts() if r.get("accountId") == account_id]
