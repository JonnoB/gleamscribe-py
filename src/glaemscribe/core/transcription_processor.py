"""Transcription processor for applying rules to text.

This is a port of the Ruby TranscriptionProcessor class, which manages
rule groups and applies transcription rules using a tree-based algorithm.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any

from .transcription_tree_node import TranscriptionTreeNode
from .rule_group import RuleGroup
from .mode_enhanced import Mode


class TranscriptionProcessor:
    """Processes text using transcription rules.
    
    This class manages rule groups and applies them to input text
    using a tree-based pattern matching algorithm.
    """
    
    # Constants for word boundaries
    WORD_BOUNDARY_TREE = "^"  # Start of word marker
    WORD_BREAKER = "$"         # End of word marker
    
    def __init__(self, mode: Mode):
        """Initialize the processor for a specific mode.
        
        Args:
            mode: The mode containing the transcription rules
        """
        self.mode: Mode = mode
        self.rule_groups: Dict[str, RuleGroup] = {}
        self.in_charset: Dict[str, RuleGroup] = {}  # Maps characters to rule groups
        self.transcription_tree: Optional[TranscriptionTreeNode] = None
    
    def add_rule_group(self, name: str, rule_group: RuleGroup):
        """Add a rule group to the processor.
        
        Args:
            name: Name of the rule group
            rule_group: The rule group to add
        """
        self.rule_groups[name] = rule_group
    
    def finalize(self, trans_options: Dict[str, Any]):
        """Finalize the processor with given transcription options.
        
        This builds the transcription tree from all the rule groups
        after applying conditional logic based on options.
        
        Args:
            trans_options: Dictionary of option values
        """
        # Finalize each rule group with the options
        for rule_group in self.rule_groups.values():
            rule_group.finalize(trans_options)
        
        # Build the input charset mapping
        self._build_input_charset()
        
        # Build the transcription tree
        self._build_transcription_tree()
    
    def _build_input_charset(self):
        """Build mapping of input characters to rule groups."""
        self.in_charset = {}
        
        for rule_group in self.rule_groups.values():
            # TODO: Get the input charset from the rule group
            # For now, we'll skip this as it requires rule implementation
            pass
    
    def _build_transcription_tree(self):
        """Build the transcription tree from all rules."""
        self.transcription_tree = TranscriptionTreeNode()
        
        # Add word boundaries
        self.transcription_tree.add_subpath(self.WORD_BOUNDARY_TREE, [""])
        self.transcription_tree.add_subpath(self.WORD_BREAKER, [""])
        
        # Add all rules from all rule groups
        for rule_group in self.rule_groups.values():
            for rule in rule_group.rules:
                # Parse target into tokens (split by spaces for now)
                target_tokens = rule['target'].split()
                self.transcription_tree.add_subpath(rule['source'], target_tokens)
    
    def transcribe(self, text: str, debug_context: Optional[Any] = None) -> List[str]:
        """Transcribe text using the rule tree.
        
        Args:
            text: The input text to transcribe
            debug_context: Optional debug context for tracing
        
        Returns:
            List of transcription tokens
        """
        if not self.transcription_tree:
            # Tree not built yet - return unknown for everything
            return ["*UNKNOWN"] * len(text)
        
        result = []
        current_group = None
        accumulated_word = ""
        
        for char in text:
            if char in (" ", "\t"):
                # Word boundary - transcribe accumulated word
                result.extend(self._transcribe_word(accumulated_word, debug_context))
                result.append("*SPACE")
                accumulated_word = ""
            elif char == "\r":
                # Ignore carriage return
                continue
            elif char == "\n":
                # Line feed boundary
                result.extend(self._transcribe_word(accumulated_word, debug_context))
                result.append("*LF")
                accumulated_word = ""
            else:
                # Regular character
                char_group = self.in_charset.get(char)
                if char_group == current_group:
                    accumulated_word += char
                else:
                    # Group changed - transcribe previous word
                    result.extend(self._transcribe_word(accumulated_word, debug_context))
                    current_group = char_group
                    accumulated_word = char
        
        # Transcribe any remaining word
        result.extend(self._transcribe_word(accumulated_word, debug_context))
        
        return result
    
    def _transcribe_word(self, word: str, debug_context: Optional[Any] = None) -> List[str]:
        """Transcribe a single word.
        
        Args:
            word: The word to transcribe
            debug_context: Optional debug context
        
        Returns:
            List of transcription tokens
        """
        if not word:
            return []
        
        # Add word boundaries for matching
        word_with_boundaries = self.WORD_BOUNDARY_TREE + word + self.WORD_BREAKER
        
        result = []
        remaining = word_with_boundaries
        
        while remaining:
            # Find longest match
            tokens, consumed = self.transcription_tree.transcribe(remaining)
            
            # Remove matched characters
            remaining = remaining[consumed:]
            
            # Get the actual characters that were matched
            eaten = word_with_boundaries[:consumed]
            word_with_boundaries = word_with_boundaries[consumed:]
            
            # Add tokens to result (skip boundary markers)
            if tokens != [""]:  # Skip empty boundary matches
                result.extend(tokens)
            
            # Debug tracing
            if debug_context:
                debug_context.processor_pathes.append([eaten, tokens, tokens])
        
        return result
    
    def __str__(self) -> str:
        """String representation of the processor."""
        return f"<TranscriptionProcessor: {len(self.rule_groups)} rule groups>"
