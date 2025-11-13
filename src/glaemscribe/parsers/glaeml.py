"""Glaeml parser for .glaem and .cst files.

This is a Python port of the Glaeml parser from the original Glaemscribe project.
It parses the custom markup language into an Abstract Syntax Tree (AST).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the Glaeml AST."""
    TEXT = 0
    ELEMENT_INLINE = 1
    ELEMENT_BLOCK = 2


@dataclass
class Error:
    """Represents a parsing error."""
    line: int
    message: str
    
    def __str__(self) -> str:
        return f"Line {self.line}: {self.message}"


@dataclass
class Node:
    """A node in the Glaeml AST."""
    line: int
    type: NodeType
    name: str
    args: List[str] = field(default_factory=list)
    children: List[Node] = field(default_factory=list)
    
    def is_text(self) -> bool:
        """Check if this node is a text node."""
        return self.type == NodeType.TEXT
    
    def is_element(self) -> bool:
        """Check if this node is an element node."""
        return self.type in (NodeType.ELEMENT_INLINE, NodeType.ELEMENT_BLOCK)
    
    def gpath(self, name: str) -> List[Node]:
        """Get all descendant nodes with the given name."""
        result = []
        for child in self.children:
            if child.is_element() and child.name == name:
                result.append(child)
            result.extend(child.gpath(name))
        return result
    
    def clone(self) -> Node:
        """Create a deep copy of this node."""
        new_node = Node(self.line, self.type, self.name)
        new_node.args = self.args.copy()
        new_node.children = [child.clone() for child in self.children]
        return new_node


@dataclass
class Document:
    """The root document containing the parsed AST."""
    errors: List[Error] = field(default_factory=list)
    root_node: Optional[Node] = None
    
    def has_errors(self) -> bool:
        """Check if the document has any parsing errors."""
        return len(self.errors) > 0


class Parser:
    """Parses Glaeml markup into an AST."""
    
    def __init__(self):
        """Initialize the parser."""
        self.line_number = 0
        self.pos = 0
        self.content = ""
        self.lines = []
    
    def parse(self, content: str) -> Document:
        """Parse Glaeml content into a Document."""
        self.content = content
        self.lines = content.split('\n')
        self.line_number = 0
        self.pos = 0
        
        doc = Document()
        
        # Create root node
        root = Node(0, NodeType.ELEMENT_BLOCK, "root")
        
        # Parse the content
        self._parse_content(root, doc)
        
        doc.root_node = root
        return doc
    
    def _parse_content(self, parent: Node, doc: Document):
        """Parse content and add nodes to parent."""
        while self.line_number < len(self.lines):
            line = self.lines[self.line_number]
            self.line_number += 1
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('**'):
                continue
            
            # Parse commands starting with \
            if line.strip().startswith('\\'):
                self._parse_command(line, parent, doc)
            else:
                # Parse text content
                if line.strip():
                    text_node = Node(self.line_number, NodeType.TEXT, "text")
                    text_node.args = [line.strip()]
                    parent.children.append(text_node)
    
    def _parse_command(self, line: str, parent: Node, doc: Document):
        """Parse a command line with proper quoted argument handling."""
        line = line.strip()
        
        # Remove the leading backslash
        cmd_and_args = line[1:]
        
        # Parse arguments with quoted string support
        import shlex
        try:
            args = shlex.split(cmd_and_args)
        except ValueError as e:
            # Fallback to simple split if shlex fails
            args = cmd_and_args.split()
            doc.errors.append(Error(self.line_number, f"Warning: Failed to parse arguments: {e}"))
        
        if not args:
            cmd = "unknown"
            cmd_args = []
        else:
            cmd = args[0]
            cmd_args = args[1:] if len(args) > 1 else []
        
        # Create node - only 'beg' creates a block, everything else is inline
        node_type = NodeType.ELEMENT_BLOCK if cmd == 'beg' else NodeType.ELEMENT_INLINE
        node = Node(self.line_number, node_type, cmd)
        node.args = cmd_args
        parent.children.append(node)
        
        # Handle block commands - only 'beg' creates a new scope
        if cmd == 'beg':
            self._parse_block(node, doc)
    
    def _parse_block(self, parent: Node, doc: Document):
        """Parse a block of content."""
        # For \beg blocks, the first argument is the block type
        block_type = parent.args[0] if parent.args else "unknown"
        parent.name = block_type
        parent.type = NodeType.ELEMENT_BLOCK
        
        while self.line_number < len(self.lines):
            line = self.lines[self.line_number]
            
            # Check for end command
            if line.strip().startswith('\\end'):
                self.line_number += 1
                break
            
            # Parse nested content
            self._parse_content(parent, doc)
