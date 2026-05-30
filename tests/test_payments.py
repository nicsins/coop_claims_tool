import pytest

from payments.ledger import compute_splits, default_payout_fields, ensure_payout_fields
from payments.payouts import allocate_payout, execute_transfer
from payments.connect import start_connect_onboarding


def test_default_payout_fields():
    fields = default_payout_fields()
    assert fields["payout_status"] == "pending"
    assert fields["stripe_account_id"] is None


def test_compute_splits_with_w_fund_promise():
    splits = compute_splits(10_000, w_fund_promise=True)
    assert splits["gross_payout_cents"] == 10_000
    assert splits["claimant_cents"] + splits["war_chest_cents"] + splits["w_fund_cents"] == 10_000
    assert splits["war_chest_cents"] == 2000
    assert splits["w_fund_cents"] == 2900
    assert splits["claimant_cents"] == 5100


def test_compute_splits_without_w_fund_promise():
    splits = compute_splits(10_000, w_fund_promise=False)
    assert splits["w_fund_cents"] == 0
    assert splits["claimant_cents"] == 8000
    assert splits["war_chest_cents"] == 2000


def test_allocate_and_transfer_mock():
    claim = {
        "claim_id": "pay_test",
        "claimant_id": "pay@example.com",
        "w_fund_promise": True,
        **default_payout_fields(),
    }
    start_connect_onboarding(claim, email="pay@example.com")
    claim["stripe_onboarding_complete"] = True
    claim["payout_status"] = "ready"

    alloc = allocate_payout(claim, 100_00, admin_note="test settlement")
    assert alloc["payout_status"] == "allocated"
    assert claim["claimant_cents"] == 51_00

    transfer = execute_transfer(claim)
    assert transfer["payout_status"] == "transferred"
    assert claim["stripe_transfer_id"].startswith("tr_mock_")
