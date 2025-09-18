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


def get_openai_api_key_masked() -> Optional[str]:
    """Get OpenAI API key with masking for logging."""
    key = get_openai_api_key()
    if key and len(key) > 8:
        return f"{key[:4]}...{key[-4:]}"
    return key


def set_openai_api_key(key: str) -> None:
    """Store OpenAI API key in user config."""
    cfg = load_config()
    cfg[CONFIG_KEY_OPENAI] = key.strip()
    save_config(cfg)


def get_task_description() -> Optional[str]:
    """Get the user's task description from config."""
    cfg = load_config()
    task = cfg.get("task_description")
    if isinstance(task, str) and task.strip():
        return task.strip()
    return None


def set_task_description(task: str) -> None:
    """Store task description in user config."""
    cfg = load_config()
    cfg["task_description"] = task.strip()
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

    print("\n" + "="*60)
    print("🔑 OpenAI API Key Setup")
    print("="*60)
    print("To enable AI features, you need your own OpenAI API key.")
    print()
    print("📋 Steps to get your API key:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (starts with 'sk-')")
    print()
    print("🔒 Security:")
    print("• Your key is stored locally in ~/.config/computer-talk/config.json")
    print("• The file has restricted permissions (600)")
    print("• Never share your API key with others")
    print("• You can also set it via: export OPENAI_API_KEY=your_key")
    print()

    while True:
        entered = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if not entered:
            print("\n⚠️  Skipping API key setup.")
            print("You can set it later with:")
            print("  export OPENAI_API_KEY=your_key_here")
            print("  or run: computer-talk --interactive")
            return None
        
        # Enhanced validation
        if validate_openai_key(entered):
            set_openai_api_key(entered)
            print("\n✅ API key saved successfully!")
            print("📍 Location: ~/.config/computer-talk/config.json")
            print("🔐 Permissions: 600 (owner read/write only)")
            
            # Prompt for task description after API key is set
            print("\n" + "="*60)
            print("🎯 Task Configuration")
            print("="*60)
            print("Now let's configure what you want computer-talk to help you with.")
            print("This helps the AI understand your goals and provide better assistance.")
            print()
            
            while True:
                task_description = input("Describe your task to complete: ").strip()
                if task_description:
                    # Save the task description to config
                    config = load_config()
                    config["task_description"] = task_description
                    save_config(config)
                    print(f"\n✅ Task saved: {task_description}")
                    print("You can change this later by running: computer-talk --interactive")
                    break
                else:
                    print("Please provide a task description to continue.")
            
            return entered
        else:
            print("\n❌ Invalid API key format.")
            print("OpenAI API keys typically:")
            print("• Start with 'sk-'")
            print("• Are 20+ characters long")
            print("• Contain letters, numbers, and sometimes hyphens")
            print("• Example: sk-1234567890abcdef...")
            print()


def validate_openai_key(key: str) -> bool:
    """
    Validate OpenAI API key format.
    
    Args:
        key: The API key to validate
        
    Returns:
        True if the key appears valid, False otherwise
    """
    if not key or not isinstance(key, str):
        return False
    
    key = key.strip()
    
    # Basic format validation
    if not key.startswith("sk-"):
        return False
    
    if len(key) < 20:
        return False
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    import re
    if not re.match(r'^sk-[a-zA-Z0-9_-]+$', key):
        return False
    
    return True


