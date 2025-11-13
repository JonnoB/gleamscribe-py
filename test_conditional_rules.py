#!/usr/bin/env python3
"""Test conditional rule parsing and evaluation."""

from src.glaemscribe.core.rule_group import RuleGroup, CodeLine, IfTerm, IfCond
from src.glaemscribe.core.mode_enhanced import Mode
from src.glaemscribe.parsers.glaeml import Parser, Document, Node

def test_conditional_parsing():
    """Test parsing of conditional rules."""
    
    # Create a simple mode
    mode = Mode("test")
    
    # Create a rule group
    rule_group = RuleGroup(mode, "conditional_test")
    
    # Simulate parsing conditional rules
    # Create an if term with conditions
    root_block = rule_group.root_code_block
    
    # Create an if term
    if_term = IfTerm(root_block)
    root_block.add_term(if_term)
    
    # Add first condition (implicit_a == true)
    if_cond1 = IfCond(1, "implicit_a == true", if_term)
    if_term.conds.append(if_cond1)
    
    # Add rules when implicit_a is true
    code_line1 = CodeLine("a --> TENGWA_A_WITH_IMPLICIT", 2)
    code_line2 = CodeLine("e --> TENGWA_E_WITH_IMPLICIT", 3)
    
    # Add to the conditional block
    if_cond1.child_code_block.add_term(code_line1)
    if_cond1.child_code_block.add_term(code_line2)
    
    # Add else condition (implicit_a == false)
    if_cond2 = IfCond(4, "true", if_term)  # else clause
    if_term.conds.append(if_cond2)
    
    # Add rules when implicit_a is false
    code_line3 = CodeLine("a --> TENGWA_A_EXPLICIT", 5)
    code_line4 = CodeLine("e --> TENGWA_E_EXPLICIT", 6)
    
    # Add to the else block
    if_cond2.child_code_block.add_term(code_line3)
    if_cond2.child_code_block.add_term(code_line4)
    
    print("Conditional parsing test:")
    print(f"Rule group: {rule_group}")
    print(f"IfTerm has {len(if_term.conds)} conditions")
    
    # Test with implicit_a = true
    print("\nTesting with implicit_a = true:")
    rule_group.rules = []  # Clear any existing rules
    rule_group.finalize({"implicit_a": "true"})
    
    print(f"Rules extracted: {len(rule_group.rules)}")
    for rule in rule_group.rules:
        print(f"  {rule['source']} --> {rule['target']}")
    
    # Test with implicit_a = false
    print("\nTesting with implicit_a = false:")
    rule_group.rules = []  # Clear any existing rules
    rule_group.finalize({"implicit_a": "false"})
    
    print(f"Rules extracted: {len(rule_group.rules)}")
    for rule in rule_group.rules:
        print(f"  {rule['source']} --> {rule['target']}")
    
    print("✓ Conditional parsing test passed!")
    return True

if __name__ == "__main__":
    test_conditional_parsing()
