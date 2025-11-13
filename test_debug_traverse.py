#!/usr/bin/env python3
"""Debug the traverse_if_tree method."""

from src.glaemscribe.parsers.mode_parser import ModeParser
from src.glaemscribe.core.rule_group import RuleGroup

def debug_traverse():
    """Debug the traverse_if_tree method."""
    
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
                elif hasattr(term, 'code_lines'):
                    print(f"    Has {len(term.code_lines)} code lines")
                    for j, code_line in enumerate(term.code_lines[:3]):
                        print(f"      Line {j}: {code_line.expression}")

if __name__ == "__main__":
    debug_traverse()
