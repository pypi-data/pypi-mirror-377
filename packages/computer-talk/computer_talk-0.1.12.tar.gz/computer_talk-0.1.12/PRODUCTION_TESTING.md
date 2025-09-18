# Production Testing Guide

This guide shows you how to test your computer-talk package in production by uploading to TestPyPI and PyPI.

## 🚀 Quick Production Test

### 1. Upload to TestPyPI (Recommended First)
```bash
# Build the package
python3 -m build

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*
```

### 2. Test Installation from TestPyPI
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ computer-talk

# Test the package
computer-talk --help
```

### 3. Upload to Production PyPI
```bash
# Upload to production PyPI
python3 -m twine upload dist/*
```

## 📦 Complete Production Testing Workflow

### Step 1: Prepare for Production
```bash
# 1. Update version number
# Edit pyproject.toml: version = "0.1.4"

# 2. Clean and build
make clean
make build

# 3. Check the package
make check
```

### Step 2: Test on TestPyPI
```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip uninstall computer-talk -y
pip install --index-url https://test.pypi.org/simple/ computer-talk

# Test fresh installation experience
rm -rf ~/.config/computer-talk
computer-talk --help
```

### Step 3: Test on Production PyPI
```bash
# Upload to production PyPI
python3 -m twine upload dist/*

# Test installation from PyPI
pip uninstall computer-talk -y
pip install computer-talk

# Test the full experience
rm -rf ~/.config/computer-talk
computer-talk --interactive
```

## 🧪 Production Test Scenarios

### Scenario 1: Fresh User Experience
```bash
# Simulate a new user
pip uninstall computer-talk -y
rm -rf ~/.config/computer-talk

# Install from PyPI
pip install computer-talk

# Test first run (should show onboarding)
python3 -c "import computer_talk"
computer-talk --help
```

### Scenario 2: Interactive Mode
```bash
# Test interactive onboarding
rm -rf ~/.config/computer-talk
computer-talk --interactive
```

### Scenario 3: API Key Environment Variable
```bash
# Test with environment variable
export OPENAI_API_KEY="sk-test1234567890"
rm -rf ~/.config/computer-talk
computer-talk --help
```

### Scenario 4: Different Python Versions
```bash
# Test with different Python versions
python3.8 -c "import computer_talk"
python3.9 -c "import computer_talk"
python3.10 -c "import computer_talk"
python3.11 -c "import computer_talk"
python3.12 -c "import computer_talk"
```

## 🔧 Production Testing Checklist

### Before Upload
- [ ] Version number updated
- [ ] All tests pass locally
- [ ] Package builds successfully
- [ ] No linting errors
- [ ] Documentation is complete
- [ ] README is up to date

### TestPyPI Testing
- [ ] Upload to TestPyPI successful
- [ ] Install from TestPyPI works
- [ ] Fresh installation shows onboarding
- [ ] Interactive mode works
- [ ] All CLI commands work
- [ ] Python API works

### Production PyPI Testing
- [ ] Upload to PyPI successful
- [ ] Install from PyPI works
- [ ] Fresh installation shows onboarding
- [ ] Interactive mode works
- [ ] All CLI commands work
- [ ] Python API works
- [ ] Package appears on PyPI website

## 🐛 Troubleshooting Production Issues

### Common Issues
1. **Upload fails**: Check credentials in ~/.pypirc
2. **Install fails**: Check package name and version
3. **Onboarding doesn't show**: Check config directory permissions
4. **CLI not found**: Check PATH and installation

### Debug Commands
```bash
# Check package installation
pip show computer-talk

# Check CLI location
which computer-talk

# Check config directory
ls -la ~/.config/computer-talk/

# Test with debug logging
computer-talk --log-level DEBUG "hello"
```

## 📊 Production Test Results

### Expected Behavior
- ✅ Package installs without errors
- ✅ Onboarding shows on first run
- ✅ Interactive API key prompt works
- ✅ All CLI commands work
- ✅ Python API works
- ✅ Config file created with correct permissions

### Success Metrics
- Package downloads successfully
- No installation errors
- Onboarding experience is smooth
- Users can set API key easily
- All functionality works as expected

## 🚀 Ready for Production

Once all tests pass:
1. Update version number
2. Upload to PyPI
3. Test installation
4. Monitor for issues
5. Gather user feedback

Your package is ready for production! 🎉
