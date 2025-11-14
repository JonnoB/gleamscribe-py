"""
Test Unicode validation for Glaemscribe transcriptions.
"""

import pytest
from src.glaemscribe.validation import UnicodeValidator, TengwarValidator
from src.glaemscribe.parsers.mode_parser import ModeParser


class TestUnicodeValidator:
    """Test basic Unicode character validation."""
    
    def setup_method(self):
        self.validator = UnicodeValidator()
    
    def test_valid_tengwar_text(self):
        """Test validation of valid Tengwar transcription."""
        # Sample Tengwar text (Unicode PUA characters)
        text = "\ue02a\uec42\ue02a\ue020 \ue065 \ue023\ue02a\ue02a\ue020\ue02a\ue900"
        result = self.validator.validate(text)
        
        assert result.is_valid
        assert result.tengwar_count > 0
        assert len(result.errors) == 0
    
    def test_empty_text(self):
        """Test validation of empty text."""
        result = self.validator.validate("")
        
        assert result.is_valid
        assert result.character_count == 0
        assert result.tengwar_count == 0
    
    def test_invalid_unicode_characters(self):
        """Test validation fails with invalid Unicode characters."""
        # Include some invalid characters outside allowed ranges
        text = "Hello \ue02a\ud83d\ude00 World"  # Contains emoji
        result = self.validator.validate(text)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Invalid character" in result.errors[0]
    
    def test_fallback_characters(self):
        """Test validation warns about fallback characters."""
        text = "\ue02a?\ue02a"  # Contains fallback '?'
        result = self.validator.validate(text)
        
        assert result.is_valid  # Still valid, but with warnings
        assert len(result.warnings) > 0
        assert any("fallback" in warning for warning in result.warnings)
    
    def test_character_counting(self):
        """Test accurate character counting."""
        text = "A \ue02a B \uec42 C \ue900"
        result = self.validator.validate(text)
        
        assert result.character_count == len(text)
        assert result.tengwar_count == 3
        assert result.punctuation_count >= 0  # May include spaces


class TestTengwarValidator:
    """Test Tengwar-specific validation."""
    
    def setup_method(self):
        self.tengwar_validator = TengwarValidator()
        self.mode_parser = ModeParser()
    
    def test_valid_quenya_transcription(self):
        """Test validation of actual Quenya transcription."""
        # Load mode and transcribe
        mode = self.mode_parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
        mode.processor.finalize({})
        
        success, result, _ = mode.transcribe("aiya")
        
        validation_result = self.tengwar_validator.validate(result)
        
        assert validation_result.is_valid
        assert validation_result.tengwar_count > 0
    
    def test_character_analysis(self):
        """Test character type analysis."""
        # Sample text with mixed character types
        text = "\ue02a\uec42 \ue065 \ue023\ue02a"  # consonants, punctuation, etc.
        
        analysis = self.tengwar_validator.get_character_analysis(text)
        
        assert 'consonants' in analysis
        assert 'vowels' in analysis
        assert 'punctuation' in analysis
        assert sum(analysis.values()) == len(text)
    
    def test_unknown_tengwar_characters(self):
        """Test handling of unknown Tengwar characters."""
        # Create text with Private Use Area character not in mapping
        unknown_char = "\ue800"  # Random PUA character
        text = f"\ue02a{unknown_char}\uec42"
        
        result = self.tengwar_validator.validate(text)
        
        # Should still be valid but with warnings
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("Unknown Tengwar" in warning for warning in result.warnings)
    
    def test_validation_summary(self):
        """Test validation summary generation."""
        text = "\ue02a\uec42\ue02a\ue020"
        unicode_validator = UnicodeValidator()
        result = unicode_validator.validate(text)
        summary = unicode_validator.get_validation_summary(result)
        
        assert "Valid Unicode transcription" in summary
        assert "Total characters:" in summary
        assert "Tengwar characters:" in summary


class TestIntegratedValidation:
    """Test validation integrated with transcription."""
    
    def test_transcription_with_validation(self):
        """Test transcription with immediate validation."""
        parser = ModeParser()
        mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
        mode.processor.finalize({})
        
        # Transcribe text
        success, result, _ = mode.transcribe("Elen síla lúmenn omentielvo")
        
        # Validate result
        unicode_validator = UnicodeValidator()
        tengwar_validator = TengwarValidator()
        
        unicode_result = unicode_validator.validate(result)
        tengwar_result = tengwar_validator.validate(result)
        
        assert unicode_result.is_valid
        assert tengwar_result.is_valid
        
        # Get detailed analysis
        analysis = tengwar_validator.get_character_analysis(result)
        assert analysis['consonants'] > 0
    
    def test_validation_error_cases(self):
        """Test validation with problematic input."""
        unicode_validator = UnicodeValidator()
        
        # Test with control characters
        problematic_text = "\ue02a\uec42\u0001\u0002"  # Contains control chars
        result = unicode_validator.validate(problematic_text)
        
        assert not result.is_valid
        assert len(result.errors) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
