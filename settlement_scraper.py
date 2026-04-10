import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_no_proof_settlements():
    settlements = []
    urls = [
        "https://topclassactions.com/category/lawsuit-settlements/open-lawsuit-settlements/",
        "https://www.claimdepot.com/settlements"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "CoopClaimsBot/1.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            # Generic parser – looks for settlement cards with "no proof" or privacy/breach keywords
            for card in soup.find_all(["div", "article"], class_=lambda x: x and ("settlement" in x.lower() or "claim" in x.lower())):
                title = card.find("h2") or card.find("h3") or card.find("a")
                title = title.get_text(strip=True) if title else "Untitled"
                if any(kw in title.lower() for kw in ["no proof", "privacy", "data breach", "pixel", "no receipt"]):
                    settlements.append({
                        "settlement_id": f"auto_{len(settlements)}",
                        "title": title,
                        "deadline": "TBD",  # parse dates in future version
                        "claim_url": card.find("a")["href"] if card.find("a") else url,
                        "eligibility_summary": "NO-PROOF candidate – check site",
                        "is_no_proof": True,
                        "form_schema": {"full_name": {"type": "string", "required": True}, "email": {"type": "string", "required": True}},
                        "rag_context": "Olivia.claims-style no-proof or privacy breach"
                    })
        except:
            pass
    return settlements
