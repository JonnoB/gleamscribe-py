"""Transcription tree node for pattern matching.

This is a port of the Ruby TranscriptionTreeNode class, which implements
a tree-based pattern matching algorithm for efficient rule application.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple


class TranscriptionTreeNode:
    """A node in the transcription tree for pattern matching.
    
    The tree structure allows efficient matching of input patterns to
    their replacements. Each node represents a character in a pattern,
    and paths through the tree represent complete patterns.
    """
    
    def __init__(self, character: Optional[str] = None, replacement: Optional[List[str]] = None):
        """Initialize a tree node.
        
        Args:
            character: The character this node represents
            replacement: The replacement tokens if this is a terminal node
        """
        self.character: Optional[str] = character
        self.replacement: Optional[List[str]] = replacement
        self.siblings: Dict[str, TranscriptionTreeNode] = {}
    
    def is_effective(self) -> bool:
        """Check if this node has a replacement (is a terminal node)."""
        return self.replacement is not None
    
    def add_subpath(self, source: str, replacement: List[str]):
        """Add a pattern and its replacement to the tree.
        
        Args:
            source: The source pattern to match
            replacement: The replacement tokens
        """
        if not source:
            return
        
        # Get first character
        first_char = source[0]
        
        # Get or create sibling for this character
        if first_char not in self.siblings:
            self.siblings[first_char] = TranscriptionTreeNode(first_char, None)
        
        sibling = self.siblings[first_char]
        
        if len(source) == 1:
            # This is the end of the pattern - mark as effective
            sibling.replacement = replacement
        else:
            # Continue building the path
            sibling.add_subpath(source[1:], replacement)
    
    def transcribe(self, string: str, chain: Optional[List[TranscriptionTreeNode]] = None) -> Tuple[List[str], int]:
        """Transcribe a string using the tree.
        
        This method walks the tree trying to match the longest possible
        pattern from the input string.
        
        Args:
            string: The input string to transcribe
            chain: The chain of nodes visited (for backtracking)
        
        Returns:
            A tuple of (replacement_tokens, characters_consumed)
        """
        if chain is None:
            chain = []
        
        chain.append(self)
        
        # Try to continue matching
        if string:
            first_char = string[0]
            sibling = self.siblings.get(first_char)
            
            if sibling:
                # Continue down the tree
                return sibling.transcribe(string[1:], chain)
        
        # We've reached the end of matching - backtrack to find effective node
        while len(chain) > 1:
            last_node = chain.pop()
            if last_node.is_effective():
                # Found a match! Return the replacement and how many chars we consumed
                return last_node.replacement, len(chain)
        
        # No match found - return unknown character marker
        return ["*UNKNOWN"], 1
    
    def __str__(self) -> str:
        """String representation of the node."""
        return f"<TreeNode '{self.character}': {len(self.siblings)} siblings, effective={self.is_effective()}>"
