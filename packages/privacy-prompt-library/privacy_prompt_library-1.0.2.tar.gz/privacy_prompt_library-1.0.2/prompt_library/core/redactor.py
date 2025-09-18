"""
Redaction Engine
Redacts privacy-sensitive terms while preserving prompt functionality
"""

import re
from typing import Dict, List, Any


class RedactionEngine:
    """Engine for redacting privacy-sensitive content from prompts."""
    
    def __init__(self, redaction_rules: Dict[str, Any]):
        self.redaction_rules = redaction_rules
        self.replacement_strategies = self._load_replacement_strategies()
    
    def _load_replacement_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load replacement strategies from rules."""
        strategies = {}
        
        for rule_name, rule_config in self.redaction_rules.items():
            if isinstance(rule_config, dict) and 'replacements' in rule_config:
                strategies[rule_name] = rule_config
        
        return strategies
    
    async def redact_prompt(self, prompt: str, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Redact privacy-sensitive content from prompt.
        
        Args:
            prompt: Original prompt
            detections: List of detected terms to redact
            
        Returns:
            Redaction result with transformed prompt
        """
        if not detections:
            return {
                'redacted': prompt,
                'applied_rules': [],
                'privacy_score': 1.0
            }
        
        redacted_prompt = prompt
        applied_rules = []
        
        # Sort detections by position (reverse order to maintain indices)
        detections_sorted = sorted(detections, key=lambda x: x['start'], reverse=True)
        
        for detection in detections_sorted:
            category = detection['category']
            term = detection['term']
            start = detection['start']
            end = detection['end']
            
            # Find appropriate replacement
            replacement = self._get_replacement(category, term)
            
            if replacement:
                # Apply redaction
                redacted_prompt = (redacted_prompt[:start] + 
                                 replacement + 
                                 redacted_prompt[end:])
                
                applied_rules.append({
                    'original_term': term,
                    'replacement': replacement,
                    'category': category,
                    'position': start,
                    'rule_type': 'pattern_replacement'
                })
        
        privacy_score = self._calculate_privacy_score(prompt, redacted_prompt, applied_rules)
        
        return {
            'redacted': redacted_prompt,
            'applied_rules': applied_rules,
            'privacy_score': privacy_score
        }
    
    def _get_replacement(self, category: str, term: str) -> str:
        """Get appropriate replacement for a detected term."""
        # Default generic replacements
        generic_replacements = {
            'physical-disabilities': 'person with mobility needs',
            'visual-impairments': 'person with visual needs',
            'hearing-impairments': 'person with hearing needs',
            'speech-language': 'person with communication needs',
            'intellectual-disabilities': 'person with cognitive support needs',
            'learning-disabilities': 'person with learning support needs',
            'autism-spectrum': 'person with neurodivergent needs',
            'mental-health': 'person with mental health considerations',
            'medical-conditions': 'person with medical considerations'
        }
        
        # Check for specific replacements in rules
        if category in self.replacement_strategies:
            replacements = self.replacement_strategies[category].get('replacements', {})
            
            # Look for exact match
            term_lower = term.lower()
            for pattern, replacement in replacements.items():
                if re.search(pattern, term_lower, re.IGNORECASE):
                    return replacement
        
        # Fall back to generic replacement
        return generic_replacements.get(category, 'person with specific needs')
    
    def _calculate_privacy_score(self, original: str, redacted: str, applied_rules: List[Dict]) -> float:
        """Calculate privacy protection score."""
        if not applied_rules:
            return 1.0
        
        # Base score on completeness of redaction
        sensitive_terms_redacted = len(applied_rules)
        
        # Check if any obvious medical terms remain
        medical_indicators = [
            'paralyzed', 'wheelchair', 'blind', 'deaf', 'autistic',
            'depression', 'anxiety', 'bipolar', 'adhd', 'disability'
        ]
        
        remaining_terms = sum(1 for term in medical_indicators 
                            if term in redacted.lower())
        
        # Calculate score (1.0 = perfect privacy, 0.0 = no privacy)
        if remaining_terms == 0:
            return 1.0
        else:
            # Penalize remaining terms
            return max(0.0, 1.0 - (remaining_terms * 0.2))
    
    def get_redaction_stats(self) -> Dict[str, Any]:
        """Get redaction engine statistics."""
        total_strategies = len(self.replacement_strategies)
        total_replacements = sum(
            len(strategy.get('replacements', {})) 
            for strategy in self.replacement_strategies.values()
        )
        
        return {
            'total_strategies': total_strategies,
            'total_replacements': total_replacements,
            'categories': list(self.replacement_strategies.keys()),
            'engine_version': '1.0.0'
        }