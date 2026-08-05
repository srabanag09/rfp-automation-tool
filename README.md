# SE Toolkit

A set of tools for common Solutions Engineering workflows: drafting RFP
responses and monitoring integration health. Runs as a single Streamlit app
with multiple pages, entirely in **Demo Mode by default — no API key, no
cost, no setup required.**

## Tools included

### 📄 RFP Automation Tool
Drafts RFP responses grounded in a retrieval layer over a knowledge base of
past answers, so drafts stay consistent instead of an LLM improvising from
scratch.

- Single-question mode and bulk CSV mode (upload many questions, get all
  responses back in one CSV)
- TF-IDF retrieval surfaces the most relevant past answers for each question
  before drafting a response
- Editable knowledge base — add entries in the UI or bulk-upload via CSV
- Runs in Demo Mode (no key needed) or live mode with a Claude API key

### 📡 API Monitoring Dashboard
A lightweight integration-health dashboard showing live-style status, latency
trends, and incidents across a set of integrations.

- Endpoint-level detail — each integration breaks down into individual
  endpoints with their own status, latency, and uptime
- Customer Report tab — a plain-language summary, plus a downloadable PDF
  report with an executive summary, comparison table, and latency chart
- Configurable alert threshold, refreshable simulated data
- Runs entirely on simulated data — no external services required

## Tech stack

- **Streamlit** — multi-page app UI
- **Claude (Anthropic API)** — RFP response generation (optional, live mode only)
- **scikit-learn (TF-IDF)** — retrieval layer for the RFP tool
- **numpy / pandas** — simulated monitoring data and bulk processing
- **reportlab / matplotlib** — PDF report generation with embedded charts

## Running locally

```bash
git clone <this-repo-url>
cd rfp-automation-tool
pip install -r requirements.txt
streamlit run app.py
```

This opens a home page linking to both tools. Everything runs in Demo Mode
out of the box — no setup needed to explore either one.

To use live Claude generation in the RFP tool instead of demo-mode retrieval,
toggle Demo Mode off on that page and add an API key:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with your real Anthropic API key
```

## Deploying (free, ~5 minutes)

1. Push this repo to GitHub (public is fine — `secrets.toml` is gitignored,
   so an API key never gets committed)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
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

## Using the RFP Automation Tool

1. Open the **RFP Automation Tool** page from the home screen
2. In the sidebar, review or expand the knowledge base (5 sample Q&A pairs
   are included) — add your own via the "Add a past RFP answer" expander or
   bulk-upload a CSV
3. **Single question:** paste a question into the text box, optionally add
   context, and click **Generate Response**
4. **Bulk mode:** switch to the "Bulk Generate" tab, upload a CSV with a
   `question` column (optional `context` column), and click **Generate All
   Responses** — download the results as a CSV when done

CSV format for bulk knowledge base upload:
```csv
question,answer
"Do you support SSO?","Yes, via SAML 2.0 and OAuth 2.0..."
```

CSV format for bulk RFP question generation:
```csv
question,context
"What is your data retention policy?","Customer is in healthcare, cares about HIPAA"
```

## Using the API Monitoring Dashboard

1. Open the **API Monitoring Dashboard** page from the home screen
2. The top row shows live-style status cards for each monitored integration
3. Click into each tab to see its latency trend chart, endpoint-level
   breakdown, and any incidents in the current window
4. Use **Refresh** in the sidebar to simulate a new data tick
5. Open the **Customer Report** tab for a plain-language summary, and click
   **Generate PDF Report** to download a shareable report with an executive
   summary, comparison table, and latency chart

## Sample data

- `knowledge_base.json` ships with 5 example RFP Q&A pairs (SSO, uptime SLA,
  SOC 2, data residency, support) so the RFP tool works out of the box
- The monitoring dashboard generates its own simulated data on load, with a
  refresh button to simulate a new tick
