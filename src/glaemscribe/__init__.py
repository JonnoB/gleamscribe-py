"""Glaemscribe - A Python implementation of the Glaemscribe transcription engine.

Glaemscribe-py is a Python port of the original Glaemscribe, focused on transcribing
Tolkien's Elvish languages (Quenya and Sindarin) to Tengwar script using Unicode.
It outputs Unicode Private Use Area (PUA) characters compatible with modern Tengwar fonts.

Features:
    - Quenya → Tengwar transcription (Classical mode)
    - Sindarin → Tengwar transcription (General Use and Beleriand modes)
    - English → Tengwar transcription (experimental)
    - Unicode output (PUA U+E000+) compatible with any Unicode Tengwar font
    - Bundled fonts (FreeMonoTengwar, AlcarinTengwar)
    - PNG rendering helpers

Quick Start:
    Install the package:
        pip install -e .
    
    Simple transcription:
        >>> from glaemscribe import transcribe
        >>> result = transcribe("Elen síla lúmenn' omentielvo", mode="quenya")
        >>> print(result)  # Unicode Tengwar output
    
    List available modes:
        >>> from glaemscribe import list_modes
        >>> modes = list_modes()
        >>> print(modes)  # ['quenya', 'sindarin', 'english', ...]

Simple API (recommended for 95% of users):
    The simple functional API provides easy-to-use functions for common tasks:
    
    >>> from glaemscribe import transcribe, list_modes, clear_cache
    >>> 
    >>> # Transcribe Quenya text
    >>> result = transcribe("aiya", mode="quenya")
    >>> 
    >>> # Transcribe Sindarin text
    >>> result = transcribe("mellon", mode="sindarin")
    >>> 
    >>> # List all available modes
    >>> modes = list_modes()
    >>> 
    >>> # Clear mode cache (if needed)
    >>> clear_cache()

Advanced API (for custom modes/charsets):
    For power users who need full control over modes and charsets:
    
    >>> from glaemscribe import Glaemscribe
    >>> from glaemscribe.parsers import ModeParser
    >>> from glaemscribe.resources import get_mode_path
    >>> 
    >>> # Load and parse a mode manually
    >>> parser = ModeParser()
    >>> mode = parser.parse(str(get_mode_path('quenya-tengwar-classical')))
    >>> mode.processor.finalize({})
    >>> success, result, debug = mode.transcribe("aiya")

Available Functions:
    transcribe(text, mode="quenya", charset=None, options=None)
        Main transcription function. Returns transcribed Unicode text.
    
    transcribe_detailed(text, mode="quenya", charset=None, options=None)
        Returns (success, result, debug) tuple with detailed information.
    
    list_modes()
        Returns list of available mode names and aliases.
    
    clear_cache()
        Clears the internal mode cache.

Mode Aliases:
    - "quenya" or "quenya-classical" → quenya-tengwar-classical
    - "sindarin" or "sindarin-general" → sindarin-tengwar-general_use
    - "sindarin-beleriand" → sindarin-tengwar-beleriand
    - "english" → english-tengwar-espeak (experimental)
    - "raw" → raw-tengwar (for direct Tengwar input)

See Also:
    - README.md for installation and usage examples
    - docs/ for comprehensive documentation
    - scripts/simple_usage.py for example code
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
