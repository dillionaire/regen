"""Integration tests for complex Unicode operations."""

import pytest
import re
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.regex_generator import RegexGenerator


@pytest.fixture
def ud():
    """Create a fresh UnicodeData instance for each test."""
    return UnicodeData()


@pytest.fixture
def generator():
    """Create a RegexGenerator instance for testing."""
    return RegexGenerator()


class TestComplexUnicodeOperations:
    """Test complex scenarios involving multiple Unicode operations."""

    def test_multilingual_identifier_pattern(self, ud, generator):
        """Test creating a pattern for multilingual programming identifiers.

        This tests combining multiple scripts, categories, and properties
        to create a pattern that matches valid identifier characters across scripts.
        """
        # Get letters from multiple scripts
        latin = ud.get_property('Script', 'Latin')
        greek = ud.get_property('Script', 'Greek')
        cyrillic = ud.get_property('Script', 'Cyrillic')

        # Get letter categories
        uppercase = ud.get_category('Lu')
        lowercase = ud.get_category('Ll')
        numbers = ud.get_category('Nd')

        # Combine for first character (letters only)
        first_char = (latin | greek | cyrillic) & (uppercase | lowercase)
        first_pattern = generator.generate_pattern(first_char)

        # Combine for rest of identifier (letters, numbers, and some symbols)
        rest_chars = first_char | numbers
        rest_pattern = generator.generate_pattern(rest_chars)

        # Test the patterns
        identifier_pattern = f"{first_pattern}({rest_pattern})*"
        assert re.match(identifier_pattern, "variable")  # Latin
        assert re.match(identifier_pattern, "μεταβλητή")  # Greek
        assert re.match(identifier_pattern, "переменная")  # Cyrillic
        assert re.match(identifier_pattern, "var123")  # With numbers
        assert not re.match(identifier_pattern, "123var")  # Can't start with number
        assert not re.match(identifier_pattern, "")  # Can't be empty

    def test_smart_text_analysis(self, ud):
        """Test complex text analysis combining multiple Unicode properties.

        This tests analyzing text properties for things like:
        - Script detection
        - Character type analysis
        - Numeric value extraction
        - Special character handling
        """
        # Get various character categories
        letters = ud.get_category('L')
        numbers = ud.get_category('N')
        punctuation = ud.get_category('P')
        symbols = ud.get_category('S')

        # Get script properties
        latin = ud.get_property('Script', 'Latin')
        greek = ud.get_property('Script', 'Greek')

        # Test complex text analysis
        text = "Hello, κόσμε! Price: €42.50"
        results = {
            'latin_letters': 0,
            'greek_letters': 0,
            'numbers': 0,
            'currency': 0,
            'numeric_values': []
        }

        for char in text:
            cp = ord(char)

            # Script detection
            if cp in (latin & letters):
                results['latin_letters'] += 1
            elif cp in (greek & letters):
                results['greek_letters'] += 1

            # Number handling
            if cp in numbers:
                results['numbers'] += 1
                try:
                    results['numeric_values'].append(ud.get_property(cp, 'numeric'))
                except ValueError:
                    pass

            # Currency detection
            if cp in (symbols & ud.get_category('Sc')):
                results['currency'] += 1

        assert results['latin_letters'] == 5  # "Hello"
        assert results['greek_letters'] == 5  # "κόσμε"
        assert results['numbers'] == 4  # "42.50"
        assert results['currency'] == 1  # "€"
        assert results['numeric_values'] == [4.0, 2.0, 5.0, 0.0]

    def test_complex_pattern_generation(self, ud, generator):
        """Test generating complex patterns combining multiple Unicode properties.

        This tests creating patterns that match specific combinations of:
        - Multiple scripts
        - Multiple categories
        - Numeric properties
        - Special cases
        """
        # Get various character sets
        uppercase = ud.get_category('Lu')
        lowercase = ud.get_category('Ll')
        digits = ud.get_category('Nd')
        math_symbols = ud.get_category('Sm')

        # Create pattern for mathematical expressions
        # Should match things like: "2x + y = Z"
        var_chars = (uppercase | lowercase) & ud.get_property('Script', 'Latin')
        operator_chars = math_symbols | CodePointSet({ord(c) for c in '+-*/='})

        # Generate patterns
        var_pattern = generator.generate_pattern(var_chars)
        num_pattern = generator.generate_pattern(digits)
        op_pattern = generator.generate_pattern(operator_chars)

        # Combine patterns
        expr_pattern = f"[{num_pattern}{var_pattern}]\\s*{op_pattern}\\s*[{num_pattern}{var_pattern}]"

        # Test the pattern
        assert re.match(expr_pattern, "2x + y")
        assert re.match(expr_pattern, "A = b")
        assert re.match(expr_pattern, "3 * Z")
        assert not re.match(expr_pattern, "2+")  # Incomplete
        assert not re.match(expr_pattern, "@#$")  # Invalid characters

    def test_unicode_normalization_handling(self, ud, generator):
        """Test handling of Unicode normalization forms and equivalence.

        This tests working with:
        - Combining marks
        - Compatibility equivalence
        - Different normalization forms
        """
        # Get relevant categories
        base_letters = ud.get_category('L') - ud.get_category('M')
        combining_marks = ud.get_category('M')

        # Test combining character sequences
        char_é = "é"  # Single character é (U+00E9)
        decomposed_é = "e\u0301"  # 'e' followed by combining acute accent

        # Both forms should be handled equivalently
        pattern = generator.generate_pattern(base_letters | combining_marks)
        assert re.match(pattern, char_é)
        assert re.match(pattern, decomposed_é)

        # Test with actual character properties
        for c in (char_é, decomposed_é):
            for cp in c.encode('utf-16-le').decode('utf-16-le'):
                cp_val = ord(cp)
                if cp_val in base_letters:
                    assert ud.get_property(cp_val, 'name') is not None
                elif cp_val in combining_marks:
                    assert 'COMBINING' in ud.get_property(cp_val, 'name')

    def test_bidirectional_text_handling(self, ud, generator):
        """Test handling of bidirectional text properties.

        This tests working with:
        - Right-to-left scripts
        - Bidirectional controls
        - Mixed script text
        """
        # Get relevant properties
        latin = ud.get_property('Script', 'Latin')
        arabic = ud.get_property('Script', 'Arabic')
        hebrew = ud.get_property('Script', 'Hebrew')

        # Get direction-related categories
        rtl_scripts = arabic | hebrew

        # Create patterns for different script combinations
        mixed_pattern = generator.generate_pattern(latin | rtl_scripts)

        # Test with mixed script text
        assert re.match(mixed_pattern, 'Hello')  # Latin
        assert re.match(mixed_pattern, 'سلام')   # Arabic
        assert re.match(mixed_pattern, 'שלום')   # Hebrew

        # Test with mixed script properties
        text = "Hello سلام שלום"
        script_counts = {'Latin': 0, 'Arabic': 0, 'Hebrew': 0}

        for char in text:
            cp = ord(char)
            if cp in latin:
                script_counts['Latin'] += 1
            elif cp in arabic:
                script_counts['Arabic'] += 1
            elif cp in hebrew:
                script_counts['Hebrew'] += 1

        assert script_counts['Latin'] == 5   # "Hello"
        assert script_counts['Arabic'] == 4  # "سلام"
        assert script_counts['Hebrew'] == 4  # "שלום"