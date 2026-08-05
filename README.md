# SE Toolkit

A set of tools built to demonstrate practical Solutions Engineering workflows —
pre-sales deal support, post-sale customer health, and everywhere in between.
Runs as a single Streamlit app with multiple pages, all in **Demo Mode by
default — no API key, no cost, no setup required.**

## Tools included

### 📄 RFP Automation Tool
AI-powered RFP response generator using Claude, grounded in a retrieval layer
over past RFP answers — cuts down the hours SEs spend drafting consistent,
accurate RFP responses under deadline pressure.

- Single-question and bulk CSV modes
- TF-IDF retrieval over a knowledge base of past answers, so drafts stay
  consistent instead of the model improvising
- Runs in Demo Mode (no key needed) or live mode with a Claude API key

### 📡 API Monitoring Dashboard
A lightweight integration-health dashboard — the kind of view an SE hands to a
customer post-deployment so they can self-serve status checks instead of
filing support tickets.

- Live-style status, latency trends, and an incident log across 4 simulated
  integrations
- **Endpoint-level detail** — each service breaks down into its individual
  endpoints (status, latency, uptime), not just a single aggregate number
- **Customer Report tab** — a plain-language summary suitable to hand a
  customer directly, plus a **downloadable PDF report** (generated with
  reportlab, including an embedded latency chart and executive summary)
- Configurable alert threshold, refreshable simulated data ticks
- Runs entirely on simulated data — no external services required
- A distinct visual identity (dark control-room theme, signal-colored status
  accents, monospace data figures) shared across the whole toolkit via a
  common `theme.py` module

## Tech stack

- **Streamlit** — multi-page app UI
- **Claude (Anthropic API)** — RFP response generation (optional, live mode only)
- **scikit-learn (TF-IDF)** — retrieval layer for the RFP tool
- **numpy / pandas** — simulated monitoring data and bulk processing
- **reportlab / matplotlib** — PDF customer report generation with embedded charts

## Running locally

```bash
git clone <your-repo-url>
cd rfp-automation-tool
pip install -r requirements.txt
streamlit run app.py
```

Opens a home page with links to both tools. Everything runs in Demo Mode out
of the box — no setup needed to explore either tool.

To use live Claude generation in the RFP tool instead of demo-mode retrieval,
toggle Demo Mode off on that page and add a key:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with your real Anthropic API key
```

## Deploying (free, ~5 minutes)

1. Push this repo to GitHub (public repo is fine — `secrets.toml` is
   gitignored, so your API key never gets committed)
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. Click **New app**, select this repo and `app.py` as the entry point
4. (Optional, only if using live Claude generation) Under **Advanced settings
   → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-real-key"
   ```
5. Deploy — you'll get a public URL like `your-app-name.streamlit.app`

**Note:** free-tier apps sleep after ~12 hours of no traffic. The first
visitor after a sleep period waits ~20-30 seconds for it to wake up — this is
normal, not a bug.

## Sample data

- `knowledge_base.json` ships with 5 example RFP Q&A pairs (SSO, uptime SLA,
  SOC 2, data residency, support) so the RFP tool's demo works out of the box
- The monitoring dashboard generates its own simulated data on load, with a
  refresh button to simulate a new data tick

CSV format for bulk knowledge base upload (RFP tool):
```csv
question,answer
"Do you support SSO?","Yes, via SAML 2.0 and OAuth 2.0..."
```

CSV format for bulk RFP question generation:
```csv
question,context
"What is your data retention policy?","Customer is in healthcare, cares about HIPAA"
```

## Why this project

Built to demonstrate the kind of technical + business-facing tooling a
Solutions Engineer builds for their own team: tools that save real hours, stay
grounded in facts instead of hallucinating, and can be handed to a
non-technical teammate — or a customer — without them touching code.

---
Built by Srabana Guha · Staff SE, 12+ years at Uber, Walmart Connect, and Hulu
