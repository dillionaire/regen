"""Unit tests for Unicode property file handling."""

import pytest
from pathlib import Path
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.code_point_set import CodePointSet


@pytest.fixture
def ud():
    """Create a fresh UnicodeData instance for each test."""
    return UnicodeData()


class TestPropertyFileLoading:
    """Test loading and parsing of property files."""

    def test_script_file_loading(self, ud):
        """Test loading the Scripts.txt file."""
        # Get Latin script properties
        latin = ud.get_property('Script', 'Latin')
        assert isinstance(latin, CodePointSet)
        assert 0x0041 in latin  # 'A'
        assert 0x007A in latin  # 'z'
        assert 0x0370 not in latin  # Greek letter

    def test_multiple_ranges_per_property(self, ud):
        """Test handling multiple ranges for the same property."""
        # Latin script has multiple ranges
        latin = ud.get_property('Script', 'Latin')
        # Test characters from different Latin ranges
        assert 0x0041 in latin  # Basic Latin 'A'
        assert 0x00C0 in latin  # Latin-1 'À'
        assert 0x0100 in latin  # Extended-A 'Ā'

    def test_property_caching(self, ud):
        """Test property caching behavior."""
        # First access should load file
        _ = ud.get_property('Script', 'Latin')
        assert 'Script' in ud._property_cache

        # Second access should use cache
        latin = ud.get_property('Script', 'Latin')
        assert isinstance(latin, CodePointSet)

    def test_all_properties_in_file(self, ud):
        """Test retrieving all properties from a file."""
        properties = ud.get_all_properties('Script')
        assert isinstance(properties, list)
        assert 'Latin' in properties
        assert 'Greek' in properties
        assert 'Cyrillic' in properties

    def test_numeric_property_loading(self, ud):
        """Test loading numeric property values."""
        # Test decimal digits
        for i in range(10):
            digit_set = ud.get_property('decimal', str(i))
            assert isinstance(digit_set, CodePointSet)
            assert ord(str(i)) in digit_set

    def test_property_file_comments(self, ud):
        """Test proper handling of file comments."""
        # Comments should be ignored when loading properties
        latin = ud.get_property('Script', 'Latin')
        assert isinstance(latin, CodePointSet)
        # Verify no comment markers in property names
        properties = ud.get_all_properties('Script')
        assert not any('#' in prop for prop in properties)


class TestPropertyFileErrors:
    """Test error handling in property file operations."""

    def test_nonexistent_file(self, ud):
        """Test handling of non-existent property files."""
        with pytest.raises(ValueError, match="Property file not found"):
            ud.get_property('NonExistentFile', 'Value')

    def test_invalid_property_value(self, ud):
        """Test handling of invalid property values."""
        with pytest.raises(ValueError):
            ud.get_property('Script', 'NonExistentScript')

    def test_malformed_range(self, tmp_path):
        """Test handling of malformed range specifications."""
        # Create a temporary property file with malformed ranges
        test_file = tmp_path / "test.txt"
        test_file.write_text("INVALID..XYZ; Test\n")

        ud = UnicodeData()
        with pytest.raises(ValueError):
            ud.get_property('test', 'Test')

    def test_invalid_code_points(self, tmp_path):
        """Test handling of invalid code point values."""
        # Create a temporary property file with invalid code points
        test_file = tmp_path / "test.txt"
        test_file.write_text("110000..110001; Test\n")  # Beyond Unicode range

        ud = UnicodeData()
        with pytest.raises(ValueError):
            ud.get_property('test', 'Test')


class TestPropertyFileIntegration:
    """Test integration with other components."""

    def test_script_category_interaction(self, ud):
        """Test interaction between scripts and categories."""
        # Get Latin uppercase letters
        latin = ud.get_property('Script', 'Latin')
        uppercase = ud.get_category('Lu')
        latin_upper = latin & uppercase

        assert 0x0041 in latin_upper  # Latin 'A'
        assert 0x0061 not in latin_upper  # Latin 'a'
        assert 0x0391 not in latin_upper  # Greek 'Α'

    def test_multiple_property_combination(self, ud):
        """Test combining multiple property lookups."""
        # Combine multiple scripts
        latin = ud.get_property('Script', 'Latin')
        greek = ud.get_property('Script', 'Greek')
        cyrillic = ud.get_property('Script', 'Cyrillic')

        combined = latin | greek | cyrillic
        assert 0x0041 in combined  # Latin 'A'
        assert 0x0391 in combined  # Greek 'Α'
        assert 0x0410 in combined  # Cyrillic 'А'

    def test_property_set_operations(self, ud):
        """Test set operations with property sets."""
        latin = ud.get_property('Script', 'Latin')
        common = ud.get_property('Script', 'Common')

        # Test union
        combined = latin | common
        assert 0x0041 in combined  # Latin 'A'
        assert 0x0374 in combined  # Common character

        # Test intersection
        intersection = latin & common
        assert not intersection  # Should be empty

        # Test difference
        diff = latin - common
        assert 0x0041 in diff  # Latin 'A'
        assert 0x0374 not in diff  # Common character


class TestPropertyFilePerformance:
    """Test performance aspects of property file handling."""

    def test_repeated_access(self, ud):
        """Test performance of repeated property access."""
        import time

        # First access (loads file)
        start = time.perf_counter()
        _ = ud.get_property('Script', 'Latin')
        first_access = time.perf_counter() - start

        # Second access (should use cache)
        start = time.perf_counter()
        _ = ud.get_property('Script', 'Latin')
        second_access = time.perf_counter() - start

        # Cached access should be significantly faster
        assert second_access < first_access

    def test_large_property_set(self, ud):
        """Test handling of large property sets."""
        # Get a large set (all Latin characters)
        latin = ud.get_property('Script', 'Latin')

        # Should handle large sets efficiently
        assert len(latin) > 1000  # Latin script has many characters

        # Operations on large sets should work
        subset = CodePointSet({0x0041, 0x0042})  # A, B
        intersection = latin & subset
        assert len(intersection) == 2