"""Test Unicode variable implementation."""

import pytest
from glaemscribe.core.rule_group import RuleGroup
from glaemscribe.core.mode_enhanced import Mode


class TestUnicodeVariables:
    """Test Unicode variable functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mode = Mode("test_mode")
        self.mode.errors = []
        self.rule_group = RuleGroup(self.mode, "test_group")
        self.rule_group.finalize({})
    
    def test_builtin_unicode_variables_defined(self):
        """Test that built-in Unicode variables are defined."""
        builtin_vars = ["NBSP", "WJ", "ZWSP", "ZWNJ", "UNDERSCORE", "ASTERISK"]
        
        for var_name in builtin_vars:
            assert var_name in self.rule_group.vars
            assert self.rule_group.vars[var_name].value.startswith("{UNI_")
    
    def test_unicode_variable_resolution(self):
        """Test Unicode variables are kept intact during apply_vars (Ruby behavior)."""
        test_cases = [
            "{UNI_E000}",  # Tengwar Tinco
            "{UNI_E001}",  # Tengwar Parma
            "{UNI_A0}",    # Non-breaking space
            "{UNI_5F}",    # Underscore
        ]
        
        for unicode_var in test_cases:
            # apply_vars keeps Unicode variables intact
            result = self.rule_group.apply_vars(1, unicode_var, allow_unicode_vars=True)
            assert result == unicode_var, f"Expected {unicode_var}, got {result}"
            
            # Conversion happens in convert_unicode_vars
            converted = self.rule_group.convert_unicode_vars(1, result)
            assert len(converted) == 1, f"Expected single character, got {converted}"
    
    def test_unicode_variable_in_rule_context(self):
        """Test Unicode variables work in transcription rules."""
        # Add a rule that uses Unicode variables (only source can have Unicode)
        self.rule_group._process_code_line("{UNI_E000} --> normal_text", 1)
        
        assert len(self.rule_group.rules) == 1
        rule = self.rule_group.rules[0]
        
        # Check that Unicode characters are in the source
        assert "\ue000" in str(rule.src_sheaf_chain)
    
    def test_invalid_unicode_hex_format(self):
        """Test invalid Unicode hex codes are rejected."""
        initial_error_count = len(self.mode.errors)
        
        result = self.rule_group.apply_vars(1, "{UNI_GARBAGE}", allow_unicode_vars=True)
        
        # Should return None and add error (Ruby behavior: undefined variable fails)
        assert result is None
        assert len(self.mode.errors) > initial_error_count
        assert "failed to evaluate variable" in str(self.mode.errors[-1])
    
    def test_unicode_out_of_range(self):
        """Test Unicode code points beyond limit are kept as variables."""
        # Valid hex format, so it stays as a Unicode variable
        result = self.rule_group.apply_vars(1, "{UNI_110000}", allow_unicode_vars=True)
        
        # Should keep the variable intact (will be validated during conversion)
        assert result == "{UNI_110000}"
    
    def test_unicode_variable_scope_validation(self):
        """Test Unicode variables rejected in non-Unicode context."""
        result = self.rule_group.apply_vars(1, "{UNI_E000}", allow_unicode_vars=False)
        
        # Should return None when Unicode not allowed
        assert result is None
    
    def test_nested_unicode_variable_resolution(self):
        """Test Unicode variables in nested variable definitions."""
        # Define a variable that contains Unicode
        self.rule_group.add_var("TEST_VAR", "{UNI_E000}", False)
        
        # Use the variable in a rule - it resolves to the Unicode variable string
        result = self.rule_group.apply_vars(1, "{TEST_VAR}", allow_unicode_vars=True)
        assert result == "{UNI_E000}"
        
        # Then convert the Unicode variable to actual character
        converted = self.rule_group.convert_unicode_vars(1, result)
        assert converted == "\ue000"
    
    @pytest.mark.regression
    def test_regression_empty_target_sheaf_chain(self):
        """REGRESSION: Unicode rules should not create empty target chains."""
        # This was a bug where Unicode variables created empty targets
        self.rule_group._process_code_line("{UNI_E000} --> normal_text", 1)
        
        assert len(self.rule_group.rules) == 1
        rule = self.rule_group.rules[0]
        
        # Target should not be empty
        assert len(rule.dst_sheaf_chain.sheaves) > 0
        assert len(rule.dst_sheaf_chain.sheaves[0].fragments) > 0
        # Check the fragment expression contains the text
        assert "normal_text" in str(rule.dst_sheaf_chain)
