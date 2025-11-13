#!/usr/bin/env python3
"""Test the Mode parser."""

from src.glaemscribe.parsers.mode_parser import ModeParser

def test_simple_mode():
    """Test parsing a simple mode definition."""
    
    # Create a simple test mode file
    test_content = r"""
\version 1.0.0
\language "Quenya"
\writing "Tengwar"
\mode "Quenya Tengwar - Test"
\authors "Test Author"

\charset tengwar_ds_annatar true

\beg options
  \option implicit_a false
  \beg option tehta_shape A_SHAPE_THREE_DOTS
    \value A_SHAPE_THREE_DOTS 1
    \value A_SHAPE_CIRCUMFLEX 2
  \end
\end
"""
    
    # Write test file
    test_file = "/tmp/test_mode.glaem"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    # Parse it
    parser = ModeParser()
    mode = parser.parse(test_file)
    
    print("Simple mode test:")
    print(f"Mode name: {mode.name}")
    print(f"Language: {mode.language}")
    print(f"Writing: {mode.writing}")
    print(f"Human name: {mode.human_name}")
    print(f"Authors: {mode.authors}")
    print(f"Version: {mode.version}")
    
    print(f"\nSupported charsets: {len(mode.supported_charsets)}")
    for name in mode.supported_charsets:
        print(f"  - {name}{' (default)' if mode.default_charset and mode.default_charset.name == name else ''}")
    
    print(f"\nOptions: {len(mode.options)}")
    for name, option in mode.options.items():
        print(f"  - {name}: {option.default_value} (values: {list(option.values.keys())})")
    
    print(f"Errors: {len(parser.errors)}")
    for error in parser.errors:
        print(f"  {error}")
    
    print(f"Warnings: {len(mode.warnings)}")
    for warning in mode.warnings:
        print(f"  {warning}")
    
    # Clean up
    import os
    os.remove(test_file)
    
    return len(parser.errors) == 0

def test_real_mode():
    """Test parsing a real mode file."""
    
    parser = ModeParser()
    
    try:
        mode = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem")
        
        print(f"\nReal mode test:")
        print(f"Mode name: {mode.name}")
        print(f"Language: {mode.language}")
        print(f"Writing: {mode.writing}")
        print(f"Human name: {mode.human_name}")
        print(f"Authors: {mode.authors}")
        print(f"Version: {mode.version}")
        
        print(f"\nSupported charsets: {len(mode.supported_charsets)}")
        for name in list(mode.supported_charsets.keys())[:5]:
            print(f"  - {name}")
        if len(mode.supported_charsets) > 5:
            print(f"  ... and {len(mode.supported_charsets) - 5} more")
        
        print(f"\nOptions: {len(mode.options)}")
        for name, option in list(mode.options.items())[:5]:
            print(f"  - {name}: {option.default_value}")
        if len(mode.options) > 5:
            print(f"  ... and {len(mode.options) - 5} more")
        
        print(f"Errors: {len(parser.errors)}")
        if parser.errors:
            print("First few errors:")
            for error in parser.errors[:3]:
                print(f"  {error}")
        
        print(f"Warnings: {len(mode.warnings)}")
        if mode.warnings:
            print("First few warnings:")
            for warning in mode.warnings[:3]:
                print(f"  {warning}")
        
        # Check for rule groups
        if hasattr(mode, 'rule_groups'):
            print(f"\nRule groups: {len(mode.rule_groups)}")
            for name, rg in list(mode.rule_groups.items())[:3]:
                print(f"  - {name}: {len(rg.vars)} vars, {len(rg.root_code_block.terms)} terms")
                if rg.vars:
                    print(f"    Variables: {list(rg.vars.keys())[:10]}")
                    # Show a few variable definitions
                    for var_name in list(rg.vars.keys())[:5]:
                        var_value = rg.vars[var_name].value
                        print(f"      {var_name} === {var_value[:50]}...")
                
                # Finalize and check rules
                rg.finalize({})
                if hasattr(rg, 'rules'):
                    print(f"    Rules: {len(rg.rules)}")
                    for rule in rg.rules[:5]:
                        print(f"      {rule['source']} --> {rule['target']}")
        else:
            print(f"\nNo rule groups found")
        
        # Test transcription if processor exists
        if hasattr(mode, 'processor') and mode.processor:
            mode.processor.finalize({})
            test_result = mode.processor.transcribe("hello")
            print(f"\nTest transcription 'hello': {test_result[:5]}...")
        
        return len(parser.errors) == 0
        
    except Exception as e:
        print(f"Error parsing real mode: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_simple_mode()
    success2 = test_real_mode()
    
    if success1 and success2:
        print("\n✓ All mode parser tests passed!")
    else:
        print("\n✗ Some tests failed!")
