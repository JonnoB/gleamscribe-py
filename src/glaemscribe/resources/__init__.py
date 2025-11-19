"""Resource management for the glaemscribe package.

This module provides helper functions to locate mode and charset files that
are bundled with the glaemscribe package. It uses importlib.resources to
ensure proper packaging support, allowing resources to be accessed whether
the package is installed normally, in editable mode, or as a wheel.

The module handles the abstraction of resource paths, so users don't need
to know where files are physically located. Resources are accessed by name
rather than file path.

Available Functions:
    get_mode_path(name): Get path to a .glaem mode file
    get_charset_path(name): Get path to a .cst charset file

Available Modes:
    - quenya-tengwar-classical: Quenya Classical Tengwar
    - sindarin-tengwar-general_use: Sindarin General Use
    - sindarin-tengwar-beleriand: Sindarin Beleriand
    - english-tengwar-espeak: English Tengwar (experimental)
    - raw-tengwar: Raw Tengwar input

Available Charsets:
    - tengwar_freemono: Unicode Tengwar (FreeMonoTengwar font)

Examples:
    >>> from glaemscribe.resources import get_mode_path, get_charset_path
    >>> from glaemscribe.parsers import ModeParser
    >>> 
    >>> # Load a mode
    >>> mode_path = get_mode_path('quenya-tengwar-classical')
    >>> parser = ModeParser()
    >>> mode = parser.parse(str(mode_path))
    >>> 
    >>> # Load a charset
    >>> charset_path = get_charset_path('tengwar_freemono')
    >>> from glaemscribe.parsers import CharsetParser
    >>> charset_parser = CharsetParser()
    >>> charset = charset_parser.parse(str(charset_path))
"""

from importlib.resources import files
from pathlib import Path


def get_mode_path(name: str) -> Path:
    """Get the path to a bundled mode file by name.
    
    Locates a .glaem mode file from the package's bundled resources using
    importlib.resources. This works regardless of how the package is installed
    (normal install, editable mode, or wheel).
    
    The mode name should not include the .glaem extension. Available modes
    include: quenya-tengwar-classical, sindarin-tengwar-general_use,
    sindarin-tengwar-beleriand, english-tengwar-espeak, and raw-tengwar.
    
    Args:
        name: Mode name without .glaem extension (e.g., "quenya-tengwar-classical")
        
    Returns:
        Path object pointing to the mode file. Convert to string with str()
        before passing to parsers.
        
    Raises:
        FileNotFoundError: If the mode file doesn't exist (implicitly when
                          the path is used)
        
    Examples:
        >>> # Get path to Quenya mode
        >>> mode_path = get_mode_path("quenya-tengwar-classical")
        >>> print(mode_path)
        PosixPath('.../glaemscribe/resources/modes/quenya-tengwar-classical.glaem')
        
        >>> # Use with ModeParser
        >>> from glaemscribe.parsers import ModeParser
        >>> parser = ModeParser()
        >>> mode = parser.parse(str(mode_path))
        
        >>> # Get Sindarin mode
        >>> mode_path = get_mode_path("sindarin-tengwar-general_use")
        >>> mode = parser.parse(str(mode_path))
    """
    resource = files("glaemscribe.resources.modes") / f"{name}.glaem"
    # For Python 3.9+, as_file() provides a context manager that returns a Path
    # For direct use, we can use the traversable directly
    return Path(str(resource))


def get_charset_path(name: str) -> Path:
    """Get the path to a bundled charset file by name.
    
    Locates a .cst charset file from the package's bundled resources using
    importlib.resources. This works regardless of how the package is installed
    (normal install, editable mode, or wheel).
    
    The charset name should not include the .cst extension. Currently, only
    tengwar_freemono (Unicode Tengwar) is bundled, as the library focuses
    on Unicode-native output.
    
    Args:
        name: Charset name without .cst extension (e.g., "tengwar_freemono")
        
    Returns:
        Path object pointing to the charset file. Convert to string with str()
        before passing to parsers.
        
    Raises:
        FileNotFoundError: If the charset file doesn't exist (implicitly when
                          the path is used)
        
    Examples:
        >>> # Get path to Unicode Tengwar charset
        >>> charset_path = get_charset_path("tengwar_freemono")
        >>> print(charset_path)
        PosixPath('.../glaemscribe/resources/charsets/tengwar_freemono.cst')
        
        >>> # Use with CharsetParser
        >>> from glaemscribe.parsers import CharsetParser
        >>> parser = CharsetParser()
        >>> charset = parser.parse(str(charset_path))
        
        >>> # Access character definitions
        >>> tinco = charset.characters.get('TINCO')
        >>> print(tinco.str_value)
        '\ue000'
    """
    resource = files("glaemscribe.resources.charsets") / f"{name}.cst"
    return Path(str(resource))


__all__ = ["get_mode_path", "get_charset_path"]
