import pytest
from pathlib import Path
from ..unicode_data import UnicodeData
from ..code_point_set import CodePointSet

@pytest.fixture
def unicode_data():
    return UnicodeData()

def test_initialization(unicode_data):
    assert not unicode_data._initialized
    assert isinstance(unicode_data._category_cache, dict)
    assert isinstance(unicode_data._property_cache, dict)

def test_ensure_initialized(unicode_data):
    unicode_data._ensure_initialized()
    assert unicode_data._initialized
    assert len(unicode_data._category_cache) == len(UnicodeData.CATEGORIES)
    assert all(isinstance(v, CodePointSet) for v in unicode_data._category_cache.values())

def test_get_category_basic(unicode_data):
    uppercase_letters = unicode_data.get_category('Lu')
    assert isinstance(uppercase_letters, CodePointSet)
    assert ord('A') in uppercase_letters
    assert ord('a') not in uppercase_letters

def test_get_category_major(unicode_data):
    all_letters = unicode_data.get_category('L')
    assert isinstance(all_letters, CodePointSet)
    assert ord('A') in all_letters
    assert ord('a') in all_letters
    assert ord('1') not in all_letters

def test_get_category_invalid():
    ud = UnicodeData()
    with pytest.raises(ValueError, match="Unknown Unicode category"):
        ud.get_category('XX')

def test_get_numeric_value(unicode_data):
    assert unicode_data.get_numeric_value('1') == 1.0
    assert unicode_data.get_numeric_value('½') == 0.5
    assert unicode_data.get_numeric_value('A') is None

def test_get_name(unicode_data):
    assert unicode_data.get_name('A') == 'LATIN CAPITAL LETTER A'
    assert unicode_data.get_name('1') == 'DIGIT ONE'
    assert unicode_data.get_name('\u0000') == 'NULL'

def test_property_file_handling(unicode_data, tmp_path):
    import os

    # Create a temporary test property file
    test_file = tmp_path / "test_props.txt"
    test_content = """
    0041..005A; Latin_Upper
    0061..007A; Latin_Lower
    """
    test_file.write_text(test_content)

    # Test property loading
    with pytest.raises(ValueError, match="Property file not found"):
        unicode_data.get_property('NonexistentFile', 'SomeProp')

def test_get_all_properties(unicode_data, monkeypatch, tmp_path):
    # Create a mock property file
    test_file = tmp_path / "Scripts.txt"
    test_content = """
    0041..005A; Latin
    0061..007A; Latin
    0370..0373; Greek
    """
    test_file.write_text(test_content)

    def mock_exists(*args, **kwargs):
        return True

    monkeypatch.setattr(Path, "exists", mock_exists)

    props = unicode_data.get_all_properties('Scripts')
    assert isinstance(props, list)
    assert 'Latin' in props
    assert 'Greek' in props