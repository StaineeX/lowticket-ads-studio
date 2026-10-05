def test_recommendations_endpoint_returns_evidence_based_pause():
    from fastapi.testclient import TestClient

    from backend.app.main import app

    response = TestClient(app).post(
        "/api/recommendations/analyze",
        json={
            "economics": {
                "price": "47",
                "net_revenue": "42.30",
                "contribution_value": "33.84",
                "checkout_conversion_rate": "0.02",
            },
            "records": [
                {
                    "platform": "meta",
                    "campaign_id": "cmp-1",
                    "campaign_name": "Curso Express",
                    "metric_date": "2026-10-01",
                    "spend": "20",
                    "impressions": 100,
                    "clicks": 10,
                    "conversions": "0",
                    "revenue": "0",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()[0]["type"] == "pause"
