"""Module for efficient handling of Unicode code point sets and ranges.

This module provides classes for working with sets of Unicode code points and code point ranges.
It includes efficient implementations for set operations and range manipulations, with proper
validation of Unicode code points.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Optional, Set, Tuple, Union


@dataclass(frozen=True)
class CodePointRange:
    """An immutable range of Unicode code points.

    This class represents a contiguous range of Unicode code points, with validation
    to ensure the range is valid according to Unicode standards. The range is inclusive
    of both start and end points.

    Attributes:
        start: The first code point in the range.
        end: The last code point in the range (inclusive).

    Raises:
        ValueError: If the range is invalid (start > end or points outside valid Unicode range).
    """

    start: int
    end: int

    def __post_init__(self) -> None:
        """Validate the range after initialization.

        Raises:
            ValueError: If the range is invalid.
        """
        if not (0 <= self.start <= self.end <= 0x10FFFF):
            raise ValueError(
                f"Invalid code point range: {self.start:X}-{self.end:X}. "
                "Code points must be between 0x0 and 0x10FFFF"
            )

    def __contains__(self, code_point: int) -> bool:
        """Check if a code point is within this range.

        Args:
            code_point: The Unicode code point to check.

        Returns:
            True if the code point is within the range, False otherwise.
        """
        return self.start <= code_point <= self.end

    def overlaps(self, other: CodePointRange) -> bool:
        """Check if this range overlaps with another range.

        Two ranges overlap if they share at least one code point.

        Args:
            other: Another code point range to check against.

        Returns:
            True if the ranges overlap, False otherwise.
        """
        return not (self.end < other.start or other.end < self.start)

    def adjacent_to(self, other: CodePointRange) -> bool:
        """Check if this range is adjacent to another range.

        Two ranges are adjacent if they can be merged into a single contiguous range.

        Args:
            other: Another code point range to check against.

        Returns:
            True if the ranges are adjacent, False otherwise.
        """
        return self.end + 1 == other.start or other.end + 1 == self.start

    def merge(self, other: CodePointRange) -> CodePointRange:
        """Merge this range with another overlapping or adjacent range.

        Args:
            other: Another code point range to merge with.

        Returns:
            A new CodePointRange representing the merged range.

        Raises:
            ValueError: If the ranges cannot be merged (not overlapping or adjacent).
        """
        if not (self.overlaps(other) or self.adjacent_to(other)):
            raise ValueError("Cannot merge non-overlapping, non-adjacent ranges")
        return CodePointRange(min(self.start, other.start), max(self.end, other.end))


class CodePointSet:
    """A set of Unicode code points with efficient range operations.

    This class provides an efficient implementation for working with sets of Unicode code points.
    It supports standard set operations (union, intersection, difference) as well as range-based
    operations for better performance when working with contiguous sequences of code points.

    The implementation uses a standard set for storage but provides optimized methods for
    working with ranges of code points.

    Attributes:
        _points: Internal set storing the actual code points.
    """

    def __init__(self, code_points: Optional[Set[int]] = None) -> None:
        """Initialize a code point set.

        Args:
            code_points: Optional initial set of code points to include.
        """
        self._points: Set[int] = set()
        if code_points is not None:
            for point in code_points:
                self.add(point)

    def __invert__(self) -> CodePointSet:
        """Return the complement of this set (all code points not in this set).

        This operation returns a new set containing all valid Unicode code points
        that are not in the current set.

        Returns:
            A new CodePointSet containing all code points not in this set.
        """
        result = CodePointSet()
        current = 0
        for point in sorted(self._points):
            if point > current:
                result.add_range(current, point - 1)
            current = point + 1
        if current <= 0x10FFFF:
            result.add_range(current, 0x10FFFF)
        return result

    @property
    def code_points(self) -> Set[int]:
        """Get a copy of the internal set of code points.

        Returns:
            A new set containing all code points in this set.
        """
        return self._points.copy()

    @classmethod
    def from_range(cls, start: int, end: int) -> CodePointSet:
        """Create a new set from a range of code points.

        Args:
            start: First code point in the range.
            end: Last code point in the range (inclusive).

        Returns:
            A new CodePointSet containing all points in the range.

        Raises:
            ValueError: If the range is invalid.
        """
        result = cls()
        result.add_range(start, end)
        return result

    @classmethod
    def from_single(cls, code_point: int) -> CodePointSet:
        """Create a new set containing a single code point.

        Args:
            code_point: The Unicode code point to include.

        Returns:
            A new CodePointSet containing only the specified code point.

        Raises:
            ValueError: If the code point is invalid.
        """
        return cls.from_range(code_point, code_point)

    @classmethod
    def from_string(cls, text: str) -> CodePointSet:
        """Create a new set from a string.

        Args:
            text: String whose characters will be converted to code points.

        Returns:
            A new CodePointSet containing code points for all characters in the string.
        """
        result = cls()
        for char in text:
            result.add(ord(char))
        return result

    def add(self, code_point: int) -> None:
        """Add a single code point to the set.

        Args:
            code_point: The Unicode code point to add.

        Raises:
            ValueError: If the code point is invalid.
        """
        if not 0 <= code_point <= 0x10FFFF:
            raise ValueError(f"Invalid code point: {code_point}")
        self._points.add(code_point)

    def add_range(self, start: int, end: int) -> None:
        """Add a range of code points to the set.

        Args:
            start: First code point in the range.
            end: Last code point in the range (inclusive).

        Raises:
            ValueError: If the range is invalid.
        """
        if not (0 <= start <= end <= 0x10FFFF):
            raise ValueError(f"Invalid code point range: {start}..{end}")
        for point in range(start, end + 1):
            self._points.add(point)

    def remove(self, code_point: int) -> None:
        """Remove a code point from the set.

        Args:
            code_point: The Unicode code point to remove.
        """
        self._points.discard(code_point)

    def remove_range(self, start: int, end: int) -> None:
        """Remove a range of code points from the set.

        Args:
            start: First code point in the range to remove.
            end: Last code point in the range to remove (inclusive).
        """
        for point in range(start, end + 1):
            self._points.discard(point)

    def __contains__(self, code_point: int) -> bool:
        """Check if a code point is in the set.

        Args:
            code_point: The Unicode code point to check.

        Returns:
            True if the code point is in the set, False otherwise.
        """
        return code_point in self._points

    def __iter__(self) -> Iterator[int]:
        """Iterate over the code points in the set in ascending order.

        Returns:
            An iterator yielding code points in ascending order.
        """
        return iter(sorted(self._points))

    def __len__(self) -> int:
        """Get the number of code points in the set.

        Returns:
            The number of code points in the set.
        """
        return len(self._points)

    def __or__(self, other: CodePointSet) -> CodePointSet:
        """Return the union of this set and another.

        Args:
            other: Another code point set.

        Returns:
            A new set containing code points from both sets.
        """
        result = CodePointSet()
        result._points = self._points | other._points
        return result

    def __and__(self, other: CodePointSet) -> CodePointSet:
        """Return the intersection of this set and another.

        Args:
            other: Another code point set.

        Returns:
            A new set containing code points common to both sets.
        """
        result = CodePointSet()
        result._points = self._points & other._points
        return result

    def __sub__(self, other: CodePointSet) -> CodePointSet:
        """Return the difference of this set and another.

        Args:
            other: Another code point set.

        Returns:
            A new set containing code points in this set but not in other.
        """
        result = CodePointSet()
        result._points = self._points - other._points
        return result

    def __bool__(self) -> bool:
        """Check if the set is non-empty.

        Returns:
            True if the set contains any code points, False otherwise.
        """
        return bool(self._points)

    def copy(self) -> CodePointSet:
        """Create a copy of this set.

        Returns:
            A new set with the same code points.
        """
        result = CodePointSet()
        result._points = self._points.copy()
        return result

    def get_ranges(self) -> Iterator[Tuple[int, int]]:
        """Get the code points as a sequence of contiguous ranges.

        This method converts the set of code points into a sequence of ranges,
        where each range represents a contiguous sequence of code points.

        Returns:
            An iterator yielding (start, end) tuples representing ranges.
        """
        if not self._points:
            return

        points = sorted(self._points)
        start = end = points[0]

        for point in points[1:]:
            if point == end + 1:
                end = point
            else:
                yield (start, end)
                start = end = point

        yield (start, end)