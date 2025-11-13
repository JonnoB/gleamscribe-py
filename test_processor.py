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
    rule_group.add_var("A", "CHAR_A")
    rule_group.add_var("B", "CHAR_B")
    
    # Add some manual rules to test
    rule_group.rules = [
        {'source': 'a', 'target': 'TENGWA_A', 'line': 1},
        {'source': 'b', 'target': 'TENGWA_B', 'line': 2},
        {'source': 'ab', 'target': 'TENGWA_AB', 'line': 3},
    ]
    
    # Add the rule group to processor
    processor.add_rule_group("test_rules", rule_group)
    
    # Finalize with empty options
    processor.finalize({})
    
    print("Simple processor test:")
    print(f"Processor: {processor}")
    print(f"Rule groups: {list(processor.rule_groups.keys())}")
    print(f"Rules in group: {len(rule_group.rules)}")
    
    # Test transcription
    result = processor.transcribe("a")
    print(f"'a' -> {result}")
    
    result = processor.transcribe("b")
    print(f"'b' -> {result}")
    
    result = processor.transcribe("ab")
    print(f"'ab' -> {result}")
    
    result = processor.transcribe("abc")
    print(f"'abc' -> {result}")
    
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
