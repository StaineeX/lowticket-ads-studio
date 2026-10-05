from decimal import Decimal

from backend.app.ai.ports import DeterministicAIProvider
from backend.app.ai.service import CampaignDraftRequest, CampaignService
from backend.app.domain.campaigns import Platform
from backend.app.providers.fake import FakeAdProvider


def make_draft():
    return CampaignService(DeterministicAIProvider()).generate_draft(
        CampaignDraftRequest(
            offer_name="Curso Express",
            benefit="Aprenda uma habilidade",
            audience="iniciantes",
            proof="aulas curtas",
            cta="Comece agora",
            price=Decimal("47"),
            currency="BRL",
            budget=Decimal("36"),
            platforms=[Platform.META],
        )
    )


def test_provider_preview_does_not_apply_campaign():
    provider = FakeAdProvider(Platform.META)
    draft = make_draft()

    preview = provider.preview_create_campaign(draft)

    assert preview.status == "preview"
    assert provider.applied == []


def test_provider_apply_creates_paused_campaign():
    provider = FakeAdProvider(Platform.META)
    draft = make_draft()

    campaign = provider.apply_create_campaign(draft)

    assert campaign.status == "paused"
    assert len(provider.applied) == 1
