#!/usr/bin/env python3
"""
Desktop integration demo for computer-talk package.
Shows how to open and interact with desktop applications.
"""

from computer_talk import ComputerTalk


def main():
    """Demonstrate desktop app integration."""
    print("🖥️  Computer-Talk Desktop Integration Demo")
    print("=" * 50)
    
    with ComputerTalk() as talk:
        print("✅ ComputerTalk started with desktop capabilities")
        
        # Show capabilities
        capabilities = talk.list_capabilities()
        print(f"\n📋 Available capabilities: {capabilities}")
        
        # List available apps
        print("\n📱 Available applications:")
        apps = talk.list_apps()
        for app in apps[:5]:  # Show first 5 apps
            print(f"  • {app['name']}: {app['description']}")
        
        # List running apps
        print("\n🔄 Currently running applications:")
        running_apps = talk.list_running_apps()
        for app in running_apps[:5]:  # Show first 5 running apps
            print(f"  • {app['name']}")
        
        # Demo app opening
        print("\n🚀 Demo: Opening applications")
        test_apps = ["Safari", "Terminal", "TextEdit"]
        
        for app_name in test_apps:
            try:
                print(f"\nOpening {app_name}...")
                result = talk.open_app(app_name)
                print(f"✅ {result['message']}")
                
                # Wait a moment
                import time
                time.sleep(1)
                
                # Try to interact with the app
                print(f"Interacting with {app_name}...")
                interaction = talk.interact_with_app(app_name, "activate")
                print(f"✅ {interaction['message']}")
                
            except Exception as e:
                print(f"❌ Failed to open {app_name}: {e}")
        
        # Demo message-based app control
        print("\n💬 Demo: Message-based app control")
        messages = [
            "list apps",
            "running apps", 
            "open Calculator",
            "close Calculator"
        ]
        
        for message in messages:
            print(f"\nSending: {message}")
            response = talk.send_message(message)
            print(f"Response: {response}")
    
    print("\n✅ Desktop integration demo completed!")


def interactive_demo():
    """Interactive demo of desktop capabilities."""
    print("\n🎮 Interactive Desktop Demo")
    print("=" * 30)
    print("Try these commands:")
    print("  • open Safari")
    print("  • open Terminal") 
    print("  • list apps")
    print("  • running apps")
    print("  • close Safari")
    print()
    
    with ComputerTalk() as talk:
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


if __name__ == "__main__":
    main()
    interactive_demo()
