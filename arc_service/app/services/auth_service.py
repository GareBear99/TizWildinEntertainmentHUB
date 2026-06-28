from __future__ import annotations
from datetime import UTC, datetime
import uuid
from app.services.store import load_entitlements, load_auth_tokens, save_auth_tokens
from app.services.sqlite_auth_service import (
    get_session,
    login_local_user,
    refresh_session,
    register_local_user,
    revoke_session,
)


def mock_login(account_id: str, machine_id: str) -> dict:
    entitlements = load_entitlements()
    if account_id not in entitlements:
        return {"approved": False, "reason": "unknown_account"}

    token = f"mock_{uuid.uuid4().hex}"
    tokens = load_auth_tokens()
    tokens[token] = {
        "accountId": account_id,
        "machineId": machine_id,
        "issuedAt": datetime.now(UTC).isoformat(),
        "mode": "mock",
        "status": "active",
    }
    save_auth_tokens(tokens)
    return {"approved": True, "accountId": account_id, "machineId": machine_id, "token": token}


def local_register(email: str, password: str, machine_id: str = "mac_local", display_name: str | None = None) -> dict:
    return register_local_user(email, password, machine_id, display_name)


def local_login(email: str, password: str, machine_id: str = "mac_local") -> dict:
    return login_local_user(email, password, machine_id)


def local_refresh(refresh_token: str, machine_id: str = "mac_local") -> dict:
    return refresh_session(refresh_token, machine_id)


def resolve_token(token: str) -> dict | None:
    local = get_session(token)
    if local:
        return local
    record = load_auth_tokens().get(token)
    if not record or record.get("status") != "active":
        return None
    return record


def validate_token(token: str) -> dict:
    record = resolve_token(token)
    if not record:
        return {"approved": False, "reason": "invalid_token"}
    return {"approved": True, **record}


def revoke_token(token: str) -> dict:
    local = revoke_session(token)
    if local.get("approved"):
        return local
    tokens = load_auth_tokens()
    record = tokens.get(token)
    if not record:
        return {"approved": False, "reason": "invalid_token"}
    record["status"] = "revoked"
    record["revokedAt"] = datetime.now(UTC).isoformat()
    save_auth_tokens(tokens)
    return {"approved": True, "reason": "token_revoked", "token": token}
