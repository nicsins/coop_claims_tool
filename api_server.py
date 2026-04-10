from flask import Flask, request, jsonify
from claims_workflow import load_dataset, process_claim_mcp, view_dashboard
# ... import your scraper too

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    # run your settlement_scraper
    return jsonify({"status": "new_settlements_ingested"})

@app.route("/process_mcp", methods=["POST"])
def process():
    data = load_dataset()
    claim_id = request.json["claim_id"]
    result = process_claim_mcp(data, claim_id)
    return jsonify(result)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify(view_dashboard(load_dataset()))

if __name__ == "__main__":
    app.run(port=5000)
