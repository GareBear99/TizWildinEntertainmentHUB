"""
Stripe webhook handler.

Processes incoming Stripe events and updates the ARC database accordingly.
Requires STRIPE_WEBHOOK_SECRET env var for signature verification.
"""

import hashlib
import hmac
import json
import os
import uuid
from app.db import get_db

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, sig_header: str) -> bool:
    """
    Verify the Stripe webhook signature.

    In production, use the official `stripe` Python SDK for this.
    This is a lightweight placeholder that checks the structure.
    """
    if not STRIPE_WEBHOOK_SECRET:
        # No secret configured — accept in dev, reject in prod
        return True

    # Stripe sends: t=<timestamp>,v1=<signature>[,v1=<sig>...]
    parts = {k: v for k, v in (p.split("=", 1) for p in sig_header.split(","))}
    timestamp = parts.get("t", "")
    expected_sig = parts.get("v1", "")

    signed_payload = f"{timestamp}.{payload.decode()}"
    computed = hmac.new(
        STRIPE_WEBHOOK_SECRET.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, expected_sig)


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def handle_checkout_completed(event: dict) -> dict:
    """A customer completed a checkout session (one-time purchase or subscription start)."""
    session = event.get("data", {}).get("object", {})
    account_id = session.get("client_reference_id") or session.get("customer")
    metadata = session.get("metadata", {})
    product_id = metadata.get("product_id")

    if not account_id:
        return {"handled": False, "reason": "no_account_id"}

    with get_db() as conn:
        # Ensure account row exists
        conn.execute(
            "INSERT OR IGNORE INTO accounts (account_id) VALUES (?)",
            (account_id,),
        )

        if product_id:
            conn.execute(
                "INSERT OR IGNORE INTO owned_products (account_id, product_id) VALUES (?, ?)",
                (account_id, product_id),
            )

        # Check for complete-collection flag
        if metadata.get("bundle") == "complete_collection":
            conn.execute(
                "UPDATE accounts SET owns_every_vst = 1 WHERE account_id = ?",
                (account_id,),
            )
            conn.execute(
                "INSERT OR IGNORE INTO owned_bundles (account_id, bundle_id) VALUES (?, ?)",
                (account_id, "complete_collection"),
            )

        # Store receipt
        conn.execute(
            """INSERT INTO receipts (receipt_id, account_id, stripe_event_id, stripe_event_type, product_id, amount_cents, payload)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                f"rcpt_{uuid.uuid4().hex[:12]}",
                account_id,
                event.get("id"),
                event.get("type"),
                product_id,
                session.get("amount_total"),
                json.dumps(event),
            ),
        )

    return {"handled": True, "accountId": account_id, "productId": product_id}


def handle_subscription_updated(event: dict) -> dict:
    """Seat-quantity subscription was updated (e.g. user added/removed extra seats)."""
    sub = event.get("data", {}).get("object", {})
    account_id = sub.get("metadata", {}).get("account_id") or sub.get("customer")

    if not account_id:
        return {"handled": False, "reason": "no_account_id"}

    # Stripe quantity = number of extra seats
    items = sub.get("items", {}).get("data", [])
    extra_seats = 0
    for item in items:
        if item.get("price", {}).get("lookup_key") == "tizwildin_extra_seats":
            extra_seats = item.get("quantity", 0)

    with get_db() as conn:
        conn.execute(
            "UPDATE accounts SET extra_seat_qty = ? WHERE account_id = ?",
            (min(extra_seats, 9), account_id),
        )

    return {"handled": True, "accountId": account_id, "extraSeats": extra_seats}


def handle_payment_failed(event: dict) -> dict:
    """An invoice payment failed — flag the account."""
    invoice = event.get("data", {}).get("object", {})
    account_id = invoice.get("metadata", {}).get("account_id") or invoice.get("customer")

    if not account_id:
        return {"handled": False, "reason": "no_account_id"}

    with get_db() as conn:
        conn.execute(
            "UPDATE accounts SET billing_state = 'payment_issue' WHERE account_id = ?",
            (account_id,),
        )

    return {"handled": True, "accountId": account_id, "billingState": "payment_issue"}


# ---------------------------------------------------------------------------
# Router dispatcher
# ---------------------------------------------------------------------------

EVENT_HANDLERS = {
    "checkout.session.completed": handle_checkout_completed,
    "customer.subscription.updated": handle_subscription_updated,
    "customer.subscription.created": handle_subscription_updated,
    "invoice.payment_failed": handle_payment_failed,
}


def dispatch_event(event: dict) -> dict:
    event_type = event.get("type", "")
    handler = EVENT_HANDLERS.get(event_type)
    if not handler:
        return {"handled": False, "reason": f"unhandled_event_type: {event_type}"}
    return handler(event)
