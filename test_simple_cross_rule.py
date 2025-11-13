#!/usr/bin/env python3
"""Test simple numeric cross rule end-to-end."""

from src.glaemscribe.core.mode_enhanced import Mode
from src.glaemscribe.core.rule_group import RuleGroup
from src.glaemscribe.core.rule import Rule

def test_simple_cross_rule():
    """Test a simple cross rule from start to finish."""
    
    print("=== Testing Simple Cross Rule End-to-End ===")
    
    # Create mode and rule group
    mode = Mode("test_mode")
    mode.errors = []
    rule_group = RuleGroup(mode, "test_group")
    
    # Add a test rule with cross schema
    print("Adding cross rule: [a][b] --> 2,1 --> [b][a]")
    rule_group.finalize_rule(1, "[a][b]", "[b][a]", "2,1")
    
    print(f"✅ Rules created: {len(rule_group.rules)}")
    
    # Check the rule
    if rule_group.rules:
        rule = rule_group.rules[0]
        print(f"✅ Rule has {len(rule.sub_rules)} sub-rules")
        
        # Show first few sub-rules
        print("First few sub-rules:")
        for i, sub_rule in enumerate(rule.sub_rules[:5]):
            print(f"  {i+1}. {sub_rule.src_combination} -> {sub_rule.dst_combination}")
        
        # Check if cross schema was applied
        if hasattr(rule, 'cross_schema'):
            print(f"✅ Cross schema: {rule.cross_schema}")
        else:
            print("⚠️ No cross schema attribute found")
    
    print(f"Mode errors: {mode.errors}")
    print(f"Rule group errors: {rule_group.errors if hasattr(rule_group, 'errors') else 'None'}")

def test_cross_rule_vs_normal():
    """Compare cross rule vs normal rule behavior."""
    
    print("\n" + "="*60)
    print("=== Cross Rule vs Normal Rule Comparison ===")
    
    mode = Mode("test_mode")
    mode.errors = []
    
    # Normal rule group
    normal_rg = RuleGroup(mode, "normal")
    normal_rg.finalize_rule(1, "[a][b]", "[a][b]")  # No cross schema
    
    # Cross rule group  
    cross_rg = RuleGroup(mode, "cross")
    cross_rg.finalize_rule(1, "[a][b]", "[b][a]", "2,1")  # With cross schema
    
    print("Normal rule sub-rules:")
    for i, sub_rule in enumerate(normal_rg.rules[0].sub_rules[:3]):
        print(f"  {i+1}. {sub_rule.src_combination} -> {sub_rule.dst_combination}")
    
    print("\nCross rule sub-rules:")
    for i, sub_rule in enumerate(cross_rg.rules[0].sub_rules[:3]):
        print(f"  {i+1}. {sub_rule.src_combination} -> {sub_rule.dst_combination}")
    
    # The key difference should be in the source combinations
    # Normal: [a] + [b] = [a,b]
    # Cross: [b] + [a] = [b,a] (swapped!)

if __name__ == "__main__":
    test_simple_cross_rule()
    test_cross_rule_vs_normal()
