#!/usr/bin/env python3
"""
Local testing script for computer-talk package.
Run this to test all functionality locally.
"""

import sys
import os
from pathlib import Path

def test_import():
    """Test package import."""
    print("🧪 Testing package import...")
    try:
        from computer_talk import ComputerTalk
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test config functionality."""
    print("\n🧪 Testing config functionality...")
    try:
        from computer_talk.config import get_user_config_path, get_openai_api_key, set_openai_api_key
        
        # Test config path
        config_path = get_user_config_path()
        print(f"✅ Config path: {config_path}")
        
        # Test getting key (should be None for fresh install)
        key = get_openai_api_key()
        print(f"✅ Current key: {key[:10] + '...' if key else 'None'}")
        
        # Test setting a test key
        set_openai_api_key("sk-test1234567890")
        new_key = get_openai_api_key()
        print(f"✅ Set test key: {new_key[:10] + '...' if new_key else 'None'}")
        
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_core():
    """Test core functionality."""
    print("\n🧪 Testing core functionality...")
    try:
        from computer_talk import ComputerTalk
        
        # Test context manager
        with ComputerTalk() as talk:
            print("✅ Context manager works")
            
            # Test status
            status = talk.get_status()
            print(f"✅ Status: {status['is_running']}")
            
            # Test message sending
            response = talk.send_message("hello")
            print(f"✅ Message response: {response}")
            
            # Test capabilities
            capabilities = talk.list_capabilities()
            print(f"✅ Capabilities: {len(capabilities)} available")
            
        return True
    except Exception as e:
        print(f"❌ Core test failed: {e}")
        return False

def test_cli():
    """Test CLI functionality."""
    print("\n🧪 Testing CLI functionality...")
    try:
        import subprocess
        
        # Test help
        result = subprocess.run([sys.executable, "-m", "computer_talk.cli", "--help"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI help works")
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
            
        # Test version
        result = subprocess.run([sys.executable, "-m", "computer_talk.cli", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI version works")
        else:
            print(f"❌ CLI version failed: {result.stderr}")
            return False
            
        # Test message
        result = subprocess.run([sys.executable, "-m", "computer_talk.cli", "test message"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI message works")
        else:
            print(f"❌ CLI message failed: {result.stderr}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_onboarding():
    """Test onboarding functionality."""
    print("\n🧪 Testing onboarding functionality...")
    try:
        # Remove config to simulate fresh install
        config_dir = Path.home() / ".config" / "computer-talk"
        if config_dir.exists():
            import shutil
            shutil.rmtree(config_dir)
        
        from computer_talk.first_run import check_and_run_onboarding
        
        # Test onboarding (should show welcome message)
        result = check_and_run_onboarding(force_interactive=False)
        print(f"✅ Onboarding result: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Onboarding test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Computer-Talk Package Locally")
    print("=" * 50)
    
    tests = [
        test_import,
        test_config,
        test_core,
        test_cli,
        test_onboarding,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is working correctly.")
        print("\n📝 Next steps:")
        print("1. Test interactive mode: computer-talk --interactive")
        print("2. Test with your API key: export OPENAI_API_KEY=your_key")
        print("3. Build package: make build (if in virtual env)")
        print("4. Upload to PyPI: make upload")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
