"""Unit tests for the UnicodeData class."""

import pytest
from unicode_regex.unicode_data import UnicodeData


def test_get_category():
    """Test getting Unicode categories."""
    ud = UnicodeData()

    # Test ASCII letter
    assert ud.get_category(65) == 'Lu'  # 'A'
    assert ud.get_category(97) == 'Ll'  # 'a'

    # Test number
    assert ud.get_category(48) == 'Nd'  # '0'

    # Test punctuation
    assert ud.get_category(46) == 'Po'  # '.'

    # Test space
    assert ud.get_category(32) == 'Zs'  # space

    # Test invalid code point
    with pytest.raises(ValueError):
        ud.get_category(-1)
    with pytest.raises(ValueError):
        ud.get_category(0x110000)


def test_get_property():
    """Test getting Unicode properties."""
    ud = UnicodeData()

    # Test name property
    assert ud.get_property(65, 'name') == 'LATIN CAPITAL LETTER A'

    # Test numeric property
    assert ud.get_property(48, 'numeric') == '0'
    assert ud.get_property(65, 'numeric') is None  # 'A' has no numeric value

    # Test decimal property
    assert ud.get_property(48, 'decimal') == '0'
    assert ud.get_property(65, 'decimal') is None  # 'A' has no decimal value

    # Test invalid property
    assert ud.get_property(65, 'invalid_property') is None

    # Test invalid code point
    with pytest.raises(ValueError):
        ud.get_property(-1, 'name')


def test_get_code_points_by_category():
    """Test getting code points by category."""
    ud = UnicodeData()

    # Test uppercase letters
    upper = ud.get_code_points_by_category('Lu')
    assert 65 in upper  # 'A'
    assert 97 not in upper  # 'a'

    # Test all letters
    letters = ud.get_code_points_by_category('L')
    assert 65 in letters  # 'A'
    assert 97 in letters  # 'a'

    # Test invalid category
    with pytest.raises(ValueError):
        ud.get_code_points_by_category('XX')

    # Test invalid major category
    with pytest.raises(ValueError):
        ud.get_code_points_by_category('X')


def test_get_code_points_by_property():
    """Test getting code points by property value."""
    ud = UnicodeData()

    # Test numeric property
    digits = ud.get_code_points_by_property('numeric', '0')
    assert 48 in digits  # ASCII '0'

    # Test name property
    a_letters = ud.get_code_points_by_property('name', 'LATIN CAPITAL LETTER A')
    assert 65 in a_letters  # 'A'
    assert len(a_letters) == 1

    # Test invalid property
    with pytest.raises(ValueError):
        ud.get_code_points_by_property('invalid_property', 'value')