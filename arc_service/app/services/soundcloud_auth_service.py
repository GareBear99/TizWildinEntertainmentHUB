from __future__ import annotations

import os
from urllib.parse import urlencode

import httpx

from app.services.sqlite_auth_service import (
    _make_account_id,
    _new_session,
    ensure_local_account,
    get_oauth_link,
    subscribe_email,
    upsert_oauth_link,
)

SC_AUTH_URL = "https://api.soundcloud.com/connect"
SC_TOKEN_URL = "https://api.soundcloud.com/oauth2/token"
SC_ME_URL = "https://api.soundcloud.com/me"
SC_FOLLOWINGS_URL = "https://api.soundcloud.com/me/followings"


def _client_id() -> str:
    return os.environ.get("SOUNDCLOUD_CLIENT_ID", "")


def _client_secret() -> str:
    return os.environ.get("SOUNDCLOUD_CLIENT_SECRET", "")


def _tizwildin_user_id() -> str:
    return os.environ.get("TIZWILDIN_SC_USER_ID", "")


def get_soundcloud_auth_url(redirect_uri: str) -> dict:
    client_id = _client_id()
    if not client_id:
        return {"approved": False, "reason": "soundcloud_not_configured"}
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "non-expiring",
    }
    return {"approved": True, "url": f"{SC_AUTH_URL}?{urlencode(params)}"}


def handle_soundcloud_callback(code: str, redirect_uri: str) -> dict:
    client_id = _client_id()
    client_secret = _client_secret()
    if not client_id or not client_secret:
        return {"approved": False, "reason": "soundcloud_not_configured"}

    # Exchange code for access token
    try:
        token_resp = httpx.post(
            SC_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            timeout=15.0,
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()
    except Exception as exc:
        return {"approved": False, "reason": f"token_exchange_failed: {exc}"}

    sc_access_token = token_data.get("access_token", "")
    if not sc_access_token:
        return {"approved": False, "reason": "no_access_token"}

    # Fetch user profile
    try:
        me_resp = httpx.get(
            SC_ME_URL,
            headers={"Authorization": f"OAuth {sc_access_token}"},
            timeout=10.0,
        )
        me_resp.raise_for_status()
        profile = me_resp.json()
    except Exception as exc:
        return {"approved": False, "reason": f"profile_fetch_failed: {exc}"}

    sc_user_id = str(profile.get("id", ""))
    sc_username = profile.get("username", "")
    sc_avatar = profile.get("avatar_url", "")
    sc_email = profile.get("email") or profile.get("primary_email") or ""

    # Derive account ID — reuse existing link if present
    existing = get_oauth_link("soundcloud", sc_user_id)
    if existing:
        account_id = existing["account_id"]
    else:
        email_for_id = sc_email or f"sc_{sc_user_id}@soundcloud.local"
        account_id = _make_account_id(email_for_id)

    # Upsert OAuth link
    upsert_oauth_link(
        provider="soundcloud",
        provider_user_id=sc_user_id,
        account_id=account_id,
        provider_username=sc_username,
        provider_avatar_url=sc_avatar,
        provider_email=sc_email,
        sc_access_token=sc_access_token,
    )

    # Ensure local entitlements/settings exist
    ensure_local_account(account_id, sc_email or None, sc_username)

    # Subscribe to email list if we have an email
    if sc_email:
        subscribe_email(
            email=sc_email,
            source="soundcloud",
            sc_username=sc_username,
            display_name=sc_username,
        )

    # Create session
    session = _new_session(account_id, "web_soundcloud")
    session["provider"] = "soundcloud"
    session["scUsername"] = sc_username
    session["scAvatar"] = sc_avatar
    session["scEmail"] = sc_email
    session["scUserId"] = sc_user_id
    return session


def check_follows_tizwildin(sc_access_token: str) -> dict:
    tw_id = _tizwildin_user_id()
    if not tw_id:
        return {"approved": True, "following": False, "reason": "tizwildin_user_id_not_configured"}
    try:
        resp = httpx.get(
            f"{SC_FOLLOWINGS_URL}/{tw_id}",
            headers={"Authorization": f"OAuth {sc_access_token}"},
            timeout=10.0,
        )
        if resp.status_code == 200:
            return {"approved": True, "following": True}
        elif resp.status_code == 404:
            return {"approved": True, "following": False}
        else:
            return {"approved": True, "following": False, "reason": f"sc_api_{resp.status_code}"}
    except Exception as exc:
        return {"approved": False, "following": False, "reason": str(exc)}


def get_sc_token_for_account(account_id: str) -> str | None:
    """Look up the stored SC access token for an account."""
    from app.services.sqlite_auth_service import _conn
    with _conn() as conn:
        row = conn.execute(
            "SELECT sc_access_token FROM oauth_links WHERE provider = 'soundcloud' AND account_id = ?",
            (account_id,),
        ).fetchone()
    if row and row["sc_access_token"]:
        return row["sc_access_token"]
    return None
