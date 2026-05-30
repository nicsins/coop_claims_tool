import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from mcp_claim_logic import (
    mcp_fill_claim_with_constraints,
    mcp_ingest_claims,
    mcp_submit_for_verification,
    verify_claims_batch,
)
from payments.ledger import default_payout_fields, ensure_payout_fields, payout_summary

DATASET_FILE = os.environ.get("CLAIMS_DATASET_FILE", "claims_dataset.json")


def default_dataset() -> Dict[str, Any]:
    return {
        "settlements": [],
        "claims": [],
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_submitted": 0,
            "war_chest_alloc": 0.20,
            "w_fund_promise": 0.29,
        },
    }


def load_dataset() -> Dict[str, Any]:
    try:
        with open(DATASET_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default_dataset()


def save_dataset(data: Dict[str, Any]) -> None:
    data.setdefault("metadata", {})
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(DATASET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_settlement(data: Dict[str, Any], sett: Dict[str, Any]) -> bool:
    settlement_id = sett.get("settlement_id")
    if not settlement_id:
        return False
    if any(s.get("settlement_id") == settlement_id for s in data["settlements"]):
        return False
    data["settlements"].append(sett)
    save_dataset(data)
    print(f"✅ New no-proof settlement ingested: {sett.get('title', settlement_id)}")
    return True


def get_claim(data: Dict[str, Any], claim_id: str) -> Optional[Dict[str, Any]]:
    return next((c for c in data["claims"] if c.get("claim_id") == claim_id), None)


def get_settlement(data: Dict[str, Any], settlement_id: str) -> Optional[Dict[str, Any]]:
    return next(
        (s for s in data["settlements"] if s.get("settlement_id") == settlement_id),
        None,
    )


def process_claim_mcp(data: Dict[str, Any], claim_id: str) -> Dict[str, Any]:
    claim = get_claim(data, claim_id)
    if not claim:
        raise ValueError(f"Unknown claim_id: {claim_id}")
    if not claim.get("consent_received"):
        raise ValueError("Explicit consent required!")

    sett = get_settlement(data, claim["settlement_id"])
    if not sett:
        raise ValueError(
            f"Unknown settlement_id: {claim.get('settlement_id')} for claim {claim_id}"
        )

    ingested = mcp_ingest_claims(claim["raw_user_data"])
    filled = mcp_fill_claim_with_constraints(
        ingested["raw_user_data"],
        {"rag_context": sett.get("rag_context", "")},
        sett["form_schema"],
    )
    claim["deduced_form"] = filled["deduced_answers"]
    claim["mcp_log"] = filled["mcp_log"]
    claim["status"] = "filled"
    claim["verification_status"] = "draft"
    review = mcp_submit_for_verification(claim)
    save_dataset(data)
    print(review)
    print(verify_claims_batch([claim]))
    return claim


def dashboard_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """JSON-serializable dashboard payload for the API."""
    claims_preview: List[Dict[str, Any]] = []
    for claim in data.get("claims", []):
        ensure_payout_fields(claim)
        row = {
            "claim_id": claim.get("claim_id"),
            "status": claim.get("status"),
            "verification_status": claim.get("verification_status"),
            "settlement_id": claim.get("settlement_id"),
            "payout_status": claim.get("payout_status"),
        }
        claims_preview.append(row)
    metadata = data.get("metadata", {})
    return {
        "claims": claims_preview,
        "total_settlements": len(data.get("settlements", [])),
        "total_claims": len(data.get("claims", [])),
        "last_updated": metadata.get("last_updated"),
        "war_chest_alloc": metadata.get("war_chest_alloc"),
        "w_fund_promise": metadata.get("w_fund_promise"),
    }


def view_dashboard(data: Dict[str, Any]) -> Dict[str, Any]:
    """Print a human-readable dashboard and return summary for callers/API."""
    summary = dashboard_summary(data)
    if data.get("claims"):
        df = pd.DataFrame(data["claims"])
        cols = [c for c in ["claim_id", "status", "verification_status"] if c in df.columns]
        if cols:
            print(df[cols])
    print(
        f"\n📊 Total settlements: {summary['total_settlements']} | "
        f"Last scan: {summary['last_updated']}"
    )
    return summary


def ensure_settlement_placeholder(data: Dict[str, Any], settlement_id: str) -> None:
    """Ensure signup targets reference a settlement row in the dataset."""
    if get_settlement(data, settlement_id):
        return
    data["settlements"].append(
        {
            "settlement_id": settlement_id,
            "title": "Pending settlement match",
            "deadline": "TBD",
            "claim_url": "",
            "eligibility_summary": "Awaiting hunter match to a live settlement",
            "is_no_proof": True,
            "form_schema": {
                "full_name": {"type": "string", "required": True},
                "email": {"type": "string", "required": True},
            },
            "rag_context": "",
        }
    )


def register_web_signup(
    data: Dict[str, Any],
    *,
    name: str,
    email: str,
    raw_user_data: str,
    settlement_id: str = "auto_ingest",
    phone: str = "",
    w_fund_promise: bool = False,
) -> Dict[str, Any]:
    """Append a consented claimant from the web signup form."""
    ensure_settlement_placeholder(data, settlement_id)
    claim_id = f"web_{uuid.uuid4().hex[:12]}"
    claim = {
        "claim_id": claim_id,
        "settlement_id": settlement_id,
        "claimant_id": email.strip().lower(),
        "claimant_name": name.strip(),
        "phone": phone.strip(),
        "status": "eligible_pending_fill",
        "consent_received": True,
        "raw_user_data": raw_user_data.strip() or "No specific claim details provided",
        "w_fund_promise": w_fund_promise,
        "deduced_form": {},
        "mcp_log": ["Web signup – consent logged"],
        "verification_status": "draft",
        **default_payout_fields(),
    }
    data["claims"].append(claim)
    save_dataset(data)
    return claim
