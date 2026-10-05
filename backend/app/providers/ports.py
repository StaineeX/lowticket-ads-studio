from dataclasses import dataclass
from typing import Protocol

from backend.app.ai.service import CampaignDraft
from backend.app.domain.campaigns import Platform


@dataclass(frozen=True)
class ProviderPreview:
    operation_id: str
    platform: Platform
    status: str
    summary: str


@dataclass(frozen=True)
class ProviderCampaign:
    provider_id: str
    platform: Platform
    status: str


class AdProvider(Protocol):
    platform: Platform

    def preview_create_campaign(self, draft: CampaignDraft) -> ProviderPreview:
        ...

    def apply_create_campaign(self, draft: CampaignDraft) -> ProviderCampaign:
        ...
