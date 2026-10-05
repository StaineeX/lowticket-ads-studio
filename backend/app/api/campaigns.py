from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from backend.app.ai.ports import DeterministicAIProvider
from backend.app.ai.service import CampaignDraftRequest, CampaignService


router = APIRouter(prefix="/api")


@router.post("/campaign-drafts/generate")
def generate_campaign_draft(request: CampaignDraftRequest) -> dict:
    draft = CampaignService(DeterministicAIProvider()).generate_draft(request)
    return jsonable_encoder(draft)
