"""Allocate settlement proceeds and transfer claimant share."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from payments.ledger import append_payout_audit, compute_splits, ensure_payout_fields
from payments import stripe_client


def allocate_payout(
    claim: Dict[str, Any],
    gross_payout_cents: int,
    *,
    admin_note: str = "",
    actor: str = "admin",
) -> Dict[str, Any]:
    ensure_payout_fields(claim)
    splits = compute_splits(
        gross_payout_cents, w_fund_promise=bool(claim.get("w_fund_promise"))
    )

    claim.update(splits)
    claim["payout_status"] = "allocated"
    claim["payout_allocated_at"] = datetime.now(timezone.utc).isoformat()
    append_payout_audit(
        claim,
        "payout_allocated",
        detail=admin_note or f"gross={gross_payout_cents}",
        actor=actor,
    )

    return {
        "claim_id": claim["claim_id"],
        "payout_status": claim["payout_status"],
        **splits,
    }


def execute_transfer(
    claim: Dict[str, Any],
    *,
    actor: str = "admin",
    idempotency_key: Optional[str] = None,
) -> Dict[str, Any]:
    ensure_payout_fields(claim)

    if claim.get("payout_status") not in ("allocated", "ready"):
        raise ValueError(
            "Claim must be allocated before transfer "
            f"(current status: {claim.get('payout_status')})"
        )
    if not claim.get("stripe_onboarding_complete"):
        sync = stripe_client.retrieve_account(claim.get("stripe_account_id", ""))
        if not (sync.get("charges_enabled") and sync.get("payouts_enabled")):
            raise ValueError("Stripe Connect onboarding not complete for claimant")
        claim["stripe_onboarding_complete"] = True

    account_id = claim.get("stripe_account_id")
    if not account_id:
        raise ValueError("Claim has no stripe_account_id; run /connect/onboard first")

    amount = claim.get("claimant_cents")
    if not amount or amount <= 0:
        raise ValueError("No claimant_cents to transfer")

    key = idempotency_key or f"transfer-{claim['claim_id']}-{amount}"
    transfer = stripe_client.create_transfer(
        amount_cents=amount,
        destination_account_id=account_id,
        claim_id=claim["claim_id"],
        idempotency_key=key,
    )

    claim["stripe_transfer_id"] = transfer["id"]
    claim["payout_status"] = "transferred"
    claim["payout_transferred_at"] = datetime.now(timezone.utc).isoformat()
    append_payout_audit(
        claim,
        "transfer_created",
        detail=transfer["id"],
        actor=actor,
    )

    return {
        "claim_id": claim["claim_id"],
        "payout_status": claim["payout_status"],
        "stripe_transfer_id": transfer["id"],
        "claimant_cents": amount,
        "mock": transfer.get("mock", False),
    }
