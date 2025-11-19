"""Mode parser for .glaem transcription mode files.

This module provides parsing for .glaem mode files, which define transcription
rules for converting text between writing systems (e.g., Quenya → Tengwar).

The parser reads .glaem files, builds an Abstract Syntax Tree (AST) using the
Glaeml parser, and processes it to create Mode objects containing:
- Metadata (language, writing system, version, authors)
- Options (user-configurable settings)
- Charsets (character set definitions)
- Preprocessor rules (text normalization)
- Processor rules (transcription logic)
- Postprocessor rules (output formatting)

Example:
    >>> from glaemscribe.parsers import ModeParser
    >>> from glaemscribe.resources import get_mode_path
    >>> 
    >>> parser = ModeParser()
    >>> mode = parser.parse(str(get_mode_path('quenya-tengwar-classical')))
    >>> mode.processor.finalize({})
    >>> success, result, debug = mode.transcribe("aiya")
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Callable
import os
import re

from .glaeml import Parser, Document, Node, Error
from ..core.mode_enhanced import Mode, Option
from ..core.charset import Charset
from .charset_parser import CharsetParser
from ..core.rule_group import RuleGroup, CodeLine, CodeBlock, CodeLinesTerm
from ..core.transcription_processor import TranscriptionProcessor
from ..core.post_processor.base import TranscriptionPreProcessor
from ..core.pre_processor_operators import SubstitutePreProcessorOperator, RxSubstitutePreProcessorOperator


class ModeParser:
    """Parses .glaem mode files into Mode objects.
    
    The ModeParser reads .glaem files (Glaemscribe mode definition files) and
    converts them into Mode objects that can perform transcriptions. It handles:
    
    - File reading and parsing
    - AST processing
    - Metadata extraction (language, version, authors)
    - Option definitions (user-configurable settings)
    - Charset loading (character set definitions)
    - Rule extraction (preprocessor, processor, postprocessor)
    - Error collection and reporting
    
    The parser automatically loads referenced charset files and validates
    the mode structure.
    
    Attributes:
        mode: The Mode object being constructed (None until parse() is called)
        errors: List of parsing errors encountered
    
    Examples:
        >>> # Parse a mode file
        >>> parser = ModeParser()
        >>> mode = parser.parse('path/to/mode.glaem')
        >>> 
        >>> # Check for errors
        >>> if mode.errors:
        ...     print(f"Errors: {mode.errors}")
        >>> 
        >>> # Use the mode
        >>> mode.processor.finalize({})
        >>> success, result, debug = mode.transcribe("text")
        
        >>> # Parse using package resources
        >>> from glaemscribe.resources import get_mode_path
        >>> mode_path = get_mode_path('quenya-tengwar-classical')
        >>> mode = parser.parse(str(mode_path))
    """
    
    def __init__(self):
        """Initialize the mode parser.
        
        Creates a new parser instance with empty mode and error list.
        The mode will be populated when parse() is called.
        """
        self.mode: Optional[Mode] = None
        self.errors: List[Error] = []
    
    def parse(self, file_path: str) -> Mode:
        """Parse a .glaem mode file and return a Mode object.
        
        Reads the specified .glaem file, parses its contents, and constructs
        a Mode object with all rules, options, and charsets. The mode name is
        derived from the filename.
        
        The parsing process:
        1. Reads the file content
        2. Parses with Glaeml parser to build AST
        3. Extracts metadata (version, language, authors, etc.)
        4. Extracts and validates options
        5. Loads referenced charset files
        6. Extracts preprocessor rules
        7. Extracts processor (transcription) rules
        8. Extracts postprocessor rules
        
        Args:
            file_path: Path to the .glaem mode file to parse
            
        Returns:
            Mode object containing all parsed rules and metadata.
            Check mode.errors for any parsing errors.
            
        Raises:
            FileNotFoundError: If the file cannot be read
            
        Examples:
            >>> parser = ModeParser()
            >>> mode = parser.parse('modes/quenya-tengwar-classical.glaem')
            >>> print(mode.name)
            'quenya-tengwar-classical'
            >>> print(mode.version)
            '0.9.12'
            
            >>> # Check for errors
            >>> if mode.errors:
            ...     for error in mode.errors:
            ...         print(f"Error: {error}")
            
            >>> # Use with package resources
            >>> from glaemscribe.resources import get_mode_path
            >>> mode = parser.parse(str(get_mode_path('quenya')))
        """
        self.errors = []
        
        # Extract mode name from filename
        mode_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Create the mode object
        self.mode = Mode(mode_name)
        
        # Read and parse the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            raise FileNotFoundError(f"Could not read file {file_path}: {e}") from e
        
        # Parse with Glaeml parser
        glaeml_parser = Parser()
        doc = glaeml_parser.parse(content)
        
        if doc.has_errors():
            self.errors.extend(doc.errors)
        
        # Process the AST
        self._process_ast(doc)
        
        # Copy errors to mode
        self.mode.errors.extend(self.errors)
        
        return self.mode
    
    def _process_ast(self, doc: Document):
        """Process the parsed AST to extract mode information.
        
        Orchestrates the extraction of all mode components from the parsed
        document in the correct order:
        1. Metadata (version, language, etc.)
        2. Options (user settings)
        3. Charsets (character definitions)
        4. Preprocessor (text normalization)
        5. Processor (transcription rules)
        6. Postprocessor (output formatting)
        
        Args:
            doc: Parsed Glaeml document containing the AST
        """
        if not doc.root_node:
            return
        
        # Extract metadata
        self._extract_metadata(doc)
        
        # Extract options
        self._extract_options(doc)
        
        # Extract charset references
        self._extract_charsets(doc)
        
        # Extract preprocessor
        self._extract_preprocessor(doc)
        
        # Extract processor rules
        self._extract_processor_rules(doc)
        
        # Extract postprocessor
        self._extract_postprocessor(doc)
    
    def _extract_metadata(self, doc: Document):
        """Extract basic mode metadata from the document.
        
        Extracts metadata fields including:
        - version: Mode version number
        - language: Source language (e.g., "Quenya")
        - writing: Target writing system (e.g., "Tengwar")
        - mode: Mode description
        - authors: Mode authors
        - world: Setting/world (e.g., "arda")
        - invention: Creator (e.g., "jrrt")
        - raw_mode: Reference to raw mode for fallback
        
        Args:
            doc: Parsed Glaeml document
        """
        root = doc.root_node
        
        # Version
        version_nodes = root.gpath("version")
        if version_nodes:
            self.mode.version = version_nodes[0].args[0] if version_nodes[0].args else ""
        
        # Basic info
        for field in ["language", "writing", "mode", "authors"]:
            nodes = root.gpath(field)
            if nodes:
                value = " ".join(nodes[0].args)
                if field == "mode":
                    self.mode.human_name = value
                else:
                    setattr(self.mode, field, value)
        
        # Additional metadata
        for field in ["world", "invention"]:
            nodes = root.gpath(field)
            if nodes:
                setattr(self.mode, field, nodes[0].args[0] if nodes[0].args else "")
        
        # Raw mode reference
        raw_mode_nodes = root.gpath("raw_mode")
        if raw_mode_nodes:
            self.mode.raw_mode_name = raw_mode_nodes[0].args[0] if raw_mode_nodes[0].args else None
    
    def _extract_options(self, doc: Document):
        """Extract mode options (user-configurable settings).
        
        Parses option definitions from the mode file. Options allow users
        to customize transcription behavior (e.g., vowel placement, tehta shapes).
        
        Each option has:
        - name: Option identifier
        - type: Option type (radio, checkbox, etc.)
        - default_value: Default setting
        - values: Available values with descriptions
        
        Args:
            doc: Parsed Glaeml document
        """
        options_nodes = doc.root_node.gpath("options")
        if not options_nodes:
            return
        
        options_node = options_nodes[0]
        
        # Process each option
        for option_element in options_node.gpath("option"):
            # Handle simple options: \option name value
            if len(option_element.args) >= 2:
                option_name = option_element.args[0]
                default_value = option_element.args[1]
                
                # Find values
                values = {}
                value_elements = option_element.gpath("value")
                for value_element in value_elements:
                    if len(value_element.args) >= 2:
                        value_name = value_element.args[0]
                        value_num = int(value_element.args[1]) if value_element.args[1].isdigit() else 1
                        values[value_name] = value_num
                
                # Check for radio button
                is_radio = bool(option_element.gpath("radio"))
                
                # Check visibility condition
                visibility = None
                visible_elements = option_element.gpath("visible_when")
                if visible_elements:
                    visibility = visible_elements[0].args[0] if visible_elements[0].args else None
                
                # Create option
                option = Option(
                    mode=self.mode,
                    name=option_name,
                    default_value=default_value,
                    values=values,
                    line=option_element.line,
                    visibility=visibility,
                    is_radio=is_radio
                )
                
                self.mode.add_option(option)
    
    def _extract_charsets(self, doc: Document):
        """Extract charset references and load charset files.
        
        Parses charset declarations and loads the corresponding .cst files
        from the package resources. Each charset defines character mappings
        for a specific font or encoding.
        
        Charsets are declared with:
        - name: Charset identifier (e.g., "tengwar_freemono")
        - is_default: Whether this is the default charset
        
        The parser automatically loads charset files using get_charset_path()
        and adds them to the mode. If a charset file is not found, a placeholder
        is created and a warning is issued.
        
        Args:
            doc: Parsed Glaeml document
        """
        charset_nodes = doc.root_node.gpath("charset")
        
        for charset_element in charset_nodes:
            if not charset_element.args:
                continue
            
            charset_name = charset_element.args[0]
            is_default = len(charset_element.args) > 1 and charset_element.args[1] == "true"
            
            # Load the actual charset file from package resources
            try:
                from ..resources import get_charset_path
                charset_file = get_charset_path(charset_name)
                
                charset_parser = CharsetParser()
                loaded_charset = charset_parser.parse(str(charset_file))
                self.mode.add_charset(loaded_charset, is_default)
                    
            except FileNotFoundError:
                # Fallback to placeholder if file not found
                print(f"Warning: Charset file {charset_name}.cst not found, using placeholder")
                placeholder_charset = Charset(name=charset_name, version="1.0.0")
                self.mode.add_charset(placeholder_charset, is_default)
            except Exception as e:
                print(f"Error loading charset {charset_name}: {e}")
                placeholder_charset = Charset(name=charset_name, version="1.0.0")
                self.mode.add_charset(placeholder_charset, is_default)
        
        # Add warning if no default charset
        if not self.mode.default_charset:
            self.mode.warnings.append(Error(0, "No default charset defined!!"))
    
    def _extract_preprocessor(self, doc: Document):
        """Extract preprocessor operators for text normalization.
        
        The preprocessor handles text preparation before transcription:
        - downcase: Convert to lowercase
        - upcase: Convert to uppercase
        - substitute: Simple text substitutions
        - rx_substitute: Regex-based substitutions
        
        Preprocessor operations run before the main transcription rules
        and are used for normalization, cleanup, and text preparation.
        
        Args:
            doc: Parsed Glaeml document
        """
        # Create the preprocessor
        self.mode.pre_processor = TranscriptionPreProcessor(self.mode)
        
        preprocessor_nodes = doc.root_node.gpath("preprocessor")
        if not preprocessor_nodes:
            return
        
        preprocessor_node = preprocessor_nodes[0]
        
        # Process each element in the preprocessor block
        for child in preprocessor_node.children:
            if child.name == "substitute":
                # Create substitute operator
                operator = SubstitutePreProcessorOperator(self.mode, child)
                self.mode.pre_processor.operators.append(operator)
            
            elif child.name == "rxsubstitute":
                # Create regex substitute operator
                operator = RxSubstitutePreProcessorOperator(self.mode, child)
                self.mode.pre_processor.operators.append(operator)
            
            elif child.is_text():
                # Handle inline text commands (fallback)
                line = child.args[0].strip()
                if line.startswith('\\substitute '):
                    parts = line.split(None, 2)
                    if len(parts) == 3:
                        # Create a fake node for the operator
                        fake_node = Node(child.line, "substitute", "substitute")
                        fake_node.args = [parts[1], parts[2]]
                        operator = SubstitutePreProcessorOperator(self.mode, fake_node)
                        self.mode.pre_processor.operators.append(operator)
                
                elif line.startswith('\\rxsubstitute '):
                    parts = line.split(None, 2)
                    if len(parts) == 3:
                        pattern = parts[1]
                        replacement = parts[2]
                        # Remove quotes if present
                        if pattern.startswith('"') and pattern.endswith('"'):
                            pattern = pattern[1:-1]
                        if replacement.startswith('"') and replacement.endswith('"'):
                            replacement = replacement[1:-1]
                        # Create a fake node for the operator
                        fake_node = Node(child.line, "rxsubstitute", "rxsubstitute")
                        fake_node.args = [pattern, replacement]
                        operator = RxSubstitutePreProcessorOperator(self.mode, fake_node)
                        self.mode.pre_processor.operators.append(operator)
    
    def _extract_processor_rules(self, doc: Document):
        """Extract processor (transcription) rules.
        
        The processor contains the main transcription logic organized into
        rule groups. Each rule group has:
        - name: Group identifier
        - rules: List of transcription rules
        - conditionals: Optional if/elsif/else blocks
        
        Rules define pattern matching and replacement for transcription.
        They can include:
        - Simple patterns: "a" → "TEHTA_A"
        - Complex patterns: "[aeiou]" → vowel mappings
        - Conditionals: Different rules based on options
        - Cross-rules: Rules spanning multiple characters
        
        Args:
            doc: Parsed Glaeml document
        """
        # Find the processor block
        processor_nodes = doc.root_node.gpath("processor")
        if not processor_nodes:
            return
        
        processor_node = processor_nodes[0]
        
        # Create the transcription processor
        self.mode.processor = TranscriptionProcessor(self.mode)
        
        # Find rules blocks within processor
        rules_nodes = processor_node.gpath("rules")
        
        for rules_element in rules_nodes:
            if not rules_element.args:
                continue
            
            rule_group_name = rules_element.args[0]
            rule_group = RuleGroup(self.mode, rule_group_name)
            
            # Store rule group in mode
            if not hasattr(self.mode, 'rule_groups'):
                self.mode.rule_groups = {}
            self.mode.rule_groups[rule_group_name] = rule_group
            
            # Add to processor
            self.mode.processor.add_rule_group(rule_group_name, rule_group)
            
            # Process the rules in this group
            self._process_rule_group_content(rules_element, rule_group)
    
    def _process_rule_group_content(self, element: Node, rule_group: RuleGroup):
        """Process the content of a rule group, handling conditionals.
        
        Traverses the rule group's AST, processing:
        - Text nodes: Individual transcription rules
        - If/elsif/else blocks: Conditional rule application
        - Nested structures: Complex rule hierarchies
        
        This method uses a recursive approach to handle nested conditionals
        and build the rule group's code block structure.
        
        Args:
            element: AST node containing rule group content
            rule_group: RuleGroup object to populate with rules
        """
        
        def process_text(parent_block: CodeBlock, text_element: Node):
            """Process text elements containing rules - matches Ruby implementation."""
            # Check if the last term is a CodeLinesTerm, if not create one
            term = None
            if parent_block.terms:
                term = parent_block.terms[-1]
            
            if not term or not hasattr(term, 'is_code_lines'):
                term = CodeLinesTerm(parent_block)
                parent_block.add_term(term)
            
            # Process all lines in the text element
            if text_element.args:
                lines = text_element.args[0].split('\n')
                lcount = text_element.line
                
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('**'):
                        continue  # Skip comments and empty lines
                    
                    # Add the code line to the current CodeLinesTerm
                    code_line = CodeLine(line, lcount)
                    term.code_lines.append(code_line)
                    lcount += 1
        
        def process_element(parent_block: CodeBlock, element: Node):
            """Process element nodes - handles macros, conditionals, etc."""
            
            if element.name == 'macro':
                # Handle macro definition: \beg macro name arg1 arg2
                if not element.args or len(element.args) < 1:
                    self.errors.append(Error(element.line, "Macro misses a name."))
                    return
                
                macro_args = element.args.copy()
                macro_name = macro_args.pop(0)
                
                # Validate argument names
                for arg in macro_args:
                    if not re.match(r'[0-9A-Z_]+', arg):
                        self.errors.append(Error(element.line, f"Macro argument name {arg} has wrong format."))
                        return
                
                # Check for macro redefinition
                if macro_name in rule_group.macros:
                    self.errors.append(Error(element.line, f"Redefining macro {macro_name}."))
                    return
                
                # Create macro object
                from ..core.macro import Macro
                macro = Macro(rule_group, macro_name, macro_args)
                
                # Process macro content
                macro_context = {
                    'owner': macro,
                    'root_element': element,
                    'rule_group': rule_group
                }
                macro.traverse_if_tree(element, process_text, process_element)
                
                # Store the macro
                rule_group.add_macro(macro)
                
            elif element.name == 'deploy':
                # Handle macro deployment: \deploy macro_name arg1 arg2
                if not element.args or len(element.args) < 1:
                    self.errors.append(Error(element.line, "Deploy misses a macro name."))
                    return
                
                deploy_args = element.args.copy()
                macro_name = deploy_args.pop(0)
                macro = rule_group.macros.get(macro_name)
                
                if not macro:
                    self.errors.append(Error(element.line, f"Macro '{macro_name}' not found in rule group '{rule_group.name}'."))
                    return
                
                # Check argument count
                expected_args = len(macro.arg_names)
                given_args = len(deploy_args)
                if expected_args != given_args:
                    self.errors.append(Error(element.line, f"Macro '{macro_name}' takes {expected_args} arguments, not {given_args}."))
                    return
                
                # Create macro deployment term
                from ..core.macro import MacroDeployTerm
                macro_deploy = MacroDeployTerm(
                    macro=macro,
                    line=element.line,
                    parent_code_block=parent_block,
                    arg_value_expressions=deploy_args
                )
                parent_block.add_term(macro_deploy)
                
            elif element.name in ['if', 'elsif', 'else', 'endif']:
                # Handle conditional elements - these should be processed by traverse_if_tree
                # But we need to let the existing infrastructure handle them
                pass
                
            else:
                # Unknown element
                self.errors.append(Error(element.line, f"Unknown directive {element.name}."))
        
        # Use the traverse_if_tree method to handle conditionals
        rule_group.traverse_if_tree(element, process_text, process_element)
    
    def _extract_postprocessor(self, doc: Document):
        """Extract postprocessor rules for output formatting.
        
        The postprocessor handles final output formatting after transcription:
        - resolve_virtuals: Resolve virtual character placeholders
        - optimize_diacritics: Optimize diacritic placement
        - Custom operators: Mode-specific formatting
        
        Postprocessor operations run after transcription rules and are used
        for cleanup, optimization, and final formatting of the output.
        
        Args:
            doc: Parsed Glaeml document
        """
        postprocessor_nodes = doc.root_node.gpath("postprocessor")
        if not postprocessor_nodes:
            return
        
        postprocessor_node = postprocessor_nodes[0]
        
        # Find all operator directives in postprocessor
        for operator_element in postprocessor_node.children:
            if operator_element.name == "resolve_virtuals":
                # Add the resolve virtuals operator
                from ..core.post_processor.resolve_virtuals import ResolveVirtualsPostProcessorOperator
                resolve_virtuals_op = ResolveVirtualsPostProcessorOperator(self.mode)
                self.mode.post_processor.operators.append(resolve_virtuals_op)
            else:
                self.errors.append(Error(operator_element.line, f"Unknown postprocessor operator: {operator_element.name}"))
