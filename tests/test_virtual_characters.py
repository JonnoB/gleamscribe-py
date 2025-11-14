#!/usr/bin/env python3
"""
Tests for virtual character resolution in post-processing.

Virtual characters are context-dependent character substitutions used
in Tengwar transcription to select the appropriate variant of a character
based on surrounding context.
"""

import pytest
from src.glaemscribe.parsers.charset_parser import CharsetParser
from src.glaemscribe.parsers.mode_parser import ModeParser


def test_charset_has_virtual_characters(tengwar_ds_sindarin_charset):
    """Test that charset parser loads virtual character definitions."""
    charset = tengwar_ds_sindarin_charset
    
    # Check that charset was loaded
    assert charset is not None
    assert len(charset.characters) > 0
    
    # Check if virtual characters were parsed
    assert hasattr(charset, 'virtual_chars'), "Charset should have virtual_chars attribute"
    
    # Check that we have some virtual characters
    if hasattr(charset, 'virtual_chars'):
        print(f"Found {len(charset.virtual_chars)} virtual character classes")
        # virtual_chars is a dict, so iterate over items
        for i, (name, vc) in enumerate(list(charset.virtual_chars.items())[:3]):
            print(f"  Virtual char '{name}': {vc}")


def test_mode_loads_virtual_character_operator():
    """Test that mode parser loads the resolve_virtuals operator."""
    parser = ModeParser()
    mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    
    # Check that post-processor exists
    assert mode.post_processor is not None
    
    # Check that post-processor has operators
    assert hasattr(mode.post_processor, 'operators')
    print(f"Post-processor has {len(mode.post_processor.operators)} operators")
    
    # Check that resolve_virtuals operator was loaded
    from src.glaemscribe.core.post_processor.resolve_virtuals import ResolveVirtualsPostProcessorOperator
    has_resolve_virtuals = any(
        isinstance(op, ResolveVirtualsPostProcessorOperator) 
        for op in mode.post_processor.operators
    )
    assert has_resolve_virtuals, "Post-processor should have ResolveVirtualsPostProcessorOperator"
    
    print("✓ resolve_virtuals operator loaded successfully")


def test_virtual_character_resolution_basic(quenya_classical_mode):
    """Test basic virtual character resolution."""
    mode = quenya_classical_mode
    
    # Simple test case - just a vowel that should use virtual character resolution
    text = "a"
    success, result, debug = mode.transcribe(text)
    
    print(f"Input: '{text}'")
    print(f"Output: '{result}'")
    print(f"Output (hex): {result.encode('unicode_escape').decode('ascii')}")
    print(f"Success: {success}")
    
    # We should get some output (not empty)
    assert result != ""
    assert success


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
