"""
Detection Engine
Identifies disability-related terms and medical information in prompts
"""

import re
from typing import Dict, List, Any


class DetectionEngine:
    """Engine for detecting privacy-sensitive terms in prompts."""
    
    def __init__(self, patterns: Dict[str, Any]):
        self.patterns = patterns
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficient matching."""
        compiled = {}
        
        for category, category_patterns in self.patterns.items():
            compiled[category] = []
            if isinstance(category_patterns, dict) and 'patterns' in category_patterns:
                for pattern in category_patterns['patterns']:
                    try:
                        compiled[category].append(re.compile(pattern, re.IGNORECASE))
                    except re.error:
                        # Skip invalid patterns
                        continue
        
        return compiled
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze prompt for privacy-sensitive content.
        
        Args:
            prompt: Input prompt to analyze
            
        Returns:
            Detection result with found terms and categories
        """
        detections = []
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(prompt)
                for match in matches:
                    detections.append({
                        'category': category,
                        'term': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.95,  # High confidence for pattern matches
                        'severity': self._get_severity(category)
                    })
        
        # Remove duplicates and sort by position
        detections = self._deduplicate_detections(detections)
        detections.sort(key=lambda x: x['start'])
        
        return {
            'has_detections': len(detections) > 0,
            'detection_count': len(detections),
            'detections': detections,
            'categories_found': list(set(d['category'] for d in detections)),
            'privacy_risk_score': self._calculate_risk_score(detections)
        }
    
    def _get_severity(self, category: str) -> str:
        """Get severity level for a category."""
        high_severity = [
            'medical-conditions',
            'physical-disabilities', 
            'mental-health',
            'genetic-disorders'
        ]
        
        if category in high_severity:
            return 'high'
        elif 'disability' in category or 'impairment' in category:
            return 'medium'
        else:
            return 'low'
    
    def _deduplicate_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate detections based on overlapping positions."""
        if not detections:
            return []
        
        # Sort by start position
        detections.sort(key=lambda x: x['start'])
        
        unique_detections = []
        
        for detection in detections:
            # Check if this detection overlaps with any existing unique detection
            overlaps = False
            for unique in unique_detections:
                if (detection['start'] < unique['end'] and 
                    detection['end'] > unique['start']):
                    overlaps = True
                    break
            
            if not overlaps:
                unique_detections.append(detection)
        
        return unique_detections
    
    def _calculate_risk_score(self, detections: List[Dict[str, Any]]) -> float:
        """Calculate overall privacy risk score."""
        if not detections:
            return 0.0
        
        # Base score on number and severity of detections
        high_severity_count = sum(1 for d in detections if d['severity'] == 'high')
        medium_severity_count = sum(1 for d in detections if d['severity'] == 'medium')
        low_severity_count = sum(1 for d in detections if d['severity'] == 'low')
        
        # Weighted score
        score = (high_severity_count * 0.8 + 
                medium_severity_count * 0.5 + 
                low_severity_count * 0.2)
        
        # Normalize to 0-1 range
        return min(score / 5.0, 1.0)  # Assume max 5 detections for normalization
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection engine statistics."""
        total_patterns = sum(len(patterns) for patterns in self.compiled_patterns.values())
        
        return {
            'total_categories': len(self.compiled_patterns),
            'total_patterns': total_patterns,
            'categories': list(self.compiled_patterns.keys()),
            'engine_version': '1.0.0'
        }