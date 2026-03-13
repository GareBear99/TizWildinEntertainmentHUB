from fastapi import APIRouter, HTTPException, Request
from app.models.domain import (
    EntitlementState,
    InstallScanReport,
    ProposalRequest,
    RuntimeValidationRequest,
    SeatAssignment,
)
from app.services.catalog_service import load_catalog
from app.services.entitlement_service import get_entitlement, load_entitlements, resolve_product_access
from app.services.proposal_service import decide_proposal
from app.services.release_service import get_latest_release, bulk_release_check
from app.services.seat_service import assign_seat, list_seats
from app.services.stripe_service import verify_signature, dispatch_event

router = APIRouter()

@router.get("/catalog")
def get_catalog():
    return load_catalog()

@router.get("/entitlements/{account_id}", response_model=EntitlementState)
def get_entitlements(account_id: str):
    data = get_entitlement(account_id)
    if not data:
        raise HTTPException(status_code=404, detail="Account not found")
    return data

@router.get("/seats/{account_id}", response_model=list[SeatAssignment])
def get_seats(account_id: str):
    return list_seats(account_id)

@router.post("/validate-runtime")
def validate_runtime(request: RuntimeValidationRequest):
    ent = get_entitlement(request.accountId)
    if not ent:
        raise HTTPException(status_code=404, detail="Account not found")

    access = resolve_product_access(ent, request.productId)
    if not access["allowed"]:
        return {"approved": False, "reason": access["reason"]}

    seat_result = assign_seat(request.accountId, request.machineId, request.productId)
    if not seat_result["approved"]:
        return seat_result

    return {
        "approved": True,
        "reason": access["reason"],
        "features": access["features"],
        "seat": seat_result["seat"]
    }

@router.post("/proposal")
def propose(request: ProposalRequest):
    return decide_proposal(request)

@router.post("/install-scan")
def report_install_scan(report: InstallScanReport):
    return {
        "accepted": True,
        "machineId": report.machineId,
        "productCount": len(report.products),
        "message": "Wire this into durable ARC receipt/store next"
    }


# ---------------------------------------------------------------------------
# GitHub release polling
# ---------------------------------------------------------------------------

@router.get("/releases/{product_id}")
def get_release(product_id: str):
    return get_latest_release(product_id)


@router.get("/release-check")
def release_check():
    return bulk_release_check()


# ---------------------------------------------------------------------------
# Stripe webhook
# ---------------------------------------------------------------------------

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("stripe-signature", "")

    if not verify_signature(body, sig):
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json
    event = json.loads(body)
    result = dispatch_event(event)
    return result
