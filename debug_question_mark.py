#!/usr/bin/env python3
from src.glaemscribe.parsers.mode_parser import ModeParser
import unicodedata

text = "Ai ! laurië lantar lassi súrinen ,"
print(f"Original: {repr(text)}")

# Test normalization
normalized = unicodedata.normalize('NFD', text)
processed = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn').lower()
print(f"After preprocessing: {repr(processed)}")

# Now transcribe
parser = ModeParser()
mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
mode.processor.finalize({})
success, result, debug = mode.transcribe(text)

print(f"\nResult has '?': {'?' in result}")
if '?' in result:
    idx = result.index('?')
    print(f"'?' at position {idx}")
    print(f"Context: {repr(result[max(0,idx-3):idx+4])}")
