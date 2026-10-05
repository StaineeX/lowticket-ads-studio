from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from backend.app.domain.campaigns import CampaignCopy, Platform


@dataclass(frozen=True)
class CampaignBriefRequest:
    platform: Platform
    offer_name: str
    benefit: str
    audience: str
    proof: str
    cta: str
    price: Decimal
    currency: str
    angle: str


@dataclass(frozen=True)
class CampaignBrief:
    copy: CampaignCopy
    creative_brief: str


class AIProvider(Protocol):
    def generate_campaign_brief(self, request: CampaignBriefRequest) -> CampaignBrief:
        """Generate copy and a visual brief for one platform/angle."""


class DeterministicAIProvider:
    def generate_campaign_brief(self, request: CampaignBriefRequest) -> CampaignBrief:
        from backend.app.ai.templates import build_copy

        copy = build_copy(
            platform=request.platform,
            offer_name=request.offer_name,
            benefit=request.benefit,
            audience=request.audience,
            proof=request.proof,
            cta=request.cta,
            price=request.price,
            currency=request.currency,
            angle=request.angle,
        )
        creative_brief = (
            f"Visual {request.angle.lower()} para {request.platform.value}: "
            f"mostrar {request.offer_name}, benefício principal e CTA claro, "
            "sem alegações não comprovadas."
        )
        return CampaignBrief(copy=copy, creative_brief=creative_brief)
