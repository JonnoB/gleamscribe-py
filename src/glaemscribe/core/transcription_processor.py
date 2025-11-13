"""Transcription processor for applying rules to text.

This is a port of the Ruby TranscriptionProcessor class, which manages
rule groups and applies transcription rules using a tree-based algorithm.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any

from .transcription_tree_node import TranscriptionTreeNode
from .rule_group import RuleGroup
from .mode_enhanced import Mode
from .mode_debug_context import ModeDebugContext


class TranscriptionProcessor:
    """Processes text using transcription rules.
    
    This class manages rule groups and applies them to input text
    using a tree-based pattern matching algorithm.
    """
    
    # Constants for word boundaries (match Ruby exactly)
    WORD_BREAKER = "|"            # Word separator
    WORD_BOUNDARY_LANG = "_"      # Language boundary  
    WORD_BOUNDARY_TREE = "\u0000" # Tree boundary (null character)
    
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
        """Build mapping of input characters to rule groups.
        
        This matches the Ruby implementation exactly:
        @in_charset = {}
        rule_groups.each{ |rgname, rg| 
          rg.in_charset.each{ |char, group|
            group_for_char = @in_charset[char]
            if group_for_char
              mode.errors << Glaeml::Error.new(-1,"Group #{rgname} uses input character #{char} which is also used by group #{group_for_char.name}. Input charsets should not intersect between groups.") 
            else
              @in_charset[char] = group
            end
          }
        }
        """
        self.in_charset = {}
        
        for rg_name, rule_group in self.rule_groups.items():
            for char, group in rule_group.in_charset.items():
                group_for_char = self.in_charset.get(char)
                if group_for_char:
                    # Character conflict - add error to mode
                    from ..parsers.glaeml import Error
                    self.mode.errors.append(Error(-1, f"Group {rg_name} uses input character '{char}' which is also used by group {group_for_char.name}. Input charsets should not intersect between groups."))
                else:
                    self.in_charset[char] = group
    
    def _build_transcription_tree(self):
        """Build the transcription tree from all rules."""
        self.transcription_tree = TranscriptionTreeNode()
        
        # Add word boundaries (match Ruby exactly)
        self.transcription_tree.add_subpath(self.WORD_BOUNDARY_TREE, [""])
        self.transcription_tree.add_subpath(self.WORD_BREAKER, [""])
        
        # Add all rules from all rule groups
        for rule_group in self.rule_groups.values():
            # Temporary gating: skip 'numbers' group in normal prose
            if getattr(rule_group, 'name', '') == 'numbers':
                continue
            for rule in rule_group.rules:
                # Add all sub-rules from this rule
                for sub_rule in rule.sub_rules:
                    # Create path from source combination
                    path = "".join(sub_rule.src_combination)
                    self.transcription_tree.add_subpath(path, sub_rule.dst_combination)
    
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
    
    def _transcribe_word(self, word: str, debug_context: Optional[ModeDebugContext] = None) -> List[str]:
        """Transcribe a single word.
        
        Args:
            word: The word to transcribe
            debug_context: Optional debug context for tracing
        
        Returns:
            List of transcription tokens
        """
        if not word:
            return []
        
        # Add word boundaries for matching (match Ruby exactly)
        word_with_boundaries = self.WORD_BOUNDARY_TREE + word + self.WORD_BOUNDARY_TREE
        
        result = []
        remaining = word_with_boundaries
        original_word = word_with_boundaries
        
        while remaining:
            # Find longest match
            tokens, consumed = self.transcription_tree.transcribe(remaining)
            
            # Get the actual characters that were matched
            eaten = original_word[:consumed]
            original_word = original_word[consumed:]
            
            # Remove matched characters from remaining
            remaining = remaining[consumed:]
            
            # Add to result
            result.extend(tokens)
            
            # Add debug trace if context provided
            if debug_context is not None:
                # TODO: Fix debug context method call
                # debug_context.add_processor_path(eaten, tokens, tokens)
                pass
        
        return result
    
    def __str__(self) -> str:
        """String representation of the processor."""
        return f"<TranscriptionProcessor: {len(self.rule_groups)} rule groups>"
