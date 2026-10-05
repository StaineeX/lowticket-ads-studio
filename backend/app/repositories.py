from decimal import Decimal

from pydantic import BaseModel, ConfigDict, HttpUrl
from sqlalchemy.orm import Session

from backend.app.models import OfferRow


class OfferCreate(BaseModel):
    name: str
    landing_url: HttpUrl
    currency: str = "BRL"
    price: Decimal
    gross_margin_pct: Decimal
    checkout_conversion_pct: Decimal
    refund_pct: Decimal = Decimal("0")
    target_cpa: Decimal
    target_roas: Decimal | None = None


class Offer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    landing_url: str
    currency: str
    price: Decimal
    gross_margin_pct: Decimal
    checkout_conversion_pct: Decimal
    refund_pct: Decimal
    target_cpa: Decimal
    target_roas: Decimal | None = None


class OfferRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: OfferCreate) -> Offer:
        row = OfferRow(
            name=data.name.strip(),
            landing_url=str(data.landing_url),
            currency=data.currency.upper(),
            price=data.price,
            gross_margin_pct=data.gross_margin_pct,
            checkout_conversion_pct=data.checkout_conversion_pct,
            refund_pct=data.refund_pct,
            target_cpa=data.target_cpa,
            target_roas=data.target_roas,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return Offer.model_validate(row)

    def list(self) -> list[Offer]:
        rows = self.session.query(OfferRow).order_by(OfferRow.id.desc()).all()
        return [Offer.model_validate(row) for row in rows]
