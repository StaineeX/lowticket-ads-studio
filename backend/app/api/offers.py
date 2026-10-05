from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.db import get_db_session
from backend.app.repositories import Offer, OfferCreate, OfferRepository


router = APIRouter(prefix="/api")


@router.post("/offers", response_model=Offer, status_code=status.HTTP_201_CREATED)
def create_offer(data: OfferCreate, session: Session = Depends(get_db_session)) -> Offer:
    return OfferRepository(session).create(data)


@router.get("/offers", response_model=list[Offer])
def list_offers(session: Session = Depends(get_db_session)) -> list[Offer]:
    return OfferRepository(session).list()
