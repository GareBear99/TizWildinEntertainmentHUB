from fastapi import APIRouter, HTTPException
from app.models.domain import BackupRestoreRequest, CheckoutSessionRequest, DownloadPlanRequest, EntitlementState, ExecuteDownloadsRequest, HubSettingsState, HubSettingsUpdateRequest, InstallPlanRequest, InstallScanReport, LocalLoginRequest, LocalRegisterRequest, MockLoginRequest, PreflightRequest, ProposalRequest, RefreshTokenRequest, ReleaseImportRequest, RepairRequest, RollbackRequest, RuntimeValidationRequest, SeatAssignment, SeatReleaseRequest, TokenRevokeRequest, TokenValidationRequest, UninstallRequest, WebhookEvent
from app.services.store import load_catalog, load_entitlements
from app.services.auth_service import local_login, local_refresh, local_register, mock_login, revoke_token, validate_token
from app.services.entitlement_service import resolve_product_access
from app.services.seat_service import assign_seat, list_seats, release_seat
from app.services.proposal_service import decide_proposal
from app.services.install_scan_service import record_install_scan
from app.services.webhook_service import ingest_webhook
from app.services.release_service import get_release_manifest, stage_local_artifacts
from app.services.install_plan_service import build_install_plan
from app.services.download_service import build_download_plan, list_receipts, record_install_receipt
from app.services.execute_downloads_service import execute_downloads, repair_product, rollback_product, uninstall_product
from app.services.account_service import get_account_summary
from app.services.machine_service import list_machines
from app.services.diagnostics_service import export_account_diagnostics
from app.services.backup_service import export_backup, list_backups, restore_backup
from app.services.preflight_service import run_preflight
from app.services.bootstrap_service import bootstrap_demo_state
from app.services.launchpad_service import get_launchpad
from app.services.settings_service import get_settings, save_account_settings
from app.services.activity_service import get_activity
from app.services.readiness_service import get_readiness
from app.services.sync_service import build_sync_status
from app.services.support_bundle_service import create_support_bundle
from app.services.audit_service import audit_account
from app.services.billing_service import complete_checkout, create_checkout_session
from app.services.release_import_service import import_release_manifests

router = APIRouter()


@router.post("/auth/register")
def auth_register(request: LocalRegisterRequest):
    result = local_register(request.email, request.password, request.machineId, request.displayName)
    if not result.get("approved"):
        raise HTTPException(status_code=400, detail=result.get("reason", "register_failed"))
    return result


@router.post("/auth/login")
def auth_login(request: LocalLoginRequest):
    result = local_login(request.email, request.password, request.machineId)
    if not result.get("approved"):
        raise HTTPException(status_code=401, detail=result.get("reason", "login_failed"))
    return result


@router.post("/auth/refresh")
def auth_refresh(request: RefreshTokenRequest):
    result = local_refresh(request.refreshToken, request.machineId)
    if not result.get("approved"):
        raise HTTPException(status_code=401, detail=result.get("reason", "refresh_failed"))
    return result


@router.get("/auth/me")
def auth_me(token: str):
    result = validate_token(token)
    if not result.get("approved"):
        raise HTTPException(status_code=401, detail="invalid_token")
    return result


@router.post("/billing/checkout-session")
def billing_checkout_session(request: CheckoutSessionRequest):
    result = create_checkout_session(request.accountId, request.productId, request.quantity, request.priceId, request.successUrl, request.cancelUrl)
    if not result.get("approved"):
        raise HTTPException(status_code=404, detail=result.get("reason", "checkout_failed"))
    return result


@router.post("/billing/checkout-complete")
def billing_checkout_complete(request: CheckoutSessionRequest):
    result = complete_checkout(request.accountId, request.productId, request.quantity)
    if not result.get("approved"):
        raise HTTPException(status_code=404, detail=result.get("reason", "checkout_complete_failed"))
    return result


@router.post("/releases/import")
def releases_import(request: ReleaseImportRequest):
    result = import_release_manifests(request.source, request.replaceExisting, request.channelOverride)
    if not result.get("approved"):
        raise HTTPException(status_code=400, detail=result.get("reason", "release_import_failed"))
    return result



@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/catalog")
def get_catalog():
    return load_catalog()




@router.post("/sync")
def sync_status(request: PreflightRequest):
    data = build_sync_status(request)
    if not data.get("approved"):
        raise HTTPException(status_code=404, detail="sync_failed")
    return data


@router.get("/support/bundle/{account_id}")
def support_bundle(account_id: str, machine_id: str = "mac_demo", channel: str = "stable"):
    data = create_support_bundle(account_id, machine_id, channel)
    if not data.get("approved"):
        raise HTTPException(status_code=404, detail=data.get("reason", "bundle_failed"))
    return data


@router.get("/audit/{account_id}")
def account_audit(account_id: str, machine_id: str = "mac_demo", channel: str = "stable"):
    data = audit_account(account_id, machine_id, channel)
    if not data.get("approved"):
        raise HTTPException(status_code=404, detail=data.get("reason", "audit_failed"))
    return data

@router.get("/settings/{account_id}", response_model=HubSettingsState)
def get_account_settings(account_id: str):
    return get_settings(account_id)


@router.post("/settings", response_model=HubSettingsState)
def post_account_settings(request: HubSettingsUpdateRequest):
    return save_account_settings(request)


@router.get("/activity/{account_id}")
def account_activity(account_id: str, limit: int = 25):
    return get_activity(account_id, limit)


@router.get("/readiness/{account_id}")
def account_readiness(account_id: str, machine_id: str | None = None, channel: str | None = None):
    data = get_readiness(account_id, machine_id, channel)
    if not data:
        raise HTTPException(status_code=404, detail="Account not found")
    return data


@router.get("/catalog/owned/{account_id}")
def get_owned_catalog(account_id: str):
    entitlements = load_entitlements().get(account_id)
    if not entitlements:
        raise HTTPException(status_code=404, detail="Account not found")
    catalog = load_catalog()
    products = []
    for product in catalog.get("products", []):
        access = resolve_product_access(entitlements, product.get("productId"))
        if access.get("allowed") or product.get("licenseClass") in {"FREE_OPEN", "FREE_LITE"}:
            products.append(product)
    return {"accountId": account_id, "products": products}


@router.post("/auth/mock-login")
def auth_mock_login(request: MockLoginRequest):
    result = mock_login(request.accountId, request.machineId)
    if not result.get("approved"):
        raise HTTPException(status_code=404, detail="Account not found")
    return result


@router.post("/auth/validate")
def auth_validate(request: TokenValidationRequest):
    result = validate_token(request.token)
    if not result.get("approved"):
        raise HTTPException(status_code=401, detail="invalid_token")
    return result


@router.post("/auth/logout")
def auth_logout(request: TokenRevokeRequest):
    result = revoke_token(request.token)
    if not result.get("approved"):
        raise HTTPException(status_code=401, detail="invalid_token")
    return result


@router.get("/entitlements/{account_id}", response_model=EntitlementState)
def get_entitlements(account_id: str):
    data = load_entitlements().get(account_id)
    if not data:
        raise HTTPException(status_code=404, detail="Account not found")
    return data


@router.get("/seats/{account_id}", response_model=list[SeatAssignment])
def get_seats(account_id: str):
    return list_seats(account_id)


@router.post("/seats/release")
def post_seat_release(request: SeatReleaseRequest):
    return release_seat(request.accountId, request.seatId)


@router.get("/machines/{account_id}")
def get_machines(account_id: str):
    return {"accountId": account_id, "machines": list_machines(account_id)}


@router.get("/receipts/{account_id}")
def get_receipts(account_id: str):
    return {"accountId": account_id, "receipts": list_receipts(account_id)}


@router.get("/account-summary/{account_id}")
def account_summary(account_id: str):
    data = get_account_summary(account_id)
    if not data:
        raise HTTPException(status_code=404, detail="Account not found")
    return data


@router.get("/releases")
def get_releases(product_id: str | None = None, channel: str | None = None):
    return get_release_manifest(product_id, channel)


@router.get("/diagnostics/export/{account_id}")
def diagnostics_export(account_id: str):
    data = export_account_diagnostics(account_id)
    if not data.get("approved"):
        raise HTTPException(status_code=404, detail="Account not found")
    return data

@router.get("/backups")
def backups_list():
    return list_backups()


@router.post("/backups/export")
def backups_export(tag: str | None = None):
    return export_backup(tag)


@router.post("/backups/restore")
def backups_restore(request: BackupRestoreRequest):
    data = restore_backup(request.path)
    if not data.get("approved"):
        raise HTTPException(status_code=404, detail=data.get("reason", "restore_failed"))
    return data


@router.post("/preflight")
def preflight(request: PreflightRequest):
    data = run_preflight(request.accountId, request.machineId, request.requestedProducts, request.channel)
    if not data.get("approved"):
        raise HTTPException(status_code=404, detail=data.get("reason", "preflight_failed"))
    return data




@router.post("/demo/bootstrap")
def demo_bootstrap(stage_artifacts: bool = True):
    return bootstrap_demo_state(stage_artifacts)


@router.get("/launchpad/{account_id}")
def launchpad(account_id: str, machine_id: str = "mac_demo", channel: str = "stable"):
    data = get_launchpad(account_id, machine_id, channel)
    if not data:
        raise HTTPException(status_code=404, detail="Account not found")
    return data

@router.post("/releases/stage-local")
def stage_releases(channel: str | None = None):
    return {"staged": stage_local_artifacts(channel)}


@router.post("/install-plan")
def install_plan(request: InstallPlanRequest):
    return build_install_plan(request)


@router.post("/download-plan")
def download_plan(request: DownloadPlanRequest):
    return build_download_plan(request)


@router.post("/execute-downloads")
def execute_download_plan(request: ExecuteDownloadsRequest):
    return execute_downloads(request)


@router.post("/repair")
def repair(request: RepairRequest):
    return repair_product(request)


@router.post("/uninstall")
def uninstall(request: UninstallRequest):
    return uninstall_product(request)


@router.post("/rollback")
def rollback(request: RollbackRequest):
    return rollback_product(request)


@router.post("/record-receipt")
def post_record_receipt(request: DownloadPlanRequest):
    plan = build_download_plan(request)
    receipts = [record_install_receipt(request.accountId, request.machineId, d, status="planned") for d in plan.get("downloads", [])]
    return {"approved": True, "receipts": receipts}


@router.post("/validate-runtime")
def validate_runtime(request: RuntimeValidationRequest):
    entitlement = load_entitlements().get(request.accountId)
    if not entitlement:
        raise HTTPException(status_code=404, detail="Account not found")
    access = resolve_product_access(entitlement, request.productId)
    if not access["allowed"]:
        return {"approved": False, "reason": access["reason"], "features": []}
    seat_result = assign_seat(request.accountId, request.machineId, request.productId)
    if not seat_result["approved"]:
        return {"approved": False, "reason": seat_result["reason"], "features": []}
    return {"approved": True, "reason": access["reason"], "features": access["features"], "seat": seat_result["seat"]}


@router.post("/proposal")
def propose(request: ProposalRequest):
    return decide_proposal(request)


@router.post("/install-scan")
def report_install_scan(report: InstallScanReport):
    return record_install_scan(report)


@router.post("/webhooks/ingest")
def webhooks_ingest(event: WebhookEvent):
    return ingest_webhook(event)
