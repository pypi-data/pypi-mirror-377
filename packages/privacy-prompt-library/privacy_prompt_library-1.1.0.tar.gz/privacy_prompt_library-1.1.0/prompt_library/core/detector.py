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
        """Compile regex patterns for efficient matching, including subgroups."""
        compiled = {}
        
        # Process disability categories first (higher priority)
        disability_categories = [
            'Physical Disabilities', 'Visual Impairments', 'Hearing Impairments', 
            'Learning Disabilities', 'Autism Spectrum', 'Mental Health', 
            'Intellectual Disabilities', 'Other Disabilities'
        ]
        
        for category, category_data in self.patterns.items():
            if category in disability_categories:
                compiled[category] = []
                # Traverse subgroups if present
                if isinstance(category_data, dict) and 'subgroups' in category_data:
                    for subgroup, patterns_list in category_data['subgroups'].items():
                        for pattern_obj in patterns_list:
                            pattern = pattern_obj.get('pattern')
                            if pattern:
                                try:
                                    compiled[category].append(re.compile(pattern, re.IGNORECASE))
                                except re.error:
                                    continue
                # Also check for direct 'patterns' key (legacy)
                if isinstance(category_data, dict) and 'patterns' in category_data:
                    for pattern in category_data['patterns']:
                        try:
                            compiled[category].append(re.compile(pattern, re.IGNORECASE))
                        except re.error:
                            continue
        
        # Then process PII categories (lower priority)
        for category, category_data in self.patterns.items():
            if category not in disability_categories:
                compiled[category] = []
                # Traverse subgroups if present
                if isinstance(category_data, dict) and 'subgroups' in category_data:
                    for subgroup, patterns_list in category_data['subgroups'].items():
                        for pattern_obj in patterns_list:
                            pattern = pattern_obj.get('pattern')
                            if pattern:
                                try:
                                    compiled[category].append(re.compile(pattern, re.IGNORECASE))
                                except re.error:
                                    continue
                # Also check for direct 'patterns' key (legacy)
                if isinstance(category_data, dict) and 'patterns' in category_data:
                    for pattern in category_data['patterns']:
                        try:
                            compiled[category].append(re.compile(pattern, re.IGNORECASE))
                        except re.error:
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
        used_positions = set()  # Track positions to avoid overlaps
        
        # Process disability categories first (higher priority)
        disability_categories = [
            'Physical Disabilities', 'Visual Impairments', 'Hearing Impairments', 
            'Learning Disabilities', 'Autism Spectrum', 'Mental Health', 
            'Intellectual Disabilities', 'Other Disabilities'
        ]
        
        for category in disability_categories:
            if category in self.compiled_patterns:
                patterns = self.compiled_patterns[category]
                for pattern in patterns:
                    matches = pattern.finditer(prompt)
                    for match in matches:
                        start, end = match.start(), match.end()
                        # Check for overlap with existing detections
                        overlap = any(pos in range(start, end) for pos in used_positions)
                        if not overlap:
                            detections.append({
                                'category': category,
                                'term': match.group(),
                                'start': start,
                                'end': end,
                                'confidence': 0.95,
                                'severity': self._get_severity(category)
                            })
                            # Mark this range as used
                            used_positions.update(range(start, end))
        
        # Then process PII categories (lower priority, avoid overlaps)
        for category, patterns in self.compiled_patterns.items():
            if category not in disability_categories:
                for pattern in patterns:
                    matches = pattern.finditer(prompt)
                    for match in matches:
                        start, end = match.start(), match.end()
                        # Check for overlap with existing detections
                        overlap = any(pos in range(start, end) for pos in used_positions)
                        if not overlap:
                            detections.append({
                                'category': category,
                                'term': match.group(),
                                'start': start,
                                'end': end,
                                'confidence': 0.95,
                                'severity': self._get_severity(category)
                            })
                            # Mark this range as used
                            used_positions.update(range(start, end))
        
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