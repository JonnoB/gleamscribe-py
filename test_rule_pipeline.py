#!/usr/bin/env python3
"""Test the new Rule/SubRule/SheafChain pipeline."""

from src.glaemscribe.parsers.mode_parser import ModeParser

def test_rule_pipeline():
    """Test the complete rule processing pipeline."""
    
    parser = ModeParser()
    mode = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    
    if mode and hasattr(mode, 'rule_groups'):
        print(f"Rule groups: {len(mode.rule_groups)}")
        
        for name, rg in mode.rule_groups.items():
            print(f"\nRule group: {name}")
            print(f"  Terms before finalize: {len(rg.root_code_block.terms)}")
            
            # Finalize the rule group
            rg.finalize({})
            
            print(f"  Variables: {len(rg.vars)}")
            print(f"  Rules: {len(rg.rules)}")
            
            # Check rule types
            for i, rule in enumerate(rg.rules[:3]):
                print(f"    Rule {i}: {type(rule).__name__}")
                if hasattr(rule, 'sub_rules'):
                    print(f"      Sub-rules: {len(rule.sub_rules)}")
                    for j, sub_rule in enumerate(rule.sub_rules[:3]):
                        src = "".join(sub_rule.src_combination)
                        dst = " ".join(sub_rule.dst_combination)
                        print(f"        {j}: '{src}' => '{dst}'")
        
        # Test transcription processor
        print(f"\nTesting transcription processor...")
        try:
            mode.processor.finalize({})
            print(f"  ✓ Processor finalized successfully!")
            print(f"  Tree built with no recursion errors!")
            
            # Test simple transcription
            result = mode.processor.transcribe("hello")
            print(f"  Test transcription: {result[:5]}")
            
        except Exception as e:
            print(f"  ✗ Processor error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_rule_pipeline()
