from datetime import date
from decimal import Decimal

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from backend.app.domain.campaigns import Platform
from backend.app.domain.economics import EconomicsResult
from backend.app.services.metrics_import import MetricRecord
from backend.app.services.recommendations import analyze_metrics


router = APIRouter(prefix="/api")


class EconomicsPayload(BaseModel):
    price: Decimal
    net_revenue: Decimal
    contribution_value: Decimal
    checkout_conversion_rate: Decimal


class MetricPayload(BaseModel):
    platform: Platform
    campaign_id: str
    campaign_name: str = ""
    metric_date: date
    spend: Decimal = Decimal("0")
    impressions: int = 0
    clicks: int = 0
    conversions: Decimal = Decimal("0")
    revenue: Decimal = Decimal("0")


class RecommendationRequest(BaseModel):
    economics: EconomicsPayload
    records: list[MetricPayload]


@router.post("/recommendations/analyze")
def analyze_recommendations(request: RecommendationRequest) -> list[dict]:
    economics = EconomicsResult(**request.economics.model_dump())
    records = [MetricRecord(**record.model_dump()) for record in request.records]
    return jsonable_encoder(analyze_metrics(records, economics))
