#!/usr/bin/env python3
"""Test real cross rule from English Tengwar mode."""

from src.glaemscribe.parsers.mode_parser import ModeParser

def test_real_cross_rule():
    """Test a real cross rule from English Tengwar mode."""
    
    print("=== Testing Real Cross Rule from English Tengwar ===")
    
    # Load the English Tengwar mode
    parser = ModeParser()
    mode = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/english-tengwar-espeak.glaem")
    
    if not mode:
        print("❌ Failed to load English Tengwar mode")
        return
    
    print(f"✅ Loaded mode: {mode.name}")
    print(f"✅ Rule groups: {list(mode.rule_groups.keys())}")
    
    # Finalize the processor
    if hasattr(mode, 'processor') and mode.processor:
        mode.processor.finalize({})
        print(f"✅ Processor finalized with {len(mode.processor.rule_groups)} rule groups")
        
        # Check if we have any rules with cross schemas
        total_rules = 0
        cross_rules = 0
        
        for rg_name, rg in mode.processor.rule_groups.items():
            rules_count = len(rg.rules) if hasattr(rg, 'rules') else 0
            total_rules += rules_count
            print(f"  Rule group '{rg_name}': {rules_count} rules")
            
            # Check for cross schemas in rules
            if hasattr(rg, 'rules'):
                for rule in rg.rules:
                    if hasattr(rule, 'cross_schema') and rule.cross_schema:
                        cross_rules += 1
                        print(f"    ✅ Cross rule: {rule.cross_schema}")
        
        print(f"\n📊 Summary:")
        print(f"  Total rules: {total_rules}")
        print(f"  Cross rules: {cross_rules}")
        
        if cross_rules > 0:
            print("🎉 Cross rules are being processed!")
        else:
            print("⚠️ No cross rules found (may need to check rule parsing)")
            
    else:
        print("❌ No processor found in mode")

if __name__ == "__main__":
    test_real_cross_rule()
