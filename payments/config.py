"""Payout rate configuration from environment."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SplitRates:
    claimant: float
    war_chest: float
    w_fund: float

    def validate(self) -> None:
        total = self.claimant + self.war_chest + self.w_fund
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Split rates must sum to 1.0, got {total}")


def _rate(name: str, default: str) -> float:
    return float(os.environ.get(name, default))


def get_split_rates(*, w_fund_promise: bool) -> SplitRates:
    """
    Return split rates for a payout.

    With W Fund promise: claimant / war chest / W Fund from env (default 51/20/29).
    Without promise: claimant receives war_chest + w_fund share (default 80/20/0).
    """
    war = _rate("WAR_CHEST_RATE", "0.20")
    w_fund = _rate("W_FUND_RATE", "0.29")
    claimant = _rate("CLAIMANT_RATE", "0.51")

    if w_fund_promise:
        rates = SplitRates(claimant=claimant, war_chest=war, w_fund=w_fund)
    else:
        rates = SplitRates(claimant=claimant + w_fund, war_chest=war, w_fund=0.0)
    rates.validate()
    return rates


def stripe_connect_return_url() -> str:
    return os.environ.get(
        "STRIPE_CONNECT_RETURN_URL",
        "https://no-proof-claims.com/signup?onboarding=complete",
    )


def stripe_connect_refresh_url() -> str:
    return os.environ.get(
        "STRIPE_CONNECT_REFRESH_URL",
        "https://no-proof-claims.com/signup?onboarding=refresh",
    )
