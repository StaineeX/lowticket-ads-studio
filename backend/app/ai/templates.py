from decimal import Decimal

from backend.app.domain.campaigns import CampaignCopy, Platform


def _truncate(value: str, maximum: int) -> str:
    return value if len(value) <= maximum else value[: maximum - 1].rstrip() + "…"


def build_copy(
    *,
    platform: Platform,
    offer_name: str,
    benefit: str,
    audience: str,
    proof: str,
    cta: str,
    price: Decimal,
    currency: str,
    angle: str,
) -> CampaignCopy:
    short_price = f"{currency} {price:.2f}"
    primary_text = f"{benefit}. Feito para {audience}. {proof}. {cta}."
    headline = f"{offer_name} por {short_price}"
    description = f"{angle}. Acesso imediato."
    if platform is Platform.META:
        return CampaignCopy(
            primary_text=_truncate(primary_text, 500),
            headline=_truncate(headline, 40),
            description=_truncate(description, 30),
            cta=_truncate(cta, 40),
        )

    google_headlines = [
        _truncate(offer_name, 30),
        _truncate(benefit, 30),
        _truncate(f"Comece por {short_price}", 30),
        _truncate(cta, 30),
    ]
    google_descriptions = [
        _truncate(f"{benefit}. {proof}. {cta}.", 90),
        _truncate(f"Método simples para {audience}. Acesse agora.", 90),
    ]
    return CampaignCopy(
        google_headlines=google_headlines,
        google_descriptions=google_descriptions,
    )
