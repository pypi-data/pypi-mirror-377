"""
Performance and integration tests for Privacy-Preserving Prompt Library
"""

import time
import pytest
from prompt_library import transform_prompt, transform_batch


class TestPerformance:
    """Test performance characteristics of the library."""
    
    def test_single_prompt_performance(self):
        """Test that single prompt transformation is reasonably fast."""
        prompt = "I'm blind and deaf, my email is test@example.com and phone is 555-1234"
        
        start_time = time.time()
        result = transform_prompt(prompt)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert result['output'] != prompt  # Should be transformed
    
    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        prompts = [
            "I have autism and need social support",
            "I use a wheelchair and need accessible venues",
            "I'm deaf and require sign language interpretation",
            "My phone is 555-1234 and email is test@example.com",
            "I have dyslexia and struggle with reading"
        ] * 10  # 50 prompts total
        
        start_time = time.time()
        results = transform_batch(prompts)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert len(results) == 50
        assert processing_time < 30.0  # Should complete within 30 seconds
        
        # Check that all prompts were processed
        for result in results:
            assert 'output' in result
            assert 'transformation' in result
    
    def test_large_prompt_handling(self):
        """Test handling of large prompts."""
        # Create a large prompt with multiple elements
        large_prompt = """
        I am writing to request accommodations for my multiple disabilities.
        I have cerebral palsy and use a wheelchair for mobility. I am also
        legally blind and rely on screen reading technology like JAWS and NVDA.
        Additionally, I have hearing loss and use hearing aids, though I still
        struggle in noisy environments and prefer written communication.
        
        My contact information is as follows:
        - Email: john.accessibility@example.com
        - Phone: 555-123-4567
        - Address: 123 Disability Rights Avenue, Inclusion City, IC 12345
        - SSN: 123-45-6789
        
        I am requesting the following accommodations:
        1. All materials provided in accessible formats (large print, electronic)
        2. Sign language interpreters for meetings
        3. Wheelchair accessible meeting rooms
        4. Additional time for tasks requiring reading
        5. Written follow-up for all verbal instructions
        
        I have attached my medical documentation and would appreciate
        a response within 10 business days. Please let me know if you
        need any additional information to process this request.
        
        Thank you for your time and consideration.
        """
        
        start_time = time.time()
        result = transform_prompt(large_prompt)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 10.0  # Should handle large prompts efficiently
        
        # Verify comprehensive redaction
        output = result['output']
        assert "cerebral palsy" not in output
        assert "wheelchair" not in output
        assert "legally blind" not in output
        assert "john.accessibility@example.com" not in output
        assert "555-123-4567" not in output
        assert "123-45-6789" not in output
        
        # Verify context was added
        assert len(result['transformation']['context_additions']) > 0


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_real_world_accessibility_request(self):
        """Test real-world accessibility request scenario."""
        prompt = """
        Hi, I'm planning a business trip to San Francisco and need help finding
        accessible accommodations. I use a wheelchair and am deaf. My travel
        dates are March 15-20, 2024. 
        
        Please send recommendations to my email: travel.access@company.com
        or call me at 408-555-9876. My assistant Sarah can also be reached
        at sarah.helper@company.com.
        
        I need:
        - Wheelchair accessible hotel rooms
        - Hotels near accessible public transit
        - Restaurants with wheelchair access
        - Meeting venues with sign language interpreters available
        
        My budget is $200-300 per night for hotels.
        """
        
        result = transform_prompt(prompt)
        output = result['output']
        
        # Check that disabilities are redacted but intent preserved
        assert "wheelchair" not in output
        assert "deaf" not in output
        
        # Check that PII is redacted
        assert "travel.access@company.com" not in output
        assert "408-555-9876" not in output
        assert "sarah.helper@company.com" not in output
        
        # Check that functional context is added
        assert "mobility" in output or "step-free" in output
        assert "hearing" in output or "visual alternatives" in output
        
        # Check that non-sensitive content is preserved
        assert "San Francisco" in output
        assert "March" in output
        assert "$200-300" in output
    
    def test_medical_appointment_scenario(self):
        """Test medical appointment scheduling scenario."""
        prompt = """
        I need to schedule an appointment with Dr. Smith. I have multiple
        disabilities including autism, ADHD, and anxiety. I also use a wheelchair.
        
        My insurance information:
        - Member ID: ABC123456789
        - Group: DEF456
        - DOB: 01/15/1985
        
        Contact info:
        - Phone: 555-Medical-1
        - Email: patient@healthcare.com
        
        I need accommodations including:
        - Quiet waiting area (sensory sensitivities)
        - Extra time for appointments
        - Written instructions
        - Wheelchair accessible exam room
        """
        
        result = transform_prompt(prompt)
        output = result['output']
        
        # Check disability redaction
        assert "autism" not in output
        assert "ADHD" not in output
        assert "anxiety" not in output
        assert "wheelchair" not in output
        
        # Check PII redaction
        assert "ABC123456789" not in output
        assert "01/15/1985" not in output
        assert "patient@healthcare.com" not in output
        
        # Check functional context
        assert "predictable" in output or "sensory" in output
        assert "mobility" in output or "step-free" in output
        
        # Preserve important medical context
        assert "Dr. Smith" in output
        assert "appointment" in output


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_input(self):
        """Test handling of malformed input."""
        test_cases = [
            None,
            123,
            [],
            {}
        ]
        
        for test_input in test_cases:
            try:
                result = transform_prompt(test_input)
                # If it doesn't raise an error, check it handles gracefully
                assert 'error' in result or result['output'] == str(test_input)
            except (ValueError, TypeError):
                # Expected behavior for invalid input
                pass
    
    def test_very_long_prompt(self):
        """Test handling of extremely long prompts."""
        # Create a very long prompt
        base_text = "I have autism and my email is test@example.com. "
        long_prompt = base_text * 1000  # ~50,000 characters
        
        result = transform_prompt(long_prompt)
        
        # Should still process without errors
        assert 'output' in result
        assert len(result['output']) > 0
        
        # Should still redact content
        assert "autism" not in result['output']
        assert "test@example.com" not in result['output']
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        prompts = [
            "I'm deaf and my email is test@exämple.com",
            "I use a wheelchair 🦽 and need help",
            "My name is José María and I have dyslexia",
            "I have autism and live at 123 Strasse, München"
        ]
        
        for prompt in prompts:
            result = transform_prompt(prompt)
            assert 'output' in result
            assert len(result['output']) > 0


if __name__ == "__main__":
    # Run performance tests
    print("Running performance tests...")
    
    # Test single prompt
    start = time.time()
    result = transform_prompt("I'm blind and my email is test@example.com")
    single_time = time.time() - start
    print(f"Single prompt processing time: {single_time:.3f} seconds")
    
    # Test batch processing
    prompts = ["I have autism", "I use a wheelchair", "My email is test@example.com"] * 10
    start = time.time()
    results = transform_batch(prompts)
    batch_time = time.time() - start
    print(f"Batch processing time ({len(prompts)} prompts): {batch_time:.3f} seconds")
    print(f"Average per prompt: {batch_time/len(prompts):.3f} seconds")
    
    print("Performance tests completed!")