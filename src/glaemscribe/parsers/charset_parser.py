"""Charset parser for .cst character set definition files.

This module provides parsing for .cst charset files, which define character
mappings for specific fonts or encodings. Charsets map character names to
Unicode code points and define virtual characters for context-dependent
character selection.

The parser reads .cst files, builds an Abstract Syntax Tree (AST) using the
Glaeml parser, and processes it to create Charset objects containing:
- Character definitions (code points and names)
- Virtual characters (context-dependent character selection)
- Sequence characters (multi-character sequences)
- Character swaps (alternative character forms)

Charsets support both:
- Unicode-native fonts (FreeMonoTengwar) using PUA (U+E000+)
- Legacy font-specific encodings (DS fonts) with automatic Unicode mapping

Example:
    >>> from glaemscribe.parsers import CharsetParser
    >>> from glaemscribe.resources import get_charset_path
    >>> 
    >>> parser = CharsetParser()
    >>> charset = parser.parse(str(get_charset_path('tengwar_freemono')))
    >>> print(charset.name)
    'tengwar_freemono'
    >>> print(len(charset.characters))
    100+
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import os

from .glaeml import Parser, Document, Node, Error
from ..core.charset import Charset as CoreCharset
from .tengwar_font_mapping import map_font_code_to_unicode


@dataclass
class Char:
    """Represents a single character in a charset.
    
    A Char maps character names to Unicode code points. It handles both
    Unicode-native charsets (using PUA directly) and legacy font-specific
    encodings (automatically mapped to Unicode).
    
    Attributes:
        line: Line number in the .cst file where this character is defined
        code: Character code point (hex value)
        names: List of names for this character (e.g., ['TINCO', 'T'])
        str_value: Unicode string representation (set in __post_init__)
        charset: Reference to parent CharsetParser
        
    Examples:
        >>> char = Char(line=10, code=0xE000, names=['TINCO'], 
        ...             str_value='', charset=parser)
        >>> print(char.str_value)  # After __post_init__
        '\ue000'
    """
    line: int
    code: int
    names: List[str]
    str_value: str
    charset: 'CharsetParser' = field(repr=False)
    
    def __post_init__(self):
        """Convert code point to Unicode character using font mapping.
        
        Automatically determines whether to use direct Unicode mapping
        (for Unicode-native charsets like FreeMonoTengwar) or legacy
        font mapping (for DS fonts). Sets the str_value attribute.
        """
        # Check if this is a Unicode-native charset (like FreeMonoTengwar)
        # by checking the charset name if available
        is_unicode_charset = False
        if hasattr(self.charset, 'charset') and self.charset.charset:
            is_unicode_charset = 'freemono' in self.charset.charset.name.lower()
        
        if self.code >= 0xE000 or is_unicode_charset:
            # Direct Unicode mapping for Unicode-native charsets
            # or for codes in the Private Use Area
            self.str_value = chr(self.code)
        else:
            # Use font mapping for legacy font-specific character codes (DS fonts)
            self.str_value = map_font_code_to_unicode(self.code)


@dataclass
class VirtualClass:
    """A class within a virtual character definition.
    
    Defines a mapping from trigger characters to a target character.
    Used within VirtualChar to implement context-dependent character selection.
    
    Attributes:
        target: Name of the result character to use
        triggers: List of trigger character names that activate this mapping
        
    Examples:
        >>> vc = VirtualClass(target='TINCO_EXTENDED', triggers=['TINCO', 'T'])
    """
    target: str
    triggers: List[str]


@dataclass(unsafe_hash=True)
class VirtualChar:
    """Represents a virtual character for context-dependent character selection.
    
    Virtual characters are placeholders that resolve to different actual characters
    based on context (e.g., preceding or following characters). They enable
    sophisticated transcription rules where the same input produces different
    outputs depending on surrounding characters.
    
    For example, a vowel tehta might use different forms when placed above
    different consonants.
    
    Attributes:
        line: Line number in the .cst file
        names: List of names for this virtual character
        classes: List of VirtualClass mappings (trigger → target)
        charset: Reference to parent CharsetParser
        reversed: Whether to check following context instead of preceding
        default: Default character name if no trigger matches
        lookup_table: Built during finalize() - maps trigger names to result chars
        
    Examples:
        >>> # Virtual character that selects different forms based on context
        >>> vc = VirtualChar(line=50, names=['A_TEHTA'], 
        ...                  classes=[...], charset=parser)
        >>> vc.finalize()  # Build lookup table
        >>> result = vc['TINCO']  # Get result for TINCO context
    """
    line: int
    names: List[str] = field(hash=False)
    classes: List[VirtualClass] = field(hash=False)
    charset: 'CharsetParser' = field(repr=False, hash=False, compare=False)
    reversed: bool = False
    default: Optional[str] = None
    lookup_table: Dict[str, Char] = field(default_factory=dict, init=False, hash=False, compare=False)
    
    def finalize(self):
        """Build lookup table for virtual character resolution.
        
        Maps trigger character names to result character objects.
        """
        self.lookup_table = {}
        
        for vc_class in self.classes:
            result_char_name = vc_class.target
            trigger_char_names = vc_class.triggers
            
            for trigger_char_name in trigger_char_names:
                if trigger_char_name in self.lookup_table:
                    # Ruby version would add an error here
                    continue
                
                # Find the result character in the charset
                result_char = self.charset._get_character_by_name(result_char_name)
                trigger_char = self.charset._get_character_by_name(trigger_char_name)
                
                if result_char is None:
                    # Ruby version would add an error here
                    continue
                elif trigger_char is None:
                    # Ruby version would add an error here
                    continue
                elif isinstance(trigger_char, VirtualChar):
                    # Ruby version would add an error here - virtual chars can't trigger other virtual chars
                    continue
                else:
                    # Map all names of the trigger character to the result character
                    for trigger_name in trigger_char.names:
                        self.lookup_table[trigger_name] = result_char
    
    def __getitem__(self, trigger_char_name: str) -> Optional[Char]:
        """Get the result character for a trigger character name.
        
        Args:
            trigger_char_name: Name of the triggering character
            
        Returns:
            Char object to use, or None if no mapping exists
            
        Examples:
            >>> result_char = virtual_char['TINCO']
            >>> if result_char:
            ...     print(result_char.str_value)
        """
        return self.lookup_table.get(trigger_char_name)
    
    def is_virtual(self) -> bool:
        """Check if this is a virtual character.
        
        Returns:
            Always True for VirtualChar objects
        """
        return True
    
    def is_sequence(self) -> bool:
        """Check if this is a sequence character.
        
        Returns:
            Always False for VirtualChar objects (True for SequenceChar)
        """
        return False
    
    def get_str(self) -> str:
        """Get the string representation if virtual char cannot be resolved.
        
        Returns the default character's string value if defined, otherwise
        returns '?' as a fallback placeholder.
        
        Returns:
            String representation (default char or '?')
        """
        if self.default:
            default_char = self.charset._get_character_by_name(self.default)
            if default_char:
                return default_char.str_value
        return "?"  # VIRTUAL_CHAR_OUTPUT in Ruby


@dataclass
class Swap:
    """Represents a character swap operation for alternative character forms.
    
    Swaps allow defining alternative forms of characters that can be
    selected based on context or user preferences.
    
    Attributes:
        line: Line number in the .cst file
        trigger: Trigger character name
        target_list: List of alternative character names
        targets: Dict mapping names to Char objects (built during finalize)
        lookup_table: Lookup table for swap resolution
    """
    line: int
    trigger: str
    target_list: List[str]
    targets: Dict[str, Char] = field(default_factory=dict, init=False)
    lookup_table: Dict[str, Char] = field(default_factory=dict, init=False)


class CharsetParser:
    """Parses .cst charset files into Charset objects.
    
    The CharsetParser reads .cst files (Glaemscribe charset definition files)
    and converts them into Charset objects that map character names to Unicode
    code points. It handles:
    
    - File reading and parsing
    - Character definitions (code points and names)
    - Virtual characters (context-dependent selection)
    - Sequence characters (multi-character sequences)
    - Character swaps (alternative forms)
    - Unicode mapping (both native and legacy font encodings)
    
    The parser automatically detects whether a charset uses Unicode-native
    encoding (FreeMonoTengwar) or legacy font-specific encoding (DS fonts)
    and applies appropriate Unicode mapping.
    
    Attributes:
        charset: The Charset object being constructed (None until parse() is called)
        chars: List of character objects (Char and VirtualChar)
        errors: List of parsing errors encountered
    
    Examples:
        >>> # Parse a charset file
        >>> parser = CharsetParser()
        >>> charset = parser.parse('charsets/tengwar_freemono.cst')
        >>> 
        >>> # Access characters by name
        >>> tinco = charset.characters.get('TINCO')
        >>> print(tinco.str_value)
        '\ue000'
        
        >>> # Parse using package resources
        >>> from glaemscribe.resources import get_charset_path
        >>> charset_path = get_charset_path('tengwar_freemono')
        >>> charset = parser.parse(str(charset_path))
    """
    
    def __init__(self):
        """Initialize the charset parser.
        
        Creates a new parser instance with empty charset, character list,
        and error list. The charset will be populated when parse() is called.
        """
        self.charset: Optional[CoreCharset] = None
        self.chars: List[Union[Char, VirtualChar]] = []
        self.errors: List[Error] = []
    
    def parse(self, file_path: str) -> CoreCharset:
        """Parse a .cst charset file and return a Charset object.
        
        Reads the specified .cst file, parses its contents, and constructs
        a Charset object with all character definitions, virtual characters,
        and other features. The charset name is derived from the filename.
        
        The parsing process:
        1. Reads the file content
        2. Parses with Glaeml parser to build AST
        3. Extracts character definitions
        4. Extracts virtual character definitions
        5. Extracts sequence and swap definitions
        6. Finalizes virtual characters (builds lookup tables)
        7. Applies Unicode mapping (native or legacy)
        
        Args:
            file_path: Path to the .cst charset file to parse
            
        Returns:
            Charset object containing all parsed character definitions.
            Access characters via charset.characters dict.
            
        Raises:
            FileNotFoundError: If the file cannot be read
            
        Examples:
            >>> parser = CharsetParser()
            >>> charset = parser.parse('charsets/tengwar_freemono.cst')
            >>> print(charset.name)
            'tengwar_freemono'
            >>> print(len(charset.characters))
            150
            
            >>> # Access a character
            >>> tinco = charset.characters['TINCO']
            >>> print(tinco.str_value)
            '\ue000'
            
            >>> # Use with package resources
            >>> from glaemscribe.resources import get_charset_path
            >>> charset = parser.parse(str(get_charset_path('tengwar_freemono')))
        """
        self.errors = []
        self.chars = []
        
        # Extract charset name from filename
        charset_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Create the core charset object
        self.charset = CoreCharset(name=charset_name, version="1.0.0")
        
        # Read and parse the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            raise FileNotFoundError(f"Could not read file {file_path}: {e}") from e
        
        # Parse with Glaeml parser
        glaeml_parser = Parser()
        doc = glaeml_parser.parse(content)
        
        if doc.has_errors():
            self.errors.extend(doc.errors)
        
        # Process the AST
        self._process_ast(doc)
        
        # Finalize the charset
        self._finalize()
        
        return self.charset
    
    def _process_ast(self, doc: Document):
        """Process the parsed AST to extract character definitions."""
        if not doc.root_node:
            return
        
        # Process character definitions
        for char_element in doc.root_node.gpath("char"):
            self._process_char(char_element)
        
        # Process sequence characters (if any)
        for seq_element in doc.root_node.gpath("sequence"):
            self._process_sequence(seq_element)
        
        # Process virtual characters
        for virtual_element in doc.root_node.gpath("virtual"):
            self._process_virtual(virtual_element)
        
        # Process swaps (if any)
        for swap_element in doc.root_node.gpath("swap"):
            self._process_swap(swap_element)
    
    def _process_char(self, char_element: Node):
        """Process a single character definition.
        
        Parses a character definition from the AST and creates a Char object.
        Character definitions specify:
        - Code point (hex value)
        - One or more character names
        
        The code point is always parsed as hexadecimal (matching Ruby and JS
        implementations). Unicode mapping is applied automatically based on
        whether this is a Unicode-native or legacy font charset.
        
        Args:
            char_element: AST node containing character definition
        """
        if not char_element.args:
            self.errors.append(Error(char_element.line, "Character definition missing code point"))
            return
        
        try:
            # Parse code point - ALWAYS treat as hexadecimal (like Ruby .hex and JS parseInt(...,16))
            code_str = char_element.args[0]
            code = int(code_str, 16)  # Always base 16, matching Ruby and JS behavior
            
            # Get character names (everything after the code point)
            names = [name.strip() for name in char_element.args[1:] if name.strip() and name.strip() != '?']
            
            if not names:
                return  # Skip characters without valid names
            
            # Create character object
            char = Char(
                line=char_element.line,
                code=code,
                names=names,
                str_value="",  # Will be set in __post_init__
                charset=self
            )
            
            self.chars.append(char)
            
            # Add to core charset's character dictionary
            for name in names:
                self.charset.characters[name] = char
                
        except ValueError as e:
            self.errors.append(Error(char_element.line, f"Invalid code point '{char_element.args[0]}': {e}"))
    
    def _process_virtual(self, virtual_element: Node):
        """Process a virtual character definition.
        
        Parses a virtual character definition from the AST and creates a
        VirtualChar object. Virtual characters define context-dependent
        character selection with:
        - Names for the virtual character
        - Classes mapping trigger characters to target characters
        - Optional reversed flag (check following instead of preceding context)
        - Optional default character if no trigger matches
        
        Args:
            virtual_element: AST node containing virtual character definition
        """
        names = [name.strip() for name in virtual_element.args if name.strip() and name.strip() != '?']
        
        if not names:
            return  # Skip virtual chars without valid names
        
        classes = []
        reversed = False
        default = None
        
        # Process classes
        for class_element in virtual_element.gpath("class"):
            if not class_element.args:
                continue
            
            target = class_element.args[0]
            triggers = [t.strip() for t in class_element.args[1:] if t.strip() and t.strip() != '?']
            
            # Also check for triggers in the body text
            for child in class_element.children:
                if child.is_text():
                    text_triggers = [t.strip() for t in child.args[0].split() if t.strip() and t.strip() != '?']
                    triggers.extend(text_triggers)
            
            if triggers:
                classes.append(VirtualClass(target=target, triggers=triggers))
        
        # Check for reversed flag
        if virtual_element.gpath("reversed"):
            reversed = True
        
        # Check for default value
        default_elements = virtual_element.gpath("default")
        if default_elements:
            default = default_elements[0].args[0] if default_elements[0].args else None
        
        # Create virtual character
        virtual_char = VirtualChar(
            line=virtual_element.line,
            names=names,
            classes=classes,
            charset=self,
            reversed=reversed,
            default=default
        )
        
        self.chars.append(virtual_char)
        
        # Add to core charset's virtual characters
        for name in names:
            # Store the actual VirtualChar object for proper resolution
            self.charset.virtual_chars[name] = virtual_char
    
    def _process_swap(self, swap_element: Node):
        """Process a swap definition."""
        # Ruby format: \swap TRIGGER TARGET1 TARGET2 ...
        # We'll also accept targets coming from text children if args are sparse
        if not swap_element.args:
            return
        trigger = swap_element.args[0]
        targets: List[str] = []
        # Collect from inline args
        if len(swap_element.args) > 1:
            targets.extend([t for t in swap_element.args[1:] if t and t != '?'])
        # Collect from text children
        for child in swap_element.children:
            if child.is_text() and child.args and child.args[0]:
                parts = [p for p in child.args[0].split() if p and p != '?']
                targets.extend(parts)
        if not targets:
            return
        # Register into core charset
        self.charset.add_swap(trigger, targets)

    def _process_sequence(self, seq_element: Node):
        """Process a sequence character definition.
        Expected patterns (tolerant):
          \sequence NAME TOKEN TOKEN ...
          or tokens listed in text children.
        Stores in charset.sequences[NAME] = [TOKENS ...]
        """
        if not seq_element.args:
            return
        name = seq_element.args[0]
        tokens: List[str] = []
        # From inline args
        if len(seq_element.args) > 1:
            tokens.extend([t for t in seq_element.args[1:] if t and t != '?'])
        # From text children
        for child in seq_element.children:
            if child.is_text() and child.args and child.args[0]:
                parts = [p for p in child.args[0].split() if p and p != '?']
                tokens.extend(parts)
        if not tokens:
            return
        self.charset.sequences[name] = tokens
    
    def _get_character_by_name(self, name: str) -> Optional[Char]:
        """Get a character object by name."""
        for char in self.chars:
            if name in char.names:
                return char
        return None
    
    def _finalize(self):
        """Finalize the charset by building lookup tables."""
        # Finalize all virtual characters to build their lookup tables
        for char in self.chars:
            if isinstance(char, VirtualChar):
                char.finalize()
