from pydantic import BaseModel, Field
from typing import List, Optional

class EntitlementState(BaseModel):
    accountId: str
    ownsEveryVST: bool = False
    ownedProducts: List[str] = Field(default_factory=list)
    ownedBundles: List[str] = Field(default_factory=list)
    extraSeatQuantity: int = 0
    billingState: str = "active"

class SeatAssignment(BaseModel):
    seatId: str
    accountId: str
    machineId: str
    productId: str
    status: str = "active"

class RuntimeValidationRequest(BaseModel):
    accountId: str
    machineId: str
    productId: str
    edition: str = "standard"
    runtimeVersion: str = "0.0.0"

class ProposalRequest(BaseModel):
    proposalId: str
    type: str
    accountId: str
    machineId: str
    requestedProducts: List[str] = Field(default_factory=list)

class InstallScanProduct(BaseModel):
    productId: str
    localVersion: Optional[str] = None
    runtimeVersion: Optional[str] = None
    installState: str
    binaryPresent: bool = False
    sourcePresent: bool = False

class InstallScanReport(BaseModel):
    accountId: str
    machineId: str
    products: List[InstallScanProduct]
