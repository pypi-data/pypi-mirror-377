import os
import json

SETTINGS_FILE = "settings.json"

def load_settings(path=SETTINGS_FILE):
    """Load settings if available, otherwise return an empty dict."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}
