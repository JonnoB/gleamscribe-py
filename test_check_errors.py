#!/usr/bin/env python3
"""Check what errors we're getting."""

from src.glaemscribe.parsers.glaeml import Parser

def check_errors():
    """Check parsing errors."""
    
    with open("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem", 'r') as f:
        content = f.read()
    
    parser = Parser()
    doc = parser.parse(content)
    
    print(f"Total errors: {len(doc.errors)}")
    
    # Show first few errors
    for i, error in enumerate(doc.errors[:10]):
        print(f"  Error {i}: {error}")
    
    # Count error types
    error_types = {}
    for error in doc.errors:
        msg = str(error)
        if "Warning: Failed to parse arguments" in msg:
            error_types["arg_parse"] = error_types.get("arg_parse", 0) + 1
        else:
            error_types["other"] = error_types.get("other", 0) + 1
    
    print(f"\nError types: {error_types}")

if __name__ == "__main__":
    check_errors()
