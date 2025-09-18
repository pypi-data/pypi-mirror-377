#!/usr/bin/env python3
"""
Production testing script for computer-talk package.
This simulates the production experience users will have.
"""

import sys
import os
import subprocess
from pathlib import Path

def test_fresh_installation():
    """Test fresh installation experience."""
    print("🧪 Testing Fresh Installation Experience")
    print("-" * 50)
    
    # Remove config to simulate fresh user
    config_dir = Path.home() / ".config" / "computer-talk"
    if config_dir.exists():
        import shutil
        shutil.rmtree(config_dir)
        print("✅ Removed existing config (simulating fresh user)")
    
    # Test import (should trigger onboarding)
    print("📦 Testing package import...")
    try:
        from computer_talk import ComputerTalk
        print("✅ Package imports successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test CLI
    print("🖥️  Testing CLI...")
    try:
        result = subprocess.run([sys.executable, "-m", "computer_talk.cli", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ CLI version: {result.stdout.strip()}")
        else:
            print(f"❌ CLI failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False
    
    return True

def test_onboarding_flow():
    """Test the onboarding flow."""
    print("\n🧪 Testing Onboarding Flow")
    print("-" * 50)
    
    # Remove config
    config_dir = Path.home() / ".config" / "computer-talk"
    if config_dir.exists():
        import shutil
        shutil.rmtree(config_dir)
    
    # Test onboarding
    print("🎉 Testing welcome message and API key prompt...")
    try:
        from computer_talk.first_run import check_and_run_onboarding
        result = check_and_run_onboarding(force_interactive=False)
        print(f"✅ Onboarding completed: {result}")
        
        # Check if config was created
        if config_dir.exists():
            print("✅ Config directory created")
        else:
            print("❌ Config directory not created")
            return False
            
    except Exception as e:
        print(f"❌ Onboarding failed: {e}")
        return False
    
    return True

def test_api_functionality():
    """Test API functionality."""
    print("\n🧪 Testing API Functionality")
    print("-" * 50)
    
    try:
        from computer_talk import ComputerTalk
        
        # Test context manager
        print("🔄 Testing context manager...")
        with ComputerTalk() as talk:
            print("✅ Context manager works")
            
            # Test status
            status = talk.get_status()
            print(f"✅ Status: Running={status['is_running']}")
            
            # Test message sending
            response = talk.send_message("production test")
            print(f"✅ Message response: {response}")
            
            # Test capabilities
            capabilities = talk.list_capabilities()
            print(f"✅ Capabilities: {len(capabilities)} available")
            
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_cli_commands():
    """Test all CLI commands."""
    print("\n🧪 Testing CLI Commands")
    print("-" * 50)
    
    commands = [
        (["--help"], "Help command"),
        (["--version"], "Version command"),
        (["hello world"], "Message command"),
        (["time"], "Time command"),
        (["status"], "Status command"),
    ]
    
    for cmd, description in commands:
        print(f"🖥️  Testing {description}...")
        try:
            result = subprocess.run([sys.executable, "-m", "computer_talk.cli"] + cmd, 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} works")
            else:
                print(f"❌ {description} failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ {description} failed: {e}")
            return False
    
    return True

def test_config_management():
    """Test config management."""
    print("\n🧪 Testing Config Management")
    print("-" * 50)
    
    try:
        from computer_talk.config import get_user_config_path, get_openai_api_key, set_openai_api_key
        
        # Test config path
        config_path = get_user_config_path()
        print(f"✅ Config path: {config_path}")
        
        # Test setting and getting key
        test_key = "sk-test1234567890"
        set_openai_api_key(test_key)
        retrieved_key = get_openai_api_key()
        
        if retrieved_key == test_key:
            print("✅ API key storage works")
        else:
            print(f"❌ API key storage failed: {retrieved_key}")
            return False
        
        # Test environment variable
        os.environ["OPENAI_API_KEY"] = "sk-env1234567890"
        env_key = get_openai_api_key()
        if env_key == "sk-env1234567890":
            print("✅ Environment variable works")
        else:
            print(f"❌ Environment variable failed: {env_key}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_production_scenarios():
    """Test production scenarios."""
    print("\n🧪 Testing Production Scenarios")
    print("-" * 50)
    
    scenarios = [
        ("Fresh user with no API key", lambda: test_fresh_user_no_key()),
        ("User with environment variable", lambda: test_user_with_env()),
        ("User with config file", lambda: test_user_with_config()),
    ]
    
    for name, test_func in scenarios:
        print(f"🎯 Testing: {name}")
        try:
            if test_func():
                print(f"✅ {name} works")
            else:
                print(f"❌ {name} failed")
                return False
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            return False
    
    return True

def test_fresh_user_no_key():
    """Test fresh user with no API key."""
    # Remove config
    config_dir = Path.home() / ".config" / "computer-talk"
    if config_dir.exists():
        import shutil
        shutil.rmtree(config_dir)
    
    # Clear environment
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    # Test onboarding
    from computer_talk.first_run import check_and_run_onboarding
    result = check_and_run_onboarding(force_interactive=False)
    return result

def test_user_with_env():
    """Test user with environment variable."""
    # Set environment variable
    os.environ["OPENAI_API_KEY"] = "sk-env1234567890"
    
    # Test getting key
    from computer_talk.config import get_openai_api_key
    key = get_openai_api_key()
    return key == "sk-env1234567890"

def test_user_with_config():
    """Test user with config file."""
    # Clear environment
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    # Set config
    from computer_talk.config import set_openai_api_key, get_openai_api_key
    set_openai_api_key("sk-config1234567890")
    key = get_openai_api_key()
    return key == "sk-config1234567890"

def main():
    """Run all production tests."""
    print("🚀 Computer-Talk Production Testing")
    print("=" * 60)
    print("This simulates the production experience users will have")
    print("=" * 60)
    
    tests = [
        test_fresh_installation,
        test_onboarding_flow,
        test_api_functionality,
        test_cli_commands,
        test_config_management,
        test_production_scenarios,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Production Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All production tests passed!")
        print("✅ Your package is ready for production deployment")
        print("\n📝 Next steps:")
        print("1. Update version number in pyproject.toml")
        print("2. Build package: python3 -m build")
        print("3. Upload to TestPyPI: python3 -m twine upload --repository testpypi dist/*")
        print("4. Test installation from TestPyPI")
        print("5. Upload to production PyPI: python3 -m twine upload dist/*")
    else:
        print("❌ Some production tests failed")
        print("Check the output above for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
