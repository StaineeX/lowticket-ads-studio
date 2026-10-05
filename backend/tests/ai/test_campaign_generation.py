from decimal import Decimal

from backend.app.ai.ports import DeterministicAIProvider
from backend.app.ai.openai_compatible import OpenAICompatibleAIProvider
from backend.app.ai.ports import CampaignBriefRequest
from backend.app.ai.service import CampaignDraftRequest, CampaignService
from backend.app.domain.campaigns import Platform


def test_generates_three_variants_per_platform_without_ai_credentials():
    request = CampaignDraftRequest(
        offer_name="Curso Express",
        benefit="Aprenda uma habilidade prática",
        audience="profissionais iniciantes",
        proof="método em aulas curtas",
        cta="Comece agora",
        price=Decimal("47.00"),
        currency="BRL",
        budget=Decimal("36.00"),
        platforms=[Platform.META, Platform.GOOGLE],
    )

    draft = CampaignService(DeterministicAIProvider()).generate_draft(request)

    assert draft.status == "paused"
    assert len(draft.variants[Platform.META]) == 3
    assert len(draft.variants[Platform.GOOGLE]) == 3
    assert all(not variant.validation_issues for variants in draft.variants.values() for variant in variants)


def test_google_variants_respect_rsa_limits():
    request = CampaignDraftRequest(
        offer_name="Curso Express",
        benefit="Aprenda uma habilidade prática",
        audience="profissionais iniciantes",
        proof="aulas curtas",
        cta="Comece agora",
        price=Decimal("47.00"),
        currency="BRL",
        budget=Decimal("36.00"),
        platforms=[Platform.GOOGLE],
    )

    draft = CampaignService(DeterministicAIProvider()).generate_draft(request)

    for variant in draft.variants[Platform.GOOGLE]:
        assert all(len(headline) <= 30 for headline in variant.copy.google_headlines)
        assert all(len(description) <= 90 for description in variant.copy.google_descriptions)


def test_openai_compatible_provider_parses_structured_campaign_brief():
    import httpx

    def handler(request):
        assert request.url.path == "/v1/chat/completions"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"primary_text":"Texto","headline":"Oferta","description":"Acesso","cta":"Saiba mais","creative_brief":"Produto em uso"}'
                        }
                    }
                ]
            },
        )

    provider = OpenAICompatibleAIProvider(
        base_url="https://local.test/v1",
        api_key="local-key",
        model="local-model",
        transport=httpx.MockTransport(handler),
    )
    brief = provider.generate_campaign_brief(
        CampaignBriefRequest(
            platform=Platform.META,
            offer_name="Curso",
            benefit="Aprenda rápido",
            audience="iniciantes",
            proof="aulas curtas",
            cta="Saiba mais",
            price=Decimal("47"),
            currency="BRL",
            angle="Praticidade",
        )
    )

    assert brief.copy.headline == "Oferta"
    assert brief.creative_brief == "Produto em uso"
