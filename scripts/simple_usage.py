#!/usr/bin/env python3
"""Simple usage examples for the Glaemscribe library.

This demonstrates the easy-to-use high-level API.
"""

from glaemscribe import transcribe, list_modes

# Example 1: Simple Quenya transcription
print("Example 1: Quenya transcription")
print("-" * 40)
quenya_text = "Elen síla lúmenn' omentielvo"
result = transcribe(quenya_text, mode="quenya")
print(f"Input:  {quenya_text}")
print(f"Output: {result}")
print()

# Example 2: Sindarin transcription
print("Example 2: Sindarin transcription")
print("-" * 40)
sindarin_text = "mellon"
result = transcribe(sindarin_text, mode="sindarin")
print(f"Input:  {sindarin_text}")
print(f"Output: {result}")
print()

# Example 3: Using mode aliases
print("Example 3: Mode aliases")
print("-" * 40)
text = "aiya"
# These all work the same:
result1 = transcribe(text, mode="quenya")
result2 = transcribe(text, mode="quenya-classical")
result3 = transcribe(text, mode="quenya-tengwar-classical")
print(f"Input: {text}")
print(f"All produce: {result1}")
print()

# Example 4: List available modes
print("Example 4: Available modes")
print("-" * 40)
modes = list_modes()
print("Available transcription modes:")
for mode in sorted(modes):
    if not mode.endswith("-espeak") and not mode.startswith("raw"):
        print(f"  - {mode}")
print()

# Example 5: Famous Quenya phrases
print("Example 5: Famous phrases")
print("-" * 40)
phrases = [
    "Elen síla lúmenn' omentielvo",  # "A star shines on the hour of our meeting"
    "Namárië",  # "Farewell"
    "Aiya Eärendil elenion ancalima",  # "Hail Eärendil, brightest of stars"
]

for phrase in phrases:
    result = transcribe(phrase, mode="quenya")
    print(f"{phrase}")
    print(f"  → {result}")
    print()
