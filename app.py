"""
SE Toolkit — Home
A collection of tools for practical Solutions Engineering workflows:
pre-sales deal support, post-sale customer health, and technical scoping.
"""

import streamlit as st
from theme import inject_theme, section_eyebrow

st.set_page_config(page_title="SE Toolkit", page_icon="🧰", layout="wide")
inject_theme()

st.title("🧰 SE Toolkit")
st.caption("A set of tools built to solve real Solutions Engineering problems — pre-sales, post-sale, and everywhere in between.")

st.markdown("""
Use the sidebar (or the cards below) to try each tool. Both run fully in **Demo Mode**
by default — no API key, no cost, no setup — so you can explore them immediately.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 RFP Automation Tool")
    st.markdown("""
**Problem it solves:** RFP responses eat huge SE hours and are often
inconsistent across reps.

**What it does:** Drafts RFP responses grounded in a retrieval layer over your
team's past answers, so drafts stay consistent instead of the model
improvising. Supports single-question and bulk CSV modes.

**Stack:** Streamlit · Claude · TF-IDF retrieval (scikit-learn)
""")
    st.page_link("pages/1_📄_RFP_Automation_Tool.py", label="Open RFP Automation Tool →", icon="📄")

with col2:
    st.subheader("📡 API Monitoring Dashboard")
    st.markdown("""
**Problem it solves:** SEs need to prove integration health to customers
during and after a POC or pilot — this is often the difference between a
smooth renewal and a churn scare.

**What it does:** A lightweight dashboard showing live-style status, latency
trends, and an incident log for a set of integrations — the kind of thing an
SE hands to a customer post-deployment to self-serve health checks.

**Stack:** Streamlit · pandas · simulated monitoring data
""")
    st.page_link("pages/2_📡_API_Monitoring_Dashboard.py", label="Open API Monitoring Dashboard →", icon="📡")

st.divider()
st.caption("More tools coming soon: SE POC Generator (auto-generates POC outlines from JD + customer notes)")
