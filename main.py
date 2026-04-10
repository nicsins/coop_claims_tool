from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import json
from settlement_scraper import scrape_no_proof_settlements
from claims_workflow import load_dataset, save_dataset, add_settlement, process_claim_mcp, view_dashboard

def daily_job():
    print(f"\n🔄 [{datetime.now()}] Running daily no-proof scan...")
    data = load_dataset()
    new_ones = scrape_no_proof_settlements()
    for s in new_ones:
        add_settlement(data, s)
    # Example: auto-process first test claimant if exists
    test_claim = next((c for c in data["claims"] if c.get("claim_id") == "test_001"), None)
    if test_claim and test_claim["status"] == "eligible_pending_fill":
        process_claim_mcp(data, "test_001")
    view_dashboard(data)
    print("✅ Scan complete – waiting 24h...")

if __name__ == "__main__":
    data = load_dataset()
    # Add a test claimant (replace with your real ones)
    if not any(c.get("claim_id") == "test_001" for c in data["claims"]):
        data["claims"].append({
            "claim_id": "test_001",
            "settlement_id": "inova_health_privacy_31m",
            "claimant_id": "your_test_user",
            "status": "eligible_pending_fill",
            "consent_received": True,
            "raw_user_data": "I visited Inova website in 2023 with MyChart account",
            "deduced_form": {},
            "mcp_log": [],
            "verification_status": "draft"
        })
        save_dataset(data)
    print("🚀 Coop Claims Tool STARTED – continuous no-proof hunter + MCP proxy filler")
    print("Press Ctrl+C to stop")
    scheduler = BlockingScheduler()
    scheduler.add_job(daily_job, 'interval', hours=24, next_run_time=datetime.now())
    scheduler.start()
