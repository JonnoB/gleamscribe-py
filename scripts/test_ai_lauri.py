"""Export the Quenya Tengwar transcription tree as a JSON debug file.

This module parses the Quenya-Tengwar classical mode using Glaemscribe and
exports the internal transcription tree structure to a JSON file for debugging
and analysis purposes.

The exported JSON contains the complete node hierarchy with metadata including
character mappings, replacement rules, effective status, and child node counts.

Typical usage:
    python script.py
"""


from glaemscribe.parsers.mode_parser import ModeParser
import json
import os

def build_node_dict(node, path: str = ""):
    children = []
    for char in sorted(node.siblings.keys()):
        child = node.siblings[char]
        children.append(build_node_dict(child, path + (char or "")))

    return {
        "character": node.character if node.character is not None else "ROOT",
        "path": path,
        "replacement": node.replacement,
        "effective": node.is_effective(),
        "child_count": len(children),
        "children": children,
    }

# Parse and finalize the mode
from glaemscribe.resources import get_mode_path
parser = ModeParser()
mode = parser.parse(str(get_mode_path('quenya-tengwar-classical')))
mode.processor.finalize({})

# Dump the Python transcription tree
tree_root = mode.processor.transcription_tree
tree_dict = build_node_dict(tree_root)

output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'debug_tree_ai_lauri_python.json')
with open(output_path, 'w') as f:
    json.dump(tree_dict, f, indent=2)

print(f"Python debug tree saved to {output_path}")
