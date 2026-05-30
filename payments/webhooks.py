"""Stripe webhook event handlers."""

import logging
from typing import Any, Dict, List, Tuple

from payments.connect import sync_account_status
from payments.ledger import append_payout_audit, find_claim_by_stripe_account

logger = logging.getLogger(__name__)


def handle_stripe_event(
    event: Dict[str, Any],
    claims: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply webhook side effects to in-memory claims list.
    Caller must persist the dataset after this returns changed=True.
    """
    event_type = event.get("type", "")
    data_object = event.get("data", {}).get("object", {})
    result: Dict[str, Any] = {"handled": False, "type": event_type}

    if event_type == "account.updated":
        account_id = data_object.get("id")
        claim = find_claim_by_stripe_account(claims, account_id)
        if not claim:
            result["message"] = "no matching claim"
            return claims, result
        sync_account_status(claim)
        result["handled"] = True
        result["claim_id"] = claim.get("claim_id")
        return claims, result

    if event_type in ("transfer.created", "transfer.paid"):
        claim_id = (data_object.get("metadata") or {}).get("claim_id")
        if claim_id:
            for claim in claims:
                if claim.get("claim_id") == claim_id:
                    claim["payout_status"] = "transferred"
                    claim["stripe_transfer_id"] = data_object.get("id")
                    append_payout_audit(
                        claim, event_type, detail=data_object.get("id", "")
                    )
                    result["handled"] = True
                    result["claim_id"] = claim_id
                    break
        return claims, result

    if event_type == "transfer.failed":
        claim_id = (data_object.get("metadata") or {}).get("claim_id")
        for claim in claims:
            if claim.get("claim_id") == claim_id:
                claim["payout_status"] = "failed"
                append_payout_audit(claim, "transfer.failed", detail=str(data_object))
                result["handled"] = True
                result["claim_id"] = claim_id
                break
        return claims, result

    logger.info("Unhandled Stripe event type: %s", event_type)
    result["message"] = "ignored"
    return claims, result
