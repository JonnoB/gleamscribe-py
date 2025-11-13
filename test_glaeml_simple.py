#!/usr/bin/env python3
"""Test glaeml parser with simple content."""

from src.glaemscribe.parsers.glaeml import Parser

def test_glaeml():
    """Test glaeml parser with simple content."""
    
    content = """
\\mode test
\\language "Quenya"
\\writing "Tengwar"

\\beg processor
  \\beg rules litteral
    0 --> NUM_0
    1 --> NUM_1
  \\end
\\end
"""
    
    parser = Parser()
    doc = parser.parse(content)
    
    print(f"Document: {doc}")
    print(f"Errors: {len(doc.errors)}")
    print(f"Root node children: {len(doc.root_node.children)}")
    
    # Find processor
    processor_nodes = doc.root_node.gpath("processor")
    print(f"Processor nodes: {len(processor_nodes)}")
    
    if processor_nodes:
        rules_nodes = processor_nodes[0].gpath("rules")
        print(f"Rules nodes: {len(rules_nodes)}")
        
        if rules_nodes:
            rules = rules_nodes[0]
            print(f"Rules children: {len(rules.children)}")
            for i, child in enumerate(rules.children[:3]):
                print(f"  Child {i}: {type(child).__name__} - {getattr(child, 'name', 'N/A')}")

if __name__ == "__main__":
    test_glaeml()
