"""
plugin_config.py
================
Manages plugin configuration: enabled/disabled state and custom icons.
Config is stored in plugins/plugins_config.json.
"""

import json
import os

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "plugins", "plugins_config.json"
)


def _load() -> dict:
    if os.path.isfile(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(config: dict):
    os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def is_enabled(folder: str) -> bool:
    """Returns True if the plugin is enabled (default: True)."""
    return _load().get(folder, {}).get("enabled", True)


def set_enabled(folder: str, enabled: bool):
    config = _load()
    if folder not in config:
        config[folder] = {}
    config[folder]["enabled"] = enabled
    _save(config)


def get_icon(folder: str, default_icon_path: str) -> str:
    """
    Returns the effective icon path for a plugin.
    If the user has set a custom icon, returns that path.
    Falls back to the plugin's default icon.
    """
    custom = _load().get(folder, {}).get("custom_icon")
    if custom and os.path.isfile(custom):
        return custom
    return default_icon_path


def set_icon(folder: str, icon_path: str):
    config = _load()
    if folder not in config:
        config[folder] = {}
    config[folder]["custom_icon"] = icon_path
    _save(config)


def get_all() -> dict:
    """Returns the entire config dict."""
    return _load()
