"""
API Monitoring Dashboard
A lightweight dashboard for monitoring integration health — the kind of tool
an SE hands to a customer post-deployment to self-serve status checks instead
of filing support tickets.

Runs entirely on simulated data. No external services or API keys required.
"""

import io
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
)

from theme import inject_theme, status_card, section_eyebrow

st.set_page_config(page_title="API Monitoring Dashboard", page_icon="📡", layout="wide")
inject_theme()

SERVICES = [
    {
        "name": "Payments API", "baseline_latency": 120, "reliability": 0.985,
        "endpoints": ["/v1/charges", "/v1/refunds", "/v1/webhooks"],
    },
    {
        "name": "Auth Service", "baseline_latency": 60, "reliability": 0.995,
        "endpoints": ["/v1/login", "/v1/token/refresh", "/v1/logout"],
    },
    {
        "name": "Notification API", "baseline_latency": 200, "reliability": 0.97,
        "endpoints": ["/v1/email/send", "/v1/sms/send", "/v1/push/send"],
    },
    {
        "name": "Data Sync Pipeline", "baseline_latency": 350, "reliability": 0.96,
        "endpoints": ["/v1/sync/customers", "/v1/sync/orders", "/v1/sync/inventory"],
    },
]

LATENCY_ALERT_THRESHOLD_MS = 500
POINTS_PER_SERVICE = 60  # simulated ticks (e.g. one per minute over the last hour)


def simulate_service_history(service, seed):
    """Generates a simulated latency + status time series for one service."""
    rng = np.random.default_rng(seed)
    now = datetime.now()
    timestamps = [now - timedelta(minutes=(POINTS_PER_SERVICE - i)) for i in range(POINTS_PER_SERVICE)]

    baseline = service["baseline_latency"]
    latencies = []
    for _ in range(POINTS_PER_SERVICE):
        lat = max(10, rng.normal(baseline, baseline * 0.15))
        if rng.random() < 0.03:
            lat += rng.uniform(150, 400)
        latencies.append(lat)

    statuses = [("down" if rng.random() > service["reliability"] else "up") for _ in latencies]

    return pd.DataFrame({"timestamp": timestamps, "latency_ms": latencies, "status": statuses})


def simulate_endpoint_snapshot(endpoint_name, baseline, reliability, seed):
    """Generates a single current-state snapshot for one endpoint."""
    rng = np.random.default_rng(seed)
    lat = max(5, rng.normal(baseline, baseline * 0.2))
    if rng.random() < 0.05:
        lat += rng.uniform(100, 300)
    is_up = rng.random() <= reliability
    uptime_pct = min(100.0, max(80.0, reliability * 100 + rng.uniform(-1.2, 0.8)))
    return {
        "endpoint": endpoint_name,
        "status": "up" if is_up else "down",
        "latency_ms": round(lat),
        "uptime_pct": round(uptime_pct, 2),
    }


def get_service_data():
    if "monitoring_data" not in st.session_state or st.session_state.get("force_refresh"):
        seed_base = st.session_state.get("sim_seed", 42)
        data = {}
        for i, service in enumerate(SERVICES):
            data[service["name"]] = simulate_service_history(service, seed_base + i)
        st.session_state.monitoring_data = data
        st.session_state.force_refresh = False
    return st.session_state.monitoring_data


def get_endpoint_data(service, seed_offset):
    seed_base = st.session_state.get("sim_seed", 42)
    rows = []
    for j, ep in enumerate(service["endpoints"]):
        seed = seed_base + seed_offset * 100 + j
        rows.append(simulate_endpoint_snapshot(ep, service["baseline_latency"], service["reliability"], seed))
    return pd.DataFrame(rows)


def compute_summary(df):
    uptime_pct = (df["status"] == "up").mean() * 100
    avg_latency = df["latency_ms"].mean()
    current_status = df.iloc[-1]["status"]
    current_latency = df.iloc[-1]["latency_ms"]
    incidents = df[(df["status"] == "down") | (df["latency_ms"] > LATENCY_ALERT_THRESHOLD_MS)]
    return uptime_pct, avg_latency, current_status, current_latency, incidents


def status_bucket(uptime_pct, current_status):
    if current_status == "down" or uptime_pct < 95:
        return "down"
    if uptime_pct < 99:
        return "warning"
    return "healthy"


def make_latency_chart_image(all_data):
    """Builds a combined latency trend chart as a PNG for embedding in the PDF report."""
    fig, ax = plt.subplots(figsize=(6.5, 2.8), dpi=150)
    for service in SERVICES:
        df = all_data[service["name"]]
        ax.plot(df["timestamp"], df["latency_ms"], label=service["name"], linewidth=1.4)
    ax.set_ylabel("Latency (ms)")
    ax.legend(fontsize=7, loc="upper left", ncol=2, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=7, rotation=0)
    ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def build_pdf_report(customer_name, all_data, summaries):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=4)
    muted_style = ParagraphStyle("Muted", parent=styles["Normal"], textColor=rl_colors.HexColor("#666666"), fontSize=9)
    body_style = styles["Normal"]

    story = []

    header_name = f"{customer_name} — " if customer_name.strip() else ""
    story.append(Paragraph(f"{header_name}Integration Health Report", title_style))
    story.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", muted_style))
    story.append(Spacer(1, 14))

    overall_uptime = np.mean([s["uptime_pct"] for s in summaries])
    total_incidents = sum(s["incident_count"] for s in summaries)
    if overall_uptime >= 99.5 and total_incidents == 0:
        exec_summary = (
            "All monitored integrations are operating normally, with no incidents detected "
            "in the reporting window."
        )
    elif overall_uptime >= 98:
        exec_summary = (
            f"Overall integration health is stable at {overall_uptime:.2f}% average uptime. "
            f"{total_incidents} minor incident(s) were detected and are detailed below."
        )
    else:
        exec_summary = (
            f"Overall integration health is at {overall_uptime:.2f}% average uptime, below target. "
            f"{total_incidents} incident(s) were detected in the reporting window and warrant review."
        )
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Paragraph(exec_summary, body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Service Summary", styles["Heading2"]))
    table_data = [["Service", "Status", "Uptime", "Avg Latency", "Incidents"]]
    for s in summaries:
        status_label = {"healthy": "Operational", "warning": "Degraded", "down": "Disruption"}[s["bucket"]]
        table_data.append([
            s["name"], status_label, f"{s['uptime_pct']:.1f}%",
            f"{s['avg_latency']:.0f} ms", str(s["incident_count"]),
        ])

    tbl = Table(table_data, colWidths=[1.7 * inch, 1.2 * inch, 0.9 * inch, 1.1 * inch, 0.9 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#1A1F2E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor("#F5F6F8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#DDDDDD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Latency Trend (last 60 minutes, simulated)", styles["Heading2"]))
    chart_buf = make_latency_chart_image(all_data)
    story.append(RLImage(chart_buf, width=6.3 * inch, height=2.7 * inch))
    story.append(Spacer(1, 14))

    story.append(Paragraph(
        "Note: This report is generated from simulated monitoring data for demonstration "
        "purposes only and does not reflect a live production system.",
        muted_style,
    ))

    doc.build(story)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Monitoring Controls")
    st.caption("This dashboard runs on simulated data — no live services or API keys are involved.")

    if st.button("🔄 Refresh (simulate new data tick)"):
        st.session_state.sim_seed = random.randint(0, 100000)
        st.session_state.force_refresh = True
        st.rerun()

    st.divider()
    st.caption(f"Alert threshold: latency > {LATENCY_ALERT_THRESHOLD_MS}ms")
    st.caption(f"Window: last {POINTS_PER_SERVICE} minutes (simulated)")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
st.title("📡 API Monitoring Dashboard")
st.caption("Integration health monitoring — the kind of view an SE hands to a customer post-deployment to self-serve status checks.")

data = get_service_data()

# --- Summary cards (custom styled, not default st.metric) ---
section_eyebrow("Live Status")
cols = st.columns(len(SERVICES))
summaries = []
for col, service in zip(cols, SERVICES):
    df = data[service["name"]]
    uptime_pct, avg_latency, current_status, current_latency, incidents = compute_summary(df)
    bucket = status_bucket(uptime_pct, current_status)
    summaries.append({
        "name": service["name"], "uptime_pct": uptime_pct, "avg_latency": avg_latency,
        "current_status": current_status, "incident_count": len(incidents), "bucket": bucket,
    })
    with col:
        status_card(
            label=service["name"],
            value=f"{current_latency:.0f} ms",
            sub=f"{uptime_pct:.1f}% uptime · {len(incidents)} incident(s)",
            status=bucket,
        )

st.divider()

# --- Detail view per service, plus a Customer Report tab ---
tab_names = [s["name"] for s in SERVICES] + ["📋 Customer Report"]
tabs = st.tabs(tab_names)

for idx, (tab, service) in enumerate(zip(tabs[:-1], SERVICES)):
    with tab:
        df = data[service["name"]]
        uptime_pct, avg_latency, current_status, current_latency, incidents = compute_summary(df)

        c1, c2, c3 = st.columns(3)
        c1.metric("Uptime (window)", f"{uptime_pct:.1f}%")
        c2.metric("Avg latency", f"{avg_latency:.0f} ms")
        c3.metric("Current status", "🟢 Up" if current_status == "up" else "🔴 Down")

        st.line_chart(df.set_index("timestamp")["latency_ms"], height=250)

        section_eyebrow("Endpoints")
        endpoint_df = get_endpoint_data(service, idx)
        display_ep = endpoint_df.copy()
        display_ep["status"] = display_ep["status"].map({"up": "🟢 Up", "down": "🔴 Down"})
        display_ep["uptime_pct"] = display_ep["uptime_pct"].astype(str) + "%"
        display_ep["latency_ms"] = display_ep["latency_ms"].astype(str) + " ms"
        display_ep.columns = ["Endpoint", "Status", "Latency", "Uptime"]
        st.dataframe(display_ep, width="stretch", hide_index=True)

        if not incidents.empty:
            st.subheader(f"⚠️ Incidents ({len(incidents)})")
            display_df = incidents.copy()
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
            display_df["latency_ms"] = display_df["latency_ms"].round(0)
            st.dataframe(
                display_df[["timestamp", "status", "latency_ms"]],
                width="stretch", hide_index=True,
            )
        else:
            st.success("No incidents in this window.")

# --- Customer Report tab ---
with tabs[-1]:
    st.subheader("Customer-Facing Report")
    st.caption("A plain-language summary you can hand to a customer, plus a downloadable PDF version.")

    customer_name = st.text_input("Customer name (optional)", placeholder="e.g. Acme Corp")

    for s in summaries:
        label = {"healthy": "✅ All systems operational", "warning": "🟡 Degraded performance detected", "down": "🔴 Service disruption"}[s["bucket"]]
        st.markdown(f"**{s['name']}** — {label}  \n"
                    f"Uptime: {s['uptime_pct']:.1f}% · Avg response time: {s['avg_latency']:.0f} ms · "
                    f"Incidents this window: {s['incident_count']}")
        st.markdown("---")

    if st.button("📄 Generate PDF Report", type="primary"):
        with st.spinner("Building report..."):
            pdf_buf = build_pdf_report(customer_name, data, summaries)
        st.success("Report ready.")
        st.download_button(
            "Download PDF Report",
            data=pdf_buf,
            file_name=f"integration_health_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )

st.divider()
st.caption("Built with Streamlit · Simulated monitoring data")
