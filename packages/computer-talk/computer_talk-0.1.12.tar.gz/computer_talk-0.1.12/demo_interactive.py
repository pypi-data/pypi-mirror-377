#!/usr/bin/env python3
"""
Demo script to show the interactive API key prompt.
"""

import sys
import os
from pathlib import Path

# Add the package to the path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

# Remove any existing config
config_dir = Path.home() / ".config" / "computer-talk"
if config_dir.exists():
    import shutil
    shutil.rmtree(config_dir)

# Import and test the interactive function directly
from computer_talk.config import ensure_openai_api_key_interactive

print("Testing interactive API key prompt...")
print("This will ask you to enter your OpenAI API key.")
print("You can press Enter to skip or enter a test key like 'sk-test123...'")
print()

# This should prompt for the API key
key = ensure_openai_api_key_interactive()
print(f"Got key: {key[:10]}..." if key else "No key provided")
