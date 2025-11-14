"""
Transcription validation functionality tests.

Consolidated from:
- test_unicode_validation.py (Unicode and Tengwar validation)
- test_unicode_variables.py (Unicode variable testing)

This reduces duplicate mode loading and provides better test organization.
"""

import pytest
from src.glaemscribe.validation.unicode_validator import UnicodeValidator
from src.glaemscribe.validation.tengwar_validator import TengwarValidator


# Use fixtures from conftest.py - no need to redefine them here
# Individual mode fixtures are already defined there


class TestUnicodeValidator:
    """Test basic Unicode character validation."""
    
    def test_valid_tengwar_characters(self, unicode_validator):
        """Test validation of valid Tengwar Unicode characters."""
        # Sample valid Tengwar characters from Private Use Area
        valid_text = "\ue02a\uec42\ue065\ue023"  # Various Tengwar characters
        
        result = unicode_validator.validate(valid_text)
        
        assert result.is_valid
        assert result.error_count == 0
        assert result.character_count == 4
    
    def test_mixed_valid_text(self, unicode_validator):
        """Test validation of text with Tengwar and basic characters."""
        mixed_text = "\ue02a\uec42 hello \ue065\ue023"
        
        result = unicode_validator.validate(mixed_text)
        
        assert result.is_valid
        assert result.error_count == 0
        assert result.character_count == 13  # 4 Tengwar + 1 space + 5 letters + 1 space + 2 Tengwar
    
    def test_invalid_characters(self, unicode_validator):
        """Test validation detects invalid Unicode characters."""
        # Include some invalid characters outside expected ranges
        invalid_text = "\ue02a\u0041\uec42"  # Tengwar + 'A' + Tengwar
        
        result = unicode_validator.validate(invalid_text)
        
        # 'A' should be flagged as invalid (not in Tengwar ranges)
        assert not result.is_valid
        assert result.error_count > 0
        assert "U+0041" in str(result.errors)
    
    def test_extended_tengwar_range(self, unicode_validator):
        """Test validation of extended Tengwar Unicode range (Plane 14)."""
        # Test Plane 14 Private Use Area characters
        extended_text = "\U000e1042\U000e1021"  # Extended Tengwar characters
        
        result = unicode_validator.validate(extended_text)
        
        assert result.is_valid
        assert result.error_count == 0
        assert result.character_count == 2
    
    def test_empty_text(self, unicode_validator):
        """Test validation of empty text."""
        result = unicode_validator.validate("")
        
        assert result.is_valid
        assert result.error_count == 0
        assert result.character_count == 0
    
    def test_validation_summary(self, unicode_validator):
        """Test validation summary generation."""
        text = "\ue02a\uec42\ue065"
        result = unicode_validator.validate(text)
        
        summary = unicode_validator.get_validation_summary(result)
        
        assert "Valid Unicode transcription" in summary
        assert "Total characters: 3" in summary
    
    def test_character_type_detection(self, unicode_validator):
        """Test character type detection."""
        # Test different character types
        assert unicode_validator.get_character_type(0xE02A) == 'tengwar'
        assert unicode_validator.get_character_type(0xE1042) == 'tengwar'  # Plane 14
        assert unicode_validator.get_character_type(0x0020) == 'space'
        assert unicode_validator.get_character_type(0x0041) == 'punctuation'  # Basic Latin
        assert unicode_validator.get_character_type(0x12345) == 'unknown'


class TestTengwarValidator:
    """Test Tengwar-specific validation functionality."""
    
    def test_valid_quenya_transcription(self, quenya_classical_mode, tengwar_validator):
        """Test validation of actual Quenya transcription."""
        mode = quenya_classical_mode
        
        success, result, _ = mode.transcribe("aiya")
        
        validation_result = tengwar_validator.validate(result)
        
        assert validation_result.is_valid
        assert validation_result.tengwar_count > 0
    
    def test_valid_sindarin_transcription(self, sindarin_general_mode, tengwar_validator):
        """Test validation of actual Sindarin transcription."""
        mode = sindarin_general_mode
        
        success, result, _ = mode.transcribe("mellon")
        
        validation_result = tengwar_validator.validate(result)
        
        assert validation_result.is_valid
        assert validation_result.tengwar_count > 0
    
    def test_character_analysis(self, tengwar_validator):
        """Test character type analysis."""
        # Sample text with mixed character types
        text = "\ue02a\uec42 \ue065 \ue023\ue02a"  # consonants, punctuation, etc.
        
        analysis = tengwar_validator.get_character_analysis(text)
        
        assert 'consonants' in analysis
        assert 'vowels' in analysis
        assert 'punctuation' in analysis
        assert sum(analysis.values()) == len(text)
    
    def test_unknown_tengwar_characters(self, tengwar_validator):
        """Test handling of unknown Tengwar characters."""
        # Create text with Private Use Area character not in mapping
        unknown_char = "\ue800"  # Random PUA character
        text = f"\ue02a{unknown_char}\uec42"
        
        validation_result = tengwar_validator.validate(text)
        
        # Should detect unknown character
        assert not validation_result.is_valid
        assert validation_result.error_count > 0
    
    def test_fallback_characters(self, tengwar_validator):
        """Test detection of fallback characters."""
        # Text with fallback character
        text_with_fallback = "\ue02a?\uec42"
        
        validation_result = tengwar_validator.validate(text_with_fallback)
        
        # Should detect fallback character as warning
        assert len(validation_result.warnings) > 0
        assert any("fallback" in str(warning).lower() for warning in validation_result.warnings)
    
    def test_tengwar_character_properties(self, tengwar_validator):
        """Test Tengwar character property analysis."""
        # Test known Tengwar characters
        test_chars = [
            ("\ue02a", "TELCO"),      # Known consonant
            ("\ue900", "A_TEHTA_CIRCUM"),  # Known vowel
            ("\ue020", "E_TEHTA"),    # Known vowel
        ]
        
        for char_code, expected_name in test_chars:
            properties = tengwar_validator.get_character_properties(char_code)
            
            assert properties is not None
            # Properties should include basic information about the character
    
    def test_tengwar_sequence_validation(self, tengwar_validator):
        """Test validation of Tengwar character sequences."""
        # Valid sequences
        valid_sequences = [
            "\ue02a\ue900",      # Consonant + vowel
            "\ue02a\uec42\ue020", # Consonant + consonant + vowel
        ]
        
        for sequence in valid_sequences:
            result = tengwar_validator.validate(sequence)
            assert result.is_valid, f"Sequence should be valid: {sequence.encode('unicode_escape')}"
    
    def test_validation_with_spaces(self, tengwar_validator):
        """Test validation handles spaces correctly."""
        text_with_spaces = "\ue02a\ue900 \uec42\ue020 \ue065"
        
        result = tengwar_validator.validate(text_with_spaces)
        
        assert result.is_valid
        assert result.space_count == 2  # Two spaces in the text


class TestIntegratedValidation:
    """Test integrated validation with actual transcription."""
    
    def test_quenya_transcription_validation(self, quenya_classical_mode, unicode_validator, tengwar_validator):
        """Test complete validation pipeline for Quenya transcription."""
        mode = quenya_classical_mode
        
        # Transcribe a sample text
        success, result, _ = mode.transcribe("Elen síla lúmenn omentielvo")
        
        assert success
        
        # Unicode validation
        unicode_result = unicode_validator.validate(result)
        assert unicode_result.is_valid
        
        # Tengwar validation
        tengwar_result = tengwar_validator.validate(result)
        assert tengwar_result.is_valid
        
        # Combined validation
        combined_errors = unicode_result.errors + tengwar_result.errors
        combined_warnings = unicode_result.warnings + tengwar_result.warnings
        
        assert len(combined_errors) == 0, f"Combined validation should have no errors: {combined_errors}"
    
    def test_sindarin_transcription_validation(self, sindarin_general_mode, unicode_validator, tengwar_validator):
        """Test complete validation pipeline for Sindarin transcription."""
        mode = sindarin_general_mode
        
        # Transcribe a sample text
        success, result, _ = mode.transcribe("A Elbereth Gilthoniel")
        
        assert success
        
        # Unicode validation
        unicode_result = unicode_validator.validate(result)
        assert unicode_result.is_valid
        
        # Tengwar validation
        tengwar_result = tengwar_validator.validate(result)
        assert tengwar_result.is_valid
    
    def test_validation_performance(self, quenya_classical_mode, unicode_validator, tengwar_validator):
        """Test validation performance with larger texts."""
        mode = quenya_classical_mode
        
        # Generate a longer text
        base_text = "aiya elenion"
        long_text = base_text * 10  # Repeat 10 times
        
        success, result, _ = mode.transcribe(long_text)
        assert success
        
        # Time the validation
        import time
        start_time = time.time()
        
        unicode_result = unicode_validator.validate(result)
        tengwar_result = tengwar_validator.validate(result)
        
        validation_time = time.time() - start_time
        
        # Validation should be fast (less than 1 second for this text)
        assert validation_time < 1.0, f"Validation took too long: {validation_time:.2f}s"
        assert unicode_result.is_valid
        assert tengwar_result.is_valid


class TestUnicodeVariables:
    """Test Unicode variable functionality in modes."""
    
    def test_unicode_variables_in_quenya_mode(self, quenya_classical_mode):
        """Test Unicode variables are available in Quenya mode."""
        mode = quenya_classical_mode
        
        # Check that Unicode variables are defined
        rule_group = list(mode.processor.rule_groups.values())[0]
        
        # Common Unicode variables
        unicode_vars = ["NBSP", "WJ", "ZWSP", "UNDERSCORE"]
        
        for var_name in unicode_vars:
            if var_name in rule_group.vars:
                var_value = rule_group.vars[var_name].value
                assert var_value.startswith("{UNI_"), f"{var_name} should be Unicode variable"
    
    def test_unicode_variables_in_sindarin_mode(self, sindarin_general_mode):
        """Test Unicode variables are available in Sindarin mode."""
        mode = sindarin_general_mode
        
        # Check that Unicode variables are defined
        rule_group = list(mode.processor.rule_groups.values())[0]
        
        # Common Unicode variables
        unicode_vars = ["NBSP", "WJ", "ZWSP", "UNDERSCORE"]
        
        for var_name in unicode_vars:
            if var_name in rule_group.vars:
                var_value = rule_group.vars[var_name].value
                assert var_value.startswith("{UNI_"), f"{var_name} should be Unicode variable"
    
    def test_unicode_variable_values(self, quenya_classical_mode):
        """Test that Unicode variables have correct values."""
        mode = quenya_classical_mode
        
        rule_group = list(mode.processor.rule_groups.values())[0]
        
        # Check specific Unicode variable values
        expected_vars = {
            "NBSP": "{UNI_00A0}",      # Non-breaking space
            "WJ": "{UNI_2060}",        # Word joiner
            "ZWSP": "{UNI_200B}",      # Zero-width space
            "UNDERSCORE": "{UNI_005F}", # Underscore
        }
        
        for var_name, expected_value in expected_vars.items():
            if var_name in rule_group.vars:
                actual_value = rule_group.vars[var_name].value
                assert actual_value == expected_value, f"{var_name} should be {expected_value}, got {actual_value}"
