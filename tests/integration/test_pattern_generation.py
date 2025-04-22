"""Integration tests for pattern generation and Unicode handling."""

import re
import time
import pytest
from typing import Set, Dict, List
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.optimizer import Optimizer, OptimizationPriority


@pytest.fixture
def components():
    """Create instances of all components needed for testing."""
    return {
        'unicode_data': UnicodeData(),
        'generator': RegexGenerator(),
        'optimizer': Optimizer()
    }


def benchmark_pattern(pattern: str, test_strings: List[str], iterations: int = 1000) -> Dict[str, float]:
    """Benchmark a pattern's performance.

    Args:
        pattern: The pattern to test
        test_strings: Strings to match against
        iterations: Number of iterations for each test

    Returns:
        Dictionary with benchmark results
    """
    results = {
        'compilation_time': 0.0,
        'avg_match_time': 0.0,
        'pattern_size': len(pattern)
    }

    # Measure compilation time
    start = time.perf_counter()
    compiled = re.compile(pattern)
    results['compilation_time'] = time.perf_counter() - start

    # Measure matching time
    total_match_time = 0.0
    for _ in range(iterations):
        for test_str in test_strings:
            start = time.perf_counter()
            compiled.match(test_str)
            total_match_time += time.perf_counter() - start

    results['avg_match_time'] = total_match_time / (len(test_strings) * iterations)
    return results


class TestComplexPatternGeneration:
    """Test complex pattern generation scenarios."""

    def test_mixed_scripts(self, components):
        """Test generating patterns for mixed scripts (Latin, Greek, Cyrillic)."""
        ud = components['unicode_data']
        gen = components['generator']

        # Get code points for different scripts
        latin = ud.get_property('Script', 'Latin')
        greek = ud.get_property('Script', 'Greek')
        cyrillic = ud.get_property('Script', 'Cyrillic')

        # Combine scripts
        mixed = latin | greek | cyrillic

        # Generate pattern with different priorities
        size_pattern = gen.generate_pattern(mixed, prioritize='size')
        readable_pattern = gen.generate_pattern(mixed, prioritize='readability')

        # Test patterns
        test_chars = ['A', 'Α', 'А']  # Latin A, Greek Alpha, Cyrillic A
        for pattern in [size_pattern, readable_pattern]:
            for char in test_chars:
                assert re.match(pattern, char), f"Pattern should match {char}"

        # Size pattern should be more compact
        assert len(size_pattern) < len(readable_pattern)

    def test_complex_categories(self, components):
        """Test patterns combining multiple Unicode categories."""
        ud = components['unicode_data']
        gen = components['generator']

        # Combine letters, numbers, and symbols
        letters = ud.get_category('L')  # All letters
        numbers = ud.get_category('N')  # All numbers
        symbols = ud.get_category('S')  # All symbols

        # Create different combinations
        alphanumeric = letters | numbers
        complex_set = letters | numbers | symbols

        # Generate and test patterns
        for test_set, name, examples in [
            (alphanumeric, 'alphanumeric', ['A', '1', 'β', '٣']),
            (complex_set, 'complex', ['A', '1', '€', '∑', '©'])
        ]:
            pattern = gen.generate_pattern(test_set)
            for char in examples:
                assert re.match(pattern, char), f"{name} pattern should match {char}"

    def test_performance_optimization(self, components):
        """Test pattern optimization for performance."""
        ud = components['unicode_data']
        gen = components['generator']

        # Get a complex set of code points
        letters = ud.get_category('L')
        numbers = ud.get_category('N')
        combined = letters | numbers

        # Generate patterns with different optimization strategies
        patterns = {
            'size': gen.generate_pattern(combined, prioritize='size'),
            'readability': gen.generate_pattern(combined, prioritize='readability'),
            'unoptimized': gen.generate_pattern(combined, prioritize=None)
        }

        # Test strings covering different cases
        test_strings = ['A', '1', 'β', '٣', 'ж', '漢', 'नम']

        # Benchmark each pattern
        results = {
            name: benchmark_pattern(pattern, test_strings)
            for name, pattern in patterns.items()
        }

        # Size-optimized pattern should be smallest
        assert len(patterns['size']) <= len(patterns['readability'])
        assert len(patterns['size']) <= len(patterns['unoptimized'])

        # Compilation time should be reasonable
        for name, result in results.items():
            assert result['compilation_time'] < 0.1, f"{name} compilation too slow"

    def test_edge_cases(self, components):
        """Test handling of edge cases and boundary conditions."""
        gen = components['generator']

        # Test empty set
        empty_set = CodePointSet()
        assert gen.generate_pattern(empty_set) == r'[]'

        # Test single boundary code point
        max_point = CodePointSet({0x10FFFF})
        pattern = gen.generate_pattern(max_point)
        assert re.match(pattern, chr(0x10FFFF))

        # Test large ranges
        large_set = CodePointSet()
        large_set.add_range(0, 0x10FFFF)
        pattern = gen.generate_pattern(large_set)
        assert re.match(pattern, 'A')
        assert re.match(pattern, '漢')
        assert re.match(pattern, '🌟')

    def test_pattern_composition(self, components):
        """Test composing patterns from multiple components."""
        ud = components['unicode_data']
        gen = components['generator']

        # Get different categories
        uppercase = ud.get_category('Lu')
        lowercase = ud.get_category('Ll')
        digits = ud.get_category('Nd')

        # Generate individual patterns
        patterns = [
            gen.generate_pattern(uppercase),
            gen.generate_pattern(lowercase),
            gen.generate_pattern(digits)
        ]

        # Compose patterns with alternation
        combined = gen.generate_alternation_pattern(patterns)

        # Test the combined pattern
        test_cases = [
            ('A', True),   # Uppercase
            ('a', True),   # Lowercase
            ('1', True),   # Digit
            ('.', False),  # Punctuation
            (' ', False)   # Space
        ]

        for char, should_match in test_cases:
            if should_match:
                assert re.match(combined, char), f"Should match {char}"
            else:
                assert not re.match(combined, char), f"Should not match {char}"

    def test_property_combinations(self, components):
        """Test combining multiple Unicode properties."""
        ud = components['unicode_data']
        gen = components['generator']

        # Get different properties
        latin = ud.get_property('Script', 'Latin')
        uppercase = ud.get_category('Lu')

        # Create intersection (uppercase Latin letters)
        uppercase_latin = latin & uppercase
        pattern = gen.generate_pattern(uppercase_latin)

        # Test pattern
        assert re.match(pattern, 'A')      # Latin uppercase
        assert not re.match(pattern, 'a')  # Latin lowercase
        assert not re.match(pattern, 'Α')  # Greek uppercase