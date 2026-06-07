# Maintenance and security agents

Yes — you should run **dedicated agents** (human or Paperclip) for **reliability** and **security**, separate from the “hunter/filler” pipeline agents. The repo’s `paperclip-org.yaml` now includes:

| Agent | Role |
|--------|------|
| **SecurityGuardian** | API exposure, secrets, CORS, dependency/CVE review, PII in logs |
| **ReliabilityWatchdog** | Health checks, pytest/CI, scraper failures, consent rules, deadlines |

## Why split these from CEO/Hunter/Processor?

- **Hunter/Processor** optimize throughput (more claims filed).
- **Security** must be allowed to **block** unsafe deploys (open API, missing API key on a public host).
- **Reliability** owns **regression tests** and operational checks without conflicting with “ship more claims.”

## Minimum operational cadence

1. **On every code change:** `python3 -m pytest` and flake8 (see `.github/workflows/python-app.yml`).
2. **Before exposing the API beyond localhost:** set `CLAIMS_API_KEY` in `.env` and verify POST routes return 401 without the header.
3. **Weekly:** review `pip audit` or Dependabot for `requirements.txt`.
4. **Before processing real PII:** keep `claims_dataset.json` local, gitignored copies for prod data, and restrict file permissions (`chmod 600`).

## Wiring in Paperclip

1. Start the bridge: `python3 api_server.py` (loopback by default).
2. Point tools at `tools.py` with `CLAIMS_API_KEY` if configured.
3. Assign **SecurityGuardian** and **ReliabilityWatchdog** on a schedule (e.g. daily) independent of OliviaScraper.

## Cursor Cloud agents

In Cursor, you can mirror the same split with two Cloud Agent rules or skills:

- **Security review** — PRs touching `api_server.py`, `security.py`, `index.html`, or env docs.
- **Reliability** — PRs touching workflow/scraper/tests; must run pytest before merge.

See `.env.example` for all security-related environment variables.
