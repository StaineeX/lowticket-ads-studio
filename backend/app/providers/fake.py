import uuid

from backend.app.ai.service import CampaignDraft
from backend.app.domain.campaigns import Platform
from backend.app.providers.ports import ProviderCampaign, ProviderPreview


class FakeAdProvider:
    def __init__(self, platform: Platform):
        self.platform = platform
        self.applied: list[ProviderCampaign] = []

    def preview_create_campaign(self, draft: CampaignDraft) -> ProviderPreview:
        return ProviderPreview(
            operation_id=str(uuid.uuid4()),
            platform=self.platform,
            status="preview",
            summary=f"Create paused {self.platform.value} campaign with budget {draft.budget}",
        )

    def apply_create_campaign(self, draft: CampaignDraft) -> ProviderCampaign:
        campaign = ProviderCampaign(
            provider_id=f"fake-{uuid.uuid4()}",
            platform=self.platform,
            status="paused",
        )
        self.applied.append(campaign)
        return campaign
