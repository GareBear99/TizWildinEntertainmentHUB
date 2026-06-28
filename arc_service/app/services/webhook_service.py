from datetime import datetime, UTC
import os
from app.models.domain import WebhookEvent
from app.services.store import load_webhooks, save_webhooks, load_entitlements, save_entitlements


DEFAULT_WEBHOOK_SECRET = "arc_demo_secret"


def _verify_signature(event: WebhookEvent) -> dict:
    expected = os.getenv("ARC_WEBHOOK_SECRET", DEFAULT_WEBHOOK_SECRET)
    if event.provider != "stripe":
        return {"verified": True, "reason": "provider_unchecked"}
    if event.signature == expected:
        return {"verified": True, "reason": "signature_ok"}
    return {"verified": False, "reason": "invalid_signature"}



def _apply_mock_mutation(event: WebhookEvent) -> dict:
    payload = event.payload or {}
    account_id = payload.get("accountId")
    if not account_id:
        return {"mutated": False, "reason": "missing_account_id"}

    entitlements = load_entitlements()
    entitlement = entitlements.get(account_id)
    if not entitlement:
        return {"mutated": False, "reason": "unknown_account"}

    if event.eventType == "checkout.session.completed":
        grant = payload.get("grant")
        if grant == "complete_collection":
            entitlement["ownsEveryVST"] = True
            if "complete_collection" not in entitlement.get("ownedBundles", []):
                entitlement.setdefault("ownedBundles", []).append("complete_collection")
            save_entitlements(entitlements)
            return {"mutated": True, "reason": "complete_collection_granted"}
        if grant == "extra_seats":
            qty = int(payload.get("quantity", 0))
            entitlement["extraSeatQuantity"] = max(0, min(9, qty))
            save_entitlements(entitlements)
            return {"mutated": True, "reason": "extra_seats_updated", "extraSeatQuantity": entitlement["extraSeatQuantity"]}

    if event.eventType == "invoice.payment_failed":
        entitlement["billingState"] = "payment_issue"
        save_entitlements(entitlements)
        return {"mutated": True, "reason": "billing_state_payment_issue"}

    if event.eventType == "invoice.payment_succeeded":
        entitlement["billingState"] = "active"
        save_entitlements(entitlements)
        return {"mutated": True, "reason": "billing_state_active"}

    return {"mutated": False, "reason": "no_mock_rule"}



def ingest_webhook(event: WebhookEvent) -> dict:
    verification = _verify_signature(event)
    events = load_webhooks()
    mutation = {"mutated": False, "reason": "verification_failed"}
    accepted = verification.get("verified", False)
    if accepted:
        mutation = _apply_mock_mutation(event)
    events.append({
        "timestamp": datetime.now(UTC).isoformat(),
        "provider": event.provider,
        "eventType": event.eventType,
        "payload": event.payload,
        "signatureVerified": verification.get("verified", False),
        "verificationReason": verification.get("reason"),
        "mutation": mutation,
    })
    save_webhooks(events)
    return {"accepted": accepted, "stored": True, "verification": verification, "mutation": mutation}
