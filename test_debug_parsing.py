#!/usr/bin/env python3
"""Debug parsing to see what we're getting."""

from src.glaemscribe.parsers.mode_parser import ModeParser

def debug_parsing():
    """Debug the parsing process."""
    
    parser = ModeParser()
    mode = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    
    print(f"Errors: {len(parser.errors)}")
    for error in parser.errors[:5]:
        print(f"  {error}")
    
    if mode and hasattr(mode, 'rule_groups'):
        for name, rg in mode.rule_groups.items():
            print(f"\nRule group: {name}")
            print(f"Terms in root block: {len(rg.root_code_block.terms)}")
            
            # Debug the terms
            for i, term in enumerate(rg.root_code_block.terms[:3]):
                print(f"  Term {i}: {type(term).__name__}")
                if hasattr(term, 'conds'):
                    print(f"    IfTerm with {len(term.conds)} conditions")
                    for j, cond in enumerate(term.conds[:2]):
                        print(f"      Cond {j}: {cond.expression} (line {cond.line})")
                        print(f"        Child block has {len(cond.child_code_block.terms)} terms")
                        # Show first few code lines
                        for k, child_term in enumerate(cond.child_code_block.terms[:3]):
                            if hasattr(child_term, 'code_lines'):
                                print(f"          CodeLinesTerm with {len(child_term.code_lines)} lines")
                                for l, code_line in enumerate(child_term.code_lines[:3]):
                                    print(f"            Line: {code_line.expression}")
                            else:
                                print(f"          Other term: {type(child_term).__name__}")

if __name__ == "__main__":
    debug_parsing()
