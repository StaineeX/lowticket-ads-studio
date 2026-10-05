from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


MONEY = Decimal("0.01")


@dataclass(frozen=True)
class EconomicsResult:
    price: Decimal
    net_revenue: Decimal
    contribution_value: Decimal
    checkout_conversion_rate: Decimal


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def _validate_percentage(name: str, value: Decimal, *, allow_zero: bool = True) -> None:
    if value < 0 or value > 100 or (not allow_zero and value == 0):
        raise ValueError(f"{name} must be between 0 and 100")


def calculate_economics(
    *,
    price: Decimal,
    gross_margin_pct: Decimal,
    checkout_conversion_pct: Decimal,
    refund_pct: Decimal,
) -> EconomicsResult:
    if price <= 0:
        raise ValueError("price must be greater than zero")
    _validate_percentage("gross_margin_pct", gross_margin_pct, allow_zero=False)
    _validate_percentage("checkout_conversion_pct", checkout_conversion_pct, allow_zero=False)
    _validate_percentage("refund_pct", refund_pct)

    net_revenue = price * (Decimal("1") - refund_pct / Decimal("100"))
    contribution_value = net_revenue * gross_margin_pct / Decimal("100")
    return EconomicsResult(
        price=_money(price),
        net_revenue=_money(net_revenue),
        contribution_value=_money(contribution_value),
        checkout_conversion_rate=checkout_conversion_pct / Decimal("100"),
    )


def break_even_cpa(economics: EconomicsResult) -> Decimal:
    return _money(economics.contribution_value * economics.checkout_conversion_rate)


def break_even_roas(economics: EconomicsResult) -> Decimal:
    if economics.contribution_value <= 0:
        raise ValueError("contribution value must be greater than zero")
    return _money(economics.price / economics.contribution_value)


def default_budget_ceiling(target_cpa: Decimal) -> Decimal:
    if target_cpa <= 0:
        raise ValueError("target_cpa must be greater than zero")
    return _money(target_cpa * Decimal("3"))
