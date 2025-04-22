"""Unit tests for the UnicodeData class."""

import pytest
from pathlib import Path
from unicode_regex.unicode_data import UnicodeData
from unicode_regex.code_point_set import CodePointSet


@pytest.fixture
def ud():
    """Create a fresh UnicodeData instance for each test."""
    return UnicodeData()


class TestUnicodeDataInitialization:
    """Test initialization and caching behavior."""

    def test_initial_state(self, ud):
        """Test the initial state of UnicodeData."""
        assert not ud._initialized
        assert isinstance(ud._category_cache, dict)
        assert isinstance(ud._property_cache, dict)
        assert len(ud._category_cache) == 0
        assert len(ud._property_cache) == 0

    def test_ensure_initialized(self, ud):
        """Test initialization of category cache."""
        ud._ensure_initialized()
        assert ud._initialized
        assert len(ud._category_cache) == len(UnicodeData.CATEGORIES)
        assert all(isinstance(v, CodePointSet) for v in ud._category_cache.values())

    def test_lazy_initialization(self, ud):
        """Test that initialization happens lazily."""
        assert not ud._initialized
        _ = ud.get_category('Lu')  # Should trigger initialization
        assert ud._initialized


class TestCategoryOperations:
    """Test Unicode category operations."""

    def test_get_category_by_code_point(self, ud):
        """Test getting category for specific code points."""
        assert ud.get_category(0x0041) == 'Lu'  # 'A'
        assert ud.get_category(0x0061) == 'Ll'  # 'a'
        assert ud.get_category(0x0030) == 'Nd'  # '0'
        assert ud.get_category(0x0020) == 'Zs'  # Space

    def test_get_category_by_name(self, ud):
        """Test getting code points for categories."""
        uppercase = ud.get_category('Lu')
        assert isinstance(uppercase, CodePointSet)
        assert 0x0041 in uppercase  # 'A'
        assert 0x0061 not in uppercase  # 'a'

    def test_major_categories(self, ud):
        """Test major category handling."""
        letters = ud.get_category('L')
        assert isinstance(letters, CodePointSet)
        assert 0x0041 in letters  # 'A'
        assert 0x0061 in letters  # 'a'
        assert 0x0030 not in letters  # '0'

    def test_invalid_categories(self, ud):
        """Test handling of invalid categories."""
        with pytest.raises(ValueError, match="Unknown Unicode category"):
            ud.get_category('XX')
        with pytest.raises(ValueError, match="Unknown Unicode category"):
            ud.get_category('X')

    def test_invalid_code_points(self, ud):
        """Test handling of invalid code points."""
        with pytest.raises(ValueError, match="Invalid code point"):
            ud.get_category(-1)
        with pytest.raises(ValueError, match="Invalid code point"):
            ud.get_category(0x110000)

    def test_get_code_points_by_category(self, ud):
        """Test getting code points by category."""
        points = ud.get_code_points_by_category('Lu')
        assert isinstance(points, set)
        assert 0x0041 in points  # 'A'
        assert 0x0061 not in points  # 'a'

    def test_get_category_set(self, ud):
        """Test getting category as CodePointSet."""
        category_set = ud.get_category_set('Lu')
        assert isinstance(category_set, CodePointSet)
        assert 0x0041 in category_set  # 'A'
        assert 0x0061 not in category_set  # 'a'


class TestPropertyOperations:
    """Test Unicode property operations."""

    def test_get_property_name(self, ud):
        """Test getting character names."""
        # Test basic ASCII
        assert ud.get_property(0x0041, 'name') == 'LATIN CAPITAL LETTER A'
        assert ud.get_property(0x0000, 'name') == 'NULL'

        # Test special characters
        assert ud.get_property(0x00A9, 'name') == 'COPYRIGHT SIGN'
        assert ud.get_property(0x20AC, 'name') == 'EURO SIGN'

        # Test error handling
        with pytest.raises(ValueError, match=r"No name found for code point: U\+10FFFF"):
            ud.get_property(0x10FFFF, 'name')
        with pytest.raises(ValueError, match="Invalid code point:"):
            ud.get_property(0x110000, 'name')

    def test_get_property_numeric(self, ud):
        """Test getting numeric values."""
        # Test ASCII digits
        assert ud.get_property(0x0030, 'numeric') == 0.0  # '0'
        assert ud.get_property(0x0039, 'numeric') == 9.0  # '9'

        # Test fractions
        assert ud.get_property(0x00BC, 'numeric') == 0.25  # '¼'
        assert ud.get_property(0x00BD, 'numeric') == 0.5   # '½'
        assert ud.get_property(0x00BE, 'numeric') == 0.75  # '¾'

        # Test non-numeric characters
        with pytest.raises(ValueError, match=r"No numeric value for code point: U\+0041"):
            ud.get_property(0x0041, 'numeric')  # 'A'
        with pytest.raises(ValueError, match=r"No numeric value for code point: U\+0020"):
            ud.get_property(0x0020, 'numeric')  # Space

    def test_get_property_decimal(self, ud):
        """Test getting decimal values."""
        # Test ASCII digits
        assert ud.get_property(0x0030, 'decimal') == 0  # '0'
        assert ud.get_property(0x0039, 'decimal') == 9  # '9'

        # Test non-decimal characters
        with pytest.raises(ValueError, match=r"No decimal value for code point: U\+00BD"):
            ud.get_property(0x00BD, 'decimal')  # '½'
        with pytest.raises(ValueError, match=r"No decimal value for code point: U\+0041"):
            ud.get_property(0x0041, 'decimal')  # 'A'

    def test_get_property_invalid_type(self, ud):
        """Test handling of invalid property types."""
        with pytest.raises(ValueError, match="Unsupported property type.*Supported types are:"):
            ud.get_property(0x0041, 'invalid_type')
        with pytest.raises(ValueError, match="Unsupported property type.*Supported types are:"):
            ud.get_property(0x0041, 'category')  # Should use get_category instead

    def test_get_property_from_file(self, ud):
        """Test getting properties from files."""
        # Test script properties
        latin = ud.get_property('Scripts', 'Latin')
        assert isinstance(latin, CodePointSet)
        assert 0x0041 in latin  # 'A'
        assert 0x0061 in latin  # 'a'
        assert 0x0391 not in latin  # 'Α' (Greek)

        # Test error handling
        with pytest.raises(ValueError, match="Property file not found"):
            ud.get_property('NonExistentFile', 'Value')
        with pytest.raises(ValueError, match="Unknown property.*in Scripts"):
            ud.get_property('Scripts', 'NonExistentScript')

    def test_get_property_type_validation(self, ud):
        """Test type validation in get_property."""
        with pytest.raises(TypeError, match="prop_file must be a string or integer"):
            ud.get_property(3.14, 'name')  # type: ignore
        with pytest.raises(TypeError, match="prop_file must be a string or integer"):
            ud.get_property(None, 'name')  # type: ignore
        with pytest.raises(TypeError, match="prop_file must be a string or integer"):
            ud.get_property([], 'name')  # type: ignore

    def test_get_code_points_by_property(self, ud):
        """Test getting code points by property."""
        points = ud.get_code_points_by_property('Scripts', 'Latin')
        assert isinstance(points, set)
        assert 0x0041 in points  # 'A'

    def test_get_all_properties(self, ud):
        """Test getting all properties from a file."""
        properties = ud.get_all_properties('Scripts')
        assert isinstance(properties, list)
        assert 'Latin' in properties


class TestUtilityMethods:
    """Test utility methods."""

    def test_get_numeric_value(self, ud):
        """Test getting numeric values."""
        assert ud.get_numeric_value('0') == 0.0
        assert ud.get_numeric_value('½') == 0.5
        assert ud.get_numeric_value('A') is None

    def test_get_name(self, ud):
        """Test getting character names."""
        assert ud.get_name('A') == 'LATIN CAPITAL LETTER A'
        assert ud.get_name('\x00') == 'NULL'
        assert ud.get_name('€') == 'EURO SIGN'
        assert ud.get_name('\U0010FFFF') is None  # Non-existent character

    def test_property_file_loading(self, ud):
        """Test property file loading."""
        # Force load a property file
        _ = ud.get_property('Scripts', 'Latin')
        assert 'Scripts' in ud._property_cache
        assert isinstance(ud._property_cache['Scripts'], dict)
        assert 'Latin' in ud._property_cache['Scripts']

    def test_load_property_file(self):
        """Test that property files can be loaded correctly."""
        unicode_data = UnicodeData()

        # Test loading Scripts.txt
        script_set = unicode_data.get_property('Scripts', 'Latin')
        assert isinstance(script_set, CodePointSet)
        assert len(script_set) > 0  # Use len() instead of is_empty()
        assert 0x0041 in script_set  # 'A' is in Latin script
        assert 0x0061 in script_set  # 'a' is in Latin script

        # Test loading Blocks.txt
        block_set = unicode_data.get_property('Blocks', 'Basic Latin')
        assert isinstance(block_set, CodePointSet)
        assert len(block_set) > 0
        assert 0x0041 in block_set  # 'A' is in Basic Latin block

        # Test loading a non-existent property file
        with pytest.raises(ValueError, match="Property file not found"):
            unicode_data.get_property('NonExistent', 'SomeProperty')

        # Test loading a non-existent property
        with pytest.raises(ValueError, match="Unknown property NonExistentScript in Scripts"):
            unicode_data.get_property('Scripts', 'NonExistentScript')