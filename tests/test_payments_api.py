import json

import pytest

from api_server import app


@pytest.fixture
def client(dataset_env):
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def _signup(client, email="stripe-flow@example.com"):
    return client.post(
        "/signup",
        json={
            "name": "Stripe Test",
            "email": email,
            "raw_user_data": "Inova",
            "consent_received": True,
            "w_fund_promise": True,
        },
    )


def test_health_reports_stripe_mock(client):
    response = client.get("/health")
    body = response.get_json()
    assert body["stripe_mode"] == "mock"


def test_connect_onboard(client):
    signup = _signup(client)
    claim_id = signup.get_json()["claim_id"]
    response = client.post(
        "/connect/onboard",
        json={"claim_id": claim_id, "email": "stripe-flow@example.com"},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["onboarding_url"]
    assert body["stripe_account_id"].startswith("acct_mock_")


def test_payouts_allocate_and_transfer(client):
    signup = _signup(client, email="allocate@example.com")
    claim_id = signup.get_json()["claim_id"]
    client.post(
        "/connect/onboard",
        json={"claim_id": claim_id, "email": "allocate@example.com"},
    )
    client.post("/connect/sync", json={"claim_id": claim_id})

    response = client.post(
        "/payouts/allocate",
        json={
            "claim_id": claim_id,
            "gross_payout_cents": 10000,
            "admin_note": "pytest",
            "execute_transfer": True,
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["claimant_cents"] == 5100
    assert body["transfer"]["payout_status"] == "transferred"


def test_payouts_get(client):
    signup = _signup(client, email="detail@example.com")
    claim_id = signup.get_json()["claim_id"]
    response = client.get(f"/payouts/{claim_id}")
    assert response.status_code == 200
    assert response.get_json()["payout_status"] == "pending"


def test_stripe_webhook_account_updated(client):
    signup = _signup(client, email="webhook@example.com")
    claim_id = signup.get_json()["claim_id"]
    onboard = client.post(
        "/connect/onboard",
        json={"claim_id": claim_id, "email": "webhook@example.com"},
    )
    account_id = onboard.get_json()["stripe_account_id"]

    event = {
        "type": "account.updated",
        "data": {
            "object": {
                "id": account_id,
                "charges_enabled": True,
                "payouts_enabled": True,
            }
        },
    }
    response = client.post(
        "/webhooks/stripe",
        data=json.dumps(event),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json()["handled"] is True

    detail = client.get(f"/payouts/{claim_id}").get_json()
    assert detail["stripe_onboarding_complete"] is True
