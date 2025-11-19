"""Test transcription of the complete Namárië poem line by line.

This test compares Python transcription output against the canonical JavaScript
outputs using FreeMonoTengwar charset (Unicode PUA). This serves as the ultimate
sanity check for parity between Python and JavaScript implementations.
"""

import pytest
import json
from glaemscribe.parsers.mode_parser import ModeParser


def load_canonical_outputs():
    """Load the canonical Unicode outputs."""
    import os
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'poem_transcription_canonical.json')
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Load the canonical outputs
CANONICAL_OUTPUTS = load_canonical_outputs()


def transcribe_mode(mode_name: str, text: str) -> str:
    """Helper function to transcribe text using a specific mode."""
    from glaemscribe.resources import get_mode_path
    parser = ModeParser()
    mode_file = get_mode_path(mode_name)
    mode = parser.parse(str(mode_file))
    mode.processor.finalize({})
    success, result, debug = mode.transcribe(text)
    return result if success else result


@pytest.mark.parametrize("test_case", CANONICAL_OUTPUTS)
def test_poem_line_transcription(test_case):
    """Test each line of the Namárië poem against canonical output.
    
    This test ensures consistent transcription of the complete Namárië poem.
    Each line is transcribed using the FreeMonoTengwar charset (Unicode PUA)
    and compared against the canonical output.
    """
    # Transcribe using Python
    result = transcribe_mode('quenya-tengwar-classical', test_case['line'])
    
    # Compare with canonical output
    assert result == test_case['output'], (
        f"Transcription mismatch for '{test_case['line']}'\n"
        f"Description: {test_case['description']}\n"
        f"Expected: {test_case['output']}\n"
        f"Got:      {result}\n"
        f"Expected chars: {[f'U+{ord(c):04X}' for c in test_case['output']]}\n"
        f"Got chars:      {[f'U+{ord(c):04X}' for c in result]}"
    )


def test_complete_poem():
    """Test that all poem lines are included in the test."""
    expected_lines = [
        "Ai ! laurië lantar lassi súrinen ,",
        "yéni únótimë ve rámar aldaron !",
        "Yéni ve lintë yuldar avánier",
        "mi oromardi lissë-miruvóreva",
        "Andúnë pella , Vardo tellumar",
        "nu luini yassen tintilar i eleni",
        "ómaryo airetári-lírinen .",
        "Sí man i yulma nin enquantuva ?",
        "Elen síla lúmenn' omentielvo"
    ]  
    actual_lines = [case['line'] for case in CANONICAL_OUTPUTS]
    assert actual_lines == expected_lines, (
        f"Poem lines mismatch. Expected {len(expected_lines)} lines, "
        f"got {len(actual_lines)} lines."
    )


if __name__ == "__main__":
    # Run the tests manually if executed directly
    for test_case in CANONICAL_OUTPUTS:
        result = transcribe_mode('quenya-tengwar-classical', test_case['line'])
        status = "✓" if result == test_case['output'] else "✗"
        print(f"{status} {test_case['description']}")
        if result != test_case['output']:
            print(f"  Expected: {test_case['output']}")
            print(f"  Got:      {result}")
    
    print(f"\nTested {len(CANONICAL_OUTPUTS)} lines")
