"""Integration tests for edge cases and error handling."""

import pytest
from unicode_regex.code_point_set import CodePointSet
from unicode_regex.regex_generator import RegexGenerator
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.optimizer import Optimizer


@pytest.fixture
def components():
    """Create instances of all components needed for testing."""
    return {
        'unicode_data': UnicodeData(),
        'generator': RegexGenerator(),
        'optimizer': Optimizer()
    }


class TestEdgeCases:
    """Test handling of edge cases and error conditions."""

    def test_invalid_code_points(self, components):
        """Test handling of invalid Unicode code points."""
        ud = components['unicode_data']
        gen = components['generator']

        # Test code points beyond Unicode range
        with pytest.raises(ValueError, match=r".*invalid code point.*"):
            CodePointSet({0x110000})  # First invalid code point

        # Test negative code points
        with pytest.raises(ValueError, match=r".*invalid code point.*"):
            CodePointSet({-1})

    def test_invalid_properties(self, components):
        """Test handling of invalid Unicode properties."""
        ud = components['unicode_data']

        # Test non-existent property
        with pytest.raises(ValueError, match=r".*invalid property.*"):
            ud.get_property("NonExistentProperty", "Value")

        # Test invalid property value
        with pytest.raises(ValueError, match=r".*invalid value.*"):
            ud.get_property("Script", "NonExistentScript")

    def test_empty_patterns(self, components):
        """Test handling of empty patterns and sets."""
        gen = components['generator']
        opt = components['optimizer']

        # Empty set should produce valid regex
        empty_set = CodePointSet()
        pattern = gen.generate_pattern(empty_set)
        assert pattern == "[]", "Empty set should produce empty character class"

        # Empty alternation should be handled
        assert gen.generate_alternation_pattern([]) == "[]", "Empty alternation should produce empty class"

    def test_boundary_conditions(self, components):
        """Test handling of Unicode boundary conditions."""
        ud = components['unicode_data']
        gen = components['generator']

        # Test surrogate code points
        surrogates = CodePointSet()
        surrogates.add_range(0xD800, 0xDFFF)
        pattern = gen.generate_pattern(surrogates)
        assert pattern, "Should handle surrogate range"

        # Test maximum valid code point
        max_point = CodePointSet({0x10FFFF})
        pattern = gen.generate_pattern(max_point)
        assert pattern, "Should handle maximum code point"

    def test_optimization_edge_cases(self, components):
        """Test edge cases in pattern optimization."""
        gen = components['generator']
        opt = components['optimizer']

        # Single character optimization
        single_char = CodePointSet({ord('a')})
        pattern = gen.generate_pattern(single_char, prioritize='size')
        assert pattern == 'a', "Single character should not be over-optimized"

        # Large range optimization
        large_set = CodePointSet()
        large_set.add_range(0, 0x10FFFF)
        pattern = gen.generate_pattern(large_set, prioritize='size')
        assert pattern, "Should handle full Unicode range"

    def test_error_propagation(self, components):
        """Test proper error propagation through component chain."""
        ud = components['unicode_data']
        gen = components['generator']

        # Test error propagation from UnicodeData through RegexGenerator
        with pytest.raises(ValueError):
            invalid_set = ud.get_property("InvalidProperty", "InvalidValue")
            gen.generate_pattern(invalid_set)

        # Test error handling in pattern generation
        with pytest.raises(ValueError):
            gen.generate_pattern(None)

    def test_concurrent_access(self, components):
        """Test handling of concurrent access to components."""
        import concurrent.futures
        import threading

        ud = components['unicode_data']
        gen = components['generator']

        def access_components():
            """Access components concurrently."""
            try:
                letters = ud.get_category('L')
                pattern = gen.generate_pattern(letters)
                return True
            except Exception as e:
                return False

        # Test concurrent access with thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(lambda _: access_components(), range(10)))
            assert all(results), "Concurrent access should be thread-safe"