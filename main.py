import os
import time
import threading
from datetime import datetime
import pyautogui
import keyboard  # listens to hotkeys

CAPTURE_INTERVAL = 5.0  # seconds

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def timestamped_filename(prefix="screenshot", ext="png"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{prefix}_{ts}.{ext}"

def monitor_stop_listener(stop_event):
    """
    1.Sequence: press Ctrl+Shift+Tab, then S, then Q 
    """
    # Quick hotkey
    #sqkeyboard.add_hotkey('ctrl+shift+q', lambda: stop_event.set())

    # Sequence detection
    sequence = ['ctrl+shift+tab', 's', 'q']
    seq_index = {'i': 0}
    last_time = {'t': None}
    seq_timeout = 3.0  # seconds to complete the sequence

    def on_key(e):
        name = e.name
        now = time.time()
        i = seq_index['i']

        # When the first element is the combo ctrl+shift+tab, check for it
        if i == 0 and keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift') and name == 'tab':
            seq_index['i'] = 1
            last_time['t'] = now
            print("[HOTKEY] Sequence: detected Ctrl+Shift+Tab -> press 'S' then 'Q' within 3s.")
            return

        # If sequence started, check next keys
        if i == 1:
            if now - last_time['t'] > seq_timeout:
                seq_index['i'] = 0
                return
            if name == 's':
                seq_index['i'] = 2
                last_time['t'] = now
                print("[HOTKEY] Sequence: detected 'S' -> press 'Q' now.")
                return

        if i == 2:
            if now - last_time['t'] > seq_timeout:
                seq_index['i'] = 0
                return
            if name == 'q':
                print("[HOTKEY] Sequence complete. Stopping monitor.")
                stop_event.set()
                return

    # Register low-level hook
    keyboard.on_press(on_key)

    # Block until stop_event is set
    while not stop_event.is_set():
        time.sleep(0.2)

def main():
    target = r"CHANGE THIS TO THE DIRECTORY WHERE YOU WOULD LIKE TO SAVE YOUR SCREENSHOTS"
   
    stop_event = threading.Event()
    listener_thread = threading.Thread(target=monitor_stop_listener, args=(stop_event,), daemon=True)
    listener_thread.start()

    try:
        count = 0
        while not stop_event.is_set():
            filename = timestamped_filename()
            filepath = os.path.join(target, filename)

            # Take screenshot (pyautogui uses Pillow internally)
            image = pyautogui.screenshot()
            image.save(filepath)

            count += 1
            #print(f"[{datetime.now().isoformat(timespec='seconds')}] Saved {filepath} (#{count})")   #you can change this to print output if you want 

            # wait in small increments to respond quickly to stop_event
            slept = 0.0
            while slept < CAPTURE_INTERVAL and not stop_event.is_set():
                time.sleep(0.25)
                slept += 0.25

        print("\nExiting monitor.")
    except KeyboardInterrupt:
        print("\nStopped by user (KeyboardInterrupt). Exiting.")
    except Exception as e:
        print(f"\nError: {e}. Exiting.")
    finally:
        stop_event.set()
        
        time.sleep(0.2)

if __name__ == "__main__":
    main()
