"""
Shared visual theme for the SE Toolkit.
A control-room aesthetic: dark graphite background, signal-colored status
accents (emerald/amber/rose), monospace for data figures. Import and call
inject_theme() at the top of each page, after st.set_page_config().
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #0B0E14;
    --card: #141922;
    --card-border: #232936;
    --text: #E7EBF2;
    --muted: #8B95A7;
    --healthy: #34D399;
    --warning: #F59E0B;
    --down: #F0576B;
    --accent: #5B8CFF;
}

/* Base type */
html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }
.mono, .stMetricValue, code { font-family: 'JetBrains Mono', monospace !important; }

/* Status card */
.status-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-left: 4px solid var(--status-color, var(--accent));
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 10px;
}
.status-card .label {
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.status-card .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--text);
}
.status-card .sub {
    color: var(--muted);
    font-size: 0.85rem;
    margin-top: 4px;
}

/* Pulse dot for "up" status */
.pulse-dot {
    height: 9px; width: 9px; border-radius: 50%;
    display: inline-block; margin-right: 7px;
    background: var(--healthy);
    box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.6);
    animation: pulse 2s infinite;
    position: relative; top: -1px;
}
.pulse-dot.down {
    background: var(--down);
    box-shadow: 0 0 0 0 rgba(240, 87, 107, 0.6);
    animation: pulse-down 2s infinite;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.55); }
    70%  { box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
    100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}
@keyframes pulse-down {
    0%   { box-shadow: 0 0 0 0 rgba(240, 87, 107, 0.55); }
    70%  { box-shadow: 0 0 0 8px rgba(240, 87, 107, 0); }
    100% { box-shadow: 0 0 0 0 rgba(240, 87, 107, 0); }
}

/* Section divider label */
.section-eyebrow {
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin: 6px 0 2px 0;
}
</style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def status_card(label, value, sub, status="healthy"):
    """Renders one styled status card as HTML. status: healthy | warning | down"""
    color_map = {"healthy": "var(--healthy)", "warning": "var(--warning)", "down": "var(--down)"}
    color = color_map.get(status, "var(--accent)")
    dot_class = "pulse-dot" if status == "healthy" else "pulse-dot down"
    st.markdown(
        f"""
        <div class="status-card" style="--status-color: {color};">
            <div class="label">{label}</div>
            <div class="value"><span class="{dot_class}"></span>{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_eyebrow(text):
    st.markdown(f'<div class="section-eyebrow">{text}</div>', unsafe_allow_html=True)
