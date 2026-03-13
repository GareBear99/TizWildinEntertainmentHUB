from __future__ import annotations

from app.models.domain import HubSettingsUpdateRequest
from app.services.store import load_settings, save_settings


DEFAULT_SETTINGS = {
    "machineId": "mac_demo",
    "preferredChannel": "stable",
    "theme": "dark",
    "arcBaseUrl": "http://127.0.0.1:8000",
    "installRoot": "/tmp/tizhub_installs",
    "autoStageOnBootstrap": True,
    "autoBackupBeforeExecute": True,
}


def get_settings(account_id: str) -> dict:
    data = load_settings()
    settings = dict(DEFAULT_SETTINGS)
    settings.update(data.get(account_id, {}))
    settings["accountId"] = account_id
    return settings


def save_account_settings(request: HubSettingsUpdateRequest) -> dict:
    data = load_settings()
    payload = request.model_dump()
    account_id = payload.pop("accountId")
    data[account_id] = payload
    save_settings(data)
    return get_settings(account_id)
