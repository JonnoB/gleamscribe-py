"""
Pytest fixtures for Glaemscribe test suite.

Session-scoped fixtures provide major performance improvements by parsing
mode files once per test session instead of once per test.

Performance impact: 60s test suite → ~5s (90% reduction)
"""

import pytest
from glaemscribe.parsers.mode_parser import ModeParser
from glaemscribe.parsers.charset_parser import CharsetParser
from glaemscribe.validation.unicode_validator import UnicodeValidator
from glaemscribe.validation.tengwar_validator import TengwarValidator
from glaemscribe.resources import get_mode_path, get_charset_path


@pytest.fixture(scope="session")
def mode_parser():
    """Shared mode parser instance for all tests."""
    return ModeParser()


@pytest.fixture(scope="session")
def charset_parser():
    """Shared charset parser instance for all tests."""
    return CharsetParser()


@pytest.fixture(scope="session")
def quenya_classical_mode(mode_parser):
    """Pre-parsed Quenya Classical Tengwar mode."""
    mode = mode_parser.parse(str(get_mode_path('quenya-tengwar-classical')))
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def sindarin_general_mode(mode_parser):
    """Pre-parsed Sindarin General Use Tengwar mode."""
    mode = mode_parser.parse(str(get_mode_path('sindarin-tengwar-general_use')))
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def sindarin_beleriand_mode(mode_parser):
    """Pre-parsed Sindarin Beleriand Tengwar mode."""
    mode = mode_parser.parse(str(get_mode_path('sindarin-tengwar-beleriand')))
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def english_tengwar_mode(mode_parser):
    """Pre-parsed English Tengwar mode."""
    mode = mode_parser.parse(str(get_mode_path('english-tengwar-espeak')))
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def tengwar_freemono_charset(charset_parser):
    """Pre-parsed Tengwar FreeMonoTengwar charset (Unicode)."""
    return charset_parser.parse(str(get_charset_path('tengwar_freemono')))


@pytest.fixture(scope="session")
def unicode_validator():
    """Shared Unicode validator instance."""
    return UnicodeValidator()


@pytest.fixture(scope="session")
def tengwar_validator():
    """Shared Tengwar validator instance."""
    return TengwarValidator()
