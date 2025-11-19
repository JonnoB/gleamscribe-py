"""Public API for Glaemscribe.

This module provides both a simple functional API for common use cases
and a class-based API for advanced usage.

Simple API (recommended for most users):
    >>> from glaemscribe import transcribe
    >>> result = transcribe("Elen síla lúmenn' omentielvo", mode="quenya")
    >>> print(result)  # Unicode Tengwar output

Advanced API:
    >>> from glaemscribe import Glaemscribe
    >>> gs = Glaemscribe()
    >>> # ... configure modes and charsets ...
"""

from typing import Dict, List, Optional, Tuple
from .parsers.mode_parser import ModeParser
from .resources import get_mode_path


# Mode name aliases for convenience
MODE_ALIASES = {
    "quenya": "quenya-tengwar-classical",
    "quenya-classical": "quenya-tengwar-classical",
    "sindarin": "sindarin-tengwar-general_use",
    "sindarin-general": "sindarin-tengwar-general_use",
    "sindarin-beleriand": "sindarin-tengwar-beleriand",
    "english": "english-tengwar-espeak",
    "raw": "raw-tengwar",
}

# Cache for loaded modes to avoid re-parsing
_mode_cache = {}


def transcribe(
    text: str,
    mode: str = "quenya",
    charset: Optional[str] = None,
    options: Optional[Dict] = None
) -> str:
    """Transcribe text to Tengwar script.
    
    This is the main high-level API for transcription. It handles mode loading,
    caching, and returns just the transcribed text.
    
    Args:
        text: The text to transcribe (e.g., "Elen síla lúmenn' omentielvo")
        mode: Mode name or alias. Common values:
            - "quenya" or "quenya-classical" (default)
            - "sindarin" or "sindarin-general"
            - "sindarin-beleriand"
            - "english"
            - "raw"
        charset: Optional charset name (default: tengwar_freemono)
        options: Optional dict of mode-specific options
        
    Returns:
        Transcribed text as Unicode Tengwar (PUA characters U+E000+)
        
    Raises:
        ValueError: If mode is not found or transcription fails
        
    Examples:
        >>> # Simple Quenya transcription
        >>> transcribe("aiya")
        
        >>> # Sindarin transcription
        >>> transcribe("mellon", mode="sindarin")
        
        >>> # With explicit mode name
        >>> transcribe("test", mode="quenya-tengwar-classical")
    """
    # Resolve mode alias
    mode_name = MODE_ALIASES.get(mode, mode)
    
    # Load mode from cache or parse it
    if mode_name not in _mode_cache:
        try:
            mode_path = get_mode_path(mode_name)
            parser = ModeParser()
            mode_obj = parser.parse(str(mode_path))
            mode_obj.processor.finalize(options or {})
            _mode_cache[mode_name] = mode_obj
        except FileNotFoundError:
            available = list_modes()
            raise ValueError(
                f"Mode '{mode}' not found. Available modes: {', '.join(available)}"
            )
    
    mode_obj = _mode_cache[mode_name]
    success, result, debug = mode_obj.transcribe(text, charset=charset)
    
    if not success:
        raise ValueError(f"Transcription failed: {result}")
    
    return result


def transcribe_detailed(
    text: str,
    mode: str = "quenya",
    charset: Optional[str] = None,
    options: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """Transcribe text with detailed results.
    
    Like transcribe() but returns the full result tuple including success
    status and debug information.
    
    Args:
        text: The text to transcribe
        mode: Mode name or alias
        charset: Optional charset name
        options: Optional dict of mode-specific options
        
    Returns:
        Tuple of (success, result, debug_info)
        
    Examples:
        >>> success, result, debug = transcribe_detailed("aiya")
        >>> if success:
        ...     print(result)
        ... else:
        ...     print(f"Error: {debug}")
    """
    mode_name = MODE_ALIASES.get(mode, mode)
    
    if mode_name not in _mode_cache:
        try:
            mode_path = get_mode_path(mode_name)
            parser = ModeParser()
            mode_obj = parser.parse(str(mode_path))
            mode_obj.processor.finalize(options or {})
            _mode_cache[mode_name] = mode_obj
        except FileNotFoundError:
            available = list_modes()
            return False, f"Mode '{mode}' not found", f"Available: {', '.join(available)}"
    
    mode_obj = _mode_cache[mode_name]
    return mode_obj.transcribe(text, charset=charset)


def list_modes() -> List[str]:
    """List all available transcription modes.
    
    Returns:
        List of mode names (both full names and aliases)
        
    Examples:
        >>> modes = list_modes()
        >>> print(modes)
        ['quenya', 'quenya-classical', 'sindarin', ...]
    """
    # Return both full names and aliases
    full_names = [
        "quenya-tengwar-classical",
        "sindarin-tengwar-general_use",
        "sindarin-tengwar-beleriand",
        "english-tengwar-espeak",
        "raw-tengwar",
    ]
    aliases = list(MODE_ALIASES.keys())
    return sorted(set(full_names + aliases))


def clear_cache():
    """Clear the mode cache.
    
    Useful if you want to reload modes or free memory.
    
    Examples:
        >>> clear_cache()  # Force reload of all modes on next use
    """
    _mode_cache.clear()


# Legacy class-based API (kept for backwards compatibility)
class Glaemscribe:
    """Class-based interface for advanced usage.
    
    Most users should use the simpler transcribe() function instead.
    This class is provided for backwards compatibility and advanced use cases.
    """
    
    def __init__(self):
        """Initialize a new Glaemscribe instance."""
        from .core.charset import Charset
        from .core.mode_enhanced import Mode
        self.modes: Dict[str, Mode] = {}
        self.charsets: Dict[str, Charset] = {}
    
    def add_charset(self, charset):
        """Add a character set."""
        self.charsets[charset.name] = charset
    
    def add_mode(self, mode):
        """Add a transcription mode."""
        self.modes[mode.name] = mode
    
    def transcribe(self, text: str, mode_name: str, charset: Optional[str] = None) -> str:
        """Transcribe text using the specified mode."""
        if mode_name not in self.modes:
            raise ValueError(f"Mode '{mode_name}' not found")
        
        mode = self.modes[mode_name]
        success, result, _ = mode.transcribe(text, charset)
        if not success:
            raise ValueError(f"Transcription failed: {result}")
        return result
    
    def list_modes(self) -> List[str]:
        """List all available modes."""
        return list(self.modes.keys())
    
    def list_charsets(self) -> List[str]:
        """List all available character sets."""
        return list(self.charsets.keys())
