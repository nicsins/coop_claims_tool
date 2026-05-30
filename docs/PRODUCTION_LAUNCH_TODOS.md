# Production launch todos & tweaks

**Product:** Co-op Claims / no-proof class-action proxy  
**Target domain:** [no-proof-claims.com](https://no-proof-claims.com)  
**Purpose:** Working checklist for production deployment, Stripe money flow, and a stakeholder review (“take it to the boys”) before go-live.

**Repo status today:** Flask API + static `index.html` + JSON dataset. **No Stripe, no production hosting, no payout automation yet.** Treat sections below as the build plan.

---

## How to use this doc

- [ ] = not started  
- [~] = in progress  
- [x] = done (date / owner in parentheses)

Add owner names (`@nic`, etc.) and dates as you go. Link PRs next to items when work lands in GitHub.

---

## 0. Stakeholder prep (“take it to the boys”)

Bring this doc + [MAINTENANCE_AGENTS.md](./MAINTENANCE_AGENTS.md) to the review meeting.

### Decisions to lock in the room

| # | Decision | Options / notes | Owner | Done |
|---|----------|-----------------|-------|------|
| 0.1 | **Legal entity** receiving fees & signing Stripe | LLC name, EIN, business address | | [ ] |
| 0.2 | **Money model** (see §4) | % on payout vs flat signup fee vs hybrid | | [ ] |
| 0.3 | **Split math** (fix marketing copy) | Code/metadata: **51% claimant / 20% war chest / 29% W Fund** (of *net payout*). UI currently says “71% to you” in places — **incorrect**; align all copy. | | [ ] |
| 0.4 | **Who moves money** | Co-op receives settlement check then distributes vs claimants paid direct by administrator | | [ ] |
| 0.5 | **KYC / identity** for claimants | Stripe Connect onboarding required before first payout? | | [ ] |
| 0.6 | **Hosting vendor** | Render / Fly / Railway / VPS (recommend managed: Render web + static) | | [ ] |
| 0.7 | **Support & disputes** | Email, refund policy, chargeback owner | | [ ] |

### Demo script for the meeting

1. Local: `./setup.sh` → `python3 api_server.py` → `python3 -m http.server 8080` → signup form → `GET /dashboard`.
2. Walk through consent checkbox + proxy language (lawyer review item).
3. Show empty Stripe Dashboard (test mode) and proposed payout flow diagram (§4).
4. List **blockers** from §8 — agree what ships in v1 vs v2.

---

## 1. Domain & DNS — no-proof-claims.com

| # | Task | Notes | Done |
|---|------|-------|------|
| 1.1 | Register or confirm domain registrar access | no-proof-claims.com | [ ] |
| 1.2 | Choose apex vs `www` canonical | e.g. `www` → apex redirect | [ ] |
| 1.3 | DNS to hosting | A/AAAA or CNAME per host (Render custom domain docs) | [ ] |
| 1.4 | TLS certificate | Auto via host (Let’s Encrypt) | [ ] |
| 1.5 | Email DNS (optional) | SPF/DKIM for `support@no-proof-claims.com` (SendGrid/Twilio Email later) | [ ] |
| 1.6 | Staging subdomain | e.g. `staging.no-proof-claims.com` for pre-prod | [ ] |

---

## 2. Production architecture (recommended)

```text
                    ┌─────────────────────────────┐
  Browser ─────────►│  CDN / static site          │
  no-proof-claims   │  index.html (+ built assets) │
                    └─────────────┬───────────────┘
                                  │ HTTPS
                    ┌─────────────▼───────────────┐
                    │  api.no-proof-claims.com    │
                    │  Flask (api_server.py)      │
                    │  + Postgres (future)        │
                    └─────────────┬───────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
   claims DB (not JSON)     Stripe API              Scraper worker
   + encrypted PII          Connect + webhooks       (scheduled job)
```

### Tweaks before production (codebase)

| # | Tweak | Why | Done |
|---|-------|-----|------|
| 2.1 | Replace `claims_dataset.json` with **Postgres** (or SQLite + backup) | JSON file is not safe for multi-user prod | [ ] |
| 2.2 | Move API to **gunicorn** + process manager | `app.run()` is dev-only | [ ] |
| 2.3 | Set `CLAIMS_API_KEY` on all mutating routes | Already supported; enforce in prod | [ ] |
| 2.4 | Point `index.html` at `https://api.no-proof-claims.com` | `window.CLAIMS_API_BASE` or build-time env | [ ] |
| 2.5 | Remove or gate **test_001** auto-seed in `main.py` for prod | Avoid fake claimant in prod DB | [ ] |
| 2.6 | Add structured logging + error tracking | Sentry / Datadog / CloudWatch | [ ] |
| 2.7 | Backup job for DB + audit log | Daily, encrypted | [ ] |
| 2.8 | Rate limit `/signup` and `/process_mcp` | Slow abuse / bot signups | [ ] |

---

## 3. Deployment checklist

### 3.1 Repository & CI

| # | Task | Done |
|---|------|------|
| 3.1.1 | Merge reliability/security PR (tests, API hardening) | [ ] |
| 3.1.2 | CI green: `flake8` + `pytest` on `main` | [ ] |
| 3.1.3 | Add deploy workflow (build → staging → manual prod) | [ ] |
| 3.1.4 | Pin Python version in CI and prod (3.10 or 3.12) | [ ] |

### 3.2 Backend API service

| # | Task | Done |
|---|------|------|
| 3.2.1 | Create production service (e.g. Render **Web Service**) | [ ] |
| 3.2.2 | Start command: `gunicorn -b 0.0.0.0:$PORT api_server:app` | [ ] |
| 3.2.3 | Health check path: `/health` | [ ] |
| 3.2.4 | Env vars from §6 (secrets in dashboard, not git) | [ ] |
| 3.2.5 | Custom domain `api.no-proof-claims.com` | [ ] |
| 3.2.6 | Scheduler: separate **worker** or cron for `main.py` daily scrape | [ ] |

### 3.3 Frontend (marketing + signup)

| # | Task | Done |
|---|------|------|
| 3.3.1 | Static site deploy for apex/`www` | [ ] |
| 3.3.2 | Inject production API URL into form script | [ ] |
| 3.3.3 | Privacy policy + Terms pages (linked in footer) | [ ] |
| 3.3.4 | Cookie/consent banner if analytics added | [ ] |

### 3.4 Post-deploy smoke tests

| # | Test | Done |
|---|------|------|
| 3.4.1 | `curl https://api.no-proof-claims.com/health` | [ ] |
| 3.4.2 | Signup from live site → claim appears in dashboard | [ ] |
| 3.4.3 | POST without API key → **401** | [ ] |
| 3.4.4 | Stripe webhook test event in Dashboard → app logs/handlers | [ ] |

---

## 4. Stripe — connect payments & fees

**Not implemented in repo yet.** Recommended approach for “pay users + take our cut”: **[Stripe Connect](https://stripe.com/docs/connect)** (platform account + connected accounts for claimants).

### 4.1 Account setup

| # | Task | Done |
|---|------|------|
| 4.1.1 | Create **Stripe account** (live + test) for legal entity from §0.1 | [ ] |
| 4.1.2 | Complete business verification (KYC, bank account for platform) | [ ] |
| 4.1.3 | Enable **Connect** | [ ] |
| 4.1.4 | Choose connected account type | **Express** (faster onboarding) vs **Custom** (more control) — decide in stakeholder meeting | [ ] |
| 4.1.5 | Create restricted API keys for prod (`sk_live_...`) — never commit | [ ] |
| 4.1.6 | Register webhook endpoint `https://api.no-proof-claims.com/webhooks/stripe` | [ ] |

### 4.2 Money flow (proposed — confirm with counsel)

**Assumption:** Settlement administrator pays the **platform balance** (or claimant directly; if direct, Stripe is only for **platform fees**).

| Step | What happens | Stripe primitive |
|------|----------------|------------------|
| A | Claimant signs up + consents on no-proof-claims.com | Your DB only |
| B | Claim filed & approved by class admin | External (settlement site) |
| C | Payout received by platform bank / Stripe balance | `PaymentIntent` or off-Stripe ACH → reconcile manually in v1 |
| D | Split recorded: 51% / 20% / 29% of **net** | App logic + `metadata` on claim |
| E | Transfer claimant share | Connect **`Transfer`** to connected account |
| F | Platform keeps 20% + 29% | **`application_fee`** on charge, or internal ledger + transfer to platform balance |

**v1 simplification (stakeholder-friendly):**

- Track payouts in DB; pay claimants manually via Stripe Dashboard or ACH while building automation.
- Automate only **optional signup/service fee** via **Checkout** until settlement inflows are clear.

### 4.3 Code tasks (new modules)

| # | Task | Done |
|---|------|------|
| 4.3.1 | Add `stripe` to `requirements.txt` | [ ] |
| 4.3.2 | `payments/stripe_client.py` — init from `STRIPE_SECRET_KEY` | [ ] |
| 4.3.3 | `POST /connect/onboard` — create Connect account + Account Link URL | [ ] |
| 4.3.4 | `POST /webhooks/stripe` — verify signature (`STRIPE_WEBHOOK_SECRET`) | [ ] |
| 4.3.5 | Extend claim model: `stripe_account_id`, `payout_status`, `gross_cents`, `splits`, `stripe_transfer_id` | [ ] |
| 4.3.6 | `POST /payouts/allocate` (admin) — given `claim_id` + `gross_cents`, compute splits & create Transfer | [ ] |
| 4.3.7 | Idempotency keys on all payout API calls | [ ] |
| 4.3.8 | Admin audit log (who triggered payout) | [ ] |

### 4.4 Webhook events to handle

| Event | Action |
|-------|--------|
| `account.updated` | Mark claimant Connect onboarding complete |
| `transfer.created` / `transfer.paid` | Update claim `payout_status` |
| `transfer.failed` | Alert ops; hold retry |
| `charge.dispute.created` | Ops playbook |

### 4.5 Fee & split configuration (env)

```bash
# .env production (examples — align in stakeholder meeting)
WAR_CHEST_RATE=0.20
W_FUND_RATE=0.29
CLAIMANT_RATE=0.51
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_CONNECT_CLIENT_ID=ca_...
```

**Tweak:** Store rates in DB `metadata` or config table so you can change without redeploy (with audit trail).

### 4.6 User-facing payment UX

| # | Task | Done |
|---|------|------|
| 4.6.1 | After signup, redirect to **Connect onboarding** if payouts enabled | [ ] |
| 4.6.2 | Dashboard: payout status (pending / onboarding / paid) | [ ] |
| 4.6.3 | Email when transfer completes (SendGrid/Twilio) | [ ] |
| 4.6.4 | Clear statement: “We deduct 20% war chest + 29% W Fund from your settlement payout when you opted in” | [ ] |

### 4.7 Compliance & ops (non-code)

| # | Task | Done |
|---|------|------|
| 4.7.1 | Lawyer review: proxy consent + fee disclosure + money transmission rules | [ ] |
| 4.7.2 | Stripe **Statement descriptor** recognizable to users | [ ] |
| 4.7.3 | 1099 / tax reporting plan for claimants (US) | [ ] |
| 4.7.4 | Refund/chargeback policy documented | [ ] |
| 4.7.5 | Reconcile Stripe balance ↔ bank ↔ internal ledger monthly | [ ] |

---

## 5. Managing payments to users & receiving platform fees

### 5.1 Internal ledger (recommended)

Track every dollar in app DB, not only in Stripe:

| Field | Purpose |
|-------|---------|
| `claim_id` | Link to claimant |
| `gross_payout_cents` | What settlement paid in |
| `claimant_cents` | 51% |
| `war_chest_cents` | 20% |
| `w_fund_cents` | 29% (only if `w_fund_promise: true`?) |
| `platform_fee_cents` | May equal war_chest + w_fund |
| `stripe_transfer_id` | Outbound to claimant |
| `status` | `pending` → `onboarding` → `transferred` → `failed` |

**Tweak to decide with stakeholders:** If user did **not** promise 29% W Fund, does their share become 51% + 29% = 80%? Document rule in code comments + Terms.

### 5.2 Roles

| Role | Can do |
|------|--------|
| Claimant | Onboard Connect, view own payout status |
| Ops / Finance | Trigger allocation, view ledger, export CSV |
| Security agent (see paperclip) | Block payout if API key missing / fraud flag |

### 5.3 Manual vs automated phases

| Phase | Claimant payout | Platform fee |
|-------|-----------------|--------------|
| **Phase 1** | Manual ACH / Stripe Dashboard | Manual transfer to business bank |
| **Phase 2** | Connect Transfer API | `application_fee` or ledger + internal transfer |
| **Phase 3** | Fully automated on webhook from settlement (if ever available) | Same |

---

## 6. Production environment variables

Copy from `.env.example` and extend:

| Variable | Required prod | Notes |
|----------|---------------|-------|
| `CLAIMS_API_KEY` | Yes | Rotate quarterly |
| `FLASK_HOST` | `0.0.0.0` behind reverse proxy | |
| `DATABASE_URL` | Yes (when DB added) | Postgres |
| `CLAIMS_CORS_ORIGINS` | `https://no-proof-claims.com,https://www.no-proof-claims.com` | |
| `STRIPE_SECRET_KEY` | Yes | Live key in prod only |
| `STRIPE_WEBHOOK_SECRET` | Yes | Per endpoint |
| `STRIPE_CONNECT_CLIENT_ID` | If Connect | |
| `WAR_CHEST_RATE` / `W_FUND_RATE` / `CLAIMANT_RATE` | Yes | Match legal docs |

---

## 7. Security & maintenance (production)

| # | Task | Done |
|---|------|------|
| 7.1 | Run **SecurityGuardian** checklist from `paperclip-org.yaml` before go-live | [ ] |
| 7.2 | Run **ReliabilityWatchdog**: `/health`, pytest, scraper logs | [ ] |
| 7.3 | Encrypt PII at rest (DB column-level or disk) | [ ] |
| 7.4 | `chmod 600` / IAM for secrets; no PII in application logs | [ ] |
| 7.5 | Dependabot or `pip audit` on schedule | [ ] |
| 7.6 | Incident runbook (API down, Stripe webhook down, data leak) | [ ] |

---

## 8. Known gaps / final issues for the boys

| Issue | Severity | Proposed fix |
|-------|----------|--------------|
| Payout split UI says “71% to you” | High (trust) | Change to **51%**; footnote 20% + 29% |
| No Stripe code | Blocker for paid launch | §4 |
| JSON file database | Blocker for scale | §2.1 |
| Settlement $ may not hit Stripe | High | Phase 1 manual reconciliation |
| `auto_ingest` settlement placeholder | Medium | Hunter matches real `settlement_id` before fill |
| MCP fill is stub (`DEDUCED_FROM_...`) | High for product | Integrate real Agent Zero / forms |
| Legal proxy + fee consent | Blocker | Attorney sign-off |
| No admin UI for Finance | Medium | Retool / internal Flask admin |
| Scraper depends on third-party HTML | Medium | Monitoring + fallbacks |

---

## 9. Suggested sprint order

1. **Week A — Stakeholder + legal:** §0, §4.7, fix copy (§0.3).  
2. **Week B — Infra:** §1, §3, §2.1–2.3, §6.  
3. **Week C — Stripe Phase 1:** §4.1–4.3, manual payouts §5.3.  
4. **Week D — Hardening:** §7, §3.4, §4.4–4.6 automation as scoped.

---

## 10. Quick links

| Resource | URL |
|----------|-----|
| Stripe Connect overview | https://stripe.com/docs/connect |
| Connect separate charges and transfers | https://stripe.com/docs/connect/separate-charges-and-transfers |
| Webhooks | https://stripe.com/docs/webhooks |
| Render custom domains | https://render.com/docs/custom-domains |
| Repo maintenance agents | [MAINTENANCE_AGENTS.md](./MAINTENANCE_AGENTS.md) |
| Env template | `../.env.example` |

---

*Last updated: 2026-05-30 — regenerate sections as implementation lands.*
