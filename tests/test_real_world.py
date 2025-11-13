#!/usr/bin/env python3
"""
Real-world transcription tests comparing Python implementation
against known good outputs from Ruby Glaemscribe.

These tests use actual Unicode Tengwar characters that may appear
as 'tofu' (boxes) on systems without appropriate fonts, but
they validate the complete transcription pipeline.
"""

import pytest
from src.glaemscribe.parsers.mode_parser import ModeParser


REAL_WORLD_TEST_CASES = [
    {
        'mode': 'quenya-tengwar-classical',
        'input': 'Ai ! laurië lantar lassi súrinen ,',
        'expected': '      ⸱',
        'description': 'Quenya phrase from Ruby implementation'
    },
    # TODO: Add more examples as we discover them
]


def transcribe_mode(mode_name: str, text: str) -> str:
    """Helper function to transcribe text using a specific mode."""
    parser = ModeParser()
    mode_file = f"resources/glaemresources/modes/{mode_name}.glaem"
    mode = parser.parse(mode_file)
    
    # Finalize and transcribe
    mode.processor.finalize({})
    result = mode.processor.transcribe(text)
    
    # Return as string (transcribe returns list of tokens)
    return "".join(result)


@pytest.mark.real_world
@pytest.mark.parametrize("test_case", REAL_WORLD_TEST_CASES)
def test_real_world_transcription(test_case):
    """Test real-world transcription examples against Ruby outputs."""
    # Skip if mode file doesn't exist yet
    mode_file = f"resources/glaemresources/modes/{test_case['mode']}.glaem"
    try:
        result = transcribe_mode(test_case['mode'], test_case['input'])
    except FileNotFoundError:
        pytest.skip(f"Mode file {mode_file} not available")
    
    # Compare with expected Ruby output
    assert result == test_case['expected'], (
        f"Transcription mismatch for '{test_case['input']}'\n"
        f"Expected: {test_case['expected']}\n"
        f"Got:      {result}"
    )


@pytest.mark.real_world
def test_tengwar_unicode_ranges():
    """Verify that our output contains valid Tengwar Unicode characters."""
    # Test with a simple case first
    test_case = REAL_WORLD_TEST_CASES[0]
    
    try:
        result = transcribe_mode(test_case['mode'], test_case['input'])
    except FileNotFoundError:
        pytest.skip("Mode file not available")
    
    # Check for characters in the Private Use Area where Tengwar lives
    tengwar_chars = [char for char in result if 0xE000 <= ord(char) <= 0xF8FF]
    assert len(tengwar_chars) > 0, "No Tengwar Unicode characters found in output"
    
    # Verify we get the same number of Tengwar chars as expected
    expected_tengwar = [char for char in test_case['expected'] if 0xE000 <= ord(char) <= 0xF8FF]
    assert len(tengwar_chars) == len(expected_tengwar), (
        f"Tengwar character count mismatch: {len(tengwar_chars)} vs {len(expected_tengwar)}"
    )


if __name__ == "__main__":
    # Quick manual test
    for case in REAL_WORLD_TEST_CASES:
        try:
            result = transcribe_mode(case['mode'], case['input'])
            print(f"Input: {case['input']}")
            print(f"Expected: {case['expected']}")
            print(f"Got:      {result}")
            print(f"Match: {result == case['expected']}")
            print()
        except Exception as e:
            print(f"Error with {case['input']}: {e}")
