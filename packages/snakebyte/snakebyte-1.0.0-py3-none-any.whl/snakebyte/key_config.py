import curses
import json
import os
from .config import key_config_path

DEFAULT_KEYS = {
    "pause": ["p"],
    "quit": ["q"],
    "instructions": ["i"],
    "up": ["w", "UP"],
    "down": ["s", "DOWN"],
    "left": ["a", "LEFT"],
    "right": ["d", "RIGHT"]
}

KEY_BINDINGS = {}

def load_key_config(path=key_config_path)->None:
    global KEY_BINDINGS
    KEY_BINDINGS.clear()

    if os.path.exists(path):
        with open(path, "r") as f:
            user_keys = json.load(f)
    else:
        user_keys = {}

    for action, defaults in DEFAULT_KEYS.items():
        keys = user_keys.get(action, defaults)
        if not isinstance(keys, list):
            keys = [keys]

        final_keys = []
        for key in keys:
            if len(key) == 1:
                final_keys.append(ord(key.lower()))
            elif key.upper() in ("UP", "DOWN", "LEFT", "RIGHT"):
                final_keys.append(getattr(curses, f"KEY_{key.upper()}"))
        KEY_BINDINGS[action] = final_keys
