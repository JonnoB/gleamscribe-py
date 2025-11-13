"""SheafChainIterator implementation for Glaemscribe.

This is a port of the Ruby SheafChainIterator class, which generates
all combinations from a SheafChain using an iterator pattern.
"""

from __future__ import annotations
from typing import List, Optional
import itertools


class SheafChainIterator:
    """Iterates through all combinations in a SheafChain.
    
    Uses a counter-based approach to efficiently generate combinations
    without storing all combinations in memory at once.
    """
    
    def __init__(self, sheaf_chain, cross_schema: Optional[str] = None):
        """Initialize the iterator.
        
        Args:
            sheaf_chain: The SheafChain to iterate over
            cross_schema: Optional cross schema string like "2,1"
        """
        self.sheaf_chain = sheaf_chain
        self.errors = []
        
        # Sizes contains the number of fragments/sheaf
        self.sizes = [len(sheaf.fragments) for sheaf in sheaf_chain.sheaves]
        
        # An array of counters, one for each sheaf, to increment on fragments
        self.iterators = [0] * len(self.sizes)
        
        # Construct the identity array
        identity_cross_array = list(range(len(sheaf_chain.sheaves)))
        
        # Make a list of iterable sheaves
        iterable_idxs = []
        prototype_array = []
        
        for i, sheaf in enumerate(sheaf_chain.sheaves):
            if sheaf.linkable:
                iterable_idxs.append(i)
                prototype_array.append(len(sheaf.fragments))
        
        self.cross_array = identity_cross_array
        self.prototype = "x".join(map(str, prototype_array))
        if not self.prototype:
            self.prototype = 'CONST'
        
        # Construct the cross array if cross_schema is provided
        if cross_schema:
            self._construct_cross_array(cross_schema, iterable_idxs, prototype_array)
    
    def _construct_cross_array(self, cross_schema: str, iterable_idxs: List[int], prototype_array: List[int]):
        """Construct the cross array for cross schema processing.
        
        This matches the Ruby implementation exactly.
        
        Args:
            cross_schema: Cross schema string like "2,1", "{VAR_NAME}", or "identity"
            iterable_idxs: List of iterable sheaf indices
            prototype_array: Array of prototype sizes
        """
        # Handle identity keyword (Ruby: if cross_schema == "identity")
        if cross_schema == "identity":
            # Use identity permutation - no changes needed
            return
        
        # Handle variable substitution (Ruby: if cross_schema starts with "{")
        if cross_schema.startswith("{") and cross_schema.endswith("}"):
            var_name = cross_schema[1:-1]  # Remove { }
            # TODO: Implement variable resolution in Phase 2
            self.errors.append(f"Variable cross schema not yet implemented: {var_name}")
            return
        
        # Parse numeric schema (Ruby: cross_schema.split(",").map{ |i| i.to_i - 1 })
        try:
            schema_array = [int(i.strip()) - 1 for i in cross_schema.split(",")]
        except ValueError:
            self.errors.append(f"Invalid cross schema: {cross_schema}")
            return
        
        # Verify count matches (Ruby: ca_count != it_count)
        it_count = len(iterable_idxs)
        ca_count = len(schema_array)
        
        if ca_count != it_count:
            self.errors.append(f"{it_count} linkable sheaves found in right predicate, but {ca_count} elements in cross rule.")
            return
        
        # Verify permutation is valid (Ruby: it_identity_array != cross_schema.sort)
        it_identity_array = list(range(it_count))
        if sorted(it_identity_array) != sorted(schema_array):
            self.errors.append("Cross rule schema should be a permutation of the identity (it should contain 1,2,..,n numbers once and only once).")
            return
        
        # Apply permutation to cross_array (Ruby logic)
        proto_array_permutted = prototype_array.copy()
        
        for to_idx, from_idx in enumerate(schema_array):
            to_permut = iterable_idxs[from_idx]
            permut = iterable_idxs[to_idx]
            self.cross_array[to_permut] = permut
            proto_array_permutted[from_idx] = prototype_array[to_idx]
        
        # Recalculate prototype (Ruby: self.prototype = "x".join(map(str, proto_array_permutted)))
        self.prototype = "x".join(map(str, proto_array_permutted))
        if not self.prototype:
            self.prototype = 'CONST'
    
    def iterate(self) -> bool:
        """Move to the next combination.
        
        Returns:
            True if there are more combinations, False if we've wrapped around
        """
        pos = 0
        while pos < len(self.sizes):
            realpos = self.cross_array[pos]
            self.iterators[realpos] += 1
            
            if self.iterators[realpos] >= self.sizes[realpos]:
                self.iterators[realpos] = 0
                pos += 1
            else:
                return True
        
        # Wrapped!
        return False
    
    def combinations(self) -> List[List[str]]:
        """Calculate all combinations for the chain, for the current iterator value.
        
        Returns:
            List of combinations (each combination is a list of strings)
        """
        # Build fragments array applying cross permutation
        # The cross_array determines which sheaf position maps to which fragment
        resolved = []
        for pos, sheaf_index in enumerate(self.cross_array):
            sheaf = self.sheaf_chain.sheaves[sheaf_index]
            fragment_index = self.iterators[sheaf_index]
            fragment = sheaf.fragments[fragment_index]
            resolved.append(fragment.combinations)
        
        # Calculate Cartesian product of all fragment combinations
        if not resolved:
            return [[""]]
        
        # Start with first fragment's combinations
        result = resolved[0]
        
        # Multiply with each subsequent fragment's combinations
        for i in range(1, len(resolved)):
            result = [combo1 + combo2 for combo1 in result for combo2 in resolved[i]]
        
        return result
    
    def __str__(self) -> str:
        """String representation of the iterator."""
        return f"<SheafChainIterator prototype='{self.prototype}': {self.iterators}/{self.sizes}>"
