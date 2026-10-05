from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from backend.app.ai.ports import DeterministicAIProvider
from backend.app.ai.service import CampaignDraftRequest, CampaignService
from backend.app.domain.campaigns import Platform
from backend.app.domain.economics import EconomicsResult
from backend.app.providers.fake import FakeAdProvider
from backend.app.services.approvals import (
    ApprovalError,
    ApprovalManager,
    OperationRequest,
)
from backend.app.services.metrics_import import MetricRecord
from backend.app.services.recommendations import analyze_metrics


def make_economics() -> EconomicsResult:
    return EconomicsResult(
        price=Decimal("47"),
        net_revenue=Decimal("42.30"),
        contribution_value=Decimal("33.84"),
        checkout_conversion_rate=Decimal("0.02"),
    )


def make_record(*, spend: str, conversions: str, revenue: str) -> MetricRecord:
    return MetricRecord(
        platform=Platform.META,
        campaign_id="cmp-1",
        campaign_name="Curso Express",
        metric_date=datetime(2026, 10, 1, tzinfo=timezone.utc).date(),
        spend=Decimal(spend),
        impressions=100,
        clicks=10,
        conversions=Decimal(conversions),
        revenue=Decimal(revenue),
    )


def test_recommends_pause_for_spend_without_conversions():
    recommendations = analyze_metrics([make_record(spend="20", conversions="0", revenue="0")], make_economics())

    assert recommendations[0].type == "pause"
    assert recommendations[0].risk_level == "high"


def test_recommends_scale_only_when_roas_and_cpa_are_better_than_break_even():
    recommendations = analyze_metrics([make_record(spend="0.50", conversions="1", revenue="10")], make_economics())

    assert recommendations[0].type == "scale"
    assert recommendations[0].proposed_change["budget_multiplier"] == "1.2"


def make_operation(budget: str = "20") -> OperationRequest:
    draft = CampaignService(DeterministicAIProvider()).generate_draft(
        CampaignDraftRequest(
            offer_name="Curso Express",
            benefit="Aprenda uma habilidade",
            audience="iniciantes",
            proof="aulas curtas",
            cta="Comece agora",
            price=Decimal("47"),
            currency="BRL",
            budget=Decimal(budget),
            platforms=[Platform.META],
        )
    )
    return OperationRequest(platform=Platform.META, action="create_campaign", draft=draft)


def test_approval_applies_only_after_preview_and_approval():
    provider = FakeAdProvider(Platform.META)
    manager = ApprovalManager()
    preview = manager.preview_operation(make_operation(), provider, budget_ceiling=Decimal("36"))

    assert provider.applied == []
    result = manager.approve_operation(preview.operation_id, preview.token, provider)

    assert result.status == "applied"
    assert provider.applied[0].status == "paused"


def test_modified_payload_is_rejected_before_provider_call():
    provider = FakeAdProvider(Platform.META)
    manager = ApprovalManager()
    preview = manager.preview_operation(make_operation(), provider, budget_ceiling=Decimal("36"))

    with pytest.raises(ApprovalError, match="payload"):
        manager.approve_operation(
            preview.operation_id,
            preview.token,
            provider,
            payload_override={"budget": "999"},
        )

    assert provider.applied == []


def test_expired_and_replayed_tokens_are_rejected():
    provider = FakeAdProvider(Platform.META)
    manager = ApprovalManager()
    now = datetime.now(timezone.utc)
    preview = manager.preview_operation(make_operation(), provider, budget_ceiling=Decimal("36"), now=now)

    with pytest.raises(ApprovalError, match="expired"):
        manager.approve_operation(
            preview.operation_id,
            preview.token,
            provider,
            now=now + timedelta(minutes=11),
        )

    fresh = manager.preview_operation(make_operation(), provider, budget_ceiling=Decimal("36"), now=now)
    manager.approve_operation(fresh.operation_id, fresh.token, provider, now=now)
    with pytest.raises(ApprovalError, match="already"):
        manager.approve_operation(fresh.operation_id, fresh.token, provider, now=now)


def test_provider_failure_is_audited():
    class FailingProvider(FakeAdProvider):
        def apply_create_campaign(self, draft):
            raise RuntimeError("provider unavailable")

    provider = FailingProvider(Platform.META)
    manager = ApprovalManager()
    preview = manager.preview_operation(make_operation(), provider, budget_ceiling=Decimal("36"))

    with pytest.raises(RuntimeError, match="provider unavailable"):
        manager.approve_operation(preview.operation_id, preview.token, provider)

    assert manager.audit.events[-1].result == "error"
