"""SheafChain implementation for Glaemscribe.

This is a port of the Ruby SheafChain class, which handles parsing
chains of sheaves like [a*b][c*d] into sheaf objects.

A sheaf chain is a sequence of sheaves. e.g. :

With a global rule of : src => res
Where src = "[a,b,c][d,e,f]"
and   res = "[x,y,z][1,2,3]"

The generated rules is a list of 9 parallel rules: 
ad => x1, ae => x2, af => x3
bd => y1, be => y2, bf => y3
cd => z1, ce => z2, cf => z3

Or, more complicated: "[m,(b|p)](h|y)[a,e]"
Will generate the following equivalences:
mha = mya
mhe = mye
bha = pha = bya = pya
bhe = phe = bye = phe
"""

from __future__ import annotations
from typing import List
import re
from .sheaf import Sheaf


class SheafChain:
    """A chain of sheaves representing a rule side (source or destination)."""
    
    SHEAF_REGEXP_IN = re.compile(r'\[(.*?)\]')
    SHEAF_REGEXP_OUT = re.compile(r'(\[.*?\])')
    
    def __init__(self, rule, expression: str, is_src: bool):
        """Initialize a sheaf chain.
        
        Args:
            rule: The parent rule object
            expression: The rule side expression like "[a*b][c*d]"
            is_src: Whether this is a source chain (True) or destination (False)
        """
        self.rule = rule
        self.mode = rule.mode
        self.is_src = is_src
        self.expression = expression
        
        # Split expression with '[...]' patterns. e.g. 'b[a*c*d]e' => [b, a*c*d, e]
        sheaf_exps = self.SHEAF_REGEXP_OUT.split(expression)
        sheaf_exps = [elt.strip() for elt in sheaf_exps if elt.strip()]
        
        sheaf_exps = [self._parse_sheaf_expression(sheaf_exp) for sheaf_exp in sheaf_exps]
        
        # Create sheaf objects
        self.sheaves = [Sheaf(self, sd['exp'], sd['linkable']) for sd in sheaf_exps]
        
        # Ensure we have at least one sheaf
        if not self.sheaves:
            self.sheaves = [Sheaf(self, "", False)]
    
    def _parse_sheaf_expression(self, sheaf_exp: str) -> dict:
        """Parse a sheaf expression to determine if it's linkable.
        
        Args:
            sheaf_exp: Sheaf expression string
            
        Returns:
            Dict with 'exp' and 'linkable' keys
        """
        match = self.SHEAF_REGEXP_IN.match(sheaf_exp)
        linkable = False
        
        if match:
            # Take the interior of the brackets it was a [...] expression
            sheaf_exp = match.group(1)
            linkable = True
        
        return {'exp': sheaf_exp.strip(), 'linkable': linkable}
    
    def is_src(self) -> bool:
        """Check if this is a source chain."""
        return self.is_src
    
    def is_dst(self) -> bool:
        """Check if this is a destination chain."""
        return not self.is_src
    
    def __str__(self) -> str:
        """String representation of the sheaf chain."""
        return f"<SheafChain '{self.expression}' (src={self.is_src}): {len(self.sheaves)} sheaves>"
