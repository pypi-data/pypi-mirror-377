#!/usr/bin/env python3
"""
Demo script that simulates the CLI behavior with interactive onboarding.
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

print("=== Computer Talk CLI Demo ===")
print("This simulates running: computer-talk --interactive")
print()

# Simulate the CLI behavior
from computer_talk.first_run import check_and_run_onboarding

# This should show the interactive prompt
print("Running onboarding check...")
result = check_and_run_onboarding(force_interactive=True)
print(f"Onboarding completed: {result}")

if result:
    print("\nNow the CLI would continue with normal operation...")
    print("Try running: computer-talk --interactive")
else:
    print("\nOnboarding was skipped (config already exists)")
