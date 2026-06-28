from __future__ import annotations

from app.services.store import load_install_receipts, load_webhooks


def get_activity(account_id: str, limit: int = 25) -> dict:
    items = []
    for receipt in load_install_receipts():
        if receipt.get("accountId") != account_id:
            continue
        items.append({
            "timestamp": receipt.get("timestamp", ""),
            "kind": "receipt",
            "summary": f"{receipt.get('action', 'install')} {receipt.get('productId', '')} -> {receipt.get('targetVersion', '')}",
            "status": receipt.get("status", "unknown"),
            "machineId": receipt.get("machineId", ""),
        })
    for webhook in load_webhooks():
        payload = webhook.get("payload", {})
        if payload.get("accountId") != account_id:
            continue
        items.append({
            "timestamp": webhook.get("timestamp", ""),
            "kind": "webhook",
            "summary": f"{webhook.get('eventType', 'webhook')} ({payload.get('grant', 'no_grant')})",
            "status": "accepted" if webhook.get("accepted", False) else "ignored",
            "machineId": payload.get("machineId", ""),
        })
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {
        "accountId": account_id,
        "count": len(items),
        "items": items[:limit],
    }
