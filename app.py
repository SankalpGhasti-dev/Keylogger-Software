import streamlit as st
import keylogger_software as keylogger_core 
import os
import time
import threading

st.set_page_config(page_title="Keylogger Dashboard", layout="wide")

if "running" not in st.session_state:
    st.session_state.running = False

# ------------------ HEADER ------------------
st.title("🔐 Keylogger Monitoring Dashboard")
st.caption("⚠️ Educational Purpose Only | Cybersecurity Mini Project")

# ------------------ SESSION STATE ------------------
if "running" not in st.session_state:
    st.session_state.running = False

# ------------------ CONTROL PANEL ------------------
st.subheader("🎛 Control Panel")

col1, col2, col3 = st.columns(3)

# START
def run_logger():
    keylogger_core.start_keylogger()

if col1.button("▶️ Start Logging"):
    if not st.session_state.get("running", False):
        thread = threading.Thread(target=run_logger, daemon=True)
        thread.start()
        st.session_state.running = True
        st.success("Started")

# STOP
if col2.button("⏹ Stop Logging"):
    keylogger_core.stop_keylogger()
    st.session_state.running = False
    st.warning("Stopped")

# CLEAR
if col3.button("🗑 Clear Logs"):
    keylogger_core.clear_logs()
    st.info("Logs Cleared")

# ------------------ STATUS ------------------
st.markdown(f"**Status:** {'🟢 Running' if st.session_state.running else '🔴 Stopped'}")

# ------------------ LOG DISPLAY ------------------
st.subheader("📄 Captured Logs")

log_placeholder = st.empty()

def mask_sensitive_data(text):
    sensitive_words = ["password", "pass", "otp", "secret"]
    for word in sensitive_words:
        text = text.replace(word, "*" * len(word))
    return text

def read_logs():
    if os.path.exists(keylogger_core.LOG_FILE):
        with open(keylogger_core.LOG_FILE, "r") as f:
            return f.read()
    return ""

logs = read_logs()
masked_logs = mask_sensitive_data(logs)

log_placeholder.text_area("Logs", masked_logs, height=300)

# ------------------ AUTO REFRESH ------------------
if st.session_state.running:
    time.sleep(2)
    st.rerun()

# ------------------ STATS ------------------
st.subheader("📊 Stats")

lines = logs.split("\n")
num_lines = len([l for l in lines if l.strip() != ""])
num_chars = len(logs)

col1, col2 = st.columns(2)
col1.metric("Total Entries", num_lines)
col2.metric("Total Characters Logged", num_chars)

# ------------------ DOWNLOAD ------------------
st.subheader("⬇️ Export Logs")

if os.path.exists(keylogger_core.LOG_FILE):
    with open(keylogger_core.LOG_FILE, "rb") as f:
        st.download_button(
            label="Download Log File",
            data=f,
            file_name="keylogger_logs.txt"
        )

# ------------------ FILE INFO ------------------
st.subheader("📁 Log File Info")

st.write(f"Path: `{"Log Location: 🔒 Hidden for security reasons"}`")

# ------------------ AWARENESS ------------------
st.subheader("⚠️ Cybersecurity Awareness")

st.markdown("""
### 🔍 How Keyloggers Work
- Capture keyboard inputs silently
- Store or transmit sensitive data

### 🛡️ Prevention Tips
- Install trusted software only
- Use antivirus & firewall
- Monitor startup programs
- Use virtual keyboards for sensitive input

### 🧠 Ethical Note
This project is built strictly for educational purposes to understand system vulnerabilities and improve security awareness.
""")