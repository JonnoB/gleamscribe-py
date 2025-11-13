#!/usr/bin/env python3
"""Debug the raw AST structure."""

from src.glaemscribe.parsers.glaeml import Parser

def debug_ast():
    """Debug the AST structure."""
    
    parser = Parser()
    doc = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    
    print(f"Document: {doc}")
    print(f"Root node: {doc.root_node}")
    print(f"Root node children: {len(doc.root_node.children)}")
    
    # Find the processor block
    processor_nodes = doc.root_node.gpath("processor")
    print(f"Processor nodes found: {len(processor_nodes)}")
    
    if processor_nodes:
        processor_node = processor_nodes[0]
        print(f"Processor node: {processor_node}")
        
        # Find rules blocks
        rules_nodes = processor_node.gpath("rules")
        print(f"Rules nodes found: {len(rules_nodes)}")
        
        if rules_nodes:
            rules_element = rules_nodes[0]
            print(f"Rules element: {rules_element}")
            print(f"Args: {rules_element.args}")
            print(f"Children: {len(rules_element.children)}")
            
            # Look at first few children
            for i, child in enumerate(rules_element.children[:5]):
                print(f"\nChild {i}:")
                print(f"  Type: {getattr(child, 'type', 'Unknown')}")
                print(f"  Name: {getattr(child, 'name', 'N/A')}")
                print(f"  Args: {getattr(child, 'args', 'N/A')}")
                if hasattr(child, 'is_text') and child.is_text():
                    print(f"  Text preview: {child.args[0][:100] if child.args else 'None'}...")
                elif hasattr(child, 'is_element') and child.is_element():
                    print(f"  Element: {child.name}")
                    if child.name == 'if':
                        print(f"    IF condition: {child.args[0] if child.args else 'None'}")

if __name__ == "__main__":
    debug_ast()
