"""Module for generating optimized regular expressions from Unicode code point sets.

This module provides functionality to generate regex patterns from sets of Unicode code points,
with support for common ranges, pattern optimization, and various formatting options.
"""

from typing import Set, Optional, Union, List, Tuple, Dict, Any
from .code_point_set import CodePointSet
from .optimizer import Optimizer, OptimizationPriority
import re


class RegexGenerator:
    """A class for generating optimized regex patterns from Unicode code point sets.

    This class provides methods to generate regular expressions from sets of Unicode code points,
    with support for common ranges (like \d, \w, \s), pattern optimization, and various formatting
    options. It includes caching for improved performance and integrates with the Optimizer class
    for pattern optimization.

    Attributes:
        SPECIAL_CHARS (frozenset): Characters that need escaping in regex patterns.
        COMMON_RANGES (dict): Mapping of common regex patterns to their CodePointSet equivalents.
    """

    SPECIAL_CHARS = frozenset('.^$*+?{}[]\\|()-')

    COMMON_RANGES = {
        r'\d': CodePointSet(range(0x0030, 0x003A)),  # 0-9
        r'\w': CodePointSet(
            list(range(0x0030, 0x003A)) +  # 0-9
            list(range(0x0041, 0x005B)) +  # A-Z
            list(range(0x0061, 0x007B)) +  # a-z
            [0x005F]  # underscore
        ),
        r'\s': CodePointSet([0x0020, 0x0009, 0x000A, 0x000B, 0x000C, 0x000D])  # Space, Tab, LF, VT, FF, CR
    }

    def __init__(self, optimizer: Optional[Optimizer] = None) -> None:
        """Initialize the regex generator with an optional optimizer.

        Args:
            optimizer: Optional custom optimizer instance. If not provided, a default
                     Optimizer instance will be created.
        """
        self.optimizer = optimizer or Optimizer()
        self._pattern_cache: Dict[Tuple[frozenset, str], str] = {}

    def _escape_char(self, char: str) -> str:
        """Escape a character if it has special meaning in regex patterns.

        Args:
            char: The character to potentially escape.

        Returns:
            The escaped character if it needs escaping, otherwise the original character.
        """
        return '\\' + char if char in self.SPECIAL_CHARS else char

    def _format_code_point(self, cp: int, use_hex: bool = False) -> str:
        """Format a code point as a character or escape sequence.

        Args:
            cp: The Unicode code point to format.
            use_hex: If True, always use hexadecimal escape sequence even for ASCII.

        Returns:
            A string representing the code point, either as a character or escape sequence.
        """
        if cp < 128 and not use_hex:
            return self._escape_char(chr(cp))
        elif cp <= 0xFFFF:
            return f"\\u{cp:04x}"
        else:
            return f"\\U{cp:08x}"

    def generate_pattern(self, code_points: Union[Set[int], CodePointSet], prioritize: str = 'size') -> str:
        """Generate a regex pattern from a set of code points.

        This method generates an optimized regex pattern that matches the given set of code points.
        It checks for common ranges (like \d, \w, \s) first, then falls back to generating a
        custom pattern. Results are cached for improved performance.

        Args:
            code_points: Set of Unicode code points to generate a pattern for.
            prioritize: Optimization priority, either 'size' or 'readability'.

        Returns:
            A string containing the generated regex pattern.

        Examples:
            >>> generator = RegexGenerator()
            >>> digits = CodePointSet(range(0x0030, 0x003A))
            >>> generator.generate_pattern(digits)
            '\\d'
        """
        if not code_points:
            return '[]'

        cache_key = (frozenset(code_points), prioritize)
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]

        for pattern, common_set in self.COMMON_RANGES.items():
            if code_points == common_set:
                self._pattern_cache[cache_key] = pattern
                return pattern

        ranges = self._get_ranges(code_points)
        pattern = self._ranges_to_pattern(ranges, prioritize)

        self._pattern_cache[cache_key] = pattern
        return pattern

    def generate_alternation_pattern(self, patterns: List[str], prioritize: str = 'size') -> str:
        """Generate a pattern that matches any of the given patterns.

        Args:
            patterns: List of regex patterns to combine with alternation.
            prioritize: Optimization priority, either 'size' or 'readability'.

        Returns:
            A string containing the alternation pattern.

        Examples:
            >>> generator = RegexGenerator()
            >>> generator.generate_alternation_pattern(['foo', 'bar'], 'readability')
            '(?:foo | bar)'
        """
        if not patterns:
            return '[]'

        if len(patterns) == 1:
            return patterns[0]

        if prioritize == 'readability':
            return f'(?:{" | ".join(patterns)})'
        return '|'.join(patterns)

    def generate_range_pattern(self, start: int, end: int) -> str:
        """Generate a pattern for a range of code points.

        Args:
            start: First code point in the range.
            end: Last code point in the range (inclusive).

        Returns:
            A string containing the range pattern.

        Raises:
            ValueError: If start is greater than end.

        Examples:
            >>> generator = RegexGenerator()
            >>> generator.generate_range_pattern(0x0041, 0x005A)  # A-Z
            '[A-Z]'
        """
        if start > end:
            raise ValueError(f'Invalid range: {start} > {end}')
        return self._ranges_to_pattern([(start, end)])

    def generate_category_pattern(self, category: str) -> str:
        """Generate a pattern for a Unicode category.

        Args:
            category: Unicode category code (e.g., 'Lu' for uppercase letters).

        Returns:
            A string containing the category pattern.

        Examples:
            >>> generator = RegexGenerator()
            >>> generator.generate_category_pattern('Lu')
            '\\p{Lu}'
        """
        return f'\\p{{{category}}}'

    def generate_property_pattern(self, property_name: str, property_value: str) -> str:
        """Generate a pattern for a Unicode property.

        Args:
            property_name: Name of the Unicode property.
            property_value: Value of the Unicode property.

        Returns:
            A string containing the property pattern.

        Examples:
            >>> generator = RegexGenerator()
            >>> generator.generate_property_pattern('Script', 'Latin')
            '\\p{Script=Latin}'
        """
        return f'\\p{{{property_name}={property_value}}}'

    def _get_ranges(self, code_points: Union[Set[int], CodePointSet]) -> List[Tuple[int, int]]:
        """Convert a set of code points to a list of contiguous ranges.

        This method converts a set of code points into a list of ranges where each range
        represents a contiguous sequence of code points.

        Args:
            code_points: Set of Unicode code points to convert.

        Returns:
            List of (start, end) tuples representing ranges.
        """
        if not code_points:
            return []

        points = sorted(code_points)
        ranges = []
        start = points[0]
        prev = start

        for point in points[1:]:
            if point != prev + 1:
                ranges.append((start, prev))
                start = point
            prev = point

        ranges.append((start, prev))
        return ranges

    def _ranges_to_pattern(self, ranges: List[Tuple[int, int]], prioritize: str = 'size') -> str:
        """Convert a list of code point ranges to a regex pattern.

        This method generates a regex pattern that matches the given ranges of code points,
        with options for optimizing for size or readability.

        Args:
            ranges: List of (start, end) tuples representing code point ranges.
            prioritize: Optimization priority, either 'size' or 'readability'.

        Returns:
            A string containing the generated pattern.
        """
        if not ranges:
            return '[]'

        if len(ranges) == 1 and ranges[0][0] == ranges[0][1]:
            point = ranges[0][0]
            char = chr(point)
            return re.escape(char) if self._needs_escape(char) else char

        patterns = []
        for start, end in ranges:
            if start == end:
                char = chr(start)
                patterns.append(re.escape(char) if self._needs_escape(char) else char)
            else:
                start_char = chr(start)
                end_char = chr(end)
                if self._needs_escape(start_char):
                    start_char = re.escape(start_char)
                if self._needs_escape(end_char):
                    end_char = re.escape(end_char)

                if prioritize == 'readability':
                    patterns.append(f'{start_char} - {end_char}')
                else:
                    patterns.append(f'{start_char}-{end_char}')

        if len(patterns) == 1:
            return f'[{patterns[0]}]'

        if prioritize == 'readability':
            return f'[{" | ".join(patterns)}]'
        return f'[{"".join(patterns)}]'

    def _needs_escape(self, char: str) -> bool:
        """Check if a character needs to be escaped in a regex pattern.

        Args:
            char: The character to check.

        Returns:
            True if the character needs escaping, False otherwise.
        """
        return char in '.^$*+?{}[]\\|()'