import os

from flask import Flask, jsonify, request

from claims_workflow import (
    add_settlement,
    dashboard_summary,
    load_dataset,
    process_claim_mcp,
    register_web_signup,
)
from security import require_api_key
from settlement_scraper import scrape_no_proof_settlements

app = Flask(__name__)

# Restrict CORS to local dev origins when the static UI runs on another port.
_ALLOWED_ORIGINS = os.environ.get(
    "CLAIMS_CORS_ORIGINS",
    "http://127.0.0.1:8080,http://localhost:8080",
).split(",")


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin and origin.strip() in [o.strip() for o in _ALLOWED_ORIGINS if o.strip()]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/scrape", methods=["POST", "OPTIONS"])
@require_api_key
def scrape():
    if request.method == "OPTIONS":
        return "", 204
    data = load_dataset()
    new_settlements = scrape_no_proof_settlements()
    ingested = 0
    for sett in new_settlements:
        if add_settlement(data, sett):
            ingested += 1
    return jsonify(
        {
            "status": "new_settlements_ingested",
            "discovered": len(new_settlements),
            "ingested": ingested,
        }
    )


@app.route("/signup", methods=["POST", "OPTIONS"])
@require_api_key
def signup():
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400
    if not body.get("consent_received"):
        return jsonify({"error": "consent_received must be true"}), 400

    data = load_dataset()
    claim = register_web_signup(
        data,
        name=name,
        email=email,
        raw_user_data=body.get("raw_user_data", ""),
        settlement_id=body.get("settlement_id", "auto_ingest"),
        phone=body.get("phone", ""),
        w_fund_promise=bool(body.get("w_fund_promise")),
    )
    return jsonify(claim), 201


@app.route("/process_mcp", methods=["POST", "OPTIONS"])
@require_api_key
def process():
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_json(silent=True) or {}
    claim_id = body.get("claim_id")
    if not claim_id:
        return jsonify({"error": "claim_id is required"}), 400
    data = load_dataset()
    try:
        result = process_claim_mcp(data, claim_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)


@app.route("/dashboard", methods=["GET"])
def dashboard():
    return jsonify(dashboard_summary(load_dataset()))


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)
