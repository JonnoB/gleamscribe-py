"""Rule implementation for Glaemscribe.

This is a port of the Ruby Rule class, which represents a transcription
rule with source and destination sheaf chains.
"""

from __future__ import annotations
from typing import List, Optional
from .sheaf_chain import SheafChain
from .sheaf_chain_iterator import SheafChainIterator
from .sub_rule import SubRule


class Rule:
    """A transcription rule with source and destination chains.
    
    Rules are processed through SheafChainIterator to generate
    all possible SubRule combinations.
    """
    
    def __init__(self, line: int, rule_group):
        """Initialize a rule.
        
        Args:
            line: Line number where the rule was defined
            rule_group: The parent rule group
        """
        self.line = line
        self.rule_group = rule_group
        self.mode = rule_group.mode
        self.sub_rules: List[SubRule] = []
        self.errors: List[str] = []
        
        # These will be set by finalize_rule
        self.src_sheaf_chain: Optional[SheafChain] = None
        self.dst_sheaf_chain: Optional[SheafChain] = None
    
    def finalize(self, cross_schema: Optional[str] = None):
        """Finalize the rule by generating all sub-rules.
        
        Args:
            cross_schema: Optional cross schema for rule processing
        """
        if self.errors:
            # Add errors to mode
            for error in self.errors:
                self.mode.errors.append(error)
            return
        
        if not self.src_sheaf_chain or not self.dst_sheaf_chain:
            self.errors.append("Rule missing source or destination chain")
            return
        
        # Create iterators for source and destination chains
        srccounter = SheafChainIterator(self.src_sheaf_chain)
        dstcounter = SheafChainIterator(self.dst_sheaf_chain, cross_schema)
        
        if srccounter.errors:
            self.errors.extend(srccounter.errors)
            for error in self.errors:
                self.mode.errors.append(error)
            return
        
        if dstcounter.errors:
            self.errors.extend(dstcounter.errors)
            for error in self.errors:
                self.mode.errors.append(error)
            return
        
        # Check prototypes match
        srcp = srccounter.prototype
        dstp = dstcounter.prototype
        
        if srcp != dstp:
            error_msg = f"Source and destination are not compatible ({srcp} vs {dstp})"
            self.errors.append(error_msg)
            self.mode.errors.append(error_msg)
            return
        
        # Generate all sub-rules
        try:
            while True:
                # Get all source combinations for current iterator state
                src_combinations = srccounter.combinations()
                
                # Get first destination combination (all should map to same destination)
                dst_combination = dstcounter.combinations()
                if dst_combination:
                    dst_combination = dst_combination[0]
                else:
                    dst_combination = []
                
                # Create sub-rules for each source combination
                for src_combination in src_combinations:
                    self.sub_rules.append(SubRule(self, src_combination, dst_combination))
                
                # Move to next destination combination
                if not dstcounter.iterate():
                    break
            
            # Continue iterating through source combinations
            while srccounter.iterate():
                src_combinations = srccounter.combinations()
                dst_combination = dstcounter.combinations()
                if dst_combination:
                    dst_combination = dst_combination[0]
                else:
                    dst_combination = []
                
                for src_combination in src_combinations:
                    self.sub_rules.append(SubRule(self, src_combination, dst_combination))
                
                if not dstcounter.iterate():
                    break
                    
        except Exception as e:
            self.errors.append(f"Error generating sub-rules: {e}")
            for error in self.errors:
                self.mode.errors.append(error)
    
    def __str__(self) -> str:
        """String representation of the rule."""
        return f"<Rule line={self.line}: {len(self.sub_rules)} sub-rules>"
