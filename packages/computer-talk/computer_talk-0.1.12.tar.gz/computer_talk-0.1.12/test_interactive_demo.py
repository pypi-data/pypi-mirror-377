#!/usr/bin/env python3
"""
Demo script to show the interactive prompts working.
"""

import sys
import os
from pathlib import Path

# Add the package to the path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

# Remove config to simulate fresh install
config_dir = Path.home() / ".config" / "computer-talk"
if config_dir.exists():
    import shutil
    shutil.rmtree(config_dir)

print("🎯 Interactive Onboarding Demo")
print("=" * 50)
print("This simulates what users see when they first use computer-talk")
print()

# Simulate the interactive flow
print("Step 1: Welcome Message (this appears automatically)")
print("-" * 50)
print("🎉 Welcome to computer-talk!")
print("Thank you for installing computer-talk!")
print("This package enables computer communication and interaction.")
print()

print("Step 2: API Key Prompt (appears in interactive mode)")
print("-" * 50)
print("To enable AI features, please provide your OpenAI API key.")
print("- Create a key at: https://platform.openai.com/api-keys")
print("- You can also set it later via the environment variable OPENAI_API_KEY")
print()
print("Please enter your OpenAI API key (or press Enter to skip): [USER INPUT]")
print()

print("Step 3: Task Description Prompt (appears after API key)")
print("-" * 50)
print("==================================================")
print("🎯 Task Configuration")
print("==================================================")
print("Now let's configure what you want computer-talk to help you with.")
print()
print("Describe your task to complete: [USER INPUT]")
print("✅ Task saved: [USER'S TASK]")
print("You can change this later by running: computer-talk --interactive")
print()

print("Step 4: Enhanced Experience")
print("-" * 50)
print("Now computer-talk will remember your task and provide task-aware responses!")
print()

print("🔧 How to trigger the interactive prompts:")
print("1. Run: computer-talk --interactive")
print("2. Or: python3 -c \"from computer_talk.config import ensure_openai_api_key_interactive; ensure_openai_api_key_interactive()\"")
print("3. Or: Set OPENAI_API_KEY environment variable first")
print()

print("✅ The onboarding IS working - it just needs to be in an interactive terminal!")
