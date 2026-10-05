from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db import Base


class OfferRow(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    landing_url: Mapped[str] = mapped_column(String(500))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    gross_margin_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    checkout_conversion_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    refund_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    target_cpa: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    target_roas: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MetricRow(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(20))
    campaign_id: Mapped[str] = mapped_column(String(160), index=True)
    campaign_name: Mapped[str] = mapped_column(String(240), default="")
    metric_date: Mapped[date] = mapped_column(Date)
    spend: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
