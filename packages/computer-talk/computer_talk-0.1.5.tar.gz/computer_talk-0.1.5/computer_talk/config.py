"""
User configuration management for computer-talk.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


CONFIG_DIR_NAME = "computer-talk"
CONFIG_FILE_NAME = "config.json"
CONFIG_KEY_OPENAI = "openai_api_key"


def get_user_config_dir() -> Path:
    """Return the user config directory path, preferring ~/.config/computer-talk."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / CONFIG_DIR_NAME
    # Default
    return Path.home() / ".config" / CONFIG_DIR_NAME


def get_user_config_path() -> Path:
    """Return the full path to the user config file."""
    return get_user_config_dir() / CONFIG_FILE_NAME


def load_config() -> Dict[str, Any]:
    """Load config JSON if present, else return empty dict."""
    path = get_user_config_path()
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Persist config to disk with secure permissions."""
    cfg_dir = get_user_config_dir()
    cfg_dir.mkdir(parents=True, exist_ok=True)
    path = get_user_config_path()
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    os.replace(tmp_path, path)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from env or config."""
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key
    cfg = load_config()
    key = cfg.get(CONFIG_KEY_OPENAI)
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def set_openai_api_key(key: str) -> None:
    """Store OpenAI API key in user config."""
    cfg = load_config()
    cfg[CONFIG_KEY_OPENAI] = key.strip()
    save_config(cfg)


def ensure_openai_api_key_interactive() -> Optional[str]:
    """
    Ensure an OpenAI API key is available. If missing and running in an interactive
    TTY, prompt the user and save the key. Returns the key or None if unavailable.
    """
    key = get_openai_api_key()
    if key:
        return key

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        # Non-interactive; don't prompt
        return None

    print("\nWelcome to computer-talk!\n")
    print("To enable AI features, please provide your OpenAI API key.")
    print("- Create a key at: https://platform.openai.com/api-keys")
    print("- You can also set it later via the environment variable OPENAI_API_KEY")

    while True:
        entered = input("Please enter your OpenAI API key (or press Enter to skip): ").strip()
        if not entered:
            print("Skipping API key setup. You can set it later with 'export OPENAI_API_KEY=...'")
            return None
        if entered.startswith("sk-") and len(entered) >= 20:
            set_openai_api_key(entered)
            print("Thanks! Your key has been saved in ~/.config/computer-talk/config.json")
            return entered
        else:
            print("That doesn't look like a valid key. It usually starts with 'sk-'. Try again.")


