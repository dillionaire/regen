"""Examples demonstrating the usage of the Regen library.

This module provides practical examples of using the Regen library for Unicode-aware
regex pattern generation and optimization. Each example includes explanations and
expected outputs.
"""

from unicode_regex.unicode_data import UnicodeData
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.optimizer import Optimizer, OptimizationPriority
from unicode_regex.code_point_set import CodePointSet

def example_unicode_data():
    """Examples of working with Unicode data and properties."""
    print("\n=== Unicode Data Examples ===")

    # Initialize UnicodeData
    ud = UnicodeData()

    # Get category information
    print("\nCategory Examples:")
    print(f"Category of 'A' (65): {ud.get_category(65)}")
    print(f"Category of '1' (49): {ud.get_category(49)}")

    # Get property information
    print("\nProperty Examples:")
    print(f"Name of 'A': {ud.get_property(65, 'name')}")
    print(f"Numeric value of '½': {ud.get_property(ord('½'), 'numeric')}")

    # Get script information
    print("\nScript Examples:")
    print(f"Script of 'A' (65): {ud.get_script(65)}")
    print(f"Script of 'Α' (913): {ud.get_script(913)}")  # Greek Alpha

    # Working with code point sets
    latin_upper = ud.get_category_set('Lu')
    latin_lower = ud.get_category_set('Ll')
    all_letters = latin_upper | latin_lower
    print(f"\nNumber of uppercase letters: {len(latin_upper)}")
    print(f"Number of lowercase letters: {len(latin_lower)}")
    print(f"Total number of letters: {len(all_letters)}")

def example_regex_generation():
    """Examples of generating regex patterns."""
    print("\n=== Regex Generation Examples ===")

    # Initialize RegexGenerator
    rg = RegexGenerator()

    # Generate patterns for common ranges
    digits = CodePointSet(range(0x0030, 0x003A))  # 0-9
    print(f"\nDigit pattern: {rg.generate_pattern(digits)}")  # Should output: \d

    # Generate pattern for custom ranges
    latin_upper = CodePointSet(range(0x0041, 0x005B))  # A-Z
    print(f"Uppercase pattern: {rg.generate_pattern(latin_upper)}")

    # Generate alternation pattern
    patterns = ['foo', 'bar', 'baz']
    print(f"\nAlternation pattern (size): {rg.generate_alternation_pattern(patterns, 'size')}")
    print(f"Alternation pattern (readability): {rg.generate_alternation_pattern(patterns, 'readability')}")

    # Generate pattern for multiple ranges
    greek_upper = CodePointSet(range(0x0391, 0x03A2))  # Α-Ω
    combined = latin_upper | greek_upper
    print(f"\nCombined Latin/Greek uppercase: {rg.generate_pattern(combined)}")

def example_pattern_optimization():
    """Examples of pattern optimization."""
    print("\n=== Pattern Optimization Examples ===")

    # Initialize Optimizer
    opt = Optimizer()

    # Optimize for size
    pattern = '[a]|[b-c]|[d-f]'
    optimized = opt.optimize_pattern(pattern, 'size')
    print(f"\nOriginal pattern: {pattern}")
    print(f"Size-optimized: {optimized}")

    # Optimize for readability
    pattern = 'a|b|c|[d-f]|[g-i]'
    readable = opt.optimize_pattern(pattern, 'readability')
    print(f"\nOriginal pattern: {pattern}")
    print(f"Readability-optimized: {readable}")

    # Benchmark patterns
    test_string = "aaabbbccc"
    pattern1 = '[a-c]+'
    pattern2 = 'a+|b+|c+'

    benchmark1 = opt.benchmark_pattern(pattern1, test_string)
    benchmark2 = opt.benchmark_pattern(pattern2, test_string)

    print("\nBenchmark Results:")
    print(f"Pattern 1 ({pattern1}):")
    print(f"  Size: {benchmark1['pattern_size']}")
    print(f"  Average match time: {benchmark1['avg_match_time']:.6f}s")

    print(f"\nPattern 2 ({pattern2}):")
    print(f"  Size: {benchmark2['pattern_size']}")
    print(f"  Average match time: {benchmark2['avg_match_time']:.6f}s")

def example_complex_patterns():
    """Examples of creating complex patterns using multiple features."""
    print("\n=== Complex Pattern Examples ===")

    ud = UnicodeData()
    rg = RegexGenerator()
    opt = Optimizer()

    # Create a pattern for matching multilingual identifiers
    # (letters from Latin, Greek, and Cyrillic scripts, plus numbers and underscore)
    latin = ud.get_property('Scripts', 'Latin')
    greek = ud.get_property('Scripts', 'Greek')
    cyrillic = ud.get_property('Scripts', 'Cyrillic')
    digits = ud.get_category_set('Nd')

    identifier_chars = latin | greek | cyrillic | digits
    identifier_chars.add(ord('_'))

    # First character can't be a digit
    first_char = latin | greek | cyrillic
    first_char.add(ord('_'))

    print("\nMultilingual Identifier Pattern:")
    first = rg.generate_pattern(first_char)
    rest = rg.generate_pattern(identifier_chars)
    identifier_pattern = f"{first}{rest}*"
    print(f"Pattern: {identifier_pattern}")

    # Create a pattern for matching numeric values in different scripts
    numeric_pattern = '|'.join([
        rg.generate_pattern(ud.get_category_set('Nd')),  # Decimal digits
        rg.generate_pattern(ud.get_category_set('No')),  # Other numbers
        rg.generate_pattern(ud.get_category_set('Nl'))   # Letter numbers
    ])
    numeric_pattern = opt.optimize_pattern(numeric_pattern, 'readability')
    print(f"\nNumeric Pattern: {numeric_pattern}")

if __name__ == '__main__':
    # Run all examples
    example_unicode_data()
    example_regex_generation()
    example_pattern_optimization()
    example_complex_patterns()