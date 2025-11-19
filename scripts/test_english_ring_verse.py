"""Transcribe and render the Ring Verse in English Tengwar script.


N.B. English-Tengwar mode is not yet implemented!

This module demonstrates Tengwar transcription of Tolkien's Ring Verse using
the English Tengwar mode with eSpeak phonetic analysis. The transcribed text
is rendered as a PNG image using a Tengwar Unicode font.

The module performs the following steps:
    1. Loads the English-Tengwar-eSpeak mode from Glaemscribe
    2. Validates the mode with a test word
    3. Transcribes the complete Ring Verse to Tengwar Unicode characters
    4. Renders the result as a PNG image with proper line wrapping and layout

Typical usage:
    python script.py
"""


#!/usr/bin/env python3
"""Test English Tengwar transcription with the Ring Verse."""

from glaemscribe.parsers.mode_parser import ModeParser
from PIL import Image, ImageDraw, ImageFont
import os

# The Ring Verse in English
ring_verse = """Three Rings for the Elven-kings under the sky,
Seven for the Dwarf-lords in their halls of stone,
Nine for Mortal Men doomed to die,
One for the Dark Lord on his dark throne
In the Land of Mordor where the Shadows lie.
One Ring to rule them all, One Ring to find them ,
One Ring to bring them all and in the darkness bind them
In the Land of Mordor where the Shadows lie."""

def main():
    print("Loading English Tengwar mode...")
    from glaemscribe.resources import get_mode_path
    parser = ModeParser()
    mode = parser.parse(str(get_mode_path('english-tengwar-espeak')))
    
    if not mode:
        print("ERROR: Failed to load mode")
        return
    
    print(f"Mode loaded: {mode.name}")
    print(f"Mode has {len(mode.processor.rule_groups)} rule groups")
    
    # Finalize the mode
    mode.finalize({})
    
    print("\nTranscribing Ring Verse...")
    # Test with a simple word first
    test_word = "Three"
    print(f"\nTesting with: '{test_word}'")
    success_test, result_test, debug_test = mode.transcribe(test_word)
    print(f"Result: {result_test}")
    print(f"Debug: {debug_test}")
    
    success, result, debug = mode.transcribe(ring_verse)
    
    if not success:
        print(f"ERROR: Transcription failed: {result}")
        print(f"Debug info: {debug}")
        return
    
    print(f"Success! Transcribed {len(ring_verse)} characters to {len(result)} characters")
    print(f"\nTranscription result:")
    print(result)
    print(f"\nUnicode codepoints (first 50 chars):")
    for i, char in enumerate(result[:50]):
        print(f"  {i}: U+{ord(char):04X} ({char})")
    
    # Render to PNG
    print("\nRendering to PNG...")
    try:
        font_path = "src/glaemscribe/fonts/FreeMonoTengwar.ttf"
        font_size = 36
        font = ImageFont.truetype(font_path, font_size)
        
        # Split into lines
        lines = result.split('\n')
        
        # Calculate image size
        line_height = font_size + 10
        max_width = 0
        for line in lines:
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            max_width = max(max_width, line_width)
        
        img_width = max_width + 40
        img_height = len(lines) * line_height + 40
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw each line
        y = 20
        for line in lines:
            draw.text((20, y), line, font=font, fill='black')
            y += line_height

        # Ensure data directory exists
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, 'ring_verse_english_tengwar.png')
        img.save(output_file)
        print(f"Saved to: {output_file}")
        
    except Exception as e:
        print(f"ERROR rendering PNG: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
