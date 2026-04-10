import requests
# Point these to your local claims_workflow.py or MCP server

def scrape_no_proof():
    # Calls your settlement_scraper.py
    return requests.post("http://localhost:5000/scrape").json()

def mcp_fill(claim_id):
    return requests.post("http://localhost:5000/process_mcp", json={"claim_id": claim_id}).json()

def view_dashboard():
    return requests.get("http://localhost:5000/dashboard").json()
