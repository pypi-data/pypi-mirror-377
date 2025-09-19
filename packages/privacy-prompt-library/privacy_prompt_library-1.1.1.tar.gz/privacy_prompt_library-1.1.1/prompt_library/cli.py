"""
Command Line Interface for Privacy Prompt Library
"""

import argparse
import json
import sys
from typing import Optional

from . import PromptLibrary, __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Privacy-Preserving Prompt Library CLI"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"privacy-prompt-library {__version__}"
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to transform (or read from stdin if not provided)"
    )
    
    parser.add_argument(
        "--privacy-level",
        choices=["low", "medium", "high"],
        default="high",
        help="Privacy protection level"
    )
    
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Disable context addition"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["json", "text"],
        default="text",
        help="Output format"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show library information"
    )
    
    args = parser.parse_args()
    
    # Initialize library
    library = PromptLibrary()
    
    if args.info:
        info = library.get_library_info()
        print(json.dumps(info, indent=2))
        return
    
    # Get input prompt
    if args.prompt:
        input_prompt = args.prompt
    else:
        if sys.stdin.isatty():
            print("Enter your prompt (Ctrl+D to finish):")
        input_prompt = sys.stdin.read().strip()
    
    if not input_prompt:
        print("Error: No prompt provided", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Transform prompt
        options = {
            'privacy_level': args.privacy_level,
            'add_context': not args.no_context
        }
        
        result = library.transform_prompt_sync(input_prompt, options)
        
        # Output result
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            if 'error' in result:
                print(f"Error: {result['error']['message']}", file=sys.stderr)
                print(f"Original: {result['input']}")
            else:
                print(result['output'])
                
                if result['transformation']['has_transformations']:
                    print(f"\n--- Transformation Summary ---")
                    print(f"Detections: {len(result['transformation']['detections'])}")
                    print(f"Privacy Score: {result['transformation']['privacy_score']:.2f}")
                    print(f"Functional Score: {result['transformation']['functional_score']:.2f}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()