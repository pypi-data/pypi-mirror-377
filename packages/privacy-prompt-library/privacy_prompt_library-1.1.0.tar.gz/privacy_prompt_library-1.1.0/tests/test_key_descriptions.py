"""
Tests for key-based disability descriptions functionality
"""

import pytest
from prompt_library import transform_by_key, get_supported_keys
from prompt_library.core.key_descriptions import validate_word_count, get_description_for_key


class TestKeyBasedTransformations:
    """Test the new key-based transformation functionality."""
    
    def test_get_supported_keys(self):
        """Test that all expected keys are supported."""
        keys = get_supported_keys()
        expected_keys = [
            "visual-impairment",
            "hearing-impairment", 
            "physical-disability",
            "speech-language-communication-and-swallowing-disability",
            "speech-intellectual-autism-spectrum-disorders",
            "maxillofacial-disabilities",
            "progressive-chronic-disorders"
        ]
        
        assert len(keys) == len(expected_keys)
        for key in expected_keys:
            assert key in keys
    
    def test_transform_visual_impairment(self):
        """Test visual impairment key transformation."""
        result = transform_by_key("visual-impairment")
        
        assert result['input'] == "visual-impairment"
        assert 'output' in result
        assert 'transformation' in result
        
        # Check that specific disability terms are not disclosed
        output = result['output'].lower()
        assert "blind" not in output
        assert "visual impairment" not in output
        assert "low vision" not in output
        
        # Check that functional needs are described
        assert "screen reader" in output or "visual" in output
        assert "accessibility" in output or "accessible" in output
    
    def test_transform_hearing_impairment(self):
        """Test hearing impairment key transformation."""
        result = transform_by_key("hearing-impairment")
        
        assert result['input'] == "hearing-impairment"
        
        output = result['output'].lower()
        assert "deaf" not in output
        assert "hearing impairment" not in output
        assert "hard of hearing" not in output
        
        # Check functional descriptions
        assert "captions" in output or "sign language" in output
        assert "accessibility" in output or "accessible" in output
    
    def test_transform_physical_disability(self):
        """Test physical disability key transformation."""
        result = transform_by_key("physical-disability")
        
        output = result['output'].lower()
        assert "wheelchair" not in output
        assert "paralyzed" not in output
        assert "physical disability" not in output
        
        # Check functional descriptions
        assert "step-free" in output or "accessible" in output
        assert "mobility" in output or "access" in output
    
    def test_transform_speech_language(self):
        """Test speech-language-communication key transformation."""
        result = transform_by_key("speech-language-communication-and-swallowing-disability")
        
        output = result['output'].lower()
        assert "speech disability" not in output
        assert "communication disorder" not in output
        
        # Check functional descriptions
        assert "communication" in output
        assert "alternative" in output or "accommodations" in output
    
    def test_transform_autism_spectrum(self):
        """Test autism spectrum disorders key transformation."""
        result = transform_by_key("speech-intellectual-autism-spectrum-disorders")
        
        output = result['output'].lower()
        assert "autism" not in output
        assert "intellectual disability" not in output
        
        # Check functional descriptions
        assert "structured" in output or "predictable" in output
        assert "sensory" in output or "routine" in output
    
    def test_transform_maxillofacial(self):
        """Test maxillofacial disabilities key transformation."""
        result = transform_by_key("maxillofacial-disabilities")
        
        output = result['output'].lower()
        assert "maxillofacial" not in output
        assert "facial" in output or "oral" in output
        assert "communication" in output or "accommodations" in output
    
    def test_transform_progressive_chronic(self):
        """Test progressive chronic disorders key transformation."""
        result = transform_by_key("progressive-chronic-disorders")
        
        output = result['output'].lower()
        assert "progressive" not in output
        assert "chronic" not in output
        
        # Check functional descriptions
        assert "flexible" in output or "adapt" in output
        assert "fatigue" in output or "variable" in output
    
    def test_invalid_key(self):
        """Test handling of invalid keys."""
        result = transform_by_key("invalid-key")
        
        assert 'error' in result
        assert 'supported_keys' in result
        assert result['input'] == "invalid-key"
    
    def test_word_count_validation(self):
        """Test that all descriptions meet the 60-word target."""
        keys = get_supported_keys()
        
        for key in keys:
            description = get_description_for_key(key)
            validation = validate_word_count(description, 60)
            
            # Allow slight variation (58-62 words) for natural language
            assert 58 <= validation['word_count'] <= 62, f"Key '{key}' has {validation['word_count']} words, expected ~60"
    
    def test_transformation_structure(self):
        """Test that transformation results have correct structure."""
        result = transform_by_key("visual-impairment")
        
        # Check main structure
        assert 'input' in result
        assert 'output' in result
        assert 'transformation' in result
        assert 'validation' in result
        assert 'metadata' in result
        
        # Check transformation details
        transformation = result['transformation']
        assert transformation['type'] == "key_based_description"
        assert transformation['category'] == "visual-impairment"
        assert 'word_count' in transformation
        assert 'meets_target' in transformation
        
        # Check validation details
        validation = result['validation']
        assert 'word_count' in validation
        assert 'target_count' in validation
        assert 'meets_target' in validation
        assert 'difference' in validation
        
        # Check metadata
        metadata = result['metadata']
        assert metadata['processing_type'] == "key_based"
        assert metadata['privacy_level'] == "high"
        assert metadata['functional_description'] is True
    
    def test_privacy_preservation(self):
        """Test that no disability-specific terms are disclosed in any description."""
        keys = get_supported_keys()
        
        # Terms that should never appear in outputs
        prohibited_terms = [
            "blind", "deaf", "wheelchair", "paralyzed", "autism", "autistic",
            "cerebral palsy", "multiple sclerosis", "spina bifida", "amputation",
            "intellectual disability", "down syndrome", "adhd", "dyslexia",
            "bipolar", "depression", "anxiety", "schizophrenia", "ptsd"
        ]
        
        for key in keys:
            description = get_description_for_key(key).lower()
            
            for term in prohibited_terms:
                assert term not in description, f"Prohibited term '{term}' found in description for key '{key}'"
    
    def test_functional_content_presence(self):
        """Test that descriptions contain functional accessibility information."""
        keys = get_supported_keys()
        
        # Terms that should appear in functional descriptions
        functional_terms = [
            "accessibility", "accessible", "accommodations", "support",
            "equipment", "technology", "alternative", "format", "method"
        ]
        
        for key in keys:
            description = get_description_for_key(key).lower()
            
            # Each description should contain at least some functional terms
            found_terms = [term for term in functional_terms if term in description]
            assert len(found_terms) >= 2, f"Key '{key}' description lacks sufficient functional content"


class TestWordCountValidation:
    """Test the word count validation functionality."""
    
    def test_exact_word_count(self):
        """Test validation with exact target word count."""
        text = " ".join(["word"] * 60)  # Exactly 60 words
        result = validate_word_count(text, 60)
        
        assert result['word_count'] == 60
        assert result['target_count'] == 60
        assert result['meets_target'] is True
        assert result['difference'] == 0
    
    def test_over_word_count(self):
        """Test validation with too many words."""
        text = " ".join(["word"] * 65)  # 65 words
        result = validate_word_count(text, 60)
        
        assert result['word_count'] == 65
        assert result['meets_target'] is False
        assert result['difference'] == 5
    
    def test_under_word_count(self):
        """Test validation with too few words."""
        text = " ".join(["word"] * 55)  # 55 words
        result = validate_word_count(text, 60)
        
        assert result['word_count'] == 55
        assert result['meets_target'] is False
        assert result['difference'] == -5
    
    def test_empty_text(self):
        """Test validation with empty text."""
        result = validate_word_count("", 60)
        
        assert result['word_count'] == 0
        assert result['meets_target'] is False
        assert result['difference'] == -60


if __name__ == "__main__":
    # Run basic functionality test
    print("Testing key-based transformations...")
    
    # Test all supported keys
    keys = get_supported_keys()
    print(f"Supported keys: {keys}")
    
    for key in keys:
        result = transform_by_key(key)
        print(f"\nKey: {key}")
        print(f"Word count: {result['transformation']['word_count']}")
        print(f"Output preview: {result['output'][:100]}...")
    
    print("\nKey-based transformation tests completed!")