"""Test suite for edge cases and error conditions."""

import pytest
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.optimizer import Optimizer


@pytest.fixture
def ud():
    """Create a UnicodeData instance for testing."""
    return UnicodeData()


@pytest.fixture
def generator():
    """Create a RegexGenerator instance for testing."""
    return RegexGenerator()


@pytest.fixture
def optimizer():
    """Create an Optimizer instance for testing."""
    return Optimizer()


class TestUnicodeDataEdgeCases:
    """Test edge cases and error conditions in UnicodeData."""

    def test_invalid_category(self, ud):
        """Test handling of invalid Unicode categories."""
        with pytest.raises(ValueError, match="Invalid category"):
            ud.get_category("XX")  # Invalid category code

        with pytest.raises(ValueError, match="Invalid category"):
            ud.get_category("")  # Empty category

        with pytest.raises(ValueError, match="Invalid category"):
            ud.get_category("Lu2")  # Invalid format

    def test_invalid_property(self, ud):
        """Test handling of invalid property lookups."""
        with pytest.raises(ValueError, match="Invalid property"):
            ud.get_property("NonexistentProperty", "Value")

        with pytest.raises(ValueError, match="Invalid value"):
            ud.get_property("Script", "NonexistentScript")

        with pytest.raises(ValueError, match="Invalid property"):
            ud.get_property("", "")  # Empty property and value

    def test_invalid_code_points(self, ud):
        """Test handling of invalid code points."""
        with pytest.raises(ValueError, match="Invalid code point"):
            ud.get_property(-1, "name")  # Negative code point

        with pytest.raises(ValueError, match="Invalid code point"):
            ud.get_property(0x110000, "name")  # Code point too large

        with pytest.raises(ValueError, match="Invalid code point"):
            ud.get_property(0x10FFFF + 1, "name")  # Beyond Unicode range

    def test_surrogate_code_points(self, ud):
        """Test handling of surrogate code points."""
        # Surrogates should be handled gracefully
        for cp in range(0xD800, 0xE000):
            with pytest.raises(ValueError, match="Surrogate code point"):
                ud.get_property(cp, "name")

    def test_nonexistent_properties(self, ud):
        """Test handling of valid code points with nonexistent properties."""
        # Valid code point but property doesn't exist
        with pytest.raises(ValueError, match="Property not found"):
            ud.get_property(0x0041, "nonexistent")

        # Valid code point but no numeric value
        with pytest.raises(ValueError, match="No numeric value"):
            ud.get_property(0x0041, "numeric")  # 'A' has no numeric value


class TestCodePointSetEdgeCases:
    """Test edge cases and error conditions in CodePointSet."""

    def test_empty_set_operations(self):
        """Test operations with empty sets."""
        empty_set = CodePointSet(set())
        normal_set = CodePointSet({0x0041, 0x0042})  # A, B

        # Operations with empty set
        assert len(empty_set) == 0
        assert len(empty_set | normal_set) == 2
        assert len(empty_set & normal_set) == 0
        assert len(empty_set - normal_set) == 0
        assert len(normal_set - empty_set) == 2

    def test_invalid_code_points_in_set(self):
        """Test handling of invalid code points in set creation."""
        with pytest.raises(ValueError, match="Invalid code point"):
            CodePointSet({-1})  # Negative code point

        with pytest.raises(ValueError, match="Invalid code point"):
            CodePointSet({0x110000})  # Beyond Unicode range

        with pytest.raises(ValueError, match="Invalid code point"):
            CodePointSet({0x0041, -1, 0x0042})  # Mix of valid and invalid

    def test_set_operation_type_checking(self):
        """Test type checking in set operations."""
        valid_set = CodePointSet({0x0041})

        with pytest.raises(TypeError):
            valid_set | {0x0042}  # Operation with regular set

        with pytest.raises(TypeError):
            valid_set & [0x0042]  # Operation with list

        with pytest.raises(TypeError):
            valid_set - 0x0042  # Operation with integer


class TestRegexGeneratorEdgeCases:
    """Test edge cases and error conditions in RegexGenerator."""

    def test_empty_pattern_generation(self, generator):
        """Test generation of patterns from empty sets."""
        empty_set = CodePointSet(set())
        pattern = generator.generate_pattern(empty_set)
        assert pattern == r"[]"  # or whatever your empty pattern representation is

    def test_large_pattern_generation(self, generator):
        """Test generation of patterns with large numbers of code points."""
        # Create a large set of consecutive code points
        large_set = CodePointSet(set(range(0x0000, 0x1000)))
        pattern = generator.generate_pattern(large_set)
        assert pattern  # Pattern should be generated
        assert len(pattern) < len(large_set) * 6  # Pattern should be optimized

    def test_invalid_input_types(self, generator):
        """Test handling of invalid input types."""
        with pytest.raises(TypeError):
            generator.generate_pattern([0x0041])  # List instead of CodePointSet

        with pytest.raises(TypeError):
            generator.generate_pattern({0x0041})  # Set instead of CodePointSet

        with pytest.raises(TypeError):
            generator.generate_pattern("A")  # String instead of CodePointSet


class TestOptimizerEdgeCases:
    """Test edge cases and error conditions in Optimizer."""

    def test_invalid_pattern_optimization(self, optimizer):
        """Test optimization of invalid patterns."""
        with pytest.raises(ValueError, match="Invalid pattern"):
            optimizer.optimize("[")  # Unclosed character class

        with pytest.raises(ValueError, match="Invalid pattern"):
            optimizer.optimize("(")  # Unclosed group

        with pytest.raises(ValueError, match="Invalid pattern"):
            optimizer.optimize("\\")  # Trailing backslash

    def test_empty_pattern_optimization(self, optimizer):
        """Test optimization of empty or whitespace patterns."""
        assert optimizer.optimize("") == ""
        assert optimizer.optimize(" ") == " "
        assert optimizer.optimize("\t") == "\t"

    def test_complex_pattern_optimization(self, optimizer):
        """Test optimization of complex patterns."""
        # Pattern with multiple groups, alternations, and quantifiers
        complex_pattern = r"(?:[a-z]+|[0-9]+){1,3}|\s+|\w+|[\u0370-\u03FF]+"
        optimized = optimizer.optimize(complex_pattern)
        assert optimized  # Should produce valid pattern
        assert len(optimized) <= len(complex_pattern)  # Should not increase size

    def test_range_compression_edge_cases(self, optimizer):
        """Test edge cases in range compression."""
        # Single character range
        assert optimizer.compress_ranges("[a-a]") == "a"

        # Adjacent ranges
        assert optimizer.compress_ranges("[a-cx-z]") == "[a-c|x-z]"

        # Overlapping ranges should be merged
        assert optimizer.compress_ranges("[a-mb-z]") == "[a-z]"

        # Invalid ranges should raise error
        with pytest.raises(ValueError, match="Invalid range"):
            optimizer.compress_ranges("[z-a]")  # Reversed range