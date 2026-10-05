from dataclasses import dataclass, field
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field

from backend.app.ai.ports import AIProvider, CampaignBriefRequest
from backend.app.domain.campaigns import CampaignCopy, Platform, ValidationIssue, validate_copy


ANGLES = ("Benefício direto", "Praticidade", "Prova e confiança")


class CampaignDraftRequest(BaseModel):
    offer_name: str = Field(min_length=2, max_length=160)
    benefit: str = Field(min_length=4, max_length=240)
    audience: str = Field(min_length=2, max_length=160)
    proof: str = Field(min_length=2, max_length=240)
    cta: str = Field(min_length=2, max_length=40)
    price: Decimal = Field(gt=0)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    budget: Decimal = Field(gt=0)
    platforms: list[Platform] = Field(min_length=1)


@dataclass(frozen=True)
class CampaignVariant:
    angle: str
    copy: CampaignCopy
    creative_brief: str
    validation_issues: list[ValidationIssue] = field(default_factory=list)


@dataclass(frozen=True)
class CampaignDraft:
    draft_id: str
    status: str
    budget: Decimal
    variants: dict[Platform, list[CampaignVariant]]


class CampaignService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    def generate_draft(self, request: CampaignDraftRequest) -> CampaignDraft:
        variants: dict[Platform, list[CampaignVariant]] = {}
        for platform in request.platforms:
            platform_variants = []
            for angle in ANGLES:
                brief = self.ai_provider.generate_campaign_brief(
                    CampaignBriefRequest(
                        platform=platform,
                        offer_name=request.offer_name,
                        benefit=request.benefit,
                        audience=request.audience,
                        proof=request.proof,
                        cta=request.cta,
                        price=request.price,
                        currency=request.currency.upper(),
                        angle=angle,
                    )
                )
                platform_variants.append(
                    CampaignVariant(
                        angle=angle,
                        copy=brief.copy,
                        creative_brief=brief.creative_brief,
                        validation_issues=validate_copy(platform, brief.copy),
                    )
                )
            variants[platform] = platform_variants
        return CampaignDraft(
            draft_id=str(uuid.uuid4()),
            status="paused",
            budget=request.budget,
            variants=variants,
        )
