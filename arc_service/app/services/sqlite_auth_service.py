from __future__ import annotations

import hashlib
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.services.store import DATA_DIR, load_entitlements, save_entitlements, load_settings, save_settings

DB_PATH = DATA_DIR / "arc_local_auth.sqlite3"
SESSION_MINUTES = 60 * 24
REFRESH_DAYS = 30


def _conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        account_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        display_name TEXT,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        access_token TEXT PRIMARY KEY,
        refresh_token TEXT UNIQUE NOT NULL,
        account_id TEXT NOT NULL,
        machine_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        refresh_expires_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS oauth_links (
        provider TEXT NOT NULL,
        provider_user_id TEXT NOT NULL,
        account_id TEXT NOT NULL,
        provider_username TEXT,
        provider_avatar_url TEXT,
        provider_email TEXT,
        sc_access_token TEXT,
        linked_at TEXT NOT NULL,
        PRIMARY KEY (provider, provider_user_id)
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS email_subscribers (
        email TEXT PRIMARY KEY,
        source TEXT NOT NULL DEFAULT 'soundcloud',
        sc_username TEXT,
        display_name TEXT,
        subscribed_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS radio_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id TEXT NOT NULL,
        url TEXT NOT NULL,
        file_name TEXT,
        score INTEGER DEFAULT 0,
        passed INTEGER DEFAULT 0,
        submitted_at TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS verified_accounts (
        account_id TEXT PRIMARY KEY,
        verified_at TEXT NOT NULL,
        reason TEXT NOT NULL DEFAULT 'radio_submissions'
    )
    """)
    conn.commit()
    return conn


def _now() -> datetime:
    return datetime.now(UTC)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()


def _make_account_id(email: str) -> str:
    stem = email.lower().split("@")[0]
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in stem).strip("_") or "user"
    return f"acct_{cleaned}"


def _new_session(account_id: str, machine_id: str) -> dict:
    now = _now()
    access_token = f"arc_{secrets.token_urlsafe(24)}"
    refresh_token = f"rfr_{secrets.token_urlsafe(30)}"
    expires_at = now + timedelta(minutes=SESSION_MINUTES)
    refresh_expires_at = now + timedelta(days=REFRESH_DAYS)
    with _conn() as conn:
        conn.execute(
            "INSERT INTO sessions (access_token, refresh_token, account_id, machine_id, created_at, expires_at, refresh_expires_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')",
            (access_token, refresh_token, account_id, machine_id, now.isoformat(), expires_at.isoformat(), refresh_expires_at.isoformat()),
        )
        conn.commit()
    return {
        "approved": True,
        "accountId": account_id,
        "machineId": machine_id,
        "token": access_token,
        "refreshToken": refresh_token,
        "issuedAt": now.isoformat(),
        "expiresAt": expires_at.isoformat(),
        "mode": "local",
    }


def ensure_local_account(account_id: str, email: str | None = None, display_name: str | None = None) -> None:
    ent = load_entitlements()
    if account_id not in ent:
        ent[account_id] = {
            "accountId": account_id,
            "ownsEveryVST": False,
            "ownedProducts": [],
            "ownedBundles": [],
            "extraSeatQuantity": 0,
            "billingState": "active",
        }
        save_entitlements(ent)
    settings = load_settings()
    if account_id not in settings:
        settings[account_id] = {
            "machineId": "mac_local",
            "preferredChannel": "stable",
            "theme": "dark",
            "arcBaseUrl": "http://127.0.0.1:8000",
            "installRoot": "/tmp/tizhub_installs",
            "autoStageOnBootstrap": True,
            "autoBackupBeforeExecute": True,
        }
        save_settings(settings)


def register_local_user(email: str, password: str, machine_id: str = "mac_local", display_name: str | None = None) -> dict:
    email_norm = email.strip().lower()
    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    account_id = _make_account_id(email_norm)
    now = _now().isoformat()
    try:
        with _conn() as conn:
            conn.execute(
                "INSERT INTO users (account_id, email, display_name, password_hash, salt, created_at, status) VALUES (?, ?, ?, ?, ?, ?, 'active')",
                (account_id, email_norm, display_name or account_id, password_hash, salt, now),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return {"approved": False, "reason": "email_exists"}
    ensure_local_account(account_id, email_norm, display_name)
    session = _new_session(account_id, machine_id)
    session["email"] = email_norm
    session["displayName"] = display_name or account_id
    session["newAccount"] = True
    return session


def login_local_user(email: str, password: str, machine_id: str = "mac_local") -> dict:
    email_norm = email.strip().lower()
    with _conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ? AND status = 'active'", (email_norm,)).fetchone()
    if not row:
        return {"approved": False, "reason": "invalid_credentials"}
    expected = _hash_password(password, row["salt"])
    if expected != row["password_hash"]:
        return {"approved": False, "reason": "invalid_credentials"}
    ensure_local_account(row["account_id"], email_norm, row["display_name"])
    session = _new_session(row["account_id"], machine_id)
    session["email"] = email_norm
    session["displayName"] = row["display_name"]
    return session


def get_session(access_token: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT s.*, u.email, u.display_name FROM sessions s LEFT JOIN users u ON u.account_id = s.account_id WHERE s.access_token = ?", (access_token,)).fetchone()
    if not row or row["status"] != "active":
        return None
    if datetime.fromisoformat(row["expires_at"]) < _now():
        revoke_session(access_token)
        return None
    return {
        "approved": True,
        "accountId": row["account_id"],
        "machineId": row["machine_id"],
        "token": row["access_token"],
        "refreshToken": row["refresh_token"],
        "issuedAt": row["created_at"],
        "expiresAt": row["expires_at"],
        "mode": "local",
        "email": row["email"],
        "displayName": row["display_name"],
    }


def refresh_session(refresh_token: str, machine_id: str = "mac_local") -> dict:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE refresh_token = ? AND status = 'active'", (refresh_token,)).fetchone()
    if not row:
        return {"approved": False, "reason": "invalid_refresh_token"}
    if datetime.fromisoformat(row["refresh_expires_at"]) < _now():
        revoke_session(row["access_token"])
        return {"approved": False, "reason": "refresh_expired"}
    revoke_session(row["access_token"])
    return _new_session(row["account_id"], machine_id or row["machine_id"])


def revoke_session(access_token: str) -> dict:
    with _conn() as conn:
        row = conn.execute("SELECT access_token FROM sessions WHERE access_token = ?", (access_token,)).fetchone()
        if not row:
            return {"approved": False, "reason": "invalid_token"}
        conn.execute("UPDATE sessions SET status = 'revoked' WHERE access_token = ?", (access_token,))
        conn.commit()
    return {"approved": True, "reason": "token_revoked", "token": access_token}


def upsert_oauth_link(
    provider: str,
    provider_user_id: str,
    account_id: str,
    provider_username: str | None = None,
    provider_avatar_url: str | None = None,
    provider_email: str | None = None,
    sc_access_token: str | None = None,
) -> None:
    now = _now().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO oauth_links (provider, provider_user_id, account_id, provider_username, provider_avatar_url, provider_email, sc_access_token, linked_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(provider, provider_user_id) DO UPDATE SET "
            "account_id=excluded.account_id, provider_username=excluded.provider_username, "
            "provider_avatar_url=excluded.provider_avatar_url, provider_email=excluded.provider_email, "
            "sc_access_token=excluded.sc_access_token, linked_at=excluded.linked_at",
            (provider, provider_user_id, account_id, provider_username, provider_avatar_url, provider_email, sc_access_token, now),
        )
        conn.commit()


def get_oauth_link(provider: str, provider_user_id: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM oauth_links WHERE provider = ? AND provider_user_id = ?",
            (provider, provider_user_id),
        ).fetchone()
    if not row:
        return None
    return dict(row)


def subscribe_email(
    email: str,
    source: str = "soundcloud",
    sc_username: str | None = None,
    display_name: str | None = None,
) -> None:
    now = _now().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO email_subscribers (email, source, sc_username, display_name, subscribed_at, status) "
            "VALUES (?, ?, ?, ?, ?, 'active') "
            "ON CONFLICT(email) DO UPDATE SET source=excluded.source, sc_username=excluded.sc_username, "
            "display_name=excluded.display_name, status='active'",
            (email, source, sc_username, display_name, now),
        )
        conn.commit()


def list_email_subscribers() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM email_subscribers WHERE status = 'active' ORDER BY subscribed_at DESC").fetchall()
    return [dict(r) for r in rows]


# ── Radio submissions + verified badge ──────────────────────────────

VERIFIED_THRESHOLD = 3  # 3 accepted songs = verified


def record_radio_submission(
    account_id: str, url: str, file_name: str, score: int, passed: bool
) -> dict:
    """Record a radio submission and check if account should be verified."""
    now = _now().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO radio_submissions (account_id, url, file_name, score, passed, submitted_at) VALUES (?, ?, ?, ?, ?, ?)",
            (account_id, url, file_name, score, 1 if passed else 0, now),
        )
        conn.commit()

    if passed:
        accepted = count_accepted_submissions(account_id)
        if accepted >= VERIFIED_THRESHOLD and not is_verified(account_id):
            verify_account(account_id, reason=f"radio_submissions_{accepted}")
            return {"newlyVerified": True, "acceptedCount": accepted}

    return {"newlyVerified": False, "acceptedCount": count_accepted_submissions(account_id)}


def count_accepted_submissions(account_id: str) -> int:
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM radio_submissions WHERE account_id = ? AND passed = 1",
            (account_id,),
        ).fetchone()
    return row["cnt"] if row else 0


def verify_account(account_id: str, reason: str = "radio_submissions") -> None:
    now = _now().isoformat()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO verified_accounts (account_id, verified_at, reason) VALUES (?, ?, ?) "
            "ON CONFLICT(account_id) DO UPDATE SET verified_at=excluded.verified_at, reason=excluded.reason",
            (account_id, now, reason),
        )
        conn.commit()


def is_verified(account_id: str) -> bool:
    with _conn() as conn:
        row = conn.execute(
            "SELECT account_id FROM verified_accounts WHERE account_id = ?",
            (account_id,),
        ).fetchone()
    return row is not None


def get_verification_status(account_id: str) -> dict:
    accepted = count_accepted_submissions(account_id)
    verified = is_verified(account_id)
    return {
        "verified": verified,
        "acceptedSubmissions": accepted,
        "threshold": VERIFIED_THRESHOLD,
        "remaining": max(0, VERIFIED_THRESHOLD - accepted) if not verified else 0,
    }
