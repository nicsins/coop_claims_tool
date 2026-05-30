from claims_workflow import (
    dashboard_summary,
    load_dataset,
    process_claim_mcp,
    register_web_signup,
)


def test_dashboard_summary_returns_claims(dataset_env):
    data = load_dataset()
    summary = dashboard_summary(data)
    assert "total_settlements" in summary
    assert summary["total_settlements"] >= 1


def test_process_claim_mcp_requires_consent(dataset_env):
    data = load_dataset()
    data["claims"].append(
        {
            "claim_id": "no_consent",
            "settlement_id": "inova_health_privacy_31m",
            "consent_received": False,
            "raw_user_data": "test",
        }
    )
    try:
        process_claim_mcp(data, "no_consent")
        raised = False
    except ValueError as exc:
        raised = True
        assert "consent" in str(exc).lower()
    assert raised


def test_process_claim_mcp_fills_test_claim(dataset_env):
    data = load_dataset()
    data["claims"] = [
        c for c in data["claims"] if c.get("claim_id") != "pytest_001"
    ]
    data["claims"].append(
        {
            "claim_id": "pytest_001",
            "settlement_id": "inova_health_privacy_31m",
            "claimant_id": "pytest@example.com",
            "status": "eligible_pending_fill",
            "consent_received": True,
            "raw_user_data": "Visited Inova with MyChart",
            "deduced_form": {},
            "mcp_log": [],
            "verification_status": "draft",
        }
    )
    from claims_workflow import save_dataset

    save_dataset(data)
    result = process_claim_mcp(load_dataset(), "pytest_001")
    assert result["status"] == "filled"
    assert result["deduced_form"]


def test_register_web_signup(dataset_env):
    data = load_dataset()
    before = len(data["claims"])
    claim = register_web_signup(
        data,
        name="Test User",
        email="signup@example.com",
        raw_user_data="Privacy breach victim",
        w_fund_promise=True,
    )
    assert claim["claim_id"].startswith("web_")
    assert len(load_dataset()["claims"]) == before + 1
