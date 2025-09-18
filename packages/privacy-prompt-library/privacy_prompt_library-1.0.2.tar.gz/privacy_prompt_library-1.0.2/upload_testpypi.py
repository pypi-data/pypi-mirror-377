#!/usr/bin/env python3
"""
Upload script for privacy-prompt-library to TestPyPI
"""

import subprocess
import os
import sys

def main():
    # Set environment variables for twine
    os.environ['TWINE_USERNAME'] = '__token__'
    os.environ['TWINE_PASSWORD'] = 'pypi-AgENdGVzdC5weXBpLm9yZwIkZDgwNDEwNzktMjJhMy00NTgwLWExYjktODQxOWFjNjZiYWM0AAIqWzMsIjQ2Mjg3MGYxLTNjNzYtNDEzYS05NmJiLWEzYjU4YzQyYzU2ZiJdAAAGILsF2erT4eG9BsfRNDnSbmhYBh7KrSEKmWhp1dn8MXAs'
    
    print("🚀 Uploading to TestPyPI...")
    
    # Upload to TestPyPI
    cmd = [
        sys.executable, '-m', 'twine', 'upload', 
        '--repository', 'testpypi',
        '--verbose',
        'dist/privacy_prompt_library-1.0.2-py3-none-any.whl',
        'dist/privacy_prompt_library-1.0.2.tar.gz'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Upload successful!")
        print(result.stdout)
        
        print("\n🔗 Package URL:")
        print("https://test.pypi.org/project/privacy-prompt-library/")
        
        print("\n📦 To test install:")
        print("pip install --index-url https://test.pypi.org/simple/ privacy-prompt-library")
        
    except subprocess.CalledProcessError as e:
        print("❌ Upload failed!")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())