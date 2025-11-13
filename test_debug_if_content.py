#!/usr/bin/env python3
"""Debug what's inside the if block."""

from src.glaemscribe.parsers.mode_parser import ModeParser

def debug_if_content():
    """Debug the if block content."""
    
    parser = ModeParser()
    mode = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    
    if mode and hasattr(mode, 'rule_groups'):
        for name, rg in mode.rule_groups.items():
            print(f"Rule group: {name}")
            print(f"Root block terms: {len(rg.root_code_block.terms)}")
            
            # Check what type of terms we have
            for i, term in enumerate(rg.root_code_block.terms):
                print(f"  Term {i}: {type(term).__name__}")
                if hasattr(term, 'conds'):
                    print(f"    Has {len(term.conds)} conditions")
                    for j, cond in enumerate(term.conds):
                        print(f"      Condition {j}: {cond.expression}")
                        print(f"        Child block has {len(cond.child_code_block.terms)} terms")
                        for k, child_term in enumerate(cond.child_code_block.terms[:3]):
                            print(f"          Child term {k}: {type(child_term).__name__}")
                            if hasattr(child_term, 'code_lines'):
                                print(f"            Has {len(child_term.code_lines)} code lines")
                                for l, code_line in enumerate(child_term.code_lines[:5]):
                                    print(f"              Line {l}: {code_line.expression}")

if __name__ == "__main__":
    debug_if_content()
