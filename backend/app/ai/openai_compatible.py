import json
import os
from decimal import Decimal
from typing import Any

import httpx

from backend.app.ai.ports import AIProvider, CampaignBrief, CampaignBriefRequest
from backend.app.domain.campaigns import CampaignCopy


class AIProviderError(RuntimeError):
    """Raised when an AI provider cannot return a valid brief."""


class OpenAICompatibleAIProvider:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        transport: httpx.BaseTransport | None = None,
    ):
        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=30,
            transport=transport,
        )
        self.model = model

    @classmethod
    def from_env(cls) -> "OpenAICompatibleAIProvider":
        return cls(
            base_url=os.getenv("AI_BASE_URL", "http://localhost:11434/v1"),
            api_key=os.getenv("AI_API_KEY", ""),
            model=os.getenv("AI_MODEL", "qwen2.5:7b"),
        )

    def generate_campaign_brief(self, request: CampaignBriefRequest) -> CampaignBrief:
        prompt = {
            "platform": request.platform.value,
            "offer_name": request.offer_name,
            "benefit": request.benefit,
            "audience": request.audience,
            "proof": request.proof,
            "cta": request.cta,
            "price": str(request.price),
            "currency": request.currency,
            "angle": request.angle,
            "output": "JSON with primary_text, headline, description, cta, google_headlines, google_descriptions, creative_brief",
        }
        try:
            response = self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "temperature": 0.7,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You create truthful performance ad drafts. Return JSON only.",
                        },
                        {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                    ],
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            payload: dict[str, Any] = json.loads(content)
            return CampaignBrief(
                copy=CampaignCopy(
                    primary_text=str(payload.get("primary_text", "")),
                    headline=str(payload.get("headline", "")),
                    description=str(payload.get("description", "")),
                    cta=str(payload.get("cta", request.cta)),
                    google_headlines=[str(value) for value in payload.get("google_headlines", [])],
                    google_descriptions=[str(value) for value in payload.get("google_descriptions", [])],
                ),
                creative_brief=str(payload.get("creative_brief", "")),
            )
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AIProviderError("AI provider returned an invalid campaign brief") from exc
