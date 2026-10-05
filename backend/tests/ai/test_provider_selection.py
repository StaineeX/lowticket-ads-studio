from backend.app.ai.factory import campaign_ai_provider
from backend.app.ai.openai_compatible import OpenAICompatibleAIProvider
from backend.app.ai.ports import DeterministicAIProvider


def test_provider_defaults_to_deterministic(monkeypatch):
    monkeypatch.delenv("AI_PROVIDER", raising=False)

    provider = campaign_ai_provider()

    assert isinstance(provider, DeterministicAIProvider)


def test_provider_can_use_openai_compatible_endpoint(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "openai_compatible")
    monkeypatch.setenv("AI_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("AI_API_KEY", "local-key")
    monkeypatch.setenv("AI_MODEL", "qwen2.5:7b")

    provider = campaign_ai_provider()

    assert isinstance(provider, OpenAICompatibleAIProvider)
    provider.client.close()
