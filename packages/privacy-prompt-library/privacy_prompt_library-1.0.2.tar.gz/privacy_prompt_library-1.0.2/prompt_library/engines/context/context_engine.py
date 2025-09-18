"""
Context Engine
Adds functional context to maintain prompt effectiveness after redaction
"""

from typing import Dict, List, Any


class ContextEngine:
    """Engine for adding functional context to redacted prompts."""
    
    def __init__(self, context_library: Dict[str, Any]):
        self.context_library = context_library
        self.context_mappings = self._load_context_mappings()
    
    def _load_context_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load context mappings from library."""
        mappings = {}
        
        for category, config in self.context_library.items():
            if isinstance(config, dict) and 'contexts' in config:
                mappings[category] = config
        
        return mappings
    
    async def add_context(self, redacted_prompt: str, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add functional context to maintain prompt effectiveness.
        
        Args:
            redacted_prompt: Prompt after redaction
            detections: Original detections that were redacted
            
        Returns:
            Enhanced prompt with functional context
        """
        if not detections:
            return {
                'enhanced': redacted_prompt,
                'added_context': [],
                'functional_score': 1.0
            }
        
        enhanced_prompt = redacted_prompt
        added_context = []
        
        # Group detections by category
        categories_detected = set(detection['category'] for detection in detections)
        
        for category in categories_detected:
            context_info = self._get_context_for_category(category)
            
            if context_info:
                # Add context at the end of the prompt
                context_text = context_info['text']
                enhanced_prompt = f"{enhanced_prompt}\n\n{context_text}"
                
                added_context.append({
                    'category': category,
                    'context_type': context_info['type'],
                    'text': context_text,
                    'purpose': context_info['purpose']
                })
        
        functional_score = self._calculate_functional_score(
            redacted_prompt, enhanced_prompt, added_context
        )
        
        return {
            'enhanced': enhanced_prompt,
            'added_context': added_context,
            'functional_score': functional_score
        }
    
    def _get_context_for_category(self, category: str) -> Dict[str, str]:
        """Get appropriate context for a category."""
        # Default contexts for common categories
        default_contexts = {
            'physical-disabilities': {
                'type': 'accessibility_requirements',
                'text': 'Please ensure any solutions consider accessibility requirements and provide alternative interaction methods.',
                'purpose': 'Maintain awareness of accessibility needs'
            },
            'visual-impairments': {
                'type': 'visual_accessibility',
                'text': 'Please ensure any visual content includes text descriptions and is compatible with screen readers.',
                'purpose': 'Maintain visual accessibility requirements'
            },
            'hearing-impairments': {
                'type': 'audio_accessibility',
                'text': 'Please ensure any audio content includes captions or transcripts.',
                'purpose': 'Maintain audio accessibility requirements'
            },
            'cognitive-disabilities': {
                'type': 'cognitive_accessibility',
                'text': 'Please ensure content is clear, simple, and includes additional explanations when needed.',
                'purpose': 'Maintain cognitive accessibility requirements'
            },
            'learning-disabilities': {
                'type': 'learning_support',
                'text': 'Please provide multiple ways to access and understand information.',
                'purpose': 'Maintain learning support requirements'
            },
            'autism-spectrum': {
                'type': 'neurodiversity_support',
                'text': 'Please consider neurodivergent perspectives and provide clear structure and expectations.',
                'purpose': 'Maintain neurodiversity considerations'
            },
            'mental-health': {
                'type': 'mental_health_awareness',
                'text': 'Please be mindful of mental health considerations in any recommendations.',
                'purpose': 'Maintain mental health awareness'
            }
        }
        
        # Check custom contexts first
        if category in self.context_mappings:
            contexts = self.context_mappings[category].get('contexts', [])
            if contexts and isinstance(contexts, list) and len(contexts) > 0:
                # Use first available context
                context = contexts[0]
                if isinstance(context, dict):
                    return {
                        'type': context.get('type', 'general'),
                        'text': context.get('text', ''),
                        'purpose': context.get('purpose', 'Maintain functional context')
                    }
        
        # Fall back to default
        return default_contexts.get(category, {
            'type': 'general_accessibility',
            'text': 'Please consider accessibility and inclusion in any solutions.',
            'purpose': 'Maintain general accessibility awareness'
        })
    
    def _calculate_functional_score(self, redacted: str, enhanced: str, contexts: List[Dict]) -> float:
        """Calculate functional preservation score."""
        if not contexts:
            return 0.8  # Moderate score without context
        
        # Base score on amount and quality of added context
        base_score = 0.9
        
        # Boost for multiple relevant contexts
        context_boost = min(len(contexts) * 0.02, 0.1)
        
        # Check if context is meaningful (not too generic)
        meaningful_contexts = sum(
            1 for context in contexts 
            if len(context['text']) > 50  # Reasonable length threshold
        )
        
        meaning_boost = (meaningful_contexts / len(contexts)) * 0.05
        
        return min(base_score + context_boost + meaning_boost, 1.0)
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context engine statistics."""
        total_categories = len(self.context_mappings)
        total_contexts = sum(
            len(mapping.get('contexts', [])) 
            for mapping in self.context_mappings.values()
        )
        
        return {
            'total_categories': total_categories,
            'total_contexts': total_contexts,
            'categories': list(self.context_mappings.keys()),
            'engine_version': '1.0.0'
        }