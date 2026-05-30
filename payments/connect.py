"""Stripe Connect onboarding for claimants."""

from typing import Any, Dict, Optional

from payments.config import stripe_connect_refresh_url, stripe_connect_return_url
from payments.ledger import append_payout_audit, ensure_payout_fields
from payments import stripe_client


def start_connect_onboarding(
    claim: Dict[str, Any],
    *,
    email: str,
    return_url: Optional[str] = None,
    refresh_url: Optional[str] = None,
) -> Dict[str, Any]:
    ensure_payout_fields(claim)
    return_url = return_url or stripe_connect_return_url()
    refresh_url = refresh_url or stripe_connect_refresh_url()

    account_id = claim.get("stripe_account_id")
    if not account_id:
        account = stripe_client.create_express_account(
            email=email, claim_id=claim["claim_id"]
        )
        account_id = account["id"]
        claim["stripe_account_id"] = account_id
        append_payout_audit(
            claim,
            "connect_account_created",
            detail=account_id,
            actor="connect",
        )

    link = stripe_client.create_account_link(
        account_id,
        return_url=return_url,
        refresh_url=refresh_url,
    )
    claim["payout_status"] = "onboarding"
    append_payout_audit(claim, "onboarding_link_created", detail=link["url"])

    return {
        "claim_id": claim["claim_id"],
        "stripe_account_id": account_id,
        "onboarding_url": link["url"],
        "mock": link.get("mock", False),
    }


def sync_account_status(claim: Dict[str, Any]) -> Dict[str, Any]:
    account_id = claim.get("stripe_account_id")
    if not account_id:
        raise ValueError("Claim has no stripe_account_id")

    account = stripe_client.retrieve_account(account_id)
    ready = bool(account.get("charges_enabled") and account.get("payouts_enabled"))
    claim["stripe_onboarding_complete"] = ready
    if ready:
        claim["payout_status"] = "ready"
        append_payout_audit(claim, "connect_onboarding_complete", detail=account_id)
    return {
        "claim_id": claim["claim_id"],
        "stripe_onboarding_complete": ready,
        "payout_status": claim.get("payout_status"),
    }
