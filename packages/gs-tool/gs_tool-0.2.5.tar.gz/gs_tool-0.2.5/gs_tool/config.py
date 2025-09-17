import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / '.gs_tool'
CONFIG_FILE = CONFIG_DIR / 'config.json'

DEFAULT_CONFIG = {
    'server_url': 'http://127.0.0.1:8000',
    'api_key': 'your_api_key_here'
}

def load_config():
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2) 