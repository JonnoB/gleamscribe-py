#!/usr/bin/env python3

"""Check charset codes to understand the mapping."""

from glaemscribe.parsers.charset_parser import CharsetParser

def compare_charsets():
    """Compare ds vs guni charset codes."""
    
    # Parse both charsets
    ds_parser = CharsetParser()
    ds_charset = ds_parser.parse("resources/glaemresources/charsets/tengwar_ds_sindarin.cst")
    
    guni_parser = CharsetParser()
    guni_charset = guni_parser.parse("resources/glaemresources/charsets/tengwar_guni_sindarin.cst")
    
    print("=== TELCO Comparison ===")
    if "TELCO" in ds_charset.characters:
        ds_telco = ds_charset.characters["TELCO"]
        print(f"DS TELCO: '{ds_telco}' (U+{ord(ds_telco):04X})")
    
    if "TELCO" in guni_charset.characters:
        guni_telco = guni_charset.characters["TELCO"]
        print(f"GUNI TELCO: '{guni_telco}' (U+{ord(guni_telco):04X})")
    
    print(f"\nExpected TELCO:  (U+E02A)")
    
    print("\n=== Key Character Codes ===")
    key_chars = ["TELCO", "PARMA", "CALMA", "NUM_1", "PUNCT_EXCLAM"]
    
    for char_name in key_chars:
        print(f"\n{char_name}:")
        if char_name in ds_charset.characters:
            ds_char = ds_charset.characters[char_name]
            print(f"  DS: '{ds_char}' (U+{ord(ds_char):04X})")
        if char_name in guni_charset.characters:
            guni_char = guni_charset.characters[char_name]
            print(f"  GUNI: '{guni_char}' (U+{ord(guni_char):04X})")
    
    print(f"\n=== Expected Codes ===")
    expected = {
        "TELCO": "U+E02A",
        "PARMA": "U+EC42", 
        "CALMA": "U+EC41",
        "NUM_1": "U+EC62",
        "PUNCT_EXCLAM": "U+E065"
    }
    
    for char_name, code in expected.items():
        print(f"{char_name}: {code}")

if __name__ == "__main__":
    compare_charsets()
