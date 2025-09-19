"""
Key-based disability descriptions without disclosing specific conditions.
Returns 60-word functional descriptions for accessibility categories.
"""

# 60-word descriptive strings for each disability category key
KEY_DESCRIPTIONS = {
    "visual-impairment": """I have specific visual accessibility needs requiring comprehensive screen reader compatibility, high contrast display options with customizable color schemes, detailed text descriptions for all visual content including images, alternative format documents in accessible formats, large print materials when needed, audio descriptions for multimedia content, tactile feedback options, keyboard navigation support, and accessible navigation systems that work seamlessly with assistive technology.""",
    
    "hearing-impairment": """I require hearing accessibility accommodations including real-time captions for all audio content and live presentations, professional sign language interpretation services, written communication alternatives for verbal instructions, visual alert systems for notifications, accessible video conferencing platforms with captioning capabilities, quiet environments for optimal hearing aid function, clear visual cues to supplement auditory information, and accessible emergency systems with visual alerts.""",
    
    "physical-disability": """I need comprehensive physical accessibility features including step-free building access with ramps, reliable elevator availability, accessible parking spaces near main entrances, wide doorways and pathways for easy navigation, adjustable height surfaces and workstations, accessible restroom facilities with grab bars and adequate space, mobility equipment accommodation areas, ergonomic workspace arrangements, and accessible emergency evacuation procedures for comfortable navigation and full participation.""",
    
    "speech-language-communication-and-swallowing-disability": """I require communication accommodations including extended time for verbal responses without pressure, alternative communication methods and assistive technology, written communication options for complex information, assistive communication technology support and training, patient listeners who understand diverse communication styles, quiet environments for clearer communication, flexible interaction formats that accommodate individual needs, and backup communication methods for conversations.""",
    
    "speech-intellectual-autism-spectrum-disorders": """I benefit from structured environments with predictable routines and clear expectations, step-by-step instructions with visual supports, sensory-friendly spaces with minimal overwhelming stimuli and noise reduction, extra processing time for complex information, visual supports and schedules to aid understanding, consistent communication patterns and familiar procedures, accommodations that recognize diverse learning styles and social interaction preferences, and flexible scheduling.""",
    
    "maxillofacial-disabilities": """I need accommodations for facial and oral function differences including alternative communication methods when speech is affected by facial structures, flexible eating arrangements and accessible dining options, accessible restroom facilities with privacy considerations, private spaces when needed for personal care, understanding of facial appearance variations without assumptions, supportive environments that prioritize comfort and dignity, and accessible emergency procedures that consider communication needs.""",
    
    "progressive-chronic-disorders": """I require flexible accommodations that adapt to changing daily capabilities including adjustable work schedules based on energy levels, fatigue management support with rest periods, accessible seating options and ergonomic furniture, climate control considerations for comfort, backup plans for symptom fluctuations and unpredictable needs, energy conservation strategies and efficient workflows, understanding of variable daily functioning levels, and adaptive equipment that adjusts."""
}

def get_description_for_key(key: str) -> str:
    """
    Get a 60-word description for a disability category key.
    
    Args:
        key: One of the supported disability category keys
        
    Returns:
        60-word descriptive string without disclosing specific conditions
        
    Raises:
        ValueError: If key is not supported
    """
    if key not in KEY_DESCRIPTIONS:
        supported_keys = list(KEY_DESCRIPTIONS.keys())
        raise ValueError(f"Unsupported key '{key}'. Supported keys: {supported_keys}")
    
    return KEY_DESCRIPTIONS[key]

def get_supported_keys() -> list:
    """Get list of all supported disability category keys."""
    return list(KEY_DESCRIPTIONS.keys())

def validate_word_count(text: str, target_count: int = 60) -> dict:
    """
    Validate that a description meets the target word count.
    
    Args:
        text: Text to validate
        target_count: Expected word count (default: 60)
        
    Returns:
        Dict with validation results
    """
    words = text.split()
    word_count = len(words)
    
    return {
        "word_count": word_count,
        "target_count": target_count,
        "meets_target": word_count == target_count,
        "difference": word_count - target_count
    }

def transform_by_key(key: str) -> dict:
    """
    Transform a disability category key into a descriptive response.
    
    Args:
        key: Disability category key
        
    Returns:
        Dict with transformation results
    """
    try:
        description = get_description_for_key(key)
        validation = validate_word_count(description)
        
        return {
            "input": key,
            "output": description,
            "transformation": {
                "type": "key_based_description",
                "category": key,
                "word_count": validation["word_count"],
                "meets_target": validation["meets_target"]
            },
            "validation": validation,
            "metadata": {
                "processing_type": "key_based",
                "privacy_level": "high",
                "functional_description": True
            }
        }
    except ValueError as e:
        return {
            "input": key,
            "error": str(e),
            "supported_keys": get_supported_keys()
        }