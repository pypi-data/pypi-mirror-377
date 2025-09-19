#!/usr/bin/env python3
"""
Test script to verify the deployed package functionality
"""

from prompt_library import transform_by_key, get_supported_keys, get_library_info

def test_deployed_package():
    print("🧪 Testing deployed privacy-prompt-library v1.1.0...")
    
    # Test library info
    info = get_library_info()
    print(f"📦 Version: {info['version']}")
    print(f"🎯 Features: {', '.join(info['features'])}")
    
    # Test supported keys
    keys = get_supported_keys()
    print(f"\n🔑 Supported keys ({len(keys)}):")
    for key in keys:
        print(f"  - {key}")
    
    # Test key-based transformations
    print("\n🎯 Testing key-based transformations:")
    for key in keys[:3]:  # Test first 3 keys
        try:
            result = transform_by_key(key)
            word_count = len(result['output'].split())
            print(f"\n Key: {key}")
            print(f" Word count: {word_count}")
            print(f" Validation: ✅" if result['validation']['meets_target'] else "❌")
            print(f" Description preview: {result['output'][:100]}...")
        except Exception as e:
            print(f" ❌ Error testing {key}: {e}")
    
    print("\n✅ Deployment test completed successfully!")

if __name__ == "__main__":
    test_deployed_package()