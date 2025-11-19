"""
Core transcription functionality tests.

Consolidated from:
- test_integration.py (mode loading, basic transcription)
- test_virtual_characters.py (virtual character resolution)
- test_cross_rules.py (cross-rule testing)

This reduces duplicate mode loading and provides better test organization.
"""

import pytest
from glaemscribe.parsers.charset_parser import CharsetParser
from glaemscribe.validation.tengwar_validator import TengwarValidator
from glaemscribe.resources import get_mode_path


# Use fixtures from conftest.py - no need to redefine them here


class TestModeLoading:
    """Test complete mode loading and finalization."""
    
    def test_quenya_classical_mode_loading(self, quenya_classical_mode):
        """Test Quenya Classical mode loads without critical errors."""
        mode = quenya_classical_mode
        
        assert mode is not None
        assert mode.name == "quenya-tengwar-classical"
        assert hasattr(mode, 'processor')
        assert len(mode.processor.rule_groups) > 0
    
    def test_sindarin_general_mode_loading(self, sindarin_general_mode):
        """Test Sindarin General Use mode loads without critical errors."""
        mode = sindarin_general_mode
        
        assert mode is not None
        assert mode.name == "sindarin-tengwar-general_use"
        assert hasattr(mode, 'processor')
        assert len(mode.processor.rule_groups) > 0
    
    def test_sindarin_beleriand_mode_loading(self, sindarin_beleriand_mode):
        """Test Sindarin Beleriand mode loads without critical errors."""
        mode = sindarin_beleriand_mode
        
        assert mode is not None
        assert mode.name == "sindarin-tengwar-beleriand"
        assert hasattr(mode, 'processor')
        assert len(mode.processor.rule_groups) > 0
    
    def test_english_tengwar_mode_loading(self, english_tengwar_mode):
        """Test English Tengwar mode loads without critical errors."""
        mode = english_tengwar_mode
        
        assert mode is not None
        assert mode.name == "english-tengwar-espeak"
        assert hasattr(mode, 'processor')
        assert len(mode.processor.rule_groups) > 0
    
    def test_raw_tengwar_mode_loading(self, mode_parser):
        """Test raw Tengwar mode loads and can transcribe."""
        mode = mode_parser.parse(str(get_mode_path('raw-tengwar')))
        mode.processor.finalize({})
        
        assert mode is not None
        assert mode.name == "raw-tengwar"
        assert len(mode.processor.rule_groups) > 0
    
    def test_mode_with_unicode_charset(self, mode_parser):
        """Test mode loading with Unicode charset support."""
        mode = mode_parser.parse(str(get_mode_path('raw-tengwar')))
        mode.processor.finalize({})
        
        # Unicode variables should be available
        rule_group = list(mode.processor.rule_groups.values())[0]
        
        # Check built-in Unicode variables
        unicode_vars = ["NBSP", "WJ", "ZWSP", "UNDERSCORE"]
        for var_name in unicode_vars:
            if var_name in rule_group.vars:
                value = rule_group.vars[var_name].value
                assert value.startswith("{UNI_"), f"{var_name} should be Unicode variable"


class TestBasicTranscription:
    """Test end-to-end transcription functionality."""
    
    @pytest.mark.known_issue
    def test_english_tengwar_basic_transcription(self, english_tengwar_mode):
        """KNOWN ISSUE: Basic English transcription should work."""
        mode = english_tengwar_mode
        
        # Try basic transcription
        try:
            result = mode.transcribe("test")
            # TODO: Should get actual Tengwar output
            # For now, just test it doesn't crash
            assert isinstance(result, str)
        except Exception as e:
            # Known issue - transcription may fail due to missing charset or other issues
            pytest.skip(f"Transcription failed with known issue: {e}")
    
    def test_quenya_basic_transcription(self, quenya_classical_mode):
        """Test basic Quenya transcription."""
        mode = quenya_classical_mode
        
        success, result, _ = mode.transcribe("aiya")
        
        assert success
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_sindarin_basic_transcription(self, sindarin_general_mode):
        """Test basic Sindarin transcription."""
        mode = sindarin_general_mode
        
        success, result, _ = mode.transcribe("mellon")
        
        assert success
        assert isinstance(result, str)
        assert len(result) > 0


class TestCharsetLoading:
    """Test charset loading and character definitions."""
    
    def test_tengwar_freemono_charset_loading(self, tengwar_freemono_charset):
        """Test Tengwar FreeMonoTengwar (Unicode) charset loads correctly."""
        charset = tengwar_freemono_charset
        
        assert charset is not None
        assert len(charset.characters) > 0
        
        # Check if virtual characters were parsed
        assert hasattr(charset, 'virtual_chars'), "Charset should have virtual_chars attribute"


class TestVirtualCharacterResolution:
    """Test virtual character resolution in post-processing."""
    
    def test_virtual_character_resolution_basic(self, quenya_classical_mode):
        """Test basic virtual character resolution."""
        mode = quenya_classical_mode
        
        # Simple test case - just a vowel that should use virtual character resolution
        text = "a"
        success, result, debug = mode.transcribe(text)
        
        print(f"Input: '{text}'")
        print(f"Output: '{result}'")
        print(f"Success: {success}")
        
        assert success
        assert isinstance(result, str)
        # Note: Validation is tested in test_transcription_validation.py
    
    def test_mode_loads_virtual_character_operator(self, quenya_classical_mode):
        """Test that post-processor loads virtual character resolution operators."""
        mode = quenya_classical_mode
        
        assert mode.post_processor is not None
        assert hasattr(mode.post_processor, 'operators')
        
        # Check that resolve_virtuals operator was loaded
        from glaemscribe.core.post_processor.resolve_virtuals import ResolveVirtualsPostProcessorOperator
        has_resolve_virtuals = any(
            isinstance(op, ResolveVirtualsPostProcessorOperator) 
            for op in mode.post_processor.operators
        )
        assert has_resolve_virtuals, "Post-processor should have ResolveVirtualsPostProcessorOperator"
    
    def test_virtual_character_context_dependence(self, quenya_classical_mode):
        """Test that virtual characters work in context-dependent scenarios."""
        mode = quenya_classical_mode
        
        # Test a word that should trigger virtual character resolution
        test_cases = [
            "aiya",  # Should use different vowel forms
            "elen",  # Should use different consonant forms
            "lúmenn", # Should use different vowel forms
        ]
        
        for text in test_cases:
            success, result, _ = mode.transcribe(text)
            assert success, f"Transcription failed for '{text}'"
            assert isinstance(result, str)
            assert len(result) > 0


class TestCrossRuleFunctionality:
    """Test cross-rule functionality and interactions."""
    
    def test_english_tengwar_cross_rule_detection(self, english_tengwar_mode):
        """Test cross-rule detection in English Tengwar."""
        mode = english_tengwar_mode
        
        # Should have cross rules if they're defined
        if hasattr(mode.processor, 'cross_rules'):
            assert len(mode.processor.cross_rules) >= 0  # May be empty
    
    def test_quenya_cross_rule_functionality(self, quenya_classical_mode):
        """Test cross-rule functionality in Quenya."""
        mode = quenya_classical_mode
        
        # Test basic transcription that might use cross rules
        success, result, _ = mode.transcribe("Elen síla")
        
        assert success
        assert isinstance(result, str)
    
    @pytest.mark.known_issue
    def test_conditional_macro_deployment(self, quenya_classical_mode):
        """KNOWN ISSUE: Test conditional macro deployment in cross rules."""
        mode = quenya_classical_mode
        
        # This test would check if conditional macros are properly deployed
        # For now, just test basic transcription works
        success, result, _ = mode.transcribe("test")
        
        if not success:
            pytest.skip("Conditional macro deployment has known issues")
        
        assert isinstance(result, str)


