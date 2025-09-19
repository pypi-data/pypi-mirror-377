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
        # Aggressive, specific contexts for common categories
        default_contexts = {
            'Physical Disabilities': {
                'type': 'mobility_accessibility',
                'text': 'I use mobility equipment and need step-free access to buildings, accessible parking close to entrances, elevator access for multi-story locations, wide pathways, and accessible restrooms with grab bars. Please ensure all recommendations include detailed accessibility information and consider transfer needs.',
                'purpose': 'Maintain mobility accessibility requirements'
            },
            'Visual Impairments': {
                'type': 'visual_accessibility',
                'text': 'I use screen readers and need all visual content to include detailed text descriptions, alt-text for images, high contrast options, and compatibility with assistive technology. Please ensure any recommended websites, apps, or documents are fully screen reader accessible.',
                'purpose': 'Maintain visual accessibility requirements'
            },
            'Hearing Impairments': {
                'type': 'audio_accessibility',
                'text': 'I have hearing considerations and need visual alternatives for audio content, including captions, transcripts, sign language interpretation options, and visual alerts. Please ensure any audio-based recommendations include these accommodations.',
                'purpose': 'Maintain audio accessibility requirements'
            },
            'Learning Disabilities': {
                'type': 'learning_support',
                'text': 'I benefit from multiple learning formats including text-to-speech options, simplified language, clear structure with headings, step-by-step instructions, and additional time for processing information. Please provide recommendations that accommodate different learning styles.',
                'purpose': 'Maintain learning support requirements'
            },
            'Autism Spectrum': {
                'type': 'neurodiversity_support',
                'text': 'I work best with predictable environments, clear expectations, sensory considerations (quiet spaces, minimal overwhelming stimuli), structured information, and advance notice of changes. Please factor these neurodivergent needs into any recommendations.',
                'purpose': 'Maintain neurodiversity considerations'
            },
            'Mental Health': {
                'type': 'mental_health_support',
                'text': 'I benefit from flexible scheduling, stress management considerations, supportive environments, and options that accommodate variable energy levels. Please ensure recommendations consider mental health wellness and include backup plans when possible.',
                'purpose': 'Maintain mental health considerations'
            },
            'Intellectual Disabilities': {
                'type': 'cognitive_support',
                'text': 'I need clear, simple language, step-by-step instructions, visual aids when possible, extra time for processing, and patient, supportive interactions. Please ensure recommendations are presented in an accessible, easy-to-understand format.',
                'purpose': 'Maintain cognitive accessibility requirements'
            },
            'Other Disabilities': {
                'type': 'comprehensive_accessibility',
                'text': 'I have specific accessibility needs that require comprehensive accommodations including flexible timing, multiple format options, assistive technology compatibility, and inclusive design principles. Please ensure all recommendations prioritize universal accessibility.',
                'purpose': 'Maintain comprehensive accessibility requirements'
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
        
        # Fall back to default - use exact category match or general fallback
        if category in default_contexts:
            return default_contexts[category]
        
        # Generic fallback for any unrecognized categories
        return {
            'type': 'general_accessibility',
            'text': 'I have specific accessibility needs that require accommodations including flexible options, inclusive design, and barrier-free access. Please ensure all recommendations prioritize accessibility and inclusion.',
            'purpose': 'Maintain general accessibility awareness'
        }
    
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