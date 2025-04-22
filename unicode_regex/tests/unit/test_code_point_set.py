"""Unit tests for the CodePointSet class."""

import pytest
from unicode_regex.code_point_set import CodePointSet


def test_code_point_set_initialization():
    """Test CodePointSet initialization."""
    code_points = {65, 66, 67}  # ASCII A, B, C
    cps = CodePointSet(code_points)
    assert cps.code_points == code_points


def test_code_point_set_validation():
    """Test code point validation."""
    with pytest.raises(ValueError):
        CodePointSet({-1})  # Invalid code point
    with pytest.raises(ValueError):
        CodePointSet({0x110000})  # Beyond Unicode range