"""Base post-processor classes for Glaemscribe.

This is a port of the Ruby post-processor system, which handles
conversion of transcription tokens to actual Unicode characters
using charset resolution and other post-processing operations.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

from ...parsers.glaeml import Node


UNKNOWN_CHAR_OUTPUT = "?"


class PrePostProcessorOperator(ABC):
    """Base class for pre/post-processor operators.
    
    Matches Ruby's PrePostProcessorOperator class exactly.
    """
    
    def __init__(self, mode, glaeml_element: Node):
        """Initialize the operator.
        
        Args:
            mode: The mode instance
            glaeml_element: The GLAEML element for this operator
        """
        self.mode = mode
        self.glaeml_element = glaeml_element
        self.finalized_glaeml_element: Optional[Node] = None
    
    def eval_arg(self, arg: str, trans_options: Dict[str, Any]) -> Any:
        """Evaluate an argument expression.
        
        Args:
            arg: Argument string to evaluate
            trans_options: Transcription options
            
        Returns:
            Evaluated argument or original string
        """
        if arg is None:
            return None
            
        # TODO: Implement \eval expressions if needed
        # For now, just return the argument as-is
        return arg
    
    def finalize_glaeml_element(self, ge: Node, trans_options: Dict[str, Any]) -> Node:
        """Finalize a GLAEML element by evaluating its arguments.
        
        Args:
            ge: GLAEML element to finalize
            trans_options: Transcription options
            
        Returns:
            Finalized GLAEML element
        """
        # Evaluate arguments
        if hasattr(ge, 'args') and ge.args:
            ge.args = [self.eval_arg(arg, trans_options) for arg in ge.args]
        
        # Recursively finalize children
        if hasattr(ge, 'children') and ge.children:
            for child in ge.children:
                self.finalize_glaeml_element(child, trans_options)
        
        return ge
    
    def finalize(self, trans_options: Dict[str, Any]):
        """Finalize the operator.
        
        Args:
            trans_options: Transcription options
        """
        # Clone and finalize the GLAEML element
        if self.glaeml_element:
            self.finalized_glaeml_element = self.finalize_glaeml_element(
                self.glaeml_element.clone(), trans_options
            )
    
    @abstractmethod
    def apply(self, *args, **kwargs) -> Any:
        """Apply the operator - must be implemented by subclasses."""
        pass


class PreProcessorOperator(PrePostProcessorOperator):
    """Base class for pre-processor operators."""
    pass


class PostProcessorOperator(PrePostProcessorOperator):
    """Base class for post-processor operators."""
    pass


class TranscriptionPrePostProcessor:
    """Base class for pre/post-processor systems.
    
    Manages a collection of operators and applies them in sequence.
    """
    
    def __init__(self, mode):
        """Initialize the processor.
        
        Args:
            mode: The mode instance
        """
        self.mode = mode
        self.operators: List[PrePostProcessorOperator] = []
    
    def finalize(self, trans_options: Dict[str, Any]):
        """Finalize all operators.
        
        Args:
            trans_options: Transcription options
        """
        # Finalize each operator
        for operator in self.operators:
            operator.finalize(trans_options)


class TranscriptionPreProcessor(TranscriptionPrePostProcessor):
    """Pre-processor that applies operators to input text."""
    
    def apply(self, text: str) -> str:
        """Apply all pre-processor operators to text.
        
        Args:
            text: Input text to process
            
        Returns:
            Processed text
        """
        result = text
        for operator in self.operators:
            result = operator.apply(result)
        return result


class TranscriptionPostProcessor(TranscriptionPrePostProcessor):
    """Post-processor that converts tokens to Unicode characters.
    
    This is the key class that converts token names like "TELCO" 
    to actual Tengwar Unicode characters using the charset.
    """
    
    def __init__(self, mode):
        """Initialize the post-processor.
        
        Args:
            mode: The mode instance
        """
        super().__init__(mode)
        self.out_space: Optional[List[str]] = None
    
    def apply(self, tokens: List[str], out_charset) -> str:
        """Apply post-processing to convert tokens to Unicode string.
        
        This matches Ruby's TranscriptionPostProcessor#apply method exactly.
        
        Args:
            tokens: List of transcription tokens
            out_charset: Charset for character resolution
            
        Returns:
            Final Unicode string
        """
        # Cleanup the output by removing empty tokens and structural markers
        tokens = [tok for tok in tokens if tok != "" and tok != "\\"]
        
        # Apply all operators
        for operator in self.operators:
            tokens = operator.apply(tokens, out_charset)
        
        # Handle out_space configuration
        out_space_str = " "
        if self.out_space and out_charset:
            out_space_str = "".join([
                out_charset.get_character(token) if out_charset.has_character(token) else UNKNOWN_CHAR_OUTPUT
                for token in self.out_space
            ])
        
        # Convert tokens to characters
        result = ""
        for token in tokens:
            if token == "":
                continue
            elif token == "*UNKNOWN":
                result += UNKNOWN_CHAR_OUTPUT
            elif token == "*SPACE":
                result += out_space_str
            elif token == "*LF":
                result += "\n"
            else:
                # This is the key line - convert token to charset character!
                result += out_charset.get_character(token) if out_charset.has_character(token) else UNKNOWN_CHAR_OUTPUT
        
        return result
