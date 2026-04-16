import keyboard
import time
import os

LOG_FILE = 'security__event_log.txt'

# Buffer holds characters between keystrokes until Enter is pressed
logged_line = ""
running = False

# Control keys that produce no printable character to log
NON_PRINTABLE_KEYS = [
    'shift', 'tab', 'alt', 'ctrl', 'left', 'right', 'up', 'down', 'esc',
    'delete', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
    'f11', 'f12', 'caps lock', 'home', 'end', 'page up', 'page down', 'insert',
    'windows', 'num lock', 'scroll lock', 'print screen', 'pause'
]

SENSITIVE_WORDS = ["password", "pass", "otp", "secret", "pin", "passwd"]


def is_sensitive(text):
    """Return True if any sensitive keyword is found in the typed line."""
    return any(word in text.lower() for word in SENSITIVE_WORDS)


def on_key_event(event):
    """Keyboard hook callback. Buffers input and writes complete lines to disk."""
    global logged_line

    if not running:
        return

    if event.event_type != keyboard.KEY_DOWN:
        return

    key_name = event.name.lower()

    if key_name == 'enter':
        if logged_line:
            if is_sensitive(logged_line):
                entry = f"[{time.ctime()}] [ALERT] Sensitive input detected\n"
            else:
                entry = f"[{time.ctime()}] Input: {logged_line}\n"
            try:
                with open(LOG_FILE, 'a') as f:
                    f.write(entry)
            except OSError as e:
                print(f"[ERROR] Could not write log: {e}")
            logged_line = ""

    elif key_name == 'backspace':
        logged_line = logged_line[:-1]

    elif key_name == 'space':
        logged_line += " "

    elif key_name in NON_PRINTABLE_KEYS or len(key_name) > 1:
        return

    else:
        logged_line += key_name


def start_keylogger():
    """Attach the keyboard hook and set the running flag."""
    global running
    running = True
    try:
        keyboard.hook(on_key_event)
    except Exception as e:
        print(f"Cloud Demo Mode: Hardware keylogging blocked by host OS ({e})")


def stop_keylogger():
    """Detach all keyboard hooks and stop logging."""
    global running
    running = False
    try:
        keyboard.unhook_all()
    except Exception:
        pass


def clear_logs():
    """Wipe the log file contents without deleting the file."""
    open(LOG_FILE, "w").close()


if __name__ == "__main__":
    print("=" * 50)
    print("ETHICAL SYSTEM EVENT LOGGER — Line-Buffered Mode")
    print(f"Log destination : {os.path.abspath(LOG_FILE)}")
    print("Type and press ENTER to flush each line.")
    print("Press ESC to quit.")
    print("=" * 50)
    start_keylogger()
    keyboard.wait('esc')
    stop_keylogger()