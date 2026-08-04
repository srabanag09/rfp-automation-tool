# RFP Automation Tool

AI-powered RFP response generator using Claude, grounded in a retrieval layer over
past RFP answers — built to cut down the hours Sales/Solutions Engineers spend
drafting consistent, accurate RFP responses under deadline pressure.

**[Live demo →](#)** *(add your deployed Streamlit URL here once live)*

![screenshot placeholder](docs/screenshot.png)

## The problem

RFP responses eat huge amounts of SE time and are often inconsistent across reps —
different people answer the same question differently, facts drift over time, and
nobody has a single source of truth for "what did we say last time."

## What this does

- **Single-question mode** — paste one RFP question, get a drafted response instantly
- **Bulk mode** — upload a CSV of RFP questions, get all responses generated and
  exported as a CSV in one pass
- **Retrieval-augmented generation** — every draft is grounded in a knowledge base
  of past RFP answers (TF-IDF similarity search), so responses stay consistent with
  what your team has actually said before, instead of the model improvising
- **Editable knowledge base** — add new Q&A pairs directly in the UI or bulk-upload
  via CSV as your answer library grows

## Tech stack

- **Streamlit** — UI
- **Claude (Anthropic API)** — response generation
- **scikit-learn (TF-IDF)** — lightweight retrieval layer over the knowledge base
- **pandas** — bulk CSV processing

## Running locally

```bash
git clone <your-repo-url>
cd rfp-automation-tool
pip install -r requirements.txt

# Add your API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml with your real Anthropic API key

streamlit run app.py
```

## Deploying (free, ~5 minutes)

1. Push this repo to GitHub (public repo is fine — secrets.toml is gitignored,
   so your API key never gets committed)
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. Click **New app**, select this repo and `app.py` as the entry point
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-real-key"
   ```
5. Deploy — you'll get a public URL like `your-app-name.streamlit.app`

**Note:** free-tier apps sleep after ~12 hours of no traffic. The first visitor
after a sleep period waits ~20-30 seconds for it to wake up — this is normal, not
a bug.

## Sample data

`knowledge_base.json` ships with 5 example RFP Q&A pairs (SSO, uptime SLA, SOC 2,
data residency, support) so the demo works out of the box. Replace with your own
team's answers, or upload a CSV via the sidebar.

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

## Why this project

Built to demonstrate the kind of technical + business-facing tooling a Solutions
Engineer builds for their own team: something that saves real hours, is grounded
in facts (not hallucinated), and can be handed to a non-technical teammate to use
without them touching code.

---
Built by Srabana Guha · Staff SE, 12+ years at Uber, Walmart Connect, and Hulu
