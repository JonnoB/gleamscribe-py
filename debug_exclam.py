#!/usr/bin/env python3
from src.glaemscribe.parsers.mode_parser import ModeParser

parser = ModeParser()
mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
mode.processor.finalize({})

# Check what PUNCT_EXCLAM maps to
charset = mode.default_charset
code = charset.characters.get('PUNCT_EXCLAM')
print(f"PUNCT_EXCLAM code in charset: {repr(code)}")

if code:
    # Try to convert it
    from src.glaemscribe.parsers.tengwar_font_mapping import map_font_code_to_unicode
    try:
        code_int = int(code, 16)
        unicode_char = map_font_code_to_unicode(code_int)
        print(f"Code as int: 0x{code_int:x}")
        print(f"Mapped to Unicode: {repr(unicode_char)} (U+{ord(unicode_char):04X})")
    except Exception as e:
        print(f"Error converting: {e}")

# Now transcribe the full text and check tokens
text = "Ai ! laurië lantar lassi súrinen ,"
success, result, debug = mode.transcribe(text)
print(f"\nFull transcription: {repr(result)}")
print(f"\nProcessor tokens (first 20):")
for i, tok in enumerate(debug.processor_output[:20]):
    if tok:
        print(f"  {i}: {repr(tok)}")
        
# Find which token produces '?'
print(f"\nLooking for '?' in result at position 5...")
print(f"Result[5] = {repr(result[5])}")
