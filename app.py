"""
Keylogger SOC Dashboard  –  app.py
Educational / Lab Use Only
"""

import streamlit as st
import keylogger_software as kl_core
import os
import time
import threading
from collections import Counter
from datetime import datetime, timedelta
import plotly.graph_objects as go

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SecureWatch SOC | Keystroke Threat Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session defaults ────────────────────────────────────────────────────────
for key, val in {
    "running": False,
    "theme": "dark",
    "session_start": None,
    "page": "dashboard",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─── Theme tokens ────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "app_bg":          "#060d1a",
        "sidebar_bg":      "#080f1e",
        "panel_bg":        "rgba(10,20,40,0.85)",
        "panel_border":    "rgba(0,212,180,0.22)",
        "panel_shadow":    "none",
        "accent":          "#00d4b4",
        "accent2":         "#3b82f6",
        "danger":          "#ef4444",
        "warning":         "#f59e0b",
        "success":         "#22c55e",
        "text":            "#cdd9f5",
        "text_dim":        "#5a7099",
        "text_head":       "#e8f4ff",
        "metric_val":      "#00d4b4",
        "chart_color":     "#3b82f6",
        "row_critical":    "rgba(239,68,68,0.15)",
        "row_info":        "rgba(0,212,180,0.06)",
        "logo_glow":       "0 0 24px rgba(0,212,180,0.55)",
        "threat_track":    "rgba(255,255,255,0.08)",
        "textarea_bg":     "rgba(4,10,22,0.88)",
        "textarea_color":  "#00d4b4",
        "bg_overlay":      "radial-gradient(ellipse at 8% 5%, rgba(0,212,180,0.07) 0%, transparent 38%), radial-gradient(ellipse at 92% 8%, rgba(59,130,246,0.09) 0%, transparent 35%), radial-gradient(ellipse at 50% 95%, rgba(59,130,246,0.05) 0%, transparent 40%),",
        "hover_glow":      "0 0 14px rgba(0,212,180,0.30)",
    },
    "light": {
        # Soft gray-blue page, white card surfaces, navy-gray text
        "app_bg":          "#F3F6FA",
        "sidebar_bg":      "#E8EEF6",
        "panel_bg":        "#FFFFFF",
        "panel_border":    "#D7DFE8",
        "panel_shadow":    "0 1px 3px rgba(15,30,60,0.06), 0 4px 12px rgba(15,30,60,0.04)",
        "accent":          "#0284C7",      # sky-blue – single teal/blue accent
        "accent2":         "#0369A1",
        "danger":          "#DC2626",      # red – critical alerts only
        "warning":         "#D97706",      # amber – warnings only
        "success":         "#16A34A",
        "text":            "#253040",      # dark navy-gray, not pure black
        "text_dim":        "#8897A8",      # muted gray secondary text
        "text_head":       "#0F1E32",      # near-black headings
        "metric_val":      "#0284C7",
        "chart_color":     "#0284C7",
        "row_critical":    "rgba(220,38,38,0.07)",
        "row_info":        "rgba(2,132,199,0.05)",
        "logo_glow":       "0 0 18px rgba(2,132,199,0.22)",
        "threat_track":    "rgba(15,30,60,0.08)",
        "textarea_bg":     "#F8FAFB",
        "textarea_color":  "#253040",
        "bg_overlay":      "",             # no glow radials in light mode
        "hover_glow":      "0 2px 8px rgba(2,132,199,0.20)",
    },
}

t = THEMES[st.session_state.theme]

# ─── Global CSS ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
.stApp {{
    background:
        {t['bg_overlay']}
        {t['app_bg']};
    color: {t['text']};
}}
/* Hide Streamlit toolbar noise (keep native header visible) */
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
[data-testid="stDeployButton"]    {{ display: none !important; }}
[data-testid="stAppDeployButton"] {{ display: none !important; }}
[data-testid="stHeaderActionElements"] {{ display: none !important; }}
button[title="Deploy"] {{ display: none !important; }}
[data-testid="stStatusWidget"]    {{ display: none !important; }}
[data-testid="stToolbarActions"]  {{ display: none !important; }}
.block-container {{ padding: 4.2rem 1.6rem 2rem; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {t['sidebar_bg']} !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
}}
[data-testid="stSidebar"] * {{ color: {t['text']} !important; }}
[data-testid="stSidebar"] > div:first-child {{
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {{
    width: 0 !important;
    height: 0 !important;
}}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track {{
    background: transparent !important;
}}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {{
    background: transparent !important;
}}

/* Style Streamlit's native collapse arrow to look like a teal pill */
[data-testid="stSidebarCollapsedControl"] {{ 
    background: {t['panel_bg']} !important;
    border: 1px solid {t['accent']} !important;
    border-left: none !important;
    border-radius: 0 12px 12px 0 !important;
    box-shadow: 0 4px 12px rgba(0,212,180,0.3) !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stSidebarCollapsedControl"] svg {{
    stroke: {t['accent']} !important;
}}

/* ── Typography ── */
h1, h2, h3, h4 {{ color: {t['text_head']} !important; font-weight: 700; }}

/* ── Panels / Cards ── */
.soc-panel {{
    background: {t['panel_bg']};
    border: 1px solid {t['panel_border']};
    border-radius: 14px;
    padding: 18px 20px 14px;
    margin-bottom: 16px;
    box-shadow: {t['panel_shadow']};
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
}}
.soc-panel-title {{
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    color: {t['text_dim']};
    margin-bottom: 6px;
}}

/* ── KPI tiles ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 0;
}}
.kpi-tile {{
    background: {t['panel_bg']};
    border: 1px solid {t['panel_border']};
    border-radius: 12px;
    padding: 16px 18px;
    text-align: left;
    position: relative;
    overflow: hidden;
    box-shadow: {t['panel_shadow']};
}}
.kpi-tile::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: {t['accent']};
    border-radius: 12px 0 0 12px;
}}
.kpi-tile.danger::before {{ background: {t['danger']}; }}
.kpi-tile.warning::before {{ background: {t['warning']}; }}
.kpi-tile.success::before {{ background: {t['success']}; }}
.kpi-label {{
    font-size: 0.72rem;
    letter-spacing: 1.1px;
    text-transform: uppercase;
    color: {t['text_dim']};
    margin-bottom: 4px;
}}
.kpi-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {t['metric_val']};
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
}}
.kpi-tile.danger .kpi-value  {{ color: {t['danger']}; }}
.kpi-tile.warning .kpi-value {{ color: {t['warning']}; }}
.kpi-tile.success .kpi-value {{ color: {t['success']}; }}
.kpi-sub {{
    font-size: 0.75rem;
    color: {t['text_dim']};
}}

/* ── Status badges ── */
.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
.badge-critical {{ background: rgba(239,68,68,0.18);  color: {t['danger']};  border: 1px solid rgba(239,68,68,0.4); }}
.badge-info     {{ background: rgba(0,212,180,0.12); color: {t['accent']};  border: 1px solid rgba(0,212,180,0.3); }}
.badge-open     {{ background: rgba(245,158,11,0.15); color: {t['warning']}; border: 1px solid rgba(245,158,11,0.4); }}
.badge-reviewed {{ background: rgba(34,197,94,0.12);  color: {t['success']};  border: 1px solid rgba(34,197,94,0.3); }}

/* ── Status pill (header) ── */
.status-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    background: {t['panel_bg']};
    border: 1px solid {t['panel_border']};
    border-radius: 10px;
    margin-bottom: 16px;
    font-size: 0.82rem;
}}
.status-dot {{
    width: 9px; height: 9px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}}
.status-dot.active  {{ background: {t['success']}; box-shadow: 0 0 6px {t['success']}; animation: pulse 1.6s ease-in-out infinite; }}
.status-dot.stopped {{ background: {t['danger']};  }}
@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.45; }} }}

/* ── Threat level meter ── */
.threat-bar-wrap {{
    background: {t['threat_track']};
    border-radius: 99px;
    height: 8px;
    overflow: hidden;
    margin: 6px 0 2px;
}}
.threat-bar-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}}

/* ── Event table rows ── */
.event-row {{ border-bottom: 1px solid {t['panel_border']}; font-size: 0.8rem; }}
.event-row.critical {{ background: {t['row_critical']}; }}

/* ── Log feed ── */
.stTextArea textarea {{
    background: {t['textarea_bg']} !important;
    color: {t['textarea_color']} !important;
    border: 1px solid {t['panel_border']} !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}}

/* ── Buttons ── */
.stButton > button {{
    border-radius: 8px;
    border: 1px solid {t['panel_border']};
    background: {t['panel_bg']};
    color: {t['text_head']};
    font-weight: 600;
    font-size: 0.82rem;
    transition: all 0.2s ease;
    width: 100%;
}}
.stButton > button:hover {{
    border-color: {t['accent']};
    box-shadow: {t['hover_glow']};
    transform: translateY(-1px);
}}

/* ── Selectbox / text input ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {{
    background: {t['panel_bg']} !important;
    color: {t['text']} !important;
    border-color: {t['panel_border']} !important;
    border-radius: 8px !important;
}}

/* ── Metrics widget ── */
[data-testid="stMetricValue"] {{ color: {t['metric_val']} !important; font-weight: 700; }}
[data-testid="stMetricLabel"] {{ color: {t['text_dim']} !important; font-size: 0.78rem !important; }}

/* ── Logo / header bar ── */
.top-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 6px;
}}
.logo-icon {{
    font-size: 2.1rem;
    filter: drop-shadow({t['logo_glow']});
}}
.product-name {{
    font-size: 1.55rem;
    font-weight: 700;
    color: {t['text_head']};
    line-height: 1;
    letter-spacing: -0.3px;
}}
.product-sub {{
    font-size: 0.73rem;
    color: {t['text_dim']};
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-top: 2px;
}}
.divider {{ height:1px; background: linear-gradient(90deg, transparent, {t['accent']}55, transparent); margin: 8px 0 16px; }}

/* ── Awareness section ── */
.aware-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }}
.aware-card {{
    background: {t['panel_bg']};
    border: 1px solid {t['panel_border']};
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: {t['panel_shadow']};
}}
.aware-card h4 {{ margin: 0 0 10px; font-size: 0.92rem; }}
.aware-card ul {{ margin: 0; padding-left: 16px; }}
.aware-card ul li {{ margin-bottom: 7px; font-size: 0.82rem; color: {t['text']}; line-height: 1.5; }}
.ethics-card {{
    background: {t['panel_bg']};
    border: 1px solid rgba(245,158,11,0.35);
    border-left: 3px solid {t['warning']};
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 0.83rem;
    line-height: 1.6;
    color: {t['text']};
}}

/* ── Sidebar nav links ── */
.nav-item {{
    display: block;
    padding: 9px 14px;
    border-radius: 8px;
    font-size: 0.84rem;
    font-weight: 500;
    cursor: pointer;
    margin-bottom: 2px;
    transition: background 0.2s;
}}
.nav-item.active {{
    background: rgba(0,212,180,0.15);
    border-left: 3px solid {t['accent']};
    color: {t['accent']} !important;
}}

/* ── Dataframe override ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {t['panel_border']};
    border-radius: 10px;
    overflow: hidden;
}}

/* ── Header theme toggle button (circular icon pill, top-right) ── */
/* Target by button key rendered as data-testid on the container */
button[kind="secondary"][data-testid="stBaseButton-secondary"]#theme_btn,
button[key="theme_btn"],
[data-testid="stButton"] button {{}}

/* Reliable: style the last column's button in the header row */
.stMainBlockContainer .stColumns .stColumn:last-child .stButton > button {{
    width: 42px !important;
    height: 42px !important;
    min-width: 42px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    font-size: 1.2rem !important;
    background: {t['panel_bg']} !important;
    border: 1px solid {t['panel_border']} !important;
    color: {t['text_head']} !important;
    box-shadow: inset 0 0 0 1px {t['panel_border']};
    transition: all 0.25s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    margin-top: 4px !important;
}}
.stMainBlockContainer .stColumns .stColumn:last-child .stButton > button:hover {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 18px rgba(0,212,180,0.40) !important;
    transform: rotate(20deg) scale(1.1) !important;
    background: rgba(0,212,180,0.13) !important;
}}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ────────────────────────────────────────────────────────────────
def read_logs() -> str:
    if os.path.exists(kl_core.LOG_FILE):
        with open(kl_core.LOG_FILE, "r") as f:
            return f.read()
    return ""


def chart_layout(title: str = "") -> dict:
    """Return a Plotly layout dict themed to match the active dark/light mode."""
    is_dark = st.session_state.theme == "dark"
    if is_dark:
        paper_bg  = "rgba(0,0,0,0)"          # transparent – panel_bg shows through
        plot_bg   = "rgba(10,20,40,0.60)"
        grid_col  = "rgba(255,255,255,0.07)"
        axis_col  = "#5a7099"
        font_col  = "#cdd9f5"
        zero_col  = "rgba(255,255,255,0.12)"
    else:
        paper_bg  = "rgba(0,0,0,0)"          # transparent – white panel_bg shows
        plot_bg   = "#FFFFFF"
        grid_col  = "#DDE4EE"                 # soft gray-blue gridlines
        axis_col  = "#8897A8"                 # muted secondary text
        font_col  = "#253040"                 # dark navy-gray labels
        zero_col  = "#BEC8D4"

    return dict(
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(family="Inter, sans-serif", color=font_col, size=11),
        title=dict(text=title, font=dict(size=12, color=font_col)) if title else {},
        margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(
            gridcolor=grid_col,
            linecolor=axis_col,
            tickcolor=axis_col,
            tickfont=dict(color=font_col, size=10),
            zerolinecolor=zero_col,
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor=grid_col,
            linecolor=axis_col,
            tickcolor=axis_col,
            tickfont=dict(color=font_col, size=10),
            zerolinecolor=zero_col,
            showgrid=True,
        ),
        showlegend=False,
        height=220,
    )


def hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    """Convert a #RRGGBB hex string to rgba(r,g,b,alpha) for Plotly fillcolor."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def mask_sensitive(text: str) -> str:
    for word in kl_core.SENSITIVE_WORDS:
        text = text.replace(word, "●" * len(word))
    return text


def parse_ts(line: str):
    if line.startswith("[") and "]" in line:
        raw = line[1:line.index("]")]
        try:
            return datetime.strptime(raw, "%a %b %d %H:%M:%S %Y")
        except ValueError:
            return None
    return None


def build_rows(raw: str) -> list[dict]:
    rows = []
    for idx, line in enumerate([l for l in raw.splitlines() if l.strip()], 1):
        ts = parse_ts(line)
        is_alert = "[ALERT]" in line
        rows.append({
            "id":         idx,
            "timestamp":  ts,
            "time":       ts.strftime("%Y-%m-%d  %H:%M:%S") if ts else "—",
            "severity":   "Critical" if is_alert else "Info",
            "event_type": "Sensitive Input" if is_alert else "Keyboard Input",
            "status":     "Open" if is_alert else "Reviewed",
            "source":     "KB Hook",
            "entity":     "Local Session",
            "details":    line,
        })
    return rows


def threat_level(rows: list[dict]) -> tuple[str, int, str]:
    """Return (label, pct, color) based on critical ratio."""
    total = len(rows)
    crits = sum(1 for r in rows if r["severity"] == "Critical")
    if total == 0:
        return "No Data", 0, "#5a7099"
    ratio = crits / total
    if ratio >= 0.4:
        return "HIGH", int(ratio * 100), t["danger"]
    if ratio >= 0.15:
        return "MEDIUM", int(ratio * 100), t["warning"]
    return "LOW", max(5, int(ratio * 100)), t["success"]


def session_duration() -> str:
    if st.session_state.session_start is None:
        return "—"
    delta = datetime.now() - st.session_state.session_start
    h, rem = divmod(int(delta.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ─── Page header helper ─────────────────────────────────────────────────────
def render_page_header(icon: str, title: str, subtitle: str):
    """Header: [logo + title] | [theme toggle]"""
    is_dark = st.session_state.theme == "dark"
    theme_icon = "🌙" if is_dark else "☀️"
    col_title, col_theme = st.columns([11, 1])

    with col_title:
        st.markdown(f"""
        <div class="top-header">
            <span class="logo-icon">{icon}</span>
            <div>
                <div class="product-name">{title}</div>
                <div class="product-sub">{subtitle}</div>
            </div>
        </div>
        <div class="divider"></div>
        """, unsafe_allow_html=True)

    with col_theme:
        if st.button(theme_icon, key="theme_btn", help="Toggle Dark ↔ Light mode"):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 18px;'>
        <div style='font-size:2.4rem; filter:drop-shadow(0 0 18px rgba(0,212,180,0.6))'>🛡️</div>
        <div style='font-size:1.1rem; font-weight:700; letter-spacing:-0.2px; margin-top:4px;'>SecureWatch</div>
        <div style='font-size:0.68rem; letter-spacing:1.4px; text-transform:uppercase; opacity:0.5; margin-top:2px;'>SOC Platform v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**NAVIGATION**")
    pages = {
        "dashboard":  "📊  Dashboard",
        "events":     "📋  Event Queue",
        "logs":       "📄  Raw Log Feed",
        "awareness":  "⚠️  Threat Awareness",
    }
    for key, label in pages.items():
        active_cls = "active" if st.session_state.page == key else ""
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    st.markdown("**AGENT CONTROLS**")
    if st.button("▶  Start Monitor"):
        if not st.session_state.running:
            threading.Thread(target=kl_core.start_keylogger, daemon=True).start()
            st.session_state.running = True
            st.session_state.session_start = datetime.now()
            st.rerun()

    if st.button("■  Stop Monitor"):
        kl_core.stop_keylogger()
        st.session_state.running = False
        st.rerun()

    if st.button("🗑  Clear Logs"):
        kl_core.clear_logs()
        st.rerun()

    st.markdown("---")
    # Log export
    if os.path.exists(kl_core.LOG_FILE):
        with open(kl_core.LOG_FILE, "rb") as f:
            st.download_button(
                label="⬇  Export Log File",
                data=f,
                file_name="securewatch_events.txt",
                mime="text/plain",
                use_container_width=True,
            )

    st.markdown(f"""
    <div style='font-size:0.68rem; color:{t['text_dim']}; margin-top:20px; line-height:1.7;'>
        <b>SecureWatch SOC</b><br>
        Educational Use Only<br>
        Keystroke Threat Monitor<br>
        © 2026 — Lab Environment
    </div>
    """, unsafe_allow_html=True)


# ─── Load data (all pages share this) ───────────────────────────────────────
raw_logs  = read_logs()
all_rows  = build_rows(raw_logs)
sev_count = Counter(r["severity"] for r in all_rows)
sta_count = Counter(r["status"]   for r in all_rows)
now_ts    = datetime.now()
last_24h  = sum(1 for r in all_rows if r["timestamp"] and r["timestamp"] >= now_ts - timedelta(hours=24))
thr_label, thr_pct, thr_color = threat_level(all_rows)



# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    # Header
    status_dot  = "active" if st.session_state.running else "stopped"
    status_text = "Active Monitoring" if st.session_state.running else "Monitoring Stopped"
    render_page_header("🛡️", "SecureWatch SOC", "Keystroke Threat Intelligence Platform")
    st.markdown(f"""
    <div class="status-bar">
        <span class="status-dot {status_dot}"></span>
        <span style="font-weight:600;">Agent Status:</span>&nbsp;{status_text}
        &nbsp;|&nbsp; <span style="color:{t['text_dim']}">Session:</span>&nbsp;{session_duration()}
        &nbsp;|&nbsp; <span style="color:{t['text_dim']}">Log File:</span>&nbsp;{kl_core.LOG_FILE}
    </div>
    """, unsafe_allow_html=True)

    # KPI Tiles
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-tile">
            <div class="kpi-label">Total Events</div>
            <div class="kpi-value">{len(all_rows)}</div>
            <div class="kpi-sub">all captured keystrokes</div>
        </div>
        <div class="kpi-tile danger">
            <div class="kpi-label">Critical Alerts</div>
            <div class="kpi-value">{sev_count.get('Critical', 0)}</div>
            <div class="kpi-sub">sensitive inputs detected</div>
        </div>
        <div class="kpi-tile warning">
            <div class="kpi-label">Open / Unreviewed</div>
            <div class="kpi-value">{sta_count.get('Open', 0)}</div>
            <div class="kpi-sub">require analyst triage</div>
        </div>
        <div class="kpi-tile success">
            <div class="kpi-label">Last 24 h</div>
            <div class="kpi-value">{last_24h}</div>
            <div class="kpi-sub">events in rolling window</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: Threat Meter + Charts
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown(f"""
        <div class="soc-panel">
            <div class="soc-panel-title">Threat Level</div>
            <div style="font-size:2.2rem; font-weight:800; color:{thr_color}; margin: 8px 0 4px;">
                {thr_label}
            </div>
            <div class="threat-bar-wrap">
                <div class="threat-bar-fill" style="width:{thr_pct}%; background:{thr_color};"></div>
            </div>
            <div style="font-size:0.72rem; color:{t['text_dim']}; margin-top:4px;">
                {thr_pct}% of events are critical
            </div>
            <div style="margin-top:16px;">
                <div style="font-size:0.72rem; color:{t['text_dim']}; margin-bottom:4px; text-transform:uppercase; letter-spacing:1px;">Breakdown</div>
                <div style="display:flex; justify-content:space-between; font-size:0.82rem; margin-bottom:6px;">
                    <span style="color:{t['danger']};">⬤ Critical</span>
                    <span style="font-weight:600;">{sev_count.get('Critical', 0)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.82rem;">
                    <span style="color:{t['accent']};">⬤ Info</span>
                    <span style="font-weight:600;">{sev_count.get('Info', 0)}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="soc-panel-title">Event Trend — Hourly Activity</div>', unsafe_allow_html=True)
        hour_counter = Counter()
        for row in all_rows:
            if row["timestamp"]:
                hour_counter[row["timestamp"].strftime("%m-%d %H:00")] += 1
        trend_data = dict(sorted(hour_counter.items()))
        if trend_data:
            hours  = list(trend_data.keys())
            counts = list(trend_data.values())
            fig_trend = go.Figure(
                go.Scatter(
                    x=hours, y=counts,
                    mode="lines+markers",
                    line=dict(color=t["chart_color"], width=2.5, shape="spline", smoothing=1.1),
                    marker=dict(size=5, color=t["chart_color"]),
                    fill="tozeroy",
                    fillcolor=hex_to_rgba(t["chart_color"], 0.12),
                    hovertemplate="%{x}<br><b>%{y} events</b><extra></extra>",
                )
            )
            fig_trend.update_layout(**chart_layout())
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No timestamped events yet — start the monitor and press Enter to flush lines.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 3: Severity bar + Status breakdown
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="soc-panel-title">Severity Distribution</div>', unsafe_allow_html=True)
        fig_sev = go.Figure(go.Bar(
            x=["Critical", "Info"],
            y=[sev_count.get("Critical", 0), sev_count.get("Info", 0)],
            marker_color=[t["danger"], t["chart_color"]],
            marker_line_width=0,
            hovertemplate="%{x}: <b>%{y}</b><extra></extra>",
        ))
        fig_sev.update_layout(**chart_layout())
        st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="soc-panel-title">Triage Status Summary</div>', unsafe_allow_html=True)
        fig_sta = go.Figure(go.Bar(
            x=["Open", "Reviewed"],
            y=[sta_count.get("Open", 0), sta_count.get("Reviewed", 0)],
            marker_color=[t["warning"], t["success"]],
            marker_line_width=0,
            hovertemplate="%{x}: <b>%{y}</b><extra></extra>",
        ))
        fig_sta.update_layout(**chart_layout())
        st.plotly_chart(fig_sta, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Monitoring stats strip
    st.markdown(f"""
    <div class="soc-panel" style="padding:12px 20px;">
        <div class="soc-panel-title">Monitoring Stats</div>
        <div style="display:flex; gap:40px; margin-top:8px; font-size:0.85rem;">
            <div><span style="color:{t['text_dim']};">Total Log Entries</span><br>
                 <strong style="font-size:1.2rem;">{len([l for l in raw_logs.splitlines() if l.strip()])}</strong></div>
            <div><span style="color:{t['text_dim']};">Log File Size</span><br>
                 <strong style="font-size:1.2rem;">{len(raw_logs.encode())} B</strong></div>
            <div><span style="color:{t['text_dim']};">Unique Hours Active</span><br>
                 <strong style="font-size:1.2rem;">{len(hour_counter)}</strong></div>
            <div><span style="color:{t['text_dim']};">Session Timer</span><br>
                 <strong style="font-size:1.2rem;">{session_duration()}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: EVENT QUEUE
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "events":
    render_page_header("📋", "Event Queue", "Analyst Triage View — All Captured Events")

    st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
    st.markdown('<div class="soc-panel-title">Filters</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns([1, 1, 2])
    time_flt = f1.selectbox("Time Range", ["All", "Last 24 h", "Last 7 d"], label_visibility="visible")
    sev_flt  = f2.selectbox("Severity",   ["All", "Critical", "Info"])
    srch_flt = f3.text_input("Keyword Search", placeholder="Filter by text in event details…")

    filtered = all_rows[:]
    if time_flt == "Last 24 h":
        filtered = [r for r in filtered if r["timestamp"] and r["timestamp"] >= now_ts - timedelta(hours=24)]
    elif time_flt == "Last 7 d":
        filtered = [r for r in filtered if r["timestamp"] and r["timestamp"] >= now_ts - timedelta(days=7)]
    if sev_flt != "All":
        filtered = [r for r in filtered if r["severity"] == sev_flt]
    if srch_flt.strip():
        q = srch_flt.strip().lower()
        filtered = [r for r in filtered if q in r["details"].lower()]

    st.markdown(f"<div style='font-size:0.8rem; color:{t['text_dim']}; margin:10px 0 4px;'>"
                f"Showing <b>{len(filtered)}</b> of <b>{len(all_rows)}</b> events</div>",
                unsafe_allow_html=True)

    if filtered:
        display = [{
            "Time":     r["time"],
            "Severity": r["severity"],
            "Type":     r["event_type"],
            "Status":   r["status"],
            "Source":   r["source"],
            "Entity":   r["entity"],
            "Details":  r["details"][:120] + ("…" if len(r["details"]) > 120 else ""),
        } for r in filtered]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No events match the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: RAW LOG FEED
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "logs":
    render_page_header("📄", "Raw Log Feed", "Live Keystroke Capture Stream — Sensitive Data Masked")

    masked = mask_sensitive(raw_logs)
    st.text_area("Live Log Stream", masked or "(No events captured yet)", height=480)

    if st.session_state.running:
        time.sleep(2)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: THREAT AWARENESS
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "awareness":
    render_page_header("⚠️", "Threat Awareness", "Cybersecurity Education & Responsible Disclosure")

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px;">
        <span style="font-size:1.1rem; font-weight:600; color:{t['text_head']};">
            Understanding Keylogger Threats in Modern Environments
        </span>
    </div>
    <div class="aware-grid">
        <div class="aware-card">
            <h4>🔍 How Keyloggers Work</h4>
            <ul>
                <li>Install a low-level OS keyboard hook to intercept every keystroke before it reaches the application.</li>
                <li>Captured data may include emails, usernames, OTPs, and passphrase sequences.</li>
                <li>Malicious variants transmit logs to a remote C2 server via HTTP, DNS, or email exfiltration.</li>
                <li>Advanced samples also capture clipboard contents and active window titles for richer context.</li>
                <li>Rootkit-class keyloggers hide in kernel space, making them invisible to standard antivirus scans.</li>
            </ul>
        </div>
        <div class="aware-card">
            <h4>🛡️ Detection & Prevention</h4>
            <ul>
                <li>Deploy EDR solutions that monitor for unauthorized keyboard hook registrations.</li>
                <li>Keep OS, browser, and AV definitions current — patched systems close common dropper entry points.</li>
                <li>Enforce application allowlisting so unknown binaries cannot execute.</li>
                <li>Enable MFA on all accounts; stolen passwords alone are insufficient to log in.</li>
                <li>Audit startup programs and scheduled tasks periodically for persistence mechanisms.</li>
                <li>Use hardware security keys where possible — they are immune to software keyloggers.</li>
            </ul>
        </div>
    </div>
    <div class="aware-grid">
        <div class="aware-card">
            <h4>🔎 Indicators of Compromise (IoCs)</h4>
            <ul>
                <li><strong>Unusual processes</strong> calling <code>SetWindowsHookEx</code> with <code>WH_KEYBOARD_LL</code>.</li>
                <li>Unexpected outbound connections from a non-browser process to remote hosts.</li>
                <li>New or modified files in <code>%APPDATA%</code> or <code>%TEMP%</code> written by unknown executables.</li>
                <li>Registry run-key entries pointing to unfamiliar binaries.</li>
            </ul>
        </div>
        <div class="aware-card">
            <h4>📌 Analyst Response Checklist</h4>
            <ul>
                <li>Isolate the affected endpoint from the network immediately.</li>
                <li>Preserve a memory dump before rebooting the system.</li>
                <li>Identify the hook registration timestamp using Sysmon Event ID 13.</li>
                <li>Reset all credentials that may have been exposed during the infection window.</li>
                <li>Notify the data protection officer if PII or credentials were exfiltrated.</li>
            </ul>
        </div>
    </div>
    <div class="ethics-card">
        <strong>⚖️ Legal & Ethical Responsibility</strong><br><br>
        This project is developed strictly for academic research, cybersecurity awareness training, and controlled 
        lab environments. Deploying a keylogger on a system without the explicit, informed consent of its owner 
        is a criminal offence in most jurisdictions — including the Indian IT Act 2000 (Section 43 / 66), 
        the U.S. Computer Fraud and Abuse Act, and the EU General Data Protection Regulation.<br><br>
        Always operate within authorised boundaries. Document your defensive intent, obtain written approval, 
        and handle all captured data with the same care expected of a licensed security professional.
    </div>
    """, unsafe_allow_html=True)


# ─── Auto-refresh while monitoring (all pages) ──────────────────────────────
if st.session_state.running and st.session_state.page != "logs":
    time.sleep(3)
    st.rerun()