import csv
import io
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from backend.app.domain.campaigns import Platform
from backend.app.models import MetricRow


@dataclass(frozen=True)
class ImportRowError:
    row: int
    message: str


@dataclass(frozen=True)
class MetricRecord:
    platform: Platform
    campaign_id: str
    campaign_name: str
    metric_date: date
    spend: Decimal
    impressions: int
    clicks: int
    conversions: Decimal
    revenue: Decimal

    def to_row(self) -> MetricRow:
        return MetricRow(
            platform=self.platform.value,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            metric_date=self.metric_date,
            spend=self.spend,
            impressions=self.impressions,
            clicks=self.clicks,
            conversions=self.conversions,
            revenue=self.revenue,
        )


@dataclass(frozen=True)
class ImportResult:
    records: list[MetricRecord]
    errors: list[ImportRowError]

    @property
    def imported(self) -> int:
        return len(self.records)


ALIASES = {
    "campaign_id": ("campaign id", "campaign_id", "id da campanha"),
    "campaign_name": ("campaign name", "campaign", "nome da campanha"),
    "date": ("date", "date start", "day", "data", "data inicial"),
    "spend": ("spend", "amount spent", "cost", "valor gasto", "custo"),
    "impressions": ("impressions", "impressões", "impressions count"),
    "clicks": ("clicks", "link clicks", "cliques"),
    "conversions": ("conversions", "purchases", "results", "conversões", "compras"),
    "revenue": (
        "revenue",
        "purchase conversion value",
        "conversions value",
        "valor de conversão",
    ),
}


def _clean_header(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _field(row: dict[str, str], name: str) -> str:
    aliases = set(ALIASES[name])
    for key, value in row.items():
        if _clean_header(key) in aliases:
            return value.strip()
    return ""


def _decimal(value: str) -> Decimal:
    value = value.strip().replace(" ", "")
    if not value:
        return Decimal("0")
    if "," in value and "." in value:
        value = value.replace(",", "")
    else:
        value = value.replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal value: {value}") from exc


def _integer(value: str) -> int:
    return int(_decimal(value)) if value.strip() else 0


class MetricImporter:
    def import_csv(self, content: bytes, platform: Platform) -> ImportResult:
        text = content.decode("utf-8-sig")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        records: list[MetricRecord] = []
        errors: list[ImportRowError] = []
        for row_number, row in enumerate(reader, start=2):
            campaign_id = _field(row, "campaign_id")
            metric_date = _field(row, "date")
            if not campaign_id:
                errors.append(ImportRowError(row_number, "campaign identifier is required"))
                continue
            if not metric_date:
                errors.append(ImportRowError(row_number, "metric date is required"))
                continue
            try:
                records.append(
                    MetricRecord(
                        platform=platform,
                        campaign_id=campaign_id,
                        campaign_name=_field(row, "campaign_name"),
                        metric_date=date.fromisoformat(metric_date),
                        spend=_decimal(_field(row, "spend")),
                        impressions=_integer(_field(row, "impressions")),
                        clicks=_integer(_field(row, "clicks")),
                        conversions=_decimal(_field(row, "conversions")),
                        revenue=_decimal(_field(row, "revenue")),
                    )
                )
            except (ValueError, TypeError) as exc:
                errors.append(ImportRowError(row_number, str(exc)))
        return ImportResult(records=records, errors=errors)
