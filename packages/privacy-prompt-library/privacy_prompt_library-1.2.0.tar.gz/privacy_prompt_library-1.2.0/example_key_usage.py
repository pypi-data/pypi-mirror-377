"""
Simple example showing how to use the new key-based transformation features
"""

import sys
sys.path.insert(0, '.')

from prompt_library.core.key_descriptions import transform_by_key, get_supported_keys

def main():
    print("🆕 Enhanced Privacy-Preserving Prompt Library")
    print("📝 Key-Based Disability Descriptions")
    print("=" * 50)
    
    # Show available keys
    print("\n📋 Available Keys:")
    keys = get_supported_keys()
    for key in keys:
        print(f"  • {key}")
    
    print("\n💡 Usage Examples:")
    
    # Example 1: Get description for visual impairment
    print("\n1️⃣ Visual Impairment:")
    result = transform_by_key("visual-impairment")
    print(f"   Input: 'visual-impairment'")
    print(f"   Output: {result['output'][:100]}...")
    print(f"   Word Count: {result['transformation']['word_count']}")
    
    # Example 2: Get description for hearing impairment
    print("\n2️⃣ Hearing Impairment:")
    result = transform_by_key("hearing-impairment")
    print(f"   Input: 'hearing-impairment'")
    print(f"   Output: {result['output'][:100]}...")
    print(f"   Word Count: {result['transformation']['word_count']}")
    
    # Example 3: Error handling
    print("\n3️⃣ Error Handling:")
    result = transform_by_key("invalid-key")
    if 'error' in result:
        print(f"   Input: 'invalid-key'")
        print(f"   Error: {result['error']}")
    
    print("\n✨ Benefits:")
    print("  • 🔒 Complete privacy - no disability terms disclosed")
    print("  • 📏 Consistent 60-word format")
    print("  • 🎯 Functional descriptions without medical details")
    print("  • 🔑 Simple key-based interface")
    print("  • ♿ Covers all major accessibility categories")

if __name__ == "__main__":
    main()