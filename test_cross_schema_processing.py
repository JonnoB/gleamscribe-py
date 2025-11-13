#!/usr/bin/env python3
"""Test cross schema processing in SheafChainIterator."""

from src.glaemscribe.core.sheaf_chain_iterator import SheafChainIterator
from src.glaemscribe.core.sheaf_chain import SheafChain
from src.glaemscribe.core.rule import Rule
from src.glaemscribe.core.rule_group import RuleGroup
from src.glaemscribe.core.mode_enhanced import Mode

def test_cross_schema_processing():
    """Test that cross schemas are processed correctly."""
    
    print("=== Testing Cross Schema Processing ===")
    
    # Create a mock mode and rule for testing
    mode = Mode("test_mode")
    mode.errors = []
    rule_group = RuleGroup(mode, "test_group")
    rule = Rule(1, rule_group)
    
    # Test Case 1: Simple cross schema "2,1" (swap positions)
    print("\n--- Test Case 1: Cross Schema '2,1' (swap) ---")
    
    # Create a simple sheaf chain: [a,b] + [c,d] 
    src_chain = SheafChain(rule, "[a][b]", True)
    
    # Test without cross schema (normal order)
    iterator_normal = SheafChainIterator(src_chain)
    print(f"Normal cross_array: {iterator_normal.cross_array}")
    print(f"Normal prototype: {iterator_normal.prototype}")
    
    # Test with cross schema "2,1" (swap)
    iterator_cross = SheafChainIterator(src_chain, "2,1")
    print(f"Cross '2,1' cross_array: {iterator_cross.cross_array}")
    print(f"Cross '2,1' prototype: {iterator_cross.prototype}")
    
    if iterator_cross.errors:
        print(f"Errors: {iterator_cross.errors}")
    else:
        print("✅ Cross schema '2,1' processed successfully")
    
    # Test Case 2: Identity schema
    print("\n--- Test Case 2: Cross Schema 'identity' ---")
    
    iterator_identity = SheafChainIterator(src_chain, "identity")
    print(f"Identity cross_array: {iterator_identity.cross_array}")
    print(f"Identity prototype: {iterator_identity.prototype}")
    
    if iterator_identity.errors:
        print(f"Errors: {iterator_identity.errors}")
    else:
        print("✅ Identity schema processed successfully")
    
    # Test Case 3: Invalid schemas
    print("\n--- Test Case 3: Invalid Cross Schemas ---")
    
    invalid_schemas = [
        "2,2,1",  # Duplicate
        "3,1",    # Out of range for 2 positions
        "2",      # Wrong count
        "abc",    # Non-numeric
        "{VAR}"   # Variable (not implemented yet)
    ]
    
    for schema in invalid_schemas:
        iterator = SheafChainIterator(src_chain, schema)
        if iterator.errors:
            print(f"✅ '{schema}' correctly rejected: {iterator.errors[0]}")
        else:
            print(f"❌ '{schema}' should have been rejected")

def test_cross_schema_combinations():
    """Test that cross schemas affect combination generation correctly."""
    
    print("\n" + "="*60)
    print("=== Testing Cross Schema Combination Generation ===")
    
    # Create mock objects
    mode = Mode("test_mode")
    mode.errors = []
    rule_group = RuleGroup(mode, "test_group")
    rule = Rule(1, rule_group)
    
    # Create sheaf chain: [a,b] + [c,d]
    src_chain = SheafChain(rule, "[a][b]", True)
    
    print("Source sheaf chain: [a] + [b]")
    print("Expected combinations without cross: a, b")
    print("Expected combinations with '2,1': b, a (swapped)")
    
    # Test normal order
    iterator_normal = SheafChainIterator(src_chain)
    print(f"\nNormal combinations:")
    for i in range(4):  # There should be 4 combinations total
        combos = iterator_normal.combinations()
        print(f"  Step {i}: {combos}")
        if not iterator_normal.iterate():
            break
    
    # Test cross order
    iterator_cross = SheafChainIterator(src_chain, "2,1")
    print(f"\nCross '2,1' combinations:")
    for i in range(4):  # There should be 4 combinations total
        combos = iterator_cross.combinations()
        print(f"  Step {i}: {combos}")
        if not iterator_cross.iterate():
            break

def test_complex_cross_schema():
    """Test more complex cross schema with multiple positions."""
    
    print("\n" + "="*60)
    print("=== Testing Complex Cross Schema ===")
    
    # Create mock objects
    mode = Mode("test_mode")
    mode.errors = []
    rule_group = RuleGroup(mode, "test_group")
    rule = Rule(1, rule_group)
    
    # Create sheaf chain with 3 positions: [a] + [b] + [c]
    src_chain = SheafChain(rule, "[a][b][c]", True)
    
    print("Source sheaf chain: [a] + [b] + [c]")
    print("Testing cross schema '3,1,2' (move first to last, shift others)")
    
    # Test complex cross schema
    iterator = SheafChainIterator(src_chain, "3,1,2")
    print(f"Cross '3,1,2' cross_array: {iterator.cross_array}")
    print(f"Cross '3,1,2' prototype: {iterator.prototype}")
    
    if iterator.errors:
        print(f"❌ Errors: {iterator.errors}")
    else:
        print("✅ Complex cross schema processed successfully")
        
        # Show first few combinations
        print(f"First few combinations:")
        for i in range(3):
            combos = iterator.combinations()
            print(f"  Step {i}: {combos}")
            if not iterator.iterate():
                break

if __name__ == "__main__":
    test_cross_schema_processing()
    test_cross_schema_combinations()
    test_complex_cross_schema()
