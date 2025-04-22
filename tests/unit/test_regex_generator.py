"""Unit tests for the RegexGenerator class."""

import re
import pytest
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.optimizer import Optimizer


@pytest.fixture
def generator():
    """Create a RegexGenerator instance for testing."""
    return RegexGenerator()


class TestRegexGenerator:
    """Test cases for the RegexGenerator class."""

    def test_single_ascii_character(self, generator):
        """Test handling of single ASCII characters."""
        pattern = generator.generate_pattern(CodePointSet({65}))  # 'A'
        assert pattern == 'A'
        assert re.match(pattern, 'A')
        assert not re.match(pattern, 'B')

    def test_special_character(self, generator):
        """Test handling of special regex characters."""
        pattern = generator.generate_pattern(CodePointSet({46}))  # '.'
        assert pattern == r'\.'
        assert re.match(pattern, '.')
        assert not re.match(pattern, 'a')

    def test_common_ranges(self, generator):
        """Test handling of common Unicode ranges."""
        # Test digits
        digits = CodePointSet()
        digits.add_range(0x0030, 0x0039)
        pattern = generator.generate_pattern(digits)
        assert pattern == r'\d'
        assert all(re.match(pattern, str(i)) for i in range(10))
        assert not re.match(pattern, 'a')

        # Test word characters
        word = CodePointSet()
        word.add_range(0x0030, 0x0039)  # 0-9
        word.add_range(0x0041, 0x005A)  # A-Z
        word.add_range(0x0061, 0x007A)  # a-z
        word.add_point(0x005F)  # underscore
        pattern = generator.generate_pattern(word)
        assert pattern == r'\w'
        assert re.match(pattern, 'a')
        assert re.match(pattern, 'Z')
        assert re.match(pattern, '5')
        assert re.match(pattern, '_')
        assert not re.match(pattern, '.')

    def test_unicode_ranges(self, generator):
        """Test handling of Unicode ranges."""
        # Test basic Latin range
        latin = CodePointSet()
        latin.add_range(0x0041, 0x005A)  # A-Z
        pattern = generator.generate_pattern(latin)
        assert pattern == '[A-Z]'
        assert re.match(pattern, 'A')
        assert re.match(pattern, 'Z')
        assert not re.match(pattern, 'a')

    def test_optimization_priorities(self, generator):
        """Test pattern generation with different optimization priorities."""
        # Create a set with multiple ranges
        cps = CodePointSet()
        cps.add_range(0x0041, 0x005A)  # A-Z
        cps.add_range(0x0061, 0x007A)  # a-z
        cps.add_range(0x0391, 0x03A9)  # Greek uppercase

        # Test size priority
        size_pattern = generator.generate_pattern(cps, prioritize='size')
        assert len(size_pattern) <= len(generator.generate_pattern(cps, prioritize='readability'))

        # Test readability priority
        readable_pattern = generator.generate_pattern(cps, prioritize='readability')
        assert ' - ' in readable_pattern or ' | ' in readable_pattern

    def test_alternation_pattern(self, generator):
        """Test generation of alternation patterns."""
        patterns = ['foo', 'bar', 'baz']

        # Test basic alternation
        pattern = generator.generate_alternation_pattern(patterns)
        assert pattern == 'foo|bar|baz'
        assert re.match(pattern, 'foo')
        assert re.match(pattern, 'bar')
        assert re.match(pattern, 'baz')
        assert not re.match(pattern, 'qux')

        # Test readable alternation
        pattern = generator.generate_alternation_pattern(patterns, prioritize='readability')
        assert pattern == '(?:foo | bar | baz)'
        assert re.match(pattern, 'foo')
        assert re.match(pattern, 'bar')
        assert re.match(pattern, 'baz')
        assert not re.match(pattern, 'qux')

    def test_empty_pattern(self, generator):
        """Test handling of empty input."""
        pattern = generator.generate_pattern(CodePointSet())
        assert pattern == '[]'
        assert not re.match(pattern, '')
        assert not re.match(pattern, 'a')

    def test_range_pattern(self, generator):
        """Test range pattern generation."""
        pattern = generator.generate_range_pattern(0x0041, 0x005A)  # A-Z
        assert pattern == '[A-Z]'
        assert re.match(pattern, 'A')
        assert re.match(pattern, 'Z')
        assert not re.match(pattern, 'a')

    def test_category_pattern(self, generator):
        """Test Unicode category pattern generation."""
        pattern = generator.generate_category_pattern('Lu')
        assert pattern == r'\p{Lu}'

    def test_property_pattern(self, generator):
        """Test Unicode property pattern generation."""
        pattern = generator.generate_property_pattern('Script', 'Latin')
        assert pattern == r'\p{Script=Latin}'

    def test_invalid_range(self, generator):
        """Test handling of invalid ranges."""
        with pytest.raises(ValueError):
            generator.generate_range_pattern(0x005A, 0x0041)  # Z-A

    def test_custom_optimizer(self):
        """Test using a custom optimizer."""
        optimizer = Optimizer()
        generator = RegexGenerator(optimizer=optimizer)
        pattern = generator.generate_pattern(CodePointSet({65, 66, 67}))
        assert pattern == '[A-C]'

    def test_pattern_caching(self, generator):
        """Test pattern caching functionality."""
        cps = CodePointSet({65, 66, 67})  # A-C
        pattern1 = generator.generate_pattern(cps)
        pattern2 = generator.generate_pattern(cps)
        assert pattern1 == pattern2
        assert pattern1 == '[A-C]'


class TestCommonUnicodeRanges:
    """Test cases for common Unicode range handling."""

    def test_digit_range(self, generator):
        """Test digit range pattern generation and matching."""
        digits = CodePointSet()
        digits.add_range(0x0030, 0x0039)  # 0-9
        pattern = generator.generate_pattern(digits)
        assert pattern == r'\d'
        assert all(re.match(pattern, str(i)) for i in range(10))
        assert not re.match(pattern, 'a')

    def test_word_character_range(self, generator):
        r"""Test \w pattern generation and matching."""
        # Create a set with word characters
        word_chars = CodePointSet()
        word_chars.add_range(0x0030, 0x0039)  # 0-9
        word_chars.add_range(0x0041, 0x005A)  # A-Z
        word_chars.add_range(0x0061, 0x007A)  # a-z
        word_chars.add_point(0x005F)  # underscore
        pattern = generator.generate_pattern(word_chars)
        assert pattern == r'\w'
        assert re.match(pattern, 'a')
        assert re.match(pattern, 'Z')
        assert re.match(pattern, '5')
        assert re.match(pattern, '_')
        assert not re.match(pattern, '.')

    def test_whitespace_range(self, generator):
        r"""Test \s pattern generation and matching."""
        whitespace = CodePointSet()
        for cp in [0x0020, 0x0009, 0x000A, 0x000B, 0x000C, 0x000D]:
            whitespace.add_point(cp)
        pattern = generator.generate_pattern(whitespace)
        assert pattern == r'\s'
        assert re.match(pattern, ' ')
        assert re.match(pattern, '\t')
        assert re.match(pattern, '\n')
        assert not re.match(pattern, 'a')

    def test_combined_ranges(self, generator):
        """Test combining multiple common ranges."""
        combined = CodePointSet()
        combined.add_range(0x0030, 0x0039)  # digits
        combined.add_range(0x0041, 0x005A)  # uppercase
        pattern = generator.generate_pattern(combined)
        assert re.match(pattern, '5')
        assert re.match(pattern, 'A')
        assert not re.match(pattern, 'a')

    def test_negated_ranges(self, generator):
        """Test negated character class ranges."""
        digits = CodePointSet()
        digits.add_range(0x0030, 0x0039)
        pattern = f'[^{generator.generate_pattern(digits)[1:-1]}]'
        assert re.match(pattern, 'a')
        assert not re.match(pattern, '5')

    def test_range_optimization(self, generator):
        """Test optimization of range patterns."""
        # Test that ranges are properly compressed
        cps = CodePointSet()
        cps.add_range(0x0041, 0x005A)  # A-Z
        cps.add_range(0x0061, 0x007A)  # a-z
        pattern = generator.generate_pattern(cps)
        assert len(pattern) < len('[A-Za-z]')  # Should use a more compact form if possible