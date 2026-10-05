from decimal import Decimal

import pytest

from backend.app.domain.economics import (
    break_even_cpa,
    break_even_roas,
    calculate_economics,
    default_budget_ceiling,
)


def test_calculates_net_revenue_contribution_and_break_even_metrics():
    economics = calculate_economics(
        price=Decimal("47.00"),
        gross_margin_pct=Decimal("80"),
        checkout_conversion_pct=Decimal("2"),
        refund_pct=Decimal("10"),
    )

    assert economics.net_revenue == Decimal("42.30")
    assert economics.contribution_value == Decimal("33.84")
    assert break_even_cpa(economics) == Decimal("0.68")
    assert break_even_roas(economics) == Decimal("1.39")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("price", Decimal("0")),
        ("gross_margin_pct", Decimal("101")),
        ("checkout_conversion_pct", Decimal("0")),
        ("refund_pct", Decimal("-1")),
    ],
)
def test_rejects_invalid_economic_inputs(field, value):
    inputs = {
        "price": Decimal("47"),
        "gross_margin_pct": Decimal("80"),
        "checkout_conversion_pct": Decimal("2"),
        "refund_pct": Decimal("10"),
    }
    inputs[field] = value

    with pytest.raises(ValueError):
        calculate_economics(**inputs)


def test_default_budget_ceiling_is_three_times_target_cpa():
    assert default_budget_ceiling(Decimal("12.50")) == Decimal("37.50")

    with pytest.raises(ValueError):
        default_budget_ceiling(Decimal("0"))
