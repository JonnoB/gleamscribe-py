"""Unicode character range validation for Glaemscribe transcriptions.

This module provides validation for Unicode characters in Tengwar transcriptions,
ensuring that output contains only valid character ranges and identifying
potential issues.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of Unicode validation.
    
    Contains validation status, error/warning messages, and character counts
    from a transcription validation check.
    
    Attributes:
        is_valid: Whether the transcription passed validation
        errors: List of error messages (validation failures)
        warnings: List of warning messages (potential issues)
        character_count: Total number of characters in the text
        tengwar_count: Number of Tengwar characters (PUA range)
        punctuation_count: Number of punctuation marks
        
    Examples:
        >>> result = ValidationResult.success(10, 8, 2)
        >>> print(result.is_valid)
        True
        >>> print(result.tengwar_count)
        8
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    character_count: int
    tengwar_count: int
    punctuation_count: int
    
    @classmethod
    def success(cls, character_count: int, tengwar_count: int, punctuation_count: int) -> 'ValidationResult':
        """Create a successful validation result.
        
        Args:
            character_count: Total number of characters validated
            tengwar_count: Number of Tengwar characters found
            punctuation_count: Number of punctuation marks found
            
        Returns:
            ValidationResult with is_valid=True and no errors
            
        Examples:
            >>> result = ValidationResult.success(10, 8, 2)
            >>> result.is_valid
            True
            >>> len(result.errors)
            0
        """
        return cls(
            is_valid=True,
            errors=[],
            warnings=[],
            character_count=character_count,
            tengwar_count=tengwar_count,
            punctuation_count=punctuation_count
        )
    
    @classmethod
    def failure(cls, errors: List[str], warnings: List[str], 
                character_count: int, tengwar_count: int, punctuation_count: int) -> 'ValidationResult':
        """Create a failed validation result.
        
        Args:
            errors: List of error messages describing validation failures
            warnings: List of warning messages for potential issues
            character_count: Total number of characters validated
            tengwar_count: Number of Tengwar characters found
            punctuation_count: Number of punctuation marks found
            
        Returns:
            ValidationResult with is_valid=False and the provided errors
            
        Examples:
            >>> errors = ["Invalid character at position 0"]
            >>> result = ValidationResult.failure(errors, [], 5, 4, 1)
            >>> result.is_valid
            False
            >>> len(result.errors)
            1
        """
        return cls(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            character_count=character_count,
            tengwar_count=tengwar_count,
            punctuation_count=punctuation_count
        )


class UnicodeValidator:
    """Validates Unicode character ranges in transcription output.
    
    This validator checks that transcribed text contains only valid Unicode
    characters for Tengwar transcriptions, including:
    - Tengwar characters in Private Use Area (U+E000-U+F8FF)
    - Basic Latin punctuation and spaces
    - General punctuation marks
    - Control characters (line breaks, etc.)
    
    The validator identifies invalid characters, counts character types,
    and provides warnings for potential issues.
    
    Examples:
        >>> validator = UnicodeValidator()
        >>> result = validator.validate("\\ue02a\\ue040")
        >>> print(result.is_valid)
        True
        >>> print(result.tengwar_count)
        2
        
        >>> # Invalid character
        >>> result = validator.validate("\\u0001")  # Control character
        >>> print(result.is_valid)
        False
    """
    
    def __init__(self):
        """Initialize the Unicode validator with valid character ranges.
        
        Sets up allowed Unicode ranges for Tengwar transcriptions including
        PUA ranges, basic Latin, and punctuation.
        """
        # Define allowed Unicode ranges
        self.valid_ranges = {
            'tengwar_pua': (0xE000, 0xF8FF),  # Private Use Area for Tengwar
            'tengwar_plane14': (0xE0000, 0xEFFFF),  # Plane 14 Private Use Area
            'basic_latin': (0x0020, 0x007F),   # Basic Latin (space, punctuation)
            'punctuation': (0x2000, 0x206F),   # General Punctuation
            'space': (0x0020, 0x0020),        # Space character
        }
        
        # Specific allowed characters outside ranges
        self.allowed_chars = {
            0x0020,  # Space
            0x000A,  # Line feed
            0x000D,  # Carriage return
            0x2028,  # Line separator
            0x2029,  # Paragraph separator
            0x2E31,  # Word separator (used in some transcriptions)
        }
    
    def is_in_range(self, char_code: int) -> bool:
        """Check if a character code is in any valid Unicode range.
        
        Args:
            char_code: Unicode code point to check
            
        Returns:
            True if the character is in a valid range or allowed list,
            False otherwise
            
        Examples:
            >>> validator = UnicodeValidator()
            >>> validator.is_in_range(0xE02A)  # Tengwar PUA
            True
            >>> validator.is_in_range(0x0020)  # Space
            True
            >>> validator.is_in_range(0x0001)  # Invalid control char
            False
        """
        for range_name, (start, end) in self.valid_ranges.items():
            if start <= char_code <= end:
                return True
        return char_code in self.allowed_chars
    
    def get_character_type(self, char_code: int) -> str:
        """Categorize a character by its type.
        
        Args:
            char_code: Unicode code point to categorize
            
        Returns:
            Character type as string: 'tengwar', 'space', 'punctuation',
            'control', or 'unknown'
            
        Examples:
            >>> validator = UnicodeValidator()
            >>> validator.get_character_type(0xE02A)
            'tengwar'
            >>> validator.get_character_type(0x0020)
            'space'
            >>> validator.get_character_type(0x002C)
            'punctuation'
            >>> validator.get_character_type(0x000A)
            'control'
        """
        if (0xE000 <= char_code <= 0xF8FF) or (0xE0000 <= char_code <= 0xEFFFF):
            return 'tengwar'
        elif char_code == 0x0020:
            return 'space'
        elif 0x0021 <= char_code <= 0x007F or 0x2000 <= char_code <= 0x206F:
            return 'punctuation'
        elif char_code in self.allowed_chars:
            return 'control'
        else:
            return 'unknown'
    
    def validate(self, text: str) -> ValidationResult:
        """Validate Unicode characters in transcription text.
        
        Checks each character in the text to ensure it's in a valid Unicode
        range for Tengwar transcriptions. Counts character types and identifies
        potential issues.
        
        Args:
            text: The transcribed text to validate
            
        Returns:
            ValidationResult containing:
            - is_valid: Whether all characters are valid
            - errors: List of validation errors
            - warnings: List of potential issues
            - character_count: Total characters
            - tengwar_count: Number of Tengwar characters
            - punctuation_count: Number of punctuation marks
            
        Examples:
            >>> validator = UnicodeValidator()
            >>> result = validator.validate("\\ue02a\\ue040\\ue016")
            >>> result.is_valid
            True
            >>> result.tengwar_count
            3
            
            >>> # Empty text
            >>> result = validator.validate("")
            >>> result.is_valid
            True
            >>> result.character_count
            0
            
            >>> # Invalid character
            >>> result = validator.validate("test\\u0001")
            >>> result.is_valid
            False
            >>> len(result.errors) > 0
            True
        """
        errors = []
        warnings = []
        tengwar_count = 0
        punctuation_count = 0
        
        if not text:
            return ValidationResult.success(0, 0, 0)
        
        for i, char in enumerate(text):
            char_code = ord(char)
            char_type = self.get_character_type(char_code)
            
            # Count character types
            if char_type == 'tengwar':
                tengwar_count += 1
            elif char_type == 'punctuation':
                punctuation_count += 1
            
            # Check if character is valid
            if not self.is_in_range(char_code):
                errors.append(
                    f"Invalid character at position {i}: "
                    f"U+{char_code:04X} ({repr(char)}) - {char_type}"
                )
            
            # Check for potential issues
            if char_type == 'unknown' and char_code < 0x10000:
                warnings.append(
                    f"Unusual character at position {i}: "
                    f"U+{char_code:04X} ({repr(char)})"
                )
        
        # Additional structural checks
        if tengwar_count == 0 and len(text.strip()) > 0:
            warnings.append("No Tengwar characters found in output")
        
        # Check for suspicious patterns
        if '?' in text:
            warnings.append("Contains fallback '?' characters - possible missing mappings")
        
        if errors:
            return ValidationResult.failure(
                errors, warnings, len(text), tengwar_count, punctuation_count
            )
        
        return ValidationResult.success(len(text), tengwar_count, punctuation_count)
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """Get a human-readable summary of validation results.
        
        Formats a ValidationResult into a readable text summary with
        character counts, errors, and warnings.
        
        Args:
            result: The ValidationResult to summarize
            
        Returns:
            Formatted string summary with checkmark (✓) for valid results
            or cross (✗) for invalid results
            
        Examples:
            >>> validator = UnicodeValidator()
            >>> result = ValidationResult.success(10, 8, 2)
            >>> summary = validator.get_validation_summary(result)
            >>> "✓ Valid" in summary
            True
            >>> "8" in summary  # Tengwar count
            True
            
            >>> errors = ["Invalid character"]
            >>> result = ValidationResult.failure(errors, [], 5, 4, 1)
            >>> summary = validator.get_validation_summary(result)
            >>> "✗ Invalid" in summary
            True
            >>> "Errors: 1" in summary
            True
        """
        if result.is_valid:
            summary = f"✓ Valid Unicode transcription\n"
            summary += f"  Total characters: {result.character_count}\n"
            summary += f"  Tengwar characters: {result.tengwar_count}\n"
            summary += f"  Punctuation: {result.punctuation_count}"
            
            if result.warnings:
                summary += f"\n  Warnings: {len(result.warnings)}"
                
            return summary
        else:
            summary = f"✗ Invalid Unicode transcription\n"
            summary += f"  Errors: {len(result.errors)}\n"
            summary += f"  Warnings: {len(result.warnings)}\n"
            
            for error in result.errors[:3]:  # Show first 3 errors
                summary += f"  - {error}\n"
            
            if len(result.errors) > 3:
                summary += f"  ... and {len(result.errors) - 3} more errors\n"
                
            return summary
