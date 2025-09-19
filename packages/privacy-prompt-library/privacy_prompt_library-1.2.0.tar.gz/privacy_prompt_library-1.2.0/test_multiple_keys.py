#!/usr/bin/env python3
"""
Test script for multiple key functionality
"""

from prompt_library import transform_multiple_keys, get_supported_keys

def test_multiple_keys():
    print("🧪 Testing multiple key functionality...")
    
    # Test data
    test_keys = ["visual-impairment", "hearing-impairment", "physical-disability"]
    
    print(f"\n📋 Testing with keys: {test_keys}")
    
    # Test separate method
    print("\n1️⃣ Testing 'separate' method:")
    result_separate = transform_multiple_keys(test_keys, "separate")
    if "error" not in result_separate:
        print(f"✅ Success! Got {len(result_separate['output'])} separate descriptions")
        print(f"Total word count: {result_separate['transformation']['total_word_count']}")
    else:
        print(f"❌ Error: {result_separate['error']}")
    
    # Test combined method
    print("\n2️⃣ Testing 'combined' method:")
    result_combined = transform_multiple_keys(test_keys, "combined")
    if "error" not in result_combined:
        print(f"✅ Success! Combined description has {result_combined['transformation']['total_word_count']} words")
        print(f"Preview: {result_combined['output'][:150]}...")
    else:
        print(f"❌ Error: {result_combined['error']}")
    
    # Test prioritized method
    print("\n3️⃣ Testing 'prioritized' method:")
    result_prioritized = transform_multiple_keys(test_keys, "prioritized")
    if "error" not in result_prioritized:
        print(f"✅ Success! Prioritized description has {result_prioritized['transformation']['total_word_count']} words")
        print(f"Primary key: {result_prioritized['transformation']['primary_key']}")
        print(f"Preview: {result_prioritized['output'][:150]}...")
    else:
        print(f"❌ Error: {result_prioritized['error']}")
    
    # Test error handling
    print("\n4️⃣ Testing error handling with invalid key:")
    result_error = transform_multiple_keys(["visual-impairment", "invalid-key"], "separate")
    if "error" in result_error:
        print(f"✅ Error handling works: {result_error['error']}")
    else:
        print("❌ Error handling failed")
    
    print("\n✅ Multiple key testing completed!")

if __name__ == "__main__":
    test_multiple_keys()