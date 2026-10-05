from decimal import Decimal

from backend.app.domain.campaigns import Platform
from backend.app.services.metrics_import import MetricImporter


def test_imports_meta_csv_with_bom_and_decimal_comma():
    content = (
        "\ufeffCampaign ID;Campaign Name;Date Start;Amount Spent;Impressions;Link Clicks;Purchases;Purchase Conversion Value\n"
        "123;Curso Express;2026-10-01;12,50;1000;20;2;94,00\n"
    ).encode("utf-8")

    result = MetricImporter().import_csv(content, Platform.META)

    assert result.imported == 1
    assert result.errors == []
    assert result.records[0].campaign_id == "123"
    assert result.records[0].spend == Decimal("12.50")
    assert result.records[0].revenue == Decimal("94.00")


def test_rejects_metric_row_without_campaign_identifier():
    content = b"Date,Spend\n2026-10-01,12.50\n"

    result = MetricImporter().import_csv(content, Platform.GOOGLE)

    assert result.imported == 0
    assert result.errors[0].row == 2
    assert "campaign" in result.errors[0].message.lower()
