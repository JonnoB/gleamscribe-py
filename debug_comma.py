#!/usr/bin/env python3
from src.glaemscribe.parsers.mode_parser import ModeParser

parser = ModeParser()
mode = parser.parse("resources/glaemresources/modes/quenya-tengwar-classical.glaem")
mode.processor.finalize({})

text = "Ai ! laurië lantar lassi súrinen ,"
success, result, debug = mode.transcribe(text)

expected = '\ue02a\uec42 \ue065 \ue900\ue02b\uec41\ue020\ue02a\ue02c\ue020 \ue023\ue02b\uec41\ue013\uec42\ue010\ue02c \ue023\ue02b\uec41\ue025\uec62\ue010 \ue026\uec42\ue020\uec62\ue010\ue013\ue900\ue013 ⸱'

print(f"Expected length: {len(expected)}")
print(f"Got length: {len(result)}")
print(f"\nExpected: {repr(expected)}")
print(f"Got:      {repr(result)}")
print(f"\nLast 5 chars expected: {[hex(ord(c)) for c in expected[-5:]]}")
print(f"Last 5 chars got:      {[hex(ord(c)) for c in result[-5:]]}")

# Find where they diverge
for i in range(min(len(expected), len(result))):
    if expected[i] != result[i]:
        print(f"\nFirst difference at position {i}:")
        print(f"  Expected: {hex(ord(expected[i]))}")
        print(f"  Got: {hex(ord(result[i]))}")
        break
else:
    if len(result) > len(expected):
        print(f"\nExtra characters at end: {[hex(ord(c)) for c in result[len(expected):]]}")
