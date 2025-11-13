"""Mode parser for .glaem files.

This parser uses the Glaeml parser to build an AST, then processes it
to create Mode objects with rules, options, and processors.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Callable
import os

from .glaeml import Parser, Document, Node, Error
from ..core.mode_enhanced import Mode, Option
from ..core.charset import Charset


class ModeParser:
    """Parses .glaem files into Mode objects."""
    
    def __init__(self):
        """Initialize the parser."""
        self.mode: Optional[Mode] = None
        self.errors: List[Error] = []
    
    def parse(self, file_path: str) -> Mode:
        """Parse a .glaem file and return a Mode object."""
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
        """Process the parsed AST to extract mode information."""
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
        """Extract basic mode metadata."""
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
        """Extract mode options."""
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
        """Extract charset references."""
        charset_nodes = doc.root_node.gpath("charset")
        
        for charset_element in charset_nodes:
            if not charset_element.args:
                continue
            
            charset_name = charset_element.args[0]
            is_default = len(charset_element.args) > 1 and charset_element.args[1] == "true"
            
            # For now, create a placeholder charset
            # In a full implementation, we'd use ResourceManager to load it
            placeholder_charset = Charset(name=charset_name, version="1.0.0")
            self.mode.add_charset(placeholder_charset, is_default)
        
        # Add warning if no default charset
        if not self.mode.default_charset:
            self.mode.warnings.append(Error(0, "No default charset defined!!"))
    
    def _extract_preprocessor(self, doc: Document):
        """Extract preprocessor rules."""
        preprocessor_nodes = doc.root_node.gpath("preprocessor")
        # TODO: Implement preprocessor parsing
        # For now, we'll skip this as it's complex
    
    def _extract_processor_rules(self, doc: Document):
        """Extract processor rules."""
        processor_rules_nodes = doc.root_node.gpath("processor.rules")
        # TODO: Implement rule group parsing
        # For now, we'll skip this as it's complex
    
    def _extract_postprocessor(self, doc: Document):
        """Extract postprocessor rules."""
        postprocessor_nodes = doc.root_node.gpath("postprocessor")
        # TODO: Implement postprocessor parsing
        # For now, we'll skip this as it's complex
