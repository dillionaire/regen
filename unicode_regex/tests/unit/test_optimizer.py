"""Unit tests for the Optimizer class."""

import pytest
from unicode_regex.optimizer import Optimizer


def test_compress_ranges():
    """Test compressing code points into ranges."""
    opt = Optimizer()

    # Test empty set
    assert opt.compress_ranges(set()) == []

    # Test single point
    assert opt.compress_ranges({65}) == [(65, 65)]

    # Test consecutive points
    assert opt.compress_ranges({65, 66, 67}) == [(65, 67)]

    # Test non-consecutive points
    assert opt.compress_ranges({65, 67, 69}) == [(65, 65), (67, 67), (69, 69)]

    # Test multiple ranges
    assert opt.compress_ranges({65, 66, 67, 70, 71, 72}) == [(65, 67), (70, 72)]


def test_minimize_pattern():
    """Test pattern minimization."""
    opt = Optimizer()

    # Test unnecessary character class
    assert opt.minimize_pattern('[a]') == 'a'

    # Test necessary character class
    assert opt.minimize_pattern('[a-z]') == '[a-z]'

    # Test unnecessary non-capturing group
    assert opt.minimize_pattern('(?:abc)') == 'abc'

    # Test necessary non-capturing group
    assert opt.minimize_pattern('(?:abc|def)') == '(?:abc|def)'

    # Test combining character classes
    assert opt.minimize_pattern('[a-z][0-9]') == '[a-z0-9]'

    # Test unnecessary escapes
    assert opt.minimize_pattern('\\a') == 'a'
    assert opt.minimize_pattern('\\[') == '\\['  # Keep necessary escapes


def test_optimize_readability():
    """Test pattern readability optimization."""
    opt = Optimizer()

    # Test alternation spacing
    assert opt.optimize_readability('a|b|c') == 'a| b| c'

    # Test range spacing
    assert opt.optimize_readability('[a-z]') == '[a - z]'

    # Test multiple optimizations
    pattern = '[a-z]|[0-9]'
    expected = '[a - z]| [0 - 9]'
    assert opt.optimize_readability(pattern) == expected


def test_optimize_pattern():
    """Test pattern optimization with different priorities."""
    opt = Optimizer()

    pattern = '[a]|[b]|[c-z]'

    # Test size priority
    assert opt.optimize_pattern(pattern, 'size') == 'a|b|[c-z]'

    # Test readability priority
    assert opt.optimize_pattern(pattern, 'readability') == 'a| b| [c - z]'

    # Test invalid priority
    with pytest.raises(ValueError):
        opt.optimize_pattern(pattern, 'invalid')


def test_benchmark_pattern():
    """Test pattern benchmarking."""
    opt = Optimizer()

    pattern = '[a-z]+'
    test_strings = ['abc', 'def', 'xyz']

    results = opt.benchmark_pattern(pattern, test_strings)

    # Check result structure
    assert 'compilation_time' in results
    assert 'avg_match_time' in results
    assert 'pattern_size' in results

    # Check value types
    assert isinstance(results['compilation_time'], float)
    assert isinstance(results['avg_match_time'], float)
    assert isinstance(results['pattern_size'], int)

    # Check pattern size
    assert results['pattern_size'] == len(pattern)