"""Integration tests for the Unicode Regex Generator."""

import re
import pytest
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.optimizer import Optimizer


def test_generate_letter_pattern():
    """Test generating an optimized pattern for letters."""
    # Setup components
    ud = UnicodeData()
    gen = RegexGenerator()
    opt = Optimizer()

    # Get all uppercase letters
    upper_letters = ud.get_code_points_by_category('Lu')
    assert upper_letters  # Ensure we got some code points

    # Generate pattern
    pattern = gen.generate_pattern(upper_letters)
    assert pattern  # Ensure pattern was generated

    # Optimize pattern
    optimized = opt.optimize_pattern(pattern, prioritize='size')
    assert optimized  # Ensure optimization worked

    # Verify pattern works
    regex = re.compile(optimized)
    assert regex.match('A')  # Should match uppercase
    assert not regex.match('a')  # Should not match lowercase
    assert not regex.match('1')  # Should not match numbers


def test_custom_character_set():
    """Test creating and using a custom character set."""
    # Setup components
    cps = CodePointSet()
    gen = RegexGenerator()
    opt = Optimizer()

    # Create a set of ASCII digits and uppercase letters
    cps.add_range(48, 57)  # Digits 0-9
    cps.add_range(65, 90)  # Letters A-Z

    # Generate and optimize pattern
    pattern = gen.generate_pattern(cps)
    optimized = opt.optimize_pattern(pattern)

    # Verify pattern
    regex = re.compile(optimized)
    for c in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        assert regex.match(c), f"Should match {c}"
    for c in 'abcdefghijklmnopqrstuvwxyz':
        assert not regex.match(c), f"Should not match {c}"


def test_unicode_categories_combination():
    """Test combining multiple Unicode categories."""
    ud = UnicodeData()
    gen = RegexGenerator()
    opt = Optimizer()

    # Get letters and numbers
    letters = ud.get_code_points_by_category('L')  # All letters
    numbers = ud.get_code_points_by_category('N')  # All numbers

    # Combine categories
    combined = letters | numbers  # Using CodePointSet's union operation

    # Generate and optimize pattern
    pattern = gen.generate_pattern(combined)
    optimized = opt.optimize_pattern(pattern, prioritize='readability')

    # Verify pattern
    regex = re.compile(optimized)
    # Test various characters
    assert regex.match('A')  # Latin uppercase
    assert regex.match('a')  # Latin lowercase
    assert regex.match('0')  # Digit
    assert regex.match('Α')  # Greek uppercase
    assert regex.match('α')  # Greek lowercase
    assert regex.match('١')  # Arabic-Indic digit
    assert not regex.match('.')  # Punctuation
    assert not regex.match(' ')  # Space


def test_pattern_optimization_workflow():
    """Test the complete pattern optimization workflow."""
    gen = RegexGenerator()
    opt = Optimizer()

    # Create a pattern that could be optimized
    initial_set = {ord(c) for c in 'aeiouAEIOU'}  # Vowels

    # Generate initial pattern
    pattern = gen.generate_pattern(initial_set)

    # Test different optimization priorities
    size_optimized = opt.optimize_pattern(pattern, prioritize='size')
    readable_optimized = opt.optimize_pattern(pattern, prioritize='readability')

    # Verify both patterns work correctly
    for p in [size_optimized, readable_optimized]:
        regex = re.compile(p)
        # Should match vowels
        for vowel in 'aeiouAEIOU':
            assert regex.match(vowel), f"{p} should match {vowel}"
        # Should not match consonants
        for consonant in 'bcdfgBCDFG':
            assert not regex.match(consonant), f"{p} should not match {consonant}"

    # Size-optimized should be shorter
    assert len(size_optimized) <= len(readable_optimized)


def test_unicode_property_pattern():
    """Test generating patterns based on Unicode properties."""
    ud = UnicodeData()
    gen = RegexGenerator()
    opt = Optimizer()

    # Get decimal numbers
    decimals = ud.get_code_points_by_property('decimal', '7')
    assert decimals  # Should find at least ASCII '7'

    # Generate and optimize pattern
    pattern = gen.generate_pattern(decimals)
    optimized = opt.optimize_pattern(pattern)

    # Verify pattern
    regex = re.compile(optimized)
    assert regex.match('7')  # ASCII seven
    assert not regex.match('8')  # Different digit
    assert not regex.match('A')  # Not a number


def test_performance_optimization():
    """Test that optimized patterns perform better."""
    gen = RegexGenerator()
    opt = Optimizer()

    # Create a deliberately suboptimal pattern
    code_points = set(range(65, 91))  # A-Z
    pattern = gen.generate_pattern(code_points)

    # Create an unoptimized version with unnecessary groups
    unoptimized = ''.join(f'(?:[{c}])' for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    # Optimize the pattern
    optimized = opt.optimize_pattern(pattern)

    # Benchmark both patterns
    test_strings = ['A', 'M', 'Z', 'a']  # Mix of matching and non-matching
    unopt_results = opt.benchmark_pattern(unoptimized, test_strings)
    opt_results = opt.benchmark_pattern(optimized, test_strings)

    # Optimized pattern should be smaller
    assert len(optimized) < len(unoptimized)

    # Optimized pattern should compile faster
    assert opt_results['compilation_time'] <= unopt_results['compilation_time']