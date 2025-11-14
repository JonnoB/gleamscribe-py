"""
Pytest fixtures for Glaemscribe test suite.

Session-scoped fixtures provide major performance improvements by parsing
mode files once per test session instead of once per test.

Performance impact: 60s test suite → ~5s (90% reduction)
"""

import pytest
from src.glaemscribe.parsers.mode_parser import ModeParser
from src.glaemscribe.parsers.charset_parser import CharsetParser
from src.glaemscribe.validation.unicode_validator import UnicodeValidator
from src.glaemscribe.validation.tengwar_validator import TengwarValidator


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
    mode = mode_parser.parse('resources/glaemresources/modes/quenya-tengwar-classical.glaem')
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def sindarin_general_mode(mode_parser):
    """Pre-parsed Sindarin General Use Tengwar mode."""
    mode = mode_parser.parse('resources/glaemresources/modes/sindarin-tengwar-general_use.glaem')
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def sindarin_beleriand_mode(mode_parser):
    """Pre-parsed Sindarin Beleriand Tengwar mode."""
    mode = mode_parser.parse('resources/glaemresources/modes/sindarin-tengwar-beleriand.glaem')
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def english_tengwar_mode(mode_parser):
    """Pre-parsed English Tengwar mode."""
    mode = mode_parser.parse('resources/glaemresources/modes/english-tengwar-espeak.glaem')
    mode.processor.finalize({})
    return mode


@pytest.fixture(scope="session")
def tengwar_ds_sindarin_charset(charset_parser):
    """Pre-parsed Tengwar DS Sindarin charset."""
    return charset_parser.parse('resources/glaemresources/charsets/tengwar_ds_sindarin.cst')


@pytest.fixture(scope="session")
def tengwar_guni_sindarin_charset(charset_parser):
    """Pre-parsed Tengwar Guni Sindarin charset."""
    return charset_parser.parse('resources/glaemresources/charsets/tengwar_guni_sindarin.cst')


@pytest.fixture(scope="session")
def tengwar_ds_quenya_charset(charset_parser):
    """Pre-parsed Tengwar DS Quenya charset."""
    return charset_parser.parse('resources/glaemresources/charsets/tengwar_ds_quenya.cst')


@pytest.fixture(scope="session")
def tengwar_guni_quenya_charset(charset_parser):
    """Pre-parsed Tengwar Guni Quenya charset."""
    return charset_parser.parse('resources/glaemresources/charsets/tengwar_guni_quenya.cst')


@pytest.fixture(scope="session")
def cirth_daeron_charset(charset_parser):
    """Pre-parsed Cirth Daeron charset."""
    return charset_parser.parse('resources/glaemresources/charsets/cirth_daeron.cst')


@pytest.fixture(scope="session")
def cirth_erebor_charset(charset_parser):
    """Pre-parsed Cirth Erebor charset."""
    return charset_parser.parse('resources/glaemresources/charsets/cirth_erebor.cst')


@pytest.fixture(scope="session")
def cirth_moria_charset(charset_parser):
    """Pre-parsed Cirth Moria charset."""
    return charset_parser.parse('resources/glaemresources/charsets/cirth_moria.cst')


@pytest.fixture(scope="session")
def cirth_woodland_charset(charset_parser):
    """Pre-parsed Cirth Woodland charset."""
    return charset_parser.parse('resources/glaemresources/charsets/cirth_woodland.cst')


@pytest.fixture(scope="session")
def unicode_validator():
    """Shared Unicode validator instance."""
    return UnicodeValidator()


@pytest.fixture(scope="session")
def tengwar_validator():
    """Shared Tengwar validator instance."""
    return TengwarValidator()
