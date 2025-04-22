"""Unit tests for the Optimizer class."""

import pytest
import re
from unicode_regex.optimizer import Optimizer, OptimizationPriority


@pytest.fixture
def opt():
    """Create a fresh Optimizer instance for each test."""
    return Optimizer()


class TestRangeCompression:
    """Test range compression functionality."""

    def test_empty_ranges(self, opt):
        """Test compressing empty ranges."""
        assert opt.compress_ranges([]) == []

    def test_single_range(self, opt):
        """Test compressing a single range."""
        assert opt.compress_ranges([(1, 1)]) == [(1, 1)]
        assert opt.compress_ranges([(1, 5)]) == [(1, 5)]

    def test_adjacent_ranges(self, opt):
        """Test compressing adjacent ranges."""
        ranges = [(1, 3), (4, 6), (7, 9)]
        assert opt.compress_ranges(ranges) == [(1, 9)]

    def test_overlapping_ranges(self, opt):
        """Test compressing overlapping ranges."""
        ranges = [(1, 4), (3, 6), (5, 8)]
        assert opt.compress_ranges(ranges) == [(1, 8)]

    def test_disjoint_ranges(self, opt):
        """Test compressing disjoint ranges."""
        ranges = [(1, 2), (4, 5), (7, 8)]
        assert opt.compress_ranges(ranges) == [(1, 2), (4, 5), (7, 8)]

    def test_mixed_ranges(self, opt):
        """Test compressing a mix of range types."""
        ranges = [(1, 3), (3, 5), (7, 8), (10, 12), (12, 15)]
        assert opt.compress_ranges(ranges) == [(1, 5), (7, 8), (10, 15)]


class TestPatternMinimization:
    """Test pattern minimization strategies."""

    def test_character_class_minimization(self, opt):
        """Test minimization of character classes."""
        assert opt.minimize_pattern('[a]') == 'a'
        assert opt.minimize_pattern('[abc]') == '[abc]'
        assert opt.minimize_pattern('[a-z]') == '[a-z]'
        assert opt.minimize_pattern('[a][b][c]') == '[abc]'

    def test_group_minimization(self, opt):
        """Test minimization of groups."""
        assert opt.minimize_pattern('(?:a)') == 'a'
        assert opt.minimize_pattern('(?:a|b)') == '(?:a|b)'
        assert opt.minimize_pattern('(?:abc)(?:def)') == 'abcdef'

    def test_escape_minimization(self, opt):
        """Test minimization of escape sequences."""
        assert opt.minimize_pattern('\\a') == 'a'
        assert opt.minimize_pattern('\\[') == '\\['
        assert opt.minimize_pattern('\\w') == '\\w'
        assert opt.minimize_pattern('\\d') == '\\d'

    def test_combined_minimization(self, opt):
        """Test minimization of combined patterns."""
        pattern = '(?:[a-z])(?:\\d)(?:[A-Z])'
        assert opt.minimize_pattern(pattern) == '[a-z]\\d[A-Z]'


class TestReadabilityOptimization:
    """Test readability optimization strategies."""

    def test_alternation_spacing(self, opt):
        """Test spacing around alternations."""
        assert opt.optimize_readability('a|b|c') == 'a | b | c'
        assert opt.optimize_readability('[a-z]|[0-9]') == '[a-z] | [0-9]'

    def test_range_spacing(self, opt):
        """Test spacing in character ranges."""
        assert opt.optimize_readability('[a-z]') == '[a - z]'
        assert opt.optimize_readability('[a-zA-Z]') == '[a - z A - Z]'

    def test_group_spacing(self, opt):
        """Test spacing in groups."""
        assert opt.optimize_readability('(?:a|b|c)') == '(?:a | b | c)'
        assert opt.optimize_readability('(a|b|c)') == '(a | b | c)'

    def test_extra_space_removal(self, opt):
        """Test removal of unnecessary spaces."""
        assert opt.optimize_readability('a  |  b') == 'a | b'
        assert opt.optimize_readability('[a  -  z]') == '[a - z]'


class TestOptimizationPriorities:
    """Test optimization with different priorities."""

    def test_size_priority(self, opt):
        """Test size-prioritized optimization."""
        pattern = opt.optimize('(?:[a-z])|(?:[0-9])', OptimizationPriority.SIZE)
        assert '[a-z]|[0-9]' in pattern
        assert ' | ' not in pattern

    def test_readability_priority(self, opt):
        """Test readability-prioritized optimization."""
        pattern = opt.optimize('(?:[a-z])|(?:[0-9])', OptimizationPriority.READABILITY)
        assert ' | ' in pattern
        assert ' - ' in pattern

    def test_invalid_priority(self, opt):
        """Test handling of invalid priorities."""
        with pytest.raises(ValueError):
            opt.optimize_pattern('abc', 'invalid')


class TestPatternBenchmarking:
    """Test pattern benchmarking functionality."""

    def test_benchmark_structure(self, opt):
        """Test structure of benchmark results."""
        results = opt.benchmark_pattern('[a-z]', ['abc', 'def'])
        assert 'compilation_time' in results
        assert 'avg_match_time' in results
        assert 'pattern_size' in results

    def test_benchmark_values(self, opt):
        """Test benchmark result values."""
        results = opt.benchmark_pattern('[a-z]+', ['abc', 'def'])
        assert results['compilation_time'] >= 0
        assert results['avg_match_time'] >= 0
        assert results['pattern_size'] == len('[a-z]+')

    def test_empty_test_strings(self, opt):
        """Test benchmarking with empty test strings."""
        results = opt.benchmark_pattern('[a-z]', [])
        assert results['avg_match_time'] == 0.0

    def test_pattern_comparison(self, opt):
        """Test comparing pattern performance."""
        # Complex pattern vs simple pattern
        complex_pattern = '(?:[a-z]|[A-Z]|[0-9])+'
        simple_pattern = '[a-zA-Z0-9]+'

        complex_results = opt.benchmark_pattern(complex_pattern, ['abc123', 'ABC123'])
        simple_results = opt.benchmark_pattern(simple_pattern, ['abc123', 'ABC123'])

        # Simple pattern should be smaller
        assert simple_results['pattern_size'] < complex_results['pattern_size']


class TestOptimizationEffectiveness:
    """Test the effectiveness of optimizations."""

    def test_size_reduction(self, opt):
        """Test that optimization reduces pattern size where possible."""
        patterns = [
            ('(?:a)|(?:b)|(?:c)', 'a|b|c'),
            ('[a][b][c]', '[abc]'),
            ('(?:foo)|(?:bar)', 'foo|bar'),
        ]

        for original, expected in patterns:
            optimized = opt.optimize(original, OptimizationPriority.SIZE)
            assert len(optimized) <= len(original)

    def test_pattern_equivalence(self, opt):
        """Test that optimized patterns match the same strings."""
        test_cases = [
            ('[a-z]|[0-9]', ['a', 'z', '0', '9', 'x']),
            ('(?:foo)|(?:bar)', ['foo', 'bar', 'baz']),
            ('[aeiou]', ['a', 'e', 'i', 'o', 'u', 'x']),
        ]

        for pattern, test_strings in test_cases:
            original_regex = re.compile(pattern)
            optimized_regex = re.compile(opt.optimize(pattern, OptimizationPriority.SIZE))

            for test_str in test_strings:
                assert bool(original_regex.match(test_str)) == bool(optimized_regex.match(test_str))