from fastapi import APIRouter, HTTPException
from app.models.domain import (
    EntitlementState,
    InstallScanReport,
    ProposalRequest,
    RuntimeValidationRequest,
    SeatAssignment,
)
from app.services.catalog_service import load_catalog
from app.services.entitlement_service import load_entitlements, resolve_product_access
from app.services.proposal_service import decide_proposal
from app.services.seat_service import assign_seat, list_seats

router = APIRouter()

@router.get("/catalog")
def get_catalog():
    return load_catalog()

@router.get("/entitlements/{account_id}", response_model=EntitlementState)
def get_entitlements(account_id: str):
    data = load_entitlements().get(account_id)
    if not data:
        raise HTTPException(status_code=404, detail="Account not found")
    return data

@router.get("/seats/{account_id}", response_model=list[SeatAssignment])
def get_seats(account_id: str):
    return list_seats(account_id)

@router.post("/validate-runtime")
def validate_runtime(request: RuntimeValidationRequest):
    ent = load_entitlements().get(request.accountId)
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
