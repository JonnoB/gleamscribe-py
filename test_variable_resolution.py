#!/usr/bin/env python3
"""Test variable resolution with nested variables."""

from src.glaemscribe.core.rule_group import RuleGroup
from src.glaemscribe.core.mode_enhanced import Mode

def test_nested_variables():
    """Test nested variable resolution."""
    
    # Create a mode
    mode = Mode("test")
    
    # Create a rule group
    rule_group = RuleGroup(mode, "variable_test")
    
    # Add nested variables like in the real mode
    rule_group.add_var("VOWELS", "a * e * i * o * u")
    rule_group.add_var("WLONG", "á * é * í * ó * ú")
    rule_group.add_var("WDIPHTHONGS", "ae * ai * ei * oi * ui")
    rule_group.add_var("NULL", "")
    
    # Add a composite variable
    rule_group.add_var("V_D_WN", "[ {VOWELS} {WLONG} {WDIPHTHONGS} * {NULL} ]")
    
    print("Variable resolution test:")
    print(f"Variables defined: {list(rule_group.vars.keys())}")
    
    # Test variable resolution
    test_cases = [
        ("a", "a"),
        ("{VOWELS}", "a * e * i * o * u"),
        ("{V_D_WN}", "[ a * e * i * o * u á * é * í * ó * ú ae * ai * ei * oi * ui *  ]"),
        ("[{V_D_WN}]", "[[ a * e * i * o * u á * é * í * ó * ú ae * ai * ei * oi * ui *  ]]")
    ]
    
    for input_expr, expected in test_cases:
        result = rule_group.apply_vars(1, input_expr)
        print(f"'{input_expr}' -> '{result}'")
        if result == expected:
            print("  ✓ Correct")
        else:
            print(f"  ✗ Expected: '{expected}'")
    
    # Test with rules
    print("\nTesting rule with variables:")
    rule_source = "{V_D_WN}"
    rule_target = "TEHTA"
    
    resolved_source = rule_group.apply_vars(1, rule_source)
    resolved_target = rule_group.apply_vars(1, rule_target)
    
    print(f"Rule: {rule_source} --> {rule_target}")
    print(f"Resolved: {resolved_source} --> {resolved_target}")
    
    return True

if __name__ == "__main__":
    test_nested_variables()
