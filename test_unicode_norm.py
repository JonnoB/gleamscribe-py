import unicodedata
text = "laurië"
normalized = unicodedata.normalize('NFD', text)
result = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn').lower()
print(f"Input: {text}")
print(f"Normalized: {result}")
print(f"Expected: laurie")
