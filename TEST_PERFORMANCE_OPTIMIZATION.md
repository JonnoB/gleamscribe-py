# Test Performance Optimization Plan

## Current State
- **Test suite time:** ~60 seconds
- **Individual test time:** ~1.6 seconds
- **Bottleneck:** Mode parsing (1.38s per test)

## Root Cause Analysis

```python
# Each test does this:
parser = ModeParser()                                    # 0.01s
mode = parser.parse('quenya-tengwar-classical.glaem')   # 1.38s  <-- BOTTLENECK
mode.processor.finalize({})                             # 0.02s
mode.transcribe('text')                                 # 0.00s
```

**Problem:** Every test re-parses the same mode files from disk.

## Optimization Options

### Option 1: Pytest Fixtures (RECOMMENDED)
```python
@pytest.fixture(scope="session")
def quenya_mode():
    """Parse mode once per test session."""
    parser = ModeParser()
    mode = parser.parse('resources/glaemresources/modes/quenya-tengwar-classical.glaem')
    mode.processor.finalize({})
    return mode

def test_something(quenya_mode):
    result = quenya_mode.transcribe('test')
    # Test logic here
```

**Impact:** 60s → ~5s (90% reduction)

### Option 2: Mode Cache
```python
class ModeCache:
    _cache = {}
    
    @classmethod
    def get_mode(cls, mode_name: str):
        if mode_name not in cls._cache:
            parser = ModeParser()
            mode = parser.parse(f'resources/glaemresources/modes/{mode_name}.glaem')
            mode.processor.finalize({})
            cls._cache[mode_name] = mode
        return cls._cache[mode_name]
```

**Impact:** 60s → ~5s (90% reduction)

### Option 3: Test Parallelization
```bash
pytest -n auto  # Run tests in parallel
```

**Impact:** 60s → ~15s (75% reduction, but uses more CPU)

## Implementation Plan

### Phase 1: Immediate Fix (Session-scoped fixtures)
1. Create fixtures for common modes (quenya, sindarin, etc.)
2. Update tests to use fixtures
3. Expected improvement: 60s → 5s

### Phase 2: Comprehensive Coverage
1. Add fixtures for all charsets
2. Add fixtures for complex mode combinations
3. Expected improvement: Maintain 5s baseline

### Phase 3: Optional Parallelization
1. Add pytest-xdist dependency
2. Configure CI to run tests in parallel
4. Expected improvement: 5s → 2s

## Files to Modify

### Primary
- `tests/conftest.py` - Add pytest fixtures
- `tests/test_js_parity.py` - Use fixtures
- `tests/test_integration.py` - Use fixtures
- `tests/test_virtual_characters.py` - Use fixtures

### Secondary
- `tests/test_real_world.py` - Use fixtures
- `tests/test_unicode_validation.py` - Use fixtures
- `pyproject.toml` - Add pytest-xdist for parallelization

## Example Fixture Implementation

```python
# tests/conftest.py
import pytest
from src.glaemscribe.parsers.mode_parser import ModeParser

@pytest.fixture(scope="session")
def mode_parser():
    """Shared mode parser instance."""
    return ModeParser()

@pytest.fixture(scope="session") 
def quenya_classical_mode(mode_parser):
    """Pre-parsed Quenya Classical mode."""
    mode = mode_parser.parse('resources/glaemresources/modes/quenya-tengwar-classical.glaem')
    mode.processor.finalize({})
    return mode

@pytest.fixture(scope="session")
def sindarin_general_mode(mode_parser):
    """Pre-parsed Sindarin General mode."""
    mode = mode_parser.parse('resources/glaemresources/modes/sindarin-tengwar-general_use.glaem')
    mode.processor.finalize({})
    return mode
```

## Expected Timeline

- **Phase 1:** 2-4 hours (immediate 90% improvement)
- **Phase 2:** 1-2 hours (comprehensive coverage)
- **Phase 3:** 30 minutes (parallelization)

## Risk Assessment

- **Low risk:** Fixtures are standard pytest practice
- **No breaking changes:** Tests will work the same way
- **Easy rollback:** Can disable fixtures if issues arise

## Success Metrics

- **Target:** Test suite under 30 seconds
- **Goal:** Test suite under 10 seconds
- **Stretch:** Test suite under 5 seconds

---

**Priority:** Medium  
**Impact:** High (developer productivity)  
**Effort:** Low (2-4 hours for 90% improvement)
