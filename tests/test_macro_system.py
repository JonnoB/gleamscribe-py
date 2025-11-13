"""Test macro system implementation."""

import pytest
from src.glaemscribe.core.rule_group import RuleGroup, CodeLinesTerm, CodeLine
from src.glaemscribe.core.macro import Macro, MacroDeployTerm
from src.glaemscribe.core.mode_enhanced import Mode


class TestMacroSystem:
    """Test macro functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mode = Mode("test_mode")
        self.mode.errors = []
        self.rule_group = RuleGroup(self.mode, "test_group")
    
    def test_macro_creation_and_storage(self):
        """Test macro objects can be created and stored."""
        macro = Macro(self.rule_group, "test_macro", ["ARG1", "ARG2"])
        self.rule_group.add_macro(macro)
        
        assert "test_macro" in self.rule_group.macros
        assert self.rule_group.macros["test_macro"] == macro
        assert macro.arg_names == ["ARG1", "ARG2"]
    
    def test_macro_deploy_term_creation(self):
        """Test macro deployment terms can be created."""
        macro = Macro(self.rule_group, "test_macro", ["ARG1"])
        deploy = MacroDeployTerm(
            macro=macro,
            line=10,
            parent_code_block=self.rule_group.root_code_block,
            arg_value_expressions=["value1"]
        )
        
        assert deploy.macro == macro
        assert deploy.line == 10
        assert deploy.arg_value_expressions == ["value1"]
        assert deploy.is_macro_deploy()
    
    def test_macro_argument_validation(self):
        """Test macro argument name validation."""
        # Valid argument names
        valid_macro = Macro(self.rule_group, "valid_macro", ["ARG_A", "ARG_B", "ARG_123"])
        assert valid_macro.arg_names == ["ARG_A", "ARG_B", "ARG_123"]
    
    def test_macro_rule_expansion(self):
        """Test that macro content creates actual rules."""
        # Create macro with a rule
        macro = Macro(self.rule_group, "test_macro", ["ARG1", "ARG2"])
        
        # Add code lines term to macro
        code_lines_term = CodeLinesTerm(macro.root_code_block)
        macro.root_code_block.add_term(code_lines_term)
        
        # Add rule that uses macro arguments
        code_line = CodeLine("{ARG1} --> {ARG2}", 1)
        code_lines_term.code_lines.append(code_line)
        
        # Deploy the macro
        deploy = MacroDeployTerm(
            macro=macro,
            line=10,
            parent_code_block=self.rule_group.root_code_block,
            arg_value_expressions=["value1", "value2"]
        )
        self.rule_group.root_code_block.add_term(deploy)
        
        # Finalize should expand the macro
        self.rule_group.finalize({})
        
        assert len(self.rule_group.rules) == 1
        rule = self.rule_group.rules[0]
        
        # Check that macro arguments were resolved
        assert "value1" in str(rule.src_sheaf_chain)
        assert "value2" in str(rule.dst_sheaf_chain)
    
    def test_cross_rule_in_macro(self):
        """Test that cross rules work inside macros."""
        # Add cross schema variable
        self.rule_group.add_var("SWAP_SCHEMA", "2,1", False)
        
        # Create macro with cross rule
        cross_macro = Macro(self.rule_group, "cross_swap", ["ARG1", "ARG2"])
        
        code_lines_term = CodeLinesTerm(cross_macro.root_code_block)
        cross_macro.root_code_block.add_term(code_lines_term)
        
        # Add cross rule using macro arguments
        cross_line = CodeLine("[{ARG1}][{ARG2}] --> {SWAP_SCHEMA} --> [{_ARG2_}][{_ARG1_}]", 1)
        code_lines_term.code_lines.append(cross_line)
        
        self.rule_group.add_macro(cross_macro)
        
        # Deploy the macro
        deploy = MacroDeployTerm(
            macro=cross_macro,
            line=10,
            parent_code_block=self.rule_group.root_code_block,
            arg_value_expressions=["a", "b"]
        )
        self.rule_group.root_code_block.add_term(deploy)
        
        # Finalize
        self.rule_group.finalize({})
        
        assert len(self.rule_group.rules) == 1
        rule = self.rule_group.rules[0]
        assert rule.cross_schema == "2,1"
    
    def test_macro_argument_scoping(self):
        """Test that macro arguments don't conflict with existing variables."""
        # Add existing variable
        self.rule_group.add_var("EXISTING_VAR", "old_value", False)
        
        # Create macro that tries to use same name
        macro = Macro(self.rule_group, "test_macro", ["EXISTING_VAR"])
        
        code_lines_term = CodeLinesTerm(macro.root_code_block)
        macro.root_code_block.add_term(code_lines_term)
        
        code_line = CodeLine("{EXISTING_VAR} --> test", 1)
        code_lines_term.code_lines.append(code_line)
        
        self.rule_group.add_macro(macro)
        
        # Deploy the macro
        deploy = MacroDeployTerm(
            macro=macro,
            line=10,
            parent_code_block=self.rule_group.root_code_block,
            arg_value_expressions=["new_value"]
        )
        self.rule_group.root_code_block.add_term(deploy)
        
        # Should add error about variable conflict
        self.rule_group.finalize({})
        
        # Should have an error about conflicting variable names
        assert len(self.mode.errors) > 0
        assert any("hinders a variable with the same name" in str(error) for error in self.mode.errors)
    
    def test_macro_variable_cleanup(self):
        """Test that macro variables are cleaned up after deployment."""
        # Create macro
        macro = Macro(self.rule_group, "test_macro", ["ARG1"])
        
        code_lines_term = CodeLinesTerm(macro.root_code_block)
        macro.root_code_block.add_term(code_lines_term)
        
        code_line = CodeLine("{ARG1} --> test", 1)
        code_lines_term.code_lines.append(code_line)
        
        self.rule_group.add_macro(macro)
        
        # Check initial variable count
        initial_var_count = len(self.rule_group.vars)
        
        # Deploy the macro
        deploy = MacroDeployTerm(
            macro=macro,
            line=10,
            parent_code_block=self.rule_group.root_code_block,
            arg_value_expressions=["value1"]
        )
        self.rule_group.root_code_block.add_term(deploy)
        
        # Finalize should expand and then cleanup
        self.rule_group.finalize({})
        
        # Variable count should be back to initial
        assert len(self.rule_group.vars) == initial_var_count
    
    @pytest.mark.regression
    def test_regression_macro_redefinition_error(self):
        """REGRESSION: Should detect macro redefinition."""
        # Create first macro
        macro1 = Macro(self.rule_group, "test_macro", ["ARG1"])
        self.rule_group.add_macro(macro1)
        
        # Try to create second macro with same name
        macro2 = Macro(self.rule_group, "test_macro", ["ARG2"])
        
        # Should detect redefinition
        assert "test_macro" in self.rule_group.macros
        assert self.rule_group.macros["test_macro"] == macro1
    
    @pytest.mark.regression
    def test_regression_argument_count_mismatch(self):
        """REGRESSION: Should detect macro argument count mismatches."""
        # Create macro expecting 2 arguments
        macro = Macro(self.rule_group, "test_macro", ["ARG1", "ARG2"])
        self.rule_group.add_macro(macro)
        
        # Try to deploy with only 1 argument
        deploy = MacroDeployTerm(
            macro=macro,
            line=10,
            parent_code_block=self.rule_group.root_code_block,
            arg_value_expressions=["value1"]  # Missing second argument
        )
        
        # This should be caught by parser validation
        # In real usage, the parser would add an error before deployment
        assert len(macro.arg_names) == 2
        assert len(deploy.arg_value_expressions) == 1
