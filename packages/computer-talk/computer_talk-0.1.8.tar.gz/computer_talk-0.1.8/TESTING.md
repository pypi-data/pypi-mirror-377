# Testing Computer-Talk Locally

This guide shows you how to test the computer-talk package locally before publishing to PyPI.

## 🚀 Quick Start Testing

### 1. Install in Development Mode
```bash
# Install the package in editable mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### 2. Test the Interactive Onboarding
```bash
# Remove any existing config to simulate fresh installation
rm -rf ~/.config/computer-talk

# Test the interactive API key prompt
python3 -c "
from computer_talk.config import ensure_openai_api_key_interactive
ensure_openai_api_key_interactive()
"
```

### 3. Test the CLI
```bash
# Test help
computer-talk --help

# Test interactive mode
computer-talk --interactive

# Test with a message
computer-talk "hello world"
```

## 🧪 Comprehensive Testing

### Test 1: Fresh Installation Simulation
```bash
# Remove existing config
rm -rf ~/.config/computer-talk

# Test import (should trigger onboarding)
python3 -c "import computer_talk"

# Test CLI (should not trigger onboarding again)
computer-talk --help
```

### Test 2: Interactive API Key Prompt
```bash
# Remove config
rm -rf ~/.config/computer-talk

# Test the interactive prompt
python3 -c "
from computer_talk.config import ensure_openai_api_key_interactive
key = ensure_openai_api_key_interactive()
print(f'Got key: {key[:10]}...' if key else 'No key provided')
"
```

### Test 3: CLI Functionality
```bash
# Test all CLI features
computer-talk --version
computer-talk --help
computer-talk "hello"
computer-talk "time"
computer-talk "status"
computer-talk --interactive
```

### Test 4: Python API
```bash
python3 -c "
from computer_talk import ComputerTalk

# Test context manager
with ComputerTalk() as talk:
    print('Status:', talk.get_status())
    print('Response:', talk.send_message('hello'))
"
```

## 🔧 Development Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=computer_talk --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

### Lint and Format
```bash
# Check code formatting
black --check computer_talk/ tests/

# Format code
black computer_talk/ tests/

# Run linting
flake8 computer_talk/ tests/

# Type checking
mypy computer_talk/
```

### Build Package
```bash
# Clean and build
make clean
make build

# Check the built package
make check
```

## 📦 Package Testing

### Test Installation
```bash
# Build the package
python -m build

# Install from built wheel
pip install dist/computer_talk-*.whl

# Test the installed package
computer-talk --help
```

### Test Uninstall/Reinstall
```bash
# Uninstall
pip uninstall computer-talk -y

# Reinstall
pip install .

# Test fresh installation
rm -rf ~/.config/computer-talk
computer-talk --help
```

## 🎯 Interactive Demo

### Full Onboarding Flow
```bash
# 1. Remove config (simulate fresh install)
rm -rf ~/.config/computer-talk

# 2. Test import onboarding
python3 -c "import computer_talk"

# 3. Test CLI onboarding
rm -rf ~/.config/computer-talk
computer-talk --interactive
```

### API Key Testing
```bash
# Test with environment variable
export OPENAI_API_KEY="sk-test1234567890"
python3 -c "
from computer_talk.config import get_openai_api_key
print('Key from env:', get_openai_api_key())
"

# Test with config file
rm -rf ~/.config/computer-talk
python3 -c "
from computer_talk.config import set_openai_api_key, get_openai_api_key
set_openai_api_key('sk-test1234567890')
print('Key from config:', get_openai_api_key())
"
```

## 🐛 Debugging

### Check Config
```bash
# View config file
cat ~/.config/computer-talk/config.json

# Check config directory
ls -la ~/.config/computer-talk/
```

### Verbose Testing
```bash
# Test with debug logging
computer-talk --log-level DEBUG "hello"

# Test Python API with debug
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from computer_talk import ComputerTalk
with ComputerTalk() as talk:
    print(talk.send_message('hello'))
"
```

## ✅ Expected Results

### Onboarding
- ✅ Welcome message appears on first run
- ✅ Interactive API key prompt (in TTY)
- ✅ Config file created with secure permissions
- ✅ Onboarding only runs once

### CLI
- ✅ All commands work correctly
- ✅ Interactive mode functions
- ✅ Help and version display
- ✅ Message processing works

### API
- ✅ Context manager works
- ✅ Start/stop functionality
- ✅ Message sending/receiving
- ✅ Status and capabilities

## 🚨 Troubleshooting

### Common Issues
1. **Onboarding doesn't show**: Check if config already exists
2. **Permission errors**: Check file permissions on config directory
3. **Import errors**: Ensure package is installed correctly
4. **CLI not found**: Check PATH and installation

### Reset Everything
```bash
# Complete reset
pip uninstall computer-talk -y
rm -rf ~/.config/computer-talk
pip install -e .
```
