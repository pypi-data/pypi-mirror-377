"""
First run setup for computer-talk package.
This runs when the user first uses the package.
"""

import sys
import os
from pathlib import Path

# Add the package to the path so we can import it
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir.parent))

try:
    from computer_talk.config import ensure_openai_api_key_interactive, get_user_config_path, get_openai_api_key
except ImportError:
    # If we can't import, just exit silently
    sys.exit(0)


def check_and_run_onboarding(force_interactive=False):
    """Check if onboarding is needed and run it if so."""
    # Check if this is a fresh installation by looking for existing config
    config_path = get_user_config_path()
    existing_key = get_openai_api_key()
    
    # Only show onboarding if no config exists and no key is set
    if not config_path.exists() and not existing_key:
        print("\n" + "="*50)
        print("🎉 Welcome to computer-talk!")
        print("="*50)
        print("Thank you for installing computer-talk!")
        print("This package enables computer communication and interaction.")
        print()
        
        # Run interactive setup if forced or in interactive environment
        if force_interactive or (sys.stdin.isatty() and sys.stdout.isatty()):
            # Run the interactive setup
            ensure_openai_api_key_interactive()
        else:
            print("To enable AI features, set your OpenAI API key:")
            print("  export OPENAI_API_KEY=your_key_here")
            print("  or run: computer-talk --interactive")
        
        print("\n" + "="*50)
        print("✅ Setup complete! You can now use computer-talk.")
        print("Try: computer-talk --help")
        print("="*50)
        return True
    
    return False


if __name__ == "__main__":
    check_and_run_onboarding()
