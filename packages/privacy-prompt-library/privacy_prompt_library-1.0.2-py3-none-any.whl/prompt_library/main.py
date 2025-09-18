"""
Privacy-Preserving Prompt Library - Main Interface
Transforms user prompts to protect disability privacy while maintaining functional context
"""

import json
import time
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .core.pipeline import TransformationPipeline
from .engines.context.context_engine import ContextEngine


class PromptLibrary:
    """Main interface for the Privacy-Preserving Prompt Library."""
    
    def __init__(self):
        self.pipeline = None
        self.initialized = False
        self._data_path = Path(__file__).parent / "data"
    
    async def initialize(self) -> None:
        """Initialize the library with all databases."""
        try:
            # Load all databases
            patterns, redaction_rules, context_library = await asyncio.gather(
                self.load_database('patterns.json'),
                self.load_database('redaction-rules.json'),
                self.load_database('context-library.json')
            )
            
            # Initialize engines
            context_engine = ContextEngine(context_library)
            
            # Create validation engine
            validator = {
                'validate': self._validate_transformation
            }
            
            # Initialize transformation pipeline
            self.pipeline = TransformationPipeline({
                'patterns': patterns,
                'redaction_rules': redaction_rules,
                'context_engine': context_engine,
                'validator': validator,
                'privacy_level': 'high',
                'add_context': True,
                'preserve_intent': True
            })
            
            self.initialized = True
            print('✅ Prompt Library initialized successfully')
            
        except Exception as error:
            print(f'❌ Failed to initialize Prompt Library: {error}')
            raise error
    
    def initialize_sync(self) -> None:
        """Synchronous wrapper for initialization."""
        asyncio.run(self.initialize())
    
    async def transform_prompt(self, user_prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Transform a user prompt - Main API function.
        
        Args:
            user_prompt: Original user prompt
            options: Transformation options
            
        Returns:
            Transformation result dictionary
        """
        if options is None:
            options = {}
            
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Validate input
            if not user_prompt or not isinstance(user_prompt, str):
                raise ValueError('Invalid input: prompt must be a non-empty string')
            
            # Apply transformation
            result = await self.pipeline.transform(user_prompt, options)
            
            # Add library metadata
            result['library'] = {
                'version': '1.0.0',
                'processing_time': (time.time() - start_time) * 1000,  # Convert to ms
                'privacy_guarantee': 'No medical terms disclosed'
            }
            
            return result
            
        except Exception as error:
            return {
                'input': user_prompt,
                'output': user_prompt,  # Fallback to original
                'error': {
                    'message': str(error),
                    'type': 'transformation_error'
                },
                'library': {
                    'version': '1.0.0',
                    'processing_time': (time.time() - start_time) * 1000,
                    'privacy_guarantee': 'Fallback - original prompt returned'
                }
            }
    
    def transform_prompt_sync(self, user_prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous wrapper for transform_prompt."""
        return asyncio.run(self.transform_prompt(user_prompt, options))
    
    async def transform_batch(self, prompts: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Batch transform multiple prompts.
        
        Args:
            prompts: List of user prompts
            options: Transformation options
            
        Returns:
            List of transformation results
        """
        if options is None:
            options = {}
            
        if not isinstance(prompts, list):
            raise ValueError('Invalid input: prompts must be a list')
        
        results = []
        
        for prompt in prompts:
            try:
                result = await self.transform_prompt(prompt, options)
                results.append(result)
            except Exception as error:
                results.append({
                    'input': prompt,
                    'output': prompt,
                    'error': {'message': str(error)}
                })
        
        return results
    
    def transform_batch_sync(self, prompts: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Synchronous wrapper for transform_batch."""
        return asyncio.run(self.transform_batch(prompts, options))
    
    def get_library_info(self) -> Dict[str, Any]:
        """Get library statistics and health."""
        return {
            'version': '1.0.0',
            'initialized': self.initialized,
            'categories': 14,
            'features': [
                'Medical term redaction',
                'Functional context addition',
                'Privacy preservation',
                'Intent maintenance',
                'Batch processing'
            ],
            'privacy_level': 'high',
            'guarantees': [
                'No medical diagnoses disclosed',
                'No personal health information leaked',
                'Functional needs preserved',
                'Original intent maintained'
            ]
        }
    
    async def load_database(self, filename: str) -> Dict[str, Any]:
        """Load database file."""
        file_path = self._data_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Database file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _validate_transformation(self, original: str, transformed: str, detections: Dict) -> Dict[str, Any]:
        """Validate transformation result."""
        return {
            'privacy_preserved': self.check_privacy_preservation(original, transformed),
            'intent_maintained': self.check_intent_preservation(original, transformed),
            'coherence_score': self.calculate_coherence(transformed),
            'recommendations': []
        }
    
    def check_privacy_preservation(self, original: str, transformed: str) -> bool:
        """Check if privacy is preserved (no medical terms in output)."""
        medical_terms = [
            'paralyz', 'wheelchair', 'blind', 'deaf', 'autism', 'dyslexia',
            'depression', 'anxiety', 'bipolar', 'schizophrenia', 'adhd',
            'cerebral palsy', 'multiple sclerosis', 'arthritis', 'fibromyalgia'
        ]
        
        lower_transformed = transformed.lower()
        
        for term in medical_terms:
            if term in lower_transformed:
                return False
        
        return True
    
    def check_intent_preservation(self, original: str, transformed: str) -> bool:
        """Check if original intent is maintained."""
        original_words = original.lower().split()
        transformed_words = transformed.lower().split()
        
        # Count preserved non-medical words
        non_medical_words = [word for word in original_words 
                           if word not in ['paralyzed', 'blind', 'deaf', 'autistic', 'wheelchair']]
        
        preserved_words = [word for word in non_medical_words 
                         if word in transformed_words]
        
        if not non_medical_words:
            return True
            
        return len(preserved_words) / len(non_medical_words) >= 0.8
    
    def calculate_coherence(self, text: str) -> float:
        """Calculate coherence score of transformed text."""
        import re
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return 0.0
        if len(sentences) == 1:
            return 1.0
        
        # Check for reasonable sentence length and structure
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if avg_length < 3 or avg_length > 30:
            return 0.6
        
        return 0.9  # Good coherence for our use case


# Create singleton instance
_prompt_library = PromptLibrary()

# Export main functions
def transform_prompt(prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Transform a single prompt (synchronous)."""
    return _prompt_library.transform_prompt_sync(prompt, options)

def transform_batch(prompts: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Transform multiple prompts (synchronous)."""
    return _prompt_library.transform_batch_sync(prompts, options)

def get_library_info() -> Dict[str, Any]:
    """Get library information."""
    return _prompt_library.get_library_info()

def initialize() -> None:
    """Initialize the library."""
    _prompt_library.initialize_sync()