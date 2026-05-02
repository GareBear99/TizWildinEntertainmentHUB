from __future__ import annotations
from pathlib import Path
import shutil
from app.models.domain import DownloadPlanRequest, ExecuteDownloadsRequest, RepairRequest, RollbackRequest, UninstallRequest
from app.services.artifact_service import install_artifact, verify_artifact
from app.services.remote_artifact_service import fetch_artifact
from app.services.download_service import build_download_plan, list_receipts, record_install_receipt
from app.services.store import load_install_scans, save_install_scans

DEFAULT_INSTALL_ROOT = Path(__file__).resolve().parents[3] / "runtime_installs"


def _latest_machine_entry(scans: list[dict], account_id: str, machine_id: str) -> dict:
    for entry in reversed(scans):
        if entry.get("accountId") == account_id and entry.get("machineId") == machine_id:
            return entry
    entry = {"accountId": account_id, "machineId": machine_id, "products": []}
    scans.append(entry)
    return entry


def _find_product_entry(machine_entry: dict, product_id: str) -> dict | None:
    for product in machine_entry.setdefault("products", []):
        if product.get("productId") == product_id:
            return product
    return None


def _upsert_scan(account_id: str, machine_id: str, product_id: str, version: str, installed_path: str, channel: str, artifact_mode: str) -> None:
    scans = load_install_scans()
    machine_entry = _latest_machine_entry(scans, account_id, machine_id)

    products = machine_entry.setdefault("products", [])
    found = _find_product_entry(machine_entry, product_id)
    if found is None:
        found = {"productId": product_id}
        products.append(found)

    found.update({
        "localVersion": version,
        "runtimeVersion": version,
        "installState": "installed",
        "binaryPresent": artifact_mode in {"binary", "file", "zip"},
        "sourcePresent": artifact_mode in {"source", "directory", "zip"},
        "installedPath": installed_path,
        "channel": channel,
    })
    save_install_scans(scans)


def _mark_uninstalled(account_id: str, machine_id: str, product_id: str) -> dict:
    scans = load_install_scans()
    machine_entry = _latest_machine_entry(scans, account_id, machine_id)
    found = _find_product_entry(machine_entry, product_id)
    if found is None:
        found = {"productId": product_id}
        machine_entry.setdefault("products", []).append(found)
    found.update({
        "localVersion": None,
        "runtimeVersion": None,
        "installState": "not_installed",
        "binaryPresent": False,
        "sourcePresent": False,
        "installedPath": "",
    })
    save_install_scans(scans)
    return found


def execute_downloads(request: ExecuteDownloadsRequest) -> dict:
    plan = build_download_plan(DownloadPlanRequest(
        accountId=request.accountId,
        machineId=request.machineId,
        requestedProducts=request.requestedProducts,
        channel=request.channel,
    ))
    if not plan.get("approved"):
        return {"approved": False, "reason": plan.get("reason", "plan_failed"), "executed": []}

    install_root = Path(request.installRoot) if request.installRoot else DEFAULT_INSTALL_ROOT / request.accountId / request.machineId
    install_root.mkdir(parents=True, exist_ok=True)

    executed = []
    for download in plan.get("downloads", []):
        if request.dryRun:
            receipt = record_install_receipt(request.accountId, request.machineId, download, status="dry_run_planned")
            executed.append({
                "productId": download.get("productId"),
                "status": "dry_run_planned",
                "receiptId": receipt.get("receiptId"),
                "targetVersion": download.get("targetVersion"),
                "steps": download.get("steps", []),
            })
            continue

        artifact_path = download.get("artifactPath", "")
        if (not artifact_path) and download.get("artifactUrl"):
            fetched = fetch_artifact(download.get("artifactUrl"), download.get("productId"), download.get("targetVersion", "0.0.0"), download.get("sha256"))
            if not fetched.get("ok"):
                receipt = record_install_receipt(request.accountId, request.machineId, download, status=fetched.get("reason", "download_failed"), verification_passed=False)
                executed.append({
                    "productId": download.get("productId"),
                    "status": fetched.get("reason", "download_failed"),
                    "receiptId": receipt.get("receiptId"),
                    "targetVersion": download.get("targetVersion"),
                    "steps": download.get("steps", []),
                })
                continue
            artifact_path = fetched.get("artifactPath", "")

        verification = verify_artifact(artifact_path, download.get("sha256"), download.get("signature"))
        if not verification.get("ok"):
            receipt = record_install_receipt(request.accountId, request.machineId, download, status=verification.get("reason", "verification_failed"), verification_passed=False)
            executed.append({
                "productId": download.get("productId"),
                "status": verification.get("reason", "verification_failed"),
                "receiptId": receipt.get("receiptId"),
                "targetVersion": download.get("targetVersion"),
                "steps": download.get("steps", []),
            })
            continue

        install_result = install_artifact(artifact_path, install_root, download.get("productId"), download.get("targetVersion", "0.0.0"))
        receipt = record_install_receipt(
            request.accountId,
            request.machineId,
            download,
            status="executed",
            verification_passed=True,
            installed_path=install_result.get("installedPath", ""),
        )
        _upsert_scan(
            request.accountId,
            request.machineId,
            download.get("productId"),
            download.get("targetVersion", "0.0.0"),
            install_result.get("installedPath", ""),
            download.get("channel", request.channel),
            install_result.get("artifactModeResolved", download.get("artifactMode", "source")),
        )
        executed.append({
            "productId": download.get("productId"),
            "status": "executed",
            "receiptId": receipt.get("receiptId"),
            "targetVersion": download.get("targetVersion"),
            "installedPath": install_result.get("installedPath", ""),
            "steps": download.get("steps", []),
        })

    return {
        "approved": True,
        "accountId": request.accountId,
        "machineId": request.machineId,
        "channel": request.channel,
        "dryRun": request.dryRun,
        "installRoot": str(install_root),
        "executed": executed,
    }


def uninstall_product(request: UninstallRequest) -> dict:
    scans = load_install_scans()
    machine_entry = _latest_machine_entry(scans, request.accountId, request.machineId)
    found = _find_product_entry(machine_entry, request.productId)
    if not found or found.get("installState") != "installed":
        return {"approved": False, "reason": "not_installed", "productId": request.productId}

    installed_path = Path(found.get("installedPath", ""))
    if installed_path.exists():
        shutil.rmtree(installed_path, ignore_errors=True)
    current_file = installed_path.parents[1] / "CURRENT" if len(installed_path.parents) >= 2 else None
    if current_file and current_file.exists():
        current_file.unlink()

    _mark_uninstalled(request.accountId, request.machineId, request.productId)
    receipt = record_install_receipt(request.accountId, request.machineId, {
        "productId": request.productId,
        "action": "uninstall",
        "targetVersion": "removed",
        "artifactMode": "local",
        "sha256": "",
        "channel": found.get("channel", "stable"),
    }, status="uninstalled", verification_passed=True, installed_path="")
    return {"approved": True, "productId": request.productId, "status": "uninstalled", "receiptId": receipt.get("receiptId")}


def repair_product(request: RepairRequest) -> dict:
    return execute_downloads(ExecuteDownloadsRequest(
        accountId=request.accountId,
        machineId=request.machineId,
        requestedProducts=[request.productId],
        channel=request.channel,
        dryRun=False,
        installRoot=request.installRoot,
    ))


def rollback_product(request: RollbackRequest) -> dict:
    receipts = [r for r in list_receipts(request.accountId) if r.get("machineId") == request.machineId and r.get("productId") == request.productId and r.get("status") == "executed"]
    if len(receipts) < 2:
        return {"approved": False, "reason": "no_previous_version"}

    receipts.sort(key=lambda r: r.get("timestamp", ""))
    previous = receipts[-2]
    _upsert_scan(
        request.accountId,
        request.machineId,
        request.productId,
        previous.get("targetVersion", "0.0.0"),
        previous.get("installedPath", ""),
        previous.get("channel", "stable"),
        previous.get("artifactMode", "source"),
    )
    return {
        "approved": True,
        "productId": request.productId,
        "rolledBackTo": previous.get("targetVersion"),
        "installedPath": previous.get("installedPath", ""),
    }
