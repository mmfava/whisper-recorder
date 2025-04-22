"""
Configuration management for whisper_recorder.
"""
import json
import os
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "whisper_recorder"

def get_config_file() -> Path:
    """
    Determine the configuration file path.
    If XDG_CONFIG_HOME is set, use that directory directly; otherwise use platformdirs.user_config_dir(APP_NAME).
    Returns a Path to 'config.json'.
    """
    # Respect XDG_CONFIG_HOME for overrides (e.g., in tests)
    cfg_home = os.getenv('XDG_CONFIG_HOME')
    if cfg_home:
        cfg_dir = Path(cfg_home)
    else:
        cfg_dir = Path(user_config_dir(APP_NAME))
    return cfg_dir / "config.json"

def save_config(config: dict) -> None:
    """
    Save configuration dict to JSON file under user config directory.
    """
    config_path = get_config_file()
    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def load_config() -> dict:
    """
    Load configuration from JSON file.
    """
    config_path = get_config_file()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))