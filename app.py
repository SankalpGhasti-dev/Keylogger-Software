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
    },
    "light": {
        "app_bg":          "#f0f4ff",
        "sidebar_bg":      "#e8eeff",
        "panel_bg":        "rgba(255,255,255,0.92)",
        "panel_border":    "rgba(37,99,235,0.22)",
        "accent":          "#0369a1",
        "accent2":         "#2563eb",
        "danger":          "#dc2626",
        "warning":         "#d97706",
        "success":         "#16a34a",
        "text":            "#1e3050",
        "text_dim":        "#64748b",
        "text_head":       "#0f1e38",
        "metric_val":      "#0369a1",
        "chart_color":     "#2563eb",
        "row_critical":    "rgba(220,38,38,0.10)",
        "row_info":        "rgba(3,105,161,0.06)",
        "logo_glow":       "0 0 22px rgba(37,99,235,0.30)",
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
        radial-gradient(ellipse at 8%  5%,  rgba(0,212,180,0.07) 0%, transparent 38%),
        radial-gradient(ellipse at 92% 8%,  rgba(59,130,246,0.09) 0%, transparent 35%),
        radial-gradient(ellipse at 50% 95%, rgba(59,130,246,0.05) 0%, transparent 40%),
        {t['app_bg']};
    color: {t['text']};
}}
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
.block-container {{ padding: 2rem 1.6rem 2rem; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {t['sidebar_bg']} !important;
    border-right: 1px solid {t['panel_border']} !important;
}}
[data-testid="stSidebar"] * {{ color: {t['text']} !important; }}

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
    background: rgba(0,0,0,0.2);
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
    background: rgba(4,10,22,0.88) !important;
    color: #00d4b4 !important;
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
    box-shadow: 0 0 14px rgba(0,212,180,0.25);
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

/* ── Theme toggle pill ── */
.theme-toggle-wrap {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: {t['panel_bg']};
    border: 1px solid {t['panel_border']};
    border-radius: 999px;
    padding: 4px 6px 4px 14px;
    margin: 4px 0 0;
    cursor: pointer;
    transition: border-color 0.2s ease;
}}
.theme-toggle-wrap:hover {{
    border-color: {t['accent']};
    box-shadow: 0 0 12px rgba(0,212,180,0.2);
}}
.theme-toggle-label {{
    font-size: 0.78rem;
    font-weight: 600;
    color: {t['text_dim']};
    letter-spacing: 0.5px;
}}
.theme-toggle-knob {{
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    background: rgba(0,212,180,0.15);
    border: 1px solid rgba(0,212,180,0.3);
    transition: all 0.3s ease;
    flex-shrink: 0;
}}
/* Collapse the "Toggle Theme" button into a slim invisible strip under the pill */
[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:nth-of-type(6) {{
    height: 24px !important;
    min-height: 24px !important;
    opacity: 0 !important;
    border: none !important;
    background: transparent !important;
    margin: -6px 0 6px !important;
    width: 100%;
    cursor: pointer;
    position: relative;
    z-index: 10;
}}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────
def read_logs() -> str:
    if os.path.exists(kl_core.LOG_FILE):
        with open(kl_core.LOG_FILE, "r") as f:
            return f.read()
    return ""


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


# ─── Sidebar ────────────────────────────────────────────────────────────────
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
    # Single pill toggle: clicking switches theme
    is_dark = st.session_state.theme == "dark"
    knob_icon = "🌙" if is_dark else "☀️"
    toggle_label = "Dark Mode" if is_dark else "Light Mode"
    st.markdown(f"""
    <div class="theme-toggle-wrap" id="theme-toggle-pill" style="margin-bottom:4px;">
        <span class="theme-toggle-label">{toggle_label}</span>
        <span class="theme-toggle-knob">{knob_icon}</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Toggle Theme", key="theme_toggle_btn",
                 help="Switch between Dark and Light mode"):
        st.session_state.theme = "light" if is_dark else "dark"
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
    st.markdown(f"""
    <div class="top-header">
        <span class="logo-icon">🛡️</span>
        <div>
            <div class="product-name">SecureWatch SOC</div>
            <div class="product-sub">Keystroke Threat Intelligence Platform</div>
        </div>
    </div>
    <div class="divider"></div>
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
            st.line_chart(trend_data, color=t["chart_color"])
        else:
            st.info("No timestamped events yet — start the monitor and press Enter to flush lines.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Row 3: Severity bar + Status breakdown
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="soc-panel-title">Severity Distribution</div>', unsafe_allow_html=True)
        st.bar_chart({"Critical": sev_count.get("Critical", 0), "Info": sev_count.get("Info", 0)})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="soc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="soc-panel-title">Triage Status Summary</div>', unsafe_allow_html=True)
        st.bar_chart({"Open": sta_count.get("Open", 0), "Reviewed": sta_count.get("Reviewed", 0)})
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
    st.markdown(f"""
    <div class="top-header">
        <span class="logo-icon">📋</span>
        <div>
            <div class="product-name">Event Queue</div>
            <div class="product-sub">Analyst Triage View — All Captured Events</div>
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="top-header">
        <span class="logo-icon">📄</span>
        <div>
            <div class="product-name">Raw Log Feed</div>
            <div class="product-sub">Live Keystroke Capture Stream — Sensitive Data Masked</div>
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

    masked = mask_sensitive(raw_logs)
    st.text_area("Live Log Stream", masked or "(No events captured yet)", height=480)

    if st.session_state.running:
        time.sleep(2)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: THREAT AWARENESS
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "awareness":
    st.markdown(f"""
    <div class="top-header">
        <span class="logo-icon">⚠️</span>
        <div>
            <div class="product-name">Threat Awareness</div>
            <div class="product-sub">Cybersecurity Education & Responsible Disclosure</div>
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)

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