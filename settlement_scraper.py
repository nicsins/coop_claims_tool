import logging
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "CoopClaimsBot/1.0 (+https://github.com/nicsins/coop_claims_tool)"
KEYWORDS = ("no proof", "privacy", "data breach", "pixel", "no receipt")


def _extract_claim_url(card, base_url: str) -> str:
    link = card.find("a", href=True)
    if not link:
        return base_url
    href = link["href"]
    if href.startswith("http"):
        return href
    return urljoin(base_url, href)


def scrape_no_proof_settlements() -> List[Dict[str, Any]]:
    settlements: List[Dict[str, Any]] = []
    urls = [
        "https://topclassactions.com/category/lawsuit-settlements/open-lawsuit-settlements/",
        "https://www.claimdepot.com/settlements",
    ]
    for url in urls:
        try:
            response = requests.get(
                url, timeout=10, headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for card in soup.find_all(
                ["div", "article"],
                class_=lambda x: x and ("settlement" in x.lower() or "claim" in x.lower()),
            ):
                title_el = card.find("h2") or card.find("h3") or card.find("a")
                title = title_el.get_text(strip=True) if title_el else "Untitled"
                if not any(kw in title.lower() for kw in KEYWORDS):
                    continue
                settlements.append(
                    {
                        "settlement_id": f"auto_{len(settlements)}",
                        "title": title,
                        "deadline": "TBD",
                        "claim_url": _extract_claim_url(card, url),
                        "eligibility_summary": "NO-PROOF candidate – check site",
                        "is_no_proof": True,
                        "form_schema": {
                            "full_name": {"type": "string", "required": True},
                            "email": {"type": "string", "required": True},
                        },
                        "rag_context": "Olivia.claims-style no-proof or privacy breach",
                    }
                )
        except requests.RequestException as exc:
            logger.warning("Scrape failed for %s: %s", url, exc)
    return settlements
