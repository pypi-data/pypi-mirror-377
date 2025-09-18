"""
Post-installation script for computer-talk package.
This runs automatically after installation to set up the user.
"""

import sys
import os
from pathlib import Path

# Add the package to the path so we can import it
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir.parent))

try:
    from computer_talk.config import ensure_openai_api_key_interactive
except ImportError:
    # If we can't import, just exit silently
    sys.exit(0)


def main():
    """Run post-installation setup."""
    # Only run if we're in an interactive environment
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return
    
    # Check if this is a fresh installation by looking for existing config
    from computer_talk.config import get_user_config_path, get_openai_api_key
    
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
        
        # Run the interactive setup
        ensure_openai_api_key_interactive()
        
        print("\n" + "="*50)
        print("✅ Setup complete! You can now use computer-talk.")
        print("Try: computer-talk --help")
        print("="*50)


if __name__ == "__main__":
    main()
