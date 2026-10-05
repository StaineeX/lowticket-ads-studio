from decimal import Decimal

from backend.app.ai.ports import DeterministicAIProvider
from backend.app.ai.service import CampaignDraftRequest, CampaignService
from backend.app.domain.campaigns import Platform
from backend.app.providers.fake import FakeAdProvider
from backend.app.services.approvals import ApprovalManager, OperationRequest


def test_local_core_flow_requires_approval_and_creates_paused_campaign():
    draft = CampaignService(DeterministicAIProvider()).generate_draft(
        CampaignDraftRequest(
            offer_name="Curso Express",
            benefit="Aprenda uma habilidade",
            audience="iniciantes",
            proof="aulas curtas",
            cta="Comece agora",
            price=Decimal("47"),
            currency="BRL",
            budget=Decimal("20"),
            platforms=[Platform.META],
        )
    )
    provider = FakeAdProvider(Platform.META)
    manager = ApprovalManager()
    preview = manager.preview_operation(
        OperationRequest(Platform.META, "create_campaign", draft),
        provider,
        budget_ceiling=Decimal("36"),
    )

    assert provider.applied == []
    result = manager.approve_operation(preview.operation_id, preview.token, provider)

    assert result.status == "applied"
    assert result.campaign.status == "paused"
