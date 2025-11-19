"""Resource management for glaemscribe package.

Provides helpers to load modes and charsets from the installed package,
using importlib.resources for proper packaging support.
"""

from importlib.resources import files
from pathlib import Path


def get_mode_path(name: str) -> Path:
    """Get the path to a mode file by name.
    
    Args:
        name: Mode name (without .glaem extension)
        
    Returns:
        Path object pointing to the mode file
        
    Example:
        >>> mode_path = get_mode_path("quenya-tengwar-classical")
        >>> parser.parse(str(mode_path))
    """
    resource = files("glaemscribe.resources.modes") / f"{name}.glaem"
    # For Python 3.9+, as_file() provides a context manager that returns a Path
    # For direct use, we can use the traversable directly
    return Path(str(resource))


def get_charset_path(name: str) -> Path:
    """Get the path to a charset file by name.
    
    Args:
        name: Charset name (without .cst extension)
        
    Returns:
        Path object pointing to the charset file
        
    Example:
        >>> charset_path = get_charset_path("tengwar_freemono")
        >>> parser.parse(str(charset_path))
    """
    resource = files("glaemscribe.resources.charsets") / f"{name}.cst"
    return Path(str(resource))


__all__ = ["get_mode_path", "get_charset_path"]
