from __future__ import annotations
from pathlib import Path
import json
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CATALOG_PATH = DATA_DIR / "products.catalog.json"
ENTITLEMENTS_PATH = DATA_DIR / "entitlements.mock.json"
SEATS_PATH = DATA_DIR / "seats.mock.json"
INSTALL_SCANS_PATH = DATA_DIR / "install_scans.mock.json"
WEBHOOKS_PATH = DATA_DIR / "webhooks.mock.json"
RELEASE_MANIFESTS_PATH = DATA_DIR / "release_manifests.mock.json"
AUTH_TOKENS_PATH = DATA_DIR / "auth_tokens.mock.json"
INSTALL_RECEIPTS_PATH = DATA_DIR / "install_receipts.mock.json"
SETTINGS_PATH = DATA_DIR / "settings.mock.json"


def _read_json(path: Path, default: Any):
    if not path.exists():
        return default
    text = path.read_text().strip()
    if not text:
        return default
    return json.loads(text)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def load_catalog() -> dict:
    return _read_json(CATALOG_PATH, {"groups": [], "products": [], "globalFlags": {}})


def load_entitlements() -> dict:
    return _read_json(ENTITLEMENTS_PATH, {})


def save_entitlements(data: dict) -> None:
    _write_json(ENTITLEMENTS_PATH, data)


def load_seats() -> dict:
    return _read_json(SEATS_PATH, {})


def save_seats(data: dict) -> None:
    _write_json(SEATS_PATH, data)


def load_install_scans() -> list:
    return _read_json(INSTALL_SCANS_PATH, [])


def save_install_scans(data: list) -> None:
    _write_json(INSTALL_SCANS_PATH, data)


def load_webhooks() -> list:
    return _read_json(WEBHOOKS_PATH, [])


def save_webhooks(data: list) -> None:
    _write_json(WEBHOOKS_PATH, data)


def load_release_manifests() -> dict:
    return _read_json(RELEASE_MANIFESTS_PATH, {})


def save_release_manifests(data: dict) -> None:
    _write_json(RELEASE_MANIFESTS_PATH, data)


def load_auth_tokens() -> dict:
    return _read_json(AUTH_TOKENS_PATH, {})


def save_auth_tokens(data: dict) -> None:
    _write_json(AUTH_TOKENS_PATH, data)


def load_install_receipts() -> list:
    return _read_json(INSTALL_RECEIPTS_PATH, [])


def save_install_receipts(data: list) -> None:
    _write_json(INSTALL_RECEIPTS_PATH, data)


def load_settings() -> dict:
    return _read_json(SETTINGS_PATH, {})


def save_settings(data: dict) -> None:
    _write_json(SETTINGS_PATH, data)
