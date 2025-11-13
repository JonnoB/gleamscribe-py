"""ModeDebugContext implementation for Glaemscribe.

This is a port of the Ruby ModeDebugContext class, which provides
detailed tracing and debugging information during transcription.
"""

from __future__ import annotations
from typing import List


class ModeDebugContext:
    """Debug context for tracing transcription process.
    
    Tracks all stages of transcription:
    - Preprocessor output
    - Processor pathes (step-by-step transcription trace)
    - Processor output (final transcription results)
    - Postprocessor output
    - TTS output (if applicable)
    """
    
    def __init__(self):
        """Initialize debug context with empty tracking."""
        self.preprocessor_output: str = ""
        self.processor_pathes: List[List[str]] = []
        self.processor_output: List[str] = []
        self.postprocessor_output: str = ""
        self.tts_output: str = ""
    
    def add_processor_path(self, eaten: str, tokens: List[str], final_tokens: List[str]):
        """Add a processor path entry for debugging.
        
        Args:
            eaten: The characters that were consumed
            tokens: The intermediate tokens generated
            final_tokens: The final tokens after processing
        """
        self.processor_pathes.append([eaten, tokens, final_tokens])
    
    def clear(self):
        """Clear all debug information."""
        self.preprocessor_output = ""
        self.processor_pathes = []
        self.processor_output = []
        self.postprocessor_output = ""
        self.tts_output = ""
    
    def get_summary(self) -> str:
        """Get a summary of debug information.
        
        Returns:
            Formatted summary string
        """
        summary = []
        summary.append(f"=== Transcription Debug Summary ===")
        summary.append(f"Preprocessor output: {len(self.preprocessor_output)} chars")
        summary.append(f"Processor steps: {len(self.processor_pathes)}")
        summary.append(f"Processor output: {len(self.processor_output)} tokens")
        summary.append(f"Postprocessor output: {len(self.postprocessor_output)} chars")
        summary.append(f"TTS output: {len(self.tts_output)} chars")
        
        if self.processor_pathes:
            summary.append(f"\nFirst few processor steps:")
            for i, path in enumerate(self.processor_pathes[:5]):
                eaten, tokens, final_tokens = path
                summary.append(f"  {i+1}. '{eaten}' -> {tokens}")
        
        return "\n".join(summary)
    
    def __str__(self) -> str:
        """String representation of debug context."""
        return self.get_summary()
