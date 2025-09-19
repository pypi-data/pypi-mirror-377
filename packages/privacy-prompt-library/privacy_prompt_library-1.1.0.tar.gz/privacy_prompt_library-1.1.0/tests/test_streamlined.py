"""
Streamlined tests for Privacy-Preserving Prompt Library
Focused on essential functionality without excessive looping
"""

import pytest
from prompt_library import transform_prompt, transform_batch, get_library_info


class TestBasicFunctionality:
    """Test core functionality with minimal looping."""
    
    def test_disability_detection_and_redaction(self):
        """Test that disabilities are properly detected and redacted."""
        prompt = "I'm blind and use a wheelchair"
        result = transform_prompt(prompt)
        
        # Check redaction - should be replaced with generic terms
        assert "blind" not in result['output']
        assert "wheelchair" not in result['output']
        # Check for expected replacements
        assert "person with specific needs" in result['output'] or "specific needs" in result['output']
        
        # Check structure
        assert 'output' in result
        assert 'transformation' in result
        assert 'context_additions' in result['transformation']
    
    def test_pii_detection_and_redaction(self):
        """Test that PII is properly detected and redacted."""
        prompt = "My email is test@example.com and phone is 555-1234"
        result = transform_prompt(prompt)
        
        # Check redaction - original terms should be gone
        assert "test@example.com" not in result['output']
        assert "555-1234" not in result['output']
        
        # Check redaction labels are present
        assert "[email redacted]" in result['output']
        assert ("[phone redacted]" in result['output'] or "[personal info redacted]" in result['output'])
    
    def test_context_addition(self):
        """Test that appropriate context is added."""
        prompt = "I'm deaf and need accommodations"
        result = transform_prompt(prompt)
        
        # Check redaction
        assert "deaf" not in result['output']
        
        # Check context addition - should have accessibility context
        assert len(result['transformation']['context_additions']) > 0
        full_output = result['output']
        assert any(word in full_output.lower() for word in ["captions", "visual", "hearing", "accessibility", "accommodations"])
    
    def test_mixed_content(self):
        """Test prompt with both disabilities and PII."""
        prompt = "I'm blind, my email is contact@example.com"
        result = transform_prompt(prompt)
        
        # Check both types are redacted
        assert "blind" not in result['output']
        assert "contact@example.com" not in result['output']
        
        # Check handling - should have redaction labels and context
        assert "[email redacted]" in result['output']
        assert len(result['transformation']['context_additions']) > 0


class TestMultipleCategories:
    """Test detection across different categories."""
    
    def test_physical_disabilities(self):
        """Test physical disability detection."""
        prompt = "I have cerebral palsy"
        result = transform_prompt(prompt)
        assert "cerebral palsy" not in result['output']
        # Should be replaced with generic term
        assert len(result['transformation']['redactions']) > 0
    
    def test_visual_impairments(self):
        """Test visual impairment detection."""
        prompt = "I have macular degeneration"
        result = transform_prompt(prompt)
        assert "macular degeneration" not in result['output']
        assert len(result['transformation']['redactions']) > 0
    
    def test_hearing_impairments(self):
        """Test hearing impairment detection."""
        prompt = "I have hearing loss"
        result = transform_prompt(prompt)
        assert "hearing loss" not in result['output']
        assert len(result['transformation']['redactions']) > 0
    
    def test_learning_disabilities(self):
        """Test learning disability detection."""
        prompt = "I have dyslexia"
        result = transform_prompt(prompt)
        assert "dyslexia" not in result['output']
        assert len(result['transformation']['redactions']) > 0
    
    def test_autism_spectrum(self):
        """Test autism spectrum detection."""
        prompt = "I have autism"
        result = transform_prompt(prompt)
        assert "autism" not in result['output']
        assert len(result['transformation']['redactions']) > 0
    
    def test_mental_health(self):
        """Test mental health condition detection."""
        prompt = "I have depression"
        result = transform_prompt(prompt)
        assert "depression" not in result['output']
        assert len(result['transformation']['redactions']) > 0


class TestPIITypes:
    """Test different types of PII detection."""
    
    def test_email_redaction(self):
        """Test email redaction."""
        prompt = "Contact me at user@domain.com"
        result = transform_prompt(prompt)
        assert "user@domain.com" not in result['output']
        assert "[email redacted]" in result['output']
    
    def test_phone_redaction(self):
        """Test phone number redaction."""
        prompt = "Call me at 555-123-4567"
        result = transform_prompt(prompt)
        assert "555-123-4567" not in result['output']
        # Phone might be redacted as general personal info
        assert ("[phone redacted]" in result['output'] or "[personal info redacted]" in result['output'])
    
    def test_address_redaction(self):
        """Test address redaction."""
        prompt = "I live at 123 Main Street"
        result = transform_prompt(prompt)
        assert "123 Main Street" not in result['output']
        assert ("[address redacted]" in result['output'] or "[personal info redacted]" in result['output'])
    
    def test_ssn_redaction(self):
        """Test SSN redaction."""
        prompt = "My SSN is 123-45-6789"
        result = transform_prompt(prompt)
        assert "123-45-6789" not in result['output']
        assert ("[ssn redacted]" in result['output'] or "[personal info redacted]" in result['output'])


class TestBatchProcessing:
    """Test batch processing functionality."""
    
    def test_batch_transform(self):
        """Test that batch processing works correctly."""
        prompts = [
            "I'm blind",
            "My email is test@example.com",
            "I use a wheelchair"
        ]
        
        results = transform_batch(prompts)
        
        assert len(results) == 3
        for result in results:
            assert 'output' in result
            assert 'transformation' in result


class TestLibraryInfo:
    """Test library information functionality."""
    
    def test_get_library_info(self):
        """Test that library info is returned correctly."""
        info = get_library_info()
        
        assert 'version' in info
        assert 'categories' in info
        assert 'features' in info
        assert info['version'] == "1.0.0"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_prompt(self):
        """Test handling of empty prompts."""
        result = transform_prompt("")
        assert result['output'] == ""
    
    def test_no_sensitive_content(self):
        """Test prompt with no sensitive content."""
        prompt = "The weather is nice today"
        result = transform_prompt(prompt)
        assert result['output'] == prompt  # Should be unchanged
        assert len(result['transformation']['context_additions']) == 0
    
    def test_partial_matches(self):
        """Test that partial matches don't trigger false positives."""
        prompt = "I work at the Department of Defense"
        result = transform_prompt(prompt)
        
        # "deaf" in "Defense" should not trigger hearing impairment detection
        assert "Defense" in result['output']  # Should not be redacted


if __name__ == "__main__":
    # Run basic smoke test
    print("Running streamlined smoke test...")
    
    # Test basic functionality
    result = transform_prompt("I'm blind and my email is test@example.com")
    print(f"Input: I'm blind and my email is test@example.com")
    print(f"Output: {result['output']}")
    
    # Test library info
    info = get_library_info()
    print(f"\nLibrary Info: {info}")
    
    print("\nStreamlined smoke test completed successfully!")