# Makefile for computer-talk package

.PHONY: help install install-dev test lint format clean build upload check

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package in development mode with dev dependencies
	pip install -e .[dev]

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=computer_talk --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 computer_talk/ tests/
	mypy computer_talk/

format:  ## Format code
	black computer_talk/ tests/

format-check:  ## Check code formatting
	black --check computer_talk/ tests/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

build: clean  ## Build the package
	python -m build

check:  ## Check the built package
	python -m twine check dist/*

upload-test:  ## Upload to test PyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

all: clean install-dev test lint format build check  ## Run all checks and build

dev-setup:  ## Set up development environment
	pip install -e .[dev]
	pre-commit install || echo "pre-commit not available, skipping"

version:  ## Show version information
	@python -c "import computer_talk; print(f'Version: {computer_talk.__version__}')"
