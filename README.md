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


