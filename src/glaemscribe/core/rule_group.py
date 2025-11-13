"""Rule group implementation for Glaemscribe.

This is a port of the Ruby RuleGroup class, supporting variables,
rules, and conditional logic.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Pattern
import re

from ..parsers.glaeml import Error


@dataclass
class RuleGroupVar:
    """A variable in a rule group."""
    name: str
    value: str
    is_pointer: bool = False
    
    def is_pointer_var(self) -> bool:
        """Check if this is a pointer variable."""
        return self.is_pointer


class CodeBlock:
    """A block of code with conditional logic."""
    
    def __init__(self):
        """Initialize a code block."""
        self.terms: List[Union[IfCond, CodeLine, Any]] = []
        self.parent_if_cond: Optional[IfCond] = None
    
    def add_term(self, term: Union[IfCond, CodeLine, Any]):
        """Add a term to this code block."""
        self.terms.append(term)


@dataclass
class CodeLine:
    """A single line of code in a rule group."""
    expression: str
    line: int
    
    def __post_init__(self):
        """Clean up the expression."""
        self.expression = self.expression.strip()


@dataclass
class IfCond:
    """A conditional statement in a rule group."""
    line: int
    expression: str
    parent_if_term: Optional[IfCond] = None
    child_code_block: Optional[CodeBlock] = field(default_factory=CodeBlock)
    
    def __post_init__(self):
        """Set up the child code block parent."""
        if self.child_code_block:
            self.child_code_block.parent_if_cond = self


class RuleGroup:
    """A group of transcription rules with variables and conditions."""
    
    # Regular expressions for parsing
    VAR_NAME_REGEXP: Pattern = re.compile(r'{([0-9A-Z_]+)}')
    UNICODE_VAR_NAME_REGEXP_IN: Pattern = re.compile(r'^UNI_([0-9A-F]+)$')
    UNICODE_VAR_NAME_REGEXP_OUT: Pattern = re.compile(r'{UNI_([0-9A-F]+)}')
    
    VAR_DECL_REGEXP: Pattern = re.compile(r'^\s*{([0-9A-Z_]+)}\s+===\s+(.+?)\s*$')
    POINTER_VAR_DECL_REGEXP: Pattern = re.compile(r'^\s*{([0-9A-Z_]+)}\s+<=>\s+(.+?)\s*$')
    RULE_REGEXP: Pattern = re.compile(r'^\s*(.*?)\s+-->\s+(.+?)\s*$')
    
    def __init__(self, mode, name: str):
        """Initialize a rule group."""
        self.name: str = name
        self.mode = mode
        self.vars: Dict[str, RuleGroupVar] = {}
        self.macros: Dict[str, Any] = {}
        self.root_code_block: CodeBlock = CodeBlock()
        self.rules: List[Any] = []  # Will be populated after finalization
    
    def add_var(self, var_name: str, value: str, is_pointer: bool = False):
        """Add a variable to the rule group."""
        self.vars[var_name] = RuleGroupVar(var_name, value, is_pointer)
    
    def apply_vars(self, line: int, string: str, allow_unicode_vars: bool = False) -> Optional[str]:
        """Replace all variables in an expression."""
        ret = string
        stack_depth = 0
        had_replacements = True
        
        while had_replacements:
            had_replacements = False
            ret = re.sub(self.VAR_NAME_REGEXP, lambda match: self._replace_var(match, line, string, allow_unicode_vars, had_replacements), ret)
        
        return ret
    
    def _replace_var(self, match, line: int, string: str, allow_unicode_vars: bool, had_replacements: bool) -> str:
        """Replace a single variable."""
        vname = match.group(1)
        cap_var = match.group(0)
        
        v = self.vars.get(vname)
        if not v:
            if self.UNICODE_VAR_NAME_REGEXP_IN.match(vname):
                # Unicode variable
                if allow_unicode_vars:
                    return cap_var
                else:
                    self.mode.errors.append(Error(line, f"In expression: {string}: making wrong use of unicode variable: {cap_var}. Unicode vars can only be used in source members of a rule or in the definition of another variable."))
                    return cap_var
            else:
                self.mode.errors.append(Error(line, f"In expression: {string}: failed to evaluate variable: {cap_var}."))
                return cap_var
        else:
            # Count replacements on non-unicode vars
            had_replacements = True
            return v.value
    
    def finalize(self, trans_options: Dict[str, Any]):
        """Finalize the rule group with given transcription options.
        
        This processes all the code lines and conditional blocks to build
        the final set of rules.
        """
        if not hasattr(self, 'rules'):
            self.rules = []
        
        # Only process if we have code blocks (parsed from file)
        if hasattr(self, 'root_code_block') and self.root_code_block.terms:
            self._process_code_block(self.root_code_block, trans_options)
    
    def _process_code_block(self, code_block: CodeBlock, trans_options: Dict[str, Any]):
        """Process a code block and extract rules.
        
        Args:
            code_block: The code block to process
            trans_options: Current transcription options
        """
        for term in code_block.terms:
            if isinstance(term, CodeLine):
                self._process_code_line(term.expression, term.line)
            elif hasattr(term, 'child_code_block'):
                # Handle conditional blocks (if/else/endif)
                # For now, we'll just process the child block
                self._process_code_block(term.child_code_block, trans_options)
    
    def _process_code_line(self, line: str, line_num: int):
        """Process a single line of code.
        
        Args:
            line: The line to process
            line_num: Line number for error reporting
        """
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('**'):
            return
        
        # Check if it's a variable declaration
        match = self.VAR_DECL_REGEXP.match(line)
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            self.add_var(var_name, var_value)
            return
        
        # Check if it's a pointer variable declaration
        match = self.POINTER_VAR_DECL_REGEXP.match(line)
        if match:
            var_name = match.group(1)
            var_value = match.group(2)
            self.add_var(var_name, var_value, is_pointer=True)
            return
        
        # Check if it's a transcription rule
        match = self.RULE_REGEXP.match(line)
        if match:
            source = match.group(1).strip()
            target = match.group(2).strip()
            
            # Apply variable substitution to both source and target
            resolved_source = self._resolve_variables(source, line_num)
            resolved_target = self._resolve_variables(target, line_num)
            
            if resolved_source and resolved_target:
                rule = {
                    'source': resolved_source,
                    'target': resolved_target,
                    'line': line_num
                }
                self.rules.append(rule)
            return
    
    def _resolve_variables(self, expression: str, line_num: int) -> Optional[str]:
        """Resolve variables in an expression.
        
        Args:
            expression: The expression with variables
            line_num: Line number for error reporting
        
        Returns:
            Resolved expression or None if error
        """
        return self.apply_vars(line_num, expression, allow_unicode_vars=True)
    
    def __str__(self) -> str:
        """String representation of the rule group."""
        return f"<RuleGroup {self.name}: {len(self.vars)} vars, {len(self.rules)} rules>"
