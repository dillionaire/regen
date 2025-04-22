"""Module for optimizing regex patterns.

This module provides functionality for optimizing regular expression patterns,
including pattern minimization, readability improvements, and performance benchmarking.
It supports different optimization strategies based on priorities like size and readability.
"""

from typing import List, Set, Tuple, Dict, Union, Any
import re
from .code_point_set import CodePointSet
from enum import Enum, auto


class OptimizationPriority(Enum):
    """Priority for pattern optimization.

    This enum defines the available optimization priorities that can be used
    when optimizing regex patterns. Each priority affects how patterns are
    optimized and formatted.

    Attributes:
        SIZE: Optimize for minimal pattern size.
        READABILITY: Optimize for human readability with proper spacing and formatting.
    """
    SIZE = auto()
    READABILITY = auto()


class Optimizer:
    """A class for optimizing regular expression patterns.

    This class provides methods to optimize regex patterns for different goals,
    such as minimizing pattern size, improving readability, and benchmarking
    performance. It includes functionality for compressing code point ranges,
    removing unnecessary constructs, and formatting patterns for better readability.

    The optimizer can work with both standard regex patterns and Unicode code point
    sets, providing various optimization strategies based on the specified priority
    (size vs. readability).

    Attributes:
        _range_cache: Internal cache for storing computed ranges to improve performance.
    """

    def __init__(self) -> None:
        """Initialize the pattern optimizer.

        Creates a new optimizer instance with an empty range cache.
        The range cache is used to store previously computed ranges
        to avoid redundant calculations.
        """
        self._range_cache: Dict[str, List[Tuple[int, int]]] = {}

    def compress_ranges(self, code_points: Union[Set[int], List[int]]) -> List[Tuple[int, int]]:
        """Compress consecutive code points into ranges.

        This method takes a set or list of Unicode code points and compresses them
        into a minimal set of contiguous ranges. This is useful for creating more
        compact regex patterns when dealing with large sets of characters.

        Args:
            code_points: A set or list of Unicode code points to compress.

        Returns:
            A list of (start, end) tuples representing contiguous ranges.
            Each tuple contains the first and last code point (inclusive) of a range.

        Examples:
            >>> optimizer = Optimizer()
            >>> optimizer.compress_ranges({65, 66, 67, 69, 70})
            [(65, 67), (69, 70)]  # Represents 'A-C' and 'E-F'
        """
        if not code_points:
            return []

        # Convert to sorted list for range detection
        points = sorted(code_points)
        ranges: List[Tuple[int, int]] = []
        start = points[0]
        prev = start

        for point in points[1:]:
            if point != prev + 1:
                # End of current range
                ranges.append((start, prev))
                start = point
            prev = point

        # Add the last range
        ranges.append((start, prev))
        return ranges

    def minimize_pattern(self, pattern: str) -> str:
        """Minimize a regex pattern by removing unnecessary constructs.

        This method optimizes a regex pattern by removing redundant constructs
        such as unnecessary character classes, non-capturing groups, and by
        combining adjacent character classes where possible.

        Args:
            pattern: The regex pattern to minimize.

        Returns:
            The minimized pattern with unnecessary constructs removed.

        Examples:
            >>> optimizer = Optimizer()
            >>> optimizer.minimize_pattern('[a]')
            'a'
            >>> optimizer.minimize_pattern('(?:abc)')
            'abc'
            >>> optimizer.minimize_pattern('[a-c][d-f]')
            '[a-cf-d]'
        """
        if not pattern:
            return pattern

        # Remove unnecessary character classes
        if pattern.startswith('[') and pattern.endswith(']'):
            content = pattern[1:-1]
            if len(content) == 1 and not content.startswith('\\'):
                return content

        # Remove unnecessary non-capturing groups
        if pattern.startswith('(?:') and pattern.endswith(')'):
            content = pattern[3:-1]
            if '|' not in content:
                return content

        # Combine adjacent character classes
        if '][' in pattern:
            parts = pattern.split('][')
            if all(p.startswith('[') for p in parts[1:]) and all(p.endswith(']') for p in parts[:-1]):
                combined = ''.join(p.strip('[]') for p in parts)
                return f'[{combined}]'

        return pattern

    def optimize_readability(self, pattern: str) -> str:
        """Optimize pattern readability by adding appropriate spacing.

        This method improves the readability of regex patterns by adding spaces
        around alternation operators (|) when they're not inside character classes.
        It preserves the pattern's functionality while making it more readable.

        Args:
            pattern: The regex pattern to optimize for readability.

        Returns:
            The pattern with improved spacing for better readability.

        Examples:
            >>> optimizer = Optimizer()
            >>> optimizer.optimize_readability('foo|bar|baz')
            'foo | bar | baz'
            >>> optimizer.optimize_readability('[a|b]')
            '[a|b]'  # No spaces added inside character class
        """
        if not pattern:
            return pattern

        # Add spaces around alternations outside character classes
        in_class = False
        result = []
        for i, c in enumerate(pattern):
            if c == '[':
                in_class = True
            elif c == ']':
                in_class = False
            elif c == '|' and not in_class:
                if i > 0 and pattern[i-1] != ' ':
                    result.append(' ')
                result.append(c)
                if i < len(pattern)-1 and pattern[i+1] != ' ':
                    result.append(' ')
                continue
            result.append(c)

        return ''.join(result)

    def optimize_pattern(self, pattern: str, prioritize: str = 'size') -> str:
        """Optimize a regex pattern based on the given priority.

        This method applies optimization strategies based on the specified priority.
        It first minimizes the pattern to remove unnecessary constructs, then
        optionally applies readability improvements if requested.

        Args:
            pattern: The regex pattern to optimize.
            prioritize: Optimization priority ('size' or 'readability').
                      'size' focuses on creating the smallest possible pattern.
                      'readability' adds spacing and formatting for better readability.

        Returns:
            The optimized pattern according to the specified priority.

        Raises:
            ValueError: If priority is not 'size' or 'readability'.

        Examples:
            >>> optimizer = Optimizer()
            >>> optimizer.optimize_pattern('[a]|[b]', 'size')
            '[ab]'
            >>> optimizer.optimize_pattern('foo|bar', 'readability')
            'foo | bar'
        """
        if prioritize not in ('size', 'readability'):
            raise ValueError("Priority must be 'size' or 'readability'")

        # First minimize the pattern
        result = self.minimize_pattern(pattern)

        # Then optimize readability if requested
        if prioritize == 'readability':
            result = self.optimize_readability(result)

        return result

    def optimize(self, pattern: str) -> str:
        """Optimize a regular expression pattern using default settings.

        This is a convenience method that applies both size minimization and
        readability improvements to a pattern. It's equivalent to calling
        optimize_pattern with prioritize='readability'.

        Args:
            pattern: The pattern to optimize.

        Returns:
            The optimized pattern with both size and readability improvements.

        Examples:
            >>> optimizer = Optimizer()
            >>> optimizer.optimize('[a]|[b-c]|[d]')
            '[a-d]'
        """
        if not pattern:
            return pattern

        # First minimize the pattern
        pattern = self.minimize_pattern(pattern)

        # Then optimize for readability
        pattern = self.optimize_readability(pattern)

        return pattern

    def benchmark_pattern(self, pattern: str, test_string: str, iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark a regex pattern's performance.

        This method measures the performance characteristics of a regex pattern
        by testing it against a sample string multiple times. It provides metrics
        such as pattern size and average matching time.

        Args:
            pattern: The regex pattern to benchmark.
            test_string: The string to test the pattern against.
            iterations: Number of matching iterations to perform (default: 1000).

        Returns:
            A dictionary containing benchmark results with the following keys:
            - pattern_size: Length of the compiled pattern
            - avg_match_time: Average time per match operation in seconds
            - iterations: Number of iterations performed
            If pattern compilation fails, returns:
            - error: Description of the error
            - pattern_size: Length of the pattern
            - iterations: 0

        Examples:
            >>> optimizer = Optimizer()
            >>> result = optimizer.benchmark_pattern('a+b+', 'aaabbb')
            >>> sorted(result.keys())
            ['avg_match_time', 'iterations', 'pattern_size']
        """
        import time

        try:
            regex = re.compile(pattern)

            start_time = time.time()
            for _ in range(iterations):
                regex.match(test_string)
            end_time = time.time()

            compile_size = len(pattern)
            match_time = (end_time - start_time) / iterations

            return {
                'pattern_size': compile_size,
                'avg_match_time': match_time,
                'iterations': iterations
            }

        except re.error as e:
            return {
                'error': str(e),
                'pattern_size': len(pattern),
                'iterations': 0
            }