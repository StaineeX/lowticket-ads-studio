from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import secrets
import uuid

from backend.app.ai.service import CampaignDraft
from backend.app.audit import AuditLog
from backend.app.domain.campaigns import Platform
from backend.app.providers.ports import AdProvider, ProviderCampaign


class ApprovalError(RuntimeError):
    pass


@dataclass(frozen=True)
class OperationRequest:
    platform: Platform
    action: str
    draft: CampaignDraft

    def payload(self) -> dict[str, str]:
        return {
            "platform": self.platform.value,
            "action": self.action,
            "draft_id": self.draft.draft_id,
            "budget": str(self.draft.budget),
            "status": self.draft.status,
        }


@dataclass(frozen=True)
class OperationPreview:
    operation_id: str
    token: str
    expires_at: datetime
    payload_hash: str
    summary: str
    status: str = "preview"


@dataclass(frozen=True)
class OperationResult:
    operation_id: str
    status: str
    campaign: ProviderCampaign


@dataclass
class _PendingApproval:
    operation: OperationRequest
    provider: AdProvider
    token: str
    expires_at: datetime
    payload_hash: str
    used: bool = False


def _hash_payload(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class ApprovalManager:
    def __init__(self, audit: AuditLog | None = None):
        self.audit = audit or AuditLog()
        self._pending: dict[str, _PendingApproval] = {}

    def preview_operation(
        self,
        operation: OperationRequest,
        provider: AdProvider,
        *,
        budget_ceiling: Decimal,
        now: datetime | None = None,
    ) -> OperationPreview:
        if operation.draft.budget > budget_ceiling:
            raise ApprovalError("budget exceeds configured ceiling")
        now = now or datetime.now(timezone.utc)
        operation_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(24)
        expires_at = now + timedelta(minutes=10)
        payload_hash = _hash_payload(operation.payload())
        provider_preview = provider.preview_create_campaign(operation.draft)
        pending = _PendingApproval(operation, provider, token, expires_at, payload_hash)
        self._pending[operation_id] = pending
        self.audit.record(operation_id, "preview", "ok", provider_preview.summary)
        return OperationPreview(operation_id, token, expires_at, payload_hash, provider_preview.summary)

    def approve_operation(
        self,
        operation_id: str,
        token: str,
        provider: AdProvider,
        *,
        payload_override: dict | None = None,
        now: datetime | None = None,
    ) -> OperationResult:
        pending = self._pending.get(operation_id)
        if pending is None:
            raise ApprovalError("operation not found")
        now = now or datetime.now(timezone.utc)
        if now >= pending.expires_at:
            raise ApprovalError("approval token expired")
        if pending.used:
            raise ApprovalError("approval token already used")
        if not secrets.compare_digest(token, pending.token):
            raise ApprovalError("invalid approval token")
        if payload_override is not None and _hash_payload(payload_override) != pending.payload_hash:
            raise ApprovalError("approval payload does not match preview")
        if provider.platform is not pending.operation.platform:
            raise ApprovalError("provider platform does not match operation")

        pending.used = True
        try:
            campaign = provider.apply_create_campaign(pending.operation.draft)
        except Exception as exc:
            self.audit.record(operation_id, "apply", "error", str(exc))
            raise
        self.audit.record(operation_id, "apply", "ok", campaign.provider_id)
        return OperationResult(operation_id, "applied", campaign)
