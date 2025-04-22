import pytest
import re
from regen import RegexGenerator

@pytest.fixture
def gen():
    """Fixture providing a RegexGenerator instance."""
    return RegexGenerator()

class TestRegexGenerator:
    def test_empty_input(self, gen):
        """Test behavior with empty input."""
        assert gen.create_alternation([]) == ""
        assert gen.create_optimized_pattern([]) == ""

    def test_single_pattern(self, gen):
        """Test behavior with single input pattern."""
        assert gen.create_alternation(["test"]) == "test"
        assert gen.create_optimized_pattern(["test"]) == "test"

    def test_alternation(self, gen):
        """Test alternation pattern generation."""
        patterns = ["foo", "bar", "baz"]
        result = gen.create_alternation(patterns)
        assert result == "(?:foo|bar|baz)"

        # Test with special characters
        patterns = ["file.txt", "file.pdf"]
        result = gen.create_alternation(patterns)
        assert result == r"(?:file\.txt|file\.pdf)"

    def test_numeric_optimization(self, gen):
        """Test numeric pattern optimization."""
        test_cases = [
            (["2024_Launch", "2025_Launch"], "202[45]_Launch"),
            (["v1.2.3", "v1.2.4"], r"v1\.2\.[34]"),
            (["test123", "test124", "test125"], "test12[345]"),
            (["2024_Start", "2025_Start", "2026_Start"], "202[456]_Start"),
        ]

        for inputs, expected in test_cases:
            result = gen.create_optimized_pattern(inputs)
            assert result == expected

            # Verify pattern matches all inputs
            pattern = re.compile(f"^{result}$")
            for input_str in inputs:
                assert pattern.match(input_str) is not None

    def test_escape(self, gen):
        """Test pattern escaping."""
        special_chars = ".^$*+?{}[]\\|()"
        for char in special_chars:
            pattern = f"test{char}pattern"
            escaped = gen.escape(pattern)
            assert char not in escaped or escaped[escaped.index(char)-1] == "\\"

    def test_non_numeric_patterns(self, gen):
        """Test patterns that can't be numerically optimized."""
        patterns = ["test_a", "test_b", "test_c"]
        result = gen.create_optimized_pattern(patterns)
        assert result == "(?:test_a|test_b|test_c)"

    def test_mixed_patterns(self, gen):
        """Test patterns with both numeric and non-numeric differences."""
        patterns = ["test1a", "test2b", "test3c"]
        result = gen.create_optimized_pattern(patterns)
        assert result == "(?:test1a|test2b|test3c)"

    def test_pattern_validation(self, gen):
        """Test that generated patterns are valid regex."""
        test_cases = [
            ["2024_Launch", "2025_Launch"],
            ["v1.2.3", "v1.2.4"],
            ["test123", "test124", "test125"],
            ["file.txt", "file.pdf"],
            ["test_a", "test_b", "test_c"],
        ]

        for inputs in test_cases:
            pattern = gen.create_optimized_pattern(inputs)
            try:
                re.compile(pattern)
            except re.error as e:
                pytest.fail(f"Invalid regex pattern '{pattern}': {e}")

    def test_edge_cases(self, gen):
        """Test edge cases and potential corner cases."""
        # Empty strings
        assert gen.create_optimized_pattern([""]) == ""

        # Single characters
        assert gen.create_optimized_pattern(["a", "b", "c"]) == "[abc]"

        # Special regex characters
        patterns = [r"\test", r"*test", r"+test"]
        result = gen.create_optimized_pattern(patterns)
        for p in patterns:
            assert re.compile(result).match(p) is not None