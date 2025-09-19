#!/usr/bin/env python3
"""
Setup script for Privacy Prompt Library development and testing
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up Privacy Prompt Library for development...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this from the project root.")
        sys.exit(1)
    
    # Install the package in development mode
    commands = [
        ("pip install -e .", "Installing package in development mode"),
        ("pip install pytest pytest-asyncio", "Installing test dependencies"),
    ]
    
    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1
    
    print(f"\n📊 Setup Summary:")
    print(f"   Completed: {success_count}/{len(commands)} steps")
    
    if success_count == len(commands):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Test the installation: python -m prompt_library.cli --info")
        print("2. Run tests: python tests/test_basic.py")
        print("3. Try transforming a prompt: python -m prompt_library.cli 'I am paralyzed and need help'")
    else:
        print("\n⚠️  Setup completed with some issues. Please check the errors above.")


if __name__ == "__main__":
    main()