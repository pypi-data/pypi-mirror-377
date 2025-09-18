#!/usr/bin/env python3
"""
Quick start script for computer-talk package.
This script demonstrates the basic functionality.
"""

from computer_talk import ComputerTalk


def main():
    """Quick demonstration of ComputerTalk functionality."""
    print("🚀 Computer Talk - Quick Start")
    print("=" * 35)
    
    # Use as context manager for automatic cleanup
    with ComputerTalk() as talk:
        print("✅ ComputerTalk is running!")
        
        # Interactive demo
        print("\nTry these commands:")
        print("  • 'hello' - Get a greeting")
        print("  • 'time' - Get current time") 
        print("  • 'status' - Get system status")
        print("  • 'quit' - Exit")
        print("\n" + "-" * 35)
        
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if user_input:
                    response = talk.send_message(user_input)
                    print(f"🤖 Computer: {response}")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    print("\n👋 Thanks for using Computer Talk!")


if __name__ == "__main__":
    main()
