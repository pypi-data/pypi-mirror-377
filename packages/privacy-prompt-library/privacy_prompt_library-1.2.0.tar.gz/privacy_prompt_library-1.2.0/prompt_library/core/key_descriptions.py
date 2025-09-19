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

def create_smart_combined_description(descriptions: list, keys: list) -> str:
    """
    Intelligently combine multiple accessibility descriptions, removing redundancy
    and creating a cohesive single description.
    
    Args:
        descriptions: List of individual 60-word descriptions
        keys: Corresponding list of category keys
        
    Returns:
        Smart combined description as a single string
    """
    # Define common terms and their categories for deduplication
    common_accessibility_terms = {
        "screen reader": ["visual"],
        "keyboard navigation": ["visual", "physical"], 
        "captions": ["hearing"],
        "visual alternatives": ["hearing"],
        "step-free access": ["physical"],
        "accessible parking": ["physical"],
        "large print": ["visual"],
        "high contrast": ["visual"],
        "flexible": ["multiple"],
        "supportive": ["multiple"],
        "clear communication": ["hearing", "speech", "intellectual"],
        "simple language": ["intellectual", "speech"],
        "predictable": ["autism"],
        "sensory": ["autism", "multiple"]
    }
    
    # Start with a comprehensive introduction
    intro = "I have comprehensive accessibility needs requiring"
    
    # Extract unique requirements by category
    requirements = []
    
    # Visual requirements
    if any("visual" in key for key in keys):
        requirements.append("screen reader compatibility with detailed text descriptions for all visual content, high contrast display options with customizable color schemes, keyboard navigation support, and large print materials when needed")
    
    # Hearing requirements  
    if any("hearing" in key for key in keys):
        requirements.append("real-time captions for all audio content, visual alternatives to sound-based information, clear written communication, and sign language interpretation when available")
    
    # Physical/mobility requirements
    if any("physical" in key for key in keys):
        requirements.append("step-free building access with ramps and elevators, accessible parking close to entrances, wide doorways and corridors, adjustable furniture and workstation heights")
    
    # Speech/communication requirements
    if any("speech" in key for key in keys):
        requirements.append("patient communication approaches, alternative communication methods, clear speaking pace, and written backup for verbal instructions")
    
    # Intellectual/cognitive requirements
    if any("intellectual" in key or "autism" in key for key in keys):
        requirements.append("simple and clear language, structured information presentation, predictable routines, extra processing time, and multiple format options")
    
    # Progressive/chronic condition requirements
    if any("progressive" in key or "chronic" in key for key in keys):
        requirements.append("flexible scheduling accommodations, energy conservation considerations, adaptive equipment as needed, and symptom management support")
    
    # Maxillofacial requirements
    if any("maxillofacial" in key for key in keys):
        requirements.append("alternative communication methods, dietary accommodations, clear lighting for lip reading, and facial expression interpretation support")
    
    # Combine all requirements into a flowing description
    if len(requirements) == 1:
        combined = f"{intro} {requirements[0]}."
    elif len(requirements) == 2:
        combined = f"{intro} {requirements[0]}, as well as {requirements[1]}."
    else:
        main_requirements = ", ".join(requirements[:-1])
        last_requirement = requirements[-1]
        combined = f"{intro} {main_requirements}, and {last_requirement}."
    
    return combined

def transform_multiple_keys(keys: list, combine_method: str = "smart_combined") -> dict:
    """
    Transform multiple disability category keys into descriptive responses.
    
    Args:
        keys: List of disability category keys
        combine_method: How to combine descriptions:
            - "smart_combined": Intelligently merge descriptions, avoiding redundancy (default)
            - "separate": Return each description separately
            - "simple_combined": Merge all descriptions into one text
            - "prioritized": Combine but prioritize the first key
        
    Returns:
        Dict with transformation results for all keys
    """
    if not isinstance(keys, list):
        return {
            "input": keys,
            "error": "Input must be a list of keys",
            "supported_keys": get_supported_keys()
        }
    
    if not keys:
        return {
            "input": keys,
            "error": "No keys provided",
            "supported_keys": get_supported_keys()
        }
    
    # Transform each key individually
    individual_results = []
    valid_descriptions = []
    errors = []
    
    for key in keys:
        result = transform_by_key(key)
        individual_results.append(result)
        
        if "error" in result:
            errors.append(f"{key}: {result['error']}")
        else:
            valid_descriptions.append(result["output"])
    
    # If there were errors, return them
    if errors:
        return {
            "input": keys,
            "error": "Some keys were invalid: " + "; ".join(errors),
            "valid_results": [r for r in individual_results if "error" not in r],
            "supported_keys": get_supported_keys()
        }
    
    # Combine descriptions based on method
    if combine_method == "smart_combined":
        # Intelligently combine descriptions, removing redundancy
        smart_combined = create_smart_combined_description(valid_descriptions, keys)
        smart_word_count = len(smart_combined.split())
        
        return {
            "input": keys,
            "output": smart_combined,
            "transformation": {
                "type": "multiple_key_descriptions",
                "method": "smart_combined",
                "key_count": len(keys),
                "total_word_count": smart_word_count,
                "compression_ratio": smart_word_count / sum(r["transformation"]["word_count"] for r in individual_results),
                "individual_word_counts": [r["transformation"]["word_count"] for r in individual_results]
            },
            "validation": {
                "combined_word_count": smart_word_count,
                "efficiency_gain": f"{(1 - smart_word_count / sum(r['transformation']['word_count'] for r in individual_results)):.1%}",
                "keys_processed": len(keys)
            },
            "metadata": {
                "processing_type": "multi_key_smart_combined",
                "privacy_level": "high",
                "functional_description": True,
                "redundancy_removed": True
            }
        }
    
    elif combine_method == "separate":
        return {
            "input": keys,
            "output": individual_results,
            "transformation": {
                "type": "multiple_key_descriptions",
                "method": "separate",
                "key_count": len(keys),
                "total_word_count": sum(r["transformation"]["word_count"] for r in individual_results)
            },
            "metadata": {
                "processing_type": "multi_key_separate",
                "privacy_level": "high",
                "functional_description": True
            }
        }
    
    elif combine_method == "simple_combined":
        combined_text = " ".join(valid_descriptions)
        combined_word_count = len(combined_text.split())
        
        return {
            "input": keys,
            "output": combined_text,
            "transformation": {
                "type": "multiple_key_descriptions",
                "method": "simple_combined",
                "key_count": len(keys),
                "total_word_count": combined_word_count,
                "individual_word_counts": [r["transformation"]["word_count"] for r in individual_results]
            },
            "validation": {
                "combined_word_count": combined_word_count,
                "average_per_key": combined_word_count / len(keys),
                "keys_processed": len(keys)
            },
            "metadata": {
                "processing_type": "multi_key_combined",
                "privacy_level": "high", 
                "functional_description": True
            }
        }
    
    elif combine_method == "prioritized":
        # Start with first key as primary, add others as additional needs
        primary_desc = valid_descriptions[0]
        additional_needs = []
        
        for desc in valid_descriptions[1:]:
            # Extract key accessibility features from additional descriptions
            # This is a simplified approach - could be more sophisticated
            words = desc.split()
            if len(words) > 20:
                additional_needs.append(" ".join(words[:20]) + "...")
            else:
                additional_needs.append(desc)
        
        if additional_needs:
            combined_text = f"{primary_desc} Additionally, {' '.join(additional_needs)}"
        else:
            combined_text = primary_desc
            
        combined_word_count = len(combined_text.split())
        
        return {
            "input": keys,
            "output": combined_text,
            "transformation": {
                "type": "multiple_key_descriptions",
                "method": "prioritized",
                "primary_key": keys[0],
                "additional_keys": keys[1:],
                "key_count": len(keys),
                "total_word_count": combined_word_count
            },
            "validation": {
                "combined_word_count": combined_word_count,
                "primary_maintained": True,
                "keys_processed": len(keys)
            },
            "metadata": {
                "processing_type": "multi_key_prioritized",
                "privacy_level": "high",
                "functional_description": True
            }
        }
    
    else:
        return {
            "input": keys,
            "error": f"Invalid combine_method '{combine_method}'. Use 'smart_combined', 'separate', 'simple_combined', or 'prioritized'",
            "supported_methods": ["smart_combined", "separate", "simple_combined", "prioritized"]
        }