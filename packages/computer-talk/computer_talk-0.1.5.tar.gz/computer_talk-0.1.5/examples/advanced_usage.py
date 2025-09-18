#!/usr/bin/env python3
"""
Advanced usage example for computer-talk package.
"""

import json
import time
from computer_talk import ComputerTalk


def main():
    """Demonstrate advanced usage of ComputerTalk."""
    print("Computer Talk - Advanced Usage Example")
    print("=" * 45)
    
    # Create ComputerTalk with custom configuration
    config = {
        "log_level": "DEBUG",
        "timeout": 30,
        "custom_setting": "example_value"
    }
    
    talk = ComputerTalk(config)
    
    try:
        # Start the system
        talk.start()
        print("✓ ComputerTalk started with custom config")
        
        # Demonstrate different message types
        test_scenarios = [
            {
                "name": "Greeting Messages",
                "messages": ["hello", "hi there", "good morning"]
            },
            {
                "name": "Time Queries", 
                "messages": ["time", "what time is it?", "current time"]
            },
            {
                "name": "Status Queries",
                "messages": ["status", "how are you?", "system status"]
            },
            {
                "name": "Echo Messages",
                "messages": ["test message", "echo this", "repeat after me"]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n--- {scenario['name']} ---")
            for message in scenario['messages']:
                response = talk.send_message(message)
                print(f"  {message} → {response}")
                time.sleep(0.1)  # Small delay for demonstration
        
        # Show detailed status
        print(f"\n--- Detailed Status ---")
        status = talk.get_status()
        print(json.dumps(status, indent=2))
        
        # Show capabilities
        print(f"\n--- Capabilities ---")
        capabilities = talk.list_capabilities()
        for i, cap in enumerate(capabilities, 1):
            print(f"  {i}. {cap}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        talk.stop()
        print("\n✓ ComputerTalk stopped")


def performance_test():
    """Test performance with multiple messages."""
    print("\n" + "=" * 45)
    print("Performance Test")
    print("=" * 45)
    
    with ComputerTalk() as talk:
        num_messages = 100
        start_time = time.time()
        
        for i in range(num_messages):
            response = talk.send_message(f"test message {i}")
            if i % 20 == 0:
                print(f"  Processed {i} messages...")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ Processed {num_messages} messages in {duration:.2f} seconds")
        print(f"  Average: {duration/num_messages*1000:.2f} ms per message")


if __name__ == "__main__":
    main()
    performance_test()
