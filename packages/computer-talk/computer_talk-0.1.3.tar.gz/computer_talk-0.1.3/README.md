# Computer Talk

A Python package for computer communication and interaction.

## Features

- Easy-to-use API for computer communication
- Cross-platform compatibility
- Extensible architecture
- Command-line interface

## Installation

### From PyPI (when published)

```bash
pip install computer-talk
```

### From source

```bash
git clone https://github.com/jordan/computer-talk.git
cd computer-talk
pip install -e .
```

## Quick Start

```python
from computer_talk import ComputerTalk

# Create a new instance
talk = ComputerTalk()

# Start communication
talk.start()

# Send a message
response = talk.send_message("Hello, computer!")

# Stop communication
talk.stop()
```

## Command Line Usage

```bash
# Start the CLI
computer-talk

# Get help
computer-talk --help
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/jordan/computer-talk.git
cd computer-talk

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
black computer_talk/
flake8 computer_talk/
mypy computer_talk/
```

### Building and Publishing

```bash
# Build the package
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### 0.1.0
- Initial release
- Basic computer communication functionality
- Command-line interface
