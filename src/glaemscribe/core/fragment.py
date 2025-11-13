"""Fragment implementation for Glaemscribe.

This is a port of the Ruby Fragment class, which handles parsing
equivalences like h(a|ä)(i|ï) into combinations.
"""

from __future__ import annotations
import re
from typing import List, Optional, Any

from ..parsers.glaeml import Error

# Unicode variable pattern - matches {UNI_XXXX}
UNICODE_VAR_NAME_REGEXP_OUT = re.compile(r'\{UNI_([0-9A-F]+)\}')

# Word boundary patterns
WORD_BOUNDARY_LANG = '_'
WORD_BOUNDARY_TREE = '\u0000'


class Fragment:
    """A fragment is a sequence of equivalences.
    
    For example h(a|ä)(i|ï) represents the four combinations:
    hai, haï, häi, häï
    """
    
    EQUIVALENCE_SEPARATOR = ","
    EQUIVALENCE_RX_OUT = re.compile(r'(\(.*?\))')
    EQUIVALENCE_RX_IN = re.compile(r'\((.*?)\)')
    
    def __init__(self, sheaf, expression: str):
        """Initialize a fragment.
        
        Args:
            sheaf: The parent sheaf object
            expression: Fragment expression like "h(a,ä)(i,ï)"
        """
        self.sheaf = sheaf
        self.mode = sheaf.mode
        self.rule = sheaf.rule
        self.expression = expression
        self.combinations: List[List[str]] = []
        self.errors: List[str] = []
        
        # Split the fragment, turn it into an array of arrays, e.g. [[h],[a,ä],[i,ï]]
        equivalences = self.EQUIVALENCE_RX_OUT.split(expression)
        equivalences = [eq.strip() for eq in equivalences if eq.strip()]
        
        equivalences = [self._parse_equivalence(eq) for eq in equivalences]
        if not equivalences:
            equivalences = [[[""]]]  # Handle empty case
        
        # Validate destination fragments
        if self.is_dst():
            self._validate_destination(equivalences)
        
        # Generate all combinations using Cartesian product
        self._generate_combinations(equivalences)
    
    def _parse_equivalence(self, eq: str) -> List[List[List[str]]]:
        """Parse a single equivalence.
        
        Args:
            eq: Equivalence string like "(a,ä)" or "h"
            
        Returns:
            Parsed equivalence structure
        """
        match = self.EQUIVALENCE_RX_IN.match(eq)
        if match:
            # Handle parenthesized equivalence: (a,ä)
            inner = match.group(1)
            parts = inner.split(self.EQUIVALENCE_SEPARATOR, -1)
            return [
                [self._finalize_fragment_leaf(leaf.strip()) for leaf in part.split()]
                for part in parts
            ]
        else:
            # Handle simple equivalence: h
            return [[self._finalize_fragment_leaf(leaf.strip()) for leaf in eq.split()]]
    
    def _finalize_fragment_leaf(self, leaf: str) -> str:
        """Process a leaf token.
        
        This matches Ruby's finalize_fragment_leaf method exactly.
        Unicode variables are converted to actual characters for source fragments.
        
        Args:
            leaf: Leaf token to process
            
        Returns:
            Processed leaf token with Unicode variables converted
        """
        if self.sheaf.is_src():
            # Replace {UNI_XXXX} by its value to allow any unicode char to be found
            # in the transcription tree (matches Ruby behavior exactly)
            def replace_unicode(match):
                hex_code = match.group(1)
                try:
                    # Convert hex to Unicode character
                    unicode_char = chr(int(hex_code, 16))
                    # Special case: replace underscore with word boundary
                    if unicode_char == '_':
                        return '\u0001'
                    return unicode_char
                except ValueError:
                    # Invalid hex code - return original
                    return match.group(0)
            
            leaf = UNICODE_VAR_NAME_REGEXP_OUT.sub(replace_unicode, leaf)
            
            # Replace '_' (word boundary) by '\u0000' to allow the real 
            # underscore to be used in the transcription tree
            # (Do it after replacing the uni_xxx vars because they have underscores inside)
            leaf = leaf.replace('_', WORD_BOUNDARY_TREE)
        
        return leaf
    
    def _validate_destination(self, equivalences: List[List[List[str]]]):
        """Validate that all symbols in destination fragments exist in charsets.
        
        Args:
            equivalences: Parsed equivalences to validate
        """
        # TODO: Implement charset validation
        # This requires access to mode.charsets
        pass
    
    def _generate_combinations(self, equivalences: List[List[List[str]]]):
        """Generate all combinations from equivalences using Cartesian product.
        
        Args:
            equivalences: Parsed equivalences
        """
        if not equivalences:
            self.combinations = [[""]]
            return
        
        # Start with first equivalence
        current = equivalences[0]
        
        # Generate combinations using iterative approach
        result = []
        for first_equiv in current:
            # Handle nested lists in first_equiv
            if isinstance(first_equiv[0], list):
                # Flatten nested structure
                first_options = []
                for nested in first_equiv:
                    first_options.extend(nested)
            else:
                first_options = first_equiv
            
            for first_token in first_options:
                if len(equivalences) == 1:
                    result.append([first_token])
                else:
                    # Recursively combine with rest
                    rest_combinations = self._generate_rest_combinations(equivalences[1:])
                    for rest_combo in rest_combinations:
                        result.append([first_token] + rest_combo)
        
        self.combinations = result
    
    def _generate_rest_combinations(self, rest_equivalences: List[List[List[str]]]) -> List[List[str]]:
        """Generate combinations for remaining equivalences.
        
        Args:
            rest_equivalences: Remaining equivalences to process
            
        Returns:
            List of combinations
        """
        if not rest_equivalences:
            return [[]]
        
        current = rest_equivalences[0]
        result = []
        
        for equiv in current:
            if isinstance(equiv[0], list):
                options = []
                for nested in equiv:
                    options.extend(nested)
            else:
                options = equiv
            
            for token in options:
                if len(rest_equivalences) == 1:
                    result.append([token])
                else:
                    for rest_combo in self._generate_rest_combinations(rest_equivalences[1:]):
                        result.append([token] + rest_combo)
        
        return result
    
    def is_src(self) -> bool:
        """Check if this is a source fragment."""
        return self.sheaf.is_src()
    
    def is_dst(self) -> bool:
        """Check if this is a destination fragment."""
        return self.sheaf.is_dst()
    
    def __str__(self) -> str:
        """String representation of the fragment."""
        return f"<Fragment '{self.expression}': {len(self.combinations)} combinations>"
