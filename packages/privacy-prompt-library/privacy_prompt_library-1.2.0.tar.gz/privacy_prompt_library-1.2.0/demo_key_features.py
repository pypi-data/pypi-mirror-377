"""
Demo of the enhanced key-based disability descriptions
"""

import sys
sys.path.insert(0, '.')

from prompt_library.core.key_descriptions import transform_by_key, get_supported_keys, validate_word_count

def demo_key_transformations():
    """Demonstrate the new key-based transformation functionality."""
    
    print("🔑 Key-Based Disability Descriptions Demo")
    print("=" * 50)
    
    # Show all supported keys
    keys = get_supported_keys()
    print(f"\n📋 Supported Keys ({len(keys)} total):")
    for i, key in enumerate(keys, 1):
        print(f"{i}. {key}")
    
    print("\n" + "=" * 50)
    print("📝 Sample Transformations:")
    
    # Test a few key transformations
    sample_keys = [
        "visual-impairment",
        "hearing-impairment", 
        "physical-disability",
        "speech-intellectual-autism-spectrum-disorders"
    ]
    
    for key in sample_keys:
        print(f"\n🔸 Key: '{key}'")
        
        result = transform_by_key(key)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
            continue
        
        # Show transformation details
        print(f"   📊 Word Count: {result['transformation']['word_count']}")
        print(f"   ✅ Meets Target: {result['transformation']['meets_target']}")
        print(f"   🔒 Privacy Level: {result['metadata']['privacy_level']}")
        
        # Show description (truncated for display)
        description = result['output']
        if len(description) > 150:
            description = description[:150] + "..."
        print(f"   📄 Description: {description}")
    
    # Test word count validation
    print("\n" + "=" * 50)
    print("📏 Word Count Validation:")
    
    all_valid = True
    for key in keys:
        result = transform_by_key(key)
        word_count = result['transformation']['word_count']
        meets_target = result['transformation']['meets_target']
        
        status = "✅" if 58 <= word_count <= 62 else "❌"
        print(f"   {status} {key}: {word_count} words")
        
        if not (58 <= word_count <= 62):
            all_valid = False
    
    print(f"\n📊 Overall validation: {'✅ All descriptions within target range' if all_valid else '❌ Some descriptions need adjustment'}")
    
    # Test error handling
    print("\n" + "=" * 50)
    print("🚫 Error Handling:")
    
    invalid_result = transform_by_key("invalid-key")
    print(f"   ❌ Invalid key test: {invalid_result['error']}")
    
    print("\n🎉 Demo completed successfully!")

if __name__ == "__main__":
    demo_key_transformations()