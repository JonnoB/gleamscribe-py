"""Tengwar-specific validation for transcription output.

This module provides validation for Tengwar script transcriptions, checking
character properties, sequences, and structural correctness.
"""

from typing import List, Set, Dict, Optional
from .unicode_validator import ValidationResult


class TengwarValidator:
    """Validates Tengwar-specific character properties and combinations.
    
    This validator checks Tengwar transcriptions for:
    - Valid character types (consonants, vowels, punctuation, numbers)
    - Invalid character sequences
    - Structural issues (missing vowels, misplaced carriers)
    - Character categorization and analysis
    
    The validator uses the Unicode Private Use Area (PUA) mapping to identify
    and categorize Tengwar characters (U+E000 to U+F8FF).
    
    Examples:
        >>> validator = TengwarValidator()
        >>> result = validator.validate("\\ue02a\\ue040")  # Tengwar text
        >>> print(result.is_valid)
        True
        
        >>> analysis = validator.get_character_analysis("\\ue02a\\ue040")
        >>> print(analysis['consonants'])
        1
    """
    
    def __init__(self):
        """Initialize the Tengwar validator with character definitions.
        
        Loads Tengwar character mappings and defines character categories
        (consonants, vowels, punctuation, numbers) and invalid sequences.
        """
        # Load Tengwar character definitions from font mapping
        from ..parsers.tengwar_font_mapping import FONT_TO_UNICODE
        
        # Create reverse mapping for validation
        self.unicode_to_font = {v: k for k, v in FONT_TO_UNICODE.items()}
        
        # Define character categories
        self.tengwar_consonants = {
            'TENWA_TINCO', 'TENWA_PARMA', 'TENWA_CALMA', 'TENWA_QUESSE',
            'TENWA_ANDO', 'TENWA_UMBAR', 'TENWA_ANWE', 'TENWA_UNQUE',
            'TENWA_FORMEN', 'TENWA_HANTA', 'TENWA_ANTO', 'TENWA_AMP',
            'TENWA_NUMEN', 'TENWA_MALTA', 'TENWA_NOLDO', 'TENWA_NWALME',
            'TENWA_ORE', 'TENWA_VALA', 'TENWA_YANTA', 'TENGWA_URE',
            # Additional consonants
            'TENGWA_SILE', 'TENGWA_ESSEL', 'TENGWA_AHA', 'TENGWA_HWESTA',
            'TENGWA_RD', 'TENGWA_ARDA', 'TENGWA_LAMB', 'TENGWA_ALDA',
            'TENGWA_DH', 'TENGWA_TH', 'TENGWA_CH', 'TENGWA_SH',
            'TENGWA_ANTHA', 'TENGWA_SST', 'TENGWA_ST', 'TENGWA_NT',
            'TENGWA_MP', 'TENGWA_NQU', 'TENGWA_NGW', 'TENGWA_ANGA',
            'TENGWA_CHAR', 'TENGWA_NCHAR', 'TENGWA_PH', 'TENGWA_BH',
            'TENGWA_TS', 'TENGWA_TSA', 'TENGWA_GH', 'TENGWA_GW',
            'TENGWA_KH', 'TENGWA_KHW', 'TENGWA_PS', 'TENGWA_H',
            'TENGWA_R', 'TENGWA_S', 'TENGWA_Z', 'TENGWA_ZH',
            'TENGWA_X', 'TENGWA_XW', 'TENGWA_Y', 'TENGWA_W',
            'TENGWA_L', 'TENGWA_LD', 'TENGWA_LL', 'TENGWA_LW',
        }
        
        self.tengwar_vowels = {
            'TEHTA_A', 'TEHTA_E', 'TEHTA_I', 'TEHTA_O', 'TEHTA_U',
            'TEHTA_Y', 'TEHTA_EA', 'TEHTA_EO', 'TEHTA_OE', 'TEHTA_AE',
            'TEHTA_AI', 'TEHTA_AU', 'TEHTA_EU', 'TEHTA_IU', 'TEHTA_UI',
            'TEHTA_IA', 'TEHTA_IO', 'TEHTA_IE', 'TEHTA_UE', 'TEHTA_UA',
            # Short/long variants
            'TEHTA_A_SHORT', 'TEHTA_E_SHORT', 'TEHTA_I_SHORT', 'TEHTA_O_SHORT', 'TEHTA_U_SHORT',
            'TEHTA_A_LONG', 'TEHTA_E_LONG', 'TEHTA_I_LONG', 'TEHTA_O_LONG', 'TEHTA_U_LONG',
            # Carrier variants
            'A_TEHTA', 'E_TEHTA', 'I_TEHTA', 'O_TEHTA', 'U_TEHTA',
            'Y_TEHTA', 'EA_TEHTA', 'EO_TEHTA', 'OE_TEHTA', 'AE_TEHTA',
        }
        
        self.tengwar_punctuation = {
            'PUNCT_COMMA', 'PUNCT_PERIOD', 'PUNCT_COLON', 'PUNCT_SEMICOLON',
            'PUNCT_EXCLAM', 'PUNCT_QUESTION', 'PUNCT_QUOTE_SINGLE', 'PUNCT_QUOTE_DOUBLE',
            'PUNCT_PAREN_OPEN', 'PUNCT_PAREN_CLOSE', 'PUNCT_BRACKET_OPEN', 'PUNCT_BRACKET_CLOSE',
            'CARRIAGE_RETURN', 'DOUBLE_PUNCT', 'PUNCT_SPACE', 'WORD_BREAK',
        }
        
        self.tengwar_numbers = {
            'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE',
            'TEN', 'ELEVEN', 'TWELVE', 'DECIMAL', 'NUMBER_BREAK',
        }
        
        # Define invalid combinations
        self.invalid_sequences = [
            # Multiple vowel carriers in sequence (usually invalid)
            ('A_TEHTA', 'E_TEHTA'),
            ('E_TEHTA', 'I_TEHTA'),
            ('I_TEHTA', 'O_TEHTA'),
            ('O_TEHTA', 'U_TEHTA'),
        ]
    
    def get_tengwar_type(self, font_name: str) -> str:
        """Categorize a Tengwar character by its type.
        
        Args:
            font_name: The font name of the Tengwar character (e.g., 'TENWA_TINCO')
            
        Returns:
            Character type as a string: 'consonant', 'vowel', 'punctuation',
            'number', or 'unknown'
            
        Examples:
            >>> validator = TengwarValidator()
            >>> validator.get_tengwar_type('TENWA_TINCO')
            'consonant'
            >>> validator.get_tengwar_type('TEHTA_A')
            'vowel'
            >>> validator.get_tengwar_type('PUNCT_COMMA')
            'punctuation'
        """
        if font_name in self.tengwar_consonants:
            return 'consonant'
        elif font_name in self.tengwar_vowels:
            return 'vowel'
        elif font_name in self.tengwar_punctuation:
            return 'punctuation'
        elif font_name in self.tengwar_numbers:
            return 'number'
        else:
            return 'unknown'
    
    def validate_character_sequence(self, font_sequence: List[str]) -> List[str]:
        """Validate a sequence of Tengwar characters for invalid combinations.
        
        Checks for known invalid character sequences, such as multiple vowel
        carriers in a row.
        
        Args:
            font_sequence: List of Tengwar font names in order
            
        Returns:
            List of error messages describing invalid sequences found.
            Empty list if no errors.
            
        Examples:
            >>> validator = TengwarValidator()
            >>> errors = validator.validate_character_sequence(['A_TEHTA', 'E_TEHTA'])
            >>> len(errors) > 0  # This is an invalid sequence
            True
            
            >>> errors = validator.validate_character_sequence(['TENWA_TINCO', 'A_TEHTA'])
            >>> len(errors)  # This is valid
            0
        """
        errors = []
        
        for i in range(len(font_sequence) - 1):
            current = font_sequence[i]
            next_char = font_sequence[i + 1]
            
            # Check for invalid sequences
            if (current, next_char) in self.invalid_sequences:
                errors.append(
                    f"Invalid sequence at positions {i}-{i+1}: {current} followed by {next_char}"
                )
        
        return errors
    
    def validate(self, text: str) -> ValidationResult:
        """Validate Tengwar-specific properties in transcription text.
        
        Performs comprehensive validation including:
        - Basic Unicode validation (via UnicodeValidator)
        - Character sequence validation
        - Structural checks (consonants without vowels, misplaced carriers)
        - Character identification and categorization
        
        Args:
            text: The transcribed Tengwar text to validate (Unicode PUA characters)
            
        Returns:
            ValidationResult object containing:
            - is_valid: Whether the text passes all validation checks
            - errors: List of error messages (if any)
            - warnings: List of warning messages (if any)
            - character_count: Total character count
            - tengwar_count: Number of Tengwar characters
            - punctuation_count: Number of punctuation marks
            
        Examples:
            >>> validator = TengwarValidator()
            >>> result = validator.validate("\\ue02a\\ue040\\ue016")
            >>> print(result.is_valid)
            True
            >>> print(result.tengwar_count)
            3
            
            >>> # Invalid sequence
            >>> result = validator.validate("\\ue040\\ue041")  # Two carriers in a row
            >>> print(result.is_valid)
            False
            >>> len(result.errors) > 0
            True
        """
        from .unicode_validator import UnicodeValidator
        
        # First do basic Unicode validation
        unicode_validator = UnicodeValidator()
        unicode_result = unicode_validator.validate(text)
        
        if not unicode_result.is_valid:
            return unicode_result
        
        # Tengwar-specific validation
        errors = []
        warnings = []
        tengwar_chars = []
        
        # Extract Tengwar characters and their font names
        for char in text:
            char_code = ord(char)
            if 0xE000 <= char_code <= 0xF8FF:  # Private Use Area
                if char_code in self.unicode_to_font:
                    font_name = self.unicode_to_font[char_code]
                    tengwar_chars.append((char, font_name))
                else:
                    warnings.append(f"Unknown Tengwar character: U+{char_code:04X}")
        
        # Validate character sequence
        font_sequence = [font_name for _, font_name in tengwar_chars]
        sequence_errors = self.validate_character_sequence(font_sequence)
        errors.extend(sequence_errors)
        
        # Check for structural issues
        if tengwar_chars:
            # Check if we have consonants without vowel support where expected
            consonant_count = sum(1 for _, font_name in tengwar_chars 
                                if self.get_tengwar_type(font_name) == 'consonant')
            vowel_count = sum(1 for _, font_name in tengwar_chars 
                            if self.get_tengwar_type(font_name) == 'vowel')
            
            if consonant_count > 0 and vowel_count == 0:
                warnings.append("Transcription has consonants but no vowel marks")
            
            # Check for isolated carriers
            for i, (char, font_name) in enumerate(tengwar_chars):
                if font_name.endswith('_TEHTA') and font_name != 'TEHTA_A':
                    # Check if carrier is properly positioned
                    if i > 0:
                        prev_type = self.get_tengwar_type(tengwar_chars[i-1][1])
                        if prev_type not in ['consonant', 'unknown']:
                            warnings.append(f"Vowel carrier {font_name} may be incorrectly positioned")
        
        if errors:
            return ValidationResult.failure(
                errors, warnings, len(text), unicode_result.tengwar_count, unicode_result.punctuation_count
            )
        
        return ValidationResult.success(len(text), unicode_result.tengwar_count, unicode_result.punctuation_count)
    
    def get_character_analysis(self, text: str) -> Dict[str, int]:
        """Analyze and count character types in a Tengwar transcription.
        
        Categorizes each character in the text and returns counts for each type.
        Useful for understanding the composition of a transcription.
        
        Args:
            text: The transcribed Tengwar text to analyze
            
        Returns:
            Dictionary with character type counts:
            - 'consonants': Number of consonant characters
            - 'vowels': Number of vowel marks/carriers
            - 'punctuation': Number of punctuation marks
            - 'numbers': Number of numeric characters
            - 'unknown': Number of unknown PUA characters
            - 'non_tengwar': Number of non-Tengwar characters
            
        Examples:
            >>> validator = TengwarValidator()
            >>> analysis = validator.get_character_analysis("\\ue02a\\ue040\\ue016")
            >>> print(analysis['consonants'])
            2
            >>> print(analysis['vowels'])
            1
            
            >>> # Mixed content
            >>> analysis = validator.get_character_analysis("\\ue02a test")
            >>> print(analysis['consonants'])
            1
            >>> print(analysis['non_tengwar'])
            5
        """
        analysis = {
            'consonants': 0,
            'vowels': 0,
            'punctuation': 0,
            'numbers': 0,
            'unknown': 0,
            'non_tengwar': 0
        }
        
        for char in text:
            char_code = ord(char)
            if 0xE000 <= char_code <= 0xF8FF:  # Private Use Area
                if char_code in self.unicode_to_font:
                    font_name = self.unicode_to_font[char_code]
                    char_type = self.get_tengwar_type(font_name)
                    analysis[char_type] += 1
                else:
                    analysis['unknown'] += 1
            else:
                analysis['non_tengwar'] += 1
        
        return analysis
