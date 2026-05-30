"""Stripe SDK wrapper with mock mode for local dev and tests."""

import os
import uuid
from typing import Any, Dict, Optional

_stripe = None


def mock_mode() -> bool:
    if os.environ.get("STRIPE_MOCK_MODE", "").lower() in ("1", "true", "yes"):
        return True
    return not os.environ.get("STRIPE_SECRET_KEY", "").strip()


def stripe_configured() -> bool:
    return not mock_mode()


def get_stripe():
    global _stripe
    if mock_mode():
        return None
    if _stripe is None:
        import stripe

        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        _stripe = stripe
    return _stripe


def create_express_account(*, email: str, claim_id: str) -> Dict[str, Any]:
    if mock_mode():
        account_id = f"acct_mock_{uuid.uuid4().hex[:12]}"
        return {"id": account_id, "mock": True}

    stripe = get_stripe()
    account = stripe.Account.create(
        type="express",
        email=email,
        capabilities={"transfers": {"requested": True}},
        metadata={"claim_id": claim_id, "platform": "coop_claims"},
    )
    return {"id": account.id, "mock": False}


def create_account_link(
    account_id: str,
    *,
    return_url: str,
    refresh_url: str,
) -> Dict[str, Any]:
    if mock_mode():
        return {
            "url": f"https://connect.stripe.com/setup/mock/{account_id}",
            "expires_at": None,
            "mock": True,
        }

    stripe = get_stripe()
    link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )
    return {"url": link.url, "expires_at": link.expires_at, "mock": False}


def create_transfer(
    *,
    amount_cents: int,
    destination_account_id: str,
    claim_id: str,
    idempotency_key: str,
) -> Dict[str, Any]:
    if amount_cents <= 0:
        raise ValueError("Transfer amount must be positive")

    if mock_mode():
        return {
            "id": f"tr_mock_{uuid.uuid4().hex[:12]}",
            "amount": amount_cents,
            "mock": True,
        }

    stripe = get_stripe()
    transfer = stripe.Transfer.create(
        amount=amount_cents,
        currency="usd",
        destination=destination_account_id,
        metadata={"claim_id": claim_id},
        idempotency_key=idempotency_key,
    )
    return {"id": transfer.id, "amount": transfer.amount, "mock": False}


def retrieve_account(account_id: str) -> Dict[str, Any]:
    if mock_mode():
        return {
            "id": account_id,
            "charges_enabled": True,
            "payouts_enabled": True,
            "details_submitted": True,
            "mock": True,
        }

    stripe = get_stripe()
    account = stripe.Account.retrieve(account_id)
    return {
        "id": account.id,
        "charges_enabled": account.charges_enabled,
        "payouts_enabled": account.payouts_enabled,
        "details_submitted": account.details_submitted,
        "mock": False,
    }


def construct_webhook_event(
    payload: bytes,
    signature: Optional[str],
) -> Dict[str, Any]:
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if mock_mode():
        import json

        return json.loads(payload.decode("utf-8"))

    if not secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET is required when Stripe is configured")
    if not signature:
        raise ValueError("Missing Stripe-Signature header")

    stripe = get_stripe()
    event = stripe.Webhook.construct_event(payload, signature, secret)
    return event.to_dict() if hasattr(event, "to_dict") else dict(event)
