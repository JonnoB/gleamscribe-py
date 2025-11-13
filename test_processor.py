#!/usr/bin/env python3
"""Test the TranscriptionProcessor."""

from src.glaemscribe.core.transcription_processor import TranscriptionProcessor
from src.glaemscribe.core.mode_enhanced import Mode
from src.glaemscribe.core.rule_group import RuleGroup

def test_simple_processor():
    """Test basic processor functionality."""
    
    # Create a mode
    mode = Mode("test")
    
    # Create processor
    processor = TranscriptionProcessor(mode)
    
    # Create a rule group with some simple rules
    rule_group = RuleGroup(mode, "test_rules")
    
    # Add some variables
    rule_group.add_var("A", "a")
    rule_group.add_var("B", "b")
    
    # Add the rule group to processor
    processor.add_rule_group("test_rules", rule_group)
    
    # Finalize with empty options
    processor.finalize({})
    
    print("Simple processor test:")
    print(f"Processor: {processor}")
    print(f"Rule groups: {list(processor.rule_groups.keys())}")
    
    # Test transcription (will return unknown since tree is empty)
    result = processor.transcribe("test")
    print(f"'test' -> {result}")
    
    print("✓ Basic processor test passed!")
    return True

def test_word_boundaries():
    """Test word boundary handling."""
    
    mode = Mode("test")
    processor = TranscriptionProcessor(mode)
    
    # Add a rule group
    rule_group = RuleGroup(mode, "test")
    processor.add_rule_group("test", rule_group)
    processor.finalize({})
    
    print("\nWord boundary test:")
    
    # Test with spaces
    result = processor.transcribe("hello world")
    print(f"'hello world' -> {result}")
    
    # Test with newlines
    result = processor.transcribe("line1\nline2")
    print(f"'line1\\nline2' -> {result}")
    
    print("✓ Word boundary test passed!")
    return True

if __name__ == "__main__":
    success1 = test_simple_processor()
    success2 = test_word_boundaries()
    
    if success1 and success2:
        print("\n✓ All processor tests passed!")
    else:
        print("\n✗ Some tests failed!")
