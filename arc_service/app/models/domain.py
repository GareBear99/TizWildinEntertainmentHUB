from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class EntitlementState(BaseModel):
    accountId: str
    ownsEveryVST: bool = False
    ownedProducts: List[str] = Field(default_factory=list)
    ownedBundles: List[str] = Field(default_factory=list)
    extraSeatQuantity: int = Field(default=0, ge=0, le=9)
    billingState: str = "active"


class SeatAssignment(BaseModel):
    seatId: str
    accountId: str
    machineId: str
    productId: str
    status: str = "active"
    assignedAt: str | None = None
    lastSeenAt: str | None = None


class DiagnosticsExportRequest(BaseModel):
    accountId: str


class RuntimeValidationRequest(BaseModel):
    accountId: str
    machineId: str
    productId: str
    edition: str = "standard"
    runtimeVersion: str = "0.0.0"


class ProposalRequest(BaseModel):
    proposalId: str
    type: Literal["refresh_catalog", "install_missing", "check_updates"]
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
    installedPath: Optional[str] = None
    channel: str = "stable"


class InstallScanReport(BaseModel):
    accountId: str
    machineId: str
    products: List[InstallScanProduct]


class InstallPlanRequest(BaseModel):
    accountId: str
    machineId: str
    requestedProducts: List[str] = Field(default_factory=list)
    channel: str = "stable"


class DownloadPlanRequest(BaseModel):
    accountId: str
    machineId: str
    requestedProducts: List[str] = Field(default_factory=list)
    channel: str = "stable"


class ExecuteDownloadsRequest(BaseModel):
    accountId: str
    machineId: str
    requestedProducts: List[str] = Field(default_factory=list)
    channel: str = "stable"
    dryRun: bool = True
    installRoot: Optional[str] = None


class RollbackRequest(BaseModel):
    accountId: str
    machineId: str
    productId: str


class SeatReleaseRequest(BaseModel):
    accountId: str
    seatId: str


class WebhookEvent(BaseModel):
    provider: str = "stripe"
    eventType: str
    payload: dict = Field(default_factory=dict)
    signature: str = ""


class MockLoginRequest(BaseModel):
    accountId: str
    machineId: str


class InstallReceipt(BaseModel):
    receiptId: str
    timestamp: str
    accountId: str
    machineId: str
    productId: str
    action: str
    targetVersion: str
    artifactMode: str
    sha256: str = ""
    status: str = "planned"
    channel: str = "stable"
    verificationPassed: bool = False
    installedPath: str = ""


class TokenValidationRequest(BaseModel):
    token: str


class TokenRevokeRequest(BaseModel):
    token: str


class UninstallRequest(BaseModel):
    accountId: str
    machineId: str
    productId: str


class BackupRestoreRequest(BaseModel):
    path: str


class PreflightRequest(BaseModel):
    accountId: str
    machineId: str
    requestedProducts: List[str] = Field(default_factory=list)
    channel: str = "stable"


class RepairRequest(BaseModel):
    accountId: str
    machineId: str
    productId: str
    channel: str = "stable"
    installRoot: Optional[str] = None


class HubSettingsState(BaseModel):
    accountId: str
    machineId: str = "mac_demo"
    preferredChannel: str = "stable"
    theme: str = "dark"
    arcBaseUrl: str = "http://127.0.0.1:8000"
    installRoot: str = "/tmp/tizhub_installs"
    autoStageOnBootstrap: bool = True
    autoBackupBeforeExecute: bool = True


class HubSettingsUpdateRequest(BaseModel):
    accountId: str
    machineId: str = "mac_demo"
    preferredChannel: str = "stable"
    theme: str = "dark"
    arcBaseUrl: str = "http://127.0.0.1:8000"
    installRoot: str = "/tmp/tizhub_installs"
    autoStageOnBootstrap: bool = True
    autoBackupBeforeExecute: bool = True


class LocalRegisterRequest(BaseModel):
    email: str
    password: str
    displayName: str | None = None
    machineId: str = "mac_local"


class LocalLoginRequest(BaseModel):
    email: str
    password: str
    machineId: str = "mac_local"


class RefreshTokenRequest(BaseModel):
    refreshToken: str
    machineId: str = "mac_local"


class CheckoutSessionRequest(BaseModel):
    accountId: str
    productId: str
    quantity: int = Field(default=1, ge=1, le=9)
    priceId: str | None = None
    successUrl: str = "http://localhost/success"
    cancelUrl: str = "http://localhost/cancel"


class ReleaseImportRequest(BaseModel):
    source: str
    replaceExisting: bool = False
    channelOverride: str | None = None
