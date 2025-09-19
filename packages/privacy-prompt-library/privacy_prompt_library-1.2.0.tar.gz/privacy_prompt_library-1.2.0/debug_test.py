"""
Debug test to understand what's happening
"""

from prompt_library import transform_prompt

def debug_test():
    test_cases = [
        "I'm blind and use a wheelchair",
        "I have cerebral palsy", 
        "My email is test@example.com"
    ]
    
    for test in test_cases:
        result = transform_prompt(test)
        print(f"\nInput: {test}")
        print(f"Output: {result['output']}")
        print(f"Has transformations: {result['metadata']['has_transformations']}")
        if result['transformation']['detections']:
            print(f"Detections: {[d['term'] for d in result['transformation']['detections']]}")

if __name__ == "__main__":
    debug_test()