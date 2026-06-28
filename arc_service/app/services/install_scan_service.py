from datetime import datetime, UTC
from app.models.domain import InstallScanReport
from app.services.store import load_install_scans, save_install_scans


def record_install_scan(report: InstallScanReport) -> dict:
    scans = load_install_scans()
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "accountId": report.accountId,
        "machineId": report.machineId,
        "products": [p.model_dump() for p in report.products],
    }
    scans.append(entry)
    save_install_scans(scans)
    return {
        "accepted": True,
        "machineId": report.machineId,
        "productCount": len(report.products),
        "message": "install scan recorded",
    }
