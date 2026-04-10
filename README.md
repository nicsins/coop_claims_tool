

# claims-maximizer
auto locate and file zero proof claims
# Coop Claims Tool – Continuous No-Proof Lawsuit Capital Engine
1. pip install -r requirements.txt
2. python main.py
→ Runs forever, scrapes daily, fills via your MCP/Agent Zero, logs everything.
First run processes Inova (deadline TODAY) + Panda.
Add more claimants to claims[] with "consent_received": true + raw_user_data.
cd coop_claims_tool
pip install -r requirements.txt
python main.py
# Start your Python bridge first
python api_server.py

# Then launch Paperclip (it will auto-run the org chart)
npx paperclipai run
