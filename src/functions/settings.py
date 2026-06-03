import json
from pathlib import Path

from src.functions.init import get_workspace_path

_DEFAULTS = {"stt_mode": "push-to-talk"}
_settings = None


def _settings_path() -> Path:
    return get_workspace_path() / "settings.json"


def load_settings():
    global _settings
    path = _settings_path()
    if path.exists():
        try:
            _settings = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            _settings = _DEFAULTS.copy()
    else:
        _settings = _DEFAULTS.copy()
    return _settings


def get_setting(key: str):
    if _settings is None:
        load_settings()
    return _settings.get(key, _DEFAULTS.get(key))


def set_setting(key: str, value):
    if _settings is None:
        load_settings()
    _settings[key] = value
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(json.dumps(_settings, indent=2) + "\n")
    except OSError:
        pass
