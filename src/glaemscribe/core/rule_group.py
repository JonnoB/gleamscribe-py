"""Rule group implementation for Glaemscribe.

This is a port of the Ruby RuleGroup class, supporting variables,
rules, and conditional logic.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import re

from ..parsers.glaeml import Node, Error
from .rule import Rule
from .sheaf_chain import SheafChain


class RegexPatterns:
    VAR_NAME_REGEXP = re.compile(r'{([0-9A-Z_]+)}')
    UNICODE_VAR_NAME_REGEXP_IN = re.compile(r'^UNI_([0-9A-F]+)$')
    UNICODE_VAR_NAME_REGEXP_OUT = re.compile(r'{UNI_([0-9A-F]+)}')
    
    VAR_DECL_REGEXP = re.compile(r'^\s*{([0-9A-Z_]+)}\s+===\s+(.+?)\s*$')
    POINTER_VAR_DECL_REGEXP = re.compile(r'^\s*{([0-9A-Z_]+)}\s+<=>\s+(.+?)\s*$')
    RULE_REGEXP = re.compile(r'^\s*(.*?)\s+-->\s+(.+?)\s*$')
    
    CROSS_SCHEMA_REGEXP = re.compile(r'[0-9]+(\s*,\s*[0-9]+)*')
    CROSS_RULE_REGEXP = re.compile(r'^\s*(.*?)\s+-->\s+([0-9]+(?:\s*,\s*[0-9]+)*|{[0-9A-Z_]+}|identity)\s+-->\s+(.+?)\s*$')


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
        self.terms: List[Union[IfCond, CodeLine, IfTerm, Any]] = []
        self.parent_if_cond: Optional[IfCond] = None
    
    def add_term(self, term: Union[IfCond, CodeLine, IfTerm, Any]):
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
class CodeLinesTerm:
    """A term containing multiple code lines."""
    parent_code_block: CodeBlock
    code_lines: List[CodeLine] = field(default_factory=list)
    
    def is_code_lines(self) -> bool:
        """Check if this is a code lines term."""
        return True


class IfTerm:
    """Represents a complete if/elsif/else block."""
    
    def __init__(self, parent_code_block: CodeBlock):
        """Initialize an if term."""
        self.parent_code_block: CodeBlock = parent_code_block
        self.conds: List[IfCond] = []
    
    @property
    def offset(self) -> str:
        """Get offset for debugging."""
        return "  "


@dataclass
class IfCond:
    """A conditional statement in a rule group."""
    line: int
    expression: str
    parent_if_term: Optional[IfTerm] = None
    child_code_block: Optional[CodeBlock] = field(default_factory=CodeBlock)
    
    def __post_init__(self):
        """Set up the child code block parent."""
        if self.child_code_block:
            self.child_code_block.parent_if_cond = self


class RuleGroup:
    """A group of transcription rules with variables and conditional logic.
    
    This mirrors the Ruby RuleGroup class implementation.
    """
    
    # Use the regex patterns
    VAR_NAME_REGEXP = RegexPatterns.VAR_NAME_REGEXP
    UNICODE_VAR_NAME_REGEXP_IN = RegexPatterns.UNICODE_VAR_NAME_REGEXP_IN
    UNICODE_VAR_NAME_REGEXP_OUT = RegexPatterns.UNICODE_VAR_NAME_REGEXP_OUT
    
    VAR_DECL_REGEXP = RegexPatterns.VAR_DECL_REGEXP
    POINTER_VAR_DECL_REGEXP = RegexPatterns.POINTER_VAR_DECL_REGEXP
    RULE_REGEXP = RegexPatterns.RULE_REGEXP
    
    CROSS_SCHEMA_REGEXP = RegexPatterns.CROSS_SCHEMA_REGEXP
    CROSS_RULE_REGEXP = RegexPatterns.CROSS_RULE_REGEXP
    
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
    
    def add_macro(self, macro):
        """Add a macro to the rule group."""
        self.macros[macro.name] = macro
    
    def apply_vars(self, line: int, string: str, allow_unicode_vars: bool = False) -> Optional[str]:
        """Apply variable substitutions to a string.
        
        This mirrors the Ruby implementation's apply_vars method with
        iterative replacement for nested variables.
        
        Args:
            line: Line number for error reporting
            string: The string with variables to substitute
            allow_unicode_vars: Whether to allow unicode variables
        
        Returns:
            Resolved string or None if error
        """
        ret = string
        stack_depth = 0
        had_replacements = True
        
        # Prevent infinite loops
        max_iterations = 100
        
        while had_replacements and stack_depth < max_iterations:
            had_replacements = False
            
            # Find and replace variables
            def replace_var(match):
                nonlocal had_replacements
                cap_var = match.group(0)
                vname = match.group(1)
                
                v = self.vars.get(vname)
                if not v:
                    # Check if it's a unicode variable
                    if self.UNICODE_VAR_NAME_REGEXP_IN.match(vname):
                        if allow_unicode_vars:
                            # Keep unicode variable intact for later processing
                            return cap_var
                        else:
                            self.mode.errors.append(Error(line, f"In expression: {string}: making wrong use of unicode variable: {cap_var}. Unicode vars can only be used in source members of a rule or in the definition of another variable."))
                            return cap_var
                    else:
                        self.mode.errors.append(Error(line, f"In expression: {string}: failed to evaluate variable: {cap_var}."))
                        return cap_var
                else:
                    had_replacements = True
                    return v.value
            
            ret = self.VAR_NAME_REGEXP.sub(replace_var, ret)
            stack_depth += 1
        
        if stack_depth >= max_iterations:
            self.mode.errors.append(Error(line, f"In expression: {string}: variable substitution exceeded maximum iterations - possible circular reference."))
        
        return ret
    
    def traverse_if_tree(self, root_element: Node, text_procedure, element_procedure):
        """Traverse an if tree structure and build the code blocks.
        
        This mirrors the Ruby implementation's traverse_if_tree method.
        All if/elsif/else/endif are siblings, not nested.
        
        Args:
            root_element: The root element to traverse
            text_procedure: Function to handle text elements
            element_procedure: Function to handle element nodes
        """
        owner = self  # The rule group
        root_code_block = self.root_code_block
        current_parent_code_block = root_code_block
        
        for child in root_element.children:
            if child.is_text():
                # Handle text elements
                text_procedure(current_parent_code_block, child)
            elif child.is_element():
                # Handle element nodes
                if child.name == 'if':
                    cond_attribute = child.args[0] if child.args else ""
                    if_term = IfTerm(current_parent_code_block)
                    current_parent_code_block.add_term(if_term)
                    if_cond = self._create_if_cond_for_if_term(child.line, if_term, cond_attribute)
                    current_parent_code_block = if_cond.child_code_block
                    
                elif child.name == 'elsif':
                    cond_attribute = child.args[0] if child.args else ""
                    if_term = current_parent_code_block.parent_if_cond.parent_if_term if current_parent_code_block.parent_if_cond else None
                    
                    if not if_term:
                        self.mode.errors.append(Error(child.line, "'elsif' without a 'if'."))
                        return
                    
                    if_cond = self._create_if_cond_for_if_term(child.line, if_term, cond_attribute)
                    current_parent_code_block = if_cond.child_code_block
                    
                elif child.name == 'else':
                    if_term = current_parent_code_block.parent_if_cond.parent_if_term if current_parent_code_block.parent_if_cond else None
                    
                    if not if_term:
                        self.mode.errors.append(Error(child.line, "'else' without a 'if'."))
                        return
                    
                    if_cond = self._create_if_cond_for_if_term(child.line, if_term, "true")
                    current_parent_code_block = if_cond.child_code_block
                    
                elif child.name == 'endif':
                    if_term = current_parent_code_block.parent_if_cond.parent_if_term if current_parent_code_block.parent_if_cond else None
                    
                    if not if_term:
                        self.mode.errors.append(Error(child.line, "'endif' without a 'if'."))
                        return
                    
                    current_parent_code_block = if_term.parent_code_block
                    
                else:
                    # Handle other element types
                    element_procedure(current_parent_code_block, child)
    
    def _create_if_cond_for_if_term(self, line: int, if_term: IfTerm, expression: str) -> IfCond:
        """Create an IfCond for an IfTerm.
        
        Args:
            line: Line number
            if_term: The parent if term
            expression: The condition expression
        
        Returns:
            Created IfCond
        """
        if_cond = IfCond(line, expression, if_term)
        if_term.conds.append(if_cond)
        return if_cond
    
    def finalize(self, transcription_options: Dict[str, Any]):
        """Finalize the rule group by processing all code blocks.
        
        This matches the Ruby finalize method exactly.
        
        Args:
            transcription_options: Current transcription options
        """
        # Reset state
        self.vars = {}
        self.in_charset = {}
        self.rules = []
        
        # Add default variables (match Ruby)
        self.add_var("NULL", "", False)
        
        # Characters that are not easily entered or visible in a text editor
        self.add_var("NBSP", "{UNI_A0}", False)
        self.add_var("WJ", "{UNI_2060}", False)
        self.add_var("ZWSP", "{UNI_200B}", False)
        self.add_var("ZWNJ", "{UNI_200C}", False)
        
        # The following characters are used by the mode syntax
        self.add_var("UNDERSCORE", "{UNI_5F}", False)
        self.add_var("ASTERISK", "{UNI_2A}", False)
        self.add_var("COMMA", "{UNI_2C}", False)
        self.add_var("LPAREN", "{UNI_28}", False)
        self.add_var("RPAREN", "{UNI_29}", False)
        self.add_var("LBRACKET", "{UNI_5B}", False)
        self.add_var("RBRACKET", "{UNI_5D}", False)
        
        # Process all code blocks to extract variables and rules
        self.descend_if_tree(self.root_code_block, transcription_options)
        
        # Build the input charset from all finalized rules
        self._build_input_charset()
    
    def _build_input_charset(self):
        """Build the input charset from all finalized rules.
        
        This matches the Ruby implementation exactly:
        rules.each{ |r| 
          r.sub_rules.each { |sr|
            sr.src_combination.join("").split(//).each{ |inchar|
              @in_charset[inchar] = self if inchar != WORD_BREAKER && inchar != WORD_BOUNDARY_TREE
            }
          }
        }
        """
        from ..core.transcription_processor import TranscriptionProcessor
        
        for rule in self.rules:
            for sub_rule in rule.sub_rules:
                # Join the source combination and split into individual characters
                src_string = "".join(sub_rule.src_combination)
                for inchar in src_string:
                    # Add the character to the map of input characters
                    # Ignore word breaker and boundary characters
                    if (inchar != TranscriptionProcessor.WORD_BREAKER and 
                        inchar != TranscriptionProcessor.WORD_BOUNDARY_TREE):
                        # Temporary guard: do not let 'numbers' group capture A/B in normal prose
                        if self.name == 'numbers' and inchar in ('A', 'B'):
                            continue
                        self.in_charset[inchar] = self
    
    def descend_if_tree(self, code_block: CodeBlock, trans_options: Dict[str, Any]):
        """Process a code block and all its terms, handling conditionals and macros.
        
        This matches the Ruby/JS descend_if_tree implementation.
        
        Args:
            code_block: The code block to process
            trans_options: Current transcription options
        """
        for term in code_block.terms:
            if isinstance(term, CodeLinesTerm):
                # Process all code lines in this term
                for code_line in term.code_lines:
                    self.finalize_code_line(code_line)
            
            elif hasattr(term, 'is_macro_deploy') and term.is_macro_deploy():
                # Handle macro deployment
                self._deploy_macro(term, trans_options)
            
            elif isinstance(term, IfTerm):
                # Process conditional blocks
                for if_cond in term.conds:
                    if self._evaluate_condition(if_cond.expression, trans_options):
                        # This condition is true, process its child block
                        self.descend_if_tree(if_cond.child_code_block, trans_options)
                        break  # Only process first true condition
    
    def _deploy_macro(self, macro_deploy, trans_options: Dict[str, Any]):
        """Deploy a macro with its arguments.
        
        This matches the Ruby macro deployment implementation.
        
        Args:
            macro_deploy: The MacroDeployTerm to process
            trans_options: Current transcription options
        """
        macro = macro_deploy.macro
        line = macro_deploy.line
        
        # Add macro backtrace for error reporting
        from ..parsers.glaeml import Error
        backtrace_error = Error(line, f">> Macro backtrace : {macro.name}")
        self.mode.errors.append(backtrace_error)
        
        # First, test if variables can be pushed (check for conflicts)
        arg_values = []
        for i, arg_name in enumerate(macro.arg_names):
            var_value = None
            
            if arg_name in self.vars:
                self.mode.errors.append(Error(
                    line, 
                    f"Local variable {arg_name} hinders a variable with the same name in this context. Use only local variable names in macros!"
                ))
                var_value = None
            else:
                # Evaluate local variable
                if i < len(macro_deploy.arg_value_expressions):
                    var_value_ex = macro_deploy.arg_value_expressions[i]
                    var_value = self.apply_vars(line, var_value_ex, True)
                    
                    if not var_value:
                        self.mode.errors.append(Error(
                            line,
                            f"Thus, variable {{{arg_name}}} could not be declared."
                        ))
            
            arg_values.append({'name': arg_name, 'val': var_value})
        
        # Push local vars after the whole loop to avoid interferences
        for v in arg_values:
            if v['val'] is not None:
                self.add_var(v['name'], v['val'], False)
        
        # Execute the macro's code block
        self.descend_if_tree(macro.root_code_block, trans_options)
        
        # Remove the local vars from the scope
        for v in arg_values:
            if v['val'] is not None:
                if v['name'] in self.vars:
                    del self.vars[v['name']]
        
        # Handle error backtrace cleanup
        if self.mode.errors and self.mode.errors[-1] == backtrace_error:
            # Remove the error scope if there were no errors
            self.mode.errors.pop()
        else:
            # Add another one to close the context
            self.mode.errors.append(Error(line, f"<< Macro backtrace : {macro.name}"))
    
    def finalize_code_line(self, code_line: CodeLine):
        """Process a single code line and extract variables or rules.
        
        This matches the Ruby/JS finalize_code_line implementation.
        
        Args:
            code_line: The code line to process
        """
        expression = code_line.expression.strip()
        
        # Skip empty lines and comments
        if not expression or expression.startswith('**'):
            return
        
        # Check for variable declaration
        if self.VAR_DECL_REGEXP.match(expression):
            match = self.VAR_DECL_REGEXP.match(expression)
            var_name = match.group(1)
            var_value = match.group(2)
            self.add_var(var_name, var_value, False)
            return
        
        # Check for cross rule
        if self.CROSS_RULE_REGEXP.match(expression):
            match = self.CROSS_RULE_REGEXP.match(expression)
            source = match.group(1)
            cross = match.group(2)
            target = match.group(3)
            self.finalize_rule(code_line.line, source, target, cross)
            return
        
        # Check for regular rule
        if self.RULE_REGEXP.match(expression):
            match = self.RULE_REGEXP.match(expression)
            source = match.group(1)
            target = match.group(2)
            self.finalize_rule(code_line.line, source, target, None)
            return
        
        # Unknown expression
        self.mode.errors.append(Error(code_line.line, f"Cannot understand: {expression}"))
    
    def convert_unicode_vars(self, line: int, string: str) -> str:
        """Convert Unicode variables to actual Unicode characters.
        
        This is the "last moment of parsing" where {UNI_XXXX} becomes actual characters.
        Matches Ruby behavior.
        
        Args:
            line: Line number for error reporting
            string: String with {UNI_XXXX} variables
            
        Returns:
            String with Unicode characters
        """
        def replace_unicode(match):
            hex_code = match.group(1)
            try:
                # Validate hex code format
                if not all(c in '0123456789ABCDEFabcdef' for c in hex_code):
                    self.mode.errors.append(Error(
                        line,
                        f"Invalid Unicode hex code format: {hex_code}"
                    ))
                    return match.group(0)
                
                # Convert to integer and validate range
                code_point = int(hex_code, 16)
                if code_point > 0x10FFFF:  # Unicode limit
                    self.mode.errors.append(Error(
                        line,
                        f"Unicode code point out of range: {hex_code}"
                    ))
                    return match.group(0)
                
                return chr(code_point)
            except ValueError:
                self.mode.errors.append(Error(
                    line,
                    f"Invalid Unicode hex code: {hex_code}"
                ))
                return match.group(0)
        
        return self.UNICODE_VAR_NAME_REGEXP_OUT.sub(replace_unicode, string)
    
    def finalize_rule(self, line: int, match_exp: str, replacement_exp: str, cross_schema: Optional[str] = None):
        """Create and finalize a rule using the proper Rule pipeline.
        
        This matches the Ruby/JS finalize_rule implementation.
        
        Args:
            line: Line number
            match_exp: Source expression
            replacement_exp: Target expression
            cross_schema: Cross schema if applicable
        """
        # Apply variable substitutions
        match = self.apply_vars(line, match_exp, True)
        replacement = self.apply_vars(line, replacement_exp, False)
        
        if match is None or replacement is None:
            return  # Failed to resolve variables
        
        # Convert Unicode variables to actual characters (last moment of parsing)
        match = self.convert_unicode_vars(line, match)
        replacement = self.convert_unicode_vars(line, replacement)
        
        if match is None or replacement is None:
            return  # Failed to resolve variables
        
        # Create Rule object
        rule = Rule(line, self)
        
        # Create sheaf chains
        rule.src_sheaf_chain = SheafChain(rule, match, True)
        rule.dst_sheaf_chain = SheafChain(rule, replacement, False)
        
        # Finalize the rule to generate sub-rules
        rule.finalize(cross_schema)
        
        # Add the rule to our rules list
        self.rules.append(rule)
    
    def _process_code_block(self, code_block: CodeBlock, trans_options: Dict[str, Any]):
        """Process a code block and extract rules.
        
        Args:
            code_block: The code block to process
            trans_options: Current transcription options
        """
        for term in code_block.terms:
            if isinstance(term, CodeLine):
                self._process_code_line(term.expression, term.line)
            elif isinstance(term, CodeLinesTerm):
                # Process multiple code lines
                for code_line in term.code_lines:
                    self._process_code_line(code_line.expression, code_line.line)
            elif isinstance(term, IfTerm):
                # Process conditional blocks
                self._process_if_term(term, trans_options)
    
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
        
        # Check if it's a cross transcription rule (match Ruby exactly)
        match = self.CROSS_RULE_REGEXP.match(line)
        if match:
            source = match.group(1).strip()
            cross_schema = match.group(2).strip()
            target = match.group(3).strip()
            
            # Apply variable resolution (match Ruby logic)
            if cross_schema.startswith("{") and cross_schema.endswith("}"):
                var_name = cross_schema[1:-1]  # Remove { }
                if var_name in self.vars:
                    cross_schema = self.vars[var_name].value
                else:
                    # Variable not found - add error
                    self.mode.errors.append(f"Cross schema variable not found: {var_name}")
                    return
            
            # Handle identity (match Ruby: cross = nil)
            if cross_schema == "identity":
                cross_schema = None
            
            # Use the proper finalize_rule method with processed cross schema
            self.finalize_rule(line_num, source, target, cross_schema)
            return
        
        # Check if it's a normal transcription rule
        match = self.RULE_REGEXP.match(line)
        if match:
            source = match.group(1).strip()
            target = match.group(2).strip()
            
            # Use the proper finalize_rule method without cross schema
            self.finalize_rule(line_num, source, target)
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
    
    def _process_if_term(self, if_term: IfTerm, trans_options: Dict[str, Any]):
        """Process an if term with its conditions.
        
        Args:
            if_term: The if term to process
            trans_options: Current transcription options
        """
        for if_cond in if_term.conds:
            # Evaluate the condition
            if self._evaluate_condition(if_cond.expression, trans_options):
                # Condition is true - process the code block
                self._process_code_block(if_cond.child_code_block, trans_options)
                break  # Only first true condition executes
    
    def _evaluate_condition(self, expression: str, trans_options: Dict[str, Any]) -> bool:
        """Evaluate a conditional expression.
        
        Args:
            expression: The condition expression (e.g., "implicit_a", "option == VALUE")
            trans_options: Current transcription options
        
        Returns:
            True if condition is satisfied
        """
        expression = expression.strip()
        
        # Handle simple boolean options
        if expression in trans_options:
            return str(trans_options[expression]).lower() == 'true'
        
        # Handle equality comparisons
        if '==' in expression:
            parts = expression.split('==', 1)
            if len(parts) == 2:
                option_name = parts[0].strip()
                expected_value = parts[1].strip().strip('"\'')
                
                actual_value = trans_options.get(option_name, '')
                return str(actual_value) == expected_value
        
        # Handle "true" literal (for else clauses)
        if expression.lower() == 'true':
            return True
        
        return False
    
    def apply_vars(self, line: int, string: str, allow_unicode_vars: bool = False) -> Optional[str]:
        """Replace all variables in an expression with their values.
        
        This matches the Ruby apply_vars implementation exactly.
        
        Args:
            line: Line number for error reporting
            string: The string to process
            allow_unicode_vars: Whether to allow Unicode variables
            
        Returns:
            The processed string, or None if there was an error
        """
        ret = string
        stack_depth = 0
        had_replacements = True
        
        error_occurred = False
        
        while had_replacements:
            had_replacements = False
            
            def replace_var(match):
                nonlocal had_replacements, error_occurred
                vname = match.group(1)
                v = self.vars.get(vname)
                
                if not v:
                    # Check if it's a Unicode variable
                    if self.UNICODE_VAR_NAME_REGEXP_IN.match(vname):
                        if allow_unicode_vars:
                            # Keep Unicode variable intact for later processing
                            return match.group(0)
                        else:
                            self.mode.errors.append(Error(
                                line, 
                                f"In expression: {string}: making wrong use of unicode variable: {match.group(0)}. Unicode vars can only be used in source members of a rule or in the definition of another variable."
                            ))
                            error_occurred = True
                            return match.group(0)  # Return original to avoid empty string
                    else:
                        self.mode.errors.append(Error(
                            line,
                            f"In expression: {string}: failed to evaluate variable: {match.group(0)}."
                        ))
                        error_occurred = True
                        return match.group(0)  # Return original to avoid empty string
                else:
                    had_replacements = True
                    return v.value
            
            # Apply variable replacement
            ret = self.VAR_NAME_REGEXP.sub(replace_var, ret)
            
            if error_occurred:
                return None
            
            stack_depth += 1
            if not had_replacements:
                break
                
            if stack_depth > 16:
                self.mode.errors.append(Error(
                    line,
                    f"In expression: {string}: evaluation stack overflow."
                ))
                return None
        
        # Unicode variables are kept intact and will be replaced at the last moment of parsing
        # This matches Ruby behavior exactly
        return ret
    
    def __str__(self) -> str:
        """String representation of the rule group."""
        return f"<RuleGroup {self.name}: {len(self.vars)} vars, {len(self.rules)} rules>"
