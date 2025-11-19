#!/usr/bin/env python3
"""Command-line helper for auditing Glaemscribe Unicode output.

The script can validate raw Tengwar strings or first transcribe plain text via a
specified .glaem mode. It prints Unicode and Tengwar-specific diagnostics,
including errors, warnings, and character breakdowns, making it handy for
spot-checking inputs outside the automated test suite.

Usage:
    python validate_unicode.py "text to validate"
    python validate_unicode.py --mode quenya-tengwar-classical "Elen síla lúmenn"
"""

import sys
import argparse
from glaemscribe.validation import UnicodeValidator, TengwarValidator
from glaemscribe.parsers.mode_parser import ModeParser


def validate_text(text: str, mode_name: str = None) -> bool:
    """Validate Unicode and Tengwar rules for a given transcription.

    Args:
        text: The Unicode string to inspect (plain Tengwar or transliteration).
        mode_name: Optional .glaem mode identifier for logging context when the
            text came from a specific transcription workflow.

    Returns:
        bool: ``True`` when both the general Unicode and Tengwar-specific
        validators find no blocking errors, otherwise ``False``.

    Example:
        >>> validate_text("Elen síla lúmenn' omentielvo")
        Validating text: "Elen síla lúmenn' omentielvo"
        ...

    The function prints a human-readable breakdown of Unicode errors/warnings,
    Tengwar-specific issues, and a character-type histogram so you can quickly
    audit ad-hoc strings outside the automated test suite.
    """
    unicode_validator = UnicodeValidator()
    tengwar_validator = TengwarValidator()
    
    print(f"Validating text: {repr(text)}")
    print("=" * 50)
    
    # Basic Unicode validation
    unicode_result = unicode_validator.validate(text)
    print(unicode_validator.get_validation_summary(unicode_result))
    
    if unicode_result.errors:
        print("\nErrors:")
        for error in unicode_result.errors:
            print(f"  - {error}")
    
    if unicode_result.warnings:
        print("\nWarnings:")
        for warning in unicode_result.warnings:
            print(f"  - {warning}")
    
    # Tengwar-specific validation
    print("\n" + "=" * 50)
    print("Tengwar-specific validation:")
    
    tengwar_result = tengwar_validator.validate(text)
    if tengwar_result.is_valid:
        print("✓ Tengwar validation passed")
    else:
        print("✗ Tengwar validation failed")
        for error in tengwar_result.errors:
            print(f"  - {error}")
    
    if tengwar_result.warnings:
        print("\nTengwar warnings:")
        for warning in tengwar_result.warnings:
            print(f"  - {warning}")
    
    # Character analysis
    analysis = tengwar_validator.get_character_analysis(text)
    print(f"\nCharacter analysis:")
    for char_type, count in analysis.items():
        if count > 0:
            print(f"  {char_type}: {count}")
    
    return unicode_result.is_valid and tengwar_result.is_valid


def transcribe_and_validate(text: str, mode_name: str) -> bool:
    """Transcribe text using specified mode and validate result."""
    print(f"Transcribing with mode: {mode_name}")
    print("=" * 50)
    
    try:
        # Load mode
        from glaemscribe.resources import get_mode_path
        parser = ModeParser()
        mode = parser.parse(str(get_mode_path(mode_name)))
        mode.processor.finalize({})
        
        # Transcribe
        success, result, debug = mode.transcribe(text)
        
        if not success:
            print(f"✗ Transcription failed")
            return False
        
        print(f"Original: {text}")
        print(f"Result:   {result}")
        print("=" * 50)
        
        # Validate result
        return validate_text(result, mode_name)
        
    except Exception as e:
        print(f"✗ Error loading mode or transcribing: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate Unicode transcriptions for Glaemscribe"
    )
    parser.add_argument(
        "text", 
        help="Text to validate (or transcribe and validate if --mode is specified)"
    )
    parser.add_argument(
        "--mode", 
        help="Mode name to transcribe text before validation"
    )
    parser.add_argument(
        "--list-modes", 
        action="store_true",
        help="List available transcription modes"
    )
    
    args = parser.parse_args()
    
    if args.list_modes:
        print("Available modes:")
        # List built-in modes
        modes = [
            "quenya-tengwar-classical",
            "sindarin-tengwar-general_use",
            "sindarin-tengwar-beleriand",
            "english-tengwar-espeak",
            "raw-tengwar"
        ]
        for mode in modes:
            print(f"  - {mode}")
        return
    
    if args.mode:
        success = transcribe_and_validate(args.text, args.mode)
    else:
        success = validate_text(args.text)
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Overall validation: PASSED")
        sys.exit(0)
    else:
        print("✗ Overall validation: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
