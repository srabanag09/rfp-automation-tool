"""
API Monitoring Dashboard
A lightweight dashboard for monitoring integration health — the kind of tool
an SE hands to a customer post-deployment to self-serve status checks instead
of filing support tickets.

Runs entirely on simulated data. No external services or API keys required.

Built by Srabana Guha
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="API Monitoring Dashboard", page_icon="📡", layout="wide")

SERVICES = [
    {"name": "Payments API", "baseline_latency": 120, "reliability": 0.985},
    {"name": "Auth Service", "baseline_latency": 60, "reliability": 0.995},
    {"name": "Notification API", "baseline_latency": 200, "reliability": 0.97},
    {"name": "Data Sync Pipeline", "baseline_latency": 350, "reliability": 0.96},
]

LATENCY_ALERT_THRESHOLD_MS = 500
POINTS_PER_SERVICE = 60  # simulated ticks (e.g. one per minute over the last hour)


def simulate_service_history(service, seed):
    """Generates a simulated latency + status time series for one service."""
    rng = np.random.default_rng(seed)
    now = datetime.now()

    timestamps = [now - timedelta(minutes=(POINTS_PER_SERVICE - i)) for i in range(POINTS_PER_SERVICE)]

    # Stationary noise around the baseline latency, with occasional spikes.
    # (Deliberately not a random walk — an unbounded walk drifts over 60 ticks
    # and produces unrealistic latency figures.)
    baseline = service["baseline_latency"]
    latencies = []
    for _ in range(POINTS_PER_SERVICE):
        lat = max(10, rng.normal(baseline, baseline * 0.15))
        if rng.random() < 0.03:
            lat += rng.uniform(150, 400)
        latencies.append(lat)

    # Status: down based on the service's configured reliability
    statuses = []
    for lat in latencies:
        is_down = rng.random() > service["reliability"]
        statuses.append("down" if is_down else "up")

    return pd.DataFrame({
        "timestamp": timestamps,
        "latency_ms": latencies,
        "status": statuses,
    })


def get_service_data():
    """Cached-per-session simulated data, regenerated on demand via refresh."""
    if "monitoring_data" not in st.session_state or st.session_state.get("force_refresh"):
        data = {}
        for i, service in enumerate(SERVICES):
            seed = st.session_state.get("sim_seed", 42) + i
            data[service["name"]] = simulate_service_history(service, seed)
        st.session_state.monitoring_data = data
        st.session_state.force_refresh = False
    return st.session_state.monitoring_data


def compute_summary(df):
    uptime_pct = (df["status"] == "up").mean() * 100
    avg_latency = df["latency_ms"].mean()
    current_status = df.iloc[-1]["status"]
    current_latency = df.iloc[-1]["latency_ms"]
    incidents = df[(df["status"] == "down") | (df["latency_ms"] > LATENCY_ALERT_THRESHOLD_MS)]
    return uptime_pct, avg_latency, current_status, current_latency, incidents


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

# --- Summary cards ---
cols = st.columns(len(SERVICES))
for col, service in zip(cols, SERVICES):
    df = data[service["name"]]
    uptime_pct, avg_latency, current_status, current_latency, incidents = compute_summary(df)

    with col:
        status_emoji = "🟢" if current_status == "up" else "🔴"
        st.metric(
            label=f"{status_emoji} {service['name']}",
            value=f"{current_latency:.0f} ms",
            delta=f"{uptime_pct:.1f}% uptime",
            delta_color="normal" if uptime_pct > 98 else "inverse",
        )

st.divider()

# --- Detail view per service ---
tab_names = [s["name"] for s in SERVICES]
tabs = st.tabs(tab_names)

for tab, service in zip(tabs, SERVICES):
    with tab:
        df = data[service["name"]]
        uptime_pct, avg_latency, current_status, current_latency, incidents = compute_summary(df)

        c1, c2, c3 = st.columns(3)
        c1.metric("Uptime (window)", f"{uptime_pct:.1f}%")
        c2.metric("Avg latency", f"{avg_latency:.0f} ms")
        c3.metric("Current status", "🟢 Up" if current_status == "up" else "🔴 Down")

        st.line_chart(df.set_index("timestamp")["latency_ms"], height=250)

        if not incidents.empty:
            st.subheader(f"⚠️ Incidents ({len(incidents)})")
            display_df = incidents.copy()
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
            display_df["latency_ms"] = display_df["latency_ms"].round(0)
            st.dataframe(
                display_df[["timestamp", "status", "latency_ms"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("No incidents in this window.")

st.divider()
st.caption("Built with Streamlit · Simulated monitoring data · [Srabana Guha](https://www.linkedin.com/)")
