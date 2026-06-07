import pytest

from api_server import app


@pytest.fixture
def client(dataset_env):
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_dashboard_not_null(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert "total_settlements" in body


def test_process_mcp_missing_claim_id(client):
    response = client.post("/process_mcp", json={})
    assert response.status_code == 400


def test_signup_requires_consent(client):
    response = client.post(
        "/signup",
        json={"name": "A", "email": "a@example.com", "consent_received": False},
    )
    assert response.status_code == 400


def test_signup_success(client):
    response = client.post(
        "/signup",
        json={
            "name": "API Test",
            "email": "api-test@example.com",
            "raw_user_data": "Inova visitor",
            "consent_received": True,
            "w_fund_promise": True,
        },
    )
    assert response.status_code == 201
    assert response.get_json()["claim_id"].startswith("web_")


def test_api_key_required_when_configured(client, monkeypatch):
    monkeypatch.setenv("CLAIMS_API_KEY", "secret-test-key")
    response = client.post("/scrape")
    assert response.status_code == 401
    response = client.post(
        "/scrape", headers={"X-API-Key": "secret-test-key"}
    )
    assert response.status_code == 200
