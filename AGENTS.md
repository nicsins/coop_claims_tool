# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is

Single Python app: **Co-op Claims Assistant** — scrapes no-proof class-action settlements, runs MCP-style claim fill stubs, and exposes an optional Flask API for Paperclip integration. Data lives in `claims_dataset.json`. See `README.md` for product overview.

### Services (dev)

| Service | Port | Start command | Notes |
|--------|------|---------------|--------|
| **Claim scheduler** | — | `python3 main.py` | Blocking 24h loop; runs scrape + optional `test_001` processing on start. Needs network for live scraper. |
| **Flask API** | 5000 | `python3 api_server.py` | **Flask is not in `requirements.txt`** — install with `pip install flask` (included in cloud update script). `GET /dashboard` returns JSON `null` because `view_dashboard()` only prints; use `POST /process_mcp` with `{"claim_id":"..."}` for real API output. |
| **Static signup UI** | 8080 | `python3 -m http.server 8080` then open `/index.html` | No backend wiring; form logs to browser console only. |

Use tmux for long-running processes (e.g. `flask-api`, `static-ui` sessions).

### Lint / test / build

From repo root (`/workspace`):

- **Lint (CI parity):** `python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics` then `python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`
- **Tests:** `python3 -m pytest` — **no test files in repo**; pytest exits **5** (“no tests collected”). GitHub Actions runs the same command; treat as known gap until tests are added.
- **Build:** none (interpreted Python).

Install dev tools: `pip install -r requirements.txt` plus `flask`, `flake8`, and `pytest` (update script installs these).

### Minimal “hello world” (core flow, offline)

```bash
cd /workspace
python3 -c "
from claims_workflow import load_dataset, save_dataset, process_claim_mcp
data = load_dataset()
# ensure test_001 exists with consent + settlement_id inova_health_privacy_31m
process_claim_mcp(data, 'test_001')
"
```

Expect `status: filled` and deduced form fields in `claims_dataset.json`.

### Gotchas

- `README.md` references `./setup.sh` — **file does not exist**; use `pip install -r requirements.txt` instead.
- `pip` user scripts install under `~/.local/bin` — add `export PATH="$HOME/.local/bin:$PATH"` if `flake8`/`flask` are not found.
- Optional: Paperclip (`npx paperclipai`) and live scraping require network and external setup; not required for local claim-processing dev.
