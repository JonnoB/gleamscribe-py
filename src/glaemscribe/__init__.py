"""Glaemscribe - A Python implementation of the Glaemscribe transcription engine.

Simple API (recommended):
    >>> from glaemscribe import transcribe, list_modes
    >>> result = transcribe("Elen síla lúmenn' omentielvo", mode="quenya")
    >>> print(result)  # Unicode Tengwar output
    
    >>> modes = list_modes()
    >>> print(modes)  # ['quenya', 'sindarin', ...]

Advanced API (for custom modes/charsets):
    >>> from glaemscribe import Glaemscribe
    >>> from glaemscribe.parsers import ModeParser
    >>> # ... advanced usage ...
"""

__version__ = "0.1.0"

# Simple functional API (recommended for most users)
from .api import transcribe, transcribe_detailed, list_modes, clear_cache

# Advanced/legacy class-based API
from .api import Glaemscribe

# Core classes (for advanced usage)
from .core import Charset, Mode, TranscriptionRule

__all__ = [
    # Simple API
    "transcribe",
    "transcribe_detailed", 
    "list_modes",
    "clear_cache",
    # Advanced API
    "Glaemscribe",
    "Charset",
    "Mode",
    "TranscriptionRule",
]
