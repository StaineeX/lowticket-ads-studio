from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.main import app


def draft_payload():
    return {
        "platform": "meta",
        "budget_ceiling": "36.00",
        "draft": {
            "offer_name": "Curso Express",
            "benefit": "Aprenda uma habilidade prática",
            "audience": "iniciantes",
            "proof": "aulas curtas",
            "cta": "Comece agora",
            "price": "47.00",
            "currency": "BRL",
            "budget": "20.00",
            "platforms": ["meta"],
        },
    }


def test_preview_then_approve_operation():
    client = TestClient(app)
    preview = client.post("/api/operations/preview", json=draft_payload())

    assert preview.status_code == 200
    body = preview.json()
    assert body["status"] == "preview"
    assert body["token"]

    result = client.post(
        f"/api/operations/{body['operation_id']}/approve",
        json={"token": body["token"]},
    )

    assert result.status_code == 200
    assert result.json()["status"] == "applied"
    assert result.json()["campaign"]["status"] == "paused"


def test_audit_endpoint_exposes_operation_history():
    response = TestClient(app).get("/api/audit")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
