# Rule/SubRule/SheafChain Implementation Plan

## Current Status
✅ IfTree conditional logic working
✅ Variable extraction working (73 vars from litteral group)
✅ 3 rule groups correctly parsed
❌ Transcription tree recursion error - need proper Rule processing

## Problem
We're passing unparsed rule expressions like `[a*b*c][d*e]` directly to the transcription tree,
but Ruby/JS first parse these into combinations before adding to the tree.

## Architecture Overview

### Ruby/JS Pipeline:
```
Rule Expression → SheafChain → Sheaf → Fragment → Combinations → SubRules → Tree
```

### Example:
```
Input:  "[a*b][c*d] --> [X*Y][1*2]"
Parse:  SheafChain with 2 sheaves each
Generate: 4 SubRules:
  - "ac" → ["X", "1"]
  - "ad" → ["X", "2"]
  - "bc" → ["Y", "1"]
  - "bd" → ["Y", "2"]
Add to tree: Each SubRule's src_combination.join("") as path
```

## Classes to Implement

### 1. Fragment (fragment.py)
**Purpose**: Parses equivalences like `h(a,ä)(i,ï)` into combinations
**Key Methods**:
- `__init__(sheaf, expression)`: Parse expression
- `finalize()`: Generate all combinations
**Ruby Reference**: `/home/jonno/glaemscribe/lib_rb/api/fragment.rb`

### 2. Sheaf (sheaf.py)
**Purpose**: Bundle of fragments, parses `[a*b*c]`
**Key Methods**:
- `__init__(sheaf_chain, expression, linkable)`: Parse with `*` separator
- Creates Fragment objects for each part
**Ruby Reference**: `/home/jonno/glaemscribe/lib_rb/api/sheaf.rb`

### 3. SheafChain (sheaf_chain.py)
**Purpose**: Chain of sheaves, parses `[a*b][c*d]`
**Key Methods**:
- `__init__(rule, expression, is_src)`: Split by `[...]` patterns
- Creates Sheaf objects for each bracket group
**Ruby Reference**: `/home/jonno/glaemscribe/lib_rb/api/sheaf_chain.rb`

### 4. SheafChainIterator (sheaf_chain_iterator.py)
**Purpose**: Generates all combinations from a SheafChain
**Key Methods**:
- `combinations()`: Get current combination
- `iterate()`: Move to next combination
- `prototype()`: Get the structure type
**Ruby Reference**: `/home/jonno/glaemscribe/lib_rb/api/sheaf_chain_iterator.rb`

### 5. Rule (rule.py)
**Purpose**: Transcription rule with source and destination chains
**Key Attributes**:
- `src_sheaf_chain`: Source SheafChain
- `dst_sheaf_chain`: Destination SheafChain
- `sub_rules`: List of SubRule objects
**Key Methods**:
- `finalize(cross_schema)`: Generate all SubRules
**Ruby Reference**: `/home/jonno/glaemscribe/lib_rb/api/rule.rb`

### 6. SubRule (sub_rule.py)
**Purpose**: Single combination from a rule
**Key Attributes**:
- `src_combination`: Array of source tokens
- `dst_combination`: Array of destination tokens
**Ruby Reference**: `/home/jonno/glaemscribe/lib_rb/api/sub_rule.rb`

## Implementation Order

1. **Fragment** (simplest, no dependencies)
2. **Sheaf** (depends on Fragment)
3. **SheafChain** (depends on Sheaf)
4. **SheafChainIterator** (depends on SheafChain)
5. **SubRule** (simple data class)
6. **Rule** (depends on all above)
7. **Update RuleGroup.finalize_rule** (create Rule objects)
8. **Update TranscriptionProcessor** (use SubRules)

## Testing Strategy

1. Test Fragment parsing: `h(a,ä)(i,ï)` → 4 combinations
2. Test Sheaf parsing: `[a*b*c]` → 3 fragments
3. Test SheafChain parsing: `[a*b][c*d]` → 2 sheaves
4. Test SheafChainIterator: Generate all 4 combinations
5. Test Rule creation: Full pipeline
6. Test transcription tree: No recursion errors

## Success Criteria

✅ No recursion errors in transcription tree
✅ Complex rules like `[a*b*c][d*e]` correctly expanded
✅ Transcription works end-to-end
✅ Matches Ruby/JS output exactly
