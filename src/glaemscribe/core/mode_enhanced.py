"""Enhanced Mode definitions for Glaemscribe.

This is a port of the Ruby Mode class, supporting the full feature set
including processors, options, and complex rule management.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

from .charset import Charset


@dataclass
class Option:
    """Represents a mode option with possible values."""
    mode: 'Mode'
    name: str
    default_value: str
    values: Dict[str, int] = field(default_factory=dict)
    line: int = 0
    visibility: Optional[str] = None
    is_radio: bool = False
    
    def __post_init__(self):
        """Set up default values map."""
        if not self.values:
            self.values = {self.default_value: 1}


@dataclass
class ModeDebugContext:
    """Debug context for mode processing."""
    preprocessor_output: str = ""
    processor_pathes: List[str] = field(default_factory=list)
    processor_output: List[str] = field(default_factory=list)
    postprocessor_output: str = ""
    tts_output: str = ""


class Mode:
    """Enhanced Mode class matching the Ruby implementation.
    
    This class represents a complete transcription mode with support for:
    - Multiple character sets
    - Configurable options
    - Pre/post processors
    - Complex rule groups
    - Debug information
    """
    
    def __init__(self, name: str):
        """Initialize a new Mode."""
        self.name: str = name
        
        # Error handling
        self.errors: List = []
        self.warnings: List = []
        
        # Basic metadata
        self.language: str = ""
        self.writing: str = ""
        self.human_name: str = ""
        self.authors: str = ""
        self.version: str = ""
        
        # Character sets
        self.supported_charsets: Dict[str, Charset] = {}
        self.default_charset: Optional[Charset] = None
        
        # Options
        self.options: Dict[str, Option] = {}
        self.latest_option_values: Dict[str, str] = {}
        self._last_raw_options: Optional[Dict] = None
        
        # Processors (will be implemented later)
        self.pre_processor: Optional[Any] = None
        self.processor: Optional[Any] = None
        self.post_processor: Optional[Any] = None
        
        # Additional metadata
        self.raw_mode_name: Optional[str] = None
        self.world: str = ""
        self.invention: str = ""
        self.has_tts: bool = False
        self.current_tts_voice: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the mode."""
        return (f"<Mode {self.name}: Language '{self.language}', "
                f"Writing '{self.writing}', Human Name '{self.human_name}', "
                f"Authors '{self.authors}', Version '{self.version}'>")
    
    def __repr__(self) -> str:
        """Representation of the mode."""
        return self.__str__()
    
    def finalize(self, options: Dict[str, Any] = None):
        """Finalize the mode with given options.
        
        This sets up the processors and rule groups based on the options.
        """
        if options is None:
            options = {}
        
        # Optimization: don't refinalize if options are the same
        if options == self._last_raw_options:
            return
        
        self._last_raw_options = options.copy()
        
        # Process options into trans_options format
        trans_options = {}
        for opt_name, opt in self.options.items():
            opt_value = options.get(opt_name, opt.default_value)
            trans_options[opt_name] = opt_value
            self.latest_option_values[opt_name] = opt_value
        
        # Finalize processors (will be implemented when we create them)
        if self.pre_processor:
            self.pre_processor.finalize(trans_options)
        if self.processor:
            self.processor.finalize(trans_options)
        if self.post_processor:
            self.post_processor.finalize(trans_options)
    
    def get_charset(self, charset_name: Optional[str] = None) -> Charset:
        """Get a charset by name, returning default if not specified."""
        if charset_name:
            return self.supported_charsets.get(charset_name, self.default_charset)
        return self.default_charset
    
    def has_charset(self, charset_name: str) -> bool:
        """Check if a charset is supported."""
        return charset_name in self.supported_charsets
    
    def add_charset(self, charset: Charset, is_default: bool = False):
        """Add a supported charset."""
        self.supported_charsets[charset.name] = charset
        if is_default or self.default_charset is None:
            self.default_charset = charset
    
    def add_option(self, option: Option):
        """Add an option to the mode."""
        self.options[option.name] = option
    
    def get_option_value(self, option_name: str, default: Any = None) -> Any:
        """Get the current value of an option."""
        if option_name in self.latest_option_values:
            return self.latest_option_values[option_name]
        elif option_name in self.options:
            return self.options[option_name].default_value
        return default
