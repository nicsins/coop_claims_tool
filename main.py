from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from claims_workflow import (
    add_settlement,
    load_dataset,
    process_claim_mcp,
    save_dataset,
    view_dashboard,
)
from settlement_scraper import scrape_no_proof_settlements


def daily_job():
    print(f"\n🔄 [{datetime.now()}] Running daily no-proof scan...")
    data = load_dataset()
    new_ones = scrape_no_proof_settlements()
    for settlement in new_ones:
        add_settlement(data, settlement)
    data = load_dataset()
    test_claim = next(
        (c for c in data["claims"] if c.get("claim_id") == "test_001"), None
    )
    if test_claim and test_claim.get("status") == "eligible_pending_fill":
        process_claim_mcp(data, "test_001")
    view_dashboard(load_dataset())
    print("✅ Scan complete – waiting 24h...")


def ensure_test_claimant():
    data = load_dataset()
    if any(c.get("claim_id") == "test_001" for c in data["claims"]):
        return
    data["claims"].append(
        {
            "claim_id": "test_001",
            "settlement_id": "inova_health_privacy_31m",
            "claimant_id": "your_test_user",
            "status": "eligible_pending_fill",
            "consent_received": True,
            "raw_user_data": "I visited Inova website in 2023 with MyChart account",
            "deduced_form": {},
            "mcp_log": [],
            "verification_status": "draft",
        }
    )
    save_dataset(data)


if __name__ == "__main__":
    ensure_test_claimant()
    print("🚀 Coop Claims Tool STARTED – continuous no-proof hunter + MCP proxy filler")
    print("Press Ctrl+C to stop")
    scheduler = BlockingScheduler()
    scheduler.add_job(
        daily_job, "interval", hours=24, next_run_time=datetime.now()
    )
    scheduler.start()
