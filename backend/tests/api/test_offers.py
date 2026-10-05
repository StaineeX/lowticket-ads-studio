from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import Base, get_db_session
from backend.app.main import app


def test_create_and_list_offer_round_trip():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_session():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_session
    try:
        client = TestClient(app)
        response = client.post(
            "/api/offers",
            json={
                "name": "Curso Express",
                "landing_url": "https://example.com/curso",
                "currency": "BRL",
                "price": "47.00",
                "gross_margin_pct": "80",
                "checkout_conversion_pct": "2",
                "refund_pct": "10",
                "target_cpa": "12.00",
            },
        )

        assert response.status_code == 201
        assert response.json()["price"] == "47.00"

        listed = client.get("/api/offers")
        assert listed.status_code == 200
        assert listed.json()[0]["name"] == "Curso Express"
        assert Decimal(listed.json()[0]["target_cpa"]) == Decimal("12.00")
    finally:
        app.dependency_overrides.clear()


def test_metrics_import_rejects_unknown_platform():
    client = TestClient(app)

    response = client.post(
        "/api/metrics/import?platform=unknown",
        files={"file": ("metrics.csv", b"Campaign,Date\n123,2026-10-01\n", "text/csv")},
    )

    assert response.status_code == 422
