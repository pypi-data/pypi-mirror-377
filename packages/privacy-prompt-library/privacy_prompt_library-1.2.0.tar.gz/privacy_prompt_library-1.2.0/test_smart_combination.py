#!/usr/bin/env python3
"""
Test script for smart combined multiple key functionality
"""

from prompt_library import transform_multiple_keys, get_supported_keys

def test_smart_combination():
    print("🧪 Testing smart combination functionality...")
    
    # Test data
    test_keys = ["visual-impairment", "hearing-impairment", "physical-disability"]
    
    print(f"\n📋 Testing with keys: {test_keys}")
    
    # Test smart_combined method (new default)
    print("\n🎯 Testing 'smart_combined' method (new default):")
    result_smart = transform_multiple_keys(test_keys)  # Default is now smart_combined
    if "error" not in result_smart:
        print(f"✅ Success! Smart combined description has {result_smart['transformation']['total_word_count']} words")
        print(f"🔧 Compression ratio: {result_smart['transformation']['compression_ratio']:.2f}")
        print(f"💡 Efficiency gain: {result_smart['validation']['efficiency_gain']}")
        print(f"\n📄 Smart Combined Description:")
        print(f"{result_smart['output']}")
        print(f"\n📊 Original total words: {sum(result_smart['transformation']['individual_word_counts'])}")
        print(f"📊 Smart combined words: {result_smart['transformation']['total_word_count']}")
    else:
        print(f"❌ Error: {result_smart['error']}")
    
    # Compare with simple_combined
    print("\n🔄 Comparing with 'simple_combined' method:")
    result_simple = transform_multiple_keys(test_keys, "simple_combined")
    if "error" not in result_simple:
        print(f"📊 Simple combined words: {result_simple['transformation']['total_word_count']}")
        print(f"💾 Space saving: {result_smart['transformation']['total_word_count'] - result_simple['transformation']['total_word_count']} words")
    
    # Test with different combinations
    print("\n🎨 Testing different key combinations:")
    
    combinations = [
        ["visual-impairment"],
        ["visual-impairment", "physical-disability"], 
        ["hearing-impairment", "speech-language-communication-and-swallowing-disability"],
        ["visual-impairment", "hearing-impairment", "physical-disability", "speech-intellectual-autism-spectrum-disorders"]
    ]
    
    for combo in combinations:
        result = transform_multiple_keys(combo, "smart_combined")
        if "error" not in result:
            word_count = result['transformation']['total_word_count']
            key_count = len(combo)
            print(f"  {key_count} keys → {word_count} words | {combo[0]}{'...' if len(combo) > 1 else ''}")
    
    print("\n✅ Smart combination testing completed!")

if __name__ == "__main__":
    test_smart_combination()