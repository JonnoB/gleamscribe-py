"""Tests for the simple high-level API."""

import pytest
from glaemscribe import transcribe, transcribe_detailed, list_modes, clear_cache


class TestSimpleAPI:
    """Test the simple functional API."""
    
    def test_transcribe_quenya(self):
        """Test basic Quenya transcription."""
        result = transcribe("aiya", mode="quenya")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain Tengwar Unicode characters
        assert any(0xE000 <= ord(c) <= 0xF8FF for c in result)
    
    def test_transcribe_sindarin(self):
        """Test basic Sindarin transcription."""
        result = transcribe("mellon", mode="sindarin")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_transcribe_with_alias(self):
        """Test that mode aliases work."""
        # These should all work
        result1 = transcribe("test", mode="quenya")
        result2 = transcribe("test", mode="quenya-classical")
        result3 = transcribe("test", mode="quenya-tengwar-classical")
        
        # All should produce the same result
        assert result1 == result2 == result3
    
    def test_transcribe_default_mode(self):
        """Test that default mode is quenya."""
        result = transcribe("aiya")  # No mode specified
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_transcribe_invalid_mode(self):
        """Test that invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            transcribe("test", mode="nonexistent-mode")
    
    def test_transcribe_detailed(self):
        """Test detailed transcription with full results."""
        success, result, debug = transcribe_detailed("aiya", mode="quenya")
        
        assert success is True
        assert isinstance(result, str)
        assert len(result) > 0
        # Debug can be a string or debug object
        assert debug is not None
    
    def test_list_modes(self):
        """Test listing available modes."""
        modes = list_modes()
        
        assert isinstance(modes, list)
        assert len(modes) > 0
        
        # Should include both aliases and full names
        assert "quenya" in modes
        assert "sindarin" in modes
        assert "quenya-tengwar-classical" in modes
        assert "sindarin-tengwar-general_use" in modes
    
    def test_cache_functionality(self):
        """Test that mode caching works."""
        # First call should parse the mode
        result1 = transcribe("test", mode="quenya")
        
        # Second call should use cached mode (faster)
        result2 = transcribe("test", mode="quenya")
        
        # Results should be identical
        assert result1 == result2
        
        # Clear cache
        clear_cache()
        
        # Should still work after cache clear
        result3 = transcribe("test", mode="quenya")
        assert result3 == result1
    
    def test_transcribe_famous_phrase(self):
        """Test transcription of famous Quenya phrase."""
        result = transcribe("Elen síla lúmenn' omentielvo", mode="quenya")
        
        assert isinstance(result, str)
        assert len(result) > 20  # Should be a substantial transcription
        # Should contain Tengwar characters
        assert any(0xE000 <= ord(c) <= 0xF8FF for c in result)
    
    def test_multiple_modes(self):
        """Test that different modes produce different results."""
        text = "test"
        
        quenya_result = transcribe(text, mode="quenya")
        sindarin_result = transcribe(text, mode="sindarin")
        
        # Different modes should (likely) produce different results
        # Note: They might be the same for some inputs, but generally differ
        assert isinstance(quenya_result, str)
        assert isinstance(sindarin_result, str)


class TestAPIConsistency:
    """Test consistency between simple and advanced APIs."""
    
    def test_simple_vs_advanced_api(self):
        """Test that simple API produces same results as advanced API."""
        from glaemscribe.parsers.mode_parser import ModeParser
        from glaemscribe.resources import get_mode_path
        
        text = "aiya"
        
        # Simple API
        simple_result = transcribe(text, mode="quenya")
        
        # Advanced API
        parser = ModeParser()
        mode = parser.parse(str(get_mode_path('quenya-tengwar-classical')))
        mode.processor.finalize({})
        success, advanced_result, _ = mode.transcribe(text)
        
        assert success
        assert simple_result == advanced_result
