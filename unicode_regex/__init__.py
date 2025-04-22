"""
Unicode Regex Generator for Python

A library for generating optimized, Unicode-aware regular expressions.
"""

__version__ = "0.1.0"

from .code_point_set import CodePointSet
from .regex_generator import RegexGenerator
from .unicode_data import UnicodeData
from .optimizer import Optimizer

__all__ = ["CodePointSet", "RegexGenerator", "UnicodeData", "Optimizer"]