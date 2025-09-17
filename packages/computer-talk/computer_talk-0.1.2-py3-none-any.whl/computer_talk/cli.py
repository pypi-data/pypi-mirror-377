"""
Command-line interface for computer-talk.
"""

import argparse
import sys
import json
from typing import Optional

from .core import ComputerTalk
from .exceptions import ComputerTalkError


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
        "message",
        nargs="?",
        help="Message to send (non-interactive mode)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = {"log_level": args.log_level}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            sys.exit(1)
    
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
  quit/exit/q   - Exit the program
  
Any other input will be sent as a message to the computer.
    """
    print(help_text.strip())


if __name__ == "__main__":
    main()
