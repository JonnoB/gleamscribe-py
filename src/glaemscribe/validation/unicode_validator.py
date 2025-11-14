"""
Unicode character range validation for Glaemscribe transcriptions.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of Unicode validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    character_count: int
    tengwar_count: int
    punctuation_count: int
    
    @classmethod
    def success(cls, character_count: int, tengwar_count: int, punctuation_count: int) -> 'ValidationResult':
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
        return cls(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            character_count=character_count,
            tengwar_count=tengwar_count,
            punctuation_count=punctuation_count
        )


class UnicodeValidator:
    """Validates Unicode character ranges in transcription output."""
    
    def __init__(self):
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
        """Check if character code is in any valid range."""
        for range_name, (start, end) in self.valid_ranges.items():
            if start <= char_code <= end:
                return True
        return char_code in self.allowed_chars
    
    def get_character_type(self, char_code: int) -> str:
        """Categorize character by type."""
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
        """Validate Unicode characters in transcription text."""
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
        """Get a human-readable summary of validation results."""
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
