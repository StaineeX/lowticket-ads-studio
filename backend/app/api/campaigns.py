from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from backend.app.ai.factory import campaign_ai_provider
from backend.app.ai.service import CampaignDraftRequest, CampaignService


router = APIRouter(prefix="/api")


@router.post("/campaign-drafts/generate")
def generate_campaign_draft(request: CampaignDraftRequest) -> dict:
    draft = CampaignService(campaign_ai_provider()).generate_draft(request)
    return jsonable_encoder(draft)
