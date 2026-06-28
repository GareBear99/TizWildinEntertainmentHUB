from __future__ import annotations

from datetime import UTC, datetime
import uuid

from app.services.store import load_entitlements, save_entitlements, load_webhooks, save_webhooks

PRICE_MAP = {
    "complete_collection": {"grant": "complete_collection", "kind": "bundle"},
    "extra_seat": {"grant": "extra_seats", "kind": "seat"},
}


def create_checkout_session(account_id: str, product_id: str, quantity: int = 1, price_id: str | None = None, success_url: str = '', cancel_url: str = '') -> dict:
    entitlements = load_entitlements()
    if account_id not in entitlements:
        return {"approved": False, "reason": "unknown_account"}
    if product_id not in PRICE_MAP and product_id not in {"freeeq8", "therum", "paintmask", "whispergate", "waveform_pro", "riftsynth_pro", "aether", "wurp"}:
        return {"approved": False, "reason": "unknown_product"}
    checkout_id = f"chk_{uuid.uuid4().hex[:12]}"
    return {
        "approved": True,
        "checkoutId": checkout_id,
        "accountId": account_id,
        "productId": product_id,
        "priceId": price_id or f"price_{product_id}",
        "quantity": quantity,
        "status": "pending",
        "successUrl": success_url,
        "cancelUrl": cancel_url,
    }


def complete_checkout(account_id: str, product_id: str, quantity: int = 1) -> dict:
    entitlements = load_entitlements()
    if account_id not in entitlements:
        return {"approved": False, "reason": "unknown_account"}
    entitlement = entitlements[account_id]
    if product_id == "complete_collection":
        entitlement["ownsEveryVST"] = True
        entitlement.setdefault("ownedBundles", [])
        if "complete_collection" not in entitlement["ownedBundles"]:
            entitlement["ownedBundles"].append("complete_collection")
    elif product_id == "extra_seat":
        entitlement["extraSeatQuantity"] = min(9, int(entitlement.get("extraSeatQuantity", 0)) + quantity)
    else:
        entitlement.setdefault("ownedProducts", [])
        if product_id not in entitlement["ownedProducts"]:
            entitlement["ownedProducts"].append(product_id)
    save_entitlements(entitlements)
    events = load_webhooks()
    events.append({
        "timestamp": datetime.now(UTC).isoformat(),
        "provider": "billing_local",
        "eventType": "checkout.completed",
        "payload": {"accountId": account_id, "productId": product_id, "quantity": quantity},
        "signatureVerified": True,
        "verificationReason": "local_checkout",
        "mutation": {"mutated": True, "reason": "local_checkout_complete"},
    })
    save_webhooks(events)
    return {"approved": True, "accountId": account_id, "productId": product_id, "quantity": quantity, "entitlements": entitlement}
