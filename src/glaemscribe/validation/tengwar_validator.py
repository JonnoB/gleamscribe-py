"""
Tengwar-specific validation for transcription output.
"""

from typing import List, Set, Dict, Optional
from .unicode_validator import ValidationResult


class TengwarValidator:
    """Validates Tengwar-specific character properties and combinations."""
    
    def __init__(self):
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
        """Categorize Tengwar character by type."""
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
        """Validate sequence of Tengwar characters."""
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
        """Validate Tengwar-specific properties in transcription text."""
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
        """Analyze character types in transcription."""
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
