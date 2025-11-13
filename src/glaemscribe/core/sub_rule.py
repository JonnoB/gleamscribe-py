"""SubRule implementation for Glaemscribe.

This is a port of the Ruby SubRule class, which represents a single
combination from a rule after processing through SheafChainIterator.
"""

from __future__ import annotations
from typing import List


class SubRule:
    """A single rule combination generated from a parent rule.
    
    For example, from rule "[a*b][c*d] => [x*y][1*2]" we might get:
    src_combination = ["a", "c"]
    dst_combination = ["x", "1"]
    """
    
    def __init__(self, rule, src_combination: List[str], dst_combination: List[str]):
        """Initialize a subrule.
        
        Args:
            rule: The parent rule object
            src_combination: List of source tokens
            dst_combination: List of destination tokens
        """
        self.rule = rule
        self.src_combination = src_combination
        self.dst_combination = dst_combination
    
    def __str__(self) -> str:
        """String representation of the subrule."""
        src_str = "".join(self.src_combination)
        dst_str = " ".join(self.dst_combination)
        return f"<SubRule '{src_str}' => '{dst_str}'>"
