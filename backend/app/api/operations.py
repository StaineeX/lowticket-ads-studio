from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from backend.app.ai.factory import campaign_ai_provider
from backend.app.ai.service import CampaignDraftRequest, CampaignService
from backend.app.domain.campaigns import Platform
from backend.app.providers.fake import FakeAdProvider
from backend.app.services.approvals import ApprovalError, ApprovalManager, OperationRequest


router = APIRouter(prefix="/api")
manager = ApprovalManager()
providers: dict[str, FakeAdProvider] = {}


class OperationPreviewRequest(BaseModel):
    platform: Platform
    budget_ceiling: Decimal = Field(gt=0)
    draft: CampaignDraftRequest


class ApprovalRequest(BaseModel):
    token: str = Field(min_length=1)


@router.post("/operations/preview")
def preview_operation(request: OperationPreviewRequest) -> dict:
    draft_request = request.draft.model_copy(update={"platforms": [request.platform]})
    draft = CampaignService(campaign_ai_provider()).generate_draft(draft_request)
    provider = FakeAdProvider(request.platform)
    preview = manager.preview_operation(
        OperationRequest(request.platform, "create_campaign", draft),
        provider,
        budget_ceiling=request.budget_ceiling,
    )
    providers[preview.operation_id] = provider
    return jsonable_encoder(preview)


@router.post("/operations/{operation_id}/approve")
def approve_operation(operation_id: str, request: ApprovalRequest) -> dict:
    provider = providers.get(operation_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="operation not found")
    try:
        result = manager.approve_operation(operation_id, request.token, provider)
    except ApprovalError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return jsonable_encoder(result)


@router.get("/audit")
def list_audit_events() -> list[dict]:
    return jsonable_encoder(manager.audit.events)
