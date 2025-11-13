#!/usr/bin/env python3
from src.glaemscribe.parsers.mode_parser import ModeParser
from src.glaemscribe.core.mode_debug_context import ModeDebugContext

parser = ModeParser()
mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
mode.processor.finalize({})

text = "ai ! laurie lantar lassi surinen ,"
debug = ModeDebugContext()
tokens = mode.processor.transcribe(text, debug)

# Get unique tokens
unique_tokens = sorted(set(t for t in tokens if t and t != '\\' and not t.startswith('*')))
print("Unique tokens needed:")
for tok in unique_tokens:
    print(f"  {tok}")

# Check which ones are in the charset
charset = mode.default_charset
print("\nChecking charset mappings:")
for tok in unique_tokens:
    char_code = charset.characters.get(tok)
    if char_code:
        print(f"  {tok}: 0x{char_code}")
    else:
        print(f"  {tok}: NOT FOUND IN CHARSET")
