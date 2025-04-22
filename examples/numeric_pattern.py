from regen import RegexGenerator

def create_numeric_pattern(*strings):
    """
    Generate an optimized regex pattern that matches exact strings,
    automatically detecting and optimizing numeric alternations.

    Args:
        *strings: Variable number of strings to match

    Returns:
        str: Optimized regex pattern

    Example:
        >>> create_numeric_pattern("2024_Launch", "2025_Launch")
        '202[45]_Launch'
    """
    gen = RegexGenerator()
    return gen.create_optimized_pattern(strings)

def test_numeric_pattern():
    """Test the numeric pattern optimization with various inputs."""
    test_cases = [
        (["2024_Launch", "2025_Launch"], "202[45]_Launch"),
        (["2024_Start", "2025_Start", "2026_Start"], "202[456]_Start"),
        (["v1.2.3", "v1.2.4"], "v1\\.2\\.[34]"),
        (["test123", "test124", "test125"], "test12[345]"),
    ]

    print("Testing Numeric Pattern Optimization:")
    print("=====================================")

    for inputs, expected in test_cases:
        pattern = create_numeric_pattern(*inputs)
        match = pattern == expected
        result = "✓" if match else "✗"
        print(f"\n{result} Input: {inputs}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {pattern}")

        # Verify pattern matches all input strings
        import re
        regex = re.compile(f"^{pattern}$")
        for input_str in inputs:
            matches = bool(regex.match(input_str))
            print(f"  Match '{input_str}': {'✓' if matches else '✗'}")

if __name__ == "__main__":
    test_numeric_pattern()