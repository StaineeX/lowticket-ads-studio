from dataclasses import dataclass
from decimal import Decimal

from backend.app.domain.economics import EconomicsResult, break_even_cpa, break_even_roas
from backend.app.services.metrics_import import MetricRecord


@dataclass(frozen=True)
class Recommendation:
    type: str
    rationale: str
    evidence: dict[str, str]
    proposed_change: dict[str, str]
    risk_level: str
    status: str = "open"


def analyze_metrics(
    records: list[MetricRecord],
    economics: EconomicsResult,
) -> list[Recommendation]:
    spend = sum((record.spend for record in records), Decimal("0"))
    conversions = sum((record.conversions for record in records), Decimal("0"))
    revenue = sum((record.revenue for record in records), Decimal("0"))
    if spend > 0 and conversions == 0:
        return [
            Recommendation(
                type="pause",
                rationale="Campaign spent money without recording a conversion.",
                evidence={"spend": str(spend), "conversions": str(conversions)},
                proposed_change={"status": "paused"},
                risk_level="high",
            )
        ]
    if conversions > 0:
        cpa = spend / conversions
        roas = revenue / spend if spend else Decimal("0")
        if cpa < break_even_cpa(economics) and roas > break_even_roas(economics):
            return [
                Recommendation(
                    type="scale",
                    rationale="CPA is below break-even and ROAS is above break-even.",
                    evidence={"cpa": str(cpa), "roas": str(roas)},
                    proposed_change={"budget_multiplier": "1.2"},
                    risk_level="medium",
                )
            ]
    return []
