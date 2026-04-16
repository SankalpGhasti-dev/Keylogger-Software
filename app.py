"""
SecureWatch SOC — Threat Intelligence Console
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

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SecureWatch SOC | Threat Intelligence Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session defaults ─────────────────────────────────────────────────────────
for key, val in {
    "running": False,
    "session_start": None,
    "page": "dashboard",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Design tokens – dark only ────────────────────────────────────────────────
C = {
    "app_bg":      "#0D1117",
    "sidebar_bg":  "#161B22",
    "card_bg":     "#1C2333",
    "card_alt":    "#21262D",
    "border":      "#30363D",
    "border_dim":  "#21262D",
    "text":        "#E6EDF3",
    "text_dim":    "#8B949E",
    "text_head":   "#F0F6FF",
    "critical":    "#F85149",
    "warning":     "#D29922",
    "info":        "#58A6FF",
    "success":     "#3FB950",
    "teal":        "#39D0B3",
    "critical_bg": "rgba(248,81,73,0.10)",
    "warning_bg":  "rgba(210,153,34,0.10)",
    "info_bg":     "rgba(88,166,255,0.08)",
    "success_bg":  "rgba(63,185,80,0.08)",
    "teal_bg":     "rgba(57,208,179,0.08)",
    "chart_bg":    "#161B22",
    "grid":        "#21262D",
    "shadow":      "0 4px 20px rgba(0,0,0,0.50)",
    "shadow_sm":   "0 2px 8px rgba(0,0,0,0.30)",
}

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {C['text']};
}}
.stApp {{
    background: {C['app_bg']};
    color: {C['text']};
}}

/* ── Streamlit native header ── */
[data-testid="stHeader"] {{
    background: {C['sidebar_bg']} !important;
    border-bottom: 1px solid {C['border']} !important;
}}
[data-testid="stHeader"] * {{ color: {C['text']} !important; }}

/* ── Hide clutter ── */
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
[data-testid="stDeployButton"],
[data-testid="stAppDeployButton"],
[data-testid="stHeaderActionElements"],
button[title="Deploy"],
[data-testid="stStatusWidget"],
[data-testid="stToolbarActions"] {{ display: none !important; }}
.block-container {{ padding: 4rem 1.8rem 2.5rem; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {C['sidebar_bg']} !important;
    border-right: 1px solid {C['border']} !important;
}}
[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}
[data-testid="stSidebar"] > div:first-child {{
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
}}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {{ width: 0 !important; }}
[data-testid="stSidebarCollapsedControl"] {{
    background: {C['card_bg']} !important;
    border: 1px solid {C['teal']} !important;
    border-left: none !important;
    border-radius: 0 10px 10px 0 !important;
    box-shadow: 0 0 12px rgba(57,208,179,0.20) !important;
}}
[data-testid="stSidebarCollapsedControl"] svg {{ stroke: {C['teal']} !important; }}

/* ── Typography ── */
h1, h2, h3, h4 {{ color: {C['text_head']} !important; font-weight: 700; }}

/* ── Sidebar spacing — 8px grid ── */
section[data-testid="stSidebarContent"] {{
    padding: 0 16px 24px !important;
}}
[data-testid="stSidebar"] .stVerticalBlock {{
    gap: 4px !important;
}}
[data-testid="stSidebar"] .stButton {{
    margin: 0 !important;
    padding: 0 !important;
}}
[data-testid="stSidebar"] [data-testid="element-container"] {{
    margin: 0 !important;
    padding: 0 !important;
}}

/* ── Sidebar all buttons – base ── */
[data-testid="stSidebar"] .stButton > button {{
    border-radius: 8px !important;
    border: 1px solid {C['border']} !important;
    background: {C['card_alt']} !important;
    color: {C['text']} !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    transition: all 0.18s ease !important;
    width: 100% !important;
    cursor: pointer !important;
    text-align: left !important;
    padding: 9px 14px !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {C['teal']} !important;
    background: {C['teal_bg']} !important;
    color: {C['teal']} !important;
}}

/* Nav active state */
.nav-active [data-testid="stSidebar"] .stButton > button,
.nav-active .stButton > button {{
    background: rgba(57,208,179,0.12) !important;
    border-left: 3px solid {C['teal']} !important;
    border-color: rgba(57,208,179,0.35) !important;
    color: {C['teal']} !important;
    border-radius: 0 8px 8px 0 !important;
}}

/* Start Monitor – green */
.btn-start .stButton > button {{
    border-color: rgba(63,185,80,0.35) !important;
    background: rgba(63,185,80,0.09) !important;
    color: {C['success']} !important;
}}
.btn-start .stButton > button:hover {{
    border-color: {C['success']} !important;
    background: rgba(63,185,80,0.16) !important;
    box-shadow: 0 0 10px rgba(63,185,80,0.18) !important;
    color: {C['success']} !important;
}}

/* Stop Monitor – red */
.btn-stop .stButton > button {{
    border-color: rgba(248,81,73,0.30) !important;
    background: rgba(248,81,73,0.08) !important;
    color: {C['critical']} !important;
}}
.btn-stop .stButton > button:hover {{
    border-color: {C['critical']} !important;
    background: rgba(248,81,73,0.14) !important;
    box-shadow: 0 0 10px rgba(248,81,73,0.16) !important;
    color: {C['critical']} !important;
}}

/* Clear Logs – amber */
.btn-clear .stButton > button {{
    border-color: rgba(210,153,34,0.30) !important;
    background: rgba(210,153,34,0.08) !important;
    color: {C['warning']} !important;
}}
.btn-clear .stButton > button:hover {{
    border-color: {C['warning']} !important;
    background: rgba(210,153,34,0.14) !important;
    color: {C['warning']} !important;
}}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {{
    border-radius: 8px !important;
    border: 1px solid {C['border']} !important;
    background: {C['card_alt']} !important;
    color: {C['text']} !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    text-align: left !important;
    padding: 9px 14px !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    border-color: {C['teal']} !important;
    background: {C['teal_bg']} !important;
    color: {C['teal']} !important;
}}

/* ── KPI tiles ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
}}
.kpi-tile {{
    background: {C['card_bg']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 18px 20px 16px;
    position: relative;
    overflow: hidden;
    box-shadow: {C['shadow']};
}}
.kpi-tile::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: {C['teal']};
    border-radius: 12px 0 0 12px;
}}
.kpi-tile.crit-tile {{
    background: linear-gradient(140deg, {C['card_bg']} 60%, rgba(248,81,73,0.07));
    border-color: rgba(248,81,73,0.28);
}}
.kpi-tile.crit-tile::before {{ background: {C['critical']}; }}
.kpi-tile.warn-tile {{
    background: linear-gradient(140deg, {C['card_bg']} 60%, rgba(210,153,34,0.07));
    border-color: rgba(210,153,34,0.28);
}}
.kpi-tile.warn-tile::before {{ background: {C['warning']}; }}
.kpi-tile.ok-tile::before {{ background: {C['success']}; }}
.kpi-label {{
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: {C['text_dim']};
    margin-bottom: 10px;
}}
.kpi-value {{
    font-size: 2.7rem;
    font-weight: 800;
    color: {C['text_head']};
    line-height: 1;
    margin-bottom: 6px;
    font-variant-numeric: tabular-nums;
    letter-spacing: -1.5px;
}}
.kpi-tile.crit-tile .kpi-value {{ color: {C['critical']}; }}
.kpi-tile.warn-tile .kpi-value  {{ color: {C['warning']}; }}
.kpi-tile.ok-tile   .kpi-value  {{ color: {C['success']}; }}
.kpi-sub {{
    font-size: 0.72rem;
    color: {C['text_dim']};
    line-height: 1.4;
}}

/* ── Status bar ── */
.status-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    background: {C['card_bg']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    margin-bottom: 14px;
    font-size: 0.82rem;
}}
.status-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    display: inline-block;
}}
.status-dot.active {{
    background: {C['success']};
    box-shadow: 0 0 8px {C['success']};
    animation: blink 1.6s ease-in-out infinite;
}}
.status-dot.stopped {{ background: {C['critical']}; opacity: 0.6; }}
@keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.35; }} }}

/* ── SOC Panel ── */
.soc-panel {{
    background: {C['card_bg']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 18px 22px 16px;
    margin-bottom: 14px;
    box-shadow: {C['shadow']};
}}
.panel-label {{
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: {C['text_dim']};
    margin-bottom: 10px;
}}

/* ── Threat bar ── */
.threat-track {{
    background: {C['border_dim']};
    border-radius: 99px;
    height: 6px;
    overflow: hidden;
    margin: 8px 0 4px;
}}
.threat-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}}

/* ── Monitoring stats ── */
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
}}
.stat-cell {{
    padding: 12px 20px;
    border-right: 1px solid {C['border_dim']};
}}
.stat-cell:last-child {{ border-right: none; }}
.stat-label {{
    font-size: 0.63rem;
    color: {C['text_dim']};
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 600;
    margin-bottom: 5px;
}}
.stat-value {{
    font-size: 1.45rem;
    font-weight: 700;
    color: {C['text_head']};
    font-variant-numeric: tabular-nums;
}}

/* ── Log feed ── */
.stTextArea textarea {{
    background: {C['card_alt']} !important;
    color: {C['teal']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
}}

/* ── Selectbox / text input ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {{
    background: {C['card_alt']} !important;
    color: {C['text']} !important;
    border-color: {C['border']} !important;
    border-radius: 8px !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {C['border']};
    border-radius: 10px;
    overflow: hidden;
}}

/* ── Brand / header ── */
.top-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 4px;
}}
.brand-icon {{
    font-size: 2rem;
    filter: drop-shadow(0 0 18px rgba(57,208,179,0.55));
}}
.brand-name {{
    font-size: 1.5rem;
    font-weight: 800;
    color: {C['text_head']};
    letter-spacing: -0.5px;
    line-height: 1;
}}
.brand-sub {{
    font-size: 0.65rem;
    color: {C['text_dim']};
    letter-spacing: 2.2px;
    text-transform: uppercase;
    margin-top: 3px;
}}
.soc-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {C['teal']}44, transparent);
    margin: 8px 0 16px;
}}

/* ── Awareness cards ── */
.aware-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }}
.aware-card {{
    background: {C['card_bg']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: {C['shadow_sm']};
}}
.aware-card h4 {{ margin: 0 0 10px; font-size: 0.92rem; color: {C['text_head']}; }}
.aware-card ul {{ margin: 0; padding-left: 16px; }}
.aware-card ul li {{ margin-bottom: 7px; font-size: 0.82rem; color: {C['text']}; line-height: 1.5; }}
.ethics-card {{
    background: {C['card_bg']};
    border: 1px solid rgba(210,153,34,0.28);
    border-left: 3px solid {C['warning']};
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 0.83rem;
    line-height: 1.6;
    color: {C['text']};
}}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def read_logs() -> str:
    if os.path.exists(kl_core.LOG_FILE):
        with open(kl_core.LOG_FILE, "r") as f:
            return f.read()
    return ""


def chart_layout(height: int = 220) -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=C["chart_bg"],
        font=dict(family="Inter, sans-serif", color=C["text_dim"], size=11),
        margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(
            gridcolor=C["grid"],
            linecolor=C["border"],
            tickcolor=C["border"],
            tickfont=dict(color=C["text_dim"], size=10),
            zerolinecolor=C["border"],
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor=C["grid"],
            linecolor=C["border"],
            tickcolor=C["border"],
            tickfont=dict(color=C["text_dim"], size=10),
            zerolinecolor=C["border"],
            showgrid=True,
        ),
        showlegend=False,
        height=height,
    )


def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
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
    total = len(rows)
    crits = sum(1 for r in rows if r["severity"] == "Critical")
    if total == 0:
        return "No Data", 0, C["text_dim"]
    ratio = crits / total
    if ratio >= 0.4:
        return "HIGH", int(ratio * 100), C["critical"]
    if ratio >= 0.15:
        return "MEDIUM", int(ratio * 100), C["warning"]
    return "LOW", max(4, int(ratio * 100)), C["success"]


def session_duration() -> str:
    if st.session_state.session_start is None:
        return "—"
    delta = datetime.now() - st.session_state.session_start
    h, rem = divmod(int(delta.total_seconds()), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def render_page_header(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div class="top-header">
        <span class="brand-icon">{icon}</span>
        <div>
            <div class="brand-name">{title}</div>
            <div class="brand-sub">{subtitle}</div>
        </div>
    </div>
    <div class="soc-divider"></div>
    """, unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:24px 0 16px;'>
        <div style='font-size:2.1rem; filter:drop-shadow(0 0 20px rgba(57,208,179,0.55));'>🛡️</div>
        <div style='font-size:1.05rem; font-weight:800; letter-spacing:-0.3px; margin-top:8px; color:{C['text_head']};'>SecureWatch</div>
        <div style='font-size:0.60rem; letter-spacing:2.4px; text-transform:uppercase; color:{C['text_dim']}; margin-top:4px;'>SOC Platform v1.0</div>
    </div>
    <div style='height:1px; background:linear-gradient(90deg,transparent,{C['teal']}44,transparent); margin:0 0 16px;'></div>
    <div style='font-size:0.60rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{C['text_dim']}; margin-bottom:8px;'>Navigation</div>
    """, unsafe_allow_html=True)

    pages = {
        "dashboard":  "📊  Dashboard",
        "events":     "📋  Event Queue",
        "logs":       "📄  Raw Log Feed",
        "awareness":  "⚠️  Threat Awareness",
    }
    for key, label in pages.items():
        wrap_cls = "nav-active" if st.session_state.page == key else "nav-item"
        st.markdown(f'<div class="{wrap_cls}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='height:1px; background:{C['border_dim']}; margin:16px 0;'></div>
    <div style='font-size:0.60rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{C['text_dim']}; margin-bottom:8px;'>Agent Controls</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="btn-start">', unsafe_allow_html=True)
    if st.button("▶  Start Monitor"):
        if not st.session_state.running:
            threading.Thread(target=kl_core.start_keylogger, daemon=True).start()
            st.session_state.running = True
            st.session_state.session_start = datetime.now()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="btn-stop">', unsafe_allow_html=True)
    if st.button("■  Stop Monitor"):
        kl_core.stop_keylogger()
        st.session_state.running = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    if st.button("🗑  Clear Logs"):
        kl_core.clear_logs()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div style="height:1px; background:{C["border_dim"]}; margin:16px 0 8px;"></div>', unsafe_allow_html=True)

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
    <div style='font-size:0.62rem; color:{C['text_dim']}; margin-top:16px; line-height:2.0;'>
        <strong style='color:{C['text_dim']};'>SecureWatch SOC</strong><br>
        Research &amp; Training Environment<br>
        Keystroke Threat Monitor<br>
        © 2026 — Lab Use Only
    </div>
    """, unsafe_allow_html=True)


# ─── Load data ────────────────────────────────────────────────────────────────
raw_logs  = read_logs()
all_rows  = build_rows(raw_logs)
sev_count = Counter(r["severity"] for r in all_rows)
sta_count = Counter(r["status"]   for r in all_rows)
now_ts    = datetime.now()
last_24h  = sum(
    1 for r in all_rows
    if r["timestamp"] and r["timestamp"] >= now_ts - timedelta(hours=24)
)
thr_label, thr_pct, thr_color = threat_level(all_rows)
hour_counter = Counter()
for row in all_rows:
    if row["timestamp"]:
        hour_counter[row["timestamp"].strftime("%m-%d %H:00")] += 1


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    render_page_header("🛡️", "SecureWatch SOC", "Threat Intelligence Console")

    dot_cls  = "active" if st.session_state.running else "stopped"
    dot_text = "Active Monitoring" if st.session_state.running else "Monitoring Stopped"
    st.markdown(f"""
    <div class="status-bar">
        <span class="status-dot {dot_cls}"></span>
        <span style="font-weight:600; color:{C['text_head']};">Agent Status:</span>
        <span style="color:{C['success'] if st.session_state.running else C['critical']};">{dot_text}</span>
        <span style="color:{C['border']}; margin:0 4px;">|</span>
        <span style="color:{C['text_dim']};">Session:</span>&nbsp;<span>{session_duration()}</span>
        <span style="color:{C['border']}; margin:0 4px;">|</span>
        <span style="color:{C['text_dim']};">Log File:</span>&nbsp;<span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:{C['teal']};">{kl_core.LOG_FILE}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-tile">
            <div class="kpi-label">Captured Events</div>
            <div class="kpi-value">{len(all_rows)}</div>
            <div class="kpi-sub">total keystroke entries logged</div>
        </div>
        <div class="kpi-tile crit-tile">
            <div class="kpi-label">Critical Alerts</div>
            <div class="kpi-value">{sev_count.get('Critical', 0)}</div>
            <div class="kpi-sub">sensitive inputs flagged</div>
        </div>
        <div class="kpi-tile warn-tile">
            <div class="kpi-label">Pending Triage</div>
            <div class="kpi-value">{sta_count.get('Open', 0)}</div>
            <div class="kpi-sub">cases require analyst review</div>
        </div>
        <div class="kpi-tile ok-tile">
            <div class="kpi-label">24-Hour Window</div>
            <div class="kpi-value">{last_24h}</div>
            <div class="kpi-sub">events in rolling window</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 2.2])

    with left_col:
        st.markdown(f"""
        <div class="soc-panel" style="height:100%;">
            <div class="panel-label">Threat Level</div>
            <div style="font-size:2.4rem; font-weight:900; color:{thr_color}; margin:6px 0 2px; letter-spacing:-1px;">
                {thr_label}
            </div>
            <div class="threat-track">
                <div class="threat-fill" style="width:{thr_pct}%; background:{thr_color};"></div>
            </div>
            <div style="font-size:0.70rem; color:{C['text_dim']}; margin-top:5px;">
                {thr_pct}% critical detection rate
            </div>
            <div style="margin-top:18px; padding-top:14px; border-top:1px solid {C['border_dim']};">
                <div style="font-size:0.60rem; color:{C['text_dim']}; margin-bottom:8px; text-transform:uppercase; letter-spacing:1.4px; font-weight:600;">Breakdown</div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.82rem; margin-bottom:8px;">
                    <span style="display:flex;align-items:center;gap:7px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:{C['critical']};display:inline-block;box-shadow:0 0 6px {C['critical']};"></span>
                        Critical
                    </span>
                    <span style="font-weight:700; color:{C['critical']};">{sev_count.get('Critical', 0)}</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.82rem;">
                    <span style="display:flex;align-items:center;gap:7px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:{C['info']};display:inline-block;"></span>
                        Info
                    </span>
                    <span style="font-weight:700; color:{C['info']};">{sev_count.get('Info', 0)}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Keystroke Activity — Hourly</div>', unsafe_allow_html=True)
        trend_data = dict(sorted(hour_counter.items()))
        if trend_data:
            hours  = list(trend_data.keys())
            counts = list(trend_data.values())
            fig = go.Figure(go.Scatter(
                x=hours, y=counts,
                mode="lines+markers",
                line=dict(color=C["teal"], width=2.5, shape="spline", smoothing=1.1),
                marker=dict(size=5, color=C["teal"], line=dict(width=1.5, color=C["card_bg"])),
                fill="tozeroy",
                fillcolor=hex_to_rgba(C["teal"], 0.10),
                hovertemplate="<b>%{x}</b><br>%{y} events<extra></extra>",
            ))
            fig.update_layout(**chart_layout(240))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No timestamped events yet — start the monitor and press Enter to log a line.")
        st.markdown("</div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Severity Breakdown</div>', unsafe_allow_html=True)
        fig_sev = go.Figure(go.Bar(
            x=["Critical", "Info"],
            y=[sev_count.get("Critical", 0), sev_count.get("Info", 0)],
            marker_color=[C["critical"], C["info"]],
            marker_line_width=0,
            width=0.45,
            hovertemplate="<b>%{x}</b>: %{y}<extra></extra>",
        ))
        fig_sev.update_layout(**chart_layout())
        st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-label">Case Status Overview</div>', unsafe_allow_html=True)
        fig_sta = go.Figure(go.Bar(
            x=["Open", "Reviewed"],
            y=[sta_count.get("Open", 0), sta_count.get("Reviewed", 0)],
            marker_color=[C["warning"], C["success"]],
            marker_line_width=0,
            width=0.45,
            hovertemplate="<b>%{x}</b>: %{y}<extra></extra>",
        ))
        fig_sta.update_layout(**chart_layout())
        st.plotly_chart(fig_sta, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="soc-panel" style="padding:14px 0;">
        <div class="panel-label" style="padding:0 22px 10px;">Monitoring Stats</div>
        <div class="stats-grid">
            <div class="stat-cell">
                <div class="stat-label">Log Entries</div>
                <div class="stat-value">{len([l for l in raw_logs.splitlines() if l.strip()])}</div>
            </div>
            <div class="stat-cell">
                <div class="stat-label">File Size</div>
                <div class="stat-value">{len(raw_logs.encode())} B</div>
            </div>
            <div class="stat-cell">
                <div class="stat-label">Active Hours</div>
                <div class="stat-value">{len(hour_counter)}</div>
            </div>
            <div class="stat-cell">
                <div class="stat-label">Session Duration</div>
                <div class="stat-value">{session_duration()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: EVENT QUEUE
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "events":
    render_page_header("📋", "Event Queue", "Analyst Triage View — All Captured Events")

    st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-label">Filters</div>', unsafe_allow_html=True)

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

    st.markdown(
        f"<div style='font-size:0.78rem; color:{C['text_dim']}; margin:10px 0 6px;'>"
        f"Showing <b style='color:{C['text']};'>{len(filtered)}</b> of "
        f"<b style='color:{C['text']};'>{len(all_rows)}</b> events</div>",
        unsafe_allow_html=True,
    )

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


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: RAW LOG FEED
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "logs":
    render_page_header("📄", "Raw Log Feed", "Live Keystroke Capture Stream — Sensitive Data Masked")

    masked = mask_sensitive(raw_logs)
    st.text_area("Live Log Stream", masked or "(No events captured yet — start the monitor)", height=500)

    if st.session_state.running:
        time.sleep(2)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: THREAT AWARENESS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "awareness":
    render_page_header("⚠️", "Threat Awareness", "Cybersecurity Education & Responsible Disclosure")

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px;">
        <span style="font-size:1.05rem; font-weight:600; color:{C['text_head']};">
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


# ─── Auto-refresh while monitoring (all pages) ────────────────────────────────
if st.session_state.running and st.session_state.page != "logs":
    time.sleep(3)
    st.rerun()