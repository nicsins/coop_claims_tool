import os

import requests

API_BASE = os.environ.get("CLAIMS_API_BASE", "http://127.0.0.1:5000").rstrip("/")
REQUEST_TIMEOUT = int(os.environ.get("CLAIMS_HTTP_TIMEOUT", "30"))


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("CLAIMS_API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def _request(method: str, path: str, **kwargs):
    url = f"{API_BASE}{path}"
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    kwargs.setdefault("headers", _headers())
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json()


def scrape_no_proof():
    return _request("POST", "/scrape")


def mcp_fill(claim_id: str):
    return _request("POST", "/process_mcp", json={"claim_id": claim_id})


def view_dashboard():
    return _request("GET", "/dashboard")


def connect_onboard(claim_id: str, email: str):
    return _request(
        "POST",
        "/connect/onboard",
        json={"claim_id": claim_id, "email": email},
    )


def payouts_allocate(
    claim_id: str,
    gross_payout_cents: int,
    *,
    admin_note: str = "",
    execute_transfer: bool = False,
):
    return _request(
        "POST",
        "/payouts/allocate",
        json={
            "claim_id": claim_id,
            "gross_payout_cents": gross_payout_cents,
            "admin_note": admin_note,
            "execute_transfer": execute_transfer,
        },
    )
