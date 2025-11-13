"""Sheaf implementation for Glaemscribe.

This is a port of the Ruby Sheaf class, which handles parsing
sheaf expressions like [a*b*c] into fragments.
"""

from __future__ import annotations
from typing import List
from .fragment import Fragment


class Sheaf:
    """A sheaf is a bundle of fragments.
    
    They are used to factorize the writing process of rules, and thus 
    represent parallel rules. For example [(a|ä),b,c] => [1,2,3] means 
    that we send one sheaf to another, defining 4 rules:
    a => 1
    ä => 1
    b => 2
    c => 3
    """
    
    SHEAF_SEPARATOR = "*"
    
    def __init__(self, sheaf_chain, expression: str, linkable: bool):
        """Initialize a sheaf.
        
        Args:
            sheaf_chain: The parent sheaf chain
            expression: Sheaf expression like "a*b*c" or "h,s,t"
            linkable: Whether this sheaf is linkable (from brackets)
        """
        self.linkable = linkable
        self.sheaf_chain = sheaf_chain
        self.mode = sheaf_chain.mode
        self.rule = sheaf_chain.rule
        self.expression = expression
        
        # Split members using "*" separator, KEEP NULL MEMBERS (this is legal)
        fragment_exps = expression.split(self.SHEAF_SEPARATOR, -1)
        fragment_exps = [exp.strip() for exp in fragment_exps]
        if not fragment_exps:
            fragment_exps = [""]  # For NULL case
        
        # Build the fragments inside
        self.fragments = [Fragment(self, fragment_exp) for fragment_exp in fragment_exps]
    
    def is_src(self) -> bool:
        """Check if this is a source sheaf."""
        return self.sheaf_chain.is_src
    
    def is_dst(self) -> bool:
        """Check if this is a destination sheaf."""
        return self.sheaf_chain.is_dst
    
    def __str__(self) -> str:
        """String representation of the sheaf."""
        return f"<Sheaf '{self.expression}' (linkable={self.linkable}): {len(self.fragments)} fragments>"
