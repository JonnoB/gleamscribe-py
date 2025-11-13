"""Resolve virtual characters post-processor operator.

This is a port of the Ruby ResolveVirtualsPostProcessorOperator which handles
context-dependent character substitutions in Tengwar transcription.

Virtual characters are placeholder tokens that get replaced by actual characters
based on the surrounding context (what comes before/after them).
"""

from __future__ import annotations
from typing import List, Dict, Optional, Any
from .base import PostProcessorOperator
from ..charset import Charset


class ResolveVirtualsPostProcessorOperator(PostProcessorOperator):
    """Post-processor operator that resolves virtual characters.
    
    Virtual characters are context-dependent substitutions. For example,
    a vowel character might have different forms depending on which
    consonant it appears above.
    """
    
    def __init__(self, mode, glaeml_element=None):
        """Initialize the virtual character resolver.
        
        Args:
            mode: The mode instance
            glaeml_element: Optional GLAEML element for this operator
        """
        super().__init__(mode, glaeml_element)
        self.last_triggers: Dict[Any, Any] = {}
    
    def finalize(self, trans_options: Dict[str, Any]):
        """Finalize the operator.
        
        Args:
            trans_options: Transcription options
        """
        super().finalize(trans_options)
        # Initialize trigger states for each virtual character class
        self.last_triggers = {}
    
    def reset_trigger_states(self, charset: Charset):
        """Reset trigger states for all virtual character classes.
        
        Args:
            charset: The charset containing virtual character definitions
        """
        if hasattr(charset, 'virtual_chars'):
            # charset.virtual_chars is a dict: name -> VirtualChar
            for vc in getattr(charset, 'virtual_chars', {}).values():
                self.last_triggers[vc] = None
    
    def apply_loop(self, charset: Charset, tokens: List[str], new_tokens: List[str], 
                   reversed: bool, token: str, idx: int) -> str:
        """Apply virtual character resolution for a single token.
        
        Matches Ruby's apply_loop method exactly.
        """
        if token in ['*SPACE', '*LF']:
            self.reset_trigger_states(charset)
            return token
        
        # Check if token is a virtual character
        if hasattr(charset, 'virtual_chars') and token in getattr(charset, 'virtual_chars', {}):
            virtual_char = charset.virtual_chars[token]
            if virtual_char.is_virtual() and reversed == virtual_char.reversed:
                # Try to replace with last triggered character
                last_trigger = self.last_triggers.get(virtual_char)
                if last_trigger is not None and hasattr(last_trigger, 'names') and last_trigger.names:
                    new_tokens[idx] = last_trigger.names[0]  # Take the first name of the non-virtual replacement
                    token = new_tokens[idx]  # Consider the token replaced, being itself a potential trigger for further virtuals (cascading virtuals)
        
        # Update states of virtual classes
        if hasattr(charset, 'virtual_chars'):
            for vc in getattr(charset, 'virtual_chars', {}).values():
                result_char = vc[token]  # Use the __getitem__ method
                if result_char is not None:
                    self.last_triggers[vc] = result_char
        
        return token
    
    def apply(self, tokens: List[str], out_charset) -> List[str]:
        """Apply virtual character resolution to token list.
        
        Args:
            tokens: List of transcription tokens
            out_charset: Charset for character resolution
            
        Returns:
            Modified token list with virtual characters resolved
        """
        if not out_charset:
            return tokens
        
        # 1) Expand sequence characters first (no-op if none defined)
        tokens = self.apply_sequences(out_charset, tokens)
        
        # 2) Apply swaps (no-op if none defined)
        tokens = self.apply_swaps(out_charset, tokens)
        
        # If no virtuals, return
        if not hasattr(out_charset, 'virtual_chars'):
            return tokens
        
        # Clone the tokens so that we can perform ligatures AND diacritics without interferences
        new_tokens = tokens.copy()
        
        # 3) Handle left-to-right virtuals
        self.reset_trigger_states(out_charset)
        for idx, token in enumerate(tokens):
            self.apply_loop(out_charset, tokens, new_tokens, False, token, idx)
        
        # 4) Handle right-to-left virtuals
        self.reset_trigger_states(out_charset)
        for r_idx, token in enumerate(reversed(tokens)):
            idx = len(tokens) - 1 - r_idx
            self.apply_loop(out_charset, tokens, new_tokens, True, token, idx)
        
        return new_tokens

    def apply_sequences(self, charset: Charset, tokens: List[str]) -> List[str]:
        """Expand sequence tokens into their component tokens.
        Matches Ruby's apply_sequences behavior.
        """
        ret: List[str] = []
        seqs = getattr(charset, 'sequences', {})
        for token in tokens:
            # If parser has populated sequences dict with lists
            if token in seqs:
                ret.extend(seqs[token])
            else:
                ret.append(token)
        return ret

    def apply_swaps(self, charset: Charset, tokens: List[str]) -> List[str]:
        """Apply swap rules in a single left-to-right pass."""
        # Expect charset to expose has_swap_target(trigger, target)
        if not hasattr(charset, 'has_swap_target'):
            return tokens
        if len(tokens) < 2:
            return tokens
        i = 0
        while i < len(tokens) - 1:
            tok = tokens[i]
            tgt = tokens[i + 1]
            if charset.has_swap_target(tok, tgt):
                tokens[i], tokens[i + 1] = tgt, tok
            i += 1
        return tokens
