#!/usr/bin/env python3
"""
Build script for computer-talk package.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd: list, description: str) -> None:
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running {description}:")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    
    print(f"✓ {description} completed successfully")
    if result.stdout:
        print(result.stdout)


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
    
    # Remove .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
    
    for pycache_dir in Path('.').rglob('__pycache__'):
        shutil.rmtree(pycache_dir)
    
    print("✓ Clean completed")


def install_build_deps():
    """Install build dependencies."""
    run_command(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', 'build', 'twine'],
        "Installing build dependencies"
    )


def build_package():
    """Build the package."""
    run_command(
        [sys.executable, '-m', 'build'],
        "Building package"
    )


def check_package():
    """Check the built package."""
    run_command(
        [sys.executable, '-m', 'twine', 'check', 'dist/*'],
        "Checking package"
    )


def main():
    """Main build process."""
    print("Building computer-talk package...")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Clean previous builds
    clean_build()
    
    # Install build dependencies
    install_build_deps()
    
    # Build the package
    build_package()
    
    # Check the package
    check_package()
    
    print("=" * 50)
    print("Build completed successfully!")
    print("\nTo upload to PyPI:")
    print("  python -m twine upload dist/*")
    print("\nTo install locally:")
    print("  pip install dist/computer_talk-*.whl")


if __name__ == "__main__":
    main()
