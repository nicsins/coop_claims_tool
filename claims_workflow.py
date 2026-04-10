import json
from datetime import datetime
import pandas as pd
from mcp_claim_logic import mcp_ingest_claims, mcp_fill_claim_with_constraints, mcp_submit_for_verification, verify_claims_batch

DATASET_FILE = 'claims_dataset.json'

def load_dataset():
    try:
        with open(DATASET_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"settlements": [], "claims": [], "metadata": {"last_updated": datetime.now().isoformat(), "total_submitted": 0, "war_chest_alloc": 0.20, "w_fund_promise": 0.29}}

def save_dataset(data):
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    with open(DATASET_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_settlement(data, sett):
    if not any(s["settlement_id"] == sett["settlement_id"] for s in data["settlements"]):
        data["settlements"].append(sett)
        save_dataset(data)
        print(f"✅ New no-proof settlement ingested: {sett['title']}")

def process_claim_mcp(data, claim_id: str):
    claim = next((c for c in data["claims"] if c["claim_id"] == claim_id), None)
    if not claim or not claim.get("consent_received"):
        raise ValueError("Explicit consent required!")
    sett = next(s for s in data["settlements"] if s["settlement_id"] == claim["settlement_id"])
    ingested = mcp_ingest_claims(claim["raw_user_data"])
    filled = mcp_fill_claim_with_constraints(ingested["raw_user_data"], {"rag_context": sett.get("rag_context", "")}, sett["form_schema"])
    claim["deduced_form"] = filled["deduced_answers"]
    claim["mcp_log"] = filled["mcp_log"]
    claim["status"] = "filled"
    claim["verification_status"] = "draft"
    review = mcp_submit_for_verification(claim)
    save_dataset(data)
    print(review)
    print(verify_claims_batch([claim]))
    return claim

def view_dashboard(data):
    if data["claims"]:
        df = pd.DataFrame(data["claims"])
        print(df[["claim_id", "status", "verification_status"]])
    print(f"\n📊 Total settlements: {len(data['settlements'])} | Last scan: {data['metadata']['last_updated']}")
