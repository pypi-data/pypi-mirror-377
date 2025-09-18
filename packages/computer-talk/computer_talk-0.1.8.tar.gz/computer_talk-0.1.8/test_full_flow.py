#!/usr/bin/env python3
"""
Test the full onboarding flow by simulating a fresh installation.
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

print("=== Testing Full Onboarding Flow ===")
print("This simulates what happens when a user first installs computer-talk")
print()

# Test 1: Import should trigger onboarding
print("1. Testing import-triggered onboarding...")
from computer_talk import ComputerTalk
print("Import completed")
print()

# Test 2: CLI should not trigger onboarding again (config exists)
print("2. Testing CLI after config exists...")
from computer_talk.first_run import check_and_run_onboarding
result = check_and_run_onboarding(force_interactive=True)
print(f"Onboarding result: {result}")
print()

# Test 3: Fresh install simulation
print("3. Testing fresh install simulation...")
config_dir = Path.home() / ".config" / "computer-talk"
if config_dir.exists():
    import shutil
    shutil.rmtree(config_dir)

# Now test the interactive prompt directly
from computer_talk.config import ensure_openai_api_key_interactive
print("This should now prompt for your API key:")
key = ensure_openai_api_key_interactive()
print(f"Got key: {key[:10]}..." if key else "No key provided")
