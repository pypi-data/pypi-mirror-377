#!/usr/bin/env python3
"""
Test script to demonstrate the interactive onboarding.
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

# Now test the onboarding
from computer_talk.first_run import check_and_run_onboarding

print("Testing interactive onboarding...")
result = check_and_run_onboarding(force_interactive=True)
print(f"Onboarding result: {result}")
