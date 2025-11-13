#!/usr/bin/env python3
"""Test the debug context functionality."""

from src.glaemscribe.parsers.mode_parser import ModeParser
from src.glaemscribe.core.mode_debug_context import ModeDebugContext

def test_debug_context():
    """Test that debug context provides detailed tracing."""
    
    print("=== Testing ModeDebugContext Class ===")
    
    # Test basic debug context functionality
    debug_context = ModeDebugContext()
    
    # Add some test processor paths
    debug_context.add_processor_path("h", ["AHA"], ["AHA"])
    debug_context.add_processor_path("e", ["*UNKNOWN"], ["*UNKNOWN"])
    debug_context.add_processor_path("1", ["NUM_1"], ["NUM_1"])
    
    print("Debug Context Summary:")
    print(debug_context.get_summary())
    
    print("\n" + "="*60)
    print("=== Testing Debug Context in Transcription ===")
    
    # Test with actual mode
    parser = ModeParser()
    mode = parser.parse("/home/jonno/glaemscribe-py/resources/glaemresources/modes/quenya-tengwar-classical.glaem")
    
    if mode and hasattr(mode, 'processor'):
        # Finalize the processor
        mode.processor.finalize({})
        
        # Test transcription with debug context
        test_cases = [
            "hello",
            "123",
            "hello123!",
            "a.b,c"
        ]
        
        for test_text in test_cases:
            print(f"\n--- Transcribing '{test_text}' ---")
            
            # Create debug context
            debug_context = ModeDebugContext()
            
            try:
                # Transcribe with debug context
                success, result, debug_context = mode.transcribe(test_text, debug_context=debug_context)
                
                print(f"Success: {success}")
                print(f"Result: {result[:100]}...")  # Show first 100 chars
                print(f"Processor steps: {len(debug_context.processor_pathes)}")
                
                # Show first few processor steps
                if debug_context.processor_pathes:
                    print("First few steps:")
                    for i, path in enumerate(debug_context.processor_pathes[:5]):
                        eaten, tokens, final_tokens = path
                        print(f"  {i+1}. '{eaten}' -> {tokens}")
                
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("=== Testing Debug Context Features ===")
        
        # Test debug context features
        debug_context = ModeDebugContext()
        debug_context.preprocessor_output = "test preprocessing"
        debug_context.postprocessor_output = "test postprocessing"
        debug_context.tts_output = "test tts"
        
        print("Full debug context with all features:")
        print(debug_context)

if __name__ == "__main__":
    test_debug_context()
