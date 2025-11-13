#!/usr/bin/env python3
"""Test the TranscriptionTreeNode."""

from src.glaemscribe.core.transcription_tree_node import TranscriptionTreeNode

def test_simple_tree():
    """Test basic tree functionality."""
    
    # Create root node
    root = TranscriptionTreeNode()
    
    # Add some patterns
    root.add_subpath("a", ["CHAR_A"])
    root.add_subpath("b", ["CHAR_B"])
    root.add_subpath("th", ["CHAR_TH"])
    root.add_subpath("the", ["CHAR_THE"])
    
    print("Simple tree test:")
    print(f"Root has {len(root.siblings)} siblings")
    
    # Test transcription
    result, consumed = root.transcribe("a")
    print(f"'a' -> {result}, consumed {consumed}")
    assert result == ["CHAR_A"]
    assert consumed == 1
    
    result, consumed = root.transcribe("b")
    print(f"'b' -> {result}, consumed {consumed}")
    assert result == ["CHAR_B"]
    assert consumed == 1
    
    result, consumed = root.transcribe("th")
    print(f"'th' -> {result}, consumed {consumed}")
    assert result == ["CHAR_TH"]
    assert consumed == 2
    
    result, consumed = root.transcribe("the")
    print(f"'the' -> {result}, consumed {consumed}")
    assert result == ["CHAR_THE"]
    assert consumed == 3
    
    # Test longest match (should match "the" not "th")
    result, consumed = root.transcribe("them")
    print(f"'them' -> {result}, consumed {consumed}")
    assert result == ["CHAR_THE"]
    assert consumed == 3
    
    print("✓ All tree tests passed!")
    return True

if __name__ == "__main__":
    test_simple_tree()
