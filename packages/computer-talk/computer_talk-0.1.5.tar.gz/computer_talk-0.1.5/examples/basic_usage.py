#!/usr/bin/env python3
"""
Basic usage example for computer-talk package.
"""

from computer_talk import ComputerTalk


def main():
    """Demonstrate basic usage of ComputerTalk."""
    print("Computer Talk - Basic Usage Example")
    print("=" * 40)
    
    # Create a ComputerTalk instance
    talk = ComputerTalk()
    
    try:
        # Start the system
        print("Starting ComputerTalk...")
        talk.start()
        print("✓ ComputerTalk started")
        
        # Send some messages
        messages = [
            "Hello, computer!",
            "What time is it?",
            "What's your status?",
            "Echo this message"
        ]
        
        for message in messages:
            print(f"\nSending: {message}")
            response = talk.send_message(message)
            print(f"Response: {response}")
        
        # Show capabilities
        print(f"\nAvailable capabilities: {talk.list_capabilities()}")
        
        # Show status
        status = talk.get_status()
        print(f"\nStatus: {status}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always stop the system
        print("\nStopping ComputerTalk...")
        talk.stop()
        print("✓ ComputerTalk stopped")


def context_manager_example():
    """Demonstrate using ComputerTalk as a context manager."""
    print("\n" + "=" * 40)
    print("Context Manager Example")
    print("=" * 40)
    
    # Using as context manager (automatic cleanup)
    with ComputerTalk() as talk:
        print("✓ ComputerTalk started automatically")
        
        response = talk.send_message("Hello from context manager!")
        print(f"Response: {response}")
        
        print("✓ ComputerTalk will stop automatically")
    
    print("✓ ComputerTalk stopped automatically")


if __name__ == "__main__":
    main()
    context_manager_example()
