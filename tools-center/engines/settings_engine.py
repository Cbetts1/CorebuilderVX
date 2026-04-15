"""
settings_engine.py — Tools Center settings engine.

Loads, saves, and provides access to settings.json.
Provides typed getters with defaults.
"""

import os
import json
from typing import Any

_SETTINGS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "settings", "settings.json"
)

_settings: dict = {}
_loaded: bool = False


def load():
    """Load settings from settings.json into memory."""
    global _settings, _loaded
    path = _SETTINGS_FILE
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            _settings = json.load(f)
    else:
        _settings = _defaults()
        save()
    _loaded = True


def save():
    """Persist the current in-memory settings to settings.json."""
    os.makedirs(os.path.dirname(_SETTINGS_FILE), exist_ok=True)
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(_settings, f, indent=2)


def get(key: str, default: Any = None) -> Any:
    """Return a setting value by key, with optional default."""
    if not _loaded:
        load()
    return _settings.get(key, default)


def set(key: str, value: Any):
    """Set a setting value and persist immediately."""
    if not _loaded:
        load()
    _settings[key] = value
    save()


def all_settings() -> dict:
    """Return a copy of all settings."""
    if not _loaded:
        load()
    return dict(_settings)


def reset_to_defaults():
    """Reset all settings to their default values and save."""
    global _settings
    _settings = _defaults()
    save()


def _defaults() -> dict:
    return {
        "theme": "default",
        "simulation_mode": False,
        "colour_enabled": True,
        "debug_mode": False,
        "default_shell": "/bin/sh",
        "log_level": "INFO",
        "cloud_provider": "local",
        "vdrive_default_size_mb": 512,
        "ai_model": "llama",
        "editor": "nano",
    }
