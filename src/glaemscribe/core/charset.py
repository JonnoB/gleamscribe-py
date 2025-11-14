"""Character set definitions for Glaemscribe."""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set


@dataclass
class Charset:
    """Represents a character set for a writing system."""
    name: str
    version: str
    characters: Dict[str, str] = field(default_factory=dict)
    virtual_chars: Dict[str, str] = field(default_factory=dict)
    sequences: Dict[str, List[str]] = field(default_factory=dict)
    swaps: Dict[str, Set[str]] = field(default_factory=dict)
    
    def get_character(self, char_name: str) -> str:
        """Get the Unicode character for a given character name."""
        char = self.characters.get(char_name, char_name)
        # Handle Char objects from charset parser
        if hasattr(char, 'str_value'):
            return char.str_value
        return char
    
    def has_character(self, char_name: str) -> bool:
        """Check if a character name exists in this charset."""
        return char_name in self.characters
    
    def __getitem__(self, char_name: str) -> Optional[str]:
        """Allow dictionary-style access to characters."""
        char = self.characters.get(char_name)
        if hasattr(char, 'str_value'):
            return char.str_value
        return char
    
    def get(self, char_name: str, default: Optional[str] = None) -> Optional[str]:
        """Get character with default value."""
        char = self.characters.get(char_name, default)
        if hasattr(char, 'str_value'):
            return char.str_value
        return char
    
    def resolve_virtual(self, virtual_name: str) -> Optional[str]:
        """Resolve a virtual character to its definition."""
        return self.virtual_chars.get(virtual_name)

    def has_swap_target(self, trigger: str, target: str) -> bool:
        """Check if there is a swap rule for trigger that targets the given next token."""
        tgts = self.swaps.get(trigger)
        return target in tgts if tgts else False

    def add_swap(self, trigger: str, targets: List[str]) -> None:
        """Add swap targets for a trigger."""
        if trigger not in self.swaps:
            self.swaps[trigger] = set()
        self.swaps[trigger].update(targets)
