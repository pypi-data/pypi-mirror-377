#!/usr/bin/env python3
"""
Upload script for privacy-prompt-library to real PyPI
"""

import subprocess
import os
import sys

def main():
    print("🚀 Uploading to PyPI...")
    print("⚠️  This will make your package publicly available to all Python users worldwide!")
    
    # Check if API token is provided via environment variable first
    api_token = os.environ.get('PYPI_API_TOKEN')
    if not api_token:
        api_token = input("Enter your PyPI API token (starts with 'pypi-'): ").strip()
    
    if not api_token.startswith('pypi-'):
        print("❌ Invalid API token. Please get one from https://pypi.org/manage/account/token/")
        return
    
    # Set environment variables for twine
    os.environ['TWINE_USERNAME'] = '__token__'
    os.environ['TWINE_PASSWORD'] = api_token
    
    # Upload to PyPI
    cmd = [
        sys.executable, '-m', 'twine', 'upload', 
        '--verbose',
        'dist/privacy_prompt_library-1.1.0-py3-none-any.whl',
        'dist/privacy_prompt_library-1.1.0.tar.gz'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Upload successful!")
        print(result.stdout)
        
        print("\n🎉 Your package is now live on PyPI!")
        print("📦 Package URL: https://pypi.org/project/privacy-prompt-library/")
        print("🔧 Installation command: pip install privacy-prompt-library")
        
    except subprocess.CalledProcessError as e:
        print("❌ Upload failed!")
        print("Error:", e.stderr)
        if "409" in e.stderr:
            print("This version already exists. Increment the version number and rebuild.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())