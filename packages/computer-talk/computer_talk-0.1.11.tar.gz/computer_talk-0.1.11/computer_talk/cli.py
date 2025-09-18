"""
Command-line interface for computer-talk.
"""

import argparse
import sys
import json
from typing import Optional

# Check for onboarding BEFORE importing anything that might create config
from .first_run import check_and_run_onboarding

from .core import ComputerTalk
from .exceptions import ComputerTalkError
from .config import get_openai_api_key, get_task_description


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Computer Talk - A Python package for computer communication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="computer-talk 0.1.0"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start in interactive mode"
    )
    
    parser.add_argument(
        "--reset-key",
        action="store_true",
        help="Reset/change your OpenAI API key"
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        help="Message to send (non-interactive mode)"
    )
    
    args = parser.parse_args()
    
    # Handle reset key command
    if args.reset_key:
        from .config import ensure_openai_api_key_interactive
        print("🔑 Resetting OpenAI API Key")
        print("="*40)
        ensure_openai_api_key_interactive()
        return
    
    # Check for first run and run onboarding if needed
    # Force interactive mode if --interactive flag is used
    check_and_run_onboarding(force_interactive=args.interactive)
    
    # Load configuration
    config = {"log_level": args.log_level}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            sys.exit(1)

    # Add OpenAI API key if available
    key = get_openai_api_key()
    if key:
        config["openai_api_key"] = key
    
    # Create ComputerTalk instance
    try:
        talk = ComputerTalk(config)
        talk.start()
        
        if args.interactive:
            run_interactive_mode(talk)
        elif args.message:
            response = talk.send_message(args.message)
            print(response)
        else:
            # Show status
            status = talk.get_status()
            print(json.dumps(status, indent=2))
            
    except ComputerTalkError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if 'talk' in locals():
            try:
                talk.stop()
            except ComputerTalkError:
                pass


def run_interactive_mode(talk: ComputerTalk) -> None:
    """Run interactive mode."""
    print("Computer Talk - Interactive Mode")
    print("Type 'help' for commands, 'quit' to exit")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'status':
                status = talk.get_status()
                print(json.dumps(status, indent=2))
                continue
            elif user_input.lower() == 'capabilities':
                capabilities = talk.list_capabilities()
                print("Available capabilities:")
                for cap in capabilities:
                    print(f"  - {cap}")
                continue
            elif user_input.lower() == 'apps':
                apps = talk.list_apps()
                print("Available applications:")
                for app in apps[:10]:
                    print(f"  - {app['name']}: {app['description']}")
                continue
            elif user_input.lower() == 'running':
                apps = talk.list_running_apps()
                print("Currently running applications:")
                for app in apps[:10]:
                    print(f"  - {app['name']}")
                continue
            
            # Send message
            response = talk.send_message(user_input)
            print(f"Response: {response}")
            
        except KeyboardInterrupt:
            break
        except ComputerTalkError as e:
            print(f"Error: {e}")
        except EOFError:
            break


def print_help() -> None:
    """Print help information."""
    help_text = """
Available commands:
  help          - Show this help message
  status        - Show current status
  capabilities  - List available capabilities
  apps          - List available applications
  running       - List currently running applications
  quit/exit/q   - Exit the program
  
Desktop app commands:
  open <app>    - Open an application (e.g., "open Safari")
  close <app>   - Close an application (e.g., "close Safari")
  list apps     - List available applications
  running apps  - List running applications

Task commands:
  task          - Show current task
  clear task    - Clear current task
  
Any other input will be sent as a message to the computer.
    """
    print(help_text.strip())


if __name__ == "__main__":
    main()
