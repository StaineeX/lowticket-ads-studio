import os

from backend.app.ai.openai_compatible import OpenAICompatibleAIProvider
from backend.app.ai.ports import AIProvider, DeterministicAIProvider


def campaign_ai_provider() -> AIProvider:
    provider_name = os.getenv("AI_PROVIDER", "deterministic").strip().lower()
    if provider_name in {"openai", "openai_compatible", "ollama"}:
        return OpenAICompatibleAIProvider.from_env()
    return DeterministicAIProvider()
