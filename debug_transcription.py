#!/usr/bin/env python3

"""Debug script to analyze transcription output vs expected output."""

from glaemscribe.parsers.mode_parser import ModeParser

def analyze_transcription():
    """Analyze the transcription step by step."""
    
    # Load mode
    parser = ModeParser()
    mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    mode.processor.finalize({})
    
    # Test input
    text = "Ai ! laurië lantar lassi súrinen ,"
    
    print(f"Input text: {text}")
    print(f"Mode: {mode.name}")
    print(f"Default charset: {mode.default_charset.name}")
    print(f"Charset size: {len(mode.default_charset.characters)}")
    print()
    
    # Transcribe
    success, result, debug = mode.transcribe(text)
    
    print(f"Transcription successful: {success}")
    print(f"Output: {result}")
    print()
    
    # Expected output from test
    expected = '\ue02a\uec42 \ue065 \ue900\ue02b\uec41\ue020\uec62\ue010\uec53\ue010 ⸱'
    print(f"Expected: {expected}")
    print()
    
    # Character-by-character analysis
    print("Character analysis:")
    print("Index | Actual | Expected | Actual Unicode | Expected Unicode")
    print("-" * 70)
    
    for i, (actual, expected_char) in enumerate(zip(result, expected)):
        actual_code = ord(actual) if i < len(result) else "N/A"
        expected_code = ord(expected_char) if i < len(expected) else "N/A"
        
        actual_str = str(actual_code) if actual_code != "N/A" else "N/A"
        expected_str = str(expected_code) if expected_code != "N/A" else "N/A"
        print(f"{i:5d} | {actual:7s} | {expected_char:9s} | {actual_str:14s} | {expected_str:15s}")
    
    # Check length differences
    if len(result) != len(expected):
        print(f"\nLength mismatch: actual={len(result)}, expected={len(expected)}")
        if len(result) > len(expected):
            print(f"Extra characters in actual: {result[len(expected):]}")
        else:
            print(f"Missing characters in actual: {expected[len(result):]}")
    
    # Check some specific characters in charset
    print(f"\nCharset character checks:")
    test_chars = ["TELCO", "PARMA", "CALMA", "NUM_1", "PUNCT_EXCLAM"]
    for char_name in test_chars:
        if char_name in mode.default_charset.characters:
            char_value = mode.default_charset.characters[char_name]
            print(f"{char_name}: '{char_value}' (U+{ord(char_value):04X})")
        else:
            print(f"{char_name}: NOT FOUND")

if __name__ == "__main__":
    analyze_transcription()
