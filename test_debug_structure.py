#!/usr/bin/env python3
"""Debug the actual structure of parsed elements."""

from src.glaemscribe.parsers.glaeml import Parser

def debug_structure():
    """Debug the structure of parsed elements."""
    
    with open("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem", 'r') as f:
        content = f.read()
    
    parser = Parser()
    doc = parser.parse(content)
    
    # Find processor.rules
    processor_nodes = doc.root_node.gpath("processor")
    if processor_nodes:
        processor_node = processor_nodes[0]
        rules_nodes = processor_node.gpath("rules")
        
        if rules_nodes:
            rules_element = rules_nodes[0]
            print(f"Rules element: {rules_element.name}")
            print(f"Rules args: {rules_element.args}")
            print(f"Rules children: {len(rules_element.children)}")
            
            # Look at ALL children
            for i, child in enumerate(rules_element.children):
                print(f"\nChild {i}:")
                print(f"  Name: {child.name}")
                print(f"  Type: {child.type}")
                print(f"  Args: {child.args}")
                
                if child.is_element() and child.name == 'if':
                    print(f"  *** FOUND IF! ***")
                    print(f"  IF children: {len(child.children)}")
                    for j, if_child in enumerate(child.children[:3]):
                        print(f"    IF child {j}: {if_child.name} - {getattr(if_child, 'args', [])}")

if __name__ == "__main__":
    debug_structure()
