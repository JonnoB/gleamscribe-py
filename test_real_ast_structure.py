#!/usr/bin/env python3
"""Debug the real mode file AST structure in detail."""

from src.glaemscribe.parsers.glaeml import Parser

def debug_real_ast():
    """Debug the actual AST structure from the real mode file."""
    
    # Read the real mode file
    with open("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem", 'r') as f:
        content = f.read()
    
    parser = Parser()
    doc = parser.parse(content)
    
    print(f"Document has {len(doc.errors)} errors")
    
    # Find processor block
    processor_nodes = doc.root_node.gpath("processor")
    if processor_nodes:
        processor_node = processor_nodes[0]
        
        # Find rules blocks
        rules_nodes = processor_node.gpath("rules")
        if rules_nodes:
            rules_element = rules_nodes[0]
            print(f"\nRules block found with {len(rules_element.children)} children")
            
            # Look at ALL children to find the if blocks
            for i, child in enumerate(rules_element.children):
                print(f"\nChild {i}:")
                print(f"  Type: {child.type}")
                print(f"  Name: {getattr(child, 'name', 'N/A')}")
                print(f"  Args: {getattr(child, 'args', 'N/A')}")
                
                if hasattr(child, 'is_text') and child.is_text():
                    # Show the actual text content
                    text_content = child.args[0] if child.args else ""
                    lines = text_content.split('\n')
                    print(f"  Text has {len(lines)} lines")
                    # Show first few non-empty lines
                    non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('**')]
                    for j, line in enumerate(non_empty_lines[:5]):
                        print(f"    Line {j}: {line.strip()}")
                        if '\\if' in line:
                            print(f"      *** FOUND IF COMMAND! ***")
                
                elif hasattr(child, 'is_element') and child.is_element():
                    print(f"  Element: {child.name}")
                    if child.name == 'if':
                        print(f"    *** FOUND IF ELEMENT! Condition: {child.args[0] if child.args else 'None'} ***")

if __name__ == "__main__":
    debug_real_ast()
