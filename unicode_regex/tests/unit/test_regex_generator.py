"""Unit tests for the RegexGenerator class."""

import re
import pytest
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.optimizer import Optimizer


def test_single_ascii_character():
    """Test generating pattern for a single ASCII character."""
    gen = RegexGenerator()
    pattern = gen.generate_pattern({65})  # ASCII 'A'
    assert pattern == 'A'
    assert re.match(pattern, 'A')
    assert not re.match(pattern, 'B')


def test_multiple_ascii_characters():
    """Test generating pattern for multiple ASCII characters."""
    gen = RegexGenerator()
    pattern = gen.generate_pattern({65, 66, 67})  # ASCII 'A', 'B', 'C'
    assert pattern == '(?:ABC)'
    assert re.match(pattern, 'A')
    assert re.match(pattern, 'B')
    assert re.match(pattern, 'C')
    assert not re.match(pattern, 'D')


def test_many_ascii_characters():
    """Test generating pattern for many ASCII characters."""
    gen = RegexGenerator()
    pattern = gen.generate_pattern(set(range(65, 70)))  # ASCII 'A' through 'E'
    assert pattern == '[ABCDE]'
    for c in 'ABCDE':
        assert re.match(pattern, c)
    assert not re.match(pattern, 'F')


def test_special_characters():
    """Test generating pattern for regex special characters."""
    gen = RegexGenerator()
    pattern = gen.generate_pattern({ord(c) for c in r'[]'})
    assert pattern == r'(?:\[\])'
    assert re.match(pattern, '[')
    assert re.match(pattern, ']')


def test_unicode_characters():
    """Test generating pattern for Unicode characters."""
    gen = RegexGenerator()
    # Unicode 'GREEK CAPITAL LETTER ALPHA' (U+0391)
    pattern = gen.generate_pattern({0x0391})
    assert pattern == r'\u0391'
    assert re.match(pattern, 'Α')


def test_code_point_set():
    """Test generating pattern from CodePointSet."""
    gen = RegexGenerator()
    cps = CodePointSet()
    cps.add_range(65, 67)  # ASCII 'A' through 'C'
    pattern = gen.generate_pattern(cps)
    assert pattern == '[A-C]'
    for c in 'ABC':
        assert re.match(pattern, c)
    assert not re.match(pattern, 'D')


def test_empty_set():
    """Test generating pattern for empty set."""
    gen = RegexGenerator()
    pattern = gen.generate_pattern(set())
    assert pattern == '(?!)'
    assert not re.match(pattern, '')
    assert not re.match(pattern, 'a')


def test_supplementary_plane():
    """Test generating pattern for supplementary plane characters."""
    gen = RegexGenerator()
    # '𐐀' DESERET CAPITAL LETTER LONG I (U+10400)
    pattern = gen.generate_pattern({0x10400})
    assert pattern == r'\U00010400'
    assert re.match(pattern, '𐐀')


def test_pattern_optimization():
    """Test pattern optimization integration."""
    gen = RegexGenerator()

    # Test with optimization enabled (default)
    pattern = gen.generate_pattern({65, 66, 67}, optimize=True)
    assert pattern == 'ABC'  # Should be optimized from '(?:ABC)'

    # Test with optimization disabled
    pattern = gen.generate_pattern({65, 66, 67}, optimize=False)
    assert pattern == '(?:ABC)'  # Should remain unoptimized

    # Test with readability priority
    pattern = gen.generate_pattern({65, 66, 67}, prioritize='readability')
    assert ' ' in pattern  # Should contain spaces for readability

    # Test with custom optimizer
    opt = Optimizer()
    gen_with_opt = RegexGenerator(optimizer=opt)
    pattern = gen_with_opt.generate_pattern({65, 66, 67})
    assert pattern == 'ABC'  # Should use the provided optimizer


def test_invalid_optimization_priority():
    """Test handling of invalid optimization priority."""
    gen = RegexGenerator()
    with pytest.raises(ValueError):
        gen.generate_pattern({65}, prioritize='invalid')