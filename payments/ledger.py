"""Payout ledger fields and split math."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from payments.config import get_split_rates


def default_payout_fields() -> Dict[str, Any]:
    return {
        "payout_status": "pending",
        "stripe_account_id": None,
        "stripe_onboarding_complete": False,
        "gross_payout_cents": None,
        "claimant_cents": None,
        "war_chest_cents": None,
        "w_fund_cents": None,
        "platform_fee_cents": None,
        "stripe_transfer_id": None,
        "payout_allocated_at": None,
        "payout_transferred_at": None,
        "payout_audit": [],
    }


def ensure_payout_fields(claim: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in default_payout_fields().items():
        claim.setdefault(key, value if not isinstance(value, list) else [])
    if claim.get("payout_audit") is None:
        claim["payout_audit"] = []
    return claim


def append_payout_audit(
    claim: Dict[str, Any],
    action: str,
    *,
    detail: str = "",
    actor: str = "system",
) -> None:
    ensure_payout_fields(claim)
    claim["payout_audit"].append(
        {
            "at": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "actor": actor,
            "detail": detail,
        }
    )


def compute_splits(gross_cents: int, *, w_fund_promise: bool) -> Dict[str, int]:
    if gross_cents < 0:
        raise ValueError("gross_payout_cents must be non-negative")

    rates = get_split_rates(w_fund_promise=w_fund_promise)
    claimant = int(round(gross_cents * rates.claimant))
    war_chest = int(round(gross_cents * rates.war_chest))
    w_fund = int(round(gross_cents * rates.w_fund))
    platform_fee = war_chest + w_fund

    # Fix rounding drift: assign remainder to claimant
    remainder = gross_cents - claimant - war_chest - w_fund
    claimant += remainder

    return {
        "gross_payout_cents": gross_cents,
        "claimant_cents": claimant,
        "war_chest_cents": war_chest,
        "w_fund_cents": w_fund,
        "platform_fee_cents": platform_fee,
        "rates_applied": {
            "claimant": rates.claimant,
            "war_chest": rates.war_chest,
            "w_fund": rates.w_fund,
            "w_fund_promise": w_fund_promise,
        },
    }


def payout_summary(claim: Dict[str, Any]) -> Dict[str, Any]:
    ensure_payout_fields(claim)
    return {
        "claim_id": claim.get("claim_id"),
        "payout_status": claim.get("payout_status"),
        "stripe_account_id": claim.get("stripe_account_id"),
        "stripe_onboarding_complete": claim.get("stripe_onboarding_complete"),
        "gross_payout_cents": claim.get("gross_payout_cents"),
        "claimant_cents": claim.get("claimant_cents"),
        "war_chest_cents": claim.get("war_chest_cents"),
        "w_fund_cents": claim.get("w_fund_cents"),
        "platform_fee_cents": claim.get("platform_fee_cents"),
        "stripe_transfer_id": claim.get("stripe_transfer_id"),
        "payout_allocated_at": claim.get("payout_allocated_at"),
        "payout_transferred_at": claim.get("payout_transferred_at"),
    }


def find_claim_by_stripe_account(
    claims: List[Dict[str, Any]], account_id: str
) -> Optional[Dict[str, Any]]:
    for claim in claims:
        if claim.get("stripe_account_id") == account_id:
            return claim
    return None
