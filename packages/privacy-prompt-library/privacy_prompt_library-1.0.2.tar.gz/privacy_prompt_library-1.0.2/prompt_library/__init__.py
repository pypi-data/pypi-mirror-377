"""
Privacy-Preserving Prompt Library

A privacy-preserving prompt transformation library that redacts disability mentions 
while maintaining functional context for AI interactions.
"""

__version__ = "1.0.2"
__author__ = "Accessibility Team"
__email__ = "accessibility@example.com"

from .main import PromptLibrary, transform_prompt, transform_batch, get_library_info, initialize
from .core.pipeline import TransformationPipeline
from .core.detector import DetectionEngine
from .core.redactor import RedactionEngine
from .engines.context.context_engine import ContextEngine

__all__ = [
    "PromptLibrary",
    "TransformationPipeline", 
    "DetectionEngine",
    "RedactionEngine",
    "ContextEngine",
    "transform_prompt",
    "transform_batch", 
    "get_library_info",
    "initialize"
]