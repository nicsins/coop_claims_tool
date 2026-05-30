# AGENTS.md

## Cursor Cloud specific instructions

### Services (dev)

| Service | Port | Command |
|--------|------|---------|
| Flask API | 5000 | `python3 api_server.py` |
| Scheduler | — | `python3 main.py` |
| Static UI | 8080 | `python3 -m http.server 8080` → `/index.html` |

Setup: `./setup.sh` or `pip install -r requirements.txt` plus `flake8` / `pytest`.

### Security defaults

- API binds to **127.0.0.1** unless `FLASK_HOST` is set.
- Set **`CLAIMS_API_KEY`** before exposing POST endpoints (`/scrape`, `/signup`, `/process_mcp`). Clients send `X-API-Key`.
- `GET /dashboard` and `GET /health` stay open for local monitoring; lock down at a reverse proxy in production.
- Copy `.env.example` → `.env` for local config.

### Lint / test

```bash
python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
python3 -m pytest -v
```

### Stripe payouts (mock by default)

- Module: `payments/` — Connect onboarding, split math, transfers, webhooks.
- Mock mode: `STRIPE_MOCK_MODE=true` or leave `STRIPE_SECRET_KEY` empty.
- Admin routes: `/connect/onboard`, `/payouts/allocate`, `/payouts/transfer` (use `X-API-Key` when `CLAIMS_API_KEY` is set).
- Launch checklist: `docs/PRODUCTION_LAUNCH_TODOS.md`.

### Maintenance agents

See `docs/MAINTENANCE_AGENTS.md` and `paperclip-org.yaml` roles **SecurityGuardian** and **ReliabilityWatchdog**.
