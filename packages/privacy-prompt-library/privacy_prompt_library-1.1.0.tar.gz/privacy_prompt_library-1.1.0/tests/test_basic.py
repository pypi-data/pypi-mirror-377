"""
Basic tests for the Privacy Prompt Library
"""

import pytest
import json
from pathlib import Path

from prompt_library import PromptLibrary, transform_prompt, get_library_info


def test_library_info():
    """Test library information retrieval."""
    info = get_library_info()
    
    assert info['version'] == '1.0.0'
    assert info['categories'] == 14
    assert 'features' in info
    assert len(info['features']) > 0


def test_simple_transform():
    """Test basic prompt transformation."""
    # This is a simple test - in a real scenario you'd need the data files
    try:
        result = transform_prompt("I am paralyzed and need help with accessibility.")
        
        # Basic structure checks
        assert 'input' in result
        assert 'output' in result
        assert 'transformation' in result
        
    except FileNotFoundError:
        # Expected if data files aren't present yet
        pytest.skip("Data files not found - this is expected during initial setup")


def test_library_initialization():
    """Test library can be instantiated."""
    library = PromptLibrary()
    assert not library.initialized
    
    info = library.get_library_info()
    assert info['version'] == '1.0.0'


if __name__ == "__main__":
    # Run basic tests
    test_library_info()
    test_library_initialization()
    print("✅ Basic tests passed!")