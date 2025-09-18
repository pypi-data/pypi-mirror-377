"""
Transformation Pipeline
Orchestrates the complete prompt transformation process
"""

import time
from typing import Dict, Any, Optional

from .detector import DetectionEngine
from .redactor import RedactionEngine


class TransformationPipeline:
    """Main pipeline for transforming prompts while preserving privacy."""
    
    def __init__(self, config: Dict[str, Any]):
        self.detection_engine = DetectionEngine(config['patterns'])
        self.redaction_engine = RedactionEngine(config['redaction_rules'])
        self.context_engine = config['context_engine']
        self.validator = config['validator']
        
        # Pipeline configuration
        self.config = {
            'privacy_level': config.get('privacy_level', 'high'),
            'add_context': config.get('add_context', True),
            'preserve_intent': config.get('preserve_intent', True),
            'max_processing_time': config.get('max_processing_time', 5000)
        }
    
    async def transform(self, user_prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main transformation function.
        
        Args:
            user_prompt: Original user prompt
            options: Transformation options
            
        Returns:
            Complete transformation result
        """
        if options is None:
            options = {}
            
        start_time = time.time()
        
        try:
            # Step 1: Input validation
            self.validate_input(user_prompt)
            
            # Step 2: Detection phase
            detection_result = await self.detection_engine.analyze_prompt(user_prompt)
            
            # Step 3: Redaction phase (if detections found)
            redaction_result = {
                'redacted': user_prompt,
                'applied_rules': [],
                'privacy_score': 1.0
            }
            
            if detection_result['has_detections']:
                redaction_result = await self.redaction_engine.redact_prompt(
                    user_prompt,
                    detection_result['detections']
                )
            
            # Step 4: Context addition phase
            context_result = {
                'enhanced': redaction_result['redacted'],
                'added_context': [],
                'functional_score': 1.0
            }
            
            if self.config['add_context'] and detection_result['has_detections']:
                context_result = await self.context_engine.add_context(
                    redaction_result['redacted'],
                    detection_result['detections']
                )
            
            # Step 5: Validation phase
            validation_result = await self.validator['validate'](
                user_prompt,
                context_result['enhanced'],
                detection_result['detections']
            )
            
            # Step 6: Compile final result
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'input': user_prompt,
                'output': context_result['enhanced'],
                'transformation': {
                    'detections': detection_result['detections'],
                    'redactions': redaction_result['applied_rules'],
                    'context_additions': context_result['added_context'],
                    'privacy_score': redaction_result['privacy_score'],
                    'functional_score': context_result['functional_score']
                },
                'validation': validation_result,
                'metadata': {
                    'processing_time_ms': processing_time,
                    'privacy_level': self.config['privacy_level'],
                    'has_transformations': detection_result['has_detections'],
                    'pipeline_version': '1.0.0'
                }
            }
            
        except Exception as error:
            processing_time = (time.time() - start_time) * 1000
            return {
                'input': user_prompt,
                'output': user_prompt,  # Fallback to original
                'error': {
                    'message': str(error),
                    'type': 'pipeline_error'
                },
                'metadata': {
                    'processing_time_ms': processing_time,
                    'privacy_level': self.config['privacy_level'],
                    'has_transformations': False,
                    'pipeline_version': '1.0.0'
                }
            }
    
    def validate_input(self, user_prompt: str) -> None:
        """Validate input prompt."""
        if not user_prompt or not isinstance(user_prompt, str):
            raise ValueError('Input must be a non-empty string')
        
        if len(user_prompt.strip()) == 0:
            raise ValueError('Input cannot be empty or only whitespace')
        
        if len(user_prompt) > 10000:  # Reasonable limit
            raise ValueError('Input prompt too long (max 10,000 characters)')
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            'config': self.config,
            'engines': {
                'detection': True,
                'redaction': True,
                'context': True,
                'validation': True
            },
            'version': '1.0.0'
        }